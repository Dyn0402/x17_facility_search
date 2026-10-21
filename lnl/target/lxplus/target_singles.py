#!/usr/bin/env python3
"""
target_singles.py -- the per-arm "singles library" of a background sample
(¹⁹F γ lines, the 6.05 MeV E0 pairs, ...) for the target study's rate and
pile-up model (lnl/target/target_rates.py).

    python3 target_singles.py <EOS sample dir> -o <out.npz>

Reads the lnl_reduce parts (<dir>/parts_lnl/*.npz) and keeps every event that
leaves anything in an arm: per arm the SiPM-wall and back-plastic energies
(MeV), the trigger-leg bitmask, and the Micromegas drift-gap charge.  For
γ-line runs inv_mass is the line energy.  n_generated keeps the normalisation.
"""
import argparse
import glob
import os

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("dir")
ap.add_argument("-o", "--out", required=True)
a = ap.parse_args()
keys = ("E_sipm", "E_plast", "legs", "seg_e", "inv_mass", "event_type")
acc = {k: [] for k in keys}
ngen = 0
files = sorted(glob.glob(os.path.join(a.dir, "parts_lnl", "*.npz")))
for f in files:
    z = np.load(f)
    ngen += int(z["n_generated"][0])
    act = ((z["legs"] != 0) | (z["E_sipm"].sum(1) > 0) | (z["E_plast"].sum(1) > 0) | (z["seg_e"].sum(1) > 0))
    for k in keys:
        acc[k].append(z[k][act])
out = {k: np.concatenate(v) for k, v in acc.items()}
out["n_generated"] = np.array([ngen])
np.savez_compressed(a.out, **out)
print(f"{a.dir}: {len(files)} parts, {ngen} generated, {len(out['legs'])} active -> {a.out}")
