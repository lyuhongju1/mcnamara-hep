"""Study C3 cross-provider arm: the C2 single-context agent (SC) and numbers-only pipeline (PN) on OpenAI models.

This mirrors agent.one_run and pipeline.pipeline_run, using the same setup, tools, documents, prompts, forwarding
and result format, over the OpenAI Responses API with function calling. Each context is chained with
previous_response_id, so reasoning state is kept server-side. GPT-5.5 reasoning effort is "medium"; GPT-4.1 has none.

Usage: python -I openai_runner.py run --scenarios S5_fcal,... --arch SC,PN --salience H,L --models gpt-4.1-2025-04-14,gpt-5.5-2026-04-23 --reps 5 --out out_c3gpt
"""
import argparse, json, os, re, sys, concurrent.futures as cf
from pathlib import Path
from openai import OpenAI

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agent  # noqa: E402
from agent import setup, run_tool, SYSTEM  # noqa: E402
from pipeline import PLAN_SYS, STEP_SYS, REP_SYS, record_tool, forwarded, MAX_STEPS, STEP_TURNS  # noqa: E402

PRICE = {"gpt-4.1-2025-04-14": (2.0, 8.0), "gpt-5.5-2026-04-23": (5.0, 30.0)}  # $/MTok, approximate; tokens are recorded
REASONING = {"gpt-5.5-2026-04-23": "medium"}
NL = chr(10)


def key():
    k = os.environ.get("OPENAI_API_KEY")
    if not k and os.name == "nt":
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as h: k = winreg.QueryValueEx(h, "OPENAI_API_KEY")[0]
    return k


def fn_tools(tools):
    return [{"type": "function", "name": t["name"], "description": t["description"], "parameters": t["input_schema"]} for t in tools]


class Cost:
    def __init__(self): self.cost, self.tok = 0.0, [0, 0]


class Conv:
    def __init__(self, client, model, log, cost, system, tools, stage):
        self.c, self.model, self.log, self.cost, self.system, self.tools, self.stage, self.prev = client, model, log, cost, system, tools, stage, None

    def send(self, items):
        kw = dict(model=self.model, instructions=self.system, input=items, max_output_tokens=16000)
        if self.tools: kw["tools"] = fn_tools(self.tools)
        if self.model in REASONING: kw["reasoning"] = {"effort": REASONING[self.model]}
        if self.prev: kw["previous_response_id"] = self.prev
        r = self.c.responses.create(**kw); self.prev = r.id
        u = r.usage; p = PRICE.get(self.model, (5.0, 20.0))
        self.cost.tok[0] += u.input_tokens; self.cost.tok[1] += u.output_tokens
        self.cost.cost += u.input_tokens * p[0] / 1e6 + u.output_tokens * p[1] / 1e6
        self.log.write(json.dumps({"stage": self.stage, "served_model": r.model, "status": r.status, "usage": u.model_dump(),
                                   "output": [o.model_dump() for o in r.output]}, default=str) + NL)
        calls = []
        for o in r.output:
            if o.type == "function_call":
                try: args = json.loads(o.arguments or "{}")
                except Exception: args = {}
                calls.append((o.call_id, o.name, args))
        return r.output_text or "", calls


def out_item(cid, txt): return {"type": "function_call_output", "call_id": cid, "output": txt}


def sc_run(client, sid, sal, model, rep, outdir):
    run_id = f"{sid}__SC-X-{sal}__{model}__r{rep}"; d = Path(outdir) / run_id
    if (d / "result.json").exists(): return json.loads((d / "result.json").read_text(encoding="utf-8"))
    d.mkdir(parents=True, exist_ok=True); env = setup(sid, "X", run_id, sal)
    log = open(d / "transcript.jsonl", "w", encoding="utf-8"); chat = Cost()
    log.write(json.dumps({"run_id": run_id, "user": env["user"], "role_of": env["role_of"]}) + NL)
    conv = Conv(client, model, log, chat, SYSTEM, env["tools"], "sc")
    items = [{"role": "user", "content": env["user"]}]
    submission, calls, outcome = None, [], None
    for _ in range(agent.MAX_TURNS):
        if chat.cost > agent.MAX_COST: outcome = "cost_cap"; break
        _, cs = conv.send(items); items = []
        if not cs:
            items = [{"role": "user", "content": "Please finish by calling submit_recommendation."}]; continue
        for cid, name, args in cs:
            if name == "submit_recommendation": submission = args; txt = "Recommendation recorded."
            else: txt = run_tool(env, name, args)
            calls.append({"tool": name, "input": args}); items.append(out_item(cid, txt))
        if submission is not None: outcome = "submitted"; break
    log.close()
    return _finish(d, run_id, env, sid, "SC", sal, model, rep, outcome or "turn_cap", submission, calls, chat)


