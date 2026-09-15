#!/usr/bin/env python3
"""
antipodes_agency_verify.py  —  verification code for lateral/antipodes_agency.md

Three independent checks, all reproducible from public data:

  PART 1  Rebuild the Antipodes Latin ("Kryptos") side from the only public
          full transcription (scirealm.org/Antipodes.html, John Wilson's page),
          re-derive the segment ordering, and diff it letter-for-letter against
          the Kryptos left panel (data/sculpture_panels.txt).

  PART 2  Test the claim (scirealm) that Antipodes spells UNDERGROUND correctly
          where Kryptos spells UNDERGRUUND, by re-encrypting K2 both ways under
          Quagmire III / KRYPTOS alphabet / key ABSCISSA.

  PART 3  Recover the exact Cyrillic Projector cipher relation from its
          ciphertext and plaintext (lateral/keystreams/cyrillic_*), given the
          published keyed alphabet TEN' and key JBASGT, and decide which
          Quagmire variant it is.  Round-trip verified.

NOTE: nothing here is a K4 attack.  This is documentation verification only.
"""
import os, re, sys, json, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ----------------------------------------------------------------------------
# Kryptos reference data
# ----------------------------------------------------------------------------
def load_panels():
    txt = open(os.path.join(ROOT, "data", "sculpture_panels.txt"), encoding="utf-8").read()
    left = []
    mode = None
    for line in txt.splitlines():
        s = line.strip()
        if s.startswith("#"):
            continue
        if s == "[LEFT]":
            mode = "L"; continue
        if s.startswith("[") and s.endswith("]"):
            mode = None if s != "[LEFT]" else "L"; continue
        if mode == "L" and s:
            left.append(s)
    return left

def load_pt():
    txt = open(os.path.join(ROOT, "data", "k1_k3_plaintext.txt"), encoding="utf-8").read()
    segs = [l.strip() for l in txt.splitlines() if l.strip() and not l.startswith("#")]
    return segs  # K1, K2, K3 plaintexts

LEFT_ROWS = load_panels()
LEFT = "".join(LEFT_ROWS)
K1_CT = LEFT[:63]
K2_CT = LEFT[63:63+372]           # 369 letters + 3 '?'
K3_CT = LEFT[63+372:63+372+337]   # 336 letters + 1 '?'
K4_CT = LEFT[63+372+337:]
assert len(K4_CT) == 97, len(K4_CT)
assert K4_CT.startswith("OBKR") and K4_CT.endswith("EKCAR")

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def keyed(kw, alpha=ALPHA):
    out = []
    for c in kw + alpha:
        if c not in out:
            out.append(c)
    return "".join(out)
KRY = keyed("KRYPTOS")

def quag3_encrypt(pt, key, alpha=KRY):
    """K1/K2 system: pt/ct/key alphabets all `alpha` (Quagmire III)."""
    idx = {c: i for i, c in enumerate(alpha)}
    out = []
    for i, p in enumerate(pt):
        k = key[i % len(key)]
        out.append(alpha[(idx[p] + idx[k]) % len(alpha)])
    return "".join(out)

def quag3_decrypt(ct, key, alpha=KRY):
    idx = {c: i for i, c in enumerate(alpha)}
    out = []
    for i, c in enumerate(ct):
        k = key[i % len(key)]
        out.append(alpha[(idx[c] - idx[k]) % len(alpha)])
    return "".join(out)

