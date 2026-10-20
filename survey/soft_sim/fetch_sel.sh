#!/usr/bin/env bash
# copy the merged soft-source tables from EOS (lxplus) into survey/soft_sim/sel/
cd "$(dirname "$0")" && mkdir -p sel
rsync -t lxplus:/eos/experiment/ntof/data/x17/nfs/sel_soft/'*_sel.npz' sel/ && ls -la sel/
