"""(a) Transposition + NON-periodic substitution.

Model  P -> S -> T -> C   (substitution first, transposition second), cribs read
as *plaintext* positions (see two2_lib docstring).  Then for every candidate
transposition T the intermediate text is I = T^-1(C) and the key stream is
pinned at 24 known contiguous positions:

        k_j = derive_key(combo, P[j], C[T[j]])      j in 21..33 and 63..73

No periodicity is assumed anywhere.  For every T in the catalogue (the same
~1.17M route / columnar / double-columnar / modular / sculpture transpositions
enumerated by twocipher_B_transpositions.py, plus inverses) and every one of the
24 cipher/alphabet combos we ask:

  T1  is the key stream constant (period 1)?
  T2  is it periodic with period p = 2..26?   (positions are fixed, so the number
      of non-trivial checks is the familiar c_p; p <= 23 has chance < 1.2e-10.)
  T3  does the 13-letter block or the 11-letter block occur *exactly* anywhere in
      the sculpture-text corpus (66 texts, plus all 26 rotations of each under
      both the plain and the KRYPTOS key alphabet = 3432 texts)?
  T4  do both blocks occur in the same text at offsets o and o+42 (the joint
      running-key test)?
  T5  how English-like is the key stream (quadgram model), compared with a
      matched random control?

Also reported: the same key stream under the reversed stage order
(P -> T -> S -> C with the plaintext-position reading), where the key values are
identical but sit at the scattered positions T[j]; there only the periodicity
question is meaningful and it is answered with a per-row residue test.

Usage: python two2_a_transpose_keystream.py  (needs numpy)
"""
import os, sys, time, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import two2_lib as L
import runningkey_lib as RK

