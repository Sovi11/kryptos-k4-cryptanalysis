"""(h) The irregular-advance sweep made ALPHABET-INDEPENDENT.

seg_c, seg_d and seg_e test each candidate key-advance rule against 867 keyword-mixed
cipher configurations (and, in seg_c and seg_d, against a further 208,627 dictionary
alphabets).  A sceptic can always answer: "your alphabet was not in the list."

This script removes that objection entirely, using the argument `findings/geometry.md`
applied to plain periodic keys.  Whatever the key alphabet and whatever the mixed
alphabets, a key slot is ONE monoalphabetic substitution.  So inside a single key slot
the map ciphertext letter -> plaintext letter must be a partial BIJECTION:

    * the same ciphertext letter cannot decrypt to two different plaintext letters;
    * two different ciphertext letters cannot decrypt to the same plaintext letter.

Applied to K4's 24 crib pairs this yields 22 CONFLICTING PAIRS of crib positions that
can never share a key slot.  A key-advance rule whose pointer puts a conflicting pair
into the same slot is therefore impossible for EVERY alphabet set that exists - not
merely for the ones anybody tested.  That is a proof, not a search.

Sections:
  H0  machinery check: reproduce the published plain-periodic impossibility list.
  H1  ciphertext-triggered rules (the seg_c family), alphabet-independent.
  H2  plaintext-triggered rules with free per-run offsets (the seg_e E1 family).
  H3  interrupted keys: one or two inserted/deleted key letters (the seg_d family).
  H4  the UNRESTRICTED irregular advance: any monotone pointer path at all.
"""
import itertools
import math
import sys
import time
from collections import Counter, defaultdict

import numpy as np

import seg_common as S

CT = S.CT
N = 97
PLAIN = S.PLAIN
CRIB_POS = np.array(S.CRIB_POS)
CRIB_CT = S.CRIB_CT
CRIB_PT = S.CRIB_PT

# ------------------------------------------------------------------ conflicts
CONFLICT = [(a, b) for a in range(24) for b in range(a + 1, 24)
            if (CRIB_CT[a] == CRIB_CT[b]) != (CRIB_PT[a] == CRIB_PT[b])]
CA = np.array([x[0] for x in CONFLICT])
CB = np.array([x[1] for x in CONFLICT])
RUN1_CONF = [(a, b) for a, b in CONFLICT if b < 13]
RUN2_CONF = [(a - 13, b - 13) for a, b in CONFLICT if a >= 13]
CROSS_CONF = [(a, b - 13) for a, b in CONFLICT if a < 13 <= b]


def possible(resid):
    """True iff this residue assignment puts no conflicting pair in one key slot."""
    r = np.asarray(resid)
    return not bool((r[CA] == r[CB]).any())


def possible_batch(res):
    """res: (n, 24) residue matrix -> (n,) bool."""
    return ~(res[:, CA] == res[:, CB]).any(axis=1)


def _verify():
    # the conflict list must be exactly the pairs that break function-ness or injectivity
    for a, b in CONFLICT:
        assert (CRIB_CT[a] == CRIB_CT[b] and CRIB_PT[a] != CRIB_PT[b]) or \
               (CRIB_CT[a] != CRIB_CT[b] and CRIB_PT[a] == CRIB_PT[b])
    # a partition that puts every crib in its own slot is always possible
    assert possible(np.arange(24))
    # a partition that puts everything in one slot is not
    assert not possible(np.zeros(24, dtype=int))
    # synthetic: build a ciphertext from a known period-5 key with arbitrary mixed
    # alphabets per slot, and check the true period is never declared impossible
    rng = np.random.default_rng(41)
    pt = ("THEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGROUNDTOANUNKNOWN"
          "LOCATIONDOESLANGLEYKNOWABOUTTHISTHEYSHOULD")[:97]
    p = 5
    alphas = ["".join(rng.permutation(list(PLAIN))) for _ in range(p)]
    ct = "".join(alphas[i % p][ord(pt[i]) - 65] for i in range(N))
    cct = "".join(ct[i] for i in S.CRIB_POS)
    cpt = "".join(pt[i] for i in S.CRIB_POS)
    conf = [(a, b) for a in range(24) for b in range(a + 1, 24)
            if (cct[a] == cct[b]) != (cpt[a] == cpt[b])]
    res = CRIB_POS % p
    assert not any(res[a] == res[b] for a, b in conf), \
        "the true period was wrongly declared impossible"
    return True


