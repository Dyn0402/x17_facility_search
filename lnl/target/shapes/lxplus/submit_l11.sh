#!/usr/bin/env bash
# L11: the ogive, the light shells and the window's tube in Geant4 (x17_facility_search lnl/target/SHAPES_GEANT.md §10).
# Per (config × detector): X17 m16.8, Born M1/E1 IPC at 18.15 (γ0) and 15.1 (γ1), 2e7 ⁸Be γ (EPC); the γ-line
# library for LIBKEYS (both detectors); the K x-ray lines for XKEYS (big plastics); X17-only diagnostics (DIAG).
#   FULL=0 LIBS=0 XRAYS=0 DIAGS=0 skip a group; KEYS/LIBKEYS/XKEYS/DIAGKEYS pick configs; DETS="bigP asb".
cd /afs/cern.ch/work/d/dneff/git/x17_lnl/MX17_Full_Geant
source scripts/setup_lxplus.sh >/dev/null 2>&1
source ../analysis/l11_configs.sh
EXE=${EXE:-bin/mx17_full_sim_ogive_$(git rev-parse --short HEAD)}
[ -x $EXE ] || { mkdir -p bin; cp build/mx17_full_sim $EXE; }
sub() { for i in 1 2 3 4; do python3 scripts/submit_lnl.py --exe $EXE "$@" && return 0; sleep 20; done; echo "FAILED $*"; }
for det in ${DETS:-bigP asb}; do
  [ $det = bigP ] && D="$BIGP" || D="$ASB"
  if [ "${FULL:-1}" = 1 ]; then
    for k in ${KEYS:-${!CFG[@]}}; do
      t=${k}_$det
      sub --run L11 --sample X17_m16.8 --tag $t --njobs 5 --nevents 100000 -- ${CFG[$k]} $D
      sub --run L11 --sample M1_18.15 --tag $t --njobs 5 --nevents 100000 -- ${CFG[$k]} $D
      sub --run L11 --sample E1_18.15 --tag $t --njobs 5 --nevents 100000 -- ${CFG[$k]} $D
      sub --run L11 --sample M1_15.1 --tag $t --njobs 5 --nevents 100000 -- ${CFG[$k]} $D
      sub --run L11 --sample E1_15.1 --tag $t --njobs 5 --nevents 100000 -- ${CFG[$k]} $D
      sub --run L11 --sample gam_8Be --tag $t --njobs 10 --nevents 2000000 -- ${CFG[$k]} $D
    done
  fi
  if [ "${LIBS:-1}" = 1 ]; then
    for k in ${LIBKEYS:-ogCu200 ogBe200mo8 win45be}; do
      sub --run L11 --sample gam_lib --tag ${k}_$det --njobs 26 --nevents 1000000 -- ${CFG[$k]} $D
    done
  fi
  if [ "${XRAYS:-1}" = 1 ] && [ $det = bigP ]; then
    for k in ${XKEYS:-ogCu200 ogBe200mo8 win45be win45wide}; do
      sub --run L11 --sample gam_lib --tag xray_${k}_$det --njobs 4 --nevents 1000000 -- ${CFG[$k]} --gamma-lines $XRAY $D
    done
  fi
  if [ "${DIAGS:-1}" = 1 ] && [ $det = bigP ]; then
    for k in ${DIAGKEYS:-${!DIAG[@]}}; do
      sub --run L11 --sample X17_m16.8 --tag diag_${k}_$det --njobs 5 --nevents 100000 -- ${DIAG[$k]} $D
    done
  fi
done
