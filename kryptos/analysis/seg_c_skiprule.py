"""(c) Key streams whose ADVANCE is driven by a trigger in the ciphertext.

This is the "Liber Primus skip rule" family and its relatives.  A periodic key of
length p is consumed by a pointer j that does not simply increment:

  HOLD          j does not advance when the trigger fires   (the classic skip rule)
  DOUBLE        j advances by two when the trigger fires
  RESET_AFTER   j restarts at 0 after the trigger
  RESET_AT      j restarts at 0 on the trigger
  ADVANCE_ONLY  j advances ONLY on the trigger (key letter held between triggers -
                i.e. "the key changes at a structural boundary")

Triggers: every letter A-Z of the ciphertext, the doubled letters (19 BB, 26 QQ,
33 SS, 43 SS, 47 ZZ, 68 TT), the two X's, the panel-row boundaries, and each of
those delayed by one position.  Periods 2..26.  Cipher configurations: 3 families
x 17 plaintext alphabets x 17 ciphertext alphabets = 867 (the KEY alphabet is
irrelevant to a consistency test: it only relabels key values bijectively).

A configuration "survives" if every pair of crib positions that share a key-pointer
residue carries the same required key value.  Chance survival probability is
26^-c with c = 24 - (number of distinct residues used by the 24 crib positions),
and the expected number of chance survivors is printed beside every observed count.

Second pass: every surviving/constrained pattern is re-tested against 208k
keyword-mixed alphabets from /usr/share/dict/words on the free side.
"""
import json, os, sys, time
from collections import Counter, defaultdict

import numpy as np

import seg_common as S

CT = S.CT
N = 97
CODE = S.CT_CODE
PLAIN = S.PLAIN
CRIB_POS = np.array(S.CRIB_POS)

# ------------------------------------------------------------------ trigger sets
def letter_positions(ch):
    return {i for i in range(N) if CT[i] == ch}

DOUBLES_SECOND = {i for i in range(1, N) if CT[i] == CT[i - 1]}       # 19,26,33,43,47,68
DOUBLES_FIRST = {i - 1 for i in DOUBLES_SECOND}
ROW_BOUNDS = {4, 35, 66}
X_POS = letter_positions("X")

TRIGGERS = {}
for ch in PLAIN:
    TRIGGERS[f"letter {ch}"] = letter_positions(ch)
TRIGGERS["doubled-2nd"] = DOUBLES_SECOND
TRIGGERS["doubled-1st"] = DOUBLES_FIRST
TRIGGERS["the two X"] = X_POS
TRIGGERS["panel-row bounds"] = ROW_BOUNDS
TRIGGERS["vowels AEIOU"] = {i for i in range(N) if CT[i] in "AEIOU"}
TRIGGERS["KRYPTOS letters"] = {i for i in range(N) if CT[i] in "KRYPTOS"}

VARIANTS = ["HOLD", "DOUBLE", "RESET_AFTER", "RESET_AT", "ADVANCE_ONLY"]


def pointer_map(variant, trig, delay=0):
    """j[i] = key pointer used at position i (an int >= 0)."""
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
        else:
            raise ValueError(variant)
    return j


# ------------------------------------------------------------------ shift table
CFG = [(f, pn, cn) for f in S.FAMILIES for pn in S.ALPHABET_NAMES for cn in S.ALPHABET_NAMES]
SHIFTS = np.array([S.required_shifts(f, S.ALPHABETS[pn], S.ALPHABETS[cn]) for f, pn, cn in CFG])
assert SHIFTS.shape == (len(CFG), 24)


def partition_of(resid):
    """resid: length-24 array of key-pointer residues -> (classes, constraint pairs)."""
    groups = defaultdict(list)
    for k, r in enumerate(resid):
        groups[int(r)].append(k)
    pairs = []
    for g in groups.values():
        for x in g[1:]:
            pairs.append((g[0], x))
    return len(groups), pairs


def test_pairs(pairs):
    """Boolean mask over CFG of configurations satisfying all equality constraints."""
    if not pairs:
        return np.ones(len(CFG), dtype=bool)
    a = np.array([p[0] for p in pairs]); b = np.array([p[1] for p in pairs])
    return (SHIFTS[:, a] == SHIFTS[:, b]).all(axis=1)


# ------------------------------------------------------------------ dictionary pass
_DICT = None
def dict_alpha_idx():
    """(M, 26) matrix: for each keyword-mixed alphabet, idx[letter] -> position."""
    global _DICT
    if _DICT is not None:
        return _DICT
    seen = {}
    with open("/usr/share/dict/words") as f:
        for w in f:
            w = w.strip().upper()
            if len(w) < 3 or not w.isalpha() or not w.isascii():
                continue
            a = S.keyed_alphabet(w)
            if a not in seen:
                seen[a] = w
    alphas = list(seen)
    M = np.empty((len(alphas), 26), dtype=np.int8)
    for r, a in enumerate(alphas):
        for pos, ch in enumerate(a):
            M[r, ord(ch) - 65] = pos
    _DICT = (M, alphas, [seen[a] for a in alphas])
    return _DICT


