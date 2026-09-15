# K4 — panel geometry: rearrangements, the whole left panel, lag 7, and the number 97

Scripts: `analysis/geo2_common.py`, `geo2_a_readorders.py`, `geo2_b_panel.py`, `geo2_c_lag7.py`,
`geo2_d_97.py`, `geo2_validate.py`, plus the repaired `analysis/geometry_4_rearrangements.py`.
Raw output: `findings/geo2_a_out.txt`, `geo2_b_out.txt`, `geo2_c_out.txt`, `geo2_d_out.txt`,
`geo2_validate_out.txt`, `geometry_4_out.txt`.

**Bottom line: nothing survives. No physical reading order of the 4+31+31+31 panel block, no
key positioned in the full 869-character left panel, no period-7 structure and no 31- or
93-based structure fits the 24 Sanborn cribs. The lag-7 autocorrelation spike is multiple-testing
noise (corrected p = 0.15–0.47). Two genuinely new, alphabet-independent impossibility results
came out of the work and are recorded in §5.**

---

## 0. Verification of the machinery (`geo2_validate.py`, all PASS)

Every negative below rests on one routine, so it was checked five ways:

| check | result |
|---|---|
| V1 encrypt/decrypt round trip, 3 ciphers x 4 alphabet pairings x 200 random texts | 0 failures |
| V2 plant a known period-p key on the real crib positions (p = 3,7,10,13,17,26,31), recover it | 0 failures — key and decrypt exact |
| V3 same, planted **through a reading order** (column-major of the grid), to exercise the permutation + crib-remap path | 0 failures |
| V4 general-polyalphabetic test never rejects a genuine period-p polyalphabetic (p = 2..31) | 0 false rejections; p=7 conflict count also hand-enumerated and matches |
| V5 empirical null: crib plaintexts replaced by random letters | measured consistency rate matches 26^-c to 2 significant figures at every period checked |

V5 matters for reading the tables: for a period whose crib positions collide `c` times, a random
key passes the consistency test with probability 26^-c, and that figure is empirically correct.
Where observed survivor counts fall *below* the chance expectation (they often do), that deficit
is **not** evidence of anything — the real crib shifts are fixed, not random.

---

## 1. The repaired `geometry_4_rearrangements.py`

**Bug.** `apply()` inverted the permutation with `inv[pos-1]` for all 24 cribs, but three of the
4,703 "rearrangements" (`identity`, `odd positions only`, `even positions only`) are *subsets* of
the 97 positions, not permutations, so `inv` had no entry for the dropped crib letters →
`KeyError: 21`. Fixed by dropping cribs whose letter is not present and renumbering the rest
(11 cribs survive the odd split, 13 the even split). The script now runs to completion.

**Result (2,652,492 tests: 4,703 rearrangements x periods 2–48 x 12 pairings).**

| #crib collisions c | tests | expected consistent by chance | observed consistent |
|---|---|---|---|
| 0 (vacuous) | 467,592 | 467,592 | 467,592 |
| 1 | 133,908 | 5,150 | 3,172 |
| 2 | 153,144 | 227 | 144 |
| 3 | 149,844 | 8.5 | **0** |
| >= 4 | 1,748,004 | < 0.4 | **0** |

Nothing above the chance rate; nothing at all once a period imposes three or more real
constraints. The periodic-IoC maxima reported at p = 25–30 in that file (0.10–0.12) are artefacts
of 2–4-letter columns, not signal — see §2.

---

## 2. (a) Every plausible physical reading order — `geo2_a_readorders.py`

**274 reading orders** of the sculpture's 4+31+31+31 block (row 1 = OBKR at columns 28–31 after
the `?`; rows 2–4 = 31 letters each):

* row-major in 4 directions; boustrophedon by row, 2 phases x 2 vertical senses;
* column-major in 4 directions; boustrophedon by column, 2 phases x 2 senses;
* both diagonal families (constant r+c and constant r−c), 2 diagonal orders x 2 within-diagonal
  senses = 8;
* spirals inward and outward from each of the 4 corners in both rotational senses = 16;
* the three 31-letter rows in all 6 orders with each row independently forward/reversed (48),
  crossed with 4 placements of OBKR (front / front-reversed / end / dropped) = **192**;