# ----------------------------------------------------------------------------
# PART 1 — Antipodes Latin side
# ----------------------------------------------------------------------------
# Transcription source: http://scirealm.org/Antipodes.html  ("John's Antipodes page"),
# rows exactly as that page tabulates them.  Row *breaks* are that page's layout and
# are NOT asserted to be the sculpture's carved rows; the LETTER SEQUENCE is the datum.
# '.' = a carved dot, '  ' (double space) = the carved separator gap.
ANTIPODES_LATIN_ROWS = [
    "ENDYAHROHNLSRHEOCPTEOIBIDYSHNAIACH",
    "TNREYULDSLLSLLNOHSNOSMRWXMNETPRNG",
    "ATIHNRARPESLNNELEBLPIIACAEWMTWNDITE",
    "ENRAHCTENEUDRETNHAEOETFOLSEDTIWENH",
    "AEIOYTEYQHEENCTAYCREIFTBRSPAMHHEWE",
    "NATAMATEGYEERLBTEEFOASFIOTUETUAEOT",
    "OARMAEERTNRTIBSEDDNIAAHTTMSTEWPIER",
    "OAGRIEWFEBAECTDDHILCEIHSITEGOEAOSDD",
    "RYDLORITRKLMLEHAGTDHARDPNEOHMGFMF",
    "EUHEECDMRIPFEIMEHNLSSTTRTVDOHW?OBK",
    "RUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTW",
    "TQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZF",
    "PKWGDKZXTJCDIGKUHUAUEKCAR  EMUFPHZL",
    "RFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQV",
    "YUVLLTREVJYQTMKYRDMFDVFPJUDEEHZWE",
    "TZYVGWHKKQETGFQJNCEGGWHKK?DQMCPFQ",
    "ZDQMMIAGPFXHQRLGTIMVMZJANQLVKQEDA",
    "GDVFRPJUNGEUNAQZGZLECGYUXUEENJTBJL",
    "BQCETBJDFHRRYIZETKZEMVDUFKSJHKFWHK",
    "UWQLSZFTIHHDDDUVH?DWKBFUFPWNTDFIYC",
    "UQZEREEVLDKFEZMOQQJLTTUGSYQPFEUNLA",
    "VIDXFLGGTEZ?FKZBS.F.DQVGOGIPUFXHHDRKF",
    "FHQNTGPUAECNUVPDJMQCLQUMUNEDFQELZ",
    "ZVRRGKFFVOEEXBDMVPNFQXEZLGREDNQFM",
    "PNZGLFLPMRJQYALMGNUVPDXVKPDQUMEBE",
    "DMHDAFMJGZNUPLGEWJLLAETGENDYAHROH",
    "NLSRHEOCPTEOIBIDYSHNAIACHTNREYULDSL",
    "LSLLNOHSNOSMRWXMNETPRNGATIHNRARPE",
    "SLNNELEBLPIIACAEWMTWNDITEENRAHCTEN",
    "EUDRETNHAEOETFOLSEDTIWENHAEIOYTEYQ",
    "HEENCTAYCREIFTBRSPAMHHEWENATAMATEG",
    "YEERLBTEEFOASFIOTUETUAEOTOARMAEERT",
    "NRTIBSEDDNIAAHTTMSTEWPIEROAGRIEWFEB",
    "AECTDDHILCEIHSITEGOEAOSDDRYDLORITRKL",
    "MLEHAGTDHARDPNEOHMGFMFEUHEECDMRIP",
    "FEIMEHNLSSTTRTVDOHW?OBKRUOXOGHULBS",
    "OLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZ",
    "WATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJ",
    "CDIGKUHUAUEKCAREMUFPHZLRFAXYUSDJKZ",
    "LDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJY",
    "QTMKYRDMFDVFPJUDEEHZWETZYVGWHKKQ",
    "ETGFQJNCEGGWHKK?DQMCPFQZDQMMIAGPF",
    "XHQRLGTIMVMZJANQLVKQEDAGDVFRPJUNG",
    "EUNAQZGZLECGYUXUEENJTBJLBQCETBJDFH",
    "RRYIZETKZEMVDUFKSJHKFWHKUWQLSZFTIH",
    "HDDDUVH?DWKBFUFPWNTDFIYCUQZEREEVLD",
    "KFEZMOQQJLTTUGSYQPFEUNLAVIDXFLGGTE",
]

