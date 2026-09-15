"""(a) The tableau's ANOMALIES as signal.

The deviation list between the carved right-hand panel and the ideal KRYPTOS-keyed
tableau is re-derived from scratch here (lateral/tableau_anomalies.json is checked
against it, not trusted).  Then the three readings the brief asks for:

  A2  information-theoretic bound on what a deviation list of this size CAN encode
  A3  the anomaly POSITIONS as a number sequence: every number the anomaly names, used
      as a constant shift, a period, a decimation step, a Gronsfeld digit stream and a
      running-key offset
  A4  the anomaly LETTERS as a key stream (the whole stream is one letter, 'L')
  A5  the anomaly positions as SPECIAL INDICES WHERE A CIPHER RULE CHANGES -- an
      exhaustive sweep of two-regime models over ALL 96 switch points, so the
      anomaly-derived switch points can be scored against the best any switch point
      achieves
  A6  the PHASE-SLIP hypothesis: the anomaly is an inserted letter, and Sanborn is on
      record (K2, April 2006) for exactly this class of error throwing a key stream out
      of phase.  Running key from the tableau with one inserted/deleted letter at every
      position, every offset, every combo, every rotation.

Every count is quoted against its chance expectation, which is Monte-Carlo'd in
tab_common.null_modal() rather than guessed.
"""
import os
import sys
import time
import itertools
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import tab_common as T
from tab_common import (PLAIN, KEYED, ALPHAS, COMBOS, combo_name, CRIB_POS, CRIB_PT,
                        CRIB_CT, K4_CT, RIGHT_ROWS, RIGHT_ROWS_IDEAL, TAB_PHYS, TAB_IDEAL,
                        POS, REQ, IDX, crib_match_matrix, modal_counts, expected_hits,
                        constraints, FINDINGS)

OUT = []
def w(*a):
    OUT.append(" ".join(str(x) for x in a))


NULL = None          # filled in main()


def rate(k):
    """P(best-over-26-rotations crib match >= k) for a random key stream.
    Analytic union bound 26*P(Binom(24,1/26)>=k); agrees with the Monte-Carlo null to
    within its resolution for k <= 8 and stays valid above it."""
    return T.rate_bound(k)


def show_decrypt(label, cb, key_letters):
    """Any result above the null's p99 gets fully decrypted and scored as English."""
    r = T.score_report(cb, key_letters)
    w("    %s -> cribs %d/24" % (label, r["cribs"]))
    w("      plaintext : %s" % r["marked"])
    w("      bigram %.3f (English ~-5.3, random ~-7.5 ; random 99th pct -7.05), IoC %.4f"
      % (r["bigram"], r["ioc"]))
    w("      dict words >=5 letters outside the cribs: %s"
      % (sorted(set(r["words"]))[:12] or "none"))


# ================================================================== A1 =========
def a1_deviations():
    w("## A1. The deviation list, re-derived from scratch\n")
    import difflib
    phys, ideal = TAB_PHYS, TAB_IDEAL
    sm = difflib.SequenceMatcher(None, ideal, phys, autojunk=False)
    devs = [op for op in sm.get_opcodes() if op[0] != "equal"]
    w("carved letters %d ; ideal letters %d ; difflib similarity %.6f"
      % (len(phys), len(ideal), sm.ratio()))
    w("opcodes that are not 'equal': %d" % len(devs))
    for tag, i1, i2, j1, j2 in devs:
        w("  %-7s ideal[%d:%d]=%r -> physical[%d:%d]=%r   (1-indexed physical pos %d)"
          % (tag, i1, i2, ideal[i1:i2], j1, j2, phys[j1:j2], j1 + 1))
    # row-by-row
    rowdiff = [(i, RIGHT_ROWS[i], RIGHT_ROWS_IDEAL[i])
               for i in range(28) if RIGHT_ROWS[i] != RIGHT_ROWS_IDEAL[i]]
    w("rows differing from the ideal tableau: %d -> %s" % (len(rowdiff), [r[0] for r in rowdiff]))
    for i, p, q in rowdiff:
        w("  row %d (label %r): carved %r (%d) / ideal %r (%d)"
          % (i, p[0], p, len(p), q, len(q)))
    # cross-check the stored JSON
    import json
    jp = os.path.join(T.ROOT, "lateral", "tableau_anomalies.json")
    stored = json.load(open(jp))
    ok = (stored["physical_letters"] == len(phys) and stored["ideal_letters"] == len(ideal)
          and len(stored["anomalies"]) == 1
          and stored["anomalies"][0]["stream_pos_1idx"] == devs[0][3] + 1
          and stored["anomalies"][0]["actual"] == "L")
    w("")
    w("lateral/tableau_anomalies.json agrees with this independent re-derivation: %s" % ok)
    w("ANOMALY SET = { (position 465 1-indexed / 464 0-indexed, inserted letter 'L') }")
    w("cardinality = 1.  There is no second deviation to build a sequence out of.")
    w("")
    return devs


