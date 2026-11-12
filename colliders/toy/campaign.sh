#!/usr/bin/env bash
# Full collider X17 toy campaign (2026-11-12): ~1 h on 16 cores.  Outputs in colliders/out/pairs/.
# Signal/background points carry the pair conversion-veto fit; scans do not (acceptance/resolution only).
# Resumable: points whose .json exists are skipped (delete colliders/out/pairs/* for a clean rerun).
set -u
cd "$(dirname "$0")/../.."
PY=${PY:-$HOME/PycharmProjects/nTof_x17/.venv/bin/python}
run() {
  local det=$1 src=$2; shift 2
  local tag="${det}__${src//:/}__${S}"
  [ -f "colliders/out/pairs/${tag}.json" ] && return
  $PY colliders/toy/run.py --det "$det" --source "$src" --system "$S" "$@"
}
for det in star star_lowB sphenix_tpc sphenix_si sphenix_tpc_q sphenix_si_q alice_tpc_0p5T alice_tpc_0p2T alice_its_0p5T alice_its_0p2T alice3_2T alice3_0p5T; do
  case $det in star*|sphenix*) S=auau200;; *) S=pp13600;; esac
  run $det x17_pi0 --n 400000 --nfit 2000
  run $det x17_eta --n 400000 --nfit 2000
  run $det dal_pi0 --n 1500000 --nfit 4000
  run $det dal_eta --n 1500000 --nfit 2500
  run $det conv --n 1000000 --nfit 4000
  for p in 0.0 0.025 0.05 0.1 0.2 0.4 0.8 1.6; do
    run $det scan:$p --n 40000 --nfit 600
  done
done
echo CAMPAIGN_DONE
