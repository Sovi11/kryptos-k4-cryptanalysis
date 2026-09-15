# The Kryptos tableau as a KEY TABLE

Line of attack: the carved right-hand panel treated as a two-dimensional lookup table and as a
source of structural signal, **not** as a linear string (that reading is already exhausted in
`findings/runningkey.md`). Four questions, from the task brief: (a) the physical-vs-ideal
anomalies as signal, (b) the tableau as a coordinate lookup, (c) the solvekryptos.com published
claim, (d) the column and row-label sequences as key streams.

Scripts: `analysis/tab_common.py`, `analysis/tab_a_anomaly.py`, `analysis/tab_b_lookup.py`,
`analysis/tab_c_solvekryptos.py`, `analysis/tab_d_streams.py`.
Raw logs: `findings/tab_a_out.txt`, `tab_b_out.txt`, `tab_c_out.txt`, `tab_d_out.txt`.
Built on `lateral/tableau_panel.md` and `lateral/tableau_anomalies.json` (re-derived, not trusted);
reuses `analysis/tableau_common.py` (cross-checked against `k4_common.py` at every run).

Nothing was submitted to Paradigm's paid verifier. Date: 2026-09-13.

**Reproduce:** `python3.12 analysis/tab_a_anomaly.py` (and `tab_b_lookup.py`, `tab_c_solvekryptos.py`,
`tab_d_streams.py`). They need numpy, which on this machine lives under `python3.12`/`python3.13`, not
the default `python3`. Each rewrites only its own `findings/tab_*_out.txt`. Runtimes: a 40 s, b 100 s,
c 25 s, d 45 s. `analysis/tab_common.py` is the shared engine and runs the self-test on import of
`main()`; it also prints the Monte-Carlo null when run directly.

---

## 0. Bottom line

**No survivors. Four exhaustive negatives, one of them exact rather than merely thorough, plus one
structural theorem that explains why this whole direction was always going to fail.**

| | result |
|---|---|
| (a) anomalies as signal | **CLOSED.** The deviation set has cardinality 1 and carries **14.5 bits**; a 97-letter key needs **456**. Every selector role it could play (period, offset, shift, decimation step, switch point, phase slip) tested exhaustively: 0 hits in 23.3M trials, all bests at or below chance. |
| (b) tableau as lookup | **CLOSED, EXACTLY.** Collapse theorem: every carved body cell equals `KEYED[(row+col) mod 26]` with **zero exceptions**, so the whole 2-D table carries no more information than a 1-D shift. The full affine lookup family — **88,248,160 coordinate models × 24 combos × 26 rotations = 55,066,851,840 trials** — solved exactly by hash join, not sampled: **0 solutions**. |
| (c) solvekryptos.com | **NOT DERIVABLE, and mechanically proved so.** Their f/g incidence graph is a **forest** (0 cycles, 0 duplicate edges). Consequence: **20,000 of 20,000 uniformly random plaintexts fit the model exactly**. Fitted to public data alone it predicts **0 of the 73 unknown letters**. The brief's "roughly 73 of 97 back-solved" is exactly right: 97 − 24 cribs = 73. |
| (d) column / row-label streams | **NOT previously covered** by `lateral/test_lateral.py` (the `tab_*.txt` files it would have needed were deleted from `lateral/keystreams/` before it ran — 0 present now). Tested here: 2.58M trials, **0 hits**, best joint Hamming **16/24**, the identical chance-level figure `test_lateral.py` got on its own 73 streams. |

**The one finding worth carrying forward is negative and structural** (§2.1): the tableau cannot be a
2-D key source, because it is not 2-D. Any hypothesis of the form "look the key up in the tableau at
coordinates derived from position" is arithmetically identical to "add two position functions mod
26" — a family this repo already ruled out in `findings/geometry.md`. That closes the geometric
reading of "LAYER TWO" as a tableau-lookup instruction.

### Scope, in numbers

| part | explicit crib trials | covered exactly (not sampled) |
|---|---|---|
| (a) anomalies | 23,301,880 | — |
| (b) lookup | 20,785,440 | **55,066,851,840** (affine family, hash join) |
| (c) solvekryptos | 20,000 plaintext fits + 353M gate-rule evaluations (2,920,400 rules × 121 gate maps) | incidence-graph theorem covers all 26⁹⁷ plaintexts |
| (d) streams | 2,582,760 | — |
| **total** | **≈ 46.7 million** | **≈ 55.1 billion** |

