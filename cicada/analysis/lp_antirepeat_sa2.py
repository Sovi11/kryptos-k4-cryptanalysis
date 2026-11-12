#!/usr/bin/env python3
"""Joint gap-1 + gap-2 test of c = sigma(p) + k with a random-walk key: k_i = k_{i-1} + d_i,
d_i i.i.d. from an ARBITRARY distribution w, sigma ANY fixed substitution (annealed).
Gap-1 within-word differences ~ D1_sigma (*) w ; gap-2 ~ D2_sigma (*) (w (*) w).  EM is exact for w."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lp_common import IDX, relikd_runes, RELIKD_DIR
rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 11)
R = relikd_runes(); r = np.array([x["r"] for x in R]); N = len(r)
def inw(i):  # rune i continues the same word as rune i-1
    return (not R[i]["first"]) and (len(R[i]["j"]) == 0 or R[i]["j"] == frozenset({"LB"}))
w1 = np.array([inw(i) for i in range(N)])
i1 = np.where(w1)[0]; i2 = np.array([i for i in range(2, N) if w1[i] and w1[i - 1]])
O1 = np.bincount((r[i1] - r[i1 - 1]) % 29, minlength=29).astype(float)
O2 = np.bincount((r[i2] - r[i2 - 2]) % 29, minlength=29).astype(float)
print(f"LP2 within-word: gap-1 pairs {int(O1.sum())} (repeats {int(O1[0])}), gap-2 pairs {int(O2.sum())} (repeats {int(O2[0])})")
P1 = np.zeros((29, 29)); P2 = np.zeros((29, 29))
for word in open(os.path.join(RELIKD_DIR, "baseline-rune-words.txt"), encoding="utf-8").read().split():
    q = [IDX[c] for c in word if c in IDX]
    for a, b in zip(q, q[1:]): P1[a, b] += 1
    for a, b in zip(q, q[2:]): P2[a, b] += 1
P1 = (P1 / P1.sum()).ravel(); P2 = (P2 / P2.sum()).ravel()
A_, B_ = np.meshgrid(np.arange(29), np.arange(29), indexing="ij"); A_, B_ = A_.ravel(), B_.ravel()
SH = (np.arange(29)[None, :] - np.arange(29)[:, None]) % 29          # SH[x, y] = y - x
S3 = (np.arange(29)[:, None] + np.arange(29)[None, :]) % 29           # S3[d1, d2] = d1 + d2
def Ds(sig):
    d = (sig[B_] - sig[A_]) % 29
    return np.bincount(d, weights=P1, minlength=29), np.bincount(d, weights=P2, minlength=29)
def fit(sig, w, iters, Oa=None, Ob=None):
    Oa = O1 if Oa is None else Oa; Ob = O2 if Ob is None else Ob
    D1, D2 = Ds(sig); M1 = D1[SH]; M2 = D2[SH]
    for _ in range(iters):
        E1 = w @ M1; g1 = M1 @ (Oa / E1)                        # g1[x] = sum_y O1 D1(y-x)/E1
        ww = np.bincount(S3.ravel(), weights=np.outer(w, w).ravel(), minlength=29)
        E2 = ww @ M2; g2 = M2 @ (Ob / E2)                        # g2[s]
        c2 = w * (g2[S3] @ w)                                    # expected uses of each value in gap-2 pairs (per slot)
        w = (w * g1 + 2 * c2) / (Oa.sum() + 2 * Ob.sum())
    E1 = w @ M1; ww = np.bincount(S3.ravel(), weights=np.outer(w, w).ravel(), minlength=29); E2 = ww @ M2
    G = lambda O, E: 2 * float((O[O > 0] * np.log(O[O > 0] / (O.sum() * E[O > 0]))).sum())
    return G(Oa, E1) + G(Ob, E2), G(Oa, E1), G(Ob, E2), w, E1, E2
best = None
for restart in range(2):
    sig = rng.permutation(29); w = np.full(29, 1 / 29)
    cur, _, _, w, _, _ = fit(sig, w, 1500)
    steps, T0 = 12000, 8.0
    for t in range(steps):
        T = T0 * (0.02 / T0) ** (t / steps)
        a, b = rng.choice(29, 2, replace=False); s2 = sig.copy(); s2[a], s2[b] = s2[b], s2[a]
        Gt, _, _, w2, _, _ = fit(s2, w.copy(), 30)
        if Gt < cur or rng.random() < np.exp((cur - Gt) / T):
            sig, cur, w = s2, Gt, w2
    Gt, Ga, Gb, w, E1, E2 = fit(sig, w, 20000)
    print(f"restart {restart}: joint G = {Gt:.1f} (gap-1 {Ga:.1f}, gap-2 {Gb:.1f}); fitted gap-1 repeats {E1[0]*O1.sum():.0f}", flush=True)
    if best is None or Gt < best[0]: best = (Gt, sig.copy(), w.copy(), E1, E2)
Gt, sig, w, E1, E2 = best
boot = []
for _ in range(150):
    Oa = rng.multinomial(int(O1.sum()), E1 / E1.sum()).astype(float)
    Ob = rng.multinomial(int(O2.sum()), E2 / E2.sum()).astype(float)
    boot.append(fit(sig, np.full(29, 1 / 29), 2500, Oa, Ob)[0])
boot = np.array(boot)
print(f"best joint G = {Gt:.1f}; bootstrap (sigma fixed) mean {boot.mean():.1f}, max {boot.max():.1f}, P(G*>=G) {(boot>=Gt).mean():.3f}")
