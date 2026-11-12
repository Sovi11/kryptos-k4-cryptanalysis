#!/usr/bin/env python3
"""Key streams with statistically flat differences, for the skip-aware LP2 search.

Every stream is returned as a numpy int array of values 0..28. Families:
  digits of constants (pi, e, sqrt2, sqrt3, sqrt5, phi, ln2, sqrt3301), read as 2-digit or
  3-digit groups mod 29 at every phase; concatenation constants (Copeland-Erdos primes,
  Champernowne, concatenated Fibonacci); totient phi(n) mod 29; SHA-256/512 hash chains from
  3301-related seeds (bytes mod 29); PRNGs (Python 3 randrange, Python 2 int(random()*29),
  glibc rand() % 29) for a few seeds.
Exact integer arithmetic throughout; no external libraries.
"""
import hashlib, math, random, sys
sys.set_int_max_str_digits(0)
import numpy as np

NDIG = 64000

def _arctan_inv(x, scale):
    """scale * arctan(1/x) by the alternating series, integers only."""
    total = term = scale // x; x2 = x * x; n = 1; sign = -1
    while term:
        term //= x2
        total += sign * (term // (2 * n + 1)); sign = -sign; n += 1
    return total

def digits_pi(n=NDIG):
    s = 10 ** (n + 20)
    pi = 4 * (4 * _arctan_inv(5, s) - _arctan_inv(239, s))
    return str(pi)[:n]                     # "31415..." (leading 3 included)

def digits_e(n=NDIG):
    s = 10 ** (n + 20); total = 0; term = s; k = 0
    while term:
        total += term; k += 1; term //= k
    return str(total)[:n]                  # "27182..."

def digits_sqrt(m, n=NDIG):
    return str(math.isqrt(m * 10 ** (2 * n)))[:n]

def digits_phi(n=NDIG):
    s5 = math.isqrt(5 * 10 ** (2 * (n + 5)))
    return str((10 ** (n + 5) + s5) // 2)[:n]   # "16180..."

def digits_ln2(n=NDIG):
    # ln 2 = 2 * artanh(1/3) = 2 * sum 1/((2k+1) 3^(2k+1))
    s = 10 ** (n + 20); total = 0; p = s // 3; k = 0
    while p:
        total += p // (2 * k + 1); p //= 9; k += 1
    return "0" + str(2 * total)[:n - 1]    # "0693..." keeps the integer part like the others

def digits_copeland_erdos(n=NDIG):
    out, k = [], 2
    sieve_n = 400000
    sieve = bytearray([1]) * (sieve_n + 1); sieve[0:2] = b"\x00\x00"
    for i in range(2, int(sieve_n ** 0.5) + 1):
        if sieve[i]: sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    s = "".join(str(i) for i in range(sieve_n + 1) if sieve[i])
    return s[:n]

def digits_champernowne(n=NDIG):
    out, k, L = [], 1, 0
    while L < n:
        t = str(k); out.append(t); L += len(t); k += 1
    return "".join(out)[:n]

def digits_fibcat(n=NDIG):
    out, a, b, L = [], 1, 1, 0
    while L < n:
        t = str(a); out.append(t); L += len(t); a, b = b, a + b
    return "".join(out)[:n]

def groups_mod29(d, g, phase):
    d = d[phase:]; m = len(d) // g
    return np.array([int(d[i * g:(i + 1) * g]) % 29 for i in range(m)], dtype=np.int64)

def totient_stream(n=30000):
    phi = list(range(n + 1))
    for p in range(2, n + 1):
        if phi[p] == p:
            for q in range(p, n + 1, p): phi[q] -= phi[q] // p
    return np.array([phi[k] % 29 for k in range(1, n + 1)], dtype=np.int64)

HASH_SEEDS = ["3301", "cicada", "cicada3301", "Cicada 3301", "liber primus", "LIBER PRIMUS",
              "divinity", "DIVINITY", "instar", "circumference", "1595277641",
              "36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4"]

def hash_chain(seed, algo, nbytes=40000):
    h = hashlib.new(algo, seed.encode()).digest(); out = bytearray()
    while len(out) < nbytes:
        out += h; h = hashlib.new(algo, h).digest()
    return np.frombuffer(bytes(out[:nbytes]), dtype=np.uint8).astype(np.int64) % 29

PRNG_SEEDS = [3301, 1033, 2012, 2013, 2014, 1595277641, 0, 1]

def py3_randrange(seed, n=30000):
    r = random.Random(seed); return np.array([r.randrange(29) for _ in range(n)], dtype=np.int64)

def py2_randrange(seed, n=30000):
    r = random.Random(seed); return np.array([int(r.random() * 29) for _ in range(n)], dtype=np.int64)

def glibc_rand(seed, n=30000):
    r = [0] * 34; r[0] = seed if seed != 0 else 1
    for i in range(1, 31):
        hi, lo = divmod(r[i - 1], 127773)
        word = 16807 * lo - 2836 * hi
        if word < 0: word += 2147483647
        r[i] = word
    for i in range(31, 34): r[i] = r[i - 31]
    out = []
    for i in range(34, 34 + 310 + n):
        v = (r[i - 31] + r[i - 3]) & 0xFFFFFFFF; r.append(v)
        if i >= 344: out.append((v >> 1) % 29)
    return np.array(out[:n], dtype=np.int64)

def all_streams():
    """List of (name, generator-thunk). Thunks so worker processes build streams lazily."""
    S = []
    consts = [("pi", digits_pi), ("e", digits_e), ("sqrt2", lambda: digits_sqrt(2)),
              ("sqrt3", lambda: digits_sqrt(3)), ("sqrt5", lambda: digits_sqrt(5)),
              ("phi", digits_phi), ("ln2", digits_ln2), ("sqrt3301", lambda: digits_sqrt(3301)),
              ("copeland-erdos", digits_copeland_erdos), ("champernowne", digits_champernowne),
              ("fibcat", digits_fibcat)]
    for name, f in consts:
        for g in (2, 3):
            for ph in range(g):
                S.append((f"{name}/{g}-digit/phase{ph}", ("digits", name, g, ph)))
    S.append(("totient(n)", ("totient",)))
    for algo in ("sha256", "sha512"):
        for sd in HASH_SEEDS:
            S.append((f"{algo}-chain('{sd[:16]}')", ("hash", sd, algo)))
    for sd in PRNG_SEEDS:
        for kind in ("py3", "py2", "glibc"):
            S.append((f"{kind}-rand({sd})", ("prng", kind, sd)))
    return S

_DIG = {}
def build(spec):
    kind = spec[0]
    if kind == "digits":
        _, name, g, ph = spec
        if name not in _DIG:
            f = {"pi": digits_pi, "e": digits_e, "sqrt2": lambda: digits_sqrt(2), "sqrt3": lambda: digits_sqrt(3),
                 "sqrt5": lambda: digits_sqrt(5), "phi": digits_phi, "ln2": digits_ln2,
                 "sqrt3301": lambda: digits_sqrt(3301), "copeland-erdos": digits_copeland_erdos,
                 "champernowne": digits_champernowne, "fibcat": digits_fibcat}[name]
            _DIG[name] = f()
        return groups_mod29(_DIG[name], g, ph)
    if kind == "totient": return totient_stream()
    if kind == "hash": return hash_chain(spec[1], spec[2])
    if kind == "prng":
        return {"py3": py3_randrange, "py2": py2_randrange, "glibc": glibc_rand}[spec[1]](spec[2])
    raise ValueError(spec)

if __name__ == "__main__":
    # sanity checks against known values
    assert digits_pi(30) == "314159265358979323846264338327", digits_pi(30)
    assert digits_e(20) == "27182818284590452353"
    assert digits_sqrt(2, 15) == "141421356237309"
    assert digits_phi(15) == "161803398874989"
    assert digits_ln2(15) == "069314718055994", digits_ln2(15)
    assert digits_copeland_erdos(15) == "235711131719232"
    assert list(glibc_rand(1, 3)) == [1804289383 % 29, 846930886 % 29, 1681692777 % 29]
    S = all_streams(); print(len(S), "streams")
    for name, spec in S[:3] + S[-3:]:
        k = build(spec); d = np.diff(k) % 29
        print(f"{name:40s} len {len(k)}  diff-chi2 {((np.bincount(d,minlength=29)-len(d)/29)**2/(len(d)/29)).sum():.1f}")
