"""Part 2: OBKR (the 4 letters that share the last K3 row with '?') as a header/key.

Tests: OBKR / RKBO as a period-4 key (every phase, key letters indexed in the plain or the
KRYPTOS alphabet), applied to the 93-letter body and to the full 97; ciphertext- and
plaintext-autokey with primer OBKR; periodic IoC of the 93-letter body; period-31
(three rows of 31) column consistency of the cribs on the body.
"""
import geometry_common as g

CT, CRIB = g.CT, g.CRIB
BODY = CT[4:]
BCRIB = {p - 4: v for p, v in CRIB.items()}      # crib positions within the 93-letter body
assert len(BODY) == 93
combos = [(c, pa, ca) for c in g.CIPHERS for pa, ca in g.ALPHA_PAIRS]

print('93-letter body:', BODY)
print('crib positions in body:', sorted(BCRIB))
print('IoC full 97 = %.4f   IoC body 93 = %.4f' % (g.ioc(CT), g.ioc(BODY)))

# ---- OBKR as a periodic key ----
print('\n== OBKR / RKBO as a period-4 key (key letter -> shift via plain or KRYPTOS index) ==')
best = []
for text, cribs, label in ((BODY, BCRIB, 'body93'), (CT, CRIB, 'full97')):
    for keyword in ('OBKR', 'RKBO'):
        for ka in g.ALPHABETS:
            kv = [g.IDX[ka][c] for c in keyword]
            for ph in range(4):
                for cmb in combos:
                    n = sum(1 for pos, pt in cribs.items()
                            if g.shift_for(text[pos - 1], pt, *cmb) == kv[(pos - 1 + ph) % 4])
                    best.append((n, label, keyword, ka, ph, cmb))
best.sort(reverse=True)
print('tests:', len(best), ' best crib fit:', best[0][0], 'of 24')
for b in best[:6]:
    print('  ', b)
print('  chance expectation for 24 cribs at 1/26 each: mean 0.92, P(>=5) = 0.19%')

# ---- OBKR as an autokey primer ----
print('\n== ciphertext-autokey with primer OBKR (k_i = ct_{i-4}) on the 97 letters ==')
for cmb in combos:
    dec = []
    for i, ch in enumerate(CT):
        k = g.IDX[cmb[2]][CT[i - 4]] if i >= 4 else None   # primer letters key themselves? treat OBKR as primer only
        dec.append(g.decrypt_letter(ch, k, *cmb) if k is not None else '.')
    dec = ''.join(dec)
    n = sum(1 for pos, pt in CRIB.items() if dec[pos - 1] == pt)
    print('  %-8s %-7s %-7s crib hits %2d/24  %s' % (cmb + (n, dec)))
print('\n== plaintext-autokey with primer OBKR (k_i = pt_{i-4}); testable where pt_{i-4} is a crib ==')
for cmb in combos:
    hits = tot = 0
    for pos, pt in CRIB.items():
        if pos - 4 in CRIB:
            tot += 1
            need = g.shift_for(CT[pos - 1], pt, *cmb)
            if need == g.IDX[cmb[1]][CRIB[pos - 4]]:
                hits += 1
    print('  %-8s %-7s %-7s testable %d, hits %d' % (cmb + (tot, hits)))

# ---- periodic IoC of the body ----
print('\n== periodic IoC (mean column IoC) of the 93-letter body, p=2..46 ==')
rows = []
for p in range(2, 47):
    rows.append((p, g.periodic_ioc(BODY, p)))
print('  ' + '  '.join('p%d=%.3f' % r for r in rows))
print('  top 5:', sorted(rows, key=lambda r: -r[1])[:5])
print('  (random text ~0.038; English/monoalphabetic ~0.066; columns are short, ~3-46 letters)')

# ---- period 31: three rows of 31 ----
print('\n== period-31 (3 rows of 31) column consistency on the body ==')
print('  body crib positions -> (row, col):', {p: (( p - 1) // 31 + 1, (p - 1) % 31 + 1) for p in sorted(BCRIB)})
for cmb in combos:
    r = g.periodic_crib_test(BODY, BCRIB, 31, *cmb)
    print('  %-8s %-7s %-7s collisions=%d consistent=%s conflicts=%s' % (cmb + (r['collisions'], r['consistent'], r['conflicts'])))
    print('       partial decrypt (key from cribs; conflicting columns blanked):')
    for row in range(3):
        print('        ', r['decrypt'][row * 31:(row + 1) * 31])
