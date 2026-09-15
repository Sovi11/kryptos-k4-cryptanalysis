"""search_recur.py -- (c) mapping the space of crib-consistent English plaintexts.

Runs the crib-pinned annealer many independent times and asks: do particular WORDS
recur across independent runs, and -- the part that actually matters -- do they recur
MORE than in matched control conditions where the pinned letters carry no K4 information?

Conditions (all identical except for what is pinned / what corpus the LM saw):

  k4        24 Sanborn crib letters at their true positions          [the hypothesis]
  ctlfreq   24 letters drawn from English unigram frequencies at the SAME positions
  ctlword   real English words of the same block lengths (13 and 11) at the SAME positions
  ctlshuf   the SAME 24 crib letters, at 24 randomly chosen positions
  k4_man    k4 pins, but the LM trained only on man pages
  k4_doc    k4 pins, but the LM trained only on doc/info prose

If a word recurs in `k4` at the same rate as in `ctlfreq`/`ctlword`, its recurrence is a
property of the language model's training corpus, not of K4.  If the `k4_man` and
`k4_doc` vocabularies differ from `k4`, the vocabulary is corpus-driven, full stop.

Usage:
    python3.13 search_recur.py run  [restarts] [steps]
    python3.13 search_recur.py report
"""
import json, os, random, re, subprocess, sys
from collections import Counter, defaultdict
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
sys.path.insert(0, HERE)
import search_anneal as SA

A2Z = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
OUT = os.path.join(HERE, "search_recur.json")

# words the task asks about explicitly, plus the obvious Kryptos-thematic set
WATCH = ["COMPASS", "ROSE", "POSITION", "LATITUDE", "LONGITUDE", "LAYER", "INVISIBLE",
         "SHADOW", "BERLIN", "CLOCK", "NORTH", "EAST", "SOUTH", "WEST", "HERE", "THERE",
         "BURIED", "MAGNETIC", "LANGLEY", "SHADOWS", "MEMORY", "LUCID", "DIGITAL",
         "VIRTUALLY", "SECRET", "MESSAGE", "LIGHT", "TIME", "HOUR", "DEGREE", "DEGREES",
         "GRID", "POINT", "BEARING", "WALL", "EGYPT", "TOMB", "STONE", "WATER", "COPPER"]

def load_words(minlen=5):
    w = set()
    with open("/usr/share/dict/words") as f:
        for x in f:
            x = x.strip().upper()
            if len(x) >= minlen and x.isalpha() and x.isascii():
                w.add(x)
    return w

def words_in(s, vocab, minlen=5, maxlen=12):
    """All dictionary words >= minlen occurring as substrings, with start offsets."""
    out = []
    for i in range(len(s)):
        for L in range(minlen, min(maxlen, len(s) - i) + 1):
            sub = s[i:i + L]
            if sub in vocab:
                out.append((i, sub))
    return out

# ------------------------------------------------------------------ pin sets
def pins_k4(_seed):
    return dict(SA.CRIB)

def pins_freq(seed):
    return SA.random_fixed(seed)

def pins_word(seed):
    return SA.crib_word_control(seed)

def pins_shuf(seed):
    rnd = random.Random(seed)
    posns = rnd.sample(range(97), 24)
    letters = [SA.CRIB[p] for p in SA.CRIB_POS]
    return {p: c for p, c in zip(sorted(posns), letters)}

CONDITIONS = {
    "k4":      (pins_k4,   "all"),
    "ctlfreq": (pins_freq, "all"),
    "ctlword": (pins_word, "all"),
    "ctlshuf": (pins_shuf, "all"),
    "k4_man":  (pins_k4,   "man"),
    "k4_doc":  (pins_k4,   "docinfo"),
}

# ------------------------------------------------------------------ workers
def _job(a):
    fixed, seed, steps = a
    return SA.anneal(fixed, seed, steps)

def run_condition(name, restarts, steps, procs=8):
    pinf, variant = CONDITIONS[name]
    if variant != "all":
        # re-exec with the corpus variant selected, so the LM tables differ
        cmd = [sys.executable, __file__, "_child", name, str(restarts), str(steps)]
        env = dict(os.environ, K4_LM=variant)
        r = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if r.returncode != 0:
            print(r.stdout[-3000:], r.stderr[-3000:])
            raise SystemExit(f"child for {name} failed")
        return json.loads(r.stdout.strip().splitlines()[-1])
    args = [(pinf(1000 + i), i * 7919 + 13, steps) for i in range(restarts)]
    with Pool(procs) as pool:
        out = pool.map(_job, args, chunksize=1)
    return out

def run_all(restarts=600, steps=400_000):
    res = {}
    for name in CONDITIONS:
        print(f"--- {name}: {restarts} independent restarts x {steps} steps", flush=True)
        r = run_condition(name, restarts, steps)
        res[name] = r
        sc = [s for s, _ in r]
        print(f"    score mean {sum(sc)/len(sc):.4f}  max {max(sc):.4f}", flush=True)
    with open(OUT, "w") as f:
        json.dump(res, f)
    return res

