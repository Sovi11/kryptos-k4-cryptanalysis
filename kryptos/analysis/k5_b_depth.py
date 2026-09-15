"""(b) THE K5 LEVER.

K5 is a second 97-character Sanborn message, made in 1988 at the same time as K4, and
described by the auction house as the "unpublished 1988 alternate K4 plaintext AND
CODING CHART".  Sanborn (Scientific American, 2025-11-12):

    "Both 97-letter messages will share some of the same coded words in the same position."

This script does four things:

  L1  Turns that sentence into propositions and works out, exactly, what each reading
      implies about the key stream.  In particular it checks the claim carried in this
      repository (README 3.4, findings/sanborn_statements.md C10) that the statement
      "argues against pure autokey and for a key stream fixed by position".  That claim
      is tested, not assumed: three synthetic-cipher experiments decide it.

  L2  Quantifies the alleged tension with "position-indexed systems are all ruled out"
      by measuring the fraction of the position-indexed key-stream space that the
      repository has actually searched.

  L3  Computes, alphabet-free and family-free, which CHART PERIODS the 24 cribs refute.
      This is the strongest statement the cribs can make about a positional chart and it
      needs no cipher model at all.

  L4  Builds and validates the depth machinery for the day K5 is published, and derives
      the exact chance expectations for the aligned-run test, so the decision rule is
      pre-registered rather than fitted afterwards.  It also settles how much a depth
      pair is actually worth, which turns out to depend entirely on whether the chart is
      shift-structured or a general per-column table.

Nothing here is a decryption claim.  Every count is printed beside its chance value.
"""
import os
import sys
import math
import random
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import k4_common as K
import runningkey_lib as RK

OUT = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


A2Z = K.A2Z
KRY = K.KRYPTOS_ALPHA
CT = K.CT
N = 97
CRIB = K.CRIB                      # 0-indexed pos -> plaintext letter
CRIB_POS = K.CRIB_POS


def hdr(t):
    P("")
    P("=" * 78)
    P(t)
    P("=" * 78)


# =========================================================================== L1
def L1_readings():
    hdr("L1.  WHAT \"THE SAME CODED WORDS IN THE SAME POSITION\" CAN MEAN")

    P("""
The sentence has one ambiguous noun.  "Coded words" is either

   READING A  the ciphertext letter-groups -- the words AFTER coding, i.e. C4 and C5
              carry identical letter runs at identical indices;
   READING B  the words that were coded -- the plaintext words, i.e. P4 and P5 carry
              the same words at the same indices, and nothing is claimed about the
              ciphertext at all.

Reading B is the ordinary-English one and matches how Sanborn uses the phrase elsewhere
("the coded words on the sculpture" = the message, not the cipher letters).  Reading A
is the one this repository's C10 note assumed.  They are NOT equivalent and they imply
different things, so both are carried through below.

Three models of the cipher are relevant:

   M_pos     C[i] = g_i(P[i]) with g_i a bijection on the alphabet depending only on the
             position i and on a chart that is the same for both messages.
   M_auto    the key at i depends on the message itself (plaintext or ciphertext
             autokey, with a primer).
   M_2chart  M_pos but K4 and K5 use DIFFERENT charts g_i and g'_i.  The auction lot
             description -- "alternate K4 plaintext AND coding chart" -- is evidence for
             exactly this.
""")


def _rand_chart(rng):
    """97 independent random bijections of A-Z: the most general positional chart."""
    ch = []
    for _ in range(N):
        a = list(A2Z)
        rng.shuffle(a)
        ch.append("".join(a))
    return ch


def _enc_chart(chart, pt):
    return "".join(chart[i][A2Z.index(c)] for i, c in enumerate(pt))


def _enc_shiftchart(kstream, pt):
    return "".join(A2Z[(A2Z.index(c) + kstream[i]) % 26] for i, c in enumerate(pt))


def _enc_ptautokey(primer, pt):
    """Classical plaintext autokey, Vigenere, plain alphabet."""
    key = list(primer)
    out = []
    for i, c in enumerate(pt):
        k = key[i]
        out.append(A2Z[(A2Z.index(c) + A2Z.index(k)) % 26])
        key.append(c)
    return "".join(out)


