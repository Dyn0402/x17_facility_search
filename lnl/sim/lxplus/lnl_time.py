#!/usr/bin/env python3
"""
lnl_time.py -- per event and arm, the earliest scintillator hit time, for the
time-of-flight veto against cosmic muons crossing two arms.

    python3 lnl_time.py <prefix_jobNNN_t0.root> -o <parts_time/stem.npz>

Writes ev (eventIDs with any scintillator hit), t_sipm (n,4) and t_plast (n,4)
in ns (NaN where the arm saw nothing).  Truth times: the detector resolution is
applied in the analysis.  lnl_merge.py joins these on eventID when a
parts_time/ directory sits next to parts_lnl/.
"""
from __future__ import annotations

import argparse

import numpy as np

BR = ["eventID", "armID", "detType", "time", "edep"]


def _s(a):
    return np.array([x.decode() if isinstance(x, bytes) else str(x) for x in a])


def main():
    import uproot
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    keys, ts, tp = [], [], []
    with uproot.open(a.file) as f:
        for t in f["HitTree"].iterate(BR, library="np", step_size="200 MB"):
            det = _s(t["detType"])
            for name, store in (("PlasticScint", ts), ("BackScint", tp)):
                m = (np.char.startswith(det.astype(str), name)) & (t["edep"] > 0)
                if m.any():
                    k = t["eventID"][m].astype(np.int64) * 4 + t["armID"][m].astype(np.int64)
                    store.append((k, t["time"][m].astype(np.float64)))
    out = {}
    allk = np.unique(np.concatenate([k for st in (ts, tp) for k, _ in st])) if (ts or tp) else np.zeros(0, np.int64)
    ev = np.unique(allk // 4)
    for name, st in (("t_sipm", ts), ("t_plast", tp)):
        arr = np.full((len(ev), 4), np.nan, np.float32)
        if st:
            k = np.concatenate([x for x, _ in st])
            tt = np.concatenate([y for _, y in st])
            uk, inv = np.unique(k, return_inverse=True)
            tmin = np.full(len(uk), np.inf)
            np.minimum.at(tmin, inv, tt)
            arr[np.searchsorted(ev, uk // 4), uk % 4] = tmin
        out[name] = arr
    np.savez_compressed(a.out, ev=ev, **out)
    print(f"{a.file}: {len(ev)} events with scintillator hits -> {a.out}")


if __name__ == "__main__":
    main()
