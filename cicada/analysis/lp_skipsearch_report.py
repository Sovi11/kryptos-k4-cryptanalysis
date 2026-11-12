#!/usr/bin/env python3
"""Post-analysis of the skip-aware search (lp_skipsearch.py): reads findings/skipsearch_out/*.json.

1. Planted controls, scored correctly: the key index the search should report at a window start is the
   planted key index *including every skip the plant made before that start* (the in-search label only
   allowed 0..8 accumulated skips, so later windows were mislabelled MISSED).
2. Chance level of the per-stream maximum: exact exchangeability p-value for "k of 104 real streams beat
   the best of 16 decoys", plus a rank-sum comparison of the two sets of maxima.
3. Out-of-sample continuation: every hit was *selected* on a 100-rune window, so its score is
   inflated. A true key keeps reading as English past the window; a chance peak does not. For each hit,
   decode the next (up to) 200 runes from key index offset+100+s, s = 0..14 (the unknown number of
   skips inside the window), with the hit's own (sp, a) held fixed, and keep the best of the 15. The
   null is the same procedure applied to the decoy streams' top hits.
"""
import os, sys, json, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lp_skipsearch as S
import lp_keystreams as KS

OUT = S.OUT
ctrl = json.load(open(os.path.join(OUT, "controls.json")))
real = json.load(open(os.path.join(OUT, "real.json")))
SD = dict(KS.all_streams())
PLANTS = [("sqrt3/2-digit/phase1", 3, 12345, 1, 1, 7, 5000, 1),
          ("sha512-chain('3301')", 6, 4321, -1, -1, 20, 40000, 2),
          ("py3-rand(3301)", 7, 9876, 1, -1, 0, 90000, 3)]          # same as lp_skipsearch.__main__

def plant_trace(K, file_idx, off, sk, sp, a, word_from, seed):
    """Exact replay of S.plant (same RNG draws), also recording the key index before each rune."""
    rng = np.random.default_rng(seed)
    words = [[S.IDX[c] for c in w if c in S.IDX] for w in
             open(os.path.join(S.RELIKD_DIR, "baseline-rune-words.txt"), encoding="utf-8").read().split()]
    st = next(i for i, x in enumerate(S.R) if x["first"] and x["sec"] == file_idx)
    en = st
    while en < S.N and S.R[en]["sec"] == file_idx: en += 1
    inw = S.inword_mask(st, en - st); lens = []
    for i in range(en - st):
        if inw[i]: lens[-1] += 1
        else: lens.append(1)
    k = word_from; pt = []
    for L in lens:
        while len(words[k]) != L: k += 1
        pt.extend(words[k]); k += 1
    c = S.RUN.copy(); jj = off; prev = None; jidx = {}; skips = 0
    for i in range(st, en):
        jidx[i] = jj
        p = pt[i - st]; v = (sp * p + sk * K[jj] + a) % 29
        if prev is not None and v == prev and rng.random() < 0.81:
            jj += 1; skips += 1; v = (sp * p + sk * K[jj] + a) % 29
        c[i] = v; jj += 1; prev = v
    return c, st, en, jidx, skips

def continuation(cipher, h, K, ext=200, slack=15):
    st2 = h["start"] + h["n"]
    if h["n"] < S.W or st2 >= S.N or S.R[st2]["sec"] != S.R[h["start"]]["sec"]: return None
    cw, cprev = S.window(cipher, st2, ext)
    if len(cw) < 50: return None
    K = np.asarray(K); offs = np.arange(h["offset"] + h["n"], h["offset"] + h["n"] + slack)
    offs = offs[offs + 2 * len(cw) + 4 < len(K)]
    _, Y = S.beam_C(cw, cprev, K, offs, h["sk"])
    t = S.TRANS.index(tuple(h["trans"])); inw = S.inword_mask(st2, len(cw))
    P = (Y[:, :-1] * 29 + Y[:, 1:])[:, inw[1:]]; I = Y[:, ~inw]
    sc = (S.TB[t].reshape(-1)[P].sum(1) + S.TI[t][I].sum(1)) / len(cw)
    b = int(sc.argmax())
    return float(sc[b]), int(offs[b]), len(cw), Y[b]

