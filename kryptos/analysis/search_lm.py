"""search_lm.py -- corpus construction + calibrated character language model for K4.

Builds an English character-level model (quadgram + interpolated 5-gram) from prose
available offline on this machine.  IMPORTANT: the Kryptos working directory is
EXCLUDED from the corpus so that the model is not contaminated by K4 hypotheses,
crib words or prior-art plaintexts.

Usage:
    python3.13 search_lm.py build      # build corpus + model (cached)
    python3.13 search_lm.py calibrate  # print the calibration tables
"""
import os, re, sys, gzip, json, math, random, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
CACHE = os.path.join(HERE, ".search_corpus.txt")
MODEL = os.path.join(HERE, ".search_lm.npz")

# A model VARIANT restricts the corpus to a subset of sources.  Used to show that
# whatever "themes" the annealer produces track the training corpus, not K4.
VARIANT = os.environ.get("K4_LM", "all")          # all | man | docinfo
VARIANT_TAGS = {"all": None, "man": {"man"}, "docinfo": {"doc", "info"}}
if VARIANT != "all":
    CACHE = os.path.join(HERE, f".search_corpus_{VARIANT}.txt")
    MODEL = os.path.join(HERE, f".search_lm_{VARIANT}.npz")

A2Z = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# ---------------------------------------------------------------- dictionary
def load_dict():
    words = set()
    for path in ("/usr/share/dict/words",):
        if os.path.exists(path):
            with open(path, errors="ignore") as f:
                for w in f:
                    w = w.strip().lower()
                    if w.isalpha():
                        words.add(w)
    return words

# ---------------------------------------------------------------- line filter
TROFF = re.compile(r"\\f[BIRP]|\\s[-+]?\d|\\&|\\\*|\\-|\\\(\w\w|\\e")

def clean_line(line):
    line = TROFF.sub(" ", line)
    line = re.sub(r"<[^>]{0,80}>", " ", line)          # html/xml tags
    line = re.sub(r"[^A-Za-z'\- ]+", " ", line)
    line = re.sub(r"\s+", " ", line).strip()
    return line

def good_line(line, words, min_len=45, min_dict=0.80):
    """Keep only lines that look like running English prose."""
    if len(line) < min_len:
        return False
    toks = [t.strip("'-").lower() for t in line.split()]
    toks = [t for t in toks if t]
    if len(toks) < 7:
        return False
    hits = sum(1 for t in toks if t in words or (len(t) == 1 and t in "ai"))
    if hits / len(toks) < min_dict:
        return False
    avg = sum(len(t) for t in toks) / len(toks)
    if not (2.6 <= avg <= 8.0):
        return False
    return True

# ---------------------------------------------------------------- sources
def iter_source_files():
    """(tag, path, kind) for every candidate prose file.  Kryptos dir excluded."""
    out = []
    info = "/opt/homebrew/share/info"
    if os.path.isdir(info):
        for fn in sorted(os.listdir(info)):
            p = os.path.join(info, fn)
            if os.path.isfile(p) and (".info" in fn) and not fn.endswith((".png", ".jpg")):
                out.append(("info", p, "text"))
    for mandir in ("/usr/share/man", "/opt/homebrew/share/man"):
        if os.path.isdir(mandir):
            for root, _dirs, files in os.walk(mandir, followlinks=True):
                for fn in sorted(files):
                    if fn.endswith((".gz", ".1", ".3", ".5", ".7", ".8")):
                        out.append(("man", os.path.join(root, fn), "man"))
    for docdir in ("/opt/homebrew/share/doc", "/opt/homebrew/Cellar"):
        if os.path.isdir(docdir):
            for root, _dirs, files in os.walk(docdir, followlinks=True):
                for fn in sorted(files):
                    if fn.lower().endswith((".txt", ".md", ".rst")) or fn in (
                            "README", "NEWS", "AUTHORS", "THANKS", "ChangeLog"):
                        out.append(("doc", os.path.join(root, fn), "text"))
    for pydir in ("/opt/homebrew/lib/python3.13", "/opt/homebrew/lib/python3.12",
                  "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10"):
        if os.path.isdir(pydir):
            for root, _dirs, files in os.walk(pydir):
                if "test" in root or "site-packages" in root:
                    continue
                for fn in sorted(files):
                    if fn.endswith(".py"):
                        out.append(("py", os.path.join(root, fn), "py"))
                    elif fn.endswith((".rst", ".txt")):
                        out.append(("py", os.path.join(root, fn), "text"))
    return out

