#!/usr/bin/env bash
# Final feasibility pass (after C1w): baseline and timing+veto reports, variants, scan table.
cd /afs/cern.ch/work/d/dneff/git/x17_ill/analysis
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh > /dev/null
E=/eos/experiment/ntof/data/x17/ill
A=$E/analysis
python3 sim_report.py --s1 $E/S1/summary --contracts $E/contracts -o $A/v3_base --r-max 1.9e10 > $A/v3_base.log 2>&1 &
python3 sim_report.py --s1 $E/S1/summary --contracts $E/contracts -o $A/v3_timing --r-max 1.9e10 \
  --sigma-t-ns 0.2 --dt-cut-ns 0.6 --tau-ns 0.6 --cos-scale 0.01 --skip-common > $A/v3_timing.log 2>&1 &
python3 sim_variants.py --s1 $E/S1/summary --contracts $E/contracts -o $A/variants_v3.csv > $A/variants_v3.log 2>&1 &
wait
python3 make_scan.py --base $E --reach $A/v3_base/results.json $A/v3_timing/results.json -o $A/scan_v1.csv > $A/scan_v1.log 2>&1
echo "final done $(date)" >> $A/v3_base.log
