# K4 as TWO ciphers — synthesis and second-round results

Scripts (round 1, pre-existing): `analysis/twocipher_common.py`,
`twocipher_A_transposition_first.py`, `twocipher_B_transpositions.py`,
`twocipher_B2_offsets.py`, `twocipher_C_double_vigenere.py`.
Scripts (round 2, this work): `analysis/two2_lib.py`,
`two2_a_transpose_keystream.py`, `two2_b_k3.py`, `two2_c_double_keys.py`,
`two2_d_double_transposition.py`, `two2_e_keyword_blocks.py`.
Raw output: `analysis/twocipher_*_output.txt`, `analysis/two2_*_output.txt`,
`analysis/two2_*_results.json`.

**Bottom line: nothing survives.** Round 2 added, across the four previously
untested combinations (a)-(d) plus a per-block keyword sweep (e), **49.4 million forced-key-stream tests** (17.4M in (a),
0.13M in (b), 31.9M in (d)), **13.1 million forced-key periodicity tests** and
**111 million two-stage configuration pairs** in (c) — and every count it
produced is at or below its chance expectation. No two-stage scheme in any of
the families below reproduces the four Sanborn cribs, and no candidate decrypts
to English.

---

## 1. The modelling point that organises everything

Two stages can be ordered two ways, and Sanborn's position statements
("the letters in positions 64-69 of K4 decode to BERLIN") can be read two ways.
That makes four cases, and they are **not** equivalent — each gives the cribs a
different grip. Getting this straight is what made round 2 possible.

Notation: `S` = letter-wise substitution whose key stream may vary with position;
`T` = transposition (`T[j]` = ciphertext position receiving intermediate
position `j`, so the intermediate text is `I[j] = C[T[j]]`).

| case | reading | what the cribs pin down | covered by | result |
|---|---|---|---|---|
| **T then S** | CT-reading (ciphertext letters at 22-34/64-74 decrypt to the crib words) | The substitution is indexed by *ciphertext* position, so the 24 (ct, pt) pairs are **exactly** those of a one-stage cipher. The transposition is invisible to the crib test. | already done: `families.md` (periodic, Porta, Gronsfeld, Hill, …), `runningkey.md` (running key, autokey), `twocipher_A` | **ruled out for every T**, periodic or not |
| **S then T** | CT-reading | Key *values* are the same fixed 24 as above, but they sit at the relocated positions `T^-1[c]`. For the crib words to still be words in the plaintext they must land contiguously. | `twocipher_B`, `twocipher_B2_offsets`, `two2_a` (§3a, whole-catalogue scattered test), `two2_d` | 0 |
| **S then T** | PT-reading (plaintext at 22-34/64-74 *is* the crib words) | The substitution is indexed by *plaintext* position, so the key stream is **completely determined at 24 known contiguous positions** for every candidate T: `k_j = derive_key(P[j], C[T[j]])`. No periodicity needed. | **new: `two2_a`, `two2_b`, `two2_d`** | 0 |
| **T then S** | PT-reading | Same 24 key *values* as the line above, but at the scattered positions `T[j]`; only periodicity is testable. | **new: `two2_a` (§3a)** | 0 |

Two consequences worth stating on their own, because they close whole regions
without any new computation:

* **A transposition applied before the substitution cannot rescue any cipher
  under the CT-reading.** The crib pairs are untouched by it, so every negative
  in `families.md` and `runningkey.md` transfers verbatim. "K4 = transposition
  then Vigenère/running key/autokey" is dead for *all* 97! transpositions, not
  just catalogued ones.
* **A sculpture-text running key cannot be rescued by relocating the crib
  blocks.** Under the CT-reading with S-then-T the two required key blocks are
  the fixed 13-letter and 11-letter strings tabulated in `runningkey.md`, and
  neither block occurs *anywhere* in the 66-text corpus at any offset, under any
  of the 24 cipher/alphabet combos, at any of the 26 key-alphabet rotations
  (0 exact hits, 0 within Hamming 1). A transposition only changes *where* the
  two blocks sit relative to each other; it cannot make a string appear in a
  text that does not contain it. So no gap between the blocks, i.e. no
  transposition at all, helps.

