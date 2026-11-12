"""Planted-cipher check for lp_multfeedback.py: encrypt real English runes with
multiplicative feedback keyed by phi(prime) at a hidden offset, then run the same search."""
import numpy as np, runpy, sys
sys.argv = ["x"]
g = runpy.run_path("lp_multfeedback.py", run_name="not_main") if False else None
from lp_common import IDX, LATIN
exec(open("lp_multfeedback.py").read().split("secs = []")[0])   # reuse streams, INV, ioc helpers' deps
# English runes from the corpus (same converter as lp_streams.py)
raw_t = open("/Users/pravarkataria/Desktop/crypto/kryptos/analysis/.search_corpus.txt").read(5000)
DI = {"TH": 2, "EO": 12, "NG": 21, "OE": 22, "AE": 25, "IA": 27, "IO": 27, "EA": 28}
SG = {Lt: i for i, Lt in enumerate(LATIN) if len(Lt) == 1}; SG.update({"K": 5, "Q": 5, "V": 1, "Z": 15})
eng, i = [], 0
while len(eng) < 500:
    for dg in DI:
        if raw_t.startswith(dg, i): eng.append(DI[dg]); i += 2; break
    else:
        if raw_t[i] in SG: eng.append(SG[raw_t[i]])
        i += 1
eng = np.array(eng)
m = dict(stream_variants())["phi(prime)=p-1 [filter0]"]
HID, z = 7321, 18
c = np.zeros(len(eng), np.int64); c[0] = 5
for k in range(1, len(eng)):
    c[k] = (c[k-1] + m[HID + k - 1] * (eng[k] - z)) % 29
d = (c[1:L+1] - c[:L]) % 29
s = m
W = np.lib.stride_tricks.sliding_window_view(s, L)[:OFF]
rows = W.shape[0]
Q = (d[None, :] * INV[W]) % 29
cnt = np.bincount((np.arange(rows)[:, None] * 29 + Q).ravel(), minlength=rows * 29).reshape(rows, 29)
io = 29 * (cnt * (cnt - 1)).sum(1) / (L * (L - 1))
print(f"planted offset {HID}: search found offset {int(io.argmax())} with IoC {io.max():.3f} (next best {np.sort(io)[-2]:.3f})")
