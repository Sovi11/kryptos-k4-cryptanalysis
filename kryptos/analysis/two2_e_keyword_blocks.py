"""(e) Per-block keyword test for the forced key streams of (a) and (d).

Why this exists.  two2_a scores the forced key stream as one object (the 13
quadgrams of block 1 plus the 11 of block 2).  Calibration shows that test is
strong when *both* blocks are meaningful --

    PALIMPSESTABS / CISSAKRYPTO   -5.96
    ABSCISSAPALIM / PSESTKRYPTOS  -6.09
    THEQUICKBROWN / FOXJUMPSOVE   -6.33
    XQZPALIMPSEST / QJXBERLINCLO  -6.47      (observed maximum over 17.4M: -6.70)

-- but weak when only one block is:

    ZQXPALIMPSEST / ZQXWJVBKMQP   -7.56      (deep inside the noise)

So a scheme whose key happens to put a real keyword under EASTNORTHEAST and
something unrelated under BERLINCLOCK would slip through.  This script closes
that hole with a test that has no such blind spot: for each block separately, is
any substring of length 8..13 an English dictionary word (or a Kryptos keyword)?
Chance is computed per length from the number of words of that length.

Sources tested: the 726,578 distinct crib images of the transposition catalogue
(same as two2_a) and the 1,327,758 distinct crib signatures of the 2,449,225
two-transposition compositions (same as two2_d).
"""
import os, sys, time, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import two2_lib as L
import runningkey_lib as RK
import twocipher_common as TC

OUT = os.path.join(HERE, "two2_e_output.txt")
RES = os.path.join(HERE, "two2_e_results.json")
_fh = open(OUT, "w")
def say(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True); _fh.write(s + "\n"); _fh.flush()

LMIN, LMAX = 8, 13
BLOCKS = [(0, 13, "EASTNORTHEAST block"), (13, 11, "BERLINCLOCK block")]

def word_tables():
    words = TC.load_words(minlen=LMIN, maxlen=LMAX)
    tabs = {}
    for Lw in range(LMIN, LMAX + 1):
        ws = sorted(w for w in words if len(w) == Lw)
        codes = np.zeros(len(ws), dtype=np.int64)
        for i, w in enumerate(ws):
            c = 0
            for ch in w:
                c = c * 26 + (ord(ch) - 65)
            codes[i] = c
        tabs[Lw] = (np.unique(codes), ws)
    return tabs

def in_sorted(vals, arr):
    i = np.clip(np.searchsorted(arr, vals), 0, len(arr) - 1)
    return arr[i] == vals

def quad_one_block(keys, lo, Lb):
    Q = L.quad_array()
    blk = keys[:, lo:lo + Lb].astype(np.int64)
    code = (blk[:, 0:Lb - 3] * 26 ** 3 + blk[:, 1:Lb - 2] * 26 ** 2
            + blk[:, 2:Lb - 1] * 26 + blk[:, 3:Lb])
    return Q[code].sum(axis=1) / (Lb - 3)

def source_catalogue():
    Tj, Tic, desc = L.load_transposition_catalogue(verbose=False)
    uniq, inv = np.unique(Tj.astype(np.int16), axis=0, return_index=True)
    return uniq, [desc[int(i)] for i in inv], "transposition catalogue (two2_a)"

def source_compositions():
    import two2_d_double_transposition as D
    fam = D.base_family()
    nb = len(fam)
    Tm = np.array([T for _, T in fam], dtype=np.int16)
    cp = np.array(L.CRIB_POS, dtype=np.int64)
    sig = np.empty((nb * nb, 24), dtype=np.int16)
    for i1 in range(nb):
        sig[i1 * nb:(i1 + 1) * nb] = Tm[:, Tm[i1][cp]]
    uniq, first = np.unique(sig, axis=0, return_index=True)
    names = [f"T1={fam[int(r) // nb][0]} | T2={fam[int(r) % nb][0]}" for r in first]
    return uniq, names, f"{nb*nb:,} two-transposition compositions (two2_d)"

