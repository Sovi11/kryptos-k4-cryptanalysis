"""Shared utilities for the two-cipher (substitution + transposition) K4 tests.

Conventions
-----------
* All positions are 0-indexed internally.  The data files are 1-indexed; we
  convert once, here.
* A transposition T is a tuple of length 97 with T[j] = ciphertext position that
  intermediate (pre-transposition) position j is moved to.  So  ct[T[j]] = inter[j]
  and  inter[j] = ct[T[j]];  the inverse Tinv[c] = j.
* A "periodic substitution" is described by (family, PA, CA, period) where
      Vigenere-type :  ct = CA[(PA.index(pt) + s) % 26]
      Beaufort-type :  ct = CA[(s - PA.index(pt)) % 26]
  with s the key shift for the column (pos % period).  PA/CA are the plaintext /
  ciphertext alphabets (26-letter strings).  PA == CA == plain is ordinary Vigenere
  / Beaufort; PA == CA == KRYPTOS-keyed is the K1/K2 system (a.k.a. Quagmire III
  with identical alphabets); PA plain/CA keyed or vice versa are Quagmire II / I.
  Variant Beaufort (ct = CA[(PA.index(pt) - s)]) is consistent iff Vigenere is, so
  it is not tested separately.
"""
import json, os, re, math, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")

PLAIN = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRYPTOS = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

def keyed_alphabet(word):
    seen = []
    for ch in (word.upper() + PLAIN):
        if ch.isalpha() and ch not in seen:
            seen.append(ch)
    return "".join(seen)

assert keyed_alphabet("KRYPTOS") == KRYPTOS

with open(os.path.join(DATA, "k4_ciphertext.txt")) as f:
    CT = "".join(ch for ch in f.read() if ch.isalpha()).upper()
N = len(CT)
assert N == 97, N

with open(os.path.join(DATA, "cribs.json")) as f:
    _cj = json.load(f)
# list of (pos0, ct, pt, name)
CRIB_WORDS = [(c["pos"] - 1, c["ct"], c["pt"], c["pt"]) for c in _cj["cribs"]]
for p, ctw, ptw, _ in CRIB_WORDS:
    assert CT[p:p + len(ctw)] == ctw, (p, ctw, CT[p:p + len(ctw)])
# per-letter cribs: list of (ct_pos, ct_letter, pt_letter)
CRIBS = [(p + k, ctw[k], ptw[k]) for p, ctw, ptw, _ in CRIB_WORDS for k in range(len(ctw))]
assert len(CRIBS) == 24

# ---------------------------------------------------------------- periodic test
FAMILIES = ("vig", "beau")

def shift_for(family, PA, CA, pt, ct):
    """Key shift s implied by one (pt, ct) pair under the given family/alphabets."""
    a = PA.index(pt); b = CA.index(ct)
    if family == "vig":
        return (b - a) % 26
    else:  # beaufort: b = s - a
        return (a + b) % 26

def periodic_consistency(pairs, period, family, PA, CA):
    """pairs: iterable of (position, ct_letter, pt_letter).
    Returns (ok, key_dict, n_constraints) where key_dict maps column -> shift and
    n_constraints is the number of *non-trivial* checks performed (pairs that hit a
    column already fixed by an earlier pair).  ok is True iff every check passed.
    A result with n_constraints == 0 is vacuous."""
    key = {}
    checks = 0
    for pos, ct, pt in pairs:
        col = pos % period
        s = shift_for(family, PA, CA, pt, ct)
        if col in key:
            checks += 1
            if key[col] != s:
                return False, key, checks
        else:
            key[col] = s
    return True, key, checks

def decrypt_periodic(text, key, period, family, PA, CA, unknown="."):
    out = []
    for i, ch in enumerate(text):
        col = i % period
        if col not in key:
            out.append(unknown); continue
        s = key[col]; b = CA.index(ch)
        if family == "vig":
            out.append(PA[(b - s) % 26])
        else:
            out.append(PA[(s - b) % 26])
    return "".join(out)

ALPHABET_SETS = {
    "plain/plain": (PLAIN, PLAIN),
    "kryptos/kryptos": (KRYPTOS, KRYPTOS),
    "kryptos-pt/plain-ct (QuagI)": (KRYPTOS, PLAIN),
    "plain-pt/kryptos-ct (QuagII)": (PLAIN, KRYPTOS),
}

def run_periodic_battery(pairs, periods=range(2, 27), alphabet_sets=None, families=FAMILIES):
    """Return list of survivors (period, family, alphabet_name, key, checks)."""
    alphabet_sets = alphabet_sets or ALPHABET_SETS
    out = []
    for period in periods:
        for fam in families:
            for aname, (PA, CA) in alphabet_sets.items():
                ok, key, checks = periodic_consistency(pairs, period, fam, PA, CA)
                if ok:
                    out.append((period, fam, aname, key, checks))
    return out

