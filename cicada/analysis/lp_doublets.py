"""(1) Is the conditional-IoC excess fully explained by the missing doublets?
   (2) Anatomy of the 86 surviving doublets."""
import random
from collections import Counter
from lp_common import *

s, brk = lp2_unsolved()
N = len(s)

# (1) group by previous rune, drop the diagonal symbol, IoC over remaining 28 symbols
def off_diag_ioc(t):
    tot = 0; acc = 0.0
    for v in range(29):
        g = [t[i] for i in range(1, len(t)) if t[i-1] == v and t[i] != v]
        if len(g) > 1:
            acc += len(g) * ioc(g, n=28); tot += len(g)
    return acc / tot
obs = off_diag_ioc(s)
rng = random.Random(7); vals = []
for _ in range(60):
    t = s[:]; rng.shuffle(t); vals.append(off_diag_ioc(t))
m = sum(vals)/len(vals); sd = (sum((v-m)**2 for v in vals)/len(vals))**0.5
print(f"(1) conditional IoC with the doublet symbol removed: {obs:.4f}   shuffled null {m:.4f} ± {sd:.4f}   z={(obs-m)/sd:+.2f}")

# (2) the 86 doublets
dpos = [i for i in range(1, N) if s[i] == s[i-1]]
c = Counter(s[i] for i in dpos)
print(f"\n(2) {len(dpos)} doublets by rune (uniform would be ~3 each):")
print("   " + "  ".join(f"{LATIN[r]}:{n}" for r, n in c.most_common()))
print(f"   across a word break: {sum(brk[i] for i in dpos)}   within a word: {sum(not brk[i] for i in dpos)}")
# chi-square vs proportional to rune frequency
fr = Counter(s); tot = sum(fr.values())
chi = sum((c[r] - len(dpos)*fr[r]/tot)**2 / (len(dpos)*fr[r]/tot) for r in range(29))
print(f"   chi2 of doublet runes vs rune frequency: {chi:.1f} on 28 df (5% crit 41.3)")

# per-page position: cumulative counts by section
print("\n   doublets per section:")
pos = 0
from lp_common import sections, tokens
for head, blocks in sections():
    if head.startswith("73.jpg") or head.startswith("74.jpg"): continue
    n = sum(1 for b in blocks for k, v in tokens(b) if k == "r")
    if n == 0: continue
    dd = sum(1 for i in dpos if pos <= i < pos + n)
    print(f"     {head[:45]:45s} runes={n:5d}  doublets={dd:3d}  rate={dd/max(n,1)*100:.2f}%")
    pos += n

# triples and near-doublets: is c_i == c_{i-2} suppressed too?
print("\n(3) gap-2 repeats c_i == c_{i-2}:", sum(1 for i in range(2, N) if s[i] == s[i-2]), f"(uniform expects {(N-2)/29:.0f})")
print("    gap-3 repeats c_i == c_{i-3}:", sum(1 for i in range(3, N) if s[i] == s[i-3]), f"(uniform expects {(N-3)/29:.0f})")
