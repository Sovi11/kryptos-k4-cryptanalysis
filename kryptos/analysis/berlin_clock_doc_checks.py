#!/usr/bin/env python3
"""
Verification arithmetic for lateral/berlin_clock.md.

Nothing here is cryptanalysis. It checks the factual claims the document makes, so that
none of them is asserted from memory:

  1. International Morse renderings of every K0 slab message, and the three
     spacing/direction ambiguities the published transcriptions disagree about.
  2. Mengenlehreuhr row arithmetic: reading a time, state-space counts, lamp totals.
  3. Great-circle and rhumb-line bearings from the sculpture (and from the K2
     coordinates) to Berlin, and where they fall on 16- and 32-point compass roses.

Run:  python3 analysis/berlin_clock_doc_checks.py
"""
MORSE = {
 'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..',
 'J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.',
 'S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..',
 '0':'-----','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....',
 '6':'-....','7':'--...','8':'---..','9':'----.'}
INV = {v:k for k,v in MORSE.items()}

def enc(txt):
    "letters -> space-separated Morse, one group per letter"
    return ' '.join(MORSE[c] for c in txt.upper() if c in MORSE)
def marks(txt):
    "letters -> the bare mark sequence, all inter-letter gaps removed"
    return ''.join(MORSE[c] for c in txt.upper() if c in MORSE)

def hr(t): print('\n' + t + '\n' + '-'*len(t))

# ---------------------------------------------------------------- 1. Morse --
hr('1. K0 slab messages rendered in International Morse (derived, not transcribed)')
MSGS = [
 ('SOS',                    'complete; a distress call, on its own slab'),
 ('RQ',                     'complete as marks; two letters, reading direction disputed'),
 ('LUCID',                  'complete'),
 ('MEMORY',                 'complete'),
 ('SHADOW',                 'complete'),
 ('FORCES',                 'complete'),
 ('VIRTUALLY',              'complete'),
 ('INVISIBLE',              'complete'),
 ('DIGETAL',                'as carved; one dit short of DIGITAL'),
 ('INTERPRETATIT',          'truncated word; == INTERPRETATU as marks'),
 ('TISYOUR',               'truncated at the left: "[WHA]T IS YOUR"'),
 ('POSITION',               'complete; partly obscured by the lodestone'),
 ('E',                      'the lone filler dit'),
]
for w, note in MSGS:
    print('  %-14s %-42s %s' % (w, enc(w), note))

hr('1a. DIGETAL vs DIGITAL: exactly one dit apart?')
a, b = marks('DIGETAL'), marks('DIGITAL')
print('  DIGETAL marks: %s  (%d marks)' % (a, len(a)))
print('  DIGITAL marks: %s  (%d marks)' % (b, len(b)))
print('  DIGITAL has exactly one extra dit, all else identical:',
      len(b) - len(a) == 1 and marks('DIG') + '.' == marks('DIGE') and
      marks('DIG') + '..' == marks('DIGI') and marks('TAL') == marks('TAL'))

hr('1b. INTERPRETATIT vs INTERPRETATU: identical marks, different letter gaps?')
x, y = marks('INTERPRETATIT'), marks('INTERPRETATU')
print('  INTERPRETATIT marks: %s' % x)
print('  INTERPRETATU  marks: %s' % y)
print('  identical mark sequence:', x == y)
print('  trailing groups differ only in spacing:  "%s" vs "%s"' % (enc('IT')[-4:], enc('U')))
z = marks('INTERPRETATAU')
print('  INTERPRETATAU marks: %s   identical to the other two: %s' % (z, z == x))

hr('1c. RQ vs YR: reverse of each other?')
p, q = marks('RQ'), marks('YR')
print('  RQ marks: %s' % p)
print('  YR marks: %s' % q)
print('  YR is RQ read backwards:', q == p[::-1])

hr('1d. Which messages are Morse palindromes (same read either way)?')
for w in ['SOS','RQ','YR','LUCID','MEMORY','SHADOW','FORCES','VIRTUALLY','INVISIBLE','E','EE','EEE']:
    m = marks(w)
    print('  %-10s %-24s palindrome: %s' % (w, m, m == m[::-1]))

hr('1e. Runs of filler dits are spacing-ambiguous: N dits = ?')
for n in range(1, 6):
    s = '.' * n
    print('  %d dit(s) "%s" -> as one letter: %-4s   as %d E\'s: %s'
          % (n, s, INV.get(s, '(none)'), n, 'E' * n))

