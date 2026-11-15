"""Study C2: does a numbers-only interface between pipeline stages drop unquantified requirements?

Architectures (factor ARCH):
  SC  single-context agent (agent.py one_run)
  PN  GRACE-style pipeline: planner -> step executors (fresh context each) -> reporter.
      Steps pass forward ONLY numeric key=value results (record_results accepts numbers only),
      as GRACE v1 passed prior results mostly as k=v scratchpad entries and formatted numbers.
  PT  same pipeline, but steps may also pass free-text notes, and each step's closing text is forwarded.
Evidence (factor EVID): "M" = r2 memo present in documents, r1 tool only; "X" = r2 evidence nowhere, r1 tool only.
Salience (factor SAL): H explicit numeric hard constraint in the brief, L vague phrase.

The reporter is the only stage that can call submit_recommendation; it sees the brief and the forwarded results.

Usage: python -I pipeline.py run --arch PN,PT,SC --evid M,X --salience H,L --models m1,m2 --reps 1 --out out_c2pilot
"""
import argparse, json, re, sys, concurrent.futures as cf
from pathlib import Path
import anthropic

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agent  # noqa: E402
from agent import MODELS, setup, run_tool  # noqa: E402

MAX_STEPS, STEP_TURNS, MAX_COST = 6, 10, 2.50

PLAN_SYS = ("You are the planning module of an autonomous research agent for a physics collaboration. "
            "Given a task brief and the list of available tools, write a plan of 3 to 6 sequential steps that an executor "
            "will carry out one at a time. A separate reporting module will write the final recommendation from the step results. "
            'Output ONLY JSON: {"steps": [{"id": "s1", "description": "..."}, ...]}')
STEP_SYS = ("You are the execution module of an autonomous research agent. Carry out ONLY the step you are given, using the tools. "
            "When the step is done, call record_results once to pass this step's results to later steps.")
REP_SYS = ("You are the reporting module of an autonomous research agent. From the task brief and the results recorded by the "
           "executed steps, make the final recommendation by calling submit_recommendation exactly once.")


def record_tool(arch):
    props = {"results": {"type": "object", "additionalProperties": {"type": "number"},
                         "description": "Numeric results of this step as key-value pairs (e.g. resolution_OptionX_5cm: 3.1)."}}
    desc = "Record this step's results for later steps. Only numeric values can be recorded."
    if arch == "PT":
        props["notes"] = {"type": "string", "description": "Free-text notes for later steps (findings, caveats, open questions)."}
        desc = "Record this step's results for later steps: numeric key-value pairs and free-text notes."
    return {"name": "record_results", "description": desc, "input_schema": {"type": "object", "properties": props, "required": ["results"]}}


class Run:
    def __init__(self, client, model, log):
        self.client, self.model, self.M, self.log, self.cost = client, model, MODELS[model], log, 0.0
        self.calls = []

    def call(self, system, messages, tools=None):
        kw = dict(model=self.model, max_tokens=16000, system=system, messages=messages, **self.M["kw"])
        if tools: kw["tools"] = tools
        if self.M["betas"]: kw["betas"] = self.M["betas"]
        if self.M["fallbacks"]: kw["fallbacks"] = self.M["fallbacks"]
        r = self.client.beta.messages.create(**kw)
        u = r.usage; p = self.M["price"]
        self.cost += (u.input_tokens + (u.cache_creation_input_tokens or 0)) * p[0] / 1e6 + (u.cache_read_input_tokens or 0) * p[0] * 0.1 / 1e6 + u.output_tokens * p[1] / 1e6
        self.log.write(json.dumps({"stage": self._stage, "served_model": r.model, "stop_reason": r.stop_reason, "usage": u.to_dict(),
                                   "content": [b.to_dict() for b in r.content]}, default=str) + "\n")
        return r


def text_of(r): return "".join(b.text for b in r.content if b.type == "text")


def forwarded(arch, records):
    if not records: return "No results have been recorded yet."
    lines = []
    for sid_, rec in records:
        for k, v in (rec.get("results") or {}).items():
            if isinstance(v, (int, float)): lines.append(f"{k} = {v:.6g}")
        if arch == "PT":
            if rec.get("notes"): lines.append(f"[{sid_} notes] {rec['notes']}")
            if rec.get("closing"): lines.append(f"[{sid_} summary] {rec['closing']}")
    return "Results recorded by previous steps:\n" + ("\n".join(lines) if lines else "(none)")


