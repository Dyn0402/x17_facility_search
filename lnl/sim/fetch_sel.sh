#!/usr/bin/env bash
# copy the merged LNL Geant4 tables (lnl_merge.py output) from EOS.
#   bash fetch_sel.sh          # sel_v3 (2026-10-12): L1-L4, L7 with per-arm layer energies; use LNL_SEL=lnl/sim/sel_v3
#   bash fetch_sel.sh sel      # the original tables (also L5, L6)
set -e
V=${1:-sel_v3}
D=$(cd "$(dirname "$0")" && pwd)/$V
mkdir -p "$D"
rsync -a --checksum --include='*_sel.npz' --exclude='*' lxplus:/eos/experiment/ntof/data/x17/lnl/$V/ "$D/"
ls -la "$D"
