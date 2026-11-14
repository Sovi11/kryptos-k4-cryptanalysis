#!/usr/bin/env python3
"""Heading-crib search: guess an LP2 heading's plaintext, turn it into a key-difference pattern, find that pattern
anywhere in a large library of candidate key streams, then decode the text after the heading with every match.

Model: c = sp*p + sk*K + a (mod 29). Over a crib, K_{t+1} - K_t = sk*((c_{t+1} - c_t) - sp*(p_{t+1} - p_t)); the unknown
shift a cancels, so each crib gives 4 exact patterns (sp, sk = +-1). No slip inside the heading is assumed
(probability ~0.75 for a 10-rune heading at LP2's slip rate).

Cribs: LP2 headings (text from a line/section start up to the next ⁜, at most 5 words, no sentence punctuation) with
at least 9 runes (>= 8 constrained differences). Guesses: every combination of words from Cicada's own vocabulary
(all solved LP pages) whose rune lengths match the heading's word lengths, capped at 300k per heading by keeping the
most frequent words of each length.

Library (values mod 29): all OEIS sequences at every listed position; sqrt(n) for non-square n <= 1000 and cbrt(n) for
non-cube n <= 200 (20,000 digits; 1-, 2-, 3-, 4-digit groups at every phase; and as base-29 digits); pi, e, phi, ln2
(same readings); md5/sha1/sha256/sha512 chains (bytes mod 29) seeded with every Cicada vocabulary word in three
cases; Python random (randrange(29) and int(random()*29)) for seeds 0..2000; the 104 streams of lp_keystreams.

Every pattern hit is verified by decoding the next 100 runes after the heading from the matched key index (beam,
skip and stay modes, the crib's own (sp, a)); the chance level is the same verification applied to hits on random
patterns.
"""
import os, sys, gzip, json, math, time, hashlib, random, itertools
import numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.set_int_max_str_digits(0)
import lp_skipsearch as S
import lp_repairsearch as RS
import lp_keystreams as KS
from lp_common import relikd_runes, LATIN, PUNCT, RELIKD_DIR

R, RUN, N = S.R, S.RUN, S.N
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "findings", "cribsearch_out")
OEIS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "oeis", "stripped.gz")
SEG = 600                      # key values kept from each hit onwards (enough to verify 100 runes)
LMAX = 12                      # differences hashed per window (29^12 < 2^63); longer cribs verified in full
P29 = 29 ** np.arange(LMAX - 1, -1, -1, dtype=np.int64)

# ----------------------------------------------------------------------------- headings and vocabulary
def headings():
    starts = set(i for i, x in enumerate(R) if x["first"] or x["j"] & {"⁜", "PB", "X"})
    out = []
    for s in sorted(starts):
        lens = [1]; i = s + 1; ok = False
        while i < N and R[i]["sec"] == R[s]["sec"]:
            j = R[i]["j"]
            if "⁜" in j: ok = True; break
            if j & (PUNCT - {"⁜"}) or len(lens) > 5: break
            if "•" in j: lens.append(1)
            else: lens[-1] += 1
            i += 1
        if ok and sum(lens) >= 9: out.append((s, i, tuple(lens)))
    return out

def vocabulary():
    names = sorted(f[:-4] for f in os.listdir(RELIKD_DIR) if f.startswith("solved_"))
    cnt = {}
    for nm in names:
        Q = relikd_runes([nm]); w = []
        for i, x in enumerate(Q):
            if i > 0 and (Q[i]["j"] & ({"•"} | PUNCT) or "PB" in Q[i]["j"] or "LB" in Q[i]["j"] and False):
                if w: cnt[tuple(w)] = cnt.get(tuple(w), 0) + 1
                w = []
            w.append(x["r"])
        if w: cnt[tuple(w)] = cnt.get(tuple(w), 0) + 1
    byl = {}
    for w, c in sorted(cnt.items(), key=lambda t: -t[1]): byl.setdefault(len(w), []).append(w)
    wp = {}
    for word in open(os.path.join(RELIKD_DIR, "baseline-rune-words.txt"), encoding="utf-8").read().split():
        q = tuple(S.IDX[ch] for ch in word if ch in S.IDX)
        if q: wp[q] = wp.get(q, 0) + 1
    for w, c in sorted(wp.items(), key=lambda t: -t[1]):
        lst = byl.setdefault(len(w), [])
        if len(lst) < 400 and w not in lst: lst.append(w)
    return byl

