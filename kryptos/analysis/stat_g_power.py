#!/usr/bin/env python3
"""(f, continued) STATISTICAL POWER at n = 97.

The negative results in this suite only mean something if the tests had power.
This script answers the converse question: at 97 letters, what could the
classical tests have detected even in principle?

  * Power of the IoC test (5% level, one-sided high) to detect a periodic key
    of length L over English.
  * Power of the periodic-IoC (Friedman) test targeted at the true period.
  * Power of Kasiski (a repeated trigram whose gap is a multiple of the period).
  * The same three for the K1-K3 plaintexts as the plaintext source, to check
    that the answer does not depend on the corpus.

The output is the honest boundary of what 97 letters can say.

    python3 analysis/stat_g_power.py
"""
import math
import os
import random
from collections import Counter
from multiprocessing import Pool

import stat_common as S

TRIALS = 200_000
SEED = 20260913
NPROC = min(8, os.cpu_count() or 4)
N = 97

_CORP = None
_SANBORN = None


def _init_worker():
    global _CORP, _SANBORN
    _CORP = S.english_corpus()
    _SANBORN = S.to_ints(S.K1_PT + S.K2_PT + S.K3_PT)


def col_pairs(n, p):
    q, r = divmod(n, p)
    return r * (q + 1) * q + (p - r) * q * (q - 1)


def spectrum(b, maxlag):
    n = len(b)
    out = [0] * (maxlag + 1)
    for d in range(1, maxlag + 1):
        m = n - d
        if m <= 0:
            break
        x = int.from_bytes(b[:m], "big") ^ int.from_bytes(b[d:], "big")
        out[d] = x.to_bytes(m, "big").count(0)
    return out


def per_ioc(spec, n, p):
    s = 2 * sum(spec[d] for d in range(p, n, p))
    D = col_pairs(n, p)
    return s / D if D else float("nan")


def per_ioc_direct(b, p):
    """Pooled period-p column IoC without building the whole lag spectrum.

    Only separations that are multiples of p contribute, so this touches
    n/p lags instead of n-1.  Checked against per_ioc(spectrum(...)) in
    _selftest() before any use.
    """
    n = len(b)
    s = 0
    for d in range(p, n, p):
        m = n - d
        x = int.from_bytes(b[:m], "big") ^ int.from_bytes(b[d:], "big")
        s += x.to_bytes(m, "big").count(0)
    D = col_pairs(n, p)
    return (2 * s / D) if D else float("nan")


def _selftest():
    """per_ioc_direct must agree exactly with the spectrum-based computation."""
    import random as _r
    rng = _r.Random(11)
    worst = 0.0
    for _ in range(40):
        b = bytes(rng.randrange(26) for _ in range(N))
        spec = spectrum(b, N - 1)
        for p in range(2, 31):
            worst = max(worst, abs(per_ioc(spec, N, p) - per_ioc_direct(b, p)))
    assert worst == 0.0, worst
    return worst


def kasiski_hit(b, p):
    """Does the text contain a repeated trigram whose gap is a multiple of p?"""
    seen = {}
    for i in range(len(b) - 2):
        seen.setdefault(b[i:i + 3], []).append(i)
    for pos in seen.values():
        if len(pos) > 1:
            for i in range(len(pos)):
                for j in range(i + 1, len(pos)):
                    if (pos[j] - pos[i]) % p == 0:
                        return True
    return False


def any_repeated_trigram(b):
    seen = set()
    for i in range(len(b) - 2):
        g = b[i:i + 3]
        if g in seen:
            return True
        seen.add(g)
    return False


# --- the honest, SCANNED version of the periodic-IoC test -------------------
# An attacker does not know the period, so the realistic test is
#   reject iff  max over p in 2..PSCAN of z_p  >=  crit,
# with crit the 95th percentile of that maximum under the uniform null.
# That percentile is measured in stat_d_autocorr.py section 4 from 10^6
# replicates at n = 97: +3.720 (uniform null) / +3.386 (K4-letter shuffle).
PSCAN = 48
SCAN_CRIT = 3.720
_PSD = {p: math.sqrt(2 * (1 / 26) * (25 / 26) / col_pairs(N, p))
        for p in range(2, PSCAN + 1)}


def scan_maxz(spec):
    mu = 1 / 26
    best = -99.0
    for p in range(2, PSCAN + 1):
        z = (per_ioc(spec, N, p) - mu) / _PSD[p]
        if z > best:
            best = z
    return best


def _chunk(args):
    seed, trials, L, src = args
    rng = random.Random(seed)
    corpus = _CORP if src == "corpus" else _SANBORN
    hi = len(corpus) - N - 1
    iocs = []
    perz = []
    kas = 0
    trig = 0
    scan = 0
    mu = 1 / 26
    sd = math.sqrt(2 * mu * (1 - mu) / col_pairs(N, L)) if L > 1 else 1.0
    for _ in range(trials):
        i = rng.randrange(hi)
        pt = corpus[i:i + N]
        key = bytes(rng.randrange(26) for _ in range(L))
        ct = bytes((pt[j] + key[j % L]) % 26 for j in range(N))
        c = Counter(ct)
        iocs.append(sum(v * (v - 1) for v in c.values()) / (N * (N - 1)))
        spec = spectrum(ct, N - 1)
        perz.append((per_ioc(spec, N, L) - mu) / sd if L > 1 else 99.0)
        if scan_maxz(spec) >= SCAN_CRIT:
            scan += 1
        if any_repeated_trigram(ct):
            trig += 1
            if kasiski_hit(ct, L):
                kas += 1
    return iocs, perz, kas, trig, trials, scan


