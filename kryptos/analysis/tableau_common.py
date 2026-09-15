"""Shared code for the "tableau as a physical key TABLE" hypothesis (K4).

Distinct from analysis/runningkey_lib.py, which treats the right panel as a linear
string of letters.  Here the right panel is a two-dimensional carved grid and the key
letter at K4 position i is looked up at some coordinate (row, col) derived from i.

Conventions
-----------
* K4 positions are 0-indexed internally (0..96); cribs.json is 1-indexed.
* A cipher "combo" is (family, pt_alphabet, ct_alphabet, key_alphabet), exactly as in
  runningkey_lib.py, so results are directly comparable:
      p = A_p.index(P), c = A_c.index(C), k = A_k.index(K)
      vigenere      : c = p + k   -> k = c - p
      beaufort      : c = k - p   -> k = c + p
      varbeaufort   : c = p - k   -> k = p - c
  Each alphabet is plain A-Z or the KRYPTOS keyed alphabet.  24 combos.
* "rotation r" means the key letter actually carved is the required key letter rotated
  by r in the key alphabet (an unknown index convention).  Searching for a constant
  difference between the carved and required key letters covers all 26 rotations at once.
"""
import os
import re
import itertools

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
FINDINGS = os.path.join(ROOT, "findings")

PLAIN = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KEYED = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
ALPHAS = {"plain": PLAIN, "keyed": KEYED}
FAMILIES = ["vigenere", "beaufort", "varbeaufort"]


def letters(s):
    return re.sub(r"[^A-Z]", "", s.upper())


def _read(name):
    with open(os.path.join(DATA, name)) as f:
        return f.read()


# ------------------------------------------------------------------ K4 + cribs ----
K4_CT = letters(_read("k4_ciphertext.txt"))
assert len(K4_CT) == 97

import json
_cribs = json.loads(_read("cribs.json"))["cribs"]
CRIB = {}
for _c in _cribs:
    _s = _c["pos"] - 1
    assert K4_CT[_s:_s + len(_c["ct"])] == _c["ct"], _c
    for _k, _p in enumerate(_c["pt"]):
        CRIB[_s + _k] = _p
CRIB_POS = sorted(CRIB)                     # 24 positions, 0-indexed
CRIB_PT = [CRIB[i] for i in CRIB_POS]
CRIB_CT = [K4_CT[i] for i in CRIB_POS]
assert len(CRIB_POS) == 24


# ------------------------------------------------------------- panel geometry ----
def panels():
    """(left_rows, right_rows) as carved, from data/sculpture_panels.txt."""
    left, right, cur = [], [], None
    for ln in _read("sculpture_panels.txt").splitlines():
        if ln.startswith("#"):
            continue
        s = ln.strip()
        if s == "[LEFT]":
            cur = left
            continue
        if s == "[RIGHT]":
            cur = right
            continue
        if cur is not None and s:
            cur.append(ln.rstrip("\n"))
    return left, right


LEFT_ROWS_RAW, RIGHT_ROWS_RAW = panels()
# Right panel rows, letters only.  28 rows:
#   row 0  : header  "ABCDEFGHIJKLMNOPQRSTUVWXYZABCD"          (30 letters, no label)
#   rows1-26: label + 30-letter rotation of KEYED               (31, row N has 32)
#   row 27 : footer  "ABCDEFGHIJKLMNOPQRSTUVWXYZABCD"          (30 letters, no label)
RIGHT_ROWS = [letters(r) for r in RIGHT_ROWS_RAW]
LEFT_ROWS = [r.strip() for r in LEFT_ROWS_RAW]       # keep '?' so column indices are right
assert len(RIGHT_ROWS) == 28 and len(LEFT_ROWS) == 28

TABLEAU_PHYS_STR = "".join(RIGHT_ROWS)


def ideal_right_rows():
    """The tableau the carver *should* have produced: header, 26 labelled rotations, footer."""
    rows = [PLAIN + "ABCD"]
    for i in range(26):
        rot = KEYED[i:] + KEYED[:i]
        rows.append(PLAIN[i] + rot + rot[:4])
    rows.append(PLAIN + "ABCD")
    return rows


RIGHT_ROWS_IDEAL = ideal_right_rows()
TABLEAU_IDEAL_STR = "".join(RIGHT_ROWS_IDEAL)


# --------------------------------------------------------------- cipher engine ----
def combos():
    out = []
    for fam in FAMILIES:
        for ap in ("plain", "keyed"):
            for ac in ("plain", "keyed"):
                for ak in ("plain", "keyed"):
                    out.append((fam, ap, ac, ak))
    return out


COMBOS = combos()
assert len(COMBOS) == 24


def combo_name(cb):
    return "%s/pt=%s/ct=%s/key=%s" % cb


