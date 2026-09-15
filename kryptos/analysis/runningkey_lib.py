"""Shared library for the K4 running-key / autokey tests.

Conventions
-----------
* Positions are 0-indexed internally; the report converts to 1-indexed.
* A cipher "combo" is (family, pt_alphabet, ct_alphabet, key_alphabet) with
    p = A_p.index(P), c = A_c.index(C), k = A_k.index(K)
    Vigenere         : c = p + k   -> k = c - p
    Beaufort         : c = k - p   -> k = c + p
    Variant Beaufort : c = p - k   -> k = p - c
  Each alphabet is either the plain A-Z or the KRYPTOS keyed alphabet.
  (K1/K2 on the sculpture are Vigenere with pt=keyed, ct=keyed, key=keyed;
  this is verified in verify_k1_k2() below.)
"""
import re, os, itertools

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

PLAIN = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KEYED = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
ALPHAS = {"plain": PLAIN, "keyed": KEYED}
FAMILIES = ["vigenere", "beaufort", "varbeaufort"]

def letters(s):
    return re.sub(r"[^A-Z]", "", s.upper())

# ---------------------------------------------------------------- data ----
def _read(name):
    with open(os.path.join(DATA, name)) as f:
        return f.read()

K4_CT = letters(_read("k4_ciphertext.txt"))
assert len(K4_CT) == 97

_pt_lines = [l for l in _read("k1_k3_plaintext.txt").splitlines() if l and not l.startswith("#")]
K1_PT, K2_PT, K3_PT = (letters(l) for l in _pt_lines)
K2_PT_ORIG = K2_PT[:-len("LAYERTWO")] + "IDBYROWS"   # pre-2006 reading (no X before it)
assert K2_PT.endswith("XLAYERTWO")
K2_PT_ORIG = K2_PT[:-len("XLAYERTWO")] + "IDBYROWS"

def _panels():
    txt = _read("sculpture_panels.txt")
    left, right, cur = [], [], None
    for l in txt.splitlines():
        if l.startswith("#"): continue
        if l.strip() == "[LEFT]": cur = left; continue
        if l.strip() == "[RIGHT]": cur = right; continue
        if cur is not None and l.strip(): cur.append(l)
    return left, right

LEFT_ROWS, RIGHT_ROWS = _panels()
LEFT_RAW = "".join(LEFT_ROWS)                     # includes '?' chars
LEFT_ALL = letters(LEFT_RAW)                       # 865 letters
# Sections by row: K1 = rows 0-1, K2 = rows 2-13 (contains three '?' that are part of K2),
# K3 = rows 14.. up to the '?' in row 24, K4 = after that '?'.
K1_CT = letters("".join(LEFT_ROWS[0:2]))
K2_CT = letters("".join(LEFT_ROWS[2:14]))
_tail = "".join(LEFT_ROWS[14:])
K3_CT, K4_CT_PANEL = (letters(x) for x in _tail.split("?"))
assert K4_CT_PANEL == K4_CT, (K4_CT_PANEL, K4_CT)
# Known: K2 CT on the sculpture is 1 char short of the 2006-corrected plaintext (dropped 'S'
# in ciphertext; equivalently a dropped X in plaintext pre-correction).  K3 CT is 336.

TABLEAU_RAW = "".join(RIGHT_ROWS)                  # rows incl. row labels, header rows, nbsp
TABLEAU = letters(TABLEAU_RAW)                      # 867 letters (physical, with extra L)
def ideal_tableau():
    rows = [PLAIN + "ABCD"]
    for i in range(26):
        rot = KEYED[i:] + KEYED[:i]
        rows.append(PLAIN[i] + rot + rot[:4])
    rows.append(PLAIN + "ABCD")
    return "".join(rows)
TABLEAU_IDEAL = ideal_tableau()

