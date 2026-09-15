"""search_sample.py -- EXACT sampling from the space of crib-consistent English plaintexts.

Annealing returns the MODE of the language model, which is why it overshoots real English
(it reaches -0.66 where real English sits at -0.74 and real Sanborn plaintext at -0.97).
The mode is a terrible way to map a space.

The quadgram model is a 3rd-order Markov chain over 26 letters, so the distribution of
97-letter strings CONDITIONED on the 24 crib letters being at their true positions can be
handled exactly by dynamic programming over the 26^3 = 17,576 states:

  backward pass  B_i(s) = sum over all legal completions of the weight from state s at i
  forward sample draw c_i with probability  P(c_i | s) * B_{i+1}(s') / B_i(s)

This yields INDEPENDENT, UNBIASED draws from "English text that has EAST at 22, NORTHEAST
at 26, BERLIN at 64, CLOCK at 70", under the model.  It also yields, exactly:

  * log10 P(the four cribs land where Sanborn says) under the model
  * the conditional entropy of the 73 free letters, i.e. log2 of the effective NUMBER of
    crib-consistent English plaintexts -- the number that says whether this line of attack
    could ever confirm anything

Usage:
    python3.13 search_sample.py stats
    python3.13 search_sample.py sample [n]
    python3.13 search_sample.py recur  [n]      # word recurrence vs matched controls
"""
import json, math, os, random, re, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
sys.path.insert(0, HERE)
import search_lm
import search_anneal as SA
import runningkey_lib as RK

A2Z = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
N = 97

UNI = [8.17,1.49,2.78,4.25,12.70,2.23,2.02,6.09,6.97,0.15,0.77,4.03,2.41,
       6.75,7.51,1.93,0.10,5.99,6.33,9.06,2.76,0.98,2.36,0.15,1.97,0.07]

def _p4():
    import numpy as np
    Q, _, _ = search_lm.load()
    P = np.power(10.0, Q.astype(np.float64)).reshape(26 ** 3, 26)
    P /= P.sum(axis=1, keepdims=True)
    return P

_P4 = None
def P4():
    global _P4
    if _P4 is None:
        _P4 = _p4()
    return _P4

def backward(fixed, n=N):
    """B[i] (i = 3..n) as (n-2) arrays of length 26^3, log-scaled.
    B[i][s] = sum over legal c_i..c_{n-1} of prod P(c_j | state).  Returns (Bs, logscale)."""
    import numpy as np
    P = P4()
    allowed = []
    for i in range(n):
        a = np.zeros(26)
        if i in fixed:
            a[ord(fixed[i]) - 65] = 1.0
        else:
            a[:] = 1.0
        allowed.append(a)
    B = [None] * (n + 1)
    B[n] = np.ones(26 ** 3)
    logscale = [0.0] * (n + 1)
    for i in range(n - 1, 2, -1):
        nxt = B[i + 1].reshape(26, 26, 26)              # [b, c0, c]
        Nmat = nxt.reshape(676, 26)                      # [b*26+c0, c]
        W = P * allowed[i][None, :]                      # [s, c]
        Bi = (W.reshape(26, 676, 26) * Nmat[None, :, :]).sum(axis=2).reshape(-1)
        m = Bi.max()
        if m <= 0:
            raise SystemExit(f"no legal completion at position {i}")
        B[i] = Bi / m
        logscale[i] = logscale[i + 1] + math.log10(m)
    return B, logscale

def head_weights(fixed):
    """Weight of each initial 3-letter state (unigram model for the first three letters)."""
    import numpy as np
    u = np.array(UNI) / sum(UNI)
    w = np.zeros(26 ** 3)
    a0 = np.ones(26); a1 = np.ones(26); a2 = np.ones(26)
    for i, a in ((0, a0), (1, a1), (2, a2)):
        if i in fixed:
            a[:] = 0.0
            a[ord(fixed[i]) - 65] = 1.0
    w = (u * a0)[:, None, None] * (u * a1)[None, :, None] * (u * a2)[None, None, :]
    return w.reshape(-1)

def log_partition(fixed):
    """log10 of the total model probability of all strings consistent with `fixed`."""
    import numpy as np
    B, ls = backward(fixed)
    w = head_weights(fixed)
    z = float((w * B[3]).sum())
    return math.log10(z) + ls[3]

