"""(c, continued) ADFGVX and fractionate-transpose-recombine, unknown square.

matrix_d_fractionation.py settles bifid/trifid with an unknown square.  ADFGVX
is the other half of the fractionation question a 1988 primer would contain.

  F1  classic ADFGVX / ADFGX are excluded outright, on two independent counts
  F2  the only 26-letter-output generalisation -- fractionate, columnar-
      transpose the coordinate stream, recombine pairs through the square --
      as a CSP over the unknown square, EXHAUSTIVE over every columnar key of
      width 2..7, with the full decryption of every SAT model scored
  F3  the counting boundary for wide/arbitrary transpositions
"""
import itertools
import json
import math
import os
import random
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matrix_common import CT, CRIBS, N, A2Z
from ortools.sat.python import cp_model

OUT = []
def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUT.append(s)

HERE = os.path.dirname(os.path.abspath(__file__))
_QG = json.load(open(os.path.join(HERE, ".quadgrams_cache.json")))
_Q, _FL = _QG["q"], _QG["floor"]
def qscore(t):
    return sum(_Q.get(t[i:i + 4], _FL) for i in range(len(t) - 3)) / max(1, len(t) - 3)

P("=" * 78)
P("(c continued) ADFGVX / FRACTIONATE-TRANSPOSE-RECOMBINE, UNKNOWN SQUARE")
P("=" * 78)

# ---------------------------------------------------------------- F1
P("\nF1. CLASSIC ADFGVX AND ADFGX ARE EXCLUDED OUTRIGHT")
P("    ADFGVX ciphertext is written in the six letters A D F G V X (ADFGX: five,")
P("    A D F G X).  Two independent counts kill it:")
P("      (1) alphabet.  K4 uses %d distinct letters, all 26 of them:"
  % len(set(CT)))
P("          %s" % " ".join("%s%d" % (c, Counter(CT)[c]) for c in sorted(set(CT))))
P("          Letters outside {A,D,F,G,V,X} in K4: %d of 97 (%.0f%%)."
  % (sum(1 for c in CT if c not in "ADFGVX"), 100 * sum(1 for c in CT if c not in "ADFGVX") / 97))
P("      (2) parity.  ADFGVX emits exactly two symbols per plaintext letter, so")
P("          its ciphertext length is EVEN.  K4 is 97 letters, odd.  Even with a")
P("          hypothetical 26-symbol coordinate alphabet the length could not be 97.")
P("    Both hold for every square, every transposition key and every key width,")
P("    so no search is required.")

# ---------------------------------------------------------------- F2
P("\nF2. THE 26-LETTER GENERALISATION: fractionate -> columnar transposition of")
P("    the coordinate stream -> recombine pairs through the SAME square.")
P("    This is the only way to get 97 letters over a 26-letter alphabet out of")
P("    an ADFGVX-shaped pipeline, and it is exactly 'bifid with a keyed columnar")
P("    interleave' instead of bifid's fixed period.  The square is UNKNOWN.")

ALPH25 = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
ALPH36 = A2Z + "0123456789"


def columnar_src(nsym, w, perm):
    """src[t] = index in the input stream that lands at output index t."""
    rows = (nsym + w - 1) // w
    out = []
    for c in perm:
        for r in range(rows):
            i = r * w + c
            if i < nsym:
                out.append(i)
    return out


def encrypt(pt, square, w, perm):
    Z = []
    for ch in pt:
        r, c = square[ch]
        Z += [r, c]
    src = columnar_src(len(Z), w, perm)
    Y = [Z[i] for i in src]
    inv = {v: k for k, v in square.items()}
    return "".join(inv[(Y[2 * j], Y[2 * j + 1])] for j in range(len(pt)))


def decrypt(ct, square, w, perm):
    Y = []
    for ch in ct:
        r, c = square[ch]
        Y += [r, c]
    src = columnar_src(len(Y), w, perm)
    Z = [None] * len(Y)
    for t, i in enumerate(src):
        Z[i] = Y[t]
    inv = {v: k for k, v in square.items()}
    return "".join(inv[(Z[2 * i], Z[2 * i + 1])] for i in range(len(ct)))


