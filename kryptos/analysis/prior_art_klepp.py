#!/usr/bin/env python3
"""Forensic audit of the mattklepp/k4 claim (repo now 404; README recovered
from the Wayback Machine snapshot 2026-05-28).

The README's own numbers are the audit: a base formula shift(i) = (4i+20) mod 26
that it says hits 7/24 cribs, then 24 hand-listed 'position-specific corrections'
-- exactly one free parameter per crib -- that bring it to 24/24.  We reproduce
both halves and then measure how much information the corrections actually carry.
"""
CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
CRIBS = [(22, "EAST"), (26, "NORTHEAST"), (64, "BERLIN"), (70, "CLOCK")]
pairs = []           # (0-indexed position, ct letter, pt letter)
for pos, w in CRIBS:
    for j, ch in enumerate(w):
        pairs.append((pos-1+j, CT[pos-1+j], ch))

A = ord('A')
req = {i: (ord(c) - ord(p)) % 26 for i, c, p in pairs}   # shift that must be subtracted

print("required shift (C-P) mod 26 at each 0-indexed crib position:")
print("  ", {i: req[i] for i in sorted(req)})

# base formula from the README
base = {i: (4*i + 20) % 26 for i in range(97)}
hit = [i for i in sorted(req) if base[i] == req[i]]
print(f"\nbase formula (4i+20) mod 26 alone: {len(hit)}/24 crib positions correct "
      f"(README claims 7/24 = 29.2%)  -> positions {hit}")
print(f"chance expectation for any fixed shift schedule: 24/26 = 0.92 hits")

# the corrections the README lists, in its own 0-indexed 'Pos' numbering
# keys are the README's own 'Pos' labels, which are 0-indexed
corr = {21:+1, 22:+7, 23:-9, 24:-10,
        25:+13, 26:+8, 27:0, 28:-4, 29:0, 30:-8, 31:-4, 32:+8, 33:+3,
        63:0, 64:+4, 65:+4, 66:+12, 67:+9, 68:0,
        69:0, 70:0, 71:-1, 72:-9, 73:0}
print(f"\nREADME lists {len(corr)} corrections for {len(req)} crib positions "
      f"-> {len(corr)}/{len(req)} free parameters per constraint.")
ok = sum(1 for i in req if (base[i] + corr.get(i, 0)) % 26 == req[i])
print(f"base + listed corrections: {ok}/24 correct  (as advertised)")

# how many distinct correction values? if the corrections were a real rule they
# would be predictable from position; measure that directly.
vals = sorted(set(corr.values()))
print(f"\ncorrection values used: {vals}")
print("residual after removing base formula, as a function of position:")
for i in sorted(req):
    print(f"   pos {i:>2}  ct {CT[i]}  pt {dict((x,z) for x,_,z in pairs)[i]}  "
          f"required {req[i]:>2}  base {base[i]:>2}  correction {corr.get(i,0):>+3}")

print("""
VERDICT
  The 24 corrections are exactly the 24 residuals req(i) - base(i).  They are not
  derived from anything; they are defined to close the gap at the only 24
  positions where the answer is already published.  The model therefore has as
  many free parameters as data points and zero degrees of freedom left over, so
  its '100% accuracy on all 24 known constraint positions' is a tautology, not
  evidence.  At the other 73 positions the model is unconstrained, and the
  plaintext the README prints there --
    UDILKAFSGDMZLYQJCVNJA ... OPOHAYLOMIQSDZSSHTQNSXYMEMNBT ... SYRUFZRDSPQKKQZIKAGIWQD
  -- is not English.""")
