#!/usr/bin/env python3
"""Independent re-derivation of the statistics Richard Bean reports in
'Cryptodiagnosis of Kryptos K4' (HistoCrypt 2021/2022).

Checked here:
  1. IC = 0.03608
  2. 10 repeated bigrams, no repeated trigrams
  3. repeated-bigram count when the CT is written at width 21 (Bean: ~1 in 6750)
  4. A->{L,K}, C->{M,P}, L->{V,Z}: mean |distance| in A-Z = 3.6 (Bean: ~1 in 240)
  5. all crib pairs with d(Pi,Pj)<=1 -> mean d(Ci,Cj) = 3.8 (Bean: ~1 in 5000)
  6. Materna: crib PT letters in KRYPTOS move mean distance 2.1 (Bean: ~1 in 5500)
All significance figures are recomputed by Monte-Carlo over random permutations
of the 97 ciphertext letters (for 1-3) or random bijective substitutions (4-6).
"""
import random
from collections import Counter
from itertools import combinations

CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
PAIRS = list(zip("EAST"+"NORTHEAST"+"BERLIN"+"CLOCK", "FLRV"+"QQPRNGKSS"+"NYPVTT"+"MZFPK"))
random.seed(20260912)
N = 200_000

def ic(s):
    n = len(s); c = Counter(s)
    return sum(v*(v-1) for v in c.values()) / (n*(n-1))

def ngram_reps(s, n):
    c = Counter(s[i:i+n] for i in range(len(s)-n+1))
    return sum(v-1 for v in c.values() if v > 1)

def col_bigrams(s, w):
    """bigrams read down the columns when text is written in rows of width w"""
    rows = [s[i:i+w] for i in range(0, len(s), w)]
    out = []
    for r in range(len(rows)-1):
        for c in range(min(len(rows[r]), len(rows[r+1]))):
            out.append(rows[r][c] + rows[r+1][c])
    return out

def rep_col_bigrams(s, w):
    c = Counter(col_bigrams(s, w))
    return sum(v-1 for v in c.values() if v > 1)

print(f"1. IC = {ic(CT):.5f}   (Bean: 0.03608)")
print(f"2. repeated bigrams (linear): {ngram_reps(CT,2)};  repeated trigrams: {ngram_reps(CT,3)}   (Bean: 10, 0)")

obs21 = rep_col_bigrams(CT, 21)
lst = list(CT)
cnt = 0
for _ in range(N):
    random.shuffle(lst)
    if rep_col_bigrams("".join(lst), 21) >= obs21: cnt += 1
print(f"3. column-bigram repeats at width 21: observed {obs21}; "
      f"P(random permutation >= obs) = {cnt/N:.5f}  ~ 1 in {N/max(cnt,1):.0f}   (Bean: ~1 in 6750)")

def circ(a, b):
    d = abs(ord(a)-ord(b)) % 26
    return min(d, 26-d)

def lin(a, b):
    return abs(ord(a)-ord(b))

# map PT letter -> set of CT letters it becomes
m = {}
for p, c in PAIRS: m.setdefault(p, set()).add(c)
multi = {p: sorted(v) for p, v in m.items() if len(v) > 1}
print(f"\n4. plaintext letters with more than one ciphertext image: {multi}")
ds = [lin(v[0], v[1]) for v in multi.values()]
print(f"   linear A-Z distances {ds}, mean {sum(ds)/len(ds):.2f}   (Bean: 3.6)")

# Monte Carlo: random bijection A-Z, measure the same statistic on the same PT multiset
alpha = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
def mc_multi(trials=N):
    hits = 0
    obs = sum(ds)/len(ds)
    for _ in range(trials):
        # a random "polyalphabetic" assignment: each crib position gets an independent random CT letter
        rnd = {}
        for p in multi:
            rnd[p] = [random.choice(alpha) for _ in range(2)]
        v = [lin(x[0], x[1]) for x in rnd.values()]
        if sum(v)/len(v) <= obs: hits += 1
    return hits/trials
p4 = mc_multi(50_000)
print(f"   P(random CT assignment gives mean <= observed) = {p4:.5f} ~ 1 in {1/max(p4,1e-9):.0f}   (Bean: ~1 in 240)")

