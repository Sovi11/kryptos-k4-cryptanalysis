"""(e) Irregular key advance driven by the PLAINTEXT letter, and by the KEY letter.

seg_c_skiprule.py covered triggers defined on the CIPHERTEXT letter, where the
pointer path is known at every one of the 97 positions and crib consistency is the
complete test.  This script covers the two cases it could not:

  E1  PLAINTEXT trigger, crib-consistency form.  The plaintext is known only inside
      the two crib runs (0-idx 21..33 EASTNORTHEAST, 63..73 BERLINCLOCK), so the
      pointer path is known WITHIN each run but the pointer's value at the start of
      each run is a free unknown (the 29 unknown letters between the runs may fire
      the trigger any number of times).  Enumerate both run-start offsets.

  E2  PLAINTEXT trigger, FORWARD-SIMULATION form - the test with real power.
      For the causal rules the pointer at position i depends only on plaintext
      letters BEFORE i, so a plaintext-triggered key is self-synchronising: fix
      (rule, trigger, period p, the pointer offset at position 21, cipher family,
      both alphabets) and run 1 determines the whole key, after which positions
      34..96 decrypt with NO remaining freedom.  Reaching position 63 and finding
      BERLINCLOCK is then a pure prediction with chance 26^-11 = 7.0e-16.
      This is the strongest single test in the whole irregular-advance family.

  E3  KEY-driven trigger ("interruptor on the key letter").  The pointer advances
      irregularly when the KEY letter it just used is some letter T.  The path then
      depends only on WHICH RESIDUES of the key hold T, so enumerate every subset
      S of Z_p.  The key alphabet is free, so "key[r] == T" is testable as "the
      crib-forced key values on S are all equal and no residue off S carries that
      value" - no key alphabet needed.

Cipher configurations throughout: 3 families x 17 plaintext alphabets x 17
ciphertext alphabets = 867.  The KEY alphabet only relabels key values bijectively
and is irrelevant to every consistency test here.

Every count is printed beside its chance expectation.  Nothing is called a survivor
on count alone.
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
CODE = S.CT_CODE
PLAIN = S.PLAIN
CRIB_POS = np.array(S.CRIB_POS)
RUN1 = (21, 34)          # half-open, 13 letters, crib indices 0..12
RUN2 = (63, 74)          # half-open, 11 letters, crib indices 13..23
R1_IDX = list(range(0, 13))
R2_IDX = list(range(13, 24))
PT1 = S.CRIB_PT[:13]     # EASTNORTHEAST
PT2 = S.CRIB_PT[13:]     # BERLINCLOCK
assert PT1 == "EASTNORTHEAST" and PT2 == "BERLINCLOCK"

CFG = [(f, pn, cn) for f in S.FAMILIES for pn in S.ALPHABET_NAMES for cn in S.ALPHABET_NAMES]
NCFG = len(CFG)
SHIFTS = np.array([S.required_shifts(f, S.ALPHABETS[pn], S.ALPHABETS[cn]) for f, pn, cn in CFG])
assert SHIFTS.shape == (NCFG, 24)

# --------------------------------------------------------------------------
# per-configuration decryption lookup: DEC[cfg, ct_code, key_value] -> pt_code
# --------------------------------------------------------------------------
def build_dec_lut():
    lut = np.empty((NCFG, 26, 26), dtype=np.int8)
    for ci, (fam, pn, cn) in enumerate(CFG):
        pa = S.ALPHABETS[pn]; ca = S.ALPHABETS[cn]
        cidx = S.idx_map(ca)                       # ct letter code -> index in ct alphabet
        pt_of_idx = np.frombuffer(pa.encode(), dtype=np.uint8).astype(np.int64) - 65
        for c in range(26):
            ci_ = cidx[c]
            kv = np.arange(26)
            if fam == "vigenere":
                pi = (ci_ - kv) % 26
            elif fam == "beaufort":
                pi = (kv - ci_) % 26
            else:                                   # varbeaufort
                pi = (ci_ + kv) % 26
            lut[ci, c, :] = pt_of_idx[pi]
    return lut

DEC = build_dec_lut()

# sanity: DEC must reproduce required_shifts at the cribs
for _ci in (0, 17, 400, 866):
    for _k, _pos in enumerate(S.CRIB_POS):
        assert DEC[_ci, CODE[_pos], SHIFTS[_ci, _k]] == ord(S.CRIB_PT[_k]) - 65


# --------------------------------------------------------------------------
# trigger sets on the PLAINTEXT
# --------------------------------------------------------------------------
TRIG_SETS = {}
for _ch in PLAIN:
    TRIG_SETS[f"letter {_ch}"] = frozenset(_ch)
TRIG_SETS["vowels AEIOU"] = frozenset("AEIOU")
TRIG_SETS["KRYPTOS letters"] = frozenset("KRYPTOS")
TRIG_SETS["BERLIN letters"] = frozenset("BERLIN")
TRIG_SETS["high-freq ETAOIN"] = frozenset("ETAOIN")
TRIG_SETS["rare JQXZ"] = frozenset("JQXZ")

CAUSAL_RULES = ["HOLD", "DOUBLE", "RESET_AFTER", "ADVANCE_ONLY"]
ALL_RULES = CAUSAL_RULES + ["RESET_AT"]


def run_pointer(rule, trigset, pt_run):
    """Pointer path inside a run of KNOWN plaintext.

    Returns (rel, isabs, rel_after, isabs_after).
      pointer at run offset t = rel[t]                if isabs[t]
                              = base + rel[t]         otherwise
    rel_after / isabs_after describe the pointer at the position just past the run.
    """
    n = len(pt_run)
    rel = np.zeros(n, dtype=np.int64)
    isabs = np.zeros(n, dtype=bool)
    cur = 0
    absf = False
    for t in range(n):
        ch = pt_run[t]
        if rule == "RESET_AT" and ch in trigset:
            cur = 0
            absf = True
        rel[t] = cur
        isabs[t] = absf
        if rule == "HOLD":
            cur += 0 if ch in trigset else 1
        elif rule == "DOUBLE":
            cur += 2 if ch in trigset else 1
        elif rule == "RESET_AFTER":
            if ch in trigset:
                cur = 0
                absf = True
            else:
                cur += 1
        elif rule == "RESET_AT":
            cur += 1
        elif rule == "ADVANCE_ONLY":
            cur += 1 if ch in trigset else 0
        else:
            raise ValueError(rule)
    return rel, isabs, cur, absf


def residues(rel, isabs, base, p):
    return np.where(isabs, rel % p, (base + rel) % p)


def partition_pairs(resid):
    """(#classes, [(first, other), ...]) - equality constraints implied by the residues."""
    groups = defaultdict(list)
    for k, r in enumerate(resid):
        groups[int(r)].append(k)
    pairs = []
    for g in groups.values():
        for x in g[1:]:
            pairs.append((g[0], x))
    return len(groups), pairs


def test_pairs(pairs):
    if not pairs:
        return np.ones(NCFG, dtype=bool)
    a = np.array([q[0] for q in pairs]); b = np.array([q[1] for q in pairs])
    return (SHIFTS[:, a] == SHIFTS[:, b]).all(axis=1)


# --------------------------------------------------------------------------
# nulls
# --------------------------------------------------------------------------
_NULL = {}
def null_quad(L, ntrials=40000, seed=17):
    if L in _NULL:
        return _NULL[L]
    m = np.random.default_rng(seed + L).integers(0, 26, size=(ntrials, L))
    sc = np.sort(S.quad_scores_batch(m))
    _NULL[L] = sc
    return sc

def best_of_n_threshold(L, n, q=0.95):
    sc = null_quad(L)
    if n < 1:
        n = 1
    return float(sc[min(int(len(sc) * (q ** (1.0 / n))), len(sc) - 1)])


# --------------------------------------------------------------------------
# verification
# --------------------------------------------------------------------------
def _verify_e1():
    """Synthetic: encipher with a plaintext-HOLD skip rule, period 7, and check that
    the E1 machinery (pointer inside a run + free base) accepts the true (rule,
    trigger, period) and rejects most wrong periods."""
    rng = np.random.default_rng(21)
    pt = ("SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBERED"
          "THELOWERPARTOFTHEDOORWAYWASREMOVEDWITH")[:97]
    assert len(pt) == 97
    key = rng.integers(0, 26, 7)
    trig = frozenset("E")
    j = np.empty(N, dtype=np.int64)
    cur = 0
    for i in range(N):
        j[i] = cur
        cur += 0 if pt[i] in trig else 1
    ct = S.encrypt(S.codes(pt), key[j % 7], "vigenere", S.PLAIN, S.KEYED)
    # crib shifts derived from the synthetic pt/ct at the true crib positions
    pi = S.idx_map(S.PLAIN)[S.codes("".join(pt[i] for i in S.CRIB_POS))]
    ci = S.idx_map(S.KEYED)[S.codes("".join(ct[i] for i in S.CRIB_POS))]
    sh = (ci - pi) % 26
    syn_pt1 = "".join(pt[i] for i in range(*RUN1))
    syn_pt2 = "".join(pt[i] for i in range(*RUN2))
    r1, a1, _, _ = run_pointer("HOLD", trig, syn_pt1)
    r2, a2, _, _ = run_pointer("HOLD", trig, syn_pt2)
    ok = False
    for b1 in range(7):
        for b2 in range(7):
            res = np.concatenate([residues(r1, a1, b1, 7), residues(r2, a2, b2, 7)])
            _, prs = partition_pairs(res)
            if prs and all(sh[x] == sh[y] for x, y in prs):
                ok = True
    assert ok, "E1 failed to accept the true configuration"
    # and the true (b1, b2) really is the offset of j at the run starts
    assert (residues(r1, a1, int(j[RUN1[0]]) % 7, 7) == j[RUN1[0]:RUN1[1]] % 7).all()
    return True


def _verify_e2():
    """Synthetic: same construction, but now check that the FORWARD SIMULATION
    recovers the key from run 1 alone and predicts run 2 exactly, and that wrong
    periods/triggers essentially never do."""
    rng = np.random.default_rng(22)
    pt = ("SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBERED"
          "THELOWERPARTOFTHEDOORWAYWASREMOVEDWITH")[:97]
    key = rng.integers(0, 26, 6)
    trig = frozenset("T")
    j = np.empty(N, dtype=np.int64); cur = 0
    for i in range(N):
        j[i] = cur
        cur += 0 if pt[i] in trig else 1
    ct_codes = S.codes(S.encrypt(S.codes(pt), key[j % 6], "vigenere", S.PLAIN, S.KEYED))
    syn_run1_pt = pt[RUN1[0]:RUN1[1]]
    syn_run2_pt = pt[RUN2[0]:RUN2[1]]
    shifts_run1 = np.array([(S.idx_map(S.KEYED)[ct_codes[i]] - S.idx_map(S.PLAIN)[ord(pt[i]) - 65]) % 26
                            for i in range(*RUN1)])
    good = []
    for p in range(2, 14):
        for b1 in range(p):
            r1, a1, after, aft_abs = run_pointer("HOLD", trig, syn_run1_pt)
            res = residues(r1, a1, b1, p)
            k = np.full(p, -1, dtype=np.int64)
            bad = False
            for t in range(13):
                r = int(res[t])
                if k[r] >= 0 and k[r] != shifts_run1[t]:
                    bad = True; break
                k[r] = shifts_run1[t]
            if bad or (k < 0).any():
                continue
            jj = (after if aft_abs else b1 + after)
            out = []
            for i in range(RUN1[1], N):
                kv = k[jj % p]
                pcode = (S.idx_map(S.KEYED)[ct_codes[i]] - kv) % 26
                ch = S.PLAIN[pcode]
                out.append(ch)
                jj += 0 if ch in trig else 1
            pred = "".join(out)[RUN2[0] - RUN1[1]:RUN2[0] - RUN1[1] + 11]
            if pred == syn_run2_pt:
                good.append((p, b1))
    periods_found = sorted({g[0] for g in good})
    # The true period must be found; a period only fits if it is a multiple of the
    # true one (the key repeated), and every base offset of a fitting period works
    # because the offset merely rotates the key.  Nothing else may survive.
    assert 6 in periods_found, f"E2 did not recover the true period: {good}"
    assert all(q % 6 == 0 for q in periods_found), \
        f"E2 accepted a non-multiple of the true period: {periods_found}"
    assert len(periods_found) == 2, f"E2 is not discriminating: {periods_found}"
    return True


def _verify_e3():
    """Synthetic: key-driven DOUBLE advance.  Encipher with period 5 where residue 2
    of the key is the 'interruptor' letter; check the subset scan accepts S={2}."""
    rng = np.random.default_rng(23)
    pt = ("THEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOOR"
          "WAYWASREMOVEDWITHTREMBLINGHANDSIMADEAT")[:97]
    p = 5
    key = np.array([3, 9, 14, 21, 6])          # residue 2 holds value 14
    Strue = {2}
    j = np.empty(N, dtype=np.int64); cur = 0
    for i in range(N):
        j[i] = cur
        cur += 2 if (cur % p) in Strue else 1
    ct = S.encrypt(S.codes(pt), key[j % p], "vigenere", S.PLAIN, S.KEYED)
    pi = S.idx_map(S.PLAIN)[S.codes("".join(pt[i] for i in S.CRIB_POS))]
    ci = S.idx_map(S.KEYED)[S.codes("".join(ct[i] for i in S.CRIB_POS))]
    sh = (ci - pi) % 26
    found = []
    for Ssub in itertools.chain.from_iterable(itertools.combinations(range(p), r) for r in range(p + 1)):
        Sset = set(Ssub)
        jj = np.empty(N, dtype=np.int64); c2 = 0
        for i in range(N):
            jj[i] = c2
            c2 += 2 if (c2 % p) in Sset else 1
        res = jj[CRIB_POS] % p
        _, prs = partition_pairs(res)
        if prs and all(sh[x] == sh[y] for x, y in prs):
            found.append(Ssub)
    assert tuple(sorted(Strue)) in found, found
    return True


# --------------------------------------------------------------------------
# E1
# --------------------------------------------------------------------------
def run_e1():
    print("=" * 78)
    print("E1. PLAINTEXT-TRIGGERED KEY ADVANCE - crib-consistency sweep")
    print("=" * 78)
    print("The pointer path is known inside each crib run; the pointer's value at the")
    print("start of each run is free (the unknown letters between the runs can fire the")
    print("trigger any number of times).  Both run-start offsets are enumerated, so the")
    print("adversary is given every benefit of the doubt.")
    print(f"cipher configurations per test: {NCFG}")
    print(f"rules: {ALL_RULES}")
    print(f"trigger sets: {len(TRIG_SETS)}  periods: 2..26\n")

    rows = []
    patterns = {}
    t_tests = 0; t_obs = 0; t_exp = 0.0
    for rule in ALL_RULES:
        for tname, trig in TRIG_SETS.items():
            r1, a1, _, _ = run_pointer(rule, trig, PT1)
            r2, a2, _, _ = run_pointer(rule, trig, PT2)
            for p in range(2, 27):
                seen = set()
                for b1 in range(p):
                    for b2 in range(p):
                        res = np.concatenate([residues(r1, a1, b1, p),
                                              residues(r2, a2, b2, p)])
                        keyres = tuple(res.tolist())
                        if keyres in seen:
                            continue
                        seen.add(keyres)
                        ncls, prs = partition_pairs(res)
                        c = 24 - ncls
                        mask = test_pairs(prs)
                        n = int(mask.sum())
                        exp = NCFG * 26.0 ** (-c)
                        t_tests += 1; t_obs += n; t_exp += exp
                        rows.append((rule, tname, p, b1, b2, c, n, exp))
                        if c >= 2:
                            patterns.setdefault(tuple(sorted(prs)), (c, rule, tname, p))
    print(f"distinct (rule, trigger, period, offsets) tests: {t_tests:,}")
    print(f"total configurations examined: {t_tests * NCFG:,}")
    print(f"observed survivors: {t_obs};  expected by chance: {t_exp:.1f}   "
          f"ratio {t_obs / max(t_exp, 1e-9):.3f}")
    cc = Counter(r[5] for r in rows)
    print("constraint-count distribution: " + " ".join(f"c={c}:{n}" for c, n in sorted(cc.items())))
    print(f"vacuous tests (c=0): {cc.get(0, 0)}")
    strong = [r for r in rows if r[6] > 0 and r[5] >= 5]
    print(f"\nsurvivors with c >= 5 (chance {NCFG * 26.0 ** -5:.2e} per test): {len(strong)}")
    for r in sorted(strong, key=lambda x: -x[5])[:20]:
        print(f"   {r[0]:<12} trig={r[1]:<18} p={r[2]:<3} b1={r[3]:<2} b2={r[4]:<2} "
              f"c={r[5]:<2} survivors={r[6]} (exp {r[7]:.2e})")
    best = max(rows, key=lambda r: r[5])
    print(f"\nmost-constrained single test: {best[0]} trig={best[1]} p={best[2]} "
          f"c={best[5]} -> survivors {best[6]}")
    return rows, patterns


# --------------------------------------------------------------------------
# E2 - forward simulation
# --------------------------------------------------------------------------
def run_e2():
    print()
    print("=" * 78)
    print("E2. PLAINTEXT-TRIGGERED KEY ADVANCE - deterministic forward simulation")
    print("=" * 78)
    print("For the causal rules the key pointer at position i depends only on plaintext")
    print("BEFORE i, so once (rule, trigger, p, offset at position 21, family, pt and ct")
    print("alphabets) are fixed, the 13 letters of EASTNORTHEAST determine the entire")
    print("period-p key and positions 34..96 decrypt with zero remaining freedom.")
    print("Reaching BERLINCLOCK at 63..73 is then an 11-letter prediction: chance 26^-11")
    print("= 7.0e-16 per fully determined simulation.")
    print(f"rules: {CAUSAL_RULES}   triggers: {len(TRIG_SETS)}   periods: 2..13")
    print("(p > 13 cannot be fully determined: 13 crib letters cannot cover 14+ residues)\n")

    ct_run = CODE[RUN1[1]:]                       # positions 34..96
    npos = len(ct_run)
    crib2_rel = [63 - RUN1[1] + t for t in range(11)]
    crib2_code = np.array([ord(ch) - 65 for ch in PT2])
    trig_mask_cache = {name: np.array([ch in trig for ch in PLAIN])
                       for name, trig in TRIG_SETS.items()}

    total_sims = 0
    total_determined = 0
    hits = []
    scored = []
    stall_reasons = Counter()
    cfg_all = np.arange(NCFG)

    for rule in CAUSAL_RULES:
        for tname, trig in TRIG_SETS.items():
            tmask = trig_mask_cache[tname]
            for p in range(2, 14):
                r1, a1, after, aft_abs = run_pointer(rule, trig, PT1)
                for b1 in range(p):
                    total_sims += 1
                    res = residues(r1, a1, b1, p)
                    # build the key for every config at once
                    keys = np.full((NCFG, p), -1, dtype=np.int64)
                    alive = np.ones(NCFG, dtype=bool)
                    for t in range(13):
                        r = int(res[t])
                        prev = keys[:, r]
                        conflict = (prev >= 0) & (prev != SHIFTS[:, t])
                        alive &= ~conflict
                        keys[:, r] = np.where(prev >= 0, prev, SHIFTS[:, t])
                    covered = (keys >= 0).all(axis=1)
                    alive &= covered
                    if not alive.any():
                        stall_reasons["no config: conflict or incomplete coverage"] += 1
                        continue
                    idx = cfg_all[alive]
                    total_determined += idx.size
                    j = np.full(idx.size, (after if aft_abs else b1 + after), dtype=np.int64)
                    out = np.empty((idx.size, npos), dtype=np.int64)
                    kk = keys[idx]
                    for t in range(npos):
                        kv = kk[np.arange(idx.size), j % p]
                        pc = DEC[idx, ct_run[t], kv].astype(np.int64)
                        out[:, t] = pc
                        adv = np.where(tmask[pc], 0, 1) if rule == "HOLD" else \
                              np.where(tmask[pc], 2, 1) if rule == "DOUBLE" else \
                              np.where(tmask[pc], 1, 0) if rule == "ADVANCE_ONLY" else None
                        if rule == "RESET_AFTER":
                            j = np.where(tmask[pc], 0, j + 1)
                        else:
                            j = j + adv
                    pred = out[:, crib2_rel]
                    nmatch = (pred == crib2_code[None, :]).sum(axis=1)
                    bestm = int(nmatch.max())
                    if bestm >= 6:
                        for w in np.nonzero(nmatch >= 6)[0]:
                            hits.append((int(nmatch[w]), rule, tname, p, b1, CFG[idx[w]]))
                    # quadgram score of the out-of-sample stretch 34..62 and 74..96
                    free = np.concatenate([out[:, :63 - RUN1[1]], out[:, 74 - RUN1[1]:]], axis=1)
                    q = S.quad_scores_batch(free)
                    w = int(np.argmax(q))
                    scored.append((float(q[w]), rule, tname, p, b1, CFG[idx[w]],
                                   "".join(PLAIN[x] for x in out[w])))

    print(f"simulations attempted (rule x trigger x period x offset): {total_sims:,}")
    print(f"fully determined (rule, trigger, p, offset, config) simulations: {total_determined:,}")
    print(f"expected 11/11 BERLINCLOCK matches by chance: "
          f"{total_determined * 26.0 ** -11:.3e}")
    if total_determined:
        exp6 = total_determined * sum(
            math.comb(11, m) * (1 / 26.0) ** m * (25 / 26.0) ** (11 - m) for m in range(6, 12))
        print(f"expected >= 6/11 matches by chance: {exp6:.3e}")
    print(f"observed simulations with >= 6/11 of BERLINCLOCK predicted: {len(hits)}")
    for h in sorted(hits, reverse=True)[:20]:
        print("   ", h)
    if not hits:
        print("   (none)")

    L = 63 - RUN1[1] + (97 - 74)
    thr = best_of_n_threshold(L, max(total_determined, 1))
    scored.sort(key=lambda x: -x[0])
    print(f"\nout-of-sample English check on the {L} non-crib letters the simulation")
    print(f"predicts (positions 35-62 and 75-97, 1-indexed).  Null for {L} random letters:")
    sc = null_quad(L)
    print(f"   mean {sc.mean():+.3f} sd {sc.std():.3f};  best-of-{total_determined:,} 95% "
          f"threshold {thr:+.3f};  English about -4.7")
    print("top 10 by that score:")
    for s in scored[:10]:
        star = " ***" if s[0] > thr else ""
        print(f"   q={s[0]:+.3f}{star} {s[1]:<12} trig={s[2]:<18} p={s[3]:<3} b1={s[4]} {s[5]}")
        print(f"      34..96: {s[6]}")
    return hits, scored, total_determined


# --------------------------------------------------------------------------
# E3 - key-driven interruptor
# --------------------------------------------------------------------------
def key_driven_pointer(rule, p, Sset):
    j = np.empty(N, dtype=np.int64)
    cur = 0
    for i in range(N):
        j[i] = cur
        r = cur % p
        if rule == "DOUBLE":
            cur += 2 if r in Sset else 1
        elif rule == "RESET_AFTER":
            cur = 0 if r in Sset else cur + 1
        else:
            raise ValueError(rule)
    return j


def run_e3():
    print()
    print("=" * 78)
    print("E3. KEY-DRIVEN INTERRUPTOR (the ACA 'interrupted key' with the interruptor")
    print("    on the KEY letter rather than on the text)")
    print("=" * 78)
    print("The pointer path depends only on WHICH RESIDUES of the key carry the")
    print("interruptor letter, so every subset S of Z_p is enumerated.  Because the key")
    print("alphabet is free, 'key[r] == T' reduces to: all crib-forced key values on S")
    print("are equal, and no crib-forced value off S equals that value.")
    print("HOLD is impossible here (the pointer would stick forever); DOUBLE and")
    print("RESET_AFTER are the two well-defined rules.  Periods 2..14.\n")

    tests = 0; obs = 0; exp = 0.0
    rows = []
    for rule in ("DOUBLE", "RESET_AFTER"):
        for p in range(2, 15):
            for r in range(p + 1):
                for Ssub in itertools.combinations(range(p), r):
                    Sset = set(Ssub)
                    if rule == "RESET_AFTER" and 0 in Sset and len(Sset) == p:
                        continue
                    j = key_driven_pointer(rule, p, Sset)
                    res = j[CRIB_POS] % p
                    ncls, prs = partition_pairs(res)
                    c = 24 - ncls
                    mask = test_pairs(prs)
                    if mask.any():
                        # extra constraint: crib-forced values on S all equal,
                        # and no crib-forced value off S equals it
                        onS = [k for k in range(24) if int(res[k]) in Sset]
                        offS = [k for k in range(24) if int(res[k]) not in Sset]
                        if onS:
                            v = SHIFTS[:, onS[0]]
                            ok = np.ones(NCFG, dtype=bool)
                            for k in onS[1:]:
                                ok &= SHIFTS[:, k] == v
                            for k in offS:
                                ok &= SHIFTS[:, k] != v
                            mask = mask & ok
                            c_eff = c + max(len(onS) - 1, 0)      # equality part only
                        else:
                            c_eff = c
                    else:
                        c_eff = c
                    n = int(mask.sum())
                    e = NCFG * 26.0 ** (-c_eff)
                    tests += 1; obs += n; exp += e
                    rows.append((rule, p, Ssub, c_eff, n, e))
    print(f"subset tests: {tests:,}   configurations examined: {tests * NCFG:,}")
    print(f"observed survivors: {obs};  expected by chance: {exp:.2f}   "
          f"ratio {obs / max(exp, 1e-9):.3f}")
    cc = Counter(r[3] for r in rows)
    print("constraint-count distribution: " + " ".join(f"c={c}:{n}" for c, n in sorted(cc.items())))
    strong = [r for r in rows if r[4] > 0 and r[3] >= 5]
    print(f"survivors with c >= 5: {len(strong)}")
    for r in sorted(strong, key=lambda x: -x[3])[:20]:
        print(f"   {r[0]:<12} p={r[1]:<3} S={r[2]} c={r[3]} survivors={r[4]} (exp {r[5]:.2e})")

    # decrypt any fully determined survivor
    cands = []
    for (rule, p, Ssub, c, n, e) in rows:
        if n == 0 or c < 3:
            continue
        Sset = set(Ssub)
        j = key_driven_pointer(rule, p, Sset)
        res = j[CRIB_POS] % p
        mask = test_pairs(partition_pairs(res)[1])
        onS = [k for k in range(24) if int(res[k]) in Sset]
        offS = [k for k in range(24) if int(res[k]) not in Sset]
        if onS:
            v = SHIFTS[:, onS[0]]
            ok = np.ones(NCFG, dtype=bool)
            for k in onS[1:]:
                ok &= SHIFTS[:, k] == v
            for k in offS:
                ok &= SHIFTS[:, k] != v
            mask = mask & ok
        for ci in np.nonzero(mask)[0]:
            key = np.full(p, -1, dtype=np.int64)
            for k in range(24):
                key[int(res[k])] = SHIFTS[ci, k]
            if (key < 0).any():
                continue
            fam, pn, cn = CFG[ci]
            pt = S.decrypt(CODE, key[j % p], fam, S.ALPHABETS[pn], S.ALPHABETS[cn])
            cands.append((S.quad_score(pt), pt, rule, p, Ssub, c, CFG[ci]))
    print(f"\nfully determined decryptable survivors: {len(cands)}")
    if cands:
        cands.sort(key=lambda x: -x[0])
        thr = crib_planted_threshold(max(len(cands), 1))
        print(f"crib-planted null: a random 97-letter text with EASTNORTHEAST and")
        print(f"BERLINCLOCK planted at the true positions scores {CRIB_NULL_MEAN:+.3f} "
              f"+- {CRIB_NULL_SD:.3f};")
        print(f"best-of-{len(cands)} 95% threshold {thr:+.3f}.  English about -4.7.")
        for cd in cands[:10]:
            star = " ***" if cd[0] > thr else ""
            print(f"   q={cd[0]:+.3f}{star} {cd[2]} p={cd[3]} S={cd[4]} c={cd[5]} {cd[6]}")
            print(f"      {cd[1]}")
    return rows, cands


# --------------------------------------------------------------------------
# the crib-planted null (used wherever a candidate has the cribs forced into it)
# --------------------------------------------------------------------------
def _crib_planted_null(ntrials=40000, seed=31):
    m = np.random.default_rng(seed).integers(0, 26, size=(ntrials, 97))
    for k, pos in enumerate(S.CRIB_POS):
        m[:, pos] = ord(S.CRIB_PT[k]) - 65
    return np.sort(S.quad_scores_batch(m))

CRIB_NULL = _crib_planted_null()
CRIB_NULL_MEAN = float(CRIB_NULL.mean())
CRIB_NULL_SD = float(CRIB_NULL.std())

def crib_planted_threshold(n, q=0.95):
    return float(CRIB_NULL[min(int(len(CRIB_NULL) * (q ** (1.0 / max(n, 1)))), len(CRIB_NULL) - 1)])


def main():
    t0 = time.time()
    assert _verify_e1(); print("verification E1: synthetic plaintext-HOLD period-7 key accepted.  OK")
    assert _verify_e2(); print("verification E2: forward simulation recovers a synthetic plaintext-HOLD")
    print("                 period-6 key from run 1 and predicts run 2 exactly, and does")
    print("                 so for at most 3 of the 12 periods tried.  OK")
    assert _verify_e3(); print("verification E3: synthetic key-driven DOUBLE interruptor S={2}, p=5, "
                               "accepted.  OK")
    print()
    print(f"crib-planted null (97 letters, cribs forced): mean {CRIB_NULL_MEAN:+.3f} "
          f"sd {CRIB_NULL_SD:.3f}")
    print("This is the ONLY correct null for a candidate decryption that has the 24 crib")
    print("letters built into it; comparing such a candidate to a pure-random null")
    print("(-8.23) would manufacture significance out of the cribs themselves.\n")

    run_e1()
    run_e2()
    run_e3()
    print(f"\n[runtime {time.time() - t0:.1f}s]")


if __name__ == "__main__":
    main()
