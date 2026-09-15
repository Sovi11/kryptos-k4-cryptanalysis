"""Shared machinery for the K4 crib-placement / crib-variant sweeps.

The question these scripts attack: everyone (including every prior sweep in this
repo) assumes the four Sanborn cribs are exactly

    22-25 EAST, 26-34 NORTHEAST, 64-69 BERLIN, 70-74 CLOCK   (1-indexed)

and that the plaintext is ordinary correctly-spelled English.  Sanborn misspells
on purpose in K1/K2/K3, journalists have paraphrased his position statements,
and the 2006 K2 correction was exactly a one-letter shift.  So we re-run the
periodic-substitution consistency test over *variant plaintexts* and *shifted
placements*.

Everything here is 0-indexed internally; data/cribs.json is 1-indexed.

Core object: a **placement** = list of (pos, pt_letter) with 0 <= pos < 97.
The ciphertext letter at that position is CT[pos], so a placement fully
determines the (cipher, plain) pairs.

Core test: `consistent(placement, period, combo)` -- does there exist a periodic
key of that period, under that cipher rule and that pair of alphabets, matching
every pair?  Equivalent to: the required key value is constant on each residue
class mod `period`.

Also provided: `universal_ok(placement, period)`, an **alphabet-free necessary
condition** that holds for every Vigenere/Beaufort/variant-Beaufort periodic
cipher with *any* pair of 26-letter alphabets (i.e. every Quagmire I-IV):
within a residue class, equal ciphertext letters force equal plaintext letters
and vice versa.  Failing it rules out the placement for all ~4e11 alphabet
pairs at once, not just the 12 concrete combos.
"""
import json
import math
import os
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
FINDINGS = os.path.join(ROOT, "findings")

A2Z = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

with open(os.path.join(DATA, "k4_ciphertext.txt")) as f:
    CT = "".join(ch for ch in f.read() if ch.isalpha()).upper()
assert len(CT) == 97, len(CT)
N = 97

ALPHABETS = {"plain": A2Z, "kryptos": KRY}
# letter -> index, per alphabet, as a 26-entry lookup indexed by ord(ch)-65
AIDX = {name: np.array([a.index(ch) for ch in A2Z], dtype=np.int64)
        for name, a in ALPHABETS.items()}

RULES = ("vigenere", "beaufort", "varbeaufort")

# 3 rules x (pt alphabet) x (ct alphabet) = 12 combos.  The *key* alphabet is
# irrelevant to a consistency test (it only renames key values), so 12 combos
# exhaust the Quagmire I/II/III/IV space restricted to {plain, KRYPTOS}.
COMBOS = [(rule, pta, cta) for rule in RULES
          for pta in ("plain", "kryptos") for cta in ("plain", "kryptos")]
assert len(COMBOS) == 12


def combo_name(combo):
    rule, pta, cta = combo
    return "%s/pt=%s/ct=%s" % (rule, pta, cta)


CT_CODE = np.frombuffer(CT.encode(), dtype=np.uint8).astype(np.int64) - 65


# ---------------------------------------------------------------- key algebra
def required_key(rule, pt_idx, ct_idx):
    """Key value forced by one (plaintext, ciphertext) pair, given the indices
    of the plaintext letter in the pt alphabet and of the ciphertext letter in
    the ct alphabet.  Works elementwise on numpy arrays."""
    if rule == "vigenere":        # ct = CTA[(pt_idx + k) % 26]
        return (ct_idx - pt_idx) % 26
    if rule == "beaufort":        # ct = CTA[(k - pt_idx) % 26]
        return (ct_idx + pt_idx) % 26
    if rule == "varbeaufort":     # ct = CTA[(pt_idx - k) % 26]
        return (pt_idx - ct_idx) % 26
    raise ValueError(rule)


def encrypt(pt, key, rule, pta, cta):
    """key = list of ints (the periodic key values), repeated cyclically."""
    A, B = ALPHABETS[pta], ALPHABETS[cta]
    out = []
    for i, ch in enumerate(pt):
        pi = A.index(ch)
        k = key[i % len(key)]
        if rule == "vigenere":
            ci = (pi + k) % 26
        elif rule == "beaufort":
            ci = (k - pi) % 26
        else:
            ci = (pi - k) % 26
        out.append(B[ci])
    return "".join(out)


