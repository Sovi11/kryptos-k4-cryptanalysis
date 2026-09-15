"""(g) The gold-standard null for the E2 forward-simulation sweep.

seg_e's E2 reported that the best out-of-sample quadgram score over 673,297 fully
determined forward simulations was -7.138, against a best-of-N threshold of -7.283
computed from UNIFORM RANDOM 52-letter strings.  That analytic threshold assumes the
673,297 decryptions are independent uniform strings.  They are not: they all come
from the same 97 ciphertext letters, the key of each is fitted to the same 13 crib
letters, and simulations sharing a period or a configuration produce heavily
correlated text.  An analytic best-of-N threshold is therefore not trustworthy here.

The only null that is trustworthy is the identical procedure run on data with no
signal in it.  This script re-runs the complete E2 sweep on synthetic 97-letter
ciphertexts, keeping EVERYTHING else the same - same crib positions, same assumed
crib plaintext, same rules, triggers, periods, offsets, configurations, same scoring
- and records the maximum out-of-sample score each replicate attains.  The real
-7.138 is then placed in that distribution.

Two null flavours are used:
  UNIFORM   the synthetic ciphertext is 97 i.i.d. uniform letters.
  SHUFFLE   the synthetic ciphertext is a random permutation of the real K4 letters,
            so the letter frequencies (and the sub-uniform IoC) are preserved exactly
            and only the ORDER is destroyed.
"""
import sys
import time
from collections import Counter

import numpy as np

import seg_common as S
from seg_e_plaintrig import (CFG, NCFG, DEC, TRIG_SETS, CAUSAL_RULES, PLAIN,
                             run_pointer, N, RUN1, RUN2, PT1, PT2)

CRIB_POS = list(S.CRIB_POS)
CRIB_PT_CODE = np.array([ord(c) - 65 for c in S.CRIB_PT])
CRIB2_CODE = np.array([ord(c) - 65 for c in PT2])
CRIB2_REL = [63 - RUN1[1] + t for t in range(11)]
TRIG_MASKS = {name: np.array([ch in trig for ch in PLAIN]) for name, trig in TRIG_SETS.items()}
CFG_ALL = np.arange(NCFG)

# shift tables per configuration, as functions of the (synthetic) ciphertext
PT_IDX = np.array([S.idx_map(S.ALPHABETS[pn]) for _, pn, _ in CFG])     # (NCFG, 26)
CT_IDX = np.array([S.idx_map(S.ALPHABETS[cn]) for _, _, cn in CFG])     # (NCFG, 26)
FAM = np.array([{"vigenere": 0, "beaufort": 1, "varbeaufort": 2}[f] for f, _, _ in CFG])


def shifts_for(ct_codes):
    """(NCFG, 24) required key values, given a ciphertext, assuming the real cribs."""
    pi = PT_IDX[:, CRIB_PT_CODE]                                 # (NCFG, 24)
    ci = CT_IDX[:, ct_codes[CRIB_POS]]                           # (NCFG, 24)
    out = np.empty_like(pi)
    m0 = FAM == 0; m1 = FAM == 1; m2 = FAM == 2
    out[m0] = ci[m0] - pi[m0]
    out[m1] = ci[m1] + pi[m1]
    out[m2] = pi[m2] - ci[m2]
    return out % 26


def _check_shifts():
    """shifts_for on the real ciphertext must equal seg_common.required_shifts."""
    got = shifts_for(S.CT_CODE)
    for i, (f, pn, cn) in enumerate(CFG):
        want = S.required_shifts(f, S.ALPHABETS[pn], S.ALPHABETS[cn])
        assert (got[i] == want).all(), (f, pn, cn)
    return True