OUT = os.path.join(HERE, "two2_a_output.txt")
RES = os.path.join(HERE, "two2_a_results.json")
_fh = None
def say(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    _fh.write(s + "\n"); _fh.flush()

# ------------------------------------------------------------------ verify
def verify():
    """Synthetic round trip: build a ciphertext from a known plaintext (with the
    cribs in place), a known NON-periodic key stream and a known transposition,
    then check that the pipeline recovers exactly that key stream at the cribs."""
    rng = np.random.default_rng(11)
    pt = list("".join(chr(65 + int(x)) for x in rng.integers(0, 26, L.N)))
    for i, p in zip(L.CRIB_POS, L.CRIB_PT):
        pt[i] = p
    pt = "".join(pt)
    key = "".join(chr(65 + int(x)) for x in rng.integers(0, 26, L.N))
    combo = ("beaufort", "keyed", "plain", "keyed")
    inter = "".join(RK.encrypt_letter(combo, p, k) for p, k in zip(pt, key))
    T = list(rng.permutation(L.N))
    ct = [None] * L.N
    for j in range(L.N):
        ct[T[j]] = inter[j]
    ct = "".join(ct)
    # recover
    ctc = np.array([ord(c) - 65 for c in ct], dtype=np.int64)
    Tj = np.array([[T[j] for j in L.CRIB_POS]], dtype=np.int64)
    K = L.key_codes(combo, ctc[Tj])
    got = L.codes_to_str(K)
    want = "".join(key[j] for j in L.CRIB_POS)
    ok1 = got == want
    # and the inverse direction (required intermediate letters)
    back = L.inter_codes_required(combo, K)
    ok2 = L.codes_to_str(back) == "".join(inter[j] for j in L.CRIB_POS)
    # identity transposition must reproduce the runningkey.md table
    Tid = np.arange(L.N, dtype=np.int64)[None, :][:, L.CRIB_POS]
    ok3 = True
    for cb in L.COMBOS:
        k = L.codes_to_str(L.key_codes(cb, L.CT_CODES[Tid]))
        b1, b2 = RK.required_key(cb)
        if k != b1 + b2:
            ok3 = False
            say("   MISMATCH", RK.combo_name(cb), k, b1 + b2)
    say(f"verification: synthetic keystream recovered={ok1}  intermediate round trip={ok2}  "
        f"identity-T matches runningkey.md table for all 24 combos={ok3}")
    assert ok1 and ok2 and ok3
    return ok1 and ok2 and ok3

# ------------------------------------------------------------------ corpus
def build_corpus_index():
    """13-gram codes, 11-gram codes and joint (o, o+42) hashes for every corpus
    text, every key-alphabet rotation r=0..25 under both alphabet orderings."""
    texts = RK.corpus()
    c13, c11, joint = [], [], []
    ntext = 0
    for name, txt in texts.items():
        base = np.array([ord(c) - 65 for c in txt], dtype=np.int64)
        variants = []
        for aname, alpha in (("plain", L.PLAIN), ("keyed", L.KEYED)):
            ia = L.IDX[aname][base]
            for r in range(26):
                variants.append(L.LET[aname][(ia + r) % 26])
            if aname == "plain":
                pass
        for v in variants:
            ntext += 1
            n = len(v)
            if n >= 13:
                code = np.zeros(n - 12, dtype=np.int64)
                for i in range(13):
                    code = code * 26 + v[i:n - 12 + i]
                c13.append(code)
            if n >= 11:
                code2 = np.zeros(n - 10, dtype=np.int64)
                for i in range(11):
                    code2 = code2 * 26 + v[i:n - 10 + i]
                c11.append(code2)
            if n >= 13 + 42 + 11 - 13:   # need o+42+11 <= n
                m = n - 52
                if m > 0:
                    a = c13[-1][:m].astype(np.uint64)
                    b = c11[-1][42:42 + m].astype(np.uint64)
                    joint.append(a * np.uint64(6364136223846793005) + b)
    c13 = np.unique(np.concatenate(c13))
    c11 = np.unique(np.concatenate(c11))
    joint = np.unique(np.concatenate(joint))
    return c13, c11, joint, ntext

def in_sorted(vals, sorted_arr):
    i = np.searchsorted(sorted_arr, vals)
    i = np.clip(i, 0, len(sorted_arr) - 1)
    return sorted_arr[i] == vals

# ------------------------------------------------------------------ main
def main():
    global _fh
    _fh = open(OUT, "w")
    t0 = time.time()
    say("=== (a) transposition + non-periodic substitution ===")
    verify()

    Tj, Tic, desc = L.load_transposition_catalogue()
    # only T[j] at the crib plaintext positions matters for this test
    uniq, inv = np.unique(Tj.astype(np.int16), axis=0, return_inverse=True)
    inv = np.asarray(inv).ravel()
    first_desc = {}
    for row, d in zip(inv, desc):
        first_desc.setdefault(int(row), d)
    m = uniq.shape[0]
    say(f"distinct crib images T[j] over the catalogue: {m}")

    INTER = L.CT_CODES[uniq].astype(np.int16)      # (m,24) intermediate letters
    say(f"distinct intermediate crib letter patterns: "
        f"{len(np.unique(INTER, axis=0))}")

    c13, c11, joint, ntext = build_corpus_index()
    say(f"corpus index: {ntext} text variants (66 texts x 26 rotations x 2 alphabet "
        f"orderings), {len(c13)} distinct 13-grams, {len(c11)} distinct 11-grams, "
        f"{len(joint)} distinct joint (o,o+42) pairs")

    results = {"m_transpositions": int(m), "combos": L.COMBO_NAMES}

    # ---------- periodicity structure (independent of combo up to relabelling)
    PMAX = 60
    per_pairs = {p: L.period_pairs(L.CRIB_POS, p) for p in range(1, PMAX + 1)}
    say("\n-- periodic key test (S-then-T; key positions are the fixed crib positions)")
    say("   NB the two crib blocks start 42 apart, so periods above 26 are NOT all")
    say("   vacuous: p=42 still imposes 11 checks.")
    say("   p : checks  chance/row      configs tested   survivors   min violations")
    # for consistency only fam in {vigenere,beaufort} x (ap,ac) matter (varbeaufort
    # negates the key, key alphabet relabels it; neither affects equality classes)
    CORE = [c for c in L.COMBOS if c[0] in ("vigenere", "beaufort") and c[3] == "plain"]
    assert len(CORE) == 8
    KC = {}
    for cb in CORE:
        KC[cb] = L.key_codes(cb, INTER).astype(np.int8)
    surv_periodic = []
    for p in range(1, PMAX + 1):
        pairs = per_pairs[p]
        nchk = len(pairs)
        tot = 0; minviol = 99
        for cb in CORE:
            K = KC[cb]
            ok = np.ones(m, dtype=bool)
            viol = np.zeros(m, dtype=np.int16)
            for i, j in pairs:
                eq = (K[:, i] == K[:, j])
                ok &= eq
                viol += (~eq)
            idx = np.nonzero(ok)[0]
            tot += len(idx)
            if nchk:
                minviol = min(minviol, int(viol.min()))
            else:
                minviol = 0
            for r in idx[:20]:
                surv_periodic.append((p, RK.combo_name(cb), int(r), first_desc[int(r)],
                                      L.codes_to_str(K[r])))
        chance = 26.0 ** (-nchk)
        say(f"   {p:2d} : {nchk:2d}      {chance:.3g}      {m*len(CORE):>12,}   "
            f"{tot:>10,}   (chance-expected {m*len(CORE)*chance:,.2f})  min viol {minviol}")
    STRONG = [p for p in range(1, PMAX + 1) if len(per_pairs[p]) >= 5]
    results["periodic_survivors_strong"] = [s for s in surv_periodic if s[0] in STRONG]
    say(f"   periods with >= 5 checks (chance <= 8.4e-8 per configuration): {STRONG}")
    say(f"   survivors at those periods (chance-expected "
        f"{m*8*sum(26.0**-len(per_pairs[p]) for p in STRONG):.3g}): "
        f"{len([s for s in surv_periodic if s[0] in STRONG])}")
    for s in surv_periodic:
        if s[0] in STRONG:
            say("     !!", s)
            # judge the survivor on the text it implies, not on passing the test
            p_, cname, r_, d_, kstr = s
            cb = [c for c in L.COMBOS if RK.combo_name(c) == cname][0]
            Trow = uniq[r_]
            # rebuild the full transposition is not stored; decrypt only what the
            # key columns determine, using the intermediate text I = T^-1(C) is
            # unavailable without full T, so report the key columns instead.
            key = {}
            for i, pos in enumerate(L.CRIB_POS):
                key[pos % p_] = kstr[i]
            say(f"        period {p_}: {len(key)}/{p_} key columns determined -> "
                f"{p_ - len(key)} columns unknown; key = "
                + "".join(key.get(c, ".") for c in range(p_)))

    # ---------- corpus + English tests over all 24 combos
    say("\n-- corpus running-key test and English test (all 24 combos)")
    tot13 = tot11 = totj = 0
    best = []           # (score, combo, row)
    hits = []
    HBINS = np.arange(-12.0, -2.0, 0.1)
    allsc = []
    for cb in L.COMBOS:
        K = L.key_codes(cb, INTER).astype(np.int16)
        code13 = L.encode_block(K[:, :13], 13)
        code11 = L.encode_block(K[:, 13:], 11)
        h13 = in_sorted(code13, c13)
        h11 = in_sorted(code11, c11)
        jh = (code13.astype(np.uint64) * np.uint64(6364136223846793005)
              + code11.astype(np.uint64))
        hj = in_sorted(jh, joint)
        tot13 += int(h13.sum()); tot11 += int(h11.sum()); totj += int(hj.sum())
        for r in np.nonzero(h13 | h11 | hj)[0][:50]:
            hits.append((RK.combo_name(cb), int(r), first_desc[int(r)],
                         L.codes_to_str(K[r]), bool(h13[r]), bool(h11[r]), bool(hj[r])))
        sc = L.quad_score_blocks(K)
        top = np.argpartition(-sc, 40)[:40]
        for r in top:
            best.append((float(sc[r]), RK.combo_name(cb), int(r), L.codes_to_str(K[r])))
        allsc.append(np.histogram(sc, bins=HBINS)[0])
    say(f"   exact 13-gram (EASTNORTHEAST block) corpus hits: {tot13}")
    say(f"   exact 11-gram (BERLINCLOCK block) corpus hits:   {tot11}")
    say(f"   exact JOINT (both blocks, gap 42) corpus hits:   {totj}")
    ncomp = m * 24
    say(f"   comparisons: {ncomp:,} (T x combo) against {len(c13):,} 13-grams / "
        f"{len(c11):,} 11-grams / {len(joint):,} joint pairs")
    say(f"   chance expectation: 13-gram {ncomp*len(c13)/26**13:.3g}, "
        f"11-gram {ncomp*len(c11)/26**11:.3g}, joint {ncomp*len(joint)/26**24:.3g}")
    results["exact_hits"] = {"block13": tot13, "block11": tot11, "joint": totj}
    for h in hits[:60]:
        say("     hit:", h)

    best.sort(reverse=True)
    say("\n   top 15 key streams by quadgram score (English prose ~ -4.7, "
        "uniform random ~ -8.2):")
    for sc, cn, r, k in best[:15]:
        say(f"     {sc:+.3f}  {cn:42s} {k[:13]} / {k[13:]}   {first_desc[r][:70]}")
    results["top_english"] = [(sc, cn, k, first_desc[r]) for sc, cn, r, k in best[:40]]

    # matched random control: 24-letter draws with the same letter statistics
    rng = np.random.default_rng(5)
    ctrl_max = -99.0; ctrl_all = []
    ctrl_hist = np.zeros(len(HBINS) - 1, dtype=np.int64)
    NCH, CH = 70, 250000
    for _ in range(NCH):
        idx = rng.permuted(np.tile(np.arange(L.N, dtype=np.int16), (CH, 1)), axis=1)[:, :24]
        sc = L.quad_score_blocks(L.CT_CODES[idx].astype(np.int16))
        ctrl_max = max(ctrl_max, float(sc.max()))
        ctrl_all.append(np.percentile(sc, [50, 99, 99.99]))
        ctrl_hist = ctrl_hist + np.histogram(sc, bins=HBINS)[0]
    q = np.mean(np.array(ctrl_all), axis=0)
    say(f"   matched random control ({NCH*CH:,} draws of 24 letters sampled without "
        f"replacement from the ciphertext): max={ctrl_max:+.3f}, "
        f"median={q[0]:+.3f}, 99th={q[1]:+.3f}, 99.99th={q[2]:+.3f}")
    results["control"] = {"n": NCH * CH, "max": ctrl_max, "median": float(q[0]),
                          "p99": float(q[1]), "p9999": float(q[2])}
    obs = np.sum(np.array(allsc), axis=0)
    say(f"   upper tail, observed (all {int(obs.sum()):,} real key streams) vs control "
        f"({int(ctrl_hist.sum()):,} random draws), counts above each threshold:")
    for thr in (-7.4, -7.2, -7.0, -6.8, -6.6):
        i = int(np.searchsorted(HBINS, thr))
        o = int(obs[i:].sum()); c = int(ctrl_hist[i:].sum())
        cscaled = c * obs.sum() / max(ctrl_hist.sum(), 1)
        say(f"      score > {thr:+.1f} : observed {o:>9,}   control-scaled {cscaled:>12,.0f}")
    results["tail"] = {"bins": HBINS.tolist(), "observed": obs.tolist(),
                       "control": ctrl_hist.tolist()}

    # ---------- reversed stage order: key values identical, positions = T[j]
    say("\n-- periodic key test (T-then-S; key positions are the scattered T[j])")
    say("   p :   configs tested     survivors    chance-expected")
    pos = uniq
    surv2 = []
    for p in range(1, PMAX + 1):
        R = (pos % p).astype(np.int32)
        nR = np.zeros(m, dtype=np.int32)
        Rs = np.sort(R, axis=1)
        nR = 1 + (Rs[:, 1:] != Rs[:, :-1]).sum(axis=1)
        tot = 0
        for cb in CORE:
            K = KC[cb].astype(np.int32)
            pair = R * 26 + K
            ps = np.sort(pair, axis=1)
            nP = 1 + (ps[:, 1:] != ps[:, :-1]).sum(axis=1)
            ok = nP == nR
            idx = np.nonzero(ok)[0]
            tot += len(idx)
            if p in STRONG:
                for r in idx[:10]:
                    surv2.append((p, RK.combo_name(cb), int(r), first_desc[int(r)],
                                  L.codes_to_str(KC[cb][r])))
        exp = float((26.0 ** -(24 - nR)).sum()) * len(CORE)
        say(f"   {p:2d} : {m*len(CORE):>12,}   {tot:>10,}   {exp:,.2f}")
    results["periodic_scattered_survivors_strong"] = surv2[:200]
    say(f"   survivors at strong periods (listed, truncated per period/combo): {len(surv2)}")
    for s in surv2[:40]:
        say("     !!", s)

    # ---------- CT-reading with S-then-T: the 24 key VALUES are the fixed ones
    # of the single-cipher problem, but they sit at the relocated positions
    # T^-1[c].  twocipher_B ran the periodic battery only on the 750 contiguity-
    # preserving transpositions; this closes that gap over the whole catalogue.
    say("\n-- periodic key test (S-then-T, CT-reading: fixed key values at the "
        "relocated positions T^-1[c])")
    say("   p :   configs tested     survivors    chance-expected")
    posi = np.unique(Tic.astype(np.int16), axis=0)
    mi = posi.shape[0]
    say(f"   distinct T^-1 crib images: {mi:,}")
    fixed_vals = {}
    for cb in CORE:
        fixed_vals[cb] = L.key_codes(cb, L.CT_CODES[np.array(L.CRIB_POS)][None, :]
                                     ).astype(np.int32)[0]
    surv3 = []
    for p in range(1, PMAX + 1):
        R = (posi % p).astype(np.int32)
        Rs = np.sort(R, axis=1)
        nR = 1 + (Rs[:, 1:] != Rs[:, :-1]).sum(axis=1)
        tot = 0
        for cb in CORE:
            v = fixed_vals[cb][None, :]
            pair = R * 26 + v
            ps = np.sort(pair, axis=1)
            nP = 1 + (ps[:, 1:] != ps[:, :-1]).sum(axis=1)
            good = nP == nR
            idx = np.nonzero(good)[0]
            tot += len(idx)
            if p in STRONG:
                for r in idx[:5]:
                    surv3.append((p, RK.combo_name(cb), int(r),
                                  [int(x) for x in posi[r]]))
        exp = float((26.0 ** -(24 - nR)).sum()) * len(CORE)
        say(f"   {p:2d} : {mi*len(CORE):>12,}   {tot:>10,}   {exp:,.2f}")
    say(f"   survivors at strong periods: {len(surv3)}")
    for s in surv3[:30]:
        say("     !!", s)
    results["ctread_scattered_strong"] = surv3[:100]

    with open(RES, "w") as f:
        json.dump(results, f, indent=1, default=str)
    say(f"\ntotal runtime {time.time()-t0:.1f}s")
    _fh.close()

if __name__ == "__main__":
    main()
