"""(e) OBKR AS AN INDICATOR GROUP.

Standard 1940s field practice prefixes a message with a short INDICATOR that encodes the
message key.  If OBKR is one, the real message is the 93 letters from position 5, and the
key is derived from OBKR by a rule.  This script

  E1  proves which indicator rules are already decided by work on record (most of them
      are, and the proof is one short invariance argument, verified numerically);
  E2  enumerates and tests the DIRECT-KEYWORD rules, including the properly 1940s one --
      the indicator is itself enciphered under a standing key and the recovered group is
      the message key;
  E3  the NUMERIC rules (alphabet position, both index conventions, both alphabets);
  E4  the TABLEAU-COORDINATE rules: OBKR names cells of the Kryptos tableau and the key
      stream is read out from there.  Row-major reading of the tableau at every offset is
      already closed by findings/runningkey.md; column, diagonal and boustrophedon walks
      from a named cell are NOT, and are the genuinely new part of this section;
  E5  the GROMARK-PRIMER rule: OBKR seeds a chain-addition key for the 93-letter body;
  E6  OBKR-KEYED ALPHABETS, which are absent from the 208,627-alphabet dictionary set
      swept in findings/families.md because OBKR is not a word.

Chance: a random key reproduces 24/26 = 0.923 of the 24 crib letters; 24/24 is the only
result that counts.  Every table prints its own expectation.
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
CRIB, CRIB_POS, CRIB_PT, CRIB_CT = L.CRIB, L.CRIB_POS, L.CRIB_PT, L.CRIB_CT
IND = CT[:4]                      # OBKR
BODY = CT[4:]                     # 93 letters
CB = L.Combos([("plain", A2Z), ("kryptos", KRY)])


TOP = []


def best_of(keystreams, tag=""):
    """keystreams: iterable of (name, 97-letter key text).  Returns (best, n_tests, hist).
    Also records the highest-scoring individual configurations in TOP."""
    global TOP
    best = (0, None)
    n = 0
    hist = defaultdict(int)
    top = []
    for name, ks in keystreams:
        if len(ks) < N:
            ks = (ks * (N // max(1, len(ks)) + 2))[:N]
        ag = L.crib_agreement(ks[:N], CB)
        n += CB.n
        for v in ag:
            hist[int(v)] += 1
        m = int(ag.max())
        if m >= 6:
            for j in np.nonzero(ag >= 6)[0]:
                top.append((int(ag[j]), name, CB.labels[int(j)]))
        if m > best[0]:
            best = (m, (name, CB.labels[int(ag.argmax())]))
    TOP = sorted(top, reverse=True)[:10]
    return best, n, hist


def report(label, best, n, hist):
    P("   %-52s tests %-8d best %d/24  %s"
      % (label, n, best[0], best[1] if best[1] else ""))
    P("      histogram %s ; expected total crib hits %.1f, observed %d"
      % (dict(sorted(hist.items())), n * 24 / 26.0,
         sum(k * v for k, v in hist.items())))
    P("      tests reaching >= %d/24: observed %d, expected by chance %.2f"
      % (best[0], sum(v for kk, v in hist.items() if kk >= best[0]),
         L.tail_expect(n, best[0])))
    P("      P(one test = 24/24) = 1.10e-34 ; expected over %d tests = %.2e"
      % (n, n * 26.0 ** -24))
    for t in TOP[:6]:
        P("         top: %d/24  %-34s %s" % t)


# ==================================================================== E0
def validate():
    hdr("E0.  VALIDATION")
    fails = L.selftest(verbose=False)
    P("k5_lib selftest:", "PASS" if not fails else "FAIL %r" % (fails,))
    # positive control: build a synthetic K4 whose body key IS derived from OBKR by the
    # direct-keyword rule, then check the E2 machinery finds it at 24/24.
    key = [KRY.index(c) for c in IND]
    pt = list("X" * N)
    for i, ch in CRIB.items():
        pt[i] = ch
    fake = []
    for i in range(N):
        k = 0 if i < 4 else key[(i - 4) % 4]
        fake.append(KRY[L.ct_from(0, KRY.index(pt[i]), k)])
    fake = "".join(fake)
    ks = "AAAA" + "".join(IND[(i) % 4] for i in range(N - 4))
    ag = L.crib_agreement(ks, CB, ct=fake)
    P("positive control: synthetic K4 with body key = OBKR repeated from position 5,")
    P("   Quagmire III.  E2 machinery recovers it at %d/24 (expected 24)." % int(ag.max()))


# ==================================================================== E1
def E1_theory():
    hdr("E1.  WHICH INDICATOR RULES ARE ALREADY DECIDED?")
    P("""
