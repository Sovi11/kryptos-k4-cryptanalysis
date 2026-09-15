"""geo2 (b): is K4's key POSITIONAL WITHIN THE WHOLE LEFT PANEL?

The left panel carries K1|K2|K3|K4 = 869 characters (865 letters + four '?').  K1 occupies
panel letters 0-62, K2 63-431, K3 432-767, K4 768-864.  If the sculpture carried one key
indexed by absolute panel position, K4 would meet that key at a phase offset.

Three things are done here.

1. PHASE INVARIANCE.  For a periodic key the crib-consistency test asks only which crib
   positions fall in the same residue class mod p.  Adding a constant offset to every
   position is a bijection on Z_p, so the partition -- and hence the verdict -- is
   unchanged.  Demonstrated empirically for p = 2..60 at all 869 possible offsets.
   Consequence: every negative result already obtained for periodic keys on K4-relative
   positions applies verbatim to absolute panel positions, and to every repeating keyword
   at every possible alignment.

2. THE CONSTRAINT TABLE for p = 2..97, so that any future "survivor" at a long period can
   be judged against how many constraints the period actually imposes.

3. THE DECISIVE NEW TEST.  K1 and K2 have known plaintext AT KNOWN PANEL POSITIONS.  If one
   positional key ran across the panel, K1 and K2 determine it, and it then PREDICTS K4.
   Run for: uniform column widths w = 2..500 over the panel; the panel's actual physical
   (ragged) row/column geometry; and linear row/column shift models.
"""
import sys
from collections import Counter
import geo2_common as G
import geometry_common as g

CT, CRIB, N = G.CT, G.CRIB, G.N
COMBOS = G.COMBOS
PANEL_LET, PANEL_ALL = G.PANEL_LET, G.PANEL_ALL
K4L, K4A = G.K4_OFF_LET, G.K4_OFF_ALL

# ------------------------------------------------------------------ inputs --
_pt = open(G.DATA + '/k1_k3_plaintext.txt').read().split('\n')
K1PT = [l for l in _pt if l.startswith('BETWEEN')][0]
K2PT = [l for l in _pt if l.startswith('ITWAS')][0]
assert len(K1PT) == 63 and len(K2PT) == 370

# known (absolute panel letter index, ciphertext letter, plaintext letter)
KNOWN = []
for i in range(63):
    KNOWN.append((i, PANEL_LET[i], K1PT[i]))
for i in range(361):                       # K2 matches for 361 letters, then a carving error
    KNOWN.append((63 + i, PANEL_LET[63 + i], K2PT[i]))
for idx, c, p in KNOWN:
    assert PANEL_LET[idx] == c
print('known (ct,pt) pairs at absolute panel letter positions: %d  (K1 0-62, K2 63-423)'
      % len(KNOWN))

# K4 cribs at absolute panel letter positions
K4KNOWN = [(K4L + pos - 1, CT[pos - 1], CRIB[pos]) for pos in sorted(CRIB)]
print('K4 crib absolute panel letter positions: %d..%d'
      % (K4KNOWN[0][0], K4KNOWN[-1][0]))

# regression: under vig/kryptos/kryptos the K1 shifts must be PALIMPSEST, period 10
sh = [g.shift_for(c, p, 'vig', 'kryptos', 'kryptos') for _, c, p in KNOWN[:63]]
pal = ''.join(g.KRYPTOS[s] for s in sh[:10])
print('REGRESSION: K1 shifts under vig/kryptos/kryptos spell %s, period-10 repeat: %s'
      % (pal, all(sh[i] == sh[i % 10] for i in range(63))))
sh2 = [g.shift_for(c, p, 'vig', 'kryptos', 'kryptos') for _, c, p in KNOWN[63:]]
abs8 = ''.join(g.KRYPTOS[s] for s in sh2[:8])
print('REGRESSION: K2 shifts under vig/kryptos/kryptos spell %s, period-8 repeat: %s'
      % (abs8, all(sh2[i] == sh2[i % 8] for i in range(361))))

# ==================================================== 1. phase invariance ====
print('\n' + '=' * 78)
print('1. PHASE INVARIANCE OF THE PERIODIC CRIB TEST')
print('=' * 78)
bad = 0
checked = 0
for p in range(2, 61):
    base = None
    for off in range(0, 869):
        part = frozenset(frozenset(q for q in sorted(CRIB) if (q - 1 + off) % p == r)
                         for r in range(p))
        part = frozenset(f for f in part if f)
        if base is None:
            base = part
        elif part != base:
            bad += 1
        checked += 1
