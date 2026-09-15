# Kryptos K4 — consolidated summary of this effort

**The one document to open first.** It merges every line of attack in `findings/` and `lateral/`
into a single record: what was tested, at what scale, with what outcome, and what is left.

Written 2026-09-13. Sources for every number are the per-attack reports named in each row; the
core arithmetic below (ciphertext, cribs, conflict structure, period constraints) was
re-derived independently while writing this file and matches the reports exactly.

---

## 1. Bottom line

**K4 is not solved by this effort. No candidate decryption exists. Nothing here is a partial
solution, a near miss, or a lead that survived scrutiny.**

Stated precisely, because "not solved" is a weaker claim than what was actually achieved:

* Across roughly **10⁹ explicit crib-consistency tests** plus several families closed **exactly**
  rather than by enumeration (55,066,851,840 tableau-lookup trials settled by hash join; the full
  25!, 36!, 27!, 25!², 36!² unknown-square spaces settled by CP-SAT; all 26! cipher alphabets
  settled in the Gromark test; all 97! transpositions settled by an invariance argument), the
  number of configurations fitting all 24 Sanborn crib letters **and** producing English is
  **zero**.
* The best crib agreement anywhere among tests that actually constrain the key is **10 of 24** —
  from a sweep in which chance alone produces 4.09 such results. The best in the K5/genealogy line is
  7/24 (chance expectation 0.24, one correlated observation, p ≈ 0.21). A solution is 24/24.
* Every sweep's survivor count sits **at or below** its own chance expectation. Where survivor
  counts exceed chance they are traced to dependence between near-duplicate alphabets or
  transpositions, and in every such case the survivors carry **c ≤ 4** forced constraints, where
  the true placement carries **c = 22** at period 2 and **c = 11** at period 13.
* The few models that *do* fit 24/24 (conjugated-matrix bifid, conjugated-matrix ADFGVX, a
  26-of-100 monome-dinome grid, M-209/SIGABA, wide-key ADFGVX, any free per-position chart) fit
  because their key entropy exceeds the 113 bits the cribs supply. They are **guaranteed to fit by
  counting alone**, their decryptions are gibberish (quadgram −6.9 to −7.6 against a random median
  of −8.24 and English ≈ −5.6), and they are therefore unfalsifiable rather than promising.

The deliverable of this effort is the **negative space**: §3 below is a map of where K4 is not, at
a resolution nobody has published, with chance expectations attached to every figure so a future
solver can trust it and skip it.

---

## 2. The real-world state (facts, with the disputed one flagged)

| when | what | status |
|---|---|---|
| **3 Sep 2025** | Writers **Jarett Kobek** and **Richard Byrne**, having seen from the auction listing that Sanborn's coding charts were at the **Smithsonian's Archives of American Art**, requested access and photographed the papers. Among them were **taped-together strips of scrambled sentence fragments** — copies Sanborn made in 1990 so the CIA's Historical Intelligence staff could vet the content without reading it. Combining the fragments with the four public cribs, they reconstructed the K4 **plaintext** and emailed it to Sanborn, who confirmed it. | Kobek: *"There's no way on earth that this is a cryptographic solve."* Sanborn: they *"found scrambled text, and not by solving the cryptogram."* **Output recovered; method not.** They signed no NDA, agreed not to publish, and have not. |
| **16 Oct – 20 Nov 2025** | RR Auction sale #730, *"Decoding History: Kryptos K4 & K5, Enigma, and the Rosetta Stone"*, lot 2001, *"The Complete Secrets of Kryptos: Jim Sanborn's Private Archive"* — 17 components including the **handwritten K4 plaintext with a signed Scheidt letter**, **the original K4 coding system**, the K1–K3 coding charts, and item 6, the **unpublished 1988 alternate K4 plaintext and coding chart, now designated K5**. Estimate $300–500k. | Closed on Sanborn's 80th birthday; **$962,500** including buyer's premium, anonymous bidder. |
| **12 Jun 2026** | **Paradigm** identified itself as the buyer and published its verifier: Sanborn typed the plaintext on an isolated, freshly set-up laptop; the text was hashed with **SHA-256**; the hash was sent to **Google Cloud KMS**, which returned an **HMAC** tag reproducible only with the cloud-held key; the plaintext never left the device and the laptop was wiped. Check is `HMAC_k(SHA256(candidate)) == tag`. Submissions **$1** via Stripe (stated purpose: make brute force uneconomic). A separate ten-puzzle **Kryptos CTF** ($1,000 per puzzle, $10,000 total) launched the same day; **K4 itself carries no prize**. | Live. **This project does not submit** — it is a paid transaction and out of scope. Note what the design does *not* do: it binds a **plaintext string, not a method**, so it cannot distinguish a cryptanalytic solve from a leak, and anyone already holding the plaintext can produce a verifying submission at will. |
| **"sealed until 2075"** | Widely reported: Sanborn asked the Smithsonian to seal the relevant files for 50 years and the Smithsonian complied. | **Disputed by the primary document.** The official finding aid (`sirismm.si.edu/EADpdfs/AAA.sanbojim.pdf`, *A Finding Aid to the Jim Sanborn papers, circa 1945–2024*, Ricky Gomez, 2024-02-12, **revised 2026-05-06**) states the collection is **"open for research"**, names no closure, and contains the words "sealed", "closed" and "2075" nowhere. It lists **Box 6 Folders 18–19, "Cracked Codes and Charts"** and, in the 2026 accession, **Box 18 Folder 19, "Russian Charts"** as available. Four readings are consistent with this (donor agreement never written into the EAD; the specific scraps withdrawn; restriction administered at the desk; press over-read the request) and the record does not choose between them. Anyone repeating "sealed until 2075" should know the finding aid does not say it. |
| **K5** | 97 characters, made in 1988 as the alternate K4 plaintext, ciphertext held by Paradigm, release promised with no date. Sanborn (SciAm, 12 Nov 2025): both 97-letter messages *"will share some of the same coded words in the same position."* | **Not public.** §6 ranks the experiment that becomes available the day it is. |

**What would count as a public cryptanalytic solve.** Not a plaintext — a plaintext is now
obtainable by four people without any cryptanalysis, and a $1 verifier receipt proves only that
someone has a string. A solve is: **a stated method that takes the 97 published ciphertext letters
plus public material, produces the plaintext, reproduces all 24 crib letters as output rather than
as input, and is executable by a third party who was told nothing else.** The standing bar in this
repository — **24/24 cribs AND English**, with every hit count quoted against its chance
expectation — is the operational form of that, and nothing in this effort weakens it. The method
remains the open problem, and because K5 was built by the same process it is worth more than the
K4 plaintext.

Headlines reading "Kryptos K4 solved by Paradigm" are wrong: Paradigm bought a solution; it did
not break a cipher. Paradigm's own pages say K4 is still unsolved.

---

## 3. THE CONSOLIDATED RULED-OUT TABLE

**How to read every row.** The 24 cribs (1-indexed 22–25 EAST, 26–34 NORTHEAST, 64–69 BERLIN,
70–74 CLOCK) give 24 (ciphertext, plaintext) pairs. For a key with period *p*, those 24 positions
occupy 24 − *c* distinct residues, so a random key passes the consistency test with probability
**26⁻ᶜ**; *c* is quoted as the strength of any negative. Verified values (re-derived here):

```
p:  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 | 27 28 29 | 30 ... 52 | >=53
c: 22 21 20 19 18 17 16 15 14 13 12 11 11  9  8  7  7  9 11 11  9  7  5  3  1 |  0  0  0 |  1 ...  1 |   0
```

Periods **27, 28, 29 and every p ≥ 53 impose zero crib constraints** — the cribs cannot see them
at all. That boundary recurs in every row below and is the honest limit of crib-based work.

Two structural facts used throughout, both verified here: the ciphertext contains **all 26
letters** (J at 41, 52, 82), and **S→S at 33 and K→K at 74** — a letter can represent itself.
A third: the cribs need **three E's** and the ciphertext has **two**.

### 3.A One-stage letterwise substitution

