"""(c) CROSS-SECTION KEY CONTINUATION.

K1 is keyed PALIMPSEST (10 letters), K2 is keyed ABSCISSA (8).  If one of those keys ran
CONTINUOUSLY through the sculpture instead of restarting at each section, K4 would begin
at a specific, computable phase.  This script

  C1  computes every defensible cumulative letter count and the phase it implies, for
      both keywords and for their concatenations, including the variants created by
      Sanborn's dropped K2 letter, by the four carved question marks, and by the
      X separators;
  C2  proves the SUBSUMPTION theorem -- a repeating key of length L is tested at every
      phase simultaneously by the period-L crib-consistency test, so the specific phases
      are decided by sweeps that are already on record -- and then runs the explicit
      per-phase test anyway, so the negative is stated as a number rather than inferred;
  C3  handles the cases subsumption does NOT cover: alphabet rotation carried across
      sections, a progressive key whose advance counter continues, and a key stream that
      continues as a RUNNING key rather than as a repeating one.

Chance expectation for every explicit test: a random key reproduces 24/26 = 0.923 of the
24 crib letters on average; 24/24 is the only result that matters.
"""
import os
import sys
import itertools
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import k5_lib as L
import runningkey_lib as RK

OUT = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def hdr(t):
    P("")
    P("=" * 78)
    P(t)
    P("=" * 78)


A2Z, KRY, CT, N = L.A2Z, L.KRY, L.CT, L.N
CRIB_POS, CRIB_PT, CRIB_CT = L.CRIB_POS, L.CRIB_PT, L.CRIB_CT

# ---------------------------------------------------------------- the counts
K1_PT, K2_PT, K3_PT = RK.K1_PT, RK.K2_PT, RK.K3_PT
K1_CT, K2_CT, K3_CT = RK.K1_CT, RK.K2_CT, RK.K3_CT


def counts_table():
    hdr("C1.  EVERY DEFENSIBLE CUMULATIVE COUNT BEFORE K4, AND THE PHASE IT IMPLIES")
    P("")
    P("Raw lengths actually in the data (verified, not quoted):")
    P("   K1 plaintext %3d   K1 ciphertext %3d" % (len(K1_PT), len(K1_CT)))
    P("   K2 plaintext %3d   K2 ciphertext %3d   (Sanborn's 2006 dropped S: pt is 1 longer)"
      % (len(K2_PT), len(K2_CT)))
    P("   K3 plaintext %3d   K3 ciphertext %3d" % (len(K3_PT), len(K3_CT)))
    P("   question marks carved: 3 inside K2, 1 ending K3")
    P("   panel offset of K4 among all 869 carved characters: 772")
    P("   panel offset of K4 among the 865 carved letters   : 768")
    P("")
    cands = {}
    cands["K1 only (ct=pt=63)"] = 63
    cands["K1+K2 ciphertext (63+369)"] = 63 + len(K2_CT)
    cands["K1+K2 plaintext  (63+370)"] = 63 + len(K2_PT)
    cands["K2 ciphertext only"] = len(K2_CT)
    cands["K2 plaintext only"] = len(K2_PT)
    cands["K3 only"] = len(K3_CT)
    cands["K2+K3 ciphertext"] = len(K2_CT) + len(K3_CT)
    cands["K2+K3 plaintext"] = len(K2_PT) + len(K3_PT)
    cands["K1+K2+K3 ciphertext (=panel letters, 768)"] = 63 + len(K2_CT) + len(K3_CT)
    cands["K1+K2+K3 plaintext (769)"] = 63 + len(K2_PT) + len(K3_PT)
    cands["K1+K2+K3 ct + 4 question marks (=772)"] = 63 + len(K2_CT) + len(K3_CT) + 4
    cands["K1+K2+K3 pt, X separators stripped"] = (
        len(K1_PT.replace("X", "")) + len(K2_PT.replace("X", "")) + len(K3_PT.replace("X", "")))
    cands["K1+K2 pt, X stripped"] = len(K1_PT.replace("X", "")) + len(K2_PT.replace("X", ""))

    P("%-46s %6s %8s %8s %8s %8s" % ("cumulative count before K4", "n", "mod 10",
                                     "mod 8", "mod 18", "mod 7"))
    for name, n in cands.items():
        P("%-46s %6d %8d %8d %8d %8d" % (name, n, n % 10, n % 8, n % 18, n % 7))
    P("")
    P("So the phases to test are, for PALIMPSEST (L=10):",
      sorted({n % 10 for n in cands.values()}))
    P("                       for ABSCISSA   (L=8) :",
      sorted({n % 8 for n in cands.values()}))
    P("                       for PALIMPSESTABSCISSA (L=18):",
      sorted({n % 18 for n in cands.values()}))
    return cands


