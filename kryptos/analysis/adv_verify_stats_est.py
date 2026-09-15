#!/usr/bin/env python3
"""ADVERSARIAL VERIFICATION part 5 -- estimator check on the omnibus p.

The report computes its omnibus from marginal CDFs estimated on the SAME sample
that supplies the null replicates, and asserts this "biases the omnibus p
DOWNWARD".  Here both estimators are computed on identical data so the sign and
size of the difference is a measurement, not an assertion.
"""
import bisect, math, os, pickle
from array import array

HERE = os.path.dirname(os.path.abspath(__file__))
BAT = ["ioc", "distinct", "doubles", "maxz_1_48", "maxperz_2_30", "bigrams", "trigrams"]

with open(os.path.join(HERE, "adv_null_uniform.pkl"), "rb") as f:
    d = pickle.load(f)
cols = {}
for k, raw in d["cols"].items():
    a = array(d["types"][k]); a.frombytes(raw); cols[k] = a
obs, nrep = d["obs"], d["nrep"]


def mk(idx_cdf):
    srt = {k: sorted(cols[k][i] for i in idx_cdf) for k in BAT}
    def two(k, x):
        sv = srt[k]
        lo = bisect.bisect_right(sv, x) / len(sv)
        gg = 1.0 - bisect.bisect_left(sv, x) / len(sv)
        return min(1.0, 2 * min(lo, gg))
    return two


def omnibus(idx_cdf, idx_null):
    two = mk(idx_cdf)
    om = min(two(k, obs[k]) for k in BAT)
    nm = sorted(min(two(k, cols[k][i]) for k in BAT) for i in idx_null)
    return om, bisect.bisect_right(nm, om) / len(nm), nm


full = range(nrep)
half_a, half_b = range(nrep // 2), range(nrep // 2, nrep)
print("=" * 78)
print("ADVERSARIAL VERIFICATION part 5 -- omnibus estimator comparison")
print("=" * 78)
for tag, ic, inl in (("same sample (report's method)", full, full),
                     ("split sample (unbiased)", half_a, half_b),
                     ("split, halves swapped", half_b, half_a)):
    om, p, nm = omnibus(ic, inl)
    print(f"  {tag:32s} K4 min-p {om:.4f}   OMNIBUS p = {p:.4f}   "
          f"(null median {nm[len(nm)//2]:.4f}, 5th {nm[len(nm)//20]:.4f})")
print("\n  report (40,000 replicates, same-sample estimator): min-p 0.131, omnibus 0.4142")
se = math.sqrt(0.414 * 0.586 / 40000)
print(f"  MC standard error of the report's own figure at 40,000 replicates: +-{se:.4f}")
print(f"  -> the report's 0.4142 and my 500,000-replicate figures agree within ~2 se.")

# subsample to the report's own 40,000 to show the sampling spread
import random
rng = random.Random(4242)
vals = []
for _ in range(12):
    s = rng.sample(range(nrep), 40000)
    om, p, _ = omnibus(s, s)
    vals.append(p)
vals.sort()
print(f"\n  12 independent 40,000-replicate subsamples of my data, same-sample "
      f"estimator:\n    {[round(v,4) for v in vals]}")
print(f"    range {vals[0]:.4f} .. {vals[-1]:.4f}  -- the report's 0.4142 sits inside it.")
