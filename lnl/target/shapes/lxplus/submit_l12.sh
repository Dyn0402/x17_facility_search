#!/usr/bin/env bash
# L12: the Al ogive with a Cu liner in Geant4 (x17_facility_search lnl/target/CU_LINER.md).  As submit_l11.sh:
# per (config × detector) X17 m16.8, Born M1/E1 IPC at 18.15 and 15.1, 2e7 ⁸Be γ (EPC); the γ-line library for
# LIBKEYS; the K x-ray lines (Cu, Mo, Ti) for every config and XCFG (big plastics).
cd /afs/cern.ch/work/d/dneff/git/x17_lnl/MX17_Full_Geant
source scripts/setup_lxplus.sh >/dev/null 2>&1
source ../analysis/l12_configs.sh
EXE=${EXE:-bin/mx17_full_sim_culiner_$(git rev-parse --short HEAD)}
[ -x $EXE ] || { echo "no $EXE"; exit 1; }
sub() { for i in 1 2 3 4; do python3 scripts/submit_lnl.py --exe $EXE "$@" && return 0; sleep 20; done; echo "FAILED $*"; }
for det in ${DETS:-bigP asb}; do
  [ $det = bigP ] && D="$BIGP" || D="$ASB"
  if [ "${FULL:-1}" = 1 ]; then
    for k in ${KEYS:-${!CFG[@]}}; do
      t=${k}_$det
      for s in X17_m16.8 M1_18.15 E1_18.15 M1_15.1 E1_15.1; do
        sub --run L12 --sample $s --tag $t --njobs 5 --nevents 100000 -- ${CFG[$k]} $D
      done
      sub --run L12 --sample gam_8Be --tag $t --njobs 10 --nevents 2000000 -- ${CFG[$k]} $D
    done
  fi
  if [ "${LIBS:-1}" = 1 ]; then
    for k in ${LIBKEYS:-ogAl300cu12r8m4}; do
      sub --run L12 --sample gam_lib --tag ${k}_$det --njobs 26 --nevents 1000000 -- ${CFG[$k]} $D
    done
  fi
  if [ "${XRAYS:-1}" = 1 ] && [ $det = bigP ]; then
    for k in ${XKEYS:-${!CFG[@]} ogAl300mo8}; do
      c="${CFG[$k]}"; [ -z "$c" ] && c="${XCFG[$k]}"
      sub --run L12 --sample gam_lib --tag xray_${k}_$det --njobs 4 --nevents 1000000 -- $c --gamma-lines $XRAY $D
    done
  fi
done
