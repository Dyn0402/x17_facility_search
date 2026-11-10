#!/usr/bin/env bash
# fetch_l13.sh -- as fetch_l12.sh for L13 (high-statistics as-built backgrounds): merge any finished singles library on
# lxplus that l13_driver.sh has not merged yet, then copy the merged L13 tables from EOS to
# $WORK_DATA/x17_facility_search/lnl_sel/ (default /media/ucla/work/...; L13_DEST=<dir> overrides).
set -e
D=${L13_DEST:-${WORK_DATA:-/media/ucla/work}/x17_facility_search/lnl_sel}
mkdir -p "$D"
ssh lxplus 'source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh >/dev/null;
  E=/eos/experiment/ntof/data/x17/lnl; A=/afs/cern.ch/work/d/dneff/git/x17_lnl/analysis
  for d in $E/L13/gam_*; do s=$(basename $d); o=$E/target/sel_l13/L13_${s}_sng.npz
    nj=$(sed -n 2p $d/RUN_INFO.txt | awk "{print \$1+0}"); np=$(ls $d/parts_sng/*.npz 2>/dev/null | wc -l)
    [ "$np" -eq "$nj" ] && [ ! -e $o ] && python3 $A/l10_sng_merge.py $d -o $o; done; true'
rsync -a --include='L13_*.npz' --exclude='*' lxplus:/eos/experiment/ntof/data/x17/lnl/target/sel_l13/ "$D/"
ls -la "$D" | grep L13_