def run(uniq, names, label, tabs, results):
    t0 = time.time()
    m = uniq.shape[0]
    INTER = L.CT_CODES[uniq.astype(np.int64)].astype(np.int16)
    say(f"\n=== source: {label} ===")
    say(f"  {m:,} distinct crib signatures x 24 combos = {m*24:,} forced key streams")
    # chance per length
    say("  chance expectation for 'some substring of this length is a dictionary word':")
    exp_total = 0.0
    for Lw in range(LMIN, LMAX + 1):
        nw = len(tabs[Lw][0])
        npos = sum(max(0, Lb - Lw + 1) for _, Lb, _ in BLOCKS)
        e = m * 24 * npos * nw / 26.0 ** Lw
        exp_total += e
        say(f"    len {Lw}: {nw:>6,} distinct words, {npos} substring positions "
            f"-> {e:,.2f} expected hits")
    hits = {Lw: [] for Lw in range(LMIN, LMAX + 1)}
    counts = {Lw: 0 for Lw in range(LMIN, LMAX + 1)}
    bestq = {b[2]: [] for b in BLOCKS}
    for cb in L.COMBOS:
        K = L.key_codes(cb, INTER).astype(np.int16)
        for lo, Lb, bname in BLOCKS:
            for Lw in range(LMIN, min(LMAX, Lb) + 1):
                for off in range(Lb - Lw + 1):
                    sub = K[:, lo + off: lo + off + Lw]
                    code = L.encode_block(sub, Lw)
                    h = in_sorted(code, tabs[Lw][0])
                    n = int(h.sum())
                    if n:
                        counts[Lw] += n
                        for r in np.nonzero(h)[0][:8]:
                            hits[Lw].append((RK.combo_name(cb), bname, off,
                                             L.codes_to_str(sub[r]),
                                             L.codes_to_str(K[r]), names[int(r)]))
            sc = quad_one_block(K, lo, Lb)
            for r in np.argpartition(-sc, 10)[:10]:
                bestq[bname].append((float(sc[r]), RK.combo_name(cb),
                                     L.codes_to_str(K[r, lo:lo + Lb]), names[int(r)]))
    say(f"  dictionary-word hits by length (observed vs expected):")
    for Lw in range(LMIN, LMAX + 1):
        nw = len(tabs[Lw][0])
        npos = sum(max(0, Lb - Lw + 1) for _, Lb, _ in BLOCKS)
        e = m * 24 * npos * nw / 26.0 ** Lw
        say(f"    len {Lw}: observed {counts[Lw]:>6,}   expected {e:>10,.2f}")
        for h in hits[Lw][:6]:
            say(f"       {h[3]}  in {h[1]} off {h[2]}  ({h[0]})  key={h[4]}  {h[5][:60]}")
    # per-block English tail with a matched control
    rng = np.random.default_rng(17)
    say("  per-block quadgram test (each block scored on its own):")
    for lo, Lb, bname in BLOCKS:
        bq = sorted(bestq[bname], reverse=True)
        ctrl_max = -99.0; ctrl = []
        NCH = 12
        for _ in range(NCH):
            idx = rng.permuted(np.tile(np.arange(L.N, dtype=np.int16), (200000, 1)),
                               axis=1)[:, :Lb]
            s = quad_one_block(L.CT_CODES[idx].astype(np.int16), 0, Lb)
            ctrl_max = max(ctrl_max, float(s.max()))
            ctrl.append(np.percentile(s, [50, 99.99]))
        q = np.mean(np.array(ctrl), axis=0)
        say(f"    {bname} ({Lb} letters): best {bq[0][0]:+.3f} "
            f"[{bq[0][2]}] ; control over {NCH*200000:,} draws "
            f"max {ctrl_max:+.3f}, median {q[0]:+.3f}, 99.99th {q[1]:+.3f}")
        for s_, cn, blk, nm in bq[:5]:
            say(f"       {s_:+.3f}  {blk:14s} {cn:40s} {nm[:60]}")
    results[label] = {"m": int(m), "counts": counts,
                      "expected": {str(Lw): m * 24 * sum(max(0, Lb - Lw + 1)
                                   for _, Lb, _ in BLOCKS) * len(tabs[Lw][0]) / 26.0 ** Lw
                                   for Lw in range(LMIN, LMAX + 1)},
                      "examples": {str(k): [list(map(str, x)) for x in v[:20]]
                                   for k, v in hits.items()},
                      "top_per_block": {b[2]: sorted(bestq[b[2]], reverse=True)[:15]
                                        for b in BLOCKS}}
    say(f"  ({time.time()-t0:.1f}s)")

def main():
    t0 = time.time()
    say("=== (e) per-block keyword / English test on the forced key streams ===")
    # calibration, so the reader can see what the joint test can and cannot see
    say("calibration of the JOINT (two-block) quadgram score used in two2_a:")
    for b1, b2 in [("PALIMPSESTABS", "CISSAKRYPTO"), ("ABSCISSAPALIM", "PSESTKRYPTOS"),
                   ("THEQUICKBROWN", "FOXJUMPSOVE"), ("XQZPALIMPSEST", "QJXBERLINCLO"),
                   ("ZQXPALIMPSEST", "ZQXWJVBKMQP"), ("KRYPTOSKRYPTO", "SKRYPTOSKRY")]:
        a = np.array([[ord(c) - 65 for c in (b1 + b2)]], dtype=np.int64)
        say(f"   {L.quad_score_blocks(a)[0]:+.3f}  {b1} / {b2}")
    say("   -> the joint score sees a keyword only when both blocks carry signal; "
         "this script therefore tests each block on its own.")
    tabs = word_tables()
    say(f"\nword list: {sum(len(tabs[k][1]) for k in tabs):,} words of length "
        f"{LMIN}-{LMAX} from /usr/share/dict/words + data/*")
    results = {}
    for src in (source_catalogue, source_compositions):
        uniq, names, label = src()
        run(uniq, names, label, tabs, results)
    with open(RES, "w") as f:
        json.dump(results, f, indent=1, default=str)
    say(f"\ntotal runtime {time.time()-t0:.1f}s")

if __name__ == "__main__":
    main()
