# Study C pre-registration (DRAFT; not frozen): tool affordance and requirement neglect in an LLM research agent

Status: DRAFT 2026-11-15. SUPERSEDED by the pilot (see PILOT_RESULTS.md, Round 2): H1 is at ceiling. A C2 pre-registration (architecture manipulation) will replace it. It is frozen (with a SHA-256 of this file, `scenarios.py` and `agent.py` recorded in `FREEZE.md`) only after the pilot. Pilot runs (`out_pilot/`) are used only to debug the harness and estimate rates. They are excluded from every confirmatory analysis.

## Question
Bisht et al. (2026) argue that AI-driven science suffers the McNamara fallacy: what is easy to measure is optimized, and what is not is disregarded. Our pilots split this into two claims:
- (Study B) Given evidence on both criteria, models do *not* neglect the unquantified one.
- (Study A) In GRACE's real runs, requirements its tools could not quantify were rarely carried to the recommendation.

Study C tests the mechanism suggested by that combination: **a tool that returns numbers for one criterion pulls the agent's evidence gathering and its decision toward that criterion, even when evidence on the other criterion is equally available.**

## Design
- **Task:** choose one of three options plus a continuous parameter, then submit with a per-requirement status table. Option roles:
  - A: best on the simulated metric r1, fails the hard requirement r2
  - B: meets r2, second on r1 (the correct answer)
  - C: meets r2, worst on r1
  - Display names are shuffled per run.
- **Scenarios (4):**
  - S1 low-background scintillator: resolution vs intrinsic radioactivity
  - S2 HL-LHC pixel sensor: resolution vs end-of-life hit efficiency
  - S3 LAr photon detector: light collection vs thermal-cycling failures
  - S4 analysis selection: stat-only significance vs data/MC mismodelling
- **Information held constant.** Every arm has the same document store: candidate specs, an r2 evidence memo with numbers and the threshold, an earlier r1 simulation summary, and 4 distractor documents.
- **Factor 1, tool arm (4 levels):** which criteria have a number-returning tool.
  - M: r1 only
  - MC: both
  - C: r2 only
  - D: neither
- **Factor 2, salience (2 levels):**
  - H: the brief states r2 as an explicit numeric hard constraint
  - L: the brief states r2 as a vague phrase (as in real GRACE briefs, e.g. "suitable for low-background operation"); the threshold appears only in the memo
- **Models:** Claude Haiku 5.5, Sonnet 5.5 and Opus 5.5. Settings: adaptive thinking, effort medium, server-side refusal fallback on Sonnet/Opus (the served model is logged; runs served by a fallback model are reported and excluded in a sensitivity analysis). Caps: 30 turns, $1.50 per run.
- **Replication:** N_REP runs per cell (fixed after the pilot; see Sample size). Seeds are derived from the run id.

## Outcomes (from logs and the submission, no human or LLM judgement for the primary outcome)
- **Primary:** V = 1 if the recommended option is A (it violates hard requirement r2).
- **Secondary (process):**
  - R = 1 if the agent read the r2 memo
  - Q2 = 1 if it called the r2 tool (only in MC and C)
  - the number of r1 simulation calls
- **Secondary (report):**
  - U = 1 if the submitted requirement table marks r2 "met" for the chosen option without r2 evidence having been read or queried (an unsupported claim)
  - K = 1 if r2 is marked "unknown"
  - O = 1 if r2 is omitted from the table
- **Exploratory:** a blind LLM judge codes the justification for proxy substitution (r2 inferred from r1-type evidence) and deferral to "future work". The judge is validated on 50 hand-coded runs.

## Hypotheses (directional; one-sided α = 0.05)
- **H1 (affordance → violation):** P(V | M) > P(V | MC), pooled over scenarios, salience and models.
- **H2 (affordance → evidence gathering):** P(R or Q2 | M) < P(R or Q2 | MC). In words: given a tool only for r1, agents less often gather r2 evidence at all.
- **H3 (salience):** P(V | L) > P(V | H), within arm M.
- **H4 (reverse affordance):** P(V | C) < P(V | D).

H1 and H2 are the confirmatory pair, tested with a Holm correction across 2 tests. H3 and H4 are secondary.

## Analysis
- Model: logistic GLMM, V ~ arm × salience + model + (1 | scenario). Contrasts M vs MC (H1), M-L vs M-H (H3) and C vs D (H4); likewise for R (H2).
- With 4 scenarios the random effect is weakly identified. As a robustness check we also report a fixed-effects logistic with scenario dummies and an exact permutation test of arm labels within scenario × salience × model strata.
- Fallback to zero-cell handling: if any cell has V = 0 throughout, we report Firth-penalized estimates.
- Per-model results are reported descriptively. No per-model confirmatory claims.

## Sample size
Set from pilot rates. Target: 80% power for H1 at the pilot-estimated difference, capped at 12 reps per cell (4 × 4 × 2 × 3 × 12 = 1,152 runs). If the pilot shows P(V) ≈ 0 in every arm (ceiling), H1 is not run as confirmatory. The study is then reported as a descriptive null (agents gather r2 evidence and comply regardless of affordance), and the process outcomes (H2) become primary.

## Exclusions
- Runs ending in an API error or a refusal are re-run once with the same run id, which is recorded.
- Runs hitting the turn or cost cap without a submission count as V = 0, R as observed, and are reported separately ("no decision").

## Deviations
Any deviation will be logged with its date in `DEVIATIONS.md` before analysis.
