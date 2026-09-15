"""search_keystream.py -- what key stream does each candidate plaintext imply?

Given a candidate 97-letter K4 plaintext (from search_anneal.py, or supplied on the
command line), derive the key stream under each of the 24 cipher/alphabet combos and
test that stream for:
   * periodicity   (best period 2-48 by residue-class agreement, vs chance)
   * index of coincidence
   * English-likeness (calibrated quadgram score from search_lm.py)
   * substring matches against the sculpture corpus (K1-K3 plaintexts/ciphertexts,
     the panels, the tableau, the Morse text) -- longest common substring >= 5

Usage:
    python3.13 search_keystream.py top [n]        # analyse the n best annealed plaintexts
    python3.13 search_keystream.py text PLAINTEXT # analyse one supplied plaintext
"""
import json, os, re, sys, random
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import search_lm
import runningkey_lib as RK

A2Z = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CT = RK.K4_CT
COMBOS = list(RK.combos())
CORPUS = RK.corpus()

def keystream(cb, pt):
    return "".join(RK.derive_key_letter(cb, p, c) for p, c in zip(pt, CT))

def ioc(s):
    n = len(s); cnt = Counter(s)
    return sum(v * (v - 1) for v in cnt.values()) / (n * (n - 1))

def best_period(s, pmax=48):
    """For each period p, the fraction of letters equal to the modal letter of their
    residue class.  Chance value is roughly (1/26 + ...) ~ depends on class size;
    we return (p, agreement, expected_agreement)."""
    best = None
    for p in range(2, pmax + 1):
        agree = 0
        exp = 0.0
        for r in range(p):
            cls = s[r::p]
            if not cls:
                continue
            m = Counter(cls).most_common(1)[0][1]
            agree += m
            # expected max count of a multinomial(len,1/26) -- Monte-Carlo-free approx:
            exp += expected_modal(len(cls))
        val = agree / len(s)
        e = exp / len(s)
        if best is None or (val - e) > best[1] - best[2]:
            best = (p, val, e)
    return best

_EXP_CACHE = {}
def expected_modal(n, trials=4000):
    if n in _EXP_CACHE:
        return _EXP_CACHE[n]
    if n <= 1:
        _EXP_CACHE[n] = float(n); return float(n)
    rnd = random.Random(99 + n)
    tot = 0
    for _ in range(trials):
        c = Counter(rnd.randrange(26) for _ in range(n))
        tot += c.most_common(1)[0][1]
    v = tot / trials
    _EXP_CACHE[n] = v
    return v

_CORPUS_SETS = None
def corpus_substrings(minlen=5):
    global _CORPUS_SETS
    if _CORPUS_SETS is None:
        d = {}
        for name, t in CORPUS.items():
            for L in range(minlen, minlen + 4):
                for i in range(len(t) - L + 1):
                    d.setdefault(t[i:i + L], name)
        _CORPUS_SETS = d
    return _CORPUS_SETS

def longest_corpus_match(s, minlen=5):
    d = corpus_substrings(minlen)
    best = ("", None)
    for L in range(minlen + 3, minlen - 1, -1):
        for i in range(len(s) - L + 1):
            sub = s[i:i + L]
            if sub in d:
                if len(sub) > len(best[0]):
                    best = (sub, d[sub])
        if best[0]:
            break
    return best

def analyse(pt, label="", verbose=True):
    rows = []
    for cb in COMBOS:
        ks = keystream(cb, pt)
        p, agree, exp = best_period(ks)
        q = search_lm.quad(ks)
        m = longest_corpus_match(ks)
        rows.append(dict(combo=RK.combo_name(cb), key=ks, ioc=ioc(ks), period=p,
                         agree=agree, exp=exp, quad=q, match=m[0], match_src=m[1]))
    if verbose:
        print(f"--- {label}  PT={pt}")
        print(f"    PT quad={search_lm.quad(pt):.4f}")
        print(f"{'combo':44s} {'IoC':>6s} {'p*':>3s} {'agree':>6s} {'exp':>6s} {'quadK':>7s} match")
        for r in sorted(rows, key=lambda r: -r["quad"]):
            print(f"{r['combo']:44s} {r['ioc']:6.4f} {r['period']:3d} {r['agree']:6.3f} "
                  f"{r['exp']:6.3f} {r['quad']:7.3f} {r['match']}"
                  + (f" ({r['match_src']})" if r["match"] else ""))
    return rows

def null_keystream_stats(n=400, seed=5):
    """Chance distribution of the per-keystream statistics: take random 97-letter
    plaintexts (crib letters fixed) and look at the implied streams."""
    import numpy as np
    rnd = random.Random(seed)
    crib = RK.CRIBS
    iocs, quads, gaps, matches = [], [], [], 0
    for _ in range(n):
        pt = "".join(crib.get(i, A2Z[rnd.randrange(26)]) for i in range(97))
        cb = COMBOS[rnd.randrange(len(COMBOS))]
        ks = keystream(cb, pt)
        iocs.append(ioc(ks)); quads.append(search_lm.quad(ks))
        p, a, e = best_period(ks); gaps.append(a - e)
        if longest_corpus_match(ks)[0]:
            matches += 1
    import statistics as st
    return dict(ioc_mean=st.mean(iocs), ioc_sd=st.pstdev(iocs),
                quad_mean=st.mean(quads), quad_sd=st.pstdev(quads),
                gap_mean=st.mean(gaps), gap_sd=st.pstdev(gaps),
                match_rate=matches / n)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "top"
    if mode == "text":
        analyse(re.sub("[^A-Z]", "", sys.argv[2].upper()), "supplied")
    else:
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        with open(os.path.join(HERE, "search_anneal_k4.json")) as f:
            res = json.load(f)
        print("NULL distribution of key-stream statistics (random plaintexts, cribs fixed):")
        ns = null_keystream_stats()
        print("   ", {k: round(v, 4) for k, v in ns.items()})
        print()
        allrows = []
        for s, pt in res[:n]:
            allrows += analyse(pt, f"anneal score {s:.4f}")
            print()
        # aggregate
        print("AGGREGATE over the analysed plaintexts:")
        bq = max(allrows, key=lambda r: r["quad"])
        print(f"   best key-stream quad score: {bq['quad']:.3f}  ({bq['combo']})")
        print(f"   key: {bq['key']}")
        bg = max(allrows, key=lambda r: r["agree"] - r["exp"])
        print(f"   best periodicity excess: {bg['agree']-bg['exp']:.3f} at p={bg['period']} "
              f"({bg['combo']})")
        nm = [r for r in allrows if r["match"]]
        print(f"   key streams with a corpus substring match >= 5: {len(nm)}/{len(allrows)}")
        for r in nm[:10]:
            print(f"      {r['combo']:44s} {r['match']} ({r['match_src']})")
