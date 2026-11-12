"""Shared Liber Primus parsing and Gematria Primus utilities."""
import os, re

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
LATIN = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
IDX = {r: i for i, r in enumerate(RUNES)}
assert len(RUNES) == 29 and len(set(RUNES)) == 29

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "data", "liber_primus.md")

def sections():
    """Yield (header, list_of_rune_block_lines) for every '## ' section of LP2."""
    lines = open(SRC, encoding="utf-8").read().split("\n")
    start = next(i for i, l in enumerate(lines) if l.startswith("# LP2"))
    cur, blocks, inrunes = None, [], False
    for l in lines[start + 1:]:
        if l.startswith("## "):
            if cur: yield cur, blocks
            cur, blocks, inrunes = l[3:].strip(), [], False
            continue
        if l.startswith("Runes:"):
            inrunes = True; continue
        if inrunes:
            if l.startswith("    ") or l.strip() == "":
                if l.strip(): blocks.append(l.strip())
            else:
                inrunes = False
    if cur: yield cur, blocks

def tokens(text):
    """Turn a rune text into a list of (kind, value): ('r', idx) or ('sep', char)."""
    out = []
    for ch in text:
        if ch in IDX: out.append(("r", IDX[ch]))
        else: out.append(("sep", ch))
    return out

def lp2_unsolved():
    """Return (stream, wordbreak) for LP2 excluding the two solved final pages.
    wordbreak[i] is True if a non-rune separator sits between rune i-1 and rune i."""
    stream, brk, pending = [], [], False
    for head, blocks in sections():
        if head.startswith("73.jpg") or head.startswith("74.jpg"):
            continue
        for b in blocks:
            for kind, v in tokens(b):
                if kind == "r":
                    stream.append(v); brk.append(pending); pending = False
                else:
                    pending = True
            pending = True  # line end
    return stream, brk

def section_runes(prefix):
    for head, blocks in sections():
        if head.startswith(prefix):
            return blocks
    raise KeyError(prefix)

def to_latin(seq):
    return "".join(LATIN[i] for i in seq)

def ioc(seq, n=29):
    from collections import Counter
    c = Counter(seq); N = len(seq)
    if N < 2: return float("nan")
    return n * sum(v * (v - 1) for v in c.values()) / (N * (N - 1))

# ---------------------------------------------------------------------------
# relikd/LiberPrayground transcription: keeps physical lines and page blocks.
# Fetch: for f in p0-2 p3-7 p8-14 p15-22 p23-26 p27-32 p33-39 p40-53 p54-55; do
#   gh api repos/relikd/LiberPrayground/contents/pages/$f.txt \
#     -H "Accept: application/vnd.github.raw" > cicada/data/relikd/$f.txt; done
RELIKD_DIR = os.path.join(HERE, "..", "data", "relikd")
RELIKD_LP2 = ["p0-2", "p3-7", "p8-14", "p15-22", "p23-26", "p27-32", "p33-39", "p40-53", "p54-55"]
PUNCT = set("⁘⁚⁖⁜")

def relikd_runes(names=RELIKD_LP2, folder=RELIKD_DIR):
    """Parse relikd page files into one record per rune.

    Each record: r (index), sec (file), blk (blank-line-separated block, i.e. a page
    or page part), line (physical line), pl/pb/ps (rune position in line/block/section),
    cps (character position in section, separators included), j (frozenset of what sits
    between this rune and the previous rune of the same section: '•', punctuation,
    'LB' line break, 'PB' block break, 'X' other), first (first rune of section)."""
    recs, gblk, gline = [], 0, 0
    for s, name in enumerate(names):
        text = open(os.path.join(folder, name + ".txt"), encoding="utf-8").read()
        pending, ps, pb, cps, first = set(), 0, 0, 0, True
        for ln in text.split("\n"):
            if ln.strip() == "":
                if pb > 0:
                    gblk += 1; pb = 0
                pending.add("PB"); continue
            if not any(ch in IDX for ch in ln):
                pending.add("X"); continue
            pl = 0
            for ch in ln:
                if ch in IDX:
                    recs.append(dict(r=IDX[ch], sec=s, blk=gblk, line=gline, pl=pl, pb=pb,
                                     ps=ps, cps=cps, j=frozenset(pending), first=first))
                    pending = set(); pl += 1; pb += 1; ps += 1; first = False
                elif ch == "•" or ch in PUNCT or ch in "'\"":
                    pending.add(ch)
                elif not ch.isspace():
                    pending.add("X")
                cps += 1
            gline += 1; pending.add("LB")
        if pb > 0:
            gblk += 1
    return recs
