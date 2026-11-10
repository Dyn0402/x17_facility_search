#!/usr/bin/env bash
# L13 (2026-11-10): high-statistics as-built background MC for the floating-shape fit (see l13_configs.sh).
# Per config: Born M1/E1 IPC at 18.15 and 15.1 (NIPC x 100k pairs; L11/L12 had 5 jobs -> x30) and 8Be gamma lines
# for EPC (NGAM x 2M gammas; L11/L12 had 10 jobs -> x15).  No X17, no --ipc-min-open (biases thick targets).
# Each cluster gets job priority PRIO (condor_prio -p) so it runs ahead of dneff's own idle jobs; this only reorders
# dneff's queue, it never preempts running jobs.
#   RUN=L13t NIPC=2 NGAM=2 SAMPLES="M1_18.15 gam_8Be" bash submit_l13.sh     # smoke test
#   bash submit_l13.sh                                                       # the run
cd /afs/cern.ch/work/d/dneff/git/x17_lnl/MX17_Full_Geant
source scripts/setup_lxplus.sh >/dev/null 2>&1
source ../analysis/l13_configs.sh
EXE=${EXE:-bin/mx17_full_sim_culiner_812488b}
[ -x $EXE ] || { echo "no $EXE"; exit 1; }
RUN=${RUN:-L13}; NIPC=${NIPC:-150}; NGAM=${NGAM:-150}; PRIO=${PRIO:-10}
sub() {
  for i in 1 2 3 4; do
    out=$(python3 scripts/submit_lnl.py --exe $EXE "$@" 2>&1); rc=$?
    echo "$out"
    if [ $rc -eq 0 ]; then
      cl=$(echo "$out" | grep -o 'submitted to cluster [0-9]*' | awk '{print $4}')
      [ -n "$cl" ] && condor_prio -p $PRIO $cl && echo "prio $PRIO cluster $cl $*" >> ../analysis/l13_clusters.txt
      return 0
    fi
    sleep 20
  done
  echo "FAILED $*"
}
for k in ${KEYS:-ogCu200 ogAl300cu12r8m4}; do
  t=${k}_asb
  for s in ${SAMPLES:-M1_18.15 E1_18.15 M1_15.1 E1_15.1 gam_8Be}; do
    case $s in
      gam_*) sub --run $RUN --sample $s --tag $t --njobs $NGAM --nevents 2000000 -- ${CFG[$k]} $ASB ;;
      *)     sub --run $RUN --sample $s --tag $t --njobs $NIPC --nevents 100000 -- ${CFG[$k]} $ASB ;;
    esac
  done
done
