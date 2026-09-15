# K4 prior art, and a forensic audit of every public "solution"

Compiled 2026-09-12. Scripts: `analysis/prior_art_check.py`, `prior_art_naughton.py`,
`prior_art_scott.py`, `prior_art_klepp.py`, `prior_art_bean_stats.py`, `prior_art_keystream.py`.

**One-line summary.** In 35 years nobody has publicly broken K4. The plaintext was *recovered*
in September 2025 from Jim Sanborn's own papers in the Smithsonian archive — not decrypted —
and that recovered text has never been published. Every public "solution" I could find either
(a) fits the four Sanborn cribs by construction, using one fitted parameter per crib letter, and
produces gibberish everywhere else, or (b) does not fit the cribs at all when its stated recipe is
applied mechanically. The single most useful thing in the prior art is not a solution but a
diagnosis: Richard Bean's HistoCrypt paper, which rules out the seriated-digraphic and Playfair
families on known-plaintext grounds and nominates **Gromark** as the surviving candidate. Gromark
is *not* in our ruled-out list and should be.

---

## 0. How to read this, and the test I applied

Every claim in Part B was put through the same four questions:

1. **Mechanical crib test.** Apply the stated recipe literally, no re-alignment, no interpretation.
   Does it put EAST at 22–25, NORTHEAST at 26–34, BERLIN at 64–69, CLOCK at 70–74?
2. **Parameter count.** How many free parameters does the method carry, versus the 24 crib letters
   it must explain? A model with ≥24 free parameters that fits 24 constraints has explained nothing.
3. **Non-crib output.** Is the other 73 characters English?
4. **Confirmation.** Any word from Sanborn, Scheidt, Paradigm, or an independent reproduction?

Chance bookkeeping used throughout: a random letter matches a crib letter with probability 1/26, so
a random 97-letter string scores **0.92 of 24** crib letters on average. Scoring 5–7/24 after a
search over tens of thousands of configurations is *chance*, not signal. A solution must be 24/24
**and** English elsewhere.

---

# PART A — what the community has already tried

## A.1 What the makers said, and what it constrains

These are the only first-party statements about the K4 mechanism, and they bound the search.

| Source | Statement | What it constrains |
|---|---|---|
| Sanborn letter to CIA staff, Dec 1989 | the right side is "partly deciphered by using the [Vigenère] table and partly by using a potentially challenging encoding system" | the tableau is a tool for K1–K3, maybe not for K4 |
| Sanborn, Jan 1990 | K4 is "encoded in a modern system created for the project by an expert cryptographer" | not a textbook classical cipher, or not only one |
| Sanborn, Apr 1991 | "a whole different ballgame of multiple codes" | multi-stage |
| Ed Scheidt, *Wired*, Jan 2005 | he "masked" the English so frequency analysis fails; "I disguise that. So… you need to solve the technique first and then go for the puzzle" | the flat IoC (0.0361) is deliberate, an artefact of masking, not evidence of a one-time pad |
| Sanborn, *Wired* 2005 | he took Scheidt's technique and masked it further, so that even Scheidt would not know the content | the final layer is the artist's, possibly ad hoc |
| Sanborn, repeatedly | the system is "anathema to math" / does not "necessarily depend on mathematics" | argues against Hill, PRNG, and linear-congruence schemes — though it does not forbid modelling them mathematically |
| Sanborn to Elonka Dunin, 2003 | "Yes. It ain't easy, but it's solvable!" | solvable from public data |
| Bean (2022 talk), reporting the design intent | the original intent was a solution in "5, 7 or 10 years with **no** known plaintext" | the difficulty was calibrated for a hobbyist, not an agency — a strong argument against exotic mechanisms |