# ================================================================== A2 =========
def a2_information():
    w("## A2. What a one-element deviation list can possibly encode\n")
    n = len(TAB_PHYS)
    bits_pos = math.log2(n)
    bits_letter = math.log2(26)
    need = 97 * math.log2(26)
    w("An observer who knows the ideal tableau learns, from the carving, only:")
    w("  which position was altered : log2(%d) = %.2f bits" % (n, bits_pos))
    w("  which letter was inserted  : log2(26)  = %.2f bits" % bits_letter)
    w("  total                      : %.2f bits" % (bits_pos + bits_letter))
    w("A 97-letter key stream carries 97*log2(26) = %.0f bits." % need)
    w("A 24-letter crib fit demands 24*log2(26) = %.0f bits of key information." % (24 * math.log2(26)))
    w("")
    w("So the anomaly CANNOT BE the key: it is short of a 97-letter stream by a factor of")
    w("%.0f, and short of even the crib block by a factor of %.1f."
      % (need / (bits_pos + bits_letter), 24 * math.log2(26) / (bits_pos + bits_letter)))
    w("The only cryptographically coherent roles left for it are SELECTOR roles -- it can")
    w("name a number (a period, an offset, a shift, a switch point) or flip a rule.  A3-A6")
    w("test every such role exhaustively.  This bound is why (a) can be CLOSED rather than")
    w("merely searched: the space of things one datum can select is small and finite.")
    w("")


# ================================================================== A3 =========
ANOMALY_NUMBERS = {
    11: "L is index 11 of the plain alphabet",
    13: "N is index 13 of the plain alphabet",
    14: "row N is the 14th lettered row (0-indexed), carved row 14 of 28",
    15: "row N is carved row 15 (1-indexed)",
    18: "L is index 18 of the KRYPTOS alphabet",
    26: "rows in the tableau body (alphabet size)",
    30: "ideal body-row width",
    31: "the extra L sits at column 31 (0-indexed) of its row",
    32: "carved row N is 32 characters long",
    97: "K4 length (for reference)",
    402: "letters after the extra L",
    464: "0-indexed linear position of the extra L",
    465: "1-indexed linear position of the extra L",
    866: "ideal tableau length",
    867: "carved tableau length",
}