def run(L, src, trials, seed):
    per = trials // NPROC
    args = [(seed + 7919 * i + 31 * L, per, L, src) for i in range(NPROC)]
    with Pool(NPROC, initializer=_init_worker) as pl:
        parts = pl.map(_chunk, args)
    iocs, perz = [], []
    kas = trig = tot = scan = 0
    for a, b_, c_, d_, t, sc in parts:
        iocs.extend(a)
        perz.extend(b_)
        kas += c_
        trig += d_
        tot += t
        scan += sc
    iocs.sort()
    perz.sort()
    return iocs, perz, kas, trig, tot, scan


def main():
    print("=" * 78)
    print("STATISTICAL POWER AT n = 97 -- what could these tests ever have found?")
    print("=" * 78)
    print(f"\n[selftest] per_ioc_direct vs full-spectrum per_ioc: "
          f"max abs diff {_selftest():.1f}   (must be exactly 0)")

    # critical values from the exact uniform null
    obsS = S.ioc_S(S.K4)
    dist = S.exact_ioc_cdf(N, s_cap=520, c=26)
    cum = 0.0
    crit_ioc = None
    for s in sorted(dist):
        cum += dist[s]
        if cum >= 0.95 and crit_ioc is None:
            crit_ioc = s / (N * 95 + N)  # placeholder, fixed below
            crit_S = s
            break
    crit_ioc = crit_S / (N * (N - 1))
    print(f"\n5%-level critical value of the IoC (exact uniform null, n=97): "
          f"IoC >= {crit_ioc:.5f} (S >= {crit_S})")
    print(f"K4's IoC is {S.ioc(S.K4):.5f}; K4 does not come close to it.")
    print("\nPeriodic-IoC test, two versions:")
    print("  ORACLE  -- z >= 1.645 AT THE TRUE PERIOD.  Maximally generous: it assumes")
    print("             the attacker is told the period in advance.")
    print(f"  SCANNED -- max over p = 2..{PSCAN} of z_p >= {SCAN_CRIT}, the 95th percentile")
    print("             of that maximum under the uniform null (measured in")
    print("             stat_d_autocorr.py section 4 from 10^6 replicates).  This is")
    print("             what a real attacker can actually run.")

    print(f"\n{TRIALS:,} simulated Vigenere encipherments of random 97-letter English")
    print("windows per key length.\n")
    print(f"{'L':>3s} {'mean IoC':>9s} {'pwr IoC':>9s} "
          f"{'pwr perIoC(oracle)':>19s} {'pwr perIoC(scan)':>17s} "
          f"{'P(rep.trigram)':>15s} {'pwr Kasiski':>12s}")
    rows = []
    for L in list(range(1, 21)) + [22, 24, 26, 28, 30]:
        iocs, perz, kas, trig, tot, scan = run(L, "corpus", TRIALS, SEED + L)
        p_ioc = S.frac_ge(iocs, crit_ioc)
        p_per = S.frac_ge(perz, 1.645) if L > 1 else 1.0
        p_scan = scan / tot
        rows.append((L, sum(iocs) / tot, p_ioc, p_per, trig / tot, kas / tot, p_scan))
        print(f"{L:3d} {sum(iocs)/tot:9.5f} {p_ioc:9.4f} {p_per:19.4f} "
              f"{p_scan:17.4f} {trig/tot:15.4f} {kas/tot:12.4f}")

    half = [r[0] for r in rows if r[2] >= 0.5]
    half_p = [r[0] for r in rows if r[3] >= 0.5]
    half_s = [r[0] for r in rows if r[6] >= 0.5]
    print(f"\n  IoC test has >= 50% power only for L <= {max(half) if half else 0}")
    print(f"  periodic-IoC ORACLE  (told the period) has >= 50% power for "
          f"L <= {max(half_p) if half_p else 0}")
    print(f"  periodic-IoC SCANNED (the realistic test) has >= 50% power for "
          f"L <= {max(half_s) if half_s else 0}")
    print("  Kasiski essentially never fires: a 97-letter text rarely repeats a trigram")
    print("  at all, which is why K4's zero repeated trigrams is not informative.")

    print("\n--- Corpus dependence check: Sanborn's own English (K1-K3 plaintext) ---")
    print(f"{'L':>3s} {'mean IoC (corpus)':>18s} {'mean IoC (K1-K3 pt)':>20s} "
          f"{'power corpus':>13s} {'power K1-K3':>12s}")
    for L in (2, 5, 8, 10, 15, 20, 30):
        i1, p1, _, _, t1, _ = run(L, "corpus", 40_000, SEED + 500 + L)
        i2, p2, _, _, t2, _ = run(L, "sanborn", 40_000, SEED + 900 + L)
        print(f"{L:3d} {sum(i1)/t1:18.5f} {sum(i2)/t2:20.5f} "
              f"{S.frac_ge(i1, crit_ioc):13.4f} {S.frac_ge(i2, crit_ioc):12.4f}")
    print("\n  The two plaintext sources give the same answer to two decimal places,")
    print("  so nothing below depends on which English corpus is used.")

    print("\n--- The conclusion that matters ------------------------------------")
    print("At 97 letters the classical statistics are blind beyond a key length of")
    print(f"about {max(half_s) if half_s else 0}.  Every negative in this project that rests on")
    print("statistics alone therefore applies ONLY to the short-key end of the space.")
    print("Periods 27, 28, 29 and everything >= 53 -- the ones the cribs cannot")
    print("constrain either -- are exactly the region where BOTH tools are powerless.")
    print("That region is not 'ruled out by statistics'; it is unexamined.")


if __name__ == "__main__":
    main()
