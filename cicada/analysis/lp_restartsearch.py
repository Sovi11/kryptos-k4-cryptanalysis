#!/usr/bin/env python3
"""Key-restart search: every OEIS sequence as the key, restarted at every LP2 heading / section / page start.

LP1 precedent: page 56 ("AN END") is encrypted with phi(prime) starting from the first prime *at the title*;
the Vigenere pages restart DIVINITY/FIRFUMFERENFE per section. If LP2 restarts a generated key at each heading, the
heading and the text after it are encrypted with the sequence's FIRST terms, which is exactly what the OEIS data
section lists. No crib is needed: decode and let the English model judge.

Rows: every OEIS sequence with >= 30 terms that looks flat mod 29 (>= 15 distinct values and >= 15 distinct
differences among the first 42 terms), deduplicated mod 29; key start o = 0, 1, 2 (skip a leading 0/1 etc.);
key sign sk = +-1. Cipher model and slips as lp_repairsearch.py: modes 'skip' and 'stay' (aligned rules are covered
by 'skip', see findings/lp2_repairrules.md). Output map (sp, a) maximised over all 58.
Each decode is scored on its first 26, 36 and 56 runes (only where the sequence has enough terms).
Control: the identical rows decoded at 24 random mid-text positions where no restart is expected; the per-position
maximum there is the chance level for this many trials.

Usage: lp_restartsearch.py [run|report]
"""
import os, sys, gzip, json, time
import numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lp_skipsearch as S
from lp_common import LATIN

R, RUN, N = S.R, S.RUN, S.N
B = 12; CHUNK = 15000; NMAX = 56; CUTS = (26, 36, 56); TPAD = 128; OS = (0, 1, 2)
OEIS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "oeis", "stripped.gz")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "findings", "restartsearch_out")

def load_oeis(minterms=30):
    ids, rows, lens, seen = [], [], [], set()
    for line in gzip.open(OEIS, "rt"):
        if line[0] == "#": continue
        aid, _, rest = line.partition(" ")
        t = [int(x) for x in rest.strip().strip(",").split(",") if x]
        if len(t) < minterms: continue
        m = [x % 29 for x in t[:TPAD]]
        if len(set(m[:42])) < 15 or len(set((np.diff(m[:42]) % 29).tolist())) < 15: continue
        k = bytes(m[:64])
        if k in seen: continue
        seen.add(k); ids.append(aid); rows.append(m); lens.append(len(m))
    rng = np.random.default_rng(29)
    K2 = rng.integers(0, 29, (len(rows), TPAD)).astype(np.int16)     # random padding past the listed terms
    for i, m in enumerate(rows): K2[i, :len(m)] = m
    return ids, K2, np.array(lens)

_CACHE = {}
def oeis():
    if "o" not in _CACHE: _CACHE["o"] = load_oeis()
    return _CACHE["o"]

def beam_rows(cw, cprev, K2, rseq, j0, sk, mode):
    """lp_repairsearch.beam with a different key sequence per row (row r uses K2[rseq[r]] from index j0[r]).
    Returns every beam path (M, B, n) and which are alive. In windows this short, picking the path with the most
    coincidences picks the wrong one about 10% of the time when a repair falls in the window, so all alive paths
    are scored with the English model instead (score_paths)."""
    M = len(rseq)
    alive = np.zeros((M, B), bool); alive[:, 0] = True
    j = np.zeros((M, B), np.int64); j[:, 0] = j0
    cnt = np.zeros((M, B, 29), np.int16); C = np.zeros((M, B), np.int32)
    H = np.zeros((M, B, len(cw)), np.int8); BIG = np.iinfo(np.int32).max
    for i in range(len(cw)):
        ci = int(cw[i]); prev = int(cw[i - 1]) if i > 0 else cprev
        alive0 = alive.copy(); done = np.zeros((M, B), bool)
        for s in range(B):
            act = alive0[:, s] & ~done[:, s]
            if not act.any(): continue
            rows = np.nonzero(act)[0]; js = np.minimum(j[rows, s], TPAD - 2); kj = K2[rseq[rows], js].astype(np.int64)
            if prev is not None:
                if mode == "skip":
                    kj1 = K2[rseq[rows], js + 1].astype(np.int64)
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
    return H, alive

TBF = S.TB.reshape(len(S.TRANS), -1).T.copy()     # (29*29, 58): bigram LL under every output map
TIF = S.TI.T.copy()                                 # (29, 58): word-initial LL under every output map