# 5. all crib pairs with d(Pi,Pj)<=1
sel = [(i, j) for i, j in combinations(range(len(PAIRS)), 2) if lin(PAIRS[i][0], PAIRS[j][0]) <= 1]
d5 = [lin(PAIRS[i][1], PAIRS[j][1]) for i, j in sel]
obs5 = sum(d5)/len(d5)
print(f"\n5. crib pairs with |Pi-Pj|<=1: {len(sel)} pairs, mean |Ci-Cj| = {obs5:.2f}   (Bean: 3.8)")
hits = 0
T = 50_000
for _ in range(T):
    rc = [random.choice(alpha) for _ in PAIRS]
    v = [lin(rc[i], rc[j]) for i, j in sel]
    if sum(v)/len(v) <= obs5: hits += 1
print(f"   P(random) = {hits/T:.5f} ~ 1 in {T/max(hits,1):.0f}   (Bean: ~1 in 5000)")

# 6. Materna: crib PT letters that are in KRYPTOS
KSET = set("KRYPTOS")
sel6 = [(p, c) for p, c in PAIRS if p in KSET]
d6 = [lin(p, c) for p, c in sel6]
obs6 = sum(d6)/len(d6)
print(f"\n6. Materna: crib positions whose PT letter is in KRYPTOS: {len(sel6)}; mean |P-C| = {obs6:.2f}   (Bean: 2.1)")
hits = 0
for _ in range(T):
    v = [lin(p, random.choice(alpha)) for p, _ in sel6]
    if sum(v)/len(v) <= obs6: hits += 1
print(f"   P(random) = {hits/T:.5f} ~ 1 in {T/max(hits,1):.0f}   (Bean: ~1 in 5500)")
print(f"\n   all crib positions mean |P-C| = {sum(lin(p,c) for p,c in PAIRS)/len(PAIRS):.2f} "
      f"(expected for random ~8.67)")

# ---------------------------------------------------------------- addendum
# Cleaner version of the "small displacement" phenomenon, which is the one
# result here that is both large and directly exploitable.
print("\n" + "="*70)
print("ADDENDUM: displacement statistic, stated precisely\n")
disp = [(ord(c)-ord(p)) % 26 for p, c in PAIRS]
print("signed shift (C-P) mod 26 at the 24 crib positions:")
print("  ", disp)
lind = [lin(p, c) for p, c in PAIRS]
cird = [circ(p, c) for p, c in PAIRS]
print(f"mean |C-P| linear   = {sum(lind)/24:.3f}   (uniform-random expectation 8.667)")
print(f"mean |C-P| circular = {sum(cird)/24:.3f}   (uniform-random expectation 6.500)")
T = 200_000
h_lin = h_cir = 0
for _ in range(T):
    rc = [random.choice(alpha) for _ in PAIRS]
    if sum(lin(PAIRS[i][0], rc[i]) for i in range(24))/24 <= sum(lind)/24: h_lin += 1
    if sum(circ(PAIRS[i][0], rc[i]) for i in range(24))/24 <= sum(cird)/24: h_cir += 1
print(f"P(random <= observed), linear   = {h_lin/T:.5f}  ~ 1 in {T/max(h_lin,1):.0f}")
print(f"P(random <= observed), circular = {h_cir/T:.5f}  ~ 1 in {T/max(h_cir,1):.0f}")

# repeated-PT-letter spread, all variants
print("\nspread of ciphertext images of a repeated plaintext letter:")
for name, f in (("linear", lin), ("circular", circ)):
    vals = []
    for p, imgs in sorted(multi.items()):
        for a, b in combinations(imgs, 2):
            vals.append(f(a, b))
    print(f"  {name}: n={len(vals)} pairs, mean {sum(vals)/len(vals):.2f} "
          f"(uniform expectation {8.667 if name=='linear' else 6.5:.2f})")
    hits = 0
    for _ in range(50_000):
        rv = []
        for p, imgs in sorted(multi.items()):
            r = [random.choice(alpha) for _ in imgs]
            for a, b in combinations(r, 2): rv.append(f(a, b))
        if sum(rv)/len(rv) <= sum(vals)/len(vals): hits += 1
    print(f"           P(random) = {hits/50_000:.5f} ~ 1 in {50_000/max(hits,1):.0f}")
