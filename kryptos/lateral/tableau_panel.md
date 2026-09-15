# Kryptos: the right-hand (Vigenère tableau) panel, transcribed and diffed

**Scope:** lateral source #1 — the carved right-hand panel of *Kryptos*, converted into candidate
K4 key material. Nothing here was submitted to any paid verifier.
**Artefacts:** `build_tableau_panel.py`, `tableau_anomalies.json`, `build_tableau_panel.out.txt`,
21 keystream files in `keystreams/` registered in `keystreams/MANIFEST.tsv`.

---

## 0. Bottom line

| Question | Answer |
|---|---|
| Physical panel | **867 letters** in 28 rows, occupying **869 character cells** |
| Ideal panel | **866 letters**, 868 cells |
| Number of anomalies | **Exactly one.** A single inserted `L` |
| Where | Row **N**, appended after the row's 30th body letter |
| Position in the 867-letter stream | **465** (1-indexed) |
| Non-tableau characters on the panel | **Two blank cells only** — no `?`, no superscripts, no extra words |
| Is the anomaly deliberate? | **Probably not.** Sanborn has indicated it was accidental and omits it from the models he sells |

The panel is *clean*. Apart from the one extra `L`, every one of the other 866 carved letters is
exactly what a mechanically-generated KRYPTOS-keyed tableau would produce. There is no second
hidden anomaly for a keystream to be built from.

---

## 1. (a) Authoritative transcription

Reproduced character for character, preserving row breaks and row-label letters. A leading space
marks the **blank row-label cell** on the header and footer rows.

```
 ABCDEFGHIJKLMNOPQRSTUVWXYZABCD     <- column-label row (no row label)
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
MFGHIJLMNQUVWXZKRYPTOSABCDEFGHI     <- last line of the TOP-RIGHT copper plate
NGHIJLMNQUVWXZKRYPTOSABCDEFGHIJL    <- first line of the BOTTOM-RIGHT plate; 32 cells, EXTRA L
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
 ABCDEFGHIJKLMNOPQRSTUVWXYZABCD     <- column-label row repeated (no row label)
```

Structure: **28 rows** = column-label row + 26 rows labelled `A`–`Z` + column-label row repeated.
Each labelled row is the keyed alphabet `KRYPTOSABCDEFGHIJLMNQUVWXZ` rotated left by the row's
index, then padded to 30 letters by repeating its own first 4 letters. Row labels are the **plain**
alphabet `A`–`Z`; the body alphabet is the **keyed** one. This is the same keyed alphabet used for
K1 (PALIMPSEST) and K2 (ABSCISSA).
<https://en.wikipedia.org/wiki/Kryptos>

### Physical plate split

The panel is two copper plates, and the join falls **between rows M and N**:

| Plate | Rows | Letters | Cells | Published figure |
|---|---|---|---|---|
| Top-right | header + `A`…`M` | 433 | 434 | 434 |
| Bottom-right | `N`…`Z` + footer | 434 | 435 | 435 |
| **Total** | 28 | **867** | **869** | 867 / 869 |

Plate figures from John Wilson's page <http://scirealm.org/KryptosDetails.html>; my reconstruction
reproduces 434 / 435 / 869 exactly. The 867-letter total is Wikipedia's
<https://en.wikipedia.org/wiki/Kryptos>. **The extra `L` is the last letter of the bottom plate's
first line** — i.e. it sits immediately at the plate seam, which is a plausible fabrication-error
location. The same fact ("on the top line of the bottom plate, on tableau row N") is stated
independently at <http://scirealm.org/KryptosDetails.html>.

### Verification method

I did not trust any single transcription. I pulled four independent renderings and diffed them
programmatically:

| # | Source | URL | Result |
|---|---|---|---|
| 1 | Wikipedia (raw wikitext) | <https://en.wikipedia.org/wiki/Kryptos> | baseline |
| 2 | CIA, official | <https://www.cia.gov/legacy/headquarters/kryptos-sculpture/> | identical |
| 3 | John Wilson, "John's Kryptos Details" | <http://scirealm.org/KryptosDetails.html> | identical |
| 4 | `hamidsamak/kryptos`, `tableau.txt` | <https://github.com/hamidsamak/kryptos/blob/master/tableau.txt> | identical |

**All four agree on all 867 letters, character for character.** The only textual difference found
anywhere was source 3 encoding the blank label cell as `U+00A0` rather than `U+0020` — cosmetic.

