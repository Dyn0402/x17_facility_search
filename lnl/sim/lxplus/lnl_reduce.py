#!/usr/bin/env python3
"""
lnl_reduce.py -- one LNL ROOT file (pairs, γ lines or cosmics) -> one .npz.

    python3 lnl_reduce.py <prefix_jobNNN_t0.root> -o <part.npz>

Two passes over the file, both with existing reducers:
  * MX17_Full_Geant scripts/ill_pairs.py reduce: truth, the primary leptons'
    first drift-gap hits, the per-arm trigger legs (SiPM bar >= 0.5 MIP AND
    plastic >= 0.5 MIP in one arm) and the per-arm calorimetry
    (E_sipm, E_plast, E_ls, MeV);
  * seg_reduce.py (the ILL one, copied here): per arm, the Micromegas charge
    and the PCA segment of the dominant track (c_dom, d_dom, fdom).
Joined on eventID.  Pair runs keep every event; γ-line and cosmic runs keep
only events with a leg, scintillator energy or drift-gap charge somewhere
(n_generated keeps the normalisation).
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, os.environ.get("MX17_SCRIPTS",
                                  "/afs/cern.ch/work/d/dneff/git/x17_lnl/MX17_Full_Geant/scripts"))
import ill_pairs      # noqa: E402
import seg_reduce     # noqa: E402

SEG_KEYS = ("e", "n", "c_all", "c_dom", "d_dom", "fdom", "n_dom")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    tmp = Path(os.environ.get("_CONDOR_SCRATCH_DIR", tempfile.gettempdir()))
    stem = Path(a.file).stem
    pp, sp = tmp / f"{stem}_pairs.npz", tmp / f"{stem}_seg.npz"
    ill_pairs.reduce_file(a.file, str(pp))
    seg_reduce.reduce_file(a.file, str(sp))
    P = dict(np.load(pp))
    S = dict(np.load(sp))
    pp.unlink()
    sp.unlink()
    N = len(P["eventID"])
    ev = P["eventID"]
    idx = np.searchsorted(S["ev"], ev)
    idx = np.clip(idx, 0, max(len(S["ev"]) - 1, 0))
    has = (len(S["ev"]) > 0) & (S["ev"][idx] == ev) if len(S["ev"]) else np.zeros(N, bool)
    for k in SEG_KEYS:
        if k not in S:
            continue
        v = S[k]
        fill = 0 if k in ("e", "n", "n_dom", "fdom") else np.nan
        arr = np.full((N,) + v.shape[1:], fill, np.float32)
        arr[has] = v[idx[has]]
        P[f"seg_{k}"] = arr
    if "seg_e" not in P:                       # file without any gap charge
        for k in SEG_KEYS:
            shp = (N, 4, 3) if k.startswith(("c_", "d_")) else (N, 4)
            P[f"seg_{k}"] = np.full(shp, 0 if k in ("e", "n", "n_dom", "fdom") else np.nan, np.float32)
    et = P["event_type"]
    if not np.isin(et, (0, 1)).all():
        act = ((P["legs"] != 0) | (P["seg_e"].sum(1) > 0) | (P["E_sipm"].sum(1) > 0)
               | (P["E_plast"].sum(1) > 0) | (P["E_ls"].sum(1) > 0))
        P = {k: v[act] for k, v in P.items()}
    P["n_generated"] = np.array([N])
    np.savez_compressed(a.out, **P)
    print(f"{a.file}: {N} events, kept {len(P['eventID'])} -> {a.out}")


if __name__ == "__main__":
    main()
