"""(d) The solvekryptos.com claim: keystream from "the tableau side of the copper screen"
plus a one-bit position gate.  Implemented faithfully from their public description and
audited for whether it is DERIVABLE from public data or BACK-SOLVED.

Sources (fetched 2026-09-12):
  https://solvekryptos.com/            https://solvekryptos.com/verify
  https://solvekryptos.com/solution    https://solvekryptos.com/resources
The three 7x14 grids below (R-grid, r-grid, gate map) and the helper packet are
transcribed verbatim from the /verify page.

Their stated model, in their notation:
    T_i  = the letter carved on the tableau side at the same (row, column) as K4's
           ciphertext letter i                                   ("helper packet")
    r_i  = ( f(C_i) + g_state(i)(T_i) )  mod 26                  (f = "row-identity card",
                                                                  g = four "helper cards")
    R_i  = r_i + gate_i ,  gate_i in {0,1}                       ("one-bit gate")
    P_i  = ( C_i - R_i )  mod 26                                 ("Quagmire III subtraction")

Audit questions answered here
  D1  Is the helper packet T derivable from public data?
  D2  Does the published R-grid carry any information beyond (C - P) mod 26?
  D3  Is the gate map derivable "from position alone", as claimed?
  D4  How many degrees of freedom does (f, g, gate) have, and can the model fit an
      ARBITRARY plaintext?  (the decisive test)
  D5  Does any falsifiable restriction of the model survive the four Sanborn cribs?
"""
import os
import sys
import random
import itertools
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tableau_common import (PLAIN, KEYED, ALPHAS, COMBOS, combo_name, CRIB_POS, CRIB_PT,
                            K4_CT, RIGHT_ROWS, LEFT_ROWS, required_key_indices,
                            crib_matches, decrypt, selftest, FINDINGS)

OUT = []
def w(*a):
    OUT.append(" ".join(str(x) for x in a))