MORSE_WORDS = ["VIRTUALLY INVISIBLE", "SHADOW FORCES", "LUCID MEMORY", "T IS YOUR POSITION",
               "SOS", "RQ", "DIGETAL INTERPRETATU"]
MORSE = letters("".join(MORSE_WORDS))
# Physical order on the slabs differs by source; also provide the commonly cited order.
MORSE_ALT = letters("".join(["VIRTUALLY INVISIBLE", "DIGETAL INTERPRETATU", "SHADOW FORCES",
                             "LUCID MEMORY", "T IS YOUR POSITION", "SOS", "RQ"]))

def strip_x(s):  return s.replace("X", "")

# The candidate key-text corpus.  name -> text
def corpus():
    c = {}
    c["K1_pt"] = K1_PT
    c["K2_pt"] = K2_PT
    c["K2_pt_IDBYROWS"] = K2_PT_ORIG
    c["K3_pt"] = K3_PT
    c["K1K2K3_pt"] = K1_PT + K2_PT + K3_PT
    c["K1K2K3_pt_IDBYROWS"] = K1_PT + K2_PT_ORIG + K3_PT
    c["K1_ct"] = K1_CT
    c["K2_ct"] = K2_CT
    c["K3_ct"] = K3_CT
    c["K4_ct"] = K4_CT
    c["K1K2K3_ct"] = K1_CT + K2_CT + K3_CT
    c["left_panel_all_ct"] = LEFT_ALL                # K1..K4 ct, 865 letters
    c["K3K4_ct_lower_panel"] = K3_CT + K4_CT
    c["tableau_physical"] = TABLEAU
    c["tableau_ideal"] = TABLEAU_IDEAL
    c["tableau_rows_no_labels"] = letters("".join(r[1:] for r in RIGHT_ROWS))
    c["morse"] = MORSE
    c["morse_alt_order"] = MORSE_ALT
    c["keywords"] = "PALIMPSESTABSCISSAKRYPTOS"
    c["K1K2K3_pt_plus_keywords"] = "PALIMPSEST" + K1_PT + "ABSCISSA" + K2_PT + K3_PT
    base = dict(c)
    for n, t in base.items():
        if "X" in t and "tableau" not in n:
            c[n + "_noX"] = strip_x(t)
    base = dict(c)
    for n, t in base.items():
        c[n + "_rev"] = t[::-1]
    return c

# ------------------------------------------------------------- ciphers ----
def combos():
    for fam in FAMILIES:
        for ap in ("plain", "keyed"):
            for ac in ("plain", "keyed"):
                for ak in ("plain", "keyed"):
                    yield (fam, ap, ac, ak)

def combo_name(cb):
    fam, ap, ac, ak = cb
    return f"{fam}/pt={ap}/ct={ac}/key={ak}"

def key_index(fam, p, c):
    if fam == "vigenere":    return (c - p) % 26
    if fam == "beaufort":    return (c + p) % 26
    if fam == "varbeaufort": return (p - c) % 26
    raise ValueError(fam)

def ct_index(fam, p, k):
    if fam == "vigenere":    return (p + k) % 26
    if fam == "beaufort":    return (k - p) % 26
    if fam == "varbeaufort": return (p - k) % 26
    raise ValueError(fam)

def pt_index(fam, c, k):
    if fam == "vigenere":    return (c - k) % 26
    if fam == "beaufort":    return (k - c) % 26
    if fam == "varbeaufort": return (c + k) % 26
    raise ValueError(fam)

def derive_key_letter(cb, P, C):
    fam, ap, ac, ak = cb
    return ALPHAS[ak][key_index(fam, ALPHAS[ap].index(P), ALPHAS[ac].index(C))]

def decrypt_letter(cb, C, K):
    fam, ap, ac, ak = cb
    return ALPHAS[ap][pt_index(fam, ALPHAS[ac].index(C), ALPHAS[ak].index(K))]

