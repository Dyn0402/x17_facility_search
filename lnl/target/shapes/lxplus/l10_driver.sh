#!/usr/bin/env bash
# l10_driver.sh -- reduce, time, merge every L10 sample as its simulation finishes (lnl_pipe.sh), and the
# per-channel singles (l10_singles.py) of the γ samples.  Merged tables -> $E/target/sel_l10/.  Run with nohup.
A=/afs/cern.ch/work/d/dneff/git/x17_lnl/analysis
E=/eos/experiment/ntof/data/x17/lnl
export SEL=$E/target/sel_l10
mkdir -p $SEL
for it in $(seq 1 120); do
  all=1
  for d in $E/L10/*; do
    s=L10/$(basename $d)
    nj=$(sed -n 2p $d/RUN_INFO.txt | awk '{print $1+0}')
    ns=$(grep -l "Run Summary" $d/*_job*.log 2>/dev/null | wc -l)
    case $s in *gam_*) bash $A/l10_sng.sh $s > /dev/null 2>&1 ;; esac
    nsg=$(ls $d/parts_sng/*.npz 2>/dev/null | wc -l)
    case $s in *gam_lib*) [ "$nsg" -eq "$nj" ] || all=0; continue ;; esac
    case $s in *gam_*) [ "$nsg" -eq "$nj" ] || all=0 ;; esac
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
