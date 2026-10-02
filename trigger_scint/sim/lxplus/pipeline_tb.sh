#!/usr/bin/env bash
# TB pipeline: when a run dir is complete, submit its reduction; when all parts
# exist, merge.  Idempotent (marker files); safe to restart.
#   signal (X17/M1/E0)  -> $E/TB/summary/<geom>_<ch>/events.npz      (ill_pairs merge)
#   C1/C1w/C1g/K1       -> $E/TB/contracts/<kind>_<geom>/{accounting.json,table.npz}
cd /afs/cern.ch/work/d/dneff/git/x17_trig/MX17_Full_Geant
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh > /dev/null
E=/eos/experiment/ntof/data/x17/ill
done_logs() { grep -l "Run Summary" "$1"/*_job*.log 2>/dev/null | wc -l; }
n_logs() { sed -n 2p "$1"/RUN_INFO.txt 2>/dev/null | awk "{print \$1}"; }
for iter in $(seq 1 ${1:-300}); do
  pending=0
  for d in $E/TB/G1_*; do
    [ -d "$d" ] || continue
    name=$(basename $d); rest=${name#G1_}; geom=${rest%_*}; kind=${rest##*_}
    case $kind in X17|M1|E0) red=pairs; ext=npz;; *) red=accounting; ext=json;; esac
    tot=$(n_logs $d); fin=$(done_logs $d)
    if [ "$fin" -lt "$tot" ] || [ "$tot" -eq 0 ]; then pending=1; continue; fi
    if [ ! -e $d/parts/.submitted ]; then
      mem=8000; case $kind in C1|C1w) mem=16000;; esac
      python3 scripts/submit_reduce_ill.py $d --kind $red --memory $mem 2>&1 | tail -1
      mkdir -p $d/parts; touch $d/parts/.submitted; pending=1; continue
    fi
    np=$(ls $d/parts/*.$ext 2>/dev/null | wc -l)
    if [ "$np" -lt "$tot" ]; then pending=1; continue; fi
    if [ $red = pairs ]; then out=$E/TB/summary/${geom}_$kind; else out=$E/TB/contracts/${kind}_$geom; fi
    if [ ! -e $out/.merged ]; then
      mkdir -p $out
      if [ $red = pairs ]; then
        python3 scripts/ill_pairs.py merge "$d/parts/*.npz" -o $out --config G1 > $out/merge.log 2>&1
      else
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
      fi
      touch $out/.merged; echo "merged $name $(date +%H:%M)"
    fi
  done
  [ $pending = 0 ] && { echo "pipeline: everything merged $(date)"; exit 0; }
  sleep 300
done
