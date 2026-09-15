"""Non-periodic / one-time-pad-like view of the K4 cribs.

The 24 crib positions fix the key value at those positions for any additive cipher.
This script reports how those 24 required shifts are distributed (Vigenere and Beaufort,
straight and KRYPTOS-keyed alphabets): distinct values, repeats, chi-square against uniform,
runs, and whether the key letters read as English (running-key hypothesis).
Also gives whole-ciphertext statistics (IoC, chi-square) for context.
"""
import json
import math
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from k4_common import (A2Z, KRYPTOS_ALPHA, CT, CRIB_POS, CRIB_CT, CRIB_PT, ROOT, ENG_FREQ,
                       bigram_score, chi2_english, ioc)

RES = {}


def shifts(alpha, mode):
    inv = {ch: i for i, ch in enumerate(alpha)}
    out = []
    for c, p in zip(CRIB_CT, CRIB_PT):
        ci, pi = inv[c], inv[p]
        out.append((ci - pi) % 26 if mode == "vig" else (ci + pi) % 26)
    return out


def chi2_uniform(vals, k=26):
    n = len(vals)
    cnt = Counter(vals)
    return sum((cnt[v] - n / k) ** 2 / (n / k) for v in range(k))


def expected_distinct(n=24, k=26):
    return k * (1 - (1 - 1 / k) ** n)


print(f"whole ciphertext: IoC = {ioc(CT):.4f} (English ~0.066, uniform random 0.0385); chi-square vs English monograms = {chi2_english(CT):.1f} (df 25)")
print(f"expected number of distinct values among 24 uniform draws from 26: {expected_distinct():.1f}\n")
for aname, alpha in (("straight", A2Z), ("kryptos", KRYPTOS_ALPHA)):
    for mode in ("vig", "beau"):
        s = shifts(alpha, mode)
        key_letters = "".join(alpha[v] for v in s)
        block1, block2 = key_letters[:13], key_letters[13:]
        cnt = Counter(s)
        rep = {alpha[v]: c for v, c in cnt.items() if c > 1}
        chi_u = chi2_uniform(s)
        # chi-square df=25: mean 25, sd ~7.07; p>0.05 if chi2 < 37.7
        # runs: adjacent equal shifts inside each crib block
        adj_eq = sum(1 for k in range(23) if CRIB_POS[k + 1] == CRIB_POS[k] + 1 and s[k] == s[k + 1])
        diffs = [(s[k + 1] - s[k]) % 26 for k in range(23) if CRIB_POS[k + 1] == CRIB_POS[k] + 1]
        print(f"[{aname:8s} {mode:4s}] required shifts: {s}")
        print(f"    as key letters ({aname} alphabet): {block1} | {block2}")
        print(f"    distinct values {len(cnt)}/24 (uniform expectation {expected_distinct():.1f}); repeated: {rep}")
        print(f"    chi-square vs uniform = {chi_u:.1f} (df 25; 95th percentile 37.7); adjacent equal shifts: {adj_eq}; "
              f"successive differences: {diffs}")
        print(f"    running-key test: chi-square of key letters vs English = {chi2_english(key_letters):.1f} (df 25), "
              f"bigram score {bigram_score(block1):.2f} / {bigram_score(block2):.2f} (English ~ -5.3, random ~ -7.4)")
        RES[f"{aname}/{mode}"] = {"shifts": s, "key_letters": key_letters, "distinct": len(cnt), "repeats": rep,
                                  "chi2_uniform": chi_u, "chi2_english_keyletters": chi2_english(key_letters),
                                  "bigram_block1": bigram_score(block1), "bigram_block2": bigram_score(block2)}
        print()

print("Interpretation: with 24 samples, chi-square against uniform has df=25; values near 25 are what a uniform")
print("(one-time-pad-like) key stream gives.  A keyword-based key stream would show fewer distinct values and")
print("a skew toward common letters; a running English key would give key letters with English statistics.")
with open(os.path.join(ROOT, "findings", "keystream_results.json"), "w") as f:
    json.dump(RES, f, indent=1)
