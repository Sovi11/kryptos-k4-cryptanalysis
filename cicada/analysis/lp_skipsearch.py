#!/usr/bin/env python3
"""Skip-aware key-generator search on LP2 (see findings/lp2_antirepeat.md §7-8).

Cipher model (decryptable form of the anti-repeat rule):
    v = sp*p + sk*K[j] + a  (mod 29)
    if v == c[i-1] and the rule fires:  j += 1;  v = sp*p + sk*K[j] + a      # skip one key value
    c[i] = v;  j += 1
A reader with the key sees a possible skip exactly where c[i]-c[i-1] == sk*(K[j+1]-K[j]); that happens
about once per 29 runes, by chance or by a real skip, so decoding is a beam over those branch points.
The skip structure does not depend on sp or a, so stage 1 scores each path by the index of coincidence of
y = c - sk*K, which every (sp, a) leaves unchanged. Stage 2 decodes the best candidates in full and picks
(sp, a) with an English rune model.

Stage 1: every stream in lp_keystreams × 28 chapter/file starts × sk = ±1 × key offsets 0..14,999,
window 100 runes, beam 12 (pruned by coincidences).  The best path per offset is then scored with an English
rune-bigram model that uses LP2's own word breaks, maximised over all 58 (sp, a) transforms.  Controls: a planted cipher (must be found) and 16 uniform random decoy
streams (the chance baseline for the per-stream maximum).
"""
import os, sys, json, time
import numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lp_common import IDX, LATIN, relikd_runes, RELIKD_DIR, PUNCT
import lp_keystreams as KS

W, B, MAXOFF = 100, 12, 15000
R = relikd_runes(); RUN = np.array([x["r"] for x in R]); N = len(RUN)
STARTS = [i for i, x in enumerate(R) if x["first"] or "⁜" in x["j"]]
STARTS = [st for st in STARTS if sum(1 for t in range(st, min(N, st + W)) if R[t]["sec"] == R[st]["sec"]) >= 80]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "findings", "skipsearch_out")

def english_model():
    uni = np.ones(29); bi = np.ones((29, 29)); ini = np.ones(29)
    for word in open(os.path.join(RELIKD_DIR, "baseline-rune-words.txt"), encoding="utf-8").read().split():
        q = [IDX[c] for c in word if c in IDX]
        if not q: continue
        ini[q[0]] += 1
        for v in q: uni[v] += 1
        for a, b in zip(q, q[1:]): bi[a, b] += 1
    return np.log(uni / uni.sum()), np.log(bi / bi.sum(1, keepdims=True)), np.log(ini / ini.sum())
MODEL = english_model()
_y = np.arange(29)
TRANS = [(sp, a) for sp in (1, -1) for a in range(29)]
TB = np.stack([MODEL[1][np.ix_((sp * (_y - a)) % 29, (sp * (_y - a)) % 29)] for sp, a in TRANS]).astype(np.float32)
TI = np.stack([MODEL[2][(sp * (_y - a)) % 29] for sp, a in TRANS]).astype(np.float32)
def inword_mask(st, n):
    return np.array([i > 0 and not ("•" in R[st + i]["j"] or bool(R[st + i]["j"] & PUNCT) or "PB" in R[st + i]["j"])
                     for i in range(n)])

def window(cipher, st, w=W):
    sec = R[st]["sec"]; end = st
    while end < N and R[end]["sec"] == sec and end - st < w: end += 1
    return cipher[st:end], (None if R[st]["first"] else int(cipher[st - 1]))

def beam_C(cw, cprev, K, offsets, sk):
    """Best coincidence count over beam paths, per key offset (vectorised over offsets)."""
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
            rows = np.nonzero(act)[0]; js = j[rows, s]; kj = K[js]; kj1 = K[js + 1]
            if prev is not None:
                cb = ((sk * (kj1 - kj) - (ci - prev)) % 29) == 0
                if cb.any():
                    rb = rows[cb]; jb = js[cb]; yB = (ci - sk * kj1[cb]) % 29
                    parC = C[rb, s].copy(); parcnt = cnt[rb, s].copy()
                    free = ~alive[rb]; hasf = free.any(1)
                    worst = np.where(alive[rb], C[rb], BIG).argmin(1)
                    t = np.where(hasf, free.argmax(1), worst)
                    ok = hasf | (parC > C[rb, t])
                    rb, t, parC, parcnt, yB, jb = rb[ok], t[ok], parC[ok], parcnt[ok], yB[ok], jb[ok]
                    k = np.arange(len(rb))
                    C[rb, t] = parC + parcnt[k, yB]; parcnt[k, yB] += 1
                    cnt[rb, t] = parcnt; j[rb, t] = jb + 2; alive[rb, t] = True; done[rb, t] = True
                    H[rb, t] = H[rb, s]; H[rb, t, i] = yB
            yA = (ci - sk * kj) % 29
            C[rows, s] += cnt[rows, s, yA]; cnt[rows, s, yA] += 1; j[rows, s] = js + 1; done[rows, s] = True
            H[rows, s, i] = yA
    best = np.where(alive, C, -1).argmax(1)
    return C[np.arange(M), best], H[np.arange(M), best].astype(np.int64)

