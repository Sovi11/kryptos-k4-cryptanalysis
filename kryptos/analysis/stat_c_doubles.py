#!/usr/bin/env python3
"""(c) Doubled letters: six of them in 97 characters.  Expected? Anomalous?

Key exact fact used here: for an i.i.d. uniform source over Z_26 the successive
differences d_i = x_{i+1} - x_i are i.i.d. uniform, so the number of adjacent
equal pairs is EXACTLY Binomial(n-1, 1/26).  No simulation needed for the null,
though one is run as a cross-check.

Also treated: the two positional claims that circulate about K4's doubles --
"five of the six sit at positions == 5 (mod 7)" and "the doubles cluster in the
last two columns of a 7x14 layout" -- with an honest multiple-testing
correction over every modulus and every residue.

    python3 analysis/stat_c_doubles.py
"""
import math
import os
import random
from collections import Counter
from multiprocessing import Pool

import stat_common as S

TRIALS = 200_000
BIG = 1_000_000
SEED = 20260913
NPROC = min(8, os.cpu_count() or 4)

_CORP = None


def _init_worker():
    global _CORP
    _CORP = S.english_corpus()


def _chunk(args):
    tag, seed, L, trials, mode = args
    rng = random.Random(seed)
    corpus = _CORP
    hi = len(corpus) - 98
    hist = Counter()
    for _ in range(trials):
        if mode == "uniform":
            ct = bytes(rng.randrange(26) for _ in range(97))
        elif mode == "english":
            i = rng.randrange(hi)
            ct = corpus[i:i + 97]
        else:
            i = rng.randrange(hi)
            pt = corpus[i:i + 97]
            if mode == "otp":
                ct = bytes((pt[j] + rng.randrange(26)) % 26 for j in range(97))
            else:
                key = bytes(rng.randrange(26) for _ in range(L))
                ct = bytes((pt[j] + key[j % L]) % 26 for j in range(97))
        hist[sum(1 for j in range(96) if ct[j] == ct[j + 1])] += 1
    return tag, hist


def _modulus_chunk(args):
    """Null for 'some modulus m in 2..M collects >= r of the k doubles in one
    residue class' -- k positions placed uniformly at random in 1..96."""
    seed, trials, k, M, r = args
    rng = random.Random(seed)
    hits_any = 0
    best_hist = Counter()
    for _ in range(trials):
        pos = rng.sample(range(1, 97), k)
        best = 0
        for m in range(2, M + 1):
            cc = Counter(p % m for p in pos)
            b = max(cc.values())
            if b > best:
                best = b
        best_hist[best] += 1
        if best >= r:
            hits_any += 1
    return hits_any, best_hist


