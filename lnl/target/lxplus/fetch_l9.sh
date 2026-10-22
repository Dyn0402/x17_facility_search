#!/usr/bin/env bash
# fetch_l9.sh -- copy the merged L9 tables (target options, TARGET_OPTIONS.md §7) and the
# backing-line singles library from EOS to lnl/target/sel/ (gitignored).
set -e
D=$(cd "$(dirname "$0")/.." && pwd)/sel
mkdir -p "$D"
rsync -a --include='L9_*_sel.npz' --exclude='*' lxplus:/eos/experiment/ntof/data/x17/lnl/target/sel_l9/ "$D/"
rsync -a lxplus:/eos/experiment/ntof/data/x17/lnl/target/L9_gam_7Li_bklines_singles.npz "$D/"
ls -la "$D"
