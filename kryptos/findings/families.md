# K4 — cipher families beyond periodic Vigenère/Beaufort/Quagmire III

Scripts: `analysis/families_quagmire.py`, `families_shiftkeys.py`, `families_digraphic.py`,
`families_hill.py`, `families_mono.py`, `families_keystream.py` (shared code in `analysis/k4_common.py`).
Raw logs/JSON: `findings/*_run.log`, `findings/*_results.json`.

Inputs: the 97-letter ciphertext and the four Sanborn cribs (1-indexed 22-25 EAST, 26-34 NORTHEAST,
64-69 BERLIN, 70-74 CLOCK), i.e. 24 (cipher, plain) pairs:

```
22:F->E 23:L->A 24:R->S 25:V->T 26:Q->N 27:Q->O 28:P->R 29:R->T 30:N->H 31:G->E 32:K->A 33:S->S 34:S->T
64:N->B 65:Y->E 66:P->R 67:V->L 68:T->I 69:T->N 70:M->C 71:Z->L 72:F->O 73:P->C 74:K->K
```

Two facts used throughout:

* **The ciphertext contains all 26 letters** (J at positions 41, 52, 82; Y and M once each).
* The crib letters S (pos 33) and K (pos 74) encrypt to themselves.

Chance-survival bookkeeping for any "key value must repeat with period p" test: the 24 crib positions
occupy 24 - c_p distinct residues mod p, so a random key passes with probability 26^-c_p.
c_p = 24-p for p <= 13; for larger p: 14:11, 15:9, 16:8, 17:7, 18:7, 19:9, 20:11, 21:11, 22:9, 23:7,
**24:5, 25:3, 26:1**. Periods 25 and 26 are therefore almost unconstrained by the cribs and their
"survivors" have to be judged on the decrypted text, not on passing the test.

**Bottom line: nothing survives. No family tested here is consistent with the cribs, except the
period-26 Quagmire cases that pass a single constraint by chance and decrypt to gibberish.**

---

## 1. Quagmire I / II / IV (independently keyed plaintext and ciphertext alphabets)

Model: `c_i = CT_ALPHA[(idx_PT_ALPHA(p_i) + k[i mod p]) mod 26]`, so each crib forces
`k_i = idx_CT(c_i) - idx_PT(p_i) (mod 26)`; a period-p Quagmire exists iff k_i is constant on residue
classes mod p. Quagmire I = (keyed PT, straight CT), II = (straight PT, keyed CT), III = same keyed
alphabet twice, IV = two different keyed alphabets. The same code covers all four. Regression: the
model reproduces the K1 ciphertext from K1 plaintext with the KRYPTOS alphabet and key PALIMPSEST.

Alphabets:
* short list (17): straight A-Z + keyword-mixed alphabets from KRYPTOS, PALIMPSEST, ABSCISSA, SANBORN,
  SCHEIDT, LANGLEY, BERLIN, CLOCK, COMPASS, LODESTONE, SHADOW, IQLUSION, UNDERGRUUND, DESPARATLY,
  LAYERTWO, MASKING.
* dictionary: every distinct keyword-mixed alphabet from `/usr/share/dict/words` (words >= 3 letters):
  **208,627 distinct alphabets**.

Pairs tested (periods 2-26 each): short x short = 289; short(PT) x dict(CT) and dict(PT) x short(CT)
= 7,093,318. **Total 7,093,607 alphabet pairs x 25 periods.** Runtime 14 s on 8 cores.
Not tested: dict x dict (~4e10 pairs), non-keyword alphabet constructions (columnar-transposed keyword
blocks, decimated alphabets, reversed alphabets), periods > 26.

Results (observed survivors vs. the number a uniformly random key stream would produce):

| period | constraints | expected by chance | observed |
|---|---|---|---|
| 2-13 | 22 .. 11 | < 2e-9 | 0 |
| 14-23 | 11 .. 7 | <= 9e-4 | 0 |
| 24 | 5 | 0.6 | 0 |
| 25 | 3 | 404 | 0 |
| 26 | 1 | 2.7e5 | 487,280 |

