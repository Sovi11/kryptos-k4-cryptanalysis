# Liber Primus — status report

**Revised: September 2026.** This revision re-verified every claim in the previous draft against primary
sources, and independently *recomputed* the cipher solutions and the unsolved-page statistics from the raw
rune transcription rather than repeating published figures. Corrections to the earlier draft are flagged
inline as **[CORRECTED]**.

Evidence labels used throughout:

| Label | Meaning |
|---|---|
| **[V]** | Verified — reproduced computationally here, or attested by a cryptographically signed artifact |
| **[C]** | Community consensus — documented on the CicadaSolvers / Uncovering Cicada wikis, widely replicated, not independently checkable |
| **[S]** | Speculation — hypothesis, explicitly not established |

---

## 1. What the Liber Primus is

A runic book published by Cicada 3301 during and after the 2014 recruitment puzzle, written in the 29-symbol
**Gematria Primus** alphabet — Anglo-Saxon futhorc runes mapped to Latin letters/digraphs and to the first 29
primes (2…109). Pages were distributed as JPEG images. Many of the LP1 images additionally carry an
**Outguess** steganographic payload, PGP-signed with Cicada's key. **[V]**

The published portion is titled **"Chapter 1 — Intus"**, implying the released material is a fragment of a
larger work. **[V]** (stated on page 02.jpg, which is in cleartext runes)

---

## 2. Page count and the LP1 / LP2 split

**[CORRECTED]** The previous draft said "LP1: 17 content pages plus 2 cover pages." That is wrong — 17 is the
*total*, composed of 2 + 15.

| Set | Pages | Numbering | Status |
|---|---|---|---|
| **LP1** | **17** (= 2 + 15) | `00.jpg`–`16.jpg` | **All 17 solved** |
| **LP2** | **58** | `0.jpg`–`57.jpg` | **2 solved** (`56.jpg`, `57.jpg`), **56 unsolved** |
| **Total** | **75** | | 19 solved, 56 unsolved |

**[V]** — the split, the counts and the arithmetic (75 = 73 + 2) are stated verbatim in the scream314
transcription and independently in the CicadaSolvers cryptanalysis briefing.

### The numbering trap

There are **two live numbering schemes**, and they collide. This is the single most common source of error in
secondary write-ups:

- **LP2-local numbering** (`0.jpg`–`57.jpg`) — the filenames 3301 actually used in the May 2014 dump. The two
  solved LP2 pages are **56.jpg** and **57.jpg** in this scheme.
- **Global numbering** (`00.jpg`–`74.jpg`) — the scream314 archive concatenates LP1 and LP2. The same two
  solved pages are **73.jpg** and **74.jpg** here.

So "56.jpg is solved" and "73.jpg is solved" are the same statement. **[V]**

A handful of LP1 pages also carry legacy names from their original drops (`14.jpg` = `107.jpg`,
`15.jpg` = `167.jpg`, `16.jpg` = `229.jpg`, `10.jpg`–`13.jpg` = `index.1.jpg`–`index.4.jpg`). **[V]**

### Not every unsolved page is runic

LP2 pages **49, 50 and 51** (local numbering) contain no runes at all. They carry a block of ASCII digit-pairs
(`3N 3p 2l 36 1b 3v …`) whose first character is always 0–4 and whose second ranges over exactly 60 values —
a **sexagesimal (base-60)** encoding, consistent with the cuneiform numerals that appear as marginalia on
pages 34–39. The community has rendered it as a 256-byte hex blob; it has not been broken. **[C]**

---

## 3. The Gematria Primus

29 runes, each with a Latin transliteration and a prime value. Index 0–28 is used for all modular arithmetic
(everything is mod 29).

| # | Rune | Latin | Prime | | # | Rune | Latin | Prime |
|---|---|---|---|---|---|---|---|---|
| 0 | ᚠ | F | 2 | | 15 | ᛋ | S / Z | 53 |
| 1 | ᚢ | U / V | 3 | | 16 | ᛏ | T | 59 |
| 2 | ᚦ | TH | 5 | | 17 | ᛒ | B | 61 |
| 3 | ᚩ | O | 7 | | 18 | ᛖ | E | 67 |
| 4 | ᚱ | R | 11 | | 19 | ᛗ | M | 71 |
| 5 | ᚳ | C / K | 13 | | 20 | ᛚ | L | 73 |
| 6 | ᚷ | G | 17 | | 21 | ᛝ | NG / ING | 79 |
| 7 | ᚹ | W | 19 | | 22 | ᛟ | OE | 83 |
| 8 | ᚻ | H | 23 | | 23 | ᛞ | D | 89 |
| 9 | ᚾ | N | 29 | | 24 | ᚪ | A | 97 |
| 10 | ᛁ | I | 31 | | 25 | ᚫ | AE | 101 |
| 11 | ᛄ | J | 37 | | 26 | ᚣ | Y | 103 |
| 12 | ᛇ | EO | 41 | | 27 | ᛡ | IA / IO | 107 |
| 13 | ᛈ | P | 43 | | 28 | ᛠ | EA | 109 |
| 14 | ᛉ | X | 47 | | | | | |

