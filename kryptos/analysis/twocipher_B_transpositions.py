"""(B) Substitution BEFORE transposition:  plaintext -> periodic sub -> transposition T -> ct.

T is a permutation of the 97 positions: T[j] = ciphertext position receiving
intermediate position j.  Two readings of the cribs are tested for every T in a
large structured family:

  B1 (fixed-point reading): the 24 crib ciphertext positions are fixed points of T.
     (Then the cribs sit at the same positions in the intermediate text, and the
     periodic test is *identical* to test (A) - so B1 cannot rescue a periodic
     substitution; we only count how many structured T have this property.)

  B2 (contiguity reading): each crib word's letters come from consecutive,
     increasing intermediate positions (the plaintext word is contiguous and T
     moved it as a block to the quoted ciphertext positions).  We also record the
     weaker "contiguous in any order" variant and the stronger "EASTNORTHEAST is a
     13-block and BERLINCLOCK an 11-block" variant.

For every B2 survivor the crib letters are placed at their intermediate positions
and the periodic Vigenere/Beaufort/Quagmire battery (periods 2-26, four alphabet
arrangements) is run.  Because the battery depends only on the 24 intermediate
positions, survivors are de-duplicated by that position tuple.

Transposition families enumerated (each also with its inverse, since a designer
may have used the "decrypt" direction of a scheme as the encryption):
  * route transpositions on every w x h grid, w = 1..97 (h = ceil(97/w)), row-fill
    and column-fill, ~48 routes each: rows/columns in all four orientations,
    boustrophedon (rows and columns), spirals (4 corners x 2 turning senses, inward
    and outward), diagonals and anti-diagonals (plain and zigzag, both directions);
  * keyed columnar transposition: all column permutations for widths 2..9, and
    keyword-derived permutations from /usr/share/dict/words + data-file words for
    widths 10..24;
  * double keyless columnar (K3-style: write w1 wide read by columns, write the
    result w2 wide, read by columns) for w1, w2 in 2..48;
  * modular / skip transpositions  T[j] = (a*j + b) mod M with cells >= 97 skipped,
    M = 97..104, all a coprime to M, all b;
  * sculpture-layout transpositions: the 4 physical rows (OBKR, three 31-letter
    rows) permuted and/or reversed; the 31-wide, 4-row grid with OBKR right- or
    left-aligned in row 0, with all routes; the 3x31 / 31x3 body with all routes and
    OBKR kept in front or behind.
"""
import sys, os, math, itertools, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import twocipher_common as C

N = C.N
CT = C.CT
CRIB_POS = [pos for pos, _, _ in C.CRIBS]

# ------------------------------------------------------------------ helpers
def perm_from_read_order(order):
    """order[k] = intermediate index read k-th to form the ciphertext -> T."""
    assert sorted(order) == list(range(N)), "read order must be a permutation of 0..96"
    T = [None] * N
    for k, j in enumerate(order):
        T[j] = k
    return tuple(T)

def inverse(T):
    Ti = [None] * N
    for j, c in enumerate(T):
        Ti[c] = j
    return tuple(Ti)