def guesses(lens, byl, cap=300000):
    lists = [list(byl.get(L, [])) for L in lens]
    if any(not l for l in lists): return []
    while math.prod(len(l) for l in lists) > cap:
        k = max(range(len(lists)), key=lambda q: len(lists[q])); lists[k] = lists[k][:max(1, int(len(lists[k]) * 0.8))]
    return [sum(ws, ()) for ws in itertools.product(*lists)]

def pattern_ints(cw, P, sp, sk):
    """P: (G, L) plaintext guesses -> int64 hash of the first min(L-1, LMAX) key differences, and full diffs."""
    dc = np.diff(cw) % 29; dp = np.diff(P, axis=1) % 29
    D = (sk * (dc[None, :] - sp * dp)) % 29
    L = min(D.shape[1], LMAX)
    return (D[:, :L] * P29[LMAX - L:]).sum(1), D

# ----------------------------------------------------------------------------- library
def stream_windows(vals, L):
    """vals: int array mod 29 (may contain -1 separators) -> (window hash of L diffs, start index of window)."""
    d = (np.diff(vals) % 29).astype(np.int64)
    bad = (vals[:-1] < 0) | (vals[1:] < 0)
    if len(d) < L: return np.zeros(0, np.int64), np.zeros(0, np.int64)
    W = np.lib.stride_tricks.sliding_window_view(d, L) @ P29[LMAX - L:]
    badw = np.lib.stride_tricks.sliding_window_view(bad, L).any(1)
    idx = np.nonzero(~badw)[0]
    return W[idx], idx

def digits_to_streams(name, digs):
    out = []
    for g in (1, 2, 3, 4):
        for ph in range(g):
            dd = digs[ph:]; m = len(dd) // g
            out.append((f"{name}/{g}d/ph{ph}", np.array([int(dd[i * g:(i + 1) * g]) for i in range(m)], np.int64) % 29))
    return out

def base29(num, den, n):
    """First n base-29 digits of the fraction num/den (0 <= num < den)."""
    x = num * 29 ** n // den; out = []
    for _ in range(n): x, r = divmod(x, 29); out.append(r)
    return np.array(out[::-1], np.int64)

