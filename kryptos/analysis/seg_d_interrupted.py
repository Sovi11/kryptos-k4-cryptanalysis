"""(d) Interrupted / irregular periodic key: the key stream is periodic but one or
two key letters are inserted or deleted at unknown positions.

This is exactly the failure mode the carved K2 ciphertext exhibits (Sanborn dropped
one letter), and it is the generic symptom of a hand-enciphered text that lost sync.

Models (key of period p, pointer j, key letter = key[j(i) mod p]):

  D0  free desync between the two crib runs: j(i) = i inside run 1 and i + d inside
      run 2, d free.  This subsumes ANY number of insertions/deletions that happen
      outside the two crib runs, which is the overwhelmingly likely case (a slip in
      the long uncribbed stretches 1-21, 35-63, 75-97).
  D1  one insertion (+1) or deletion (-1) at an unknown position b, 1 <= b <= 96.
  D2  two such events at unknown positions b1 <= b2, signs independent.
      D1/D2 also cover events INSIDE a crib run, which D0 cannot.

For each model the crib consistency test is run against 3 families x 17 plaintext
alphabets x 17 ciphertext alphabets = 867 configurations, and the observed survivor
count is printed next to the number a uniformly random key would produce.
Constrained patterns are then re-tested against 208,627 dictionary keyword alphabets.
"""
import time
from collections import Counter, defaultdict

import numpy as np

import seg_common as S
from seg_c_skiprule import (CFG, SHIFTS, partition_of, test_pairs, dict_alpha_idx,
                            dict_survivors)

CT = S.CT
N = 97
CODE = S.CT_CODE
PLAIN = S.PLAIN
CRIB_POS = np.array(S.CRIB_POS)
RUN1 = (21, 34)
RUN2 = (63, 74)


def _verify():
    """Synthetic recovery: encipher with a period-9 key that has ONE inserted key
    letter at position 40, then check that the D1 scan finds b=40 and rejects most
    other (b, p)."""
    rng = np.random.default_rng(11)
    pt = ("THEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGROUNDTOANUNKNOWN"
          "LOCATIONDOESLANGLEYKNOWABOUTTHISTHEYSHOULD")[:97]
    key = rng.integers(0, 26, 9)
    b_true, p_true = 40, 9
    j = np.arange(N) + (np.arange(N) >= b_true)
    ct = S.encrypt(S.codes(pt), key[j % p_true], "vigenere", S.PLAIN, S.KEYED)
    pi = S.idx_map(S.PLAIN)[S.codes("".join(pt[i] for i in S.CRIB_POS))]
    ci = S.idx_map(S.KEYED)[S.codes("".join(ct[i] for i in S.CRIB_POS))]
    sh = (ci - pi) % 26
    hits = []
    for b in range(1, N):
        for eps in (1, -1):
            jj = np.arange(N) + eps * (np.arange(N) >= b)
            for p in range(2, 21):
                _, pairs = partition_of(jj[CRIB_POS] % p)
                if pairs and all(sh[a] == sh[c] for a, c in pairs):
                    hits.append((b, eps, p, len(pairs)))
    best = [h for h in hits if h[3] >= 10]
    assert any(h[2] == p_true and h[1] == 1 and 34 <= h[0] <= 63 for h in best), best[:10]
    return True


def report(model, tests, nconfig=len(CFG)):
    obs = sum(t[2] for t in tests)
    exp = sum(nconfig * 26.0 ** (-t[1]) for t in tests)
    print(f"{model}: {len(tests)} (pattern, period) tests x {nconfig} configs = "
          f"{len(tests)*nconfig:,} configurations")
    print(f"   observed survivors {obs};  expected by chance {exp:.2f}")
    cc = Counter(t[1] for t in tests)
    print("   constraint counts: " + " ".join(f"c={c}:{n}" for c, n in sorted(cc.items())))
    strong = [t for t in tests if t[2] > 0 and t[1] >= 4]
    print(f"   survivors with c >= 4 (chance {nconfig*26.0**-4:.2e}/test): {len(strong)}")
    for t in sorted(strong, key=lambda x: -x[1])[:20]:
        print("      ", t[0], f"c={t[1]} survivors={t[2]}")
    return obs, exp