# ------------------------------------------------------------------ report
def report():
    with open(OUT) as f:
        res = json.load(f)
    vocab = load_words(5)
    print("=" * 100)
    print("TABLE C1 -- annealer score by condition (mean log10 P/letter; higher = 'more English')")
    print("=" * 100)
    print(f"{'condition':10s} {'runs':>5s} {'mean':>8s} {'sd':>7s} {'max':>8s}")
    import statistics as st
    for name, r in res.items():
        sc = [s for s, _ in r]
        print(f"{name:10s} {len(sc):5d} {st.mean(sc):8.4f} {st.pstdev(sc):7.4f} {max(sc):8.4f}")
    print()
    print("Reference: held-out English 97-grams -0.741 +- 0.077; K1-K3 Sanborn plaintext -0.967;")
    print("crib-pinned random -1.646.  Every condition lands ABOVE real English: the annealer")
    print("overfits by construction, so its score cannot be used as evidence for any plaintext.")
    print()

    # word recurrence, per condition
    percond = {}
    for name, r in res.items():
        cnt = Counter()
        posn = defaultdict(Counter)
        for _s, txt in r:
            seen = set()
            for i, w in words_in(txt, vocab):
                if w not in seen:
                    cnt[w] += 1
                    seen.add(w)
                posn[w][i] += 1
        percond[name] = (cnt, posn, len(r))

    print("=" * 100)
    print("TABLE C2 -- most recurrent dictionary words (>=5 letters), by condition")
    print("            'runs%' = share of that condition's independent runs containing the word")
    print("=" * 100)
    k4c, _, k4n = percond["k4"]
    top = [w for w, _ in k4c.most_common(30)]
    hdr = f"{'word':14s}"
    for name in res:
        hdr += f" {name:>9s}"
    print(hdr)
    for w in top:
        line = f"{w:14s}"
        for name in res:
            c, _, n = percond[name]
            line += f" {100.0*c[w]/n:8.1f}%"
        print(line)
    print()

    print("=" * 100)
    print("TABLE C3 -- the words the task asked about specifically")
    print("=" * 100)
    hdr = f"{'word':12s}"
    for name in res:
        hdr += f" {name:>9s}"
    print(hdr)
    for w in WATCH:
        row = [percond[name][0][w] for name in res]
        if sum(row) == 0:
            continue
        line = f"{w:12s}"
        for name in res:
            c, _, n = percond[name]
            line += f" {100.0*c[w]/n:8.2f}%"
        print(line)
    print()

    # vocabulary overlap between conditions -- is the vocabulary K4's or the corpus's?
    print("=" * 100)
    print("TABLE C4 -- Jaccard overlap of the top-100 word vocabularies between conditions")
    print("=" * 100)
    tops = {name: set(w for w, _ in percond[name][0].most_common(100)) for name in res}
    names = list(res)
    print(f"{'':10s}" + "".join(f"{n:>10s}" for n in names))
    for a in names:
        line = f"{a:10s}"
        for b in names:
            j = len(tops[a] & tops[b]) / len(tops[a] | tops[b])
            line += f"{j:10.2f}"
        print(line)
    print()
    print("Read C4 as: high overlap between k4 and the ctl* conditions means the recurring")
    print("vocabulary is produced by the language model, not by the K4 constraint.  Low overlap")
    print("between k4 and k4_man / k4_doc means the vocabulary tracks the TRAINING CORPUS.")
    print()

    # positional stability: does any word recur at the SAME position?
    print("=" * 100)
    print("TABLE C5 -- positionally stable words in the k4 condition")
    print("            (word, most common start offset 1-indexed, runs at that offset)")
    print("=" * 100)
    _, k4p, n = percond["k4"]
    rows = []
    for w, pc in k4p.items():
        off, c = pc.most_common(1)[0]
        if c >= 0.02 * n and len(w) >= 5:
            rows.append((c, w, off + 1, len(w)))
    rows.sort(reverse=True)
    print(f"{'word':14s} {'start':>6s} {'runs':>6s} {'runs%':>7s}")
    for c, w, off, _ in rows[:25]:
        print(f"{w:14s} {off:6d} {c:6d} {100.0*c/n:6.1f}%")
    if not rows:
        print("   (none above 2% of runs)")
    print()
    # the same for the strongest control, as the null
    _, cp, cn = percond["ctlfreq"]
    rows = []
    for w, pc in cp.items():
        off, c = pc.most_common(1)[0]
        if c >= 0.02 * cn and len(w) >= 5:
            rows.append((c, w, off + 1))
    rows.sort(reverse=True)
    print("   NULL (ctlfreq condition), same statistic:")
    for c, w, off in rows[:10]:
        print(f"   {w:14s} {off:6d} {c:6d} {100.0*c/cn:6.1f}%")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    if mode == "_child":
        name, restarts, steps = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
        pinf, _ = CONDITIONS[name]
        args = [(pinf(1000 + i), i * 7919 + 13, steps) for i in range(restarts)]
        with Pool(8) as pool:
            out = pool.map(_job, args, chunksize=1)
        print(json.dumps(out))
    elif mode == "run":
        a = [int(x) for x in sys.argv[2:]]
        run_all(*(a or [600, 400_000]))
        report()
    else:
        report()
