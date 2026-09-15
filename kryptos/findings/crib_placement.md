# Crib placement — are the four K4 cribs where everybody thinks they are?

Line of attack: **challenge the assumption the whole field is built on.** If the Sanborn crib
positions are off by one, every published K4 cryptanalysis, including every negative in this
repository, is void. The worry is not idle: Sanborn's own 2006 K2 correction was exactly a
one-letter shift caused by a carving error, and he misspells on purpose in every solved section
(IQLUSION, UNDERGRUUND, DESPARATLY).

Written 2026-09-13. Scripts `analysis/crib_lib.py`, `crib_a_variants.py`, `crib_b_shifts.py`,
`crib_c_sources.py`, `crib_d_anneal.py`, `crib_e_ptct.py`; raw logs `findings/crib_a_out.txt`,
`crib_b_out.txt`, `crib_c_out.txt`, `crib_d_out.txt`, `crib_e_out.txt`.

---

## 0. Bottom line

**The crib positions are correct and are now verified from primary sources, not inherited.** They
are self-verifying: each release states *both* an index range *and* the ciphertext letters found
there, and those two facts are simultaneously true under exactly one indexing convention — the one
this repo uses. `data/cribs.json` needs no change.

The off-by-one hypothesis is dead in a strong sense: not only does the standard placement survive,
but **68.5 million** placement/variant × period × combo consistency tests over shifted, re-worded,
re-indexed and re-read cribs produced **no survivor carrying more than 4 of the possible 22
constraints**, and that one stratum had 1 hit against 3.53 expected by chance. Every stratum
c ≥ 5 is empty. A real solution would sit at c = 22.

One genuine weakness was found, and it is *not* a positional error: **the EAST crib has materially
weaker provenance than the other three**, and two incompatible accounts of how it was released are
in circulation. Sliding the EASTNORTHEAST block alone, with BERLINCLOCK nailed down, still finds
nothing — so the weakness does not currently buy anything, but it is the one place a future
correction could land.

Secondary result worth carrying forward: **"the plaintext is deliberately misspelled" is not an
explanation for failing to recognise it.** Measured on Sanborn's own three misspellings, a
deliberate misspelling costs 0.02–0.14 of quadgram log-probability; the gap between English and
random is 3.5. Misspelling tolerance cannot rescue a search that is otherwise 3.5 away from English.

---

## 1. Task (a) — verification of the positions from primary sources

This was done first and matters most. All four releases were retrieved and quoted verbatim; the
*New York Times* articles came back through the Internet Archive because nytimes.com refuses
automated fetches. Full text and URLs in `crib_c_out.txt`.

### 1.1 What each source actually says

