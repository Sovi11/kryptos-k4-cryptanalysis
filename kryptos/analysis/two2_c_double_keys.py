"""(c) Substitution + substitution, keyed by the OTHER Kryptos sections.

Model   P --stage1(key A)--> M --stage2(key B)--> C,  both stages letter-wise and
position-indexed, so the cribs pin 24 (P, C) pairs directly.

A stage is (key word, phase, family, pt-alphabet, ct-alphabet, key-alphabet):
  vigenere  c = CA[(PA.idx(p) + KA.idx(k)) % 26]
  beaufort  c = CA[(KA.idx(k) - PA.idx(p)) % 26]
  varbeauf. c = CA[(PA.idx(p) - KA.idx(k)) % 26]
with the key letter k = key[(i + phase) % len(key)] at position i, alphabets
either plain A-Z or the KRYPTOS-keyed alphabet (24 combos per stage, exactly the
set used throughout this repo).  "Phase" covers a key that does not start at
position 0, which also covers every rotation of the keyword.

The search is made exact and exhaustive by a meet-in-the-middle:

  forward set   F = { enc_stage1(EASTNORTHEAST/BERLINCLOCK at their positions) }
  backward set  B = { dec_stage2(FLRVQQPRNGKSS/NYPVTTMZFPK at their positions) }

a configuration solves the cribs iff the two 24-letter intermediate strings are
equal, i.e. iff F and B intersect.  So the whole cross product of stage-1 and
stage-2 configurations is decided by one set intersection, and stage lists of
millions of configurations are affordable.

Three scopes are run:
  C1  the task's core question: both keys drawn from {PALIMPSEST, ABSCISSA,
      KRYPTOS}, every ordering, every phase, all 24x24 alphabet/family combos;
  C2  both keys drawn from a 40-word Kryptos-motivated list;
  C3  one key from the core three, the other ANY word of length 2-24 in
      /usr/share/dict/words plus every word appearing in data/* (both orders).

Chance: a configuration passes only if 24 letters agree, probability 26^-24 =
1.2e-34 per pair of stage configurations, so even 10^13 pairs expect 0.
"""
import os, sys, time, json, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import runningkey_lib as RK
import twocipher_common as TC

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "two2_c_output.txt")
RES = os.path.join(HERE, "two2_c_results.json")
_fh = open(OUT, "w")
def say(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True); _fh.write(s + "\n"); _fh.flush()

CT = TC.CT
CRIB_POS = list(range(21, 34)) + list(range(63, 74))
CRIB_PT = "EASTNORTHEAST" + "BERLINCLOCK"
CRIB_CT = "".join(CT[p] for p in CRIB_POS)
COMBOS = list(RK.combos())

CORE_KEYS = ["PALIMPSEST", "ABSCISSA", "KRYPTOS"]
LIST_KEYS = CORE_KEYS + [
    "SANBORN", "SCHEIDT", "LANGLEY", "CIA", "WW", "MASKING", "COMPASS", "LODESTONE",
    "IQLUSION", "UNDERGRUUND", "DESPARATLY", "LAYERTWO", "IDBYROWS", "BERLIN",
    "CLOCK", "BERLINCLOCK", "EAST", "NORTHEAST", "EASTNORTHEAST", "SHADOWFORCES",
    "LUCIDMEMORY", "VIRTUALLYINVISIBLE", "DIGETALINTERPRETATU", "TISYOURPOSITION",
    "SOS", "RQ", "KRYPTOSABCDEFGHIJLMNQUVWXZ", "PALIMPSESTABSCISSA",
    "ABSCISSAPALIMPSEST", "TSESPMILAP", "ASSICSBA", "SOTPYRK", "XLAYERTWO",
    "NORTHEASTBERLINCLOCK", "PALIMPSESTKRYPTOS", "KRYPTOSPALIMPSEST",
    "ABSCISSAKRYPTOS", "KRYPTOSABSCISSA", "YAR", "TENTATIVE",
]

def enc(fam, PA, CA, KA, p, k):
    a = PA.index(p); b = KA.index(k)
    if fam == "vigenere":    return CA[(a + b) % 26]
    if fam == "beaufort":    return CA[(b - a) % 26]
    return CA[(a - b) % 26]

def dec(fam, PA, CA, KA, c, k):
    b = KA.index(k); x = CA.index(c)
    if fam == "vigenere":    return PA[(x - b) % 26]
    if fam == "beaufort":    return PA[(b - x) % 26]
    return PA[(x + b) % 26]

