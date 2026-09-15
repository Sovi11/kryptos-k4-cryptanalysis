"""(c) Tableau-as-lookup: key letter at K4 position i = tableau[row(i)][col(i)].

Families searched
-----------------
C0  Structural collapse theorem (proved computationally, not assumed).
C1  Baseline: key_i = A[(a + b*i) mod 26] for A in {plain, KRYPTOS} -- the family the
    collapse theorem reduces most of C2/C3 to.
C2  Fixed-modulus affine lookup: row = (r0 + p*i) mod R, col = (c0 + q*i) mod W,
    over every carved/ideal grid variant, every r0,p < R and c0,q < W.
C3  Free-modulus affine lookup: row = (r0 + p*i) mod mr, col = (c0 + q*i) mod mc,
    for every mr <= R and mc <= W (this is the literal "row = i mod r, col = i mod c
    for all plausible r and c" family, generalised with offsets and strides).
C4  Serial readings of the grid (raster, boustrophedon, column-major, anti-diagonal),
    forward and reversed, at every start offset.
C5  Physical co-location: the key letter for K4 position i is the character carved at
    the SAME (row, column) on the tableau panel.

Every test uses the constant-difference criterion, which covers all 26 rotations of the
key alphabet simultaneously, on top of the 24 (family, alphabet) combos.

Chance expectation
------------------
A single (key stream, combo) trial reproduces all 24 crib letters with probability
26^-24 = 1.86e-34; allowing the 26 free rotations makes it 26^-23 = 4.8e-33 per
(key stream, combo) pair.  Totals are reported per family.
"""
import os
import sys
import time
import itertools
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tableau_common import (PLAIN, KEYED, ALPHAS, COMBOS, combo_name, CRIB_POS, CRIB_PT,
                            K4_CT, RIGHT_ROWS, RIGHT_ROWS_IDEAL, LEFT_ROWS,
                            required_key_indices, decrypt, crib_matches, selftest,
                            FINDINGS, letters)

import numpy as np

OUT = []
def w(*a):
    OUT.append(" ".join(str(x) for x in a))


POS = np.array(CRIB_POS, dtype=np.int64)          # 24 crib positions, 0-indexed
# key-alphabet index look-up tables: given a letter's PLAIN index, its index in A
LUT = {nm: np.array([A.index(ch) for ch in PLAIN], dtype=np.uint8)
       for nm, A in ALPHAS.items()}
REQ = {cb: np.array(required_key_indices(cb), dtype=np.uint8) for cb in COMBOS}


# ------------------------------------------------------------------- grids ----
def build_grids():
    g = {}
    g["square26"] = [KEYED[i:] + KEYED[:i] for i in range(26)]              # 26x26 body
    g["body30_carved"] = [r[1:] for r in RIGHT_ROWS[1:27]]                  # labels stripped
    g["body30_ideal"] = [r[1:] for r in RIGHT_ROWS_IDEAL[1:27]]
    g["labeled31_carved"] = list(RIGHT_ROWS[1:27])
    g["labeled31_ideal"] = list(RIGHT_ROWS_IDEAL[1:27])
    g["full28_carved"] = list(RIGHT_ROWS)                                   # incl header/footer
    g["full28_ideal"] = list(RIGHT_ROWS_IDEAL)
    # column-major view of the carved panel: row k of this grid = column k read downward
    W = max(len(r) for r in RIGHT_ROWS)
    g["cols_carved"] = ["".join(r[c] for r in RIGHT_ROWS if c < len(r)) for c in range(W)]
    return g


GRIDS = build_grids()


def grid_lut(rows):
    """(R, W) uint8 array of PLAIN indices; short rows wrap cyclically."""
    R = len(rows)
    W = max(len(r) for r in rows)
    L = np.zeros((R, W), dtype=np.uint8)
    for r, row in enumerate(rows):
        for c in range(W):
            L[r, c] = PLAIN.index(row[c % len(row)])
    return L