**24/24 crib fits found: zero, in every family.** Expected by chance across the whole task: 6.1e-24.

### Calibration used throughout

Every "best n/24" below is quoted against a Monte-Carlo + analytic null. For a **random** 24-letter
key stream, the best-over-26-rotations crib-match count has mean **3.25**; the union bound
26·P(Binom(24,1/26) ≥ k) gives

| k | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|
| P(best ≥ k) | 0.050 | 6.2e-3 | 6.3e-4 | 5.3e-5 | 3.7e-6 | 2.2e-7 | 1.1e-8 | 4.8e-10 |

(Monte-Carlo over 200,000 random streams agrees to within its resolution for k ≤ 8.) A single trial
fits all 24 cribs with probability 26⁻²³ = 4.8e-33 with the rotation free. **A 7/24 happens by
chance once per 1,600 streams and an 8/24 once per 19,000 — in a million-trial sweep both are
guaranteed.** No figure below exceeds what its own trial count predicts.

### Verification

`tab_common.selftest()` runs before every script and asserts: the two independent data loaders agree
on the 97-letter ciphertext and all 24 cribs; encrypt/decrypt round-trips on all 24 combos; K1
re-encrypts to the carved ciphertext under Quagmire-III/PALIMPSEST; and — the one that matters —
**synthetic-key recovery**: a randomly planted 97-letter key is recovered at 24/24 under all 24
combos, its rotation is identified, and a single-letter perturbation is detected as 23/24. No
negative below is reported from an unverified routine.

---

## 1. (a) The anomalies as signal

### 1.1 The deviation list, re-derived

Independently regenerated the ideal tableau and diffed it against the carving (`difflib`,
`autojunk=False`), row-by-row and as one linear stream:

```
opcodes that are not 'equal': 1
  insert  ideal[464:464]='' -> physical[464:465]='L'   (1-indexed physical position 465)
similarity 0.999423 ; rows differing from ideal: 1  -> row 14, label 'N'
```

`lateral/tableau_anomalies.json` agrees with this re-derivation. **The anomaly set is
{(position 465, inserted letter L)}. Cardinality one.** There is no sequence to read.

### 1.2 Why (a) can be closed rather than merely searched

An observer who knows the ideal tableau learns from the carving only *which* position was altered
(log₂ 867 = 9.76 bits) and *which* letter appeared (log₂ 26 = 4.70 bits): **14.46 bits total**. A
97-letter key stream is 456 bits; fitting the 24 crib letters alone needs 113. The anomaly is short
of a key by a factor of 32 and short of the crib block by a factor of 7.8. It **cannot be** the key.
The only coherent roles left are *selector* roles — naming a number or flipping a rule — and that
space is small and finite, so it can be exhausted.

### 1.3 The anomaly position as a number

