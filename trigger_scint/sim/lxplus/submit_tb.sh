#!/usr/bin/env bash
# TB campaign: beam backgrounds, signal and cosmics for the big trigger plastics.
# G1 cell, all 20 SiPM bars, no LS.  Geometries:
#   P2   70 x 70 x 2 cm PVT           (the acceptance-only option)
#   P5   75 x 75 x 5 cm PVT           (the calorimetric option)
#   P5L  P5 + 2 mm 6LiF around each slab
#   P5B  P5 + 2 mm B4C  around each slab
# Outputs: /eos/experiment/ntof/data/x17/ill/TB/G1_<geom>_<kind>/
cd /afs/cern.ch/work/d/dneff/git/x17_trig/MX17_Full_Geant
source scripts/setup_lxplus.sh > /dev/null 2>&1
E=/eos/experiment/ntof/data/x17/ill
EXE=$PWD/bin/mx17_full_sim_trig3
LIB=$E/libs/C1_G1_gas.csv
COMMON="--no-ls --sipm-readout 20 0"
declare -A GEO=(
  [P2]="--big-plastic 70 70 2"
  [P5]="--big-plastic 75 75 5"
  [P5L]="--big-plastic 75 75 5 --plastic-shield LiF6:2"
  [P5B]="--big-plastic 75 75 5 --plastic-shield B4C:2"
)
sub() { python3 scripts/submit_ill.py --run TB --config G1 --exe $EXE "$@" 2>&1 | tail -1; }
for g in ${ONLY:-${!GEO[@]}}; do
  ga="${GEO[$g]} $COMMON"
  sub --tag ${g}_C1  --njobs 10 --nevents 10000000 --flavour workday --bias-ncapture 1e5 -- $ga
  sub --tag ${g}_C1w --njobs 10 --nevents 10000000 --flavour workday --bias-ncapture 1e5 -- \
      --bias-wall 300 --bias-thick 20 --bias-air 100 $ga
  sub --tag ${g}_C1g --njobs 20 --nevents 1000000  --flavour workday --bias-ncapture 1e7 -- $ga
  sub --tag ${g}_X17 --mode pairs --njobs 10 --nevents 100000 --flavour workday -- --ipc 0 --pair-vertex-lib $LIB $ga
  for ch in M1 E0; do
    sub --tag ${g}_$ch --mode pairs --njobs 10 --nevents 100000 --flavour workday -- \
        --ipc 1 --ipc-multipole $ch --pair-vertex-lib $LIB $ga
  done
done
for g in ${KONLY-P2 P5}; do
  sub --tag ${g}_K1 --mode pairs --njobs 40 --nevents 1300000 --flavour workday -- --cosmic ${GEO[$g]} $COMMON
done