* the 93-letter body alone under all of the geometric orders above; identity; whole-text reversal.

Sanity checks in the output confirm the identity order reproduces the ciphertext and the cribs,
and that the body-only order reproduces `CT[5..97]` with the cribs shifted by 4.

### Crib consistency (82,200 tests: 274 orders x p = 2..26 x 12 pairings)

* **Expected consistent by chance: 141.0. Observed: 104.**
* All 104 are at c = 0 (96 cases, vacuous) or c = 1 (8 cases, chance 1/26 each; 43 expected).
* **Consistent cases with >= 3 real constraints: NONE.**
* Ranking all consistent cases by the English-likeness of the newly revealed (non-crib) letters
  gives a best unigram log-prob of **−3.504** against −2.90 for English and about −3.4 for a
  shuffle of K4's own letter pool. The best decrypts contain no English words. They are noise.

### Periodic IoC

The correct null is a random permutation of K4's *own* 97 letters (a transposition preserves the
multiset). 4,000 shuffles per period give 95th percentiles of 0.041 (p=2) rising to 0.053 (p=12).
Restricting to p <= 12, where columns still hold >= 8 letters:

* **74 of 2,046 (order, period) pairs exceed the 95th-percentile null; 102 are expected.**

Below chance. The IoC gives no reason to prefer any reading order. (This also explains the
`geometry_4` p = 25–30 maxima: at p = 28 a 97-letter text has columns of 3–4 letters, where a
single accidental repeat forces IoC to 0.10+.)

---

## 3. (b) A key positioned in the whole left panel — `geo2_b_panel.py`

Panel layout verified from the transcription: **869 characters = 865 letters + four `?`**.
K1 ciphertext at panel letters 0–62, K2 at 63–431, K3 at 432–767, **K4 at 768–864** (or 772–868
counting the `?`s). Regression checks in the output re-derive PALIMPSEST (period 10) from K1 and
ABSCISSA (period 8) from K2 under vigenere/KRYPTOS/KRYPTOS, confirming the alignment.

### 3.1 The phase question is closed, and it is closed a priori

The periodic crib test asks only **which crib positions share a residue class mod p**. Adding a
constant offset to every position is a bijection on Z_p, so the partition — and therefore the
verdict — cannot change. Verified exhaustively: for p = 2..60 and every offset 0..868, all
**51,271** induced partitions are identical to the offset-0 partition, and 0 consistency verdicts
differ.

> **Consequence.** Every periodic-key negative already obtained on K4-relative positions applies
> verbatim to absolute panel positions. In particular *every repeating keyword of length <= 60,
> at every one of the 869 possible panel alignments, is already ruled out* — including
> PALIMPSEST and ABSCISSA themselves. The same argument closes the analogous loophole for the
> polynomial shift models of `geometry_1`: the families `a*i+b`, `a*i^2+b*i+c`, `a*i^3+...` are
> closed under `i -> i + 772`, so re-running them on absolute panel indices is the same search.

### 3.2 The constraint table, p = 2..97

`c` = number of crib collisions; `cons` = how many of the 12 pairings are consistent.

```
 p: c cons |  p: c cons |  p: c cons |  p: c cons
 2:22   0  | 14:11   0  | 26: 1   0  | 38: 9   0
 3:21   0  | 15: 9   0  | 27: 0  12  | 39:10   0
 4:20   0  | 16: 8   0  | 28: 0  12  | 40:11   0
 5:19   0  | 17: 7   0  | 29: 0  12  | 41:11   0
 6:18   0  | 18: 7   0  | 30: 1   0  | 42:11   0
 7:17   0  | 19: 9   0  | 31: 2   0  | 43:10   0
 8:16   0  | 20:11   0  | 32: 3   0  | 44: 9   0
 9:15   0  | 21:11   0  | 33: 4   0  | 45: 8   0
10:14   0  | 22: 9   0  | 34: 5   0  | 46: 7   0
11:13   0  | 23: 7   0  | 35: 6   0  | 47: 6   0
12:12   0  | 24: 5   0  | 36: 7   0  | 48: 5   0
13:11   0  | 25: 3   0  | 37: 8   0  | 49: 4   0
      ... 50:3, 51:2, 52:1 all cons=0; every p in 53..97 has c=0 (vacuous, 12/12).
```

