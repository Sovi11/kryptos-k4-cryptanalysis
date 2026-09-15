#!/usr/bin/env python3
"""
Generate candidate keystreams from the two Berlin clocks named in the K4 debate:

  * the Mengenlehreuhr / Berlin-Uhr (Budapester Str., Europa-Center)
  * the Urania-Weltzeituhr (Alexanderplatz)  <-- the referent Sanborn confirmed Nov 2025

Every file written here is DERIVED, not transcribed: the derivation is in this script.
Provenance for the underlying facts is in ../berlin_clock.md and keystreams/MANIFEST.tsv.

Usage:  python3 gen_berlin_clock_keystreams.py
"""
import os, math, csv

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keystreams")
os.makedirs(OUT, exist_ok=True)
MAN = []   # (filename, description, source_url, confidence)

def write(name, seq, desc, url, conf):
    seq = str(seq)
    with open(os.path.join(OUT, name), "w") as f:
        f.write(seq + "\n")
    MAN.append((name, desc, url, conf))

A0 = lambda n: chr(ord('A') + (n % 26))          # 0 -> A
A1 = lambda n: chr(ord('A') + ((n - 1) % 26))    # 1 -> A

# ----------------------------------------------------------------------------
# Mengenlehreuhr model
#   row lengths, top to bottom: 1 (seconds blink), 4 (5h), 4 (1h), 11 (5min), 4 (1min)
#   total 24 light fields;  1+4+4+11+4 = 24
#   red lamps at positions 3,6,9 of the 11-lamp row mark 15/30/45 minutes
# ----------------------------------------------------------------------------
ROWS = (1, 4, 4, 11, 4)
WEIGHTS = (None, 5, 1, 5, 1)       # hours / hours / minutes / minutes
QUARTER_MARKERS = (3, 6, 9)        # 1-indexed inside the 11-lamp row

