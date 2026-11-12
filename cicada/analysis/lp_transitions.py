"""(1) Full 29x29 transition scan: is ANY non-identical rune pair suppressed like doublets?
   In particular pairs whose Latin forms repeat a letter at the junction (T|TH, E|EA, TH|H...).
(2) Ciphertext autokey, ANY primer length L: group c_i by c_{i-L}; English would give ~1.7."""
import numpy as np
from math import erf, sqrt
from lp_common import lp2_unsolved, LATIN

s, brk = lp2_unsolved(); s = np.array(s); N = len(s)
M = np.zeros((29, 29)); np.add.at(M, (s[:-1], s[1:]), 1)
row, col = M.sum(1), M.sum(0)
E = np.outer(row, col) / M.sum()
Z = (M - E) / np.sqrt(E)
off = ~np.eye(29, dtype=bool)
print(f"(1) diagonal (doublets): observed {int(np.trace(M))}, expected {np.trace(E):.0f}")
zs = Z[off]
print(f"    off-diagonal cells: {zs.size}; min z {zs.min():.2f}, max z {zs.max():.2f}; cells with z<-3: {(zs<-3).sum()}  (Bonferroni 5% needs |z|>3.67)")
for i, j in zip(*np.where((Z < -2.8) & off)):
    print(f"      {LATIN[i]:>2s}->{LATIN[j]:<2s} obs {int(M[i,j]):3d} exp {E[i,j]:5.1f} z {Z[i,j]:+.2f}")
junction = [(i, j) for i in range(29) for j in range(29) if i != j and LATIN[i][-1] == LATIN[j][0]]
o = sum(M[i, j] for i, j in junction); e = sum(E[i, j] for i, j in junction)
print(f"    Latin-junction repeat pairs (e.g. T->TH, EA->A), {len(junction)} cells: observed {int(o)}, expected {e:.0f}, ratio {o/e:.2f}")

print("\n(2) ciphertext autokey primer L: IoC of c_i grouped by c_{i-L}")
def grouped(L):
    a, b = s[:-L], s[L:]
    cnt = np.zeros((29, 29)); np.add.at(cnt, (a, b), 1)
    n = cnt.sum(1)
    return 29 * ((cnt * (cnt - 1)).sum(1)).sum() / (n * (n - 1)).sum()
vals = np.array([grouped(L) for L in range(1, 6001)])
print(f"    L=1..6000: max {vals.max():.4f} at L={vals.argmax()+1}; mean {vals.mean():.4f}; sd {vals.std():.4f}")
print(f"    top 5: " + ", ".join(f"L={i+1}:{vals[i]:.4f}" for i in np.argsort(vals)[-5:][::-1]))
print("    (L=1 includes the doublet effect; English monoalphabetic groups would give ~1.7)")