Notes:
* The period-25 zero and the period-26 excess are both structural, not bugs (verified by injecting
  synthetic period-25 Quagmire IV keys, which are detected). Keyword-mixed alphabets keep the tail in
  alphabetical order (Z last, F early), which makes the period-25 constraint
  `idx_CT(F)-idx_CT(Z) = idx_PT(E)-idx_PT(L)` essentially unattainable and the period-26 constraint
  `idx_CT(F)-idx_CT(P) = idx_PT(E)-idx_PT(C)` more common than 1/26.
* Period 26 leaves residues 8, 9, 10 undetermined (26 letters of the 97 unknown). The 487,280
  period-26 "survivors" were ranked by a bigram log-likelihood of the partial decrypt. Best score
  -6.17 (PT=AMORPHIA, CT=UNDERGRUUND):
  `ATOCHRWN???UTHEABOXAJeastnortheast???APHIPLGTINACUSEXALINTVF???berlinclockCTAFDDDNJLEH???ISGXZPZU`
  followed by MORULATION/COMPASS (-6.20), COCCYGOMORPH/UNDERGRUUND (-6.20), MALACANTHUS/SANBORN (-6.21),
  STRONTIUM/LODESTONE (-6.22) ... English text scores about -5.3 on this model. Filling the same
  template with random letters and taking the best of 200,000 trials gives -6.13, i.e. the observed
  best is exactly the chance level. No dictionary words of length >= 5 appear outside the cribs in any
  of the top 40. Judgement: **noise, not a solution**.
* Short x short only (289 pairs): 0 survivors for p <= 25; 18 at p = 26, all with PT alphabet in
  {ABSCISSA, SHADOW, IQLUSION} and CT alphabet in {STRAIGHT, SANBORN, COMPASS, LODESTONE, DESPARATLY,
  LAYERTWO}, bigram scores -6.8 to -7.2 (random level). Full list in `findings/quagmire_run.log`
  and the companion listing printed during analysis; e.g. SHADOW/LAYERTWO:
  `PEBKQRDB???LLUYBZHXHTeastnortheast???RSUBSBIQFKVEXAISSJRGKIK???berlinclockEECJFYUYWVRI???GCVTVTPR`.

**Conclusion: no Quagmire I/II/IV with a keyword-mixed alphabet from the Kryptos word list on either
side, and any dictionary keyword on the other side, fits the cribs at any period 2-25. Period 26 is
too weakly constrained to test and produces only chance hits.**

---

## 2. Porta, Gronsfeld, Trithemius / progressive key

### Porta (13 reciprocal alphabets)
Tested the standard ACA table and the Bellaso-direction variant, on the straight and the KRYPTOS
alphabet ordering, periods 2-26. In every configuration 16 of the 24 crib pairs have cipher and plain
letter in the same half of the alphabet, which no Porta row can do; 0 periods survive.
Stronger: Porta always swaps halves, so it can never map a letter to itself, and the cribs contain
S->S and K->K. **Porta is ruled out for every possible 26-letter alphabet ordering.**

### Gronsfeld (digit key 0-9)
Required shifts computed for Vigenère, Beaufort and variant-Beaufort on straight and KRYPTOS
alphabets (6 configurations). Between 11 and 16 of the 24 required shifts exceed 9 in every
configuration (e.g. straight/Vigenère: 1 11 25 2 3 2 24 24 6 2 10 0 25 12 20 24 10 11 6 10 14 17 13 0).
**Gronsfeld ruled out** regardless of period. (Periodicity check 2-26 also gives 0 fits.)

### Trithemius / progressive key, letter-wise: shift_i = a + b*i
All 676 (a, b) pairs x {straight, KRYPTOS} x {Vigenère, Beaufort} = 2,704 keys: **0 exact fits**.
Best partial agreement is 7/24 crib positions (straight/Vig, a=20, b=4); all others <= 5/24.

### Periodic key with a progressive alphabet shift
(A) `shift_i = key[i mod p] + b*floor(i/p)` (alphabet advances by b after every period) and
(B) `shift_i = key[i mod p] + b*i` (advances after every letter), for p = 2-26, b = 0-25,
{straight, KRYPTOS} x {Vigenère, Beaufort}: 5,200 combinations, **0 consistent**, not even at
period 26 (there the single constraint is between positions 21 and 73; variant B needs
shift_21 = shift_73, which fails in all four configurations; variant A needs shift_21 - shift_73 = 2b,
which is odd in all four). b = 0 reproduces the prior "no periodic Vigenère/Beaufort" result.

