#!/usr/bin/env python3
"""Verification harness for stat_common.py.

Every routine used to produce a number in findings/statistics.md is checked
here against either (i) a closed form, (ii) brute-force enumeration on a small
case, or (iii) an independent Monte-Carlo estimate.  Run before trusting any
negative.

    python3 analysis/stat_validate.py
"""
import itertools
import math
import random
from collections import Counter

import stat_common as S

FAIL = []


def check(name, cond, detail=""):
    tag = "ok  " if cond else "FAIL"
    if not cond:
        FAIL.append(name)
    print(f"[{tag}] {name}" + (f"   {detail}" if detail else ""))


def main():
    print("=" * 78)
    print("stat_validate.py -- verification of the statistical machinery")
    print("=" * 78)

    # ---------------------------------------------------------------- data
    print("\n-- 1. data integrity ----------------------------------------------")
    check("K4 is 97 letters", len(S.K4) == 97, S.K4[:12] + "...")
    check("panel splits to 63/369/336/97",
          (len(S.K1_CT), len(S.K2_CT), len(S.K3_CT), len(S.K4_CT)) == (63, 369, 336, 97))
    check("K1 ct begins EMUFPHZLRF", S.K1_CT.startswith("EMUFPHZLRF"), S.K1_CT[:10])
    check("K4 ct begins OBKRUOXOGH", S.K4_CT.startswith("OBKRUOXOGH"))
    check("K3 ct is an anagram of K3 pt", Counter(S.K3_CT) == Counter(S.K3_PT))
    check("to_ints/to_str round trip", S.to_str(S.to_ints(S.K4)) == S.K4)

    # ------------------------------------------------------- known K4 stats
    print("\n-- 2. published K4 statistics reproduced --------------------------")
    v = S.ioc(S.K4)
    check("K4 IoC == 0.03608", abs(v - 0.03608) < 5e-6, f"{v:.6f}")
    check("K4 has all 26 letters", S.n_distinct(S.K4) == 26)
    check("K4 has 6 doubled letters", S.n_doubles(S.K4) == 6)
    dpos = [i + 1 for i in range(96) if S.K4[i] == S.K4[i + 1]]
    check("doubles at 19,26,33,43,47,68", dpos == [19, 26, 33, 43, 47, 68], str(dpos))
    c7 = S.coincidences(S.K4, 7)
    z7 = S.autocorr_z(S.K4, 7)
    check("lag-7 coincidences == 9", c7 == 9, f"{c7}")
    check("lag-7 z == +3.04", abs(z7 - 3.036) < 0.01, f"{z7:+.3f}")
    bi = S.ngram_repeats(S.K4, 2)
    tri = S.ngram_repeats(S.K4, 3)
    nbi = sum(len(p) - 1 for p in bi.values())
    check("10 repeated bigram occurrences (Bean)", nbi == 10, f"{nbi} extra occurrences, {len(bi)} distinct")
    check("0 repeated trigrams", len(tri) == 0)

    # ----------------------------------------------------- exact IoC moments
    print("\n-- 3. exact IoC null moments vs Monte-Carlo ------------------------")
    for n in (30, 97, 369):
        mu, sd = S.ioc_null_moments(n)
        pool = S.LetterPool(1234 + n)
        vals = [S.ioc(pool.take(n)) for _ in range(200_000)]
        m, s = S.mean_sd(vals)
        check(f"n={n} mean matches (exact {mu:.6f}, mc {m:.6f})", abs(mu - m) < 4 * s / math.sqrt(200_000),
              f"|d|={abs(mu-m):.2e}")
        check(f"n={n} sd matches (exact {sd:.6f}, mc {s:.6f})", abs(sd - s) / sd < 0.02,
              f"rel {abs(sd-s)/sd:.4f}")

    # ------------------------------------------- exact IoC lower-tail DP
    print("\n-- 4. exact IoC lattice DP vs brute-force enumeration -------------")
    # brute force: n=8 letters over c=4 symbols, all 4^8 = 65536 strings
    n_bf, c_bf = 8, 4
    brute = Counter()
    for t in itertools.product(range(c_bf), repeat=n_bf):
        cc = Counter(t)
        brute[sum(v * (v - 1) for v in cc.values())] += 1
    tot = c_bf ** n_bf
    dp = S.exact_ioc_cdf(n_bf, s_cap=n_bf * (n_bf - 1), c=c_bf)
    ok = all(abs(dp.get(s, 0.0) - cnt / tot) < 1e-12 for s, cnt in brute.items())
    check("DP == exhaustive enumeration (n=8, c=4)", ok,
          f"{len(brute)} lattice points, sum dp = {sum(dp.values()):.12f}")
    # a second, asymmetric case
    n_bf, c_bf = 7, 3
    brute = Counter()
    for t in itertools.product(range(c_bf), repeat=n_bf):
        cc = Counter(t)
        brute[sum(v * (v - 1) for v in cc.values())] += 1
    tot = c_bf ** n_bf
    dp = S.exact_ioc_cdf(n_bf, s_cap=n_bf * (n_bf - 1), c=c_bf)
    ok = all(abs(dp.get(s, 0.0) - cnt / tot) < 1e-12 for s, cnt in brute.items())
    check("DP == exhaustive enumeration (n=7, c=3)", ok, f"sum dp = {sum(dp.values()):.12f}")
    # truncation behaves: capping must give the same lower-tail masses
    dp_full = S.exact_ioc_cdf(10, s_cap=90, c=5)
    dp_cap = S.exact_ioc_cdf(10, s_cap=12, c=5)
    ok = all(abs(dp_full[s] - dp_cap[s]) < 1e-14 for s in dp_cap)
    check("truncated DP agrees with untruncated on the retained tail", ok)

    # --------------------------------------------------- coupon collector
    print("\n-- 5. coupon-collector exact vs Monte-Carlo ------------------------")
    for n in (60, 97, 200):
        p = S.coupon_all_present(n)
        pool = S.LetterPool(999 + n)
        hits = sum(1 for _ in range(200_000) if S.n_distinct(pool.take(n)) == 26)
        mc = hits / 200_000
        se = math.sqrt(mc * (1 - mc) / 200_000)
        check(f"n={n}: exact {p:.5f} vs mc {mc:.5f}", abs(p - mc) < 4 * se + 1e-9,
              f"se={se:.5f}")

    # ------------------------------------------------- doubles are binomial
    print("\n-- 6. adjacent-doubles are exactly Binomial(n-1, 1/26) -------------")
    pool = S.LetterPool(4242)
    cnt = Counter(S.n_doubles(pool.take(97)) for _ in range(400_000))
    worst = 0.0
    for k in range(0, 13):
        exact = S.binom_pmf(k, 96, 1 / 26)
        mc = cnt.get(k, 0) / 400_000
        worst = max(worst, abs(exact - mc))
    check("pmf matches to <0.002 everywhere", worst < 0.002, f"max |exact-mc| = {worst:.5f}")
    check("binom_cdf + binom_sf consistent",
          abs(S.binom_cdf(5, 96, 1 / 26) + S.binom_sf(6, 96, 1 / 26) - 1.0) < 1e-12)

    # ----------------------------------------------------- autocorr z null
    print("\n-- 7. autocorrelation z null is standard normal-ish ----------------")
    pool = S.LetterPool(31337)
    zs = [S.autocorr_z(pool.take(97), 7) for _ in range(200_000)]
    m, s = S.mean_sd(zs)
    check("mean ~ 0", abs(m) < 0.02, f"{m:+.4f}")
    check("sd ~ 1", abs(s - 1) < 0.03, f"{s:.4f}")

    # ----------------------------------------------------------- ciphers
    print("\n-- 8. cipher routines round-trip -----------------------------------")
    rng = random.Random(7)
    pt = bytes(rng.randrange(26) for _ in range(97))
    key = bytes(rng.randrange(26) for _ in range(9))
    ct = S.vigenere(pt, key)
    back = bytes((ct[i] - key[i % 9]) % 26 for i in range(97))
    check("vigenere round trip", back == pt)
    ct = S.beaufort(pt, key)
    back = bytes((key[i % 9] - ct[i]) % 26 for i in range(97))
    check("beaufort round trip (involutive)", back == pt)
    ct = S.autokey_pt(pt, key[:4])
    ks = key[:4] + pt
    back = bytes((ct[i] - ks[i]) % 26 for i in range(97))
    check("plaintext-autokey round trip", back == pt)
    prim = [3, 1, 4, 1, 5]
    ct = S.gromark(pt, prim)
    n = len(prim)
    kk = list(prim)
    while len(kk) < 97:
        kk.append((kk[-n] + kk[-n + 1]) % 10)
    back = bytes((ct[i] - kk[i]) % 26 for i in range(97))
    check("gromark round trip", back == pt)
    check("gromark keystream is the lagged-Fibonacci one",
          kk[5] == (prim[0] + prim[1]) % 10 and kk[6] == (prim[1] + prim[2]) % 10)
    perm = list(range(97)); rng.shuffle(perm)
    tp = S.transpose(pt, perm)
    check("transposition preserves the letter multiset", Counter(tp) == Counter(pt))
    alphs = [list(range(26)) for _ in range(5)]
    for a in alphs:
        rng.shuffle(a)
    ct = S.random_polyalpha(pt, alphs)
    check("random_polyalpha is invertible per slot",
          all(alphs[i % 5][pt[i]] == ct[i] for i in range(97)))

    # ---------------------------------------------- Vigenere sanity on K1
    print("\n-- 9. Vigenere machinery reproduces a known Kryptos fact -----------")
    # K1 is Quagmire III on the KRYPTOS alphabet with key PALIMPSEST; encoding
    # plaintext and key through that alphabet must give the carved ciphertext.
    ka = S.KRYPTOS_ALPHA
    idx = {ch: i for i, ch in enumerate(ka)}
    pt1 = bytes(idx[c] for c in S.K1_PT)
    key1 = bytes(idx[c] for c in "PALIMPSEST")
    ct1 = S.vigenere(pt1, key1)
    got = "".join(ka[x] for x in ct1)
    check("Quagmire-III re-encryption of K1 == carved K1", got == S.K1_CT,
          f"{got[:20]} vs {S.K1_CT[:20]}")

    # ------------------------------------------------------- letter pool
    print("\n-- 10. LetterPool is uniform ---------------------------------------")
    pool = S.LetterPool(2026)
    big = pool.take(520_000)
    c = Counter(big)
    check("26 symbols only", set(c) == set(range(26)))
    exp = 520_000 / 26
    chi = sum((c[i] - exp) ** 2 / exp for i in range(26))
    check("chi-square vs uniform < 52 (df 25)", chi < 52, f"chi2 = {chi:.1f}")

    # --------------------------------------------------- English corpus
    print("\n-- 11. English corpus ----------------------------------------------")
    corp = S.english_corpus()
    check("corpus >= 1e6 letters", len(corp) >= 1_000_000, f"{len(corp):,} letters")
    ci = S.ioc(corp[:2_000_000])
    check("corpus IoC is English (0.060-0.072)", 0.060 < ci < 0.072, f"{ci:.5f}")
    w = list(S.english_windows(3, 97, seed=5))
    check("english_windows yields 97-letter windows", all(len(x) == 97 for x in w))

    print("\n" + "=" * 78)
    if FAIL:
        print(f"FAILURES: {len(FAIL)} -> {FAIL}")
    else:
        print("ALL CHECKS PASSED")
    print("=" * 78)


if __name__ == "__main__":
    main()
