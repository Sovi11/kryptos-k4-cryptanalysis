"""Quagmire I / II / IV sweep against the K4 cribs.

Model (covers Quagmire I, II, III and IV uniformly):
    c_i = CTALPHA[ (idx_PTALPHA(p_i) + k[i mod period]) mod 26 ]
so for every crib position the required key value is
    k_i = idx_CT(c_i) - idx_PT(p_i)  (mod 26)
and the cipher is a period-p Quagmire iff k_i is constant on residue classes mod p.

  Quagmire I  : PT alphabet keyed,   CT alphabet straight
  Quagmire II : PT alphabet straight, CT alphabet keyed
  Quagmire III: same keyed alphabet for both (already covered by prior work; re-run here
                only for the short list as a regression check)
  Quagmire IV : two different keyed alphabets

Alphabet sources:
  short  = straight A..Z + 16 keyword-mixed alphabets from the Kryptos word list
  dict   = every distinct keyword-mixed alphabet from /usr/share/dict/words (>=3 letters)

Pairs tested: short x short (all), short(PT) x dict(CT), dict(PT) x short(CT).
dict x dict (~3e10 pairs) is out of reach and is NOT tested.

Periods 2..26. For period 26 only one constraint exists (1/26 of random pairs pass),
for 25 three constraints, so those survivors are ranked by an English score of the
partial decryption and only the top ones are kept.
"""
import json
import multiprocessing as mp
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from k4_common import (A2Z, CT, CRIB, CRIB_CT, CRIB_POS, CRIB_PT, SHORT_KEYWORDS, ROOT,
                       keyed_alphabet, dict_alphabets, period_pairs, constraints_per_period,
                       bigram_score, mark_cribs, noncrib, dict_words_in)

PERIODS = list(range(2, 27))
PAIRS = {p: period_pairs(p) for p in PERIODS}
# reorder so the pair most likely to fail comes first (any order works; keep deterministic)
FULL_RECORD_MAX_PERIOD = 25     # periods <= this: record every survivor
TOPN = 40                        # for period 26 keep the best-scoring survivors per chunk

SHORT = [("STRAIGHT", A2Z)] + [(w, keyed_alphabet(w)) for w in SHORT_KEYWORDS]


def idx_vectors(alpha):
    inv = {ch: i for i, ch in enumerate(alpha)}
    return [inv[c] for c in CRIB_CT], [inv[p] for p in CRIB_PT]


def decrypt(pt_alpha, ct_alpha, period, shifts):
    """Partial decryption; residues not fixed by the cribs decrypt to '?'."""
    key = {}
    for k, pos in enumerate(CRIB_POS):
        key[pos % period] = shifts[k]
    inv = {ch: i for i, ch in enumerate(ct_alpha)}
    out = []
    for i, c in enumerate(CT):
        r = i % period
        if r in key:
            out.append(pt_alpha[(inv[c] - key[r]) % 26])
        else:
            out.append("?")
    return "".join(out)


def check_pair(ct_idx, pt_idx):
    s = [(a - b) % 26 for a, b in zip(ct_idx, pt_idx)]
    hits = []
    for p in PERIODS:
        for a, b in PAIRS[p]:
            if s[a] != s[b]:
                break
        else:
            hits.append(p)
    return s, hits


def worker(args):
    """args = (role, short_index, list of (name, alpha) for the other side)."""
    role, si, others = args
    sname, salpha = SHORT[si]
    s_ct, s_pt = idx_vectors(salpha)
    full = []          # (period, ptname, ctname, ptalpha, ctalpha, score, decrypt)
    top26 = []         # (score, ptname, ctname, ptalpha, ctalpha, decrypt)
    n26 = 0
    n = 0
    for oname, oalpha in others:
        o_ct, o_pt = idx_vectors(oalpha)
        if role == "short_is_pt":
            pt_name, pt_alpha, ct_name, ct_alpha = sname, salpha, oname, oalpha
            s, hits = check_pair(o_ct, s_pt)
        else:
            pt_name, pt_alpha, ct_name, ct_alpha = oname, oalpha, sname, salpha
            s, hits = check_pair(s_ct, o_pt)
        n += 1
        if not hits:
            continue
        for p in hits:
            dec = decrypt(pt_alpha, ct_alpha, p, s)
            score = bigram_score(noncrib(dec) if p <= 13 else dec)
            if p <= FULL_RECORD_MAX_PERIOD:
                full.append((p, pt_name, ct_name, pt_alpha, ct_alpha, score, dec))
            else:
                n26 += 1
                top26.append((score, pt_name, ct_name, pt_alpha, ct_alpha, dec))
                if len(top26) > 4 * TOPN:
                    top26.sort(reverse=True)
                    del top26[TOPN:]
    top26.sort(reverse=True)
    return n, full, top26[:TOPN], n26