def verify_engine():
    """The stage engine must reproduce K1 from its plaintext with PALIMPSEST and
    K2 from its plaintext with ABSCISSA (Vigenere, all three alphabets KRYPTOS)."""
    K = RK.KEYED
    k1 = "".join(enc("vigenere", K, K, K, p, "PALIMPSEST"[i % 10])
                 for i, p in enumerate(RK.K1_PT))
    k2 = "".join(enc("vigenere", K, K, K, p, "ABSCISSA"[i % 8])
                 for i, p in enumerate(RK.K2_PT))
    ok1 = k1 == RK.K1_CT
    ok2 = k2[:361] == RK.K2_CT[:361]
    # decrypt must invert encrypt for every combo
    ok3 = all(dec(f, RK.ALPHAS[a], RK.ALPHAS[b], RK.ALPHAS[c],
                  enc(f, RK.ALPHAS[a], RK.ALPHAS[b], RK.ALPHAS[c], "Q", "W"), "W") == "Q"
              for f in RK.FAMILIES for a in ("plain", "keyed")
              for b in ("plain", "keyed") for c in ("plain", "keyed"))
    say(f"engine verification: K1 re-encrypted={ok1}  K2 prefix re-encrypted={ok2}  "
        f"enc/dec inverse for all 24 combos={ok3}")
    assert ok1 and ok2 and ok3

def stage_strings(keys, direction):
    """Yield (label, 24-letter intermediate string).
    direction='fwd' : stage 1 applied to the known plaintext  -> required M
    direction='bwd' : stage 2 undone from the known ciphertext -> produced M
    """
    for w in keys:
        Lw = len(w)
        for ph in range(Lw):
            for fam, ap, ac, ak in COMBOS:
                PA, CA, KA = RK.ALPHAS[ap], RK.ALPHAS[ac], RK.ALPHAS[ak]
                if direction == "fwd":
                    s = "".join(enc(fam, PA, CA, KA, CRIB_PT[i], w[(pos + ph) % Lw])
                                for i, pos in enumerate(CRIB_POS))
                else:
                    s = "".join(dec(fam, PA, CA, KA, CRIB_CT[i], w[(pos + ph) % Lw])
                                for i, pos in enumerate(CRIB_POS))
                yield (w, ph, fam, ap, ac, ak), s

def run(name, keys1, keys2, results):
    t0 = time.time()
    fwd = {}
    n1 = 0
    for lab, s in stage_strings(keys1, "fwd"):
        n1 += 1
        fwd.setdefault(s, []).append(lab)
    hits = []
    n2 = 0
    for lab, s in stage_strings(keys2, "bwd"):
        n2 += 1
        if s in fwd:
            for l1 in fwd[s]:
                hits.append((l1, lab, s))
    pairs = n1 * n2
    say(f"{name}: stage-1 configs {n1:,}, stage-2 configs {n2:,}, "
        f"pairs decided {pairs:,}, chance-expected solutions {pairs*26.0**-24:.3g}, "
        f"observed {len(hits)}   ({time.time()-t0:.1f}s)")
    for h in hits[:20]:
        say("   SOLUTION", h)
    results[name] = {"stage1_configs": n1, "stage2_configs": n2, "pairs": pairs,
                     "chance": pairs * 26.0 ** -24, "hits": [str(h) for h in hits[:50]]}
    return hits

