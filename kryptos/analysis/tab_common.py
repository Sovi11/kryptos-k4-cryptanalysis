"""Shared helpers for the tab_* line of attack: the Kryptos tableau as a KEY TABLE.

Distinct from runningkey_lib.py (tableau as a linear string, already exhausted) and
complementary to tableau_common.py (whose engine is reused and independently re-verified
here against k4_common).

Conventions
-----------
* K4 positions 0-indexed (0..96).  cribs.json is 1-indexed.
* A "combo" is (family, pt_alphabet, ct_alphabet, key_alphabet); 24 of them.
* "rotation": the carved key letter may be the required key letter rotated by an unknown
  constant r in the key alphabet.  Testing for a CONSTANT difference between carved and
  required key indices covers all 26 rotations in one test, and the modal frequency of
  that difference is the best-over-rotations crib-match count.

Chance bookkeeping used everywhere
----------------------------------
  rot fixed  : P(one trial matches all 24) = 26^-24 = 1.86e-34
  rot free   : P(one trial matches all 24) = 26^-23 = 4.84e-33
  best-of-26-rotations match count for a RANDOM stream: Monte-Carlo'd in null_modal().
"""
import os
import sys
import math
import random
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
FINDINGS = os.path.join(ROOT, "findings")

import numpy as np
import tableau_common as tc
import k4_common as k4

PLAIN = tc.PLAIN
KEYED = tc.KEYED
ALPHAS = tc.ALPHAS
COMBOS = tc.COMBOS
combo_name = tc.combo_name
CRIB_POS = tc.CRIB_POS
CRIB_PT = tc.CRIB_PT
CRIB_CT = tc.CRIB_CT
K4_CT = tc.K4_CT
RIGHT_ROWS = tc.RIGHT_ROWS                 # 28 carved rows, letters only
RIGHT_ROWS_IDEAL = tc.RIGHT_ROWS_IDEAL
LEFT_ROWS = tc.LEFT_ROWS
TAB_PHYS = tc.TABLEAU_PHYS_STR             # 867 letters
TAB_IDEAL = tc.TABLEAU_IDEAL_STR           # 866 letters

POS = np.array(CRIB_POS, dtype=np.int64)
REQ = {cb: np.array(tc.required_key_indices(cb), dtype=np.int64) for cb in COMBOS}

# letter -> index in each alphabet, as a 26-entry LUT keyed by PLAIN index
PLAIN_IDX = {c: i for i, c in enumerate(PLAIN)}
KEYED_IDX = {c: i for i, c in enumerate(KEYED)}
IDX = {"plain": PLAIN_IDX, "keyed": KEYED_IDX}


def as_idx(text, alpha):
    """letters -> numpy array of indices in the named alphabet."""
    d = IDX[alpha]
    return np.array([d[c] for c in text], dtype=np.int64)


# ---------------------------------------------------------------- crib tests ----
def modal_counts(diff):
    """diff: (N, 24) int array of (req - stream) mod 26.  Returns (N,) best-over-rotation
    match counts and (N,) the winning rotation."""
    n = diff.shape[0]
    flat = (diff + 26 * np.arange(n, dtype=np.int64)[:, None]).ravel()
    cnt = np.bincount(flat, minlength=26 * n).reshape(n, 26)
    return cnt.max(axis=1), cnt.argmax(axis=1)


def crib_match_matrix(kidx, cb):
    """kidx: (N, 24) key indices already expressed in cb's key alphabet.
    Returns (best_counts, rotations, exact_counts_at_rot0)."""
    req = REQ[cb]
    diff = (req[None, :] - kidx) % 26
    best, rot = modal_counts(diff)
    exact0 = (diff == 0).sum(axis=1)
    return best, rot, exact0


def crib_match_stream(cb, key_letters):
    """Best-over-rotation crib match for one 97-letter key stream (letters)."""
    ak = cb[3]
    kidx = np.array([[IDX[ak][key_letters[p]] for p in CRIB_POS]], dtype=np.int64)
    best, rot, exact0 = crib_match_matrix(kidx, cb)
    return int(best[0]), int(rot[0]), int(exact0[0])


_rng = random.Random(20260913)


def null_modal(trials=200000, seed=20260913):
    """Monte-Carlo null for the best-over-26-rotations crib-match count of a random
    24-letter key stream.  Returns (mean, p95, p99, max, P(>=k) table)."""
    rs = np.random.RandomState(seed)
    diff = rs.randint(0, 26, size=(trials, 24))
    best, _ = modal_counts(diff)
    cnt = Counter(best.tolist())
    tail = {}
    for k in range(1, 25):
        tail[k] = float((best >= k).mean())
    return float(best.mean()), int(np.percentile(best, 95)), int(np.percentile(best, 99)), \
        int(best.max()), tail


def null_exact(trials=200000, seed=20260914):
    rs = np.random.RandomState(seed)
    diff = rs.randint(0, 26, size=(trials, 24))
    ex = (diff == 0).sum(axis=1)
    return float(ex.mean()), int(ex.max())


def expected_hits(n_trials, rot_free=True):
    return n_trials * (26.0 ** (-23 if rot_free else -24))


def _binom_sf(k, n=24, p=1.0 / 26.0):
    """P(Binomial(n,p) >= k), exact."""
    tot = 0.0
    for i in range(k, n + 1):
        tot += math.comb(n, i) * p ** i * (1 - p) ** (n - i)
    return tot


