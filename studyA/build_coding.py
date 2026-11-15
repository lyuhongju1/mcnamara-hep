# Combines pre-registered classes (requirements_preregistered.py) with report codes below.
# Codes assigned after reading each academic_report.md. Usage: python -I build_coding.py <studyA_dir>
import json, sys, os, collections
D = sys.argv[1]
ns = {}
exec(open(os.path.join(D, "requirements_preregistered.py"), encoding="utf-8").read(), ns)
REQS = ns["REQS"]
CV4 = "celeritas_run_files_v4/"; CV7 = "celeritas_run_files_v7/"; OV5 = "opticks_run_files_v5/"; OV9 = "opticks_run_files_v9/"
# (code, dismiss, satisfied, evidence, note)
C = {
CV4+"calorimeter": {
 "R1": ("Q", False, "unknown", "compact tungsten projective design achieves superior energy resolution (σ/E = 0.0500 ± 0.0011)", "Report itself flags identical mean energy at all beam energies; numbers suspect"),
 "R2": ("Q", False, "unknown", "employed π+ particle beams at 10, 100, and 200 GeV", ""),
 "R3": ("M", False, "unknown", "response linearity was assessed across the full energy range", "No linearity number; report notes 148,903.9 MeV at every energy (a linearity failure) only as an 'anomaly'"),
 "R4": ("D", False, "unknown", "90% Containment: Improved radial shower containment due to cylindrical geometry", "Asserted, no number"),
 "R5": ("M", False, "unknown", "contributed to improved hadronic response through ... reduced non-compensation effects compared to steel", "One-line unsupported attribution; e/h never computed"),
 "R6": ("Q", False, "yes", "Compactness Factor: 5× more compact than baseline design", ""),
 "R7": ("M", False, "unknown", "Radiation hardness evaluation for long-term operation", "Future work only; tungsten recommended without radiation consideration"),
 "R8": ("D", False, "unknown", "Cost-Effective Alternative: Cylindrical brass barrel for balanced performance with hermetic coverage", "Hermeticity asserted, never simulated, yet used to justify alternative"),
 "R9": ("D", False, "unknown", "physics-motivated scoring that weighted hermeticity, crack effects, jet energy measurement capability", "Qualitative input to variant selection; limitation: single-particle studies don't capture jets"),
},
CV7+"calorimeter": {
 "R1": ("Q", False, "yes", "baseline configuration achieved optimal energy resolution of 8.12% ± 1.05%", ""),
 "R2": ("Q", False, "unknown", "Simulations were limited to 50 GeV maximum energy due to computational constraints", "10-50 GeV quantified; 50-200 GeV not"),
 "R3": ("Q", False, "yes", "Mean linearity: 83.3%", ""),
 "R4": ("M", False, "unknown", "Shower Containment: Fraction of energy deposited within detector volume", "Defined as metric, never reported"),
 "R5": ("D", False, "unknown", "degraded performance compared to steel is attributed to increased non-compensation effects in the denser tungsten medium", "Used in trade-off reasoning; e/h not computed"),
 "R6": ("Q", False, "no", "Baseline (Fe) | 1.000 | 1.000 | 0.000 | 0.862 | 0.773", "Recommended design has worst volume score (0.333 m3, 167 cm deep) despite hard 'tight spatial constraints'"),
 "R7": ("M", False, "unknown", "Radiation damage effects were not considered", "Limitation only"),
 "R8": ("Q", False, "yes", "Total depth: 167.0 cm (10 interaction lengths)", ""),
 "R9": ("Q", False, "yes", "Sampling fraction: 3.00%", "Design value, not measured"),
 "R10": ("X", False, "unknown", "", ""),
 "R11": ("M", False, "unknown", "Projective tower geometry for hermetic coverage", ""),
},
CV4+"emcal": {
 "R1": ("Q", False, "yes", "projective PbWO₄ tower configuration demonstrated superior performance with energy resolution of 2.14% ± 0.05%", "Single % value compared to a %/sqrt(E) target"),
 "R2": ("Q", False, "yes", "Each configuration was simulated using Geant4 across the full energy range", "Per-energy numbers not reported"),
 "R3": ("Q", False, "unknown", "optimal shower containment (90% within 100 mm radius)", "100 mm likely the geometry boundary; 'full' containment not shown"),
 "R4": ("Q", False, "yes", "excellent linearity (0.979 ± 0.001)", ""),
 "R5": ("D", False, "yes", "Dense scintillating crystals (PbWO₄) offer significant advantages over lower-density alternatives", "Also tested sampling (shashlik/accordion) variants"),
 "R6": ("M", False, "unknown", "Projective tower geometry optimizes light collection efficiency and reduces edge effects", ""),
 "R7": ("M", False, "unknown", "Tower segmentation enables better shower reconstruction and noise rejection", ""),
},
CV7+"emcal": {
 "R1": ("Q", False, "yes", "Expected Performance: 1.16-1.68% energy resolution across 0.5-10 GeV range", ""),
 "R2": ("Q", False, "unknown", "Parallel simulations were conducted at three representative energies (0.5, 2.0, and 5.0 GeV)", "5-10 GeV extrapolated"),
 "R3": ("Q", False, "yes", "PbWO₄ projective tower calorimeter with 17.8 cm depth (20 radiation lengths)", ""),
 "R4": ("Q", False, "yes", "Longitudinal containment exceeded 99% for the 20 radiation length depth specification", "May be design-derived rather than measured"),
 "R5": ("Q", False, "yes", "enhanced linearity (0.9897 vs 0.9663)", ""),
 "R6": ("D", False, "yes", "constructed from single active materials without passive absorber layers", ""),
},
CV4+"muon": {
 "R1": ("Q", False, "yes", "Baseline Planar: 100.0% efficiency (1000/1000 events) at all energies", ""),
 "R2": ("Q", False, "unknown", "detailed examination showed perfect rejection (100.0%) at individual energy points", "Report flags rejection numbers as inconsistent"),
 "R3": ("Q", False, "yes", "5 GeV ... 100 GeV (maximum specified energy)", ""),
 "R4": ("Q", False, "yes", "totaling 80 cm of iron (≈4.8 interaction lengths)", ""),
 "R5": ("X", False, "unknown", "", ""),
},
CV7+"muon": {
 "R1": ("Q", False, "yes", "All three configurations achieved 100% muon detection efficiency", ""),
 "R2": ("Q", False, "no", "Planar: Optimal muon resolution (0.1593) but lowest pion rejection (1.72)", "Recommended design chosen on an unrequested quantifiable metric (muon dE resolution) over the stated goal"),
 "R3": ("Q", False, "unknown", "Simulations were limited to 50 GeV maximum; extension to the full 100 GeV target range is necessary", ""),
 "R4": ("Q", False, "yes", "Layers: 4 iron/plastic scintillator pairs", ""),
 "R5": ("Q", False, "yes", "Iron thickness: 20 cm per layer (1.19 λ_int)", ""),
 "R6": ("Q", False, "yes", "Total depth: 84 cm (5.0 λ_int)", ""),
 "R7": ("Q", False, "no", "its limited pion rejection factor (1.72) indicates that 20 cm iron layers provide insufficient stopping power", ""),
 "R8": ("M", False, "unknown", "Cylindrical geometry for 4π coverage", ""),
},
CV4+"tof": {
 "R1": ("Q", False, "unknown", "particle separation capabilities of 5.1σ for π-K and 7.6σ for K-p discrimination", "Pseudo-quantified: timing from assumed σt = k/√Nph giving 8.9 ps (unphysical)"),
 "R2": ("Q", False, "unknown", "Validated performance across 0.5-3 GeV/c with consistent characteristics", "0.5 GeV/c not simulated (1.0-2.0, then 1-20)"),
 "R3": ("D", False, "yes", "All simulations used plastic scintillator material with standard optical properties", ""),
 "R4": ("D", False, "unknown", "modest improvements over the baseline, primarily through enhanced geometric acceptance. However, the gains were insufficient", "Affects choice; acceptance not quantified"),
},
CV7+"tof": {
 "R1": ("Q", False, "no", "Cylindrical barrel topology is optimal ... achieving 103 ps timing resolution", "103 ps asserted, not simulated; report's own Δt (50-200 ps at 3 GeV) gives <1σ π-K at 3 GeV/c, contradicting the '3-sigma' claim"),
 "R2": ("Q", False, "unknown", "Energies: 1.0, 2.0, 3.0 GeV (covering momentum range 0.5-3 GeV/c)", "0.5 GeV/c not simulated"),
 "R3": ("Q", False, "yes", "3 cm scintillator thickness providing optimal balance", ""),
 "R4": ("Q", False, "yes", "1.06 m effective path length", ""),
 "R5": ("D", False, "unknown", "The 98% detection efficiency indicates excellent geometric acceptance", "Efficiency misread as acceptance"),
},
CV4+"tracking": {
 "R1": ("M", False, "unknown", "Direct measurement of tracking resolution through trajectory reconstruction rather than energy deposit analysis", "Surrogate: energy-deposit σ/E used in place of momentum resolution in the recommendation"),
 "R2": ("Q", False, "yes", "Minimal material budget (0.013 X₀)", ""),
 "R3": ("Q", False, "yes", "Excellent hit efficiency (99.9%)", ""),
 "R4": ("Q", False, "no", "The measured energy deposit of 0.437 MeV exceeds the expected ~0.1 MeV", ""),
 "R5": ("Q", False, "yes", "Momentum range: 1, 5, 10, 50 GeV/c", "No per-momentum results"),
 "R6": ("M", False, "unknown", "trajectory reconstruction", "Only as future work"),
},
CV7+"tracking": {
 "R1": ("Q", False, "unknown", "Momentum Resolution: 0.009% at 10 GeV/c (excellent precision)", "Analytic, no completed simulation; implausible value"),
 "R2": ("Q", False, "yes", "Material Budget: 0.64% X₀", "Geometry calculation"),
 "R3": ("Q", False, "unknown", "Multiple scattering: 0.05 mrad", "Analytic"),
 "R4": ("M", False, "unknown", "No energy deposition or efficiency measurements obtained", "Acknowledged absent"),
 "R5": ("Q", False, "yes", "Layers: 4", ""),
 "R6": ("Q", False, "yes", "Silicon thickness: 150 μm", ""),
 "R7": ("Q", False, "unknown", "Layer Spacing: 5.0-8.3 cm", "Recommended config's spacing not stated"),
 "R8": ("X", False, "unknown", "", ""),
},
OV5+"darkside_lar": {
 "R1": ("Q", False, "unknown", "light yield of 2.12 PE/keV", ""),
 "R2": ("Q", False, "unknown", "66.51% improvement in light yield (3.53 PE/keV)", "Light-yield proxy only"),
 "R3": ("D", False, "no", "PMT density maintenance: Original ratio preserved through proportional scaling", "Optimization raises PMTs 30->50 ('Surface coverage: 133.3%'), breaking the ratio"),
 "R4": ("X", False, "unknown", "", "S1/S2 never mentioned"),
 "R5": ("Q", False, "unknown", "9.37% improvement in position reconstruction accuracy (8.82mm 3D resolution)", ""),
 "R6": ("M", False, "unknown", "The optimized detector demonstrated enhanced spatial uniformity", "No uniformity number"),
 "R7": ("X", False, "unknown", "", "Only 'radioactive background simulations' as future work"),
},
OV9+"darkside_lar": {
 "R1": ("Q", False, "unknown", "light yield of 1479.23 ± 0.54 PE/MeV at 1 MeV", ""),
 "R2": ("Q", False, "unknown", "modest improvements at lower energies (0.1-1 MeV) suggest that other factors beyond PMT count may limit performance", "Improvement quantified mainly at 5 MeV"),
 "R3": ("X", False, "unknown", "", "S1/S2 not mentioned; quenching-based 'discrimination power' substituted"),
 "R4": ("Q", False, "unknown", "spatial resolution capabilities ranging from 1.23 mm at 0.1 MeV to 25.27 mm at 1 MeV", ""),
 "R5": ("X", False, "unknown", "", ""),
 "R6": ("M", False, "unknown", "DarkSide-50 532-day Dark Matter Search with Low-Radioactivity Argon", "Only in cited paper title"),
},
OV5+"detector": {
 "R1": ("Q", False, "unknown", "Light Collection Efficiency: 1.0000 ± 0.0000 (100% collection)", "Implausible 100% LCE"),
 "R2": ("Q", False, "unknown", "Spatial Uniformity: 0.784 ± 0.078 (coefficient of variation)", ""),
 "R3": ("Q", False, "unknown", "Cost Effectiveness: 1.275 ± 0.128", "Pseudo-quantified: 'cost-effectiveness' = efficiency x uniformity per sensor; no cost input"),
},
OV9+"detector": {
 "R1": ("Q", False, "unknown", "Light collection efficiency: 0.0 (analysis artifact)", "Number produced but declared an artifact; no recommendation"),
 "R2": ("Q", False, "unknown", "Spatial uniformity: 1.0 (constant data indication)", "Artifact"),
 "R3": ("X", False, "unknown", "", "Cost-effectiveness absent"),
},
OV5+"protodune_lar": {
 "R1": ("Q", False, "unknown", "Light Yield: 22.61 PE/MeV (+3129.3% improvement)", ""),
 "R2": ("Q", False, "unknown", "Detection Efficiency: 0.1700 ± 0.0376 (+70.0% improvement)", ""),
 "R3": ("Q", False, "unknown", "Spatial Uniformity Index: 0.404", "Optimized uniformity asserted without number"),
 "R4": ("Q", False, "unknown", "70% enhancement in detection efficiency, 3130% increase in light yield", ""),
 "R5": ("D", False, "unknown", "photosensor positioning and TPB coating coverage were major limiting factors", "WLS effect not isolated"),
 "R6": ("Q", False, "no", "preserving sensor density ratios at 80% of the original configuration", ""),
},
OV9+"protodune_lar": {
 "R1": ("Q", False, "unknown", "light yield of 652.6 ± 0.9 photoelectrons per MeV", ""),
 "R2": ("Q", False, "unknown", "100% detection efficiency across all energy scales", "Implausible"),
 "R3": ("Q", False, "unknown", "coefficient of variation of 2.769% for spatial uniformity", ""),
 "R4": ("Q", False, "unknown", "Predicted light yield: 870.1 PE/MeV (+33% improvement)", "Predicted by linear scaling, not simulated"),
 "R5": ("M", False, "unknown", "Modified sensor placement and TPB coating parameters to improve spatial response uniformity", "Listed, not tested"),
},
}
rows = []
for run, reqs in REQS.items():
    for rid, req, src, cls, sub, reason in reqs:
        code, dis, sat, ev, note = C[run][rid]
        rows.append(dict(run=run.rstrip("/"), req_id=rid, requirement=req, source=src, cls=cls, subtype=sub,
                         class_reason=reason, code=code, dismiss=dis, satisfied=sat, evidence=ev, note=note))
