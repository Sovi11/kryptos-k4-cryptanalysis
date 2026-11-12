# Liber Primus LP2: the anti-repeat rule

*Session of 12 Nov 2026. A follow-up to [`lp2_attack_2026-11.md`](lp2_attack_2026-11.md).*

**Bottom line.**
- **No plaintext was recovered.**
- **What was settled:**
  - LP2's missing doublets come from a step that compares each output rune with the previous one. They cannot come from the key alone.
  - That step runs over the continuous rune stream, ignoring word, punctuation, line and page breaks.
  - It lets about **19% of collisions through, at random**. The leak is a coin flip with no detectable link to position, rune, word structure, line, page or chapter.
  - The step does not occur in any solved Liber Primus page.
- **What was excluded:** every structured explanation tested. That covers blocks of n runes, resets at words, lines or pages, prime positions, counter rules, and doublets that copy the plaintext's.

Scripts are `cicada/analysis/lp_antirepeat.py`, `lp_antirepeat2.py`, `lp_antirepeat_sa.py` and `lp_antirepeat_sa2.py`. They need numpy and are seeded, so they reproduce exactly. Raw outputs are in `antirepeat_out/`.

The data is the relikd/LiberPrayground page transcription. It keeps physical lines and page blocks. The fetch command is in `lp_common.py`, and the data is not redistributed here.

## 0. The data

| check | result |
|---|---|
| relikd vs scream314 transcriptions | agree at 12,955 of 12,956 runes; the only difference is one A/AE at stream position 5,892 |
| Doublets, both transcriptions | **86** in 12,947 adjacent pairs; independent-rune expectation 447.4; ratio **0.192** |
| Structure available | 9 files, 60 page blocks (pages or page parts), 594 physical lines |

## 1. The rule runs over the continuous rune stream

The leak rate is the same at every kind of junction:

| junction between the two runes | pairs | doublets | ratio to chance |
|---|---|---|---|
| inside a word, same line | 9,636 | 60 | 0.18 |
| inside a word, across a line break | 388 | 3 | 0.22 |
| word separator | 2,581 | 21 | 0.24 |
| word separator plus line break | 123 | 1 | 0.24 |
| sentence or chapter punctuation | 157 | 1 | 0.18 |
| page or paragraph break | 51 | 0 | 0 (1.8 expected if unprotected; p = 0.17) |

**What this shows.** The encryptor's notion of the "previous rune" is the previous *rune*. It skips over separators, line breaks and, as far as the data can tell, page breaks. So the rule was applied to the rune stream before layout, and does not reset at words or lines.

**What it excludes.**
- **A rule restricted to the inside of words.** It would predict zero within-word doublets; there are 63.
- **A rule that resets at each line.** It would predict a leak about 22 times larger at line starts, and none is seen (simulation in §6).

## 2. The leak is homogeneous and random

**Rate per unit.** The leak rate does not vary by line, page block or chapter file. Each test compares the observed spread with 4,000 random re-placements of the 86 doublets:

| unit | χ², observed | χ², null mean | P(over-dispersed) |
|---|---|---|---|
| line | 537.0 | 589.7 | 0.95 |
| page block | 62.4 | 58.5 | 0.33 |
| file | 6.2 | 7.9 | 0.62 |

**Spacing.** Gaps between successive doublets look like a Poisson process. Their coefficient of variation is 0.950, against 0.975 ± 0.108 for random placement (p = 0.44). There is no clustering: 4 gaps of 10 runes or fewer, against 5.5 expected.

**Counter rules.** The data rules out a counter rule such as "every k-th collision is allowed through". Such a rule makes the spacing regular:

| rule | CV of gaps | doublets produced |
|---|---|---|
| every 2nd collision | 0.69 ± 0.04 | 224 |
| every 3rd collision | 0.57 ± 0.04 | 149 |
| every 4th collision | 0.49 ± 0.04 | 112 |
| **every 5th collision** | **0.43 ± 0.04** | **89**, the same count as LP2 |
| every 6th collision | 0.39 ± 0.04 | 75 |
| **LP2 observed** | **0.950** | **86** |

None of the 1,000 simulations of any counter rule reached LP2's CV. The every-5th rule matches the doublet count, but its CV misses by about 13 standard deviations.

**The doublets themselves.**
- **Runes involved.** 28 of the 29 runes occur. Runes with two Latin forms (U/V, C/K, S/Z, NG/ING, IA/IO) account for 10 doublets against 14.9 expected. So the rule is not comparing Latin spellings.
- **Neighbouring runes.** The runes before and after each doublet are uniform: χ² 23.9 and 32.5 on 28 df.
- **Triplets.** There are none, against 0.57 expected.
- **Word length.** Within-word doublets follow word length exactly as random pairs would.

