# Liber Primus LP2: key restarts at headings, and heading cribs against large key libraries (2026-11-13/14)

Both attacks rest on one idea from LP1. LP1's ciphers restart their key at section boundaries:
- the Vigenère pages restart DIVINITY / FIRFUMFERENFE per section;
- page 56 runs φ(prime) *from the first prime* starting at its title, "AN END".

If LP2 does the same with a generated key, two things follow:
- each section's opening is encrypted with the **first terms** of the key, which is exactly what reference tables such as the OEIS list;
- each section's **heading** is a short, guessable plaintext. A guessed heading turns into an exact pattern of key differences, and that pattern can be looked up in a large library of candidate keys.

**Result: negative for both.**
- **Part A (restart):** no OEIS sequence decrypts any LP2 section, page or heading opening. Restart points score exactly like random mid-text points, and the best hits decode as noise.
- **Part B (crib):** guessed headings matched the library no more often than random patterns did, and no match decodes the text after its heading.

Both searches recover planted keys.

Scripts:
- [`analysis/lp_restartsearch.py`](../analysis/lp_restartsearch.py): Part A, including plants, report and power check.
- [`analysis/lp_cribsearch.py`](../analysis/lp_cribsearch.py): Part B.

Outputs:
- [`restartsearch_run.txt`](restartsearch_run.txt) and [`restartsearch_out/results.json`](restartsearch_out/results.json);
- [`cribsearch_run.txt`](cribsearch_run.txt) and [`cribsearch_out/verified.json`](cribsearch_out/verified.json).

The OEIS data (`stripped.gz`, 401,367 sequences, from oeis.org) is third-party and kept out of git under `cicada/data/oeis/`.

Both parts use the cipher model of the earlier sessions ([`lp2_skipsearch.md`](lp2_skipsearch.md), [`lp2_repairrules.md`](lp2_repairrules.md)):

```
c = sp·p + sk·K[j] + a  (mod 29, Gematria order; sp, sk = ±1; a = 0..28)
```

Collisions with the previous rune are repaired 81% of the time. Both the **skip** rule (use the next key value) and the **stay** rule (write the rune with no key and hold the key) are decoded. The aligned rules (flip, reroll, literal with the key used up) are covered by the skip decoder, as shown in `lp2_repairrules.md` §3.

## Part A: every OEIS sequence as a key restarted at every break

### What was searched

