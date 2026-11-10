#!/usr/bin/env bash
# l13_driver.sh -- as l12_driver.sh for L13: reduce, time, merge every sample as its simulation finishes (lnl_pipe.sh),
# the per-channel singles (l10_singles.py) of the γ samples and their merge (l10_sng_merge.py, light: ~1 MB/part).
# Merged tables -> $E/target/sel_l13/L13_<sample>_<config>_asb_sel.npz (+ _sng.npz for gam_8Be).  Run with nohup:
#   nohup bash l13_driver.sh > l13_driver.log 2>&1 &
# RUN=L13t ONCE=1 for the smoke test.  Differences from l12_driver.sh:
#  * merges request 18 GB, as L11/L12 (150 pair parts of ~45 MB each in memory, then concatenated: ~14 GB peak; bigP
#    parts are the same size, 100k rows each, and there are 50).  At CERN RequestCpus = ceil(mem/3 GB): 24-30 GB
#    asks for 8-10 cores and such slots hardly ever free up (the first merges sat idle for hours at 30 GB);
#  * idle pipeline jobs of this run get job priority PPRIO=15, above the L13 sim jobs (10): the 8-24 GB pipeline jobs
#    otherwise wait behind the 2 GB sim jobs and dneff's other idle jobs for a slot.  Only reorders dneff's own queue;
#  * reduce jobs go out as each simulation file finishes (time and merge still wait for the whole sample);
#  * up to 400 passes of 15 min (100 h).
A=/afs/cern.ch/work/d/dneff/git/x17_lnl/analysis
E=/eos/experiment/ntof/data/x17/lnl
RUN=${RUN:-L13}; PPRIO=${PPRIO:-15}
export SEL=$E/target/sel_$(echo $RUN | tr A-Z a-z)
mkdir -p $SEL
LCG=/cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
bump() {   # idle lnl pipeline jobs (reduce/time/sng/merge) whose arguments point into this run
  condor_q dneff -constraint "JobStatus == 1 && JobPrio < $PPRIO && regexp(\"/condor/lnl/pipe/\", Cmd)" -af ClusterId ProcId Args 2>/dev/null |
    awk -v r="/$RUN/" 'index($0, r) {print $1"."$2}' | xargs -r condor_prio -p $PPRIO > /dev/null 2>&1
}
for it in $(seq 1 ${NPASS:-400}); do
  all=1
  for d in $E/$RUN/*; do
    s=$RUN/$(basename $d)
    nj=$(sed -n 2p $d/RUN_INFO.txt | awk '{print $1+0}')
    ns=$(grep -l "Run Summary" $d/*_job*.log 2>/dev/null | wc -l)
    case $s in *gam_*) bash $A/l10_sng.sh $s > /dev/null 2>&1 ;; esac
    nsg=$(ls $d/parts_sng/*.npz 2>/dev/null | wc -l)
    case $s in *gam_*)
      if [ "$nsg" -eq "$nj" ]; then
        o=$SEL/${s//\//_}_sng.npz
        [ -e $o ] || (source $LCG > /dev/null; python3 $A/l10_sng_merge.py $d -o $o 2>&1 | sed "s|^|$(date +%H:%M) |")
      else all=0; fi ;;
    esac
    [ -e $SEL/${s//\//_}_sel.npz ] && continue
    all=0
    bash $A/lnl_pipe.sh reduce $s > /dev/null 2>&1     # finished files only (lnl_pipe.sh checks "Run Summary")
    [ "$ns" -eq "$nj" ] || continue                     # 'time' does not check, so it waits for the whole sample
    nt=$(ls $d/parts_time/*.npz 2>/dev/null | wc -l)
    if [ ! -d $d/parts_time ] || { [ "$nt" -lt "$nj" ] && [ ! -e $d/.time_submitted ]; }; then
      bash $A/lnl_pipe.sh time $s > /dev/null 2>&1 && touch $d/.time_submitted
    fi
    MEM=18000 bash $A/lnl_pipe.sh merge $s 2>&1 | grep -v "not merging" | sed "s|^|$(date +%H:%M) |"
  done
  bump
  echo "$(date +%m-%d_%H:%M) pass $it: $(ls $SEL/${RUN}_*_sel.npz 2>/dev/null | wc -l) sel, $(ls $SEL/${RUN}_*_sng.npz 2>/dev/null | wc -l) sng"
  [ $all -eq 1 ] && { echo "all merged $(date)"; exit 0; }
  [ "${ONCE:-0}" = 1 ] && exit 0
  sleep 900
done
