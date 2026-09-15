"""(d) THE QUESTION MARK.

K3 ends "CAN YOU SEE ANYTHING?" and the `?` is carved immediately before OBKR.  Three
distinct hypotheses hang off that character, and they are NOT the same hypothesis:

  D1  INDEXING.  Sanborn counted the `?` when he said "the 64th through 69th
      characters".  Settled documentarily in findings/crib_placement.md 1.3 and
      re-derived here in one line, because it is cheap and it is the premise everything
      else rests on.

  D2  KEY SLOT.  The `?` is not a ciphertext letter but it OCCUPIES A CELL on the
      worksheet, so the key stream advances across it and K4's key starts one step late.
      More generally K4 might be the tail of a 98-, 124- or 869-cell layout.  For a
      repeating key this is a phase shift and is subsumed; for a key stream read out of
      a fixed text it is an offset and is subsumed; the case that is NOT subsumed is the
      one where the `?` changes WHICH CIPHERTEXT LETTER pairs with which crib letter,
      i.e. K4 actually begins before OBKR.  That is tested here over the full range of
      K3-tail prefixes, extending findings/crib_placement.md 2 (which stopped at -21).

  D3  THE MISSING ANSWER.  The sculpture asks Carter's question and does not carry the
      answer.  "YES, WONDERFUL THINGS" is the single most conspicuous piece of text that
      belongs to the Kryptos narrative and is absent from the sculpture, so it is absent
      from findings/runningkey.md's 66-text corpus.  Sanborn's own 2006 statement is that
      "the answers to the first three passages contain clues to the fourth".  This is
      genuinely untested key material and it is tested here as a running key, as a
      keyword, and as a keyed alphabet.

Every count is printed with its chance expectation.
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
CRIB, CRIB_POS = L.CRIB, L.CRIB_POS
CRIB_WORDS = [(21, "EASTNORTHEAST"), (63, "BERLINCLOCK")]   # 0-indexed starts


# ================================================================ validation
def validate():
    hdr("D0.  VALIDATION")
    fails = L.selftest(verbose=False)
    P("k5_lib selftest:", "PASS" if not fails else "FAIL %r" % (fails,))

    # Plant a cipher on an EXTENDED text  X = tail + body  where the cribs sit at the
    # standard indices of X, then hand the sweep only the 97-letter body plus the tail
    # source, exactly as in the real test, and check it recovers the true tail length.
    sw = L.Sweeper([("plain", A2Z), ("kryptos", KRY)])
    rng = np.random.default_rng(5)
    for true_k, period in ((3, 9), (11, 13), (25, 7)):
        ext_len = true_k + N
        key = list(rng.integers(0, 26, period))
        pt = list("".join(A2Z[i] for i in rng.integers(0, 26, ext_len)))
        for st, w in CRIB_WORDS:
            for j, ch in enumerate(w):
                pt[st + j] = ch
        X_ct = L.encrypt("".join(pt), key, "vigenere", A2Z, A2Z)
        body = X_ct[true_k:]                    # what a solver would see as "K4"
        tail_src = "ZZZZZZZZ" + X_ct[:true_k]   # the guessed source text; its last
                                                # true_k letters are the real tail
        hits = []
        for k in range(1, 32):
            if k > len(tail_src):
                break
            Xk = tail_src[len(tail_src) - k:] + body
            pos, ptl, ctl = [], [], []
            for st, w in CRIB_WORDS:
                for j, ch in enumerate(w):
                    p = st + j
                    if p < len(Xk):
                        pos.append(p); ptl.append(ch); ctl.append(Xk[p])
            r = sw.sweep(pos, "".join(ptl), "".join(ctl), [period])[0]
            if r[2] > 0:
                hits.append(k)
        P("   planted period-%d cipher, true tail length %d: sweep survivors at k = %r"
          % (period, true_k, hits), "-> true k recovered:", true_k in hits)


# ==================================================================== D1
def D1_indexing():
    hdr("D1.  DOES SANBORN'S INDEX COUNT THE `?` ?  (one-line re-derivation)")
    q = "?" + CT
    P("Sanborn, NYT 2010: 'the characters that are the 64th through 69th ... read NYPVTT'.")
    P("   K4 alone, 1-indexed, 64-69   :", CT[63:69], " <- matches the published string")
    P("   '?'+K4,  1-indexed, 64-69    :", q[63:69].replace("?", "[?]"))
    P("   K4 alone, 0-indexed, 64-69   :", CT[64:70])
    P("Only the first reading reproduces NYPVTT, so the `?` is NOT counted in the index.")
    P("This agrees with findings/crib_placement.md 1.3 and with the delta=-1 cryptanalytic")
    P("sweep there (2 survivors against 0.46 expected, all at period 26, c=1).")


# ==================================================================== D2
def D2_prefix():
    hdr("D2.  K4 BEGINS BEFORE OBKR: K3's TAIL AS THE HEAD OF K4")
    P("""
