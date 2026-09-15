"""geo2 (a): read the 97 letters off the 4+31+31+31 panel block in every plausible
PHYSICAL order, remap the 24 cribs, and re-run the periodic-substitution consistency
test (p = 2..26, 12 cipher/alphabet pairings) plus a periodic-IoC scan.

Orders covered: row-major (4 directions), boustrophedon by row (4), column-major (4),
boustrophedon by column (4), the two diagonal families (8), spirals in and out from each
corner in both senses (16), every ordering of the three 31-letter rows with each row
independently forward/reversed (6 x 8 = 48) crossed with four placements of OBKR
(front / front-reversed / end / dropped) = 192, the 93-letter body alone under the same
geometric orders, and whole-text reversal.

Every reported "consistent" case is accompanied by its collision count c (the number of
crib constraints the period actually imposes) and the chance probability 26^-c.
"""
import sys
from collections import Counter
from itertools import permutations, product
import geo2_common as G
import geometry_common as g

CT, CRIB, N = G.CT, G.CRIB, G.N
CELLS, CELL_AT, ROWS4 = G.CELLS, G.CELL_AT, G.ROWS4
COMBOS = G.COMBOS

orders = {}   # name -> list of original 0-indexed positions

def add(name, order):
    order = list(order)
    assert len(set(order)) == len(order)
    orders[name] = order

# ---- helper: sort the cells by a key over (row, col) ----------------------
def by(keyf, cells=CELLS):
    return [o for r, c, o in sorted(cells, key=lambda t: keyf(t[0], t[1]))]

BODY = [ (r, c, o) for r, c, o in CELLS if r >= 1 ]   # the 93-letter 3x31 block

