
### All requirements (n=99)

| class | Q | D | M | X | n |
|---|---|---|---|---|---|
| T | 54 | 5 | 4 | 1 | 64 |
| T? | 8 | 4 | 5 | 1 | 18 |
| U? | 2 | 1 | 3 | 3 | 9 |
| U | 1 | 1 | 3 | 3 | 8 |
### PERF only (SPEC design bounds removed)

| class | Q | D | M | X | n |
|---|---|---|---|---|---|
| T | 41 | 1 | 4 | 1 | 47 |
| T? | 6 | 4 | 5 | 1 | 16 |
| U? | 2 | 1 | 3 | 3 | 9 |
| U | 1 | 1 | 3 | 3 | 8 |
### PERF, excluding context-only items

| class | Q | D | M | X | n |
|---|---|---|---|---|---|
| T | 36 | 1 | 3 | 0 | 40 |
| T? | 4 | 1 | 2 | 0 | 7 |
| U? | 2 | 1 | 0 | 0 | 3 |
| U | 1 | 1 | 3 | 1 | 6 |

### Per run (T-class Q/total | U-class [U,U?] D+/total)

| run | T: Q/n | T?: Q/n | U+U?: D-or-better/n | U+U? codes |
|---|---|---|---|---|
| celeritas_run_files_v4/calorimeter | 2/4 | 1/2 | 2/3 | R7:M R8:D R9:D |
| celeritas_run_files_v7/calorimeter | 5/6 | 1/2 | 0/3 | R7:M R10:X R11:M |
| celeritas_run_files_v4/emcal | 4/5 | 0/1 | 0/1 | R6:M |
| celeritas_run_files_v7/emcal | 5/6 | 0/0 | 0/0 |  |
| celeritas_run_files_v4/muon | 4/4 | 0/1 | 0/0 |  |
| celeritas_run_files_v7/muon | 7/7 | 0/1 | 0/0 |  |
| celeritas_run_files_v4/tof | 1/2 | 0/1 | 1/1 | R1:Q |
| celeritas_run_files_v7/tof | 3/3 | 0/1 | 1/1 | R1:Q |
| celeritas_run_files_v4/tracking | 4/4 | 0/1 | 0/1 | R6:M |
| celeritas_run_files_v7/tracking | 4/5 | 2/2 | 0/1 | R8:X |
| opticks_run_files_v5/darkside_lar | 1/3 | 2/2 | 0/2 | R4:X R7:X |
| opticks_run_files_v9/darkside_lar | 1/2 | 2/2 | 0/2 | R3:X R6:M |
| opticks_run_files_v5/detector | 2/2 | 0/0 | 1/1 | R3:Q |
| opticks_run_files_v9/detector | 2/2 | 0/0 | 0/1 | R3:X |
| opticks_run_files_v5/protodune_lar | 5/5 | 0/1 | 0/0 |  |
| opticks_run_files_v9/protodune_lar | 4/4 | 0/1 | 0/0 |  |
