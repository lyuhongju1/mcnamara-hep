"""Additional analyses requested in a pre-submission review (exploratory unless stated). Usage: python -I referee_checks.py"""
import json, math, random, sys
from collections import defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze_c2 import load, r2_status
S45 = "claude-sonnet-4-5-20250929"; NEW = ("claude-sonnet-5-5", "claude-haiku-5-5")
um = lambda r: r["r2"] == "met"


def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z*z/n; c = (p + z*z/(2*n)) / d; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d; return c - h, c + h


def newcombe(k1, n1, k2, n2):
    p1, p2 = k1/n1, k2/n2; l1, u1 = wilson(k1, n1); l2, u2 = wilson(k2, n2); d = p1 - p2
    return d, d - math.sqrt((p1-l1)**2 + (u2-p2)**2), d + math.sqrt((u1-p1)**2 + (p2-l2)**2)


c2 = [r for r in load("out_c2conf") if r["evid"] == "X"]
print("1. H1 per question (Sonnet 4.5 vs Claude 5.5 models, SC+PN)")
for s in sorted(set(r["scenario"] for r in c2)):
    a = [r for r in c2 if r["scenario"] == s and r["model"] == S45 and r["arch"] in ("SC", "PN")]
    b = [r for r in c2 if r["scenario"] == s and r["model"] in NEW]
    print(f"   {s:12} Sonnet4.5 {sum(map(um,a))}/{len(a)}  vs  5.5 models {sum(map(um,b))}/{len(b)}")
# question-clustered bootstrap of the H1 difference
qs = sorted(set(r["scenario"] for r in c2)); rng = random.Random(7); ds = []
for _ in range(10000):
    pick = [rng.choice(qs) for _ in qs]
    a = [r for q in pick for r in c2 if r["scenario"] == q and r["model"] == S45 and r["arch"] in ("SC", "PN")]
    b = [r for q in pick for r in c2 if r["scenario"] == q and r["model"] in NEW]
    ds.append(sum(map(um, a))/len(a) - sum(map(um, b))/len(b))
ds.sort(); print(f"   H1 difference, question-clustered bootstrap 95% interval [{ds[250]:.2f}, {ds[9750]:.2f}] (4 clusters, coarse)")

print("\n2. Which option did runs claiming r2 'met' choose? (C2+C3, evidence absent; A truly fails r2)")
allx = c2 + [r for o in ["out_c3gpt", "out_c3fixF1", "out_c3fixF2"] for r in load(o) if r["evid"] == "X"]
m = [r for r in allx if um(r)]
cnt = defaultdict(int)
for r in m: cnt[r["choice_role"]] += 1
print(f"   {len(m)} claims; chosen option roles {dict(cnt)}; share A = {cnt['A']/len(m):.2f}")
print("   (Option A's r2 status is FAIL in truth in every scenario; its description gives no r2 value.)")
for s in sorted(set(r["scenario"] for r in m)):
    x = [r for r in m if r["scenario"] == s]; print(f"   {s:12} claims {len(x)}, of which chose A {sum(r['choice_role']=='A' for r in x)}")

print("\n3. C4 condition Y (r2 memo PRESENT, r1 unevaluable): did agents choose the r2-failing option A?")
c4 = [r for o in ["out_c4", "out_c4gpt"] for r in load(o) if r["evid"] == "Y"]
for mdl in sorted(set(r["model"] for r in c4)):
    x = [r for r in c4 if r["model"] == mdl]
    print(f"   {mdl:28} n={len(x)} chose A {sum(r['choice_role']=='A' for r in x)}, chose B {sum(r['choice_role']=='B' for r in x)}, chose C {sum(r['choice_role']=='C' for r in x)}, read memo {sum(bool(r['read_memo']) for r in x)}")

print("\n4. C4 difference to three decimals")
c4x = [r for o in ["out_c4", "out_c4gpt"] for r in load(o) if r["evid"] == "X"]
print(f"   X {sum(r['r2']=='met' for r in c4x)}/{len(c4x)}; see tests_c4.py for Y; 45/80 - 31/80 = {45/80-31/80:.3f}; Newcombe {newcombe(45,80,31,80)}")

print("\n5. Study A, Newcombe interval instead of cluster bootstrap")
# T: substantive/non-split among both-T; U: 3/8 (from BLIND_RESULTS.txt: T substantive 52, not 14)
d, lo, hi = newcombe(52, 66, 3, 8); print(f"   T 52/66 vs U 3/8, difference {d:.2f}, Newcombe 95% CI [{lo:.2f}, {hi:.2f}]; Wilson U {wilson(3,8)}")
