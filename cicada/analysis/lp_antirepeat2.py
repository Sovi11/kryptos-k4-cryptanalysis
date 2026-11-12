#!/usr/bin/env python3
"""Follow-ups to lp_antirepeat.py:
  J  regularity of the leak: Poisson thinning vs counter rules ("every k-th collision gets through")
  K  the 86 doublets listed in context; leak by word length and by rune
  L  EM convergence check, and keyed-alphabet extension: c = sigma(p) + k for ANY fixed
     substitution sigma (hill-climbed) and ANY plaintext-independent key distribution
"""
import os, sys, math, collections
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lp_common import IDX, LATIN, relikd_runes, RELIKD_DIR, PUNCT
rng = np.random.default_rng(29)
SEP = "=" * 78
R = relikd_runes(); r = np.array([x["r"] for x in R]); N = len(r)
same = np.array([not x["first"] for x in R]); idx = np.arange(1, N)[same[1:]]
dbl = r[idx] == r[idx - 1]; NP, ND = len(idx), int(dbl.sum())
freq = np.bincount(r, minlength=29) / N; p0 = (freq ** 2).sum()
sec = np.array([x["sec"] for x in R])

print(SEP); print("J. IS THE LEAK RANDOM OR COUNTED?"); print(SEP)
def gaps_of(pos):
    g = np.diff(pos); return g[sec[pos[1:]] == sec[pos[:-1]]]
g_obs = gaps_of(idx[dbl]); cv_obs = g_obs.std() / g_obs.mean()
def sim_counter(k, reps=2000):
    """Would-be doublets occur independently w.p. p0 at each pair; every k-th one (random phase
    per section) is let through. Returns CV of gaps between leaked doublets."""
    out = []
    for _ in range(reps):
        would = idx[rng.random(NP) < p0 * 1.0]
        keep = []
        for s in np.unique(sec[would]):
            w = would[sec[would] == s]; ph = rng.integers(0, k)
            keep.extend(w[(np.arange(len(w)) + ph) % k == 0])
        keep = np.array(sorted(keep))
        if len(keep) > 3:
            g = gaps_of(keep); out.append((g.std() / g.mean(), len(keep)))
    return np.array(out)
print(f"observed: {len(g_obs)} within-section gaps, mean {g_obs.mean():.1f}, CV {cv_obs:.3f}")
for k, label in [(1, "random thinning (Poisson)"), (2, "every 2nd collision leaks"), (3, "every 3rd"),
                 (4, "every 4th"), (5, "every 5th (matches the 0.19 rate)"), (6, "every 6th")]:
    if k == 1:
        out = []
        for _ in range(2000):
            sel = np.sort(rng.choice(NP, ND, replace=False)); g = gaps_of(idx[sel]); out.append((g.std()/g.mean(), ND))
        out = np.array(out)
    else:
        out = sim_counter(k, 1000)
    cv = out[:, 0]
    print(f"{label:36s} CV {cv.mean():.3f} ± {cv.std():.3f}   P(CV <= obs) {(cv <= cv_obs).mean():.3f}"
          f"   leaked doublets {out[:,1].mean():.0f}")

print(SEP); print("K. THE 86 DOUBLETS IN CONTEXT"); print(SEP)
def word_of(i):
    a = i
    while a > 0 and same[a] and not (("•" in R[a]["j"]) or (R[a]["j"] & PUNCT) or "PB" in R[a]["j"]): a -= 1
    b = i
    while b + 1 < N and same[b + 1] and not (("•" in R[b+1]["j"]) or (R[b+1]["j"] & PUNCT) or "PB" in R[b+1]["j"]): b += 1
    return a, b
wl_obs = collections.Counter(); rows = []
for i in idx[dbl]:
    a, b = word_of(i)
    w = "".join(LATIN[v] + ("|" if t == i - 1 else "") for t, v in zip(range(a, b + 1), r[a:b + 1]))
    if a <= i - 1: wl_obs[b - a + 1] += 1
    rows.append(f"sec{R[i]['sec']} line{R[i]['line']:3d} pos{R[i]['pl']:2d}  {LATIN[r[i]]:3s} word {w}")
for k in range(0, len(rows), 2):
    print("   ".join(f"{x:52s}" for x in rows[k:k+2]))
# within-word doublets by word length vs expected (pairs inside words of each length)
wl_pairs = collections.Counter(); i = 0
while i < N:
    a, b = word_of(i); L = b - a + 1; wl_pairs[L] += L - 1; i = b + 1
tot_in = sum(wl_pairs.values()); in_dbl = sum(wl_obs.values())
print("\nwithin-word doublets by word length (obs / expected at LP2's rate):")
print("  " + "  ".join(f"L{L}:{wl_obs[L]}/{in_dbl*wl_pairs[L]/tot_in:.1f}" for L in range(2, 13)))
cnt = np.bincount(r[idx[dbl]], minlength=29)
print("doublets by rune:", " ".join(f"{LATIN[v]}:{cnt[v]}" for v in np.argsort(-cnt) if cnt[v]))
two = [IDX[c] for c in "ᚢᚳᛋᛝᛡ"]
print(f"runes with two Latin forms (U/V, C/K, S/Z, NG/ING, IA/IO): {cnt[two].sum()} of {ND} doublets "
      f"(expected {ND*freq[two].sum()/1:.1f} if proportional to frequency)")