def icbrt(n):
    x = 1 << ((n.bit_length() + 2) // 3)
    while True:
        y = (2 * x + n // (x * x)) // 3
        if y >= x: break
        x = y
    while x ** 3 > n: x -= 1
    while (x + 1) ** 3 <= n: x += 1
    return x

ND = 20000
def lib_chunk(spec):
    """Generate one chunk of the library -> list of (name, values)."""
    kind = spec[0]; out = []
    if kind == "sqrt":
        for n in spec[1]:
            r = math.isqrt(n)
            if r * r == n: continue
            X = math.isqrt(n * 10 ** (2 * ND)); out += digits_to_streams(f"sqrt{n}", str(X)[:ND])
            Y = math.isqrt(n * 29 ** (2 * 14000)); out.append((f"sqrt{n}/base29", base29(Y % 29 ** 14000, 29 ** 14000, 14000)))
    elif kind == "cbrt":
        for n in spec[1]:
            r = icbrt(n)
            if r ** 3 == n: continue
            X = icbrt(n * 10 ** (3 * ND)); out += digits_to_streams(f"cbrt{n}", str(X)[:ND])
            Y = icbrt(n * 29 ** (3 * 14000)); out.append((f"cbrt{n}/base29", base29(Y % 29 ** 14000, 29 ** 14000, 14000)))
    elif kind == "const":
        for name, f in (("pi", KS.digits_pi), ("e", KS.digits_e), ("phi", KS.digits_phi), ("ln2", KS.digits_ln2)):
            d = f(ND + 50); out += digits_to_streams(name, d[:ND])
            ip = 1 if name == "ln2" else 1
            num, den = int(d[ip:ND + 40]), 10 ** (ND + 40 - ip)      # fractional part
            out.append((f"{name}/base29", base29(num, den, 14000)))
    elif kind == "hash":
        for w in spec[1]:
            for seed in (w, w.lower(), w.capitalize()):
                for algo in ("md5", "sha1", "sha256", "sha512"):
                    out.append((f"{algo}('{seed}')", KS.hash_chain(seed, algo, 8000)))
    elif kind == "prng":
        for sd in spec[1]:
            r = random.Random(sd); out.append((f"py3-rand({sd})", np.array([r.randrange(29) for _ in range(8000)], np.int64)))
            r = random.Random(sd); out.append((f"py2-rand({sd})", np.array([int(r.random() * 29) for _ in range(8000)], np.int64)))
    elif kind == "ks":
        for name, s in KS.all_streams(): out.append((name, KS.build(s)))
    elif kind == "oeis":
        vals, names, starts = [], [], []
        for line in gzip.open(OEIS, "rt"):
            if line[0] == "#": continue
            aid, _, rest = line.partition(" ")
            t = [int(x) % 29 for x in rest.strip().strip(",").split(",") if x]
            starts.append(len(vals)); names.append(aid); vals.extend(t); vals.append(-1)
        out.append(("OEIS", np.array(vals, np.int64), (names, np.array(starts))))
    return out

_PAT = {}
def init_worker(pat): _PAT.update(pat)

def search_chunk(args):
    spec, which = args; PAT = _PAT[which]
    t = time.time(); hits = []; nvals = 0
    for item in lib_chunk(spec):
        name, vals = item[0], item[1]; nvals += len(vals)
        for L, pats in PAT.items():
            W, idx = stream_windows(vals, L)
            if not len(W): continue
            q = np.minimum(np.searchsorted(pats, W), len(pats) - 1)
            for k in np.nonzero(pats[q] == W)[0]:
                pos = int(idx[k]); nm = name; seg = vals[pos:pos + SEG]
                if len(item) > 2:                                   # OEIS: map back to sequence and term index
                    names, starts = item[2]; j = int(np.searchsorted(starts, pos, side="right") - 1)
                    nm = names[j]; pos = pos - int(starts[j]); seg = seg[:np.argmax(seg < 0)] if (seg < 0).any() else seg
                hits.append((nm, pos, L, int(W[k]), seg.astype(np.int8).tolist()))
    return hits, nvals, spec[0], time.time() - t

def library_specs():
    byl = vocabulary(); words = sorted(set("".join(LATIN[v] for v in w) for L in byl for w in byl[L]))
    specs = [("ks",), ("const",), ("oeis",)]
    ns = list(range(2, 1001)); specs += [("sqrt", ns[i::24]) for i in range(24)]
    cs = list(range(2, 201)); specs += [("cbrt", cs[i::8]) for i in range(8)]
    specs += [("hash", words[i::16]) for i in range(16)]
    sd = list(range(0, 2001)); specs += [("prng", sd[i::16]) for i in range(16)]
    return specs

# ----------------------------------------------------------------------------- verification
def get_stream(name):
    """Rebuild a library stream by name (for verification)."""
    if name.startswith("A") and name[1:].isdigit():
        for line in gzip.open(OEIS, "rt"):
            if line.startswith(name + " "):
                return np.array([int(x) % 29 for x in line.partition(" ")[2].strip().strip(",").split(",") if x], np.int64)
    for spec in library_specs():
        if spec[0] == "oeis": continue
        for item in lib_chunk(spec):
            if item[0] == name: return item[1]
    raise KeyError(name)

def verify(start, K, kidx, sp, sk, a, mode, n=100):
    """Decode up to n runes at LP2 position `start` from key index kidx (as far as the stream has terms)."""
    n = min(n, len(K) - kidx - 4)
    cw, cprev = S.window(RUN, start, n)
    if n < 15 or len(cw) < 15: return None
    Kp = np.concatenate([K, np.random.default_rng(7).integers(0, 29, 3 * len(cw) + 10)])
    Y = RS.beam(cw, cprev, Kp, np.array([kidx]), sk, mode)[1]
    t = S.TRANS.index((sp, a)); inw = S.inword_mask(start, len(cw))
    P = (Y[:, :-1] * 29 + Y[:, 1:])[:, inw[1:]]; I = Y[:, ~inw]
    return float(((S.TB[t].reshape(-1)[P].sum(1) + S.TI[t][I].sum(1)) / len(cw))[0]), Y[0], len(cw)

def build_patterns(H, byl, control=False):
    """Per hash length L: sorted hashes plus (heading, guess, sp, sk) for each, and the guesses themselves."""
    rng = np.random.default_rng(29); per = {}; GUESS = {}
    for hid, (s, e, lens) in enumerate(H):
        G = guesses(lens, byl)
        if not G: continue
        Pm = np.array(G, np.int64)
        if control: Pm = rng.integers(0, 29, Pm.shape)
        GUESS[hid] = Pm
        for ci, (sp, sk) in enumerate(((1, 1), (1, -1), (-1, 1), (-1, -1))):
            hsh, D = pattern_ints(RUN[s:e], Pm, sp, sk); L = min(D.shape[1], LMAX)
            per.setdefault(L, []).append((hsh, np.full(len(hsh), hid, np.int16), np.arange(len(hsh), dtype=np.int32),
                                          np.full(len(hsh), ci, np.int8)))
    TAB = {}
    for L, parts in per.items():
        hv = np.concatenate([p[0] for p in parts]); o = np.argsort(hv, kind="stable")
        TAB[L] = (hv[o], np.concatenate([p[1] for p in parts])[o], np.concatenate([p[2] for p in parts])[o],
                  np.concatenate([p[3] for p in parts])[o])
    return TAB, GUESS

def verify_hits(hits, H, TAB, GUESS, cache):
    rows = []
    for nm, kpos, L, hv, seg in hits:
        hvs, hid, gid, cid = TAB[L]; lo, hi = np.searchsorted(hvs, hv), np.searchsorted(hvs, hv, side="right")
        K = np.array(seg, np.int64); pos = 0
        for q in range(lo, hi):
            s, e, lens = H[int(hid[q])]; p = GUESS[int(hid[q])][int(gid[q])]
            sp, sk = ((1, 1), (1, -1), (-1, 1), (-1, -1))[int(cid[q])]
            D = (sk * ((np.diff(RUN[s:e]) % 29) - sp * (np.diff(p) % 29))) % 29
            if len(K) < pos + len(D) + 1 or not np.array_equal(np.diff(K[pos:pos + len(D) + 1]) % 29, D): continue
            a = int((RUN[s] - sp * p[0] - sk * K[pos]) % 29)
            for mode in ("skip", "stay"):
                v = verify(e, K, pos + (e - s), sp, sk, a, mode)
                if v: rows.append(dict(stream=nm, kidx=int(kpos), heading=int(s), guess=".".join(
                    "".join(LATIN[x] for x in p[c0:c0 + Lw]) for c0, Lw in zip(np.cumsum((0,) + lens[:-1]), lens)),
                    sp=sp, sk=sk, a=a, mode=mode, ll=v[0], n=v[2], text=S.render((sp * (v[1] - a)) % 29, e)[:90]))
    return rows

# ----------------------------------------------------------------------------- planted controls
PLANTS = [  # heading index, guess index, library stream, key index, rule, sk, sp, a
    (2, 777, "sqrt7/4d/ph1", 1234, "skip", 1, 1, 5),
    (5, 4321, "A000040", 2, "stay", -1, -1, 17),
]

def run_plants():
    """Encrypt a heading (a guess from the vocabulary) plus the following text (LP2's word skeleton filled with War and
    Peace words) with a library stream, then search that stream's whole library chunk blind and verify."""
    global RUN
    H = headings(); byl = vocabulary(); orig = RUN.copy(); rng = np.random.default_rng(5)
    words = [[S.IDX[c] for c in w if c in S.IDX] for w in
             open(os.path.join(RELIKD_DIR, "baseline-rune-words.txt"), encoding="utf-8").read().split()]
    specs = library_specs()
    for hi, gi, name, kidx, rule, sk, sp, a in PLANTS:
        s, e, lens = H[hi]; p_head = list(guesses(lens, byl)[gi])
        if name.startswith("A"): spec = ("oeis",); K = get_stream(name)
        else:
            n = int(name[4:].split("/")[0]); spec = next(x for x in specs if x[0] == "sqrt" and n in x[1])
            K = next(v for nm, v in lib_chunk(spec) if nm == name)
        en = e
        while en < N and R[en]["sec"] == R[s]["sec"] and en - e < 200: en += 1
        inw = S.inword_mask(e, en - e); Ls = []
        for i in range(en - e):
            if inw[i]: Ls[-1] += 1
            else: Ls.append(1)
        w = int(rng.integers(0, 300000)); pt = []
        for L in Ls:
            while len(words[w]) != L: w += 1
            pt.extend(words[w]); w += 1
        P = p_head + pt[:en - e]; Kx = list(K[kidx:]) + rng.integers(0, 29, 1000).tolist()
        c = orig.copy(); jj = 0; prev = int(orig[s - 1]); nrep = 0
        for i in range(s, en):
            p = P[i - s]; v = (sp * p + sk * Kx[jj] + a) % 29; adv = 1
            if v == prev and i >= e and rng.random() < 0.81:        # no repair inside the heading (the search assumes none)
                nrep += 1
                if rule == "skip": jj += 1; v = (sp * p + sk * Kx[jj] + a) % 29
                else: v = (sp * p + a) % 29; adv = 0
            c[i] = v; jj += adv; prev = int(v)
        RUN = c
        TAB, GUESS = build_patterns(H, byl); init_worker({"real": {L: v[0] for L, v in TAB.items()}})
        hits, nv, kind, dt = search_chunk((spec, "real"))
        rows = verify_hits(hits, H, TAB, GUESS, None); rows.sort(key=lambda r: -r["ll"])
        truth = "".join(LATIN[x] for x in p_head); ttxt = S.render(np.array(P[e - s:]), e).replace(".", "").split()
        top = rows[0]; got = top["text"].replace(".", "").split()[:-1]       # text is cut at 90 chars: drop the last word
        wc = np.mean([x == y for x, y in zip(got, ttxt)])
        ok = top["guess"].replace(".", "") == truth and wc > 0.8
        print(f"   PLANT heading {s}, guess {truth}, key {name} from index {kidx}, {rule}, (sk, sp, a) = ({sk:+d}, {sp:+d}, {a}); "
              f"{nrep} repairs after the heading\n      {len(hits)} raw hits in the whole '{spec[0]}' library chunk ({nv:,} values); "
              f"top verified: {top['stream']} index {top['kidx']}, guess {top['guess']}, {top['mode']}, LL {top['ll']:.3f} over {top['n']}, "
              f"{wc:.0%} of words correct -> {'FOUND' if ok else 'MISSED'}\n      {top['text'][:80]}", flush=True)
    RUN = orig

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); t0 = time.time()
    if sys.argv[1:] == ["plants"]:
        run_plants(); sys.exit()
    H = headings(); byl = vocabulary()
    print(f"vocabulary: Cicada's solved-page words first, then War and Peace words, up to 400 per length; "
          f"headings with >= 9 runes: {len(H)}")
    for s, e, lens in H:
        print(f"   heading at {s:5d} (file {R[s]['sec']}): word lengths {lens}, {len(guesses(lens, byl))} guesses")
    TAB, GUESS = build_patterns(H, byl); CTAB, CGUESS = build_patterns(H, byl, control=True)
    print(f"patterns by hashed length: { {L: len(v[0]) for L, v in TAB.items()} } (x2 with the random-guess control)", flush=True)
    RAW = os.path.join(os.path.dirname(OEIS), "..", "cribsearch_raw_hits.json.gz")      # gitignored checkpoint
    SMOKE = bool(os.environ.get("SMOKE"))                  # quick end-to-end test on two small library chunks
    if SMOKE: RAW += ".smoke"; OUT = os.path.join(os.path.dirname(OEIS), "..")
    if os.path.exists(RAW):
        res, total = json.load(gzip.open(RAW, "rt")); print("raw hits loaded from checkpoint", RAW, flush=True)
    else:
        specs = library_specs()[:2] if SMOKE else library_specs(); res = {"real": [], "ctrl": []}; total = 0
        tasks = [(sp_, w) for w in ("real", "ctrl") for sp_ in specs]
        with Pool(int(os.environ.get("WORKERS", 6)), initializer=init_worker,
                  initargs=({"real": {L: v[0] for L, v in TAB.items()}, "ctrl": {L: v[0] for L, v in CTAB.items()}},)) as pool:
            for q, ((h, nv, kind, dt), (_, w)) in enumerate(zip(pool.imap(search_chunk, tasks), tasks), 1):
                res[w] += h; total += nv if w == "real" else 0
                if q % 12 == 0: print(f"   {q}/{len(tasks)} library chunks ({time.time()-t0:.0f}s)", flush=True)
        with gzip.open(RAW, "wt") as f: json.dump([res, total], f)
    print(f"library: {total:,} key values; raw pattern hits: real guesses {len(res['real'])}, random guesses {len(res['ctrl'])} "
          f"({time.time()-t0:.0f}s)", flush=True)
    rows = verify_hits(res["real"], H, TAB, GUESS, None); crow = verify_hits(res["ctrl"], H, CTAB, CGUESS, None)
    rows.sort(key=lambda r: -r["ll"]); crow.sort(key=lambda r: -r["ll"])
    def summ(rr):
        if not rr: return "none"
        a = np.array([r["ll"] for r in rr]); return f"n={len(rr)}, median {np.median(a):.3f}, max {a.max():.3f}"
    print(f"verified decodes after the heading: real guesses {summ(rows)}; random guesses {summ(crow)}")
    for r in rows[:15]:
        print(f"   {r['stream']:26s} k={r['kidx']:6d} heading {r['heading']:5d} guess {r['guess']:24s} (sp,sk,a)=({r['sp']:+d},{r['sk']:+d},{r['a']:2d}) "
              f"{r['mode']:4s} LL {r['ll']:.3f} over {r['n']}: {r['text'][:50]}")
    json.dump(dict(real=rows, control=crow), open(os.path.join(OUT, "verified.json"), "w"), indent=1)
    print(f"({time.time()-t0:.0f}s)")
