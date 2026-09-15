"""geo2 (d): what the number 97 could mean, tested explicitly.

97 is prime: 4 + 93 = 4 + 3*31 is the sculpture's own decomposition, and 93 = 3 x 31 is the
only way any part of K4 forms an exact rectangle.  Tested here:
  1. arithmetic facts and what primality rules out;
  2. a per-block key for the 4|31|31|31 blocks;
  3. a key of length 31 applied to the 93-letter BODY only (additive, all 12 pairings, and
     the general-alphabet version), plus the full body constraint table p = 2..93;
  4. the 3x31 body grid in all 8 orientations with period tests;
  5. 97 +/- 1: Sanborn's K2 ciphertext is known to be missing one carved letter.  If K4 were
     too, every position after the gap shifts by one.  Insert a wildcard at each of the 98
     slots (and delete each non-crib letter) and re-run the periodic test for p = 2..31.
     The s=0 insertion is exactly "the '?' before OBKR belongs to K4", which would make K4
     98 = 7 x 14 characters -- the one reading under which a 7-wide grid is exact.
"""
import math
from collections import Counter
from itertools import product
import geo2_common as G
import geometry_common as g

CT, CRIB, N = G.CT, G.CRIB, G.N
COMBOS = G.COMBOS
BODY = CT[4:]
BODYCRIB = {pos - 4: pt for pos, pt in CRIB.items()}
assert len(BODY) == 93 and len(BODYCRIB) == 24

print('=' * 78)
print('1. ARITHMETIC')
print('=' * 78)
for n in (93, 96, 97, 98, 869, 865):
    divs = [d for d in range(1, n + 1) if n % d == 0]
    print('  %3d : divisors %s' % (n, divs if len(divs) < 14 else str(divs[:7]) + '...'))
print('  97 is prime, so the ONLY exact rectangles for 97 letters are 1x97 and 97x1: no')
print('  columnar transposition of the whole of K4 has a full last row, and no square or')
print('  near-square grid exists.  Every 97-letter grid is ragged, which is why the')
print('  sculpture sets OBKR aside: 97 - 4 = 93 = 3 x 31 is exact, and 31 is the panel width.')
print('  98 = 2 x 7^2 = 7 x 14; 96 = 2^5 x 3.')

print('\n' + '=' * 78)
print('2. ONE KEY VALUE PER BLOCK (4 | 31 | 31 | 31)')
print('=' * 78)
blocks = {0: range(1, 5), 1: range(5, 36), 2: range(36, 67), 3: range(67, 98)}
for cmb in COMBOS[:4]:
    sh = g.crib_shifts(*cmb)
    line = []
    for b, rng_ in blocks.items():
        vals = {sh[p] for p in sh if p in rng_}
        line.append('block%d: %d cribs, %d distinct shifts' % (b, sum(1 for p in sh if p in rng_), len(vals)))
    print('  %-24s %s' % ('/'.join(cmb), ' ; '.join(line)))
print('  Block 1 alone contains 13 crib letters needing 11-13 distinct shift values in every')
print('  pairing, so a constant key per 31-letter block is impossible.  (Also covered by the')
print('  "block a*(i div m)+b" family in findings/geometry_1_out.txt, best fit 8/24.)')

print('\n' + '=' * 78)
print('3. A KEY OF LENGTH 31 ON THE 93-LETTER BODY')
print('=' * 78)
print('  body = CT[5..97] (1-indexed), 93 letters; the 24 cribs sit at body positions')
print('  %s' % sorted(BODYCRIB))
c31 = G.n_collisions(BODYCRIB, 31)
print('  period 31 on the body: the cribs occupy %d distinct residues, so c = %d constraint(s);'
      % (24 - c31, c31))
print('  chance of passing = 26^-%d = %.4f.' % (c31, 26.0 ** -c31))
for cmb in COMBOS:
    r = g.periodic_crib_test(BODY, BODYCRIB, 31, *cmb)
    print('    %-8s pt=%-7s ct=%-7s consistent=%-5s conflicts=%s'
          % (cmb + (r['consistent'], r['conflicts'])))