def encrypt_letter(cb, P, K):
    fam, ap, ac, ak = cb
    return ALPHAS[ac][ct_index(fam, ALPHAS[ap].index(P), ALPHAS[ak].index(K))]

def decrypt(cb, ct, keystream):
    return "".join(decrypt_letter(cb, c, k) for c, k in zip(ct, keystream))

# --------------------------------------------------------------- cribs ----
import json
def cribs():
    j = json.loads(_read("cribs.json"))
    d = {}
    for cr in j["cribs"]:
        for i, (c, p) in enumerate(zip(cr["ct"], cr["pt"])):
            pos = cr["pos"] - 1 + i
            assert K4_CT[pos] == c, (pos, c, K4_CT[pos])
            d[pos] = p
    return d
CRIBS = cribs()                      # 0-indexed pos -> plaintext letter (24 entries)
BLOCK1 = list(range(21, 34))         # 1-indexed 22..34, EASTNORTHEAST
BLOCK2 = list(range(63, 74))         # 1-indexed 64..74, BERLINCLOCK
assert set(CRIBS) == set(BLOCK1) | set(BLOCK2)

def required_key(cb):
    """(block1_key_13, block2_key_11) required at the crib positions under combo cb."""
    b1 = "".join(derive_key_letter(cb, CRIBS[i], K4_CT[i]) for i in BLOCK1)
    b2 = "".join(derive_key_letter(cb, CRIBS[i], K4_CT[i]) for i in BLOCK2)
    return b1, b2

# ------------------------------------------------------------ checks ----
def verify_k1_k2():
    """Sanity: re-encrypt K1/K2 plaintext with the known keys under the K1/K2 combo and
    compare to the sculpture ciphertext."""
    cb = ("vigenere", "keyed", "keyed", "keyed")
    out = {}
    k1 = "".join(encrypt_letter(cb, p, "PALIMPSEST"[i % 10]) for i, p in enumerate(K1_PT))
    out["K1"] = (k1 == K1_CT, len(K1_PT), len(K1_CT))
    k2 = "".join(encrypt_letter(cb, p, "ABSCISSA"[i % 8]) for i, p in enumerate(K2_PT))
    # sculpture K2 ct is missing one letter near the end; compare prefix
    n = 0
    while n < min(len(k2), len(K2_CT)) and k2[n] == K2_CT[n]: n += 1
    out["K2"] = (n, len(k2), len(K2_CT), k2[n:], K2_CT[n:])
    out["K3_is_anagram_of_pt"] = sorted(K3_CT) == sorted(K3_PT)
    return out

# --------------------------------------------------- English scoring ----
_QUAD = None
def english_score(s):
    """Cheap English plausibility: log-prob under a small letter/bigram model built from
    K1-K3 plaintext plus common-English bigram frequencies is overkill; use a simple
    scoring of common bigrams/trigrams and vowel ratio."""
    s = letters(s)
    if not s: return 0.0
    common_bi = ["TH","HE","IN","ER","AN","RE","ON","AT","EN","ND","TI","ES","OR","TE","OF","ED","IS","IT","AL","AR","ST","TO","NT","NG","SE","HA","AS","OU","IO","LE","VE","CO","ME","DE","HI","RI","RO","IC","NE","EA","RA","CE"]
    common_tri = ["THE","AND","ING","ENT","ION","HER","FOR","THA","NTH","INT","ERE","TIO","TER","EST","ERS","ATI","HAT","ATE","ALL","ETH","HES","VER","HIS","OFT","ITH","FTH","STH","OTH","RES","ONT"]
    sc = 0.0
    for i in range(len(s)-1):
        if s[i:i+2] in common_bi: sc += 1
    for i in range(len(s)-2):
        if s[i:i+3] in common_tri: sc += 2
    return sc / len(s)

def hamming(a, b):
    return sum(x != y for x, y in zip(a, b))

def pos1(i):  # 0-indexed -> 1-indexed
    return i + 1