# ---------------------------------------------------------------- subsumption
def subsumption(cands):
    hdr("C2.  THE SUBSUMPTION THEOREM, AND THE EXPLICIT PER-PHASE TEST ANYWAY")
    P("""
THEOREM.  Let W be any key word of length L and s any phase.  The key stream
k_i = W[(s+i) mod L] is periodic with period L.  The crib-consistency test at period L
asks only whether the 24 crib-forced key values are constant on residue classes mod L;
it quantifies over ALL period-L key streams at once, hence over all (W, s) pairs
simultaneously.  Therefore a period-L test that returns zero survivors kills every
keyword of length L at every phase, including every cross-section continuation phase.

Corollary.  Rotating an alphabet is also absorbed: replacing the plaintext alphabet by
its rotation by r maps every forced key value k -> k - r (Vigenere/variant-Beaufort) or
k + r (Beaufort), a constant offset that cannot change whether the values are constant on
a residue class.  The same holds for the ciphertext alphabet.  So "the alphabet rotation
carried over from K1/K2" is subsumed too.

This makes (c) a CLOSED corollary of findings/families.md, where periods 2-26 were swept
over 7.09M keyed-alphabet pairs with zero survivors.  The explicit test below is run so
that the negative is a measured number rather than an inference.""")

    sw = L.Sweeper([("plain", A2Z), ("kryptos", KRY)])
    P("")
    P("Period-L crib consistency for the relevant L (12 combos = 3 rules x 2 pt x 2 ct):")
    P("%-6s %6s %10s %14s %12s" % ("L", "c", "survivors", "chance/test", "expected"))
    for Lp in (7, 8, 10, 18, 25):
        rows = sw.sweep(CRIB_POS, CRIB_PT, CRIB_CT, [Lp])
        p, c, ns, ch, _ = rows[0]
        P("%-6d %6d %10d %14.3e %12.3e" % (p, c, ns, ch, ch * sw.n))
    P("")
    P("(c = number of independent equalities the 24 cribs force on a period-L key.)")


# ---------------------------------------------------------- explicit phase test
def explicit_phases(cands):
    hdr("C2b.  EXPLICIT: build the actual continued key stream and count crib hits")
    cb = L.Combos([("plain", A2Z), ("kryptos", KRY)])
    P("Key alphabet now matters (a concrete key TEXT is supplied), so all 24 combos")
    P("(3 rules x 2 pt x 2 ct x 2 key alphabets) are scored.  Chance = 24/26 = 0.923 of")
    P("the 24 crib letters; only 24/24 counts.")
    P("")
    words = {"PALIMPSEST": "PALIMPSEST", "ABSCISSA": "ABSCISSA",
             "PALIMPSESTABSCISSA": "PALIMPSESTABSCISSA",
             "ABSCISSAPALIMPSEST": "ABSCISSAPALIMPSEST",
             "KRYPTOS": "KRYPTOS",
             "PALIMPSESTABSCISSAKRYPTOS": "PALIMPSESTABSCISSAKRYPTOS"}
    best = (0, None)
    tests = 0
    hist = defaultdict(int)
    for wname, w in words.items():
        phases = sorted({n % len(w) for n in cands.values()} | {0})
        for s in phases:
            ks = "".join(w[(s + i) % len(w)] for i in range(N))
            ag = L.crib_agreement(ks, cb)
            tests += cb.n
            for v in ag:
                hist[int(v)] += 1
            m = int(ag.max())
            if m > best[0]:
                best = (m, (wname, s, cb.labels[int(ag.argmax())]))
    P("tests: %d (word x continuation phase x combo)" % tests)
    P("best crib agreement: %d/24 at %s" % (best[0], best[1]))
    P("agreement histogram:", dict(sorted(hist.items())))
    exp = tests * 24 / 26.0
    P("expected total crib hits by chance: %.1f ; observed: %d"
      % (exp, sum(k * v for k, v in hist.items())))
    P("P(any one test reaches 24/24) = 26^-24 = %.3e ; over %d tests, expected %.3e"
      % (26.0 ** -24, tests, tests * 26.0 ** -24))