def dict_survivors(pairs, fam, fixed_side, fixed_alpha):
    """Count alphabets on the free side making every constraint hold.
    fixed_side = 'pt' (search over ct alphabets) or 'ct' (search over pt alphabets)."""
    M, alphas, words = dict_alpha_idx()
    pt_c = S.CRIB_PT_CODE; ct_c = S.CRIB_CT_CODE
    fix = S.idx_map(fixed_alpha)
    idx = np.arange(M.shape[0])
    for (a, b) in pairs:
        if fixed_side == "pt":
            # need idxC(ct_a) - idxC(ct_b) == D  (vig/varbeau)  or  == -D (beaufort)
            dp = int(fix[pt_c[a]] - fix[pt_c[b]]) % 26
            want = dp if fam in ("vigenere", "varbeaufort") else (-dp) % 26
            got = (M[idx, ct_c[a]].astype(np.int16) - M[idx, ct_c[b]]) % 26
        else:
            dc = int(fix[ct_c[a]] - fix[ct_c[b]]) % 26
            want = dc if fam in ("vigenere", "varbeaufort") else (-dc) % 26
            got = (M[idx, pt_c[a]].astype(np.int16) - M[idx, pt_c[b]]) % 26
        idx = idx[got == want]
        if idx.size == 0:
            return 0, []
    return int(idx.size), [words[i] for i in idx[:5]]


def _verify():
    """Synthetic-key recovery: build a ciphertext with a known HOLD skip rule and
    check the machinery finds it."""
    rng = np.random.default_rng(3)
    pt = ("THEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGROUNDTOANUNKNOWN"
          "LOCATIONDOESLANGLEYKNOWABOUTTHISTHEYSHOULD")[:97]
    assert len(pt) == 97, len(pt)
    key = rng.integers(0, 26, 7)
    # encipher with HOLD on plaintext-independent trigger: use a fixed trigger position set
    trig = {5, 20, 44, 70}
    j = np.empty(N, dtype=np.int64); cur = 0
    for i in range(N):
        j[i] = cur
        cur += 0 if i in trig else 1
    ks = key[j % 7]
    ct = S.encrypt(S.codes(pt), ks, "vigenere", S.PLAIN, S.KEYED)
    # now recover: crib positions = the true ones, required shifts from the true pt
    pi = S.idx_map(S.PLAIN)[S.codes("".join(pt[i] for i in S.CRIB_POS))]
    ci = S.idx_map(S.KEYED)[S.codes("".join(ct[i] for i in S.CRIB_POS))]
    sh = (ci - pi) % 26
    resid = j[CRIB_POS] % 7
    ncls, pairs = partition_of(resid)
    ok = all(sh[a] == sh[b] for a, b in pairs)
    assert ok, "synthetic HOLD key not recovered"
    # and a wrong period must fail
    bad = 0
    for p in (5, 6, 8, 9):
        _, pr = partition_of(j[CRIB_POS] % p)
        if not all(sh[a] == sh[b] for a, b in pr):
            bad += 1
    assert bad >= 3, "test is not discriminating"
    return True


