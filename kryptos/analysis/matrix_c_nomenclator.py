"""(d) NOMENCLATOR / CODEBOOK: are short ciphertext runs code groups rather
than enciphered letters?

A nomenclator (or its 20th-century descendant, the codebook + superencipherment)
replaces whole words or syllables with fixed groups.  Its defining property is
that it is NOT length-preserving: the group that stands for a word has no
relation to the word's length.  That is exactly what the four Sanborn cribs let
us test, and it is also what makes the "some of K4 is code groups" hypothesis
testable in the gaps between the cribs.

  C1  the four cribs are exactly length-matched -- what that costs a codebook
  C2  tiling arithmetic for the three non-crib gaps
  C3  do the doubled letters mark group boundaries?  (they fall inside cribs)
  C4  repetition structure: a codebook reuses groups; K4's repeat count vs null
  C5  shared runs between K4 and the other Kryptos ciphertexts
  C6  the length-preservation trap for a MIXED letter+codegroup reading
"""
import math
import os
import random
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matrix_common import CT, CRIBS, N, A2Z, DATA, CRIB_PT

OUT = []
def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUT.append(s)

P("=" * 78)
P("(d) NOMENCLATOR / CODEBOOK")
P("=" * 78)

SPANS = [(21, 25, "EAST"), (25, 34, "NORTHEAST"), (63, 69, "BERLIN"), (69, 74, "CLOCK")]
GAPS = [(0, 21), (34, 63), (74, 97)]

# ---------------------------------------------------------------- C1
P("\nC1. THE CRIBS ARE EXACTLY LENGTH-MATCHED")
for a, b, w in SPANS:
    assert "".join(CRIB_PT[i] for i in range(a, b)) == w
    P("    ct[%2d:%-2d] = %-9s  <->  pt = %-9s   %d ct letters, %d pt letters"
      % (a + 1, b, CT[a:b], w, b - a, len(w)))
P("    4 clues, 4 exact length matches, total 24 ciphertext letters <-> 24")
P("    plaintext letters.  A codebook cannot do that except by coincidence.")
P("")
P("    Cost under explicit code-group models (P that all four words would come")
P("    out length-matched):")
P("      (i)   fixed group length g: needs g = 4 and 9 and 6 and 5 at once -> 0")
P("      (ii)  group length uniform on {2,3,4}  (classic nomenclator):")
P("            NORTHEAST(9), BERLIN(6), CLOCK(5) are unreachable -> 0")
P("      (iii) group length uniform on {2,..,6} (a generous chart):")
P("            NORTHEAST needs 9 -> 0")
P("      (iv)  group length uniform on {2,..,10} (absurdly generous):")
for lo, hi in [(2, 10)]:
    q = 1.0 / (hi - lo + 1)
    tot = 1.0
    for a, b, w in SPANS:
        tot *= q if lo <= (b - a) <= hi else 0.0
    P("            P = (1/%d)^4 = %.2e" % (hi - lo + 1, tot))
P("      (v)   a chart whose group lengths happen to equal the word lengths is")
P("            not a code chart -- it is a letter cipher with extra steps.")
P("    CONCLUSION: at the 24 positions where we can see the mapping, it is")
P("    length-preserving and letter-for-letter.  The cribs are not code groups.")
P("    Note which words these are: EAST, NORTHEAST, BERLIN, CLOCK -- a direction,")
P("    a city and an object, precisely the vocabulary a nomenclator exists to")
P("    encode.  The hybrid 'cipher for text, code groups for names and places'")
P("    is refuted at the only four places it is observable.")

# ---------------------------------------------------------------- C2
P("\nC2. TILING ARITHMETIC FOR THE THREE NON-CRIB GAPS")
P("    If the crib spans are letter-for-letter and the gaps hold fixed-length")
P("    code groups, each gap length must be divisible by the group length.")
P("    gaps: %s  (total %d letters)"
  % (", ".join("[%d,%d) = %d" % (a, b, b - a) for a, b in GAPS),
     sum(b - a for a, b in GAPS)))
P("      g   21   29   23   all three?")
for g in range(2, 12):
    P("     %2d   %-4s %-4s %-4s %s" % (g, 21 % g == 0, 29 % g == 0, 23 % g == 0,
                                        "YES" if all(x % g == 0 for x in (21, 29, 23)) else "no"))
P("    gcd(21,29,23) = %d.  No uniform group length >= 2 tiles all three gaps."
  % math.gcd(math.gcd(21, 29), 23))
P("    (29 and 23 are prime; 21 = 3*7.  g=3 and g=7 fit the first gap only.)")
P("    Variable-length groups can of course tile anything -- but then something")
P("    must mark the boundaries, which is what C3 tests.")