def grid_cells(h, w, fill, cell_index=None):
    """Return dict (r,c) -> intermediate index for an h x w grid holding 97 letters.
    fill='row': row-major, last row partial.  fill='col': column-major, last column
    partial.  cell_index may override with an explicit mapping."""
    if cell_index is not None:
        return cell_index
    m = {}
    if fill == "row":
        for j in range(N):
            m[(j // w, j % w)] = j
    else:
        for j in range(N):
            m[(j % h, j // h)] = j
    return m

def routes(h, w):
    """Yield (name, [(r,c), ...]) covering the full h x w rectangle."""
    R, Cc = range(h), range(w)
    # rows / columns in all orientations, and boustrophedon
    for rdir in (1, -1):
        for cdir in (1, -1):
            rows = list(R)[::rdir]; cols = list(Cc)[::cdir]
            yield f"rows r{rdir}c{cdir}", [(r, c) for r in rows for c in cols]
            yield f"cols r{rdir}c{cdir}", [(r, c) for c in cols for r in rows]
            # boustrophedon: alternate the inner direction
            yield f"boust-rows r{rdir}c{cdir}", [(r, c) for i, r in enumerate(rows)
                                                for c in (cols if i % 2 == 0 else cols[::-1])]
            yield f"boust-cols r{rdir}c{cdir}", [(r, c) for i, c in enumerate(cols)
                                                for r in (rows if i % 2 == 0 else rows[::-1])]
    # spirals: canonical top-left clockwise and counter-clockwise inward spirals,
    # reflected to each of the four corners (reflection flips the sense, but both
    # senses are generated, so all 8 corner/sense combinations appear); outward =
    # reversed.
    def spiral_canon(h, w, cw):
        seq = []
        top, bot, left, right = 0, h - 1, 0, w - 1
        while top <= bot and left <= right:
            if cw:
                for c in range(left, right + 1): seq.append((top, c))
                for r in range(top + 1, bot + 1): seq.append((r, right))
                if top < bot:
                    for c in range(right - 1, left - 1, -1): seq.append((bot, c))
                if left < right:
                    for r in range(bot - 1, top, -1): seq.append((r, left))
            else:
                for r in range(top, bot + 1): seq.append((r, left))
                for c in range(left + 1, right + 1): seq.append((bot, c))
                if left < right:
                    for r in range(bot - 1, top - 1, -1): seq.append((r, right))
                if top < bot:
                    for c in range(right - 1, left, -1): seq.append((top, c))
            top += 1; bot -= 1; left += 1; right -= 1
        return seq
    for start in ("tl", "tr", "bl", "br"):
        for cw in (True, False):
            base = spiral_canon(h, w, cw)
            def tf(rc):
                r, c = rc
                if start == "tr": c = w - 1 - c
                elif start == "bl": r = h - 1 - r
                elif start == "br": r, c = h - 1 - r, w - 1 - c
                return (r, c)
            s = [tf(rc) for rc in base]
            yield f"spiral-in {start} {'cw' if cw else 'ccw'}", s
            yield f"spiral-out {start} {'cw' if cw else 'ccw'}", s[::-1]
    # diagonals: anti-diagonals (r+c=k) and main diagonals (r-c=k)
    for kind in ("anti", "main"):
        if kind == "anti":
            groups = [[(r, k - r) for r in range(h) if 0 <= k - r < w] for k in range(h + w - 1)]
        else:
            groups = [[(r, r - k) for r in range(h) if 0 <= r - k < w] for k in range(-(w - 1), h)]
        for inner in ("asc", "desc", "zig-a", "zig-d"):
            seq = []
            for i, g in enumerate(groups):
                if inner == "asc": seq += g
                elif inner == "desc": seq += g[::-1]
                elif inner == "zig-a": seq += g if i % 2 == 0 else g[::-1]
                else: seq += g[::-1] if i % 2 == 0 else g
            yield f"diag-{kind} {inner}", seq
            yield f"diag-{kind} {inner} rev", seq[::-1]

def perm_from_route(cells, route):
    order = [cells[rc] for rc in route if rc in cells]
    if len(order) != N:
        return None
    return perm_from_read_order(order)

def keyword_perm(word):
    """Standard columnar key: rank letters alphabetically, ties left-to-right.
    Returns column read order (list of column indices)."""
    idx = sorted(range(len(word)), key=lambda i: (word[i], i))
    return idx

def columnar(w, col_order, fill="row"):
    h = math.ceil(N / w)
    cells = grid_cells(h, w, fill)
    order = []
    for c in col_order:
        for r in range(h):
            if (r, c) in cells:
                order.append(cells[(r, c)])
    return perm_from_read_order(order)

def compose(T1, T2):
    """Apply T1 then T2: j -> T2[T1[j]]."""
    return tuple(T2[T1[j]] for j in range(N))

# ------------------------------------------------------------------ crib tests
def crib_intermediate_positions(T):
    Ti = inverse(T)
    return [Ti[c] for c in CRIB_POS]

def classify(T):
    """Return dict of boolean properties for T."""
    Ti = inverse(T)
    fixed = all(Ti[c] == c for c in CRIB_POS)
    per_word_inc = True; per_word_any = True
    for p, ctw, ptw, _ in C.CRIB_WORDS:
        src = [Ti[p + k] for k in range(len(ctw))]
        if src != list(range(src[0], src[0] + len(src))):
            per_word_inc = False
        if sorted(src) != list(range(min(src), min(src) + len(src))):
            per_word_any = False
    # strong: 13-block and 11-block, increasing
    src1 = [Ti[c] for c in range(21, 34)]; src2 = [Ti[c] for c in range(63, 74)]
    strong = (src1 == list(range(src1[0], src1[0] + 13)) and src2 == list(range(src2[0], src2[0] + 11)))
    return {"fixed": fixed, "contig_inc": per_word_inc, "contig_any": per_word_any, "strong": strong}

# ------------------------------------------------------------------ enumeration
def enumerate_family():
    """Yield (family, description, T)."""
    # 1. route transpositions on every grid
    for w in range(1, N + 1):
        h = math.ceil(N / w)
        for fill in ("row", "col"):
            cells = grid_cells(h, w, fill)
            for name, route in routes(h, w):
                T = perm_from_route(cells, route)
                if T is not None:
                    yield "route", f"grid {h}x{w} fill={fill} route={name}", T
    # 2. keyed columnar, widths 2..9 all permutations
    for w in range(2, 10):
        for perm in itertools.permutations(range(w)):
            yield "columnar-allperm", f"w={w} order={perm}", columnar(w, perm)
    # 2b. keyword columnar, widths 10..24 from dictionary
    words = C.load_words(minlen=10, maxlen=24)
    seen = set()
    for word in sorted(words):
        w = len(word)
        perm = tuple(keyword_perm(word))
        if (w, perm) in seen:
            continue
        seen.add((w, perm))
        yield "columnar-keyword", f"w={w} keyword={word} order={perm}", columnar(w, perm)
    # 3. double keyless columnar
    for w1 in range(2, 49):
        T1 = columnar(w1, list(range(w1)))
        for w2 in range(2, 49):
            T2 = columnar(w2, list(range(w2)))
            yield "double-columnar", f"w1={w1} w2={w2}", compose(T1, T2)
    # 4. modular / skip
    for M in range(97, 105):
        for a in range(1, M):
            if math.gcd(a, M) != 1:
                continue
            for b in range(M):
                order = [(a * k + b) % M for k in range(M)]
                order = [x for x in order if x < N]
                yield "modular", f"M={M} a={a} b={b}", perm_from_read_order(order)
    # 5. sculpture layout
    blocks = [list(range(0, 4)), list(range(4, 35)), list(range(35, 66)), list(range(66, 97))]
    for perm in itertools.permutations(range(4)):
        for revmask in range(16):
            order = []
            for i, bi in enumerate(perm):
                b = blocks[bi]
                order += b[::-1] if (revmask >> i) & 1 else b
            yield "sculpture-blocks", f"block order={perm} reversed={revmask:04b}", perm_from_read_order(order)
    # 31-wide 4-row grid with OBKR right-aligned (physical) or left-aligned
    for align in ("right", "left"):
        cells = {}
        for k in range(4):
            cells[(0, 27 + k if align == "right" else k)] = k
        for j in range(4, N):
            r = 1 + (j - 4) // 31; c = (j - 4) % 31
            cells[(r, c)] = j
        for name, route in routes(4, 31):
            T = perm_from_route(cells, route)
            if T is not None:
                yield "sculpture-grid", f"4x31 OBKR {align}-aligned route={name}", T
    # 3x31 body with all routes, OBKR in front or behind (and reversed or not)
    for hh, ww in ((3, 31), (31, 3)):
        for fill in ("row", "col"):
            cells = {}
            for j in range(93):
                if fill == "row": cells[(j // ww, j % ww)] = j + 4
                else: cells[(j % hh, j // hh)] = j + 4
            for name, route in routes(hh, ww):
                body = [cells[rc] for rc in route if rc in cells]
                if len(body) != 93: continue
                for head in ("front", "back"):
                    for hrev in (False, True):
                        ob = [3, 2, 1, 0] if hrev else [0, 1, 2, 3]
                        order = ob + body if head == "front" else body + ob
                        yield "sculpture-body", f"{hh}x{ww} fill={fill} route={name} OBKR={head}{' rev' if hrev else ''}", perm_from_read_order(order)

def main():
    t0 = time.time()
    seen_T = set()
    counts = {"total": 0, "unique": 0, "fixed": 0, "contig_inc": 0, "contig_any": 0, "strong": 0, "identity": 0}
    fam_counts = {}
    by_positions = {}   # tuple of intermediate crib positions -> list of descriptions (contig_inc)
    by_positions_any = {}
    fixed_examples = []
    for fam, desc, T in enumerate_family():
        for variant, TT in (("", T), (" [inverse]", inverse(T))):
            counts["total"] += 1
            fam_counts.setdefault(fam, [0, 0, 0])[0] += 1
            if TT in seen_T:
                continue
            seen_T.add(TT)
            counts["unique"] += 1
            if all(TT[j] == j for j in range(N)):
                counts["identity"] += 1
            cl = classify(TT)
            for k in ("fixed", "contig_inc", "contig_any", "strong"):
                counts[k] += cl[k]
            if cl["fixed"]:
                fam_counts[fam][1] += 1
                if len(fixed_examples) < 40:
                    fixed_examples.append(fam + ": " + desc + variant)
            if cl["contig_inc"]:
                fam_counts[fam][2] += 1
                key = tuple(crib_intermediate_positions(TT))
                by_positions.setdefault(key, []).append(fam + ": " + desc + variant)
            elif cl["contig_any"]:
                key = tuple(crib_intermediate_positions(TT))
                by_positions_any.setdefault(key, []).append(fam + ": " + desc + variant)
    print(f"Enumerated {counts['total']} (family,variant) transpositions, {counts['unique']} distinct permutations "
          f"in {time.time() - t0:.1f}s; identity present: {counts['identity']}")
    print(f"  B1  all 24 crib positions fixed:          {counts['fixed']}")
    print(f"  B2  each crib word contiguous+increasing: {counts['contig_inc']}   (distinct crib-position tuples: {len(by_positions)})")
    print(f"      each crib word contiguous, any order:  {counts['contig_any']}   (extra tuples: {len(by_positions_any)})")
    print(f"      strong (13-block and 11-block):        {counts['strong']}")
    print("\nPer family: [enumerated (x2 with inverses), B1 fixed, B2 contig_inc]")
    for fam, v in fam_counts.items():
        print(f"  {fam:18s} {v}")
    print("\nB1 examples (up to 40):")
    for e in fixed_examples:
        print("   ", e)

    # ---- periodic battery on B2 survivors (distinct crib-position tuples)
    results = []
    def run_on(key, descs, label):
        pairs = [(key[i], C.CRIBS[i][1], C.CRIBS[i][2]) for i in range(24)]
        surv = C.run_periodic_battery(pairs, periods=range(2, 27))
        nonvac = [s for s in surv if s[4] > 0]
        # is this tuple just a uniform shift of the original (then equivalent to test A)?
        diffs = {key[i] - CRIB_POS[i] for i in range(24)}
        results.append((label, key, descs, surv, nonvac, len(diffs) == 1))
    for key, descs in by_positions.items():
        run_on(key, descs, "contig_inc")
    for key, descs in by_positions_any.items():
        run_on(key, descs, "contig_any")

    print("\n=== Periodic battery on B2 survivors ===")
    n_shift = sum(1 for r in results if r[5])
    print(f"{len(results)} distinct crib-position tuples tested ({n_shift} are pure uniform shifts of the original "
          f"positions and therefore equivalent to test A).")
    any_hit = False
    for label, key, descs, surv, nonvac, is_shift in results:
        if surv:
            any_hit = True
            print(f"\n[{label}] crib intermediate positions: {key}")
            print(f"   uniform shift of original: {is_shift};  transpositions giving this tuple: {len(descs)}")
            for d in descs[:6]:
                print("     ", d)
            print(f"   consistent periodic configs: {len(surv)} (non-vacuous: {len(nonvac)})")
            for period, fam, aname, keyd, checks in surv:
                print(f"     p={period} {fam} {aname} checks={checks} key={dict(sorted(keyd.items()))}")
    if not any_hit:
        print("No B2 survivor admits any periodic substitution (periods 2-26, vig/beaufort, 4 alphabet sets).")

    # ---- decryptions for non-vacuous hits
    print("\n=== Implied decryptions for non-vacuous hits ===")
    hits = 0
    for label, key, descs, surv, nonvac, is_shift in results:
        for period, fam, aname, keyd, checks in nonvac:
            hits += 1
            # find a T with this key to build the intermediate text
            # (all T with the same tuple give the same crib placement but different other letters;
            #  show the first few)
            PA, CA = C.ALPHABET_SETS[aname]
            print(f"\n[{label}] p={period} {fam} {aname} checks={checks} (key columns known: {len(keyd)}/{period})")
            for d in descs[:3]:
                T = find_T(d)
                inter = "".join(CT[T[j]] for j in range(N))
                dec = C.decrypt_periodic(inter, keyd, period, fam, PA, CA)
                q, w, verdict = C.english_judgement(dec.replace(".", ""))
                print(f"   T: {d}")
                print(f"   intermediate: {inter}")
                print(f"   decryption  : {dec}")
                print(f"   english     : quad={q:.2f} wordcov={w:.2f} -> {verdict}")
    if hits == 0:
        print("(none)")

    with open(os.path.join(C.HERE, "twocipher_B_results.json"), "w") as f:
        json.dump({"counts": counts, "fam_counts": fam_counts,
                   "survivor_tuples": [{"label": r[0], "positions": list(r[1]), "n_T": len(r[2]),
                                        "examples": r[2][:5], "periodic_survivors": [list(map(str, s[:3])) + [s[4]] for s in r[3]],
                                        "uniform_shift": r[5]} for r in results]}, f, indent=1)

_T_CACHE = {}
def find_T(desc):
    if not _T_CACHE:
        for fam, d, T in enumerate_family():
            _T_CACHE[fam + ": " + d] = T
            _T_CACHE[fam + ": " + d + " [inverse]"] = inverse(T)
    return _T_CACHE[desc]

if __name__ == "__main__":
    main()
