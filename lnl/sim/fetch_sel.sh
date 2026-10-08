#!/usr/bin/env bash
# copy the merged LNL Geant4 tables (lnl_merge.py output, a few MB each) from EOS
set -e
D=$(cd "$(dirname "$0")" && pwd)/sel
mkdir -p "$D"
rsync -a --include='*_sel.npz' --exclude='*' lxplus:/eos/experiment/ntof/data/x17/lnl/sel/ "$D/"
ls -la "$D"
