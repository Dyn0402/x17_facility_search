#!/usr/bin/env bash
# lnl_pipe.sh -- condor reduce (one job per ROOT file) and merge (one job per
# sample) for the LNL runs.  Idempotent: skips parts / merges that exist.
#
#   bash lnl_pipe.sh reduce L1/X17_m16.7 L2/M1_18.15 ...   # submit missing reduces
#   bash lnl_pipe.sh merge  L1/X17_m16.7 ...               # submit merges whose parts are complete
#   bash lnl_pipe.sh status L1/* L2/*
#
# Parts: $E/<run>/<sample>/parts_lnl/<stem>.npz ; merged: $E/sel/<run>_<sample>_sel.npz
set -e
A=/afs/cern.ch/work/d/dneff/git/x17_lnl/analysis
E=/eos/experiment/ntof/data/x17/lnl
J=/afs/cern.ch/user/d/dneff/condor/lnl/pipe
LCG=/cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
cmd=$1; shift
# condor_submit fails now and then from some lxplus nodes (an "AFS" policy
# banner): retry a few times before giving up
csub() { for i in 1 2 3 4; do condor_submit "$1" > $J/last_submit.txt 2>&1 && { tail -1 $J/last_submit.txt; return 0; }; sleep 20; done; tail -5 $J/last_submit.txt; return 1; }
mkdir -p $J/logs $E/sel
cd $J      # not EOS: condor_submit from an EOS cwd hangs or fails
done_sim() { grep -l "Run Summary" $E/$1/*_job*.log 2>/dev/null | wc -l; }
nroot() { ls $E/$1/*_t0.root 2>/dev/null | wc -l; }
njobs() { sed -n 2p $E/$1/RUN_INFO.txt 2>/dev/null | awk '{print $1+0}'; }   # "10 x 100000 pairs"
nparts() { ls $E/$1/parts_lnl/*.npz 2>/dev/null | wc -l; }

case $cmd in
status)
  for d in "$@"; do printf "%-28s sim %3s/%-3s parts %3s  sel %s\n" $d $(done_sim $d) $(nroot $d) $(nparts $d) \
      $([ -e $E/sel/${d//\//_}_sel.npz ] && echo yes || echo no); done ;;
reduce)
  cat > $J/reduce.sh <<EOS
#!/usr/bin/env bash
set -e
source $LCG > /dev/null
python3 $A/lnl_reduce.py "\$1" -o "\$2"
EOS
  chmod +x $J/reduce.sh
  tag=r$(date +%H%M%S)
  SUB=$J/reduce_$tag.sub
  {
  echo "executable = $J/reduce.sh"
  echo 'output = '$J'/logs/$(tag).out'
  echo 'error = '$J'/logs/$(tag).err'
  echo "log = $J/logs/reduce.log"
  echo '+JobFlavour = "longlunch"'
  echo "request_memory = ${MEM:-8000}"
  echo 'requirements = (OpSysAndVer =?= "AlmaLinux9")'
  echo "should_transfer_files = NO"
  echo 'arguments = $(inp) $(out)'
  echo "queue inp,out,tag from ("
  for d in "$@"; do
    mkdir -p $E/$d/parts_lnl
    for f in $E/$d/*_t0.root; do
      s=$(basename $f .root); o=$E/$d/parts_lnl/$s.npz; lg=${f%_t0.root}.log
      [ -e $o ] && continue
      grep -q "Run Summary" $lg 2>/dev/null || continue      # sim not finished
      grep -q "${d//\//_}_$s\$" $J/submitted.txt 2>/dev/null && continue
      echo "  $f, $o, ${d//\//_}_$s"
    done
  done
  echo ")"
  } > $SUB
  n=$(grep -c '_t0.root,' $SUB || true)
  echo "$n reduce jobs"
  if [ "$n" -gt 0 ]; then
    csub $SUB && grep '_t0.root,' $SUB | awk -F', ' '{print $3}' >> $J/submitted.txt
  fi ;;
time)
  # lnl_time.py for every file of the given samples -> parts_time/ ; then re-merge
  cat > $J/time.sh <<EOS
#!/usr/bin/env bash
set -e
source $LCG > /dev/null
python3 $A/lnl_time.py "\$1" -o "\$2"
EOS
  chmod +x $J/time.sh
  SUB=$J/time_$(date +%H%M%S).sub
  {
  echo "executable = $J/time.sh"
  echo 'output = '$J'/logs/t_$(tag).out'
  echo 'error = '$J'/logs/t_$(tag).err'
  echo "log = $J/logs/time.log"
  echo '+JobFlavour = "longlunch"'
  echo "request_memory = 4000"
  echo 'requirements = (OpSysAndVer =?= "AlmaLinux9")'
  echo "should_transfer_files = NO"
  echo 'arguments = $(inp) $(out)'
  echo "queue inp,out,tag from ("
  for d in "$@"; do
    mkdir -p $E/$d/parts_time
    for f in $E/$d/*_t0.root; do
      s=$(basename $f .root); o=$E/$d/parts_time/$s.npz
      [ -e $o ] && continue
      echo "  $f, $o, ${d//\//_}_$s"
    done
  done
  echo ")"
  } > $SUB
  n=$(grep -c '_t0.root,' $SUB || true); echo "$n time jobs"
  [ "$n" -gt 0 ] && csub $SUB ;;
remerge)
  # drop the merged table and its record so 'merge' redoes it (after 'time')
  for d in "$@"; do rm -f $E/sel/${d//\//_}_sel.npz; sed -i "\|^merge $d\$|d" $J/submitted.txt; done ;;
merge)
  cat > $J/merge.sh <<EOS
#!/usr/bin/env bash
set -e
source $LCG > /dev/null
out=\$1; shift
python3 $A/lnl_merge.py \$(ls \$1/*.npz) -o \$out
EOS
  chmod +x $J/merge.sh
  for d in "$@"; do
    o=$E/sel/${d//\//_}_sel.npz
    [ -e $o ] && continue
    nr=$(njobs $d); np=$(nparts $d)
    [ "$nr" -gt 0 ] && [ "$np" -eq "$nr" ] || { echo "$d: parts $np/$nr, not merging"; continue; }
    if [ -d $E/$d/parts_time ]; then nt=$(ls $E/$d/parts_time/*.npz 2>/dev/null | wc -l); [ "$nt" -eq "$nr" ] || { echo "$d: time parts $nt/$nr, not merging"; continue; }; fi
    grep -q "^merge $d\$" $J/submitted.txt 2>/dev/null && continue
    t=m_${d//\//_}
    cat > $J/$t.sub <<EOS
executable = $J/merge.sh
output = $J/logs/$t.out
error = $J/logs/$t.err
log = $J/logs/merge.log
+JobFlavour = "longlunch"
request_memory = ${MEM:-16000}
requirements = (OpSysAndVer =?= "AlmaLinux9")
should_transfer_files = NO
arguments = $o $E/$d/parts_lnl
queue
EOS
    csub $J/$t.sub && echo "merge $d" >> $J/submitted.txt
  done ;;
esac
