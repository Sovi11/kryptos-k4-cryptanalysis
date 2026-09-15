# K4 — method genealogy, the K5 lever, cross-section phase, the question mark, and OBKR

Line of attack: **exploit structural relationships nobody has mined** — the design progression
K1→K2→K3→K4, the existence of a second 97-character message, the arithmetic of a key running
across section boundaries, the question mark carved immediately before `OBKR`, and `OBKR` itself
as a message indicator.

Written 2026-09-13. Scripts `analysis/k5_lib.py` (shared, self-tested), `k5_a_genealogy.py`,
`k5_b_depth.py`, `k5_c_phase.py`, `k5_d_question.py`, `k5_e_indicator.py`, `k5_f_slidefair.py`.
Raw logs `analysis/k5_a_output.txt`, `k5_b_output.txt`, `k5_c_output.txt`, `k5_d_output.txt`,
`k5_e_output.txt`, `k5_f_output.txt`.

---

## 0. Bottom line

**No decryption. Every sweep sits at or below its chance expectation.** Roughly **51 million**
crib tests across the five tasks; the best crib agreement anywhere is **7 of 24**, against a
chance expectation of 0.92 of 24 per test and a required 24 of 24.

The value is in three results that are not sweeps:

1. **The headline logical finding (task b).** The claim carried in this repository — that K5
   sharing "coded words in the same position" with K4 is evidence the system is **positional** and
   evidence **against autokey** — **does not survive scrutiny**. Under a positional chart the
   ciphertext-sharing reading and the plaintext-sharing reading are the *same statement*
   (proved below), so the inference is affirming the consequent; and a shared run at the head of
   two messages is exactly what autokey with a shared primer produces, so autokey is not excluded
   either. There is **no contradiction** with the repository's negatives, because the repository
   has not ruled out position-indexed systems — it has searched about **3 × 10⁻⁶⁷** of the
   crib-consistent positional key space. §2.

2. **A newly closed cipher family, closed decisively (task a).** A complete census of 1989
   hand ciphers against this repository's record leaves exactly two 26-letter, hand-executable,
   fixed-point-permitting families untested: the ACA **Slidefair** and **Portax**. Slidefair
   carries a **key-free invariant** — the key cancels out of every digraph — so the 24 cribs
   refute it with no key search at all: **2 of 11 required equations, over 384 configurations,
   where a genuine Slidefair satisfies 11 of 11 (chance 26⁻¹¹ = 2.7 × 10⁻¹⁶)**. §1.

3. **A pre-registered, decisive experiment for the day K5 is published**, with its decision rule
   and chance thresholds fixed in advance and its machinery validated on synthetic depth pairs.
   It distinguishes "one shared chart → depth attack, message falls" from "two charts → depth
   worthless" in one string comparison. §2.6.

Tasks (c), (d) and (e) are **closed negatives, three of them by subsumption proofs** that convert
"untested" into "already decided" — a more useful outcome than another sweep, because the proofs
retire whole classes of future proposals.

---

## 1. Task (a) — method genealogy

`analysis/k5_a_genealogy.py` (already on record, log `k5_a_output.txt`) argued the genealogy from
Gromark and from composing K3's route with a key stream. Summary of its results, then the part
that was missing.

### 1.1 What was already done