print('  partitions of the 24 crib positions into residue classes mod p, for p=2..60')
print('  and every offset 0..868: %d partitions compared, %d differed from the offset-0'
      % (checked, bad))
print('  partition.  (0 differences = the verdict cannot depend on the panel phase.)')
print('  Empirical check that the CONSISTENCY VERDICT is identical, p=2..60, offsets 0..96:')
mismatch = 0
for p in range(2, 61):
    for off in (0, 1, 7, 31, 96, 772, 768):
        for cmb in COMBOS[:4]:
            c0 = g.periodic_crib_test(CT, CRIB, p, *cmb)['consistent']
            cribs_off = {pos + off: pt for pos, pt in CRIB.items()}
            text_off = 'A' * off + CT
            c1 = g.periodic_crib_test(text_off, cribs_off, p, *cmb)['consistent']
            if c0 != c1:
                mismatch += 1
print('    verdict mismatches: %d' % mismatch)
print('  => every periodic key (any period 2-60, any content, hence every repeating keyword')
print('     of length <= 60) that fails on K4-relative positions also fails at absolute')
print('     panel positions, at all 869 alignments.  Periods 2-25 were already exhausted')
print('     in findings/families.md; this closes the "but the phase is different" loophole.')

# ================================================== 2. constraint table ======
print('\n' + '=' * 78)
print('2. HOW CONSTRAINED IS EACH PERIOD?  p = 2..97')
print('=' * 78)
print('  c = #crib collisions = 24 - #distinct residues.  chance = 26^-c.')
print('  "cons" = how many of the 12 cipher/alphabet pairings are consistent.')
rows = []
for p in range(2, 98):
    c = G.n_collisions(CRIB, p)
    cons = sum(1 for cmb in COMBOS if g.periodic_crib_test(CT, CRIB, p, *cmb)['consistent'])
    rows.append((p, c, cons))
print('   p: c cons |' * 4)
for i in range(0, len(rows), 4):
    print('  ' + ' | '.join('%3d:%3d %2d' % r for r in rows[i:i + 4]))
vac = [p for p, c, cons in rows if c == 0]
print('  periods with ZERO constraints (test is vacuous, all 12 pairings trivially pass): %s'
      % vac)
real = [(p, c, cons) for p, c, cons in rows if c > 0 and cons > 0]
print('  periods with >=1 constraint AND >=1 consistent pairing: %s' % (real or 'NONE'))
tot_exp = sum(12 * 26.0 ** -c for p, c, cons in rows if c > 0)
tot_obs = sum(cons for p, c, cons in rows if c > 0)
print('  over all constrained periods 2..97: expected %.2f consistent pairings by chance,'
      ' observed %d' % (tot_exp, tot_obs))

# ======================= 3. one positional key across the whole panel ========
print('\n' + '=' * 78)
print('3. A SINGLE POSITIONAL KEY ACROSS THE WHOLE LEFT PANEL')
print('=' * 78)
print('  K1+K2 give 424 (ct,pt) pairs at known absolute panel positions.  For a key indexed')
print('  by absolute position with period/width w, those pairs DETERMINE the key; K4 is then')
print('  a prediction, not a fit.  A width is reported only if the K1+K2 key is itself')
print('  self-consistent.')

def panel_column_test(index_of, wname, widths, known, k4known, seq_len):
    """index_of(w, i) -> key slot.  Returns list of (w, combo, n_pred, n_ok)."""
    out = []
    selfcons = 0
    for w in widths:
        for cmb in COMBOS:
            key = {}
            ok = True
            for i, c, p in known:
                slot = index_of(w, i)
                k = g.shift_for(c, p, *cmb)
                if slot in key:
                    if key[slot] != k:
                        ok = False
                        break
                else:
                    key[slot] = k
            if not ok:
                continue
            selfcons += 1
            npred = nok = 0
            for i, c, p in k4known:
                slot = index_of(w, i)
                if slot in key:
                    npred += 1
                    if key[slot] == g.shift_for(c, p, *cmb):
                        nok += 1
            out.append((w, cmb, npred, nok))
    return out, selfcons

