"""(b) Homophonic / polyphonic substitution, and a proper null for the low IoC.

Three questions:
  B1. How unusual is IoC = 0.0361 really?  (Proper null: uniform random 97-letter
      strings, plus 97-letter windows of the *known* Kryptos ciphertexts.)
  B2. Is a homophonic substitution (one plaintext letter -> several ciphertext
      symbols, DISJOINT classes so decryption is unique) consistent with the cribs?
  B3. Is a polyphonic substitution (one ciphertext symbol -> several plaintext
      letters) consistent with the cribs?
  B4. What is the MINIMUM number of substitution alphabets the cribs force?
      (chromatic number of the crib conflict graph) -- and which periods survive
      the alphabet-free periodicity test that follows from it.
"""
import math
import os
import sys
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matrix_common import CT, CRIBS, N, A2Z, DATA, ioc

out = []
def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.append(s)

rng = np.random.default_rng(20260912)

def _bt(adj, order, k, colour, idx=0):
    if idx == len(order):
        return True
    v = order[idx]
    used = {colour[u] for u in adj[v] if u in colour}
    for c in range(k):
        if c in used:
            continue
        colour[v] = c
        if _bt(adj, order, k, colour, idx + 1):
            return True
        del colour[v]
    return False


P("=" * 78)
P("(b) HOMOPHONIC / POLYPHONIC SUBSTITUTION AND THE 'BELOW RANDOM' IoC")
P("=" * 78)

# ------------------------------------------------------------------ B1. IoC null
P("\nB1. Is IoC = 0.0361 evidence of deliberate frequency flattening?")
obs = ioc(CT)
cnt = Counter(CT)
P("    observed IoC (delta form, sum n(n-1)/N(N-1)) = %.6f" % obs)
P("    uniform-random expectation                   = 1/26 = %.6f" % (1 / 26))
P("    English                                      ~ 0.0667")
P("    counts:", " ".join("%s%d" % (c, cnt[c]) for c in A2Z))

# exact mean/variance of the delta-IoC for iid uniform letters
# IoC = (sum_i n_i^2 - N) / (N(N-1)); n ~ Multinomial(N, 1/26)
K = 26.0
ENn2 = N * (N - 1) / K + N                     # E[sum n_i^2]
mean_exact = (ENn2 - N) / (N * (N - 1))
P("    exact E[IoC] under uniform = %.6f (= 1/26)" % mean_exact)

TRIALS = 2_000_000
samp = rng.integers(0, 26, size=(TRIALS, N), dtype=np.int8)
# fast per-row counts
cnts = np.zeros((TRIALS, 26), dtype=np.int16)
for v in range(26):
    cnts[:, v] = (samp == v).sum(axis=1)
sumsq = (cnts.astype(np.int64) ** 2).sum(axis=1)
iocs = (sumsq - N) / float(N * (N - 1))
frac_le = float((iocs <= obs + 1e-12).mean())
P("    null simulation: %d uniform random 97-letter strings" % TRIALS)
P("      mean %.6f  sd %.6f" % (iocs.mean(), iocs.std()))
P("      z of observed = %.3f" % ((obs - iocs.mean()) / iocs.std()))
P("      *** P(IoC <= 0.03608) = %.4f  (%.1f%% of random strings are at least"
  % (frac_le, 100 * frac_le))
P("          this flat) ***")
P("      P(IoC <= 0.0361 AND all 26 letters present) = %.4f"
  % float(((iocs <= obs + 1e-12) & (cnts > 0).all(axis=1)).mean()))
P("    VERDICT: 'below uniform random' is NOT a signature of anything.  A flat")
P("    ciphertext is exactly what a long-key polyalphabetic already produces, and")
P("    one string in %.0f of *pure random noise* is this flat or flatter." % (1 / frac_le))

# reference: 97-letter windows of the real Kryptos ciphertexts
lines = [l.strip() for l in open(os.path.join(DATA, "sculpture_panels.txt"))
         if l.strip() and not l.startswith("#") and not l.startswith("[")]
left = "".join(ch for ch in "".join(lines[:28]) if ch.isalpha())
K1K3 = left[:len(left) - 97]
P("\n    Reference: IoC of 97-letter windows of the carved K1-K3 ciphertext")
ws = [ioc(K1K3[i:i + 97]) for i in range(len(K1K3) - 96)]
ws = np.array(ws)
P("      %d windows: min %.4f  1st-quartile %.4f  median %.4f  max %.4f"
  % (len(ws), ws.min(), np.percentile(ws, 25), np.median(ws), ws.max()))