for tag, cells in (('97', CELLS), ('body93', BODY)):
    # 1. row-major, four directions
    add('%s rowmajor LR/TB' % tag, by(lambda r, c: (r, c), cells))
    add('%s rowmajor RL/TB' % tag, by(lambda r, c: (r, -c), cells))
    add('%s rowmajor LR/BT' % tag, by(lambda r, c: (-r, c), cells))
    add('%s rowmajor RL/BT' % tag, by(lambda r, c: (-r, -c), cells))
    # 2. boustrophedon by row, two phases, two vertical directions
    for ph in (0, 1):
        add('%s boustro-row TB ph%d' % (tag, ph),
            by(lambda r, c, ph=ph: (r, c if r % 2 == ph else -c), cells))
        add('%s boustro-row BT ph%d' % (tag, ph),
            by(lambda r, c, ph=ph: (-r, c if r % 2 == ph else -c), cells))
    # 3. column-major, four directions
    add('%s colmajor LR/TB' % tag, by(lambda r, c: (c, r), cells))
    add('%s colmajor LR/BT' % tag, by(lambda r, c: (c, -r), cells))
    add('%s colmajor RL/TB' % tag, by(lambda r, c: (-c, r), cells))
    add('%s colmajor RL/BT' % tag, by(lambda r, c: (-c, -r), cells))
    # 4. boustrophedon by column
    for ph in (0, 1):
        add('%s boustro-col LR ph%d' % (tag, ph),
            by(lambda r, c, ph=ph: (c, r if c % 2 == ph else -r), cells))
        add('%s boustro-col RL ph%d' % (tag, ph),
            by(lambda r, c, ph=ph: (-c, r if c % 2 == ph else -r), cells))
    # 5. diagonals
    for dname, dk in (('sum', lambda r, c: r + c), ('diff', lambda r, c: r - c)):
        for ds in (1, -1):
            for ws in (1, -1):
                add('%s diag-%s order%+d within%+d' % (tag, dname, ds, ws),
                    by(lambda r, c, dk=dk, ds=ds, ws=ws: (ds * dk(r, c), ws * r), cells))
    # 6. spirals over the bounding box, skipping absent cells
    present = {(r, c): o for r, c, o in cells}
    r0, r1 = min(r for r, c in present), max(r for r, c in present)
    c0, c1 = min(c for r, c in present), max(c for r, c in present)
    def spiral(start, sense):
        """start in {TL,TR,BL,BR}; sense 'cw' or 'ccw'.  Returns cell list inward."""
        top, bot, lef, rig = r0, r1, c0, c1
        out = []
        # normalise: build the ring traversal generically
        while top <= bot and lef <= rig:
            ring = []
            if start == 'TL' and sense == 'cw':
                ring += [(top, c) for c in range(lef, rig + 1)]
                ring += [(r, rig) for r in range(top + 1, bot + 1)]
                if bot > top: ring += [(bot, c) for c in range(rig - 1, lef - 1, -1)]
                if rig > lef: ring += [(r, lef) for r in range(bot - 1, top, -1)]
            elif start == 'TL' and sense == 'ccw':
                ring += [(r, lef) for r in range(top, bot + 1)]
                ring += [(bot, c) for c in range(lef + 1, rig + 1)]
                if rig > lef: ring += [(r, rig) for r in range(bot - 1, top - 1, -1)]
                if bot > top: ring += [(top, c) for c in range(rig - 1, lef, -1)]
            elif start == 'TR' and sense == 'cw':
                ring += [(r, rig) for r in range(top, bot + 1)]
                ring += [(bot, c) for c in range(rig - 1, lef - 1, -1)]
                if rig > lef: ring += [(r, lef) for r in range(bot - 1, top - 1, -1)]
                if bot > top: ring += [(top, c) for c in range(lef + 1, rig)]
            elif start == 'TR' and sense == 'ccw':
                ring += [(top, c) for c in range(rig, lef - 1, -1)]
                ring += [(r, lef) for r in range(top + 1, bot + 1)]
                if bot > top: ring += [(bot, c) for c in range(lef + 1, rig + 1)]
                if rig > lef: ring += [(r, rig) for r in range(bot - 1, top, -1)]
            elif start == 'BL' and sense == 'cw':
                ring += [(bot, c) for c in range(lef, rig + 1)]
                ring += [(r, rig) for r in range(bot - 1, top - 1, -1)]
                if bot > top: ring += [(top, c) for c in range(rig - 1, lef - 1, -1)]
                if rig > lef: ring += [(r, lef) for r in range(top + 1, bot)]
            elif start == 'BL' and sense == 'ccw':
                ring += [(r, lef) for r in range(bot, top - 1, -1)]
                ring += [(top, c) for c in range(lef + 1, rig + 1)]
                if rig > lef: ring += [(r, rig) for r in range(top + 1, bot + 1)]
                if bot > top: ring += [(bot, c) for c in range(rig - 1, lef, -1)]
            elif start == 'BR' and sense == 'cw':
                ring += [(r, rig) for r in range(bot, top - 1, -1)]
                ring += [(top, c) for c in range(rig - 1, lef - 1, -1)]
                if rig > lef: ring += [(r, lef) for r in range(top + 1, bot + 1)]
                if bot > top: ring += [(bot, c) for c in range(lef + 1, rig)]
            else:  # BR ccw
                ring += [(bot, c) for c in range(rig, lef - 1, -1)]
                ring += [(r, lef) for r in range(bot - 1, top - 1, -1)]
                if bot > top: ring += [(top, c) for c in range(lef + 1, rig + 1)]
                if rig > lef: ring += [(r, rig) for r in range(top + 1, bot)]
            out += ring
            top += 1; bot -= 1; lef += 1; rig -= 1
        seen = set(); res = []
        for rc in out:
            if rc in present and rc not in seen:
                seen.add(rc); res.append(present[rc])
        return res
    for st in ('TL', 'TR', 'BL', 'BR'):
        for sn in ('cw', 'ccw'):
            sp = spiral(st, sn)
            add('%s spiral-in %s %s' % (tag, st, sn), sp)
            add('%s spiral-out %s %s' % (tag, st, sn), sp[::-1])

