"""(b) The tableau as a LOOKUP TABLE: key_i = tableau[row(i)][col(i)].

Structure of the argument
-------------------------
B0  COLLAPSE THEOREM, proved computationally rather than assumed: every cell of the
    carved tableau BODY -- including the anomalous extra L -- equals KEYED[(row+col) mod
    26].  The only cells that are not that function are the 26 row labels (plain
    alphabet) and the two header/footer rows.  Consequence: any lookup into the body,
    however exotic the path, delivers a key stream that depends on (row_i + col_i) only.
B1  The literal family in the brief: row = i mod r, col = i mod c, every r and c.
B2  Full affine generalisation: row = (r0 + p*i) mod mr, col = (c0 + q*i) mod mc, for
    EVERY mr, mc, r0, p, c0, q.  Solved exactly and exhaustively by a hash join rather
    than by enumeration, so the whole family is covered, not sampled.
B3  Diagonal, anti-diagonal, and constant knight's-move walks (all special cases of B2,
    reported separately because the brief names them), plus alternating knight moves,
    which are not.
B4  Non-additive grids: the label column, the header/footer rows, and the full 28-row
    carved panel, where the collapse theorem does NOT apply -- swept directly.
B5  Serial readings of the grid (raster, boustrophedon, column-major, spiral, diagonal
    stripes) at every start offset, forward and reversed.

Chance expectation is quoted for every family: a (key stream, combo) trial with the key
alphabet rotation free reproduces all 24 crib letters with probability 26^-23 = 4.84e-33.
"""
import os
import sys
import math
import time
import itertools
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import tab_common as T
from tab_common import (PLAIN, KEYED, ALPHAS, COMBOS, combo_name, CRIB_POS, CRIB_PT,
                        K4_CT, RIGHT_ROWS, RIGHT_ROWS_IDEAL, LEFT_ROWS, POS, REQ, IDX,
                        crib_match_matrix, expected_hits, FINDINGS)

OUT = []
def w(*a):
    OUT.append(" ".join(str(x) for x in a))


KEYED_OF_PLAIN = np.array([KEYED.index(c) for c in PLAIN], dtype=np.int64)   # plain->keyed idx
PLAIN_OF_KEYED = np.array([PLAIN.index(c) for c in KEYED], dtype=np.int64)   # keyed->plain idx


def rate(k):
    return T.rate_bound(k)


def sweep(li, tag_fn=None):
    """li: (N,24) PLAIN letter indices of the candidate key letters.
    Returns (n_hits_24, best_count, best_meta) over all 24 combos and 26 rotations."""
    hits = 0
    best = (-1, None)
    for cb in COMBOS:
        ak = cb[3]
        kidx = li if ak == "plain" else KEYED_OF_PLAIN[li]
        b, rot, e = crib_match_matrix(kidx, cb)
        hits += int((b == 24).sum())
        m = int(b.argmax())
        if int(b[m]) > best[0]:
            meta = (combo_name(cb), int(rot[m]))
            if tag_fn is not None:
                meta = tag_fn(m) + meta
            best = (int(b[m]), meta)
    return hits, best[0], best[1]


def show_decrypt(label, cb, key_letters):
    r = T.score_report(cb, key_letters)
    w("    %s -> cribs %d/24" % (label, r["cribs"]))
    w("      plaintext : %s" % r["marked"])
    w("      bigram %.3f (English ~-5.3, random median -7.50, random 99th pct -7.05), IoC %.4f"
      % (r["bigram"], r["ioc"]))


