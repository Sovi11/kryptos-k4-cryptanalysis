#!/usr/bin/env python3
"""Adversarial verification, stage 2: fair batteries + shuffle null."""
import math, json
import numpy as np
from vadv_statistics_english import (K4_LITERAL, vec, k4_stats, _run_stats_block,
                                     collect, STATS)

def collect_shuffle(rng, R, chunk=25_000):
    """Null that fixes K4's exact letter multiset and permutes it."""
    base = vec(K4_LITERAL)
    acc = {}
    done = 0
    while done < R:
        b = min(chunk, R - done)
        X = np.tile(base, (b, 1))
        # independent random permutation per row
        keys = rng.random((b, 97))
        order = np.argsort(keys, axis=1)
        X = np.take_along_axis(X, order, axis=1)
        d = _run_stats_block(X, None)
        for k, v in d.items():
            acc.setdefault(k, []).append(v)
        done += b
    return {k: np.concatenate(v) for k, v in acc.items()}

def two_sided_p(values, cal_v):
    srt = np.sort(cal_v); N = len(srt)
    ge = 1.0 - np.searchsorted(srt, values, side='left')/N
    le = np.searchsorted(srt, values, side='right')/N
    return np.minimum(1.0, 2*np.minimum(ge, le))

def omnibus(obs, cal, ev, bat, label):
    obs_p = np.array([two_sided_p(np.array([obs[k]]), cal[k])[0] for k in bat])
    k4min = float(obs_p.min()); which = bat[int(np.argmin(obs_p))]
    P = np.stack([two_sided_p(ev[k], cal[k]) for k in bat], axis=1)
    nullmin = P.min(axis=1)
    omn = float((nullmin <= k4min + 1e-12).mean())
    print(f"  {label}")
    print(f"     size {len(bat):>2}  K4 min-p {k4min:.5f} ({which})  OMNIBUS p = {omn:.4f}")
    return omn

obs = k4_stats()
R = 150_000

print("="*72)
print("A. UNIFORM null -- FAIR batteries (no after-the-fact width-21 member)")
print("="*72)
cal = collect(np.random.default_rng(101), R)
ev  = collect(np.random.default_rng(202), R)
fair15 = [s for s in STATS if s != 'colbig21_ex']
omnibus(obs, cal, ev, ['ioc','distinct','doubles','maxZ48','maxper30','bigrams','trigrams'],
        "report's 7 (maxper 2-30)")
omnibus(obs, cal, ev, ['ioc','distinct','doubles','maxZ48','maxper48','bigrams','trigrams'],
        "report's 7 but maxper 2-48")
omnibus(obs, cal, ev, fair15, "fair expanded 14 (all pre-specifiable stats)")
omnibus(obs, cal, ev, [s for s in fair15 if s != 'maxper30'],
        "fair expanded 13, maxper 2-48 only")
omnibus(obs, cal, ev, [s for s in fair15 if s != 'maxper48'],
        "fair expanded 13, maxper 2-30 only")

print()
print("="*72)
print("B. SHUFFLE null -- K4's exact letter multiset permuted")
print("   (fixes IoC/distinct/chi2 by construction; tests ARRANGEMENT only)")
print("="*72)
scal = collect_shuffle(np.random.default_rng(303), R)
sev  = collect_shuffle(np.random.default_rng(404), R)
print(f"  {'statistic':<12} {'K4':>9} {'nullmean':>9} {'P(>=obs)':>9} {'P(<=obs)':>9} {'2-sided':>8}")
for k in STATS:
    v = scal[k]
    ge = float((v >= obs[k]).mean()); le = float((v <= obs[k]).mean())
    print(f"  {k:<12} {obs[k]:>9.4f} {v.mean():>9.4f} {ge:>9.5f} {le:>9.5f} "
          f"{min(1.0,2*min(ge,le)):>8.5f}")
print()
arr = ['doubles','maxZ48','maxper30','bigrams','trigrams','colbig_ex48',
       'colbig_pr48','dblmod','gapfac']
omnibus(obs, scal, sev, arr, "arrangement battery, maxper 2-30")
arr2 = [s if s != 'maxper30' else 'maxper48' for s in arr]
omnibus(obs, scal, sev, arr2, "arrangement battery, maxper 2-48")
omnibus(obs, scal, sev, arr + ['maxper48','maxZ96'], "arrangement battery, both ranges")
