"""Shared helpers for the second-wave K4 geometry work (geo2_*).

Adds to geometry_common:
  * the full left panel (869 chars incl. the four '?'), with K4's absolute offset;
  * a library of physical reading orders over the 4+31+31+31 K4 block;
  * crib-aware permutation handling (subsets allowed);
  * exact chance bookkeeping for the periodic-key consistency test.
"""
import os, random, math
from collections import Counter
import geometry_common as g

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')

CT = g.CT
CRIB = g.CRIB
N = 97
COMBOS = [(c, pa, ca) for c in g.CIPHERS for pa, ca in g.ALPHA_PAIRS]

# ---------------------------------------------------------------- panel -----
def _load_panel():
    txt = open(os.path.join(DATA, 'sculpture_panels.txt')).read()
    left = txt.split('[LEFT]')[1].split('[RIGHT]')[0]
    rows = [l.strip() for l in left.split('\n') if l.strip() and not l.startswith('#')]
    return rows

PANEL_ROWS = _load_panel()
PANEL_ALL = ''.join(PANEL_ROWS)            # 869 chars, includes 4 '?'
PANEL_LET = ''.join(c for c in PANEL_ALL if c.isalpha())   # 865 letters
K4_OFF_ALL = PANEL_ALL.index(CT)           # 0-indexed start of K4 among all 869
K4_OFF_LET = PANEL_LET.index(CT)           # 0-indexed start of K4 among 865 letters
assert len(PANEL_ALL) == 869 and len(PANEL_LET) == 865
assert K4_OFF_ALL == 772 and K4_OFF_LET == 768

# ------------------------------------------------------- the K4 grid --------
# row 0 holds OBKR at 1-indexed cols 28..31 (the '?' sits at col 27 and belongs to K3);
# rows 1..3 hold 31 letters each.
CELLS = []          # (row, col0, orig0) with col0 0-indexed 0..30
for i in range(N):
    j = i + 27
    CELLS.append((j // 31, j % 31, i))
CELL_AT = {(r, c): o for r, c, o in CELLS}
ROWS4 = [[o for r, c, o in CELLS if r == R] for R in range(4)]
assert [len(r) for r in ROWS4] == [4, 31, 31, 31]

# ------------------------------------------------------- permutations -------
def apply_perm(perm, ct=CT, cribs=CRIB):
    """perm[j] = original 0-indexed position of new position j (may be a subset).
    Returns (text, {1-indexed new pos: plaintext letter})."""
    text = ''.join(ct[i] for i in perm)
    inv = {orig: j for j, orig in enumerate(perm)}
    nc = {inv[pos - 1] + 1: pt for pos, pt in cribs.items() if (pos - 1) in inv}
    return text, nc

def n_collisions(cribs, p):
    """#crib constraints = 24 - (#distinct residues mod p) among the crib positions."""
    return len(cribs) - len({(pos - 1) % p for pos in cribs})

def consistency(text, cribs, p, cmb):
    return g.periodic_crib_test(text, cribs, p, *cmb)

# ------------------------------------------------------- statistics ---------
def periodic_ioc(text, p):
    return g.periodic_ioc(text, p)

_rng = random.Random(20260912)

def periodic_ioc_null(text, p, trials=2000):
    """Null distribution of periodic IoC for a random shuffle of the SAME letters."""
    chars = list(text)
    vals = []
    for _ in range(trials):
        _rng.shuffle(chars)
        vals.append(g.periodic_ioc(''.join(chars), p))
    vals.sort()
    mean = sum(vals) / len(vals)
    return mean, vals[int(0.95 * len(vals))], vals[-1]

def ioc(t):
    return g.ioc(t)

def logp(t):
    return g.unigram_logp(t)

def words(t):
    return g.word_hits(t)
