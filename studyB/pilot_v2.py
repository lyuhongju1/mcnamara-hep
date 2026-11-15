"""Study B v2: form-of-information test with matched pass/fail information, plus evidence-omission forms.

Changes from v1 (see PILOT_RESULTS.md):
- Both requirements are graded with an explicit minimum ("at most X required; lower preferred"), and in every
  form both options are stated to meet both minimums. Number and prose versions therefore carry the same
  pass/fail information; only the size of the difference is exact (numbers) or verbal ("substantially").
- Two options only (v1's 3-option designs were at ceiling).
- Omission forms N0 / P0: the requirement-2 evidence block is absent; only the metric evidence is given.
  This is the decision-level analogue of "what is not measured is not considered".
Forms: NN NP PN PP N0 P0 (metric form, constraint form; 0 = no constraint evidence).

Usage: python -I pilot_v2.py run [--reps 5] [--models a,b] | judge | analyze | show SCEN FORM
"""
import json, os, random, re, sys, hashlib, threading, concurrent.futures as cf
from collections import defaultdict
import anthropic

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "responses_v2.jsonl")
JUDGE_OUT = os.path.join(HERE, "judge_v2.jsonl")
MODELS = {
    "claude-haiku-5-5": {"thinking": {"type": "disabled"}},
    "claude-sonnet-5-5": {"thinking": {"type": "between_tools"}},
    "claude-opus-5-5": {"thinking": {"type": "adaptive"}, "output_config": {"effort": "low"}},
}
FORMS = ["NN", "NP", "PN", "PP", "N0", "P0"]

S = {
 "S1_scint": dict(
  who="a low-background gamma-ray screening facility that assays materials for a dark-matter experiment",
  task="choose the scintillator for a new gamma spectrometer", opts="two candidate inorganic scintillator crystals",
  r1="Energy resolution at 662 keV: at most 8% FWHM is required; better is preferred.",
  r2="Intrinsic background of the crystal (its own radioactivity), 100-3000 keV: at most 1.0 counts/kg/day is required; lower is preferred.",
  m_src="the Geant4 + optical simulation study", c_src="the radiopurity assay of sample crystals",
  m_num="Energy resolution at 662 keV (FWHM): {A} 3.5%, {C} 6.0%.",
  m_pro="Both meet the resolution requirement. {A}'s energy resolution is substantially better than {C}'s.",
  c_num="Intrinsic background, 100-3000 keV: {A} 0.6, {C} 0.2 counts/kg/day.",
  c_pro="Both meet the background requirement. {A}'s intrinsic background is substantially higher than {C}'s."),
 "S2_pixel": dict(
  who="an LHC experiment preparing its high-luminosity inner tracker",
  task="choose the sensor technology for the innermost pixel layer", opts="two candidate pixel sensor technologies",
  r1="Single-hit spatial resolution: at most 15 um is required; better is preferred.",
  r2="Hit efficiency after the end-of-life fluence of 2e16 neq/cm^2: at least 93% is required; higher is preferred.",
  m_src="the Geant4 + charge-transport simulation study", c_src="the irradiation and test-beam campaign",
  m_num="Single-hit resolution (unirradiated): {A} 7 um, {C} 11 um.",
  m_pro="Both meet the resolution requirement. {A}'s single-hit resolution is substantially better than {C}'s.",
  c_num="Hit efficiency after 2e16 neq/cm^2: {A} 95.0%, {C} 98.5%.",
  c_pro="Both meet the efficiency requirement. After end-of-life fluence, {A}'s hit efficiency is substantially lower than {C}'s."),
 "S3_lar": dict(
  who="a liquid-argon neutrino experiment",
  task="choose the photon-detection module design for the far detector, where modules are inaccessible after the cryostat is filled",
  opts="two candidate photon-detection module designs",
  r1="Light collection: at least 15 photoelectrons per MeV is required; more is preferred.",
  r2="Reliability through cooldowns (fraction of modules failing after 20 thermal cycles, 300 K to 87 K): at most 10% is required; lower is preferred.",
  m_src="the Geant4 optical-photon simulation study", c_src="the thermal-cycling tests",
  m_num="Light collection: {A} 32 PE/MeV, {C} 22 PE/MeV.",
  m_pro="Both meet the light-collection requirement. {A} collects substantially more light than {C}.",
  c_num="Fraction of modules failed after 20 cycles: {A} 6%, {C} 2%.",
  c_pro="Both meet the reliability requirement. {A}'s modules failed substantially more often than {C}'s."),
 "S4_selection": dict(
  who="an LHC analysis team searching for a rare process",
  task="choose the event selection for the search", opts="two candidate event selections",
  r1="Expected signal significance (statistical uncertainty only): at least 3.0 sigma is required; higher is preferred.",
  r2="Data/MC agreement for the variables the selection uses, measured as the yield disagreement in a signal-free validation region: at most 20% is required; smaller is preferred.",
  m_src="the Monte Carlo sensitivity study", c_src="the data/MC comparison in the validation region",
  m_num="Expected significance: {A} 3.9 sigma, {C} 3.1 sigma.",
  m_pro="Both meet the significance requirement. {A} gives substantially higher expected significance than {C}.",
  c_num="Data/MC yield disagreement in the validation region: {A} 15%, {C} 5%.",
  c_pro="Both meet the agreement requirement. {A}'s data/MC disagreement is substantially larger than {C}'s."),
}


