"""(B2, exhaustive) Family-independent test of "substitution then transposition"
under the contiguity reading.

If the crib words are contiguous, in order, in the plaintext (hence in the
intermediate text), then whatever the transposition T is, the only thing that
matters for a periodic substitution of period p is the set of *relative offsets*
between the crib blocks in the intermediate text, mod p.  So instead of
enumerating transpositions we enumerate offsets:

  strong reading : two blocks, EASTNORTHEAST (13) and BERLINCLOCK (11); one free
                   offset d (mod p) = start(BERLINCLOCK) - start(EASTNORTHEAST).
  4-word reading : four blocks EAST, NORTHEAST, BERLIN, CLOCK; three free offsets
                   (mod p), each relative to the start of EAST.

For every period 2..26, family (vig/beau), alphabet arrangement, and every offset
tuple we run the consistency test and record the number of non-trivial checks.
Whether a "consistent" offset tuple is meaningful is judged by the number of
checks it survived (each is a 1-in-26 event under the null) and by the total
number of offset tuples tried.  A survivor here would then have to be realised by
some transposition; a non-survivor rules out *every* transposition of that
reading at that period.

Note the blocks may not overlap in the intermediate text, but since only offsets
mod p matter and p <= 26 while the blocks are 13/11 (or 4/9/6/5) long, we do not
impose non-overlap (the offsets mod p are what the test sees; the actual offsets
can always be chosen large enough), except that we do require the 4 words to be
placeable without overlap, which is always possible within 97 letters.
"""
import sys, os, itertools, json
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import twocipher_common as C

WORDS = [(ctw, ptw) for _, ctw, ptw, _ in C.CRIB_WORDS]   # EAST, NORTHEAST, BERLIN, CLOCK

def pairs_for(blocks, starts):
    """blocks: list of (ct, pt) strings, starts: list of start positions."""
    out = []
    for (ctw, ptw), s in zip(blocks, starts):
        for k in range(len(ctw)):
            out.append((s + k, ctw[k], ptw[k]))
    return out

def run(blocks, free, label):
    """free = number of free offsets (len(blocks) - 1).  First block at position 0
    (absolute alignment mod p is a key rotation and irrelevant).  We place block i at
    offset d_i + BIG*i so that offsets mod p are exactly d_i while blocks never overlap."""
    BIG = 26 * 30
    results = []   # (p, fam, aname, offsets, checks)
    tried = 0
    per_period = {}
    for p in range(2, 27):
        n_cons = 0; best = 0; cons_list = []
        for ds in itertools.product(range(p), repeat=free):
            starts = [0] + [BIG * (i + 1) * 0 + (ds[i] + 40 * (i + 1) * p) for i in range(free)]
            # starts[i] mod p == ds[i-1]; 40*(i+1)*p spacing keeps blocks apart
            pairs = pairs_for(blocks, starts)
            for fam in C.FAMILIES:
                for aname, (PA, CA) in C.ALPHABET_SETS.items():
                    tried += 1
                    ok, key, checks = C.periodic_consistency(pairs, p, fam, PA, CA)
                    if ok:
                        n_cons += 1
                        best = max(best, checks)
                        cons_list.append((fam, aname, ds, checks, key))
        per_period[p] = (n_cons, best, cons_list)
    print(f"\n=== {label}: {len(blocks)} blocks, {free} free offset(s); {tried} (period,offsets,family,alphabet) tests ===")
    print("  p   #offset-tuples  consistent  max_checks  [checks histogram of consistent]")
    for p in range(2, 27):
        n_cons, best, cl = per_period[p]
        hist = defaultdict(int)
        for _, _, _, ch, _ in cl: hist[ch] += 1
        print(f"  {p:2d}   {p**free:6d} x8      {n_cons:6d}     {best:2d}        {dict(sorted(hist.items()))}")
    # Expected number of consistent under the null for comparison, per period:
    # each (offsets,fam,alph) with k checks survives w.p. 26^-k.  Compute k for each
    # offsets tuple (independent of fam/alph) and sum.
    print("\n  Null comparison (sum over offset tuples x 8 of 26^-checks):")
    for p in range(2, 27):
        exp = 0.0
        for ds in itertools.product(range(p), repeat=free):
            starts = [0] + [ds[i] + 40 * (i + 1) * p for i in range(free)]
            pairs = pairs_for(blocks, starts)
            cols = set(); checks = 0
            for pos, _, _ in pairs:
                if pos % p in cols: checks += 1
                cols.add(pos % p)
            exp += 8 * 26.0 ** (-checks)
        n_cons = per_period[p][0]
        flag = "  <-- more than expected" if n_cons > 3 * exp + 3 else ""
        print(f"  p={p:2d}: observed {n_cons:6d}  null-expected {exp:9.1f}{flag}")
    # Detail: survivors with the most checks
    allc = [(p,) + tuple(x) for p in range(2, 27) for x in per_period[p][2]]
    allc.sort(key=lambda r: -r[4])
    print(f"\n  Strongest survivors (most checks) for {label}:")
    for r in allc[:15]:
        p, fam, aname, ds, checks, key = r
        print(f"    p={p:2d} {fam:4s} {aname:28s} offsets={ds} checks={checks}")
    return per_period

def main():
    strong = run([("FLRVQQPRNGKSS", "EASTNORTHEAST"), ("NYPVTTMZFPK", "BERLINCLOCK")], 1, "STRONG reading (2 blocks)")
    four = run(WORDS, 3, "4-WORD reading (EAST / NORTHEAST / BERLIN / CLOCK)")
    # Save
    out = {"strong": {p: [(fam, an, list(ds), ch) for fam, an, ds, ch, _ in v[2]] for p, v in strong.items()},
           "four": {p: [(fam, an, list(ds), ch) for fam, an, ds, ch, _ in v[2] if ch >= 3] for p, v in four.items()}}
    with open(os.path.join(C.HERE, "twocipher_B2_offsets_results.json"), "w") as f:
        json.dump(out, f)

if __name__ == "__main__":
    main()