# --------------------------------------------------------- the crib matcher ----
def match_counts(keyplain):
    """keyplain: (..., 24) uint8 of PLAIN indices.  Returns dict combo -> (best, hits24).

    A 'hit' is a key stream that reproduces ALL 24 crib letters for SOME rotation of the
    key alphabet, i.e. (key_j - req_j) mod 26 is the same for all j.
    """
    res = {}
    flat = np.ascontiguousarray(keyplain.reshape(-1, 24))
    for cb in COMBOS:
        k = LUT[cb[3]][flat]                       # indices in this combo's key alphabet
        # uint8-safe modular subtraction: k + (26 - req) stays < 52
        d = (k + (26 - REQ[cb])) % 26
        eq = (d == d[:, :1])
        m = eq.sum(axis=1, dtype=np.int16)
        best = int(m.max())
        hits = np.nonzero(m == 24)[0]
        res[cb] = (best, hits)
        del k, d, eq, m
    return res


def summarise(name, keyplain, ntrials_note=""):
    res = match_counts(keyplain)
    best = max(v[0] for v in res.values())
    nhit = sum(len(v[1]) for v in res.values())
    bestcb = [cb for cb in COMBOS if res[cb][0] == best][0]
    return best, nhit, bestcb, res


# =============================================================== C0 theorem ====
def c0_theorem():
    w("## C0. Structural collapse theorem\n")
    w("The Kryptos tableau is not an arbitrary key table: it is the Cayley table of Z/26")
    w("written in the KRYPTOS-keyed alphabet.  For the 26x26 body,")
    w("    T[r][c] = KEYED[(r + c) mod 26].")
    ok = all(KEYED[(r + c) % 26] == GRIDS["square26"][r][c]
             for r in range(26) for c in range(26))
    w("  verified for all 676 cells: %s" % ok)
    w("For the carved 30-letter rows the wrap columns repeat the body, and for the")
    w("labelled rows column 0 holds the row label:")
    ok2 = all(RIGHT_ROWS_IDEAL[1 + r][1 + c] == KEYED[(r + c) % 26]
              for r in range(26) for c in range(30))
    ok3 = all(RIGHT_ROWS_IDEAL[1 + r][0] == PLAIN[r] for r in range(26))
    w("  T_carved[r][1+c] == KEYED[(r+c) mod 26] for all r<26, c<30 : %s" % ok2)
    w("  T_carved[r][0]   == PLAIN[r]                               : %s" % ok3)
    w("")
    w("CONSEQUENCE.  If row(i) = (r0 + p*i) mod 26 and col(i) = (c0 + q*i) mod 26 (or any")
    w("moduli dividing 26 / any affine map whose crib cells all land in the BODY), then")
    w("    key_i = KEYED[(r0 + c0 + (p+q)*i) mod 26],")
    w("a plain arithmetic progression.  The two-dimensional lookup therefore carries NO")
    w("more information than a one-dimensional linear shift for every cell that is not")
    w("an exceptional cell.  The exceptional cells are exactly:")
    w("    * column 0 of the 26 lettered rows (the row-label letters)")
    w("    * the header row and the footer row (plain A..Z + ABCD, no label)")
    w("    * the single extra L at the end of row N")
    w("Linear shift models were already exhausted (findings/geometry.md: 0 of 1e8 models")
    w("fit; best 9/24).  C1 below reconfirms the KEYED-alphabet case directly, so the")
    w("brute forces in C2/C3 are only searching for maps that USE the exceptional cells.")
    w("")


