#!/usr/bin/env python3
"""l10_sng_merge.py <sample dir> -o <out.npz> -- concatenate the l10_singles.py parts of one γ sample
(event ids made unique per part), keep the per-line generated counts (SHAPES_GEANT.md §6)."""
import argparse
import glob
import os

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("dir")
ap.add_argument("-o", "--out", required=True)
a = ap.parse_args()
acc = {k: [] for k in ("ev", "arm", "ch", "e", "line")}
cnt, off = {}, 0
for f in sorted(glob.glob(os.path.join(a.dir, "parts_sng", "*.npz"))):
    z = np.load(f)
    for k in acc:
        acc[k].append(z[k] + (off if k == "ev" else 0))
    off += int(z["n_generated"][0])
    for L, n in zip(z["lines_all"], z["n_per_line"]):
        cnt[round(float(L), 5)] = cnt.get(round(float(L), 5), 0) + int(n)
out = {k: np.concatenate(v) for k, v in acc.items()}
out["lines"] = np.array(sorted(cnt))
out["n_line"] = np.array([cnt[L] for L in sorted(cnt)])
out["n_generated"] = np.array([off])
np.savez_compressed(a.out, **out)
print(a.dir, off, len(out["e"]), "->", a.out)
