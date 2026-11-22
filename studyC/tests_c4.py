"""Pre-registered test for C4 (PREREGISTRATION_C4.md). Usage: python -I tests_c4.py"""
import json, math, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze_c2 import r2_status
from scenarios import R1_KW
from scipy.stats import fisher_exact, chi2
import numpy as np

THR = {"S5_fcal": "4.5", "S6_trigger": "80", "S7_gas": "1.5", "S8_rich": "3.5"}


def r1_status(r):
    for e in ((r.get("submission") or {}).get("requirements") or []):
        t = (e.get("requirement", "") + " ").lower()
        if any(k in t for k in R1_KW[r["scenario"]]) and THR[r["scenario"]] in t: return e.get("status", "omitted")
    return "omitted" if r.get("submission") else "no_submission"


rows = []
for out in ["out_c4", "out_c4gpt"]:
    for p in (HERE / out).glob("*/result.json"):
        r = json.loads(p.read_text(encoding="utf-8"))
        if "arch" not in r: continue
        r["U"] = (r2_status(r) if r["evid"] == "X" else r1_status(r)) == "met"
        r["r1"] = r1_status(r); r["r2"] = r2_status(r); rows.append(r)
X = [r for r in rows if r["evid"] == "X"]; Y = [r for r in rows if r["evid"] == "Y"]
k1, n1, k2, n2 = sum(r["U"] for r in X), len(X), sum(r["U"] for r in Y), len(Y)
p = fisher_exact([[k1, n1 - k1], [k2, n2 - k2]], "greater")[1]


def wilson(k, n, z=1.96):
    ph = k / n; d = 1 + z*z/n; c = (ph + z*z/(2*n)) / d; h = z*math.sqrt(ph*(1-ph)/n + z*z/(4*n*n)) / d; return c - h, c + h


l1, u1 = wilson(k1, n1); l2, u2 = wilson(k2, n2); d = k1/n1 - k2/n2
lo = d - math.sqrt((k1/n1 - l1)**2 + (u2 - k2/n2)**2); hi = d + math.sqrt((u1 - k1/n1)**2 + (k2/n2 - l2)**2)
ts = []
for key in sorted(set((r["model"], r["arch"], r["scenario"]) for r in rows)):
    a = [r for r in X if (r["model"], r["arch"], r["scenario"]) == key]; b = [r for r in Y if (r["model"], r["arch"], r["scenario"]) == key]
    t = np.array([[sum(r["U"] for r in a), len(a) - sum(r["U"] for r in a)], [sum(r["U"] for r in b), len(b) - sum(r["U"] for r in b)]], float)
    if t.sum(1).min() > 0 and t.sum(0).min() > 0: ts.append(t)
A = sum(t[0, 0] for t in ts); E = sum(t[0].sum() * t[:, 0].sum() / t.sum() for t in ts)
V = sum(t[0].sum() * t[1].sum() * t[:, 0].sum() * t[:, 1].sum() / (t.sum() ** 2 * (t.sum() - 1)) for t in ts)
cmh = chi2.sf((abs(A - E) - 0.5) ** 2 / V, 1) if V > 0 else float("nan")
print(f"H6  X (unsimulatable unevaluable) {k1}/{n1} vs Y (simulatable unevaluable) {k2}/{n2}")
print(f"    difference {d:.2f}, 95% Newcombe CI [{lo:.2f}, {hi:.2f}], one-sided Fisher p={p:.2e}, CMH p={cmh:.2e}")
for m in sorted(set(r["model"] for r in rows)):
    for arch in ["SC", "PN"]:
        x = [r for r in X if r["model"] == m and r["arch"] == arch]; y = [r for r in Y if r["model"] == m and r["arch"] == arch]
        if x and y:
            print(f"  {m:28} {arch}: X {sum(r['U'] for r in x)}/{len(x)}   Y {sum(r['U'] for r in y)}/{len(y)}   "
                  f"Y r1 statuses {dict((s, sum(r['r1'] == s for r in y)) for s in set(r['r1'] for r in y))}")
print("no decision:", sum(r["outcome"] != "submitted" for r in rows), " | Y r2 statuses:",
      dict((s, sum(r["r2"] == s for r in Y)) for s in set(r["r2"] for r in Y)))
print(f"cost ${sum(r['cost'] for r in rows):.2f}")
