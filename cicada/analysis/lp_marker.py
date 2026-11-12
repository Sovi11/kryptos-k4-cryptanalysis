"""Hypothesis: c_i = c_{i-1} + m_i*(p_i - z), m_i != 0.  Then ciphertext doublets occur
exactly where plaintext rune = z.  Predictions: (a) freq(z) in plaintext ~= LP2 doublet
rate 0.664% (86/12955); (b) the word-position profile of doublets matches z's profile."""
import math
from collections import Counter
from lp_common import LATIN, IDX, SRC, lp2_unsolved, sections, tokens

# --- plaintext reference: LP's own cleartext rune pages, with word structure ---
lines = open(SRC, encoding="utf-8").read().split("\n")
words, keep, inr = [], False, False
for l in lines:
    if l.startswith("## "): keep = inr = False
    if l.startswith("**Key:**"): keep = "default Gematria" in l
    if l.startswith("Runes:"): inr = True; continue
    if inr and not (l.startswith("    ") or not l.strip()): inr = False
    if keep and inr:
        cur = []
        for ch in l.strip():
            if ch in IDX: cur.append(IDX[ch])
            else:
                if cur: words.append(cur); cur = []
        if cur: words.append(cur)
pt = [r for w in words for r in w]
f = Counter(pt); n = len(pt)

def profile(word_list, target):
    """counts of target occurrences that are: single-rune word, word-initial, word-final, medial"""
    c = Counter()
    for w in word_list:
        for j, r in enumerate(w):
            if r != target: continue
            if len(w) == 1: c["single"] += 1
            elif j == 0: c["initial"] += 1
            elif j == len(w) - 1: c["final"] += 1
            else: c["medial"] += 1
    return c

# --- LP2 doublets with word positions ---
lp2_words = []
for head, blocks in sections():
    if head.startswith(("73.jpg", "74.jpg")): continue
    for b in blocks:
        cur = []
        for k, v in tokens(b):
            if k == "r": cur.append(v)
            elif cur: lp2_words.append(cur); cur = []
        if cur: lp2_words.append(cur)
stream = [r for w in lp2_words for r in w]
pos_info = []  # (word_len, index_in_word) for each rune
for w in lp2_words:
    for j in range(len(w)): pos_info.append((len(w), j))
dbl = Counter()
for i in range(1, len(stream)):
    if stream[i] == stream[i-1]:
        L, j = pos_info[i]   # the SECOND rune of the doublet is where p_i = z
        dbl["single" if L == 1 else "initial" if j == 0 else "final" if j == L-1 else "medial"] += 1
D = sum(dbl.values())
print(f"LP2 doublets: {D}   rate {D/(len(stream)-1)*100:.3f}%   word-position of 2nd rune: {dict(dbl)}")

cats = ["single", "initial", "medial", "final"]
print(f"\n{'rune':5s} {'freq%':>6s}  {'single':>6s} {'init':>5s} {'med':>5s} {'final':>5s}   rate-fit  position-chi2")
rows = []
for r in range(29):
    pr = profile(words, r); tot = sum(pr.values())
    freq = f[r] / n * 100
    if tot < 3:
        rows.append((r, freq, pr, float("inf"))); continue
    # chi2 of LP2 doublet positions vs this rune's positional distribution (add-0.5 smoothing)
    chi = 0.0
    for c in cats:
        e = D * (pr[c] + 0.5) / (tot + 2)
        chi += (dbl[c] - e) ** 2 / e
    rows.append((r, freq, pr, chi))
rows.sort(key=lambda x: abs(x[1] - 0.664))
for r, freq, pr, chi in rows:
    tot = max(1, sum(pr.values()))
    rate_ok = "OK" if 0.45 <= freq <= 0.95 else ""
    print(f"{LATIN[r]:5s} {freq:6.2f}  " + " ".join(f"{pr[c]/tot*100:5.0f}%" for c in cats) + f"   {rate_ok:8s} {chi:8.1f}")
print(f"\n(base rate of the 4 word-position classes among all LP2 rune positions:)")
base = Counter("single" if L == 1 else "initial" if j == 0 else "final" if j == L-1 else "medial" for L, j in pos_info[1:])
print("  " + "  ".join(f"{c}:{base[c]/sum(base.values())*100:.0f}%" for c in cats), "   doublets:", "  ".join(f"{c}:{dbl[c]/D*100:.0f}%" for c in cats))
print("chi2 critical (3 df): 7.8 at 5%")
