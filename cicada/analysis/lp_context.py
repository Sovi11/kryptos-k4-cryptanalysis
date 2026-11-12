"""Test the ledger's favourite: 'the shift for rune i depends on the previous rune'.

Key idea: if c_i = g_v(p_i) where v = c_{i-1} (ANY function/permutation per previous
ciphertext rune, plus an optional constant), then the runes that follow a given v
form a monoalphabetic encryption of English -> normalized IoC ~1.7 per group.
This tests the whole family at once without guessing g.
"""
import random
from collections import Counter
from lp_common import *

s, brk = lp2_unsolved()
N = len(s)
pairs_all = list(range(1, N))
pairs_in = [i for i in pairs_all if not brk[i]]

def chi2_uniform(cnt, cats):
    tot = sum(cnt[c] for c in cats); e = tot / len(cats)
    return sum((cnt[c] - e) ** 2 / e for c in cats)

print("=== 1. Distribution of the difference d = c_i - c_{i-1} (mod 29) ===")
for name, idx in (("all pairs", pairs_all), ("within-word", pairs_in)):
    d = Counter((s[i] - s[i-1]) % 29 for i in idx)
    tot = len(idx)
    print(f"{name}: n={tot}  d=0: {d[0]} (uniform expects {tot/29:.0f})")
    print("   chi2 over d=1..28 vs uniform: %.1f on 27 df (5%% crit 40.1)" % chi2_uniform(d, range(1, 29)))
    print("   counts d=1..28:", " ".join(str(d[k]) for k in range(1, 29)))

def grouped_ioc(seq, keyfn, idx):
    groups = {}
    for i in idx:
        groups.setdefault(keyfn(i), []).append(seq[i])
    tot = sum(len(g) for g in groups.values())
    return sum(len(g) * ioc(g) for g in groups.values() if len(g) > 1) / tot, len(groups)

def shuffled_null(keyname, keyfn_maker, idx_maker, reps=200):
    vals = []
    rng = random.Random(1)
    for _ in range(reps):
        t = s[:]; rng.shuffle(t)
        kf = keyfn_maker(t); idx = idx_maker(t)
        vals.append(grouped_ioc(t, kf, idx)[0])
    m = sum(vals)/len(vals); sd = (sum((v-m)**2 for v in vals)/len(vals))**0.5
    return m, sd, max(vals)

print("\n=== 2. Conditional IoC: group c_i by context, IoC within groups ===")
print("    (English monoalphabetic per group would give ~1.7; random gives ~1.0)")
tests = [
    ("prev rune c_{i-1}",            lambda t: (lambda i: t[i-1]),                      lambda t: range(1, N)),
    ("prev 2 runes c_{i-2},c_{i-1}", lambda t: (lambda i: (t[i-2], t[i-1])),            lambda t: range(2, N)),
    ("rune two back c_{i-2}",        lambda t: (lambda i: t[i-2]),                      lambda t: range(2, N)),
    ("prev diff c_{i-1}-c_{i-2}",    lambda t: (lambda i: (t[i-1]-t[i-2]) % 29),       lambda t: range(2, N)),
    ("prev sum c_{i-1}+c_{i-2}",     lambda t: (lambda i: (t[i-1]+t[i-2]) % 29),       lambda t: range(2, N)),
    ("next rune c_{i+1}",            lambda t: (lambda i: t[i+1]),                      lambda t: range(0, N-1)),
]
for name, km, im in tests:
    obs, ng = grouped_ioc(s, km(s), im(s))
    m, sd, mx = shuffled_null(name, km, im, reps=100)
    print(f"  {name:30s} groups={ng:4d}  IoC={obs:.4f}   shuffled null {m:.4f} ± {sd:.4f} (max {mx:.4f})  z={(obs-m)/sd:+.2f}")

print("\n=== 3. Derived streams: is c_i - c_{i-1} (or the sum) English-like or periodic? ===")
for name, f in (("diff c_i-c_{i-1}", lambda i: (s[i]-s[i-1]) % 29),
                ("diff c_{i-1}-c_i", lambda i: (s[i-1]-s[i]) % 29),
                ("sum c_i+c_{i-1}",  lambda i: (s[i]+s[i-1]) % 29),
                ("prime diff",       lambda i: (PRIMES[s[i]]-PRIMES[s[i-1]]) % 29),
                ("prime-shift  c_i - prime(c_{i-1})", lambda i: (s[i]-PRIMES[s[i-1]]) % 29),
                ("prime-shift  c_i + prime(c_{i-1})", lambda i: (s[i]+PRIMES[s[i-1]]) % 29)):
    dd = [f(i) for i in range(1, N)]
    best = max(((sum(len(dd[j::p])*ioc(dd[j::p]) for j in range(p))/len(dd), p) for p in range(1, 61)))
    print(f"  {name:36s} IoC={ioc(dd):.4f}   best periodic column IoC over p=1..60: {best[0]:.4f} at p={best[1]}")
