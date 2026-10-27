#!/usr/bin/env bash
# l10_sng.sh <run/sample>... -- condor l10_singles.py for every finished ROOT file -> <sample>/parts_sng/ (idempotent)
A=/afs/cern.ch/work/d/dneff/git/x17_lnl/analysis
E=/eos/experiment/ntof/data/x17/lnl
J=/afs/cern.ch/user/d/dneff/condor/lnl/pipe
LCG=/cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
mkdir -p $J/logs; cd $J
cat > $J/sng.sh <<EOS
#!/usr/bin/env bash
set -e
source $LCG > /dev/null
python3 $A/l10_singles.py "\$1" -o "\$2"
EOS
chmod +x $J/sng.sh
SUB=$J/sng_$(date +%H%M%S).sub
{
echo "executable = $J/sng.sh"
echo 'output = '$J'/logs/s_$(tag).out'
echo 'error = '$J'/logs/s_$(tag).err'
echo "log = $J/logs/sng.log"
echo '+JobFlavour = "longlunch"'
echo "request_memory = 6000"
echo 'requirements = (OpSysAndVer =?= "AlmaLinux9")'
echo "should_transfer_files = NO"
echo 'arguments = $(inp) $(out)'
echo "queue inp,out,tag from ("
for d in "$@"; do
  mkdir -p $E/$d/parts_sng
  for f in $E/$d/*_t0.root; do
    s=$(basename $f .root); o=$E/$d/parts_sng/$s.npz; lg=${f%_t0.root}.log
    [ -e $o ] && continue
    grep -q "Run Summary" $lg 2>/dev/null || continue
    grep -q "^sng ${d//\//_}_$s :sng\$" $J/submitted.txt 2>/dev/null && continue
    echo "  $f, $o, ${d//\//_}_$s"
  done
done
echo ")"
} > $SUB
n=$(grep -c '_t0.root,' $SUB || true); echo "$n singles jobs"
if [ "$n" -gt 0 ]; then
  for i in 1 2 3 4; do condor_submit $SUB > $J/last_sng.txt 2>&1 && break; sleep 20; done
  tail -1 $J/last_sng.txt
  grep '_t0.root,' $SUB | awk -F', ' '{print "sng "$3" :sng"}' >> $J/submitted.txt
fi
