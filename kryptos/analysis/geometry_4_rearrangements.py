"""Part 4: rearrangements of the 97 letters.

Each rearrangement is a permutation; cribs travel with their letters.  For each we run
(a) the periodic IoC for p=2..30 and (b) the periodic-key crib-consistency test for
p=2..48 under all 12 cipher/alphabet pairings.  Rearrangements: identity, odd/even
interleave (both split texts and both concatenations), column-major reads of a w-wide grid
(w=2..48, every offset, four reading directions).  97 is prime so the only exact rectangle
is 1x97 / 97x1 (identity).
"""
import geometry_common as g
from collections import Counter

CT, CRIB = g.CT, g.CRIB
N = 97
combos = [(c, pa, ca) for c in g.CIPHERS for pa, ca in g.ALPHA_PAIRS]

def apply(perm):
    """perm[j] = original 0-indexed position of new position j.
    perm may be a proper subset of range(97) (e.g. odd positions only); cribs whose
    original letter is not present are dropped, the rest are renumbered."""
    text = ''.join(CT[i] for i in perm)
    inv = {orig: j for j, orig in enumerate(perm)}
    cribs = {inv[pos - 1] + 1: pt for pos, pt in CRIB.items() if (pos - 1) in inv}
    return text, cribs

rearr = {}
rearr['identity'] = list(range(N))
rearr['odd positions only'] = list(range(0, N, 2))
rearr['even positions only'] = list(range(1, N, 2))
for w in range(2, 49):
    for off in range(w):
        cells = [(divmod(i + off, w), i) for i in range(N)]   # ((row, col), orig)
        for name, keyf in (('down,L->R', lambda rc: (rc[1], rc[0])),
                           ('up,L->R', lambda rc: (rc[1], -rc[0])),
                           ('down,R->L', lambda rc: (-rc[1], rc[0])),
                           ('up,R->L', lambda rc: (-rc[1], -rc[0]))):
            order = [orig for rc, orig in sorted(cells, key=lambda t: keyf(t[0]))]
            rearr['colread w=%d off=%d %s' % (w, off, name)] = order
print('rearrangements:', len(rearr))

# (a) periodic IoC
ioc_rows = []
for name, perm in rearr.items():
    text, cribs = apply(perm)
    vals = [(p, g.periodic_ioc(text, p)) for p in range(2, 31)]
    pmax, vmax = max(vals, key=lambda t: t[1])
    ioc_rows.append((vmax, pmax, name))
ioc_rows.sort(reverse=True)
allmax = [r[0] for r in ioc_rows]
print('\n== periodic IoC, max over p=2..30, for every rearrangement ==')
print('  distribution of the per-rearrangement maxima: mean %.4f, 95th pct %.4f, max %.4f'
      % (sum(allmax) / len(allmax), sorted(allmax)[int(0.95 * len(allmax))], max(allmax)))
print('  identity:', [r for r in ioc_rows if r[2] == 'identity'][0])
print('  top 12:')
for r in ioc_rows[:12]:
    print('    max IoC %.4f at p=%2d  %s' % r)
print('  full-period table for identity, odd, even:')
for nm in ('identity', 'odd positions only', 'even positions only'):
    text, _ = apply(rearr[nm])
    print('    %-20s' % nm, ' '.join('%d:%.3f' % (p, g.periodic_ioc(text, p)) for p in range(2, 31)))

# (b) crib consistency
print('\n== periodic-key crib consistency, p=2..48, all 12 cipher/alphabet pairings ==')
hits = []
total = 0
for name, perm in rearr.items():
    text, cribs = apply(perm)
    for p in range(2, 49):
        for cmb in combos:
            r = g.periodic_crib_test(text, cribs, p, *cmb)
            total += 1
            if r['consistent'] and r['collisions'] >= 1:
                hits.append((r['collisions'], name, p, cmb, r))
print('  tests run:', total)
byc = Counter(h[0] for h in hits)
print('  consistent cases by number of collisions:', dict(sorted(byc.items())))
print('  chance expectation (tests * 26^-c, ignoring how many tests have c collisions) is an upper bound;')
print('  the following lists every consistent case with >= 4 collisions:')
strong = sorted([h for h in hits if h[0] >= 4], key=lambda h: (-h[0], h[1]))
for c, name, p, cmb, r in strong:
    lp = g.unigram_logp(r['new_letters'])
    print('   coll=%d p=%2d %-8s %-7s %-7s %-32s known=%2d logp=%.3f words=%s' % (c, p, *cmb, name, r['n_known'], lp, g.word_hits(r['new_letters'])))
    print('        ', r['decrypt'])
if not strong:
    print('   none')
# Also the 2-way split texts alone for every period
print('\n== odd/even split texts: consistency detail ==')
for nm in ('odd positions only', 'even positions only'):
    text, cribs = apply(rearr[nm])
    print('  %s: %s  (%d cribs survive) cribs at %s' % (nm, text, len(cribs), sorted(cribs)))
    for p in range(2, 25):
        cons = [cmb for cmb in combos if g.periodic_crib_test(text, cribs, p, *cmb)['consistent']]
        ncol = g.periodic_crib_test(text, cribs, p, 'vig', 'plain', 'plain')['collisions']
        print('    p=%2d collisions=%2d consistent pairings=%d %s' % (p, ncol, len(cons), ['%s/%s/%s' % c for c in cons] if 0 < len(cons) < 12 else ''))
