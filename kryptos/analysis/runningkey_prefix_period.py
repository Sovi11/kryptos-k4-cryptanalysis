"""Item 4: key = first N letters of a sculpture text, repeated with period N (N = 1..97),
checked against the 24 crib letters under all 24 combos.  Also the variant where the
repeated block starts at an arbitrary offset s of the text (s<len(text)), for N in 5..97."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import runningkey_lib as L

def check(cb, key):
    """key: function i -> key letter. returns (checks, matches)."""
    m = 0
    for i, pl in L.CRIBS.items():
        if L.derive_key_letter(cb, pl, L.K4_CT[i]) == key(i): m += 1
    return m

def run():
    corpus = L.corpus()
    md = ["## 4. Key = first N letters of a sculpture text, repeated (period N)\n"]
    md.append("For every text in the corpus, every N = 1..min(97, len), every combo: count crib letters matched "
              "(24 total; expected ~0.92 by chance). A survivor needs 24/24.\n")
    total = 0; best = (0, None); surv = []
    hist = {}
    for name, text in corpus.items():
        for Nn in range(1, min(97, len(text)) + 1):
            for cb in L.combos():
                total += 1
                m = check(cb, lambda i: text[i % Nn])
                hist[m] = hist.get(m, 0) + 1
                if m > best[0]: best = (m, (cb, name, Nn))
                if m == 24: surv.append((cb, name, Nn))
    md.append(f"Tests: {total:,}. Survivors (24/24): **{len(surv)}**. Best match count: **{best[0]}/24** "
              f"({L.combo_name(best[1][0])}, {best[1][1]}, N={best[1][2]}).")
    md.append("Histogram of matched crib letters: " + ", ".join(f"{k}:{hist[k]}" for k in sorted(hist)))
    for cb, name, Nn in surv:
        pt = L.decrypt(cb, L.K4_CT, [corpus[name][i % Nn] for i in range(97)])
        md.append(f"- SURVIVOR {L.combo_name(cb)} {name} N={Nn}: `{pt}`")
    md.append("")
    md.append("### Extension: repeated block taken from an arbitrary start offset s in the text (N = 5..97)\n")
    total = 0; best = (0, None); surv = []; hist = {}
    for name, text in corpus.items():
        if name.endswith("_rev") or name.endswith("_noX"): continue
        for s in range(len(text)):
            for Nn in range(5, min(97, len(text) - s) + 1):
                seg = text[s:s+Nn]
                for cb in L.combos():
                    total += 1
                    m = check(cb, lambda i: seg[i % Nn])
                    hist[m] = hist.get(m, 0) + 1
                    if m > best[0]: best = (m, (cb, name, s, Nn))
                    if m == 24: surv.append((cb, name, s, Nn))
    md.append(f"Tests: {total:,}. Survivors (24/24): **{len(surv)}**. Best match count: **{best[0]}/24** "
              f"({L.combo_name(best[1][0])}, {best[1][1]}, s={best[1][2]}, N={best[1][3]}).")
    md.append("Histogram of matched crib letters: " + ", ".join(f"{k}:{hist[k]}" for k in sorted(hist)))
    for cb, name, s, Nn in surv:
        seg = corpus[name][s:s+Nn]
        pt = L.decrypt(cb, L.K4_CT, [seg[i % Nn] for i in range(97)])
        md.append(f"- SURVIVOR {L.combo_name(cb)} {name} s={s} N={Nn}: `{pt}`")
    return "\n".join(md)

if __name__ == "__main__":
    print(run())
