"""Digraphic / fractionating families: Playfair, two-square, four-square, bifid, trifid.

Structural checks first (letter inventory, parity, self-mapping, doubled digraphs),
then brute-force decryption of bifid (5x5 with I/J merged, 6x6 with digits) and trifid
(27 symbols) with keyword-mixed squares/cubes, periods 2..30, scored by crib agreement.
"""
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from k4_common import A2Z, CT, CRIB, CRIB_POS, SHORT_KEYWORDS, ROOT, keyed_alphabet, mark_cribs

RESULTS = {}


def structural_section():
    print("=" * 70)
    print("STRUCTURAL CHECKS")
    letters = sorted(set(CT))
    print(f"distinct ciphertext letters: {len(letters)}  (J occurs {CT.count('J')}x at 1-indexed positions {[i+1 for i,c in enumerate(CT) if c=='J']})")
    print("-> every 25-letter-square cipher (Playfair, two-square, four-square, 5x5 bifid, 5x5 Polybius-based)")
    print("   can only emit 25 distinct letters; K4 uses all 26. Ruled out unless the sculpture text has an error.")
    print(f"length 97 is odd -> Playfair/two-square/four-square would need a null appended (98) or a leading/trailing")
    print("   letter that is not part of the digraph stream; no such padding convention is evident.")
    selfmap = [(i + 1, CT[i], CRIB[i]) for i in CRIB_POS if CT[i] == CRIB[i]]
    print(f"crib positions where ciphertext letter == plaintext letter: {selfmap}")
    print("-> Playfair never encrypts a letter to itself: ruled out independently of the square.")
    print("   (two-square and four-square CAN map a letter to itself, so this does not touch them.)")
    for parity in (0, 1):
        pairs = [(i, i + 1) for i in range(parity, 96, 2)]
        doubled_ct = [(a + 1, CT[a:a + 2]) for a, b in pairs if CT[a] == CT[b]]
        in_crib = [(a + 1, CT[a:a + 2], CRIB.get(a, "?") + CRIB.get(b, "?")) for a, b in pairs
                   if CT[a] == CT[b] and (a in CRIB or b in CRIB)]
        print(f"digraph alignment starting at 1-indexed position {parity+1}: doubled CT digraphs {doubled_ct}; inside cribs: {in_crib}")
    print("-> Playfair cannot produce a doubled ciphertext digraph; alignment starting at position 2 has QQ->NO and TT->IN.")
    RESULTS["structural"] = {"distinct_letters": len(letters), "self_map": selfmap}


# ---------------------------------------------------------------- bifid
def bifid_decrypt(ct, square, period, side):
    pos = {ch: (i // side, i % side) for i, ch in enumerate(square)}
    out = []
    for start in range(0, len(ct), period):
        blk = ct[start:start + period]
        n = len(blk)
        seq = []
        for ch in blk:
            seq.extend(pos[ch])
        rows = seq[:n]
        cols = seq[n:]
        # In bifid, the row digits of the block occupy the first n coordinates written out row-wise:
        # encryption wrote rows then columns, then read pairs; decryption reverses that.
        # Standard: the ciphertext coordinates are read off in sequence (r1c1 r2c2...), giving 2n numbers;
        # the first n are the plaintext rows, the last n the plaintext columns.
        for r, c in zip(rows, cols):
            out.append(square[r * side + c])
    return "".join(out)


def crib_matches(pt):
    return sum(1 for i in CRIB_POS if i < len(pt) and pt[i] == CRIB[i])


def bifid_section():
    print("=" * 70)
    print("BIFID")
    res = []
    keywords = ["KRYPTOS"] + [k for k in SHORT_KEYWORDS if k != "KRYPTOS"]
    # 5x5, I/J merged.  K4 contains J, so J is mapped onto I *as a tolerance* (this is already a violation).
    ct25 = CT.replace("J", "I")
    for kw in keywords:
        sq = keyed_alphabet(kw, "ABCDEFGHIKLMNOPQRSTUVWXYZ")
        best = (0, None, None)
        for period in range(2, 31):
            pt = bifid_decrypt(ct25, sq, period, 5)
            m = crib_matches(pt)
            if m > best[0]:
                best = (m, period, pt)
        res.append({"square": "5x5", "keyword": kw, "best_crib_matches": best[0], "period": best[1], "decrypt": mark_cribs(best[2])})
    print("5x5 square (I/J merged; J in ciphertext treated as I), periods 2-30, best crib agreement per keyword:")
    for r in res:
        print(f"   {r['keyword']:12s} best {r['best_crib_matches']:2d}/24 at period {r['period']:2d}: {r['decrypt']}")
    # 6x6 with digits: keyword, remaining letters, digits 0-9
    res6 = []
    for kw in keywords:
        sq = keyed_alphabet(kw) + "0123456789"
        best = (0, None, None)
        for period in range(2, 31):
            pt = bifid_decrypt(CT, sq, period, 6)
            m = crib_matches(pt)
            if m > best[0]:
                best = (m, period, pt)
        res6.append({"square": "6x6", "keyword": kw, "best_crib_matches": best[0], "period": best[1], "decrypt": mark_cribs(best[2])})
    print("6x6 square (A-Z keyed + 0-9), periods 2-30, best crib agreement per keyword:")
    for r in res6:
        print(f"   {r['keyword']:12s} best {r['best_crib_matches']:2d}/24 at period {r['period']:2d}: {r['decrypt']}")
    print("   (chance agreement per crib letter ~1/25 or 1/36; 24 letters -> about 1 match expected; a real fit gives 24/24)")
    RESULTS["bifid"] = res + res6


# ---------------------------------------------------------------- trifid
def trifid_decrypt(ct, cube, period):
    pos = {ch: (i // 9, (i // 3) % 3, i % 3) for i, ch in enumerate(cube)}
    out = []
    for start in range(0, len(ct), period):
        blk = ct[start:start + period]
        n = len(blk)
        seq = []
        for ch in blk:
            seq.extend(pos[ch])
        a, b, c = seq[:n], seq[n:2 * n], seq[2 * n:]
        for x, y, z in zip(a, b, c):
            out.append(cube[x * 9 + y * 3 + z])
    return "".join(out)


def trifid_section():
    print("=" * 70)
    print("TRIFID (27 symbols: keyed A-Z + '#')")
    res = []
    keywords = ["KRYPTOS"] + [k for k in SHORT_KEYWORDS if k != "KRYPTOS"]
    for kw in keywords:
        for extra_pos in ("end", "start"):
            cube = keyed_alphabet(kw) + "#" if extra_pos == "end" else "#" + keyed_alphabet(kw)
            best = (0, None, None)
            for period in range(2, 31):
                pt = trifid_decrypt(CT, cube, period)
                m = crib_matches(pt)
                if m > best[0]:
                    best = (m, period, pt)
            res.append({"keyword": kw, "extra": extra_pos, "best_crib_matches": best[0], "period": best[1], "decrypt": mark_cribs(best[2])})
    for r in res:
        print(f"   {r['keyword']:12s} #{r['extra']:5s} best {r['best_crib_matches']:2d}/24 at period {r['period']:2d}: {r['decrypt']}")
    RESULTS["trifid"] = res


if __name__ == "__main__":
    structural_section()
    bifid_section()
    trifid_section()
    with open(os.path.join(ROOT, "findings", "digraphic_results.json"), "w") as f:
        json.dump(RESULTS, f, indent=1)
