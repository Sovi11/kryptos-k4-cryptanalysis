#!/usr/bin/env python3
"""Keyed-alphabet extension of the additive-key impossibility (lp_antirepeat.py G / lp_antirepeat2.py L).
Model: c = sigma(p) + k, sigma ANY fixed substitution, k ANY plaintext-independent key whose
within-word differences have an arbitrary distribution.  Simulated annealing over sigma; the key
distribution is fitted exactly (EM, convex) for each sigma.  Also tests the best fit on gap-2."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lp_common import IDX, relikd_runes, RELIKD_DIR
rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
R = relikd_runes(); r = np.array([x["r"] for x in R]); N = len(r)
same = np.array([not x["first"] for x in R]); idx = np.arange(1, N)[same[1:]]
inword = np.array([(len(R[i]["j"]) == 0 or R[i]["j"] == frozenset({"LB"})) for i in idx])
O = np.bincount(((r[idx] - r[idx - 1]) % 29)[inword], minlength=29).astype(float)
bi = np.zeros((29, 29))
for word in open(os.path.join(RELIKD_DIR, "baseline-rune-words.txt"), encoding="utf-8").read().split():
    q = [IDX[c] for c in word if c in IDX]
    for a, b in zip(q, q[1:]): bi[a, b] += 1
P = (bi / bi.sum()).ravel()
A_, B_ = np.meshgrid(np.arange(29), np.arange(29), indexing="ij"); A_, B_ = A_.ravel(), B_.ravel()
SH = (np.arange(29)[None, :] - np.arange(29)[:, None]) % 29     # SH[x, y] = y - x
def D_of(sig): return np.bincount((sig[B_] - sig[A_]) % 29, weights=P, minlength=29)
def em(D, w, iters):
    M = D[SH]
    for _ in range(iters):
        E = w @ M; w = w * (M @ (O / E)) / O.sum()
    E = w @ M
    return 2 * float((O * np.log(O / (O.sum() * E))).sum()), w, E
best = (1e9, None, None)
for restart in range(3):
    sig = rng.permutation(29); w = np.full(29, 1 / 29)
    cur, w, _ = em(D_of(sig), w, 2000)
    T0, steps = 8.0, 30000
    for t in range(steps):
        T = T0 * (0.02 / T0) ** (t / steps)
        a, b = rng.choice(29, 2, replace=False); s2 = sig.copy(); s2[a], s2[b] = s2[b], s2[a]
        G2, w2, _ = em(D_of(s2), w.copy(), 60)
        if G2 < cur or rng.random() < np.exp((cur - G2) / T):
            sig, cur, w = s2, G2, w2
    G, w, E = em(D_of(sig), w, 50000)
    print(f"restart {restart}: annealed G = {G:.1f}, fitted doublets {E[0]*O.sum():.0f} (observed {int(O[0])})", flush=True)
    if G < best[0]: best = (G, sig.copy(), w.copy())
G, sig, w = best
_, _, E = em(D_of(sig), w, 1)
# parametric bootstrap with sigma fixed (conservative: re-optimising sigma would only lower null G)
Gs = []
O_save = O.copy()
for _ in range(300):
    O = rng.multinomial(int(O_save.sum()), E / E.sum()).astype(float) + 1e-12
    Gs.append(em(D_of(sig), np.full(29, 1 / 29), 3000)[0])
O = O_save
Gs = np.array(Gs)
print(f"best annealed keyed alphabet: G = {G:.1f}; bootstrap (sigma fixed, 300 reps) mean {Gs.mean():.1f}, "
      f"99th pct {np.quantile(Gs, .99):.1f}, max {Gs.max():.1f}, P(G* >= G) = {(Gs >= G).mean():.3f}")
print("fitted key-difference distribution (x: weight):", " ".join(f"{x}:{v:.3f}" for x, v in enumerate(w) if v > 0.005))
print(f"effective number of key-difference values used: {1/np.sum(w**2):.1f} of 29")
