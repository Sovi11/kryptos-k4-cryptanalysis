"""(B2, exhaustive, keyed alphabets)  Same offset-exhaustive test as
twocipher_B2_offsets.py, but with every distinct keyed alphabet derivable from
/usr/share/dict/words (+ data-file words) in place of plain / KRYPTOS.

Alphabet arrangements per keyed alphabet A:  A/A (Quagmire III, the K1/K2 system),
A-pt/plain-ct (Quagmire I), plain-pt/A-ct (Quagmire II); families vig and beau.

Two crib readings:
  strong : blocks EASTNORTHEAST (13) and BERLINCLOCK (11), one free offset, p = 2..26.
  4-word : EAST / NORTHEAST / BERLIN / CLOCK, three free offsets, p = 2..PMAX4
           (PMAX4 = 16: beyond that the 4-word test has essentially no power once
           ~200k alphabets are tried; the chance-survivor count explodes).

The search per (alphabet, arrangement, family, p) is hierarchical: place block 1 at
offset 0, then try each offset for block 2 against the merged column->shift map,
and so on, rejecting at the first conflict.  Output: survivors with their number
of non-trivial checks, plus the null-expected count for comparison.
"""
import sys, os, json, time
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import twocipher_common as C

PMAX4 = 16
STRONG = [("FLRVQQPRNGKSS", "EASTNORTHEAST"), ("NYPVTTMZFPK", "BERLINCLOCK")]
FOUR = [(ctw, ptw) for _, ctw, ptw, _ in C.CRIB_WORDS]
PLAIN_IDX = {ch: i for i, ch in enumerate(C.PLAIN)}

def alphabets():
    words = C.load_words(minlen=2, maxlen=25)
    seen = set(); out = []
    for w in sorted(words):
        A = C.keyed_alphabet(w)
        if A in seen: continue
        seen.add(A); out.append((w, A))
    return out

def block_shifts(blocks, pidx, cidx, fam):
    """List (per block) of shift lists."""
    res = []
    for ctw, ptw in blocks:
        if fam == "vig":
            res.append([(cidx[c] - pidx[p]) % 26 for c, p in zip(ctw, ptw)])
        else:
            res.append([(cidx[c] + pidx[p]) % 26 for c, p in zip(ctw, ptw)])
    return res

def search(shifts, p):
    """Hierarchical offset search.  Returns list of (offsets, checks) survivors."""
    # block 0 at offset 0
    key = {}
    checks0 = 0
    for k, s in enumerate(shifts[0]):
        col = k % p
        if col in key:
            checks0 += 1
            if key[col] != s: return []
        else:
            key[col] = s
    survivors = []
    def rec(bi, key, offs, checks):
        if bi == len(shifts):
            survivors.append((tuple(offs), checks)); return
        blk = shifts[bi]
        for d in range(p):
            k2 = dict(key); ch = checks; ok = True
            for k, s in enumerate(blk):
                col = (d + k) % p
                if col in k2:
                    ch += 1
                    if k2[col] != s: ok = False; break
                else:
                    k2[col] = s
            if ok:
                rec(bi + 1, k2, offs + [d], ch)
    rec(1, key, [], checks0)
    return survivors

def work(chunk):
    out = []   # (word, arrangement, fam, reading, p, offsets, checks)
    for word, A in chunk:
        aidx = {ch: i for i, ch in enumerate(A)}
        for arr, (pidx, cidx) in (("A/A", (aidx, aidx)), ("Apt/Pct", (aidx, PLAIN_IDX)), ("Ppt/Act", (PLAIN_IDX, aidx))):
            for fam in ("vig", "beau"):
                sh2 = block_shifts(STRONG, pidx, cidx, fam)
                for p in range(2, 27):
                    for offs, ch in search(sh2, p):
                        out.append((word, arr, fam, "strong", p, offs, ch))
                sh4 = block_shifts(FOUR, pidx, cidx, fam)
                for p in range(2, PMAX4 + 1):
                    for offs, ch in search(sh4, p):
                        out.append((word, arr, fam, "4word", p, offs, ch))
    return out

def null_expectation(blocks, pmax, free_reading):
    """Expected survivors per (alphabet, arrangement, family) under the null, per period."""
    import itertools
    exp = {}
    for p in range(2, pmax + 1):
        e = 0.0
        for ds in itertools.product(range(p), repeat=len(blocks) - 1):
            starts = [0] + [ds[i] + 40 * (i + 1) * p for i in range(len(ds))]
            cols = set(); checks = 0
            for (ctw, _), st in zip(blocks, starts):
                for k in range(len(ctw)):
                    c = (st + k) % p
                    if c in cols: checks += 1
                    cols.add(c)
            e += 26.0 ** (-checks)
        exp[p] = e
    return exp

def main():
    t0 = time.time()
    alph = alphabets()
    print(f"{len(alph)} distinct keyed alphabets from dictionary words")
    nproc = os.cpu_count() or 4
    chunks = [alph[i::nproc * 8] for i in range(nproc * 8)]
    results = []
    with Pool(nproc) as pool:
        for r in pool.imap_unordered(work, chunks):
            results.extend(r)
    print(f"search done in {time.time() - t0:.0f}s; {len(results)} raw survivors")
    n_trials = len(alph) * 3 * 2
    exp_s = null_expectation(STRONG, 26, 1)
    exp_4 = null_expectation(FOUR, PMAX4, 3)
    from collections import defaultdict
    hist = defaultdict(lambda: defaultdict(int))   # (reading, p) -> checks -> count
    for word, arr, fam, reading, p, offs, ch in results:
        hist[(reading, p)][ch] += 1
    print("\nSTRONG reading (2 blocks): survivors per period vs null expectation "
          f"({n_trials} alphabet x arrangement x family trials per period)")
    for p in range(2, 27):
        h = hist[("strong", p)]; tot = sum(h.values())
        print(f"  p={p:2d}: observed {tot:8d}  null-expected {n_trials * exp_s[p]:10.1f}  checks-histogram {dict(sorted(h.items()))}")
    print(f"\n4-WORD reading: survivors per period vs null expectation (p <= {PMAX4})")
    for p in range(2, PMAX4 + 1):
        h = hist[("4word", p)]; tot = sum(h.values())
        print(f"  p={p:2d}: observed {tot:8d}  null-expected {n_trials * exp_4[p]:10.1f}  checks-histogram {dict(sorted(h.items()))}")
    # strongest survivors
    results.sort(key=lambda r: (-r[6], r[4]))
    print("\nSurvivors with the most non-trivial checks (top 40):")
    for r in results[:40]:
        print("  ", r)
    # survivors with checks >= 4 in full
    strong_hits = [r for r in results if r[6] >= 4]
    print(f"\nSurvivors with >= 4 checks: {len(strong_hits)}")
    with open(os.path.join(C.HERE, "twocipher_B2_keyed_results.json"), "w") as f:
        json.dump({"n_alphabets": len(alph), "n_raw_survivors": len(results),
                   "hist": {f"{k[0]}-p{k[1]}": dict(v) for k, v in hist.items()},
                   "top": results[:200]}, f)

if __name__ == "__main__":
    main()