def _rand_text(rng, n):
    return "".join(rng.choice(A2Z) for _ in range(n))


def L1_theorems():
    hdr("L1b.  THE THREE THEOREMS, VERIFIED BY CONSTRUCTION")
    rng = random.Random(20260913)

    # ---- T1: positional single chart  =>  reading A and reading B coincide -------
    bad = 0
    for _ in range(400):
        chart = _rand_chart(rng)
        p4 = _rand_text(rng, N)
        p5 = list(_rand_text(rng, N))
        a, b = 30, 42                      # force a shared plaintext word here
        p5[a:b] = list(p4[a:b])
        p5 = "".join(p5)
        c4, c5 = _enc_chart(chart, p4), _enc_chart(chart, p5)
        agree_ct = [i for i in range(N) if c4[i] == c5[i]]
        agree_pt = [i for i in range(N) if p4[i] == p5[i]]
        if agree_ct != agree_pt:
            bad += 1
    P("T1  Under M_pos (one chart, any bijections):  C4[i]==C5[i]  <=>  P4[i]==P5[i].")
    P("    400 random charts x random message pairs with a planted shared 12-letter word:")
    P("    positions where the ciphertexts agree differed from where the plaintexts agree in",
      bad, "of 400 trials.")
    P("    => Under M_pos readings A and B are THE SAME STATEMENT.  A shared ciphertext run")
    P("       is neither more nor less than a shared plaintext run.  Reading A therefore")
    P("       carries no information about the key beyond what reading B carries.")

    # ---- T2: shared PREFIX is compatible with autokey ---------------------------
    P("")
    bad = 0
    for _ in range(400):
        primer = _rand_text(rng, 7)
        p4 = _rand_text(rng, N)
        shared = rng.randrange(20, 60)
        p5 = p4[:shared] + _rand_text(rng, N - shared)
        c4, c5 = _enc_ptautokey(primer, p4), _enc_ptautokey(primer, p5)
        if c4[:shared] != c5[:shared]:
            bad += 1
    P("T2  Under M_auto (plaintext autokey, shared primer): if the two plaintexts agree on")
    P("    the whole PREFIX [0,s), the two ciphertexts agree on [0,s) as well.")
    P("    400 trials with a random shared prefix: failures =", bad, "of 400.")
    P("    => 'shared coded words at shared positions' does NOT by itself exclude autokey.")
    P("       It excludes autokey only for a shared run that starts AFTER the first")
    P("       position at which the two plaintexts differ.  This is the step C10 skipped.")

    # ---- T3: a shared run AFTER a divergence does exclude autokey ---------------
    P("")
    trials = 4000
    runlen = 6
    hits = 0
    for _ in range(trials):
        primer = _rand_text(rng, 7)
        p4 = _rand_text(rng, N)
        p5 = list(_rand_text(rng, N))
        p5[63:69] = list(p4[63:69])        # shared PLAINTEXT word late in the message
        p5 = "".join(p5)
        c4, c5 = _enc_ptautokey(primer, p4), _enc_ptautokey(primer, p5)
        if c4[63:69] == c5[63:69]:
            hits += 1
    P("T3  Under M_auto, a shared plaintext word at positions 64-69 (1-indexed) does NOT")
    P("    produce a shared ciphertext run, because the keys have already diverged.")
    P("    %d trials, shared 6-letter plaintext word planted at 64-69:" % trials)
    P("    ciphertext run also shared in %d trials (chance 26^-6 = %.3e, expected %.2f)."
      % (hits, 26.0 ** -runlen, trials * 26.0 ** -runlen))
    P("    => IF a shared ciphertext run is observed at a position where the plaintexts")
    P("       had already diverged, autokey is excluded at odds 26^-len.  IF the shared")
    P("       run sits at the head of the message, nothing is excluded.")

    # ---- T4: two charts ---------------------------------------------------------
    P("")
    rng2 = random.Random(7)
    ch4 = _rand_chart(rng2)
    p4 = _rand_text(rng2, N)
    p5 = _rand_text(rng2, N)
    c4 = _enc_chart(ch4, p4)
    # build a SECOND chart that forces C5 to equal C4 on 64..74 although P5 differs there
    ch5 = _rand_chart(rng2)
    forced = list(range(63, 74))
    ok = True
    for i in forced:
        row = list(ch5[i])
        want, have = c4[i], row[A2Z.index(p5[i])]
        j, k = row.index(want), A2Z.index(p5[i])
        row[j], row[k] = row[k], row[j]
        ch5[i] = "".join(row)
        if ch5[i][A2Z.index(p5[i])] != c4[i]:
            ok = False
    c5 = _enc_chart(ch5, p5)
    P("T4  Under M_2chart the statement is vacuous: with a free second chart any ciphertext")
    P("    agreement can be manufactured over any plaintext disagreement.")
    P("    constructed example: P4 and P5 differ at all of 64-74, yet C4[64:74]==C5[64:74]:",
      c4[63:74] == c5[63:74], "and every chart column is still a bijection:",
      ok and all(len(set(c)) == 26 for c in ch5))
    P("    => If K5 really has its own coding chart, 'the same coded words in the same")
    P("       position' constrains NOTHING about the mechanism.")


