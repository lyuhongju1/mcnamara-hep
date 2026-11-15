# Pilot results (2026-11-15)

## Study A: GRACE corpus, retrospective (studyA/, single unblinded coder)
- 16 detector runs coded (the 2 higgs ML runs were excluded); 80 requirements.
- Tool-quantifiable requirements (T) reached a number in 87% of cases (41/47). Non-quantifiable ones (U/U?) reached substantive discussion in 29% (5/17).
- No requirement was explicitly dismissed. Instead, U requirements were moved to "Limitations/Future work" and a design was recommended without them.
- Proxy substitution: "cost-effectiveness" was reported as 1.275 ± 0.128, computed from efficiency × uniformity per sensor with no cost input (opticks v5 detector; spot-checked).
- Measurable-but-off-goal optimization: the muon v7 report recommends planar on muon energy resolution, which wasn't asked for. The stated goal was pion rejection, and the thick absorber does 3x better on it (spot-checked).

## Study B: form-of-information vignettes (studyB/, 704 calls, 4 Claude models)
- Hard and 3-option balanced framings were at ceiling: the middle or compliant option was chosen almost always (the A-option was never chosen in any of 384 trials).
- 2-option trade-off, P(choose the simulation-best option A):

| model | NN | NP | PN | PP |
|---|---|---|---|---|
| Haiku 5.5 | .05 | .00 | .20 | .00 |
| Sonnet 4.5 | .30 | .00 | .10 | .05 |
| Sonnet 5.5 | .45 | .05 | .50 | .00 |
| Opus 5.5 | .50 | .00 | .50 | .00 |

- This is the reverse of the McNamara prediction. The form of the *constraint* drives the choice: when it is stated in prose, models protect it. The form of the metric barely matters.
- Mechanism, from reading the responses: r2 is worded as a threshold ("low enough"). Prose hides the magnitude, so the model treats it as a possible fail. Numbers let it judge "0.6 counts/kg/day is low enough". So the prose and number versions are NOT information-equivalent. This is a design flaw, to be fixed by stating the threshold status in both forms or by using non-threshold wording.
- Scenario effects: S2 (radiation tolerance) and S4 (data/MC mismodelling) produce C almost always. HEP norms are strongly present.
- Models recognise real materials (Opus named LaBr3(Ce) and its 138La/227Ac activity), so the vignettes are not disguised (cf. the hindsight twins).

## Reading
With the information in front of them, current models do not neglect the unquantified criterion; if anything, they over-weight verbal risk. The McNamara pattern appears in the *agent workflow* (Study A): what never gets measured never enters the decision, gets proxied, or is deferred to future work. Study C (prospective agent runs, with tool availability manipulated) is therefore the decisive test.

---
# Round 2 (2026-11-15, later)

## Study B v2: pass/fail information matched; omission forms added (360 calls; Haiku/Sonnet/Opus 5.5)
P(choose the simulation-best option A), pooled: NN .43, NP .17, PN .30, PP .03, N0 .90, P0 .85.
- **Metric in numbers** raises P(A) by about 0.13 (NN vs PN; NP vs PP). This is a small effect in the McNamara direction.
- **Constraint in numbers** raises P(A) by about 0.27 (NN vs NP; PN vs PP). In words, a constraint is protected; in numbers it is traded off. This is the larger effect, and it runs against the McNamara prediction.
- **Constraint evidence absent (N0/P0):** A is chosen 85–90% of the time. The judge (Sonnet 5.5) codes 100% as noting the missing evidence and making the choice conditional; "assumes met" is 0–15%. Call this "flag and proceed": it is rational for a single decision.
- Scenario effects are large. S4 (data/MC) and S3 trade off most; S2 (radiation tolerance) least.

## Study C pilot: agent with tools (144 runs, $5.75)
- **Arms M/MC/C/D** (the r2 memo is in the document store in every arm): 0/96 violations. The memo is read in 98% of runs regardless of the tools, and the r2 tool is used when it is offered. **Tool affordance alone does not produce the fallacy in a small, clean environment.** The pre-registered H1 would be at ceiling, so it is NOT run as drafted.
- **Arm X** (r2 evidence exists nowhere, as in GRACE): 48/48 recommend the r1-best option A. r2 is marked "unknown" in 46/48 (2 omitted, 0 claimed "met"), and the justification flags the gap in 44/48. Example (Opus, vague brief): "IMPORTANT CAVEAT: none of the project documents give data on the crystals' own radioactivity... That is the deciding factor."
- So current models in a single-context harness do the honest version: flag and proceed. GRACE (Sonnet 4, Jan 2026) did worse: no flag in 71% of U requirements, plus a fabricated proxy for cost.

## Revised hypothesis
The McNamara pattern in GRACE is an **architectural** property, not a judgement bias. In GRACE v1, results pass between steps as numbers: the scratchpad holds 15 `k=v` entries, step outputs are cut to 500 characters, and the report is written from the numeric results (V2_PLAN §1). A caveat about an unmeasured requirement has no slot in a number-only interface, so it is lost before the report is written. A second candidate is model generation (Sonnet 4 vs 5.5).

Next test (C2): the same scenarios and arm X, with the harness architecture manipulated:
- (a) a single-context agent (as now)
- (b) a GRACE-style pipeline: planner, then executor steps, then reporter, where only numeric key=value results pass between steps
- (c) the same pipeline with free-text notes allowed

Model contrast: Sonnet 4.5 retires on 2026-11-30, so any older-model arm has to run before then.