# ==================================================================== B0 =======
def b0_collapse():
    w("## B0. The collapse theorem\n")
    body_carved = [r[1:] for r in RIGHT_ROWS[1:27]]
    body_ideal = [r[1:] for r in RIGHT_ROWS_IDEAL[1:27]]
    bad = []
    for i, row in enumerate(body_carved):
        for j, ch in enumerate(row):
            if ch != KEYED[(i + j) % 26]:
                bad.append((i, j, ch, KEYED[(i + j) % 26]))
    w("Carved body (labels stripped), %d rows of widths %s:"
      % (len(body_carved), sorted(set(len(r) for r in body_carved))))
    w("  cells where carved != KEYED[(row+col) mod 26] : %d" % len(bad))
    if bad:
        for b in bad:
            w("    row %d col %d carved %s expected %s" % b)
    w("")
    i, j = 13, 30
    w("The anomalous extra L is at body row 13 (label N), column 30 (0-indexed).")
    w("  KEYED[(13+30) mod 26] = KEYED[%d] = %r ; carved = %r"
      % ((i + j) % 26, KEYED[(i + j) % 26], body_carved[13][30]))
    w("  So the extra L is not a WRONG letter -- it is the RIGHT letter in an extra")
    w("  column.  The carver continued the row's own rotation one step too far.  This is")
    w("  what a miscount looks like and not what a planted signal looks like, and it")
    w("  means the carved body and the ideal body are the SAME function of (row, col).")
    w("")
    lab_bad = [(i, RIGHT_ROWS[i + 1][0], KEYED[(i + 0) % 26])
               for i in range(26) if RIGHT_ROWS[i + 1][0] != KEYED[i % 26]]
    w("Cells that are NOT that function: the 26 row labels (they are the PLAIN alphabet,")
    w("  not the keyed one -- %d of the 26 differ from KEYED[row]; only label Z coincides)"
      % len(lab_bad))
    w("  and the 2 header/footer rows (plain A-Z + ABCD).  Those are handled in B4.")
    w("")
    w("CONSEQUENCE, and it is the main structural result of this task: for any lookup")
    w("path through the tableau body, key_i = KEYED[(row_i + col_i) mod 26].  The two")
    w("coordinates are not independent sources of key material -- only their sum matters.")
    w("A 26x30 table of 780 cells therefore carries exactly 26 distinct key values, i.e.")
    w("log2(26) = 4.7 bits per position, the same as a bare shift.  'Looking the key up in")
    w("the tableau' is arithmetically identical to 'adding two position functions mod 26'.")
    w("")
    return len(bad) == 0


# ==================================================================== B1 =======
def b1_literal():
    w("## B1. The literal family: row = i mod r, col = i mod c\n")
    w("| grid | r range | c range | models | trials (x24 combos) | 24/24 hits | expected | best |")
    w("|---|---|---|---|---|---|---|---|")
    grids = _grids()
    grand = 0
    for gname, (G, rowlen) in grids.items():
        R, C = G.shape[0], G.shape[1]
        rowsM, tags = [], []
        for r in range(1, R + 1):
            rows = (POS % r)
            for c in range(1, C + 1):
                eff = (POS % c) % rowlen[rows]
                rowsM.append(G[rows, eff])
                tags.append((r, c))
        li = np.array(rowsM, dtype=np.int64)
        models = li.shape[0]
        hits, bc, bm = sweep(li, lambda m: tags[m])
        best = (bc, bm)
        trials = models * 24
        grand += trials
        w("| %s | 1..%d | 1..%d | %s | %s | %d | %.3g | %d/24 r=%d c=%d %s |"
          % (gname, R, C, f"{models:,}", f"{trials:,}", hits, expected_hits(trials),
             best[0], best[1][0], best[1][1], best[1][2]))
    w("")
    w("  total trials in B1: %s ; expected 24/24 by chance %.3g"
      % (f"{grand:,}", expected_hits(grand)))
    w("  P(a random stream reaching 7/24) <= %.3g, 8/24 <= %.3g -- the bests above are"
      % (rate(7), rate(8)))
    w("  what this many trials is supposed to produce.")
    w("")