if __name__ == "__main__":
    print("== 1. Planted controls (key index at the hit's window start includes the plant's own skips)")
    pcont = []
    for (name, fidx, off, sk, sp, a, wf, seed), pr in zip(PLANTS, ctrl["plants"]):
        K = KS.build(SD[name]); c, st, en, jidx, skips = plant_trace(K, fidx, off, sk, sp, a, wf, seed)
        h = pr["top"]; true_j = jidx[h["start"]]
        ok = h["sk"] == sk and tuple(h["trans"]) == (sp, a) and abs(h["offset"] - true_j) <= 1
        before = sum(1 for i in range(st, h["start"]) if jidx.get(i + 1, jidx[i] + 1) - jidx[i] == 2)
        cont = continuation(c, h, K)
        pcont.append(cont[0] if cont else None)
        print(f"   {name:24s} file {fidx} ({en-st} runes, {skips} skips planted): top hit start {h['start']} "
              f"(+{h['start']-st} runes, {before} skips before it) offset {h['offset']} vs true {true_j}; "
              f"sk {h['sk']:+d} trans {tuple(h['trans'])} vs ({sp:+d}, {a}); window LL {h['ll']:.3f}; "
              f"continuation LL {cont[0]:.3f} over {cont[2]} runes -> {'RECOVERED' if ok else 'NOT recovered'}")
        if cont: print(f"      continuation reads: {S.render(((sp * (cont[3] - a)) % 29), h['start'] + h['n'])[:110]}")

    print("\n== 2. Per-stream maxima: real vs decoy")
    dmax = np.array([hs[0]["ll"] for _, hs in ctrl["decoys"]]); rmax = np.array([hs[0]["ll"] for _, hs in real])
    k = int((rmax > dmax.max()).sum()); nd, nr = len(dmax), len(rmax)
    p = math.comb(nr, k) / math.comb(nr + nd, k)
    # rank-sum (Mann-Whitney U, normal approximation)
    allv = np.concatenate([rmax, dmax]); ranks = allv.argsort().argsort() + 1
    U = ranks[:nr].sum() - nr * (nr + 1) / 2; mu = nr * nd / 2; sd = math.sqrt(nr * nd * (nr + nd + 1) / 12)
    print(f"   decoys (n={nd}): median {np.median(dmax):.3f}, max {dmax.max():.3f}")
    print(f"   real   (n={nr}): median {np.median(rmax):.3f}, max {rmax.max():.3f}")
    print(f"   real streams above the best decoy: {k}; P(>= {k} | exchangeable) = {p:.3f}"
          f"  (expected {nr/(nd+1):.1f});  rank-sum z = {(U-mu)/sd:+.2f}")

    print("\n== 3. Out-of-sample continuation (next <=200 runes, fixed (sp,a), best of 15 skip counts)")
    # rebuild the exact decoy streams (same RNG sequence as lp_skipsearch.__main__)
    null = []
    rng = np.random.default_rng(3301); DK = [rng.integers(0, 29, 30000) for _ in range(16)]
    for (nm, hs), K in zip(ctrl["decoys"], DK):
        for h in hs:
            r = continuation(S.RUN, h, K)
            if r: null.append(r[0])
    null = np.array(null)
    print(f"   null (decoy top hits, n={len(null)}): median {np.median(null):.3f}, 99th pct {np.percentile(null, 99):.3f}, max {null.max():.3f}")
    print(f"   planted keys: {', '.join(f'{x:.3f}' for x in pcont if x is not None)}")
    rows = []
    for nm, hs in real:
        K = KS.build(SD[nm])
        for h in hs:
            r = continuation(S.RUN, h, K)
            if r: rows.append((r[0], h, r))
    rows.sort(key=lambda t: -t[0])
    cl = np.array([t[0] for t in rows])
    print(f"   real hits (n={len(cl)}): median {np.median(cl):.3f}, max {cl.max():.3f}; "
          f"above null max: {(cl > null.max()).sum()}; above null 99th pct: {(cl > np.percentile(null, 99)).sum()} "
          f"(expected ~{0.01*len(cl):.0f})")
    print("   best 8 real continuations:")
    for c_, h, r in rows[:8]:
        sp, a = h["trans"]
        print(f"     {h['stream']:32s} start {h['start']:5d} sk {h['sk']:+d} off {h['offset']:5d}  window {h['ll']:.3f}  "
              f"cont {c_:.3f}: {S.render(((sp * (r[3] - a)) % 29), h['start'] + h['n'])[:70]}")
    json.dump(dict(null=null.tolist(), plants=pcont,
                   real=[dict(stream=h["stream"], start=h["start"], sk=h["sk"], offset=h["offset"], window_ll=h["ll"],
                              cont_ll=c_) for c_, h, _ in rows]),
              open(os.path.join(OUT, "continuation.json"), "w"), indent=1)

    print("\n== 4. Does the scorer recognise Cicada's own English? (solved LP1/LP2 plaintext pages, 100-rune windows)")
    from lp_common import relikd_runes, PUNCT
    names = sorted(f[:-4] for f in os.listdir(S.RELIKD_DIR) if f.startswith("solved_"))
    lls = []
    for nm in names:
        Q = relikd_runes([nm]); y = np.array([x["r"] for x in Q])
        inw = np.array([i > 0 and not ("•" in Q[i]["j"] or bool(Q[i]["j"] & PUNCT) or "PB" in Q[i]["j"])
                        for i in range(len(Q))])
        for s in range(0, len(y) - S.W + 1, S.W):
            Y = y[None, s:s + S.W]; ll, t = S.score_paths(Y, inw[s:s + S.W].copy())
            lls.append(float(ll[0]))
    lls = np.array(lls)
    print(f"   {len(names)} solved pages, {len(lls)} windows: LL/rune median {np.median(lls):.3f}, "
          f"min {lls.min():.3f}, max {lls.max():.3f}  (decoy per-stream max {dmax.max():.3f})")
