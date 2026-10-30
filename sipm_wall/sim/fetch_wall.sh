#!/usr/bin/env bash
# fetch_wall.sh -- copy the merged per-bar wall tables from EOS into sim/sel/ (gitignored)
set -e
D=$(cd "$(dirname "$0")" && pwd)/sel
mkdir -p "$D"
rsync -av "lxplus:/eos/experiment/ntof/data/x17/lnl/sel_wall/*_wall.npz" "lxplus:/eos/experiment/ntof/data/x17/lnl/sel_wall/*_tplast.npz" "$D/"
