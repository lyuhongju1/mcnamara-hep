# Pre-registered requirement extraction + T/U classification.
# Written BEFORE reading any academic_report.md. Classes are frozen once coding begins.
# fields: (req_id, requirement, source, class, subtype, reason)
# source: goal | constraint | task_description | context
# subtype: PERF (performance requirement) | SPEC (design-parameter bound checkable from geometry)
CV4 = "celeritas_run_files_v4/"; CV7 = "celeritas_run_files_v7/"; OV5 = "opticks_run_files_v5/"; OV9 = "opticks_run_files_v9/"
HCAL_RAD = "Radiation damage/tolerance is not produced by Geant4 energy-deposit runs (needs dose + damage models/data)."
NONCOMP = "e/h or e/pi could be computed by also shooting electrons in Geant4, but prescribed workflow is pions/protons only; ambiguous."
JET = "Only single-particle guns available; jet energy measurement needs multi-particle jets/fragmentation not produced."
HERM = "Hermeticity/cracks would need angular scans across module boundaries; workflow shoots one module centre; possible in principle."
COMPACT = "Depth in cm/lambda trivially computable but no target dimension given; feasibility beyond size not quantifiable."
REQS = {
CV4 + "calorimeter": [
 ("R1", "Accurate hadron energy measurement (energy resolution)", "goal", "T", "PERF", "sigma_E/E from Geant4 deposits"),
 ("R2", "Cover energy range 10-200 GeV", "constraint", "T", "PERF", "Simulable at each energy"),
 ("R3", "Response linearity", "task_description", "T", "PERF", "Deposited vs incident energy"),
 ("R4", "Shower containment", "task_description", "T", "PERF", "Leakage computable"),
 ("R5", "Minimize non-compensation effects", "goal+constraint", "T?", "PERF", NONCOMP),
 ("R6", "Compact design with tight spatial constraints", "goal+constraint", "T?", "SPEC", COMPACT),
 ("R7", "Moderate radiation exposure (radiation tolerance)", "constraint", "U", "PERF", HCAL_RAD),
 ("R8", "Hermeticity", "task_description", "U?", "PERF", HERM),
 ("R9", "Jet energy measurement capability", "task_description", "U", "PERF", JET),
],
CV7 + "calorimeter": [
 ("R1", "Good energy resolution", "goal", "T", "PERF", "sigma_E/E from Geant4 deposits"),
 ("R2", "Cover energy range 10-200 GeV (sim capped at 50 GeV)", "constraint", "T", "PERF", "Simulable; run cap means 50-200 GeV only by extrapolation"),
 ("R3", "Response linearity", "task_description", "T", "PERF", "Deposited vs incident energy"),
 ("R4", "Shower containment / leakage", "task_description", "T", "PERF", "Leakage computable"),
 ("R5", "Minimal non-compensation effects", "goal", "T?", "PERF", NONCOMP),
 ("R6", "Compact design with tight spatial constraints", "goal+constraint", "T?", "SPEC", COMPACT),
 ("R7", "Moderate radiation exposure (radiation tolerance)", "constraint", "U", "PERF", HCAL_RAD),
 ("R8", "Total depth 8-12 interaction lengths", "constraint", "T", "SPEC", "Geometry"),
 ("R9", "Sampling fraction 2-5%", "constraint", "T", "SPEC", "Active/total deposits"),
 ("R10", "Jet energy measurement (projective vs planar)", "context", "U", "PERF", JET),
 ("R11", "Hermeticity (cylindrical)", "context", "U?", "PERF", HERM),
],
CV4 + "emcal": [
 ("R1", "Energy resolution 2-3%/sqrt(E)", "goal+constraint", "T", "PERF", "sigma_E/E from deposits"),
 ("R2", "Cover 0.5-10 GeV electrons", "constraint", "T", "PERF", "Simulable"),
 ("R3", "Full EM shower containment", "constraint", "T", "PERF", "Leakage computable"),
 ("R4", "Energy linearity", "task_description", "T", "PERF", "Computable"),
 ("R5", "Homogeneous calorimeter with dense scintillating material", "goal+constraint", "T", "SPEC", "Material/topology checkable from geometry"),
 ("R6", "Dead material between towers (projective)", "context", "U?", "PERF", "Needs multi-tower crack scan; single central gun; possible in principle"),
 ("R7", "Position resolution vs tower segmentation", "context", "T?", "PERF", "Needs per-cell readout; tool output mostly total deposit"),
],
CV7 + "emcal": [
 ("R1", "Energy resolution ~1-3%/sqrt(E)", "goal", "T", "PERF", "sigma_E/E from deposits"),
 ("R2", "Cover 0.5-10 GeV electrons", "constraint", "T", "PERF", "Simulable (sweep 0.5-5)"),
 ("R3", "Total depth 15-25 X0", "constraint", "T", "SPEC", "Geometry"),
 ("R4", "Shower containment", "task_description", "T", "PERF", "Leakage computable"),
 ("R5", "Linearity", "task_description", "T", "PERF", "Computable"),
 ("R6", "Homogeneous single-material design (no shashlik/accordion)", "constraint", "T", "SPEC", "Geometry check"),
],
CV4 + "muon": [
 ("R1", "High muon identification efficiency", "goal", "T", "PERF", "Last-layer deposit fraction"),
 ("R2", "Reject punch-through pions", "goal", "T", "PERF", "Punch-through fraction"),
 ("R3", "Cover 5-100 GeV", "constraint", "T", "PERF", "Simulable"),
 ("R4", "Iron absorbers", "constraint", "T", "SPEC", "Geometry check"),
 ("R5", "Angular coverage (cylindrical)", "context", "T?", "PERF", "Solid angle computable from geometry; no angular scans"),
],
CV7 + "muon": [
 ("R1", "High muon identification efficiency", "goal", "T", "PERF", "Simulable"),
 ("R2", "Reject punch-through pions", "goal", "T", "PERF", "Simulable"),
 ("R3", "Cover 5-100 GeV (sim capped at 50)", "constraint", "T", "PERF", "Simulable; 50-100 extrapolated"),
 ("R4", "3-6 iron/scintillator layers", "constraint", "T", "SPEC", "Geometry"),
 ("R5", "Iron 10-30 cm per layer", "constraint", "T", "SPEC", "Geometry"),
 ("R6", "Total depth 3-6 lambda_I", "constraint", "T", "SPEC", "Geometry"),
 ("R7", "Muon/pion separation power", "context", "T", "PERF", "From deposits"),
 ("R8", "Angular coverage (cylindrical)", "context", "T?", "PERF", "Geometry calc possible; not simulated"),
],
CV4 + "tof": [
 ("R1", "Distinguish pi/K/p over 0.5-3 GeV/c", "goal+constraint", "U?", "PERF", "Needs detector time resolution (photostatistics, light transport, electronics) not produced by Geant4 energy-deposit runs; Delta-t is analytic"),
 ("R2", "Cover momentum range 0.5-3 GeV/c", "constraint", "T", "PERF", "Simulable"),
 ("R3", "Plastic scintillator", "constraint", "T", "SPEC", "Geometry"),
 ("R4", "Particle coverage (cylindrical)", "context", "T?", "PERF", "Geometric acceptance computable; not simulated"),
],
CV7 + "tof": [
 ("R1", "Reliably distinguish pi/K/p over 0.5-3 GeV/c", "goal", "U?", "PERF", "Needs time resolution not produced by tools; Delta-t analytic"),
 ("R2", "Cover momentum range 0.5-3 GeV/c", "constraint", "T", "PERF", "Simulable"),
 ("R3", "Scintillator thickness 1-5 cm", "constraint", "T", "SPEC", "Geometry"),
 ("R4", "Path length 0.5-2 m", "constraint", "T", "SPEC", "Geometry"),
 ("R5", "Particle coverage (cylindrical)", "context", "T?", "PERF", "Geometric acceptance computable; not simulated"),
],
CV4 + "tracking": [
 ("R1", "Good momentum resolution 1-50 GeV/c", "goal", "T?", "PERF", "No B-field or track fit in tools; multiple-scattering proxy computable"),
 ("R2", "Minimize material budget", "goal+constraint", "T", "PERF", "X/X0 from geometry"),
 ("R3", "Maintain hit detection efficiency", "constraint", "T", "PERF", "Per-layer deposits"),
 ("R4", "~0.1 MeV deposit for MIP in 300um Si", "constraint", "T", "PERF", "Deposits"),
 ("R5", "Cover 1-50 GeV/c", "constraint", "T", "PERF", "Simulable"),
 ("R6", "Track reconstruction (cylindrical vs planar)", "context", "U?", "PERF", "No track reconstruction in tool chain"),
],
CV7 + "tracking": [
 ("R1", "Good momentum resolution 1-50 GeV/c", "goal", "T?", "PERF", "No B-field/track fit; MS proxy computable"),
 ("R2", "Minimize material budget", "goal", "T", "PERF", "X/X0 from geometry"),
 ("R3", "Minimize multiple scattering", "constraint", "T?", "PERF", "Highland-formula proxy / hit positions"),
 ("R4", "Maintain hit detection", "constraint", "T", "PERF", "Deposits"),
 ("R5", "3-8 layers", "constraint", "T", "SPEC", "Geometry"),
 ("R6", "Layer thickness 100-500 um", "constraint", "T", "SPEC", "Geometry"),
 ("R7", "Layer spacing 2-10 cm", "constraint", "T", "SPEC", "Geometry"),
 ("R8", "Track reconstruction (cylindrical vs planar)", "context", "U?", "PERF", "No reconstruction in tools"),
],
OV5 + "darkside_lar": [
 ("R1", "Light yield (PE/keV) from own simulation", "goal+context", "T", "PERF", "Opticks photon hits"),
 ("R2", "Optimize geometry for improved low-energy DM detection", "goal", "T?", "PERF", "Light-yield/threshold proxy quantifiable; full DM sensitivity (PSD, backgrounds) not"),
 ("R3", "Same PMT density ratio as paper", "constraint", "T", "SPEC", "Geometry"),
 ("R4", "Characterize S1/S2 signal properties", "context", "U?", "PERF", "S1 simulable; S2 needs drift/electroluminescence not in optical setup"),
 ("R5", "Assess position reconstruction capability", "context", "T?", "PERF", "PMT hit patterns produced; needs reconstruction analysis"),
 ("R6", "Improved uniformity", "context", "T", "PERF", "Hit maps"),
 ("R7", "Low-radioactivity underground argon", "context/parameters", "U", "PERF", "Radiopurity not produced by optical sim"),
],
OV9 + "darkside_lar": [
 ("R1", "Light yield (PE/keV) from own simulation", "goal+context", "T", "PERF", "Opticks hits"),
 ("R2", "Optimize for improved low-energy DM detection", "goal", "T?", "PERF", "Proxy quantifiable; full sensitivity not"),
 ("R3", "Characterize S1/S2 signal properties", "context", "U?", "PERF", "S2 not simulated"),
 ("R4", "Assess position reconstruction capability", "context", "T?", "PERF", "Hit patterns available"),
 ("R5", "Improved uniformity", "context", "T", "PERF", "Hit maps"),
 ("R6", "Low-radioactivity underground argon", "context/parameters", "U", "PERF", "Radiopurity not produced"),
],
OV5 + "detector": [
 ("R1", "Maximize light collection efficiency", "goal", "T", "PERF", "Opticks hits / produced"),
 ("R2", "Uniform detector response", "goal", "T", "PERF", "Position-dependent hits"),
 ("R3", "Photosensor cost-effectiveness", "goal", "U", "PERF", "Cost not produced by tools (needs price data); LCE-per-sensor proxy possible"),
],
OV9 + "detector": [
 ("R1", "Maximize light collection efficiency", "goal", "T", "PERF", "Opticks hits"),
 ("R2", "Uniform detector response", "goal", "T", "PERF", "Hit maps"),
 ("R3", "Photosensor coverage cost-effectiveness", "context", "U", "PERF", "Cost not produced by tools"),
],
OV5 + "protodune_lar": [
 ("R1", "Light yield (PE/MeV)", "context", "T", "PERF", "Opticks hits"),
 ("R2", "Detection efficiency", "context", "T", "PERF", "Hits/produced"),
 ("R3", "Spatial uniformity", "context", "T", "PERF", "Hit maps"),
 ("R4", "Propose PDS improvements (photosensor coverage)", "goal+context", "T", "PERF", "Re-simulate coverage variants"),
 ("R5", "Alternative wavelength-shifter configurations", "context", "T?", "PERF", "Modelable only if WLS optical properties configured"),
 ("R6", "Maintain sensor density ratio", "constraint", "T", "SPEC", "Geometry"),
],
OV9 + "protodune_lar": [
 ("R1", "Light yield", "goal", "T", "PERF", "Opticks hits"),
 ("R2", "Detection efficiency", "goal", "T", "PERF", "Hits/produced"),
 ("R3", "Spatial uniformity", "context", "T", "PERF", "Hit maps"),
 ("R4", "Optimize PDS (photosensor coverage)", "goal", "T", "PERF", "Re-simulate"),
 ("R5", "Alternative wavelength-shifter configurations", "context", "T?", "PERF", "Only if WLS modelled"),
],
}
EXCLUDED = """OPS/ENV/PROC excluded: number of configurations; events/run; GPU memory/photon budget; size & sensor caps imposed by GPU;
particle-type / energy-sweep prescriptions; starting configurations (16 X0, 4x20cm Fe, 4x300um Si); material constants (lambda_I, X0, light yield);
'no magnetic field' and 'mid-energy collider' (environment assumptions); 'extract design specs only' / 'do not compare to paper' (procedural);
'must explore topology and parameters' (procedural). Higgs runs (2) excluded: ML on fixed dataset, no detector simulation."""
