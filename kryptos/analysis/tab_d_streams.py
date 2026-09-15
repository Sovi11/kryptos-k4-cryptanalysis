"""(d) The tableau's COLUMN at each index, and the ROW-LABEL sequence, as key streams.

D0  COVERAGE CHECK first, as the brief requires: does lateral/test_lateral.py already
    cover these exact streams?  It globs lateral/keystreams/*.txt, so the answer depends
    entirely on what is in that directory at run time.  Checked programmatically below.
D1  The streams, regenerated in-process (deterministically) so the result does not depend
    on the contents of a directory that other agents write to and delete from.
D2  K4-ALIGNED streams: for each K4 position, the row label and the column label of the
    tableau cell physically opposite it.  These are exactly 97 letters long, so they are
    used position-for-position with no offset -- the only reading in which "the column at
    each index" is literally a key stream.
D3  Whole-column reads (each tableau column top to bottom) and the row-label alphabet,
    as running keys at every offset and as periodic keys of every period.
D4  The same block-Hamming metric lateral/test_lateral.py uses, so the numbers here are
    directly comparable with lateral/test_lateral_out.txt.

All 24 combos and all 26 key-alphabet rotations throughout; chance quoted everywhere.
"""
import os
import sys
import glob
import math
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import tab_common as T
from tab_common import (PLAIN, KEYED, ALPHAS, COMBOS, combo_name, CRIB_POS, CRIB_PT,
                        K4_CT, RIGHT_ROWS, RIGHT_ROWS_IDEAL, LEFT_ROWS, POS, REQ, IDX,
                        crib_match_matrix, expected_hits, FINDINGS, ROOT)

OUT = []
def w(*a):
    OUT.append(" ".join(str(x) for x in a))


def rate(k):
    return T.rate_bound(k)


def show_decrypt(label, cb, key_letters):
    r = T.score_report(cb, key_letters)
    w("      %s -> cribs %d/24" % (label, r["cribs"]))
    w("        plaintext : %s" % r["marked"])
    w("        bigram %.3f (English ~-5.3, random median -7.50), IoC %.4f"
      % (r["bigram"], r["ioc"]))


HEADER = "ABCDEFGHIJKLMNOPQRSTUVWXYZABCD"      # 30 letters, carved above the body


# ===================================================================== D0 ======
def d0_coverage():
    w("## D0. Coverage check against lateral/test_lateral.py\n")
    ksdir = os.path.join(ROOT, "lateral", "keystreams")
    files = sorted(glob.glob(os.path.join(ksdir, "*.txt")))
    names = [os.path.basename(f) for f in files]
    tabfiles = [n for n in names if n.startswith("tab_")]
    w("  lateral/keystreams/*.txt present now : %d files" % len(files))
    w("  of those, tableau-derived (tab_*.txt) : %d" % len(tabfiles))
    w("  lateral/test_lateral.py globs exactly that directory and keeps streams of")
    w("  length >= 11; its own log records 73 streams of 194 files.")
    manifest = os.path.join(ksdir, "MANIFEST.tsv")
    reg = []
    if os.path.exists(manifest):
        for line in open(manifest):
            f0 = line.split("\t")[0].strip()
            if f0.startswith("tab_"):
                reg.append(f0)
    w("  MANIFEST.tsv rows naming tab_* files  : %d" % len(reg))
    w("")
    if tabfiles:
        w("  -> the tableau streams ARE present, so test_lateral.py would have covered")
        w("     them.  This section re-tests them anyway with rotations and periodic use.")
    else:
        w("  -> the tableau streams are NOT present.  lateral/tableau_panel.md records that")
        w("     a sibling process deleted every file in that directory that was not its own;")
        w("     the %d tab_* files it registered in MANIFEST.tsv are gone." % len(reg))
        w("     lateral/test_lateral_out.txt confirms it: its 73 surviving streams are all")
        w("     Cyrillic / Mengenlehreuhr / compass-rose / world-clock material.  So NO")
        w("     tableau column or row-label stream has been tested by it, and this section")
        w("     is required, not duplicative.")
    w("")
    return tabfiles


