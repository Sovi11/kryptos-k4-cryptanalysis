#!/usr/bin/env python3
"""(e) Kasiski: every repeated n-gram, its positions, its gaps, and whether the
gap factors carry any signal once multiple testing is paid for.

Includes a POSITIVE CONTROL: the same code is run on K2, whose key ABSCISSA has
period 8, so a working Kasiski test must find factor 8 there.  If it does not,
the negative on K4 means nothing.

Also calibrates the one geometric anomaly in the literature -- Richard Bean's
"excess repeated column bigrams when K4 is written at width 21" -- including the
multiple-testing correction over widths that has never been applied to it.

    python3 analysis/stat_e_kasiski.py
"""
import math
import os
import random
from collections import Counter
from multiprocessing import Pool

import stat_common as S

TRIALS = 500_000
SEED = 20260913
NPROC = min(8, os.cpu_count() or 4)
WMIN, WMAX = 2, 48


# ---------------------------------------------------------------- helpers ---
def repeated_ngrams(text, n):
    seen = {}
    for i in range(len(text) - n + 1):
        seen.setdefault(text[i:i + n], []).append(i)
    return {g: p for g, p in seen.items() if len(p) > 1}


def n_repeat_pairs(text, n):
    """Number of unordered position pairs sharing an n-gram."""
    c = Counter(text[i:i + n] for i in range(len(text) - n + 1))
    return sum(v * (v - 1) // 2 for v in c.values())


def column_bigram_repeats(b, w):
    """Repeated vertical bigrams when the text is written in rows of width w:
    the pairs (x_i, x_{i+w}).  Returns the number of repeated position-pairs."""
    n = len(b)
    if n - w < 2:
        return 0
    c = Counter((b[i], b[i + w]) for i in range(n - w))
    return sum(v * (v - 1) // 2 for v in c.values())


def column_bigram_excess(b, w):
    """The OTHER natural convention for the same observation: excess
    occurrences, sum(v - 1), rather than unordered pairs, sum(v(v-1)/2).

    The two agree on K4 (no vertical bigram occurs three times at w = 21) but
    NOT in the tail of the null, because a triple contributes 2 to one and 3 to
    the other.  Bean's published figure uses the excess convention.  Reporting
    both is the point: the nominal significance of the width-21 observation
    moves by a factor of ~5 depending on a choice nobody states."""
    n = len(b)
    if n - w < 2:
        return 0
    c = Counter((b[i], b[i + w]) for i in range(n - w))
    return sum(v - 1 for v in c.values() if v > 1)


def gaps_of(rep):
    out = []
    for g, pos in sorted(rep.items()):
        for a in range(len(pos)):
            for bb in range(a + 1, len(pos)):
                out.append((g, pos[a] + 1, pos[bb] + 1, pos[bb] - pos[a]))
    return out


def factor_table(gaps, fmax=48):
    return {f: sum(1 for g in gaps if g % f == 0) for f in range(2, fmax + 1)}


# ---------------------------------------------------------------- workers ---
def _chunk(args):
    seed, trials, n, mode, multiset = args
    rng = random.Random(seed)
    if mode == "uniform":
        pool = S.LetterPool(seed)
        gen = lambda: pool.take(n)
    else:
        chars = list(multiset)
        def gen():
            rng.shuffle(chars)
            return bytes(chars)
    bi, tri, quad = Counter(), Counter(), Counter()
    colmax = Counter()
    col21 = Counter()
    facmax = Counter()
    colmax_ex = Counter()
    col21_ex = Counter()
    joint = Counter()
    for _ in range(trials):
        b = gen()
        bi[n_repeat_pairs(b, 2)] += 1
        tri[n_repeat_pairs(b, 3)] += 1
        quad[n_repeat_pairs(b, 4)] += 1
        best = 0
        best_ex = 0
        for w in range(WMIN, WMAX + 1):
            c = Counter((b[i], b[i + w]) for i in range(n - w)) if n - w >= 2 else Counter()
            v = sum(x * (x - 1) // 2 for x in c.values())
            vx = sum(x - 1 for x in c.values() if x > 1)
            if v > best:
                best = v
            if vx > best_ex:
                best_ex = vx
            if w == 21:
                col21[v] += 1
                col21_ex[vx] += 1
        colmax[best] += 1
        colmax_ex[best_ex] += 1
        # Kasiski factor concentration: of the repeated-bigram gaps, the largest
        # number sharing any single factor 2..24
        rep = {}
        for i in range(n - 1):
            rep.setdefault(b[i:i + 2], []).append(i)
        gg = [p[j] - p[i] for p in rep.values() if len(p) > 1
              for i in range(len(p)) for j in range(i + 1, len(p))]
        bf = 0
        for f in range(2, 25):
            cnt = sum(1 for g in gg if g % f == 0)
            if cnt > bf:
                bf = cnt
        facmax[bf] += 1
        # joint (number of gaps, best factor count): the unconditional facmax
        # tail partly re-measures the gap COUNT, since a text with more gaps can
        # pile more of them onto one factor.  Conditioning separates the two.
        joint[(len(gg), bf)] += 1
    return bi, tri, quad, colmax, col21, facmax, colmax_ex, col21_ex, joint


NSTAT = 9


def run_null(n, mode, multiset, trials, seed):
    per = trials // NPROC
    args = [(seed + 7919 * i, per, n, mode, multiset) for i in range(NPROC)]
    with Pool(NPROC) as pl:
        parts = pl.map(_chunk, args)
    out = [Counter() for _ in range(NSTAT)]
    for part in parts:
        for k in range(NSTAT):
            out[k].update(part[k])
    return out, per * NPROC


def tail(counter, x, total):
    return sum(v for k, v in counter.items() if k >= x) / total


def mean_of(counter, total):
    return sum(k * v for k, v in counter.items()) / total


# ------------------------------------------------------------------- main ---
def main():
    print("=" * 78)
    print("(e) KASISKI -- repeated n-grams, gaps, factors")
    print("=" * 78)

    ct = S.K4
    n = 97

    print("\n--- 1. Every repeated n-gram in K4 (1-indexed positions) ------------")
    total_pairs = 0
    for k in range(2, 8):
        rep = repeated_ngrams(ct, k)
        if not rep:
            print(f"  {k}-grams: NONE repeated  "
                  f"(expected pairs under uniform random: "
                  f"{math.comb(n - k + 1, 2) / 26 ** k:.4f})")
            continue
        gg = gaps_of(rep)
        total_pairs += len(gg)
        print(f"  {k}-grams: {len(rep)} distinct repeated, {len(gg)} position pairs "
              f"(expected {math.comb(n - k + 1, 2) / 26 ** k:.3f})")
        for g, a, bb, d in gg:
            print(f"      {g:<6s} at {a:3d} and {bb:3d}   gap {d:3d}   "
                  f"factors {sorted(f for f in range(2, 49) if d % f == 0)}")

    rep2 = repeated_ngrams(ct, 2)
    gaps = [d for _, _, _, d in gaps_of(rep2)]
    print(f"\n  the 10 bigram gaps: {sorted(gaps)}")
    print(f"  gcd of all gaps = {math.gcd(*gaps)}")

    print("\n--- 2. Kasiski factor table for K4 ----------------------------------")
    ft = factor_table(gaps)
    print(f"  {len(gaps)} gaps.  A period-p cipher would pile the gaps onto multiples of p.")
    print(f"  {'factor':>7s} {'gaps divisible':>15s} {'expected':>9s} {'ratio':>7s}")
    for f in range(2, 25):
        exp = len(gaps) / f
        print(f"  {f:7d} {ft[f]:15d} {exp:9.2f} {ft[f]/exp if exp else 0:7.2f}")
    best_f = max(range(2, 25), key=lambda f: ft[f] - len(gaps) / f)
    print(f"\n  best factor by excess: {best_f} ({ft[best_f]} of {len(gaps)} gaps, "
          f"{len(gaps)/best_f:.2f} expected)")

    print("\n--- 3. POSITIVE CONTROL: the same test on K1, K2, K3 ----------------")
    print("K1 key PALIMPSEST (period 10), K2 key ABSCISSA (period 8), K3 transposition.")
    for name, t, truep in (("K1", S.K1_CT, 10), ("K2", S.K2_CT, 8),
                           ("K3", S.K3_CT, None), ("K4", S.K4_CT, None)):
        r = repeated_ngrams(t, 3)
        g3 = [d for _, _, _, d in gaps_of(r)]
        r2 = repeated_ngrams(t, 2)
        g2 = [d for _, _, _, d in gaps_of(r2)]
        if g3:
            ft3 = factor_table(g3, 26)
            bf = max(range(2, 27), key=lambda f: (ft3[f] - len(g3) / f))
            note = (f"trigram gaps {len(g3)}; best factor {bf} "
                    f"({ft3[bf]}/{len(g3)}, exp {len(g3)/bf:.1f})")
            if truep:
                note += f"; factor {truep} takes {ft3[truep]}/{len(g3)}"
        else:
            note = f"no repeated trigrams ({len(g2)} bigram gaps)"
        print(f"  {name} (n={len(t):3d}): {note}")
    print("\n  K2 is the demonstration that the method works: its true period 8 shows up")
    print("  in the trigram gaps.  K4 has NO repeated trigram at all, so Kasiski on K4")
    print("  has nothing to work with -- which is itself the finding.")

    print("\n--- 4. Null distributions --------------------------------------------")
    print(f"{TRIALS:,} replicates, two nulls.")
    obs_bi = n_repeat_pairs(ct, 2)
    obs_tri = n_repeat_pairs(ct, 3)
    obs_quad = n_repeat_pairs(ct, 4)
    obs_col21 = column_bigram_repeats(S.K4_B, 21)
    obs_colmax = max(column_bigram_repeats(S.K4_B, w) for w in range(WMIN, WMAX + 1))
    obs_colbest = max(range(WMIN, WMAX + 1),
                      key=lambda w: column_bigram_repeats(S.K4_B, w))
    obs_facmax = max(sum(1 for g in gaps if g % f == 0) for f in range(2, 25))
    obs_col21_ex = column_bigram_excess(S.K4_B, 21)
    obs_colmax_ex = max(column_bigram_excess(S.K4_B, w) for w in range(WMIN, WMAX + 1))

    for mode, label in (("uniform", "uniform random 97 letters"),
                        ("shuffle", "random permutation of K4's own letters")):
        (bi, tri, quad, colmax, col21, facmax, colmax_ex, col21_ex,
         joint), tot = run_null(
            n, mode, S.K4_B, TRIALS, SEED + (0 if mode == "uniform" else 99))
        print(f"\n  null = {label}  ({tot:,} replicates)")
        print(f"  {'statistic':44s} {'obs':>5s} {'null mean':>10s} {'P(>=obs)':>10s}")
        print(f"  {'repeated bigram pairs':44s} {obs_bi:5d} "
              f"{mean_of(bi, tot):10.3f} {tail(bi, obs_bi, tot):10.5f}")
        print(f"  {'repeated trigram pairs':44s} {obs_tri:5d} "
              f"{mean_of(tri, tot):10.3f} {tail(tri, obs_tri, tot):10.5f}"
              f"   [P(=0) = {tri.get(0,0)/tot:.4f}]")
        print(f"  {'repeated 4-gram pairs':44s} {obs_quad:5d} "
              f"{mean_of(quad, tot):10.3f} {tail(quad, obs_quad, tot):10.5f}")
        print(f"  {'col-bigram PAIRS  at width 21':44s} {obs_col21:5d} "
              f"{mean_of(col21, tot):10.3f} {tail(col21, obs_col21, tot):10.5f}")
        print(f"  {'col-bigram EXCESS at width 21 (Bean)':44s} {obs_col21_ex:5d} "
              f"{mean_of(col21_ex, tot):10.3f} {tail(col21_ex, obs_col21_ex, tot):10.5f}")
        print(f"  {f'MAX col-bigram PAIRS  over widths 2..48':44s} {obs_colmax:5d} "
              f"{mean_of(colmax, tot):10.3f} {tail(colmax, obs_colmax, tot):10.5f}"
              f"   <-- multiple-testing-corrected")
        print(f"  {f'MAX col-bigram EXCESS over widths 2..48':44s} {obs_colmax_ex:5d} "
              f"{mean_of(colmax_ex, tot):10.3f} {tail(colmax_ex, obs_colmax_ex, tot):10.5f}"
              f"   <-- multiple-testing-corrected")
        print(f"  {'max bigram-gaps sharing one factor 2..24':44s} {obs_facmax:5d} "
              f"{mean_of(facmax, tot):10.3f} {tail(facmax, obs_facmax, tot):10.5f}")
        cond_n = sum(v for (g, f), v in joint.items() if g == len(gaps))
        cond_h = sum(v for (g, f), v in joint.items()
                     if g == len(gaps) and f >= obs_facmax)
        print(f"  {f'   ... CONDITIONAL on exactly {len(gaps)} gaps':44s} {obs_facmax:5d} "
              f"{'':>10s} {cond_h / cond_n if cond_n else float('nan'):10.5f}"
              f"   [{cond_n:,} of {tot:,} replicates had {len(gaps)} gaps]")

    print(f"\n  (K4's best width for column bigrams is {obs_colbest}, with {obs_colmax}.)")
    print("\n  READING, in two parts.")
    print("  (i) CONVENTION.  K4 scores 11 under BOTH conventions, because no vertical")
    print("      bigram occurs three times at width 21.  The NULLS differ: a triple")
    print("      contributes 3 to the pairs count but only 2 to the excess count, so the")
    print("      pairs statistic has the heavier upper tail.  Bean's published ~1/6750")
    print("      is the excess convention; this repo's earlier prior_art_bean_stats.py")
    print("      measured 1/3226 for it.  The pairs convention gives ~1/650 on the same")
    print("      null.  Same observation, same data, a factor of ~5 in nominal")
    print("      significance, decided by an unstated choice.")
    print("  (ii) SELECTION.  Width 21 was chosen from among all plausible widths. Once")
    print("      the MAXIMUM over widths 2..48 is scored against its own null, the")
    print("      effect is what scanning 47 widths always produces. It is the strongest")
    print("      single anomaly in K4 and it does not survive its own correction under")
    print("      either convention.")

    print("\n--- 5. Column-bigram repeats, every width ---------------------------")
    print(f"  {'w':>3s} {'pairs':>6s} {'repeats':>8s} {'expected':>9s}   |  "
          f"{'w':>3s} {'pairs':>6s} {'repeats':>8s} {'expected':>9s}")
    rows = []
    for w in range(WMIN, WMAX + 1):
        m = n - w
        rows.append((w, m, column_bigram_repeats(S.K4_B, w),
                     math.comb(m, 2) / 676 if m >= 2 else 0.0))
    half = (len(rows) + 1) // 2
    for i in range(half):
        a = rows[i]
        line = f"  {a[0]:3d} {a[1]:6d} {a[2]:8d} {a[3]:9.2f}"
        if i + half < len(rows):
            c = rows[i + half]
            line += f"   |  {c[0]:3d} {c[1]:6d} {c[2]:8d} {c[3]:9.2f}"
        print(line)


if __name__ == "__main__":
    main()