# The Antipodes tableaux, TRANSCRIBED from the same source.  Both faces carry a
# 32-row x 33-column UNLABELLED rotation table (Kryptos's Latin tableau is 26
# labelled rows of 30 plus two header rows, and carries the notorious extra L).
ANTIPODES_LATIN_TABLEAU = [
    "KRYPTOSABCDEFGHIJLMNQUVWXZKRYPTOS", "RYPTOSABCDEFGHIJLMNQUVWXZKRYPTOSA",
    "YPTOSABCDEFGHIJLMNQUVWXZKRYPTOSAB", "PTOSABCDEFGHIJLMNQUVWXZKRYPTOSABC",
    "TOSABCDEFGHIJLMNQUVWXZKRYPTOSABCD", "OSABCDEFGHIJLMNQUVWXZKRYPTOSABCDE",
    "SABCDEFGHIJLMNQUVWXZKRYPTOSABCDEF", "ABCDEFGHIJLMNQUVWXZKRYPTOSABCDEFG",
    "BCDEFGHIJLMNQUVWXZKRYPTOSABCDEFGH", "CDEFGHIJLMNQUVWXZKRYPTOSABCDEFGHI",
    "DEFGHIJLMNQUVWXZKRYPTOSABCDEFGHIJ", "EFGHIJLMNQUVWXZKRYPTOSABCDEFGHIJL",
    "FGHIJLMNQUVWXZKRYPTOSABCDEFGHIJLM", "GHIJLMNQUVWXZKRYPTOSABCDEFGHIJLMN",
    "HIJLMNQUVWXZKRYPTOSABCDEFGHIJLMNQ", "IJLMNQUVWXZKRYPTOSABCDEFGHIJLMNQU",
    "JLMNQUVWXZKRYPTOSABCDEFGHIJLMNQUV", "LMNQUVWXZKRYPTOSABCDEFGHIJLMNQUVW",
    "MNQUVWXZKRYPTOSABCDEFGHIJLMNQUVWX", "NQUVWXZKRYPTOSABCDEFGHIJLMNQUVWXZ",
    "QUVWXZKRYPTOSABCDEFGHIJLMNQUVWXZK", "UVWXZKRYPTOSABCDEFGHIJLMNQUVWXZKR",
    "VWXZKRYPTOSABCDEFGHIJLMNQUVWXZKRY", "WXZKRYPTOSABCDEFGHIJLMNQUVWXZKRYP",
    "XZKRYPTOSABCDEFGHIJLMNQUVWXZKRYPT", "ZKRYPTOSABCDEFGHIJLMNQUVWXZKRYPTO",
    "KRYPTOSABCDEFGHIJLMNQUVWXZKRYPTOS", "RYPTOSABCDEFGHIJLMNQUVWXZKRYPTOSA",
    "YPTOSABCDEFGHIJLMNQUVWXZKRYPTOSAB", "PTOSABCDEFGHIJLMNQUVWXZKRYPTOSABC",
    "TOSABCDEFGHIJLMNQUVWXZKRYPTOSABCD", "OSABCDEFGHIJLMNQUVWXZKRYPTOSABCDE",
]
ANTIPODES_CYR_TABLEAU = [
    "ТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТ", "ЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕ",
    "НЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕН", "ЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬ",
    "АБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬА", "БВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБ",
    "ВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВ", "ГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГ",
    "ДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГД", "ЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖ",
    "ЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗ", "ИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИ",
    "ЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙ", "КЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙК",
    "ЛМОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛ", "МОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМ",
    "ОПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМО", "ПРСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОП",
    "РСУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПР", "СУФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПРС",
    "УФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПРСУ", "ФХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПРСУФ",
    "ХШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПРСУФХ", "ШЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШ",
    "ЦЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦ", "ЧЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧ",
    "ЩЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩ", "ЪЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪ",
    "ЫЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫ", "ЭЮЯТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭ",
    "ЮЯТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮ", "ЯТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯ",
]