def e2_max(ct_codes, periods=range(2, 14), want_detail=False):
    """Run the complete E2 sweep on `ct_codes`; return (max out-of-sample quadgram
    score, best BERLINCLOCK match count, number of fully determined simulations)."""
    SH = shifts_for(ct_codes)
    ct_run = ct_codes[RUN1[1]:]
    npos = len(ct_run)
    best_q = -np.inf
    best_match = 0
    ndet = 0
    detail = None
    for rule in CAUSAL_RULES:
        for tname in TRIG_SETS:
            trig = TRIG_SETS[tname]
            tmask = TRIG_MASKS[tname]
            for p in periods:
                r1, a1, after, aft_abs = run_pointer(rule, trig, PT1)
                for b1 in range(p):
                    res = np.where(a1, r1 % p, (b1 + r1) % p)
                    keys = np.full((NCFG, p), -1, dtype=np.int64)
                    alive = np.ones(NCFG, dtype=bool)
                    for t in range(13):
                        r = int(res[t])
                        prev = keys[:, r]
                        alive &= ~((prev >= 0) & (prev != SH[:, t]))
                        keys[:, r] = np.where(prev >= 0, prev, SH[:, t])
                    alive &= (keys >= 0).all(axis=1)
                    if not alive.any():
                        continue
                    idx = CFG_ALL[alive]
                    ndet += idx.size
                    j = np.full(idx.size, (after if aft_abs else b1 + after), dtype=np.int64)
                    out = np.empty((idx.size, npos), dtype=np.int64)
                    kk = keys[idx]
                    ar = np.arange(idx.size)
                    for t in range(npos):
                        kv = kk[ar, j % p]
                        pc = DEC[idx, ct_run[t], kv].astype(np.int64)
                        out[:, t] = pc
                        if rule == "RESET_AFTER":
                            j = np.where(tmask[pc], 0, j + 1)
                        elif rule == "HOLD":
                            j = j + np.where(tmask[pc], 0, 1)
                        elif rule == "DOUBLE":
                            j = j + np.where(tmask[pc], 2, 1)
                        else:                                   # ADVANCE_ONLY
                            j = j + np.where(tmask[pc], 1, 0)
                    nm = (out[:, CRIB2_REL] == CRIB2_CODE[None, :]).sum(axis=1)
                    best_match = max(best_match, int(nm.max()))
                    free = np.concatenate([out[:, :63 - RUN1[1]], out[:, 74 - RUN1[1]:]], axis=1)
                    q = S.quad_scores_batch(free)
                    w = int(np.argmax(q))
                    if q[w] > best_q:
                        best_q = float(q[w])
                        if want_detail:
                            detail = (rule, tname, p, b1, CFG[idx[w]],
                                      "".join(PLAIN[x] for x in out[w]))
    return (best_q, best_match, ndet, detail) if want_detail else (best_q, best_match, ndet)


def main():
    t0 = time.time()
    assert _check_shifts()
    print("verification: the vectorised shift table reproduces seg_common.required_shifts")
    print("for all 867 configurations on the real ciphertext.  OK\n")
    print("=" * 78)
    print("(g) GOLD-STANDARD NULL FOR THE E2 FORWARD-SIMULATION SWEEP")
    print("=" * 78)

    real_q, real_m, real_n, det = e2_max(S.CT_CODE, want_detail=True)
    print(f"REAL K4: max out-of-sample quadgram {real_q:+.4f}, best BERLINCLOCK match "
          f"{real_m}/11, fully determined simulations {real_n:,}")
    print(f"         attained by {det[0]} trig={det[1]} p={det[2]} b1={det[3]} {det[4]}")
    print()

    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    for label, gen in (("UNIFORM  ", lambda r: r.integers(0, 26, 97)),
                       ("SHUFFLE  ", lambda r: r.permutation(S.CT_CODE))):
        qs = []; ms = []; ns = []
        for rep in range(reps):
            rng = np.random.default_rng(5000 + rep + (0 if label.startswith("U") else 777))
            q, m, n = e2_max(gen(rng))
            qs.append(q); ms.append(m); ns.append(n)
            print(f"  {label} rep {rep + 1:>2}/{reps}: max q {q:+.4f}  best match {m}/11  "
                  f"determined {n:,}   [{time.time() - t0:.0f}s]")
        qs = np.array(qs)
        above = int((qs >= real_q).sum())
        print(f"  {label} null over {reps} replicates: mean {qs.mean():+.4f} "
              f"sd {qs.std(ddof=1):.4f}  min {qs.min():+.4f}  max {qs.max():+.4f}")
        print(f"  {label} replicates whose max q reached or beat the real {real_q:+.4f}: "
              f"{above}/{reps}   -> p = {(above + 1) / (reps + 1):.3f}")
        print(f"  {label} best BERLINCLOCK match across replicates: {max(ms)}/11 "
              f"(real {real_m}/11)")
        print()

    print("Reading: if the real K4 maximum sits inside the null cloud, the E2 sweep found")
    print("nothing - the analytic best-of-N threshold quoted in seg_e was simply the")
    print("wrong threshold, because the 673,297 simulations are not independent.")
    print(f"\n[runtime {time.time() - t0:.1f}s]")


if __name__ == "__main__":
    main()
