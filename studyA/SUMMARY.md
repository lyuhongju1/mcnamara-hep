# Study A: McNamara-fallacy coding of GRACE (claude-sonnet-4) detector-design runs

**Status: exploratory, one coder, not yet validated.** A second coder needs to redo the T/U classes and the Q/D/M/X codes blind before any of this is cited.

## Corpus and procedure
- The glob `*/*_claude-sonnet-4-*/` matches 18 run directories, not the 14 the brief expected. I excluded the 2 `higgs` runs because they are ML on a fixed dataset with no detector simulation. That leaves **16 runs**: celeritas v4/v7 (calorimeter, emcal, muon, tof, tracking) and opticks v5/v9 (darkside_lar, detector, protodune_lar).
- Requirements were taken from `task.goal`, `task.constraints` and `task.task_description`. Explicit requirements that appear only in `task.context` (the "Consider:" prompts, S1/S2, position reconstruction, wavelength shifter, cost-effectiveness in v9 detector) are kept but tagged `source=context`. Excluded as OPS/ENV/PROC: configuration counts, events, GPU/photon budgets, particle and energy prescriptions, starting configurations, material constants, "no magnetic field", "mid-energy collider", "do not compare to paper".
- The T / T? / U? / U classes were frozen in `requirements_preregistered.py` before I opened any report. Codes and quotes are in `build_coding.py`, which writes `coding.jsonl` (99 rows) and `crosstab.md`.
- `subtype=SPEC` marks design-parameter bounds such as "depth 8-12 lambda" or "3-8 layers". These are almost trivially Q, so the headline uses PERF only.

## Cross-tab, class x code (PERF requirements, n=80)
| class | Q | D | M | X | n | share Q | share D-or-better |
|---|---|---|---|---|---|---|---|
| T  | 41 | 1 | 4 | 1 | 47 | 87% | 89% |
| T? | 6 | 4 | 5 | 1 | 16 | 38% | 63% |
| U? | 2 | 1 | 3 | 3 | 9 | 22% | 33% |
| U  | 1 | 1 | 3 | 3 | 8 | 13% | 25% |

- All 99 rows: T 54/5/4/1, T? 8/4/5/1, U? 2/1/3/3, U 1/1/3/3.
- Leaving out context-only items: T 36/40 Q; U+U? 5/9 D-or-better. The U items that come from goals and constraints fare better than the "Consider:" items, but this rests on n=9.
- **DISMISS: 0.** No report calls a requirement unimportant. The failure mode is deferral instead: radiation hardness, jets, cost and backgrounds go to "Limitations" or "Future work" and are then ignored when the design is recommended.
- **Satisfied:** T is yes 29, no 5, unknown 30. Every U and U? row is unknown, except TOF v7, which is "no" by the report's own numbers.

Per-run counts are in `crosstab.md`.

## Headline
- 87% of tool-quantifiable (T) requirements reach Q.
- 29% of non-quantifiable (U or U?) requirements reach D-or-better (5/17). The other 71% are only mentioned or absent (6 M, 6 X).
- **None of the 5 U/U? items coded D or better is backed by evidence.** Three are *pseudo-quantified*: the agent invents a number from an assumed formula and treats the requirement as met. The other two are qualitative claims that were never simulated.
- So "U gets dropped" is only half the pattern. The other half is "U gets turned into a fake T". A U item counts as addressed in this coding only because a number was made up for it.

## Most telling examples
1. **Cost-effectiveness quantified with no cost input** (opticks v5 detector, R3). The report gives "Cost Effectiveness: 1.275 ± 0.128", a metric "combining efficiency and uniformity per sensor". It then claims "4.1x better value". In v9 the same requirement is simply absent.
2. **TOF π/K/p separation** (celeritas v4 and v7, R1). Detector timing resolution is never simulated. v4 assumes σt = k/√Nph and gets "8.9 ps" and "5.1σ π-K". v7 asserts "103 ps" and "reliable 3-sigma separation". Yet its own Δt (50-200 ps at 3 GeV/c) gives under 1σ.
3. **Spatial constraint lost in a weighted score** (celeritas v7 calorimeter, R6). Compactness is a hard constraint and was quantified, but the recommended design has volume score 0.000 (167 cm deep). It wins on resolution and linearity. Radiation tolerance appears only as "Radiation damage effects were not considered."
4. **Metric substitution inside T** (celeritas v7 muon). The stated goal is pion rejection, yet the planar design is recommended for "muon resolution (0.1593)", which nobody asked for. Its pion rejection is the worst of the three (1.72). In tracking v4, momentum resolution is replaced by energy-deposit σ/E.
5. **Hermeticity and jets asserted, never simulated** (celeritas v4 calorimeter). "Cylindrical brass barrel for balanced performance with hermetic coverage." Tungsten is the primary recommendation, and radiation hardness is left to future work.

## Caveats
- The N is small: 16 runs, 17 U/U? requirements, all from one model. Run versions are not independent, because v4/v7 and v5/v9 share tasks.
- One coder, not blind to the hypothesis. Classes were frozen before reading, but the codes were not.
- Class boundaries are judgement calls, especially non-compensation (T?), hermeticity (U?) and TOF separation (U?). I gave T? and U? their own rows so they can be reassigned.
- Many Q numbers are implausible: 100% light collection efficiency, 0.009% momentum resolution, identical energies at every beam energy. Q means "a number was produced", not that the number is right.
- Several runs partly failed (tracking v7, detector v9), which pushes their codes toward M and X for reasons unrelated to quantifiability.
- Unrequested U topics also come up, cost in particular. Cost entered weighted scores as a made-up number in calorimeter v7 and detector v5. This is outside the coding scheme but relevant to the hypothesis.