def h0():
    print("=" * 78)
    print("H0. MACHINERY CHECK - plain periodic key, alphabet-independent")
    print("=" * 78)
    print(f"conflicting crib pairs (cannot share a key slot under ANY alphabet): "
          f"{len(CONFLICT)}")
    for a, b in CONFLICT:
        print(f"    pos {S.CRIB_POS[a]+1:>2} {CRIB_CT[a]}->{CRIB_PT[a]}   "
              f"vs  pos {S.CRIB_POS[b]+1:>2} {CRIB_CT[b]}->{CRIB_PT[b]}   "
              f"({'same ct, different pt' if CRIB_CT[a] == CRIB_CT[b] else 'different ct, same pt'})")
    imp = [p for p in range(2, 31) if not possible(CRIB_POS % p)]
    print(f"\nplain periodic key - periods IMPOSSIBLE for every alphabet set: {imp}")
    published = [2, 3, 4, 5, 6, 7, 9, 10, 14, 15, 17, 21, 25]
    print(f"published list in findings/geometry.md section 5:                {published}")
    print("match:", "YES" if imp[:len(published)] == published or
          set(published) <= set(imp) else "NO")
    print("(geometry.md scanned 2..26; this scan goes to 30.)")
    return imp


# ------------------------------------------------------------------ H1
DOUBLES_SECOND = {i for i in range(1, N) if CT[i] == CT[i - 1]}
TRIGGERS_CT = {}
for _ch in PLAIN:
    TRIGGERS_CT[f"letter {_ch}"] = {i for i in range(N) if CT[i] == _ch}
TRIGGERS_CT["doubled-2nd"] = DOUBLES_SECOND
TRIGGERS_CT["doubled-1st"] = {i - 1 for i in DOUBLES_SECOND}
TRIGGERS_CT["the two X"] = {i for i in range(N) if CT[i] == "X"}
TRIGGERS_CT["panel-row bounds"] = {4, 35, 66}
TRIGGERS_CT["vowels AEIOU"] = {i for i in range(N) if CT[i] in "AEIOU"}
TRIGGERS_CT["KRYPTOS letters"] = {i for i in range(N) if CT[i] in "KRYPTOS"}
VARIANTS = ["HOLD", "DOUBLE", "RESET_AFTER", "RESET_AT", "ADVANCE_ONLY"]


def pointer_map(variant, trig, delay=0):
    t = {i + delay for i in trig}
    j = np.empty(N, dtype=np.int64)
    cur = 0
    for i in range(N):
        if variant == "RESET_AT" and i in t:
            cur = 0
        j[i] = cur
        if variant == "HOLD":
            cur += 0 if i in t else 1
        elif variant == "DOUBLE":
            cur += 2 if i in t else 1
        elif variant == "RESET_AFTER":
            cur = 0 if i in t else cur + 1
        elif variant == "RESET_AT":
            cur += 1
        elif variant == "ADVANCE_ONLY":
            cur += 1 if i in t else 0
    return j


