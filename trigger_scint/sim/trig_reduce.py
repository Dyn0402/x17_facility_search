#!/usr/bin/env python3
"""
trig_reduce.py -- per-lepton trigger-scintillator table from one MX17 pair file
===============================================================================
    python3 trig_reduce.py <pairs_jobNNN_t0.root> -o <part.npz>

Input: an MX17_Full_Geant (branch trigger_plastics) pair run, either
  T0  as-built stack (2 x 20x30x2 cm plastics + LS), all 20 SiPM bars present
  T1  --big-plastic 78 120 10 --no-ls --sipm-readout 20 0: one oversized slab
      per arm, from which any smaller centred plastic is cut out here.

Keeps events whose two primary leptons first enter the drift gas of two
DIFFERENT arms.  Per lepton (em, ep), for the arm it entered:
  arm, gap_uv      first drift-gas hit, MM frame (active-area cut is offline)
  sipm[20]         edep per SiPM-wall bar (all particles), MeV; bar index in
                   the STRUCTURE frame, u_struct = u_MM - pinwheel shift
  T0: plastL, plastR, ls  (MeV)
  T1: grid[W, L, T]  edep (MeV) inside the centred sub-slab |u| < W/2,
                   |v| < L/2, depth < T, for the W/L/T lists below
      ent_uv       where the primary lepton first enters the slab (or nan)
Truth: theta, em_ke, ep_ke, V.  n_generated is stored for normalisation.
"""
import argparse
import numpy as np

W_CM = np.array([30, 40, 50, 60, 70, 78], float)
L_CM = np.array([30, 40, 50, 60, 70, 80, 100, 120], float)
T_CM = np.array([1, 2, 3, 4, 5, 6, 8, 10], float)
PIN_MM = np.array([15.5, 15.75, 16.35, 17.3])
GAP_SIPM_PLAST_CM = np.array([6.5, 6.1, 6.3, 6.1])
PLAST_FRONT_MM = 145.0 + 10 * GAP_SIPM_PLAST_CM + 0.22   # scint face (inside tape + Al)
BR = ["eventID", "parentID", "armID", "detType", "particle", "u", "v", "w", "edep"]


def _s(a):
    return np.array([x.decode() if isinstance(x, bytes) else str(x) for x in a])


