"""Shared helpers for the 'K4 is several ciphers / key changes at boundaries' investigation.

Conventions (identical to analysis/runningkey_lib.py so results are comparable):
  p = index of plaintext letter in the PT alphabet
  c = index of ciphertext letter in the CT alphabet
  k = key value (an integer 0..25; the key ALPHABET only relabels it, so every
      *consistency* test below is invariant to the key alphabet and we never need it)

    vigenere     : c = p + k   ->  k = c - p ,  p = c - k
    beaufort     : c = k - p   ->  k = c + p ,  p = k - c
    varbeaufort  : c = p - k   ->  k = p - c ,  p = c + k

All positions are 0-indexed internally.
"""
import json, math, os, re
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
FINDINGS = os.path.join(ROOT, "findings")

PLAIN = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KEYED = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

def letters(s):
    return re.sub(r"[^A-Z]", "", s.upper())

with open(os.path.join(DATA, "k4_ciphertext.txt")) as f:
    CT = letters(f.read())
assert len(CT) == 97, len(CT)

with open(os.path.join(DATA, "cribs.json")) as f:
    _cribs = json.load(f)["cribs"]

CRIB = {}
for _c in _cribs:
    _s = _c["pos"] - 1
    assert CT[_s:_s + len(_c["ct"])] == _c["ct"], _c
    for _k, _p in enumerate(_c["pt"]):
        CRIB[_s + _k] = _p
CRIB_POS = sorted(CRIB)                      # 24 positions, 0-indexed
CRIB_PT = "".join(CRIB[i] for i in CRIB_POS)
CRIB_CT = "".join(CT[i] for i in CRIB_POS)
# the two contiguous runs
CRIB_RUNS = [(21, 34), (63, 74)]             # [start, end) half-open, 0-indexed
assert all(all(i in CRIB for i in range(a, b)) for a, b in CRIB_RUNS)
assert len(CRIB_POS) == 24

SHORT_KEYWORDS = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "SANBORN", "SCHEIDT", "LANGLEY",
                  "BERLIN", "CLOCK", "COMPASS", "LODESTONE", "SHADOW", "IQLUSION",
                  "UNDERGRUUND", "DESPARATLY", "LAYERTWO", "MASKING"]

def keyed_alphabet(keyword, base=PLAIN):
    seen = []
    for ch in keyword.upper():
        if ch in base and ch not in seen:
            seen.append(ch)
    return "".join(seen) + "".join(ch for ch in base if ch not in seen)

# 17 alphabets: straight + the 16 Kryptos-world keywords
ALPHABETS = {"STRAIGHT": PLAIN}
for _w in SHORT_KEYWORDS:
    ALPHABETS[_w] = keyed_alphabet(_w)
ALPHABET_NAMES = list(ALPHABETS)

FAMILIES = ["vigenere", "beaufort", "varbeaufort"]

def idx_map(alpha):
    m = np.zeros(26, dtype=np.int64)
    for i, ch in enumerate(alpha):
        m[ord(ch) - 65] = i
    return m

CT_CODE = np.frombuffer(CT.encode(), dtype=np.uint8).astype(np.int64) - 65
CRIB_POS_ARR = np.array(CRIB_POS)
CRIB_PT_CODE = np.frombuffer(CRIB_PT.encode(), dtype=np.uint8).astype(np.int64) - 65
CRIB_CT_CODE = np.frombuffer(CRIB_CT.encode(), dtype=np.uint8).astype(np.int64) - 65


def required_shifts(family, pt_alpha, ct_alpha):
    """The 24 key values forced by the cribs, as ints 0..25, in CRIB_POS order."""
    pi = idx_map(pt_alpha)[CRIB_PT_CODE]
    ci = idx_map(ct_alpha)[CRIB_CT_CODE]
    if family == "vigenere":
        k = ci - pi
    elif family == "beaufort":
        k = ci + pi
    elif family == "varbeaufort":
        k = pi - ci
    else:
        raise ValueError(family)
    return k % 26


