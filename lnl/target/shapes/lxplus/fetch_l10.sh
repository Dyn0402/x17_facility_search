#!/usr/bin/env bash
# fetch_l10.sh -- merge the L10 singles libraries on lxplus, then copy them and the merged L10 tables
# (SHAPES_GEANT.md) from EOS to lnl/target/shapes/sel/ (gitignored).
set -e
D=$(cd "$(dirname "$0")/.." && pwd)/sel
mkdir -p "$D"
ssh lxplus 'source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh >/dev/null;
  E=/eos/experiment/ntof/data/x17/lnl; A=/afs/cern.ch/work/d/dneff/git/x17_lnl/analysis
  for d in $E/L10/gam_*; do s=$(basename $d); o=$E/target/sel_l10/L10_${s}_sng.npz
    nj=$(sed -n 2p $d/RUN_INFO.txt | awk "{print \$1+0}"); np=$(ls $d/parts_sng/*.npz 2>/dev/null | wc -l)
    [ "$np" -eq "$nj" ] && [ ! -e $o ] && python3 $A/l10_sng_merge.py $d -o $o; done; true'
rsync -a --include='L10_*.npz' --exclude='*' lxplus:/eos/experiment/ntof/data/x17/lnl/target/sel_l10/ "$D/"
ls -la "$D" | tail -n +1 | wc -l
