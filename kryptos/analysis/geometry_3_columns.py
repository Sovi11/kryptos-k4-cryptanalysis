"""Part 3: column analysis of the 31-wide sculpture layout (4 + 31 + 31 + 31).

Row 1 = OBKR at cols 28-31 (after the '?' at col 27); rows 2-4 = 31 letters each.
For each cipher / alphabet pairing, the key value every crib demands of its column is
listed; columns hit by two cribs are checked for agreement.  Then the crib-derived
column keys are used to decrypt every other letter in those columns (a period-31 key
is exactly a per-column key), and the same is done for periods 27-30 and 32-52.
"""
import geometry_common as g

CT, CRIB, CP = g.CT, g.CRIB, g.CRIB_POS
combos = [(c, pa, ca) for c in g.CIPHERS for pa, ca in g.ALPHA_PAIRS]
OFF = 27  # sculpture layout

print('Sculpture layout (row, col) of each crib letter, 4+31+31+31, rows numbered 1-4:')
for pos in CP:
    r, c = g.layout_rowcol(pos, OFF)
    print('  pos %2d  %s->%s  row %d col %2d' % (pos, CT[pos - 1], CRIB[pos], r + 1, c))
cols = {}
for pos in CP:
    cols.setdefault(g.layout_rowcol(pos, OFF)[1], []).append(pos)
double = {c: ps for c, ps in cols.items() if len(ps) > 1}
print('\nEAST NORTHEAST occupies row 2 cols %d-%d; BERLIN CLOCK occupies row 3 cols %d-31 and row 4 cols 1-%d'
      % (g.layout_rowcol(22, OFF)[1], g.layout_rowcol(34, OFF)[1], g.layout_rowcol(64, OFF)[1], g.layout_rowcol(74, OFF)[1]))
print('Columns constrained twice:', {c: [(p, CT[p-1], CRIB[p]) for p in ps] for c, ps in double.items()})
print('Distinct constrained columns:', len(cols), sorted(cols))

print('\n== required key value per column, per cipher/alphabet pairing (col: values) ==')
for cmb in combos:
    sh = g.crib_shifts(*cmb)
    line = []
    ok = True
    for c in sorted(cols):
        vals = sorted({sh[p] for p in cols[c]})
        if len(vals) > 1:
            ok = False
        line.append('%d:%s' % (c, '/'.join(map(str, vals))))
    print('  %-8s pt=%-7s ct=%-7s consistent=%-5s  %s' % (cmb + (ok, ' '.join(line))))

print('\n== period-31 column-key decryption of the whole 97 (crib columns only) ==')
print('   Under any per-column (period-31) key the 22 crib-fixed columns decrypt every row.')
print('   Non-crib letters produced are scored: unigram log-prob per letter (English ~ -2.9, random ~ -3.5)')
scored = []
for cmb in combos:
    r = g.periodic_crib_test(CT, CRIB, 31, *cmb)
    scored.append((g.unigram_logp(r['new_letters']), cmb, r))
scored.sort(key=lambda t: -t[0])
for lp, cmb, r in scored:
    print('  %-8s pt=%-7s ct=%-7s consistent=%-5s conflicts=%s  new-letter logp=%.3f  words=%s'
          % (cmb + (r['consistent'], r['conflicts'], lp, g.word_hits(r['new_letters']))))
    d = '   ' + r['decrypt']
    print('      ', '?' * 0 + ' ' * 27 + d[:4] if False else '')
    # print in sculpture rows
    grid = ' ' * 27 + r['decrypt']
    for row in range(4):
        print('        ', grid[row * 31:(row + 1) * 31])

print('\n== same test for every period 2..52 (per-column keys of a p-wide layout): consistent ones ==')
print('   period, #collisions, consistent combos; for consistent cases the new-letter unigram score')
summary = []
for p in range(2, 53):
    for cmb in combos:
        r = g.periodic_crib_test(CT, CRIB, p, *cmb)
        if r['consistent'] and r['collisions'] > 0:
            summary.append((p, r['collisions'], cmb, g.unigram_logp(r['new_letters']), r['new_letters']))
    n_coll = g.periodic_crib_test(CT, CRIB, p, 'vig', 'plain', 'plain')['collisions']
    if n_coll == 0:
        print('  p=%2d: 0 collisions (unconstrained by consistency)' % p)
print('  consistent (period, collisions, combo, logp):')
for s in sorted(summary, key=lambda s: (-s[1], -s[3])):
    print('   p=%2d coll=%d %-8s %-7s %-7s logp=%.3f  %s' % (s[0], s[1], *s[2], s[3], s[4]))
if not summary:
    print('   none')
print('\n== periods 27, 28, 29 (no crib collisions): decrypt of the crib-keyed positions ==')
for p in (27, 28, 29):
    best = max(((g.unigram_logp(r['new_letters']), cmb, r) for cmb in combos
                for r in [g.periodic_crib_test(CT, CRIB, p, *cmb)]), key=lambda t: t[0])
    print('  p=%d best combo %s logp=%.3f' % (p, best[1], best[0]))
    print('     ', best[2]['decrypt'])
    print('      new letters:', best[2]['new_letters'])