def L1_verdict():
    hdr("L1c.  VERDICT ON THE ALLEGED CONTRADICTION")
    P("""
The claim in README 3.4 / C10 -- "shared coded words at shared positions is a strong hint
that the system is positional, and argues against autokey" -- does not survive T1-T4.

  * Under reading A + M_pos the statement is EQUIVALENT to reading B (T1).  It is
    therefore not evidence FOR M_pos; it is what M_pos predicts once the plaintexts
    share words, and reading B predicts the plaintext sharing directly.  The inference
    "shared ciphertext => positional" is affirming the consequent.
  * Autokey is not excluded (T2).  A shared head-of-message run is exactly what autokey
    with a shared primer produces.  Only a shared run occurring after the plaintexts
    have diverged excludes it (T3), and we cannot know that until K5 is published.
  * A second chart makes the whole statement vacuous (T4), and the auction lot text is
    direct evidence for a second chart.

SO: there is NO contradiction with the repository's negatives, because the repository has
not in fact ruled out position-indexed systems -- see L2, which measures how little of
that space has been searched.  The tension was an artefact of overreading one sentence of
Sanborn's and of understating what "position-indexed systems are ruled out" means.

The weaker claim the orchestrator anticipated is the correct one: the shared words are
most likely shared because the two PLAINTEXTS share words at those positions.  That is
consistent with every cipher model on the table and it is the reading under which
Sanborn's sentence is a plain statement about his two drafts of the same message.
""")


# =========================================================================== L2
def L2_freedom():
    hdr("L2.  HOW MUCH OF THE POSITION-INDEXED SPACE HAS ACTUALLY BEEN SEARCHED?")

    total = 26.0 ** N
    fit = 26.0 ** (N - 24)
    P("A position-indexed key stream for a letterwise cipher on 97 letters is one of")
    P("   26^97 = %.3e  streams." % total)
    P("The 24 cribs fix exactly 24 of the 97 key symbols (one per crib position; the")
    P("positions are distinct), leaving")
    P("   26^73 = %.3e  streams that fit all 24 cribs EXACTLY, for EVERY one of the 24" % fit)
    P("   cipher/alphabet combos.  That is %.3e crib-perfect key streams in total." % (24 * fit))
    P("")
    P("What the repository has searched inside that space (orders of magnitude, generous):")
    searched = []
    per = sum(26.0 ** p for p in range(2, 27))
    searched.append(("periodic keys, periods 2-26 (all keys, via the consistency test)", per))
    searched.append(("position-dependent arithmetic shift models", 1.0e8))
    searched.append(("running key: 66 texts x ~900 offsets x 24 combos x 26 rotations", 66 * 900 * 24 * 26.0))
    searched.append(("autokey: 2 directions x primer lengths 1-96 x 24 combos", 2 * 96 * 24 * 26.0 ** 4))
    searched.append(("lateral key material: 194 streams x offsets x combos", 1.65e7))
    searched.append(("two-stage forced-keystream tests", 4.94e7))
    tot = 0.0
    for name, v in searched:
        P("   %-62s %.3e" % (name, v))
        tot += v
    P("   %-62s %.3e" % ("TOTAL (upper bound, double counting allowed)", tot))
    P("")
    P("   fraction of the crib-perfect positional space examined:  %.3e / %.3e = %.3e"
      % (tot, fit, tot / fit))
    P("")
    P("""CONCLUSION.  "Position-indexed systems are ruled out" is false as stated.  What is
ruled out is the STRUCTURED position-indexed streams: short-period, arithmetic in the
index, or copied in reading order out of a known text.  Roughly 3e-67 of the
crib-consistent positional space has been touched.  A 97-symbol hand-drawn chart with no
compressive description is a position-indexed key stream, it fits the cribs trivially,
and no crib-based search can ever reach it.  That is precisely the object Sanborn keeps
naming -- "no one has recovered the original matrix" -- and it is entirely consistent
with K5 sharing words with K4 at the same positions.""")