P("      fraction of K1-K3 windows with IoC <= K4's = %.3f" % float((ws <= obs).mean()))
P("      Read this correctly.  K4 IS flatter than every 97-letter window of the")
P("      carved K1-K3 ciphertext (min 0.0363 vs K4's 0.03608) -- but that is")
P("      because K1/K2 are Vigenere with 10- and 8-letter keys over English, which")
P("      leaves a lot of residual structure, and K3 is a bare transposition of")
P("      English.  The correct null for 'was this flattened on purpose?' is")
P("      uniform random, and against that null K4 is at the 22nd percentile.")
P("      So the IoC says the K4 keystream is LONG or APERIODIC (unlike K1/K2), not")
P("      that frequencies were deliberately flattened by a homophonic device.")

# ------------------------------------------------------------------ B2/B3
P("\nB2. Homophonic substitution (plaintext letter -> several ciphertext symbols)")
P("    Definition used: a partition of the ciphertext alphabet into disjoint")
P("    classes, one class per plaintext letter.  Disjointness is what makes a")
P("    homophonic cipher decipherable at all.")
fwd = defaultdict(set)
rev = defaultdict(set)
for pos, c, p in CRIBS:
    fwd[c].add(p)
    rev[p].add(c)
polyphonic = {c: v for c, v in fwd.items() if len(v) > 1}
homophonic = {p: v for p, v in rev.items() if len(v) > 1}
P("    Ciphertext letters that stand for >1 plaintext letter (kills disjointness):")
for c in sorted(polyphonic):
    pos = [(q + 1, pp) for q, cc, pp in CRIBS if cc == c]
    P("      %s -> %s   at %s" % (c, "/".join(sorted(polyphonic[c])), pos))
P("    count = %d of the %d distinct ciphertext letters seen in the cribs"
  % (len(polyphonic), len(fwd)))
P("    RESULT: homophonic substitution with a fixed, position-independent table is")
P("    IMPOSSIBLE.  Any class containing F would have to be a subclass of both E's")
P("    and O's class.  This holds for ANY number of homophones and ANY assignment,")
P("    and it also kills 'cycling homophones' (n-th occurrence uses the n-th")
P("    equivalent), because that scheme still has disjoint classes.")
P("\n    Counting argument, independently: homophony needs MORE ciphertext symbols")
P("    than plaintext letters.  K4's ciphertext alphabet has exactly 26 symbols and")
P("    all 26 occur.  Giving any letter a second equivalent leaves at most 25")
P("    classes, i.e. at least one plaintext letter becomes unwritable.  A 26-symbol")
P("    homophonic cipher over a 26-letter plaintext alphabet does not exist unless")
P("    the mapping is position-dependent -- and a position-dependent substitution")
P("    is a polyalphabetic cipher, which is the space already exhausted in")
P("    findings/families.md.")

P("\nB3. Polyphonic substitution (one ciphertext symbol -> several plaintext letters,")
P("    disambiguated by context; the plaintext->ciphertext map is a FUNCTION)")
P("    Plaintext letters written with >1 ciphertext symbol (kills functionality):")
for p in sorted(homophonic):
    pos = [(q + 1, cc) for q, cc, pp in CRIBS if pp == p]
    P("      %s <- %s   at %s" % (p, "/".join(sorted(homophonic[p])), pos))
P("    count = %d of the %d distinct plaintext letters in the cribs" % (len(homophonic), len(rev)))
P("    RESULT: pure polyphonic substitution is IMPOSSIBLE too -- plaintext E is")
P("    written F (22), G (31) and Y (65); T is written R, S and V.")
P("    So the cribs are simultaneously non-injective in both directions: this is")
P("    the fingerprint of a polyalphabetic/keystream cipher, not of a flattening")
P("    substitution of any kind.")

# how surprising are those conflicts?  chance baseline
P("\n    Chance baseline for the two rule-outs (how easily would random cribs do it?)")
ENGL = "".join(ch * f for ch, f in zip(A2Z, [82,15,28,43,127,22,20,61,70,2,8,40,24,
                                             67,75,19,1,60,63,91,28,10,24,2,20,1]))
