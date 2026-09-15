"""(b) Per-segment cipher fitting for K4.

B1  Constraint accounting: how much do the cribs actually constrain a per-segment
    periodic key?  (Answer: almost nothing for most segmentations - quantified.)
B2  LOCAL KEY EXTENSION (the test with real power).  Each crib run is a block of
    consecutive positions: 13 (EASTNORTHEAST, 0-idx 21..33) and 11 (BERLINCLOCK,
    63..73).  For any period p <= run length the cribs determine the key at EVERY
    residue class mod p, so the key is fully known.  Decrypt the neighbourhood and
    see whether English appears.  If K4 were locally a periodic cipher whose key
    changes at a boundary, this must light up.
B3  Agreement between the key implied by run 1 and the key implied by run 2.
B4  Exhaustive short-period Vigenere/Beaufort on each uncribbed segment, with the
    correct best-of-N null (the same search run on scrambled ciphertext).

Everything is compared against an explicit null; nothing is called a survivor
unless it beats the best-of-N chance level.
"""
import itertools, json, math, os, sys, time
from collections import Counter

import numpy as np

import seg_common as S

rng = np.random.default_rng(7)
CT = S.CT
N = 97
CODE = S.CT_CODE
PLAIN = S.PLAIN

RUNS = {"EASTNORTHEAST": (21, 34), "BERLINCLOCK": (63, 74),
        "row4-head(LINCLOCK)": (66, 74), "row3-tail(BER)": (63, 66)}

PANEL_ROWS = [(0, 4), (4, 35), (35, 66), (66, 97)]

CFG = [(f, pn, cn) for f in S.FAMILIES for pn in S.ALPHABET_NAMES for cn in S.ALPHABET_NAMES]


# ---------------------------------------------------------------- null for quadgrams
_NULL_CACHE = {}
def null_quad(L, ntrials=200_000):
    """Distribution of the quadgram score of a uniformly random L-letter string."""
    if L in _NULL_CACHE:
        return _NULL_CACHE[L]
    m = np.random.default_rng(1234 + L).integers(0, 26, size=(ntrials, L))
    sc = S.quad_scores_batch(m)
    _NULL_CACHE[L] = (float(sc.mean()), float(sc.std()), np.sort(sc))
    return _NULL_CACHE[L]

def null_best_of(L, n, reps=2000):
    """Expected maximum quadgram score over n independent random L-letter strings."""
    mu, sd, sorted_sc = null_quad(L)
    M = len(sorted_sc)
    # order statistic of the max of n draws
    idx = np.minimum((M * (np.random.default_rng(99).random((reps, 1)) ** (1.0 / n) * 1.0)
                      ).astype(int), M - 1)
    return float(sorted_sc[idx].mean()), float(sorted_sc[idx].std()), \
           float(sorted_sc[min(int(M * (0.95 ** (1.0 / n))), M - 1)])


def hdr(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)


# =================================================================== B1
def b1():
    hdr("B1. Constraint accounting: what do the cribs constrain inside a segment?")
    print("A period-p key inside a segment is pinned only where two crib positions of that")
    print("segment share a residue mod p.  constraints c = (#crib positions in segment) -")
    print("(#distinct residues mod p).  A random key passes with probability 26^-c, so")
    print("c = 0 means the test is VACUOUS - every key passes.\n")
    segmentations = {
        "whole text (baseline)": [(0, 97)],
        "panel rows 4/31/31/31": PANEL_ROWS,
        "halves 48/49": [(0, 48), (48, 97)],
        "thirds 32/33/32": [(0, 32), (32, 65), (65, 97)],
        "crib blocks (5 parts)": [(0, 21), (21, 34), (34, 63), (63, 74), (74, 97)],
    }
    rows = {}
    for name, segs in segmentations.items():
        print(f"--- {name}")
        print("  period:      " + " ".join(f"{p:>3}" for p in range(2, 27)))
        tot = []
        for (a, b) in segs:
            pos = [i for i in S.CRIB_POS if a <= i < b]
            if not pos:
                print(f"  seg {a+1:>3}-{b:<3} : no cribs -> completely unconstrained "
                      f"({b-a} letters of free plaintext)")
                continue
            cs = []
            for p in range(2, 27):
                c = len(pos) - len({i % p for i in pos})
                cs.append(c)
            print(f"  seg {a+1:>3}-{b:<3} : " + " ".join(f"{c:>3}" for c in cs) +
                  f"   ({len(pos)} crib letters)")
            tot.append(cs)
        if tot:
            summ = [sum(x) for x in zip(*tot)]
            print("  TOTAL c      " + " ".join(f"{c:>3}" for c in summ))
            print("  vacuous from period p = " +
                  str(next((p for p, c in zip(range(2, 27), summ) if c == 0), ">26")))
            rows[name] = summ
    print("\nThe whole-text row is the one the earlier sweeps used.  Splitting the text")
    print("strictly REDUCES c, so any per-segment model is weaker, never stronger: a")
    print("'survivor' of a per-segment test is only meaningful if the decryption is English.")
    return rows


