#!/usr/bin/env python3
"""
Kryptos right-hand (tableau) panel: authoritative transcription, ideal reconstruction,
character-by-character diff, and keystream extraction.

Transcription verified identical across four independent sources (see tableau_panel.md):
  Wikipedia, cia.gov, scirealm.org (John Wilson), github.com/hamidsamak/kryptos.
"""
import os, difflib, json

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keystreams")
os.makedirs(OUT, exist_ok=True)

PLAIN = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KEYED = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

# ---------------------------------------------------------------- PHYSICAL ----
# As carved. Index 0 = header, 1..26 = rows A..Z, 27 = footer.
# Header/footer have a BLANK row-label cell (represented here by the leading space).
PHYS = [
    " ABCDEFGHIJKLMNOPQRSTUVWXYZABCD",
    "AKRYPTOSABCDEFGHIJLMNQUVWXZKRYP",
    "BRYPTOSABCDEFGHIJLMNQUVWXZKRYPT",
    "CYPTOSABCDEFGHIJLMNQUVWXZKRYPTO",
    "DPTOSABCDEFGHIJLMNQUVWXZKRYPTOS",
    "ETOSABCDEFGHIJLMNQUVWXZKRYPTOSA",
    "FOSABCDEFGHIJLMNQUVWXZKRYPTOSAB",
    "GSABCDEFGHIJLMNQUVWXZKRYPTOSABC",
    "HABCDEFGHIJLMNQUVWXZKRYPTOSABCD",
    "IBCDEFGHIJLMNQUVWXZKRYPTOSABCDE",
    "JCDEFGHIJLMNQUVWXZKRYPTOSABCDEF",
    "KDEFGHIJLMNQUVWXZKRYPTOSABCDEFG",
    "LEFGHIJLMNQUVWXZKRYPTOSABCDEFGH",
    "MFGHIJLMNQUVWXZKRYPTOSABCDEFGHI",   # <- last line of TOP-RIGHT plate
    "NGHIJLMNQUVWXZKRYPTOSABCDEFGHIJL",  # <- first line of BOTTOM-RIGHT plate; EXTRA L
    "OHIJLMNQUVWXZKRYPTOSABCDEFGHIJL",
    "PIJLMNQUVWXZKRYPTOSABCDEFGHIJLM",
    "QJLMNQUVWXZKRYPTOSABCDEFGHIJLMN",
    "RLMNQUVWXZKRYPTOSABCDEFGHIJLMNQ",
    "SMNQUVWXZKRYPTOSABCDEFGHIJLMNQU",
    "TNQUVWXZKRYPTOSABCDEFGHIJLMNQUV",
    "UQUVWXZKRYPTOSABCDEFGHIJLMNQUVW",
    "VUVWXZKRYPTOSABCDEFGHIJLMNQUVWX",
    "WVWXZKRYPTOSABCDEFGHIJLMNQUVWXZ",
    "XWXZKRYPTOSABCDEFGHIJLMNQUVWXZK",
    "YXZKRYPTOSABCDEFGHIJLMNQUVWXZKR",
    "ZZKRYPTOSABCDEFGHIJLMNQUVWXZKRY",
    " ABCDEFGHIJKLMNOPQRSTUVWXYZABCD",
]
TOP_PLATE_ROWS   = list(range(0, 14))    # header + rows A..M
BOT_PLATE_ROWS   = list(range(14, 28))   # rows N..Z + footer

# ------------------------------------------------------------------- IDEAL ----
def ideal_rows():
    """Header, 26 labelled rotations of the KRYPTOS alphabet padded to 30, footer."""
    hdr = " " + PLAIN + "ABCD"
    rows = [hdr]
    for i in range(26):
        rot = KEYED[i:] + KEYED[:i]
        rows.append(PLAIN[i] + rot + rot[:4])
    rows.append(hdr)
    return rows

IDEAL = ideal_rows()

def letters(rows):
    return "".join(r.replace(" ", "") for r in rows)

PHYS_S, IDEAL_S = letters(PHYS), letters(IDEAL)

# ----------------------------------------------------------------- CHECKS ----
report = []
def say(s=""):
    print(s); report.append(s)

say("=" * 78)
say("KRYPTOS RIGHT-HAND (TABLEAU) PANEL - PHYSICAL vs IDEAL")
say("=" * 78)
say(f"physical rows            : {len(PHYS)}")
say(f"physical letters         : {len(PHYS_S)}   (published figure: 867)")
say(f"physical chars incl 2 blank label cells : {len(PHYS_S)+2}   (published figure: 869)")
say(f"ideal letters            : {len(IDEAL_S)}   (866)")
say(f"difference               : {len(PHYS_S)-len(IDEAL_S)}")
say()
say(f"top-right plate letters  : {len(letters([PHYS[i] for i in TOP_PLATE_ROWS]))} "
    f"(+1 blank cell = {len(letters([PHYS[i] for i in TOP_PLATE_ROWS]))+1}; published: 434)")