def score_cuts(Y, inw, cuts):
    """Per-rune English LL of the first c runes of each row, maximised over the 58 maps, for each cut c."""
    M, n = Y.shape; cuts = [c for c in cuts if c <= n]
    best = np.empty((M, len(cuts)), np.float32); arg = np.empty((M, len(cuts)), np.int16)
    Yt = np.ascontiguousarray(Y.T).astype(np.intp)          # (n, M): fast per-position reads
    acc = TIF[Yt[0]].copy(); q = 0
    for i in range(1, n + 1):
        if i == cuts[q]:
            arg[:, q] = acc.argmax(1); best[:, q] = acc[np.arange(M), arg[:, q]] / i; q += 1
            if q == len(cuts): break
        acc += TBF[Yt[i - 1] * 29 + Yt[i]] if inw[i] else TIF[Yt[i]]
    return cuts, best, arg

def score_paths(H, alive, inw, cuts):
    """score_cuts over every beam path; per row and cut, the best alive path's LL and map."""
    M, Bn, n = H.shape
    cuts, best, arg = score_cuts(H.reshape(M * Bn, n), inw, cuts)
    best = np.where(alive.reshape(-1, 1), best, -np.inf).reshape(M, Bn, len(cuts)); arg = arg.reshape(M, Bn, len(cuts))
    p = best.argmax(1)
    return cuts, np.take_along_axis(best, p[:, None], 1)[:, 0], np.take_along_axis(arg, p[:, None], 1)[:, 0]

def position_task(args):
    pos, mode, kind = args[:3]; cipher = args[3] if len(args) > 3 else RUN
    ids, K2, lens = oeis()
    cw, cprev = S.window(cipher, pos, NMAX)
    n = len(cw); inw = S.inword_mask(pos, n)
    nseq = len(ids); out = {}
    for sk in (1, -1):
        for o in OS:
            for a0 in range(0, nseq, CHUNK):
                rseq = np.arange(a0, min(nseq, a0 + CHUNK)); j0 = np.full(len(rseq), o)
                H, alive = beam_rows(cw, cprev, K2, rseq, j0, sk, mode)
                cuts, best, arg = score_paths(H, alive, inw, CUTS)
                for q, c in enumerate(cuts):
                    valid = lens[rseq] - o >= c + 2
                    sc = np.where(valid, best[:, q], -np.inf)
                    top = np.argsort(-sc)[:5]
                    lst = out.setdefault(c, [])
                    for r in top:
                        if np.isfinite(sc[r]):
                            lst.append(dict(seq=ids[rseq[r]], o=o, sk=sk, ll=float(sc[r]), trans=S.TRANS[int(arg[r, q])]))
    for c in out: out[c] = sorted(out[c], key=lambda h: -h["ll"])[:10]
    return dict(pos=int(pos), mode=mode, kind=kind, n=n, top={str(c): v for c, v in out.items()})

def positions():
    first = [i for i, x in enumerate(R) if x["first"]]
    after = [i for i, x in enumerate(R) if "⁜" in x["j"]]
    page = [i for i, x in enumerate(R) if "PB" in x["j"]]
    lines = {}
    for i, x in enumerate(R): lines.setdefault((x["sec"], x["line"]), []).append(i)
    head = []
    for (sec, ln), idx in lines.items():
        st = idx[0]; x = R[st]
        if not (x["first"] or x["j"] & {"PB", "X", "⁜"}): continue
        words = 1
        for i in idx[1:]:
            if "⁜" in R[i]["j"]: head.append(st); break
            if "•" in R[i]["j"]: words += 1
            if words > 5: break
    kinds = {}
    for lab, L in (("page", page), ("after⁜", after), ("heading", head), ("file", first)):
        for p in L: kinds[p] = lab
    restart = sorted(p for p in kinds if len(S.window(RUN, p, NMAX)[0]) >= 26)
    near = np.zeros(N, bool)
    for p in restart: near[max(0, p - 5):p + 60] = True
    rng = np.random.default_rng(3301)
    cand = [i for i in range(N) if not near[i] and len(S.window(RUN, i, NMAX)[0]) == NMAX]
    control = sorted(rng.choice(cand, 24, replace=False).tolist())
    return [(p, kinds[p]) for p in restart], [(p, "control") for p in control]