def read_file(path, kind):
    try:
        if path.endswith(".gz"):
            with gzip.open(path, "rt", errors="ignore") as f:
                txt = f.read()
        else:
            with open(path, errors="ignore") as f:
                txt = f.read()
    except Exception:
        return ""
    if kind == "man":
        lines = [ln for ln in txt.splitlines() if not ln.startswith((".", "'", '"'))]
        txt = "\n".join(lines)
    elif kind == "py":
        # docstrings and comments only
        chunks = []
        try:
            import ast
            tree = ast.parse(txt)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    d = ast.get_docstring(node)
                    if d:
                        chunks.append(d)
        except Exception:
            pass
        for ln in txt.splitlines():
            s = ln.strip()
            if s.startswith("# ") and len(s) > 30:
                chunks.append(s[2:])
        txt = "\n".join(chunks)
    return txt

def build_corpus(target_letters=30_000_000, verbose=True):
    words = load_dict()
    files = iter_source_files()
    keep_tags = VARIANT_TAGS[VARIANT]
    if keep_tags is not None:
        files = [f for f in files if f[0] in keep_tags]
    random.Random(12345).shuffle(files)
    seen_lines = set()
    pieces = []
    total = 0
    per_tag = {}
    for tag, path, kind in files:
        if total >= target_letters:
            break
        txt = read_file(path, kind)
        if not txt:
            continue
        keep = []
        for raw in txt.splitlines():
            ln = clean_line(raw)
            if good_line(ln, words):
                key = ln.lower()
                if key in seen_lines:
                    continue
                seen_lines.add(key)
                keep.append(ln)
        if keep:
            blob = " ".join(keep)
            letters = re.sub("[^A-Z]", "", blob.upper())
            pieces.append(letters)
            total += len(letters)
            per_tag[tag] = per_tag.get(tag, 0) + len(letters)
    corpus = "".join(pieces)
    if verbose:
        print(f"corpus letters: {len(corpus):,}  from {len(files):,} candidate files")
        for k, v in sorted(per_tag.items(), key=lambda kv: -kv[1]):
            print(f"   {k:6s} {v:>12,}")
    return corpus

def get_corpus(rebuild=False):
    if os.path.exists(CACHE) and not rebuild:
        with open(CACHE) as f:
            return f.read().strip()
    c = build_corpus()
    with open(CACHE, "w") as f:
        f.write(c)
    return c

# ---------------------------------------------------------------- model
def build_model(rebuild=False):
    import numpy as np
    if os.path.exists(MODEL) and not rebuild:
        return np.load(MODEL)
    corpus = get_corpus(rebuild=rebuild)
    n = len(corpus)
    holdout = corpus[int(n * 0.95):]          # 5% held out for calibration
    train = corpus[:int(n * 0.95)]
    print(f"train {len(train):,} letters, holdout {len(holdout):,} letters")
    c = np.frombuffer(train.encode(), dtype=np.uint8).astype(np.int64) - 65
    def ngram_counts(order):
        idx = np.zeros(len(c) - order + 1, dtype=np.int64)
        for k in range(order):
            idx = idx * 26 + c[k: len(c) - order + 1 + k]
        return np.bincount(idx, minlength=26 ** order).astype(np.float64)
    c1 = ngram_counts(1); c2 = ngram_counts(2); c3 = ngram_counts(3)
    c4 = ngram_counts(4); c5 = ngram_counts(5)
    # quadgram conditional log10 P(d | abc) with add-k smoothing
    k = 0.5
    ctx3 = c3[: 26 ** 3].copy()
    q = np.log10((c4.reshape(26**3, 26) + k) / (ctx3.reshape(-1, 1) + 26 * k)).astype(np.float32)
    # 5-gram conditional, interpolated with the quadgram model (Jelinek-Mercer)
    ctx4 = c4.copy()
    lam = 0.75
    p5 = (c5.reshape(26**4, 26) + 1e-9) / (ctx4.reshape(-1, 1) + 1e-9)
    p4 = 10.0 ** q.reshape(26**3, 26)
    p4b = np.repeat(p4, 26, axis=0)           # broadcast quad probs over the 4-letter contexts
    mix = lam * p5 + (1 - lam) * p4b
    mix = np.where(ctx4.reshape(-1, 1) > 0, mix, p4b)
    g5 = np.log10(np.maximum(mix, 1e-12)).astype(np.float32)
    np.savez_compressed(MODEL, q=q.ravel(), g5=g5.ravel(),
                        holdout=np.frombuffer(holdout.encode(), dtype=np.uint8))
    print("model written", MODEL)
    return np.load(MODEL)