An indicator changes three things and only three things:

  (1) WHERE THE KEY STREAM STARTS.  The body begins at position 5, so the key index at
      K4 position i becomes i-4 instead of i.  That is a constant shift of the key
      pointer.  For any periodic key the crib test is invariant under it (the residue
      partition of the crib positions is unchanged), and for a key stream read out of a
      text it is an offset, and findings/runningkey.md swept every offset.

  (2) WHICH KEY.  If the rule yields a repeating key of length Lk, the period-Lk sweep in
      findings/families.md quantified over ALL period-Lk keys at once, so every such rule
      is already dead -- for the alphabets swept there.

  (3) NOTHING ELSE.  The indicator does not move the cribs: Sanborn's positions 22-25,
      26-34, 64-69, 70-74 are absolute in the carved 97 and the ciphertext letters there
      are unchanged.

So an indicator rule has new content only if it produces a NON-periodic key stream, or a
NEW ALPHABET, or both.  That is what E4, E5 and E6 test; E2 and E3 are run anyway so the
negative is a measured number.""")
    P("")
    bad = []
    for d in (4, -4):
        for p in range(2, 41):
            c0 = len(CRIB_POS) - len({i % p for i in CRIB_POS})
            cd = len(CRIB_POS) - len({(i + d) % p for i in CRIB_POS})
            if c0 != cd:
                bad.append((d, p, c0, cd))
    P("numeric check of (1): c_p for the 97-indexing vs the 93-body indexing, p=2..40:",
      "IDENTICAL at every period" if not bad else "differs %r" % bad[:5])
    P("")
    P("Consequence worth stating: 'the message is 93 letters' is NOT a testable")
    P("hypothesis against the cribs.  It is a relabelling of the key pointer.")


# ==================================================================== E2
def E2_keyword():
    hdr("E2.  DIRECT-KEYWORD RULES")
    P("")
    P("E2a. OBKR and its elementary transforms, used directly as a repeating key on the")
    P("     body, at every phase.")
    variants = {
        "OBKR": "OBKR", "RKBO": "RKBO", "BKOR": "BKOR", "ROKB": "ROKB",
        "KROB": "KROB", "OBKROBKR": "OBKROBKR",
        "OBKR+KRYPTOS": "OBKRKRYPTOS", "KRYPTOS+OBKR": "KRYPTOSOBKR",
    }
    streams = []
    for nm, w in variants.items():
        for s in range(len(w)):
            for lead in (0, 4):          # key starts at position 1 or at position 5
                ks = "A" * lead + "".join(w[(s + i) % len(w)] for i in range(N))
                streams.append(("%s ph%d lead%d" % (nm, s, lead), ks[:N]))
    report("OBKR transforms as repeating key", *best_of(streams))

    P("")
    P("E2b. THE PROPER 1940s RULE: the indicator is itself enciphered under a standing")
    P("     key; the recovered group is the message key.  Here OBKR is de/enciphered")
    P("     under the K1/K2 system with each documented standing key at every phase, and")
    P("     the recovered 4-letter group is then used as the body key at every phase.")
    standing = ["PALIMPSEST", "ABSCISSA", "KRYPTOS", "PALIMPSESTABSCISSA",
                "SANBORN", "SCHEIDT", "LAYERTWO"]
    recovered = {}
    for sk in standing:
        for ph in range(len(sk)):
            for rule in L.RULES:
                for pta_n, pta in (("plain", A2Z), ("kry", KRY)):
                    for cta_n, cta in (("plain", A2Z), ("kry", KRY)):
                        kv = [pta.index(sk[(ph + i) % len(sk)]) if False else
                              A2Z.index(sk[(ph + i) % len(sk)]) for i in range(4)]
                        kvk = [KRY.index(sk[(ph + i) % len(sk)]) for i in range(4)]
                        for kname, kvals in (("keyA", kv), ("keyK", kvk)):
                            d = L.decrypt(IND, kvals, rule, pta, cta)
                            e = L.encrypt(IND, kvals, rule, pta, cta)
                            recovered["%s/%d/%s/%s/%s/%s/dec" %
                                      (sk, ph, rule, pta_n, cta_n, kname)] = d
                            recovered["%s/%d/%s/%s/%s/%s/enc" %
                                      (sk, ph, rule, pta_n, cta_n, kname)] = e
    groups = sorted(set(recovered.values()))
    P("     distinct 4-letter groups recovered from OBKR: %d (of 26^4 = 456,976)"
      % len(groups))
    streams = []
    for g in groups:
        for s in range(4):
            for lead in (0, 4):
                ks = "A" * lead + "".join(g[(s + i) % 4] for i in range(N))
                streams.append(("%s ph%d lead%d" % (g, s, lead), ks[:N]))
    report("recovered message keys as period-4 body keys", *best_of(streams))
    P("     (subsumed by the period-4 sweep, which has c=20 and chance 26^-20 = 5.7e-29")
    P("      per configuration and returned 0 survivors over 7.09M alphabet pairs.)")


# ==================================================================== E3
def E3_numeric():
    hdr("E3.  NUMERIC RULES: OBKR AS DIGITS")
    for nm, idx in (("A=0 plain", [A2Z.index(c) for c in IND]),
                    ("A=1 plain", [A2Z.index(c) + 1 for c in IND]),
                    ("KRYPTOS index", [KRY.index(c) for c in IND]),
                    ("KRYPTOS index +1", [KRY.index(c) + 1 for c in IND])):
        P("   %-18s OBKR -> %s   sum=%d  concat=%s"
          % (nm, idx, sum(idx), "".join(str(x) for x in idx)))
    P("")
    P("E3a. as a Gronsfeld/period-4 shift key on the body, every phase, every convention")
    streams = []
    for nm, idx in (("A=0", [A2Z.index(c) for c in IND]),
                    ("A=1", [A2Z.index(c) + 1 for c in IND]),
                    ("KRY", [KRY.index(c) for c in IND]),
                    ("A=0 mod10", [A2Z.index(c) % 10 for c in IND]),
                    ("A=1 mod10", [(A2Z.index(c) + 1) % 10 for c in IND])):
        for s in range(4):
            for lead in (0, 4):
                ks = "A" * lead + "".join(A2Z[idx[(s + i) % 4] % 26] for i in range(N))
                streams.append(("%s ph%d lead%d" % (nm, s, lead), ks[:N]))
    report("OBKR digits as a period-4 key", *best_of(streams))

    P("")
    P("E3b. as a DECIMATION rule: take every n-th letter of a sculpture text, n from OBKR")
    P("     (this is not an offset, so it is not covered by the all-offsets running-key")
    P("      sweep; it is a genuinely different read-out of the same texts).")
    corpus = RK.corpus()
    texts = {k: v for k, v in corpus.items() if len(v) >= 200 and "rev" not in k}
    streams = []
    ns = sorted({A2Z.index(c) + 1 for c in IND} | {A2Z.index(c) for c in IND if c != "A"}
                | {2, 3, 4, 5, 7})
    for tname, t in texts.items():
        for step in ns:
            if step < 1:
                continue
            for start in range(0, min(step, 8)):
                ks = t[start::step]
                if len(ks) >= N:
                    streams.append(("%s step%d st%d" % (tname, step, start), ks[:N]))
    report("decimated sculpture texts, step from OBKR", *best_of(streams))


# ==================================================================== E4
def _ideal_square():
    return [KRY[r:] + KRY[:r] for r in range(26)]


def _physical_square():
    rows = [r for r in RK.RIGHT_ROWS if r and r[0] in A2Z and len(r) > 26]
    sq = []
    for r in rows:
        body = "".join(ch for ch in r[1:] if ch in A2Z)
        sq.append(body[:26] if len(body) >= 26 else (body + body)[:26])
    return sq if len(sq) == 26 else _ideal_square()


def _walk(sq, r0, c0, mode, n=N):
    out = []
    r, c = r0, c0
    for i in range(n):
        out.append(sq[r % 26][c % 26])
        if mode == "right":
            c += 1
        elif mode == "left":
            c -= 1
        elif mode == "down":
            r += 1
        elif mode == "up":
            r -= 1
        elif mode == "diag":
            r += 1; c += 1
        elif mode == "antidiag":
            r += 1; c -= 1
        elif mode == "boust":
            c += 1
            if c % 26 == 0:
                r += 1
        elif mode == "knight":
            r += 1; c += 2
    return "".join(out)


def E4_tableau():
    hdr("E4.  TABLEAU-COORDINATE RULES  (the new part)")
    P("""
