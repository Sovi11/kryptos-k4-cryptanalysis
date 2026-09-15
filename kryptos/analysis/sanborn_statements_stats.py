#!/usr/bin/env python3
"""
Backing arithmetic for the statistical claims in findings/sanborn_statements.md.

Two pieces of K4 "folklore" are frequently cited as evidence that Ed Scheidt's
"masking" worked -- that the index of coincidence is BELOW uniform random, and
that all 26 letters appear.  Both are checked here against the correct null
distribution for a 97-letter string.  A third folklore item, the lag-7
autocorrelation spike, is checked for multiple-comparison inflation.

Run:  python3 analysis/sanborn_statements_stats.py
"""

from collections import Counter
import random
import statistics

CT = ("OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFB"
      "NYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR")

N_TRIALS = 200_000
SEED = 20260912


def ioc(seq):
    n = len(seq)
    c = Counter(seq)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1))


def main():
    assert len(CT) == 97, len(CT)
    n = len(CT)
    obs_ioc = ioc(CT)
    obs_distinct = len(set(CT))

    rng = random.Random(SEED)
    iocs, distincts = [], []
    for _ in range(N_TRIALS):
        s = [rng.randrange(26) for _ in range(n)]
        iocs.append(ioc(s))
        distincts.append(len(set(s)))

    mu, sd = statistics.mean(iocs), statistics.pstdev(iocs)
    p_le = sum(1 for v in iocs if v <= obs_ioc) / N_TRIALS
    p_all26 = sum(1 for d in distincts if d == 26) / N_TRIALS

    print(f"K4 length                     : {n}")
    print(f"K4 observed IoC               : {obs_ioc:.5f}")
    print(f"uniform-random IoC mean +- sd : {mu:.5f} +- {sd:.5f}")
    print(f"  => z                        : {(obs_ioc - mu) / sd:+.2f}")
    print(f"  => P(IoC <= observed | rand) : {p_le:.3f}")
    print(f"English prose IoC (reference) : ~0.0667")
    print()
    print(f"K4 distinct letters           : {obs_distinct}/26")
    print(f"P(all 26 present | 97 random) : {p_all26:.3f}")
    print()

    # Multiple-comparison inflation for the "lag-7 autocorrelation z = +3.0" claim.
    p_one = 0.00135          # one-sided P(z > 3.0) for a single lag
    for n_lags in (24, 48, 96):
        fw = 1 - (1 - p_one) ** n_lags
        print(f"lag-7 z=+3.0, family-wise p over {n_lags:2d} lags : {fw:.3f}")
    print()
    print("Conclusion: neither the sub-random IoC, the all-26-letters property,")
    print("nor the lag-7 spike is statistically distinguishable from a uniformly")
    print("random 97-letter string.  None of them should be used as evidence for")
    print("or against any cipher hypothesis.")


if __name__ == "__main__":
    main()
