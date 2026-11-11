#!/usr/bin/env bash
# fetch_l14.sh -- as fetch_l13.sh for L14 (the flat Al end cap): merge any finished singles library on
# lxplus that l14_driver.sh has not merged yet, then copy the merged L14 tables from EOS to
# $WORK_DATA/x17_facility_search/lnl_sel/ (default /media/ucla/work/...; L14_DEST=<dir> overrides).
set -e
D=${L14_DEST:-${WORK_DATA:-/media/ucla/work}/x17_facility_search/lnl_sel}
mkdir -p "$D"
ssh lxplus 'source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh >/dev/null;
  E=/eos/experiment/ntof/data/x17/lnl; A=/afs/cern.ch/work/d/dneff/git/x17_lnl/analysis
  for d in $E/L14/gam_*; do s=$(basename $d); o=$E/target/sel_l14/L14_${s}_sng.npz
    nj=$(sed -n 2p $d/RUN_INFO.txt | awk "{print \$1+0}"); np=$(ls $d/parts_sng/*.npz 2>/dev/null | wc -l)
    [ "$np" -eq "$nj" ] && [ ! -e $o ] && python3 $A/l10_sng_merge.py $d -o $o; done; true'
rsync -a --include='L14_*.npz' --exclude='*' lxplus:/eos/experiment/ntof/data/x17/lnl/target/sel_l14/ "$D/"
ls -la "$D" | grep L14_
