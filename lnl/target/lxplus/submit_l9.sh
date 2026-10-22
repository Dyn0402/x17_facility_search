#!/usr/bin/env bash
# L9: LNL target options (x17_facility_search lnl/target/TARGET_OPTIONS.md)
cd /afs/cern.ch/work/d/dneff/git/x17_lnl/MX17_Full_Geant
source scripts/setup_lxplus.sh >/dev/null 2>&1
source ../analysis/l9_configs.sh
EXE=bin/mx17_full_sim_lnltgt_97a41fa
sub() { for i in 1 2 3 4; do python3 scripts/submit_lnl.py --exe $EXE "$@" && return 0; sleep 20; done; echo "FAILED $*"; }
for k in "${!CFG[@]}"; do
  sub --run L9 --sample X17_m16.8 --tag $k --njobs 5 --nevents 100000 -- ${CFG[$k]} $BIGP
  sub --run L9 --sample M1_18.15 --tag $k --njobs 5 --nevents 100000 -- ${CFG[$k]} $BIGP
  sub --run L9 --sample E1_18.15 --tag $k --njobs 5 --nevents 100000 -- ${CFG[$k]} $BIGP
  sub --run L9 --sample gam_8Be --tag $k --njobs 10 --nevents 2000000 -- ${CFG[$k]} $BIGP
done
# the baseline's EPC at the same statistics, and the backing/film gamma lines (baseline geometry, big plastics)
sub --run L9 --sample gam_8Be --tag base --njobs 10 --nevents 2000000 -- $BIGP
sub --run L9 --sample gam_7Li --tag bklines --njobs 10 --nevents 1000000 -- --gamma-lines 0.136:1,0.478:1,0.843:1,1.369:1,2.37:1,4.44:1,5.6:1,8.06:1,10.76:1 $BIGP