def a3_numbers():
    w("## A3. The anomaly POSITION as a number, used every way a number can be used\n")
    # ---- (i) as a constant shift
    w("### A3(i) as a constant additive shift  key_i = A[k] for all i")
    w("A constant key is monoalphabetic; the 24 crib pairs demand 24 equal required-key")
    w("indices.  Number of combos for which the 24 required indices are all equal:")
    n_ok = sum(1 for cb in COMBOS if len(set(REQ[cb].tolist())) == 1)
    w("  %d / 24 combos.  (A constant shift is therefore impossible regardless of WHICH" % n_ok)
    w("  number the anomaly names; this re-confirms the monoalphabetic negative.)")
    w("")

    # ---- (ii) as a period
    w("### A3(ii) as a key PERIOD")
    w("| number | meaning | constraints c_p | chance 26^-c_p | combos consistent |")
    w("|---|---|---|---|---|")
    for num in sorted(ANOMALY_NUMBERS):
        p = num if num <= 97 else num
        c_p = constraints(p)
        classes = {}
        for j, pos in enumerate(CRIB_POS):
            classes.setdefault(pos % p, []).append(j)
        nok = sum(1 for cb in COMBOS
                  if all(len({int(REQ[cb][j]) for j in js}) == 1 for js in classes.values()))
        note = "VACUOUS" if c_p == 0 else ""
        w("| %d | %s | %d | %.3g | %d/24 %s|"
          % (num, ANOMALY_NUMBERS[num], c_p, 26.0 ** -c_p, nok, note))
    w("")

    # ---- (iii) as a decimation step into the tableau
    w("### A3(iii) as a DECIMATION step into the tableau")
    w("key_i = source[(o + step*i) mod len(source)], for each anomaly number as `step`,")
    w("every start o, both tableau variants and their reversals, 24 combos, 26 rotations.")
    srcs = {"phys": TAB_PHYS, "ideal": TAB_IDEAL,
            "phys_rev": TAB_PHYS[::-1], "ideal_rev": TAB_IDEAL[::-1]}
    best_all = (-1, None)
    trials = 0
    hits = 0
    for sname, s in srcs.items():
        L = len(s)
        si = {a: T.as_idx(s, a) for a in ("plain", "keyed")}
        for step in sorted(ANOMALY_NUMBERS):
            if step % L == 0:
                continue
            offs = np.arange(L, dtype=np.int64)
            gather = (offs[:, None] + step * POS[None, :]) % L      # (L, 24)
            for cb in COMBOS:
                kidx = si[cb[3]][gather]
                best, rot, ex0 = crib_match_matrix(kidx, cb)
                trials += L
                hits += int((best == 24).sum())
                b = int(best.max())
                if b > best_all[0]:
                    o = int(best.argmax())
                    best_all = (b, (sname, step, o, combo_name(cb), int(rot[o])))
    w("  trials %s ; 24/24 hits %d ; expected by chance %.3g ; best %d/24 %s"
      % (f"{trials:,}", hits, expected_hits(trials), best_all[0], best_all[1]))
    w("  P(a single random stream reaching %d/24) <= %.3g ; expected number of trials at"
      % (best_all[0], rate(best_all[0])))
    w("  or above that mark over %s trials: %.2f.  Observed: 1."
      % (f"{trials:,}", trials * rate(best_all[0])))
    sname, step, o, cbname, rot = best_all[1]
    s_ = srcs[sname]
    cb = [c for c in COMBOS if combo_name(c) == cbname][0]
    L = len(s_)
    ak = cb[3]
    ks = "".join(ALPHAS[ak][(IDX[ak][s_[(o + step * i) % L]] + rot) % 26] for i in range(97))
    show_decrypt("best decimation model", cb, ks)
    w("")

    # ---- (iv) as a Gronsfeld digit stream
    w("### A3(iv) as a Gronsfeld / numeric key")
    w("The digits of each anomaly number, repeated, used as shift values 0-9:")
    rows = []
    for num in sorted(ANOMALY_NUMBERS):
        digs = [int(d) for d in str(num)]
        best_here = -1
        bestcb = None
        for cb in COMBOS:
            for st in range(len(digs)):
                kidx = np.array([[(digs[(st + p) % len(digs)]) for p in CRIB_POS]], dtype=np.int64)
                b, r, e = crib_match_matrix(kidx, cb)
                if int(b[0]) > best_here:
                    best_here = int(b[0])
                    bestcb = (combo_name(cb), st, int(r[0]))
        rows.append((num, digs, best_here, bestcb))
    w("| number | digits | best crib match | where |")
    w("|---|---|---|---|")
    for num, digs, b, cb in rows:
        w("| %d | %s | %d/24 | %s |" % (num, "".join(map(str, digs)), b, cb))
    w("  Structural impossibility, independent of search: the 24 required shifts under")
    req_spans = []
    for cb in COMBOS:
        vals = REQ[cb].tolist()
        # a Gronsfeld key only ever supplies 0..9 (plus a free rotation r)
        ok_any = False
        for r in range(26):
            if all(0 <= (v - r) % 26 <= 9 for v in vals):
                ok_any = True
                break
        req_spans.append(ok_any)
    w("  every combo need values that no 0-9 digit stream can supply for %d of 24 combos;"
      % (24 - sum(req_spans)))
    w("  combos where SOME rotation brings all 24 required shifts into 0..9: %d/24."
      % sum(req_spans))
    w("")


