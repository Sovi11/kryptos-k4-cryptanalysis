"""geo2 (c): the lag-7 autocorrelation spike (9 coincidences in 90 pairs, z = +3.04).

Is it real or is it the maximum of 96 correlated tests?  Establish the null distribution of
max_lag z for 97-letter strings, both uniform-random and random permutations of K4's own
letter multiset (the correct null: a transposition/substitution of K4 keeps the multiset).

Then, if anything survives, ask what a period-7 structure could be, given that a period-7
ADDITIVE key is flatly contradicted by the cribs (17 collisions, 0 of 12 pairings consistent):
  * a general period-7 POLYALPHABETIC with seven independent arbitrary mixed alphabets --
    strictly more general than Quagmire I-IV, and not previously tested;
  * the 7-residue structure of the six doubled letters.
"""
import random, math
from collections import Counter
import geo2_common as G
import geometry_common as g

CT, CRIB, N = G.CT, G.CRIB, G.N
rng = random.Random(7717)

def autocorr_z(s, lag):
    n = len(s) - lag
    c = sum(1 for i in range(n) if s[i] == s[i + lag])
    exp = n / 26.0
    return (c - exp) / math.sqrt(n * (1 / 26.0) * (25 / 26.0)), c, n

print('=' * 78)
print('1. OBSERVED')
print('=' * 78)
obs = {lag: autocorr_z(CT, lag) for lag in range(1, N)}
for lo, hi, label in ((1, 96, 'all lags 1..96'), (1, 48, 'lags 1..48 (>=49 pairs)'),
                      (1, 30, 'lags 1..30 (>=67 pairs)'), (1, 20, 'lags 1..20')):
    mx = max(range(lo, hi + 1), key=lambda l: obs[l][0])
    print('  %-26s max z = %+.3f at lag %d (%d coincidences / %d pairs)'
          % (label, obs[mx][0], mx, obs[mx][1], obs[mx][2]))

print('\n=' * 1 + '=' * 77)
print('2. NULL DISTRIBUTION OF THE MAXIMUM z  (the multiple-testing question)')
print('=' * 78)
POOL = list(CT)
TRIALS = 200000
def run_null(sampler, name, ranges):
    maxima = {r: [] for r in ranges}
    for _ in range(TRIALS):
        s = sampler()
        zs = {}
        hi_needed = max(r[1] for r in ranges)
        for lag in range(1, hi_needed + 1):
            n = N - lag
            c = 0
            for i in range(n):
                if s[i] == s[i + lag]:
                    c += 1
            zs[lag] = (c - n / 26.0) / math.sqrt(n * (1 / 26.0) * (25 / 26.0))
        for r in ranges:
            maxima[r].append(max(zs[l] for l in range(r[0], r[1] + 1)))
    print('  %s (%d trials):' % (name, TRIALS))
    for r in ranges:
        v = sorted(maxima[r])
        obs_max = max(obs[l][0] for l in range(r[0], r[1] + 1))
        pval = sum(1 for x in v if x >= obs_max - 1e-9) / len(v)
        print('    lags %2d..%2d : null max-z mean %+.2f, 95th %+.2f, 99th %+.2f ; '
              'observed %+.2f -> p = %.4f'
              % (r[0], r[1], sum(v) / len(v), v[int(.95 * len(v))], v[int(.99 * len(v))],
                 obs_max, pval))
    return maxima

RANGES = [(1, 96), (1, 48), (1, 30), (7, 7)]
run_null(lambda: [rng.choice(g.PLAIN) for _ in range(N)], 'uniform random 26-letter strings', RANGES)
def shuf():
    rng.shuffle(POOL)
    return POOL
run_null(shuf, "random permutations of K4's own 97 letters (the transposition null)", RANGES)

print('\n' + '=' * 78)
print('3. WHERE THE LAG-7 COINCIDENCES ARE')
print('=' * 78)
pairs = [(i + 1, i + 8, CT[i]) for i in range(N - 7) if CT[i] == CT[i + 7]]
print('  the 9 coincident pairs (1-indexed):', pairs)
print('  positions of the first member mod 7:', sorted(Counter(p[0] % 7 for p in pairs).items()))
inside = [p for p in pairs if all(22 <= x <= 34 or 64 <= x <= 74 for x in p[:2])]
print('  pairs lying entirely inside a crib region: %d' % len(inside))
first_half = [p for p in pairs if p[1] <= 48]
print('  pairs in the first half (both <=48): %d ; second half: %d'
      % (len(first_half), len(pairs) - len(first_half)))
