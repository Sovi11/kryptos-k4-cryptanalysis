"""(a) Segment statistics for K4.

Split the 97 letters at every plausible boundary and ask, with a proper null
distribution, whether any segment differs from the others more than chance allows.
Also ask why the global IoC (0.0361) sits BELOW the uniform-random value 1/26.

Outputs a text report to stdout; JSON summary to findings/seg_a_results.json.
"""
import itertools, json, math, os
from collections import Counter

import numpy as np

import seg_common as S

rng = np.random.default_rng(20260912)
NPERM = 200_000

CT = S.CT
N = len(CT)
CODE = S.CT_CODE
CNT = np.bincount(CODE, minlength=26)


def counts(sub):
    return np.bincount(S.codes(sub), minlength=26)


def ioc_counts(c):
    n = c.sum()
    if n < 2:
        return float("nan")
    return float((c * (c - 1)).sum() / (n * (n - 1)))


def gstat(seg_counts):
    """Likelihood-ratio (G) statistic for homogeneity of a segments x 26 table."""
    obs = np.asarray(seg_counts, dtype=float)          # (k, 26)
    row = obs.sum(axis=1, keepdims=True)
    col = obs.sum(axis=0, keepdims=True)
    tot = obs.sum()
    exp = row * col / tot
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.where(obs > 0, obs * np.log(obs / exp), 0.0)
    return float(2 * t.sum())


# ----------------------------------------------------------------- segmentations
def cuts_to_segs(cuts):
    b = [0] + list(cuts) + [N]
    return [(b[i], b[i + 1]) for i in range(len(b) - 1)]


SEGMENTATIONS = {
    "panel rows 4/31/31/31":          cuts_to_segs([4, 35, 66]),
    "crib blocks (5 parts)":          cuts_to_segs([21, 34, 63, 74]),
    "halves 48/49":                   cuts_to_segs([48]),
    "halves 49/48":                   cuts_to_segs([49]),
    "thirds 32/33/32":                cuts_to_segs([32, 65]),
    "quarters 24/24/24/25":           cuts_to_segs([24, 48, 72]),
    "OBKR vs rest 4/93":              cuts_to_segs([4]),
    "before/after the two X (7,79)":  cuts_to_segs([6, 78]),
    "pre-crib / cribbed span / post": cuts_to_segs([21, 74]),
    "doubled-letter blocks":          cuts_to_segs([18, 25, 32, 42, 46, 67]),
    "K3-style rows of 7 (lag-7)":     cuts_to_segs(list(range(7, 97, 7))),
}


def describe(name, segs):
    rows = []
    for (a, b) in segs:
        sub = CT[a:b]
        c = counts(sub)
        rows.append(dict(start=a + 1, end=b, n=b - a, text=sub,
                         ioc=ioc_counts(c),
                         chi2_eng=S.chi2_english(sub),
                         chi2_unif=S.chi2_uniform(sub),
                         distinct=int((c > 0).sum())))
    return rows


def perm_test_homogeneity(segs, nperm=NPERM):
    """Null: the 97 letters are a fixed multiset in random order.  Statistic: G."""
    sizes = [b - a for a, b in segs]
    obs_counts = [counts(CT[a:b]) for a, b in segs]
    obs = gstat(obs_counts)
    pool = CODE.copy()
    k = len(sizes)
    bounds = np.cumsum([0] + sizes)
    null = np.empty(nperm)
    # vectorised: permute once per trial
    for t in range(nperm):
        p = rng.permutation(pool)
        tab = np.empty((k, 26))
        for i in range(k):
            tab[i] = np.bincount(p[bounds[i]:bounds[i + 1]], minlength=26)
        null[t] = gstat(tab)
    pval = float((null >= obs).mean())
    return obs, float(null.mean()), float(null.std()), pval


def perm_test_fast(segs, nperm=NPERM):
    """Same as perm_test_homogeneity but vectorised over trials."""
    sizes = np.array([b - a for a, b in segs])
    k = len(sizes)
    bounds = np.cumsum(np.concatenate([[0], sizes]))
    obs = gstat([counts(CT[a:b]) for a, b in segs])
    # generate nperm permutations of the pooled codes
    B = 2000
    null = np.empty(nperm)
    done = 0
    col = CNT.astype(float)[None, :]
    while done < nperm:
        m = min(B, nperm - done)
        perms = np.argsort(rng.random((m, N)), axis=1)
        vals = CODE[perms]                                  # (m, N)
        tab = np.empty((m, k, 26))
        for i in range(k):
            seg = vals[:, bounds[i]:bounds[i + 1]]
            tab[:, i, :] = (seg[:, :, None] == np.arange(26)[None, None, :]).sum(axis=1)
        row = tab.sum(axis=2, keepdims=True)
        colm = tab.sum(axis=1, keepdims=True)
        exp = row * colm / N
        with np.errstate(divide="ignore", invalid="ignore"):
            t = np.where(tab > 0, tab * np.log(tab / exp), 0.0)
        null[done:done + m] = 2 * t.sum(axis=(1, 2))
        done += m
    return obs, float(null.mean()), float(null.std()), float((null >= obs).mean())


