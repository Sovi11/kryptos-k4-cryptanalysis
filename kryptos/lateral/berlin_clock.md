# The Berlin clocks, the compass rose, the Morse slabs, and the K2 coordinates

Reference document for the "lateral key material" line of attack. **This file is documentation, not
cryptanalysis.** It records (a) what the two Berlin clocks actually are, (b) everything Sanborn has
said about "BERLIN CLOCK" and what the eleven-year ambiguity did to the community, (c) exactly what
this repo generated from that material and exactly how it failed, (d) the Morse slabs, compass rose
and lodestone character for character, and (e) what the K2 coordinates point at and what bearing
Berlin really lies on from the sculpture.

Compiled 2026-09-13. Every factual claim carries an inline URL. Claims I could not pin to a reliable
source are marked **[uncertain]**. Nothing here is a proposed K4 solution.

Backing arithmetic — Morse renderings, Mengenlehreuhr state counts, all bearings, and the
chance-expectation figures quoted in §4 — is in
`/Users/pravarkataria/Desktop/crypto/kryptos/analysis/berlin_clock_doc_checks.py`. Run it; every
number below is printed by it. The keystream generator is
`/Users/pravarkataria/Desktop/crypto/kryptos/lateral/gen_berlin_clock_keystreams.py`; the tests are
`test_lateral.py` and `test_lateral_numeric.py` in the same directory, with their captured output in
`test_lateral_out.txt` and `test_lateral_numeric_out.txt`.

---

## Contents

