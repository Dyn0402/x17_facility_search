#!/usr/bin/env bash
# fetch_sel.sh -- copy the merged Birmingham tables (B1-B3 targets, R2 wall leakage, R3 room return) and the
# wall-stage plane records from EOS into birmingham/geant/sel/ (gitignored).
cd "$(dirname "$0")"
mkdir -p sel
rsync -t --info=stats0 "lxplus:/eos/experiment/ntof/data/x17/bham/sel/*.npz" sel/
rsync -t --info=stats0 "lxplus:/eos/experiment/ntof/data/x17/bham/R1/guns/*planes.npz" "lxplus:/eos/experiment/ntof/data/x17/bham/R1/guns/merge_*.txt" sel/ 2>/dev/null
ls sel | wc -l