### Bonus: autokey
Plaintext autokey (key_i = p_{i-L}) checkable for primer lengths L = 1-12 and 30-52 (where two crib
letters are L apart), ciphertext autokey (key_i = c_{i-L}) checkable for every L = 1-96, both with
Vigenère and Beaufort rules on both alphabets: **0 consistent primer lengths**.

---

## 3. Digraphic and fractionating ciphers (Playfair, two-square, four-square, bifid, trifid)

Structural findings:
1. **All 26 letters occur in the ciphertext.** Any cipher built on a 25-cell square (Playfair,
   two-square, four-square, 5x5 bifid, any 5x5 Polybius-based system) can emit at most 25 distinct
   letters. This alone rules out the whole 5x5 family unless the sculpture text is in error.
2. 97 is odd. Playfair/two-square/four-square would additionally need a null appended (98) or a
   stray letter; nothing on the sculpture suggests one (the "?" before OBKR belongs to K3).
3. Playfair never maps a letter to itself: cribs have S->S (33) and K->K (74). Playfair cannot produce
   a doubled ciphertext digraph: with digraphs starting at position 2, QQ (26-27) -> NO and TT (68-69)
   -> IN would be needed. Playfair is therefore ruled out three times over. Two-square and four-square
   can map a letter to itself and can emit doubled digraphs, so for them only point 1 applies.
4. K4's odd length is not an obstacle for bifid/trifid (the last block is simply shorter).

Bifid and trifid brute force (decrypt the full ciphertext, count crib letters that match):
* 5x5 bifid, I/J merged, keyword-mixed squares for all 16 keywords, periods 2-30 (J in the ciphertext
  treated as I purely as a tolerance; strictly it is already impossible): best 5/24 (UNDERGRUUND,
  period 22); KRYPTOS square best 3/24 at period 7.
* 6x6 bifid (keyed A-Z + 0-9), same keywords and periods: best 4/24.
* Trifid (27 symbols: keyed A-Z plus '#', at either end), same keywords, periods 2-30: best 5/24
  (MASKING, period 26); KRYPTOS cube best 3/24.
Chance agreement is about 1 letter per trial; the best-of-464 (16 keywords x 29 periods) maxima of
4-5 are what chance gives. A real fit would be 24/24. Decrypt routines were verified by encrypt/decrypt
round trips at several periods, including partial last blocks. **No bifid/trifid fit.** (Squares that
are not keyword-mixed were not searched; a general unknown-square bifid search was not attempted.)

---

## 4. Hill cipher

Because encryption is linear, each row of the key matrix can be solved independently:
`c_r = sum_j K[r][j] p_j (+ v_r)`. For every alignment of the digraph/trigraph boundaries, only blocks
lying entirely inside the cribs are used (2x2: 11 blocks for each of the two parities; 3x3: 7, 7, 6
blocks for the three offsets). Each row was brute-forced over all 26^n coefficient rows (and 26^(n+1)
with an affine constant, which also covers A=1..Z=26 numbering), in both the encryption direction
(C = K P) and the decryption direction (P = D C), with straight and KRYPTOS-keyed letter numbering.
The solver recovers a synthetic 2x2 key from the same crib blocks uniquely.

Result: **every row has zero solutions in every configuration** (2x2: 2 parities x 2 alphabets x
{linear, affine} x {enc, dec}; 3x3: 3 offsets x the same). Not one row of a Hill key can be made
consistent with the cribs, so odd length / padding questions are moot: no 2x2 or 3x3 Hill cipher over
Z26 produced K4.

---

## 5. Simple substitution sanity check

Forward conflicts (one cipher letter would need two plaintexts):
F->{E,O} (22,72); K->{A,K} (32,74); N->{B,H} (30,64); P->{C,R} (28,66,73); Q->{N,O} (26,27);
R->{S,T} (24,29); S->{S,T} (33,34); T->{I,N} (68,69); V->{L,T} (25,67).
Reverse conflicts (one plaintext letter from several cipher letters, impossible for a bijection):
A<-{K,L}; C<-{M,P}; E<-{F,G,Y}; L<-{V,Z}; N<-{Q,T}; O<-{F,Q}; S<-{R,S}; T<-{R,S,V}.
**9 forward and 8 reverse conflicts: monoalphabetic substitution is ruled out** (the Q->N / Q->O pair
at adjacent positions 26-27 alone suffices). Caesar/affine c = a*p + b (1,352 keys, both alphabets):
none. Pure transposition without substitution: the cribs need three E's but the ciphertext contains
only two E's, so a transposition-only K4 is impossible as well.