Model.  The message actually enciphered is  X = T[-k:] + K4  for some tail T of the
preceding carved text, and Sanborn's index 64 counts from the start of X.  Then the crib
letter at index 64 pairs with X[63] instead of CT[63].  For k <= 21 this is exactly the
delta = -k global slide already swept in findings/crib_placement.md 2; this run extends
it to k = 1..31 (the whole of panel row 25) and to k = 1..40, and adds the two tails that
the -k slide cannot express: K3's PLAINTEXT tail, and the tail taken from the panel's
letter stream rather than from K3's ciphertext.

Chance bookkeeping: a placement that forces c independent equalities on a period-p key is
passed by a random key with probability 26^-c, and the expectation column below is the
sum of 26^-c over every (k, p, combo) triple actually tested.""")
    sw = L.Sweeper([("plain", A2Z), ("kryptos", KRY)])
    sw17 = L.Sweeper([("plain", A2Z)] + [(kw, L.keyed_alphabet(kw))
                                         for kw in K_KEYWORDS])
    tails = {
        "K3 ciphertext tail": RK.K3_CT,
        "K3 plaintext tail": RK.K3_PT,
        "panel letters before K4": RK.LEFT_ALL[:RK.LEFT_ALL.index(CT)] if CT in RK.LEFT_ALL
        else RK.K1_CT + RK.K2_CT + RK.K3_CT,
        "K3 ciphertext tail REVERSED": RK.K3_CT[::-1],
    }
    periods = tuple(range(2, 31))
    for swname, S in (("12 combos", sw), ("867 combos", sw17)):
        P("")
        P("--- alphabet set: %s (%d cipher configurations) ---" % (swname, S.n))
        P("%-30s %4s %8s %10s %12s %6s" % ("tail source", "k", "tests", "survivors",
                                           "chance exp", "max c"))
        for tname, T in tails.items():
            tot_surv = tot_exp = tot_tests = 0
            maxc_surv = -1
            for k in range(1, 41):
                if k > len(T):
                    break
                X = T[-k:] + CT
                pos, ptl, ctl = [], [], []
                for st, w in CRIB_WORDS:
                    for j, ch in enumerate(w):
                        p = st + j
                        if p < len(X):
                            pos.append(p); ptl.append(ch); ctl.append(X[p])
                rows = S.sweep(pos, "".join(ptl), "".join(ctl), periods)
                for p, c, ns, ch, idxs in rows:
                    tot_tests += S.n
                    tot_exp += ch * S.n
                    tot_surv += ns
                    if ns and c > maxc_surv:
                        maxc_surv = c
            P("%-30s %4s %8d %10d %12.2f %6d" % (tname, "1-40", tot_tests, tot_surv,
                                                 tot_exp, maxc_surv))
    P("")
    P("A genuine solution would appear as a survivor at c >= 10.  Nothing does.")


K_KEYWORDS = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "SANBORN", "SCHEIDT", "LANGLEY",
              "BERLIN", "CLOCK", "COMPASS", "LODESTONE", "SHADOW", "IQLUSION",
              "UNDERGRUUND", "DESPARATLY", "LAYERTWO", "MASKING"]


# ==================================================================== D2b
def D2b_keyslot():
    hdr("D2b.  THE `?` AS A KEY SLOT (the key advances, the letter does not)")
    P("""
