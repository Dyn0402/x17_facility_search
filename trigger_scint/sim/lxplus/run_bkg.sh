#!/usr/bin/env bash
# Run bkg_reach.py per geometry as soon as its inputs are merged (parallel).
cd /afs/cern.ch/work/d/dneff/git/x17_trig/analysis
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh > /dev/null
E=/eos/experiment/ntof/data/x17/ill/TB
O=$E/analysis; mkdir -p $O
ARGS="--gates 0 10 25 50 100 --menus sipm2 strict --ecuts 13 --nrates 10 --air 1 0.1"
need() {  # geometry -> marker files that must exist
  case $1 in
    asbuilt) echo "";;
    P2) echo "$E/contracts/C1_P2/.merged $E/contracts/C1w_P2/.merged $E/contracts/C1g_P2/.merged $E/contracts/K1_P2/.merged $E/summary/P2_E0/.merged";;
    *)  echo "$E/contracts/C1_$1/.merged $E/contracts/C1w_$1/.merged $E/contracts/C1g_$1/.merged $E/contracts/K1_P5/.merged $E/summary/$1_E0/.merged $E/summary/$1_X17/.merged $E/summary/$1_M1/.merged";;
  esac
}
for g in ${@:-asbuilt P2 P5 P5L P5B}; do
  (
    for i in $(seq 1 200); do
      ok=1; for f in $(need $g); do [ -e $f ] || ok=0; done
      [ $ok = 1 ] && break; sleep 300
    done
    python3 -u bkg_reach.py --geoms $g $ARGS -o $O > $O/$g.log 2>&1
  ) &
done
wait
echo "run_bkg done $(date)" >> $O/done.log
