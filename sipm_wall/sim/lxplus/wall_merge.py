#!/usr/bin/env python3
"""
wall_merge.py -- concatenate wall_reduce.py parts of one sample into one table.

    python3 wall_merge.py <parts_wall/*.npz> -o <sample>_wall.npz

Event arrays are concatenated; the sparse bar list's w_row is offset so that it
indexes the merged event arrays.  n_generated is summed; part records the source file index.
"""
from __future__ import annotations

import argparse

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("parts", nargs="+")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    R, off, ngen = {}, 0, 0
    for i, p in enumerate(sorted(a.parts)):
        z = np.load(p)
        n = len(z["eventID"])
        ngen += int(z["n_generated"].sum())
        for k in z.files:
            if k == "n_generated":
                continue
            v = z[k] + off if k == "w_row" else z[k]
            R.setdefault(k, []).append(v)
        R.setdefault("part", []).append(np.full(n, i, np.int16))
        off += n
    out = {k: np.concatenate(v) for k, v in R.items()}
    out["n_generated"] = np.array([ngen])
    np.savez_compressed(a.out, **out)
    print(f"{a.out}: {off} events, {len(out['w_row'])} bar hits, {ngen} generated")


if __name__ == "__main__":
    main()
