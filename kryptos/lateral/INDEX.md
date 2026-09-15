# Kryptos K4 — lateral sources index

**What this folder is.** The "lateral key material" line of attack: the hypothesis that K4's key is
not in the ciphertext or the tableau but *somewhere else* — on the sculpture, on its siblings, or in
the objects the plaintext points at. Every source was transcribed or derived from a cited public
record, converted into candidate keystreams, and tested against the four Sanborn cribs.

**Status, stated precisely.** 194 keystreams were generated; **128 of them are long enough to be
testable** (73 with ≥ 11 letters, 55 with ≥ 24 digits, of which 7 are ≥ 97-bit binary) and all 128
were tested, under running-key, periodic-key, Gronsfeld and one-bit-gate models, across 24
cipher/alphabet combinations and all 26 key-alphabet rotations: **nothing above chance**. The
remaining 66 hold 1–10 letters or 1–23 digits and are too short to be a running key for a 13- or
11-letter crib block at all (see §5, item T5). The strong form of the lateral hypothesis — *the
K4 key is a public sequence readable off the Mengenlehreuhr, the Weltzeituhr, the compass rose, the
Cyrillic Projector or Antipodes* — is closed. The weak form — *some lateral object supplies the key
by a mechanism nobody has guessed* — is not closed by anything, and cannot be.

Nothing here is a proposed solution. Nothing here was submitted to Paradigm's paid verifier.

Last revised 2026-09-13. **This is a snapshot.** Other agents write into this repository
concurrently; several items that were open when §5 was first drafted were closed while it was being
written, and are marked **[closed …]** below. Check file timestamps before trusting any "untested"
claim here.

---

## 1. The lateral sources

