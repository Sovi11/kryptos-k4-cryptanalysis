"""search_ksbattery.py -- a VALIDATED battery of structure tests for an implied key stream.

Given a candidate 97-letter plaintext P and the K4 ciphertext C, each of the 24
cipher/alphabet combos determines a key stream K position by position.  If the candidate
plaintext is right and the cipher is in that family, K must be *something* -- a keyword
repeated, a running key from a text, an arithmetic sequence, digits of something.  If K
is indistinguishable from random under every test, then either the plaintext is wrong or
the cipher is outside the family (which is the whole point of reporting it honestly).

A negative from this battery is only worth anything if the battery can DETECT structure
when it is there.  `validate` therefore measures detection power on synthetic key streams
of each kind before any real candidate is scored.

Tests
  ioc        index of coincidence of K
  per        best period 2..48 by modal-agreement excess over a Monte-Carlo null
  rep        number of repeated 4-grams in K (Kasiski signal)
  quad       calibrated quadgram score of K (is the key itself English?)
  lcs_scu    longest common substring with the sculpture corpus (K1-K3, panels, tableau, Morse)
  lcs_lat    longest common substring with the lateral corpus (Berlin clock, Antipodes Cyrillic,
             Cyrillic Projector, compass bearings, Alexanderplatz world clock -- 194 streams)
  run        longest run of an identical shift
  ap         longest arithmetic progression in the shift sequence (constant first difference)
  d1         count of the modal first difference (a Trithemius/progressive signal)
  ac         max autocorrelation z of the shift sequence over lags 1..32

Usage:
    python3.13 search_ksbattery.py validate
    python3.13 search_ksbattery.py claims
    python3.13 search_ksbattery.py annealed [n]
"""
import glob, json, math, os, random, re, statistics as st, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import search_lm
import runningkey_lib as RK

A2Z = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CT = RK.K4_CT
COMBOS = list(RK.combos())

# ------------------------------------------------------------------ corpora
_SCU = None
def sculpture_corpus():
    global _SCU
    if _SCU is None:
        _SCU = RK.corpus()
    return _SCU

_LAT = None
def lateral_corpus():
    """The 194 lateral keystreams built in lateral/keystreams/ (Berlin clock, Antipodes,
    Cyrillic Projector, compass rose, Alexanderplatz)."""
    global _LAT
    if _LAT is None:
        d = {}
        for p in sorted(glob.glob(os.path.join(ROOT, "lateral", "keystreams", "*.txt"))):
            t = re.sub("[^A-Z]", "",
                       open(p, encoding="utf-8", errors="ignore").read().upper())
            if len(t) >= 5:
                d[os.path.basename(p)] = t
        _LAT = d
    return _LAT

def _subs(corpus, lo=5, hi=12):
    d = {}
    for name, t in corpus.items():
        for L in range(lo, hi + 1):
            for i in range(len(t) - L + 1):
                d.setdefault(t[i:i + L], name)
    return d

_SUBS = {}
def subs_for(which):
    if which not in _SUBS:
        _SUBS[which] = _subs(sculpture_corpus() if which == "scu" else lateral_corpus())
    return _SUBS[which]

def lcs_with(s, which, lo=5, hi=12):
    d = subs_for(which)
    best = ("", None)
    for L in range(hi, lo - 1, -1):
        for i in range(len(s) - L + 1):
            sub = s[i:i + L]
            if sub in d:
                return sub, d[sub]
    return best

# ------------------------------------------------------------------ stats
def ioc(s):
    n = len(s)
    c = Counter(s)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1))

_EXP = {}
def expected_modal(n, trials=6000):
    if n in _EXP:
        return _EXP[n]
    if n <= 1:
        _EXP[n] = float(n); return float(n)
    rnd = random.Random(1234 + n)
    tot = 0
    for _ in range(trials):
        tot += Counter(rnd.randrange(26) for _ in range(n)).most_common(1)[0][1]
    _EXP[n] = tot / trials
    return _EXP[n]

def best_period(s, pmax=48):
    best = (0, 0.0, 0.0, 0.0)
    for p in range(2, pmax + 1):
        agree = exp = 0.0
        for r in range(p):
            cls = s[r::p]
            if not cls:
                continue
            agree += Counter(cls).most_common(1)[0][1]
            exp += expected_modal(len(cls))
        ex = (agree - exp) / len(s)
        if ex > best[3]:
            best = (p, agree / len(s), exp / len(s), ex)
    return best                     # (p, agree, expected, excess)

def rep4(s):
    c = Counter(s[i:i + 4] for i in range(len(s) - 3))
    return sum(v - 1 for v in c.values() if v > 1)

def max_run(seq):
    b = c = 1
    for i in range(1, len(seq)):
        c = c + 1 if seq[i] == seq[i - 1] else 1
        b = max(b, c)
    return b

