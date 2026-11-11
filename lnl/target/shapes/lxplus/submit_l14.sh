#!/usr/bin/env bash
# L14 (2026-11-11): the flat 45° Al end cap of TARGET_REVIEW.md §6.1 in Geant4 (see l14_configs.sh).  As submit_l12.sh:
# per (config × detector) X17 m16.8, Born M1/E1 IPC at 18.15 and 15.1 (5 × 100k), 2e7 ⁸Be γ (EPC); the Cu K x-ray
# lines for the caps (big plastics).  Each cluster gets job priority PRIO (condor_prio -p), which only reorders
# dneff's own idle jobs.
#   RUN=L14t NJ=1 NEV=20000 NGAM=0 XRAYS=0 DETS=bigP SAMPLES=X17_m16.8 PRIO=12 bash submit_l14.sh    # smoke test
#   bash submit_l14.sh
cd /afs/cern.ch/work/d/dneff/git/x17_lnl/MX17_Full_Geant
source scripts/setup_lxplus.sh >/dev/null 2>&1
source ../analysis/l14_configs.sh
EXE=${EXE:-bin/mx17_full_sim_culiner_812488b}
[ -x $EXE ] || { echo "no $EXE"; exit 1; }
RUN=${RUN:-L14}; NJ=${NJ:-5}; NEV=${NEV:-100000}; NGAM=${NGAM:-10}; PRIO=${PRIO:-5}
sub() {
  for i in 1 2 3 4; do
    out=$(python3 scripts/submit_lnl.py --exe $EXE "$@" 2>&1); rc=$?
    echo "$out"
    if [ $rc -eq 0 ]; then
      cl=$(echo "$out" | grep -o 'submitted to cluster [0-9]*' | awk '{print $4}')
      [ -n "$cl" ] && condor_prio -p $PRIO $cl && echo "prio $PRIO cluster $cl $*" >> ../analysis/l14_clusters.txt
      return 0
    fi
    sleep 20
  done
  echo "FAILED $*"
}
for det in ${DETS:-bigP asb}; do
  [ $det = bigP ] && D="$BIGP" || D="$ASB"
  for k in ${KEYS:-cap45al400cu cap45al500cu cap45al400cu_ep03 ogAl400cu12}; do
    t=${k}_$det
    for s in ${SAMPLES:-X17_m16.8 M1_18.15 E1_18.15 M1_15.1 E1_15.1}; do
      sub --run $RUN --sample $s --tag $t --njobs $NJ --nevents $NEV -- ${CFG[$k]} $D
    done
    [ "$NGAM" -gt 0 ] && sub --run $RUN --sample gam_8Be --tag $t --njobs $NGAM --nevents 2000000 -- ${CFG[$k]} $D
  done
  if [ "${XRAYS:-1}" = 1 ] && [ $det = bigP ]; then
    for k in ${XKEYS:-cap45al400cu cap45al500cu}; do
      sub --run $RUN --sample gam_lib --tag xray_${k}_$det --njobs 4 --nevents 1000000 -- ${CFG[$k]} --gamma-lines $XRAY $D
    done
  fi
done
