#!/usr/bin/env python3
"""ADVERSARIAL VERIFICATION part 2 -- independent Monte-Carlo nulls and omnibus.

Written from scratch; imports nothing from this repo.  Generates a large sample
of null 97-letter strings under two nulls (uniform, and shuffles of K4's own
letter multiset), records a full battery per replicate, and then:

  * reproduces every family-wise p in findings/statistics.md,
  * re-runs the min-p omnibus with an UNBIASED split-sample estimator,
  * stress-tests the omnibus against the analyst choices that were made
    (period range, battery membership, one- vs two-sided, combination rule),
  * computes a GLOBAL family-wise correction over every scanned choice at once.
"""
import math
import os
import pickle
import random
import sys
from collections import Counter
from multiprocessing import Pool

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
N = 97
V4 = bytes(ord(c) - 65 for c in K4)
HERE = os.path.dirname(os.path.abspath(__file__))

NREP = int(os.environ.get("ADV_NREP", "400000"))
NPROC = min(8, os.cpu_count() or 4)
LAGSETS = [(1, 24), (1, 30), (1, 48), (1, 67), (1, 96)]
PERSETS = [(2, 30), (2, 48)]
WIDTHS = list(range(2, 49))

# exact binomial survival table: BSF[m][k] = P(Binom(m,1/26) >= k)
_BSF = []
for m in range(N + 1):
    pmf = [0.0] * (m + 1)
    lp, lq = math.log(1 / 26), math.log(25 / 26)
    for k in range(m + 1):
        pmf[k] = math.exp(math.lgamma(m + 1) - math.lgamma(k + 1) - math.lgamma(m - k + 1)
                          + k * lp + (m - k) * lq)
    sf = [0.0] * (m + 2)
    for k in range(m, -1, -1):
        sf[k] = sf[k + 1] + pmf[k]
    _BSF.append(sf)

_SD = {m: math.sqrt(m * (1 / 26) * (25 / 26)) for m in range(1, N + 1)}


def col_pairs(n, p):
    q, r = divmod(n, p)
    return r * (q + 1) * q + (p - r) * q * (q - 1)


_D = {p: col_pairs(N, p) for p in range(2, 49)}
_PSD = {p: math.sqrt(2 * (1 / 26) * (25 / 26) / _D[p]) for p in _D}


def battery(b):
    n = len(b)
    cnt = Counter(b)
    S = sum(k * (k - 1) for k in cnt.values())
    # full autocorrelation spectrum
    spec = [0] * n
    ib = int.from_bytes(b, "big")
    for d in range(1, n):
        m = n - d
        x = (ib >> (8 * d)) ^ (ib & ((1 << (8 * m)) - 1))
        spec[d] = x.to_bytes(m, "big").count(0)
    out = {"S": S, "ioc": S / (n * (n - 1)), "distinct": len(cnt), "doubles": spec[1]}
    # autocorrelation maxima and min exact-p over lag ranges
    zz = [0.0] * n
    pp = [1.0] * n
    for d in range(1, n):
        m = n - d
        zz[d] = (spec[d] - m / 26) / _SD[m]
        pp[d] = _BSF[m][spec[d]]
    for lo, hi in LAGSETS:
        out[f"maxz_{lo}_{hi}"] = max(zz[lo:hi + 1])
        out[f"minp_{lo}_{hi}"] = min(pp[lo:hi + 1])
    # periodic IoC z
    pz = {}
    for p in range(2, 49):
        s = 2 * sum(spec[d] for d in range(p, n, p))
        pz[p] = (s / _D[p] - 1 / 26) / _PSD[p]
    for lo, hi in PERSETS:
        out[f"maxperz_{lo}_{hi}"] = max(pz[p] for p in range(lo, hi + 1))
    # repeated n-grams
    out["bigrams"] = sum(v * (v - 1) // 2 for v in Counter(b[i:i + 2] for i in range(n - 1)).values())
    out["trigrams"] = sum(v * (v - 1) // 2 for v in Counter(b[i:i + 3] for i in range(n - 2)).values())
    out["chi2u"] = sum((cnt.get(i, 0) - n / 26) ** 2 / (n / 26) for i in range(26))
    # column bigrams
    bp21 = be21 = 0
    mxp = mxe = -1
    for w in WIDTHS:
        c = Counter(b[i:i + 1] + b[i + w:i + w + 1] for i in range(n - w))
        pr = sum(v * (v - 1) // 2 for v in c.values())
        ex = sum(v - 1 for v in c.values())
        if w == 21:
            bp21, be21 = pr, ex
        if pr > mxp:
            mxp = pr
        if ex > mxe:
            mxe = ex
    out["colb21_pairs"], out["colb21_excess"] = bp21, be21
    out["colbmax_pairs"], out["colbmax_excess"] = mxp, mxe
    # doubles mod-class concentration: max over moduli 2..48 of largest residue class
    dp = [i + 1 for i in range(n - 1) if b[i] == b[i + 1]]
    best = 0
    if dp:
        for mod in range(2, 49):
            c = Counter(p % mod for p in dp)
            if c.most_common(1)[0][1] > best:
                best = c.most_common(1)[0][1]
    out["ndoub"] = len(dp)
    out["modmax"] = best
    return out


KEYS = None


def _chunk(arg):
    seed, k, mode = arg
    rng = random.Random(seed)
    rows = []
    pool = list(V4)
    for _ in range(k):
        if mode == "uniform":
            b = bytes(rng.randrange(26) for _ in range(N))
        else:
            rng.shuffle(pool)
            b = bytes(pool)
        rows.append(battery(b))
    keys = sorted(rows[0])
    return keys, [[r[kk] for kk in keys] for r in rows]


def run(mode, nrep, seed0):
    per = nrep // NPROC
    args = [(seed0 + 1013 * i, per, mode) for i in range(NPROC)]
    with Pool(NPROC) as pl:
        parts = pl.map(_chunk, args, chunksize=1)
    keys = parts[0][0]
    from array import array
    INTK = {"S", "distinct", "doubles", "bigrams", "trigrams", "colb21_pairs",
            "colb21_excess", "colbmax_pairs", "colbmax_excess", "ndoub", "modmax"}
    cols = {k: array("i" if k in INTK else "d") for k in keys}
    for _keys, rows in parts:
        assert _keys == keys
        for r in rows:
            for k, v in zip(keys, r):
                cols[k].append(v)
    return cols


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "uniform"
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 777001
    obs = battery(V4)
    print(f"K4 observed battery:")
    for k in sorted(obs):
        print(f"   {k:18s} {obs[k]}")
    print(f"\nrunning {NREP:,} replicates, null={mode}, {NPROC} procs ...")
    import time
    t0 = time.time()
    cols = run(mode, NREP, seed0)
    print(f"done in {time.time()-t0:.1f}s")
    with open(os.path.join(HERE, f"adv_null_{mode}.pkl"), "wb") as f:
        pickle.dump({"obs": obs, "cols": {k: v.tobytes() for k, v in cols.items()},
                     "types": {k: v.typecode for k, v in cols.items()},
                     "nrep": len(cols["ioc"]), "mode": mode}, f, protocol=4)
    print(f"saved adv_null_{mode}.pkl  ({len(cols['ioc']):,} replicates)")