def mlu_counts(h, m):
    """lit-lamp count per row, hour and minute rows only"""
    return (h // 5, h % 5, m // 5, m % 5)

def mlu_bits(h, m, s=1):
    """24-bit lamp pattern, reading order top-left to bottom-right."""
    c = mlu_counts(h, m)
    bits = ['1' if s % 2 else '0']
    for n, ln in zip(c, ROWS[1:]):
        bits.append('1' * n + '0' * (ln - n))
    return ''.join(bits)

def bits_to_ab(b):
    return ''.join('B' if c == '1' else 'A' for c in b)

def lit_positions(b):
    return [i + 1 for i, c in enumerate(b) if c == '1']

# ---------------------------------------------------------------- structure --
WP = "https://en.wikipedia.org/wiki/Mengenlehreuhr"
WPDE = "https://de.wikipedia.org/wiki/Berlin-Uhr"

write("mlu_rowlengths_digits.txt", "144114",
      "Mengenlehreuhr row lengths 1,4,4,11,4 concatenated as decimal digits (the 11 contributes '11')",
      WP, "high")
write("mlu_rowlengths_letters_a0.txt", ''.join(A0(n) for n in ROWS),
      "Row lengths 1,4,4,11,4 as letters, A=0 (B E E L E)", WP, "high")
write("mlu_rowlengths_letters_a1.txt", ''.join(A1(n) for n in ROWS),
      "Row lengths 1,4,4,11,4 as letters, A=1 (A D D K D)", WP, "high")

cum = []
t = 0
for n in ROWS:
    t += n
    cum.append(t)                       # 1,5,9,20,24
write("mlu_cumulative_digits.txt", ''.join(str(n) for n in cum),
      "Cumulative lamp totals down the face: 1,5,9,20,24 as digits", WP, "high")
write("mlu_cumulative_letters_a0.txt", ''.join(A0(n) for n in cum),
      "Cumulative lamp totals 1,5,9,20,24 as letters, A=0 (B F J U Y)", WP, "high")
write("mlu_cumulative_letters_a1.txt", ''.join(A1(n) for n in cum),
      "Cumulative lamp totals 1,5,9,20,24 as letters, A=1 (A E I T X)", WP, "high")

# per-lamp weight stream across all 24 fields (seconds lamp given weight 0)
wstream = [0] + [5]*4 + [1]*4 + [5]*11 + [1]*4
write("mlu_lampweights_digits.txt", ''.join(str(n) for n in wstream),
      "Weight of each of the 24 lamps in reading order (0 for the seconds blink, then 5,5,5,5,1,1,1,1,5x11,1,1,1,1)",
      WP, "high")
write("mlu_lampweights_letters_a0.txt", ''.join(A0(n) for n in wstream),
      "Same 24 lamp weights as letters, A=0 (A F F F F B B B B F... )", WP, "high")

# cumulative value carried by each lamp, i.e. the running total if all were lit
runw, acc = [], 0
for w in wstream[1:]:
    acc += w
    runw.append(acc)
write("mlu_lampcumvalue_letters_a0.txt", ''.join(A0(n) for n in runw),
      "Running total of lamp values over the 23 value-bearing lamps (5,10,15,20,21,22,23,24,29,...,83) as letters mod 26, A=0",
      WP, "medium")

write("mlu_quartermarkers_digits.txt", ''.join(str(n) for n in QUARTER_MARKERS),
      "Positions of the three red quarter-hour lamps inside the 11-lamp five-minute row: 3,6,9", WP, "high")
write("mlu_quartermarkers_letters_a1.txt", ''.join(A1(n) for n in QUARTER_MARKERS),
      "Red quarter-hour lamp positions 3,6,9 as letters, A=1 (C F I)", WP, "high")
write("mlu_quarterminutes_digits.txt", "153045",
      "The three quarter-hour minute values the red lamps mark: 15,30,45", WP, "high")

write("mlu_keyfacts_digits.txt",
      "24" "1441 1 4" .replace(" ","") + "2459232880144017061975199519967",
      "Mengenlehreuhr numerics run together: 24 lamps; row lengths 1,4,4,11,4; max hour 24; max minute 59; "
      "max simultaneously-lit value lamps 23; 2880 lamp states; 1440 minute-states; installed 17-06-1975; "
      "decommissioned 1995; re-erected 1996; 7 m tall",
      WP, "low")

# state-space numbers
write("mlu_statespace_digits.txt", "242880144060242",
      "State-space numerics: 24 lamps, 2880 distinct lamp states (24h x 60m x 2 seconds phases), "
      "1440 minute-states, 60 minutes, 24 hours, 2 seconds phases", WP, "high")

# ------------------------------------------------------------------- times --
# label, h, m, note, url, confidence
TIMES = [
 ("wallfall_1853", 18, 53,
  "9 Nov 1989 18:53 - Schabowski takes out Krenz's note at the ADN/press conference",
  "https://www.bpb.de/themen/deutschlandarchiv/302060/2-schabowski-und-die-oeffnung-der-grenzen-am-9-november-1989/",
  "medium"),
 ("wallfall_1850", 18, 50,
  "9 Nov 1989 18:50 - Chronik der Mauer's time for Schabowski's announcement (variant of 18:53)",
  "https://www.chronik-der-mauer.de/en/chronicle/_year1989/_month11/",
  "medium"),
 ("wallfall_1900", 19, 0,
  "9 Nov 1989 ~19:00 - 'shortly before 7 p.m.', the round-number reading of the announcement",
  "https://www.berlin.de/en/history/8482274-8619314-opening-and-fall-of-the-berlin-wall.en.html",
  "medium"),
 ("wallfall_1904", 19, 4,
  "9 Nov 1989 19:04 - ADN distributes the text Schabowski read",
  "https://www.bpb.de/themen/deutschlandarchiv/302060/2-schabowski-und-die-oeffnung-der-grenzen-am-9-november-1989/",
  "medium"),
 ("wallfall_1905", 19, 5,
  "9 Nov 1989 19:05 - AP flash 'GDR opens border'",
  "https://www.chronik-der-mauer.de/en/chronicle/_year1989/_month11/",
  "medium"),
 ("wallfall_2000", 20, 0,
  "9 Nov 1989 20:00 - ARD Tagesschau carries the announcement to East German living rooms",
  "https://www.bpb.de/themen/deutschlandarchiv/302060/2-schabowski-und-die-oeffnung-der-grenzen-am-9-november-1989/",
  "medium"),
 ("wallfall_2120", 21, 20,
  "9 Nov 1989 21:20 - first East Berliners let through at Bornholmer Strasse ('valve solution')",
  "https://en.wikipedia.org/wiki/Bornholmer_Stra%C3%9Fe_border_crossing",
  "medium"),
 ("wallfall_2330", 23, 30,
  "9 Nov 1989 23:30 - Harald Jaeger raises the Bornholmer Strasse barrier completely; the Wall is open",
  "https://en.wikipedia.org/wiki/Bornholmer_Stra%C3%9Fe_border_crossing",
  "high"),
 ("gdr40_1700", 17, 0,
  "7 Oct 1989 17:00 - demonstration forms at the Weltzeituhr on the GDR's 40th anniversary, 33 days before the Wall fell",
  "https://www.ddr-museum.de/en/blog/2017/world-time-clock",
  "medium"),
 ("date_0911", 9, 11,
  "The date 9 November read as a clock time 09:11 (day:month)",
  "https://en.wikipedia.org/wiki/Kryptos", "low"),
 ("date_1109", 11, 9,
  "The date 9 November read as a clock time 11:09 (month:day, US order)",
  "https://en.wikipedia.org/wiki/Kryptos", "low"),
 ("dedication_0311", 3, 11,
  "Kryptos dedication 3 Nov 1990 read as 03:11 (day:month)",
  "https://en.wikipedia.org/wiki/Kryptos", "low"),
 ("dedication_1103", 11, 3,
  "Kryptos dedication 3 Nov 1990 read as 11:03 (month:day)",
  "https://en.wikipedia.org/wiki/Kryptos", "low"),
 ("mlu_install_1706", 17, 6,
  "Mengenlehreuhr installed 17 June 1975, read as 17:06 (day:month)",
  WP, "low"),
 ("wz_open_0930", 9, 30,
  "Weltzeituhr opened 30 Sept 1969, read as 09:30 (month:day)",
  "https://en.wikipedia.org/wiki/World_Clock_(Alexanderplatz)", "low"),
 ("k2coord_0508", 5, 8,
  "K2 longitude 77 deg 08' 44\" W -> local mean solar offset 5h 08m 35s behind UTC, read as 05:08",
  "https://en.wikipedia.org/wiki/Kryptos", "medium"),
 ("k2coord_0844", 8, 44,
  "K2 longitude minutes and seconds 08' 44\" read literally as the clock time 08:44",
  "https://en.wikipedia.org/wiki/Kryptos", "low"),
 ("k2coord_1457", 14, 57,
  "K2 latitude 38 deg 57' N read as a clock time with the degrees reduced mod 24 (38-24=14): 14:57. "
  "Speculative - the latitude has no natural time reading",
  "https://en.wikipedia.org/wiki/Kryptos", "low"),
 ("doc_1754", 17, 54,
  "17:54 - the time displayed in the canonical 1979 Willy Pragher photograph of the clock at Kurfuerstendamm",
  WP, "high"),
 ("doc_1232", 12, 32,
  "12:32 - the worked example used in the Wikipedia 'how to read the clock' section",
  WP, "high"),
 ("doc_1031", 10, 31,
  "10:31 - the time on the lead photograph of the German Berlin-Uhr article",
  WPDE, "high"),
]

for label, h, m, note, url, conf in TIMES:
    b_on  = mlu_bits(h, m, s=1)   # seconds lamp lit (odd second)
    b_off = mlu_bits(h, m, s=0)   # seconds lamp dark (even second)
    c = mlu_counts(h, m)
    write("mlu_t_%s_bits24_sec_on.txt" % label, b_on,
          "Mengenlehreuhr 24-lamp pattern for %02d:%02d, odd second (seconds lamp lit). %s" % (h, m, note),
          url, conf)
    write("mlu_t_%s_bits24_sec_off.txt" % label, b_off,
          "Mengenlehreuhr 24-lamp pattern for %02d:%02d, even second (seconds lamp dark). %s" % (h, m, note),
          url, conf)
    write("mlu_t_%s_ab24.txt" % label, bits_to_ab(b_on),
          "Same 24-lamp pattern for %02d:%02d as an A/B letter stream (A=dark, B=lit), seconds lamp lit" % (h, m),
          url, conf)
    write("mlu_t_%s_rowletters_a0.txt" % label, ''.join(A0(n) for n in c),
          "Lit-lamp counts per row for %02d:%02d (%d,%d,%d,%d) as letters, A=0" % ((h, m) + c),
          url, conf)
    write("mlu_t_%s_rowdigits.txt" % label, ''.join(str(n) for n in c),
          "Lit-lamp counts per row for %02d:%02d as digits (%d,%d,%d,%d)" % ((h, m) + c),
          url, conf)
    write("mlu_t_%s_litpos_letters_a1.txt" % label,
          ''.join(A1(p) for p in lit_positions(b_on)),
          "1-indexed positions of the lit lamps for %02d:%02d (seconds lamp lit) as letters, A=1" % (h, m),
          url, conf)

# ----------------------------------------------------- running/ticking keys --
def tick_rowletters(h0, m0, n_letters):
    out = []
    h, m = h0, m0
    while len(out) < n_letters:
        out += [A0(x) for x in mlu_counts(h, m)]
        m += 1
        if m == 60:
            m = 0; h = (h + 1) % 24
    return ''.join(out[:n_letters])

def tick_lampcount(h0, m0, n):
    out = []
    h, m = h0, m0
    for _ in range(n):
        out.append(A0(sum(mlu_counts(h, m))))
        m += 1
        if m == 60:
            m = 0; h = (h + 1) % 24
    return ''.join(out)

def tick_bits(h0, m0, n_bits):
    out = ''
    h, m = h0, m0
    while len(out) < n_bits:
        out += mlu_bits(h, m, s=1)
        m += 1
        if m == 60:
            m = 0; h = (h + 1) % 24
    return out[:n_bits]

START_POINTS = [
 ("0000", 0, 0,  "midnight, the clock's all-dark zero state"),
 ("1853", 18, 53, "9 Nov 1989 18:53, Schabowski's note"),
 ("1900", 19, 0,  "9 Nov 1989 19:00"),
 ("2330", 23, 30, "9 Nov 1989 23:30, Bornholmer Strasse opens"),
 ("1700", 17, 0,  "7 Oct 1989 17:00, the Weltzeituhr demonstration"),
 ("1200", 12, 0,  "noon"),
 ("1754", 17, 54, "the 1979 photograph time"),
]
for lbl, h, m, note in START_POINTS:
    write("mlu_tick_%s_rowletters_97.txt" % lbl, tick_rowletters(h, m, 97),
          "Mengenlehreuhr ticking keystream: 4 letters per minute (5h,1h,5m,1m lit counts, A=0) "
          "for successive minutes from %02d:%02d - %s. Truncated to 97 = len(K4)." % (h, m, note),
          WP, "medium")
    write("mlu_tick_%s_lampcount_97.txt" % lbl, tick_lampcount(h, m, 97),
          "Mengenlehreuhr ticking keystream: total lit lamps (0-23 -> A-X) for each successive minute "
          "from %02d:%02d - %s. 97 letters." % (h, m, note), WP, "medium")
    write("mlu_tick_%s_bits97.txt" % lbl, tick_bits(h, m, 97),
          "Mengenlehreuhr ticking bitstream: the 24-lamp pattern concatenated minute by minute from "
          "%02d:%02d, first 97 bits - %s." % (h, m, note), WP, "medium")

write("mlu_day_lampcount_1440.txt", tick_lampcount(0, 0, 1440),
      "Total lit lamps (hour+minute rows, 0-23 -> A-X) for every minute of a full 24-hour day, 00:00 to 23:59. "
      "1440 letters; use any offset as a running key.", WP, "medium")
write("mlu_day_rowletters_5760.txt", tick_rowletters(0, 0, 5760),
      "Per-row lit counts (4 letters per minute, A=0) for every minute of a full day. 5760 letters.",
      WP, "medium")

# --------------------------------------------------------- Urania-Weltzeituhr
WZ = "https://en.wikipedia.org/wiki/World_Clock_(Alexanderplatz)"
write("wz_hours_1_24_letters_a1.txt", ''.join(A1(n) for n in range(1, 25)),
      "The 24 hour numerals that revolve around the Weltzeituhr's rotunda, 1..24, as letters A=1 (A..X)",
      WZ, "high")
write("wz_hours_1_24_digits.txt", ''.join(str(n) for n in range(1, 25)),
      "The 24 hour numerals 1..24 as a digit string", WZ, "high")
write("wz_zone_offsets_letters_a0.txt",
      ''.join(A0(n % 24) for n in list(range(-11, 13))),
      "The 24 main time-zone offsets carried by the 24 faces, -11..+12, reduced mod 24 and mapped A=0",
      WZ, "medium")
write("wz_keyfacts_digits.txt", "2414816101204201969093019972719515",
      "Weltzeituhr numerics run together: 24 faces, 148 cities, 16 tons, 10 m high, 120 engineers, "
      "4 subsidiary analogue clocks, 20 cities added in 1997, opened 1969-09-30, 1997 overhaul, "
      "base cylinder 2.7 m high 1.5 m diameter", WZ, "medium")
write("wz_icositetragon_digits.txt", "24",
      "The cross-section of the Weltzeituhr column is a regular icositetragon: 24 sides", WZ, "high")

# ------------------------------------------------------------ compass rose --
# The Weltzeituhr stands on a painted windrose; Kryptos stands on its own compass rose;
# and K4 positions 22-34 spell EASTNORTHEAST, which IS a compass point (ENE, 067.5 deg).
ROSE = "https://en.wikipedia.org/wiki/World_Clock_(Alexanderplatz)"

P16 = ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
W16 = ["NORTH","NORTHNORTHEAST","NORTHEAST","EASTNORTHEAST","EAST","EASTSOUTHEAST",
       "SOUTHEAST","SOUTHSOUTHEAST","SOUTH","SOUTHSOUTHWEST","SOUTHWEST","WESTSOUTHWEST",
       "WEST","WESTNORTHWEST","NORTHWEST","NORTHNORTHWEST"]
G16 = ["NORD","NORDNORDOST","NORDOST","OSTNORDOST","OST","OSTSUEDOST","SUEDOST","SUEDSUEDOST",
       "SUED","SUEDSUEDWEST","SUEDWEST","WESTSUEDWEST","WEST","WESTNORDWEST","NORDWEST","NORDNORDWEST"]
P32 = ["N","NBE","NNE","NEBN","NE","NEBE","ENE","EBN","E","EBS","ESE","SEBE","SE","SEBS","SSE","SBE",
       "S","SBW","SSW","SWBS","SW","SWBW","WSW","WBS","W","WBN","WNW","NWBW","NW","NWBN","NNW","NBW"]

write("rose_16_abbrev.txt", ''.join(P16),
      "The 16 compass-rose point abbreviations concatenated, starting at north and going clockwise", ROSE, "high")
write("rose_32_abbrev.txt", ''.join(P32),
      "The 32 compass-rose point abbreviations concatenated (B = 'by'), clockwise from north", ROSE, "high")
write("rose_16_words_en.txt", ''.join(W16),
      "The 16 compass-rose points spelled out in full English, clockwise from north. "
      "K4 positions 22-34 spell EASTNORTHEAST, which is point 4 of this list", ROSE, "high")
write("rose_16_words_de.txt", ''.join(G16),
      "The 16 compass-rose points spelled out in full German (UE for umlaut-U), clockwise from north; "
      "OSTNORDOST is the German for the K4 crib EASTNORTHEAST", ROSE, "medium")
write("rose_16_words_en_from_ene.txt", ''.join(W16[3:] + W16[:3]),
      "Same 16 full English compass points but rotated to start at EASTNORTHEAST, the K4 crib at positions 22-34",
      ROSE, "medium")
write("rose_16_bearings_digits.txt", ''.join("%04d" % round(i*225) for i in range(16)),
      "Bearings of the 16 compass points in hundredths of a degree x10 (0000,0225,0450,0675,...) - "
      "i.e. 0, 22.5, 45, 67.5 ... degrees", ROSE, "high")
write("rose_32_bearings_digits.txt", ''.join("%05d" % round(i*1125) for i in range(32)),
      "Bearings of the 32 compass points, in units of 1/100 degree (00000,01125,02250,...)", ROSE, "medium")

# --------------------------------------------------------------- geometry ---
def bearing(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1)*math.sin(p2) - math.sin(p1)*math.cos(p2)*math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360

KRY = (38.95227, -77.14573)
MLUC = (52.505153, 13.338878)
WZC = (52.5212, 13.4133)
b_mlu = bearing(*KRY, *MLUC)
b_wz = bearing(*KRY, *WZC)
print("initial great-circle bearing Kryptos -> Mengenlehreuhr : %.3f deg" % b_mlu)
print("initial great-circle bearing Kryptos -> Weltzeituhr    : %.3f deg" % b_wz)
write("geo_bearings_digits.txt",
      "%04d%04d" % (round(b_mlu*10), round(b_wz*10)),
      "Initial great-circle bearings from the Kryptos sculpture (38.95227,-77.14573) to the "
      "Mengenlehreuhr (%.3f deg) and to the Weltzeituhr (%.3f deg), in tenths of a degree" % (b_mlu, b_wz),
      WZ, "high")

# --------------------------------------------------------------- manifest ---
mp = os.path.join(OUT, "MANIFEST.tsv")
new = not os.path.exists(mp)
with open(mp, "w") as f:
    f.write("filename\tdescription\tsource_url\tconfidence\n")
    for row in MAN:
        f.write("\t".join(str(x).replace("\t", " ").replace("\n", " ") for x in row) + "\n")
print("wrote %d keystream files + MANIFEST.tsv to %s" % (len(MAN), OUT))
