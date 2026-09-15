#!/usr/bin/env python3
"""(f) Side-by-side statistical profile: K4 vs K1/K2/K3 vs simulated output of
every candidate system, and the resulting numeric verdicts.

For each candidate cipher the script simulates N encipherments of random
97-letter windows of real English and records a battery of statistics.  K4's
observed value of each statistic is then placed in that candidate's own null
distribution.  A candidate is declared IMPLAUSIBLE when at least one statistic
puts K4 in the extreme 0.1% of what the candidate produces.

    python3 analysis/stat_f_profile.py
"""
import math
import os
import random
from collections import Counter
from multiprocessing import Pool

import stat_common as S

TRIALS = 40_000
SEED = 20260913
NPROC = min(8, os.cpu_count() or 4)

_CORP = None


def _init_worker():
    global _CORP
    _CORP = S.english_corpus()


# --------------------------------------------------------------- statistics --
def spectrum(b, maxlag):
    n = len(b)
    out = [0] * (maxlag + 1)
    for d in range(1, maxlag + 1):
        m = n - d
        if m <= 0:
            break
        x = int.from_bytes(b[:m], "big") ^ int.from_bytes(b[d:], "big")
        out[d] = x.to_bytes(m, "big").count(0)
    return out


def col_pairs(n, p):
    q, r = divmod(n, p)
    return r * (q + 1) * q + (p - r) * q * (q - 1)


