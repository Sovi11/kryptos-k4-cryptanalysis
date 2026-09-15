"""(c, completion) Conjugated-matrix ADFGVX: fractionate with square 1,
columnar-transpose the coordinate stream, recombine pairs through an
INDEPENDENT square 2.

matrix_f_adfgvx.py answers the single-square case (all UNSAT, widths 2-7).
Using two independent squares roughly doubles the free variables, so it is the
fair generalisation to test before declaring the family closed.
"""
import itertools
import json
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matrix_common import CT, CRIBS, N, A2Z
from matrix_f_adfgvx import columnar_src, UF, ALPH25, ALPH36
from ortools.sat.python import cp_model

HERE = os.path.dirname(os.path.abspath(__file__))
_QG = json.load(open(os.path.join(HERE, ".quadgrams_cache.json")))
_Q, _FL = _QG["q"], _QG["floor"]
def qscore(t):
    return sum(_Q.get(t[i:i + 4], _FL) for i in range(len(t) - 3)) / max(1, len(t) - 3)

OUT = []
def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUT.append(s)

P("=" * 78)
P("(c completion) CONJUGATED-MATRIX ADFGVX -- two independent unknown squares")
P("=" * 78)


def encrypt2(pt, sq1, sq2, w, perm):
    Z = []
    for ch in pt:
        r, c = sq1[ch]
        Z += [r, c]
    src = columnar_src(len(Z), w, perm)
    Y = [Z[i] for i in src]
    inv2 = {v: k for k, v in sq2.items()}
    return "".join(inv2[(Y[2 * j], Y[2 * j + 1])] for j in range(len(pt)))


def decrypt2(ct, sq1, sq2, w, perm):
    Y = []
    for ch in ct:
        r, c = sq2[ch]
        Y += [r, c]
    src = columnar_src(len(Y), w, perm)
    Z = [None] * len(Y)
    for t, i in enumerate(src):
        Z[i] = Y[t]
    inv1 = {v: k for k, v in sq1.items()}
    return "".join(inv1[(Z[2 * i], Z[2 * i + 1])] for i in range(len(ct)))


def build2(ct, cribs, alph, w, perm):
    src = columnar_src(2 * len(ct), w, perm)
    cp = dict(cribs)
    uf = UF()
    for sy in alph:
        for tag in ("1", "2"):
            uf.find("r" + tag + sy)
            uf.find("c" + tag + sy)
    n = 0
    for j in range(len(ct)):
        for k, t in ((0, 2 * j), (1, 2 * j + 1)):
            i = src[t]
            m, par = i // 2, i % 2
            if m in cp:
                uf.union(("r" if k == 0 else "c") + "2" + ct[j],
                         ("r" if par == 0 else "c") + "1" + cp[m])
                n += 1
    return uf, n


def solve2(uf, alph, d, timeout=5.0):
    m = cp_model.CpModel()
    cls = {}
    def V(nm):
        r = uf.find(nm)
        if r not in cls:
            cls[r] = m.NewIntVar(0, d - 1, "c%d" % len(cls))
        return cls[r]
    for tag in ("1", "2"):
        cells = []
        for sy in alph:
            v = m.NewIntVar(0, d * d - 1, "")
            m.Add(v == d * V("r" + tag + sy) + V("c" + tag + sy))
            cells.append(v)
        m.AddAllDifferent(cells)
    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = timeout
    sv.parameters.num_search_workers = 1
    st = sv.Solve(m)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        sq = {}
        for tag in ("1", "2"):
            sq[tag] = {sy: (sv.Value(cls[uf.find("r" + tag + sy)]),
                            sv.Value(cls[uf.find("c" + tag + sy)])) for sy in alph}
        return sq
    if st == cp_model.INFEASIBLE:
        return "unsat"
    return "unknown"