# ==================================================================== B2 =======
def _affine_params(M):
    """All (modulus, stride, offset) with 1<=m<=M, 0<=p<m, 0<=o<m; returns (n,24) values."""
    vals = []
    meta = []
    for m in range(1, M + 1):
        for p in range(m):
            for o in range(m):
                vals.append((o + p * POS) % m)
                meta.append((m, p, o))
    return np.array(vals, dtype=np.int64), meta


_HASH_W = None


def _hashes(mat):
    """Polynomial hash of each row of a (n,23) array of values 0..25."""
    global _HASH_W
    if _HASH_W is None:
        rs = np.random.RandomState(12345)
        _HASH_W = rs.randint(1, 2 ** 31, size=23).astype(np.int64)
    return (mat.astype(np.int64) * _HASH_W[None, :]).sum(axis=1)


def b2_affine_exact():
    w("## B2. The FULL affine lookup family, solved exactly\n")
    w("Model: row_i = (r0 + p*i) mod mr, col_i = (c0 + q*i) mod mc, key_i =")
    w("KEYED[(row_i + col_i + t) mod 26] by B0.  Free: mr, p, r0, mc, q, c0, t, the combo.")
    w("")
    R, C = 28, 32
    A, Ameta = _affine_params(R)
    B, Bmeta = _affine_params(C)
    nrow, ncol = len(Ameta), len(Bmeta)
    family = nrow * ncol
    w("  row parameter triples (mr<=%d): %s" % (R, f"{nrow:,}"))
    w("  col parameter triples (mc<=%d): %s" % (C, f"{ncol:,}"))
    w("  coordinate models: %s x %s = %s" % (f"{nrow:,}", f"{ncol:,}", f"{family:,}"))
    w("  x 24 combos x 26 key rotations = %s trials" % f"{family * 24 * 26:,}")
    w("  expected 24/24 by chance: %s * 26^-24 = %.3g"
      % (f"{family * 24 * 26:,}", family * 24 * 26 * 26.0 ** -24))
    w("")
    w("Solved by hash join, not enumeration.  The crib condition is")
    w("  PLAINidx_or_KEYEDidx( KEYED[(a_j + b_j + t) mod 26] ) = req_j + rot   for all j,")
    w("which for each of the 26 candidate rot values inverts to a required sum vector")
    w("v_j, and the condition becomes (a_j - v_j) + b_j = const -- separable in the row")
    w("and column parameters, hence an exact O(nrow + ncol) join per (combo, rot).")
    w("")
    t0 = time.time()
    # normalised column vectors (independent of combo)
    nb = (-(B[:, 1:] - B[:, :1])) % 26
    hb = _hashes(nb)
    order = np.argsort(hb, kind="stable")
    hb_sorted = hb[order]
    na = (A[:, 1:] - A[:, :1]) % 26
    total_checked = 0
    exact_hits = []
    for cb in COMBOS:
        ak = cb[3]
        req = REQ[cb]
        for rot in range(26):
            # required key letter at each crib position, as an index into KEYED
            want_plain = np.array([ALPHAS[ak][(int(req[j]) + rot) % 26] for j in range(24)])
            v = np.array([KEYED.index(ch) for ch in want_plain], dtype=np.int64)
            nv = (v[1:] - v[0]) % 26
            da = (na - nv[None, :]) % 26
            ha = _hashes(da)
            lo = np.searchsorted(hb_sorted, ha, side="left")
            hi = np.searchsorted(hb_sorted, ha, side="right")
            total_checked += nrow
            pairs = []
            for x in np.nonzero(hi > lo)[0]:
                for k in range(lo[x], hi[x]):
                    pairs.append((int(x), int(order[k])))
            for x, y in pairs:
                # exact verification, no reliance on the hash
                kk = KEYED_OF_PLAIN if ak == "keyed" else None
                a_, b_ = A[x], B[y]
                lett = [KEYED[(int(a_[j]) + int(b_[j])) % 26] for j in range(24)]
                got = [ALPHAS[ak].index(ch) for ch in lett]
                if all((got[j] - int(req[j])) % 26 == (got[0] - int(req[0])) % 26
                       for j in range(24)):
                    exact_hits.append((cb, rot, Ameta[x], Bmeta[y]))
    w("  hash join complete in %.1fs ; verified 24/24 solutions: %d ; expected %.3g"
      % (time.time() - t0, len(exact_hits), family * 24 * 26 * 26.0 ** -24))
    for cb, rot, am, bm in exact_hits[:20]:
        w("    %s rot=%d row(mr,p,r0)=%s col(mc,q,c0)=%s" % (combo_name(cb), rot, am, bm))
    if not exact_hits:
        w("    NONE.  The entire affine lookup family is eliminated, exactly, not sampled.")
    w("")
    return exact_hits


