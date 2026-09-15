#!/usr/bin/env python3
"""ADVERSARIAL VERIFICATION part 3 -- analysis of the independent null sample.

Reproduces every family-wise number in findings/statistics.md from MY sample,
then stress-tests the omnibus against the analyst's discretionary choices and
computes a GLOBAL multiple-testing correction over everything that was scanned.
"""
import bisect
import math
import os
import pickle
import sys
from array import array

HERE = os.path.dirname(os.path.abspath(__file__))


def load(mode):
    with open(os.path.join(HERE, f"adv_null_{mode}.pkl"), "rb") as f:
        d = pickle.load(f)
    cols = {}
    for k, raw in d["cols"].items():
        a = array(d["types"][k])
        a.frombytes(raw)
        cols[k] = a
    return d["obs"], cols, d["nrep"]


def le(sv, x):      # P(X <= x)
    return bisect.bisect_right(sv, x) / len(sv)


def ge(sv, x):      # P(X >= x)
    return 1.0 - bisect.bisect_left(sv, x) / len(sv)


def two(sv, x):
    return min(1.0, 2 * min(le(sv, x), ge(sv, x)))


def mean_sd(a):
    n = len(a)
    m = sum(a) / n
    v = sum((x - m) ** 2 for x in a) / n
    return m, math.sqrt(v)


def gauss_jordan_inv(M):
    n = len(M)
    A = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(M)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(A[r][c]))
        if abs(A[p][c]) < 1e-14:
            raise ValueError("singular")
        A[c], A[p] = A[p], A[c]
        pv = A[c][c]
        A[c] = [x / pv for x in A[c]]
        for r in range(n):
            if r != c and A[r][c] != 0.0:
                f = A[r][c]
                A[r] = [a - f * b for a, b in zip(A[r], A[c])]
    return [row[n:] for row in A]


