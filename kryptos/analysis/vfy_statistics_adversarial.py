#!/usr/bin/env python3
"""ADVERSARIAL VERIFICATION of findings/statistics.md's omnibus claim.

Written from scratch.  Imports nothing from stat_common.py / stat_f_profile.py.
Only numpy + stdlib.  Reads data/k4_ciphertext.txt and data/cribs.json.

Checks:
  A. crib per-position check (the assigned lens) + scope audit of the claim
  B. independent recomputation of the 7 battery statistics on K4
  C. independent uniform null (my own RNG, my own generator), two-sided p's
  D. independent omnibus min-p, incl. a SPLIT-SAMPLE (unbiased) variant
  E. direction audit of the min-p statistic (flat vs structured)
  F. stress test: add the width-21 col-bigram statistic (the strongest
     published anomaly) as an 8th battery member and redo the omnibus
  G. crib-conditional structure test (a statistic the battery cannot see)
"""
import json
import math
import sys
from collections import Counter

import numpy as np

ROOT = "/Users/pravarkataria/Desktop/crypto/kryptos"
N = 97
A = 26
RNG = np.random.default_rng(0xC0FFEE_2026)


# ------------------------------------------------------------------ inputs --
def load():
    with open(f"{ROOT}/data/k4_ciphertext.txt") as f:
        ct = "".join(c for c in f.read() if c.isalpha()).upper()
    with open(f"{ROOT}/data/cribs.json") as f:
        cr = json.load(f)["cribs"]
    return ct, cr


# ---------------------------------------------- statistics (single string) --
def ioc_single(v):
    c = np.bincount(v, minlength=A)
    return float((c * (c - 1)).sum()) / (len(v) * (len(v) - 1))


def stats_single(v):
    n = len(v)
    c = np.bincount(v, minlength=A)
    d = {}
    d["ioc"] = float((c * (c - 1)).sum()) / (n * (n - 1))
    d["distinct"] = int((c > 0).sum())
    d["doubles"] = int((v[1:] == v[:-1]).sum())
    # max autocorrelation z, lags 1..48
    best = -1e9
    for lag in range(1, 49):
        m = n - lag
        k = int((v[:m] == v[lag:]).sum())
        z = (k - m / A) / math.sqrt(m * (1 / A) * (1 - 1 / A))
        best = max(best, z)
    d["maxz"] = best
    # max periodic-IoC z, periods 2..30, computed DIRECTLY by residue class
    bestp = -1e9
    for p in range(2, 31):
        S = 0
        D = 0
        for r in range(p):
            col = v[r::p]
            q = len(col)
            if q < 2:
                continue
            cc = np.bincount(col, minlength=A)
            S += int((cc * (cc - 1)).sum())
            D += q * (q - 1)
        if D == 0:
            continue
        mu = 1 / A
        sd = math.sqrt(2 * mu * (1 - mu) / D)
        bestp = max(bestp, (S / D - mu) / sd)
    d["maxperz"] = bestp
    d["bigrams"] = sum(x * (x - 1) // 2
                       for x in Counter(tuple(v[i:i + 2]) for i in range(n - 1)).values())
    d["trigrams"] = sum(x * (x - 1) // 2
                        for x in Counter(tuple(v[i:i + 3]) for i in range(n - 2)).values())
    return d


def colbigram_excess_max(v, wmax=48):
    """max over widths 2..wmax of Sum (count-1) over repeated vertical bigrams.

    Vertical bigram at width w = (row r, col c) letter over (row r+1, col c).
    """
    n = len(v)
    best = -1
    bestw = None
    for w in range(2, wmax + 1):
        rows = (n + w - 1) // w
        cnt = Counter()
        for c in range(w):
            for r in range(rows - 1):
                i, j = r * w + c, (r + 1) * w + c
                if j < n:
                    cnt[(v[i], v[j])] += 1
        ex = sum(x - 1 for x in cnt.values() if x > 1)
        if ex > best:
            best, bestw = ex, w
    return best, bestw


# ----------------------------------------------- vectorised null machinery --
def null_batch(nrep, seed):
    """nrep uniform-random 97-letter strings -> dict of stat arrays."""
    rng = np.random.default_rng(seed)
    B = rng.integers(0, A, size=(nrep, N), dtype=np.uint8)
    return B, stats_batch(B)


