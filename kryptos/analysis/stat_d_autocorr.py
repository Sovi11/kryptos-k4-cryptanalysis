#!/usr/bin/env python3
"""(d) Autocorrelation and the periodic-IoC scan, with honest multiple testing.

Two pieces of K4 folklore are settled here with null distributions of the
MAXIMUM of the scanned statistic, not of a single pre-specified one:

  * "autocorrelation spike at lag 7, z = +3.0";
  * "periodic-IoC peaks at periods 25, 28, 30".

Machinery
---------
The whole lag spectrum C(d) = #{i : x_i = x_{i+d}} is computed in one shot with
an integer-XOR trick (bytes -> int, XOR, count zero bytes), which is ~50x faster
than a Python loop and lets 10^6 Monte-Carlo replicates run in minutes.

The pooled periodic IoC at period p is derived from the SAME spectrum:
within-column pairs are exactly the pairs whose separation is a multiple of p,
so   S(p) = 2 * sum_{k>=1} C(kp)   and   IoC(p) = S(p) / D(p),
D(p) = sum over columns of m(m-1).  Exact null moments follow the same
argument as for the plain IoC: mean 1/26, Var = 2p(1-p)/D(p).

    python3 analysis/stat_d_autocorr.py
"""
import math
import os
from collections import Counter
from multiprocessing import Pool

import stat_common as S

TRIALS = 1_000_000
TRIALS_CTRL = 100_000
SEED = 20260913
NPROC = min(8, os.cpu_count() or 4)
MAXLAG = 96
PMAX = 48


# ------------------------------------------------------------- spectrum -----
def spectrum(b, maxlag=None):
    """C[d] for d = 1..maxlag, via XOR of the two shifted byte strings."""
    n = len(b)
    maxlag = maxlag or (n - 1)
    out = [0] * (maxlag + 1)
    for d in range(1, maxlag + 1):
        m = n - d
        if m <= 0:
            break
        x = int.from_bytes(b[:m], "big") ^ int.from_bytes(b[d:], "big")
        out[d] = x.to_bytes(m, "big").count(0)
    return out


def col_pairs(n, p):
    """D(p) = sum over the p columns of m(m-1)."""
    q, r = divmod(n, p)
    return r * (q + 1) * q + (p - r) * q * (q - 1)


def pooled_ioc_from_spectrum(spec, n, p):
    s = 2 * sum(spec[d] for d in range(p, min(n, len(spec)), p))
    d = col_pairs(n, p)
    return (s / d) if d else float("nan"), s, d


def periodic_moments(n, p, c=26):
    d = col_pairs(n, p)
    pp = 1.0 / c
    return pp, math.sqrt(2 * pp * (1 - pp) / d) if d else float("nan")


def lag_z(count, m, c=26):
    pp = 1.0 / c
    return (count - m * pp) / math.sqrt(m * pp * (1 - pp))


_SF_CACHE = {}


def sf_table(m, c=26):
    """[P(Binom(m,1/c) >= k) for k = 0..m], by a stable forward recursion.

    Replaces per-call math.comb summation, which made the 10^6-replicate null
    run for days.  Checked against stat_common.binom_sf in _selftest().
    """
    t = _SF_CACHE.get(m)
    if t is not None:
        return t
    p = 1.0 / c
    q = 1.0 - p
    pmf = [0.0] * (m + 1)
    pmf[0] = q ** m
    r = p / q
    for k in range(1, m + 1):
        pmf[k] = pmf[k - 1] * (m - k + 1) / k * r
    sf = [0.0] * (m + 2)
    for k in range(m, -1, -1):
        sf[k] = sf[k + 1] + pmf[k]
    t = sf[:m + 1]
    _SF_CACHE[m] = t
    return t


def lag_p_exact(count, m, c=26):
    """P(Binomial(m, 1/26) >= count) -- the honest per-lag p-value."""
    t = sf_table(m, c)
    return t[count] if count <= m else 0.0


def _selftest():
    """Verify the fast SF table against the slow exact one before any use."""
    worst = 0.0
    for m in (5, 17, 50, 90, 96, 200, 368):
        t = sf_table(m)
        for k in sorted({min(k, m) for k in (0, 1, 2, 3, 5, 9, 15, m)}):
            worst = max(worst, abs(t[k] - S.binom_sf(k, m, 1 / 26.0)))
    assert worst < 1e-12, worst
    return worst


# -------------------------------------------------- Counter-based samples ---
# Every statistic collected below is DISCRETE: a lag-z is (integer count minus
# a constant) / constant, an exact binomial tail comes from a finite table, and
# a pooled periodic IoC is (even integer)/D(p).  So the Monte-Carlo sample is
# stored as a Counter over its distinct values rather than as a 10^6-long list.
# Exact, ~1000x smaller, and it keeps the multiprocessing result payload tiny
# (a 10^6-float list per worker per statistic overflowed the pool's pipe).