def main():
    t0 = time.time()
    dicts = dict_alphabets()
    dict_list = sorted((w, a) for a, w in dicts.items())
    print(f"distinct dictionary keyed alphabets: {len(dict_list)}")
    print(f"short alphabets: {len(SHORT)}")

    # ---- short x short (includes Q-I, Q-II, Q-III, Q-IV over the short list) ----
    jobs = [("short_is_pt", si, SHORT) for si in range(len(SHORT))]
    # ---- short x dict, both roles ----
    chunk = 12000
    for si in range(len(SHORT)):
        for start in range(0, len(dict_list), chunk):
            jobs.append(("short_is_pt", si, dict_list[start:start + chunk]))
            jobs.append(("short_is_ct", si, dict_list[start:start + chunk]))

    ctx = mp.get_context("fork")
    total = 0
    full = []
    top26 = []
    n26 = 0
    with ctx.Pool(os.cpu_count()) as pool:
        for n, f, t, c in pool.imap_unordered(worker, jobs, chunksize=1):
            total += n
            full.extend(f)
            top26.extend(t)
            n26 += c
    top26.sort(reverse=True)
    top26 = top26[:TOPN]
    elapsed = time.time() - t0

    # ---- summarise ----
    short_pairs = len(SHORT) ** 2
    dict_pairs = 2 * len(SHORT) * len(dict_list)
    print(f"\nalphabet pairs tested: {total}  (short x short {short_pairs}, short x dict both roles {dict_pairs})")
    print(f"elapsed {elapsed:.0f}s")
    by_p = {}
    for rec in full:
        by_p.setdefault(rec[0], []).append(rec)
    print("\nperiod  constraints  expected_by_chance  observed")
    for p in PERIODS:
        c = constraints_per_period(p)
        exp = total * 26.0 ** -c
        obs = len(by_p.get(p, [])) if p <= FULL_RECORD_MAX_PERIOD else n26
        print(f"{p:6d}  {c:11d}  {exp:18.3g}  {obs}")

    out = {"pairs_tested": total, "dict_alphabets": len(dict_list), "short_alphabets": [n for n, _ in SHORT],
           "elapsed_s": elapsed, "survivors": {}, "period26_count": n26, "period26_top": []}
    for p in sorted(by_p):
        recs = sorted(by_p[p], key=lambda r: -r[5])
        out["survivors"][p] = [{"pt_alpha_name": r[1], "ct_alpha_name": r[2], "pt_alpha": r[3],
                                "ct_alpha": r[4], "bigram_score": r[5], "decrypt": mark_cribs(r[6]),
                                "dict_words": [w for _, w in dict_words_in(r[6])]} for r in recs[:200]]
        print(f"\n=== period {p}: {len(recs)} survivors (showing up to 15, best English score first) ===")
        for r in recs[:15]:
            print(f"  PT={r[1]:<12} CT={r[2]:<12} score={r[5]:.3f}  {mark_cribs(r[6])}")
            words = [w for _, w in dict_words_in(r[6]) if len(w) >= 5]
            if words:
                print(f"      words>=5: {sorted(set(words))[:12]}")
    print(f"\n=== period 26: {n26} survivors (expected by chance {total/26:.0f}); top {TOPN} by English score ===")
    for sc, pn, cn, pa, ca, dec in top26:
        out["period26_top"].append({"pt_alpha_name": pn, "ct_alpha_name": cn, "pt_alpha": pa, "ct_alpha": ca,
                                    "bigram_score": sc, "decrypt": mark_cribs(dec),
                                    "dict_words": [w for _, w in dict_words_in(dec)]})
    for sc, pn, cn, pa, ca, dec in top26[:15]:
        print(f"  PT={pn:<12} CT={cn:<12} score={sc:.3f}  {mark_cribs(dec)}")
    with open(os.path.join(ROOT, "findings", "quagmire_results.json"), "w") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