# ============================================================== C1 baseline ====
def c1_linear():
    w("## C1. Baseline: key_i = A[(a + b*i) mod 26]\n")
    rows = []
    for anm, A in ALPHAS.items():
        arr = np.zeros((26, 26, 24), dtype=np.uint8)
        for a in range(26):
            for b in range(26):
                for j, pos in enumerate(CRIB_POS):
                    arr[a, b, j] = PLAIN.index(A[(a + b * pos) % 26])
        best, nhit, bestcb, res = summarise("linear/" + anm, arr)
        rows.append((anm, best, nhit, bestcb))
        w("  key alphabet %-5s : 26*26*24 = %d (a,b,combo) trials, x26 rotations."
          % (anm, 26 * 26 * 24))
        w("      24/24 hits: %d   best: %d/24 (%s)" % (nhit, best, combo_name(bestcb)))
    w("")
    w("  chance expectation of a 24/24 hit over %d trials: %.3g"
      % (2 * 26 * 26 * 24, 2 * 26 * 26 * 24 * 26.0 ** -23))
    w("")
    return rows


# ======================================================== C2 fixed modulus ====
def c2_fixed():
    w("## C2. Fixed-modulus affine lookup over every grid variant\n")
    w("  row(i) = (r0 + p*i) mod R,  col(i) = (c0 + q*i) mod W  (W = widest row;")
    w("  short rows wrap cyclically, so every (r,c) resolves to a carved letter).")
    w("")
    w("| grid | R x W | (r0,p,c0,q) tuples | x24 combos | 24/24 hits | expected by chance | best |")
    w("|---|---|---|---|---|---|---|")
    total = 0
    for name, rows in GRIDS.items():
        L = grid_lut(rows)
        R, W = L.shape
        rvec = (np.arange(R)[:, None, None] + np.arange(R)[None, :, None] * POS[None, None, :]) % R
        cvec = (np.arange(W)[:, None, None] + np.arange(W)[None, :, None] * POS[None, None, :]) % W
        rvec = rvec.reshape(-1, 24).astype(np.int32)       # (R*R, 24)
        cvec = cvec.reshape(-1, 24).astype(np.int32)       # (W*W, 24)
        key = L[rvec[:, None, :], cvec[None, :, :]]        # (R*R, W*W, 24)
        ntup = rvec.shape[0] * cvec.shape[0]
        best, nhit, bestcb, res = summarise(name, key)
        total += ntup * 24
        w("| %s | %dx%d | %d | %d | %d | %.3g | %d/24 (%s) |"
          % (name, R, W, ntup, ntup * 24, nhit, ntup * 24 * 26.0 ** -23, best,
             combo_name(bestcb)))
        if nhit:
            for cb in COMBOS:
                for h in res[cb][1]:
                    ri, ci = divmod(int(h), cvec.shape[0])
                    w("    HIT grid=%s combo=%s rowvec=%s colvec=%s"
                      % (name, combo_name(cb), rvec[ri], cvec[ci]))
        del key
    w("")
    w("  TOTAL C2 trials: %d ; expected 24/24 by chance: %.3g" % (total, total * 26.0 ** -23))
    w("")


# ========================================================= C3 free modulus ====
def _vecs(maxmod, pos):
    """Distinct index vectors (m0 + s*pos) mod m for every m<=maxmod, m0<m, s<m."""
    seen = {}
    for m in range(1, maxmod + 1):
        base = pos % m
        for m0 in range(m):
            for s in range(m):
                v = tuple(int((m0 + s * b) % m) for b in base)
                if v not in seen:
                    seen[v] = (m, m0, s)
    keys = list(seen)
    return np.array(keys, dtype=np.int32), [seen[k] for k in keys]