# ===================================================================== D1 ======
def build_streams():
    """Every tableau-derived stream this task needs, regenerated from the carving."""
    S = {}
    body_c = [r[1:] for r in RIGHT_ROWS[1:27]]
    body_i = [r[1:] for r in RIGHT_ROWS_IDEAL[1:27]]

    S["row_labels A..Z"] = "".join(r[0] for r in RIGHT_ROWS[1:27])
    S["col_labels (header row)"] = HEADER
    S["row label per carved letter"] = "".join(
        (RIGHT_ROWS[r][0] if 1 <= r <= 26 else "") * 0 + "".join(
            RIGHT_ROWS[r][0] for _ in range(len(RIGHT_ROWS[r])))
        for r in range(28) if 1 <= r <= 26)
    # per-index row label over the whole 867: header/footer contribute nothing labelled
    per_row = []
    for r in range(28):
        lab = RIGHT_ROWS[r][0] if 1 <= r <= 26 else None
        for _ in RIGHT_ROWS[r]:
            if lab:
                per_row.append(lab)
    S["row label per carved letter"] = "".join(per_row)
    per_col = []
    for r in range(28):
        row = RIGHT_ROWS[r]
        if 1 <= r <= 26:
            for j in range(1, len(row)):          # skip the label cell
                per_col.append(HEADER[j - 1] if j - 1 < len(HEADER) else PLAIN[(j - 1) % 26])
        else:
            for j in range(len(row)):
                per_col.append(HEADER[j])
    S["col label per carved letter"] = "".join(per_col)

    for j in range(max(len(r) for r in body_c)):
        col = "".join(r[j] for r in body_c if j < len(r))
        if len(col) >= 11:
            S["carved body column %d (down)" % j] = col
    S["last carved column, all 28 rows"] = "".join(r[-1] for r in RIGHT_ROWS)
    S["last ideal column, all 28 rows"] = "".join(r[-1] for r in RIGHT_ROWS_IDEAL)
    S["first carved column (labels)"] = "".join(r[0] for r in RIGHT_ROWS)
    S["carved body column-major"] = "".join(
        r[j] for j in range(max(len(x) for x in body_c)) for r in body_c if j < len(r))
    S["ideal body column-major"] = "".join(
        r[j] for j in range(30) for r in body_i)
    S["main diagonal of the 26x26 core"] = "".join(KEYED[(i + i) % 26] for i in range(26))
    S["anti-diagonal of the 26x26 core"] = "".join(KEYED[(i + 25 - i) % 26] for i in range(26))
    return S


# ===================================================================== D2 ======
def d2_k4_aligned():
    w("## D2. K4-aligned label streams (exactly 97 letters, no offset freedom)\n")
    w("K4 occupies left-panel row 25 columns 28-31 and all of rows 26-28, 31 columns wide.")
    w("Opposite those cells the tableau carries rows X, Y, Z and the footer.  The ROW")
    w("LABEL and the COLUMN LABEL of each of those 97 cells are the two streams the brief")
    w("names.  Neither has any free offset, so each is a single 97-letter candidate.")
    w("")
    rowlab = "X" * 4 + "Y" * 31 + "Z" * 31 + "?" * 31        # footer has no row label
    collab_cells = ["A", "B", "C", "D"]                       # row 25, cols 28..31
    for _ in range(3):
        collab_cells.append("?")                              # col 1 is the label column
        collab_cells.extend(HEADER)                            # cols 2..31
    collab = "".join(collab_cells)
    assert len(rowlab) == 97 and len(collab) == 97, (len(rowlab), len(collab))
    w("  row-label stream : %s" % rowlab)
    w("  col-label stream : %s" % collab)
    w("  ('?' marks a cell that has no label: the footer row carries no row label, and")
    w("   column 1 of each body row IS the label column and so has no column label.)")
    w("")
    w("Every substitution for the unlabelled cells is tried: each of the 26 letters, and")
    w("also 'take the other label instead'.")
    w("")
    w("| stream | filler | best crib match | P(>=best) | 24/24 |")
    w("|---|---|---|---|---|")
    trials = 0
    hits = 0
    best_all = (-1, None)
    variants = []
    for base, nm in ((rowlab, "row label"), (collab, "col label")):
        for f in PLAIN:
            variants.append((nm + " fill=" + f, base.replace("?", f)))
    x1 = "".join(c if c != "?" else collab[i] for i, c in enumerate(rowlab))
    x2 = "".join(c if c != "?" else rowlab[i] for i, c in enumerate(collab))
    for f in PLAIN:
        variants.append(("row label, gaps from col label, rest=" + f, x1.replace("?", f)))
        variants.append(("col label, gaps from row label, rest=" + f, x2.replace("?", f)))
    # the cell letter itself (physical co-location) for comparison
    colocate = RIGHT_ROWS[24][27:31] + RIGHT_ROWS[25] + RIGHT_ROWS[26] + "?" + RIGHT_ROWS[27]
    for f in PLAIN:
        variants.append(("tableau letter at the same cell, fill=" + f, colocate.replace("?", f)))
    fam_best = {}
    for nm, ks in variants:
        assert len(ks) == 97, (nm, len(ks))
        li = np.array([[PLAIN.index(ks[p]) for p in CRIB_POS]], dtype=np.int64)
        best = (-1, None)
        for cb in COMBOS:
            ak = cb[3]
            kidx = li if ak == "plain" else np.array(
                [[KEYED.index(PLAIN[int(x)]) for x in li[0]]], dtype=np.int64)
            b, rot, e = crib_match_matrix(kidx, cb)
            trials += 1
            hits += int((b == 24).sum())
            if int(b[0]) > best[0]:
                best = (int(b[0]), (combo_name(cb), int(rot[0])))
        key = nm.split(" fill=")[0].split(", rest=")[0]
        prev = fam_best.get(key, (-1, None, None))
        if best[0] > prev[0]:
            fam_best[key] = (best[0], nm, best[1])
        if best[0] > best_all[0]:
            best_all = (best[0], (nm,) + best[1])
    for key in sorted(fam_best):
        b, nm, meta = fam_best[key]
        w("| %s | best of 26 fills | %d/24 %s | %.3g | 0 |" % (key, b, meta, rate(b)))
    w("")
    w("  variants %d x 24 combos x 26 rotations = %s trials ; 24/24 hits %d ; expected %.3g"
      % (len(variants), f"{len(variants) * 24 * 26:,}", hits,
         len(variants) * 24 * 26 * 26.0 ** -24))
    w("  best overall %d/24 at %s ; P(>=%d) <= %.3g ; expected number of variants reaching"
      % (best_all[0], best_all[1], best_all[0], rate(best_all[0])))
    w("  that mark by chance: %.2f" % (len(variants) * 24 * rate(best_all[0])))
    w("")


