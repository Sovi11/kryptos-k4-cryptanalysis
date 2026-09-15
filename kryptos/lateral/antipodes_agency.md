# Antipodes, the Cyrillic Projector, and the agency/archival record

Compiled 2026-09-13. Verification code: `/Users/pravarkataria/Desktop/crypto/kryptos/analysis/antipodes_agency_verify.py`.
Raw output: `/Users/pravarkataria/Desktop/crypto/kryptos/lateral/antipodes_agency_verify_out.txt`.

This is a documentation deliverable. It contains **no K4 attack** and proposes no K4 solution. Three
things in it are new results rather than compilation, and all three are reproducible from the script:

1. **The Antipodes Latin side differs from the Kryptos left panel by exactly ONE letter**, carved
   twice (once in each repetition of K2), and that one letter is *exactly* the change that turns
   `UNDERGRUUND` into `UNDERGROUND`. Verified by re-encryption. Everything else — all 97 letters of
   K4, twice, included — is character-for-character identical.
2. **The Cyrillic Projector / Antipodes-Cyrillic cipher is fully recovered**: ACA **Quagmire II** over
   a 32-letter Russian alphabet, keyed alphabet from **ТЕНЬ** ("shadow") with **Ш** hand-moved next to
   **Х**, key **МЕДУЗА** (MEDUSA) — the clue word carved on the sculpture — with the key **restarting
   at the start of message 2**. Decrypt and encrypt round-trip at **1558/1558 characters, exact**.
3. **Antipodes' Latin tableau has no extra L.** It is a mathematically perfect 32×33 rotation table,
   zero anomalies. This is direct evidence against the Bauer/Link/Molle `HILL` reading of the Kryptos
   tableau anomaly (README §1.3).

Reliability tiers used throughout: **[V]** verified computationally in this repo; **[A]** primary or
first-party source read directly; **[B]** reliable secondary source; **[C]** single/weak source or
inference; **[✗]** widely repeated but contradicted by a better source.

---

# PART A — Sanborn's other cipher sculptures

## A.0 Every Sanborn work known to carry cipher text

From Elonka Dunin's "Complete List of All Works" (the most complete inventory ever assembled; read
from the Internet Archive because elonka.com now serves a bot challenge to automated fetchers) plus
the 2026 Smithsonian finding aid. **[A/B]**

| work | year | location | cipher content | status |
|---|---|---|---|---|
| **Kryptos** | commissioned 1988, dedicated 1990 | CIA New HQ, Langley VA | 865 letters + 4 `?` in 4 parts; KRYPTOS tableau on the reverse; Morse slabs outside | K1–K3 solved; **K4 unsolved** |
| **Untitled Kryptos Piece** (a.k.a. *Covert Balance*, *Secrets Past*, *Kryptos II*) | 1992, 6 ft | Gilbert Kinney → Hirshhorn → sold June 2001 to David Bohnett, CA | half Kryptos text, half Cyrillic/KGB | Cyrillic solved 2003 |
| **Encoded Cylinder** → **The Cyrillic Projector** | cylinder made 1990–93; installed 1997 | UNC Charlotte, between the Friday and Fretwell buildings | 1133 Cyrillic ciphertext characters + a Cyrillic ТЕНЬ tableau, light projected from within | **solved 2003** (§A.5) |
| **Antipodes** | 1997, 9 ft (240 × 190 × 66 cm) | Hirshhorn Museum and Sculpture Garden, Washington DC, acc. **98.22** | Latin face = Kryptos text (1590 glyphs); Cyrillic face = Cyrillic Projector text **+ 425 further characters**; a 32×33 tableau on each face | Latin = Kryptos (so K4 still unsolved); **all Cyrillic solved Sept 2003** |
| **Code Room** | 1990 and 1992 versions | gallery shows *Covert Obsolescence*, *Secrets Passed* | half-height illuminated Kryptos Vigenère cylinder (1990); bronze Cyrillic-Projector cylinder + petrified tree (1992) | same texts |
| **Covert Obsolescence** / **Covert Operations** / **Fragment** series | 1990–91 | Federal Reserve Board Art Gallery and gallery shows | pulped classified CIA documents with enciphered text in **English**, **Cyrillic** and **Arabic** | not publicly transcribed |
| **Archeotranscription** | 1992 | *Secrets Passed* | double-etched copper microfilm of KGB documents | not a cipher per se |
| **Kryptos Decoding Filter** | 1994 | *Filter Media* | aluminium/brass/copper/shadow, 51 × 17 in | decoding aid, not ciphertext |
| **Indian Run Park** | 1994–95 | US Federal Courthouse, Beltsville/Greenbelt MD | Iroquois text; bronze cylinder with **Onondaga** text | language, not cipher |
| **Ex Nexum** | 1997 | US Courthouse, Little Rock AR | waterjet Greek and Latin text | language, not cipher |
| **A Comma, A** | 2000s | Houston | multilingual cut text | language, not cipher |
| later cylinders — **Luminous** (Livermore, 2019–21), **Omnis** (Minneapolis, 2020–21), Santa Clara cylinder (2024), Denver Union Station (2013–17), Univ. of Rochester MAG (2016), *Obelisk* (Rockville, 2012) | | | projected/cut text in many scripts | no published cipher |

**Load-bearing point.** Only **three** objects carry a *cryptogram* in the strict sense: Kryptos, the
Cyrillic Projector, and Antipodes (plus the 1992 Untitled piece, which is Antipodes' smaller
predecessor). Two of those three carry the *same two* cryptograms. Sanborn has produced exactly
**two** independent cipher systems in his career, and we now have a complete specification of one of
them.

> Caveat **[C]**: the *Covert Obsolescence* / *Covert Operations* pulped-paper pieces are described in
> Sanborn's own catalogue as carrying "enciphered English text", "encoded text (Cyrillic)" and
> "encoded text (Arabic)". Nobody has published a transcription of any of them. They are the only
> genuinely un-mined Sanborn cipher material in existence. Whether any of it is a real cryptogram or
> decorative is unknown.

---

## A.1 Antipodes — physical and provenance facts **[A/B]**

* Two curved copper plates, letters **waterjet-cut** (not engraved) through the copper, bolted with
  steel bands to a **petrified tree that was burned before petrifaction**. One plate carries the
  Kryptos (Latin) text; the other carries Cyrillic.
* **Two versions exist and they are routinely confused.** Sanborn's own account, relayed by Dunin:
  a ~6 ft version was made in **1992** and bought by collector **Gilbert Kinney**, who displayed it on
  his terrace and later donated it to the Hirshhorn. The **Neuberger Museum of Art** commissioned a
  larger (9 ft) version for its 1997 Biennial; after that show Sanborn **traded the large version to
  the Hirshhorn in exchange for the small one**, and the 1992 piece was then sold through the
  **L.A. Louver** gallery to a California collector (**David Bohnett**, June 2001).
* The Hirshhorn object is therefore the **1997** large version: *Antipodes*, 1997, copper and
  petrified wood, 240 × 190 × 66 cm, "Partial Gift of Gilbert and Ann Kinney and Joseph H. Hirshhorn
  Purchase Fund, by Exchange, 1998 (**98.22**)", 38°53′16.65″N 77°1′21.22″W.
* Sanborn's own description of the piece (as *Covert Balance*): it "depicts two opposing encoded
  texts, one relating to C.I.A. covert operations and the other to K.G.B. operations." **[A]**
* Dunin's page went up **27 Aug 2003**; the ciphertext-difference note was added **20 Jun 2005**; the
  Cyrillic solution was posted **26 Sep 2003**.

## A.2 The Antipodes Latin side — full text and exact diff against Kryptos **[V]**

### Source and its limits

The only public full transcription of the Antipodes Latin face is on **John Wilson's page**,
`http://scirealm.org/Antipodes.html`. Dunin's own pages describe the differences but never published
a full Antipodes transcript. So:

* The **letter sequence** below is the datum, and it is confirmed self-consistently: it reconstructs
  to Kryptos with exactly two deviations, which is exactly the kind of result a corrupt transcription
  would not produce.
* The **row breaks** in that source vary from 32 to 37 characters and are almost certainly the HTML
  table's layout, **not** the sculpture's carved rows. Treat the row structure as **[C]**. This
  matters: nobody should build a geometry argument on Antipodes row widths.

### The segment ordering

Dunin, verbatim **[A]**: the Antipodes ciphertext "starts with part 3", continues through part 4, has
a space separator, restarts at part 1, runs 1-2-3-4, then does **not** have a space separator, and
continues with parts 1 and 2, truncating mid-part-2 at the bottom of the sculpture. Reconstructed and
confirmed **[V]**:

```
K3  K4  ␣  K1  K2  K3  K4  K1  K2(truncated)
```

Counts **[V]**: 1594 carved glyphs = 1583 letters + 7 `?` + 2 dots + 2 space glyphs. Untruncated the
sequence would be 1738; the carving stops 148 glyphs into the final K2.

### The diff — one letter, carved twice

Reconstructing `K3 K4 K1 K2 K3 K4 K1 K2` from the Kryptos left panel and diffing against the
Antipodes stream glyph by glyph over all 1590 letters-and-`?`:

```
letterwise diff over 1590 glyphs: 2 mismatches

index  612  (= K2 glyph offset 115, K2 LETTER 115 1-indexed)  Kryptos 'R' -> Antipodes 'E'
   Kryptos   ...UEENJTBJLBQC[R]TBJDFHRRYIZE...
   Antipodes ...UEENJTBJLBQC[E]TBJDFHRRYIZE...
index 1481  (the same position in the second K2)               Kryptos 'R' -> Antipodes 'E'
```

**Both K4 blocks are byte-identical to the Kryptos K4**, at stream offsets 337 and 1206:

```
K4 occurrences: 2 at [337, 1206]
  offset  337: identical to Kryptos K4: True
  offset 1206: identical to Kryptos K4: True
```

