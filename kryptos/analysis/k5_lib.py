"""Shared helpers for the k5_* line of attack (method genealogy / K5 lever /
cross-section phase / the question mark / OBKR as an indicator).

Everything here is validated by `selftest()`, which plants known ciphers and checks
that the routines recover or reject them.  Nothing in k5_c/k5_d/k5_e trusts a negative
that has not passed it.

Conventions
-----------
* 0-indexed internally, 1-indexed only when printing.
* A "combo" is (rule, pt_alphabet_name, ct_alphabet_name).  The KEY alphabet only
  relabels key values bijectively and so is irrelevant to any consistency test; it
  matters only when a concrete key TEXT is supplied, which is handled separately.
* `rule` in {vigenere, beaufort, varbeaufort}:
      vigenere     ct = CTA[(pt + k) % 26]     k = ct - pt
      beaufort     ct = CTA[(k - pt) % 26]     k = ct + pt
      varbeaufort  ct = CTA[(pt - k) % 26]     k = pt - ct
"""
import os
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import k4_common as K

A2Z = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
CT = K.CT
N = 97
CRIB = K.CRIB                       # 0-indexed pos -> plaintext letter
CRIB_POS = K.CRIB_POS               # 24 sorted positions
CRIB_PT = "".join(CRIB[i] for i in CRIB_POS)
CRIB_CT = "".join(CT[i] for i in CRIB_POS)

RULES = ("vigenere", "beaufort", "varbeaufort")
_RID = {r: i for i, r in enumerate(RULES)}


def keyed_alphabet(keyword, base=A2Z):
    seen = []
    for ch in keyword.upper():
        if ch in base and ch not in seen:
            seen.append(ch)
    return "".join(seen) + "".join(ch for ch in base if ch not in seen)


def code(s):
    return np.frombuffer(s.encode(), dtype=np.uint8).astype(np.int64) - 65


# ------------------------------------------------------------------ key algebra
def required_key(rid, pt_idx, ct_idx):
    if rid == 0:
        return (ct_idx - pt_idx) % 26
    if rid == 1:
        return (ct_idx + pt_idx) % 26
    return (pt_idx - ct_idx) % 26


def ct_from(rid, pt_idx, k):
    if rid == 0:
        return (pt_idx + k) % 26
    if rid == 1:
        return (k - pt_idx) % 26
    return (pt_idx - k) % 26


def pt_from(rid, ct_idx, k):
    if rid == 0:
        return (ct_idx - k) % 26
    if rid == 1:
        return (k - ct_idx) % 26
    return (ct_idx + k) % 26


def encrypt(pt, keyvals, rule, pta=A2Z, cta=A2Z):
    rid = _RID[rule]
    return "".join(cta[ct_from(rid, pta.index(c), keyvals[i % len(keyvals)])]
                   for i, c in enumerate(pt))


def decrypt(ct, keyvals, rule, pta=A2Z, cta=A2Z):
    rid = _RID[rule]
    return "".join(pta[pt_from(rid, cta.index(c), keyvals[i % len(keyvals)])]
                   for i, c in enumerate(ct))


# ------------------------------------------------- explicit key-stream scoring
class Combos:
    """All (rule x pt alphabet x ct alphabet x key alphabet) combos over an
    alphabet list, as flat arrays, for fast scoring of explicit key streams."""

    def __init__(self, alphabets):
        self.names = [n for n, _ in alphabets]
        self.strs = [a for _, a in alphabets]
        self.AID = np.array([[a.index(ch) for ch in A2Z] for a in self.strs],
                            dtype=np.int64)
        self.rid, self.pid, self.cid, self.kid, self.labels = [], [], [], [], []
        for r in RULES:
            for i in range(len(self.strs)):
                for j in range(len(self.strs)):
                    for k in range(len(self.strs)):
                        self.rid.append(_RID[r])
                        self.pid.append(i)
                        self.cid.append(j)
                        self.kid.append(k)
                        self.labels.append("%s/pt=%s/ct=%s/key=%s"
                                           % (r, self.names[i], self.names[j],
                                              self.names[k]))
        for a in ("rid", "pid", "cid", "kid"):
            setattr(self, a, np.array(getattr(self, a)))
        self.n = len(self.labels)


def crib_agreement(keytext, combos, ct=CT, cribs=None):
    """For an explicit 97+-letter KEY TEXT, count how many of the 24 crib letters each
    combo reproduces.  Returns an int array of length combos.n."""
    if cribs is None:
        cribs = CRIB
    pos = np.array(sorted(cribs), dtype=np.int64)
    ptc = code("".join(cribs[i] for i in sorted(cribs)))
    ctc = code("".join(ct[i] for i in pos))
    kc = code(keytext[:len(ct)])[pos]
    pidx = combos.AID[combos.pid][:, ptc]
    cidx = combos.AID[combos.cid][:, ctc]
    kidx = combos.AID[combos.kid][:, kc]
    need = np.where(combos.rid[:, None] == 0, (cidx - pidx) % 26,
                    np.where(combos.rid[:, None] == 1, (cidx + pidx) % 26,
                             (pidx - cidx) % 26))
    return (need == kidx).sum(axis=1)


def tail_expect(n_tests, m, k=24, p=1.0 / 26.0):
    """Expected number of tests, out of n_tests, that reach >= m of k crib letters by
    chance alone.  This is the only correct yardstick for a 'best of N' figure."""
    from math import comb
    tail = sum(comb(k, j) * p ** j * (1 - p) ** (k - j) for j in range(m, k + 1))
    return n_tests * tail