# --------------------------------------------------- published data (verbatim) ----
# Column order on the site is L14, L1, L2, ... L13, which is exactly position order
# within a tier, so each grid read left-to-right, top-to-bottom is positions 1..97.
R_GRID = [
    [21, 20, 6, 15, 6, 2, 8, 14, 14, 15, 3, 23, 9, 14],
    [6, 19, 1, 1, 10, 23, 25, 1, 11, 25, 2, 3, 2, 24],
    [24, 6, 2, 10, 0, 25, 21, 12, 14, 1, 8, 0, 11, 2],
    [24, 1, 15, 22, 7, 17, 3, 18, 5, 22, 13, 9, 6, 17],
    [22, 18, 4, 16, 5, 17, 14, 12, 20, 24, 10, 11, 6, 10],
    [14, 17, 13, 0, 0, 25, 21, 8, 18, 15, 1, 22, 14, 12],
    [15, 25, 6, 20, 15, 1, 12, 15, 23, 6, 11, 22, 20, None],
]
r_GRID = [
    [21, 19, 6, 14, 6, 2, 7, 13, 13, 14, 2, 23, 8, 13],
    [6, 18, 0, 0, 9, 23, 25, 0, 10, 24, 1, 2, 2, 24],
    [23, 5, 1, 10, 0, 25, 20, 11, 13, 0, 7, 25, 10, 1],
    [23, 0, 14, 21, 6, 16, 2, 17, 4, 21, 12, 9, 5, 16],
    [21, 17, 3, 15, 5, 16, 13, 12, 20, 24, 9, 11, 6, 10],
    [13, 16, 12, 0, 25, 25, 21, 7, 17, 14, 0, 21, 14, 11],
    [14, 25, 6, 19, 14, 0, 11, 14, 22, 6, 10, 21, 19, None],
]
GATE_GRID = [
    [0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1],
    [0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0],
    [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
    [1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0],
    [1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, None],
]

# their reconstructed (NOT authenticated) plaintext, /solution
SK_PT = ("THECOMPASSROSEISHEREXEASTNORTHEASTTHISISYOURPOSITIONX"
         "COMMISSIONBERLINCLOCKWHICHISNORTHEASTOFHEREX")

# their helper packet, /verify
SK_T = ("WXZK"
        "YXZKRYPTOSABCDEFGHIJLMNQUVWXZKR"
        "ZZKRYPTOSABCDEFGHIJLMNQUVWXZKRY"
        "_ABCDEFGHIJKLMNOPQRSTUVWXYZABCD")
SK_Z2_EFFECTIVE = "ZZKRYPTOSABCDEFGHIJLMNQUVWXZKRY"   # their "basis handoff" for 67-97


def flat(grid):
    out = []
    for row in grid:
        for v in row:
            if v is not None:
                out.append(v)
    return out


R_SEQ = flat(R_GRID)
r_SEQ = flat(r_GRID)
G_SEQ = flat(GATE_GRID)


def state_of(i):          # i is 0-indexed K4 position
    if i < 4:
        return "X"
    if i < 35:
        return "Y"
    if i < 66:
        return "Z1"
    return "Z2"


# ==================================================================== D1 ========
def d1_helper_packet():
    w("## D1. Is the helper packet derivable from public data?\n")
    w("Claim: the helper letter for K4 position i is carved on the tableau side at the")
    w("same row and column as K4's ciphertext letter i.")
    w("")
    derived = RIGHT_ROWS[24][27:31] + RIGHT_ROWS[25] + RIGHT_ROWS[26] + RIGHT_ROWS[27]
    w("  derived from data/sculpture_panels.txt : %s  (%d letters)" % (derived, len(derived)))
    w("  solvekryptos published packet          : %s  (%d cells)" % (SK_T, len(SK_T)))
    w("  agree on the first 66 positions        : %s" % (derived[:66] == SK_T[:66]))
    w("  agree on positions 67-97               : %s" % (derived[66:] == SK_T[66:]))
    w("")
    w("VERDICT D1: positions 1-66 ARE mechanically derivable - the cap WXZK is tableau")
    w("row 25 columns 28-31, and the two full rows are the carved rows labelled Y and Z.")
    w("That much is a genuine, checkable, public derivation and I confirm it.")
    w("")
    w("Positions 67-97 are NOT derivable.  The footer row carries 30 letters, because it")
    w("has no row-label letter, while the cipher row above it carries 31.  There is no")
    w("31st character to read.  solvekryptos inserts a BLANK cell and then, via their")
    w("'Z2 footer basis handoff', maps the whole footer to")
    w("  %s" % SK_Z2_EFFECTIVE)
    w("which is exactly the carved Z row again - i.e. after the handoff the 'footer'")
    w("reading is discarded and replaced by a re-read of row Z, one row above.  Their own")
    w("page asserts the opposite in the sentence before (a footer read, 'not a re-read of")
    w("the Z row').  So one third of the 'physical' keystream is a construction, not a")
    w("reading, and it contradicts its own stated justification.")
    w("")
    w("Check: effective Z2 key == carved row Z (row 27 of the panel)? %s"
      % (SK_Z2_EFFECTIVE == RIGHT_ROWS[26]))
    w("")


# ==================================================================== D2 ========
def d2_rgrid():
    w("## D2. Does the published R-grid contain any information?\n")
    calc = [(PLAIN.index(c) - PLAIN.index(p)) % 26 for c, p in zip(K4_CT, SK_PT)]
    w("  R_i = (C_i - P_i) mod 26 computed from their reconstructed plaintext equals the")
    w("  published R-grid at all 97 positions: %s" % (calc == R_SEQ))
    bad = [i for i in range(97) if calc[i] != R_SEQ[i]]
    if bad:
        w("  mismatches at 0-indexed %s" % bad)
    w("")
    w("  R = r + gate holds at all 97 positions: %s"
      % all((r_SEQ[i] + G_SEQ[i]) % 26 == R_SEQ[i] for i in range(97)))
    w("")
    w("VERDICT D2: the R-grid is the DEFINITION of the shift, not a result.  Given any")
    w("97-letter plaintext whatsoever, R = (C - P) mod 26 exists and is unique.  A page")
    w("that publishes R and then verifies 'R = (C - P) mod 26 at 97/97 positions' has")
    w("verified an identity.  The r-grid is likewise just R minus the gate.  Neither")
    w("grid is evidence for the plaintext; both are re-encodings of it.")
    w("")
    w("  (Their own /verify page concedes the point: fitted cards, it says, can always")
    w("  reproduce a supplied shift stream.)")
    w("")


# ==================================================================== D3 ========
def d3_gate():
    w("## D3. Is the one-bit gate map derivable 'from position alone'?\n")
    w("The claim on /verify is that the gate is 'fixed by position' and")
    w("'plaintext-independent by construction'.  The same page also says the gate value")
    w("is whatever makes R = r + gate match (C - P) mod 26, which is a definition in")
    w("terms of the plaintext, not a position rule.  Test it empirically.")
    w("")
    w("  published gate bits: %s" % "".join(str(b) for b in G_SEQ))
    w("  ones = %d, zeros = %d  (the page says 69 and 28)" % (sum(G_SEQ), 97 - sum(G_SEQ)))
    w("")

    def tier(i):    # 1-indexed position
        return (i - 1) // 14 + 1

    def lane(i):
        return ((i - 2) % 14) + 1

    rules = {}
    rules["constant 1"] = lambda i: 1
    rules["constant 0"] = lambda i: 0
    rules["i odd"] = lambda i: i % 2
    rules["i even"] = lambda i: 1 - i % 2
    rules["i mod 3 != 0"] = lambda i: 0 if i % 3 == 0 else 1
    rules["tier odd"] = lambda i: tier(i) % 2
    rules["tier mod 3 != 0"] = lambda i: 0 if tier(i) % 3 == 0 else 1
    rules["lane odd"] = lambda i: lane(i) % 2
    rules["(tier+lane) odd"] = lambda i: (tier(i) + lane(i)) % 2
    rules["lane == 14 (col31)"] = lambda i: 1 if lane(i) == 14 else 0
    rules["lane != 14"] = lambda i: 0 if lane(i) == 14 else 1
    rules["ct letter index odd"] = lambda i: PLAIN.index(K4_CT[i - 1]) % 2
    rules["ct letter index even"] = lambda i: 1 - PLAIN.index(K4_CT[i - 1]) % 2
    rules["ct in KEYED first half"] = lambda i: 1 if KEYED.index(K4_CT[i - 1]) < 13 else 0
    rules["helper letter index odd"] = lambda i: (PLAIN.index(SK_T[i - 1]) % 2
                                                 if SK_T[i - 1] != "_" else 0)
    rules["(ct+helper) odd"] = lambda i: ((PLAIN.index(K4_CT[i - 1]) +
                                          (PLAIN.index(SK_T[i - 1]) if SK_T[i - 1] != "_" else 0)) % 2)
    rules["state X/Y=0, Z=1"] = lambda i: 0 if state_of(i - 1) in ("X", "Y") else 1
    rules["i in a crib"] = lambda i: 1 if (i - 1) in CRIB_POS else 0
    rules["left-panel letter is a vowel"] = lambda i: 1 if K4_CT[i - 1] in "AEIOU" else 0
    rules["fib/pos mod 7 != 0"] = lambda i: 0 if i % 7 == 0 else 1
    rules["x cap 0101 then 1"] = lambda i: [0, 1, 0, 1][i - 1] if i <= 4 else 1

    w("| candidate position rule | bits matched / 97 | (chance 48.5 +- 4.9) |")
    w("|---|---|---|")
    best = (0, None)
    for nm, fn in sorted(rules.items()):
        m = sum(1 for i in range(1, 98) if fn(i) == G_SEQ[i - 1])
        m = max(m, 97 - m)            # a rule and its complement are equally 'a rule'
        w("| %s | %d | |" % (nm, m))
        if m > best[0]:
            best = (m, nm)
    w("")
    w("  best of %d simple position rules (and their complements): %d/97 (%s)"
      % (len(rules), best[0], best[1]))
    w("  the all-ones rule alone already gets %d/97 because the map is 69/28 unbalanced;"
      % max(sum(G_SEQ), 97 - sum(G_SEQ)))
    w("  a rule must beat that substantially to be doing any work.")
    w("")
    w("  X-cap check: published gate for positions 1-4 = %s (their stated '0101': %s)"
      % ("".join(str(b) for b in G_SEQ[:4]), "".join(str(b) for b in G_SEQ[:4]) == "0101"))
    w("")
    w("VERDICT D3: no simple position rule reproduces the map.  The stated recipe ('Y-row")
    w("gate rule, Z1 from Y by +3 internal drift with terminal +1 carry, Z2 from Y by")
    w("footer / basis-handoff collapse') is not published in executable form on the site,")
    w("and the site's own operational definition of the gate is 'whatever makes R = r +")
    w("gate come out right'.  97 free bits are enough to absorb any residual on their own:")
    w("see D4.")
    w("")


# ==================================================================== D4 ========
def fit_model(target_pt, gate=None, z2_handoff=True, ct=K4_CT, helper=None):
    """Solve r_i = f(C_i) + g_state(T_i) (mod 26) for f and g, given a plaintext.

    Returns (ok, ncomponents, ncycles, nnodes, nedges, f, g).
    ok is True iff an exact assignment exists.  Because each connected component of the
    (f-node, g-node) bipartite graph carries one free additive constant, the number of
    distinct exact solutions is 26**ncomponents when ok.
    """
    if gate is None:
        gate = [0] * 97
    if helper is None:
        helper = list(SK_T)
        if z2_handoff:
            helper[66:] = list(SK_Z2_EFFECTIVE)
    R = [(PLAIN.index(c) - PLAIN.index(p)) % 26 for c, p in zip(ct, target_pt)]
    r = [(R[i] - gate[i]) % 26 for i in range(97)]

    adj = defaultdict(list)
    nodes = set()
    for i in range(97):
        fn = ("f", ct[i])
        gn = ("g", state_of(i), helper[i])
        nodes.add(fn)
        nodes.add(gn)
        adj[fn].append((gn, r[i]))
        adj[gn].append((fn, r[i]))
    val = {}
    comps = 0
    ok = True
    for n in nodes:
        if n in val:
            continue
        comps += 1
        val[n] = 0
        stack = [n]
        while stack:
            u = stack.pop()
            for v, weight in adj[u]:
                # f + g = weight ; u is one side, v the other
                want = (weight - val[u]) % 26
                if v in val:
                    if val[v] != want:
                        ok = False
                else:
                    val[v] = want
                    stack.append(v)
    nedges = 97
    nnodes = len(nodes)
    ncycles = nedges - nnodes + comps
    f = {k[1]: v for k, v in val.items() if k[0] == "f"}
    g = {(k[1], k[2]): v for k, v in val.items() if k[0] == "g"}
    return ok, comps, ncycles, nnodes, nedges, f, g


def d4_degrees_of_freedom():
    w("## D4. Degrees of freedom, and the decisive test\n")
    ok, comps, cyc, nn, ne, f, g = fit_model(SK_PT)
    w("Bipartite structure of  r_i = f(C_i) + g_state(T_i)  over the 97 positions:")
    w("  distinct f nodes (ciphertext letters)     : %d" % len({c for c in K4_CT}))
    hel = list(SK_T); hel[66:] = list(SK_Z2_EFFECTIVE)
    for st in ("X", "Y", "Z1", "Z2"):
        w("  distinct g nodes for state %-2s             : %d"
          % (st, len({hel[i] for i in range(97) if state_of(i) == st})))
    w("  TOTAL unknown card entries (nodes)        : %d" % nn)
    w("  equations (one per position, edges)       : %d" % ne)
    w("  connected components                      : %d" % comps)
    w("  independent cycles = E - V + C            : %d" % cyc)
    w("")
    if cyc == 0:
        w("  The constraint graph is a FOREST.  A forest of additive constraints is")
        w("  ALWAYS solvable, for every right-hand side.  The system therefore imposes")
        w("  ZERO conditions on the plaintext.")
    w("")
    w("  plus 97 free gate bits on top of that.")
    w("  size of the exact solution set for a GIVEN plaintext, gate fixed: 26^%d = %.3g"
      % (comps, 26.0 ** comps))
    w("  ... and 2^97 gate choices, each with its own such set.")
    w("")

    w("### The test: can the model fit a plaintext it was not built for?\n")
    rnd = random.Random(20260912)
    trials = []
    trials.append(("solvekryptos' own reconstruction", SK_PT))
    trials.append(("all A's", "A" * 97))
    trials.append(("the alphabet repeated", (PLAIN * 4)[:97]))
    trials.append(("a rival 'plaintext' with the same cribs",
                   "ITWASBURIEDOUTTHERESOMEWHEREX" + "EASTNORTHEAST" +
                   "WHOKNOWSTHEEXACTLOCATIONQ" + "BERLINCLOCK" +
                   "XSLOWLYDESPARATLYSLOWLYX"[:19]))
    for k in range(5):
        trials.append(("random letters #%d" % (k + 1),
                       "".join(rnd.choice(PLAIN) for _ in range(97))))
    w("| target 'plaintext' | fits exactly (gate=0) | components | cycles | solutions |")
    w("|---|---|---|---|---|")
    nfit = 0
    for nm, pt in trials:
        pt = (pt + "X" * 97)[:97]
        ok, comps, cyc, nn, ne, f, g = fit_model(pt)
        nfit += ok
        w("| %s | %s | %d | %d | 26^%d |" % (nm, ok, comps, cyc, comps))
    w("")
    # large-scale
    N = 2000
    good = 0
    for _ in range(N):
        pt = "".join(rnd.choice(PLAIN) for _ in range(97))
        ok, *_ = fit_model(pt)
        good += ok
    w("  %d uniformly random 97-letter strings: %d fit the model EXACTLY (%.1f%%)"
      % (N, good, 100.0 * good / N))
    w("")
    w("VERDICT D4: the published mechanism has at least %d free card entries and 97 free" % nn)
    w("gate bits against 97 equations, and its constraint graph is a forest, so it fits")
    w("EVERY 97-letter string over the alphabet.  It is not a cipher hypothesis; it is a")
    w("re-parameterisation of an arbitrary shift stream.  No amount of '97/97 internal")
    w("consistency' can distinguish their reconstruction from any other text, including")
    w("random letters, and the cribs are satisfied by construction because they were")
    w("written into the assumed plaintext before the cards were solved.")
    w("")


# ==================================================================== D5 ========
def d5_falsifiable():
    w("## D5. Is any falsifiable restriction of the model consistent with the cribs?\n")
    w("Strip the free cards away and keep only what is genuinely 'read off the sculpture':")
    w("the helper packet T.  Then ask whether ANY of the standard periodic-free ciphers")
    w("turns C into the cribs using T as the key stream.")
    w("")
    hel_v = SK_T.replace("_", "Z")                      # visible footer, blank -> Z
    hel_h = SK_T[:66] + SK_Z2_EFFECTIVE                 # after their 'basis handoff'
    for nm, hel in (("visible packet (blank->Z)", hel_v),
                    ("packet after Z2 basis handoff", hel_h)):
        best = (-1, None)
        for cb in COMBOS:
            Ak = ALPHAS[cb[3]]
            req = required_key_indices(cb)
            d0 = None
            m = 0
            for j, pos in enumerate(CRIB_POS):
                d = (Ak.index(hel[pos]) - req[j]) % 26
                if d0 is None:
                    d0 = d
                if d == d0:
                    m += 1
            if m > best[0]:
                best = (m, (cb, d0))
        w("  %-32s best %2d/24 over 24 combos x 26 rotations (%s, rot %d)"
          % (nm, best[0], combo_name(best[1][0]), best[1][1]))
        # plain Vigenere/Beaufort decryptions for the record
    w("")
    w("  chance: 24 combos x 26 rotations = 624 trials; P(24/24) = 624 * 26^-24 = 1.2e-31")
    w("")
    w("Now allow f and g to be AFFINE rather than free (f(C) = a*idxK(C)+b,")
    w("g(T) = u*idxK(T)+v_state), with the published gate map, and demand all 24 cribs:")
    hits = 0
    trials = 0
    bestm = 0
    hel = list(SK_T[:66] + SK_Z2_EFFECTIVE)
    ctidx = [KEYED.index(c) for c in K4_CT]
    tidx = [KEYED.index(t) if t in KEYED else 0 for t in hel]
    Rneed = {i: (PLAIN.index(K4_CT[i]) - PLAIN.index(CRIB_PT[CRIB_POS.index(i)])) % 26
             for i in CRIB_POS}
    stateidx = {"X": 0, "Y": 1, "Z1": 2, "Z2": 3}
    for a in range(26):
        for b in range(26):
            for u in range(26):
                # v_state is free per state: solve it from the first crib in each state,
                # then check the rest.  Cribs live only in states Y (pos 21-33) and
                # Z1/Z2 (63-73), so at most 3 states are constrained.
                vs = {}
                m = 0
                okall = True
                for i in CRIB_POS:
                    st = stateidx[state_of(i)]
                    base = (a * ctidx[i] + b + u * tidx[i] + G_SEQ[i]) % 26
                    need = (Rneed[i] - base) % 26
                    if st in vs:
                        if vs[st] == need:
                            m += 1
                        else:
                            okall = False
                    else:
                        vs[st] = need
                        m += 1
                trials += 1
                bestm = max(bestm, m)
                if okall:
                    hits += 1
                    if hits <= 5:
                        w("    affine fit a=%d b=%d u=%d v=%s" % (a, b, u, vs))
    w("  affine (a,b,u) triples tested: %d ; consistent with all 24 cribs: %d ; best %d/24"
      % (trials, hits, bestm))
    w("  chance expectation: the cribs occupy 3 states, so 21 of the 24 are real tests;")
    w("  expected consistent triples = %d * 26^-21 = %.3g" % (trials, trials * 26.0 ** -21))
    w("")
    w("VERDICT D5: with the cards removed the 'physical keystream' does not fit the cribs")
    w("under any standard cipher, and with the cards restricted to the simplest")
    w("non-vacuous form (affine) it does not fit either.  All of the model's agreement")
    w("with the cribs comes from the 205+ free parameters, i.e. from fitting.")
    w("")


def main():
    selftest()
    w("# (d) Audit of the solvekryptos.com 'tableau side + one-bit gate' claim\n")
    w("Everything below is computed from their own published grids and from the carved")
    w("tableau.  I did not use their paid verifier or download their bundle.\n")
    d1_helper_packet()
    d2_rgrid()
    d3_gate()
    d4_degrees_of_freedom()
    d5_falsifiable()
    w("## Overall verdict on (d)\n")
    w("Derivable from public data : the helper packet for K4 positions 1-66 (tableau row")
    w("  25 cols 28-31, then carved rows Y and Z).  I reproduce it exactly.")
    w("Not derivable              : positions 67-97 of the packet (the footer is 30")
    w("  letters, not 31; a blank is invented and then overwritten by a re-read of row Z),")
    w("  the f-table (15 of 26 entries admitted as reconstruction), all four helper cards")
    w("  (explicitly labelled back-solved on their own site), and the 97 gate bits.")
    w("Back-solved                : everything that does the cryptographic work.")
    w("The model cannot be wrong, which is the problem: it fits uniformly random text")
    w("with probability 1.  It therefore provides no evidence about K4's plaintext, and")
    w("its 'reconstructed plaintext' is an assumption of the fit, not an output of it.")
    print("\n".join(OUT))
    with open(os.path.join(FINDINGS, "tableau_d_out.txt"), "w") as fh:
        fh.write("\n".join(OUT) + "\n")


if __name__ == "__main__":
    main()