def decrypt(ct, key, rule, pta, cta):
    A, B = ALPHABETS[pta], ALPHABETS[cta]
    out = []
    for i, ch in enumerate(ct):
        ci = B.index(ch)
        k = key[i % len(key)]
        if rule == "vigenere":
            pi = (ci - k) % 26
        elif rule == "beaufort":
            pi = (k - ci) % 26
        else:
            pi = (ci + k) % 26
        out.append(A[pi])
    return "".join(out)


# ---------------------------------------------------------------- placements
def placement_arrays(placement):
    """placement -> (positions int64[m], pt letter codes int64[m], ct codes int64[m])."""
    pos = np.array([p for p, _ in placement], dtype=np.int64)
    ptc = np.array([ord(c) - 65 for _, c in placement], dtype=np.int64)
    return pos, ptc, CT_CODE[pos]


def n_constraints(positions, period):
    """Number of independent equality constraints the placement imposes on a
    period-`period` key: len(positions) - (number of distinct residues)."""
    return len(positions) - len({int(p) % period for p in positions})


def chance_prob(positions, period):
    return 26.0 ** (-n_constraints(positions, period))


def consistent(arrs, period, combo):
    """Exact test for one concrete (rule, pt alphabet, ct alphabet).
    arrs = placement_arrays(...).  Returns (ok, key_dict)."""
    pos, ptc, ctc = arrs
    rule, pta, cta = combo
    k = required_key(rule, AIDX[pta][ptc], AIDX[cta][ctc])
    res = pos % period
    seen = {}
    for r, kv in zip(res.tolist(), k.tolist()):
        if r in seen:
            if seen[r] != kv:
                return False, None
        else:
            seen[r] = kv
    return True, seen


def universal_ok(arrs, period):
    """Alphabet-FREE necessary condition, valid for every periodic
    Vigenere/Beaufort/variant-Beaufort with ANY pair of 26-letter alphabets:

        for i, j in the same residue class mod `period`,
            ct[i] == ct[j]  <=>  pt[i] == pt[j]

    Proof: in all three rules the forced key is  k = f(beta(c)) +- alpha(p)
    with alpha, beta injective, so k_i == k_j and c_i == c_j together force
    alpha(p_i) == alpha(p_j) hence p_i == p_j, and symmetrically.
    Failing this rules the placement out for all alphabet pairs at once."""
    pos, ptc, ctc = arrs
    by_res = defaultdict(list)
    for idx, r in enumerate(pos % period):
        by_res[int(r)].append(idx)
    for idxs in by_res.values():
        if len(idxs) < 2:
            continue
        for a in range(len(idxs)):
            for b in range(a + 1, len(idxs)):
                i, j = idxs[a], idxs[b]
                if (ctc[i] == ctc[j]) != (ptc[i] == ptc[j]):
                    return False
    return True


