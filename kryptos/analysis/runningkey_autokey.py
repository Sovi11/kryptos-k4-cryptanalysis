"""Item 3: autokey tests.
Plaintext autokey: key_i = prime_i (i<p) else P_{i-p}.  Starting from the 24 crib letters, propagate
forward (P_i known & C_{i+p} known -> P_{i+p}) and backward (P_i, C_i -> K_i = P_{i-p}); every time
propagation reaches a position already known we get a consistency check.
Ciphertext autokey: key_i = prime_i (i<p) else C_{i-p}: every crib position i>=p is a hard check.
p is taken 1..96 (the task asks 1..21; the rest is reported as an extension)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import runningkey_lib as L

N = 97

def pt_autokey(cb, p):
    """Each residue class r (mod p) is one autokey chain: P_r, P_{r+p}, P_{r+2p}, ... with
    key_{r} = prime_r and key_{j} = P_{j-p} for j>=p.  One crib in a class determines the whole
    chain (forward: P_j = D(C_j, P_{j-p}); backward: P_{j-p} = K_j = derive(P_j, C_j)); every
    further crib in that class is an independent check.  checks = 24 - (#classes with a crib)."""
    classes = {}
    for i in L.CRIBS:
        classes.setdefault(i % p, []).append(i)
    P = {}; prime = {}
    checks = conflicts = 0
    for r, members in classes.items():
        seed = min(members)
        P[seed] = L.CRIBS[seed]
        j = seed + p
        while j < N:
            P[j] = L.decrypt_letter(cb, L.K4_CT[j], P[j - p]); j += p
        j = seed
        while j - p >= 0:
            P[j - p] = L.derive_key_letter(cb, P[j], L.K4_CT[j]); j -= p
        prime[r] = L.derive_key_letter(cb, P[r], L.K4_CT[r])
        for i in members:
            if i != seed:
                checks += 1
                if P[i] != L.CRIBS[i]: conflicts += 1
    pt = "".join(P.get(i, ".") for i in range(N))
    pr = "".join(prime.get(i, ".") for i in range(p))
    return checks, conflicts, pt, pr

def ct_autokey(cb, p):
    checks = matches = 0
    for i, pl in L.CRIBS.items():
        if i >= p:
            checks += 1
            if L.derive_key_letter(cb, pl, L.K4_CT[i]) == L.K4_CT[i - p]: matches += 1
    return checks, matches

def run():
    md = ["## 3. Autokey (plaintext-autokey and ciphertext-autokey)\n"]
    md.append("### Plaintext autokey\n")
    md.append("For each (combo, p): propagate the cribs through the autokey chain in both directions; "
              "`checks` = number of positions reached twice (consistency tests), `conflicts` = failed checks. "
              "A (combo, p) survives only if checks>0 and conflicts=0.  With plaintext autokey the cribs determine the "
              "plaintext on every residue class mod p that contains a crib, so a survivor yields a large partial decryption.\n")
    surv = []; vac = []
    total = 0
    rows = []
    for p in range(1, N):
        for cb in L.combos():
            total += 1
            ch, cf, pt, pr = pt_autokey(cb, p)
            if ch == 0:
                vac.append((cb, p, pt, pr))
            elif cf == 0:
                surv.append((cb, p, ch, pt, pr))
            rows.append((p, cb, ch, cf))
    md.append(f"Tested {total} (combo, p) pairs (24 combos x p=1..96).\n")
    # summary per p for p<=21
    md.append("Per-p summary for p=1..21 (over the 24 combos): number of checks available, and min conflicts over combos:\n")
    md.append("| p | checks (per combo) | combos with 0 conflicts | min conflicts |\n|---|---|---|---|")
    for p in range(1, 22):
        rs = [r for r in rows if r[0] == p]
        ch = rs[0][2]
        zero = sum(1 for r in rs if r[3] == 0 and r[2] > 0)
        md.append(f"| {p} | {ch} | {zero} | {min(r[3] for r in rs)} |")
    md.append("")
    # expected number of chance survivors: sum over (combo,p) of 26^-checks
    exp = sum(26.0 ** (-r[2]) for r in rows if r[2] > 0)
    md.append(f"**Survivors with checks>0 and 0 conflicts (all p=1..96): {len(surv)}** (expected by chance, "
              f"assuming independent uniform letters: {exp:.2f}).  Survivors by number of checks: " +
              ", ".join(f"{c} checks: {sum(1 for s_ in surv if s_[2]==c)}" for c in sorted(set(s_[2] for s_ in surv))) + "\n")
    md.append("Checks available per p for p=22..52 (24 combos each; p>=53 has no two cribs in one chain): " +
              ", ".join(f"p{p}:{[r for r in rows if r[0]==p][0][2]}" for p in range(22, 53)) + "\n")
    md.append("Survivors with >=3 checks (chance probability <= 26^-3 = 5.7e-5 each):\n")
    strong = [s_ for s_ in surv if s_[2] >= 3]
    if not strong: md.append("- none")
    for cb, p, ch, pt, pr in strong:
        md.append(f"- {L.combo_name(cb)}, p={p}, checks={ch}: prime=`{pr}`\n  pt=`{pt}` (english score {L.english_score(pt):.2f})")
    md.append("\nAll survivors with 1-2 checks (chance level; the forced partial plaintext is shown so it can be eyeballed):\n")
    for cb, p, ch, pt, pr in surv:
        if ch < 3:
            md.append(f"- {L.combo_name(cb)}, p={p}, checks={ch}: pt=`{pt}` (score {L.english_score(pt):.2f})")
    md.append(f"\nVacuous (checks=0) pairs: {len(vac)} — these are p values for which no two crib positions are linked by the chain, "
              "so the cribs impose no constraint; they are listed below with the partial plaintext the cribs force, for eyeballing:\n")
    # Vacuous list: p values only
    vp = sorted(set(p for _, p, _, _ in vac))
    md.append(f"p with zero checks for every combo: {vp}\n")
    # Show for the vacuous p the best-scoring partial decryptions (they're weakly informative)
    scored = sorted(vac, key=lambda t: -L.english_score(t[2]))[:10]
    md.append("Top-10 partial decryptions (by crude English bigram/trigram score) among vacuous (combo,p):\n")
    for cb, p, pt, pr in scored:
        md.append(f"- {L.combo_name(cb)}, p={p}: `{pt}` score {L.english_score(pt):.2f}")
    md.append("")
    # Ciphertext autokey
    md.append("### Ciphertext autokey\n")
    md.append("key_i = C_{i-p} for i>=p, so each crib position i>=p is one hard letter test. Expected matches under "
              "randomness = checks/26.\n")
    md.append("| p | checks | best matches over 24 combos | combo(s) achieving it |\n|---|---|---|---|")
    csurv = []
    total = 0
    for p in range(1, N):
        res = []
        for cb in L.combos():
            total += 1
            ch, m = ct_autokey(cb, p)
            res.append((m, cb, ch))
            if ch > 0 and m == ch: csurv.append((cb, p, ch))
        ch = res[0][2]
        if ch == 0: continue
        bm = max(r[0] for r in res)
        who = ", ".join(L.combo_name(r[1]) for r in res if r[0] == bm)
        if p <= 21 or bm >= 4:
            md.append(f"| {p} | {ch} | {bm} | {who if bm >= 3 else '-'} |")
    md.append(f"\nTested {total} (combo, p) pairs. **Full survivors (all checks pass, checks>0): {len(csurv)}**")
    for cb, p, ch in csurv:
        ks = ["?"] * p + [L.K4_CT[i - p] for i in range(p, N)]
        pt = "".join(L.decrypt_letter(cb, L.K4_CT[i], ks[i]) if ks[i] != "?" else "." for i in range(N))
        md.append(f"- {L.combo_name(cb)}, p={p}, checks={ch}: pt=`{pt}`")
    return "\n".join(md)

if __name__ == "__main__":
    print(run())
