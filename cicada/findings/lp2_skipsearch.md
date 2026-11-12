# Liber Primus LP2: skip-aware key-generator search (2026-11-12)

**Result: negative.** None of 104 candidate key streams decrypts LP2 under the "collision → skip one key value" model of the anti-repeat rule.

The search would have found such a key. Three keys planted in real LP2 chapters were all recovered at exactly the right key index, including one found 2,474 runes and 79 accumulated skips into its chapter. By contrast, every real stream scores at chance level, both on the selection window and on the 200 runes after it.

Scripts:
- [`analysis/lp_keystreams.py`](../analysis/lp_keystreams.py): the streams.
- [`analysis/lp_skipsearch.py`](../analysis/lp_skipsearch.py): the search.
- [`analysis/lp_skipsearch_report.py`](../analysis/lp_skipsearch_report.py): controls and out-of-sample test.

Outputs are in [`skipsearch_out/`](skipsearch_out/), [`skipsearch_report.txt`](skipsearch_report.txt) and the raw run log [`skipsearch_run.txt`](skipsearch_run.txt).

The run log has two known flaws:
- Its in-run FOUND/MISSED label for the plants was wrong; see §3.
- It ends with harmless `BrokenPipeError` tracebacks from worker shutdown after all results had been collected. One of these overwrote the tail of the DECOYS line.

`skipsearch_report.txt` is the authoritative summary.

## 1. Model

[`lp2_antirepeat.md`](lp2_antirepeat.md) showed that LP2's doublet deficit needs an explicit output check. Each rune is compared with the previous *rune*, and about 81% of collisions are repaired. The simplest decryptable version of that check consumes key:

```
v = sp·p + sk·K[j] + a            (mod 29; sp, sk = ±1; a = 0..28)
if v == c[i-1] and the rule fires:  j += 1;  v = sp·p + sk·K[j] + a
c[i] = v;  j += 1
```

A reader who holds the key sees a possible skip wherever `c[i] − c[i−1] ≡ sk·(K[j+1] − K[j])`. That happens about once per 29 runes, by chance or because a real skip occurred.

Decoding is therefore a beam search over those branch points. The branch structure does not depend on `(sp, a)`. So paths are first ranked by the coincidence count of `y = c − sk·K`, and the best path is then scored for English under all 58 output transforms.

## 2. What was searched

| | |
|---|---|
| Key streams (104) | **Digit expansions (55 streams).** π, e, √2, √3, √5, φ, ln 2, √3301, plus Copeland–Erdős, Champernowne and concatenated Fibonacci. Each is read as 2-digit groups mod 29 (both phases) or 3-digit groups mod 29 (all three phases).<br>**Totient.** φ(n) mod 29.<br>**Hash chains (24 streams).** SHA-256 and SHA-512 chains, bytes mod 29, from 12 seeds: 3301, cicada, Cicada 3301, liber primus, divinity, instar, circumference, 1595277641, the page-56 hash, and others.<br>**PRNGs (24 streams).** Python 3 `randrange(29)`, Python 2 `int(random()*29)` and glibc `rand() % 29`, each with seeds 3301, 1033, 2012–2014, 1595277641, 0 and 1.<br>Every generator is self-tested against published values. |
| Where | 28 starts. Each is the first rune of a file, or the first rune after a ⁜ chapter mark, and has at least 80 runes in the 100-rune window. |
| Key position | Offsets 0–14,999 at each start, for both key signs. Suppose the key ran continuously from index 0 at the start of LP2: 12,956 runes plus about 360 skips is roughly 13,300 key values. Its offset at every start is then below 15,000, so it is covered. So is a key restarted per chapter at any offset below 15,000. |
| Decoding | Beam of 12 over 100 runes, ranked by coincidence count. The best path per offset is scored with an English rune-bigram model: War and Peace in runes, with LP2's own word breaks, word-initial runes scored separately. The score is maximised over the 58 transforms `(sp, a)`. |
| Volume | 104 × 28 × 2 × 15,000 ≈ **87 million** beam decodes. These took 73 min on 8 cores, controls included. |

## 3. Controls: the search finds a planted key

Each plant re-encrypts one real LP2 chapter with a known key under the skip rule, with the rule firing at 81%. The plaintext follows LP2's own word skeleton, filled with War and Peace words of matching rune length. The search then runs blind over that chapter's starts.

The "true offset" is the planted key index at the hit's window start, counting every skip made before it. The in-run label allowed at most 8 accumulated skips, so it mislabelled the second and third plants as MISSED. [`lp_skipsearch_report.py`](../analysis/lp_skipsearch_report.py) replays each plant exactly, with the same RNG draws, and checks the hit against the true index.

