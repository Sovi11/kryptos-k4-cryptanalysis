# Kryptos — reference document

Working reference for this K4 effort. Everything here is sourced; URLs are inline. Claims I could not
pin to a reliable source are marked **[uncertain]**. Nothing on this page is a proposed solution to
K4, and no third party's claimed solution is repeated here as fact.

Last revised 2026-09-12.

Repository layout:

| path | contents |
|---|---|
| `data/` | ciphertexts, plaintexts, cribs, panel transcriptions (the inputs every script reads) |
| `analysis/` | Python: cipher-family sweeps, running-key/autokey, geometry, two-cipher stacks |
| `findings/` | per-line-of-attack reports and raw logs/JSON |
| `README.md` | this file |

---

## 0. One-paragraph summary

*Kryptos* is a 1990 sculpture by Jim Sanborn in the courtyard of the CIA's New Headquarters Building
at Langley, Virginia. Its main element is an S-shaped copper screen carrying 865 letters and 4
question marks of ciphertext on one face and a keyed Vigenère tableau on the other. The ciphertext
divides into four passages. K1 and K2 are Quagmire-III polyalphabetics on a KRYPTOS-keyed alphabet
with keys PALIMPSEST and ABSCISSA; K3 is a pure route transposition; K4, the last 97 letters, has
never been solved publicly. Sanborn has released four plaintext cribs. In 2025 his private archive —
including the K4 plaintext — was sold at auction for $962,500 after two journalists independently
found the plaintext in his papers at the Smithsonian. The buyer, Paradigm, now runs a hash-based
verifier for submitted K4 solutions. The *method* by which the K4 ciphertext maps to that plaintext
has still not been published by anyone.

---

## 1. The sculpture

### 1.1 Physical form