_WORDS = None
def plant(pos, key, sk, sp, a, rule, word_from, seed, fire=0.81):
    """Re-encrypt LP2 from pos (to the end of its file) with key = the given sequence from its first term.
    Plaintext: LP2's word skeleton filled with War and Peace words of the same rune length."""
    global _WORDS
    if _WORDS is None:
        _WORDS = [[S.IDX[c] for c in w if c in S.IDX] for w in
                  open(os.path.join(S.RELIKD_DIR, "baseline-rune-words.txt"), encoding="utf-8").read().split()]
    en = pos
    while en < N and R[en]["sec"] == R[pos]["sec"]: en += 1
    inw = S.inword_mask(pos, en - pos); lens = []
    for i in range(en - pos):
        if inw[i]: lens[-1] += 1
        else: lens.append(1)
    k = word_from; pt = []
    for L in lens:
        while len(_WORDS[k]) != L: k += 1
        pt.extend(_WORDS[k]); k += 1
    rng = np.random.default_rng(seed); key = list(key) + rng.integers(0, 29, 4 * (en - pos)).tolist()
    c = RUN.copy(); jj = 0; prev = int(RUN[pos - 1]) if not R[pos]["first"] else None
    for i in range(pos, en):
        p = pt[i - pos]; v = (sp * p + sk * key[jj] + a) % 29; adv = 1
        if prev is not None and v == prev and rng.random() < fire:
            if rule == "skip": jj += 1; v = (sp * p + sk * key[jj] + a) % 29
            else: v = (sp * p + a) % 29; adv = 0
        c[i] = v; jj += adv; prev = int(v)
    return c

PLANTS = [  # (position kind, which: index into the restart list of that kind), terms wanted, rule, sk, sp, a, word_from, seed
    ("file", 2, 60, "skip", 1, 1, 0, 7000, 1),
    ("page", 10, 40, "stay", -1, 1, 11, 50000, 2),
    ("heading", 1, 30, "skip", 1, -1, 25, 90000, 3),
]

def plant_ciphers(rs):
    ids, K2, lens = oeis(); rng = np.random.default_rng(1033); tasks = []; meta = []
    for kind, which, want, rule, sk, sp, a, wf, seed in PLANTS:
        pos = [p for p, k in rs if k == kind][which]
        cand = np.nonzero((lens >= want) & (lens < want + 10))[0]; si = int(rng.choice(cand))
        c = plant(pos, K2[si, :lens[si]].astype(int).tolist(), sk, sp, a, rule, wf, seed)
        tasks.append((pos, rule, kind, c)); meta.append((ids[si], pos, kind, int(lens[si]), rule, sk, sp, a))
    return tasks, meta

def run_plants(rs):
    tasks, meta = plant_ciphers(rs)
    with Pool(len(tasks)) as pool: res = pool.map(position_task, tasks)
    for (sid, pos, kind, L, rule, sk, sp, a), r in zip(meta, res):
        for c, hs in sorted(r["top"].items(), key=lambda t: int(t[0])):
            h = hs[0]; ok = h["seq"] == sid and h["o"] == 0 and h["sk"] == sk and tuple(h["trans"]) == (sp, a)
            if L < int(c) + 2:
                print(f"   PLANT {sid} ({L} terms) at {kind} {pos}: cut {c:>2s}: not eligible (sequence shorter than the window)")
                continue
            print(f"   PLANT {sid} ({L} terms) at {kind} {pos}, rule {rule}, sk {sk:+d} (sp,a)=({sp},{a}): cut {c:>2s}: "
                  f"top {h['seq']} o={h['o']} sk {h['sk']:+d} {tuple(h['trans'])} LL {h['ll']:.3f} -> {'FOUND' if ok else 'missed'}"
                  f"   (2nd {hs[1]['ll']:.3f})")
    return res