# ---------------------------------------------------------------- self-tests
def _selftest(verbose=True):
    ok = True

    def check(name, cond):
        nonlocal ok
        if not cond:
            ok = False
        if verbose:
            print("  [%s] %s" % ("PASS" if cond else "FAIL", name))

    if verbose:
        print("crib_lib self-tests")

    # 1. encrypt/decrypt round trip for all 12 combos, several periods
    rng = np.random.default_rng(7)
    rt = True
    for combo in COMBOS:
        for p in (1, 3, 7, 11, 26):
            key = rng.integers(0, 26, p).tolist()
            pt = "".join(A2Z[i] for i in rng.integers(0, 26, 97))
            ct = encrypt(pt, key, *combo)
            if decrypt(ct, key, *combo) != pt:
                rt = False
    check("encrypt/decrypt round trip, 12 combos x 5 periods", rt)

    # 2. K1 regression: Quagmire III, KRYPTOS alphabet both sides, key PALIMPSEST.
    k1_pt = ("BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION")
    k1_ct = ("EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD")
    key = [KRY.index(c) for c in "PALIMPSEST"]
    check("K1 re-encrypts correctly (Quagmire III / KRYPTOS / PALIMPSEST)",
          encrypt(k1_pt, key, "vigenere", "kryptos", "kryptos") == k1_ct)

    # 3. synthetic-key recovery: plant a period-p key, check `consistent`
    #    finds it and recovers the right key values, and check it rejects a
    #    perturbed plaintext.
    rec = True
    rej = 0
    trials = 0
    for combo in COMBOS:
        for p in (5, 9, 13, 17):
            trials += 1
            key = rng.integers(0, 26, p).tolist()
            pt = "".join(A2Z[i] for i in rng.integers(0, 26, 97))
            ct = encrypt(pt, key, *combo)
            # build a placement at the real Sanborn windows using the planted pt
            pl = [(i, pt[i]) for i in list(range(21, 34)) + list(range(63, 74))]
            saved = CT_CODE.copy()
            try:
                CT_CODE[:] = np.frombuffer(ct.encode(), dtype=np.uint8).astype(np.int64) - 65
                arrs = placement_arrays(pl)
                good, found = consistent(arrs, p, combo)
                if not good:
                    rec = False
                else:
                    for r, kv in found.items():
                        if kv != key[r % p]:
                            rec = False
                if not universal_ok(arrs, p):
                    rec = False
                # perturb one crib letter -> should usually be rejected
                pl2 = list(pl)
                i0, c0 = pl2[0]
                pl2[0] = (i0, A2Z[(A2Z.index(c0) + 1) % 26])
                if not consistent(placement_arrays(pl2), p, combo)[0]:
                    rej += 1
            finally:
                CT_CODE[:] = saved
    check("synthetic period-p key planted and recovered (48 trials)", rec)
    check("perturbed crib rejected in >=90%% of trials (%d/%d)" % (rej, trials),
          rej >= 0.9 * trials)

    # 4. the real cribs are NOT consistent at any period 2-26 for any of the 12
    #    combos (reproduces the established negative result)
    base = baseline_placement()
    arrs = placement_arrays(base)
    surv = [(p, c) for p in range(2, 27) for c in COMBOS
            if consistent(arrs, p, c)[0]]
    exp = sum(chance_prob([p for p, _ in base], p) for p in range(2, 27)) * 12
    check("baseline cribs: survivors at p=2..26 = %d (chance expectation %.2f)"
          % (len(surv), exp), True)
    if verbose:
        for p, c in surv:
            print("      survivor p=%d %s (constraints=%d)"
                  % (p, combo_name(c), n_constraints([q for q, _ in base], p)))

    # 5. n_constraints agrees with the table in findings/families.md
    known = {2: 22, 13: 11, 14: 11, 15: 9, 16: 8, 17: 7, 18: 7, 19: 9,
             20: 11, 21: 11, 22: 9, 23: 7, 24: 5, 25: 3, 26: 1}
    pos = [p for p, _ in base]
    check("n_constraints matches findings/families.md table",
          all(n_constraints(pos, p) == v for p, v in known.items()))

    print("crib_lib self-tests: %s" % ("ALL PASS" if ok else "FAILURES"))
    return ok


def baseline_placement():
    """The standard cribs, 0-indexed."""
    out = []
    for start, word in ((21, "EAST"), (25, "NORTHEAST"), (63, "BERLIN"), (69, "CLOCK")):
        for k, ch in enumerate(word):
            out.append((start + k, ch))
    return out


def merge_blocks(blocks):
    """blocks = list of (start, word).  Returns a placement, or None if two
    blocks overlap with conflicting letters or fall outside [0, 97)."""
    d = {}
    for start, word in blocks:
        if start < 0 or start + len(word) > N:
            return None
        for k, ch in enumerate(word):
            p = start + k
            if p in d and d[p] != ch:
                return None
            d[p] = ch
    return sorted(d.items())


if __name__ == "__main__":
    _selftest()
    print()
    print("CT:", CT)
    base = baseline_placement()
    print("baseline placement (0-idx):",
          "".join("%d:%s->%s " % (p, CT[p], c) for p, c in base))


