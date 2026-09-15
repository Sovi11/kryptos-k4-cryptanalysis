# Kryptos K4 & Cicada 3301 — a research archive

An open record of a systematic cryptanalytic attack on **Kryptos K4**, the 97-letter unsolved
passage on Jim Sanborn's 1990 sculpture at CIA headquarters, plus a documented status report on
**Cicada 3301's Liber Primus**.

**K4 is not solved here.** No candidate decryption exists in this repository, and none is claimed.
What this archive offers instead is the **negative space**: a map of where K4 is *not*, at a
resolution that does not appear to have been published before, with chance expectations attached
to every figure so a future solver can trust the numbers and skip the ground.

## The problem

```
OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR
```

97 letters. Four plaintext fragments confirmed by Sanborn, 1-indexed:

| positions | ciphertext | plaintext | released |
|---|---|---|---|
| 22–25 | `FLRV` | `EAST` | 2020 |
| 26–34 | `QQPRNGKSS` | `NORTHEAST` | 2020 |
| 64–69 | `NYPVTT` | `BERLIN` | 2010 |
| 70–74 | `MZFPK` | `CLOCK` | 2014 |

For context, the solved sections: **K1** and **K2** are Vigenère on a KRYPTOS-keyed alphabet with
keys `PALIMPSEST` and `ABSCISSA`; **K3** is a pure route transposition with no key. K4's method was
designed with retired CIA cryptographer Ed Scheidt and has never been published.

## Start here

**[kryptos/findings/SUMMARY.md](kryptos/findings/SUMMARY.md)** — the consolidated record: everything
tested, at what scale, with what outcome, and what remains.

## Scale of the search

Roughly **10⁹ explicit crib-consistency tests**, plus several families closed *exactly* rather than
by enumeration:

- all **97!** transpositions, by an invariance argument
- all **26!** cipher alphabets in the Gromark test
- the full **25!**, **36!**, **27!**, **25!²**, **36!²** unknown-square spaces, via CP-SAT
- 55,066,851,840 tableau-lookup trials, settled by hash join

Configurations fitting all 24 crib letters *and* producing English: **zero**. Best crib agreement
among tests that genuinely constrain the key: **10 of 24**, where chance alone yields 4.09.

## Some results worth knowing

- **Porta and every Enigma-like system are dead on inspection.** The cribs contain `S→S` at
  position 33 and `K→K` at 74. Any cipher forbidding a letter to map to itself is excluded.
- **Pure transposition is dead on inspection.** The cribs require three `E`s; the ciphertext has two.
- **A transposition applied *before* the substitution cannot rescue anything.** Under the
  ciphertext reading it leaves the 24 crib pairs untouched, so every one-stage negative transfers
  to all 97! transpositions at once.
- **No sculpture-derived running key works.** The two required key blocks (13 and 11 letters)
  appear nowhere in a 66-text corpus at any offset, rotation, or cipher combination.
- **Lateral key material fails too.** 194 keystreams from the Berlin Clock's lamp structure, the
  Antipodes Cyrillic text, the Cyrillic Projector and compass bearings: 16.5M tests, best joint
  match 16/24 — exactly chance. Gronsfeld is impossible outright, since 11–15 of the required
  shifts exceed 9.
- **The statistics show nothing once selection is paid for.** An omnibus test over 7 statistics
  gives p ≈ 0.40. K4's index of coincidence, 0.0361, sits *below* uniform random — it is flatter
  than chance, not more structured.

## Layout

```
kryptos/
  README.md            background library: sculpture, K1–K3, K4 facts, sources
  data/                ciphertext, cribs, panel layout, K1–K3 plaintexts
  findings/            one report per line of attack (start with SUMMARY.md)
  lateral/             Berlin Clock, Antipodes, tableau, clue history + keystreams
  analysis/            ~118 Python scripts; every negative is reproducible
cicada/
  liber_primus_status.md   Liber Primus status, page-by-page methods, statistics
```

## Reproducing

Scripts are plain Python 3 and self-contained. Generated corpora and language-model caches
(~85 MB) are gitignored and rebuild on first run.

```bash
python3 kryptos/lateral/test_lateral.py          # lateral keystreams vs the cribs
python3 kryptos/lateral/test_lateral_numeric.py  # Berlin Clock numeric/binary streams
```

## Two notes on the record

**On "sealed until 2075."** Widely reported, but the primary document does not support it. The
official Smithsonian finding aid for the Jim Sanborn papers (revised 2026-05-06) states the
collection is "open for research" and contains the words *sealed*, *closed* and *2075* nowhere.
See SUMMARY.md §2.

**On what would count as a solve.** Since September 2025 the K4 plaintext has been obtainable
without any cryptanalysis: Kobek and Byrne reconstructed it from scrambled paper strips in
Sanborn's donated papers. Paradigm's verifier binds a *plaintext string, not a method*, so it
cannot distinguish a genuine break from a leak. A real solve means publishing the **method**, and
deriving it from public data.

## Status of the Cicada side

Liber Primus remains largely unsolved. LP1's 17 pages are decrypted (Atbash, Vigenère with
`DIVINITY` and a rune-F skip rule, prime-totient streams); of LP2's 58 pages only two are. Its
sharpest structural fingerprint is a deficiency of same-rune bigrams — about 86 in ~13,000 runes,
far below chance — pointing at a system that forbids a rune encrypting to itself. Cicada's last
authenticated message was April 2017; genuine messages are PGP-signed with key `7A35090F`.

## Provenance

Research and code produced with [Claude Code](https://claude.com/claude-code) across a
multi-agent workflow, with every negative result independently verified by adversarial
re-derivation. Findings are as reliable as the scripts that produced them, which are all here.
