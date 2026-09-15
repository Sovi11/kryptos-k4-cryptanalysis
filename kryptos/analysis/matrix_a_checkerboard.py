"""(a) STRADDLING CHECKERBOARD + numeric key (VIC family), including the
variant with a disrupted columnar transposition.

The point of this script is NOT to brute-force VIC keys -- a VIC additive is a
chain-addition stream as long as the message, so the key space swamps the 24
crib letters and any "solution" found would be meaningless (the same
unfalsifiability boundary matrix_e_rotor.py documents for the M-209).  The
point is that a straddling checkerboard is a *variable-length* encoding, and
that property alone is testable against the cribs, transposition or no
transposition.

Structure
  A0  validation of the checkerboard implementation (round trip + digit count)
  A1  what a VIC pipeline actually emits, and why K4 cannot be raw VIC output
  A2  the digit-count identity, which is invariant under ANY length-preserving
      digit operation (additive, plain columnar, disrupted columnar)
  A3  weak crib reading (block boundaries align): exhaustive over all
      short-row choices on BOTH sides
  A4  strong crib reading (letter j <-> letter j): the conflict-component
      analysis, exhaustive
  A5  the degenerate no-straddle case (monome-dinome / Polybius + periodic
      digit additive), as a CP-SAT constraint problem over an unknown grid
"""
import itertools
import math
import os
import random
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matrix_common import CT, CRIBS, N, A2Z, CRIB_PT

OUT = []
def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUT.append(s)

# English monogram frequencies (percent), standard table
ENG = dict(zip(A2Z, [8.17, 1.49, 2.78, 4.25, 12.70, 2.23, 2.02, 6.09, 6.97, 0.15,
                     0.77, 4.03, 2.41, 6.75, 7.51, 1.93, 0.10, 5.99, 6.33, 9.06,
                     2.76, 0.98, 2.36, 0.15, 1.97, 0.07]))
ENGV = np.array([ENG[c] / 100.0 for c in A2Z])

P("=" * 78)
P("(a) STRADDLING CHECKERBOARD / VIC")
P("=" * 78)

# ---------------------------------------------------------------- A0 validation
P("\nA0. VALIDATION of the checkerboard implementation")

class Board:
    """Straddling checkerboard.  `short` maps k letters to single digits;
    the remaining 10-k digits are row prefixes; every other symbol gets a
    two-digit code prefix+column."""
    def __init__(self, short_row, rest):
        # short_row: string of length 10 with '.' where a prefix digit sits
        self.short = {}
        self.prefixes = []
        for d, ch in enumerate(short_row):
            if ch == ".":
                self.prefixes.append(d)
            else:
                assert ch not in self.short
                self.short[ch] = str(d)
        self.long = {}
        i = 0
        for pfx in self.prefixes:
            for col in range(10):
                if i < len(rest):
                    self.long[rest[i]] = "%d%d" % (pfx, col)
                    i += 1
        assert i == len(rest), "not enough two-digit slots"
        self.dec = {v: k for k, v in self.short.items()}
        self.dec.update({v: k for k, v in self.long.items()})
        self.pfxset = set(str(d) for d in self.prefixes)

    def encode(self, text):
        o = []
        for ch in text:
            o.append(self.short[ch] if ch in self.short else self.long[ch])
        return "".join(o)

    def decode(self, digits):
        o, i = [], 0
        while i < len(digits):
            if digits[i] in self.pfxset:
                o.append(self.dec[digits[i:i + 2]])
                i += 2
            else:
                o.append(self.dec[digits[i]])
                i += 1
        return "".join(o)


# The classic English straddling checkerboard: high-frequency letters
# A T . O N E . S I R on digits 0-9 with 2 and 6 as prefixes.
SHORT_ROW = "AT.ONE.SIR"
REST = "BCDFGHJKLMPQUVWXYZ"          # the other 18 letters
bd = Board(SHORT_ROW, REST)
P("    board: short row %r (prefixes %s)" % (SHORT_ROW, bd.prefixes))
P("    single-digit letters: %s" % "".join(sorted(bd.short)))
P("    e.g. A=%s T=%s E=%s R=%s | B=%s K=%s Z=%s"
  % (bd.short["A"], bd.short["T"], bd.short["E"], bd.short["R"],
     bd.long["B"], bd.long["K"], bd.long["Z"]))