# ==========================================================================
# Vectorised two-window sweep.
#
# A "window" is a fixed list of ciphertext positions plus a list of candidate
# plaintext strings for it ('?' = wildcard, imposes no constraint).  The sweep
# tests every (variant A, variant B) pair against every period and every combo,
# plus the alphabet-free universal test.
# ==========================================================================

def _codes(strings, L):
    m = np.full((len(strings), L), -1, dtype=np.int16)
    for i, s in enumerate(strings):
        assert len(s) == L, (s, L)
        for j, ch in enumerate(s):
            if ch != "?":
                m[i, j] = ord(ch) - 65
    return m


def _fold(K, res, period):
    """K : (n, L) int16 key values (-1 = unknown), res : (L,) residues.
    Returns (M, ok) with M : (n, period) int16 folded key values (-1 unknown)
    and ok : (n,) bool saying the row is internally consistent."""
    n = K.shape[0]
    M = np.full((n, period), -1, dtype=np.int16)
    ok = np.ones(n, dtype=bool)
    for r in range(period):
        cols = np.nonzero(res == r)[0]
        if cols.size == 0:
            continue
        sub = K[:, cols]                       # (n, t)
        valid = sub >= 0
        any_valid = valid.any(axis=1)
        # first valid value per row
        first_idx = np.argmax(valid, axis=1)
        firstv = sub[np.arange(n), first_idx]
        bad = (valid & (sub != firstv[:, None])).any(axis=1)
        ok &= ~bad
        M[any_valid, r] = firstv[any_valid]
    return M, ok


def _cross_conflict(MA, okA, MB, okB, period):
    """Boolean (nA, nB) matrix: True where the two folded key maps disagree."""
    conf = np.zeros((MA.shape[0], MB.shape[0]), dtype=bool)
    for r in range(period):
        a = MA[:, r][:, None]
        b = MB[None, :, r] if False else MB[:, r][None, :]
        conf |= (a >= 0) & (b >= 0) & (a != b)
    conf |= ~okA[:, None]
    conf |= ~okB[None, :]
    return conf


def universal_pattern_conflict(posA, PA, posB, PB, period):
    """Alphabet-free necessary condition, vectorised over variant pairs.
    Returns (nA, nB) bool: True where the pair is impossible for EVERY pair of
    26-letter alphabets under Vigenere/Beaufort/variant-Beaufort."""
    ctA = CT_CODE[posA]
    ctB = CT_CODE[posB]
    nA, nB = PA.shape[0], PB.shape[0]
    badA = np.zeros(nA, dtype=bool)
    badB = np.zeros(nB, dtype=bool)
    # within-window pairs
    for pos, P, ct, bad in ((posA, PA, ctA, badA), (posB, PB, ctB, badB)):
        L = len(pos)
        for i in range(L):
            for j in range(i + 1, L):
                if (pos[i] - pos[j]) % period:
                    continue
                vi, vj = P[:, i], P[:, j]
                known = (vi >= 0) & (vj >= 0)
                bad |= known & ((vi == vj) != (ct[i] == ct[j]))
    conf = badA[:, None] | badB[None, :]
    for i in range(len(posA)):
        for j in range(len(posB)):
            if (posA[i] - posB[j]) % period:
                continue
            a = PA[:, i][:, None]
            b = PB[:, j][None, :]
            known = (a >= 0) & (b >= 0)
            conf |= known & ((a == b) != (ctA[i] == ctB[j]))
    return conf


