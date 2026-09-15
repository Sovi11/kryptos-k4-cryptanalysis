# K4: running-key / autokey hypotheses using the sculpture's own text

Generated 2026-09-12 00:44 by analysis/runningkey_report.py.

## 0. Data sanity checks

- K4 ciphertext: 97 letters; 24 crib letters at 1-indexed 22-34 (EASTNORTHEAST) and 64-74 (BERLINCLOCK) agree with the ciphertext file.
- K1 ciphertext (from the panel transcription) re-derived from K1 plaintext with key PALIMPSEST, Vigenere with KRYPTOS-keyed pt/ct/key alphabets: match = True.
- K2: re-encryption with ABSCISSA matches the carved ciphertext for the first 361 letters; the carved text is then missing one letter (expected `SWJLLAETG`, carved `WJLLAETG`), the known Sanborn error. Carved K2 ct = 369 letters, plaintext = 370.
- K3 ciphertext is an exact anagram of K3 plaintext: True.
- Tableau (right panel) transcription: 867 letters (ideal tableau would be 866; the physical one has the extra L in row N).

## 1-2. Running key drawn from the sculpture's own texts

### Required key letters at the crib positions (per cipher family / alphabet combo)

Alphabet naming: pt=keyed,ct=plain is Quagmire-I style; pt=plain,ct=keyed is Quagmire-II style; pt=keyed,ct=keyed is Quagmire-III style (this is the K1/K2 system, verified by re-encryption); key=keyed/plain says which alphabet the key letter is read from.

| combo | key @22-34 (for EASTNORTHEAST) | key @64-74 (for BERLINCLOCK) |
|---|---|---|
| vigenere/pt=plain/ct=plain/key=plain | `BLZCDCYYGCKAZ` | `MUYKLGKORNA` |
| vigenere/pt=plain/ct=plain/key=keyed | `REZYPYXXSYDKZ` | `FQXDESDHLGK` |
| vigenere/pt=plain/ct=keyed/key=plain | `IRJDHGMIMJAON` | `SYMLWRQOYBQ` |
| vigenere/pt=plain/ct=keyed/key=keyed | `BLCPASFBFCKHG` | `MXFEVLJHXRJ` |
| vigenere/pt=keyed/ct=plain/key=plain | `UELRXLONZVDMO` | `FNOEEADIAGK` |
| vigenere/pt=keyed/ct=plain/key=keyed | `QTELWEHGZUPFH` | `OGHTTKPBKSD` |
| vigenere/pt=keyed/ct=keyed/key=plain | `BKVSBPCXFCTAC` | `LRCFPLJIHUA` |
| vigenere/pt=keyed/ct=keyed/key=keyed | `RDUMRIYWOYNKY` | `ELYOIECBAQK` |
| beaufort/pt=plain/ct=plain/key=plain | `JLJODEGKUKKKL` | `OCGGBGOKTRU` |
| beaufort/pt=plain/ct=plain/key=keyed | `CECHPTSDQDDDE` | `HYSSRSHDNLQ` |
| beaufort/pt=plain/ct=keyed/key=plain | `QRTPHIUUARAYZ` | `UGUHMRUKAFK` |
| beaufort/pt=plain/ct=keyed/key=keyed | `JLNIABQQKLKXZ` | `QSQAFLQDKOD` |
| beaufort/pt=keyed/ct=plain/key=plain | `QSXZJVQVBRRYW` | `VJQMIMVQKYK` |
| beaufort/pt=keyed/ct=plain/key=keyed | `JMWZCUJURLLXV` | `UCJFBFUJDXD` |
| beaufort/pt=keyed/ct=keyed/key=plain | `XYHANZEFHYHMK` | `BNENTXBQRMA` |
| beaufort/pt=keyed/ct=keyed/key=keyed | `WXAKGZTOAXAFD` | `RGTGNWRJLFK` |
| varbeaufort/pt=plain/ct=plain/key=plain | `ZPBYXYCCUYQAB` | `OGCQPUQMJNA` |
| varbeaufort/pt=plain/ct=plain/key=keyed | `ZIRXWXYYQXJKR` | `HSYJIQJFCGK` |
| varbeaufort/pt=plain/ct=keyed/key=plain | `SJRXTUOSORAMN` | `ICOPEJKMCZK` |
| varbeaufort/pt=plain/ct=keyed/key=keyed | `MCLWNQHMHLKFG` | `BYHITCDFYZD` |
| varbeaufort/pt=keyed/ct=plain/key=plain | `GWPJDPMNBFXOM` | `VNMWWAXSAUQ` |
| varbeaufort/pt=keyed/ct=plain/key=keyed | `SVICPIFGROWHF` | `UGFVVKWMKQJ` |
| varbeaufort/pt=keyed/ct=keyed/key=plain | `ZQFIZLYDVYHAY` | `PJYVLPRSTGA` |
| varbeaufort/pt=keyed/ct=keyed/key=keyed | `ZJOBZEXPUXAKX` | `ICXUEILMNSK` |