def reduce_file(fp, out, step="300 MB"):
    import uproot
    with uproot.open(fp) as f:
        et = f["EventTree"].arrays(["eventID", "openingAngle", "em_ke", "ep_ke",
                                    "vtx_x", "vtx_y", "vtx_z"], library="np")
        emax = int(et["eventID"].max()) + 1
        nW, nL, nT = len(W_CM), len(L_CM), len(T_CM)
        arm = {p: np.full(emax, -1, np.int8) for p in ("em", "ep")}
        guv = {p: np.full((emax, 2), np.nan, np.float32) for p in ("em", "ep")}
        euv = {p: np.full((emax, 2), np.nan, np.float32) for p in ("em", "ep")}
        sipm = np.zeros((emax, 4, 20), np.float32)
        plL = np.zeros((emax, 4), np.float32)
        plR = np.zeros((emax, 4), np.float32)
        ls = np.zeros((emax, 4), np.float32)
        grid = {}                                  # (event*4+arm) -> [nW,nL,nT]
        big = [False]

        def process(t):
            det = _s(t["detType"])
            ev = t["eventID"].astype(np.int64)
            a = t["armID"].astype(np.int64)
            e = t["edep"] * 1e-6
            m = det == "PlasticScint"
            if m.any():
                bar = np.clip(np.floor((t["u"][m] - PIN_MM[a[m]] + 250.0) / 25.0), 0, 19).astype(int)
                np.add.at(sipm, (ev[m], a[m], bar), e[m])
            m = det == "LiqScint_1"
            if m.any():
                np.add.at(ls, (ev[m], a[m]), e[m])
            m = det == "BackScintR"
            if m.any():
                np.add.at(plR, (ev[m], a[m]), e[m])
            m = det == "BackScintL"
            if m.any():
                np.add.at(plL, (ev[m], a[m]), e[m])
                if big[0]:
                    au, av = np.abs(t["u"][m]) / 10, np.abs(t["v"][m]) / 10
                    dw = (t["w"][m] - PLAST_FRONT_MM[a[m]]) / 10
                    iW = np.searchsorted(W_CM / 2, au, side="right")   # first W with W/2 > au
                    iL = np.searchsorted(L_CM / 2, av, side="right")
                    iT = np.searchsorted(T_CM, dw, side="right")
                    k = ev[m] * 4 + a[m]
                    ok = (iW < nW) & (iL < nL) & (iT < nT)
                    uk, inv = np.unique(k[ok], return_inverse=True)
                    H = np.zeros((len(uk), nW, nL, nT))
                    np.add.at(H, (inv, iW[ok], iL[ok], iT[ok]), e[m][ok])
                    H = H.cumsum(1).cumsum(2).cumsum(3)
                    for kk, h in zip(uk.tolist(), H):
                        grid[kk] = grid.get(kk, 0) + h.astype(np.float32)
            prt = _s(t["particle"])
            for p, name in (("em", "e-"), ("ep", "e+")):
                pm = (t["parentID"] == 0) & (prt == name)
                for d_, store in (("DriftGas", guv), ("BackScintL", euv)):
                    mm = pm & (det == d_)
                    if not mm.any():
                        continue
                    ue, first = np.unique(ev[mm], return_index=True)
                    idx = np.flatnonzero(mm)[first]
                    new = np.isnan(store[p][ue, 0])
                    store[p][ue[new]] = np.stack([t["u"][idx], t["v"][idx]], 1)[new]
                    if d_ == "DriftGas":
                        arm[p][ue[new]] = a[idx][new]

        carry = None
        for t in f["HitTree"].iterate(BR, library="np", step_size=step):
            if not big[0]:
                big[0] = bool(np.any(np.abs(t["v"][_s(t["detType"]) == "BackScintL"]) > 160))
            if carry is not None:
                t = {k: np.concatenate([carry[k], t[k]]) for k in t}
            cut = np.searchsorted(t["eventID"], t["eventID"][-1], side="left")
            carry = {k: v[cut:] for k, v in t.items()}
            if cut:
                process({k: v[:cut] for k, v in t.items()})
        if carry is not None and len(carry["eventID"]):
            process(carry)

    e = et["eventID"].astype(np.int64)
    am, ap = arm["em"][e], arm["ep"][e]
    sel = (am >= 0) & (ap >= 0) & (am != ap)
    e = e[sel]
    rec = dict(n_generated=np.array([len(et["eventID"])]), big=np.array([big[0]]),
               W_cm=W_CM, L_cm=L_CM, T_cm=T_CM,
               theta=et["openingAngle"][sel].astype(np.float32),
               em_ke=et["em_ke"][sel].astype(np.float32), ep_ke=et["ep_ke"][sel].astype(np.float32),
               V=np.stack([et["vtx_x"], et["vtx_y"], et["vtx_z"]], 1)[sel].astype(np.float32))
    zero = np.zeros((len(W_CM), len(L_CM), len(T_CM)), np.float32)
    for p in ("em", "ep"):
        ar = arm[p][e].astype(np.int64)
        rec[f"{p}_arm"] = ar.astype(np.int8)
        rec[f"{p}_gap_uv"] = guv[p][e]
        rec[f"{p}_sipm"] = sipm[e, ar]
        if big[0]:
            rec[f"{p}_grid"] = np.stack([grid.get(int(k), zero) for k in (e * 4 + ar)])
            rec[f"{p}_ent_uv"] = euv[p][e]
        else:
            rec[f"{p}_plastL"], rec[f"{p}_plastR"], rec[f"{p}_ls"] = plL[e, ar], plR[e, ar], ls[e, ar]
    np.savez_compressed(out, **rec)
    print(f"{fp}: {len(et['eventID'])} events, {sel.sum()} two-arm kept (big={big[0]}) -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    reduce_file(a.root, a.out)