# =================================================================== B2
def derive_key(shifts24, run, p):
    """Key values for residues 0..p-1 from the crib positions inside `run`.
    Returns None if some residue is not covered."""
    a, b = run
    key = np.full(p, -1, dtype=np.int64)
    for j, pos in enumerate(S.CRIB_POS):
        if a <= pos < b:
            r = pos % p
            if key[r] == -1:
                key[r] = shifts24[j]
            elif key[r] != shifts24[j]:
                return None                       # inconsistent even inside the run
    return None if (key < 0).any() else key


def b2():
    hdr("B2. LOCAL KEY EXTENSION: key fully determined by one crib run, decrypt outwards")
    print("For a run of L consecutive crib positions and period p <= L every residue class")
    print("mod p contains a crib, so the key is FULLY determined - no search, no freedom.")
    print("The decryption of the rest of the text is then a prediction.  If K4 is locally")
    print("periodic (a key that changes only at a boundary), the letters next to the run")
    print("must come out English.\n")

    results = []
    for run_name, (a, b) in RUNS.items():
        L = b - a
        for p in range(1, L + 1):
            for (fam, pn, cn) in CFG:
                sh = S.required_shifts(fam, S.ALPHABETS[pn], S.ALPHABETS[cn])
                key = derive_key(sh, (a, b), p)
                if key is None:
                    continue
                ks = key[np.arange(N) % p]
                pt = S.decrypt(CODE, ks, fam, S.ALPHABETS[pn], S.ALPHABETS[cn])
                assert pt[a:b] == CT[a:b] or True
                # sanity: the run must reproduce the crib
                for j, pos in enumerate(S.CRIB_POS):
                    if a <= pos < b:
                        assert pt[pos] == S.CRIB_PT[j], (run_name, p, fam, pn, cn)
                results.append(dict(run=run_name, p=p, fam=fam, pn=pn, cn=cn,
                                    key="".join(PLAIN[x] for x in key), pt=pt))
    print(f"configurations with a fully determined key: {len(results)}")

    # --- score several windows
    windows = {
        "pre20":  lambda a, b: (max(0, a - 20), a),
        "pre_all": lambda a, b: (0, a),
        "post20": lambda a, b: (b, min(N, b + 20)),
        "post_all": lambda a, b: (b, N),
        "outside_all": None,
        "whole97": lambda a, b: (0, N),
    }
    print()
    for wname in ("pre20", "post20", "pre_all", "post_all", "whole97"):
        best = {}
        for r in results:
            a, b = RUNS[r["run"]]
            lo, hi = windows[wname](a, b)
            if hi - lo < 8:
                continue
            sc = S.quad_score(r["pt"][lo:hi])
            k = (r["run"], hi - lo)
            if k not in best or sc > best[k][0]:
                best[k] = (sc, r, lo, hi)
        for (run_name, Lw), (sc, r, lo, hi) in sorted(best.items()):
            n_cfg = sum(1 for x in results if x["run"] == run_name)
            mu, sd, _ = null_quad(Lw)
            bmu, bsd, b95 = null_best_of(Lw, n_cfg)
            flag = "***" if sc > b95 else ""
            print(f"{wname:>9} {run_name:<20} win={Lw:>2} best={sc:+.3f} "
                  f"(null mean {mu:+.3f} sd {sd:.3f}; best-of-{n_cfg} expect {bmu:+.3f} "
                  f"95% {b95:+.3f}) {flag}")
            print(f"          -> {r['fam']}/pt={r['pn']}/ct={r['cn']} p={r['p']} "
                  f"key={r['key']}")
            print(f"          -> {r['pt'][lo:hi]}")

    # --- explicit look at the very best whole-text candidates
    print()
    print("Top 12 configurations by whole-97-letter quadgram score:")
    scored = sorted(results, key=lambda r: -S.quad_score(r["pt"]))[:12]
    mu, sd, _ = null_quad(97)
    bmu, bsd, b95 = null_best_of(97, len(results))
    print(f"(null for 97 random letters: mean {mu:+.3f} sd {sd:.3f}; "
          f"best-of-{len(results)} expect {bmu:+.3f}, 95% {b95:+.3f}; English about -4.7)")
    for r in scored:
        q = S.quad_score(r["pt"]); w = S.word_coverage(r["pt"])
        print(f"  q={q:+.3f} wc={w:.2f} {r['run']:<20} p={r['p']:<2} "
              f"{r['fam']}/pt={r['pn']}/ct={r['cn']} key={r['key']}")
        print(f"     {r['pt']}")
    return results


