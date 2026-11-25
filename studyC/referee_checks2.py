"""Second round of pre-submission checks (exploratory). Usage: python -I referee_checks2.py"""
import json, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze_c2 import load
S45 = "claude-sonnet-4-5-20250929"

c2 = [r for r in load("out_c2conf") if r["evid"] == "X"]
c3g = [r for r in load("out_c3gpt") if r["evid"] == "X"]
f1 = load("out_c3fixF1"); f2 = load("out_c3fixF2")
main = c2 + c3g
print(f"1. Run counts. C2+C3 evidence-absent runs (excluding fix arms): {len(main)}; C2 evidence-present: {len([r for r in load('out_c2conf') if r['evid']=='M'])}; fix arms {len(f1)+len(f2)}")
print("   C2 status options offered: met / not_met / unknown (agent.py schema, FIX=None)")

print("\n2. UM by statement of r2 (H explicit numeric, L vague), per model")
for m in [S45, "claude-sonnet-5-5", "claude-haiku-5-5", "gpt-4.1-2025-04-14", "gpt-5.5-2026-04-23"]:
    for sal in "HL":
        x = [r for r in main if r["model"] == m and r["salience"] == sal]
        if x: print(f"   {m:28} {sal}: {sum(r['r2']=='met' for r in x)}/{len(x)}")

print("\n3. Non-claim outcomes in the main runs, by model (status of r2)")
for m in sorted(set(r["model"] for r in main)):
    x = [r for r in main if r["model"] == m]
    print(f"   {m:28} {dict(Counter(r['r2'] for r in x))}  no-decision {sum(r['outcome']!='submitted' for r in x)}")

print("\n4. F2 follow-through: runs with at least one rejection")
rej = [r for r in f2 if (r.get("rejections") or 0) > 0]
print(f"   {len(rej)} runs rejected; final r2 status: {dict(Counter(r['r2'] for r in rej))}")
print(f"   runs never rejected: {len(f2)-len(rej)}; their final r2 status: {dict(Counter(r['r2'] for r in f2 if not (r.get('rejections') or 0)))}")

print("\n5. GPT-5.5 PN in C3 by statement of r2 (C4 used the explicit form plus an added r1 threshold)")
for sal in "HL":
    x = [r for r in c3g if r["model"].startswith("gpt-5.5") and r["arch"] == "PN" and r["salience"] == sal]
    print(f"   {sal}: {sum(r['r2']=='met' for r in x)}/{len(x)}")

print("\n6. Claude 5.5 claims by question")
x = [r for r in c2 if r["model"] in ("claude-sonnet-5-5", "claude-haiku-5-5") and r["r2"] == "met"]
print("  ", dict(Counter(r["scenario"] for r in x)))