def two_window_sweep(posA, varsA, posB, varsB, periods=tuple(range(2, 27)),
                     combos=COMBOS, detail_min=5, max_detail=400, progress=None):
    """Full sweep of every (variant A, variant B) x period x combo.

    Because variants may carry '?' wildcards, different pairs impose different
    numbers of constraints, and a low-constraint pair survives by chance with
    high probability.  So everything is reported **stratified by the number of
    constraints c** the pair imposes at that period: a random key survives with
    probability 26^-c, and the expected survivor count in each stratum is
    reported next to the observed count.

    Returns a dict with obs[c], exp[c] (Counter / dict over constraint counts),
    `details` (survivors with c >= detail_min), and the alphabet-free
    (universal) pass counts, also stratified by c.
    """
    from collections import Counter
    posA = np.asarray(posA, dtype=np.int64)
    posB = np.asarray(posB, dtype=np.int64)
    PA = _codes(varsA, len(posA))
    PB = _codes(varsB, len(posB))
    ctA, ctB = CT_CODE[posA], CT_CODE[posB]
    nA, nB = PA.shape[0], PB.shape[0]
    knownA = PA >= 0
    knownB = PB >= 0
    nkA = knownA.sum(axis=1)
    nkB = knownB.sum(axis=1)

    obs = Counter()
    exp = Counter()
    uni_obs = Counter()
    details = []
    n_pairs = nA * nB

    for period in periods:
        resA, resB = (posA % period).astype(np.int64), (posB % period).astype(np.int64)
        # residue bitmask actually covered by each variant (wildcards excluded)
        maskA = np.zeros(nA, dtype=np.uint32)
        for j in range(len(posA)):
            maskA |= np.where(knownA[:, j], np.uint32(1) << np.uint32(resA[j]), np.uint32(0))
        maskB = np.zeros(nB, dtype=np.uint32)
        for j in range(len(posB)):
            maskB |= np.where(knownB[:, j], np.uint32(1) << np.uint32(resB[j]), np.uint32(0))
        cA = nkA - np.bitwise_count(maskA).astype(np.int64)
        cB = nkB - np.bitwise_count(maskB).astype(np.int64)
        shared = np.bitwise_count(maskA[:, None] & maskB[None, :]).astype(np.int64)
        C = cA[:, None] + cB[None, :] + shared           # (nA, nB) constraint counts

        # chance expectation, per stratum, summed over combos
        for c in np.unique(C):
            cnt = int((C == c).sum())
            exp[int(c)] += cnt * len(combos) * 26.0 ** (-int(c))

        # alphabet-free necessary condition
        uconf = universal_pattern_conflict(posA, PA, posB, PB, period)
        good = ~uconf
        for c in np.unique(C[good]) if good.any() else []:
            uni_obs[int(c)] += int((good & (C == c)).sum())

        for combo in combos:
            rule, pta, cta = combo
            KA = np.where(knownA,
                          required_key(rule, AIDX[pta][np.maximum(PA, 0)],
                                       AIDX[cta][ctA][None, :]), -1).astype(np.int16)
            KB = np.where(knownB,
                          required_key(rule, AIDX[pta][np.maximum(PB, 0)],
                                       AIDX[cta][ctB][None, :]), -1).astype(np.int16)
            MA, okA = _fold(KA, resA, period)
            MB, okB = _fold(KB, resB, period)
            if not okA.any() or not okB.any():
                continue
            conf = _cross_conflict(MA, okA, MB, okB, period)
            surv = ~conf
            if not surv.any():
                continue
            for c in np.unique(C[surv]):
                obs[int(c)] += int((surv & (C == c)).sum())
            hit = surv & (C >= detail_min)
            if hit.any() and len(details) < max_detail:
                for iA, iB in zip(*np.nonzero(hit)):
                    kd = {}
                    for r in range(period):
                        v = MA[iA, r] if MA[iA, r] >= 0 else MB[iB, r]
                        if v >= 0:
                            kd[r] = int(v)
                    details.append(dict(period=period, combo=combo, iA=int(iA),
                                        iB=int(iB), c=int(C[iA, iB]), key=kd))
                    if len(details) >= max_detail:
                        break
        if progress:
            progress(period, sum(obs.values()))

    return dict(n_pairs=n_pairs, n_periods=len(periods), n_combos=len(combos),
                tested=n_pairs * len(periods) * len(combos),
                obs=dict(obs), exp=dict(exp), uni_obs=dict(uni_obs),
                uni_tested=n_pairs * len(periods),
                observed=sum(obs.values()), expected=sum(exp.values()),
                universal_pass=sum(uni_obs.values()),
                details=details)