# ---------------------------------------------------------------- dictionary
def load_words(minlen=1, maxlen=99):
    words = set()
    try:
        with open("/usr/share/dict/words") as f:
            for w in f:
                w = w.strip().upper()
                if w.isalpha() and minlen <= len(w) <= maxlen:
                    words.add(w)
    except FileNotFoundError:
        pass
    # words from the data files
    for fn in os.listdir(DATA):
        with open(os.path.join(DATA, fn)) as f:
            for w in re.findall(r"[A-Za-z]+", f.read()):
                w = w.upper()
                if minlen <= len(w) <= maxlen:
                    words.add(w)
    return words

# ---------------------------------------------------------------- English scoring
_QUAD = None
_QUAD_FLOOR = None

def _build_quadgram_model():
    """Train a quadgram log-probability model on English prose available offline:
    the K1-K3 plaintexts plus the docstrings of the Python standard library
    (several hundred KB of ordinary English).  Cached to the scratch dir."""
    global _QUAD, _QUAD_FLOOR
    cache = os.path.join(HERE, ".quadgrams_cache.json")
    if os.path.exists(cache):
        with open(cache) as f:
            d = json.load(f)
        _QUAD = d["q"]; _QUAD_FLOOR = d["floor"]
        return
    import pkgutil, importlib, io, contextlib
    corpus = []
    with open(os.path.join(DATA, "k1_k3_plaintext.txt")) as f:
        for line in f:
            if not line.startswith("#"):
                corpus.append(line)
    for m in pkgutil.iter_modules():
        name = m.name
        if name.startswith("_") or name in ("antigravity", "this", "idlelib", "turtledemo", "tkinter"):
            continue
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                mod = importlib.import_module(name)
        except BaseException:
            continue
        doc = getattr(mod, "__doc__", None)
        if isinstance(doc, str):
            corpus.append(doc)
        for attr in dir(mod):
            try:
                obj = getattr(mod, attr)
                d = getattr(obj, "__doc__", None)
                if isinstance(d, str) and len(d) > 40:
                    corpus.append(d)
            except BaseException:
                pass
    text = re.sub(r"[^A-Z]", "", " ".join(corpus).upper())
    counts = defaultdict(int)
    for i in range(len(text) - 3):
        counts[text[i:i + 4]] += 1
    total = sum(counts.values())
    q = {k: math.log10(v / total) for k, v in counts.items()}
    floor = math.log10(0.01 / total)
    with open(cache, "w") as f:
        json.dump({"q": q, "floor": floor, "corpus_letters": len(text)}, f)
    _QUAD = q; _QUAD_FLOOR = floor

def quadgram_score(text):
    """Average quadgram log10 probability per quadgram (higher = more English-like).
    Only letters A-Z are scored; '.' unknowns are skipped by scoring runs."""
    if _QUAD is None:
        _build_quadgram_model()
    tot = 0.0; n = 0
    for run in re.findall(r"[A-Z]+", text):
        for i in range(len(run) - 3):
            tot += _QUAD.get(run[i:i + 4], _QUAD_FLOOR); n += 1
    return tot / n if n else float("nan")

_WORDS = None
def word_coverage(text, minlen=3):
    """Fraction of letters covered by a maximal non-overlapping tiling of dictionary
    words (length >= minlen), via DP.  Random text scores ~0.3-0.45; English ~0.9+."""
    global _WORDS
    if _WORDS is None:
        _WORDS = load_words(minlen=minlen)
    n = len(text)
    best = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        best[i] = best[i + 1]
        for L in range(minlen, min(24, n - i) + 1):
            if text[i:i + L] in _WORDS:
                best[i] = max(best[i], L + best[i + L])
    return best[0] / n if n else 0.0

def english_judgement(text):
    """Calibrated on 97-letter windows: English quadgram mean -4.69 (sd 0.16),
    uniform-random -8.23 (sd 0.12), unigram-frequency-random -7.46 (sd 0.25);
    word coverage: English 0.94 (sd 0.02), random 0.20 (sd 0.07)."""
    q = quadgram_score(text); w = word_coverage(text)
    if q > -5.3 and w > 0.8:
        verdict = "looks like English"
    elif q > -6.5 or w > 0.6:
        verdict = "weakly English-like (partial / probably chance)"
    else:
        verdict = "not English"
    return q, w, verdict

if __name__ == "__main__":
    print(CT)
    print(CRIBS)
    for t in [CT, "SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVED",
              "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOGANDTHENRUNSAWAYINTOTHEFOREST"]:
        print(english_judgement(t), t[:40])
