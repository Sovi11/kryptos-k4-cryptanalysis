"""Do 3301-style number streams, used as keys on real English runes, reproduce LP2's
fingerprint: flat frequencies, flat adjacent differences EXCEPT d=0 suppressed ~5x?"""
import random, math
from collections import Counter
from lp_common import LATIN, IDX, RUNES, ioc, lp2_unsolved

# --- English -> Gematria Primus runes (greedy digraphs) ---
CORPUS = "/Users/pravarkataria/Desktop/crypto/kryptos/analysis/.search_corpus.txt"
raw = open(CORPUS).read(400000)
DI = {"ING": 21, "TH": 2, "EO": 12, "NG": 21, "OE": 22, "AE": 25, "IA": 27, "IO": 27, "EA": 28}
SG = {L: i for i, L in enumerate(LATIN) if len(L) == 1}
SG.update({"K": 5, "Q": 5, "V": 1, "Z": 15})
eng, i = [], 0
while i < len(raw) and len(eng) < 60000:
    for dg in ("ING", "TH", "EO", "NG", "OE", "AE", "IA", "IO", "EA"):
        if raw.startswith(dg, i):
            eng.append(DI[dg]); i += len(dg); break
    else:
        if raw[i] in SG: eng.append(SG[raw[i]])
        i += 1
print(f"English rune text: {len(eng)} runes, IoC {ioc(eng):.3f}, plaintext doublet rate {sum(eng[j]==eng[j-1] for j in range(1,len(eng)))/(len(eng)-1)*100:.2f}%")

def primes(n):
    sieve = bytearray([1]) * (n + 1); sieve[0:2] = b"\x00\x00"
    for p in range(2, int(n ** 0.5) + 1):
        if sieve[p]: sieve[p*p::p] = bytearray(len(sieve[p*p::p]))
    return [i for i in range(n + 1) if sieve[i]]
P = primes(1_200_000)
def totients(n):
    phi = list(range(n + 1))
    for p in range(2, n + 1):
        if phi[p] == p:
            for k in range(p, n + 1, p): phi[k] -= phi[k] // p
    return phi
PHI = totients(80000)
fib = [0, 1]
while len(fib) < 80000: fib.append((fib[-1] + fib[-2]) % 29)
rng = random.Random(11)
STREAMS = {
    "phi(prime_n) = p_n - 1": lambda n: P[n] - 1,
    "prime_n":                lambda n: P[n],
    "prime_(prime_n)":        lambda n: P[P[n] - 1] if P[n] - 1 < len(P) else 0,
    "Fibonacci F_n":          lambda n: fib[n],
    "totient phi(n)":         lambda n: PHI[n + 1],
    "n (Trithemius)":         lambda n: n,
    "uniform random":         lambda n: rng.randrange(29),
}

def fingerprint(c):
    n = len(c) - 1
    d = Counter((c[j] - c[j-1]) % 29 for j in range(1, len(c)))
    e = n / 29
    chi = sum((d[k] - (n - d[0]) / 28) ** 2 / ((n - d[0]) / 28) for k in range(1, 29))
    fr = Counter(c); expd = sum(v * v for v in fr.values()) / len(c)
    return d[0] / expd, chi, ioc(c)

def encrypt(stream, sign, fskip, start, L=12956):
    out, n = [], start
    for p in eng[start % 20000: start % 20000 + L]:
        if fskip and p == 0:
            out.append(0); continue
        out.append((p + sign * STREAMS[stream](n)) % 29); n += 1
    return out

s, _ = lp2_unsolved()
r, chi, ic = fingerprint(s)
print(f"\nLP2 target fingerprint: doublet ratio {r:.3f}  chi2(d=1..28) {chi:.1f}  IoC {ic:.4f}   F share {s.count(0)/len(s)*100:.2f}% (uniform 3.45%)\n")
print(f"{'stream':26s} {'op':3s} {'Fskip':5s}  doublet-ratio  chi2(d!=0)  IoC     (avg of 4 start offsets)")
for name in STREAMS:
    for sign in (1, -1):
        for fskip in (False, True):
            res = [fingerprint(encrypt(name, sign, fskip, st)) for st in (0, 3000, 9000, 17000)]
            a = [sum(x[k] for x in res) / len(res) for k in range(3)]
            flag = "  <-- suppresses doublets" if a[0] < 0.5 else ""
            print(f"{name:26s} {'+' if sign>0 else '-':3s} {str(fskip):5s}   {a[0]:6.3f}      {a[1]:8.1f}   {a[2]:.4f}{flag}")
