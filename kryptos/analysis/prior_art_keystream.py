#!/usr/bin/env python3
"""If the circulating K4 plaintext is genuine, the keystream is fully determined.
This script derives it under every standard alphabet/rule combination and asks
whether it has any recognisable structure -- period, Gromark-style recurrence,
or a match to text carved on the sculpture.

This is the concrete payoff of the 2025 archive recovery for method-hunting,
and it is testable without ever trusting the plaintext: if NO combination
yields structure, either the plaintext is wrong or the mechanism is not a
letter-wise shift over a fixed pair of alphabets.
"""
from collections import Counter
from itertools import product

CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
PT = "THECOMPASSROSEISHEREXEASTNORTHEASTTHISISYOURPOSITIONXCOMMISSIONBERLINCLOCKWHICHISNORTHEASTOFHEREX"
assert len(CT) == len(PT) == 97
CRIBS = [(22,"EAST"),(26,"NORTHEAST"),(64,"BERLIN"),(70,"CLOCK")]
assert all(PT[p-1:p-1+len(w)] == w for p, w in CRIBS), "plaintext fails the Sanborn cribs"
STR = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KEY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
ALPH = {"straight": STR, "kryptos": KEY}

def keystream(rule, Apt, Act):
    ks = []
    for c, p in zip(CT, PT):
        ci, pi = Act.index(c), Apt.index(p)
        if rule == "vig":  k = (ci - pi) % 26
        elif rule == "bea": k = (ci + pi) % 26
        else:               k = (pi - ci) % 26
        ks.append(k)
    return ks

def ic(seq):
    n = len(seq); c = Counter(seq)
    return sum(v*(v-1) for v in c.values())/(n*(n-1))

def best_period(ks):
    """for each p, fraction of residue classes that are constant, and the
    mean pairwise agreement within classes (a real period shows ~1.0)."""
    out = []
    for p in range(2, 49):
        agree = tot = 0
        for r in range(p):
            cls = ks[r::p]
            for i in range(len(cls)):
                for j in range(i+1, len(cls)):
                    tot += 1
                    agree += (cls[i] == cls[j])
        if tot: out.append((agree/tot, p))
    out.sort(reverse=True)
    return out[:4]

def gromark_check(ks):
    """Gromark: key digits satisfy k[i] = k[i-n] + k[i-n+1] (mod base).
    Test every primer length n and base b for a lagged-Fibonacci recurrence."""
    hits = []
    for n in range(2, 16):
        for b in (10, 26):
            kk = [x % b for x in ks]
            ok = sum(1 for i in range(n, 97) if kk[i] == (kk[i-n] + kk[i-n+1]) % b)
            hits.append((ok/(97-n), n, b))
    hits.sort(reverse=True)
    return hits[:4]

print("Derived keystreams for the circulating plaintext\n" + "="*70)
rows = []
for rule, (pn, Ap), (cn, Ac) in product(("vig","bea","var"), ALPH.items(), ALPH.items()):
    ks = keystream(rule, Ap, Ac)
    letters = "".join(STR[k] for k in ks)
    rows.append((rule, pn, cn, ks, letters))
    print(f"\n{rule}/pt={pn}/ct={cn}")
    print(f"  keystream as letters: {letters}")
    print(f"  distinct values {len(set(ks))}/26, IoC {ic(ks):.4f} (flat random 0.0385, English 0.066)")
    print(f"  best periods (agreement, p): {[(f'{a:.2f}',p) for a,p in best_period(ks)]}")
    print(f"  best Gromark recurrence (frac, primer_len, base): {[(f'{a:.2f}',n,b) for a,n,b in gromark_check(ks)]}")

print("\n" + "="*70)
print("running-key test: does any derived keystream appear verbatim in the sculpture text?")
import re, os
panel = ""
p = "data/sculpture_panels.txt"
if os.path.exists(p):
    panel = "".join(ch for ch in open(p).read() if ch.isalpha())