def h1():
    print()
    print("=" * 78)
    print("H1. CIPHERTEXT-TRIGGERED RULES (the seg_c family), alphabet-independent")
    print("=" * 78)
    tot = 0
    imp = 0
    by_variant = Counter(); imp_by_variant = Counter()
    survivors = []
    for v in VARIANTS:
        for tname, trig in TRIGGERS_CT.items():
            if not trig:
                continue
            for delay in (0, 1):
                j = pointer_map(v, trig, delay)
                for p in range(2, 27):
                    tot += 1
                    by_variant[v] += 1
                    if not possible(j[CRIB_POS] % p):
                        imp += 1
                        imp_by_variant[v] += 1
                    else:
                        survivors.append((v, tname, delay, p))
    print(f"(rule, trigger, delay, period) combinations: {tot:,}")
    print(f"IMPOSSIBLE for every alphabet set that exists: {imp:,} "
          f"({100.0 * imp / tot:.1f}%)")
    print(f"not excluded by this argument alone: {tot - imp:,}")
    print("  by rule: " + "  ".join(f"{v}:{imp_by_variant[v]}/{by_variant[v]}"
                                    for v in VARIANTS))
    surv_p = Counter(s[3] for s in survivors)
    print("  periods among the not-excluded: " +
          " ".join(f"{p}:{surv_p[p]}" for p in sorted(surv_p)))
    print("  (seg_c then killed all of these on the 867 keyword configurations and the")
    print("   208,627-alphabet dictionary pass, at exactly the chance rate.)")
    return imp, tot


# ------------------------------------------------------------------ H2
PT1 = CRIB_PT[:13]
PT2 = CRIB_PT[13:]
TRIG_SETS_PT = {f"letter {c}": frozenset(c) for c in PLAIN}
TRIG_SETS_PT["vowels AEIOU"] = frozenset("AEIOU")
TRIG_SETS_PT["KRYPTOS letters"] = frozenset("KRYPTOS")
TRIG_SETS_PT["BERLIN letters"] = frozenset("BERLIN")
TRIG_SETS_PT["high-freq ETAOIN"] = frozenset("ETAOIN")
TRIG_SETS_PT["rare JQXZ"] = frozenset("JQXZ")


def run_pointer(rule, trigset, pt_run):
    n = len(pt_run)
    rel = np.zeros(n, dtype=np.int64)
    isabs = np.zeros(n, dtype=bool)
    cur = 0; absf = False
    for t in range(n):
        ch = pt_run[t]
        if rule == "RESET_AT" and ch in trigset:
            cur = 0; absf = True
        rel[t] = cur; isabs[t] = absf
        if rule == "HOLD":
            cur += 0 if ch in trigset else 1
        elif rule == "DOUBLE":
            cur += 2 if ch in trigset else 1
        elif rule == "RESET_AFTER":
            if ch in trigset:
                cur = 0; absf = True
            else:
                cur += 1
        elif rule == "RESET_AT":
            cur += 1
        elif rule == "ADVANCE_ONLY":
            cur += 1 if ch in trigset else 0
    return rel, isabs


def h2():
    print()
    print("=" * 78)
    print("H2. PLAINTEXT-TRIGGERED RULES with free per-run offsets (seg_e E1 family),")
    print("    alphabet-independent")
    print("=" * 78)
    tot = 0; imp = 0
    surv_keys = Counter()
    for rule in VARIANTS:
        for tname, trig in TRIG_SETS_PT.items():
            r1, a1 = run_pointer(rule, trig, PT1)
            r2, a2 = run_pointer(rule, trig, PT2)
            for p in range(2, 27):
                res_all = []
                for b1 in range(p):
                    x1 = np.where(a1, r1 % p, (b1 + r1) % p)
                    for b2 in range(p):
                        x2 = np.where(a2, r2 % p, (b2 + r2) % p)
                        res_all.append(np.concatenate([x1, x2]))
                res_all = np.array(res_all)
                ok = possible_batch(res_all)
                tot += res_all.shape[0]
                imp += int((~ok).sum())
                if ok.any():
                    surv_keys[(rule, p)] += int(ok.sum())
    print(f"(rule, trigger, period, offset1, offset2) combinations: {tot:,}")
    print(f"IMPOSSIBLE for every alphabet set: {imp:,} ({100.0 * imp / tot:.1f}%)")
    print(f"not excluded: {tot - imp:,}")
    print("  not-excluded counts by (rule, period), top 12:")
    for (rule, p), n in surv_keys.most_common(12):
        print(f"    {rule:<12} p={p:<3} {n}")
    print("  (seg_e then tested all of these against 867 configurations: 0 survivors")
    print("   at c >= 5, and the E2 forward simulation predicted 0 of 11 BERLINCLOCK")
    print("   letters better than chance in 673,297 fully determined simulations.)")
    return imp, tot