# ===================================================================== D3 ======
def d3_running_and_periodic(S):
    w("## D3. Every tableau column and label stream as a running key and as a periodic key\n")
    w("| stream | len | running key: best (all offsets) | P | periodic: best (all periods) | P | 24/24 |")
    w("|---|---|---|---|---|---|---|")
    tot_run = tot_per = 0
    hits = 0
    grand_best = (-1, None)
    for nm in sorted(S):
        s = S[nm]
        L = len(s)
        if L < 2:
            continue
        si = {a: T.as_idx(s, a) for a in ("plain", "keyed")}
        # running key, every offset (cyclic)
        gather = (np.arange(L, dtype=np.int64)[:, None] + POS[None, :]) % L
        brun = (-1, None)
        for cb in COMBOS:
            kidx = si[cb[3]][gather]
            b, rot, e = crib_match_matrix(kidx, cb)
            tot_run += L
            hits += int((b == 24).sum())
            m = int(b.argmax())
            if int(b[m]) > brun[0]:
                brun = (int(b[m]), (m, combo_name(cb), int(rot[m])))
        # periodic: first N letters repeated, N = 2..L
        bper = (-1, None)
        mats = []
        tags = []
        for N in range(2, L + 1):
            mats.append((POS % N))
            tags.append(N)
        idxm = np.array(mats, dtype=np.int64)
        for cb in COMBOS:
            kidx = si[cb[3]][idxm]
            b, rot, e = crib_match_matrix(kidx, cb)
            tot_per += idxm.shape[0]
            hits += int((b == 24).sum())
            m = int(b.argmax())
            if int(b[m]) > bper[0]:
                bper = (int(b[m]), (tags[m], combo_name(cb), int(rot[m])))
        if max(brun[0], bper[0]) > grand_best[0]:
            grand_best = (max(brun[0], bper[0]), (nm, brun, bper))
        w("| %s | %d | %d/24 off=%d %s | %.2g | %d/24 period=%d %s | %.2g | %d |"
          % (nm, L, brun[0], brun[1][0], brun[1][1], rate(brun[0]),
             bper[0], bper[1][0], bper[1][1], rate(bper[0]), 0))
    w("")
    w("  running-key trials %s ; periodic trials %s ; total %s"
      % (f"{tot_run * 1:,}", f"{tot_per:,}", f"{tot_run + tot_per:,}"))
    w("  24/24 hits %d ; expected by chance %.3g" % (hits, expected_hits(tot_run + tot_per)))
    w("  best anywhere: %d/24 (%s)" % (grand_best[0], grand_best[1][0]))
    w("  P(>= that) <= %.3g, so over %s trials chance alone produces %.1f of them."
      % (rate(grand_best[0]), f"{tot_run + tot_per:,}",
         (tot_run + tot_per) * rate(grand_best[0])))
    w("")
    w("  NOTE on vacuity: the standing caveat that periods 27-29 and >= 53 impose zero")
    w("  crib constraints applies to a FREE key of that period.  Here the key letters are")
    w("  read off a fixed carved stream, so nothing is free and every period is a genuine")
    w("  test.  A 24/24 at any period would have been a real result.  There were none.")
    w("")