| Planted key | Chapter (runes, skips) | Top hit | Offset found vs true | (sk; sp, a) found vs true | Window LL | Next 200 runes LL |
|---|---|---|---|---|---|---|
| √3 2-digit, phase 1 | file 3 (1,903; 46) | +20 runes, 0 skips before | 12,365 = 12,365 | (+1; +1, 7) = (+1; +1, 7) | −2.432 | −2.450 |
| SHA-512 chain('3301') | file 6 (1,680; 42) | +845 runes, **22 skips** before | 5,188 = 5,188 | (−1; −1, 20) = (−1; −1, 20) | −2.344 | −2.389 |
| py3-rand(3301) | file 7 (3,008; 98) | +2,474 runes, **79 skips** before | 12,429 = 12,429 | (+1; −1, 0) = (+1; −1, 0) | −2.362 | −2.569 |

All three are recovered exactly. Their continuations read as the planted text. For example, plant 2 reads "…TOMORROW HER PROMOTIAN DID TO END SAID…"; the residual misspellings are skip points where the beam guessed wrong.

**Chance baseline.** 16 uniform random key streams were run through the identical search over all 28 starts. Their per-stream maximum log-likelihood had median −4.072 and **maximum −3.976 per rune**. The planted keys score 1.5 nats per rune above that.

**Does the scorer recognise Cicada's own English, not just War and Peace?** The nine solved plaintext pages, cut into 24 windows of 100 runes, score from −2.64 to −2.19 per rune (median −2.43). Every one is far above the decoy maximum.

## 4. Results on the real streams

**Per-stream maxima (selection window).**

| | n | median | max |
|---|---|---|---|
| decoys | 16 | −4.072 | −3.976 |
| real streams | 104 | −4.060 | −3.812 (φ 3-digit phase 2, start 848) |

- 15 real streams beat the best decoy. The expected number is 6.1 under exchangeability, and P(≥ 15) = 0.10.
- The rank-sum comparison of the two sets gives z = +0.66.
- This is chance. The best real hit, −3.81, is closer to the decoys than to any planted key (≈ −2.4) or any Cicada plaintext window (≥ −2.64).

**Out of sample.** Every hit was chosen on its 100-rune window, so its window score is inflated by selection. The test continues each hit into the next 200 runes:
- the hit's own transform is held fixed;
- 15 starting key indices are tried, covering the unknown number of skips inside the window;
- the best of the 15 is kept.

The null distribution is the same procedure applied to the decoys' top hits.

| | n | median | 99th pct | max |
|---|---|---|---|---|
| null (decoy hits) | 155 | −5.428 | −5.035 | −4.891 |
| planted keys | 3 | | | −2.389 … −2.569 |
| real hits | 979 | −5.422 | | −4.852 |

- 12 real hits exceed the null 99th percentile, where about 10 are expected.
- The best continuation (e 2-digit phase 0 at start 8059) reads "TTPWSF FEOP LOEEOTHE N THD ATH…".
- No real hit continues as language.

## 5. What is now excluded, and what is not

**Excluded** (all three plants were recovered, with a 1.5 nat/rune margin):
- LP2 as `c = ±p ± K + a` over the standard Gematria order;
- with K any of the 104 streams above, entered at any offset below 15,000 at any chapter or file start;
- with the anti-repeat check implemented as "on a collision, skip one key value";
- with English plaintext and LP2's word breaks genuine.

**Probably covered, not planted.** A repair that does not consume key, such as "bump the output rune". The key then stays aligned, and the no-skip path is always in the beam; only about 3% of runes would decode wrongly.

**Not covered:**
1. Other repair rules: rerolling from a second stream, skipping a plaintext rune or inserting a null, or skipping more than one key value. **Update:** these are now tested in [`lp2_repairrules.md`](lp2_repairrules.md). Bump and null-and-retry are excluded by statistics. Flip, reroll2, literal-with-the-key-used-up and skip-until are covered by this search, as confirmed by planted keys. The LP1-style "stay" rule was searched separately, with a negative result.
2. Multiplicative keys, keyed alphabets, and Gematria orders other than the standard one.
3. Streams outside the list. That includes:
   - digit groupings other than 2 and 3 digits mod 29, and base-29 conversions;
   - hash outputs read as hex characters or with rejection sampling;
   - other seeds;
   - offsets of 15,000 or more.
4. Non-English plaintext.
5. Ciphers where the key also depends on the plaintext (the "plaintext-dependent key plus uniform key" family in [`lp2_antirepeat.md`](lp2_antirepeat.md) §8).
6. A true one-time pad plus check, which no generator search can reach by construction.

**Reusing the search.** A new candidate generator is one entry in `lp_keystreams.all_streams()`. A full search costs about 5 CPU-minutes per stream.