> **Consequence for K4 work.** Antipodes is a genuinely independent second carving of the K4
> ciphertext, made seven years later from the artist's own charts, and it agrees with the Kryptos
> carving in **all 97 characters**. The hope in README §1.6 — that diffing the two carvings might
> yield a transcription correction to K4 — is **closed**: there is nothing to correct.
> `OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR`
> is what Sanborn meant to carve.

### The non-letter marks

```
GAP at stream index 434: between the end of the FIRST K4 and the start of the FIRST K1
dot after index 727  (= K2 letter 231): ...GTEZ?FKZBS·FDQVGOGIPU...
dot after index 728  (= K2 letter 232): ...TEZ?FKZBSF·DQVGOGIPUF...
second K4/K1 junction at index 1303: ...GKUHUAUEKCAR|EMUFPHZLRFAX...  (no gap carved)
```

Dunin's reading of the dots **[A]**: they "correspond to the location of the plaintext initials
'WW'" — i.e. Antipodes punctuates `ONLY W.W.` where Kryptos writes `ONLYWW`. Confirmed **[V]**: the
Antipodes glyph run `...FKZBS.F.DQ...` decrypts (K2/ABSCISSA) to `...ONLYW.W.THIS...`. This is the
single clearest demonstration that Sanborn thinks of punctuation as riding *outside* the cipher — the
same convention as Kryptos's three K2 question marks. It is a small but real constraint on K4: if
Sanborn wanted punctuation in K4 he would have carved it, and he did not.

### The tableaux — and the missing extra L **[V]**

Both Antipodes faces carry a tableau. Each is **32 unlabelled rows × 33 columns**, i.e. 32 successive
rotations of the relevant keyed alphabet, 1056 letters:

```
Antipodes LATIN tableau  : rows 32, all width 33
   rows differing from an ideal 32x33 KRYPTOS rotation table: 0
Antipodes CYRILLIC tableau: rows 32, all width 33
   rows differing from an ideal 32x33 ТЕНЬ rotation table:   0
```

Kryptos's tableau, by contrast, is 26 **labelled** rows of 30 plus two header rows — and carries the
famous extra `L` at the end of row `N`, 867 letters where 866 are called for.

> **This matters for the Hill conjecture.** README §1.3 records Bauer, Link and Molle's argument
> (*Cryptologia* 40(6), 2016) that the extra L is deliberate, because it makes the tableau's rightmost
> column read `...HILL...` instead of `...HIJL...`. Two independent pieces of counter-evidence now
> stand together: Sanborn omitted the extra letter from the small *Kryptos* models he sold
> (Wikipedia **[B]**), and **he did not reproduce it on Antipodes** — where he re-cut the same keyed
> alphabet, in a different geometry, with zero anomalies **[V]**. The extra L looks like a
> fabrication slip. (This repo has separately ruled out Hill 2×2 and 3×3 outright — `findings/families.md`.)
> Caveat: the Antipodes tableau geometry is 32×33 and unlabelled, so the specific `HILL` column does
> not exist there to be reproduced; what is shown is that Sanborn's *second* cutting of this alphabet
> contains no deliberate letter anomaly at all.

Also worth recording: the tableau row that carries the extra L on Kryptos is the same row whose
letters are out of alignment, and **Roger Anderson of Florida** was the person who noticed the extra
L, on **8 October 2003** — every published Kryptos transcript before that date was wrong **[A]**.

## A.3 The one real difference: UNDERGROUND, not UNDERGRUUND **[V]**

John Wilson's page claims the Antipodes change encodes the *correctly spelled* `UNDERGROUND`. Tested
mechanically:

```
K2 plaintext position of 'UNDERGRUUND'     : 0-indexed 107
re-encrypt both spellings, Quagmire III / KRYPTOS alphabet / key ABSCISSA
  the two ciphertexts differ at EXACTLY ONE position: K2 letter 114 (0-indexed)
     UNDERGRUUND -> 'R'        UNDERGROUND -> 'E'
  Kryptos carves  ...BJLBQC[R]TBJDFH...   == the UNDERGRUUND prediction   (True)
  Antipodes carves ...BJLBQC[E]TBJDFH...  == the UNDERGROUND prediction   (True)
```

So the *entire* difference between the two sculptures' Latin ciphertexts, across 1590 glyphs and two
full repetitions of K1–K4, is that Antipodes silently fixes one of Kryptos's three celebrated
"deliberate" misspellings. Carved twice, consistently, so it is not a slip of the waterjet.

**What this is worth, and what it is not.**

* It is a clean demonstration that **Sanborn re-ran his own encryption** to produce Antipodes rather
  than copying the Kryptos artwork — you cannot make a single-letter change like this by tracing.
  He still had working charts and a working procedure in 1997.
* It is **direct evidence that at least one "intentional misspelling" was not intentional**, or at
  least that Sanborn did not regard it as load-bearing enough to preserve. README §2.2 already records
  the arithmetic by which `IQLUSION` is fully explained as a `PALIMPCEST` keyword slip. `UNDERGRUUND`
  now joins it as a misspelling Sanborn himself corrected when given a second chance.
  `DESPARATLY` (K3) is untouched — but K3 is a transposition, so correcting it would have required
  re-transposing 336 letters.
* It is **not** a K4 clue. The change is inside K2, it is explained entirely by the spelling, and K4
  is untouched.

> Note **[C]**: Wilson further observes that the changed ciphertext run `BQCETB` anagrams to `CBET`
> (Russian *свет*, "light"), pairing with the Cyrillic keyword ТЕНЬ ("shadow") and the title
> *Antipodes*. That is a charming observation about a 4-letter string in a 1590-character text and
> should be treated as coincidence unless someone can quantify it. It is recorded here so nobody
> spends time rediscovering it.

## A.4 The Antipodes Cyrillic side

The Cyrillic face carries the **entire** Cyrillic Projector ciphertext as a prefix, then continues
**[V]**:

```
Cyrillic Projector ciphertext : 1133 characters
Antipodes Cyrillic ciphertext : 1558 characters
CP ciphertext is an exact prefix of the Antipodes ciphertext: True
```

425 further characters — Dunin's contemporaneous estimate of "an additional 20% of encrypted text" is
right (425/1133 = 37.5% more text, 27% of the total; her estimate was made before transcription).
The continuation is the rest of the same KGB report, and it is enciphered with the same key.

`lateral/keystreams/antipodes_cyrillic_extra_ciphertext.txt` and `..._extra_plaintext.txt` hold the
continuation on its own.

## A.5 The Cyrillic Projector — full recovery of method and key

### The object **[A/B]**

Hollow bronze cylinder, ~5 ft diameter, lit from within so the cut letters project onto the
surroundings. Made in the early 1990s as *Encoded Cylinder* for gallery shows; **purchased by UNC
Charlotte and installed in 1997**, between the Friday and Fretwell buildings
(35°18′22″N 80°43′46″W). Its museum label calls the two halves an encoded text and "Vigenere's
Tableaux… the decoding text" — the same tool-plus-cryptogram pairing as Kryptos.

### The solve — dates, names, order of events **[A]**

From Dunin's own dated timeline, which is the primary community record:

| date | event |
|---|---|
| **May 2003** | Randall Bollig photographs the sculpture at Dunin's suggestion |
| **13 Jun 2003** | Dunin publishes the first full transcript, from Bollig's photos |
| **18 Jun 2003** | independent transcripts from **Bill Houck** (VA) and **Brian Hill** (TX) are collated against hers; extra photos from **Susan Zimmerman** of UNC Charlotte settle disputed characters; ~a dozen corrections |
| **9 Jul 2003** | **Frank Corr**, a hobbyist in North Carolina working alone and *without* Dunin's transcript, derives a decryption technique producing Russian-looking output. He sends Dunin an anonymous letter claiming a solve, with too little detail to evaluate; she files it |
| **13 Sep 2003** | **Mike Bales** (Michigan) independently derives a decryption reaching Russian statistics; he also says nothing, having no translation |
| **18 Sep 2003** | Corr quietly posts an unmarked page with his decryption table and the first two Russian words, linking to Dunin's page |
| **19 Sep 2003** | Dunin spots the unusual referrer in her web logs, finds Corr's page, confirms the decryption with **Ferdinando Stehle**'s Excel Cyrillic-Vigenère sheet; **Gary Warzin** traces the URL to Corr's identity |
| **20 Sep 2003** | Dunin, with her father **Stanley Dunin** and **Anatoly K.** (an ex-Soviet engineer in New Mexico), produces the English translation. Bales steps forward and posts his decryption |
| **21 Sep 2003** | independent translations by **Dr. Richard Nelson** and **Alexander Slauk** (Cleveland) from Bales' text, and by **Olga L. Pechenaya** (St Louis) from Dunin's |
| **22 Sep 2003** | Slashdot announcement; thousands of visitors in hours |
| **23 Sep 2003** | **Dunin and Anatoly K. solve and translate the remaining Cyrillic on Antipodes. All Cyrillic on all Sanborn sculptures is now deciphered** |
| **Oct 2003** | *Science* covers it: "Cryptic Sculpture Cracked", vol. 302 p. 224, 10 Oct 2003 |

So: **Dunin did not break the cipher** — she built the transcript that made breaking it possible, ran
the group that noticed Corr's page, produced the first translation, and personally solved the
*Antipodes* continuation. Corr and Bales broke the cipher, independently, neither knowing of the
other. This is worth stating precisely because secondary sources routinely collapse it into "Elonka
Dunin solved the Cyrillic Projector."

### The cipher, exactly **[V]**

Everything below is forced from the ciphertext and plaintext and then round-trip verified.

**Alphabets.** 32 letters — the standard Russian alphabet with **Ё omitted** (Dunin flagged the
missing Ё in June 2003; her Ukrainian correspondent explained it is the rarely-written umlaut-E).

```
plaintext alphabet  A : А Б В Г Д Е Ж З И Й К Л М Н О П Р С Т У Ф Х Ц Ч Ш Щ Ъ Ы Ь Э Ю Я   (straight)
cipher/key alphabet B : Т Е Н Ь А Б В Г Д Ж З И Й К Л М О П Р С У Ф Х Ш Ц Ч Щ Ъ Ы Э Ю Я   (keyed)
```

