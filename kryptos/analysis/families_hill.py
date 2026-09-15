"""Hill cipher consistency with the K4 cribs.

Because C = K P (mod 26) is linear, each ROW of K is independent:
    c_r = sum_j K[r][j] * p_j   (+ v_r for the affine variant)
so a 2x2 key is searched row-wise over 26^2 (or 26^3 affine) values per row, for every
block alignment, using only the crib blocks that lie entirely inside the cribs.
Both the encryption direction (C = K P) and the decryption direction (P = D C) are
searched; a consistent key must give a solution for every row.  3x3 is done the same way.
Letter numbering: straight A=0..Z=25 and KRYPTOS-keyed index.  The affine term covers
the A=1..Z=26 convention as a special case.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from k4_common import A2Z, KRYPTOS_ALPHA, CT, CRIB, CRIB_POS, ROOT

RESULTS = []


def blocks(n, offset):
    """(pt tuple, ct tuple) for every length-n block, aligned at 0-indexed position `offset`, fully in the cribs."""
    out = []
    for start in range(offset, 97 - n + 1, n):
        idxs = range(start, start + n)
        if all(i in CRIB for i in idxs):
            out.append((tuple(CRIB[i] for i in idxs), tuple(CT[i] for i in idxs), start + 1))
    return out


def row_solutions(n, pairs, affine):
    """pairs: list of (input vector, output scalar).  Return all coefficient rows satisfying every pair."""
    import itertools
    sols = []
    rng = range(26)
    for coeffs in itertools.product(rng, repeat=n):
        for v in (rng if affine else (0,)):
            ok = True
            for x, y in pairs:
                if (sum(a * b for a, b in zip(coeffs, x)) + v) % 26 != y:
                    ok = False
                    break
            if ok:
                sols.append((coeffs, v))
    return sols


def run(n, alpha_name, alpha, affine):
    inv = {ch: i for i, ch in enumerate(alpha)}
    for offset in range(n):
        blks = blocks(n, offset)
        rows_enc, rows_dec = [], []
        for r in range(n):
            pairs_enc = [(tuple(inv[ch] for ch in p), inv[c[r]]) for p, c, _ in blks]
            pairs_dec = [(tuple(inv[ch] for ch in c), inv[p[r]]) for p, c, _ in blks]
            rows_enc.append(row_solutions(n, pairs_enc, affine))
            rows_dec.append(row_solutions(n, pairs_dec, affine))
        rec = {"n": n, "alpha": alpha_name, "affine": affine, "offset_1idx": offset + 1,
               "blocks": [(p, c, s) for p, c, s in blks],
               "enc_row_solution_counts": [len(r) for r in rows_enc],
               "dec_row_solution_counts": [len(r) for r in rows_dec]}
        full_enc = all(rows_enc)
        full_dec = all(rows_dec)
        rec["consistent_encryption_key_exists"] = full_enc
        rec["consistent_decryption_key_exists"] = full_dec
        RESULTS.append(rec)
        tag = "affine " if affine else ""
        print(f"{n}x{n} {tag}{alpha_name:8s} blocks aligned from pos {offset+1}: {len(blks)} crib blocks "
              f"{[s for _,_,s in blks]}; per-row solutions enc={rec['enc_row_solution_counts']} "
              f"dec={rec['dec_row_solution_counts']} -> {'CONSISTENT KEY' if full_enc or full_dec else 'no key'}")
        if full_enc or full_dec:
            for r in range(n):
                print("    enc row", r, rows_enc[r][:5], " dec row", r, rows_dec[r][:5])


if __name__ == "__main__":
    print("Hill cipher crib consistency (rows solved independently; 'no key' means at least one row has zero solutions)")
    print("Note: 97 is not divisible by 2 or 3, so a genuine Hill K4 would need padding or a stray letter.")
    for n in (2, 3):
        for alpha_name, alpha in (("straight", A2Z), ("kryptos", KRYPTOS_ALPHA)):
            for affine in (False, True):
                run(n, alpha_name, alpha, affine)
    with open(os.path.join(ROOT, "findings", "hill_results.json"), "w") as f:
        json.dump(RESULTS, f, indent=1)