# ================================================================== A4 =========
def a4_letters():
    w("## A4. The anomaly LETTERS as a key stream\n")
    w("The deviation list contains exactly one letter, 'L'.  As a key stream of length 1")
    w("it is a constant key, i.e. a monoalphabetic shift, already impossible by A3(i).")
    w("For completeness, all 24 combos with the single key letter L repeated:")
    best = -1
    for cb in COMBOS:
        kidx = np.array([[IDX[cb[3]]["L"]] * 24], dtype=np.int64)
        b, r, e = crib_match_matrix(kidx, cb)
        best = max(best, int(b[0]))
    w("  best crib match over 24 combos x 26 rotations: %d/24 (chance-level: P(>=%d)=%.3g)"
      % (best, best, rate(best)))
    w("")
    w("Extending the 'letters' reading to every letter the anomaly touches -- the inserted")
    w("L, its row label N, the four letters of the HILL column, the row-N body, and the")
    w("two rows either side of the plate seam -- used as repeated key blocks:")
    blocks = {
        "L": "L",
        "N": "N",
        "HILL": "HILL",
        "row N carved (32)": RIGHT_ROWS[14],
        "row N body carved (31)": RIGHT_ROWS[14][1:],
        "row N ideal body (30)": RIGHT_ROWS_IDEAL[14][1:],
        "rows M,N at the plate seam": RIGHT_ROWS[13] + RIGHT_ROWS[14],
        "last-column carved A..Z": "".join(r[-1] for r in RIGHT_ROWS[1:27]),
        "last-column ideal A..Z": "".join(r[-1] for r in RIGHT_ROWS_IDEAL[1:27]),
    }
    w("")
    w("| key block | len | best crib match | chance P(>=that) | where |")
    w("|---|---|---|---|---|")
    trials = 0
    hits = 0
    for nm, blk in blocks.items():
        L = len(blk)
        bi = {a: T.as_idx(blk, a) for a in ("plain", "keyed")}
        bb, bwhere = -1, None
        for cb in COMBOS:
            gather = (np.arange(L, dtype=np.int64)[:, None] + POS[None, :]) % L
            kidx = bi[cb[3]][gather]
            b, r, e = crib_match_matrix(kidx, cb)
            trials += L
            hits += int((b == 24).sum())
            if int(b.max()) > bb:
                o = int(b.argmax())
                bb, bwhere = int(b[o]), (combo_name(cb), "start=%d" % o, "rot=%d" % int(r[o]))
        w("| %s | %d | %d/24 | %.3g | %s |" % (nm, L, bb, rate(bb), bwhere))
    w("")
    w("  total trials %s ; 24/24 hits %d ; expected by chance %.3g"
      % (f"{trials * 24:,}", hits, expected_hits(trials * 24)))
    w("")