def c_total(c):
    return sum(c.values())


def c_mean_sd(c):
    tot = c_total(c)
    m = sum(k * v for k, v in c.items()) / tot
    var = sum((k - m) ** 2 * v for k, v in c.items()) / tot
    return m, math.sqrt(var)


def c_quantile(c, q):
    tot = c_total(c)
    want = q * tot
    run = 0
    for k in sorted(c):
        run += c[k]
        if run >= want:
            return k
    return max(c)


def c_frac_ge(c, x):
    tot = c_total(c)
    return sum(v for k, v in c.items() if k >= x) / tot


def c_frac_le(c, x):
    tot = c_total(c)
    return sum(v for k, v in c.items() if k <= x) / tot


# ------------------------------------------------------------- workers ------
def _null_chunk(args):
    (seed, trials, n, mode, multiset, lag_ranges, per_moments) = args
    import random
    if mode == "uniform":
        pool = S.LetterPool(seed)
        gen = lambda: pool.take(n)
    else:
        rng = random.Random(seed)
        chars = list(multiset)
        def gen():
            rng.shuffle(chars)
            return bytes(chars)

    # never index a lag with no pairs: a control text can be shorter than MAXLAG
    maxlag = min(MAXLAG, n - 1)
    ranges = [(lo, min(hi, maxlag)) for (lo, hi) in lag_ranges]

    maxz = {r: Counter() for r in lag_ranges}
    minp = {r: Counter() for r in lag_ranges}
    per_sum = [0.0] * (PMAX + 1)
    per_sq = [0.0] * (PMAX + 1)
    per_maxz = Counter()
    for _ in range(trials):
        b = gen()
        spec = spectrum(b, maxlag)
        zs = [0.0] * (maxlag + 1)
        for d in range(1, maxlag + 1):
            zs[d] = lag_z(spec[d], n - d)
        for r, (lo, hi) in zip(lag_ranges, ranges):
            maxz[r][max(zs[lo:hi + 1])] += 1
        # exact-binomial version, for the last (widest) range
        lo, hi = ranges[-1]
        best = 1.0
        for d in range(lo, hi + 1):
            pv = lag_p_exact(spec[d], n - d)
            if pv < best:
                best = pv
        minp[lag_ranges[-1]][best] += 1
        # periodic IoC -- only when the caller asked for it (it needs the full
        # spectrum, which only the n = 97 runs compute)
        if per_moments is not None:
            mz = -99.0
            for p in range(2, PMAX + 1):
                v, _, _ = pooled_ioc_from_spectrum(spec, n, p)
                per_sum[p] += v
                per_sq[p] += v * v
                mu, sd = per_moments[p]
                z = (v - mu) / sd
                if z > mz:
                    mz = z
            per_maxz[mz] += 1
    return maxz, minp, per_sum, per_sq, per_maxz, trials


def run_null(n, mode, multiset, trials, seed, lag_ranges, per_moments):
    per = trials // NPROC
    args = [(seed + 104729 * i, per, n, mode, multiset, lag_ranges, per_moments)
            for i in range(NPROC)]
    with Pool(NPROC) as pl:
        parts = pl.map(_null_chunk, args)
    maxz = {r: Counter() for r in lag_ranges}
    minp = {r: Counter() for r in lag_ranges}
    per_sum = [0.0] * (PMAX + 1)
    per_sq = [0.0] * (PMAX + 1)
    per_maxz = Counter()
    tot = 0
    for mz, mp, psu, psq, pmz, t in parts:
        for r in lag_ranges:
            maxz[r].update(mz[r])
            minp[r].update(mp[r])
        for p in range(PMAX + 1):
            per_sum[p] += psu[p]
            per_sq[p] += psq[p]
        per_maxz.update(pmz)
        tot += t
    return maxz, minp, per_sum, per_sq, per_maxz, tot


