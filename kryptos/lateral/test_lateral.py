import os, glob, itertools, collections, json

CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
CRIBS = {22:"EAST", 26:"NORTHEAST", 64:"BERLIN", 70:"CLOCK"}
PAIRS=[]
for p,w in CRIBS.items():
    for i,ch in enumerate(w): PAIRS.append((p-1+i, CT[p-1+i], ch))
A="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def keyed(kw):
    s=""
    for c in kw+A:
        if c not in s: s+=c
    return s
K=keyed("KRYPTOS")
ALPHAS={"plain":A,"kryptos":K}
IDX={n:{c:i for i,c in enumerate(al)} for n,al in ALPHAS.items()}

# required key INDEX at each crib position, per (family, pt_alpha, ct_alpha)
def req_indices(fam, pa, ca):
    out={}
    for pos,c,p in PAIRS:
        ip=IDX[pa][p]; ic=IDX[ca][c]
        if   fam=="vig":     v=(ic-ip)%26
        elif fam=="beau":    v=(ic+ip)%26
        else:                v=(ip-ic)%26   # varbeau
        out[pos]=v
    return out

COMBOS=[(f,pa,ca,ka) for f in ("vig","beau","varbeau")
        for pa in ("plain","kryptos") for ca in ("plain","kryptos") for ka in ("plain","kryptos")]

# crib blocks: 0-indexed 21..33 (13) and 63..73 (11); start gap = 42
B1=list(range(21,34)); B2=list(range(63,74))

def blocks_for(fam,pa,ca,ka):
    ri=req_indices(fam,pa,ca); al=ALPHAS[ka]
    return ("".join(al[ri[i]] for i in B1), "".join(al[ri[i]] for i in B2))

def ham(a,b): return sum(1 for x,y in zip(a,b) if x!=y)

files=sorted(glob.glob("lateral/keystreams/*.txt"))
streams={}
for f in files:
    t="".join(ch for ch in open(f,encoding="utf-8",errors="ignore").read().upper() if ch.isalpha())
    if len(t)>=11: streams[os.path.basename(f)]=t
print(f"keystream files with >=11 letters: {len(streams)} (of {len(files)})")
print(f"total letters in corpus: {sum(len(v) for v in streams.values())}")

best_b1=(99,None); best_b2=(99,None); best_joint=(99,None)
hits=[]
tests_b1=tests_b2=tests_j=0
for fam,pa,ca,ka in COMBOS:
    b1,b2=blocks_for(fam,pa,ca,ka)
    combo=f"{fam}/pt={pa}/ct={ca}/key={ka}"
    for r in range(26):   # key-alphabet rotation
        al=ALPHAS[ka]
        rot=lambda s: "".join(al[(al.index(ch)+r)%26] for ch in s)
        r1,r2=rot(b1),rot(b2)
        for name,t in streams.items():
            n=len(t)
            for o in range(n-12):
                tests_b1+=1
                d=ham(r1,t[o:o+13])
                if d<best_b1[0]: best_b1=(d,(combo,r,name,o,t[o:o+13]))
                if d<=2: hits.append(("B1",d,combo,r,name,o,t[o:o+13],r1))
                if o+42+11<=n:
                    tests_j+=1
                    dj=d+ham(r2,t[o+42:o+53])
                    if dj<best_joint[0]: best_joint=(dj,(combo,r,name,o))
                    if dj<=4: hits.append(("JOINT",dj,combo,r,name,o,t[o:o+13]+"|"+t[o+42:o+53],r1+"|"+r2))
            for o in range(n-10):
                tests_b2+=1
                d=ham(r2,t[o:o+11])
                if d<best_b2[0]: best_b2=(d,(combo,r,name,o,t[o:o+11]))
                if d<=2: hits.append(("B2",d,combo,r,name,o,t[o:o+11],r2))

print(f"\ntests: block1={tests_b1:,}  block2={tests_b2:,}  joint={tests_j:,}")
print(f"best block1 Hamming: {best_b1[0]}/13  {best_b1[1]}")
print(f"best block2 Hamming: {best_b2[0]}/11  {best_b2[1]}")
print(f"best joint  Hamming: {best_joint[0]}/24  {best_joint[1]}")
print(f"\nhits within threshold (B1<=2, B2<=2, JOINT<=4): {len(hits)}")
for h in hits[:20]: print("  ",h)

# periodic use of each stream: first N letters repeated
print("\n=== each stream as a PERIODIC key (prefix of length N repeated) ===")
bestp=(0,None); tp=0
for fam,pa,ca,ka in COMBOS:
    ri=req_indices(fam,pa,ca); al=ALPHAS[ka]
    need={i:al[ri[i]] for i in ri}
    for name,t in streams.items():
        for N in range(2,min(97,len(t))+1):
            tp+=1
            m=sum(1 for i,ch in need.items() if t[i%N]==ch)
            if m>bestp[0]: bestp=(m,(f"{fam}/{pa}/{ca}/{ka}",name,N))
print(f"tests: {tp:,}   best crib match: {bestp[0]}/24  {bestp[1]}   (chance ~0.92/24)")
