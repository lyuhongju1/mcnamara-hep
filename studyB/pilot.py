"""Study B pilot: does the *form* of information (number vs prose) change which criterion drives a design choice?

Design (within scenario): 2 framings (hard, balanced) x 4 forms (metric N/P x constraint N/P) x models x reps.
Information content is held fixed across forms; only whether each criterion is stated as numbers or as words changes.
Option A is always best on the simulation metric and worst on the non-simulated constraint (fails it under 'hard').
Letters shown to the model are shuffled per sample.

Usage: python -I pilot.py run [--reps 5] [--models m1,m2]   then   python -I pilot.py analyze
"""
import json, os, random, re, sys, hashlib, threading, concurrent.futures as cf
import anthropic

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "responses.jsonl")

MODELS = {  # minimum reasoning per model, as in the companion hindsight study
    "claude-haiku-5-5": {"thinking": {"type": "disabled"}},
    "claude-sonnet-5-5": {"thinking": {"type": "between_tools"}},
    "claude-opus-5-5": {"thinking": {"type": "adaptive"}, "output_config": {"effort": "low"}},
    "claude-sonnet-4-5-20250929": {},
}

# Each scenario: roles A (metric-best, constraint-worst), B (middle), C (metric-worst, constraint-best).
SCEN = {
 "S1_scint": dict(
  who="a low-background gamma-ray screening facility that assays materials for a dark-matter experiment",
  task="choose the scintillator for a new gamma spectrometer",
  r1="energy resolution as good as possible",
  r2="intrinsic background of the scintillator (its own radioactivity) low enough for low-background assays",
  opts="three candidate inorganic scintillator crystals",
  m_src="the Geant4 + optical simulation study", c_src="the radiopurity assay of sample crystals",
  m_num="Energy resolution at 662 keV (FWHM): {A} 2.9%, {B} 4.5%, {C} 8.5%.",
  m_pro="{A} has the best energy resolution by a wide margin; {B} is intermediate; {C} has the worst.",
  c_num="Intrinsic background, 100-3000 keV: {A} 2.0, {B} 0.3, {C} 0.1 counts/kg/day.",
  c_num_budget=" The facility's background budget is 0.5 counts/kg/day.",
  c_pro="{A}'s intrinsic background is far above that of {B} and {C}; {B}'s is moderately above {C}'s; {C}'s is the lowest.",
  c_pro_budget=" {A} exceeds the facility's background budget; {B} and {C} are within it.",
  kw=["background", "radio", "intrinsic", "activity", "contamina"]),
 "S2_pixel": dict(
  who="an LHC experiment preparing its high-luminosity inner tracker",
  task="choose the sensor technology for the innermost pixel layer",
  r1="single-hit spatial resolution as good as possible",
  r2="hit efficiency maintained up to the end-of-life fluence of 2e16 neq/cm^2",
  opts="three candidate pixel sensor technologies",
  m_src="the Geant4 + charge-transport simulation study", c_src="the irradiation and test-beam campaign",
  m_num="Single-hit resolution (unirradiated): {A} 6 um, {B} 9 um, {C} 14 um.",
  m_pro="{A} has the best single-hit resolution by a wide margin; {B} is intermediate; {C} has the worst.",
  c_num="Hit efficiency after 2e16 neq/cm^2: {A} 82%, {B} 98.5%, {C} 99.2%.",
  c_num_budget=" The layer requires at least 97%.",
  c_pro="After end-of-life fluence, {A}'s hit efficiency drops far below that of {B} and {C}; {B} is slightly below {C}; {C} retains the most.",
  c_pro_budget=" {A} falls below the layer's efficiency requirement; {B} and {C} meet it.",
  kw=["irradia", "fluence", "radiation", "end-of-life", "end of life", "damage"]),
 "S3_lar": dict(
  who="a liquid-argon neutrino experiment",
  task="choose the photon-detection module design for the far detector, where modules are inaccessible after the cryostat is filled",
  r1="light collection (photoelectrons per MeV) as high as possible",
  r2="reliability of the modules through repeated cooldowns, since failed modules cannot be replaced",
  opts="three candidate photon-detection module designs",
  m_src="the Geant4 optical-photon simulation study", c_src="the thermal-cycling tests (300 K to 87 K, 20 cycles)",
  m_num="Light collection: {A} 38 PE/MeV, {B} 27 PE/MeV, {C} 18 PE/MeV.",
  m_pro="{A} collects the most light by a wide margin; {B} is intermediate; {C} collects the least.",
  c_num="Fraction of modules failed after 20 cycles: {A} 30%, {B} 2%, {C} 0.5%.",
  c_num_budget=" The reliability requirement is at most 5%.",
  c_pro="{A}'s modules failed far more often than {B}'s or {C}'s; {B}'s failed slightly more often than {C}'s; {C}'s failed least.",
  c_pro_budget=" {A} fails the reliability requirement; {B} and {C} meet it.",
  kw=["thermal", "cycl", "reliab", "failure", "failed", "cryo", "cooldown"]),
 "S4_selection": dict(
  who="an LHC analysis team searching for a rare process",
  task="choose the event selection for the search",
  r1="expected signal significance as high as possible",
  r2="the selection should rely on variables that the simulation models well in data, so the background estimate is defensible",
  opts="three candidate event selections",
  m_src="the Monte Carlo sensitivity study (statistical uncertainty only)", c_src="the data/MC comparison in a signal-free validation region",
  m_num="Expected significance: {A} 4.1 sigma, {B} 3.4 sigma, {C} 2.6 sigma.",
  m_pro="{A} gives the highest expected significance by a wide margin; {B} is intermediate; {C} gives the lowest.",
  c_num="Data/MC yield disagreement in the validation region: {A} 35%, {B} 6%, {C} 3%.",
  c_num_budget=" The team's tolerance is 10%.",
  c_pro="{A}'s data/MC disagreement in the validation region is far larger than {B}'s or {C}'s; {B}'s is slightly larger than {C}'s; {C}'s is smallest.",
  c_pro_budget=" {A} exceeds the team's tolerance; {B} and {C} are within it.",
  kw=["validation", "data/mc", "data-mc", "mismodel", "systematic", "disagree", "defensib", "modeling", "modelling"]),
}

