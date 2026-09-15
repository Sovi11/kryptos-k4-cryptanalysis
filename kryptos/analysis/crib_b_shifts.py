"""Tasks (b) and (c): the cribs may not sit where everyone assumes.

(b) slide each crib block by -3..+3 independently (and much further), re-run the
    periodic-substitution consistency test, and report any (shift, period,
    combo) that becomes consistent together with the chance expectation given
    the extra freedom.
(c) the special case where Sanborn's 1-indexed positions are counted over the
    panel *including* the '?' that ends K3, i.e. everything shifts by one.

Motivation: contemporaneous articles paraphrase Sanborn's position statements
differently, and the 2006 K2 correction was exactly a one-letter shift caused by
a carving error.  If a single omitted or doubled letter exists in the carved K4
the same way, the crib offsets would be off by one.

Run:  python3.12 crib_b_shifts.py > ../findings/crib_b_out.txt
"""
import itertools
import os
import sys
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crib_lib as L
import twocipher_common as TC

PERIODS = tuple(range(2, 27))
BLOCKS = [("EAST", 21), ("NORTHEAST", 25), ("BERLIN", 63), ("CLOCK", 69)]


# --------------------------------------------------------------------------
def validate():
    """Plant a periodic cipher whose cribs sit at SHIFTED positions and check
    the placement sweep recovers exactly that shift."""
    print("## validation: planted shifted cribs")
    ca = L.build_combo_arrays(L.alphabet_set("two"))
    allok = True
    for period, ci, shift in ((9, 3, +2), (12, 7, -3), (7, 0, +1)):
        rng = np.random.default_rng(100 + period)
        rule, pta, cta = L.COMBOS[ci % 12]
        key = rng.integers(0, 26, period).tolist()
        pt = "".join(L.A2Z[i] for i in rng.integers(0, 26, 97))
        ct = L.encrypt(pt, key, rule, pta, cta)
        saved = L.CT_CODE.copy()
        L.CT_CODE[:] = np.frombuffer(ct.encode(), dtype=np.uint8).astype(np.int64) - 65
        # cribs taken from the planted plaintext at the SHIFTED window
        blocks = [(21 + shift, pt[21 + shift:25 + shift]),
                  (25 + shift, pt[25 + shift:34 + shift]),
                  (63 + shift, pt[63 + shift:69 + shift]),
                  (69 + shift, pt[69 + shift:74 + shift])]
        found_at = []
        for d in (-3, -2, -1, 0, 1, 2, 3):
            pl = L.merge_blocks([(s - shift + d, w) for s, w in blocks])
            if pl is None:
                continue
            sv, _ = L.placement_sweep_one(pl, ca, periods=(period,))
            if sv:
                found_at.append(d)
        L.CT_CODE[:] = saved
        ok = found_at == [shift]
        allok &= ok
        print("   planted shift %+d, period %2d, %-28s -> sweep fires at %s  [%s]"
              % (shift, period, L.combo_name((rule, pta, cta)), found_at,
                 "PASS" if ok else "FAIL"))
    print("   validation: %s\n" % ("ALL PASS" if allok else "FAILURES"))
    return allok


# --------------------------------------------------------------------------
def run(tag, placements, labels, combo_arrays, periods=PERIODS, detail_min=8,
        show=25, note=""):
    """placements: list of placement lists (or None for rejected)."""
    nK = len(combo_arrays[4])
    obs = Counter()
    exp = Counter()
    uni_pass = Counter()
    uni_tot = 0
    details = []
    n_used = 0
    for pl, lab in zip(placements, labels):
        if pl is None:
            continue
        n_used += 1
        sv, info = L.placement_sweep_one(pl, combo_arrays, periods)
        for period, c, uni in info:
            exp[c] += nK * 26.0 ** (-c)
            uni_tot += 1
            if uni:
                uni_pass[c] += 1
        for period, ki, c, kd in sv:
            obs[c] += 1
            if c >= detail_min:
                details.append((c, period, ki, lab, kd, pl))
    print("\n### %s" % tag)
    if note:
        print("  %s" % note)
    print("  placements tested          : %d (of %d proposed; the rest overlap "
          "inconsistently or run off the 97 letters)" % (n_used, len(placements)))
    print("  combos                     : %d   periods: %d" % (nK, len(periods)))
    print("  (placement, period, combo) tests: %d" % (n_used * len(periods) * nK))
    print("  survivors observed %d   vs chance expectation %.4g"
          % (sum(obs.values()), sum(exp.values())))
    print("  alphabet-free necessary condition passes for %d / %d "
          "(placement, period) pairs (%.1f%%)"
          % (sum(uni_pass.values()), uni_tot,
             100.0 * sum(uni_pass.values()) / max(1, uni_tot)))
    print("  by number of constraints c:")
    print("    %-4s %12s %14s %10s %14s" % ("c", "tests", "expected", "observed",
                                            "univ-pass"))
    for c in sorted(set(exp) | set(obs), reverse=True):
        e = exp.get(c, 0.0)
        o = obs.get(c, 0)
        t = int(round(e * 26.0 ** c)) if e else 0
        if o or c >= 6:
            print("    %-4d %12d %14.4g %10d %14d"
                  % (c, t, e, o, uni_pass.get(c, 0)))
    if not details:
        print("  no survivor with c >= %d." % detail_min)
        return
    details.sort(key=lambda r: -r[0])
    print("  survivors with c >= %d (%d of them):" % (detail_min, len(details)))
    for c, period, ki, lab, kd, pl in details[:show]:
        rule, pta, cta = _combo_from_label(combo_arrays[4][ki])
        key = [kd.get(r) for r in range(period)]
        line = "    c=%-2d p=%-2d %-34s %s" % (c, period, combo_arrays[4][ki], lab)
        print(line)
        if all(k is not None for k in key):
            pt = L.decrypt(L.CT, key, rule, pta, cta)
            print("        decrypt q=%.2f wordcov=%.2f  %s"
                  % (TC.quadgram_score(pt), TC.word_coverage(pt), pt))


