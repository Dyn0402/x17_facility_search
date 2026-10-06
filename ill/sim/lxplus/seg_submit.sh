#!/usr/bin/env bash
# One condor job per ROOT file: seg_reduce.py -> <run dir>/parts_seg/<stem>.npz
# Usage: bash seg_submit.sh [run/cfg ...]   (on lxplus; skips files whose output exists)
# Default dirs: the G1 baseline set + K1/G5.
set -e
A=/afs/cern.ch/work/d/dneff/git/x17_ill/analysis
E=/eos/experiment/ntof/data/x17/ill
J=/afs/cern.ch/user/d/dneff/condor/ill/seg/$(echo ${*:-base} | tr ' /' '__')
mkdir -p $J/logs
cat > $J/run.sh <<EOS
#!/usr/bin/env bash
set -e
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh > /dev/null
python3 $A/seg_reduce.py "\$1" -o "\$2"
EOS
chmod +x $J/run.sh
SUB=$J/seg.sub
{
echo "executable = $J/run.sh"
echo 'output = '$J'/logs/$(tag).out'
echo 'error = '$J'/logs/$(tag).err'
echo "log = $J/logs/condor.log"
echo '+JobFlavour = "longlunch"'
echo "request_memory = 6000"
echo 'requirements = (OpSysAndVer =?= "AlmaLinux9")'
echo "should_transfer_files = NO"
echo 'arguments = $(inp) $(out)'
echo "queue inp,out,tag from ("
DIRS=${*:-C1/G1 C1w/G1 C1g/G1 K1/G5 S1/G1_X17 S1/G1_M1 S1/G1_E0}
for d in $DIRS; do
  mkdir -p $E/$d/parts_seg
  for f in $E/$d/*_t0.root; do
    s=$(basename $f .root); o=$E/$d/parts_seg/$s.npz
    [ -e $o ] || echo "  $f, $o, ${d//\//_}_$s"
  done
done
echo ")"
} > $SUB
echo "$(grep -c '_t0.root,' $SUB) jobs"
condor_submit $SUB
