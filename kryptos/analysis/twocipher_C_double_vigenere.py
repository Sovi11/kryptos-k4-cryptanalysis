"""(C) Double Vigenere "masking":  ct = E2( E1(pt) )  with two periodic stages that
may use different alphabets, so the composite is NOT a single Vigenere.

Stage k (k=1,2) has family f_k in {vig, beau}, plaintext/ciphertext alphabets
(PA_k, CA_k), period p_k and key shifts s_k[0..p_k-1].  For a crib position i with
c1 = i mod p1, c2 = i mod p2:

    m  = CA1[(PA1.idx(pt) + s1[c1]) % 26]           (vig)   or  CA1[(s1[c1] - PA1.idx(pt)) % 26]  (beau)
    ct = CA2[(PA2.idx(m)  + s2[c2]) % 26]           (vig)   or  CA2[(s2[c2] - PA2.idx(m)) % 26]   (beau)

Given s1[c1], each crib determines s2[c2] uniquely, and vice versa.  So the crib
constraints form a bipartite graph between the p1 "stage-1 columns" and the p2
"stage-2 columns" touched by the 24 crib letters; within each connected component
one free choice (26 values) determines everything and every extra edge (a cycle,
or a second crib letter on the same (c1,c2) pair) is a genuine 1-in-26 check.

We enumerate p1, p2 in 2..12, the four alphabet arrangements for each stage
(plain/plain, KRYPTOS/KRYPTOS, KRYPTOS-pt/plain-ct, plain-pt/KRYPTOS-ct), both
families for each stage, and count consistent (s1, s2) assignments by propagation.
For each configuration we also report the expected number of consistent
assignments under a null model (26 ** (V1 + V2 - 24), V1/V2 = distinct columns
touched), so vacuous "survivals" can be recognised.  Any configuration whose
solution count exceeds its null expectation by a large factor is printed with its
implied (partial) decryption and an English-likelihood judgement.
"""
import sys, os, math, itertools, json
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import twocipher_common as C

N, CT = C.N, C.CT
ALPHS = {
    "P/P": (C.PLAIN, C.PLAIN),
    "K/K": (C.KRYPTOS, C.KRYPTOS),
    "Kpt/Pct": (C.KRYPTOS, C.PLAIN),
    "Ppt/Kct": (C.PLAIN, C.KRYPTOS),
}

def enc(fam, PA, CA, s, pt):
    a = PA.index(pt)
    return CA[(a + s) % 26] if fam == "vig" else CA[(s - a) % 26]

def dec(fam, PA, CA, s, ct):
    b = CA.index(ct)
    return PA[(b - s) % 26] if fam == "vig" else PA[(s - b) % 26]

def s2_from_s1(f1, A1, f2, A2, s1, pt, ct):
    m = enc(f1, A1[0], A1[1], s1, pt)
    return C.shift_for(f2, A2[0], A2[1], m, ct)

def s1_from_s2(f1, A1, f2, A2, s2, pt, ct):
    m = dec(f2, A2[0], A2[1], s2, ct)
    return C.shift_for(f1, A1[0], A1[1], pt, m)

def solve(p1, p2, f1, A1, f2, A2, cribs=C.CRIBS):
    """Return (solutions, V1, V2) where solutions is a list of (s1 dict, s2 dict)."""
    edges = [(pos % p1, pos % p2, pt, ct) for pos, ct, pt in cribs]
    adj = defaultdict(list)   # node ('a',c1) / ('b',c2) -> list of (other node, edge)
    for e in edges:
        adj[("a", e[0])].append((("b", e[1]), e))
        adj[("b", e[1])].append((("a", e[0]), e))
    nodes = list(adj.keys())
    V1 = len({n for n in nodes if n[0] == "a"}); V2 = len({n for n in nodes if n[0] == "b"})
    # components
    seen = set(); comps = []
    for n in nodes:
        if n in seen: continue
        stack = [n]; comp = []
        seen.add(n)
        while stack:
            x = stack.pop(); comp.append(x)
            for y, _ in adj[x]:
                if y not in seen:
                    seen.add(y); stack.append(y)
        comps.append(comp)
    # per component: try 26 values for the first node, propagate
    comp_solutions = []
    for comp in comps:
        root = comp[0]
        sols = []
        for v in range(26):
            val = {root: v}
            stack = [root]; ok = True
            while stack and ok:
                x = stack.pop()
                for y, e in adj[x]:
                    c1, c2, pt, ct = e
                    if x[0] == "a":
                        yv = s2_from_s1(f1, A1, f2, A2, val[x], pt, ct)
                    else:
                        yv = s1_from_s2(f1, A1, f2, A2, val[x], pt, ct)
                    if y in val:
                        if val[y] != yv: ok = False; break
                    else:
                        val[y] = yv; stack.append(y)
            if ok:
                sols.append(val)
        comp_solutions.append(sols)
    # combine
    solutions = []
    if all(comp_solutions):
        for combo in itertools.product(*comp_solutions):
            s1 = {}; s2 = {}
            for val in combo:
                for n, v in val.items():
                    (s1 if n[0] == "a" else s2)[n[1]] = v
            solutions.append((s1, s2))
    # analytic null: per component, k independent 1-in-26 checks (edges - nodes + 1);
    # 26 free choices -> P(component consistent) = 1 - (1 - 26^-k)^26
    p_cons = 1.0
    comp_nodes = {n: i for i, comp in enumerate(comps) for n in comp}
    edges_per = [0] * len(comps)
    for e in edges:
        edges_per[comp_nodes[("a", e[0])]] += 1
    for i, comp in enumerate(comps):
        k = edges_per[i] - len(comp) + 1
        p_cons *= 1 - (1 - 26.0 ** (-k)) ** 26
    return solutions, V1, V2, len(comps), p_cons

