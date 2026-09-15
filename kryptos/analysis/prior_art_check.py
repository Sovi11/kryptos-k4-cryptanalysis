#!/usr/bin/env python3
"""Mechanical crib-check of publicly claimed K4 plaintexts.

For each claimed plaintext we ask ONE question: applied literally, with no
re-alignment, does the claim place EAST/NORTHEAST/BERLIN/CLOCK at the exact
1-indexed positions Sanborn confirmed (22-25, 26-34, 64-69, 70-74)?
"""
CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
CRIBS = [(22, "EAST"), (26, "NORTHEAST"), (64, "BERLIN"), (70, "CLOCK")]

def check(name, pt, note=""):
    pt = "".join(ch for ch in pt.upper() if ch.isalpha())
    out = [f"--- {name}"]
    out.append(f"    length: {len(pt)} (need 97) {'OK' if len(pt)==97 else 'MISMATCH'}")
    hits = 0
    total = 0
    for pos, word in CRIBS:
        total += len(word)
        seg = pt[pos-1:pos-1+len(word)] if len(pt) >= pos-1+len(word) else "<short>"
        ok = seg == word
        hits += sum(1 for a, b in zip(seg, word) if a == b) if seg != "<short>" else 0
        out.append(f"    {pos:>3}-{pos+len(word)-1:<3} want {word:<9} got {seg:<9} {'OK' if ok else 'FAIL'}")
        # also report where the word actually occurs, if anywhere
        idxs = [i+1 for i in range(len(pt)-len(word)+1) if pt[i:i+len(word)] == word]
        out.append(f"          occurrences of {word}: {idxs if idxs else 'none'}")
    out.append(f"    crib letters matched: {hits}/{total}")
    if note:
        out.append(f"    note: {note}")
    return "\n".join(out), hits, total

CLAIMS = [
    ("solvekryptos.com reconstruction (Quagmire III variant + back-solved helper cards)",
     "THECOMPASSROSEISHEREXEASTNORTHEASTTHISISYOURPOSITIONXCOMMISSIONBERLINCLOCKWHICHISNORTHEASTOFHEREX",
     "site itself states most f/g card values are back-solved from this plaintext"),
    ("ChatGPT claim A (Reddit, via atoponce gist)",
     "BERLINCLOCKINNORTHEASTAREAKEYTOPUZZLE", "LLM output, not 97 letters"),
    ("ChatGPT claim B (Reddit, via atoponce gist)",
     "INTHECENTEROFTHISCITYEASTNORTHEASTNEARROTESRATHAUSCHIMESFROMTHEBERLINCLOCK", "LLM output"),
    ("ChatGPT claim C (Reddit, via atoponce gist)",
     "ABANDONCONTACTNEARTHEBERLINCLOCK", "LLM output"),
]

if __name__ == "__main__":
    print("K4 ciphertext, 1-indexed crib segments actually present in the CIPHERtext:")
    for pos, word in CRIBS:
        print(f"  {pos}: ct={CT[pos-1:pos-1+len(word)]} -> pt={word}")
    print()
    for name, pt, note in CLAIMS:
        s, h, t = check(name, pt, note)
        print(s); print()