---

## 6. Non-periodic / one-time-pad view of the 24 required shifts

Whole ciphertext: IoC = 0.0361 (uniform random 0.0385, English 0.066), chi-square vs English = 577.
The 24 key values forced by the cribs:

| alphabet / rule | shifts | as key letters (block 22-34, block 64-74) | distinct (uniform exp. 15.9) | chi-sq vs uniform (df 25) |
|---|---|---|---|---|
| straight / Vigenère | 1 11 25 2 3 2 24 24 6 2 10 0 25 / 12 20 24 10 11 6 10 14 17 13 0 | BLZCDCYYGCKAZ / MUYKLGKORNA | 14 | 30.2 |
| straight / Beaufort | 9 11 9 14 3 4 6 10 20 10 10 10 11 / 14 2 6 6 1 6 14 10 19 17 20 | JLJODEGKUKKKL / OCGGBGOKTRU | 12 | 49.7 |
| KRYPTOS / Vigenère | 1 10 21 18 1 15 2 23 5 2 19 0 2 / 11 17 2 5 15 11 9 8 7 20 0 | RDUMRIYWOYNKY / ELYOIECBAQK | 16 | 25.8 |
| KRYPTOS / Beaufort | 23 24 7 0 13 25 4 5 7 24 7 12 10 / 1 13 4 13 19 23 1 16 17 12 0 | WXAKGZTOAXAFD / RGTGNWRJLFK | 14 | 28.0 |

Three of the four look uniform (chi-square 26-30 against an expectation of 25; 95th percentile 37.7);
straight/Beaufort is mildly clumpy (K x5, G x4) but that is one configuration out of four and within
what multiple testing allows. The key letters do not read as English under any rule (chi-square
vs English 94-319, bigram scores -7.0 to -8.1 vs about -5.3 for English), so a running-key cipher with
an English key on these alphabets is not indicated either (the KRYPTOS/Vigenère stream, chi-square 94,
is the least un-English, but RDUMRIYWOYNKY / ELYOIECBAQK is not text). With only 24 samples this
cannot distinguish a one-time pad from a long non-repeating keyword or a cipher of a different kind;
what it does say is that the required additive key, if K4 is additive at all, shows no periodicity,
no digit restriction, no progressive structure and no English-like structure in the crib windows.

---

## Summary of what was tested and the outcome

| family | scope | survivors |
|---|---|---|
| Quagmire I/II/IV | 7,093,607 alphabet pairs (17 Kryptos-list alphabets x 208,627 dictionary alphabets, both roles, plus 17x17) x periods 2-26 | 0 for p<=25; p=26 chance-level only |
| Porta | 2 tables x 2 alphabet orders x periods 2-26 | 0 (ruled out for any alphabet: S->S, K->K) |
| Gronsfeld | 3 rules x 2 alphabets x periods 2-26 | 0 (11-16 shifts > 9) |
| Trithemius a+b*i | 2,704 keys | 0 (best 7/24) |
| periodic + progressive (per period / per letter) | 5,200 combinations | 0 |
| autokey (PT and CT, both rules, both alphabets) | L = 1-96 | 0 |
| Playfair / two-square / four-square | structural | ruled out (26 distinct CT letters; Playfair also self-map and doubled digraphs) |
| bifid 5x5 / 6x6, trifid | 16 keywords x periods 2-30 | 0 (max 5/24 crib letters, chance) |
| Hill 2x2, 3x3 (linear and affine, both directions, both alphabets, all alignments) | full row-wise brute force | 0 (no row solvable) |
| monoalphabetic / affine / pure transposition | exhaustive | ruled out (9+8 conflicts; E-count) |

Nothing here produces a candidate plaintext. The additive key implied by the cribs is aperiodic and
statistically flat; the digraphic and matrix families are excluded outright. Remaining unexplored
directions in these families: Quagmire with dict x dict alphabets or non-keyword alphabet
constructions, bifid/trifid with an unknown (non-keyword) square, and any two-stage system
(transposition combined with substitution), which the crib-position tests above do not cover.
