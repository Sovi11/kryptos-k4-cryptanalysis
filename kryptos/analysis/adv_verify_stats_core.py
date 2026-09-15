#!/usr/bin/env python3
"""ADVERSARIAL VERIFICATION of findings/statistics.md -- independent re-implementation.

Nothing here imports stat_common.py or any other script from this repo.  Every
statistic, every null and every p-value is written from scratch so that a bug in
the original suite cannot propagate into the check.

Part 1: observed statistics + exact nulls (closed form / DP, no Monte Carlo).
"""
import math
from collections import Counter
from fractions import Fraction

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
assert len(K4) == 97 and K4.isalpha() and K4.isupper()

N = len(K4)
V = [ord(c) - 65 for c in K4]


# ---------------------------------------------------------------- statistics
def ioc_S(v):
    return sum(k * (k - 1) for k in Counter(v).values())


def ioc(v):
    n = len(v)
    return ioc_S(v) / (n * (n - 1))


def coincidences(v, lag):
    """Naive O(n) count -- deliberately dumb, used to validate the fast version."""
    return sum(1 for i in range(len(v) - lag) if v[i] == v[i + lag])


def spectrum_naive(v):
    return [0] + [coincidences(v, d) for d in range(1, len(v))]


def n_doubles(v):
    return coincidences(v, 1)


def n_distinct(v):
    return len(set(v))


