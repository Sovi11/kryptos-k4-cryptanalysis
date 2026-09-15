"""(e) Rotor / Enigma-like systems: the fixed-point argument, verified and quantified.

A reflector-based rotor machine (Enigma in every variant, Typex, and any cipher whose
step permutation is a fixed-point-free involution, e.g. Porta and Playfair) can NEVER
encipher a letter to itself.  If K4 contains even one crib position where ciphertext
letter == plaintext letter, the whole family is dead with probability exactly 1.

This script (1) re-derives the crib letters straight from the data files rather than
trusting any transcription, (2) counts self-maps, (3) checks robustness to the cribs
being misplaced, and (4) states the information-theoretic reason why a keystream
machine WITHOUT a reflector (M-209, SIGABA) is not testable from 24 crib letters.
"""
import math
import sys
from collections import Counter

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from matrix_common import CT, CRIBS, N, A2Z

out = []
def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.append(s)

P("=" * 78)
P("(e) ROTOR / ENIGMA-LIKE SYSTEMS")
P("=" * 78)

# ---------------------------------------------------------------- 1. verify
P("\n1. Crib letters re-derived from data/k4_ciphertext.txt + data/cribs.json")
P("   ciphertext length:", len(CT))
P("   pos(1-idx)  ct  pt   self-map?")
selfmaps = []
for pos0, c, p in CRIBS:
    flag = "  <== SELF-MAP" if c == p else ""
    if c == p:
        selfmaps.append((pos0 + 1, c))
    P("   %4d        %s   %s%s" % (pos0 + 1, c, p, flag))
P("   total crib letters:", len(CRIBS))
P("   self-maps found:", selfmaps)

# belt and braces: index the raw file string directly
raw = open("/Users/pravarkataria/Desktop/crypto/kryptos/data/k4_ciphertext.txt").read().strip()
P("\n   direct check, raw[32] (1-indexed 33) =", repr(raw[32]),
  "and EASTNORTHEAST[33-22] =", repr("EASTNORTHEAST"[33 - 22]))
P("   direct check, raw[73] (1-indexed 74) =", repr(raw[73]),
  "and BERLINCLOCK[74-64] =", repr("BERLINCLOCK"[74 - 64]))
assert raw[32] == "S" == "EASTNORTHEAST"[33 - 22]
assert raw[73] == "K" == "BERLINCLOCK"[74 - 64]
P("   VERIFIED: two independent self-maps, S->S at 33 and K->K at 74.")

# ---------------------------------------------------------------- 2. verdict
P("\n2. Verdict")
P("   Under any cipher whose per-position permutation has no fixed point,")
P("   P(observe >=1 self-map in 24 crib letters) = 0 exactly.")
P("   We observe 2.  => Enigma (all wheel/reflector/plugboard settings, all")
P("   models incl. M3, M4, Zahlwerk, Abwehr), Typex, Porta and Playfair are")
P("   ruled out with certainty, independently of key, rotor wiring, ring")
P("   settings, plugboard and stepping.  No search is required or meaningful.")

lam = 24 / 26.0
p_ge2 = 1 - math.exp(-lam) * (1 + lam)
P("\n   Conversely the observation is entirely unremarkable for an UNRESTRICTED")
P("   cipher: expected self-maps = 24/26 = %.3f, P(>=2) ~ %.3f (Poisson)." % (lam, p_ge2))
P("   So the self-maps neither support nor weaken any non-reflector hypothesis.")

# ---------------------------------------------------------------- 3. robustness
P("\n3. Robustness: would the conclusion survive a misplaced crib?")
words = [("EAST", 22), ("NORTHEAST", 26), ("BERLIN", 64), ("CLOCK", 70)]
P("   (a) whole crib block shifted by d (all four words together):")
rows = []
for d in range(-6, 7):
    tot = 0
    ok = True
    for w, p in words:
        s = p - 1 + d
        if s < 0 or s + len(w) > N:
            ok = False
            break
        tot += sum(1 for i, ch in enumerate(w) if CT[s + i] == ch)
    rows.append((d, tot if ok else None))
P("       shift  self-maps")
for d, t in rows:
    P("       %+5d  %s" % (d, "out of range" if t is None else t))

P("   (b) each word slid independently over every legal position 1..97:")
for w, _ in words:
    cnt = Counter()
    for s in range(N - len(w) + 1):
        k = sum(1 for i, ch in enumerate(w) if CT[s + i] == ch)
        cnt[k] += 1
    tot = sum(cnt.values())
    zero = cnt[0]
    P("       %-10s placements=%2d  with 0 self-maps=%2d (%.0f%%)  dist=%s"
      % (w, tot, zero, 100.0 * zero / tot, dict(sorted(cnt.items()))))
P("   Honest caveat: the rule-out is contingent on Sanborn's announced positions.")
P("   A random placement of one word is self-map-free 67-83 pct of the time, and six")
P("   of the thirteen whole-block shifts in [-6,+6] happen to be self-map-free")
P("   (d = -6,-3,-2,+3,+5,+6).  So the argument is NOT robust to the cribs being")
P("   misplaced -- it is robust to nothing except the cribs being right.  Since")
P("   the positions are Sanborn's own and have been restated by him repeatedly,")
P("   that is a good enough footing, but it should be stated rather than hidden.")

# ---------------------------------------------------------------- 4. non-reflector
P("\n4. Rotor machines WITHOUT a reflector are not excluded -- and not testable")
P("   M-209 / C-38 (the US Army converter Scheidt's generation trained on) is a")
P("   Beaufort machine, C = (k - P) mod 26, so self-maps are allowed and the two")
P("   observed self-maps are no objection.  But its keystream is generated by 6")
P("   pin wheels of periods 26,25,23,21,19,17 (lcm = 101,405,850), so over 97")
P("   letters it is effectively aperiodic: no repeat constraint exists at all.")
pins = 26 + 25 + 23 + 21 + 19 + 17
lugbits = 27 * math.log2(22)          # 27 bars, each with 0,1 or 2 lugs on 6 wheels
offbits = math.log2(26 * 25 * 23 * 21 * 19 * 17)
cribbits = 24 * math.log2(26)
P("   key entropy:   pins %d bits + lugs %.0f bits + wheel offsets %.0f bits = %.0f bits"
  % (pins, lugbits, offbits, pins + lugbits + offbits))
P("   crib evidence: 24 letters x log2(26) = %.0f bits" % cribbits)
P("   %.0f >> %.0f, so consistent M-209 settings are guaranteed to exist by pure"
  % (pins + lugbits + offbits, cribbits))
P("   counting (~2^%.0f of them) and finding one would prove nothing."
  % (pins + lugbits + offbits - cribbits))
P("   The same argument applies to SIGABA (15 rotors, no reflector, ~2^95 key)")
P("   and to any one-time-pad-like keystream.  These families are UNFALSIFIABLE")
P("   from the cribs; they can only ever be attacked through the plaintext.")
P("   That is the honest boundary of what crib-consistency testing can do.")

with open("/Users/pravarkataria/Desktop/crypto/kryptos/analysis/matrix_e_output.txt", "w") as f:
    f.write("\n".join(out) + "\n")