def longest_ap(sh):
    """Longest run with a constant first difference mod 26 (>=3 counts as an AP)."""
    n = len(sh)
    best = 1
    i = 0
    while i < n - 1:
        d = (sh[i + 1] - sh[i]) % 26
        j = i + 1
        while j < n - 1 and (sh[j + 1] - sh[j]) % 26 == d:
            j += 1
        best = max(best, j - i + 1)
        i = j if j > i else i + 1
    return best

def autocorr_z(sh, lagmax=32):
    """Max over lags of the z-score of 'number of positions where shift repeats at that lag'."""
    n = len(sh)
    best = (0, 0.0)
    for lag in range(1, lagmax + 1):
        m = n - lag
        if m < 12:
            break
        k = sum(1 for i in range(m) if sh[i] == sh[i + lag])
        mu = m / 26.0
        sd = math.sqrt(m * (1 / 26.0) * (25 / 26.0))
        z = (k - mu) / sd if sd else 0.0
        if z > best[1]:
            best = (lag, z)
    return best

def shifts(ks, cb):
    Ak = RK.ALPHAS[cb[3]]
    return [Ak.index(c) for c in ks]

def battery(ks, cb):
    sh = shifts(ks, cb)
    d1 = [(sh[i + 1] - sh[i]) % 26 for i in range(len(sh) - 1)]
    p, agree, exp, ex = best_period(ks)
    lag, az = autocorr_z(sh)
    s_scu, n_scu = lcs_with(ks, "scu")
    s_lat, n_lat = lcs_with(ks, "lat")
    return dict(ioc=ioc(ks), period=p, per_excess=ex, rep4=rep4(ks),
                quad=search_lm.quad(ks), lcs_scu=s_scu, lcs_scu_src=n_scu,
                lcs_lat=s_lat, lcs_lat_src=n_lat, run=max_run(sh), ap=longest_ap(sh),
                d1=Counter(d1).most_common(1)[0][1], ndistinct=len(set(sh)),
                ac_lag=lag, ac_z=az)

# ------------------------------------------------------------------ null
NULLFILE = os.path.join(HERE, "search_ksbattery_null.json")

def build_null(n=4000, seed=20260913):
    """Null: uniform-random 97-letter key streams.  (The key stream of a WRONG plaintext
    under any of these combos is a bijective relabelling of that plaintext, so a random
    plaintext gives a random key stream; verified below.)"""
    if os.path.exists(NULLFILE):
        with open(NULLFILE) as f:
            return json.load(f)
    rnd = random.Random(seed)
    keys = ["ioc", "per_excess", "rep4", "quad", "run", "ap", "d1", "ndistinct", "ac_z"]
    acc = {k: [] for k in keys}
    mscu = mlat = 0
    cb = ("vigenere", "plain", "plain", "plain")
    for _ in range(n):
        ks = "".join(A2Z[rnd.randrange(26)] for _ in range(97))
        b = battery(ks, cb)
        for k in keys:
            acc[k].append(b[k])
        mscu += 1 if b["lcs_scu"] else 0
        mlat += 1 if b["lcs_lat"] else 0
    out = {k: dict(mean=st.mean(v), sd=st.pstdev(v),
                   p99=sorted(v)[int(0.99 * len(v))], mx=max(v)) for k, v in acc.items()}
    out["_lcs_scu_rate"] = mscu / n
    out["_lcs_lat_rate"] = mlat / n
    out["_n"] = n
    with open(NULLFILE, "w") as f:
        json.dump(out, f, indent=1)
    return out

def zrow(b, null):
    return {k: (b[k] - null[k]["mean"]) / null[k]["sd"] if null[k]["sd"] else 0.0
            for k in ("ioc", "per_excess", "rep4", "quad", "run", "ap", "d1", "ndistinct", "ac_z")}

# ------------------------------------------------------------------ validation
def synth_keys(kind, n=97, seed=0):
    rnd = random.Random(seed)
    if kind == "random":
        return "".join(A2Z[rnd.randrange(26)] for _ in range(n))
    if kind.startswith("periodic"):
        p = int(kind.split("-")[1])
        kw = "".join(A2Z[rnd.randrange(26)] for _ in range(p))
        return "".join(kw[i % p] for i in range(n))
    if kind == "english":
        _, _, hold = search_lm.load()
        i = rnd.randrange(0, len(hold) - n - 1)
        return hold[i:i + n]
    if kind == "sculpture":
        c = sculpture_corpus()
        name = rnd.choice([k for k, v in c.items() if len(v) >= n + 1])
        t = c[name]
        i = rnd.randrange(0, len(t) - n)
        return t[i:i + n]
    if kind == "lateral":
        c = lateral_corpus()
        cand = [k for k, v in c.items() if len(v) >= n + 1]
        t = c[rnd.choice(cand)]
        i = rnd.randrange(0, len(t) - n)
        return t[i:i + n]
    if kind == "progressive":
        a = rnd.randrange(26); d = rnd.randrange(1, 26)
        return "".join(A2Z[(a + d * i) % 26] for i in range(n))
    if kind == "quadratic":
        a, b, c0 = rnd.randrange(26), rnd.randrange(26), rnd.randrange(26)
        return "".join(A2Z[(a * i * i + b * i + c0) % 26] for i in range(n))
    if kind == "digits":                       # Gronsfeld-style: shifts 0..9 only
        return "".join(A2Z[rnd.randrange(10)] for i in range(n))
    if kind == "autokey":                      # key = English primer then the plaintext
        _, _, hold = search_lm.load()
        i = rnd.randrange(0, len(hold) - n - 1)
        return hold[i:i + n]
    raise ValueError(kind)