# ------------------------------------------------------ periodic crib sweeping
class Sweeper:
    """Periodic-key crib-consistency test over an arbitrary placement.

    placement = list of (0-indexed position, plaintext letter) with the ciphertext
    taken from `ct`.  The key alphabet is irrelevant here (it only relabels key
    values), so only rule x pt-alphabet x ct-alphabet is enumerated.
    """

    def __init__(self, alphabets):
        self.names = [n for n, _ in alphabets]
        self.strs = [a for _, a in alphabets]
        self.AID = np.array([[a.index(ch) for ch in A2Z] for a in self.strs],
                            dtype=np.int64)
        rid, pid, cid, labels = [], [], [], []
        for r in RULES:
            for i in range(len(self.strs)):
                for j in range(len(self.strs)):
                    rid.append(_RID[r]); pid.append(i); cid.append(j)
                    labels.append("%s/pt=%s/ct=%s" % (r, self.names[i], self.names[j]))
        self.rid, self.pid, self.cid = np.array(rid), np.array(pid), np.array(cid)
        self.labels = labels
        self.n = len(labels)

    def keys(self, positions, ptletters, ctletters):
        ptc, ctc = code(ptletters), code(ctletters)
        pidx = self.AID[self.pid][:, ptc]
        cidx = self.AID[self.cid][:, ctc]
        Km = np.where(self.rid[:, None] == 0, (cidx - pidx) % 26,
                      np.where(self.rid[:, None] == 1, (cidx + pidx) % 26,
                               (pidx - cidx) % 26))
        return np.asarray(positions, dtype=np.int64), ptc, ctc, Km

    def sweep(self, positions, ptletters, ctletters, periods):
        """Returns (rows, total_chance) where rows = (period, c, n_survivors,
        chance_per_test, survivor_combo_indices)."""
        pos, ptc, ctc, Km = self.keys(positions, ptletters, ctletters)
        rows = []
        for p in periods:
            res = pos % p
            ok = np.ones(self.n, dtype=bool)
            c = 0
            for r in np.unique(res):
                g = np.nonzero(res == r)[0]
                if g.size < 2:
                    continue
                c += g.size - 1
                ok &= (Km[:, g] == Km[:, g[0]][:, None]).all(axis=1)
            rows.append((p, c, int(ok.sum()), 26.0 ** -c, np.nonzero(ok)[0]))
        return rows


# ------------------------------------------------------------------- self-test
def selftest(verbose=True):
    rng = np.random.default_rng(20260913)
    fails = []

    # 1. round trip for every rule / alphabet pair
    for rule in RULES:
        for pta in (A2Z, KRY):
            for cta in (A2Z, KRY):
                pt = "".join(A2Z[i] for i in rng.integers(0, 26, 97))
                key = list(rng.integers(0, 26, 9))
                ct = encrypt(pt, key, rule, pta, cta)
                if decrypt(ct, key, rule, pta, cta) != pt:
                    fails.append(("roundtrip", rule))

    # 2. planted periodic key is recovered by the sweeper at the right period
    sw = Sweeper([("plain", A2Z), ("kryptos", KRY)])
    for p in (3, 7, 11, 13, 17):
        rule = RULES[int(rng.integers(0, 3))]
        pta = [A2Z, KRY][int(rng.integers(0, 2))]
        cta = [A2Z, KRY][int(rng.integers(0, 2))]
        key = list(rng.integers(0, 26, p))
        pt = "".join(A2Z[i] for i in rng.integers(0, 26, 97))
        ct = encrypt(pt, key, rule, pta, cta)
        pos = CRIB_POS
        rows = sw.sweep(pos, "".join(pt[i] for i in pos),
                        "".join(ct[i] for i in pos), [p])
        if rows[0][2] == 0:
            fails.append(("plant-period", p))

    # 3. the sweeper REJECTS a perturbed key
    key = list(rng.integers(0, 26, 9))
    pt = "".join(A2Z[i] for i in rng.integers(0, 26, 97))
    ct = list(encrypt(pt, key, "vigenere", A2Z, A2Z))
    bad = CRIB_POS[5]
    ct[bad] = A2Z[(A2Z.index(ct[bad]) + 7) % 26]
    rows = sw.sweep(CRIB_POS, "".join(pt[i] for i in CRIB_POS),
                    "".join("".join(ct)[i] for i in CRIB_POS), [9])
    if rows[0][2] != 0:
        fails.append(("reject-perturbed", rows[0][2]))

    # 4. crib_agreement returns 24/24 on a planted explicit key stream
    cb = Combos([("plain", A2Z), ("kryptos", KRY)])
    keytext = "".join(A2Z[i] for i in rng.integers(0, 26, 97))
    kvals = [A2Z.index(c) for c in keytext]
    pt = list("".join(A2Z[i] for i in rng.integers(0, 26, 97)))
    for i, ch in CRIB.items():
        pt[i] = ch
    pt = "".join(pt)
    ctp = "".join(A2Z[ct_from(0, A2Z.index(c), kvals[i])] for i, c in enumerate(pt))
    ag = crib_agreement(keytext, cb, ct=ctp)
    if ag.max() != 24:
        fails.append(("crib_agreement", int(ag.max())))

    # 5. K1 re-encryption under the real system
    import runningkey_lib as RKL
    k1 = encrypt(RKL.K1_PT, [KRY.index(c) for c in "PALIMPSEST"],
                 "vigenere", KRY, KRY)
    if k1 != RKL.K1_CT:
        fails.append(("K1", k1[:20]))

    if verbose:
        print("k5_lib selftest:", "PASS" if not fails else "FAIL %r" % (fails,))
    return fails


if __name__ == "__main__":
    selftest()
