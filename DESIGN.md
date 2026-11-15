# The McNamara fallacy in AI-assisted high-energy physics: design draft (2026-11-15)

## Claim under test
Bisht et al. (arXiv:2605.08956) say AI-driven science measures what is easy to measure, disregards what is not, presumes the unmeasured is unimportant, and finally declares it nonexistent (Yankelovich's four steps). Their only evidence is bibliometric (Hao et al. 2026), and none of it is from HEP. HEP is a hard test case, for two reasons. Its central tool, simulation, makes some requirements very cheap to quantify (resolution, efficiency, significance) while leaving others expensive or unquantifiable within a run (radiation tolerance, radiopurity, cryogenic reliability, data/MC mismodelling, cost, maintainability). And the field already has strong human norms (systematics culture, blinding) against exactly this failure.

We split the claim into three levels:

| Level | Question | Study |
|---|---|---|
| Decision | Given the same information, does stating a criterion in numbers rather than words change how much it drives the choice? | **B** (controlled vignettes) |
| Agent | In real autonomous runs, do tool-quantifiable requirements survive to the final recommendation while non-quantifiable ones are dropped or dismissed? | **A** (GRACE corpus, retrospective) and **C** (prospective GRACE/HEP-Prov agent runs) |
| Field | Does ML-for-HEP research concentrate on benchmark-amenable problems, relative to the community's stated priorities? | **D** (bibliometric) |

## Study A: retrospective on the GRACE corpus (running)
The 14 Sonnet-4 runs in `GRACE_whitepaper_data`. Before reading the report, each stated requirement is coded as tool-quantifiable (T) or not (U). Then we code how the final report treats it: Q (quantified), D (discussed and bearing on the decision), M (mentioned only), X (absent), plus a flag for dismissal without evidence. Prediction: T requirements reach Q, while U requirements end at M or X. Limitations: N=14 runs, one coder (a second blind coder is needed), and the task briefs were themselves LLM-classified.

## Study B: form-of-information manipulation (pilot running)
Four HEP decision vignettes:
- S1 low-background scintillator: resolution vs radiopurity
- S2 HL-LHC pixel sensor: resolution vs end-of-life radiation tolerance
- S3 LAr photon detector: light yield vs cryogenic reliability
- S4 analysis selection: stat-only significance vs data/MC mismodelling

In each vignette, criterion 1 comes "from simulation" and criterion 2 from another source. We cross the form of each criterion (Numbers vs Prose), giving NN, NP, PN and PP, while holding information content, source labels and stated priorities fixed. Option letters are shuffled.
- *hard* framing (3 options): criterion 2 is binding, so choosing A is a normative error.
- *balanced* framing (3 options): there is a compromise option B. The smoke test showed ceiling/compromise behaviour (Haiku 5.5 chose B in 32/32).
- *tradeoff2* (2 options, equal weight): this is the sensitive design. The McNamara prediction is P(A | NP) > P(A | PP) ≈ P(A | NN) > P(A | PN). Form effects are estimated as the metric-number effect and the constraint-number effect (logistic GLMM, scenario random effect).
- Secondary outcomes: does the justification mention criterion 2 (keyword screen now; a blind judge later), and is it dismissed?

## Study C: prospective agent study (planned)
This tests the agent-level mechanism Bisht et al. actually worry about. The agent has a simulation tool that returns numbers for criterion 1. Criterion 2 is stated once in the brief, and evidence on it sits in a document the agent can read but no tool turns into a number. Arms:
- (i) tool for criterion 1 only
- (ii) tools for both criteria
- (iii) tool for criterion 2 only
- (iv) no tools (bare backbone, which the APS paper showed is the necessary comparison)

Outcomes: the final choice, whether criterion 2 appears in the report, and whether the run's own success flag would pass a design that violates criterion 2. The tasks can reuse the HEP-Prov local agent harness (no Delta needed). The study is pre-registered before running, as with the hindsight study.

## Study D: field level (optional; most work)
Classify the HEPML Living Review entries by whether a public benchmark, dataset or scalar metric exists, and compare the topic shares against the priorities in P5 (2023) and the European Strategy update (2026). Is there over-representation of benchmark-amenable tasks (tagging, fast simulation, anomaly detection on LHCO), and has it changed over time? This is the HEP analogue of Hao et al. It is only worth doing if A–C show something.

## Disconfirmation is a result
HEP's systematics culture may protect against the fallacy. If B shows no form effect and A shows U requirements handled substantively, the paper reports that the McNamara concern does not transfer to HEP decision-making in current models, and locates where it does (if anywhere): for example only in agent runs (C), only in older backbones, or only when criterion 2 is less salient.
