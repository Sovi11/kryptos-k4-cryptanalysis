#!/usr/bin/env python3
"""(a) The index of coincidence: exact null distribution and calibration.

Question this settles: K4's IoC is 0.03608, below the 0.03846 expected of a
uniform-random 97-letter string.  Is that anomalously flat, or small-sample
noise?  Asserted both ways in the literature; nobody computed the null.

What is computed here:
  1. The EXACT null distribution of the IoC lattice statistic S = sum n(n-1)
     for n i.i.d. uniform letters (dynamic programming, verified against
     exhaustive enumeration in stat_validate.py).  Gives an exact p-value, not
     a Monte-Carlo estimate.
  2. A 10^7-draw Monte-Carlo cross-check.
  3. The same treatment for K1 (63), K2 (369), K3 (336) ciphertexts, and for
     the K1/K2/K3 plaintexts as English controls.
  4. Simulated Vigenere-over-English at key lengths 1..30 (plus 40/50/97):
     the null IoC distribution of each, and P(IoC <= K4's) under each.
     This is the number that says which key lengths the IoC alone excludes.

    python3 analysis/stat_a_ioc.py
"""
import math
import os
import sys
from multiprocessing import Pool

import stat_common as S

TRIALS_MC = 10_000_000
TRIALS_VIG = 200_000
SEED = 20260913
NPROC = min(8, os.cpu_count() or 4)


# ------------------------------------------------------------------ workers --
def _mc_ioc_chunk(args):
    seed, n, trials = args
    pool = S.LetterPool(seed)
    from collections import Counter
    hist = Counter()
    for _ in range(trials):
        b = pool.take(n)
        c = Counter(b)
        hist[sum(v * (v - 1) for v in c.values())] += 1
    return hist


def mc_ioc_hist(n, trials, seed):
    per = trials // NPROC
    args = [(seed + 1000 * i, n, per) for i in range(NPROC)]
    with Pool(NPROC) as p:
        parts = p.map(_mc_ioc_chunk, args)
    from collections import Counter
    tot = Counter()
    for h in parts:
        tot.update(h)
    return tot, per * NPROC


_CORP = None


def _init_worker():
    global _CORP
    _CORP = S.english_corpus()


def _vig_chunk(args):
    tag, seed, L, trials, mode = args
    import random
    from collections import Counter
    corpus = _CORP
    rng = random.Random(seed)
    hi = len(corpus) - 98
    out = []
    for _ in range(trials):
        i = rng.randrange(hi)
        pt = corpus[i:i + 97]
        if mode == "otp":
            key = bytes(rng.randrange(26) for _ in range(97))
            ct = bytes((pt[j] + key[j]) % 26 for j in range(97))
        else:
            key = bytes(rng.randrange(26) for _ in range(L))
            ct = bytes((pt[j] + key[j % L]) % 26 for j in range(97))
        c = Counter(ct)
        out.append(sum(v * (v - 1) for v in c.values()))
    return tag, out


def vig_sim_all(specs, trials, seed, pool):
    """specs: list of (tag, keylen, mode).  Returns {tag: sorted S values}."""
    per = trials // NPROC
    args = []
    for tag, L, mode in specs:
        h = sum(ord(c) * (k + 1) for k, c in enumerate(str(tag)))   # stable, unlike hash()
        for i in range(NPROC):
            args.append((tag, seed + 7919 * i + 131 * h, L, per, mode))
    res = {}
    for tag, vals in pool.map(_vig_chunk, args, chunksize=1):
        res.setdefault(tag, []).extend(vals)
    for tag in res:
        res[tag].sort()
    return res


# ------------------------------------------------------------------ report --
def exact_tail_table(n, obs_S, cap_extra=350):
    """Exact P(S <= obs) and the exact null quantiles, for n uniform letters."""
    cap = obs_S + cap_extra
    dist = S.exact_ioc_cdf(n, s_cap=cap, c=26)
    mass = sum(dist.values())
    cum = 0.0
    p_le = 0.0
    quant = {}
    targets = [0.001, 0.01, 0.025, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.975, 0.99]
    ti = 0
    for s in sorted(dist):
        cum += dist[s]
        if s <= obs_S:
            p_le = cum
        while ti < len(targets) and cum >= targets[ti]:
            quant[targets[ti]] = s
            ti += 1
    return dist, mass, p_le, quant


