"""search_solvekryptos.py -- falsifiable test of the plaintext claimed publicly by
solvekryptos.com:

  THE COMPASS ROSE IS HERE X EAST NORTHEAST THIS IS YOUR POSITION X COMMISSION
  BERLIN CLOCK WHICH IS NORTHEAST OF HERE X

Checks: (1) length == 97, (2) the four Sanborn cribs land at 22-25, 26-34, 64-69,
70-74, (3) calibrated language-model score vs the calibration distributions,
(4) the key stream it implies under each of the 24 cipher/alphabet combos, and
whether that stream has any structure at all (periodicity, IoC, English-likeness,
matches against the sculpture corpus, arithmetic structure of the shift sequence).

Usage: python3.13 search_solvekryptos.py
"""
import os, re, sys, random
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import search_lm, search_keystream as SK
import runningkey_lib as RK

A2Z = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CT = RK.K4_CT

CLAIM_RAW = ("THE COMPASS ROSE IS HERE X EAST NORTHEAST THIS IS YOUR POSITION X "
             "COMMISSION BERLIN CLOCK WHICH IS NORTHEAST OF HERE X")
CLAIM = re.sub("[^A-Z]", "", CLAIM_RAW.upper())

def crib_check(pt):
    ok = True
    for cr in [(22, "EAST"), (26, "NORTHEAST"), (64, "BERLIN"), (70, "CLOCK")]:
        pos, word = cr
        got = pt[pos - 1: pos - 1 + len(word)]
        good = got == word
        ok &= good
        print(f"   crib {word:10s} at 1-indexed {pos:2d}-{pos+len(word)-1:2d}: "
              f"claim has {got!r}  {'OK' if good else 'MISMATCH'}")
    return ok

def shift_structure(ks, cb):
    """Are the implied shifts an arithmetic/low-order sequence?"""
    fam, ap, ac, ak = cb
    Ak = RK.ALPHAS[ak]
    sh = [Ak.index(c) for c in ks]
    d1 = [(sh[i+1] - sh[i]) % 26 for i in range(len(sh) - 1)]
    c1 = Counter(d1).most_common(1)[0]
    return dict(n_distinct=len(set(sh)), modal_first_diff=c1[0], modal_count=c1[1],
                mean=sum(sh) / len(sh), max_run=max_run(sh))

def max_run(seq):
    best = cur = 1
    for i in range(1, len(seq)):
        cur = cur + 1 if seq[i] == seq[i-1] else 1
        best = max(best, cur)
    return best

def words_in(s, minlen=5):
    words = set()
    try:
        with open("/usr/share/dict/words") as f:
            for w in f:
                w = w.strip().upper()
                if len(w) >= minlen and w.isalpha():
                    words.add(w)
    except FileNotFoundError:
        pass
    found = []
    for L in range(minlen, 12):
        for i in range(len(s) - L + 1):
            if s[i:i+L] in words:
                found.append((i + 1, s[i:i+L]))
    return found

def main():
    print("=" * 78)
    print("solvekryptos.com claimed plaintext")
    print("=" * 78)
    print(f"raw   : {CLAIM_RAW}")
    print(f"letters: {CLAIM}")
    print(f"length : {len(CLAIM)}  (K4 is 97)  -> {'MATCH' if len(CLAIM)==97 else 'MISMATCH'}")
    crib_check(CLAIM)
    print()
    q = search_lm.quad(CLAIM); p = search_lm.pent(CLAIM)
    print(f"language model: quad {q:.4f}   pent(interpolated 5-gram) {p:.4f}")
    print("   (held-out English 97-grams: mean -0.741 sd 0.077; K2/K3 plaintext ~ -0.93 to -0.98;")
    print("    uniform random: -1.81.  Annealed-to-fit English: about -0.68.)")
    print()
    print("Key streams implied by the claim, per cipher/alphabet combo:")
    rows = SK.analyse(CLAIM, "solvekryptos claim", verbose=True)
    print()
    print("Structure of the implied shift sequences:")
    print(f"{'combo':44s} {'distinct':>8s} {'modal d1':>8s} {'count':>5s} {'maxrun':>6s} "
          f"{'words>=5 in key'}")
    for cb, r in zip(SK.COMBOS, rows):
        st = shift_structure(r["key"], cb)
        w = words_in(r["key"])
        print(f"{RK.combo_name(cb):44s} {st['n_distinct']:8d} {st['modal_first_diff']:8d} "
              f"{st['modal_count']:5d} {st['max_run']:6d} {w if w else ''}")
    print()
    # how do these compare with a null: key streams from random 97-letter plaintexts
    print("NULL for the same statistics (random plaintexts with the cribs fixed, 400 draws):")
    ns = SK.null_keystream_stats(400)
    print("   ", {k: round(v, 4) for k, v in ns.items()})
    print()
    # Is the claim's score better than what annealing reaches unconstrained?
    print("Dictionary words (>=5) in the claim outside the cribs:", words_in(CLAIM))

if __name__ == "__main__":
    main()
