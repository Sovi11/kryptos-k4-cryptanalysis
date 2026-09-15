#!/usr/bin/env python3
"""(b) "All 26 letters appear in 97 characters" -- is that evidence of anything?

Computed here:
  1. Exact P(all 26 present) in n i.i.d. uniform letters, by inclusion-exclusion,
     for n = 97 and for the K1/K2/K3 lengths.
  2. The exact distribution of the number of DISTINCT letters in 97 uniform
     draws (also exact, by inclusion-exclusion on the surjection count), so the
     observed 26 can be placed in a percentile.
  3. P(all 26 present) under Vigenere-over-English at key lengths 1..30 and
     under a one-time pad -- i.e. what each candidate cipher predicts.
  4. The likelihood ratio between hypotheses, which is the only honest way to
     ask whether "all 26 present" is evidence.

    python3 analysis/stat_b_coverage.py
"""
import math
import os
from collections import Counter
from multiprocessing import Pool

import stat_common as S

TRIALS = 200_000
SEED = 20260913
NPROC = min(8, os.cpu_count() or 4)

_CORP = None


def _init_worker():
    global _CORP
    _CORP = S.english_corpus()


def _chunk(args):
    tag, seed, L, trials, mode = args
    import random
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
        hist[len(set(ct))] += 1
    return tag, hist


def exact_distinct_distribution(n, c=26):
    """Exact P(exactly k distinct symbols) for n i.i.d. uniform draws over c.

    P(k) = C(c,k) * Surj(n,k) / c^n, with Surj(n,k) the number of surjections
    from an n-set onto a k-set = sum_j (-1)^j C(k,j) (k-j)^n.
    """
    out = {}
    for k in range(1, c + 1):
        surj = sum((-1) ** j * math.comb(k, j) * (k - j) ** n for j in range(k + 1))
        out[k] = math.comb(c, k) * surj / c ** n
    return out


def main():
    print("=" * 78)
    print("(b) LETTER COVERAGE -- 'all 26 appear in 97 characters'")
    print("=" * 78)

    print("\n--- 1. Exact, under a uniform-random source -------------------------")
    for n, label in [(63, "K1 length"), (97, "K4 length"), (336, "K3 length"),
                     (369, "K2 length")]:
        p = S.coupon_all_present(n)
        print(f"  n = {n:3d} ({label:9s}):  P(all 26 present) = {p:.6f}")
    print("\n  For K4's 97 letters this is 0.542 -- MORE LIKELY THAN NOT.")
    print("  'All 26 letters appear' is the majority outcome, not an anomaly.")

    print("\n--- 2. Exact distribution of the distinct-letter count at n = 97 ----")
    dist = exact_distinct_distribution(97)
    tot = sum(dist.values())
    assert abs(tot - 1) < 1e-9, tot
    mean = sum(k * v for k, v in dist.items())
    var = sum((k - mean) ** 2 * v for k, v in dist.items())
    print(f"  mean distinct = {mean:.4f}   sd = {math.sqrt(var):.4f}")
    print(f"\n  {'k':>4s} {'P(exactly k)':>14s} {'P(<= k)':>12s}")
    cum = 0.0
    for k in range(19, 27):
        cum_prev = cum
        cum += dist[k]
        print(f"  {k:4d} {dist[k]:14.6f} {cum:12.6f}")
    print(f"\n  K4 has 26 distinct.  P(distinct >= 26) = P(= 26) = {dist[26]:.6f}")
    print(f"  z of 26 against the null = {(26 - mean)/math.sqrt(var):+.3f}")
    print("  => a +0.7 sigma outcome.  Carries essentially no information.")

    print("\n--- 3. What each candidate cipher predicts --------------------------")
    print(f"{TRIALS:,} simulated 97-letter outputs per row "
          f"(plaintext = random window of real English).")
    specs = [("uniform", 0, "uniform"), ("English (plaintext)", 0, "english"),
             ("OTP over English", 97, "otp")]
    specs += [(f"Vigenere L={L}", L, "vig") for L in list(range(1, 31)) + [40, 50]]
    args = []
    per = TRIALS // NPROC
    for tag, L, mode in specs:
        h = sum(ord(c) * (i + 1) for i, c in enumerate(tag))
        for i in range(NPROC):
            args.append((tag, SEED + 7919 * i + 131 * h, L, per, mode))
    with Pool(NPROC, initializer=_init_worker) as pool:
        parts = pool.map(_chunk, args, chunksize=1)
    agg = {}
    for tag, h in parts:
        agg.setdefault(tag, Counter()).update(h)

    print(f"\n{'source':22s} {'mean distinct':>14s} {'P(all 26)':>11s} "
          f"{'P(>=26)':>9s} {'compatible with K4?':>21s}")
    for tag, L, mode in specs:
        h = agg[tag]
        n_t = sum(h.values())
        m = sum(k * v for k, v in h.items()) / n_t
        p26 = h.get(26, 0) / n_t
        verdict = "yes" if p26 > 0.01 else ("marginal" if p26 > 1e-4 else "NO -- excluded")
        print(f"{tag:22s} {m:14.3f} {p26:11.5f} {p26:9.5f} {verdict:>21s}")

    print("\n--- 4. Likelihood ratios: what does 'all 26 present' buy you? -------")
    p_unif = S.coupon_all_present(97)
    print(f"  P(all 26 | uniform-random / OTP / long key) = {p_unif:.4f}")
    for tag in ("English (plaintext)", "Vigenere L=1", "Vigenere L=2", "Vigenere L=3",
                "Vigenere L=5", "Vigenere L=8", "Vigenere L=12"):
        h = agg[tag]
        n_t = sum(h.values())
        p = h.get(26, 0) / n_t
        lr = (p_unif / p) if p > 0 else float("inf")
        ps = f"{p:.5f}" if p > 0 else f"<{1/n_t:.1e}"
        print(f"  P(all 26 | {tag:20s}) = {ps:>10s}   LR vs uniform = "
              f"{('%.1f' % lr) if lr != float('inf') else '>1e4':>7s}")
    print("\n  Reading: the observation 'K4 contains all 26 letters' is ~2x more likely")
    print("  under a flat source than under a short-key Vigenere, and ~18x more likely")
    print("  than under raw English.  Two-to-eighteen-fold likelihood ratios on a single")
    print("  binary observation are weak evidence (a Bayes factor of 2 moves a 50% prior")
    print("  to 67%).  The honest statement: coverage tells you K4 is not raw English and")
    print("  not a one-alphabet cipher, which the IoC already told you far more loudly,")
    print("  and it tells you nothing else.")

    print("\n--- 5. Which letters are rare in K4 ---------------------------------")
    c = Counter(S.K4)
    ones = sorted(ch for ch in S.A2Z if c[ch] == 1)
    print(f"  letters appearing exactly once: {' '.join(ones)} ({len(ones)} of 26)")
    exp_ones = 26 * 97 * (1 / 26) * (25 / 26) ** 96
    print(f"  expected number of singletons under uniform random = {exp_ones:.2f}")
    top = sorted(c.items(), key=lambda kv: -kv[1])[:6]
    print(f"  most frequent: {', '.join(f'{k}x{v}' for k, v in top)}")
    print(f"  chi-square vs uniform (df 25) = {S.chi2_vs(S.K4):.1f}  "
          f"[95th pct 37.7, 99th 44.3]")
    print(f"  chi-square vs English (df 25) = {S.chi2_vs(S.K4, S.ENGLISH_FREQ):.1f}")
    print("  => K4's letter distribution is statistically indistinguishable from flat,")
    print("     and decisively NOT English.")


if __name__ == "__main__":
    main()
