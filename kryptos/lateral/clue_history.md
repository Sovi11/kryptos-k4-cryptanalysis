# Kryptos K4 — the complete clue history, with the crib positions independently verified

Compiled 2026-09-13. Companion machine-readable file: `keystreams/clue_positions.tsv`.
Chronological dossier of *what Sanborn and Scheidt said about the method* lives in
`../findings/sanborn_statements.md`; this file is about **the clues themselves** — dates, exact
published wording, outlets, and above all **the character positions**, because a silent off-by-one
in those four numbers would void every negative result in this repository.

Nothing here is a proposed solution. Nothing here was submitted to Paradigm's paid verifier.

---

## 0. Bottom line

| Question | Answer |
|---|---|
| Are the crib positions 22–25 / 26–34 / 64–69 / 70–74 correct? | **Yes. Verified, and the verification is not merely a count of agreeing websites.** |
| Is the indexing 1-based? | **Yes, unambiguously** — see §1, the argument is self-checking and does not depend on trusting any one source. |
| Did any source disagree on the numbers? | **No source gives different numbers.** One source (*Smithsonian Magazine*, 2020) swaps the *words* BERLIN and CLOCK against the positions. Two further factual slips in secondary coverage are recorded in §3. |
| Does the repository's `data/cribs.json` match? | **Yes, exactly**, including the release dates as corrected on 2026-09-12. |
| Is anything about the clues genuinely contested? | **Yes, but not the numbers.** What is contested is whether a clue asserts a *letter-for-letter* mapping at those positions or only that the plaintext *word* occupies that index range. See §4. |

---

## 1. The critical verification: why the positions cannot be off by one

The task that produced this file asked for the numbers to be checked against multiple primary
sources. That was done (§2, §3) — but source-counting is the weaker half of the argument. The
stronger half is that **every primary publication of a clue printed the ciphertext letters
alongside the position number**, and the two are mutually redundant. Only one indexing convention
makes them agree.

K4, 97 letters, with 1-based indices:

```
pos  1      OBKR                               (panel row 25, last 4 chars)
pos  5- 35  UOXOGHULBSOLIFBBWFLRVQQPRNGKSSO    (panel row 26)
pos 36- 66  TWTQSJQSSEKZZWATJKLUDIAWINFBNYP    (panel row 27)
pos 67- 97  VTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR    (panel row 28)
```

Each published ciphertext fragment occurs **exactly once** in the 97 letters, and at exactly the
published 1-indexed start:

| fragment | occurrences in K4 | 1-indexed start | published as |
|---|---|---|---|
| `FLRV` | 1 | **22** | "positions 22 through 25" |
| `QQPRNGKSS` | 1 | **26** | "letters 26 through 34" |
| `NYPVTT` | 1 | **64** | "the 64th through 69th … characters" |
| `MZFPK` | 1 | **70** | "the 70th through 74th letters" |
| `FLRVQQPRNGKSS` | 1 | **22** | EAST + NORTHEAST, contiguous |
| `NYPVTTMZFPK` | 1 | **64** | BERLIN + CLOCK, contiguous |

Under 0-indexing the same numbers would name `LRVQ`, `QPRNGKSSO`, `YPVTTM` and `ZFPKW` — none of
which any source has ever printed. The indexing is therefore pinned by the data, not by an
editorial convention anyone could have got wrong. (Reproduce: the substring/uniqueness check is
four lines of Python against
`data/k4_ciphertext.txt`; the panel row split is in `data/sculpture_panels.txt`.)

A second, independent geometric check falls out of the panel layout. Panel row 26 is
`UOXOGHULBSOLIFBBWFLRVQQPRNGKSSO`; its first 17 letters are `UOXOGHULBSOLIFBBW`, so `FLRV` begins
at the 18th character of a row that starts at global position 5 → **5 + 17 = 22**. Panel row 27 is
`TWTQSJQSSEKZZWATJKLUDIAWINFBNYP`, and `NYP` begins at its 29th character → **36 + 28 = 64**.
NumberWorld's K4 layout diagram and Klaus Schmeh's *Cipherbrain* EAST post both print this same
row-aligned overlay of plaintext on ciphertext, which is a letter-level confirmation rather than a
restatement of a number:

```
                     EASTNORTHEAST
OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSO
                            BERLINCLOCK
TWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKW…
```

**Consequence for this project:** the 24 (ciphertext, plaintext) pairs used by every script in
`analysis/` are correct as stated. No result in `findings/` is invalidated by a position error.

The 24 pairs, for the record:

```
22:F→E 23:L→A 24:R→S 25:V→T 26:Q→N 27:Q→O 28:P→R 29:R→T 30:N→H 31:G→E 32:K→A 33:S→S 34:S→T
64:N→B 65:Y→E 66:P→R 67:V→L 68:T→I 69:T→N 70:M→C 71:Z→L 72:F→O 73:P→C 74:K→K
```

