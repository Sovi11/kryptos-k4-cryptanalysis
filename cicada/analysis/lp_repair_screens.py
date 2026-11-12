#!/usr/bin/env python3
"""Key-free screens for collision-repair rules on LP2 (see findings/lp2_repairrules.md).

A repair rule decides what is written when the encryption of p_i would equal c_{i-1}. Different rules
leave different fingerprints in the ciphertext, testable without the key:
  * diff spectrum d = c_i - c_{i-1}: a rule that writes "previous rune + d" piles ~360 repairs onto one d.
  * gap-2 repeats (A?A, c_{i+1} = c_{i-1}): a rule that inserts a null and re-encrypts p with the same
    key value writes exactly c_{i-1} again after the null, so it adds ~360 A?A triples.
  * unigrams: a rule that writes the plaintext rune unencrypted puts ~360 English-distributed runes
    into the text (statistic: mixture log-likelihood ratio, maximised over the 58 (sp, a) maps).
Each statistic is compared with LP2-sized simulations: English plaintext (War and Peace in runes), uniform key,
rule firing on 81% of collisions.
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lp_common import relikd_runes, IDX, RELIKD_DIR

R = relikd_runes(); C = np.array([x["r"] for x in R]); SEC = np.array([x["sec"] for x in R]); N = len(C)
WORDS = [[IDX[ch] for ch in w if ch in IDX] for w in
         open(os.path.join(RELIKD_DIR, "baseline-rune-words.txt"), encoding="utf-8").read().split()]
PT = np.array([v for w in WORDS for v in w])
F = np.bincount(PT, minlength=29) / len(PT)
WLIT = 0.81 / 29                                           # expected share of repaired runes

def stats(c, sec):
    s1 = sec[1:] == sec[:-1]; s2 = sec[2:] == sec[:-2]
    d = ((c[1:] - c[:-1]) % 29)[s1]; h = np.bincount(d, minlength=29)
    nz = h[1:]; e = nz.sum() / 28
    aba = int((c[2:] == c[:-2])[s2].sum())
    n = np.bincount(c, minlength=29); best = -np.inf
    for sp in (1, -1):
        for a in range(29):
            ft = F[(sp * (np.arange(29) - a)) % 29]        # frequency of y = sp*p + a
            best = max(best, float((n * np.log1p(WLIT * (29 * ft - 1))).sum()))
    return dict(doublets=int(h[0]), maxdiff=int(nz.max()), argd=int(nz.argmax()) + 1,
                chi2=float(((nz - e) ** 2 / e).sum()), aba=aba, lit=best)

def simulate(rule, rng, fire=0.81, d=7):
    st = rng.integers(0, len(PT) - 2 * N); p = PT[st:st + 2 * N]; K = rng.integers(0, 29, 3 * N)
    out = []; j = 0; i = 0; prev = None
    while len(out) < N:
        v = (p[i] + K[j]) % 29
        if prev is not None and v == prev and rng.random() < fire:
            if rule == "skip":   j += 1; v = (p[i] + K[j]) % 29
            elif rule == "bump": v = (prev + d) % 29
            elif rule == "literal": out.append(int(p[i])); prev = int(p[i]); i += 1; continue   # key not consumed
            elif rule == "null":
                nul = int(rng.integers(0, 28)); nul += nul >= prev
                out.append(nul); prev = nul; continue                     # p_i retried with the same K[j]
        out.append(int(v)); prev = int(v); i += 1; j += 1
    return np.array(out[:N])

if __name__ == "__main__":
    obs = stats(C, SEC)
    rng = np.random.default_rng(29)
    print(f"LP2 ({N} runes): doublets {obs['doublets']}, largest nonzero-diff count {obs['maxdiff']} (d={obs['argd']}), "
          f"chi2(27) of nonzero diffs {obs['chi2']:.1f}, A?A {obs['aba']}, literal LLR {obs['lit']:.2f}")
    print(f"{'rule (fires on 81% of collisions)':40s} {'doublets':>14s} {'max diff':>14s} {'chi2 diffs':>14s} {'A?A':>14s} {'literal LLR':>14s}")
    sims = {}
    for rule, label in [("skip", "skip one key value (null for this test)"), ("bump", "write previous rune + d (d=7)"),
                        ("null", "insert null, retry same key value"), ("literal", "write plaintext, key not consumed")]:
        S = [stats(simulate(rule, rng), SEC) for _ in range(200)]; sims[rule] = S
        def f(k): a = np.array([s[k] for s in S]); return f"{a.mean():7.1f}±{a.std():5.1f}"
        print(f"{label:40s} {f('doublets'):>14s} {f('maxdiff'):>14s} {f('chi2'):>14s} {f('aba'):>14s} {f('lit'):>14s}")
    for k in ("maxdiff", "chi2", "aba", "lit"):
        for rule in ("skip", "bump", "null", "literal"):
            a = np.array([s[k] for s in sims[rule]])
            print(f"   P(sim >= LP2) for {k:8s} under {rule:8s}: {(a >= obs[k]).mean():.3f}   P(sim <= LP2): {(a <= obs[k]).mean():.3f}")