# =========================================================================== L3
def L3_chart_periods():
    hdr("L3.  WHICH CHART PERIODS DO THE CRIBS REFUTE?  (alphabet-free, family-free)")

    P("""Model: C[i] = g_i(P[i]) with each g_i a bijection.  Say the chart has period p if
g_i = g_j whenever i == j (mod p).  Then for any i,j in the same class:
        P_i == P_j  <=>  C_i == C_j.
This uses no alphabet, no cipher family and no key algebra: it holds for Vigenere,
Beaufort, Quagmire, Gromark, a hand-drawn table, anything letterwise.  A crib pair that
violates it refutes EVERY p dividing |i-j|.""")

    pos = CRIB_POS
    eq_pairs, ne_pairs = [], []
    for a in range(len(pos)):
        for b in range(a + 1, len(pos)):
            i, j = pos[a], pos[b]
            pe = CRIB[i] == CRIB[j]
            ce = CT[i] == CT[j]
            if pe != ce:
                ne_pairs.append((i, j))
            elif pe and ce:
                eq_pairs.append((i, j))
    P("")
    P("crib pairs that REFUTE g_i == g_j (one of pt/ct equal, the other not):", len(ne_pairs))
    seps = sorted({j - i for i, j in ne_pairs})
    P("   their separations:", seps)
    P("crib pairs CONSISTENT with g_i == g_j and informative (both pt and ct equal):",
      len(eq_pairs), "->", [(i + 1, j + 1, j - i) for i, j in eq_pairs])

    refuted = set()
    for i, j in ne_pairs:
        d = j - i
        for p in range(1, N + 1):
            if d % p == 0:
                refuted.add(p)
    surv = [p for p in range(1, N + 1) if p not in refuted]
    P("")
    P("periods p in 1..97 REFUTED outright by a single crib pair:", len(refuted))
    P("periods p in 1..97 that SURVIVE this test:", len(surv))
    P("   ", surv)
    P("")
    # how many constraints does each surviving p actually carry?
    P("For each surviving p, the number of crib pairs that would have to agree by")
    P("coincidence if the chart were NOT periodic (i.e. the evidential weight available):")
    rows = []
    for p in surv:
        by = defaultdict(list)
        for i in pos:
            by[i % p].append(i)
        c = sum(len(v) - 1 for v in by.values() if len(v) > 1)
        eq = sum(1 for i, j in eq_pairs if (j - i) % p == 0)
        rows.append((p, c, eq))
    for p, c, eq in rows:
        P("   p=%-3d  crib collisions c=%-3d  supporting equal-pairs=%d   chance 26^-c = %.3e"
          % (p, c, eq, 26.0 ** -c))
    P("")
    P("""READ THIS CAREFULLY.  Every surviving p with c == 0 is not evidence for that period;
it is a period the cribs cannot see at all.  The list above is the exact boundary of what
24 crib letters can say about a positional chart, and it is the same boundary the period
sweeps hit: nothing above p = 26 carries real weight, and p >= 53 carries none.""")