| family | scope actually tested | outcome (with chance expectation) | source |
|---|---|---|---|
| Monoalphabetic, Caesar, affine | exhaustive; 1,352 affine keys × 2 alphabets | **impossible.** 9 forward + 8 reverse crib conflicts (Q→N and Q→O at adjacent 26–27 alone suffices). The crib conflict graph has **chromatic number 3**: at least three distinct substitution alphabets are forced | `families.md` §5, `matrix_b_output.txt` B4 |
| Pure transposition (no substitution) | structural + statistical | **impossible twice over.** Cribs need 3 E's, ciphertext has 2. Independently: K3's ciphertext *is* a transposition of English and has IoC 0.06615 against K4's 0.03608, ~9–11 null sd apart; "transposition of English" is excluded at p ≈ 0 by the IoC | `families.md` §5, `statistics.md` §2, §7 |
| Periodic Vigenère / Beaufort / variant-Beaufort / Quagmire I–IV | **7,093,607 keyed-alphabet pairs** (17 Kryptos-list alphabets × 208,627 dictionary alphabets, both roles, + 17×17) × periods 2–26 ≈ **1.8 × 10⁸ tests** | **0 survivors for p ≤ 25.** p = 26 carries c = 1, so its 487,280 "survivors" are chance; best partial decryption scores bigram −6.17 where filling the same template at random gives −6.13 | `families.md` §1 |
| Porta | 2 tables × 2 alphabet orders × p 2–26 | **impossible for every 26-letter alphabet.** 16 of 24 crib pairs have ct and pt in the same half; and Porta can never map a letter to itself (S→S, K→K) | `families.md` §2 |
| Gronsfeld (any digit key, any source) | 3 rules × 2 alphabets; plus 55 lateral digit streams, 24,564 alignments | **arithmetically impossible.** 11–16 of the 24 required shifts exceed 9 in every configuration. No digit stream that will ever be proposed can be a Gronsfeld key for K4 | `families.md` §2, `lateral/INDEX.md` §2 |
| Trithemius / progressive `a + b·i` | all 2,704 keys | 0; best 7/24 | `families.md` §2 |
| Periodic key + progressive alphabet shift | 5,200 combinations (p 2–26, b 0–25, 2 alphabets, 2 families, both advance rules) | 0, including at p = 26 | `families.md` §2 |
| Plaintext autokey | 2,304 (combo, primer) pairs, L = 1–96 | 1 survivor carrying a **single** check, against 2.84 expected by chance; 0 survivors with ≥3 checks | `runningkey.md` §3 |
| Ciphertext autokey | 2,304 (combo, primer) pairs, L = 1–96, 24 hard letter tests each | **0 full survivors**; best 4/24 | `runningkey.md` §3 |
| **Gromark** (the one family the ML classifiers and Bean endorsed) | G1: **14,732,068** primer × plaintext-alphabet tests, *exact over all 26! cipher alphabets*; G2 (Bean's reading, free single alphabet): **19,347,878** primers swept, 20,965 passed the digit filter; periodic Gromark, bases 10 and 26, p = 1–6, all keys | **0 survivors everywhere.** Including Bean's own published case (base 10, primer length 5): **0 alphabet-feasible of 100,000**, where Bean reported 39 crib-consistent primers — the difference is that this test also requires an alphabet to exist. **This closes `prior_art.md`'s only "open" item** | `k5_a_output.txt` S1–S3 |
| **Slidefair** (all three slides) | closed by a **key-free invariant** — the key cancels from every digraph (`c1+c2 = p1+p2`, or `c1−c2 = p1−p2`) — over 32 alphabets × 3 slides × 2 orders × 2 alignments = 384 configurations, i.e. **all keys, all periods, all phases at once** | 11 complete crib digraphs are available; a genuine Slidefair satisfies 11/11 (chance 26⁻¹¹ = 2.7 × 10⁻¹⁶). **Best observed 2 of 11**, expected best 0.42 | `k5_genealogy.md` §1.3 |
| **Portax** | key-free row-parity invariant (`#TOP(ct pair) = 2 − #TOP(pt pair)`) + inheritance: Portax is position-preserving and its substitution is indexed by ciphertext position, so every one-stage negative transfers | closed. *Correction on record:* Portax **does** permit self-encipherment (degenerate same-column case), so the S→S/K→K argument does **not** close it — the inheritance argument does | `k5_genealogy.md` §1.4 |
| Enigma (all models incl. M3, M4, Zahlwerk, Abwehr), Typex, any reflector machine | structural | **excluded with certainty, no search meaningful.** Such machines have no fixed points; P(≥1 self-map in 24 crib letters) = 0 exactly, and 2 are observed. *Honest caveat:* this is contingent on the announced crib positions — 67–83 % of random placements of a single crib word are self-map-free | `matrix_e_output.txt` |
| Homophonic and polyphonic substitution (fixed table, any number of homophones, cycling homophones) | structural | **impossible in both directions.** 9 ciphertext letters would need ≥2 plaintext values, 8 plaintext letters come from ≥2 ciphertext letters; and a 26-symbol ciphertext alphabet, all 26 used, cannot carry homophones at all | `matrix_b_output.txt` B2–B3 |
| Nomenclator / codebook / hybrid "cipher for text, code groups for names" | structural + arithmetic | **refuted at the only four places it is observable.** All four cribs are exactly length-matched (4/4, 9/9, 6/6, 5/5); fixed group length is impossible, uniform {2..4} impossible, uniform {2..10} gives P = 1.5 × 10⁻⁴. The three non-crib gaps are 21, 29, 23 with **gcd 1** — no uniform group length ≥ 2 tiles them. 3 of the 6 doubled letters lie inside cribs and decrypt to ordinary pairs (NO, ST, IN), so doubles are not group markers | `matrix_c_output.txt` |
| Straddling checkerboard / VIC | digit-count identity `S_pt = S_ct` (every VIC stage is length-preserving); CSP over key periods 1–30 for 5- and 6-cell short rows | **excluded by composition.** The largest `S_ct` any 8-letter ciphertext short row can reach is 45 (46.4 % of the text) against **E[S_pt] = 61.7** for a standard English board, z = −3.50; the device is a compression tuned to English and K4's flat letter distribution cannot absorb the digits. CSP: UNSAT at every period 1–30 except 27 and 29, where the chance baseline is 0.08–0.09 SAT/period | `matrix_a_output.txt` |

### 3.B Digraphic, fractionating and matrix systems

| family | scope | outcome | source |
|---|---|---|---|
| Playfair, two-square, four-square, any 5×5 Polybius system | structural | **impossible.** K4 emits all 26 letters; a 25-cell square emits at most 25. Playfair additionally: no self-maps (S→S, K→K), and it cannot emit a doubled digraph (QQ at 26–27, TT at 68–69 would be required) | `families.md` §3 |
| Seriated digraphic at width 21 | structural (Bean) | **impossible.** BERLIN→NYPVTT forces two different bigrams, one ending I and one ending N, both to encipher to `ZT` | `prior_art.md` A.3 |
| Bifid 5×5 and 6×6, trifid — keyword squares | 16 keywords × periods 2–30 | best 5/24 (chance ≈ 1/trial) | `families.md` §3 |
| Bifid 5×5 / 6×6 and trifid — **unknown square, solved as a CSP over the square itself** | all **25! = 1.55 × 10²⁵**, **36! = 3.72 × 10⁴¹**, **27! = 1.09 × 10²⁸** squares, periods 2–97 | **UNSAT at all 96 periods in every case.** Validated by synthetic-square recovery (the solver recovers a planted square from the 24 crib letters) and by contradictory-crib UNSAT | `matrix_d_output.txt` |
| Conjugated-matrix bifid (two independent unknown squares, 25!² = 2.4 × 10⁵⁰ and 36!² = 1.4 × 10⁸³) | periods 2–97 | 2 and 3 SAT of 96 periods, against random-crib baselines of 0.017 and 0.065 SAT/period (1.6 and 6.2 expected). The SAT decryptions score quadgram **−7.29 to −7.63** against a random median −8.24 and 99th percentile −7.92: **noise, and the model is underdetermined by construction** | `matrix_d_output.txt` |
| Classic ADFGVX / ADFGX | structural | **impossible twice.** The ciphertext would use 6 (or 5) letters; K4 uses 26, 78 of 97 outside {A,D,F,G,V,X}. And ADFGVX output length is even; 97 is odd | `matrix_f_output.txt` F1 |
| 26-letter ADFGVX generalisation (fractionate → columnar → recombine), unknown square | every columnar key of width 2–7 (**5,912 keys**) × 5×5 and 6×6 squares, 48 active crib constraints each | **0 SAT / 11,824 configurations** | `matrix_f_output.txt` F2 |
| Conjugated-matrix ADFGVX (two unknown squares) | same 5,912 keys | 99 SAT (5×5) and 130 SAT (6×6) — but against chance baselines of 0.0073 and 0.0018, and every decryption is gibberish (best −6.91). The counting argument explains it: a 6×6 square is 138 bits and the cribs supply 113 | `matrix_g_out.txt` |
| **Hill 2×2 and 3×3**, linear and affine, both directions, both alphabets, all block alignments | full row-wise brute force over 26ⁿ and 26ⁿ⁺¹ per row | **every row has zero solutions in every configuration.** The famous `HILL` reading in the tableau's last column is separately explained away in §3.C | `families.md` §4 |

### 3.C Key-source hypotheses — "the key is somewhere on or around the sculpture"

| hypothesis | scope | outcome | source |
|---|---|---|---|
| Running key from the sculpture's own texts | **66 texts** (K1/K2/K3 plaintexts and ciphertexts, the whole left panel, the physical and ideal tableau, tableau rows, Morse in two orders, keywords; reversed and X-stripped copies) × 24 cipher/alphabet combos; 720,576 + 723,744 + 658,512 block comparisons, and 17,121,312 joint comparisons over all 26 key-alphabet rotations | **0 exact hits, 0 within Hamming 2.** Best joint 16/24 mismatches where a solution is 0 | `runningkey.md` §1–2 |
| Repeated prefix / arbitrary repeated block from those texts | 143,472 + **18,290,064** tests | 0; best 7/24 then 8/24 | `runningkey.md` §4 |
| **Lateral key material** — Mengenlehreuhr (163 streams), Urania-Weltzeituhr (5), compass rose and bearings (7), Cyrillic Projector (10), Antipodes Cyrillic (9), Berlin-Wall timestamps, Alexanderplatz | 194 streams, 128 long enough to test; **48,697,953 alignments** as running keys, periodic keys, Gronsfeld digits, digit-pairs mod 26 and one-bit alphabet gates, all 24 combos × 26 rotations | **0 survivors, no false positive possible** (E[perfect fit] = 5.3 × 10⁻²⁷). Best block-1 7 of 13 matched (E[#that good] = 2.9), block-2 6 of 11 (E = 21.0), joint 8 of 24 (E = 31.1), periodic 6/24 (E[# ≥6] = 24.4). No binary gate state forces a single shift | `lateral/INDEX.md` §2, `lateral/berlin_clock.md` §4 |
| The tableau as a **2-D key table / coordinate lookup** ("LAYER TWO") | **collapse theorem**: every carved body cell equals `KEYED[(row+col) mod 26]` with **zero exceptions**; then the full affine lookup family `row = r0+p·i mod mr`, `col = c0+q·i mod mc` — **88,248,160 coordinate models × 24 combos × 26 rotations = 55,066,851,840 trials solved exactly by hash join in 2.0 s**; plus 13 constant-step walks, alternating knight moves, label/header grids, serial readings (20.7M further trials) | **0 solutions.** And the theorem explains why it had to fail: 780 cells hold exactly **26 distinct values**, so any coordinate lookup *is* a position-dependent shift — a family already exhausted. Best model anywhere 10/24 where chance gives 4.09 | `tableau.md` §2 |
| The tableau **anomaly** (the extra `L`) as signal | deviation set has **cardinality 1** (position 465) carrying **14.46 bits** where a 97-letter key needs 456 and the crib block 113; every selector role swept: constant shift, 15 candidate periods, decimation (1,164,576 trials), Gronsfeld, all 96 interior switch points in 4 model families (1,126,656 models), **phase-slip running keys (20,885,760 trials)** | **0 hits; 23.3M trials; every best at or below chance** (phase-slip best 9/24 against **77 expected** at that level). The collapse theorem also reclassifies the anomaly: `KEYED[(13+30) mod 26] = L` is exactly what is carved, so the extra L is **the right letter in an extra column** — a miscount, not a plant, and `HILL` survives only as a coincidence of where the row stopped | `tableau.md` §1–2 |
| Tableau column and row-label sequences as key streams | 41 streams + 130 K4-aligned label variants, as running keys and as periodic keys of every period; 2,582,760 trials | 0; best 8/24 (E[# at that level] = 10.5); identical chance-level 16/24 joint Hamming to the lateral sweep. *(These had never been tested: the registered `tab_*.txt` files were deleted from `lateral/keystreams/` before `test_lateral.py` ran, so they were regenerated in-process here)* | `tableau.md` §4 |
| **"YES, WONDERFUL THINGS"** — the Carter/Carnarvon reply the sculpture withholds, absent from the 66-text corpus | 16 phrases as explicit key streams (6,264 tests), as 34 keyword-mixed alphabets over periods 2–30 (100,572 tests), as running keys (162,864 tests) | best 6/24; 5,510 crib hits against **5,782 expected** (below chance); 10,646 alphabet survivors against 10,671 expected, all at c ≤ 1; best joint Hamming 16/24. **The best-motivated untested key text there was** | `k5_genealogy.md` §4.4 |
| Cross-section key continuation (PALIMPSEST/ABSCISSA/KRYPTOS running across section boundaries into K4) | **proved a corollary**, not an open question: `k_i = W[(s+i) mod L]` is periodic with period L, so the period-L test already quantifies over every keyword of length L at **every** phase, and alphabet rotation is absorbed into the key. Explicit runs anyway: 1,176 + 2,496 + 1,344 + 6,384 tests over all 13 defensible cumulative counts | periods 7/8/10/18/25 return 0 survivors at c = 17/16/14/7/3; explicit best 5/24 with 1,045 hits against 1,085 expected | `k5_genealogy.md` §3 |
| K3's double rotation applied to the **key stream** (rather than the text) | 12,224,976 tests | best 9/24; **0** reaching 12/24 | `k5_a_output.txt` S4 |
| OBKR as an **indicator group** | 7 rule families: direct keyword + 7 transforms; the proper 1940s enciphered-indicator rule yielding **1,270 distinct message keys** (243,840 tests); numeric Gronsfeld; decimation with step from OBKR; **416 tableau walks** from OBKR-named cells on both squares; chain-addition Gromark primers; 20 OBKR-keyed alphabets — 303,648 tests | every stratum at or below chance. Best **7/24**, which resolves to **one** correlated observation (the ideal and carved tableaux differ by one letter), p ≈ 0.21 before correcting for six strata. Also proved: a 4-letter indicator addresses at most 26⁴ = 456,976 message keys against a crib-perfect key space of 26⁷³ | `k5_genealogy.md` §5 |

### 3.D Position and geometry models

| hypothesis | scope | outcome | source |
|---|---|---|---|
| Position-dependent shift models | **90,641,136 models** in 10 families: linear, quadratic, cubic, triangular, sawtooth (37.1M), block (37.1M), `a·row+b·col+c` widths 2–48 (9.3M), width 31, bilinear (6.5M), K2-coordinate Gronsfeld | **0 fitting 24 cribs**; best **9/24**, where P(random model ≥ 8) = 2.0 × 10⁻⁶ | `geometry_1_out.txt` |
| Every plausible physical reading order of the 4+31+31+31 block | **274 orders** (row/column-major in 4 directions, boustrophedon, both diagonal families, 16 spirals, all 6 row orders × reversals × 4 OBKR placements, body-only variants) × periods 2–26 × 12 pairings = 82,200 tests | 104 consistent against **141 expected**; all at c ≤ 1; **none with ≥3 real constraints**; best revealed-text unigram −3.504 against −2.90 for English | `geometry.md` §2 |
| Column-read rearrangements | 4,703 rearrangements × periods 2–48 × 12 pairings = **2,652,492** tests | 0 consistent at c ≥ 3 (8.5 expected at c = 3); nothing above chance anywhere | `geometry.md` §1 |
| A key indexed by **absolute panel position** | closed *a priori* by an offset theorem (a constant offset is a bijection on Z_p, so the residue partition cannot change) — verified over p = 2–60 × all 869 alignments, **51,271 partitions identical, 0 verdicts changed** | **every repeating keyword of length ≤ 60 at every one of the 869 panel alignments is ruled out**, PALIMPSEST and ABSCISSA included; the polynomial shift families are closed under the same shift | `geometry.md` §3.1 |
| A single panel-wide positional key, tested as a **prediction** from K1+K2's 424 known pairs | uniform widths 2–500 (5,988 cases), per-physical-column, per-physical-row, `a·row+b·col+d` (210,912 models), and continuing K1/K2's own keys into K4 (600 combinations) | 924 cases are self-consistent on K1+K2 and **0 predict all 24 cribs**; aggregate prediction accuracy **0.037 against 1/26 = 0.038**; physical columns 0/12 self-consistent (369 of 424 letters conflict); best `a·row+b·col+d` 7/24; best key-continuation 4/24 | `geometry.md` §3.3 |
| 97 ± 1 — a missing or extra carved letter (the K2 failure mode) | insertion at each of 98 slots (31,392 tests) and deletion of each of 73 non-crib letters (23,652 tests), p = 2–31 × 12 pairings | **0 consistent** against 70.4 and 55.9 expected. The special case that would make K4 **98 = 7 × 14** — the one reading in which a 7-wide grid is exact — fails cleanly (p = 7: 17 constraints, 0/12; p = 14: 11 constraints, 0/12) | `geometry.md` §6 |
| 31- and 93-based structures (one key per 31-letter block, a 31-length key on the 93-letter body, the 3×31 grid in all 8 orientations) | body periods 2–93, 2,880 grid tests | no period with ≥1 constraint has any consistent pairing; the 31-key on the body fails 12/12 on its 2 constraints; "the real message is 93 letters" is **invisible to the cribs** (c_p identical to the 97-indexing at every period) | `geometry.md` §6, `k5_genealogy.md` §5.1 |
| Lag-7 period structure | full 96-lag spectrum, 10⁶ replicates; plus the additive and the **general** period-7 polyalphabetic | the spike is noise (§4); and no period-7 key can exist anyway — 17 constraints, all 12 pairings inconsistent, every one of the 7 residues individually conflicted | `geometry.md` §4–5, `statistics.md` §5 |
| **Alphabet-free impossibility** (general periodic polyalphabetic, each slot an arbitrary independent mixed alphabet) | the only crib constraint is that within a residue class the ct→pt map is a partial bijection — so a failure kills **every alphabet set that exists** | periods **2, 3, 4, 5, 6, 7, 9, 10, 14, 15, 17, 21, 25 are impossible outright**; under the chart model `C[i]=g_i(P[i])` the refuted set extends to **{1,2,3,4,5,6,7,9,10,14,15,17,21,25,34,42,43,45,50}** (22 crib pairs conflict, separations {1,3,4,5,7,9,34,42,43,45,50}); across 186 reading orders, periods 2–5 die for **every** order | `geometry.md` §5, `k5_genealogy.md` §2.5, `seg_h_out.txt` |
| **Periods 27–57, attacked from the plaintext side** (the crib-blind region) | the cribs still *pin* key letters: at p = 27 only 3 letters are free (26³ = 17,576 decryptions, exhaustively searchable), rising to 29–36 free letters at p = 53–57; coordinate descent validated against exhaustive search at p = 27 and by synthetic recovery | **p = 30–52 are refuted by the cribs outright** (24/24 combos impossible). At p = 27, 28, 29, 53–57 the best achievable English score is **−1.43 to −1.50** and **−1.07 to −1.17** against a crib-pinned null of −1.28 to −1.69 — an excess of only +0.13 to +0.26 — where real English is **−0.741 ± 0.077** and Sanborn's own plaintext is **−0.967 ± 0.087**. No periodic key at any period ≤ 57 produces English | `search_periods_out.txt` |

### 3.E Two-stage and multi-stage systems

| hypothesis | scope | outcome | source |
|---|---|---|---|
| **Transposition *before* substitution, ciphertext reading** | argument, not search | **closed for all 97! transpositions.** Under this reading the substitution is indexed by ciphertext position, so the 24 crib pairs are *untouched* by the transposition and every one-stage negative transfers verbatim | `twocipher.md` §1 |
| Substitution then transposition, ciphertext reading | 1,172,862 catalogued transpositions → 1,138,449 distinct permutations; 750 keep the crib words contiguous; periodic battery over all 917 distinct crib-position tuples; plus 985,600 free-offset tests | **1 non-vacuous survivor with a single check**, decrypting at quadgram −7.29 (not English); offset counts track the null exactly | `twocipher.md` §2 |
| Substitution then transposition, **plaintext reading** (the one door the cribs can open) | **726,578 distinct crib images × 24 combos = 17,437,872 forced key streams**, plus 1,327,758 images from **2,449,225 two-transposition compositions** = 31,866,192 more, plus 132,408 from 5,517 K3-style transpositions — ≈ **49.4 M forced key streams**, each tested for periodicity (p = 1–60, 13.1 M tests), for exact occurrence in 3,432 corpus text variants, and for English | **0.** Periodicity: 2 survivors at p = 34 against 1.51 expected across the 39 periods with ≥5 checks. Corpus: **0 exact 13-gram, 11-gram or joint hits**. English: best quadgram −6.699 against a matched control whose own maximum is −6.809. Per-block dictionary test: **no key block contains any English word of ≥10 letters** (0.02 expected) | `twocipher.md` §3 |
| Double substitution with two independent keys | meet-in-the-middle deciding **111,007,296** configuration pairs exactly (43-word Kryptos list, every ordering, phase, family, alphabet arrangement), plus **13,148,928** tests covering *any* key word of length ≤ 26 at every phase opposite a known key | **0**, against 1.2 × 10⁻²⁶ expected. The named hypothesis (PALIMPSEST then ABSCISSA, Quagmire III) agrees with the required intermediate in **0 of 24** positions. The free-key sweep gives 9,838 consistent against 9,740 expected, **0** of which imply a dictionary word | `twocipher.md` §3(c) |
| Two transpositions then substitution | 2,449,225 compositions; 470,800 configurations in the CT-reading | 16 survivors with ≥1 check against **221.5 expected** — below chance | `twocipher.md` §3(d) |
| The **K3 procedure itself**, derived from the data and applied to K4 | K3's transposition re-derived (rows of 8, columns right-to-left, then rows of 24, again — **keyless**; the "KRYPTOS = 0362514" column key is decoration, not necessity); 5,517 K3-style variants applied to K4 | best quadgram −8.32 / −8.10 (noise); 1 chance-level survivor | `twocipher.md` §3(b) |

### 3.F Irregular, interrupted and segmented keys

| hypothesis | scope | outcome | source |
|---|---|---|---|
| Trigger-driven key advance ("skip rules": HOLD, DOUBLE, RESET_AFTER, ADVANCE_ONLY, RESET_AT) on ciphertext triggers | 8,000 (variant, trigger, delay, period) tests × **867 cipher configurations = 6,936,000** | 22,828 survivors against **22,130.7 expected**; the single survivor at c = 3 is at the chance rate | `seg_c_out.txt` |
| The same, on **plaintext** triggers (the pointer path known inside each crib run, both run-start offsets enumerated) | 931,425 tests × 867 configs = **807,545,475 configurations** | 8,906,578 survivors against 8,788,865.7 expected (ratio **1.013**); **0 survivors at c ≥ 5** | `seg_e_out.txt` |
| Key-driven interruptor (ACA "interrupted key", interruptor on the key letter) | every subset of Z_p, p = 2–14: 65,515 subset tests, **56,801,505 configurations** | **0 survivors**, 0 expected | `seg_e_out.txt` E3 |
| Interrupted periodic key: one or two inserted/deleted key letters at unknown positions | D1 807,177 and D2 **19,784,073** configurations; plus free desync between the two crib runs (303,450) | **0 survivors** in D1 and D2; D0 5,567 against 5,483.6 expected, none at c ≥ 4 | `seg_d_out.txt` |
| Segmented cipher — each segment its own family, alphabets and period | panel rows, halves, thirds, crib blocks; 867 configurations available to each segment independently | 0 joint survivors wherever any constraint exists. Note the structural point: a segment containing no crib is unconstrained **by construction**, so its plaintext is whatever you choose — such models are not testable, not passing | `seg_b_out.txt`, `seg_f_out.txt` |
| The correct null for a crib-fitted candidate | 97-letter texts with the 24 crib letters planted score quadgram **−7.359 ± 0.115**, against −8.230 for pure random | **every candidate any `seg_*` script starred sits at or below the mean of its own planted null** (best −7.197, z = +1.41, below the best-of-N threshold). The stars were artefacts of comparing against a pure-random null | `seg_f_out.txt` F1 |
| Gold-standard null for the forward-simulation sweep | 15 uniform and 15 shuffle replicates of the entire 673,297-simulation sweep | real K4 max quadgram **−7.1377**; uniform null mean −7.1326, **7 of 15 replicates beat it (p = 0.500)**; shuffle p = 0.375. The sweep found nothing | `seg_g_out.txt` |

### 3.G Structural and indexing hypotheses (challenging the assumptions)

| hypothesis | scope | outcome | source |
|---|---|---|---|
| **Are the crib positions right?** | primary sources retrieved and quoted; 9 indexing conventions tested; then **68,491,350** placement/variant × period × combo tests: global slides δ = −21…+23, both phrase blocks slid independently, all four words slid independently, and the **complete free slide of both phrases over all 97 positions** | **The positions are verified, not inherited.** The 2010 release states *both* an index range and the ciphertext letters (`64th through 69th … read NYPVTT`), and only one convention satisfies both. Across all 68.5 M tests the **highest-constraint survivor anywhere carries c = 4** (1 observed against 3.53 expected); **every stratum c ≥ 5 is empty**. A correct placement would sit at c = 22 | `crib_placement.md` |
| Sanborn counted K3's `?` (δ = −1), or a letter was dropped (δ = +1) | documentary + 867-alphabet sweeps | refuted documentarily (`?`+K4 at 64–69 reads **BNYPVT**, not NYPVTT) and cryptanalytically (all survivors at period 26, c = 1) | `crib_placement.md` §3, `k5_genealogy.md` §4.1 |
| The `?` as a **key slot** (98 cells) | proved subsumed: shifting every crib position by a constant *d* shifts every residue by the same constant, so the partition and c_p are unchanged — verified d = 0…8, p = 2…40, **0 exceptions** | closed | `k5_genealogy.md` §4.2 |
| K4 **begins before OBKR** (K3's tail is the head of the message) | 4 tail sources × k = 1…40 × periods 2–30 × {12, 867} alphabet combos = **4,078,560** tests (1,005,720 per source at 867 combos) | 106,778–106,814 survivors against 106,710 expected; **max c carrying any survivor = 1** everywhere (a solution appears at c ≥ 10) | `k5_genealogy.md` §4.3 |
| The crib **words** are misspelled, separated by X/Q, or part of longer phrases | 124,271 variant pairs (X/Q separators, Sanborn-style misspellings, German renderings incl. MENGENLEHREUHR/WELTZEITUHR, every single-letter mutation of both phrases, partial cribs) — 37,281,300 tests in the full cross-product plus 27.2 M single-substitution tests | **nothing**; max c = 4 with 1 observed against 3.53 expected | `crib_placement.md` §4 |
| "The plaintext is deliberately misspelled, that is why nothing looks like English" | measured on Sanborn's own three misspellings | **quantitatively dead**: IQLUSION costs 0.10, UNDERGRUUND 0.14, DESPARATLY 0.02 quadgram units. The English-to-random gap is **3.5**. Misspelling tolerance cannot rescue a search that is 3.5 away | `crib_placement.md` §4.1 |
| Plaintext-positions vs ciphertext-positions reading of the clues | 240 random position-keyed ciphers across 12 combos | **the two readings are identical for every position-preserving cipher** (240/240), so the question is vacuous for nearly everything ruled out. It has teeth only when a stage moves letters, and 3 of those 4 cases are closed; the fourth (T-then-S under the plaintext reading) is **crib-free**, i.e. untestable rather than open | `crib_placement.md` §5, `twocipher.md` §1 |
| **The K5 inference** — "K5 sharing coded words at shared positions shows the system is positional and argues against autokey" (README §3.4, constraint C10) | four theorems, each verified by construction (400–4,000 trials each) | **WITHDRAWN AS UNSOUND.** Under one positional chart, `C4[i]==C5[i] ⟺ P4[i]==P5[i]`, so the ciphertext reading and the plaintext reading are the *same statement* and the inference affirms the consequent (0 failures in 400 trials). Autokey with a shared primer *produces* agreeing ciphertext prefixes (0 failures in 400). With a second chart the statement is vacuous — a pair with P4 ≠ P5 everywhere in 64–74 yet identical ciphertext there was constructed explicitly | `k5_genealogy.md` §2 |

### 3.H Families that are *not* ruled out, because the cribs cannot rule them out

These are recorded so nobody mistakes a counting artefact for a lead. In each case the key
entropy exceeds the **113 bits** (24 × log₂26) the cribs supply, so consistent settings are
guaranteed to exist and finding one proves nothing.

| family | key entropy | consequence |
|---|---|---|
| M-209 / C-38 (the machine Scheidt's generation trained on) | 278 bits (131 pins + 120 lugs + 27 offsets); pin-wheel lcm 101,405,850, so aperiodic over 97 letters | ~2^165 crib-consistent settings. **Unfalsifiable from cribs.** Note it is a Beaufort machine, so the two self-maps are no objection |
| SIGABA | ~2^95 | same |
| Wide-key ADFGVX (historical widths 15–22) | 138-bit square + 40-bit key, or 1,200 bits for a free permutation of the 194-symbol stream | same; only widths 2–7 are settled |
| 10×10 monome-dinome (26 letters in 100 cells) | 168 bits + key | SAT at exactly the periods the random-plaintext baseline predicts. The model is **not total** (74 % of shifts land on an empty cell), which is itself the finding |
| A free per-position chart `C[i] = g_i(P[i])` | 456 bits | **26⁷³ = 1.96 × 10¹⁰³ key streams fit all 24 cribs exactly**, for each of the 24 cipher/alphabet combos. Everything this repository has ever searched totals ≈ 6.4 × 10³⁶, i.e. **3.26 × 10⁻⁶⁷** of the crib-perfect positional space |
| Any periodic key with p ≥ 58 | ≥ 34 free letters after the cribs pin the rest | **provably beyond testing**: there are ≈ 10⁵⁵ crib-consistent English plaintexts out of 26⁷³ = 10¹⁰³·³, a dilution of 10⁻⁴⁸·³, so 26^free ≥ 10⁴⁸·³ supplies English-looking decryptions by chance alone. Any "solution" found there is a fit, not a finding |

---

## 4. What the statistics actually establish

`statistics.md` recomputed every statistic ever used to argue about K4 against a properly
calibrated null, using exact distributions where a closed form exists and 14.6 M Monte-Carlo
replicates where not. All machinery is validated (exhaustive-enumeration check of the IoC lattice
DP; closed-form vs MC moment checks; cipher round-trips; Quagmire-III re-encryption of K1
reproducing the carved ciphertext).

**Headline: at n = 97, K4's ciphertext is statistically indistinguishable from a uniformly random
string of letters. Every published "anomaly" dies once the selection that produced it is paid for.**

| claim on record | corrected number |
|---|---|
| "IoC 0.0361 is below uniform random 0.0385 — the masking is visible" | **Exact** P(IoC ≤ 0.036082 \| uniform, n = 97) = **0.215723** by lattice DP (10⁷-draw MC: 0.215599). z = −0.84, **21.6th percentile**. A two-sided 95 % interval for a random 97-letter string is [0.03372, 0.04467] |
| "All 26 letters in 97 characters is unusual" | exact coupon-collector P = **0.542** — the majority outcome; distinct-count mean 25.42, sd 0.72, so 26 is +0.80 σ |
| "Six doubled letters is high" | exact Binomial(96, 1/26): mean 3.692, **P(≥6) = 0.165**. K2's ciphertext has 21 doubles against 14.15 expected (z = +1.86) — and K2 is solved |
| "Doubled letters cluster mod 7 (five of six ≡ 5)" | nominal 0.0022 → **corrected p = 0.245** over moduli 2–48 (10⁶ trials). The related "7×14 last two columns" claim is indexing-dependent: the doubles sit in 0-indexed columns 4,4,4,0,4,4 |
| "Autocorrelation spike at lag 7, z = +3.04" | family-wise **p = 0.219** (lags 1–48) / **0.557** (lags 1–96, the range actually searched). The null mean of max-z over lags 1–96 is **+3.257** — K4's +3.04 is *below the average maximum of a random string*. Controls: K1 max-z 4.24 (p = 0.034), K2 5.38 (p = 0.0001), K3 7.42 (p < 0.0001) — **every solved section spikes harder than K4** |
| "Periodic-IoC peaks at periods 25, 28, 30" | artefact of the collapsing within-column pair count D(p) (at p = 28, D = 246 and the null sd is 0.0173). Standardised: p = 25 → **+1.13**, p = 28 → **+0.13**, p = 30 → **−0.13**; family-wise p of K4's maximum over p = 2–48 is **0.9913** — K4 is *flatter* than 99 % of random strings |
| "Excess column bigrams at width 21" (Bean, the strongest published anomaly) | nominal reproduces (11 observed, 1 in 2,900 on the excess convention) but **selection over widths 2–48 kills it**: corrected p = **0.090–0.419** depending on convention, against a best-of-47-widths null mean of 8.7–10.4 versus K4's 11. Also: the nominal figure moves by a factor of 5 between two equally natural counting conventions that both give 11 on K4 |
| "Seven of ten bigram gaps share a factor" | conditioned on exactly 10 gaps: **p = 0.197 / 0.205** |
| "Zero repeated trigrams shows a long key" | a random 97-letter string has no repeated trigram **78 %** of the time. Zero is the ordinary outcome; Kasiski has nothing to work on (gcd of the ten bigram gaps = 1, no factor enriched, **no excess at 7**) |
| **omnibus over the whole classical battery** | min-p over 7 statistics against a one-time-pad null: **p = 0.414** (periods 2–30 for the periodic statistic) |

**What the statistics *do* exclude**, at overwhelming significance, driven by the IoC: raw English
plaintext, **pure transposition of English**, monoalphabetic substitution, and Vigenère key length
1–2 (3–5 disfavoured). Everything else — Hill 2×2, Vigenère/Beaufort/Quagmire-III with L ≥ 7,
general polyalphabetic, running key, both autokeys, Gromark, and a one-time pad — produces K4's
profile with p between 0.10 and 0.44 and is **mutually indistinguishable at this length**.

**The power boundary, which is the real result.** 200,000 simulated encipherments per key length:
the plain IoC test has ≥ 50 % power only for **L ≤ 4**; the periodic-IoC test *told the true
period* reaches **L ≤ 26**; the periodic-IoC test as actually runnable — scanned over p = 2–48 and
multiple-testing-corrected — has ≥ 50 % power only for **L ≤ 8**, and ≤ 16 % power at periods 27,
28, 29 and ≥ 53. **The statistics have power exactly where the cribs already impose 11–22
constraints, and no power exactly where the cribs impose none.** Those periods are not "ruled out
by statistics"; they are unexamined by both tools simultaneously — which is why §3.D closes them
by direct English maximisation instead.

**Operational consequence.** Do not use K4's ciphertext statistics as a search signal, a fitness
function, or a filter. A search that prioritises candidates for "explaining the lag-7 spike", "the
width-21 column bigrams", or "the sub-random IoC" is fitting noise. Use statistics on the
**plaintext** side, where they have real power: at n = 97 a quadgram score separates English from
uniform random with **zero overlap** (English 1st percentile −4.614; maximum of 200,000 uniform
strings −7.243), and Sanborn's own plaintexts sit inside the English distribution.

**Corrections this forces on the repository's own record** (not yet applied to those files):
`README.md` §3.1 calls the sub-random IoC "the central fact about K4" and gives the lag-7
multiple-comparison p as "roughly 0.03" — the correct family-wise values are 0.109 (lags 1–24) and
0.557 (lags 1–96). `prior_art.md` §A.6 and its recommendation 3 ("treat the width-21 excess as the
live phenomenon") should be **withdrawn**: corrected p is 0.09–0.42 and there is nothing to explain.

---

## 5. Surviving candidates

**None. There is no surviving candidate decryption, and no surviving method hypothesis with
positive evidence behind it.**

The four "best" results anywhere in the effort, stated so they can be dismissed rather than
rediscovered:

| what | crib fit | chance expectation | verdict |
|---|---|---|---|
| Tableau boustrophedon walk from cell (O,K), KRYPTOS-index coordinates | 7/24 | 0.24 tests expected at ≥7/24 over 9,984; **2 observed, but the ideal and carved tableaux differ by one letter, so this is ONE observation** → p ≈ 0.21 before correcting for six strata | noise; 17 crib letters short |
| Recovered message key BQHM (OBKR deciphered under a standing key) as a period-4 body key | 6/24 | **58.33** expected at ≥6/24 over 243,840 tests; **14 observed** — four times *fewer* than chance | noise |
| YESWONDERFULTHINGS at phase 8 as an explicit key stream | 6/24 | total crib hits 5,510 against 5,782 expected | noise |
| Best model in the whole tableau-lookup sweep (`full28_ideal`, affine coordinates) | 10/24 | **4.09** models expected at 10/24 in that sweep; 1 observed; its decryption scores bigram −7.34, *worse than a random string* | noise |

**Public claims, audited mechanically.** None is a solution:

| claim | cribs applied mechanically | non-crib text | independently derivable? |
|---|---|---|---|
| **solvekryptos.com** (`THE COMPASS ROSE IS HERE X EAST NORTHEAST THIS IS YOUR POSITION X COMMISSION BERLIN CLOCK WHICH IS NORTHEAST OF HERE X`) | 24/24, 97 letters | English, and **inside the band of real Sanborn plaintext** (quadgram −0.941 against Sanborn's −0.967 ± 0.087) — so it is *not refutable on English-likeness* | **No, and mechanically proved so.** Its f/g incidence graph is a **forest** (108 nodes, 97 edges, 11 components, **0 cycles, 0 duplicate edges**) under every convention for the blank at position 67, so the system fits *every* plaintext: **20,000 of 20,000 uniformly random 97-letter plaintexts are exactly realisable**. Fitted to public data alone it forces **0 of the 73 unknown letters** (73 = 97 − 24). Its 97 gate bits are 97 fitted parameters — a permutation null beats the real gate map 120 times out of 120 (p = 1.000). Its helper packet is genuinely derivable for positions 1–66 and **authored for 67–97** (the footer row has 30 letters, not 31). The site says the mechanism is back-solved; this audit agrees |
| **mattklepp/k4** | 24/24 | gibberish | No. 24 "position-specific corrections" that are *identical* to the residuals at the 24 published positions: 24 free parameters fitting 24 data points, zero residual degrees of freedom. Repository now 404 |
| Naughton / Grok-3 | **1/24** (0 of 2,400 variants fit) | — | recipe public and wrong |
| "Scott" Quagmire III + `y = 77 + 38x mod 97` | **1/24** literal; best 7/24 over 37,248 variants where chance predicts 0.9 at that level | — | yes, and it fails the CLOCK crib that was already public when proposed |
| Hörenberg XOR / mod-5 (DYAHR) | does not reach the cribs | — | **Sanborn explicitly told him his first ten letters were wrong** — the only specific negative Sanborn has given on a specific proposal |
| ChatGPT / LLM claims, figshare "Genie", "Structured Solution" video | 0–24/24 but all short of 97 letters, or no procedure published at all | — | no method |

**Verification verdicts on this round's findings.** Only one line of attack carries recorded
adversarial verdicts: three independent agents re-derived `statistics.md` from scratch, writing
their own code and nulls (`analysis/vfy_statistics_adversarial.py`, `adv_verify_stats_*.py`,
`vadv_statistics_english.py`).

* **All three returned NOT REFUTED.** Every exact figure reproduced to 4–7 digits (IoC lower tail
  0.215723 vs 0.215723; coupon collector 0.542462; doubles 0.165112; width-21 and lag-7 family-wise
  values to ±0.002).
* **One real defect, found by all three independently and worth propagating:** the omnibus battery
  scans the periodic-IoC statistic over periods **2–30** while the same report scans **2–48**
  elsewhere. With 2–48 that statistic's two-sided p is 0.019 rather than 0.127 and the omnibus
  falls from **0.414 to 0.070**. The headline conclusion survives (0.070 is still not significant,
  and the driver is K4 being *flatter* than random, which is not exploitable), but the honest
  statement is **"omnibus p ≈ 0.07–0.13 depending on a defensible scan range, not 0.41"**, and
  confidence should be **high on the conclusion, medium on the exact number**.
* One stated reason in that report is wrong even though its conclusion is right: adding the raw
  width-21 count to the battery **lowers** the omnibus to 0.015 (it is only the *selection-corrected*
  maximum over widths that raises it to ~0.45). Adding an uncorrected post-hoc statistic as if
  pre-specified is precisely the fallacy the report exists to expose.
* Controls the original lacked, added and passed: the omnibus is correctly calibrated (a one-time
  pad rejects at 0.045 for a nominal 0.05) with power 1.00 against English and pure transposition,
  0.91 at L = 3, 0.45 at L = 8, 0.19 against autokey — consistent with the power boundary above. A
  strictly more powerful Mahalanobis omnibus over the full 7×7 null covariance gives p = 0.108.

No other finding in this round has been through an adversarial pass. Treat the tableau collapse
theorem, the Slidefair invariant, the K5 theorems and the subsumption proofs as *verified by
construction inside their own scripts* (each ships planted-cipher recovery and perturbation
rejection) but **not independently replicated**.

---

## 6. The strongest remaining directions, ranked

Each with a concrete first step. Ranking is by expected information per unit of effort, not by
how appealing the hypothesis is.

**1. The pre-registered K5 aligned-run experiment. Highest value by a wide margin; costs one
minute on publication day.**
*First step:* monitor `paradigm.xyz/kryptos`. The moment the K5 ciphertext appears, run
`k5_b_depth.align_runs(C4, C5)` and apply the decision rule fixed **in advance**: exact chance
values are P(some aligned run ≥ 4) = 1.98 × 10⁻⁴, ≥ 5 = 7.53 × 10⁻⁶, ≥ 9 = 1.58 × 10⁻¹¹, and
E[aligned matches] = 3.73 (sd 1.89). A run **≥ 5** establishes one shared positional chart plus
shared plaintext there; a run **≥ 9** is decisive and is almost certainly a released crib word;
**no run ≥ 4 anywhere** confirms two charts and kills the depth attack; **≥ 10 isolated matches
with no long run** would mean two charts sharing individual columns, which neither published
reading anticipates and would be the most informative outcome of all.
*Falsifiable prediction to check first:* if there is one shared chart and the shared words are the
released cribs, K5's ciphertext must read literally `FLRV` at 22–25, `QQPRNGKSS` at 26–34,
`NYPVTT` at 64–69, `MZFPK` at 70–74.
*And know what it is worth:* if the chart is shift-structured the key cancels and 97 letters of
depth-2 is the whole message; if it is a general per-column chart, K5 leaks **exactly the 97-bit
agreement pattern and nothing more** (for any pair of distinct plaintext letters a bijection exists
realising any pair of distinct ciphertext letters — constructed in 2000/2000 trials).

**2. Error tolerance. The single cheapest way any existing negative could be void.**
Sanborn omitted a letter from K2's carved ciphertext and admitted it in 2006; **nobody ever ran a
reverse check on K4** (2005 dinner notes); and his measured hand-encipherment error rate on the
*Antipodes* Cyrillic cryptogram is **~25 errors in 1,558 characters ≈ 1.6 %**, i.e. **~1.5 expected
errors in 97 letters**. Every large sweep except the running-key suite demanded an exact 24/24.
*First step:* re-run `families_quagmire.py` and the position-model sweeps with a mismatch budget
k ≤ 2, reporting survivors against the inflated chance expectation (**×600 for k = 1, ×1.7 × 10⁵
for k = 2**). At periods 2–13, where expected survivors are < 2 × 10⁻⁹, a k ≤ 2 sweep is still a
meaningful test; at periods ≥ 24 it is not, and should not be run.

**3. Perturbed keyword-mixed alphabets. The one genuinely actionable lead the lateral work
produced.**
In the Cyrillic cipher — recovered exactly here and round-tripped 1558/1558 — Sanborn **hand-moved
Ш** out of its keyword-mixed position for no cryptographic reason. Every alphabet sweep in this
repository assumes alphabets are generated by the standard keyword rule; 208,627 dictionary
alphabets do not include a single hand-perturbed one.
*First step:* take each of the 17 Kryptos-list alphabets, apply all 650 single-letter relocations,
and re-run periods 2–26 in all 12 pairings (11,050 alphabets — cheaper than the sweep already run).
Chance bookkeeping is unchanged (26⁻ᶜ). Extend to the dictionary set only if the small sweep shows
anything.

**4. The semantic crib-drag on the 2025 disclosures (constraint C9). The only operational content
the new clues have.**
Sanborn's November 2025 letter puts the **1986 Egypt trip** and the **1989 fall of the Berlin Wall**
in the solution, and names the **Weltzeituhr at Alexanderplatz**.
*First step:* under the strong positional reading, for each word in {WALL, NOVEMBER, NINETEEN,
EIGHTYNINE, BRANDENBURG, ALEXANDERPLATZ, WELTZEITUHR, WORLDCLOCK, TOMB, VALLEY, CARTER, LUXOR,
PYRAMID, SHADOW, COMPASS, LODESTONE, MERIDIAN, LATITUDE, MARKER, CROSSHAIRS} and every legal offset, compute the implied key letters and test them for consistency with the 24 known
pairs. Report any word placing at **c ≥ 5**; quote 26⁻ᶜ beside it. Note the counter-evidence
already on record: crib-pinned English sampling produces COMPASS 0.00 %, POSITION 0.13 %,
SHADOW 0.00 % of the time, so this vocabulary is not favoured by the ciphertext.

**5. Non-keyword alphabet constructions (constraint C7). A named, never-closed gap.**
`families.md` explicitly records as untested: columnar-transposed keyword blocks (the standard ACA
construction for Quagmire alphabets, and exactly what a hand-drawn chart produces), decimated
alphabets (step *d* coprime to 26, 12 non-trivial values), and reversed variants.
*First step:* generate those three alphabet families and re-run the 25-period Quagmire sweep — a
~4× multiple of a job that takes 14 s on 8 cores.

**6. The weak crib reading and nulls confined to the three non-anchor regions (C12/C2-weak).**
Scheidt, 2004: *"I used a bit of stego when designing the fourth part."* The anchors occupy
22–34 and 64–74 contiguously, so any null-dropping or letter-selection scheme must leave those
blocks intact, which leaves exactly three regions: **1–21, 35–63, 75–97**.
*First step:* enumerate letter-selection rules that preserve both anchor blocks (drop every k-th
letter outside them; geometric predicates on the panel), and for each re-derive the crib pairs and
run the standard battery. Be honest in advance that this reading is **crib-free in the
T-then-S case** and can only ever be decided on English.

**7. Documentary routes, which are now competitive with cryptanalytic ones.**
*First steps, in order:* (a) the **2009 Archives of American Art oral history** with Sanborn — 6.5
hours, the longest first-person account of the encoding process in existence; `aaa.si.edu` returns
403 to scripted fetches, so a human must read it. (b) The **K1/K2 coding charts the *NYT* published
in 2010**, which Sanborn has repeatedly said reward forensic study. (c) **AAA Box 6 Folders 18–19
("Cracked Codes and Charts") and Box 18 Folder 19 ("Russian Charts")**, which the 2026-05-06
finding aid lists as *open for research*. (d) Sanborn's original **EAST layout image** — every
published version of that clue is a transcription of a picture nobody has reproduced.

**8. Lower-prior items, listed so they are not mistaken for gaps.** Non-additive uses of the clock
(as a transposition schedule or a chart selector rather than a key stream); short lateral streams
as periodic keys (formally uncovered, almost certainly subsumed by the period sweeps); non-repeating
knight's tours through the tableau (excluded on parsimony — more free parameters than letters
explained — not by search); re-sourcing the *Antipodes* K4 transcription from a citable photograph.

**Two free filters every future candidate should be run through.** (i) The cribs force exactly
**one** equality on any letterwise key stream: **k[28] = k[66]**, separation 38. A periodic key
satisfies it automatically only if p ∈ {1, 2, 19, 38}, all four dead; anything else must satisfy it
by coincidence at 1/26. (ii) The 22 forced **inequalities** refute, alphabet-free and family-free,
the chart periods {1,2,3,4,5,6,7,9,10,14,15,17,21,25,34,42,43,45,50}.

---

## 7. The limits — stated honestly

**What a hand cipher built to defeat statistical attack looks like.** Scheidt's stated design goal
was to *"mask the English language"* so that frequency counting fails — and §4 measures exactly how
completely that worked. At 97 letters, *every* system with an effective key length ≥ 7 produces
K4's statistical profile: Hill 2×2, Quagmire III, running key, both autokeys, Gromark, a
one-time pad. They are not merely hard to tell apart; they are **statistically identical at this
length**. A designer who wanted a cipher that a mid-century cryptanalyst's toolkit could not
classify did not need anything exotic — 97 letters and a key longer than about 8 suffices. The
corollary is uncomfortable: K4's flatness is **not evidence** that anything clever was done. K1's
own ciphertext — a period-10 Quagmire over 63 letters — has IoC z = −0.13, also indistinguishable
from random. Flatness is what short texts do.

**Where the two self-mapping crib letters point.** S→S at 33 and K→K at 74 do one thing with
certainty and nothing else: they kill every cipher whose per-position permutation has no fixed
point — the entire Enigma family (all models, all wirings, all plugboards, all ring and rotor
settings), Typex, Porta, Playfair and its derivatives — with probability exactly 0, no search
required. That is a real and permanent exclusion of the most famous machine ciphers of the era.
But for anything else they are **unremarkable**: the expected number of self-maps in 24 crib
letters under an unrestricted cipher is 24/26 = 0.923, and P(≥2) ≈ 0.236. They support no positive
inference. And the exclusion is contingent on the announced positions: 67–83 % of random
placements of a single crib word are self-map-free, and 6 of the 13 whole-block shifts in [−6,+6]
happen to be self-map-free too. The argument is robust to nothing except the cribs being right —
which §3.G establishes as firmly as documentary evidence allows, but which is still an assumption.

**Where the flat IoC points.** Not at masking, and not at a one-time pad. It points at the
**boundary of what 97 letters can carry**. Combine the three quantitative boundaries this effort
established and the shape of the problem is complete:

* **The crib boundary.** 24 crib letters are **113 bits**. Any system whose key carries more than
  that is guaranteed to have crib-consistent settings — M-209 (278 bits, ~2^165 of them), a 6×6
  square plus a wide columnar key, a 26-of-100 grid (168 bits), and above all a free
  97-column chart (456 bits, **26⁷³ = 1.96 × 10¹⁰³** crib-perfect key streams). Crib testing has no
  purchase on any of them. It never will.
* **The statistical boundary.** Scanned, corrected classical statistics have ≥ 50 % power only
  below effective key length 8 — the same region the cribs demolish with 11–22 constraints.
* **The dilution boundary.** There are about **10⁵⁵ crib-consistent English plaintexts** out of
  26⁷³ ≈ 10¹⁰³·³ candidates (conditional entropy of the 73 free letters: 182.5 bits). Any model
  with ≥ 34 free key letters therefore produces English-looking decryptions **by chance**, which is
  why periods ≥ 58 cannot be tested by anyone, ever, with this evidence.

The three boundaries meet in the same place, and the object that sits in the gap is not exotic: it
is a **hand-drawn 97-column chart with no compressive description**. That object fits the cribs
trivially, is invisible to every statistic, is a position-indexed key stream (so it contradicts none
of the negatives above), and is exactly what Sanborn keeps naming — *"no one has recovered the
original matrix"*, where in his vocabulary "matrix" means a handwritten coding spreadsheet, not
linear algebra. The auction lot's own wording supports it: K5 is the *"unpublished 1988 alternate
K4 plaintext **and coding chart**"* — you do not redraw a keyword for an alternate draft; redrawing
the chart is what you do when the chart *is* the key. Two consequences follow that nobody had
stated: **97 is a property of the worksheet, not of the message** (the chart predates the final
plaintext, so any theory deriving 97 from the message has the causality backwards), and the search
fraction is not small but **vanishing** — 3.26 × 10⁻⁶⁷ of the crib-perfect positional space.

**The genuine tension, unresolved.** An incompressible chart contradicts Scheidt directly:
*"designed to be solved in a straight-forward manner with pencil and paper"*, a 9-out-of-10
difficulty rating, a five-to-ten-year expectation, and his own brief — *"don't create something
that you cannot break."* The documented resolution is Sanborn's, not an invention: Scheidt supplied
systems *"plus ways to modify all of those systems"*; Sanborn says he modified them further so that
**even Scheidt would not know what it says**; and nobody ever ran a reverse check on K4. Scheidt's
breakability guarantee covers *Scheidt's* layer. If something incompressible exists, it is the
artist's mask on top — which is a statement about **where to look: at a worksheet, not at an
algorithm**.

**Why public cryptanalysis may be insufficient.** The method was never written down anywhere
public. Scheidt's "masking technique" is *his* name for *his* design goal; he said it "may not be
known" and that he promised Sanborn to keep it secret — and the man who actually performed the
encryption **did not recognise the term** when it was put to him in 2019. Any model treating
"masking" as a specific named operation is building on sand. The one artefact that would settle it
— the original K4 coding system — is item 2 of a lot in private hands; the plaintext is held by
four people and a hash; the verifier binds a string, not a procedure. Meanwhile every negative in
§3 rests on a single assumption Sanborn himself declined to reaffirm in 2019: that ciphertext
letter *i* maps to plaintext letter *i* at the crib positions. He confirmed it emphatically at the
2013 ACA convention (N=B, Y=E, P=R, V=L, T=I, T=N — *"decodes"*); six years later he would commit
only to *"K4 is exactly 97 characters long, and BERLIN is plaintext that starts at exactly the 64th
character."*

That is the honest end-state. The space of *catalogued* classical systems is now very thoroughly
closed, with numbers attached. What remains is either (a) a documented, specific hypothesis about a
non-catalogued hand method, judged solely on 24/24 cribs plus English; (b) one of the three
assumptions failing — a carved letter is wrong, the positional reading is wrong, or the plaintext
is far less English-like than any model allows; or (c) K5, a 97-cell worksheet, and the archive.

---

## Appendix — where each number comes from

| report | line of attack |
|---|---|
| `findings/families.md` | periodic Vigenère/Beaufort/variant/Quagmire I–IV, Porta, Gronsfeld, Trithemius, autokey, digraphic and fractionating families, Hill, monoalphabetic |
| `findings/runningkey.md` | running key and autokey from all 66 sculpture-text variants, with rotations |
| `findings/geometry.md` | reading orders, panel-wide positional keys, lag 7, the number 97, alphabet-free impossibility |
| `findings/twocipher.md` | two-stage transposition + substitution in all four readings; double substitution; double transposition; the K3 procedure |
| `findings/crib_placement.md` | verification of the crib positions from primary sources; 68.5 M placement/variant tests |
| `findings/statistics.md` | calibrated nulls for every K4 statistic; power analysis at n = 97 |
| `findings/tableau.md` | the tableau as key table, the collapse theorem, the anomaly, the solvekryptos audit |
| `findings/k5_genealogy.md` | 1989 hand-cipher census (Slidefair, Portax), the K5 lever and its four theorems, cross-section phase, the question mark, OBKR |
| `findings/prior_art.md` | published prior art (Bean, Bauer/Link/Molle, Schridde, Hörenberg, kryptosfan) and a forensic audit of every public "solution" |
| `findings/sanborn_statements.md` | tiered dossier of every Sanborn/Scheidt statement; constraints C1–C18; attributions that do not hold up |
| `findings/seg_*_out.txt` | interrupted, segmented and trigger-driven key models; the crib-planted null; the gold-standard forward-simulation null |
| `findings/search_*_out.txt`, `analysis/search_*.py` | language-model attack: calibration, annealing, crib-blind periods 27–57, key-stream battery, public-claim scoring |
| `analysis/matrix_*_output.txt`, `findings/matrix_g_out.txt` | checkerboard/VIC, homophonic/polyphonic, nomenclator, unknown-square fractionation (CP-SAT), rotor machines, ADFGVX and conjugated-matrix ADFGVX |
| `lateral/INDEX.md`, `berlin_clock.md`, `antipodes_agency.md`, `clue_history.md`, `tableau_panel.md` | lateral key material (both Berlin clocks, compass rose, Morse, Cyrillic Projector, Antipodes), the clue record, the archival record |

**Standing rules that produced these numbers, and that any continuation should keep.** Verify every
routine by round-trip and synthetic-key recovery before trusting a negative. Quote the chance
expectation beside every hit count — a hit at the chance rate is not a hit. Report the null
distribution of the **maximum** of any statistic over everything that was scanned to find it, not
the nominal p. Never seed a search from a circulating plaintext. A solution is **24/24 cribs and
English**, and nothing less has ever been claimed here.