def main():
    t0 = time.time()
    say("=== (c) double substitution keyed by the Kryptos sections ===")
    verify_engine()
    say(f"cribs: plaintext {CRIB_PT}  ciphertext {CRIB_CT}  at 0-indexed {CRIB_POS}")
    say(f"{len(COMBOS)} alphabet/family combos per stage: {RK.combo_name(COMBOS[0])} ...")
    results = {}

    # --- C1: the core question, exhaustive
    say("\n-- C1: both keys in {PALIMPSEST, ABSCISSA, KRYPTOS}, every ordering, "
        "every phase, all 24x24 combos")
    run("C1_core", CORE_KEYS, CORE_KEYS, results)
    # spell out the specific configuration the hypothesis names
    say("   the named case (stage 1 PALIMPSEST, stage 2 ABSCISSA, both Vigenere on "
        "the KRYPTOS alphabet, phase 0):")
    K = RK.KEYED
    mid = "".join(enc("vigenere", K, K, K, CRIB_PT[i], "PALIMPSEST"[pos % 10])
                  for i, pos in enumerate(CRIB_POS))
    mid2 = "".join(dec("vigenere", K, K, K, CRIB_CT[i], "ABSCISSA"[pos % 8])
                   for i, pos in enumerate(CRIB_POS))
    say(f"     stage-1 output required : {mid}")
    say(f"     stage-2 input produced  : {mid2}")
    say(f"     agree in {sum(a==b for a,b in zip(mid,mid2))}/24 positions "
        f"(chance 0.92)")
    # full decryption under that configuration, for the record
    full = "".join(dec("vigenere", K, K, K,
                       dec("vigenere", K, K, K, c, "ABSCISSA"[i % 8]),
                       "PALIMPSEST"[i % 10]) for i, c in enumerate(CT))
    q, wv, v = TC.english_judgement(full)
    say(f"     full decryption: {full}")
    say(f"     quad={q:.2f} wordcov={wv:.2f} -> {v}")
    results["named_case"] = {"mid_required": mid, "mid_produced": mid2, "decrypt": full,
                             "quad": q, "wordcov": wv}

    # --- C2: 40-word Kryptos list both sides
    say("\n-- C2: both keys from the Kryptos-motivated word list "
        f"({len(LIST_KEYS)} words)")
    run("C2_list", LIST_KEYS, LIST_KEYS, results)

    # --- C3: one stage keyed by a known key, the other by ANY word of length
    #         <= 24 at any phase.  Instead of enumerating words we invert: the
    #         known stage fixes the intermediate text M at the 24 crib positions,
    #         which forces the *other* stage's key letter at each crib position.
    #         A key word of length Lw exists iff those 24 forced letters are
    #         consistent on residue classes mod Lw; the phase only relabels the
    #         residues, so it need not be enumerated.  This covers every word,
    #         dictionary or not, of every length 1..24, at every phase.
    say("\n-- C3: one stage keyed by a known Kryptos key, the other by ANY key word "
        "of length 1..24 at any phase (solved by forcing the key letters, so no "
        "word list is needed)")

    def forced_key_letters(mid, side, fam, PA, CA, KA):
        """Key letters the other stage must use at the 24 crib positions."""
        out = []
        for i, pos in enumerate(CRIB_POS):
            if side == "stage2":      # stage 2 maps mid -> ct
                a = PA.index(mid[i]); x = CA.index(CRIB_CT[i])
                if fam == "vigenere":   b = (x - a) % 26
                elif fam == "beaufort": b = (x + a) % 26
                else:                   b = (a - x) % 26
            else:                     # stage 1 maps pt -> mid
                a = PA.index(CRIB_PT[i]); x = CA.index(mid[i])
                if fam == "vigenere":   b = (x - a) % 26
                elif fam == "beaufort": b = (x + a) % 26
                else:                   b = (a - x) % 26
            out.append(KA[b])
        return "".join(out)

    # number of non-trivial checks a period Lw imposes: it depends only on the
    # crib positions, not on the letters, so compute it once.
    NCHECK = {Lw: 24 - len({p % Lw for p in CRIB_POS}) for Lw in range(1, 27)}
    say("   non-trivial checks per candidate key length: "
        + " ".join(f"{Lw}:{NCHECK[Lw]}" for Lw in range(1, 27)))

    def periodic_ok(letters, Lw):
        """(consistent, key dict residue->letter) for period Lw."""
        key = {}
        for i, pos in enumerate(CRIB_POS):
            r = pos % Lw
            if r in key:
                if key[r] != letters[i]:
                    return False, key
            else:
                key[r] = letters[i]
        return True, key

    dictwords = TC.load_words(minlen=1, maxlen=24)
    for known_side, keylist, klabel in (("stage1", LIST_KEYS, "stage 1 known, stage 2 free"),
                                        ("stage2", LIST_KEYS, "stage 2 known, stage 1 free")):
        ntest = 0; nconsistent = 0; chance = 0.0; found = []
        for lab, mid in stage_strings(keylist, "fwd" if known_side == "stage1" else "bwd"):
            for fam, ap, ac, ak in COMBOS:
                PA, CA, KA = RK.ALPHAS[ap], RK.ALPHAS[ac], RK.ALPHAS[ak]
                other = "stage2" if known_side == "stage1" else "stage1"
                letters = forced_key_letters(mid, other, fam, PA, CA, KA)
                for Lw in range(1, 27):
                    ntest += 1
                    checks = NCHECK[Lw]
                    chance += 26.0 ** -checks
                    ok, key = periodic_ok(letters, Lw)
                    if ok:
                        nconsistent += 1
                        kw = "".join(key.get(r, ".") for r in range(Lw))
                        rots = {kw[i:] + kw[:i] for i in range(Lw)}
                        isword = any(r in dictwords for r in rots)
                        found.append((lab, (fam, ap, ac, ak), Lw, checks, kw, isword))
        say(f"   {klabel}: {ntest:,} (known-config, free-combo, period) tests, "
            f"{nconsistent} consistent, chance-expected {chance:.3g}")
        nz = [f for f in found if f[3] > 0]
        say(f"     consistent with >=1 non-trivial check: {len(nz)}; "
            f"of those, implied key word (any rotation) in the dictionary: "
            f"{sum(1 for f in nz if f[5])}")
        for f in sorted(nz, key=lambda x: -x[3])[:10]:
            say(f"       {f[0]} x {f[1]} period={f[2]} checks={f[3]} key={f[4]} "
                f"dictword={f[5]}")
        results["C3_" + known_side] = {"tests": ntest, "consistent": nconsistent,
                                       "chance": chance,
                                       "nonvacuous": [str(f) for f in nz[:100]]}

    # --- C4: same-key-twice and three-stage sanity note
    say("\n-- C4: does any *single* stage of this engine already fit the cribs? "
        "(sanity: it must not, since periodic substitution is ruled out)")
    n = 0; hit = 0
    for lab, s in stage_strings(LIST_KEYS, "bwd"):
        n += 1
        if s == CRIB_PT:
            hit += 1; say("   SINGLE-STAGE SOLUTION", lab)
    say(f"   {n:,} single-stage configurations tested, {hit} fit all 24 cribs")
    results["C4_single_stage"] = {"tested": n, "hits": hit}

    with open(RES, "w") as f:
        json.dump(results, f, indent=1)
    say(f"\nruntime {time.time()-t0:.1f}s")

if __name__ == "__main__":
    main()