**Repeats at longer gaps.** These match what a one-step anti-repeat chain predicts:

| gap | observed | independent runes | first-order anti-repeat chain |
|---|---|---|---|
| 2 | 440 | 447.0 | 456.5 |
| 3 | 439 | 446.7 | 445.5 |
| 4 | 458 | 446.4 | 445.5 |

These cannot separate the two models; the difference at gap 2 is about 0.8 sd.

## 3. No positional structure of any kind

| hypothesis | test | result |
|---|---|---|
| **Fixed-size groups** (a 5-rune group cipher, protection that resets every n runes, Playfair-like blocks) | Alignment-free: for n = 2–40, sum over units of the most popular residue of doublet positions. Under the hypothesis this equals 86. Calibrated by 2,000 permutations that keep each unit's count. | Nothing. Global p is 0.33 (chapter, rune index), 0.57 (chapter, separators counted), 0.53 (page block) and 0.73 (line). At n = 5: 32 against 32.1 by chance. |
| Fixed alignment to line, page or chapter start | χ² of position mod n, n = 2–12 | Smallest p 0.14 across 33 tests. Doublets at line positions 0–4: 4, 7, 3, 3, 4 against 3.9 each. |
| **Protection switched off at prime positions** | Fraction of doublets at prime positions, for 3 units × 3 index conventions | Would need all 86 at primes; the most found is 26 (18.6 expected, nominal p 0.04, not significant after 9 tests). Simulated, the rule would also give the wrong rate (0.215). |
| Fibonacci positions | count | 0 against 0.9 |
| **Cipher doublets copy plaintext doublets** (differential or multiplicative-difference ciphers, an alphabet held between runes) | Where in the word the doublets sit | **Excluded at p = 6 × 10⁻¹³.** English almost never starts a word with a doubled rune: 0.2% of English rune doublets are word-initial. LP2 has **12 word-initial doublets out of 63**, against 0.6 expected under this hypothesis. LP2's split is initial 11, medial 33, final 18, whole two-rune word 1. Random pairs give 14.9, 30.4, 14.8 and 2.9. |

## 4. No key, however chosen, can produce the deficit

For an additive cipher cᵢ = s·pᵢ + kᵢ with the key independent of the plaintext, the distribution of within-word differences cᵢ − cᵢ₋₁ is the plaintext's difference distribution convolved with the key's. This holds for **any** key-difference distribution, so it covers:
- one-time pads;
- running keys;
- Vigenère, Beaufort and variant;
- Atbash followed by a shift;
- every number stream.

For each multiplier s, the best key distribution was fitted exactly. This is a convex mixture problem solved by EM, and 40,000 and 300,000 iterations give identical results. The fit was then compared with a parametric bootstrap.

| plaintext model | best fit (deviance G) | bootstrap 99.9th percentile | doublets the best fit can reach |
|---|---|---|---|
| English: *War and Peace* in runes, 1.8M pairs | **185.6** (Vigenère 207.2, Beaufort 208.6) | 36.6 | 208, against 63 observed |
| Cicada's own LP1 plaintext spelling | **169.0** | 28.1 | 207, against 63 observed |

The best any plaintext-independent additive key can do is about 208 within-word doublets. To get lower, it must make the rest of the difference spectrum visibly lumpy. LP2 has 63 doublets and a flat spectrum.

**This corrects the earlier ledger.** A one-time pad *on its own* is not consistent with LP2. It would give about 346 within-word doublets.

**Keyed alphabets.** Allowing an arbitrary fixed substitution σ, with c = σ(p) + k, raises the model's capacity a great deal. Simulated annealing over σ with an exact key fit at each step gives:

- **Within-word differences only:**
  - best G = 36.3 and 41.0 on two seeds;
  - p = 0.007 and 0.003 by a conservative fixed-σ bootstrap.
  - Getting even that close needs a key whose consecutive differences take only **3–4 values**.
- **Both gap-1 and gap-2 differences, random-walk key (any step distribution):**
  - Such a 3–4-value key forces structure two runes apart, so this fit is the real test.
  - Best G = 88.1 and 88.8 on two seeds, against a bootstrap maximum of 67.7 and 71.2 over 150 replicates.
  - The best fit still needs at least 117 within-word doublets.
  - **Excluded.**

A keyed alphabet whose key differences are concentrated *and* have non-Markov dependence between steps is not tested. It is contrived, and it would be a strong structure in its own right.

**Conclusion.** The deficit requires the encryptor to look at its own output. Something compares cᵢ with cᵢ₋₁ and changes it, about 81% of the time, when they match.

## 5. The rule is new in LP2