# ----------------------------------------------------------------------------- report
_ROW = {}
def decode_hit(pos, h, mode, c, cipher=RUN):
    """Re-decode one hit. Among the beam paths, take those with the best LL on the first c runes under the hit's map,
    and of those the best continuation; return (plaintext, LL on the first c runes, LL on runes c.. up to the end of the
    window or of the listed terms, number of continuation runes)."""
    ids, K2, lens = oeis()
    if not _ROW: _ROW.update({s: i for i, s in enumerate(ids)})
    r = _ROW[h["seq"]]; n_ok = min(NMAX, int(lens[r]) - h["o"] - 2)
    cw, cprev = S.window(cipher, pos, n_ok); n = len(cw); inw = S.inword_mask(pos, n)
    H, alive = beam_rows(cw, cprev, K2, np.array([r]), np.array([h["o"]]), h["sk"], mode)
    t = S.TRANS.index(tuple(h["trans"])); P = H[0][alive[0]].astype(np.int64)
    con = np.empty(P.shape, np.float32); con[:, 0] = S.TI[t][P[:, 0]]
    con[:, 1:] = np.where(inw[1:], S.TB[t][P[:, :-1], P[:, 1:]], S.TI[t][P[:, 1:]])
    pre = con[:, :c].mean(1); cand = np.nonzero(pre >= pre.max() - 1e-6)[0]
    post = con[cand, c:].mean(1) if n > c else np.zeros(len(cand)); k = cand[int(np.argmax(post))]
    sp, a = h["trans"]; p = (sp * (P[k] - a)) % 29
    return S.render(p, pos), float(pre[k]), (float(post.max()) if n > c else float("nan")), n - c

def report():
    rs, cs = positions(); res = json.load(open(os.path.join(OUT, "results.json")))
    by = {(r["pos"], r["mode"]): r for r in res}
    print("== chance level vs restart positions: per-position maximum LL over all", end=" ")
    ids, K2, lens = oeis(); print(f"{len(ids)} sequences x {len(OS)} starts x 2 key signs x 58 maps (beam paths included)")
    summary = {}
    for mode in ("skip", "stay"):
        for c in map(str, CUTS):
            ctl = np.array([by[(p, mode)]["top"][c][0]["ll"] for p, _ in cs if c in by[(p, mode)]["top"]])
            rst = [(by[(p, mode)]["top"][c][0]["ll"], p, k) for p, k in rs if c in by[(p, mode)]["top"]]
            rv = np.array([x for x, _, _ in rst]); above = sorted([x for x in rst if x[0] > ctl.max()], reverse=True)
            pv = np.array([(1 + (ctl >= x).sum()) / (len(ctl) + 1) for x in rv])
            summary[(mode, c)] = (ctl, rst)
            print(f"   {mode:4s} cut {c}: controls n={len(ctl)} median {np.median(ctl):.3f} max {ctl.max():.3f} | "
                  f"restarts n={len(rv)} median {np.median(rv):.3f} max {rv.max():.3f} | "
                  f"{len(above)} restarts above the control max (expected {len(rv)/(len(ctl)+1):.1f}); "
                  f"rank-sum z {ranksum_z(rv, ctl):+.2f}")
            for x, p, k in above[:5]:
                print(f"         above: {k} {p}  LL {x:.3f}  {by[(p, mode)]['top'][c][0]['seq']}")
    print("\n== out of sample: each position's best hit at cut 26 and 36, decoded on to the end of its window")
    print("   (the continuation uses the hit's own map; positions with fewer than 10 continuation runes skipped)")
    oos = {}
    for mode in ("skip", "stay"):
        for c in ("26", "36"):
            grp = {}
            for lab, P in (("control", cs), ("restart", rs)):
                vals = []
                for p, k in P:
                    if c not in by[(p, mode)]["top"]: continue
                    h = by[(p, mode)]["top"][c][0]; txt, pre, post, m = decode_hit(p, h, mode, int(c))
                    if m >= 10: vals.append((post, pre, p, k, h, txt))
                grp[lab] = vals
            cv = np.array([v[0] for v in grp["control"]]); rv = np.array([v[0] for v in grp["restart"]])
            oos[(mode, c)] = grp
            print(f"   {mode:4s} cut {c}: control continuations n={len(cv)} median {np.median(cv):.3f} max {cv.max():.3f} | "
                  f"restart n={len(rv)} median {np.median(rv):.3f} max {rv.max():.3f}; {int((rv > cv.max()).sum())} above the control max "
                  f"(expected {len(rv)/(len(cv)+1):.1f})")
    print("\n== planted keys: same re-decode")
    tasks, meta = plant_ciphers(rs)
    for (pos, rule, kind, cph), (sid, _, _, L, _, sk, sp, a) in zip(tasks, meta):
        for c in ("26", "36"):
            h = dict(seq=sid, o=0, sk=sk, trans=(sp, a)); txt, pre, post, m = decode_hit(pos, h, rule, int(c), cph)
            print(f"   {sid} {rule} at {kind} {pos}, cut {c}: first {c} LL {pre:.3f}, next {m} runes LL {post:.3f}: {txt[:90]}")
    print("\n== power: would a real English opening stand above the chance ceiling? (ceiling = control max, both modes)")
    power(rs, {c: max(summary[(m, str(c))][0].max() for m in ("skip", "stay")) for c in CUTS})
    print("\n== best restart hits (top 12 by window LL over modes and cuts), decoded")
    allh = []
    for (mode, c), (ctl, rst) in summary.items():
        for x, p, k in rst: allh.append((x - ctl.max(), x, mode, c, p, k))
    allh.sort(reverse=True)
    for d, x, mode, c, p, k in allh[:12]:
        h = by[(p, mode)]["top"][c][0]; txt, pre, post, m = decode_hit(p, h, mode, int(c))
        print(f"   {mode:4s} cut {c} {k:7s} {p:5d} {h['seq']} o={h['o']} sk {h['sk']:+d} {tuple(h['trans'])}: "
              f"LL {x:.3f} ({d:+.3f} vs control max), continuation {post:.3f} over {m}: {txt[:80]}")
    return summary, oos