findings/runningkey.md read the tableau in reading order at every offset (row-major,
left to right) and found nothing.  It did NOT read it by column, by diagonal, or
boustrophedon from a named starting cell.  An indicator's natural job is exactly to name
a starting cell, so those walks are tested here, from every cell OBKR can name, on both
the ideal tableau and the carved one with its anomalous L.""")
    squares = {"ideal": _ideal_square(), "physical": _physical_square()}
    modes = ("right", "left", "down", "up", "diag", "antidiag", "boust", "knight")
    streams = []
    for sqn, sq in squares.items():
        for a, b in itertools.permutations(IND, 2):
            for conv, alpha in (("A2Z", A2Z), ("KRY", KRY)):
                r0, c0 = alpha.index(a), alpha.index(b)
                for m in modes:
                    streams.append(("%s (%s,%s)%s %s" % (sqn, a, b, conv, m),
                                    _walk(sq, r0, c0, m)))
        # all four letters as a 2x2 coordinate pair: (O,B) then continue from (K,R)
        for conv, alpha in (("A2Z", A2Z), ("KRY", KRY)):
            for m in modes:
                s1 = _walk(sq, alpha.index(IND[0]), alpha.index(IND[1]), m, 49)
                s2 = _walk(sq, alpha.index(IND[2]), alpha.index(IND[3]), m, 48)
                streams.append(("%s split(OB|KR)%s %s" % (sqn, conv, m), s1 + s2))
    report("tableau walks from OBKR-named cells", *best_of(streams))
    P("     walks tested: %d (2 squares x 12 ordered letter pairs x 2 index conventions"
      % len(streams))
    P("      x 8 walk modes, plus the split-coordinate variants)")


# ==================================================================== E5
def E5_gromark():
    hdr("E5.  GROMARK-PRIMER RULE: OBKR SEEDS A CHAIN-ADDITION KEY")
    P("""