def main():
    t0 = time.time()
    assert _verify()
    print("verification: synthetic HOLD-skip key with period 7 is recovered by the same")
    print("machinery, and 3 of 4 wrong periods are rejected.  OK\n")

    print("=" * 78)
    print("(c) TRIGGER-DRIVEN KEY ADVANCE ('skip rule') - crib consistency sweep")
    print("=" * 78)
    print(f"cipher configurations per test: {len(CFG)} "
          f"(3 families x 17 pt alphabets x 17 ct alphabets)")
    print("doubled letters (1-indexed, 2nd of pair):",
          sorted(i + 1 for i in DOUBLES_SECOND))
    print("X positions (1-indexed):", sorted(i + 1 for i in X_POS))
    print()

    rows = []
    uniq_pairsets = {}
    total_tests = 0
    total_expected = 0.0
    total_observed = 0
    for variant in VARIANTS:
        for tname, trig in TRIGGERS.items():
            if not trig:
                continue
            for delay in (0, 1):
                j = pointer_map(variant, trig, delay)
                resid_full = j[CRIB_POS]
                for p in range(2, 27):
                    ncls, pairs = partition_of(resid_full % p)
                    c = 24 - ncls
                    mask = test_pairs(pairs)
                    nsurv = int(mask.sum())
                    exp = len(CFG) * (26.0 ** (-c))
                    total_tests += 1
                    total_expected += exp
                    total_observed += nsurv
                    rows.append((variant, tname, delay, p, c, nsurv, exp))
                    if c > 0:
                        key = tuple(sorted(pairs))
                        uniq_pairsets.setdefault(key, (c, variant, tname, delay, p))
    print(f"tests run: {total_tests} (variant x trigger x delay x period)")
    print(f"total configurations examined: {total_tests * len(CFG):,}")
    print(f"observed survivors: {total_observed};  expected by chance: {total_expected:.1f}")
    print()

    # ---- which tests were actually informative?
    by_c = Counter(r[4] for r in rows)
    print("distribution of constraint counts c (c=0 means the test is vacuous):")
    print("  " + "  ".join(f"c={c}:{n}" for c, n in sorted(by_c.items())))
    vac = sum(n for c, n in by_c.items() if c == 0)
    print(f"  vacuous tests (c=0): {vac} of {total_tests}")
    print()

    # ---- survivors with c >= 3 are the only ones worth printing
    interesting = [r for r in rows if r[5] > 0 and r[4] >= 3]
    print(f"survivors with c >= 3 (chance < {len(CFG)*26.0**-3:.3f} per test): {len(interesting)}")
    for r in sorted(interesting, key=lambda x: -x[4])[:40]:
        print(f"  {r[0]:<12} trig={r[1]:<16} delay={r[2]} p={r[3]:<3} c={r[4]:<3} "
              f"survivors={r[5]} (exp {r[6]:.2e})")

    print()
    print("best-constrained tests and their outcome:")
    for r in sorted(rows, key=lambda x: -x[4])[:15]:
        print(f"  {r[0]:<12} trig={r[1]:<16} delay={r[2]} p={r[3]:<3} c={r[4]:<3} "
              f"survivors={r[5]} (exp {r[6]:.2e})")

    # --------------------------------------------------- decrypt any survivor
    print()
    print("-" * 78)
    print("Decryptions of every survivor with c >= 2, scored against the chance level")
    print("-" * 78)
    cands = []
    for (variant, tname, delay, p, c, nsurv, exp) in rows:
        if nsurv == 0 or c < 2:
            continue
        j = pointer_map(variant, TRIGGERS[tname], delay)
        resid_full = j[CRIB_POS]
        ncls, pairs = partition_of(resid_full % p)
        mask = test_pairs(pairs)
        for ci in np.nonzero(mask)[0]:
            fam, pn, cn = CFG[ci]
            sh = SHIFTS[ci]
            key = np.full(p, -1, dtype=np.int64)
            for k, pos in enumerate(CRIB_POS):
                key[int(j[pos]) % p] = sh[k]
            if (key < 0).any():
                continue                      # key not fully determined -> not decryptable
            ks = key[j % p]
            pt = S.decrypt(CODE, ks, fam, S.ALPHABETS[pn], S.ALPHABETS[cn])
            cands.append((S.quad_score(pt), pt, variant, tname, delay, p, c, fam, pn, cn,
                          "".join(PLAIN[x] for x in key)))
    print(f"fully-determined decryptable survivors: {len(cands)}")
    if cands:
        cands.sort(key=lambda x: -x[0])
        mu = -8.23
        print(f"(uniform-random 97-letter quadgram score is {mu}; English about -4.7)")
        for c in cands[:15]:
            print(f"  q={c[0]:+.3f} {c[2]:<12} trig={c[3]:<16} d={c[4]} p={c[5]:<3} c={c[6]:<2} "
                  f"{c[7]}/pt={c[8]}/ct={c[9]} key={c[10]}")
            print(f"     {c[1]}")

    # --------------------------------------------------- dictionary alphabets
    print()
    print("-" * 78)
    print("Second pass: 208k dictionary keyword-mixed alphabets on the free side")
    print("-" * 78)
    M, alphas, words = dict_alpha_idx()
    print(f"distinct keyword-mixed alphabets from /usr/share/dict/words: {len(alphas):,}")
    todo = sorted(uniq_pairsets.items(), key=lambda kv: -kv[1][0])
    print(f"distinct non-vacuous constraint patterns: {len(todo)}")
    # only patterns with c >= 2 are worth a dictionary search (c=1 gives ~8000 chance hits)
    todo = [t for t in todo if t[1][0] >= 2]
    print(f"patterns with c >= 2 tested against the dictionary: {len(todo)}")
    grand = 0; grand_exp = 0.0; hits = []
    for pairs, (c, variant, tname, delay, p) in todo:
        for fam in S.FAMILIES:
            for side, names in (("pt", S.ALPHABET_NAMES), ("ct", S.ALPHABET_NAMES)):
                for nm in names:
                    n, ex = dict_survivors(list(pairs), fam, side, S.ALPHABETS[nm])
                    grand += n
                    grand_exp += len(alphas) * 26.0 ** (-c)
                    if n:
                        hits.append((c, variant, tname, delay, p, fam, side, nm, n, ex))
    print(f"comparisons: {len(todo) * 3 * 2 * 17 * len(alphas):,}")
    print(f"observed survivors: {grand};  expected by chance: {grand_exp:.1f}")
    if hits:
        hits.sort(key=lambda h: -h[0])
        print("top hits (by constraint count c):")
        for h in hits[:25]:
            print(f"  c={h[0]:<2} {h[1]:<12} trig={h[2]:<16} d={h[3]} p={h[4]:<3} {h[5]} "
                  f"{h[6]}-fixed={h[7]} -> {h[8]} alphabets, e.g. {h[9]}")
    print(f"\n[runtime {time.time()-t0:.1f}s]")


if __name__ == "__main__":
    main()