def rate_bound(k):
    """Analytic UNION BOUND on P(best-over-26-rotations crib match >= k) for a random
    24-letter key stream: at most 26 * P(Binomial(24,1/26) >= k).  Tight for small p and
    valid for every k (the Monte-Carlo null runs out of resolution above 9/24)."""
    if k <= 0:
        return 1.0
    return min(1.0, 26.0 * _binom_sf(k))


ENGLISH_REF = None


def english(text):
    """Bigram log-prob per pair under k4_common's model.  English ~ -5.2..-5.6,
    uniform-random 26-letter text ~ -6.9."""
    return k4.bigram_score(text)


def score_report(cb, key_letters):
    """Full 97-letter decryption of K4 under (combo, key stream) with English gauges."""
    pt = tc.decrypt(cb, key_letters)
    return {
        "pt": pt,
        "marked": k4.mark_cribs(pt),
        "bigram": english(pt),
        "bigram_noncrib": english(k4.noncrib(pt)),
        "ioc": k4.ioc(pt),
        "words": [wd for _, wd in k4.dict_words_in(pt, 5)],
        "cribs": tc.crib_matches(cb, key_letters),
    }


# ------------------------------------------------------- period bookkeeping ----
def constraints(period, positions=CRIB_POS):
    return len(positions) - len({p % period for p in positions})


# ---------------------------------------------------------------- selftest ----
def selftest(verbose=True):
    """Round-trip + synthetic-key recovery.  Nothing downstream is trusted without this."""
    msgs = []

    # 1. the two independent data loaders agree
    assert tc.K4_CT == k4.CT, "tableau_common and k4_common disagree on the ciphertext"
    assert tc.CRIB_POS == k4.CRIB_POS and tc.CRIB_PT == k4.CRIB_PT, "crib disagreement"
    assert len(K4_CT) == 97 and len(CRIB_POS) == 24
    msgs.append("data loaders agree: 97-letter CT, 24 cribs (k4_common vs tableau_common)")

    # 2. encrypt/decrypt round trip on every combo with a random key
    rs = random.Random(7)
    for cb in COMBOS:
        key = "".join(rs.choice(PLAIN) for _ in range(97))
        pt = "".join(rs.choice(PLAIN) for _ in range(97))
        ct = tc.encrypt(cb, pt, key)
        assert tc.decrypt(cb, key) is not None
        # decrypt() works on K4_CT, so round-trip through the primitive directly
        fam, ap, ac, ak = cb
        back = []
        for C, K in zip(ct, key):
            c, kk = ALPHAS[ac].index(C), ALPHAS[ak].index(K)
            if fam == "vigenere":
                p = (c - kk) % 26
            elif fam == "beaufort":
                p = (kk - c) % 26
            else:
                p = (c + kk) % 26
            back.append(ALPHAS[ap][p])
        assert "".join(back) == pt, cb
    msgs.append("encrypt/decrypt round trip: 24/24 combos OK")

    # 3. K1 re-encryption reproduces the carved K1 ciphertext (real-world check)
    import runningkey_lib as rk
    v = rk.verify_k1_k2()
    assert v["K1"][0] is True, v["K1"]
    msgs.append("K1 re-encrypts to the carved ciphertext under Quagmire-III/PALIMPSEST")

    # 4. SYNTHETIC KEY RECOVERY: plant a known 97-letter key, rebuild the crib
    #    requirements it implies, and confirm crib_match_matrix returns 24/24 for it and
    #    chance for a perturbation.
    for cb in COMBOS:
        key = "".join(rs.choice(PLAIN) for _ in range(97))
        ak = cb[3]
        kidx = np.array([[IDX[ak][key[p]] for p in CRIB_POS]], dtype=np.int64)
        # forge requirements = exactly this key
        saved = REQ[cb].copy()
        REQ[cb][:] = kidx[0]
        best, rot, ex0 = crib_match_matrix(kidx, cb)
        assert best[0] == 24 and ex0[0] == 24 and rot[0] == 0, (cb, best, ex0)
        # rotate the planted key by 5: must still be 24/24 best-over-rotation, 0 exact
        kr = (kidx + 5) % 26
        best2, rot2, ex2 = crib_match_matrix(kr, cb)
        assert best2[0] == 24 and rot2[0] == 21, (cb, best2, rot2)
        # perturb one position: must drop to 23
        kp = kidx.copy()
        kp[0, 3] = (kp[0, 3] + 1) % 26
        best3, _, _ = crib_match_matrix(kp, cb)
        assert best3[0] == 23, (cb, best3)
        REQ[cb][:] = saved
    msgs.append("synthetic-key recovery: planted key found at 24/24 under all 24 combos, "
                "rotation recovered, single perturbation detected")

    # 5. the carved tableau is what we think it is
    assert len(TAB_PHYS) == 867 and len(TAB_IDEAL) == 866
    msgs.append("carved tableau 867 letters, ideal 866")

    if verbose:
        for m in msgs:
            print("  [selftest] " + m)
    return msgs


if __name__ == "__main__":
    selftest()
    m, p95, p99, mx, tail = null_modal()
    print("null best-of-26-rotations crib match: mean %.3f  p95 %d  p99 %d  max %d" % (m, p95, p99, mx))
    print("  P(>=k):", {k: round(v, 6) for k, v in tail.items() if v > 0})
    print("null rot-0 exact match: mean %.3f max %d" % null_exact())
