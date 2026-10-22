#!/usr/bin/env bash
# l9_driver.sh -- reduce, time and merge every L9 sample as its simulation finishes
# (lnl_pipe.sh is idempotent).  Merged tables -> $E/target/sel_l9/.  Run with nohup.
A=/afs/cern.ch/work/d/dneff/git/x17_lnl/analysis
E=/eos/experiment/ntof/data/x17/lnl
export SEL=$E/target/sel_l9
mkdir -p $SEL
for it in $(seq 1 60); do
  all=1
  for d in $E/L9/*; do
    s=L9/$(basename $d)
    nj=$(sed -n 2p $d/RUN_INFO.txt | awk '{print $1+0}')
    ns=$(grep -l "Run Summary" $d/*_job*.log 2>/dev/null | wc -l)
    [ -e $SEL/${s//\//_}_sel.npz ] && continue
    all=0
    [ "$ns" -eq "$nj" ] || continue
    bash $A/lnl_pipe.sh reduce $s > /dev/null 2>&1
    nt=$(ls $d/parts_time/*.npz 2>/dev/null | wc -l)
    if [ ! -d $d/parts_time ] || { [ "$nt" -lt "$nj" ] && [ ! -e $d/.time_submitted ]; }; then
      bash $A/lnl_pipe.sh time $s > /dev/null 2>&1 && touch $d/.time_submitted
    fi
    bash $A/lnl_pipe.sh merge $s 2>&1 | grep -v "not merging" | sed "s|^|$(date +%H:%M) |"
  done
  [ $all -eq 1 ] && { echo "all merged $(date)"; exit 0; }
  sleep 900
done