def sample(fixed, count, seed=0, n=N):
    import numpy as np
    P = P4()
    B, _ls = backward(fixed, n)
    w = head_weights(fixed)
    rng = np.random.default_rng(seed)
    init = w * B[3]
    init = init / init.sum()
    out = []
    for _ in range(count):
        s = int(rng.choice(26 ** 3, p=init))
        c = [s // 676, (s // 26) % 26, s % 26]
        st = s
        for i in range(3, n):
            b, c0 = (st // 26) % 26, st % 26
            nxt_base = b * 676 + c0 * 26
            pr = P[st] * B[i + 1][nxt_base: nxt_base + 26]
            if i in fixed:
                mask = np.zeros(26); mask[ord(fixed[i]) - 65] = 1.0
                pr = pr * mask
            tot = pr.sum()
            if tot <= 0:
                raise SystemExit("dead end")
            pr = pr / tot
            ch = int(rng.choice(26, p=pr))
            c.append(ch)
            st = nxt_base + ch
        out.append("".join(A2Z[x] for x in c))
    return out

# ------------------------------------------------------------------ helpers
def load_words(minlen=5):
    w = set()
    with open("/usr/share/dict/words") as f:
        for x in f:
            x = x.strip().upper()
            if len(x) >= minlen and x.isalpha() and x.isascii():
                w.add(x)
    return w

def words_in(s, vocab, minlen=5, maxlen=12):
    out = []
    for i in range(len(s)):
        for L in range(minlen, min(maxlen, len(s) - i) + 1):
            if s[i:i + L] in vocab:
                out.append((i, s[i:i + L]))
    return out

CONDS = {
    "k4":      lambda seed: dict(RK.CRIBS),
    "ctlfreq": lambda seed: SA.random_fixed(seed),
    "ctlword": lambda seed: SA.crib_word_control(seed),
    "free":    lambda seed: {},
}

def stats():
    import numpy as np
    print("=" * 96)
    print("TABLE S1 -- exact conditional statistics of the language model")
    print("=" * 96)
    lz_free = log_partition({})
    lz_k4 = log_partition(dict(RK.CRIBS))
    print(f"log10 P(any 97-letter string)          = {lz_free:10.4f}   (1.0000 expected; check)")
    print(f"log10 P(the 24 Sanborn crib letters at their true positions) = {lz_k4:10.4f}")
    print(f"   i.e. the cribs cost {-(lz_k4 - lz_free):.2f} log10 units = "
          f"{-(lz_k4-lz_free)/24:.3f} per pinned letter")
    print(f"   (24 uniform-random letters would cost {24*math.log10(26):.2f}; "
          f"English text makes them much cheaper than that)")
    print()
    # entropy of the conditional distribution, by sampling
    S = sample(dict(RK.CRIBS), 400, seed=101)
    lp = []
    P = P4()
    u = np.log10(np.array(UNI) / sum(UNI))
    for s in S:
        c = [ord(x) - 65 for x in s]
        t = u[c[0]] + u[c[1]] + u[c[2]]
        for i in range(3, N):
            st = ((c[i-3] * 26 + c[i-2]) * 26 + c[i-1])
            t += math.log10(P[st][c[i]])
        lp.append(t)
    mean_lp = sum(lp) / len(lp)
    H = -(mean_lp - lz_k4)                      # log10 of the effective support size
    print(f"mean log10 P(sample) under the model   = {mean_lp:.3f}")
    print(f"conditional entropy of the 73 free letters = {H:.2f} log10 units "
          f"= {H*math.log2(10):.1f} bits")
    print(f"   -> the number of DISTINCT crib-consistent English plaintexts the model")
    print(f"      considers about as likely as each other is on the order of 10^{H:.0f}.")
    print(f"      ({H/73:.3f} log10 units per free letter, vs {math.log10(26):.3f} for random.)")
    print()
    sc = [search_lm.quad(s) for s in S]
    import statistics as sts
    print(f"quadgram score of exact samples: mean {sts.mean(sc):.4f} sd {sts.pstdev(sc):.4f}")
    print(f"   held-out English -0.741 +- 0.077;  Sanborn K1-K3 -0.967 +- 0.087;")
    print(f"   ANNEALED (the mode) about -0.66.  Exact samples sit where real text sits;")
    print(f"   the annealer's mode does not.  This is why annealing cannot be used as evidence.")
    return S

def recur(n=1500):
    vocab = load_words(5)
    res = {}
    for name, f in CONDS.items():
        txts = []
        # for the control conditions, redraw the pins every 50 samples so the control
        # is over pin CONTENT as well as over sampling noise
        k = 0
        while len(txts) < n:
            fixed = f(9000 + k)
            txts += sample(fixed, min(50, n - len(txts)), seed=k * 17 + 3)
            k += 1
        res[name] = txts
    print("=" * 96)
    print(f"TABLE S2 -- word recurrence in {n} EXACT samples per condition")
    print("           (exact draws from 'English text with these 24 letters pinned')")
    print("=" * 96)
    cnt = {}
    posn = {}
    for name, txts in res.items():
        c = Counter(); p = defaultdict(Counter)
        for t in txts:
            seen = set()
            for i, w in words_in(t, vocab):
                if w not in seen:
                    c[w] += 1; seen.add(w)
                p[w][i] += 1
        cnt[name] = c; posn[name] = p
    names = list(CONDS)
    top = [w for w, _ in cnt["k4"].most_common(25)]
    print(f"{'word':14s}" + "".join(f"{x:>10s}" for x in names))
    for w in top:
        print(f"{w:14s}" + "".join(f"{100.0*cnt[x][w]/n:9.2f}%" for x in names))
    print()
    print("TABLE S3 -- the words the task asked about")
    print(f"{'word':14s}" + "".join(f"{x:>10s}" for x in names))
    from search_recur import WATCH
    for w in WATCH:
        if sum(cnt[x][w] for x in names) == 0:
            continue
        print(f"{w:14s}" + "".join(f"{100.0*cnt[x][w]/n:9.2f}%" for x in names))
    print()
    tot = {x: sum(cnt[x].values()) for x in names}
    print("words >=5 letters per sample:", {x: round(tot[x] / n, 2) for x in names})
    with open(os.path.join(HERE, "search_sample_recur.json"), "w") as f:
        json.dump({k: v[:200] for k, v in res.items()}, f)
    return res

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "stats"
    if mode == "stats":
        S = stats()
        print()
        print("Ten independent EXACT samples (crib letters lower-cased):")
        for s in S[:10]:
            print("   " + "".join(ch.lower() if i in RK.CRIBS else ch
                                  for i, ch in enumerate(s)))
    elif mode == "sample":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        for s in sample(dict(RK.CRIBS), n, seed=5):
            print(s)
    elif mode == "recur":
        recur(int(sys.argv[2]) if len(sys.argv) > 2 else 1500)
