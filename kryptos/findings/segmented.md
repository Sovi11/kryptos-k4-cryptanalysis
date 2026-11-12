# K4 — irregular key advance, interrupted keys, and segmented ciphers

Scripts: `analysis/seg_common.py`, `seg_a_stats.py` … `seg_h_bijection.py`.
Raw output: `findings/seg_a_out.txt` … `seg_h_out.txt`, `seg_a_results.json`.
The compute ran 12–13 Sep 2026; the agent died before writing this report, so it was
assembled on 12 Nov 2026 directly from the raw outputs. Every number below is quoted from them.

**Bottom line: nothing survives.** Irregular key advance (the Liber Primus skip rule and
four relatives), interrupted keys with inserted or deleted key letters, plaintext-triggered
advance and key-driven interruptors all produce survivor counts at or below chance. The few
decryptions that looked promising were shown by a dedicated null experiment to be
exactly what random ciphertexts produce.

---

## Why this family mattered

A key that does not advance on every letter defeats every periodicity test, so it is the one
idea that could explain why 35 years of period hunting on K4 found nothing. It is also an
attested hand-cipher technique. Cicada 3301's Liber Primus uses a Vigenère whose key does not
advance on the rune F. It is also exactly the kind of modification Scheidt described teaching Sanborn.

## (a) Segment statistics: the IoC is not anomalous

| test | value | null | p |
|---|---|---|---|
| Global IoC | 0.03608 | uniform mean 0.03847, sd 0.00281 (500k trials) | **P(IoC ≤ 0.03608) = 0.214** |
| Homogeneity across panel rows 4/31/31/31 | G = 84.72 | permutation mean 78.54 | 0.259 |
| Homogeneity across crib-block segments | G = 127.91 | permutation mean 112.44 | 0.061 |
| Homogeneity across halves 48/49 | G = 44.19 | permutation mean 31.56 | 0.063 |

**Correction to earlier project statements.** K4's IoC sitting below 1/26 has been read,
including in this project's own earlier summaries, as evidence of deliberate frequency
flattening. It is not. One random 97-letter string in five lands at or below 0.0361. No
segment differs from the others at p < 0.05. `statistics.md` reaches the same conclusion
independently, with an omnibus p ≈ 0.40.

## (c) Ciphertext-triggered key advance — `seg_c_skiprule.py`

Pointer rules: **HOLD** (classic skip rule), **DOUBLE**, **RESET_AFTER**, **RESET_AT**,
**ADVANCE_ONLY**. Triggers: each letter A–Z, the doubled letters, the X's, panel-row
boundaries, letter classes (vowels, rare letters, KRYPTOS letters), each with delay 0 or 1.
Periods 2–26. 867 cipher configurations per test (3 families × 17 plaintext alphabets ×
17 ciphertext alphabets).

| pass | configurations | observed survivors | expected by chance |
|---|---|---|---|
| Kryptos-list alphabets | 6,936,000 | 22,828 | 22,130.7 |
| Survivors with ≥ 3 constraints | — | 1 (HOLD on G, p = 25, c = 3) | 0.049 per test |
| 208,627 dictionary alphabets on the free side | 57,668,675,340 | 849,261 | 984,036.7 |

The best constrained hits carry 5–7 constraints, against 11–22 for any reasonable period, and
pair Kryptos words with dictionary noise (EPIGUANINE, BOLTMAKER, MEANINGFULLY). Fully determined
survivor decryptions score quadgram −7.33 to −7.46, against −8.2 for random and about −4.7 for English.
The cribs are visible in these decryptions because they were imposed. The rest of the text is gibberish.

## (d) Interrupted keys — `seg_d_interrupted.py`

A periodic key with one or two key letters inserted or deleted at unknown positions. This is the
failure mode of Sanborn's own 2006 K2 correction.

| variant | configurations | observed | expected |
|---|---|---|---|
| D0, single break | 303,450 | 5,567 | 5,483.6 |
| D1 | 807,177 | 0 | 0.00 |
| D2, two breaks | 19,784,073 | 0 | 0.00 |
| dictionary second pass | 19,534,997,772 | 5,829 | 5,088.0 |

One fully determined survivor (Beaufort, COMPASS/LAYERTWO, p = 22) decrypts at q = −7.39.
Outside the cribs it is noise.

## (e) Plaintext-triggered advance and key-driven interruptors — `seg_e_plaintrig.py`

* **E1, crib-consistency sweep:** 807,545,475 configurations; 8,906,578 survivors against
  8,788,865.7 expected (ratio 1.013).
* **E2, forward simulation:** each surviving key was run forward deterministically and the 52
  non-crib letters were scored out of sample. Six configurations beat the analytic best-of-N
  threshold, all RESET_AFTER at p = 13. Best: q = −7.138.
* **E3, interruptor on the key letter (ACA "interrupted key"):** 56,801,505 configurations,
  0 survivors, 0.00 expected.

## (g) The E2 "hits" are artefacts — `seg_g_e2null.py`

The E2 threshold assumed 673,297 independent trials. They are not independent, so the
threshold was wrong. The definitive check reran the whole E2 pipeline on 15 uniformly random
ciphertexts and 15 shuffles of K4 itself:

| null | mean max q | replicates ≥ K4's −7.138 | p |
|---|---|---|---|
| uniform | −7.133 | 7 / 15 | 0.50 |
| shuffled K4 | −7.126 | 5 / 15 | 0.375 |

Random ciphertexts do as well as K4. Their best BERLINCLOCK reproduction was 6/11, compared with
K4's 5/11. **The E2 sweep found nothing.**

## (h) Bijection constraint — `seg_h_bijection.py`

Requiring the plaintext-to-ciphertext map at each key value to be a bijection removes all
remaining candidates at c ≥ 5. The E2 forward simulation predicted 0 of 11 BERLINCLOCK letters.

---

## Conclusion

Irregular key advance was the strongest untested hypothesis left. It is now tested at a scale of
about 7.7 × 10¹⁰ configurations, counting the dictionary passes, and closed. Together with
`families.md`, `runningkey.md`, `geometry.md` and `twocipher.md`, this leaves no position-indexed
key system with a key small enough to be constrained by 24 crib letters.
