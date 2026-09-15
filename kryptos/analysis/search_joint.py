"""search_joint.py -- joint plaintext+keystream optimisation (running key with an
UNKNOWN English key).

The completed work ruled out running keys drawn from the sculpture's own texts.
This script asks the more general question: is there ANY 97-letter English-looking
key stream that turns K4 into English, consistent with the 24 cribs?

State  : the 73 free plaintext letters (the 24 crib letters are pinned).
Given P, the key stream K is determined position-by-position by the cipher combo.
Objective: quad(P) + W * quad(K)  under the calibrated model of search_lm.py.

Validation (mandatory before believing a negative): the same optimiser is run on
SYNTHETIC ciphertexts built from a real English plaintext and a real English running
key, with 24 letters of the plaintext revealed at the K4 crib positions.  The
recovery rate on those tells us how much power the attack has.

Usage:
    python3.13 search_joint.py validate [ntrials] [restarts] [steps]
    python3.13 search_joint.py k4       [restarts] [steps]
    python3.13 search_joint.py control  [ntrials] [restarts] [steps]
"""
import json, math, os, random, re, sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import search_lm
import runningkey_lib as RK

A2Z = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CT_K4 = RK.K4_CT
CRIBS = RK.CRIBS                     # 0-indexed pos -> plaintext letter
COMBOS = list(RK.combos())
W = 1.0                              # weight on the key-stream language model

_QL = None
def qtab():
    global _QL
    if _QL is None:
        Q, _, _ = search_lm.load()
        _QL = Q.astype("float64").tolist()
    return _QL

def keytab(cb, ct):
    """(len(ct), 26) table: plaintext letter code -> implied key letter code."""
    fam, ap, ac, ak = cb
    Ap, Ac, Ak = RK.ALPHAS[ap], RK.ALPHAS[ac], RK.ALPHAS[ak]
    tab = []
    for c in ct:
        ci = Ac.index(c)
        row = []
        for pcode in range(26):
            pi = Ap.index(A2Z[pcode])
            ki = RK.key_index(fam, pi, ci)
            row.append(ord(Ak[ki]) - 65)
        tab.append(row)
    return tab

def _quad_sum(codes, Q):
    s = 0.0
    for i in range(len(codes) - 3):
        s += Q[((codes[i] * 26 + codes[i+1]) * 26 + codes[i+2]) * 26 + codes[i+3]]
    return s

def _local(codes, pos, Q):
    s = 0.0
    lo = max(0, pos - 3); hi = min(len(codes) - 4, pos)
    for i in range(lo, hi + 1):
        s += Q[((codes[i] * 26 + codes[i+1]) * 26 + codes[i+2]) * 26 + codes[i+3]]
    return s

def joint_anneal(ct, fixed, cb, seed, steps=400_000, t0=1.6, t1=0.03, w=W):
    Q = qtab()
    tab = keytab(cb, ct)
    n = len(ct)
    rnd = random.Random(seed)
    free = [i for i in range(n) if i not in fixed]
    p = [rnd.randrange(26) for _ in range(n)]
    for pos, ch in fixed.items():
        p[pos] = ord(ch) - 65
    k = [tab[i][p[i]] for i in range(n)]
    cur = _quad_sum(p, Q) + w * _quad_sum(k, Q)
    best = cur; bp = p[:]
    for step in range(steps):
        T = t0 * (t1 / t0) ** (step / steps)
        pos = free[rnd.randrange(len(free))]
        oldp, oldk = p[pos], k[pos]
        newp = rnd.randrange(26)
        if newp == oldp:
            continue
        b = _local(p, pos, Q) + w * _local(k, pos, Q)
        p[pos] = newp; k[pos] = tab[pos][newp]
        a = _local(p, pos, Q) + w * _local(k, pos, Q)
        d = a - b
        if d >= 0 or rnd.random() < math.exp(d / T):
            cur += d
            if cur > best:
                best = cur; bp = p[:]
        else:
            p[pos] = oldp; k[pos] = oldk
    # greedy polish
    p = bp[:]; k = [tab[i][p[i]] for i in range(n)]
    cur = _quad_sum(p, Q) + w * _quad_sum(k, Q)
    improved = True
    while improved:
        improved = False
        for pos in free:
            b = _local(p, pos, Q) + w * _local(k, pos, Q)
            oldp = p[pos]
            bl, bd = oldp, 0.0
            for newp in range(26):
                if newp == oldp:
                    continue
                p[pos] = newp; k[pos] = tab[pos][newp]
                d = _local(p, pos, Q) + w * _local(k, pos, Q) - b
                if d > bd:
                    bd, bl = d, newp
            p[pos] = bl; k[pos] = tab[pos][bl]
            if bl != oldp:
                cur += bd; improved = True
    PT = "".join(A2Z[c] for c in p)
    KS = "".join(A2Z[c] for c in k)
    return cur / 94.0, PT, KS