* **Periods with >= 1 real constraint AND >= 1 consistent pairing: NONE, for all p = 2..97.**
* Over all constrained periods: 1.42 consistent pairings expected by chance, **0 observed**.
* Periods **27, 28, 29 and every p >= 53 impose no constraint at all** — the cribs cannot test
  them, and a "survivor" there is meaningless. This is the honest boundary of the periodic search.

### 3.3 The decisive new test: K1 and K2 *determine* a panel-wide positional key

K1 and K2 supply **424 (ciphertext, plaintext) pairs at known absolute panel positions** (K1's 63
letters plus K2's first 361, before the known carving error). If one key were indexed by absolute
panel position, those 424 pairs fix it and K4 becomes a **prediction, not a fit**.

| test | result |
|---|---|
| uniform width w = 2..500 over the 865 panel letters, 12 pairings (5,988 cases) | 924 are self-consistent on K1+K2, and all 924 make predictions about K4 |
| ... cases predicting **all 24** cribs correctly | **0** |
| ... best case | w=430, vig/plain/kryptos: 24 predictions, **4 correct** (chance 0.92) |
| ... aggregate accuracy | 811 correct of 22,176 predictions = **0.037**, versus 1/26 = 0.038 |
| same with the four `?` counted as positions (869 slots) | 888 self-consistent, 0 predicting all 24, aggregate 0.036 |

The 924 self-consistent cases are exactly **w >= 424**: below that no single width can reconcile
PALIMPSEST at period 10 from panel position 0 with ABSCISSA at period 8 from panel position 63.
That is the structural reason the panel carries no global positional key — and it is confirmed
independently by the physical geometry:

* **Per-physical-column key** (the panel's real ragged rows, widths 29–33, so 33 columns):
  self-consistent for **0 of 12** pairings — 369 of the 424 K1/K2 letters conflict with an
  earlier letter in their own physical column.
* **Per-physical-row key** (28 rows): 0 of 12 self-consistent, and in any case K4 occupies rows
  24–27, which contain no K1/K2 letters, so it could never predict anything.
* **shift = a*row + b*col + d on the physical panel geometry** (family 26^3 x 12 = 210,912
  models; enumerated as 8,112 (a,b) cases with d forced by the first crib, which cannot miss an
  all-24 fit): best fit **7 of 24**, 0 fitting all 24, and chance predicts a best of ~7
  (expected 1.5 models at >= 7).
* **Continuing K1's/K2's own keys into K4** — PALIMPSEST, ABSCISSA, KRYPTOS and the two
  concatenations, anchored at panel letter 0, panel char 0, K4 letter 0, K3 start and K2 start,
  in both key alphabets, under all 12 pairings (600 combinations): best **4 of 24** cribs, against
  a chance mean of 0.92 and P(>=5) = 0.19%.

---

## 4. (c) The lag-7 autocorrelation spike — `geo2_c_lag7.py`

Observed: 9 coincidences in 90 pairs at lag 7, z = **+3.036**, the maximum over all 96 lags.

### It does not survive multiple testing

200,000 Monte Carlo trials of the **maximum** z over a lag range, under two nulls:

| lag range searched | uniform-random null: p | K4-letter-shuffle null: p |
|---|---|---|
| 1..96 (what was actually searched) | **0.557** | **0.473** |
| 1..48 | 0.218 | 0.149 |
| 1..30 | 0.137 | 0.087 |
| lag 7 alone, pre-specified | 0.0076 | 0.0048 |

The null distribution of max-z over 96 lags has mean +3.1 to +3.3 — **the observed +3.04 is below
the average maximum of a random string.** The spike is exactly what scanning 96 lags produces.
It is not evidence. (The 95th percentile of that maximum is +5.0; a real signal would have to
reach roughly there.)

The 9 coincident pairs are (1,8,O) (8,15,O) (13,20,B) (16,23,L) (33,40,S) (46,53,K) (66,73,P)
(77,84,D) (87,94,K) — spread evenly over the text (5 in the first half, 4 in the second; 6 of
them between two non-crib positions) and spread evenly over the residues mod 7, i.e. showing no
internal structure of their own.

### The doubled letters mod 7 — also noise

The six doubled letters start at 19, 26, 33, 43, 47, 68, and **five of the six are ≡ 5 (mod 7)**
(19, 26, 33, 47, 68). The naive p-value for that is 0.0012 — but modulus 7 was chosen *after*
seeing the lag-7 spike. Correcting honestly (200,000 trials of 6 uniform positions in 1..96,
asking whether *any* modulus 2..48 collects >= 5 of them):

* **P = 0.247.** Not significant.

### What a period-7 structure would have to be, and why it cannot exist

* **Additive period-7 key** (Vigenère / Beaufort / variant-Beaufort, either alphabet on either
  side): the 24 cribs occupy only 7 residues, so 17 constraints; all 12 pairings are inconsistent,
  and every one of the 7 residues is individually conflicted (vig/plain/plain needs residue 0 to
  be simultaneously 1, 12, 14 and 24). Chance of passing would be 26^-17 = 9e-25.
* **General period-7 polyalphabetic** — see §5. Also impossible, for *any* seven alphabets.

So even if the lag-7 signal had been real, no period-7 key could explain it. Taken together with
the p = 0.47 correction, **lag 7 should be retired as a lead.**

---

## 5. Two new alphabet-independent impossibility results

Both come from a test that had not been run: a **general periodic polyalphabetic**, in which each
of the p key slots carries its own *arbitrary, independent* mixed alphabet. This is strictly more
general than Quagmire I–IV (which force all p alphabets to be rotations of one mixed alphabet) and
than any additive key. The only crib constraint is that within each residue class the ct -> pt map
must be a **partial bijection**. A period that fails this is impossible **for every alphabet set
that exists**, not merely for keyword-mixed ones.

**Result A — on the ciphertext as carved (and on the 93-letter body, identically):**

Periods **2, 3, 4, 5, 6, 7, 9, 10, 14, 15, 17, 21 and 25 are impossible**, full stop.
Periods 8, 11, 12, 13, 16, 18, 19, 20, 22, 23, 24 and 26+ survive — but surviving is nearly
automatic once p x 26 free parameters face 24 crib letters, so survival is a *necessary condition*,
not evidence.

Worked example at p = 7 (hand-verified in `geo2_validate_out.txt`): residue class 2 contains
`24:R->S 31:G->E 66:P->R 73:P->C` — the same ciphertext P must decrypt to both R and C in the same
key slot; residue class 3 contains `25:V->T 32:K->A 67:V->L 74:K->K`, conflicting twice more.

**Result B — across reading orders:** applying the same test to all 186 full-97 reading orders of
§2 x periods 2..31 (5,580 combinations), **periods 2, 3, 4 and 5 are killed for every single
reading order**, and no period is killed for none. Period 20 is the most permissive (killed for
only 12 of 186 orders), period 9 the most hostile (184 of 186).

---

## 6. (d) What the number 97 could mean — `geo2_d_97.py`

**Arithmetic.** 97 is prime (divisors 1, 97); 93 = 3 x 31; 98 = 2 x 7^2 = 7 x 14; 96 = 2^5 x 3;
869 = 11 x 79; 865 = 5 x 173. Because 97 is prime, *no* grid of the whole of K4 is exact — every
columnar layout has a ragged last row, and there is no square or near-square form. 97 − 4 = 93 =
3 x 31 is the only exact rectangle available, and 31 is the panel width; this is presumably why
the sculpture sets OBKR apart.

**One key value per 31-letter block (4 | 31 | 31 | 31).** Impossible by inspection: block 1 alone
holds 13 crib letters that require 9–13 *distinct* shift values in every pairing. (The broader
family `a*floor(i/m)+b` was already covered in `geometry_1_out.txt`, best fit 8/24.)

**A key of length 31 on the 93-letter body.** The cribs sit at body positions 18–30 and 60–70 and
occupy 22 distinct residues mod 31, so there are exactly **2 constraints**: body 29/60 and 30/61,
i.e. K4 33/64 (`S->S` against `N->B`) and K4 34/65 (`S->T` against `Y->E`) — the S and T that end
NORTHEAST share 31-wide columns with the B and E that begin BERLIN. Both conflict in **all 12 pairings** — but on two constraints only, so the
strength of this particular negative is 26^-2 = 0.0015, suggestive rather than decisive on its own.
The same test on the full 97 (`geometry_3_out.txt`) has 2 constraints and likewise fails 12/12.

**Full body constraint table, p = 2..93.** Periods with >= 1 constraint and >= 1 consistent
pairing: **NONE**. 1.42 consistent pairings expected by chance over all constrained periods, 0
observed. Periods 27, 28, 29 and every p >= 53 are unconstrained (vacuous), exactly as for the
full 97.

**The 3 x 31 body grid in all 8 orientations** (rows forward/reversed x columns forward/reversed x
as-is/transposed) x periods 2..31 x 12 pairings = 2,880 tests: **0 consistent cases with a real
constraint, 1.93 expected by chance.**

**97 ± 1 — a missing or extra carved letter.** K2's carved ciphertext is known to be one letter
short of its plaintext (Sanborn's error), so K4 could be too; that would shift every position after
the gap by one and invalidate every position-based test run to date. Tested by inserting an unknown
letter at each of the 98 slots and by deleting each of the 73 non-crib letters, then re-running
p = 2..31 x 12 pairings:

| variant | constrained tests | expected consistent by chance | observed |
|---|---|---|---|
| insertion at each of 98 slots | 31,392 | 70.4 | **0** |
| deletion of each non-crib letter | 23,652 | 55.9 | **0** |

The special case s = 0 — treating the `?` before OBKR as belonging to K4, which would make it
**98 = 7 x 14 characters, the one reading under which a 7-wide grid is exact and the lag-7 idea
would have a home** — fails cleanly: p = 7 has 17 constraints and 0/12 consistent, p = 14 has 11
constraints and 0/12, p = 49 has 4 constraints and 0/12; and both 7-wide column reads of the
98-cell grid yield no consistent case with a real constraint.

---

## 7. What this closes, and what it does not

**Closed by this work:**

1. All 274 physical reading orders of the sculpture's 4+31+31+31 block, combined with any periodic
   key of period 2–26 in 12 cipher/alphabet pairings — and, via `geometry_4`, 4,703 column-reads
   at every width 2–48 and offset, periods 2–48.
2. The "different phase in the full panel" hypothesis, *a priori* and for all periods and all 869
   alignments — including every repeating keyword up to length 60 and the polynomial shift families.
3. A single positional key across the whole left panel, in three independent forms (uniform width
   2–500, physical column, physical row) plus the linear row/column model, all tested as
   **predictions** from K1+K2's known plaintext rather than as fits.
4. The lag-7 spike (corrected p = 0.47) and the doubled-letters-mod-7 pattern (corrected p = 0.25).
5. All 31-based and 93-based structures, including a 31-length key on the body, per-block keys,
   the 3 x 31 grid in all orientations, and 97 ± 1 with a missing or extra letter.
6. Periods 2, 3, 4, 5, 6, 7, 9, 10, 14, 15, 17, 21, 25 for *any* polyalphabetic with independent
   arbitrary alphabets; periods 2–5 for any polyalphabetic under any of the 186 reading orders.

**Not closed (honest gaps):**

* Periods 27, 28, 29 and every period >= 53 impose **zero** crib constraints. Nothing in the
  periodic family can be tested there; they must be attacked on decrypted text, not on cribs.
* The general-polyalphabetic test leaves periods 8, 11, 12, 13, 16, 18, 19, 20, 22, 23, 24 and
  26+ alive as necessary conditions. Finding actual alphabets that produce English is a separate,
  much larger search (26!^p) and was not attempted.
* Reading orders combined with *non-periodic* keys (autokey, running key, progressive) were not
  re-run here; the reading-order library in `geo2_a_readorders.py` is the natural input for that.
* Two-stage systems where the transposition is keyed by something other than the panel geometry
  (e.g. a keyword-ordered columnar transposition) are outside the geometric hypothesis and were
  covered only partially in `findings/families.md` §7.
* The `?` characters' status is assumed (they belong to K1/K2/K3); the s=0 insertion test covers
  the one case where the last `?` might belong to K4, but not readings where several do.
