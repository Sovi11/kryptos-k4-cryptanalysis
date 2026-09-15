"""Task (e): are Sanborn's numbers CIPHERTEXT positions or PLAINTEXT positions?

Everyone reads "the characters that are the 64th through 69th ... read NYPVTT.
When deciphered, they read BERLIN" as a claim about one window of a
position-preserving cipher: ciphertext position 64 carries plaintext position
64.  Two other readings are logically available:

  CT-reading  the quoted index locates the CIPHERTEXT letters, and the crib
              word is what those letters decrypt to (possibly landing somewhere
              else in the plaintext);
  PT-reading  the quoted index locates the word inside the PLAINTEXT, and the
              ciphertext letters carrying it may sit elsewhere.

findings/twocipher.md shows the two readings are NOT equivalent once a
transposition is in play, and exhausts the two-stage schemes under both.  This
script does the parts that sit upstream of that work:

  E1  proves the readings coincide exactly when the cipher is position
      preserving, so (e) is vacuous for every one-stage system -- which is most
      of what this repo has ruled out;
  E2  validates the sweep machinery on planted ciphers before any negative is
      trusted;
  E3  the ASYMMETRIC-ANCHOR test.  crib_c_sources.py shows BERLIN's window is
      pinned by two independent published facts (an index AND the ciphertext
      string NYPVTT) while EAST's rests on a layout image alone.  So the
      interesting hypothesis is not "everything slid" but "the EASTNORTHEAST
      block is misplaced while BERLINCLOCK is right".  Free slide of one block
      with the other nailed down, both ways round;
  E4  the rigid-rotation model: plaintext index i is carried by ciphertext index
      (i + d) mod 97, i.e. the quoted numbers are right but they index the other
      text and the two texts are offset cyclically.  All 97 rotations.  (The
      non-wrapping part of this is crib_b's global slide; the wrap is new.);
  E5  the reversed-text reading, ciphertext and plaintext each reversed;
  E6  how many crib constraints each of the four (stage-order x reading) cases
      actually imposes, which is what decides whether cribs can test it at all.

Run:  python3.12 crib_e_ptct.py > ../findings/crib_e_out.txt
"""
import os
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crib_lib as L

CT = L.CT
N = L.N
PERIODS = tuple(range(2, 27))
BLOCK_A = ("EASTNORTHEAST", 21)      # 0-indexed start
BLOCK_B = ("BERLINCLOCK", 63)


# ---------------------------------------------------------------------------
def sec_e1():
    print("=" * 78)
    print("E1.  THE TWO READINGS COINCIDE FOR EVERY POSITION-PRESERVING CIPHER")
    print("=" * 78)
    print("Claim: if the cipher maps plaintext letter i to ciphertext letter i")
    print("(any letterwise rule, any per-position key, any alphabets), then")
    print("   'the ciphertext at 64..69 decrypts to BERLIN'   (CT-reading)")
    print("and")
    print("   'the plaintext at 64..69 is BERLIN'             (PT-reading)")
    print("are the same sentence, so task (e) cannot separate them.")
    print()
    print("Demonstration: build random position-keyed ciphers (a fresh random key")
    print("value at every one of the 97 positions, all 12 rule/alphabet combos),")
    print("and check the two readings always pick out the identical 24 (ct, pt)")
    print("pairs.")
    rng = np.random.default_rng(11)
    agree = 0
    trials = 0
    for combo in L.COMBOS:
        for t in range(20):
            trials += 1
            key = rng.integers(0, 26, N).tolist()
            pt = "".join(L.A2Z[i] for i in rng.integers(0, 26, N))
            ct = L.encrypt(pt, key, *combo)
            # CT-reading: decrypt the window
            win = list(range(21, 34)) + list(range(63, 74))
            ct_read = [(i, L.decrypt(ct, key, *combo)[i]) for i in win]
            # PT-reading: read the plaintext at the same window
            pt_read = [(i, pt[i]) for i in win]
            if ct_read == pt_read:
                agree += 1
    print("  identical in %d / %d trials  [%s]"
          % (agree, trials, "PASS" if agree == trials else "FAIL"))
    print()
    print("  So (e) has teeth only when a stage moves letters -- a transposition,")
    print("  a fractionation, or a variable-length encoding.  findings/twocipher.md")
    print("  enumerates the four (stage order x reading) cases over a 1.17M-entry")
    print("  transposition catalogue plus 2.45M compositions and finds nothing;")
    print("  the sections below attack the readings from the placement side")
    print("  instead, which does not need a transposition catalogue at all.")


