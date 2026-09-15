# K4 — what the statistics actually prove

Calibrated null distributions for every statistic that has been used to argue about K4.

Scripts: `analysis/stat_common.py` (shared machinery), `stat_validate.py` (verification harness),
`stat_a_ioc.py`, `stat_b_coverage.py`, `stat_c_doubles.py`, `stat_d_autocorr.py`,
`stat_e_kasiski.py`, `stat_f_profile.py`, `stat_g_power.py`.
Raw output: `findings/stat_validate_out.txt`, `stat_a_out.txt` … `stat_g_out.txt`.

Generated 2026-09-13.

---

## 0. Bottom line

**K4's ciphertext is, at n = 97, statistically indistinguishable from a uniformly random string of
letters. Every published "anomaly" in it dies once the null distribution is computed properly and the
selection that produced the anomaly is paid for.**

| claim on record | corrected verdict | number |
|---|---|---|
| "IoC 0.0361 is below uniform random 0.0385 — the masking is visible" | **no** | 21.6th percentile of the exact null; z = −0.84 |
| "All 26 letters in 97 characters is unusual" | **no** | P = 0.542 under uniform — the majority outcome |
| "Six doubled letters is high" | **no** | exact P(≥6) = 0.165 |
| "Autocorrelation spike at lag 7, z = +3.0" | **no** | family-wise p = 0.22 (lags 1–48) / 0.56 (lags 1–96) |
| "Doubled letters cluster mod 7" | **no** | corrected p = 0.245 |
| "Periodic-IoC peaks at periods 25, 28, 30" | **no** | K4 is *flatter* than random: family-wise p = 0.99 |
| "Excess column bigrams at width 21" (Bean) | **no** | corrected p = 0.090 (excess) / 0.207 (pairs) — and the nominal figure itself moves 5× with an unstated counting convention |
| "Seven of ten bigram gaps share a factor" | **no** | p = 0.197 / 0.205 once conditioned on the gap count |
| **omnibus over the whole classical battery** | **no structure detected** | **p = 0.414** |

What the statistics *do* establish, at overwhelming significance, is a short list of exclusions
(§7): K4 is not raw English, not monoalphabetic, not a pure transposition, and not a periodic
polyalphabetic of key length 1–2 (3–5 disfavoured). Everything else in the candidate space is
statistically untouched — including Hill 2×2, Quagmire III, running key, autokey, Gromark, and a
one-time pad, which are mutually indistinguishable at this length. That is not because they have been
checked and passed; it is because **97 letters cannot see past an effective key length of about 8**
(§8), which is exactly the region the cribs already destroy.

The practical consequence: **stop designing searches around K4's statistical anomalies.** They are
noise. The cribs are the only real constraint the ciphertext supplies, and where they are silent
(periods 27, 28, 29 and ≥ 53) the statistics are silent too.

---

## 1. Verification of the machinery (`stat_validate.py` → `stat_validate_out.txt`)

No number below is trusted until the routine producing it has been checked against a closed form,
exhaustive enumeration, or an independent estimate. **All checks pass.** The substantive ones:

* Exact-IoC lattice DP vs **exhaustive enumeration**: for (n = 8, c = 4) all 65,536 strings and for
  (n = 7, c = 3) all 2,187 strings, the DP reproduces every lattice-point probability to < 1e−12, and
  the truncated DP agrees with the untruncated one on the retained tail.
* Exact IoC null moments (mean 1/26, Var = 2p(1−p)/(n(n−1))) vs Monte Carlo at n = 30, 97, 369:
  agree to < 0.2–0.3 % in sd and within MC error in mean.
* Coupon-collector inclusion–exclusion vs Monte Carlo at n = 60, 97, 200: agree within 4 standard
  errors.
* Adjacent-doubles distribution vs exact Binomial(n−1, 1/26): max |exact − MC| = 0.00089 over
  k = 0…12.
* Autocorrelation z null: mean +0.0000, sd 0.9985 over 200,000 replicates.
* Fast binomial survival table (added to make the 10⁶-replicate nulls feasible) vs
  `math.comb` summation: max abs diff **4.4e−16**.
* `per_ioc_direct` vs the full-spectrum computation: **exactly 0** difference.
* Cipher routines round-trip (Vigenère, Beaufort, autokey, Gromark's lagged-Fibonacci keystream,
  transposition, general polyalphabetic).
* Positive control on real Kryptos data: Quagmire-III re-encryption of the K1 plaintext under
  PALIMPSEST reproduces the carved K1 ciphertext exactly.
* English corpus: 22,409,130 letters, IoC 0.06601.
* Published K4 statistics reproduced: IoC 0.036082, 26 distinct letters, 6 doubles at
  1-indexed 19/26/33/43/47/68, lag-7 coincidences 9 (z = +3.036), 10 repeated bigrams, 0 repeated
  trigrams.

---

## 2. (a) Index of coincidence — settled

`stat_a_ioc.py` → `stat_a_out.txt`

K4: n = 97, **IoC = 0.036082** (lattice numerator S = 336 out of 9,312 ordered pairs).

### The exact null

The IoC statistic on n uniform letters is a lattice variable, so its distribution can be computed
**exactly** rather than simulated. A DP over letters tracking Σ nᵢ(nᵢ−1) gives the whole lower tail
(mass captured: 0.9999999996):

```
EXACT P(IoC <= 0.036082 | uniform random 97 letters) = 0.215723
EXACT P(IoC >= 0.036082)                             = 0.810507
```

Cross-checked by **10,000,000 Monte-Carlo draws**: P(≤) = 0.215599 against the exact 0.215723, a
difference of 0.00012 with an MC standard error of 0.00013. Mean and sd also match the closed forms
to five decimals (0.038461/0.038462 and 0.002817/0.002818).

Exact quantiles of the null:

