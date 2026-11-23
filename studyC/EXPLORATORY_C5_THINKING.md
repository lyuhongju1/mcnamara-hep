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
