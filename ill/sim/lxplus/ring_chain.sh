#!/usr/bin/env bash
# local driver: only light ssh calls (ls, condor_submit) to lxplus
S="ssh -o BatchMode=yes lxplus"
E=/eos/experiment/ntof/data/x17/ill
A=/afs/cern.ch/work/d/dneff/git/x17_ill/analysis
M=/afs/cern.ch/work/d/dneff/git/x17_ill/MX17_Full_Geant
D="C1/G1_ringCFRP C1w/G1_ringCFRP C1/G1_ringLiF C1w/G1_ringLiF"
cnt() { timeout 60 $S "n=0; for d in $D; do n=\$((n + \$(ls $E/\$d/$1 2>/dev/null | wc -l))); done; echo \$n"; }
until [ "$(timeout 60 $S "grep -l 'Run Summary' $(for d in $D; do echo -n "$E/$d/*_job*.log "; done) 2>/dev/null | wc -l")" -ge 40 ]; do sleep 600; done
echo "sims done $(date)"
timeout 120 $S "cd $M && source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh >/dev/null && python3 scripts/submit_reduce_ill.py $(for d in $D; do echo -n "$E/$d "; done) --kind accounting --memory 6000 | tail -4; bash $A/seg_submit.sh $D | tail -1"
until [ "$(cnt 'parts/*.json')" -ge 40 ] && [ "$(cnt 'parts_seg/*.npz')" -ge 40 ]; do sleep 300; done
echo "reduce done $(date)"
timeout 120 $S "bash $A/merge_submit.sh C1:G1_ringCFRP C1w:G1_ringCFRP C1:G1_ringLiF C1w:G1_ringLiF | tail -1"
until [ "$(timeout 60 $S "ls $E/contracts/C1*_G1_ring*/.merged 2>/dev/null | wc -l")" -ge 4 ]; do sleep 300; done
echo "merged $(date)"
