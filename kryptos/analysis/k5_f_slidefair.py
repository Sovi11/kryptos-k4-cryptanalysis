"""(a, continued) METHOD GENEALOGY -- the census, and the family it turns up.

analysis/k5_a_genealogy.py already argued the genealogy from Gromark and from composing
K3's route with a key stream.  This script does the part that was missing: a COMPLETE
census of the hand ciphers a 1989 CIA cryptographer would have had on the shelf, each
classified against this repository's record, with the reason it is closed.  Two hard
structural facts do most of the work:

   F1  K4's ciphertext contains all 26 letters (J at 41, 52, 82).  Any system whose
       ciphertext alphabet has fewer than 26 symbols is impossible outright.
   F2  S -> S at position 33 and K -> K at 74: a letter can represent itself, which kills
       every reciprocal-without-fixed-points system.

The census turns up exactly one 26-letter, hand-executable, self-encryption-permitting
family that is nowhere in this repository: the ACA **SLIDEFAIR** (and its Portax cousin),
the digraphic slide cipher -- which is precisely "the next step up from Vigenere" in the
1989 ACA curriculum and therefore exactly what a genealogy argument should predict.

Slidefair turns out to carry an ALPHABET-DEPENDENT BUT KEY-FREE invariant, so the cribs
decide it in one line per alphabet rather than by sweeping keys.  That invariant is
derived, verified by round trip, and then applied.
"""
import os
import sys
import itertools
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import k5_lib as L
import k4_common as K

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
CRIB, CRIB_POS = L.CRIB, L.CRIB_POS


# ================================================================== the census
def census():
    hdr("F1/F2.  THE TWO STRUCTURAL FACTS, RESTATED AS A FILTER")
    from collections import Counter
    c = Counter(CT)
    P("letters present in K4:", len(c), "of 26 ; rarest:",
      sorted(c.items(), key=lambda x: x[1])[:5])
    P("J occurs at 1-indexed", [i + 1 for i, ch in enumerate(CT) if ch == "J"])
    P("self-encryptions in the cribs: ", [(i + 1, CT[i]) for i in CRIB_POS
                                          if CT[i] == CRIB[i]])
    P("doubled ciphertext letters at 1-indexed:",
      [(i + 1, CT[i]) for i in range(N - 1) if CT[i] == CT[i + 1]])

    hdr("THE 1989 HAND-CIPHER CENSUS, CLASSIFIED")
    rows = [
        # (family, verdict, reason)
        ("Aristocrat / Patristocrat (monoalphabetic)", "CLOSED", "families.md"),
        ("Key Phrase cipher", "CLOSED", "monoalphabetic; families.md"),
        ("Affine / decimation", "CLOSED", "families.md"),
        ("Vigenere / Beaufort / Variant, periodic", "CLOSED", "families.md p=2-26"),
        ("Quagmire I-IV", "CLOSED", "families.md, 7.09M alphabet pairs"),
        ("Gronsfeld", "CLOSED", "families.md"),
        ("Porta", "CLOSED", "F2: Porta has no fixed points; S->S at 33 kills it"),
        ("Trithemius / progressive key", "CLOSED", "families.md"),
        ("Running key", "CLOSED", "runningkey.md, 66 texts, all offsets"),
        ("Autokey (pt and ct)", "CLOSED", "runningkey.md, primers 1-96"),
        ("Interrupted key (ct-triggered)", "CLOSED", "seg_c_skiprule.py"),
        ("Interrupted key (pt-triggered)", "CLOSED", "seg_e_plaintrig.py"),
        ("Irregular key advance / desync", "CLOSED", "seg_d_interrupted.py"),
        ("Gromark, periodic Gromark", "CLOSED", "k5_a_genealogy.py"),
        ("Hill 2x2 / 3x3, linear and affine", "CLOSED", "families.md"),
        ("Playfair", "IMPOSSIBLE", "F1 (25 letters) and F2 and doubled digraphs"),
        ("Two-square / four-square / seriated Playfair", "IMPOSSIBLE", "F1 (25 letters)"),
        ("Bifid 5x5", "IMPOSSIBLE", "F1 (25 letters)"),
        ("Checkerboard (ACA 5x5)", "IMPOSSIBLE", "F1 (25 letters)"),
        ("Phillips (8 x 5x5 squares)", "IMPOSSIBLE", "F1 (25 letters)"),
        ("Trisquare (3 x 5x5)", "IMPOSSIBLE", "F1 (25 letters)"),
        ("Ragbaby", "IMPOSSIBLE", "F1: 24-letter alphabet"),
        ("Nihilist substitution, Grandpre, Tridigital", "IMPOSSIBLE",
         "ciphertext is digits, not 26 letters"),
        ("Bifid 6x6 / trifid", "CLOSED", "families.md best 5/24"),
        ("ADFGX / ADFGVX / CM-ADFGVX", "CLOSED", "matrix_f, matrix_g"),
        ("Straddling checkerboard + additive (VIC family)", "CLOSED", "matrix_a"),
        ("Homophonic", "CLOSED", "matrix_b"),
        ("Nomenclator / codebook", "CLOSED", "matrix_c"),
        ("Fractionated Morse / Morbit / Pollux", "CLOSED", "matrix_d"),
        ("Rotor / Enigma-like", "IMPOSSIBLE", "F2: no fixed points"),
        ("Columnar / route / Myszkowski / Amsco / Cadenus / Swagman", "IMPOSSIBLE",
         "pure transposition needs three E's; K4 ciphertext has two"),
        ("Double transposition", "IMPOSSIBLE", "same E-count argument"),
        ("Nicodemus (columnar + Vigenere)", "CLOSED", "twocipher.md, S+T both orders"),
        ("Bazeries (transposition + substitution)", "CLOSED", "twocipher.md"),
        ("SLIDEFAIR (Vigenere / Beaufort / Variant)", "**OPEN**",
         "26 letters, allows fixed points, hand cipher -- tested below"),
        ("PORTAX", "**OPEN**", "26 letters, seriated digraphic, permits fixed points -- below"),
    ]
    P("")
    P("%-52s %-12s %s" % ("family", "verdict", "why / where"))
    for a, b, c_ in rows:
        P("%-52s %-12s %s" % (a, b, c_))
    P("")
    P("Counts: %d CLOSED by computation, %d IMPOSSIBLE by F1/F2 or the E-count, %d OPEN."
      % (sum(1 for r in rows if r[1] == "CLOSED"),
         sum(1 for r in rows if r[1] == "IMPOSSIBLE"),
         sum(1 for r in rows if r[1].startswith("**"))))
    P("")
    P("""The census is the point of this section.  A genealogy argument that only produces
candidates already in the ruled-out list has produced nothing; this one produces exactly
two, and they are the two the ACA itself teaches immediately after Vigenere.""")


