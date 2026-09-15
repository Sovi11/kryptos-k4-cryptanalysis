"""Shared machinery for the K4 statistical-calibration suite (stat_*.py).

Everything here is about NULL DISTRIBUTIONS: what a statistic looks like when
nothing is going on.  No cipher searching happens in this module.

Design notes
------------
* Letters are handled as integers 0..25 packed into `bytes`, because
  `collections.Counter(bytes)` and `bytes.count()` are C-level and make
  10^7-draw Monte-Carlo feasible in pure Python (no numpy on this machine).
* Every RNG is seeded; every routine has a matching check in stat_validate.py.
"""
from __future__ import annotations

import math
import os
import random
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")

A2Z = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

# ---------------------------------------------------------------- texts -----

def _panel_letters() -> str:
    txt = open(os.path.join(DATA, "sculpture_panels.txt")).read()
    left = txt.split("[LEFT]")[1].split("[RIGHT]")[0]
    rows = [l.strip() for l in left.split("\n") if l.strip() and not l.startswith("#")]
    return "".join(c for c in "".join(rows) if c.isalpha())


PANEL_LET = _panel_letters()
assert len(PANEL_LET) == 865, len(PANEL_LET)

K4 = open(os.path.join(DATA, "k4_ciphertext.txt")).read()
K4 = "".join(c for c in K4 if c.isalpha()).upper()
assert len(K4) == 97

# K1 63 + K2 369 + K3 336 + K4 97 = 865
K1_CT = PANEL_LET[0:63]
K2_CT = PANEL_LET[63:63 + 369]
K3_CT = PANEL_LET[63 + 369:63 + 369 + 336]
K4_CT = PANEL_LET[63 + 369 + 336:]
assert K4_CT == K4


def _plaintexts():
    lines = [l.strip() for l in open(os.path.join(DATA, "k1_k3_plaintext.txt"))
             if l.strip() and not l.startswith("#")]
    return lines


_PT = _plaintexts()
K1_PT, K2_PT, K3_PT = _PT[0], _PT[1], _PT[2]
assert len(K1_PT) == 63 and len(K2_PT) == 370 and len(K3_PT) == 336

# ------------------------------------------------------------ conversion ----

def to_ints(s: str) -> bytes:
    return bytes(ord(c) - 65 for c in s)


def to_str(b: bytes) -> str:
    return "".join(chr(x + 65) for x in b)


K4_B = to_ints(K4)

# ------------------------------------------------------------ statistics ----

def ioc(b) -> float:
    """Index of coincidence, the 'delta' form: sum n(n-1) / (N(N-1)).

    Expected value under a uniform-random 26-letter source is exactly 1/26.
    """
    if isinstance(b, str):
        b = to_ints(b)
    n = len(b)
    if n < 2:
        return 0.0
    c = Counter(b)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1))


def ioc_S(b) -> int:
    """The integer numerator sum n_i (n_i - 1) -- the natural lattice statistic."""
    if isinstance(b, str):
        b = to_ints(b)
    c = Counter(b)
    return sum(v * (v - 1) for v in c.values())


def n_distinct(b) -> int:
    return len(set(b))


def n_doubles(b) -> int:
    """Adjacent equal pairs.  For an i.i.d. uniform source this is exactly
    Binomial(N-1, 1/26) because the successive differences are i.i.d. uniform."""
    if isinstance(b, str):
        b = to_ints(b)
    return sum(1 for i in range(len(b) - 1) if b[i] == b[i + 1])


def coincidences(b, lag: int) -> int:
    if isinstance(b, str):
        b = to_ints(b)
    n = len(b)
    return sum(1 for i in range(n - lag) if b[i] == b[i + lag])


def autocorr_z(b, lag: int) -> float:
    """z of the coincidence count at `lag` against the uniform-random null.

    N-lag independent Bernoulli(1/26) trials -> mean (N-lag)/26,
    sd sqrt((N-lag) * (1/26) * (25/26)).
    """
    if isinstance(b, str):
        b = to_ints(b)
    m = len(b) - lag
    if m <= 0:
        return float("nan")
    obs = coincidences(b, lag)
    mu = m / 26.0
    sd = math.sqrt(m * (1 / 26.0) * (25 / 26.0))
    return (obs - mu) / sd


def periodic_ioc(b, p: int) -> float:
    """Mean IoC of the p columns obtained by slicing every p-th letter."""
    if isinstance(b, str):
        b = to_ints(b)
    vals = []
    for r in range(p):
        col = b[r::p]
        if len(col) >= 2:
            vals.append(ioc(col))
    return sum(vals) / len(vals) if vals else 0.0


def ngram_repeats(b, n: int):
    """{ngram: [start positions]} for n-grams occurring more than once (0-indexed)."""
    if isinstance(b, bytes):
        b = to_str(b)
    seen = {}
    for i in range(len(b) - n + 1):
        seen.setdefault(b[i:i + n], []).append(i)
    return {g: pos for g, pos in seen.items() if len(pos) > 1}


