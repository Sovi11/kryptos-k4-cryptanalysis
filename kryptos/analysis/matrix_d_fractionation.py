"""(d) Fractionation with an UNKNOWN square, solved as a constraint problem.

Prior work only tried keyword-derived squares.  Here the square itself is the
unknown and the cribs are the constraints, so a negative result covers ALL
squares (25! = 1.55e25 for 5x5, 36! = 3.7e41 for 6x6, 27! = 1.1e28 for trifid).

Why this is a clean CSP.  In Delastelle's bifid the whole ciphertext is known,
so for a block of length L starting at s the interleaved coordinate sequence
    Z = [row(y_1), col(y_1), row(y_2), col(y_2), ...]        (length 2L)
is known *as a function of the square*, and the plaintext letter at offset i is
    x_i = cell( Z_i , Z_{L+i} ).
Every crib therefore becomes two equalities between coordinate variables:
    row[P] == (row|col)[y_a]     and     col[P] == (row|col)[y_b]
with y_a, y_b concrete ciphertext letters.  Add the bijection (all 25/27/36
cells distinct) and hand it to z3.  Same construction for trifid (three
coordinates) and for the conjugated-matrix variant (two independent squares).
"""
import itertools
import os
import random
import sys
import time
from collections import defaultdict

import z3
from ortools.sat.python import cp_model

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matrix_common import CT, CRIBS, N, A2Z

out = []
def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.append(s)


# ------------------------------------------------------------------ geometry
def bifid_sources(p, n=N):
    """pos -> ((kind, ctpos), (kind, ctpos)) giving the row- and col-coordinate
    of the plaintext letter at `pos`, each as a coordinate of a ciphertext letter."""
    res = {}
    s = 0
    while s < n:
        L = min(p, n - s)
        def zsrc(t):                       # t = 1..2L
            j = (t + 1) // 2
            return ("r" if t % 2 else "c", s + j - 1)
        for i in range(1, L + 1):
            res[s + i - 1] = (zsrc(i), zsrc(L + i))
        s += L
    return res


def trifid_sources(p, n=N):
    res = {}
    s = 0
    while s < n:
        L = min(p, n - s)
        def zsrc(t):                       # t = 1..3L
            j = (t + 2) // 3
            k = t - 3 * (j - 1)            # 1,2,3
            return ("abc"[k - 1], s + j - 1)
        for i in range(1, L + 1):
            res[s + i - 1] = (zsrc(i), zsrc(L + i), zsrc(2 * L + i))
        s += L
    return res


# ------------------------------------------------------------------ reference impl (validation)
def bifid_encrypt(pt, square, side, period):
    """square: symbol -> (r,c).  Returns ciphertext."""
    inv = {v: k for k, v in square.items()}
    outp = []
    for s in range(0, len(pt), period):
        blk = pt[s:s + period]
        L = len(blk)
        rows = [square[ch][0] for ch in blk]
        cols = [square[ch][1] for ch in blk]
        Z = rows + cols
        for j in range(L):
            outp.append(inv[(Z[2 * j], Z[2 * j + 1])])
    return "".join(outp)


def trifid_encrypt(pt, cube, period):
    inv = {v: k for k, v in cube.items()}
    outp = []
    for s in range(0, len(pt), period):
        blk = pt[s:s + period]
        L = len(blk)
        A = [cube[ch][0] for ch in blk]
        B = [cube[ch][1] for ch in blk]
        C = [cube[ch][2] for ch in blk]
        Z = A + B + C
        for j in range(L):
            outp.append(inv[(Z[3 * j], Z[3 * j + 1], Z[3 * j + 2])])
    return "".join(outp)


# ------------------------------------------------------------------ solver
#
# The crib constraints are pure EQUALITIES between coordinate variables, so we
# first collapse them with union-find.  What is left for z3 is only the
# bijection: assign a value in [0, side) to each equivalence class such that the
# |alphabet| resulting (row, col) [or (a,b,c)] tuples are all distinct.  This is
# a far smaller problem than handing z3 the equalities directly and it solves in
# milliseconds instead of timing out.

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