def decrypt(p1, p2, f1, A1, f2, A2, s1, s2):
    out = []
    for i, ch in enumerate(CT):
        c1, c2 = i % p1, i % p2
        if c1 in s1 and c2 in s2:
            m = dec(f2, A2[0], A2[1], s2[c2], ch)
            out.append(dec(f1, A1[0], A1[1], s1[c1], m))
        else:
            out.append(".")
    return "".join(out)

def main(pmin=2, pmax=12, cribs=C.CRIBS, quiet=False):
    rows = []
    total = 0
    for p1 in range(pmin, pmax + 1):
        for p2 in range(pmin, pmax + 1):
            for a1, A1 in ALPHS.items():
                for a2, A2 in ALPHS.items():
                    for f1 in C.FAMILIES:
                        for f2 in C.FAMILIES:
                            total += 1
                            sols, V1, V2, ncomp, pc = solve(p1, p2, f1, A1, f2, A2, cribs)
                            expected = 26.0 ** (V1 + V2 - 24)
                            rows.append((p1, p2, a1, a2, f1, f2, len(sols), expected, V1, V2, ncomp, sols, pc))
    n_cons = sum(1 for r in rows if r[6] > 0)
    if quiet:
        return n_cons, rows
    print(f"(C) double periodic substitution: {total} configurations "
          f"(p1,p2 in {pmin}..{pmax}, 4x4 alphabet arrangements, 2x2 families)")
    n_nonvac = sum(1 for r in rows if r[6] > 0 and r[7] < 1)
    print(f"  consistent (>=1 solution): {n_cons}")
    print(f"  consistent AND null-expectation < 1 (non-vacuous): {n_nonvac}")
    # significance: ratio found/expected
    rows.sort(key=lambda r: -(r[6] / r[7]) if r[6] else 0)
    print("\nTop configurations by (solutions found)/(null expectation):")
    print("  p1 p2  alph1    alph2    f1   f2   found   expected   V1 V2 comps")
    rows_top = [r for r in rows if r[6] > 0][:25] or rows[:10]
    for r in rows_top:
        p1, p2, a1, a2, f1, f2, nf, ex, V1, V2, nc, sols, pc = r
        print(f"  {p1:2d} {p2:2d}  {a1:8s} {a2:8s} {f1:4s} {f2:4s} {nf:5d}  {ex:10.3g}  {V1:2d} {V2:2d} {nc}  P(consistent|null)={pc:.3g}")
    # Table of the smallest-period consistent configurations
    print("\nAll consistent configurations with null expectation < 0.05 (would be surprising):")
    strong = [r for r in rows if r[6] > 0 and r[7] < 0.05]
    if not strong:
        print("  (none)")
    for r in strong:
        p1, p2, a1, a2, f1, f2, nf, ex, V1, V2, nc, sols, pc = r
        print(f"\n  p1={p1} p2={p2} {a1} {a2} {f1}/{f2}: {nf} solutions, expected {ex:.3g}, P(consistent|null)={pc:.3g}")
        for s1, s2 in sols[:5]:
            d = decrypt(p1, p2, f1, ALPHS[a1], f2, ALPHS[a2], s1, s2)
            q, w, verdict = C.english_judgement(d.replace(".", ""))
            print(f"    s1={dict(sorted(s1.items()))} s2={dict(sorted(s2.items()))}")
            print(f"    dec: {d}   quad={q:.2f} wordcov={w:.2f} {verdict}")
    # Distribution check: how does the number of consistent configs compare with chance?
    exp_total = sum(r[12] for r in rows)
    print(f"\nAnalytic null: expected number of consistent configurations = {exp_total:.2f}; observed = {n_cons}.")
    # empirical null: randomise the crib ciphertext letters and recount
    import random
    random.seed(12345)
    trials = 30
    counts = []
    for t in range(trials):
        fake = [(pos, random.choice(C.PLAIN), pt) for pos, ct, pt in C.CRIBS]
        nc_, _ = main(pmin, pmax, cribs=fake, quiet=True)
        counts.append(nc_)
    import statistics
    print(f"Empirical null ({trials} trials with random crib ciphertext letters): consistent configs per trial "
          f"mean={statistics.mean(counts):.2f} sd={statistics.pstdev(counts):.2f} min={min(counts)} max={max(counts)}")
    # Marginal: which (p1,p2) pairs are ever consistent, and with how many checks
    print("\nPer (p1,p2): number of the 64 alphabet/family combos that are consistent, and null expectation per combo")
    byp = defaultdict(lambda: [0, 0.0])
    for r in rows:
        byp[(r[0], r[1])][0] += (r[6] > 0); byp[(r[0], r[1])][1] = r[12]
    for (p1, p2), (k, pc) in sorted(byp.items()):
        if k:
            print(f"  p1={p1:2d} p2={p2:2d}: {k:2d}/64 consistent  (P(consistent|null) per combo {pc:.3g}, i.e. ~{64*pc:.2f} expected)")
    with open(os.path.join(C.HERE, "twocipher_C_results.json"), "w") as f:
        json.dump([{"p1": r[0], "p2": r[1], "alph1": r[2], "alph2": r[3], "f1": r[4], "f2": r[5],
                    "found": r[6], "expected": r[7], "V1": r[8], "V2": r[9], "comps": r[10], "p_consistent_null": r[12]} for r in rows], f)

if __name__ == "__main__":
    pmax = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    main(2, pmax)
