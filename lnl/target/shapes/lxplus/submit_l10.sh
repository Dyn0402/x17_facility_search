#!/usr/bin/env bash
# L10: the two LNL target designs in Geant4 (x17_facility_search lnl/target/SHAPES_GEANT.md).
# Per (shape config × detector): X17 m16.8, Born M1/E1 IPC at 18.15 (γ0) and 15.1 (γ1), 2e7 ⁸Be γ (EPC);
# plus the γ-line response library (26 lines) for two shapes.  Detectors: big plastics (bigP), as built (asb).
cd /afs/cern.ch/work/d/dneff/git/x17_lnl/MX17_Full_Geant
source scripts/setup_lxplus.sh >/dev/null 2>&1
source ../analysis/l10_configs.sh
EXE=${EXE:-bin/mx17_full_sim_shapes_$(git rev-parse --short HEAD)}
[ -x $EXE ] || { mkdir -p bin; cp build/mx17_full_sim $EXE; }
sub() { for i in 1 2 3 4; do python3 scripts/submit_lnl.py --exe $EXE "$@" && return 0; sleep 20; done; echo "FAILED $*"; }
for det in ${DETS:-bigP asb}; do
  [ $det = bigP ] && D="$BIGP" || D="$ASB"
  for k in ${KEYS:-${!CFG[@]}}; do
    t=${k}_$det
    sub --run L10 --sample X17_m16.8 --tag $t --njobs 5 --nevents 100000 -- ${CFG[$k]} $D
    sub --run L10 --sample M1_18.15 --tag $t --njobs 5 --nevents 100000 -- ${CFG[$k]} $D
    sub --run L10 --sample E1_18.15 --tag $t --njobs 5 --nevents 100000 -- ${CFG[$k]} $D
    sub --run L10 --sample M1_15.1 --tag $t --njobs 5 --nevents 100000 -- ${CFG[$k]} $D
    sub --run L10 --sample E1_15.1 --tag $t --njobs 5 --nevents 100000 -- ${CFG[$k]} $D
    sub --run L10 --sample gam_8Be --tag $t --njobs 10 --nevents 2000000 -- ${CFG[$k]} $D
  done
  for k in ${LIBKEYS:-dome200 win45d200}; do
    sub --run L10 --sample gam_lib --tag ${k}_$det --njobs 26 --nevents 1000000 -- ${CFG[$k]} $D
  done
done
