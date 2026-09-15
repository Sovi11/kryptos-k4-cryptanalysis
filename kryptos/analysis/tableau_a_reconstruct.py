"""(a) Reconstruct the Kryptos right-hand (tableau) panel and inventory every anomaly.

Verifies data/sculpture_panels.txt against two independent external transcriptions
(Wikipedia article wikitext, Elonka Dunin's transcript.html via the Wayback Machine);
the expected strings from those sources are hard-coded below so the check is offline
and reproducible.  Then produces the full diff physical-vs-ideal.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tableau_common import (PLAIN, KEYED, RIGHT_ROWS, RIGHT_ROWS_IDEAL, LEFT_ROWS,
                            TABLEAU_PHYS_STR, TABLEAU_IDEAL_STR, selftest, letters)

# --------------------------------------------------------------------------------
# External transcriptions, copied verbatim 2026-09-12 from
#   (1) https://en.wikipedia.org/w/index.php?title=Kryptos&action=raw  (the <pre> block)
#   (2) http://web.archive.org/web/2020id_/https://elonka.com/kryptos/transcript.html
# Both give the row label at the START of each row and both agree letter for letter.
EXTERNAL_RIGHT = """ABCDEFGHIJKLMNOPQRSTUVWXYZABCD
AKRYPTOSABCDEFGHIJLMNQUVWXZKRYP
BRYPTOSABCDEFGHIJLMNQUVWXZKRYPT
CYPTOSABCDEFGHIJLMNQUVWXZKRYPTO
DPTOSABCDEFGHIJLMNQUVWXZKRYPTOS
ETOSABCDEFGHIJLMNQUVWXZKRYPTOSA
FOSABCDEFGHIJLMNQUVWXZKRYPTOSAB
GSABCDEFGHIJLMNQUVWXZKRYPTOSABC
HABCDEFGHIJLMNQUVWXZKRYPTOSABCD
IBCDEFGHIJLMNQUVWXZKRYPTOSABCDE
JCDEFGHIJLMNQUVWXZKRYPTOSABCDEF
KDEFGHIJLMNQUVWXZKRYPTOSABCDEFG
LEFGHIJLMNQUVWXZKRYPTOSABCDEFGH
MFGHIJLMNQUVWXZKRYPTOSABCDEFGHI
NGHIJLMNQUVWXZKRYPTOSABCDEFGHIJL
OHIJLMNQUVWXZKRYPTOSABCDEFGHIJL
PIJLMNQUVWXZKRYPTOSABCDEFGHIJLM
QJLMNQUVWXZKRYPTOSABCDEFGHIJLMN
RLMNQUVWXZKRYPTOSABCDEFGHIJLMNQ
SMNQUVWXZKRYPTOSABCDEFGHIJLMNQU
TNQUVWXZKRYPTOSABCDEFGHIJLMNQUV
UQUVWXZKRYPTOSABCDEFGHIJLMNQUVW
VUVWXZKRYPTOSABCDEFGHIJLMNQUVWX
WVWXZKRYPTOSABCDEFGHIJLMNQUVWXZ
XWXZKRYPTOSABCDEFGHIJLMNQUVWXZK
YXZKRYPTOSABCDEFGHIJLMNQUVWXZKR
ZZKRYPTOSABCDEFGHIJLMNQUVWXZKRY
ABCDEFGHIJKLMNOPQRSTUVWXYZABCD""".split("\n")

# Row lengths of the LEFT panel as given by Elonka's transcript (independent check on
# data/sculpture_layout.txt's claim that the left panel is ragged).
ELONKA_LEFT_LENS = [32, 31, 31, 30, 31, 32, 31, 31, 32, 31, 30, 31, 31, 31,
                    32, 30, 31, 30, 32, 30, 32, 31, 33, 29, 31, 31, 31, 31]


def main():
    selftest()
    out = []
    w = out.append

    w("# (a) Reconstruction of the Kryptos right-hand tableau panel\n")

    # ---- 1. agreement with external sources
    w("## 1. Transcription agreement\n")
    same = (RIGHT_ROWS == EXTERNAL_RIGHT)
    w("data/sculpture_panels.txt [RIGHT] == Wikipedia/Elonka transcription: %s" % same)
    if not same:
        for i, (a, b) in enumerate(zip(RIGHT_ROWS, EXTERNAL_RIGHT)):
            if a != b:
                w("  row %2d local=%r external=%r" % (i, a, b))
    w("left-panel row lengths (local)   : %s" % [len(letters(r)) for r in LEFT_ROWS])
    w("left-panel row lengths (Elonka)  : %s" % ELONKA_LEFT_LENS)
    w("left-panel row lengths agree     : %s" %
      ([len(letters(r)) + r.count("?") for r in LEFT_ROWS] == ELONKA_LEFT_LENS))
    w("")

    # ---- 2. shape
    w("## 2. Shape of the carved tableau\n")
    w("28 carved rows.  Row 0 and row 27 are the unlabelled plain header/footer")
    w("  'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + 'ABCD' = 30 letters.")
    w("Rows 1..26 are 'row label' + a 30-letter window of the KRYPTOS-keyed alphabet:")
    w("  row with label L(i) carries KEYED rotated left by i, then its first 4 letters again.")
    w("row lengths (physical): %s" % [len(r) for r in RIGHT_ROWS])
    w("row lengths (ideal)   : %s" % [len(r) for r in RIGHT_ROWS_IDEAL])
    w("total letters physical = %d, ideal = %d, difference = %d"
      % (len(TABLEAU_PHYS_STR), len(TABLEAU_IDEAL_STR),
         len(TABLEAU_PHYS_STR) - len(TABLEAU_IDEAL_STR)))
    w("  866 = 2*30 (header+footer) + 26*(1 label + 30 body).")
    w("")

    # ---- 3. anomaly inventory
    w("## 3. Complete anomaly inventory (physical minus ideal)\n")
    diffs = []
    for i, (ph, idl) in enumerate(zip(RIGHT_ROWS, RIGHT_ROWS_IDEAL)):
        if ph != idl:
            diffs.append((i, ph, idl))
    w("rows that differ from the ideal tableau: %d" % len(diffs))
    for i, ph, idl in diffs:
        w("  row index %d (carved label %r, 1-indexed carved row %d):" % (i, ph[0], i + 1))
        w("    physical %r  (%d chars)" % (ph, len(ph)))
        w("    ideal    %r  (%d chars)" % (idl, len(idl)))
        # locate the insertion
        j = 0
        while j < len(idl) and ph[j] == idl[j]:
            j += 1
        w("    first divergence at column %d (0-indexed within the row)" % j)
        w("    physical row = ideal row + one extra %r appended at the end" % ph[-1])
        assert ph[:-1] == idl
    w("")
    w("There is exactly ONE deviation: a single extra letter L at the end of the row")
    w("labelled N (carved row 15 of 28, 1-indexed).  Everything else is a perfect")
    w("KRYPTOS-keyed Vigenere tableau.")
    w("")

    # linear index of the anomalous letter
    lin = sum(len(r) for r in RIGHT_ROWS[:14]) + len(RIGHT_ROWS[14]) - 1
    w("linear index of the extra L in the 867-letter physical reading:")
    w("  0-indexed %d, 1-indexed %d" % (lin, lin + 1))
    assert TABLEAU_PHYS_STR[lin] == "L"
    w("  letters before it: %d ; letters after it: %d"
      % (lin, len(TABLEAU_PHYS_STR) - lin - 1))
    w("  factorisations of interest: 465 = 3*5*31 = 15*31 ; 464 = 16*29 ; 867 = 3*17^2")
    w("")

    # ---- 4. the rightmost column (the HILL observation)
    w("## 4. Rightmost column of the carved rows (the Bauer/Link/Molle 'HILL')\n")
    lastcol_phys = "".join(r[-1] for r in RIGHT_ROWS[1:27])
    lastcol_ideal = "".join(r[-1] for r in RIGHT_ROWS_IDEAL[1:27])
    w("physical last column, rows A..Z : %s" % lastcol_phys)
    w("ideal    last column, rows A..Z : %s" % lastcol_ideal)
    w("physical contains 'HILL': %s at index %s"
      % ("HILL" in lastcol_phys, lastcol_phys.find("HILL")))
    w("ideal    contains 'HILL': %s" % ("HILL" in lastcol_ideal))
    w("(the extra L turns ...H I J L... into ...H I L L..., i.e. rows L,M,N,O)")
    w("")

    # ---- 5. all 30/31/32 columns read downward
    w("## 5. Every column of the carved tableau read downward (rows A..Z only)\n")
    maxlen = max(len(r) for r in RIGHT_ROWS[1:27])
    for c in range(maxlen):
        col = "".join(r[c] for r in RIGHT_ROWS[1:27] if c < len(r))
        w("  col %2d (%2d letters): %s" % (c, len(col), col))
    w("")

    # ---- 6. alignment of K4 with the tableau panel
    w("## 6. Row/column alignment of K4 with the tableau panel\n")
    w("K4 occupies the last 4 characters of left-panel row 25 and all of rows 26,27,28")
    w("(1-indexed), each of which is exactly 31 characters wide.")
    for r in (24, 25, 26, 27):
        w("  left  row %2d (%2d chars): %s" % (r + 1, len(LEFT_ROWS[r]), LEFT_ROWS[r]))
        w("  right row %2d (%2d chars): %s" % (r + 1, len(RIGHT_ROWS[r]), RIGHT_ROWS[r]))
    w("")
    w("Same-row/same-column key stream for K4 (the 'physical keystream'):")
    ks = RIGHT_ROWS[24][27:31] + RIGHT_ROWS[25] + RIGHT_ROWS[26] + RIGHT_ROWS[27]
    w("  row25 cols 28-31 : %s   (under left-panel  %s)" % (RIGHT_ROWS[24][27:31],
                                                            LEFT_ROWS[24][27:31]))
    w("  row26            : %s" % RIGHT_ROWS[25])
    w("  row27            : %s" % RIGHT_ROWS[26])
    w("  row28 (footer)   : %s   <-- only 30 letters, the footer has no row label" % RIGHT_ROWS[27])
    w("  concatenated     : %s  (%d letters)" % (ks, len(ks)))
    w("NOTE: the footer row carries 30 letters, not 31, because it has no row-label")
    w("letter.  A naive same-column reading therefore runs out of letters one short")
    w("for K4 positions 67..97; solvekryptos.com patches this by inserting a blank.")
    w("")

    print("\n".join(out))
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "findings", "tableau_a_out.txt"), "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