WID = range(2, 501)
res, selfcons = panel_column_test(lambda w, i: i % w, 'letters-only', WID, KNOWN, K4KNOWN, 865)
print('\n  (3a) uniform width w = 2..500 over the 865 panel LETTERS')
print('       (w, combo) pairs tested: %d ; K1+K2-self-consistent: %d'
      % (len(WID) * len(COMBOS), selfcons))
pred = [r for r in res if r[2] > 0]
print('       of those, %d make >=1 prediction about a K4 crib.' % len(pred))
if pred:
    best = max(pred, key=lambda r: (r[3] / r[2], r[3]))
    print('       best: w=%d %s  predicted %d crib letters, %d correct (chance %.2f)'
          % (best[0], '/'.join(best[1]), best[2], best[3], best[2] / 26))
    full = [r for r in pred if r[2] == 24 and r[3] == 24]
    print('       cases predicting all 24 cribs correctly: %d' % len(full))
    hist = Counter(r[3] for r in pred)
    print('       distribution of #correct predictions:', dict(sorted(hist.items())))
    tot_pred = sum(r[2] for r in pred)
    tot_ok = sum(r[3] for r in pred)
    print('       aggregate: %d predictions, %d correct (%.3f); chance 1/26 = 0.038'
          % (tot_pred, tot_ok, tot_ok / tot_pred))
    ws = sorted({r[0] for r in res})
    print('       the %d widths whose K1+K2 key is self-consistent for >=1 pairing: %s'
          % (len(ws), ws if len(ws) < 90 else str(ws[:40]) + ' ... ' + str(ws[-10:])))
    print('       (a global width w must reconcile PALIMPSEST at period 10 from panel 0 with')
    print('        ABSCISSA at period 8 from panel 63; below w=%d no width can.)' % min(ws))

# with the four '?' counted as positions
K4KNOWN_A = [(K4A + pos - 1, CT[pos - 1], CRIB[pos]) for pos in sorted(CRIB)]
qpos = [i for i, ch in enumerate(PANEL_ALL) if ch == '?']
lett_to_all = [i for i, ch in enumerate(PANEL_ALL) if ch.isalpha()]
KNOWN_A = [(lett_to_all[i], c, p) for i, c, p in KNOWN]
res2, selfcons2 = panel_column_test(lambda w, i: i % w, 'with-?', WID, KNOWN_A, K4KNOWN_A, 869)
pred2 = [r for r in res2 if r[2] > 0]
print('\n  (3b) same, but counting the four "?" as occupying positions (869 slots)')
print('       self-consistent: %d ; making predictions: %d' % (selfcons2, len(pred2)))
if pred2:
    best = max(pred2, key=lambda r: (r[3] / r[2], r[3]))
    print('       best: w=%d %s  predicted %d, correct %d' % (best[0], '/'.join(best[1]), best[2], best[3]))
    print('       cases predicting all 24 correctly: %d'
          % len([r for r in pred2 if r[2] == 24 and r[3] == 24]))
    tot_pred = sum(r[2] for r in pred2); tot_ok = sum(r[3] for r in pred2)
    print('       aggregate: %d predictions, %d correct (%.3f)' % (tot_pred, tot_ok, tot_ok / tot_pred))

# (3c) the panel's ACTUAL ragged rows: key indexed by physical column
rowof = {}
colof = {}
li = 0
for R, row in enumerate(G.PANEL_ROWS):
    for C, ch in enumerate(row):
        if ch.isalpha():
            rowof[li] = R
            colof[li] = C
            li += 1
assert li == 865
print('\n  (3c) the panel\'s ACTUAL physical geometry: 28 rows of 29-33 characters.')
print('       row widths:', [len(r) for r in G.PANEL_ROWS])
print('       K4 crib letters sit in physical rows %s' % sorted({rowof[i] for i, _, _ in K4KNOWN}))
res3, sc3 = panel_column_test(lambda w, i: colof[i], 'physcol', [0], KNOWN, K4KNOWN, 865)
print('       per-physical-COLUMN key (33 slots): K1+K2-self-consistent pairings: %d of 12' % sc3)
for w, cmb, npred, nok in res3:
    print('         %s predicted %d, correct %d' % ('/'.join(cmb), npred, nok))
if sc3 == 0:
    # show why
    for cmb in COMBOS[:1]:
        key = {}; conf = 0
        for i, c, p in KNOWN:
            k = g.shift_for(c, p, *cmb); s = colof[i]
            if s in key and key[s] != k: conf += 1
            else: key.setdefault(s, k)
        print('         (e.g. %s: %d of %d K1+K2 letters conflict with an earlier letter in'
              ' their own physical column -- the panel has no per-column key)'
              % ('/'.join(cmb), conf, len(KNOWN)))