print('  The two constraints pair body positions 29/60 and 30/61, i.e. K4 33/64 (S->S and')
print('  N->B) and K4 34/65 (S->T and Y->E): the S and T that end NORTHEAST share 31-wide')
print('  columns with the B and E that begin BERLIN.  Both pairs conflict in all 12')
print('  pairings, so period 31 on the body is dead -- but on two constraints only')
print('  (chance 26^-2 = 0.0015), so this is suggestive rather than overwhelming alone.')
print('  The same test on the full 97 (findings/geometry_3_out.txt) has 2 constraints and')
print('  also fails in all 12 pairings.')

print('\n  full constraint table for the 93-letter body, p = 2..93:')
rows = []
for p in range(2, 94):
    c = G.n_collisions(BODYCRIB, p)
    cons = sum(1 for cmb in COMBOS if g.periodic_crib_test(BODY, BODYCRIB, p, *cmb)['consistent'])
    rows.append((p, c, cons))
for i in range(0, len(rows), 4):
    print('    ' + ' | '.join('p=%2d c=%2d cons=%2d' % r for r in rows[i:i + 4]))
bad = [(p, c, cons) for p, c, cons in rows if c > 0 and cons > 0]
print('  periods with >=1 constraint AND >=1 consistent pairing: %s' % (bad or 'NONE'))
exp = sum(12 * 26.0 ** -c for p, c, cons in rows if c > 0)
print('  expected consistent pairings by chance over all constrained periods: %.2f; observed %d'
      % (exp, sum(cons for p, c, cons in rows if c > 0)))