def c3_free(grid_names):
    w("## C3. Free-modulus affine lookup (the literal 'row = i mod r, col = i mod c' family)\n")
    w("  row(i) = (r0 + p*i) mod mr for every mr <= R,  col(i) = (c0 + q*i) mod mc for")
    w("  every mc <= W.  Index vectors are de-duplicated first (many (m,m0,s) triples")
    w("  give the same 24 indices), then every surviving pair is tested against all 24")
    w("  cipher combos with the all-rotations constant-difference criterion.")
    w("")
    w("| grid | raw (mr,r0,p) | distinct row vecs | raw (mc,c0,q) | distinct col vecs | pairs | x24 combos | hits | expected | best |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for name in grid_names:
        rows = GRIDS[name]
        L = grid_lut(rows)
        R, W = L.shape
        rv, rmeta = _vecs(R, POS)
        cv, cmeta = _vecs(W, POS)
        raw_r = sum(m * m for m in range(1, R + 1))
        raw_c = sum(m * m for m in range(1, W + 1))
        npair = len(rv) * len(cv)
        best = 0
        nhit = 0
        bestcb = COMBOS[0]
        t0 = time.time()
        CH = 256
        for cb in COMBOS:
            req = REQ[cb]
            lut = LUT[cb[3]]
            RI, CI, DR = [], [], []
            for s in range(0, len(rv), CH):
                rc = rv[s:s + CH]
                k0 = lut[L[rc[:, None, 0], cv[None, :, 0]]]
                d0 = (k0 + (26 - req[0])) % 26
                k1 = lut[L[rc[:, None, 1], cv[None, :, 1]]]
                d1 = (k1 + (26 - req[1])) % 26
                a, b_ = np.nonzero(d0 == d1)
                if len(a):
                    RI.append(a.astype(np.int32) + s)
                    CI.append(b_.astype(np.int32))
                    DR.append(d0[a, b_])
                del k0, k1, d0, d1
            if RI:
                ri = np.concatenate(RI); ci = np.concatenate(CI); dref = np.concatenate(DR)
            else:
                ri = ci = dref = np.zeros(0, dtype=np.int32)
            m = np.full(ri.shape, 2, dtype=np.int16)
            alive = np.ones(ri.shape, dtype=bool)
            for j in range(2, 24):
                kk = lut[L[rv[ri, j], cv[ci, j]]]
                good = ((kk + (26 - req[j])) % 26) == dref
                m += good
                alive &= good
                if not alive.any():
                    break
            b = int(m.max()) if len(m) else 2
            nh = int(alive.sum())
            nhit += nh
            if b > best:
                best, bestcb = b, cb
            if nh:
                for idx in np.nonzero(alive)[0][:5]:
                    w("    HIT grid=%s combo=%s row(m,m0,s)=%s col(m,m0,s)=%s"
                      % (name, combo_name(cb), rmeta[ri[idx]], cmeta[ci[idx]]))
        w("| %s | %d | %d | %d | %d | %d | %d | %d | %.3g | >=%d/24 (%s) |"
          % (name, raw_r, len(rv), raw_c, len(cv), npair, npair * 24, nhit,
             npair * 24 * 26.0 ** -23, best, combo_name(bestcb)))
        w("    (%.1f s)" % (time.time() - t0))
    w("")
    w("  NOTE the 'best' column counts only streams that pass the first two crib letters")
    w("  consistently; streams failing that can never reach 24/24, so the hit counts are")
    w("  exact even though the best-fit statistic is a lower bound.")
    w("")


# ============================================================ C4 serial reads ====
def c4_serial():
    w("## C4. Serial readings of the carved panel\n")
    reads = {}
    for gname in ("full28_carved", "full28_ideal", "labeled31_carved", "cols_carved"):
        rows = GRIDS[gname]
        reads[gname + "/raster"] = "".join(rows)
        reads[gname + "/boustro"] = "".join(r if i % 2 == 0 else r[::-1]
                                            for i, r in enumerate(rows))
        Wm = max(len(r) for r in rows)
        reads[gname + "/colmajor"] = "".join("".join(r[c] for r in rows if c < len(r))
                                             for c in range(Wm))
        # anti-diagonals of the rectangular core
        R = len(rows)
        diag = []
        for d in range(R + Wm):
            for r in range(R):
                c = d - r
                if 0 <= c < len(rows[r]):
                    diag.append(rows[r][c])
        reads[gname + "/antidiag"] = "".join(diag)
    allr = dict(reads)
    for k, v in reads.items():
        allr[k + "_rev"] = v[::-1]

    w("| reading | letters | offsets | x24 combos | 24/24 hits | expected | best |")
    w("|---|---|---|---|---|---|---|")
    grand = 0
    for name, txt in sorted(allr.items()):
        n = len(txt)
        offs = [o for o in range(n) if o + 96 < n]
        if not offs:
            offs = [0]
        arr = np.zeros((len(offs), 24), dtype=np.uint8)
        for k, o in enumerate(offs):
            for j, pos in enumerate(CRIB_POS):
                arr[k, j] = PLAIN.index(txt[(o + pos) % n])
        best, nhit, bestcb, res = summarise(name, arr)
        grand += len(offs) * 24
        w("| %s | %d | %d | %d | %d | %.3g | %d/24 (%s) |"
          % (name, n, len(offs), len(offs) * 24, nhit, len(offs) * 24 * 26.0 ** -23,
             best, combo_name(bestcb)))
    w("")
    w("  TOTAL C4 trials: %d ; expected 24/24 by chance: %.3g" % (grand, grand * 26.0 ** -23))
    w("")


# ======================================================== C5 co-location ====
def c5_colocation():
    w("## C5. Physical co-location (same row, same column on the two panels)\n")
    w("K4 = last 4 chars of left row 25 + all of left rows 26,27,28 (1-indexed).")
    w("Reading the tableau panel at the same (row, column):")
    base = RIGHT_ROWS[24][27:31] + RIGHT_ROWS[25] + RIGHT_ROWS[26] + RIGHT_ROWS[27]
    w("  gives only %d letters -- the footer row carries 30 letters, not 31, because it")
    w("  has no row-label letter.  Six ways to patch the missing 97th position:" % len(base))
    variants = {}
    head = RIGHT_ROWS[24][27:31] + RIGHT_ROWS[25] + RIGHT_ROWS[26]
    foot = RIGHT_ROWS[27]
    for ch in "ZAK":
        variants["footer prefixed with %s" % ch] = head + ch + foot
    variants["footer suffixed with E (wrap)"] = head + foot + "E"
    variants["footer = plain A..Z + ABCDE"] = head + PLAIN + "ABCDE"
    variants["drop K4 pos 97"] = (head + foot)[:96] + (head + foot)[-1]
    # solvekryptos' 'basis handoff': the footer is re-read as if it were row Z of the tableau
    variants["footer re-read as row Z body"] = head + RIGHT_ROWS[26][1:] + "Y"
    w("")
    w("| keystream variant | 24/24 hits (24 combos x 26 rotations) | best | best combo |")
    w("|---|---|---|---|")
    for nm, ks in variants.items():
        assert len(ks) == 97, (nm, len(ks))
        arr = np.array([[PLAIN.index(ks[pos]) for pos in CRIB_POS]], dtype=np.uint8)
        best, nhit, bestcb, res = summarise(nm, arr)
        w("| %s | %d | %d/24 | %s |" % (nm, nhit, best, combo_name(bestcb)))
    w("")
    w("  trials: %d keystreams x 24 combos x 26 rotations = %d ; expected 24/24: %.3g"
      % (len(variants), len(variants) * 24 * 26, len(variants) * 24 * 26.0 ** -23))
    w("")
    w("For the record, the unrotated decryptions of the canonical variant under the eight")
    w("Vigenere combos (none reproduces the cribs):")
    ks = variants["footer prefixed with Z"]
    w("  keystream: %s" % ks)
    for cb in COMBOS[:8]:
        pt = decrypt(cb, ks)
        w("   %-38s %s   cribs %d/24" % (combo_name(cb), pt, crib_matches(cb, ks)))
    w("")


def main():
    selftest()
    w("# (c) Tableau-as-lookup: a finite, quantified family\n")
    c0_theorem()
    c1_linear()
    c2_fixed()
    c3_free(["full28_carved", "full28_ideal", "labeled31_carved", "square26"])
    c4_serial()
    c5_colocation()
    print("\n".join(OUT))
    with open(os.path.join(FINDINGS, "tableau_c_out.txt"), "w") as f:
        f.write("\n".join(OUT) + "\n")


if __name__ == "__main__":
    main()
