"""Direct attack on the feedback family:
     c_i = c_{i-1} + m_i * (p_i - z)        (multiplicative feedback, m_i != 0 mod 29)
     c_i = c_{i-1} + p_i + k_i               (additive feedback, for completeness)
  => q_i = d_i * inv(m_i)   or   q_i = d_i - k_i   should be English (IoC ~1.7).
Streams: 3301-style number sequences; start offset 0..OFF; per LP2 section.
Zero multipliers are handled two ways: 'filter' (skip values = 0 mod 29) and 'plus1'."""
import numpy as np
from lp_common import sections, tokens

OFF, L = 16000, 400
def primes(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for p in range(2, int(n ** .5) + 1):
        if s[p]: s[p*p::p] = False
    return np.nonzero(s)[0]
P = primes(3_000_000)
n = np.arange(1, 400000)
phi = np.arange(400001)
for p in P[P <= 400000]:
    phi[p::p] -= phi[p::p] // p
fib = np.zeros(400000, np.int64); fib[1] = 1
for i in range(2, 400000): fib[i] = (fib[i-1] + fib[i-2]) % 29
raw = {
    "prime_n": P, "phi(prime)=p-1": P - 1, "prime_(prime)": P[P[:19000] - 1],
    "totient(n)": phi[1:], "fibonacci": fib[1:], "n": n, "n^2": n * n,
    "prime gaps": np.diff(P),
}
INV = np.zeros(29, np.int64)
for a in range(1, 29): INV[a] = pow(a, 27, 29)

def stream_variants():
    for name, arr in raw.items():
        a = (arr % 29).astype(np.int64)
        yield name + " [filter0]", a[a != 0][: OFF + L + 5]
        yield name + " [+1]", ((a + 1) % 29)[: OFF + L + 5]

secs = []
for head, blocks in sections():
    if head.startswith(("73.jpg", "74.jpg")): continue
    r = [v for b in blocks for k, v in tokens(b) if k == "r"]
    if len(r) > L + 1: secs.append((head.split(" - ")[-1], np.array(r)))
print(f"sections tested: {len(secs)}  (first {L} differences each, offsets 0..{OFF})")

def ioc_rows(Q):
    rows = Q.shape[0]
    cnt = np.bincount((np.arange(rows)[:, None] * 29 + Q).ravel(), minlength=rows * 29).reshape(rows, 29)
    return 29 * (cnt * (cnt - 1)).sum(1) / (L * (L - 1))

rng = np.random.default_rng(5)
# null: same pipeline on shuffled differences -> distribution of the max over offsets
best_overall = []
for sname, c in secs:
    d = (c[1:L+1] - c[:L]) % 29
    for vname, s in stream_variants():
        W = np.lib.stride_tricks.sliding_window_view(s, L)[:OFF]
        mult = ioc_rows((d[None, :] * INV[W]) % 29)
        best_overall.append((mult.max(), sname, vname, "mult", int(mult.argmax())))
        if "[+1]" in vname:   # additive feedback uses raw stream values
            add = ioc_rows((d[None, :] - W) % 29)
            best_overall.append((add.max(), sname, vname.replace("[+1]", ""), "add", int(add.argmax())))
best_overall.sort(reverse=True)
print("\ntop 10 (section, stream, mode, offset) by max IoC of recovered text:")
for b in best_overall[:10]:
    print(f"  IoC {b[0]:.3f}  {b[1]:22s} {b[2]:26s} {b[3]:4s} offset {b[4]}")
# null calibration: shuffle d, take max over offsets for a few streams
nulls = []
for sname, c in secs[:4]:
    d = (c[1:L+1] - c[:L]) % 29
    for vname, s in list(stream_variants())[:6]:
        W = np.lib.stride_tricks.sliding_window_view(s, L)[:OFF]
        dd = rng.permutation(d)
        nulls.append(ioc_rows((dd[None, :] * INV[W]) % 29).max())
print(f"\nnull (shuffled differences), max over {OFF} offsets: mean {np.mean(nulls):.3f}, max {np.max(nulls):.3f}")
print("English plaintext would give IoC ~1.7")