| # | Source | What was recovered | Report | Testable key material? | Test outcome |
|---|---|---|---|---|---|
| 1 | **Right-hand *Kryptos* panel (the Vigenère tableau)** | Full 28-row transcription, 867 carved letters in 869 cells, diffed against a generated ideal tableau. **Exactly one anomaly: an extra `L` appended to row `N`, at 1-indexed position 465 of the letter stream.** No second hidden anomaly. Two blank cells, no `?`, no superscripts. | [`tableau_panel.md`](tableau_panel.md); data in `tableau_anomalies.json`, `build_tableau_panel.out.txt` | **21 streams designed and documented in `keystreams/_rows_tableau.tsv` — but the `.txt` files are NOT on disk.** See §5, item T1. | Negative on two independent fronts. (i) As **running keys**: the physical, ideal and label-stripped tableaux gave 0 exact hits and 0 within Hamming 2, best joint 16/24 ([`../findings/runningkey.md`](../findings/runningkey.md)). (ii) As a **coordinate lookup** — the "LAYER TWO" reading, constraint C11 — closed 2026-09-13 by `../analysis/tab_a_anomaly.py` and `tab_b_lookup.py` (`../findings/tab_a_out.txt`, `tab_b_out.txt`), which show the carved body satisfies `cell(row,col) = KEYED[(row+col) mod 26]` at **every** cell, so any lookup path yields only **26 distinct key values** and the two coordinates collapse to their sum. The same result reclassifies the extra `L`: it is the *right* letter in an *extra column*, i.e. a miscount, not a planted signal. |
| 2 | **Mengenlehreuhr / Berlin-Uhr** (Budapester Str., Europa-Center) — the clock the community assumed for a decade | Lamp geometry (row lengths 1,4,4,11,4 = 24 fields), cumulative totals, lamp weights, quarter-markers, full 24-bit lamp patterns, and the lamp state at **21 named candidate timestamps** (Wall fall, Schabowski's press conference, Bornholmer Straße opening, *Kryptos* dedication, the clock's own installation, K2's coordinates read as a time, …) plus 7 whole-day tick streams | [`berlin_clock.md`](berlin_clock.md) §1, §3, §4 (written 2026-09-13) | Yes: **163 `mlu_*` streams**, registered in `keystreams/MANIFEST.tsv` with source URL and confidence | **Negative.** Included in the 16.5M-test block sweep and the numeric sweep below. Also **retired on the merits**: Sanborn said in Nov 2025 that BERLINCLOCK means the *World Clock*, not this one ([Scientific American](https://www.scientificamerican.com/article/cia-kryptos-puzzle-creator-releases-final-clues/)). |
| 3 | **Urania-Weltzeituhr (World Clock), Alexanderplatz** — the clock Sanborn confirmed in Nov 2025 | 24-hour ring structure, icositetragon geometry, the 24 time-zone hour offsets | [`berlin_clock.md`](berlin_clock.md) §2 | Yes: **5 `wz_*` structural streams**, plus the Weltzeituhr's own opening time fed through the lamp model as `mlu_t_wz_open_0930_*` | **Negative**, same sweeps. Note the honest caveat: the Weltzeituhr is a *thematic* referent for the plaintext; nothing Sanborn said implies it supplies key material. |
| 4 | **Compass rose and bearings** (the engraved rose pointing at the lodestone; and the EAST NORTHEAST bearing the cribs themselves spell) | 16- and 32-point compass abbreviations, English and German point names, bearing values in degrees | [`berlin_clock.md`](berlin_clock.md) §5, §6 | Yes: **7 `rose_*` streams** + `geo_bearings_digits.txt` | **Negative.** Best periodic fit in the whole letter corpus came from here — `rose_16_words_de.txt` at period 14, **6/24 cribs**, against a chance expectation of 0.92/24 per test and ~24 such ≥6/24 events expected across the 102,192 periodic tests. That is chance. |
| 5 | **Antipodes (1997, Hirshhorn) — the Cyrillic face** | Cyrillic ciphertext and plaintext, plus the "extra" Cyrillic block unique to *Antipodes*; transliterations and ord-26 reductions | none | Yes: **9 `antipodes_cyrillic_*` files** — **not registered in `MANIFEST.tsv`** (§5, item T3) | **Negative** as K4 key material, though this corpus produced the three "best" (chance-level) numbers in the sweep: best block-1 Hamming 6/13, best block-2 5/11, best joint 16/24. Separately, the Cyrillic cipher **itself** was fully recovered on 2026-09-13 by `../analysis/antipodes_agency_verify.py` (`antipodes_agency_verify_out.txt`): ACA **Quagmire II**, key **МЕДУЗА / MEDUSA** (carved on the sculpture in Latin letters), key restarting at character 777 at the message-1/message-2 boundary; encrypt and decrypt both round-trip 1558/1558. |
| 6 | **Cyrillic Projector (1993/1997, UNC Charlotte)** | Cyrillic ciphertext as carved and as ordered, plaintext, and the Cyrillic keyed alphabet; transliterations, ord-26 and ord-32 reductions | none | Yes: **10 `cyrillic_*` files** — **not registered in `MANIFEST.tsv`** (§5, item T3) | **Negative** as K4 key material, same sweeps. The CP ciphertext is an exact prefix of the *Antipodes* Cyrillic ciphertext and decrypts under the same Quagmire II / MEDUSA system. **Data defect found:** `keystreams/cyrillic_projector_plaintext_cyrillic.txt` disagrees with the verified decryption at indices 777 and 778 (file `З`,`Я`; decryption `О`,`Б`) — 1131/1133 elsewhere. Fix before reusing that file. |
| 7 | **Fall of the Berlin Wall, 1989-11-09** (Schabowski's press conference; Bornholmer Straße) | Eight candidate timestamps, used to drive the Mengenlehreuhr lamp model: 18:50, 18:53, 19:00, 19:04, 19:05, 20:00, 21:20, 23:30 | none | Yes, as the `mlu_t_wallfall_*` families (48 files) | **Negative.** Sourced to [chronik-der-mauer.de](https://www.chronik-der-mauer.de/en/chronicle/_year1989/_month11/), [bpb.de](https://www.bpb.de/themen/deutschlandarchiv/302060/2-schabowski-und-die-oeffnung-der-grenzen-am-9-november-1989/) and [Wikipedia: Bornholmer Straße](https://en.wikipedia.org/wiki/Bornholmer_Stra%C3%9Fe_border_crossing). |
| 8 | **Morse-code granite slabs ("K0")** | The published reading, with the genuine transcription disagreements flagged | [`berlin_clock.md`](berlin_clock.md) §5; `../data/morse_and_misc.txt`; README §1.4 | Yes, but generated earlier, not here | **Negative** — tested as a running key in two orderings, forwards and reversed, in [`../findings/runningkey.md`](../findings/runningkey.md). |
| 9 | **Lodestone, courtyard stonework, the buried USGS marker** | Descriptive only | [`berlin_clock.md`](berlin_clock.md) §5, §6; README §1.5 | **No.** Nothing here reduces to a letter or digit sequence without inventing the reduction. | not applicable |
| 10 | **Antipodes — the *Latin* (Kryptos) face** | **RECOVERED 2026-09-13** (superseding the "not obtained" state this index was drafted in): 47 rows, 1,590 glyphs, order K3 K4 · gap · K1 K2 K3 K4 K1 K2, truncated inside the final K2. | `antipodes_agency_verify_out.txt` Part 1 | Not key material — but a **second independent carving** of the same ciphertext | **The single most useful result in this folder.** K4 appears **twice** on *Antipodes* (stream offsets 337 and 1206) and **both copies are letter-for-letter identical to the Kryptos K4**. The whole 1,590-glyph Latin stream differs from the Kryptos panel at exactly **one** letter — K2 offset 115, Kryptos `R` → Antipodes `E` — and *Antipodes* also carries 2 carved dots and 7 `?` where Kryptos has 0 and 4. So the K4 carving is independently corroborated; constraint **C6** (a mis-carved K4 letter voiding the exact-fit sweeps) is much weaker than it was. |

---

## 2. The test harness and what it found

Two scripts, both in this folder, both re-run and their output captured on 2026-09-13:

| script | output | corpus | tests |
|---|---|---|---|
| `test_lateral.py` | `test_lateral_out.txt` | 73 keystream files with ≥ 11 letters; 27,380 letters total | block-1 16,538,496 · block-2 16,629,600 · joint 15,390,336 · periodic 102,192 |
| `test_lateral_numeric.py` | `test_lateral_numeric_out.txt` | 55 files with ≥ 24 digits (2,047 digits); 7 files of ≥ 97 bits | Gronsfeld 24,564 · digit-pairs-mod-26 10,728 · gate 2,037 |

**Model.** Each of the 24 combinations {Vigenère, Beaufort, variant-Beaufort} × {plain, KRYPTOS}
plaintext alphabet × {plain, KRYPTOS} ciphertext alphabet forces a specific 13-letter key block at
crib positions 22–34 and a specific 11-letter block at 64–74, with a fixed 42-position gap between
their starts. Each block is slid against every keystream at every offset, under all 26 key-alphabet
rotations, and scored by Hamming distance. A real keystream would appear at Hamming **0**.

### Results, each against its chance expectation

| test | best observed | expected max under the null | verdict |
|---|---|---|---|
| block-1, 13 letters | Hamming **6/13** = 7 matches (`antipodes_cyrillic_extra_plaintext_translit`, offset 105) | E[#≥7/13] = 2.9; E[#≥8/13] = 0.086 → expected max ≈ 7 | **exactly at chance** |
| block-2, 11 letters | Hamming **5/11** = 6 matches (`antipodes_cyrillic_ciphertext_ord26`, offset 88) | E[#≥6/11] = 21; E[#≥7/11] = 0.60 → expected max ≈ 6–7 | **at or below chance** |
| joint, 24 letters | Hamming **16/24** = 8 matches (`antipodes_cyrillic_ciphertext_translit`, offset 945) | E[#≥8/24] = 31; E[#≥9/24] = 2.2; E[#≥10/24] = 0.13 → expected max ≈ 9 | **below chance** |
| hits within threshold (B1≤2, B2≤2, joint≤4) | **0** | E = 3.3×10⁻⁷, 1.6×10⁻⁴ and 7.1×10⁻¹⁸ respectively | 0 is what the null predicts — the value of the test is that a *real* key would have sat at Hamming 0, and none did |
| stream as a periodic key (prefix of length N repeated, N = 2…97) | **6/24** cribs (`rose_16_words_de`, N = 14) | 0.92/24 per test; E[# ≥6/24 across 102,192 tests] = 24.4 | **at chance** |
| numeric streams as Gronsfeld | **7/24** (`rose_32_bearings_digits`, offset 50) | E[# ≥7/24 across 24,564 tests] = 0.59 | at chance within a factor of two — **and structurally impossible anyway**: 11–15 of the 24 required shifts exceed 9 in every alphabet combo, so no digit stream can supply them |
| digit-pairs mod 26 | **6/24** (`rose_32_bearings_digits`, offset 42) | E[# ≥6/24 across 10,728 tests] = 2.6 | **at chance** |
| binary streams as a one-bit alphabet gate | best 1 of 2 gate states forcing a single shift value | a working gate needs **both** states to force one value each | **no gate state works** |

**Reading this honestly.** Three things are worth separating.

1. The *exact-match* tests are decisive within their scope: if any of these 73 letter sequences were
   the K4 keystream, at any offset, under any of the 24 combos and 26 rotations, it would have
   appeared at Hamming 0. None did. That closes the sources listed in §1 as **direct running keys**.
2. The *near-match* numbers are not near-misses. Every "best" is at or below the maximum you get by
   sliding random text of the same volume past the target. Where an observed best falls *below*
   chance (the joint block does), that deficit is not evidence of anything either — the crib shifts
   are fixed, not random, and the corpus is internally correlated (reversed and transliterated
   copies of the same text).
3. The Gronsfeld result is the only **structural** impossibility in the set, and it is the strongest
   thing in this folder: a Gronsfeld key is a digit, so it can only supply shifts 0–9, and the cribs
   demand shifts above 9 at 11–15 of the 24 positions depending on the alphabet pair. No numeric
   sequence from any source can be a Gronsfeld key for K4. That holds for every digit stream that
   will ever be proposed, not just these 55.

---

## 3. Verified ground truth

Everything in this section has been re-derived computationally inside this repository, not merely
cited. Scripts: `../analysis/k4_common.py`, `runningkey_lib.py`, `two2_lib.py`, `geo2_common.py`.

### 3.1 The keyed alphabet

```
KRYPTOSABCDEFGHIJLMNQUVWXZ
```

`KRYPTOS` followed by the remaining letters in order; all 26 present. This is the alphabet the
right-hand panel tabulates, and it is used as plaintext, ciphertext **and** key alphabet in K1 and
K2 — i.e. the system is ACA **Quagmire III**, not plain Vigenère, although most write-ups say
"Vigenère".
<https://en.wikipedia.org/wiki/Kryptos>

### 3.2 K1, K2, K3

| section | length | system | key | verified how |
|---|---|---|---|---|
| **K1** | 63 letters | Quagmire III, KRYPTOS alphabet | **PALIMPSEST** | Re-encrypting the K1 plaintext reproduces the carved ciphertext **exactly**. `IQLUSION` for `ILLUSION` is deliberate (or a `PALIMPCEST` keyword slip — the arithmetic is consistent with both; README §2.2). |
| **K2** | 369 letters carved / **370** plaintext | Quagmire III, KRYPTOS alphabet | **ABSCISSA** | Re-encryption matches the carving for the **first 361 letters**, then expects `SWJLLAETG` where the sculpture carries `WJLLAETG` — the one omitted `S`, exactly as Sanborn admitted in 2006. `UNDERGRUUND` is deliberate. |
| **K3** | 336 letters + a final `?` | **Route transposition, no substitution** | **none — no keyword is required** | The ciphertext is an exact anagram of the plaintext. Concrete procedure: write into rows 24 wide, read out by columns rightmost-first top-to-bottom; then write that into rows 8 wide and repeat. The width pairs (8,24), (12,16), (16,12), (4,48), (48,4) work identically; an exhaustive search over widths 2–59 found exactly those six. The widely quoted "key KRYPTOS = 0362514" is decoration, not necessity. `DESPARATLY` is deliberate. |

K2's corrected ending is **`... WEST X LAYER TWO`**, not `... WEST ID BY ROWS`. Full history of that
correction, including who found it and every statement about what it implies for K4, is in
[`clue_history.md`](clue_history.md) §6.

### 3.3 The K4 cribs — verified, with disagreements flagged

K4 ciphertext, 97 letters (`../data/k4_ciphertext.txt`):

```
OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR
```

| clue | positions (1-indexed, inclusive) | ciphertext | plaintext | released |
|---|---|---|---|---|
| EAST | **22–25** | `FLRV` | `EAST` | privately Apr 2020; public **2020-08-24** |
| NORTHEAST | **26–34** | `QQPRNGKSS` | `NORTHEAST` | **2020-01-29**, *NYT* |
| BERLIN | **64–69** | `NYPVTT` | `BERLIN` | **2010-11-20** online / 11-21 print, *NYT* |
| CLOCK | **70–74** | `MZFPK` | `CLOCK` | **2014-11-20** online / 11-21 print, *NYT* |

Machine-readable: [`keystreams/clue_positions.tsv`](keystreams/clue_positions.tsv). Identical to
`../data/cribs.json`.

**Why these numbers are safe.** Every source that published a clue published the *ciphertext
letters* next to the position number, and each of `FLRV`, `QQPRNGKSS`, `NYPVTT` and `MZFPK` occurs
**exactly once** in the 97 letters — at the stated 1-indexed start. Under 0-indexing the same
numbers would name `LRVQ`, `QPRNGKSSO`, `YPVTTM` and `ZFPKW`, which no source has ever printed. The
numbering is therefore pinned by the data, not by a convention anyone could have got wrong. Full
argument, including a second geometric check off the panel row boundaries, in
[`clue_history.md`](clue_history.md) §1.

**Source disagreements found — flagged, none affecting the numbers:**

* **[flagged] *Smithsonian Magazine* swaps the words against the positions.** Verbatim: "The other
  two hints—'clock' and 'Berlin,' released in 2010 and 2014, respectively—sit back-to-back at
  positions 64 through 69 and 70 through 74." Read in order that assigns *clock* → 2010 → 64–69 and
  *Berlin* → 2014 → 70–74. Both are backwards. The numbers are right; the word order is wrong.
  [link](https://www.smithsonianmag.com/smart-news/third-and-final-clue-released-ci-sculptures-last-puzzling-passage-180974102/)
* **[flagged] The same piece dates the sculpture to 1991.** It was dedicated **1990-11-03**.
* **[resolved] 2010-11-20 vs 11-21** for BERLIN, and **2014-11-20 vs 11-21** for CLOCK: online vs
  print. The msnbc syndication timestamp (Nov 20, 2010, 8:43 PM EST) settles the first.
* **[resolved] NORTHEAST dated "February 2020"** by some aggregators. First publication is
  **2020-01-29**; the NPR interview aired 2020-01-30; *Smithsonian* ran 01-31.
* **[open] The given name of the person who found LAYER TWO in 2005.** Wikipedia says **Nicole**
  Friedrich; Elonka Dunin's own timeline and LEMMiNO say **Monet** Friedrich, on 2005-10-11. Dunin
  ran the group where it happened. This repository's `README.md` and `data/k1_k3_plaintext.txt`
  currently follow Wikipedia. Nothing cryptanalytic depends on it.
* **[not a disagreement, but the real caveat] What a clue *means*.** At the 2013 ACA convention
  Sanborn confirmed the letter-for-letter mapping emphatically (N=B, Y=E, P=R, V=L, T=I, T=N;
  "decodes"). At a 2019 dinner he **declined to reaffirm it**, committing only to "K4 is exactly 97
  characters long, and BERLIN is plaintext that starts at exactly the 64th character". The strong
  (position-preserving) reading is this project's working assumption and the basis of nearly every
  negative on record. It is an assumption. Tracked as constraint **C2** in
  [`../findings/sanborn_statements.md`](../findings/sanborn_statements.md).

### 3.4 The tableau anomaly

The carved right-hand panel has **867** letters where an ideal tableau has **866**. The single
difference is an extra `L` appended to row `N` (1-indexed position 465 of the letter stream). The
consequence is that the rightmost column reads `…H I L L…` down rows L, M, N, O instead of
`…H I J L…` — the "HILL" of Bauer, Link & Molle's *Cryptologia* matrix-encryption conjecture
([doi:10.1080/01611194.2016.1141556](https://doi.org/10.1080/01611194.2016.1141556)). Two things to
carry: Sanborn **omits the extra L from the scale models he sells**, which is weak evidence it was a
fabrication slip; and Hill 2×2 and 3×3, linear and affine, both directions, both alphabets, all
alignments, are independently closed in [`../findings/families.md`](../findings/families.md).

---

## 4. Files in this folder

| file | what it is |
|---|---|
| `INDEX.md` | this file |
| [`clue_history.md`](clue_history.md) | every released clue with exact date, published wording, outlet and positions; the position verification; the 2006 correction; every hint about K4's nature |
| [`tableau_panel.md`](tableau_panel.md) | the right-hand panel transcribed and diffed against an ideal tableau |
| `build_tableau_panel.py` / `.out.txt` / `tableau_anomalies.json` | the code and output behind it |
| [`berlin_clock.md`](berlin_clock.md) | both Berlin clocks, every Sanborn statement about "BERLIN CLOCK", the compass rose, lodestone and Morse slabs, the K2 coordinates, and what failed (arithmetic: `../analysis/berlin_clock_doc_checks.py`) |
| `gen_berlin_clock_keystreams.py` | generates the 176 clock / world-clock / compass streams; every derivation is in the script, not asserted |
| `antipodes_agency_verify_out.txt` | the *Antipodes* Latin- and Cyrillic-face verification — K4 carved twice and identical, and the Cyrillic cipher recovered (script: `../analysis/antipodes_agency_verify.py`) |
| `test_lateral.py` / `test_lateral_out.txt` | the 16.5M-test letter-stream sweep |
| `test_lateral_numeric.py` / `test_lateral_numeric_out.txt` | Gronsfeld, digit-pair and binary-gate sweeps |
| `keystreams/` | 194 `.txt` keystream files plus one `.csv` |
| `keystreams/MANIFEST.tsv` | 176 of them, with description, source URL and confidence (high 44 / medium 83 / low 49). The remaining 19 — every Cyrillic/Antipodes file — are unregistered; see §5, item T3 |
| `keystreams/_rows_tableau.tsv` | 21 **designed but unwritten** tableau streams, with descriptions |
| `keystreams/clue_positions.tsv` | the four crib positions, machine-readable |

---

## 5. To do — what remains unrecovered or untested

Ordered by value as originally drafted. Three of the seven items were closed by parallel work on
2026-09-13 while this index was being written; they are kept in place, marked, because the results
matter more than the to-dos did. **Still open: T3, T5, T6, T7.**

**[CLOSED 2026-09-13] T4 — Obtain a letter-level transcription of *Antipodes*' Latin (Kryptos)
face.** Done, by `../analysis/antipodes_agency_verify.py`; output in `antipodes_agency_verify_out.txt`.
The finding is the strongest thing in this folder and is worth restating: *Antipodes* carves K4
**twice**, at stream offsets 337 and 1206, and **both copies are letter-for-letter identical to the
Kryptos K4**. Across the entire 1,590-glyph Latin stream there is exactly one letter difference
(K2 offset 115, `R` → `E`), plus 2 carved dots and 7 `?` against Kryptos's 0 and 4. Residual work:
fold this into `../findings/sanborn_statements.md` constraint **C6**, which assumed the K4 carving
was unverified.

**[LARGELY CLOSED 2026-09-13] T1 — the 21 tableau keystream files.** The `.txt` files described
in `keystreams/_rows_tableau.tsv` are still absent, so `test_lateral.py` never saw them — but the
question they existed to answer has been settled analytically rather than by sweep. `tab_b_lookup.py`
(`../findings/tab_b_out.txt`) proves the carved tableau body satisfies
`cell(row, col) = KEYED[(row + col) mod 26]` at every cell, so **every** lookup path through it —
column-major, diagonal, per-index row/column label, plate split — returns one of only 26 distinct key
values determined by `(row + col) mod 26`. The two coordinates are not independent key material.
That closes constraint **C11** ("LAYER TWO" as a coordinate lookup) far more cleanly than writing
and sweeping 21 files would have. Residual: write the files anyway if the label rows and
header/footer (which are the *plain* alphabet and are the only cells not on that surface) are ever
to be swept separately.

**[CLOSED 2026-09-13] T2 — Write `berlin_clock.md`.** Done: [`berlin_clock.md`](berlin_clock.md)
now covers both clocks, every Sanborn statement about "BERLIN CLOCK", what was generated and how it
failed, the compass rose, lodestone and Morse slabs, and the K2 coordinates. Its backing arithmetic
is `../analysis/berlin_clock_doc_checks.py`.

**T3 — Register the Cyrillic and Antipodes streams in `MANIFEST.tsv`.** Nineteen files
(9 `antipodes_cyrillic_*`, 10 `cyrillic_*`) sit in `keystreams/` with no manifest row, so they carry no
recorded source URL or confidence — even though they produced the three "best" (chance-level)
numbers in the whole sweep. They also need reports: there is no `cyrillic_projector.md` or
`antipodes.md` in this folder, only the raw files. Provenance should cite
[Cyrillic Projector](https://en.wikipedia.org/wiki/Cyrillic_Projector) (solved by Frank Corr, July
2003, and independently Mike Bales, September 2003) and
[Antipodes](https://en.wikipedia.org/wiki/Antipodes_(sculpture)), and should now record the verified
system: **Quagmire II, key МЕДУЗА/MEDUSA, key restart at character 777**
(`antipodes_agency_verify_out.txt` Part 3). **One file is defective and should be fixed first:**
`keystreams/cyrillic_projector_plaintext_cyrillic.txt` disagrees with the verified decryption at
indices 777 and 778.

**T5 — Short streams as short periodic keys.** 66 of the 194 files were seen by neither harness: 38
hold only 1–10 letters (below `test_lateral.py`'s ≥ 11 filter) and 28 hold only 1–23 digits (below
`test_lateral_numeric.py`'s ≥ 24 filter). None can be a running key for a 13- or 11-letter block, so
that is not a gap — but the 38 short letter streams were never tried as **periodic** keys of period
2–10 either. That is **formally uncovered and almost certainly subsumed**:
`../findings/families.md` solved for the key directly at periods 2–25 under both the plain and
KRYPTOS alphabets and found that *no* key of any period ≤ 13 satisfies the cribs at all, which would
include any short lateral stream. Cheap to close properly; low expected yield. The 28 short digit
files are covered by the Gronsfeld impossibility result regardless.

**T6 — Read the sealed material that exists.** Two documents would settle more than any sweep:
Sanborn's 2009 Archives of American Art oral history (6.5 hours, the longest first-person account of
the encoding process; `aaa.si.edu` returns 403 to scripted fetches — a human should read it), and
the K1/K2 coding charts the *NYT* published in 2010, which Sanborn has repeatedly said reward study
("if [studied] in a forensic manner, there might be revelations in there").
<https://www.aaa.si.edu/collections/interviews/oral-history-interview-jim-sanborn-15700> ·
<https://www.nytimes.com/2010/11/21/us/21codecharts.html>

**T7 — Watch for K5.** Not a lateral source, but it dwarfs everything in this folder. K5 is 97
characters, was built on the same 1988 worksheet, and Sanborn says the two messages "share some of
the same coded words in the same position". If both are position-preserving encipherments under the
same chart, the key cancels in the position-wise difference and the shared words give runs of zeros
— classical depth-2, worth more than all four cribs combined. Paradigm holds the ciphertext and says
it plans to release it. Monitor <https://www.paradigm.xyz/kryptos/k4>. Constraint **C10**.

---

## 6. What this folder does *not* license anyone to say

* Not "the Berlin Clock is ruled out as a key". What is ruled out is the 163 specific sequences in
  `keystreams/`, under the models in §2. A different reduction of the same clock is a different
  hypothesis.
* Not "lateral key material is impossible". The Gronsfeld result is the only claim here that
  generalises beyond the streams tested.
* Not "the crib positions are certain to be a letter-for-letter mapping". They are certain to be
  *positions*; the mapping is the working assumption (§3.3).
* Not "K4's flat index of coincidence proves the masking worked". For 97 letters the null IoC is
  0.0385 ± 0.0028 and the observed 0.0361 sits at z = −0.84 — unremarkable. 97 characters is too
  short to tell a masked ciphertext from a random string.

---

## 7. Related reading in this repository

| file | subject |
|---|---|
| [`../README.md`](../README.md) | the sculpture, K1–K3, the 2025 auction and the Paradigm verifier |
| [`../findings/sanborn_statements.md`](../findings/sanborn_statements.md) | tiered dossier of every Sanborn/Scheidt statement, and constraints C1–C18 |
| [`../findings/prior_art.md`](../findings/prior_art.md) | published prior art and a forensic audit of every claimed public solution |
| [`../findings/families.md`](../findings/families.md) | periodic and digraphic cipher families — all negative |
| [`../findings/runningkey.md`](../findings/runningkey.md) | running key and autokey from the sculpture's own texts — all negative |
| [`../findings/geometry.md`](../findings/geometry.md) | panel geometry, reading orders, lag 7, the number 97 — all negative |
| [`../findings/twocipher.md`](../findings/twocipher.md) | two-stage transposition + substitution stacks — all negative |
| [`../findings/crib_placement.md`](../findings/crib_placement.md) | crib-placement work |
| [`../findings/statistics.md`](../findings/statistics.md) | the statistical profile of K4 and what it does and does not support |
| `../findings/tab_a_out.txt`, `tab_b_out.txt` | the tableau as anomaly source and as a key table — the `(row+col) mod 26` collapse result |
| [`clue_history.md`](clue_history.md) | the clue record, verified |