# ---------------------------------------------------------------- C3
P("\nC3. ARE THE DOUBLED LETTERS GROUP MARKERS?")
doubles = [(i, CT[i]) for i in range(N - 1) if CT[i] == CT[i + 1]]
P("    doubled letters at 1-indexed positions: %s"
  % ", ".join("%d %s%s" % (i + 1, c, c) for i, c in doubles))
inside = []
for i, c in doubles:
    for a, b, w in SPANS:
        if a <= i and i + 1 < b:
            inside.append((i + 1, c, w, CRIB_PT[i] + CRIB_PT[i + 1]))
P("    doubles that fall INSIDE a Sanborn crib (so their plaintext is known):")
for pos, c, w, pt in inside:
    P("      %d %s%s lies inside %-9s and stands for the plaintext pair %r"
      % (pos, c, c, w, pt))
P("    %d of the %d doubles are inside cribs and decrypt to ordinary letter pairs."
  % (len(inside), len(doubles)))
P("    A doubled letter is therefore NOT a sentinel, a group marker or a shift")
P("    indicator in K4; it is ordinary cipher output.")
P("    (Count check: %d doubles observed; the random-permutation null in C4 gives"
  % len(doubles))
P("    3.46 on average, P(null >= 6) = 0.13 -- no excess worth explaining.)")

# ---------------------------------------------------------------- C4
P("\nC4. REPETITION STRUCTURE -- a codebook reuses its groups")
def repeats(s, n):
    c = Counter(s[i:i + n] for i in range(len(s) - n + 1))
    return sum(v - 1 for v in c.values() if v > 1), {k: v for k, v in c.items() if v > 1}

rng = random.Random(2026)
letters = list(CT)
TRIALS = 50000
P("    Null: random permutations of K4's own 97 letters (letter multiset fixed).")
P("    %d permutations." % TRIALS)
P("    %-4s %-10s %-12s %-12s %s" % ("n", "observed", "null mean", "null sd", "P(null >= obs)"))
obs_rep = {}
null_stats = {}
sims = []
for _ in range(TRIALS):
    rng.shuffle(letters)
    sims.append("".join(letters))
for n in (2, 3, 4, 5):
    o, which = repeats(CT, n)
    obs_rep[n] = (o, which)
    vals = [repeats(s, n)[0] for s in sims]
    mu = sum(vals) / len(vals)
    sd = math.sqrt(sum((v - mu) ** 2 for v in vals) / len(vals))
    ge = sum(1 for v in vals if v >= o) / len(vals)
    null_stats[n] = (mu, sd, ge)
    P("    %-4d %-10d %-12.3f %-12.3f %.4f" % (n, o, mu, sd, ge))
P("    repeated bigrams in K4: %s"
  % ", ".join("%s x%d" % (k, v) for k, v in sorted(obs_rep[2][1].items())))
P("    repeated trigrams or longer: %s"
  % (", ".join("%s x%d" % (k, v) for k, v in sorted(obs_rep[3][1].items())) or "NONE"))
dvals = [sum(1 for i in range(N - 1) if s[i] == s[i + 1]) for s in sims]
P("    doubled-letter count: observed %d, null mean %.2f sd %.2f, P(null >= obs) = %.3f"
  % (len(doubles), sum(dvals) / len(dvals),
     math.sqrt(sum((v - sum(dvals) / len(dvals)) ** 2 for v in dvals) / len(dvals)),
     sum(1 for v in dvals if v >= len(doubles)) / len(dvals)))