1. [The Mengenlehreuhr](#1-the-mengenlehreuhr-berlin-uhr-set-theory-clock)
2. [The Urania-Weltzeituhr](#2-the-urania-weltzeituhr-world-clock-alexanderplatz)
3. [Every Sanborn statement about the Berlin Clock](#3-every-sanborn-statement-about-the-berlin-clock)
4. [What was generated, what was tested, and the negative result](#4-what-was-generated-what-was-tested-and-the-negative-result)
5. [The compass rose, the lodestone and the Morse slabs](#5-the-compass-rose-the-lodestone-and-the-morse-slabs)
6. [The K2 coordinates, and the true bearing to Berlin](#6-the-k2-coordinates-and-the-true-bearing-to-berlin)
7. [Bottom line](#7-bottom-line)

---

## 1. The Mengenlehreuhr (Berlin-Uhr, "Set Theory Clock")

### 1.1 What it is and where it stands

The **Mengenlehreuhr** — literally "set-theory clock", also called the **Berlin-Uhr** and, in English
writing about Kryptos, "the Berlin Clock" — is a public clock that displays the time as counts of
illuminated coloured fields rather than as hands or digits. It was **installed on 17 June 1975** and
entered the *Guinness Book of Records* as "the first public clock in the world that tells the time by
means of illuminated, coloured fields."
([Wikipedia: Mengenlehreuhr](https://en.wikipedia.org/wiki/Mengenlehreuhr),
[de.wikipedia: Berlin-Uhr](https://de.wikipedia.org/wiki/Berlin-Uhr))

* **Original site:** the central reservation of the **Kurfürstendamm at the corner of Uhlandstraße**,
  Berlin-Charlottenburg, then West Berlin. It stood there 1975–1995.
* **Present site:** since **1996**, in front of the Tourist-Information-Center at the **Europa-Center,
  Budapester Straße**, a few hundred metres away. (≈ 52.5052 N, 13.3389 E.)
  ([de.wikipedia: Europa-Center](https://de.wikipedia.org/wiki/Europa-Center-Berlin))

Height is commonly given as about 7 m; I could not source that to a primary reference — **[uncertain]**.

### 1.2 Row structure — the full anatomy

Five horizontal rows, **24 light fields in total** (1 + 4 + 4 + 11 + 4 = 24), read top to bottom:

| # | row | fields | colour | each lit field means | range |
|---|---|---|---|---|---|
| 0 | seconds lamp | **1** | yellow | — (a heartbeat, no value) | on for odd seconds, off for even |
| 1 | five-hour row | **4** | red | **5 hours** | 0–4 lit → 0, 5, 10, 15, 20 h |
| 2 | one-hour row | **4** | red | **1 hour** | 0–4 lit → 0–4 h |
| 3 | five-minute row | **11** | yellow, but the **3rd, 6th and 9th are red** | **5 minutes** | 0–11 lit → 0–55 min |
| 4 | one-minute row | **4** | yellow | **1 minute** | 0–4 lit → 0–4 min |

The three red lamps inside the eleven mark the **quarter hours**: the 3rd lamp is minute **15**, the
6th is **30**, the 9th is **45**. They exist purely so the eye can read the long row at a glance.
The top lamp "blinks on/off every two seconds" — i.e. its state has a one-second period, lit on odd
seconds.
([Wikipedia](https://en.wikipedia.org/wiki/Mengenlehreuhr),
[secretcitytravel](http://www.secretcitytravel.com/berlin-march-2014/berlin-set-theory-clock-guide.shtml),
[Atlas Obscura listing](https://www.atlasobscura.com/places/mengenlehreuhr))

### 1.3 How it encodes a time

Pure **base-5 place value**, twice over — once for hours, once for minutes:

```
hours   = 5 * (lamps lit in row 1) + (lamps lit in row 2)
minutes = 5 * (lamps lit in row 3) + (lamps lit in row 4)
```

Worked examples (all verified by `berlin_clock_doc_checks.py` §2):

| time | row 1 (5h) | row 2 (1h) | row 3 (5m) | row 4 (1m) | arithmetic | value lamps lit |
|---|---|---|---|---|---|---|
| 00:00 | 0 | 0 | 0 | 0 | 0·5+0 h, 0·5+0 m | 0 |
| 10:31 | 2 | 0 | 6 | 1 | 2·5+0 = 10 h, 6·5+1 = 31 m | 9 |
| 12:32 | 2 | 2 | 6 | 2 | 2·5+2 = 12 h, 6·5+2 = 32 m | 12 |
| 17:54 | 3 | 2 | 10 | 4 | 3·5+2 = 17 h, 10·5+4 = 54 m | 19 |
| 19:00 | 3 | 4 | 0 | 0 | 3·5+4 = 19 h, 0 m | 7 |
| 23:59 | 4 | 3 | 11 | 4 | 4·5+3 = 23 h, 11·5+4 = 59 m | 22 |

### 1.4 Arithmetic a cryptanalyst would care about

Computed, not quoted:

* **1,440** distinct lamp patterns across a day (one per minute); **2,880** counting the seconds lamp.
* **23** value-bearing lamps; the seconds lamp is the 24th.
* **The 24 lamps are never all lit at once.** The ceiling is **23** (22 value lamps + seconds), first
  reached at **19:59**. Four-of-four in the five-hour row requires h ≥ 20, which forces h mod 5 ≤ 3,
  so the two hour rows peak jointly at **7 of 8**. The minute rows do reach 15 of 15, at :59.
* Because the hour rows can never both saturate, the mapping (h, m) → lamp pattern is injective but
  **not surjective** onto the 2^23 possible patterns: only 1,440 of them ever occur.
* Reading order top-left to bottom-right gives a natural 24-bit word per minute; the per-row lit
  counts give a 4-symbol word per minute. Both parameterisations were generated (§4).

### 1.5 History, relocation, restoration

* **Designer: Dieter Binninger** (born 1938), a trained watchmaker and electrical engineer, who
  developed the clock **on commission from the Berlin Senate** (*im Auftrag des Berliner Senats*).
  The oversized prototype was built by the firm Videor and given to the Bezirk Charlottenburg;
  Binninger's company also sold roughly 1,973 desk and wall versions, patented as display devices,
  some using a Texas Instruments TMS1000 microcontroller.
  ([de.wikipedia: Dieter Binninger](https://de.wikipedia.org/wiki/Dieter_Binninger))
* **The maintenance problem.** The interior was hundreds of incandescent bulbs, constantly failing —
  upkeep ran to roughly **€5,000 a year**. Binninger's response was to invent a long-life bulb (the
  *Ewigkeitsglühbirne*) rated at **150,000 hours**, after observing that traffic vibration on the
  Kurfürstendamm was killing ordinary lamps. ([de.wikipedia](https://de.wikipedia.org/wiki/Berlin-Uhr))
* **Binninger's death.** "*Am 5. März 1991 starb Binninger beim Absturz eines Privatflugzeugs nördlich
  von Helmstedt*" — on **5 March 1991** he died when his private aircraft, a TB10 Tobago, crashed
  north of Helmstedt; **his son and the pilot died with him**. He had bought an East German lamp
  factory only days earlier to begin production of the long-life bulb. This sequence — long-life bulb,
  factory purchase, fatal crash — is why the clock is, in the *New York Times*' words, "a favorite of
  conspiracy theorists". ([de.wikipedia: Dieter Binninger](https://de.wikipedia.org/wiki/Dieter_Binninger))
* **Decommissioning, 1995.** With Binninger dead and neither the city nor the district willing to
  carry the running costs, the clock was switched off and dismantled at the Kurfürstendamm site in
  **1995**, twenty years after installation.
* **Re-erection, 1996.** A group of local businesspeople funded its re-installation in front of the
  Tourist-Information-Center at the **Europa-Center on Budapester Straße**, where it stands today.
* **Restoration.** Until **2002** the fields were lit by computer-controlled halogen lamps in coloured
  glass; a renovation after 2002 replaced the coloured glass elements and fitted them with distinct
  black frames. In the **2012** refurbishment of the column the lamps were replaced with **LEDs**.
  ([de.wikipedia: Europa-Center](https://de.wikipedia.org/wiki/Europa-Center-Berlin))
* **Protection.** The whole Europa-Center complex is under *Denkmalschutz*; I found no source for a
  separate listing of the clock itself — **[uncertain]**.

Footnote worth carrying: the **"Clock of Flowing Time"** (Bernard Gitton's water clock) stands inside
the same Europa-Center. Sanborn named it in 2014 as one of Berlin's other interesting clocks (§3).

### 1.6 Why the community fixed on this clock for eleven years

Two reasons, neither of them a Sanborn statement:

1. **The name.** In English-language writing "the Berlin Clock" *is* the Mengenlehreuhr. A solver
   reading the plaintext BERLINCLOCK naturally lands on it.
2. **It looks like a cipher machine.** Base-5 counters, 24 binary fields, a one-bit seconds gate,
   quarter-hour markers — it is almost designed to be read as a keystream generator. The
   Mengenlehreuhr branch of Kryptos work is enormous for that reason alone.

Both reasons are about the clock, not about Kryptos. See §3.

---

## 2. The Urania-Weltzeituhr (World Clock, Alexanderplatz)

The clock Sanborn confirmed in **November 2025** as the actual referent.
([Wikipedia: World Clock (Alexanderplatz)](https://en.wikipedia.org/wiki/World_Clock_(Alexanderplatz)))

* **Designer: Erich John**, then a product-design lecturer. **Opened 30 September 1969**, in East
  Berlin, alongside the television tower. ≈ 52.5212 N, 13.4133 E.
* **Form:** a **twenty-four-sided column** (a regular icositetragon in cross-section), about **10 m**
  high, weighing **sixteen tons**. Each of the 24 faces is one of the Earth's main time zones and
  carries the names of major cities in it — **148 cities** in all. The hour numerals **1 through 24
  revolve around the outside** of the rotunda through the day; you find your city and read the
  number standing beneath it.
* **On top:** a steel-ring-and-sphere model of the **Solar System** that rotates once per minute.
* **Underfoot:** "*a windrose is painted onto the pavement below the column which holds up the
  clock*" — the clock literally stands on a **compass rose**. Kryptos also has a compass rose (§5).
  That echo is real and is worth noting; it is not evidence of a cipher.
* **1997:** overhauled after unification; **twenty cities added**, including Tel Aviv and Seoul.
* **2015:** declared a **historically and culturally significant monument** by the federal government.
* **Cold-War significance:** on **7 October 1989**, during the GDR's 40th-anniversary celebrations,
  opposition groups formed a demonstration that **began at the clock**; the state arrested over 1,200
  protesters. **Thirty-three days later the Wall fell.** This is the reason the Weltzeituhr and the
  1989 fall of the Wall belong to the same clue in Sanborn's 2025 letter (§3).

---

## 3. Every Sanborn statement about the Berlin Clock

Chronological. Tier letters follow the convention of
[`findings/sanborn_statements.md`](../findings/sanborn_statements.md): **A** = verbatim quote in a
named, dated publication; **B** = notes/paraphrase by a named attendee; **C** = second-hand or a
journalist's characterisation.

### 3.1 November 2010 — BERLIN (tier A)

Sanborn told John Schwartz of the *New York Times* that ciphertext **NYPVTT** at positions **64–69**
decrypts to **BERLIN**. Sources differ on 20 vs 21 November (online vs print) — **[uncertain]** on the
exact day. Coverage: [NPR, 22 Nov 2010](https://www.npr.org/2010/11/22/131520768/-kryptos-sculptor-drops-new-clue-in-20-year-mystery);
[NBC News](https://www.nbcnews.com/id/wbna40294019);
[ACM TechNews, "Berlin Is Revealed as Kryptos Clue"](https://cacmb4.acm.org/news/102070-berlin-is-revealed-as-kryptos-clue/fulltext).

At this point **"BERLIN" stood alone**. Reading it as *the Berlin Wall*, or as the city, or as the
first half of a compound, were all open.

### 3.2 20 November 2014 — CLOCK, and the sentence that started the argument (tier A)

Sanborn told the *NYT* that **MZFPK** at positions **70–74** is **CLOCK**, making the plaintext
**BERLINCLOCK** across 64–74. Asked whether the clue referred to a Berlin clock, he said:

> "There are several really interesting clocks in Berlin."

and

> **"You'd better delve into that particular clock."**

and, of Berlin's timepieces generally,

> "There's a lot of fodder there."

*NYT*, John Schwartz, "Another Kryptos Clue Is Offered in a 24-Year-Old Mystery at the C.I.A.",
<https://www.nytimes.com/2014/11/21/us/another-kryptos-clue-is-offered-in-a-24-year-old-mystery-at-the-cia.html>
(nytimes.com is not fetchable from this environment; the three quotations above are corroborated
verbatim in secondary coverage and in this repo's dossier).

**The critical point about this exchange.** Read the words themselves: *"that particular clock"* has
**no antecedent in anything Sanborn said**. The antecedent is supplied by the reporter's own
surrounding prose, which glossed it as the clock that is "a favorite of conspiracy theorists because
of the mysterious death in 1991 of its designer, Dieter Binninger" — and Binninger designed only the
Mengenlehreuhr. The same sentence went on to mention the "Clock of Flowing Time" as another candidate.

So: **the newspaper identified the Mengenlehreuhr; Sanborn did not.** The contemporaneous wire
follow-ups took the newspaper's reading and hardened it — a January 2015 Newser piece carried on Fox
News describes the referent flatly as the Berlin clock that is "itself a puzzle that tells time using
colored blocks of light", which is the Mengenlehreuhr and nothing else
([Fox News / Newser, 8 Jan 2015](https://www.foxnews.com/science/man-behind-secret-code-at-cia-releases-2nd-hint.print)).
That is the origin of an eleven-year misdirection that no one had to manufacture.

### 3.3 December 2014 — the community notices the ambiguity (tier C)

The kryptosfan write-up of the clue lists the candidates — Mengenlehreuhr, the **Weltzeituhr /
Urania clock at Alexanderplatz**, an atomic clock — and states plainly that **Sanborn never said
which**, arguing that BERLIN and CLOCK are *plaintext results*, not decryption tools.
([kryptosfan, "Kryptos F2P: Berlin Clock", 15 Dec 2014](https://kryptosfan.wordpress.com/2014/12/15/kryptos-f2p-berlin-clock/))

A contemporaneous post already noticed the compass-rose echo — that the Weltzeituhr "stands on a
compass rose shaped stone mosaic", as Kryptos has a compass rose engraved on one of its slabs
([joseph4barna, 23 Nov 2014](https://joseph4barna.wordpress.com/2014/11/23/kryptos-k4-part-4-berlin-clock-kryptos-a-compass-rose/)).
That observation turned out to point at the right clock, six years early, for a reason that was pure
coincidence at the time.

### 3.4 March 2019 — what he would and would not commit to (tier B)

At a private "Kryptos dinner", per Elonka Dunin's notes, Sanborn was pressed on whether NYPVTT maps
1:1 to BERLIN or whether a further step ("the masking technique") intervenes. He **backed off** and
would commit only to: K4 is exactly 97 characters, and BERLIN's plaintext starts at exactly character
64. He did not recognise the term "masking technique". (Relayed at
[rumkin](https://rumkin.com/reference/kryptos/k4/); full treatment in
[`findings/sanborn_statements.md`](../findings/sanborn_statements.md).)

Nothing about which clock.

### 3.5 January and August 2020 — NORTHEAST and EAST (tier A)

**29 January 2020**, *NYT*: **QQPRNGKSS** at 26–34 is **NORTHEAST**
(<https://www.nytimes.com/interactive/2020/01/29/climate/kryptos-sculpture-final-clue.html>).
**August 2020**: **FLRV** at 22–25 is **EAST**, giving the contiguous run **EASTNORTHEAST** at 22–34.

These matter to the clock question because they establish that the K4 plaintext carries **a compass
bearing and a place name** — which is what §5 and §6 are about. They say nothing about which clock.

### 3.6 12 November 2025 — the disambiguation, eleven years late (tier A)

Speaking at the International Spy Museum and in an open letter to the Kryptos community, reported by
Dan Vergano for *Scientific American*, Sanborn released four clues. Clue 2:

> "The 'BERLINCLOCK' mentioned in previous K4 clues refers to the **World Clock in Berlin**."

And clue 1:

> "Two events figure in the solution: **a 1986 trip that Sanborn took to Egypt** and the **1989 fall
> of the Berlin Wall**."

Clue 3: the codes are about **"delivering a message"**. Clue 4: **K5** is thematically connected to
K2's "its buried out there somewhere". In the same appearance he said **"Kryptos has not been
solved"** and **"K4 has not been solved or decrypted"**, joked **"Who says it is even a math
solution?"**, and counselled **"creativity"**.
([Scientific American, 12 Nov 2025](https://www.scientificamerican.com/article/cia-kryptos-puzzle-creator-releases-final-clues/))

"The World Clock in Berlin" is the **Urania-Weltzeituhr at Alexanderplatz** (§2). Clue 1 makes the
choice coherent rather than arbitrary: Alexanderplatz is where the 7 October 1989 demonstration began,
thirty-three days before the Wall fell.

### 3.7 The three-way debate, resolved and unresolved

| candidate | case for | status after Nov 2025 |
|---|---|---|
| **Mengenlehreuhr** (Set Theory Clock) | it is what "the Berlin Clock" means in English; base-5 lamp structure looks like a keystream generator; the *NYT*'s own 2014 gloss (Binninger's 1991 death) points at it | **contradicted.** Sanborn named the World Clock. Any keystream derived from the Mengenlehreuhr now rests on a decade-old community guess the artist has since corrected. |
| **Urania-Weltzeituhr** (World Clock, Alexanderplatz) | literally called the World Clock; stands on a painted windrose, echoing Kryptos's compass rose; the 7 Oct 1989 demonstration site; fits clue 1 | **confirmed** as the referent of BERLINCLOCK. |
| **The Berlin Wall** (i.e. BERLIN read alone, 2010–2014) | "BERLIN" stood alone for four years; the Wall is the obvious Berlin referent for a 1989-90 sculpture; confirmed in 2025 as thematically present | **partly right, differently.** The Wall is in the *solution's subject matter* (clue 1) but **BERLIN belongs to the compound BERLINCLOCK**, which is the World Clock. |

**Did he ever disambiguate before 2025? No.** Between the 2014 "that particular clock" and the
12 November 2025 letter there is no statement on record from Sanborn naming a clock — a gap of
**eleven years**, during which the largest single branch of community work was aimed at the wrong
object, on an identification the artist never made.

**What clue 2 does and does not license.** It fixes a *referent for a plaintext word*. It does **not**
say the clock is a key, a keystream, an algorithm, or an arithmetic device — and clue 3 ("delivering
a message") plus Sanborn's "who says it is even a math solution?" cut the other way. The honest
reading is that BERLINCLOCK is a **place named in the plaintext**, parallel to EASTNORTHEAST being a
**bearing named in the plaintext**. This repo's tests (§4) treated it as a key source anyway, because
that hypothesis is cheap to falsify and it had never been falsified quantitatively.

---

## 4. What was generated, what was tested, and the negative result

### 4.1 What was generated

`lateral/gen_berlin_clock_keystreams.py` writes **176 derived streams** into `lateral/keystreams/`,
each with a description, a source URL and a confidence grade in
[`keystreams/MANIFEST.tsv`](keystreams/MANIFEST.tsv). Every file is **derived**, not transcribed —
the derivation is the script itself.

| prefix | files | what they are |
|---|---|---|
| `mlu_*` | **163** | Mengenlehreuhr: row lengths, cumulative totals, per-lamp weights, quarter-hour markers, state-space numerics; 24-bit lamp patterns and per-row lit counts for **21 named times**; minute-by-minute ticking streams from 7 start points; a full day of lamp counts (1,440 letters) and row letters (5,760 letters) |
| `rose_*` | 7 | 16- and 32-point compass-rose abbreviations and full names (English and German), rotated variants, and bearings as digit strings |
| `wz_*` | 5 | Weltzeituhr: the 24 hour numerals, the 24 zone offsets, the icositetragon, assorted numerics |
| `geo_*` | 1 | great-circle bearings from the sculpture to both clocks, as digits |
| **total** | **176** | listed in `MANIFEST.tsv`; 44 graded high confidence, 83 medium, 49 low |

The 21 named times include the timeline of **9 November 1989** (18:50, 18:53, 19:00, 19:04, 19:05,
20:00, 21:20, 23:30), the **7 October 1989** Weltzeituhr demonstration (17:00), the Kryptos
dedication, the Mengenlehreuhr's own installation date, the K2 longitude read as a solar-time offset,
and the times shown in the canonical photographs of the clock. Each time yields **six** files: the
24-lamp bit pattern with the seconds lamp lit and with it dark, the same pattern as A/B letters, the
per-row lit counts as letters and as digits, and the 1-indexed positions of the lit lamps as letters.
(21 times × 6 = 126 of the 163 `mlu_*` files; the rest are structural constants, 7 ticking streams ×
3 forms, and the two full-day streams.)

`lateral/keystreams/` also holds **18** streams from the Antipodes / Cyrillic-Projector generator, so
the directory presents **194 `.txt` candidate keystreams** to the test harness.

### 4.2 What was tested

Both test scripts derive, for each of the 24 crib positions, the **key letter that would be required**
under a given cipher family and alphabet pairing, then ask whether any alignment of any stream
supplies those letters.

* Families: **Vigenère, Beaufort, variant Beaufort**.
* Alphabets: plaintext, ciphertext and key alphabets independently **plain** or **KRYPTOS-keyed**
  (12 family/alphabet combos in `test_lateral.py`, ×26 key-alphabet rotations).
* Crib blocks: **EASTNORTHEAST** at 0-indexed 21–33 (13 letters) and **BERLINCLOCK** at 63–73
  (11 letters), with the true **42-letter gap** enforced in the joint test.
* Modes: (i) **sliding running key** — every offset in every stream; (ii) **periodic key** — the first
  *N* letters of a stream repeated, *N* = 2…97; (iii) **Gronsfeld** — digits used directly as shifts;
  (iv) **digit pairs mod 26**; (v) **one-bit alphabet gate** driven by the binary lamp streams.

### 4.3 Results, each stated against its chance expectation

Raw output: [`test_lateral_out.txt`](test_lateral_out.txt),
[`test_lateral_numeric_out.txt`](test_lateral_numeric_out.txt). Chance figures computed in
`analysis/berlin_clock_doc_checks.py` §4 under a uniform-random-keystream null (each required key
letter matched with probability 1/26).

**Letter streams** — 73 of the 194 files carry ≥ 11 letters; 27,380 letters of corpus.

| test | alignments | best observed | E\[matches] per alignment | P(≥ best \| random) | E\[count of that good or better] | verdict |
|---|---|---|---|---|---|---|
| block 1, EASTNORTHEAST (13) | 16,538,496 | **7 of 13** matched (Hamming 6) | 0.500 | 1.74e-07 | **2.9** | at chance |
| block 2, BERLINCLOCK (11) | 16,629,600 | **6 of 11** matched (Hamming 5) | 0.423 | 1.27e-06 | **21.0** | at chance |
| joint, both blocks (24) | 15,390,336 | **8 of 24** matched (Hamming 16) | 0.923 | 2.02e-06 | **31.1** | at chance |
| periodic key, all N | 102,192 | **6 of 24** | 0.923 | — | — | at chance |

Every observed maximum sits **at or below** the number of such maxima a random keystream corpus of
that size would produce. **Hits inside the pre-registered threshold (block ≤ 2 mismatches, joint ≤ 4):
0.** That zero is not by itself informative — the null predicts E\[hits] of 3.3e-07, 1.6e-04 and
7.1e-18 for the three tests, so a false positive was never plausible. **The informative statement is
the one above it: the best fits are exactly as good as noise.**

**Numeric streams** — 55 files carry ≥ 24 digits; 2,047 digits of corpus.

| test | alignments | best | note |
|---|---|---|---|
| Gronsfeld, digits as shifts | 24,564 | 7 of 24 | **impossible outright:** depending on the alphabet pairing, **11–15 of the 24 required shifts exceed 9** and so cannot be represented by a decimal digit at all |
| digit pairs mod 26 | 10,728 | 6 of 24 | chance ≈ 0.92 |
| binary lamp streams as a one-bit alphabet gate (7 streams ≥ 97 bits) | 2,037 | 1 of 2 gate states forced a single shift | a working gate needs **both** states to force one shift value each; no offset, stream or family achieved it |

**Grand total: 48,697,953 alignments tested. Zero survivors.** For calibration: a true 24-of-24 fit
has probability 1.1e-34 under the null, so over every alignment ever run here the expected number of
spurious perfect fits is 5.3e-27 — this experiment could not have produced a false positive, and it
produced no true one.

### 4.4 What this closes, and what it does not

**Closed.** *"The K4 key is a stream you can read off the Berlin Clock (either clock), the compass
rose, or the Weltzeituhr's numerals."* Under Vigenère/Beaufort/variant-Beaufort, plain and
KRYPTOS-keyed alphabets in every pairing, every rotation, every offset, as a running key, as a
periodic key, as Gronsfeld digits, as digit pairs, or as a binary alphabet gate — no. Combined with
the Antipodes/Cyrillic, Cyrillic-Projector, compass-bearing and Alexanderplatz material tested in the
same sweep, the broader proposition **"the key is hidden elsewhere on or around the sculpture"** is
closed at this level of generality.

**Not closed, and worth being honest about.**

1. **Non-additive uses of the clock.** The sweep tests stream → key letter → shift. It does not test
   the clock as a *transposition* schedule, as a *selector* among several charts, or as a source of
   plaintext (rather than key) material.
2. **The 2025 re-pointing was not fully absorbed.** 163 of 176 generated streams are
   **Mengenlehreuhr**-derived — the clock Sanborn has since said is *not* the referent — against 5
   Weltzeituhr streams. If anyone revisits this branch, the file inventory should be inverted. That
   said, the Weltzeituhr offers far less to derive: 24 numerals and 148 city names, with no state
   machine.
3. **The clue may simply not be a key clue at all.** See §3.7. This is the most likely explanation of
   the negative, and it is consistent with everything Sanborn said in 2025.

---

## 5. The compass rose, the lodestone and the Morse slabs

### 5.1 The physical arrangement at the New Headquarters Building entrance

The CIA's own description is the best primary source for what is where:

> the sculpture "begins at the entrance to the New Headquarters Building and continues in the
> northwest corner of the New Headquarters Building courtyard"

> at the entrance, "two red granite and copperplate constructions flank the walkway from the parking
> deck", carrying "International Morse code and ancient ciphers"

> there is "a lodestone (a naturally magnetized rock) co-located with a navigational compass rose"

([CIA, "About the *Kryptos* Sculpture"](https://www.cia.gov/legacy/headquarters/kryptos-sculpture/))

Elonka Dunin's aerial-photograph analysis places the two halves on opposite sides of the path, and is
explicit about the uncertainty:

> "It's located near the north side of walkway in the above image, somewhere in the middle (we're not
> sure exactly where, but the lamppost shadow and other features in the background may eventually help
> narrow it down)." — of the Morse slabs

> "The Kryptos sculpture is in the northwestern area of the Plaza."

([Elonka, "Kryptos — The Bird's Eye View"](https://elonka.com/kryptos/KryptosAerial.html))

So: **Morse on the north side of the entrance walkway, compass rose and lodestone on the south side,
main screen in the north-west corner of the courtyard beyond.** Wikipedia adds that the Morse is read
**facing south** ([Wikipedia: Kryptos](https://en.wikipedia.org/wiki/Kryptos)).

### 5.2 The Morse messages, character for character

The messages as published by Wikipedia and rumkin, with the Morse rendered here from the standard
International Morse table by `analysis/berlin_clock_doc_checks.py` §1. **The Morse column is derived,
not transcribed from a photograph** — it says what those letters *would* be in Morse, which is the
right basis for the ambiguity analysis in §5.3, and is not a claim about individual marks in the
copper.

| # | text as carved | Morse (derived) | complete? |
|---|---|---|---|
| 1 | `SOS` | `... --- ...` | **complete** |
| 2 | `RQ` (also read `YR`) | `.-. --.-` | **complete as marks**, 2 letters; reading direction disputed |
| 3 | `LUCID` `E E E` \| `MEMORY` `E` | `.-.. ..- -.-. .. -..` / `-- . -- --- .-. -.--` | **complete** |
| 4 | `E E` `SHADOW` `E E` \| `FORCES` `E E E E E` | `... .... .- -.. --- .--` / `..-. --- .-. -.-. . ...` | **complete** |
| 5 | `E E` `VIRTUALLY` `E` \| `E E E E E E` `INVISIBLE` | `...- .. .-. - ..- .- .-.. .-.. -.--` / `.. -. ...- .. ... .. -... .-.. .` | **complete**; cut across **two plates** |
| 6 | `DIGETAL` `E E E` \| `INTERPRETATIT` | `-.. .. --. . - .- .-..` / `.. -. - . .-. .--. .-. . - .- - .. -` | **truncated.** The second word runs off the plate mid-word; `DIGETAL` is complete as carved but is one dit short of `DIGITAL` (§5.3) |
| 7 | `T IS YOUR` \| `POSITION` `E` | `- .. ... -.-- --- ..- .-.` / `.--. --- ... .. - .. --- -.` | **truncated at the left.** Universally read as "[WHA]T IS YOUR POSITION"; the opening letters disappear under the granite and the lodestone |

The lone `E` is a single dit (`.`). Wikipedia's list and rumkin's list disagree on some of the run
lengths — for example rumkin shows 5 dits before `INVISIBLE` where Wikipedia's list shows 6 — and
LEMMiNO published a correction stating that the Morse for `FORCES E E E E E` ends with **five** dits,
not four. **Treat every dit-run count as [uncertain].**
([rumkin K0](https://rumkin.com/reference/kryptos/k0/),
[Wikipedia](https://en.wikipedia.org/wiki/Kryptos),
[LEMMiNO](https://www.lemmi.no/p/the-unbreakable-kryptos-code))

**Physical order is also [uncertain], and the two published orders are near-reverses of each other:**

| Wikipedia's list order | rumkin's stated physical order |
|---|---|
| VIRTUALLY INVISIBLE | SOS |
| DIGETAL INTERPRETATIT | RQ / YR |
| SHADOW FORCES | LUCID MEMORY |
| LUCID MEMORY | SHADOW FORCES |
| T IS YOUR POSITION | WHAT IS YOUR POSITION |
| SOS | DIGITAL INTERPRETATION |
| RQ | VIRTUALLY INVISIBLE |

Reverse either column and you nearly get the other. That is exactly the signature of **two
transcribers walking the same slabs in opposite directions**, which is the most economical explanation
and leaves the true order undetermined from published sources alone. Sanborn told attendees in 2005
that the Morse was meant to "continue under the rock" and "extend into the rock, and all the way down
between each layer of stone", with one observer suspecting this was something he **planned to do
before running out of time** — **[uncertain]**, relayed via [LEMMiNO](https://www.lemmi.no/p/the-unbreakable-kryptos-code).

### 5.3 Three "deliberate misspellings" that are spacing or a single dit

This is the part of the Morse record that the arithmetic actually settles. All three checks are in
`analysis/berlin_clock_doc_checks.py` §1a–1c and print `True`.

1. **`DIGETAL` is exactly one dit short of `DIGITAL`.** `I` is `..`, `E` is `.`. Drop one dit from the
   fourth letter and DIGITAL becomes DIGETAL — 17 marks become 16, everything else identical. This is
   the same class of explanation as the PALIMPCEST slip behind K1's `IQLUSION` (see the README): a
   single-symbol error is a fully sufficient account of the "intentional" misspelling, and does not
   require intent.

2. **`INTERPRETATIT` and `INTERPRETATU` are the same marks.** The disputed tail is `I T` = `..` `-`
   versus `U` = `..-`. Identical dots and dashes; the **only** difference is the size of one gap in the
   copper. Verified: the full mark strings of INTERPRETATIT and INTERPRETATU are character-for-character
   identical (`..-.-..-..--..-..-.--..-`). So the long-standing disagreement between published
   transcriptions is **not a disagreement about what is carved** — it is a judgement call about one
   inter-letter space. (`INTERPRETATAU`, the third published variant, is genuinely different marks and
   can be set aside.)

3. **`RQ` and `YR` are the same marks read in opposite directions.** `RQ` = `.-.--.-`, `YR` = `-.--.-.`;
   each is the reverse of the other. Whoever reads the slab from the other end gets the other word.
   This also means the pair carries no information beyond "seven marks in this order".

Two more observations of the same kind, for completeness:

* **`SOS` is a Morse palindrome** (`...---...`) — it reads the same from either end, which is why it
  is the one message no reading-direction dispute touches.
* **Every run of filler dits is spacing-ambiguous.** 1 dit = `E`, 2 = `I`, 3 = `S`, 4 = `H`, 5 = the
  digit `5`. Whether the copper says `E E` or `I` is decided entirely by gap width. Any keyword or
  keystream extracted from the "filler" is therefore extracted from the transcriber's judgement, not
  from the sculpture. **This is a hard constraint on anyone trying to mine the Morse for key material.**

### 5.4 The compass rose and the lodestone

* One granite slab carries **an engraved compass rose pointing to a lodestone** — a naturally
  magnetised rock. ([Wikipedia](https://en.wikipedia.org/wiki/Kryptos); the CIA phrases it as the
  lodestone being "co-located with a navigational compass rose".)
* Elonka's aerial page, verbatim: *"This is a close up of the compass (also courtesy of Jim Gillogly)
  that's on one of the slabs."* … *"One report is that the 'north' direction on the compass rose is
  pointing roughly south-southwest (around 220 degrees) but this is not exact."* … *"The needle of the
  compass appears to be pointing towards another small stone nearby, which is probably a magnetized
  rock, or lodestone."*
  ([Elonka](https://elonka.com/kryptos/KryptosAerial.html))
* Note the internal inconsistency in that quotation: **220° is nearer south-west (225°) than
  south-south-west (202.5°)**, and the source itself says "this is not exact". Treat the engraved
  rose's orientation as **known only to within a sector** — **[uncertain]**.
* The widely repeated claim that the lodestone pulls a compass needle **west-south-west** appears only
  in secondary write-ups; I found no primary source and no measurement. **[uncertain]**. Another
  second-hand reading has the needle's south end pointing roughly 15–30° north of east
  ([scirealm](https://scirealm.org/Kryptos.html)) — which is a different claim again. There is no
  reliable published measurement of either the rose's engraved orientation or the lodestone's
  deflection.
* The motif is thematically continuous with K2, whose plaintext says the information was gathered
  using "the earths magnetic field", and with Sanborn's practice of making invisible forces visible.
  The point of the piece is arguably that **local reference frames disagree with true north** — which
  is a warning about bearings, not an instruction.

### 5.5 East-north-east, and the sculpture's orientation

* **ENE is exactly 67.5°.** On a 16-point rose each point is 360/16 = 22.5° wide and ENE is the third
  point clockwise from north: 3 × 22.5 = **67.5°**. Its sector runs **56.25° to 78.75°**.
* K4's confirmed plaintext at positions 22–34 is **EASTNORTHEAST** — i.e. the plaintext names that
  bearing. This is the single strongest reason to take bearings seriously at all in K4 work.
* **The sculpture's orientation.** Documented: the main screen stands in the **north-west corner of
  the New Headquarters Building courtyard**, outside the cafeteria, at **38.95227° N, 77.14573° W**;
  the ciphertext half is read from the courtyard and the Vigenère tableau half is **deliberately
  reversed so it can only be read from behind the sculpture**
  ([CIA](https://www.cia.gov/legacy/headquarters/kryptos-sculpture/),
  [Wikipedia](https://en.wikipedia.org/wiki/Kryptos)). **What is not documented anywhere I could find
  is a compass bearing for the face of the screen** — no published source gives the azimuth the
  copper faces. **[uncertain]**, and it should be treated as an open physical measurement, not an
  assumption. Given that K4 names a bearing and the entrance piece carries a compass rose, this is a
  genuine gap in the public record.

---

## 6. The K2 coordinates, and the true bearing to Berlin

### 6.1 The numbers

K2's plaintext ends:

> THIRTY EIGHT DEGREES FIFTY SEVEN MINUTES SIX POINT FIVE SECONDS NORTH
> SEVENTY SEVEN DEGREES EIGHT MINUTES FORTY FOUR SECONDS WEST X LAYER TWO

**38° 57′ 6.5″ N, 77° 8′ 44″ W** = **38.951806 N, 77.145556 W**.

Measured against the sculpture's own published position (38.95227 N, 77.14573 W), that point is
**54 metres away on a bearing of 163.7° (south-south-east)** — computed here, and in agreement with
Wikipedia's "approximately 174 feet (53 meters) southeast of the sculpture".

### 6.2 What is there

* **Datum matters.** Plotted on **NAD83/WGS84** the coordinates fall on "a plot of grass near the south
  edge of the courtyard"; plotted on the obsolete **NAD27** they fall on "the edge of a roof near the
  courtyard's southeast corner". The modern datum is the sensible assumption for a 1988–90 work and is
  the only one that lands somewhere you could bury something.
  ([LEMMiNO](https://www.lemmi.no/p/the-unbreakable-kryptos-code))
* **What was found there, in Sanborn's own words.** At the American Cryptogram Association convention,
  Norfolk VA, 23–25 August 2013, asked whether something was buried on CIA grounds, Sanborn said:

  > "Yes, there is something buried adjacent to Kryptos… The thing that was buried is a **bronze USGS
  > marker**. It was **half buried**. It had **little cross hairs on the top of it**."

  He added that it had been **removed** by around 2011, when he and his wife visited — "but it is
  important." Tier **B**, from an attendee's notes:
  [kryptosfan, "Kryptos Notes From the ACA Convention", 28 Oct 2013](https://kryptosfan.wordpress.com/2013/10/28/kryptos-notes-from-the-aca-convention/).
* **So the answer to "what do the coordinates point to" is: a US Geological Survey benchmark that no
  longer exists.** There is no public record of an excavation, and no CIA statement about the spot.
  Everything beyond the survey marker — buried plates, chambers, a second cipher — is community
  speculation. **[uncertain]** in the strongest sense.
* Sanborn's November 2025 clue 4 ties **K5** thematically to K2's "its buried out there somewhere"
  ([Scientific American](https://www.scientificamerican.com/article/cia-kryptos-puzzle-creator-releases-final-clues/)),
  which keeps the burial motif alive as *subject matter* without making it a location to dig at.

### 6.3 The bearing from the sculpture to Berlin — the real number

Asked directly: **is Berlin east-north-east of Kryptos?** Computed with the standard great-circle
formulae in `analysis/berlin_clock_doc_checks.py` §3, from 38.95227 N, 77.14573 W (identical to three
decimal places if you start from the K2 coordinates instead):

| destination | great-circle **initial** bearing | 16-point | great-circle **final** bearing | **rhumb-line** (constant) bearing | 16-point | distance |
|---|---|---|---|---|---|---|
| Weltzeituhr, Alexanderplatz | **44.420°** | **NE** | 116.549° | **77.797°** | **ENE** | 6,713.7 km |
| Mengenlehreuhr, Europa-Center | 44.460° | NE | 116.510° | 77.804° | ENE | 6,710.0 km |
| Brandenburg Gate | 44.437° | NE | 116.529° | 77.798° | ENE | 6,711.8 km |
| Berlin city centre | 44.424° | NE | 116.545° | 77.797° | ENE | 6,713.2 km |

**The number you asked for, stated plainly: the great-circle initial bearing from the Kryptos
sculpture to the Berlin World Clock is 44.42°. That is NORTH-EAST, not east-north-east. It misses
ENE (67.5°) by 23.08°, and it hits NE (45°) to within 0.58°.**

Two qualifications, both real and both quantified rather than hand-waved:

* **On a rhumb line the answer flips.** A constant-bearing course — what you get by drawing a straight
  line on a Mercator chart, or by walking a fixed compass bearing — reaches Berlin on **77.797°**.
  On a 16-point rose the ENE sector is 56.25°–78.75°, so 77.797° falls **inside the ENE sector, with
  0.95° to spare**. On a 32-point rose it is not ENE but **east-by-north** (EbN, sector
  73.125°–84.375°). So "Berlin is east-north-east of Langley" is **true for a rhumb line on a
  16-point rose and false for a great circle**, and the margin in the true case is under one degree.
* **The great-circle course sweeps through ENE anyway.** Its forward azimuth rises monotonically from
  **44.42° at departure** through **73.24° at the midpoint** to **116.55° on arrival**, crossing
  exactly **67.5°** about **42.9% of the way along, at 53.915° N 45.873° W** in the North Atlantic
  south-east of Newfoundland. A single "bearing to Berlin" is not a well-defined quantity on a sphere,
  which is exactly why the great-circle and rhumb answers differ by 33°.

**Do not build anything on this.** The rhumb coincidence is one degree wide, it depends on choosing
the 16-point rose over the 32-point rose, and the plaintext phrase EASTNORTHEAST sits at positions
22–34 while BERLINCLOCK sits at 64–74 — thirty letters and, on any natural reading, a different clause
apart. The honest summary is the table: **great circle 44.4° (NE), rhumb 77.8° (ENE), 6,714 km.**

### 6.4 One more bearing, for the record

For completeness, since Sanborn's 2025 clue 1 also names a **1986 trip to Egypt**: the great-circle
initial bearing from the sculpture to the Valley of the Kings is **58.03°** (9,776 km) and to Giza
**55.78°** (9,351 km) — both between NE and ENE, both closer to ENE than Berlin is, and neither within
a 16-point sector of 67.5°. Recorded so nobody has to recompute it; it is not evidence of anything.

---

## 7. Bottom line

* **The Mengenlehreuhr is fully documented above, and is the wrong clock.** Sanborn said so on
  **12 November 2025**. The right clock is the **Urania-Weltzeituhr at Alexanderplatz**, which has no
  state machine to derive a keystream from — it has 24 numerals, 148 city names and a windrose
  underfoot.
* **He never disambiguated between 20 November 2014 and 12 November 2025** — eleven years. The
  Mengenlehreuhr identification came from the *New York Times*' own gloss on "that particular clock",
  not from the artist.
* **The keystream hypothesis is dead at this level of generality.** 176 generated streams (163 of them
  Mengenlehreuhr), 194 candidate streams in the harness, **48,697,953 alignments**, best joint fit
  **8 of 24 crib letters** against a chance expectation of **0.92** per alignment and **31 such maxima
  expected** from that many random draws. Zero survivors, and the null says no false positive was ever
  possible. Gronsfeld is not merely unsupported but **arithmetically impossible**: 11–15 of the 24
  required shifts exceed 9.
* **The Morse record is less solid than it is usually presented.** Physical order is undetermined (the
  two published orders are near-reverses). Dit-run counts disagree between sources. And three of the
  famous "deliberate misspellings" dissolve under the Morse table: **DIGETAL is one dit from DIGITAL**,
  **INTERPRETATIT and INTERPRETATU are literally the same marks**, and **RQ and YR are the same marks
  read backwards**. Two messages are genuinely truncated — the DIGITAL INTERPRETATI… plate runs off
  mid-word, and "[WHA]T IS YOUR POSITION" is cut at the left by the granite and the lodestone.
* **The K2 coordinates point 54 m south-south-east of the sculpture, to a spot where a half-buried
  bronze USGS benchmark with crosshairs used to be.** Sanborn confirmed the marker in 2013 and said it
  had already been removed.
* **Berlin is north-east of Langley on a great circle (44.42°), east-north-east on a rhumb line
  (77.80°), 6,714 km away.** The ENE reading is true only on a 16-point rose and only by 0.95°.
