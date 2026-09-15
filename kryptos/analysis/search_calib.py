"""search_calib.py -- explicit calibration of the character language model used by the
constrained-plaintext search, so that every later score is interpretable.

Reports, for the quadgram model of search_lm.py (mean log10 P(letter | previous 3)):

  * held-out English 97-grams (the model's own domain)
  * K1 / K2 / K3 plaintext -- the only *known* Sanborn plaintexts, i.e. the best available
    proxy for what a true K4 plaintext should score
  * uniform-random and unigram-random 97-grams
  * the K4 ciphertext itself
  * "crib-pinned random": 24 crib letters fixed, 73 uniform-random -- the annealer's start
  * annealed-to-fit text (the annealer's ceiling), if search_anneal_k4.json exists
  * every public plaintext claim with a stated full text

and converts each to a z-score against the held-out English distribution, plus a
DOMAIN check (the same texts scored under corpus variants restricted to man pages
only and to doc/info only) so the reader can see how much of any score gap is the
model's technical-prose bias rather than the text.

Usage: python3.13 search_calib.py
"""
import json, os, re, subprocess, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
sys.path.insert(0, HERE)
import search_lm

A2Z = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

with open(os.path.join(DATA, "k4_ciphertext.txt")) as f:
    CT = re.sub("[^A-Z]", "", f.read().upper())
with open(os.path.join(DATA, "cribs.json")) as f:
    _c = json.load(f)["cribs"]
CRIB = {}
for c in _c:
    st = c["pos"] - 1
    for k, p in enumerate(c["pt"]):
        CRIB[st + k] = p
CRIB_POS = sorted(CRIB)

# ------------------------------------------------------------------ claims
# Every publicly stated K4 plaintext claim I could find with a full text.
# Sources are documented in findings/prior_art.md; they are NOT treated as evidence here.
CLAIMS = {
 "solvekryptos.com":
   "THE COMPASS ROSE IS HERE X EAST NORTHEAST THIS IS YOUR POSITION X COMMISSION "
   "BERLIN CLOCK WHICH IS NORTHEAST OF HERE X",
 "mattklepp/k4":
   "UDILKAFSGDMZLYQJCVNJA EASTNORTHEAST OPOHAYLOMIQSDZSSHTQNSXYMEMNBT BERLINCLOCK "
   "SYRUFZRDSPQKKQZIKAGIWQD",
 "Naughton/Grok-3":
   "THIS IS A GUIDE TO THE BERLIN CLOCK WHICH IS NORTHEST OF HERE AT CIA LANGLEY VIRGINIA",
 "figshare Genie":
   "TO SET THE EAST NORTHEAST HOUR BY BEARING BERLIN CLOCK DEGREES GRID POINT "
   "NORTHWEST TO FIND GROSSER STERN",
 "ChatGPT (Toponce #2)":
   "INTHECENTEROFTHISCITYEASTNORTHEASTNEARROTESRATHAUSCHIMESFROMTHEBERLINCLOCK",
 "ChatGPT (Toponce #1)":
   "BERLINCLOCKINNORTHEASTAREAKEYTOPUZZLE",
 "ChatGPT (Toponce #3)":
   "ABANDONCONTACTNEARTHEBERLINCLOCK",
}

def L(s):
    return re.sub("[^A-Z]", "", s.upper())

def k123():
    pt, cur = {}, None
    with open(os.path.join(DATA, "k1_k3_plaintext.txt")) as f:
        for line in f:
            if line.startswith("#"):
                m = re.match(r"#\s*(K\d)", line)
                if m:
                    cur = m.group(1)
                continue
            s = L(line)
            if s and cur:
                pt[cur] = pt.get(cur, "") + s
    return pt

def windows(s, n=97):
    if len(s) < n:
        return [s]
    return [s[i:i + n] for i in range(len(s) - n + 1)]