def validate(trials=200):
    null = build_null()
    cb = ("vigenere", "plain", "plain", "plain")
    kinds = ["random", "periodic-5", "periodic-7", "periodic-11", "periodic-17",
             "periodic-26", "english", "sculpture", "lateral", "progressive",
             "quadratic", "digits"]
    print("=" * 108)
    print(f"TABLE B0 -- DETECTION POWER of the battery.  {trials} synthetic key streams of each kind;")
    print("            entries are the % of streams flagged by that test at |z| >= 3 (or a corpus hit).")
    print("=" * 108)
    cols = ["ioc", "per_excess", "rep4", "quad", "run", "ap", "d1", "ndistinct", "ac_z"]
    print(f"{'key-stream kind':16s}" + "".join(f"{c:>11s}" for c in cols) + f"{'lcs_scu':>9s}{'lcs_lat':>9s}{'ANY':>6s}")
    rows = {}
    for kind in kinds:
        flags = {c: 0 for c in cols}
        hs = hl = anyf = 0
        for t in range(trials):
            ks = synth_keys(kind, seed=t * 31 + 7)
            b = battery(ks, cb)
            z = zrow(b, null)
            f = False
            for c in cols:
                if abs(z[c]) >= 3.0:
                    flags[c] += 1; f = True
            if b["lcs_scu"]:
                hs += 1; f = True
            if b["lcs_lat"]:
                hl += 1; f = True
            if f:
                anyf += 1
        rows[kind] = (flags, hs, hl, anyf)
        print(f"{kind:16s}" + "".join(f"{100.0*flags[c]/trials:10.0f}%" for c in cols)
              + f"{100.0*hs/trials:8.0f}%{100.0*hl/trials:8.0f}%{100.0*anyf/trials:5.0f}%")
    print()
    print("The 'random' row is the FALSE-POSITIVE rate of the battery; every other row is power.")
    return rows

# ------------------------------------------------------------------ scoring
def keystream(cb, pt):
    return "".join(RK.derive_key_letter(cb, p, c) for p, c in zip(pt, CT))

def score_plaintext(pt, label, null=None, verbose=True, top=None):
    null = null or build_null()
    rows = []
    for cb in COMBOS:
        ks = keystream(cb, pt)
        b = battery(ks, cb)
        b["combo"] = RK.combo_name(cb)
        b["key"] = ks
        b["z"] = zrow(b, null)
        rows.append(b)
    if verbose:
        print(f"--- {label}")
        print(f"    PT  {pt}")
        print(f"    PT quad {search_lm.quad(pt):+.4f}  (English -0.741+-0.077; Sanborn K1-K3 -0.967)")
        cols = ["ioc", "per_excess", "quad", "rep4", "run", "ap", "d1", "ac_z"]
        print(f"    {'combo':40s}" + "".join(f"{'z'+c:>10s}" for c in cols) + "   corpus hits")
        for r in sorted(rows, key=lambda r: -max(abs(v) for v in r["z"].values())):
            hits = []
            if r["lcs_scu"]:
                hits.append(f"SCU:{r['lcs_scu']}({r['lcs_scu_src']})")
            if r["lcs_lat"]:
                hits.append(f"LAT:{r['lcs_lat']}({r['lcs_lat_src']})")
            print(f"    {r['combo']:40s}" + "".join(f"{r['z'][c]:+10.2f}" for c in cols)
                  + "   " + " ".join(hits))
        mx = max(rows, key=lambda r: max(abs(v) for v in r["z"].values()))
        m = max(abs(v) for v in mx["z"].values())
        print(f"    LARGEST |z| anywhere in the 24x9 grid: {m:.2f}  ({mx['combo']})")
        print(f"    Expected largest |z| over 216 independent N(0,1) draws: about 3.0 "
              f"(P(max>3.5) ~ {1-(1-2*0.000233)**216:.2f}).")
    return rows

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "validate"
    if mode == "null":
        print(json.dumps(build_null(), indent=1))
    elif mode == "validate":
        validate(int(sys.argv[2]) if len(sys.argv) > 2 else 200)