def build(sid, form, letters):
    s = S[sid]; L = {"A": letters[0], "C": letters[1]}
    pair = sorted(letters)
    parts = [f"You are advising {s['who']}. The task is to {s['task']}.", "",
             "Requirements:", f"1. {s['r1']}", f"2. {s['r2']}", "The collaboration considers the two requirements equally important.", "",
             f"There are {s['opts']}, labelled {pair[0]} and {pair[1]}.", "",
             f"From {s['m_src']}:", (s["m_num"] if form[0] == "N" else s["m_pro"]).format(**L), ""]
    if form[1] != "0":
        parts += [f"From {s['c_src']}:", (s["c_num"] if form[1] == "N" else s["c_pro"]).format(**L), ""]
    parts.append("Recommend one option. Give your reasoning in at most 150 words, then end with a final line of the form `DECISION: <letter>`.")
    return "\n".join(parts)


def run(reps, models):
    client = anthropic.Anthropic(max_retries=6)
    done = {json.loads(l)["key"] for l in open(OUT, encoding="utf-8")} if os.path.exists(OUT) else set()
    jobs = []
    for sid in S:
        for form in FORMS:
            for model in models:
                for rep in range(reps):
                    key = f"{sid}|{form}|{model}|{rep}"
                    if key in done: continue
                    letters = random.Random(hashlib.sha256(key.encode()).hexdigest()).sample("PQRSTUVW", 2)
                    jobs.append((key, sid, form, model, rep, letters))
    print(f"{len(jobs)} calls", flush=True)
    lock = threading.Lock()
    def work(j):
        key, sid, form, model, rep, letters = j
        prompt = build(sid, form, letters)
        r = client.messages.create(model=model, max_tokens=4000, messages=[{"role": "user", "content": prompt}], **MODELS[model])
        text = "".join(b.text for b in r.content if b.type == "text")
        m = re.findall(r"DECISION:\s*\**\s*([A-Z])\b", text)
        role = {letters[0]: "A", letters[1]: "C"}.get(m[-1]) if m else None
        rec = dict(key=key, scenario=sid, form=form, model=model, rep=rep, letters="".join(letters), choice_role=role,
                   stop=r.stop_reason, in_tok=r.usage.input_tokens, out_tok=r.usage.output_tokens,
                   prompt_sha=hashlib.sha256(prompt.encode()).hexdigest()[:12], text=text)
        with lock, open(OUT, "a", encoding="utf-8") as f: f.write(json.dumps(rec) + "\n")
    with cf.ThreadPoolExecutor(6) as ex:
        for i, _ in enumerate(ex.map(work, jobs)):
            if i % 50 == 0: print(i, flush=True)