| crib | source | exact wording | gives index? | gives ciphertext? |
|---|---|---|---|---|
| **BERLIN** | John Schwartz, *"Clues to Stubborn Secret in C.I.A.'s Backyard"*, **NYT, published online Nov 20 2010, print Nov 21 2010 p. A1** ([archived](https://web.archive.org/web/20120101102610/http://www.nytimes.com/2010/11/21/us/21code.html)) | "He has provided The New York Times with the answers to six letters in the sculpture's final passage. The characters that are the **64th through 69th** in the final series on the sculpture read **NYPVTT**. When deciphered, they read **BERLIN**." | yes | **yes** |
| **CLOCK** | John Schwartz, *"Sculptor Offers Another Clue in 24-Year-Old Mystery at C.I.A."*, **NYT, Nov 20 2014, print Nov 21 2014 p. A16** ([archived](https://web.archive.org/web/20160101034413/http://www.nytimes.com/2014/11/21/us/another-kryptos-clue-is-offered-in-a-24-year-old-mystery-at-the-cia.html)) | "The **64th through 69th** characters of the final panel, when deciphered, spelled out the word BERLIN. […] five additional letters, those in the **70th through 74th** position. They spell 'clock.' This means that the letters from **positions 64 to 74** spell out two words: 'Berlin clock.'" | yes | no |
| **NORTHEAST** | John Schwartz & Jonathan Corum, *"This Sculpture Holds a Decades-Old C.I.A. Mystery. And Now, Another Clue."*, **NYT, Jan 29 2020** ([archived](https://web.archive.org/web/20201208072511/https://www.nytimes.com/interactive/2020/01/29/climate/kryptos-sculpture-final-clue.html)) | "The 2010 clue was the word BERLIN, in the **64th through 69th** positions of that final passage. In 2014 he revealed the word CLOCK in the next five, **70 through 74**. […] the word **NORTHEAST**, at **positions 26 through 34**." | yes | no |
| **EAST** | No article. Released by Sanborn **as an image of the K4 layout**, emailed to individual correspondents from **April 2020**, surfaced publicly **August 24 2020** via John Schwartz ([@jswatz](https://web.archive.org/web/20240314154346/https://twitter.com/jswatz/status/1297658577914667008), cited by Wikipedia); relayed by [Intel Today](https://inteltoday.org/2020/09/28/the-kryptos-sculpture-jim-sanborn-this-is-the-third-and-to-be-sure-final-clue-update-and-now-a-4th-clue/) | Intel Today: "The 4th Clue — The four letters in **positions 22-25**, cipher-text **FLRV**, are **EAST** in the plain-text." Sanborn, quoted by Schwartz: "I don't do much that's inadvertent… I released this layout to several people as early as April [2020] to spice things up during this unprecedented time and to see how long it would take to flow through the community." | indirectly (from the image) | community read-off |

Additional primary anchor, independent of the press: **Elonka Dunin's contemporaneous notes from a
March 2019 lunch with Sanborn**, reproduced at [rumkin.com/reference/kryptos/k4](https://rumkin.com/reference/kryptos/k4/) —
"Jim backed off and said he would only commit to the fact that K4 is exactly 97 characters long,
and that **BERLIN is plaintext that starts at exactly the 64th character**, but he wouldn't go
further than that." That is Sanborn himself, in person, restating position 64.

### 1.2 Elonka Dunin's layout, parsed character by character

`elonka.com/kryptos/` (fetched 2026-09-13; it does respond to a plain `curl` with a browser
user-agent, contrary to the note in `README.md` §5) publishes the cribs as a **picture** of the
4/31/31/31 K4 row layout rather than as numbers:

```
                                       ....
            .................EASTNORTHEAST.
            ............................BER
            LINCLOCK.......................
```

Concatenated it is exactly 97 characters, its row widths are exactly the carved `4, 31, 31, 31`,
and the letter runs land at **1-indexed 22–34 over ciphertext FLRVQQPRNGKSS** and **64–74 over
NYPVTTMZFPK**. A picture and a set of ordinals, produced independently, pick out the same 24
letters.

### 1.3 The decisive arithmetic: the index and the ciphertext confirm each other

Because the 2010 release states two independent facts about the same window — where it is *and*
what is there — only one indexing convention can satisfy both. Nine candidate conventions tested
(`crib_c_sources.py` §A1):

| convention | letters at "64–69" | at "70–74" | at "26–34" | at "22–25" | all match? |
|---|---|---|---|---|---|
| **K4, 1-indexed (the standard)** | **NYPVTT** | **MZFPK** | **QQPRNGKSS** | **FLRV** | **yes** |
| K4, 0-indexed | YPVTTM | ZFPKW | QPRNGKSSO | LRVQ | no |
| `?`+K4, 1-indexed — *the task (c) hypothesis* | BNYPVT | TMZFP | VQQPRNGKS | WFLR | **no** |
| `?`+K4, 0-indexed | NYPVTT | MZFPK | QQPRNGKSS | FLRV | yes (same map) |
| K4 counted from the end | SSKGNR | PQQVR | FZMTTVPYN | GWKP | no |
| whole left panel incl. `?` | VFPJUD | EEHZW | HGNFIVJYQ | KRNS | no |
| whole left panel, letters only | VFPJUD | EEHZW | HGNFIVJYQ | KRNS | no |
| last four panel rows (= K4) | WTQSJQ | SSEKZ | W?OBKRUOX | VDOH | no |
| final panel row only | off end | off end | off end | UHUA | no |

Exactly two conventions pass, and they are the **same map** — prefixing the `?` and switching to
0-indexing are inverse shifts that cancel. So the admissible reading is unique, and it is the one
already in `data/cribs.json`.

This settles **task (c) on documentary grounds before any cryptanalysis**: if Sanborn had counted
the `?` that ends K3, his own 2010 sentence would have had to read "the 64th through 69th … read
**BNYPVT**". It reads NYPVTT.

### 1.4 Each quoted ciphertext string is unique inside K4

`NYPVTT`, `MZFPK`, `QQPRNGKSS` and `FLRV` each occur exactly once in the 97 letters (and once in
the whole 865-letter panel). For BERLIN — the one crib whose ciphertext string Sanborn published —
**the string alone pins the window and the index number is redundant**, so a reporting off-by-one
literally could not have moved it.

### 1.5 Cross-carving check: *Antipodes*

*Antipodes* (1997, Hirshhorn) carries the Kryptos text twice. In the community transcription held
in this session's scratch copy, **both** occurrences of K4 reproduce the 97 letters
character-for-character against the Kryptos carving, and in both the character immediately
preceding `OBKR` is the `?` that ends K3. If that transcription is right, K4 contains no carving
discrepancy of the K2 kind, and the 97-letter length every index is counted over is confirmed on a
second sculpture. **[uncertain — the transcription's provenance is a 2026-09-12 fetch I could not
re-verify today; elonka.com/kryptos/sanborn/antipodes.html now returns a stub. Worth re-sourcing.]**

### 1.6 Discrepancies found between sources

Four, none of them positional:

1. **Elonka Dunin's page calls two different releases "a third clue"** — both the January 2020
   NORTHEAST release and the April/August 2020 EAST release. Typo; the layout diagram on the same
   page is correct.
2. **Smithsonian Magazine (Jan 31 2020) swaps the release years**: "'clock' and 'Berlin,' released
   in 2010 and 2014, respectively". BERLIN was 2010, CLOCK 2014. Its positions (26–34, 64–69,
   70–74) are right.
3. **Two incompatible provenance stories for EAST.** Schwartz (and Intel Today relaying him) say
   Sanborn sent an unsolicited layout image to several correspondents; rumkin.com says "a member of
   the Kryptos group asked him about EASTNORTHEAST being in a specific location and Sanborn
   confirmed it." The first makes EAST a Sanborn release; the second makes it a Sanborn
   *confirmation of a solver's guess*, which is a much weaker thing. Both cannot be right.
4. **The 2010 and 2014 articles index differently in words** — "the final series on the sculpture"
   (2010) versus "the final panel" (2014) versus "that final passage" (2020). All three resolve to
   the same 97 letters, but only because §1.3 pins them; the phrase "the final panel" taken
   literally would be wrong, since K4 starts four characters from the end of panel row 25.
5. **The secondary literature is split on whether these are *plaintext* or *ciphertext* positions.**
   A scan of every source retrieved in this project turned up both formulations in roughly equal
   numbers — "the 6 letters from 64-69 of the ciphertext K4 decrypt to BERLIN" alongside
   "NORTHEAST … refers to the positions 26-34 of K4's **plaintext**" and "BERLINCLOCK appears at
   confirmed positions 64–74 in the K4 **plaintext**". This is exactly the ambiguity task (e) was
   set to probe, surfacing in the literature. It is harmless for any position-preserving cipher
   (§5.1) and is dealt with for the rest in §5.2–5.3.

**Unanimity on the numbers.** A regular-expression scan over every page retrieved for this project —
the three NYT articles, Wikipedia, Elonka Dunin, rumkin, Intel Today, Smithsonian, NPR, PBS NOVA,
NBC, Hörenberg, NumberWorld, kryptosfan, solvekryptos and the rest — found **no source anywhere
that gives a different position range for any of the four cribs.** Every one of the ~40 distinct
position statements found reads 22–25 / 26–34 / 64–69 / 70–74.

### 1.7 Resulting strength ranking

| crib | strength | why |
|---|---|---|
| **BERLIN 64–69** | **firmest** | index *and* ciphertext string both published by Sanborn, 2010; restated by Sanborn in person, March 2019 |
| **CLOCK 70–74** | firm | index published 2014; independently corroborated by the widely-reported fact that the 74th letter is K in both plaintext and ciphertext, which only makes sense at that alignment |
| **NORTHEAST 26–34** | firm | index published 2020, single source, no ciphertext quoted |
| **EAST 22–25** | **weakest** | never stated in words by Sanborn; derived from a layout image; rumkin.com flags the doubt explicitly — *"It is possible that the first EAST in the plain text isn't correct. Sanborn did confirm it, but it's possible that it was confirmed out of hand as opposed to being intentional."* |

The practical consequence drove the rest of the work: **an error, if one exists, is far likelier in
the EAST/NORTHEAST block than in BERLIN/CLOCK.** That asymmetric hypothesis is tested directly in
§2 and §5.

---

## 2. Task (b) — slide each crib block

`crib_b_shifts.py`, log `crib_b_out.txt`. Validated first: three periodic ciphers were planted with
their cribs at *shifted* positions (+2/period 9, −3/period 12, +1/period 7) and the sweep recovered
exactly the planted shift in all three cases. `crib_lib.py`'s own self-tests also pass — round-trip
encryption for all 12 combos × 5 periods, K1 re-encryption under PALIMPSEST, 48/48 planted-key
recoveries, 48/48 perturbed-crib rejections.

Periods 2–26, 12 cipher/alphabet combos (3 rules × plaintext alphabet ∈ {plain, KRYPTOS} ×
ciphertext alphabet ∈ {plain, KRYPTOS}; the *key* alphabet only renames key values and so is
irrelevant to a consistency test, which is why 12 combos exhaust Quagmire I–IV over those two
alphabets). Every count is reported stratified by **c**, the number of independent equalities the
placement forces on a period-p key; a random key survives a stratum with probability 26⁻ᶜ, and that
is the chance expectation quoted beside every observed count.

| sweep | placements | tests | survivors | chance expectation | max c with a survivor |
|---|---|---|---|---|---|
| B0 control: baseline placement | 1 | 300 | **0** | 0.46 | — |
| B1 global slide, δ = −21…+23 | 45 | 13,500 | 26 | 20.8 | 1 |
| B1e same, 867 keyed-alphabet combos | 45 | 975,375 | 1,655 | 1,503 | 1 |
| B2 two phrase-blocks slid independently −3…+3 | 49 | 14,700 | 300 | 298.5 | 1 |
| B2e same, 867 combos | 49 | 1,062,075 | 21,541 | 21,570 | 2 |
| **B3 four blocks slid independently −3…+3** | **784** (of 2,401 proposed; rest overlap inconsistently or run off the 97) | **235,200** | **881** | **863.5** | **2** |
| B4 free slide: EASTNORTHEAST anywhere × BERLINCLOCK anywhere | 5,550 | 1,665,000 | 21,722 | 21,660 | 3 |

**No (shift, period, combo) becomes consistent.** Every observed count sits on its chance
expectation to within a few per cent (the one exception, B1e at 1,655 against 1,503, is a
dependence artefact — see §6), and **every survivor in the whole table carries c ≤ 3**: a placement
so under-constrained that one key in 26³ passes it by accident. Nothing reaches c ≥ 8 anywhere; a
genuine solution carries c = 22 at period 2 and still c = 5 at period 24.

Chance expectation is already adjusted for the extra freedom: the expectation column *is* the sum
over all placements, periods and combos of 26⁻ᶜ, so widening the search widens the expectation in
step. That is why B4's 21,722 survivors are not a result and B0's 0 is not a surprise.

B4 is worth calling out: it is the complete "where could these two phrases possibly be?" sweep, a
strict superset of tasks (b) and (c) and of every δ anyone could propose. It is empty above chance.

The **alphabet-free necessary condition** (columns marked *univ-pass* in the logs) strengthens this
beyond the 12 or 867 tested alphabets. Within a residue class, every Vigenère/Beaufort/variant-
Beaufort with *any* pair of 26-letter alphabets forces `ct_i = ct_j ⟺ pt_i = pt_j`. Failing it kills
a placement for all ≈4 × 10¹¹ alphabet pairs at once. In B4 it kills 58.4 % of (placement, period)
pairs outright.

---

## 3. Task (c) — the reading that includes K3's question mark

Two ways the index could shift by one:

* **δ = −1** — Sanborn 1-indexed over a string beginning with the `?` that ends K3 (the `?` is
  carved immediately before `OBKR`), so each crib sits one letter earlier in K4 than assumed.
* **δ = +1** — a carved letter was dropped from K4 the way an S was dropped from K2 in 2006, so
  each crib sits one letter later.

Both are in B1's global slide and both were also run on their own with the wider 867-combo
alphabet set:

| hypothesis | 12 combos × 25 periods | chance | 867 combos × 25 periods | chance |
|---|---|---|---|---|
| δ = −1 (the `?` counted) | 2 survivors | 0.46 | 50 survivors | 33.4 |
| δ = +1 (a dropped letter) | 3 survivors | 0.46 | 41 survivors | 33.4 |

Every one of those survivors is at **period 26, c = 1** — one constraint, one chance in 26, a coin
landing heads. Neither hypothesis produces a single survivor with c ≥ 2.

And, as §1.3 shows, the δ = −1 reading is refuted documentarily before any of this: under it the
2010 release would have had to say NYPVTT sits at 63–68, or that 64–69 reads BNYPVT.

---

## 4. Task (d) — crib-word variants that still fit the stated spans

`crib_a_variants.py`, log `crib_a_out.txt`. The hypothesis: the spans are right but the *words* are
not — Sanborn misspells on purpose, K2 uses `X` as a word separator, and journalists paraphrase.

Variants swept at the stated windows (13 letters at 22–34, 11 letters at 64–74), each core string
slid through its window in every alignment with `?` wildcards outside:

* **X and Q separators in every position**: `EASTXNORTHEAST`, `XEASTNORTHEAST`, `EASTNORTHEASTX`,
  `XEASTXNORTHEASTX`, `EASTXXNORTHEAST`, …; `BERLINXCLOCK`, `BERLINCLOCKX`, `XBERLINXCLOCK`, …
* **Sanborn-style deliberate misspellings**: doubled, dropped and transposed letters —
  `EASTNORTHEEAST`, `EASTNORTHEST`, `EASTNORHTEAST`, `EASTNORTHEASST`, `BERLINCLOKC`,
  `BERLINCLOC`, `BERLENCLOCK`, `BERLINCLCOK`, …
* **the words inside longer phrases**: `NORTHEASTERLY`, `EASTNORTHEASTERLY`, `NORTHEASTBYEAST`,
  `THEBERLINCLOCK`, `EASTBERLINCLOCK`, …
* **German renderings and the clock's real names**: `OSTNORDOST`, `NORDOSTEN`, `MENGENLEHREUHR`,
  `WELTZEITUHR`, `URANIAWELTZEITUHR`, `BERLINUHR`
* **every single-letter substitution** of each phrase (325 and 275 mutants), separately and
  simultaneously
* **partial cribs** — each released word on its own, the rest wildcard

"EAST NORTH EAST" as three words is the same 13-letter string as EASTNORTHEAST and is the baseline.

| sweep | variant pairs | tests | survivors | chance | max c with a survivor |
|---|---|---|---|---|---|
| baseline control | 1 | 300 | **0** | 0.46 | — |
| full cross-product | 124,271 | 37,281,300 | 2,051,527 | 2,052,000 | **4** (1 obs. vs 3.53 expected) |
| one substituted letter in EASTNORTHEAST | 326 | 97,800 | 12 | 150.7 | 1 |
| one substituted letter in BERLINCLOCK | 276 | 82,800 | 12 | 127.6 | 1 |
| one substituted letter in **each** window | 326 × 276 | 26,992,800 | 6,912 | 41,590 | 1 |
| partial cribs alone | 9 | 2,700 | 363 | 366.7 | 1 |

**Nothing.** Across 64.5 M tests the single highest-constraint survivor anywhere carries c = 4
against an expectation of 3.53 survivors in that stratum — i.e. fewer hits than chance predicts.
Every stratum c ≥ 5 is empty.

### 4.1 A misspelling-tolerant score, calibrated (`crib_d_anneal.py`)

The companion question: if the plaintext really is a misspelled riddle, would we even recognise it?
Measured directly (`crib_d_out.txt`, part 1), on a quadgram model with the D worst quadgrams
discarded:

| 97-letter text | q | q_tol8 |
|---|---|---|
| English | −4.97 | −4.67 |
| English, 2 letters corrupted | −5.14 | −4.84 |
| English, 5 letters corrupted | −5.39 | −5.11 |
| uniform random | −8.23 | −8.21 |
| shuffle of K4 | −8.20 | −8.18 |
| K4 ciphertext itself | −8.05 | −8.01 |

And on Sanborn's own three deliberate misspellings:

| text | as carved | corrected | cost |
|---|---|---|---|
| K1 (IQLUSION) | −4.579 | −4.482 | 0.10 |
| K2 window (UNDERGRUUND) | −4.425 | −4.290 | 0.14 |
| K3 (DESPARATLY) | −4.641 | −4.618 | 0.02 |

**A deliberate Sanborn misspelling costs 0.02–0.14. The English-to-random gap is 3.5.** So
"the plaintext is misspelled, that's why nothing scores as English" does not work as an
explanation, at any tolerance setting. This closes a standing excuse rather than a cipher family,
but it is worth having in writing.

Two further parts of that script are complete and clean: the hill-climber **recovers planted
period-3 to period-14 keys exactly** (5/5, exact text recovery), and the **progressive/Trithemius
family** (`key_i = a + b·i`) is exhausted over all 676 keys in four combos — best q_tol2 −7.53,
against a null of 200 random 97-letter texts whose own exhaustive best averages −7.69 ± 0.08. K4 is
inside its null. **[status: the long period-by-period sweep, part 3, was still running when this
report was written; the stored log is a partial run, marked as such. Where it has reported so far,
periods 2–22 of the first family, the positive control separates from the null by 6–80 σ while K4
sits within ±2 σ of the null at every period except p = 10 (z = +3.8) and p = 20 (z = +4.8) —
neither of which decrypts to anything resembling English, and both of which are unremarkable given
~100 period × family cells. No claim is made from them.]**

---

## 5. Task (e) — plaintext positions or ciphertext positions?

`crib_e_ptct.py`, log `crib_e_out.txt`.

### 5.1 The two readings coincide for every position-preserving cipher

If the cipher maps plaintext letter *i* to ciphertext letter *i* — any letterwise rule, any
per-position key, any alphabets — then "the ciphertext at 64–69 decrypts to BERLIN" and "the
plaintext at 64–69 is BERLIN" are the same sentence. Demonstrated over 240 random position-keyed
ciphers across all 12 combos: the two readings select the identical 24 (ct, pt) pairs in 240/240
cases.

**So task (e) is vacuous for every one-stage system** — which is nearly everything this repository
has ruled out. It has teeth only when a stage moves letters.

### 5.2 What the readings constrain once a transposition is present

| stage order | reading | what the cribs pin | status |
|---|---|---|---|
| T then S | CT | the 24 (ct, pt) pairs *are* those of a one-stage cipher; T is invisible | closed — every one-stage negative transfers to all 97! transpositions |
| S then T | CT | same 24 key values at relocated positions | closed — `twocipher.md`, 0 survivors |
| S then T | PT | key stream fully determined at 24 known plaintext positions for each candidate T | closed — `twocipher.md` (`two2_a/b/d`), 0 survivors |
| **T then S** | **PT** | 24 known key *values* at positions that depend on T | **c = 0 at every period for un-enumerated T — the cribs cannot test it at all** |

The last row is the honest gap, and it is not a gap the cribs can close. That reading puts itself in
exactly the evidential position of periods ≥ 27: crib-free, decidable only by whether the output
reads as English. It does *not* relocate the cribs to some other 24 contiguous pairs.

### 5.3 New sweeps: the asymmetric anchor, the rigid rotation, the reversed reading

Validated first: three periodic ciphers planted with one crib block at a known non-standard start
(A@30, A@21/B@50, A@40/B@70) were recovered exactly by the free slide, 3/3.

| sweep | placements | tests | survivors | chance | max c |
|---|---|---|---|---|---|
| **E3a** BERLINCLOCK nailed at 64–74 (the firmly anchored crib), EASTNORTHEAST slid over every legal start | 62 | 18,600 | 249 | 250.3 | 2 |
| **E3b** EASTNORTHEAST nailed at 22–34, BERLINCLOCK slid (the mirror) | 64 | 19,200 | 280 | 275.2 | 1 |
| **E4** rigid cyclic rotation: plaintext index *i* carried by ciphertext index (*i*+d) mod 97, all 97 d | 97 | 29,100 | 27 | 22.9 | 1 |
| **E5 R1** positions mirrored end-to-end, word forward | 1 | 300 | 0 | 0.46 | — |
| **E5 R2** positions mirrored, word reversed (plaintext written backwards) | 1 | 300 | 1 | 0.46 | 1 |

E3a is the test that follows directly from §1.7: it is the *strongest available* version of "the
EAST clue is wrong." It finds nothing. E4 adds the wrap-around offsets that `crib_b`'s
non-wrapping global slide could not reach. E5 asks the question K3's right-to-left route
transposition invites — which end do you count from — and answers it negatively.

---

## 6. Multiple-testing accounting

Everything above is one family of tests and should be read as one.

* **68,491,350** (placement or variant, period, combo) consistency tests in total —
  64.46 M in `crib_a`, 3.97 M in `crib_b`, 67.5 K in `crib_e`.
* **Total-count z-scores are the wrong statistic here and are reported only for completeness.**
  Survivor totals against a naive Poisson run from z = −170 (`crib_a`, one substituted letter in
  each window: 6,912 observed against 41,590 expected) to z = +3.9 (`crib_b` B1e, 1,655 against
  1,503). Both tails are artefacts of dependence, not signal: the 867 keyed alphabets share most of
  their letters and so produce correlated required-key values, and the variant strings within a
  window overlap heavily. The naive model treats them as independent draws and is therefore wrong
  in both directions. Every one of those excess survivors is at **period 26, c = 1** — a single
  constraint, one chance in 26.
* The statistic that *is* valid, because it is a hard structural bound rather than a count, is the
  constraint stratification. **The highest-constraint stratum containing any survivor anywhere is
  c = 4**, with 1 observed against 3.53 expected. Every stratum c ≥ 5 is empty across all 68.5 M
  tests, in every sweep, at every period, for every alphabet set.
* For reference, the true placement imposes c = 22 at period 2, c = 11 at period 13, c = 5 at
  period 24 and c = 1 at period 26. A correct (placement, period, combo) would appear as a survivor
  at c ≫ 5 and would stand out by 20-plus orders of magnitude. None does.
* Periods 27, 28, 29 and ≥ 53 impose **zero** crib constraints and are therefore untestable by this
  method at all, whatever the placement. That limitation is unchanged by any of this work.

---

## 7. What this closes

1. **The crib positions are verified, not assumed.** 22–25 EAST, 26–34 NORTHEAST, 64–69 BERLIN,
   70–74 CLOCK, 1-indexed over the 97 letters. `data/cribs.json` is correct and needs no edit.
2. **"Sanborn counted the `?`" is refuted** on documentary grounds (§1.3) and independently on
   cryptanalytic grounds (§3).
3. **"The cribs are off by a small shift" is refuted** — every block, individually and jointly,
   −3…+3 and far beyond, up to the complete free slide of both phrases over all 97 positions.
4. **"The crib words are misspelled or separated differently" is refuted** at the stated spans,
   over 124 k variant pairs including every single-letter mutation of both phrases.
5. **"Sanborn quoted the other text's positions" is refuted or shown vacuous**: identical for every
   position-preserving cipher, closed by `twocipher.md` for two of the three transposition cases,
   and crib-free (hence untestable, not merely relocated) in the fourth.
6. **"It's misspelled, that's why it doesn't look like English" is quantitatively dead** — the cost
   of Sanborn's own misspellings is under 4 % of the English-to-random gap.

Every published cryptanalysis that rests on these four cribs rests on solid ground. The failure of
K4 is not a crib-placement failure.

---

## 8. What remains open here

* **The EAST provenance conflict (§1.6, item 3) is unresolved.** Worth settling from the Kryptos
  discussion-group archive: whether Sanborn volunteered the layout image or merely assented to a
  solver's proposed placement. It does not change the arithmetic — EAST at 22–25 is consistent with
  everything — but it is the one crib that could in principle be retracted, and it supplies 4 of
  the 24 pairs.
* **Re-source the *Antipodes* K4 transcription (§1.5)** from a citable primary photograph or
  rubbing. If the two carvings ever disagree inside K4, that is the one thing that could still move
  a position.
* **Sanborn's layout image itself.** Schwartz reports that what Sanborn sent was a *picture* of the
  K4 layout. Nobody in the accessible sources reproduces the image; every published version of the
  EAST clue is a transcription of it. Locating the original would upgrade EAST from "weakest" to
  "firmest" in one step.
* **Periods ≥ 27 and the PT-reading with T-then-S remain crib-free.** No amount of placement work
  touches them; they need a language-model attack, which is `crib_d_anneal.py`'s and
  `search_*`'s territory.

---

## 9. Reproducing

`crib_lib.py` and the sweeps need numpy, which is not in the system `python3` here; use
`python3.12`.

```
cd analysis
python3.12 crib_lib.py                    # self-tests: round trip, K1 regression, planted keys
python3.12 crib_a_variants.py > ../findings/crib_a_out.txt     # ~6 min
python3.12 crib_b_shifts.py   > ../findings/crib_b_out.txt     # ~7 min
ANTIPODES_FILE=<transcription> \
python3.12 crib_c_sources.py  > ../findings/crib_c_out.txt     # instant
python3.12 crib_d_anneal.py   > ../findings/crib_d_out.txt     # long; hill-climb + nulls
python3.12 crib_e_ptct.py     > ../findings/crib_e_out.txt     # ~1 min
```

`crib_b_shifts.py` was re-run in full on 2026-09-13 and reproduced its stored output
**byte-for-byte** (`diff` clean, all 319 lines), so the stored logs are trustworthy.
`crib_c_sources.py` and `crib_e_ptct.py` were written and run today.
