#!/usr/bin/env python3
"""LP2's anti-repeat rule: where the 86 surviving doublets sit, and what can produce them.

Needs numpy and the relikd page transcription in cicada/data/relikd (see lp_common).
Sections:
  A  inventory and junction classes (word, line, page, punctuation)
  B  dispersion across lines / blocks / sections
  C  alignment-free block test: doublet positions mod n, n = 2..40
  D  aligned residues from line / block / section starts
  E  prime and other number-theoretic positions
  F  clustering and neighbourhood (triplets, gaps between doublets)
  G  can ANY plaintext-independent additive key produce the spectrum?  (EM + bootstrap)
  H  simulated mechanisms vs LP2
  I  calibration: doublets on the solved pages and in English runes
"""
import os, sys, math, collections
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lp_common import IDX, RUNES, relikd_runes, RELIKD_DIR, PUNCT

rng = np.random.default_rng(3301)
N29 = 29
SEP = "=" * 78

R = relikd_runes()
r = np.array([x["r"] for x in R])
N = len(r)
same = np.array([not x["first"] for x in R])                 # pair (i-1, i) exists
idx = np.arange(1, N)[same[1:]]                              # second rune of each pair
dbl = r[idx] == r[idx - 1]
freq = np.bincount(r, minlength=N29) / N
p0 = float((freq ** 2).sum())                                # P(doublet) for independent runes
NP, ND = len(idx), int(dbl.sum())
RATIO = ND / (NP * p0)
J = [R[i]["j"] for i in idx]

def ppois_two(obs, exp):
    """Two-sided Poisson p (doubled smaller tail, capped at 1)."""
    from math import exp as e, lgamma, log
    def cdf(k):  # P(X <= k)
        return sum(e(-exp + i * log(exp) - lgamma(i + 1)) for i in range(0, k + 1)) if exp > 0 else 1.0
    lo = cdf(obs); hi = 1 - cdf(obs - 1) if obs > 0 else 1.0
    return min(1.0, 2 * min(lo, hi))

print(SEP); print("A. INVENTORY"); print(SEP)
print(f"runes {N}, pairs {NP}, doublets {ND}, expected (indep.) {NP*p0:.1f}, ratio {RATIO:.3f}")
print(f"lines {R[-1]['line']+1}, blocks {R[-1]['blk']+1}, sections {R[-1]['sec']+1}")

def jclass(j):
    if "PB" in j: return "block/page break"
    if j & PUNCT: return "punctuation (.,;chapter)"
    if "X" in j or "'" in j or '"' in j: return "other symbol"
    w, lb = "•" in j, "LB" in j
    return {(False, False): "in word, same line", (False, True): "in word, across line break",
            (True, False): "word break, same line", (True, True): "word break + line break"}[(w, lb)]

cls = np.array([jclass(j) for j in J])
print(f"\n{'junction':30s} {'pairs':>6s} {'dbl':>4s} {'exp@1':>7s} {'ratio':>6s} {'exp@LP2':>8s}  p(vs rest)")
for c in ["in word, same line", "in word, across line break", "word break, same line",
          "word break + line break", "punctuation (.,;chapter)", "block/page break", "other symbol"]:
    m = cls == c; n = int(m.sum()); o = int(dbl[m].sum())
    if n == 0: continue
    e1 = n * p0; e2 = n * p0 * RATIO
    print(f"{c:30s} {n:6d} {o:4d} {e1:7.1f} {o/e1:6.2f} {e2:8.1f}  {ppois_two(o, e2):.3f}")
lb = np.array(["LB" in j or "PB" in j for j in J])
for name, m in [("any line/page break", lb), ("no break", ~lb)]:
    n = int(m.sum()); o = int(dbl[m].sum())
    print(f"{name:30s} {n:6d} {o:4d} {n*p0:7.1f} {o/(n*p0):6.2f} {n*p0*RATIO:8.1f}  {ppois_two(o, n*p0*RATIO):.3f}")

