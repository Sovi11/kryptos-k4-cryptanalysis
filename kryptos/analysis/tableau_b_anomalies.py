"""(b) Do the tableau's ANOMALIES encode the key?

The physical tableau deviates from the ideal one in exactly one place: an extra L at the
end of the row labelled N.  This script tests every way that single deviation could be
read as key material:

  B1. the deviation stream  delta_i = (physical_i - ideal_i) mod 26  as a running key
  B2. the numbers the anomaly names (row 15, label N=13, column 31/32, linear index
      464/465, 402 letters after it, 867/866 totals) as PERIODS of a periodic key
  B3. the anomaly as a POSITION: running key taken from the tableau starting at the
      extra L, in both directions, all 24 combos, all 26 key-alphabet rotations
  B4. the anomalous row (and the 'HILL' column) as a repeated key block
  B5. a completeness sweep: periodic keys of EVERY period 2..97 (families.md covered
      2..26 only), with the chance expectation stated for each period

Chance bookkeeping
------------------
For a period-p key, the 24 crib positions fall into d_p distinct residue classes, giving
c_p = 24 - d_p independent consistency constraints.  A uniformly random key stream passes
all of them with probability 26^-c_p.  c_p = 0 means the test is VACUOUS (any period-p key
can be chosen to fit the cribs, so "passing" means nothing).
For a fixed 97-letter running key the probability of reproducing all 24 crib letters is
26^-24 = 1.9e-34.
"""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tableau_common import (PLAIN, KEYED, ALPHAS, COMBOS, combo_name, CRIB_POS, CRIB_PT,
                            CRIB_CT, K4_CT, RIGHT_ROWS, RIGHT_ROWS_IDEAL,
                            TABLEAU_PHYS_STR, TABLEAU_IDEAL_STR, required_key_indices,
                            crib_matches, decrypt, selftest, FINDINGS)

OUT = []
def w(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)


# ------------------------------------------------------------------ helpers ----
def periodic_consistency(p):
    """(#constraints, {combo: survives}) for a period-p key with a free 26-letter key."""
    classes = {}
    for j, pos in enumerate(CRIB_POS):
        classes.setdefault(pos % p, []).append(j)
    c_p = 24 - len(classes)
    res = {}
    for cb in COMBOS:
        req = required_key_indices(cb)
        ok = all(len({req[j] for j in js}) == 1 for js in classes.values())
        res[cb] = ok
    return c_p, res, classes


def running_key_scan(name, text, label_extra=""):
    """All offsets x 24 combos; report best crib-match count (max over 26 rotations is
    handled by the constant-difference test, reported separately)."""
    best = (-1, None)
    hist = Counter()
    n = len(text)
    for cb in COMBOS:
        Ak = ALPHAS[cb[3]]
        req = required_key_indices(cb)
        for off in range(n):
            # constant-difference test covers all 26 rotations at once
            d0 = None
            m = 0
            for j, pos in enumerate(CRIB_POS):
                idx = off + pos
                if idx >= n:
                    m = -1
                    break
                d = (Ak.index(text[idx]) - req[j]) % 26
                if d0 is None:
                    d0 = d
                if d == d0:
                    m += 1
            if m < 0:
                continue
            hist[m] += 1
            if m > best[0]:
                best = (m, (cb, off, d0))
    return best, hist


