#!/usr/bin/env python3
"""ADVERSARIAL VERIFICATION part 4 -- (i) the one number that did not reproduce,
(ii) POWER of the omnibus: does this machinery detect structure when it is there?

A negative result is worthless without power, and the report gives power figures
for the INDIVIDUAL tests (its section 8) but never for the OMNIBUS that carries
its headline conclusion.  This supplies it.
"""
import bisect
import math
import os
import pickle
import random
from array import array
from collections import Counter
from multiprocessing import Pool

import adv_verify_stats_mc as M     # reuse only MY OWN battery implementation

HERE = os.path.dirname(os.path.abspath(__file__))
NPROC = min(8, os.cpu_count() or 4)


# ----------------------------------------------------- (i) mod-class null ---
def _mod_chunk(args):
    seed, trials, k, Mx, r = args
    rng = random.Random(seed)
    hits = 0
    hits_all = 0
    for _ in range(trials):
        pos = rng.sample(range(1, 97), k)
        best = 0
        for mod in range(2, Mx + 1):
            c = Counter(p % mod for p in pos)
            b = c.most_common(1)[0][1]
            if b > best:
                best = b
        if best >= r:
            hits += 1
        if best >= k:
            hits_all += 1
    return hits, hits_all, trials


def modclass():
    print("--- (i) the doubles mod-class null, CONDITIONED on 6 doubles --------")
    print("    (my unconditional run gave 0.083; the report's null draws exactly 6")
    print("     positions uniformly from 1..96, which is the right conditioning.)")
    per = 1_000_000 // NPROC
    args = [(555_000 + 97 * i, per, 6, 48, 5) for i in range(NPROC)]
    with Pool(NPROC) as pl:
        res = pl.map(_mod_chunk, args)
    h = sum(r[0] for r in res); ha = sum(r[1] for r in res); t = sum(r[2] for r in res)
    print(f"    {t:,} trials: P(some modulus 2..48 collects >=5 of 6) = {h/t:.4f} "
          f"(report 0.2452)")
    print(f"                 P(some modulus collects all 6)          = {ha/t:.4f} "
          f"(report 0.0295)")
    naive = 7 * (math.comb(6, 5) * (1/7)**5 * (6/7) + (1/7)**6)
    print(f"    naive pre-selection p for mod 7 alone = {naive:.5f} (report 0.0022)")


# ------------------------------------------------------------ (ii) power ----
BAT = ["ioc", "distinct", "doubles", "maxz_1_48", "maxperz_2_30", "bigrams", "trigrams"]
BAT48 = ["ioc", "distinct", "doubles", "maxz_1_48", "maxperz_2_48", "bigrams", "trigrams"]
CB = BAT48


def load_null():
    with open(os.path.join(HERE, "adv_null_uniform.pkl"), "rb") as f:
        d = pickle.load(f)
    cols = {}
    for k, raw in d["cols"].items():
        a = array(d["types"][k]); a.frombytes(raw); cols[k] = a
    return d["obs"], cols, d["nrep"]


_CORP = None
def _init():
    global _CORP
    _CORP = open(os.path.join(HERE, ".stat_corpus.bin"), "rb").read()


def _pow_chunk(args):
    seed, trials, mode, L = args
    rng = random.Random(seed)
    hi = len(_CORP) - 100
    rows = []
    for _ in range(trials):
        j = rng.randrange(hi)
        pt = _CORP[j:j + 97]
        if mode == "vig":
            key = bytes(rng.randrange(26) for _ in range(L))
            ct = bytes((pt[i] + key[i % L]) % 26 for i in range(97))
        elif mode == "otp":
            ct = bytes((pt[i] + rng.randrange(26)) % 26 for i in range(97))
        elif mode == "english":
            ct = pt
        elif mode == "transp":
            idx = list(range(97)); rng.shuffle(idx)
            ct = bytes(pt[i] for i in idx)
        elif mode == "autokey":
            primer = bytes(rng.randrange(26) for _ in range(L))
            ks = primer + pt
            ct = bytes((pt[i] + ks[i]) % 26 for i in range(97))
        b = M.battery(ct)
        rows.append([b[k] for k in sorted(b)])
    return sorted(M.battery(bytes(97))), rows


def power():
    obs, cols, nrep = load_null()
    half = nrep // 2
    srtA = {k: sorted(cols[k][:half]) for k in set(BAT) | set(BAT48)}

    def two(k, x):
        sv = srtA[k]
        lo = bisect.bisect_right(sv, x) / len(sv)
        gg = 1.0 - bisect.bisect_left(sv, x) / len(sv)
        return min(1.0, 2 * min(lo, gg))

    def minp(row, bat):
        return min(two(k, row[k]) for k in bat)

    nullmin = {}
    for bat, tag in ((BAT, "2-30"), (BAT48, "2-48")):
        v = []
        for i in range(half, nrep):
            v.append(min(two(k, cols[k][i]) for k in bat))
        v.sort()
        nullmin[tag] = v

    def omni(mp, tag):
        v = nullmin[tag]
        return bisect.bisect_right(v, mp) / len(v)

    print("\n--- (ii) POWER of the omnibus at n = 97 ----------------------------")
    print("  8,000 simulated 97-letter ciphertexts per system (plaintext = real")
    print("  English).  'power' = fraction whose OMNIBUS p falls below 0.05.")
    systems = [("english", 0), ("transp", 0), ("vig", 1), ("vig", 2), ("vig", 3),
               ("vig", 5), ("vig", 8), ("vig", 10), ("vig", 15), ("vig", 20),
               ("autokey", 8), ("otp", 0)]
    print(f"\n  {'system':22s} {'median min-p':>12s} {'power(2-30)':>12s} {'power(2-48)':>12s}")
    T = 8000
    per = T // NPROC
    for mode, L in systems:
        args = [(909_000 + 131 * i + 7919 * L + 17 * hash(mode) % 1000, per, mode, L)
                for i in range(NPROC)]
        with Pool(NPROC, initializer=_init) as pl:
            parts = pl.map(_pow_chunk, args, chunksize=1)
        keys = parts[0][0]
        mps30, mps48 = [], []
        for _k, rows in parts:
            for r in rows:
                d = dict(zip(keys, r))
                mps30.append(minp(d, BAT))
                mps48.append(minp(d, BAT48))
        p30 = [omni(m, "2-30") for m in mps30]
        p48 = [omni(m, "2-48") for m in mps48]
        pw30 = sum(1 for x in p30 if x < 0.05) / len(p30)
        pw48 = sum(1 for x in p48 if x < 0.05) / len(p48)
        mps30.sort()
        name = f"{mode} L={L}" if L else mode
        print(f"  {name:22s} {mps30[len(mps30)//2]:12.4f} {pw30:12.3f} {pw48:12.3f}")
    print("\n  K4 itself, for reference:")
    m30 = minp({k: obs[k] for k in BAT}, BAT)
    m48 = minp({k: obs[k] for k in BAT48}, BAT48)
    print(f"  {'K4':22s} {m30:12.4f} {omni(m30,'2-30'):12.4f} {omni(m48,'2-48'):12.4f}")
    print("   (last two columns for K4 are its omnibus p, not a power.)")


if __name__ == "__main__":
    print("=" * 78)
    print("ADVERSARIAL VERIFICATION part 4")
    print("=" * 78)
    modclass()
    power()