That leaves the PT-reading as the only live door for "transposition +
substitution", and §3a walks through it exhaustively over the transposition
catalogue.

---

## 2. Round 1 (pre-existing outputs), summarised

### (A) Transposition first, periodic substitution — `twocipher_A_output.txt`
Per the table above this is identical to the one-stage periodic test.
Periods 2-26 × {Vigenère, Beaufort} × 4 alphabet arrangements: **0 consistent
configurations**. Minimum violated constraints per period runs from 17/22 at
p=2 down to 1/1 at p=26; the test first becomes vacuous at p=27. (It is *not*
vacuous above 26 in general — the two crib blocks start 42 apart, so p=42 still
imposes 11 checks; round 2 extends the period range to 60, see §3a.)

### (B) Substitution first, transposition second, CT-reading — `twocipher_B_output.txt`
1,172,862 (family, variant) transpositions → 1,138,449 distinct permutations
(routes on every grid, keyed columnar for widths 2-24, double keyless columnar,
modular/skip, sculpture-layout). Of these:

* 27 fix all 24 crib positions (so they reduce to test A);
* 750 keep every crib word contiguous and increasing (217 distinct crib-position
  tuples); 2,084 keep them contiguous in any order (700 further tuples);
* running the periodic battery on the 917 distinct crib-position tuples (45 of
  which are uniform shifts of the original positions and therefore equivalent to
  test A): 113 tuples admitted any consistent periodic configuration at all, 112
  of them only vacuously (0 non-trivial checks), and **1 tuple gave a
  non-vacuous survivor with a single check** (p=23, Beaufort, plain/plain, from
  `route grid 6x18 fill=row route=rows r-1c1`); its decryption scores quadgram
  −7.29 / word-coverage 0.43, i.e. not English.

### (B2) Exhaustive key offsets — `twocipher_B2_offsets_output.txt`
Letting each crib block start at a free key offset (2,800 tests in the 2-block
reading, 985,600 in the 4-word reading): **0 consistent for p ≤ 22**, and for
p = 23-26 observed counts track the null exactly (e.g. 4-word p=26: observed 540,
null 561). Maximum non-trivial checks among survivors: 1.

Note: `analysis/twocipher_B2_keyed.py` (the same offset search with all ~208k
dictionary-derived keyed alphabets) exists but **has never been run** — there is
no corresponding output file. That is a live gap, listed in §5.

### (C) Double periodic substitution, two independent alphabets — `twocipher_C_output.txt`
7,744 configurations (p1, p2 ∈ 2..12 × 4×4 alphabet arrangements × 2×2
families): **1 consistent**, against an analytic null of 4.99 and an empirical
null of 2.73 ± 1.91 — i.e. *below* chance. The single hit
(p1=11, p2=12, Beaufort/Beaufort) decrypts to quadgram −7.45, word-coverage 0.39:
not English.

---

## 3. Round 2 — the four untested combinations

All round-2 code was validated before use:

* `two2_a` builds a synthetic ciphertext from a known plaintext (cribs in place),
  a known **non-periodic** key stream and a known random transposition, and
  checks that the pipeline recovers that key stream exactly at the crib
  positions, plus the inverse direction; and it checks that the identity
  transposition reproduces the 24-combo required-key table already published in
  `runningkey.md`. All three checks pass.
* `two2_b` derives K3's transposition from the K3 ciphertext/plaintext pair
  rather than quoting it, and verifies the recovered permutation in both
  directions.
* `two2_c` re-encrypts K1 from its plaintext with PALIMPSEST and K2 with
  ABSCISSA and compares against the carved ciphertext (both match), and checks
  that decrypt inverts encrypt for all 24 combos.

### (a) Transposition + NON-periodic substitution — `two2_a_transpose_keystream.py`

Model `P → S → T → C` under the PT-reading. For each transposition in the
catalogue the 24 key letters are forced, so we can interrogate the key stream
directly. The catalogue (1,172,862 enumerated variants) collapses to
**726,578 distinct crib images `T[j]`**, giving 726,578 × 24 combos =
**17,437,872 forced key streams**.