| page | method | doublets | independent expectation | expected under LP2's rule |
|---|---|---|---|---|
| Welcome (LP1) | Vigenère, DIVINITY | 16 | 21.8 | 4.2 |
| Koan 2 (LP1) | Vigenère, FIRFUMFERENFE | 9 | 13.4 | 2.6 |
| An End (LP2 p56) | φ(prime) stream | 2 | 3.7 | 0.7 |
| **total** | | **27** | 38.9 | **7.5** (P ≈ 10⁻⁸) |

The monoalphabetic pages (Atbash and shifts) preserve the plaintext's doublets exactly, so they say nothing either way. None of Cicada's solved polyalphabetic pages has the anti-repeat step, so it belongs to the unsolved method.

## 6. Simulated mechanisms

Each mechanism was run on LP2's exact skeleton: its word, line and page breaks. The plaintext is English runes and the key is uniform. Results are 12 replicates each.

| mechanism | doublet ratio | gap-2 ratio | line-break leak ÷ overall | verdict |
|---|---|---|---|---|
| **LP2 observed** | **0.192** | **0.984** | **1.03** | |
| no rule | 0.98 ± 0.03 | 0.98 ± 0.03 | 1.08 | rate wrong |
| reroll once on collision | 0.033 ± 0.009 | 1.04 | 1.00 | rate wrong (15 doublets, not 86) |
| **rule fires with probability 0.81** | **0.198 ± 0.020** | 1.05 ± 0.04 | 1.12 | **matches** |
| reset at each line | 0.040 | 1.02 | 22.1 | rate wrong; would be line-dominated |
| reset at each word | 0.231 | 1.03 | 1.55 | excluded by 63 within-word doublets (§1) |
| reset every 5 runes | 0.194 | 1.02 | 1.25 | rate right; excluded by the block test (§3) |
| off at prime positions | 0.215 | 1.04 | 0.82 | excluded by position test (§3) |

Only a rule whose failures are randomly placed survives.

The leak probability is 0.192, with a 95% interval of **0.15–0.23**. Several simple fractions sit in that interval: 1/6, 1/5, 5/29 and 4/29. If the rule rerolls on a collision, its rate of not firing is about 0.16, since a uniform reroll leaks 1/29 by itself.

## 7. What this means for an attack

1. **LP2 is not a "pure key" cipher.** Every attack that models LP2 as plaintext plus a key stream is mis-specified unless it also includes the output check. This covers OTP, running key, number streams and keyed-alphabet Vigenère; the check can coexist with any of them.
2. **The check is decryptable if the reroll is deterministic.** Take "on a collision, use the next key value". A reader with the key sees cᵢ = cᵢ₋₁ as a leaked collision, so no skip happened there. Where cᵢ − cᵢ₋₁ = kⱼ₊₁ − kⱼ, a skip may have happened. That ambiguity occurs about once per 29 runes and is resolved by reading. This is a natural successor to LP1's plaintext-F interrupter: the key is again interrupted, but the trigger is now a collision in the output.
3. **If rerolls consume key, alignment slips about 360 times.** That is roughly once per 36 runes over the unsolved text. Any search that tests a candidate key generator assuming continuous alignment over long windows can recover at most a few dozen runes before it fails. Future generator searches should use skip-aware decoding: a beam over the ambiguous positions in item 2.
4. **Structured number streams stay dead regardless.** Skips do not rescue primes, φ(primes) or Fibonacci-type streams. Their key differences are lumpy, and LP2's difference spectrum is flat whether or not there are slips. A surviving generator must produce statistically flat differences. Examples are digit expansions taken in pairs, hash chains, or a PRNG.
5. **The random 19% is itself a clue to the implementation.** A deterministic program that always checks would leak about 0% (reroll until different) or 3.4% (one uniform reroll). A 15–23% leak with no positional pattern points to one of three things:
   - an explicit random draw;
   - a condition on a hidden variable (the key or plaintext value) that holds about 16% of the time;
   - a human applying the rule by hand and missing about one in five.

## 8. Next steps

1. ~~**Skip-aware generator search.**~~ **Done, negative:** see [`lp2_skipsearch.md`](lp2_skipsearch.md). The search covered 104 flat-difference streams (digit expansions, totient, SHA chains, PRNGs) at every chapter start and every offset below 15,000, under the collision-skip rule, about 87 million beam decodes. Three planted keys were recovered exactly, while every real stream scored at chance, both in the selection window and out of sample.
2. **Plaintext-conditioned firing.** If the rule is skipped when pᵢ belongs to a set S with about 16–19% frequency, the leaked doublets inherit S's position-in-word profile. With 86 doublets this has little power alone, but it can score candidate decryptions.
3. **Plaintext-dependent key plus uniform key.** This remains live. It is the only family other than "uniform key + explicit check" that the data does not yet exclude.
