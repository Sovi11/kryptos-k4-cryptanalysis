# Liber Primus LP2: other collision-repair rules (2026-11-12)

[`lp2_skipsearch.md`](lp2_skipsearch.md) tested one way of fixing a collision: skip one key value. This session tests the others.

**Result: negative.**
- Two rules are excluded outright by key-free statistics.
- Four more turn out to be covered by the earlier skip-aware search. Planted keys under each rule were recovered by that search unchanged.
- The LP1-style rule needed a new search: write the rune without key, and hold the key. It found nothing over the same 104 generators. Planted keys under that rule were recovered at the exact key index, including one 2,474 runes and 90 key holds into its chapter.

Scripts:
- [`analysis/lp_repair_screens.py`](../analysis/lp_repair_screens.py): key-free screens.
- [`analysis/lp_repairsearch.py`](../analysis/lp_repairsearch.py): plants, the "stay" search and its report.

Outputs:
- [`repair_screens.txt`](repair_screens.txt)
- [`repairsearch_run.txt`](repairsearch_run.txt)
- [`repairsearch_out/`](repairsearch_out/)

## 1. Repair rules, by what they do to key alignment

The encryption step is `v = sp·p + sk·K[j] + a`. When `v` would equal `c[i−1]` and the rule fires (81% of the time), a repair rule decides what is written instead.

The key distinction is whether every ciphertext rune still uses up exactly one key value.

| Class | Rule | Alignment | How tested |
|---|---|---|---|
| forward slip | **skip**: use `K[j+1]`; two key values used | key runs ahead | earlier search ([`lp2_skipsearch.md`](lp2_skipsearch.md)) |
| | **skip-until**: keep skipping until there is no collision | key runs ahead | planted, earlier search finds it (§3) |
| aligned | **flip**: write `sp·p − sk·K[j] + a` (Vigenère ↔ Beaufort) | unchanged | planted, earlier search finds it (§3) |
| | **reroll2**: re-encrypt with a value from a second, unknown stream | unchanged | planted, earlier search finds it (§3) |
| | **litcons**: write `p` unencrypted, key value still used up | unchanged | planted, earlier search finds it (§3) |
| | **bump**: write `c[i−1] + d` | unchanged | **excluded by the difference spectrum** (§2) |
| plaintext slip | **null**: write a null, then retry `p` with the same key value | key falls behind | **excluded by A?A count** (§2) |
| backward slip | **stay**: write `sp·p + a` (no key) and do *not* use up the key value | key falls behind | **new search** (§4) |

**Why aligned rules need no new search.** With the right key and offset, every unrepaired rune decodes correctly. Only the repaired runes (about 2.8%) come out wrong. The earlier beam always keeps the no-skip path, so a correct aligned key still scores like English. The plants in §3 confirm this for every aligned rule except "bump", which §2 excludes anyway.

**Stay is the LP1 interrupter, collision-triggered.** In LP1, a plaintext F is written as ᚠ unencrypted and the key does not advance. The stay rule does the same, but triggers when encryption would repeat the previous rune.

For `(sp, a) = (1, 0)`, the rune written is literally the plaintext. That is the orientation of LP1's Vigenère and φ(prime) pages, so "write the raw plaintext rune and hold the key" is covered exactly there. For other `(sp, a)` the search covers writing `sp·p + a`, which is what the encryption gives with a zero key.

A reader holding the key sees a possible stay wherever `c[i−1] − c[i] ≡ sk·K[j]`. This happens about once per 29 runes and does not depend on `(sp, a)`, so the beam, coincidence and English pipeline carries over with only the branch changed.

## 2. Key-free screens

Each statistic is computed over LP2's continuous rune stream, within files, and compared with 200 simulations per rule. The simulations are LP2-sized, use War and Peace plaintext and a uniform key, and fire on 81% of collisions.

| | doublets | largest non-zero difference count | χ² of the 28 non-zero differences | A?A (cᵢ₊₁ = cᵢ₋₁) | literal-rune LLR |
|---|---|---|---|---|---|
| **LP2** | **86** | **510** (d = 9) | **41.2** | **440** | **0.93** |
| skip (reference) | 98 ± 10 | 503 ± 9 | 27.5 ± 7.6 | 457 ± 19 | 1.8 ± 1.4 |
| bump (`c[i−1] + 7`) | 85 ± 9 | **807 ± 28** | 300 ± 44 | 456 ± 22 | 1.9 ± 1.4 |
| null, retry same key | 82 ± 9 | 503 ± 10 | 27.0 ± 7.2 | **794 ± 26** | 2.1 ± 1.4 |
| stay with raw literal | 97 ± 10 | 503 ± 11 | 27.0 ± 7.1 | 456 ± 22 | 4.3 ± 2.0 |

