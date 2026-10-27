#!/usr/bin/env bash
# bham_driver.sh -- run under nohup on lxplus: every 10 min merge finished samples (bham_pipe.sh) and chain the
# shield-wall stages (TARGET_GEANT.md §3): s1 -> s2 -> s3 -> the experimental-room runs R2.  Logs to driver.log.
B=/afs/cern.ch/work/d/dneff/git/x17_nfs/MX17_Full_Geant
A=/afs/cern.ch/work/d/dneff/git/x17_nfs/analysis
E=/eos/experiment/ntof/data/x17/bham
EXE=$B/bin/mx17_full_sim_bham_7182359
LCG=/cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
G=$E/R1/guns; mkdir -p $G
SR="python3 $B/scripts/submit_room.py --exe $EXE"
DET_asb="--sipm-readout 16 1"; DET_bigP="--big-plastic 75 75 5 --no-ls --sipm-readout 20 0"
CELL="--target cell --cell-pressure 30 --cell-length 400 --cell-radius 50 --cell-yw -200 --skin Be:0.1+CFRP:0.3 --window Be:3 --aperture 45 --end-cap Al:4 --scraper none"
complete() { local n; n=$(sed -n 2p $E/$1/RUN_INFO.txt | awk '{print $1+0}'); [ "$(ls $E/$1/*.nev 2>/dev/null | wc -l)" -ge "$n" ]; }
mergeps() {  # stage, out tag, [type]
  ( set +u; source $LCG > /dev/null; python3 $A/bham_ps_merge.py $E/R1/$1 -o $G/$2.csv --npz $G/$1_planes.npz ${3:+--type $3} >> $G/merge_$1.txt 2>&1 )
}
step() {
  for p in n g; do
    if [ ! -e $G/gun1_$p.csv ] && complete R1/s1_$p; then mergeps s1_$p gun1_$p; echo "$(date) merged s1_$p"
      $SR --run R1 --name s2_$p --mode ps --njobs 200 --nevents 200000 -- --room --ps-gun $G/gun1_$p.csv --ps-plane -1250 --ps-plane -1050 --ps-gkeep 0.2 | tail -1; fi
    if [ -e $G/gun1_$p.csv ] && [ ! -e $G/gun2_$p.csv ] && [ -e $E/R1/s2_$p/RUN_INFO.txt ] && complete R1/s2_$p; then mergeps s2_$p gun2_$p; echo "$(date) merged s2_$p"
      $SR --run R1 --name s3_$p --mode ps --njobs 200 --nevents 200000 -- --room --ps-gun $G/gun2_$p.csv --ps-plane -850 --ps-plane -650 --ps-plane -600 --ps-gkeep 0.5 | tail -1; fi
    if [ -e $G/gun2_$p.csv ] && [ ! -e $G/gun3_$p.n.csv ] && [ -e $E/R1/s3_$p/RUN_INFO.txt ] && complete R1/s3_$p; then
      mergeps s3_$p gun3_$p.n 0; mergeps s3_$p gun3_$p.g 1; echo "$(date) merged s3_$p"
      for d in asb bigP; do eval da=\$DET_$d
        for t in n g; do
          $SR --run R2 --name leak_${p}src_${t}_$d --mode det --njobs 100 --nevents 100000 -- --room $CELL $da --ps-gun $G/gun3_$p.$t.csv | tail -1
        done; done; fi
  done
}
while true; do
  cd /afs/cern.ch/user/d/dneff/condor
  bash $A/bham_pipe.sh merge B1 B2 B3 R2 R3 2>&1 | grep -v incomplete | sed "s/^/$(date +%H:%M) /"
  step
  sleep 600
done