enc = bd.encode("ATTACKATDAWN")
P("    ATTACKATDAWN -> %s  (%d digits for 12 letters)" % (enc, len(enc)))
assert bd.decode(enc) == "ATTACKATDAWN"
rng = random.Random(4)
ok = True
for _ in range(4000):
    t = "".join(rng.choice(A2Z) for _ in range(rng.randint(1, 200)))
    e = bd.encode(t)
    ok &= (bd.decode(e) == t)
    ok &= (len(e) == 2 * len(t) - sum(1 for c in t if c in bd.short))
P("    4000 random round trips, and the digit-count identity")
P("        len(encode(T)) == 2*len(T) - #(letters of T in the short row): %s" % ok)
assert ok

# a 3-prefix board too
bd3 = Board("ET.AO.NI.S", "BCDFGHJKLMPQRUVWXYZ")
ok3 = all(bd3.decode(bd3.encode(t)) == t
          for t in ["".join(rng.choice(A2Z) for _ in range(rng.randint(1, 120)))
                    for _ in range(2000)])
P("    3-prefix board (7 single-digit letters): 2000 round trips ok = %s" % ok3)
assert ok3

# VIC additive (non-carrying mod-10 digit addition) and columnar transposition,
# purely to demonstrate they preserve digit count.
def add_mod10(a, b):
    return "".join(str((int(x) + int(y)) % 10) for x, y in zip(a, b))

def columnar(digits, key):
    w = len(key)
    cols = [[] for _ in range(w)]
    for i, ch in enumerate(digits):
        cols[i % w].append(ch)
    order = sorted(range(w), key=lambda i: key[i])
    return "".join("".join(cols[i]) for i in order)

def disrupted_columnar(digits, key):
    """VIC's second transposition: fill the rectangle normally until the
    triangular 'disrupted' areas begin, which are then filled last."""
    w = len(key)
    order = sorted(range(w), key=lambda i: key[i])
    rank = {c: r for r, c in enumerate(order)}
    rows = (len(digits) + w - 1) // w
    grid = [[None] * w for _ in range(rows)]
    # mark the disrupted triangles
    blocked = [[False] * w for _ in range(rows)]
    r, start = 0, 0
    while r < rows:
        cut = rank_order_cut = None
        # triangle starting under column with rank `start`
        width = (start % w) + 1
        for j in range(w - width, w):
            if r < rows:
                blocked[r][j] = True
        r += 1
        start += 1
    it = iter(digits)
    for rr in range(rows):
        for cc in range(w):
            if not blocked[rr][cc]:
                try:
                    grid[rr][cc] = next(it)
                except StopIteration:
                    pass
    for rr in range(rows):
        for cc in range(w):
            if blocked[rr][cc]:
                try:
                    grid[rr][cc] = next(it)
                except StopIteration:
                    pass
    return "".join(grid[rr][c] for c in order for rr in range(rows)
                   if grid[rr][c] is not None)

d = bd.encode("THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG")
k = "".join(str(rng.randint(0, 9)) for _ in range(len(d)))
lp = (len(add_mod10(d, k)) == len(d)
      and len(columnar(d, "3142756")) == len(d)
      and len(disrupted_columnar(d, "3142756")) == len(d))
P("    additive / columnar / disrupted-columnar all preserve digit count: %s" % lp)
assert lp
P("    => every stage of VIC after the checkerboard is length-preserving.")

# ---------------------------------------------------------------- A1
P("\nA1. WHAT A VIC PIPELINE EMITS, AND THE FIRST ARITHMETIC")
P("    VIC output is a DIGIT stream (grouped in fives), not letters.  K4 is 97")
P("    letters using all 26 of the alphabet, so some digit->letter recode must")
P("    close the pipeline.  There are exactly two ways to close it:")
P("      (i)  fixed 2-digit recode (a Polybius/monome-dinome read-out).  Then")
P("           the digit count must be even and equal to 2*97 = 194.  Since the")
P("           checkerboard emits 2*L - S digits for an L-letter plaintext with")
P("           S short-row letters, L = 97 forces S = 0: NOT ONE plaintext letter")
P("           may be in the short row.  That is a checkerboard with no straddle,")
P("           i.e. no checkerboard at all (case A5 below).")
P("      (ii) a checkerboard recode.  Then the count identity of A2 applies.")