*(Row 14, ᛉ = X = 47, was missing from earlier versions of this table. Corrected 2026-11-12; the
parser in `analysis/lp_common.py` uses all 29 runes and reproduces every published statistic.)*

**[V]** — this table is not merely copied; it is *proved* by the round-trip re-encryption in §4.1, which fails
on any other assignment.

Consequences that matter for cryptanalysis:

- **The mapping is not a bijection with Latin.** ᚳ covers both C and K; ᚢ covers U and V; ᛋ covers S and Z.
  So decrypted plaintext reads `BOOC` for BOOK, `CNOW` for KNOW, `YOV`/`YOUR`, `TRVE` for TRUE, `SEEC` for
  SEEK, `COAN` for KOAN. These are not errors — they are the alphabet. **[V]**
- **You cannot round-trip runes → Latin → runes.** ᛏᚻᚫᛡ → `THAEIO` → ᚦᚫᛡ. This is the strongest argument
  that **the encryption was performed on runes, not on Latin characters**. **[C]**
- **Digraph runes wreck cribbing.** A single rune may be TH, EO, NG, OE, AE, IA or EA, so a guessed English
  word has many possible rune-lengths. **[C]**
- **Single-rune words** are frequent in both LP1 and LP2 and can essentially only be "A" or "I" (possibly "O"
  as a Blakean interjection). **[C]**
- LP text routinely drops vowels: `WARNNG`, `NOTHNG`, `DURNG`, `THNGS`, `SVFFERNG`. **[V]**