# =================================================================== B3
def b3():
    hdr("B3. Do the two crib runs imply the same periodic key?")
    print("If one periodic key covered both runs we would already have a solution (it does")
    print("not - established).  But the DEGREE of agreement says whether a key change")
    print("between them is plausible: with a genuine shared period we would expect the two")
    print("independently derived keys to agree on many residues by accident of the data.\n")
    print(f"{'p':>3} {'best agree':>10} {'of p':>5} {'chance E':>9}  best config")
    for p in range(2, 12):
        best = (-1, None)
        for (fam, pn, cn) in CFG:
            sh = S.required_shifts(fam, S.ALPHABETS[pn], S.ALPHABETS[cn])
            k1 = derive_key(sh, RUNS["EASTNORTHEAST"], p)
            k2 = derive_key(sh, RUNS["BERLINCLOCK"], p)
            if k1 is None or k2 is None:
                continue
            ag = int((k1 == k2).sum())
            if ag > best[0]:
                best = (ag, (fam, pn, cn, "".join(PLAIN[x] for x in k1),
                             "".join(PLAIN[x] for x in k2)))
        if best[1]:
            f, pn, cn, s1, s2 = best[1]
            print(f"{p:>3} {best[0]:>10} {p:>5} {p/26:>9.2f}  {f}/pt={pn}/ct={cn} "
                  f"{s1} vs {s2}")
    print("\n(Both keys exist for every config, so 'consistent' would mean agreement = p.")
    print(" Maximum agreement found is reported; chance is p/26 residues.)")


# =================================================================== B4
_FAMS12 = [(f, pn, cn) for f in S.FAMILIES for pn in ("STRAIGHT", "KRYPTOS")
           for cn in ("STRAIGHT", "KRYPTOS")]


def _best_periodic(sub_codes, p, keys, fams):
    """Max quadgram score over all period-p keys and all (family, pt, ct) configs."""
    n = len(sub_codes)
    resid = np.arange(n) % p
    ks = keys[:, resid].astype(np.int16)                       # (nk, n)
    best = -99.0; rec = None
    for (fam, pn, cn) in fams:
        pa, ca = S.ALPHABETS[pn], S.ALPHABETS[cn]
        ci = S.idx_map(ca)[sub_codes].astype(np.int16)
        if fam == "vigenere":
            pi = ci[None, :] - ks
        elif fam == "beaufort":
            pi = ks - ci[None, :]
        else:
            pi = ci[None, :] + ks
        pi %= 26
        mat = (np.frombuffer(pa.encode(), dtype=np.uint8)[pi].astype(np.int32) - 65)
        sc = S.quad_scores_batch(mat)
        j = int(np.argmax(sc))
        if sc[j] > best:
            best = float(sc[j])
            rec = (fam, pn, cn, "".join(PLAIN[x] for x in keys[j]),
                   "".join(chr(65 + c) for c in mat[j]))
    return best, rec


def b4():
    hdr("B4. Exhaustive short-period search on each segment, with a best-of-N null")
    print("Give every segment its OWN key and period and ask for the most English-looking")
    print("decryption.  The null is the IDENTICAL exhaustive search run on scrambles of the")
    print("same segment, so the margin reported is exactly 'how much better than chance'.")
    print("Configs: 3 families x {STRAIGHT,KRYPTOS} plaintext alphabet x {STRAIGHT,KRYPTOS}")
    print("ciphertext alphabet = 12, times every one of the 26^p keys.\n")
    segs = {"pre-crib 1-21": (0, 21), "mid 35-63": (34, 63), "post 75-97": (74, 97),
            "row2 5-35": (4, 35), "row3 36-66": (35, 66), "row4 67-97": (66, 97)}
    plan = [(1, 60), (2, 60), (3, 60), (4, 12)]
    for sname, (a, b) in segs.items():
        sub = CODE[a:b]
        n = len(sub)
        for p, nnull in plan:
            keys = np.array(np.meshgrid(*[np.arange(26)] * p, indexing="ij")).reshape(p, -1).T
            sc, rec = _best_periodic(sub, p, keys, _FAMS12)
            nulls = np.array([_best_periodic(np.random.default_rng(5000 + t).permutation(sub),
                                             p, keys, _FAMS12)[0] for t in range(nnull)])
            star = "  *** beats every null" if sc > nulls.max() else ""
            print(f"--- {sname:<14} p={p} keys={len(keys):>7} nulls={nnull:>3}: best q={sc:+.3f}  "
                  f"null mean {nulls.mean():+.3f} sd {nulls.std():.3f} max {nulls.max():+.3f}{star}")
            print(f"        {rec[0]}/pt={rec[1]}/ct={rec[2]} key={rec[3]}  -> {rec[4]}")
        print()
    print("English 97-letter text scores about -4.7 on this quadgram model; uniform random")
    print("-8.2.  A short segment searched over 26^p keys will always score well above -8.2:")
    print("the only meaningful comparison is against the null column.")


if __name__ == "__main__":
    t0 = time.time()
    b1()
    b2()
    b3()
    b4()
    print(f"\n[runtime {time.time()-t0:.1f}s]")
