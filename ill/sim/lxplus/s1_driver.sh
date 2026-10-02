#!/usr/bin/env bash
# S1 driver: per config, wait for a finished C1 file, build the vertex lib, submit X17/M1/E0.
cd /afs/cern.ch/work/d/dneff/git/x17_ill/MX17_Full_Geant
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh > /dev/null
E=/eos/experiment/ntof/data/x17/ill
EXE=$PWD/bin/mx17_full_sim_7892a77
todo="G1 G2 G3 G4 G5 G6"
for iter in $(seq 1 120); do
  left=""
  for g in $todo; do
    lib=$E/libs/C1_${g}_gas.csv
    if [ ! -s $lib ]; then
      log=$(grep -l "Run Summary" $E/C1/$g/neutrons_job*.log 2>/dev/null | head -1)
      if [ -z "$log" ]; then left="$left $g"; continue; fi
      python3 scripts/ill_make_lib.py ${log%.log}_t0.root -o $lib || { left="$left $g"; continue; }
    fi
    for ch in X17 M1 E0; do
      [ -d $E/S1/${g}_$ch ] && continue
      if [ $ch = X17 ]; then ex="--ipc 0"; else ex="--ipc 1 --ipc-multipole $ch"; fi
      python3 scripts/submit_ill.py --run S1 --config $g --tag $ch --mode pairs --njobs 34 \
        --nevents 100000 --flavour longlunch --exe $EXE -- $ex --pair-vertex-lib $lib 2>&1 | tail -1
    done
  done
  todo="$left"
  [ -z "$todo" ] && { echo "all S1 submitted $(date)"; exit 0; }
  echo "waiting for C1:$todo $(date)"; sleep 120
done
