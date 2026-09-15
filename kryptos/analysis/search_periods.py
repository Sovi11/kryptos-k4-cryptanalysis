"""search_periods.py -- the crib-blind periods, attacked from the plaintext side.

findings/families.md swept periodic Vigenere/Beaufort/variant-Beaufort/Quagmire for periods
2-26.  Periods 27+ were never tested, and for a good reason: the 24 crib positions occupy
24 DISTINCT residues mod 27, 28, 29 and mod every p >= 53, so the cribs impose ZERO
constraints there and the crib test has nothing to say.

But the cribs still PIN key letters.  At period p the 24 cribs fix the key at `distinct`
residues, leaving only p - distinct free.  At p = 27 that is THREE letters -- 26^3 = 17,576
candidate decryptions, exhaustively searchable.  The right test is therefore not "do the
cribs fit" (they always do) but "does the best-scoring decryption read as English, compared
with what the same number of free parameters buys on a ciphertext known to have no such key".

Power, computed from search_sample.py: the crib-consistent English plaintexts number about
10^55 out of 26^73 = 10^103.3, a fraction of 10^-48.3.  A period-p key offers 26^free
candidate decryptions, so the expected number of English-looking decryptions by chance is
10^(1.415*free - 48.3).  That is < 1 for free <= 34, i.e. for p <= 57 (and for p <= 52 via
the free-letter count).  ABOVE p = 57 the test has no power AT ALL: chance alone supplies
English.  This script therefore tests p = 27..57 and states the rest as untestable.

Usage:
    python3.13 search_periods.py validate      # optimiser vs exhaustive at p=27; synthetic recovery
    python3.13 search_periods.py run [pmax]
"""
import json, math, os, random, sys, time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import search_lm
import runningkey_lib as RK

A2Z = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CT = RK.K4_CT
CRIBS = RK.CRIBS
COMBOS = list(RK.combos())

_QL = None
def qtab():
    global _QL
    if _QL is None:
        Q, _, _ = search_lm.load()
        _QL = Q.astype("float64").tolist()
    return _QL

def dec_table(cb, ct):
    """T[i][k] = plaintext code at position i when the key letter code (in the key alphabet
    index space) is k."""
    fam, ap, ac, ak = cb
    Ap, Ac = RK.ALPHAS[ap], RK.ALPHAS[ac]
    T = []
    for c in ct:
        ci = Ac.index(c)
        T.append([ord(Ap[RK.pt_index(fam, ci, k)]) - 65 for k in range(26)])
    return T

def req_key_index(cb, pos, ct):
    fam, ap, ac, ak = cb
    return RK.key_index(fam, RK.ALPHAS[ap].index(CRIBS[pos]), RK.ALPHAS[ac].index(ct[pos]))

def pin_map(cb, p, ct, cribs=None):
    """residue -> required key index, or None if the cribs contradict each other at period p."""
    cribs = CRIBS if cribs is None else cribs
    pins = {}
    for pos in sorted(cribs):
        fam, ap, ac, ak = cb
        k = RK.key_index(fam, RK.ALPHAS[ap].index(cribs[pos]), RK.ALPHAS[ac].index(ct[pos]))
        r = pos % p
        if r in pins and pins[r] != k:
            return None
        pins[r] = k
    return pins

def score_codes(codes, Q):
    s = 0.0
    for i in range(len(codes) - 3):
        s += Q[((codes[i] * 26 + codes[i+1]) * 26 + codes[i+2]) * 26 + codes[i+3]]
    return s

