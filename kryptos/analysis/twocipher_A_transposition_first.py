"""(A) Transposition BEFORE substitution:  plaintext -> transposed -> periodic sub -> ct.

Under this order the crib letters (as quoted by Sanborn at ciphertext positions
22-34 and 64-74) are in the *same* positions in the transposed text, so a periodic
substitution must be consistent with the cribs exactly as positioned.  This is the
same test as the prior single-cipher work; we re-run it here for completeness,
with the four alphabet arrangements and both Vigenere- and Beaufort-type keying,
and we also record for every period the *minimum* number of violated constraints
(how close it comes) and the period at which the test first becomes vacuous.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import twocipher_common as C

def min_violations(pairs, period, family, PA, CA):
    """Number of crib pairs that disagree with the majority shift in their column."""
    from collections import defaultdict, Counter
    cols = defaultdict(list)
    for pos, ct, pt in pairs:
        cols[pos % period].append(C.shift_for(family, PA, CA, pt, ct))
    v = 0
    for col, shifts in cols.items():
        v += len(shifts) - Counter(shifts).most_common(1)[0][1]
    return v

def main():
    print("(A) cribs as positioned (0-indexed):", C.CRIBS)
    surv = C.run_periodic_battery(C.CRIBS, periods=range(2, 27))
    print(f"Periods 2-26 x {len(C.FAMILIES)} families x {len(C.ALPHABET_SETS)} alphabet sets: "
          f"{len(surv)} consistent configurations")
    for s in surv:
        print("  SURVIVOR", s)
    # Closeness table
    print("\nMinimum violated constraints per period (best over families/alphabets); "
          "'checks' = non-trivial constraints available at that period:")
    for period in range(2, 50):
        best = None
        for fam in C.FAMILIES:
            for aname, (PA, CA) in C.ALPHABET_SETS.items():
                v = min_violations(C.CRIBS, period, fam, PA, CA)
                ok, key, checks = C.periodic_consistency(C.CRIBS, period, fam, PA, CA)
                if best is None or v < best[0]:
                    best = (v, fam, aname)
        # number of non-trivial checks is independent of family/alphabet
        cols = {}
        checks = 0
        for pos, ct, pt in C.CRIBS:
            if pos % period in cols: checks += 1
            cols[pos % period] = 1
        print(f"  p={period:2d}  checks={checks:2d}  min_violations={best[0]:2d}  ({best[1]}, {best[2]})")
    # First vacuous period
    for period in range(2, 98):
        cols = set(); checks = 0
        for pos, ct, pt in C.CRIBS:
            if pos % period in cols: checks += 1
            cols.add(pos % period)
        if checks == 0:
            print(f"\nTest becomes vacuous (no two crib letters share a column) at period {period}.")
            break

if __name__ == "__main__":
    main()