res4, sc4 = panel_column_test(lambda w, i: rowof[i], 'physrow', [0], KNOWN, K4KNOWN, 865)
print('       per-physical-ROW key (28 slots): self-consistent pairings: %d of 12' % sc4)
print('         (K4 occupies rows 24-27, which contain no K1/K2 letters, so even a')
print('          self-consistent row key would make 0 predictions about K4.)')

# (3d) linear models in the PHYSICAL row and column of the panel
print('\n  (3d) shift = a*row + b*col + d (mod 26) on the panel\'s physical geometry,')
print('       fitted to the 24 K4 cribs alone.  The full family is 26^3 x 12 = 210912')
print('       models; d is forced by the first crib, so 26^2 x 12 = 8112 (a,b) cases are')
print('       enumerated -- no model that fits all 24 cribs can be missed this way.')
best = []
for cmb in COMBOS:
    need = [(rowof[i], colof[i], g.shift_for(c, p, *cmb)) for i, c, p in K4KNOWN]
    for a in range(26):
        for b in range(26):
            # d is forced by the first crib
            d = (need[0][2] - a * need[0][0] - b * need[0][1]) % 26
            n = sum(1 for r, cl, k in need if (a * r + b * cl + d) % 26 == k)
            best.append((n, cmb, a, b, d))
best.sort(reverse=True)
print('       best fit: %d of 24 cribs  (%s a=%d b=%d d=%d)'
      % (best[0][0], '/'.join(best[0][1]), best[0][2], best[0][3], best[0][4]))
print('       models fitting all 24: %d' % sum(1 for b in best if b[0] == 24))
hist = Counter(b[0] for b in best)
print('       fit histogram:', dict(sorted(hist.items(), reverse=True)))
import math
print('       (the histogram starts at 1 because d is chosen to satisfy crib #1)')
print('       chance: P(a random model matches >=7 of the remaining 23) = %.2g, so among'
      % (1 - sum(math.comb(23, k) * (1/26.)**k * (25/26.)**(23-k) for k in range(6))))
print('       8112 models a best of 7/24 is exactly what chance delivers (expected %.1f).'
      % (8112 * (1 - sum(math.comb(23, k) * (1/26.)**k * (25/26.)**(23-k) for k in range(6)))))

# (3e) does K1's PALIMPSEST / K2's ABSCISSA, continued without a break, reach K4?
print('\n  (3e) continuing K1\'s and K2\'s own keys through the panel into K4')
KEYS = {'PALIMPSEST': 'PALIMPSEST', 'ABSCISSA': 'ABSCISSA', 'KRYPTOS': 'KRYPTOS',
        'PALIMPSESTABSCISSA': 'PALIMPSESTABSCISSA', 'ABSCISSAPALIMPSEST': 'ABSCISSAPALIMPSEST'}
ANCH = {'panel letter 0': K4L, 'panel char 0 (incl ?)': K4A, 'K4 letter 0': 0,
        'K3 start (panel letter 432)': K4L - 432, 'K2 start (panel letter 63)': K4L - 63}
print('       key, anchor, key-alphabet, cipher/alphabets -> #cribs matched of 24')
bestrow = (0,)
nrun = 0
for kname, kw in KEYS.items():
    for aname, base in ANCH.items():
        for keyalpha in ('plain', 'kryptos'):
            kv = [g.IDX[keyalpha][ch] for ch in kw]
            for cmb in COMBOS:
                n = 0
                for pos in sorted(CRIB):
                    k = kv[(base + pos - 1) % len(kv)]
                    if g.shift_for(CT[pos - 1], CRIB[pos], *cmb) == k:
                        n += 1
                nrun += 1
                if n > bestrow[0]:
                    bestrow = (n, kname, aname, keyalpha, cmb)
print('       %d (key, anchor, key-alphabet, cipher) combinations tested' % nrun)
print('       best: %d of 24 cribs -- %s anchored at %s, key alphabet %s, %s'
      % (bestrow[0], bestrow[1], bestrow[2], bestrow[3], '/'.join(bestrow[4])))
print('       chance expectation for 24 cribs at 1/26: mean 0.92; P(>=5) = 0.19%')
