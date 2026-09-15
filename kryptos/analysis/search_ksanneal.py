"""search_ksanneal.py -- (b) key streams implied by the annealed crib-consistent plaintexts.

Takes the plaintexts produced by search_anneal.py, derives the key stream each one implies
under each of the 24 cipher/alphabet combos, and runs every stream through the validated
battery of search_ksbattery.py.  Reports the whole multiple-testing budget explicitly: with
N plaintexts x 24 combos x 9 statistics, the number of |z| >= 3.5 EXPECTED by chance is
stated next to the number observed.

Also reports the sculpture-corpus and lateral-corpus substring hit counts against their
measured null rates (2.9% and 7.5% per stream respectively), because those are the tests
that could in principle point at a real key source.

Usage:
    python3.13 search_ksanneal.py [n_top] [n_random]
"""
import json, math, os, random, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import search_lm
import search_ksbattery as KB
import runningkey_lib as RK

A2Z = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CT = RK.K4_CT
COMBOS = list(RK.combos())
STATS = ["ioc", "per_excess", "rep4", "quad", "run", "ap", "d1", "ndistinct", "ac_z"]

def sweep(plaintexts, null, label):
    nz = {s: [] for s in STATS}
    hits_scu, hits_lat = [], []
    maxz = []
    for pt in plaintexts:
        for cb in COMBOS:
            ks = KB.keystream(cb, pt)
            b = KB.battery(ks, cb)
            z = KB.zrow(b, null)
            for s in STATS:
                nz[s].append(z[s])
            maxz.append(max(abs(v) for v in z.values()))
            if b["lcs_scu"]:
                hits_scu.append((RK.combo_name(cb), b["lcs_scu"], b["lcs_scu_src"], ks))
            if b["lcs_lat"]:
                hits_lat.append((RK.combo_name(cb), b["lcs_lat"], b["lcs_lat_src"], ks))
    n_streams = len(plaintexts) * len(COMBOS)
    n_z = n_streams * len(STATS)
    print("-" * 100)
    print(f"{label}: {len(plaintexts)} plaintexts x {len(COMBOS)} combos = {n_streams} key streams, "
          f"{n_z} z-scores")
    print("-" * 100)
    print(f"{'statistic':12s} {'mean z':>8s} {'sd z':>7s} {'max|z|':>8s} {'n |z|>=3.5':>11s} {'expected':>9s}")
    exp_per_stat = n_streams * 2 * (1 - 0.5 * (1 + math.erf(3.5 / math.sqrt(2))))
    for s in STATS:
        v = nz[s]
        n35 = sum(1 for x in v if abs(x) >= 3.5)
        print(f"{s:12s} {sum(v)/len(v):8.2f} "
              f"{(sum((x - sum(v)/len(v))**2 for x in v)/len(v))**0.5:7.2f} "
              f"{max(abs(x) for x in v):8.2f} {n35:11d} {exp_per_stat:9.1f}")
    print(f"{'ALL':12s} {'':8s} {'':7s} {max(maxz):8.2f} "
          f"{sum(1 for x in maxz if x >= 3.5):11d} {exp_per_stat*len(STATS):9.1f}   "
          f"(streams with any |z|>=3.5)")
    print()
    er_s = null["_lcs_scu_rate"] * n_streams
    er_l = null["_lcs_lat_rate"] * n_streams
    print(f"sculpture-corpus substring hits (>=5 letters): {len(hits_scu):5d}   "
          f"expected by chance {er_s:.1f}  ratio {len(hits_scu)/er_s if er_s else 0:.2f}")
    print(f"lateral-corpus   substring hits (>=5 letters): {len(hits_lat):5d}   "
          f"expected by chance {er_l:.1f}  ratio {len(hits_lat)/er_l if er_l else 0:.2f}")
    if hits_scu:
        c = Counter(h[1] for h in hits_scu)
        print("   most common sculpture matches:", c.most_common(6))
        print("   longest:", max(hits_scu, key=lambda h: len(h[1]))[:3])
    if hits_lat:
        c = Counter(h[1] for h in hits_lat)
        print("   most common lateral matches:", c.most_common(6))
        print("   longest:", max(hits_lat, key=lambda h: len(h[1]))[:3])
    print()
    return dict(maxz=maxz, hits_scu=len(hits_scu), hits_lat=len(hits_lat))

def main():
    ntop = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    nrnd = int(sys.argv[2]) if len(sys.argv) > 2 else 150
    null = KB.build_null()
    with open(os.path.join(HERE, "search_anneal_k4.json")) as f:
        res = json.load(f)
    res.sort(key=lambda t: -t[0])
    print(f"annealed plaintexts available: {len(res)}   "
          f"score range {res[-1][0]:.4f} .. {res[0][0]:.4f}")
    print()
    top = [t[1] for t in res[:ntop]]
    sweep(top, null, f"TOP-{ntop} ANNEALED PLAINTEXTS (highest language-model score)")

    rnd = random.Random(31337)
    # matched null: random plaintexts with the same 24 crib letters pinned
    rndpt = []
    for _ in range(nrnd):
        rndpt.append("".join(RK.CRIBS.get(i, A2Z[rnd.randrange(26)]) for i in range(97)))
    sweep(rndpt, null, f"{nrnd} CRIB-PINNED RANDOM PLAINTEXTS (matched null)")

    # and the single best annealed plaintext, in full
    print("=" * 100)
    print("The single highest-scoring annealed plaintext, in full:")
    print("=" * 100)
    KB.score_plaintext(res[0][1], f"best annealed (score {res[0][0]:.4f})", null=null, verbose=True)

if __name__ == "__main__":
    main()
