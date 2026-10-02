source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh >/dev/null
E=/eos/experiment/ntof/data/x17/ill
W=/afs/cern.ch/work/d/dneff/git/x17_trig
for i in $(seq 1 120); do
  n=$(grep -l "Run Summary" $E/T0/G1_*/pairs_job*.log $E/T1/G1_*/pairs_job*.log 2>/dev/null | wc -l)
  [ "$n" -ge 40 ] && break
  sleep 60
done
echo "done sims: $n $(date)"
for r in T0 T1; do for c in X17 M1; do mkdir -p $E/trig/$r/G1_$c/parts; done; done
ls $E/T0/G1_*/pairs_job*_t0.root $E/T1/G1_*/pairs_job*_t0.root | \
  xargs -P 10 -I{} sh -c 'f={}; r=$(basename $(dirname $(dirname $f))); c=$(basename $(dirname $f)); b=$(basename $f _t0.root); python3 '$W'/trig_reduce.py $f -o '$E'/trig/$r/$c/parts/$b.npz' 2>&1 | tail -3
python3 $W/trig_accept.py --t0 $E/trig/T0 --t1 $E/trig/T1 -o $E/trig/accept 2>&1 | tail -40
echo "all done $(date)"