# ------------------------------------------------------------------ H3
def h3():
    print()
    print("=" * 78)
    print("H3. INTERRUPTED KEYS - inserted / deleted key letters (seg_d family),")
    print("    alphabet-independent")
    print("=" * 78)
    ar = np.arange(N)
    # D0: free desync between the runs
    tot = imp = 0
    d0_surv = []
    for p in range(2, 27):
        for d in range(p):
            j = ar.copy(); j[63:] += d
            tot += 1
            if not possible(j[CRIB_POS] % p):
                imp += 1
            else:
                d0_surv.append((p, d))
    print(f"D0 free desync: {tot} (period, offset) pairs, {imp} impossible for every")
    print(f"   alphabet ({100.0 * imp / tot:.1f}%), {tot - imp} not excluded")
    # D1
    uniq = {}
    for b in range(1, N):
        for eps in (1, -1):
            j = ar + eps * (ar >= b)
            uniq.setdefault(tuple(j[CRIB_POS].tolist()), j)
    tot1 = imp1 = 0
    for key, j in uniq.items():
        for p in range(2, 21):
            tot1 += 1
            if not possible(j[CRIB_POS] % p):
                imp1 += 1
    print(f"D1 one insert/delete: {len(uniq)} distinct crib-restricted maps x 19 periods "
          f"= {tot1} tests")
    print(f"   impossible for every alphabet: {imp1} ({100.0 * imp1 / tot1:.1f}%), "
          f"{tot1 - imp1} not excluded")
    # D2
    uniq2 = {}
    for b1 in range(1, N):
        for b2 in range(b1, N):
            for e1 in (1, -1):
                for e2 in (1, -1):
                    j = ar + e1 * (ar >= b1) + e2 * (ar >= b2)
                    uniq2.setdefault(tuple(j[CRIB_POS].tolist()), j)
    tot2 = imp2 = 0
    for key, j in uniq2.items():
        for p in range(2, 21):
            tot2 += 1
            if not possible(j[CRIB_POS] % p):
                imp2 += 1
    print(f"D2 two inserts/deletes: {len(uniq2)} distinct crib-restricted maps x 19 "
          f"periods = {tot2:,} tests")
    print(f"   impossible for every alphabet: {imp2:,} ({100.0 * imp2 / tot2:.1f}%), "
          f"{tot2 - imp2:,} not excluded")
    return (imp, tot), (imp1, tot1), (imp2, tot2)


# ------------------------------------------------------------------ H4
def cum_patterns(nstep, steps):
    grids = np.array(np.meshgrid(*[np.array(steps)] * nstep,
                                 indexing="ij")).reshape(nstep, -1).T
    cum = np.zeros((grids.shape[0], nstep + 1), dtype=np.int64)
    cum[:, 1:] = np.cumsum(grids, axis=1)
    return cum


def filter_run(cum, conf, p):
    idx = np.arange(cum.shape[0])
    for a, b in conf:
        idx = idx[((cum[idx, b] - cum[idx, a]) % p) != 0]
        if idx.size == 0:
            break
    return idx