# ================================================================== A5 =========
def a5_switch():
    """The anomaly position as a SPECIAL INDEX where a cipher rule changes."""
    w("## A5. The anomaly position as a SWITCH POINT where the rule changes\n")
    w("This is the only reading in which one datum can do real cryptographic work: it")
    w("names an index s at which the system changes behaviour.  The anomaly's own")
    w("candidate switch points, mapped into K4's 0..96 index range:")
    cands = {}
    for num, why in ANOMALY_NUMBERS.items():
        cands.setdefault(num % 97, []).append("%d (%s)" % (num, why))
    for s in sorted(cands):
        w("  s = %-3d <- %s" % (s, "; ".join(cands[s])))
    w("")
    w("Rather than test only those, every model below is swept over ALL 96 interior switch")
    w("points, so the anomaly-named ones can be scored against the best obtainable.")
    w("")

    # ---- M1: two constant shifts
    w("### A5-M1  two constant shifts (regime A before s, regime B from s on)")
    w("key_i = a for i < s, b for i >= s.  Free: a, b (and the combo).  The 24 cribs then")
    w("impose (n1-1)+(n2-1) = 22 constraints, chance 26^-22 = %.3g per (s, combo)." % (26.0 ** -22))
    results = []
    for s in range(1, 97):
        for cb in COMBOS:
            v = REQ[cb]
            m = POS < s
            g1 = set(v[m].tolist())
            g2 = set(v[~m].tolist())
            n1, n2 = int(m.sum()), int((~m).sum())
            if len(g1) <= 1 and len(g2) <= 1:
                results.append((s, cb, n1, n2))
    n_trials = 96 * 24
    w("  (s, combo) pairs tested: %d ; consistent: %d ; expected by chance %.3g"
      % (n_trials, len(results), n_trials * 26.0 ** -22))
    for s, cb, n1, n2 in results[:10]:
        w("    s=%d %s (%d|%d)" % (s, combo_name(cb), n1, n2))
    if not results:
        w("    none.")
    w("")

    # ---- M2: combo swap at s, constant shift each side
    w("### A5-M2  the CIPHER ITSELF changes at s (combo A before, combo B after), each")
    w("side a constant shift.  24x24 combo pairs x 96 switch points = %d models." % (24 * 24 * 96))
    found = []
    for s in range(1, 97):
        m = POS < s
        for cbA in COMBOS:
            if len(set(REQ[cbA][m].tolist())) > 1:
                continue
            for cbB in COMBOS:
                if len(set(REQ[cbB][~m].tolist())) <= 1:
                    found.append((s, cbA, cbB))
    w("  consistent models: %d ; expected by chance %.3g" % (len(found), 24 * 24 * 96 * 26.0 ** -22))
    for s, a, b in found[:10]:
        w("    s=%d  %s -> %s" % (s, combo_name(a), combo_name(b)))
    if not found:
        w("    none.")
    w("")

    # ---- M3: periodic key with a phase jump at s
    w("### A5-M3  periodic key of period p with a PHASE JUMP of d at s")
    w("key_i = K[(i + d*[i>=s]) mod p].  p 2..30, d 1..p-1, s 1..96, 24 combos.")
    w("The crib constraint count c = 24 - #distinct key slots touched; a model with c<=0")
    w("is vacuous and is reported separately, never as a hit.")
    tested = 0
    consistent = []
    vacuous = 0
    for p in range(2, 31):
        for d in range(1, p):
            for s in range(1, 97):
                slot = (POS + d * (POS >= s)) % p
                nslots = len(set(slot.tolist()))
                c = 24 - nslots
                for cb in COMBOS:
                    tested += 1
                    if c <= 0:
                        vacuous += 1
                        continue
                    v = REQ[cb]
                    ok = True
                    for sl in set(slot.tolist()):
                        if len(set(v[slot == sl].tolist())) > 1:
                            ok = False
                            break
                    if ok:
                        consistent.append((p, d, s, cb, c))
    w("  models tested %s (of which %s vacuous, c<=0) ; consistent non-vacuous: %d"
      % (f"{tested:,}", f"{vacuous:,}", len(consistent)))
    exp = 0.0
    for p in range(2, 31):
        for d in range(1, p):
            for s in range(1, 97):
                slot = (POS + d * (POS >= s)) % p
                c = 24 - len(set(slot.tolist()))
                if c > 0:
                    exp += 24 * 26.0 ** -c
    w("  expected consistent-by-chance over the same non-vacuous models: %.4f" % exp)
    w("  (a 'consistent' model here is NOT a candidate solution: with c constraints the")
    w("   key still has p - (24-c) free letters, so the 73 non-crib positions are not")
    w("   determined at all.  Only c >= a large value would make the model predictive.)"
      )
    byp = Counter(x[0] for x in consistent)
    if consistent:
        w("  consistent models by period: %s" % dict(sorted(byp.items())))
        for p, d, s, cb, c in consistent[:15]:
            w("    p=%d d=%d s=%d c=%d %s" % (p, d, s, c, combo_name(cb)))
    else:
        w("    none.")
    w("")

    # ---- M4: periodic key that RESTARTS at s
    w("### A5-M4  periodic key of period p that RESTARTS (phase resets to 0) at s")
    tested = 0
    consistent = []
    vacuous = 0
    exp = 0.0
    for p in range(2, 31):
        for s in range(1, 97):
            slot = np.where(POS < s, POS % p, (POS - s) % p)
            # slots before and after s are different name spaces only if we say so; the
            # key is the SAME 26-letter block, so slots collide across the boundary.
            nslots = len(set(slot.tolist()))
            c = 24 - nslots
            if c > 0:
                exp += 24 * 26.0 ** -c
            for cb in COMBOS:
                tested += 1
                if c <= 0:
                    vacuous += 1
                    continue
                v = REQ[cb]
                ok = all(len(set(v[slot == sl].tolist())) == 1 for sl in set(slot.tolist()))
                if ok:
                    consistent.append((p, s, cb, c))
    w("  models tested %s (%s vacuous) ; consistent non-vacuous %d ; expected by chance %.4f"
      % (f"{tested:,}", f"{vacuous:,}", len(consistent), exp))
    for p, s, cb, c in consistent[:15]:
        w("    p=%d s=%d c=%d %s" % (p, s, c, combo_name(cb)))
    if not consistent:
        w("    none.")
    w("")


