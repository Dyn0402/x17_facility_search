#!/usr/bin/env python3
"""g4tendl_check.py -- what Geant4's low-energy proton data (G4TENDL1.4, used by the *_AllHP
physics lists below 200 MeV) contains for the LNL target nuclei (TARGET_OPTIONS.md §11).

Prints, per nucleus, the total inelastic σ at 0.3-2 MeV and the reaction channels present
(final-state files F01..F36), so we know which reactions Geant4 can produce at all.
    python3 g4tendl_check.py > g4tendl_check.csv        (on lxplus: reads /cvmfs)
"""
import glob
import os
import zlib

import numpy as np

D = "/cvmfs/geant4.cern.ch/share/data/G4TENDL1.4/Proton/Inelastic"
NUC = ["3_7_Lithium", "3_6_Lithium", "5_11_Boron", "6_12_Carbon", "6_13_Carbon", "8_16_Oxygen",
       "9_19_Fluorine", "13_27_Aluminum", "29_63_Copper", "73_181_Tantalum"]
EN = [300e3, 441e3, 550e3, 800e3, 1030e3, 1100e3, 1500e3, 2000e3]


def read(p):
    s = zlib.decompress(open(p, "rb").read()).decode(errors="replace").split()
    return s


print("nucleus,n_points_below_1.2MeV," + ",".join(f"sigma_b_{e/1e3:g}keV" for e in EN) + ",final-state files")
for n in NUC:
    f = f"{D}/CrossSection/{n}.z"
    if not os.path.exists(f):
        print(f"{n},missing")
        continue
    s = read(f)
    i0 = 3 if s[0] != "G4NDL" else 5
    v = np.array(s[i0:], float)
    e, x = v[0::2], v[1::2]
    sig = [float(np.interp(E, e, x, left=0, right=x[-1])) for E in EN]
    ch = []
    for ff in sorted(glob.glob(f"{D}/F*/{n}.z")):
        ch.append(os.path.basename(os.path.dirname(ff)))
    print(f"{n},{int((e < 1.2e6).sum())}," + ",".join(f"{v:.3g}" for v in sig) + "," + " ".join(ch))