# ==================================================================== B3 =======
def b3_walks():
    w("## B3. Diagonal, anti-diagonal and knight's-move walks\n")
    w("Constant-step walks (including both diagonals and all 8 knight moves) are the")
    w("special case p,q in {+-1,+-2} of B2 and are therefore already eliminated exactly.")
    w("Listed here explicitly, with their best crib fit, because the brief names them:")
    w("")
    grids = _grids()
    G, rowlen = grids["body30_carved"]
    R, C = G.shape
    walks = {"main diagonal (+1,+1)": (1, 1), "anti-diagonal (+1,-1)": (1, -1),
             "(+1,+2)": (1, 2), "(+2,+1)": (2, 1), "(+1,-2)": (1, -2), "(+2,-1)": (2, -1),
             "(-1,+2)": (-1, 2), "(-2,+1)": (-2, 1), "(-1,-2)": (-1, -2), "(-2,-1)": (-2, -1),
             "(+2,+3) leaper (not a knight move)": (2, 3), "row-only (+1,0)": (1, 0), "col-only (0,+1)": (0, 1)}
    w("| walk | best over all starts, 24 combos, 26 rotations | P(>=best) |")
    w("|---|---|---|")
    trials = 0
    for nm, (dr, dc) in walks.items():
        mats, tags = [], []
        for r0 in range(R):
            for c0 in range(C):
                rows = (r0 + dr * POS) % R
                eff = ((c0 + dc * POS) % C) % rowlen[rows]
                mats.append(G[rows, eff])
                tags.append((r0, c0))
        li = np.array(mats, dtype=np.int64)
        trials += li.shape[0] * 24
        _, bc, bm = sweep(li, lambda m: tags[m])
        w("| %s | %d/24 at start (%d,%d) %s rot=%d | %.3g |"
          % (nm, bc, bm[0], bm[1], bm[2], bm[3], rate(bc)))
    w("")
    w("  constant-step walk trials: %s ; 24/24 hits 0 ; expected %.3g"
      % (f"{trials:,}", expected_hits(trials)))
    w("")
    # alternating knight moves -- genuinely outside B2
    w("Alternating knight's moves (step vectors alternate between two of the 8), which")
    w("are NOT in the affine family:")
    moves = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
    best = (-1, None)
    n_alt = 0
    for m1 in moves:
        for m2 in moves:
            dr = np.where(np.arange(97) % 2 == 0, m1[0], m2[0])
            dc = np.where(np.arange(97) % 2 == 0, m1[1], m2[1])
            cr = np.concatenate([[0], np.cumsum(dr)[:-1]])
            cc = np.concatenate([[0], np.cumsum(dc)[:-1]])
            mats, tags = [], []
            for r0 in range(R):
                for c0 in range(C):
                    rows = (r0 + cr[POS]) % R
                    eff = ((c0 + cc[POS]) % C) % rowlen[rows]
                    mats.append(G[rows, eff])
                    tags.append((m1, m2, r0, c0))
            li = np.array(mats, dtype=np.int64)
            n_alt += li.shape[0] * 24
            _, bc, bm = sweep(li, lambda m: tags[m])
            if bc > best[0]:
                best = (bc, bm)
    w("  trials %s ; best %d/24 at %s ; P(>=%d) <= %.3g ; expected 24/24 %.3g"
      % (f"{n_alt:,}", best[0], best[1], best[0], rate(best[0]), expected_hits(n_alt)))
    w("")
    w("A genuine non-repeating knight's TOUR is not testable as a family: the number of")
    w("open tours on a 26x30 board is astronomically large and no canonical one is named")
    w("by the sculpture, so a 'tour' hypothesis has more free parameters than the 97")
    w("letters it would explain.  It is excluded on parsimony, not by search, and this")
    w("report says so rather than pretending to have covered it.")
    w("")