| percentile | 0.1 | 1 | 2.5 | 5 | 25 | 50 | 75 | 95 | 97.5 | 99 |
|---|---|---|---|---|---|---|---|---|---|---|
| IoC | 0.03200 | 0.03308 | 0.03372 | 0.03436 | 0.03651 | 0.03823 | 0.04016 | 0.04360 | 0.04467 | 0.04639 |

A two-sided 95 % interval for a random 97-letter string is IoC ∈ [0.03372, 0.04467]. **K4's 0.03608
sits at the 21.6th percentile, comfortably inside, 0.84 null standard deviations below the mean.**

### Answer to the question that has been asserted both ways

**K4 is not anomalously flat. This is ordinary small-sample noise.** 21.6 % of uniformly random
97-letter strings are at least this flat. The gap between 0.0361 and 0.0385 is 0.0024 against a null
sd of 0.0028. There is nothing to explain.

The inference "IoC is *below* uniform random, therefore the masking is visible" is backwards twice
over: the sub-uniform value is not significant, and even a perfect one-time pad has a 21.6 % chance
of landing at least this low.

### Controls

| text | n | IoC | null mean | null sd | z | P(IoC ≤ obs) |
|---|---|---|---|---|---|---|
| K1 ciphertext | 63 | 0.03789 | 0.03846 | 0.00435 | −0.13 | 0.513 |
| K2 ciphertext | 369 | 0.04547 | 0.03846 | 0.00074 | **+9.49** | 1.000 |
| K3 ciphertext | 336 | 0.06615 | 0.03846 | 0.00081 | **+34.16** | 1.000 |
| **K4 ciphertext** | **97** | **0.03608** | 0.03846 | 0.00282 | **−0.84** | **0.216** |
| K1 plaintext | 63 | 0.06503 | — | — | +6.11 | — |
| K2 plaintext | 370 | 0.06564 | — | — | +36.93 | — |
| K3 plaintext | 336 | 0.06615 | — | — | +34.16 | — |

Two of these are load-bearing.

* **K1** is a period-10 Quagmire III over 63 letters and its IoC is 0.03789 — z = −0.13, *also*
  indistinguishable from random. A short key over a short text already produces a flat IoC. K4's
  flatness is therefore not even evidence of an unusually long key.
* **K3** is a pure transposition, so its ciphertext IoC *is* its plaintext IoC: 0.06615 both. That is
  the single most useful control available — it is exactly what K4 would look like if K4 were a
  transposition, and it is **8.9 null sd away from what K4 actually is**. Transposition-only is dead
  on the IoC alone, independently of the three-E's crib argument in `families.md`.

### Vigenère over English, key lengths 1–50

200,000 simulated encipherments per key length; plaintext = a random 97-letter window of real English
prose (22.4 M letters, IoC 0.0660); key drawn uniformly.