FRAME = {
 "hard": "Requirement 2 is a hard requirement: an option that fails it cannot be used. Within that, requirement 1 should be as good as possible.",
 "balanced": "The collaboration considers the two requirements equally important.",
 "tradeoff2": "The collaboration considers the two requirements equally important.",
}
FORMS = ["NN", "NP", "PN", "PP"]

# 2-option trade-off variant (frame "tradeoff2"): A better on the simulated metric, C better on the other criterion,
# equal stated weight, moderate magnitudes both ways. Outcome: P(choose A).
T2 = {
 "S1_scint": dict(m_num="Energy resolution at 662 keV (FWHM): {A} 3.5%, {C} 6.0%.",
                  m_pro="{A}'s energy resolution is substantially better than {C}'s.",
                  c_num="Intrinsic background, 100-3000 keV: {A} 0.6, {C} 0.2 counts/kg/day.",
                  c_pro="{A}'s intrinsic background is substantially higher than {C}'s."),
 "S2_pixel": dict(m_num="Single-hit resolution (unirradiated): {A} 7 um, {C} 11 um.",
                  m_pro="{A}'s single-hit resolution is substantially better than {C}'s.",
                  c_num="Hit efficiency after 2e16 neq/cm^2: {A} 95.0%, {C} 98.5%.",
                  c_pro="After end-of-life fluence, {A}'s hit efficiency is substantially lower than {C}'s."),
 "S3_lar": dict(m_num="Light collection: {A} 32 PE/MeV, {C} 22 PE/MeV.",
                  m_pro="{A} collects substantially more light than {C}.",
                  c_num="Fraction of modules failed after 20 cycles: {A} 6%, {C} 2%.",
                  c_pro="{A}'s modules failed substantially more often than {C}'s."),
 "S4_selection": dict(m_num="Expected significance: {A} 3.9 sigma, {C} 3.1 sigma.",
                  m_pro="{A} gives substantially higher expected significance than {C}.",
                  c_num="Data/MC yield disagreement in the validation region: {A} 15%, {C} 5%.",
                  c_pro="{A}'s data/MC disagreement in the validation region is substantially larger than {C}'s."),
}  # metric form, constraint form (N=numbers, P=prose)


def build(sid, frame, form, letters):
    s = SCEN[sid]; L = dict(zip("ABC", letters))
    if frame == "tradeoff2":
        t = T2[sid]
        m = (t["m_num"] if form[0] == "N" else t["m_pro"]).format(**L)
        c = (t["c_num"] if form[1] == "N" else t["c_pro"]).format(**L)
        pair = sorted([L["A"], L["C"]])
        NL = chr(10)
        return NL.join([
            f"You are advising {s['who']}. The task is to {s['task']}.", "",
            "Requirements:", f"1. {s['r1'][0].upper() + s['r1'][1:]}.", f"2. {s['r2'][0].upper() + s['r2'][1:]}.", FRAME[frame], "",
            f"There are {s['opts'].replace('three', 'two')}, labelled {pair[0]} and {pair[1]}.", "",
            f"From {s['m_src']}:", m, "", f"From {s['c_src']}:", c, "",
            "Recommend one option. Give your reasoning in at most 150 words, then end with a final line of the form `DECISION: <letter>`."])
    m = (s["m_num"] if form[0] == "N" else s["m_pro"]).format(**L)
    if form[1] == "N": c = s["c_num"] + (s["c_num_budget"] if frame == "hard" else "")
    else: c = s["c_pro"] + (s["c_pro_budget"] if frame == "hard" else "")
    c = c.format(**L)
    shown = ", ".join(sorted(letters))
    return (f"You are advising {s['who']}. The task is to {s['task']}.\n\n"
            f"Requirements:\n1. {s['r1'][0].upper() + s['r1'][1:]}.\n2. {s['r2'][0].upper() + s['r2'][1:]}.\n{FRAME[frame]}\n\n"
            f"There are {s['opts']}, labelled {shown}.\n\n"
            f"From {s['m_src']}:\n{m}\n\nFrom {s['c_src']}:\n{c}\n\n"
            "Recommend one option. Give your reasoning in at most 150 words, then end with a final line of the form `DECISION: <letter>`.")