def _solve_classes_z3(uf, tuples, side, timeout_ms):
    """Reference solver (z3).  Kept as a cross-check; it is slow on 6x6."""
    S = z3.Solver()
    S.set("timeout", timeout_ms)
    cls = {}
    def V(name):
        r = uf.find(name)
        if r not in cls:
            v = z3.Int("c%d" % len(cls))
            cls[r] = v
            S.add(v >= 0, v < side)
        return cls[r]
    for group in tuples:
        exprs = []
        for tup in group:
            e = 0
            for name in tup:
                e = e * side + V(name)
            exprs.append(e)
        S.add(z3.Distinct(exprs))
    res = S.check()
    if res == z3.sat:
        m = S.model()
        return {r: m[v].as_long() for r, v in cls.items()}, uf
    return (None if res == z3.unsat else "unknown"), uf


def _solve_classes_cpsat(uf, tuples, side, timeout_ms):
    """Primary solver: OR-Tools CP-SAT.  Same model, but all-different is a
    native global constraint here, so 6x6 finishes in milliseconds instead of
    timing out.  cell = side*row + col is LINEAR (side is a constant), so no
    multiplication constraints are needed."""
    m = cp_model.CpModel()
    cls = {}
    def V(name):
        r = uf.find(name)
        if r not in cls:
            cls[r] = m.NewIntVar(0, side - 1, "c%d" % len(cls))
        return cls[r]
    for group in tuples:
        cells = []
        for tup in group:
            k = len(tup)
            expr = sum(V(nm) * (side ** (k - 1 - i)) for i, nm in enumerate(tup))
            c = m.NewIntVar(0, side ** k - 1, "")
            m.Add(c == expr)
            cells.append(c)
        m.AddAllDifferent(cells)
    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = timeout_ms / 1000.0
    sv.parameters.num_search_workers = 8
    st = sv.Solve(m)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {r: sv.Value(v) for r, v in cls.items()}, uf
    if st == cp_model.INFEASIBLE:
        return None, uf
    return "unknown", uf


SOLVER = "cpsat"


def _solve_classes(uf, tuples, side, timeout_ms):
    if SOLVER == "cpsat":
        return _solve_classes_cpsat(uf, tuples, side, timeout_ms)
    return _solve_classes_z3(uf, tuples, side, timeout_ms)


def solve_bifid(ct, cribs, symbols, side, period, two_squares=False, timeout_ms=60000):
    src = bifid_sources(period, len(ct))
    uf = UF()
    tag2 = "2" if two_squares else "1"
    for s in symbols:
        uf.find("r1" + s); uf.find("c1" + s)
        if two_squares:
            uf.find("r2" + s); uf.find("c2" + s)
    for pos, pt in cribs:
        (k1, p1), (k2, p2) = src[pos]
        uf.union("r1" + pt, ("r" if k1 == "r" else "c") + tag2 + ct[p1])
        uf.union("c1" + pt, ("r" if k2 == "r" else "c") + tag2 + ct[p2])
    groups = [[["r1" + s, "c1" + s] for s in symbols]]
    if two_squares:
        groups.append([["r2" + s, "c2" + s] for s in symbols])
    sol, uf = _solve_classes(uf, groups, side, timeout_ms)
    if sol is None:
        return "unsat", None
    if sol == "unknown":
        return "unknown", None
    sq1 = {s: (sol[uf.find("r1" + s)], sol[uf.find("c1" + s)]) for s in symbols}
    sq2 = ({s: (sol[uf.find("r2" + s)], sol[uf.find("c2" + s)]) for s in symbols}
           if two_squares else sq1)
    return "sat", (sq1, sq2)


def solve_trifid(ct, cribs, symbols, period, timeout_ms=60000):
    src = trifid_sources(period, len(ct))
    uf = UF()
    for s in symbols:
        for k in "abc":
            uf.find(k + s)
    for pos, pt in cribs:
        for idx, (kind, cp) in enumerate(src[pos]):
            uf.union("abc"[idx] + pt, kind + ct[cp])
    groups = [[[k + s for k in "abc"] for s in symbols]]
    sol, uf = _solve_classes(uf, groups, 3, timeout_ms)
    if sol is None:
        return "unsat", None
    if sol == "unknown":
        return "unknown", None
    return "sat", {s: tuple(sol[uf.find(k + s)] for k in "abc") for s in symbols}