| test | scale | result |
|---|---|---|
| S0 alphabet-free invariants of the forced key stream | — | **1 forced equality** k₂₈ = k₆₆ (separation 38); **22 forced inequalities** |
| S1 Gromark model G1 (free cipher alphabet, exact over all 26! ) | 14,732,068 primer×alphabet tests | 0 survivors |
| S2 Gromark model G2 (Bean's reading, free single alphabet) | 19,347,878 primers | 0 alphabet-feasible |
| S3 periodic Gromark, base 10 and 26, p = 1–6 | all keys | 0 |
| S4 K3's double rotation applied to the **key stream** | 12,224,976 tests | best 9/24; 0 reaching 12/24 |

The S0 result deserves restating because it is free and alphabet-independent: the *only* equality
the cribs force on any letterwise key stream is `k[28] == k[66]`, separation 38. A periodic key
satisfies it automatically only if its period divides 38 — i.e. p ∈ {1, 2, 19, 38} — and all four
are already dead. Every other candidate key stream in this repository should be checked against it.

### 1.2 What "the next step in the progression" means, argued properly

K1 and K2 are one system (Quagmire III on the KRYPTOS-keyed tableau) with two keywords. K3 is a
keyless route transposition. Scheidt: *"There are four different processes. Two of them are
similar and the other two are different things."* So the genealogy is

```
K1, K2   substitution, key = a word          the solver must find a WORD
K3       transposition, key = none           the solver must find a GEOMETRY
K4       ?                                   the solver must find ???
```

A genealogy argument is only worth anything if it *predicts candidates that are not already in the
ruled-out list*. The disciplined way to do that is a **census**: enumerate every hand cipher a CIA
cryptographer would have had on the shelf in 1989 — essentially the ACA Cipher Exchange canon plus
the field systems — and classify each against the two hard structural facts and against this
repository's record.

* **F1.** K4's ciphertext uses **all 26 letters** (J at 1-indexed 41, 52, 82). Any system whose
  ciphertext alphabet has fewer than 26 symbols is impossible outright.
* **F2.** S→S at 33 and K→K at 74: **a letter can represent itself**, killing every
  reciprocal-without-fixed-points system.

`k5_f_slidefair.py` runs the census. Result: **23 families closed by computation on record,
11 impossible by F1/F2 or the E-count argument, and exactly 2 open** —

| open family | why it survived the filters |
|---|---|
| **Slidefair** (Vigenère / Beaufort / Variant slides) | 26-letter, permits fixed points, pure hand cipher, nowhere in this repository |
| **Portax** | 26-letter, seriated digraphic, **does** permit fixed points (see below), nowhere in this repository |

Both are the ACA's own "next step up from Vigenère". That is what a genealogy argument is supposed
to produce.

### 1.3 Slidefair — refuted by a key-free invariant

Slidefair uses two alphabet rows, the lower slid by the key letter. For a digraph (p₁, p₂):
locate p₁ in the top row, p₂ in the bottom row, and take the other two corners of the rectangle.
In alphabet indices, for the Vigenère slide

```
c1 = p2 − k        c2 = p1 + k        so   c1 + c2 = p1 + p2   (mod 26)
```

and for the Beaufort slide `c1 = k − p2`, `c2 = k − p1`, so `c1 − c2 = p1 − p2`. **The key
cancels.** Every complete crib digraph therefore imposes one equation that holds for *every key,
every period and every phase*; only the alphabet matters.

Eleven complete crib digraphs exist in each of the two digraph alignments:

```
alignment 0 (even):  1-indexed 23 25 27 29 31 33 | 65 67 69 71 73
alignment 1 (odd):   1-indexed 22 24 26 28 30 32 | 64 66 68 70 72
```

A genuine Slidefair satisfies 11 of 11; a random cipher satisfies all 11 with probability
26⁻¹¹ = 2.7 × 10⁻¹⁶.

**Validation first.** The implementation recovers the planted key identically from *both* halves
of every digraph, for all 3 slide variants × 2 alphabets × 48 digraphs — PASS.

**Result.** Over 32 alphabets × 3 slide variants × 2 output orders × 2 alignments = **384
configurations**, the best is **2 of 11** (SCHEIDT-keyed alphabet, Vigenère slide, alignment 0),
against an expected best of 0.42 of 11. Every single configuration table entry reads 2/11.

> **Slidefair is refuted for all keys, all periods and all phases simultaneously, over 32
> alphabets, with no key search performed.** This is the most decisive single family closure in
> the repository per unit of computation.

### 1.4 Portax — closed, but by inheritance, and one correction

Portax seriates the plaintext into rows of length p, pairs each letter with the one below it, and
enciphers vertical pairs on a two-row slide, writing the ciphertext back into the same cells — so
Portax **is** position-preserving and the cribs apply directly.

**Correction to a natural first guess, recorded because it is the kind of error that produces a
false negative:** it is tempting to say a top-row letter can never encipher to itself under Portax
and that F2 therefore kills it. That is wrong. In the mixed case where both letters of a pair sit
in the *same column*, the rectangle degenerates and the pair is returned unchanged, so Portax does
permit self-encryption. F2 does not close it.

What does close it, weakly on its own and firmly by inheritance:

* **Key-free row-parity invariant** (derived here): in all three Portax rules,
  `#TOP(c_u, c_l) = 2 − #TOP(p_u, p_l)`, whatever the key and slide. This is one bit per crib
  pair, so it is a weak test; at p = 2–11 between 1 and 9 crib pairs are testable, the best
  alphabet satisfies 5/9 at p = 2 and 6/7 at p = 3, and at p ≥ 12 **no** crib pair is testable at
  all. It leaves short periods standing, as a 1-bit test must.
* **Inheritance.** Portax's substitution stage is a letterwise map indexed by ciphertext position,
  so every one-stage negative transfers (`twocipher.md`, the T-then-S / ciphertext-reading row),
  and every period it leaves standing is a period where `families.md` already returns zero
  survivors over 7.09 M alphabet pairs.

Stated that way and not more strongly.

---

## 2. Task (b) — the K5 lever. **The main result.**

This is the part of the brief that asked for the reasoning to be got exactly right, so the
argument is set out in full. Script `k5_b_depth.py`, log `k5_b_output.txt`.

### 2.1 The two sources, quoted precisely

* **Sanborn**, International Spy Museum / *Scientific American*, 2025-11-12:
  > "The new code will involve elements of the other puzzles and, like K4, will be 97 characters
  > long. **Both 97-letter messages will share some of the same coded words in the same position.**"
* **RR Auction lot description**, item 6 (the seller's own words, October 2025):
  > "Unpublished 1988 **alternate K4 plaintext and coding chart** — now known as K5."

The second source is the one the community has under-weighted, and it points the opposite way from
the first as usually read.

### 2.2 The ambiguity, and the three models

"Coded words" is ambiguous:

* **Reading A** — the *ciphertext* letter groups: C4 and C5 carry identical letter runs at
  identical indices.
* **Reading B** — the words *that were coded*, i.e. the plaintext words: P4 and P5 carry the same
  words at the same indices, and nothing is claimed about the ciphertext.

Reading B is the ordinary-English one and matches how Sanborn uses the phrase elsewhere ("the coded
words on the sculpture" means the message, not the cipher letters). Reading A is the one this
repository's `README` §3.4 and `sanborn_statements.md` C10 assumed.

Three cipher models matter:

| model | definition |
|---|---|
| **M_pos** | `C[i] = g_i(P[i])`, `g_i` a bijection depending only on position *i*, same chart for both messages |
| **M_auto** | the key at *i* depends on the message (plaintext or ciphertext autokey, with a primer) |
| **M_2chart** | as M_pos but K4 and K5 use **different** charts — which is what the auction lot text says |

### 2.3 Four theorems, each verified by construction

**T1. Under M_pos, reading A and reading B are the same statement.**
`C4[i] == C5[i] ⟺ P4[i] == P5[i]`, for any bijections. Verified over 400 random 97-column charts
with a planted shared 12-letter plaintext word: the ciphertext-agreement set differed from the
plaintext-agreement set in **0 of 400** trials.

*Consequence:* a shared ciphertext run is neither more nor less than a shared plaintext run. So
reading A carries **no information about the key** beyond what reading B carries, and "shared
ciphertext ⟹ positional" is affirming the consequent.

**T2. A shared run at the head of the message does not exclude autokey.**
Under plaintext autokey with a shared primer, if the two plaintexts agree on the whole prefix
[0, s) then the key streams agree on [0, s) and so do the ciphertexts. Verified: **0 failures in
400** trials with a random shared prefix.

*Consequence:* this is the step C10 skipped. Autokey is excluded only by a shared run beginning
**after** the first position where the plaintexts differ.

**T3. A shared run after a divergence *does* exclude autokey, at 26⁻ˡᵉⁿ.**
4,000 trials with a 6-letter shared plaintext word planted at 64–69 and different plaintext
before it: the ciphertext run was also shared in **0** trials (chance 26⁻⁶ = 3.2 × 10⁻⁹).

**T4. Under M_2chart the statement is vacuous.**
With a second free chart, any ciphertext agreement can be manufactured over any plaintext
disagreement. Constructed explicitly: a pair with P4 ≠ P5 at every one of 64–74 and yet
C4[64:74] == C5[64:74], with every chart column still a bijection.

### 2.4 Verdict on the alleged contradiction

> **There is no contradiction with the repository's negatives, and the C10 inference does not
> hold.** The tension was an artefact of (i) over-reading one sentence of Sanborn's and (ii)
> understating what "position-indexed systems are ruled out" actually means.

On (ii), the quantification matters and has never been stated:

| quantity | value |
|---|---|
| position-indexed key streams over 97 letters | 26⁹⁷ = 1.788 × 10¹³⁷ |
| of those, **fitting all 24 cribs exactly** (per cipher/alphabet combo) | 26⁷³ = **1.964 × 10¹⁰³** |
| ditto across all 24 combos | 4.71 × 10¹⁰⁴ |
| total searched by this repository (generous upper bound, double counting allowed) | 6.40 × 10³⁶ |
| **fraction of the crib-perfect positional space examined** | **3.26 × 10⁻⁶⁷** |

What has been ruled out is *structured* position-indexed streams — short-period, arithmetic in the
index, or copied in reading order from a known text. A **97-symbol hand-drawn chart with no
compressive description** is a position-indexed key stream, fits the cribs trivially, and no
crib-based search can ever reach it. That is precisely the object Sanborn keeps naming: *"no one
has recovered the original matrix."*

**The weaker claim the brief anticipated is the correct one.** The shared words are most likely
shared because the two *plaintexts* share words at those positions — a plain statement about two
drafts of the same message, consistent with every cipher model on the table, and carrying no
cryptanalytic content about the mechanism.

### 2.5 What the cribs *can* say about a positional chart — alphabet-free, family-free

New, and the strongest statement available without any cipher model. Say the chart has period *p*
if `g_i = g_j` whenever `i ≡ j (mod p)`. Then for any *i, j* in the same class,
`P_i == P_j ⟺ C_i == C_j` — no alphabet, no family, no key algebra. A crib pair violating it
refutes **every p dividing |i − j|**.

* 22 crib pairs refute `g_i = g_j`; their separations are **{1, 3, 4, 5, 7, 9, 34, 42, 43, 45, 50}**.
* 1 crib pair is consistent and informative: positions 28 and 66, separation 38.
* **19 periods in 1–97 are refuted outright by a single crib pair**: {1, 2, 3, 4, 5, 6, 7, 9, 10,
  14, 15, 17, 21, 25, 34, 42, 43, 45, 50}.
* **78 periods survive** — but the survival is mostly vacuous. Weight available, by period:
  p = 8 carries c = 16 constraints, p = 13 carries 11, p = 24 carries 5, p = 26 carries 1, and
  **p = 27, 28, 29 and every p ≥ 53 carry zero**. Those are periods the cribs cannot see at all,
  not periods with evidence for them.

This is the exact boundary of what 24 crib letters can say about a positional chart, and it
coincides with the boundary the period sweeps hit.

### 2.6 The pre-registered K5 experiment

Machinery built and validated now, decision rule fixed now, so that nothing is fitted after the
fact. `k5_b_depth.py` exports `align_runs(C4, C5)`.

**Chance expectations, exact (DP over 97 positions, per-position match probability 1/26):**

| statistic | chance |
|---|---|
| expected aligned equal positions | 3.73 (sd 1.89) |
| P(some aligned run ≥ 3) | 5.19 × 10⁻³ |
| P(some aligned run ≥ 4) | 1.98 × 10⁻⁴ |
| P(some aligned run ≥ 5) | 7.53 × 10⁻⁶ |
| P(some aligned run ≥ 6) | 2.87 × 10⁻⁷ |
| P(some aligned run ≥ 9) | 1.58 × 10⁻¹¹ |
| P(some aligned run ≥ 11) | 2.48 × 10⁻¹⁴ |
| P(≥ 8 aligned matches, any arrangement) | 0.034 |
| P(≥ 10 aligned matches) | 0.0042 |
| P(≥ 14 aligned matches) | 2.1 × 10⁻⁵ |

**Decision rule, fixed in advance:**

1. Any aligned identical run of **length ≥ 5** ⟹ one shared positional chart *and* shared
   plaintext there (p < 3 × 10⁻⁴).
2. A run of **length ≥ 9 or ≥ 11** ⟹ decisive (p < 10⁻⁹), and it is almost certainly one of the
   released crib words.
3. **No aligned run of length ≥ 4 anywhere** ⟹ evidence for M_2chart, i.e. the auction lot's
   "alternate … coding chart" is literal, and **the depth attack is dead**.
4. An excess of *isolated* aligned matches (≥ 10) with no long run ⟹ the middle case: two charts
   drawn on one worksheet sharing individual columns. Neither reading anticipates this; it would
   be the most informative outcome of all.

**Falsifiable predictions, if there is one shared chart and the shared words are the released
cribs.** K5's ciphertext must read, literally:

```
positions 22–25   FLRV        (EAST)
positions 26–34   QQPRNGKSS   (NORTHEAST)
positions 64–69   NYPVTT      (BERLIN)
positions 70–74   MZFPK       (CLOCK)
```

### 2.7 How much is a depth pair actually worth? (This has never been asked.)

The C10 note assumes the key cancels in the difference stream. **That assumption is a Vigenère
assumption and it may well be false.**

* **Case 1 — shift-structured chart** (Quagmire/Vigenère family: `g_i` is "add k_i" in a fixed
  alphabet pair). Then `idx(C4ᵢ) − idx(C5ᵢ) = idx(P4ᵢ) − idx(P5ᵢ)`, the key cancels, and 97 letters
  of classical depth-2 with two English plaintexts is comfortably solvable. *Worth: the whole
  message.* Verified on a synthetic shift-chart pair: the difference stream was recovered exactly
  and the planted shared word at 64–74 was localised as an 11-long run of zeros.
* **Case 2 — general per-column chart** (97 independent bijections: a hand-drawn spreadsheet of
  97 columns × 26 rows, which is exactly what Sanborn means by "the matrix"). Knowing
  (C4ᵢ, C5ᵢ) pins two cells of column *i* and nothing else: for **any** pair of distinct plaintext
  letters there exists a bijection realising **any** pair of distinct ciphertext letters —
  constructed successfully in 2000 of 2000 random trials. The only surviving constraint is
  `C4ᵢ == C5ᵢ ⟺ P4ᵢ == P5ᵢ`. *Worth: exactly the 97-bit agreement pattern between the two
  plaintexts, and no more.*

So the entire value of K5 hinges on whether the chart is shift-structured. That question is
answered by the same aligned-run test — and by §2.5's period analysis once the pair is in hand.

### 2.8 The strategic consequence, and a real unresolved tension

Put the auction text and the 1988 date together. Two messages, 97 characters each, **each with its
own chart**, both drawn in 1988, before the final plaintext was fixed.

1. **97 is a property of the worksheet, not of the message.** Sanborn had a 97-cell chart and wrote
   messages to fit it; 97 = 4 + 31 + 31 + 31 is the panel layout. Any theory deriving 97 from the
   plaintext has the causality backwards.
2. **The chart is per-message, hence fitted, hence plausibly incompressible.** You do not redraw a
   keyword for an alternate draft. Redrawing the *chart* is what you do when the chart **is** the
   key material. This is the best available explanation for 35 years of failure: there may be no
   short description of the key stream to find.
3. **Therefore the aligned-run test is the most informative single experiment left**, and it costs
   one minute on publication day. Note that (2) predicts *no* shared runs while reading A predicts
   shared runs — the two are in direct conflict and one string comparison resolves it.

**The tension this creates with Scheidt is real and is not resolved here.** If the key material is
an incompressible 97-symbol chart, K4 is not breakable from the ciphertext, which contradicts
Scheidt directly: *"designed to be solved in a straight-forward manner with pencil and paper"*, a
9/10 difficulty rating, an expectation of five to ten years, and his own brief *"don't create
something that you cannot break."* The documented resolution is Sanborn's, not an invention of
this report: Scheidt supplied systems *"plus ways to modify all of those systems"*; Sanborn says he
modified them further so that even Scheidt would not know the content; and **nobody ever ran a
reverse check on K4**. Scheidt's breakability guarantee covers *Scheidt's* layer. If something
incompressible exists, it is the artist's mask on top — which is a statement about where to look:
**at a hand-drawn worksheet, not at an algorithm.**

---

## 3. Task (c) — cross-section key continuation

Script `k5_c_phase.py`, log `k5_c_output.txt`. Validated first: `k5_lib` self-test PASSes (round
trips, planted-period recovery, perturbation rejection, explicit-key crib scoring, K1
re-encryption under PALIMPSEST), and a synthetic K4 built with PALIMPSEST at phase 8 under
Quagmire III is recovered at 24/24 by the explicit phase test.

### 3.1 The exact arithmetic

Lengths verified from the data, not quoted: K1 63/63, K2 **370 plaintext / 369 ciphertext** (the
2006 dropped S), K3 336/336, three `?` inside K2 and one ending K3, K4 starting at panel character
**772** of 869 and panel letter **768** of 865.

| cumulative count before K4 | n | mod 10 (PALIMPSEST) | mod 8 (ABSCISSA) | mod 18 |
|---|---|---|---|---|
| K1 only | 63 | 3 | 7 | 9 |
| K1+K2 ciphertext | 432 | 2 | 0 | 0 |
| K1+K2 plaintext | 433 | 3 | 1 | 1 |
| K2 ciphertext | 369 | 9 | 1 | 9 |
| K2 plaintext | 370 | 0 | 2 | 10 |
| K3 only | 336 | 6 | 0 | 12 |
| K2+K3 ciphertext | 705 | 5 | 1 | 3 |
| K2+K3 plaintext | 706 | 6 | 2 | 4 |
| **K1+K2+K3 ciphertext = panel letters** | **768** | **8** | **0** | 12 |
| K1+K2+K3 plaintext | 769 | 9 | 1 | 13 |
| **K1+K2+K3 + the four `?` = panel characters** | **772** | **2** | **4** | 16 |
| K1+K2+K3 plaintext, X stripped | 761 | 1 | 1 | 5 |

So the phases to test are {0,1,2,3,5,6,8,9} for PALIMPSEST and {0,1,2,4,7} for ABSCISSA.

### 3.2 The subsumption theorem — task (c) is a closed corollary

> **Theorem.** For any key word W of length L and any phase s, the stream `k_i = W[(s+i) mod L]`
> is periodic with period L. The crib-consistency test at period L quantifies over **all** period-L
> streams at once, hence over all (W, s) pairs simultaneously. A period-L test returning zero
> survivors therefore kills every keyword of length L at **every** phase, including every
> cross-section continuation phase.
>
> **Corollary.** Alphabet rotation is absorbed too: rotating the plaintext or ciphertext alphabet
> by *r* maps every forced key value by a constant offset, which cannot change whether the values
> are constant on a residue class. "The K1/K2 alphabet rotation carried over" is subsumed.

Explicit period-L consistency, 12 combos:

| L | constraints c | survivors | chance/test | expected |
|---|---|---|---|---|
| 7 | 17 | **0** | 8.8 × 10⁻²⁵ | 1.1 × 10⁻²³ |
| 8 (ABSCISSA) | 16 | **0** | 2.3 × 10⁻²³ | 2.8 × 10⁻²² |
| 10 (PALIMPSEST) | 14 | **0** | 1.6 × 10⁻²⁰ | 1.9 × 10⁻¹⁹ |
| 18 (both concatenated) | 7 | **0** | 1.2 × 10⁻¹⁰ | 1.5 × 10⁻⁹ |
| 25 | 3 | **0** | 5.7 × 10⁻⁵ | 6.8 × 10⁻⁴ |

### 3.3 The explicit runs anyway, and the non-subsumed cases

| sweep | tests | best | chance |
|---|---|---|---|
| 6 key words × every continuation phase × 24 combos | 1,176 | **5/24** | 0.92/24 per test |
| progressive continuation, `k_i = W[(n₀+i) mod L] + ⌊(n₀+i)/L⌋`, both directions | 2,496 | **5/24** | — |
| running-key continuation: sculpture texts read from the cross-section offset | 56 offsets × 24 combos | **5/24** | — |
| "the next keyword in the list" — 27 Sanborn-vocabulary words × all phases | 6,384 | **5/24** | — |

Agreement histogram for the first sweep: {0:484, 1:425, 2:193, 3:64, 4:8, 5:2}; total observed crib
hits 1,045 against 1,085 expected. **Below chance.**

**Task (c) is closed.** The single most physically motivated phase — PALIMPSEST continuing across
the whole carved panel, arriving at K4 at phase 8 (letters) or 2 (characters including the `?`) —
is dead along with every other.

---

## 4. Task (d) — the question mark

Script `k5_d_question.py`, log `k5_d_output.txt`. Validation: planted period-9, -13 and -7 ciphers
on extended texts with true tail lengths 3, 11 and 25 were each recovered at exactly the true tail
length and nowhere else.

### 4.1 Does Sanborn's index count the `?` ? No.

One line, re-derived here and agreeing with `crib_placement.md` §1.3:

```
K4 alone, 1-indexed, 64–69 :  NYPVTT   <- matches the published string
'?'+K4,   1-indexed, 64–69 :  BNYPVT
K4 alone, 0-indexed, 64–69 :  YPVTTM
```

### 4.2 The `?` as a key slot — subsumed, with the proof

> **Theorem.** Shifting every crib position by a constant *d* shifts every residue mod *p* by the
> same constant, so the partition of the crib positions into residue classes — and hence the number
> of forced equalities `c_p` — is **unchanged**. No constant key-slot offset can change any periodic
> crib test.

Verified numerically for d = 0…8 and p = 2…40: **0 exceptions**. So "the worksheet had 98 cells and
the key advanced across the `?`" adds nothing beyond §3 and `runningkey.md`'s all-offsets sweep.

### 4.3 K4 begins *before* `OBKR` — the part with real content

The only version of the `?` hypothesis that changes anything is the one that changes **which
ciphertext letter pairs with which crib letter**: the enciphered message is `X = T[−k:] + K4` and
Sanborn's index 64 counts from the start of X. `crib_placement.md` §2 covered this as a δ = −k
global slide for k ≤ 21; this run extends to k = 1…40 and adds two tail sources the slide cannot
express.

| tail source | k | tests (12 combos) | survivors | chance exp | max c with a survivor |
|---|---|---|---|---|---|
| K3 ciphertext tail | 1–40 | 13,920 | 1,482 | 1,477 | **1** |
| K3 **plaintext** tail | 1–40 | 13,920 | 1,477 | 1,477 | **1** |
| panel letters before K4 | 1–40 | 13,920 | 1,482 | 1,477 | **1** |
| K3 ciphertext tail reversed | 1–40 | 13,920 | 1,489 | 1,477 | **1** |

Repeated over **867 keyed-alphabet combos**: 1,005,720 tests per tail source, 106,778–106,814
survivors against 106,710 expected, **max c = 1 everywhere**. A genuine solution would appear at
c ≥ 10. Nothing does.

### 4.4 The missing answer — "YES, WONDERFUL THINGS"

K3 ends with Carter's question and the sculpture withholds his reply. That reply is the one piece
of Kryptos-narrative text deliberately *absent* from the stone, so it is absent from
`runningkey.md`'s 66-text corpus and has never been tested. Sanborn, April 2006: *"the answers to
the first three passages contain clues to the fourth passage."* This is the most literal possible
reading of that sentence, and it is the genuinely new key material in task (d).

16 phrases tested (`WONDERFULTHINGS`, `YESWONDERFULTHINGS`, `CANYOUSEEANYTHING`, the question and
answer concatenated in both orders, `HOWARDCARTER`, `LORDCARNARVON`, `TUTANKHAMUN`,
`VALLEYOFTHEKINGS`, `NOVEMBERTWENTYSIXTH`, …).

| test | scale | result |
|---|---|---|
| explicit key stream, every phase, 24 combos | 6,264 tests | **best 6/24**; 5,510 total crib hits against 5,782 expected |
| as keyword-mixed **alphabets** (34 new alphabets), periods 2–30, 3 rules | 100,572 tests | 10,646 survivors against **10,671 expected**; every survivor at c ≤ 1 |
| as a **running key** against the required key blocks, 24 combos × 26 rotations | 162,864 tests | **best joint Hamming distance 16 of 24**; a solution is 0, and P(≤ 2 mismatches) = 1.9 × 10⁻²⁹ |

**Negative at chance on all three.** Worth having in writing: it was the best-motivated untested
key text on the board.

---

## 5. Task (e) — OBKR as an indicator group

Script `k5_e_indicator.py`, log `k5_e_output.txt`. Positive control: a synthetic K4 whose body key
is OBKR repeated from position 5 under Quagmire III is recovered at 24/24.

### 5.1 What an indicator can change — and the resulting subsumption

An indicator changes three things and only three:

1. **Where the key stream starts.** The body begins at position 5, so the key index becomes *i*−4.
   That is a constant shift; by the theorem of §4.2 it leaves `c_p` identical at every period
   (verified for d = ±4, p = 2…40: **identical at every period**), and for a text-derived stream it
   is an offset, already swept.
2. **Which key.** If the rule yields a repeating key of length L, the period-L sweep in
   `families.md` quantified over all period-L keys at once.
3. **Nothing else.** The cribs do not move: positions 22–25, 26–34, 64–69, 70–74 are absolute in
   the carved 97 and the ciphertext letters there are unchanged.

> **Consequence worth stating on its own: "the real message is 93 letters" is not a hypothesis the
> cribs can test. It is a relabelling of the key pointer.**

So an indicator rule has new content only if it produces a **non-periodic** key stream, a **new
alphabet**, or both.

### 5.2 Every rule, tested

| rule | tests | best | observed ≥ best | chance expectation |
|---|---|---|---|---|
| E2a OBKR + 7 elementary transforms as repeating keys, every phase, both leads | 2,400 | 5/24 | 2 | 4.65 |
| E2b **the proper 1940s rule** — OBKR de/enciphered under 7 standing keys × all phases × 3 rules × 4 alphabet pairings × 2 key alphabets, yielding **1,270 distinct message keys**, each tested as a period-4 body key at every phase | 243,840 | 6/24 | 14 | 58.33 |
| E3a numeric (A=0, A=1, KRYPTOS index, mod-10) as period-4 Gronsfeld | 960 | 4/24 | 8 | 12.05 |
| E3b **decimation** — every n-th letter of each sculpture text, n from OBKR (not an offset, so not covered by the running-key sweep) | 8,784 | 6/24 | 2 | 2.10 |
| E4 **tableau walks** from OBKR-named cells: 2 squares (ideal and carved, with the anomalous L) × 12 ordered letter pairs × 2 index conventions × 8 walk modes (right, left, down, up, diagonal, anti-diagonal, boustrophedon, knight) + split-coordinate variants = 416 streams | 9,984 | **7/24** | 2 | 0.24 |
| E5 **Gromark primer** — OBKR seeding chain addition, 5 index conventions × 2 bases × 3 lags × 2 leads × forward/reversed | 2,880 | 5/24 | 6 | 5.58 |
| E6 **OBKR-keyed alphabets** (20 alphabets absent from the 208,627-word dictionary set, including alphabets keyed by the K4 ciphertext prefix), periods 2–30 | 34,800 | — | 3,700 survivors | 3,692 expected; **max c = 1** |

`OBKR` in numbers, for the record: A=0 → (14, 1, 10, 17), sum 42; A=1 → (15, 2, 11, 18), sum 46;
KRYPTOS index → (5, 8, 0, 1), sum 14.

**The one nominal excess, handled honestly.** E4 shows 2 observations at ≥ 7/24 against 0.24
expected. They are `ideal (O,K)/KRYPTOS-index/boustrophedon` and `physical (O,K)/KRYPTOS-index/
boustrophedon` under the *same* cipher configuration — and the ideal and carved tableaux differ by
a single letter, so these are **one observation, not two**. One event against 0.24 expected is
p ≈ 0.21, before any correction for the six strata reported in this table. It is noise, and 7/24 is
17 crib letters short of a solution.

### 5.3 What an indicator can and cannot buy

A four-letter indicator addresses at most 26⁴ = 456,976 message keys. The crib-perfect positional
key space is 26⁷³ (§2.4). Even a perfect indicator rule reduces the problem by a factor of about
10⁻⁹⁷ of what would be needed. **Indicator hypotheses are cheap to test and structurally incapable
of being the whole story.**

---

## 6. Multiple-testing accounting

All five tasks are one family of tests and should be read as one.

* **New tests in this work: 4,663,692** — 11,400 in (c), 4,348,260 in (d), 303,648 in (e), 384 in
  (a, continued). With `k5_a_genealogy.py`'s 46.3 M already on record, the k5_* line totals
  **≈ 51.0 million** crib tests.
* The **best crib agreement anywhere is 7 of 24**, and it resolves to a single correlated
  observation. Chance expectation per test is 0.92 of 24. A solution is 24 of 24.
* Every consistency-sweep survivor count sits on its chance expectation to within a few per cent,
  and — the statistic that actually matters because it is a structural bound rather than a count —
  **the highest-constraint stratum containing any survivor anywhere in this work is c = 1.** The
  true placement carries c = 22 at period 2 and c = 11 at period 13.
* Counts are not independent: keyed alphabets share most of their letters, tableau walks from
  nearby cells overlap, and the ideal and carved tableaux differ by one letter. Where a naive
  Poisson figure is quoted it is quoted as an upper bound on significance, and every nominal excess
  in this work is traced to that dependence.

---

## 7. What this closes, and what it opens

**Closed.**

1. **Slidefair**, all three slide variants, both digraph alignments, both output orders, 32
   alphabets, **all keys and all periods at once** — by a key-free invariant, 2/11 against a
   required 11/11.
2. **Portax** — by the row-parity invariant plus inheritance from the one-stage negatives.
3. **Cross-section key continuation** (task c) — and, more usefully, *proved to be a corollary* of
   the period sweeps rather than a separate question.
4. **The `?` hypotheses** (task d): the indexing reading is refuted documentarily, the key-slot
   reading is proved subsumed, and the "K4 begins before OBKR" reading is swept to k = 40 over four
   tail sources and 867 alphabets with max c = 1.
5. **"YES, WONDERFUL THINGS"** and the Carter/Carnarvon field as key material — the best-motivated
   untested key text there was.
6. **OBKR as an indicator**, under every derivation rule that can be named, plus the proof that the
   93-letter-body reading is invisible to the cribs.
7. **The C10 inference** — "K5's shared words show the system is positional and not autokeyed" — is
   withdrawn as unsound, and the repository's `README` §3.4 and `sanborn_statements.md` C10 should
   be amended to the weaker, correct reading.

**Open, and where the value now is.**

1. **The aligned-run experiment on K5**, pre-registered in §2.6 with its decision rule and chance
   thresholds fixed. It is the single most informative experiment available and it costs one minute
   on publication day. Watch `paradigm.xyz/kryptos`.
2. **The chart hypothesis.** If K5 shows no aligned runs, the auction lot's "alternate K4 plaintext
   *and coding chart*" is literal, the key material is per-message, and no key-stream search can
   ever succeed. The remaining routes are then documentary, not cryptanalytic: the Smithsonian
   files (sealed to 2075), Paradigm's archive, and the reconstruction of a 97-cell worksheet.
3. **Periods 27, 28, 29 and ≥ 53 remain untestable by cribs** — confirmed here alphabet-free and
   family-free in §2.5, not merely for the periodic-Vigenère family. Only English scoring can
   decide them.
4. The forced equality **k₂₈ = k₆₆ (separation 38)** remains a free filter that every future
   candidate key stream in this repository should be run against.
