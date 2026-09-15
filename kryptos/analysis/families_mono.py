"""Monoalphabetic substitution sanity check on the K4 cribs.

Lists every cipher-letter -> plain-letter pair implied by the four cribs and every conflict
in either direction (one cipher letter to two plain letters, or two cipher letters to one plain
letter -- both impossible for a bijective simple substitution).  Also checks the Caesar/affine
(c = a*p + b) subfamily and simple transposition (letter multiset) for completeness.
"""
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from k4_common import A2Z, CT, CRIB, CRIB_POS, ROOT, KRYPTOS_ALPHA

pairs = [(i + 1, CT[i], CRIB[i]) for i in CRIB_POS]
print("crib pairs (1-indexed position: cipher -> plain):")
print("  " + ", ".join(f"{p}:{c}->{t}" for p, c, t in pairs))

c2p = defaultdict(set)
p2c = defaultdict(set)
for _, c, t in pairs:
    c2p[c].add(t)
    p2c[t].add(c)
conf_c = {c: sorted(v) for c, v in c2p.items() if len(v) > 1}
conf_p = {t: sorted(v) for t, v in p2c.items() if len(v) > 1}
print("\ncipher letters that would have to decrypt to two or more different plain letters:")
for c, v in sorted(conf_c.items()):
    print(f"  {c} -> {v}   at positions {[p for p, cc, _ in pairs if cc == c]}")
print("plain letters that would have to come from two or more different cipher letters (bijection violated):")
for t, v in sorted(conf_p.items()):
    print(f"  {v} -> {t}   at positions {[p for p, _, tt in pairs if tt == t]}")
print(f"\n{len(conf_c)} forward conflicts, {len(conf_p)} reverse conflicts -> simple substitution ruled out.")
selfmap = [(p, c) for p, c, t in pairs if c == t]
print(f"letters mapped to themselves (fine for substitution in general, fatal for Playfair/Porta): {selfmap}")

# affine c = a*p + b under both alphabets
aff = []
for aname, alpha in (("straight", A2Z), ("kryptos", KRYPTOS_ALPHA)):
    inv = {ch: i for i, ch in enumerate(alpha)}
    for a in range(26):
        for b in range(26):
            if all((a * inv[t] + b) % 26 == inv[c] for _, c, t in pairs):
                aff.append((aname, a, b))
print(f"affine/Caesar fits (both alphabets, 1352 keys): {aff or 'none'}")

# pure transposition: plaintext letters must be a sub-multiset of the ciphertext letters
ctc = Counter(CT)
ptc = Counter(CRIB.values())
short = {L: (ptc[L], ctc[L]) for L in ptc if ptc[L] > ctc[L]}
print(f"pure transposition (no substitution): crib letter counts exceeding ciphertext supply: {short or 'none'}")
print("  crib letters:", dict(sorted(ptc.items())))
print("  ciphertext  :", dict(sorted(ctc.items())))
if short:
    print("  -> a pure transposition of the 97 letters cannot yield these cribs.")

with open(os.path.join(ROOT, "findings", "mono_results.json"), "w") as f:
    json.dump({"pairs": pairs, "forward_conflicts": conf_c, "reverse_conflicts": conf_p, "self_map": selfmap,
               "affine_fits": aff, "transposition_shortfall": short}, f, indent=1)