# ==================================================================== B4 =======
def b4_nonadditive():
    w("## B4. The grids where the collapse theorem does NOT hold\n")
    w("The row-label column and the header/footer rows are plain-alphabet, so grids that")
    w("include them are not a function of (row+col).  Those are swept directly.")
    w("")
    grids = _grids(include_labels=True)
    w("| grid | shape | models (r,c sweep incl. offsets) | trials | 24/24 | expected | best | E[#>=best] |")
    w("|---|---|---|---|---|---|---|---|")
    grand = 0
    allbest = []
    for gname, (G, rowlen) in grids.items():
        R, C = G.shape
        mats, tags = [], []
        for mr in range(1, R + 1):
            for r0 in range(mr):
                rows = (r0 + POS) % mr
                for mc in range(1, C + 1):
                    for c0 in range(mc):
                        eff = ((c0 + POS) % mc) % rowlen[rows]
                        mats.append(G[rows, eff])
                        tags.append((mr, r0, mc, c0))
        li = np.array(mats, dtype=np.int64)
        models = li.shape[0]
        hits, bc, bm = sweep(li, lambda m: tags[m])
        best = (bc, bm)
        trials = models * 24
        grand += trials
        allbest.append((bc, gname, bm, G, rowlen))
        w("| %s | %dx%d | %s | %s | %d | %.3g | %d/24 %s | %.2f |"
          % (gname, R, C, f"{models:,}", f"{trials:,}", hits, expected_hits(trials),
             best[0], best[1], trials * rate(best[0])))
    w("")
    w("  total B4 trials %s ; expected 24/24 %.3g" % (f"{grand:,}", expected_hits(grand)))
    bc, gname, bm, G, rowlen = max(allbest)
    mr, r0, mc, c0, cbname, rot = bm
    cb = [c for c in COMBOS if combo_name(c) == cbname][0]
    ak = cb[3]
    idx97 = np.arange(97)
    rows = (r0 + idx97) % mr
    eff = ((c0 + idx97) % mc) % rowlen[rows]
    li = G[rows, eff]
    ks = "".join(ALPHAS[ak][(ALPHAS[ak].index(PLAIN[int(x)]) + rot) % 26] for x in li)
    w("  The single best model in B4, decrypted in full:")
    show_decrypt("%s mr=%d r0=%d mc=%d c0=%d %s" % (gname, mr, r0, mc, c0, cbname), cb, ks)
    w("  Its %d/24 is reached by chance %.2f times in %s trials, so it is not a lead."
      % (bc, grand * rate(bc), f"{grand:,}"))
    w("")