print(SEP); print("L. ADDITIVE-KEY IMPOSSIBILITY: convergence + arbitrary keyed alphabet"); print(SEP)
bi = np.zeros((29, 29))
for word in open(os.path.join(RELIKD_DIR, "baseline-rune-words.txt"), encoding="utf-8").read().split():
    q = [IDX[c] for c in word if c in IDX]
    for a, b in zip(q, q[1:]): bi[a, b] += 1
Pab = bi / bi.sum()
inword = np.array([(len(R[i]["j"]) == 0 or R[i]["j"] == frozenset({"LB"})) for i in idx])
O = np.bincount(((r[idx] - r[idx - 1]) % 29)[inword], minlength=29).astype(float)
A_, B_ = np.meshgrid(np.arange(29), np.arange(29), indexing="ij")
def dist_sigma(sig):
    return np.bincount(((sig[B_] - sig[A_]) % 29).ravel(), weights=Pab.ravel(), minlength=29)
def em(D, O, w=None, iters=2000):
    M = np.array([np.roll(D, x) for x in range(29)])
    w = np.full(29, 1 / 29) if w is None else w
    for _ in range(iters):
        E = w @ M; w = w * (M @ (O / np.maximum(E, 1e-300))) / O.sum()
    E = w @ M
    return 2 * float((O[O > 0] * np.log(O[O > 0] / (O.sum() * E[O > 0]))).sum()), w, E
ident = np.arange(29)
for s in (1, 5):
    for it in (40000, 300000):
        G, w, E = em(dist_sigma((s * ident) % 29), O, iters=it)
        print(f"s={s}: EM {it:6d} iterations  G = {G:.2f}  fitted doublets {E[0]*O.sum():.1f}")
best_overall = (1e9, None)
for restart in range(4):
    sig = rng.permutation(29) if restart else ident.copy()
    G, w, _ = em(dist_sigma(sig), O, iters=3000); cur = G
    for step in range(2500):
        a, b = rng.choice(29, 2, replace=False); t = sig.copy(); t[a], t[b] = t[b], t[a]
        G2, w2, _ = em(dist_sigma(t), O, w=w.copy(), iters=300)
        if G2 < cur:
            sig, cur, w = t, G2, w2
    G, w, E = em(dist_sigma(sig), O, iters=60000)
    print(f"keyed alphabet hill-climb restart {restart}: best G = {G:.1f}, fitted doublets {E[0]*O.sum():.0f}")
    if G < best_overall[0]: best_overall = (G, sig.copy(), E)
G, sig, E = best_overall
boot = [em(dist_sigma(sig), rng.multinomial(int(O.sum()), E / E.sum()).astype(float), iters=4000)[0] for _ in range(200)]
print(f"best keyed alphabet: G = {G:.1f}; bootstrap under that fitted model mean {np.mean(boot):.1f}, "
      f"max {np.max(boot):.1f}  ->  P < 1/200")

print(SEP); print("M. WHERE IN THE WORD DO DOUBLETS SIT?  (LP2 vs English plaintext doublets)"); print(SEP)
def pos_class(i):
    """class of within-word pair (i-1, i)"""
    a, b = word_of(i)
    if b - a + 1 == 2: return "whole 2-rune word"
    if i - 1 == a: return "word-initial pair"
    if i == b: return "word-final pair"
    return "medial pair"
inw = [i for i in idx if (len(R[i]["j"]) == 0 or R[i]["j"] == frozenset({"LB"}))]
base = collections.Counter(pos_class(i) for i in inw)
obs = collections.Counter(pos_class(i) for i in inw if r[i] == r[i - 1])
eng_all, eng_d = collections.Counter(), collections.Counter()
for word in open(os.path.join(RELIKD_DIR, "baseline-rune-words.txt"), encoding="utf-8").read().split()[:400000]:
    q = [IDX[c] for c in word if c in IDX]; L = len(q)
    for k in range(1, L):
        c_ = "whole 2-rune word" if L == 2 else "word-initial pair" if k == 1 else "word-final pair" if k == L - 1 else "medial pair"
        eng_all[c_] += 1
        if q[k] == q[k - 1]: eng_d[c_] += 1
n_obs = sum(obs.values()); n_base = sum(base.values()); n_ed = sum(eng_d.values())
print(f"{'class':20s} {'LP2 dbl':>8s} {'LP2 exp(base)':>14s} {'English pt doublets':>20s}")
for c_ in ["word-initial pair", "medial pair", "word-final pair", "whole 2-rune word"]:
    print(f"{c_:20s} {obs[c_]:8d} {n_obs*base[c_]/n_base:14.1f} {100*eng_d[c_]/n_ed:18.1f} %")
ini = obs["word-initial pair"] + obs["whole 2-rune word"]
f_eng = (eng_d["word-initial pair"] + eng_d["whole 2-rune word"]) / n_ed
from math import comb
pv = sum(comb(n_obs, t) * f_eng ** t * (1 - f_eng) ** (n_obs - t) for t in range(ini, n_obs + 1))
print(f"word-initial doublets: {ini} of {n_obs}; if cipher doublets mirrored English plaintext doublets: "
      f"expected {n_obs*f_eng:.1f}, P(>= {ini}) = {pv:.1e}")
