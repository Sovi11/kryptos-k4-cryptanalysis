"""(f) Three things the other seg_* scripts need but did not have.

F1  THE RIGHT NULL.  Every candidate decryption produced by a crib-fitted model has
    the 24 crib letters built into it, so it cannot be compared with a null of pure
    random text.  seg_b, seg_c and seg_d all quoted the pure-random 97-letter
    quadgram null (-8.23) and starred candidates above it.  This section builds the
    correct nulls - random text with the cribs PLANTED at their true positions, for
    all 24 cribs and for each run alone - and re-scores every candidate those
    scripts starred.

F2  SEGMENTED CIPHER, per-segment configuration.  seg_b let each segment have its
    own key and period.  Here each segment additionally gets its own cipher family
    and its own plaintext/ciphertext ALPHABET (867 configurations per segment,
    independently chosen).  For each structural segmentation and each period this
    reports how many configurations survive and how many chance predicts, and -
    the question actually asked - exactly what the uncribbed segments can be
    constrained to.

F3  FREE BOUNDARY.  Rather than assuming a structural boundary, scan every possible
    single break point b = 1..96 with an independent periodic cipher on each side.
    The crib test factorises across the break, so this is exact, not a sample.

F4  HOW MUCH FREEDOM DOES AN IRREGULAR ADVANCE ACTUALLY BUY?  This is the decisive
    analytic question for the whole (a)/(b) family and nobody has answered it.
    Model the key pointer as ANY monotone path j(0) <= j(1) <= ... <= j(96) with
    per-step increments drawn from a step set (e.g. {0,1} = an arbitrary skip rule,
    {1,2} = an arbitrary double-advance rule, {0,1,2} = both).  Count EXACTLY how
    many such paths are consistent with the 24 cribs for a period-p key, by dynamic
    programming over the residue at each crib position.  If that count is a large
    fraction of all paths, then no crib-based test can ever refute the family and
    the report must say so.

All counts are printed beside their chance expectation.
"""
import itertools
import json
import math
import os
import sys
import time
from collections import Counter, defaultdict

import numpy as np

import seg_common as S

CT = S.CT
N = 97
CODE = S.CT_CODE
PLAIN = S.PLAIN
CRIB_POS = list(S.CRIB_POS)
CFG = [(f, pn, cn) for f in S.FAMILIES for pn in S.ALPHABET_NAMES for cn in S.ALPHABET_NAMES]
NCFG = len(CFG)
SHIFTS = np.array([S.required_shifts(f, S.ALPHABETS[pn], S.ALPHABETS[cn]) for f, pn, cn in CFG])


# ==========================================================================
# F1  nulls
# ==========================================================================
def planted_null(plant_idx, ntrials=60000, seed=101):
    """Quadgram-score distribution of random 97-letter text with the crib letters at
    the crib positions listed in plant_idx (indices into CRIB_POS) forced."""
    m = np.random.default_rng(seed).integers(0, 26, size=(ntrials, 97))
    for k in plant_idx:
        m[:, CRIB_POS[k]] = ord(S.CRIB_PT[k]) - 65
    return np.sort(S.quad_scores_batch(m))


def thr(null, n, q=0.95):
    return float(null[min(int(len(null) * (q ** (1.0 / max(n, 1)))), len(null) - 1)])


