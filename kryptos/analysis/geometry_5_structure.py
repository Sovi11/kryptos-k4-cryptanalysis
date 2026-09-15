"""Part 5: other structural signals: autocorrelation at lags 1-96, letter distribution by
column of the 31-wide layout, the six doubled letters against the geometry, repeated n-grams.
"""
import geometry_common as g
from collections import Counter
from math import sqrt

CT, CRIB = g.CT, g.CRIB
N = 97
print('IoC of K4 = %.4f (random 0.0385, English 0.066)' % g.ioc(CT))
print('letter counts:', sorted(Counter(CT).items(), key=lambda t: -t[1]))
print('missing letters:', [c for c in g.PLAIN if c not in CT])

print('\n== autocorrelation: coincidences ct[i]==ct[i+lag] ==')
rows = []
for lag in range(1, N):
    n = N - lag
    c = sum(1 for i in range(n) if CT[i] == CT[i + lag])
    exp = n / 26
    z = (c - exp) / sqrt(n * (1 / 26) * (25 / 26))
    rows.append((lag, c, n, c / n, z))
print('  lag  coinc  pairs  rate    z')
for lag, c, n, rate, z in rows:
    flag = ' <--' if z >= 2 else ''
    print('  %3d   %2d    %2d   %.3f  %+.2f%s' % (lag, c, n, rate, z, flag))
print('  lags with z>=2:', [(lag, c, n) for lag, c, n, rate, z in rows if z >= 2])
print('  total coincidences over all lags: %d, expected %.1f' % (sum(r[1] for r in rows), sum(r[2] for r in rows) / 26))

print('\n== letters by column, 31-wide sculpture layout (offset 27) ==')
grid = {}
for i, ch in enumerate(CT):
    r, c = g.layout_rowcol(i + 1, 27)
    grid.setdefault(c, []).append(ch)
same = [c for c, v in grid.items() if len(set(v)) < len(v)]
print('  col: letters (rows top->bottom)')
for c in range(1, 32):
    print('  %2d: %s' % (c, ''.join(grid[c])))
print('  columns with a repeated letter:', same, '(expected for 3-4 random letters per column: ~%.1f columns)' % (31 * (1 - (25/26)*(24/26))))
# also for the plain 31x3+4 layout (offset 0) and column-sum stats for widths 2..48
print('  repeated-letter columns count for every layout offset 0..30 (31-wide):',
      [sum(1 for c in range(31) if len(set(CT[i] for i in range(N) if (i + off) % 31 == c)) < sum(1 for i in range(N) if (i + off) % 31 == c)) for off in range(31)])

print('\n== doubled letters ==')
dbl = [(i + 1, CT[i]) for i in range(N - 1) if CT[i] == CT[i + 1]]
print('  positions (first letter, 1-indexed):', dbl)
print('  gaps between doubled-letter starts:', [b[0] - a[0] for a, b in zip(dbl, dbl[1:])])
for pos, ch in dbl:
    r, c = g.layout_rowcol(pos, 27)
    pt = (CRIB.get(pos, '?') + CRIB.get(pos + 1, '?'))
    print('  %s%s at %2d-%2d: sculpture row %d col %2d-%2d, plaintext %s, pos mod 31 = %d, pos mod 7 = %d, pos mod 4 = %d'
          % (ch, ch, pos, pos + 1, r + 1, c, c + 1, pt, pos % 31, pos % 7, pos % 4))
print('  Note: QQ=NO, SS=ST, TT=OC -> doubled ciphertext from non-doubled plaintext; for a periodic')
print('  key this needs key difference = plaintext difference at those two positions:')
for pos, ch in dbl:
    if pos in CRIB and pos + 1 in CRIB:
        for cmb in [('vig','plain','plain'),('vig','plain','kryptos'),('vig','kryptos','kryptos'),('beau','plain','kryptos')]:
            s1 = g.shift_for(CT[pos-1], CRIB[pos], *cmb); s2 = g.shift_for(CT[pos], CRIB[pos+1], *cmb)
            print('     %s%s pos %d %s: k=%d then %d (diff %d)' % (ch, ch, pos, '/'.join(cmb), s1, s2, (s2 - s1) % 26))

print('\n== repeated n-grams (n>=2) and their spacings (Kasiski) ==')
for n in (2, 3):
    seen = {}
    for i in range(N - n + 1):
        seen.setdefault(CT[i:i + n], []).append(i + 1)
    reps = {k: v for k, v in seen.items() if len(v) > 1}
    print('  n=%d: %d repeated: %s' % (n, len(reps), {k: (v, [b - a for a, b in zip(v, v[1:])]) for k, v in reps.items()}))
print('  expected repeated bigrams in 96 random bigrams over 676: ~%.1f' % (96 * 95 / 2 / 676))
