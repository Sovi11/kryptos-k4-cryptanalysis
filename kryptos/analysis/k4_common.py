"""Shared helpers for the K4 cipher-family sweeps.

Everything is 0-indexed internally; the cribs.json positions are 1-indexed.
"""
import json
import math
import os
import re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")

A2Z = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

with open(os.path.join(DATA, "k4_ciphertext.txt")) as f:
    CT = "".join(ch for ch in f.read() if ch.isalpha()).upper()
assert len(CT) == 97

with open(os.path.join(DATA, "cribs.json")) as f:
    _cribs = json.load(f)["cribs"]

# 0-indexed position -> plaintext letter
CRIB = {}
for c in _cribs:
    start = c["pos"] - 1
    assert CT[start:start + len(c["ct"])] == c["ct"], c
    for k, p in enumerate(c["pt"]):
        CRIB[start + k] = p
CRIB_POS = sorted(CRIB)          # 24 positions
CRIB_PT = [CRIB[i] for i in CRIB_POS]
CRIB_CT = [CT[i] for i in CRIB_POS]

SHORT_KEYWORDS = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "SANBORN", "SCHEIDT", "LANGLEY",
                  "BERLIN", "CLOCK", "COMPASS", "LODESTONE", "SHADOW", "IQLUSION",
                  "UNDERGRUUND", "DESPARATLY", "LAYERTWO", "MASKING"]


def keyed_alphabet(keyword, base=A2Z):
    """Keyword-mixed alphabet: keyword letters (deduplicated) then the rest of `base`."""
    seen = []
    for ch in keyword.upper():
        if ch in base and ch not in seen:
            seen.append(ch)
    return "".join(seen) + "".join(ch for ch in base if ch not in seen)


def dict_alphabets(min_len=3):
    """Distinct keyword-mixed alphabets from /usr/share/dict/words, with the word that produced each."""
    out = {}
    with open("/usr/share/dict/words") as f:
        for w in f:
            w = w.strip().upper()
            if len(w) < min_len or not w.isalpha() or not w.isascii():
                continue
            a = keyed_alphabet(w)
            if a not in out:
                out[a] = w
    return out


def period_pairs(period, positions=CRIB_POS):
    """Index pairs (into the crib-position list) that must carry equal key values for this period."""
    by_res = {}
    for k, pos in enumerate(positions):
        by_res.setdefault(pos % period, []).append(k)
    pairs = []
    for res, ks in by_res.items():
        for j in range(1, len(ks)):
            pairs.append((ks[0], ks[j]))
    return pairs


def constraints_per_period(period, positions=CRIB_POS):
    return len(positions) - len({p % period for p in positions})


# --------------------------------------------------------------------------
# English scoring.  Small bigram model built from the K1-K3 plaintext plus an
# original prose passage (both embedded), add-0.5 smoothing.  This is a
# coarse "does this look like English" gauge, not a quadgram model.
# --------------------------------------------------------------------------
_PROSE = """
It was a bright cold day in the middle of the month and the streets of the small
town were nearly empty. The old man walked slowly along the river with his hands in
his pockets, thinking about the letter that had arrived that morning. There was
nothing in it that he had not expected, and yet the words seemed to carry a weight
that surprised him. He stopped at the bridge and looked down at the water, which was
high after the rain and moving quickly under the stone arches. Somewhere behind him
a door closed and a woman called out a name he did not recognize. He thought of the
house where he had grown up, of the garden and the apple trees and the long summer
evenings when the light seemed to last forever. All of that was gone now, sold years
ago to people he had never met. The letter was from his brother, who wrote once a
year, always at the same time, always saying the same things about the weather and
the children and the state of the roads. He folded the paper again and put it back
in his coat. Across the river the church bell began to ring, and a few people came
out of the shops to see what the noise was about. It was only the hour. Nothing had
happened. He walked on toward the station where the afternoon train would soon be
leaving, and he wondered whether he would find a seat by the window. The information
was gathered slowly and transmitted to those who needed it. Between the lines of the
report there was a clear direction north and east from the point of origin, and the
time was marked on the clock. Those who could see the whole picture were few. The
secret lay buried somewhere out there, and only a handful of people knew the exact
location. They said it was totally invisible, a shadow of a shadow, but the truth
was that it had been in plain sight all along, waiting for someone to look.
"""