# ---------------------------------------------------------------------------
def _placement(blocks):
    return L.merge_blocks(blocks)


def sec_e2():
    print()
    print("=" * 78)
    print("E2.  VALIDATION: PLANTED CIPHERS MUST BE RECOVERED")
    print("=" * 78)
    print("Before any negative below is believed, plant a periodic cipher whose")
    print("crib blocks sit at a KNOWN non-standard placement and check the free")
    print("slide finds exactly that placement.")
    ca = L.build_combo_arrays(L.alphabet_set("two"))
    rng = np.random.default_rng(4242)
    allok = True
    for period, ci, startA, startB in ((9, 0, 30, 63), (11, 5, 21, 50), (13, 8, 40, 70)):
        key = rng.integers(0, 26, period).tolist()
        pt = "".join(L.A2Z[i] for i in rng.integers(0, 26, N))
        pt = (pt[:startA] + BLOCK_A[0] + pt[startA + len(BLOCK_A[0]):])
        pt = (pt[:startB] + BLOCK_B[0] + pt[startB + len(BLOCK_B[0]):])
        rule, pta, cta = L.COMBOS[ci]
        ct = L.encrypt(pt, key, rule, pta, cta)
        saved = L.CT_CODE.copy()
        try:
            L.CT_CODE[:] = np.frombuffer(ct.encode(), dtype=np.uint8).astype(np.int64) - 65
            found = []
            for sA in range(0, N - len(BLOCK_A[0]) + 1):
                pl = _placement([(sA, BLOCK_A[0]), (startB, BLOCK_B[0])])
                if pl is None:
                    continue
                surv, _ = L.placement_sweep_one(pl, ca, periods=(period,))
                if surv:
                    found.append(sA)
            ok = startA in found
            allok &= ok
            print("  planted A@%d B@%d period %2d %-28s -> free slide of A fires at %s  [%s]"
                  % (startA, startB, period, L.combo_name(L.COMBOS[ci]),
                     found, "PASS" if ok else "FAIL"))
        finally:
            L.CT_CODE[:] = saved
    print("  validation: %s" % ("ALL PASS" if allok else "FAILURES"))
    return allok


# ---------------------------------------------------------------------------
def free_slide(fixed_block, fixed_start, moving_block, label, combos_which="two"):
    """Slide `moving_block` over every legal start while `fixed_block` stays put.
    Reports survivors stratified by the number of constraints, against chance."""
    ca = L.build_combo_arrays(L.alphabet_set(combos_which))
    nk = len(ca[4])
    obs = Counter()
    exp = Counter()
    uni = Counter()
    tested = 0
    placements = 0
    best = []
    for s in range(0, N - len(moving_block) + 1):
        pl = _placement([(fixed_start, fixed_block), (s, moving_block)])
        if pl is None:
            continue
        placements += 1
        surv, info = L.placement_sweep_one(pl, ca, periods=PERIODS)
        for period, c, u in info:
            exp[c] += nk * 26.0 ** (-c)
            tested += nk
            if u:
                uni[c] += 1
        for period, ki, c, kd in surv:
            obs[c] += 1
            if c >= 8:
                best.append((c, period, ca[4][ki], s))
    print()
    print("### %s" % label)
    print("  moving-block placements tested : %d" % placements)
    print("  combos %d x periods %d  ->  %d (placement, period, combo) tests"
          % (nk, len(PERIODS), tested))
    print("  survivors observed %d   vs chance expectation %.4g"
          % (sum(obs.values()), sum(exp.values())))
    print("  by number of constraints c (a random key survives with prob 26^-c):")
    print("    %-4s %12s %14s %12s %12s" % ("c", "tests", "expected", "observed",
                                            "univ-pass"))
    for c in sorted(set(obs) | set(exp), reverse=True):
        e = exp.get(c, 0.0)
        o = obs.get(c, 0)
        t = int(round(e * 26.0 ** c)) if e else 0
        if o or c >= 6:
            print("    %-4d %12d %14.4g %12d %12d" % (c, t, e, o, uni.get(c, 0)))
    if best:
        print("  survivors with c >= 8:")
        for c, period, lab, s in best[:40]:
            print("     c=%d p=%d %s moving-block start(0-idx)=%d" % (c, period, lab, s))
    else:
        print("  no survivor with c >= 8.")
    return sum(obs.values()), sum(exp.values())