24 combos, 24 distinct (block1, block2) key-pairs.

### Corpus of candidate key texts

| text | letters |
|---|---|
| K1_pt (+ reversed) | 63 |
| K2_pt (+ reversed) | 370 |
| K2_pt_IDBYROWS (+ reversed) | 369 |
| K3_pt (+ reversed) | 336 |
| K1K2K3_pt (+ reversed) | 769 |
| K1K2K3_pt_IDBYROWS (+ reversed) | 768 |
| K1_ct (+ reversed) | 63 |
| K2_ct (+ reversed) | 369 |
| K3_ct (+ reversed) | 336 |
| K4_ct (+ reversed) | 97 |
| K1K2K3_ct (+ reversed) | 768 |
| left_panel_all_ct (+ reversed) | 865 |
| K3K4_ct_lower_panel (+ reversed) | 433 |
| tableau_physical (+ reversed) | 867 |
| tableau_ideal (+ reversed) | 866 |
| tableau_rows_no_labels (+ reversed) | 841 |
| morse (+ reversed) | 80 |
| morse_alt_order (+ reversed) | 80 |
| keywords (+ reversed) | 25 |
| K1K2K3_pt_plus_keywords (+ reversed) | 787 |
| K2_pt_noX (+ reversed) | 363 |
| K2_pt_IDBYROWS_noX (+ reversed) | 363 |
| K3_pt_noX (+ reversed) | 335 |
| K1K2K3_pt_noX (+ reversed) | 761 |
| K1K2K3_pt_IDBYROWS_noX (+ reversed) | 761 |
| K1_ct_noX (+ reversed) | 61 |
| K2_ct_noX (+ reversed) | 362 |
| K3_ct_noX (+ reversed) | 335 |
| K4_ct_noX (+ reversed) | 95 |
| K1K2K3_ct_noX (+ reversed) | 758 |
| left_panel_all_ct_noX (+ reversed) | 853 |
| K3K4_ct_lower_panel_noX (+ reversed) | 430 |
| K1K2K3_pt_plus_keywords_noX (+ reversed) | 779 |

Total 66 texts including reversed copies and X-stripped copies. Texts: K1/K2/K3 plaintexts (K2 both with the 2006 LAYERTWO ending and the older IDBYROWS reading), their concatenation, K1/K2/K3/K4 ciphertexts as on the left panel (K2 ct as carved, i.e. 369 letters), the whole left panel, the physical right-panel tableau (867 letters, with the anomalous extra L), the ideal tableau, the tableau with row labels removed, the Morse text in two orderings, and the keywords.

### Results: exact and fuzzy search (no rotation)

- Block-1 (13 letters) comparisons: 720,576. Exact hits: **0**. Hits with Hamming<=2: **0**. Best (minimum) Hamming distance seen: **7/13** at K1_ct offset 6 under varbeaufort/pt=plain/ct=plain/key=keyed (text there: `ZLRFAXYUSDJKZ`).
- Block-2 (11 letters) comparisons: 723,744. Exact hits: **0**. Hits with Hamming<=2: **0**. Best Hamming: **6/11** at K2_ct_noX offset 282 under vigenere/pt=keyed/ct=plain/key=plain (text there: `FVOEEBDMVPN`).
- Joint (block1 at o, block2 at o+42; 24 letters) comparisons: 658,512. Exact joint hits: **0**. Joint Hamming<=4: **0**. Best joint Hamming: **16/24** at K1_ct offset 6 under varbeaufort/pt=plain/ct=plain/key=keyed.

Observed Hamming-distance histogram vs. expectation for random 26-letter text (the corpus is not random and the reversed/X-stripped copies are correlated, so the expectation is only a guide):

| block | h | observed | expected if random |
|---|---|---|---|
| block1 | 0 | 0 | 2.9e-13 |
| block1 | 1 | 0 | 9.44e-11 |
| block1 | 2 | 0 | 1.42e-08 |
| block1 | 3 | 0 | 1.3e-06 |
| block1 | 4 | 0 | 8.11e-05 |
| block1 | 5 | 0 | 0.00365 |
| block1 | 6 | 0 | 0.122 |
| block1 | 7 | 3 | 3.04 |
| block2 | 0 | 0 | 1.97e-10 |
| block2 | 1 | 0 | 5.42e-08 |
| block2 | 2 | 0 | 6.78e-06 |
| block2 | 3 | 0 | 0.000508 |
| block2 | 4 | 0 | 0.0254 |
| block2 | 5 | 0 | 0.89 |
| block2 | 6 | 38 | 22.2 |
| block2 | 7 | 384 | 397 |
| joint | 0 | 0 | 7.23e-29 |
| joint | 1 | 0 | 4.34e-26 |
| joint | 2 | 0 | 1.25e-23 |
| joint | 3 | 0 | 2.29e-21 |
| joint | 4 | 0 | 3e-19 |
| joint | 5 | 0 | 3e-17 |
| joint | 6 | 0 | 2.38e-15 |
| joint | 7 | 0 | 1.53e-13 |