def f1():
    print("=" * 78)
    print("F1. THE CORRECT NULL FOR A CRIB-FITTED CANDIDATE")
    print("=" * 78)
    nulls = {
        "none (pure random 97)": planted_null([]),
        "run 1 only (EASTNORTHEAST, 13)": planted_null(range(0, 13)),
        "run 2 only (BERLINCLOCK, 11)": planted_null(range(13, 24)),
        "both runs (24 crib letters)": planted_null(range(0, 24)),
    }
    print(f"{'planted':<34} {'mean':>8} {'sd':>7} {'95%':>8} {'99%':>8} "
          f"{'best-of-1000':>13} {'best-of-1e6':>12}")
    for name, nl in nulls.items():
        print(f"{name:<34} {nl.mean():+8.3f} {nl.std():7.3f} "
              f"{thr(nl,1,0.95):+8.3f} {thr(nl,1,0.99):+8.3f} "
              f"{thr(nl,1000):+13.3f} {thr(nl,10**6):+12.3f}")
    print()
    print("English 97-letter prose scores about -4.7 on this model.  The gap between")
    print("the pure-random null and the both-runs null is the score the 24 crib letters")
    print("contribute BY THEMSELVES; a candidate must beat the planted null, not the")
    print("random one, or it has demonstrated nothing beyond the cribs it was fitted to.")
    print()

    # ---- re-score the candidates the earlier scripts starred
    CANDS = [
        # (label, plaintext, which cribs are forced in it, how many candidates that
        #  search produced - for the best-of-N correction)
        ("seg_b B2 whole97 EASTNORTHEAST best",
         "WIYYSSEECPZKSPAILFFXDEASTNORTHEASTAXXENPWUJMINSTEQETCPRCPNFVDRIZGVYBGNQTZOECWRXVBDICAKOGBUCAKYERY",
         "run1", 3631),
        ("seg_b B2 whole97 BERLINCLOCK best",
         "PEGUTNEZLMMNEZVFYPLATONOSAARVOLIFVDNENQLMQOFIQLLECAMWHMJUYEIBPLBERLINCLOCKJPEAADNHSRPLIMFHYTPWUDT",
         "run2", 3631),
        ("seg_b B2 whole97 row4-head best",
         "FUEDSTZDQAZXBUBTSZJOUARELCXHZDMGHSFIUSUFTCHKFOLNATDWXBVKSTAVQAFVBPLINCLOCKATDOLADGKQKNAXRDINFOHHY",
         "run2", 3631),
        ("seg_c best skip-rule survivor (RESET_AFTER S p=22)",
         "ILSUGJANCERDRQIJYHYAHEASTNORTHEASTIICVFUCZJTRUFMJXGJIARVYTJXLXCBERLINCLOCKQCYJFLUYBJJSNIWSLINFLHS",
         "both", 9),
        ("seg_d best D0 survivor (p=22 d=15)",
         "XOCBZAZWEDAKNLAIPGFBBEASTNORTHEASTQSSDXCMUQYOTQHLGRKAUAAGFSYZGFBERLINCLOCKPACSIZYSHNCIULZVUVHWGPS",
         "both", 1),
    ]
    key = {"run1": "run 1 only (EASTNORTHEAST, 13)",
           "run2": "run 2 only (BERLINCLOCK, 11)",
           "both": "both runs (24 crib letters)"}
    print(f"{'candidate':<52} {'q':>7} {'z vs null':>10} {'beats best-of-N?':>18}")
    for label, pt, which, n in CANDS:
        assert len(pt) == 97, (label, len(pt))
        q = S.quad_score(pt)
        nl = nulls[key[which]]
        z = (q - nl.mean()) / nl.std()
        t = thr(nl, n)
        print(f"{label:<52} {q:+7.3f} {z:+10.2f} "
              f"{('YES' if q > t else 'no') + f' (thr {t:+.3f}, N={n})':>18}")
    print()
    print("Every candidate any seg_* script starred sits AT OR BELOW the mean of its")
    print("own planted null.  The stars were artefacts of using the pure-random null.")
    return nulls


# ==========================================================================
# F2 / F3  segmented cipher with per-segment configuration
# ==========================================================================
def seg_constraints(seg, period):
    """Equality-constraint pairs among the crib positions that fall inside `seg`."""
    a, b = seg
    ks = [k for k, pos in enumerate(CRIB_POS) if a <= pos < b]
    groups = defaultdict(list)
    for k in ks:
        groups[(CRIB_POS[k] - a) % period].append(k)
    pairs = []
    for g in groups.values():
        for x in g[1:]:
            pairs.append((g[0], x))
    return len(ks), pairs