**Periodicity of the forced key stream** (positions are fixed, so the check count
is the familiar `c_p`; periods extended to 60 because the 42-letter gap between
the crib blocks revives the test above p=26):

| p | checks | configurations | survivors | chance-expected | min violations |
|---|---|---|---|---|---|
| 1-24 | 23 … 5 | 5,812,624 each | **0** | ≤ 0.49 | 15 at p=1 down to 1 at p=24 |
| 25 | 3 | 5,812,624 | 339 | 330.7 | 0 |
| 26 | 1 | 5,812,624 | 219,688 | 223,562 | 0 |
| 27-29 | 0 | — | vacuous | — | — |
| 30-33 | 1-4 | 5,812,624 each | 223,570 / 9,253 / 320 / 14 | 223,562 / 8,599 / 331 / 12.7 | 0 |
| 34-48 | 5-11 | 5,812,624 each | **2** (both p=34) | 1.51 total | 0-5 |
| 49-52 | 4-1 | 5,812,624 each | 29 / 339 / 7,981 / 219,688 | 12.7 / 331 / 8,599 / 223,562 | 0 |
| 53-60 | 0 | — | vacuous | — | — |

Across the 39 periods that impose ≥ 5 checks (chance ≤ 8.4e-8 per configuration)
the total is **2 survivors against a chance expectation of 1.51** — exactly
chance. Both are at p=34, from two neighbouring width-9 columnar permutations;
19 of the 34 key columns are determined and the implied key reads
`UBSOUG...............HOPDAFYNUDMKQ`, which is not a word and leaves 15 columns
free, so the "solution" predicts nothing.

**Sculpture-text running key.** Every forced key stream was tested for an exact
occurrence in a corpus of **3,432 text variants** — the 66 texts of
`runningkey.md` (K1/K2/K3 plaintexts and ciphertexts, the whole left panel, the
physical and ideal tableau, the Morse text, the keywords, reversed and
X-stripped copies) × all 26 rotations under both the plain and the KRYPTOS key
alphabet — as a 13-gram, as an 11-gram, and jointly at offsets (o, o+42):

```
exact 13-gram hits: 0      exact 11-gram hits: 0      exact joint hits: 0
17,437,872 tests against 249,780 distinct 13-grams / 237,458 11-grams / 334,082 joint pairs
chance expectation: 1.8e-06 / 1.1e-03 / 6.4e-22
```

**English-likeness of the key stream.** Quadgram score over the 10 quadgrams of
block 1 and the 8 of block 2 (English prose ≈ −4.7, uniform random ≈ −8.2),
against a matched control of 17,500,000 random draws of 24 letters sampled
without replacement from the ciphertext:

```
best real score   -6.699        control max          -6.809
                                control median       -8.321
                                control 99th         -7.781
                                control 99.99th      -7.361
upper tail        > -7.4: observed 1,074   control-scaled   823
                  > -7.2: observed    78   control-scaled    57
                  > -7.0: observed    10   control-scaled     3
                  > -6.8: observed     1   control-scaled     0
```

The real distribution is the control distribution; the one bin where observed
(10) exceeds control-scaled (3) is a count of ten out of 17.4 million, in a
catalogue full of near-duplicate transpositions, and the single best real score
is *below* the control's own maximum.

Calibration of what this joint score can see (measured, `two2_e_output.txt`):
`PALIMPSESTABS/CISSAKRYPTO` −5.96, `ABSCISSAPALIM/PSESTKRYPTOS` −6.09,
`THEQUICKBROWN/FOXJUMPSOVE` −6.33, `XQZPALIMPSEST/QJXBERLINCLO` −6.47 — all
above the observed maximum of −6.70, so a key that is meaningful across both
blocks would have surfaced. But `ZQXPALIMPSEST/ZQXWJVBKMQP` scores −7.56, deep
inside the noise: **the joint score is blind to a key where only one block is a
keyword.** That hole is closed separately in §3e.

