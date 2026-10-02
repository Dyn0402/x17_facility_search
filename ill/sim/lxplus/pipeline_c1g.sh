#!/usr/bin/env bash
# Overnight pipeline: when a run dir is complete, submit its reduction; when all
# parts exist, merge.  Idempotent (marker files); safe to restart.
cd /afs/cern.ch/work/d/dneff/git/x17_ill/MX17_Full_Geant
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh > /dev/null
E=/eos/experiment/ntof/data/x17/ill
done_logs() { grep -l "Run Summary" "$1"/*_job*.log 2>/dev/null | wc -l; }
n_logs() { sed -n 2p "$1"/RUN_INFO.txt 2>/dev/null | awk "{print \$1}"; }
for iter in $(seq 1 ${1:-200}); do
  pending=0
  for d in $E/C1g/G?; do
    [ -d "$d" ] || continue
    run=$(basename $(dirname $d)); cfg=$(basename $d)
    case $run in S1) kind=pairs; ext=npz;; *) kind=accounting; ext=json;; esac
    tot=$(n_logs $d); fin=$(done_logs $d)
    if [ "$fin" -lt "$tot" ] || [ "$tot" -eq 0 ]; then pending=1; continue; fi
    if [ ! -e $d/parts/.submitted ]; then
      mem=4000; true && mem=6000
      python3 scripts/submit_reduce_ill.py $d --kind $kind --memory $mem 2>&1 | tail -1
      touch $d/parts/.submitted; pending=1; continue
    fi
    np=$(ls $d/parts/*.$ext 2>/dev/null | wc -l)
    if [ "$np" -lt "$tot" ]; then pending=1; continue; fi
    if [ $kind = pairs ]; then out=$E/S1/summary/$cfg; else out=$E/contracts/${run}_$cfg; fi
    if [ ! -e $out/.merged ]; then
      mkdir -p $out
      if [ $kind = pairs ]; then
        python3 scripts/ill_pairs.py merge "$d/parts/*.npz" -o $out --config $cfg > $out/merge.log 2>&1
      else
        python3 scripts/ill_accounting.py merge "$d/parts/*.json" -o $out --config ${run}_$cfg > $out/merge.log 2>&1
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
      fi
      touch $out/.merged; echo "merged $run/$cfg $(date +%H:%M)"
    fi
  done
  [ $pending = 0 ] && { echo "pipeline: everything merged $(date)"; exit 0; }
  sleep 300
done