ENGLISH_FREQ = {  # standard reference frequencies, fractions
    'A': .08167, 'B': .01492, 'C': .02782, 'D': .04253, 'E': .12702, 'F': .02228,
    'G': .02015, 'H': .06094, 'I': .06966, 'J': .00153, 'K': .00772, 'L': .04025,
    'M': .02406, 'N': .06749, 'O': .07507, 'P': .01929, 'Q': .00095, 'R': .05987,
    'S': .06327, 'T': .09056, 'U': .02758, 'V': .00978, 'W': .02360, 'X': .00150,
    'Y': .01974, 'Z': .00074}


def chi2_vs(b, freq=None) -> float:
    """Pearson chi-square of the letter counts against a reference distribution
    (default: uniform)."""
    if isinstance(b, bytes):
        b = to_str(b)
    n = len(b)
    c = Counter(b)
    tot = 0.0
    for i, ch in enumerate(A2Z):
        e = n * (freq[ch] if freq else 1 / 26.0)
        tot += (c.get(ch, 0) - e) ** 2 / e
    return tot


# -------------------------------------------------------- exact formulas ----

def coupon_all_present(n: int, c: int = 26) -> float:
    """Exact P(all c letters appear at least once in n i.i.d. uniform draws),
    by inclusion-exclusion."""
    tot = 0.0
    for j in range(c + 1):
        tot += (-1) ** j * math.comb(c, j) * ((c - j) / c) ** n
    return tot


def binom_pmf(k: int, n: int, p: float) -> float:
    return math.comb(n, k) * p ** k * (1 - p) ** (n - k)


def binom_sf(k: int, n: int, p: float) -> float:
    """P(X >= k)."""
    return sum(binom_pmf(j, n, p) for j in range(k, n + 1))


def binom_cdf(k: int, n: int, p: float) -> float:
    """P(X <= k)."""
    return sum(binom_pmf(j, n, p) for j in range(0, k + 1))


def ioc_null_moments(n: int, c: int = 26):
    """Exact mean and sd of the IoC statistic for n i.i.d. uniform letters.

    S = #ordered pairs (j,k), j != k, with equal letters.  E[S] = n(n-1)/c.
    The only non-zero covariances are between (j,k) and (k,j) (identical
    indicators), and both contribute p - p^2, so
        Var(S) = n(n-1) * 2 * p * (1-p),  p = 1/c.
    Hence Var(IoC) = 2 p (1-p) / (n(n-1)).
    """
    p = 1.0 / c
    mean = p
    var = 2 * p * (1 - p) / (n * (n - 1))
    return mean, math.sqrt(var)


def exact_ioc_cdf(n: int, s_cap: int, c: int = 26):
    """EXACT lower tail of the IoC lattice statistic S = sum n_i(n_i-1)
    for n i.i.d. uniform letters over c symbols.

    Returns dict {s: P(S = s)} for s <= s_cap.  (Only the lower tail is
    computed; states with s > s_cap are dropped, which is exactly what we
    want for P(S <= s_obs).)

    DP over letters, tracking W(m, s) = sum over count vectors of prod 1/n_i!.
    Then P(S = s) = n! / c^n * W(n, s).
    """
    # w[m][s] as dict-of-dicts keyed by m for locality
    inv_fact = [1.0]
    for k in range(1, n + 1):
        inv_fact.append(inv_fact[-1] / k)
    # largest count k that can appear at all, i.e. with k(k-1) <= s_cap
    kmax = 0
    while kmax < n and (kmax + 1) * kmax <= s_cap:
        kmax += 1

    cur = [dict() for _ in range(n + 1)]
    cur[0][0] = 1.0
    for letter in range(c):
        nxt = [dict() for _ in range(n + 1)]
        remaining_letters = c - letter - 1
        for m in range(n + 1):
            row = cur[m]
            if not row:
                continue
            # prune: with `remaining_letters` letters left we can place at most
            # remaining_letters * n more, always true; no useful prune, but we
            # can prune m > n.
            for k in range(0, min(kmax, n - m) + 1):
                add = k * (k - 1)
                w = inv_fact[k]
                tgt = nxt[m + k]
                for s, v in row.items():
                    s2 = s + add
                    if s2 > s_cap:
                        continue
                    tgt[s2] = tgt.get(s2, 0.0) + v * w
        cur = nxt
    scale = math.exp(math.lgamma(n + 1) - n * math.log(c))
    return {s: v * scale for s, v in sorted(cur[n].items())}


# ---------------------------------------------------------- random pools ----

