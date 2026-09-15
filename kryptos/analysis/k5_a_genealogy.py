"""(a) METHOD GENEALOGY: what is "the next step" after K1/K2 (Quagmire III) and K3
(keyless route transposition), from a 1988-90 hand-cipher standpoint?

The genealogy argument is written up in findings/k5_genealogy.md.  This script tests
the concrete candidates it produces:

  S0  Alphabet-independent invariants of the forced key stream.  Whatever the
      letter-substitution primitive, if K4 is C[i] = f_i(P[i]) with f_i depending on
      one key symbol drawn from ONE fixed pair of alphabets, the 24 cribs force
      equalities and inequalities between key symbols that hold for EVERY alphabet
      and EVERY family.  These are free constraints no previous script has stated.

  S1  GROMARK, model G1 (ACA reading: plaintext located in a plain/keyed alphabet,
      counted forward k places, read off a *different* mixed cipher alphabet):
          C[i] = A_c[(idx_{A_p}(P[i]) + k_i) mod 26],  k_i in 0..base-1
      With A_p fixed and A_c completely free, the cribs are testable EXACTLY over all
      26! cipher alphabets by a well-definedness + injectivity check.  Exhaustive over
      every primer of every length for base 10 and base 26.

  S2  GROMARK, model G2 (Bean's reading, "GROnsfeld with Mixed Alphabet": one mixed
      alphabet used for both sides):
          C[i] = A[(idx_A(P[i]) + k_i) mod 26]
      Feasibility over all 26! alphabets A is a union-find-with-potentials problem plus
      a disjoint-placement check.  Exhaustive over primers, bases and lag structures;
      survivors are completed by hill-climbing the free part of the alphabet and scored.

  S3  Periodic / progressive Gromark (Bean's own suggested repair), exhaustive for
      digit-key periods 1..6 in base 10 with a free mixed alphabet.

  S4  The literal product-cipher genealogy: K3's recovered double-rotation applied to
      the KEY STREAM rather than to the text (a running key read through K3's route).

Every search is validated by planting a synthetic cipher of the same type and checking
that the search recovers it.  Chance expectations are printed beside every count.
"""
import os
import sys
import time
import itertools
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import k4_common as K
import runningkey_lib as RK
import twocipher_common as TC

OUT = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


A2Z = K.A2Z
KRY = K.KRYPTOS_ALPHA
CT = K.CT
N = 97

# 0-indexed crib positions, ciphertext letters, plaintext letters
CPOS = K.CRIB_POS
CPT = K.CRIB_PT
CCT = K.CRIB_CT
assert len(CPOS) == 24

P("=" * 78)
P("(a) METHOD GENEALOGY -- concrete candidates and their tests")
P("=" * 78)
P("ciphertext  :", CT)
P("crib pos    :", " ".join(str(p + 1) for p in CPOS))
P("crib ct/pt  :", "".join(CCT), "/", "".join(CPT))


# ===========================================================================
# S0.  Alphabet-independent invariants of the forced key stream
# ===========================================================================
P("\n" + "=" * 78)
P("S0.  ALPHABET-INDEPENDENT INVARIANTS OF THE FORCED KEY STREAM")
P("=" * 78)
P("""
Model assumed:  C[i] = f(P[i], k_i) where f is a letter-wise rule over ONE fixed pair
of alphabets and k_i is a single key symbol.  Every classical polyalphabetic in play
(Vigenere, Beaufort, variant Beaufort, Quagmire I-IV, Gronsfeld, Gromark, running key,
one-time chart) is of this form.  For such an f, k -> f(p,k) is a bijection for fixed p
and p -> f(p,k) is a bijection for fixed k.  Hence:

    (C_i,P_i) == (C_j,P_j)                       =>  k_i == k_j
    P_i == P_j and C_i != C_j                    =>  k_i != k_j
    C_i == C_j and P_i != P_j                    =>  k_i != k_j

These hold for EVERY alphabet pair and EVERY family, so they are properties of the
Sanborn cribs alone.""")

eqs = []
neqs = []
for a in range(24):
    for b in range(a + 1, 24):
        if CCT[a] == CCT[b] and CPT[a] == CPT[b]:
            eqs.append((CPOS[a], CPOS[b]))
        elif CCT[a] == CCT[b] or CPT[a] == CPT[b]:
            neqs.append((CPOS[a], CPOS[b]))

P("\nFORCED EQUALITIES  (k_i == k_j), 1-indexed:")
for i, j in eqs:
    P("   k[%d] == k[%d]   (both %s -> %s), separation %d"
      % (i + 1, j + 1, CT[i], K.CRIB[i], j - i))
