"""(b) The K3 procedure, derived exactly and then applied to K4.

Part 1 recovers K3's transposition from the data itself: the 336-letter K3
ciphertext and plaintext are both on file, so the transposition is *found*, not
quoted, by searching compositions of simple grid routes until one maps ct to pt
letter-for-letter.

Part 2 defines the step operator that search returns and applies it, and its
inverse, to K4 in every variant (all widths, one and two steps, both stage
orders), then re-tests substitution on each result under both crib readings:

  CT-reading: are the crib words contiguous in the intermediate text, and if so
      does a periodic Vigenere/Beaufort/Quagmire fit (periods 2-26)?
  PT-reading: the key stream implied at the 24 crib plaintext positions -- is it
      constant, periodic, English, or a sculpture text?  (same test as two2_a)
"""
import os, sys, math, time, json, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import runningkey_lib as RK
import twocipher_common as TC

HAVE_NP = True
try:
    import numpy as np
    import two2_lib as L
except Exception:
    HAVE_NP = False

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "two2_b_output.txt")
RES = os.path.join(HERE, "two2_b_results.json")
_fh = open(OUT, "w")
def say(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True); _fh.write(s + "\n"); _fh.flush()

# --------------------------------------------------------------- grid steps
def grid_order(n, w, fill, route):
    """Read order (list of source indices) for an n-letter text written into a
    grid of width w (height h = ceil(n/w)) and read out along `route`.
    fill='row' fills by rows (ragged last row), 'col' fills by columns.
    routes: 'cols-R2L'  = columns right-to-left, each top-to-bottom  (= rotate 90 CCW)
            'cols-L2R'  = columns left-to-right, each top-to-bottom  (= transpose)
            'cols-R2L-up', 'cols-L2R-up' = the same with columns read bottom-to-top
            'rows-B2T'  = rows bottom-to-top, each left-to-right     (= flip vertical)
            'rows-T2B'  = identity read
    """
    h = math.ceil(n / w)
    cell = {}
    if fill == "row":
        for j in range(n):
            cell[(j // w, j % w)] = j
    else:
        for j in range(n):
            cell[(j % h, j // h)] = j
    cols = range(w - 1, -1, -1) if "R2L" in route else range(w)
    rows_up = route.endswith("-up")
    order = []
    if route.startswith("cols"):
        for c in cols:
            rr = range(h - 1, -1, -1) if rows_up else range(h)
            for r in rr:
                if (r, c) in cell:
                    order.append(cell[(r, c)])
    else:
        rr = range(h - 1, -1, -1) if route == "rows-B2T" else range(h)
        for r in rr:
            for c in range(w):
                if (r, c) in cell:
                    order.append(cell[(r, c)])
    assert sorted(order) == list(range(n))
    return order

ROUTES = ["cols-R2L", "cols-L2R", "cols-R2L-up", "cols-L2R-up", "rows-T2B", "rows-B2T"]

def apply_order(order, s):
    return "".join(s[j] for j in order)

def invert_order(order):
    inv = [0] * len(order)
    for k, j in enumerate(order):
        inv[j] = k
    return inv

# --------------------------------------------------------------- Part 1: K3
def derive_k3():
    ct, pt = RK.K3_CT, RK.K3_PT
    n = len(ct)
    say(f"K3: ct {n} letters, pt {len(pt)} letters, anagram={sorted(ct)==sorted(pt)}")
    divs = [d for d in range(2, n) if n % d == 0]
    perms = []
    for w in divs:
        for fill in ("row", "col"):
            for rt in ROUTES:
                perms.append((f"w={w} fill={fill} {rt}", tuple(grid_order(n, w, fill, rt))))
    say(f"  simple grid steps on divisor widths: {len(perms)}")
    singles = [d for d, o in perms if apply_order(o, ct) == pt]
    say(f"  single-step solutions: {len(singles)}")
    mid = {}
    for d, o in perms:
        mid.setdefault(apply_order(o, ct), []).append(d)
    doubles = []
    for s, ds in mid.items():
        for d2, o2 in perms:
            if apply_order(o2, s) == pt:
                doubles.append((ds, d2))
    say(f"  two-step solutions: {len(doubles)}")
    for ds, d2 in doubles:
        say(f"    step1 in {ds}  ->  step2 {d2}")
    # canonical: the (8, 24) pair with fill=row, cols right-to-left
    o1 = grid_order(n, 8, "row", "cols-R2L")
    o2 = grid_order(n, 24, "row", "cols-R2L")
    got = apply_order(o2, apply_order(o1, ct))
    say(f"  canonical check  ct -> [rows of 8, read columns right-to-left] -> "
        f"[rows of 24, read columns right-to-left] == K3 plaintext : {got == pt}")
    say(f"    intermediate after step 1: {apply_order(o1, ct)[:60]}...")
    say(f"    result                   : {got[:60]}...")
    # the operator is a 90-degree rotation: rows of w, read columns right-to-left
    comp = [o1[k] for k in o2]      # composite read order ct -> pt
    assert apply_order(comp, ct) == pt
    # verify the inverse reproduces the ciphertext
    assert apply_order(invert_order(comp), pt) == ct
    say("  composite permutation verified in both directions.")
    # are all the two-step solutions re-factorisations of one permutation?
    def parse(d):
        w = int(d.split("w=")[1].split()[0]); fill = d.split("fill=")[1].split()[0]
        return grid_order(n, w, fill, d.split()[-1])
    comps = set()
    for ds, d2 in doubles:
        a = parse(ds[0]); b = parse(d2)
        comps.add(tuple(a[k] for k in b))
    say(f"  the {len(doubles)} two-step solutions are re-factorisations of "
        f"{len(comps)} distinct composite permutation(s).")
    return comp

# ------------------------------------------------- Part 2: the same on K4
def k4_transpositions():
    """Yield (desc, order) where order is a read order on the 97 K4 letters.
    order[k] = index in the source text that becomes position k of the result."""
    n = 97
    for w in range(2, n):
        for fill in ("row", "col"):
            for rt in ROUTES:
                o = grid_order(n, w, fill, rt)
                yield f"1-step w={w} fill={fill} {rt}", o
                yield f"1-step w={w} fill={fill} {rt} [inv]", invert_order(o)
    # two steps, K3-style (fill by rows, read columns right-to-left), all width pairs
    base = {}
    for w in range(2, 49):
        base[w] = grid_order(n, w, "row", "cols-R2L")
    for w1 in range(2, 49):
        for w2 in range(2, 49):
            o = [base[w1][k] for k in base[w2]]
            yield f"2-step K3-style w1={w1} w2={w2}", o
            yield f"2-step K3-style w1={w1} w2={w2} [inv]", invert_order(o)
    # two steps with the exact K3 widths but every route/fill combination
    for w1, w2 in itertools.permutations((8, 24), 2):
        for f1 in ("row", "col"):
            for r1 in ROUTES:
                o1 = grid_order(n, w1, f1, r1)
                for f2 in ("row", "col"):
                    for r2 in ROUTES:
                        o2 = grid_order(n, w2, f2, r2)
                        o = [o1[k] for k in o2]
                        yield f"2-step K3widths w1={w1}{f1}/{r1} w2={w2}{f2}/{r2}", o
                        yield f"2-step K3widths w1={w1}{f1}/{r1} w2={w2}{f2}/{r2} [inv]", invert_order(o)

def main():
    t0 = time.time()
    say("=== (b) the K3 procedure, derived and applied to K4 ===\n")
    comp = derive_k3()

    say("\n--- applying K3-style transpositions to K4 ---")
    n = 97
    CT = TC.CT
    CRIB_POS = [p for p, _, _ in TC.CRIBS]
    results = {"n_transpositions": 0, "ctread_contiguous": [], "ptread_hits": [],
               "top_english": []}
    best = []
    ncontig = 0
    seen = set()
    rows = []
    for desc, order in k4_transpositions():
        to = tuple(order)
        if to in seen:
            continue
        seen.add(to)
        rows.append((desc, order))
    say(f"distinct K3-style transpositions of K4: {len(rows)}")
    results["n_transpositions"] = len(rows)

    # ---- CT-reading: crib words contiguous in the intermediate text?
    # order[k] = source index placed at result position k, i.e. result = T^-1(ct)
    # in the notation of twocipher: intermediate[k] = ct[order[k]], so a crib at
    # ct position c sits at intermediate position inv_order[c].
    contig = []
    for desc, order in rows:
        inv = invert_order(order)
        ok = True
        for p, ctw, ptw, _ in TC.CRIB_WORDS:
            src = [inv[p + k] for k in range(len(ctw))]
            if src != list(range(src[0], src[0] + len(src))):
                ok = False; break
        if ok:
            contig.append((desc, tuple(inv[c] for c in CRIB_POS)))
    ncontig = len(contig)
    say(f"\nCT-reading: transpositions keeping every crib word contiguous+increasing "
        f"in the intermediate text: {ncontig}")
    seen_tuple = {}
    for desc, tup in contig:
        seen_tuple.setdefault(tup, []).append(desc)
    say(f"  distinct crib-position tuples: {len(seen_tuple)}")
    nonvac_total = 0
    for tup, descs in sorted(seen_tuple.items()):
        pairs = [(tup[i], TC.CRIBS[i][1], TC.CRIBS[i][2]) for i in range(24)]
        surv = TC.run_periodic_battery(pairs, periods=range(2, 27))
        nonvac = [s for s in surv if s[4] > 0]
        nonvac_total += len(nonvac)
        say(f"    positions {tup[:4]}...{tup[-2:]}  ({len(descs)} transpositions, "
            f"e.g. {descs[0]}): consistent periodic configs {len(surv)}, "
            f"non-vacuous {len(nonvac)}")
        for s in nonvac:
            p, fam, an, key, checks = s
            say(f"       NON-VACUOUS: p={p} {fam} {an} checks={checks} key={key}")
    results["ctread_contiguous"] = [(d, list(t)) for d, t in contig[:200]]
    say(f"  total non-vacuous periodic survivors: {nonvac_total}")

    # ---- PT-reading: the implied key stream (needs numpy)
    if not HAVE_NP:
        say("\nPT-reading test skipped (numpy unavailable)")
    else:
        say("\nPT-reading: key stream implied at the 24 crib plaintext positions "
            "(k_j = derive_key(P[j], C[T[j]]))")
        import two2_a_transpose_keystream as A
        A._fh = _fh
        c13, c11, joint, ntext = A.build_corpus_index()
        # intermediate[j] = ct[order[j]]  => I[j] = C[order[j]], so the "T[j]" of
        # two2_lib is order[j] itself.
        Tj = np.array([[o[j] for j in L.CRIB_POS] for _, o in rows], dtype=np.int64)
        INTER = L.CT_CODES[Tj]
        PMAX = 60
        per_pairs = {p: L.period_pairs(L.CRIB_POS, p) for p in range(1, PMAX + 1)}
        STRONG = [p for p in range(1, PMAX + 1) if len(per_pairs[p]) >= 5]
        hits13 = hits11 = hitsj = 0
        periodic_hits = []
        for cb in L.COMBOS:
            K = L.key_codes(cb, INTER)
            c13c = L.encode_block(K[:, :13], 13); c11c = L.encode_block(K[:, 13:], 11)
            h13 = A.in_sorted(c13c, c13); h11 = A.in_sorted(c11c, c11)
            jh = (c13c.astype(np.uint64) * np.uint64(6364136223846793005)
                  + c11c.astype(np.uint64))
            hj = A.in_sorted(jh, joint)
            hits13 += int(h13.sum()); hits11 += int(h11.sum()); hitsj += int(hj.sum())
            sc = L.quad_score_blocks(K)
            for r in np.argsort(-sc)[:5]:
                best.append((float(sc[r]), RK.combo_name(cb), rows[int(r)][0],
                             L.codes_to_str(K[r])))
            if cb[0] in ("vigenere", "beaufort") and cb[3] == "plain":
                for p in STRONG:
                    ok = np.ones(len(rows), dtype=bool)
                    for i, j in per_pairs[p]:
                        ok &= (K[:, i] == K[:, j])
                    for r in np.nonzero(ok)[0]:
                        periodic_hits.append((p, RK.combo_name(cb), rows[int(r)][0],
                                              L.codes_to_str(K[r])))
        say(f"  exact corpus hits: 13-block {hits13}, 11-block {hits11}, joint {hitsj} "
            f"(out of {len(rows)*24:,} tests; chance ~{len(rows)*24*len(c13)/26**13:.2g})")
        say(f"  periodic key streams at periods with >= 5 checks "
            f"({STRONG[0]}..{STRONG[-1]}, chance <= 8.4e-8 each; "
            f"{len(rows)*8*sum(26.0**-len(per_pairs[p]) for p in STRONG):.3g} expected): "
            f"{len(periodic_hits)}")
        for h in periodic_hits[:20]:
            say("    ", h)
        best.sort(reverse=True)
        say("  top 10 key streams by quadgram score:")
        for sc, cn, d, k in best[:10]:
            say(f"    {sc:+.3f}  {cn:40s} {k[:13]}/{k[13:]}  {d}")
        results["top_english"] = best[:30]
        results["ptread_hits"] = {"b13": hits13, "b11": hits11, "joint": hitsj,
                                  "periodic_le23": periodic_hits[:50]}

    # ---- literal K3 recipe applied to K4, printed for inspection
    say("\n--- literal K3 recipe on K4 (rows of 8 then rows of 24, columns "
        "right-to-left), all four stage/direction variants ---")
    o8 = grid_order(97, 8, "row", "cols-R2L")
    o24 = grid_order(97, 24, "row", "cols-R2L")
    variants = {
        "K3-decrypt order (8 then 24)": [o8[k] for k in o24],
        "reverse order (24 then 8)": [o24[k] for k in o8],
        "inverse of K3-decrypt (encrypt direction)": invert_order([o8[k] for k in o24]),
        "inverse of reverse order": invert_order([o24[k] for k in o8]),
    }
    for name, o in variants.items():
        t = apply_order(o, CT)
        q, w, v = TC.english_judgement(t)
        say(f"  {name}:\n    {t}\n    quad={q:.2f} wordcov={w:.2f} -> {v}")

    with open(RES, "w") as f:
        json.dump(results, f, indent=1, default=str)
    say(f"\nruntime {time.time()-t0:.1f}s")

if __name__ == "__main__":
    main()