def optimise(T, p, pins, Q, restarts=12, rng=None, n=97):
    """Coordinate descent over the free residues; returns (best score/94, best key indices)."""
    rng = rng or random.Random(0)
    free = [r for r in range(p) if r not in pins]
    if not free:
        key = [pins[i % p] for i in range(p)]
        codes = [T[i][key[i % p]] for i in range(n)]
        return score_codes(codes, Q) / (n - 3), key
    windows = {}
    for r in free:
        S = [i for i in range(n) if i % p == r]
        W = set()
        for i in S:
            for w in range(max(0, i - 3), min(n - 4, i) + 1):
                W.add(w)
        windows[r] = (S, sorted(W))
    best_all = (-1e9, None)
    for _ in range(restarts):
        key = [pins.get(r, rng.randrange(26)) for r in range(p)]
        codes = [T[i][key[i % p]] for i in range(n)]
        cur = score_codes(codes, Q)
        improved = True
        while improved:
            improved = False
            for r in free:
                S, W = windows[r]
                base = sum(Q[((codes[w]*26 + codes[w+1])*26 + codes[w+2])*26 + codes[w+3]]
                           for w in W)
                old = key[r]
                bestk, bestd = old, 0.0
                for k in range(26):
                    if k == old:
                        continue
                    for i in S:
                        codes[i] = T[i][k]
                    v = sum(Q[((codes[w]*26 + codes[w+1])*26 + codes[w+2])*26 + codes[w+3]]
                            for w in W)
                    if v - base > bestd:
                        bestd, bestk = v - base, k
                for i in S:
                    codes[i] = T[i][bestk]
                key[r] = bestk
                if bestk != old:
                    cur += bestd
                    improved = True
        if cur > best_all[0]:
            best_all = (cur, key[:])
    return best_all[0] / (n - 3), best_all[1]

def decrypt_with(T, p, key, n=97):
    return "".join(A2Z[T[i][key[i % p]]] for i in range(n))

# ------------------------------------------------------------------ validate
def exhaustive_p27(cb, Q):
    T = dec_table(cb, CT)
    p = 27
    pins = pin_map(cb, p, CT)
    if pins is None:
        return None
    free = [r for r in range(p) if r not in pins]
    assert len(free) == 3, free
    best = (-1e9, None)
    key = [pins.get(r, 0) for r in range(p)]
    for a in range(26):
        key[free[0]] = a
        for b in range(26):
            key[free[1]] = b
            for c in range(26):
                key[free[2]] = c
                codes = [T[i][key[i % p]] for i in range(97)]
                s = score_codes(codes, Q)
                if s > best[0]:
                    best = (s, key[:])
    return best[0] / 94.0, best[1]

def validate():
    Q = qtab()
    print("=" * 100)
    print("VALIDATION 1 -- coordinate descent vs EXHAUSTIVE search at p = 27 (3 free key letters)")
    print("=" * 100)
    t0 = time.time()
    for cb in COMBOS[:6]:
        ex = exhaustive_p27(cb, Q)
        if ex is None:
            print(f"{RK.combo_name(cb):44s} cribs contradictory at p=27")
            continue
        T = dec_table(cb, CT)
        pins = pin_map(cb, 27, CT)
        got = optimise(T, 27, pins, Q, restarts=12, rng=random.Random(1))
        flag = "MATCH" if abs(got[0] - ex[0]) < 1e-9 else f"MISS by {ex[0]-got[0]:.4f}"
        print(f"{RK.combo_name(cb):44s} exhaustive {ex[0]:+.4f}   descent {got[0]:+.4f}   {flag}")
    print(f"({time.time()-t0:.0f}s)")
    print()
    print("=" * 100)
    print("VALIDATION 2 -- synthetic recovery: a REAL periodic key of period p, 24 letters of")
    print("               plaintext revealed at the K4 crib positions.  Can the optimiser find it?")
    print("=" * 100)
    _, _, hold = search_lm.load()
    rnd = random.Random(99)
    cb = ("vigenere", "plain", "plain", "plain")
    print(f"{'p':>3} {'free':>5} {'true score':>11} {'found score':>12} {'key letters right':>18} "
          f"{'plaintext letters right':>24}")
    for p in (27, 29, 33, 40, 47, 53, 60, 75):
        ok_k = ok_p = trials = 0
        for t in range(4):
            i = rnd.randrange(0, len(hold) - 98)
            pt = hold[i:i + 97]
            key = [rnd.randrange(26) for _ in range(p)]
            ct = "".join(A2Z[(ord(pt[j]) - 65 + key[j % p]) % 26] for j in range(97))
            cribs = {pos: pt[pos] for pos in CRIBS}
            T = dec_table(cb, ct)
            pins = pin_map(cb, p, ct, cribs)
            if pins is None:
                continue
            s, k2 = optimise(T, p, pins, Q, restarts=12, rng=random.Random(t))
            got = decrypt_with(T, p, k2)
            ok_k += sum(1 for r in range(p) if k2[r] == key[r])
            ok_p += sum(1 for j in range(97) if got[j] == pt[j])
            trials += 1
            true_s = search_lm.quad(pt)
        if trials:
            print(f"{p:3d} {p-len({q%p for q in CRIBS}):5d} {true_s:+11.4f} {s:+12.4f} "
                  f"{ok_k/trials:10.1f}/{p:<6d} {ok_p/trials:18.1f}/97")
    print()
    print("Read validation 2 as the POWER of this attack: where plaintext recovery is near 97/97")
    print("the test can find a real periodic key; where it is not, a negative means nothing.")