P("\n    Validation:")
rng = random.Random(13)
ok = True
for d, alph in ((5, ALPH25), (6, ALPH36)):
    cells = [(a, b) for a in range(d) for b in range(d)]
    for w in (2, 3, 5, 7, 11):
        rng.shuffle(cells)
        sq = dict(zip(alph, cells))
        perm = list(range(w))
        rng.shuffle(perm)
        pt = "".join(rng.choice(alph) for _ in range(N))
        ok &= decrypt(encrypt(pt, sq, w, perm), sq, w, perm) == pt
P("      round trip encrypt/decrypt, 5x5 and 6x6, widths 2,3,5,7,11: %s" % ok)
assert ok


class UF:
    def __init__(self):
        self.p = {}
    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


def build(ct, cribs, alph, d, w, perm):
    """Returns (uf, n_active) for this configuration."""
    src = columnar_src(2 * len(ct), w, perm)
    cribpos = {pos: l for pos, l in cribs}
    uf = UF()
    for sy in alph:
        uf.find("r" + sy)
        uf.find("c" + sy)
    n = 0
    for j in range(len(ct)):
        for k, t in ((0, 2 * j), (1, 2 * j + 1)):
            i = src[t]
            m, par = i // 2, i % 2
            if m in cribpos:
                uf.union(("r" if k == 0 else "c") + ct[j],
                         ("r" if par == 0 else "c") + cribpos[m])
                n += 1
    return uf, n


def solve(uf, alph, d, timeout=10.0):
    m = cp_model.CpModel()
    cls = {}
    def V(nm):
        r = uf.find(nm)
        if r not in cls:
            cls[r] = m.NewIntVar(0, d - 1, "c%d" % len(cls))
        return cls[r]
    cells = []
    for sy in alph:
        v = m.NewIntVar(0, d * d - 1, "")
        m.Add(v == d * V("r" + sy) + V("c" + sy))
        cells.append(v)
    m.AddAllDifferent(cells)
    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = timeout
    sv.parameters.num_search_workers = 1
    st = sv.Solve(m)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {sy: (sv.Value(cls[uf.find("r" + sy)]), sv.Value(cls[uf.find("c" + sy)]))
                for sy in alph}
    if st == cp_model.INFEASIBLE:
        return "unsat"
    return "unknown"


# synthetic-key recovery
P("      synthetic-key recovery (encrypt with a known square + key, then ask the")
P("      solver for a square from the 24 crib letters only):")
for d, alph in ((5, ALPH25), (6, ALPH36)):
    for w in (4, 6):
        cells = [(a, b) for a in range(d) for b in range(d)]
        rng.shuffle(cells)
        sq = dict(zip(alph, cells))
        perm = list(range(w)); rng.shuffle(perm)
        pt = list(rng.choice(alph) for _ in range(N))
        for pos, _, l in CRIBS:
            pt[pos] = l if l in alph else "I"
        pt = "".join(pt)
        ct2 = encrypt(pt, sq, w, perm)
        cr = [(pos, pt[pos]) for pos, _, _ in CRIBS]
        uf, na = build(ct2, cr, alph, d, w, perm)
        mm = solve(uf, alph, d)
        good = isinstance(mm, dict) and all(decrypt(ct2, mm, w, perm)[pos] == l for pos, l in cr)
        P("        d=%d w=%d: %d active constraints -> %s, cribs reproduced %s"
          % (d, w, na, "sat" if isinstance(mm, dict) else mm, good))
        assert isinstance(mm, dict) and good
uf_bad = UF()
uf_bad.union("rA", "rB"); uf_bad.union("cA", "cB")
P("        contradictory instance -> %s (expect unsat)" % solve(uf_bad, ALPH25, 5))

CT_IJ = CT.replace("J", "I")
CRIBS25 = [(pos, ("I" if l == "J" else l)) for pos, _, l in CRIBS]
CRIBS36 = [(pos, l) for pos, _, l in CRIBS]

ENGPOOL = "".join(ch * f for ch, f in zip(A2Z, [82, 15, 28, 43, 127, 22, 20, 61, 70, 2, 8,
                                                40, 24, 67, 75, 19, 1, 60, 63, 91, 28, 10,
                                                24, 2, 20, 1]))

P("\n    EXHAUSTIVE over every columnar key of width 2..7 (%d keys), both squares."
  % sum(math.factorial(w) for w in range(2, 8)))