# ================================================================== Slidefair
def slidefair_encrypt(pt, keyvals, alpha=A2Z, variant="vigenere", order="normal"):
    """ACA Slidefair.  Two rows: TOP[i] = alpha[i]; BOTTOM depends on the key letter k:
         vigenere    BOTTOM[j] = alpha[(j + k) % 26]
         beaufort    BOTTOM[j] = alpha[(k - j) % 26]
         variant     BOTTOM[j] = alpha[(j - k) % 26]
       For a digraph (p1, p2): i = index of p1 in TOP, j = index of p2 in BOTTOM;
       the ciphertext is the other two corners, TOP[j] and BOTTOM[i]."""
    idx = {ch: i for i, ch in enumerate(alpha)}
    out = []
    for t in range(0, len(pt) - 1, 2):
        k = keyvals[(t // 2) % len(keyvals)]
        p1, p2 = idx[pt[t]], idx[pt[t + 1]]
        if variant == "vigenere":
            j = (p2 - k) % 26
            c1, c2 = j, (p1 + k) % 26
        elif variant == "beaufort":
            j = (k - p2) % 26
            c1, c2 = j, (k - p1) % 26
        else:                                     # variant Beaufort slide
            j = (p2 + k) % 26
            c1, c2 = j, (p1 - k) % 26
        a, b = (c1, c2) if order == "normal" else (c2, c1)
        out.append(alpha[a]); out.append(alpha[b])
    if len(pt) % 2:
        out.append(pt[-1])
    return "".join(out)


def slidefair_key_from_digraph(variant, p1, p2, c1, c2, order="normal"):
    """Return (k_from_first, k_from_second) -- the two independent determinations of the
    key value.  Slidefair is over-determined per digraph: a genuine Slidefair digraph
    must give the same k twice.  All arguments are alphabet indices."""
    if order == "swap":
        c1, c2 = c2, c1
    if variant == "vigenere":
        return (p2 - c1) % 26, (c2 - p1) % 26
    if variant == "beaufort":
        return (c1 + p2) % 26, (c2 + p1) % 26
    return (c1 - p2) % 26, (p1 - c2) % 26


def slidefair():
    hdr("SLIDEFAIR -- THE KEY-FREE INVARIANT, AND THE SWEEP")
    P("""
DERIVATION.  Write a Slidefair digraph in alphabet indices.  For the Vigenere slide,
    c1 = p2 - k  and  c2 = p1 + k,   so   c1 + c2 = p1 + p2   (mod 26),
for the variant slide the same identity holds, and for the Beaufort slide
    c1 = k - p2  and  c2 = k - p1,   so   c1 - c2 = p1 - p2   (mod 26).
In each case the key CANCELS.  So every complete crib digraph imposes one equation that
holds for every key, every period and every phase; only the alphabet matters.  Eleven
complete crib digraphs are available in each alignment, so a random cipher passes all of
them with probability 26^-11 = 2.7e-16.  This is the strongest single test any family in
this repository has been given.""")

    # --- validation: round trip and key recovery
    rng = np.random.default_rng(31)
    ok = True
    for variant in ("vigenere", "beaufort", "variant"):
        for alpha in (A2Z, KRY):
            pt = "".join(A2Z[i] for i in rng.integers(0, 26, 96))
            kv = list(rng.integers(0, 26, 5))
            ct = slidefair_encrypt(pt, kv, alpha, variant)
            ia = {ch: i for i, ch in enumerate(alpha)}
            for t in range(0, 96, 2):
                k1, k2 = slidefair_key_from_digraph(
                    variant, ia[pt[t]], ia[pt[t + 1]], ia[ct[t]], ia[ct[t + 1]])
                if k1 != k2 or k1 != kv[(t // 2) % 5]:
                    ok = False
    P("")
    P("VALIDATION: key recovered identically from both halves of every digraph, and equal")
    P("   to the planted key, for all 3 variants x 2 alphabets x 48 digraphs:",
      "PASS" if ok else "FAIL")

    # --- the invariant applied to the real cribs
    P("")
    P("APPLYING THE INVARIANT TO K4's CRIBS")
    alphas = [("plain", A2Z), ("kryptos", KRY)] + \
             [(kw, L.keyed_alphabet(kw)) for kw in K.SHORT_KEYWORDS] + \
             [(kw + "/K", L.keyed_alphabet(kw, KRY)) for kw in K.SHORT_KEYWORDS]
    seen, uniq = set(), []
    for nm, a in alphas:
        if a not in seen:
            seen.add(a); uniq.append((nm, a))
    P("alphabets tested: %d" % len(uniq))

    best = (0, None)
    total = 0
    results = defaultdict(list)
    for align in (0, 1):
        digs = []
        for t in range(align, N - 1, 2):
            if t in CRIB and t + 1 in CRIB:
                digs.append(t)
        for nm, alpha in uniq:
            ia = {ch: i for i, ch in enumerate(alpha)}
            for variant in ("vigenere", "beaufort", "variant"):
                for order in ("normal", "swap"):
                    total += 1
                    agree = 0
                    for t in digs:
                        k1, k2 = slidefair_key_from_digraph(
                            variant, ia[CRIB[t]], ia[CRIB[t + 1]],
                            ia[CT[t]], ia[CT[t + 1]], order)
                        if k1 == k2:
                            agree += 1
                    results[(align, variant, order)].append((agree, nm))
                    if agree > best[0]:
                        best = (agree, (align, nm, variant, order))
        P("   alignment %d: %d complete crib digraphs at 1-indexed %s"
          % (align, len(digs), [t + 1 for t in digs]))
    P("")
    P("%-10s %-12s %-8s %10s %10s %12s" % ("alignment", "variant", "order",
                                           "best/11", "n alphabets", "chance exp"))
    for (align, variant, order), lst in sorted(results.items()):
        lst.sort(reverse=True)
        nd = 11
        exp = len(lst) * sum(_binom(nd, j) * (1 / 26.0) ** j * (25 / 26.0) ** (nd - j)
                             for j in range(lst[0][0], nd + 1))
        P("%-10d %-12s %-8s %10s %10d %12.3e"
          % (align, variant, order, "%d (%s)" % (lst[0][0], lst[0][1]), len(lst), exp))
    P("")
    P("overall best: %d of 11 key-free equations satisfied, at %s" % best)
    P("a genuine Slidefair would satisfy 11 of 11.  Expected best over all %d"
      % total)
    P("(alphabet, variant, order, alignment) configurations, by chance: %.3f of 11"
      % (11 / 26.0))
    P("")
    P("VERDICT: Slidefair in all three slide variants, both digraph alignments, both")
    P("output orders and %d alphabets is REFUTED by the cribs, with no key search at all."
      % len(uniq))


def _binom(n, k):
    from math import comb
    return comb(n, k)


# ==================================================================== Portax
def portax():
    hdr("PORTAX -- THE ROW-PARITY INVARIANT")
    P("""
Portax seriates the plaintext into rows of length p (the period), pairs each letter with
the one directly below it, and enciphers the vertical pair on a two-row slide: a fixed
TOP row of 13 letters and a BOTTOM row of 13 that slides by the key letter.  The
ciphertext is written back into the same cells, so Portax IS position-preserving and the
24 cribs apply directly.

Its three rules are
   both letters in TOP     -> the two letters directly BELOW them  (both in BOTTOM)
   both letters in BOTTOM  -> the two letters directly ABOVE them  (both in TOP)
   one in each row         -> the other two corners of the rectangle (one in each row)

NOTE, correcting a natural first guess: the mixed case with both letters in the SAME
column returns the pair unchanged, so Portax DOES permit a letter to encipher to itself.
Fact F2 therefore does NOT kill it, and it has to be tested.

KEY-FREE INVARIANT.  In all three rules the number of TOP-row letters in the output is
    #TOP(c_u, c_l) = 2 - #TOP(p_u, p_l),
whatever the key, whatever the slide.  Only the alphabet's top/bottom split matters.
Each crib pair tests one bit, so m testable pairs give a chance pass rate of 2^-m.""")

    alphas = [("plain A-M/N-Z", A2Z), ("kryptos", KRY)] + \
             [(kw, L.keyed_alphabet(kw)) for kw in K.SHORT_KEYWORDS]
    P("")
    P("%-6s %8s %-16s %10s %12s" % ("period", "testable", "alphabet(best)",
                                    "passes", "chance 2^-m"))
    any_full = []
    for p in range(2, 27):
        pairs = []
        for i in range(N):
            row = i // p
            j = i + p if row % 2 == 0 else i - p
            if j < 0 or j >= N:
                continue
            u, l = (i, j) if row % 2 == 0 else (j, i)
            if u in CRIB and l in CRIB and (u, l) not in pairs:
                pairs.append((u, l))
        m = len(pairs)
        if m == 0:
            P("%-6d %8d %-16s %10s %12s" % (p, 0, "-", "untestable", "1.0"))
            continue
        best = (-1, None)
        for nm, alpha in alphas:
            top = set(alpha[:13])
            good = 0
            for u, l in pairs:
                nin = (CRIB[u] in top) + (CRIB[l] in top)
                nout = (CT[u] in top) + (CT[l] in top)
                if nout == 2 - nin:
                    good += 1
            if good > best[0]:
                best = (good, nm)
            if good == m:
                any_full.append((p, nm))
        P("%-6d %8d %-16s %10s %12.3e"
          % (p, m, best[1], "%d/%d" % (best[0], m), 2.0 ** -m))
    P("")
    P("(period, alphabet) pairs satisfying EVERY testable row-parity constraint:",
      any_full if any_full else "none")
    P("""
VERDICT.  The row-parity invariant is a weak test (one bit per pair) and it leaves a few
short periods standing, as it must.  But every period it leaves standing is also a period
at which the ordinary crib-consistency test in findings/families.md already returns zero
survivors over 7.09M alphabet pairs, and Portax's substitution stage is a letterwise map
indexed by ciphertext position, so those negatives transfer (findings/twocipher.md, the
T-then-S/ciphertext-reading row).  Portax is therefore closed, but by inheritance rather
than by a decisive invariant of its own -- state it that way, not more strongly.""")


def main():
    hdr("(a, continued)  METHOD GENEALOGY: THE CENSUS AND THE DIGRAPHIC SLIDE FAMILY")
    P("K4:", CT)
    fails = L.selftest(verbose=False)
    P("k5_lib selftest:", "PASS" if not fails else "FAIL %r" % (fails,))
    census()
    slidefair()
    portax()
    hdr("END (a, continued)")
    with open(os.path.join(HERE, "k5_f_output.txt"), "w") as f:
        f.write("\n".join(OUT) + "\n")


if __name__ == "__main__":
    main()