Source 3 carries independent weight: Elonka Dunin's FAQ names "Elonka's transcript and John
Wilson's transcript" as the accurate ones
(<https://web.archive.org/web/20240401065545/http://www.elonka.com/kryptos/faq.html>).
Elonka's own site was behind a CAPTCHA/interstitial at fetch time, so her transcript is represented
here only via that endorsement of Wilson's, not fetched directly — see §5.

---

## 2. (b) Ideal tableau and the character-by-character diff

`build_tableau_panel.py` generates the ideal panel from first principles — 26 rotations of
`KRYPTOSABCDEFGHIJLMNQUVWXZ`, plain `A`–`Z` row labels, `ABCDEFGHIJKLMNOPQRSTUVWXYZABCD` header and
footer — and diffs it against the carved panel both row-by-row and as one linear stream
(`difflib.SequenceMatcher(..., autojunk=False)`).

### Result: exactly one anomaly

```
row 14 (label N): INSERT  expected '' -> actual 'L' at offset 31 within the row
GLOBAL: INSERT ideal[464:464]='' -> physical[464:465]='L'   (1-indexed position 465)
similarity ratio: 0.999423
```

| Field | Value |
|---|---|
| Kind | insertion (not a substitution) |
| Position in 867-letter physical stream | **465** (1-indexed) / 464 (0-indexed) |
| Row | index 14 of 28 (header = 0); **row label `N`** |
| Offset within row | 31 (0-indexed, label counted) — i.e. appended after the row's 30th body letter |
| Expected | *nothing* |
| Actual | **`L`** |

Row `N` ideal body `GHIJLMNQUVWXZKRYPTOSABCDEFGHIJ` → carved `GHIJLMNQUVWXZKRYPTOSABCDEFGHIJ` **+ `L`**.

Every other character of the panel matches the ideal. Machine-readable form:
`lateral/tableau_anomalies.json`.

### The "HILL" observation

Reading the **last carved character of each row** top to bottom:

```
physical : DPTOSABCDEFGHILLMNQUVWXZKRYD
ideal    : DPTOSABCDEFGHIJLMNQUVWXZKRYD
                        ^^^^
rows L,M,N,O  physical = H I L L      ideal = H I J L
```

The `L` lengthens row `N` by one, so row `N`'s final letter becomes `L` instead of `J`, and
`HILL` appears down the right edge. Bauer, Link and Molle proposed in *Cryptologia* that this points
to the **Hill cipher** (matrix encryption) for K4: Craig Bauer, Gregory Link, Dante Molle, "James
Sanborn's *Kryptos* and the matrix encryption conjecture", *Cryptologia* 40(6), 2016, p.548,
<https://doi.org/10.1080/01611194.2016.1141556>. Note the word exists **only** because of the extra
letter — see the caveat in §6.

### Cross-panel coincidence, recorded but not endorsed

The three superscript letters on the *cipher* side (`Y`,`A`,`R` — chars 4, 5 and 7 of
`ENDYAHROHNLSRHEOCPTEOIBIDYSHNAIA`) sit on the top line of the bottom-**left** plate, i.e. the same
physical line as row `N`. Chars 4, 5 and 7 of row `N` are `I`, `J`, `M` — an anagram of `JIM`.
Reported at <http://scirealm.org/KryptosDetails.html>. I verified the index arithmetic; the
*interpretation* is folklore, and with only three letters the coincidence is weak. **Uncertain.**

---

## 3. (c) Non-tableau characters on the panel

Established answer: **there are none, beyond two blank cells.**

1. **Two blank row-label cells.** The header and footer rows carry no row label, leaving an empty
   cell at the left of each. These are the only non-letter cells: 867 letters + 2 blanks = **869
   cells**, the figure given at <http://scirealm.org/KryptosDetails.html> ("869 chars on the tableau
   side, counting the extra 'L' and the 2 spaces on the top/bottom alphabets").
2. **No question marks.** The four `?` characters are all on the ciphertext side
   (<https://en.wikipedia.org/wiki/Kryptos>).
3. **No superscript or raised letters.** Wikipedia states the three `YAR` letters on the left side
   "are the only characters on the sculpture in superscript"
   (<https://en.wikipedia.org/wiki/Kryptos>). The tableau panel has none.
4. **The header and footer rows read `ABCDEFGHIJKLMNOPQRSTUVWXYZABCD`** — the plain alphabet plus a
   4-letter `ABCD` tail. The tail is not "extra content"; it is the wrap-around padding that makes
   every row 30 columns wide, matching the 30-letter body rows. Both rows are carved identically;
   neither is a variant of the other.
5. **No signature, date, title or dedication appears among the 28 rows.** A copyright notice
   *"Kryptos" © Copyright 1988 James Sanborn* is associated with the sculpture, but I could not
   establish from any source that it is carved **on this panel** rather than on the base or another
   element. **Flagged uncertain; no keystream built from it.**

### The 869 = 869 balance

Left (cipher) side: 869 cells = 865 letters + 4 `?`. Right (tableau) side: 869 cells = 867 letters
+ 2 blanks. I verified both counts against the local transcriptions. This matters: in April 2006
Sanborn stated that a letter was omitted from the cipher side *"for aesthetic reasons, to keep the
sculpture visually balanced"* (Kim Zetter, "Typo Confounds Kryptos Sleuths", *Wired*, 2006-04-20,
<https://www.wired.com/2006/04/typo-confounds-kryptos-sleuths/>). So Sanborn is on record
manipulating letter counts for visual balance — which supplies a **mundane, artist-stated motive**
for a one-letter discrepancy on the tableau side too.

*Caveat on totals:* 865 + 867 = **1732** letters, but the CIA titles its page "*Kryptos* 1,735
Alphabetical letters" (<https://www.cia.gov/legacy/headquarters/kryptos-sculpture/>). I could not
reconcile the 3-letter gap. **Unresolved.**

---

## 4. (d) Keystream files

All in `lateral/keystreams/`, registered in `keystreams/MANIFEST.tsv` (tab-separated:
filename, description, source URL, confidence).

| File | Len | What it is |
|---|---|---|
| `tab_phys_full.txt` | 867 | Panel exactly as carved, all 28 rows, labels + header/footer, letters only |
| `tab_phys_full_rev.txt` | 867 | Reversed (see note below) |
| `tab_ideal_full.txt` | 866 | Ideal panel, no extra L |
| `tab_ideal_full_rev.txt` | 866 | Reversed |
| `tab_phys_body.txt` | 781 | 26 rows, labels and header/footer stripped |
| `tab_ideal_body.txt` | 780 | Same, ideal |
| `tab_core_rows.txt` | 676 | Ideal 26×26 core (wrap-padding removed), row-major |
| `tab_core_cols.txt` | 676 | Ideal 26×26 core, **column-major** |
| `tab_phys_body_cols.txt` | 781 | Physical body, **column-major** |
| `tab_row_labels.txt` | 26 | Row-label sequence `A`–`Z` |
| `tab_col_labels.txt` | 30 | Column-label row `ABCDEFGHIJKLMNOPQRSTUVWXYZABCD` |
| `tab_rowlabel_per_index.txt` | 867 | **Per-index**: row label of each panel letter (`-` = unlabelled header/footer) |
| `tab_collabel_per_index.txt` | 867 | **Per-index**: column label of each panel letter (`-` = label cell, `?` = the extra L, which falls beyond column 30) |
| `tab_anomaly_positions.txt` | 1 no. | `465` |
| `tab_anomaly_letters.txt` | 1 | `L` |
| `tab_last_column.txt` | 28 | Last char of each row — contains `HILL` |
| `tab_last_column_ideal.txt` | 28 | Same, ideal — contains `HIJL` |
| `tab_core_diag_main.txt` | 26 | Main diagonal of the ideal core |
| `tab_core_diag_anti.txt` | 26 | Anti-diagonal of the ideal core |
| `tab_phys_top_plate.txt` | 433 | Top-right plate only |
| `tab_phys_bottom_plate.txt` | 434 | Bottom-right plate only |

Notes on two choices:

- **"The column of the tableau at each index"** is supplied as `tab_collabel_per_index.txt`: an
  867-character stream, aligned 1:1 with `tab_phys_full.txt`, giving the carved column-label letter
  above each position. It is the direct companion to `tab_rowlabel_per_index.txt`. Whole-column
  reads are supplied separately as `tab_core_cols.txt` / `tab_phys_body_cols.txt`.
- **Reversed streams are physically motivated, not decorative.** The letters are cut *through* the
  copper screen, so the panel is legible from both sides and reads mirrored from the far side —
  "the tableau side should be reversed, since the chars are engraved from the other side"
  (<http://scirealm.org/KryptosDetails.html>).

### A warning for whoever runs these

`lateral/keystreams/` is shared with concurrently-running agents, and during this task a sibling
process **deleted every file in it** that was not its own before I had registered mine. I
regenerated and re-registered. **Re-run `python3 lateral/build_tableau_panel.py` and check
`MANIFEST.tsv` before consuming any `tab_*.txt` file**; the script is deterministic, self-verifying
(it re-derives the 867/866/434/435 counts and asserts on the anomaly) and safe to re-run — it
appends to the manifest without clobbering other agents' rows.

---

## 5. (e) Source disagreement — flag every character

**Among current sources: no disagreement at all.** All four transcriptions in §1 agree on every one
of the 867 letters. There is no character I need to flag as contested in present-day sources.

The disagreements are **historical**, and they matter because older material is still in
circulation:

| Source | Disagreement | Effect |
|---|---|---|
| **Doug Gwyn's transcript** (the standard for years) | **Omits the extra `L`** — discovered 2003 | 866 letters, not 867; `HILL` does not appear; every downstream position after 464 shifts by one |
| **CIA transcript** (historical) | Elonka's FAQ says it "has multiple errors which they haven't gotten around to fixing yet" | The page I fetched in 2026 now matches the consensus tableau exactly — apparently since corrected, at least on the tableau side |
| **Sanborn's own sale models** | Extra `L` deliberately **omitted** | 866 letters |
| **Elonka Dunin's transcript** | Endorsed as accurate; not directly fetched (CAPTCHA) | Represented via her endorsement of Wilson's transcript |

Provenance for the Gwyn and CIA rows: Elonka Dunin's Kryptos FAQ —
"Doug Gwyn's transcript was the standard for a long time, but it was learned in 2003 that it had one
omission on the tableau side (a missing 'L')"
<https://web.archive.org/web/20240401065545/http://www.elonka.com/kryptos/faq.html>.

**The single character to check in any inherited data is position 465.** A stream of 866 is
pre-2003 Gwyn-lineage (or a model); a stream of 867 is the sculpture. Any prior K4 work that drew
key material from "the tableau" should be audited for which of the two it used, because the choice
shifts 402 subsequent letters by one place.

---

## 6. Assessment: how much should anyone bet on the extra L?

Recorded honestly, because the `HILL` reading is the most-cited K4 lead attached to this panel:

**Against deliberateness:**
- Sanborn has indicated the extra character was **accidental**; one of the lines is simply one
  character too long (<https://en.wikipedia.org/wiki/Kryptos>,
  <https://www.numberworld.blog/2018/07/kryptos-cipher-part-3.html>).
- **He omits the `L` from the small Kryptos models he sells** — hard behavioural evidence that he
  does not regard it as load-bearing (<https://en.wikipedia.org/wiki/Kryptos>).
- It sits at the **plate seam**, the single most likely place for a fabrication miscount.
- Sanborn has separately admitted adjusting letter counts purely for visual balance
  (<https://www.wired.com/2006/04/typo-confounds-kryptos-sleuths/>), and the two sides do come out
  at 869 cells each *with* the `L` present — a compositional motive, not a cryptographic one.

**For deliberateness:**
- Sanborn also says his work is "rife with mistakes on purpose"
  (<https://rumkin.com/reference/kryptos/k5/>), and the K1 `IQLUSION` / K2 `UNDERGRUUND`
  misspellings are confirmed intentional
  (<https://web.archive.org/web/20240401065545/http://www.elonka.com/kryptos/faq.html>).
- `HILL` is a real English word naming a real cipher, published in *Cryptologia*
  (<https://doi.org/10.1080/01611194.2016.1141556>).

**My read:** the artist's stated position and, more tellingly, his behaviour with the models point
to an accident. Treat `HILL` as a low-prior lead. Note also that Hill 2×2 and 3×3 are already on the
ruled-out list in the task brief — so the panel's most famous anomaly points at a door that has
already been tried.

**The more useful output of this task is the negative result:** the panel is otherwise *perfectly
regular*. It contains no hidden text, no second anomaly, no misspelling, no stray character. As a
source of novel key material it is exhausted by the 21 files in §4 — which is worth knowing before
anyone spends more effort looking for secrets in it.

---

## Sources

- Kryptos — Wikipedia: <https://en.wikipedia.org/wiki/Kryptos>
- CIA, "About the Kryptos Sculpture": <https://www.cia.gov/legacy/headquarters/kryptos-sculpture/>
- John Wilson, "John's Kryptos Details": <http://scirealm.org/KryptosDetails.html>
- `hamidsamak/kryptos`, `tableau.txt`: <https://github.com/hamidsamak/kryptos/blob/master/tableau.txt>
- Elonka Dunin, Kryptos FAQ (Wayback): <https://web.archive.org/web/20240401065545/http://www.elonka.com/kryptos/faq.html>
- Elonka Dunin, Kryptos main page (Wayback): <https://web.archive.org/web/20240401065545/http://www.elonka.com/kryptos/>
- Bauer, Link & Molle, *Cryptologia* 40(6) 2016: <https://doi.org/10.1080/01611194.2016.1141556>
- Kim Zetter, "Typo Confounds Kryptos Sleuths", *Wired*, 2006: <https://www.wired.com/2006/04/typo-confounds-kryptos-sleuths/>
- NumberWorld, "Kryptos – The Cipher (Part 3): intentional vs non-intentional errors": <https://www.numberworld.blog/2018/07/kryptos-cipher-part-3.html>
- Rumkin Kryptos K5 / Sanborn interview extracts: <https://rumkin.com/reference/kryptos/k5/>