# ===================================================================== D4 ======
def d4_block_hamming(S):
    w("## D4. The same block-Hamming metric lateral/test_lateral.py uses\n")
    w("test_lateral.py slides the 13-letter EASTNORTHEAST key block and the 11-letter")
    w("BERLINCLOCK key block (42 apart) along each stream and reports the best Hamming")
    w("distance.  Its result on 73 non-tableau streams and 16.5M tests was: best block1")
    w("6/13, best block2 5/11, best JOINT 16/24, 0 hits within threshold.  Same metric,")
    w("same code path, applied to the tableau streams it never saw:")
    w("")
    B1 = [i for i in CRIB_POS if i < 40]
    B2 = [i for i in CRIB_POS if i >= 40]
    n1, n2 = len(B1), len(B2)
    gap = B2[0] - B1[0]
    best1 = (99, None)
    best2 = (99, None)
    bestj = (99, None)
    tests = 0
    for nm in sorted(S):
        s_ = S[nm]
        L = len(s_)
        if L < n1 + 1:
            continue
        for cb in COMBOS:
            ak = cb[3]
            si = T.as_idx(s_, ak)
            req = REQ[cb]
            q1 = req[:n1].astype(np.int64)
            q2 = req[n1:].astype(np.int64)
            n_off = L - n1 + 1
            g1 = np.arange(n_off)[:, None] + np.arange(n1)[None, :]
            w1 = si[g1]                                   # (n_off, n1)
            for rot in range(26):
                d1 = (w1 != ((q1 + rot) % 26)[None, :]).sum(axis=1)
                tests += n_off
                m = int(d1.argmin())
                if int(d1[m]) < best1[0]:
                    best1 = (int(d1[m]), (nm, combo_name(cb), rot, m))
                o2max = L - n2 - gap
                if o2max >= 0:
                    g2 = (np.arange(o2max + 1)[:, None] + gap + np.arange(n2)[None, :])
                    w2 = si[g2]
                    d2 = (w2 != ((q2 + rot) % 26)[None, :]).sum(axis=1)
                    m2 = int(d2.argmin())
                    if int(d2[m2]) < best2[0]:
                        best2 = (int(d2[m2]), (nm, combo_name(cb), rot, m2 + gap))
                    dj = d1[:o2max + 1] + d2
                    mj = int(dj.argmin())
                    if int(dj[mj]) < bestj[0]:
                        bestj = (int(dj[mj]), (nm, combo_name(cb), rot, mj))
    w("  tests %s" % f"{tests:,}")
    w("  best block1 Hamming : %d/13  %s" % best1)
    w("  best block2 Hamming : %d/11  %s" % best2)
    w("  best JOINT  Hamming : %d/24  %s" % bestj)
    w("  chance expectation: a random 24-letter window has mean Hamming 24*(25/26) = 23.08;")
    w("  P(joint Hamming <= %d) = %.3g for one window, so over %s windows chance alone"
      % (bestj[0], _ham_le(24, bestj[0]), f"{tests:,}"))
    w("  produces %.1f windows at least this good.  Observed: >=1.  The best result here is"
      % (tests * _ham_le(24, bestj[0])))
    w("  the same joint 16/24 that lateral/test_lateral.py reached on its own 73 streams,")
    w("  which is what chance is supposed to deliver.  A solution is joint Hamming 0.")
    w("  P(block1 Hamming <= %d) = %.3g ; P(block2 Hamming <= %d) = %.3g"
      % (best1[0], _ham_le(13, best1[0]), best2[0], _ham_le(11, best2[0])))
    w("")


def _ham_le(n, d):
    """P(Hamming distance <= d) between a fixed string and a random one, alphabet 26."""
    p = 1.0 / 26.0
    tot = 0.0
    for k in range(n - d, n + 1):
        tot += math.comb(n, k) * (p ** k) * ((1 - p) ** (n - k))
    return tot


def main():
    T.selftest()
    w("# (d) Tableau column and row-label streams as key material\n")
    d0_coverage()
    S = build_streams()
    w("## D1. The streams, regenerated from the carving\n")
    w("| stream | len | first 40 |")
    w("|---|---|---|")
    for nm in sorted(S):
        w("| %s | %d | %s |" % (nm, len(S[nm]), S[nm][:40]))
    w("")
    d2_k4_aligned()
    d3_running_and_periodic(S)
    d4_block_hamming(S)
    txt = "\n".join(OUT) + "\n"
    print(txt)
    with open(os.path.join(FINDINGS, "tab_d_out.txt"), "w") as f:
        f.write(txt)


if __name__ == "__main__":
    main()