- **Bump, for any d: excluded.** The repairs would pile about 360 extra pairs onto one difference. LP2's largest is 510, below all 200 simulations.
- **Null-and-retry: excluded.** The retried rune re-encrypts to exactly `c[i−1]`, adding about 360 A?A triples. LP2 has 440, below all 200 simulations.
- **Stay: mildly disfavoured, not excluded.** Its roughly 360 plaintext-distributed runes should skew the unigram counts. LP2's mixture LLR, maximised over the 58 `(sp, a)` maps, is 0.93. Only 1.5% of stay simulations go that low, against 29% for the skip rule. That is suggestive but not decisive, so the key search below was still run.
- **Aside.** LP2's non-zero differences are slightly lumpy: χ² = 41.2 on 27 degrees of freedom, P ≈ 0.045 against the simulations, with the peak at d = 9. Several statistics were examined here, so this is not significant. It is recorded only so it is not rediscovered as a lead.

## 3. Planted controls

Each control re-encrypts one real LP2 chapter under the rule, using LP2's word skeleton filled with War and Peace words. The search then runs blind over that chapter's starts:
- the stay plants with the new stay-mode beam;
- every other plant with the unchanged skip-mode beam from the earlier search.

"True offset" is the planted key index at the hit's window start, counting every slip before it.

| Rule | Key | Chapter (runes, repairs) | Hit depth | Offset found = true | (sk; sp, a) | Window LL | Next 200 LL |
|---|---|---|---|---|---|---|---|
| stay | π 3-digit | file 2 (1,729; 48) | +0 | 3,000 = 3,000 | (+1; 1, 0) | −2.314 | −2.584 |
| stay | SHA-256 chain('cicada') | file 5 (1,433; 37) | +19 | 7,796 = 7,796 | (−1; −1, 13) | −2.391 | −2.427 |
| stay | glibc rand(1033) | file 8 (308; 6) | +0 | 11,111 = 11,111 | (+1; 1, 22) | −2.564 | −2.506 |
| stay, searched ≥ 1,000 runes in | py3 rand(3301) | file 7 (3,008; 90) | **+2,474** | 12,284 = 12,284 | (+1; −1, 0) | −2.504 | −2.491 |
| flip | e 2-digit | file 1 (1,145; 32) | +0 | 2,222 = 2,222 | (+1; 1, 5) | −2.441 | −2.581 |
| reroll2 | SHA-512 chain('divinity') | file 4 (1,021; 32) | +16 | 6,016 = 6,016 | (−1; 1, 9) | −2.585 | −2.597 |
| litcons | py2 rand(2014) | file 0 (729; 16) | +13 | 513 = 513 | (+1; −1, 3) | −2.568 | −2.557 |
| skip-until | φ 2-digit | file 6 (1,680; 47) | +99 | 9,104 = 9,104 | (−1; −1, 1) | −2.361 | −2.500 |

All eight are recovered exactly, and every continuation reads as the planted text. The scores sit far above the random-key ceiling, about −3.9 (below).

## 4. The stay search on LP2

The search used the same 104 streams, 28 starts, both key signs, offsets 0–14,999 and 58 output maps as the skip search. It took 39 minutes on 8 cores.

| | n | median | max |
|---|---|---|---|
| per-stream max LL, decoys (16 uniform streams, same search) | 16 | −4.081 | −3.924 |
| per-stream max LL, real streams | 104 | −4.061 | −3.834 (py3 rand(1), start 7970) |

- 3 real streams beat the best decoy, where 6.1 are expected (P = 0.65).

**Out of sample.** Each hit is decoded over the next 200 runes with its own `(sp, a)`, allowing 0–14 holds inside the window. The null is the same procedure applied to the decoys' top hits (n = 150): median −5.408, 99th percentile −5.004, max −4.950.

- Real hits (n = 953): median −5.416, max −4.898.
- 8 hits exceed the null 99th percentile, where about 9.5 are expected.
- The 4 hits above the null maximum are three copies of one Champernowne window plus one PRNG window. They miss it by 0.05 or less, and the planted keys sit about 2.4 higher. Their text reads "JL ROEEOUHEDT GBNGL CDPP…".
- Nothing continues as language.

## 5. Coverage after this session

**Excluded**, for the 104 generators at any chapter start and any offset below 15,000, with English plaintext:
- skip;
- skip-until;
- flip;
- reroll from a second stream with the main key still used up;
- literal with the key used up;
- stay, which includes the exact LP1-style "raw plaintext, hold the key" at `(sp, a) = (1, 0)`.

**Excluded for any key**, by the screens: bump by any fixed d, and null-and-retry.

**Still open:**
1. Raw-literal stay at `(sp, a) ≠ (1, 0)`. Covering every map costs 58 times the search; the screen above already disfavours literal rules.
2. Reroll from a second stream *with the main key held*. This cannot be decoded without the second stream.
3. Fixed skips of two or more.
4. A null that uses up a key value. This keeps the key in step, so it should be covered like the other aligned rules, but no plant was run.
5. Keyed alphabets and multiplicative keys.
6. Generators outside the list.
7. A plaintext-dependent key.
8. A one-time pad plus a check.

The machinery is reusable:
- `lp_repairsearch.beam(..., mode)` takes `"skip"` or `"stay"`, and a new branch rule is a few lines;
- a new stream is one entry in `lp_keystreams.all_streams()`.