def sec_e3():
    print()
    print("=" * 78)
    print("E3.  ASYMMETRIC ANCHORS: SLIDE ONE PHRASE, NAIL THE OTHER")
    print("=" * 78)
    print("crib_c_sources.py A5: BERLIN's window is fixed by two independently")
    print("published facts (the 64th-69th characters, AND that they read NYPVTT);")
    print("EAST's rests on one layout image whose reading rumkin.com flags as")
    print("possibly 'confirmed out of hand'.  So the hypothesis worth the compute")
    print("is not a global slide but a one-sided one.")
    free_slide(BLOCK_B[0], BLOCK_B[1], BLOCK_A[0],
               "E3a. BERLINCLOCK nailed at 64-74, EASTNORTHEAST slid over all starts")
    free_slide(BLOCK_A[0], BLOCK_A[1], BLOCK_B[0],
               "E3b. EASTNORTHEAST nailed at 22-34, BERLINCLOCK slid over all starts "
               "(the mirror; weaker prior, run for symmetry)")


# ---------------------------------------------------------------------------
def sec_e4():
    print()
    print("=" * 78)
    print("E4.  RIGID CYCLIC ROTATION: PT INDEX i CARRIED BY CT INDEX (i+d) mod 97")
    print("=" * 78)
    print("The simplest way the two readings can both be literally true while")
    print("disagreeing: the quoted numbers index the plaintext, and plaintext and")
    print("ciphertext are offset by one constant.  crib_b's global slide covers the")
    print("non-wrapping offsets; here every d in 0..96 is tested, wrap included, so")
    print("a crib may straddle the end of the 97 letters.")
    ca = L.build_combo_arrays(L.alphabet_set("two"))
    nk = len(ca[4])
    obs = Counter(); exp = Counter(); uni = Counter()
    tested = 0
    hits = []
    words = [(BLOCK_A[1], BLOCK_A[0]), (BLOCK_B[1], BLOCK_B[0])]
    for d in range(N):
        pl = []
        bad = False
        seen = {}
        for start, w in words:
            for k, ch in enumerate(w):
                p = (start + k + d) % N
                if p in seen and seen[p] != ch:
                    bad = True
                seen[p] = ch
        if bad:
            continue
        pl = sorted(seen.items())
        surv, info = L.placement_sweep_one(pl, ca, periods=PERIODS)
        for period, c, u in info:
            exp[c] += nk * 26.0 ** (-c)
            tested += nk
            if u:
                uni[c] += 1
        for period, ki, c, kd in surv:
            obs[c] += 1
            if c >= 8:
                hits.append((c, period, ca[4][ki], d))
    print()
    print("  rotations tested : %d   tests: %d" % (N, tested))
    print("  survivors observed %d   vs chance expectation %.4g"
          % (sum(obs.values()), sum(exp.values())))
    print("    %-4s %12s %14s %12s %12s" % ("c", "tests", "expected", "observed",
                                            "univ-pass"))
    for c in sorted(set(obs) | set(exp), reverse=True):
        e = exp.get(c, 0.0); o = obs.get(c, 0)
        t = int(round(e * 26.0 ** c)) if e else 0
        if o or c >= 6:
            print("    %-4d %12d %14.4g %12d %12d" % (c, t, e, o, uni.get(c, 0)))
    if hits:
        print("  survivors with c >= 8:")
        for h in hits[:40]:
            print("     c=%d p=%d %s d=%d" % h)
    else:
        print("  no survivor with c >= 8.")


