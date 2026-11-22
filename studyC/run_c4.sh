#!/bin/sh
# Study C4 per PREREGISTRATION_C4.md. Re-invoking skips completed run ids.
P=../../GRACE_v2/.venv-grace/Scripts/python.exe
S=S5_fcal,S6_trigger,S7_gas,S8_rich
for pass in 1 2; do
  $P -I pipeline.py run --scenarios $S --arch SC,PN --evid X,Y --salience H --models claude-sonnet-4-5-20250929 --reps 5 --sym --out out_c4 --workers 2
  $P -I openai_runner.py run --scenarios $S --arch SC,PN --salience H --models gpt-5.5-2026-04-23 --reps 5 --sym --evid X --out out_c4gpt --workers 2
  $P -I openai_runner.py run --scenarios $S --arch SC,PN --salience H --models gpt-5.5-2026-04-23 --reps 5 --sym --evid Y --out out_c4gpt --workers 2
done
