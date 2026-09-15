#!/usr/bin/env python3
"""Mechanical test of the Naughton/Grok-3 recipe for K4.

Stated recipe (Feb 2025): reverse the ciphertext, apply Vigenere with key
KRYPTOS, reverse the result.  We test that literally and then generously
broaden it: every combination of {reverse-in?, reverse-out?} x {Vigenere,
Beaufort, variant-Beaufort} x {straight, KRYPTOS-keyed alphabets on pt/ct/key}
x every rotation of the key x the keys KRYPTOS/PALIMPSEST/ABSCISSA.

Round-trip regression: the same engine must reproduce the real K1 ciphertext
from the real K1 plaintext with key PALIMPSEST and KRYPTOS-keyed alphabets.
"""
import itertools

CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
CRIBS = [(22, "EAST"), (26, "NORTHEAST"), (64, "BERLIN"), (70, "CLOCK")]
STRAIGHT = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KEYED = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

K1_PT = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
K1_CT = "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD"

def enc(pt, key, rule, A_pt, A_ct, A_key):
    out = []
    for i, ch in enumerate(pt):
        p = A_pt.index(ch); k = A_key.index(key[i % len(key)])
        if rule == "vig":  c = (p + k) % 26
        elif rule == "bea": c = (k - p) % 26
        else:               c = (p - k) % 26
        out.append(A_ct[c])
    return "".join(out)

def dec(ct, key, rule, A_pt, A_ct, A_key):
    out = []
    for i, ch in enumerate(ct):
        c = A_ct.index(ch); k = A_key.index(key[i % len(key)])
        if rule == "vig":  p = (c - k) % 26
        elif rule == "bea": p = (k - c) % 26
        else:               p = (c + k) % 26
        out.append(A_pt[p])
    return "".join(out)

# --- regression ---
assert enc(K1_PT, "PALIMPSEST", "vig", KEYED, KEYED, KEYED) == K1_CT, "K1 regression failed"
assert dec(K1_CT, "PALIMPSEST", "vig", KEYED, KEYED, KEYED) == K1_PT, "K1 round-trip failed"
print("regression: K1 encrypt+decrypt with PALIMPSEST / KRYPTOS alphabets OK\n")

def score(pt):
    n = 0
    for pos, w in CRIBS:
        n += sum(1 for a, b in zip(pt[pos-1:pos-1+len(w)], w) if a == b)
    return n

def exact(pt):
    return all(pt[pos-1:pos-1+len(w)] == w for pos, w in CRIBS)

# --- the literal stated recipe ---
lit = dec(CT[::-1], "KRYPTOS", "vig", STRAIGHT, STRAIGHT, STRAIGHT)[::-1]
print("LITERAL Naughton recipe (straight alphabets, reverse-Vigenere-reverse):")
print("  ", lit)
print(f"   cribs {score(lit)}/24, exact={exact(lit)}")
for pos, w in CRIBS:
    print(f"     {pos}: want {w:<9} got {lit[pos-1:pos-1+len(w)]}")
print()

# --- generous sweep ---
keys = ["KRYPTOS", "PALIMPSEST", "ABSCISSA"]
alphas = {"straight": STRAIGHT, "keyed": KEYED}
best = []
tested = 0
for key in keys:
    for rot in range(len(key)):
        k = key[rot:] + key[:rot]
        for rule in ("vig", "bea", "var"):
            for ap, Ap in alphas.items():
                for ac, Ac in alphas.items():
                    for ak, Ak in alphas.items():
                        for rin in (False, True):
                            for rout in (False, True):
                                src = CT[::-1] if rin else CT
                                pt = dec(src, k, rule, Ap, Ac, Ak)
                                if rout: pt = pt[::-1]
                                tested += 1
                                s = score(pt)
                                best.append((s, key, rot, rule, ap, ac, ak, rin, rout, pt))
best.sort(key=lambda t: -t[0])
print(f"generous sweep: {tested} configurations (keys x rotations x rules x 8 alphabet combos x reverse flags)")
print(f"exact 24/24 fits: {sum(1 for b in best if b[0]==24)}")
print("top 5 by crib agreement (chance expectation for 24 crib letters = 24/26 = 0.92):")
for b in best[:5]:
    s,key,rot,rule,ap,ac,ak,rin,rout,pt = b
    print(f"  {s}/24  key={key} rot={rot} {rule} pt={ap} ct={ac} key_a={ak} revin={rin} revout={rout}")
    print(f"        {pt}")
