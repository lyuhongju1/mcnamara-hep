"""Agreement between the original (unblinded) coder and the two blind LLM coders, plus the blind-consensus cross-tab.
Primary Study A quantity (decided before the blind codes were seen, 2026-11-15):
  among requirements both blind coders class as U vs as T, the share treated substantively (code Q or D),
  with a cluster bootstrap over tasks (v4/v7 and v5/v9 runs of the same task form one cluster).
Usage: python -I agreement.py
"""
import json, os, random
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
L = lambda f: [json.loads(l) for l in open(os.path.join(HERE, f), encoding="utf-8")]
orig = {(r["run"], r["req_id"]): r for r in L("coding.jsonl")}
cls = defaultdict(dict); trt = defaultdict(dict)
for r in L("blind_class.jsonl"): cls[(r["run"], r["req_id"])][r["coder"]] = r.get("class")
for r in L("blind_treat.jsonl"): trt[(r["run"], r["req_id"])][r["coder"]] = r


def kappa(a, b):
    n = len(a); cats = sorted(set(a) | set(b))
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


out = []
keys = [k for k in orig if k in cls and len(cls[k]) == 2 and k in trt and len(trt[k]) == 2]
oc = [orig[k]["class"].rstrip("?") for k in keys]
o_, s_ = [cls[k]["opus"] for k in keys], [cls[k]["sonnet"] for k in keys]
out.append(f"n requirements with both blind codes: {len(keys)}")
out.append(f"CLASS kappa: opus-sonnet {kappa(o_, s_):.2f}, orig-opus {kappa(oc, o_):.2f}, orig-sonnet {kappa(oc, s_):.2f}")
ot = [orig[k]["code"] for k in keys]; to_ = [trt[k]["opus"].get("code") for k in keys]; ts_ = [trt[k]["sonnet"].get("code") for k in keys]
out.append(f"TREATMENT kappa (Q/D/M/X): opus-sonnet {kappa(to_, ts_):.2f}, orig-opus {kappa(ot, to_):.2f}, orig-sonnet {kappa(ot, ts_):.2f}")
sub = lambda c: "S" if c in ("Q", "D") else "N"
out.append(f"TREATMENT kappa (substantive vs not): opus-sonnet {kappa([sub(x) for x in to_], [sub(x) for x in ts_]):.2f}")

# blind consensus: class agreed by both blind coders; treatment = substantive if both say Q/D, not if both say M/X, else split
rows = []
for k in keys:
    c = cls[k]["opus"] if cls[k]["opus"] == cls[k]["sonnet"] else "?"
    a, b = sub(trt[k]["opus"].get("code")), sub(trt[k]["sonnet"].get("code"))
    t = a if a == b else "split"
    task = k[0].split("/")[1]; fam = "celeritas" if "celeritas" in k[0] else "opticks"
    rows.append(dict(key=k, cls=c, sub=t, cluster=fam + "/" + task,
                     proxy=all(trt[k][x].get("proxy") for x in ("opus", "sonnet")),
                     deferred=all(trt[k][x].get("deferred") for x in ("opus", "sonnet")),
                     dismiss=all(trt[k][x].get("dismiss") for x in ("opus", "sonnet"))))
out.append("\nBlind consensus cross-tab (class x substantive treatment):")
ct = Counter((r["cls"], r["sub"]) for r in rows)
for c in ["T", "U", "?"]:
    out.append(f"  {c}: substantive={ct[(c,'S')]}, not={ct[(c,'N')]}, split={ct[(c,'split')]}")
for c in ["T", "U"]:
    x = [r for r in rows if r["cls"] == c]
    out.append(f"  {c}: proxy (both coders)={sum(r['proxy'] for r in x)}, deferred={sum(r['deferred'] for r in x)}, dismissed={sum(r['dismiss'] for r in x)}")


def share(rs, c):
    x = [r for r in rs if r["cls"] == c and r["sub"] != "split"]
    return sum(r["sub"] == "S" for r in x) / len(x) if x else float("nan")


diff = share(rows, "T") - share(rows, "U")
clusters = sorted(set(r["cluster"] for r in rows)); rng = random.Random(1); boots = []
for _ in range(5000):
    pick = [rng.choice(clusters) for _ in clusters]
    rs = [r for c in pick for r in rows if r["cluster"] == c]
    d = share(rs, "T") - share(rs, "U")
    if d == d: boots.append(d)
boots.sort()
out.append(f"\nPRIMARY: substantive share T {share(rows,'T'):.2f} vs U {share(rows,'U'):.2f}; difference {diff:.2f}, "
           f"95% cluster-bootstrap CI [{boots[int(.025*len(boots))]:.2f}, {boots[int(.975*len(boots))]:.2f}] over {len(clusters)} task clusters")
s = "\n".join(out); open(os.path.join(HERE, "BLIND_RESULTS.txt"), "w", encoding="utf-8").write(s); print(s)
