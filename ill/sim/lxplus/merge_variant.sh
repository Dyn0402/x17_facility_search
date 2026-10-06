#!/usr/bin/env bash
# Merge one reduced ILL neutron run into contracts/<run>_<cfg>/ (accounting.json +
# table.npz), exactly as pipeline.sh does.  Meant to run as a condor job:
#   bash merge_variant.sh C1 G1_ringCFRP
set -e
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh > /dev/null
M=/afs/cern.ch/work/d/dneff/git/x17_ill/MX17_Full_Geant
E=/eos/experiment/ntof/data/x17/ill
run=$1; cfg=$2; d=$E/$run/$cfg; out=$E/contracts/${run}_$cfg
mkdir -p $out
python3 $M/scripts/ill_accounting.py merge "$d/parts/*.json" -o $out --config ${run}_$cfg > $out/merge.log 2>&1
python3 - "$d/parts" "$out/table.npz" <<'PY' >> $out/merge.log 2>&1
import sys, glob, numpy as np
R = {}
for i, f in enumerate(sorted(glob.glob(sys.argv[1] + "/*.npz"))):
    z = np.load(f)
    names = z["capvol_names"]
    for k in z.files:
        if k == "capvol_names":
            continue
        v = z[k]
        if k == "capvol":
            v = names[v]
        if k == "ev":
            v = v + i * 10**9
        R.setdefault(k, []).append(v)
np.savez_compressed(sys.argv[2], **{k: np.concatenate(v) for k, v in R.items()})
print("table rows", sum(len(x) for x in R["ev"]))
PY
touch $out/.merged
echo "merged $run/$cfg $(date)"