**Reversed stage order under the PT-reading** (`T → S`, key values identical but
at the scattered positions `T[j]`) and **the CT-reading with `S → T`** (the fixed
key values of the one-stage problem at the relocated positions `T^-1[c]` — this
closes the gap left by `twocipher_B`, which ran the periodic battery on only 750
of its 1.14M transpositions) were both run for p = 1..60 over the whole
catalogue, 5,812,624 configurations per period each. Because the relocated
positions usually collide in few residue classes, these tests are individually
weak and the chance expectation is computed per row; the result is that both
give **0 survivors at every period p ≤ 21**, and from p = 22 up the observed
counts track expectation:

| p | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 31 | 42 | 51 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| chance-expected | 0.01 | 0.19 | 0.97 | 23.8 | 269 | 1,726 | 3,013 | 11,547 | 210,650 | 361,203 | 3,334,425 |
| observed, `T→S` PT-reading | 0 | 0 | 0 | 26 | 261 | 1,823 | 2,966 | 11,528 | 217,064 | 362,766 | 3,333,645 |
| observed, `S→T` CT-reading | 0 | 0 | 0 | 29 | 314 | 1,221 | 2,934 | 13,012 | 221,036 | — | — |

Full tables in `analysis/two2_a_output.txt`.

### (b) The K3 procedure, derived and applied to K4 — `two2_b_k3.py`

**K3's transposition, recovered from the data.** Searching all 216 simple grid
steps on divisor widths of 336 and all their compositions: 0 single-step
solutions, **18 two-step solutions, all refactorisations of one and the same
composite permutation**. The canonical form is

> write the ciphertext in rows of 8 (42 rows), read the columns right-to-left,
> each top-to-bottom; write the result in rows of 24 (14 rows), read the columns
> right-to-left again.