def rep_ngram_pairs(v, k):
    c = Counter(tuple(v[i:i + k]) for i in range(len(v) - k + 1))
    return sum(m * (m - 1) // 2 for m in c.values())


def col_pairs(n, p):
    q, r = divmod(n, p)
    return r * (q + 1) * q + (p - r) * q * (q - 1)


def periodic_ioc_z(v, p):
    """Pooled within-column IoC at period p, standardised against the uniform null.

    Independent implementation: build the columns explicitly rather than
    summing the autocorrelation spectrum at multiples of p.
    """
    n = len(v)
    cols = [v[i::p] for i in range(p)]
    num = sum(k * (k - 1) for col in cols for k in Counter(col).values())
    D = sum(len(col) * (len(col) - 1) for col in cols)
    assert D == col_pairs(n, p), (p, D, col_pairs(n, p))
    if D == 0:
        return None
    mu = 1 / 26
    sd = math.sqrt(2 * mu * (1 - mu) / D)
    return (num / D - mu) / sd


def col_bigrams(v, width, convention):
    """Vertical bigrams when the text is written in rows of `width`.

    A column bigram is (v[i], v[i+width]).  'pairs' = sum C(m,2); 'excess' = sum (m-1).
    """
    n = len(v)
    c = Counter((v[i], v[i + width]) for i in range(n - width))
    if convention == "pairs":
        return sum(m * (m - 1) // 2 for m in c.values())
    return sum(m - 1 for m in c.values())


# ------------------------------------------------------- exact null: doubles
def binom_sf(k, n, p):
    """P(X >= k) for X~Binomial(n,p), exact rational then float."""
    P = Fraction(p).limit_denominator(10**6)
    tot = Fraction(0)
    for i in range(k, n + 1):
        tot += math.comb(n, i) * P**i * (1 - P) ** (n - i)
    return float(tot)


# ----------------------------------------------- exact null: coupon collector
def p_all_present(n, c=26):
    """P(all c letters appear in n uniform draws) -- inclusion-exclusion."""
    return sum((-1) ** i * math.comb(c, i) * ((c - i) / c) ** n for i in range(c + 1))


def distinct_pmf(n, c=26):
    """Exact pmf of the number of distinct letters in n uniform draws."""
    # P(exactly k distinct) = C(c,k) * Surj(n,k)/c^n, Surj via inclusion-exclusion
    out = {}
    for k in range(0, c + 1):
        s = sum((-1) ** j * math.comb(k, j) * (k - j) ** n for j in range(k + 1))
        out[k] = math.comb(c, k) * s / c**n
    return out


# ----------------------------------------------------------- exact null: IoC
def exact_ioc_lower_tail(n, Smax, c=26):
    """P(S <= Smax) where S = sum n_i(n_i-1) over c cells, n uniform draws.

    DP over letter types.  Q[j][s] = (number of length-j strings over the types
    processed so far with statistic s) * 26^-j.  Truncated at s > Smax, which is
    exact for a lower tail because s never decreases.
    Returns (P(S<=Smax), dict s -> P(S=s)).
    """
    inv = 1.0 / c
    pw = [inv**m for m in range(n + 1)]
    Q = [[0.0] * (Smax + 1) for _ in range(n + 1)]
    Q[0][0] = 1.0
    for _t in range(c):
        R = [[0.0] * (Smax + 1) for _ in range(n + 1)]
        for j in range(n + 1):
            row = Q[j]
            for s in range(Smax + 1):
                q = row[s]
                if q == 0.0:
                    continue
                m = 0
                while j + m <= n:
                    ds = m * (m - 1)
                    if s + ds > Smax:
                        break
                    R[j + m][s + ds] += q * math.comb(j + m, m) * pw[m]
                    m += 1
        Q = R
    pmf = {s: Q[n][s] for s in range(Smax + 1) if Q[n][s] > 0}
    return sum(pmf.values()), pmf


def main():
    print("=" * 78)
    print("ADVERSARIAL VERIFICATION -- part 1: observed stats and EXACT nulls")
    print("=" * 78)

    # -- validate the fast spectrum trick against the naive loop --------------
    def spectrum_fast(b):
        n = len(b)
        out = [0] * n
        for d in range(1, n):
            m = n - d
            x = int.from_bytes(b[:m], "big") ^ int.from_bytes(b[d:], "big")
            out[d] = x.to_bytes(m, "big").count(0)
        return out

    bb = bytes(V)
    assert spectrum_fast(bb) == spectrum_naive(V), "fast spectrum disagrees with naive"
    print("\n[check] fast XOR spectrum == naive O(n^2) spectrum for K4: OK")

    S = ioc_S(V)
    print(f"\nK4: n={N}  S=sum n_i(n_i-1) = {S}  IoC = {S}/{N*(N-1)} = {ioc(V):.6f}")
    print(f"K4: distinct letters = {n_distinct(V)}")
    d_pos = [i + 1 for i in range(N - 1) if V[i] == V[i + 1]]
    print(f"K4: adjacent doubles = {n_doubles(V)} at 1-indexed {d_pos}  "
          f"({''.join(K4[i-1:i+1] for i in d_pos)})")
    print(f"K4: repeated bigram pairs = {rep_ngram_pairs(V,2)}, "
          f"trigram pairs = {rep_ngram_pairs(V,3)}, 4-gram pairs = {rep_ngram_pairs(V,4)}")

    spec = spectrum_naive(V)
    print(f"K4: total coincidences over lags 1..96 = {sum(spec)} "
          f"(= S/2 = {S//2}); expected {sum((N-d)/26 for d in range(1,N)):.2f}")

    print("\n--- exact null: IoC ------------------------------------------------")
    tail, pmf = exact_ioc_lower_tail(N, S)
    print(f"  EXACT P(S <= {S}) = P(IoC <= {ioc(V):.6f}) = {tail:.6f}")
    print(f"  report claims 0.215723   -> diff {abs(tail-0.215723):.2e}")
    # moments, closed form
    mu = 1 / 26
    var = 2 * mu * (1 - mu) / (N * (N - 1))
    print(f"  closed-form null mean {mu:.6f} sd {math.sqrt(var):.6f}; "
          f"z = {(ioc(V)-mu)/math.sqrt(var):+.3f}")
    # exact quantiles of the lower tail
    cum, qs, want = 0.0, {}, [0.001, 0.01, 0.025, 0.05, 0.25]
    for s in sorted(pmf):
        cum += pmf[s]
        for w in want:
            if w not in qs and cum >= w:
                qs[w] = s / (N * (N - 1))
    print("  exact lower quantiles of IoC: " +
          "  ".join(f"{int(w*1000)/10}%={qs[w]:.5f}" for w in want if w in qs))

    print("\n--- exact null: coverage -------------------------------------------")
    pa = p_all_present(N)
    print(f"  EXACT P(all 26 letters present | 97 uniform) = {pa:.6f}  "
          f"(report 0.5425, diff {abs(pa-0.5425):.2e})")
    pm = distinct_pmf(N)
    m = sum(k * v for k, v in pm.items())
    sd = math.sqrt(sum(k * k * v for k, v in pm.items()) - m * m)
    print(f"  exact mean distinct {m:.4f}, sd {sd:.4f}; K4's 26 is z = {(26-m)/sd:+.3f}")

    print("\n--- exact null: doubles --------------------------------------------")
    p6 = binom_sf(6, N - 1, Fraction(1, 26))
    print(f"  EXACT P(Binom(96,1/26) >= 6) = {p6:.6f}  (report 0.1651, "
          f"diff {abs(p6-0.1651):.2e})")
    mb, sb = (N - 1) / 26, math.sqrt((N - 1) * (1 / 26) * (25 / 26))
    print(f"  mean {mb:.4f} sd {sb:.4f}; z = {(6-mb)/sb:+.3f}")

    print("\n--- exact null: lag-7 coincidences ---------------------------------")
    for lag in (7,):
        obs, mtrials = spec[lag], N - lag
        pl = binom_sf(obs, mtrials, Fraction(1, 26))
        z = (obs - mtrials / 26) / math.sqrt(mtrials * (1 / 26) * (25 / 26))
        print(f"  lag {lag}: obs {obs}, trials {mtrials}, exp {mtrials/26:.3f}, "
              f"z = {z:+.3f}, EXACT P(>= obs) = {pl:.6f} (report 0.00787)")
    top = sorted(range(1, N), key=lambda d: -(spec[d] - (N-d)/26) /
                 math.sqrt((N-d)*(1/26)*(25/26)))[:8]
    print("  eight largest standardised lags (lag, obs, exp, z):")
    for d in top:
        mt = N - d
        z = (spec[d] - mt/26) / math.sqrt(mt*(1/26)*(25/26))
        print(f"    lag {d:3d}  obs {spec[d]:2d}  exp {mt/26:6.3f}  z {z:+.3f}")

    print("\n--- observed: periodic IoC z ---------------------------------------")
    pz = {p: periodic_ioc_z(V, p) for p in range(2, 49)}
    best30 = max(range(2, 31), key=lambda p: pz[p])
    best48 = max(range(2, 49), key=lambda p: pz[p])
    print(f"  max z over periods 2..30 = {pz[best30]:+.3f} at p={best30} "
          f"(report +1.129 at 25)")
    print(f"  max z over periods 2..48 = {pz[best48]:+.3f} at p={best48} "
          f"(report +1.13 at 25)")
    for p in (7, 21, 25, 28, 30):
        print(f"    p={p:2d}: z = {pz[p]:+.3f}  (D={col_pairs(N,p)})")

    print("\n--- observed: column bigrams by width ------------------------------")
    for conv in ("pairs", "excess"):
        vals = {w: col_bigrams(V, w, conv) for w in range(2, 49)}
        bw = max(vals, key=lambda w: vals[w])
        print(f"  {conv:6s}: width 21 -> {vals[21]}; best width = {bw} -> {vals[bw]}")

    print("\n--- observed: repeated bigrams and their gaps ----------------------")
    c = Counter()
    pos = {}
    for i in range(N - 1):
        g = K4[i:i + 2]
        c[g] += 1
        pos.setdefault(g, []).append(i + 1)
    reps = {g: pos[g] for g in c if c[g] > 1}
    print(f"  {len(reps)} distinct repeated bigrams")
    gaps = []
    for g in sorted(reps, key=lambda g: pos[g][1] - pos[g][0]):
        p_ = reps[g]
        gaps.append(p_[1] - p_[0])
        print(f"    {g}  at {p_}  gap {p_[1]-p_[0]}")
    print(f"  gaps = {sorted(gaps)}  gcd = {math.gcd(*gaps)}")
    print(f"  count divisible by 2 = {sum(1 for g in gaps if g%2==0)}, "
          f"by 7 = {sum(1 for g in gaps if g%7==0)}")

    print("\n--- doubles mod 7 folklore -----------------------------------------")
    print(f"  double start positions (1-indexed): {d_pos}")
    print(f"  residues mod 7: {[p % 7 for p in d_pos]}")


if __name__ == "__main__":
    main()
