import glob, os
CT="OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
CRIBS={22:"EAST",26:"NORTHEAST",64:"BERLIN",70:"CLOCK"}
PAIRS=[]
for p,w in CRIBS.items():
    for i,ch in enumerate(w): PAIRS.append((p-1+i,CT[p-1+i],ch))
A="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def keyed(kw):
    s=""
    for c in kw+A:
        if c not in s: s+=c
    return s
K=keyed("KRYPTOS"); ALPH={"plain":A,"kryptos":K}
IDX={n:{c:i for i,c in enumerate(al)} for n,al in ALPH.items()}
def req(fam,pa,ca):
    o={}
    for pos,c,p in PAIRS:
        ip=IDX[pa][p]; ic=IDX[ca][c]
        o[pos]=(ic-ip)%26 if fam=="vig" else (ic+ip)%26 if fam=="beau" else (ip-ic)%26
    return o
COMBOS=[(f,pa,ca) for f in("vig","beau","varbeau") for pa in("plain","kryptos") for ca in("plain","kryptos")]

files=sorted(glob.glob("lateral/keystreams/*.txt"))
num={}
for f in files:
    raw=open(f,encoding="utf-8",errors="ignore").read()
    d=[int(c) for c in raw if c.isdigit()]
    if len(d)>=24: num[os.path.basename(f)]=d
print(f"numeric streams with >=24 digits: {len(num)}")
print(f"total digits: {sum(len(v) for v in num.values())}")

# (a) digits used directly as shifts (Gronsfeld), sliding offset over the stream
best=(0,None); tests=0
for fam,pa,ca in COMBOS:
    r=req(fam,pa,ca)
    for name,d in num.items():
        n=len(d)
        for off in range(n):
            tests+=1
            m=sum(1 for pos,v in r.items() if d[(off+pos)%n]==v%10 and v<10)
            if m>best[0]: best=(m,(f"{fam}/{pa}/{ca}",name,off))
print(f"\n(a) Gronsfeld sliding: tests={tests:,}  best={best[0]}/24  {best[1]}")
# note: only crib shifts <10 are even representable
for fam,pa,ca in COMBOS[:4]:
    r=req(fam,pa,ca); big=sum(1 for v in r.values() if v>9)
    print(f"    {fam}/{pa}/{ca}: {big}/24 required shifts exceed 9 -> Gronsfeld impossible")

# (b) digit PAIRS as mod-26 shifts
best2=(0,None); t2=0
for fam,pa,ca in COMBOS:
    r=req(fam,pa,ca)
    for name,d in num.items():
        n=len(d)
        if n<50: continue
        for off in range(n-1):
            t2+=1
            m=0
            for pos,v in r.items():
                i=(off+2*pos)%(n-1)
                if (d[i]*10+d[i+1])%26==v: m+=1
            if m>best2[0]: best2=(m,(f"{fam}/{pa}/{ca}",name,off))
print(f"\n(b) digit-pairs mod 26: tests={t2:,}  best={best2[0]}/24  {best2[1]}  (chance ~0.92)")

# (c) binary streams as a one-bit gate selecting between two alphabets
bins={}
for f in files:
    raw="".join(c for c in open(f,encoding="utf-8",errors="ignore").read() if c in "01")
    if len(raw)>=97: bins[os.path.basename(f)]=raw
print(f"\n(c) binary streams >=97 bits: {len(bins)}")
best3=(0,None); t3=0
for name,b in bins.items():
    n=len(b)
    for off in range(n):
        for fam in ("vig","beau","varbeau"):
            r0=req(fam,"plain","plain"); r1=req(fam,"kryptos","kryptos")
            t3+=1
            # gate picks which alphabet pairing applies at each position; test whether ANY single
            # constant shift per gate-state can satisfy all cribs
            g0={}; g1={}; ok=True
            for pos in r0:
                bit=b[(off+pos)%n]
                tgt=(g0 if bit=="0" else g1)
                v=(r0 if bit=="0" else r1)[pos]
                if pos%1==0:
                    tgt.setdefault("v",set()).add(v)
            m=(1 if len(g0.get("v",set()))<=1 else 0)+(1 if len(g1.get("v",set()))<=1 else 0)
            if m>best3[0]: best3=(m,(name,off,fam,len(g0.get('v',set())),len(g1.get('v',set()))))
print(f"    constant-shift-per-gate-state test: tests={t3:,}  best={best3[0]}/2 states constant  {best3[1]}")
print("    (a gate needs each state to force ONE shift value; observed distinct values per state above)")