No block1 Hamming<=2 hits.
No block2 Hamming<=2 hits.
No joint Hamming<=4 hits.

### Extension: unknown constant rotation of the key alphabet

If the tableau were read with a different index convention (e.g. key letter K meaning 'no shift' vs 'shift 1'), the required key string would be the derived one rotated by a constant r in the key alphabet.  Search repeated for r = 0..25 (only the joint offset-42 test and per-block exact/fuzzy tests are reported).

- Joint comparisons: 17,121,312. Exact joint hits: **0**. Joint Hamming<=4: **0**. Best joint Hamming: **16/24** (vigenere/pt=keyed/ct=plain/key=plain, r=12, tableau_physical_rev, offset 792).
- Single-block hits with Hamming<=1 for r=1..25: **0**.


_(search runtime 69s)_

## 3. Autokey (plaintext-autokey and ciphertext-autokey)

### Plaintext autokey

For each (combo, p): propagate the cribs through the autokey chain in both directions; `checks` = number of positions reached twice (consistency tests), `conflicts` = failed checks. A (combo, p) survives only if checks>0 and conflicts=0.  With plaintext autokey the cribs determine the plaintext on every residue class mod p that contains a crib, so a survivor yields a large partial decryption.

Tested 2304 (combo, p) pairs (24 combos x p=1..96).

Per-p summary for p=1..21 (over the 24 combos): number of checks available, and min conflicts over combos:

| p | checks (per combo) | combos with 0 conflicts | min conflicts |
|---|---|---|---|
| 1 | 23 | 0 | 20 |
| 2 | 22 | 0 | 19 |
| 3 | 21 | 0 | 18 |
| 4 | 20 | 0 | 17 |
| 5 | 19 | 0 | 17 |
| 6 | 18 | 0 | 16 |
| 7 | 17 | 0 | 15 |
| 8 | 16 | 0 | 14 |
| 9 | 15 | 0 | 11 |
| 10 | 14 | 0 | 11 |
| 11 | 13 | 0 | 11 |
| 12 | 12 | 0 | 9 |
| 13 | 11 | 0 | 8 |
| 14 | 11 | 0 | 9 |
| 15 | 9 | 0 | 7 |
| 16 | 8 | 0 | 6 |
| 17 | 7 | 0 | 6 |
| 18 | 7 | 0 | 5 |
| 19 | 9 | 0 | 8 |
| 20 | 11 | 0 | 9 |
| 21 | 11 | 0 | 9 |

**Survivors with checks>0 and 0 conflicts (all p=1..96): 1** (expected by chance, assuming independent uniform letters: 2.84).  Survivors by number of checks: 1 checks: 1

Checks available per p for p=22..52 (24 combos each; p>=53 has no two cribs in one chain): p22:9, p23:7, p24:5, p25:3, p26:1, p27:0, p28:0, p29:0, p30:1, p31:2, p32:3, p33:4, p34:5, p35:6, p36:7, p37:8, p38:9, p39:10, p40:11, p41:11, p42:11, p43:10, p44:9, p45:8, p46:7, p47:6, p48:5, p49:4, p50:3, p51:2, p52:1

Survivors with >=3 checks (chance probability <= 26^-3 = 5.7e-5 each):

- none

All survivors with 1-2 checks (chance level; the forced partial plaintext is shown so it can be eyeballed):

- varbeaufort/pt=plain/ct=plain/key=keyed, p=26, checks=1: pt=`XYYQXJKR...HYSKMXLRMAEASTNORTHEAST...HSYJIQJFCGKDGXCPMYRTHCM...BERLINCLOCKGTBTCPVKGRRY...CLVVZVJI` (score 0.20)

Vacuous (checks=0) pairs: 1128 — these are p values for which no two crib positions are linked by the chain, so the cribs impose no constraint; they are listed below with the partial plaintext the cribs force, for eyeballing:

p with zero checks for every combo: [27, 28, 29, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96]

Top-10 partial decryptions (by crude English bigram/trigram score) among vacuous (combo,p):