def _load_corpus():
    text = re.sub("[^A-Z]", "", _PROSE.upper())
    with open(os.path.join(DATA, "k1_k3_plaintext.txt")) as f:
        for line in f:
            if not line.startswith("#"):
                text += re.sub("[^A-Z]", "", line.upper())
    return text


_CORPUS = _load_corpus()
_MONO = Counter(_CORPUS)
_BI = Counter(_CORPUS[i:i + 2] for i in range(len(_CORPUS) - 1))
_N1 = sum(_MONO.values())
_N2 = sum(_BI.values())
LOGP_MONO = {a: math.log((_MONO[a] + 0.5) / (_N1 + 13)) for a in A2Z}
LOGP_BI = {a + b: math.log((_BI[a + b] + 0.5) / (_N2 + 338)) for a in A2Z for b in A2Z}
# Standard English monogram frequencies (percent), for chi-square tests.
ENG_FREQ = dict(zip(A2Z, [8.17, 1.49, 2.78, 4.25, 12.70, 2.23, 2.02, 6.09, 6.97, 0.15, 0.77, 4.03,
                          2.41, 6.75, 7.51, 1.93, 0.10, 5.99, 6.33, 9.06, 2.76, 0.98, 2.36, 0.15,
                          1.97, 0.07]))


def bigram_score(text):
    """Mean bigram log-prob per adjacent letter pair; '?' (unknown) breaks runs.
    English text scores around -5.2 to -5.6 with this model; random text around -6.9."""
    n = 0
    s = 0.0
    for i in range(len(text) - 1):
        a, b = text[i], text[i + 1]
        if a == "?" or b == "?":
            continue
        s += LOGP_BI[a + b]
        n += 1
    return s / n if n else float("-inf")


def chi2_english(text):
    letters = [c for c in text if c in A2Z]
    n = len(letters)
    if n == 0:
        return float("inf")
    cnt = Counter(letters)
    return sum((cnt[a] - n * ENG_FREQ[a] / 100) ** 2 / (n * ENG_FREQ[a] / 100) for a in A2Z)


def ioc(text):
    letters = [c for c in text if c in A2Z]
    n = len(letters)
    if n < 2:
        return 0.0
    cnt = Counter(letters)
    return sum(v * (v - 1) for v in cnt.values()) / (n * (n - 1))


_WORDS = None


def dict_words_in(text, min_len=4):
    """Dictionary words (>= min_len) occurring as substrings, excluding those inside the cribs."""
    global _WORDS
    if _WORDS is None:
        _WORDS = set()
        with open("/usr/share/dict/words") as f:
            for w in f:
                w = w.strip().upper()
                if len(w) >= min_len and w.isalpha() and w.isascii():
                    _WORDS.add(w)
    found = []
    for i in range(len(text)):
        for L in range(min_len, min(12, len(text) - i) + 1):
            sub = text[i:i + L]
            if "?" in sub:
                break
            if sub in _WORDS:
                found.append((i, sub))
    return found


def mark_cribs(pt):
    """Lower-case the crib positions so the reader can tell forced letters from derived ones."""
    return "".join(ch.lower() if i in CRIB else ch for i, ch in enumerate(pt))


def noncrib(text):
    return "".join(ch for i, ch in enumerate(text) if i not in CRIB)


def random_baseline(n=2000, seed=1):
    """Bigram-score distribution of random 26-letter text of length 73 (the non-crib count)."""
    import random
    rnd = random.Random(seed)
    scores = sorted(bigram_score("".join(rnd.choice(A2Z) for _ in range(73))) for _ in range(n))
    return scores[len(scores) // 2], scores[int(0.99 * n)], scores[-1]


if __name__ == "__main__":
    print("CT:", CT)
    print("crib positions (0-idx):", CRIB_POS)
    print("crib pairs:", list(zip(CRIB_CT, CRIB_PT)))
    print("corpus letters:", _N1)
    print("bigram score english (K3 sample):", bigram_score(_CORPUS[-300:]))
    print("bigram score random median/99%/max:", random_baseline())
    for p in range(2, 27):
        print("period", p, "constraints", constraints_per_period(p), "chance survival 26^-c =", 26.0 ** -constraints_per_period(p))