P("    Reading, stated carefully.  The only test that moves at all is the")
P("    bigram one: 10 repeated bigrams against a null mean of 5.7, one-sided")
P("    p = 0.047 -- and that is one of four n-gram tests plus the doubles test,")
P("    so the Sidak-corrected p is 1-(1-0.047)^5 = 0.21.  Nothing survives")
P("    correction.  Decisively, there is not a single repeated TRIGRAM in K4,")
P("    where the null already expects only 0.2, so the data cannot distinguish")
P("    K4 from a random permutation of its own letters in the direction that")
P("    matters.  A 97-letter codebook message would be")
P("    about %d-%d groups; real code traffic repeats its commonest groups"
  % (97 // 5, 97 // 3))
P("    (articles, prepositions, 'STOP', numerals).  K4 shows no such excess.")

# ---------------------------------------------------------------- C5
P("\nC5. SHARED RUNS BETWEEN K4 AND THE OTHER KRYPTOS CIPHERTEXTS")
panel = []
for line in open(os.path.join(DATA, "sculpture_panels.txt")):
    t = line.strip()
    if t and not t.startswith("#") and not t.startswith("["):
        panel.append(t)
alltext = "".join(ch for ch in "".join(panel) if ch.isalpha()).upper()
k123 = alltext[:alltext.rfind(CT)] if CT in alltext else alltext.replace(CT, "")
P("    left panel letters: %d ; K1-K3 portion: %d" % (len(alltext), len(k123)))
SETS = {n: set(k123[i:i + n] for i in range(len(k123) - n + 1)) for n in range(3, 12)}
best = 0
hits = []
for n in range(3, 12):
    found = set()
    s123 = SETS[n]
    for i in range(N - n + 1):
        if CT[i:i + n] in s123:
            found.add((i + 1, CT[i:i + n]))
    if found:
        best = n
        hits = sorted(found)
P("    longest K4 substring also occurring in K1-K3 ciphertext: %d letters" % best)
P("      %s" % ", ".join("pos %d %s" % (p, g) for p, g in hits[:12]))
# null
rngs = random.Random(77)
nl = list(CT)
cnt_ge = 0
NT = 20000
for _ in range(NT):
    rngs.shuffle(nl)
    s = "".join(nl)
    m = 0
    for n in range(3, 12):
        s123 = SETS[n]
        if any(s[i:i + n] in s123 for i in range(N - n + 1)):
            m = n
        else:
            break
    if m >= best:
        cnt_ge += 1
P("    null (random permutations of K4's letters, %d trials): P(longest >= %d) = %.3f"
  % (NT, best, cnt_ge / NT))
P("    No shared run long enough to be a reused code group.")

# ---------------------------------------------------------------- C6
P("\nC6. THE LENGTH TRAP FOR A MIXED LETTER + CODEGROUP READING")
P("    Suppose the 24 crib positions are letter-for-letter (C1 forces that) and")
P("    the 73 gap positions mix plain letters with code groups.  Let the gaps")
P("    hold c code groups whose ciphertext lengths are g_1..g_c and whose")
P("    plaintext expansions are w_1..w_c letters, plus u plain letters:")
P("        sum(g_i) + u = 73          (ciphertext side, known)")
P("        sum(w_i) + u = L - 24      (plaintext side)")
P("    If the plaintext is also 97 letters -- which is the standing assumption")
P("    behind every crib position Sanborn has released, and which his statement")
P("    that K5 is likewise 97 characters reinforces -- then L = 97 and")
P("        sum(g_i) = sum(w_i).")
P("    The code groups must be length-preserving IN AGGREGATE.  A chart whose")
P("    groups are on average as long as the words they replace buys no brevity")
P("    and no extra security; it is a codebook that is not a codebook.")
P("")
P("    Quantitatively, English word length averages ~4.5 letters and nomenclator")
P("    groups run 2-4 characters, so a real chart SHORTENS by ~40 percent.  For 73")
P("    ciphertext letters that is a plaintext of ~%d letters in the gaps, i.e."
  % round(73 * 1.7))
P("    a total plaintext of ~%d rather than 97." % (24 + round(73 * 1.7)))
P("")
P("    If instead L != 97, then ciphertext index and plaintext index diverge and")
P("    'positions 64-69 decrypt to BERLIN' can only be read as a statement about")
P("    ciphertext positions -- which is how this repo already reads it, and which")
P("    leaves the 73 gap letters completely unconstrained.  In that case the")
P("    codebook hypothesis is UNFALSIFIABLE from the cribs: any assignment of")
P("    code groups to the gaps is consistent, and no search can distinguish them.")
P("    That is the honest boundary.  What the cribs DO settle is that the four")
P("    clue words themselves are not code groups (C1) and that nothing in K4's")
P("    surface statistics -- repeats, doubles, shared runs -- shows the")
P("    signature of reused groups (C3-C5).")

P("\nC7. SANBORN'S 'CODED WORDS' REMARK")
P("    Sanborn (2025, Scientific American): K5 is also 97 characters and the two")
P("    messages 'will share some of the same coded words in the same positions'.")
P("    Two readings:")
P("      (1) the same PLAINTEXT words appear at the same positions in K4 and K5")
P("          -- a statement about content, and the reading that fits 97 = 97;")
P("      (2) the same CODE GROUPS appear -- which would be the first real")
P("          evidence for a codebook.")
P("    Reading (2) cannot be tested: the K5 ciphertext is not public.  Reading")
P("    (1) is the only one consistent with both messages being exactly 97")
P("    characters if the system is length-preserving, which C1 shows it is at")
P("    every position we can see.  Note also what (1) implies: if plaintext")
P("    position i carries the same word in both messages and the ciphertexts")
P("    differ, the keystream is POSITIONAL, not autokeyed.")

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "matrix_c_output.txt"), "w") as f:
    f.write("\n".join(OUT) + "\n")
print("\n[written to matrix_c_output.txt]")