# ---------------------------------------------------------------- A2
P("\nA2. THE DIGIT-COUNT IDENTITY  (invariant under any transposition)")
P("    D_pt = 2*97 - S_pt ,  D_ct = 2*97 - S_ct ,  and every VIC stage preserves")
P("    length, so D_pt = D_ct and therefore  S_pt = S_ct  exactly, where")
P("      S_pt = # plaintext letters in the plaintext board's short row")
P("      S_ct = # ciphertext letters in the ciphertext board's short row.")
P("    S_ct is COMPUTABLE, because the whole ciphertext is known.")
ctc = Counter(CT)
P("    ciphertext letter counts: %s" % " ".join("%s%d" % (c, ctc[c]) for c in A2Z if ctc[c]))
srt = sorted(ctc.values(), reverse=True)
for k_ in (6, 7, 8):
    P("      short row of %d letters: S_ct ranges %d .. %d   (max = the %d commonest"
      % (k_, sum(sorted(ctc[c] for c in A2Z)[:k_]), sum(srt[:k_]), k_))
    P("        ciphertext letters %s)" % "".join(c for c, _ in ctc.most_common(k_)))
P("    English expectation for S_pt with a *properly built* board (short row =")
P("    the k commonest English letters):")
for k_ in (6, 7, 8):
    top = sorted(A2Z, key=lambda c: -ENG[c])[:k_]
    p = sum(ENG[c] for c in top) / 100
    P("      k=%d  short row %s  mass %.1f%%  E[S_pt] = %.1f  sd %.1f"
      % (k_, "".join(top), 100 * p, 97 * p, math.sqrt(97 * p * (1 - p))))
P("    Compare: the LARGEST S_ct any 8-letter ciphertext short row can reach is")
P("    %d, i.e. %.1f%% of the ciphertext, against E[S_pt] = %.1f for the standard"
  % (sum(srt[:8]), 100 * sum(srt[:8]) / 97, 97 * 0.6348))
P("    8-letter English board.  z = %.2f.  The gap is structural: a straddling"
  % ((sum(srt[:8]) - 97 * 0.6348) / math.sqrt(97 * 0.6348 * 0.3652)))
P("    checkerboard is a COMPRESSION device tuned to English, and K4's flat")
P("    letter distribution cannot absorb the same number of digits.")

# ---------------------------------------------------------------- A3
P("\nA3. WEAK CRIB READING -- block boundaries align.  EXHAUSTIVE.")
P("    Sanborn's clues are contiguous ciphertext spans equal in length to their")
P("    plaintext words:")
SPANS = [(21, 25, "EAST"), (25, 34, "NORTHEAST"), (63, 69, "BERLIN"), (69, 74, "CLOCK")]
for a, b, w in SPANS:
    assert CT[a:b] == CT[a:b] and len(w) == b - a
    assert "".join(CRIB_PT[i] for i in range(a, b)) == w
    P("      ct[%2d:%2d] = %-9s  pt = %-9s  (both %d letters)" % (a + 1, b, CT[a:b], w, b - a))
P("    Because each span has equal ciphertext and plaintext length, the digit")
P("    offsets must agree at every span boundary: positions 0,21,25,34,63,69,74,97.")
P("    Each of the 7 segments then gives  #short_pt = #short_ct  on that segment.")
SEGS = [(0, 21), (21, 25), (25, 34), (34, 63), (63, 69), (69, 74), (74, 97)]
KNOWN_PT = {i: CRIB_PT[i] for i in CRIB_PT}
for a, b in SEGS:
    known = all(i in KNOWN_PT for i in range(a, b))
    P("      segment [%2d,%2d): %2d letters, plaintext %s"
      % (a, b, b - a, ("known: " + "".join(KNOWN_PT[i] for i in range(a, b))) if known else "UNKNOWN"))

# weight vectors (per letter) for the four known segments and the three unknown ones
def wvec(s):
    v = np.zeros(26, dtype=np.int32)
    for ch in s:
        v[A2Z.index(ch)] += 1
    return v

PT_KNOWN_SEGS = ["EAST", "NORTHEAST", "BERLIN", "CLOCK"]
CT_KNOWN_SEGS = [CT[21:25], CT[25:34], CT[63:69], CT[69:74]]
W_PT = np.stack([wvec(s) for s in PT_KNOWN_SEGS])            # 4 x 26
W_CT = np.stack([wvec(s) for s in CT_KNOWN_SEGS])            # 4 x 26
UNK = [(0, 21), (34, 63), (74, 97)]
W_CTU = np.stack([wvec(CT[a:b]) for a, b in UNK])            # 3 x 26

_MASK_CACHE = {}
def all_masks(k):
    """Index array of every k-subset of the 26 letters."""
    if k not in _MASK_CACHE:
        _MASK_CACHE[k] = np.array(list(itertools.combinations(range(26), k)), dtype=np.int8)
    return _MASK_CACHE[k]

