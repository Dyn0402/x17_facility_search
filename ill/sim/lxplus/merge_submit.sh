#!/usr/bin/env bash
# Condor: one merge_variant.sh job per "<run> <cfg>" pair.  bash merge_submit.sh C1:G1_ringCFRP ...
set -e
A=/afs/cern.ch/work/d/dneff/git/x17_ill/analysis
J=/afs/cern.ch/user/d/dneff/condor/ill/merge
mkdir -p $J/logs
{
echo "executable = /bin/bash"
echo 'output = '$J'/logs/$(tag).out'
echo 'error = '$J'/logs/$(tag).err'
echo "log = $J/logs/condor.log"
echo '+JobFlavour = "longlunch"'
echo "request_memory = 12000"
echo 'requirements = (OpSysAndVer =?= "AlmaLinux9")'
echo "should_transfer_files = NO"
echo 'arguments = '$A'/merge_variant.sh $(run) $(cfg)'
echo "queue tag,run,cfg from ("
for x in "$@"; do echo "  ${x%%:*}_${x#*:}, ${x%%:*}, ${x#*:}"; done
echo ")"
} > $J/merge.sub
condor_submit $J/merge.sub