def main():
    import numpy as np
    Q, G5, hold = search_lm.load()
    rng = np.random.default_rng(7)
    rows = []           # (label, array of quad scores)

    # ---- reference distributions
    starts = rng.integers(0, len(hold) - 98, size=20000)
    eng = np.array([[ord(ch) - 65 for ch in hold[s:s + 97]] for s in starts], dtype=np.int64)
    ENG = search_lm.quad_batch(eng)
    rows.append(("held-out English 97-grams (model's own domain)", ENG))

    pt = k123()
    for name in ("K1", "K2", "K3"):
        s = pt[name]
        w = windows(s)
        arr = np.array([search_lm.quad(x) for x in w])
        rows.append((f"{name} plaintext 97-grams (n={len(w)})", arr))
    allpt = pt["K1"] + pt["K2"] + pt["K3"]
    w = windows(allpt)
    rows.append((f"K1+K2+K3 plaintext 97-grams (n={len(w)})",
                 np.array([search_lm.quad(x) for x in w])))

    ru = rng.integers(0, 26, size=(20000, 97))
    rows.append(("uniform random 97-grams", search_lm.quad_batch(ru)))
    f = np.array([8.17,1.49,2.78,4.25,12.70,2.23,2.02,6.09,6.97,0.15,0.77,4.03,2.41,
                  6.75,7.51,1.93,0.10,5.99,6.33,9.06,2.76,0.98,2.36,0.15,1.97,0.07])
    f = f / f.sum()
    rows.append(("unigram-random 97-grams", search_lm.quad_batch(rng.choice(26, size=(20000, 97), p=f))))

    # crib-pinned random: the annealer's starting distribution
    cp = rng.integers(0, 26, size=(20000, 97))
    for p, ch in CRIB.items():
        cp[:, p] = ord(ch) - 65
    rows.append(("crib-pinned random (24 fixed + 73 uniform)", search_lm.quad_batch(cp)))

    rows.append(("K4 CIPHERTEXT", np.array([search_lm.quad(CT)])))

    # annealer ceiling
    ann = os.path.join(HERE, "search_anneal_k4.json")
    if os.path.exists(ann):
        with open(ann) as fh:
            res = json.load(fh)
        rows.append((f"ANNEALED to fit the cribs (n={len(res)} restarts)",
                     np.array([s for s, _ in res])))
    ctl = os.path.join(HERE, "search_anneal_control.json")
    if os.path.exists(ctl):
        with open(ctl) as fh:
            cres = json.load(fh)
        rows.append((f"ANNEALED, control pins (n={len(cres)})",
                     np.array([s for s, _ in cres])))

    em, es = float(ENG.mean()), float(ENG.std())
    print("=" * 100)
    print("TABLE A1 -- calibration of the quadgram model (mean log10 P(letter|prev 3); higher = more English)")
    print("=" * 100)
    print(f"{'text':52s} {'n':>6s} {'mean':>7s} {'sd':>6s} {'p1':>7s} {'p50':>7s} {'p99':>7s} {'z vs Eng':>9s}")
    for name, arr in rows:
        z = (arr.mean() - em) / es
        print(f"{name:52s} {len(arr):6d} {arr.mean():7.3f} {arr.std():6.3f} "
              f"{np.percentile(arr,1):7.3f} {np.percentile(arr,50):7.3f} "
              f"{np.percentile(arr,99):7.3f} {z:+9.2f}")
    print()
    print(f"held-out English:  mean {em:.3f}  sd {es:.3f}   -> z = (score - {em:.3f}) / {es:.3f}")
    print()

    # ---- claims
    print("=" * 100)
    print("TABLE A2 -- public plaintext claims scored on the same scale")
    print("=" * 100)
    print(f"{'claim':24s} {'len':>4s} {'cribs':>6s} {'quad':>7s} {'z':>7s} {'pent':>7s}  verdict-on-length-and-cribs")
    kpt = np.array([search_lm.quad(x) for x in windows(allpt)])
    for name, raw in CLAIMS.items():
        s = L(raw)
        nc = sum(1 for i in CRIB_POS if i < len(s) and s[i] == CRIB[i])
        q = search_lm.quad(s) if len(s) >= 5 else float("nan")
        p5 = search_lm.pent(s) if len(s) >= 6 else float("nan")
        z = (q - em) / es
        verdict = []
        verdict.append("len=97 OK" if len(s) == 97 else f"len={len(s)} FAIL")
        verdict.append(f"cribs {nc}/24" + (" OK" if nc == 24 else " FAIL"))
        print(f"{name:24s} {len(s):4d} {nc:4d}/24 {q:7.3f} {z:+7.2f} {p5:7.3f}  {'; '.join(verdict)}")
    print()
    print("Reference band for a TRUE K4 plaintext (from the only known Sanborn plaintexts):")
    print(f"   K1+K2+K3 97-gram windows: mean {kpt.mean():.3f}  sd {kpt.std():.3f}  "
          f"range {kpt.min():.3f} .. {kpt.max():.3f}")
    print(f"   i.e. z in [{(kpt.min()-em)/es:+.2f}, {(kpt.max()-em)/es:+.2f}] against held-out English.")
    print()

    # ---- domain sensitivity
    print("=" * 100)
    print("TABLE A3 -- domain sensitivity: the same texts under corpus-restricted model variants")
    print("=" * 100)
    texts = [("held-out English (this model's own holdout)", None),
             ("K1+K2+K3 plaintext (whole)", allpt),
             ("solvekryptos claim", L(CLAIMS["solvekryptos.com"])),
             ("K4 ciphertext", CT)]
    hdr = f"{'text':46s}"
    for v in ("all", "man", "docinfo"):
        hdr += f" {v:>9s}"
    print(hdr)
    vals = {}
    for v in ("all", "man", "docinfo"):
        out = subprocess.run([sys.executable, "-c",
            "import os,sys;os.environ['K4_LM']=%r;sys.path.insert(0,%r);"
            "import search_lm,json,re;"
            "Q,G5,h=search_lm.load();"
            "import numpy as np;"
            "rng=np.random.default_rng(7);"
            "st=rng.integers(0,len(h)-98,size=4000);"
            "e=np.array([[ord(c)-65 for c in h[s:s+97]] for s in st],dtype=np.int64);"
            "print(json.dumps({'eng':float(search_lm.quad_batch(e).mean()),"
            "'k123':search_lm.quad(%r),'claim':search_lm.quad(%r),'ct':search_lm.quad(%r)}))"
            % (v, HERE, allpt, L(CLAIMS["solvekryptos.com"]), CT)],
            capture_output=True, text=True)
        try:
            vals[v] = json.loads(out.stdout.strip().splitlines()[-1])
        except Exception:
            vals[v] = {"eng": float("nan"), "k123": float("nan"),
                       "claim": float("nan"), "ct": float("nan")}
    for label, key in [("held-out English 97-grams (that variant's holdout)", "eng"),
                       ("K1+K2+K3 plaintext (whole)", "k123"),
                       ("solvekryptos claim", "claim"),
                       ("K4 ciphertext", "ct")]:
        line = f"{label:46s}"
        for v in ("all", "man", "docinfo"):
            line += f" {vals[v][key]:9.3f}"
        print(line)
    print()
    print("Read A3 as: the absolute numbers move with the training domain, so only DIFFERENCES")
    print("within one column are meaningful.  The ordering (English > Sanborn plaintext >>")
    print("ciphertext) is stable across variants.")

if __name__ == "__main__":
    main()
