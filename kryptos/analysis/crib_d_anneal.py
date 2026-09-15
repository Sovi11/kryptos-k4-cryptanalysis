"""Task (d): forget the cribs entirely -- can ANY key stream inside a given
structural family make K4 read like English, if we allow Sanborn-style
deliberate misspellings?

Method: hill-climb (steepest ascent, random restarts) over the key of each
structural family, scoring the 97-letter decryption with a quadgram model in
two variants:

  q      -- mean log10 quadgram probability over all 94 quadgrams
  q_tol2 -- the same after discarding the 8 worst quadgrams.  A single wrong
            letter damages at most 4 quadgrams, so discarding 8 makes the score
            blind to up to TWO deliberate misspellings (IQLUSION / UNDERGRUUND
            / DESPARATLY style).  The hill-climb maximises q_tol2.

The number that matters is not the best score but the best score RELATIVE TO A
NULL: the same search run on texts that are certainly not English-under-a-
period-p-key (shuffles of K4, and uniform random text).  A period-p key has p
free letters controlling 97 plaintext letters, so for large p the optimiser can
manufacture a lot of fake English; only the null tells you how much.

Run:  python3.12 crib_d_anneal.py > ../findings/crib_d_out.txt
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crib_lib as L
import twocipher_common as TC

# --------------------------------------------------------------------------
# quadgram array
# --------------------------------------------------------------------------
TC._build_quadgram_model()
QARR = np.full(26 ** 4, TC._QUAD_FLOOR, dtype=np.float32)
for _g, _v in TC._QUAD.items():
    _i = 0
    for _ch in _g:
        _i = _i * 26 + (ord(_ch) - 65)
    QARR[_i] = _v
NDROP = 8          # 2 misspellings x 4 damaged quadgrams


def quad_vals(P):
    """P : (n, m) int -> (n, m-3) float32 quadgram log10 probabilities."""
    m = P.shape[1]
    idx = (P[:, 0:m - 3] * 17576 + P[:, 1:m - 2] * 676
           + P[:, 2:m - 1] * 26 + P[:, 3:m])
    return QARR[idx]


def score_pair(P, ndrop=NDROP):
    v = quad_vals(P)
    q = v.mean(axis=1)
    if ndrop <= 0:
        return q, q
    part = np.partition(v, ndrop, axis=1)
    return q, part[:, ndrop:].mean(axis=1)


def q_of(text, ndrop=NDROP):
    P = np.frombuffer(text.encode(), dtype=np.uint8).astype(np.int64)[None, :] - 65
    a, b = score_pair(P, ndrop)
    return float(a[0]), float(b[0])


# --------------------------------------------------------------------------
# families: T[k, ctcode] = plaintext code
# --------------------------------------------------------------------------
def family_table(rule, pta, cta):
    A, B = L.ALPHABETS[pta], L.ALPHABETS[cta]
    Bidx = np.array([B.index(ch) for ch in L.A2Z])
    T = np.zeros((26, 26), dtype=np.int64)
    for k in range(26):
        for c in range(26):
            if rule == "vigenere":
                pi = (Bidx[c] - k) % 26
            elif rule == "beaufort":
                pi = (k - Bidx[c]) % 26
            else:
                pi = (Bidx[c] + k) % 26
            T[k, c] = ord(A[pi]) - 65
    return T


FAMILIES = [("vigenere", "plain", "plain"),
            ("beaufort", "plain", "plain"),
            ("vigenere", "plain", "kryptos"),
            ("vigenere", "kryptos", "kryptos")]


# --------------------------------------------------------------------------
# hill climb
# --------------------------------------------------------------------------
def climb(ctcode, period, T, rng, restarts, obj=1):
    """obj: 0 = maximise q, 1 = maximise q_tol2.  Returns (best_obj, best_q,
    best_qtol, best_key, best_plaintext_codes)."""
    n = len(ctcode)
    resmap = np.arange(n) % period
    cols = [np.nonzero(resmap == r)[0] for r in range(period)]
    Tsub = [T[:, ctcode[c]] for c in cols]     # (26, len(cols[r]))
    best = (-1e9, None, None, None, None)
    for _ in range(restarts):
        key = rng.integers(0, 26, period)
        P = T[key[resmap], ctcode][None, :]
        cur = score_pair(P)[obj][0]
        improved = True
        while improved:
            improved = False
            for r in range(period):
                cand = np.repeat(P, 26, axis=0)
                cand[:, cols[r]] = Tsub[r]
                s = score_pair(cand)[obj]
                j = int(np.argmax(s))
                if s[j] > cur + 1e-9:
                    P = cand[j:j + 1].copy()
                    key[r] = j
                    cur = float(s[j])
                    improved = True
        if cur > best[0]:
            a, b = score_pair(P)
            best = (cur, float(a[0]), float(b[0]), key.copy(), P[0].copy())
    return best


def as_text(codes):
    return "".join(L.A2Z[int(c)] for c in codes)


# --------------------------------------------------------------------------
HELDOUT = """
The committee met on a Thursday afternoon in a room that smelled of old paper and
floor polish. Nobody wanted to speak first. A clerk read the minutes of the last
meeting in a flat voice while the rain went on falling against the tall windows,
and outside in the square a bus pulled away from the kerb and left a long wet
stripe on the road behind it. When the reading was finished the chairman took off
his glasses and said that they had better begin, since the afternoon would not
last forever and there were three matters on the agenda that could not wait
another month. The first concerned the roof. The second concerned money. The third
nobody was willing to name aloud, although everyone in the room had thought about
it every day for a fortnight, and it was the only reason any of them had come.
A young woman at the end of the table opened her notebook, wrote the date at the
top of a clean page, and waited. Somewhere below them a door banged shut and the
sound travelled up through the floor like a question nobody had asked.
"""


def english_samples(n=40, seed=3):
    import re
    txt = re.sub("[^A-Z]", "", HELDOUT.upper())
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, len(txt) - 97, n)
    return [txt[s:s + 97] for s in starts]


def corrupt(s, k, rng):
    s = list(s)
    for i in rng.choice(len(s), k, replace=False):
        s[i] = L.A2Z[int(rng.integers(0, 26))]
    return "".join(s)


# --------------------------------------------------------------------------
def part1_calibration():
    print("=" * 78)
    print("TASK (d)  PART 1: what a misspelling-tolerant score actually tolerates")
    print("=" * 78)
    print("q_tolD = mean quadgram log10 probability after discarding the D worst")
    print("quadgrams.  One wrong letter damages at most 4 quadgrams, so D=8")
    print("absorbs two deliberate misspellings and D=16 absorbs four.")
    rng = np.random.default_rng(11)
    samples = english_samples(40)
    drops = (0, 8, 16)
    print("\n  %-40s %10s %10s %10s" % ("97-letter text", "q", "q_tol8", "q_tol16"))
    for k in (0, 1, 2, 3, 5, 10):
        acc = {d: [] for d in drops}
        for s in samples:
            for _ in range(5):
                t = corrupt(s, k, rng) if k else s
                for d in drops:
                    acc[d].append(q_of(t, d)[1])
        print("  %-40s %10.3f %10.3f %10.3f"
              % ("English, %d random letters corrupted" % k,
                 np.mean(acc[0]), np.mean(acc[8]), np.mean(acc[16])))
    for name, gen in (("uniform random", lambda: "".join(
                          L.A2Z[i] for i in rng.integers(0, 26, 97))),
                      ("shuffle of K4 (same letter multiset)", lambda: "".join(
                          rng.permutation(list(L.CT)))),
                      ("K4 ciphertext itself", lambda: L.CT)):
        acc = {d: [] for d in drops}
        for _ in range(200 if name != "K4 ciphertext itself" else 1):
            t = gen()
            for d in drops:
                acc[d].append(q_of(t, d)[1])
        print("  %-40s %10.3f %10.3f %10.3f"
              % (name, np.mean(acc[0]), np.mean(acc[8]), np.mean(acc[16])))
    print()
    print("  Sanborn's own deliberately misspelled plaintexts vs. corrected:")
    for name, s in (("K1 as carved (IQLUSION)",
                     "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"),
                    ("K1 corrected (ILLUSION)",
                     "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFILLUSION"),
                    ("K2 window as carved (UNDERGRUUND)",
                     "THEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONX"),
                    ("K2 window corrected (UNDERGROUND)",
                     "THEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGROUNDTOANUNKNOWNLOCATIONX"),
                    ("K3 as carved (DESPARATLY)",
                     "SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVED"),
                    ("K3 corrected (DESPERATELY)",
                     "SLOWLYDESPERATELYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOV")):
        print("    %-36s (%2d letters) q=%.3f  q_tol8=%.3f"
              % (name, len(s), q_of(s, 0)[1], q_of(s, 8)[1]))
    print()
    print("  Reading: the English-to-random gap is about 3.5 on every variant of")
    print("  the score, while Sanborn's actual deliberate misspellings cost 0.05")
    print("  to 0.15 and two random corruptions cost about 0.17.  Tolerating")
    print("  misspellings therefore cannot rescue a search that is otherwise 3.5")
    print("  away from English: 'the plaintext is a misspelled riddle' is not an")
    print("  explanation for failing to find it.")


def part2_validate(rng):
    print()
    print("=" * 78)
    print("TASK (d)  PART 2: validation -- the climber recovers planted keys exactly")
    print("=" * 78)
    T = family_table(*FAMILIES[0])
    samples = english_samples(6, seed=9)
    print("  %-8s %-12s %-12s %-9s %s" % ("period", "planted qtol", "found qtol",
                                          "exact?", "recovered text (first 58)"))
    allok = True
    for period in (3, 5, 9, 12, 14):
        s = samples[period % len(samples)]
        key = rng.integers(0, 26, period)
        ct = L.encrypt(s, key.tolist(), *FAMILIES[0])
        ctc = np.frombuffer(ct.encode(), dtype=np.uint8).astype(np.int64) - 65
        obj, q, qt, fkey, P = climb(ctc, period, T, rng, restarts=40)
        txt = as_text(P)
        ok = txt == s
        allok &= ok
        print("  %-8d %-12.3f %-12.3f %-9s %s" %
              (period, q_of(s)[1], obj, "YES" if ok else "no", txt[:58]))
    print("  validation: %s" % ("exact recovery at every period 3-14"
                                if allok else "NOT exact at some period"))
    return allok


def part3_sweep(rng, periods, families, n_null, n_pos, restarts, with_pos=True,
                shared_nulls=None, shared_pos=None):
    """Three-arm design at each period, all three arms given the SAME search
    budget:
        POS  -- held-out English encrypted with a random period-p key of this
                family (the search should find it, if the search has power)
        K4   -- the real ciphertext
        NULL -- shuffles of K4 and uniform random text (no English underneath)
    The comparison that matters is where K4 falls between NULL and POS."""
    ctc = np.frombuffer(L.CT.encode(), dtype=np.uint8).astype(np.int64) - 65
    nulls = shared_nulls
    if nulls is None:
        nulls = []
        for _ in range(n_null // 2):
            nulls.append(np.array([ord(c) - 65 for c in rng.permutation(list(L.CT))]))
        for _ in range(n_null - n_null // 2):
            nulls.append(rng.integers(0, 26, 97))
    pos_texts = shared_pos if shared_pos is not None else english_samples(n_pos, seed=21)

    for fam in families:
        T = family_table(*fam)
        print("\n  family %s   (%d restarts per climb, %d nulls, %d positives)"
              % (L.combo_name(fam), restarts, len(nulls), len(pos_texts)))
        print("  %-4s | %-17s | %-8s | %-25s | %-7s | %s"
              % ("p", "POS English mean", "K4", "NULL mean / sd / max",
                 "z(K4)", "best K4 decryption"))
        for p in periods:
            k4 = climb(ctc, p, T, rng, restarts)
            nv = np.array([climb(nc, p, T, rng, restarts)[0] for nc in nulls])
            if with_pos:
                pv = []
                for s in pos_texts:
                    key = rng.integers(0, 26, p)
                    ct = L.encrypt(s, key.tolist(), *fam)
                    cc = np.frombuffer(ct.encode(), dtype=np.uint8).astype(np.int64) - 65
                    pv.append(climb(cc, p, T, rng, restarts)[0])
                pv = np.array(pv)
                posdesc = "%.3f" % pv.mean()
                sep = (pv.mean() - nv.mean()) / (nv.std() + 1e-9)
            else:
                posdesc = "   --"
                sep = float("nan")
            z = (k4[0] - nv.mean()) / (nv.std() + 1e-9)
            print("  %-4d | %8s (sep %5.1f) | %8.3f | %7.3f / %5.3f / %7.3f | %7.2f | %s"
                  % (p, posdesc, sep, k4[0], nv.mean(), nv.std(), nv.max(), z,
                     as_text(k4[4])))
            sys.stdout.flush()


def part4_progressive(rng):
    print()
    print("=" * 78)
    print("TASK (d)  PART 4: exhaustive over the progressive-key family")
    print("                  key_i = a + b*i  (Trithemius / progressive)")
    print("=" * 78)
    ctc = np.frombuffer(L.CT.encode(), dtype=np.uint8).astype(np.int64) - 65
    i = np.arange(97)
    for fam in FAMILIES:
        T = family_table(*fam)
        best = (-1e9,)
        allq = []
        for a in range(26):
            for b in range(26):
                key = (a + b * i) % 26
                P = T[key, ctc][None, :]
                q, qt = score_pair(P)
                allq.append(float(qt[0]))
                if qt[0] > best[0]:
                    best = (float(qt[0]), float(q[0]), a, b, as_text(P[0]))
        allq = np.array(allq)
        print("  %-30s best q_tol2 %.3f (a=%d b=%d, q=%.3f); 676 keys: "
              "mean %.3f sd %.3f" % (L.combo_name(fam), best[0], best[2],
                                     best[3], best[1], allq.mean(), allq.std()))
        print("      %s" % best[4])
    # null for the same family size
    nulls = []
    T = family_table(*FAMILIES[0])
    for _ in range(200):
        nc = rng.integers(0, 26, 97)
        bb = -1e9
        for a in range(26):
            for b in range(26):
                P = T[(a + b * i) % 26, nc][None, :]
                bb = max(bb, float(score_pair(P)[1][0]))
        nulls.append(bb)
    nulls = np.array(nulls)
    print("  null (200 random 97-letter texts, same exhaustive 676-key search): "
          "best q_tol2 mean %.3f sd %.3f max %.3f"
          % (nulls.mean(), nulls.std(), nulls.max()))


def main():
    rng = np.random.default_rng(2024)
    part1_calibration()
    part2_validate(rng)
    part4_progressive(rng)
    print()
    print("=" * 78)
    print("TASK (d)  PART 3: best achievable q_tol8 under a period-p key")
    print("=" * 78)
    print("Three arms, identical search budget.  POS = held-out English encrypted")
    print("with a random period-p key of the same family (a positive control that")
    print("measures the SEARCH POWER at that period); NULL = K4 shuffles and")
    print("uniform random text; 'sep' = how many null sd's the positive control")
    print("sits above the null, i.e. how much power the test has at that period.")
    print("z(K4) = how many null sd's K4 sits above the null.")
    periods = list(range(2, 27))
    part3_sweep(rng, periods, FAMILIES[:1], n_null=10, n_pos=6, restarts=60)
    part3_sweep(rng, periods, FAMILIES[1:], n_null=10, n_pos=4, restarts=60)
    print()
    print("  long periods (family %s only; note the search power collapses here)"
          % L.combo_name(FAMILIES[0]))
    part3_sweep(rng, [28, 31, 34, 40, 48], FAMILIES[:1], n_null=8, n_pos=5,
                restarts=80)


if __name__ == "__main__":
    main()