def call(client, model, prompt):
    kw = dict(model=model, max_tokens=4000, messages=[{"role": "user", "content": prompt}], **MODELS[model])
    r = client.messages.create(**kw)
    text = "".join(b.text for b in r.content if b.type == "text")
    return text, r.stop_reason, r.usage.input_tokens, r.usage.output_tokens


def run(reps, models, frames=None):
    client = anthropic.Anthropic(max_retries=6)
    done = set()
    if os.path.exists(OUT):
        for l in open(OUT, encoding="utf-8"):
            d = json.loads(l); done.add(d["key"])
    jobs = []
    for sid in SCEN:
        for frame in (frames or FRAME):
            for form in FORMS:
                for model in models:
                    for rep in range(reps):
                        key = f"{sid}|{frame}|{form}|{model}|{rep}"
                        if key in done: continue
                        rng = random.Random(hashlib.sha256(key.encode()).hexdigest())
                        letters = rng.sample("XYZ", 3)  # letters[0] plays role A, etc.
                        jobs.append((key, sid, frame, form, model, rep, letters))
    print(f"{len(jobs)} calls to make", flush=True)
    lock = threading.Lock()
    def work(j):
        key, sid, frame, form, model, rep, letters = j
        prompt = build(sid, frame, form, letters)
        text, stop, it, ot = call(client, model, prompt)
        m = re.findall(r"DECISION:\s*\**\s*([XYZ])", text)
        role = {l: r for l, r in zip(letters, "ABC")}.get(m[-1]) if m else None
        low = text.lower()
        rec = dict(key=key, scenario=sid, frame=frame, form=form, model=model, rep=rep, letters="".join(letters),
                   choice_letter=m[-1] if m else None, choice_role=role, stop=stop, in_tok=it, out_tok=ot,
                   mentions_constraint=any(k in low for k in SCEN[sid]["kw"]),
                   prompt_sha=hashlib.sha256(prompt.encode()).hexdigest()[:12], text=text)
        with lock:
            with open(OUT, "a", encoding="utf-8") as f: f.write(json.dumps(rec) + "\n")
        return rec
    with cf.ThreadPoolExecutor(6) as ex:
        for i, _ in enumerate(ex.map(work, jobs)):
            if i % 50 == 0: print(i, flush=True)


def analyze():
    rows = [json.loads(l) for l in open(OUT, encoding="utf-8")]
    from collections import defaultdict
    t = defaultdict(lambda: [0, 0, 0, 0])  # A, B, C, unparsed
    for r in rows:
        k = (r["frame"], r["model"], r["form"])
        t[k]["ABC".index(r["choice_role"]) if r["choice_role"] else 3] += 1
    lines = ["frame     model                        form  n   P(A)  P(B)  P(C)  unparsed"]
    for k in sorted(t):
        a, b, c, u = t[k]; n = a + b + c + u
        lines.append(f"{k[0]:9} {k[1]:28} {k[2]:4} {n:3} {a/n:5.2f} {b/n:5.2f} {c/n:5.2f} {u:3}")
    # pooled over models
    p = defaultdict(lambda: [0, 0])
    for r in rows:
        p[(r["frame"], r["scenario"], r["form"])][0] += r["choice_role"] == "A"; p[(r["frame"], r["scenario"], r["form"])][1] += 1
    lines += ["", "P(choose metric-best option A), pooled over models", "frame     scenario       NN    NP    PN    PP"]
    for fr in FRAME:
        for sid in SCEN:
            lines.append(f"{fr:9} {sid:13} " + " ".join(f"{p[(fr, sid, f)][0]/max(1, p[(fr, sid, f)][1]):5.2f}" for f in FORMS))
    cost_in = sum(r["in_tok"] for r in rows); cost_out = sum(r["out_tok"] for r in rows)
    lines += ["", f"n={len(rows)}, input tokens {cost_in}, output tokens {cost_out}",
              f"constraint mentioned in {sum(r['mentions_constraint'] for r in rows)}/{len(rows)} responses"]
    s = "\n".join(lines)
    open(os.path.join(HERE, "pilot_results.txt"), "w", encoding="utf-8").write(s); print(s)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "run":
        reps = int(a[a.index("--reps") + 1]) if "--reps" in a else 5
        models = a[a.index("--models") + 1].split(",") if "--models" in a else list(MODELS)
        frames = a[a.index("--frames") + 1].split(",") if "--frames" in a else ["hard", "balanced"]
        run(reps, models, frames)
    elif a and a[0] == "analyze": analyze()
    elif a and a[0] == "show":
        print(build(a[1], a[2], a[3], list("XYZ")))
    else: print(__doc__)