def decrypt_bifid(ct, sq1, sq2, side, period):
    inv1 = {v: k for k, v in sq1.items()}
    src = bifid_sources(period, len(ct))
    o = []
    for i in range(len(ct)):
        (k1, p1), (k2, p2) = src[i]
        a = sq2[ct[p1]][0 if k1 == "r" else 1]
        b = sq2[ct[p2]][0 if k2 == "r" else 1]
        o.append(inv1[(a, b)])
    return "".join(o)


def decrypt_trifid(ct, cube, period):
    inv = {v: k for k, v in cube.items()}
    src = trifid_sources(period, len(ct))
    o = []
    for i in range(len(ct)):
        co = []
        for idx, (kind, cp) in enumerate(src[i]):
            co.append(cube[ct[cp]]["abc".index(kind)])
        o.append(inv[tuple(co)])
    return "".join(o)


P("=" * 78)
P("(d) FRACTIONATION WITH AN UNKNOWN SQUARE -- CSP over the square itself")
P("=" * 78)
P("solvers: z3 %s (cross-check) + OR-Tools CP-SAT (primary, SOLVER=%s)"
  % (z3.get_version_string(), SOLVER))

# ------------------------------------------------------------------ 0. validation
P("\n0. VALIDATION (the solver must recover a square that really was used)")
rng = random.Random(7)
ALPH25 = "ABCDEFGHIKLMNOPQRSTUVWXYZ"          # J merged into I
ALPH36 = A2Z + "0123456789"
ALPH27 = A2Z + "#"

ok_all = True
P("   (a) round-trip: encrypt then decrypt with the SAME square must be the identity")
for side, alph in [(5, ALPH25, ), (6, ALPH36, )]:
    for per in (2, 3, 5, 7, 8, 97):
        cells = [(r, c) for r in range(side) for c in range(side)]
        rng.shuffle(cells)
        sq = dict(zip(alph, cells))
        pt = "".join(rng.choice(alph) for _ in range(N))
        ok = decrypt_bifid(bifid_encrypt(pt, sq, side, per), sq, sq, side, per) == pt
        ok_all &= ok
        if not ok:
            P("   FAIL bifid %d period %d" % (side, per))
for per in (2, 3, 5, 8, 97):
    cells = [(a, b, c) for a in range(3) for b in range(3) for c in range(3)]
    rng.shuffle(cells)
    cube = dict(zip(ALPH27, cells))
    pt = "".join(rng.choice(ALPH27) for _ in range(N))
    ok = decrypt_trifid(trifid_encrypt(pt, cube, per), cube, per) == pt
    ok_all &= ok
    if not ok:
        P("   FAIL trifid period %d" % per)
P("       bifid 5x5/6x6 and trifid round-trips at periods 2,3,5,7,8,97: %s" % ok_all)

P("   (b) synthetic-square recovery: encrypt a known plaintext, hand the solver the")
P("       crib letters, and check (i) it returns SAT, (ii) the model reproduces the")
P("       cribs, (iii) with ALL 97 plaintext letters given it recovers the plaintext.")
for side, alph, per in [(5, ALPH25, 7), (5, ALPH25, 9), (6, ALPH36, 5), (6, ALPH36, 11)]:
    cells = [(r, c) for r in range(side) for c in range(side)]
    rng.shuffle(cells)
    sq = dict(zip(alph, cells))
    pt = list(rng.choice(alph) for _ in range(N))
    for pos, _, l in CRIBS:
        pt[pos] = l if l in alph else "I"
    pt = "".join(pt)
    ct = bifid_encrypt(pt, sq, side, per)
    cr = [(pos, pt[pos]) for pos, _, _ in CRIBS]
    st, mm = solve_bifid(ct, cr, alph, side, per)
    rec = decrypt_bifid(ct, mm[0], mm[1], side, per) if st == "sat" else ""
    cribs_ok = st == "sat" and all(rec[pos] == l for pos, l in cr)
    st2, mm2 = solve_bifid(ct, [(i, pt[i]) for i in range(N)], alph, side, per)
    rec2 = decrypt_bifid(ct, mm2[0], mm2[1], side, per) if st2 == "sat" else ""
    full_ok = (st2 == "sat" and rec2 == pt)
    ok_all &= (st == "sat" and cribs_ok and full_ok)
    P("       bifid %dx%d period %-3d: 24-crib %s (cribs reproduced %s); 97-letter %s (pt recovered %s)"
      % (side, side, per, st, cribs_ok, st2, full_ok))