- vigenere/pt=plain/ct=plain/key=plain, p=76: `.....................EASTNORTHEAST.............................BERLINCLOCK.......................` score 0.54
- vigenere/pt=plain/ct=plain/key=keyed, p=76: `.....................EASTNORTHEAST.............................BERLINCLOCK.......................` score 0.54
- vigenere/pt=plain/ct=keyed/key=plain, p=76: `.....................EASTNORTHEAST.............................BERLINCLOCK.......................` score 0.54
- vigenere/pt=plain/ct=keyed/key=keyed, p=76: `.....................EASTNORTHEAST.............................BERLINCLOCK.......................` score 0.54
- vigenere/pt=keyed/ct=plain/key=plain, p=76: `.....................EASTNORTHEAST.............................BERLINCLOCK.......................` score 0.54
- vigenere/pt=keyed/ct=plain/key=keyed, p=76: `.....................EASTNORTHEAST.............................BERLINCLOCK.......................` score 0.54
- vigenere/pt=keyed/ct=keyed/key=plain, p=76: `.....................EASTNORTHEAST.............................BERLINCLOCK.......................` score 0.54
- vigenere/pt=keyed/ct=keyed/key=keyed, p=76: `.....................EASTNORTHEAST.............................BERLINCLOCK.......................` score 0.54
- beaufort/pt=plain/ct=plain/key=plain, p=76: `.....................EASTNORTHEAST.............................BERLINCLOCK.......................` score 0.54
- beaufort/pt=plain/ct=plain/key=keyed, p=76: `.....................EASTNORTHEAST.............................BERLINCLOCK.......................` score 0.54

### Ciphertext autokey

key_i = C_{i-p} for i>=p, so each crib position i>=p is one hard letter test. Expected matches under randomness = checks/26.

| p | checks | best matches over 24 combos | combo(s) achieving it |
|---|---|---|---|
| 1 | 24 | 3 | vigenere/pt=keyed/ct=plain/key=plain, varbeaufort/pt=plain/ct=keyed/key=keyed, varbeaufort/pt=keyed/ct=plain/key=keyed, varbeaufort/pt=keyed/ct=keyed/key=keyed |
| 2 | 24 | 3 | beaufort/pt=keyed/ct=plain/key=plain |
| 3 | 24 | 2 | - |
| 4 | 24 | 2 | - |
| 5 | 24 | 2 | - |
| 6 | 24 | 2 | - |
| 7 | 24 | 2 | - |
| 8 | 24 | 3 | vigenere/pt=keyed/ct=keyed/key=keyed, beaufort/pt=plain/ct=keyed/key=keyed, beaufort/pt=keyed/ct=plain/key=plain |
| 9 | 24 | 3 | beaufort/pt=keyed/ct=plain/key=keyed |
| 10 | 24 | 2 | - |
| 11 | 24 | 4 | vigenere/pt=keyed/ct=plain/key=plain |
| 12 | 24 | 3 | varbeaufort/pt=keyed/ct=keyed/key=keyed |
| 13 | 24 | 2 | - |
| 14 | 24 | 3 | vigenere/pt=keyed/ct=plain/key=plain |
| 15 | 24 | 3 | beaufort/pt=plain/ct=keyed/key=keyed |
| 16 | 24 | 3 | beaufort/pt=keyed/ct=plain/key=keyed, varbeaufort/pt=keyed/ct=plain/key=keyed |
| 17 | 24 | 2 | - |
| 18 | 24 | 3 | varbeaufort/pt=keyed/ct=plain/key=plain |
| 19 | 24 | 4 | beaufort/pt=plain/ct=plain/key=plain |
| 20 | 24 | 2 | - |
| 21 | 24 | 2 | - |

Tested 2304 (combo, p) pairs. **Full survivors (all checks pass, checks>0): 0**

_(autokey runtime 0s)_

## 4. Key = first N letters of a sculpture text, repeated (period N)

For every text in the corpus, every N = 1..min(97, len), every combo: count crib letters matched (24 total; expected ~0.92 by chance). A survivor needs 24/24.

Tests: 143,472. Survivors (24/24): **0**. Best match count: **7/24** (beaufort/pt=plain/ct=keyed/key=plain, K4_ct_rev, N=10).
Histogram of matched crib letters: 0:60939, 1:50172, 2:22594, 3:7856, 4:1584, 5:293, 6:28, 7:6

### Extension: repeated block taken from an arbitrary start offset s in the text (N = 5..97)

Tests: 18,290,064. Survivors (24/24): **0**. Best match count: **8/24** (varbeaufort/pt=plain/ct=keyed/key=keyed, K3_pt, s=102, N=7).
Histogram of matched crib letters: 0:7566301, 1:6621742, 2:2973649, 3:891354, 4:196174, 5:34725, 6:5702, 7:393, 8:24

_(prefix-period runtime 133s)_