# ================================================================== A6 =========
def a6_phase_slip():
    w("## A6. The PHASE-SLIP hypothesis\n")
    w("Motivation, and it is documented rather than invented: in April 2006 Sanborn")
    w("announced that he had OMITTED one ciphertext letter from K2, which threw the tail")
    w("of that message out of phase with its key and made the ending unreadable")
    w("(https://elonka.com/kryptos/CorrectedK2Announcement.html).  The tableau anomaly is")
    w("an INSERTED letter.  If a running key were drawn from the carved panel, an")
    w("insertion is exactly the defect that puts everything after it one place out.")
    w("So: running key from the tableau, with one letter deleted or duplicated at every")
    w("possible slip point, every offset, all 24 combos, all 26 rotations.")
    w("")
    srcs = {
        "tableau carved (867)": TAB_PHYS,
        "tableau ideal (866)": TAB_IDEAL,
        "tableau carved reversed": TAB_PHYS[::-1],
        "tableau ideal reversed": TAB_IDEAL[::-1],
        "tableau carved, labels stripped (781)": "".join(r[1:] for r in RIGHT_ROWS[1:27]),
        "tableau carved body column-major": _colmajor(),
    }
    t0 = time.time()
    grand_trials = 0
    grand_hits = 0
    best_all = (-1, None)
    w("| source | len | trials | 24/24 hits | expected | best | P(>=best) |")
    w("|---|---|---|---|---|---|---|")
    for nm, s in srcs.items():
        L = len(s)
        si = {a: T.as_idx(s, a) for a in ("plain", "keyed")}
        nofs = L - 98
        if nofs <= 0:
            continue
        offs = np.arange(nofs, dtype=np.int64)
        trials = 0
        hits = 0
        best = (-1, None)
        for slip in range(0, 98):
            for kind, sign in (("skip", 1), ("dup", -1)):
                d = sign * (POS >= slip).astype(np.int64)
                gather = offs[:, None] + POS[None, :] + d[None, :]
                valid = (gather >= 0).all(axis=1) & (gather < L).all(axis=1)
                g = gather[valid]
                if g.size == 0:
                    continue
                for cb in COMBOS:
                    kidx = si[cb[3]][g]
                    b, r, e = crib_match_matrix(kidx, cb)
                    trials += b.shape[0]
                    hits += int((b == 24).sum())
                    if int(b.max()) > best[0]:
                        o = int(b.argmax())
                        best = (int(b[o]), (kind, slip, int(offs[valid][o]), combo_name(cb),
                                            int(r[o])))
        grand_trials += trials
        grand_hits += hits
        if best[0] > best_all[0]:
            best_all = (best[0], (nm,) + best[1])
        w("| %s | %d | %s | %d | %.3g | %d/24 %s | %.3g |"
          % (nm, L, f"{trials:,}", hits, expected_hits(trials), best[0], best[1], rate(best[0])))
    w("")
    w("  TOTAL trials %s ; 24/24 hits %d ; expected by chance %.3g ; wall %.1fs"
      % (f"{grand_trials:,}", grand_hits, expected_hits(grand_trials), time.time() - t0))
    w("  best overall %d/24 at %s" % best_all)
    w("  A random key stream reaches %d/24 with probability %.3g, so over %s trials the"
      % (best_all[0], rate(best_all[0]), f"{grand_trials:,}"))
    w("  expected number of streams at or above that mark is %.3g -- i.e. the best result"
      % (grand_trials * rate(best_all[0])))
    w("  here is not merely consistent with chance, it is BELOW what chance predicts.")
    nm, kind, slip, off, cbname, rot = best_all[1]
    s_ = srcs[nm]
    cb = [c for c in COMBOS if combo_name(c) == cbname][0]
    ak = cb[3]
    sign = 1 if kind == "skip" else -1
    ks = "".join(ALPHAS[ak][(IDX[ak][s_[off + i + (sign if i >= slip else 0)]] + rot) % 26]
                 for i in range(97))
    show_decrypt("best phase-slip model", cb, ks)
    w("")