# 7. the three 31-letter rows in every order, each forward or reversed,
#    with OBKR placed four ways
R = [ROWS4[1], ROWS4[2], ROWS4[3]]
OB = ROWS4[0]
for perm in permutations(range(3)):
    for flips in product((0, 1), repeat=3):
        body = []
        for k, idx in enumerate(perm):
            row = R[idx]
            body += (row[::-1] if flips[k] else row)
        tagp = 'rows%s%s' % (''.join(str(i + 1) for i in perm),
                             ''.join('R' if f else 'F' for f in flips))
        add('%s OBKR-front' % tagp, OB + body)
        add('%s OBKRrev-front' % tagp, OB[::-1] + body)
        add('%s OBKR-end' % tagp, body + OB)
        add('%s OBKR-dropped' % tagp, body)

# 8. whole-text reversal, and the plain identity
add('identity', list(range(N)))
add('reverse97', list(range(N))[::-1])

print('reading orders built: %d' % len(orders))
print('sanity: identity text == CT:', G.apply_perm(orders['identity'])[0] == CT)
t, c = G.apply_perm(orders['97 rowmajor LR/TB'])
print('sanity: "97 rowmajor LR/TB" == CT:', t == CT, 'cribs identical:', c == CRIB)
t, c = G.apply_perm(orders['body93 rowmajor LR/TB'])
print('sanity: body93 rowmajor == CT[4:]:', t == CT[4:], 'cribs shifted by 4:',
      c == {k - 4: v for k, v in CRIB.items()}, 'n cribs', len(c))
t, c = G.apply_perm(orders['97 colmajor LR/TB'])
print('col-major text:', t)
print('  crib positions there:', sorted(c))

# ---------------------------------------------------------------- tests -----
PERIODS = range(2, 27)
print('\n== periodic-key crib consistency over every reading order ==')
print('   periods %d..%d, %d cipher/alphabet pairings' % (PERIODS[0], PERIODS[-1], len(COMBOS)))
hits = []
tests = 0
expected = 0.0
coll_hist = Counter()
for name, perm in orders.items():
    text, cribs = G.apply_perm(perm)
    for p in PERIODS:
        c = G.n_collisions(cribs, p)
        coll_hist[c] += len(COMBOS)
        expected += len(COMBOS) * (26.0 ** -c)
        for cmb in COMBOS:
            r = G.consistency(text, cribs, p, cmb)
            tests += 1
            if r['consistent']:
                hits.append((c, name, p, cmb, r))
print('   tests run: %d' % tests)
print('   constraint-count histogram (c = #crib collisions; tests at that c):')
for c in sorted(coll_hist):
    print('      c=%2d : %6d tests, each passes by chance with prob 26^-%d = %.3g'
          % (c, coll_hist[c], c, 26.0 ** -c))
print('   EXPECTED number of consistent cases by chance: %.1f' % expected)
print('   OBSERVED number of consistent cases:           %d' % len(hits))
obs_hist = Counter(h[0] for h in hits)
print('   observed consistent by constraint count c:', dict(sorted(obs_hist.items())))
print('   expected consistent by constraint count c:',
      {c: round(coll_hist[c] * 26.0 ** -c, 2) for c in sorted(coll_hist)})

strong = sorted([h for h in hits if h[0] >= 3], key=lambda h: -h[0])
print('\n   every consistent case with >= 3 real constraints (chance <= 5.7e-5 each):')
if not strong:
    print('      NONE')
for c, name, p, cmb, r in strong[:60]:
    print('      c=%2d p=%2d %-8s pt=%-7s ct=%-7s %-28s logp=%.3f words=%s'
          % (c, p, cmb[0], cmb[1], cmb[2], name, g.unigram_logp(r['new_letters']),
             g.word_hits(r['new_letters'])))
    print('           ', r['decrypt'])
if len(strong) > 60:
    print('      ... %d more' % (len(strong) - 60))

# rank ALL consistent cases by English-likeness of the newly revealed letters
print('\n   top 15 consistent cases ranked by unigram log-prob of the NEW (non-crib) letters')
print('   (English ~ -2.90, uniform random ~ -3.30, K4-letter-pool shuffle ~ -3.4):')
ranked = sorted(hits, key=lambda h: -g.unigram_logp(h[4]['new_letters']))
for c, name, p, cmb, r in ranked[:15]:
    print('      logp=%.3f c=%2d p=%2d %-8s %-7s %-7s %-28s known=%2d words=%s'
          % (g.unigram_logp(r['new_letters']), c, p, cmb[0], cmb[1], cmb[2], name,
             r['n_known'], g.word_hits(r['new_letters'])))
    print('           ', r['decrypt'])

