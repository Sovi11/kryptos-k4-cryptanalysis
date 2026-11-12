#!/usr/bin/env python3
"""Other collision-repair rules for LP2 (see findings/lp2_repairrules.md). Builds on lp_skipsearch.py.

Encryption step: v = sp*p + sk*K[j] + a (mod 29). When v == c[i-1] and the rule fires (81%), a repair rule decides
what is written. Rules fall into three classes by what they do to key alignment:

  forward slip   "skip"      write sp*p + sk*K[j+1] + a, consume two key values      (lp_skipsearch.py, done)
                 "skipuntil" keep skipping until no collision                        (planted here, skip-mode search)
  aligned        "flip"      write sp*p - sk*K[j] + a  (Vigenere <-> Beaufort switch) (planted here, skip-mode search)
                 "reroll2"   write sp*p + sk*U + a, U from a second, unknown stream   (planted here, skip-mode search)
                 "litcons"   write p unencrypted, key value still consumed             (planted here, skip-mode search)
  backward slip  "stay"      write sp*p + a (the rune with no key added) and do NOT consume the key value: the LP1
                             interrupter, triggered by a collision instead of by plaintext F. For (sp, a) = (1, 0) this
                             is literally "write the plaintext rune and hold the key", as LP1 did with F.  (new search)

A reader with the key sees a possible "stay" wherever c[i-1] - c[i] == sk*K[j]: about once per 29 runes, independent
of (sp, a), so the beam/coincidence/English pipeline of lp_skipsearch carries over with a different branch.

Usage: lp_repairsearch.py plants | search | report | full
"""
import os, sys, json, time
import numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lp_skipsearch as S
import lp_keystreams as KS

R, RUN, N, W, B, MAXOFF = S.R, S.RUN, S.N, S.W, S.B, S.MAXOFF
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "findings", "repairsearch_out")
FIRE = 0.81

def beam(cw, cprev, K, offsets, sk, mode):
    """S.beam_C with the branch rule chosen by mode ('skip' = forward slip, 'stay' = backward slip)."""
    M = len(offsets)
    alive = np.zeros((M, B), bool); alive[:, 0] = True
    j = np.zeros((M, B), np.int64); j[:, 0] = offsets
    cnt = np.zeros((M, B, 29), np.int16); C = np.zeros((M, B), np.int32)
    H = np.zeros((M, B, len(cw)), np.int8)
    BIG = np.iinfo(np.int32).max
    for i in range(len(cw)):
        ci = int(cw[i]); prev = int(cw[i - 1]) if i > 0 else cprev
        alive0 = alive.copy(); done = np.zeros((M, B), bool)
        for s in range(B):
            act = alive0[:, s] & ~done[:, s]
            if not act.any(): continue
            rows = np.nonzero(act)[0]; js = j[rows, s]; kj = K[js]
            if prev is not None:
                if mode == "skip":
                    kj1 = K[js + 1]
                    cb = ((sk * (kj1 - kj) - (ci - prev)) % 29) == 0
                    yb_all = (ci - sk * kj1) % 29; jb_all = js + 2
                else:
                    cb = ((prev - ci - sk * kj) % 29) == 0
                    yb_all = np.full(len(js), ci); jb_all = js
                if cb.any():
                    rb = rows[cb]; jb = jb_all[cb]; yB = yb_all[cb]
                    parC = C[rb, s].copy(); parcnt = cnt[rb, s].copy()
                    free = ~alive[rb]; hasf = free.any(1)
                    worst = np.where(alive[rb], C[rb], BIG).argmin(1)
                    t = np.where(hasf, free.argmax(1), worst)
                    ok = hasf | (parC > C[rb, t])
                    rb, t, parC, parcnt, yB, jb = rb[ok], t[ok], parC[ok], parcnt[ok], yB[ok], jb[ok]
                    k = np.arange(len(rb))
                    C[rb, t] = parC + parcnt[k, yB]; parcnt[k, yB] += 1
                    cnt[rb, t] = parcnt; j[rb, t] = jb; alive[rb, t] = True; done[rb, t] = True
                    H[rb, t] = H[rb, s]; H[rb, t, i] = yB
            yA = (ci - sk * kj) % 29
            C[rows, s] += cnt[rows, s, yA]; cnt[rows, s, yA] += 1; j[rows, s] = js + 1; done[rows, s] = True
            H[rows, s, i] = yA
    best = np.where(alive, C, -1).argmax(1)
    return C[np.arange(M), best], H[np.arange(M), best].astype(np.int64)