P("   total:", len(eqs))
P("\nFORCED INEQUALITIES (k_i != k_j), 1-indexed:  %d pairs" % len(neqs))
P("   " + ", ".join("%d!=%d" % (i + 1, j + 1) for i, j in neqs))

if eqs:
    i, j = eqs[0]
    d = j - i
    divs = [p for p in range(1, 98) if d % p == 0]
    P("""
CONSEQUENCE.  The single forced equality is k[28] == k[66] (1-indexed), separation 38.
Any PERIODIC key of period p satisfies it automatically iff p divides 38, i.e.
p in {1, 2, 19, 38}; all four are already ruled out by the periodic sweeps.  For any
other p the equality must hold by coincidence, probability 1/26.  A NON-periodic key
stream must satisfy it exactly -- it is a free, alphabet-independent filter that every
candidate key stream in this repository should be checked against.""")
    P("   divisors of 38 in 1..97:", divs)

# How many of the 24 key symbols are forced to be pairwise distinct?
adj = defaultdict(set)
for i, j in neqs:
    adj[i].add(j)
    adj[j].add(i)
P("\nDistinctness pressure: the inequality graph on the 24 crib positions has %d edges;"
  % len(neqs))
P("   mean degree %.2f.  A key stream that is constant on any of these pairs is "
  "impossible." % (2 * len(neqs) / 24.0))


# ===========================================================================
# Digit-stream generators
# ===========================================================================
def chain_stream(primer, base, n, lag_pair=(0, 1)):
    """Lagged-Fibonacci / chain addition.  k_i = k_{i-L+lag_pair[0]} + k_{i-L+lag_pair[1]}
    (mod base) for i >= L, where L = len(primer).  Standard Gromark is lag_pair=(0,1)."""
    L = len(primer)
    k = list(primer)
    a, b = lag_pair
    while len(k) < n:
        i = len(k)
        k.append((k[i - L + a] + k[i - L + b]) % base)
    return k[:n]