k1k2k3 = "".join(ch for ch in open("data/k1_k3_plaintext.txt").read() if ch.isalpha()) if os.path.exists("data/k1_k3_plaintext.txt") else ""
corpus = {"panels_all": panel, "k1k2k3_pt_file": k1k2k3}
found = 0
for rule, pn, cn, ks, letters in rows:
    for name, txt in corpus.items():
        for L in (97, 24, 13, 11):
            sub = letters[:L]
            if L < 97:
                continue
            if sub and sub in txt:
                print(f"  MATCH {rule}/{pn}/{cn} len{L} in {name}")
                found += 1
print(f"  full-length (97) verbatim matches: {found}")
print("""
NOTE ON WHAT THIS PROVES
  The keystream is derived, not tested: any plaintext whatsoever produces one.
  What is informative is whether it has structure.  Flat IoC, no period with
  agreement near 1.0, and no lagged-Fibonacci recurrence together mean that IF
  this plaintext is the real one, the mechanism is NOT a letter-wise shift with
  a periodic or Gromark keystream over these alphabets.""")

# --------------------------------------------------------------------------
# FALSIFICATION TEST OF THE CIRCULATING RECONSTRUCTION
# Bean/Materna found that at the 24 CRIB positions, plaintext letters drawn
# from {K,R,Y,P,T,O,S} move very little in the ciphertext (mean |P-C| = 2.10,
# vs 8.67 for random).  That anomaly was measured on the 24 positions Sanborn
# published.  If the circulating 97-letter reconstruction is the real plaintext,
# the SAME anomaly should appear at the 73 positions Sanborn never published,
# because the encryption mechanism does not know which letters were leaked.
# If it does not, the anomaly is either a 24-letter fluke or the reconstruction
# is wrong.
import random
random.seed(7)
A = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def lin(a, b): return abs(ord(a) - ord(b))
def circ(a, b):
    d = abs(ord(a) - ord(b)) % 26
    return min(d, 26 - d)

crib_idx = set()
for pos, w in CRIBS:
    crib_idx.update(range(pos-1, pos-1+len(w)))
rest_idx = [i for i in range(97) if i not in crib_idx]
KSET = set("KRYPTOS")

print("\n" + "="*70)
print("FALSIFICATION TEST: does the Bean/Materna displacement anomaly extend\n"
      "from the 24 published crib positions to the 73 unpublished ones?\n")

def report(label, idxs, subset=None):
    sel = [(PT[i], CT[i]) for i in idxs if (subset is None or PT[i] in subset)]
    if not sel:
        print(f"  {label}: no positions"); return
    ml = sum(lin(p, c) for p, c in sel)/len(sel)
    mc = sum(circ(p, c) for p, c in sel)/len(sel)
    T, hits = 100_000, 0
    for _ in range(T):
        v = sum(lin(p, random.choice(A)) for p, _ in sel)/len(sel)
        if v <= ml: hits += 1
    print(f"  {label}: n={len(sel):>3}  mean|P-C| linear {ml:5.2f} (rand 8.67)  "
          f"circular {mc:5.2f} (rand 6.50)   P(random<=obs) = {hits/T:.4f}")

print(" all plaintext letters")
report("  24 published crib positions ", sorted(crib_idx))
report("  73 unpublished positions    ", rest_idx)
report("  all 97 positions            ", range(97))
print("\n Materna subset: plaintext letter in {K,R,Y,P,T,O,S}")
report("  24 published crib positions ", sorted(crib_idx), KSET)
report("  73 unpublished positions    ", rest_idx, KSET)
report("  all 97 positions            ", range(97), KSET)

print("""
READING THIS
  If the anomaly is a property of the cipher, the 73-position row should look
  like the 24-position row.  If the 73-position row sits at the random level,
  then either (a) the published cribs are statistically unrepresentative --
  which would itself be a strong clue, since Sanborn chose which words to leak
  -- or (b) the circulating reconstruction is not the true plaintext.""")