def main():
    print("=" * 78)
    print("(c) DOUBLED LETTERS")
    print("=" * 78)

    obs = S.n_doubles(S.K4)
    pos = [i + 1 for i in range(96) if S.K4[i] == S.K4[i + 1]]
    pairs = [S.K4[i - 1:i + 1] for i in pos]
    print(f"\nK4: {obs} doubled letters, 1-indexed starts {pos}")
    print(f"    pairs {pairs}")

    print("\n--- 1. Exact null: Binomial(96, 1/26) -------------------------------")
    n, p = 96, 1 / 26
    mean, sd = n * p, math.sqrt(n * p * (1 - p))
    print(f"  mean = {mean:.4f}   sd = {sd:.4f}")
    print(f"  z of 6 = {(obs - mean)/sd:+.3f}")
    print(f"\n  {'k':>3s} {'P(exactly k)':>14s} {'P(>= k)':>12s} {'P(<= k)':>12s}")
    for k in range(0, 11):
        print(f"  {k:3d} {S.binom_pmf(k, n, p):14.6f} {S.binom_sf(k, n, p):12.6f} "
              f"{S.binom_cdf(k, n, p):12.6f}")
    print(f"\n  EXACT P(>= 6 doubles) = {S.binom_sf(6, n, p):.6f}")
    print(f"  EXACT P(<= 6 doubles) = {S.binom_cdf(6, n, p):.6f}")
    print(f"  => 6 sits at the {S.binom_cdf(5, n, p)*100:.1f}-{S.binom_cdf(6, n, p)*100:.1f}"
          "th percentile of the uniform-random null.  Unremarkable.")

    print("\n--- 2. Monte-Carlo cross-check --------------------------------------")
    pool = S.LetterPool(SEED)
    h = Counter(S.n_doubles(pool.take(97)) for _ in range(BIG))
    worst = max(abs(h.get(k, 0) / BIG - S.binom_pmf(k, n, p)) for k in range(13))
    print(f"  {BIG:,} uniform draws; max |MC - exact| over k=0..12 is {worst:.5f}")
    print(f"  MC P(>= 6) = {sum(v for k, v in h.items() if k >= 6)/BIG:.6f} "
          f"vs exact {S.binom_sf(6, n, p):.6f}")

    print("\n--- 3. K1, K2, K3 controls ------------------------------------------")
    print(f"{'text':26s} {'n':>5s} {'doubles':>8s} {'exp':>7s} {'z':>7s} "
          f"{'P(>=obs)':>10s} {'P(<=obs)':>10s}")
    for name, t in [("K1 ciphertext", S.K1_CT), ("K2 ciphertext", S.K2_CT),
                    ("K3 ciphertext", S.K3_CT), ("K4 ciphertext", S.K4_CT),
                    ("K1 plaintext", S.K1_PT), ("K2 plaintext", S.K2_PT),
                    ("K3 plaintext", S.K3_PT)]:
        d = S.n_doubles(t)
        m_ = (len(t) - 1) * p
        s_ = math.sqrt((len(t) - 1) * p * (1 - p))
        print(f"{name:26s} {len(t):5d} {d:8d} {m_:7.2f} {(d-m_)/s_:+7.2f} "
              f"{S.binom_sf(d, len(t)-1, p):10.5f} {S.binom_cdf(d, len(t)-1, p):10.5f}")
    print("\n  Note K3: a transposition scatters English's own doubles, so its count is")
    print("  a good control for 'what an English-derived text looks like'.")

    print("\n--- 4. What each candidate cipher predicts --------------------------")
    specs = [("uniform", 0, "uniform"), ("English (plaintext)", 0, "english"),
             ("OTP over English", 97, "otp")]
    specs += [(f"Vigenere L={L}", L, "vig") for L in (1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 25, 30)]
    args = []
    per = TRIALS // NPROC
    for tag, L, mode in specs:
        hh = sum(ord(ch) * (i + 1) for i, ch in enumerate(tag))
        for i in range(NPROC):
            args.append((tag, SEED + 7919 * i + 131 * hh, L, per, mode))
    with Pool(NPROC, initializer=_init_worker) as pl:
        parts = pl.map(_chunk, args, chunksize=1)
    agg = {}
    for tag, hh in parts:
        agg.setdefault(tag, Counter()).update(hh)
    print(f"\n{'source':22s} {'mean doubles':>13s} {'sd':>6s} {'P(>=6)':>9s} {'P(<=6)':>9s}")
    for tag, L, mode in specs:
        hh = agg[tag]
        n_t = sum(hh.values())
        m_ = sum(k * v for k, v in hh.items()) / n_t
        v_ = sum((k - m_) ** 2 * v for k, v in hh.items()) / n_t
        pge = sum(v for k, v in hh.items() if k >= 6) / n_t
        ple = sum(v for k, v in hh.items() if k <= 6) / n_t
        print(f"{tag:22s} {m_:13.3f} {math.sqrt(v_):6.3f} {pge:9.5f} {ple:9.5f}")
    print("\n  Every candidate except raw English predicts ~3.7 doubles with sd ~1.9.")
    print("  6 is compatible with all of them.  The doubled-letter count discriminates")
    print("  nothing except 'not raw English'.")

    print("\n--- 5. The positional folklore, corrected for multiple testing ------")
    print(f"  Observed positions {pos}.  Residues mod 7: "
          f"{[q % 7 for q in pos]} -- five of six are 5 (mod 7).")
    print(f"  Naive p for that alone: P(>=5 of 6 uniform positions share a residue mod 7)")
    k, M = 6, 48
    # exact-ish naive: 7 * [C(6,5)(1/7)^5(6/7) + (1/7)^6]
    naive = 7 * (math.comb(6, 5) * (1 / 7) ** 5 * (6 / 7) + (1 / 7) ** 6)
    print(f"    = {naive:.5f}   (7 residues x binomial tail)")
    print(f"  But modulus 7 was chosen AFTER seeing a lag-7 autocorrelation bump.")
    print(f"  Correct null: max over moduli 2..{M} of the largest residue class,")
    print(f"  for 6 positions drawn uniformly without replacement from 1..96.")
    per = BIG // NPROC
    args = [(SEED + 31 * i, per, k, M, 5) for i in range(NPROC)]
    with Pool(NPROC) as pl:
        res = pl.map(_modulus_chunk, args)
    hits = sum(r[0] for r in res)
    hist = Counter()
    for r in res:
        hist.update(r[1])
    ntot = per * NPROC
    print(f"    {ntot:,} trials: P(some modulus 2..{M} collects >= 5 of 6) = "
          f"{hits/ntot:.4f}")
    hits6 = sum(v for kk, v in hist.items() if kk >= 6)
    print(f"                  P(some modulus collects all 6)          = {hits6/ntot:.4f}")
    print("  => the mod-7 pattern is NOT significant. It is what you always find when")
    print("     you let yourself pick the modulus after the fact.")

    print("\n  Second claim: 'doubles cluster in the last two columns of a 7x14 grid'.")
    cols = [(q - 1) % 7 for q in pos]
    print(f"    columns (0-indexed, width 7, 1-indexed positions): {cols}")
    print("    -- five in column 4, one in column 0; not the last two columns at all")
    print("    under this indexing. The claim is indexing-dependent, and the corrected")
    print("    p-value above covers every indexing.")

    print("\n  Third: are the doubles unusually early in the text?")
    print(f"    last double starts at {max(pos)}, so the final "
          f"{96 - max(pos)} adjacent pairs contain none.")
    pempty = (max(pos) / 96) ** 6
    print(f"    P(all 6 of 6 uniform positions <= {max(pos)}) = {pempty:.4f}  -- not significant")


if __name__ == "__main__":
    main()