def score_paths(Y, inw):
    """Per-rune English log-likelihood of each row of Y, maximised over the 58 transforms."""
    n = Y.shape[1]
    P = (Y[:, :-1] * 29 + Y[:, 1:])[:, inw[1:]]            # in-word bigrams
    I = Y[:, ~inw]                                          # word-initial runes (incl. position 0)
    TBf = TB.reshape(len(TRANS), -1)
    best = np.full(len(Y), -np.inf, np.float32); arg = np.zeros(len(Y), np.int64)
    for t in range(len(TRANS)):
        sc = (TBf[t][P].sum(1) + TI[t][I].sum(1)) / n
        m = sc > best; best[m] = sc[m]; arg[m] = t
    return best, arg

def search_stream(args):
    name, spec, cipher, starts = args
    K = spec if isinstance(spec, np.ndarray) else KS.build(spec)
    offsets = np.arange(min(MAXOFF, len(K) - 2 * W - 4))
    hits = []
    for st in starts:
        cw, cprev = window(cipher, st)
        n = len(cw); pairs = n * (n - 1) / 2; inw = inword_mask(st, n)
        for sk in (1, -1):
            Cb, Y = beam_C(cw, cprev, K, offsets, sk)
            ll, targ = score_paths(Y, inw)
            for o in np.argsort(-ll)[:3]:
                hits.append(dict(stream=name, start=int(st), sk=sk, offset=int(offsets[o]), ll=float(ll[o]),
                                 trans=TRANS[int(targ[o])], ioc=float(Cb[o] * 29 / pairs), n=n))
    hits.sort(key=lambda h: -h["ll"])
    return name, hits[:10]

# ----------------------------------------------------------------------------- stage 2
def decode_full(cw, cprev, K, off, sk, beam=64):
    paths = [(0, off, [0] * 29, [])]
    for i, ci in enumerate(cw):
        ci = int(ci); prev = int(cw[i - 1]) if i > 0 else cprev; new = []
        for Cc, jj, cnt, ys in paths:
            kj, kj1 = int(K[jj]), int(K[jj + 1])
            if prev is not None and (sk * (kj1 - kj) - (ci - prev)) % 29 == 0:
                y = (ci - sk * kj1) % 29; c2 = cnt[:]; nC = Cc + c2[y]; c2[y] += 1
                new.append((nC, jj + 2, c2, ys + [(y, 1)]))
            y = (ci - sk * kj) % 29; c2 = cnt[:]; nC = Cc + c2[y]; c2[y] += 1
            new.append((nC, jj + 1, c2, ys + [(y, 0)]))
        new.sort(key=lambda t: -t[0]); paths = new[:beam]
    return paths[0]

def best_transform(ys, st, model):
    lu, lb, li = model; y = np.array([v for v, _ in ys])
    inword = np.array([i > 0 and not ("•" in R[st + i]["j"] or R[st + i]["j"] & PUNCT or "PB" in R[st + i]["j"])
                       for i in range(len(y))])
    best = None
    for sp in (1, -1):
        for a in range(29):
            p = (sp * (y - a)) % 29
            sc = np.where(inword[1:], lb[p[:-1], p[1:]], li[p[1:]]).sum() + li[p[0]]
            sc = sc / len(p)
            if best is None or sc > best[0]: best = (sc, sp, a, p)
    return best

def render(p, st):
    out = []
    for i, v in enumerate(p):
        j = R[st + i]["j"]
        if i > 0:
            if j & PUNCT: out.append(". ")
            elif "•" in j or "PB" in j: out.append(" ")
        out.append(LATIN[v])
    return "".join(out)

# ----------------------------------------------------------------------------- planted control
_WORDS = None
def plant(cipher, file_idx, K, off, sk, sp, a, fire, rng, word_from):
    """Re-encrypt one LP2 file with a known key under the skip rule. The plaintext keeps LP2's own
    word skeleton, filled with real English words of the same rune length (War and Peace, in order)."""
    global _WORDS
    if _WORDS is None:
        _WORDS = [[IDX[c] for c in w if c in IDX] for w in
                  open(os.path.join(RELIKD_DIR, "baseline-rune-words.txt"), encoding="utf-8").read().split()]
    st = next(i for i, x in enumerate(R) if x["first"] and x["sec"] == file_idx)
    en = st
    while en < N and R[en]["sec"] == file_idx: en += 1
    inw = inword_mask(st, en - st); lens = []
    for i in range(en - st):
        if inw[i]: lens[-1] += 1
        else: lens.append(1)
    by_len = {}; k = word_from
    pt = []
    for L in lens:
        while len(_WORDS[k]) != L: k += 1
        pt.extend(_WORDS[k]); k += 1
    c = cipher.copy(); jj = off; prev = None
    for i in range(st, en):
        p = pt[i - st]; v = (sp * p + sk * K[jj] + a) % 29
        if prev is not None and v == prev and rng.random() < fire:
            jj += 1; v = (sp * p + sk * K[jj] + a) % 29
        c[i] = v; jj += 1; prev = v
    return c, st, en