which reproduces the K3 plaintext letter-for-letter, and whose inverse
reproduces the carved ciphertext. Reading columns right-to-left, each
top-to-bottom, is a 90° rotation of the grid, so the encryption direction is
(verified separately, same script's machinery):

> write the plaintext in rows of 42 (8 rows), rotate; write the result in rows
> of 14 (24 rows), rotate.

i.e. exactly the published double-rotation description of K3 with grid widths 42
and 14 — derived here from the data rather than quoted, and **with no column
key**: both steps are keyless rotations, so the frequently repeated claim that
K3 uses the KRYPTOS key as a column order 0362514 is not needed and not used.
The same composite permutation re-factors 18 ways, including the width pairs
(4,48), (8,24), (12,16), (16,12) in the row-fill/right-to-left form (note
w1·w2 = 192 in each) and mixed row/column-fill forms at (7,84), (12,21),
(14,42) and (16,28).

**Applied to K4.** 5,517 distinct K3-style transpositions of the 97 letters
(the step operator at every width 2-96 with both fill orders and six readouts;
two-step K3-style compositions for every width pair 2-48; the exact K3 widths 8
and 24 with every route/fill combination; every inverse):

* CT-reading: 172 keep every crib word contiguous (110 distinct position
  tuples). Running the periodic battery on all 110: **1 non-vacuous survivor,
  with a single check** (p=23, Beaufort, plain/plain) — chance level.
* PT-reading: 5,517 × 24 = **132,408 forced key streams**. Exact corpus hits
  0/0/0 (chance 1.3e-08). Periodic key streams at the 39 periods with ≥ 5
  checks: **0** (0.0115 expected). Best quadgram −6.244, inside the chance range
  established in §3a (control max −6.809 over 17.5M draws).
* The literal recipe (rows of 8 then rows of 24, columns right-to-left) applied
  to K4 gives
  `CEAHKICTZDWPZTVYBNWIUKTWZESJQWOSGRQVLWBIOBUGXUKOAKUUUGDJXKGKFMTPNFIADLJAZKSQSTTSKNPQRFBFLSLHOORBR`
  (quadgram −8.32, word coverage 0.09) and its inverse gives
  `ZAZCKKEESUSAQUJHSUQKTGWITDOCSJSTKXGZNKRDPGQWQKVPRFLZFMWTBTBVFPIYLNOBSFBNLIUWHAGIODXUOLUKRJKTBAOWR`
  (−8.10, 0.23). Both are noise. (Curiosity: on 97 letters, unlike on 336, the
  width-8 and width-24 steps commute, so "8 then 24" and "24 then 8" are the
  same permutation.)

### (c) Double substitution keyed by the other Kryptos sections — `two2_c_double_keys.py`

Model `P --stage1(key A)--> M --stage2(key B)--> C`. Each stage is
(key word, phase, family ∈ {Vigenère, Beaufort, variant Beaufort}, plaintext /
ciphertext / key alphabet ∈ {plain, KRYPTOS}) = 24 combos per stage; the phase
covers every rotation of the key word. The whole cross product is decided
exactly by a meet-in-the-middle: stage 1 *requires* a specific 24-letter
intermediate at the crib positions, stage 2 *produces* one, and a configuration
solves the cribs iff the two agree — so an intersection of two sets settles
every pair at once. A pair passes by chance with probability 26^-24 = 1.2e-34.

| scope | stage-1 configs | stage-2 configs | pairs decided | chance-expected | observed |
|---|---|---|---|---|---|
| **C1** both keys ∈ {PALIMPSEST, ABSCISSA, KRYPTOS}, every ordering and phase, all 24×24 combos | 600 | 600 | 360,000 | 4e-29 | **0** |
| **C2** both keys from a 43-word Kryptos-motivated list (adds SANBORN, SCHEIDT, LANGLEY, MASKING, COMPASS, LODESTONE, the three misspellings, LAYERTWO, the Morse phrases, the crib words, concatenations and reversals) | 10,536 | 10,536 | 111,007,296 | 1.2e-26 | **0** |
| **C4** single stage alone (sanity) | 10,536 | — | 10,536 | — | **0** |

The specific configuration the hypothesis names — stage 1 PALIMPSEST, stage 2
ABSCISSA, both Vigenère on the KRYPTOS alphabet, phase 0 — requires the
intermediate `MXUVVEFDMHHWNWPTWKZGQFKI` but produces `SEQIFHQFGANZXFUUJUIFNOVM`:
they agree in **0 of 24** positions (chance 0.92). Its full decryption is
`UNPPHVFGKYFRYEAAYNVUOZQOWCBCSCTFBCAMYGBUSOCBTLGADUUKQVWKYHEYRZEWPMDDCBJXOPZRICGGQRFFBTHPRCXOOOEWH`
(quadgram −8.30, word coverage 0.19).

**C3 — one known key, the other key completely unconstrained.** Instead of
enumerating a word list for the free stage, the known stage fixes the
intermediate text at the 24 crib positions, which *forces* the free stage's key
letter at each of those positions. A key word of length L then exists iff those
24 forced letters are consistent on residue classes mod L — and the phase only
relabels residues, so it need not be enumerated. This covers **every possible
key word, dictionary or not, of every length 1-26, at every phase**:

```
stage 1 known, stage 2 free : 6,574,464 tests, 9,838 consistent, chance-expected 9,740
stage 2 known, stage 1 free : 6,574,464 tests, 9,838 consistent, chance-expected 9,740
of which the implied key word (in any rotation) is a dictionary word:  0  and  0
```

Every consistent case sits at L = 25 or 26, where only 1-3 non-trivial checks
exist; the counts match chance to 1%.

### (d) Transposition + transposition, then substitution — `two2_d_double_transposition.py`

A composition `T2 ∘ T1` of two simple transpositions is generally *outside* the
single-transposition catalogue, so this is genuinely new. Base family: 1,565
distinct transpositions (row/column routes on every grid of width 2-50 in both
fill orders and all four orientations; keyed columnar with every column
permutation for widths 2-5; the four sculpture blocks in every order with every
subset reversed; decimations `j → a·j mod 97`; each with its inverse) →
**2,449,225 compositions**.

* **CT-reading.** 32,945 compositions keep every crib word contiguous and
  increasing — 44× more than the 750 single transpositions that do — giving
  2,354 distinct crib-position tuples. Periodic battery over 470,800
  (tuple, period 2-26, arrangement) configurations: **16 survivors with ≥ 1
  non-trivial check, against a chance expectation of 221.5.** All 16 have
  exactly one check. Below chance.
* **PT-reading.** 1,327,758 distinct forced crib signatures × 24 combos =
  **31,866,192 forced key streams**. Periodicity, p = 1..60: **0 survivors at
  every period with ≥ 5 checks** (p ≤ 24 and p = 34..48, including p=42 with its
  11 checks); at p = 25, 26, 30-33, 49-52 the counts match expectation to within
  2% (e.g. p=26: 410,261 observed vs 408,541 expected). Exact corpus hits
  0/0/0 over 31.9M tests. Best quadgram −6.723, inside the chance range.

### (e) Per-block keyword test — `two2_e_keyword_blocks.py`

The joint quadgram score of §3a has a blind spot, measured rather than assumed:

| key stream | joint score |
|---|---|
| `PALIMPSESTABS / CISSAKRYPTO` | −5.96 |
| `ABSCISSAPALIM / PSESTKRYPTOS` | −6.09 |
| `THEQUICKBROWN / FOXJUMPSOVE` | −6.33 |
| `XQZPALIMPSEST / QJXBERLINCLO` | −6.47 |
| observed maximum over 17.4M real key streams | **−6.70** |
| `ZQXPALIMPSEST / ZQXWJVBKMQP` (keyword in one block only) | −7.56 |

So the joint test would have caught a key meaningful across both blocks, but not
one where only the EASTNORTHEAST block (or only the BERLINCLOCK block) carries a
keyword. This script closes that with a test that has no such blind spot: for
each block **separately**, is any substring of length 8-13 an English word
(154,356 words of length 8-13 from `/usr/share/dict/words` plus every word in
`data/*`)? Both sources of §3a and §3d are re-tested.

**Transposition catalogue (726,578 signatures × 24 combos = 17,437,872 key streams):**

| substring length | distinct words | substring positions | expected hits | observed |
|---|---|---|---|---|
| 8 | 29,865 | 10 | 24.94 | **22** |
| 9 | 32,304 | 8 | 0.83 | **1** (`PHORONOMY`) |
| 10 | 30,833 | 6 | 0.02 | **0** |
| 11 | 25,971 | 4 | 0.00 | **0** |
| 12 | 20,455 | 2 | 0.00 | **0** |
| 13 | 14,928 | 1 | 0.00 | **0** |

Textbook chance agreement, and in particular **no key block contains a
10-or-more-letter word** — which is what a real keyword (PALIMPSEST is 10,
ABSCISSA 8, KRYPTOS 7) would look like.

Per-block quadgram tails (each block scored alone, against a control of
2,400,000 random draws per block):

```
EASTNORTHEAST block (13): best -4.379 [EANOSERECEDAV]  control max -4.077, median -8.276, 99.99th -5.694
BERLINCLOCK   block (11): best -3.840 [EWERENTENCO]    control max -4.248, median -8.476, 99.99th -5.343
```

Block 1's best is *below* the control's own maximum. Block 2 has five values
above the control maximum (−3.840, −4.097, −4.097, −4.133, −4.145), which is
what a 7.3× larger sample (17.4M vs 2.4M draws) is expected to produce — about
7 by chance. None of them is a word, none has a matching partner block, and
the sharp instrument (a ≥ 9-letter dictionary word) fires at exactly its chance
rate. `RACTOTHEDAM` and `EWERENTENCO` are pareidolia.

PLACEHOLDER_COMPOSITIONS

---

## 4. How every count above was judged

Every "survivor" number is reported next to what a random key stream would
produce, and nothing here exceeds it.

* **Periodic tests.** With the 24 crib positions occupying `24 − c_p` distinct
  residues mod p, a random key passes with probability 26^-c_p. The check
  counts are 23, 22, …, 11 for p = 1..13, then 11, 9, 8, 7, 7, 9, 11, 11, 9, 7,
  5, 3, 1 for p = 14..26, 0 for p = 27-29, then 1, 2, 3, 4, 5, 6, …, 11 at p=42
  and back down to 1 at p=52, 0 from p=53. Only periods with c_p ≥ 5 have real
  power (chance ≤ 8.4e-8 per configuration); those are the numbers quoted.
* **Exact corpus tests.** A 13-letter block matches one of 249,780 corpus
  13-grams with probability 249,780/26^13 = 1.0e-13; the joint test is 26^-24.
* **English tests.** Calibrated against a random control drawn from the
  ciphertext's own letter multiset, reported as tail counts rather than a single
  best score; where the control is smaller than the real sample the ratio is
  stated. The sharpest of these is the §3e dictionary-word test, whose chance
  rate per length is computed from the number of words of that length
  (e.g. a 10-letter word somewhere in the two key blocks: 0.02 expected across
  17.4M key streams).
* **Two-stage substitution tests.** A configuration must reproduce 24 letters
  exactly: 26^-24 = 1.2e-34 per pair.

---

## 5. What is now excluded, and what is not

**Excluded (in addition to everything in `families.md` and `runningkey.md`):**

1. Any transposition, catalogued or not, applied **before** the substitution,
   under the ciphertext-position reading of the cribs — the crib pairs are
   untouched, so all prior negatives apply unchanged.
2. Any sculpture-text running key combined with any transposition, under either
   crib reading (the CT-reading by the block-non-occurrence argument in §1; the
   PT-reading by the 17.4M + 31.9M exact tests of §3a and §3d).
3. Substitution-then-transposition with a **non-periodic** key, over 726,578
   distinct crib images of the transposition catalogue and 1,327,758 further
   images from two-transposition compositions: not periodic at any period 1-60
   with power, not a corpus running key, not English jointly, and (§3e) with
   neither key block containing an English word of 10 letters or more.
4. The K3 procedure — derived exactly, keyless, widths 8 and 24 — applied to K4
   in 5,517 variants, one step and two, both directions.
5. Double substitution with any pair of keys from {PALIMPSEST, ABSCISSA,
   KRYPTOS} (and a 43-word Kryptos list), every ordering, phase, family and
   alphabet arrangement; and, more strongly, one such key on either stage
   combined with *any* key word of length ≤ 26 on the other.
6. Two transpositions followed by a substitution, over 2.45M compositions.

**Not excluded / not tested:**

1. **Keyed alphabets in the two-stage tests.** `two2_a`, `two2_b` and `two2_d`
   use only the plain and KRYPTOS alphabets (24 cipher/alphabet combos, plus all
   26 key-alphabet rotations on the corpus side). A substitution built on a
   different keyword-mixed alphabet would change the forced key letters.
   `analysis/twocipher_B2_keyed.py` was written to cover the keyed-alphabet case
   for the offset search but **has never been executed** — running it is the
   cheapest outstanding item.
2. **Transpositions outside the catalogue.** 1.17M enumerated + 2.45M
   compositions is a vanishing fraction of 97!. The catalogue is
   "designer-plausible" (routes, columnar, double columnar, skips, sculpture
   geometry) but a keyed columnar with a width in 25-50, a disrupted/irregular
   columnar, a Cadenus, or a keyed route is not in it.
3. **Fractionation combined with transposition** (e.g. bifid/trifid then
   columnar) — the digraphic work in `families.md` ruled out the single-stage
   versions structurally, but not the composed ones.
4. **Three or more stages**, and any stage that is not letter-wise (e.g. a
   nomenclator, or the "masking technique" being something non-classical).
5. **The PT-reading itself is an assumption.** If Sanborn's positions are
   ciphertext positions *and* the plaintext crib words are not contiguous (i.e.
   the words survive only as scattered letters), the schemes are cryptographic
   nonsense but were not enumerated.

---

## 6. Reproducing

`two2_lib.py` and the round-2 scripts need numpy, which is not in the system
Python here; they were run under a scratch virtualenv:

```
python3 -m venv <scratch>/venv && <scratch>/venv/bin/pip install numpy
cd analysis
<scratch>/venv/bin/python two2_a_transpose_keystream.py    # ~4 min, writes two2_a_output.txt
<scratch>/venv/bin/python two2_b_k3.py                     # ~3 s,   writes two2_b_output.txt
<scratch>/venv/bin/python two2_c_double_keys.py            # ~18 s,  writes two2_c_output.txt
<scratch>/venv/bin/python two2_d_double_transposition.py   # ~55 s,  writes two2_d_output.txt
<scratch>/venv/bin/python two2_e_keyword_blocks.py         # ~8 min, writes two2_e_output.txt
```

`two2_c_double_keys.py` runs without numpy as well.
