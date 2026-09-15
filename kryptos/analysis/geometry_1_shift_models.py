"""Part 1: position-dependent shift models  shift_i = f(i)  fitted to the 24 crib shifts.

For every cipher (Vigenere / Beaufort / variant Beaufort) and every (plaintext alphabet,
ciphertext alphabet) pairing in {plain, KRYPTOS}^2 we compute the key value k_i required at
each crib position, then ask whether any simple f(i) reproduces all 24 of them.
Families: linear, quadratic, cubic, triangular, sawtooth (i mod m), block (i // m),
row/col-linear in a w-wide panel (all widths 2..48, all offsets), row*col bilinear in the
31-wide panel, and Gronsfeld keys built from the K2 coordinate digits.
"""
import sys, itertools, time
from math import comb
import geometry_common as g

CT, CP = g.CT, g.CRIB_POS
combos = [(c, pa, ca) for c in g.CIPHERS for pa, ca in g.ALPHA_PAIRS]
SHIFTS = {cmb: g.crib_shifts(*cmb) for cmb in combos}

results = {}   # family -> dict(tested, best, best_models, full)
def record(family, cmb, nfit, desc, tested_inc=1):
    r = results.setdefault(family, {'tested': 0, 'best': 0, 'best_models': [], 'full': []})
    r['tested'] += tested_inc
    if nfit > r['best']:
        r['best'], r['best_models'] = nfit, [(cmb, desc)]
    elif nfit == r['best'] and len(r['best_models']) < 5:
        r['best_models'].append((cmb, desc))
    if nfit == 24:
        r['full'].append((cmb, desc))

def count_fit(sh, f):
    return sum(1 for p in CP if f(p) == sh[p])