# ---------------------------------------------------------------------------
print(SEP); print("B. DISPERSION (is the leak rate constant?)"); print(SEP)
def dispersion(unit):
    u = np.array([R[i][unit] for i in idx])
    _, inv = np.unique(u, return_inverse=True)
    pairs = np.bincount(inv); obs = np.bincount(inv, weights=dbl)
    exp = pairs * ND / NP
    stat = lambda o: float(((o - exp) ** 2 / np.maximum(exp, 1e-9)).sum())
    S = stat(obs); null = []
    for _ in range(4000):
        sel = rng.choice(NP, ND, replace=False)
        null.append(stat(np.bincount(inv[sel], minlength=len(pairs))))
    null = np.array(null)
    zero = int((obs == 0).sum()); ge2 = int((obs >= 2).sum())
    return len(pairs), S, null.mean(), float((null >= S).mean()), float((null <= S).mean()), zero, ge2
for unit in ["line", "blk", "sec"]:
    n, S, mu, pu, pl, z, g2 = dispersion(unit)
    print(f"{unit:5s}: {n:4d} units  chi2 {S:7.1f} (null mean {mu:7.1f})  P(over) {pu:.3f}  P(under) {pl:.3f}"
          f"  units with 0 dbl {z}, with >=2 dbl {g2}")
sec_ids = np.array([R[i]["sec"] for i in idx])
print("per section (file):", " ".join(f"{int(dbl[sec_ids==s].sum())}/{(sec_ids==s).sum()*p0:.0f}" for s in range(sec_ids.max()+1)))

# ---------------------------------------------------------------------------
print(SEP); print("C. ALIGNMENT-FREE BLOCK TEST  (doublets confined to one residue mod n per unit?)"); print(SEP)
print("Statistic S_n = sum over units of the most-populated residue class of doublet positions.")
print("Under 'protection resets every n runes' every doublet in a unit shares one residue, so S_n = 86.")
NS = np.arange(2, 41)
def block_test(unit, posk, nperm=2000):
    u = np.array([R[i][unit] for i in idx]); pos = np.array([R[i][posk] for i in idx])
    _, uinv = np.unique(u, return_inverse=True); nu = uinv.max() + 1
    k = np.bincount(uinv, weights=dbl, minlength=nu).astype(int)
    def S(sel):
        out = []
        for n in NS:
            c = np.bincount(uinv[sel] * n + pos[sel] % n, minlength=nu * n).reshape(nu, n)
            out.append(c.max(1).sum())
        return np.array(out)
    obs = S(np.where(dbl)[0])
    starts = np.searchsorted(uinv, np.arange(nu))  # idx is in reading order, so units are contiguous
    null = np.empty((nperm, len(NS)))
    for t in range(nperm):
        key = rng.random(NP)
        o = np.lexsort((key, uinv))
        rank = np.arange(NP) - starts[uinv[o]]
        null[t] = S(o[rank < k[uinv[o]]])
    mu, sd = null.mean(0), null.std(0) + 1e-9
    z = (obs - mu) / sd; zn = (null - mu) / sd
    pglob = float((zn.max(1) >= z.max()).mean())
    b = int(np.argmax(z))
    return obs, mu, z, NS[b], pglob
for unit, posk, label in [("sec", "ps", "section, rune index"), ("sec", "cps", "section, char index (separators count)"),
                          ("blk", "pb", "block/page, rune index"), ("line", "pl", "line, rune index")]:
    obs, mu, z, nb, pg = block_test(unit, posk)
    sel = [2, 3, 4, 5, 6, 7, 8]
    print(f"{label:40s} best n={nb:2d} S={obs[nb-2]:.0f} (null {mu[nb-2]:.1f}, z {z[nb-2]:+.2f}), global p {pg:.3f}")
    print("   n=2..8  S/null: " + "  ".join(f"{n}:{obs[n-2]:.0f}/{mu[n-2]:.1f}" for n in sel))