def required_key_indices(cb):
    """Key-letter INDEX (in the combo's key alphabet) required at each crib position."""
    fam, ap, ac, ak = cb
    Ap, Ac = ALPHAS[ap], ALPHAS[ac]
    out = []
    for P, C in zip(CRIB_PT, CRIB_CT):
        p, c = Ap.index(P), Ac.index(C)
        if fam == "vigenere":
            k = (c - p) % 26
        elif fam == "beaufort":
            k = (c + p) % 26
        else:
            k = (p - c) % 26
        out.append(k)
    return out


def required_key_letters(cb):
    A = ALPHAS[cb[3]]
    return "".join(A[k] for k in required_key_indices(cb))


def decrypt(cb, key_letters):
    """Decrypt the whole 97-letter K4 with a 97-letter key stream under combo cb."""
    fam, ap, ac, ak = cb
    Ap, Ac, Ak = ALPHAS[ap], ALPHAS[ac], ALPHAS[ak]
    out = []
    for C, K in zip(K4_CT, key_letters):
        c, k = Ac.index(C), Ak.index(K)
        if fam == "vigenere":
            p = (c - k) % 26
        elif fam == "beaufort":
            p = (k - c) % 26
        else:
            p = (c + k) % 26
        out.append(Ap[p])
    return "".join(out)


def encrypt(cb, plain, key_letters):
    fam, ap, ac, ak = cb
    Ap, Ac, Ak = ALPHAS[ap], ALPHAS[ac], ALPHAS[ak]
    out = []
    for P, K in zip(plain, key_letters):
        p, k = Ap.index(P), Ak.index(K)
        if fam == "vigenere":
            c = (p + k) % 26
        elif fam == "beaufort":
            c = (k - p) % 26
        else:
            c = (p - k) % 26
        out.append(Ac[c])
    return "".join(out)


def crib_matches(cb, key_letters):
    """How many of the 24 crib letters this key stream reproduces (24 = solution)."""
    pt = decrypt(cb, key_letters)
    return sum(1 for i, L in zip(CRIB_POS, CRIB_PT) if pt[i] == L)


# ----------------------------------------------------------- English scoring ----
_PROSE = ("THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG")  # replaced below by k4_common's corpus


def english_score(text):
    """Quadgram-ish score via k4_common's bigram model (kept identical for comparability)."""
    import k4_common
    return k4_common.bigram_score(text)


def ioc(text):
    n = len(text)
    if n < 2:
        return 0.0
    from collections import Counter
    cnt = Counter(text)
    return sum(v * (v - 1) for v in cnt.values()) / (n * (n - 1))


def selftest():
    """Round-trip and known-answer checks.  Raises on failure."""
    # 1. encrypt/decrypt round trip for every combo
    import random
    rnd = random.Random(7)
    key = "".join(rnd.choice(PLAIN) for _ in range(97))
    pt = "".join(rnd.choice(PLAIN) for _ in range(97))
    for cb in COMBOS:
        ct = encrypt(cb, pt, key)
        # decrypt() works on the module-level K4_CT, so do it inline here
        fam, ap, ac, ak = cb
        Ap, Ac, Ak = ALPHAS[ap], ALPHAS[ac], ALPHAS[ak]
        back = []
        for C, K in zip(ct, key):
            c, k = Ac.index(C), Ak.index(K)
            if fam == "vigenere":
                p = (c - k) % 26
            elif fam == "beaufort":
                p = (k - c) % 26
            else:
                p = (c + k) % 26
            back.append(Ap[p])
        assert "".join(back) == pt, cb

    # 2. required_key_* really is the key that reproduces the cribs
    for cb in COMBOS:
        req = required_key_letters(cb)
        fake = list("A" * 97)
        for pos, K in zip(CRIB_POS, req):
            fake[pos] = K
        assert crib_matches(cb, "".join(fake)) == 24, cb

    # 3. K1 regression: Vigenere with keyed pt/ct/key alphabets and key PALIMPSEST
    k1_pt = ("BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION")
    k1_ct = letters("".join(LEFT_ROWS[0:2]))
    key = "".join((("PALIMPSEST" * 20)[i]) for i in range(len(k1_pt)))
    cb = ("vigenere", "keyed", "keyed", "keyed")
    assert encrypt(cb, k1_pt, key) == k1_ct, (encrypt(cb, k1_pt, key), k1_ct)

    # 4. tableau shape
    assert len(TABLEAU_PHYS_STR) == 867, len(TABLEAU_PHYS_STR)
    assert len(TABLEAU_IDEAL_STR) == 866, len(TABLEAU_IDEAL_STR)
    return True


if __name__ == "__main__":
    selftest()
    print("tableau_common selftest OK")
    print("physical tableau letters:", len(TABLEAU_PHYS_STR))
    print("ideal tableau letters   :", len(TABLEAU_IDEAL_STR))