print('\n' + '=' * 78)
print('4. THE 3x31 BODY GRID IN ALL 8 ORIENTATIONS')
print('=' * 78)
cells = [(i // 31, i % 31, i) for i in range(93)]
orients = {}
for fr in (0, 1):
    for fc in (0, 1):
        for tr in (0, 1):
            nm = 'rows%s cols%s %s' % ('rev' if fr else 'fwd', 'rev' if fc else 'fwd',
                                       'transposed' if tr else 'as-is')
            key = (lambda r, c, fr=fr, fc=fc, tr=tr:
                   ((c if not fc else -c, r if not fr else -r) if tr
                    else (r if not fr else -r, c if not fc else -c)))
            orients[nm] = [o for r, c, o in sorted(cells, key=lambda t: key(t[0], t[1]))]
best = []
for nm, perm in orients.items():
    text, cribs = G.apply_perm(perm, BODY, BODYCRIB)
    for p in range(2, 32):
        c = G.n_collisions(cribs, p)
        for cmb in COMBOS:
            r = g.periodic_crib_test(text, cribs, p, *cmb)
            if r['consistent'] and c > 0:
                best.append((c, nm, p, cmb, r))
print('  8 orientations x periods 2..31 x 12 pairings = %d tests' % (8 * 30 * 12))
totexp = sum(12 * 26.0 ** -G.n_collisions(G.apply_perm(perm, BODY, BODYCRIB)[1], p)
             for perm in orients.values() for p in range(2, 32)
             if G.n_collisions(G.apply_perm(perm, BODY, BODYCRIB)[1], p) > 0)
print('  consistent cases with >=1 real constraint: observed %d, expected by chance %.2f'
      % (len(best), totexp))
for c, nm, p, cmb, r in sorted(best, key=lambda t: -t[0])[:12]:
    print('    c=%d p=%2d %-26s %-8s %-7s %-7s logp=%.3f words=%s'
          % (c, p, nm, cmb[0], cmb[1], cmb[2], g.unigram_logp(r['new_letters']),
             g.word_hits(r['new_letters'])))
    print('        ', r['decrypt'])

print('\n' + '=' * 78)
print('5. 97 +/- 1: A MISSING OR EXTRA CARVED LETTER')
print('=' * 78)
print('  K2\'s carved ciphertext is one letter short of its plaintext (Sanborn\'s error),')
print('  so the same could be true of K4.  Insert an unknown letter at slot s (0 = before')
print('  OBKR, which is where the "?" sits and would make K4 98 = 7 x 14 characters);')
print('  every crib at a position > s moves up by one.  Also delete each non-crib letter.')
print('  Only the crib POSITIONS matter for the consistency test, so the inserted letter')
print('  being unknown costs nothing.')
def shifted_cribs(s, delta):
    """delta=+1 insertion at slot s (0..97); delta=-1 deletion of 1-indexed position s."""
    out = {}
    for pos, pt in CRIB.items():
        if delta == 1:
            out[pos + 1 if pos > s else pos] = pt
        else:
            if pos == s:
                return None
            out[pos - 1 if pos > s else pos] = pt
    return out

def run_shift(cases, label):
    hits = []
    tests = 0
    expected = 0.0
    for tag, cribs, text in cases:
        for p in range(2, 32):
            c = len(cribs) - len({(q - 1) % p for q in cribs})
            if c == 0:
                continue
            expected += len(COMBOS) * 26.0 ** -c
            for cmb in COMBOS:
                tests += 1
                if g.periodic_crib_test(text, cribs, p, *cmb)['consistent']:
                    hits.append((c, tag, p, cmb))
    print('  %s: %d constrained tests, expected %.2f consistent by chance, observed %d'
          % (label, tests, expected, len(hits)))
    for h in sorted(hits, key=lambda t: -t[0])[:15]:
        print('     c=%2d p=%2d %-22s %s' % (h[0], h[2], h[1], '/'.join(h[3])))
    return hits

ins_cases = []
for s in range(0, 98):
    cr = shifted_cribs(s, 1)
    txt = CT[:s] + 'A' + CT[s:]          # the inserted letter is never a crib
    ins_cases.append(('insert@%d' % s, cr, txt))
run_shift(ins_cases, 'insertion at each of 98 slots, p=2..31')

del_cases = []
for s in range(1, 98):
    cr = shifted_cribs(s, -1)
    if cr is None:
        continue
    txt = CT[:s - 1] + CT[s:]
    del_cases.append(('delete@%d' % s, cr, txt))
run_shift(del_cases, 'deletion of each of the 73 non-crib letters, p=2..31')

print('\n  the special case s=0 ("?OBKR..." -> 98 letters, an exact 7x14 / 14x7 grid):')
cr0 = shifted_cribs(0, 1)
txt0 = '?' .replace('?', 'A') + CT
for p in (7, 14, 2, 49, 98):
    c = len(cr0) - len({(q - 1) % p for q in cr0})
    cons = [cmb for cmb in COMBOS if g.periodic_crib_test(txt0, cr0, p, *cmb)['consistent']]
    print('    p=%2d : %2d constraints, %d of 12 pairings consistent' % (p, c, len(cons)))
print('    and the two 7-wide column reads of the 98-cell grid:')
for tr, nm in ((0, '7 wide, 14 rows'), (1, '14 wide, 7 rows')):
    w = 7 if tr == 0 else 14
    cells98 = [(i // w, i % w, i) for i in range(98)]
    perm = [o for r, c, o in sorted(cells98, key=lambda t: (t[1], t[0]))]
    text, cribs = G.apply_perm(perm, txt0, cr0)
    found = []
    for p in range(2, 32):
        c = len(cribs) - len({(q - 1) % p for q in cribs})
        if c == 0:
            continue
        for cmb in COMBOS:
            if g.periodic_crib_test(text, cribs, p, *cmb)['consistent']:
                found.append((c, p, cmb))
    print('      %s, read down columns: consistent (c>0) cases = %s'
          % (nm, sorted(found, key=lambda t: -t[0])[:5] or 'none'))
