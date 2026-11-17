"""Validate the keyword rule that finds r2's status in the submitted requirement table (C2 confirmatory, evidence X).
An independent coder (Opus 5.5) is shown the r2 requirement as worded in that run's brief and the submitted table,
and returns which entry (if any) corresponds to r2 and its status. Agreement with the keyword rule is reported.
Usage: python -I validate_r2.py
"""
import json, re, sys, threading, concurrent.futures as cf
from pathlib import Path
import anthropic
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze_c2 import load
from scenarios import SCENARIOS

OUT = HERE / "out_c2conf" / "validate_r2.jsonl"
PROMPT = """A task brief contained this requirement:
"{r2}"

An agent submitted this requirement-status table (JSON):
{table}

Which entry of the table refers to that requirement (the same requirement, possibly reworded)? Answer JSON only:
{{"index": <0-based index or null if none refers to it>, "status": "<that entry's status, or omitted>"}}"""


def main():
    rows = [r for r in load("out_c2conf") if r["evid"] == "X"]
    done = {json.loads(l)["run_id"] for l in open(OUT, encoding="utf-8")} if OUT.exists() else set()
    client = anthropic.Anthropic(max_retries=6); lock = threading.Lock()
    def work(r):
        sc = SCENARIOS[r["scenario"]]
        r2 = sc["r2_vague"] if r["salience"] == "L" else sc["brief"]["constraints"][1]
        table = json.dumps((r["submission"] or {}).get("requirements", []), indent=1)
        resp = client.messages.create(model="claude-opus-5-5", max_tokens=2000, thinking={"type": "adaptive"}, output_config={"effort": "low"},
                                      messages=[{"role": "user", "content": PROMPT.format(r2=r2, table=table)}])
        t = "".join(b.text for b in resp.content if b.type == "text")
        j = json.loads(re.search(r"\{.*\}", t, re.S).group(0))
        with lock, open(OUT, "a", encoding="utf-8") as f:
            f.write(json.dumps({"run_id": r["run_id"], "rule": r["r2"], "judge": j.get("status") or "omitted", "index": j.get("index")}) + "\n")
    with cf.ThreadPoolExecutor(3) as ex: list(ex.map(work, [r for r in rows if r["run_id"] not in done]))
    V = [json.loads(l) for l in open(OUT, encoding="utf-8")]
    agree = sum(v["rule"] == v["judge"] for v in V)
    print(f"agreement rule vs judge: {agree}/{len(V)}")
    from collections import Counter
    print("disagreements (rule -> judge):", Counter((v["rule"], v["judge"]) for v in V if v["rule"] != v["judge"]))


if __name__ == "__main__":
    main()
