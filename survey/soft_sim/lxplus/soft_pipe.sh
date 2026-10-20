#!/usr/bin/env bash
# soft_pipe.sh -- merge the soft-source beam runs (N5 neutrons, G5 photons; MX17_Full_Geant branch soft)
# with soft_beam_merge.py into $E/sel_soft/<run>_<sample>_sel.npz, one condor job per sample.
#
#   bash soft_pipe.sh status
#   bash soft_pipe.sh merge          # samples whose parts_beam/ are complete
set -e
A=/afs/cern.ch/work/d/dneff/git/x17_nfs/analysis
E=/eos/experiment/ntof/data/x17/nfs
J=/afs/cern.ch/user/d/dneff/condor/nfs/pipe
LCG=/cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
S=$E/sel_soft
SAMPLES="N5/beam_soft N5/beam_soft_bigP G5/beam_gamma G5/beam_gamma_bigP G6/beam_gamma G6/beam_gamma_bigP"
mkdir -p $S $J/logs
cd $J
njobs() { sed -n 2p $E/$1/RUN_INFO.txt | awk '{print $1+0}'; }
np() { ls $E/$1/parts_beam/*.npz 2>/dev/null | wc -l; }
case $1 in
status) for d in $SAMPLES; do echo "$d parts $(np $d)/$(njobs $d)  sel $([ -e $S/${d//\//_}_sel.npz ] && echo yes || echo no)"; done ;;
merge)
  cat > $J/smerge.sh <<EOS
#!/usr/bin/env bash
set -e
source $LCG > /dev/null
cd $A
out=\$1; shift
python3 $A/soft_beam_merge.py \$(ls \$1/*.npz) -o \$out
EOS
  chmod +x $J/smerge.sh
  for d in $SAMPLES; do
    o=$S/${d//\//_}_sel.npz
    [ -e $o ] && continue
    [ "$(np $d)" -eq "$(njobs $d)" ] || { echo "$d: parts $(np $d)/$(njobs $d), not merging"; continue; }
    t=sm_${d//\//_}
    cat > $J/$t.sub <<EOS
executable = $J/smerge.sh
output = $J/logs/$t.out
error = $J/logs/$t.err
log = $J/logs/merge.log
+JobFlavour = "longlunch"
request_memory = 12000
requirements = (OpSysAndVer =?= "AlmaLinux9")
should_transfer_files = NO
arguments = $o $E/$d/parts_beam
queue
EOS
    condor_submit $J/$t.sub | tail -1
  done ;;
esac