def main():
    out = {}
    print("=" * 78)
    print("(a) SEGMENT STATISTICS FOR K4")
    print("=" * 78)
    print(f"ciphertext ({N} letters): {CT}")
    print()

    # ---------------------------------------------------------------- global
    print("-" * 78)
    print("A0. Global composition and the sub-uniform IoC")
    print("-" * 78)
    freq = ", ".join(f"{S.PLAIN[i]}:{CNT[i]}" for i in range(26))
    print("counts:", freq)
    print(f"distinct letters: {(CNT > 0).sum()}/26   min {CNT.min()}  max {CNT.max()}")
    g_ioc = ioc_counts(CNT)
    print(f"IoC = {g_ioc:.5f}   (E[IoC] for i.i.d. uniform = 1/26 = {1/26:.5f}; English 0.066)")
    chi_u = S.chi2_uniform(CT)
    chi_e = S.chi2_english(CT)
    print(f"chi2 vs uniform = {chi_u:.2f} (df 25; E=25, 5th pct 14.6, 95th pct 37.7)")
    print(f"chi2 vs English = {chi_e:.2f}")

    # null for "too flat": iid uniform multinomial, 97 draws
    M = 500_000
    draws = rng.integers(0, 26, size=(M, N))
    cnts = np.zeros((M, 26), dtype=np.int32)
    for v in range(26):
        cnts[:, v] = (draws == v).sum(axis=1)
    iocs = (cnts * (cnts - 1)).sum(axis=1) / (N * (N - 1))
    chis = ((cnts - N / 26) ** 2 / (N / 26)).sum(axis=1)
    p_flat = float((iocs <= g_ioc).mean())
    print(f"\nP(IoC <= {g_ioc:.5f}) under i.i.d. uniform, n=97, {M} trials: {p_flat:.4f}")
    print(f"   null IoC mean {iocs.mean():.5f} sd {iocs.std():.5f}; "
          f"1st pct {np.percentile(iocs,1):.5f}, 5th pct {np.percentile(iocs,5):.5f}")
    print(f"P(chi2_unif <= {chi_u:.2f}): {float((chis <= chi_u).mean()):.4f}")
    print("  -> The sub-uniform IoC is NOT anomalous: a flat 97-letter sample lands there routinely.")
    out["global"] = dict(ioc=g_ioc, chi2_unif=chi_u, chi2_eng=chi_e, p_ioc_flat=p_flat,
                         counts={S.PLAIN[i]: int(CNT[i]) for i in range(26)})
    del draws, cnts, iocs, chis

    # ---------------------------------------------------------------- segments
    seg_results = {}
    for name, segs in SEGMENTATIONS.items():
        print()
        print("-" * 78)
        print(f"A1. segmentation: {name}")
        print("-" * 78)
        rows = describe(name, segs)
        print(f"{'span':>10} {'n':>4} {'IoC':>8} {'chi2E':>8} {'chi2U':>8} {'dist':>5}  text")
        for r in rows:
            print(f"{r['start']:>4}-{r['end']:<5} {r['n']:>4} {r['ioc']:>8.4f} "
                  f"{r['chi2_eng']:>8.1f} {r['chi2_unif']:>8.1f} {r['distinct']:>5}  {r['text']}")
        obs, mu, sd, p = perm_test_fast(segs, NPERM)
        z = (obs - mu) / sd if sd else float("nan")
        print(f"homogeneity G = {obs:.2f};  permutation null mean {mu:.2f} sd {sd:.2f}; "
              f"z = {z:+.2f};  p = {p:.4f}  ({NPERM} permutations)")
        seg_results[name] = dict(rows=[{k: v for k, v in r.items()} for r in rows],
                                 G=obs, null_mean=mu, null_sd=sd, z=z, p=p)
    out["segmentations"] = seg_results

    # ------------------------------------------------------- changepoint scan
    print()
    print("-" * 78)
    print("A2. single-changepoint scan (every split point 5..92), statistic = G")
    print("-" * 78)
    pts = list(range(5, N - 4))
    obsG = []
    for c in pts:
        obsG.append(gstat([counts(CT[:c]), counts(CT[c:])]))
    obsG = np.array(obsG)
    best = int(np.argmax(obsG))
    print(f"max G = {obsG[best]:.2f} at split after position {pts[best]} "
          f"(1-indexed: {CT[:pts[best]]} | {CT[pts[best]:]})")
    # null distribution of the MAX over all split points
    M2 = 20_000
    nullmax = np.empty(M2)
    for t in range(M2):
        v = rng.permutation(CODE)
        cum = np.zeros((N + 1, 26))
        np.add.at(cum, (np.arange(1, N + 1), v), 1)
        cum = np.cumsum(cum, axis=0)
        tot = cum[N]
        g = np.empty(len(pts))
        for j, c in enumerate(pts):
            a = cum[c]; b = tot - a
            tab = np.vstack([a, b])
            g[j] = gstat(tab)
        nullmax[t] = g.max()
    p_max = float((nullmax >= obsG[best]).mean())
    print(f"null (permutation) max-G: mean {nullmax.mean():.2f} sd {nullmax.std():.2f}, "
          f"95th pct {np.percentile(nullmax,95):.2f}")
    print(f"family-wise p for the best split = {p_max:.4f}  ({M2} permutations)")
    top = np.argsort(-obsG)[:8]
    print("top 8 split points (position, G):", ", ".join(f"{pts[i]}:{obsG[i]:.1f}" for i in top))
    out["changepoint"] = dict(best_split=pts[best], best_G=float(obsG[best]), p_familywise=p_max,
                              null_mean=float(nullmax.mean()), null_sd=float(nullmax.std()))

    # ------------------------------------------- within/between coincidences
    print()
    print("-" * 78)
    print("A3. where do the coincidences live?  (panel rows and crib blocks)")
    print("-" * 78)
    for name in ("panel rows 4/31/31/31", "crib blocks (5 parts)"):
        segs = SEGMENTATIONS[name]
        cs = [counts(CT[a:b]) for a, b in segs]
        tot_pairs = N * (N - 1) / 2
        within = sum((c * (c - 1)).sum() / 2 for c in cs)
        wpairs = sum(c.sum() * (c.sum() - 1) / 2 for c in cs)
        cross = (CNT * (CNT - 1)).sum() / 2 - within
        cpairs = tot_pairs - wpairs
        print(f"{name}: within-segment coincidence rate {within/wpairs:.5f} "
              f"({int(within)}/{int(wpairs)}), cross-segment {cross/cpairs:.5f} "
              f"({int(cross)}/{int(cpairs)})")
        # pairwise mutual IoC
        k = len(cs)
        print("   pairwise mutual IoC (kappa):")
        for i in range(k):
            line = []
            for j in range(k):
                if i == j:
                    line.append(f"{ioc_counts(cs[i]):.4f}*")
                else:
                    mic = float((cs[i] * cs[j]).sum() / (cs[i].sum() * cs[j].sum()))
                    line.append(f"{mic:.4f} ")
            print("     " + " ".join(line))

    # ------------------------------------------------- periodic IoC per segment
    print()
    print("-" * 78)
    print("A4. periodic (decimation) IoC: average coset IoC for period p, per segment")
    print("-" * 78)
    def periodic_ioc(sub, p):
        num = den = 0
        for r in range(p):
            c = counts(sub[r::p])
            n = c.sum()
            if n >= 2:
                num += (c * (c - 1)).sum(); den += n * (n - 1)
        return num / den if den else float("nan")
    targets = [("whole", CT)] + [(f"row{i+1}", CT[a:b]) for i, (a, b) in
                                 enumerate(SEGMENTATIONS["panel rows 4/31/31/31"])] \
              + [("half1", CT[:48]), ("half2", CT[48:])]
    print(f"{'segment':>8} " + " ".join(f"{p:>6}" for p in range(1, 16)))
    for nm, sub in targets:
        if len(sub) < 8:
            continue
        print(f"{nm:>8} " + " ".join(f"{periodic_ioc(sub,p):6.3f}" for p in range(1, 16)))
    print("(English ~0.066, uniform-random 1/26=0.038.  A true period p shows a spike at p and "
          "its multiples.)")

    with open(os.path.join(S.FINDINGS, "seg_a_results.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("\nwrote findings/seg_a_results.json")


if __name__ == "__main__":
    main()
