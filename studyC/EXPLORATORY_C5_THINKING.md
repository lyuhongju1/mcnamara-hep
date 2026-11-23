# Exploratory arm C5: Sonnet 4.5 with extended thinking (written 2026-11-23, before any run)

Purpose: in C2 the Claude 5.5 models ran with adaptive reasoning, while Sonnet 4.5 ran without extended reasoning, so 87% vs 9% confounds model with reasoning mode. This arm runs Sonnet 4.5 WITH extended thinking (budget_tokens 4000, interleaved thinking) under the C2 confirmatory conditions.

This arm is exploratory: it was not pre-registered, and no confirmatory claim is made.
- Design: S5-S8 x SC and PN x salience H and L x evidence X x 4 reps = 64 runs.
- Output: out_c5think.
- Outcome: UM as in C2 (frozen keyword rule).
- Comparison: descriptive, against the C2 Sonnet 4.5 SC+PN runs (50+61 of 128) and the Claude 5.5 models (15 of 160), with Newcombe intervals.
- Interpretation:
  - If the UM rate stays high, reasoning mode does not explain the model difference.
  - If it falls near the Claude 5.5 rate, the C2 model contrast is confounded with reasoning, and the paper says so.
2026-11-23: C5 background run killed by OS memory pressure after 1/64; resumed in the foreground in small batches with unchanged run ids.

Result (2026-11-23, 64/64 runs, $15.15): UM 50/64 (SC 28/32, PN 22/32). Versus C2 Sonnet 4.5 without thinking (111/128): difference -0.09, Newcombe 95% CI -0.21 to 0.02. Versus the Claude 5.5 models (15/160): +0.69, CI 0.56 to 0.78. Reasoning mode does not explain the model contrast. Process note: the S6 PN batch overran the foreground time limit and finished in the background while the S7 batch ran. The run ids were disjoint and all 64 result files parse.