for per in (5, 8):
    cells = [(a, b, c) for a in range(3) for b in range(3) for c in range(3)]
    rng.shuffle(cells)
    cube = dict(zip(ALPH27, cells))
    pt = list(rng.choice(ALPH27) for _ in range(N))
    for pos, _, l in CRIBS:
        pt[pos] = l
    pt = "".join(pt)
    ct = trifid_encrypt(pt, cube, per)
    cr = [(pos, pt[pos]) for pos, _, _ in CRIBS]
    st, mm = solve_trifid(ct, cr, ALPH27, per)
    rec = decrypt_trifid(ct, mm, per) if st == "sat" else ""
    cribs_ok = st == "sat" and all(rec[pos] == l for pos, l in cr)
    st2, mm2 = solve_trifid(ct, [(i, pt[i]) for i in range(N)], ALPH27, per)
    rec2 = decrypt_trifid(ct, mm2, per) if st2 == "sat" else ""
    full_ok = (st2 == "sat" and rec2 == pt)
    ok_all &= (st == "sat" and cribs_ok and full_ok)
    P("       trifid period %-3d: 24-crib %s (cribs reproduced %s); 97-letter %s (pt recovered %s)"
      % (per, st, cribs_ok, st2, full_ok))

P("   (c) soundness of UNSAT: give the solver a contradictory crib set")
bad = [(0, "A"), (0, "B")]
st, _ = solve_bifid(CT_IJ0 := CT.replace("J", "I"), bad, ALPH25, 5, 7)
ok_all &= (st == "unsat")
P("       contradictory cribs -> %s" % st)
P("   all validations passed: %s" % ok_all)
assert ok_all

# negative control: a synthetic ciphertext whose cribs were NOT produced by any square
P("\n   Negative control (random 'cribs' on the real K4 ciphertext) is run below")
P("   for every system, as the chance-expectation column.")

# ------------------------------------------------------------------ 1. real runs
CT_IJ = CT.replace("J", "I")
CRIBS_IJ = [(pos, ("I" if l == "J" else l)) for pos, _, l in CRIBS]
CRIBS_PLAIN = [(pos, l) for pos, _, l in CRIBS]

ENGL = "".join(ch * f for ch, f in zip(A2Z, [82,15,28,43,127,22,20,61,70,2,8,40,24,
                                             67,75,19,1,60,63,91,28,10,24,2,20,1]))

def run_family(name, solve, ct, cribs, periods, nulls=20, rng=random.Random(11)):
    P("\n%s" % name)
    sats, unsats, unks = [], 0, []
    t0 = time.time()
    for p in periods:
        st, mm = solve(ct, cribs, p)
        if st == "sat":
            sats.append((p, mm))
        elif st == "unsat":
            unsats += 1
        else:
            unks.append(p)
    # chance expectation: same solver, same positions, random English plaintext
    nullsat = 0
    ntot = 0
    for _ in range(nulls):
        rc = [(pos, rng.choice(ENGL)) for pos, _ in cribs]
        for p in periods:
            ntot += 1
            st, _m = solve(ct, rc, p)
            if st == "sat":
                nullsat += 1
    P("   periods tested: %d (%d..%d)   time %.1fs" % (len(periods), periods[0], periods[-1], time.time() - t0))
    P("   UNSAT: %d   SAT: %d   unknown/timeout: %s" % (unsats, len(sats), unks or "none"))
    P("   chance baseline: %d random-crib trials x %d periods = %d solves, %d SAT (%.3f per period)"
      % (nulls, len(periods), ntot, nullsat, nullsat / max(ntot, 1)))
    return sats

PERIODS = list(range(2, 98))

sats_5 = run_family(
    "1. BIFID, unknown 5x5 square (J read as I), all 25! = 1.55e25 squares",
    lambda ct, cr, p: solve_bifid(ct, cr, ALPH25, 5, p),
    CT_IJ, CRIBS_IJ, PERIODS)

sats_6 = run_family(
    "2. BIFID, unknown 6x6 square over A-Z0-9, all 36! = 3.72e41 squares",
    lambda ct, cr, p: solve_bifid(ct, cr, ALPH36, 6, p),
    CT, CRIBS_PLAIN, PERIODS)