_Q = None; _G5 = None; _HOLD = None
def load():
    global _Q, _G5, _HOLD
    import numpy as np
    if _Q is None:
        m = build_model()
        _Q = m["q"].astype(np.float32)
        _G5 = m["g5"].astype(np.float32)
        _HOLD = m["holdout"].tobytes().decode()
    return _Q, _G5, _HOLD

def codes(s):
    import numpy as np
    return np.frombuffer(s.encode(), dtype=np.uint8).astype(np.int64) - 65

def quad(s):
    """mean log10 P(letter | previous 3), over positions 3..n-1"""
    import numpy as np
    Q, _, _ = load()
    c = codes(s)
    idx = (((c[:-3] * 26 + c[1:-2]) * 26 + c[2:-1]) * 26 + c[3:])
    return float(Q[idx].mean())

def quad_batch(mat):
    import numpy as np
    Q, _, _ = load()
    idx = (((mat[:, :-3] * 26 + mat[:, 1:-2]) * 26 + mat[:, 2:-1]) * 26 + mat[:, 3:])
    return Q[idx].mean(axis=1)

def pent(s):
    import numpy as np
    _, G5, _ = load()
    c = codes(s)
    idx = ((((c[:-4] * 26 + c[1:-3]) * 26 + c[2:-2]) * 26 + c[3:-1]) * 26 + c[4:])
    return float(G5[idx].mean())

# ---------------------------------------------------------------- calibration
def k123():
    pt = {}
    cur = None
    with open(os.path.join(DATA, "k1_k3_plaintext.txt")) as f:
        for line in f:
            if line.startswith("#"):
                m = re.match(r"#\s*(K\d)", line)
                if m:
                    cur = m.group(1)
                continue
            s = re.sub("[^A-Z]", "", line.upper())
            if s and cur:
                pt[cur] = pt.get(cur, "") + s
    return pt

def calibrate():
    import numpy as np
    Q, G5, hold = load()
    rng = np.random.default_rng(7)
    print("=" * 78)
    print("CALIBRATION of the character language model (mean log10 prob per letter)")
    print("=" * 78)
    rows = []
    # held-out English 97-grams
    starts = rng.integers(0, len(hold) - 98, size=20000)
    eng = np.array([[ord(ch) - 65 for ch in hold[s:s + 97]] for s in starts], dtype=np.int64)
    eq = quad_batch(eng)
    rows.append(("held-out English 97-grams (n=20000)", eq))
    # K1..K3
    pt = k123()
    for name in ("K1", "K2", "K3"):
        s = pt[name]
        if len(s) >= 97:
            wins = np.array([[ord(ch) - 65 for ch in s[i:i + 97]]
                             for i in range(0, len(s) - 97 + 1)], dtype=np.int64)
            rows.append((f"{name} plaintext 97-grams (n={len(wins)})", quad_batch(wins)))
        else:
            rows.append((f"{name} plaintext whole ({len(s)} letters)",
                         np.array([quad(s)])))
    # random uniform
    ru = rng.integers(0, 26, size=(20000, 97))
    rows.append(("uniform random 97-grams (n=20000)", quad_batch(ru)))
    # random with English unigram frequencies
    f = np.array([8.17,1.49,2.78,4.25,12.70,2.23,2.02,6.09,6.97,0.15,0.77,4.03,2.41,
                  6.75,7.51,1.93,0.10,5.99,6.33,9.06,2.76,0.98,2.36,0.15,1.97,0.07])
    f = f / f.sum()
    rf = rng.choice(26, size=(20000, 97), p=f)
    rows.append(("unigram-random 97-grams (n=20000)", quad_batch(rf)))
    # K4 ciphertext itself
    with open(os.path.join(DATA, "k4_ciphertext.txt")) as fh:
        ct = re.sub("[^A-Z]", "", fh.read().upper())
    rows.append(("K4 CIPHERTEXT (n=1)", np.array([quad(ct)])))
    print(f"{'text':44s} {'mean':>7s} {'sd':>6s} {'p1':>7s} {'p50':>7s} {'p99':>7s} {'max':>7s}")
    for name, arr in rows:
        print(f"{name:44s} {arr.mean():7.3f} {arr.std():6.3f} "
              f"{np.percentile(arr,1):7.3f} {np.percentile(arr,50):7.3f} "
              f"{np.percentile(arr,99):7.3f} {arr.max():7.3f}")
    print()
    print("Separation: English mean - uniform mean = "
          f"{rows[0][1].mean() - rows[4][1].mean():.3f} log10 units/letter; "
          f"sd of English = {rows[0][1].std():.3f}")
    return rows

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "calibrate"
    if cmd == "build":
        build_model(rebuild=True)
    calibrate()