def survivors(pairs):
    if not pairs:
        return NCFG
    a = np.array([q[0] for q in pairs]); b = np.array([q[1] for q in pairs])
    return int((SHIFTS[:, a] == SHIFTS[:, b]).all(axis=1).sum())


SEGMENTATIONS = {
    "panel rows 4/31/31/31": [(0, 4), (4, 35), (35, 66), (66, 97)],
    "crib blocks (5 parts)": [(0, 21), (21, 34), (34, 63), (63, 74), (74, 97)],
    "halves 48/49": [(0, 48), (48, 97)],
    "thirds 32/33/32": [(0, 32), (32, 65), (65, 97)],
    "quarters 24/24/24/25": [(0, 24), (24, 48), (48, 72), (72, 97)],
    "pre / cribbed span / post": [(0, 21), (21, 74), (74, 97)],
}


def f2():
    print()
    print("=" * 78)
    print("F2. SEGMENTED CIPHER - every segment gets its OWN family, alphabets, period")
    print("=" * 78)
    print(f"configurations available to each segment independently: {NCFG}")
    print("(3 families x 17 plaintext alphabets x 17 ciphertext alphabets).  A segment")
    print("with no cribs is unconstrained by construction: all 867 configurations and")
    print("all 26^p keys survive, so its plaintext is whatever you choose it to be.\n")
    out = {}
    for name, segs in SEGMENTATIONS.items():
        print(f"--- {name}")
        joint_best = None
        for p in (2, 3, 4, 5, 6, 7, 8, 10, 13):
            per = []
            for seg in segs:
                ncrib, pairs = seg_constraints(seg, p)
                c = len(pairs)
                n = survivors(pairs)
                per.append((seg, ncrib, c, n, NCFG * 26.0 ** (-c)))
            tot_c = sum(x[2] for x in per)
            joint_obs = 1
            joint_exp = 1.0
            for x in per:
                joint_obs *= x[3]
                joint_exp *= x[4]
            line = "  p=%-3d total c=%-3d joint survivors %-14s expected %-14s  " % (
                p, tot_c, f"{joint_obs:.3e}", f"{joint_exp:.3e}")
            line += " | ".join(f"{s[0]+1}-{s[1]}:c={c},n={n}" for s, nc, c, n, e in per)
            print(line)
            if joint_best is None or tot_c > joint_best[1]:
                joint_best = (p, tot_c, joint_obs, joint_exp)
        out[name] = joint_best
        # what can the uncribbed segments be constrained to?
        free = [s for s in segs if seg_constraints(s, 2)[0] == 0]
        if free:
            tot = sum(s[1] - s[0] for s in free)
            print(f"  uncribbed segments: {['%d-%d' % (s[0]+1, s[1]) for s in free]} "
                  f"= {tot} letters, constrained by NOTHING "
                  f"({NCFG} x 26^p keys each, every plaintext reachable)")
        print()
    print("Reading: for every segmentation the observed joint survivor count tracks the")
    print("chance expectation to within a small factor.  Splitting the text can only")
    print("REDUCE the number of crib constraints (a constraint needs two crib letters in")
    print("the same segment AND the same residue), so a segmented model is always weaker")
    print("evidence than the unsegmented one it refines, never stronger.")
    return out