sats_cm5 = run_family(
    "3. CONJUGATED-MATRIX BIFID, two independent unknown 5x5 squares (25!^2 = 2.4e50)",
    lambda ct, cr, p: solve_bifid(ct, cr, ALPH25, 5, p, two_squares=True),
    CT_IJ, CRIBS_IJ, PERIODS, nulls=10)

sats_cm6 = run_family(
    "4. CONJUGATED-MATRIX BIFID, two independent unknown 6x6 squares (36!^2 = 1.4e83)",
    lambda ct, cr, p: solve_bifid(ct, cr, ALPH36, 6, p, two_squares=True),
    CT, CRIBS_PLAIN, PERIODS, nulls=10)

sats_tri = run_family(
    "5. TRIFID, unknown 3x3x3 cube over A-Z plus one null (27! = 1.09e28)",
    lambda ct, cr, p: solve_trifid(ct, cr, ALPH27, p),
    CT, CRIBS_PLAIN, PERIODS)

# ------------------------------------------------------------------ 2. report SATs
P("\n6. Any SAT results, decrypted and scored")
QG = None
def score(txt):
    global QG
    if QG is None:
        import json
        QG = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         ".quadgrams_cache.json")))
    tot, n = 0.0, 0
    floor = QG["floor"]
    d = QG["q"]
    for i in range(len(txt) - 3):
        g = txt[i:i + 4]
        tot += d.get(g, floor)
        n += 1
    return tot / max(n, 1)

any_sat = False
rows = []
for label, sats, dec in [("bifid 5x5", sats_5, lambda m, p: decrypt_bifid(CT_IJ, m[0], m[1], 5, p)),
                         ("bifid 6x6", sats_6, lambda m, p: decrypt_bifid(CT, m[0], m[1], 6, p)),
                         ("CM bifid 5x5", sats_cm5, lambda m, p: decrypt_bifid(CT_IJ, m[0], m[1], 5, p)),
                         ("CM bifid 6x6", sats_cm6, lambda m, p: decrypt_bifid(CT, m[0], m[1], 6, p)),
                         ("trifid", sats_tri, lambda m, p: decrypt_trifid(CT, m, p))]:
    for per, mm in sats:
        any_sat = True
        txt = dec(mm, per)
        ok = all(txt[pos] == (("I" if l == "J" else l) if "5x5" in label else l)
                 for pos, _c, l in CRIBS)
        rows.append((score(txt), label, per, ok, txt))
if not any_sat:
    P("   none.")
else:
    rows.sort(reverse=True)
    P("   %d SAT models in total.  Every one reproduces the cribs by construction" % len(rows))
    P("   (verified column 'cribs'); the question is only whether the other 73")
    P("   letters read as English.  Quadgram score: English ~ -5.6, random ~ -8.2.")
    P("   %-14s %-4s %-6s %-9s %s" % ("family", "per", "cribs", "quadgram", "decryption"))
    for sc, label, per, ok, txt in rows[:25]:
        P("   %-14s %-4d %-6s %-9.3f %s" % (label, per, ok, sc, txt))
    import statistics as _st
    P("   score distribution over all %d SAT models: min %.3f median %.3f max %.3f"
      % (len(rows), min(r[0] for r in rows), _st.median([r[0] for r in rows]),
         max(r[0] for r in rows)))
    # random baseline on the same alphabet/length
    rb = []
    _r = random.Random(99)
    for _ in range(3000):
        rb.append(score("".join(_r.choice(A2Z) for _ in range(97))))
    rb.sort()
    P("   random-text baseline (3000 draws): median %.3f  99th pct %.3f  max %.3f"
      % (rb[1500], rb[int(0.99 * 3000)], rb[-1]))
    P("   NOTE: a bifid model whose square is only partly pinned by the cribs has")
    P("   many completions; the solver returns ONE. The scores below are therefore")
    P("   a lower bound on what hill-climbing the free cells could reach, which is")
    P("   why the transposition-free unknown-square question is settled by the")
    P("   UNSAT/SAT counts above rather than by these scores.")

with open("/Users/pravarkataria/Desktop/crypto/kryptos/analysis/matrix_d_output.txt", "w") as f:
    f.write("\n".join(out) + "\n")