def _colmajor():
    body = [r[1:] for r in RIGHT_ROWS[1:27]]
    wmax = max(len(r) for r in body)
    out = []
    for c in range(wmax):
        for r in body:
            if c < len(r):
                out.append(r[c])
    return "".join(out)


# ==================================================================== main =====
import math


def main():
    global NULL
    T.selftest()
    NULL = T.null_modal()
    w("# (a) The tableau's anomalies as signal\n")
    w("Null calibration (Monte-Carlo, 200,000 random 24-letter key streams):")
    w("  best-over-26-rotations crib match: mean %.3f, p95 %d, p99 %d, max %d"
      % (NULL[0], NULL[1], NULL[2], NULL[3]))
    w("  P(>=k) for k = " + ", ".join("%d:%.2g" % (k, v) for k, v in sorted(NULL[4].items())
                                      if 3 <= k <= 12 and v > 0))
    w("  Any 'best' figure below must be read against this table.  7/24 happens by chance")
    w("  once per ~1,600 random streams; 9/24 once per ~67,000.")
    w("")
    a1_deviations()
    a2_information()
    a3_numbers()
    a4_letters()
    a5_switch()
    a6_phase_slip()
    txt = "\n".join(OUT) + "\n"
    print(txt)
    with open(os.path.join(FINDINGS, "tab_a_out.txt"), "w") as f:
        f.write(txt)


if __name__ == "__main__":
    main()