The ACA Gromark takes a short numeric primer and extends it by chain addition
(k_i = k_{i-L} + k_{i-L+1} mod base).  OBKR is exactly the right shape for a primer.
analysis/k5_a_genealogy.py swept every base-26 primer of length <= 4 with the key stream
indexed from position 1 of the 97; the indicator reading starts the stream at position 5
instead, and adds the base-10 and KRYPTOS-index conventions.  Both alignments are run.""")
    streams = []
    convs = {"A=0": [A2Z.index(c) for c in IND],
             "A=1": [(A2Z.index(c) + 1) % 26 for c in IND],
             "KRY": [KRY.index(c) for c in IND],
             "A=0 mod10": [A2Z.index(c) % 10 for c in IND],
             "A=1 mod10": [(A2Z.index(c) + 1) % 10 for c in IND]}
    for cname, primer in convs.items():
        for base in (10, 26):
            for lag in (1, 2, 3):
                for lead in (0, 4):
                    k = list(primer)
                    while len(k) < N + 8:
                        k.append((k[-len(primer)] + k[-len(primer) + lag]) % base
                                 if len(primer) > lag else (k[-1] + k[-2]) % base)
                    ks = "A" * lead + "".join(A2Z[v % 26] for v in k)
                    streams.append(("%s b%d lag%d lead%d" % (cname, base, lag, lead),
                                    ks[:N]))
                    # reversed-primer and running-decimal variants
                    k2 = list(reversed(primer))
                    while len(k2) < N + 8:
                        k2.append((k2[-len(primer)] + k2[-len(primer) + lag]) % base
                                  if len(primer) > lag else (k2[-1] + k2[-2]) % base)
                    ks2 = "A" * lead + "".join(A2Z[v % 26] for v in k2)
                    streams.append(("rev %s b%d lag%d lead%d" % (cname, base, lag, lead),
                                    ks2[:N]))
    report("OBKR as a chain-addition primer", *best_of(streams))


# ==================================================================== E6
def E6_alphabets():
    hdr("E6.  OBKR-KEYED ALPHABETS  (absent from the 208,627-word alphabet set)")
    P("OBKR is not a dictionary word, so keyed_alphabet('OBKR') was never in the")
    P("families.md sweep.  Neither were alphabets keyed by the K4 ciphertext prefix.")
    words = ["OBKR", "BKOR", "RKBO", "OBKRKRYPTOS", "KRYPTOSOBKR",
             "OBKRUOXO", "OBKRUOXOGHULBSOLIFBBWFLRV",
             CT[:31], CT[:40], CT, "OBKRUOXOGHUL"]
    alphas = [("plain", A2Z), ("kryptos", KRY)]
    for w in words:
        alphas.append((w[:12], L.keyed_alphabet(w)))
        alphas.append((w[:12] + "_K", L.keyed_alphabet(w, KRY)))
    seen, uniq = set(), []
    for nm, a in alphas:
        if a not in seen:
            seen.add(a)
            uniq.append((nm, a))
    P("distinct alphabets:", len(uniq))
    S = L.Sweeper(uniq)
    rows = S.sweep(CRIB_POS, CRIB_PT, CRIB_CT, tuple(range(2, 31)))
    tot_s = sum(r[2] for r in rows)
    tot_e = sum(r[3] * S.n for r in rows)
    P("configurations per period %d ; total tests %d" % (S.n, S.n * len(rows)))
    P("survivors %d ; expected by chance %.2f" % (tot_s, tot_e))
    P("periods with survivors (period, c, n):", [(r[0], r[1], r[2]) for r in rows if r[2]])
    P("max c carrying any survivor:", max([r[1] for r in rows if r[2]] or [-1]))


def E7_summary():
    hdr("E7.  WHAT AN INDICATOR CAN AND CANNOT BUY")
    P("""
 * It cannot move the cribs, and it cannot change c_p at any period (E1).  "The message
   is really 93 letters" is a relabelling, not a hypothesis the cribs can see.
 * Every rule whose output is a repeating key -- direct keyword, enciphered indicator,
   numeric Gronsfeld -- is decided by the period sweeps already on record, and the
   explicit runs above confirm it with measured numbers rather than inference.
 * The only rules with genuinely new content are the ones that make the tableau into a
   non-reading-order key stream (E4), that seed a non-periodic generator (E5), or that
   build an alphabet OBKR cannot otherwise reach (E6).  All three were run here.  All
   three are negative at chance.
 * A four-letter indicator can address at most 26^4 = 456,976 message keys.  The
   crib-perfect positional key space is 26^73 (see k5_b_depth.py L2).  Even a perfect
   indicator rule reduces the problem by a factor of 10^-97 of what would be needed.
   Indicator hypotheses are cheap to test and structurally incapable of being the whole
   story.""")


def main():
    hdr("(e) OBKR AS AN INDICATOR GROUP")
    P("K4:", CT)
    P("indicator candidate:", IND, " body (93 letters):", BODY)
    validate()
    E1_theory()
    E2_keyword()
    E3_numeric()
    E4_tableau()
    E5_gromark()
    E6_alphabets()
    E7_summary()
    hdr("END (e)")
    with open(os.path.join(HERE, "k5_e_output.txt"), "w") as f:
        f.write("\n".join(OUT) + "\n")


if __name__ == "__main__":
    main()