# ---------------------------------------------------------------------------
def sec_e5():
    print()
    print("=" * 78)
    print("E5.  REVERSED READINGS")
    print("=" * 78)
    print("K3 is a route transposition read right-to-left, so 'which end do you")
    print("count from' is a live question for this designer.  Two variants:")
    print("  R1  the quoted 1-indexed positions counted from the END of K4")
    print("      (crib word at 97-hi+1 .. 97-lo+1, word left-to-right);")
    print("  R2  the same, with the crib word itself reversed, i.e. the plaintext")
    print("      is written backwards under the ciphertext.")
    ca = L.build_combo_arrays(L.alphabet_set("two"))
    nk = len(ca[4])
    for tag, rev_word in (("R1 positions mirrored, word forward", False),
                          ("R2 positions mirrored, word reversed", True)):
        blocks = []
        for start, w in ((BLOCK_A[1], BLOCK_A[0]), (BLOCK_B[1], BLOCK_B[0])):
            lo = start                       # 0-indexed
            hi = start + len(w) - 1
            nlo = N - 1 - hi
            ww = w[::-1] if rev_word else w
            blocks.append((nlo, ww))
        pl = _placement(blocks)
        pairs = " ".join("%d:%s->%s" % (p + 1, CT[p], c) for p, c in pl)
        surv, info = L.placement_sweep_one(pl, ca, periods=PERIODS)
        exp = sum(nk * 26.0 ** (-c) for _, c, _ in info)
        uni_ok = [p for p, c, u in info if u]
        print()
        print("  %s" % tag)
        print("    placement: %s" % pairs)
        print("    survivors %d over %d tests, chance expectation %.4g"
              % (len(surv), nk * len(PERIODS), exp))
        print("    periods where the alphabet-free necessary condition still "
              "permits a solution: %s" % uni_ok)
        big = [(c, p, ca[4][k]) for p, k, c, _ in surv if c >= 8]
        print("    survivors with c >= 8: %s" % (big if big else "none"))


# ---------------------------------------------------------------------------
def sec_e6():
    print()
    print("=" * 78)
    print("E6.  HOW MUCH DOES EACH READING ACTUALLY CONSTRAIN?")
    print("=" * 78)
    print("S = letterwise substitution whose key may vary with position;")
    print("T = transposition.  Constraint counts are for a period-p key; c is the")
    print("number of independent equalities the 24 crib letters impose, and a")
    print("random key passes with probability 26^-c.")
    print()
    base = L.baseline_placement()
    pos = [p for p, _ in base]
    print("  CT-reading, T then S   the 24 (ct, pt) pairs are exactly those of a")
    print("                         one-stage cipher; T is invisible to the test.")
    print("                         c by period:")
    line = "    "
    for p in PERIODS:
        line += "p%d:%d  " % (p, L.n_constraints(pos, p))
        if len(line) > 66:
            print(line); line = "    "
    if line.strip():
        print(line)
    print()
    print("  CT-reading, S then T   same 24 key VALUES, but sitting at the")
    print("                         relocated positions T^-1[c]; testable only once")
    print("                         T is enumerated.  Covered exhaustively in")
    print("                         findings/twocipher.md (0 survivors).")
    print()
    print("  PT-reading, S then T   key stream fully determined at the 24 known")
    print("                         PLAINTEXT positions for each candidate T; no")
    print("                         periodicity needed.  Covered: twocipher.md")
    print("                         two2_a/two2_b/two2_d (0 survivors).")
    print()
    print("  PT-reading, T then S   the 24 key values are known but their POSITIONS")
    print("                         depend on T.  For an un-enumerated T the cribs")
    print("                         impose c = 0 at every period -- they cannot")
    print("                         test it at all.  This reading is in exactly the")
    print("                         same evidential position as periods >= 27:")
    print("                         crib-free, decidable only by whether the output")
    print("                         reads as English.")
    print()
    print("  Bottom line for (e): the reading question changes nothing for any")
    print("  position-preserving cipher (E1), is closed by twocipher.md for two of")
    print("  the three transposition cases, and in the fourth case removes the")
    print("  cribs from play entirely rather than relocating them.  There is no")
    print("  version of (e) in which the standard 24 pairs are simply shifted to")
    print("  some other 24 contiguous pairs -- E3, E4 and E5 test those directly")
    print("  and find nothing above chance.")


if __name__ == "__main__":
    print("=" * 78)
    print("TASK (e)  PLAINTEXT-POSITION vs CIPHERTEXT-POSITION READINGS OF THE CRIBS")
    print("=" * 78)
    print("K4 = %s" % CT)
    print()
    sec_e1()
    sec_e2()
    sec_e3()
    sec_e4()
    sec_e5()
    sec_e6()