`B` is the straight alphabet mixed by the keyword **ТЕНЬ** ("shadow"/"shade") — *but not only that*.
Verified **[V]**:

```
straight alphabet minus ТЕНЬ : А Б В Г Д Ж З И Й К Л М О П Р С У Ф Х Ц Ч Ш Щ Ъ Ы Э Ю Я
carved keyed alphabet tail   : А Б В Г Д Ж З И Й К Л М О П Р С У Ф Х Ш Ц Ч Щ Ъ Ы Э Ю Я
identical: False
```

**Ш has been lifted out of its normal slot (between Ч and Щ) and parked immediately after Х.** This is
a deliberate, undocumented, hand-made deviation from the textbook keyword-mixing rule — one letter,
moved, for no cryptographic reason. (Wilson's guess is that Ш and Х look like Latin W and X; the
motive is **[C]**, the fact is **[V]**.)

**The key.** The published second keyword is **ЙБАСГТ**. It is not a word. Verified **[V]**:

```
МЕДУЗА (MEDUSA) indices in the STRAIGHT alphabet : [12, 5, 4, 19, 7, 0]
letters at those indices in the KEYED alphabet   :  Й  Б  А  С  Г  Т   == ЙБАСГТ
shifts from ЙБАСГТ read in the KEYED alphabet    : [12, 5, 4, 19, 7, 0]   — identical
```

**The operative key is МЕДУЗА — MEDUSA — the clue word Sanborn carved into the ciphertext in Latin
letters**, at a point about two-thirds of the way down the top panel. (Dunin flagged it in 2003 as an
anomaly, because Cyrillic has no D, U or S glyphs; the Latin `MEDUSA` sits inline in the cut text.)
`ЙБАСГТ` is simply MEDUSA rewritten through the cipher's own alphabet, so the two are the same key.
**Sanborn carved the key into the cryptogram.**

**The rule.**

```
C[i] = B[ ( index_A(P[i]) + index_B(key[j]) ) mod 32 ],   j = (i - segment_start) mod 6
```

Under plaintext `А` (index 0) the ciphertext *is* the key letter, which is precisely the ACA
definition of **Quagmire II** with indicator A: straight plaintext alphabet, keyed ciphertext
alphabet. (Kryptos K1/K2 are **Quagmire III** — the *same* keyed alphabet on both sides.)

**The key restarts between messages.** Verified **[V]**:

```
best combo over all 12 family/alphabet pairings, published key, no restart:
   vigenere pt=straight ct=keyed key-alpha=keyed : 777/1558 = 49.9%  (chance 3.1%)
matches exactly for the first 777 characters, then breaks
   plaintext around the break: ...ТИМЕЖЛИЧНОСТНЫХОТНОШЕНИЙ | ОБИЗГОТОВЛЕНИИСАХАРОВЫМО...
   tail with key phase +0: 781/781   <== the key RESTARTS at 777
full round trip with the restart:
   decrypt(ciphertext) == plaintext : True   (1558/1558)
   encrypt(plaintext)  == ciphertext: True
```

777 is exactly the boundary between message 1 (the tradecraft text) and message 2 (the KGB report on
Sakharov). So: **one key, applied per message, restarting at each message boundary.**

Wilson's page records the technique as "Alt-LU" (alternate-alphabet lookup) with "ШЩ paired" — an
artefact of his own decoder's UI, not of the cipher. The clean statement is the Quagmire II one above.

### Plaintexts and their sources **[A/B]**

* **Message 1 (777 characters)** — a Russian tradecraft passage on developing and controlling human
  sources: the highest art of secret intelligence is the ability to develop a source you can wholly
  direct and control; a controlled source gives the most reliable information; a controlled source is
  one bought or otherwise made dependent; the professional's traditional aim is to entangle any
  potentially valuable source in a psychological net and draw it tight at the right moment; officers
  who do this well get promotion and colleagues' respect, **however** the methods required run
  fundamentally counter to the ethics and morals of society in interpersonal relations. Opens
  `ВЫСОЧАЙЪИМ ИСКУССТВОМ В ТАЙНОЙ РАЗВЕДКЕ …`.
* **Message 2 (781 characters on Antipodes; 354 on the Projector, where it is cut off)** — a **1982
  KGB memorandum** on Andrei Sakharov's appeal to the Pugwash Conference and its use by Americans for
  anti-Soviet purposes, signed by KGB Chairman **V. Fedorchuk**. Opens
  `ОБ ИЗГОТОВЛЕНИИ САХАРОВЫМ ОЧЕРЕДНОГО АНТЮСОВЕТСКОГО "ОБРАЩЕНИЯ" К ЗАПАДУ …`.
* Dunin found a KGB document in the Sanborn files of the **Nancy Drysdale gallery** while researching,
  and **David Wilson** pointed the group at an online collection of KGB Sakharov documents; those
  were the leads to the source text.
* **The plaintext contains Sanborn's own typos**: ~21 wrong letters in message 1 and ~4 in message 2
  on the Projector, ~6 in the Antipodes continuation, per Bales' corrections. E.g. `ВЫСОЧАЙЪИМ` for
  `ВЫСОЧАЙШИМ`, `ПОЭТОСУ` for `ПОЭТОМУ`, `ЗАВИТИМОСТИ` for `ЗАВИСИМОСТИ`, `ОДНАКЛ` for `ОДНАКО`,
  `АНТЮСОВЕТСКОГО` for `АНТИСОВЕТСКОГО`.

> **This is the single most useful behavioural fact in this whole document.** Sanborn's non-Kryptos
> cryptogram has roughly **25 accidental single-letter errors in 1558 characters — a ~1.6% error
> rate**, produced by hand-enciphering from charts. Kryptos itself carries a **known** error of the
> same species (the omitted `S` in K2, confirmed by Sanborn on 19 Apr 2006). It is therefore
> statistically *likely*, not merely possible, that **K4's 97 characters contain one or more carving
> or encipherment errors**. At 1.6% the expected count over 97 characters is ~1.5. Any K4 attack that
> demands a perfect 97/97 fit may be demanding more than the artefact can deliver.

## A.6 What this says about how Sanborn reuses a system — the K4 inference

Put the two systems side by side:

| | **Kryptos K1/K2 (1988–90)** | **Cyrillic Projector / Antipodes (1990–97)** |
|---|---|---|
| family | **Quagmire III** | **Quagmire II** |
| alphabet size | 26 | 32 (Russian minus Ё) |
| mixed alphabet | KRYPTOS-keyed, textbook mixing | ТЕНЬ-keyed, **plus one letter hand-moved** |
| key | PALIMPSEST (10), ABSCISSA (8) | МЕДУЗА (6) |
| key source | thematic English words | thematic Russian word, **carved into the cryptogram in Latin letters** |
| key handling | restarts at each message (K1, K2) | restarts at each message (msg 1, msg 2) |
| tableau supplied | yes, on the reverse face | yes, on the same cylinder / same face-pair |
| plaintext errors | ≥1 confirmed (K2 dropped S) + 3 "deliberate" misspellings, one of which he later fixed | ~25 |

**The conclusions that bear on K4:**

1. **When Sanborn reuses a system, he reuses the *genus* and varies the *parameters*.** Both are
   short-key, keyword-mixed, tableau-supplied, position-indexed polyalphabetics of the Quagmire type,
   differing in variant, alphabet size, and keyword. He did not invent a second mechanism for the
   Russian piece; he re-parameterised the first one.
2. **That genus is exhaustively dead for K4.** `findings/families.md` rules out Quagmire I–IV over
   periods 2–25 and 7.09M keyed-alphabet pairs, plus Porta, Gronsfeld, Trithemius and progressive
   keys. So K4 is **not** "the Kryptos system again with a different keyword", and it is **not** "the
   Cyrillic Projector system in Latin". This is now settled by construction rather than by assumption.
3. **Therefore K4 is the one place where Sanborn did something categorically different** — which is
   exactly what Scheidt said ("a change in the methodology", "I masked the English language") and what
   Sanborn said ("a whole different ballgame of multiple codes"). The Cyrillic evidence converts those
   statements from rhetoric into a measured contrast: we can now *see* what Sanborn's ordinary
   practice looks like, and K4 is not it.
4. **He hides keys in plain sight.** MEDUSA is carved in the cryptogram, in the wrong script, exactly
   where a solver will trip over it. KRYPTOS is carved on the sculpture. The tableau is supplied. On
   present evidence, Sanborn's instinct is to *give* you the key material and make the *technique* the
   hard part — precisely Scheidt's "solve the technique first and then go for the puzzle".
5. **He hand-modifies his alphabets.** The moved Ш is a one-letter, unmotivated, undocumented
   deviation from the textbook rule that would defeat any attack assuming a clean keyword-mixed
   alphabet, and that no amount of reasoning about ТЕНЬ would predict. If K4's system involves a
   mixed alphabet, the corresponding assumption in every sweep this repo has run — that mixed
   alphabets are generated by the standard keyword rule — may be the load-bearing wrong one.
   **This is the one genuinely actionable lead in this document.** It does not contradict any existing
   negative (the Quagmire sweeps covered 208,627 dictionary-generated alphabets plus arbitrary pairs,
   not arbitrary *perturbations* of them), and it is cheap to test: take each keyword-mixed alphabet
   and apply all 26×25 single-letter relocations. Left for whoever owns the families work; **not
   tested here**, because this is a documentation task.

## A.7 Keystreams already derived from these sculptures — tested, negative, do not re-test

`lateral/keystreams/` already contains, from earlier work in this repo:

```
cyrillic_projector_ciphertext_cyrillic.txt / _translit.txt / _ord26.txt / _ord32.csv
cyrillic_projector_plaintext_cyrillic.txt  / _translit.txt / _ord26.txt
antipodes_cyrillic_ciphertext.txt          / _translit.txt / _ord26.txt
antipodes_cyrillic_plaintext.txt           / _translit.txt
antipodes_cyrillic_extra_ciphertext.txt    / _translit.txt
antipodes_cyrillic_extra_plaintext.txt     / _translit.txt
cyrillic_keyed_alphabet.txt                / _translit.txt
```

These were part of the 194-stream lateral battery run on 2026-09-12 (`lateral/test_lateral.py`,
`test_lateral_numeric.py`): 16.5M block tests against the 24 crib-forced key blocks in 24
cipher/alphabet combinations × 26 rotations. **Best joint score 16/24 = chance; 0 hits within
threshold.** Do not re-run them.

Two defects in those files, found here and worth recording rather than silently fixing (they belong
to another agent's deliverable):

1. **`cyrillic_projector_plaintext_cyrillic.txt` has two wrong characters**, at 0-indexed 777 and 778:
   it stores `З`, `Я` where the ciphertext decrypts to `О`, `Б` (the start of `ОБ ИЗГОТОВЛЕНИИ…`).
   The Antipodes file has it right. Artefact of stitching two source pages. **[V]**
2. Both Cyrillic-Projector files have the inline Latin `MEDUSA` stripped from the carved stream. That
   happens to be harmless — 6 ≡ 0 (mod 6), so the key phase survives the excision — but it means the
   stored ciphertext is 1133 characters where the sculpture carries 1139 glyphs. **[V]**

---

# PART B — the official and archival record

## B.1 NSA, 1992–93: the first solve of K1–K3

**What happened [A/B].** At the 1992 Gold Bug Award ceremony, CIA Deputy Director **Admiral William
O. Studeman** — himself a former NSA Director — challenged NSA to break the sculpture in his own
agency's courtyard. NSA Director **Vice Admiral John M. "Mike" McConnell** announced the challenge
internally and a **four-person team** took it on. Named members: **Ken Miller** (coordinator) and
**Dennis McDaniels**; the other two are redacted in the released documents. Reporting elsewhere
attributes K1 to **Lance Estes** and K2 to **Ed Hannon**, and K3 to McDaniels — **[C]**, because the
released documents redact the names and I have not seen a primary source for that attribution.

They solved K1–K3 in **late 1992**. A progress memo went to CIA in **December 1992 or January 1993**
(Dunin's timeline **[A]**); the formal **"CIA Kryptos Sculpture – Challenge and Resolution Memo" is
dated 9 June 1993**. **None of this was public until March 2000.**

**The documents [A].** Eight documents sit on NSA's public declassification page,
`https://www.nsa.gov/news-features/declassified-documents/cia-kryptos-sculpture/`, plus mirrors on
`media.defense.gov`. Both hosts return **HTTP 403 to automated clients**, so the PDFs could not be
fetched here; the titles and the quoted technical content below come from NSA's own indexing and from
search-engine extracts of the PDFs, tier **[B]**.

| document | date |
|---|---|
| CIA Kryptos Sculpture — Challenge and Resolution Memo | 9 June 1993 |
| Kryptos Sculpture: Text of the Cryptogram | — |
| (U) The CIA KRYPTOS Sculpture (`KRYPTOS_Summary.pdf`) | — |
| The CIA KRYPTOS Sculpture: A Summary of Previous Work and New Revelations | — |
| The CIA KRYPTOS Sculpture Slides (`KRYPTOS_SLIDES.PDF`) | — |
| NSA Staff Processing Form to DDO; CIA Sculpture Study Group; doc_7, doc_8 … | — |

**Release history [A/B].** Elonka Dunin filed **FOIA #61191 in March 2010**, paid **$251.00** for a
professional/executive-level search, and received the material in **June 2013**. A further release was
processed for **Michael Ravnitzky in April 2014**. NSA then published the set on its own site.

**The technical content, and one thing in it that does not check out.** The NSA material states that
K1 and K2 are polyalphabetic substitution with **10 alphabets** and **8 alphabets** respectively —
exactly the lengths of PALIMPSEST (10) and ABSCISSA (8), so that is right and is independently
confirmed by this repo's re-encryptions. It further describes K3 as **"a route transposition on a
width of 86"** — and here README §2.5 flags an inconsistency, because 4 × 86 = 344 ≠ 336.

Resolved here, partly **[V]**:

* The "86" is **arithmetically exact once you allow an incomplete matrix.** David Stein's paper gives
  the formula `y = (336 − Bx + x)/B` with B = 4, and reports the correct solution as **(x = 8,
  y = 78)** — 8 columns of 3 letters and 78 columns of 4, total **86 columns, 336 letters**. The
  README's "[uncertain] — the description or the relay is imprecise" can be narrowed: the arithmetic
  is fine.
* But the transposition is **not** a plain keyed columnar transposition on 86 columns. Tested **[V]**:
  the K3 ciphertext cannot be partitioned into the plaintext's 86 columns in *either* orientation, and
  a sweep of every width 2–119 finds **no** width at which such a tiling exists. A further sweep of 8
  simple single-pass routes (columns L→R, R→L, up, down, boustrophedon both ways, reversed rows,
  diagonals) at **every width 2–179** finds **zero** matches in either direction; at width 86 the best
  agreement is 32/336, i.e. chance.
* So: **K3 is genuinely two-stage**, as this repo verified (rows of 24 → columns right-to-left → rows
  of 8 → columns right-to-left, and five other width pairs; no keyword needed). The "width 86" phrase
  describes a route more complex than a column read-out — or an intermediate stage. Anyone citing the
  NSA description as a *procedure* is over-reading it.

## B.2 CIA: David Stein, 1998 — the first solve by a human being with a pencil

**[A/B]** **David D. Stein**, a CIA physicist and technical analyst, solved K1–K3 **by hand, using
nothing but pencil and paper**, over roughly **400 hours spread across seven years**. He broke **K2
first, on 21 February 1998**, then K3 and K1 within days. He briefed roughly **250 CIA staff in an
auditorium at Langley on 26 March 1998** — Ed Scheidt was in the audience.

His write-up, **"The Puzzle at CIA Headquarters: Cracking the Courtyard Crypto"**, appeared in
***Studies in Intelligence***, the CIA's internal quarterly, in early **1999**. It was classified and
circulated only inside the intelligence community; a November 1998 note said publicly only that a CIA
analyst had solved "the lion's share". After Gillogly's public solve in June 1999 the CIA confirmed
Stein's priority (July 1999).

**Where to find it.** A redacted version sits in the **CIA FOIA Electronic Reading Room**
(`https://www.cia.gov/readingroom/`); the Kryptos-related reading-room items surfaced by search carry
document numbers **C06498615** (released 20 Jul 2017, 7 pp.) and **C06712772** **[C]** — the reading
room serves an SPA shell to automated clients and the document numbers could not be confirmed
against the live records here. The readable text is mirrored at
`https://www.elonka.com/kryptos/mirrors/daw/steinarticle.html` **[A]**.

**What Stein said about K4, verbatim [A]:**

> "And what about Part V of the puzzle? I haven't spent much time on this portion … but there are
> interesting patterns in here as well."

He adds that it is "more difficult than the previous pieces" but that he is "confident that it is not
impossible". (Stein numbers the sections I–V, counting the tableau; his "Part V" is our K4.) That is
the earliest recorded professional opinion on K4 and it is worth noting how little it contains: the
man who broke the other three by hand spent almost no time on it and offered no diagnosis.

## B.3 Jim Gillogly, 1999 — the first public solve

**[A/B]** **Jim Gillogly**, a computer scientist in southern California and a past president of the
American Cryptogram Association, announced K1–K3 on **8 June 1999** in a post to the Usenet group
**sci.crypt**, answering someone's "Has anyone deciphered it yet?". He worked from **Doug Gwyn's**
transcript — Gwyn had computerised **PHOENIX**'s partial ACA transcript (*The Cryptogram*,
March/April 1992) on **7 March 1992** and posted a corrected version on **1 September 1992** after
checking it against video supplied by Harry Carter. Gillogly used custom software on a Linux machine
with a **Pentium II 400 MHz**, over **four evenings**.

When he telephoned CIA's Office of Public Affairs he was told that Stein and an anonymous NSA group
had got there first. Gillogly's photographs of the panels (`http://www.voynich.net/Kryptos/`) remain
the reference for settling transcription disputes.

## B.4 Elonka Dunin's archive and the Kryptos Group

**[A/B]**

* **`https://www.elonka.com/kryptos/`** is the community's archive of record: the transcript, FAQ,
  the dated timeline used throughout Part A, the clue history, her October 2002 rubbings (taken on a
  visit to brief CIA on al-Qaeda codes), the Sanborn works list, photographs, and mirrors of the NSA
  FOIA release. **Operational note for this project:** the site now sits behind a bot challenge and
  returns a captcha redirect to `curl`; `WebFetch` reaches some pages and not others. The Internet
  Archive (`https://web.archive.org/web/<timestamp>id_/<url>`, fetched with `curl`) works reliably and
  is how the timeline, works list, Cyrillic transcript and Antipodes page were read for this document.
* **The discussion group** began as a Yahoo Group co-moderated by Dunin and **Chris "Xenon" Hanson**.
  Yahoo Groups shut down on 15 December 2020; the group **migrated to Groups.io in January 2020** and
  lives at `kryptos+subscribe@groups.io`. The old wiki at **`http://kryptos.yak.net/`** is still up.
  This is where Sanborn posted the April 2006 K2 correction.
* Dunin is co-author (with Klaus Schmeh) of *Codebreaking: A Practical Guide* and remains the de facto
  historian of the problem. Her site's last dated news item is **August 2025** (Sanborn's auction
  announcement).

**Two corrections to this repo from her timeline [A]:**