with open(os.path.join(D, "coding.jsonl"), "w", encoding="utf-8") as f:
    for r in rows:
        r2 = dict(r); r2["class"] = r2.pop("cls")
        f.write(json.dumps(r2, ensure_ascii=False) + "\n")

def tab(filt, title):
    out = [f"\n### {title}\n", "| class | Q | D | M | X | n |", "|---|---|---|---|---|---|"]
    for k in ["T", "T?", "U?", "U"]:
        c = collections.Counter(r["code"] for r in rows if r["cls"] == k and filt(r))
        n = sum(c.values())
        if n: out.append(f"| {k} | {c['Q']} | {c['D']} | {c['M']} | {c['X']} | {n} |")
    return "\n".join(out)
txt = tab(lambda r: True, "All requirements (n=%d)" % len(rows))
txt += tab(lambda r: r["subtype"] == "PERF", "PERF only (SPEC design bounds removed)")
txt += tab(lambda r: r["subtype"] == "PERF" and r["source"] != "context", "PERF, excluding context-only items")
per = ["\n### Per run (T-class Q/total | U-class [U,U?] D+/total)\n", "| run | T: Q/n | T?: Q/n | U+U?: D-or-better/n | U+U? codes |", "|---|---|---|---|---|"]
for run in REQS:
    rr = [r for r in rows if r["run"] == run.rstrip("/")]
    t = [r for r in rr if r["cls"] == "T"]; tq = [r for r in rr if r["cls"] == "T?"]; u = [r for r in rr if r["cls"] in ("U", "U?")]
    per.append(f"| {run.rstrip('/')} | {sum(r['code']=='Q' for r in t)}/{len(t)} | {sum(r['code']=='Q' for r in tq)}/{len(tq)} | {sum(r['code'] in 'QD' for r in u)}/{len(u)} | {' '.join(r['req_id']+':'+r['code'] for r in u)} |")
txt += "\n" + "\n".join(per)
open(os.path.join(D, "crosstab.md"), "w", encoding="utf-8").write(txt + "\n")
sat = collections.Counter((r["cls"], r["satisfied"]) for r in rows)
open(os.path.join(D, "satisfied.json"), "w").write(json.dumps({f"{a}|{b}": v for (a, b), v in sat.items()}, indent=1))
print(len(rows))
