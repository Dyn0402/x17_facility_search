#!/usr/bin/env bash
# submit_all.sh -- the Demokritos Geant4 campaign D1-D3 (GEANT_PREP.md §3), 2026-10-19.
# Run on lxplus from the demokritos worktree:
#   cd /afs/cern.ch/work/d/dneff/git/x17_demok/MX17_Full_Geant && bash <this> [--dry-run]
# Cosmics are not rerun: the LNL L4 samples (same apparatus) are re-cut in the analysis.
set -e
EXE=bin/mx17_full_sim_demok_4bad297
DRY=${1:-}
S="python3 scripts/submit_demokritos.py --exe $EXE $DRY"
BIGP="--big-plastic 75 75 5 --no-ls --sipm-readout 20 0"
# target configurations: tag -> extra args (the baseline is TiT 2300 ug/cm2 on Cu 50 um)
declare -A CFG=(
  [cu50]=""
  [cu1000]="--backing Cu:1000"
  [cu1000_y120]="--backing Cu:1000 --target-y 120"
)
for t in cu50 cu1000 cu1000_y120; do
  for hw in "" _bigP; do
    xa="${CFG[$t]}"; [ -n "$hw" ] && xa="$xa $BIGP"
    # D1: X17 at W = 20.49 MeV (E_p = 900 keV), m = 16.94 (ATOMKI 4He)
    $S --run D1 --sample X17_m16.94 --tag $t$hw --njobs 5 --nevents 100000 -- $xa
    # D2: Born E1 IPC at 20.49, generated above 70 deg (normalise with the Born fraction)
    $S --run D2 --sample E1_20.49 --tag $t$hw --njobs 10 --nevents 100000 -- $xa --ipc-min-open 70
  done
  # D3: the 20.49 MeV gamma line from the beam spot: EPC in the tritide / backing / holder / chamber
  $S --run D3 --sample gam_He4 --tag $t --njobs 20 --nevents 500000 -- ${CFG[$t]}
done
# the X17 mass dependence, thin backing only
for m in 16.7 17.2; do
  for hw in "" _bigP; do
    xa=""; [ -n "$hw" ] && xa="$BIGP"
    $S --run D1 --sample X17_m$m --tag cu50$hw --njobs 3 --nevents 100000 -- $xa
  done
done
# an unbiased IPC sample to check the >70 deg normalisation
$S --run D2 --sample E1_20.49 --tag cu50_all --njobs 2 --nevents 100000