P("\nValidation (synthetic two-square instance must be recovered as SAT):")
rng = random.Random(21)
for d, alph in ((5, ALPH25), (6, ALPH36)):
    for w in (3, 5):
        cells = [(a, b) for a in range(d) for b in range(d)]
        rng.shuffle(cells); sq1 = dict(zip(alph, cells))
        cells = cells[:]; rng.shuffle(cells); sq2 = dict(zip(alph, cells))
        perm = list(range(w)); rng.shuffle(perm)
        pt = list(rng.choice(alph) for _ in range(N))
        for pos, _, l in CRIBS:
            pt[pos] = l if l in alph else "I"
        pt = "".join(pt)
        ct2 = encrypt2(pt, sq1, sq2, w, perm)
        assert decrypt2(ct2, sq1, sq2, w, perm) == pt
        cr = [(pos, pt[pos]) for pos, _, _ in CRIBS]
        uf, na = build2(ct2, cr, alph, w, perm)
        mm = solve2(uf, alph, d)
        good = isinstance(mm, dict) and all(
            decrypt2(ct2, mm["1"], mm["2"], w, perm)[pos] == l for pos, l in cr)
        P("  d=%d w=%d: round trip ok, %d constraints -> %s, cribs reproduced %s"
          % (d, w, na, "sat" if isinstance(mm, dict) else mm, good))
        assert good
ufb = UF(); ufb.union("r1A", "r1B"); ufb.union("c1A", "c1B")
P("  contradictory instance -> %s (expect unsat)" % solve2(ufb, ALPH25, 5))

CT_IJ = CT.replace("J", "I")
CR25 = [(pos, ("I" if l == "J" else l)) for pos, _, l in CRIBS]
CR36 = [(pos, l) for pos, _, l in CRIBS]
ENGPOOL = "".join(ch * f for ch, f in zip(A2Z, [82, 15, 28, 43, 127, 22, 20, 61, 70, 2, 8,
                                                40, 24, 67, 75, 19, 1, 60, 63, 91, 28, 10,
                                                24, 2, 20, 1]))

P("\nEXHAUSTIVE over every columnar key of width 2..7 (%d keys):"
  % sum(math.factorial(w) for w in range(2, 8)))
for d, alph, ct, cribs in ((5, ALPH25, CT_IJ, CR25), (6, ALPH36, CT, CR36)):
    t0 = time.time()
    nsat = nunsat = nunk = 0
    best = []
    for w in range(2, 8):
        for perm in itertools.permutations(range(w)):
            uf, na = build2(ct, cribs, alph, w, list(perm))
            mm = solve2(uf, alph, d)
            if isinstance(mm, dict):
                nsat += 1
                txt = decrypt2(ct, mm["1"], mm["2"], w, list(perm))
                okc = all(txt[pos] == l for pos, l in cribs)
                best.append((qscore(txt), w, perm, okc, txt))
            elif mm == "unsat":
                nunsat += 1
            else:
                nunk += 1
    best.sort(reverse=True)
    P("  %dx%d: %d configs, SAT %d / UNSAT %d / unknown %d  (%.0fs)"
      % (d, d, nsat + nunsat + nunk, nsat, nunsat, nunk, time.time() - t0))
    for sc, w, perm, okc, txt in best[:5]:
        P("     w=%d key=%s cribs=%s %.3f %s" % (w, "".join(map(str, perm)), okc, sc, txt))
    rr = random.Random(7 + d)
    ns = nt = 0
    for _ in range(2):
        rc = [(pos, rr.choice(ENGPOOL)) for pos, _ in cribs]
        for w in range(2, 8):
            for perm in itertools.permutations(range(w)):
                uf, _ = build2(ct, rc, alph, w, list(perm))
                nt += 1
                if isinstance(solve2(uf, alph, d), dict):
                    ns += 1
    P("     chance baseline: %d/%d SAT = %.4f  (observed %.4f)"
      % (ns, nt, ns / nt, nsat / (nsat + nunsat + nunk)))

rb = sorted(qscore("".join(random.Random(1000 + i).choice(A2Z) for _ in range(97)))
            for i in range(2000))
P("\nrandom-text quadgram baseline (2000 draws): median %.3f  99th %.3f  max %.3f"
  % (rb[1000], rb[1980], rb[-1]))

with open(os.path.join(HERE, "matrix_g_output.txt"), "w") as f:
    f.write("\n".join(OUT) + "\n")
print("\n[written to matrix_g_output.txt]")
