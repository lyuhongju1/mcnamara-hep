#!/bin/sh
# Confirmatory C2 per PREREGISTRATION_C2.md. Re-invoking skips completed run ids, so passes 2-3 re-run failures.
P=../../GRACE_v2/.venv-grace/Scripts/python.exe
S=S5_fcal,S6_trigger,S7_gas,S8_rich
for pass in 1 2 3; do
  $P -I pipeline.py run --scenarios $S --arch SC,PN,PT --evid X --salience H,L --models claude-sonnet-4-5-20250929 --reps 8 --out out_c2conf --workers 4
  $P -I pipeline.py run --scenarios $S --arch SC,PN --evid X --salience H,L --models claude-sonnet-5-5,claude-haiku-5-5 --reps 5 --out out_c2conf --workers 4
  $P -I pipeline.py run --scenarios $S --arch SC,PN --evid M --salience H,L --models claude-sonnet-4-5-20250929 --reps 1 --out out_c2conf --workers 4
done
