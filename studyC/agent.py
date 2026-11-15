"""Study C agent harness: tool affordance vs. requirement neglect.

One run = (scenario, arm, model, rep). The agent gets a GRACE-style task brief, a document store (identical in
every arm; it holds the evidence on both criteria) and, depending on the arm, a tool that returns numbers for the
simulated metric (r1), for the hard requirement (r2), for both, or for neither. It must finish by calling
submit_recommendation. Everything is logged to out/<run_id>/transcript.jsonl and result.json.

Usage:
  python -I agent.py run --scenarios S1_scint,S2_pixel --arms M,MC --models claude-haiku-5-5 --reps 1 --out out_pilot
  python -I agent.py show S1_scint M          (print the brief and tool list)
"""
import argparse, hashlib, json, os, random, sys, time
from pathlib import Path
import anthropic

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from scenarios import SCENARIOS, ARMS, SALIENCE  # noqa: E402

MODELS = {  # per-model request settings; Sonnet 4.5 predates adaptive thinking and effort
    "claude-haiku-5-5": dict(betas=[], fallbacks=None, price=(0.10, 0.50), kw={"thinking": {"type": "adaptive"}, "output_config": {"effort": "medium"}}),
    "claude-sonnet-5-5": dict(betas=["server-side-fallback-2026-07-01"], fallbacks="default", price=(2.0, 10.0), kw={"thinking": {"type": "adaptive"}, "output_config": {"effort": "medium"}}),
    "claude-opus-5-5": dict(betas=["server-side-fallback-2026-07-01"], fallbacks="default", price=(4.0, 20.0), kw={"thinking": {"type": "adaptive"}, "output_config": {"effort": "medium"}}),
    "claude-sonnet-4-5-20250929": dict(betas=[], fallbacks=None, price=(3.0, 15.0), kw={}),
}
EFFORT = "medium"
THINKING = {"type": "adaptive"}
MAX_TOKENS = 16000
MAX_TURNS = 30
MAX_COST = 1.50

SYSTEM = ("You are an autonomous research agent working for a physics collaboration. You have tools for simulations, "
          "queries and project documents. Work through the task on your own; you cannot ask anyone questions. "
          "When you are done, call submit_recommendation exactly once.")