The **gematria sums** (adding the prime values of a phrase's runes) are a separate, real signalling channel —
e.g. `ALL THINGS SHOULD BE ENCRYPTED` = 1237, an emirp. But the prime values themselves **have not been
useful for decryption** of the unsolved pages. **[C]**

---

## 4. Page-by-page: how every solved page was solved

All arithmetic is mod 29 on rune indices 0–28.

| Page (global) | Page (LP2-local) | Title | Method | Key |
|---|---|---|---|---|
| 00.jpg | — | *Liber Primus* | cleartext runes | — |
| 01.jpg | — | **A Warning** | **Atbash**: `p = 28 − c` | — |
| 02.jpg | — | *Chapter I — Intus* | cleartext runes | — |
| 03.jpg | — | **Welcome** | **Vigenère** + plaintext-F rule | **DIVINITY** |
| 04.jpg | — | *(Welcome, cont.)* | Vigenère, key stream continues | DIVINITY |
| 05.jpg | — | **Some Wisdom** | direct transliteration + magic square | — |
| 06–09.jpg | — | **Koan 1** | **Atbash then shift +3**: `p = (28 − c) + 3` | — |
| 10–13.jpg | — | **The Loss of Divinity** | direct transliteration + magic squares | — |
| 14–15.jpg | — | **Koan 2** | **Vigenère** + plaintext-F rule | **FIRFUMFERENFE** |
| 16.jpg | — | **An Instruction** | direct transliteration + magic square | — |
| 17.jpg–72.jpg | **0–55** | *(56 pages)* | **UNSOLVED** | — |
| 73.jpg | **56.jpg** | **An End** | **φ(prime) stream**: `p = c − (prime[i] − 1)` + plaintext-F rule | prime sequence |
| 74.jpg | **57.jpg** | **Parable** | direct transliteration | — |

**[CORRECTED]** The earlier draft assigned "Welcome" to pages 2–5. Correct: 03–04 are Welcome; 02 is the
cleartext chapter heading; 05 is "Some Wisdom".

### 4.1 The rune-F rule — stated precisely

This is the detail most write-ups get backwards. The rule is:

> **When the *plaintext* rune is ᚠ (F, index 0), it is written into the ciphertext unencrypted, and the key
> index does *not* advance.**

It is a rule about the plaintext, not the ciphertext. The consequence is an asymmetry that makes automated
decryption genuinely hard: **a ciphertext ᚠ is ambiguous.** It may be a literal skipped plaintext F, or it may
be an ordinary encryption of some other letter that happened to land on index 0. On page 56 there are five ᚠ
runes in the ciphertext and **only one of them is a skip.** **[V]**

Because of this ambiguity, the wiki publishes the skip positions explicitly rather than an algorithm:

- **03–04.jpg (DIVINITY)** — skip indices **48, 74, 84, 132, 159, 160, 250, 421, 443, 465, 514** **[C]**
- **14–15.jpg (FIRFUMFERENFE)** — skip indices **49, 56** **[C]**
- **56.jpg (φ(prime))** — skip rune **#57** (1-based) **[V]**

**Verification performed here.** I re-encrypted the known plaintext of page 03 —
`WELCOME / WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS` — by spelling it in Gematria
Primus, applying Vigenère with DIVINITY, and applying the plaintext-F rule. The output matched the published
ciphertext **rune-for-rune, 55 of 55**. This simultaneously confirms the rune table, the key, the shift
direction, and the exact form of the F rule. No other combination produces a match.

Under a naive "skip every ciphertext ᚠ" rule the same page decodes to `WELCOFA / …FILGRIM…` — wrong. Under
no F rule at all it decodes correctly for a while and then drifts at the first true skip. Both failure modes
are reproducible.

### 4.2 The keys

**DIVINITY** = ᛞᛁᚢᛁᚾᛁᛏᚣ = indices `23, 10, 1, 10, 9, 10, 16, 26`. The scream314 archive lists the key as
`6, 19, 28, 19, 20, 19, 13, 3` — those are the same key expressed as *decryption* shifts, i.e. `29 − index`.
Both are correct; they are inverses. **[V]**

**FIRFUMFERENFE** = ᚠᛁᚱᚠᚢᛗᚠᛖᚱᛖᚾᚠᛖ = indices `0, 10, 4, 0, 1, 19, 0, 18, 4, 18, 9, 0, 18` (13 runes). It is
CIRCUMFERENCE with every C replaced by F — a self-referential joke, since the koan it encrypts is *about* the
circumference, and F is the rune the cipher skips. **[V]**

### 4.3 The φ(prime) stream on 56.jpg — exact algorithm

```
decimal[i] = (decimal[i] − (primes[i] − 1)) mod 29
```

i.e. subtract 1, 2, 4, 6, 10, 12, 16, 18, 22, 28, 30, 36, … using the primes in order. Since φ(p) = p − 1 for
prime p, this is Euler's totient evaluated along the primes — which ties directly to page 05's cleartext
assertion `THE TOTIENT FUNCTION IS SACRED`. **[V]**

**Verification performed here.** Decrypting page 56 with this stream, skipping rune #57 only, yields cleanly:

> AN END / WITHIN THE DEEP WEB / THERE EXISTS A PAGE THAT HASHES TO / `36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4` / IT IS THE DUTY OF EUERY PILGRIM TO SEEC OUT THIS PAGE

The skip is forced, and the reason is arithmetically pretty: rune #57 would consume the 57th prime, **269**,
and `(269 − 1) mod 29 = 7`, which would emit **OE** instead of **F** and garble everything after it. Skipping
it hands prime 269 to the *next* rune instead. I confirmed 269 is prime #57 and that the five ᚠ runes on the
page sit at positions **36, 48, 52, 57, 75** — so the skip is indeed the fourth of five. **[V]**

**The referenced hash has never been found.** No deep-web page matching that digest has ever surfaced. Note it
need not be a website — it may be a content identifier for Freenet/GNUnet/P2P. **[C]**

### 4.4 The solved plaintexts (abridged)

- **01.jpg, A Warning** — `A WARNNG / BELIEVE NOTHNG FROM THIS BOOC EXCEPT WHAT YOV CNOW TO BE TRVE / TEST THE
  CNOWLEDGE / FIND YOVR TRVTH / EXPERIENCE YOVR DEATH / DO NOT EDIT OR CHANGE THIS BOOC OR THE MESSAGE
  CONTAINED WITHIN, EITHER THE WORDS OR THEIR NVMBERS / FOR ALL IS SACRED` **[V]**
- **03–04.jpg, Welcome** — the pilgrimage text ending `AN INSTRVCTIAN: COMMAND YOVR OWN SELF` **[V]**
- **05.jpg, Some Wisdom** — `THE PRIMES ARE SACRED / THE TOTIENT FVNCTIAN IS SACRED / ALL THNGS SHOVLD BE
  ENCRYPTED`, plus a 5×5 square mixing runes and numbers **[V]**
- **06–09.jpg, Koan 1** — the "who are you / what are you" master-and-student koan **[V]**
- **14–15.jpg, Koan 2** — the koan of the I as `THE VOICE OF THE CIRCVMFERENCE` **[V]**
- **57.jpg, Parable** — `LICE THE INSTAR TVNNELNG TO THE SVRFACE / WE MVST SHED OVR OWN CIRCVMFERENCES / FIND
  THE DIVINITY WITHIN AND EMERGE`. This is Parable 1,595,277,641, which had already appeared in 2013 inside
  the ID3 tag of `761.mp3` ("The Instar Emergence"); the number is the product of the gematria sums of its
  three lines, 1259 × 1031 × 1229. **[C]**

### 4.5 The magic squares

Five 5×5 squares appear across LP1 (pages 05, 10–13, 16). They are doubly symmetric (each is its own
180°-rotation) and their row/column sums are meaningful. The square on page 05 was already known — it is
identical to one recovered from out-of-band data during the 2014 onion chain, which is what let solvers
anchor page 05 as cleartext. The square on 15.jpg has been mathematically reconstructed as the value array of
a prime-index recurrence of pseudo-Fibonacci form, also derivable via Zeckendorf's theorem. **[C]**

---

## 5. The Outguess steganography layer

`outguess -r <image> out.txt` on the LP images. Findings, page by page: **[V]** unless noted

| Page | Outguess payload |
|---|---|
| 00, 01, 02.jpg | PGP-signed messages containing large hex blobs |
| 03.jpg | PGP-signed: **"Let the text guide you. Good luck. 3301"**, followed by a hex blob beginning `ffd8ffe000104a464946` — a **JFIF/JPEG file header**, i.e. an embedded image |
| 04.jpg | ~7.5 kB of garbage (no payload) |
| 05.jpg | none |
| 06, 07, 09.jpg | garbage |
| 08.jpg | **"For those who have fallen behind:"** followed by a 2×14 block of digraphs (`TL BE IE OV UT HT RE ID TS EO ST PO SO YR / SL BT II IY T4 DG UQ IM NU 44 2I 15 33 9M`), then "Good luck. 3301" |
| 10–13.jpg | PGP-signed: **"Create one Tor hidden service that can accept CGI file uploads. When this hidden service returns and can accept input, post the three magic squares and the URL to your Tor hidden service here. Work alone."** plus an ASCII-art bordered square |
| 14, 15, 16.jpg | none |
| LP2 pages | mostly **none**; several (LP2 17, 21, and others) yield exactly **58.2 kB of garbage** — an Outguess artifact, not a payload |

The important structural point: **the Outguess layer is an LP1 phenomenon.** It carried the live instructions
that drove the 2014 recruitment (build a hidden service, upload the magic squares, work alone). It carries
**nothing** for the unsolved LP2 pages. Anyone hoping the key to LP2 is hidden steganographically in the LP2
images is working against the evidence. **[C]**

**Caveat on "58.2 kB garbage":** Outguess will emit pseudorandom bytes from any JPEG whether or not one was
embedded. The consistent size is a function of the images' capacity, not proof of a payload. Error-Level
Analysis of the LP2 JPEGs has also been tried, with no result. **[C]**

---

## 6. The 56 unsolved LP2 pages — exact statistics

**All figures in this section were recomputed from the rune transcription, not copied.** They agree with the
published CicadaSolvers / Uncovering Cicada figures to the digit.

### 6.1 Headline numbers **[V]**

| Quantity | Value |
|---|---|
| **Rune count (unsolved corpus)** | **12,956** |
| Rune count, solved 56.jpg / 57.jpg | 86 / 95 |
| Rune count, all of LP2 | 13,137 (= 12,956 + 86 + 95 ✓) |
| Rune count, all of LP1 | 2,801 |
| **Index of coincidence (normalized)** | **0.999** (raw 0.03448; uniform 1/29 = 0.034483) |
| IC of English in this alphabet, for comparison | ≈ 1.73 |
| Word count | 2,900 |
| Mean word length | 4.47 runes |
| Most common rune | ᛟ OE — 492 (3.80%) |
| Least common rune | ᛇ EO — 399 (3.08%) |
| Unigram χ² | **26.5** on 28 df (5% critical value 41.3) → **fails to reject uniformity** |

The frequency distribution is *flat*. Not "flattish" — statistically indistinguishable from a uniform random
draw over 29 symbols. This single fact eliminates every cipher that preserves plaintext letter statistics.

**[CORRECTED]** The earlier draft's "~13,000 runes" is now pinned at exactly 12,956.

### 6.2 The same-rune bigram (doublet) deficiency — the one real signal

This is the **only** statistically significant deviation from randomness anywhere in the corpus, and it is
enormous.

| | Value |
|---|---|
| Adjacent rune pairs | 12,955 |
| **Doublets observed** | **86** |
| Doublets expected (from the corpus's own unigram frequencies) | **447.6** |
| Doublet rate observed | **0.663%** |
| Doublet rate expected (1/29) | **3.45%** |
| Ratio observed / expected | **0.192** — a **5.2× suppression** |
| Standard deviation of the expectation | 20.8 |
| **z-score** | **−17.4** |

A z of −17.4 is not a fluctuation. It is a structural property of the cipher. **[V]**

Restricting to *within-word* adjacencies only (excluding pairs that straddle a word delimiter) gives 63
doublets out of 10,056 pairs against 347.5 expected — the same effect, so it is not an artifact of how
delimiters are counted. **[V]**

Per chapter (chapters delimited by marginalia artwork; LP2-local page numbers): **[C]** for the chapter
boundaries, **[V]** for the counts

| Chapter (marginalia) | Pages | Runes | IC | Doublets | Rate |
|---|---|---|---|---|---|
| Cross | 0–2 | 729 | 0.988 | 4 | 0.549% |
| Spirals | 3–7 | 1,145 | 1.004 | 6 | 0.524% |
| Branches | 8–14 | 1,729 | 0.999 | 9 | 0.520% |
| Möbius | 15–22 | 1,903 | 1.000 | 10 | 0.525% |
| Mayfly | 23–26 | 1,021 | 0.993 | 11 | 1.078% |
| Wing / Tree | 27–32 | 1,433 | 0.991 | 13 | 0.907% |
| Cuneiform | 33–39 | 1,680 | 0.996 | 12 | 0.714% |
| Spiral / Branches | 40–53 | 3,008 | 1.001 | 18 | 0.598% |
| Hollow | 54–55 | 308 | 0.980 | 3 | 0.977% |
| **Total** | **0–55** | **12,956** | **0.999** | **86** | **0.663%** |

The suppression is present in **every** chapter. Whatever mechanism causes it is applied uniformly across a
corpus that is otherwise believed to change cipher per section.

### 6.3 Repeated n-grams

**The 6-gram DJUBEI (ᛞᛄᚢᛒᛖᛁ) is the longest repetition in the entire unsolved corpus, occurring exactly
twice** — at stream positions **6555** and **12950**, a gap of **6395**. It is a *dis legomenon*: it appears
twice and never again, and there is no 7-gram repeat anywhere. **[V]**

Its two occurrences sit in different chapters and split across word boundaries differently each time — on
LP2 page 27 (Wing/Tree) it spans `ᛒᚠ-ᛞᛄᚢ-ᛒᛖᛁ-ᚫᚠ`, and on page 55 (Hollow, the last two words) it spans
`ᚳᛠᛁᛗᚳᛉ-ᛞᛄᚢ-ᛒᛖᛁ`. That the same six runes recur across a chapter boundary is what makes it a candidate
attack point. **[C]**

The complete set of repeated 5-grams — there are only five: **[V]**

| 5-gram | Indices | Positions | Gap | Chapters |
|---|---|---|---|---|
| **DJUBE / JUBEI** | 23-11-1-17-18-10 | 6555, 12950 | 6395 | Wing/Tree → Hollow |
| **BMRNM** | 17-19-4-9-19 | 5448, 12001 | 6553 | Möbius → Spiral/Branches |
| **OUNWM** | 3-1-9-7-19 | 6985, 8016 | 1031 | Wing/Tree → Cuneiform |
| **OFLOENG** | 3-0-20-22-21 | 7393, 12385 | 4992 | Wing/Tree → Spiral/Branches |
| **IMNGYA** | 10-19-21-26-24 | 10671, 12764 | 2093 | Spiral/Branches → Hollow |

Note the gaps — 6395, 6553, 1031, 4992, 2093 — share no useful common factor. Kasiski gives nothing. **[V]**

n-gram counts against a random-text null model: **[C]**

| | LP observed | Random mean ± sd | Deviation |
|---|---|---|---|
| Unique bigrams | 840 | 841.00 ± 0.02 | — |
| Repeated trigrams | 2,508 | 2,433.5 ± 31.2 | **+2.4 σ** |
| Repeated quadgrams | **127** | 117.2 ± 10.9 | +0.9 σ |
| Total repeated quadgrams | 255 | 235.2 ± 21.9 | +0.9 σ |

I independently counted 127 repeated 4-grams, matching exactly. The trigram excess at +2.4 σ is suggestive
but well short of decisive; the quadgram excess is noise. **The corpus is very slightly less random than
random — but only very slightly, and only above the bigram level.** **[V]**

---

## 7. Ledger: what has been ruled out vs. what remains live

### 7.1 Definitively ruled out

| Cipher family | Why it is dead | Status |
|---|---|---|
| **Monoalphabetic substitution** (incl. Atbash, Caesar, ROT-n, keyed simple substitution) | A monoalphabetic cipher *permutes* the frequency distribution, it does not flatten it. LP2 unigram χ² = 26.5 on 28 df. English would be nowhere near flat. | **Ruled out [V]** |
| **Short-key Vigenère / any cyclically-repeating polyalphabetic** | Friedman test run: ciphertext split into *k* columns for each candidate key length, mean per-column IoC computed. **Max observed IoC < 1.15**, versus ~1.6 expected for a correct *k* on English plaintext. Repeated separately on blocks of 50–5000 runes in case the key changes mid-text. Nothing. Kasiski on the five repeated 5-grams gives no common factor. Every cyclic polyalphabetic is a special case of Vigenère, so all of them fall together. | **Ruled out [C]**, methodology sound |
| **Autokey / autoclave with a short primer** | Stochastic hill-climbing search over primer lengths 3–20 (standard practicalcryptography approach). **No hits.** | **Ruled out for short primers [C]** — *not* ruled out for long primers |
| **Hill cipher keyed on the LP matrices** | The base-60 cuneiform 2×2 matrix and the 4×4 matrix were both tried as Hill keys, with n-gram significance testing on the output. No results. The cuneiform was subsequently shown to read "3301" and "1033" in base 60 — it is a signature, not a key. | **Ruled out for those keys [C]** |
| **Transposition-only** | A pure transposition preserves unigram frequencies exactly. LP2's are flat; English is not. | **Ruled out [V]** |
| **The key being hidden in the LP2 images** | Outguess returns nothing on LP2 beyond capacity-sized noise; ELA found nothing. | **Ruled out as far as tested [C]** |

### 7.2 Still live

| Hypothesis | Standing |
|---|---|
| **A stream cipher whose shift depends on the previous rune** | **Largely closed 2026-11-12, see `findings/lp2_attack_2026-11.md`.** Any cipher where the previous *ciphertext* rune selects the substitution (any function) is ruled out: grouped IoC with the doublet symbol removed is z = +0.83. Feedback ciphers c_i = c_{i-1} + m_i·(p_i − z) and c_i = c_{i-1} + p_i + k_i fail for 8 number streams × 16,000 offsets (planted-cipher verified). Dependence on the previous *plaintext* rune with an additional uniform key is not excluded. **[V]** |
| **Prime × Fibonacci interleavings** | 3301 demonstrably like meshing the two. Page 56 uses φ(primes). The 2016 message's structure is recovered by cumulatively subtracting Fibonacci numbers from 464 (3301's prime index) and reading the result as a prime index; the 2017 message's gematria sum is the *next term* that algorithm predicts — which is strong evidence the 2016 reading is not coincidence. The 15.jpg square is a prime-index pseudo-Fibonacci recurrence. **Live, and well-motivated. [C]** |
| **Long-primer autokey / running key from an external text** | **Ruled out 2026-11-12.** An additive cipher with any English-text key, whether a running key from any book or a plaintext autokey with any primer, gives ciphertext frequencies equal to English convolved with itself, IoC ≈ 1.05. LP2 is 0.9999, which is 12–14 sd away and robust to plaintext-sampling error. Ciphertext autokey fails at every primer L = 1–6000. A running key also *cannot* produce the doublet suppression. **[V]** |
| **Per-chapter cipher changes** | The marginalia demarcate chapters and 3301 is believed to change method per section. Note the doublet suppression is *uniform* across chapters, which slightly argues the *mechanism* is shared even if the key is not. **Live. [C]** |
| **A DJUBEI-anchored crib attack** | The only long repetition available. **Live but thin. [C]** |
| **Encryption on runes, not Latin** | Effectively settled in favour, from the non-invertibility of the rune↔Latin map. Any attack operating on Latin text is probably mis-specified. **[C]** |
| **One-time pad** | Consistent with every observation. Also **unfalsifiable and unbreakable** — if true, LP2 is not a puzzle but a monument. Kept on the list for honesty, not for hope. **[S]** |

### 7.3 A caution about the ledger

The "ruled out" column rests on community testing, much of it from 2014–2016, documented on wikis rather than
in reproducible artifacts. The Vigenère and autokey exclusions are methodologically sound and have been
re-run many times, so they are safe. The Hill-cipher exclusion is narrow — it rules out *two specific keys*,
not the family. Treat the ledger as "no one has found it this way," not as a proof of impossibility. **[S]**

---

## 8. Authentic timeline, 2012–2017

Only PGP-signed material and the onion/file drops are treated as authentic here.

| Date | Event |
|---|---|
| **2012-01-04** | First puzzle posted to 4chan /b/. (Some community pages say Jan 5; Wikipedia and most sources say Jan 4.) Winners were taken private; a leaked email describes a think-tank-like group advocating liberty, privacy and security. **[C]** |
| **2013-01-04** | Second round. **Gematria Primus discovered** this year. Some solvers reported invitations that were never answered. **[C]** |
| **2014-01-04/05** | Third round, announced via Twitter. Runs through an onion chain; **LP1 pages are released in stages** across this puzzle (hence the legacy filenames 107/167/229/index.N). LP1 is solved within weeks. **[C]** |
| **2014-04-02** | The onion that will serve LP2 is set up — `Last-Modified: Wed, 02 Apr 2014 08:33:19 GMT`. 3301 then waits a month. **[V]** |
| **2014-05-02, ~10:00 GMT** | **LP2 released.** 3301 connects to every hidden service solvers had previously registered, fetches `/key.asc` and `/`, then POSTs `message.txt.asc` to each — a signed message linking to `ky2khlqdf7qdznac.onion`. The User-Agent string is `Cicada/33.01 CicaDOS 1.033 E Edition` (GET) and `S Edition` (POST). That onion served a bare HTML page listing `0.jpg` … `57.jpg`. **[V]** |
| **2014 (days–weeks later)** | **57.jpg** solved immediately (plain transliteration); **56.jpg** solved shortly after via the φ(prime) stream. Nothing else has been solved since. **[C]** |
| **2015-01** | No new January puzzle. The three-year cadence breaks. **[C]** |
| **2015-07-27/28** | **Planned Parenthood denial.** Signed Pastebin via @1231507051321: *"Some news organisations have recently claimed that '3301' is tied to the illegal activities of a group that has claimed responsibility for attacks against Planned Parenthood. We do not engage in illegal activities. We are not associated with this group in any way, nor do condone their use of our name, number, or symbolism."* **[V]** — signature verifies |
| **2015-12-31, 19:01:07 EST** | The 2016 message is **signed**. **[V]** |
| **2016-01-06, 04:44:50 UTC** | …and **tweeted** (2016-01-05 late evening US time — hence the "Jan 5" vs "Jan 6" discrepancy across sources). Image `4gq25.jpg` (563 × 569 — both prime), Outguess yields: *"Hello. The path lies empty; epiphany seeks the devoted. **Liber Primus is the way. Its words are the map, their meaning is the road, and their numbers are the direction.** Seek and you will be found. Good luck. 3301. Beware false paths. Verify OpenPGP 7A35090F."* **[V]** |
| **2017-04-04, 23:23 GMT** | **The last authentic message is signed** and posted to Pastebin (`pastebin.com/yEiTHhvF`). Full text: *"Beware false paths. Always verify PGP signature from 7A35090F. 3301"*. Signature version string: `CicadaPG v.3301`. **[V]** |
| **2017-04-29** | It is *discovered* — 25 days later — by IRC user `psilynt1`, who searched Pastebin for the string "7A35090F" sorted by date. The paste had 113 views. Google's cache shows 72 views on Apr 6. **[V]** |
| **2017 → 2026** | **Nothing.** No authentic signed output for over nine years. Everything since is community work or imposture. **[V]** |

### The PGP key

- **Short key ID:** `7A35090F`
- **Long key ID:** `181F01E57A35090F`
- **Full fingerprint:** `6D85 4CD7 9333 22A6 01C3 286D 181F 01E5 7A35 090F`
- **UID:** `Cicada 3301 (845145127)`

**[V]** — I decoded the issuer subpacket embedded in the April 2017 signature block directly. The base-64
fragment `EBgfAeV6NQkP` decodes to bytes `10 18 1F 01 E5 7A 35 09 0F`, i.e. subpacket marker `0x10` followed
by the long key ID `181F01E57A35090F`. The same issuer appears in the 2015 and 2016 signatures. The full
fingerprint is as reported by gpg on the wiki and is consistent with that long ID.

**3301's own rule, stated twice in their final two messages: if it isn't signed by 7A35090F, it isn't them.**
This is the entire authentication model, and it is sufficient — anyone can verify, offline, in seconds.

---

## 9. Imposters, hoaxes and scams — CLEARLY LABELLED

> **Nothing in this section is Cicada 3301.** None of it is signed by 7A35090F. Some of it is criminal.

### 9.1 The "hidden layer decrypted" Solana scam (2025–2026) — **SCAM. Do not engage.**

A wiki page titled **"53cr37-layer"** hosted at **`unc0vering-cicada.fandom.com`** — note the **zero** in
"unc0vering", a deliberate typosquat of the legitimate `uncovering-cicada.fandom.com` — claims to have
"decrypted the hidden layer of the Liber Primus (pages 1–73)" using keys `DANAD` and `MIDBV` supposedly
extracted from the "Know This" number square, via "rune transliteration → Atbash → Vigenère".

The claimed "solution" then instructs readers to:

- buy a **Solana token** (address beginning `AWM9MQn8J5od…`), whose trading volume and holder count are
  asserted to be "deliberate pointers";
- **send a transaction with the memo `118993`** to the token address, after which "metadata will reveal
  coordinates in Grozny";
- travel to **Grozny, Chechnya** and find a building numbered `123157`;
- contact the author, who will supply "the full decryption" only to those who "can genuinely continue the
  operation."

**Why this is a scam, concretely:**

1. **Not signed.** No PGP signature from 7A35090F, or from anything. 3301's last two messages exist
   specifically to make this test easy.
2. **The method is self-refuting.** Atbash-then-Vigenère is a cyclic polyalphabetic composition — exactly the
   family excluded by the Friedman analysis in §7.1. It cannot produce coherent English from a corpus with
   IC 0.999.
3. **No ciphertext, no plaintext, no verification path.** A genuine solve is checkable by anyone in minutes;
   this one is withheld pending recruitment.
4. **It asks for money and for physical travel.** 3301 never did either. "Send a transaction to reveal the
   next step" is the structure of an advance-fee fraud, not a puzzle.
5. **The urgency-plus-exclusivity framing** ("Who is ready to take on the final stage? I cannot travel there
   myself") is standard social engineering.

**Do not buy the token, do not send a memo transaction, do not travel anywhere.** Treat the `unc0vering`
domain as hostile.

### 9.2 The "Cicada3301" ransomware gang (2024–) — **unrelated criminals**

A ransomware-as-a-service operation that appropriated the name, the number and the cicada logo.

- First observed **June 2024**; began recruiting affiliates on the RAMP cybercrime forum on **2024-06-29**. **[C]**
- Rust-based locker using ChaCha20 + RSA; targets Windows, Linux, ESXi, NAS and PowerPC. **[C]**
- Double extortion — encryption plus a data-leak site. **[C]**
- Strong code and tradecraft similarities to the retired **ALPHV/BlackCat**, widely assessed as a rebrand or
  splinter. **[C]**
- Had hit ~30 organisations across critical sectors within three months. **[C]**

It has **no connection whatsoever** to the puzzle. Security vendors (Group-IB, Unit 42, Truesec) treat them
as entirely separate entities that happen to share a name. Note the precedent: 3301 explicitly denied a
comparable name-appropriation in 2015 (§8). They have issued no statement about this one, because they have
issued no statements at all since 2017 — **absence of a denial is not evidence of involvement.**

### 9.3 The general category: unsigned "new puzzle" claims

Since January 2015 there has been a steady stream of imitation puzzles, troll drops, fake Twitter accounts,
"I've solved it" YouTube announcements and lookalike onions. The 2017 message exists precisely to deal with
them.

**The test, in full:**

```
gpg --verify message.asc
```

If it does not report a good signature from `181F01E57A35090F` / fingerprint
`6D854CD7933322A601C3286D181F01E57A35090F`, it is not Cicada 3301. There are no exceptions, no "they lost the
key" stories, no "this one is different." Also note: **the people running the wikis, the IRC channel and the
Discord are not 3301 either**, and say so explicitly.

---

## 10. Honest summary of where this stands

- LP1 (17 pages) is fully solved and the methods are **reproducible from scratch** — I re-derived all five
  cipher schemes above from the raw runes.
- LP2 is 58 pages; **2 solved, 56 unsolved, unchanged since 2014.** That is over twelve years.
- The unsolved corpus is 12,956 runes with a flat unigram distribution (χ² = 26.5/28 df) and IC 0.999. Every
  classical statistical handle is dead **except one**: the doublet count of 86 against 447.6 expected, a
  −17.4 σ suppression present uniformly across all nine chapters.
- The longest repetition in the whole corpus is a single 6-gram, DJUBEI, occurring twice.
- The doublet signature is the shape of a **cipher whose shift depends on the preceding rune** — which is a
  natural generalisation of the φ(prime) stream already proven on page 56 and of the plaintext-F interrupter
  used on three separate LP1 pages. That is where the evidence points.
- The counter-possibility is that 12,956 runes is simply **too little ciphertext** to break a per-rune stream
  with no crib, in which case no amount of statistics will help and the book is open only to someone who
  guesses the generator.
- Nothing authentic has come from 3301 since **2017-04-04**. The final instruction was "Beware false paths."
  Read it as a warning about §9.

---

## Sources

**Primary artifacts**
- [scream314/cicada3301 — `liber_primus.md`](https://github.com/scream314/cicada3301/blob/master/liber_primus.md) — full rune transcription with per-page keys and Outguess payloads (all computation in this report was run against this file)
- [krisyotam/cicada3301](https://github.com/krisyotam/cicada3301) — complete archive: scans, signed messages, public key, IRC logs, tools
- [rtkd/iddqd](https://github.com/rtkd/iddqd) — the canonical transcription used by the wikis
- [micheloosterhof/cicada-2014](https://github.com/micheloosterhof/cicada-2014) — raw stage-11 onion capture of the LP2 dump
- April 2017 signed message: [pastebin.com/yEiTHhvF](https://pastebin.com/yEiTHhvF)
- 2016 signed message: [pastebin.com/kKtNd0G0](https://pastebin.com/kKtNd0G0)
- 2015 signed message: [pastebin.com/smRatr3D](https://pastebin.com/smRatr3D)

**Community documentation**
- [CicadaSolvers — Liber Primus Cryptanalysis Briefing](https://www.cicadasolvers.com/quickstart)
- [Uncovering Cicada Wiki — How the solved pages were solved](https://uncovering-cicada.fandom.com/wiki/How_the_solved_pages_of_the_Liber_Primus_were_solved)
- [Uncovering Cicada Wiki — Frequency Analysis, Unsolved Pages](https://uncovering-cicada.fandom.com/wiki/Frequency_Analysis_Unsolved_Pages)
- [Uncovering Cicada Wiki — What Happened: Liber Primus (Post 2014)](https://uncovering-cicada.fandom.com/wiki/What_Happened_Liber_Primus_(Post_2014))
- [Uncovering Cicada Wiki — PGP Signed Message April 2017](https://uncovering-cicada.fandom.com/wiki/PGP_Signed_Message_April_2017)
- [Uncovering Cicada Wiki — 2016 Message](https://uncovering-cicada.fandom.com/wiki/2016_Message)
- [Uncovering Cicada Wiki — Gematria Primus](https://uncovering-cicada.fandom.com/wiki/Gematria_Primus)
- [Uncovering Cicada Wiki — Cicada Part 9: Attempts](https://uncovering-cicada.fandom.com/wiki/Cicada_Part_9_-_Attempts) (the ruled-out ledger)
- [Uncovering Cicada Wiki — Liber Primus Ideas and Suggestions](https://uncovering-cicada.fandom.com/wiki/Liber_Primus_Ideas_and_Suggestions)
- [Uncovering Cicada Wiki — FAQ](https://uncovering-cicada.fandom.com/wiki/FAQ)
- [Boxentriq — Cicada 3301 Liber Primus Guide](https://www.boxentriq.com/guides/cicada-3301-liber-primus)
- [Wikipedia — Cicada 3301](https://en.wikipedia.org/wiki/Cicada_3301)

**On the imposters (§9) — cited as documentation of the fakes, not as Cicada material**
- Solana scam page: `unc0vering-cicada.fandom.com/wiki/53cr37-layer` (**typosquat — hostile, do not transact**)
- [Group-IB — Infiltrating the Cicada3301 Ransomware-as-a-Service Group](https://www.group-ib.com/blog/cicada3301/)
- [Unit 42 — Repellent Scorpius, Distributors of Cicada3301 Ransomware](https://unit42.paloaltonetworks.com/repellent-scorpius-cicada3301-ransomware/)
- [Truesec — Dissecting the Cicada](https://www.truesec.com/hub/blog/dissecting-the-cicada)
- [The Register — Cicada ransomware / BlackCat links](https://www.theregister.com/2024/09/04/cicada_ransomware_blackcat_links/)
