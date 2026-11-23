# Physics agents and unmeasured requirements

This repository holds the data and code for the article *Physics Agents Report Unmeasured Requirements as Met. A Test of the McNamara Fallacy* (Hong Joo Ryoo, Johns Hopkins University). The manuscript itself is not included.

The question is whether language-model agents doing particle-physics design carry requirements that their tools cannot quantify through to their decisions, or whether they disregard such requirements or declare them satisfied.

## Contents

| Path | Study |
|---|---|
| `studyA/` | Blind re-coding of 16 archived GRACE detector-design runs (two independent model coders) |
| `studyB/` | Decision-level vignettes, numbers versus words (v1 and v2) |
| `studyC/` | Tool-using agents: the development pilot (C), the confirmatory studies C2, C3 and C4, the harnesses and the scenarios |
| `DESIGN.md`, `PILOT_RESULTS.md` | The original design and the pilot log |

### Confirmatory studies

All three were pre-registered and frozen before data collection.

| Study | Pre-registration | Freeze manifest | Deviations | Outputs | Test |
|---|---|---|---|---|---|
| C2, model and pipeline architecture | `studyC/PREREGISTRATION_C2.md` | `studyC/FREEZE_C2.md`, tag `c2-frozen` | `DEVIATIONS_C2.md` | `out_c2conf/` | `tests_c2.py` |
| C3, second provider and schema fix | `studyC/PREREGISTRATION_C3.md` | `studyC/FREEZE_C3.md`, tag `c3-frozen` | `DEVIATIONS_C3.md` | `out_c3gpt/`, `out_c3fixF1/`, `out_c3fixF2/` | `tests_c3.py` |
| C4, measurability-specificity control | `studyC/PREREGISTRATION_C4.md` | `studyC/FREEZE_C4.md` (commit "Freeze Study C4 pre-registration") | `DEVIATIONS_C4.md` | `out_c4/`, `out_c4gpt/` | `tests_c4.py` |

Development data (`out_pilot/`, `out_c2pilot/`, and every `*smoke*` directory) are excluded from all confirmatory analyses.

Each run directory holds `transcript.jsonl`, which records every request setting, response, tool call and tool result, and `result.json`, which holds the submission and the derived outcomes.

## Reproducing the numbers

You need Python 3.12 with `anthropic`, `openai`, `scipy`, `numpy` and `matplotlib`. Run the scripts from `studyC/` with `python -I`.

```
python -I tests_c2.py        # C2 hypotheses H1, H2
python -I tests_c3.py        # C3 hypotheses H3, H4, H5
python -I tests_c4.py        # C4 hypothesis H6
python -I analyze_c2.py out_c2conf
python -I validate_r2.py     # outcome-coding validation (calls the API)
```

Re-running the agents requires API keys (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`) and reproduces the procedure, not identical samples.

## Licence

The data (transcripts, results, coding) are licensed under CC BY 4.0. The scripts are licensed under the MIT licence. See `LICENSE`.

## Funding and disclosure

This work was supported by the NSF Graduate Research Fellowship Program under Grant No. DGE-2139757, and by API credits from Anthropic's AI for Science program. Three of the five models evaluated in the confirmatory studies are Anthropic products. The author is a co-developer of GRACE, whose archived runs are analysed in Study A.