1. README §2.4 credits the 2005 `LAYERTWO` observation to "**Nicole** Friedrich, a logician in
   Vancouver". Dunin's contemporaneous timeline entry, dated **11 October 2005**, names
   "**Monet** Friedrich, a member of the Kryptos Group", who noticed that using the key `BSCISSAA`
   instead of `ABSCISSA` yields `PLAYERTWO` at the end of K2; **Paul Kiesel, Mark Siegal** and
   **Thorne Kontos** then argued the reading should be `LAYER TWO`. Wikipedia and most secondary
   sources say Nicole. **Flagged as a genuine name discrepancy; Dunin's timeline is the earlier and
   closer source.**
2. README §1.3 does not say who found the tableau's extra L. It was **Roger Anderson of Florida**, on
   **8 October 2003**.

## B.5 The Smithsonian Archives of American Art, and the 2025 "50-year seal"

**The recovery [A/B].** Writers **Jarett Kobek** and **Richard Byrne** noticed that the RR Auction
listing referred to Sanborn's original coding charts being held at the **Smithsonian's Archives of
American Art**. They requested access, photographed the papers, found taped-together scraps of
scrambled sentence fragments, and — combining those with Sanborn's four public cribs — reconstructed
the K4 plaintext. They e-mailed Sanborn with it on **3 September 2025**. Sanborn confirmed it was
correct. Kobek: **"There's no way on earth that this is a cryptographic solve."** Sanborn has said he
included the scraps by accident while assembling the donation during cancer treatment.

Sanborn then asked them to sign NDAs; they **refused**, but agreed not to publish, and have not.
Kobek and Byrne say the auction house's lawyers threatened them with copyright infringement and
tortious interference **[B — this appears in press coverage, not in any document I could verify]**.

**The seal, and what the public record actually says.** Press coverage (and Wikipedia) reports that
Sanborn asked the Smithsonian to **seal the relevant files for 50 years, until 2075**, and that the
Smithsonian complied. **This is not visible in the finding aid.** Verified directly against the
official EAD PDF, `https://sirismm.si.edu/EADpdfs/AAA.sanbojim.pdf`:

* Finding aid: *A Finding Aid to the Jim Sanborn papers, circa 1945–2024*, by **Ricky Gomez**,
  **2024 February 12; revised 2026 May 6**. Collection ID **AAA.sanbojim**, **16.1 linear feet**.
* **Acquisition Information:** "Donated in **2023 and 2026** by Jim Sanborn."
* **Restrictions**, quoted in full: *"This collection is open for research. Access to original papers
  requires an appointment and is limited to the Archives' Washington, D.C. Research Center.
  Researchers interested in accessing audiovisual recordings and born-digital records in this
  collection must use access copies."*
* **There is no mention anywhere in the 26-page finding aid of a seal, a closure, a restricted series
  or box, or the year 2075.** The words "sealed", "closed" and "2075" do not appear.

The Kryptos-relevant containers are listed openly under Series 3 (Commission Files), "Kryptos" CIA
Headquarters:

```
Box  6, Folder 10  Pre-Production and Notes, 1990-1999
Box  6, Folder 11  Codes Research, circa 1980s-circa 2002
Box  6, Folder 13-17  Correspondence, Attempts at Deciphering Codes, 1988-2015
Box  6, Folder 18  Cracked Codes and Charts, 1990-circa 2013
Box  6, Folder 19  Cracked Codes and Charts, circa 1999-2010
Box 18, Folder 19  Russian Charts, undated            <-- 2026 addition
```

**How to read this honestly.** Four readings are consistent with the evidence and I cannot choose
between them: (a) the seal exists as a donor agreement but was never written into the public finding
aid; (b) the specific scraps were physically withdrawn from the collection and the folder descriptions
that remain are innocuous; (c) the restriction is administered at the reference desk rather than in
the EAD; (d) the press over-read what Sanborn requested. What can be stated flatly is: **as of the
2026-05-06 revision, the Archives of American Art publicly describes the Jim Sanborn papers as open
for research, and lists "Cracked Codes and Charts" and "Russian Charts" as available folders.** Anyone
repeating "sealed until 2075" as a fact should know that the finding aid does not say so.

**`Box 18, Folder 19 — "Russian Charts, undated"`**, part of the 2026 addition, is almost certainly
the Cyrillic Projector / Antipodes coding material, and is the only physical Sanborn cipher-chart
holding this project knows of that is described as open.

## B.6 RR Auction, November 2025

