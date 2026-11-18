"""Pre-registered tests for C3 (PREREGISTRATION_C3.md)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_c2 import load
from scipy.stats import fisher_exact
um = lambda r: r["r2"] == "met"
nd = lambda r: r["outcome"] != "submitted"
def t(a, b): return [[sum(map(um, a)), len(a) - sum(map(um, a))], [sum(map(um, b)), len(b) - sum(map(um, b))]]
g = load("out_c3gpt"); f1 = load("out_c3fixF1"); f2 = load("out_c3fixF2")
ctrl = [r for r in load("out_c2conf") if r["evid"] == "X" and r["model"] == "claude-sonnet-4-5-20250929" and r["arch"] in ("SC", "PN")]
g41 = [r for r in g if r["model"].startswith("gpt-4.1")]; g55 = [r for r in g if r["model"].startswith("gpt-5.5")]
tests = {"H3 GPT-4.1 > GPT-5.5": (g41, g55), "H4 control > F2": (ctrl, f2), "H5 control > F1": (ctrl, f1)}
ps = {k: fisher_exact(t(a, b), "greater")[1] for k, (a, b) in tests.items()}
order = sorted(ps, key=ps.get); holm = {}; run = 0
for i, k in enumerate(order): run = max(run, min(1, (3 - i) * ps[k])); holm[k] = run
for k, (a, b) in tests.items():
    print(f"{k}: {sum(map(um,a))}/{len(a)} vs {sum(map(um,b))}/{len(b)}  p={ps[k]:.2e}  Holm p={holm[k]:.2e}")
print("\nSensitivity, excluding runs without a decision:")
for k, (a, b) in tests.items():
    a2 = [r for r in a if not nd(r)]; b2 = [r for r in b if not nd(r)]
    print(f"  {k}: {sum(map(um,a2))}/{len(a2)} vs {sum(map(um,b2))}/{len(b2)}  p={fisher_exact(t(a2,b2),'greater')[1]:.2e}")
print("\nBreakdown (met / not_evaluated|unknown / omitted / no decision):")
for name, x in [("GPT-4.1", g41), ("GPT-5.5", g55), ("Son4.5 control", ctrl), ("Son4.5 F1", f1), ("Son4.5 F2", f2)]:
    for a in ["SC", "PN"]:
        y = [r for r in x if r["arch"] == a]
        print(f"  {name:15} {a}: met {sum(map(um,y))}/{len(y)}, notev/unk {sum(r['r2'] in ('not_evaluated','unknown') for r in y)}, omitted {sum(r['r2']=='omitted' for r in y)}, no-decision {sum(map(nd,y))}, mean r1 sims {sum(r['n_r1_calls'] for r in y)/len(y):.1f}")
print("\nRejections under F2:", sum(r.get("rejections") or 0 for r in f2), "across", sum(bool(r.get("rejections")) for r in f2), "runs")
cost = sum(r["cost"] for r in g + f1 + f2); print(f"cost ${cost:.2f}")