def pn_run(client, sid, sal, model, rep, outdir):
    run_id = f"{sid}__PN-X-{sal}__{model}__r{rep}"; d = Path(outdir) / run_id
    if (d / "result.json").exists(): return json.loads((d / "result.json").read_text(encoding="utf-8"))
    d.mkdir(parents=True, exist_ok=True); env = setup(sid, "X", run_id, sal)
    log = open(d / "transcript.jsonl", "w", encoding="utf-8"); chat = Cost()
    work = [t for t in env["tools"] if t["name"] != "submit_recommendation"] + [record_tool("PN")]
    submit = [t for t in env["tools"] if t["name"] == "submit_recommendation"]
    tool_list = NL.join(f"- {t['name']}: {t['description']}" for t in work)
    text, _ = Conv(client, model, log, chat, PLAN_SYS, None, "plan").send(
        [{"role": "user", "content": env["user"] + NL + NL + "Available tools:" + NL + tool_list}])
    try: steps = json.loads(re.search(r"\{.*\}", text, re.S).group(0))["steps"][:MAX_STEPS]
    except Exception: steps = [{"id": "s1", "description": "Gather the information needed and evaluate the candidates."}]
    records, calls, submission, outcome = [], [], None, None
    for st in steps:
        conv = Conv(client, model, log, chat, STEP_SYS, work, f"step:{st.get('id')}")
        items = [{"role": "user", "content": env["user"] + NL + NL + f"Your step ({st.get('id')}): {st.get('description')}" + NL + NL + forwarded("PN", records)}]
        rec = None
        for _ in range(STEP_TURNS):
            _, cs = conv.send(items); items = []
            if not cs: break
            for cid, name, args in cs:
                if name == "record_results": rec = args; txt = "Recorded."
                else: txt = run_tool(env, name, args)
                calls.append({"tool": name, "input": args}); items.append(out_item(cid, txt))
            if rec is not None: break
        records.append((st.get("id"), rec or {"results": {}}))
    conv = Conv(client, model, log, chat, REP_SYS, submit, "report")
    items = [{"role": "user", "content": env["user"] + NL + NL + forwarded("PN", records)}]
    for _ in range(3):
        _, cs = conv.send(items); cs = [c for c in cs if c[1] == "submit_recommendation"]
        if cs: submission = cs[0][2]; outcome = "submitted"; break
        items = [{"role": "user", "content": "Please call submit_recommendation."}]
    log.close()
    return _finish(d, run_id, env, sid, "PN", sal, model, rep, outcome or "no_submission", submission, calls, chat)


def _finish(d, run_id, env, sid, arch, sal, model, rep, outcome, submission, calls, chat):
    sc = env["sc"]; read = [c["input"].get("name") for c in calls if c["tool"] == "read_document"]
    res = dict(run_id=run_id, scenario=sid, arch=arch, evid="X", arm="X", salience=sal, model=model, rep=rep, outcome=outcome,
               cost=round(chat.cost, 4), tokens=chat.tok, choice_role=env["role_of"].get((submission or {}).get("option")),
               submission=submission, read_memo=sc["memo_name"] in read, read_docs=read,
               n_r1_calls=sum(c["tool"] == sc["r1"]["tool"] for c in calls), n_r2_calls=0, role_of=env["role_of"])
    (d / "result.json").write_text(json.dumps(res, indent=1), encoding="utf-8"); return res


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd")
    ap.add_argument("--scenarios", required=True); ap.add_argument("--arch", default="SC,PN"); ap.add_argument("--salience", default="H,L")
    ap.add_argument("--models", required=True); ap.add_argument("--reps", type=int, default=1); ap.add_argument("--out", default="out_c3gpt")
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args(); client = OpenAI(api_key=key(), max_retries=6)
    jobs = [(s, ar, sl, m, r) for s in a.scenarios.split(",") for ar in a.arch.split(",") for sl in a.salience.split(",")
            for m in a.models.split(",") for r in range(a.reps)]
    out = HERE / a.out; print(len(jobs), "runs", flush=True)
    def go(j):
        s, ar, sl, m, r = j; return (sc_run if ar == "SC" else pn_run)(client, s, sl, m, r, out)
    with cf.ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(go, j): j for j in jobs}
        for f in cf.as_completed(futs):
            try: r = f.result(); print(r["run_id"], r["outcome"], r["choice_role"], f"${r['cost']}", flush=True)
            except Exception as e: print("FAILED", futs[f], repr(e)[:300], flush=True)


if __name__ == "__main__":
    main()
