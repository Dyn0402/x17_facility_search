#!/usr/bin/env bash
# Merge accounting parts for a run dir whose truncated raw files were dropped
# (merge normalises by summed N.sim, so missing parts only cost statistics).
#   usage: merge_partial.sh G1_<geom>_<kind>
cd /afs/cern.ch/work/d/dneff/git/x17_trig/MX17_Full_Geant
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh > /dev/null
E=/eos/experiment/ntof/data/x17/ill
name=$1; d=$E/TB/$name; rest=${name#G1_}; geom=${rest%_*}; kind=${rest##*_}
out=$E/TB/contracts/${kind}_$geom; mkdir -p $out
python3 scripts/ill_accounting.py merge "$d/parts/*.json" -o $out --config ${kind}_$geom > $out/merge.log 2>&1
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
echo "partial merge $(ls $d/parts/*.json | wc -l) parts" >> $out/merge.log
touch $out/.merged; echo "merged $name (partial) $(date +%H:%M)"