def power(rs, thresholds, trials=40, seed=11):
    """How often true English at these positions (LP2's own word skeleton, War and Peace words, random start in the
    book) scores above the chance ceiling at each cut, assuming the beam recovers the right path."""
    plant(rs[0][0], [0], 1, 1, 0, "skip", 0, 0)        # loads the word list
    rng = np.random.default_rng(seed); out = {c: [] for c in CUTS}
    for p, k in rs:
        n = len(S.window(RUN, p, NMAX)[0]); inw = S.inword_mask(p, n); lens_ = []
        for i in range(n):
            if inw[i]: lens_[-1] += 1
            else: lens_.append(1)
        Y = []
        for _ in range(trials):
            w = int(rng.integers(0, len(_WORDS) - 200000)); pt = []
            for L in lens_:
                while len(_WORDS[w]) != L: w += 1
                pt.extend(_WORDS[w]); w += 1
            Y.append(pt[:n])
        cuts, best, _ = score_cuts(np.array(Y), inw, CUTS)
        for q, c in enumerate(cuts): out[c].extend(best[:, q].tolist())
    for c in CUTS:
        v = np.array(out[c]); t = thresholds[c]
        print(f"   cut {c}: English at the restart positions, n={len(v)}: median {np.median(v):.3f}, "
              f"5th pct {np.percentile(v, 5):.3f}; above the control max {t:.3f}: {np.mean(v > t):.0%}")

def ranksum_z(x, y):
    a = np.concatenate([x, y]); r = a.argsort().argsort() + 1.0; n1, n2 = len(x), len(y)
    return (r[:n1].sum() - n1 * (n1 + n2 + 1) / 2) / np.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); t0 = time.time(); what = sys.argv[1] if len(sys.argv) > 1 else "run"
    if what == "run":
        rs, cs = positions()
        ids, K2, lens = oeis()
        print("== planted keys (each searched against all sequences at its own position)", flush=True)
        run_plants(rs); print(f"   ({time.time()-t0:.0f}s)", flush=True)
        print(f"{len(ids)} OEIS sequences after filter+dedupe; {len(rs)} restart positions "
              f"({', '.join(f'{k} {sum(1 for _, x in rs if x == k)}' for k in ('file', 'heading', 'after⁜', 'page'))}); "
              f"{len(cs)} control positions; rows per position per mode = {len(ids) * len(OS) * 2}", flush=True)
        tasks = [(p, m, k) for p, k in cs + rs for m in ("skip", "stay")]
        part = lambda p, m: os.path.join(OUT, "parts", f"{p}_{m}.json"); os.makedirs(os.path.join(OUT, "parts"), exist_ok=True)
        todo = [t for t in tasks if not os.path.exists(part(t[0], t[1]))]
        print(f"   {len(tasks) - len(todo)} of {len(tasks)} position-mode tasks already done (checkpoints)", flush=True)
        with Pool(int(os.environ.get("WORKERS", 6))) as pool:
            for q, r in enumerate(pool.imap_unordered(position_task, todo), 1):
                json.dump(r, open(part(r["pos"], r["mode"]), "w"))
                if q % 10 == 0: print(f"   {q}/{len(todo)} ({time.time()-t0:.0f}s)", flush=True)
        res = [json.load(open(part(p, m))) for p, m, _ in tasks]
        json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1)
        print(f"done ({time.time()-t0:.0f}s)", flush=True)
    if what in ("run", "report"):
        print(); report()