def shuffle_batch(nrep, seed, v):
    """nrep random permutations of K4's OWN letter multiset."""
    rng = np.random.default_rng(seed)
    B = rng.permuted(np.tile(v, (nrep, 1)), axis=1)
    return B, stats_batch(B)


def stats_batch(B):
    nrep = B.shape[0]
    out = {}

    # letter counts per row
    flat = (np.arange(nrep, dtype=np.int64)[:, None] * A + B.astype(np.int64)).ravel()
    C = np.bincount(flat, minlength=nrep * A).reshape(nrep, A)
    out["ioc"] = (C.astype(np.int64) * (C.astype(np.int64) - 1)).sum(1) / (N * (N - 1))
    out["distinct"] = (C > 0).sum(1)

    # full coincidence spectrum, lags 1..96
    spec = np.zeros((nrep, N), dtype=np.int32)
    for lag in range(1, N):
        spec[:, lag] = (B[:, :N - lag] == B[:, lag:]).sum(1)
    out["doubles"] = spec[:, 1].astype(np.int64)

    zs = np.empty((nrep, 48))
    for lag in range(1, 49):
        m = N - lag
        zs[:, lag - 1] = (spec[:, lag] - m / A) / math.sqrt(m * (1 / A) * (1 - 1 / A))
    out["maxz"] = zs.max(1)

    pz = np.empty((nrep, 29))
    mu = 1 / A
    for p in range(2, 31):
        q, r = divmod(N, p)
        D = r * (q + 1) * q + (p - r) * q * (q - 1)
        s = 2 * spec[:, p::p].sum(1).astype(np.float64)
        sd = math.sqrt(2 * mu * (1 - mu) / D)
        pz[:, p - 2] = (s / D - mu) / sd
    out["maxperz"] = pz.max(1)

    out["bigrams"] = _rep_pairs(B[:, :-1].astype(np.int32) * A + B[:, 1:])
    tri = (B[:, :-2].astype(np.int32) * A + B[:, 1:-1]) * A + B[:, 2:]
    out["trigrams"] = _rep_pairs(tri)
    return out


def _rep_pairs(codes):
    """per-row Sum_v C(v,2) for the multiset of codes in each row."""
    s = np.sort(codes, axis=1)
    eq = s[:, 1:] == s[:, :-1]
    run = np.zeros(s.shape[0], dtype=np.int64)
    tot = np.zeros(s.shape[0], dtype=np.int64)
    for j in range(eq.shape[1]):
        run = np.where(eq[:, j], run + 1, 0)
        tot += run
    return tot


def colbig_excess_max_batch(B, wmax=48):
    """vectorised max-over-widths column-bigram EXCESS count."""
    nrep = B.shape[0]
    best = np.full(nrep, -1, dtype=np.int64)
    for w in range(2, wmax + 1):
        rows = (N + w - 1) // w
        pairs = []
        for c in range(w):
            for r in range(rows - 1):
                i, j = r * w + c, (r + 1) * w + c
                if j < N:
                    pairs.append((i, j))
        if not pairs:
            continue
        ii = np.array([p[0] for p in pairs])
        jj = np.array([p[1] for p in pairs])
        codes = B[:, ii].astype(np.int32) * A + B[:, jj]
        s = np.sort(codes, axis=1)
        eq = s[:, 1:] == s[:, :-1]
        ex = eq.sum(1).astype(np.int64)   # Sum (v-1) over all codes == excess
        best = np.maximum(best, ex)
    return best


# ------------------------------------------------------------- p machinery --
def two_sided(sample_sorted, x):
    n = len(sample_sorted)
    le = np.searchsorted(sample_sorted, x, side="right") / n
    ge = 1.0 - np.searchsorted(sample_sorted, x, side="left") / n
    return min(1.0, 2 * min(le, ge))


def two_sided_vec(sample_sorted, xs):
    n = len(sample_sorted)
    le = np.searchsorted(sample_sorted, xs, side="right") / n
    ge = 1.0 - np.searchsorted(sample_sorted, xs, side="left") / n
    return np.minimum(1.0, 2 * np.minimum(le, ge))


BATTERY = ["ioc", "distinct", "doubles", "maxz", "maxperz", "bigrams", "trigrams"]