class LetterPool:
    """Unbiased uniform 0..25 letters from random.randbytes, via rejection."""

    def __init__(self, seed: int, chunk: int = 1 << 21):
        self.rng = random.Random(seed)
        self.chunk = chunk
        self.buf = b""
        self.pos = 0

    def _refill(self, need: int):
        parts = [self.buf[self.pos:]]
        have = len(parts[0])
        while have < need:
            raw = self.rng.randbytes(self.chunk)
            good = bytes(x % 26 for x in raw if x < 234)
            parts.append(good)
            have += len(good)
        self.buf = b"".join(parts)
        self.pos = 0

    def take(self, k: int) -> bytes:
        if self.pos + k > len(self.buf):
            self._refill(max(k, self.chunk))
        out = self.buf[self.pos:self.pos + k]
        self.pos += k
        return out


# ------------------------------------------------------- English corpus -----

_CORPUS_CACHE = None


def english_corpus() -> bytes:
    """A large real-English letter stream (A-Z only), as 0..25 bytes.

    Source: analysis/.search_corpus.txt, ~22.4M letters of English prose
    (system manual pages / documentation).  Verified IoC 0.06594, which is
    normal English (0.066-0.067).  If it is missing, fall back to the
    Kryptos K1-K3 plaintexts repeated, and say so.
    """
    global _CORPUS_CACHE
    if _CORPUS_CACHE is not None:
        return _CORPUS_CACHE
    binpath = os.path.join(HERE, ".stat_corpus.bin")   # 0..25 bytes, built once
    if os.path.exists(binpath):
        _CORPUS_CACHE = open(binpath, "rb").read()
        return _CORPUS_CACHE
    path = os.path.join(HERE, ".search_corpus.txt")
    if os.path.exists(path):
        s = open(path).read()
        s = "".join(c for c in s if c.isalpha()).upper()
    else:  # pragma: no cover
        s = (K1_PT + K2_PT + K3_PT) * 500
    _CORPUS_CACHE = to_ints(s)
    with open(binpath, "wb") as f:
        f.write(_CORPUS_CACHE)
    return _CORPUS_CACHE


def english_windows(n_windows: int, length: int, seed: int, corpus=None):
    """Random contiguous `length`-letter windows of real English."""
    corpus = corpus if corpus is not None else english_corpus()
    rng = random.Random(seed)
    hi = len(corpus) - length - 1
    for _ in range(n_windows):
        i = rng.randrange(hi)
        yield corpus[i:i + length]


# ------------------------------------------------------------- ciphers ------

def vigenere(pt: bytes, key: bytes) -> bytes:
    L = len(key)
    return bytes((pt[i] + key[i % L]) % 26 for i in range(len(pt)))


def beaufort(pt: bytes, key: bytes) -> bytes:
    L = len(key)
    return bytes((key[i % L] - pt[i]) % 26 for i in range(len(pt)))


def running_key(pt: bytes, key: bytes) -> bytes:
    return bytes((pt[i] + key[i]) % 26 for i in range(len(pt)))


def autokey_pt(pt: bytes, primer: bytes) -> bytes:
    ks = primer + pt
    return bytes((pt[i] + ks[i]) % 26 for i in range(len(pt)))


def gromark(pt: bytes, primer_digits, base: int = 10):
    """Gromark: lagged-Fibonacci numeric keystream added to the plaintext.

    k_i = k_{i-n} + k_{i-n+1} (mod base), seeded by the primer.  The keystream
    digit is added mod 26 to the plaintext index (the ACA form uses a mixed
    ct alphabet, which does not change any of the statistics computed here).
    """
    n = len(primer_digits)
    ks = list(primer_digits)
    while len(ks) < len(pt):
        ks.append((ks[-n] + ks[-n + 1]) % base)
    return bytes((pt[i] + ks[i]) % 26 for i in range(len(pt)))


def random_polyalpha(pt: bytes, alphabets) -> bytes:
    """General periodic polyalphabetic: alphabets[i % p] is an arbitrary
    permutation of 0..25 applied at position i."""
    p = len(alphabets)
    return bytes(alphabets[i % p][pt[i]] for i in range(len(pt)))


def transpose(pt: bytes, perm) -> bytes:
    return bytes(pt[i] for i in perm)


# --------------------------------------------------------------- utils ------

def percentile_of(sorted_vals, x) -> float:
    """Fraction of the sample <= x (left tail)."""
    import bisect
    return bisect.bisect_right(sorted_vals, x) / len(sorted_vals)


def frac_ge(sorted_vals, x) -> float:
    import bisect
    return 1.0 - bisect.bisect_left(sorted_vals, x) / len(sorted_vals)


def quantiles(sorted_vals, qs=(0.005, 0.025, 0.05, 0.25, 0.5, 0.75, 0.95, 0.975, 0.995)):
    m = len(sorted_vals)
    return {q: sorted_vals[min(m - 1, int(q * m))] for q in qs}


def mean_sd(vals):
    m = sum(vals) / len(vals)
    v = sum((x - m) ** 2 for x in vals) / len(vals)
    return m, math.sqrt(v)