def _job(a):
    ct, fixed, cb, seed, steps = a
    return joint_anneal(ct, fixed, cb, seed, steps)

def best_of(ct, fixed, cb, restarts, steps, procs=8, seed0=0):
    args = [(ct, fixed, cb, seed0 + i, steps) for i in range(restarts)]
    with Pool(procs) as pool:
        out = pool.map(_job, args, chunksize=1)
    out.sort(key=lambda t: -t[0])
    return out[0]

# ------------------------------------------------------------------ synthetic
def english_slices(n, length=97, seed=3):
    _, _, hold = search_lm.load()
    rnd = random.Random(seed)
    return [hold[i:i + length] for i in
            (rnd.randrange(0, len(hold) - length - 1) for _ in range(n))]

def encrypt(cb, pt, key):
    return "".join(RK.encrypt_letter(cb, p, k) for p, k in zip(pt, key))

def validate(ntrials=8, restarts=16, steps=400_000):
    print("SYNTHETIC VALIDATION: real English plaintext + real English running key,")
    print("24 plaintext letters revealed at the K4 crib positions.")
    pts = english_slices(ntrials, seed=11)
    kys = english_slices(ntrials, seed=77)
    cb = ("vigenere", "plain", "plain", "plain")
    rec = []
    for t in range(ntrials):
        pt, key = pts[t], kys[t]
        ct = encrypt(cb, pt, key)
        fixed = {i: pt[i] for i in CRIBS}
        s, P, K = best_of(ct, fixed, cb, restarts, steps, seed0=t * 1000)
        free = [i for i in range(97) if i not in fixed]
        acc = sum(1 for i in free if P[i] == pt[i]) / len(free)
        true_s = (search_lm.quad(pt) * 94 + W * search_lm.quad(key) * 94) / 94.0
        rec.append((acc, s, true_s))
        print(f"  trial {t}: free-letter recovery {acc*100:5.1f}%   "
              f"found joint {s:7.4f}  true joint {true_s:7.4f}")
        print(f"     true PT {pt}")
        print(f"     got  PT {P}")
        print(f"     true KY {key}")
        print(f"     got  KY {K}")
    import statistics as st
    print(f"  MEAN recovery {st.mean(a for a,_,_ in rec)*100:.1f}% of free letters; "
          f"found >= true joint score in "
          f"{sum(1 for a,s,ts in rec if s >= ts)}/{ntrials} trials")
    return rec

def run_k4(restarts=24, steps=400_000):
    out = []
    for cb in COMBOS:
        s, P, K = best_of(CT_K4, CRIBS, cb, restarts, steps)
        out.append((s, RK.combo_name(cb), P, K))
        print(f"{RK.combo_name(cb):44s} joint {s:7.4f}  PTq {search_lm.quad(P):7.4f} "
              f"KYq {search_lm.quad(K):7.4f}")
        print(f"    PT {P}")
        print(f"    KY {K}")
    out.sort(key=lambda t: -t[0])
    with open(os.path.join(HERE, "search_joint_k4.json"), "w") as f:
        json.dump(out, f)
    return out

def control(ntrials=12, restarts=24, steps=400_000):
    """Same optimisation on random ciphertexts -- the null for 'how high a joint score
    can this optimiser reach on a text with no English running key at all'."""
    rnd = random.Random(4242)
    cb = ("vigenere", "plain", "plain", "plain")
    scores = []
    for t in range(ntrials):
        ct = "".join(A2Z[rnd.randrange(26)] for _ in range(97))
        s, P, K = best_of(ct, CRIBS, cb, restarts, steps, seed0=t * 777)
        scores.append(s)
        print(f"  control {t}: joint {s:7.4f}  PTq {search_lm.quad(P):7.4f} "
              f"KYq {search_lm.quad(K):7.4f}")
    import statistics as st
    print(f"  CONTROL mean {st.mean(scores):.4f} sd {st.pstdev(scores):.4f} "
          f"max {max(scores):.4f}")
    with open(os.path.join(HERE, "search_joint_control.json"), "w") as f:
        json.dump(scores, f)
    return scores

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "validate"
    a = [int(x) for x in sys.argv[2:]]
    if mode == "validate":
        validate(*(a or [8, 16, 400_000]))
    elif mode == "k4":
        run_k4(*(a or [24, 400_000]))
    elif mode == "control":
        control(*(a or [12, 24, 400_000]))
