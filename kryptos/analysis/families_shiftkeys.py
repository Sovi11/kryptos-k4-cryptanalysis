"""Shift-key families against the K4 cribs:
  * Porta (13 reciprocal alphabets, standard and Bellaso-variant tables; straight and KRYPTOS order)
  * Gronsfeld (digit keys 0-9, periods 2-26; Vigenere / Beaufort / variant-Beaufort; straight + KRYPTOS)
  * Trithemius / progressive key, letter-wise:  shift_i = a + b*i
  * Periodic key with progressive increment per period: shift_i = key[i mod p] + b*floor(i/p)
  * Periodic key with progressive increment per letter: shift_i = key[i mod p] + b*i
  * Bonus: plaintext-autokey and ciphertext-autokey with primer length 1..96

All "shift" ciphers are reduced to the required key value at each crib position and a
consistency test.  Modes:
  vig      c = p + k      -> k = c - p
  beau     c = k - p      -> k = c + p
  varbeau  c = p - k      -> k = p - c   (same periodicity as vig; matters only for Gronsfeld digit range)
Alphabets: straight A..Z and the KRYPTOS keyed alphabet (indices taken in that alphabet).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from k4_common import (A2Z, KRYPTOS_ALPHA, CT, CRIB, CRIB_POS, CRIB_CT, CRIB_PT, ROOT,
                       period_pairs, constraints_per_period, bigram_score, mark_cribs, noncrib)

ALPHAS = {"straight": A2Z, "kryptos": KRYPTOS_ALPHA}
MODES = ["vig", "beau", "varbeau"]
RESULTS = {}


def required_shifts(alpha, mode):
    inv = {ch: i for i, ch in enumerate(alpha)}
    out = []
    for c, p in zip(CRIB_CT, CRIB_PT):
        ci, pi = inv[c], inv[p]
        if mode == "vig":
            out.append((ci - pi) % 26)
        elif mode == "beau":
            out.append((ci + pi) % 26)
        else:
            out.append((pi - ci) % 26)
    return out


def periodic(shifts, period):
    return all(shifts[a] == shifts[b] for a, b in period_pairs(period))


def decrypt_shift(alpha, mode, shift_fn):
    inv = {ch: i for i, ch in enumerate(alpha)}
    out = []
    for i, c in enumerate(CT):
        k = shift_fn(i)
        if k is None:
            out.append("?")
            continue
        ci = inv[c]
        if mode == "vig":
            out.append(alpha[(ci - k) % 26])
        elif mode == "beau":
            out.append(alpha[(k - ci) % 26])
        else:
            out.append(alpha[(ci + k) % 26])
    return "".join(out)


# ---------------------------------------------------------------- Porta
def porta_section():
    print("=" * 70)
    print("PORTA")
    res = {}
    for aname, alpha in ALPHAS.items():
        inv = {ch: i for i, ch in enumerate(alpha)}
        same_half = [(CRIB_POS[k] + 1, c, p) for k, (c, p) in enumerate(zip(CRIB_CT, CRIB_PT))
                     if (inv[c] < 13) == (inv[p] < 13)]
        print(f"[{aname} alphabet] crib pairs with cipher and plain letter in the SAME half "
              f"(impossible for any Porta row): {len(same_half)}/24")
        print("   ", ", ".join(f"{pos}:{c}->{p}" for pos, c, p in same_half))
        res[aname] = {"same_half_pairs": same_half}
        for variant in ("standard", "bellaso"):
            allowed = []
            for c, p in zip(CRIB_CT, CRIB_PT):
                ci, pi = inv[c], inv[p]
                ks = set()
                for k in range(13):
                    if variant == "standard":
                        e = 13 + (pi + k) % 13 if pi < 13 else (pi - 13 - k) % 13
                    else:
                        e = 13 + (pi - k) % 13 if pi < 13 else (pi - 13 + k) % 13
                    if e == ci:
                        ks.add(k)
                allowed.append(ks)
            n_empty = sum(1 for s in allowed if not s)
            surv = []
            for p in range(2, 27):
                ok = True
                for a, b in period_pairs(p):
                    if not (allowed[a] & allowed[b]):
                        ok = False
                        break
                if ok and n_empty == 0:
                    surv.append(p)
            print(f"   {variant:8s} table: positions with NO valid key row = {n_empty}; periods 2-26 consistent: {surv or 'none'}")
            res[aname][variant] = {"positions_with_no_row": n_empty, "surviving_periods": surv}
    print("Note: Porta never maps a letter to itself, and the cribs contain S->S (pos 33) and K->K (pos 74),")
    print("      so Porta is ruled out for EVERY 26-letter alphabet ordering, not only the two tested.")
    RESULTS["porta"] = res


# ---------------------------------------------------------------- Gronsfeld
def gronsfeld_section():
    print("=" * 70)
    print("GRONSFELD (key digits 0-9)")
    res = {}
    for aname, alpha in ALPHAS.items():
        for mode in MODES:
            s = required_shifts(alpha, mode)
            over = [(CRIB_POS[k] + 1, s[k]) for k in range(24) if s[k] > 9]
            surv = [p for p in range(2, 27) if periodic(s, p)] if not over else []
            print(f"[{aname:8s} {mode:7s}] required shifts: {s}")
            print(f"     positions needing shift > 9: {len(over)}/24 -> {'ruled out' if over else 'digit-compatible'};"
                  f" periodic fits 2-26: {surv or 'none'}")
            res[f"{aname}/{mode}"] = {"shifts": s, "n_over_9": len(over), "surviving_periods": surv}
    RESULTS["gronsfeld"] = res


# ---------------------------------------------------------------- Trithemius / progressive
def trithemius_section():
    print("=" * 70)
    print("TRITHEMIUS / PROGRESSIVE KEY, letter-wise: shift_i = a + b*i (mod 26), i = 0-based position")
    res = {}
    total = 0
    for aname, alpha in ALPHAS.items():
        for mode in ("vig", "beau"):
            s = required_shifts(alpha, mode)
            surv = []
            for a in range(26):
                for b in range(26):
                    total += 1
                    if all((a + b * pos) % 26 == s[k] for k, pos in enumerate(CRIB_POS)):
                        surv.append((a, b))
            # how far can any (a,b) get? report best partial agreement for context
            best = max(((sum(1 for k, pos in enumerate(CRIB_POS) if (a + b * pos) % 26 == s[k]), a, b)
                        for a in range(26) for b in range(26)))
            print(f"[{aname:8s} {mode:4s}] exact fits: {surv or 'none'};  best partial agreement {best[0]}/24 at (a,b)=({best[1]},{best[2]})")
            res[f"{aname}/{mode}"] = {"fits": surv, "best_partial": best}
    print(f"(a,b) pairs tested: {total}")
    RESULTS["trithemius"] = res


def progressive_periodic_section():
    print("=" * 70)
    print("PERIODIC KEY + PROGRESSIVE INCREMENT")
    print("  (A) shift_i = key[i mod p] + b*floor(i/p)   -- alphabet advances by b after every period")
    print("  (B) shift_i = key[i mod p] + b*i            -- alphabet advances by b after every letter")
    res = {"A": [], "B": []}
    tested = 0
    for aname, alpha in ALPHAS.items():
        for mode in ("vig", "beau"):
            s = required_shifts(alpha, mode)
            for p in range(2, 27):
                for b in range(26):
                    for variant in ("A", "B"):
                        tested += 1
                        if variant == "A":
                            adj = [(s[k] - b * (pos // p)) % 26 for k, pos in enumerate(CRIB_POS)]
                        else:
                            adj = [(s[k] - b * pos) % 26 for k, pos in enumerate(CRIB_POS)]
                        if periodic(adj, p):
                            key = {}
                            for k, pos in enumerate(CRIB_POS):
                                key[pos % p] = adj[k]
                            if variant == "A":
                                fn = lambda i, key=key, p=p, b=b: (key[i % p] + b * (i // p)) % 26 if i % p in key else None
                            else:
                                fn = lambda i, key=key, p=p, b=b: (key[i % p] + b * i) % 26 if i % p in key else None
                            dec = decrypt_shift(alpha, mode, fn)
                            sc = bigram_score(noncrib(dec) if p <= 13 else dec)
                            res[variant].append({"alpha": aname, "mode": mode, "period": p, "b": b,
                                                 "constraints": constraints_per_period(p),
                                                 "bigram_score": sc, "decrypt": mark_cribs(dec)})
    print(f"(alphabet, mode, period, b, variant) combinations tested: {tested}")
    for variant in ("A", "B"):
        recs = sorted(res[variant], key=lambda r: (r["period"], -r["bigram_score"]))
        strong = [r for r in recs if r["constraints"] >= 5]
        weak = [r for r in recs if r["constraints"] < 5]
        print(f"  variant {variant}: {len(recs)} consistent (alpha,mode,p,b); with >=5 constraints: {len(strong)}; "
              f"weak (period 25/26, 1-3 constraints, chance expected {4*26*2*26.0**-1 + 4*26*26.0**-3:.1f}): {len(weak)}")
        for r in strong:
            print(f"     STRONG  {r['alpha']:8s} {r['mode']:4s} p={r['period']:2d} b={r['b']:2d} score={r['bigram_score']:.3f} {r['decrypt']}")
        for r in weak:
            if r["b"] == 0:
                tag = "(b=0: plain periodic; already excluded by prior work at this period only if constraints were strong)"
            else:
                tag = ""
            print(f"     weak    {r['alpha']:8s} {r['mode']:4s} p={r['period']:2d} b={r['b']:2d} score={r['bigram_score']:.3f} {r['decrypt']} {tag}")
    RESULTS["progressive_periodic"] = res


# ---------------------------------------------------------------- autokey (bonus)
def autokey_section():
    print("=" * 70)
    print("AUTOKEY (bonus): primer length L = 1..96")
    res = {"plaintext_autokey": [], "ciphertext_autokey": []}
    for aname, alpha in ALPHAS.items():
        inv = {ch: i for i, ch in enumerate(alpha)}
        for mode in ("vig", "beau"):
            # plaintext autokey: key_i = p_{i-L}; both p_i and p_{i-L} must be crib letters
            for L in range(1, 97):
                checks = 0
                bad = 0
                for i in CRIB_POS:
                    j = i - L
                    if j in CRIB:
                        checks += 1
                        ci, pi, kj = inv[CT[i]], inv[CRIB[i]], inv[CRIB[j]]
                        exp = (pi + kj) % 26 if mode == "vig" else (kj - pi) % 26
                        if exp != ci:
                            bad += 1
                if checks and bad == 0:
                    res["plaintext_autokey"].append({"alpha": aname, "mode": mode, "L": L, "checks": checks})
            # ciphertext autokey: key_i = c_{i-L} (known); p_i = c_i - c_{i-L} (vig) or c_{i-L} - c_i (beau)
            for L in range(1, 97):
                checks = 0
                bad = 0
                for i in CRIB_POS:
                    j = i - L
                    if j >= 0:
                        checks += 1
                        ci, cj, pi = inv[CT[i]], inv[CT[j]], inv[CRIB[i]]
                        got = (ci - cj) % 26 if mode == "vig" else (cj - ci) % 26
                        if got != pi:
                            bad += 1
                if checks and bad == 0:
                    res["ciphertext_autokey"].append({"alpha": aname, "mode": mode, "L": L, "checks": checks})
    for k, v in res.items():
        print(f"  {k}: consistent primer lengths: {v or 'none'}")
    print("  (plaintext autokey can only be checked for L where two crib letters are L apart: L=1..12 and 30..52;")
    print("   ciphertext autokey is checkable at every crib position with i-L >= 0.)")
    RESULTS["autokey"] = res


if __name__ == "__main__":
    porta_section()
    gronsfeld_section()
    trithemius_section()
    progressive_periodic_section()
    autokey_section()
    with open(os.path.join(ROOT, "findings", "shiftkeys_results.json"), "w") as f:
        json.dump(RESULTS, f, indent=1, default=str)