# ---------- polynomial families in i (1-indexed; any index offset is absorbed) ----------
for cmb in combos:
    sh = SHIFTS[cmb]
    # linear
    for a in range(26):
        for b in range(26):
            n = count_fit(sh, lambda i: (a * i + b) % 26)
            record('linear a*i+b', cmb, n, f'a={a} b={b}')
    # quadratic
    for a in range(26):
        for b in range(26):
            for c in range(26):
                n = count_fit(sh, lambda i: (a * i * i + b * i + c) % 26)
                record('quadratic a*i^2+b*i+c', cmb, n, f'a={a} b={b} c={c}')
    # triangular numbers T(i)=i(i+1)/2 (not reachable as a*i^2 mod 26 since 2 is not invertible)
    for a in range(26):
        for b in range(26):
            n = count_fit(sh, lambda i: (a * (i * (i + 1) // 2) + b) % 26)
            record('triangular a*T(i)+b', cmb, n, f'a={a} b={b}')
    # sawtooth: a*(i mod m)+b, and block: a*(i // m)+b, with i 0-indexed and all phases
    for m in range(2, 98):
        for ph in range(m):
            for a in range(1, 26):
                for b in range(26):
                    n = count_fit(sh, lambda i: (a * ((i - 1 + ph) % m) + b) % 26)
                    record('sawtooth a*((i+ph) mod m)+b', cmb, n, f'm={m} ph={ph} a={a} b={b}')
                    n = count_fit(sh, lambda i: (a * ((i - 1 + ph) // m) + b) % 26)
                    record('block a*((i+ph) div m)+b', cmb, n, f'm={m} ph={ph} a={a} b={b}')
    print('poly/sawtooth done for', cmb, file=sys.stderr)

# ---------- cubic (c determined from first crib to keep it cheap) ----------
p0 = CP[0]
for cmb in combos:
    sh = SHIFTS[cmb]
    for a in range(26):
        for b in range(26):
            for c in range(26):
                d = (sh[p0] - a * p0 ** 3 - b * p0 ** 2 - c * p0) % 26
                n = count_fit(sh, lambda i: (a * i ** 3 + b * i * i + c * i + d) % 26)
                record('cubic', cmb, n, f'a={a} b={b} c={c} d={d}')

# ---------- row/col linear in a w-wide panel: k = a*row + b*col + c ----------
# w=31 with offset 27 is the sculpture layout; all widths/offsets are tried.
t0 = time.time()
for w in range(2, 49):
    for off in range(w):
        rc = {p: divmod(p - 1 + off, w) for p in CP}
        for cmb in combos:
            sh = SHIFTS[cmb]
            r0, c0 = rc[p0]
            for a in range(26):
                for b in range(26):
                    c = (sh[p0] - a * r0 - b * c0) % 26
                    n = 1 + sum(1 for p in CP[1:] if (a * rc[p][0] + b * rc[p][1] + c) % 26 == sh[p])
                    fam = 'rowcol a*row+b*col+c (w=31)' if w == 31 else 'rowcol a*row+b*col+c (w=2..48)'
                    record(fam, cmb, n, f'w={w} off={off} a={a} b={b} c={c}')
print('rowcol done', time.time() - t0, file=sys.stderr)

# ---------- bilinear in the 31-wide panel: k = a*row*col + b*row + c*col + d ----------
t0 = time.time()
for off in range(31):
    rc = {p: divmod(p - 1 + off, 31) for p in CP}
    rest = CP[1:]
    for cmb in combos:
        sh = SHIFTS[cmb]
        r0, c0 = rc[p0]
        for a in range(26):
            for b in range(26):
                for c in range(26):
                    d = (sh[p0] - a * r0 * c0 - b * r0 - c * c0) % 26
                    n = 1
                    for p in rest:
                        r, cc = rc[p]
                        if (a * r * cc + b * r + c * cc + d) % 26 == sh[p]:
                            n += 1
                    record('bilinear w=31', cmb, n, f'off={off} a={a} b={b} c={c} d={d}')
print('bilinear done', time.time() - t0, file=sys.stderr)

# ---------- Gronsfeld keys from the K2 coordinates 38 57 6.5 N, 77 8 44 W ----------
DIGIT_KEYS = {
    'N+W 38576577844': '38576577844',
    'N+W zero-padded 3857065778440': '3857065778440',
    'N 385765': '385765', 'N 3857065': '3857065',
    'W 77844': '77844', 'W 778440': '778440',
    'W+N 7784438576 5': '7784438576' + '5',
    'digits with 6.5->65 and 44 as 4,4 + K2 fix hint 2 (LAYER TWO)': '385765778442',
    'pairs mod 26: 38,57,65,77,8,44': ''.join(chr(65 + (x % 26)) for x in (38, 57, 65, 77, 8, 44)),
    'pairs mod 26: 38,57,6,5,77,8,44': ''.join(chr(65 + (x % 26)) for x in (38, 57, 6, 5, 77, 8, 44)),
}
def gron_key_values(s):
    vals = []
    for ch in s:
        vals.append(int(ch) if ch.isdigit() else ord(ch) - 65)
    return vals
for name, s in DIGIT_KEYS.items():
    vals = gron_key_values(s)
    for direction, kv in (('fwd', vals), ('rev', vals[::-1])):
        L = len(kv)
        for ph in range(L):
            for cmb in combos:
                sh = SHIFTS[cmb]
                n = count_fit(sh, lambda i: kv[(i - 1 + ph) % L])
                record('Gronsfeld K2-coordinate digits', cmb, n, f'{name} {direction} phase={ph}')
                # also digits as shifts in the negative direction is covered by varbeau; and
                # digits applied only to the 93-letter body (skip OBKR) = phase shift by 4, covered.

# ---------- report ----------
print('Crib shifts (key value needed at each crib position) for each cipher/alphabet pairing:')
for cmb in combos:
    print('  %-8s pt=%-7s ct=%-7s' % cmb, [SHIFTS[cmb][p] for p in CP])
print()
print('%-42s %10s %8s  %s' % ('family', 'models', 'best fit', 'example best models (cipher,pt-alpha,ct-alpha; params)'))
for fam, r in results.items():
    ex = '; '.join(f'{c[0]}/{c[1]}/{c[2]} {d}' for c, d in r['best_models'][:3])
    print('%-42s %10d %8d  %s' % (fam, r['tested'], r['best'], ex))
print()
full = [(fam, c, d) for fam, r in results.items() for c, d in r['full']]
print('Models fitting all 24 cribs:', len(full))
for fam, c, d in full:
    print('  ', fam, c, d)

# Expected best-fit under pure chance, for context: P(a random model matches >= m of 24 cribs)
print()
print('Chance reference: P(random model fits >= m cribs) for m=4..8:',
      {m: '%.2e' % sum(comb(24, k) * (1 / 26) ** k * (25 / 26) ** (24 - k) for k in range(m, 25)) for m in range(4, 9)})
