#!/usr/bin/env python3
"""
he3ng_samearm.py -- the ³He(n,γ) 20.6 MeV γ as a same-arm two-track fake.

A single-arm trigger (single_arm.py) records pairs with both leptons in one
arm.  ³He(n,γ) gives ~200 γ per IPC pair; a γ that converts (or Comptons and
scatters) in front of an arm can show two tracks in one Micromegas.  The
contract tables keep one charge centroid per arm, so this goes back to the C1g
ROOT files (³He(n,γ) biased, full HitTree).

    # per ROOT file (condor)
    python3 he3ng_samearm.py reduce <neutrons_jobNNN_t0.root> -o <part.npz>
    # merge -> per-cycle same-arm fakes vs T, and their chord-angle spectrum
    python3 he3ng_samearm.py merge <parts/*.npz> --accounting <contracts/C1g_G1/accounting.json> -o <prefix>

reduce keeps, for every ³He(n,γ) event (capture_vol He3Gas, weight < 0.01),
per arm with any deposit: E_sipm/E_plast/E_ls (MeV), the trigger leg (a SiPM
bar >= 0.5 MIP AND a plastic bar >= 0.5 MIP, ill_pairs definitions), and the
charged DriftGas tracks with >= 3 steps: their count and, for the two with the
most edep, the first-step position, edep, particle, and origin process/volume.

merge counts a same-arm candidate as: leg, E_arm > T, >= 2 such tracks whose
first gap hits are >= SEP mm apart (the definition single_arm.py applies to the
IPC leptons), and bins the chord angle from the origin (nomline-like).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

MIP_S_EV, MIP_P_EV, LEG_MIP = 0.4751e6, 3.3494e6, 0.5
BR = ["eventID", "trackID", "armID", "detType", "particle", "edep", "time", "gx", "gy", "gz",
      "u", "origin_proc", "origin_vol"]
NEUTRAL = {"gamma", "neutron"}
T_LIST = (0.0, 4.0, 8.0, 10.0, 12.0, 13.0, 14.0)
SEP_MM = (0.0, 5.0, 10.0)
TH_BINS = np.arange(0.0, 181.0, 4.0)
DAY = 86400.0


def _s(a):
    return np.array([x.decode() if isinstance(x, bytes) else str(x) for x in a])


def reduce_file(fp, out):
    import uproot
    with uproot.open(fp) as f:
        et = f["EventTree"].arrays(["eventID", "capture_vol", "weight"], library="np")
        sel = (_s(et["capture_vol"]) == "He3Gas") & (et["weight"] < 0.01)
        evs = np.sort(et["eventID"][sel].astype(np.int64))
        wmap = dict(zip(et["eventID"][sel].astype(np.int64).tolist(), et["weight"][sel].astype(float).tolist()))
        cols = {k: [] for k in BR}
        for t in f["HitTree"].iterate(BR, library="np", step_size="300 MB"):
            m = np.isin(t["eventID"].astype(np.int64), evs)
            if m.any():
                for k in BR:
                    cols[k].append(t[k][m])
    t = {k: (np.concatenate(v) if v else np.array([])) for k, v in cols.items()}
    rows = []
    if len(t["eventID"]):
        ev = t["eventID"].astype(np.int64)
        arm = t["armID"].astype(np.int64)
        det = _s(t["detType"])
        prt = _s(t["particle"])
        proc = _s(t["origin_proc"])
        vol = _s(t["origin_vol"])
        edep = t["edep"].astype(float)
        X = np.stack([t["gx"], t["gy"], t["gz"]], 1).astype(float)
        order = np.lexsort((t["time"], ev))
        for e in np.unique(ev):
            ie = order[np.searchsorted(ev[order], e, "left"):np.searchsorted(ev[order], e, "right")]
            for a in np.unique(arm[ie]):
                if a < 0:
                    continue
                ia = ie[arm[ie] == a]
                d = det[ia]
                Es = edep[ia][d == "PlasticScint"].sum() * 1e-6
                Ep = edep[ia][(d == "BackScintL") | (d == "BackScintR")].sum() * 1e-6
                El = edep[ia][d == "LiqScint_1"].sum() * 1e-6
                # leg: one SiPM bar and one plastic bar over 0.5 MIP
                ms = d == "PlasticScint"
                bars = np.clip((t["u"][ia][ms] + 250.0) // 25.0, 0, 19).astype(int)
                sbar = np.bincount(bars, edep[ia][ms], minlength=20).max() if ms.any() else 0.0
                pl = edep[ia][d == "BackScintL"].sum(), edep[ia][d == "BackScintR"].sum()
                leg = (sbar >= LEG_MIP * MIP_S_EV) and (max(pl) >= LEG_MIP * MIP_P_EV)
                g = ia[(d == "DriftGas") & ~np.isin(prt[ia], list(NEUTRAL))]
                trk = []
                if len(g):
                    tid = t["trackID"][g].astype(np.int64)
                    for k in np.unique(tid):
                        gk = g[tid == k]           # time-ordered
                        if len(gk) >= 3:
                            trk.append((edep[gk].sum() * 1e-6, X[gk[0]], prt[gk[0]], proc[gk[0]], vol[gk[0]], len(gk)))
                if Es + Ep + El <= 0 and not trk:
                    continue
                trk.sort(key=lambda x: -x[0])
                r = dict(ev=e, w=wmap[int(e)], arm=a, E_sipm=Es, E_plast=Ep, E_ls=El, leg=leg, ntrk=len(trk),
                         e_gap=sum(x[0] for x in trk))
                for j in (0, 1):
                    if j < len(trk):
                        r.update({f"t{j}_e": trk[j][0], f"t{j}_P": trk[j][1], f"t{j}_part": trk[j][2],
                                  f"t{j}_proc": trk[j][3], f"t{j}_vol": trk[j][4], f"t{j}_n": trk[j][5]})
                    else:
                        r.update({f"t{j}_e": 0.0, f"t{j}_P": np.full(3, np.nan), f"t{j}_part": "",
                                  f"t{j}_proc": "", f"t{j}_vol": "", f"t{j}_n": 0})
                rows.append(r)
    keys = ["ev", "w", "arm", "E_sipm", "E_plast", "E_ls", "leg", "ntrk", "e_gap"] + \
        [f"t{j}_{k}" for j in (0, 1) for k in ("e", "P", "part", "proc", "vol", "n")]
    rec = {k: np.array([r[k] for r in rows]) if rows else np.array([]) for k in keys}
    rec["n_he3ng"] = np.array([len(evs)])
    np.savez_compressed(out, **rec)
    print(f"{fp}: {len(evs)} ³He(n,γ) events, {len(rows)} arm rows -> {out}", flush=True)


def chord(p1, p2):
    c = (p1 * p2).sum(-1) / (np.linalg.norm(p1, axis=-1) * np.linalg.norm(p2, axis=-1))
    return np.degrees(np.arccos(np.clip(c, -1, 1)))


def merge(parts, accounting, prefix, R=6e10, days=50.0):
    import pandas as pd
    absorbed = json.load(open(accounting))["counts"]["absorbed_np"]
    zs = [dict(np.load(p, allow_pickle=True)) for p in parts]
    zs = [z for z in zs if len(z["ev"])]
    z = {k: np.concatenate([q[k] for q in zs]) for k in zs[0] if k != "n_he3ng"}
    nabs = R * days * DAY
    per = z["w"].astype(float) / absorbed * nabs           # per cycle
    E = z["E_sipm"] + z["E_plast"] + z["E_ls"]
    sep = np.linalg.norm(z["t0_P"].astype(float) - z["t1_P"].astype(float), axis=1)
    th = chord(z["t0_P"].astype(float), z["t1_P"].astype(float))
    leg = z["leg"].astype(bool)
    rows, hrows = [], []
    for T in T_LIST:
        base = leg & (E > T)
        mm = base & (z["ntrk"] >= 1)
        rows.append(dict(T=T, sep_mm=np.nan, kind="leg+E", per_cycle=per[base].sum(), n_mc=int(base.sum())))
        rows.append(dict(T=T, sep_mm=np.nan, kind="leg+E+MM track", per_cycle=per[mm].sum(), n_mc=int(mm.sum())))
        for s in SEP_MM:
            m = base & (z["ntrk"] >= 2) & (np.nan_to_num(sep) >= s)
            rows.append(dict(T=T, sep_mm=s, kind="two tracks", per_cycle=per[m].sum(), n_mc=int(m.sum())))
            if s == 5.0 and T in (10.0, 13.0):
                h, _ = np.histogram(th[m], TH_BINS, weights=per[m])
                n, _ = np.histogram(th[m], TH_BINS)
                for lo, v, c in zip(TH_BINS[:-1], h, n):
                    hrows.append(dict(T=T, th_lo=lo, per_cycle=v, n_mc=int(c)))
                o = pd.DataFrame(dict(p0=z["t0_part"][m], p1=z["t1_part"][m], proc0=z["t0_proc"][m],
                                      proc1=z["t1_proc"][m], vol0=z["t0_vol"][m], w=per[m]))
                print(f"\nT {T}, sep >= {s} mm: {m.sum()} MC arms, {per[m].sum():.3g} / cycle; by origin:")
                print(o.groupby(["p0", "p1", "proc0", "proc1", "vol0"]).w.agg(["sum", "count"])
                      .sort_values("sum", ascending=False).head(12).to_string())
    df = pd.DataFrame(rows)
    df.to_csv(f"{prefix}_counts.csv", index=False)
    pd.DataFrame(hrows).to_csv(f"{prefix}_theta.csv", index=False)
    print("\n", df.to_string(index=False))
    print(f"³He(n,γ) events in C1g: {sum(int(q['n_he3ng'][0]) for q in zs)}; absorbed {absorbed:.3g}; wrote {prefix}_*.csv")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("reduce")
    r.add_argument("file")
    r.add_argument("-o", "--out", required=True)
    m = sub.add_parser("merge")
    m.add_argument("parts", nargs="+")
    m.add_argument("--accounting", required=True)
    m.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    if a.cmd == "reduce":
        reduce_file(a.file, a.out)
    else:
        merge(a.parts, a.accounting, a.out)


if __name__ == "__main__":
    main()