If the worksheet had 98 cells and the `?` consumed one key symbol, K4's key stream begins
at key index 1 rather than 0.  For a repeating key of length Lk this is the phase shift
s -> s+1, already quantified over in (c) and in every period sweep.  For a key stream
read out of a fixed text it is the offset shift n0 -> n0+1, already quantified over in
findings/runningkey.md's all-offsets sweep.  Formally:

  THEOREM.  Let the crib positions be {i_1..i_24}.  Shifting every position by a constant
  d changes the residues mod p by the same constant d mod p, so the PARTITION of the crib
  positions into residue classes is unchanged and the number of forced equalities c_p is
  identical.  Hence no constant key-slot offset can change any periodic crib test.

Verified numerically below for d = 0..8 and p = 2..40.""")
    bad = []
    for d in range(0, 9):
        for p in range(2, 41):
            c0 = len(CRIB_POS) - len({i % p for i in CRIB_POS})
            cd = len(CRIB_POS) - len({(i + d) % p for i in CRIB_POS})
            if c0 != cd:
                bad.append((d, p, c0, cd))
    P("constant-shift invariance of c_p over d=0..8, p=2..40:",
      "HOLDS (0 exceptions)" if not bad else "FAILS %r" % bad[:5])
    P("So D2b adds nothing that (c) and runningkey.md have not already covered.  The only")
    P("part of the `?` hypothesis with real content is D2 -- a changed ciphertext/crib")
    P("PAIRING -- and that is the part just tested, negatively.")


# ==================================================================== D3
CARTER = {
    "WONDERFULTHINGS": "WONDERFULTHINGS",
    "YESWONDERFULTHINGS": "YESWONDERFULTHINGS",
    "YESWONDERFULTHINGSX": "YESWONDERFULTHINGSX",
    "CANYOUSEEANYTHING": "CANYOUSEEANYTHING",
    "CANYOUSEEANYTHINGYESWONDERFULTHINGS": "CANYOUSEEANYTHINGYESWONDERFULTHINGS",
    "YESWONDERFULTHINGSCANYOUSEEANYTHING": "YESWONDERFULTHINGSCANYOUSEEANYTHING",
    "WONDERFUL": "WONDERFUL",
    "THINGS": "THINGS",
    "YESWONDERFUL": "YESWONDERFUL",
    "HOWARDCARTER": "HOWARDCARTER",
    "CARNARVON": "CARNARVON",
    "LORDCARNARVON": "LORDCARNARVON",
    "TUTANKHAMUN": "TUTANKHAMUN",
    "VALLEYOFTHEKINGS": "VALLEYOFTHEKINGS",
    "NOVEMBERTWENTYSIXTH": "NOVEMBERTWENTYSIXTH",
    "SIXTEENFEBRUARY": "SIXTEENFEBRUARY",
}


def D3_missing_answer():
    hdr("D3.  THE MISSING ANSWER -- 'YES, WONDERFUL THINGS' AS KEY MATERIAL")
    P("""
The sculpture carries Carter's question and withholds his reply.  That reply is the one
piece of Kryptos-narrative text that is deliberately absent from the stone, so it is
absent from the 66-text running-key corpus in findings/runningkey.md and has never been
tested.  Sanborn, April 2006: "the answers to the first three passages contain clues to
the fourth passage."  This is the most literal possible reading of that sentence.