**[A]** Auction: **"Decoding History: Kryptos K4 & K5, Enigma, and the Rosetta Stone" (#730)**, RR
Auction, Boston. Opened **16 October 2025**, closed **20 November 2025** — Sanborn's 80th birthday.
Lot **2001**, *"The Complete Secrets of Kryptos: Jim Sanborn's Private Archive"*. Estimate
**$300,000+** (press reported a $300,000–$500,000 range). Sold for **$962,500** including buyer's
premium, to an anonymous bidder. Bobby Livingston, RR's EVP: "one of the most significant transfers of
cryptographic knowledge in auction history."

The 17 listed components:

1. Original handwritten K4 plaintext, with a signed letter from **Ed Scheidt**
2. **The original coding system for K4**
3. Handwritten, signed Kryptos plaintexts used for screen cutting, K4 (2 pieces)
4. Original coding charts for K1, K2, K3
5. Unpublished **1988 alternate K1 plaintext** and coding chart
6. Unpublished **1988 alternate K4 plaintext, now designated K5**
7. The original **scrambled texts shown to the Department of Historical Intelligence**
8. A private afternoon session with Sanborn
9. Sanborn's US Government "Escort Required" badge
10. Colour photograph of the original 1988 model
11. A 3/8″ curved copper proof-of-concept plate, 12″ × 24″, signed "J.S.1988"
12. Studio photograph of the copper plate during cutting
13. Signed b/w photograph of Sanborn with the plate, 1990
14. Original signed GSA contract
15. Original dedication-ceremony speeches
16. Original CIA photograph of **William Webster receiving the code**
17. Original signed dedication pamphlet

Two items deserve emphasis for this project. **Item 6** confirms that K5 is not a later invention but
an *alternate 1988 K4 plaintext* — the same message slot, a different text, which is why K4 and K5 are
both 97 characters and "share some of the same coded words in the same positions". **Item 7** is the
scrambled-fragment material of the same species Kobek and Byrne found at the Smithsonian, which tells
you Sanborn's working method involved physically cut-up text.

RR's own conditions noted that the materials remained in Sanborn's possession and were not
independently verified, and conceded that the K4 plaintext might become public through independent
research — "only the winning bidder will possess Sanborn's explanation".

## B.7 Paradigm, June 2026: the verifier and the CTF

**[A]** On **12 June 2026** **Paradigm**, a crypto investment firm, identified itself as the buyer
(`https://paradigm.xyz/2026/06/kryptos`).

**The verifier, per Paradigm's own description:**

1. A dedicated, freshly set-up, isolated computer was provided for Sanborn to type the K4 plaintext.
2. The plaintext was hashed with **SHA-256**.
3. The hash was sent to **Google Cloud Key Management Service**, which returned an **HMAC** tag
   reproducible only by sending the same SHA-256 hash to the same cloud-held key.
4. "The plaintext never left the device, and we wiped the laptop afterward."

So the check is `HMAC_k(SHA256(candidate)) == stored_tag`, with `k` held in Cloud KMS and never
exported. Paradigm can therefore verify a submission without knowing the answer. **What this design
does not do** is bind the *method*: it accepts a plaintext string and nothing else, so it cannot
distinguish a cryptanalytic solve from a leak, and it is exactly as strong as the assumption that
nobody with the plaintext will publish. Note also that anyone holding the plaintext (Sanborn, Kobek,
Byrne, Paradigm) can produce a verifying submission at will.

**Submissions** cost **$1** via Stripe at `paradigm.xyz/kryptos/`, stated purpose: making brute-force
uneconomic. **This project does not submit** — it is a paid transaction and out of scope.

**The CTF.** Sponsor **Paradigm Operations LP**; rules at
`https://paradigm.xyz/kryptos-ctf/official-rules`. Started **Friday 12 June 2026**; runs until all ten
puzzles are solved or the sponsor closes it. **Ten** prize-bearing cryptography puzzles of increasing
difficulty, **$1,000 cash to the first solver of each**, **$10,000** total. Puzzles stay open until
solved. Global entry, minors need parental consent, sanctioned jurisdictions excluded (Cuba, Iran,
North Korea, Russia, Syria, Donetsk, Luhansk, Crimea), sponsor employees and vendors ineligible.
**K4 is a separate, non-prize channel**: "No prize will be awarded for K4 unless Sponsor expressly
states otherwise," and the $1 fee is non-refundable.

**K5.** Paradigm holds the 97-character K5 ciphertext, says Sanborn "created [it] at the same time" as
K4, and plans to release it "in the future" with no date. **It is not public.** Paradigm's own pages
describe K4 as still unsolved. Headlines reading "Kryptos K4 solved by Paradigm" are wrong: Paradigm
bought a solution, it did not break a cipher.

## B.8 Net corrections this document makes to the repo

| where | was | now |
|---|---|---|
| README §1.6 | "I have not systematically diffed [Kryptos and Antipodes]; that is an open direction." | **Done.** Exactly one letter differs, twice; K4 is identical in both carvings. Direction closed. **[V]** |
| README §1.6 | Cyrillic Projector "1993 [uncertain on exact year]"; "Solved by Frank Corr (July 2003) and independently by Mike Bales (September 2003)" | Cylinder made c. 1990–93 as *Encoded Cylinder*, renamed and installed at UNC Charlotte 1997. Corr's technique dates to **9 Jul 2003** but was only found by the group on **19 Sep 2003**; Bales **13 Sep 2003**; translation **20 Sep 2003**; Antipodes Cyrillic **23 Sep 2003** by Dunin and Anatoly K. **[A]** |
| README §1.6 | Antipodes ordering "[uncertain]" | Confirmed: `K3 K4 ␣ K1 K2 K3 K4 K1 K2(trunc)` **[V]**, matching Dunin's description **[A]** |
| README §1.3 | extra L "[uncertain] whether intentional" | Additional counter-evidence: Antipodes' Latin tableau (32×33) is anomaly-free **[V]**. Discoverer of the L: Roger Anderson, 8 Oct 2003 **[A]** |
| README §2.4 | "Nicole Friedrich" | Dunin's timeline says **Monet Friedrich**, 11 Oct 2005. Discrepancy flagged **[A]** |
| README §2.5 | NSA "4 × 86 = 344 ≠ 336, so the description is imprecise [uncertain]" | The arithmetic is exact for an **incomplete** matrix: Stein's (x=8, y=78), 8×3 + 78×4 = 336, 86 columns. But no keyed columnar transposition at **any** width 2–119, and no simple single-pass route at **any** width 2–179, reproduces K3 **[V]** — so "route transposition on a width of 86" is not a procedure you can follow |
| §4 of README | "Sanborn asked the Smithsonian to seal the relevant files for 50 years, until 2075, and the Smithsonian complied" | The AAA finding aid revised **2026-05-06** says the collection is **"open for research"** and names no restriction, no closure and no 2075 date; "Cracked Codes and Charts" and "Russian Charts" are listed as available folders **[A]**. The seal is a press claim not reflected in the public record |
| new | — | Sanborn's measured hand-encipherment error rate on his other cryptogram is **~25 errors in 1558 characters ≈ 1.6%**, expected ~1.5 errors over 97 characters **[V]**. Demanding a perfect 97/97 fit may be demanding more than the artefact offers |
| new | — | Sanborn **hand-moved Ш** out of its keyword-mixed position in the Cyrillic alphabet, for no cryptographic reason **[V]**. Untested corollary for K4: perturbed keyword-mixed alphabets |

---

## Sources

Primary / first-party

* Elonka Dunin, *Antipodes* — `https://elonka.com/kryptos/sanborn/antipodes.html` (read via `https://web.archive.org/web/20100105153302id_/http://elonka.com/kryptos/sanborn/antipodes.html`)
* Elonka Dunin, *The Cyrillic Projector — Transcript* — `https://elonka.com/kryptos/cyrillic.html` (via Wayback)
* Elonka Dunin, *Cryptography Timeline — Kryptos, Antipodes, and the Cyrillic Projector* — `https://elonka.com/kryptos/KryptosTimeline.html` (via Wayback)
* Elonka Dunin, *Jim Sanborn — Complete List of All Works* — `https://elonka.com/kryptos/sanborn/list.html` (via Wayback)
* Elonka Dunin, *Kryptos Part 2 Was Wrong* — `https://elonka.com/kryptos/CorrectedK2Announcement.html`
* Elonka's Kryptos page — `https://www.elonka.com/kryptos/`; discussion group `kryptos+subscribe@groups.io`; wiki `http://kryptos.yak.net/`
* David D. Stein, "The Puzzle at CIA Headquarters: Cracking the Courtyard Crypto", *Studies in Intelligence*, 1999 — `https://www.elonka.com/kryptos/mirrors/daw/steinarticle.html`; CIA FOIA Reading Room `https://www.cia.gov/readingroom/`
* NSA declassified Kryptos documents — `https://www.nsa.gov/news-features/declassified-documents/cia-kryptos-sculpture/` (403 to automated clients); "Challenge and Resolution Memo, 9 June 1993" `https://www.nsa.gov/Helpful-Links/NSA-FOIA/Declassification-Transparency-Initiatives/FOIA-Reports-and-Releases/FOIA-Reports-and-Releases-List/igphoto/2002760459/`; slides `https://media.defense.gov/2021/Jul/12/2002760451/-1/-1/0/KRYPTOS_SLIDES.PDF`
* Smithsonian Archives of American Art, *A Finding Aid to the Jim Sanborn papers, circa 1945–2024* (Ricky Gomez, 2024-02-12; rev. 2026-05-06), AAA.sanbojim — `https://sirismm.si.edu/EADpdfs/AAA.sanbojim.pdf`; collection page `https://www.aaa.si.edu/collections/jim-sanborn-papers-22298`
* RR Auction lot 2001 — `https://www.rrauction.com/auctions/lot-detail/350761607302001-the-complete-secrets-of-kryptos-jim-sanborns-private-archive/`; result `https://content.rrauction.com/jim-sanborns-complete-kryptos-archive-sells-for-962500-at-auction/`; "discovered, not solved" `https://content.rrauction.com/kryptos-k4-discovered-not-solved-heres-what-actually-happened/`
* Paradigm — `https://paradigm.xyz/2026/06/kryptos`; CTF rules `https://paradigm.xyz/kryptos-ctf/official-rules`
* Jim Gillogly's photographs — `http://www.voynich.net/Kryptos/`; sci.crypt archive `https://groups.google.com/g/sci.crypt/`

Secondary

* John Wilson, *Antipodes: The Sanborn Sculpture at Hirshhorn Museum* — `http://scirealm.org/Antipodes.html` (the only public full Antipodes transcription)
* Wikipedia: *Antipodes (sculpture)* `https://en.wikipedia.org/wiki/Antipodes_(sculpture)`; *Cyrillic Projector* `https://en.wikipedia.org/wiki/Cyrillic_Projector`; *Kryptos* `https://en.wikipedia.org/wiki/Kryptos`; *Jim Sanborn* `https://en.wikipedia.org/wiki/Jim_Sanborn`
* "Cryptic Sculpture Cracked", *Science* 302, 224 (10 Oct 2003) — `https://www.science.org/content/article/cryptic-sculpture-cracked`
* Slashdot, 22 Sep 2003 — `https://it.slashdot.org/story/03/09/22/205244/cyrillic-projector-code-finally-cracked`
* Elonka Dunin, "Kryptos and the Cyrillic Projector Cipher", ShmooCon 2006 — `https://archive.org/details/2006-shmoocon-Dunin-Kryptos`; DEF CON 12 slides `https://www.defcon.org/images/defcon-12/dc-12-presentations/Dunin/dc-12-dunin.ppt`
* Intel Today, "KRYPTOS — History of the NSA Involvement" — `https://inteltoday.org/2020/11/06/kryptos-30-years-anniversary-history-of-the-nsa-involvement/`
* *Scientific American*, "How the CIA's Kryptos Sculpture Gave Up Its Final Secret" — `https://www.scientificamerican.com/article/how-the-cias-kryptos-sculpture-gave-up-its-final-secret/`
* Smithsonian art inventory, Antipodes — `https://siris-artinventories.si.edu/` (record 416281); GSA Fine Arts Collection, Sanborn — `https://art.gsa.gov/people/3001/jim-sanborn/`

---

# Appendix 1 — Antipodes, Latin (Kryptos) face: full transcription

Source: `http://scirealm.org/Antipodes.html`. **Row breaks are that page's layout, not
necessarily the sculpture's carved rows** (they run 32–37 characters); the letter sequence is the
datum. `.` = carved dot, `  ` = the carved separator gap. Reconstructs to
`K3 K4 ␣ K1 K2 K3 K4 K1 K2(trunc)` with exactly two deviations from the Kryptos left panel, both
the same `R`→`E` at K2 letter 115.

```
 1  ENDYAHROHNLSRHEOCPTEOIBIDYSHNAIACH
 2  TNREYULDSLLSLLNOHSNOSMRWXMNETPRNG
 3  ATIHNRARPESLNNELEBLPIIACAEWMTWNDITE
 4  ENRAHCTENEUDRETNHAEOETFOLSEDTIWENH
 5  AEIOYTEYQHEENCTAYCREIFTBRSPAMHHEWE
 6  NATAMATEGYEERLBTEEFOASFIOTUETUAEOT
 7  OARMAEERTNRTIBSEDDNIAAHTTMSTEWPIER
 8  OAGRIEWFEBAECTDDHILCEIHSITEGOEAOSDD
 9  RYDLORITRKLMLEHAGTDHARDPNEOHMGFMF
10  EUHEECDMRIPFEIMEHNLSSTTRTVDOHW?OBK
11  RUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTW
12  TQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZF
13  PKWGDKZXTJCDIGKUHUAUEKCAR  EMUFPHZL
14  RFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQV
15  YUVLLTREVJYQTMKYRDMFDVFPJUDEEHZWE
16  TZYVGWHKKQETGFQJNCEGGWHKK?DQMCPFQ
17  ZDQMMIAGPFXHQRLGTIMVMZJANQLVKQEDA
18  GDVFRPJUNGEUNAQZGZLECGYUXUEENJTBJL
19  BQCETBJDFHRRYIZETKZEMVDUFKSJHKFWHK
20  UWQLSZFTIHHDDDUVH?DWKBFUFPWNTDFIYC
21  UQZEREEVLDKFEZMOQQJLTTUGSYQPFEUNLA
22  VIDXFLGGTEZ?FKZBS.F.DQVGOGIPUFXHHDRKF
23  FHQNTGPUAECNUVPDJMQCLQUMUNEDFQELZ
24  ZVRRGKFFVOEEXBDMVPNFQXEZLGREDNQFM
25  PNZGLFLPMRJQYALMGNUVPDXVKPDQUMEBE
26  DMHDAFMJGZNUPLGEWJLLAETGENDYAHROH
27  NLSRHEOCPTEOIBIDYSHNAIACHTNREYULDSL
28  LSLLNOHSNOSMRWXMNETPRNGATIHNRARPE
29  SLNNELEBLPIIACAEWMTWNDITEENRAHCTEN
30  EUDRETNHAEOETFOLSEDTIWENHAEIOYTEYQ
31  HEENCTAYCREIFTBRSPAMHHEWENATAMATEG
32  YEERLBTEEFOASFIOTUETUAEOTOARMAEERT
33  NRTIBSEDDNIAAHTTMSTEWPIEROAGRIEWFEB
34  AECTDDHILCEIHSITEGOEAOSDDRYDLORITRKL
35  MLEHAGTDHARDPNEOHMGFMFEUHEECDMRIP
36  FEIMEHNLSSTTRTVDOHW?OBKRUOXOGHULBS
37  OLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZ
38  WATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJ
39  CDIGKUHUAUEKCAREMUFPHZLRFAXYUSDJKZ
40  LDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJY
41  QTMKYRDMFDVFPJUDEEHZWETZYVGWHKKQ
42  ETGFQJNCEGGWHKK?DQMCPFQZDQMMIAGPF
43  XHQRLGTIMVMZJANQLVKQEDAGDVFRPJUNG
44  EUNAQZGZLECGYUXUEENJTBJLBQCETBJDFH
45  RRYIZETKZEMVDUFKSJHKFWHKUWQLSZFTIH
46  HDDDUVH?DWKBFUFPWNTDFIYCUQZEREEVLD
47  KFEZMOQQJLTTUGSYQPFEUNLAVIDXFLGGTE
```

As one stream (1590 letters-and-`?`, dots and gap removed):

```
ENDYAHROHNLSRHEOCPTEOIBIDYSHNAIACHTNREYULDSLLSLLNOHSNOSMRWXMNETPRNGATIHNRARPESLN
NELEBLPIIACAEWMTWNDITEENRAHCTENEUDRETNHAEOETFOLSEDTIWENHAEIOYTEYQHEENCTAYCREIFTB
RSPAMHHEWENATAMATEGYEERLBTEEFOASFIOTUETUAEOTOARMAEERTNRTIBSEDDNIAAHTTMSTEWPIEROA
GRIEWFEBAECTDDHILCEIHSITEGOEAOSDDRYDLORITRKLMLEHAGTDHARDPNEOHMGFMFEUHEECDMRIPFEI
MEHNLSSTTRTVDOHW?OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFB
NYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAREMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVL
LTREVJYQTMKYRDMFDVFPJUDEEHZWETZYVGWHKKQETGFQJNCEGGWHKK?DQMCPFQZDQMMIAGPFXHQRLGTI
MVMZJANQLVKQEDAGDVFRPJUNGEUNAQZGZLECGYUXUEENJTBJLBQCETBJDFHRRYIZETKZEMVDUFKSJHKF
WHKUWQLSZFTIHHDDDUVH?DWKBFUFPWNTDFIYCUQZEREEVLDKFEZMOQQJLTTUGSYQPFEUNLAVIDXFLGGT
EZ?FKZBSFDQVGOGIPUFXHHDRKFFHQNTGPUAECNUVPDJMQCLQUMUNEDFQELZZVRRGKFFVOEEXBDMVPNFQ
XEZLGREDNQFMPNZGLFLPMRJQYALMGNUVPDXVKPDQUMEBEDMHDAFMJGZNUPLGEWJLLAETGENDYAHROHNL
SRHEOCPTEOIBIDYSHNAIACHTNREYULDSLLSLLNOHSNOSMRWXMNETPRNGATIHNRARPESLNNELEBLPIIAC
AEWMTWNDITEENRAHCTENEUDRETNHAEOETFOLSEDTIWENHAEIOYTEYQHEENCTAYCREIFTBRSPAMHHEWEN
ATAMATEGYEERLBTEEFOASFIOTUETUAEOTOARMAEERTNRTIBSEDDNIAAHTTMSTEWPIEROAGRIEWFEBAEC
TDDHILCEIHSITEGOEAOSDDRYDLORITRKLMLEHAGTDHARDPNEOHMGFMFEUHEECDMRIPFEIMEHNLSSTTRT
VDOHW?OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK
WGDKZXTJCDIGKUHUAUEKCAREMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMK
YRDMFDVFPJUDEEHZWETZYVGWHKKQETGFQJNCEGGWHKK?DQMCPFQZDQMMIAGPFXHQRLGTIMVMZJANQLVK
QEDAGDVFRPJUNGEUNAQZGZLECGYUXUEENJTBJLBQCETBJDFHRRYIZETKZEMVDUFKSJHKFWHKUWQLSZFT
IHHDDDUVH?DWKBFUFPWNTDFIYCUQZEREEVLDKFEZMOQQJLTTUGSYQPFEUNLAVIDXFLGGTE
```

Segment boundaries in that stream (0-indexed): K3 = 0–336, K4 = **337–433**, gap at 434,
K1 = 434–496, K2 = 497–868, K3 = 869–1205, K4 = **1206–1302**, K1 = 1303–1365, K2 = 1366–1589 (truncated).

# Appendix 2 — Antipodes tableaux

Both faces carry an **unlabelled 32 × 33** rotation table. Verified against ideal: **0 deviations**
on each. Kryptos's Latin tableau, by contrast, is 26 labelled rows of 30 plus two header rows and
carries the extra `L` on row `N`.

Latin face — 32 rotations of `KRYPTOSABCDEFGHIJLMNQUVWXZ`:

```
KRYPTOSABCDEFGHIJLMNQUVWXZKRYPTOS
RYPTOSABCDEFGHIJLMNQUVWXZKRYPTOSA
YPTOSABCDEFGHIJLMNQUVWXZKRYPTOSAB
PTOSABCDEFGHIJLMNQUVWXZKRYPTOSABC
TOSABCDEFGHIJLMNQUVWXZKRYPTOSABCD
OSABCDEFGHIJLMNQUVWXZKRYPTOSABCDE
SABCDEFGHIJLMNQUVWXZKRYPTOSABCDEF
ABCDEFGHIJLMNQUVWXZKRYPTOSABCDEFG
BCDEFGHIJLMNQUVWXZKRYPTOSABCDEFGH
CDEFGHIJLMNQUVWXZKRYPTOSABCDEFGHI
DEFGHIJLMNQUVWXZKRYPTOSABCDEFGHIJ
EFGHIJLMNQUVWXZKRYPTOSABCDEFGHIJL
FGHIJLMNQUVWXZKRYPTOSABCDEFGHIJLM
GHIJLMNQUVWXZKRYPTOSABCDEFGHIJLMN
HIJLMNQUVWXZKRYPTOSABCDEFGHIJLMNQ
IJLMNQUVWXZKRYPTOSABCDEFGHIJLMNQU
JLMNQUVWXZKRYPTOSABCDEFGHIJLMNQUV
LMNQUVWXZKRYPTOSABCDEFGHIJLMNQUVW
MNQUVWXZKRYPTOSABCDEFGHIJLMNQUVWX
NQUVWXZKRYPTOSABCDEFGHIJLMNQUVWXZ
QUVWXZKRYPTOSABCDEFGHIJLMNQUVWXZK
UVWXZKRYPTOSABCDEFGHIJLMNQUVWXZKR
VWXZKRYPTOSABCDEFGHIJLMNQUVWXZKRY
WXZKRYPTOSABCDEFGHIJLMNQUVWXZKRYP
XZKRYPTOSABCDEFGHIJLMNQUVWXZKRYPT
ZKRYPTOSABCDEFGHIJLMNQUVWXZKRYPTO
KRYPTOSABCDEFGHIJLMNQUVWXZKRYPTOS
RYPTOSABCDEFGHIJLMNQUVWXZKRYPTOSA
YPTOSABCDEFGHIJLMNQUVWXZKRYPTOSAB
PTOSABCDEFGHIJLMNQUVWXZKRYPTOSABC
TOSABCDEFGHIJLMNQUVWXZKRYPTOSABCD
OSABCDEFGHIJLMNQUVWXZKRYPTOSABCDE
```

Cyrillic face — 32 rotations of `ТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯ`:

```
ТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТ
ЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕ
НЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕН
ЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬ
АБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬА
БВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБ
ВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВ
ГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГ
ДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГД
ЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖ
ЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗ
ИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИ
ЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙ
КЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙК
ЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛ
МОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМ
ОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМО
ПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОП
РСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПР
СУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПРС
УФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПРСУ
ФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПРСУФ
ХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПРСУФХ
ШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШ
ЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦ
ЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧ
ЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩ
ЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪ
ЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫ
ЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭ
ЮЯТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮ
ЯТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯ
```

# Appendix 3 — the Cyrillic cryptogram

The Cyrillic Projector carries the first **1133** characters; Antipodes carries all **1558**
(the Projector's text is an exact prefix). Both files are already in `lateral/keystreams/`.
The inline Latin `MEDUSA`, carved in the ciphertext about two-thirds down the Projector's top
panel, is omitted from these streams (harmlessly: 6 ≡ 0 mod 6, so the key phase is unaffected).

**Ciphertext, Antipodes Cyrillic face (1558):**

```
ЛТФЕЮТФЯЙЯМПХЦФАЧНЩПВБГЖЧСКЬГГЛЗДЭЙПЪКХСЙРЭАФНФПЩВПЕЦРДФАЩШТКСХСЧЫУХХЕЮКУМЛЕЧЛЫТ
ОБНЕЯЖЖИЬНЭЗЩЦРЛЫБПНФОИИАБЬПИКЛЕУРЫСМЪШЛЛБХМХЛЖШРАЩРЙЛПЕООЙЙВЦИЪЛБХЦРЫЧСКАРСРВЯЭ
ФКЮФРЮМОЯЗОЛОДЭШРЗУДХМАЭХОЙГЙЮФМЩХХСВИИЗХАГЙЯЬПСИБРРШОМКТСУЯГХУЬЛЕУРЫСМЪШСППЯЯЦШ
УШАЦЧПИМШНРБЧРЯЫМИУРАДФАИЮЙЫЦЯЛОНУФЖОФШХФЖСБВЪЧДЦСФБМДЭШРЗУДХУРБШТОКЩЪМХПОТОХОЩЧ
ЖАЦДЩРАЮГОЙВРБГЮБЗГЕЖРЙЛПЕООЙЙВЦНЗПГФЦЗАИВЯЮФЛЪЦХСЧЫШЬБЕОМЩШЖТЭДЙОТТФХПРПЛОДЭЩРЗ
УДХКПГФОЦБЩЪММЭКЧЕРЛМКЪЦЦЗЩЛФЦЧЪЩКВНФАЕСДПТДФПРЯЙКЮНХВЦБЮЕИСЧЯЧЦХМЖЛСПРЧУЛЭШЖЫИИ
ИНХЕЗЛЧЗРЗЙКЛППЕВЛЧСХЦЫОЙВРБУДХСВЪГЖЧСКАРСРВЯЭФРЩФЯЦЩПЪЗЫТФОЙЙУСДТЮТВСБРХСПБЩЛШК
УВЙЙГЗЙАЧЛЬРЙЭМДЧЧРЬСТНКЙЕКДОБЖБЛШИЫЙБЙИДРРЦХОЩЖВЪКБЧКЖНФПШЦЗУЙДЯГАЧЙКУЗФЕЦИЯИЙФ
ЭБЛСДТГЗШРЖЕДФЩЖЙЯНБООЬШФПЮКЗЦУДИНХЕОХПОЙАХДЭСБЩЙЖЭШВЪОДЩВУСЛМЩГЖШУДИГЛЕШКПУУЕЧД
ЛСУЦЮТЮНХЪПБУПРЬГИУСБЙЙПЮГАФФЕШБФБМЙПИМЪЮКЩХХТНФЩШПЕЯБЧККЩВЙЩЗЛЮСВЮЙКУКФСЫТЫСВЛС
ЛЬЗУЦИКЩДРСУРЗХРФЙРЭМРХФЛКФАЙЙКУАЛЩГМЙЖШЪЙЬЩКФНФИДЙРФГКУКАЯЙОУМАТЭТЦКВЕЖОЙИДЦДКГ
ЩФЕЖБЮХЛЕССЭСНЩЩХПОЬДЖЙЙЗГЕИТЙМАШЙЙУМФСЫТЫСВСИДСДРБФНУОРУШТБЗПЪДЗЯЫААЧКУМАЯХТМЦР
ИЦЗЩЛЛЕУУПФЖТЭДУХРШЙОРБЭЦЙОПЙЛЪЙТЧШЙАФНПШФЭМБЩЪЖТПДЛРШБШБЧРЖЫМНЧЗЫТЙЖЪСМЪЧДХКЛНЦ
ПЗХРФЙРЭМРХФМЫБВЪЧБШЕФБЖТЩВВЪУБЧКЖАЦПЫГШАМИПРЙЪГОЦКЙГРЛЮБУСПБЮРРХФТЫХЖТГИЙКАФМТН
КЙФФНЦЙЫСЧБШЕФБЖБЛСВТЧРЫЙПТМБОЙМСГУМБПЪЦРЙРАЪХКЫХАДГОЩГДЦСТМСГЪЮБЭМЙЩГЯЛОЬЦЧШЮСФ
ЕЖБЮХЛЕЙЬЩХШШГОЭШВЕХОЩЖРЮКТПШРАЧТЛБХМЦЯСБЛЬНРГПРУТБЭШВЕСМЫЗФЮЙАЯЗХУФОНСВЩГМЫБВСЮ
БШСВЦПТЪТХСЙРЭАФЭФЙЪФРЯЙРУФРФГРДЭЙЬФЗЩЗАТЧДЛСЖТУЛПЖВЪКБЧКЖТГГЙУАШЙДПДРЬЩЗЩГРШМРП
ОЖЫФЕЛКПНЙРЯЫААЧКУМРФХТМЦРИЦЗЩДРШЖДРЗПЪВНЭОЖНФЙЭОЖШФНЙРЙЪХЛШКХЪПБЭХФЬХОЩГРЖМОЯЗХ
ВЮБЧТЧЭЖЙПЭАБЙИДХХФЩНЩДПВЧОПРПЪЙАПОАТГЦПЛФБШТЧТЙФНПЮЦСЮЙКУАХФЛТБКХВРДНСФВКАПРПЛЫ
ГЙХРФЙОАЗПЪЙЛЭСБЕФМЙХПЛЫЬЩХШШГОЭШВЦУКГ
```

**Plaintext (1558), decrypted exactly by the rule in §A.5; message 1 = 0–776, message 2 = 777–1557:**

```
ВЫСОЧАЙЪИМИСКУССТВОМВТАЙНОЙРАЗВЕДКЕСПИТАЕТСЯСПОСОБНОСТЬРАЗРАБОТАТЬИСТОЧНИККОТОРЫ
МТЫБУДЕШЬВСЕЦЕЛОРАНПОРЯЖАТЬСЯИКОНТРОЛИРОВАТЬПОЭТОСУТАЙНОЙРАЗВЕДЫВАТЕЛЬНОЙСЛУЖБЫК
ОНТРОЛИРУЕМЫЙИСТОЧНИККАКПРАВИЛОПОСТАЯЛЯЕТСАМУЮНАДЕЖНУЭИНФОРМАЦИЮКОНТРОЛИРУЕМЫМСЧ
ИТАЕТСЯКУПЛЕННЫЙИЛИНАХОДЯЩИЙСЯВЛЮБОЙДРУГОЙЗАВИТИМОСТИИСТОЧНИКПОТРАДИЦИИЦЕЛЬЭПРОФ
ЕССИОНАЛАРАБОТАЮЩЕГОВТАЙНОЙРАЗВЕЫКЕВСЕГДЯБЫЛООПУТАТЬЛЮБОЙПОТЕНЦИАЛЬНОЦЕННЫЙИСХОЧ
НИКИНФОРМАЦИИПСИХОЛОГИЧЕСКОЙСЕТЫОИВПОДХОДЮЩИЙМОМЕНТЭТУСЕТЬЗАТЯНУТЬВОЗМОЖНОСТЕЙДЛ
ЯЭТОГОНЕОЧЕНВМНОЯОНОТЕХРАБОТНИКОВИАЙНОЙСЛУЖБЫКОТОРЫЕУСПЕШНОРАЗРАБАТЫВАЮТКОНТУОЛИ
РУЕМЫЕИСТОЧНИКИИНФОРМАЦИИОЖИДАЕТЗЧЯЧИТЕЛЬНОЕПРОДВИЖЕНИЕПОСЛУЖБЕИУВАЖЕНИЕСОСЛУЖИВ
ЦЕВОДНАКЛНЕОБХОДИМЫЕДЛЯДОСТИЖЕНИЯЭТОЙЦЕЛИСПИСОБЗЕЙСТВИЙИОБРАЗПОВЕДНИЯВКОРНЕПРОТИ
ВОРЕЧАТЭТИКЕИМОРАЛИОБЩЕСТВАВОБЛАСТИМЕЖЛИЧНОСТНЫХОТНОШЕНИЙОБИЗГОТОВЛЕНИИСАХАРОВЫМ
ОЧЕРЕДНОГОАНТЮСОВЕТСКОГООБРАЩЕНИЯКЗАПАДУИЕГОИСПОЛЬЗОВАНИИАМЕРИКАНЦАМИВОВРАЖДЕБНЫ
ХСОВЕТСКОМУСОЮЗУЦЕЛЯХВМАЕГОДААКАДЕМИКСАХАРОВАДИЗГОТОВИЛОБРАЩЕНИБКУЧАСТНИКАМПАГУО
ШСКОЙКОНФЕРЕНЦИИСОДЕРЖАЩЕЕРЕЗКИЕАНТИСОВЕТСКИЕОЦЕНКИВНУТРЕННЕЙИВНЕШНЕЙПОЛИТИКИКПС
СЮСОВЕТСКОГОПРАВИТЕЛЬСТВАОБВИНЕНИЕСССРВУСИЛЕНИИАРМИИФЛОТАРАКЕТНОГОАРСЕНАЛАИАВИАЦ
ИИВОВМЗШАТЕЛЬСТВЕВОВНТТРЗННИЕДЗЛААФГАНИСТАНАИПНРСАХАРОВДЕМАГОГИЧЕСКИЗАЯВЛЯЕТЧТОС
ОВЕТСКОЕГОСУДАРСТВОПРОДОЛЖАЕТОСТАВАТЬСЯЗАКРЫТЫМОБЩЕСТВОМПРЕСЛЕДУЕТБОРЦОВЗАПРАВАЧ
ЕЛОВЕКАПЫТАЕТСЯСКОМПРОМЕТИРОВАТЬШИРОКОЕАНТИВОЕННОЕДВИЖЕНИЕНАЗАПАДЕИЕГОРУКОВОДИТЕ
ЛЕЙОБВИНПЕТУЧАСТНИКОВПАГУОШСКОГОДВИЖЕНИЯВСЛЕПОМСЛЕДОВАНИИПОЛИТИКЕСССРПРОВОЦИРУЕТ
УЧЕНЫХКВМЕШАТЕЛЬСТВУВОГНУТРЕННИЕДЕЛАНАШЕЙСТРАНЫИВЫСТУПЛЕНИЯТВЗАЩИТУЛИЦОСУЖДЕННЫХ
ЗАСОВЕРШЕНИЕОСОБООПАСНЫХГОСУДАРСТВЕННЫ
```

**The cipher, restated for reimplementation:**

```python
A = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"   # straight Russian, no Ё      -> plaintext
B = "ТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯ"   # ТЕНЬ-keyed, Ш moved after Х -> ciphertext AND key
KEY = "ЙБАСГТ"       # == МЕДУЗА (MEDUSA) transcoded A->B; shifts [12,5,4,19,7,0]
BOUNDARIES = [0, 777]  # the key restarts at the start of message 2

def shift(i):
    s = max(b for b in BOUNDARIES if b <= i)
    return B.index(KEY[(i - s) % 6])

encrypt = lambda P: "".join(B[(A.index(p) + shift(i)) % 32] for i, p in enumerate(P))
decrypt = lambda C: "".join(A[(B.index(c) - shift(i)) % 32] for i, c in enumerate(C))
```

Round-trip on the real text: **decrypt(ciphertext) == plaintext and encrypt(plaintext) == ciphertext,
1558/1558 characters, exact.** In ACA terms this is **Quagmire II** (straight plaintext alphabet,
keyed ciphertext alphabet, key letter = the ciphertext of plaintext `А`), where Kryptos K1/K2 are
**Quagmire III**.