def plant_task(args):
    name, spec, file_idx, off, sk, sp, a, word_from, seed = args
    rng = np.random.default_rng(seed); K = KS.build(spec)
    pc, st, en = plant(RUN, file_idx, K, off, sk, sp, a, 0.81, rng, word_from)
    _, hits = search_stream((name, spec, pc, [x for x in STARTS if st <= x < en]))
    h = hits[0]
    found = h["sk"] == sk and 0 <= h["offset"] - off - (h["start"] - st) <= 8
    return dict(stream=name, file=file_idx, offset=off, sk=sk, sp=sp, a=a, top=h, found=bool(found))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(3301)
    streams = KS.all_streams(); SD = dict(streams)
    t0 = time.time()
    # controls: 3 planted ciphers (searched only over their own file's starts) + 16 decoy key streams
    plants = [("sqrt3/2-digit/phase1", SD["sqrt3/2-digit/phase1"], 3, 12345, 1, 1, 7, 5000, 1),
              ("sha512-chain('3301')", SD["sha512-chain('3301')"], 6, 4321, -1, -1, 20, 40000, 2),
              ("py3-rand(3301)", SD["py3-rand(3301)"], 7, 9876, 1, -1, 0, 90000, 3)]
    with Pool(8) as pool:
        pres = pool.map_async(plant_task, plants)
        dres = pool.map(search_stream, [(f"decoy{k}", rng.integers(0, 29, 30000), RUN, STARTS) for k in range(16)])
        pres = pres.get()
    for pr in pres:
        h = pr["top"]
        print(f"PLANT {pr['stream']} in file {pr['file']} (offset {pr['offset']}, sk {pr['sk']:+d}, sp {pr['sp']:+d}, a {pr['a']}): "
              f"top hit start {h['start']} offset {h['offset']} trans {tuple(h['trans'])}  LL {h['ll']:.3f}/rune  IoC {h['ioc']:.2f}  "
              f"{'FOUND' if pr['found'] else 'MISSED'}")
    dll = sorted(r[1][0]["ll"] for r in dres)
    dio = sorted(r[1][0]["ioc"] for r in dres)
    print(f"DECOYS (16 random key streams, same search): per-stream max LL min {dll[0]:.3f} median {np.median(dll):.3f} "
          f"max {dll[-1]:.3f} /rune;  max IoC median {np.median(dio):.2f}  ({time.time()-t0:.0f}s)", flush=True)
    json.dump(dict(plants=pres, decoys=dres), open(os.path.join(OUT, "controls.json"), "w"), indent=1, default=str)
    if len(sys.argv) > 1 and sys.argv[1] == "controls": sys.exit()
    with Pool(8) as pool: res = pool.map(search_stream, [(n, s, RUN, STARTS) for n, s in streams])
    json.dump(res, open(os.path.join(OUT, "real.json"), "w"), indent=1, default=str)
    allh = sorted((h for _, hs in res for h in hs), key=lambda h: -h["ll"])
    smax = sorted(((hs[0]["ll"], n) for n, hs in res), reverse=True)
    above = [x for x in smax if x[0] > dll[-1]]
    print(f"REAL: {len(streams)} streams; per-stream max LL: median {np.median([x[0] for x in smax]):.3f}, "
          f"max {smax[0][0]:.3f} ({smax[0][1]}); streams above the highest decoy: {len(above)}")
    print("Top 12 (stream, start, sign, offset, transform, LL/rune, IoC):")
    for h in allh[:12]:
        print(f"   {h['stream']:40s} start {h['start']:5d} sk {h['sk']:+d} off {h['offset']:5d} {str(tuple(h['trans'])):9s}"
              f" LL {h['ll']:.3f}  IoC {h['ioc']:.2f}")
    print("Full 300-rune decodes of the top 4:")
    for h in allh[:4]:
        K = KS.build(SD[h["stream"]])
        cw, cprev = window(RUN, h["start"], 300); Cc, _, _, ys = decode_full(cw, cprev, K, h["offset"], h["sk"])
        sc, sp, a, p = best_transform(ys, h["start"], MODEL)
        print(f"   {h['stream']} @ {h['start']}: LL {sc:.2f}/rune: {render(p, h['start'])[:120]}")
    print(f"({time.time()-t0:.0f}s)")
