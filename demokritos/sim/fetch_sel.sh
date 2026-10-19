#!/usr/bin/env bash
# copy the merged Demokritos Geant4 tables (lnl_merge.py output) from EOS.
#   bash demokritos/sim/fetch_sel.sh        # -> demokritos/sim/sel/
set -e
D=$(cd "$(dirname "$0")" && pwd)/sel
mkdir -p "$D"
rsync -a --checksum --include='*_sel.npz' --exclude='*' lxplus:/eos/experiment/ntof/data/x17/demokritos/sel/ "$D/"
ls -la "$D"
