#!/usr/bin/env bash
# wall_pipe.sh -- condor: wall_reduce.py for every file of the given LNL samples
# (needs the lnl_pipe parts_lnl/ already there), then a light merge.  Idempotent.
#
#   bash wall_pipe.sh reduce L1/X17_m16.7_bigP L4/cosmic_bigP ...
#   bash wall_pipe.sh status L1/X17_m16.7_bigP ...
#   bash wall_pipe.sh merge  L1/X17_m16.7_bigP ...     # interactive, small
#
# Parts: $E/<run>/<sample>/parts_wall/<stem>.npz ; merged: $E/sel_wall/<run>_<sample>_wall.npz
set -e
A=/afs/cern.ch/work/d/dneff/git/x17_lnl/analysis/sipm_wall
E=/eos/experiment/ntof/data/x17/lnl
J=/afs/cern.ch/user/d/dneff/condor/lnl/sipm_wall
LCG=/cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
cmd=$1; shift
csub() { for i in 1 2 3 4; do condor_submit "$1" > $J/last_submit.txt 2>&1 && { tail -1 $J/last_submit.txt; return 0; }; sleep 20; done; tail -5 $J/last_submit.txt; return 1; }
mkdir -p $J/logs $E/sel_wall
cd $J
case $cmd in
status)
  for d in "$@"; do printf "%-26s parts_lnl %3s  parts_wall %3s  merged %s\n" $d $(ls $E/$d/parts_lnl/*.npz 2>/dev/null | wc -l) \
      $(ls $E/$d/parts_wall/*.npz 2>/dev/null | wc -l) $([ -e $E/sel_wall/${d//\//_}_wall.npz ] && echo yes || echo no); done ;;
reduce)
  cat > $J/reduce.sh <<EOS
#!/usr/bin/env bash
set -e
source $LCG > /dev/null
python3 $A/wall_reduce.py "\$1" "\$2" -o "\$3"
EOS
  chmod +x $J/reduce.sh
  SUB=$J/reduce_$(date +%H%M%S).sub
  {
  echo "executable = $J/reduce.sh"
  echo 'output = '$J'/logs/$(tag).out'
  echo 'error = '$J'/logs/$(tag).err'
  echo "log = $J/logs/reduce.log"
  echo '+JobFlavour = "longlunch"'
  echo "request_memory = ${MEM:-6000}"
  echo 'requirements = (OpSysAndVer =?= "AlmaLinux9")'
  echo "should_transfer_files = NO"
  echo 'arguments = $(inp) $(prt) $(out)'
  echo "queue inp,prt,out,tag from ("
  for d in "$@"; do
    mkdir -p $E/$d/parts_wall
    for p in $E/$d/parts_lnl/*.npz; do
      s=$(basename $p .npz); o=$E/$d/parts_wall/$s.npz
      [ -e $o ] && continue
      grep -q "${d//\//_}_$s\$" $J/submitted.txt 2>/dev/null && continue
      echo "  $E/$d/$s.root, $p, $o, ${d//\//_}_$s"
    done
  done
  echo ")"
  } > $SUB
  n=$(grep -c '.root,' $SUB || true)
  echo "$n reduce jobs"
  if [ "$n" -gt 0 ]; then
    csub $SUB && grep '.root,' $SUB | awk -F', ' '{print $4}' >> $J/submitted.txt
  fi ;;
merge)
  source $LCG > /dev/null
  for d in "$@"; do
    python3 $A/wall_merge.py $E/$d/parts_wall/*.npz -o $E/sel_wall/${d//\//_}_wall.npz
  done ;;
esac