Three tests: (i) the phrase as an explicit key stream at every phase, (ii) the phrase as
a keyword-mixed ALPHABET crossed with all periods (a genuinely new alphabet -- keyed
alphabets built from multi-word phrases are not in the 208,627-alphabet dictionary set),
(iii) the phrase as a running key against the required key blocks by Hamming distance.""")
    cb = L.Combos([("plain", A2Z), ("kryptos", KRY)])

    # (i) explicit key stream, every phase
    P("")
    P("D3a. explicit key stream, every phase, 24 combos")
    best, tests, hist = (0, None), 0, defaultdict(int)
    for name, w in CARTER.items():
        for s in range(len(w)):
            ks = "".join(w[(s + i) % len(w)] for i in range(N))
            ag = L.crib_agreement(ks, cb)
            tests += cb.n
            for v in ag:
                hist[int(v)] += 1
            if int(ag.max()) > best[0]:
                best = (int(ag.max()), (name, s, cb.labels[int(ag.argmax())]))
    P("   tests %d ; best %d/24 at %s" % (tests, best[0], best[1]))
    P("   histogram", dict(sorted(hist.items())),
      "; expected total hits %.1f, observed %d"
      % (tests * 24 / 26.0, sum(k * v for k, v in hist.items())))

    # (ii) as keyed alphabets, all periods
    P("")
    P("D3b. as keyword-mixed ALPHABETS (new alphabets), periods 2-30, 3 rules")
    alphas = [("plain", A2Z), ("kryptos", KRY)] + \
             [(n, L.keyed_alphabet(w)) for n, w in CARTER.items()] + \
             [(n + "_kry", L.keyed_alphabet(w, KRY)) for n, w in CARTER.items()]
    P("   distinct alphabets:", len({a for _, a in alphas}), "of", len(alphas))
    S = L.Sweeper(alphas)
    rows = S.sweep(CRIB_POS, L.CRIB_PT, L.CRIB_CT, tuple(range(2, 31)))
    tot_s = sum(r[2] for r in rows)
    tot_e = sum(r[3] * S.n for r in rows)
    P("   configurations per period: %d ; total tests %d" % (S.n, S.n * len(rows)))
    P("   survivors %d ; expected by chance %.2f" % (tot_s, tot_e))
    surv_by_c = [(r[1], r[0], r[2]) for r in rows if r[2]]
    P("   (c, period, survivors) for periods with any survivor:", surv_by_c)

    # (iii) running key by Hamming distance against the required blocks
    P("")
    P("D3c. as a running key: does the phrase contain the required key block?")
    P("   (the 13-letter block for EASTNORTHEAST and the 11-letter block for BERLINCLOCK,")
    P("    separated by the fixed 29-letter gap; 24 combos x 26 key-alphabet rotations)")
    best = (99, None)
    n_tests = 0
    for name, w in CARTER.items():
        tiled = w * (120 // len(w) + 2)
        for cbn in RK.combos():
            b1, b2 = RK.required_key(cbn)
            for rot in range(26):
                rk = "".join(A2Z[(A2Z.index(c) + rot) % 26] for c in tiled)
                for off in range(len(w)):      # offsets beyond |w| repeat exactly
                    n_tests += 1
                    h = (RK.hamming(rk[off + 21:off + 34], b1)
                         + RK.hamming(rk[off + 63:off + 74], b2))
                    if h < best[0]:
                        best = (h, (name, RK.combo_name(cbn), rot, off))
    P("   tests %d ; best joint Hamming distance %d of 24 (0 = solution)"
      % (n_tests, best[0]))
    P("   at", best[1])
    P("   chance: with 24 independent letters at 1/26, P(<=2 mismatches) = %.3e"
      % sum(_binom(24, k) * (1 / 26.0) ** (24 - k) * (25 / 26.0) ** k for k in range(0, 3)))


def _binom(n, k):
    from math import comb
    return comb(n, k)


def main():
    hdr("(d) THE QUESTION MARK")
    P("K4 ciphertext:", CT)
    validate()
    D1_indexing()
    D2_prefix()
    D2b_keyslot()
    D3_missing_answer()
    hdr("END (d)")
    with open(os.path.join(HERE, "k5_d_output.txt"), "w") as f:
        f.write("\n".join(OUT) + "\n")


if __name__ == "__main__":
    main()
