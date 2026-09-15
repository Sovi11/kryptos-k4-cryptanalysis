"""(d) Transposition + transposition, then substitution.

A composition T = T2 o T1 of two simple transpositions is a permutation that
generally lies OUTSIDE the single-transposition catalogue, so this is not covered
by two2_a / twocipher_B.  The cribs bite in two different ways depending on where
the substitution sits:

  P -> S -> T1 -> T2 -> C   (substitution first)
      CT-reading: for a periodic substitution to be testable at all the crib
      words must land on contiguous, increasing intermediate positions; we count
      how many compositions do that and run the periodic battery on each distinct
      crib-position tuple.
      PT-reading: the key stream at the 24 crib plaintext positions is forced, so
      the two2_a battery applies verbatim (periodic / corpus / English).

  P -> T1 -> T2 -> S -> C   (substitution last)
      Under the CT-reading the transpositions are invisible to the crib pairs, so
      this reduces exactly to the single-cipher tests that are already negative.
      Under the PT-reading the key values are the same as above but sit at the
      scattered positions T[j]; reported as the scattered periodic test.

Base family (each with its inverse, de-duplicated):
  * row/column routes on every grid of width 2..50, both fill orders, all four
    orientations of rows-then-columns and columns-then-rows;
  * keyed columnar with every column permutation for widths 2..5;
  * the four sculpture blocks (OBKR + three 31-letter rows) in every order with
    every subset reversed;
  * skip/decimation permutations j -> (a*j + b) mod 97.
"""
import os, sys, time, json, math, itertools
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import two2_lib as L
import runningkey_lib as RK
import twocipher_common as TC
import two2_a_transpose_keystream as A

OUT = os.path.join(HERE, "two2_d_output.txt")
RES = os.path.join(HERE, "two2_d_results.json")
_fh = open(OUT, "w")
A._fh = _fh
def say(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True); _fh.write(s + "\n"); _fh.flush()

N = 97
CRIB_POS = L.CRIB_POS

def perm_from_read_order(order):
    T = [0] * N
    for k, j in enumerate(order):
        T[j] = k
    return T

def inverse(T):
    Ti = [0] * N
    for j, c in enumerate(T):
        Ti[c] = j
    return Ti