_ALPH_CACHE = {}


def _combo_from_label(label):
    rule, pt, ct = label.split("/")
    return rule, pt[3:], ct[3:]


# make decrypt() accept keyword-alphabet names
_orig_alphabets = dict(L.ALPHABETS)
for _kw in L.SHORT_KEYWORDS:
    L.ALPHABETS[_kw] = L.keyed_alphabet(_kw)


# --------------------------------------------------------------------------
def main():
    ok = validate()
    ca2 = L.build_combo_arrays(L.alphabet_set("two"))       # 12 combos
    ca17 = L.build_combo_arrays(L.alphabet_set("short17"))  # 3*17*17 = 867 combos

    print("=" * 78)
    print("TASKS (b) AND (c)  SHIFTED CRIB PLACEMENTS")
    print("=" * 78)
    print("K4 = %s" % L.CT)
    print("baseline blocks (0-indexed starts): EAST@21 NORTHEAST@25 BERLIN@63 CLOCK@69")

    # ---- B0 control
    run("B0. CONTROL: baseline placement, 12 combos",
        [L.merge_blocks([(s, w) for w, s in BLOCKS])], ["shift 0"], ca2)

    # ---- (c) the off-by-one hypothesis, in full detail
    print("\n### C. THE OFF-BY-ONE HYPOTHESIS (task c)")
    print("  If Sanborn's 1-indexed positions are counted over the panel row")
    print("  INCLUDING the '?' that ends K3, every crib sits one letter EARLIER")
    print("  in K4 than assumed (delta = -1).  The opposite convention (a dropped")
    print("  carved letter, as in the 2006 K2 correction) gives delta = +1.")
    for delta in (-1, +1):
        pl = L.merge_blocks([(s + delta, w) for w, s in BLOCKS])
        print("\n  delta = %+d  ->  %s" % (delta, "".join(
            "%d:%s->%s " % (p + 1, L.CT[p], c) for p, c in pl)))
        sv, info = L.placement_sweep_one(pl, ca2, PERIODS)
        e = sum(len(ca2[4]) * 26.0 ** (-c) for _, c, _ in info)
        print("    12 combos x 25 periods: %d survivors (chance expectation %.3f)"
              % (len(sv), e))
        print("    periods where the alphabet-free condition still permits a "
              "solution: %s" % [p for p, c, u in info if u])
        sv17, info17 = L.placement_sweep_one(pl, ca17, PERIODS)
        e17 = sum(len(ca17[4]) * 26.0 ** (-c) for _, c, _ in info17)
        print("    867 combos (3 rules x 17 x 17 keyed alphabets) x 25 periods: "
              "%d survivors (chance expectation %.3f)" % (len(sv17), e17))
        for period, ki, c, kd in sv17:
            print("        c=%-2d p=%-2d %s" % (c, period, ca17[4][ki]))

    # ---- B1 global slide over the whole ciphertext
    deltas = list(range(-21, 24))
    pls, labs = [], []
    for d in deltas:
        pls.append(L.merge_blocks([(s + d, w) for w, s in BLOCKS]))
        labs.append("global delta=%+d" % d)
    run("B1. GLOBAL SLIDE of the whole crib pattern, delta = -21..+23, 12 combos",
        pls, labs, ca2,
        note="relative spacing of the four words preserved; delta=-1 and +1 are "
             "the task-(c) hypotheses")
    run("B1e. same 45 global slides, 867 keyed-alphabet combos", pls, labs, ca17)

    # ---- B2 two blocks independently, -3..+3 (the literal task-(b) request)
    pls, labs = [], []
    for dA, dB in itertools.product(range(-3, 4), repeat=2):
        pls.append(L.merge_blocks([(21 + dA, "EASTNORTHEAST"),
                                   (63 + dB, "BERLINCLOCK")]))
        labs.append("EASTNORTHEAST%+d / BERLINCLOCK%+d" % (dA, dB))
    run("B2. TWO blocks slid independently by -3..+3 (49 placements), 12 combos",
        pls, labs, ca2)
    run("B2e. same 49 placements, 867 keyed-alphabet combos", pls, labs, ca17)

    # ---- B3 four blocks independently, -3..+3  (2401 placements)
    pls, labs = [], []
    for ds in itertools.product(range(-3, 4), repeat=4):
        blocks = [(s + d, w) for (w, s), d in zip(BLOCKS, ds)]
        pls.append(L.merge_blocks(blocks))
        labs.append("EAST%+d NORTHEAST%+d BERLIN%+d CLOCK%+d" % ds)
    run("B3. FOUR blocks slid independently by -3..+3 (2401 placements), 12 combos",
        pls, labs, ca2,
        note="overlapping blocks that disagree on a letter are rejected")

    # ---- B4 completely free slide of the two phrases
    pls, labs = [], []
    for a in range(0, 97 - 13 + 1):
        for b in range(0, 97 - 11 + 1):
            pls.append(L.merge_blocks([(a, "EASTNORTHEAST"), (b, "BERLINCLOCK")]))
            labs.append("EASTNORTHEAST@%d / BERLINCLOCK@%d" % (a + 1, b + 1))
    run("B4. FREE slide: EASTNORTHEAST anywhere x BERLINCLOCK anywhere "
        "(85 x 87 placements), 12 combos", pls, labs, ca2,
        note="this is the complete 'where could the two phrases possibly be?' "
             "sweep, a strict superset of (b) and (c)")


if __name__ == "__main__":
    main()
