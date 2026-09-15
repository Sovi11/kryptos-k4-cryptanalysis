"""Shared helpers for the 'what a 1988 CIA cryptographer would teach' sweep.

Covers: straddling checkerboard / VIC, homophonic & polyphonic substitution,
nomenclator / codebook elements, fractionation with an UNKNOWN square (CSP),
and rotor / Enigma-like (self-map-forbidding) systems.

Everything here is 0-indexed internally; data/cribs.json is 1-indexed.
"""
import json
import os
import random
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
FINDINGS = os.path.join(ROOT, "findings")

A2Z = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

with open(os.path.join(DATA, "k4_ciphertext.txt")) as f:
    CT = "".join(ch for ch in f.read() if ch.isalpha()).upper()
assert len(CT) == 97
N = 97

with open(os.path.join(DATA, "cribs.json")) as f:
    _cj = json.load(f)["cribs"]

# CRIBS: list of (0-indexed position, ciphertext letter, plaintext letter)
CRIBS = []
for c in _cj:
    p0 = c["pos"] - 1
    assert CT[p0:p0 + len(c["ct"])] == c["ct"], c
    assert len(c["ct"]) == len(c["pt"])
    for i, (cc, pp) in enumerate(zip(c["ct"], c["pt"])):
        CRIBS.append((p0 + i, cc, pp))
assert len(CRIBS) == 24

CRIB_POS = [p for p, _, _ in CRIBS]
CRIB_PT = {p: pt for p, _, pt in CRIBS}          # 0-indexed pos -> plaintext letter
# contiguous crib runs, 0-indexed [start, end)
CRIB_RUNS = [(21, 34), (63, 74)]                 # EASTNORTHEAST, BERLINCLOCK
assert "".join(CRIB_PT[p] for p in range(21, 34)) == "EASTNORTHEAST"
assert "".join(CRIB_PT[p] for p in range(63, 74)) == "BERLINCLOCK"


def ioc(s):
    n = len(s)
    if n < 2:
        return 0.0
    c = Counter(s)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1))


def keyed_alphabet(word, base=A2Z):
    seen, out = set(), []
    for ch in word.upper():
        if ch in base and ch not in seen:
            seen.add(ch)
            out.append(ch)
    for ch in base:
        if ch not in seen:
            out.append(ch)
    return "".join(out)


def random_crib_letters(rng):
    """A random plaintext assignment for the 24 crib positions, used to
    measure the CHANCE rate at which a model admits a 'solution'.

    Letter frequencies are drawn from English so the null is not artificially
    easy or hard; positions are kept identical to the real cribs."""
    return [rng.choice(ENGLISH_POOL) for _ in range(24)]


# English letter pool weighted by frequency (per 1000)
_FREQ = dict(zip(A2Z, [82, 15, 28, 43, 127, 22, 20, 61, 70, 2, 8, 40, 24,
                       67, 75, 19, 1, 60, 63, 91, 28, 10, 24, 2, 20, 1]))
ENGLISH_POOL = "".join(ch * _FREQ[ch] for ch in A2Z)


def load_quadgrams():
    path = os.path.join(HERE, ".quadgrams_cache.json")
    with open(path) as f:
        return json.load(f)