# ---------------------------------------------------------------- main ------
def main():
    print("=" * 78)
    print("(d) AUTOCORRELATION SPECTRUM AND PERIODIC-IoC SCAN")
    print("=" * 78)
    print(f"\n[selftest] fast binomial SF table vs exact math.comb sum: "
          f"max abs diff {_selftest():.2e}   (must be < 1e-12)")

    b = S.K4_B
    n = 97
    spec = spectrum(b, MAXLAG)

    print("\n--- 1. K4's full lag spectrum, lags 1..96 ---------------------------")
    print(f"{'lag':>4s} {'pairs':>6s} {'obs':>4s} {'exp':>6s} {'z':>7s} {'P(>=obs)':>9s}"
          "   |  " + f"{'lag':>4s} {'pairs':>6s} {'obs':>4s} {'exp':>6s} {'z':>7s} {'P(>=obs)':>9s}")
    rows = []
    for d in range(1, MAXLAG + 1):
        m = n - d
        rows.append((d, m, spec[d], m / 26, lag_z(spec[d], m), lag_p_exact(spec[d], m)))
    half = (len(rows) + 1) // 2
    for i in range(half):
        a = rows[i]
        line = (f"{a[0]:4d} {a[1]:6d} {a[2]:4d} {a[3]:6.2f} {a[4]:+7.2f} {a[5]:9.5f}")
        if i + half < len(rows):
            c = rows[i + half]
            line += ("   |  " + f"{c[0]:4d} {c[1]:6d} {c[2]:4d} {c[3]:6.2f} "
                     f"{c[4]:+7.2f} {c[5]:9.5f}")
        print(line)

    obs_z = {d: rows[d - 1][4] for d in range(1, MAXLAG + 1)}
    obs_p = {d: rows[d - 1][5] for d in range(1, MAXLAG + 1)}
    print(f"\n  total coincidences over all 96 lags: {sum(spec[1:]):d}  "
          f"(expected {sum(n - d for d in range(1, 97))/26:.1f})")
    top = sorted(range(1, MAXLAG + 1), key=lambda d: -obs_z[d])[:8]
    print("  top lags by z: " + ", ".join(f"lag {d} z={obs_z[d]:+.2f} "
                                          f"(p={obs_p[d]:.4f})" for d in top))
    bot = sorted(range(1, MAXLAG + 1), key=lambda d: obs_z[d])[:3]
    print("  most negative:  " + ", ".join(f"lag {d} z={obs_z[d]:+.2f}" for d in bot))

    print("\n  NOTE on long lags: at lag 90 there are only 7 pairs, at lag 96 only one.")
    print("  A SINGLE coincidence at lag 96 scores z = +4.99.  Any 'max z over lags")
    print("  1..96' therefore has a null mean above +3 for purely degenerate reasons.")
    print("  The lag ranges below are reported separately for that reason.")

    lag_ranges = [(1, 24), (1, 30), (1, 48), (1, 67), (1, 96)]
    print("\n--- 2. Null distribution of the MAXIMUM z over a scanned lag range --")
    print(f"{TRIALS:,} Monte-Carlo replicates per null.")

    per_mom = {p: periodic_moments(n, p) for p in range(2, PMAX + 1)}

    results = {}
    for mode, label in (("uniform", "uniform random 97 letters"),
                        ("shuffle", "random permutation of K4's own 97 letters")):
        maxz, minp, psum, psq, pmz, tot = run_null(
            n, mode, b, TRIALS, SEED + (0 if mode == "uniform" else 555),
            lag_ranges, per_mom)
        results[mode] = (maxz, minp, psum, psq, pmz, tot)
        print(f"\n  null = {label}   ({tot:,} replicates)")
        print(f"  {'lag range':>11s} {'observed max z':>15s} {'null mean':>10s} "
              f"{'null 95th':>10s} {'family-wise p':>14s}")
        for r in lag_ranges:
            lo, hi = r
            om = max(obs_z[d] for d in range(lo, hi + 1))
            vals = maxz[r]
            mu, sd = c_mean_sd(vals)
            p95 = c_quantile(vals, 0.95)
            fw = c_frac_ge(vals, om)
            print(f"  {f'{lo}..{hi}':>11s} {om:15.3f} {mu:10.3f} {p95:10.3f} {fw:14.4f}")
        # exact-p version for the full range
        r = lag_ranges[-1]
        om_p = min(obs_p[d] for d in range(r[0], r[1] + 1))
        vals = minp[r]
        fw = c_frac_le(vals, om_p)
        print(f"  [better statistic] min exact binomial p over lags {r[0]}..{r[1]}: "
              f"observed {om_p:.5f}, family-wise p = {fw:.4f}")

    print("\n  Pre-specified single-lag comparison (what the folklore implicitly claims):")
    print(f"    lag 7 alone, exact:  P(Binomial(90, 1/26) >= 9) = {obs_p[7]:.5f}")
    print("    That is the ONLY way to get a small number here, and it requires having")
    print("    named lag 7 before looking, which nobody did.")

    print("\n--- 3. Controls: do K1/K2/K3 show the same kind of 'spike'? ---------")
    print(f"{TRIALS_CTRL:,} replicates each, lag range 1..48.")
    print(f"{'text':16s} {'n':>5s} {'best lag':>9s} {'max z':>8s} {'null mean':>10s} "
          f"{'null 95th':>10s} {'family-wise p':>14s}")
    for name, t in (("K1 ciphertext", S.K1_CT), ("K2 ciphertext", S.K2_CT),
                    ("K3 ciphertext", S.K3_CT), ("K4 ciphertext", S.K4_CT)):
        bb = S.to_ints(t)
        nn = len(bb)
        hi = min(48, nn - 2)
        sp = spectrum(bb, hi)
        zs = {d: lag_z(sp[d], nn - d) for d in range(1, hi + 1)}
        best = max(zs, key=lambda d: zs[d])
        maxz, _, _, _, _, tot = run_null(nn, "uniform", bb, TRIALS_CTRL,
                                         SEED + 3 * nn, [(1, hi)], None)
        vals = maxz[(1, hi)]
        mu, sd = c_mean_sd(vals)
        print(f"{name:16s} {nn:5d} {best:9d} {zs[best]:8.2f} {mu:10.3f} "
              f"{c_quantile(vals, 0.95):10.3f} {c_frac_ge(vals, zs[best]):14.4f}")
    print("\n  Every solved Kryptos section shows a comparable 'spike'.  A max-z near +3")
    print("  is the normal output of scanning ~50 lags of a 100-400 letter string.")

    print("\n--- 4. Periodic-IoC scan, periods 2..48 -----------------------------")
    print("Pooled column IoC.  Exact null moments (mean 1/26, Var = 2p(1-p)/D(p))")
    print("where D(p) is the number of ordered within-column pairs.")
    print(f"\n{'p':>3s} {'cols (len)':>14s} {'D(p)':>6s} {'IoC(p)':>8s} {'null sd':>8s} "
          f"{'z':>7s}   |  {'p':>3s} {'cols (len)':>14s} {'D(p)':>6s} {'IoC(p)':>8s} "
          f"{'null sd':>8s} {'z':>7s}")
    prows = []
    for p in range(2, PMAX + 1):
        v, s_, d_ = pooled_ioc_from_spectrum(spec, n, p)
        mu, sd = periodic_moments(n, p)
        q, r = divmod(n, p)
        desc = f"{r}x{q+1}+{p-r}x{q}"
        prows.append((p, desc, d_, v, sd, (v - mu) / sd))
    half = (len(prows) + 1) // 2
    for i in range(half):
        a = prows[i]
        line = f"{a[0]:3d} {a[1]:>14s} {a[2]:6d} {a[3]:8.5f} {a[4]:8.5f} {a[5]:+7.2f}"
        if i + half < len(prows):
            c = prows[i + half]
            line += (f"   |  {c[0]:3d} {c[1]:>14s} {c[2]:6d} {c[3]:8.5f} "
                     f"{c[4]:8.5f} {c[5]:+7.2f}")
        print(line)

    obs_per_maxz = max(r[5] for r in prows)
    obs_per_best = max(prows, key=lambda r: r[5])
    print(f"\n  observed maximum standardised periodic IoC: period {obs_per_best[0]}, "
          f"IoC = {obs_per_best[3]:.5f}, z = {obs_per_maxz:+.2f}")
    for mode, label in (("uniform", "uniform random"), ("shuffle", "K4-letter shuffle")):
        pmz = results[mode][4]
        mu, sd = c_mean_sd(pmz)
        print(f"  null = {label:18s}: max-z over p=2..48 has mean {mu:+.3f}, "
              f"95th pct {c_quantile(pmz, 0.95):+.3f}; "
              f"family-wise p = {c_frac_ge(pmz, obs_per_maxz):.4f}")
    print("\n  Per-period null means from the same simulation (uniform null), which")
    print("  shows why raw IoC values at large p look big:")
    psum, psq, tot = results["uniform"][2], results["uniform"][3], results["uniform"][5]
    print(f"  {'p':>3s} {'null mean IoC':>14s} {'null sd (MC)':>13s} {'null sd (exact)':>16s}")
    for p in (2, 5, 7, 10, 14, 21, 25, 28, 30, 40, 48):
        m_ = psum[p] / tot
        v_ = psq[p] / tot - m_ * m_
        print(f"  {p:3d} {m_:14.5f} {math.sqrt(max(v_,0)):13.5f} "
              f"{periodic_moments(n, p)[1]:16.5f}")
    print("\n  At p = 28 the columns hold 3-4 letters; a single accidental repeat inside")
    print("  one column moves the pooled IoC by ~0.02.  Raw peaks at p = 25/28/30 are")
    print("  a consequence of that variance, not of structure, and they vanish once the")
    print("  value is standardised by the correct per-period sd (column z above).")


if __name__ == "__main__":
    main()
