# What Sanborn and Scheidt actually said about how K4 was encoded

A sourced, chronological dossier, 1988–2026, followed by the section that matters:
**[Cryptanalytic constraints implied](#part-iii--cryptanalytic-constraints-implied)**.

Compiled 2026-09-12. Backing arithmetic for the statistical claims:
`/Users/pravarkataria/Desktop/crypto/kryptos/analysis/sanborn_statements_stats.py`.

---

## How to read this file

Nearly everything "known" about K4's method is *reported speech about a 1988–1990
conversation between two men, one of whom says he has forgotten the details and the other
of whom says he was never told them.* Reliability varies enormously. Every item below
carries a tier:

| Tier | Meaning |
|---|---|
| **A** | Verbatim quote in a named, dated publication, read directly or from a faithful mirror. |
| **B** | Contemporaneous notes/paraphrase by a named attendee of a private event, or a quote reaching me only through a compilation. |
| **C** | Second-hand, undated, or a journalist's *characterisation* of a hint rather than a quote. Treat as weak. |
| **✗** | Widely repeated but **not** attributable to Sanborn or Scheidt. Listed in [Part IV](#part-iv--attributions-that-do-not-hold-up) so we stop citing it. |

Two standing warnings that Sanborn himself has issued:

> "It's not my intent to put out disinformation. I'm a benevolent cryptographer."
> — Sanborn, *Wired*, April 2009 (tier A)

> He "admitted he'd given contradictory statements over the years and said he liked to
> 'manipulate the information coming out, in a sort of disinformation fashion.'"
> — Sanborn at a 2005 Hirshhorn presentation, as recorded in LEMMiNO's reference #11 (tier B)

And the corresponding warning about Scheidt: he designed systems that Sanborn then
**altered without telling him**. Scheidt's statements describe the *design brief*, not
necessarily the *artefact*. This single fact is the most important thing in the dossier.

---

## Part I — Chronological dossier

### 1988–1990: design and installation

**1988–89 · Sanborn ⇄ Scheidt, the working relationship** (tier A, reported 2009)
Steven Levy, *Wired*, "Mission Impossible: The Code Even the CIA Can't Crack", Apr 2009:

> "Scheidt schooled Sanborn in cryptographic techniques employed from the late 19th
> century until World War II, when field agents had to use pencil and paper to encode and
> decode their messages… After experimenting with a range of techniques, including
> poly-alphabetic substitution, shifting matrices, and transposition, the two arrived at a
> form of old-school, artisanal cryptography that they felt would hold off code breakers
> long enough to generate some suspense. The solutions, however, were Sanborn's alone, and
> he did not share them with Scheidt."

Scheidt, same article:

> "I was reminded of my need to preserve the agency's secrets… You know, don't tell him
> the current way of doing business. And don't create something that you cannot break —
> but at the same time, make it something that will last a while."

Source: <https://itzmenu.wordpress.com/2009/05/11/mission-impossible-the-code-even-the-cia-cant-crack/>
(faithful mirror of the *Wired* text; wired.com is not directly fetchable).

**1989-12-15 · Sanborn, letter to CIA employees** (tier A)

> "This code, which includes certain ancient ciphers, begins as International Morse and
> increases in complexity as you move through the piece… The left side of the plate is a
> table for deciphering and enciphering code, developed by Blaise de Vigenere in 1570. The
> right side is a text that can be partly deciphered by using the table and **partly by
> using a potentially challenging encoding system**."

Note the split: *part* of the text is tableau-decipherable; the rest is something else.
Source: transcribed at <http://scirealm.org/KryptosHints.html>.

**1990-11 · Scheidt's expectations** (tier B)
Scheidt "figured that the first chunks of the puzzle would stand a few years; the last
part, perhaps ten" (*Washington Post*, 1999). Levy 2009 reports he expected the whole
puzzle solved "in less than seven years." Richard Bean (*The Conversation*, 2021-05-30)
reports Scheidt rated K4's difficulty "around nine out of ten" and that there was an
intentional **"change in the methodology"** as the sections progressed — Bean gives no
single primary citation for the 9/10 figure.
<https://theconversation.com/declassified-cold-war-code-breaking-manual-has-lessons-for-solving-impossible-puzzles-161595>

### 1991–1999: the early, glib period

**1991-04-02 · Sanborn, ABC *World News Tonight*** (tier A, transcript by Dunin/Zimolzak)

> "Once the plate is deciphered I'm not convinced the true meaning will be clear even
> then. There's another deeper mystery."

And from the same B-roll interview:

> "I've made a statement which is straightforward, but that leads to something else.
> There's another deeper mystery. As you peel off a layer of an onion… you get closer to
> the heart of what it is… **It's in English, it's in plain English, it's in text, and you
> can read it**, but that isn't necessarily the whole story."

This is the earliest first-person statement that the plaintext is plain English.
Source: <http://scirealm.org/KryptosHints.html>

**1992 · Sanborn, *Covert Obsolescence* exhibition catalog** (tier A)

> "The method of encoding and decoding that I use, called Vigenere Tableau, is ancient."

**1993 · *Secrets Passed* exhibition catalog** (tier B, curator's paraphrase)

> "Sanborn then worked with an ex-CIA cryptographer in developing methods for encoding the
> text, beginning with a chart developed in the 15th century by a French diplomat. **This
> cryptographer offered several options each of which could be modified so the final code
> would be known only to the artist.**"

The "modified so only the artist knows" formulation predates the Wired interviews by 12 years.

**1999 · Scheidt, *Washington Post*** (tier A)

> "I could use methods to encrypt it that had a historic basis, that didn't compromise any
> current methods" of cryptography used by the government.

> "The last 97 characters? Don't hold your breath… I saved the best for last."

**1999 · Sanborn, *New York Times*** (tier B)
"the sculpture contains a riddle within a riddle — one that will be solvable only after the
4 encrypted passages are known."

**1999 · Sanborn, NPR *All Things Considered*** (tier B)

> "There are encoding systems which use pattern, light and shadow, and it's those kinds of
> systems that I was most interested in using, because I'm an artist… and I chose not to
> use, in at least what's been deciphered already, **perhaps what has not been
> deciphered**… I like to use spatial systems of encoding and decoding."

The parenthetical is the single strongest hint that K4 is a *visual/spatial* construction
rather than a catalogued classical cipher.

**1999 · David Stein (CIA analyst, first solver), *New York Times*** (tier A — not the authors, but load-bearing)

> "The Kryptos puzzle is a layered puzzle… and we may find that it has layers within layers
> within layers."
> "Kryptos was meant to be solved with pencil and paper."

Scheidt to Stein after his 1998 briefing: *"the solution is correct, but you didn't do it
the way I intended you to do it."* (Stein had used frequency analysis instead of recovering
the keywords.) — *Washington Post*, 1999.

### 2003: the Elonka Dunin roadtrip — the "matrix" vocabulary appears

All tier **B** (Dunin's contemporaneous notes, with commentary by Gary Warzin, mirrored at
<http://scirealm.org/KryptosHints.html>).

**Sanborn:**
- He said it was odd that **"no one has recovered the original matrix"**. He kept using
  that word — **"matrix"**, **"matrix system"**.
- He thought Dunin's clean-diagonal K3 solution "must be **a by-product of the original
  matrix system**".
- **"He was surprised that no one had tried recovering the original matrix and running it
  through all the possible 'shifts'."**
- Scheidt did **not** do the encryption. Scheidt taught him various systems, "going back to
  Caesar", and he used "several" of them; the actual encryption was done by Sanborn
  himself, on the trip to retrieve the petrified tree. He and Scheidt agreed to keep it
  **"compartmentalized"**.
- Nobody beta-tested the code, "not even Scheidt", but Sanborn was certain he got it right.
- The misspellings were deliberate, but *what* they are matters less than **"the orientation
  of those letters"**; later in the evening he repeated that it was the **"positioning"**
  that was important. Of the out-of-alignment letters: **"They're important."**
- Declined to say whether the final "?" belongs to K3 or K4.

**Scheidt:**
- He talked about how **"it was necessary to recover the keys, and that the keys were
  concealed at the sculpture."**
- Part 4 **"is designed to be solved in a straight-forward manner with pencil and paper"**,
  and he did things to **"disguise the English"** in part 4, so that it couldn't be solved
  by the frequency analysis used on parts 1–3.
- He and Sanborn debated using an obscure language and **decided against it** as unfair.
- He said/implied he had built in **dead-ends** to throw people off.
- **"In a modern digital system, the 'key' is the keyword or number… In analog systems (as
  used in Kryptos) the 'key' is the algorithm."**
- **"Imagine that you have an operative in place that you will need to get a message to in
  the future… You have to assume that they will not remember the 'key'. How do you deliver
  a message in such a way that it conveys not only the encrypted data, but also the key?"**

### 2004–2005: the "masking technique" enters the record

**c. 2004-09-17/18 · Scheidt, a cryptography talk** (tier B, "unreliable source, but parts later confirmed directly")

> 1. On steganography: **"I used a bit of stego when designing the fourth part of Kryptos."**
> 2. **"In the first 3 parts, I gave anyone attempting to break the code the advantage of
>    the English language with all its known patterns, but I removed that advantage in the
>    fourth part."**

Scheidt's own subsequent clarification (tier A — his words, by email):

> "There were a string of questions for which I was focusing on how other folks did their
> analysis relying on the English language and resulting in three parts being decyphered.
> I did say that **in the last part the advantage of the language was taken away**. I also
> stated that **there was a piece relating to Stego, but did not state how or in what
> context**." — Ed Scheidt

**2005-01-20 · Sanborn, *Wired News*, interviewed by Kim Zetter** (tier A — full transcript)
<https://www.wired.com/2005/01/questions-for-kryptos-creator/> (mirror:
<https://kryptosfan.wordpress.com/the-continuity-of-kryptos/pr/questions-for-kryptos-creator-by-kim-zetter/>)

> **WN: Do you have to be on the CIA grounds in order to solve Kryptos?**
> **JS: No.**
> WN: So just by reading the text taken from Kryptos and posted online, you can solve the puzzle?
> JS: Well, yeah. That doesn't mean that what I've said in the piece doesn't do something
> physically there at the agency.

> **WN: How many (cryptographic) techniques did you use (in Kryptos)?**
> **JS: I would think five or six.**

> "Mr. Scheidt basically gave me an outline of historic and contemporary … encoding systems
> that have been formally used by the agency and were still used by the agency and other
> people (in 1990). **He gave me a whole variety of possible systems to use and ways to
> modify all of those systems.** But as a visual artist, I like to rely on systems that
> include visual (material) as well as digital material that can be deciphered by machines.
> **It's also well-known that I did use some matrix codes Ed gave me**, and I have also
> designed **visual systems for encoding, which are much harder for cryptographers to crack
> because they're individualistic**."

> "No, he doesn't know the solution. I made that very clear that I didn't want him to be
> able to decipher what's going on … **that I'd be modifying systems and developing my own,
> which would make it virtually impossible for him to decipher all of it.** I intended the
> 80 percent (of the text) that's been deciphered to be deciphered and to be deciphered in
> stages and relatively quickly. The final part is obviously the, you know, the apex of the
> pyramid there."

> "I will say that **I have left instructions in the earlier text that refer to later
> text**." … "if it can be deciphered exactly, **considering most of my things are rife
> with mistakes on purpose**".

> "I definitely didn't give him [Webster] the last section, which has never been deciphered."

**2005-01-21 · Scheidt, *Wired News*, interviewed by Kim Zetter** (tier A — full transcript)
<https://www.wired.com/2005/01/inside-info-on-kryptos-codes/> (same mirror as above)

> **WN: How many cryptographic processes are used on the sculpture?**
> **Scheidt: There are four different processes. Two of them are similar and the other two
> are different things. The first three processes were designed so that a person could,
> through cryptographic analysis, have access to the English language (on the sculpture).
> And the last process, I masked the English language so it's more of a challenge now. It's
> progressively harder in the challenges.**

> "All four (sections) are done in the English language. The message could have been in
> another language. (But) this particular puzzle is in the English language…. The techniques
> of the first three parts, which some people have broken, (used) frequency counting and
> other techniques that are similar to that. You can get insight into the sculpture through
> that technique because **the English language is still visible through the code**. (But
> with) this other technique (in the fourth part), **I disguise that. So … you need to solve
> the technique first and then go for the puzzle.**"

> **WN: Are all four of the processes known processes? There aren't any that aren't known, right?**
> **Scheidt: The masking technique may not be known.**
> WN: What do you mean?
> Scheidt: **That's part of the puzzle I told (Jim) I would keep secret.**

> WN: Jim said that he took your techniques and then he deliberately masked them even more
> so that even you wouldn't know what was in the puzzle.
> Scheidt: **"Ah hah. I can't respond to that one. I haven't heard him say that before. It's
> possible I guess. I haven't talked to Jim on what he did, but I do know … there was some
> masking techniques that were used and that's about it."**

> "Well, the idea of encoding a message is not only to encode the externals of a message
> (the English language), but the message itself. Once it is readable, **it may have other
> encoding that's involved in it**." [the "cake = 1 o'clock Friday" analogy]

> **"I think there are 98 characters left.** That's not a lot of characters. It's a question
> of how would you approach it? Would you approach it mathematically? Would you approach it
> in the context of secret writings or symbols?"

**2005-05-27 · *Wall Street Journal*, p. A1** (tier C for the method line, tier A for the quote)

> "Experts say the fourth passage — known to insiders as 'K4' — is written in a more complex
> and difficult code than the first three, **one designed to mask patterns of recurring
> letters that code breakers look for**." (journalist's characterisation)

> Sanborn: **"The most obvious key to the sculpture, nobody has picked up on."**

**2005-06-09 · NPR *Morning Edition*, Mary Louise Kelly** (tier B)
Scheidt:

> "In the 1st 3, you could rely on the fact that, in English, some letters occur more
> frequently than others… because there are more E's in English language than there are
> Z's… **in part 4, (I) deliberately masked that advantage.**"

Sanborn: "I don't really believe I gave them the entire code, so… if it was a deception on
my part, hey, so be it." He nodded when asked whether all four passages link together, and
said whoever cracks part 4 will then be **at the beginning of the puzzle**.

**2005-06-19 · Sanborn, CNN (David Ensor)** (tier A — CNN transcript)

> "Ed Scheidt, the cryptographer who I worked with, who's retired from the agency, **gave me
> an overview of encoding systems, and worked with me**. We met in secret locations at the
> time… **Then he gave me the systems. I was able to modify them to my own ends.**"

> "Let's just think of the last passage of the 'Kryptos' as being like sand in an hourglass.
> At this point in time, **every little grain of sand that leaves that hourglass is a clue**…
> I was very glib in 1990, '94… I am far less glib now."

**2005 · Two private post-convention dinners** (tier B, notes by Chris "Xenon" Hanson,
Elonka Dunin and John Wilson, catalogued as LEMMiNO refs #11 and #24)
- Sanborn said K4 is **"approximately a hundred characters"** and refused to be more specific.
- Asked whether the final "?" is a question mark or a piece of code: **"It's a question mark."**
- **Neither Sanborn nor anyone else "has done a reverse check to make sure the code for K4
  works."** Scheidt, separately, said he is **"confident that [K4] was done correctly."**

### 2006: the LAYERTWO correction

**2006-04-19/20 · Sanborn to the Yahoo Kryptos group; reported by Kim Zetter, *Wired*,
"Typo Confounds Kryptos Sleuths", 2006-04-20** (tier A/B)

Sanborn went through his notes and found that the accepted K2 ending "ID BY ROWS" was wrong:
he had **omitted an S from the carved ciphertext (an X in the plaintext) after "WEST"**, for
**"aesthetic reasons, to keep the sculpture visually balanced."** With the letter restored,
K2 ends **"…WEST X LAYER TWO"**.

In the same commentary he stated that **the answers to the first three passages contain clues
to the fourth passage**. This is the primary citation for the "K1–K3 plaintexts are clues to
K4" claim, and it is the only place Sanborn says it on the record.
<https://www.wired.com/2006/04/typo-confounds-kryptos-sleuths/>

Two things follow that are often forgotten:
1. The carved ciphertext is **demonstrably not a faithful record of the encipherment** — one
   letter is missing on the K2 side, by the artist's own admission, and the same could be
   true of K4.
2. Scheidt, at the 2013 ACA convention, cast doubt on even this: "**The ID BY ROWS /
   LAYERTWO error may not have been a mistake after all. Sometimes in spycraft you
   deliberately do these things.**" (tier B, via "ENDEAVOUR",
   <https://kryptosfan.wordpress.com/2013/10/30/more-about-ed-scheidts-aca-talk/>)

### 2009: the Smithsonian oral history and the Levy profile

**2009-07-14/16 · Sanborn, oral history interview, Archives of American Art, Smithsonian
(interviewer Avis Berman)** (tier B — the transcript itself is tier A but is now behind a
403 and the relevant passage reaches me only via quotation)

> "And Ed basically gave me — **he gave me a primer of ancient encoding systems**. And he
> also gave me some ideas for contemporary coding systems, more sophisticated systems,
> **systems that didn't necessarily depend on mathematics. That was one of my prerequisites.**
> So he told me about **matrix codes** and things like that. These are the parts of Kryptos
> that have already been cracked. So I can discuss them. But he told me about **coding
> systems that I could then modify in a myriad of ways. So that even he would not know what
> it says.** Okay? So that was very seductive to me. And so I took those things. We met two
> or three times. And that's what I based the whole thing on."

Quoted at <https://rumkin.com/reference/kryptos/k4/>; the opening clause is independently
quoted by Klaus Schmeh, *Cipherbrain*, 2020-07-22,
<https://scienceblogs.de/klausis-krypto-kolumne/2020/07/22/a-6-5-hour-interview-with-kryptos-creator-jim-sanborn/>.
Record link: <https://www.aaa.si.edu/collections/interviews/oral-history-interview-jim-sanborn-15700>

Note the precise scoping: "matrix codes … **these are the parts of Kryptos that have already
been cracked**." By his own account the matrix codes are K1–K3, not K4.

**2009-04 · Levy, *Wired*** (tier A for quotes, **tier C** for the sidebar)
Sidebar, written by *Wired*, not by Sanborn:

> "Sanborn intentionally made K4 much harder to crack, **hinting that the plaintext itself
> is not standard English and would require a second level of cryptanalysis**. Misspellings
> and other anomalies in previous sections may help."

This sentence is the origin of the widespread belief that K4's plaintext is not plain
English. It is a journalist's gloss on a hint, it directly contradicts Sanborn's 1991 "it's
in plain English", and it should be weighted accordingly.

Scheidt, same article: **"There may be more to the puzzle than what you see… Just because
you broke it doesn't mean you have the answer."**
Sanborn: "I haven't looked at the plaintext of K4 in a long time, and I don't have a very
good memory, so I don't really know what it says."

**2009-08 · Sanborn video interview** (tier C, blogger's paraphrase)
Sanborn says solvers have "everything we need at Antipodes" and don't need "environmentals";
also that K4 starts with the "?".
<https://kryptosfan.wordpress.com/2009/08/04/sanborn-interview/>

### 2010: BERLIN

**2010-11-20 · Sanborn to John Schwartz, *New York Times*, "Artist releases clue to Kryptos"** (tier A)
Ciphertext **NYPVTT** at positions **64–69** decrypts to **BERLIN**.
<https://www.nytimes.com/2010/11/21/us/21code.html>
NPR follow-up 2010-11-22: <https://www.npr.org/2010/11/22/131520768/-kryptos-sculptor-drops-new-clue-in-20-year-mystery>

Alongside the clue the NYT published photographs of **Sanborn's original handwritten
encoding charts** for K1 and part of K2 — the "matrix" in physical form.
<https://www.nytimes.com/2010/11/21/us/21codecharts.html>
Sanborn later said that if those charts were studied **"in a forensic manner, there might be
revelations in there."** (tier B, LEMMiNO ref #45)

### 2013: the ACA convention — the most technically informative event on record

American Cryptogram Association convention, Norfolk VA, 2013-08-23/25. Scheidt was the
banquet speaker (he refused to be recorded); Sanborn joined a post-convention dinner Q&A.
All tier **B**, from an attendee's notes published 2013-10-28,
<https://kryptosfan.wordpress.com/2013/10/28/kryptos-notes-from-the-aca-convention/>

- Asked whether N decodes to B, Y to E, etc., **Sanborn confirmed it does. Emphatically.**
  He "rattled through the entire crib": N=B, Y=E, P=R, V=L, T=I, T=N.
- Asked whether N **decodes** to B or **encodes** to B, **Sanborn stated "decodes."**
- When the same question was put to Scheidt, **Sanborn cut in: "I'm the only one who knows."**
- Asked whether K4 was a **"one-off"**: Scheidt looked at Sanborn and said "well Jim, how are
  we going to answer that one?" Sanborn: **"we don't answer it."**
- Dunin reminded Scheidt that he had once told her **Kryptos uses "a system unknown to anyone
  on the planet."** Scheidt "stated he didn't recall that conversation, and back-pedaled out
  of saying anything more."
- Asked whether something was buried on CIA grounds: **"Yes, there is something buried
  adjacent to Kryptos… The thing that was buried is a bronze USGS marker. It was half
  buried. It had little cross hairs on the top of it."** It had been removed by ~2011, "but
  it is important."
- **Q: can we solve K4 without solving K1–K3 first? Sanborn: "Yes, but K5 cannot be solved
  without K4."**
- Sanborn "still believes there's something to be gained if we study his encryption charts
  that he released to the *New York Times*"; he "brought up his K1/K2 matrix and seemed
  mystified no one has gotten anything more from it."

From Scheidt's own Q&A (tier B, second-hand via "ENDEAVOUR"):
- **"After part IV is decrypted, the next thing to figure out is how the receiver's identity
  is kept hidden. Ed said that this was built into the process, but gave no clues as to how
  it is done."**
- The LAYERTWO "error" may have been deliberate (quoted above).

**2013 · Sanborn, TNG Big Techday 6 talk** (tier C, blogger's summary)
"He really liked doing the encryption in **handwritten spreadsheets as 'matrixes'**… He
really liked K1 and K2 encryption but K3 was all about just randomly turning and rearranging
the letters. He indicates that it starts with the question mark. And he **alludes again to
visual encryption systems**."
<https://kryptosfan.wordpress.com/the-continuity-of-kryptos/pr/sanborns-tng-big-techday-6-talk/>

**2013 · 97 or 98?** (tier B, LEMMiNO ref #42d) Asked whether K4 is 97 or 98 characters long,
Sanborn responded: **"Try both."**

### 2014: CLOCK

**2014-11-20 · Sanborn to John Schwartz, *New York Times*** (tier A)
Ciphertext **MZFPK** at positions **70–74** decrypts to **CLOCK**. Note that position 74 is
**K → K**: a letter enciphers to itself, which rules out the Enigma-style "no self-encipherment"
family.

> **"You'd better delve into that particular clock."** … **"There are several really
> interesting clocks in Berlin."**

<https://www.nytimes.com/2014/11/21/us/another-kryptos-clue-is-offered-in-a-24-year-old-mystery-at-the-cia.html>

### 2019–2020: EAST, NORTHEAST, and the collapse of the "1:1" assumption

**2019-03 · private "Kryptos dinner", notes by Elonka Dunin** (tier B) — **critically important**

> "We spent quite a bit of time asking Jim about the correlation between the plaintext
> BERLIN and the ciphertext such as NYPVTT. Specifically, we were trying to find out if
> there was a 1:1 relationship from NYPVTT to BERLIN, or there was some other step, **the
> masking technique. Jim was confused when we mentioned masking technique, evidently it's
> something that Ed said that Jim didn't understand.** Jim said that yes the ciphertext and
> plaintext were connected, but when I tried to explain what exactly we were asking, like
> that in K1 EMUFPH is exactly BETWEE, but in K3 ENDYAH does not map exactly to SLOWLY,
> **Jim backed off and said he would only commit to the fact that K4 is exactly 97
> characters long, and that BERLIN is plaintext that starts at exactly the 64th character,
> but he wouldn't go further than that.**"

<https://rumkin.com/reference/kryptos/k4/>

This is the confusion the task brief refers to, and it cuts two ways:
- **The author of K4 does not recognise the term "masking technique."** It is Scheidt's
  word for Scheidt's *design*, and Sanborn built the thing. Any model that treats "masking"
  as a named, specific operation Sanborn applied is building on sand.
- **Sanborn walked back the 1:1 claim he had made emphatically in 2013.** After 2019 the
  defensible statement is only: *K4 is 97 characters and BERLIN's B sits at position 64.*
  See constraint **C2**.

**2020-01-29 · Sanborn to John Schwartz and Jonathan Corum, *New York Times*** (tier A)
Ciphertext **QQPRNGKSS** at positions **26–34** is **NORTHEAST**. Presented as the third and
final clue.
<https://www.nytimes.com/interactive/2020/01/29/climate/kryptos-sculpture-final-clue.html>

**2020-01-30 / 2020-02-06 · Sanborn, NPR *All Things Considered*, Mary Louise Kelly** (tier A)

> KELLY: Why give us a new clue now?
> SANBORN: "Well, it is very close – within days – to when I actually **developed that
> 97-character string**. The dedication ceremony is actually not until November, but
> obviously prior to the dedication, I had to come up with the final clue section."

> KELLY: …you told me you're pretty lousy at math.
> SANBORN: "I am lousy at math to the point where I consider myself to be an analpha-math.
> Now, **perhaps being an artist, I have an advantage in that I can employ methods that
> don't have anything to do with mathematics.**"

> "**It's a 97-character phrase. And that phrase is in itself a riddle. It's mysterious.
> It's going to lead to something else. It's not going to be finished when it's decoded.**"

> "I really do want Kryptos to remain secret – the plain text, the final section of Kryptos,
> I would prefer for it to remain secret indefinitely."

<https://www.npr.org/2020/01/30/801323608/a-new-and-final-clue-to-kryptos-a-long-standing-puzzle>
(quotes transcribed at <https://inteltoday.org/2022/02/06/two-years-ago-kryptos-sculpture-jim-sanborn-this-is-the-third-and-to-be-sure-final-clue-update-and-then-came-a-4th-clue/>)

**2020-04 → 2020-08-24 · EAST** (tier A/B)
Despite calling NORTHEAST final, Sanborn released **FLRV** at positions **22–25** = **EAST**
privately in April 2020, through the paid submission system he uses to filter enquiries; it
surfaced publicly in August. John Schwartz, @jswatz, 2020-08-24:
<https://twitter.com/jswatz/status/1297658577914667008>

Sanborn, by email, on whether it was inadvertent: **"I don't do much that's inadvertent."**
And: **"I released this layout to several people as early as April … to spice things up
during this unpresidented [sic] time and to see how long it would take to flow through the
community, and frankly I was a tad bored."**

**2020-07-25 · Sanborn, CNN** (tier A, via secondary)
On Scheidt: they met "more or less in secret"; **"He educated me on the subject of code,
modern codes, contemporary coding systems — at least contemporary in '88."**

### 2025–2026: the auction, the archive leak, and K5

**2025-08-14 · Sanborn, open letter to the Kryptos community, published via the
*Washington Post*** (tier A, via Wikipedia's quotation of the WaPo piece)

> "I no longer have the physical, mental or financial resources to maintain the 97-character
> K4 code section of my sculpture and continue my other projects."
> "If they don't then (CLUE) what's the point? … **Power resides with a secret not without it.**"

He confirmed **the existence of K5**, to be revealed after K4 is solved.
<https://www.washingtonpost.com/entertainment/art/2025/08/14/kryptos-code-k4-solution-jim-sanborn-auction/>
· open letter mirrored at <https://www.elonka.com/kryptos/OpenLetterAug2025.html> (site is
behind a bot-challenge; not directly fetchable)

On the sculpture's carving, asked about the K2 omission (NYT, 2025-08-14):
> **"You could not make any mistake with 1,800 letters. It could not be repaired."**

**2025-09-02 · the Smithsonian archive discovery** (tier A)
Jarett Kobek and Richard Byrne found five pages of scrambled text in Sanborn's papers at the
Archives of American Art and reassembled what is very likely the K4 plaintext. Sanborn
confirmed its accuracy and had the files sealed until 2075.
<https://www.nytimes.com/2025/10/16/science/kryptos-cia-solution-sanborn-auction.html>
· <https://www.scientificamerican.com/article/a-solution-to-the-cias-kryptos-code-is-found-after-35-years/>

Sanborn (tier A, RR Auction):
> **"What they found was scrambled text, and not by solving the cryptogram. They did not
> solve K4."**
> **"K4 has not been solved. K4 has been discovered and it points in the direction of K5."**

Kobek: **"There's no way on earth that this is a cryptographic solve."**
Dunin: **"One thing is to have the words. It's another to have the method. If they don't
have the method, it's not solved."**
<https://content.rrauction.com/kryptos-k4-discovered-not-solved-heres-what-actually-happened/>

**2025-10-16 → 2025-11-20 · RR Auction lot description** (tier A — primary, from the seller)
"The Complete Secrets of Kryptos: Jim Sanborn's Private Archive", 17 items, including:
1. Original handwritten K4 plaintext **with a signed letter from cryptographer Ed Scheidt**
2. **The original K4 coding system**
3. Handwritten signed plaintexts used for screen-cutting K4
4. **The original coding charts used to create K1, K2 and K3**
5. Unpublished **1988 alternate K1 plaintext and coding chart**
6. **Unpublished 1988 alternate K4 plaintext and coding chart — "now known as K5"**
7. The original scrambled texts shown to the Department of Historical Intelligence
8. A private session with Sanborn explaining "the relationship between K4 and K5, and what
   the complete message truly means"

No photographs of items 1–7 were published. Sold 2025-11-20 for **$962,500**.
<https://www.rrauction.com/auctions/lot-detail/350761607302001-the-complete-secrets-of-kryptos-jim-sanborns-private-archive/>

**2025-11-12 · Sanborn, International Spy Museum, reported by Dan Vergano, *Scientific
American*** (tier A) — **the most substantive method statement since 2005**

> **"Kryptos has not been solved."** … **"K4 has not been solved or decrypted."**
> "It's sort of my last chance to impart information about what the new owner — or, as I
> call it, **the Kryptos keeper** — is going to be able to say and do after it's transferred."

Asked by *Scientific American* about the mathematics of the K4 solution he joked:
> **"Who says it is even a math solution?"**
> **"I was fortunate not to understand mathematics, probably in my ability to make the code."**

He counselled **"creativity"** to anyone seeking the decipherment key, and in a new open
letter to the Kryptos community announced **four clues**:
1. **Two events figure in the solution: a 1986 trip Sanborn took to Egypt, and the 1989 fall
   of the Berlin Wall.**
2. **The "BERLINCLOCK" of the earlier clues refers to the World Clock (Weltzeituhr,
   Alexanderplatz) in Berlin** — *not* the Mengenlehreuhr that solvers had assumed for a
   decade.
3. **The codes within Kryptos are about "delivering a message".**
4. **K5 is thematically connected to the K2 text "its buried out there somewhere."**

And on K5's structure:
> "The new code will involve elements of the other puzzles and, **like K4, will be 97
> characters long. Both 97-letter messages will share some of the same coded words in the
> same position.**"

<https://www.scientificamerican.com/article/cia-kryptos-puzzle-creator-releases-final-clues/>

**2026-06-12 · Paradigm** (tier A)
The anonymous winning bidder was Paradigm, a San Francisco investment firm. They deliberately
never looked at the plaintext: Sanborn typed it into an isolated laptop, a program ran it
through SHA-256, Google Cloud KMS produced an HMAC verification tag, and the laptop was
wiped. Submissions cost $1. Sanborn also gave them **the ciphertext of K5**, which Paradigm
"plan to release … in the future".
<https://www.paradigm.xyz/writing/kryptos> · <https://www.paradigm.xyz/kryptos/k4>
· *New York Times*, "They Bought a Famous Puzzle in Cryptography. Now They're Opening It Up.",
2026-06-12

---

## Part II — The threads, condensed

| Thread | Best evidence | Net position |
|---|---|---|
| **"Masking technique"** | Scheidt, Wired 2005-01-21; NPR 2005; his own 2004 email | Scheidt's term for *his design goal* — flatten the English signal so frequency counting fails. He said the technique "may not be known" and that he promised Sanborn to keep it secret. **Sanborn did not recognise the term in 2019.** |
| **"Matrix"** | Sanborn 2003 roadtrip; Wired 2005; AAA 2009; Big Techday 2013 | In Sanborn's vocabulary **"matrix" = the hand-drawn coding chart/spreadsheet**, not linear algebra. He explicitly scopes "matrix codes" to K1–K3. "No one has recovered the original matrix" is his most repeated complaint. |
| **Primer of systems / modification** | Wired 2005; CNN 2005; AAA 2009; *Secrets Passed* 1993 | Scheidt gave an outline of historic + contemporary systems **plus "ways to modify all of those systems"**, explicitly so that Scheidt himself could not decipher the result. Consistent across 16 years and four independent tellings. |
| **English / frequency flattening** | Scheidt, Wired 2005 + NPR 2005 + 2004 email | All four sections are English. K1–K3 leak the English; K4 does not. "Solve the technique first, then the puzzle." |
| **K4 ≠ K1–K3 system** | Scheidt, Wired 2005: "four different processes; two similar, the other two different" | K1≈K2 (Vigenère). K3 and K4 are each different again. |
| **Sculpture needed?** | Sanborn, Wired 2005: "No." Also 2009: "everything we need at Antipodes" | The *cipher* is solvable from the published transcription. The *meaning* points to a physical place (a USGS marker, since removed). |
| **97 vs 98** | 2005: "approximately a hundred"; 2005 Scheidt: "98"; 2013: **"Try both"**; 2019: "exactly 97"; 2025: K5 also 97 | Post-2019 Sanborn has consistently said 97. Earlier ambiguity concerned whether the "?" belongs to K3 or K4. |
| **Plaintext = a riddle** | 1991 ABC; 1999 NYT; 2005 Wired/CNN; NPR 2020 | Decrypting K4 yields a 97-character phrase that is "in itself a riddle" and "leads to something else". Expect the output to be terse, referential and possibly not fluent prose. |
| **K5** | ACA 2013; Sanborn Aug 2025; SciAm Nov 2025; RR lot | Real, 97 characters, the **unpublished 1988 *alternate K4* plaintext + chart**; shares coded words with K4 **at the same positions**; ciphertext now held by Paradigm and slated for release. |

---

## Part III — Cryptanalytic constraints implied

Each constraint gives the statement, its **testable form**, and its **status** against the
work already completed in this repository (`findings/families.md`, `findings/runningkey.md`,
the geometry and two-cipher suites).

Legend: ✅ tested and closed · 🟡 partially tested / tested only under an assumption that the
statements now undermine · ⬜ untested.

---

### Group 1 — Constraints that the completed work has already discharged

**C1 — The plaintext of all four sections is English.**
*Source:* Scheidt, Wired 2005-01-21 ("All four (sections) are done in the English language");
Sanborn, ABC 1991 ("it's in plain English"). They explicitly **rejected** using an obscure
language as unfair (Scheidt, 2003).
*Testable form:* any candidate decryption must be English (see C8 for how loosely).
✅ Used as the scoring criterion throughout. **No further work needed — but see C8, which
says the threshold used so far is too strict.**

**C2 — The four anchors sit at fixed positions 22–25, 26–34, 64–69, 70–74.**
*Source:* the 2010/2014/2020 clue releases; Sanborn, ACA 2013 (N=B, Y=E, P=R, V=L, T=I, T=N,
"decodes"); Sanborn, 2019 dinner (would commit only to "97 characters" and "BERLIN starts at
exactly the 64th character").
*Testable form (strong reading):* K4 is position-preserving; ciphertext letter *i* maps to
plaintext letter *i*.
*Testable form (weak reading, the only one Sanborn still stands behind):* the plaintext words
occupy those index ranges; nothing is claimed about the mapping at other indices.
✅ Every completed suite assumes the strong reading, which is why pure transposition is
excluded (the anchors require three E's and K4's ciphertext has two).
🟡 **The weak reading has never been tested.** See C12 and C13.

**C3 — K4 uses a different process from K1, K2 and K3.**
*Source:* Scheidt, Wired 2005: "There are four different processes. Two of them are similar
and the other two are different things"; "progressively harder"; the 1989 letter's "partly by
using a potentially challenging encoding system"; Scheidt's "change in the methodology".
*Testable form:* K4 is neither a Vigenère/Quagmire on the KRYPTOS tableau with a short key,
nor a pure transposition.
✅ Closed on both halves. Note the alternative reading — that K3 and K4 are the "two similar"
pair, making K4 transposition-based — **is already refuted** by the E-count argument.

**C4 — The method is executable and breakable with pencil and paper, by a man who says he
cannot do mathematics.**
*Source:* Scheidt 2003 ("designed to be solved in a straight-forward manner with pencil and
paper"); Scheidt on NOVA ("I set the codes up for him, which means that he didn't have to know
the mathematics of it"); Sanborn NPR 2020 ("methods that don't have anything to do with
mathematics"); Sanborn Nov 2025 ("Who says it is even a math solution?", "I was fortunate not
to understand mathematics").
*Testable form:* exclude schemes requiring modular inverses, matrix algebra, or arithmetic
beyond table lookup and letter counting.
✅ Hill 2×2/3×3 (linear and affine, both directions, both alphabets, all alignments) is
closed — and it was always the family this constraint most disfavoured. The extra "L" in
tableau row N spelling HILL down the last column is a coincidence Sanborn **omitted from the
scale models he sells**, which argues against it being a deliberate pointer.
*Corollary:* deprioritise any future family that a non-mathematician could not execute by
hand on a sheet of paper.

**C5 — It is not a true one-time pad.**
*Source:* Scheidt's brief to himself — "don't create something that you cannot break — but at
the same time, make it something that will last a while" (Wired 2009); his ~9/10 difficulty
rating and 5–10 year expectation.
*Testable form:* the keystream is reconstructible from public material.
✅ The obvious reconstructible pads (all sculpture texts, both panels, the tableau, the Morse,
forwards/reversed/X-stripped, 24 alphabet combos × 26 rotations) are closed.
⚠️ **Caveat that weakens this constraint badly:** Scheidt's guarantee covers *his* design.
Sanborn says he modified the systems "so that even he would not know what it says", and
**nobody ever ran a reverse check on K4** (2005 dinner notes). Scheidt's breakability promise
may simply not apply to the artefact.

---

### Group 2 — Constraints the statements imply that are **untested**, ranked by value

**C6 ⬜ — Tolerate encoding errors. HIGHEST VALUE, CHEAPEST TO RUN.**
*Source:* Sanborn omitted a letter from K2's carved ciphertext for aesthetic reasons (2006,
his own admission); **"neither Sanborn nor anyone else has done a reverse check to make sure
the code for K4 works"** (2005 dinner notes, Dunin/Wilson); "You could not make any mistake
with 1,800 letters. It could not be repaired." (2025); Scheidt said he *built in dead ends*
(2003).
*Testable form:* re-run the large family sweeps requiring **22/24 or 23/24** crib agreement
instead of 24/24, and report survivors against the correspondingly inflated chance
expectation.
*Status:* the running-key suite checked Hamming ≤ 2 and found nothing. **The 7.09-million-pair
Quagmire sweep, the 100-million-model position-dependent shift sweep, the digraphic suite and
the two-cipher suites all demanded exact 24/24 fits.** If a single carved letter in K4 is
wrong, every one of those negatives is void.
*Chance bookkeeping to state alongside results:* allowing *k* mismatches multiplies the
number of passing random keys by roughly `C(24,k)·25^k`, i.e. ×600 for k=1 and ×1.7×10⁵ for
k=2. For the tightly-constrained periods (2–13, expected survivors < 2×10⁻⁹) this is still
comfortably below 1, so a k≤2 sweep of those periods remains a meaningful test. For periods
≥ 24 it is not.

**C7 ⬜ — Alphabet constructions other than simple keyword-mixed.**
*Source:* "matrix", "matrix system", "handwritten spreadsheets as matrixes", "It's also
well-known that I did use some matrix codes Ed gave me", "no one has recovered the original
matrix and [tried] running it through all the possible shifts."
*Testable form:* `families.md` explicitly records as **not tested**: "non-keyword alphabet
constructions (columnar-transposed keyword blocks, decimated alphabets, reversed alphabets)".
Columnar-transposed keyword blocks are the standard ACA construction for Quagmire mixed
alphabets and are exactly what a hand-drawn chart produces. Decimated alphabets likewise.
*Status:* ⬜ named gap. Re-run the Quagmire I–IV sweep with (a) columnar-transposed keyword
alphabets (keyword written into a block of width 2–10, read off by transposed column order),
(b) decimated alphabets (step *d* coprime to 26, 12 non-trivial values), (c) reversed variants
of every alphabet. This roughly quadruples an already-cheap sweep (14 s on 8 cores).

**C8 ⬜ — Loosen the English criterion; the plaintext is a riddle, not prose.**
*Source:* "that phrase is in itself a riddle… it's going to lead to something else" (NPR
2020); "once it is readable, it may have other encoding that's involved in it" (Scheidt,
Wired 2005 — the "cake" analogy); "just because you broke it doesn't mean you have the
answer" (Scheidt, 2009); "most of my things are rife with mistakes on purpose" (2005); three
confirmed deliberate misspellings in K1–K3; the anchors themselves are a **compass bearing**
(EAST NORTHEAST) and a **place name** (BERLIN CLOCK).
*Testable form:* a correct 97-character K4 plaintext could easily score −6.5 or worse on
English quadgrams — it may contain a bearing, a proper noun, a coordinate, a misspelling and
a terminal marker. Any pipeline that rejects candidates below a prose-like quadgram threshold
can throw away the answer.
*Status:* ⬜ The completed suites applied the quadgram filter only to candidates that were
already at chance level, so no past conclusion is affected — but **every future search must
report the top N candidates by crib fit regardless of English score**, and score them on a
"K4-like" model (anchors + bearings + proper nouns) rather than newspaper English.

**C9 ⬜ — The 1986 Egypt trip and the 1989 fall of the Berlin Wall are in the solution.**
*Source:* Sanborn's November 2025 open letter, clue 1, reported by *Scientific American*
2025-11-12. Clue 2 fixes BERLINCLOCK as the **Weltzeituhr at Alexanderplatz** — the square
where the crowds gathered before the Wall fell — not the Mengenlehreuhr.
*Testable form:* a semantic crib-drag. Under the strong positional reading (C2), for each
candidate word *w* from the field {WALL, NOVEMBER, NINETEEN, EIGHTYNINE, GATE, BRANDENBURG,
ALEXANDERPLATZ, WELTZEITUHR, WORLDCLOCK, TOMB, VALLEY, NILE, LUXOR, KARNAK, CARTER, SAND,
DESERT, PYRAMID, SHADOW, COMPASS, LODESTONE, MERIDIAN, LATITUDE, MARKER, CROSSHAIRS} and each
offset, compute the required key letters and test them for consistency with the 24 known
pairs under each cipher family. Words that place without contradiction are new anchors.
*Status:* ⬜ never run. Cheap, high information, and it is the only lane in which the 2025
clues have any operational content. **This is the highest-value new experiment created by the
2025 disclosures.**

**C10 ⬜ — K5 gives depth. Watch for its release.**
*Source:* RR Auction lot item 6, "unpublished 1988 alternate K4 plaintext and coding chart
now known as K5"; Sanborn, SciAm 2025-11-12: K5 is "97 characters long" and **"both 97-letter
messages will share some of the same coded words in the same position"**; Paradigm 2026:
"Sanborn provided the ciphertext for another 97-character puzzle, known as K5… we plan to
release K5 in the future."
*Testable form:* if K4 and K5 are position-preserving encipherments of two different
97-character plaintexts under the **same or nearly the same chart**, then for a Vigenère-type
system the key cancels outright:
`idx(C4ᵢ) − idx(C5ᵢ) = idx(P4ᵢ) − idx(P5ᵢ) (mod 26)`
and the shared words at shared positions give stretches where that difference is **zero**.
That is classical depth-2, and it would be by far the most powerful attack ever available on
K4 — stronger than all four cribs combined.
*Status:* ⬜ blocked on publication. **Concrete action:** monitor
<https://www.paradigm.xyz/kryptos/k4> for the K5 ciphertext. The moment it appears, compute
the position-wise difference stream against K4 and look for runs of zeros; each zero-run
localises a shared coded word and, under a Vigenère/Quagmire model, the runs alone may
recover the alphabet ordering.
*Corollary already usable now:* the 97-character length was fixed **in 1988, for a chart that
predates the final plaintext**. 97 is a property of the *worksheet*, not of the message. On
the panel, 97 = 4 + 31 + 31 + 31. Worksheet geometries worth modelling: 97 cells laid out as
4 + 3×31, or as a grid whose row length is 31.

**C11 ⬜ — The tableau side is "layer two", read by coordinate, not in reading order.**
*Source:* the corrected K2 ending is **"X LAYER TWO"** (Sanborn, 2006); "the keys were
concealed at the sculpture" and "how do you deliver a message in such a way that it conveys
not only the encrypted data, but also the key?" (Scheidt, 2003); "the answers to the first
three passages contain clues to the fourth passage" (Sanborn, 2006).
*Testable form:* `runningkey.md` tested the tableau (physical, with the anomalous L, and
ideal) as a **running key in reading order** with 26 rotations and 24 alphabet combos — 0
hits. It did **not** test the tableau as a **positional lookup**: helper letter for K4
position *i* = `tableau[row(i)][col(i)]`, where (row, col) is derived from where character *i*
sits on the 31-wide left panel, or from the ciphertext letter itself (`tableau[C_i][col]`),
or from the plaintext/ciphertext pair as a coordinate. This is precisely how a Vigenère
tableau is used by hand and precisely what "layer two" would name.
*Status:* ⬜ untested family. Enumerate a modest space: row index ∈ {position mod 31,
position mod 26, letter index of Cᵢ, letter index of Cᵢ₋₁, panel row}, column index ∈
{position mod 31, position mod 26, letter index of Cᵢ, constant}, combined with the 24
alphabet/family combos already implemented. Chance expectation for each combo is the usual
26⁻ᶜ bookkeeping; report it.

**C12 ⬜ — Nulls / "a bit of stego", confined to the non-anchor regions.**
*Source:* Scheidt, 2004: "I used a bit of stego when designing the fourth part of Kryptos",
confirmed in substance by his own email ("there was a piece relating to Stego, but did not
state how or in what context").
*Testable form:* the four anchors occupy **22–34 (13 contiguous)** and **64–74 (11
contiguous)**. Any null-dropping or letter-selection scheme must leave those two blocks
intact and contiguous. That leaves exactly three regions where nulls may live: **1–21, 35–63,
75–97**. A scheme that, say, drops every *k*-th letter outside the anchors, or reads only the
letters at panel positions satisfying some geometric predicate, is compatible with every
public statement and has never been searched.
*Status:* ⬜ untested. This is the natural home for the **weak reading of C2** and for
Sanborn's "spatial systems of encoding and decoding" / "pattern, light and shadow".

**C13 ⬜ — An indicator group: "how the receiver's identity is kept hidden… was built into
the process."**
*Source:* Scheidt, ACA 2013 Q&A. Plus his standing operative-in-the-field framing (2003):
the message must carry its own key.
*Testable form:* in period field ciphers the addressee and the key are both named by an
**indicator group** at the head of the message. K4's physical layout is **4 + 31 + 31 + 31**:
`OBKR` sits alone on its line, above the "?" that ends K3. Model K4 as **4-letter indicator +
93-letter message**, where OBKR *selects* a key/alphabet/starting offset from an enumerable
set rather than *being* the key.
*Status:* ⬜ `geometry_2_obkr.py` tested OBKR **as** a period-4 key and **as** an autokey
primer (best 4/24). It did not test OBKR as a **selector**. Concretely: for each of the 24
alphabet/family combos, treat O, B, K, R as four independent indices (row, column, alphabet
id, starting rotation) into the tableau or into the coding chart, and enumerate. Small space,
directly motivated, never run.

**C14 ⬜ — The out-of-alignment letters and the misspellings, as *positions* not as *words*.**
*Source:* Sanborn, 2003: of the out-of-alignment letters, **"They're important"**; on the
misspellings, "it's more the **orientation** of those letters that's useful there", repeated
later as "**positioning**". The superscript "YAR" is the only superscript on the sculpture.
*Testable form:* build the key from *where* the anomalies are, not what they say — e.g. the
panel coordinates of IQLUSION's Q, UNDERGRUUND's U, DESPARATLY's A, the superscript Y/A/R,
the anomalous L in tableau row N, and the four "?" — as a grille, a set of offsets, or an
index sequence into the tableau.
*Status:* ⬜ untested. Note that `families.md` used the *words* IQLUSION, UNDERGRUUND,
DESPARATLY, LAYERTWO as keyword-alphabet seeds — that is the opposite of what Sanborn is
pointing at.

**C15 ⬜ — Re-index with the question mark (98 characters).**
*Source:* "Try both" (2013); Scheidt's "I think there are 98 characters left" (2005);
Sanborn's 2009 remark that K4 starts with "?"; his 2003 refusal to say which section owns it.
Against: he committed to "exactly 97" in 2019 and 2020, and to 97 for K5 in 2025.
*Testable form:* re-run every **position-dependent and aperiodic** model with indices shifted
by one (position of `O` = 2 rather than 1).
*Status:* 🟡 For periodic systems a global index shift is equivalent to a key-phase shift,
which the period sweeps already covered; for running keys, the offset sweeps covered it. For
the 100-million-model position-dependent suite (linear/quadratic/cubic/triangular/sawtooth/
block/row-col/bilinear) it was **not** verified that both indexings were run. Cheap to
confirm; low expected yield.

**C16 ⬜ — Antipodes as an additional corpus.**
*Source:* Sanborn, 2009: solvers have "everything we need at Antipodes"; Wired 2005: the
Cyrillic Projector and the "Untitled Kryptos Piece" contain "primarily the same text" with
alterations, and Sanborn refused to say whether they hold clues.
*Testable form:* *Antipodes* (1997, Hirshhorn) repeats the Kryptos ciphertext **with slight
differences**. The running-key corpus in `runningkey.md` used the Kryptos panel only. If the
Antipodes rendering of K4 differs from the Kryptos rendering at even one position, that is a
direct, independent check on the carving (C6) and a second sample of the same chart.
*Status:* ⬜ I could not obtain a letter-level Antipodes transcription in this pass — the
canonical one is on elonka.com, which is behind a bot-challenge. **Action: obtain the
Antipodes transcription and diff it against `data/sculpture_panels.txt`.** Small effort,
potentially decisive for C6.

---

### Group 3 — Constraints that cut against further brute force

**C17 — "A one-off", "a system unknown to anyone on the planet", "visual systems for
encoding… individualistic", "spatial systems of encoding and decoding".**
*Source:* Sanborn/Scheidt refusing to answer the "one-off" question (ACA 2013); Dunin's
recollection of Scheidt's "unknown to anyone on the planet" (which Scheidt declined to
confirm); Sanborn NPR 1999 and Wired 2005 on visual/spatial systems; "creativity" (2025).
*Implication:* there is a substantial prior that K4 is **not a member of any catalogued
classical family**, which is exactly what 7.09 million keyed-alphabet pairs, 100 million
position-dependent shift models, every digraphic family, both Hill orders and every
sculpture-derived running key have collectively been telling us. Enumerating more classical
families has low expected yield.
*Where to spend effort instead:* C6 (error tolerance), C9 (semantic crib-drag), C11 (tableau
as coordinate lookup), C13 (indicator), C12/C14 (geometry and anomaly positions), and above
all **C10 (wait for K5 and exploit depth)**.

**C18 — The sharpest thing the statements plus the completed work jointly imply.**
Put together:
- the anchors sit at fixed positions (C2, strong reading), so there is no net displacement;
- the mapping flattens English so frequency analysis fails (C4/masking), so it is not
  monoalphabetic — and indeed mono and affine are closed;
- every periodic polyalphabetic to period 25 is closed, over 7.09 million alphabet pairs;
- every keystream drawn from the sculpture's own texts, forwards, reversed, X-stripped,
  rotated, and every autokey variant, is closed;
- fractionating systems that flatten frequencies (bifid, trifid, and by extension
  ADFGVX-style fractionate-then-transpose, Fractionated Morse, Morbit, Pollux, straddling
  checkerboard) either are closed or **necessarily displace letters**, which C2's strong
  reading forbids.

**The residue is narrow and specific: a position-preserving polyalphabetic substitution whose
key stream is aperiodic and comes from a source that has not been tried — i.e. literally
"the original matrix" that Sanborn says nobody has recovered.** Either that, or the strong
reading of C2 is false (C12/C2-weak), or a carved letter is wrong (C6).
Those three branches are the entire remaining space consistent with the public record, and
they map one-to-one onto the three highest-priority experiments above.

---

### Group 4 — Statistical folklore that the statements are often used to support

Run `python3 analysis/sanborn_statements_stats.py` to reproduce.

| Claim | Reality |
|---|---|
| "K4's IoC (0.0361) is **below** uniform random (0.0385) — proof the masking worked." | For a 97-letter string the null IoC is 0.0385 ± 0.0028. Observed **z = −0.84, P(IoC ≤ observed) = 0.22**. Completely unremarkable. |
| "All 26 letters appear — unusual for 97 characters." | P(all 26 present in 97 uniform random letters) = **0.54**. Slightly more likely than not. |
| "Autocorrelation spike at lag 7, z = +3.0." | Family-wise p over 24/48/96 lags = **0.032 / 0.063 / 0.122**. Marginal at best, and not significant if all lags were examined. |

None of these three is evidence for or against any hypothesis. They should not be used to
motivate a search or to claim that "masking" is visible in the statistics. The honest reading
is that **97 characters is simply too short to distinguish Scheidt's masked ciphertext from a
uniformly random string** — which is itself consistent with everything he said, and equally
consistent with almost every candidate system.

---

## Part IV — Attributions that do not hold up

Listed so the team stops treating these as authorial statements.

- ✗ **"Sanborn confirmed a 1:1 letter-for-letter mapping across all of K4."** He confirmed the
  six BERLIN pairs emphatically in 2013, then in 2019 **explicitly declined** to generalise,
  committing only to "97 characters" and "BERLIN starts at character 64". The global 1:1
  assumption is a solver convention, not a statement.
- ✗ **"The Berlin Clock is the Mengenlehreuhr / Set Theory Clock."** Sanborn never said which
  clock until 2025, and in November 2025 he said it is the **World Clock (Weltzeituhr) at
  Alexanderplatz**. Any base-5 lamp-row keystream derived from the Mengenlehreuhr rests on a
  decade-old community guess that is now contradicted.
- ✗ **"The +19 bridge rule" / "f(correct) = f(wrong) + 19 mod 26" derived from the
  misspellings.** This is a construction from solvekryptos.com's 2025–26 reconstruction, not
  a Sanborn statement. That site now labels its own mechanism "back-solved … internally
  consistent but not independently recovered from public data."
- ✗ **"OBKR decrypts to THEC."** Same source, same status. Do not seed searches with it.
- ✗ **"K4's plaintext is not standard English."** This is *Wired*'s 2009 sidebar gloss on a
  hint, not a quote, and it contradicts Sanborn's own 1991 "it's in plain English, it's in
  text, and you can read it". Treat the plaintext as English, but terse and referential (C8).
- ✗ **"The extra L in the tableau points to a Hill cipher."** That is Bauer, Link and Molle's
  2016 *Cryptologia* conjecture, not a Sanborn or Scheidt statement — and Sanborn **omitted
  the extra L from the scale models he sells**, which is weak evidence against it being a
  deliberate pointer. (Hill is closed anyway.)
- ✗ **"Kryptos was meant to be solved with pencil and paper" as a Sanborn quote.** That line
  is David Stein's (*New York Times*, 1999). Scheidt said something equivalent about K4 in
  2003; Sanborn, so far as I can find, did not.
- ✗ **"Scheidt did the encryption."** Sanborn was "adamant" in 2003 that Scheidt taught the
  systems but **Sanborn did the encryption himself**. (Warzin's commentary on the same 2003
  notes asserts the opposite for Scheidt; where they conflict, Sanborn's first-person account
  plus Scheidt's own repeated "I don't know the answer" should win.)

---

## Sources

Primary interviews and articles
- Kim Zetter, "Questions for Kryptos' Creator", *Wired*, 2005-01-20 — <https://www.wired.com/2005/01/questions-for-kryptos-creator/>
- Kim Zetter, "Inside Info on Kryptos Codes" (the Scheidt interview), *Wired*, 2005-01-21 — <https://www.wired.com/2005/01/inside-info-on-kryptos-codes/>
  (both transcripts mirrored at <http://scirealm.org/KryptosHints.html> and <https://kryptosfan.wordpress.com/the-continuity-of-kryptos/pr/questions-for-kryptos-creator-by-kim-zetter/>)
- Kim Zetter, "Typo Confounds Kryptos Sleuths", *Wired*, 2006-04-20 — <https://www.wired.com/2006/04/typo-confounds-kryptos-sleuths/>
- Steven Levy, "Mission Impossible: The Code Even the CIA Can't Crack", *Wired*, 2009-04 — mirror <https://itzmenu.wordpress.com/2009/05/11/mission-impossible-the-code-even-the-cia-cant-crack/>
- John Schwartz, "Artist releases clue to Kryptos", *NYT*, 2010-11-20 — <https://www.nytimes.com/2010/11/21/us/21code.html>; charts <https://www.nytimes.com/2010/11/21/us/21codecharts.html>
- John Schwartz, "Sculptor Offers Another Clue…", *NYT*, 2014-11-20 — <https://www.nytimes.com/2014/11/21/us/another-kryptos-clue-is-offered-in-a-24-year-old-mystery-at-the-cia.html>
- Schwartz & Corum, "This Sculpture Holds a Decades-Old C.I.A. Mystery. And Now, Another Clue", *NYT*, 2020-01-29 — <https://www.nytimes.com/interactive/2020/01/29/climate/kryptos-sculpture-final-clue.html>
- NPR, "A New (And Final) Clue To 'Kryptos'", 2020-01-30 — <https://www.npr.org/2020/01/30/801323608/a-new-and-final-clue-to-kryptos-a-long-standing-puzzle>
- NPR, "'Kryptos' Sculptor Drops New Clue In 20-Year Mystery", 2010-11-22 — <https://www.npr.org/2010/11/22/131520768/-kryptos-sculptor-drops-new-clue-in-20-year-mystery>
- John Schwartz (@jswatz), EAST clue, 2020-08-24 — <https://twitter.com/jswatz/status/1297658577914667008>
- Kelsey Ables, "The 'Kryptos' code has gone unsolved for 35 years. Now it's up for sale.", *Washington Post*, 2025-08-14 — <https://www.washingtonpost.com/entertainment/art/2025/08/14/kryptos-code-k4-solution-jim-sanborn-auction/>
- "A C.I.A. Secret Kept for 35 Years is Found in the Smithsonian's Vault", *NYT*, 2025-10-16 — <https://www.nytimes.com/2025/10/16/science/kryptos-cia-solution-sanborn-auction.html>
- Dan Vergano, "Final Clues to Mystery of CIA Kryptos Puzzle Released", *Scientific American*, 2025-11-12 — <https://www.scientificamerican.com/article/cia-kryptos-puzzle-creator-releases-final-clues/>
- Humberto Basilio, "After 35 Years, a Solution to the CIA's Kryptos Puzzle Has Been Found", *Scientific American*, 2025-10 — <https://www.scientificamerican.com/article/a-solution-to-the-cias-kryptos-code-is-found-after-35-years/>
- RR Auction lot 7302001, "The Complete Secrets of Kryptos: Jim Sanborn's Private Archive" — <https://www.rrauction.com/auctions/lot-detail/350761607302001-the-complete-secrets-of-kryptos-jim-sanborns-private-archive/>
- RR Auction, "Kryptos K4: Discovered, Not Solved" — <https://content.rrauction.com/kryptos-k4-discovered-not-solved-heres-what-actually-happened/>
- Paradigm, "Project Kryptos", 2026-06-12 — <https://www.paradigm.xyz/writing/kryptos> · <https://www.paradigm.xyz/kryptos/k4>
- Sanborn oral history, Archives of American Art (Avis Berman), 2009-07-14/16 — <https://www.aaa.si.edu/collections/interviews/oral-history-interview-jim-sanborn-15700>

Compilations and event notes (secondary, cited above by tier)
- John Wilson, "John's Collected Kryptos Hints" — <http://scirealm.org/KryptosHints.html> (1991 ABC transcript, 1999 WaPo/NYT/NPR, 2003 Dunin roadtrip notes, 2004 Scheidt talk + his email, 2005 WSJ/NPR/CNN, 2006 Yahoo-group note)
- "Kryptos Notes From the ACA Convention", 2013-10-28 — <https://kryptosfan.wordpress.com/2013/10/28/kryptos-notes-from-the-aca-convention/>
- "More about Ed Scheidt's ACA Talk", 2013-10-30 — <https://kryptosfan.wordpress.com/2013/10/30/more-about-ed-scheidts-aca-talk/>
- "Masking vs. English" — <https://kryptosfan.wordpress.com/k4/artichoke/masking-vs-english/>
- Tyler Akins, "K4 — Unsolved" (carries the 2019 Dunin lunch notes and the AAA "primer" passage) — <https://rumkin.com/reference/kryptos/k4/>
- LEMMiNO, "The Unbreakable Kryptos Code" (reference apparatus; refs #11, #22, #24, #42d, #45, #53) — <https://www.lemmi.no/p/the-unbreakable-kryptos-code>
- Intel Today, 2017-09-10 and 2022-02-06 — <https://inteltoday.org/2017/09/10/the-kryptos-sculpture-section-iv-a-few-clues/> · <https://inteltoday.org/2022/02/06/two-years-ago-kryptos-sculpture-jim-sanborn-this-is-the-third-and-to-be-sure-final-clue-update-and-then-came-a-4th-clue/>
- Richard Bean, *The Conversation*, 2021-05-30 — <https://theconversation.com/declassified-cold-war-code-breaking-manual-has-lessons-for-solving-impossible-puzzles-161595>
- Klaus Schmeh, *Cipherbrain*, 2020-07-22 — <https://scienceblogs.de/klausis-krypto-kolumne/2020/07/22/a-6-5-hour-interview-with-kryptos-creator-jim-sanborn/>
- *Kryptos*, Wikipedia (used as a reference index, not as a source) — <https://en.wikipedia.org/wiki/Kryptos>

Not obtainable in this pass
- `elonka.com` (the Kryptos FAQ, the Antipodes transcription, and the August/November 2025 open letters) serves a bot-challenge and returned no content. The open-letter content reached me only through *Washington Post*/*Scientific American* quotation. **Someone with a browser should retrieve `elonka.com/kryptos/faq.html`, `elonka.com/kryptos/sanborn/antipodes.html` and `elonka.com/kryptos/OpenLetterAug2025.html` — the Antipodes transcription in particular feeds constraint C16.**
- `aaa.si.edu` returns 403 to scripted fetches; the 2009 oral-history transcript should be read in full by a human. It is a 6.5-hour interview and is the longest first-person account of the encoding process in existence.