def pipeline_run(client, sid, arch, evid, sal, model, rep, outdir):
    run_id = f"{sid}__{arch}-{evid}-{sal}__{model}__r{rep}"
    d = Path(outdir) / run_id
    if (d / "result.json").exists(): return json.loads((d / "result.json").read_text(encoding="utf-8"))
    if arch == "SC":
        res = agent.one_run(client, sid, evid, sal, model, rep, Path(outdir) / "_sc")
        res = dict(res, run_id=run_id, arch="SC", evid=evid); d.mkdir(parents=True, exist_ok=True)
        (d / "result.json").write_text(json.dumps(res, indent=1), encoding="utf-8"); return res
    d.mkdir(parents=True, exist_ok=True)
    env = setup(sid, evid, run_id, sal)
    log = open(d / "transcript.jsonl", "w", encoding="utf-8")
    R = Run(client, model, log)
    work_tools = [t for t in env["tools"] if t["name"] != "submit_recommendation"] + [record_tool(arch)]
    submit = [t for t in env["tools"] if t["name"] == "submit_recommendation"]
    tool_list = "\n".join(f"- {t['name']}: {t['description']}" for t in work_tools)
    log.write(json.dumps({"run_id": run_id, "arch": arch, "user": env["user"], "role_of": env["role_of"], "settings": R.M["kw"]}) + "\n")
    outcome, submission, records, step_calls = None, None, [], []
    # 1. plan
    R._stage = "plan"
    plan_r = R.call(PLAN_SYS, [{"role": "user", "content": env["user"] + "\n\nAvailable tools:\n" + tool_list}])
    try:
        steps = json.loads(re.search(r"\{.*\}", text_of(plan_r), re.S).group(0))["steps"][:MAX_STEPS]
    except Exception:
        steps = [{"id": "s1", "description": "Gather the information needed and evaluate the candidates."}]
    # 2. execute steps
    for st in steps:
        R._stage = f"step:{st.get('id')}"
        msgs = [{"role": "user", "content": env["user"] + f"\n\nYour step ({st.get('id')}): {st.get('description')}\n\n" + forwarded(arch, records)}]
        rec, closing = None, ""
        for _ in range(STEP_TURNS):
            if R.cost > MAX_COST: outcome = "cost_cap"; break
            r = R.call(STEP_SYS, msgs, work_tools)
            msgs.append({"role": "assistant", "content": r.content})
            uses = [b for b in r.content if b.type == "tool_use"]
            if not uses:
                closing = text_of(r).strip(); break
            res_blocks = []
            for b in uses:
                if b.name == "record_results":
                    rec = dict(b.input); txt = "Recorded."
                else:
                    txt = run_tool(env, b.name, b.input)
                step_calls.append({"stage": R._stage, "tool": b.name, "input": b.input})
                log.write(json.dumps({"stage": R._stage, "tool": b.name, "input": b.input, "result": txt[:1500]}) + "\n")
                res_blocks.append({"type": "tool_result", "tool_use_id": b.id, "content": txt})
            msgs.append({"role": "user", "content": res_blocks})
            if rec is not None:
                r2 = R.call(STEP_SYS, msgs, work_tools); msgs.append({"role": "assistant", "content": r2.content})
                closing = text_of(r2).strip(); break
        if outcome: break
        rec = rec or {"results": {}}
        rec["closing"] = closing[:3000]
        records.append((st.get("id"), rec))
    # 3. report
    if not outcome:
        R._stage = "report"
        msgs = [{"role": "user", "content": env["user"] + "\n\n" + forwarded(arch, records)}]
        for _ in range(3):
            r = R.call(REP_SYS, msgs, submit)
            msgs.append({"role": "assistant", "content": r.content})
            uses = [b for b in r.content if b.type == "tool_use" and b.name == "submit_recommendation"]
            if uses:
                submission = uses[0].input; outcome = "submitted"
                msgs.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": uses[0].id, "content": "Recorded."}]})
                break
            msgs.append({"role": "user", "content": "Please call submit_recommendation."})
        outcome = outcome or "no_submission"
    log.close()
    sc = env["sc"]
    read_docs = [c["input"].get("name") for c in step_calls if c["tool"] == "read_document"]
    res = dict(run_id=run_id, scenario=sid, arch=arch, evid=evid, arm=evid, salience=sal, model=model, rep=rep, outcome=outcome,
               cost=round(R.cost, 4), n_steps=len(steps), choice_role=env["role_of"].get((submission or {}).get("option")),
               submission=submission, read_memo=sc["memo_name"] in read_docs, read_docs=read_docs,
               n_r1_calls=sum(c["tool"] == sc["r1"]["tool"] for c in step_calls), n_r2_calls=0,
               forwarded_to_reporter=forwarded(arch, records), role_of=env["role_of"], turns=None, listed_docs=None, nudges=None)
    (d / "result.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--scenarios", default=None); ap.add_argument("--arch", default="PN,PT,SC"); ap.add_argument("--evid", default="M,X")
    ap.add_argument("--salience", default="H,L"); ap.add_argument("--models", default="claude-haiku-5-5")
    ap.add_argument("--reps", type=int, default=1); ap.add_argument("--rep0", type=int, default=0)
    ap.add_argument("--out", default="out_c2pilot"); ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    from scenarios import SCENARIOS
    scen = a.scenarios.split(",") if a.scenarios else list(SCENARIOS)
    client = anthropic.Anthropic(max_retries=6)
    jobs = [(s, ar, e, sl, m, r) for s in scen for ar in a.arch.split(",") for e in a.evid.split(",") for sl in a.salience.split(",")
            for m in a.models.split(",") for r in range(a.rep0, a.rep0 + a.reps)]
    out = HERE / a.out
    print(f"{len(jobs)} runs", flush=True)
    with cf.ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(pipeline_run, client, *j, out): j for j in jobs}
        for f in cf.as_completed(futs):
            try:
                r = f.result(); print(r["run_id"], r["outcome"], r["choice_role"], f"memo={r['read_memo']}", f"${r['cost']}", flush=True)
            except Exception as e:
                print("FAILED", futs[f], repr(e)[:300], flush=True)


if __name__ == "__main__":
    main()
