#!/usr/bin/env bash
# requench.sh <run/sample> ...: re-reduce the kept ROOT files with bham_chan_reduce.py (quenched light, legs) -> parts_chanq/, merge -> $E/sel/<run>_<sample>_chanq.npz
# quenched channel spectra from the kept ROOT files (2 per sample)
A=/afs/cern.ch/work/d/dneff/git/x17_nfs/analysis
E=/eos/experiment/ntof/data/x17/bham
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh > /dev/null
for d in "$@"; do
  mkdir -p $E/$d/parts_chanq
  for f in $E/$d/*_t0.root; do o=$E/$d/parts_chanq/$(basename $f .root).npz; [ -e $o ] || python3 $A/bham_chan_reduce.py $f -o $o; done
  python3 $A/bham_chan_merge.py $E/$d/parts_chanq/*.npz -o $E/sel/${d//\//_}_chanq.npz
done
echo REQ_DONE