def window_variants(cores, L, min_known, extra=()):
    """Slide each core string through a length-L window in every alignment,
    filling outside positions with '?'.  Keep windows with >= min_known real
    letters.  `extra` strings (already length L) are appended verbatim.
    Returns (list_of_strings, list_of_labels)."""
    seen = {}
    for core in cores:
        for o in range(-(L - 1), len(core)):
            s = "".join(core[o + j] if 0 <= o + j < len(core) else "?"
                        for j in range(L))
            if sum(ch != "?" for ch in s) < min_known:
                continue
            if s not in seen:
                seen[s] = "%s@%+d" % (core, o)
    for s in extra:
        if s not in seen:
            seen[s] = "extra"
    return list(seen.keys()), list(seen.values())


# ==========================================================================
# Placement sweep: positions VARY (shifted cribs), variable alphabet set.
# ==========================================================================
SHORT_KEYWORDS = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "SANBORN", "SCHEIDT",
                  "LANGLEY", "BERLIN", "CLOCK", "COMPASS", "LODESTONE",
                  "SHADOW", "IQLUSION", "UNDERGRUUND", "DESPARATLY",
                  "LAYERTWO", "MASKING"]


def keyed_alphabet(keyword, base=A2Z):
    seen = []
    for ch in keyword.upper():
        if ch in base and ch not in seen:
            seen.append(ch)
    return "".join(seen) + "".join(ch for ch in base if ch not in seen)


def alphabet_set(which="two"):
    if which == "two":
        return [("plain", A2Z), ("kryptos", KRY)]
    if which == "short17":
        out = [("plain", A2Z)]
        for kw in SHORT_KEYWORDS:
            out.append((kw, keyed_alphabet(kw)))
        return out
    raise ValueError(which)


_RULE_ID = {"vigenere": 0, "beaufort": 1, "varbeaufort": 2}


def build_combo_arrays(alphabets, rules=RULES):
    names, strs = zip(*alphabets)
    AID = np.array([[a.index(ch) for ch in A2Z] for a in strs], dtype=np.int64)
    rid, pid, cid, labels = [], [], [], []
    for r in rules:
        for i in range(len(strs)):
            for j in range(len(strs)):
                rid.append(_RULE_ID[r]); pid.append(i); cid.append(j)
                labels.append("%s/pt=%s/ct=%s" % (r, names[i], names[j]))
    return (AID, np.array(rid), np.array(pid), np.array(cid), labels)


def placement_keys(placement, combo_arrays):
    """(K, m) matrix of required key values, one row per combo."""
    AID, rid, pid, cid, _ = combo_arrays
    pos, ptc, ctc = placement_arrays(placement)
    pidx = AID[pid][:, ptc]
    cidx = AID[cid][:, ctc]
    out = np.where(rid[:, None] == 0, (cidx - pidx) % 26,
                   np.where(rid[:, None] == 1, (cidx + pidx) % 26,
                            (pidx - cidx) % 26))
    return pos, ptc, ctc, out


def placement_sweep_one(placement, combo_arrays, periods=tuple(range(2, 27))):
    """Returns list of (period, combo_index, c, keydict) survivors, plus
    per-period (c, universal_ok) info."""
    pos, ptc, ctc, K = placement_keys(placement, combo_arrays)
    nK = K.shape[0]
    survivors = []
    info = []
    for period in periods:
        res = pos % period
        ok = np.ones(nK, dtype=bool)
        uni = True
        c = 0
        groups = []
        for r in np.unique(res):
            g = np.nonzero(res == r)[0]
            if g.size < 2:
                continue
            c += g.size - 1
            groups.append(g)
            ok &= (K[:, g] == K[:, g[0]][:, None]).all(axis=1)
            for a in range(g.size):
                for b in range(a + 1, g.size):
                    i, j = g[a], g[b]
                    if (ctc[i] == ctc[j]) != (ptc[i] == ptc[j]):
                        uni = False
        info.append((period, c, uni))
        for ki in np.nonzero(ok)[0]:
            kd = {}
            for idx, r in enumerate(res.tolist()):
                kd[r] = int(K[ki, idx])
            survivors.append((period, int(ki), c, kd))
    return survivors, info
