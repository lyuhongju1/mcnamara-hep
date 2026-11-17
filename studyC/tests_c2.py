"""Pre-registered tests for C2 (PREREGISTRATION_C2.md)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_c2 import load
from scipy.stats import fisher_exact
from scipy.stats import chi2
import numpy as np
rows = [r for r in load("out_c2conf") if r["evid"] == "X"]
S45 = "claude-sonnet-4-5-20250929"
um = lambda r: r["r2"] == "met"
def tab(a, b): return [[sum(map(um, a)), len(a) - sum(map(um, a))], [sum(map(um, b)), len(b) - sum(map(um, b))]]
def cmh(a, b, key):
    ts = []
    for k in sorted(set(map(key, a + b))):
        t = np.array(tab([r for r in a if key(r) == k], [r for r in b if key(r) == k]), float)
        if t.sum(1).min() > 0 and t.sum(0).min() > 0: ts.append(t)
    # Mantel-Haenszel chi-square with continuity correction (two-sided)
    if not ts: return float("nan")
    a = sum(t[0, 0] for t in ts); e = sum(t[0].sum() * t[:, 0].sum() / t.sum() for t in ts)
    v = sum(t[0].sum() * t[1].sum() * t[:, 0].sum() * t[:, 1].sum() / (t.sum() ** 2 * (t.sum() - 1)) for t in ts)
    return chi2.sf((abs(a - e) - 0.5) ** 2 / v, 1)
shared = [r for r in rows if r["arch"] in ("SC", "PN")]
old = [r for r in shared if r["model"] == S45]; new = [r for r in shared if r["model"] != S45]
t1 = tab(old, new); p1 = fisher_exact(t1, "greater")[1]
p1c = cmh(old, new, lambda r: (r["scenario"], r["salience"], r["arch"]))
pn = [r for r in rows if r["model"] == S45 and r["arch"] == "PN"]; sc = [r for r in rows if r["model"] == S45 and r["arch"] == "SC"]
pt = [r for r in rows if r["model"] == S45 and r["arch"] == "PT"]
t2 = tab(pn, sc); p2 = fisher_exact(t2, "greater")[1]; p2c = cmh(pn, sc, lambda r: (r["scenario"], r["salience"]))
ps = sorted([(p1, "H1"), (p2, "H2")]); holm = {ps[0][1]: min(1, 2 * ps[0][0]), ps[1][1]: min(1, max(2 * ps[0][0], ps[1][0]))}
print(f"H1 Sonnet4.5 UM {t1[0][0]}/{len(old)} vs 5.5 models {t1[1][0]}/{len(new)}: Fisher p={p1:.2e}, Holm p={holm['H1']:.2e}, CMH p={p1c:.2e}")
print(f"H2 Sonnet4.5 PN {t2[0][0]}/{len(pn)} vs SC {t2[1][0]}/{len(sc)}: Fisher p={p2:.3f}, Holm p={holm['H2']:.3f}, CMH p(two-sided)={p2c:.3f}")
print(f"Secondary: PT {sum(map(um, pt))}/{len(pt)}; PT<PN Fisher p={fisher_exact(tab(pn, pt), 'greater')[1]:.3f}")
for m in sorted(set(r["model"] for r in rows)):
    for a in ["SC", "PN", "PT"]:
        x = [r for r in rows if r["model"] == m and r["arch"] == a]
        if x: print(f"  {m:28} {a}: met {sum(map(um, x))}/{len(x)}, unknown {sum(r['r2']=='unknown' for r in x)}, omitted {sum(r['r2']=='omitted' for r in x)}")
for s in "HL":
    x = [r for r in rows if r["model"] == S45 and r["salience"] == s]; print(f"  Sonnet4.5 salience {s}: met {sum(map(um, x))}/{len(x)}")
for sc_ in sorted(set(r["scenario"] for r in rows)):
    x = [r for r in rows if r["model"] == S45 and r["scenario"] == sc_]; print(f"  Sonnet4.5 {sc_}: met {sum(map(um, x))}/{len(x)}")
M = [r for r in load("out_c2conf") if r["evid"] == "M"]
print(f"Evidence-present arm: violations {sum(r['V'] for r in M)}/{len(M)}; served-model fallbacks check below")
