"""Second, cross-provider coder for the justification types: GPT-5.5 codes all unsupported 'met' claims with the
identical prompt used for Opus 5.5 (justification_types.py), then per-label agreement and Cohen's kappa are reported.
Usage: python -I justification_types_gpt.py
"""
import json, re, sys, threading, concurrent.futures as cf
from pathlib import Path
from openai import OpenAI
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze_c2 import load, KW
from scenarios import SCENARIOS
from justification_types import PROMPT, docs_text
from openai_runner import key
OUT = HERE / "justification_types_gpt.jsonl"
LABELS = ["proxy", "fabricated", "infrastructure", "assertion", "other"]


def main():
    rows = []
    for out in ["out_c2conf", "out_c3gpt", "out_c3fixF1", "out_c3fixF2"]:
        for r in load(out):
            if r["evid"] == "X" and r["r2"] == "met": r["_set"] = out; rows.append(r)
    done = {json.loads(l)["key"] for l in open(OUT, encoding="utf-8")} if OUT.exists() else set()
    client = OpenAI(api_key=key(), max_retries=6); lock = threading.Lock()
    def work(r):
        k = r["_set"] + "/" + r["run_id"]
        if k in done: return
        sc = SCENARIOS[r["scenario"]]; r2 = sc["r2_vague"] if r["salience"] == "L" else sc["brief"]["constraints"][1]
        e = next(e for e in r["submission"]["requirements"] if any(x in (e.get("requirement", "") + " ").lower() for x in KW[r["scenario"]]))
        ev = (e.get("evidence", "") + (" | source: " + e["evidence_source"] if e.get("evidence_source") else ""))[:1500]
        p = PROMPT.format(r2=r2, docs=docs_text(r), ev=ev, just=(r["submission"].get("justification") or "")[:2500])
        resp = client.responses.create(model="gpt-5.5-2026-04-23", input=p, reasoning={"effort": "low"}, max_output_tokens=4000)
        t = resp.output_text or ""
        try: j = json.loads(re.search(r"\{.*\}", t, re.S).group(0))
        except Exception: j = {"labels": ["parse_error"]}
        with lock, open(OUT, "a", encoding="utf-8") as fh: fh.write(json.dumps({"key": k, **j}) + "\n")
    with cf.ThreadPoolExecutor(3) as ex: list(ex.map(work, rows))
    O = {json.loads(l)["key"]: json.loads(l) for l in open(HERE / "justification_types.jsonl", encoding="utf-8")}
    G = {json.loads(l)["key"]: json.loads(l) for l in open(OUT, encoding="utf-8")}
    ks = sorted(set(O) & set(G)); print(f"claims coded by both: {len(ks)}")
    for lab in LABELS:
        a = [int(lab in O[k].get("labels", [])) for k in ks]; b = [int(lab in G[k].get("labels", [])) for k in ks]
        po = sum(x == y for x, y in zip(a, b)) / len(ks); pa, pb = sum(a) / len(ks), sum(b) / len(ks)
        pe = pa * pb + (1 - pa) * (1 - pb); kap = (po - pe) / (1 - pe) if pe < 1 else 1.0
        print(f"{lab:15} Opus {pa:.2f}  GPT-5.5 {pb:.2f}  agreement {po:.2f}  kappa {kap:.2f}")


if __name__ == "__main__":
    main()
