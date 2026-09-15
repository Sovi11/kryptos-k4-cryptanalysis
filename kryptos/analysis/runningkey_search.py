"""Items 1+2: running-key search.  For each of the 24 (family, alphabets) combos derive the
required key letters at the crib positions (13-letter block at 1-indexed 22-34, 11-letter
block at 64-74, offset 42) and search every candidate key text for them:
exact single-block hits, exact joint hits (block2 exactly 42 after block1), and fuzzy hits
(Hamming <= 2 per block, joint Hamming <= 4).  Also an extension where the key alphabet is
allowed an unknown constant rotation (index convention uncertainty)."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import runningkey_lib as L
from math import comb

def p_hamming_le(n, k):
    return sum(comb(n, j) * (25/26)**j * (1/26)**(n-j) for j in range(k+1))

def scan(text, block):
    n = len(block)
    return [(o, L.hamming(text[o:o+n], block)) for o in range(len(text) - n + 1)]

def joint_scan(text, b1, b2, gap=42):
    out = []
    for o in range(len(text) - (gap + len(b2)) + 1):
        out.append((o, L.hamming(text[o:o+len(b1)], b1) + L.hamming(text[o+gap:o+gap+len(b2)], b2)))
    return out

def rotate_key(block, ak, r):
    A = L.ALPHAS[ak]
    return "".join(A[(A.index(ch) + r) % 26] for ch in block)

def full_decrypt_from_text(cb, text, o):
    """Key stream = text aligned so that text[o] is the key for K4 position 21 (1-idx 22)."""
    start = o - 21
    ks = []
    for i in range(97):
        j = start + i
        ks.append(text[j] if 0 <= j < len(text) else None)
    pt = "".join(L.decrypt_letter(cb, L.K4_CT[i], k) if k else "." for i, k in enumerate(ks))
    return pt

def run():
    corpus = L.corpus()
    md = []
    md.append("## 1-2. Running key drawn from the sculpture's own texts\n")
    md.append("### Required key letters at the crib positions (per cipher family / alphabet combo)\n")
    md.append("Alphabet naming: pt=keyed,ct=plain is Quagmire-I style; pt=plain,ct=keyed is Quagmire-II style; "
              "pt=keyed,ct=keyed is Quagmire-III style (this is the K1/K2 system, verified by re-encryption); "
              "key=keyed/plain says which alphabet the key letter is read from.\n")
    md.append("| combo | key @22-34 (for EASTNORTHEAST) | key @64-74 (for BERLINCLOCK) |\n|---|---|---|")
    reqs = {}
    for cb in L.combos():
        b1, b2 = L.required_key(cb)
        reqs[cb] = (b1, b2)
        md.append(f"| {L.combo_name(cb)} | `{b1}` | `{b2}` |")
    distinct = len(set(reqs.values()))
    md.append(f"\n{len(reqs)} combos, {distinct} distinct (block1, block2) key-pairs.\n")

    md.append("### Corpus of candidate key texts\n")
    md.append("| text | letters |\n|---|---|")
    for n, t in corpus.items():
        if not n.endswith("_rev"):
            md.append(f"| {n} (+ reversed) | {len(t)} |")
    md.append(f"\nTotal {len(corpus)} texts including reversed copies and X-stripped copies. "
              "Texts: K1/K2/K3 plaintexts (K2 both with the 2006 LAYERTWO ending and the older IDBYROWS reading), "
              "their concatenation, K1/K2/K3/K4 ciphertexts as on the left panel (K2 ct as carved, i.e. 369 letters), "
              "the whole left panel, the physical right-panel tableau (867 letters, with the anomalous extra L), the ideal "
              "tableau, the tableau with row labels removed, the Morse text in two orderings, and the keywords.\n")

    exact1 = exact2 = joint_exact = 0
    fuzzy1 = []; fuzzy2 = []; fuzzyj = []
    best1 = (99, None); best2 = (99, None); bestj = (99, None)
    ncomp1 = ncomp2 = ncompj = 0
    hist1 = {}; hist2 = {}; histj = {}
    hits_detail = []
    for cb in L.combos():
        b1, b2 = reqs[cb]
        for name, text in corpus.items():
            s1 = scan(text, b1); s2 = scan(text, b2); sj = joint_scan(text, b1, b2)
            ncomp1 += len(s1); ncomp2 += len(s2); ncompj += len(sj)
            for o, h in s1:
                hist1[h] = hist1.get(h, 0) + 1
                if h == 0: exact1 += 1
                if h <= 2: fuzzy1.append((cb, name, o, h, text[o:o+13]))
                if h < best1[0]: best1 = (h, (cb, name, o, text[o:o+13]))
            for o, h in s2:
                hist2[h] = hist2.get(h, 0) + 1
                if h == 0: exact2 += 1
                if h <= 2: fuzzy2.append((cb, name, o, h, text[o:o+11]))
                if h < best2[0]: best2 = (h, (cb, name, o, text[o:o+11]))
            for o, h in sj:
                histj[h] = histj.get(h, 0) + 1
                if h == 0: joint_exact += 1
                if h <= 4: fuzzyj.append((cb, name, o, h))
                if h < bestj[0]: bestj = (h, (cb, name, o))

    md.append("### Results: exact and fuzzy search (no rotation)\n")
    md.append(f"- Block-1 (13 letters) comparisons: {ncomp1:,}. Exact hits: **{exact1}**. Hits with Hamming<=2: **{len(fuzzy1)}**. "
              f"Best (minimum) Hamming distance seen: **{best1[0]}/13** at {best1[1][1]} offset {best1[1][2]} under {L.combo_name(best1[1][0])} (text there: `{best1[1][3]}`).")
    md.append(f"- Block-2 (11 letters) comparisons: {ncomp2:,}. Exact hits: **{exact2}**. Hits with Hamming<=2: **{len(fuzzy2)}**. "
              f"Best Hamming: **{best2[0]}/11** at {best2[1][1]} offset {best2[1][2]} under {L.combo_name(best2[1][0])} (text there: `{best2[1][3]}`).")
    md.append(f"- Joint (block1 at o, block2 at o+42; 24 letters) comparisons: {ncompj:,}. Exact joint hits: **{joint_exact}**. "
              f"Joint Hamming<=4: **{len(fuzzyj)}**. Best joint Hamming: **{bestj[0]}/24** at {bestj[1][1]} offset {bestj[1][2]} under {L.combo_name(bestj[1][0])}.")
    md.append("")
    md.append("Observed Hamming-distance histogram vs. expectation for random 26-letter text (the corpus is not random and the "
              "reversed/X-stripped copies are correlated, so the expectation is only a guide):\n")
    md.append("| block | h | observed | expected if random |\n|---|---|---|---|")
    for lab, hist, n, ncomp in (("block1", hist1, 13, ncomp1), ("block2", hist2, 11, ncomp2), ("joint", histj, 24, ncompj)):
        for h in range(0, 8):
            exp = ncomp * (comb(n, h) * (25/26)**h * (1/26)**(n-h))
            md.append(f"| {lab} | {h} | {hist.get(h,0)} | {exp:.3g} |")
    md.append("")
    for lab, lst in (("block1 Hamming<=2", fuzzy1), ("block2 Hamming<=2", fuzzy2), ("joint Hamming<=4", fuzzyj)):
        if lst:
            md.append(f"**{lab} partial hits:**\n")
            for item in lst:
                md.append(f"- {L.combo_name(item[0])}, text {item[1]}, offset {item[2]} (0-indexed), h={item[3]}")
        else:
            md.append(f"No {lab} hits.")
    md.append("")

    # rotation-tolerant extension
    md.append("### Extension: unknown constant rotation of the key alphabet\n")
    md.append("If the tableau were read with a different index convention (e.g. key letter K meaning 'no shift' vs 'shift 1'), "
              "the required key string would be the derived one rotated by a constant r in the key alphabet.  "
              "Search repeated for r = 0..25 (only the joint offset-42 test and per-block exact/fuzzy tests are reported).\n")
    rot_exact_j = 0; rot_fuzzy_j = []; rot_best = (99, None); rot_exact_single = []
    ncomp = 0
    for cb in L.combos():
        b1, b2 = reqs[cb]
        for r in range(26):
            rb1, rb2 = rotate_key(b1, cb[3], r), rotate_key(b2, cb[3], r)
            for name, text in corpus.items():
                for o, h in joint_scan(text, rb1, rb2):
                    ncomp += 1
                    if h == 0: rot_exact_j += 1
                    if h <= 4: rot_fuzzy_j.append((cb, r, name, o, h))
                    if h < rot_best[0]: rot_best = (h, (cb, r, name, o))
                if r:
                    for o, h in scan(text, rb1):
                        if h <= 1: rot_exact_single.append(("block1", cb, r, name, o, h, text[o:o+13]))
                    for o, h in scan(text, rb2):
                        if h <= 1: rot_exact_single.append(("block2", cb, r, name, o, h, text[o:o+11]))
    md.append(f"- Joint comparisons: {ncomp:,}. Exact joint hits: **{rot_exact_j}**. Joint Hamming<=4: **{len(rot_fuzzy_j)}**. "
              f"Best joint Hamming: **{rot_best[0]}/24** ({L.combo_name(rot_best[1][0])}, r={rot_best[1][1]}, {rot_best[1][2]}, offset {rot_best[1][3]}).")
    md.append(f"- Single-block hits with Hamming<=1 for r=1..25: **{len(rot_exact_single)}**.")
    for it in rot_exact_single:
        md.append(f"  - {it[0]}: {L.combo_name(it[1])}, r={it[2]}, {it[3]}, offset {it[4]}, h={it[5]}, text `{it[6]}`")
    for it in rot_fuzzy_j:
        md.append(f"  - joint: {L.combo_name(it[0])}, r={it[1]}, {it[2]}, offset {it[3]}, h={it[4]}")
    md.append("")
    # If any exact joint hit exists, show decryption
    if joint_exact or rot_exact_j:
        md.append("### Full decryptions implied by exact joint hits\n")
        for cb in L.combos():
            b1, b2 = reqs[cb]
            for r in range(26):
                rb1, rb2 = rotate_key(b1, cb[3], r), rotate_key(b2, cb[3], r)
                for name, text in corpus.items():
                    for o, h in joint_scan(text, rb1, rb2):
                        if h == 0:
                            pt = full_decrypt_from_text(cb, text, o)
                            md.append(f"- {L.combo_name(cb)} r={r} {name} offset {o}: `{pt}` (english score {L.english_score(pt):.2f})")
    return "\n".join(md)

if __name__ == "__main__":
    print(run())
