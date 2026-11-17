#!/bin/sh
# Study C3 per PREREGISTRATION_C3.md. Re-invoking skips completed run ids.
P=../../GRACE_v2/.venv-grace/Scripts/python.exe
S=S5_fcal,S6_trigger,S7_gas,S8_rich
for pass in 1 2; do
  $P -I openai_runner.py run --scenarios $S --arch SC,PN --salience H,L --models gpt-4.1-2025-04-14,gpt-5.5-2026-04-23 --reps 5 --out out_c3gpt --workers 2
  $P -I pipeline.py run --scenarios $S --arch SC,PN --evid X --salience H,L --models claude-sonnet-4-5-20250929 --reps 5 --fix F1 --out out_c3fixF1 --workers 2
  $P -I pipeline.py run --scenarios $S --arch SC,PN --evid X --salience H,L --models claude-sonnet-4-5-20250929 --reps 5 --fix F2 --out out_c3fixF2 --workers 2
done