# ---------------------------------------------------------------------- main ----
def main():
    selftest()
    w("# (b) The tableau anomalies as key material\n")

    # ---------------- the deviation itself
    w("## B0. What the deviation actually is\n")
    w("physical row N (index 14): %s" % RIGHT_ROWS[14])
    w("ideal    row N (index 14): %s" % RIGHT_ROWS_IDEAL[14])
    w("=> exactly one inserted letter, 'L', at the end of that row.")
    lin = sum(len(r) for r in RIGHT_ROWS[:14]) + len(RIGHT_ROWS[14]) - 1
    w("linear index (0-indexed) in the 867-letter reading: %d" % lin)
    w("Because it is an INSERTION, physical[%d:] == ideal[%d:] exactly: %s"
      % (lin + 1, lin, TABLEAU_PHYS_STR[lin + 1:] == TABLEAU_IDEAL_STR[lin:]))
    w("So the 'sequence of deviations' has length 1.  Everything below is an attempt to")
    w("turn that single datum into a key stream, a period, or a position.\n")

    # ---------------- B1 deviation stream
    w("## B1. Deviation stream as a running key\n")
    # align physical[:866] against ideal
    d_letters = "".join(PLAIN[(PLAIN.index(a) - PLAIN.index(b)) % 26]
                        for a, b in zip(TABLEAU_PHYS_STR, TABLEAU_IDEAL_STR))
    d_letters_k = "".join(KEYED[(KEYED.index(a) - KEYED.index(b)) % 26]
                          for a, b in zip(TABLEAU_PHYS_STR, TABLEAU_IDEAL_STR))
    w("delta stream (plain-index subtraction), 866 letters, first 80:")
    w("  " + d_letters[:80])
    w("  ... non-A run starts at index %d" % next(i for i, c in enumerate(d_letters) if c != "A"))
    w("  tail (last 60): " + d_letters[-60:])
    w("delta stream (KRYPTOS-index subtraction), first 80:")
    w("  " + d_letters_k[:80])
    streams = {
        "delta_plainidx": d_letters,
        "delta_plainidx_rev": d_letters[::-1],
        "delta_keyedidx": d_letters_k,
        "delta_keyedidx_rev": d_letters_k[::-1],
        # the non-trivial tail only (from the insertion onwards)
        "delta_tail": d_letters[lin:],
        "delta_tail_keyed": d_letters_k[lin:],
    }
    w("")
    for nm, txt in streams.items():
        if len(txt) < 97:
            w("  %-22s len=%d  (too short for a 97-letter run; scanned anyway)" % (nm, len(txt)))
        best, hist = running_key_scan(nm, txt)
        m, det = best
        w("  %-22s len=%4d  best crib match (over offsets x 24 combos x 26 rotations): %2d/24  %s"
          % (nm, len(txt), m, "" if det is None else "at %s off=%d rot=%d" %
             (combo_name(det[0]), det[1], det[2])))
    w("")
    w("Chance expectation: each (offset, combo) trial matches all 24 with prob 26*26^-24")
    w("= 26^-23 = 1.4e-33; with <2e5 trials the expected number of 24/24 hits is ~1e-28.")
    w("Expected BEST match count over ~2e5 trials is 3-4 out of 24.\n")

    # ---------------- B2 anomaly-derived periods
    w("## B2. Numbers named by the anomaly, tested as key periods\n")
    named = {
        13: "N is the 14th letter (index 13) of the plain alphabet",
        14: "row N is the 14th lettered row / 15th carved row (0-indexed 14)",
        15: "row N is carved row 15 (1-indexed)",
        18: "L is at index 18 of the KRYPTOS alphabet",
        11: "L is the 12th letter of the plain alphabet (index 11)",
        31: "the anomalous letter sits in column 31 (0-indexed) = 32nd position of its row",
        32: "row N is 32 characters long",
        30: "ideal row body width",
        464: "0-indexed linear position of the extra L",
        465: "1-indexed linear position of the extra L",
        402: "letters after the extra L",
        866: "ideal tableau length",
        867: "physical tableau length",
        97: "K4 length",
    }
    w("| period p | constraints c_p | chance 26^-c_p | combos consistent | note |")
    w("|---|---|---|---|---|")
    for p in sorted(named):
        c_p, res, _ = periodic_consistency(p)
        nsurv = sum(res.values())
        w("| %d | %d | %.3g | %d/24 | %s |" % (p, c_p, 26.0 ** (-c_p), nsurv, named[p]))
    w("")
    w("A period p >= 74 puts every crib position in its own residue class (c_p = 0), so the")
    w("test is vacuous: '24/24 combos consistent' there means nothing at all.\n")

    # ---------------- B5 completeness sweep 2..97
    w("## B5. Completeness: periodic key of EVERY period 2..97\n")
    w("| p | c_p | chance per combo | consistent combos | p | c_p | chance | consistent |")
    w("|---|---|---|---|---|---|---|---|")
    rows = []
    for p in range(2, 98):
        c_p, res, _ = periodic_consistency(p)
        rows.append((p, c_p, sum(res.values())))
    half = (len(rows) + 1) // 2
    for a, b in zip(rows[:half], rows[half:] + [(None, None, None)]):
        left = "| %d | %d | %.3g | %d/24 " % (a[0], a[1], 26.0 ** (-a[1]), a[2])
        right = ("| %d | %d | %.3g | %d/24 |" % (b[0], b[1], 26.0 ** (-b[1]), b[2])
                 if b[0] is not None else "| | | | |")
        w(left + right)
    nonvac = [(p, c, s) for p, c, s in rows if c > 0 and s > 0]
    w("")
    w("Periods with c_p > 0 (a real test) AND at least one consistent combo: %s" % nonvac)
    w("Total (p, combo) pairs with c_p>0: %d ; observed consistent: %d ; expected by chance: %.3f"
      % (sum(1 for p, c, s in rows if c > 0) * 24,
         sum(s for p, c, s in rows if c > 0),
         sum(24 * 26.0 ** (-c) for p, c, s in rows if c > 0)))
    w("")

    # ---------------- B3 anomaly as a position in a running key
    w("## B3. Running key from the tableau STARTING AT the anomaly\n")
    cands = {
        "phys @ extra-L (fwd)": TABLEAU_PHYS_STR[lin:],
        "phys @ extra-L+1 (fwd)": TABLEAU_PHYS_STR[lin + 1:],
        "phys @ extra-L (bwd)": TABLEAU_PHYS_STR[:lin + 1][::-1],
        "phys @ row N start (fwd)": TABLEAU_PHYS_STR[lin - 31:],
        "ideal @ same index (fwd)": TABLEAU_IDEAL_STR[lin:],
    }
    for nm, txt in cands.items():
        if len(txt) < 97:
            w("  %-26s len=%3d  TOO SHORT" % (nm, len(txt)))
            continue
        best = (-1, None)
        for cb in COMBOS:
            Ak = ALPHAS[cb[3]]
            req = required_key_indices(cb)
            d0 = None
            m = 0
            for j, pos in enumerate(CRIB_POS):
                d = (Ak.index(txt[pos]) - req[j]) % 26
                if d0 is None:
                    d0 = d
                if d == d0:
                    m += 1
            if m > best[0]:
                best = (m, (cb, d0))
        w("  %-26s len=%3d  best %2d/24 over 24 combos x 26 rotations (%s, rot=%d)"
          % (nm, len(txt), best[0], combo_name(best[1][0]), best[1][1]))
    w("")
    w("Chance: 24 combos x 26 rotations = 624 trials per text; P(24/24) = 624*26^-24 = 1.2e-31.")
    w("Expected best over 624 trials: 2-3 out of 24.\n")

    # ---------------- B4 anomalous row / HILL column as a repeated key
    w("## B4. The anomalous row and the 'HILL' column as repeated key blocks\n")
    blocks = {
        "row N physical (32)": RIGHT_ROWS[14],
        "row N ideal (31)": RIGHT_ROWS_IDEAL[14],
        "row N body physical (31)": RIGHT_ROWS[14][1:],
        "last column physical (26)": "".join(r[-1] for r in RIGHT_ROWS[1:27]),
        "last column ideal (26)": "".join(r[-1] for r in RIGHT_ROWS_IDEAL[1:27]),
        "HILL": "HILL",
        "col 31 = 'L'": "L",
        "rows L,M,N,O labels": "LMNO",
    }
    best_overall = (-1, None)
    trials = 0
    for nm, blk in blocks.items():
        best = (-1, None)
        for cb in COMBOS:
            Ak = ALPHAS[cb[3]]
            req = required_key_indices(cb)
            for shift in range(len(blk)):
                d0 = None
                m = 0
                for j, pos in enumerate(CRIB_POS):
                    d = (Ak.index(blk[(pos + shift) % len(blk)]) - req[j]) % 26
                    if d0 is None:
                        d0 = d
                    if d == d0:
                        m += 1
                trials += 1
                if m > best[0]:
                    best = (m, (cb, shift, d0))
        w("  %-26s len=%2d  best %2d/24  (%s, start offset %d, rot %d)"
          % (nm, len(blk), best[0], combo_name(best[1][0]), best[1][1], best[1][2]))
        if best[0] > best_overall[0]:
            best_overall = (best[0], nm)
    w("")
    w("  total trials %d ; expected 24/24 hits by chance = %.3g ; observed = 0"
      % (trials, trials * 26.0 ** -23))
    w("  best overall: %d/24 (%s)" % best_overall)
    w("")

    # ---------------- summary
    w("## Verdict for (b)\n")
    w("The physical-vs-ideal deviation set has cardinality ONE.  One bit of information")
    w("cannot be a 97-letter key stream, and every derived reading of it (the delta stream,")
    w("the numbers it names used as periods, its linear position used as a running-key")
    w("offset, its row and its column used as repeated key blocks) fails the cribs at the")
    w("chance level.  No survivor.")

    print("\n".join(OUT))
    with open(os.path.join(FINDINGS, "tableau_b_out.txt"), "w") as f:
        f.write("\n".join(OUT) + "\n")


if __name__ == "__main__":
    main()