# =========================================================================== L4
def _binom_tail(n, m, p=1.0 / 26.0):
    from math import comb
    return sum(comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(m, n + 1))


def _run_dp(n, L, p=1.0 / 26.0):
    """P(no aligned matching run of length >= L in n independent positions)."""
    # states: current run length 0..L-1
    st = [0.0] * L
    st[0] = 1.0
    for _ in range(n):
        new = [0.0] * L
        for r in range(L):
            if st[r] == 0.0:
                continue
            new[0] += st[r] * (1 - p)
            if r + 1 < L:
                new[r + 1] += st[r] * p
            # r+1 == L means a run of length L was achieved -> absorbed as failure
        st = new
    return sum(st)


def L4_depth():
    hdr("L4.  THE DEPTH ATTACK: WHAT K5 WOULD ACTUALLY BUY, AND THE PRE-REGISTERED TEST")

    P("L4a.  Chance expectations for the aligned-run test (two independent 97-letter texts)")
    P("")
    exp_match = N / 26.0
    P("   expected number of aligned equal positions: 97/26 = %.4f" % exp_match)
    P("   P(at least one aligned run of length >= L), exact DP over 97 positions:")
    for L in (3, 4, 5, 6, 9, 11, 13):
        q = 1.0 - _run_dp(N, L)
        P("      L=%-3d  %.3e" % (L, q))
    P("")
    P("""   DECISION RULE, pre-registered.  On the day K5's ciphertext is published:
      * any aligned identical run of length >= 5 between C4 and C5 is significant at
        p < 3e-4 and establishes ONE SHARED POSITIONAL CHART plus shared plaintext there;
      * an aligned run of length >= 9 (NORTHEAST) or >= 11 (BERLINCLOCK) is decisive
        (p < 1e-9), and under M_pos it also tells us the shared word is the one Sanborn
        already released as a crib;
      * NO aligned run of length >= 4 anywhere is evidence for M_2chart, i.e. for the
        auction lot's "alternate ... coding chart" reading, and it kills the depth attack.""")

    # second statistic: the COUNT of aligned matches, independent of run length
    import math
    mean = N / 26.0
    var = N * (1 / 26.0) * (25 / 26.0)
    sd = math.sqrt(var)
    P("")
    P("   SECOND STATISTIC (weaker but more robust): the plain COUNT of aligned equal")
    P("   positions.  Under independence it is Binomial(97, 1/26): mean %.2f, sd %.2f."
      % (mean, sd))
    P("   thresholds:  >= %2d matches  p = %.4f" % (8, _binom_tail(N, 8)))
    P("                >= %2d matches  p = %.4f" % (10, _binom_tail(N, 10)))
    P("                >= %2d matches  p = %.2e" % (14, _binom_tail(N, 14)))
    P("""   This one matters because two charts drawn on the SAME worksheet by the same hand
   could share individual columns without sharing whole words.  An excess of isolated
   aligned matches with no long run would be evidence for that middle case, which
   neither reading A nor reading B anticipates.""")

    P("")
    P("L4b.  How much information is a depth pair worth?  This depends on the chart type.")
    P("")
    P("""   CASE 1, shift-structured chart (Quagmire/Vigenere family: g_i is 'add k_i' in a
   fixed alphabet pair).  Then
        idx(C4_i) - idx(C5_i) = idx(P4_i) - idx(P5_i)   (mod 26)
   and the key cancels.  The 97-symbol difference stream is recovered outright; with both
   plaintexts English this is textbook depth-2 and 97 letters is comfortably enough.
   Worth: the whole message.

   CASE 2, general per-column chart (97 independent bijections -- a hand-drawn
   spreadsheet with 97 columns and 26 rows, which is exactly what Sanborn calls "the
   matrix").  Then knowing (C4_i, C5_i) pins two cells of column i and NOTHING ELSE:
   for any pair of distinct plaintext letters there exists a bijection realising any pair
   of distinct ciphertext letters.  The only surviving constraint is
        C4_i == C5_i  <=>  P4_i == P5_i.
   Worth: exactly the 97-bit agreement pattern between the two plaintexts, and no more.""")

    # verify CASE 2 claim by construction
    rng = random.Random(99)
    ok = 0
    for _ in range(2000):
        p4i, p5i = rng.sample(range(26), 2)
        c4i, c5i = rng.sample(range(26), 2)
        row = list(range(26))
        # want row[p4i]=c4i and row[p5i]=c5i
        j = row.index(c4i)
        row[p4i], row[j] = row[j], row[p4i]
        k = row.index(c5i)          # k != p4i because row[p4i]==c4i!=c5i
        row[p5i], row[k] = row[k], row[p5i]
        if row[p4i] == c4i and row[p5i] == c5i and len(set(row)) == 26:
            ok += 1
    P("")
    P("   verification of CASE 2: for 2000 random (P4_i != P5_i, C4_i != C5_i) quadruples a")
    P("   valid bijection column realising both was constructed in %d of 2000 cases." % ok)
    P("   => under a general chart, depth-2 leaks the agreement pattern and nothing else.")

    P("")
    P("L4c.  The depth machinery itself, validated on synthetic pairs.")
    rng = random.Random(2468)
    # synthetic shift-chart depth: recover the difference stream
    kstream = [rng.randrange(26) for _ in range(N)]
    p4 = _rand_text(rng, N)
    p5 = list(_rand_text(rng, N))
    p5[63:74] = list(p4[63:74])
    p5 = "".join(p5)
    c4 = _enc_shiftchart(kstream, p4)
    c5 = _enc_shiftchart(kstream, p5)
    diff_ct = [(A2Z.index(c4[i]) - A2Z.index(c5[i])) % 26 for i in range(N)]
    diff_pt = [(A2Z.index(p4[i]) - A2Z.index(p5[i])) % 26 for i in range(N)]
    P("   shift-chart pair: difference stream recovered exactly:", diff_ct == diff_pt)
    zruns = []
    i = 0
    while i < N:
        if diff_ct[i] == 0:
            j = i
            while j < N and diff_ct[j] == 0:
                j += 1
            if j - i >= 3:
                zruns.append((i + 1, j, j - i))
            i = j
        else:
            i += 1
    P("   zero-runs of length >= 3 (1-indexed start, end, length):", zruns)
    P("   planted shared word was at 64-74 (length 11): located =",
      any(s <= 64 and e >= 74 for s, e, _ in zruns))
    # synthetic general-chart depth: only the agreement pattern survives
    chart = _rand_chart(rng)
    c4g, c5g = _enc_chart(chart, p4), _enc_chart(chart, p5)
    agree_ct = [i for i in range(N) if c4g[i] == c5g[i]]
    agree_pt = [i for i in range(N) if p4[i] == p5[i]]
    P("   general-chart pair: ciphertext agreement pattern == plaintext agreement pattern:",
      agree_ct == agree_pt, "(this is all it yields)")

    P("")
    P("L4d.  What the released cribs predict for K5, if there is one shared chart.")
    P("""   Sanborn's four released 'coded words' are EAST, NORTHEAST, BERLIN, CLOCK.  If
   'some of the same coded words in the same position' instantiates on any of them, then
   under M_pos K5's ciphertext must literally reproduce K4's letters there:""")
    for name, a, b in (("EAST", 22, 25), ("NORTHEAST", 26, 34),
                       ("BERLIN", 64, 69), ("CLOCK", 70, 74)):
        P("      %-10s positions %2d-%2d  =>  C5 must read  %s" % (name, a, b, CT[a - 1:b]))
    P("""   These are falsifiable the moment K5 appears and they cost nothing to check.
   If they hold, the 24 cribs transfer to K5 unchanged and buy no new equations -- the
   value then lies entirely in the OTHER aligned runs, each of which localises a shared
   word that can be crib-dragged.  If they fail while some other aligned run holds, the
   shared words are not the released ones.  If no aligned run of length >= 4 exists at
   all, M_2chart is confirmed and K5 is worthless as depth.""")