print('  removing the 24 crib letters and recomputing lag-7 on what is left is not')
print('  meaningful (it changes the spacing), so instead: lag-7 coincidences among the')
print('  73 NON-crib positions only (both members non-crib): %d of %d such pairs'
      % (sum(1 for i in range(N - 7)
             if (i + 1) not in CRIB and (i + 8) not in CRIB and CT[i] == CT[i + 7]),
         sum(1 for i in range(N - 7) if (i + 1) not in CRIB and (i + 8) not in CRIB)))

print('\n' + '=' * 78)
print('4. WHAT A PERIOD-7 STRUCTURE WOULD HAVE TO BE')
print('=' * 78)
print('  (a) additive period-7 key (Vigenere / Beaufort / variant-Beaufort, either alphabet')
print('      on either side).  The 24 cribs occupy only 7 residues, so there are 17')
print('      constraints; chance of passing = 26^-17 = %.2g.' % 26.0 ** -17)
for cmb in G.COMBOS:
    r = g.periodic_crib_test(CT, CRIB, 7, *cmb)
    assert not r['consistent']
print('      all 12 pairings inconsistent (verified).  Worst-case detail for vig/plain/plain:')
r = g.periodic_crib_test(CT, CRIB, 7, 'vig', 'plain', 'plain')
print('      conflicting residues ->', r['conflicts'])

print('\n  (b) GENERAL period-p polyalphabetic: p INDEPENDENT, arbitrary mixed alphabets')
print('      (strictly more general than Quagmire I-IV, which force all p alphabets to be')
print('      rotations of one mixed alphabet).  The only crib constraint is that within each')
print('      residue class the ct->pt map be a partial BIJECTION.  Tested p = 2..31 on the')
print('      97 letters and on the 93-letter body.')
def general_poly_ok(text, cribs, p):
    """Returns (ok, n_fwd_conflicts, n_rev_conflicts)."""
    fwd = {}
    rev = {}
    nf = nr = 0
    for pos, pt in sorted(cribs.items()):
        r = (pos - 1) % p
        c = text[pos - 1]
        if fwd.setdefault((r, c), pt) != pt:
            nf += 1
        if rev.setdefault((r, pt), c) != c:
            nr += 1
    return (nf == 0 and nr == 0), nf, nr
BODY = CT[4:]
BODYCRIB = {pos - 4: pt for pos, pt in CRIB.items()}
print('      p : 97-letter (ok, fwd-conflicts, rev-conflicts) | 93-letter body')
for p in range(2, 32):
    a = general_poly_ok(CT, CRIB, p)
    b = general_poly_ok(BODY, BODYCRIB, p)
    mark = ''
    if a[0] or b[0]:
        mark = '   <-- survives'
    print('      %2d : %-22s | %-22s%s' % (p, a, b, mark))
print('      NOTE: a general period-p polyalphabetic has p x 26 free parameters and only 24')
print('      crib letters, so surviving this test is nearly automatic once p is large; it is')
print('      a NECESSARY condition, not evidence.  The informative fact is which small p')
print('      are KILLED by it, because those are killed for every possible alphabet set.')

print('\n  (c) the six doubled letters and the modulus 7')
dbl = [i + 1 for i in range(N - 1) if CT[i] == CT[i + 1]]
print('      doubled-letter start positions:', dbl)
best_m, best_sz = None, 0
for m in range(2, 49):
    sz = max(Counter(d % m for d in dbl).values())
    if sz > best_sz or (sz == best_sz and best_m is None):
        best_sz, best_m = sz, m
print('      largest single residue class over all moduli m=2..48: %d of 6 at m=%d'
      % (best_sz, best_m))
print('      residues mod 7:', sorted(Counter(d % 7 for d in dbl).items()))
T = 200000
cnt = 0
cnt7 = 0
for _ in range(T):
    s = rng.sample(range(1, N), 6)
    mx = max(max(Counter(d % m for d in s).values()) for m in range(2, 49))
    if mx >= best_sz:
        cnt += 1
    if max(Counter(d % 7 for d in s).values()) >= 5:
        cnt7 += 1
print('      null (6 uniform positions in 1..96, %d trials):' % T)
print('        P(some modulus 2..48 collects >= %d of the 6) = %.4f   <-- the honest,'
      % (best_sz, cnt / T))
print('          multiple-testing-corrected p-value for this observation')
print('        P(modulus 7 alone collects >= 5 of the 6)     = %.4f   (the naive p-value)'
      % (cnt7 / T))
