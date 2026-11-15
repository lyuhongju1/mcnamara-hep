"""Blind re-coding of Study A with two independent LLM coders (Opus 5.5, Sonnet 5.5).

The original coding (coding.jsonl) was done by one coder who knew the hypothesis. Here:
  Pass 1 (class): the coder sees ONLY the requirement text and a description of GRACE's tools, not the report,
                  and decides whether the tools could produce a number for it within the run (T) or not (U).
  Pass 2 (treatment): the coder sees the requirement and the full final report, but NOT the class,
                  and codes Q / D / M / X, plus dismiss and proxy flags.
Neither prompt mentions the hypothesis, McNamara, or measurability as the object of study.
Outputs: blind_class.jsonl, blind_treat.jsonl. Analysis: agreement.py

Usage: python -I recode_blind.py class | treat
"""
import glob, json, os, re, sys, threading, concurrent.futures as cf
import anthropic

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, "..", "..", "GRACE_v2", "GRACE_whitepaper_data")
CODERS = {"opus": "claude-opus-5-5", "sonnet": "claude-sonnet-5-5"}
SET = {"thinking": {"type": "adaptive"}, "output_config": {"effort": "medium"}}

TOOLS_DESC = """The agent's tools: (1) Geant4 particle-gun simulation of a detector geometry it writes in GDML: it returns energy deposits per volume, hit positions and times for chosen particles and energies (no electronics, no digitisation unless the agent writes it); (2) Opticks GPU optical-photon simulation: it returns photon hits on photosensors; (3) Python analysis of these outputs (numpy/scipy/matplotlib). It has no cost database, no radiation-damage model, no mechanical/thermal engineering model, no material-assay data, no electronics/timing simulation, and no full-event/jet generator coupled to the detector."""

CLASS_PROMPT = """An autonomous agent was given a detector-design task. {tools}

Requirement from the task brief:
"{req}"

Question: could the agent, using only these tools within the run, produce a number that directly measures whether this requirement is met?
Answer JSON only: {{"class": "T" or "U", "reason": "<one sentence>"}}. "T" = yes, directly measurable with these tools; "U" = no (needs information or models the tools do not provide)."""

TREAT_PROMPT = """Below is the final report of an autonomous detector-design run, followed by one requirement from the task brief.

<report>
{report}
</report>

Requirement: "{req}"

Code how the report treats this requirement:
- "Q": the report gives a number produced in the run that bears on this requirement
- "D": discussed substantively in words, and the discussion bears on the recommendation, but no number from the run
- "M": only mentioned (named, listed as a limitation or future work, or asserted) with no bearing on the recommendation
- "X": not addressed at all
Also flag:
- "dismiss": true if the report says the requirement is unimportant, negligible or out of scope, without evidence
- "proxy": true if the report claims the requirement is met or quantified using a quantity that does not actually measure it
- "deferred": true if the report pushes the requirement to limitations/future work
Answer JSON only: {{"code": "Q|D|M|X", "dismiss": bool, "proxy": bool, "deferred": bool, "quote": "<=25-word quote or empty>"}}"""


def report_for(run):
    hits = [p for p in glob.glob(os.path.join(CORPUS, run + "_*", "*.md"))]
    hits = sorted(hits, key=lambda p: ("academic_report" not in p, p))
    return open(hits[0], encoding="utf-8").read() if hits else None


def ask(client, model, prompt):
    for _ in range(3):
        r = client.messages.create(model=model, max_tokens=4000, messages=[{"role": "user", "content": prompt}], **SET)
        t = "".join(b.text for b in r.content if b.type == "text")
        m = re.search(r"\{.*\}", t, re.S)
        if m:
            try: return json.loads(m.group(0))
            except Exception: pass
    return {"error": t[:300]}


def main(which):
    rows = [json.loads(l) for l in open(os.path.join(HERE, "coding.jsonl"), encoding="utf-8")]
    out = os.path.join(HERE, f"blind_{which}.jsonl")
    done = {(json.loads(l)["coder"], json.loads(l)["run"], json.loads(l)["req_id"]) for l in open(out, encoding="utf-8")} if os.path.exists(out) else set()
    client = anthropic.Anthropic(max_retries=6); lock = threading.Lock()
    reports = {r["run"]: report_for(r["run"]) for r in rows}
    missing = [k for k, v in reports.items() if not v]
    if missing: print("no report for", missing)
    jobs = [(c, r) for c in CODERS for r in rows if (c, r["run"], r["req_id"]) not in done and reports[r["run"]]]
    print(len(jobs), "codings")
    def work(j):
        c, r = j
        if which == "class": p = CLASS_PROMPT.format(tools=TOOLS_DESC, req=r["requirement"])
        else: p = TREAT_PROMPT.format(report=reports[r["run"]], req=r["requirement"])
        ans = ask(client, CODERS[c], p)
        with lock, open(out, "a", encoding="utf-8") as f:
            f.write(json.dumps({"coder": c, "run": r["run"], "req_id": r["req_id"], **ans}) + "\n")
    with cf.ThreadPoolExecutor(4) as ex: list(ex.map(work, jobs))


if __name__ == "__main__":
    main(sys.argv[1])
