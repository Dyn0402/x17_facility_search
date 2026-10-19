#!/usr/bin/env bash
# fetch_sel.sh -- copy the merged NFS tables from EOS into ganil_nfs/sim/sel/,
# and the beam tables from …/nfs/sel_beam/ into sim/sel_beam/,
# plus the LNL cosmic tables (same arms) from lnl/sim/sel_v3.
set -e
D=$(cd "$(dirname "$0")" && pwd)/sel
mkdir -p "$D"
rsync -t "lxplus:/eos/experiment/ntof/data/x17/nfs/sel/*_sel.npz" "$D/"
# beam samples reduced into per-arm time clusters (nfs_beam_reduce/merge) -> sel_beam/
mkdir -p "$D/../sel_beam"
rsync -t "lxplus:/eos/experiment/ntof/data/x17/nfs/sel_beam/*_sel.npz" "$D/../sel_beam/" || true
for f in L4_cosmic L4_cosmic_bigP; do
  [ -e "$D/${f}_sel.npz" ] || cp "$D/../../../lnl/sim/sel_v3/${f}_sel.npz" "$D/"
done
ls -la "$D"