Sources: [Elonka's Kryptos FAQ](https://www.elonka.com/kryptos/faq.html);
[Bean, *Cryptodiagnosis of "Kryptos K4"*, HistoCrypt](https://richardbean.id.au/presentations/2022-06-21%20cryptodiagnosis_of_k4.pdf);
[kryptosfan, "masking technique"](https://kryptosfan.wordpress.com/tag/masking-technique/).

**The last row is the most important line in this report.** A cipher designed to fall in 5–10 years
to an amateur with *no* cribs, which has now survived 35 years *with* 24 crib letters, is a cipher
whose designer misjudged something — most likely, the method depends on a physical or contextual
fact that is not in any transcription. Bean says as much: "Something has gone quite wrong."

## A.2 Crib release timeline

| Date | Clue | Positions | Released via |
|---|---|---|---|
| Nov 2010 | NYPVTT → BERLIN | 64–69 | NYT |
| Nov 2014 | MZFPK → CLOCK | 70–74 | NYT |
| Jan 2020 | QQPRNGKSS → NORTHEAST | 26–34 | NYT |
| Apr–Aug 2020 | FLRV → EAST | 22–25 | NYT / interviews |
| 2025 | the clock is the **Weltzeituhr** (World Clock) at Alexanderplatz, not the Mengenlehreuhr | — | Sanborn |

That last item matters: a large amount of community work assumed the Mengenlehreuhr (Berlin Set
Theory Clock, base-5 lamp counts). Sanborn's 2025 clarification retires that whole branch.

## A.3 Academic and conference treatments

### Richard Bean, "Cryptodiagnosis of *Kryptos K4*", HistoCrypt 2021 (presented 2022)
[paper](https://ecp.ep.liu.se/index.php/histocrypt/article/view/153) ·
[slides](https://richardbean.id.au/presentations/2022-06-21%20cryptodiagnosis_of_k4.pdf) ·
[code](https://github.com/RichardBean/k4testing)

The most rigorous public treatment. It does not attempt a solution; it does classification. Findings,
with my independent reproduction (`analysis/prior_art_bean_stats.py`) in the right-hand column:

| Bean's observation | Bean | reproduced here |
|---|---|---|
| index of coincidence | 0.03608 | **0.03608** ✓ |
| repeated bigrams / trigrams in the linear text | 10 / 0 | **10 / 0** ✓ |
| excess column-bigram repeats when written at width 21 | ~1 in 6,750 | 11 observed, **1 in 3,226** by Monte-Carlo over 200k permutations — same order, weaker |
| repeated-plaintext-letter images sit close in A–Z | mean 3.6, ~1 in 240 | mean 3.12 (all 8 repeated letters, adjacent images), **1 in 455** |
| pairs with d(Pᵢ,Pⱼ)≤1 give small d(Cᵢ,Cⱼ) | mean 3.8, ~1 in 5,000 | mean 4.59, **1 in 1,316** |
| **Materna**: crib plaintext letters in {K,R,Y,P,T,O,S} barely move | mean 2.1, ~1 in 5,500 | mean **2.10** ✓, **1 in 25,000** |

Two **hard eliminations** Bean derives from the cribs, which we should adopt and not re-derive:

- **Seriated digraphic at width 21 is impossible.** BERLIN → NYPVTT forces two different bigrams,
  one ending in I and one ending in N, both to encipher to `ZT`. A digraphic system cannot do that.
- **Playfair and every Playfair-derived system is impossible.** CLOCK → MZFPK has K → K; Playfair
  cannot encipher a letter to itself. (We already had this from the S→S / K→K argument.)

His **positive** proposal is the **Gromark** cipher (W. J. Hall, *The Cryptogram*, 1969; Callimahos,
*Military Cryptanalytics III*, 1977): a mixed plaintext alphabet and a mixed ciphertext alphabet, with
a numeric keystream generated from a short primer by a lagged-Fibonacci recurrence
kᵢ = kᵢ₋ₙ + kᵢ₋ₙ₊₁ (mod base). Arguments for, in his words: it is one of the few ACA ciphers whose IoC
is almost flat (≈1/26); an even base with primer length 5 produces an underlying pattern at width 21;
it is letter-to-letter with no transposition, matching the observed one-to-one behaviour; and it fits
Sanborn's hints about a pencil-and-paper field cipher with more than one stage and "base" arithmetic.
Arguments against: the Gromark plaintext alphabet is usually straight A–Z, and his **exhaustive search
over base 10, primer length 5 found only 39 of 99,999 primers** consistent with the cribs, none of
which produced English. His diagnosis of the failure is precise and is the best open lead in the
literature: *"Stats are strongest within the cribs but not between them → progressive key? Periodic
Gromark?"*

Independently, two machine-learning cipher classifiers — BION's tool and Leierzopf's NCID — both
return **Seriated Playfair and Gromark** as their top choices for K4. Seriated Playfair is dead by the
argument above. That leaves Gromark and its variants as the only classifier-endorsed survivor.

### Craig Bauer, Gregory Link, Dante Molle, "James Sanborn's *Kryptos* and the matrix encryption conjecture", *Cryptologia* 40(6), 2016, 541–552
Argues the anomalous extra **L** in row N of the carved tableau is deliberate, and that with it the
letters **HILL** read down a column — a signpost to Hill-cipher matrix encryption. They ran brute-force
attacks for 2×2 and 3×3 cases. Outcome: no solution. **We have independently re-run and extended this**
(`findings/families.md`, §Hill): Hill 2×2 and 3×3, linear and affine, both directions, both alphabets,
all alignments — every row has zero solutions. This branch is closed.

### Christian Schridde, numberworld.blog "Kryptos — The Cipher" series (Parts 1–5, 2017–2022)
[Part 2](https://www.numberworld.blog/2017/03/kryptos-cipher-part-2.html) ·
[Part 4](https://www.numberworld.blog/2020/07/kryptos-cipher-part-4.html)

The best-documented single-researcher programme. Catalogues the K4 anomalies (all seven KRYPTOS
letters clustered on the right of the ciphertext; doubled letters concentrating in the last two
columns of a 7×14 layout at p ≈ 10⁻³–10⁻⁴; M and Y each appearing exactly once and both inside the
BERLINCLOCK span; BERLIN starting at 64 = 9·7+1, a 3×3 block boundary; the extra tableau L). Attempts
and outcomes:

- **Hill 3×3 keyed on BERLINCLOCK** — the determinant equation Det(S)·20 ≡ 23 (mod 26) is unsolvable
  since gcd(20,26) ∤ 23; the A=1 variant is solvable but extends to nothing. No decryption.
- **Running key** — Cryptocrack's classifier ranks running key first by a wide margin; the key implied
  by BERLIN is `MUYKLGKOR` (straight tableau) or `SYMLWRHZN` (KRYPTOS tableau), neither English; no
  matching fragment found in books or in K1–K3. *(Our `findings/runningkey.md` independently produced
  the same required key `MUYKLGKOR` for that configuration — a useful cross-check that both pipelines
  are correct.)*
- **Wichmann–Hill PRNG** (chosen because it is from 1982, contains "Hill", and takes three seeds that
  might be the K2 coordinates) — seeds 0–50 in each of three dimensions. Nothing.
- **"Scott's" route: Quagmire III (alphabet KRYPTOS, key EMUFPHZLRFA) then the positional map
  y = 77 + 38x mod 97 taken from the K2 coordinates.** Schridde reports this puts BERLIN at the right
  place but yields PEEK, not CLOCK, after it. **Re-tested here** (`analysis/prior_art_scott.py`): the
  literal recipe scores 1/24 cribs; sweeping *all* 37,248 linear-congruence transpositions of that same
  Quagmire-3 output gives 0 exact fits and a best of **7/24**, of which 6 are the BERLIN the parameters
  were chosen to produce. Over 37,248 trials, chance alone predicts 0.9 results at ≥7/24. **This is
  chance, and it fails the CLOCK crib that was already public in 2014 when it was proposed.**

### Klaus Hörenberg, kryptos.hoerenberg.com
[site](https://kryptos.hoerenberg.com/) · [sitemap](https://kryptos.hoerenberg.com/index.php?action=sitemap)

A two-layer theory built on the **DYAHR** anomaly — a group of deliberately out-of-alignment letters
on the sculpture, which Sanborn confirmed are intentional and "important". Hörenberg reads DYAHR as an
anagram of HYDRA (the WWII teletype XOR traffic), converts it to 5-bit ASCII, and proposes XOR
combined with mod-5 addition, with "layer two: ID by rows" pointing at the tableau's row labels.
**Outcome: negative, and usefully so.** He submitted his first ten proposed letters to Sanborn in
February 2018 and was told: *"Sorry but these are not the first ten letters."* Sanborn separately told
Klaus Schmeh in March 2019 that a German submission about a year earlier had been "kind of scary"
because "the first part had started to look right, but then the rest didn't." His own conclusion page
does not reproduce the cribs at their positions.

This is the only case in the whole corpus where Sanborn has given a *specific* negative on a *specific*
proposal. It is worth more than most of the positive claims.

### kryptosfan, "Kryptos — Beyond K4" (2009–2013)
[cryptanalysis index](https://kryptosfan.wordpress.com/cryptanalysis/) ·
[methods](https://kryptosfan.wordpress.com/welcome/methods/)

A systematic amateur sweep. Numbered trials apply a transposition to K4 and then test Playfair, bifid
and four-square on the result (e.g. Trial #1 strips the letters of KRYPTOS; Trial #7 is double columnar
transposition keyed KRYPTOS/IQLUSION; Trial #9 reads left-to-right diagonals of a 9×10 grid). The site
also enumerates and discusses: Caesar, Vigenère, Playfair, bifid, Morbit, Pollux, fractionated Morse,
Gronsfeld, keyed Caesar, nomenclator, straddling checkerboard, Werftschlüssel, affine, Atbash, SMS,
Castor, digraphic substitution, runic; rail fence, route, columnar, double, permutation,
Rasterschlüssel, rotational, scytale, Übchi, keyed columnar; plus one-time pad, Baconian, nulls,
steganography, block and stream ciphers. **All negative.** Most of this overlaps what we have already
closed rigorously; the fractionated-Morse / Pollux / Morbit branch does not, but is inconsistent with
the one-to-one letter mapping (below).

### Other reference points
- [rumkin.com/reference/kryptos/k4](https://rumkin.com/reference/kryptos/k4/) — a summary page. Notes
  the "komitet" anonymous key suggestion, the extra-L/Hill hint, and that K4 is probably not a
  transposition.
- [kryptos.today](https://kryptos.today/) — an AI-agent-run live cryptanalysis project (2026),
  reporting **0 verified candidates** as of May 2026. Figures I read directly off its
  [progress log](https://kryptos.today/progress): one phase logged "1.26 billion attempts" with
  "0/96 crib-passing"; another "~108M attempts … 0 candidates". It rules out simple monoalphabetic
  substitution (IoC), short-period polyalphabetic schemes (zero repeated trigrams, Kasiski), and
  width-7 columnar transposition + KRYPTOS-keyed Vigenère, and has deprioritised the Mengenlehreuhr
  keystream family after Sanborn's Weltzeituhr correction. Its acceptance bar is the right one: all
  four cribs, coherent non-crib English, reproducible method, generalisation — "all four. No
  exceptions."
  **Directly relevant to us:** it tested the lag-7 autocorrelation spike (it measures z = +3.05, matching
  our z ≈ +3.0) against four null distributions at 10,000 samples each and concluded the spike is
  explained by baseline English properties rather than by a period-7 key. We should not build a search
  around lag 7."
- The **Kryptos Group** (groups.io/g/KRYPTOS, ~2,300 members, moderated by Elonka Dunin and others) is
  the main discussion venue; it is moderated and the archive is members-only, so it cannot be mined
  wholesale. Bean's blunt assessment of it is worth recording: the main discussion group "has many
  posts but very little measurement going on." Elonka's FAQ lists community-floated ideas that were
  checked and led nowhere: Morse code, palindromes, courtyard rock placement, shadows and sundials,
  Egyptian references, magnetism, folding the sculpture halves together, forming a Jefferson cylinder
  from the two halves, book codes off the ciphertext side, running K4 through an Enigma, and combining
  the K1–K3 methods.

## A.4 Master table

| # | Approach | Who / where | Outcome |
|---|---|---|---|
| 1 | Periodic Vigenère / Beaufort / variant / Quagmire I–IV | community since 1990; us, 7.09 M alphabet pairs | **ruled out**, periods 2–25 |
| 2 | Porta, Gronsfeld, Trithemius/progressive | community; us | **ruled out** (Porta structurally: S→S, K→K) |
| 3 | Playfair / two-square / four-square / bifid | kryptosfan; Bean; us | **ruled out** (K→K; Bean's `ZT` argument) |
| 4 | Seriated digraphic at width 21 | Bean 2021 | **ruled out** by BERLIN→NYPVTT |
| 5 | Hill 2×2, 3×3, matrix conjecture | Bauer/Link/Molle 2016; Schridde; us | **ruled out** |
| 6 | Running key from any sculpture text | Gillogly (conjecture); Schridde; us | **ruled out** for all sculpture corpora |
| 7 | Autokey (plaintext and ciphertext) | Gillogly (conjecture); us | **ruled out**, all primer lengths |
| 8 | Transposition-only | everyone | **ruled out** (cribs need three E's, ciphertext has two) |
| 9 | Monoalphabetic / affine | everyone | **ruled out** (9 forward + 8 reverse conflicts) |
| 10 | Position-dependent shift models (linear/quadratic/…); Quagmire3 + linear congruence | Schridde/"Scott"; Klepp; us, >10⁸ models | **ruled out**; best 9/24, chance |
| 11 | Wichmann–Hill and other PRNG keystreams | Schridde | negative over the searched seed range |
| 12 | XOR / mod-5, DYAHR two-layer | Hörenberg | negative; **Sanborn explicitly rejected his first ten letters** |
| 13 | Mengenlehreuhr (Berlin Set Theory Clock) lamp gates | very large community branch | negative; **retired by Sanborn's 2025 Weltzeituhr clarification** |
| 14 | Fractionated Morse / Pollux / Morbit | kryptosfan | negative; also inconsistent with one-to-one mapping |
| 15 | Physical/steganographic readings (shadows, rock placement, folding, Jefferson cylinder, Enigma, book code) | Kryptos Group, per Elonka's FAQ | all negative |
| 16 | **Gromark**, base 10 primer length 5 | Bean 2021 | **39 of 99,999 primers survive the cribs, none give English — not closed** |
| 17 | Progressive-key or periodic Gromark, other bases/primer lengths | proposed by Bean, **not done** | **open** |

## A.5 The residue — what is genuinely still open

Stripping out everything with a rigorous negative, what the literature leaves standing is narrow:

1. **Gromark and its variants.** Endorsed by two independent ML classifiers, consistent with the flat
   IoC, consistent with letter-to-letter encipherment, consistent with Sanborn's "pencil-and-paper,
   more than one stage, base arithmetic" hints, and only searched by Bean in one corner of its
   parameter space (base 10, primer length 5, presumably straight plaintext alphabet). **Not in our
   ruled-out list.** The obvious extensions are other bases, other primer lengths, keyword-mixed
   plaintext alphabets (which Bean flags as the anomaly Gromark alone does not explain), and his own
   suggestion of a progressive or periodic Gromark to explain why the statistics are strong *within*
   each crib block but not *between* them.
2. **Anything keyed on a physical fact of the sculpture that no transcription captures** — the
   out-of-alignment letters (DYAHR and others; Sanborn confirmed they are intentional and important),
   the copper's back face, the compass and lodestone, the true carved spacing. This is where the
   "designed to fall in 5–10 years but still standing after 35" contradiction most plausibly resolves.
3. **A two-stage system whose first stage is not a letter permutation of the 97**, so that our
   transposition-then-substitution sweep did not cover it.

## A.6 Statistical facts worth carrying forward (independently verified here)

- IoC 0.03608, below uniform random — this is *designed*, per Scheidt's masking statement, and should
  not be read as evidence of a one-time pad.
- 10 repeated bigrams, **0 repeated trigrams**. Excess column-bigram repeats at width 21 (11 observed,
  ~1 in 3,200 by permutation test). Width 21 is the one non-random geometry in the ciphertext, and the
  cribs kill the obvious explanation for it.
- **A one-to-one-ish mapping is strongly supported**: no transposition, letter-for-letter.
- The Materna effect — crib plaintext letters from {K,R,Y,P,T,O,S} move a mean of only 2.10 places in
  A–Z — reproduces exactly (p ≈ 1/25,000 by Monte-Carlo). **But see Part C: it does not survive
  extension beyond the published cribs, and it was a post-hoc subset of 10 of 24 letters, so its
  nominal significance is inflated.**

---

# PART B — forensic audit of public "solutions"

## Scorecard

| Claim | Cribs, applied mechanically | Non-crib text English? | Independently derivable? | Confirmed? |
|---|---|---|---|---|
| mattklepp/k4 | 24/24 — **by 24 fitted parameters** | **no**, gibberish | no, back-solved | no |
| solvekryptos.com | 24/24 — **by back-solved helper cards** | yes, but it is an *assumed* plaintext | **no, site says so itself** | no |
| "Structured Solution May 2026" video | **untestable** — no published procedure | — | no method published | no |
| Naughton / Grok-3 | **1/24** literal; 0 of 2,400 variants fit | no | recipe is public but wrong | no |
| ChatGPT / LLM claims | 0–24/24, but all are short of 97 letters and have no cipher behind them | — | no method at all | no |
| figshare "Genie" Berlin-Clock route | **0/24** | — | no | no |
| "Scott" Quagmire3 + y=77+38x | **1/24** literal; best 7/24 over 37k variants = chance | no | yes, and it fails | no |
| Hörenberg XOR / mod 5 | does not reach the cribs | — | yes | **explicitly rejected by Sanborn** |

## B.1 mattklepp/k4 — "Solved K4 Cipher"

**Status: the repository is now 404.** It existed from at least 2025-08-16 and was still live on
2026-05-28; Wayback holds ten snapshots of the repo root and hundreds of its source files. I recovered
the README from `web.archive.org/web/20260528051817/https://github.com/mattklepp/k4`. Contemporary
coverage: [staael.com/blog/kryptos-k4](https://staael.com/blog/kryptos-k4) (19 Aug 2025); a Hacker News
submission ([44109212](https://news.ycombinator.com/item?id=44109212)) drew one enthusiastic comment and
no technical scrutiny.

**Claimed plaintext:**
`UDILKAFSGDMZLYQJCVNJA` `EASTNORTHEAST` `OPOHAYLOMIQSDZSSHTQNSXYMEMNBT` `BERLINCLOCK` `SYRUFZRDSPQKKQZIKAGIWQD`

**Claimed method**, per the README's own five phases: a base shift schedule `(4·position + 20) mod 26`;
then a neural network on 52 engineered features; then a backtracking constraint solver that "fixed the
24 known plaintext characters as constraints"; then "region-based corrections" with the regions named
EAST, NORTHEAST, BERLIN and CLOCK.

**Audit** (`analysis/prior_art_klepp.py`, verified):

- The base formula alone hits **7/24** crib positions — exactly the 29.2% the README claims, so the
  arithmetic is faithfully reproduced. (Chance for any fixed shift schedule: 0.92/24.)
- The README then lists **24 "position-specific corrections", one for each of the 24 crib letters.**
  I computed the residuals `required(i) − base(i)` independently: they are *identical* to the listed
  corrections, value for value. The corrections are not derived from anything; they are defined to be
  whatever closes the gap at the 24 positions where the answer was already published.
- So the model has 24 free parameters fitting 24 data points. Zero residual degrees of freedom. The
  advertised "100% accuracy on all 24 known constraint positions" is a tautology.
- The corrections take 14 distinct values with no positional pattern, i.e. they carry no compressible
  rule that could extrapolate to the other 73 positions.
- And indeed the other 73 characters are `UDILKAFSGDMZLYQJCVNJA…OPOHAYLOMIQSDZSSHTQNSXYMEMNBT…SYRUFZRDSPQKKQZIKAGIWQD`,
  which is not English and not close to it.

The blog covering it states the corrections were "used to tune his solver with local corrections" over
"the exact regional groupings Matt used to tune his solver" — the claimant's own framing concedes the
fitting. **Verdict: not a solution. A 24-parameter curve fit to 24 points, with no predictive content.**
The repository's removal is consistent with the author having reached the same conclusion.

## B.2 solvekryptos.com

**This is the most intellectually honest of the claims, and it is honest specifically about being
circular.** Its own [what-changed note](https://solvekryptos.com/about) reads:

> "Earlier versions of this site described K4 as solved. After extensive forward-testing in 2026, we
> regrounded the claims. … the mechanism is a back-solved model, internally consistent but not
> independently recovered from public data."

**Claimed plaintext (97 letters):**
`THE COMPASS ROSE IS HERE X EAST NORTHEAST THIS IS YOUR POSITION X COMMISSION BERLIN CLOCK WHICH IS NORTHEAST OF HERE X`

Verified here: exactly 97 letters, and all four cribs land at their exact positions (24/24).

**Claimed method:** a Quagmire III variant keyed KRYPTOS, with a "helper letter" read from the tableau
side of the sculpture, a row-identity card f(C), a column-offset card g_state(T) selected by which of
four 31-cell passes the position falls in, a one-bit gate fixed by position, and P = (C − R) mod 26.

**Audit.** The site does the audit itself, and its admissions are the finding:

- *"Most f and g values are back-solved from the plaintext and reproduce the reconstruction by construction."*
- Of 26 f-table entries, **11 are forward-derived from public data and 15 are back-solved**.
- Its per-position grade map: **27 derived, 2 public-relational, 22 witness-claimed, 1 bridge, and 45
  back-solved-only** out of 97.
- The g_Y card is "the largest underived object: 18 of the Y pass's 31 positions rest on values that
  exist only as an authored worksheet."
- The decisive sentence, from [/verify](https://solvekryptos.com/verify):
  > "because the full-system incidence graph is a forest (no forcing cycles; given the plaintext, the
  > fitted f/g layer carries six degrees of freedom), the fitted card cells can always be tuned to
  > reproduce a supplied shift stream. 97/97 agreement therefore certifies that the plaintext is
  > arithmetically consistent with the ciphertext under the reconstructed machine; it does not
  > independently validate the plaintext or the method."

That is exactly right, and it is the general lesson for this whole field: **any** 97-letter string is
arithmetically consistent with the ciphertext under a sufficiently flexible shift model. Consistency
is not evidence.

Two further cautions specific to this site:

1. It states its plaintext "comes from Sanborn's Smithsonian archive". **The archive text has never
   been published** — Kobek and Byrne agreed to keep it secret, the Smithsonian sealed the files until
   2075, and the auction buyer has not released it (Part C). So the site's 97-letter text is a
   *reconstruction of what it believes the archive says*, not a transcription of it. Its own "honest
   reconstruction" language concedes this; its front-page framing does not.
2. The text is internally plausible for good reasons that are also reasons a reconstructor would pick
   it: the sculpture has a compass and lodestone ("THE COMPASS ROSE IS HERE"), and the Morse slabs
   carry **"T IS YOUR POSITION"**, which completes naturally to "[THIS] IS YOUR POSITION". Those are
   public clues. Corroboration by public clues is weak evidence when the claimant had the clues.

**Verdict: not a solution and does not claim to be one. Useful as a well-documented reconstruction and
as a model of how to state a claim's boundaries. Its plaintext should not be used as a crib source.**

## B.3 "The Kryptos K4 Structured Solution — May 2026"

A YouTube video, channel **Creation Unified** (confirmed via YouTube's oEmbed API), pointing viewers to
creationunified.com. That site is a general "structural intelligence" consultancy by Kevin L. Brown,
covering quantum gravity, dark matter, consciousness and abiogenesis. **I could find no K4 page on it.**
I probed `/kryptos`, `/kryptos-k4`, `/k4`, `/kryptos-k4-structured-solution` and
`/the-kryptos-k4-structured-solution` — all 404 — and searched its sitemap and link graph for any
Kryptos entry: none.

**Verdict: not evaluable.** There is no published procedure, so it cannot be applied mechanically, and
it therefore fails the reproducibility bar automatically. This is not a judgement that it is wrong; it
is that a claim with no stated method is not a cryptographic claim.

## B.4 Michael P. Naughton (with Grok 3), February 2025

[Medium part 1](https://medium.com/@michaelpnaughton/how-i-cracked-the-kryptos-code-a-35-year-mystery-7c46004f61b6) ·
[part 2](https://medium.com/@michaelpnaughton/how-i-cracked-the-kryptos-code-a-35-year-mystery-part-2-b447ed87213b)

**Claimed plaintext:** "THIS IS A GUIDE TO THE BERLIN CLOCK WHICH IS NORTHEAST OF HERE AT CIA LANGLEY,
VIRGINIA" (with a claimed deliberate NORTHEST typo).
**Claimed method, stated precisely enough to test:** reverse the ciphertext, apply Vigenère with key
KRYPTOS, reverse the result.

**Audit** (`analysis/prior_art_naughton.py`, with a K1 encrypt/decrypt round-trip regression first):

- The literal recipe yields
  `AIVTDEFANSWURAASTHKRERSCXZGXDURMBIWFDESBZYEZPMIPEMAUMUKLUHHKWVJZFAXCJULMAMFWLWGIVSSLUNVWQKIGLVEJH`
  — **1 of 24 crib letters**, i.e. at the chance level of 0.92.
- Being generous, I swept 2,400 near-variants: keys KRYPTOS / PALIMPSEST / ABSCISSA × all rotations ×
  {Vigenère, Beaufort, variant-Beaufort} × all 8 straight/KRYPTOS assignments of the plaintext,
  ciphertext and key alphabets × reverse-in and reverse-out flags. **0 exact fits.** Best 5/24 — and
  over 2,400 trials chance alone predicts ~3.6 results at ≥5/24.
- Separately, the claimed plaintext is **69 letters, not 97**, and none of the four cribs falls at its
  required position within it.

The author has since walked it back, saying he was "being facetious and ironic" and that "it is
impossible for anyone to solve this fourth wall since Jim Sanborn has to approve the solution."
**Verdict: refuted, by the author's own stated recipe.**

## B.5 The AI-generated claims

Aaron Toponce's gist [*No, ChatGPT didn't solve Kryptos 4*](https://gist.github.com/atoponce/1cd01f40786ab21af011f0d6257fba0c)
is the standing reference. It collects seven ChatGPT outputs of varying lengths with mutually
inconsistent plaintexts and applies exactly the crib test. I re-ran three of them:

| output | length | cribs at correct positions |
|---|---|---|
| `BERLINCLOCKINNORTHEASTAREAKEYTOPUZZLE` | 37 | 1/24 |
| `INTHECENTEROFTHISCITYEASTNORTHEASTNEARROTESRATHAUSCHIMESFROMTHEBERLINCLOCK` | 74 | 24/24 |
| `ABANDONCONTACTNEARTHEBERLINCLOCK` | 32 | 0/24 |

The middle row is instructive and worth dwelling on: **it hits all 24 crib letters at their exact
positions and it is still worthless**, because it is 74 letters instead of 97 and there is no cipher
behind it at all — it is English prose written *around* the published crib offsets. This is the single
most important calibration in this report: **passing the crib test is necessary, cheap, and nowhere
near sufficient.** Anyone can write English that puts EAST at 22 and BERLIN at 64. What is hard is a
mechanism that *produces* it from OBKRUOXOGHUL… without a free parameter per letter.

One commenter in that thread conceded that "gpt-4 and gpt-4o models do not get it right" and that
neural-network attempts produced "biased results". The broader Medium genre (e.g. "The Kryptos K4
Scandal: How AI Exposed a 35-Year Intelligence Community Hoax", "ShadowCipher and the Cracking of
Kryptos") is in the same category; none publishes a mechanically reproducible procedure.

## B.6 The figshare cluster

Several 2025–2026 figshare deposits claim K4 results, including *"Kryptos K4: A Mechanism-Based Partial
Solution and Statistical Confirmation"*, *"Genie Replication Package: Resolution of Kryptos K4 via
Berlin Clock Route and Substitution Funnel"*, *"Kryptos K4 Partial Decryption: A Structured Analysis"*
and *"Proposed analysis and decryption of KRYPTOS K4"*.

The Genie package's claimed plaintext is: "TO SET THE EAST-NORTHEAST HOUR BY BEARING BERLIN CLOCK
DEGREES GRID POINT NORTHWEST TO FIND GROSSER STERN", produced by a 4-4-11-4 Berlin-Clock route with
offset 21 and a boustrophedon mask, plus a substitution governed by k mod 3, and claimed significant at
p ≤ 0.0001 against 10,000 randomised crib-constrained trials.

**Audit** (`analysis/prior_art_check.py`): the text is **88 letters, not 97**. EAST occurs at positions
9 and 18, not 22. NORTHEAST occurs at 13, not 26. BERLIN occurs at 35, not 64. CLOCK occurs at 41, not
70. **0 of 24 crib letters are in the right place.** The stated p-value is therefore measuring
something other than what it claims: a null distribution built from "crib-constrained" randomised
decodes is not a test of a candidate that does not satisfy the crib constraint.

**Verdict: refuted on the primary constraint.** A deposit with a DOI is not peer review.

## B.7 Cases where the claimant was honest

Two entries deserve to be distinguished from the rest.

- **Hörenberg** never claimed a solution; he submitted ten letters, was told they were wrong, and
  published that.
- **solvekryptos.com** retracted its own "solved" framing in 2026 and published a per-position audit of
  which values are derived and which are fitted. Its boundary statement (quoted in B.2) is a better
  piece of cryptanalytic hygiene than anything else in this corpus.

---

# PART C — what the 2025 archive recovery does and does not tell us about the method

## C.1 What actually happened

- Circa 2023, while compiling his papers during cancer treatment, Sanborn donated material to the
  **Smithsonian's Archives of American Art** and inadvertently included five pages of scrambled text.
  These were copies of 1990 documents he had made for the CIA's Historical Intelligence staff, to let
  them confirm the sculpture's text was not offensive: he had **cut the sentences into strips and taped
  them back together out of order**, so officials could check the content without easily reconstructing
  the message.
- In **September 2025**, writer **Jarett Kobek** and journalist **Richard Byrne**, having noticed from
  the auction listing that the coding charts were in the Smithsonian collection, requested access.
  Byrne photographed the papers; Kobek recognised the already-published fragments — "I see the words,
  you know, 'Berlin clock.' And I'm like, hey, whoa" — and reassembled the strips into the plaintext.
  They emailed Sanborn on **3 September 2025**. Sanborn confirmed the text was correct.
- RR Auction's lawyers threatened legal action if they published. Sanborn asked for NDAs; they refused
  but **agreed to keep the plaintext secret**. Sanborn had the Smithsonian **seal the material until
  2075**.
- The archive sold on **21 November 2025** for **$962,500** against a $300–500k estimate. The buyer is
  **Paradigm**, who state they deliberately did **not** read the solution: Sanborn entered the plaintext
  on an isolated laptop, it was SHA-256 hashed, the hash was sent to Google Cloud KMS to produce an
  HMAC verification tag, the plaintext never left the device, and the laptop was wiped. Submissions are
  checked against the tag for **$1** each (anti-brute-force). Paradigm also hold the **K5 ciphertext**
  — 97 characters, made at the same time as K4 — to be released after K4 falls.
- Paradigm's own summary of the state of play: "But it's still unsolved."

Sources: [RR Auction, "Discovered, Not Solved"](https://content.rrauction.com/kryptos-k4-discovered-not-solved-heres-what-actually-happened/) ·
[Scientific American](https://www.scientificamerican.com/article/a-solution-to-the-cias-kryptos-code-is-found-after-35-years/) ·
[Kobek interview, Zona Motel](https://zonamotel.substack.com/p/interview-kryptos-k4-uncovered-jarett) ·
[Paradigm, *Project Kryptos*](https://www.paradigm.xyz/writing/kryptos) ·
[PuzzCulture](https://puzzculture.com/2025/12/16/the-kryptos-solution-is-auctioned-off-but-the-mystery-is-far-from-over/)

## C.2 What it tells us about the method: **almost nothing**

This is the heart of Part C, and it needs stating bluntly.

**It tells us nothing about the encryption mechanism.** What was recovered is *output*, not *process*.
Kobek is explicit: *"Rich and I recovered the plain text. There's no way on earth that this is a
cryptographic solve, and we have not claimed that."* Sanborn: *"They found scrambled text, and not by
solving the cryptogram. They did not solve K4."* Byrne adds that the recovery leaned on the artist's
public clues: *"You absolutely had to have the clues that the artist provided over the years to really
make sense of it."* The coding charts, the key, and the step-by-step procedure were **not** what they
found; those went to the auction buyer, and the method is still known only to Sanborn and Scheidt.

**It also does not give us the plaintext.** The recovered text has never been published. Kobek and
Byrne are holding it; the Smithsonian sealed it to 2075; the buyer has not released it. **Every
97-letter "K4 plaintext" circulating in 2026 — including the widely-copied "THE COMPASS ROSE IS HERE…"
— is a reconstruction or a guess, not a transcription of the archive document.** Treating it as ground
truth is the single most likely way for our search to go wrong from here.

**What it does change, and it is not nothing:**

1. **It confirms a coherent English plaintext exists** and is broadly of the "instructions pointing at
   a location" kind, consistent with EAST / NORTHEAST / BERLIN / CLOCK. It kills the "K4 is noise",
   "K4 is a hoax", and "K4 is a one-time pad with no recoverable message" families.
2. **It confirms K4 is a letter-for-letter encipherment of ordinary English.** Sanborn's strip-and-tape
   trick only makes sense over sentences; there is no suggestion of an intermediate code layer.
3. **It supplies a verification oracle.** For the first time there is an instant, authoritative check
   on a candidate plaintext. *(Out of scope for us: it is a paid service.)*
4. **It removes the incentive to trust folklore.** Any pre-2025 claim that "the plaintext is X" can now
   be dated and set aside.
5. **It sharpens the prize.** The remaining problem is purely the *method* — and since K5 is another 97
   characters made by the same process at the same time, the method is worth more than the K4 plaintext.

## C.3 A test that shows why the circulating reconstruction must not be trusted

If a 97-letter plaintext is genuine, then every statistical property induced by the cipher must hold at
the 73 positions Sanborn never published, not just at the 24 he did — the encryption process has no way
of knowing which letters would later be leaked. This gives a clean falsification test, and the
circulating reconstruction fails it (`analysis/prior_art_keystream.py`):

| statistic | 24 published crib positions | 73 unpublished positions |
|---|---|---|
| mean \|P−C\| in A–Z, all letters | 6.25 (random 8.67), p = 0.031 | 7.62, p = 0.27 |
| **Materna subset** (plaintext letter in {K,R,Y,P,T,O,S}) | **2.10**, n = 10, **p = 0.0001** | **7.58**, n = 33, **p = 0.57** |

The Materna anomaly — the strongest single statistical signature in the whole prior-art literature —
is **completely absent** outside the published cribs under this reconstruction. Two readings, both
useful:

- **The reconstruction's non-crib content is wrong.** Most likely. It is a guess assembled from public
  clues, and it should not be used as a crib source, a scoring target, or a keystream oracle.
- **Or the Materna effect is itself an artefact.** It was a post-hoc subset — 10 of 24 letters, chosen
  after inspecting them. With even a handful of alternative subsets on the table, a nominal 1-in-25,000
  becomes roughly 1-in-2,500 or worse. We should not design a search around it.

I also derived the full 97-letter keystream implied by that reconstruction under all 12 combinations of
{Vigenère, Beaufort, variant-Beaufort} × {straight, KRYPTOS} plaintext alphabet × {straight, KRYPTOS}
ciphertext alphabet. In every case the keystream has **flat IoC (0.0363–0.0438), no period with within-
class agreement above 0.13 for any period 2–48 (a real period gives ≈1.0), no lagged-Fibonacci
(Gromark) recurrence above chance for primer lengths 2–15 in base 10 or 26, and no verbatim occurrence
in any sculpture text.** On the Gromark test specifically: the best observed agreement was 0.18 of ~85
positions in base 10, against a chance rate of 0.10; that is z ≈ 2.45 on a single test, and across the
336 tests run (12 keystreams × 14 primer lengths × 2 bases) chance alone predicts about 2.4 results
that good. It is noise. Two
sanity checks confirm the pipeline: the derived crib-window keys reproduce the table in
`findings/runningkey.md` exactly, and the BERLIN-window key under the straight/Vigenère combination is
`MUYKLGKOR…`, matching Schridde's independently published value.

So: either the reconstruction is wrong, or the mechanism is not a letter-wise shift over a fixed pair
of alphabets. Given C.2, the first is far more likely — but the method is worth re-running the instant
any authenticated plaintext becomes public, because at that moment the keystream becomes known and the
problem collapses from "find the cipher" to "recognise this 97-symbol sequence".

---

# What I would do next

1. **Gromark, properly.** It is the one family with independent ML-classifier support, it is consistent
   with every structural fact we have, and the only published search covered base 10 / primer length 5 /
   straight plaintext alphabet and still left 39 crib-consistent primers. Extend to: bases 2–26; primer
   lengths 2–10; keyword-mixed plaintext alphabets (Bean's own "argument against" is that Gromark
   normally uses straight A–Z, which is exactly the assumption to relax given KRYPTOS); and Bean's
   suggestion of a **progressive or periodic Gromark**, motivated by his observation that the
   statistics are strong within each crib block but not between them. Score on the 24 cribs first,
   then on English quality of the other 73.
2. **Re-check every ruled-out family against the two Bean eliminations** to make sure we are not
   spending cycles re-deriving them, and add #4 (seriated digraphic at width 21) and #16/#17 (Gromark
   status) to `families.md`.
3. **Treat the width-21 column-bigram excess as the live phenomenon.** It is the one non-random geometry
   in the ciphertext (~1 in 3,200), its obvious explanation is dead, and no one has proposed a
   replacement. Bean's own framing — find, measure, explain, exploit — has stopped at "measure".
4. **Do not use any circulating 97-letter plaintext as ground truth**, and do not score candidates by
   similarity to it. Score on the 24 Sanborn letters plus English-likelihood only.
5. **Revisit the Mengenlehreuhr branch as retired** and, if the clock matters at all, use the
   **Weltzeituhr** at Alexanderplatz per Sanborn's 2025 clarification.

---

# Sources

**Primary / institutional**
- Elonka Dunin, [Kryptos FAQ](https://www.elonka.com/kryptos/faq.html) and [Kryptos page](https://www.elonka.com/kryptos/)
- [Kryptos Group, groups.io/g/KRYPTOS](https://groups.io/g/KRYPTOS) (moderated; archive members-only)
- [Wikipedia: Kryptos](https://en.wikipedia.org/wiki/Kryptos)
- [RR Auction: "Kryptos K4: Discovered, Not Solved"](https://content.rrauction.com/kryptos-k4-discovered-not-solved-heres-what-actually-happened/)
- [RR Auction: archive sells for $962,500](https://content.rrauction.com/jim-sanborns-complete-kryptos-archive-sells-for-962500-at-auction/)
- [Paradigm, *Project Kryptos*](https://www.paradigm.xyz/writing/kryptos)

**Academic**
- Richard Bean, *Cryptodiagnosis of "Kryptos K4"*, HistoCrypt 2021 — [paper](https://ecp.ep.liu.se/index.php/histocrypt/article/view/153), [slides](https://richardbean.id.au/presentations/2022-06-21%20cryptodiagnosis_of_k4.pdf), [code](https://github.com/RichardBean/k4testing)
- Craig Bauer, Gregory Link, Dante Molle, "James Sanborn's *Kryptos* and the matrix encryption conjecture", *Cryptologia* 40(6) 2016, 541–552

**Community research sites**
- [kryptos.hoerenberg.com](https://kryptos.hoerenberg.com/) (Hörenberg; DYAHR, two-layer XOR)
- [numberworld.blog Kryptos series](https://www.numberworld.blog/2017/03/kryptos-cipher-part-2.html) (Schridde)
- [kryptosfan.wordpress.com](https://kryptosfan.wordpress.com/cryptanalysis/)
- [rumkin.com/reference/kryptos/k4](https://rumkin.com/reference/kryptos/k4/)
- [kryptos.today](https://kryptos.today/) (AI-agent live cryptanalysis, 2026)

**Claims audited**
- mattklepp/k4 — repo **404**; README recovered from Wayback snapshot 2026-05-28; coverage at [staael.com](https://staael.com/blog/kryptos-k4), [HN 44109212](https://news.ycombinator.com/item?id=44109212)
- [solvekryptos.com](https://solvekryptos.com/) — [/solution](https://solvekryptos.com/solution), [/verify](https://solvekryptos.com/verify), [/about](https://solvekryptos.com/about)
- ["The Kryptos K4 Structured Solution — May 2026"](https://www.youtube.com/watch?v=HizjD_r-2hs), channel Creation Unified (no method published at creationunified.com)
- Michael P. Naughton — [part 1](https://medium.com/@michaelpnaughton/how-i-cracked-the-kryptos-code-a-35-year-mystery-7c46004f61b6), [part 2](https://medium.com/@michaelpnaughton/how-i-cracked-the-kryptos-code-a-35-year-mystery-part-2-b447ed87213b)
- Aaron Toponce, [*No, ChatGPT didn't solve Kryptos 4*](https://gist.github.com/atoponce/1cd01f40786ab21af011f0d6257fba0c)
- [figshare project 261475](https://figshare.com/projects/_Kryptos_K4_A_Mechanism-Based_Partial_Solution_and_Statistical_Confirmation_/261475) and related deposits

**Reporting on the 2025 recovery**
- [Scientific American](https://www.scientificamerican.com/article/a-solution-to-the-cias-kryptos-code-is-found-after-35-years/)
- [Kobek interview, Zona Motel](https://zonamotel.substack.com/p/interview-kryptos-k4-uncovered-jarett)
- [PuzzCulture](https://puzzculture.com/2025/12/16/the-kryptos-solution-is-auctioned-off-but-the-mystery-is-far-from-over/)
- [Artnet](https://news.artnet.com/art-world/cia-kryptos-sculpture-code-auction-2677451)