results = {}
P("\n    Exhaustive enumeration of short rows on BOTH sides (sizes 6,7,8).")
for kpt in (6, 7, 8):
    cpt = all_masks(kpt)
    # e[i] = # of crib word i's letters in H_pt
    E = np.zeros((len(cpt), 4), dtype=np.int16)
    for i in range(4):
        E[:, i] = W_PT[i][cpt].sum(axis=1)
    PMASS = ENGV[cpt].sum(axis=1)
    for kct in (6, 7, 8):
        cct = all_masks(kct)
        F = np.zeros((len(cct), 4), dtype=np.int16)
        for i in range(4):
            F[:, i] = W_CT[i][cct].sum(axis=1)
        M = np.zeros((len(cct), 3), dtype=np.int16)
        for i in range(3):
            M[:, i] = W_CTU[i][cct].sum(axis=1)
        # bucket by the 4-vector
        keyE = (E[:, 0] * 1000 + E[:, 1] * 100 + E[:, 2] * 10 + E[:, 3]).astype(np.int32)
        keyF = (F[:, 0] * 1000 + F[:, 1] * 100 + F[:, 2] * 10 + F[:, 3]).astype(np.int32)
        setF = set(np.unique(keyF).tolist())
        okE = np.fromiter((int(x) in setF for x in keyE), dtype=bool, count=len(keyE))
        n_ok = int(okE.sum())
        best_p = float(PMASS[okE].max()) if n_ok else float("nan")
        results[(kpt, kct)] = (len(cpt), n_ok, best_p, cpt, okE, PMASS, keyE, keyF, M, cct)
        P("      |H_pt|=%d |H_ct|=%d : %7d / %7d plaintext boards admit SOME ciphertext"
          % (kpt, kct, n_ok, len(cpt)))
        P("                          board satisfying all four span equations;"
          " best English mass of such a board = %.1f%%" % (100 * best_p if n_ok else 0))

P("\n    Reference: the largest English mass any short row of that size can have")
for k_ in (6, 7, 8):
    top = sorted(A2Z, key=lambda c: -ENG[c])[:k_]
    P("      k=%d : %.1f%%  (%s)" % (k_, sum(ENG[c] for c in top), "".join(top)))

# For the best-p feasible boards, now apply the three UNKNOWN-segment equations
def logbinom_pmf(n, k, p):
    if k < 0 or k > n:
        return -1e9
    return (math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
            + (k * math.log(p) if k else 0.0)
            + ((n - k) * math.log1p(-p) if n - k else 0.0))

P("\n    Now the three UNKNOWN segments.  For a feasible (H_pt,H_ct) pair the")
P("    unknown plaintext must ALSO put exactly m0/m3/m6 of its letters in the")
P("    short row on segments [0,21), [34,63), [74,97).  Under English that is")
P("    Binomial(21,p), Binomial(29,p), Binomial(23,p).  Best case over all pairs:")
for kpt in (6, 7, 8):
    for kct in (6, 7, 8):
        npt, n_ok, best_p, cpt, okE, PMASS, keyE, keyF, M, cct = results[(kpt, kct)]
        if not n_ok:
            continue
        # index ciphertext boards by bucket
        buck = {}
        for idx in range(len(cct)):
            buck.setdefault(int(keyF[idx]), set()).add((int(M[idx, 0]), int(M[idx, 1]), int(M[idx, 2])))
        # shortlist: the 400 feasible plaintext boards with the largest English mass
        cand = np.where(okE)[0]
        cand = cand[np.argsort(-PMASS[cand])][:400]
        rows_lr = []
        for idx in cand:
            p = float(PMASS[idx])
            mode = (max(logbinom_pmf(21, m, p) for m in range(22))
                    + max(logbinom_pmf(29, m, p) for m in range(30))
                    + max(logbinom_pmf(23, m, p) for m in range(24)))
            bst = None
            for (m0, m3, m6) in buck.get(int(keyE[idx]), ()):
                lp = (logbinom_pmf(21, m0, p) + logbinom_pmf(29, m3, p)
                      + logbinom_pmf(23, m6, p))
                if bst is None or lp > bst[0]:
                    bst = (lp, m0, m3, m6)
            if bst:
                rows_lr.append((bst[0] - mode, p, idx, bst))
        if rows_lr:
            # (i) the most English-heavy feasible board
            by_mass = max(rows_lr, key=lambda t: t[1])
            # (ii) the feasible board whose unknown-segment demand is most ordinary
            by_lr = max(rows_lr, key=lambda t: t[0])
            for tag, (lr, p, idx, (lp, m0, m3, m6)) in [("max English mass", by_mass),
                                                        ("max likelihood  ", by_lr)]:
                row = "".join(A2Z[i] for i in cpt[idx])
                P("      |H_pt|=%d |H_ct|=%d  %s: short row %-9s mass %.1f%%,"
                  % (kpt, kct, tag, row, 100 * p))
                P("            needs %2d/21, %2d/29, %2d/23 short letters in the unknown"
                  " plaintext" % (m0, m3, m6))
                P("            (English predicts %.1f, %.1f, %.1f); likelihood ratio to the"
                  % (21 * p, 29 * p, 23 * p))
                P("            most likely demand = %.2e  (log %.2f)" % (math.exp(lr), lr))