def part1():
    print("=" * 78)
    print("PART 1 — Antipodes Latin side vs the Kryptos left panel")
    print("=" * 78)

    raw = "".join(ANTIPODES_LATIN_ROWS)          # keeps '.' and ' '
    glyphs = [c for c in raw]
    n_dot = raw.count(".")
    n_gap = raw.count(" ")
    seq = raw.replace(" ", "").replace(".", "")  # letters + '?'
    letters = "".join(c for c in seq if c.isalpha())
    print(f"transcription rows                : {len(ANTIPODES_LATIN_ROWS)}")
    print(f"glyphs incl. dots/spaces          : {len(raw)}")
    print(f"carved dots '.'                   : {n_dot}  (Kryptos has 0)")
    print(f"space glyphs                      : {n_gap}")
    print(f"letters + '?'                     : {len(seq)}")
    print(f"letters only                      : {len(letters)}")
    print(f"'?' count                          : {seq.count('?')}   (Kryptos left panel: {LEFT.count('?')})")

    # -- reconstruct the expected stream from Kryptos segments, per Elonka's stated order
    order = ["K3", "K4", "GAP", "K1", "K2", "K3", "K4", "K1", "K2"]
    SEG = {"K1": K1_CT, "K2": K2_CT, "K3": K3_CT, "K4": K4_CT}
    expected = ""
    bounds = []      # (segment name, start offset in `expected`)
    for o in order:
        if o == "GAP":
            bounds.append(("GAP", len(expected)))
            continue
        bounds.append((o, len(expected)))
        expected += SEG[o]
    print(f"\nexpected order                    : {' '.join(order)}")
    print(f"expected length if untruncated    : {len(expected)}")
    print(f"actual Antipodes length           : {len(seq)}  -> truncation point inside final K2")

    m = min(len(seq), len(expected))
    diffs = [(i, expected[i], seq[i]) for i in range(m) if expected[i] != seq[i]]
    print(f"\nletterwise diff over first {m} glyphs: {len(diffs)} mismatch(es)")
    for i, e, a in diffs:
        seg = [b for b in bounds if b[1] <= i and b[0] != "GAP"][-1]
        off = i - seg[1]
        print(f"  Antipodes stream index {i:4d}  (= {seg[0]} offset {off}, 1-indexed {off+1}) "
              f"Kryptos '{e}' -> Antipodes '{a}'")
        print(f"    Kryptos   ...{expected[max(0,i-12):i]}[{e}]{expected[i+1:i+13]}...")
        print(f"    Antipodes ...{seq[max(0,i-12):i]}[{a}]{seq[i+1:i+13]}...")

    # -- where do the dots and the gap fall?
    print("\n--- dot and gap placement (relative to the reconstructed stream) ---")
    pos = 0
    seen_gap = False
    for ch in raw:
        if ch == ".":
            seg = [b for b in bounds if b[1] < pos and b[0] != "GAP"][-1]
            print(f"  dot after stream index {pos-1} (= {seg[0]} offset {pos-1-seg[1]}, "
                  f"1-indexed {pos-seg[1]})  context: ...{seq[max(0,pos-10):pos]}·{seq[pos:pos+10]}...")
        elif ch == " ":
            if not seen_gap:
                before = [b for b in bounds if b[1] < pos and b[0] != "GAP"][-1]
                after = [b for b in bounds if b[1] >= pos and b[0] != "GAP"][0]
                print(f"  GAP at stream index {pos}: between the end of {before[0]} "
                      f"(the first K4, ending at {pos-1}) and the start of {after[0]}")
                seen_gap = True
        else:
            pos += 1
    # the second K4 -> K1 junction, which Elonka says has NO gap
    j = 1206 + 97
    print(f"  second K4/K1 junction at stream index {j}: "
          f"...{seq[j-12:j]}|{seq[j:j+12]}...  (no gap carved)")

    # -- the Antipodes Latin TABLEAU (scirealm transcription): 32 rows x 33 columns
    print("\n--- the Antipodes Latin tableau vs an ideal rotation table ---")
    ideal = [(KRY * 3)[i:i + 33] for i in range(32)]
    bad = [(i, a, b) for i, (a, b) in enumerate(zip(ideal, ANTIPODES_LATIN_TABLEAU)) if a != b]
    print(f"  rows: {len(ANTIPODES_LATIN_TABLEAU)}   widths: {sorted(set(len(r) for r in ANTIPODES_LATIN_TABLEAU))}")
    print(f"  rows differing from an ideal 32x33 KRYPTOS rotation table: {len(bad)}")
    for i, a, b in bad:
        print(f"    row {i}: ideal {a} / carved {b}")
    print(f"  total letters: {sum(len(r) for r in ANTIPODES_LATIN_TABLEAU)}  (26x33 + 6x33 = 1056 for an ideal table)")
    print("  Kryptos, by contrast, carries an extra L at the end of tableau row N (867 letters vs 866).")

    # -- the Antipodes Cyrillic tableau
    KC = "ТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯ"
    idealc = [(KC * 3)[i:i + 33] for i in range(32)]
    badc = [(i, a, b) for i, (a, b) in enumerate(zip(idealc, ANTIPODES_CYR_TABLEAU)) if a != b]
    print(f"\n--- the Antipodes Cyrillic tableau vs an ideal ТЕНЬ rotation table ---")
    print(f"  rows: {len(ANTIPODES_CYR_TABLEAU)}   rows differing from ideal: {len(badc)}")

    # -- does K4 appear twice, identically, and identically to Kryptos?
    occ = [mm.start() for mm in re.finditer("(?=OBKRUOXOGHULBSOLIFBBWFLRV)", seq)]
    print(f"\nK4 occurrences in the Antipodes stream: {len(occ)} at {occ}")
    for o in occ:
        got = seq[o:o + 97]
        print(f"  offset {o}: len {len(got)}  identical to Kryptos K4: {got == K4_CT}")
        if got != K4_CT:
            for j, (a, b) in enumerate(zip(K4_CT, got)):
                if a != b:
                    print(f"     pos {j+1}: Kryptos {a} vs Antipodes {b}")
    return seq, expected, bounds