# =========================================================================== L5
def L5_strategy():
    hdr("L5.  THE STRATEGIC CONSEQUENCE NOBODY HAS STATED")
    P("""
Put the auction lot text and the 1988 date together:

   item 6 of the RR Auction lot: "Unpublished 1988 alternate K4 plaintext AND CODING
   CHART -- now known as K5".

Two messages, 97 characters each, EACH WITH ITS OWN CHART, both drawn in 1988, before the
final plaintext was fixed.  Three consequences follow, and they are the useful output of
this whole line:

 1. 97 IS A PROPERTY OF THE WORKSHEET, NOT OF THE MESSAGE.  Sanborn had a 97-cell chart
    and wrote messages to fit it.  97 = 4 + 31 + 31 + 31 is the panel layout.  Any theory
    that derives 97 from the plaintext has the causality backwards.

 2. THE CHART IS PER-MESSAGE, HENCE FITTED, HENCE PLAUSIBLY INCOMPRESSIBLE.  A key stream
    drawn from a keyword, a text, or a formula would be reused across drafts -- you do not
    redraw a keyword.  Redrawing the chart for the alternate plaintext is what you do when
    the chart IS the key material.  This is the single best explanation on offer for 35
    years of failure: there may be no short description of the key stream to find.

 3. THEREFORE THE ALIGNED-RUN TEST IN L4a IS THE MOST INFORMATIVE SINGLE EXPERIMENT LEFT,
    and it costs one minute of work on the day K5 is published.  It decides between:
        one shared chart      -> depth-2, and (if shift-structured) the message falls;
        two charts            -> no depth, and the chart itself is the only route.
    Note that (2) predicts the second outcome, while Sanborn's sentence, read as reading A,
    predicts the first.  They are in direct conflict, and that conflict is resolvable by
    one string comparison.  Reading B removes the conflict at the cost of removing the
    cryptanalytic content of the sentence.

L6.  THE TENSION THIS CREATES WITH SCHEIDT, WHICH IS REAL AND UNRESOLVED.

If the key material is an incompressible 97-symbol chart, then K4 is not breakable from
the ciphertext, and that contradicts Ed Scheidt directly: "designed to be solved in a
straight-forward manner with pencil and paper" (2003), a 9/10 difficulty rating, an
expectation that it would fall in five to ten years, and his own design brief, "don't
create something that you cannot break".  Both cannot be true.  The documented resolution
is Sanborn's, not mine: Scheidt gave him systems "plus ways to modify all of those
systems", and Sanborn says he modified them further so that even Scheidt would not know
what it says, and nobody ever ran a reverse check on K4.  So Scheidt's breakability
guarantee covers SCHEIDT'S layer.  The incompressible object, if there is one, is the
artist's mask on top of it.  That is a statement about where to look: at a hand-drawn
worksheet, not at an algorithm.

Recommended standing action: watch paradigm.xyz for the K5 ciphertext and run
    align_runs(C4, C5)
from this script the moment it appears.  The decision rule is fixed above, in advance.
""")