def base_family():
    out = []
    # row/column routes
    for w in range(2, 51):
        h = math.ceil(N / w)
        for fill in ("row", "col"):
            cell = {}
            if fill == "row":
                for j in range(N):
                    cell[(j // w, j % w)] = j
            else:
                for j in range(N):
                    cell[(j % h, j // h)] = j
            for rdir in (1, -1):
                for cdir in (1, -1):
                    rows = list(range(h))[::rdir]; cols = list(range(w))[::cdir]
                    o1 = [cell[(r, c)] for r in rows for c in cols if (r, c) in cell]
                    o2 = [cell[(r, c)] for c in cols for r in rows if (r, c) in cell]
                    out.append((f"route {h}x{w} {fill} rows r{rdir}c{cdir}", perm_from_read_order(o1)))
                    out.append((f"route {h}x{w} {fill} cols r{rdir}c{cdir}", perm_from_read_order(o2)))
    # columnar, all column permutations for small widths
    for w in range(2, 6):
        h = math.ceil(N / w)
        cell = {(j // w, j % w): j for j in range(N)}
        for perm in itertools.permutations(range(w)):
            o = [cell[(r, c)] for c in perm for r in range(h) if (r, c) in cell]
            out.append((f"columnar w={w} {perm}", perm_from_read_order(o)))
    # sculpture blocks
    blocks = [list(range(0, 4)), list(range(4, 35)), list(range(35, 66)), list(range(66, 97))]
    for perm in itertools.permutations(range(4)):
        for rev in range(16):
            o = []
            for i, bi in enumerate(perm):
                b = blocks[bi]
                o += b[::-1] if (rev >> i) & 1 else b
            out.append((f"blocks {perm} rev={rev:04b}", perm_from_read_order(o)))
    # decimation
    for a in range(1, N):
        if math.gcd(a, N) != 1:
            continue
        for b in (0,):
            o = [(a * k + b) % N for k in range(N)]
            out.append((f"skip a={a} b={b}", perm_from_read_order(o)))
    # add inverses, de-duplicate
    seen = {}
    fam = []
    for d, T in out:
        for tag, TT in (("", T), (" [inv]", inverse(T))):
            k = bytes(TT)
            if k in seen:
                continue
            seen[k] = 1
            fam.append((d + tag, TT))
    return fam

def main():
    t0 = time.time()
    say("=== (d) transposition + transposition, then substitution ===")
    fam = base_family()
    nb = len(fam)
    say(f"base family: {nb} distinct transpositions (routes, columnar, sculpture "
        f"blocks, decimations, each with its inverse)")
    Tm = np.array([T for _, T in fam], dtype=np.int16)          # (nb, 97)
    Tinv = np.array([inverse(T) for _, T in fam], dtype=np.int16)
    say(f"compositions to examine: {nb*nb:,}")

    cp = np.array(CRIB_POS, dtype=np.int64)
    # forward signature of T = T2 o T1 :  T[j] = T2[T1[j]]
    # inverse signature                 :  Tinv[c] = T1inv[T2inv[c]]
    sig_f = np.empty((nb * nb, 24), dtype=np.int16)
    sig_i = np.empty((nb * nb, 24), dtype=np.int16)
    for i1 in range(nb):
        u = Tm[i1][cp]                        # (24,)
        sig_f[i1 * nb:(i1 + 1) * nb] = Tm[:, u]
    for i2 in range(nb):
        v = Tinv[i2][cp]
        sig_i[i2::nb] = Tinv[:, v]
    say(f"signatures built ({time.time()-t0:.1f}s)")

    results = {"base": nb, "compositions": nb * nb}

    # ---------------- CT-reading: crib words contiguous in the intermediate?
    ok = np.ones(nb * nb, dtype=bool)
    off = 0
    for p, ctw, ptw, _ in TC.CRIB_WORDS:
        Lw = len(ctw)
        blk = sig_i[:, off:off + Lw].astype(np.int32)
        step = blk[:, 1:] - blk[:, :-1]
        ok &= np.all(step == 1, axis=1)
        off += Lw
    nc = int(ok.sum())
    say(f"\nCT-reading: compositions keeping every crib word contiguous+increasing: "
        f"{nc:,} of {nb*nb:,}")
    idx = np.nonzero(ok)[0]
    tuples = {}
    for r in idx:
        tuples.setdefault(tuple(int(x) for x in sig_i[r]), []).append(int(r))
    say(f"  distinct crib-position tuples: {len(tuples)}")
    nonvac = 0; nonvac_list = []; chance_nv = 0.0; nconf = 0
    for tup, rows in tuples.items():
        pairs = [(tup[i], TC.CRIBS[i][1], TC.CRIBS[i][2]) for i in range(24)]
        surv = TC.run_periodic_battery(pairs, periods=range(2, 27))
        for pp in range(2, 27):
            c = 24 - len({x % pp for x in tup})
            nconf += 8
            if c > 0:
                chance_nv += 8 * 26.0 ** -c
        nv = [s for s in surv if s[4] > 0]
        nonvac += len(nv)
        for s in nv:
            r = rows[0]
            nonvac_list.append((tup, s[0], s[1], s[2], s[4],
                                fam[r // nb][0], fam[r % nb][0]))
    say(f"  periodic battery: {nconf:,} (tuple, period 2-26, arrangement) configurations")
    say(f"  periodic survivors with >=1 non-trivial check: {nonvac}  "
        f"(chance-expected {chance_nv:.1f})")
    for s in nonvac_list[:25]:
        say("    NON-VACUOUS", s)
    results["ct_contiguous"] = nc
    results["ct_nonvacuous"] = [str(s) for s in nonvac_list[:100]]

    # ---------------- PT-reading: the forced key stream
    say("\nPT-reading: forced key stream at the 24 crib plaintext positions")
    uniq, first = np.unique(sig_f, axis=0, return_index=True)
    m = uniq.shape[0]
    say(f"  distinct forward crib signatures: {m:,} (from {nb*nb:,} compositions)")
    INTER = L.CT_CODES[uniq.astype(np.int64)].astype(np.int16)
    c13, c11, joint, ntext = A.build_corpus_index()
    PMAX = 60
    per_pairs = {p: L.period_pairs(CRIB_POS, p) for p in range(1, PMAX + 1)}
    CORE = [c for c in L.COMBOS if c[0] in ("vigenere", "beaufort") and c[3] == "plain"]
    tot13 = tot11 = totj = 0
    best = []
    per_counts = {p: 0 for p in range(1, PMAX + 1)}
    for cb in L.COMBOS:
        K = L.key_codes(cb, INTER).astype(np.int16)
        c13c = L.encode_block(K[:, :13], 13); c11c = L.encode_block(K[:, 13:], 11)
        h13 = A.in_sorted(c13c, c13); h11 = A.in_sorted(c11c, c11)
        jh = (c13c.astype(np.uint64) * np.uint64(6364136223846793005)
              + c11c.astype(np.uint64))
        hj = A.in_sorted(jh, joint)
        tot13 += int(h13.sum()); tot11 += int(h11.sum()); totj += int(hj.sum())
        sc = L.quad_score_blocks(K)
        for r in np.argpartition(-sc, 20)[:20]:
            best.append((float(sc[r]), RK.combo_name(cb), int(r), L.codes_to_str(K[r])))
        if cb in CORE:
            for p in range(1, PMAX + 1):
                good = np.ones(m, dtype=bool)
                for i, j in per_pairs[p]:
                    good &= (K[:, i] == K[:, j])
                per_counts[p] += int(good.sum())
                if len(per_pairs[p]) >= 5 and good.any():
                    for r in np.nonzero(good)[0][:10]:
                        rr = int(first[r])
                        say(f"    PERIODIC p={p} {RK.combo_name(cb)} "
                            f"key={L.codes_to_str(K[r])} "
                            f"T1={fam[rr // nb][0]} T2={fam[rr % nb][0]}")
    say(f"  periodic key streams by period (8 core arrangements x {m:,} signatures):")
    for p in range(1, PMAX + 1):
        nchk = len(per_pairs[p])
        say(f"    p={p:2d} checks={nchk:2d} survivors={per_counts[p]:>8,}  "
            f"chance-expected {m*8*26.0**-nchk:,.2f}")
    say(f"  exact corpus hits: 13-block {tot13}, 11-block {tot11}, joint {totj} "
        f"(out of {m*24:,} tests)")
    best.sort(reverse=True)
    say("  top 10 key streams by quadgram score:")
    for sc, cn, r, k in best[:10]:
        rr = int(first[r])
        say(f"    {sc:+.3f}  {cn:40s} {k[:13]}/{k[13:]}  "
            f"T1={fam[rr // nb][0]} | T2={fam[rr % nb][0]}")
    results["pt_exact"] = {"b13": tot13, "b11": tot11, "joint": totj, "tests": m * 24}
    results["pt_periodic"] = {str(p): per_counts[p] for p in per_counts}
    results["pt_top"] = [(s, c, k) for s, c, _, k in best[:30]]

    with open(RES, "w") as f:
        json.dump(results, f, indent=1)
    say(f"\nruntime {time.time()-t0:.1f}s")

if __name__ == "__main__":
    main()