| | |
|---|---|
| Keys | Every OEIS sequence with ≥ 30 listed terms, reduced mod 29. The first 42 terms must contain ≥ 15 distinct residues and ≥ 15 distinct differences; the rest are excluded because LP2's flat unigrams (IoC 0.9999) rule out keys with only a few residues. After removing duplicates mod 29 this leaves **119,521 sequences** (median 48 terms). The key starts at term 0, 1 or 2, to allow for leading 0/1 terms. Both key signs are tried. |
| Restart points (73) | Every point where LP2's layout marks a break and at least 26 runes follow in the same file: 9 file starts, 5 headings (lines of ≤ 5 words ending in ⁜), 14 runes after a ⁜ chapter mark, and 45 page starts. |
| Decoding | A beam of 12 over the skip or stay ambiguities, run over up to 56 runes. Every surviving path is scored with the English rune model (War and Peace in runes with LP2's own word breaks), maximised over all 58 output maps `(sp, a)`. A window is scored on its first 26, 36 and 56 runes, but only for sequences with enough listed terms: all of them for 26 runes, 76% for 36, and 25% for 56. |
| Chance level | The identical search at 24 **control** positions: random mid-text points at least 60 runes from any break, where no restart is expected. A control's best score is the chance maximum over 717,126 key rows × 58 maps. |
| Volume | 717,126 rows × 2 modes × 97 positions ≈ 139 M beam decodes. Each scores all 12 paths under 58 maps. Run time was 21 min on 6 cores. |

**Correction made during the run.** The first pass took the beam path with the most coincidences, as the 100-rune skip search did. Over windows this short that rule picks the wrong path when a repair falls in the window. A planted stay-rule key was missed at 36 runes for this reason.

A synthetic test measured how often each rule recovers the true path. It used 240 planted English windows at LP2 restart points with random keys, half skip and half stay:

| Path selection | 26 runes | 36 runes | 56 runes |
|---|---|---|---|
| Most coincidences | 93% | 90% | 82% |
| Best English score over all 12 paths | 100% | 100% | 100% |

The search was rerun with English selection. Every result below comes from the rerun.

### Planted keys

Three OEIS sequences were planted as restarted keys in real LP2 positions, with War and Peace words filling LP2's word skeleton. Each was then searched against all 119,521 sequences:

| Planted key | Position, rule | 26 runes | 36 runes | 56 runes |
|---|---|---|---|---|
| A282544 (61 terms), sk +1, (1, 0) | file start 1874, skip | **found**, −2.600 (2nd −2.831) | **found**, −2.591 (2nd −3.166) | **found**, −2.595 (2nd −3.634) |
| A332304 (46 terms), sk −1, (1, 11) | page start 3194, stay | **found**, −2.491 (2nd −2.808) | **found**, −2.504 (2nd −3.059) | sequence too short |
| A157321 (38 terms), sk +1, (−1, 25) | heading 1541, skip | **found**, −2.228 (2nd −2.877) | **found**, −2.345 (2nd −3.157) | sequence too short |

Every plant is recovered at every length its sequence covers, with the exact sequence, start, key sign and output map. The decodes read as the planted text, for example "CNOW PAULOUNA WAS THE DUC POLITICAL SOUL NOT FEARNG…".

### Power

Would a real English opening score above the chance ceiling? Here the ceiling is the highest control score in either mode. The test filled the skeletons of all 73 restart points with War and Peace text, 40 samples each:

| | 26 runes | 36 runes | 56 runes |
|---|---|---|---|
| Chance ceiling (highest control score) | −2.641 | −2.883 | −3.431 |
| English openings, median (5th percentile) | −2.463 (−2.783) | −2.458 (−2.732) | −2.453 (−2.676) |
| Share of English openings above the ceiling | **83%** | **99%** | **100%** |

The 26-rune test is the weak one. A best-of-42-million chance decode over 26 runes reaches −2.64, which is close to English. It is the only test for sequences with 30–37 terms, 24% of the set. Longer sequences also get the 36-rune test, where power is 99%.

### Results

The table gives the highest score at each position, with medians and maxima across positions. A key restarted at a break would push some restart points far above every control.

| Rule, length | Controls (24): median / max | Restart points (73): median / max | Restart points above the control max (expected 2.9) | Rank-sum z |
|---|---|---|---|---|
| skip, 26 runes | −2.811 / −2.645 | −2.804 / −2.611 | 2 | +0.04 |
| skip, 36 runes | −3.148 / −2.891 | −3.148 / −2.886 | 1 | +0.09 |
| skip, 56 runes | −3.650 / −3.484 | −3.633 / −3.300 | 3 | +0.13 |
| stay, 26 runes | −2.810 / −2.641 | −2.808 / −2.640 | 1 | −0.54 |
| stay, 36 runes | −3.155 / −2.883 | −3.151 / −2.895 | 0 | +1.16 |
| stay, 56 runes | −3.611 / −3.431 | −3.618 / −3.352 | 1 | −0.23 |

The restart points are indistinguishable from the controls: 8 exceed the control maximum against about 17 expected across the six rows. The best restart hits sit at most 0.18 nats per rune above the control maximum, and far below a planted key of the same length (−3.30 against −2.60 at 56 runes). They decode as noise:

- skip, 56 runes, page 8174, A316749: "ST LE HE OPPU. SAT URS. LCITSB TTEUU NCNGN LO MFIGURE…"
- skip, 56 runes, heading 9519, A236178: "CES. YUTR IMEEPA OXANU WETHEA ALI DCNGSO…"
- skip, 26 runes, after ⁜ 3623, A216380: "TYOF THECCE TLFFOW CRTAI SIEULE FEAR XEAL…"

**Out of sample.** Each position's best hit at 26 and 36 runes was decoded through the rest of its window, using the hit's own map. Positions with fewer than 10 further runes were skipped.

| | Controls: median / max | Restart points: median / max | Restart points above the control max (expected) |
|---|---|---|---|
| skip, from 26 runes | −5.581 / −3.814 | −5.662 / −3.702 | 1 (2.6) |
| skip, from 36 runes | −5.551 / −4.289 | −5.492 / −4.186 | 2 (4.5) |
| stay, from 26 runes | −5.355 / −3.921 | −5.611 / −3.702 | 1 (3.0) |
| stay, from 36 runes | −5.993 / −3.813 | −5.862 / −4.229 | 0 (2.8) |
| planted keys | | −2.30 to −2.65 | |

Nothing continues as language.

## Part B: guessed headings against 593 M key values

### Method

If the heading's plaintext `p` is guessed correctly, the ciphertext gives the key's *differences* across the heading exactly:

```
K[t+1] − K[t] = sk·((c[t+1] − c[t]) − sp·(p[t+1] − p[t]))      (mod 29)
```

The shift `a` cancels, so one guess gives four exact patterns, one per `(sp, sk)`. Each pattern is looked up at every position of every stream in the library. A match fixes the key index and `a`, and the 100 runes after the heading are then decoded from that index with the beam, under both the skip and stay rules.

This finds a key at any offset of any library stream, whether the key runs continuously through LP2 or restarts at the heading. It assumes no collision repair inside the heading itself.

**Headings.** A heading is text from a line, page or file start up to the next ⁜, at most 5 words, with no other punctuation. Nine LP2 headings have at least 9 runes, which gives at least 8 constrained differences.

**Guesses.** Each guess combines words whose rune lengths match the heading's word lengths. The vocabulary is every word on the solved LP1/LP2 pages, most frequent first, then the commonest War and Peace words, up to 400 per length. Combinations are capped at 300,000 per heading by keeping the most frequent words of each length; three- and four-word headings get about 66 words per slot.

**Control.** The identical search was run with random rune strings of the same word lengths, the same number per heading. Chance matches occur at the same rate for real and random guesses, so a real heading should stand out against this control.

### Library: 593,069,527 key values (mod 29)

| Library | Contents | Values |
|---|---|---|
| Hash chains | md5, sha1, sha256 and sha512 chains seeded with each of 4,478 vocabulary words in 3 cases (53,736 chains), 8,000 bytes mod 29 each | 430 M |
| Square roots | √n for the 969 non-squares n ≤ 1000: 20,000 decimal digits in 1-, 2-, 3- and 4-digit groups at every phase (10 readings), plus 14,000 base-29 digits | 91 M |
| Python PRNGs | seeds 0–2000; Python 3 `randrange(29)` and Python 2 `int(random()·29)`, 8,000 values each | 32 M |
| Cube roots | ∛n for the 195 non-cubes n ≤ 200, read the same way as the square roots | 18 M |
| OEIS | all 401,367 sequences, every listed position | 18 M |
| Earlier streams | the 104 streams of [`lp2_skipsearch.md`](lp2_skipsearch.md) | 3 M |
| Constants | π, e, φ, ln 2, read the same way as the square roots | 0.4 M |

### Planted controls

Each plant encrypts a heading guess from the vocabulary, plus the 200 runes after it, with a library stream. The text after the heading is LP2's word skeleton filled with War and Peace words. The search then runs blind over that stream's whole library chunk. The output is in [`cribsearch_plants.txt`](cribsearch_plants.txt).

| Heading, planted guess | Key, rule | Repairs after the heading | Top verified hit | Score (100 runes after the heading) | Words decoded correctly |
|---|---|---|---|---|---|
| 1541, YOUR I ONLY IS | √7 4-digit phase 1 from index 1234, skip | 7 | √7 4-digit phase 1, index 1234 | −2.945 | 85% |
| 5506, THE MOMENT WAY NEUER | primes (A000040) from index 2, stay | 5 | A086801 (primes − 3, the same key up to `a`), index 2 | −2.380 (38 runes: the sequence ends) | 100% |

The first plant's continuation reads "TRIUMPH UIRTUE READ MEN IAX EDEES YOUNG OUERCOME AUTHORITY POWER…". The garbled words are skip points where the beam guessed wrong.

### Results

Real and random guesses matched the library equally often: 760 matches against 819, against about 810 expected by chance. The breakdown by heading:

| Heading (rune index, file) | Runes | Word lengths | Guesses | Expected chance matches | Matches, real guesses | Matches, random guesses |
|---|---|---|---|---|---|---|
| 0 (file 0) | 13 | 8, 5 | 160,000 | 0.001 | 0 | 0 |
| 729 (file 1) | 16 | 2, 11, 3 | 287,496 | ≈ 0 | 0 | 0 |
| 1541 (file 1) | 11 | 4, 1, 4, 2 | 300,000 | 1.7 | 1 | 2 |
| 3603 (file 3) | 9 | 4, 5 | 160,000 | 759 | 692 | 761 |
| 3612 (file 3) | 11 | 4, 2, 5 | 287,496 | 1.6 | 1 | 3 |
| 5506 (file 4) | 16 | 2, 6, 3, 5 | 250,000 | ≈ 0 | 0 | 0 |
| 6527 (file 5) | 19 | 3, 12, 4 | 278,784 | ≈ 0 | 0 | 0 |
| 7960 (file 6) | 10 | 2, 8 | 52,400 | 8.6 | 4 | 8 |
| 12648 (file 8) | 9 | 1, 8 | 9,600 | 46 | 53 | 34 |

The four headings of 13 runes or more were the most sensitive part of the search: a single chance match was expected about once in a thousand runs, so any match there would have been a strong signal. There were none. On the short headings, matches occur at exactly the chance rate.

**Decoding after the heading.** Each match was decoded under both rules:

| | n | Median score | Best score |
|---|---|---|---|
| Real-guess matches | 1,508 | −5.810 | −4.701 |
| Random-guess matches | 1,616 | −5.789 | −4.525 |
| Planted keys | 2 | | −2.945, −2.380 |

The best real match is md5('cnows') under the guess MAID FIRES. It reads "EIMM FF HOMUNG. TAAEU NOCEY…", which is noise.

## An aside: the check compares runes, not letters

This is a re-check within files, recorded so it is not rediscovered as a lead.
- **Not suppressed:** pairs whose Latin forms repeat a letter at the junction (T→TH, EA→A, …): 369 against 340 expected.
- **Off-diagonal pairs are clean:** the 812 pairs of different runes run from z = −2.82 to +3.51, with 2 beyond |z| = 3 against 2.2 expected.

So the anti-repeat check compares rune identity, not Latin spelling. The small excess at difference d = 9 noted in `lp2_repairrules.md` §2 is spread across files, not concentrated in one, which fits noise.

## Coverage after this session

**Excluded:**
- **Part A.** An OEIS sequence (≥ 30 terms, flat mod 29) used as an additive key from its first terms, restarted at any of LP2's 73 marked breaks, under either repair rule, with English plaintext and standard Gematria order. Power is 83 to 100%, depending on how many terms the sequence lists.
- **Part B.** Any of the nine headings, if its plaintext is among the guesses, encrypted with consecutive values of any of the 593 M library values at any offset, whether the key is continuous or restarted, with no repair inside the heading. The plants show that such a key is found and decodes the following text far above chance.

**Not covered:**
1. Sequences with fewer than 30 terms, or not in the OEIS. The `b-files` with longer term lists were not used.
2. Restarts at points LP2's layout does not mark.
3. A collision repair inside the heading itself (Part B). For a 10-rune heading the probability is about 25%.
4. Headings whose words fall outside the guess vocabulary: names, rare words, non-English words.
5. Keyed alphabets, multiplicative keys, and non-English plaintext, as in every search so far.