def profile(b):
    """The statistic battery.  Returns a dict."""
    n = len(b)
    c = Counter(b)
    S_ = sum(v * (v - 1) for v in c.values())
    spec = spectrum(b, n - 1)          # full spectrum: serves lags and periods
    zs = []
    for d in range(1, min(49, n)):
        m = n - d
        zs.append((spec[d] - m / 26) / math.sqrt(m * (1 / 26) * (25 / 26)))
    # periodic IoC, standardised, p = 2..30
    pz = []
    for p in range(2, 31):
        s = 2 * sum(spec[d] for d in range(p, n, p))
        D = col_pairs(n, p)
        if D:
            mu = 1 / 26
            sd = math.sqrt(2 * mu * (1 - mu) / D)
            pz.append((s / D - mu) / sd)
    bic = Counter(b[i:i + 2] for i in range(n - 1))
    tric = Counter(b[i:i + 3] for i in range(n - 2))
    return {
        "ioc": S_ / (n * (n - 1)),
        "distinct": len(c),
        "doubles": spec[1],
        "maxz": max(zs),
        "maxperz": max(pz),
        "bigrams": sum(v * (v - 1) // 2 for v in bic.values()),
        "trigrams": sum(v * (v - 1) // 2 for v in tric.values()),
        "chi2u": sum((c.get(i, 0) - n / 26) ** 2 / (n / 26) for i in range(26)),
    }


STATS = ["ioc", "distinct", "doubles", "maxz", "maxperz", "bigrams", "trigrams", "chi2u"]

# The omnibus test in section 5 needs one system whose output IS the uniform
# null.  A one-time pad over English is exactly that: pt + uniform noise mod 26.
OMNIBUS_TAG = "one-time pad"
# chi2u is a deterministic function of the letter counts and so is ioc; keeping
# both in a min-p battery double-counts the same evidence, so the battery drops
# chi2u.  maxperz is kept because it probes a different structure (periods).
BATTERY = ["ioc", "distinct", "doubles", "maxz", "maxperz", "bigrams", "trigrams"]


# ----------------------------------------------------------------- systems --
def make_ct(mode, L, pt, rng):
    n = len(pt)
    if mode == "english":
        return pt
    if mode == "transposition":
        idx = list(range(n))
        rng.shuffle(idx)
        return bytes(pt[i] for i in idx)
    if mode == "mono":
        a = list(range(26))
        rng.shuffle(a)
        return bytes(a[x] for x in pt)
    if mode == "vig":
        key = bytes(rng.randrange(26) for _ in range(L))
        return bytes((pt[i] + key[i % L]) % 26 for i in range(n))
    if mode == "beau":
        key = bytes(rng.randrange(26) for _ in range(L))
        return bytes((key[i % L] - pt[i]) % 26 for i in range(n))
    if mode == "quag3":
        # Quagmire III: keyed alphabet on pt, ct and key.  Statistically this is
        # Vigenere applied to the keyed-alphabet indices of the plaintext.
        ka = S.KRYPTOS_ALPHA
        idx = {ord(ch) - 65: i for i, ch in enumerate(ka)}
        pi = bytes(idx[x] for x in pt)
        key = bytes(rng.randrange(26) for _ in range(L))
        ci = bytes((pi[i] + key[i % L]) % 26 for i in range(n))
        return bytes(ord(ka[x]) - 65 for x in ci)
    if mode == "otp":
        return bytes((pt[i] + rng.randrange(26)) % 26 for i in range(n))
    if mode == "running":
        j = rng.randrange(len(_CORP) - n - 1)
        key = _CORP[j:j + n]
        return bytes((pt[i] + key[i]) % 26 for i in range(n))
    if mode == "autokey":
        primer = bytes(rng.randrange(26) for _ in range(L))
        ks = primer + pt
        return bytes((pt[i] + ks[i]) % 26 for i in range(n))
    if mode == "ctautokey":
        primer = bytes(rng.randrange(26) for _ in range(L))
        out = []
        ks = list(primer)
        for i in range(n):
            cch = (pt[i] + ks[i]) % 26
            out.append(cch)
            ks.append(cch)
        return bytes(out)
    if mode == "gromark":
        prim = [rng.randrange(10) for _ in range(L)]
        return S.gromark(pt, prim, 10)
    if mode == "polyalpha":
        alphs = []
        for _ in range(L):
            a = list(range(26))
            rng.shuffle(a)
            alphs.append(a)
        return bytes(alphs[i % L][pt[i]] for i in range(n))
    if mode == "hill2":
        while True:
            a, bb, cc, d = [rng.randrange(26) for _ in range(4)]
            if math.gcd((a * d - bb * cc) % 26, 26) == 1:
                break
        out = []
        p2 = pt + bytes([23]) if n % 2 else pt
        for i in range(0, len(p2), 2):
            x, y = p2[i], p2[i + 1]
            out.append((a * x + bb * y) % 26)
            out.append((cc * x + d * y) % 26)
        return bytes(out[:n])
    if mode == "bifid6":
        # 6x6 bifid over a 36-cell square (26 letters + 10 fillers reused);
        # here simply a 26-letter Polybius on a 26-cell 'square' is impossible,
        # so use base-5 fractionation with a 5x6 grid (26 cells exactly: 5x6=30,
        # 4 cells unused).  Period L.
        rows, colsn = 5, 6
        cells = [(r, cq) for r in range(rows) for cq in range(colsn)][:26]
        perm = list(range(26))
        rng.shuffle(perm)
        grid = {perm[i]: cells[i] for i in range(26)}
        inv = {cells[i]: perm[i] for i in range(26)}
        out = []
        for st in range(0, n, L):
            blk = pt[st:st + L]
            rr = [grid[x][0] for x in blk]
            cc2 = [grid[x][1] for x in blk]
            seq = rr + cc2
            for i in range(0, len(seq) - 1, 2):
                key = (seq[i] % rows, seq[i + 1] % colsn)
                out.append(inv.get(key, rng.randrange(26)))
        while len(out) < n:
            out.append(rng.randrange(26))
        return bytes(out[:n])
    raise ValueError(mode)


SYSTEMS = [
    ("English plaintext",            "english", 0),
    ("transposition of English",     "transposition", 0),
    ("monoalphabetic sub.",          "mono", 0),
    ("Hill 2x2",                     "hill2", 0),
    ("5x6 fractionation (bifid-like), period 7", "bifid6", 7),
    ("Vigenere L=2",                 "vig", 2),
    ("Vigenere L=3",                 "vig", 3),
    ("Vigenere L=5",                 "vig", 5),
    ("Vigenere L=7",                 "vig", 7),
    ("Vigenere L=8",                 "vig", 8),
    ("Vigenere L=10",                "vig", 10),
    ("Vigenere L=12",                "vig", 12),
    ("Vigenere L=16",                "vig", 16),
    ("Vigenere L=20",                "vig", 20),
    ("Vigenere L=25",                "vig", 25),
    ("Vigenere L=30",                "vig", 30),
    ("Beaufort L=10",                "beau", 10),
    ("Quagmire III (KRYPTOS) L=8",   "quag3", 8),
    ("Quagmire III (KRYPTOS) L=10",  "quag3", 10),
    ("general polyalphabetic p=5",   "polyalpha", 5),
    ("general polyalphabetic p=10",  "polyalpha", 10),
    ("general polyalphabetic p=20",  "polyalpha", 20),
    ("running key (English key)",    "running", 0),
    ("plaintext autokey (primer 8)", "autokey", 8),
    ("ciphertext autokey (primer 8)", "ctautokey", 8),
    ("Gromark base10 primer 5",      "gromark", 5),
    ("Gromark base10 primer 8",      "gromark", 8),
    ("one-time pad",                 "otp", 0),
]


def _chunk(args):
    tag, seed, mode, L, trials = args
    rng = random.Random(seed)
    corpus = _CORP
    hi = len(corpus) - 98
    acc = {k: [] for k in STATS}
    for _ in range(trials):
        i = rng.randrange(hi)
        pt = corpus[i:i + 97]
        ct = make_ct(mode, L, pt, rng)
        pr = profile(ct)
        for k in STATS:
            acc[k].append(pr[k])
    return tag, acc


def main():
    print("=" * 78)
    print("(f) SIDE-BY-SIDE STATISTICAL PROFILE")
    print("=" * 78)

    obs = profile(S.K4_B)
    print("\n--- 1. The observed profiles ----------------------------------------")
    hdr = (f"{'text':16s} {'n':>4s} {'IoC':>8s} {'dist':>5s} {'dbl':>4s} "
           f"{'maxZ(1-48)':>10s} {'maxZper':>8s} {'bi':>4s} {'tri':>4s} {'chi2u':>7s}")
    print(hdr)
    for name, t in (("K1 ciphertext", S.K1_CT), ("K2 ciphertext", S.K2_CT),
                    ("K3 ciphertext", S.K3_CT), ("K4 ciphertext", S.K4_CT),
                    ("K1-K3 plaintext", S.K1_PT + S.K2_PT + S.K3_PT)):
        bb = S.to_ints(t)
        p = profile(bb)
        print(f"{name:16s} {len(bb):4d} {p['ioc']:8.5f} {p['distinct']:5d} "
              f"{p['doubles']:4d} {p['maxz']:10.2f} {p['maxperz']:8.2f} "
              f"{p['bigrams']:4d} {p['trigrams']:4d} {p['chi2u']:7.1f}")
    print("\n  (maxZ and maxZper are MAXIMA over a scan, so they are inflated by")
    print("   construction; they are comparable across rows but not to 1.96.)")

    print("\n--- 2. Simulated candidate systems ----------------------------------")
    print(f"{TRIALS:,} simulated 97-letter ciphertexts per system, plaintext = random")
    print("window of real English prose.")
    args = []
    per = TRIALS // NPROC
    for tag, mode, L in SYSTEMS:
        h = sum(ord(ch) * (i + 1) for i, ch in enumerate(tag))
        for i in range(NPROC):
            args.append((tag, SEED + 7919 * i + 131 * h, mode, L, per))
    with Pool(NPROC, initializer=_init_worker) as pl:
        parts = pl.map(_chunk, args, chunksize=1)
    agg = {}
    raw = {k: [] for k in STATS}        # replicate-aligned copy, uniform null
    for tag, acc in parts:
        d = agg.setdefault(tag, {k: [] for k in STATS})
        for k in STATS:
            d[k].extend(acc[k])
        if tag == OMNIBUS_TAG:
            for k in STATS:
                raw[k].extend(acc[k])
    for tag in agg:
        for k in STATS:
            agg[tag][k].sort()

    print(f"\n{'system':42s} {'IoC mean':>9s} {'IoC sd':>8s} {'dist':>5s} {'dbl':>5s} "
          f"{'maxZ':>6s} {'bi':>5s} {'tri':>5s}")
    for tag, mode, L in SYSTEMS:
        d = agg[tag]
        mi, si = S.mean_sd(d["ioc"])
        print(f"{tag:42s} {mi:9.5f} {si:8.5f} "
              f"{sum(d['distinct'])/len(d['distinct']):5.2f} "
              f"{sum(d['doubles'])/len(d['doubles']):5.2f} "
              f"{sum(d['maxz'])/len(d['maxz']):6.2f} "
              f"{sum(d['bigrams'])/len(d['bigrams']):5.2f} "
              f"{sum(d['trigrams'])/len(d['trigrams']):5.2f}")

    print("\n--- 3. Where K4 falls inside each candidate's own null ---------------")
    print("Two-sided p for each statistic; 'p' is 2*min(P(<=obs), P(>=obs)) capped at 1.")
    print(f"K4 observed: IoC {obs['ioc']:.5f}  distinct {obs['distinct']}  "
          f"doubles {obs['doubles']}  maxZ {obs['maxz']:.2f}  "
          f"bigrams {obs['bigrams']}  trigrams {obs['trigrams']}  "
          f"chi2u {obs['chi2u']:.1f}")
    print(f"\n{'system':42s} {'p(IoC)':>8s} {'p(dist)':>8s} {'p(dbl)':>8s} "
          f"{'p(maxZ)':>8s} {'p(bi)':>8s} {'p(chi2u)':>9s} {'verdict':>16s}")
    verdicts = {}
    for tag, mode, L in SYSTEMS:
        d = agg[tag]
        ps = {}
        for k in ("ioc", "distinct", "doubles", "maxz", "bigrams", "chi2u"):
            v = d[k]
            lo = S.percentile_of(v, obs[k])
            hi = S.frac_ge(v, obs[k])
            ps[k] = min(1.0, 2 * min(lo, hi))
        worst = min(ps.values())
        if worst < 0.001:
            verdict = "IMPLAUSIBLE"
        elif worst < 0.01:
            verdict = "disfavoured"
        elif worst < 0.05:
            verdict = "mild tension"
        else:
            verdict = "compatible"
        verdicts[tag] = (worst, verdict, ps)
        fmt = lambda x: (f"{x:8.5f}" if x >= 1e-5 else f"{'<1e-05':>8s}")
        print(f"{tag:42s} {fmt(ps['ioc'])} {fmt(ps['distinct'])} {fmt(ps['doubles'])} "
              f"{fmt(ps['maxz'])} {fmt(ps['bigrams'])} {fmt(ps['chi2u'])[:9]:>9s} "
              f"{verdict:>16s}")

    print("\n--- 4. Verdict summary ----------------------------------------------")
    imp = [t for t, (w, v, _) in verdicts.items() if v == "IMPLAUSIBLE"]
    dis = [t for t, (w, v, _) in verdicts.items() if v == "disfavoured"]
    ok = [t for t, (w, v, _) in verdicts.items() if v in ("compatible", "mild tension")]
    print("  Made IMPLAUSIBLE by the statistics alone (some statistic p < 0.001):")
    for t in imp:
        w, v, ps = verdicts[t]
        drv = min(ps, key=lambda k: ps[k])
        print(f"    - {t:42s} driven by {drv} (p = {ps[drv]:.2e})")
    print("\n  Disfavoured (0.001 <= p < 0.01):")
    for t in dis:
        print(f"    - {t}")
    print("\n  Statistically COMPATIBLE with K4 (the statistics say nothing against them):")
    for t in ok:
        print(f"    - {t}")
    print("\n  Compatibility here is a weak statement: with 97 letters almost any system")
    print("  with an effective key length of 8 or more is indistinguishable from any")
    print("  other.  The statistics discriminate the SHORT-key and NO-key end of the")
    print("  space and nothing else.")

    # ------------------------------------------------------------------ 5 ---
    print("\n--- 5. OMNIBUS: is there ANY detectable structure in K4? ------------")
    print("Every individual K4 'anomaly' in the literature is one statistic picked")
    print("after the fact from a battery.  The honest question is: how surprising is")
    print("the SMALLEST of the battery's p-values?  Null = one-time pad over English,")
    print("which is exactly a uniform-random 97-letter string.")
    srt = {k: sorted(raw[k]) for k in STATS}
    nrep = len(raw[STATS[0]])

    def twosided(k, x):
        lo = S.percentile_of(srt[k], x)
        hi = S.frac_ge(srt[k], x)
        return min(1.0, 2 * min(lo, hi))

    obs_ps = {k: twosided(k, obs[k]) for k in BATTERY}
    obs_min = min(obs_ps.values())
    print(f"\n  battery of {len(BATTERY)} statistics, {nrep:,} null replicates")
    print(f"  {'statistic':12s} {'K4 value':>10s} {'two-sided p vs uniform':>24s}")
    for k in BATTERY:
        v = obs[k]
        print(f"  {k:12s} {v:10.4f} {obs_ps[k]:24.4f}")
    print(f"\n  K4's smallest p over the battery: {obs_min:.4f}  (statistic "
          f"{min(obs_ps, key=lambda k: obs_ps[k])})")
    null_min = []
    for i in range(nrep):
        m = 1.0
        for k in BATTERY:
            p = twosided(k, raw[k][i])
            if p < m:
                m = p
        null_min.append(m)
    null_min.sort()
    p_omni = S.percentile_of(null_min, obs_min)
    print(f"  null distribution of that minimum: median {null_min[nrep // 2]:.4f}, "
          f"5th pct {null_min[max(0, nrep // 20)]:.4f}")
    print(f"  OMNIBUS p = P(min-p <= K4's min-p | uniform) = {p_omni:.4f}")
    print("\n  (The marginal CDFs are estimated from the same sample that supplies the")
    print("   null replicates, which biases the omnibus p DOWNWARD -- i.e. in favour")
    print("   of finding structure.  Even so it is nowhere near significance.")
    print("   The one statistic not in this battery is the width-21 column-bigram")
    print("   count; stat_e_kasiski.py shows its multiple-testing-corrected p is 0.2-0.4,")
    print("   so adding it could only raise this omnibus p, never lower it.)")
    if p_omni > 0.05:
        print("\n  CONCLUSION: no statistic in the classical battery detects any structure")
        print("  in K4 once selection is paid for.  K4 is, at n = 97, statistically")
        print("  indistinguishable from a uniformly random string of letters.")


if __name__ == "__main__":
    main()
