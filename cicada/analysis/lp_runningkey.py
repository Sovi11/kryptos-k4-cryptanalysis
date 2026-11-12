"""Test: is LP2 = plaintext + (any English-text key), e.g. a running key or a plaintext
autokey with ANY primer length?  If so, ciphertext frequencies = convolution E*E of the
English rune distribution with itself (or E*(-E) for subtractive variants).  That has a
measurable IoC above 1; LP2's is 1.000.  Plaintext frequencies are taken from the
authors' own cleartext rune pages in LP1 (keys 'Substitution with default Gematria')."""
import random
from collections import Counter
from lp_common import RUNES, IDX, LATIN, to_latin, ioc, lp2_unsolved, SRC

lines = open(SRC, encoding="utf-8").read().split("\n")
pt, keep, inr = [], False, False
for l in lines:
    if l.startswith("## "): keep = False; inr = False
    if l.startswith("**Key:**"): keep = "default Gematria" in l
    if l.startswith("Runes:"): inr = True; continue
    if inr and not (l.startswith("    ") or not l.strip()): inr = False
    if keep and inr:
        pt += [IDX[ch] for ch in l if ch in IDX]
print(f"cleartext plaintext runes collected: {len(pt)}")
print("sample:", to_latin(pt[:80]))
E = Counter(pt); n = len(pt)
p = [E[i] / n for i in range(29)]
def ioc_dist(q): return 29 * sum(x * x for x in q)
def conv(a, b, sign=1):
    out = [0.0] * 29
    for i in range(29):
        for j in range(29):
            out[(i + sign * j) % 29] += a[i] * b[j]
    return out
print(f"\nIoC of English (LP cleartext) distribution: {ioc_dist(p):.4f}")
models = {"c = p + k (Vigenere-like)": conv(p, p, 1),
          "c = p - k (Beaufort-like)": conv(p, p, -1)}

s, _ = lp2_unsolved()
N = len(s); obs = ioc(s)
rng = random.Random(3)
def sample_ioc(q, reps=300):
    vals = []
    for _ in range(reps):
        draw = rng.choices(range(29), weights=q, k=N)
        vals.append(ioc(draw))
    m = sum(vals)/reps; sd = (sum((v-m)**2 for v in vals)/reps)**0.5
    return m, sd
mu, sdu = sample_ioc([1/29]*29)
print(f"LP2 observed IoC: {obs:.4f}    uniform-random sample: {mu:.4f} ± {sdu:.4f}")
fo = Counter(s)
for name, q in models.items():
    m, sd = sample_ioc(q)
    chi = sum((fo[i] - N*q[i])**2 / (N*q[i]) for i in range(29))
    print(f"{name:28s} distribution IoC {ioc_dist(q):.4f}; samples of size N: {m:.4f} ± {sd:.4f};"
          f"  LP2 sits {(obs-m)/sd:+.1f} sd away;  chi2 of LP2 vs this model {chi:.0f} on 28 df")

# Sensitivity: plaintext estimated from only ~n runes is noisy; bootstrap the convolution IoC
bs = []
for _ in range(300):
    d = Counter(rng.choices(pt, k=n)); q = [d[i]/n for i in range(29)]
    bs.append(ioc_dist(conv(q, q, 1)))
bs.sort()
print(f"\nbootstrap 2.5-97.5% of E*E IoC (plaintext-sample uncertainty): {bs[7]:.4f} - {bs[292]:.4f}")