# ---------------------------------------------------------------- A4
P("\nA4. STRONG CRIB READING -- ciphertext letter j decodes to plaintext letter j.")
P("    Then the digit block of ct letter j must BE the digit block of pt letter j,")
P("    so short(pt_j) == short(ct_j) for all 24 crib positions.  Equal-membership")
P("    constraints join letters into components; every letter of a component is")
P("    in its side's short row, or none is.")
par = {}
def find(x):
    par.setdefault(x, x)
    while par[x] != x:
        par[x] = par[par[x]]
        x = par[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        par[ra] = rb
for pos, c, pt in CRIBS:
    union(("pt", pt), ("ct", c))
comp = {}
for node in list(par):
    comp.setdefault(find(node), []).append(node)
comps = []
for root, nodes in comp.items():
    ptl = sorted(n[1] for n in nodes if n[0] == "pt")
    ctl = sorted(n[1] for n in nodes if n[0] == "ct")
    comps.append((ptl, ctl))
comps.sort(key=lambda t: (-len(t[0]) - len(t[1]), t[0]))
P("    %d components:" % len(comps))
for ptl, ctl in comps:
    P("      pt {%s}  <->  ct {%s}" % ("".join(ptl), "".join(ctl)))
P("    (letters not listed are unconstrained: %d plaintext, %d ciphertext)"
  % (26 - sum(len(a) for a, _ in comps), 26 - sum(len(b) for _, b in comps)))

P("\n    Enumerating all 2^%d component on/off patterns against |H| budgets:" % len(comps))
freepta = [c for c in A2Z if all(c not in ptl for ptl, _ in comps)]
freecta = [c for c in A2Z if all(c not in ctl for _, ctl in comps)]
rows_a4 = []
for bits in range(1 << len(comps)):
    onpt, onct = [], []
    for i, (ptl, ctl) in enumerate(comps):
        if bits >> i & 1:
            onpt += ptl
            onct += ctl
    for kpt in (6, 7, 8):
        if len(onpt) > kpt:
            continue
        for kct in (6, 7, 8):
            if len(onct) > kct:
                continue
            # best English mass achievable: forced letters + best free fillers
            need = kpt - len(onpt)
            fill = sorted(freepta, key=lambda c: -ENG[c])[:need]
            mass = sum(ENG[c] for c in onpt + fill)
            rows_a4.append((mass, bits, kpt, kct, "".join(sorted(onpt + fill)),
                            "".join(sorted(onct)), need, kct - len(onct)))
rows_a4.sort(reverse=True)
P("      feasible (pattern, |H_pt|, |H_ct|) triples: %d" % len(rows_a4))
P("      top 12 by achievable English mass of the plaintext short row:")
P("      %-7s %-4s %-4s %-10s %-14s %s" % ("mass%", "kpt", "kct", "H_pt", "forced H_ct", "free slots"))
for mass, bits, kpt, kct, hpt, hct, fpt, fct in rows_a4[:12]:
    P("      %-7.1f %-4d %-4d %-10s %-14s pt+%d ct+%d" % (mass, kpt, kct, hpt, hct, fpt, fct))
P("      absolute maximum for an 8-letter English short row: %.1f%% (ETAOINSR)"
  % sum(sorted(ENG.values(), reverse=True)[:8]))
P("      *** every strong-reading board leaves the plaintext short row at most")
P("      %.1f%% of English text, versus %.1f%% for a properly built board. ***"
  % (rows_a4[0][0], sum(sorted(ENG.values(), reverse=True)[:8])))

# combine A4 with the A2 count identity
P("\n    Combining A4 with the A2 identity S_pt = S_ct:")
allz = []
for mass, bits, kpt, kct, hpt, hct, fpt, fct in rows_a4:
    forced = sum(ctc[c] for c in hct)
    freec = sorted((ctc[c] for c in freecta), reverse=True)
    smax = forced + sum(freec[:fct])
    smin = forced + sum(sorted(ctc[c] for c in freecta)[:fct])
    pp = mass / 100
    exp = 97 * pp
    sd = math.sqrt(97 * pp * (1 - pp))
    nearest = min(max(exp, smin), smax)
    allz.append(((nearest - exp) / sd, mass, hpt, hct, smin, smax, exp, sd))
allz.sort(key=lambda t: -t[0])
P("      Exhaustive over all %d feasible (component pattern, |H_pt|, |H_ct|) triples." % len(allz))
zb, mb, hp, hc, s0, s1, e0, sd0 = allz[0]
P("      BEST CASE ANYWHERE: H_pt=%s (%.1f%% of English), forced H_ct=%s," % (hp, mb, hc))
P("      S_ct reachable in [%d,%d], E[S_pt]=%.1f+-%.1f  ->  z = %+.2f  (one-sided p = %.4f)"
  % (s0, s1, e0, sd0, zb, 0.5 * math.erfc(-zb / math.sqrt(2))))
P("      z quartiles over all 150: %.2f / %.2f / %.2f (best / median / worst)"
  % (allz[0][0], allz[len(allz) // 2][0], allz[-1][0]))
P("      the eight most English-heavy boards in detail:")
shown = 0
for mass, bits, kpt, kct, hpt, hct, fpt, fct in rows_a4:
    if shown >= 8:
        break
    # best/worst S_ct given the forced ct letters + best free fillers
    forced = sum(ctc[c] for c in hct)
    freec = sorted((ctc[c] for c in freecta), reverse=True)
    smax = forced + sum(freec[:fct])
    smin = forced + sum(sorted(ctc[c] for c in freecta)[:fct])
    p = mass / 100
    # required S_pt is in [smin, smax]; how far is that from English?
    exp = 97 * p
    sd = math.sqrt(97 * p * (1 - p))
    nearest = min(max(exp, smin), smax)
    P("      H_pt=%-10s (%.1f%%)  S_ct in [%d,%d]  E[S_pt]=%.1f+-%.1f  ->  z = %+.2f"
      % (hpt, mass, smin, smax, exp, sd, (nearest - exp) / sd))
    shown += 1

# ---------------------------------------------------------------- A5
P("\nA5. THE DEGENERATE NO-STRADDLE CASE: monome-dinome / Polybius + digit key")
P("    Every letter two digits, so the encoding is length-preserving and the")
P("    cribs are positionally meaningful.  Model:")
P("        (r,c) = grid(pt_j);  ct_j = grid^-1( (r+k[2j mod q]) %% 10, (c+k[2j+1 mod q]) %% 10 )")
P("    with an UNKNOWN placement of the 26 letters in the 10x10 grid and an")
P("    unknown digit key of period q.  Solved exactly with CP-SAT.")
try:
    from ortools.sat.python import cp_model
    HAVE = True
except ImportError:
    HAVE = False
    P("    ortools missing -- skipped")

if HAVE:
    def solve_period(q, cribs, side=10, timeout=20.0):
        m = cp_model.CpModel()
        R = {c: m.NewIntVar(0, side - 1, "r" + c) for c in A2Z}
        C = {c: m.NewIntVar(0, side - 1, "c" + c) for c in A2Z}
        cell = {}
        for c in A2Z:
            v = m.NewIntVar(0, side * side - 1, "z" + c)
            m.Add(v == side * R[c] + C[c])
            cell[c] = v
        m.AddAllDifferent(list(cell.values()))
        K = [m.NewIntVar(0, 9, "k%d" % i) for i in range(q)]
        for (pos, ctl, ptl) in cribs:
            for which, (X, t) in enumerate([(R, 2 * pos), (C, 2 * pos + 1)]):
                # X[ct] == (X[pt] + K[t mod q]) mod side
                s = m.NewIntVar(0, side - 1 + 9, "s%d_%d" % (pos, which))
                m.Add(s == X[ptl] + K[t % q])
                b = m.NewBoolVar("b%d_%d" % (pos, which))
                m.Add(s >= side).OnlyEnforceIf(b)
                m.Add(s < side).OnlyEnforceIf(b.Not())
                m.Add(X[ctl] == s - side).OnlyEnforceIf(b)
                m.Add(X[ctl] == s).OnlyEnforceIf(b.Not())
        sv = cp_model.CpSolver()
        sv.parameters.max_time_in_seconds = timeout
        sv.parameters.num_search_workers = 8
        st = sv.Solve(m)
        if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return "sat"
        if st == cp_model.INFEASIBLE:
            return "unsat"
        return "unknown"

    # ---------------------------------------------------------------- A5a
    # The WELL-DEFINED version: a d x d square holding exactly d*d symbols with
    # the key reduced mod d.  Every shift then lands on an occupied cell, so the
    # cipher actually exists and a synthetic positive control is possible.
    def solve_square(d, symbols, cribs, q, timeout=20.0):
        m = cp_model.CpModel()
        R = {c: m.NewIntVar(0, d - 1, "r" + c) for c in symbols}
        C = {c: m.NewIntVar(0, d - 1, "c" + c) for c in symbols}
        cell = {}
        for c in symbols:
            v = m.NewIntVar(0, d * d - 1, "z" + c)
            m.Add(v == d * R[c] + C[c])
            cell[c] = v
        m.AddAllDifferent(list(cell.values()))
        K = [m.NewIntVar(0, d - 1, "k%d" % i) for i in range(q)]
        for (pos, ctl, ptl) in cribs:
            for which, (X, t) in enumerate([(R, 2 * pos), (C, 2 * pos + 1)]):
                s_ = m.NewIntVar(0, 2 * d - 2, "s%d_%d" % (pos, which))
                m.Add(s_ == X[ptl] + K[t % q])
                b = m.NewBoolVar("b%d_%d" % (pos, which))
                m.Add(s_ >= d).OnlyEnforceIf(b)
                m.Add(s_ < d).OnlyEnforceIf(b.Not())
                m.Add(X[ctl] == s_ - d).OnlyEnforceIf(b)
                m.Add(X[ctl] == s_).OnlyEnforceIf(b.Not())
        sv = cp_model.CpSolver()
        sv.parameters.max_time_in_seconds = timeout
        sv.parameters.num_search_workers = 8
        st = sv.Solve(m)
        return ("sat" if st in (cp_model.OPTIMAL, cp_model.FEASIBLE)
                else "unsat" if st == cp_model.INFEASIBLE else "unknown")

    P("\n  A5a. CLOSED SQUARE (d x d holding exactly d*d symbols, key mod d).")
    P("       This is the version that is actually a cipher: every shifted cell")
    P("       is occupied, so encryption is total.  d=5 with I/J merged (25")
    P("       symbols) and d=6 over A-Z0-9 (36 symbols).")
    SY5 = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    SY6 = A2Z + "0123456789"
    rv = random.Random(31)
    for d, SY in ((5, SY5), (6, SY6)):
        cells = [(a, b) for a in range(d) for b in range(d)]
        for qq in (3, 5, 8):
            rv.shuffle(cells)
            g = dict(zip(SY, cells))
            iv = {v: k for k, v in g.items()}
            key = [rv.randint(0, d - 1) for _ in range(qq)]
            pt = "".join(rv.choice(SY) for _ in range(N))
            ct2 = []
            for j, ch in enumerate(pt):
                r0, c0 = g[ch]
                ct2.append(iv[((r0 + key[(2 * j) % qq]) % d, (c0 + key[(2 * j + 1) % qq]) % d)])
            cr = [(pos, ct2[pos], pt[pos]) for pos, _, _ in CRIBS]
            P("       validation d=%d q=%-2d synthetic -> %s (expect sat)"
              % (d, qq, solve_square(d, SY, cr, qq)))
    P("       validation contradictory cribs -> %s (expect unsat)"
      % solve_square(5, SY5, [(0, "A", "B"), (0, "A", "C")], 4))
    CR5 = [(pos, ("I" if c == "J" else c), ("I" if l == "J" else l)) for pos, c, l in CRIBS]
    for d, SY, cr in ((5, SY5, CR5), (6, SY6, CRIBS)):
        sat5, uns5 = [], []
        for q in range(1, 31):
            st = solve_square(d, SY, cr, q, timeout=15.0)
            (sat5 if st == "sat" else uns5).append(q)
        P("       K4, d=%d, key periods 1..30:  UNSAT %s" % (d, uns5 or "none"))
        P("                                     SAT   %s" % (sat5 or "none"))
        rv2 = random.Random(32)
        POOL5 = "".join(ch * int(ENG[ch] * 100) for ch in A2Z if ch in SY)
        ns, nt = 0, 0
        for _ in range(5):
            rc = [(pos, c, rv2.choice(POOL5)) for pos, c, _ in cr]
            for q in range(1, 31):
                nt += 1
                if solve_square(d, SY, rc, q, timeout=15.0) == "sat":
                    ns += 1
        P("       chance baseline (5 random-plaintext crib sets x 30 periods):"
          " %d/%d SAT = %.3f per period" % (ns, nt, ns / nt))

    P("\n  A5b. THE 10x10 MONOME-DINOME (26 letters in 100 cells, key mod 10).")
    P("       Caveat stated up front: with only 26 of 100 cells filled, a random")
    P("       shift lands on an empty cell with probability 0.74, so this")
    P("       'cipher' is not total and a synthetic positive control cannot be")
    P("       constructed by sampling -- which is itself the finding.  The")
    P("       UNSAT results below must therefore be read together with the")
    P("       random-plaintext baseline, not on their own.")
    # validation: a synthetic grid + periodic key must be recovered as SAT,
    # and a deliberately impossible instance must come back UNSAT.
    rr = random.Random(5)
    cells = [(a, b) for a in range(10) for b in range(10)]
    rr.shuffle(cells)
    grid = dict(zip(A2Z, cells[:26]))
    inv = {v: k for k, v in grid.items()}
    for qq in (4, 6, 10):
        key = [rr.randint(0, 9) for _ in range(qq)]
        pt = "".join(rr.choice(A2Z) for _ in range(N))
        ct2, good = [], True
        for j, ch in enumerate(pt):
            r0, c0 = grid[ch]
            t = ((r0 + key[(2 * j) % qq]) % 10, (c0 + key[(2 * j + 1) % qq]) % 10)
            if t not in inv:
                good = False
                break
            ct2.append(inv[t])
        if not good:
            P("    (validation q=%d: synthetic grid produced an unoccupied cell -- "
              "which is itself the point: only 26 of 100 cells are filled)" % qq)
            continue
        cr = [(pos, ct2[pos], pt[pos]) for pos, _, _ in CRIBS]
        P("    validation q=%-2d synthetic instance -> %s (expect sat)" % (qq, solve_period(qq, cr)))
    bad = [(0, "A", "B"), (0, "A", "C")]
    P("    validation contradictory cribs -> %s (expect unsat)" % solve_period(4, bad))

    P("\n    Counting first: an unknown 26-of-100 grid carries log2(100!/74!) = %.0f"
      % (sum(math.log2(x) for x in range(75, 101))))
    P("    bits and the key another 3.32*q; the cribs supply only 24*log2(26) = 113")
    P("    bits.  Consistent models are guaranteed to exist by counting alone, so")
    P("    SAT here is expected and carries no information.  Confirming:")
    P("\n    K4, real cribs, digit-key periods q = 1..30:")
    sat, unsat, unk = [], [], []
    for q in range(1, 31):
        st = solve_period(q, CRIBS, timeout=10.0)
        (sat if st == "sat" else unsat if st == "unsat" else unk).append(q)
    P("      UNSAT periods: %s" % (unsat or "none"))
    P("      SAT periods  : %s" % (sat or "none"))
    P("      unknown      : %s" % (unk or "none"))
    # chance baseline
    rr2 = random.Random(6)
    POOL = "".join(ch * int(ENG[ch] * 100) for ch in A2Z)
    nsat = 0
    ntot = 0
    for _ in range(5):
        rc = [(pos, c, rr2.choice(POOL)) for pos, c, _ in CRIBS]
        for q in range(1, 31):
            ntot += 1
            if solve_period(q, rc, timeout=10.0) == "sat":
                nsat += 1
    P("      chance baseline: 5 random-plaintext crib sets x 30 periods = %d solves,"
      " %d SAT (%.2f per period)" % (ntot, nsat, nsat / ntot))
    P("      Read this as: the grid has 100 cells for 26 letters, so it has enough")
    P("      freedom to absorb the cribs at almost any period.  The model is")
    P("      therefore UNFALSIFIABLE from cribs alone; the SAT results carry no")
    P("      information, exactly as the random-plaintext baseline shows.")

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "matrix_a_output.txt"), "w") as f:
    f.write("\n".join(OUT) + "\n")
print("\n[written to matrix_a_output.txt]")
