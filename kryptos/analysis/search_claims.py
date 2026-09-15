"""search_claims.py -- (d) and (e): mechanical falsification tests for every public K4
plaintext claim that states a full text.

For each claim:
  1. exact letter count against 97
  2. do EAST / NORTHEAST / BERLIN / CLOCK land at 1-indexed 22-25, 26-34, 64-69, 70-74
  3. calibrated language-model score, with a z against held-out English and against the
     only known Sanborn plaintexts (K1-K3)
  4. the key stream the claim implies under each of the 24 cipher/alphabet combos, run
     through the VALIDATED structure battery of search_ksbattery.py
  5. the same battery on the claim's implied shift stream read as numbers

Nothing here can CONFIRM a plaintext.  What it can do is (i) refute a claim outright on
length or crib position, (ii) show that a claim's non-crib text is not English, and
(iii) report whether a claim's implied key stream carries any detectable structure --
with a measured detection power so that "no structure" means something.

Usage: python3.13 search_claims.py [all|solvekryptos|<name>]
"""
import json, os, re, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import search_lm
import search_ksbattery as KB
import search_calib as CAL
import runningkey_lib as RK

A2Z = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CT = RK.K4_CT
CRIB = RK.CRIBS
CRIB_POS = sorted(CRIB)

ENG_MEAN, ENG_SD = -0.741, 0.077
SANBORN_MEAN, SANBORN_SD = -0.967, 0.087

CLAIMS = CAL.CLAIMS
SOURCES = {
 "solvekryptos.com": "https://solvekryptos.com/solution (site itself calls the mechanism back-solved)",
 "mattklepp/k4": "github.com/mattklepp/k4 README, Wayback 2026-05-28 (repo now 404)",
 "Naughton/Grok-3": "medium.com/@michaelpnaughton, Feb 2025 (author later walked it back)",
 "figshare Genie": "figshare 'Genie Replication Package', 2025-26",
 "ChatGPT (Toponce #2)": "gist.github.com/atoponce -- 'No, ChatGPT didn't solve Kryptos 4'",
 "ChatGPT (Toponce #1)": "same gist",
 "ChatGPT (Toponce #3)": "same gist",
 "'Structured Solution' video (May 2026)": "youtube.com/watch?v=HizjD_r-2hs -- NO TEXT PUBLISHED, not evaluable",
}

def L(s):
    return re.sub("[^A-Z]", "", s.upper())

def crib_report(pt):
    out = []
    for pos, word in [(22, "EAST"), (26, "NORTHEAST"), (64, "BERLIN"), (70, "CLOCK")]:
        got = pt[pos - 1: pos - 1 + len(word)] if len(pt) >= pos - 1 + len(word) else "(short)"
        out.append((word, pos, got, got == word))
    return out

def words_ge(s, minlen=5):
    v = set()
    with open("/usr/share/dict/words") as f:
        for w in f:
            w = w.strip().upper()
            if len(w) >= minlen and w.isalpha() and w.isascii():
                v.add(w)
    found = []
    for i in range(len(s)):
        for Lg in range(minlen, min(12, len(s) - i) + 1):
            if s[i:i + Lg] in v:
                found.append((i + 1, s[i:i + Lg]))
    return found

def analyse_claim(name, raw, null, full=False):
    s = L(raw)
    print("=" * 104)
    print(f"CLAIM: {name}")
    print(f"source: {SOURCES.get(name, '?')}")
    print("=" * 104)
    print(f"raw      : {raw}")
    print(f"letters  : {s}")
    print(f"LENGTH   : {len(s)}   (K4 = 97)  ->  {'MATCH' if len(s) == 97 else 'MISMATCH -- REFUTED'}")
    nc = 0
    for word, pos, got, ok in crib_report(s):
        nc += len(word) if ok else 0
        print(f"  crib {word:9s} at 1-idx {pos:2d}-{pos+len(word)-1:2d}: claim has {got!r:13s} "
              f"{'OK' if ok else 'MISMATCH'}")
    npos = sum(1 for i in CRIB_POS if i < len(s) and s[i] == CRIB[i])
    print(f"  crib letters in place: {npos}/24  ->  {'PASS' if npos == 24 else 'FAIL'}")
    if len(s) < 8:
        return None
    q = search_lm.quad(s)
    p5 = search_lm.pent(s)
    zE = (q - ENG_MEAN) / ENG_SD
    zS = (q - SANBORN_MEAN) / SANBORN_SD
    print(f"  quadgram : {q:+.4f}   z vs held-out English {zE:+.2f}   "
          f"z vs Sanborn K1-K3 plaintext {zS:+.2f}")
    print(f"  5-gram   : {p5:+.4f}")
    if abs(zS) <= 2:
        print("  -> English-likeness is INSIDE the band of real Sanborn plaintext. "
              "Not refutable on this statistic.")
    elif zS < -2:
        print("  -> English-likeness is BELOW the Sanborn band: the non-crib text does not "
              "read as English.")
    else:
        print("  -> English-likeness is ABOVE the Sanborn band (suspiciously fluent / optimised).")
    noncrib = "".join(c for i, c in enumerate(s) if i not in CRIB)
    if len(noncrib) > 8:
        qn = search_lm.quad(noncrib)
        print(f"  quadgram of the NON-CRIB letters alone ({len(noncrib)}): {qn:+.4f}  "
              f"(z vs Sanborn {(qn-SANBORN_MEAN)/SANBORN_SD:+.2f})")
    w = [x for x in words_ge(s) if x[1] not in ("EAST", "NORTHEAST", "BERLIN", "CLOCK")]
    print(f"  dictionary words >=5 outside the cribs: {w}")
    if len(s) != 97:
        print("  -> length != 97, so no key stream can be derived.  REFUTED; no further tests.")
        print()
        return None
    print()
    rows = KB.score_plaintext(s, f"key streams implied by {name}", null=null, verbose=True)
    print()
    return rows

def main():
    null = KB.build_null()
    print("NULL for the key-stream battery (uniform-random 97-letter streams, n=%d):" % null["_n"])
    for k in ("ioc", "per_excess", "rep4", "quad", "run", "ap", "d1", "ndistinct", "ac_z"):
        print(f"   {k:11s} mean {null[k]['mean']:9.4f}  sd {null[k]['sd']:8.4f}  "
              f"p99 {null[k]['p99']:9.4f}")
    print(f"   sculpture-corpus substring hit rate {null['_lcs_scu_rate']*100:.1f}%   "
          f"lateral-corpus hit rate {null['_lcs_lat_rate']*100:.1f}%")
    print()
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    order = ["solvekryptos.com", "mattklepp/k4", "ChatGPT (Toponce #2)", "Naughton/Grok-3",
             "figshare Genie", "ChatGPT (Toponce #1)", "ChatGPT (Toponce #3)"]
    for name in order:
        if which not in ("all", name):
            continue
        analyse_claim(name, CLAIMS[name], null)
    if which == "all":
        print("=" * 104)
        print("CLAIM: 'The Kryptos K4 Structured Solution' (YouTube, Creation Unified, May 2026)")
        print("=" * 104)
        print("No plaintext and no procedure is published anywhere reachable (creationunified.com")
        print("has no K4 page; /kryptos, /kryptos-k4, /k4 and the sitemap were all probed in")
        print("findings/prior_art.md and 404).  NOT EVALUABLE -- there is nothing to test.")
        print()

if __name__ == "__main__":
    main()