def search_stream(args):
    name, spec, cipher, starts, mode = args
    K = spec if isinstance(spec, np.ndarray) else KS.build(spec)
    offsets = np.arange(min(MAXOFF, len(K) - 2 * W - 4))
    hits = []
    for st in starts:
        cw, cprev = S.window(cipher, st)
        n = len(cw); pairs = n * (n - 1) / 2; inw = S.inword_mask(st, n)
        for sk in (1, -1):
            Cb, Y = beam(cw, cprev, K, offsets, sk, mode)
            ll, targ = S.score_paths(Y, inw)
            for o in np.argsort(-ll)[:3]:
                hits.append(dict(stream=name, start=int(st), sk=sk, offset=int(offsets[o]), ll=float(ll[o]),
                                 trans=S.TRANS[int(targ[o])], ioc=float(Cb[o] * 29 / pairs), n=n))
    hits.sort(key=lambda h: -h["ll"])
    return name, hits[:10]

# ----------------------------------------------------------------------------- planted controls
_WORDS = None
def plant(K, file_idx, off, sk, sp, a, rule, word_from, seed):
    """Re-encrypt one LP2 file under a repair rule. Returns cipher, file span, key index before each rune."""
    global _WORDS
    if _WORDS is None:
        _WORDS = [[S.IDX[c] for c in w if c in S.IDX] for w in
                  open(os.path.join(S.RELIKD_DIR, "baseline-rune-words.txt"), encoding="utf-8").read().split()]
    rng = np.random.default_rng(seed)
    st = next(i for i, x in enumerate(R) if x["first"] and x["sec"] == file_idx)
    en = st
    while en < N and R[en]["sec"] == file_idx: en += 1
    inw = S.inword_mask(st, en - st); lens = []
    for i in range(en - st):
        if inw[i]: lens[-1] += 1
        else: lens.append(1)
    k = word_from; pt = []
    for L in lens:
        while len(_WORDS[k]) != L: k += 1
        pt.extend(_WORDS[k]); k += 1
    c = RUN.copy(); jj = off; prev = None; jidx = {}; nrep = 0
    enc = lambda p, kv: (sp * p + sk * kv + a) % 29
    for i in range(st, en):
        jidx[i] = jj; p = pt[i - st]; v = enc(p, K[jj]); adv = 1
        if prev is not None and v == prev and rng.random() < FIRE:
            nrep += 1
            if rule == "skip":      jj += 1; v = enc(p, K[jj])
            elif rule == "skipuntil":
                while v == prev: jj += 1; v = enc(p, K[jj])
            elif rule == "flip":    v = (sp * p - sk * K[jj] + a) % 29
            elif rule == "reroll2": v = enc(p, int(rng.integers(0, 29)))
            elif rule == "litcons": v = p
            elif rule == "stay":    v = (sp * p + a) % 29; adv = 0
            else: raise ValueError(rule)
        c[i] = v; jj += adv; prev = int(v)
    return c, st, en, jidx, nrep