say(f"bot-right plate letters  : {len(letters([PHYS[i] for i in BOT_PLATE_ROWS]))} "
    f"(+1 blank cell = {len(letters([PHYS[i] for i in BOT_PLATE_ROWS]))+1}; published: 435)")
say()

# ---------------------------------------------------- ROW-LEVEL ANOMALY LIST --
say("-" * 78)
say("ROW-LEVEL DIFF (physical row vs ideal row)")
say("-" * 78)
anomalies = []
pos = 0  # 1-indexed running letter position in the physical stream
row_anom = []
for r, (p, q) in enumerate(zip(PHYS, IDEAL)):
    label = "hdr" if r == 0 else ("ftr" if r == 27 else PLAIN[r - 1])
    pl, ql = p.replace(" ", ""), q.replace(" ", "")
    if pl != ql:
        sm = difflib.SequenceMatcher(None, ql, pl, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                continue
            row_anom.append((r, label, tag, ql[i1:i2], pl[j1:j2], j1))
            say(f"  row {r:2d} (label {label}): {tag.upper()}  "
                f"expected {ql[i1:i2]!r} -> actual {pl[j1:j2]!r} "
                f"at offset {j1} within the row (0-indexed, label counted)")
            # absolute position in full physical stream, 1-indexed
            abs_pos = pos + j1 + 1
            for k, ch in enumerate(pl[j1:j2]):
                anomalies.append({"stream_pos_1idx": abs_pos + k, "row": r,
                                  "row_label": label, "col_in_row_0idx": j1 + k,
                                  "expected": (ql[i1:i2][k] if k < (i2 - i1) else None),
                                  "actual": ch, "kind": tag})
    pos += len(pl)
if not row_anom:
    say("  (none)")
say()
say(f"TOTAL ANOMALIES: {len(anomalies)}")
for a in anomalies:
    say(f"  stream position {a['stream_pos_1idx']} (1-indexed, letters only); "
        f"row {a['row']} label {a['row_label']}; column-in-row {a['col_in_row_0idx']}; "
        f"expected {a['expected']}; actual {a['actual']}; kind={a['kind']}")
say()

# ------------------------------------------------- GLOBAL STREAM-LEVEL DIFF ---
say("-" * 78)
say("GLOBAL STREAM DIFF (866-letter ideal -> 867-letter physical)")
say("-" * 78)
sm = difflib.SequenceMatcher(None, IDEAL_S, PHYS_S, autojunk=False)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        continue
    say(f"  {tag.upper()}: ideal[{i1}:{i2}]={IDEAL_S[i1:i2]!r} -> "
        f"physical[{j1}:{j2}]={PHYS_S[j1:j2]!r}  (1-indexed physical position {j1+1})")
say(f"  similarity ratio: {sm.ratio():.6f}")
say()

# --------------------------------------------------------- HILL / LAST COL ---
say("-" * 78)
say("LAST-COLUMN READING (the Bauer/Link/Molle 'HILL' observation)")
say("-" * 78)
last = "".join(r[-1] for r in PHYS)
say(f"  physical last char of each of the 28 rows: {last}")
say(f"  rows L,M,N,O (indices 12..15)            : {''.join(PHYS[i][-1] for i in range(12,16))}")
ideal_last = "".join(r[-1] for r in IDEAL)
say(f"  ideal  last char of each of the 28 rows  : {ideal_last}")
say(f"  ideal rows L,M,N,O                       : {''.join(IDEAL[i][-1] for i in range(12,16))}")
say()

# --------------------------------------- CROSS-PANEL INDEX (YA_R / JIM note) --
say("-" * 78)
say("CROSS-PANEL: superscript letters on the CIPHER side vs the same row here")
say("-" * 78)
say("  Cipher side, top line of bottom-left plate: ENDYAHROHNLSRHEOCPTEOIBIDYSHNAIA")
say("  superscript/raised letters are chars 4,5,7 -> Y, A, R  ('YA_R')")
rowN = PHYS[14]
say(f"  Tableau side, same line (row N)          : {rowN}")
say(f"  chars 4,5,7 of row N                     : "
    f"{rowN[3]}, {rowN[4]}, {rowN[6]}  -> anagram 'JIM'")
say()

# ------------------------------------------------------------- KEYSTREAMS ----
def write(name, data, desc, url, conf):
    with open(os.path.join(OUT, name), "w") as f:
        f.write(data + "\n")
    return (name, desc, url, conf, len(data))

WIKI = "https://en.wikipedia.org/wiki/Kryptos"
CIA  = "https://www.cia.gov/legacy/headquarters/kryptos-sculpture/"
SCI  = "http://scirealm.org/KryptosDetails.html"
GH   = "https://github.com/hamidsamak/kryptos/blob/master/tableau.txt"
SRC  = f"{WIKI} (verified identical against {CIA} , {SCI} , {GH} )"

man = []

# --- whole-panel streams
man.append(write("tab_phys_full.txt", PHYS_S,
    "Right panel exactly as carved, all 28 rows concatenated, row labels and header/footer "
    "included, letters only (867). Includes the anomalous extra L at row N.", SRC, "high"))
man.append(write("tab_phys_full_rev.txt", PHYS_S[::-1],
    "tab_phys_full.txt reversed. The panel is cut THROUGH the copper, so from the far side the "
    "text reads mirrored; a reversed read is physically motivated, not arbitrary.", SRC, "high"))
man.append(write("tab_ideal_full.txt", IDEAL_S,
    "The tableau the carver should have produced: header + 26 labelled rotations of "
    "KRYPTOSABCDEFGHIJLMNQUVWXZ padded to 30 + footer, letters only (866). No extra L.",
    "constructed programmatically; see build_tableau_panel.py", "high"))
man.append(write("tab_ideal_full_rev.txt", IDEAL_S[::-1],
    "tab_ideal_full.txt reversed.", "constructed programmatically", "high"))

# --- body only (no row labels, no header/footer)
phys_body = "".join(PHYS[i][1:] for i in range(1, 27))
ideal_body = "".join(IDEAL[i][1:] for i in range(1, 27))
man.append(write("tab_phys_body.txt", phys_body,
    "Physical tableau BODY only: the 26 lettered rows with row labels and the header/footer "
    "alphabet rows stripped (781 letters; 780 + the extra L).", SRC, "high"))
man.append(write("tab_ideal_body.txt", ideal_body,
    "Ideal tableau BODY only, 26 rows x 30 cols = 780 letters.",
    "constructed programmatically", "high"))

# --- 26x26 core (drop the 4-letter wrap-around tail on each row)
core_rows = [IDEAL[i][1:27] for i in range(1, 27)]
core = "".join(core_rows)
man.append(write("tab_core_rows.txt", core,
    "Ideal 26x26 core read by ROWS: the 26 rotations of the KRYPTOS keyed alphabet, tail "
    "padding and labels removed (676 letters).", "constructed programmatically", "high"))
core_cols = "".join("".join(core_rows[r][c] for r in range(26)) for c in range(26))
man.append(write("tab_core_cols.txt", core_cols,
    "Ideal 26x26 core read by COLUMNS (column-major, 676 letters). Because each row is the "
    "previous rotated left by one, the column read is itself a set of rotations.",
    "constructed programmatically", "high"))

# --- column-major of the full 26x30 body
body_rows = [PHYS[i][1:] for i in range(1, 27)]
maxw = max(len(r) for r in body_rows)
phys_cols = "".join("".join(r[c] for r in body_rows if c < len(r)) for c in range(maxw))
man.append(write("tab_phys_body_cols.txt", phys_cols,
    "Physical tableau body read by COLUMNS (column-major over the 26 rows x 30 cols, with the "
    "extra L of row N appearing in the 31st column). 781 letters.", SRC, "high"))

# --- row labels, column labels
man.append(write("tab_row_labels.txt", PLAIN,
    "The 26 row-label letters as carved down the left edge of the tableau: plain A..Z.",
    SRC, "high"))
man.append(write("tab_col_labels.txt", PLAIN + "ABCD",
    "The column-label row as carved at the top AND bottom of the panel: the plain alphabet "
    "followed by ABCD (30 letters). Carved identically in both places.", SRC, "high"))

# --- per-index row/column label streams (companions to the panel stream)
row_lab_stream, col_lab_stream = [], []
COLLAB = PLAIN + "ABCD"
for r, row in enumerate(PHYS):
    lab = " " if r in (0, 27) else PLAIN[r - 1]
    body = row[1:]
    if r in (0, 27):
        body = row[1:]
    for c, ch in enumerate(row.replace(" ", "")):
        pass
    # walk letters only, recording which row-label and column-label each letter sits under
    letters_in_row = row.replace(" ", "")
    for c, ch in enumerate(letters_in_row):
        if r in (0, 27):
            # header/footer: the blank label cell means column index == c
            row_lab_stream.append("-")
            col_lab_stream.append(COLLAB[c] if c < len(COLLAB) else "?")
        else:
            if c == 0:
                row_lab_stream.append(PLAIN[r - 1]); col_lab_stream.append("-")  # label cell
            else:
                row_lab_stream.append(PLAIN[r - 1])
                col_lab_stream.append(COLLAB[c - 1] if (c - 1) < len(COLLAB) else "?")
man.append(write("tab_rowlabel_per_index.txt", "".join(row_lab_stream),
    "For each of the 867 letters of tab_phys_full.txt, the row-label letter of the row it sits "
    "in ('-' for the unlabelled header/footer rows). Same length as the panel stream.",
    SRC, "high"))
man.append(write("tab_collabel_per_index.txt", "".join(col_lab_stream),
    "For each of the 867 letters of tab_phys_full.txt, the column-label letter of the column it "
    "sits in, taken from the carved header row ABCDEFGHIJKLMNOPQRSTUVWXYZABCD. '-' marks the "
    "row-label cells; '?' marks the extra L of row N, which falls beyond the 30 labelled "
    "columns. Same length as the panel stream.", SRC, "high"))

# --- anomaly streams
man.append(write("tab_anomaly_positions.txt",
    " ".join(str(a["stream_pos_1idx"]) for a in anomalies),
    "Position(s) of every character where the carved panel departs from the ideal tableau, as "
    "1-indexed offsets into tab_phys_full.txt (letters only). Exactly one: the extra L.",
    SRC, "high"))
man.append(write("tab_anomaly_letters.txt", "".join(a["actual"] for a in anomalies),
    "The anomalous letter(s) themselves, in panel order. Exactly one character: L.",
    SRC, "high"))

# --- the HILL column
man.append(write("tab_last_column.txt", last,
    "The last carved character of each of the 28 rows, top to bottom. Rows L,M,N,O give "
    "H,I,L,L - the 'HILL' of the Bauer/Link/Molle Hill-cipher conjecture, which exists ONLY "
    "because of the extra L.", SRC, "high"))
man.append(write("tab_last_column_ideal.txt", ideal_last,
    "The last character of each of the 28 rows of the IDEAL tableau. Rows L,M,N,O give H,I,J,L "
    "- i.e. no HILL.", "constructed programmatically", "high"))

# --- diagonals of the core
diag = "".join(core_rows[i][i] for i in range(26))
anti = "".join(core_rows[i][25 - i] for i in range(26))
man.append(write("tab_core_diag_main.txt", diag,
    "Main diagonal of the ideal 26x26 core (26 letters).", "constructed programmatically", "medium"))
man.append(write("tab_core_diag_anti.txt", anti,
    "Anti-diagonal of the ideal 26x26 core (26 letters).", "constructed programmatically", "medium"))

# --- plate-split streams
man.append(write("tab_phys_top_plate.txt", letters([PHYS[i] for i in TOP_PLATE_ROWS]),
    "Top-right copper plate only: header row + tableau rows A..M as carved (433 letters, "
    "434 cells counting the blank label cell).", SRC, "high"))
man.append(write("tab_phys_bottom_plate.txt", letters([PHYS[i] for i in BOT_PLATE_ROWS]),
    "Bottom-right copper plate only: tableau rows N..Z + footer row as carved (434 letters, "
    "435 cells). The extra L is the last letter of this plate's FIRST line.", SRC, "high"))

# --- write manifest rows + machine-readable anomaly json
with open(os.path.join(OUT, "_rows_tableau.tsv"), "w") as f:
    for name, desc, url, conf, n in man:
        f.write(f"{name}\t{desc} [{n} chars]\t{url}\t{conf}\n")

with open(os.path.join(os.path.dirname(OUT), "tableau_anomalies.json"), "w") as f:
    json.dump({"physical_letters": len(PHYS_S), "ideal_letters": len(IDEAL_S),
               "anomalies": anomalies,
               "physical_rows": PHYS, "ideal_rows": IDEAL}, f, indent=2)

say("-" * 78)
say(f"wrote {len(man)} keystream files to {OUT}")
for name, desc, url, conf, n in man:
    say(f"  {name:34s} {n:5d} chars")

with open(os.path.join(os.path.dirname(OUT), "build_tableau_panel.out.txt"), "w") as f:
    f.write("\n".join(report) + "\n")