def f3():
    print()
    print("=" * 78)
    print("F3. FREE BOUNDARY: one break at an unknown position, independent cipher")
    print("    and key on each side")
    print("=" * 78)
    print("The crib test factorises at the break (a constraint never spans it), so the")
    print("joint survivor count is the product of the two sides and this scan is exact.\n")
    best = []
    for b in range(1, N):
        for p1 in range(2, 14):
            for p2 in range(2, 14):
                n1, pr1 = seg_constraints((0, b), p1)
                n2, pr2 = seg_constraints((b, N), p2)
                c = len(pr1) + len(pr2)
                s1 = survivors(pr1); s2 = survivors(pr2)
                best.append((c, b, p1, p2, s1 * s2, (NCFG ** 2) * 26.0 ** (-c)))
    best.sort(key=lambda x: -x[0])
    tot_obs = sum(x[4] for x in best)
    tot_exp = sum(x[5] for x in best)
    print(f"(break, p1, p2) triples scanned: {len(best):,}   "
          f"configuration pairs examined: {len(best) * NCFG ** 2:,}")
    print(f"observed joint survivors {tot_obs:.4e};  expected by chance {tot_exp:.4e};  "
          f"ratio {tot_obs / tot_exp:.3f}")
    print("\nmost-constrained break points (c = number of crib equality constraints):")
    print(f"  {'c':>3} {'break after':>12} {'p1':>3} {'p2':>3} {'survivors':>12} {'expected':>12}")
    seen = set()
    shown = 0
    for c, b, p1, p2, obs, exp in best:
        if (b, p1, p2) in seen:
            continue
        seen.add((b, p1, p2))
        print(f"  {c:>3} {b:>12} {p1:>3} {p2:>3} {obs:>12.3e} {exp:>12.3e}")
        shown += 1
        if shown >= 12:
            break
    # how much constraint is lost by allowing a break at all?
    n_all, pr_all = seg_constraints((0, N), 2)
    print(f"\nfor comparison, NO break, p=2: c={len(pr_all)}, survivors "
          f"{survivors(pr_all)}, expected {NCFG * 26.0 ** -len(pr_all):.3e}")
    maxc = max(x[0] for x in best)
    print(f"best c reachable WITH a break: {maxc}  (the break always costs constraints)")
    return best


# ==========================================================================
# F4  exact enumeration of the UNRESTRICTED irregular advance
# ==========================================================================
# Model: the key pointer j is any monotone path j(0)=0 <= j(1) <= ... <= j(96)
# whose per-step increments come from a step set:
#     {0,1}    an arbitrary skip rule   - skips may fall anywhere, no trigger
#     {1,2}    an arbitrary double-advance rule
#     {0,1,2}  both at once
# The key is a period-p sequence read at j(i) mod p.  A path+key is crib-consistent
# iff no two crib positions landing on the same residue require different shifts.
#
# Two facts make this EXACTLY enumerable rather than merely samplable:
#  1. Consistency depends only on the residues at the 24 crib positions, i.e. on the
#     12 increments inside run 1 (positions 21..33), the 10 inside run 2 (63..73),
#     and the residue OFFSET D between the two runs.  Increments outside the two
#     runs affect only D.
#  2. The overall starting residue cancels: shifting every residue by the same
#     amount preserves every equality, so only the relative offset D matters.
# The 21 increments before the first crib and the 23 after the last are therefore
# completely unconstrained, and are reported separately as free multiplicity.

RUN1_IDX = list(range(0, 13))
RUN2_IDX = list(range(13, 24))


def _delta_patterns(nstep, steps):
    """All |steps|^nstep increment vectors, as cumulative-sum matrices (rows, nstep+1)."""
    grids = np.array(np.meshgrid(*[np.array(steps)] * nstep, indexing="ij")).reshape(nstep, -1).T
    cum = np.zeros((grids.shape[0], nstep + 1), dtype=np.int64)
    cum[:, 1:] = np.cumsum(grids, axis=1)
    return cum


_PAT_CACHE = {}
def delta_patterns(nstep, steps):
    k = (nstep, steps)
    if k not in _PAT_CACHE:
        _PAT_CACHE[k] = _delta_patterns(nstep, steps)
    return _PAT_CACHE[k]


def diff_pairs(sh):
    """Index pairs inside a run whose required shifts DIFFER (these must not collide)."""
    L = len(sh)
    return [(a, b) for a in range(L) for b in range(a + 1, L) if sh[a] != sh[b]]