# ------------------------------------------------------------- IoC scan -----
print('\n== periodic-IoC scan over every reading order, p=2..12 ==')
print('   (only p<=12 -- with 97 letters a period p leaves columns of ~97/p letters and the')
print('    IoC of a <8-letter column is almost pure noise, which is why the p=25..30 maxima')
print('    reported in geometry_4_out.txt are artefacts, not signal.)')
null = {}
base = list(CT)
for p in range(2, 13):
    m, p95, mx = G.periodic_ioc_null(CT, p, trials=4000)
    null[p] = (m, p95, mx)
print('   null (random shuffles of K4\'s own letters, 4000 trials):')
print('   ' + '  '.join('p%d:%.4f/%.4f' % (p, null[p][0], null[p][1]) for p in range(2, 13)))
print('   (mean / 95th percentile)')
rows = []
for name, perm in orders.items():
    text, _ = G.apply_perm(perm)
    if len(text) != N:
        continue
    for p in range(2, 13):
        v = G.periodic_ioc(text, p)
        if v > null[p][1]:
            rows.append((v - null[p][1], v, p, name))
rows.sort(reverse=True)
print('   reading orders whose periodic IoC exceeds the 95th-percentile null, top 20')
print('   of %d such (order, p) pairs out of %d tested -- 5%% of %d = %.0f expected:'
      % (len(rows), sum(1 for n, pm in orders.items() if len(pm) == N) * 11,
         sum(1 for n, pm in orders.items() if len(pm) == N) * 11,
         0.05 * sum(1 for n, pm in orders.items() if len(pm) == N) * 11))
for d, v, p, name in rows[:20]:
    print('      IoC=%.4f (null95=%.4f) p=%2d  %s' % (v, null[p][1], p, name))

# ---------------------------------------------------- general polyalphabetic -
print('\n== APPENDIX: general periodic POLYALPHABETIC over every reading order ==')
print('   Each of the p key slots gets its own arbitrary mixed alphabet (strictly more')
print('   general than Quagmire I-IV and than any additive key).  The only crib constraint')
print('   is that within a residue class the ct->pt map be a partial bijection.  A period')
print('   that fails here is impossible for EVERY alphabet set, not just keyed ones.')
def gpoly(text, cribs, p):
    fwd, rev, nf, nr = {}, {}, 0, 0
    for pos, pt in sorted(cribs.items()):
        r = (pos - 1) % p
        c = text[pos - 1]
        if fwd.setdefault((r, c), pt) != pt:
            nf += 1
        if rev.setdefault((r, pt), c) != c:
            nr += 1
    return nf + nr
full = {n: pm for n, pm in orders.items() if len(pm) == N}
print('   %d reading orders of all 97 letters x periods 2..31' % len(full))
killed = {}
for p in range(2, 32):
    k = [n for n, pm in full.items() if gpoly(*G.apply_perm(pm), p) > 0]
    killed[p] = len(k)
print('   p  : reading orders KILLED (of %d) -- i.e. no polyalphabetic of that period can'
      % len(full))
print('        produce K4 from that reading order under any alphabets at all')
for p in range(2, 32):
    bar = '#' * int(40 * killed[p] / len(full))
    print('   %2d : %4d/%d  %s' % (p, killed[p], len(full), bar))
alive = [(p, n) for p in range(2, 32) for n, pm in full.items()
         if gpoly(*G.apply_perm(pm), p) == 0]
print('   (order, period) pairs NOT killed: %d of %d' % (len(alive), len(full) * 30))
print('   periods killed for EVERY one of the %d reading orders: %s'
      % (len(full), [p for p in range(2, 32) if killed[p] == len(full)]))
print('   periods killed for NO reading order: %s'
      % [p for p in range(2, 32) if killed[p] == 0])
