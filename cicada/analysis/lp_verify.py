"""Verify parser and table: reproduce published LP2 statistics and decrypt the solved page 56."""
from collections import Counter
from lp_common import *

def primes(n):
    out, c = [], 2
    while len(out) < n:
        if all(c % p for p in out if p * p <= c): out.append(c)
        c += 1
    return out

s, brk = lp2_unsolved()
d = sum(1 for i in range(1, len(s)) if s[i] == s[i-1])
c = Counter(s)
exp = sum(v*v for v in c.values()) / len(s)
print(f"unsolved LP2 runes: {len(s)}   (published 12,956)")
print(f"doublets: {d}   (published 86)   expected ~{exp:.1f}")
print(f"normalized IoC: {ioc(s):.3f}  (published 0.999)")
pairs = [i for i in range(1, len(s)) if not brk[i]]
print(f"within-word doublets: {sum(s[i]==s[i-1] for i in pairs)} of {len(pairs)} pairs (published 63 / 10,056)")

P = primes(500)
for variant in ("skipF", "noskip"):
    out, k = [], 0
    for b in section_runes("73.jpg"):
        for kind, v in tokens(b):
            if kind == "sep": out.append(" "); continue
            if variant == "skipF" and v == 0: out.append("F"); continue
            out.append(LATIN[(v - (P[k] - 1)) % 29]); k += 1
        out.append(" / ")
    print(f"\npage 56 decrypt ({variant}):\n  " + "".join(out)[:300])