summary = []
for d, alph, ct, cribs in ((5, ALPH25, CT_IJ, CRIBS25), (6, ALPH36, CT, CRIBS36)):
    t0 = time.time()
    nsat = nunsat = nunk = 0
    act = []
    best = []
    for w in range(2, 8):
        for perm in itertools.permutations(range(w)):
            uf, na = build(ct, cribs, alph, d, w, list(perm))
            act.append(na)
            mm = solve(uf, alph, d, timeout=5.0)
            if isinstance(mm, dict):
                nsat += 1
                txt = decrypt(ct, mm, w, list(perm))
                okc = all(txt[pos] == l for pos, l in cribs)
                best.append((qscore(txt), w, perm, okc, txt))
            elif mm == "unsat":
                nunsat += 1
            else:
                nunk += 1
    best.sort(reverse=True)
    P("      %dx%d square: %d configurations, SAT %d / UNSAT %d / unknown %d,"
      " %.0fs" % (d, d, nsat + nunsat + nunk, nsat, nunsat, nunk, time.time() - t0))
    P("        active crib constraints per configuration: min %d mean %.1f max %d"
      % (min(act), sum(act) / len(act), max(act)))
    if best:
        P("        best decryptions by quadgram score (English ~ -5.6, random ~ -8.2):")
        for sc, w, perm, okc, txt in best[:6]:
            P("          w=%d key=%s cribs=%s  %.3f  %s"
              % (w, "".join(str(x) for x in perm), okc, sc, txt))
        P("        score distribution: min %.3f median %.3f max %.3f"
          % (best[-1][0], best[len(best) // 2][0], best[0][0]))
    summary.append((d, nsat, nunsat, nunk, best[0][0] if best else None))

    # chance baseline: same enumeration, random English plaintext at the crib slots
    rr = random.Random(88 + d)
    ns = nt = 0
    for _ in range(3):
        rc = [(pos, rr.choice(ENGPOOL)) for pos, _ in cribs]
        for w in range(2, 8):
            for perm in itertools.permutations(range(w)):
                uf, _na = build(ct, rc, alph, d, w, list(perm))
                nt += 1
                if isinstance(solve(uf, alph, d, timeout=5.0), dict):
                    ns += 1
    P("        chance baseline: 3 random-plaintext crib sets over the same %d keys"
      % (nt // 3))
    P("          -> %d/%d SAT = %.3f (observed %.3f)" % (ns, nt, ns / nt, nsat / (nsat + nunsat + nunk)))

rb = []
_r = random.Random(4242)
for _ in range(4000):
    rb.append(qscore("".join(_r.choice(A2Z) for _ in range(97))))
rb.sort()
P("\n    random-text quadgram baseline (4000 draws): median %.3f  99th %.3f  max %.3f"
  % (rb[2000], rb[3960], rb[-1]))

# ---------------------------------------------------------------- F3
P("\nF3. THE COUNTING BOUNDARY FOR WIDE OR ARBITRARY TRANSPOSITIONS")
P("    Historical ADFGVX keys were 15-22 letters wide; 15! = %.2e and 22! = %.2e"
  % (math.factorial(15), math.factorial(22)))
P("    are beyond enumeration, and an ARBITRARY permutation of the 194-symbol")
P("    coordinate stream has 194! = 10^%d members."
  % int(sum(math.log10(i) for i in range(1, 195))))
P("    Information check: the cribs carry 24 * log2(26) = %.0f bits." % (24 * math.log2(26)))
P("    A 6x6 square carries log2(36!) = %.0f bits; a width-15 columnar key"
  % math.log2(math.factorial(36)))
P("    log2(15!) = %.0f bits; a free permutation log2(194!) = %.0f bits."
  % (math.log2(math.factorial(15)), sum(math.log2(i) for i in range(1, 195))))
P("    Key entropy exceeds the crib evidence by a factor of %.0f even in the"
  % ((math.log2(math.factorial(36)) + math.log2(math.factorial(15))) / (24 * math.log2(26))))
P("    narrowest historical case, so consistent (square, key) pairs are")
P("    GUARANTEED to exist by counting alone and finding one proves nothing.")
P("    Wide-key ADFGVX is therefore not falsifiable from the cribs -- the same")
P("    boundary matrix_e_rotor.py documents for the M-209 and SIGABA.  What IS")
P("    settled: classic ADFGVX/ADFGX (F1), and every narrow key, width 2-7 (F2).")

with open(os.path.join(HERE, "matrix_f_output.txt"), "w") as f:
    f.write("\n".join(OUT) + "\n")
print("\n[written to matrix_f_output.txt]")