* Artist: **Jim Sanborn**. Cryptographic systems designed with **Edward Scheidt**, then retiring as
  **Chairman of the CIA's Cryptographic Center** (joined the CIA's Office of Communications in 1963,
  retired December 1989). Scheidt taught Sanborn the encryption methods; **Sanborn chose the
  messages**. ([Wikipedia: Kryptos](https://en.wikipedia.org/wiki/Kryptos),
  [Wikipedia: Edward Scheidt](https://en.wikipedia.org/wiki/Edward_Scheidt))
* Dedicated **November 3, 1990**, at the George Bush Center for Intelligence, Langley, Virginia
  (38.95227° N, 77.14573° W). Commission cost $250,000 in 1988.
  ([Wikipedia](https://en.wikipedia.org/wiki/Kryptos))
* Dimensions roughly **11–12 ft high × 20 ft** (3.4–3.7 m × 6.1 m).
* Materials: four large **copper** plates plus water, wood, plants, **red and green granite**, white
  **quartz**, and **petrified wood**.
* The dominant element is a **vertical S-shaped copper screen**, "resembling a scroll or a piece of
  paper emerging from a computer printer", standing in the northwest corner of the NHB courtyard just
  outside the agency cafeteria. The characters are **cut out of** the copper (not engraved), so the
  screen is a stencil and light passes through it. Only the 26 Latin letters and question marks
  appear. The screen is supported by a slab of petrified wood.
  ([Wikipedia](https://en.wikipedia.org/wiki/Kryptos),
  [CIA](https://www.cia.gov/legacy/headquarters/kryptos-sculpture/))
* Sanborn has said the increasing complexity of the ciphers as one moves from the entrance into the
  courtyard was meant to feel "as if it were a fossil".

### 1.2 The left (ciphertext) panel

The ciphertext face carries **869 characters = 865 letters + 4 question marks**, in **28 rows**.

**Important correction to an earlier assumption in this repo:** the panel is *not* a uniform 31-column
grid. In the standard transcription the row lengths are

```
32 31 31 30 31 32 31 31 32 31 30 31 31 31 32 30 31 30 32 30 32 31 33 29 31 31 31 31
```

— they run from 29 to 33 and only average ~31. Any geometry argument that assumes a rectangular
31-wide grid across the whole panel is assuming something the carving does not support. What *is*
true is that the **last four rows are each exactly 31 characters**, and K4 occupies the final four
characters of row 25 plus all of rows 26–28, giving the familiar `97 = 4 + 31 + 31 + 31`.

Transcription (also `data/sculpture_panels.txt`):

```
EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJ
YQTQUXQBQVYUVLLTREVJYQTMKYRDMFD
VFPJUDEEHZWETZYVGWHKKQETGFQJNCE
GGWHKK?DQMCPFQZDQMMIAGPFXHQRLG
TIMVMZJANQLVKQEDAGDVFRPJUNGEUNA
QZGZLECGYUXUEENJTBJLBQCRTBJDFHRR
YIZETKZEMVDUFKSJHKFWHKUWQLSZFTI
HHDDDUVH?DWKBFUFPWNTDFIYCUQZERE
EVLDKFEZMOQQJLTTUGSYQPFEUNLAVIDX
FLGGTEZ?FKZBSFDQVGOGIPUFXHHDRKF
FHQNTGPUAECNUVPDJMQCLQUMUNEDFQ
ELZZVRRGKFFVOEEXBDMVPNFQXEZLGRE
DNQFMPNZGLFLPMRJQYALMGNUVPDXVKP
DQUMEBEDMHDAFMJGZNUPLGEWJLLAETG
ENDYAHROHNLSRHEOCPTEOIBIDYSHNAIA
CHTNREYULDSLLSLLNOHSNOSMRWXMNE
TPRNGATIHNRARPESLNNELEBLPIIACAE
WMTWNDITEENRAHCTENEUDRETNHAEOE
TFOLSEDTIWENHAEIOYTEYQHEENCTAYCR
EIFTBRSPAMHHEWENATAMATEGYEERLB
TEEFOASFIOTUETUAEOTOARMAEERTNRTI
BSEDDNIAAHTTMSTEWPIEROAGRIEWFEB
AECTDDHILCEIHSITEGOEAOSDDRYDLORIT
RKLMLEHAGTDHARDPNEOHMGFMFEUHE
ECDMRIPFEIMEHNLSSTTRTVDOHW?OBKR
UOXOGHULBSOLIFBBWFLRVQQPRNGKSSO
TWTQSJQSSEKZZWATJKLUDIAWINFBNYP
VTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR
```

This matches the transcription in the
[Wikipedia article](https://en.wikipedia.org/wiki/Kryptos), which in turn matches
[Elonka Dunin's transcript](https://www.elonka.com/kryptos/transcript.html) and Jim Gillogly's
[photographs](http://www.voynich.net/Kryptos/)). Verified in this repo: concatenating the 28 rows
reproduces K1 (63 letters) + K2 (369 letters + 3 `?`) + K3 (336 letters + 1 `?`) + K4 (97 letters)
exactly.

Of the four question marks, **three fall inside K2** — they are carved in the ciphertext at exactly
the three places where K2's plaintext asks a question ("HOWS THAT POSSIBLE ?", "DOES LANGLEY KNOW
ABOUT THIS ?", "WHO KNOWS THE EXACT LOCATION ?"), so they are punctuation carried through the cipher
rather than enciphered characters — and **one ends K3** ("CAN YOU SEE ANYTHING**?**"). K1 and K4 have
none. The `?` immediately preceding `OBKR` is K3's; K4 begins at the `O`.

### 1.3 The right (tableau) panel — and the extra L

The other face carries a **keyed Vigenère tableau**: a header row `ABCDEFGHIJKLMNOPQRSTUVWXYZABCD`,
26 rows labelled A–Z each holding a rotation of the keyed alphabet
`KRYPTOSABCDEFGHIJLMNQUVWXZ` extended to 30 columns, and the header repeated at the bottom. That
alphabet contains all 26 letters (it is `KRYPTOS` followed by the unused letters in order).

Transcription as carved (leading space = the unlabelled header rows; row `N` is the anomaly):

```
 ABCDEFGHIJKLMNOPQRSTUVWXYZABCD
AKRYPTOSABCDEFGHIJLMNQUVWXZKRYP
BRYPTOSABCDEFGHIJLMNQUVWXZKRYPT
CYPTOSABCDEFGHIJLMNQUVWXZKRYPTO
DPTOSABCDEFGHIJLMNQUVWXZKRYPTOS
ETOSABCDEFGHIJLMNQUVWXZKRYPTOSA
FOSABCDEFGHIJLMNQUVWXZKRYPTOSAB
GSABCDEFGHIJLMNQUVWXZKRYPTOSABC
HABCDEFGHIJLMNQUVWXZKRYPTOSABCD
IBCDEFGHIJLMNQUVWXZKRYPTOSABCDE
JCDEFGHIJLMNQUVWXZKRYPTOSABCDEF
KDEFGHIJLMNQUVWXZKRYPTOSABCDEFG
LEFGHIJLMNQUVWXZKRYPTOSABCDEFGH
MFGHIJLMNQUVWXZKRYPTOSABCDEFGHI
NGHIJLMNQUVWXZKRYPTOSABCDEFGHIJL   <- 31 letters, one too many
OHIJLMNQUVWXZKRYPTOSABCDEFGHIJL
PIJLMNQUVWXZKRYPTOSABCDEFGHIJLM
QJLMNQUVWXZKRYPTOSABCDEFGHIJLMN
RLMNQUVWXZKRYPTOSABCDEFGHIJLMNQ
SMNQUVWXZKRYPTOSABCDEFGHIJLMNQU
TNQUVWXZKRYPTOSABCDEFGHIJLMNQUV
UQUVWXZKRYPTOSABCDEFGHIJLMNQUVW
VUVWXZKRYPTOSABCDEFGHIJLMNQUVWX
WVWXZKRYPTOSABCDEFGHIJLMNQUVWXZ
XWXZKRYPTOSABCDEFGHIJLMNQUVWXZK
YXZKRYPTOSABCDEFGHIJLMNQUVWXZKR
ZZKRYPTOSABCDEFGHIJLMNQUVWXZKRY
 ABCDEFGHIJKLMNOPQRSTUVWXYZABCD
```

(The `<-` annotation is mine; it is not on the sculpture. Every other row is the label letter plus
exactly 30 tableau letters.)

The carved tableau is **867 letters**; an ideal tableau would be **866**. The difference is a single
**extra `L` at the end of the row labelled `N`** — the 15th line of the panel counting the header.
Verified in this repo by diffing the transcription against a generated ideal tableau: that one row is
the *only* deviation.

```
carved  N  GHIJLMNQUVWXZKRYPTOSABCDEFGHIJL   (31 letters after the label)
ideal   N  GHIJLMNQUVWXZKRYPTOSABCDEFGHIJ    (30)
```

Consequence, also verified here: the **rightmost column** of the carved tableau reads

```
carved   DPTOSABCDEFGHILLMNQUVWXZKRYD      (28 entries: header + 26 rows + header)
ideal    DPTOSABCDEFGHIJLMNQUVWXZKRYD
```

The rows contributing those four letters are `L`, `M`, `N`, `O`: the ideal tableau gives
`H, I, J, L` there, and the extra L on row `N` makes it `H, I, L, L` — the word **`HILL`**.
Bauer, Link and Molle argued in *Cryptologia* that this may be a deliberate pointer to the **Hill
cipher** as K4's method ("James Sanborn's *Kryptos* and the matrix encryption conjecture",
*Cryptologia* 40(6), 2016, [doi:10.1080/01611194.2016.1141556](https://doi.org/10.1080/01611194.2016.1141556)).
Counter-evidence noted on Wikipedia: **Sanborn omitted the extra letter from the small *Kryptos*
models he sold**, which is at least consistent with the L being a fabrication slip rather than a
signal. Whether the L is intentional is **[uncertain]**. (This repo has separately ruled out Hill
2×2 and 3×3, linear and affine, in both directions and both alphabets — see `findings/families.md`.)

### 1.4 The Morse code slabs ("K0")

Outside the entrance to the New Headquarters Building stand several large **granite slabs with copper
sheets sandwiched between them**, carrying International Morse code. Read facing south, the usual
transcription is:

```
E E VIRTUALLY E  |  E E E E E E INVISIBLE
DIGETAL E E E    |  INTERPRETATIT
E E SHADOW E E   |  FORCES E E E E E
LUCID E E E      |  MEMORY E
T IS YOUR        |  POSITION E
SOS
RQ
```

([Wikipedia](https://en.wikipedia.org/wiki/Kryptos); dot-by-dot Morse at
[rumkin](https://rumkin.com/reference/kryptos/k0/); photographs and discussion at
[kryptosfan](https://kryptosfan.wordpress.com/speculations/keyword-retrieval/morse-code-translation/))

Caveats, all **[uncertain]**:

* The runs of lone `E` (a single dit) appear to be spacing or filler, not message letters.
* `DIGETAL ... INTERPRETATIT` is published variously as `INTERPRETATU`, `INTERPRETATAU` and
  `INTERPRETATIT`; the phrase is probably a (deliberately misspelled and truncated) "DIGITAL
  INTERPRETATION".
* `T IS YOUR POSITION` is widely read as a truncation of "WHAT IS YOUR POSITION"; the start of the
  line disappears under the granite and the lodestone.
* `RQ` is also read as `YR`.

I corrected `data/morse_and_misc.txt` to this reading and flagged the uncertainty there.

### 1.5 Compass rose, lodestone, courtyard

* One stone slab carries an engraved **compass rose pointing to a lodestone** (a naturally magnetised
  rock). ([Wikipedia](https://en.wikipedia.org/wiki/Kryptos))
* Popular accounts say the lodestone deflects a compass needle away from true north; the specific
  claim that it pulls toward west-southwest is **[uncertain]** — I found it only in secondary
  write-ups, not in a primary source.
* The courtyard installation also includes a landscaped garden, a **fish pond with opposing wooden
  benches**, a **reflecting pool**, and further stonework including a **triangle-shaped black stone
  slab**.
* The magnetism/lodestone motif ties to K2's plaintext, which speaks of the Earth's magnetic field.

### 1.6 Related sculptures that reuse Kryptos text

* ***Cyrillic Projector*** (1993 [uncertain on exact year of fabrication]; purchased by **UNC
  Charlotte** in 1997, installed between the Friday and Fretwell buildings). A hollow copper cylinder
  projecting encrypted **Russian Cyrillic** text, including an extract from a classified 1982 KGB
  document about Andrei Sakharov. Solved by **Frank Corr** (July 2003) and independently by **Mike
  Bales** (September 2003), with translation work coordinated by Elonka Dunin.
  ([Wikipedia](https://en.wikipedia.org/wiki/Cyrillic_Projector))
* ***Antipodes*** (1997), copper and petrified wood, 240 × 190 × 66 cm, at the **Hirshhorn Museum and
  Sculpture Garden**, Washington DC. One side repeats *Kryptos* text; the other repeats much of the
  *Cyrillic Projector* text plus additional Cyrillic. All the Cyrillic has been solved.
  ([Wikipedia](https://en.wikipedia.org/wiki/Antipodes_(sculpture)),
  [Elonka](https://www.elonka.com/kryptos/sanborn/antipodes.html))
* The Latin-side text on *Antipodes* differs from *Kryptos* in **spacing, added dots and added
  letters**, and it starts at a different point in the sequence. One description of the ordering
  (from Elonka's site, relayed via search results; I could not fetch the page directly, so treat the
  exact ordering as **[uncertain]**) is that *Antipodes* begins in K3, runs through K4, then a
  separator, then restarts at K1 and runs K1→K2→K3→K4, then K1→K2 again, truncating mid-K2.
* Sanborn also made an "Untitled Kryptos Piece" and small *Kryptos* models sold to collectors; the
  models omit the anomalous tableau L.

**Why this matters for K4:** *Antipodes* is a second, independent carving of the same K4 ciphertext.
Differences between the two carvings are a possible source of transcription corrections — and a
possible source of red herrings. I have not systematically diffed them; that is an open direction.

---

## 2. K1, K2, K3

### 2.1 The keyed alphabet

All of K1 and K2 use the same 26-letter keyed alphabet, which is also what the right-hand tableau
tabulates:

```
KRYPTOSABCDEFGHIJLMNQUVWXZ
```

The system is what the American Cryptogram Association calls **Quagmire III**: the plaintext
alphabet, the ciphertext alphabet and the key alphabet are all this keyed alphabet, with a repeating
keyword selecting the row. (Most popular write-ups just say "Vigenère"; Quagmire III is the precise
name, and it is the form this repo's code re-encrypts with. Verified: re-encrypting the K1 plaintext
under PALIMPSEST reproduces the carved K1 ciphertext exactly.)

### 2.2 K1

**Ciphertext (63 letters):**

```
EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD
```

**Method:** Quagmire III, KRYPTOS alphabet, key **PALIMPSEST**.

**Plaintext:**

```
BETWEEN SUBTLE SHADING AND THE ABSENCE OF LIGHT LIES THE NUANCE OF IQLUSION
```

`IQLUSION` for `ILLUSION` is one of the three misspellings Sanborn has said are intentional
("most of my things are rife with mistakes on purpose", 2005).

Wikipedia additionally reports that on line 7, column 26 of Sanborn's original coding chart the
keyword is written **PALIMPCEST**, with `ILLUSION` spelled correctly above it. **The arithmetic
checks out exactly** (verified here): the affected position is plaintext index 56 (0-based), where
the repeating key supplies `PALIMPSEST[6]`. In the KRYPTOS alphabet,

```
enc(L, C) = K   <- the letter actually carved
enc(L, S) = W
dec(K, C) = L   dec(K, S) = Q
```

So a `C`-for-`S` slip in the keyword at that one position produces precisely the carved `K`, and
decrypting that `K` with the correctly spelled keyword is what yields the `Q` of `IQLUSION`. That
makes a keyword slip a fully sufficient explanation for this particular "deliberate" misspelling.
Whether the chart really reads PALIMPCEST is **[uncertain]** — I have not seen it, and the
arithmetic is consistent with, but does not prove, the story. Note it does **not** explain
`UNDERGRUUND` or `DESPARATLY`.

Curiosity, not evidence: PALIMPSEST + ABSCISSA anagram to "P.S. It's as simple as ABC."

### 2.3 K2

**Ciphertext (369 letters + 3 question marks), as carved:**

```
VFPJUDEEHZWETZYVGWHKKQETGFQJNCEGGWHKK?DQMCPFQZDQMMIAGPFXHQRLGTIMVMZJANQLVKQEDAGDVFRPJ
UNGEUNAQZGZLECGYUXUEENJTBJLBQCRTBJDFHRRYIZETKZEMVDUFKSJHKFWHKUWQLSZFTIHHDDDUVH?DWKBFU
FPWNTDFIYCUQZEREEVLDKFEZMOQQJLTTUGSYQPFEUNLAVIDXFLGGTEZ?FKZBSFDQVGOGIPUFXHHDRKFFHQNTG
PUAECNUVPDJMQCLQUMUNEDFQELZZVRRGKFFVOEEXBDMVPNFQXEZLGREDNQFMPNZGLFLPMRJQYALMGNUVPDXVK
PDQUMEBEDMHDAFMJGZNUPLGEWJLLAETG
```

(line-wrapped here for readability; the panel row structure is in `data/sculpture_panels.txt`)

**Method:** Quagmire III, KRYPTOS alphabet, key **ABSCISSA**.

**Plaintext (corrected form):**

```
IT WAS TOTALLY INVISIBLE HOWS THAT POSSIBLE ? THEY USED THE EARTHS MAGNETIC FIELD X
THE INFORMATION WAS GATHERED AND TRANSMITTED UNDERGRUUND TO AN UNKNOWN LOCATION X
DOES LANGLEY KNOW ABOUT THIS ? THEY SHOULD ITS BURIED OUT THERE SOMEWHERE X
WHO KNOWS THE EXACT LOCATION ? ONLY WW THIS WAS HIS LAST MESSAGE X
THIRTY EIGHT DEGREES FIFTY SEVEN MINUTES SIX POINT FIVE SECONDS NORTH
SEVENTY SEVEN DEGREES EIGHT MINUTES FORTY FOUR SECONDS WEST X LAYER TWO
```

`UNDERGRUUND` is deliberate. The coordinates 38°57′6.5″N 77°8′44″W fall roughly 150–200 feet
south-east of the sculpture. "WW" is generally taken to be **William Webster**, CIA Director at the
time, who received the sealed solution at the dedication — **[uncertain]**, it is an inference, not a
Sanborn statement.

### 2.4 The 2006 correction: IDBYROWS → LAYERTWO

This one matters and is easy to get backwards, so, precisely:

* Every solution up to 2005 read K2 as ending `... WEST ID BY ROWS`.
* In **2005**, **Nicole Friedrich**, a logician in Vancouver, BC, showed that `WESTXLAYERTWO` was an
  alternative reading if one assumed a missing ciphertext character.
* On **April 19, 2006**, Sanborn contacted the online Kryptos community to say he had made an error
  in the sculpture: he **omitted an `S` from the ciphertext** (corresponding to an **`X` in the
  plaintext**), which had thrown the tail of the message out of phase with the key. He confirmed the
  correct ending is `WEST X LAYER TWO`.
  ([Wikipedia](https://en.wikipedia.org/wiki/Kryptos);
  [Elonka's announcement page](https://elonka.com/kryptos/CorrectedK2Announcement.html))
* Net effect on the data: the carved K2 ciphertext is **369 letters** but the plaintext is **370**.
  This repo verifies that re-encryption matches the carving for the first 361 letters and then
  diverges by exactly one dropped letter (expected `SWJLLAETG`, carved `WJLLAETG`).

**What Sanborn said it implied for K4.** When commenting on the error in 2006 he stated that **the
answers to the first three passages contain clues to the fourth passage**. That is the whole of the
documented statement. The much stronger readings in circulation — that "LAYER TWO" names the second
physical layer of the sculpture, that it identifies the tableau panel as a keystream source, that it
instructs you to apply two layers of cipher — are **community interpretations, not Sanborn's words**.
Treat them as hypotheses. (A separate, later observation: "LAYER TWO" also echoes Howard Carter's
phrase about "what we may call the second layer" on p. 170 of his Tutankhamun account, noted in July
2025 — suggestive, but again an interpretation.)

### 2.5 K3 — the concrete transposition

**Ciphertext (336 letters + a final `?`):**

```
ENDYAHROHNLSRHEOCPTEOIBIDYSHNAIACHTNREYULDSLLSLLNOHSNOSMRWXMNETPRNGATIHNRARPESLNNELEB
LPIIACAEWMTWNDITEENRAHCTENEUDRETNHAEOETFOLSEDTIWENHAEIOYTEYQHEENCTAYCREIFTBRSPAMHHEWE
NATAMATEGYEERLBTEEFOASFIOTUETUAEOTOARMAEERTNRTIBSEDDNIAAHTTMSTEWPIEROAGRIEWFEBAECTDDH
ILCEIHSITEGOEAOSDDRYDLORITRKLMLEHAGTDHARDPNEOHMGFMFEUHEECDMRIPFEIMEHNLSSTTRTVDOHW
```

**Method:** pure transposition — no substitution at all. K3's ciphertext is an exact anagram of its
plaintext (verified in this repo).

**Concrete procedure, re-derived and verified computationally on 2026-09-12** (ad-hoc check, not a
committed script; the procedure below is complete enough to reproduce in a few lines):

1. Write the 336 ciphertext letters left-to-right into rows **24 characters wide** (giving 14 rows).
2. Read out by **columns, rightmost column first, each column top to bottom**. (Equivalently: rotate
   the grid 90° counter-clockwise and read rows.)
3. Take that 336-letter intermediate, write it left-to-right into rows **8 characters wide** (42
   rows).
4. Read out by columns, rightmost first, top to bottom, again.

That yields the plaintext exactly. **No keyword is needed.** The same procedure works for the width
pairs (8, 24), (12, 16), (16, 12), (4, 48) and (48, 4) as well as (24, 8) — an exhaustive search over
all two-stage right-to-left column read-outs with widths 2–59 found exactly those six and nothing
else. Reverse the steps (write by columns right-to-left, read by rows) to encrypt.

**Plaintext:**

```
SLOWLY DESPARATLY SLOWLY THE REMAINS OF PASSAGE DEBRIS THAT ENCUMBERED THE LOWER PART OF
THE DOORWAY WAS REMOVED WITH TREMBLING HANDS I MADE A TINY BREACH IN THE UPPER LEFT HAND
CORNER AND THEN WIDENING THE HOLE A LITTLE I INSERTED THE CANDLE AND PEERED IN THE HOT AIR
ESCAPING FROM THE CHAMBER CAUSED THE FLAME TO FLICKER BUT PRESENTLY DETAILS OF THE ROOM
WITHIN EMERGED FROM THE MIST X CAN YOU SEE ANYTHING Q
```

`DESPARATLY` is deliberate. The passage paraphrases **Howard Carter**'s account of opening
Tutankhamun's tomb in November 1922. The final `Q` stands for the question mark carved on the panel —
`CAN YOU SEE ANYTHING?` is the question Lord Carnarvon asked Carter; Carter's answer, not on the
sculpture, was "Yes, wonderful things."

**Other descriptions you will encounter, and how much to trust them:**

* *"Key KRYPTOS = 0362514, keyed columnar transposition."* Widely repeated (e.g.
  [rumkin](https://rumkin.com/reference/kryptos/k3/), [kryptosfan](https://kryptosfan.wordpress.com/k3/),
  [Boxentriq](https://www.boxentriq.com/guides/kryptos-cipher-solutions)). It produces the right
  answer under some formulations, but the plain width-based route transposition above needs no key at
  all, so the KRYPTOS-numbering is **decoration rather than necessity** — **[uncertain]** whether
  Sanborn/Scheidt thought of it that way.
* *"NSA description: keyed columnar transposition, incompletely filled matrix 4 × 86."* Reported
  second-hand; 4 × 86 = 344 ≠ 336, so either the description or the relay is imprecise.
  **[uncertain]**.
* *"Double rotational transposition: 24 × 14 grid rotated 90°."* Same thing as steps 1–2 above, in
  different words.

### 2.6 Who solved K1–K3, and when

* **Late 1992 – June 1993:** an NSA team led by **Ken Miller**, with **Dennis McDaniels** and two
  unnamed others, solved K1–K3, following a challenge from CIA Deputy Director **Bill Studeman**. Not
  made public until March 2000; documentation released in 2013 under a FOIA request by Elonka Dunin.
* **February 1998:** CIA analyst **David Stein** solved K1–K3 by hand (K2 first, on Feb 21). Kept
  inside the intelligence community; a November 1998 note said a CIA analyst had solved "the lion's
  share".
* **1999:** **Jim Gillogly**, a computer scientist in southern California, was the first to announce
  a solution publicly, having used a computer. The CIA then confirmed Stein's earlier work (July
  1999).

([Wikipedia](https://en.wikipedia.org/wiki/Kryptos))

---

## 3. K4

### 3.1 The ciphertext

97 letters, occupying the last four characters of panel row 25 and all of rows 26–28:

```
OBKR
UOXOGHULBSOLIFBBWFLRVQQPRNGKSSO
TWTQSJQSSEKZZWATJKLUDIAWINFBNYP
VTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR
```

As one string (`data/k4_ciphertext.txt`):

```
OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR
```

Elementary statistics (recomputed here):

* n = 97; **all 26 letters appear**; index of coincidence **0.0361** (26·IoC = 0.938), i.e. *below*
  the 0.0385 expected of uniform random text and far below English's ~0.066.
* Doubled letters at 1-indexed positions 19 `BB`, 26 `QQ`, 33 `SS`, 43 `SS`, 47 `ZZ`, 68 `TT`.
* Autocorrelation: **lag 7 gives 9 coincidences against 3.46 expected, z = +3.04**, the largest of
  lags 1–24 (next largest is lag 1 at +1.22). Honest caveat: with 24 lags tested, a single +3.0
  outlier has a multiple-comparison p of roughly 0.03 — suggestive, not decisive, and this repo's
  period sweeps found nothing at period 7.

The flat-to-sub-random IoC is the central fact about K4: it is what Scheidt's "masking" remark
predicts, and it is why every unmasked periodic system fails.

### 3.2 The four confirmed cribs

All released by Sanborn; all 1-indexed into the 97 letters. `data/cribs.json`.

| positions | ciphertext | plaintext | released |
|---|---|---|---|
| 64–69 | `NYPVTT` | `BERLIN` | **November 2010** — *New York Times*, John Schwartz (sources give Nov 20 online / Nov 21 print; exact day **[uncertain]**) |
| 70–74 | `MZFPK` | `CLOCK` | **November 20, 2014** — *NYT*, "A New Clue to 'Kryptos'" |
| 26–34 | `QQPRNGKSS` | `NORTHEAST` | **January 29, 2020** — *NYT* |
| 22–25 | `FLRV` | `EAST` | **August 2020** (Sanborn: he had "released this layout to several people as early as April") |

I corrected `data/cribs.json`, which had previously dated the EAST clue to the same January 29, 2020
NYT article as NORTHEAST. It was a separate, later release.

Together they give the contiguous plaintext runs `EASTNORTHEAST` (22–34) and `BERLINCLOCK` (64–74) —
24 known (ciphertext, plaintext) pairs, the constraint set every script in `analysis/` is tested
against.

Notes on the cribs:

* **Position 74 encrypts `K` to `K`**, and position 33 encrypts `S` to `S`. Sanborn/NYT called this
  out explicitly in 2014: *a character can encrypt to itself*. This alone rules out every system in
  which no letter can ever represent itself — Playfair and the Enigma family in particular.
* On CLOCK, Sanborn said: **"You'd better delve into that particular clock"**, adding "There are
  several really interesting clocks in Berlin." In 2025 he confirmed the reference is the **World
  Clock** (Urania-Weltzeituhr) on Alexanderplatz.
* In November 2025 Sanborn released further thematic hints: that a **1986 trip to Egypt** and the
  **1989 fall of the Berlin Wall** figure in the solution, and that the codes concern "delivering a
  message". These are thematic, not positional.
  ([Scientific American](https://www.scientificamerican.com/article/cia-kryptos-puzzle-creator-releases-final-clues/))

### 3.3 What Scheidt has said about the method

Ed Scheidt has repeatedly characterised K4 as differing in kind from K1–K3:

* He rated the difficulty "around nine out of ten" and expected it to fall in five to ten years.
* He has described an intentional **"change in the methodology"** between sections.
* On K4 specifically: the earlier sections leave "the English language still visible through the
  code", but for the fourth "I masked the English language", so a solver must **"solve the technique
  first and then go for the puzzle"**.

These are paraphrases from interviews and talks (relayed at
[kryptosfan](https://kryptosfan.wordpress.com/tag/ed-scheidt/) and elsewhere) — they are not a
specification, and "masking technique" is Scheidt's phrase, not the name of a cipher.
**[uncertain]** whether "masking" means a second cipher layer, a transposition, nulls, or something
non-standard.

Sanborn has also said (2005) that he had put in place a method by which a correct solution could be
confirmed after his death, and that the sculpture contains a riddle that persists beyond K4's
decryption.

### 3.4 K5

* Sanborn has hinted for years that a **fifth message** exists and would reveal itself after the
  first four are solved.
* Confirmed in 2025: **K5 is also 97 characters long**, and **the two 97-letter messages share some
  of the same coded words in the same positions**. Sanborn has described K5 as itself a riddle that
  "is not going to be finished when it's decoded", thematically tied to K2's "its buried out there
  somewhere", and destined to appear "in a public space".
  ([Scientific American](https://www.scientificamerican.com/article/cia-kryptos-puzzle-creator-releases-final-clues/))
* The K5 **ciphertext was included in the auctioned archive**; Paradigm says Sanborn "created [it] at
  the same time" as K4 and that they "plan to release K5 in the future", with no date given.
  ([Paradigm](https://paradigm.xyz/2026/06/kryptos))
* As of this writing the K5 ciphertext is **not public**. The claim that K5 cannot be solved until K4
  is solved comes from Sanborn's own framing; whether it is a mathematical dependency or an
  editorial one is **[uncertain]**.

**Why K5 matters to K4 work:** if two 97-letter messages built at the same time share coded words at
the same positions, that is a strong hint that the system is **positional** — that position *i* is
processed the same way regardless of message. It argues against pure autokey (where the keystream
depends on the message) and for a keystream fixed by position. That is an inference, not a
confirmed fact.

---

## 4. 2025–2026: the archive, the auction, the verifier

Facts and dates only.

**August 2025.** In a letter to *The Washington Post*, Sanborn announced he would auction the
solution to K4, hoping the buyer would keep it secret: "Power resides with a secret not without it."
He wrote that the decision "has not been an easy one", acknowledged "many in the Kryptos community
will find it upsetting", and cited no longer having "the physical, mental or financial resources" to
maintain the code. He set the sale for **November 20**, his 80th birthday. In the same period he
confirmed the existence and 97-character length of K5.

**September 3, 2025 — the Smithsonian recovery.** Writers **Jarett Kobek** and **Richard Byrne**
emailed Sanborn with the K4 plaintext. They had noticed from the auction listing that Sanborn's
original coding charts were held at the **Smithsonian's Archives of American Art** (donated roughly
two years earlier), requested access, and photographed the papers. Among them were taped-together
scraps of scrambled sentence fragments — not a key and not a method. Combining those fragments with
Sanborn's publicly released cribs (BERLIN, CLOCK, EAST, NORTHEAST) let them reconstruct the K4
plaintext. Kobek: **"There's no way on earth that this is a cryptographic solve."** Sanborn has
stressed the same distinction — they found scrambled text, they did not break the cryptogram.
([Scientific American](https://www.scientificamerican.com/article/how-the-cias-kryptos-sculpture-gave-up-its-final-secret/),
[RR Auction](https://content.rrauction.com/kryptos-k4-discovered-not-solved-heres-what-actually-happened/))

**Aftermath.** Sanborn, after consulting the auction house, asked Kobek and Byrne to sign NDAs
(reportedly with a share of proceeds attached); they **refused**, but agreed to keep the plaintext
secret and have not published it. RR Auction is reported to have sent them repeated legal-threat
emails **[uncertain — this appears in press coverage, not in a primary document I could verify]**.
Sanborn asked the Smithsonian to **seal the relevant files for 50 years, until 2075**, and the
Smithsonian complied.

**October 16 – November 20, 2025 — the sale.** RR Auction (Boston) listed the lot as part of
"Decoding History: Kryptos, Enigma and the Rosetta Stone". The lot — "The Complete Secrets of
Kryptos: Jim Sanborn's Private Archive" — comprised the K4 solution, K5 material, a prototype
sculpture, the encryption tables/coding charts, ephemera, and a private explanation session with
Sanborn. Estimate **$300,000–$500,000**. It sold on **November 20, 2025** for **$962,500** to an
anonymous bidder.
([RR Auction lot](https://www.rrauction.com/auctions/lot-detail/350761607302001-the-complete-secrets-of-kryptos-jim-sanborns-private-archive/),
[Smithsonian Magazine](https://www.smithsonianmag.com/smart-news/nobody-has-been-able-to-solve-the-cias-famous-kryptos-sculpture-soon-the-solution-will-be-sold-to-the-highest-bidder-180987200/),
[ARTnews](https://www.artnews.com/art-news/news/kryptos-sculpture-code-cia-1234762958/))

**June 12, 2026 — the buyer revealed; the verifier.** **Paradigm**, a crypto investment firm,
identified itself as the buyer and published its plans.
([Paradigm](https://paradigm.xyz/2026/06/kryptos))

How the verifier works, per Paradigm's own description:

1. Sanborn typed the K4 plaintext into an isolated, freshly set-up computer.
2. A program on that machine computed **SHA-256** of the plaintext.
3. The hash was sent to **Google Cloud KMS**, which returned an **HMAC** tag reproducible only by
   sending the same SHA-256 hash to the same cloud-held key.
4. The plaintext never left the device; the laptop was then wiped.

So Paradigm claims it can *verify* a submitted plaintext without ever *knowing* it. Submissions cost
**$1** (Stripe), stated purpose: to make brute-forcing the hash uneconomic. Paradigm also published
K1–K3 solutions on its site and launched a separate ten-puzzle **Kryptos CTF** beginning on or about
**June 12, 2026**, with $1,000 per puzzle to the first solver ($10,000 total); K4 itself is a
non-prize submission channel.
([Paradigm CTF rules](https://paradigm.xyz/kryptos-ctf/official-rules))

**Status as of 2026-09-12: K4 is not publicly solved.** The plaintext exists in private hands (Kobek,
Byrne, Sanborn, and whatever is in the sealed archive), and no one has published a method that
derives it from the ciphertext. Paradigm's own page says plainly that it is "still unsolved". Some
aggregator and podcast headlines from 2026 say "Kryptos K4 solved by Paradigm" — **those headlines
are wrong**; Paradigm bought a solution, it did not break the cipher.

Two practical consequences for this project:

* The existence of a public verifier changes the endgame: a candidate plaintext can in principle be
  checked. **This project does not submit to it** — submission is a paid transaction and is out of
  scope.
* A verifier that costs $1 per guess and an archive sealed until 2075 both mean the *method* remains
  the interesting open problem, independent of the plaintext.

---

## 5. Primary sources

Ranked by usefulness for actual cryptanalysis.

| source | URL | what it's good for |
|---|---|---|
| **Elonka Dunin's Kryptos page** | https://www.elonka.com/kryptos/ | The canonical archive: [FAQ](https://www.elonka.com/kryptos/faq.html), [transcript](https://www.elonka.com/kryptos/transcript.html), [timeline](https://elonka.com/kryptos/KryptosTimeline.html), clue history, rubbings, photos, the NSA FOIA documents. Dunin is the community's de facto historian. **Note: this site did not respond to my automated fetches; cited from its known contents and from secondary references.** |
| **The Kryptos Group** | http://kryptos.yak.net/ | The long-running discussion group (originally a Yahoo Group, co-moderated by Dunin). Where Sanborn posted the April 2006 K2 correction. |
| **Jim Gillogly's photographs** | http://www.voynich.net/Kryptos/ | Photographs of the panels by the first public solver — the reference for settling transcription disputes. |
| **rumkin.com Kryptos reference** | https://rumkin.com/reference/kryptos/ | Clean per-section pages: [K0 Morse](https://rumkin.com/reference/kryptos/k0/) (with the actual dot/dash strings), [K3](https://rumkin.com/reference/kryptos/k3/), [K4](https://rumkin.com/reference/kryptos/k4/), [K5](https://rumkin.com/reference/kryptos/k5/). |
| **Hörenberg, "Kryptos K4"** | https://kryptos.hoerenberg.com/ | The most disciplined public K4 analysis site — explicitly separates documented facts from its own hypotheses (its central hypothesis is a two-layer encryption with a statistics-masking layer). Also a good [links](https://kryptos.hoerenberg.com/index.php?cat=Links) page. Its conclusions are the author's, not established. |
| **NumberWorld blog** | https://www.numberworld.blog/2017/03/kryptos-cipher-part-1.html | Four-part technical series ([2](https://www.numberworld.blog/2017/03/kryptos-cipher-part-2.html), [4](https://www.numberworld.blog/2020/07/kryptos-cipher-part-4.html)); careful on panel layout and K4 statistical anomalies. The author's own decryption proposals are proposals. |
| **kryptosfan, "Kryptos — Beyond K4"** | https://kryptosfan.wordpress.com/ | Deep archive of community work: [copperplate](https://kryptosfan.wordpress.com/copperplate/), [K3 methods](https://kryptosfan.wordpress.com/k3/), [Morse](https://kryptosfan.wordpress.com/speculations/keyword-retrieval/morse-code-translation/), [Ed Scheidt quotes](https://kryptosfan.wordpress.com/tag/ed-scheidt/). |
| **Wikipedia, "Kryptos"** | https://en.wikipedia.org/wiki/Kryptos | Best single sourced overview; carries the full panel transcriptions and the citation trail. A few passages are garbled; check its refs rather than its prose. |
| **CIA's Kryptos page** | https://www.cia.gov/legacy/headquarters/kryptos-sculpture/ | Official description and photographs. |
| **Jim Sanborn's site** | http://jimsanborn.net/main.html#KRYPTOS/ | The artist's own page. |
| **Paradigm** | https://paradigm.xyz/2026/06/kryptos | Current owner of the archive; describes the verifier. Do not submit (paid). |
| **Bauer, Link & Molle (2016)** | https://doi.org/10.1080/01611194.2016.1141556 | *Cryptologia* 40(6): the matrix-encryption / Hill-cipher conjecture built on the extra L. |
| **NSA FOIA release** | https://media.defense.gov/2021/Jul/12/2002760451/-1/-1/0/KRYPTOS_SLIDES.PDF | Declassified NSA material on the 1992–93 internal solve. |

**Sites to treat as claims, not sources.** Several sites publish a "reconstructed" or "recovered" K4
plaintext (e.g. solvekryptos.com). None of these is confirmed by Sanborn, Kobek, Byrne or Paradigm,
and none comes with a published method that derives the plaintext from the ciphertext. Do not seed
cryptanalysis with them and do not cite them as fact.

---

## 6. Corrections made to `data/`

All four edits verified not to break the parsers in `analysis/` (`runningkey_lib`, `k4_common`,
`twocipher_common`, `geometry_common`, `geo2_b_panel` all still import and produce 24 cribs, 97-letter
ciphertext, 63/370-letter K1/K2 plaintexts).

1. **`data/cribs.json`** — the EAST crib was dated `2020-01-29 (NYT)`, the same as NORTHEAST. Wrong:
   NORTHEAST came in the January 29, 2020 NYT article; **EAST was a separate release in August 2020**
   (Sanborn noted he had shared the layout privately "as early as April"). Also dated BERLIN and
   CLOCK to their specific NYT articles. Positions and letters were already correct and are unchanged.
2. **`data/k1_k3_plaintext.txt`** — the K2 note said the 2006 fix was "a dropped X in the
   ciphertext". **Backwards**: Sanborn omitted an **S from the ciphertext**, which corresponds to an
   **X in the plaintext**. Added the date (April 19, 2006), Nicole Friedrich's 2005 priority, the
   369-vs-370 letter count, and the verified concrete K3 transposition procedure. Ciphertext and
   plaintext strings unchanged.
3. **`data/sculpture_layout.txt`** — said "Left (ciphertext) panel of Kryptos is 31 characters wide".
   **Not true of the panel as a whole**: row lengths run 29–33. Replaced with the actual per-row
   widths and the accurate narrower statement (the last four rows *are* each 31, which is what makes
   `97 = 4+31+31+31` hold for K4). The four K4 lines themselves are unchanged.
4. **`data/morse_and_misc.txt`** — the Morse list was in a non-standard order and gave
   `DIGETAL INTERPRETATU`. Replaced with the reading published in Wikipedia/rumkin (including the
   filler `E`s and the two-line slab structure), flagged the genuine disagreement between published
   transcriptions, and replaced the bare phrase "masking technique, per Sanborn/Scheidt" with what
   Scheidt actually said and the note that it is a paraphrase, not a specification.

**Checked and found correct, no change:** `data/k4_ciphertext.txt` (97 letters, matches the panel);
`data/sculpture_panels.txt` (both panels match the Wikipedia/Elonka transcription character for
character, including the extra `L` in tableau row `N`; concatenating the left panel reproduces
K1+K2+K3+K4 exactly); the K1/K2/K3 plaintext strings; the keyed alphabet; all 24 crib positions.

---

## 7. Where this project stands

Summarised from `findings/families.md` and `findings/runningkey.md` — all rigorous, all negative:

* No periodic Vigenère / Beaufort / variant-Beaufort / Quagmire I–IV fits the cribs for any period
  2–25, over 7.09 million keyed-alphabet pairs. Period 26 is under-constrained (one constraint) and
  yields only chance hits that decrypt to gibberish.
* Porta, Gronsfeld, Trithemius/progressive, periodic+progressive: ruled out.
* Playfair, two-square, four-square, 5×5 bifid: ruled out (K4 uses all 26 letters; Playfair also fails
  on S→S, K→K and on doubled digraphs). 6×6 bifid and trifid with keyword squares: best 5/24.
* Hill 2×2 and 3×3, linear and affine, both directions, both alphabets, all alignments: zero
  solutions on every row. (So much for the extra L.)
* Monoalphabetic and affine: ruled out. Pure transposition: ruled out (the cribs need three E's, the
  ciphertext has two).
* Running key from every sculpture text (K1/K2/K3 plaintexts and ciphertexts, the whole left panel,
  the tableau both physical and ideal, the Morse text), forward/reversed/X-stripped, 24 alphabet
  combos, all 26 rotations: 0 exact hits, 0 within Hamming distance 2.
* Plaintext- and ciphertext-autokey, primer lengths 1–96: 0 survivors.
* Position-dependent shift models (linear, quadratic, cubic, triangular, sawtooth, block, row/column,
  bilinear, K2-coordinate Gronsfeld), 100M+ models: best fit 9/24.
* Transposition-then-substitution and substitution-then-transposition stacks; double periodic
  substitution: nothing above chance, and the few passing configurations decrypt to gibberish
  (quadgram ≈ −7.3 against English ≈ −5.3).

Standing rule for this project: **a survivor must fit 24/24 cribs *and* decrypt to English**, and any
hit count must be quoted against its chance expectation. A "hit" at the chance rate is not a result.
