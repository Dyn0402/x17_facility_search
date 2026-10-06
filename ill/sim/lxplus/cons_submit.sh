#!/usr/bin/env bash
# Condor jobs for conservative.py.  Usage (on lxplus):
#   bash cons_submit.sh <name> "<tag>|<conservative.py args>" ...
# Each quoted item is one job writing $C/<tag>.csv; nothing heavy runs on the login node.
set -e
A=/afs/cern.ch/work/d/dneff/git/x17_ill/analysis
C=/eos/experiment/ntof/data/x17/ill/analysis/cons
name=$1; shift
J=/afs/cern.ch/user/d/dneff/condor/ill/cons/$name
mkdir -p $J/logs $C
cat > $J/run.sh <<EOS
#!/usr/bin/env bash
set -e
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh > /dev/null
cd $A
python3 conservative.py "\$@"
EOS
chmod +x $J/run.sh
{
echo "executable = $J/run.sh"
echo 'output = '$J'/logs/$(tag).out'
echo 'error = '$J'/logs/$(tag).err'
echo "log = $J/logs/condor.log"
echo '+JobFlavour = "workday"'
echo "request_memory = 12000"
echo "request_cpus = 1"
echo 'requirements = (OpSysAndVer =?= "AlmaLinux9")'
echo "should_transfer_files = NO"
echo 'arguments = $(args)'
echo "queue tag,args from ("
for j in "$@"; do t=${j%%|*}; echo "  $t, ${j#*|} -o $C/$t.csv"; done
echo ")"
} > $J/cons.sub
condor_submit $J/cons.sub