| key length | mean IoC | 2.5 % | 97.5 % | P(IoC ≤ K4's) | verdict |
|---|---|---|---|---|---|
| 1 | 0.06626 | 0.05412 | 0.08312 | < 5e−6 | **excluded** |
| 2 | 0.05242 | 0.04210 | 0.06894 | 0.00007 | strongly disfavoured |
| 3 | 0.04789 | 0.03887 | 0.06143 | 0.00203 | strongly disfavoured |
| 4 | 0.04545 | 0.03737 | 0.05735 | 0.00784 | strongly disfavoured |
| 5 | 0.04404 | 0.03673 | 0.05477 | 0.01670 | disfavoured |
| 6 | 0.04306 | 0.03608 | 0.05305 | 0.02739 | disfavoured |
| 7 | 0.04234 | 0.03565 | 0.05176 | 0.03825 | disfavoured |
| 8 | 0.04183 | 0.03544 | 0.05090 | 0.04773 | disfavoured |
| 9 | 0.04147 | 0.03522 | 0.05026 | 0.05697 | compatible |
| 10 | 0.04112 | 0.03501 | 0.04961 | 0.06771 | compatible |
| 15 | 0.04014 | 0.03458 | 0.04790 | 0.10298 | compatible |
| 20 | 0.03966 | 0.03436 | 0.04704 | 0.12923 | compatible |
| 25 | 0.03936 | 0.03415 | 0.04639 | 0.14691 | compatible |
| 30 | 0.03917 | 0.03415 | 0.04596 | 0.15912 | compatible |
| 50 | 0.03877 | 0.03393 | 0.04532 | 0.18967 | compatible |
| OTP | 0.03847 | 0.03372 | 0.04467 | 0.21642 | compatible |

**Excluded by the IoC alone: key length 1. Disfavoured (p < 0.05): 2–8. Compatible: 9 and above.**
Note how little separates key length 9 from a one-time pad — 0.057 versus 0.216. That is the whole
resolving power of this statistic at n = 97.

---

## 3. (b) "All 26 letters appear" — no information

`stat_b_coverage.py` → `stat_b_out.txt`

Exact coupon-collector probabilities under a uniform source:

| n | 63 (K1) | 97 (K4) | 336 (K3) | 369 (K2) |
|---|---|---|---|---|
| P(all 26 present) | 0.0727 | **0.5425** | 0.99995 | 0.99999 |

**For K4's 97 letters, "all 26 appear" is more likely than not.** The exact distribution of the
distinct-letter count at n = 97 has mean 25.42 and sd 0.72, so 26 is a **+0.80 σ** outcome.

Under the candidate systems (200,000 simulations each, plaintext = real English):

| source | mean distinct | P(all 26) | likelihood ratio vs uniform |
|---|---|---|---|
| uniform / OTP / long key | 25.42 | 0.542 | 1 |
| raw English | 20.15 | 0.00005 | 12,055 |
| Vigenère L=1 (monoalphabetic) | 20.16 | 0.00003 | 21,699 |
| Vigenère L=2 | 22.98 | 0.0215 | 25.3 |
| Vigenère L=3 | 23.90 | 0.0911 | 6.0 |
| Vigenère L=5 | 24.61 | 0.2191 | 2.5 |
| Vigenère L=8 | 24.96 | 0.3307 | 1.6 |
| Vigenère L=12 | 25.14 | 0.4015 | 1.4 |
| Vigenère L=30 | 25.34 | 0.4945 | 1.1 |

So the observation buys a Bayes factor of ~1.4–2.5 against mid-length keys — which moves a 50 % prior
to 58–71 % and is worthless — and a large factor against raw English and monoalphabetic substitution,
which the IoC already excludes far more loudly.

Supporting detail: K4 has **2 singleton letters (M, Y)** against 2.25 expected under uniform;
χ² of the letter counts against uniform is **19.1 on 25 df** (95th percentile 37.7, 99th 44.3), i.e.
K4's letter distribution is *indistinguishable from flat*; χ² against English is **571.0**, i.e.
decisively not English.

---

## 4. (c) Doubled letters — unremarkable

`stat_c_doubles.py` → `stat_c_out.txt`

K4 has **6** adjacent doubles: `BB` `QQ` `SS` `SS` `ZZ` `TT` starting at 1-indexed
19, 26, 33, 43, 47, 68.

For an i.i.d. uniform source the count is **exactly Binomial(96, 1/26)** (successive differences are
i.i.d. uniform), mean 3.692, sd 1.884:

| k | 0 | 1 | 2 | 3 | 4 | 5 | **6** | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|---|
| P(exactly k) | .0232 | .0889 | .1690 | .2118 | .1970 | .1450 | **.0880** | .0452 | .0201 | .0079 |
| P(≥ k) | 1.000 | .9768 | .8879 | .7189 | .5071 | .3101 | **.1651** | .0772 | .0319 | .0118 |

**Exact P(≥ 6) = 0.1651**, z = +1.23. Cross-checked against 1,000,000 uniform draws (max
|MC − exact| = 0.00034 over k = 0…12). Six doubles is the 83rd–92nd percentile. Nothing.

Controls:

| text | n | doubles | expected | z | P(≥ obs) |
|---|---|---|---|---|---|
| K1 ciphertext | 63 | 1 | 2.38 | −0.91 | 0.912 |
| K2 ciphertext | 369 | 21 | 14.15 | +1.86 | 0.049 |
| K3 ciphertext | 336 | 18 | 12.88 | +1.45 | 0.099 |
| **K4 ciphertext** | **97** | **6** | 3.69 | **+1.22** | **0.165** |
| K3 plaintext | 336 | 8 | 12.88 | −1.39 | 0.946 |

K2's ciphertext is a *more* extreme double-count than K4's, and K2 is solved. Every candidate system
except raw English predicts ≈3.7 doubles with sd ≈1.9; 6 is compatible with all of them. **The
doubled-letter count discriminates nothing except "not raw English".**

### The positional folklore, corrected

Five of the six double positions (19, 26, 33, 47, 68) are ≡ 5 (mod 7). Naive p for that alone:
**0.0022**. But modulus 7 was chosen *after* seeing the lag-7 autocorrelation bump. The honest null
is the maximum over moduli of the largest residue class, for 6 positions drawn uniformly from 1…96
(1,000,000 trials):

* P(some modulus 2…48 collects ≥ 5 of the 6) = **0.2452**
* P(some modulus 2…48 collects all 6) = 0.0295

**Not significant.** It is what you always find when you pick the modulus after the fact.
(`geo2_c_lag7.py` independently measured 0.247 on 200,000 trials — agreement to three digits.)

The related claim that the doubles "concentrate in the last two columns of a 7×14 layout" is
indexing-dependent: at width 7 the six doubles sit in 0-indexed columns 4, 4, 4, 0, 4, 4 — five in
column 4 and one in column 0, not the last two columns at all. The corrected p above covers every
indexing.

Are the doubles unusually early? The last one starts at 68, so the final 28 adjacent pairs contain
none. P(all 6 uniform positions ≤ 68) = **0.1263**. Not significant either.

---

## 5. (d) Autocorrelation and the periodic-IoC scan — the lag-7 spike is dead

`stat_d_autocorr.py` → `stat_d_out.txt`

### The full lag spectrum

All 96 lags, coincidence counts against Binomial(97−d, 1/26). Total coincidences over all lags: 168
against 179.1 expected — K4 has *fewer* internal repeats than a random string, not more.

The eight largest standardised lags:

| lag | pairs | obs | exp | z | exact P(≥ obs) |
|---|---|---|---|---|---|
| **7** | 90 | 9 | 3.46 | **+3.04** | 0.00787 |
| 93 | 4 | 1 | 0.15 | +2.20 | 0.145 |
| 38 | 59 | 5 | 2.27 | +1.85 | 0.076 |
| 50 | 47 | 4 | 1.81 | +1.66 | 0.106 |
| 91 | 6 | 1 | 0.23 | +1.63 | 0.210 |
| 79 | 18 | 2 | 0.69 | +1.60 | 0.151 |
| 77 | 20 | 2 | 0.77 | +1.43 | 0.179 |
| 43 | 54 | 4 | 2.08 | +1.36 | 0.154 |

Note the degeneracy at long lags: at lag 96 there is a single pair, and one coincidence there would
score z = +4.99. Any "max z over lags 1–96" therefore has a null mean above +3 for purely arithmetic
reasons, which is why the ranges below are reported separately.

### Null distribution of the maximum — 1,000,000 replicates per null

| lag range scanned | observed max z | null mean | null 95th | **family-wise p** (uniform) | **family-wise p** (K4-letter shuffle) |
|---|---|---|---|---|---|
| 1–24 | 3.036 | 2.193 | 3.424 | **0.1091** | **0.0684** |
| 1–30 | 3.036 | 2.321 | 3.503 | **0.1364** | **0.0872** |
| 1–48 | 3.036 | 2.594 | 3.764 | **0.2185** | **0.1487** |
| 1–67 | 3.036 | 2.808 | 4.000 | **0.3199** | **0.2334** |
| 1–96 | 3.036 | 3.257 | 5.000 | **0.5571** | **0.4753** |

A better statistic than max-z (it does not suffer the small-m degeneracy) is the **minimum exact
binomial p over the scanned lags**. K4's is 0.00787 at lag 7, and its family-wise p is **0.3127**
(uniform null) / **0.2304** (shuffle null).

The only way to get a small number is to pre-specify lag 7 — P(Binomial(90, 1/26) ≥ 9) = 0.00787 —
and nobody did. At lags 1–96, the range actually searched, **the observed +3.04 is below the average
maximum of a random string (+3.26).**

This confirms and sharpens `geo2_c_lag7.py`, which measured 0.218 / 0.149 for lags 1–48 on 200,000
trials; here, on 1,000,000 trials, 0.2185 / 0.1487.

### Controls: every solved Kryptos section shows a bigger "spike"

100,000 replicates each, lag range 1–48:

| text | n | best lag | max z | null mean | null 95th | family-wise p |
|---|---|---|---|---|---|---|
| K1 ciphertext | 63 | 20 | **4.24** | 2.735 | 4.062 | 0.0343 |
| K2 ciphertext | 369 | 16 | **5.38** | 2.404 | 3.394 | 0.0001 |
| K3 ciphertext | 336 | 39 | **7.42** | 2.413 | 3.432 | 0.0000 |
| **K4 ciphertext** | **97** | **7** | **3.04** | 2.595 | 3.769 | **0.2201** |

K2 and K3 have genuine internal structure (a period-8 key, and a transposition of English) and their
autocorrelation finds it. K4's "spike" is the *weakest* of the four and the only one that fails to
reach significance.

### The periodic-IoC scan — K4 is flatter than random

The pooled column IoC at period p has exact null mean 1/26 and exact null variance 2p(1−p)/D(p),
where D(p) = Σ over columns of m(m−1) is the number of ordered within-column pairs. The simulation
reproduces those exact sds to 3–4 significant figures at every p checked (e.g. p = 28: MC 0.01733 vs
exact 0.01734), which validates the standardisation.

The reason raw periodic-IoC values "peak" at p = 25–30 is D(p) collapsing: at p = 28 the columns hold
3–4 letters and D(28) = 246, so the null sd of the pooled IoC is **0.0173** — a single accidental
repeat inside one column moves the statistic by ~0.02. Comparing a raw value at p = 28 against the
0.0385 baseline, as has been done, is comparing it against the wrong yardstick by a factor of 20.

Standardised properly, K4's **largest** periodic-IoC z over p = 2…48 is **+1.13, at period 25**
(IoC 0.05674, null sd 0.01620). Against the null of that maximum:

| null | mean of max-z | 95th pct | **family-wise p** |
|---|---|---|---|
| uniform random | +2.418 | +3.720 | **0.9913** |
| K4-letter shuffle | +2.196 | +3.386 | **0.9855** |

**K4's periodic-IoC profile is flatter than 99 % of random strings.** Far from showing a period, the
scan shows less period structure than chance. Reported z at the specific periods in question:
p = 25 → +1.13, p = 28 → **+0.13**, p = 30 → **−0.13**. The apparent peaks at 25/28/30 are entirely
the D(p) artefact.

This also explains a result already in `geometry.md` §2 from a different direction: 74 of 2,046
(order, period) pairs exceeded a 95th-percentile null where 102 were expected — below chance, for the
same reason.

---

## 6. (e) Kasiski — K4 has nothing for it to work on

`stat_e_kasiski.py` → `stat_e_out.txt`

### Every repeated n-gram in K4

**10 distinct repeated bigrams, 10 position pairs** (6.746 expected under uniform random).
**Zero repeated trigrams** (0.254 expected), zero 4-grams (0.0096 expected), nothing longer.

| bigram | positions (1-indexed) | gap | factors of the gap (≤48) |
|---|---|---|---|
| `QS` | 39, 42 | 3 | 3 |
| `SS` | 33, 43 | 10 | 2, 5, 10 |
| `SO` | 14, 34 | 20 | 2, 4, 5, 10, 20 |
| `DI` | 56, 84 | 28 | 2, 4, 7, 14, 28 |
| `TJ` | 51, 81 | 30 | 2, 3, 5, 6, 10, 15, 30 |
| `KZ` | 46, 78 | 32 | 2, 4, 8, 16, 32 |
| `FB` | 18, 62 | 44 | 2, 4, 11, 22, 44 |
| `EK` | 45, 93 | 48 | 2, 3, 4, 6, 8, 12, 16, 24, 48 |
| `GK` | 31, 86 | 55 | 5, 11 |
| `HU` | 10, 89 | 79 | — (79 is prime) |

Gaps sorted: 3, 10, 20, 28, 30, 32, 44, 48, 55, 79. **gcd = 1.**

### Factor table

| factor | gaps divisible | expected | ratio |
|---|---|---|---|
| 2 | 7 | 5.00 | 1.40 |
| 3 | 3 | 3.33 | 0.90 |
| 4 | 5 | 2.50 | 2.00 |
| 5 | 4 | 2.00 | 2.00 |
| 7 | 1 | 1.43 | 0.70 |
| 8 | 2 | 1.25 | 1.60 |
| 10 | 3 | 1.00 | 3.00 |
| 11 | 2 | 0.91 | 2.20 |
| 16 | 2 | 0.62 | 3.20 |
| 21 | 0 | 0.48 | 0.00 |

Best factor by excess is 4 (5 of 10 gaps against 2.50 expected). Note there is no excess at 7 (1 of
10 against 1.43 expected) — a second, independent reason not to build a search around lag 7.

### Positive control: the method works on K1 and K2

| text | n | trigram gaps | best factor | true period |
|---|---|---|---|---|
| K1 | 63 | 3 | 20 (3/3, exp 0.1) — and factor **10** also takes 3/3 | **10** (PALIMPSEST) |
| K2 | 369 | 18 | **8** (13/18, exp 2.2) | **8** (ABSCISSA) |
| K3 | 336 | 17 | 17 (3/17, exp 1.0) — no real period | none (transposition) |
| K4 | 97 | **0** | — | — |

K2 is the demonstration: its true period 8 falls straight out of the trigram gaps. **K4 has no
repeated trigram at all, so Kasiski on K4 has nothing to work with — that is the finding, and it is
not evidence of a long key.** Under the uniform null, a random 97-letter string has **no** repeated
trigram 78 % of the time (uniform) / 82 % (K4-letter shuffle). K4's zero is the ordinary outcome.

### Null distributions — 500,000 replicates per null

| statistic | obs | null mean (uniform) | P(≥obs) uniform | null mean (shuffle) | P(≥obs) shuffle |
|---|---|---|---|---|---|
| repeated bigram pairs | 10 | 6.742 | 0.1483 | 5.909 | 0.0713 |
| repeated trigram pairs | 0 | 0.255 | — [P(=0) = 0.782] | 0.207 | — [P(=0) = 0.818] |
| repeated 4-gram pairs | 0 | 0.010 | — | 0.007 | — |
| col-bigram **pairs** at width 21 | 11 | 4.215 | **0.00635** | 3.694 | **0.00160** |
| col-bigram **excess** at width 21 (Bean's convention) | 11 | 4.063 | **0.00155** | 3.593 | **0.00035** |
| MAX col-bigram **pairs**, widths 2–48 | 11 | 10.352 | **0.4191** | 9.370 | **0.2070** |
| MAX col-bigram **excess**, widths 2–48 | 11 | 9.476 | **0.2400** | 8.710 | **0.0903** |
| max gaps sharing one factor 2–24 | 7 | 3.709 | 0.0672 | 3.308 | 0.0351 |

### The width-21 anomaly, in two parts

**(i) The convention nobody states changes the answer by a factor of 5.** "Repeated column bigrams"
has two equally natural definitions: the number of unordered *pairs*, Σ v(v−1)/2, and the number of
*excess occurrences*, Σ (v−1). K4 scores **11 under both**, because no vertical bigram occurs three
times at width 21. The **nulls** differ, because a triple contributes 3 to the pairs count but only 2
to the excess count, so the pairs statistic has the heavier upper tail. On the same shuffle null:
excess gives p = 0.00035 (≈ 1 in 2,900), pairs gives p = 0.00160 (≈ 1 in 625). Bean's published
figure is ~1 in 6,750 on the excess convention; this repo's earlier `prior_art_bean_stats.py`
measured 1 in 3,226 for it on 200,000 trials, and the 500,000-trial figure here is 1 in 2,900 — same
order, and the **discrepancy with the pairs convention is entirely a definitional artefact, not a
disagreement about the data.** This is worth recording because the number has been quoted in the
literature without the convention attached.

**(ii) Selection over widths kills it either way.** Width 21 was chosen from among all the plausible
widths. Scoring the **maximum** over widths 2–48 against its own null:

* pairs convention: p = **0.419** (uniform) / **0.207** (shuffle)
* excess convention: p = **0.240** (uniform) / **0.090** (shuffle)

K4's best width *is* 21, with 11 — but the null mean of the best-of-47-widths is already 8.7–10.4.
**This is the strongest single anomaly in K4 and it still does not survive its own multiple-testing
correction under either convention.**

### The factor-concentration statistic, conditioned properly

Seven of K4's 10 bigram gaps are even, which is the largest single-factor concentration, and its
unconditional tail (0.067 uniform / 0.035 shuffle) is the smallest number anywhere in this section.
It is an artefact of compounding: that statistic partly re-measures the **gap count**, since a text
with more gaps can pile more of them onto one factor, and K4's 10 gaps are themselves on the high
side (p = 0.148 / 0.071). Conditioning on exactly 10 gaps removes the confound:

| null | P(max factor count ≥ 7 \| exactly 10 gaps) | replicates with 10 gaps |
|---|---|---|
| uniform random | **0.1969** | 30,090 of 500,000 |
| K4-letter shuffle | **0.2049** | 17,987 of 500,000 |

**Given 10 gaps, 7 of them sharing a factor is unremarkable.** Neither the gap count nor the factor
concentration given it is individually significant, and their product is not a test.

---

## 7. (f) Side-by-side profile, and which systems the numbers actually exclude

`stat_f_profile.py` → `stat_f_out.txt`

### The observed profiles

`maxZ` is the maximum autocorrelation z over lags 1–48 and `maxZper` the maximum standardised
periodic IoC over periods 2–30; both are maxima over a scan, so they are inflated by construction and
comparable across rows but not to 1.96.

| text | n | IoC | distinct | doubles | maxZ(1–48) | maxZper | rep. bigrams | rep. trigrams | χ²(unif) |
|---|---|---|---|---|---|---|---|---|---|
| K1 ciphertext | 63 | 0.03789 | 23 | 1 | 4.24 | 4.06 | 6 | 3 | 24.1 |
| K2 ciphertext | 369 | 0.04547 | 26 | 21 | 5.38 | 14.40 | 158 | 18 | 92.0 |
| K3 ciphertext | 336 | 0.06615 | 24 | 18 | 7.42 | 24.90 | 235 | 17 | 266.2 |
| **K4 ciphertext** | **97** | **0.03608** | **26** | **6** | **3.04** | **1.13** | **10** | **0** | **19.1** |
| K1–K3 plaintext | 769 | 0.06590 | 24 | 22 | 9.10 | 55.30 | 2299 | 497 | 572.8 |

**K4 is the one section of Kryptos with no detectable internal structure of any kind.** Every other
row, including the two that are solved, lights up on multiple statistics. The most striking column is
`maxZper`: 4.06 / 14.40 / 24.90 for K1/K2/K3 against **1.13** for K4.

### Simulated candidate systems

40,000 simulated 97-letter ciphertexts per system; plaintext = a random window of real English.

| system | IoC mean | IoC sd | distinct | doubles | maxZ | rep. bigrams | rep. trigrams |
|---|---|---|---|---|---|---|---|
| English plaintext | 0.06633 | 0.00748 | 20.15 | 2.99 | 5.57 | 38.36 | 11.42 |
| transposition of English | 0.06625 | 0.00753 | 20.15 | 6.36 | 4.39 | 20.11 | 1.33 |
| monoalphabetic substitution | 0.06622 | 0.00749 | 20.16 | 3.01 | 5.58 | 38.25 | 11.40 |
| Hill 2×2 | 0.04216 | 0.00475 | 24.93 | 3.80 | 3.59 | 16.67 | 3.70 |
| 5×6 fractionation (bifid-like), period 7 | 0.04792 | 0.00635 | 24.03 | 4.45 | 3.61 | 12.02 | 1.00 |
| Vigenère L=2 | 0.05235 | 0.00679 | 22.98 | 3.69 | 4.80 | 23.35 | 6.08 |
| Vigenère L=5 | 0.04403 | 0.00464 | 24.61 | 3.69 | 3.85 | 13.00 | 2.47 |
| Vigenère L=8 | 0.04181 | 0.00396 | 24.97 | 3.70 | 3.55 | 10.57 | 1.61 |
| Vigenère L=10 | 0.04116 | 0.00374 | 25.07 | 3.70 | 3.31 | 9.85 | 1.37 |
| Vigenère L=20 | 0.03965 | 0.00321 | 25.27 | 3.69 | 3.00 | 8.13 | 0.77 |
| Vigenère L=30 | 0.03918 | 0.00306 | 25.34 | 3.70 | 2.80 | 7.55 | 0.55 |
| Beaufort L=10 | 0.04111 | 0.00374 | 25.07 | 3.70 | 3.30 | 9.78 | 1.35 |
| Quagmire III (KRYPTOS) L=8 | 0.04182 | 0.00393 | 24.96 | 3.67 | 3.56 | 10.62 | 1.65 |
| Quagmire III (KRYPTOS) L=10 | 0.04114 | 0.00372 | 25.06 | 3.70 | 3.31 | 9.80 | 1.36 |
| general polyalphabetic p=10 | 0.04109 | 0.00367 | 25.07 | 3.68 | 3.31 | 9.84 | 1.37 |
| running key (English key) | 0.03980 | 0.00321 | 25.25 | 3.86 | 2.70 | 7.44 | 0.33 |
| plaintext autokey (primer 8) | 0.04032 | 0.00358 | 25.19 | 3.82 | 3.08 | 8.92 | 1.33 |
| ciphertext autokey (primer 8) | 0.03925 | 0.00314 | 25.33 | 3.70 | 2.97 | 6.67 | 0.26 |
| Gromark base-10 primer 5 | 0.03949 | 0.00319 | 25.29 | 3.55 | 2.68 | 7.19 | 0.28 |
| Gromark base-10 primer 8 | 0.03938 | 0.00309 | 25.30 | 3.58 | 2.66 | 7.12 | 0.27 |
| one-time pad | 0.03843 | 0.00281 | 25.42 | 3.69 | 2.60 | 6.73 | 0.25 |
| *K4 observed* | **0.03608** | — | **26** | **6** | **3.04** | **10** | **0** |

Two things are visible immediately. First, everything from key length ~10 upward — Vigenère,
Beaufort, Quagmire III, general polyalphabetic, running key, autokey, Gromark, one-time pad —
produces essentially the same profile. **These systems are not statistically distinguishable from one
another at n = 97, let alone from K4.** Second, the columns that do separate systems (IoC, repeated
trigrams) separate only the short-key end.

### Verdicts: K4 placed inside each candidate's own null

Two-sided p per statistic; a system is called IMPLAUSIBLE when some statistic puts K4 in the extreme
0.1 % of what that system produces. (Six statistics are screened per system, so a nominal 0.001
threshold corresponds to a family-wise ~0.006; the four systems below are excluded at p ≤ 5e−5 on the
IoC alone, so the distinction does not matter.)

| verdict | systems | driving statistic |
|---|---|---|
| **IMPLAUSIBLE** (p < 0.001) | **raw English plaintext**, **transposition of English**, **monoalphabetic substitution**, **Vigenère L = 2** | IoC (p ≈ 0 for the first three, 5e−5 for L=2) |
| disfavoured (0.001–0.01) | 5×6 fractionation period 7 (p = 0.008), Vigenère L = 3 (p = 0.004) | IoC |
| mild tension (0.01–0.05) | Vigenère L = 5 (p = 0.035), general polyalphabetic p = 5 (p = 0.031) | IoC |
| **compatible** | Hill 2×2, Vigenère L ≥ 7, Beaufort L=10, Quagmire III L=8 and L=10, general polyalphabetic p=10 and p=20, running key, plaintext autokey, ciphertext autokey, Gromark (primer 5 and 8), one-time pad | — |

**This is the complete list of what the statistics alone exclude.** Note in particular:

* **Transposition-only is excluded by the statistics**, independently of the crib argument
  (the cribs need three E's and the ciphertext has two). Two independent kills.
* **Hill 2×2 is statistically compatible** with K4 (p(IoC) = 0.124). The statistics do not touch it;
  the cribs do (`families.md`). The same is true of Gromark, which the ML classifiers favour: nothing
  in K4's statistics supports or opposes it.
* **Every system with an effective key length ≥ 7 is compatible.** That includes the one-time pad,
  which is the point: at n = 97 there is no statistical daylight between "long key" and "no
  structure at all".

### Omnibus: is there *any* detectable structure in K4?

Every K4 "anomaly" in the literature is one statistic picked after the fact from a battery. The
honest question is how surprising the **smallest** p in the battery is. Null = one-time pad over
English, i.e. exactly a uniform random 97-letter string; 40,000 replicates; battery of 7 statistics
(χ² dropped as a near-duplicate of the IoC).

| statistic | K4 value | two-sided p vs uniform |
|---|---|---|
| IoC | 0.0361 | 0.438 |
| distinct letters | 26 | 1.000 |
| doubles | 6 | 0.330 |
| max autocorrelation z (lags 1–48) | 3.036 | 0.431 |
| max periodic-IoC z (periods 2–30) | 1.129 | **0.131** |
| repeated bigram pairs | 10 | 0.293 |
| repeated trigram pairs | 0 | 1.000 |

K4's smallest p over the battery is **0.131** — and it belongs to `maxperz`, which is small because
K4 is *flatter* than random, not because it has structure. The null distribution of that minimum has
median 0.170 and 5th percentile 0.014, so:

```
OMNIBUS p = P(min-p <= K4's min-p | uniform) = 0.4142
```

The marginal CDFs are estimated from the same sample that supplies the null replicates, which biases
this *downward* — in favour of finding structure — and it is still 0.41. The one statistic not in the
battery is the width-21 column-bigram count, whose own selection-corrected p is 0.09–0.42 (§6), so
adding it could only raise the omnibus p.

**Conclusion: no statistic in the classical battery detects any structure in K4 once selection is
paid for. At n = 97, K4 is statistically indistinguishable from a uniformly random string of
letters.**

---

## 8. (f, continued) Statistical power at n = 97 — the honest boundary

`stat_g_power.py` → `stat_g_out.txt`

A negative result means nothing without power. This section asks the converse question: **at 97
letters, what could the classical tests have detected even in principle?** 200,000 simulated Vigenère
encipherments of random 97-letter English windows per key length.

Critical values used:

* **IoC test**: reject if IoC ≥ **0.04360** (S ≥ 406) — the exact 5 % point of the uniform null
  at n = 97. K4's 0.03608 is nowhere near it.
* **Periodic-IoC, ORACLE**: reject if z ≥ 1.645 *at the true period*. Maximally generous — it assumes
  the attacker is handed the period.
* **Periodic-IoC, SCANNED**: reject if max over p = 2…48 of z_p ≥ **3.720**, the 95th percentile of
  that maximum under the uniform null (measured in §5 from 10⁶ replicates). This is the test a real
  attacker can actually run.
* **Kasiski**: fires only if the text contains a repeated trigram whose gap is a multiple of the
  period.

| key length L | mean IoC | power: IoC | power: periodic IoC (oracle) | **power: periodic IoC (scanned)** | P(any repeated trigram) | power: Kasiski |
|---|---|---|---|---|---|---|
| 1 | 0.06629 | 1.000 | 1.000 | **0.994** | 0.991 | 0.991 |
| 2 | 0.05242 | 0.945 | 1.000 | **0.981** | 0.931 | 0.919 |
| 3 | 0.04790 | 0.774 | 0.997 | **0.916** | 0.850 | 0.823 |
| 4 | 0.04547 | 0.612 | 0.983 | **0.836** | 0.781 | 0.736 |
| 5 | 0.04403 | 0.496 | 0.970 | **0.739** | 0.714 | 0.652 |
| 6 | 0.04305 | 0.410 | 0.949 | **0.689** | 0.664 | 0.588 |
| 7 | 0.04235 | 0.345 | 0.923 | **0.572** | 0.618 | 0.527 |
| 8 | 0.04183 | 0.299 | 0.870 | **0.537** | 0.587 | 0.487 |
| 9 | 0.04144 | 0.263 | 0.839 | **0.492** | 0.559 | 0.450 |
| 10 | 0.04111 | 0.234 | 0.835 | **0.450** | 0.533 | 0.418 |
| 12 | 0.04062 | 0.192 | 0.735 | **0.397** | 0.484 | 0.354 |
| 14 | 0.04027 | 0.164 | 0.701 | **0.310** | 0.451 | 0.311 |
| 16 | 0.04000 | 0.143 | 0.653 | **0.299** | 0.423 | 0.272 |
| 18 | 0.03983 | 0.130 | 0.659 | **0.264** | 0.403 | 0.246 |
| 20 | 0.03965 | 0.118 | 0.586 | **0.206** | 0.383 | 0.221 |
| 24 | 0.03940 | 0.103 | 0.520 | **0.203** | 0.353 | 0.180 |
| 26 | 0.03932 | 0.098 | 0.537 | **0.158** | 0.343 | 0.167 |
| 28 | 0.03924 | 0.092 | 0.433 | **0.158** | 0.331 | 0.151 |
| 30 | 0.03917 | 0.088 | 0.458 | **0.161** | 0.320 | 0.137 |

(The scanned column is mildly non-monotone in L because the resolution of the scan depends on D(p),
which jumps around with the divisibility of 97 by p.)

### The three numbers that bound everything

* **The plain IoC test has ≥ 50 % power only for L ≤ 4.**
* **The periodic-IoC test, told the true period, has ≥ 50 % power for L ≤ 26.**
* **The periodic-IoC test as actually runnable — scanned, multiple-testing-corrected — has ≥ 50 %
  power only for L ≤ 8.**

Kasiski never really fires. A 97-letter text contains *any* repeated trigram only 32–59 % of the time
even when enciphered with a short key, so K4's zero repeated trigrams carries almost no information.

### Corpus independence

The whole analysis was re-run with **Sanborn's own English** (the K1–K3 plaintexts) as the plaintext
source instead of the 22.4 M-letter corpus, at L = 2, 5, 8, 10, 15, 20, 30. The largest disagreement
in mean IoC is 0.0008 (L = 2: 0.05250 vs 0.05329) and the largest disagreement in power is 0.05
(L = 8: 0.298 vs 0.348); at L = 10 and 20 the two agree to within 0.003. **Nothing here depends on
the choice of English.**

### What this means for every negative in this project

At 97 letters the classical statistics are blind beyond an effective key length of about **8**.
Every negative that rests on statistics alone therefore applies only to the short-key end of the
space. In particular:

* Periods 27, 28, 29 and every period ≥ 53 impose **zero** crib constraints (`geometry.md` §3) **and**
  fall in the region where the scanned periodic-IoC test has ≤ 16 % power. Those periods are not
  "ruled out by statistics" — they are **unexamined**, by both available tools simultaneously.
* Conversely, the region where the statistics do have power (L ≤ 8) is exactly the region the cribs
  already demolish with 11–22 independent constraints. The two tools overlap where they are least
  needed and both fail where the answer might be.

---

## 9. Corrections to claims standing in this repo and in the literature

| where | claim as stated | correction |
|---|---|---|
| `README.md` §3.1 | "The flat-to-sub-random IoC is the central fact about K4: it is what Scheidt's 'masking' remark predicts" | The IoC is not sub-random in any measurable sense: 21.6th percentile of the exact null, z = −0.84. It is consistent with masking, but it is equally consistent with **no** masking and a key of length ≥ 9, and with a plain one-time pad. It is not evidence for anything and should not be described as "the central fact". |
| `README.md` §3.1 | "with 24 lags tested, a single +3.0 outlier has a multiple-comparison p of roughly 0.03" | Understated by a factor of 4–19. The exact family-wise p over lags 1–24 is **0.109** (uniform null) / **0.068** (shuffle null); and the search that produced the claim actually ranged over all 96 lags, where the family-wise p is **0.557** / **0.475**. |
| `prior_art.md` §A.6 | "IoC 0.03608, below uniform random — this is *designed*, per Scheidt's masking statement" | The observation cannot support the inference. 21.6 % of random strings are at least this flat. Scheidt's statement may well be true; the IoC is not the evidence for it. |
| `prior_art.md` §A.6 | "Excess column-bigram repeats at width 21 … Width 21 is the one non-random geometry in the ciphertext" | The nominal figure (~1 in 3,000 on the excess convention) reproduces, at 1 in 2,900 on 500,000 replicates. But corrected for the selection of width 21 out of widths 2–48, p = **0.090–0.419** depending on the (unstated) counting convention. It is not "non-random geometry"; it is the largest of 47 scanned values. |
| `prior_art.md` recommendation 3 | "Treat the width-21 column-bigram excess as the live phenomenon … no one has proposed a replacement [explanation]" | **Withdraw this recommendation.** There is nothing to explain. The corrected p is 0.09–0.42, and the null mean of the best-of-47-widths is 8.7–10.4 against K4's 11. Bean's framing (find, measure, explain, exploit) stopped at "measure" because the measurement, properly corrected, says there is no phenomenon. |
| literature (Bean, HistoCrypt 2021) | width-21 column-bigram excess, "~1 in 6,750" | Reproduces to within a factor of ~2 on the same convention. The figure is nominal, not selection-corrected. Also note the convention ambiguity: the same observation scores 1 in 2,900 (excess) or 1 in 625 (pairs) on an identical null, and neither survives the width scan. |
| community folklore | "doubled letters concentrate mod 7 / in the last two columns of a 7×14 grid" | Corrected p = **0.245** over moduli 2–48; the 7×14 column claim is indexing-dependent (the doubles sit in 0-indexed columns 4,4,4,0,4,4 at width 7). |
| community folklore | "periodic-IoC peaks at periods 25, 28, 30" | Artefact of the collapsing within-column pair count D(p). Standardised, those periods score z = +1.13, **+0.13**, **−0.13**; K4's whole periodic profile is flatter than 99 % of random strings. |

Two earlier results in this repo are **confirmed and tightened**, not corrected:

* `geometry.md` §4 measured the lag-7 family-wise p as 0.218 (uniform) / 0.149 (shuffle) over lags
  1–48 on 200,000 trials. On 1,000,000 trials: **0.2185 / 0.1487**.
* `geo2_c_lag7.py` measured P(some modulus 2–48 collects ≥ 5 of the 6 doubles) = 0.247 on 200,000
  trials. On 1,000,000 trials: **0.2452**.
* `sanborn_statements.md` §Group 4 already carries the corrected IoC and coverage figures
  (z = −0.84, P = 0.22; P(all 26) = 0.54). They are this suite's numbers and they stand.

---

## 10. Consequences for search design

1. **Do not use K4's ciphertext statistics as a search signal, a fitness function, or a filter.**
   There is no information in them beyond the short-key exclusions in §7. A search that prioritises
   candidates because they "explain the lag-7 spike", "explain the width-21 column bigrams", or
   "reproduce the sub-random IoC" is fitting noise, and will be wrong in proportion to how well it
   fits.

2. **The IoC cannot rank hypotheses.** Everything from Vigenère L = 9 through a one-time pad produces
   K4's IoC with probability between 0.06 and 0.22. Any argument of the form "system X gives a flat
   IoC, therefore X" is worthless: so does every other candidate.

3. **Kasiski offers no handle at all.** Zero repeated trigrams (ordinary: P = 0.78 under the uniform
   null), gcd of the ten bigram gaps = 1, no factor enriched beyond chance, and the one apparently
   concentrated factor evaporates once conditioned on the gap count. There is nothing to exploit.

4. **The cribs are the only real constraint the ciphertext supplies**, and they are silent exactly
   where the statistics are blind (periods 27, 28, 29 and ≥ 53). That intersection is the genuine
   open region, and it can only be attacked by *hypothesis* — a specific, documented method — never
   by statistical search. This is the quantitative version of the point already made in
   `geometry.md` §3.

5. **Use statistics on the plaintext side, not the ciphertext side.** An English-ness score on a
   candidate decryption is a test with real power; a statistic on the 97 ciphertext letters is not.
   The project's standing bar — 24/24 cribs **and** English — is the right one, and nothing in this
   report weakens it.

6. **Protocol for any future "anomaly".** Before it is reported, compute (i) the null distribution of
   the statistic, (ii) the null distribution of the *maximum* of that statistic over every choice
   that was scanned to find it (width, modulus, lag, period, reading order, offset), and (iii) the
   p-value against (ii), not (i). `stat_common.py` supplies the exact IoC lattice DP, exact binomial
   and coupon-collector formulas, seeded uniform and shuffle letter pools, and an English corpus, so
   this costs minutes. Every anomaly in the K4 literature that has been put through step (ii) has
   died there.