def main():
    print("=" * 78)
    print("(a) INDEX OF COINCIDENCE -- exact null distributions")
    print("=" * 78)
    denom = 97 * 96
    obs = S.ioc(S.K4)
    obsS = S.ioc_S(S.K4)
    mu, sd = S.ioc_null_moments(97)
    print(f"\nK4: n = 97, IoC = {obs:.6f}  (lattice S = {obsS} of {denom})")
    print(f"uniform-random null, exact moments: mean = {mu:.6f}  sd = {sd:.6f}")
    print(f"  => z = {(obs - mu) / sd:+.4f}")
    print("  (Var(IoC) = 2p(1-p)/(n(n-1)) with p = 1/26; derivation in stat_common)")

    print("\n--- 1. EXACT null distribution of S for n = 97 ---------------------")
    dist, mass, p_le, quant = exact_tail_table(97, obsS)
    print(f"support starts at S = {min(dist)} "
          f"(the most even possible split of 97 over 26 letters, IoC = {min(dist)/denom:.6f})")
    print(f"mass captured by the truncated DP: {mass:.10f}")
    print(f"\n  EXACT P(IoC <= 0.036082 | uniform random 97 letters) = {p_le:.6f}")
    print(f"  EXACT P(IoC >= 0.036082)                             = {1 - p_le + dist.get(obsS,0):.6f}")
    print("\nexact null quantiles of the IoC:")
    for q, s in sorted(quant.items()):
        print(f"   {q*100:6.1f}th pct : S = {s:4d}   IoC = {s/denom:.6f}")
    print(f"\n  K4 sits at the {p_le*100:.2f}th percentile of the uniform-random null.")
    print("  A two-sided 95% interval for a random 97-letter string is "
          f"IoC in [{quant[0.025]/denom:.5f}, {quant[0.975]/denom:.5f}].")
    print("  K4's 0.03608 is inside it, nowhere near either edge.")

    print("\n--- 2. Monte-Carlo cross-check, 10^7 draws -------------------------")
    hist, ntot = mc_ioc_hist(97, TRIALS_MC, SEED)
    le = sum(c for s, c in hist.items() if s <= obsS)
    p_mc = le / ntot
    m = sum(s * c for s, c in hist.items()) / ntot / denom
    v = sum(((s / denom) - m) ** 2 * c for s, c in hist.items()) / ntot
    print(f"draws = {ntot:,}")
    print(f"  MC mean IoC = {m:.6f} (exact {mu:.6f})")
    print(f"  MC sd  IoC  = {math.sqrt(v):.6f} (exact {sd:.6f})")
    print(f"  MC P(IoC <= K4) = {p_mc:.6f}   vs EXACT {p_le:.6f}   "
          f"(diff {abs(p_mc - p_le):.6f}, MC se {math.sqrt(p_le*(1-p_le)/ntot):.6f})")

    print("\n--- 3. Controls: K1, K2, K3 and the plaintexts ---------------------")
    print("P(<=) is EXACT (lattice DP) for n <= 120 and a 2,000,000-draw Monte-Carlo")
    print("estimate otherwise; '<1e-06' means 0 of 2,000,000 draws were that low.")
    print(f"\n{'text':28s} {'n':>5s} {'IoC':>9s} {'null mean':>10s} {'null sd':>9s} "
          f"{'z':>8s} {'P(IoC<=obs)':>13s} {'P(IoC>=obs)':>13s}")
    rows = [("K1 ciphertext", S.K1_CT), ("K2 ciphertext", S.K2_CT),
            ("K3 ciphertext", S.K3_CT), ("K4 ciphertext", S.K4_CT),
            ("K1 plaintext (English)", S.K1_PT), ("K2 plaintext (English)", S.K2_PT),
            ("K3 plaintext (English)", S.K3_PT)]
    for name, t in rows:
        n = len(t)
        o = S.ioc(t)
        oS = S.ioc_S(t)
        m0, s0 = S.ioc_null_moments(n)
        z = (o - m0) / s0
        if n <= 120:
            d2, mass2, ple2, _ = exact_tail_table(n, oS, cap_extra=80)
            pge = 1 - ple2 + d2.get(oS, 0.0)
            lo, hi = f"{ple2:13.6f}", f"{pge:13.6f}"
        else:
            hist2, nt2 = mc_ioc_hist(n, 2_000_000, SEED + 77 * n)
            le = sum(c for s_, c in hist2.items() if s_ <= oS) / nt2
            ge = sum(c for s_, c in hist2.items() if s_ >= oS) / nt2
            lo = f"{le:13.6f}" if le > 0 else f"{'<5e-07':>13s}"
            hi = f"{ge:13.6f}" if ge > 0 else f"{'<5e-07':>13s}"
        print(f"{name:28s} {n:5d} {o:9.5f} {m0:10.5f} {s0:9.5f} {z:+8.2f} {lo} {hi}")
    print("\n  K3's ciphertext is a pure transposition, so its IoC is its PLAINTEXT's:")
    print(f"  K3 ct IoC {S.ioc(S.K3_CT):.5f} == K3 pt IoC {S.ioc(S.K3_PT):.5f} -> "
          f"{'identical' if abs(S.ioc(S.K3_CT)-S.ioc(S.K3_PT))<1e-12 else 'DIFFER'}")
    print("  That is the single most useful control in this whole table: it is what")
    print("  K4 would look like if K4 were a transposition, and it is 8.9 sd away from")
    print("  what K4 actually is.")

    print("\n--- 4. Vigenere over English, key lengths 1..30 --------------------")
    print("200,000 simulated encipherments per key length: random 97-letter window of")
    print("real English prose (22.4M-letter corpus, IoC 0.0660), random key.")
    specs = [(str(L), L, "vig") for L in list(range(1, 31)) + [40, 50]]
    specs.append(("OTP", 97, "otp"))
    with Pool(NPROC, initializer=_init_worker) as pool:
        res = vig_sim_all(specs, TRIALS_VIG, SEED, pool)

    print(f"\n{'keylen':>6s} {'mean IoC':>9s} {'sd':>8s} {'2.5%':>8s} {'97.5%':>8s} "
          f"{'P(IoC<=K4)':>11s} {'verdict':>22s}")
    vig_rows = []
    for tag, L, mode in specs:
        vals = res[tag]
        n_t = len(vals)
        iocs = sorted(v / denom for v in vals)
        m1, s1 = S.mean_sd(iocs)
        p = S.percentile_of(iocs, obs)
        lo, hi = iocs[int(0.025 * n_t)], iocs[int(0.975 * n_t)]
        if p < 1e-5:
            verdict = "EXCLUDED by IoC"
        elif p < 0.01:
            verdict = "strongly disfavoured"
        elif p < 0.05:
            verdict = "disfavoured"
        else:
            verdict = "compatible"
        if mode == "vig":
            vig_rows.append((L, m1, s1, lo, hi, p, verdict))
        pstr = f"{p:11.5f}" if p > 0 else f"{'<5e-06':>11s}"
        print(f"{tag:>6s} {m1:9.5f} {s1:8.5f} {lo:8.5f} {hi:8.5f} {pstr} {verdict:>22s}")

    excl = [r[0] for r in vig_rows if r[5] < 1e-5]
    dis = [r[0] for r in vig_rows if 1e-5 <= r[5] < 0.05]
    comp = [r[0] for r in vig_rows if r[5] >= 0.05]
    print(f"\n  key lengths EXCLUDED by the IoC alone (P < 1e-5): {excl}")
    print(f"  key lengths disfavoured (1e-5 <= P < 0.05):      {dis}")
    print(f"  key lengths compatible with K4's IoC:            {comp}")

    print("\n--- 5. What IoC = 0.03608 actually licenses ------------------------")
    print("* Against the uniform-random null the observed value is at the "
          f"{p_le*100:.1f}th percentile.")
    print("  It is NOT 'anomalously flat'. It is an ordinary draw.")
    print("* The claim 'below uniform random, therefore the masking is visible' is")
    print("  unsupported: 21.6% of random 97-letter strings are at least this low, and")
    print("  the gap (0.00238) is 0.84 null standard deviations.")
    print("* What the IoC DOES exclude, at overwhelming significance, is any system")
    print("  that leaves an English-sized IoC: pure transposition (K3's own ciphertext")
    print(f"  sits at IoC {S.ioc(S.K3_CT):.4f}) and short-period polyalphabetics.")


if __name__ == "__main__":
    sys.exit(main())
