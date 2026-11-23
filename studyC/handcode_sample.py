"""Draw a random sample of unsupported 'met' claims for hand validation of the Opus justification coding.
Writes handcode_sheet.csv (for the human coder; Opus labels NOT included) and handcode_key.json (Opus labels).
After the human fills in the five 0/1 columns, run: python -I handcode_sample.py score
"""
import csv, json, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze_c2 import load, KW
from scenarios import SCENARIOS
LABELS = ["proxy", "fabricated", "infrastructure", "assertion", "other"]
SHEET, KEY = HERE / "handcode_sheet.csv", HERE / "handcode_key.json"


def draw(n=45, seed=20261123):
    J = {json.loads(l)["key"]: json.loads(l) for l in open(HERE / "justification_types.jsonl", encoding="utf-8")}
    rows = {}
    for out in ["out_c2conf", "out_c3gpt", "out_c3fixF1", "out_c3fixF2"]:
        for r in load(out):
            k = out + "/" + r["run_id"]
            if k in J: rows[k] = r
    keys = sorted(rows); random.Random(seed).shuffle(keys); keys = keys[:n]
    with open(SHEET, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["item", "requirement_r2", "documents_that_existed", "agent_evidence_for_r2", "agent_justification"] + LABELS)
        for i, k in enumerate(keys, 1):
            r = rows[k]; sc = SCENARIOS[r["scenario"]]
            r2 = sc["r2_vague"] if r["salience"] == "L" else sc["brief"]["constraints"][1]
            e = next(e for e in r["submission"]["requirements"] if any(x in (e.get("requirement", "") + " ").lower() for x in KW[r["scenario"]]))
            ev = e.get("evidence", "") + (" | source " + e["evidence_source"] if e.get("evidence_source") else "")
            docs = "candidate_specs.md, " + sc["prev_name"] + ", " + ", ".join(sc["distract"]) + " (none contains any r2 information)"
            w.writerow([i, r2, docs, ev, (r["submission"].get("justification") or "")[:1500]] + [""] * 5)
    json.dump({str(i): {"key": k, "opus": J[k].get("labels", [])} for i, k in enumerate(keys, 1)}, open(KEY, "w", encoding="utf-8"), indent=1)
    print(f"wrote {SHEET.name} ({n} items) and {KEY.name}")


def score():
    key = json.load(open(KEY, encoding="utf-8"))
    rows = list(csv.DictReader(open(SHEET, encoding="utf-8")))
    for lab in LABELS:
        h = [int(r[lab] or 0) for r in rows]; o = [int(lab in key[r["item"]]["opus"]) for r in rows]
        agree = sum(a == b for a, b in zip(h, o)) / len(h)
        po, pa, pb = agree, sum(h) / len(h), sum(o) / len(o); pe = pa * pb + (1 - pa) * (1 - pb)
        k = (po - pe) / (1 - pe) if pe < 1 else 1.0
        print(f"{lab:15} human {sum(h):2}/{len(h)}  opus {sum(o):2}/{len(o)}  agreement {agree:.2f}  kappa {k:.2f}")


if __name__ == "__main__":
    score() if sys.argv[1:] == ["score"] else draw()
