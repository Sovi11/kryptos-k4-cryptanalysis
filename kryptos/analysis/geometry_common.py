"""Shared helpers for the K4 geometry investigation (pure Python, no numpy)."""
import json, os, math
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')

CT = open(os.path.join(DATA, 'k4_ciphertext.txt')).read().strip()
assert len(CT) == 97, len(CT)

PLAIN = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
KRYPTOS = 'KRYPTOSABCDEFGHIJLMNQUVWXZ'
ALPHABETS = {'plain': PLAIN, 'kryptos': KRYPTOS}
IDX = {name: {c: i for i, c in enumerate(a)} for name, a in ALPHABETS.items()}

_cribs = json.load(open(os.path.join(DATA, 'cribs.json')))['cribs']
# CRIB[i] = plaintext letter at 1-indexed position i
CRIB = {}
for c in _cribs:
    for k, (a, b) in enumerate(zip(c['ct'], c['pt'])):
        pos = c['pos'] + k
        assert CT[pos - 1] == a, (pos, CT[pos - 1], a)
        CRIB[pos] = b
CRIB_POS = sorted(CRIB)
assert len(CRIB_POS) == 24

CIPHERS = ('vig', 'beau', 'varbeau')

def shift_for(ct, pt, cipher, pa, ca):
    """Key value k (0..25) required to map pt->ct.
    pa = alphabet used to index plaintext, ca = alphabet used to index ciphertext.
    vig     : ct = ca[(pa.idx(pt) + k) % 26]
    beau    : ct = ca[(k - pa.idx(pt)) % 26]
    varbeau : ct = ca[(pa.idx(pt) - k) % 26]
    """
    p, c = IDX[pa][pt], IDX[ca][ct]
    if cipher == 'vig':
        return (c - p) % 26
    if cipher == 'beau':
        return (c + p) % 26
    if cipher == 'varbeau':
        return (p - c) % 26
    raise ValueError(cipher)

def decrypt_letter(ct, k, cipher, pa, ca):
    c = IDX[ca][ct]
    if cipher == 'vig':
        return ALPHABETS[pa][(c - k) % 26]
    if cipher == 'beau':
        return ALPHABETS[pa][(k - c) % 26]
    if cipher == 'varbeau':
        return ALPHABETS[pa][(c + k) % 26]
    raise ValueError(cipher)

ALPHA_PAIRS = [(pa, ca) for pa in ALPHABETS for ca in ALPHABETS]

def crib_shifts(cipher, pa, ca):
    """{pos: required key value} for the 24 crib positions."""
    return {pos: shift_for(CT[pos - 1], CRIB[pos], cipher, pa, ca) for pos in CRIB_POS}

def ioc(text):
    n = len(text)
    if n < 2:
        return 0.0
    cnt = Counter(text)
    return sum(v * (v - 1) for v in cnt.values()) / (n * (n - 1))

def periodic_ioc(text, p):
    """Mean IoC of the p columns."""
    cols = [text[i::p] for i in range(p)]
    return sum(ioc(c) for c in cols) / p

# English letter frequencies for scoring decryptions
ENG = {'A':8.167,'B':1.492,'C':2.782,'D':4.253,'E':12.702,'F':2.228,'G':2.015,'H':6.094,'I':6.966,
       'J':0.153,'K':0.772,'L':4.025,'M':2.406,'N':6.749,'O':7.507,'P':1.929,'Q':0.095,'R':5.987,
       'S':6.327,'T':9.056,'U':2.758,'V':0.978,'W':2.360,'X':0.150,'Y':1.974,'Z':0.074}
_ENG_LOG = {k: math.log(v / 100) for k, v in ENG.items()}

def unigram_logp(text):
    return sum(_ENG_LOG[c] for c in text) / max(1, len(text))

def chi2_english(text):
    n = len(text)
    cnt = Counter(text)
    return sum((cnt.get(c, 0) - n * ENG[c] / 100) ** 2 / (n * ENG[c] / 100) for c in PLAIN)

# A small list of common English words for a crude word-hit score
COMMON = ['THE','AND','THAT','WITH','HAVE','THIS','FROM','THEY','WERE','THERE','THEIR','WHICH','WOULD',
          'ABOUT','COULD','OTHER','THESE','BEEN','WHEN','WHAT','WHERE','INTO','TIME','THEN','THAN',
          'ONLY','OVER','SUCH','MORE','SOME','YOUR','THEM','VERY','ALSO','BACK','AFTER','LIKE','BEFORE',
          'BETWEEN','UNDER','LIGHT','SHADOW','EAST','NORTH','WEST','SOUTH','BERLIN','CLOCK','SEE',
          'ING','TION','ERE','ENT','HER','FOR','NOT','YOU','ARE','ALL','ONE','OUT','ITS','HIS','SHE']

def word_hits(text):
    return [w for w in COMMON if w in text]

def layout_rowcol(i, offset):
    """1-indexed K4 position i -> (row, col) with cols 1..31 in a 31-wide panel.
    offset = column (0-based) at which K4 position 1 sits.  offset=27 is the
    sculpture layout (?OBKR at cols 27-31 of the last K3 row, then 3 rows of 31)."""
    j = i - 1 + offset
    return j // 31, j % 31 + 1

def periodic_crib_test(text, cribs, p, cipher, pa, ca):
    """Periodic key of period p (== column key of a p-wide layout).
    cribs: {1-indexed pos in text: plaintext letter}.
    Returns dict: collisions (#crib pairs sharing a residue), consistent (bool),
    key ({residue: key value}), conflicts ([(residue, {values})]), n_known (residues fixed),
    decrypt (string, '.' for positions whose key residue is unknown), new_letters (decrypted
    non-crib letters only)."""
    key = {}
    conflicts = {}
    collisions = 0
    for pos, pt in cribs.items():
        r = (pos - 1) % p
        k = shift_for(text[pos - 1], pt, cipher, pa, ca)
        if r in key:
            collisions += 1
            if key[r] != k:
                conflicts.setdefault(r, {key[r]}).add(k)
        else:
            key[r] = k
    consistent = not conflicts
    dec = []
    new = []
    for i, ch in enumerate(text):
        r = i % p
        if r in key and r not in conflicts:
            d = decrypt_letter(ch, key[r], cipher, pa, ca)
            dec.append(d)
            if (i + 1) not in cribs:
                new.append(d)
        else:
            dec.append('.')
    return {'collisions': collisions, 'consistent': consistent, 'key': key,
            'conflicts': sorted((r, sorted(v)) for r, v in conflicts.items()),
            'n_known': len(key), 'decrypt': ''.join(dec), 'new_letters': ''.join(new)}