def h4():
    print()
    print("=" * 78)
    print("H4. THE UNRESTRICTED IRREGULAR ADVANCE, alphabet-independent")
    print("=" * 78)
    print("No trigger, no rule: the key pointer is ANY monotone path whose increments")
    print("come from the step set.  For each period, is there ANY such path at all whose")
    print("induced key slots avoid all 22 conflicting crib pairs?  Answering NO kills the")
    print("whole family at that period for every alphabet, every key, every trigger and")
    print("every skip pattern simultaneously.\n")
    print("Consistency depends only on the 12 increments inside EASTNORTHEAST, the 10")
    print("inside BERLINCLOCK and the residue offset D between the runs; increments")
    print("outside the crib spans are free and affect nothing.\n")
    results = {}
    for stepname, steps in (("{0,1} pure skip", (0, 1)),
                            ("{1,2} pure double-advance", (1, 2)),
                            ("{0,1,2} skip and double", (0, 1, 2))):
        c1 = cum_patterns(12, steps)
        c2 = cum_patterns(10, steps)
        print(f"--- step set {stepname}   ({c1.shape[0]:,} x {c2.shape[0]:,} "
              f"increment vectors)")
        print(f"    {'p':>3} {'paths in run1':>14} {'paths in run2':>14} "
              f"{'admissible (R1,R2,D)':>22} {'verdict':>16}")
        print("    ('~' marks a 500k-draw Monte Carlo estimate; IMPOSSIBLE is always exact)")
        dead = []
        for p in range(2, 31):
            i1 = filter_run(c1, RUN1_CONF, p)
            i2 = filter_run(c2, RUN2_CONF, p)
            if i1.size == 0 or i2.size == 0:
                print(f"    {p:>3} {i1.size:>14,} {i2.size:>14,} {0:>22,} "
                      f"{'IMPOSSIBLE':>16}")
                dead.append(p)
                continue
            r1 = c1[i1] % p
            r2 = c2[i2] % p
            ca = np.array([x[0] for x in CROSS_CONF])
            cb = np.array([x[1] for x in CROSS_CONF])
            budget = i1.size * i2.size * p
            approx = False
            if budget > 5_000_000:
                # Monte Carlo first: we only need EXISTENCE for the verdict.
                rng = np.random.default_rng(900 + p)
                NS = 500_000
                s1 = r1[rng.integers(0, i1.size, NS)][:, ca]
                dd = rng.integers(0, p, NS)
                s2 = (r2[rng.integers(0, i2.size, NS)] + dd[:, None]) % p
                good = ~(s1 == s2[:, cb]).any(axis=1)
                nfound = int(good.sum())
                if nfound:
                    total = float(nfound) / NS * budget
                    approx = True
                else:
                    total = 0          # fall through to the exact count below
            if not approx and budget <= 5_000_000:
                total = 0
                step = max(1, 4_000_000 // max(i2.size, 1))
                for D in range(p):
                    r2d = (r2 + D) % p
                    for lo in range(0, i1.size, step):
                        hi = min(i1.size, lo + step)
                        a = r1[lo:hi][:, ca]
                        b = r2d[:, cb]
                        bad = (a[:, None, :] == b[None, :, :]).any(axis=2)
                        total += int((~bad).sum())
            elif not approx:
                # MC found nothing in 500k draws; confirm with the exact count.
                total = 0
                step = max(1, 2_000_000 // max(i2.size, 1))
                for D in range(p):
                    r2d = (r2 + D) % p
                    for lo in range(0, i1.size, step):
                        hi = min(i1.size, lo + step)
                        a = r1[lo:hi][:, ca]
                        b = r2d[:, cb]
                        bad = (a[:, None, :] == b[None, :, :]).any(axis=2)
                        total += int((~bad).sum())
            of = c1.shape[0] * c2.shape[0] * p
            tag = "~" if approx else " "
            verdict = ("%s10^-%.2f of all" % (tag, math.log10(of) - math.log10(total))) if total else "IMPOSSIBLE"
            print(f"    {p:>3} {i1.size:>14,} {i2.size:>14,} {total:>22,.0f} {verdict:>16}")
            if total == 0:
                dead.append(p)
        print(f"    periods IMPOSSIBLE for every alphabet, key and skip pattern: {dead}")
        print()
        results[stepname] = dead
    return results


def main():
    t0 = time.time()
    assert _verify()
    print("verification: the conflict list is exactly the set of crib pairs that break")
    print("function-ness or injectivity, and a synthetic period-5 cipher built from five")
    print("ARBITRARY random mixed alphabets is not declared impossible at its true")
    print("period.  OK\n")
    h0()
    h1()
    h2()
    h3()
    h4()
    print(f"\n[runtime {time.time() - t0:.1f}s]")


if __name__ == "__main__":
    main()
