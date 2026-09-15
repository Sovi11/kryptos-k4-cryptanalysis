"""Shared machinery for the "K4 = two ciphers" round-2 searches (two2_*.py).

Requires numpy (the big scans are vectorised).  On this machine numpy lives in a
scratch venv; see findings/twocipher.md for the exact interpreter used.

Central modelling point
-----------------------
Write S for a letter-wise substitution whose key stream may vary with position
(periodic or not) and T for a transposition (a permutation of the 97 positions,
T[j] = ciphertext position receiving intermediate position j).

Sanborn's cribs ("letters 64-69 of K4 decode to BERLIN") admit two readings:

  (CT-reading)  the *ciphertext* letters at 64-69 are NYPVTT and they decrypt to
                BERLIN.  This is what data/cribs.json encodes and what every
                earlier K4 test in this repo used.
  (PT-reading)  the *plaintext* letters at 64-69 are BERLIN; which ciphertext
                letters carry them depends on the transposition.

Which reading is informative depends on the order of the two stages:

  T then S  (P -> T -> S -> C):  the substitution is indexed by ciphertext
       position, and under the CT-reading the 24 (ct,pt) pairs are exactly the
       ones a one-stage cipher would give.  So *any* transposition placed before
       the substitution is invisible to the crib test: the earlier periodic and
       running-key negatives already cover this whole class.  (Under the
       PT-reading the key positions become T[j], which this module also supports.)

  S then T  (P -> S -> T -> C):  the substitution is indexed by *plaintext*
       position.  Under the PT-reading the plaintext at 0-indexed 21..33 and
       63..73 is known, the intermediate text is I = T^-1(C), i.e. I[j] = C[T[j]],
       and the key stream is therefore *completely determined at 24 known,
       contiguous positions* for every candidate T:

            k_j = derive_key(combo, P[j], C[T[j]])

       No periodicity is assumed.  The decisive questions are then: is that
       24-letter key stream English, does it occur in a sculpture text, is it
       periodic, is it constant?  That is what two2_a_transpose_keystream.py asks
       over every transposition in the catalogue.
"""
import os, re, sys, math, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import runningkey_lib as RK          # corpus, combos, cipher algebra
import twocipher_common as TC        # ciphertext, cribs, English judgement

CT = TC.CT
N = 97
PLAIN = RK.PLAIN
KEYED = RK.KEYED
ALPHAS = RK.ALPHAS

# 0-indexed plaintext/ciphertext positions of the cribs and their plaintext letters
BLOCK1 = list(range(21, 34))          # EASTNORTHEAST
BLOCK2 = list(range(63, 74))          # BERLINCLOCK
CRIB_POS = BLOCK1 + BLOCK2            # 24 positions
CRIB_PT = "EASTNORTHEAST" + "BERLINCLOCK"
CRIB_CT = "".join(CT[p] for p in CRIB_POS)
assert CRIB_CT == "FLRVQQPRNGKSS" + "NYPVTTMZFPK"
GAP = BLOCK2[0] - BLOCK1[0]           # 42

COMBOS = list(RK.combos())            # 24 = 3 families x 2 x 2 x 2 alphabets
COMBO_NAMES = [RK.combo_name(c) for c in COMBOS]

# ---------------------------------------------------------------- alphabets
def idx_table(alpha):
    """t[letter_code 0..25] = index of that letter inside `alpha`."""
    t = np.zeros(26, dtype=np.int64)
    for i, ch in enumerate(alpha):
        t[ord(ch) - 65] = i
    return t

def letter_table(alpha):
    """t[index inside alpha] = letter code 0..25."""
    return np.array([ord(ch) - 65 for ch in alpha], dtype=np.int64)

IDX = {k: idx_table(v) for k, v in ALPHAS.items()}
LET = {k: letter_table(v) for k, v in ALPHAS.items()}

CT_CODES = np.array([ord(c) - 65 for c in CT], dtype=np.int64)
CRIB_PT_CODES = np.array([ord(c) - 65 for c in CRIB_PT], dtype=np.int64)

def key_codes(combo, inter_codes):
    """Vectorised key-letter derivation.

    inter_codes : (..., 24) int array of intermediate/ciphertext letter codes at
                  the 24 crib positions.
    returns     : same shape, key letter codes (0..25, as A-Z codes).
    """
    fam, ap, ac, ak = combo
    p = IDX[ap][CRIB_PT_CODES]                 # (24,)
    c = IDX[ac][inter_codes]                   # (...,24)
    if fam == "vigenere":
        k = (c - p) % 26
    elif fam == "beaufort":
        k = (c + p) % 26
    else:                                       # varbeaufort
        k = (p - c) % 26
    return LET[ak][k]

