#!/usr/bin/env bash
# bham_pipe.sh -- merges for the Birmingham target study (TARGET_GEANT.md §2-3), one condor job per sample.
# The runs reduce in the job (submit_bham.py, submit_room.py), so only merges are left.  Idempotent.
#
#   bash bham_pipe.sh status [B1 B2 B3 R2 ...]
#   bash bham_pipe.sh merge  [B1 B2 B3 R2 ...]   # samples whose parts are complete
#
# pairs (parts_nfs + parts_time) -> nfs_merge.py  -> $E/sel/<run>_<sample>_sel.npz
# beam  (parts_beam)             -> soft_beam_merge.py -> $E/sel/<run>_<sample>_sel.npz
#       (parts_chan)             -> bham_chan_merge.py -> $E/sel/<run>_<sample>_chan.npz
set -e
A=/afs/cern.ch/work/d/dneff/git/x17_nfs/analysis
E=/eos/experiment/ntof/data/x17/bham
J=/afs/cern.ch/user/d/dneff/condor/bham/pipe
LCG=/cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
mkdir -p $J/logs $E/sel
cd $J
cmd=$1; shift
RUNS=${@:-B1 B2 B3}
njobs() { sed -n 2p $E/$1/RUN_INFO.txt 2>/dev/null | awk '{print $1+0}'; }
np_() { ls $E/$1/$2/*.npz 2>/dev/null | wc -l; }
samples() { for r in $RUNS; do for d in $E/$r/*/; do echo $r/$(basename $d); done; done; }
csub() { for i in 1 2 3 4; do condor_submit "$1" > $J/last.txt 2>&1 && { tail -1 $J/last.txt; return 0; }; sleep 20; done; tail -3 $J/last.txt; return 1; }
sub() {   # name, script, args...
  local t=$1; shift
  cat > $J/$t.sub <<EOS
executable = $1
output = $J/logs/$t.out
error = $J/logs/$t.err
log = $J/logs/merge.log
+JobFlavour = "longlunch"
request_memory = ${MEM:-12000}
requirements = (OpSysAndVer =?= "AlmaLinux9")
should_transfer_files = NO
arguments = ${@:2}
queue
EOS
  csub $J/$t.sub
}
cat > $J/m.sh <<EOS
#!/usr/bin/env bash
set -e
source $LCG > /dev/null
cd $A
script=\$1; out=\$2; dir=\$3
python3 $A/\$script \$(ls \$dir/*.npz) -o \$out
EOS
chmod +x $J/m.sh
case $cmd in
status)
  for d in $(samples); do
    n=$(njobs $d)
    printf "%-34s jobs %4s  nfs %4s time %4s beam %4s chan %4s  sel %s\n" $d "$n" $(np_ $d parts_nfs) $(np_ $d parts_time) \
      $(np_ $d parts_beam) $(np_ $d parts_chan) "$(ls $E/sel/${d//\//_}_* 2>/dev/null | xargs -n1 basename 2>/dev/null | tr '\n' ' ')"
  done ;;
merge)
  for d in $(samples); do
    n=$(njobs $d); s=${d//\//_}
    [ -n "$n" ] || continue
    if [ -d $E/$d/parts_nfs ]; then
      [ -e $E/sel/${s}_sel.npz ] || grep -qx "m $s" $J/done.txt 2>/dev/null && continue
      [ "$(np_ $d parts_nfs)" -eq "$n" ] && [ "$(np_ $d parts_time)" -eq "$n" ] || { echo "$d: parts incomplete"; continue; }
      sub mp_$s $J/m.sh nfs_merge.py $E/sel/${s}_sel.npz $E/$d/parts_nfs && echo "m $s" >> $J/done.txt
    elif [ -d $E/$d/parts_beam ]; then
      [ -e $E/sel/${s}_sel.npz ] || grep -qx "b $s" $J/done.txt 2>/dev/null && continue
      [ "$(np_ $d parts_beam)" -eq "$n" ] && [ "$(np_ $d parts_chan)" -eq "$n" ] || { echo "$d: parts incomplete"; continue; }
      sub mb_$s $J/m.sh soft_beam_merge.py $E/sel/${s}_sel.npz $E/$d/parts_beam && \
      sub mc_$s $J/m.sh bham_chan_merge.py $E/sel/${s}_chan.npz $E/$d/parts_chan && echo "b $s" >> $J/done.txt
    fi
  done ;;
esac