def main():
    hdr("(b) THE K5 LEVER -- rigorous consequences of the two 97-letter messages")
    P("ciphertext K4:", CT)
    P("crib pairs   :", "".join(CT[i] for i in CRIB_POS), "->",
      "".join(CRIB[i] for i in CRIB_POS))
    L1_readings()
    L1_theorems()
    L1_verdict()
    L2_freedom()
    L3_chart_periods()
    L4_depth()
    L5_strategy()
    hdr("END (b)")
    with open(os.path.join(HERE, "k5_b_output.txt"), "w") as f:
        f.write("\n".join(OUT) + "\n")


# ------------------------------------------------------------------ public API
def align_runs(c4, c5, min_len=3):
    """The pre-registered test.  Returns the aligned identical runs of length >= min_len."""
    c4 = "".join(ch for ch in c4.upper() if ch.isalpha())
    c5 = "".join(ch for ch in c5.upper() if ch.isalpha())
    n = min(len(c4), len(c5))
    runs, i = [], 0
    while i < n:
        if c4[i] == c5[i]:
            j = i
            while j < n and c4[j] == c5[j]:
                j += 1
            if j - i >= min_len:
                runs.append((i + 1, j, j - i, c4[i:j]))
            i = j
        else:
            i += 1
    return runs


if __name__ == "__main__":
    main()
