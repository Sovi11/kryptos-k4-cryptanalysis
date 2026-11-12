# Liber Primus LP2 — attack session, 12 Nov 2026

**Bottom line: no plaintext recovered.** This session sharpens LP2's statistical fingerprint and
eliminates four families that the community ledger still listed as live, including its "strongest
live candidate." Every negative is either analytic or verified against a planted cipher.

Data: the rune transcription `liber_primus.md` from
[scream314/cicada3301](https://github.com/scream314/cicada3301) (not redistributed here; fetch
with `gh api repos/scream314/cicada3301/contents/liber_primus.md -H "Accept: application/vnd.github.raw" > cicada/data/liber_primus.md`).
Scripts: `cicada/analysis/lp_*.py`. The numpy-based scripts need a Python with numpy.

## 0. Verification of the pipeline

| check | result |
|---|---|
| Unsolved LP2 rune count | **12,956** (published 12,956) |
| Doublets | **86** (published 86), expected 447.7 |
| Within-word doublets | **63 / 10,056** pairs (published 63 / 10,056) |
| Normalized IoC | 1.000 (published 0.999) |
| Solved page 56 with φ(prime) | decrypts to "AN END / WITHIN THE DEEP WEB / THERE EXISTS A PAGE THAT HASHES TO …" |

## 1. LP2's fingerprint, made precise

1. **Unigrams are flat.** IoC 0.9999; F share 3.54% against a uniform 3.45%.
2. **Only one thing is non-random: identical adjacent runes are 5.2× too rare.** Every other
   adjacent difference cᵢ − cᵢ₋₁ is flat: χ² = 33.0 on 27 df within words. None of the 812
   non-identical rune pairs is suppressed (most negative z = −2.74; Bonferroni needs −3.67).
3. **The suppression is rune-level, not letter-level.** Pairs whose Latin forms repeat a letter at
   the junction (T→TH, EA→A, …) occur at 1.12× expectation, so they are not suppressed.
4. **The suppression has no memory beyond one step.** Repeats at gap 2 and gap 3 occur at exactly
   the random rate (441 and 440 against 447 expected).
5. **The 86 doublets are unremarkable in every other respect.** Their runes are distributed in
   proportion to rune frequency (χ² 26.7 on 28 df). They are not concentrated on F, so they are not an
   F-skip artefact. Their word positions match the base rate (27/51/22% initial/medial/final against
   22/56/22%). Their rate is homogeneous across sections (χ² ≈ 7 on 12 df). The apparently
   elevated chapters ("Mayfly", 1.08%) are noise.

**A consequence that is pure arithmetic.** If cᵢ = pᵢ + kᵢ with *any* key independent of the
plaintext, then P(cᵢ = cᵢ₋₁) = Σₓ P(Δp = x)·P(Δk = −x), which stays near 1/29 for English plaintext
and any reasonable key. A 5× suppression with all other differences flat therefore cannot
arise from the key stream alone. **The encryption process must be aware of the previous
ciphertext rune**, and the only thing it does with that awareness is avoid repeating it.
In effect it looks like a uniform key plus an explicit anti-repeat rule that fires about 81% of the time.

## 2. What this session ruled out

| family | test | result |
|---|---|---|
| **Previous ciphertext rune selects the substitution**, cᵢ = g_{cᵢ₋₁}(pᵢ) for *any* g (the ledger's "strongest live candidate", ciphertext form) | group cᵢ by cᵢ₋₁; English would give IoC ≈ 1.7 per group | 1.026, which is entirely the doublet effect; with the diagonal removed, **z = +0.83** (null) |
| Same, grouped by cᵢ₋₂, the previous two runes, or their sum or difference | grouped IoC | all null (z −0.37 to +0.87) |
| **Ciphertext autokey, any primer L = 1–6000** | group cᵢ by cᵢ₋ₗ | max 1.026 at L = 1 (the doublet effect); mean 1.0002 |
| **Running key from any English text; plaintext autokey, any primer** | ciphertext frequencies must equal English ⊛ English, IoC ≈ 1.05 | LP2 0.9999 is **−14.3 sd** (additive) and **−11.9 sd** (subtractive) away; bootstrap lower bound 1.04 |
| **LP1's F-skip convention** (plaintext F left unencrypted) | raises ciphertext IoC to ≈ 1.02 | LP2 0.9999, about 30 sd away |
| **Additive prime / φ(prime) / prime-of-prime / Fibonacci / n streams** | difference distribution | prime-type streams leave χ² 110–1000 on the differences; LP2 has 41.5 |
| **Multiplicative feedback** cᵢ = cᵢ₋₁ + mᵢ(pᵢ − z) and **additive feedback** cᵢ = cᵢ₋₁ + pᵢ + kᵢ | 8 number streams × 2 zero-handlings × 16,000 offsets × 8 sections | best IoC 1.145 against a null max of 1.161; **planted cipher recovered exactly** (offset 7321, IoC 1.769) |
| **"Doublets mark one plaintext rune"** (implied by multiplicative feedback) | rate and word-position profile | runes rare enough (EA, AE) have the wrong position profile; runes with the right profile are 3–9× too common. Weakened, but reference sample small |
| **Anti-repeat rule on Latin letters** | junction-letter pairs | not suppressed (ratio 1.12) |

## 3. What remains live

* **Uniform key (OTP or strong PRNG) plus an explicit anti-repeat step.** This fits every
  statistic. The open puzzle is the partial rate: a "re-encrypt on repeat" rule removes about 97%
  of doublets, not 81%. A rule that fires conditionally, or one whose reroll often collides again,
  would explain it. **Identifying that rule is the best remaining structural lead.** It would tell
  us what software or procedure produced LP2.
* **Dependence on the previous *plaintext* rune combined with an additional uniform key.** Grouping
  by ciphertext cannot see this.
* **Non-English inner layer** (LP2 as an encryption of already-random-looking data). This is
  consistent with everything, and it would make the anti-repeat property belong to the inner layer.
* ~~**One-time pad.** Consistent with everything, and unbreakable if true.~~ **Corrected the same day.** A
  one-time pad *on its own* cannot produce the doublet deficit: no plaintext-independent key does. See
  [`lp2_antirepeat.md`](lp2_antirepeat.md) §4. An OTP **plus** an output check remains live, under the first bullet.

## 4. Suggested next steps

1. ~~Simulate concrete anti-repeat implementations to see which one gives exactly 0.19× (86 of 448).~~
   **Done:** see [`lp2_antirepeat.md`](lp2_antirepeat.md). Only a rule whose failures fall at random
   (about 19%) fits. Blocks, resets, counters and prime-position rules are all excluded.
   Candidates: a rule applied with a fixed probability, a single reroll from a structured stream, or
   a check against the previous *plaintext* rune. Any rule that matches would be a real lead.
2. Hill-climb a plaintext-autokey-plus-key model on the longest sections, scored with an LP-style
   English model built from LP1 cleartext.
3. Re-run the feedback search with 3301's recorded number puzzles as streams (the 15.jpg square
   recurrence, the 2016/2017 Fibonacci-from-464 construction).