# ---------------------------------------------------------------------------
print(SEP); print("D. ALIGNED RESIDUES (position of 2nd rune mod n, from unit start)"); print(SEP)
def chi2_sf(x, df):
    # Wilson-Hilferty approximation, adequate for reporting
    if df <= 0: return float("nan")
    zz = ((x / df) ** (1 / 3) - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
    return 0.5 * math.erfc(zz / math.sqrt(2))
for posk, label in [("pl", "line"), ("pb", "block"), ("ps", "section")]:
    pos = np.array([R[i][posk] for i in idx]); best = (1, None)
    rows = []
    for n in range(2, 13):
        e = np.bincount(pos % n, minlength=n) * ND / NP
        o = np.bincount(pos[dbl] % n, minlength=n)
        x = float(((o - e) ** 2 / e).sum()); p = chi2_sf(x, n - 1)
        rows.append(p); best = min(best, (p, n))
    print(f"from {label:8s} start: min p {best[0]:.3f} at n={best[1]}  (11 tests; Bonferroni threshold 0.0045)")
pl = np.array([R[i]["pl"] for i in idx])
print("doublets by position-in-line of 2nd rune (0..): ", np.bincount(pl[dbl], minlength=5)[:5],
      " expected ", np.round(np.bincount(pl, minlength=5)[:5] * ND / NP, 1))

# ---------------------------------------------------------------------------
print(SEP); print("E. NUMBER-THEORETIC POSITIONS"); print(SEP)
def isprime(n):
    if n < 2: return False
    for d in range(2, int(n ** 0.5) + 1):
        if n % d == 0: return False
    return True
fib = {1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584}
for posk, label in [("pl", "line"), ("pb", "block"), ("ps", "section")]:
    pos = np.array([R[i][posk] for i in idx])
    for q, which in [(pos - 1, "1st rune, 0-based"), (pos, "2nd rune 0-based = 1st rune 1-based"), (pos + 1, "2nd rune, 1-based")]:
        isp = np.array([isprime(int(v)) for v in q])
        f_all = isp.mean(); o = int(isp[dbl].sum())
        from math import comb
        pval = sum(comb(ND, t) * f_all ** t * (1 - f_all) ** (ND - t) for t in range(o, ND + 1))
        print(f"prime position in {label:7s} ({which:36s}): {o:2d}/{ND} doublets vs base {f_all:.3f} "
              f"(exp {ND*f_all:.1f}), P(>=obs) {pval:.3f}")
ps = np.array([R[i]["ps"] for i in idx])
o = int(np.isin(ps, list(fib))[dbl].sum()); f = np.isin(ps, list(fib)).mean()
print(f"Fibonacci position in section: {o} doublets vs expected {ND*f:.2f}")

# ---------------------------------------------------------------------------
print(SEP); print("F. CLUSTERING AND NEIGHBOURHOOD"); print(SEP)
trip = sum(1 for i in range(2, N) if same[i] and same[i-1] and r[i] == r[i-1] == r[i-2])
print(f"triplets AAA: {trip}  (independent-leak expectation {ND*p0*RATIO:.2f})")
for g in (2, 3, 4):
    m = np.array([i for i in range(g, N) if all(same[i-t] for t in range(g))])
    o = int((r[m] == r[m - g]).sum()); e = len(m) * p0
    a = p0 * RATIO; lam = (N29 * a - 1) / (N29 - 1)
    em = len(m) * (1 / N29 + (N29 - 1) / N29 * lam ** g)  # first-order Markov anti-repeat chain
    print(f"gap-{g} repeats: {o}  (independent {e:.1f}, first-order anti-repeat chain {em:.1f})")
pos_global = idx[dbl]; secd = sec_ids[dbl]
gaps = np.array([b - a for a, b, s1, s2 in zip(pos_global[:-1], pos_global[1:], secd[:-1], secd[1:]) if s1 == s2])
null_small = []
for _ in range(4000):
    sel = np.sort(rng.choice(NP, ND, replace=False)); p_ = idx[sel]; s_ = sec_ids[sel]
    gg = np.diff(p_)[s_[1:] == s_[:-1]]
    null_small.append(((gg <= 10).sum(), (gg <= 30).sum(), np.median(gg)))
null_small = np.array(null_small)
for k, (lab, val) in enumerate([("gaps <= 10", (gaps <= 10).sum()), ("gaps <= 30", (gaps <= 30).sum()), ("median gap", np.median(gaps))]):
    print(f"{lab:11s}: {val:6.1f}  null mean {null_small[:,k].mean():6.1f}  P(null >= obs) {(null_small[:,k] >= val).mean():.3f}")
before = r[idx[dbl] - 2][[same[i-1] for i in idx[dbl]]]
after = np.array([r[i+1] for i in idx[dbl] if i + 1 < N and same[i+1]])
print(f"rune before a doublet equals it (= triplet): {int((before == r[idx[dbl]-1][[same[i-1] for i in idx[dbl]]]).sum())}")
cb = np.bincount(before, minlength=N29); x = float(((cb - len(before)*freq) ** 2 / (len(before)*freq)).sum())
ca = np.bincount(after, minlength=N29); y = float(((ca - len(after)*freq) ** 2 / (len(after)*freq)).sum())
print(f"runes preceding doublets chi2 {x:.1f}/28 (p {chi2_sf(x,28):.2f}); following chi2 {y:.1f}/28 (p {chi2_sf(y,28):.2f})")

# ---------------------------------------------------------------------------
print(SEP); print("G. CAN A PLAINTEXT-INDEPENDENT ADDITIVE KEY DO IT?  (any key distribution)"); print(SEP)
def english_pairs():
    """Within-word adjacent-rune differences from War and Peace (relikd baseline, runes)."""
    w = open(os.path.join(RELIKD_DIR, "baseline-rune-words.txt"), encoding="utf-8").read().split()
    D = np.zeros(N29); dd = 0; bi = np.zeros((N29, N29))
    for word in w:
        q = [IDX[c] for c in word if c in IDX]
        for a, b in zip(q, q[1:]):
            bi[a, b] += 1
    return bi
def lp1_pairs():
    bi = np.zeros((N29, N29))
    for f in os.listdir(RELIKD_DIR):
        if not f.startswith("solved_"): continue
        t = open(os.path.join(RELIKD_DIR, f), encoding="utf-8").read()
        word = []
        for ch in t + "\n":
            if ch in IDX: word.append(IDX[ch])
            else:
                for a, b in zip(word, word[1:]): bi[a, b] += 1
                word = []
    return bi
inword = np.array([(len(j) == 0 or j == frozenset({"LB"})) for j in J])
dc = (r[idx] - r[idx - 1]) % N29
O = np.bincount(dc[inword], minlength=N29).astype(float); NO = O.sum()
print(f"LP2 within-word pairs {int(NO)}, doublets {int(O[0])} (expected {NO/N29:.0f})")
That = np.fft.fft(O / NO)
def diff_dist(bi, s=1):
    P = bi / bi.sum(); D = np.zeros(N29)
    for a in range(N29):
        for b in range(N29):
            D[(s * (b - a)) % N29] += P[a, b]
    return D
def em_fit(D, O, iters=20000):
    M = np.array([np.roll(D, x) for x in range(N29)])         # M[x, y] = D(y - x)
    w = np.full(N29, 1 / N29)
    for _ in range(iters):
        E = w @ M
        w = w * (M @ (O / np.maximum(E, 1e-300))) / O.sum()
    E = w @ M
    G = 2 * float((O[O > 0] * np.log(O[O > 0] / (O.sum() * E[O > 0]))).sum())
    return G, w, E
for name, bi in [("War and Peace (runes)", english_pairs()), ("LP1 plaintext (Cicada's own spelling)", lp1_pairs())]:
    D = diff_dist(bi)
    Dh = np.abs(np.fft.fft(D))[1:]; Th = np.abs(That)[1:]
    print(f"\nplaintext model: {name}: {int(bi.sum())} within-word pairs, plaintext doublet rate {D[0]:.4f}")
    print(f"  Fourier check |D^p(w)| >= |T^(w)| needed for every w: holds at {int((Dh >= Th).sum())}/28 frequencies;"
          f" sum|D^p| = {Dh.sum():.3f} vs sum|T^| = {Th.sum():.3f}")
    res = []
    for s in range(1, N29):
        G, w, E = em_fit(diff_dist(bi, s), O, iters=6000)
        res.append((G, s))
    res.sort()
    G, s = res[0]
    G, w, E = em_fit(diff_dist(bi, s), O, iters=40000)
    boot = []
    for _ in range(200):
        Ob = rng.multinomial(int(NO), E / E.sum()).astype(float)
        boot.append(em_fit(diff_dist(bi, s), Ob, iters=4000)[0])
    boot = np.array(boot)
    print(f"  best multiplier s={s} (c = s*p + k): deviance G = {G:.1f}; bootstrap G under that model: "
          f"mean {boot.mean():.1f}, 99.9th pct {np.quantile(boot, .999):.1f}, P(G* >= G) = {(boot >= G).mean():.3f}")
    print(f"  best-fit doublets {E[0]*NO:.0f} vs observed {int(O[0])};  s=1 (Vigenere) G = {[g for g,t in res if t==1][0]:.1f},"
          f" s=28 (Beaufort) G = {[g for g,t in res if t==28][0]:.1f}")

# ---------------------------------------------------------------------------
print(SEP); print("H. SIMULATED MECHANISMS ON LP2's OWN SKELETON (English plaintext, uniform key)"); print(SEP)
words = open(os.path.join(RELIKD_DIR, "baseline-rune-words.txt"), encoding="utf-8").read().split()
eng = np.array([IDX[c] for w_ in words for c in w_ if c in IDX])
pl_all = np.array([x["pl"] for x in R]); pb_all = np.array([x["pb"] for x in R]); ps_all = np.array([x["ps"] for x in R])
first_all = np.array([x["first"] for x in R]); lbreak = np.array(["LB" in x["j"] or "PB" in x["j"] for x in R])
wbreak = np.array([("•" in x["j"]) or bool(x["j"] & PUNCT) or "PB" in x["j"] for x in R])
primepos = np.array([isprime(int(v)) for v in pb_all])
M2 = np.array([i for i in range(2, N) if same[i] and same[i-1]])
def fingerprint(c):
    d = c[idx] == c[idx - 1]
    m2 = M2
    f = np.bincount(c, minlength=N29) / N; q0 = (f ** 2).sum()
    lbm = lbreak[idx]
    return dict(ratio=d.sum() / (NP * q0), gap2=(c[m2] == c[m2 - 2]).mean() / q0,
                lb=(d[lbm].sum() / (lbm.sum() * q0)) / max(d.sum() / (NP * q0), 1e-9),
                S5=None)
def simulate(rule, reps=40):
    out = []
    for _ in range(reps):
        st = rng.integers(0, len(eng) - N); p = eng[st:st + N]
        c = np.empty(N, int); outer = rng.integers(0, N29)
        for i in range(N):
            v = (p[i] + rng.integers(0, N29)) % N29
            if i > 0 and not first_all[i]:
                prev = c[i - 1]
                if rule == "none": pass
                elif rule == "p-reroll":
                    if v == prev and rng.random() < 1 - RATIO:
                        while v == prev: v = (p[i] + rng.integers(0, N29)) % N29
                elif rule == "single-reroll":
                    if v == prev: v = (p[i] + rng.integers(0, N29)) % N29
                elif rule in ("reset-line", "reset-word", "reset-5", "prime-off"):
                    off = {"reset-line": lbreak[i], "reset-word": wbreak[i], "reset-5": ps_all[i] % 5 == 0,
                           "prime-off": primepos[i]}[rule]
                    while v == prev and not off: v = (p[i] + rng.integers(0, N29)) % N29
            c[i] = v
        out.append(fingerprint(c))
    return {k: (np.mean([o[k] for o in out]), np.std([o[k] for o in out])) for k in ("ratio", "gap2", "lb")}
obs = fingerprint(r)
print(f"{'mechanism':16s} {'doublet ratio':>16s} {'gap-2 ratio':>14s} {'line-break leak / overall':>26s}")
print(f"{'LP2 observed':16s} {obs['ratio']:16.3f} {obs['gap2']:14.3f} {obs['lb']:26.2f}")
for rule in ["none", "single-reroll", "p-reroll", "reset-line", "reset-word", "reset-5", "prime-off"]:
    s_ = simulate(rule, reps=12 if rule != "none" else 6)
    print(f"{rule:16s} {s_['ratio'][0]:9.3f} ± {s_['ratio'][1]:.3f} {s_['gap2'][0]:8.3f} ± {s_['gap2'][1]:.3f} "
          f"{s_['lb'][0]:18.2f} ± {s_['lb'][1]:.2f}")

# ---------------------------------------------------------------------------
print(SEP); print("I. CALIBRATION: doublets elsewhere"); print(SEP)
def stream_of(fname):
    t = open(os.path.join(RELIKD_DIR, fname), encoding="utf-8").read()
    return [IDX[c] for c in t if c in IDX]
CAL = [f for f in sorted(os.listdir(RELIKD_DIR)) if f.endswith(".txt") and
       (f.startswith(("0_", "jpg", "p56", "p57", "solved_")))]
for f in CAL:
    s_ = stream_of(f)
    if len(s_) < 50: continue
    d = sum(1 for a, b in zip(s_, s_[1:]) if a == b); fq = np.bincount(s_, minlength=N29) / len(s_)
    e = (len(s_) - 1) * (fq ** 2).sum()
    print(f"{f:32s} runes {len(s_):5d}  doublets {d:3d}  expected(indep) {e:6.1f}  ratio {d/e:.2f}")