def continuation(cipher, h, K, mode, ext=200, slack=15):
    st2 = h["start"] + h["n"]
    if h["n"] < W or st2 >= N or R[st2]["sec"] != R[h["start"]]["sec"]: return None
    cw, cprev = S.window(cipher, st2, ext)
    if len(cw) < 50: return None
    K = np.asarray(K); base = h["offset"] + h["n"]
    offs = base + (np.arange(slack) if mode == "skip" else -np.arange(slack))
    offs = offs[(offs >= 0) & (offs + 2 * len(cw) + 4 < len(K))]
    _, Y = beam(cw, cprev, K, offs, h["sk"], mode)
    t = S.TRANS.index(tuple(h["trans"])); inw = S.inword_mask(st2, len(cw))
    P = (Y[:, :-1] * 29 + Y[:, 1:])[:, inw[1:]]; I = Y[:, ~inw]
    sc = (S.TB[t].reshape(-1)[P].sum(1) + S.TI[t][I].sum(1)) / len(cw)
    b = int(sc.argmax())
    return float(sc[b]), int(offs[b]), len(cw), Y[b]

PLANTS = [  # rule, stream, file, offset, sk, sp, a, word_from, seed, search mode
    ("stay", "pi/3-digit/phase0", 2, 3000, 1, 1, 0, 12000, 11, "stay"),
    ("stay", "sha256-chain('cicada')", 5, 7777, -1, -1, 13, 60000, 12, "stay"),
    ("stay", "glibc-rand(1033)", 8, 11111, 1, 1, 22, 120000, 13, "stay"),
    ("flip", "e/2-digit/phase1", 1, 2222, 1, 1, 5, 30000, 14, "skip"),
    ("reroll2", "sha512-chain('divinity')", 4, 6000, -1, 1, 9, 80000, 15, "skip"),
    ("litcons", "py2-rand(2014)", 0, 500, 1, -1, 3, 100000, 16, "skip"),
    ("skipuntil", "phi/2-digit/phase0", 6, 9000, -1, -1, 1, 140000, 17, "skip"),
    ("stay", "py3-rand(3301)", 7, 9876, 1, -1, 0, 90000, 3, "stay", 1000),   # searched only >= 1000 runes in
]

def plant_task(args):
    rule, name, fidx, off, sk, sp, a, wf, seed, mode = args[:10]; mindepth = args[10] if len(args) > 10 else 0
    K = KS.build(dict(KS.all_streams())[name])
    c, st, en, jidx, nrep = plant(K, fidx, off, sk, sp, a, rule, wf, seed)
    _, hits = search_stream((name, K, c, [x for x in S.STARTS if st + mindepth <= x < en], mode))
    h = hits[0]; ok = h["sk"] == sk and tuple(h["trans"]) == (sp, a) and abs(h["offset"] - jidx[h["start"]]) <= 1
    cont = continuation(c, h, K, mode)
    text = S.render((sp * (cont[3] - a)) % 29, h["start"] + h["n"])[:100] if cont else ""
    return dict(rule=rule, stream=name, file=fidx, runes=en - st, repairs=nrep, mode=mode, top=h,
                true_offset=jidx[h["start"]], depth=h["start"] - st, recovered=bool(ok),
                cont=cont[0] if cont else None, text=text)

def run_plants():
    with Pool(8) as pool: res = pool.map(plant_task, PLANTS)
    for r in res:
        h = r["top"]
        print(f"   {r['rule']:9s} {r['stream']:26s} file {r['file']} ({r['runes']} runes, {r['repairs']} repairs), {r['mode']}-mode search: "
              f"hit +{r['depth']} runes, offset {h['offset']} vs true {r['true_offset']}, sk {h['sk']:+d} trans {tuple(h['trans'])}, "
              f"window LL {h['ll']:.3f}, next-200 LL {r['cont']:.3f} -> {'RECOVERED' if r['recovered'] else 'NOT recovered'}")
        print(f"      {r['text']}")
    return res