def omnibus(obs, cols, nrep, battery, label, sided="two"):
    """Split-sample min-p omnibus: half A estimates the marginal CDFs, half B
    supplies the null distribution of the minimum.  This removes the
    self-referential bias the original report flags in its own estimate."""
    half = nrep // 2
    srtA = {k: sorted(cols[k][:half]) for k in battery}
    def pval(k, x):
        sv = srtA[k]
        if sided == "two":
            return two(sv, x)
        if sided == "hi":           # one-sided, "more structure" direction
            return ge(sv, x)
        return le(sv, x)            # one-sided, "flatter" direction
    obs_ps = {k: pval(k, obs[k]) for k in battery}
    obs_min = min(obs_ps.values())
    nullmin = []
    for i in range(half, nrep):
        m = 1.0
        for k in battery:
            p = pval(k, cols[k][i])
            if p < m:
                m = p
        nullmin.append(m)
    nullmin.sort()
    p_omni = le(nullmin, obs_min)
    # Fisher combination on the same p-values
    def fisher(ps):
        return -2 * sum(math.log(max(p, 1e-12)) for p in ps)
    obs_f = fisher(obs_ps.values())
    nf = []
    for i in range(half, nrep):
        nf.append(fisher([pval(k, cols[k][i]) for k in battery]))
    nf.sort()
    p_fish = ge(nf, obs_f)
    return obs_ps, obs_min, p_omni, p_fish, nullmin


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "uniform"
    obs, cols, nrep = load(mode)
    print("=" * 78)
    print(f"ADVERSARIAL VERIFICATION part 3 -- null = {mode}, {nrep:,} replicates")
    print("=" * 78)
    srt = {k: sorted(cols[k]) for k in cols}
    se = lambda p: math.sqrt(max(p * (1 - p), 1e-12) / nrep)

    print("\n--- A. reproduce the report's marginal / family-wise numbers --------")
    rows = [
        ("IoC             P(<=obs)", le(srt["ioc"], obs["ioc"]), 0.2157),
        ("distinct        P(>=26)", ge(srt["distinct"], 26), 0.5425),
        ("doubles         P(>=6)", ge(srt["doubles"], 6), 0.1651),
        ("rep bigram prs  P(>=10)", ge(srt["bigrams"], 10), 0.1483),
        ("rep trigram prs P(=0)", le(srt["trigrams"], 0), 0.782),
        ("maxz lags 1-24  P(>=obs)", ge(srt["maxz_1_24"], obs["maxz_1_24"]), 0.1091),
        ("maxz lags 1-30  P(>=obs)", ge(srt["maxz_1_30"], obs["maxz_1_30"]), 0.1364),
        ("maxz lags 1-48  P(>=obs)", ge(srt["maxz_1_48"], obs["maxz_1_48"]), 0.2185),
        ("maxz lags 1-67  P(>=obs)", ge(srt["maxz_1_67"], obs["maxz_1_67"]), 0.3199),
        ("maxz lags 1-96  P(>=obs)", ge(srt["maxz_1_96"], obs["maxz_1_96"]), 0.5571),
        ("min-binom-p 1-96 P(<=obs)", le(srt["minp_1_96"], obs["minp_1_96"]), 0.3127),
        ("maxperz 2-48    P(>=obs)", ge(srt["maxperz_2_48"], obs["maxperz_2_48"]), 0.9913),
        ("maxperz 2-48    P(<=obs)", le(srt["maxperz_2_48"], obs["maxperz_2_48"]), 0.0087),
        ("maxperz 2-30    P(<=obs)", le(srt["maxperz_2_30"], obs["maxperz_2_30"]), None),
        ("colbig w21 pairs P(>=11)", ge(srt["colb21_pairs"], 11), 0.00635),
        ("colbig w21 excess P(>=11)", ge(srt["colb21_excess"], 11), 0.00155),
        ("colbig MAX pairs P(>=11)", ge(srt["colbmax_pairs"], 11), 0.4191),
        ("colbig MAX excess P(>=11)", ge(srt["colbmax_excess"], 11), 0.2400),
        ("doubles mod-class P(>=5)", ge(srt["modmax"], 5), 0.2452),
    ]
    print(f"  {'statistic':28s} {'mine':>9s} {'+-se':>8s} {'report':>9s} {'agree?':>8s}")
    for name, mine, rep in rows:
        flag = "" if rep is None else ("OK" if abs(mine - rep) < 4 * se(mine) + 0.004 else "**DIFF**")
        rs = "-" if rep is None else f"{rep:9.4f}"
        print(f"  {name:28s} {mine:9.4f} {se(mine):8.4f} {rs} {flag:>8s}")

    print("\n--- B. the report's omnibus, re-run with an unbiased split sample ---")
    BAT = ["ioc", "distinct", "doubles", "maxz_1_48", "maxperz_2_30", "bigrams", "trigrams"]
    ps, mn, po, pf, nm = omnibus(obs, cols, nrep, BAT, "report battery")
    print("  battery as published (7 statistics, two-sided):")
    for k in BAT:
        print(f"    {k:14s} K4 = {obs[k]:<10.4f} two-sided p = {ps[k]:.4f}")
    print(f"    -> K4 min-p = {mn:.4f} at {min(ps,key=lambda k:ps[k])}")
    print(f"    -> OMNIBUS min-p   p = {po:.4f}   (report 0.4142)")
    print(f"    -> Fisher combined p = {pf:.4f}")
    print(f"    null min-p: median {nm[len(nm)//2]:.4f}, 5th pct {nm[len(nm)//20]:.4f}")

    print("\n--- C. stress: does the omnibus survive the analyst's choices? ------")
    variants = [
        ("published battery", BAT),
        ("maxperz over 2-48 not 2-30", ["ioc", "distinct", "doubles", "maxz_1_48",
                                        "maxperz_2_48", "bigrams", "trigrams"]),
        ("drop the 2 saturated stats", ["ioc", "doubles", "maxz_1_48", "maxperz_2_30", "bigrams"]),
        ("drop saturated + use 2-48", ["ioc", "doubles", "maxz_1_48", "maxperz_2_48", "bigrams"]),
        ("+ width-21 colbigram (excess)", BAT + ["colb21_excess"]),
        ("+ width-scan colbigram max", BAT + ["colbmax_excess", "colbmax_pairs"]),
        ("maximal battery (everything)", ["ioc", "distinct", "doubles", "maxz_1_48",
                                          "maxz_1_96", "minp_1_96", "maxperz_2_48",
                                          "bigrams", "trigrams", "chi2u",
                                          "colbmax_excess", "colbmax_pairs", "modmax"]),
    ]
    print(f"  {'variant':32s} {'K4 min-p':>9s} {'omnibus':>9s} {'Fisher':>9s}")
    for label, bat in variants:
        ps2, mn2, po2, pf2, _ = omnibus(obs, cols, nrep, bat, label)
        print(f"  {label:32s} {mn2:9.4f} {po2:9.4f} {pf2:9.4f}")

    print("\n  one-sided variants of the published battery:")
    for sided, desc in (("hi", "structure direction (upper tail)"),
                        ("lo", "flatness direction (lower tail)")):
        ps3, mn3, po3, pf3, _ = omnibus(obs, cols, nrep, BAT, desc, sided=sided)
        print(f"    {desc:34s} min-p {mn3:.4f}  omnibus {po3:.4f}  Fisher {pf3:.4f}")

    print("\n--- D. the most powerful omnibus available: Mahalanobis in R^7 ------")
    CB = ["ioc", "distinct", "doubles", "maxz_1_48", "maxperz_2_48", "bigrams", "trigrams"]
    half = nrep // 2
    ms = {k: mean_sd(cols[k][:half]) for k in CB}
    def zv(i):
        return [(cols[k][i] - ms[k][0]) / ms[k][1] for k in CB]
    d = len(CB)
    C = [[0.0] * d for _ in range(d)]
    for i in range(half):
        z = zv(i)
        for a in range(d):
            za = z[a]
            for b in range(a, d):
                C[a][b] += za * z[b]
    for a in range(d):
        for b in range(a, d):
            C[a][b] /= half
            C[b][a] = C[a][b]
    Ci = gauss_jordan_inv(C)
    def maha(z):
        return sum(z[a] * Ci[a][b] * z[b] for a in range(d) for b in range(d))
    zo = [(obs[k] - ms[k][0]) / ms[k][1] for k in CB]
    m_obs = maha(zo)
    nullm = sorted(maha(zv(i)) for i in range(half, nrep))
    print("  correlation of the 7 battery statistics under the null (upper triangle):")
    print("       " + " ".join(f"{k[:7]:>7s}" for k in CB))
    for a in range(d):
        print(f"  {CB[a][:5]:5s} " + " ".join(
            ("       " if b < a else f"{C[a][b]/math.sqrt(C[a][a]*C[b][b]):7.3f}")
            for b in range(d)))
    print(f"\n  K4 standardised: " + "  ".join(f"{k[:6]}={z:+.2f}" for k, z in zip(CB, zo)))
    print(f"  Mahalanobis D^2 = {m_obs:.3f}; null median {nullm[len(nullm)//2]:.3f}, "
          f"95th {nullm[int(0.95*len(nullm))]:.3f}")
    print(f"  P(D^2 >= obs | null) = {ge(nullm, m_obs):.4f}   <- omnibus with FULL power")

    print("\n--- E. is the periodic-IoC 'flatness' anything but the overall IoC? -")
    So = obs["S"]
    idx = [i for i in range(nrep) if abs(cols["S"][i] - So) <= 12]
    sub = sorted(cols["maxperz_2_48"][i] for i in idx)
    print(f"  conditioning on S in [{So-12},{So+12}] ({len(idx):,} replicates of {nrep:,})")
    print(f"  unconditional P(maxperz_2-48 <= K4's) = "
          f"{le(srt['maxperz_2_48'], obs['maxperz_2_48']):.4f}")
    print(f"  CONDITIONAL   P(maxperz_2-48 <= K4's | same IoC) = "
          f"{le(sub, obs['maxperz_2_48']):.4f}")
    sub30 = sorted(cols["maxperz_2_30"][i] for i in idx)
    print(f"  conditional   P(maxperz_2-30 <= K4's | same IoC) = "
          f"{le(sub30, obs['maxperz_2_30']):.4f}")

    print("\n--- F. GLOBAL correction over every scanned choice in the report ----")
    GLOBAL = ["ioc", "distinct", "doubles", "bigrams", "trigrams", "chi2u",
              "maxz_1_24", "maxz_1_30", "maxz_1_48", "maxz_1_67", "maxz_1_96",
              "minp_1_24", "minp_1_48", "minp_1_96",
              "maxperz_2_30", "maxperz_2_48",
              "colbmax_pairs", "colbmax_excess", "modmax"]
    ps4, mn4, po4, pf4, nm4 = omnibus(obs, cols, nrep, GLOBAL, "global")
    print(f"  {len(GLOBAL)} statistics, each already family-wise corrected inside its own scan.")
    for k in sorted(ps4, key=lambda k: ps4[k]):
        print(f"    {k:16s} two-sided p = {ps4[k]:.4f}")
    print(f"  K4's smallest = {mn4:.4f}; GLOBAL omnibus p = {po4:.4f}; Fisher p = {pf4:.4f}")


if __name__ == "__main__":
    main()