# ------------------------------------------------------- 2. Mengenlehreuhr --
hr('2. Mengenlehreuhr arithmetic')
ROWS = (1, 4, 4, 11, 4)
print('  row lengths (seconds, 5h, 1h, 5min, 1min):', ROWS, ' total lamps:', sum(ROWS))
print('  value-bearing lamps (excluding the seconds lamp):', sum(ROWS) - 1)
def read(h, m):
    return (h // 5, h % 5, m // 5, m % 5)
mx = max(sum(read(h, m)) for h in range(24) for m in range(60))
arg = [(h, m) for h in range(24) for m in range(60) if sum(read(h, m)) == mx]
print('  max value lamps lit at once: %d  (first at %02d:%02d) -> with the seconds lamp, %d of 24'
      % (mx, arg[0][0], arg[0][1], mx + 1))
print('  so the 24 lamps are NEVER all lit simultaneously; the ceiling is %d' % (mx + 1))
for h, m in [(12, 32), (17, 54), (23, 59), (0, 0), (19, 0), (10, 31)]:
    c = read(h, m)
    print('  %02d:%02d -> rows lit %s  = %d*5+%d h, %d*5+%d min  = %02d:%02d  (%d lamps lit)'
          % (h, m, c, c[0], c[1], c[2], c[3], c[0]*5+c[1], c[2]*5+c[3], sum(c)))
print('  distinct minute states in a day: 24*60 =', 24*60,
      '; with the seconds lamp: x2 =', 24*60*2)
print('  5-hour row: max lit = %d of 4 (23//5);  1-hour row: max lit = %d of 4 (h mod 5)'
      % (max(read(h, 0)[0] for h in range(24)), max(read(h, 0)[1] for h in range(24))))
print('  but never both at 4: max hour lamps lit at once = %d of 8'
      % max(read(h, 0)[0] + read(h, 0)[1] for h in range(24)))
print('  minute rows: max = %d of 11 and %d of 4, both at :59 -> %d of 15'
      % (59//5, 59%5, 59//5 + 59%5))
print('  red quarter-hour lamps at 1-indexed positions 3,6,9 of the 11-lamp row'
      ' -> minute 15, 30, 45:', [3*5, 6*5, 9*5])

# ------------------------------------------------------------- 3. Bearings --
hr('3. Bearings')
import math
def init_bearing(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2); dl = math.radians(lon2 - lon1)
    y = math.sin(dl)*math.cos(p2)
    x = math.cos(p1)*math.sin(p2) - math.sin(p1)*math.cos(p2)*math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360
def final_bearing(a, b, c, d): return (init_bearing(c, d, a, b) + 180) % 360
def rhumb_bearing(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dpsi = math.log(math.tan(math.pi/4 + p2/2)/math.tan(math.pi/4 + p1/2))
    dl = math.radians(lon2 - lon1)
    if abs(dl) > math.pi: dl -= math.copysign(2*math.pi, dl)
    return (math.degrees(math.atan2(dl, dpsi)) + 360) % 360
def dist_km(lat1, lon1, lat2, lon2):
    R = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1; dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(a))
def dms(d, m, s): return d + m/60 + s/3600

P16 = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']
P32 = ['N','NbE','NNE','NEbN','NE','NEbE','ENE','EbN','E','EbS','ESE','SEbE','SE','SEbS','SSE','SbE',
       'S','SbW','SSW','SWbS','SW','SWbW','WSW','WbS','W','WbN','WNW','NWbW','NW','NWbN','NNW','NbW']
def point(deg, pts):
    step = 360/len(pts)
    return pts[int((deg + step/2) % 360 // step)]

KRY = (38.95227, -77.14573)
K2  = (dms(38, 57, 6.5), -dms(77, 8, 44))
TGT = {'Weltzeituhr, Alexanderplatz': (52.52117, 13.41333),
       'Mengenlehreuhr, Europa-Center': (52.50515, 13.33888),
       'Brandenburg Gate': (52.51627, 13.37770),
       'Berlin city centre': (52.52000, 13.40500)}
print('  K2 coordinates decimal: %.6f N, %.6f W' % (K2[0], -K2[1]))
print('  sculpture -> K2 coordinates: %.0f m on bearing %.1f deg (%s)'
      % (dist_km(*KRY, *K2)*1000, init_bearing(*KRY, *K2), point(init_bearing(*KRY, *K2), P16)))
print('  ENE as a compass bearing: 3 * 22.5 =', 3*22.5, 'deg;'
      ' 16-point ENE sector = [%.2f, %.2f]' % (67.5-11.25, 67.5+11.25))
for name, (la, lo) in TGT.items():
    ib, fb, rb = init_bearing(*KRY, la, lo), final_bearing(*KRY, la, lo), rhumb_bearing(*KRY, la, lo)
    print('  sculpture -> %-30s' % name)
    print('      great-circle initial %7.3f deg -> %-3s (16pt) / %-4s (32pt)' % (ib, point(ib, P16), point(ib, P32)))
    print('      great-circle final   %7.3f deg -> %-3s' % (fb, point(fb, P16)))
    print('      rhumb line (constant)%7.3f deg -> %-3s (16pt) / %-4s (32pt)' % (rb, point(rb, P16), point(rb, P32)))
    print('      distance %8.1f km' % dist_km(*KRY, la, lo))
wz = TGT['Weltzeituhr, Alexanderplatz']
print('  offset of the great-circle initial bearing from ENE (67.5): %+.3f deg'
      % (init_bearing(*KRY, *wz) - 67.5))
print('  offset of the great-circle initial bearing from NE  (45.0): %+.3f deg'
      % (init_bearing(*KRY, *wz) - 45.0))
print('  offset of the rhumb bearing from ENE (67.5): %+.3f deg; upper edge of the ENE sector is 78.75'
      % (rhumb_bearing(*KRY, *wz) - 67.5))


# ------------------------------------------------- 4. chance expectation ----
hr('4. Chance expectation for the lateral keystream sweep (uniform-random-key null)')
from math import comb
def p_at_least(k, n, p=1/26.0):
    return sum(comb(n, i) * p**i * (1-p)**(n-i) for i in range(k, n+1))
RUNS = [('block 1 (EASTNORTHEAST, 13 letters)', 13, 7, 16_538_496,
         'observed best = 6 mismatches, i.e. 7 of 13 matched'),
        ('block 2 (BERLINCLOCK, 11 letters)',   11, 6, 16_629_600,
         'observed best = 5 mismatches, i.e. 6 of 11 matched'),
        ('joint (both blocks, 24 letters)',     24, 8, 15_390_336,
         'observed best = 16 mismatches, i.e. 8 of 24 matched')]
for name, n, k, tests, note in RUNS:
    p = p_at_least(k, n)
    print('  %s' % name)
    print('      %s' % note)
    print('      E[matches] per alignment = %d/26 = %.3f' % (n, n/26.0))
    print('      P(>= %d matches | random key) = %.3e ; over %s alignments E[count] = %.1f'
          % (k, p, format(tests, ','), p*tests))
print('  A real fit needs 24 of 24. P(24/24 | random) = %.3e; over every alignment ever run'
      ' (%s) E[count] = %.3e' % (p_at_least(24, 24), format(48_697_953, ','),
                                 p_at_least(24, 24)*48_697_953))
print('  Threshold used by the sweep: block <= 2 mismatches, joint <= 4 mismatches.')
for name, n, k, tests, _ in RUNS:
    thr = n - (2 if n < 24 else 4)
    print('      %s: P(>= %d matches) = %.3e -> E[hits over %s] = %.3e'
          % (name, thr, p_at_least(thr, n), format(tests, ','), p_at_least(thr, n)*tests))


hr('5. Where the great circle to Berlin passes through the ENE bearing 67.5 deg')
def gc_interp(lat1, lon1, lat2, lon2, f):
    p1, l1, p2, l2 = map(math.radians, (lat1, lon1, lat2, lon2))
    d = 2*math.asin(math.sqrt(math.sin((p2-p1)/2)**2 +
                              math.cos(p1)*math.cos(p2)*math.sin((l2-l1)/2)**2))
    A, B = math.sin((1-f)*d)/math.sin(d), math.sin(f*d)/math.sin(d)
    x = A*math.cos(p1)*math.cos(l1) + B*math.cos(p2)*math.cos(l2)
    y = A*math.cos(p1)*math.sin(l1) + B*math.cos(p2)*math.sin(l2)
    z = A*math.sin(p1) + B*math.sin(p2)
    return math.degrees(math.atan2(z, math.hypot(x, y))), math.degrees(math.atan2(y, x))
prev = None
for i in range(1001):
    f = i/1000.0
    la, lo = gc_interp(*KRY, *wz, f)
    b = init_bearing(la, lo, *wz)
    if prev and prev < 67.5 <= b:
        print('  forward azimuth reaches ENE (67.5 deg) at %.1f%% of the way along,'
              ' at %.3f N %.3f W (North Atlantic)' % (f*100, la, -lo))
        break
    prev = b
la, lo = gc_interp(*KRY, *wz, 0.5)
print('  great-circle midpoint %.3f N %.3f W, forward azimuth there %.3f deg'
      % (la, -lo, init_bearing(la, lo, *wz)))
print('  azimuth is monotone: %.3f (start) -> %.3f (mid) -> %.3f (arrival)'
      % (init_bearing(*KRY, *wz), init_bearing(la, lo, *wz), final_bearing(*KRY, *wz)))