DECOY_SEED = 4242
def decoy_streams():
    rng = np.random.default_rng(DECOY_SEED); return [rng.integers(0, 29, 30000) for _ in range(16)]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); t0 = time.time(); what = sys.argv[1] if len(sys.argv) > 1 else "full"
    streams = KS.all_streams(); SD = dict(streams)
    if what in ("plants", "full"):
        print("== Planted controls"); pres = run_plants()
        json.dump(pres, open(os.path.join(OUT, "plants.json"), "w"), indent=1, default=str)
        print(f"   ({time.time()-t0:.0f}s)", flush=True)
    if what in ("search", "full"):
        with Pool(8) as pool:
            dres = pool.map(search_stream, [(f"decoy{k}", K, RUN, S.STARTS, "stay") for k, K in enumerate(decoy_streams())])
            json.dump(dres, open(os.path.join(OUT, "decoys.json"), "w"), indent=1, default=str)
            print(f"== decoys done ({time.time()-t0:.0f}s)", flush=True)
            res = pool.map(search_stream, [(n, s, RUN, S.STARTS, "stay") for n, s in streams])
        json.dump(res, open(os.path.join(OUT, "real.json"), "w"), indent=1, default=str)
        print(f"== real done ({time.time()-t0:.0f}s)", flush=True)
    if what in ("report", "full"):
        import math
        dres = json.load(open(os.path.join(OUT, "decoys.json"))); res = json.load(open(os.path.join(OUT, "real.json")))
        dmax = np.array([hs[0]["ll"] for _, hs in dres]); rmax = np.array([hs[0]["ll"] for _, hs in res])
        k = int((rmax > dmax.max()).sum()); p = math.comb(len(rmax), k) / math.comb(len(rmax) + len(dmax), k)
        print(f"== 'stay' search, per-stream max LL: decoys median {np.median(dmax):.3f} max {dmax.max():.3f}; "
              f"real median {np.median(rmax):.3f} max {rmax.max():.3f} ({res[int(rmax.argmax())][0]}); "
              f"real above best decoy {k} (expected {len(rmax)/(len(dmax)+1):.1f}, P = {p:.3f})")
        null = []
        for (nm, hs), K in zip(dres, decoy_streams()):
            for h in hs:
                r = continuation(RUN, h, K, "stay")
                if r: null.append(r[0])
        null = np.array(null); rows = []
        for nm, hs in res:
            K = KS.build(SD[nm])
            for h in hs:
                r = continuation(RUN, h, K, "stay")
                if r: rows.append((r[0], h, r))
        rows.sort(key=lambda t: -t[0]); cl = np.array([t[0] for t in rows])
        print(f"== out-of-sample next-200 LL: null (decoy hits, n={len(null)}) median {np.median(null):.3f} "
              f"99th {np.percentile(null, 99):.3f} max {null.max():.3f}; real (n={len(cl)}) median {np.median(cl):.3f} "
              f"max {cl.max():.3f}; real above null max {(cl > null.max()).sum()}, above null 99th {(cl > np.percentile(null, 99)).sum()}")
        print("   top 12 window hits:")
        for h in sorted((h for _, hs in res for h in hs), key=lambda h: -h["ll"])[:12]:
            print(f"     {h['stream']:32s} start {h['start']:5d} sk {h['sk']:+d} off {h['offset']:5d} {str(tuple(h['trans'])):9s} LL {h['ll']:.3f}")
        print("   best 6 continuations:")
        for c_, h, r in rows[:6]:
            sp, a = h["trans"]
            print(f"     {h['stream']:32s} start {h['start']:5d} window {h['ll']:.3f} cont {c_:.3f}: "
                  f"{S.render((sp * (r[3] - a)) % 29, h['start'] + h['n'])[:70]}")
        json.dump(dict(null=null.tolist(), real=[dict(stream=h["stream"], start=h["start"], sk=h["sk"], offset=h["offset"],
                       window_ll=h["ll"], cont_ll=c_) for c_, h, _ in rows]),
                  open(os.path.join(OUT, "continuation.json"), "w"), indent=1)
    print(f"({time.time()-t0:.0f}s)")