def chain_streams_vec(base, L, n, lag_pair=(0, 1)):
    """All base**L primers at once.  Returns (base**L, n) int16 array."""
    m = base ** L
    idx = np.arange(m)
    K_ = np.zeros((m, n), dtype=np.int16)
    for t in range(L):
        K_[:, L - 1 - t] = (idx // (base ** t)) % base
    a, b = lag_pair
    for i in range(L, n):
        K_[:, i] = (K_[:, i - L + a] + K_[:, i - L + b]) % base
    return K_


# ===========================================================================
# S1.  Gromark model G1 -- fixed plaintext alphabet, FREE cipher alphabet
# ===========================================================================
P("\n" + "=" * 78)
P("S1.  GROMARK model G1:  C[i] = A_c[(idx_Ap(P[i]) + k_i) mod 26]")
P("     A_p fixed, A_c FREE (the test below covers all 26! cipher alphabets exactly)")
P("=" * 78)

# --- S1.0 the alphabet-independent necessary condition on A_p -------------
P("""
Necessary condition on A_p alone.  Two cribs with the same CIPHER letter give
   idx_Ac(C) = (idx_Ap(P_i) + k_i) = (idx_Ap(P_j) + k_j)  (mod 26)
so  idx_Ap(P_j) - idx_Ap(P_i) = k_i - k_j  must be representable as a difference of two
key digits, i.e. must lie in {0..base-1} U {26-(base-1)..25}.  This is independent of
A_c and of the primer, so one evaluation kills an entire (A_p, base) pair.""")

collide = defaultdict(list)
for a in range(24):
    collide[CCT[a]].append(CPT[a])
pairs_needed = []
for c, pts in collide.items():
    for x in range(len(pts)):
        for y in range(x + 1, len(pts)):
            if pts[x] != pts[y]:
                pairs_needed.append((c, pts[x], pts[y]))
P("\n   cipher-letter collisions forcing a digit difference:")
for c, p1, p2 in pairs_needed:
    P("      %s -> {%s,%s}:  need idx(%s)-idx(%s) representable" % (c, p1, p2, p2, p1))


def g1_alphabet_feasible(Ap, base):
    """Necessary condition above; returns (ok, list of offending differences)."""
    lo = base - 1
    bad = []
    for c, p1, p2 in pairs_needed:
        d = (Ap.index(p2) - Ap.index(p1)) % 26
        if not (d <= lo or d >= 26 - lo):
            bad.append((c, p1, p2, d))
    return (not bad), bad


EXTRA_KEYWORDS = ["ORDINATE", "PALIMPSESTABSCISSA", "ABSCISSAORDINATE", "TUTANKHAMUN",
                  "WELTZEITUHR", "ALEXANDERPLATZ", "EGYPT", "CARTER", "INVISIBLE",
                  "GROMARK", "VIGENERE", "MATRIX", "WEBSTER", "LUCIDMEMORY"]
NAMED_ALPHAS = {"straight": A2Z, "KRYPTOS": KRY}
for w in K.SHORT_KEYWORDS + EXTRA_KEYWORDS:
    NAMED_ALPHAS.setdefault(w, K.keyed_alphabet(w))

for base in (10, 26):
    P("\n   base %d -- named plaintext alphabets that pass the necessary condition:" % base)
    ok_list = []
    for name, Ap in NAMED_ALPHAS.items():
        ok, bad = g1_alphabet_feasible(Ap, base)
        if ok:
            ok_list.append(name)
        elif base == 10 and name in ("straight", "KRYPTOS"):
            P("      %-10s FAILS: %s" % (name, "; ".join(
                "idx(%s)-idx(%s)=%d needs |d|<=%d" % (p2, p1, d, base - 1)
                for c, p1, p2, d in bad)))
    P("      pass: %d of %d  ->  %s" % (len(ok_list), len(NAMED_ALPHAS),
                                        ", ".join(sorted(ok_list)) or "(none)"))

# how rare is the condition over the dictionary alphabets?
t0 = time.time()
DICT_ALPHAS = K.dict_alphabets()
P("\n   dictionary keyword-mixed alphabets: %d distinct (%.1fs)" % (len(DICT_ALPHAS), time.time() - t0))
dict_ok10 = [a for a in DICT_ALPHAS if g1_alphabet_feasible(a, 10)[0]]
P("   pass the base-10 necessary condition: %d  (%.4f of them)"
  % (len(dict_ok10), len(dict_ok10) / len(DICT_ALPHAS)))

# --- S1.1 exact exhaustive test over primers and free A_c -----------------
# distinct crib cipher letters and the equality/injectivity structure
DISTINCT_CT = sorted(set(CCT))
first_of = {c: min(a for a in range(24) if CCT[a] == c) for c in DISTINCT_CT}
eq_checks = [(first_of[CCT[a]], a) for a in range(24) if a != first_of[CCT[a]]]
inj_idx = [first_of[c] for c in DISTINCT_CT]
P("\n   structure of the exact test: %d equality checks, %d distinct cipher letters "
  "needing distinct indices" % (len(eq_checks), len(inj_idx)))


def g1_scan(Ap, Kstream, cribpos, sign=+1):
    """Kstream: (m, 97) digits.  Returns boolean mask of feasible primers.
    sign=+1 : C = A_c[(p + k) mod 26]   (Gromark proper)
    sign=-1 : C = A_c[(p - k) mod 26]   (variant direction)
    sign=0  : C = A_c[(k - p) mod 26]   (Beaufort direction)"""
    p = np.array([Ap.index(x) for x in CPT], dtype=np.int16)
    kk = Kstream[:, cribpos]
    if sign == 1:
        r = (p[None, :] + kk) % 26
    elif sign == -1:
        r = (p[None, :] - kk) % 26
    else:
        r = (kk - p[None, :]) % 26
    ok = np.ones(r.shape[0], dtype=bool)
    for i, j in eq_checks:
        ok &= (r[:, i] == r[:, j])
        if not ok.any():
            return ok
    sub = r[:, inj_idx]
    for x in range(len(inj_idx)):
        for y in range(x + 1, len(inj_idx)):
            ok &= (sub[:, x] != sub[:, y])
            if not ok.any():
                return ok
    return ok


# --- free digit constraints for G1 (independent of BOTH alphabets) --------
# Cipher letters R and S both collide on the plaintext pair (S,T):
#   idx_Ap(T)-idx_Ap(S) = k_24-k_29 = k_33-k_34   (1-indexed)
# and P->R at 28 and 66 forces k_28 = k_66.  Both are alphabet-free.
G1_FREE = [("k[28]-k[66]", 27, 65, 0),
           ("(k[24]-k[29])-(k[33]-k[34])", None, None, None)]


def g1_free_mask(Kstream):
    k = Kstream
    ok = (k[:, 27] == k[:, 65])
    ok &= (((k[:, 23] - k[:, 28]) - (k[:, 32] - k[:, 33])) % 26 == 0)
    return ok


# --- validation: plant a synthetic G1 Gromark and recover it --------------
def g1_selftest():
    rng = np.random.default_rng(7)
    Ap = NAMED_ALPHAS["LODESTONE"]
    perm = list(A2Z)
    rng.shuffle(perm)
    Ac = "".join(perm)
    primer = [3, 1, 4, 1, 5]
    k = chain_stream(primer, 10, N)
    pt = list("Q" * N)
    for i, pos in enumerate(CPOS):
        pt[pos] = CPT[i]
    ct = "".join(Ac[(Ap.index(pt[i]) + k[i]) % 26] for i in range(N))
    # now pretend we only know ct at the crib positions
    saved = CCT[:]
    try:
        for i, pos in enumerate(CPOS):
            CCT[i] = ct[pos]
        d_first = {c: min(a for a in range(24) if CCT[a] == c) for c in sorted(set(CCT))}
        eqc = [(d_first[CCT[a]], a) for a in range(24) if a != d_first[CCT[a]]]
        inj = [d_first[c] for c in sorted(set(CCT))]
        Ks = chain_streams_vec(10, 5, N)
        p = np.array([Ap.index(x) for x in CPT], dtype=np.int16)
        r = (p[None, :] + Ks[:, CPOS]) % 26
        ok = np.ones(r.shape[0], dtype=bool)
        for i, j in eqc:
            ok &= (r[:, i] == r[:, j])
        sub = r[:, inj]
        for x in range(len(inj)):
            for y in range(x + 1, len(inj)):
                ok &= (sub[:, x] != sub[:, y])
        want = sum(primer[t] * 10 ** (4 - t) for t in range(5))
        hits = np.flatnonzero(ok)
        return want in set(hits.tolist()), len(hits)
    finally:
        CCT[:] = saved


found, nhit = g1_selftest()
P("\n   VALIDATION G1: planted primer 31415 with a random cipher alphabet -> "
  "recovered = %s (%d primers survive that synthetic crib set)" % (found, nhit))
assert found, "G1 self-test failed"

P("\n   exhaustive G1 scans over the named alphabets (A_c free = all 26! cipher alphabets),")
P("   all three shift directions:")
P("   %-6s %-4s %-7s %10s %10s %12s" % ("base", "L", "dir", "primers", "A_p passing", "survivors"))
g1_total = 0
g1_surv = []
for base, Ls in ((10, (2, 3, 4, 5, 6)), (26, (2, 3, 4)), (12, (2, 3, 4, 5)), (16, (2, 3, 4, 5))):
    for L in Ls:
        m = base ** L
        if m > 2_000_000:
            continue
        Ks = chain_streams_vec(base, L, N)
        feas = [(n, a) for n, a in NAMED_ALPHAS.items() if g1_alphabet_feasible(a, base)[0]]
        for sign, dname in ((1, "p+k"), (-1, "p-k"), (0, "k-p")):
            nsurv = 0
            for name, Ap in feas:
                ok = g1_scan(Ap, Ks, CPOS, sign)
                n_ok = int(ok.sum())
                g1_total += m
                nsurv += n_ok
                if n_ok:
                    for pi in np.flatnonzero(ok)[:20]:
                        g1_surv.append((name, base, L, dname, int(pi), Ks[pi].copy()))
            P("   %-6d %-4d %-7s %10d %10d %12d" % (base, L, dname, m, len(feas), nsurv))
        del Ks
P("   G1 named-alphabet total primer x alphabet x direction tests: %d ; survivors: %d"
  % (g1_total, len(g1_surv)))

# --- S1b: the full dictionary sweep, base 10 and other small bases --------
P("\n   S1b.  DICTIONARY plaintext alphabets.  Two alphabet-free digit constraints prune")
P("   the primer space first:  k[28]==k[66]  and  (k[24]-k[29])==(k[33]-k[34])  (1-indexed).")
dict_list = {}
for base in (10, 12, 16, 20):
    dict_list[base] = [a for a in DICT_ALPHAS if g1_alphabet_feasible(a, base)[0]]
    P("   base %2d: %6d of %d dictionary alphabets pass the necessary condition"
      % (base, len(dict_list[base]), len(DICT_ALPHAS)))
P("   %-6s %-4s %-7s %10s %12s %14s %10s" %
  ("base", "L", "dir", "primers", "after-prune", "alpha x primer", "survivors"))
g1b_tests = 0
g1b_surv = []
for base in (10, 12, 16, 20):
    alist = dict_list[base]
    for L in (2, 3, 4, 5, 6):
        m = base ** L
        if m > 1_200_000:
            continue
        Ks = chain_streams_vec(base, L, N)
        keep = np.flatnonzero(g1_free_mask(Ks))
        Kp = Ks[keep]
        del Ks
        for sign, dname in ((1, "p+k"), (-1, "p-k"), (0, "k-p")):
            ns = 0
            if len(keep):
                for Ap in alist:
                    ok = g1_scan(Ap, Kp, CPOS, sign)
                    n_ok = int(ok.sum())
                    if n_ok:
                        ns += n_ok
                        for pi in np.flatnonzero(ok)[:5]:
                            g1b_surv.append((Ap, base, L, dname, int(keep[pi])))
            g1b_tests += len(keep) * len(alist)
            P("   %-6d %-4d %-7s %10d %12d %14d %10d"
              % (base, L, dname, m, len(keep), len(keep) * len(alist), ns))
        del Kp
P("   G1 dictionary total tests: %d ; survivors: %d" % (g1b_tests, len(g1b_surv)))
for row in g1b_surv[:10]:
    P("      survivor:", row[1:], "alphabet", row[0], "keyword", DICT_ALPHAS[row[0]])


# ===========================================================================
# S2.  Gromark model G2 -- ONE free mixed alphabet (Bean's reading)
# ===========================================================================
P("\n" + "=" * 78)
P("S2.  GROMARK model G2 (Bean):  C[i] = A[(idx_A(P[i]) + k_i) mod 26], A free")
P("=" * 78)
P("""
Hard digit constraints available before any alphabet is considered:
   position 33 (1-indexed) has S -> S  =>  k_33 = 0
   position 74 (1-indexed) has K -> K  =>  k_74 = 0
   positions 28 and 66 both have P -> R  =>  k_28 = k_66
For base 10 those three cut the primer space by 1/1000 before the alphabet test runs.""")

SELF = [i for i in range(24) if CCT[i] == CPT[i]]
P("   self-mapping cribs (0-indexed positions):", [CPOS[i] for i in SELF],
  "=", [(CCT[i], CPT[i]) for i in SELF])


def g2_feasible(kvals, sign=+1):
    """kvals: 24 key digits at the crib positions.  Is there ANY 26-letter alphabet A
    with, for every crib i,
        sign=+1 :  idx_A(C_i) = idx_A(P_i) + k_i      (Gromark, C = A[p+k])
        sign=-1 :  idx_A(C_i) = idx_A(P_i) - k_i      (variant,  C = A[p-k])
        sign= 0 :  idx_A(C_i) = k_i - idx_A(P_i)      (Beaufort, C = A[k-p])
    all 26 indices distinct?  Solved exactly: propagate v(x) = s_x * t + c_x per
    connected component, enumerate the free parameter t over Z26, then place the
    components disjointly.  Returns (feasible, partial alphabet as a list of 26)."""
    edges = defaultdict(list)     # x -> [(y, s, c)] meaning v(y) = s*v(x) + c
    for i in range(24):
        pl, cl, k = CPT[i], CCT[i], kvals[i] % 26
        if sign == 1:
            edges[pl].append((cl, 1, k)); edges[cl].append((pl, 1, (-k) % 26))
        elif sign == -1:
            edges[pl].append((cl, 1, (-k) % 26)); edges[cl].append((pl, 1, k))
        else:
            edges[pl].append((cl, -1, k)); edges[cl].append((pl, -1, k))
    seen = set()
    comp_masks = []               # per component: list of (mask, [(letter, idx)])
    for start in list(edges):
        if start in seen:
            continue
        lab = {start: (1, 0)}     # v(x) = s*t + c
        stack = [start]
        seen.add(start)
        tcons = []                # constraints of the form 2t == m
        members = [start]
        bad = False
        while stack:
            x = stack.pop()
            sx, cx = lab[x]
            for y, s, c in edges[x]:
                sy, cy = s * sx, (s * cx + c) % 26
                if y in lab:
                    py, qy = lab[y]
                    if py == sy:
                        if qy != cy:
                            bad = True
                    else:
                        # py*t + qy == sy*t + cy  ->  (py-sy)*t == cy-qy, |py-sy| = 2
                        tcons.append((py - sy, (cy - qy) % 26))
                else:
                    lab[y] = (sy, cy)
                    members.append(y)
                    seen.add(y)
                    stack.append(y)
        if bad:
            return False, None
        opts = []
        for t in range(26):
            if any((d * t - m) % 26 != 0 for d, m in tcons):
                continue
            idxs = {x: (s * t + c) % 26 for x, (s, c) in lab.items()}
            if len(set(idxs.values())) != len(idxs):
                continue
            mask = 0
            for v in idxs.values():
                mask |= 1 << v
            opts.append((mask, sorted(idxs.items(), key=lambda kv: kv[1])))
        if not opts:
            return False, None
        comp_masks.append(opts)
    order = sorted(range(len(comp_masks)), key=lambda i: -bin(comp_masks[i][0][0]).count("1"))
    chosen = [None] * len(comp_masks)

    def dfs(t, used):
        if t == len(order):
            return True
        ci = order[t]
        for mask, mp in comp_masks[ci]:
            if not (mask & used):
                chosen[ci] = mp
                if dfs(t + 1, used | mask):
                    return True
        return False

    if not dfs(0, 0):
        return False, None
    alpha = [None] * 26
    for mp in chosen:
        for x, j in mp:
            if alpha[j] is not None:
                return False, None
            alpha[j] = x
    return True, alpha


def g2_selftest():
    rng = np.random.default_rng(11)
    perm = list(A2Z)
    rng.shuffle(perm)
    A = "".join(perm)
    primer = [2, 7, 1, 8, 2]
    k = chain_stream(primer, 10, N)
    pt = list("Q" * N)
    for i, pos in enumerate(CPOS):
        pt[pos] = CPT[i]
    ct = "".join(A[(A.index(pt[i]) + k[i]) % 26] for i in range(N))
    saved = CCT[:]
    try:
        for i, pos in enumerate(CPOS):
            CCT[i] = ct[pos]
        kk = [k[p] for p in CPOS]
        ok, _ = g2_feasible(kk)
        # and confirm a wrong stream is usually rejected
        bad = 0
        for t in range(200):
            pr = [int(x) for x in rng.integers(0, 10, 5)]
            kk2 = [chain_stream(pr, 10, N)[p] for p in CPOS]
            if g2_feasible(kk2)[0]:
                bad += 1
        return ok, bad
    finally:
        CCT[:] = saved


ok_self, false_pos = g2_selftest()
P("\n   VALIDATION G2: planted primer 27182 with a random single alphabet -> accepted = %s;"
  % ok_self)
P("   random primers accepted: %d of 200 (this is the empirical null rate)" % false_pos)
assert ok_self, "G2 self-test failed"

LAGS = {"(0,1) standard": (0, 1), "(0,2)": (0, 2), "(0,L-1) = k_{i-L}+k_{i-1}": None}


def g2_digit_mask(kc, sign):
    """Alphabet-free digit filter for model G2.
    sign +/-1 : a self-mapping crib forces k == 0.
    sign  0   : a self-mapping crib forces 2*idx = k, solvable iff k is even (mod 26).
    All signs : the two P->R cribs force k[28] == k[66] (1-indexed)."""
    ok = np.ones(kc.shape[0], dtype=bool)
    for i in SELF:
        if sign:
            ok &= (kc[:, i] % 26 == 0)
        else:
            ok &= (kc[:, i] % 2 == 0)
    for a in range(24):
        for b in range(a + 1, 24):
            if CCT[a] == CCT[b] and CPT[a] == CPT[b]:
                ok &= (kc[:, a] == kc[:, b])
    return ok


def g2_sweep(base, L, lag_pair, sign=1, cap=3_000_000):
    m = base ** L
    if m > cap:
        return None
    Ks = chain_streams_vec(base, L, N, lag_pair)
    kc = Ks[:, CPOS]
    cand = np.flatnonzero(g2_digit_mask(kc, sign))
    surv = []
    for ci in cand:
        good, alpha = g2_feasible([int(x) for x in kc[ci]], sign)
        if good:
            surv.append((int(ci), alpha, Ks[ci].copy()))
    return m, len(cand), surv


P("\n   exhaustive G2 sweeps (alphabet free = all 26! alphabets):")
P("   %-6s %-3s %-16s %10s %10s %10s" % ("base", "L", "recurrence", "primers", "pass-digit", "feasible"))
g2_all = []
for base in (10, 26, 2, 5, 8, 12, 16, 20):
    for L in (2, 3, 4, 5, 6):
        for lname, lp in (("k_{i-L}+k_{i-L+1}", (0, 1)),
                          ("k_{i-L}+k_{i-L+2}", (0, 2)),
                          ("k_{i-L}+k_{i-1}", (0, None))):
            if lp[1] is None:
                lp = (0, L - 1)
            if lp[1] >= L or lp[0] >= L or lp[0] == lp[1]:
                continue
            res = g2_sweep(base, L, lp)
            if res is None:
                continue
            m, npass, surv = res
            g2_all.append((base, L, lname, m, npass, surv))
            if surv or (base == 10 and L == 5):
                P("   %-6d %-3d %-16s %10d %10d %10d" % (base, L, lname, m, npass, len(surv)))
tot_prim = sum(x[3] for x in g2_all)
tot_pass = sum(x[4] for x in g2_all)
tot_surv = sum(len(x[5]) for x in g2_all)
P("   ---")
P("   G2 totals: %d primers swept, %d passed the digit filter, %d alphabet-feasible"
  % (tot_prim, tot_pass, tot_surv))
b10l5 = [x for x in g2_all if x[0] == 10 and x[1] == 5 and x[2] == "k_{i-L}+k_{i-L+1}"]
if b10l5:
    P("   base 10 / L=5 / standard recurrence (Bean's published case): %d feasible primers "
      "of %d  [Bean reported 39 of 99,999]" % (len(b10l5[0][5]), b10l5[0][3]))


# --- score the G2 survivors ------------------------------------------------
def complete_and_score(alpha, kstream, tries=400, seed=0):
    """alpha: list of 26 entries, some None.  Fill the holes to maximise the quadgram
    score of the full 97-letter decryption; returns (best_score, best_pt, best_alpha)."""
    rng = np.random.default_rng(seed)
    holes = [i for i in range(26) if alpha[i] is None]
    missing = [c for c in A2Z if c not in alpha]
    assert len(holes) == len(missing)
    best = (-99.0, None, None)
    for _ in range(max(1, tries // 20)):
        cur = list(alpha)
        mm = list(missing)
        rng.shuffle(mm)
        for h, c in zip(holes, mm):
            cur[h] = c
        s = _score_alpha(cur, kstream)
        improved = True
        while improved:
            improved = False
            for x in range(len(holes)):
                for y in range(x + 1, len(holes)):
                    cur[holes[x]], cur[holes[y]] = cur[holes[y]], cur[holes[x]]
                    s2 = _score_alpha(cur, kstream)
                    if s2 > s:
                        s = s2
                        improved = True
                    else:
                        cur[holes[x]], cur[holes[y]] = cur[holes[y]], cur[holes[x]]
        if s > best[0]:
            best = (s, _decrypt_alpha(cur, kstream), "".join(cur))
    return best


def _decrypt_alpha(alpha, kstream, sign=1):
    idx = {c: i for i, c in enumerate(alpha)}
    if sign == 1:
        return "".join(alpha[(idx[CT[i]] - int(kstream[i])) % 26] for i in range(N))
    if sign == -1:
        return "".join(alpha[(idx[CT[i]] + int(kstream[i])) % 26] for i in range(N))
    return "".join(alpha[(int(kstream[i]) - idx[CT[i]]) % 26] for i in range(N))


def _score_alpha(alpha, kstream, sign=1):
    return TC.quadgram_score(_decrypt_alpha(alpha, kstream, sign))


all_surv = [(b, L, ln, ci, al, ks) for b, L, ln, m, npass, sv in g2_all for ci, al, ks in sv]
P("\n   total G2 survivors across every (base, L, recurrence): %d" % len(all_surv))
if all_surv:
    scored = []
    t0 = time.time()
    for b, L, ln, ci, al, ks in all_surv[:400]:
        s, pt, alp = complete_and_score(al, ks, seed=ci)
        scored.append((s, b, L, ln, ci, pt, alp))
    scored.sort(reverse=True)
    P("   scored %d of them in %.1fs (quadgram: English ~ -4.7, random ~ -8.2)"
      % (len(scored), time.time() - t0))
    P("   top 10 by quadgram score of the full 97-letter decryption:")
    for s, b, L, ln, ci, pt, alp in scored[:10]:
        P("      %.3f  base=%d L=%d %s primer#%d" % (s, b, L, ln, ci))
        P("             A=%s" % alp)
        P("             pt=%s" % K.mark_cribs(pt))
        w = TC.word_coverage(pt)
        P("             word coverage %.2f ; words: %s"
          % (w, [x for _, x in K.dict_words_in(pt, 5)][:8]))
    # control: what does the best-of-N look like for random alphabets?
    rng = np.random.default_rng(3)
    ctrl = []
    for _ in range(60):
        perm = list(A2Z)
        rng.shuffle(perm)
        ks = np.array(chain_stream([int(x) for x in rng.integers(0, 10, 5)], 10, N))
        ctrl.append(_score_alpha(perm, ks))
    ctrl.sort()
    P("   control (random alphabet + random primer, 60 draws): median %.3f, max %.3f"
      % (ctrl[len(ctrl) // 2], ctrl[-1]))


# ===========================================================================
# S3.  Periodic Gromark (Bean's suggested repair)
# ===========================================================================
P("\n" + "=" * 78)
P("S3.  PERIODIC GROMARK -- repeating digit key, free mixed alphabet")
P("=" * 78)
P("   (Bean: 'stats are strongest within the cribs but not between them -> "
  "progressive key? periodic Gromark?')")
P("   %-6s %-4s %12s %10s %10s" % ("base", "p", "keys", "pass-digit", "feasible"))
per_surv = []
for base in (10, 26):
    for p in range(1, 7):
        m = base ** p
        if m > 3_000_000:
            continue
        idx = np.arange(m)
        keyp = np.zeros((m, p), dtype=np.int16)
        for t in range(p):
            keyp[:, p - 1 - t] = (idx // (base ** t)) % base
        kc = keyp[:, [c % p for c in CPOS]]
        ok = np.ones(m, dtype=bool)
        for i in SELF:
            ok &= (kc[:, i] % 26 == 0)
        for a in range(24):
            for b2 in range(a + 1, 24):
                if CCT[a] == CCT[b2] and CPT[a] == CPT[b2]:
                    ok &= (kc[:, a] == kc[:, b2])
        cand = np.flatnonzero(ok)
        sv = []
        for ci in cand:
            good, alpha = g2_feasible([int(x) for x in kc[ci]])
            if good:
                full = np.array([keyp[ci][i % p] for i in range(N)])
                sv.append((int(ci), alpha, full))
        per_surv += [(base, p, ci, al, ks) for ci, al, ks in sv]
        P("   %-6d %-4d %12d %10d %10d" % (base, p, m, len(cand), len(sv)))
P("   periodic-Gromark survivors: %d" % len(per_surv))
if per_surv:
    sc = []
    for base, p, ci, al, ks in per_surv[:300]:
        s, pt, alp = complete_and_score(al, ks, seed=ci)
        sc.append((s, base, p, ci, pt, alp))
    sc.sort(reverse=True)
    P("   top 5:")
    for s, base, p, ci, pt, alp in sc[:5]:
        P("      %.3f base=%d p=%d key#%d  A=%s" % (s, base, p, ci, alp))
        P("            pt=%s" % K.mark_cribs(pt))


# ===========================================================================
# S4.  K3's route applied to the KEY STREAM
# ===========================================================================
P("\n" + "=" * 78)
P("S4.  PRODUCT-CIPHER GENEALOGY: K3's double rotation applied to the KEY STREAM")
P("=" * 78)
P("""
K1/K2 = substitution with a key; K3 = keyless double rotation.  The literal 'next step'
is to compose them.  Composition applied to the TEXT is closed (findings/twocipher.md:
a transposition before the substitution leaves the 24 crib pairs untouched, and
S-then-T was swept over 1.17M transpositions).  The untried composition is to apply
K3's route to the KEY: read a running key out of a sculpture text through the same
rotation that K3 uses.  Then the key letter used at position i is keytext[pi[i]] for a
fixed permutation pi, and the 24 required key letters must appear at the SCATTERED
positions pi(crib) rather than contiguously -- a test the running-key sweep could not do.""")


def rot_perm(n, w):
    """Write 0..n-1 into rows of width w, read columns right-to-left, top-to-bottom.
    Returns out[j] = source index."""
    rows = (n + w - 1) // w
    out = []
    for c in range(w - 1, -1, -1):
        for r in range(rows):
            i = r * w + c
            if i < n:
                out.append(i)
    return out


def compose(p1, p2):
    return [p1[j] for j in p2]


PERMS = {"identity": list(range(N))}
for w in (4, 7, 8, 12, 14, 16, 21, 24, 31, 42, 48):
    pw = rot_perm(N, w)
    PERMS["rot%d" % w] = pw
for w1, w2 in ((8, 24), (24, 8), (4, 48), (12, 16), (42, 14), (14, 42), (7, 14), (31, 31)):
    PERMS["rot%d_rot%d" % (w1, w2)] = compose(rot_perm(N, w1), rot_perm(N, w2))

corpus = RK.corpus()
combos = list(RK.combos())
req = {}
for cb in combos:
    fam, ap, ac, ak = cb
    Ap, Ac, Ak = RK.ALPHAS[ap], RK.ALPHAS[ac], RK.ALPHAS[ak]
    req[cb] = [Ak[RK.key_index(fam, Ap.index(CPT[i]), Ac.index(CCT[i]))] for i in range(24)]

best = (-1, None)
tests = 0
hits = []
for pname, pi in PERMS.items():
    scat = [pi[p] for p in CPOS]
    span = max(scat) + 1
    for tname, txt in corpus.items():
        if len(txt) < span:
            continue
        for off in range(len(txt) - span + 1):
            window = [txt[off + s] for s in scat]
            for cb in combos:
                tests += 1
                m = sum(1 for a in range(24) if window[a] == req[cb][a])
                if m > best[0]:
                    best = (m, (pname, tname, off, RK.combo_name(cb)))
                if m >= 12:
                    hits.append((m, pname, tname, off, RK.combo_name(cb)))
P("\n   tests: %d (permutation x text x offset x 24 combos)" % tests)
P("   expected best-of-N by chance: with p=1/26 per letter and %d draws, "
  "P(>=12 of 24) = %.3g per draw" % (tests, sum(
      __import__("math").comb(24, t) * (1 / 26.) ** t * (25 / 26.) ** (24 - t)
      for t in range(12, 25))))
P("   best agreement: %d/24 at %s" % best)
P("   draws reaching >=12/24: %d" % len(hits))
for h in sorted(hits, reverse=True)[:5]:
    P("      ", h)

P("\n" + "=" * 78)
P("END (a)")
P("=" * 78)

with open(os.path.join(HERE, "k5_a_output.txt"), "w") as f:
    f.write("\n".join(OUT) + "\n")
print("\nwrote k5_a_output.txt")
