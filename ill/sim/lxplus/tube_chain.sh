#!/usr/bin/env bash
# local driver for the He flight-tube / entrance-window variants (2026-10-07):
# wait for the C1/C1w sims, reduce, merge, then the budget and rate-wall fits.
# Only light ssh calls (ls, condor_submit) go to lxplus.
S="ssh -o BatchMode=yes lxplus"
E=/eos/experiment/ntof/data/x17/ill
A=/afs/cern.ch/work/d/dneff/git/x17_ill/analysis
M=/afs/cern.ch/work/d/dneff/git/x17_ill/MX17_Full_Geant
V="tubeBe tubeBe25 tubeMy"
D=$(for v in $V; do echo -n "C1/G1_$v C1w/G1_$v "; done)
N=$(( $(echo $V | wc -w) * 2 ))
cnt() { timeout 60 $S "n=0; for d in $D; do n=\$((n + \$(ls $E/\$d/$1 2>/dev/null | wc -l))); done; echo \$n"; }
until [ "$(timeout 60 $S "grep -l 'Run Summary' $(for d in $D; do echo -n "$E/$d/*_job*.log "; done) 2>/dev/null | wc -l")" -ge $((N * 10)) ]; do sleep 600; done
echo "sims done $(date)"
timeout 120 $S "cd $M && source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh >/dev/null && python3 scripts/submit_reduce_ill.py $(for d in $D; do echo -n "$E/$d "; done) --kind accounting --memory 14000 | tail -4; bash $A/seg_submit.sh $D | tail -1"
until [ "$(cnt 'parts/*.json')" -ge $((N * 10)) ] && [ "$(cnt 'parts_seg/*.npz')" -ge $((N * 10)) ]; do sleep 300; done
echo "reduce done $(date)"
timeout 120 $S "bash $A/merge_submit.sh $(for v in $V; do echo -n "C1:G1_$v C1w:G1_$v "; done) | tail -1"
until [ "$(timeout 60 $S "ls $E/contracts/C1*_G1_tube*/.merged 2>/dev/null | wc -l")" -ge $N ]; do sleep 300; done
echo "merged $(date)"
jobs=()
for v in $V; do
  jobs+=("bo_$v|--budget --biased-only --variant $v --segs 3:30:0 --coll 20 --hw no-veto")
  jobs+=("e14_$v|--budget --biased-only --variant $v --segs 3:30:0 --coll 20 --hw per-arm,no-veto --ecut 14")
  jobs+=("walls_${v}_e13|--rate-walls --biased-only --variant $v --segs 3:30:0 --coll 20 --hw no-veto --ecut 13")
  jobs+=("walls_${v}_e14|--rate-walls --biased-only --variant $v --segs 3:30:0 --coll 20 --hw per-arm,no-veto --ecut 14")
done
timeout 120 $S "cd $A && bash cons_submit.sh tube $(printf "'%s' " "${jobs[@]}") | tail -1"
until [ "$(timeout 60 $S "ls $E/analysis/cons/walls_tube*_e14.csv 2>/dev/null | wc -l")" -ge 3 ] && \
      [ "$(timeout 60 $S "grep -l wrote /afs/cern.ch/user/d/dneff/condor/ill/cons/tube/logs/*.out 2>/dev/null | wc -l")" -ge $((${#jobs[@]})) ]; do sleep 300; done
echo "fits done $(date)"