| role | family size | 24/24 hits | expected | best | chance for that best |
|---|---|---|---|---|---|
| constant additive shift | 24 combos | 0 | — | impossible outright: 0/24 combos have 24 equal required key indices |
| key **period** (each of the 15 numbers the anomaly names: 11, 13, 14, 15, 18, 26, 30, 31, 32, 97, 402, 464, 465, 866, 867) | 15 × 24 | 0 | — | 0/24 combos for every period with c_p > 0 |
| **decimation** step into the tableau, all 4 variants × all starts | 1,164,576 | 0 | 3.3e-27 | 10/24 | E[#≥10] = 0.26, observed 1 |
| **Gronsfeld** digit stream | 15 × 24 × starts | 0 | — | 7/24 | **structurally impossible**: 0/24 combos admit all 24 required shifts inside 0–9 under *any* rotation |

The decimation best (10/24, `phys_rev`, step 30, offset 513, beaufort/plain) decrypts to
`ERIBYEVEMLYJTAEHKNRRU…` with bigram score **−6.98** against English −5.3 and random-text median
−7.50. It is noise.

The **Gronsfeld impossibility** is worth isolating: it is not a search result but an arithmetic one,
and it matches the lateral team's finding that 11–15 of the 24 required shifts exceed 9 for every
numeric stream. Any numeric key derived from anomaly arithmetic is dead before it is tried.

### 1.4 The anomaly letters as a key stream

The deviation list contains one letter. As a key stream it is a constant, i.e. monoalphabetic, which
§1.3 already kills. Best over 24 combos × 26 rotations: **5/24** (P ≤ 0.050). Extending "letters the
anomaly touches" to the row-N body, the plate-seam rows, the `HILL` column and the row labels, used
as repeated key blocks: best **7/24** (P ≤ 6.3e-4), 0 hits in 123,264 trials.

### 1.5 The anomaly position as a switch point — the only reading with real content

This is the one role in which a single datum can do cryptographic work: naming an index *s* at which
the rule changes. Rather than test only the anomaly-derived candidates (465 mod 97 = 77, 464 mod 97
= 76, and 11/13/14/15/18/26/30/31/32), **every model was swept over all 96 interior switch points**,
so the anomaly's own candidates can be scored against the best obtainable by any switch point.

| model | models | consistent | expected by chance | verdict |
|---|---|---|---|---|
| M1 two constant shifts, one either side of *s* | 2,304 | **0** | 1.7e-28 | eliminated |
| M2 the cipher itself changes at *s* (24×24 combo pairs) | 55,296 | **0** | 4.1e-27 | eliminated |
| M3 periodic key, period *p*, phase **jumps** by *d* at *s* | 1,002,240 (108,960 vacuous) | 274 | **3,141** | below chance |
| M4 periodic key, phase **resets** at *s* | 66,816 (4,128 vacuous) | 10 | **120** | below chance |

M3 and M4's "consistent" counts are an order of magnitude *below* chance, and every one of them has
only **c = 1** crib constraint, meaning the key still has p − 23 free letters and the 73 non-crib
positions are entirely undetermined. They are not candidate solutions; they are models too loose to
be tested. Vacuous models (c ≤ 0) are excluded from the counts, never reported as hits.

### 1.6 The phase-slip hypothesis — a new test, and the best-motivated one here

Motivation is documented, not invented. In April 2006 Sanborn announced he had **omitted one
ciphertext letter from K2**, throwing the tail out of phase with the key and making the ending
unreadable. The tableau anomaly is an **inserted** letter. If a running key were drawn from the
carved panel, an insertion is exactly the defect that puts everything after it one place out. So:
running key from the tableau with one letter deleted or duplicated at every slip point, every
offset, all combos, all rotations.

| source | trials | 24/24 | best | P(≥ best) |
|---|---|---|---|---|
| tableau carved (867) | 3,617,376 | 0 | 8/24 | 5.3e-5 |
| tableau ideal (866) | 3,612,672 | 0 | 8/24 | 5.3e-5 |
| carved reversed | 3,617,376 | 0 | 9/24 | 3.7e-6 |
| ideal reversed | 3,612,672 | 0 | 9/24 | 3.7e-6 |
| carved, labels stripped (781) | 3,212,832 | 0 | 9/24 | 3.7e-6 |
| carved body, column-major (781) | 3,212,832 | 0 | 9/24 | 3.7e-6 |
| **total** | **20,885,760** | **0** | **9/24** | expected # at ≥9/24: **77** |

Observed best 9/24 against **77 expected** at that level. The best result is *below* what chance
predicts. Its full decryption scores bigram −7.20 — worse than the median random string. The
phase-slip hypothesis is dead.

---

## 2. (b) The tableau as a lookup table

### 2.1 The collapse theorem — the structural result of this task

Generate the carved body (labels stripped) and test every cell against `KEYED[(row+col) mod 26]`:

```
cells where carved != KEYED[(row+col) mod 26] : 0
```

Zero exceptions — **including the anomalous extra L**. Body row 13 (label N), column 30 gives
`KEYED[(13+30) mod 26] = KEYED[17] = 'L'`, and `L` is exactly what is carved.

**The extra L is not a wrong letter. It is the right letter in an extra column.** The carver
continued that row's own rotation one step too far. This is what a miscount looks like; it is not
what a planted signal looks like, and it is independent behavioural evidence on the side of the
"fabrication slip" reading that `lateral/tableau_panel.md` already favoured on Sanborn's own
statements and his omission of the L from the models he sells. (It also means the `HILL` reading
survives only as a coincidence of where the row happened to stop.)

Consequence, and it is what closes (b):

> For **any** path through the tableau body, `key_i = KEYED[(row_i + col_i) mod 26]`. The two
> coordinates are not independent sources of key material — only their sum matters. A 26×30 table of
> 780 cells holds exactly 26 distinct key values. "Look the key up in the tableau" is arithmetically
> identical to "add two position functions mod 26", which `findings/geometry.md` already swept at
> 100M+ models with a best of 9/24.

Only the 26 row labels (the **plain** alphabet; 25 of the 26 differ from `KEYED[row]`, only `Z`
coincides) and the two header/footer rows escape the rule — handled separately in §2.4. A visible
corollary: the anti-diagonal of the 26×26 core is the constant letter `Z`, because `(i + 25−i)` is
constant. A tableau of this construction has no informative diagonal.

### 2.2 The literal family the brief names: row = i mod r, col = i mod c

| grid | r | c | models | trials | 24/24 | expected | best |
|---|---|---|---|---|---|---|---|
| core26 (26×26) | 1..26 | 1..26 | 676 | 16,224 | 0 | 4.6e-29 | 7/24 |
| body30 carved | 1..26 | 1..31 | 806 | 19,344 | 0 | 5.5e-29 | 7/24 |
| body30 ideal | 1..26 | 1..30 | 780 | 18,720 | 0 | 5.3e-29 | 7/24 |

54,288 trials, 0 hits, best 7/24 (P ≤ 6.3e-4 per stream — i.e. expected).

### 2.3 The full affine family, solved exactly rather than sampled

Model: `row_i = (r0 + p·i) mod mr`, `col_i = (c0 + q·i) mod mc`, `key_i = KEYED[(row+col+t) mod 26]`.
Free: `mr, p, r0, mc, q, c0, t`, and the combo.

* row parameter triples (mr ≤ 28): **7,714**
* column parameter triples (mc ≤ 32): **11,440**
* coordinate models: **88,248,160**
* × 24 combos × 26 rotations = **55,066,851,840 trials**; expected 24/24 by chance **6.1e-24**

By the collapse theorem the crib condition separates: for each of the 26 rotations it inverts to a
required sum vector `v_j`, and `(a_j − v_j) + b_j = const` is separable in the row and column
parameters. So the family is solved by an exact **hash join** in O(7,714 + 11,440) per (combo,
rotation), with every hash hit verified exactly. Runtime **2.0 s**.

> **Verified 24/24 solutions: 0.** The entire affine lookup family is eliminated exactly, not
> sampled. This covers row = i mod r and col = i mod c for all r, c; both diagonals; all eight
> constant knight moves; every start offset and stride.

### 2.4 Walks, non-additive grids, serial readings

| family | models / trials | 24/24 | best | E[# ≥ best] |
|---|---|---|---|---|
| 13 constant-step walks (both diagonals, all 8 knight moves, a (+2,+3) leaper, row-only, col-only) over every start | 251,472 trials | 0 | 8/24 | 13.2 |
| alternating knight moves (not in the affine family) | 1,238,016 trials | 0 | 9/24 | 4.6 |
| label column + header/footer grids, (mr, r0, mc, c0) sweep | 18,604,032 trials | 0 | 10/24 | **4.1** |
| serial readings (raster, boustrophedon, column-major, diagonal), fwd + reversed, every start | 637,632 trials | 0 | 9/24 | 2.4 |

The single best model anywhere in (b) — `full28_ideal`, mr=21 r0=10 mc=29 c0=18,
vigenere/plain/plain/plain, 10/24 — decrypts to
`ZYMUOGNCSQZGMPQOCXRPI…` with bigram **−7.34**, i.e. worse than a random string. Chance produces
4.09 models at 10/24 in that sweep; one was observed.

**Not covered, and said so rather than pretended:** a genuine non-repeating knight's *tour*. The
number of open tours on a 26×30 board is astronomical and the sculpture names no canonical one, so a
"tour" hypothesis has more free parameters than the 97 letters it would explain. It is excluded on
parsimony, not by search.

---

## 3. (c) The solvekryptos.com claim — a mechanical audit

Fairness-critical, so: their data was **re-fetched independently for this task on 2026-09-13** from
`/verify` and `/solution`, and the R-grid, r-grid and gate map match the copy transcribed into this
repo on 2026-09-12 cell for cell. Their paid verifier was not used and nothing was submitted
anywhere. Their stated model, verbatim:

```
r = ( f(C) + g_state(T) ) mod 26
R = r + gate                            gate in {0,1}
P = ( stdpos(C) - R ) mod 26
```

### 3.1 Their arithmetic closes — and that is the trap

* `R_i == (C_i − P_i) mod 26` for their plaintext: **97/97**
* `(R_i − r_i) ∈ {0,1}` for all i, and equals the published gate bit: **97/97**
* gate distribution: 69 ones, 28 zeros

Perfect internal consistency. But `R` is *defined* as `(C − P) mod 26`, so **publishing an R grid is
publishing the plaintext**. The R grid restates the answer; it is not evidence for it. Everything
turns on whether `r`, `f`, `g` and the gate are independently derivable.

### 3.2 What IS derivable: the helper packet, positions 1–66

Their claim is that `T_i` is the letter carved on the tableau side at the same row and column as
K4's ciphertext letter *i*. Reconstructing that from `data/sculpture_panels.txt`:

* **positions 1–66 agree exactly.** This is a real, public, checkable fact and the strongest part of
  their claim. Credit where due.
* **positions 67–97 do not.** The tableau footer row carries 30 letters, not 31, because it has no
  row label, so the same-column reading runs one letter short for the last tier. Their packet marks
  position 67 blank and their "basis handoff" then silently re-reads tableau row Z for that entire
  tier. That is a choice, not a reading. **31 of 97 helper letters are authored.**

### 3.3 The information audit: 73 of 97

`R_i` is computable exactly where `P_i` is public, and `P` is public at the four Sanborn cribs and
nowhere else.

* positions with publicly known plaintext: **24**
* positions where R comes from the **assumed** plaintext: **73**

The brief's "roughly 73 of 97 values are back-solved from an assumed plaintext" is exactly right, and
73 is not approximate — it is 97 − 24. Their own per-position grading (27 derived + 2
public-relational + 22 witness-claimed + 1 bridge + 45 back-solved-only) points the same way:
"witness-claimed" means asserted from the sealed archive, not derived, so at most 29 of 97 are
publicly checkable, and the 24 crib positions are a subset of those.

### 3.4 The decisive test: the incidence graph is a forest

The model's whole cryptographic content is the linear system over ℤ/26

```
f(C_i) + g_state(i)(T_i) = r_i          i = 1..97
```

on a bipartite graph whose left nodes are distinct ciphertext letters, right nodes are distinct
(state, helper-letter) pairs, and edges are positions. **If that graph is a forest, the system is
solvable for every right-hand side** — f and g can be tuned to produce any shift stream, hence any
plaintext, so the model cannot be contradicted by anything.

```
positions (edges)                       : 97
distinct ciphertext letters (f nodes)   : 26
distinct (state, T) pairs (g nodes)     : 82
total nodes V                           : 108
distinct edges E                        : 97
duplicate edges                         : 0
connected components                    : 11
independent cycles  E - V + C           : 0
total consistency conditions on r       : 0
```

Zero cycles and zero duplicate edges under **every** convention for patching the blank at position 67
(their handoff, the packet as published, the literal same-column read — 0 cycles in all three). The
graph is a forest.

Empirical confirmation, because a theorem deserves a test: **20,000 uniformly random 97-letter
plaintexts, gate held at the published bits, f and g free — 20,000 of 20,000 (100.00%) are exactly
realisable by the model.** There are no repeated (C, state, T) triples at all, so no shift stream
whatever can contradict it. Every one of the 26⁹⁷ possible plaintexts fits.

### 3.5 The predictive test: 0 of 73

The fair test of a method: give it only the public inputs — ciphertext, carved tableau, the four
cribs — fit its free parameters to those, and count how many of the remaining 73 letters come out
*forced*.

```
fitting f and g to the 24 crib positions only (gate as published):
  the 24 crib constraints are mutually consistent : True
  of the 73 unknown positions, number whose shift r is FORCED : 0
```

**Zero.** And with the gate treated as unknown — the honest position, per §3.6 — even a forced `r`
would leave two possible letters, so the count stays zero.

### 3.6 The gate map is not positional

Tested `gate_i = [(a·i + b) mod m < k]` over 1,460,200 rules and their negations (431,976 distinct
prediction vectors), plus letter-based gates.

* **Trivial baseline: the gate is 69 ones and 28 zeros, so "gate = 1 always" already scores 69/97.**
* best positional rule: **75/97** (`NOT[(5i) mod 33 < 4]`)
* best letter rule: 66/97 (`C in KRYPTOS`)
* **Permutation null** (shuffle the gate's own 97 bits, re-run the entire rule family against each
  shuffle, 120 shuffles): best-of-family agreement mean **76.4/97**, range 75–79. Observed on the
  real gate map: **75/97**. Shuffles matching or beating it: **120 of 120, p = 1.000.**

The real gate map is fit *less* well by a family of 432,000 positional rules than a random shuffle of
itself. The 97 gate bits are 97 fitted parameters.

### 3.7 Verdict on (c)

| component | status |
|---|---|
| helper packet, positions 1–66 | **derivable** from the carving, and correct |
| helper packet, positions 67–97 | not derivable; footer is 30 letters, substitute pass is authored |
| the R grid | a restatement of (C − P); 24 values public, 73 from the assumed plaintext |
| the f card | 11 of 26 entries claimed forward-derived, 15 back-solved (their own figure) |
| the four g cards | back-solved (their own figure) |
| the 97 gate bits | back-solved; beaten by a permutation null (§3.6) |
| the f/g system as a whole | **a forest: 0 cycles, 0 conditions, fits every possible plaintext** |

**Answer to the question as posed: it is NOT derivable from public data.** Roughly 73 of 97 values
are back-solved from an assumed plaintext, and 73 is exact. Fitted to public data alone the model
predicts nothing; it cannot be refuted by any plaintext. Those are the same fact stated twice.

**Fairness note.** solvekryptos.com publishes this audit against itself, retracted its earlier
"solved" framing, and grades its own positions — its `/verify` page states plainly that the incidence
graph is a forest and that 97/97 agreement "does not independently validate the plaintext or the
method". Nothing here is a charge of bad faith; it is the most careful of the public claims, and its
positions-1–66 helper reading is a genuine contribution. What this section establishes is only that
its model cannot be used as evidence about K4 and that **no part of its plaintext may be borrowed as
a crib** — a point that matters because its text is superficially attractive (the sculpture does have
a compass rose; the Morse slabs do read "T IS YOUR POSITION"), and those are public clues the
reconstructor had in hand.

---

## 4. (d) Column and row-label sequences as key streams

### 4.1 Coverage check first, as instructed

`lateral/test_lateral.py` globs `lateral/keystreams/*.txt`. Checked programmatically at run time:

```
lateral/keystreams/*.txt present now   : 194 files
of those, tableau-derived (tab_*.txt)  : 0
MANIFEST.tsv rows naming tab_* files   : 0
```

`lateral/tableau_panel.md` records that a sibling process deleted every file in that directory that
was not its own; the 21 tableau streams it had registered are gone, and `MANIFEST.tsv` no longer
names them. `lateral/test_lateral_out.txt` confirms it — its 73 surviving streams are all Cyrillic,
Mengenlehreuhr, compass-rose and world-clock material. **No tableau column or row-label stream has
ever been tested by it.** This section is required, not duplicative. (The streams were regenerated
in-process here rather than from that directory, so this result does not depend on a directory other
agents are writing to and deleting from.)

### 4.2 K4-aligned label streams — the literal reading of "the column at each index"

K4 sits opposite tableau rows X, Y, Z and the footer. Taking the **row label** and the **column
label** of each of those 97 cells gives two streams of exactly 97 letters with no offset freedom:

```
row-label : XXXXYYYY…YZZZZ…Z???…?         (the footer row has no row label)
col-label : ABCD?ABCDEFGHIJKLMNOPQRSTUVWXYZABCD?…   (column 1 IS the label column)
```

Every substitution for the unlabelled cells was tried (all 26 letters, and cross-filling from the
other label), plus the physical co-location stream (the tableau letter at the same cell).

| stream family | best over 26 fills × 24 combos × 26 rotations | P(≥ best) |
|---|---|---|
| row label | 6/24 | 6.2e-3 |
| col label | 6/24 | 6.2e-3 |
| row label, gaps from col label | **7/24** | 6.3e-4 |
| col label, gaps from row label | 6/24 | 6.2e-3 |
| tableau letter at the same cell | 7/24 | 6.3e-4 |

130 variants × 24 × 26 = **81,120 trials, 0 hits**, expected 8.9e-30. Best 7/24, with 1.96 expected
at that level.

### 4.3 Every column read and label sequence, as running key and as periodic key

41 streams (each of the 30 body columns read downward, the column-major reads, the per-carved-letter
row and column label streams, the row-label alphabet, the header row, the last-column and `HILL`
streams, both core diagonals), each at every offset and every period, all 24 combos, all 26
rotations:

```
running-key trials 100,344 ; periodic trials 99,360 ; total 199,704
24/24 hits 0 ; expected by chance 5.7e-28
best anywhere: 8/24 ; chance alone produces 10.5 results at that level
```

Note on vacuity: the standing caveat that periods 27–29 and ≥ 53 impose zero crib constraints applies
to a *free* key of that period. Here the key letters are read off a fixed carved stream, so nothing
is free and **every period is a genuine test**. A 24/24 at any period would have been a real result.

### 4.4 Same metric as the lateral sweep, for direct comparison

Re-running `test_lateral.py`'s exact block-Hamming metric (13-letter EASTNORTHEAST key block,
11-letter BERLINCLOCK block, 42 apart) on the tableau streams it never saw:

| | tableau streams (here) | 73 lateral streams (`test_lateral_out.txt`) |
|---|---|---|
| tests | 2,301,936 | 16,538,496 |
| best block1 | 6/13 | 6/13 |
| best block2 | 6/11 | 5/11 |
| **best joint** | **16/24** | **16/24** |

Identical chance-level outcome. P(joint Hamming ≤ 16) = 2.0e-6 per window, so 4.7 such windows are
expected from noise alone in 2.3M. A solution is joint Hamming 0.

---

## 5. What this closes, and what it does not

**Closed by this work:**

1. **The tableau anomaly as signal.** One deviation, 14.5 bits, every selector role exhausted.
   Reinforced by §2.1: the extra L is arithmetically *correct* for its column, which is the signature
   of a miscount rather than a plant. The `HILL` reading exists only because the row stopped one
   letter late.
2. **The tableau as a two-dimensional key table.** Not by search but by the collapse theorem plus an
   exact 55-billion-trial elimination of the affine family. A 2-D lookup into this tableau *is* a 1-D
   shift; the geometry adds nothing. Anyone proposing a coordinate rule into the tableau is proposing
   a position-dependent shift model, and those are already ruled out.
3. **The solvekryptos.com model as evidence.** Forest ⇒ fits every plaintext ⇒ predicts nothing ⇒ its
   97 letters are an input, not an output. Its plaintext must not be used as a crib source.
4. **The tableau column and row-label streams.** Genuinely untested before; tested now; nothing.

**Deliberately not closed, and flagged rather than papered over:**

* **Non-repeating knight's tours** and other unbounded path families through the grid. Excluded on
  parsimony (more free parameters than letters explained), not by search.
* **Which 11 f-table entries** solvekryptos.com regards as forward-derived: not published, so the
  restricted-model test in §3.5 could not be run in their preferred form. The forest result makes it
  moot — no restriction of a forest system gains predictive power unless it adds cycles — but it is
  an unverified gap in their disclosure, not in this audit.
* This work says nothing about systems whose key depends on the **plaintext** or on **non-public**
  material, which remains where the live hypotheses are.

**One negative worth stating positively.** The tableau has now been attacked as a linear string
(`runningkey.md`), as lateral key material (`lateral/`), and here as a key table and as a coordinate
system. All three fail, and §2.1 explains why the third had to: the panel is a *display* of the keyed
alphabet, not a container of extra entropy. Its 867 carved letters encode exactly 26 distinct values
plus a row/column labelling, and every one of those values is already available from the string
`KRYPTOSABCDEFGHIJLMNQUVWXZ`. **The tableau side of the sculpture contains no key material that the
keyed alphabet does not already give you.** Whatever "LAYER TWO" points at, it is not a second layer
of key hidden in the tableau's geometry.