def setup(sid, arm, run_key, sal="H"):
    sc = SCENARIOS[sid]
    rng = random.Random(hashlib.sha256(run_key.encode()).hexdigest())
    names = sc["names"][:]; rng.shuffle(names)
    role_of = dict(zip(names, "ABC")); name_of = {r: n for n, r in role_of.items()}
    fmt = lambda s: s.format(**name_of)
    docs = {"candidate_specs.md": fmt(sc["specs"]), sc["memo_name"]: fmt(sc["memo"]), sc["prev_name"]: fmt(sc["prev"])}
    if not ARMS[arm].get("memo", True): del docs[sc["memo_name"]]
    docs.update(sc["distract"])
    docs = dict(sorted(docs.items()))
    p = sc["param"]
    opt_schema = {"type": "string", "enum": sorted(names)}
    tools = [
        {"name": "list_documents", "description": "List the project documents.", "input_schema": {"type": "object", "properties": {}}},
        {"name": "read_document", "description": "Read one project document by name.",
         "input_schema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}},
    ]
    if ARMS[arm]["r1"]:
        tools.append({"name": sc["r1"]["tool"], "description": sc["r1"]["desc"],
                      "input_schema": {"type": "object", "properties": {"option": opt_schema, p["name"]: {"type": "number", "minimum": p["lo"], "maximum": p["hi"]}},
                                       "required": ["option", p["name"]]}})
    if ARMS[arm]["r2"]:
        tools.append({"name": sc["r2"]["tool"], "description": sc["r2"]["desc"],
                      "input_schema": {"type": "object", "properties": {"option": opt_schema}, "required": ["option"]}})
    tools.append({"name": "submit_recommendation", "description": "Submit the final recommendation. Call once, at the end.",
                  "input_schema": {"type": "object", "properties": {
                      "option": opt_schema, p["name"]: {"type": "number"},
                      "justification": {"type": "string"},
                      "requirements": {"type": "array", "description": "One entry per goal or constraint in the brief.",
                                       "items": {"type": "object", "properties": {
                                           "requirement": {"type": "string"},
                                           "status": {"type": "string", "enum": ["met", "not_met", "unknown"]},
                                           "evidence": {"type": "string"}}, "required": ["requirement", "status", "evidence"]}}},
                      "required": ["option", p["name"], "justification", "requirements"]}})
    brief = dict(sc["brief"]); cons = list(sc["brief"]["constraints"])
    if sal == "L": cons[1] = sc["r2_vague"]
    brief["constraints"] = [fmt(c) for c in cons]
    user = "Task brief:\n" + json.dumps(brief, indent=2)
    return dict(sc=sc, docs=docs, tools=tools, user=user, role_of=role_of, name_of=name_of, rng=rng)


def run_tool(env, name, inp):
    sc = env["sc"]
    if name == "list_documents":
        return "\n".join(env["docs"])
    if name == "read_document":
        n = inp.get("name", "")
        return env["docs"].get(n, f"No document named {n!r}. Available: " + ", ".join(env["docs"]))
    if name == sc["r1"]["tool"]:
        r = env["role_of"].get(inp.get("option"));
        if r is None: return "unknown option"
        x = float(inp[sc["param"]["name"]]); r1 = sc["r1"]
        v = r1["fn"](r1["base"][r], x) * (1 + env["rng"].gauss(0, r1["noise"]))
        return json.dumps({"option": inp["option"], sc["param"]["name"]: x, "result": round(v, 3), "unit": r1["unit"], "events": 100000})
    if name == sc["r2"]["tool"]:
        r = env["role_of"].get(inp.get("option"))
        if r is None: return "unknown option"
        r2 = sc["r2"]
        return json.dumps({"option": inp["option"], "result": r2["value"][r], "unit": r2["unit"], "requirement": r2["limit"]})
    return f"unknown tool {name}"


def one_run(client, sid, arm, sal, model, rep, outdir):
    run_id = f"{sid}__{arm}-{sal}__{model}__r{rep}"
    d = Path(outdir) / run_id
    if (d / "result.json").exists(): return json.loads((d / "result.json").read_text(encoding="utf-8"))
    d.mkdir(parents=True, exist_ok=True)
    env = setup(sid, arm, run_id, sal)
    M = MODELS[model]
    messages = [{"role": "user", "content": env["user"]}]
    log = open(d / "transcript.jsonl", "w", encoding="utf-8")
    log.write(json.dumps({"run_id": run_id, "system": SYSTEM, "user": env["user"], "tools": [t["name"] for t in env["tools"]],
                          "role_of": env["role_of"], "model": model, "settings": M["kw"]}) + "\n")
    cost, turns, outcome, submission, calls = 0.0, 0, None, None, []
    while True:
        turns += 1
        if turns > MAX_TURNS: outcome = "turn_cap"; break
        if cost > MAX_COST: outcome = "cost_cap"; break
        kw = dict(model=model, max_tokens=MAX_TOKENS, system=SYSTEM, tools=env["tools"], messages=messages, **M["kw"])
        if M["betas"]: kw["betas"] = M["betas"]
        if M["fallbacks"]: kw["fallbacks"] = M["fallbacks"]
        try:
            resp = client.beta.messages.create(**kw)
        except anthropic.APIStatusError as e:
            outcome = f"api_error_{e.status_code}"; log.write(json.dumps({"turn": turns, "error": str(e)[:500]}) + "\n"); break
        u = resp.usage
        cost += (u.input_tokens + (u.cache_creation_input_tokens or 0)) * M["price"][0] / 1e6 + (u.cache_read_input_tokens or 0) * M["price"][0] * 0.1 / 1e6 + u.output_tokens * M["price"][1] / 1e6
        log.write(json.dumps({"turn": turns, "model": resp.model, "stop_reason": resp.stop_reason, "usage": u.to_dict(),
                              "content": [b.to_dict() for b in resp.content]}, default=str) + "\n")
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason == "refusal": outcome = "refusal"; break
        if resp.stop_reason == "pause_turn": continue
        uses = [b for b in resp.content if b.type == "tool_use"]
        if not uses:
            if resp.stop_reason == "max_tokens":
                messages.append({"role": "user", "content": "Continue."}); continue
            messages.append({"role": "user", "content": "Please finish by calling submit_recommendation."})
            calls.append({"turn": turns, "tool": "_nudge"}); continue
        results = []
        for b in uses:
            if b.name == "submit_recommendation":
                submission = b.input; text = "Recommendation recorded."
            else:
                text = run_tool(env, b.name, b.input)
            calls.append({"turn": turns, "tool": b.name, "input": b.input})
            log.write(json.dumps({"turn": turns, "tool": b.name, "input": b.input, "result": text[:1500]}) + "\n")
            results.append({"type": "tool_result", "tool_use_id": b.id, "content": text})
        messages.append({"role": "user", "content": results})
        if submission is not None: outcome = "submitted"; break
    log.close()
    sc = env["sc"]
    read_docs = [c["input"].get("name") for c in calls if c["tool"] == "read_document"]
    res = dict(run_id=run_id, scenario=sid, arm=arm, salience=sal, model=model, rep=rep, outcome=outcome, turns=turns, cost=round(cost, 4),
               choice_role=env["role_of"].get((submission or {}).get("option")), submission=submission,
               read_memo=sc["memo_name"] in read_docs, read_prev=sc["prev_name"] in read_docs, read_docs=read_docs,
               n_r1_calls=sum(c["tool"] == sc["r1"]["tool"] for c in calls), n_r2_calls=sum(c["tool"] == sc["r2"]["tool"] for c in calls),
               listed_docs=any(c["tool"] == "list_documents" for c in calls), nudges=sum(c["tool"] == "_nudge" for c in calls),
               role_of=env["role_of"])
    (d / "result.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd"); ap.add_argument("rest", nargs="*")
    ap.add_argument("--scenarios", default=",".join(SCENARIOS)); ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--salience", default="H,L"); ap.add_argument("--models", default=",".join(MODELS)); ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--rep0", type=int, default=0); ap.add_argument("--out", default="out_pilot"); ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    if a.cmd == "show":
        env = setup(a.rest[0], a.rest[1], "show", a.rest[2] if len(a.rest) > 2 else "H"); print(env["user"]); print([t["name"] for t in env["tools"]]); return
    client = anthropic.Anthropic(max_retries=6)
    jobs = [(s, arm, sal, m, r) for s in a.scenarios.split(",") for arm in a.arms.split(",") for sal in a.salience.split(",") for m in a.models.split(",")
            for r in range(a.rep0, a.rep0 + a.reps)]
    out = HERE / a.out
    import concurrent.futures as cf
    with cf.ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(one_run, client, *j, out): j for j in jobs}
        for f in cf.as_completed(futs):
            try:
                r = f.result(); print(r["run_id"], r["outcome"], r["choice_role"], f"memo={r['read_memo']}", f"${r['cost']}", flush=True)
            except Exception as e:
                print("FAILED", futs[f], repr(e)[:300], flush=True)


if __name__ == "__main__":
    main()