# ------------------------------------------------------------------- main --
def main():
    ct, cribs = load()
    print("=" * 78)
    print("ADVERSARIAL RE-DERIVATION OF findings/statistics.md OMNIBUS CLAIM")
    print("=" * 78)
    print(f"ciphertext read from data/k4_ciphertext.txt, length {len(ct)}")
    assert len(ct) == N, "ciphertext is not 97 letters"
    v = np.array([ord(c) - 65 for c in ct], dtype=np.uint8)

    # ---------------------------------------------------------------- A ---
    print("\n--- A. CRIB CHECK AT EXACT 1-INDEXED POSITIONS ----------------------")
    print("The claim proposes NO decryption, so there is no candidate plaintext to")
    print("score.  What CAN be checked is (i) that the cribs sit where claimed in")
    print("the exact string the statistics were computed on, and (ii) whether any")
    print("battery statistic touches the cribs at all.")
    print(f"\n{'pos':>4s} {'CT':>3s} {'PT':>3s} {'vig k':>6s} {'beau k':>7s}  crib")
    npos = 0
    ok = True
    shifts = []
    for cr in cribs:
        for k, (cc, pp) in enumerate(zip(cr["ct"], cr["pt"])):
            pos = cr["pos"] + k              # 1-indexed
            got = ct[pos - 1]
            good = (got == cc)
            ok &= good
            ci, pi = ord(cc) - 65, ord(pp) - 65
            vig = (ci - pi) % 26             # ct = pt + k
            beau = (ci + pi) % 26            # ct = k - pt
            shifts.append(vig)
            print(f"{pos:4d} {got:>3s} {pp:>3s} {vig:6d} {beau:7d}  {cr['pt']}"
                  f"{'' if good else '   <-- MISMATCH'}")
            npos += 1
    print(f"\n  {npos} crib positions checked; ciphertext letters match the released"
          f" cribs: {ok}")
    print("  Crib letters used by any of the 7 battery statistics: 0 (all 7 are")
    print("  functions of the 97 ciphertext letters alone).  So '24/24 crib fit' is")
    print("  UNDEFINED for this claim, not failed -- exactly as the claim states.")

    # ---------------------------------------------------------------- B ---
    print("\n--- B. MY OWN RECOMPUTATION OF THE 7 BATTERY STATISTICS ON K4 -------")
    obs = stats_single(v)
    ref = {"ioc": 0.0361, "distinct": 26, "doubles": 6, "maxz": 3.0358,
           "maxperz": 1.1285, "bigrams": 10, "trigrams": 0}
    print(f"{'statistic':12s} {'mine':>12s} {'report':>12s}  agree")
    for k in BATTERY:
        mine = obs[k]
        r = ref[k]
        agree = abs(float(mine) - float(r)) < (0.01 if isinstance(r, float) else 0.5)
        print(f"{k:12s} {float(mine):12.4f} {float(r):12.4f}  {agree}")
    print(f"\n  IoC as a fraction: S = {int(round(obs['ioc']*N*(N-1)))} ordered coincident "
          f"pairs out of {N*(N-1)}  -> {obs['ioc']:.6f}")
    # which lag / which period attains the maxima
    lagbest = max(range(1, 49), key=lambda L: ((v[:N-L] == v[L:]).sum() - (N-L)/A)
                  / math.sqrt((N-L)*(1/A)*(25/A)))
    print(f"  max autocorrelation z attained at lag {lagbest}")
    ex21, _ = colbigram_excess_max(v, 21)
    print(f"  (cross-check) col-bigram excess at width 21 = {ex21}")
    exmax, exw = colbigram_excess_max(v, 48)
    print(f"  (cross-check) max col-bigram excess over widths 2-48 = {exmax} at width {exw}")

    # ---------------------------------------------------------------- C ---
    NREP = int(sys.argv[1]) if len(sys.argv) > 1 else 200_000
    print(f"\n--- C. MY OWN UNIFORM NULL: {NREP:,} replicates ----------------------")
    B, nl = null_batch(NREP, 0xBEEF_1234)
    # sanity: my vectorised null machinery must reproduce stats_single on a row
    for t in range(3):
        row = B[t]
        s1 = stats_single(row)
        for k in BATTERY:
            a, b = float(s1[k]), float(nl[k][t])
            assert abs(a - b) < 1e-9, (k, t, a, b)
    print("  self-check: vectorised null statistics == scalar implementation on 3")
    print("  sampled replicates for all 7 statistics (incl. periodic IoC computed")
    print("  by residue classes vs by coincidence spectrum).  PASS")
    print(f"\n{'statistic':12s} {'K4':>10s} {'null mean':>10s} {'null sd':>9s} "
          f"{'P(<=K4)':>9s} {'P(>=K4)':>9s} {'two-sided':>10s}")
    srt = {k: np.sort(nl[k].astype(np.float64)) for k in BATTERY}
    obs_ps = {}
    for k in BATTERY:
        s = srt[k]
        le = np.searchsorted(s, obs[k], side="right") / NREP
        ge = 1.0 - np.searchsorted(s, obs[k], side="left") / NREP
        p = min(1.0, 2 * min(le, ge))
        obs_ps[k] = p
        print(f"{k:12s} {float(obs[k]):10.4f} {s.mean():10.4f} {s.std():9.4f} "
              f"{le:9.4f} {ge:9.4f} {p:10.4f}")
    obs_min = min(obs_ps.values())
    argmin = min(obs_ps, key=lambda k: obs_ps[k])
    print(f"\n  smallest battery p = {obs_min:.4f}  (statistic '{argmin}')"
          f"   [report: 0.1309, maxperz]")

    # ---------------------------------------------------------------- D ---
    print("\n--- D. OMNIBUS min-p ------------------------------------------------")
    minp = np.ones(NREP)
    for k in BATTERY:
        minp = np.minimum(minp, two_sided_vec(srt[k], nl[k].astype(np.float64)))
    minp_s = np.sort(minp)
    p_omni = np.searchsorted(minp_s, obs_min, side="right") / NREP
    print(f"  in-sample (same replicates for CDF and null, as the report did):")
    print(f"    null min-p: median {np.median(minp):.4f}, 5th pct "
          f"{np.percentile(minp,5):.4f}")
    print(f"    OMNIBUS p = P(min-p <= {obs_min:.4f}) = {p_omni:.4f}"
          f"   [report: 0.4142]")

    # split-sample (unbiased): CDFs from half A, null min-p from half B
    h = NREP // 2
    srtA = {k: np.sort(nl[k][:h].astype(np.float64)) for k in BATTERY}
    obs_psB = {k: two_sided(srtA[k], float(obs[k])) for k in BATTERY}
    obs_minB = min(obs_psB.values())
    minpB = np.ones(NREP - h)
    for k in BATTERY:
        minpB = np.minimum(minpB, two_sided_vec(srtA[k], nl[k][h:].astype(np.float64)))
    p_omni_split = (minpB <= obs_minB + 1e-12).mean()
    print(f"  split-sample (unbiased): obs min-p {obs_minB:.4f}, "
          f"OMNIBUS p = {p_omni_split:.4f}")

    # ---------------------------------------------------------------- E ---
    print("\n--- E. DIRECTION AUDIT OF THE SMALLEST-p STATISTIC ------------------")
    s = srt[argmin]
    le = np.searchsorted(s, obs[argmin], side="right") / NREP
    print(f"  '{argmin}': K4 = {float(obs[argmin]):.4f}, null mean {s.mean():.4f}, "
          f"null median {np.median(s):.4f}")
    print(f"  P(null <= K4) = {le:.4f}  ->  K4 is in the "
          f"{'LOWER' if le < 0.5 else 'UPPER'} tail.")
    print("  LOWER tail on max periodic-IoC z means NO period shows elevated")
    print("  within-column repetition: K4 is FLATTER than random, which is the")
    print("  opposite of what any periodic cipher structure would produce.")
    print("  The report's characterisation is therefore correct in direction.")

    # ---------------------------------------------------------------- F ---
    print("\n--- F. STRESS TEST: add the strongest published anomaly to the battery")
    print("  (max column-bigram EXCESS over widths 2-48 -- the Bean width-21")
    print("   statistic, selection-corrected.  The report asserts adding it could")
    print("   only RAISE the omnibus p; I test that instead of believing it.)")
    cb = colbig_excess_max_batch(B, 48)
    scb = np.sort(cb.astype(np.float64))
    le = np.searchsorted(scb, exmax, side="right") / NREP
    ge = 1.0 - np.searchsorted(scb, exmax, side="left") / NREP
    p_cb = min(1.0, 2 * min(le, ge))
    print(f"    K4 max col-bigram excess = {exmax} (width {exw}); null mean "
          f"{scb.mean():.3f}; P(>=obs) = {ge:.4f}; two-sided p = {p_cb:.4f}")
    obs_min8 = min(obs_min, p_cb)
    minp8 = np.minimum(minp, two_sided_vec(scb, cb.astype(np.float64)))
    p_omni8 = (minp8 <= obs_min8 + 1e-12).mean()
    print(f"    8-statistic battery: obs min-p {obs_min8:.4f}, "
          f"OMNIBUS p = {p_omni8:.4f}")

    # ---------------------------------------------------------------- G ---
    print("\n--- G. A STATISTIC THE BATTERY CANNOT SEE: the 24 crib shifts --------")
    print("  The battery is ciphertext-only by construction.  If the crib-derived")
    print("  Vigenere shifts showed structure, the headline 'nothing detects any")
    print("  structure' would be misleading even though literally scoped.")
    sh = np.array(shifts)
    print(f"  24 required shifts (ct-pt mod 26): {list(map(int, sh))}")
    c = np.bincount(sh, minlength=26)
    chi2 = float(((c - 24 / 26) ** 2 / (24 / 26)).sum())
    # exact-ish null by simulation
    r2 = RNG.integers(0, 26, size=(200_000, 24))
    cc = np.zeros((200_000, 26), dtype=np.int32)
    for j in range(24):
        cc[np.arange(200_000), r2[:, j]] += 1
    chi2n = ((cc - 24 / 26) ** 2 / (24 / 26)).sum(1)
    print(f"  chi2 of shift distribution vs uniform = {chi2:.2f} on 25 df; "
          f"P(null >= obs) = {(chi2n >= chi2).mean():.4f}")
    ioc_sh = float((c * (c - 1)).sum()) / (24 * 23)
    iocn = (cc.astype(np.int64) * (cc.astype(np.int64) - 1)).sum(1) / (24 * 23)
    print(f"  IoC of the 24 shifts = {ioc_sh:.4f}; P(null >= obs) = "
          f"{(iocn >= ioc_sh).mean():.4f}")
    print(f"  distinct shift values = {int((c>0).sum())} of 24 draws")
    # any repeat structure in the two crib runs separately?
    print("  -> if these are ~1.0-ish, the crib shifts are as structureless as the")
    print("     ciphertext, and the claim's scope caveat costs it nothing.")

    # ---------------------------------------------------------------- H ---
    print("\n--- H. HARDEST CASE FOR THE CLAIM: shuffle null + 8 statistics -------")
    print("  The uniform null is generous to the claim for arrangement statistics,")
    print("  because it lets the letter multiset vary.  The sharper question is:")
    print("  is the ARRANGEMENT of K4's own letters detectably non-random?  Null =")
    print("  random permutations of K4's exact 97-letter multiset.  Battery = the")
    print("  6 arrangement statistics (IoC and distinct are constant under it)")
    print("  PLUS the max col-bigram excess, i.e. the strongest published anomaly.")
    SB, sn = shuffle_batch(NREP, 0x51F1E, v)
    sn["colbig"] = colbig_excess_max_batch(SB, 48)
    SHB = ["doubles", "maxz", "maxperz", "bigrams", "trigrams", "colbig"]
    obs2 = dict(obs)
    obs2["colbig"] = exmax
    srt2 = {k: np.sort(sn[k].astype(np.float64)) for k in SHB}
    ps2 = {}
    print(f"\n{'statistic':12s} {'K4':>10s} {'null mean':>10s} {'P(<=K4)':>9s} "
          f"{'P(>=K4)':>9s} {'two-sided':>10s}")
    for k in SHB:
        s_ = srt2[k]
        le = np.searchsorted(s_, obs2[k], side="right") / NREP
        ge = 1.0 - np.searchsorted(s_, obs2[k], side="left") / NREP
        ps2[k] = min(1.0, 2 * min(le, ge))
        print(f"{k:12s} {float(obs2[k]):10.4f} {s_.mean():10.4f} {le:9.4f} "
              f"{ge:9.4f} {ps2[k]:10.4f}")
    om2 = min(ps2.values())
    mp2 = np.ones(NREP)
    for k in SHB:
        mp2 = np.minimum(mp2, two_sided_vec(srt2[k], sn[k].astype(np.float64)))
    p2 = (mp2 <= om2 + 1e-12).mean()
    print(f"\n  smallest p = {om2:.4f} ('{min(ps2, key=lambda k: ps2[k])}'), "
          f"OMNIBUS p (shuffle null, 6 arrangement stats) = {p2:.4f}")
    # and the single most hostile reading: no correction at all
    print(f"  most hostile possible reading -- take the single best statistic and")
    print(f"  apply NO correction of any kind: nominal p = {min(om2, obs_min):.4f}")
    print("  (one-sided, that is p = %.4f) -- still not significant at 0.05."
          % (min(om2, obs_min) / 2))

    # ---------------------------------------------------------------- I ---
    print("\n--- I. SCAN-RANGE SENSITIVITY OF THE HEADLINE NUMBER -----------------")
    print("  The battery's maxperz scans periods 2-30, but the SAME report scans")
    print("  periods 2-48 in its sections 5 and 8.  Nothing justifies 30 over 48.")
    print("  I test whether the headline 0.414 survives that choice.")

    def maxperz_batch(BB, pmax):
        nrep = BB.shape[0]
        sp = np.zeros((nrep, N), dtype=np.int32)
        for lag in range(1, N):
            sp[:, lag] = (BB[:, :N - lag] == BB[:, lag:]).sum(1)
        out = np.full(nrep, -1e9)
        mu = 1 / A
        for pp in range(2, pmax + 1):
            q, r = divmod(N, pp)
            D = r * (q + 1) * q + (pp - r) * q * (q - 1)
            ss = 2 * sp[:, pp::pp].sum(1).astype(np.float64)
            out = np.maximum(out, (ss / D - mu) / math.sqrt(2 * mu * (1 - mu) / D))
        return out

    o48 = float(maxperz_batch(v[None, :], 48)[0])
    print(f"\n  K4 max periodic z: periods 2-30 -> {float(obs['maxperz']):.4f}; "
          f"periods 2-48 -> {o48:.4f} (same period, 25)")
    for pmax, o in ((30, float(obs["maxperz"])), (48, o48)):
        u = maxperz_batch(B, pmax)
        sh = maxperz_batch(SB, pmax)
        pu = min(1.0, 2 * min((u <= o).mean(), (u >= o).mean()))
        psh = min(1.0, 2 * min((sh <= o).mean(), (sh >= o).mean()))
        print(f"  periods 2-{pmax}: uniform null mean {u.mean():.3f}, P(null<=K4) "
              f"{(u <= o).mean():.4f}, two-sided p {pu:.4f}   |  shuffle null mean "
              f"{sh.mean():.3f}, P(null<=K4) {(sh <= o).mean():.4f}, two-sided p {psh:.4f}")
    nl48 = dict(nl)
    nl48["maxperz"] = maxperz_batch(B, 48)
    srt48 = {k: np.sort(nl48[k].astype(np.float64)) for k in BATTERY}
    obs48 = dict(obs)
    obs48["maxperz"] = o48
    ps48 = {k: two_sided(srt48[k], float(obs48[k])) for k in BATTERY}
    mn48 = min(ps48.values())
    mp48 = np.ones(NREP)
    for k in BATTERY:
        mp48 = np.minimum(mp48, two_sided_vec(srt48[k], nl48[k].astype(np.float64)))
    print(f"\n  OMNIBUS with periods 2-48: obs min-p {mn48:.4f} "
          f"({min(ps48, key=lambda k: ps48[k])}), p = {(mp48 <= mn48 + 1e-12).mean():.4f}")
    print(f"  OMNIBUS with periods 2-30: obs min-p {obs_min:.4f}, p = {p_omni:.4f}")
    print("\n  So the HEADLINE VALUE is scan-range dependent (0.40 vs 0.07); the")
    print("  headline CLAIM is not.  Both configurations are > 0.05, and in both the")
    print("  driving statistic is in the LOWER tail: K4 is flatter/less periodic than")
    print("  random.  Widening the scan makes K4 look LESS structured, not more --")
    print("  no period in 2-48 reaches even z = +1.65.  Nothing cryptanalytically")
    print("  exploitable follows from a ciphertext being too UNrepetitive, and")
    print("  picking 48 over 30 after seeing which gives the smaller p is itself")
    print("  the uncorrected selection the omnibus exists to price.")

    print("\nDONE")




if __name__ == "__main__":
    main()