def all_shift_configs(alpha_names=None):
    """Yield (label, shifts24) over families x pt-alphabet x ct-alphabet."""
    names = alpha_names or ALPHABET_NAMES
    for fam in FAMILIES:
        for pn in names:
            for cn in names:
                yield (f"{fam}/pt={pn}/ct={cn}", required_shifts(fam, ALPHABETS[pn], ALPHABETS[cn]))


def decrypt(ct_codes, key_vals, family, pt_alpha, ct_alpha):
    """ct_codes: int array of A=0..Z=25.  key_vals: int array, same length, 0..25.
    Returns the plaintext string."""
    ci = idx_map(ct_alpha)[ct_codes]
    if family == "vigenere":
        pi = ci - key_vals
    elif family == "beaufort":
        pi = key_vals - ci
    elif family == "varbeaufort":
        pi = ci + key_vals
    else:
        raise ValueError(family)
    pi %= 26
    arr = np.frombuffer(pt_alpha.encode(), dtype=np.uint8)[pi]
    return arr.tobytes().decode()


def encrypt(pt_codes, key_vals, family, pt_alpha, ct_alpha):
    pi = idx_map(pt_alpha)[pt_codes]
    if family == "vigenere":
        ci = pi + key_vals
    elif family == "beaufort":
        ci = key_vals - pi
    elif family == "varbeaufort":
        ci = pi - key_vals
    else:
        raise ValueError(family)
    ci %= 26
    arr = np.frombuffer(ct_alpha.encode(), dtype=np.uint8)[ci]
    return arr.tobytes().decode()


def codes(s):
    return np.frombuffer(s.encode(), dtype=np.uint8).astype(np.int64) - 65


# ------------------------------------------------------------------ English scoring
_QUAD = None
_FLOOR = None

def _load_quad():
    global _QUAD, _FLOOR
    if _QUAD is not None:
        return
    cache = os.path.join(HERE, ".quadgrams_cache.json")
    with open(cache) as f:
        d = json.load(f)
    q = d["q"]; floor = d["floor"]
    arr = np.full(26 ** 4, floor, dtype=np.float32)
    for kk, v in q.items():
        a, b, c, dd = (ord(x) - 65 for x in kk)
        arr[((a * 26 + b) * 26 + c) * 26 + dd] = v
    _QUAD = arr; _FLOOR = floor

def quad_score(text):
    """Mean log10 quadgram probability.  English ~ -4.7, uniform random ~ -8.2."""
    _load_quad()
    tot = 0.0; n = 0
    for run in re.findall(r"[A-Z]+", text):
        if len(run) < 4:
            continue
        c = codes(run)
        idx = ((c[:-3] * 26 + c[1:-2]) * 26 + c[2:-1]) * 26 + c[3:]
        tot += float(_QUAD[idx].sum()); n += len(idx)
    return tot / n if n else float("nan")

def quad_scores_batch(mat):
    """mat: (n, L) int array of letter codes -> (n,) mean log10 quadgram prob."""
    _load_quad()
    n, L = mat.shape
    idx = ((mat[:, :-3] * 26 + mat[:, 1:-2]) * 26 + mat[:, 2:-1]) * 26 + mat[:, 3:]
    return _QUAD[idx].mean(axis=1)

_WORDS = None
def _load_words(minlen=3):
    global _WORDS
    if _WORDS is None:
        _WORDS = set()
        for path in ("/usr/share/dict/words", "/usr/dict/words"):
            if os.path.exists(path):
                with open(path) as f:
                    for w in f:
                        w = w.strip().upper()
                        if minlen <= len(w) <= 24 and w.isalpha() and w.isascii():
                            _WORDS.add(w)
                break
    return _WORDS

def word_coverage(text, minlen=3):
    W = _load_words(minlen)
    n = len(text)
    best = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        best[i] = best[i + 1]
        for L in range(minlen, min(24, n - i) + 1):
            if text[i:i + L] in W:
                best[i] = max(best[i], L + best[i + L])
    return best[0] / n if n else 0.0

def ioc(text):
    n = len(text)
    if n < 2:
        return float("nan")
    cnt = Counter(text)
    return sum(v * (v - 1) for v in cnt.values()) / (n * (n - 1))