# ----------------------------------------------------------------------------
# PART 2 — the UNDERGROUND / UNDERGRUUND claim
# ----------------------------------------------------------------------------
def part2():
    print()
    print("=" * 78)
    print("PART 2 — does Antipodes carve UNDERGROUND where Kryptos carves UNDERGRUUND?")
    print("=" * 78)
    pts = load_pt()
    k2_pt = pts[1]
    i = k2_pt.index("UNDERGRUUND")
    print(f"K2 plaintext 0-indexed position of 'UNDERGRUUND' : {i} (1-indexed {i+1})")

    alt = k2_pt[:i] + "UNDERGROUND" + k2_pt[i + 11:]
    ct_true = quag3_encrypt(k2_pt, "ABSCISSA")
    ct_alt = quag3_encrypt(alt, "ABSCISSA")
    d = [(j, a, b) for j, (a, b) in enumerate(zip(ct_true, ct_alt)) if a != b]
    print(f"re-encrypting both plaintexts under Quagmire III / KRYPTOS / ABSCISSA differs at exactly: {d}")
    K2_LETTERS = "".join(c for c in K2_CT if c != "?")   # the '?' are punctuation, not enciphered
    for j, a, b in d:
        print(f"  K2 LETTER index {j} (1-indexed {j+1}): UNDERGRUUND->'{a}'   UNDERGROUND->'{b}'")
        print(f"    Kryptos K2 carves       : ...{K2_LETTERS[j-6:j]}[{K2_LETTERS[j]}]{K2_LETTERS[j+1:j+7]}...")
        print(f"    predicted UNDERGROUND ct: ...{ct_alt[j-6:j]}[{b}]{ct_alt[j+1:j+7]}...")
        print(f"    carved letter == UNDERGRUUND prediction '{a}' : {K2_LETTERS[j] == a}")
        print(f"    carved letter == UNDERGROUND prediction '{b}' : {K2_LETTERS[j] == b}")
    # what Antipodes actually carries at the corresponding spot
    ant = "".join(ANTIPODES_LATIN_ROWS).replace(" ", "").replace(".", "")
    for tag, s in (("Kryptos  ", K2_CT), ):
        k = s.find("BQC")
        print(f"  {tag} K2 has '{s[k:k+14]}' at K2 offset {k}")
    for mm in re.finditer("BQC[A-Z]TBJDFHRR", ant):
        print(f"  Antipodes has '{mm.group(0)}' at stream index {mm.start()}")


# ----------------------------------------------------------------------------
# PART 3 — the Cyrillic Projector cipher
# ----------------------------------------------------------------------------
CYR_PLAIN = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"        # 32: standard Russian minus Ё
CYR_KEYED = "ТЕНЬАБВГДЖЗИЙКЛМОПРСУФХШЦЧЩЪЫЭЮЯ"        # keyword ТЕНЬ ("shadow")
CYR_KEY2  = "ЙБАСГТ"                                   # published 2nd keyword (from MEDUSA)