Two positions are self-enciphering: **33 (S→S)** and **74 (K→K)**. The 2014 NYT piece called the
second one out explicitly — "the 74th letter is K in both the plaintext and the ciphertext, meaning
that it is possible for a character to encrypt to itself". This single observation kills the whole
Enigma/reflector family and Playfair, and it is itself a position claim that cross-checks the
CLOCK numbering.

---

## 2. (a) Every clue Sanborn has released

Dates are the date of first publication in the named outlet. "Wording" is the published sentence,
quoted from the source named in the row beneath it. Where the *New York Times* is the publication of
record but nytimes.com is not fetchable from this environment, the verbatim wording is taken from a
syndication or a faithful quotation and that is stated.

### Clue 1 — BERLIN, 64–69

* **Date:** **2010-11-20** (online; the *New York Times* print edition carries it on **2010-11-21**,
  page A16, which is why some bibliographies date it the 21st).
* **Outlet:** *The New York Times*, John Schwartz, "Artist Releases Clue to Kryptos" (print headline
  "A Sculpture That Holds a Secret Whispers a Clue"). Syndicated the same evening by msnbc.com under
  "Sculptor dangles clues to secret in CIA's backyard", dateline **Nov. 20, 2010, 8:43 PM EST**.
* **Published wording (verbatim, from the msnbc/NBC syndication of Schwartz's copy):**
  > "The characters that are the 64th through 69th in the final series on the sculpture read NYPVTT.
  > When deciphered, they read BERLIN."
* **Positions:** ciphertext `NYPVTT` at **64–69** → plaintext `BERLIN`.
* **Wikipedia's restatement** (independent of the mirror above): "'NYPVTT', the 64th–69th letters in
  passage four, become 'BERLIN' after decryption."
* **Same-day context:** the NYT simultaneously published photographs of Sanborn's original
  handwritten K1/K2 coding charts. Sanborn's stated motive was frustration: "I assumed the code
  would be cracked in a fairly short time."
* URLs: <https://www.nytimes.com/2010/11/21/us/21code.html> · charts
  <https://www.nytimes.com/2010/11/21/us/21codecharts.html> · syndication
  <https://www.nbcnews.com/id/wbna40294019> · NPR follow-up 2010-11-22
  <https://www.npr.org/2010/11/22/131520768/-kryptos-sculptor-drops-new-clue-in-20-year-mystery>

### Clue 2 — CLOCK, 70–74

* **Date:** **2014-11-20** (online; NYT print **2014-11-21**).
* **Outlet:** *The New York Times*, John Schwartz, "Another Kryptos Clue Is Offered in a 24-Year-Old
  Mystery at the C.I.A."
* **Published wording (as quoted consistently by Wikipedia, Intel Today and rumkin):**
  > "the letters 'MZFPK', the 70th–74th letters in passage four, become 'CLOCK' after decryption."
* **Positions:** ciphertext `MZFPK` at **70–74** → plaintext `CLOCK`. With clue 1 this makes
  `NYPVTTMZFPK` (64–74) → `BERLINCLOCK`.
* **Sanborn, quoted in the same piece:**
  > "You'd better delve into that particular clock."
  >
  > "There are several really interesting clocks in Berlin."
  He declined to say which clock. (He did not name it until 2025 — see §5.)
* **The self-encipherment note**, published with this clue: the 74th character is `K` in both
  ciphertext and plaintext.
* URL: <https://www.nytimes.com/2014/11/21/us/another-kryptos-clue-is-offered-in-a-24-year-old-mystery-at-the-cia.html>

### Clue 3 — NORTHEAST, 26–34

* **Date:** **2020-01-29.**
* **Outlet:** *The New York Times* interactive, John Schwartz and Jonathan Corum, "This Sculpture
  Holds a Decades-Old C.I.A. Mystery. And Now, Another Clue."
* **Published wording:**
  > "at positions 26 to 34, ciphertext 'QQPRNGKSS' is the word 'NORTHEAST'."
  *Smithsonian Magazine*, reporting it two days later: "The one-word hint — a decryption of letters
  26 through 34 — is the third and final clue Sanborn is willing to offer."
* **Positions:** ciphertext `QQPRNGKSS` at **26–34** → plaintext `NORTHEAST`.
* **Presented as final.** Sanborn told NPR the next day (*All Things Considered*, 2020-01-30):
  > "Well, it is very close – within days – to when I actually developed that 97-character string."
  and
  > "It's a 97-character phrase. And that phrase is in itself a riddle. It's mysterious. It's going
  > to lead to something else. It's not going to be finished when it's decoded."
* URLs: <https://www.nytimes.com/interactive/2020/01/29/climate/kryptos-sculpture-final-clue.html> ·
  <https://www.npr.org/2020/01/30/801323608/a-new-and-final-clue-to-kryptos-a-long-standing-puzzle> ·
  <https://www.smithsonianmag.com/smart-news/third-and-final-clue-released-ci-sculptures-last-puzzling-passage-180974102/>

### Clue 4 — EAST, 22–25

* **Dates:** released **privately in April 2020**; surfaced publicly and was confirmed on
  **2020-08-24**. (Despite clue 3 having been billed as the last one.)
* **Outlet:** not an article. Sanborn emailed a layout image of K4 to correspondents who had written
  to him; a member of Elonka Dunin's Kryptos discussion list posted it; Klaus Schmeh wrote it up on
  *Cipherbrain* on **2020-08-24**, and *New York Times* journalist John Schwartz confirmed it the
  same day on Twitter (@jswatz).
* **Positions:** ciphertext `FLRV` at **22–25** → plaintext `EAST`. Combined with clue 3 this makes
  `FLRVQQPRNGKSS` (22–34) → `EASTNORTHEAST`.
* **Published wording** (Intel Today, relaying the layout): "The four letters in positions 22–25,
  cipher-text FLRV, are EAST in the plain-text."
* **Sanborn, by email, on whether the release was accidental:**
  > "I don't do much that's inadvertent."
  and
  > "I released this layout to several people as early as April … to spice things up during this
  > unpresidented [sic] time and to see how long it would take to flow through the community, and
  > frankly I was a tad bored."
* URLs: <https://scienceblogs.de/klausis-krypto-kolumne/2020/08/24/jim-sanborn-publishes-another-new-kryptos-clue/> ·
  <https://twitter.com/jswatz/status/1297658577914667008> ·
  <https://inteltoday.org/2020/09/28/the-kryptos-sculpture-jim-sanborn-this-is-the-third-and-to-be-sure-final-clue-update-and-now-a-4th-clue/>

### Not a positional clue: the November 2025 open letter

See §5.4. The four items released in November 2025 are **thematic**, carry no index numbers, and add
no (ciphertext, plaintext) pairs.

---

## 3. Discrepancies found, stated explicitly

Every source consulted gives the same four position ranges. The discrepancies below are in the
*prose around* the numbers, in dates, or in names — none of them changes a crib.

**D1 — *Smithsonian Magazine* swaps BERLIN and CLOCK against their positions.** The sentence, quoted
verbatim, is:

> "The other two hints—'clock' and 'Berlin,' released in 2010 and 2014, respectively—sit
> back-to-back at positions 64 through 69 and 70 through 74."

Read in the order written, this assigns *clock* to 2010 and 64–69, and *Berlin* to 2014 and 70–74.
Both assignments are backwards: BERLIN is the 2010 clue at 64–69 and CLOCK is the 2014 clue at
70–74. The position *numbers* in the sentence are correct; only the word order is wrong.
<https://www.smithsonianmag.com/smart-news/third-and-final-clue-released-ci-sculptures-last-puzzling-passage-180974102/>
**This is exactly the class of error the task was worried about**, and it is live in a
well-regarded outlet. Any pipeline that scraped that sentence would build a crib set that fails
every test for reasons having nothing to do with the cipher.

**D2 — the same *Smithsonian* piece dates the sculpture to 1991** ("a sculpture erected on the
intelligence agency's grounds in 1991"). *Kryptos* was dedicated **1990-11-03**. It also writes "In
1998, the artist told Schwartz…", which cannot be right — Schwartz's reporting on Kryptos begins in
2010.

**D3 — BERLIN clue date, 20th vs 21st November 2010.** Both appear in bibliographies. The
resolution: **online 2010-11-20**, **print 2010-11-21**. The NBC/msnbc syndication timestamp
(Nov. 20, 2010, 8:43 PM EST) settles it. The same online/print split explains the 2014 clue
(online 2014-11-20, print 2014-11-21). `data/cribs.json` already records this correctly.

**D4 — NORTHEAST release date, January vs February 2020.** Intel Today's retrospectives say
"February 2020"; *Smithsonian* is dated January 31; the NYT interactive is **2020-01-29** and the
NPR interview aired **2020-01-30**. **2020-01-29** is the correct first-publication date;
"February" is an artefact of later aggregation.

**D5 — the name of the person who found LAYER TWO.** Genuine, unresolved, and worth flagging.
* Wikipedia: "**Nicole** Friedrich, a logician from Vancouver, British Columbia, Canada, determined
  that another possible plaintext was 'WESTXLAYERTWO'."
* Elonka Dunin's own timeline and LEMMiNO: "**Monet** Friedrich", on **2005-10-11**, who "was
  crib-dragging different keywords through K2 when she noticed the keyword BSCISSAA would produce
  PLAYER TWO instead of ID BY ROWS."

Dunin ran the group in which the discovery was made, so her page is the more primary of the two.
This repository's `README.md` and `data/k1_k3_plaintext.txt` currently say "Nicole", following
Wikipedia. **Recommendation: record the name as "Friedrich (given name published as both Monet and
Nicole)" until someone can check the 2005 list archive.** Nothing cryptanalytic depends on it.

**D6 — the mechanism of the 2005 discovery is described two ways.** Wikipedia: she "determined that
another possible plaintext was WESTXLAYERTWO". Dunin/LEMMiNO: she crib-dragged and found that the
*mis-shifted* keyword `BSCISSAA` yields `PLAYERTWO`. These are the same event seen from different
ends — a one-letter key phase shift is exactly what a one-letter ciphertext omission produces — but
the Dunin version is the mechanically informative one and is the version to quote.

**D7 — `elonka.com` reachability.** `findings/sanborn_statements.md` records elonka.com as
unfetchable behind a bot challenge. **As of 2026-09-13 it is fetchable** when requested **without
the `www.` prefix**: `https://elonka.com/kryptos/...` works, `https://www.elonka.com/kryptos/...`
returns nothing. The Kryptos FAQ, the timeline and the 2006 announcement were all retrieved this
way for this document. `elonka.com/kryptos/sanborn/antipodes.html` still returned empty.

**D8 — Dunin's timeline stops at May 2014.** It has no entries for the 2014 CLOCK clue, the 2020
clues, the 2025 auction or anything after. Do not treat its silence as evidence.

---

## 4. What is actually contested about the clues (and it is not the numbers)

The numbers are solid. The *semantics* of a clue are not, and this is a real constraint on how the
cribs may be used.

* **2013-08, ACA convention, Norfolk VA.** Asked whether `N` decodes to `B`, `Y` to `E` and so on,
  **Sanborn confirmed it emphatically** and "rattled through the entire crib": N=B, Y=E, P=R, V=L,
  T=I, T=N. Asked whether N *decodes* to B or *encodes* to B, he said **"decodes."** When the same
  question was put to Scheidt, Sanborn cut in: **"I'm the only one who knows."**
  (<https://kryptosfan.wordpress.com/2013/10/28/kryptos-notes-from-the-aca-convention/>)
* **2019-03, private Kryptos dinner, notes by Elonka Dunin.** Asked directly whether `NYPVTT` →
  `BERLIN` is a 1:1 relationship or whether there is an intervening step (the masking technique),
  **Sanborn backed off**:
  > "Jim backed off and said he would only commit to the fact that K4 is exactly 97 characters long,
  > and that BERLIN is plaintext that starts at exactly the 64th character, but he wouldn't go
  > further than that."
  (<https://rumkin.com/reference/kryptos/k4/>)

So there are two readings of a clue, and they are not equivalent:

| reading | claim | what it licenses |
|---|---|---|
| **strong / CT-reading** | ciphertext letter *i* maps to plaintext letter *i* at those indices | the 24 (ct, pt) pairs used by every script in `analysis/` |
| **weak / PT-reading** | the plaintext *word* occupies index range *a…b*; nothing is claimed about which ciphertext letter produced which plaintext letter | only that the plaintext contains EAST NORTHEAST at 22–34 and BERLIN CLOCK at 64–74 |

The whole of this repository's completed work assumes the strong reading, and says so. That is the
right default — it is what Sanborn said in 2013 and what the published wording ("the characters …
read NYPVTT; when deciphered, they read BERLIN") says — but it is an assumption, it is the single
assumption on which ~all the negatives rest, and Sanborn himself declined to reaffirm it in 2019.
It is tracked as constraint **C2** in `../findings/sanborn_statements.md`, and the untested weak
reading is constraint **C12**.

---

## 5. (c) Every hint about K4's *nature*

Full sourcing, tiering and the "attributions that do not hold up" list are in
`../findings/sanborn_statements.md`. Condensed here to the five threads the task names.

### 5.1 K4's plaintext is itself a riddle

* **1991-04-02, ABC *World News Tonight*:**
  > "Once the plate is deciphered I'm not convinced the true meaning will be clear even then.
  > There's another deeper mystery."
  and, from the same B-roll:
  > "I've made a statement which is straightforward, but that leads to something else. There's
  > another deeper mystery. As you peel off a layer of an onion… you get closer to the heart of what
  > it is… It's in English, it's in plain English, it's in text, and you can read it, but that isn't
  > necessarily the whole story."
* **1999, *New York Times*:** the sculpture "contains a riddle within a riddle — one that will be
  solvable only after the 4 encrypted passages are known."
* **2005-06-09, NPR *Morning Edition*:** whoever cracks part 4 will then be **at the beginning of
  the puzzle**.
* **2020-01-30, NPR:**
  > "It's a 97-character phrase. And that phrase is in itself a riddle. It's mysterious. It's going
  > to lead to something else. It's not going to be finished when it's decoded."
* **Scheidt, *Wired* 2005-01-21:** "the idea of encoding a message is not only to encode the
  externals of a message (the English language), but the message itself. Once it is readable, **it
  may have other encoding that's involved in it**."
* **Scheidt, *Wired* 2009:** "There may be more to the puzzle than what you see… Just because you
  broke it doesn't mean you have the answer."

**Operational consequence.** A correct 97-character K4 plaintext may score badly on English
quadgrams — it is expected to be terse, referential, and to contain a compass bearing, a place name
and possibly a deliberate misspelling. Any search that filters candidates on prose-like English can
discard the answer. This is constraint **C8**.

### 5.2 Solving K4 is not the end; the sculpture and its location may matter

* **Sanborn, *Wired News*, 2005-01-20, asked whether you must be on CIA grounds to solve Kryptos:**
  > "**No.**" … "Well, yeah [you can solve it from the text posted online]. That doesn't mean that
  > what I've said in the piece doesn't do something physically there at the agency."
* **2009 video interview (blogger's paraphrase, weak):** solvers have "everything we need at
  *Antipodes*" and do not need "environmentals".
* **2013 ACA, Sanborn:**
  > "Yes, there is something buried adjacent to Kryptos… The thing that was buried is a bronze USGS
  > marker. It was half buried. It had little cross hairs on the top of it."
  It had been removed by about 2011, "but it is important."
* **Scheidt, 2003 (Dunin's notes):** "it was necessary to recover the keys, and that the keys were
  concealed at the sculpture."

**Status of that last line in this project:** the "key is hidden elsewhere on or around the
sculpture" branch has now been searched and closed — see `INDEX.md`. The distinction that survives
is Sanborn's own: the **cipher** is solvable from the published transcription; the **meaning**
points at a physical place.

### 5.3 The K5 statements

* **2013 ACA, Sanborn, asked whether K4 can be solved without solving K1–K3 first:**
  > "Yes, but **K5 cannot be solved without K4**."
* **2025-08-14**, open letter via the *Washington Post*: Sanborn confirms K5 exists and will be
  revealed after K4 is solved.
* **2025-11-12, *Scientific American*:** the new code "will involve elements of the other puzzles
  and, **like K4, will be 97 characters long. Both 97-letter messages will share some of the same
  coded words in the same position.**" K5 is itself a riddle that "is not going to be finished when
  it's decoded", is thematically tied to K2's "its buried out there somewhere", and is destined for
  "a public space".
* **RR Auction lot description, 2025-10-16:** item 6 of the archive is an "unpublished 1988
  alternate K4 plaintext and coding chart — now known as K5". So K5 predates the final K4 plaintext
  and was built on the *same* 1988 worksheet.
* **Paradigm, 2026-06-12:** holds the K5 ciphertext and "plan to release K5 in the future". No date.

**Why this is the single most valuable open lead.** If K4 and K5 are position-preserving
encipherments of two different 97-character plaintexts under the same or nearly the same chart, the
key cancels: `idx(C4ᵢ) − idx(C5ᵢ) = idx(P4ᵢ) − idx(P5ᵢ) (mod 26)`, and the *shared coded words at
shared positions* give stretches where that difference is **zero**. That is classical depth-2 and
would be worth more than all four cribs combined. It is blocked on publication. Constraint **C10**;
the standing action is to watch <https://www.paradigm.xyz/kryptos/k4>.

A corollary usable today: the 97-character length was fixed **in 1988**, for a chart that predates
the final plaintext. 97 is a property of the *worksheet*, not of the message.

### 5.4 The masking technique — and the fact that Sanborn did not recognise the term

This is the most load-bearing and most misread item in the whole record.

* **Scheidt, *Wired News*, 2005-01-21:**
  > "There are four different processes. Two of them are similar and the other two are different
  > things. The first three processes were designed so that a person could, through cryptographic
  > analysis, have access to the English language (on the sculpture). And the last process, **I
  > masked the English language** so it's more of a challenge now."
  >
  > "…the English language is still visible through the code. (But with) this other technique (in
  > the fourth part), I disguise that. So … **you need to solve the technique first and then go for
  > the puzzle.**"
  >
  > **WN: Are all four of the processes known processes?**
  > **Scheidt: The masking technique may not be known.**
  > WN: What do you mean?
  > Scheidt: **"That's part of the puzzle I told (Jim) I would keep secret."**
* **Scheidt, asked about Sanborn having modified his systems further:**
  > "Ah hah. I can't respond to that one. I haven't heard him say that before. It's possible I
  > guess. I haven't talked to Jim on what he did, but I do know … there was some masking techniques
  > that were used and that's about it."
* **Scheidt, c. 2004, on steganography:** "I used a bit of stego when designing the fourth part of
  Kryptos", later clarified by him in writing: "there was a piece relating to Stego, **but did not
  state how or in what context**."
* **Sanborn, 2019 Kryptos dinner (Dunin's notes) — the crucial line:**
  > "…we were trying to find out if there was a 1:1 relationship from NYPVTT to BERLIN, or there was
  > some other step, the masking technique. **Jim was confused when we mentioned masking technique,
  > evidently it's something that Ed said that Jim didn't understand.**"

**Reading.** "Masking technique" is **Scheidt's name for his design goal** — flatten the English
signal so that frequency counting, which broke K1–K3, fails on K4. It is not the name of a cipher,
Scheidt never said what it was, and **the man who actually performed the encryption did not
recognise the term**. Any model that treats "masking" as a specific named operation Sanborn applied
is building on sand. What the statement does license is the negative: K4 is **not** monoalphabetic
and not a short-period polyalphabetic that leaves English visible — which is precisely what this
repository has confirmed by exhaustion.

A related caution: K4's flat index of coincidence is *not* evidence that masking is visible in the
statistics. For a 97-letter string the null IoC is 0.0385 ± 0.0028, so the observed 0.0361 sits at
z = −0.84 (P(IoC ≤ observed) = 0.22) — completely unremarkable. Ninety-seven characters is simply
too short to distinguish a masked ciphertext from a uniformly random string.

### 5.5 The 2025 thematic clues

Released in Sanborn's November 2025 open letter to the Kryptos community, reported by *Scientific
American* on **2025-11-12**. Four items, **none positional**:

1. **Two events figure in the solution: a 1986 trip Sanborn took to Egypt, and the 1989 fall of the
   Berlin Wall.**
2. **"BERLINCLOCK" refers to the World Clock (Urania-Weltzeituhr) at Alexanderplatz** — *not* the
   Mengenlehreuhr that solvers assumed for a decade.
3. **The codes within Kryptos are about "delivering a message".**
4. **K5 is thematically connected to the K2 text "its buried out there somewhere".**

Plus, on the mathematics: **"Who says it is even a math solution?"** and **"I was fortunate not to
understand mathematics, probably in my ability to make the code."** He counselled "creativity".

**Item 2 retires a whole branch of community work.** Every base-5 lamp-row keystream derived from
the Mengenlehreuhr rests on a guess that Sanborn has now contradicted. (This project generated and
tested those streams anyway, before and after the clarification — see `INDEX.md` — and they fail on
their own merits.)

---

## 6. (b) The 2006 correction: `ID BY ROWS` → `X LAYER TWO`

Easy to get backwards, so, precisely.

**Which letter, and where.** Sanborn **omitted an `S` from the carved K2 ciphertext**, which
corresponds to an **`X` in the plaintext**. Elonka Dunin's announcement page and her timeline both
place it as a ciphertext `s` inserted **in the ninth position from the end of K2**. Concretely:

```
carved K2 ciphertext, last 8 letters :  ...  W J L L A E T G          (369 letters total)
corrected                            :  ... S W J L L A E T G          (370 letters)
                                         ^ the omitted S, at corrected position 362
```

Verified computationally in this repository: re-encrypting the corrected K2 plaintext with
ABSCISSA on the KRYPTOS-keyed Quagmire III reproduces the carved ciphertext **exactly for the first
361 letters**, then expects `SWJLLAETG` where the sculpture carries `WJLLAETG`. Carved K2
ciphertext = **369** letters; K2 plaintext = **370**. (`findings/runningkey.md` §0,
`data/k1_k3_plaintext.txt`.)

**Why one missing letter destroyed the ending.** K2 is a repeating-key polyalphabetic. A dropped
ciphertext letter throws every subsequent letter one step out of phase with the key, so the tail
decrypts under the wrong key letters. The remarkable accident is that the out-of-phase garbage
happened to read as the English words `ID BY ROWS`, which is why the error went unnoticed for a
decade and why every pre-2006 publication has it.

**Dates and priority.**
* **2005-10-11** — Friedrich (given name published as both **Monet** and **Nicole**; see D5), a
  Kryptos-list member in Vancouver BC, crib-dragging keywords through K2, noticed that the shifted
  keyword `BSCISSAA` yields `PLAYERTWO` rather than `IDBYROWS`. Group members read this as
  `LAYER TWO`.
* **2006-04-19** — Sanborn contacted the Kryptos community (the Yahoo group co-moderated by Dunin)
  to say he had made an error in the sculpture. Dunin, working with Chris Hanson, derived the
  corrected plaintext by inserting the ciphertext `s` in the ninth position from K2's end. Reported
  by Kim Zetter, *Wired*, "Typo Confounds Kryptos Sleuths", **2006-04-20**.
* Sanborn's stated reason for the omission: **aesthetic** — to keep the sculpture visually balanced.
  He restated the underlying point in 2025: "You could not make any mistake with 1,800 letters. It
  could not be repaired."
* Elonka's page notes that Sanborn "refused to reveal anything more than that" the new reading was
  correct.

**The corrected K2 ending.**

```
... SEVENTY SEVEN DEGREES EIGHT MINUTES FORTY FOUR SECONDS WEST X LAYER TWO
```

### 6.1 Every statement about what the correction implies for K4

Ordered from *what Sanborn actually said* down to *what the community inferred*.

1. **Sanborn's own statement, 2006, and the whole of it:** in the same commentary he said that
   **the answers to the first three passages contain clues to the fourth passage.** This is the
   primary — and only — citation for the "K1–K3 plaintexts are clues to K4" claim. (Wikipedia
   repeats it verbatim: "the answers to the first three passages contain clues to the fourth
   passage.")
2. **A corroborating earlier statement**, *Wired News* 2005-01-20: **"I have left instructions in
   the earlier text that refer to later text."**
3. **What the correction proves regardless of interpretation:** the carved ciphertext is
   **demonstrably not a faithful record of the encipherment.** One letter is missing on the K2 side
   by the artist's own admission, for aesthetic reasons. The same could be true of K4 — and nobody,
   Sanborn included, ever ran a reverse check on K4 (2005 dinner notes, Dunin/Wilson: "neither
   Sanborn nor anyone else has done a reverse check to make sure the code for K4 works"). This is
   constraint **C6**: every sweep in this repository that demanded an exact 24/24 crib fit is void
   if a single carved K4 letter is wrong.
4. **Scheidt casts doubt on even the error being an error.** ACA convention, 2013: "The ID BY ROWS /
   LAYERTWO error may not have been a mistake after all. Sometimes in spycraft you deliberately do
   these things." (Second-hand, via an attendee.)
5. **Elonka's contemporaneous reading**, on her announcement page: the words "Layer Two" "could be a
   key that (figuratively) open[s] up some other section of the sculpture" and "may help find one of
   the intended Kryptos keys."
6. **Community interpretations — hypotheses, not Sanborn's words.** That "LAYER TWO" names the
   second *physical* layer of the sculpture; that it identifies the right-hand tableau panel as a
   keystream source; that it instructs you to apply two layers of cipher; that it echoes Howard
   Carter's "what we may call the second layer" (p. 170 of his Tutankhamun account — K3's plaintext
   is Carter). All are plausible and none is attributable. Treat as hypotheses. **Status in this
   project:** the "two layers of cipher" reading is exhaustively tested and negative
   (`findings/twocipher.md`); the "tableau as keystream in reading order" reading is tested and
   negative (`findings/runningkey.md`); the "tableau as a *coordinate lookup*" reading is
   constraint **C11** and is **untested**.

---

## 7. (d) Machine-readable positions

`keystreams/clue_positions.tsv` — four rows, one per released clue, 1-indexed inclusive:

```
clue_word	start	end	source_url	confidence
EAST	22	25	https://twitter.com/jswatz/status/1297658577914667008	high
NORTHEAST	26	34	https://www.nytimes.com/interactive/2020/01/29/climate/kryptos-sculpture-final-clue.html	high
BERLIN	64	69	https://www.nytimes.com/2010/11/21/us/21code.html	high
CLOCK	70	74	https://www.nytimes.com/2014/11/21/us/another-kryptos-clue-is-offered-in-a-24-year-old-mystery-at-the-cia.html	high
```

Notes for anyone consuming it:

* `source_url` is the **publication of record**. Neither `nytimes.com` nor `twitter.com` is fetchable
  from this environment; the verbatim wording was verified through the mirrors and restatements
  listed in §2, and the numbers were verified independently against the ciphertext itself (§1).
* Start/end are **1-indexed and inclusive**, into the 97-letter K4 ciphertext in
  `data/k4_ciphertext.txt`.
* The file deliberately does **not** contain the derived contiguous runs `EASTNORTHEAST` (22–34) and
  `BERLINCLOCK` (64–74), so that a script summing the rows gets exactly 24 crib letters and cannot
  double-count.
* `confidence` is `high` for all four: the number and the ciphertext letters cross-check, every
  consulted source agrees, and the repository's own `data/cribs.json` matches.

---

## 8. Sources

**Used for the position verification (§1–§3)**
- Wikipedia, *Kryptos* — <https://en.wikipedia.org/wiki/Kryptos>
- John Schwartz, "Artist Releases Clue to Kryptos", *NYT*, 2010-11-20 —
  <https://www.nytimes.com/2010/11/21/us/21code.html>; verbatim via the msnbc.com syndication
  <https://www.nbcnews.com/id/wbna40294019>
- John Schwartz, "Another Kryptos Clue Is Offered…", *NYT*, 2014-11-20 —
  <https://www.nytimes.com/2014/11/21/us/another-kryptos-clue-is-offered-in-a-24-year-old-mystery-at-the-cia.html>
- Schwartz & Corum, "This Sculpture Holds a Decades-Old C.I.A. Mystery. And Now, Another Clue",
  *NYT*, 2020-01-29 —
  <https://www.nytimes.com/interactive/2020/01/29/climate/kryptos-sculpture-final-clue.html>
- John Schwartz (@jswatz), EAST confirmation, 2020-08-24 —
  <https://twitter.com/jswatz/status/1297658577914667008>
- Klaus Schmeh, "Jim Sanborn publishes another Kryptos clue", *Cipherbrain*, 2020-08-24 —
  <https://scienceblogs.de/klausis-krypto-kolumne/2020/08/24/jim-sanborn-publishes-another-new-kryptos-clue/>
- Intel Today, "The KRYPTOS Sculpture — SECTION IV: A few clues", 2017-09-10 —
  <https://inteltoday.org/2017/09/10/the-kryptos-sculpture-section-iv-a-few-clues/>
- Intel Today, "…third and to be sure final clue [UPDATE: 4th clue]", 2020-09-28 —
  <https://inteltoday.org/2020/09/28/the-kryptos-sculpture-jim-sanborn-this-is-the-third-and-to-be-sure-final-clue-update-and-now-a-4th-clue/>
- *Smithsonian Magazine*, "New Clue May Be the Key to Cracking CIA Sculpture's Final Puzzling
  Passage", 2020-01-31 —
  <https://www.smithsonianmag.com/smart-news/third-and-final-clue-released-ci-sculptures-last-puzzling-passage-180974102/>
  **(contains discrepancy D1 and D2)**
- Tyler Akins, "K4 — Unsolved", rumkin — <https://rumkin.com/reference/kryptos/k4/>
- NumberWorld, "Kryptos — The Cipher (Part 4)" —
  <https://www.numberworld.blog/2020/07/kryptos-cipher-part-4.html>
- Boxentriq, "Kryptos Cipher Solutions" —
  <https://www.boxentriq.com/guides/kryptos-cipher-solutions>
- dcode.fr, Kryptos — <https://www.dcode.fr/kryptos-sculpture>
- Mysterious Writings, "A New Clue Released for the Unsolved Code of Kryptos" —
  <https://mysteriouswritings.com/a-new-clue-released-for-the-unsolved-code-of-kryptos/>

**Used for the 2006 correction (§6)**
- Elonka Dunin, "Kryptos Part 2 Was Wrong" — <https://elonka.com/kryptos/CorrectedK2Announcement.html>
- Elonka Dunin, Kryptos timeline — <https://elonka.com/kryptos/KryptosTimeline.html>
- Kim Zetter, "Typo Confounds Kryptos Sleuths", *Wired*, 2006-04-20 —
  <https://www.wired.com/2006/04/typo-confounds-kryptos-sleuths/> (wired.com not fetchable here;
  content via Wikipedia's and Dunin's quotation)
- LEMMiNO, "The Unbreakable Kryptos Code" — <https://www.lemmi.no/p/the-unbreakable-kryptos-code>

**Used for the nature-of-K4 hints (§5)**
- Kim Zetter, "Questions for Kryptos' Creator", *Wired*, 2005-01-20 —
  <https://www.wired.com/2005/01/questions-for-kryptos-creator/>
- Kim Zetter, "Inside Info on Kryptos Codes" (Scheidt), *Wired*, 2005-01-21 —
  <https://www.wired.com/2005/01/inside-info-on-kryptos-codes/>
  (both mirrored at <http://scirealm.org/KryptosHints.html> and
  <https://kryptosfan.wordpress.com/the-continuity-of-kryptos/pr/questions-for-kryptos-creator-by-kim-zetter/>)
- "Kryptos Notes From the ACA Convention", 2013-10-28 —
  <https://kryptosfan.wordpress.com/2013/10/28/kryptos-notes-from-the-aca-convention/>
- "More about Ed Scheidt's ACA Talk", 2013-10-30 —
  <https://kryptosfan.wordpress.com/2013/10/30/more-about-ed-scheidts-aca-talk/>
- NPR *All Things Considered*, 2020-01-30 —
  <https://www.npr.org/2020/01/30/801323608/a-new-and-final-clue-to-kryptos-a-long-standing-puzzle>
- Dan Vergano, "Final Clues to Mystery of CIA Kryptos Puzzle Released", *Scientific American*,
  2025-11-12 —
  <https://www.scientificamerican.com/article/cia-kryptos-puzzle-creator-releases-final-clues/>
- RR Auction lot 7302001 —
  <https://www.rrauction.com/auctions/lot-detail/350761607302001-the-complete-secrets-of-kryptos-jim-sanborns-private-archive/>
- Paradigm, "Project Kryptos", 2026-06-12 — <https://www.paradigm.xyz/writing/kryptos> ·
  <https://www.paradigm.xyz/kryptos/k4>

**Within this repository**
- `../findings/sanborn_statements.md` — the full tiered dossier of Sanborn/Scheidt statements and
  the C1–C18 constraint list
- `../findings/prior_art.md` §A.2 — the crib release timeline as previously recorded (agrees)
- `../README.md` §3.2 — the crib table
- `../data/cribs.json` — the canonical machine-readable crib set (agrees)
