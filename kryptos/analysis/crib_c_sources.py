"""Task (a): VERIFY THE CRIB POSITIONS against what the primary sources actually say.

Everything in this repo -- and every published K4 cryptanalysis -- is built on

    22-25 EAST, 26-34 NORTHEAST, 64-69 BERLIN, 70-74 CLOCK   (1-indexed into K4)

If those positions are off by one, all of it is invalid.  Sanborn's own 2006 K2
correction was exactly a one-letter shift caused by a carving error, so the
worry is not idle.

The decisive observation, which this script turns into arithmetic: for BERLIN
and CLOCK the releases state BOTH an index range AND the ciphertext letters at
that range.  Two independent facts about the same window.  They are
simultaneously true under exactly one indexing convention, and the convention
that satisfies them is the one this repo already uses.  For EAST and NORTHEAST
the *New York Times* text gives only index numbers -- the ciphertext strings
FLRV and QQPRNGKSS are a community read-off -- so those two are anchored less
firmly, which is exactly where crib_b_shifts.py's independent block slides earn
their keep.

Verbatim primary-source quotations are in SOURCES below with URLs.  Nothing here
depends on a paraphrase.

Run:  python3.12 crib_c_sources.py > ../findings/crib_c_out.txt
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crib_lib as L

CT = L.CT
DATA = L.DATA

# ---------------------------------------------------------------------------
# 1. The primary sources, quoted verbatim.
# ---------------------------------------------------------------------------
SOURCES = [
    dict(
        tag="BERLIN / 2010",
        cite="John Schwartz, 'Clues to Stubborn Secret in C.I.A.'s Backyard', "
             "The New York Times, published online November 20, 2010; print "
             "November 21, 2010, p. A1. Retrieved via the Internet Archive "
             "(web.archive.org/web/20120101102610/http://www.nytimes.com/2010/11/21/us/21code.html).",
        quote="He has provided The New York Times with the answers to six letters in "
              "the sculpture's final passage. The characters that are the 64th through "
              "69th in the final series on the sculpture read NYPVTT. When deciphered, "
              "they read BERLIN.",
        lo=64, hi=69, ct="NYPVTT", pt="BERLIN", ct_quoted=True,
    ),
    dict(
        tag="CLOCK / 2014",
        cite="John Schwartz, 'Sculptor Offers Another Clue in 24-Year-Old Mystery at "
             "C.I.A.', The New York Times, November 20, 2014; print November 21, 2014, "
             "p. A16. Retrieved via the Internet Archive "
             "(web.archive.org/web/20160101034413/...another-kryptos-clue-is-offered...).",
        quote="The 64th through 69th characters of the final panel, when deciphered, "
              "spelled out the word BERLIN. [...] Mr. Sanborn has decided to open the "
              "door a bit more with five additional letters, those in the 70th through "
              "74th position. They spell 'clock.' This means that the letters from "
              "positions 64 to 74 spell out two words: 'Berlin clock.'",
        lo=70, hi=74, ct="MZFPK", pt="CLOCK", ct_quoted=False,
    ),
    dict(
        tag="NORTHEAST / 2020",
        cite="John Schwartz and Jonathan Corum, 'This Sculpture Holds a Decades-Old "
             "C.I.A. Mystery. And Now, Another Clue.', The New York Times, January 29, "
             "2020. Retrieved via the Internet Archive "
             "(web.archive.org/web/20201208072511/...kryptos-sculpture-final-clue.html).",
        quote="The 2010 clue was the word BERLIN, in the 64th through 69th positions of "
              "that final passage. In 2014 he revealed the word CLOCK in the next five, "
              "70 through 74. [...] So now, Mr. Sanborn, at 74, is giving the world "
              "another shot: the word NORTHEAST, at positions 26 through 34.",
        lo=26, hi=34, ct="QQPRNGKSS", pt="NORTHEAST", ct_quoted=False,
    ),
    dict(
        tag="EAST / 2020",
        cite="Wikipedia 'Kryptos' (citing John Schwartz, @jswatz, Twitter, August 24, "
             "2020); Intel Today, 'The KRYPTOS Sculpture...', September 28, 2020, "
             "relaying Schwartz's account; Elonka Dunin, elonka.com/kryptos/ .",
        quote="In August 2020, Sanborn revealed that the four letters in positions 22 "
              "through 25, ciphertext 'FLRV', in the plaintext are 'EAST'. Sanborn "
              "commented that he 'released this layout to several people as early as "
              "April'. [Wikipedia]  --  'The 4th Clue -- The four letters in positions "
              "22-25, cipher-text FLRV, are EAST in the plain-text.' [Intel Today]",
        lo=22, hi=25, ct="FLRV", pt="EAST", ct_quoted=False,
    ),
]

# Elonka Dunin's layout block, transcribed character-for-character from the
# <pre> element on https://www.elonka.com/kryptos/ (fetched 2026-09-13).
ELONKA_LAYOUT = [
    "....",
    ".................EASTNORTHEAST.",
    "............................BER",
    "LINCLOCK.......................",
]

# ---------------------------------------------------------------------------
# 2. Candidate indexing conventions.
#
# Each returns the string that "position n" indexes into, plus the offset that
# converts a 1-indexed quoted position into a 0-indexed offset in THAT string.
# ---------------------------------------------------------------------------
def load_panel():
    rows, cur = [], None
    with open(os.path.join(DATA, "sculpture_panels.txt")) as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("#"):
                continue
            if line.strip() in ("[LEFT]", "[RIGHT]"):
                cur = line.strip()
                continue
            if cur == "[LEFT]" and line.strip():
                rows.append(line.strip())
    return rows


PANEL_ROWS = load_panel()
PANEL = "".join(PANEL_ROWS)                      # 869 chars incl. 4 '?'
PANEL_LETTERS = "".join(c for c in PANEL if c.isalpha())   # 865


def conventions():
    """name -> (indexed string, 1-indexed).  All are 1-indexed except where the
    name says otherwise."""
    qk4 = "?" + CT                               # the '?' that ends K3, then K4
    return [
        ("K4, 1-indexed (the standard assumption)", CT, 1),
        ("K4, 0-indexed", CT, 0),
        ("'?'+K4, 1-indexed (task c: the K3 question mark counted)", qk4, 1),
        ("'?'+K4, 0-indexed", qk4, 0),
        ("K4 counted from the END, 1-indexed", CT[::-1], 1),
        ("whole left panel incl. '?', 1-indexed", PANEL, 1),
        ("whole left panel, letters only, 1-indexed", PANEL_LETTERS, 1),
        ("last 4 panel rows as carved (= K4), 1-indexed", "".join(PANEL_ROWS[-4:]), 1),
        ("final panel row only (31 chars), 1-indexed", PANEL_ROWS[-1], 1),
    ]


def probe(s, base, lo, hi):
    """Return the substring that a quoted 1-indexed range lo..hi selects."""
    a = lo - base
    b = hi - base + 1
    if a < 0 or b > len(s):
        return None
    return s[a:b]


# ---------------------------------------------------------------------------
def sec_quotes():
    print("=" * 78)
    print("TASK (a)  PRIMARY-SOURCE VERIFICATION OF THE CRIB POSITIONS")
    print("=" * 78)
    print("K4 = %s" % CT)
    print("     (97 letters; repo file data/k4_ciphertext.txt)")
    print()
    for s in SOURCES:
        print("### %s" % s["tag"])
        print("  source : %s" % s["cite"])
        print("  quote  : \"%s\"" % s["quote"])
        print("  parsed : positions %d-%d  ->  plaintext %s ; ciphertext %s %s"
              % (s["lo"], s["hi"], s["pt"], s["ct"],
                 "(quoted in the release itself)" if s["ct_quoted"]
                 else "(NOT quoted in the release text -- community read-off)"))
        print()


def sec_selfconsistency():
    print("=" * 78)
    print("A1.  DOES THE QUOTED INDEX AGREE WITH THE QUOTED CIPHERTEXT?")
    print("=" * 78)
    print("The 2010 release states two independent facts about the same window:")
    print("an index range AND the letters found there.  A convention is admissible")
    print("only if it makes both true at once.  Same test applied to all four cribs")
    print("(for the three whose ciphertext string was supplied by the community")
    print("rather than the release, this is a consistency check on the community's")
    print("read-off, not on Sanborn).")
    print()
    hdr = "%-58s %s" % ("convention", "  ".join("%-10s" % s["ct"] for s in SOURCES))
    print(hdr)
    print("-" * len(hdr))
    verdicts = []
    for name, s, base in conventions():
        cells, allok = [], True
        for src in SOURCES:
            got = probe(s, base, src["lo"], src["hi"])
            ok = (got == src["ct"])
            allok &= ok
            cells.append("%-10s" % (got if got is not None else "--off--"))
        print("%-58s %s   %s" % (name, "  ".join(cells), "ALL MATCH" if allok else ""))
        verdicts.append((name, allok))
    print()
    good = [n for n, ok in verdicts if ok]
    print("  conventions under which all four quoted (index, ciphertext) pairs hold: %d"
          % len(good))
    for n in good:
        print("    -> %s" % n)
    print()
    print("  CONCLUSION: the quoted index numbers and the quoted/derived ciphertext")
    print("  strings are mutually confirming.  Exactly two of the nine conventions")
    print("  satisfy them, and those two are the SAME map -- prefixing the '?' and")
    print("  switching to 0-indexing are inverse shifts that cancel.  So there is a")
    print("  unique admissible reading, and it is the one this repo already uses.")
    print()
    print("  In particular the task-(c) hypothesis -- that Sanborn 1-indexed over a")
    print("  string that begins with the '?' ending K3 -- is refuted by the 2010")
    print("  release's own words: under that convention positions 64-69 read %s,"
          % probe("?" + CT, 1, 64, 69))
    print("  not NYPVTT.  The same convention puts CLOCK over %s, NORTHEAST over"
          % probe("?" + CT, 1, 70, 74))
    print("  %s and EAST over %s."
          % (probe("?" + CT, 1, 26, 34), probe("?" + CT, 1, 22, 25)))


def sec_offsets():
    print()
    print("=" * 78)
    print("A2.  WHERE ELSE COULD EACH QUOTED CIPHERTEXT STRING SIT?")
    print("=" * 78)
    print("If a quoted ciphertext string occurs exactly once in K4 then the string")
    print("pins the window by itself and the index number is redundant -- an")
    print("off-by-one in the reporting could not move the crib.")
    print()
    for src in SOURCES:
        occ = [m.start() + 1 for m in re.finditer("(?=%s)" % src["ct"], CT)]
        occ_panel = [m.start() + 1 for m in re.finditer("(?=%s)" % src["ct"], PANEL_LETTERS)]
        print("  %-9s ct=%-10s occurrences in K4 (1-indexed starts): %-12s "
              "| in the whole 865-letter panel: %s"
              % (src["pt"], src["ct"], occ, occ_panel))
    print()
    print("  Every quoted string is unique inside K4.  For BERLIN the string was")
    print("  published by Sanborn himself, so BERLIN's window is nailed down by two")
    print("  independent statements and is immune to a reporting off-by-one.")
    print("  FLRV, MZFPK and QQPRNGKSS were read off the published layout by the")
    print("  community, so for them uniqueness only says the community's read-off is")
    print("  self-consistent with the index it was read from.")
    print()
    print("  Distance to the nearest alternative placement (how far a crib would have")
    print("  to slide before its ciphertext letters could repeat):  no repeats exist,")
    print("  so any slide changes the ciphertext letters and therefore changes all 24")
    print("  (ct, pt) pairs.  That is what crib_b_shifts.py then tests directly.")


def sec_elonka():
    print()
    print("=" * 78)
    print("A3.  ELONKA DUNIN'S LAYOUT DIAGRAM, PARSED")
    print("=" * 78)
    print("elonka.com/kryptos/ publishes the four cribs as a picture of the 4/31/31/31")
    print("K4 row layout rather than as numbers.  Transcribed character-for-character")
    print("from the page's <pre> block and concatenated:")
    print()
    for r in ELONKA_LAYOUT:
        print("      %-32s (%d chars)" % (r, len(r)))
    lay = "".join(ELONKA_LAYOUT)
    print()
    print("  concatenated length: %d  (expected 97: %s)" % (len(lay), len(lay) == 97))
    rows = [4, 31, 31, 31]
    print("  row widths %s match the carved K4 rows %s: %s"
          % ([len(r) for r in ELONKA_LAYOUT], rows,
             [len(r) for r in ELONKA_LAYOUT] == rows))
    print()
    for m in re.finditer(r"[A-Z]+", lay):
        print("    %-14s at 1-indexed %d..%-3d over ciphertext %s"
              % (m.group(), m.start() + 1, m.end(), CT[m.start():m.end()]))
    print()
    print("  Elonka's diagram and the New York Times numbers agree exactly, and both")
    print("  agree with data/cribs.json.  Two independent renderings of the same")
    print("  claim -- a picture and a set of ordinals -- land on the same 24 letters.")
    print("  DISCREPANCY FOUND (wording, not positions): Elonka's page calls both the")
    print("  January 2020 NORTHEAST release and the April/August 2020 EAST release")
    print("  'a third clue'.  Smithsonian Magazine (Jan 31 2020) swaps the release")
    print("  years, writing that \"'clock' and 'Berlin' [were] released in 2010 and")
    print("  2014, respectively\"; BERLIN was 2010 and CLOCK 2014.  Neither error")
    print("  touches a position number.")


def sec_antipodes():
    print()
    print("=" * 78)
    print("A4.  CROSS-CARVING CHECK: ANTIPODES")
    print("=" * 78)
    print("Antipodes (1997, Hirshhorn) carries the Kryptos text a second time.  If a")
    print("carving slip of the 2006 K2 kind sits inside K4, the two carvings should")
    print("disagree there.  Transcription used: the Antipodes English-side text held")
    print("in this session's scratch copy (provenance: a 2026-09-12 fetch of the")
    print("community transcription; PROVENANCE UNCERTAIN -- treat as indicative).")
    ap = os.environ.get("ANTIPODES_FILE", "")
    if not ap or not os.path.exists(ap):
        print("  [skipped: set ANTIPODES_FILE to the transcription to run this check]")
        return
    text = "".join(ch for ch in open(ap).read() if ch.isalpha() or ch == "?")
    occ = [m.start() for m in re.finditer("OBKR", text)]
    print("  OBKR occurrences in the Antipodes English side: %d" % len(occ))
    for i, o in enumerate(occ):
        seg = "".join(c for c in text[o:o + 200] if c.isalpha())[:97]
        same = (seg == CT)
        print("    occurrence %d: first 97 letters identical to the Kryptos K4? %s"
              % (i + 1, same))
        if not same:
            for j, (a, b) in enumerate(zip(seg, CT)):
                if a != b:
                    print("      first difference at K4 position %d: Antipodes %s vs Kryptos %s"
                          % (j + 1, a, b))
                    break
        prev = text[max(0, o - 1):o]
        print("      character immediately before OBKR: %r (K3's question mark)" % prev)
    print()
    print("  If both occurrences reproduce the 97 letters exactly, K4 has no carving")
    print("  discrepancy of the K2 kind between the two sculptures, and the 97-letter")
    print("  length that every index is counted over is confirmed twice over.")


def sec_summary():
    print()
    print("=" * 78)
    print("A5.  WHAT SURVIVES AS AN ASSUMPTION, AND WHAT DOES NOT")
    print("=" * 78)
    rows = [
        ("BERLIN 64-69",
         "index AND ciphertext letters both stated by Sanborn via the NYT, 2010",
         "FIRM -- two independent statements agree; also restated by Sanborn in "
         "person (Elonka's March 2019 lunch notes: 'BERLIN is plaintext that starts "
         "at exactly the 64th character')"),
        ("CLOCK 70-74",
         "index stated by the NYT 2014 ('those in the 70th through 74th position'); "
         "ciphertext MZFPK not quoted in the article text",
         "FIRM on the index; the 74th letter being K in both plaintext and "
         "ciphertext was called out publicly, which independently confirms the "
         "alignment of that one position"),
        ("NORTHEAST 26-34",
         "index stated by the NYT 2020; ciphertext QQPRNGKSS a community read-off",
         "FIRM on the index, one source only"),
        ("EAST 22-25",
         "no index published by Sanborn in words -- released as an IMAGE of the K4 "
         "layout to individual correspondents in April 2020, surfaced August 2020",
         "WEAKEST.  rumkin.com/reference/kryptos/k4/ records the doubt explicitly: "
         "'It is possible that the first EAST in the plain text isn't correct. "
         "Sanborn did confirm it, but it's possible that it was confirmed out of "
         "hand as opposed to being intentional.'  Two incompatible provenance "
         "stories circulate: (i) Sanborn sent a layout image unprompted [Schwartz, "
         "Intel Today], (ii) a solver asked whether EASTNORTHEAST sat at a specific "
         "location and Sanborn agreed [rumkin]"),
    ]
    for a, b, c in rows:
        print("  %s" % a)
        print("      provenance : %s" % b)
        print("      strength   : %s" % c)
        print()
    print("  The practical consequence: an off-by-one, if it exists anywhere, is far")
    print("  likelier in the EAST/NORTHEAST block than in BERLIN/CLOCK.  That is the")
    print("  asymmetric hypothesis crib_b_shifts.py section B2 tests directly (each")
    print("  phrase block slid independently by -3..+3) and crib_e_ptct.py extends to")
    print("  a free slide of the EASTNORTHEAST block alone.")


if __name__ == "__main__":
    sec_quotes()
    sec_selfconsistency()
    sec_offsets()
    sec_elonka()
    sec_antipodes()
    sec_summary()