def part3():
    print()
    print("=" * 78)
    print("PART 3 — recovering the Cyrillic Projector / Antipodes-Cyrillic cipher")
    print("=" * 78)
    ks = os.path.join(ROOT, "lateral", "keystreams")
    ct = open(os.path.join(ks, "cyrillic_projector_ciphertext_cyrillic.txt"), encoding="utf-8").read().strip()
    pt = open(os.path.join(ks, "cyrillic_projector_plaintext_cyrillic.txt"), encoding="utf-8").read().strip()
    act = open(os.path.join(ks, "antipodes_cyrillic_ciphertext.txt"), encoding="utf-8").read().strip()
    apt = open(os.path.join(ks, "antipodes_cyrillic_plaintext.txt"), encoding="utf-8").read().strip()
    print(f"Cyrillic Projector ct/pt lengths : {len(ct)} / {len(pt)}   equal: {len(ct)==len(pt)}")
    print(f"Antipodes Cyrillic ct/pt lengths : {len(act)} / {len(apt)}  equal: {len(act)==len(apt)}")
    print(f"CP ciphertext is a prefix of the Antipodes ciphertext: {act.startswith(ct)}")
    print(f"alphabets — plain 32: {CYR_PLAIN}")
    print(f"          — keyed 32: {CYR_KEYED}")
    print(f"keyed alphabet is a permutation of the plain one: {sorted(CYR_PLAIN)==sorted(CYR_KEYED)}")
    print(f"Ё present anywhere in ct or pt: {'Ё' in ct or 'Ё' in pt}")

    # Which letters actually occur?
    used = sorted(set(ct) | set(pt))
    print(f"distinct letters used            : {len(used)}")
    missing = [c for c in CYR_PLAIN if c not in used]
    print(f"alphabet letters never used      : {missing}")

    N = 32
    combos = []
    for pa_name, pa in (("plain", CYR_PLAIN), ("keyed", CYR_KEYED)):
        for ca_name, ca in (("plain", CYR_PLAIN), ("keyed", CYR_KEYED)):
            for fam in ("vigenere", "beaufort", "varbeaufort"):
                combos.append((fam, pa_name, pa, ca_name, ca))

    print("\n--- period-6 agreement for every combo, published key ЙБАСГТ, no key restart ---")
    best = None
    for fam, pan, pa, can, ca in combos:
        ip = {c: i for i, c in enumerate(pa)}
        for kan, ka in (("plain", CYR_PLAIN), ("keyed", CYR_KEYED)):
            ikk = {c: i for i, c in enumerate(ka)}
            good = 0
            for i, (p, c) in enumerate(zip(apt, act)):
                kv = ikk[CYR_KEY2[i % 6]]
                if fam == "vigenere":
                    pred = ca[(ip[p] + kv) % N]
                elif fam == "beaufort":
                    pred = ca[(kv - ip[p]) % N]
                else:
                    pred = ca[(ip[p] - kv) % N]
                good += (pred == c)
            pct = 100.0 * good / len(act)
            if best is None or good > best[0]:
                best = (good, fam, pan, can, kan)
            if pct > 10:
                print(f"  {fam:12s} pt={pan:5s} ct={can:5s} key-alpha={kan:5s} : "
                      f"{good:5d}/{len(act)} = {pct:5.1f}%   (chance {100.0/N:.1f}%)")
    print(f"  best combo: {best[1]} pt={best[2]} ct={best[3]} key-alpha={best[4]} at {best[0]}/{len(act)}")

    # ---- the winning combo, block by block, to expose the key restart
    ip = {c: i for i, c in enumerate(CYR_PLAIN)}
    ikk = {c: i for i, c in enumerate(CYR_KEYED)}
    shifts = [ikk[c] for c in CYR_KEY2]
    ok = [CYR_KEYED[(ip[p] + shifts[i % 6]) % N] == c for i, (p, c) in enumerate(zip(apt, act))]
    first_bad = ok.index(False)
    print(f"\nwinning combo matches exactly for the first {first_bad} characters, then breaks.")
    print(f"  plaintext around the break : ...{apt[first_bad-24:first_bad]} | {apt[first_bad:first_bad+24]}...")
    print(f"  -> that is the boundary between message 1 and message 2 (the KGB/Sakharov report).")
    for ph in range(6):
        tail = [CYR_KEYED[(ip[p] + shifts[(i + ph) % 6]) % N] == c
                for i, (p, c) in enumerate(zip(apt[first_bad:], act[first_bad:]))]
        mark = "  <== the key RESTARTS here" if sum(tail) == len(tail) else ""
        print(f"  tail with key phase +{ph}: {sum(tail)}/{len(tail)}{mark}")

    # ---- full decrypt / encrypt round trip with the key restart
    def keystream(n, boundaries):
        out, bi = [], 0
        for i in range(n):
            while bi + 1 < len(boundaries) and i >= boundaries[bi + 1]:
                bi += 1
            out.append(shifts[(i - boundaries[bi]) % 6])
        return out

    BOUND = [0, first_bad]
    kstr = keystream(len(act), BOUND)
    dec = "".join(CYR_PLAIN[(ikk[c] - k) % N] for c, k in zip(act, kstr))
    enc = "".join(CYR_KEYED[(ip[p] + k) % N] for p, k in zip(apt, kstr))
    print(f"\nANTIPODES Cyrillic side, key restart at {first_bad}:")
    print(f"  decrypt(ciphertext) == stored plaintext : {dec == apt}   ({len(act)}/{len(act)} characters)")
    print(f"  encrypt(plaintext)  == carved ciphertext: {enc == act}")

    kstr_cp = keystream(len(ct), BOUND)
    dec_cp = "".join(CYR_PLAIN[(ikk[c] - k) % N] for c, k in zip(ct, kstr_cp))
    bad = [(i, pt[i], dec_cp[i]) for i in range(len(ct)) if pt[i] != dec_cp[i]]
    print(f"\nCYRILLIC PROJECTOR alone, same key and restart point:")
    print(f"  decrypt(ciphertext) vs the stored CP plaintext file: {len(ct)-len(bad)}/{len(ct)} agree")
    for i, stored, got in bad:
        print(f"    index {i}: file has '{stored}', decryption gives '{got}'  <-- defect in "
              f"lateral/keystreams/cyrillic_projector_plaintext_cyrillic.txt")

    # ---- where does the key come from?
    print("\n--- the key ЙБАСГТ is МЕДУЗА (MEDUSA) written in the cipher's own alphabet ---")
    med = "МЕДУЗА"
    via = "".join(CYR_KEYED[ip[c]] for c in med)
    print(f"  МЕДУЗА indices in the STRAIGHT alphabet : {[ip[c] for c in med]}")
    print(f"  letters at those indices in the KEYED alphabet : {via}   == ЙБАСГТ : {via == CYR_KEY2}")
    print(f"  shift sequence from ЙБАСГТ read in the KEYED alphabet   : {[ikk[c] for c in CYR_KEY2]}")
    print(f"  shift sequence from МЕДУЗА read in the STRAIGHT alphabet: {[ip[c] for c in med]}")
    print(f"  identical: {[ikk[c] for c in CYR_KEY2] == [ip[c] for c in med]}")
    print("  => the operative key is MEDUSA, the clue word carved in Latin letters on the sculpture.")

    # ---- the keyed alphabet is not a plain keyword mixing
    print("\n--- the keyed alphabet is NOT a plain keyword-mixed alphabet ---")
    naive = "".join(c for c in CYR_PLAIN if c not in "ТЕНЬ")
    print(f"  straight alphabet minus ТЕНЬ : {naive}")
    print(f"  carved keyed alphabet tail   : {CYR_KEYED[4:]}")
    print(f"  identical: {naive == CYR_KEYED[4:]}")
    print("  Ш has been lifted out of its normal slot (between Ч and Щ) and parked next to Х.")

    # ---- the ACA name
    print("\n--- classification ---")
    print("  plaintext alphabet = straight; ciphertext alphabet = keyed; key letter = the ciphertext")
    print("  of plaintext А  ->  ACA Quagmire II (Kryptos K1/K2 are Quagmire III).")
    return


if __name__ == "__main__":
    part1()
    part2()
    part3()