def inter_codes_required(combo, key_code_block):
    """Inverse of key_codes: given key letter codes at the 24 crib positions,
    the intermediate letters they force."""
    fam, ap, ac, ak = combo
    p = IDX[ap][CRIB_PT_CODES]
    k = IDX[ak][key_code_block]
    if fam == "vigenere":
        c = (p + k) % 26
    elif fam == "beaufort":
        c = (k - p) % 26
    else:
        c = (p - k) % 26
    return LET[ac][c]

def codes_to_str(a):
    return "".join(chr(65 + int(x)) for x in np.asarray(a).ravel())

# ---------------------------------------------------------------- quadgrams
_QUADARR = None
def quad_array():
    """456976-entry float32 array of log10 quadgram probabilities, built from the
    same cached model twocipher_common uses (English prose ~ -4.7/quadgram,
    uniform random ~ -8.2)."""
    global _QUADARR
    if _QUADARR is not None:
        return _QUADARR
    TC._build_quadgram_model()
    arr = np.full(26 ** 4, TC._QUAD_FLOOR, dtype=np.float32)
    for g, v in TC._QUAD.items():
        c = 0
        for ch in g:
            c = c * 26 + (ord(ch) - 65)
        arr[c] = v
    _QUADARR = arr
    return arr

def quad_score_blocks(keys):
    """keys : (n, 24) key letter codes -> (n,) mean log10 quadgram probability
    over the 10 quadgrams of block 1 and the 8 of block 2 (18 total)."""
    Q = quad_array()
    n = keys.shape[0]
    tot = np.zeros(n, dtype=np.float64)
    cnt = 0
    for lo, L in ((0, 13), (13, 11)):
        blk = keys[:, lo:lo + L]
        code = (blk[:, 0:L - 3] * 26 ** 3 + blk[:, 1:L - 2] * 26 ** 2
                + blk[:, 2:L - 1] * 26 + blk[:, 3:L])
        tot += Q[code].sum(axis=1)
        cnt += L - 3
    return tot / cnt

# ---------------------------------------------------------------- corpus
def corpus_texts():
    return RK.corpus()

def corpus_ngram_codes(L):
    """dict name -> (int64 array of L-gram codes, text length).  L <= 13."""
    out = {}
    for name, txt in corpus_texts().items():
        a = np.array([ord(c) - 65 for c in txt], dtype=np.int64)
        if len(a) < L:
            out[name] = (np.zeros(0, dtype=np.int64), len(a)); continue
        code = np.zeros(len(a) - L + 1, dtype=np.int64)
        for i in range(L):
            code = code * 26 + a[i:len(a) - L + 1 + i]
        out[name] = (code, len(a))
    return out

def encode_block(arr, L):
    """(n, L) letter codes -> (n,) int64 code."""
    code = np.zeros(arr.shape[0], dtype=np.int64)
    for i in range(L):
        code = code * 26 + arr[:, i]
    return code

# ------------------------------------------------------- periodic testing
def period_pairs(positions, p):
    """List of (i, j) index pairs into `positions` that must carry the same key
    value if the key has period p (each new residue anchors, later ones check)."""
    seen = {}
    pairs = []
    for i, pos in enumerate(positions):
        r = pos % p
        if r in seen:
            pairs.append((seen[r], i))
        else:
            seen[r] = i
    return pairs

def period_checks(positions, p):
    return len(period_pairs(positions, p))

# ------------------------------------------------------------ transpositions
def load_transposition_catalogue(verbose=True):
    """Stream twocipher_B_transpositions.enumerate_family() (plus inverses) and
    return

        Tj   : (m, 24) uint8   T[j] for the 24 crib *plaintext* positions
        Tic  : (m, 24) uint8   T^-1[c] for the 24 crib *ciphertext* positions
        desc : list of m description strings (first one seen for each row)

    de-duplicated on (Tj, Tic) jointly -- that pair is all any test here needs.
    """
    import twocipher_B_transpositions as B
    seen = {}
    order = []
    cnt = 0
    for fam, d, T in B.enumerate_family():
        for tag, TT in (("", T), (" [inv]", B.inverse(T))):
            cnt += 1
            Ti = B.inverse(TT)
            kj = bytes(TT[j] for j in CRIB_POS) + bytes(Ti[c] for c in CRIB_POS)
            if kj in seen:
                continue
            seen[kj] = len(order)
            order.append((kj, f"{fam}: {d}{tag}"))
    m = len(order)
    Tj = np.zeros((m, 24), dtype=np.uint8)
    Tic = np.zeros((m, 24), dtype=np.uint8)
    desc = []
    for i, (kj, d) in enumerate(order):
        Tj[i] = np.frombuffer(kj[:24], dtype=np.uint8)
        Tic[i] = np.frombuffer(kj[24:], dtype=np.uint8)
        desc.append(d)
    if verbose:
        print(f"catalogue: {cnt} (family,variant) transpositions -> {m} distinct "
              f"crib-signature rows", flush=True)
    return Tj, Tic, desc