# ==================================================================== B5 =======
def b5_serial():
    w("## B5. Serial readings of the grid as running keys\n")
    w("Raster, boustrophedon, column-major, diagonal-stripe and spiral traversals of each")
    w("grid, forward and reversed, at every start offset.")
    reads = {}
    for gname, rows in (("carved body", [r[1:] for r in RIGHT_ROWS[1:27]]),
                        ("carved labelled", list(RIGHT_ROWS[1:27])),
                        ("carved full 28", list(RIGHT_ROWS)),
                        ("ideal full 28", list(RIGHT_ROWS_IDEAL))):
        reads[gname + " raster"] = "".join(rows)
        reads[gname + " boustrophedon"] = "".join(r if i % 2 == 0 else r[::-1]
                                                  for i, r in enumerate(rows))
        wmax = max(len(r) for r in rows)
        reads[gname + " column-major"] = "".join(r[c] for c in range(wmax) for r in rows
                                                 if c < len(r))
        reads[gname + " diagonals"] = "".join(
            rows[i][d - i] for d in range(len(rows) + wmax)
            for i in range(len(rows)) if 0 <= d - i < len(rows[i]))
    w("")
    w("| reading | len | best (all starts x 24 combos x 26 rot) | P(>=best) | 24/24 | expected |")
    w("|---|---|---|---|---|---|")
    grand = 0
    for nm, s in sorted(reads.items()):
        for suffix, txt in ((" ", s), (" reversed", s[::-1])):
            L = len(txt)
            si = {a: T.as_idx(txt, a) for a in ("plain", "keyed")}
            best = (-1, None)
            hits = 0
            n = 0
            gather = (np.arange(L, dtype=np.int64)[:, None] + POS[None, :]) % L
            for cb in COMBOS:
                kidx = si[cb[3]][gather]
                b, rot, e = crib_match_matrix(kidx, cb)
                n += L
                hits += int((b == 24).sum())
                if int(b.max()) > best[0]:
                    o = int(b.argmax())
                    best = (int(b[o]), (o, combo_name(cb), int(rot[o])))
            grand += n * 1
            w("| %s%s | %d | %d/24 at %s | %.3g | %d | %.3g |"
              % (nm, suffix, L, best[0], best[1], rate(best[0]), hits, expected_hits(n)))
    w("")
    w("  total B5 trials %s ; expected 24/24 %.3g" % (f"{grand:,}", expected_hits(grand)))
    w("")


# ------------------------------------------------------------------ grids -----
def _pad(rows, fill=-1):
    R = len(rows)
    C = max(len(r) for r in rows)
    G = np.full((R, C), fill, dtype=np.int64)
    rl = np.zeros(R, dtype=np.int64)
    for i, r in enumerate(rows):
        rl[i] = len(r)
        for j, ch in enumerate(r):
            G[i, j] = PLAIN.index(ch)
    return G, rl


def _grids(include_labels=False):
    body_c = [r[1:] for r in RIGHT_ROWS[1:27]]
    body_i = [r[1:] for r in RIGHT_ROWS_IDEAL[1:27]]
    core = [KEYED[i:] + KEYED[:i] for i in range(26)]
    if not include_labels:
        return {"core26 (26x26)": _pad(core),
                "body30_carved": _pad(body_c),
                "body30_ideal": _pad(body_i)}
    return {"labelled31_carved": _pad(list(RIGHT_ROWS[1:27])),
            "labelled31_ideal": _pad(list(RIGHT_ROWS_IDEAL[1:27])),
            "full28_carved": _pad(list(RIGHT_ROWS)),
            "full28_ideal": _pad(list(RIGHT_ROWS_IDEAL))}


def main():
    T.selftest()
    w("# (b) The tableau as a key TABLE: an exact, exhaustive elimination\n")
    w("Null calibration: for a random 24-letter key stream the best-over-26-rotations crib")
    w("match has mean 3.25; P(>=6) <= %.3g, P(>=7) <= %.3g, P(>=8) <= %.3g, P(>=9) <= %.3g."
      % (rate(6), rate(7), rate(8), rate(9)))
    w("")
    ok = b0_collapse()
    assert ok, "collapse theorem failed -- everything below assumes it"
    b1_literal()
    b2_affine_exact()
    b3_walks()
    b4_nonadditive()
    b5_serial()
    txt = "\n".join(OUT) + "\n"
    print(txt)
    with open(os.path.join(FINDINGS, "tab_b_out.txt"), "w") as f:
        f.write(txt)


if __name__ == "__main__":
    main()