# -------------------------------------------------- non-subsumed continuations
def nonsubsumed(cands):
    hdr("C3.  THE CASES SUBSUMPTION DOES NOT COVER")
    cb = L.Combos([("plain", A2Z), ("kryptos", KRY)])

    P("")
    P("C3a. PROGRESSIVE continuation: the key letter advances by one each time the")
    P("     keyword restarts, and the advance counter CONTINUES from the count reached")
    P("     at the end of K3 -- k_i = W[(s+i) mod L] + floor((n0+i)/L), n0 = the count.")
    best = (0, None)
    tests = 0
    for wname, w in (("PALIMPSEST", "PALIMPSEST"), ("ABSCISSA", "ABSCISSA"),
                     ("KRYPTOS", "KRYPTOS"), ("PALIMPSESTABSCISSA", "PALIMPSESTABSCISSA")):
        Lw = len(w)
        for n0 in sorted(set(cands.values())):
            for direction in (1, -1):
                ks = "".join(A2Z[(A2Z.index(w[(n0 + i) % Lw])
                                  + direction * ((n0 + i) // Lw)) % 26] for i in range(N))
                ag = L.crib_agreement(ks, cb)
                tests += cb.n
                if int(ag.max()) > best[0]:
                    best = (int(ag.max()), (wname, n0, direction,
                                            cb.labels[int(ag.argmax())]))
    P("     tests: %d ; best %d/24 at %s" % (tests, best[0], best[1]))
    P("     chance: expected best-of-%d under 24 independent 1/26 draws is ~%.1f/24"
      % (tests, 24 / 26.0))

    P("")
    P("C3b. RUNNING-key continuation: the key is the SCULPTURE TEXT itself, continued")
    P("     past the end of K3 into K4 -- i.e. the key letter for K4 position i is the")
    P("     (n0+i)th letter of the concatenated text.  n0 is the cross-section count.")
    P("     (findings/runningkey.md swept all offsets of these texts; this restricts to")
    P("     the specific continuation offsets and is reported for completeness.)")
    corpus = RK.corpus()
    rows = []
    for tname in ("K1K2K3_pt", "K1K2K3_ct", "left_panel_all_ct",
                  "K1K2K3_pt_IDBYROWS", "tableau_physical", "tableau_ideal"):
        t = corpus[tname]
        for n0 in sorted(set(cands.values())):
            if n0 + N > len(t):
                continue
            ks = t[n0:n0 + N]
            ag = L.crib_agreement(ks, cb)
            rows.append((int(ag.max()), tname, n0, cb.labels[int(ag.argmax())]))
    rows.sort(reverse=True)
    P("     continuation offsets tested: %d ; best:" % len(rows))
    for r in rows[:5]:
        P("        %d/24  %-22s n0=%-4d %s" % r)

    P("")
    P("C3c. The 'one key per section, the NEXT key in the list' reading.  K1 used the")
    P("     first keyword, K2 the second; the next keyword of the same provenance would")
    P("     key K4.  Sanborn's own vocabulary supplies the candidate list.  A keyword of")
    P("     length L is subsumed by the period-L sweep, so this is a confirmation run.")
    cand_words = ["ORDINATE", "COORDINATE", "ABSCISSAE", "PALIMPSESTS", "TANGENT",
                  "SECANT", "ASYMPTOTE", "CARTESIAN", "MERIDIAN", "AZIMUTH",
                  "LODESTONE", "WELTZEITUHR", "ALEXANDERPLATZ", "TUTANKHAMUN",
                  "CARTER", "CARNARVON", "WONDERFULTHINGS", "LAYERTWO", "IQLUSION",
                  "UNDERGRUUND", "DESPARATLY", "SHADOWFORCES", "LUCIDMEMORY",
                  "VIRTUALLYINVISIBLE", "DIGETAL", "INVISIBLE", "MAGNETICFIELD"]
    best = (0, None)
    tests = 0
    for w in cand_words:
        for s in range(len(w)):
            ks = "".join(w[(s + i) % len(w)] for i in range(N))
            ag = L.crib_agreement(ks, cb)
            tests += cb.n
            if int(ag.max()) > best[0]:
                best = (int(ag.max()), (w, s, cb.labels[int(ag.argmax())]))
    P("     %d keywords x all phases x %d combos = %d tests ; best %d/24 at %s"
      % (len(cand_words), cb.n, tests, best[0], best[1]))


def validate():
    hdr("C0.  VALIDATION")
    fails = L.selftest(verbose=False)
    P("k5_lib selftest (round trips, planted-period recovery, perturbation rejection,")
    P("explicit-key crib scoring, K1 re-encryption under PALIMPSEST):",
      "PASS" if not fails else "FAIL %r" % (fails,))
    # positive control: plant PALIMPSEST at a known continuation phase and recover it
    cb = L.Combos([("plain", A2Z), ("kryptos", KRY)])
    s = 8
    ks = "".join("PALIMPSEST"[(s + i) % 10] for i in range(N))
    pt = list("X" * N)
    for i, ch in L.CRIB.items():
        pt[i] = ch
    fake_ct = "".join(KRY[L.ct_from(0, KRY.index(pt[i]), KRY.index(ks[i]))]
                      for i in range(N))
    ag = L.crib_agreement(ks, cb, ct=fake_ct)
    P("positive control: a synthetic K4 built with PALIMPSEST at phase 8 (Quagmire III)")
    P("   is recovered at %d/24 by the explicit phase test.  Expected 24." % int(ag.max()))


def main():
    hdr("(c) CROSS-SECTION KEY CONTINUATION")
    P("K4 ciphertext:", CT)
    validate()
    cands = counts_table()
    subsumption(cands)
    explicit_phases(cands)
    nonsubsumed(cands)
    hdr("END (c)")
    with open(os.path.join(HERE, "k5_c_output.txt"), "w") as f:
        f.write("\n".join(OUT) + "\n")


if __name__ == "__main__":
    main()