cpos = [c for _, c, _ in CRIBS]
T = 200000
nf = nb = 0
for _ in range(T):
    pts = [ENGL[rng.integers(len(ENGL))] for _ in range(24)]
    f = defaultdict(set); r = defaultdict(set)
    for c, p in zip(cpos, pts):
        f[c].add(p); r[p].add(c)
    if any(len(v) > 1 for v in f.values()): nf += 1
    if any(len(v) > 1 for v in r.values()): nb += 1
P("      random English plaintext on the SAME 24 ciphertext letters:")
P("        P(some forward conflict)  = %.4f" % (nf / T))
P("        P(some backward conflict) = %.4f" % (nb / T))
P("      i.e. the conflicts are what you expect; the rule-out is real but it is")
P("      not 'evidence of a keystream', it is just the absence of evidence for a")
P("      single fixed table.")
# how many conflicts, and what chromatic number, would random cribs give?
def chi_of(pts):
    E = []
    for i in range(24):
        for j in range(i + 1, 24):
            if (cpos[i] == cpos[j]) != (pts[i] == pts[j]):
                E.append((i, j))
    ad = {i: set() for i in range(24)}
    for i, j in E:
        ad[i].add(j); ad[j].add(i)
    order = sorted(range(24), key=lambda v: -len(ad[v]))
    for k in range(1, 27):
        col = {}
        if _bt(ad, order, k, col):
            return k, len(E)
    return 26, len(E)
T2 = 5000
chis = Counter(); nedge = []
for _ in range(T2):
    pts = [ENGL[rng.integers(len(ENGL))] for _ in range(24)]
    k, e = chi_of(pts)
    chis[k] += 1; nedge.append(e)
P("      distribution of the forced-alphabet count (chromatic number) under")
P("      random English cribs, %d trials: %s" % (T2, dict(sorted(chis.items()))))
P("      mean conflict edges %.1f (K4 has 22)" % (sum(nedge) / len(nedge)))

# ------------------------------------------------------------------ B4
P("\nB4. How many substitution alphabets do the cribs FORCE?")
P("    Build a conflict graph on the 24 crib positions: join i,j if they cannot")
P("    share one alphabet, i.e. same ciphertext letter but different plaintext, or")
P("    same plaintext letter but different ciphertext.  The chromatic number is")
P("    the minimum number of distinct substitution alphabets any cipher must use.")
V = list(range(24))
edges = set()
for i in V:
    for j in range(i + 1, 24):
        _, ci, pi = CRIBS[i]
        _, cj, pj = CRIBS[j]
        if (ci == cj) != (pi == pj):
            edges.add((i, j))
adj = {i: set() for i in V}
for i, j in edges:
    adj[i].add(j); adj[j].add(i)
P("    conflict edges: %d" % len(edges))

def chromatic(adj, V):
    for k in range(1, 27):
        colour = {}
        def bt(idx):
            if idx == len(V):
                return True
            v = V[idx]
            used = {colour[u] for u in adj[v] if u in colour}
            for c in range(k):
                if c in used:
                    continue
                colour[v] = c
                if bt(idx + 1):
                    return True
                del colour[v]
            return False
        order = sorted(V, key=lambda v: -len(adj[v]))
        if bt(0) if False else (lambda: (colour.clear(), _bt(adj, order, k, colour))[1])():
            return k, dict(colour)
    return None, None

chi, col = chromatic(adj, V)
P("    *** chromatic number = %d ***" % chi)
P("    So at least %d different substitution alphabets are needed.  One legal" % chi)
P("    %d-colouring of the crib positions (1-indexed):" % chi)
groups = defaultdict(list)
for v, c in col.items():
    groups[c].append(CRIBS[v][0] + 1)
for c in sorted(groups):
    P("      alphabet %d: %s" % (c + 1, sorted(groups[c])))

# alphabet-free periodicity consequence
P("\n    Consequence for periodic ciphers (alphabet-free): a period p is possible")
P("    only if no conflicting pair of positions is congruent mod p.")
diffs = sorted({abs(CRIBS[i][0] - CRIBS[j][0]) for i, j in edges})
P("    conflicting-pair distances: %s" % diffs)
ok = [p for p in range(1, 98)
      if all((CRIBS[i][0] - CRIBS[j][0]) % p != 0 for i, j in edges)]
P("    periods 1..97 surviving: %s" % ok)
P("    (This reproduces, with no alphabet assumptions at all, the known result")
P("    that short periods are dead; it is the same test as crib_lib.universal_ok.)")

with open("/Users/pravarkataria/Desktop/crypto/kryptos/analysis/matrix_b_output.txt", "w") as f:
    f.write("\n".join(out) + "\n")