def decrypt_survivor(jmap, p, cfg_idx):
    fam, pn, cn = CFG[cfg_idx]
    sh = SHIFTS[cfg_idx]
    key = np.full(p, -1, dtype=np.int64)
    for k, pos in enumerate(CRIB_POS):
        key[int(jmap[pos]) % p] = sh[k]
    if (key < 0).any():
        return None, None
    pt = S.decrypt(CODE, key[jmap % p], fam, S.ALPHABETS[pn], S.ALPHABETS[cn])
    return pt, "".join(PLAIN[x] for x in key)


def main():
    t0 = time.time()
    assert _verify()
    print("verification: a synthetic period-9 key with one inserted key letter at")
    print("position 40 is recovered by the D1 scan (correct period and correct gap).  OK\n")
    print("=" * 78)
    print("(d) INTERRUPTED / IRREGULAR PERIODIC KEY")
    print("=" * 78)
    print(f"configurations per test: {len(CFG)} (3 families x 17 pt x 17 ct alphabets)\n")

    all_cands = []

    # ------------------------------------------------------------------ D0
    print("-" * 78)
    print("D0. free desync between the two crib runs (subsumes any number of")
    print("    insertions/deletions occurring outside the crib runs)")
    print("-" * 78)
    tests = []
    for p in range(2, 27):
        for d in range(p):
            j = np.arange(N).copy()
            j[RUN2[0]:] += d
            _, pairs = partition_of(j[CRIB_POS] % p)
            c = len(pairs)
            mask = test_pairs(pairs)
            n = int(mask.sum())
            tests.append((f"p={p} d={d}", c, n))
            if n and c >= 2:
                for ci in np.nonzero(mask)[0]:
                    pt, key = decrypt_survivor(j, p, ci)
                    if pt:
                        all_cands.append((S.quad_score(pt), pt, f"D0 p={p} d={d} c={c}",
                                          CFG[ci], key))
    report("D0", tests)
    best_by_p = {}
    for (lbl, c, n) in tests:
        p = int(lbl.split()[0][2:])
        best_by_p[p] = max(best_by_p.get(p, -1), c)
    print("   max constraints available at each period (adversary picks the best d):")
    print("   " + " ".join(f"{p}:{best_by_p[p]}" for p in sorted(best_by_p)))

    # ------------------------------------------------------------------ D1
    print()
    print("-" * 78)
    print("D1. exactly one inserted (+1) or deleted (-1) key letter at unknown position")
    print("-" * 78)
    uniq = {}
    for b in range(1, N):
        for eps in (1, -1):
            j = np.arange(N) + eps * (np.arange(N) >= b)
            key = tuple(j[CRIB_POS].tolist())
            uniq.setdefault(key, (j, []))[1].append((b, eps))
    print(f"   distinct crib-restricted pointer maps: {len(uniq)} "
          f"(from {2*(N-1)} (b, sign) pairs)")
    tests = []
    for key, (j, srcs) in uniq.items():
        for p in range(2, 21):
            _, pairs = partition_of(j[CRIB_POS] % p)
            c = len(pairs)
            mask = test_pairs(pairs)
            n = int(mask.sum())
            tests.append((f"b in {srcs[0][0]}..{srcs[-1][0]} eps={srcs[0][1]:+d} p={p}", c, n))
            if n and c >= 2:
                for ci in np.nonzero(mask)[0]:
                    pt, k = decrypt_survivor(j, p, ci)
                    if pt:
                        all_cands.append((S.quad_score(pt), pt,
                                          f"D1 b~{srcs[0][0]} eps={srcs[0][1]:+d} p={p} c={c}",
                                          CFG[ci], k))
    report("D1", tests)

    # ------------------------------------------------------------------ D2
    print()
    print("-" * 78)
    print("D2. two inserted/deleted key letters at unknown positions")
    print("-" * 78)
    uniq2 = {}
    ar = np.arange(N)
    for b1 in range(1, N):
        for b2 in range(b1, N):
            for e1 in (1, -1):
                for e2 in (1, -1):
                    j = ar + e1 * (ar >= b1) + e2 * (ar >= b2)
                    k = tuple(j[CRIB_POS].tolist())
                    uniq2.setdefault(k, (j, (b1, e1, b2, e2)))
    print(f"   distinct crib-restricted pointer maps: {len(uniq2)} "
          f"(from {4*(N-1)*N//2:,} (b1,b2,sign,sign) combinations)")
    tests = []
    for k, (j, src) in uniq2.items():
        for p in range(2, 21):
            _, pairs = partition_of(j[CRIB_POS] % p)
            c = len(pairs)
            mask = test_pairs(pairs)
            n = int(mask.sum())
            tests.append((f"b1={src[0]}{src[1]:+d} b2={src[2]}{src[3]:+d} p={p}", c, n))
            if n and c >= 3:
                for ci in np.nonzero(mask)[0]:
                    pt, kk = decrypt_survivor(j, p, ci)
                    if pt:
                        all_cands.append((S.quad_score(pt), pt,
                                          f"D2 {src} p={p} c={c}", CFG[ci], kk))
    report("D2", tests)

    # ------------------------------------------------------------------ decrypts
    print()
    print("-" * 78)
    print("Decryptions of the fully determined survivors")
    print("-" * 78)
    print(f"total fully determined decryptable survivors: {len(all_cands)}")
    if all_cands:
        all_cands.sort(key=lambda x: -x[0])
        print("(uniform-random 97-letter quadgram score -8.23 +- 0.15; English about -4.7;")
        print(" the best of n chance decrypts rises with n, so compare against the null line)")
        n = len(all_cands)
        m = np.random.default_rng(5).integers(0, 26, size=(max(20000, n), 97))
        null = S.quad_scores_batch(m)
        thr = float(np.quantile(null, 0.95 ** (1.0 / max(n, 1))))
        print(f" best-of-{n} chance threshold (95%): {thr:+.3f}")
        for cd in all_cands[:15]:
            star = " ***" if cd[0] > thr else ""
            print(f"  q={cd[0]:+.3f}{star} {cd[2]} {cd[3]} key={cd[4]}")
            print(f"     {cd[1]}")

    # ------------------------------------------------------------------ dict pass
    print()
    print("-" * 78)
    print("Dictionary-alphabet second pass on the constrained D0/D1 patterns")
    print("-" * 78)
    M, alphas, words = dict_alpha_idx()
    pats = {}
    for p in range(2, 27):
        for d in range(p):
            j = np.arange(N).copy(); j[RUN2[0]:] += d
            _, pairs = partition_of(j[CRIB_POS] % p)
            if len(pairs) >= 3:
                pats.setdefault(tuple(sorted(pairs)), f"D0 p={p} d={d}")
    for key, (j, srcs) in uniq.items():
        for p in range(2, 21):
            _, pairs = partition_of(j[CRIB_POS] % p)
            if len(pairs) >= 3:
                pats.setdefault(tuple(sorted(pairs)),
                                f"D1 b~{srcs[0][0]} eps={srcs[0][1]:+d} p={p}")
    print(f"distinct constraint patterns with c >= 3: {len(pats)}")
    tot = 0; texp = 0.0; hits = []
    for pairs, lbl in pats.items():
        c = len(pairs)
        for fam in S.FAMILIES:
            for side in ("pt", "ct"):
                for nm in S.ALPHABET_NAMES:
                    nsv, ex = dict_survivors(list(pairs), fam, side, S.ALPHABETS[nm])
                    tot += nsv
                    texp += len(alphas) * 26.0 ** (-c)
                    if nsv:
                        hits.append((c, lbl, fam, side, nm, nsv, ex))
    print(f"comparisons: {len(pats)*3*2*17*len(alphas):,}")
    print(f"observed survivors {tot};  expected by chance {texp:.2f}")
    for h in sorted(hits, key=lambda x: -x[0])[:20]:
        print(f"   c={h[0]:<2} {h[1]:<24} {h[2]:<12} {h[3]}-fixed={h[4]:<12} "
              f"-> {h[5]} alphabets, e.g. {h[6]}")

    print(f"\n[runtime {time.time()-t0:.1f}s]")


if __name__ == "__main__":
    main()
