"""search_anneal.py -- simulated annealing over the 73 unknown K4 plaintext letters.

The 24 Sanborn crib letters are held fixed; the remaining 73 are optimised to
maximise the calibrated character language model of search_lm.py.

This is a HYPOTHESIS GENERATOR, not a solver: the optimiser will happily invent
fluent English that has nothing to do with K4.  Every run therefore has a matched
control (the same optimisation with the 24 fixed letters replaced by a random
English-like pattern) so that the achieved score can be read against a null.

Usage:
    python3.13 search_anneal.py run  [n_restarts] [steps]
    python3.13 search_anneal.py control [n_restarts] [steps]
"""
import json, math, os, random, re, sys
import multiprocessing as _mp
try:
    _mp.set_start_method("fork")
except RuntimeError:
    pass
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
sys.path.insert(0, HERE)
import search_lm

A2Z = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

with open(os.path.join(DATA, "k4_ciphertext.txt")) as f:
    CT = re.sub("[^A-Z]", "", f.read().upper())
assert len(CT) == 97
with open(os.path.join(DATA, "cribs.json")) as f:
    _cribs = json.load(f)["cribs"]
CRIB = {}
for c in _cribs:
    st = c["pos"] - 1
    assert CT[st:st + len(c["ct"])] == c["ct"]
    for k, p in enumerate(c["pt"]):
        CRIB[st + k] = p
CRIB_POS = sorted(CRIB)
FREE = [i for i in range(97) if i not in CRIB]
assert len(CRIB_POS) == 24 and len(FREE) == 73

# ---------------------------------------------------------------- fast LM
_QL = None
def qtab():
    """quadgram conditional log10 table as a flat python list (fast scalar indexing)"""
    global _QL
    if _QL is None:
        Q, _, _ = search_lm.load()
        _QL = Q.astype("float64").tolist()
    return _QL

def score_sum(codes, Q):
    s = 0.0
    for i in range(len(codes) - 3):
        s += Q[((codes[i] * 26 + codes[i+1]) * 26 + codes[i+2]) * 26 + codes[i+3]]
    return s

def local_sum(codes, pos, Q):
    """sum of the (up to 4) quadgram terms that involve index `pos`"""
    s = 0.0
    lo = max(0, pos - 3); hi = min(len(codes) - 4, pos)
    for i in range(lo, hi + 1):
        s += Q[((codes[i] * 26 + codes[i+1]) * 26 + codes[i+2]) * 26 + codes[i+3]]
    return s

def anneal(fixed, seed, steps=300_000, t0=1.2, t1=0.02):
    """fixed: dict pos->letter.  Returns (score_per_letter, plaintext)."""
    Q = qtab()
    rnd = random.Random(seed)
    n = 97
    free = [i for i in range(n) if i not in fixed]
    codes = [rnd.randrange(26) for _ in range(n)]
    for p, ch in fixed.items():
        codes[p] = ord(ch) - 65
    cur = score_sum(codes, Q)
    best = cur; bestc = codes[:]
    for step in range(steps):
        T = t0 * (t1 / t0) ** (step / steps)
        pos = free[rnd.randrange(len(free))]
        old = codes[pos]
        new = rnd.randrange(26)
        if new == old:
            continue
        before = local_sum(codes, pos, Q)
        codes[pos] = new
        after = local_sum(codes, pos, Q)
        d = after - before
        if d >= 0 or rnd.random() < math.exp(d / T):
            cur += d
            if cur > best:
                best = cur; bestc = codes[:]
        else:
            codes[pos] = old
    # greedy polish from the best state
    codes = bestc[:]
    cur = best
    improved = True
    while improved:
        improved = False
        for pos in free:
            old = codes[pos]
            before = local_sum(codes, pos, Q)
            bestl, bestd = old, 0.0
            for new in range(26):
                if new == old:
                    continue
                codes[pos] = new
                d = local_sum(codes, pos, Q) - before
                if d > bestd:
                    bestd, bestl = d, new
            codes[pos] = bestl
            if bestl != old:
                cur += bestd
                improved = True
    txt = "".join(A2Z[c] for c in codes)
    return cur / 94.0, txt

def _job(args):
    fixed, seed, steps = args
    return anneal(fixed, seed, steps)

def run_many(fixed, n_restarts, steps, procs=8, seed0=0):
    qtab()          # build the LM table BEFORE forking so workers inherit it
    args = [(fixed, seed0 + i, steps) for i in range(n_restarts)]
    with Pool(procs) as pool:
        out = pool.map(_job, args, chunksize=1)
    out.sort(key=lambda t: -t[0])
    return out

def random_fixed(seed):
    """control: 24 letters at the SAME positions, drawn from English letter frequencies"""
    f = [8.17,1.49,2.78,4.25,12.70,2.23,2.02,6.09,6.97,0.15,0.77,4.03,2.41,
         6.75,7.51,1.93,0.10,5.99,6.33,9.06,2.76,0.98,2.36,0.15,1.97,0.07]
    tot = sum(f)
    rnd = random.Random(seed)
    def pick():
        x = rnd.random() * tot; acc = 0.0
        for i, v in enumerate(f):
            acc += v
            if x <= acc:
                return A2Z[i]
        return "E"
    return {p: pick() for p in CRIB_POS}

def crib_word_control(seed):
    """control: real English words of the same lengths at the same positions."""
    rnd = random.Random(seed)
    # 22-34 is a 13-letter run, 64-74 an 11-letter run
    pool13 = ["NORTHEASTERNX","UNDERGROUNDSX","INFORMATIONXX","MAGNETICFIELD",
              "INVISIBLEXXXX","POSITIONXXXXX","LATITUDEXXXXX","COMPASSROSEXX",
              "THESHADOWFORC","LONGITUDEXXXX"]
    pool11 = ["WARSAWCLOCK","LAYERTWOXXX","LODESTONEXX","LANGLEYXXXX","MAGNETICXXX",
              "SHADOWFORCE","DIGITALXXXX","MEMORYXXXXX","VIRTUALLYXX","INTERPRETAT"]
    a = rnd.choice(pool13)[:13]; b = rnd.choice(pool11)[:11]
    d = {}
    for k in range(13):
        d[21 + k] = a[k]
    for k in range(11):
        d[63 + k] = b[k]
    return d

if __name__ == "__main__":
    import numpy as np
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    nres = int(sys.argv[2]) if len(sys.argv) > 2 else 64
    steps = int(sys.argv[3]) if len(sys.argv) > 3 else 300_000
    if mode == "run":
        res = run_many(CRIB, nres, steps)
        print(f"# K4 cribs fixed, {nres} restarts x {steps} steps")
        for s, t in res[:20]:
            print(f"{s:8.4f}  {t}")
        sc = [s for s, _ in res]
        print(f"# mean {sum(sc)/len(sc):.4f}  best {max(sc):.4f}")
        with open(os.path.join(HERE, "search_anneal_k4.json"), "w") as f:
            json.dump(res, f)
    elif mode == "control":
        allres = []
        for k in range(nres):
            fixed = random_fixed(1000 + k)
            r = run_many(fixed, 8, steps, seed0=k * 100)
            allres.append((max(s for s, _ in r), "".join(fixed[p] for p in CRIB_POS)))
            print(f"control {k}: best {allres[-1][0]:.4f}  fixed={allres[-1][1]}")
        sc = [s for s, _ in allres]
        print(f"# CONTROL mean-of-best {sum(sc)/len(sc):.4f}  max {max(sc):.4f}")
        with open(os.path.join(HERE, "search_anneal_control.json"), "w") as f:
            json.dump(allres, f)
