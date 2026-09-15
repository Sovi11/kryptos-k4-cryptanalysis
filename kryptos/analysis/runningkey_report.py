"""Driver: runs all running-key/autokey tests and writes findings/runningkey.md."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import runningkey_lib as L
import runningkey_search, runningkey_autokey, runningkey_prefix_period

def main():
    parts = ["# K4: running-key / autokey hypotheses using the sculpture's own text\n",
             f"Generated {time.strftime('%Y-%m-%d %H:%M')} by analysis/runningkey_report.py.\n"]
    v = L.verify_k1_k2()
    parts.append("## 0. Data sanity checks\n")
    parts.append(f"- K4 ciphertext: 97 letters; 24 crib letters at 1-indexed 22-34 (EASTNORTHEAST) and 64-74 (BERLINCLOCK) agree with the ciphertext file.")
    parts.append(f"- K1 ciphertext (from the panel transcription) re-derived from K1 plaintext with key PALIMPSEST, Vigenere with KRYPTOS-keyed pt/ct/key alphabets: match = {v['K1'][0]}.")
    parts.append(f"- K2: re-encryption with ABSCISSA matches the carved ciphertext for the first {v['K2'][0]} letters; the carved text is then missing one letter (expected `{v['K2'][3]}`, carved `{v['K2'][4]}`), the known Sanborn error. Carved K2 ct = {v['K2'][2]} letters, plaintext = {v['K2'][1]}.")
    parts.append(f"- K3 ciphertext is an exact anagram of K3 plaintext: {v['K3_is_anagram_of_pt']}.")
    parts.append(f"- Tableau (right panel) transcription: {len(L.TABLEAU)} letters (ideal tableau would be {len(L.TABLEAU_IDEAL)}; the physical one has the extra L in row N).\n")
    t = time.time(); parts.append(runningkey_search.run()); parts.append(f"\n_(search runtime {time.time()-t:.0f}s)_\n")
    t = time.time(); parts.append(runningkey_autokey.run()); parts.append(f"\n_(autokey runtime {time.time()-t:.0f}s)_\n")
    t = time.time(); parts.append(runningkey_prefix_period.run()); parts.append(f"\n_(prefix-period runtime {time.time()-t:.0f}s)_\n")
    out = os.path.join(L.ROOT, "findings", "runningkey.md")
    with open(out, "w") as f:
        f.write("\n".join(parts))
    print("wrote", out)

if __name__ == "__main__":
    main()
