"""Task (a): crib VARIANTS at the stated positions.

Hypothesis under attack: the plaintext under 22-34 really is the 13 letters
EASTNORTHEAST and under 64-74 really is BERLINCLOCK, spelled correctly, with no
word separator.  Sanborn misspells on purpose (IQLUSION, UNDERGRUUND,
DESPARATLY), K2 uses X as a word separator, and journalists paraphrase.

For each variant pair that still occupies the stated window we re-run the
periodic-substitution consistency test for periods 2-26 over the 12
cipher/alphabet combos, plus the alphabet-FREE necessary condition that covers
every possible pair of 26-letter alphabets at once.

Run:  python3.12 crib_a_variants.py  > ../findings/crib_a_out.txt
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crib_lib as L
import twocipher_common as TC

POS_A = list(range(21, 34))      # 1-indexed 22-34, ct = FLRVQQPRNGKSS
POS_B = list(range(63, 74))      # 1-indexed 64-74, ct = NYPVTTMZFPK
LA, LB = len(POS_A), len(POS_B)

# --------------------------------------------------------------------------
# Variant cores
# --------------------------------------------------------------------------
CORES_A = [
    # baseline
    "EASTNORTHEAST",
    # X / Q word separators, in every position (K2 uses X between words)
    "EASTXNORTHEAST", "XEASTNORTHEAST", "EASTNORTHEASTX",
    "XEASTNORTHEASTX", "EASTXNORTHEASTX", "XEASTXNORTHEAST",
    "EASTXXNORTHEAST", "EASTQNORTHEAST", "XXEASTNORTHEAST",
    "EASTNORTHEASTXX", "XEASTXNORTHEASTX",
    # the same words inside a longer phrase
    "NORTHEASTERLY", "EASTNORTHEASTERLY", "NORTHEASTERN",
    "NORTHEASTBYEAST", "EASTBYNORTHEAST", "NORTHEASTQUADRANT",
    "NORTHEASTCORNER", "THENORTHEAST", "TOTHENORTHEAST",
    "LOOKNORTHEAST", "DUEEASTNORTHEAST", "NORTHEASTOF",
    "EASTNORTHEASTOF", "SETNORTHEAST", "GONORTHEAST",
    # Sanborn-style deliberate misspellings: doubled / dropped / swapped letters
    "EASTNORTHEEAST", "EASTNORTHEST", "EASTNORHTEAST", "EASTNORTHEASST",
    "EASTNORTHEASTT", "ESTNORTHEAST", "EASTNORTHEAS", "EASTNORTHESAT",
    "EASTNROTHEAST", "EAASTNORTHEAST", "EASTNORTHAEST", "EASTNORTTHEAST",
    "EASTNNORTHEAST", "EASTNORTHEASTE", "AESTNORTHEAST",
    # other compass strings of about the right length
    "EASTSOUTHEAST", "WESTNORTHWEST", "WESTSOUTHWEST", "NORTHEASTEAST",
    "NORTHNORTHEAST", "SOUTHSOUTHEAST", "NORTHEASTNORTH", "EASTNORTHNORTH",
    "NORTHEASTSOUTH",
    # German / non-English renderings
    "OSTNORDOST", "NORDOSTEN", "NORDNORDOST", "OSTNORDOSTEN",
]

CORES_B = [
    "BERLINCLOCK",
    "BERLINXCLOCK", "XBERLINCLOCK", "BERLINCLOCKX", "XBERLINXCLOCK",
    "BERLINXCLOCKX", "XBERLINCLOCKX", "BERLINQCLOCK", "XXBERLINCLOCK",
    "BERLINCLOCKXX",
    "THEBERLINCLOCK", "BERLINCLOCKS", "BERLINCLOCKED", "ATBERLINCLOCK",
    "THEBERLINCLOCKX", "SEEBERLINCLOCK", "BERLINCLOCKAT",
    "OSTBERLINCLOCK", "EASTBERLINCLOCK", "WESTBERLINCLOCK",
    # Sanborn-style misspellings
    "BERLINCLOKC", "BERLINCLOC", "BERLINCLOCC", "BERLINNCLOCK",
    "BERLINCLLOCK", "BERLENCLOCK", "BERLINCOCK", "BERLINCLOCKK",
    "BERLLINCLOCK", "BERILNCLOCK", "BREILNCLOCK", "BERLINCLCOK",
    # the real German names of the Berlin Clock, and near neighbours
    "BERLINUHR", "DIEBERLINUHR", "MENGENLEHREUHR", "WELTZEITUHR",
    "URANIAWELTZEITUHR", "BERLINERUHR", "BERLINWALL", "BERLINWALLX",
    "CLOCKBERLIN", "BERLINGATE", "BERLINCLOCKIS",
]


def build_variants():
    vA, lA = L.window_variants(CORES_A, LA, min_known=8)
    vB, lB = L.window_variants(CORES_B, LB, min_known=7)
    return (vA, lA), (vB, lB)


def single_subs(word):
    """All single-letter substitutions of `word` (one deliberate misspelling)."""
    out = []
    for i in range(len(word)):
        for ch in L.A2Z:
            if ch != word[i]:
                out.append(word[:i] + ch + word[i + 1:])
    return out


def report(tag, res, vA, lA, vB, lB, show=20):
    print("\n### %s" % tag)
    print("  variant pairs              : %d  (A=%d, B=%d)"
          % (res["n_pairs"], len(vA), len(vB)))
    print("  (pair, period, combo) tests: %d" % res["tested"])
    print("  survivors observed %d   vs chance expectation %.4g"
          % (res["observed"], res["expected"]))
    print("  alphabet-free necessary condition: %d / %d (pair, period) pairs pass "
          "(%.2f%%) -- failing it rules the pair out for EVERY pair of 26-letter "
          "alphabets, not just the 12 combos"
          % (res["universal_pass"], res["uni_tested"],
             100.0 * res["universal_pass"] / max(1, res["uni_tested"])))
    cs = sorted(set(res["obs"]) | set(res["exp"]), reverse=True)
    print("  by number of constraints c (a random key survives with prob 26^-c):")
    print("    %-4s %14s %14s %14s" % ("c", "tests", "expected", "observed"))
    tot_t = 0
    for c in cs:
        e = res["exp"].get(c, 0.0)
        o = res["obs"].get(c, 0)
        t = int(round(e * 26.0 ** c)) if e else 0
        tot_t += t
        if o or c >= 5:
            print("    %-4d %14d %14.4g %14d" % (c, t, e, o))
    print("    (strata with c < 5 and no survivors omitted; a genuine solution "
          "would appear at large c)")
    if not res["details"]:
        print("  no survivor with c >= 5.")
        return
    rows = []
    for d in res["details"]:
        period, combo, iA, iB, kd = d["period"], d["combo"], d["iA"], d["iB"], d["key"]
        key = [kd.get(r) for r in range(period)]
        if all(k is not None for k in key):
            pt = L.decrypt(L.CT, key, *combo)
            q, w = TC.quadgram_score(pt), TC.word_coverage(pt)
        else:
            pt, q, w = None, float("nan"), float("nan")
        rows.append((d["c"], period, combo, vA[iA], vB[iB], lA[iA], lB[iB], pt, q, w))
    rows.sort(key=lambda r: (-r[0], r[1]))
    print("  survivors with c >= 5, most constrained first (%d shown of %d kept):"
          % (min(show, len(rows)), len(rows)))
    for c, period, combo, sa, sb, la, lb, pt, q, w in rows[:show]:
        print("    c=%-2d p=%-2d %-28s A=%s (%s)  B=%s (%s)"
              % (c, period, L.combo_name(combo), sa, la, sb, lb))
        if pt:
            print("        decrypt q=%.2f wordcov=%.2f  %s" % (q, w, pt))


def main():
    print("=" * 78)
    print("TASK (a)  CRIB VARIANTS AT THE STATED POSITIONS")
    print("=" * 78)
    print("window A: 1-indexed 22-34 (13 letters), ct = %s"
          % "".join(L.CT[p] for p in POS_A))
    print("window B: 1-indexed 64-74 (11 letters), ct = %s"
          % "".join(L.CT[p] for p in POS_B))
    print("periods 2-26, 12 cipher/alphabet combos "
          "(3 rules x pt in {plain,KRYPTOS} x ct in {plain,KRYPTOS}).")
    print("The key alphabet is irrelevant to a consistency test, so these 12")
    print("combos cover Quagmire I-IV restricted to those two alphabets.")

    # --- 0. baseline, for calibration
    res = L.two_window_sweep(POS_A, ["EASTNORTHEAST"], POS_B, ["BERLINCLOCK"])
    report("0. BASELINE (control): EASTNORTHEAST / BERLINCLOCK",
           res, ["EASTNORTHEAST"], ["exact"], ["BERLINCLOCK"], ["exact"])

    # --- 1. the big variant cross-product
    (vA, lA), (vB, lB) = build_variants()
    res = L.two_window_sweep(POS_A, vA, POS_B, vB)
    report("1. FULL VARIANT CROSS-PRODUCT (separators, longer phrases, "
           "Sanborn-style misspellings, German renderings, partial cribs)",
           res, vA, lA, vB, lB)

    # --- 2. exactly one deliberate misspelling, window A
    subA = ["EASTNORTHEAST"] + single_subs("EASTNORTHEAST")
    res = L.two_window_sweep(POS_A, subA, POS_B, ["BERLINCLOCK"])
    report("2. ONE substituted letter in EASTNORTHEAST (325 mutants + original), "
           "BERLINCLOCK fixed", res, subA, ["sub"] * len(subA),
           ["BERLINCLOCK"], ["exact"])

    # --- 3. exactly one deliberate misspelling, window B
    subB = ["BERLINCLOCK"] + single_subs("BERLINCLOCK")
    res = L.two_window_sweep(POS_A, ["EASTNORTHEAST"], POS_B, subB)
    report("3. ONE substituted letter in BERLINCLOCK (275 mutants + original), "
           "EASTNORTHEAST fixed", res, ["EASTNORTHEAST"], ["exact"],
           subB, ["sub"] * len(subB))

    # --- 4. one misspelling in EACH window simultaneously
    res = L.two_window_sweep(POS_A, subA, POS_B, subB)
    report("4. ONE substituted letter in EACH window (326 x 276)",
           res, subA, ["sub"] * len(subA), subB, ["sub"] * len(subB))

    # --- 5. only the sub-cribs Sanborn released separately
    #     (NORTHEAST alone, BERLIN alone, CLOCK alone, EAST alone)
    partA = ["????NORTHEAST", "EAST?????????", "EASTNORTHEAST"]
    partB = ["BERLIN?????", "??????CLOCK", "BERLINCLOCK"]
    res = L.two_window_sweep(POS_A, partA, POS_B, partB)
    report("5. PARTIAL cribs only (each released word on its own)",
           res, partA, ["partial"] * 3, partB, ["partial"] * 3)


if __name__ == "__main__":
    main()
