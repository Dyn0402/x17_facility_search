#!/usr/bin/env bash
# L9, second round: geometry variants of the 1 mm diamond (TARGET_OPTIONS.md §7.2)
cd /afs/cern.ch/work/d/dneff/git/x17_lnl/MX17_Full_Geant
source scripts/setup_lxplus.sh >/dev/null 2>&1
source ../analysis/l9_configs.sh
EXE=bin/mx17_full_sim_lnltgt_97a41fa
sub() { for i in 1 2 3 4; do python3 scripts/submit_lnl.py --exe $EXE "$@" && return 0; sleep 20; done; echo "FAILED $*"; }
for k in ${L9B:-li20_dia1_y180 li20_dia1_r8 li20_dia1_r8_y120}; do
  v=CFG2_$k; a=${!v}
  sub --run L9 --sample X17_m16.8 --tag $k --njobs 5 --nevents 100000 -- $a $BIGP
  sub --run L9 --sample M1_18.15 --tag $k --njobs 5 --nevents 100000 -- $a $BIGP
  sub --run L9 --sample E1_18.15 --tag $k --njobs 5 --nevents 100000 -- $a $BIGP
  sub --run L9 --sample gam_8Be --tag $k --njobs 10 --nevents 2000000 -- $a $BIGP
done