ENG_FREQ = dict(zip(PLAIN, [8.17, 1.49, 2.78, 4.25, 12.70, 2.23, 2.02, 6.09, 6.97, 0.15, 0.77, 4.03,
                            2.41, 6.75, 7.51, 1.93, 0.10, 5.99, 6.33, 9.06, 2.76, 0.98, 2.36, 0.15,
                            1.97, 0.07]))
ENG_P = np.array([ENG_FREQ[a] / 100 for a in PLAIN])

def chi2_vs(text, probs):
    n = len(text)
    cnt = np.zeros(26)
    for ch in text:
        cnt[ord(ch) - 65] += 1
    exp = n * probs
    return float(((cnt - exp) ** 2 / exp).sum())

def chi2_english(text):
    return chi2_vs(text, ENG_P)

def chi2_uniform(text):
    return chi2_vs(text, np.full(26, 1 / 26))


# ------------------------------------------------------------------ self-test
def _selftest():
    # round-trip every family / alphabet combination
    rng = np.random.default_rng(0)
    pt = "".join(PLAIN[i] for i in rng.integers(0, 26, 97))
    key = rng.integers(0, 26, 97)
    for fam in FAMILIES:
        for pa in (PLAIN, KEYED, ALPHABETS["ABSCISSA"]):
            for ca in (PLAIN, KEYED, ALPHABETS["LODESTONE"]):
                ct = encrypt(codes(pt), key, fam, pa, ca)
                back = decrypt(codes(ct), key, fam, pa, ca)
                assert back == pt, (fam, pa, ca)
    # required_shifts must reproduce the cribs
    for fam in FAMILIES:
        for pn in ("STRAIGHT", "KRYPTOS"):
            for cn in ("STRAIGHT", "KRYPTOS"):
                k = required_shifts(fam, ALPHABETS[pn], ALPHABETS[cn])
                got = decrypt(CRIB_CT_CODE, k, fam, ALPHABETS[pn], ALPHABETS[cn])
                assert got == CRIB_PT, (fam, pn, cn, got)
    # known published values: straight/vigenere shifts for block1 = BLZCDCYYGCKAZ
    k = required_shifts("vigenere", PLAIN, PLAIN)
    s = "".join(PLAIN[x] for x in k)
    assert s == "BLZCDCYYGCKAZ" + "MUYKLGKORNA", s
    k = required_shifts("beaufort", PLAIN, PLAIN)
    s = "".join(PLAIN[x] for x in k)
    assert s == "JLJODEGKUKKKL" + "OCGGBGOKTRU", s
    # NB: the runningkey.md table prints the key letter in the KEY alphabet; these
    # integers are the key alphabet's *index*, so they match the key=plain rows.
    k = required_shifts("vigenere", KEYED, KEYED)
    s = "".join(PLAIN[x] for x in k)
    assert s == "BKVSBPCXFCTAC" + "LRCFPLJIHUA", s
    k = required_shifts("varbeaufort", PLAIN, PLAIN)
    s = "".join(PLAIN[x] for x in k)
    assert s == "ZPBYXYCCUYQAB" + "OGCQPUQMJNA", s
    k = required_shifts("beaufort", KEYED, PLAIN)
    s = "".join(PLAIN[x] for x in k)
    assert s == "QSXZJVQVBRRYW" + "VJQMIMVQKYK", s
    # quadgram sanity
    q_eng = quad_score("THEQUICKBROWNFOXJUMPSOVERTHELAZYDOGANDTHENWALKEDAWAYINTOTHEFOREST")
    q_rnd = quad_score("XQZJVBKWPQMZXJVBQKWZPXQJVBMKZWPQXJVBKZWMPQXJVBZKWMPQXJVBKZWPMQXJV")
    assert q_eng > -5.5 > -7.0 > q_rnd, (q_eng, q_rnd)
    return True

if __name__ == "__main__":
    assert _selftest()
    print("seg_common self-test OK")
    print("CT      :", CT)
    print("cribs   :", CRIB_PT, "at", CRIB_POS)
    print("IoC     : %.5f" % ioc(CT))
    print("quad eng-check on K1 pt: %.3f" % quad_score("BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHT"))
