#!/usr/bin/env python3
"""
l10_singles.py -- per-channel deposits of one γ-line ROOT file (L10, SHAPES_GEANT.md §6).

    python3 l10_singles.py <gammas_jobNNN_t0.root> -o <part.npz>

One row per (event, arm, channel) with a deposit, for the scintillator load study:
  ch 0-19  SiPM-wall bars (PlasticScint, 25 mm in u, as ill_pairs.py)
  ch 20    BackScintL (as built: the left 20×30×2 cm bar; big plastics: the 75×75×5 slab)
  ch 21    BackScintR (as built only)
  ch 22    LiqScint_1 (as built only)
  ch 23    Micromegas drift gas (DriftGas)
edep in MeV (all particles).  inv_mass = the line energy of each event; n_generated keeps
the normalisation.
"""
import argparse

import numpy as np
import uproot

ap = argparse.ArgumentParser()
ap.add_argument("file")
ap.add_argument("-o", "--out", required=True)
a = ap.parse_args()

CH = {"BackScintL": 20, "BackScintR": 21, "LiqScint_1": 22, "DriftGas": 23}
acc = {k: [] for k in ("ev", "arm", "ch", "e")}
with uproot.open(a.file) as f:
    et = f["EventTree"].arrays(["eventID", "inv_mass"], library="np")
    for t in f["HitTree"].iterate(["eventID", "armID", "detType", "u", "edep"], library="np",
                                  step_size="300 MB"):
        det = np.array([x.decode() if isinstance(x, bytes) else x for x in t["detType"]])
        ch = np.full(len(det), -1, np.int64)
        sip = det == "PlasticScint"
        ch[sip] = np.clip((t["u"][sip] + 250.0) // 25.0, 0, 19)
        for k, v in CH.items():
            ch[det == k] = v
        m = ch >= 0
        if not m.any():
            continue
        key = (t["eventID"][m].astype(np.int64) * 4 + t["armID"][m]) * 24 + ch[m]
        uk, inv = np.unique(key, return_inverse=True)
        s = np.bincount(inv, t["edep"][m] * 1e-6)
        acc["ev"].append(uk // 96)
        acc["arm"].append((uk // 24) % 4)
        acc["ch"].append(uk % 24)
        acc["e"].append(s)
# an event split across two chunks appears twice: sum again
ev, arm, ch, e = (np.concatenate(acc[k]) if acc[k] else np.zeros(0) for k in ("ev", "arm", "ch", "e"))
key = (ev.astype(np.int64) * 4 + arm.astype(np.int64)) * 24 + ch.astype(np.int64)
uk, inv = np.unique(key, return_inverse=True)
e = np.bincount(inv, e) if len(key) else e
ev, arm, ch = uk // 96, (uk // 24) % 4, uk % 24
lineE = np.zeros(int(et["eventID"].max()) + 1, np.float32)
lineE[et["eventID"]] = et["inv_mass"]
np.savez_compressed(a.out, ev=ev.astype(np.int32), arm=arm.astype(np.int8), ch=ch.astype(np.int8),
                    e=e.astype(np.float32), line=lineE[ev], n_generated=np.array([len(et["eventID"])]),
                    lines_all=np.unique(et["inv_mass"]).astype(np.float32),
                    n_per_line=np.array([np.sum(np.isclose(et["inv_mass"], L)) for L in np.unique(et["inv_mass"])]))
print(f"{a.file}: {len(et['eventID'])} events, {len(e)} deposits -> {a.out}")