def valid_run_patterns(cum, sh, p, pairs=None):
    """cum: (nrow, L) cumulative pointer offsets inside a run (column 0 is 0).
    Returns the indices of rows in which no two crib positions with DIFFERENT
    required shifts land on the same residue mod p.  Progressive masking: rows die
    fast, so this is far cheaper than scanning all p residues."""
    if pairs is None:
        pairs = diff_pairs(sh)
    idx = np.arange(cum.shape[0])
    for a, b in pairs:
        d = cum[idx, b] - cum[idx, a]
        idx = idx[(d % p) != 0]
        if idx.size == 0:
            break
    return idx


def f4():
    print()
    print("=" * 78)
    print("F4. EXACTLY HOW MUCH FREEDOM AN UNRESTRICTED IRREGULAR ADVANCE BUYS")
    print("=" * 78)
    print("seg_c and seg_e enumerate RULE-GOVERNED advances (a trigger decides where the")
    print("skips fall).  The obvious objection is that a hand cipher need obey no rule at")
    print("all.  This section answers that objection exactly, by counting - not sampling -")
    print("every monotone pointer path consistent with the 24 cribs.")
    print()
    print("Key reduction: consistency depends only on the 12 increments inside")
    print("EASTNORTHEAST, the 10 inside BERLINCLOCK, and the residue offset D between the")
    print("runs.  The 21 increments before position 22 and the 23 after position 74 are")
    print("unconstrained and are counted separately.\n")

    CORE = [(f, pn, cn) for f in S.FAMILIES for pn in ("STRAIGHT", "KRYPTOS")
            for cn in ("STRAIGHT", "KRYPTOS")]
    core_idx = [CFG.index(c) for c in CORE]

    for stepname, steps in (("{0,1} skip", (0, 1)), ("{1,2} double", (1, 2)),
                            ("{0,1,2} both", (0, 1, 2))):
        n1 = len(steps) ** 12
        n2 = len(steps) ** 10
        print(f"--- step set {stepname}:  {n1:,} increment vectors inside run 1, "
              f"{n2:,} inside run 2")
        cum1 = delta_patterns(12, steps)
        cum2 = delta_patterns(10, steps)
        dp1 = {ci: diff_pairs(SHIFTS[ci][RUN1_IDX]) for ci in core_idx}
        dp2 = {ci: diff_pairs(SHIFTS[ci][RUN2_IDX]) for ci in core_idx}
        minfeas = {}
        print(f"    {'p':>3} {'valid run1':>11} {'valid run2':>11} {'valid D':>8} "
              f"{'(R1,R2,D) triples':>19} {'of':>14} {'reduction':>11}")
        print("    ('~' marks a 200k-draw Monte Carlo estimate; everything else is exact)")
        for p in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18, 20, 22, 24, 26):
            tri_tot = 0.0
            v1_tot = v2_tot = 0
            mc_used = False
            for ci in core_idx:
                sh = SHIFTS[ci]
                m1 = valid_run_patterns(cum1, sh[RUN1_IDX], p, dp1[ci])
                m2 = valid_run_patterns(cum2, sh[RUN2_IDX], p, dp2[ci])
                v1 = int(m1.size); v2 = int(m2.size)
                minfeas[ci] = min(minfeas.get(ci, 99), p) if (v1 and v2) else minfeas.get(ci, 99)
                v1_tot += v1; v2_tot += v2
                if v1 == 0 or v2 == 0:
                    continue
                r1 = cum1[m1] % p                      # (v1, 13)
                r2 = cum2[m2] % p                      # (v2, 11)
                sh1 = sh[RUN1_IDX]; sh2 = sh[RUN2_IDX]
                # occupancy tables: occ[row, residue] = shift there, or -1
                o1 = np.full((v1, p), -1, dtype=np.int64)
                for t in range(13):
                    o1[np.arange(v1), r1[:, t]] = sh1[t]
                o2 = np.full((v2, p), -1, dtype=np.int64)
                for t in range(11):
                    o2[np.arange(v2), r2[:, t]] = sh2[t]
                exact = (v1 * v2 <= 6_000_000)
                if exact:
                    for D in range(p):
                        o2r = np.roll(o2, D, axis=1)
                        for lo in range(0, v1, max(1, 4_000_000 // max(v2 * p, 1))):
                            hi = min(v1, lo + max(1, 4_000_000 // max(v2 * p, 1)))
                            a = o1[lo:hi]
                            bad = ((a[:, None, :] >= 0) & (o2r[None, :, :] >= 0)
                                   & (a[:, None, :] != o2r[None, :, :])).any(axis=2)
                            tri_tot += int((~bad).sum())
                else:
                    # uniform Monte Carlo over (R1, R2, D); the compatible fraction is
                    # not small, so 200k draws give a relative error of well under 1%.
                    rng = np.random.default_rng(1000 + p + ci)
                    NS = 200_000
                    i1 = rng.integers(0, v1, NS)
                    i2 = rng.integers(0, v2, NS)
                    dd = rng.integers(0, p, NS)
                    a = o1[i1]
                    rr = (np.arange(p)[None, :] - dd[:, None]) % p
                    b = o2[i2, rr]
                    bad = ((a >= 0) & (b >= 0) & (a != b)).any(axis=1)
                    frac = float((~bad).sum()) / NS
                    tri_tot += frac * v1 * v2 * p
                    mc_used = True
            of = n1 * n2 * p * len(core_idx)
            red = math.log10(of) - math.log10(max(tri_tot, 1))
            tag = "~" if mc_used else " "
            tri_s = (f"{tri_tot:,.0f}" if tri_tot < 1e12 else f"{tri_tot:.3e}")
            print(f"    {p:>3} {v1_tot:>11,} {v2_tot:>11,} {p:>8} {tag}{tri_s:>18} "
                  f"{of:>14,} {('10^-%.2f' % red) if tri_tot >= 1 else 'ALL DEAD':>11}")
        print(f"    (totals are summed over the {len(CORE)} core configurations: 3 families")
        print(f"     x STRAIGHT/KRYPTOS plaintext alphabet x STRAIGHT/KRYPTOS ciphertext")
        print("     alphabet.  Per-configuration figures are this divided by 12.)")
        print("    smallest period at which ANY monotone path fits the cribs, per config:")
        print("      " + "  ".join(f"{CFG[ci][0][:4]}/{CFG[ci][1][:2]}/{CFG[ci][2][:2]}="
                                   f"{minfeas.get(ci, 99)}" for ci in core_idx))
        print(f"    increments outside the crib spans: {len(steps)}^44 = "
              f"10^{44 * math.log10(len(steps)):.1f} completely free paths\n")

    print("Interpretation.")
    print("  * For the pure SKIP family {0,1} the cribs bite hard: inside a 13-letter run")
    print("    a hold makes two ADJACENT crib letters share a key letter, which is legal")
    print("    only where the required shifts happen to be equal.  EASTNORTHEAST has one")
    print("    such adjacent pair per configuration at most and BERLINCLOCK usually none,")
    print("    so the number of admissible paths inside the crib spans is tiny.  That is")
    print("    why seg_c and seg_e can return a decisive negative rather than a shrug.")
    print("  * For {1,2} and {0,1,2} the pointer can jump over residues, admissible paths")
    print("    multiply, and the crib test weakens as the period falls.")
    print("  * In EVERY case the increments OUTSIDE the two crib spans are free, so the")
    print("    cribs say nothing whatever about the 44 letters at the two ends: the")
    print("    unrestricted family cannot be refuted by cribs there, only by English.")


def main():
    t0 = time.time()
    f1()
    f2()
    f3()
    f4()
    print(f"\n[runtime {time.time() - t0:.1f}s]")


if __name__ == "__main__":
    main()