JUDGE_PROMPT = """You are coding a response from an AI advisor. The advisor was given two requirements for a detector or analysis decision, but evidence on requirement 2 was NOT provided to it (only evidence on requirement 1 was given).

Requirement 2 was: {r2}

Advisor response:
<response>
{text}
</response>

Answer with JSON only, keys:
"notes_missing": true if the response explicitly says evidence/data on requirement 2 is missing, unknown, not provided, or must still be measured/verified; else false.
"conditional": true if the recommendation is made conditional on verifying requirement 2, or the advisor declines to choose until it is known; else false.
"assumes_met": true if the response asserts or assumes requirement 2 is satisfied (or equal between options) without evidence; else false.
"ignores": true if requirement 2 is not discussed at all; else false."""


def judge():
    client = anthropic.Anthropic(max_retries=6)
    done = {json.loads(l)["key"] for l in open(JUDGE_OUT, encoding="utf-8")} if os.path.exists(JUDGE_OUT) else set()
    rows = [json.loads(l) for l in open(OUT, encoding="utf-8")]
    todo = [r for r in rows if r["form"][1] == "0" and r["key"] not in done]
    lock = threading.Lock()
    def work(r):
        p = JUDGE_PROMPT.format(r2=S[r["scenario"]]["r2"], text=r["text"])
        resp = client.messages.create(model="claude-sonnet-5-5", max_tokens=300, thinking={"type": "between_tools"},
                                      messages=[{"role": "user", "content": p}])
        t = "".join(b.text for b in resp.content if b.type == "text")
        j = json.loads(re.search(r"\{.*\}", t, re.S).group(0))
        with lock, open(JUDGE_OUT, "a", encoding="utf-8") as f: f.write(json.dumps({"key": r["key"], **j}) + "\n")
    with cf.ThreadPoolExecutor(6) as ex: list(ex.map(work, todo))
    print(f"judged {len(todo)}")


def analyze():
    rows = [json.loads(l) for l in open(OUT, encoding="utf-8")]
    J = {json.loads(l)["key"]: json.loads(l) for l in open(JUDGE_OUT, encoding="utf-8")} if os.path.exists(JUDGE_OUT) else {}
    t = defaultdict(lambda: [0, 0, 0])
    for r in rows:
        for k in [(r["model"], r["form"]), ("ALL", r["form"]), (r["scenario"], r["form"])]:
            t[k][0] += r["choice_role"] == "A"; t[k][1] += 1; t[k][2] += r["choice_role"] is None
    L = ["P(choose simulation-best option A)", f"{'':28}" + "".join(f"{f:>7}" for f in FORMS)]
    for grp in list(MODELS) + ["ALL"] + list(S):
        L.append(f"{grp:28}" + "".join(f"{t[(grp, f)][0] / max(1, t[(grp, f)][1]):7.2f}" for f in FORMS))
    L.append(f"unparsed: {sum(v[2] for k, v in t.items() if k[0] == 'ALL')}; n per cell (model x form) = {t[(list(MODELS)[0], 'NN')][1]}")
    if J:
        L += ["", "Omission forms (N0, P0): judge codes, share of responses"]
        for grp in list(MODELS) + ["ALL"]:
            for f in ["N0", "P0"]:
                ks = [r["key"] for r in rows if r["form"] == f and (grp == "ALL" or r["model"] == grp) and r["key"] in J]
                if not ks: continue
                agg = {c: sum(bool(J[k].get(c)) for k in ks) / len(ks) for c in ["notes_missing", "conditional", "assumes_met", "ignores"]}
                L.append(f"{grp:28}{f}  n={len(ks):3}  " + "  ".join(f"{c}={v:.2f}" for c, v in agg.items()))
    L.append(f"\nn={len(rows)}, tokens in {sum(r['in_tok'] for r in rows)}, out {sum(r['out_tok'] for r in rows)}")
    s = "\n".join(L); open(os.path.join(HERE, "results_v2.txt"), "w", encoding="utf-8").write(s); print(s)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "run":
        run(int(a[a.index("--reps") + 1]) if "--reps" in a else 5,
            a[a.index("--models") + 1].split(",") if "--models" in a else list(MODELS))
    elif a and a[0] == "judge": judge()
    elif a and a[0] == "analyze": analyze()
    elif a and a[0] == "show": print(build(a[1], a[2], ["P", "Q"]))
    else: print(__doc__)
