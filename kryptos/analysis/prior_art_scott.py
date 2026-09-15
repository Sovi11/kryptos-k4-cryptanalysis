#!/usr/bin/env python3
"""Mechanical re-test of the 'Scott' Quagmire-3 + linear-congruence route
reported on numberworld.blog (Schridde, 2020): Quagmire III with alphabet
keyword KRYPTOS and key EMUFPHZLRFA, then a positional transposition
y = 77 + 38x (mod 97) taken from the K2 coordinates.

The blog's own summary is that this puts BERLIN at the right place but
gives PEEK, not CLOCK, after it.  We check all four Sanborn cribs.
"""
CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
CRIBS = [(22, "EAST"), (26, "NORTHEAST"), (64, "BERLIN"), (70, "CLOCK")]
KEYED = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STRAIGHT = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def quag3_dec(ct, key, A):
    """Quagmire III: same keyed alphabet for pt and ct; key letter indexes into it."""
    out = []
    for i, ch in enumerate(ct):
        c = A.index(ch); k = A.index(key[i % len(key)])
        out.append(A[(c - k) % 26])
    return "".join(out)

def score(pt):
    return sum(1 for pos, w in CRIBS for a, b in zip(pt[pos-1:pos-1+len(w)], w) if a == b)

def report(tag, pt):
    ok = all(pt[p-1:p-1+len(w)] == w for p, w in CRIBS)
    print(f"{tag}")
    print(f"   {pt}")
    print(f"   cribs {score(pt)}/24  exact={ok}")
    for p, w in CRIBS:
        print(f"     {p:>3} want {w:<9} got {pt[p-1:p-1+len(w)]}")
    print()

base = quag3_dec(CT, "EMUFPHZLRFA", KEYED)
report("Quagmire III, alphabet KRYPTOS, key EMUFPHZLRFA (no transposition):", base)

# linear congruence y = 77 + 38x mod 97, both read directions, 0- and 1-indexed
for a, b in [(38, 77)]:
    for oneidx in (False, True):
        for direction in ("gather", "scatter"):
            out = [None]*97
            for x in range(97):
                xi = x + 1 if oneidx else x
                y = (b + a*xi) % 97
                if direction == "gather":
                    out[x] = base[y]
                else:
                    out[y] = base[x]
            pt = "".join(out)
            report(f"y={b}+{a}x mod 97, {'1' if oneidx else '0'}-indexed, {direction}:", pt)

# generous sweep over all (a,b) with gcd(a,97)=1, both directions, both indexings
best = []
for a in range(1, 97):
    for b in range(97):
        for oneidx in (False, True):
            for direction in ("gather", "scatter"):
                out = [None]*97
                for x in range(97):
                    xi = x + 1 if oneidx else x
                    y = (b + a*xi) % 97
                    if direction == "gather": out[x] = base[y]
                    else: out[y] = base[x]
                pt = "".join(out)
                best.append((score(pt), a, b, oneidx, direction, pt))
best.sort(key=lambda t: -t[0])
n = len(best)
print(f"generous sweep of all {n} linear-congruence transpositions of the same Quagmire-3 output")
print(f"exact 24/24: {sum(1 for x in best if x[0]==24)}")
print("top 3:")
for s,a,b,oi,d,pt in best[:3]:
    print(f"  {s}/24  y={b}+{a}x, 1idx={oi}, {d}")
    print(f"        {pt}")
# chance: each crib letter matches with prob 1/26 under a random permutation-ish model
from math import comb
p = 1/26
pmf = [comb(24,k)*p**k*(1-p)**(24-k) for k in range(25)]
tail = lambda k: sum(pmf[k:])
print(f"\nchance expectation: E[matches]=24/26={24/26:.2f}; over {n} trials expected count with >=5 matches = {tail(5)*n:.1f}, >=7 = {tail(7)*n:.3f}, >=10 = {tail(10)*n:.2e}")