# ------------------------------------------------------------------ run
def run(pmax=57):
    Q = qtab()
    print("=" * 108)
    print("TABLE P1 -- best English score reachable by a periodic key of period p, cribs pinned")
    print("=" * 108)
    print(f"{'p':>3} {'free':>5} {'impossible':>11} {'best quad':>10} {'combo':>40} "
          f"{'null best':>10} {'excess':>8}")
    rows = []
    rnd = random.Random(4242)
    # null ciphertexts: random 97-letter strings, with random 'crib' plaintext letters at the
    # same 24 positions -- same free-parameter count, no real structure.
    NULLCT = []
    for t in range(6):
        ct = "".join(A2Z[rnd.randrange(26)] for _ in range(97))
        NULLCT.append((ct, {pos: A2Z[rnd.randrange(26)] for pos in CRIBS}))
    for p in range(27, pmax + 1):
        best = (-1e9, None, None)
        nimp = 0
        for cb in COMBOS:
            pins = pin_map(cb, p, CT)
            if pins is None:
                nimp += 1
                continue
            T = dec_table(cb, CT)
            s, key = optimise(T, p, pins, Q, restarts=40, rng=random.Random(p * 131 + 7))
            if s > best[0]:
                best = (s, cb, key)
        nb = -1e9
        cbn = ("vigenere", "plain", "plain", "plain")
        for ct, cr in NULLCT:
            pins = pin_map(cbn, p, ct, cr)
            if pins is None:
                continue
            T = dec_table(cbn, ct)
            s, _ = optimise(T, p, pins, Q, restarts=40, rng=random.Random(p * 17 + 3))
            nb = max(nb, s)
        free = p - len({q % p for q in CRIBS})
        rows.append(dict(p=p, free=free, impossible=nimp, best=best[0],
                         combo=RK.combo_name(best[1]) if best[1] else None,
                         key="".join(A2Z[k] for k in best[2]) if best[2] else None,
                         pt=decrypt_with(dec_table(best[1], CT), p, best[2]) if best[1] else None,
                         null=nb))
        print(f"{p:3d} {free:5d} {nimp:8d}/24 {best[0]:+10.4f} "
              f"{RK.combo_name(best[1]) if best[1] else '-':>40} {nb:+10.4f} {best[0]-nb:+8.4f}",
              flush=True)
    print()
    print("Reference: held-out English -0.741+-0.077; Sanborn K1-K3 plaintext -0.967+-0.087;")
    print("crib-pinned random -1.646.  A real periodic key would put the K4 column in the")
    print("Sanborn band AND far above the null column.")
    print()
    print("Best decryptions found (crib letters lower-cased):")
    for r in sorted(rows, key=lambda r: -(r["best"] - r["null"]))[:8]:
        pt = r["pt"]
        print(f"  p={r['p']:2d} {r['combo']:40s} quad {r['best']:+.4f} (null {r['null']:+.4f})")
        print("     key " + r["key"])
        print("     pt  " + "".join(c.lower() if i in CRIBS else c for i, c in enumerate(pt)))
    with open(os.path.join(HERE, "search_periods.json"), "w") as f:
        json.dump(rows, f)
    print()
    print("=" * 108)
    print("Periods above 57 are NOT TESTED and CANNOT BE: with >= 34 free key letters, 26^free")
    print("exceeds the 10^48.3 dilution factor, so chance alone supplies an English-looking")
    print("decryption.  Any 'solution' found there is a fit, not a finding.")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    if mode == "validate":
        validate()
    else:
        run(int(sys.argv[2]) if len(sys.argv) > 2 else 57)
