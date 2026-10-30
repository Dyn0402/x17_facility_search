#!/usr/bin/env python3
"""
wall_reduce.py -- per-bar SiPM-wall hits for the selected two-arm events of one
LNL Geant4 file, so that the readout granularity (ganged groups of 4, every bar,
every SiPM) can be emulated offline.

    python3 wall_reduce.py <prefix_jobNNN_t0.root> <parts_lnl/stem.npz> -o <parts_wall/stem.npz>

Selection: the lnl_merge.py "ok arm" (trigger leg = SiPM AND plastic, MM dominant
segment >= 3 steps, centroid in the active area), >= 2 ok arms, the pair = the two
ok arms with the most scintillator energy.  Applied per row, so it is the same as
in the merged sel tables.  Cosmic / gamma samples also keep pairs at any angle.

Written per selected event: the lnl_merge pair fields (reco_c, E1, E2, per-arm
energies, c_dom/d_dom/c_all of both arms, truth), and a sparse list of wall bars
hit in the two pair arms:
    w_row  index into the event arrays     w_slot 0 = pair arm 1, 1 = pair arm 2
    w_bar  0..19 across the wall (+u)      w_E    edep [MeV]
    w_t    earliest hit time [ns]          w_u, w_v, w_w  edep-weighted local [mm]
    w_g    edep-weighted global (x, y, z) [mm]
Bars are centred on the wall structure; local u is measured from the
pinwheel-shifted MM centre, so bar = floor((u - shift)/25 + 10).
"""
from __future__ import annotations

import argparse

import numpy as np

HALF_ALONG, HALF_TRANS = 180.0, 199.7
SHIFT = np.array([15.5, -15.75, -16.35, 17.3])        # transverse MM offsets in global axes (lnl_merge)
TRANS_AX = np.array([2, 2, 0, 0])
PIN_MM = np.array([15.5, 15.75, 16.35, 17.3])          # SimConfig mm_pinwheel_shift_cm, local u
BAR_W, N_BARS = 25.0, 20
BR = ["eventID", "armID", "detType", "u", "v", "w", "time", "edep", "gx", "gy", "gz"]


def _s(a):
    return np.array([x.decode() if isinstance(x, bytes) else str(x) for x in a])


def _ang(a, b):
    c = (a * b).sum(-1) / (np.linalg.norm(a, axis=-1) * np.linalg.norm(b, axis=-1))
    return np.degrees(np.arccos(np.clip(c, -1, 1)))


def select(P):
    C = P["seg_c_all"].astype(float)
    arms = np.arange(4)
    trans = C[:, arms, TRANS_AX] - SHIFT[None, :]
    active = (np.abs(C[:, :, 1]) < HALF_ALONG) & (np.abs(trans) < HALF_TRANS)
    mm_ok = (P["seg_n_dom"] >= 3) & (P["seg_e"] > 0) & active
    legs = P["legs"].astype(np.int64)
    leg = ((legs[:, None] >> arms[None, :]) & 1).astype(bool)
    ok = leg & mm_ok
    Earm = (P["E_sipm"] + P["E_plast"] + P["E_ls"]).astype(float)
    sel = ok.sum(1) >= 2
    o = np.argsort(-np.where(ok, Earm, -1.0), axis=1)
    return sel, o[:, 0], o[:, 1], Earm, ok


def main():
    import uproot
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("parts")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--max-chunks", type=int, default=0, help="test: stop after N HitTree chunks")
    a = ap.parse_args()

    P = dict(np.load(a.parts))
    sel, a1, a2, Earm, ok = select(P)
    r = np.nonzero(sel)[0]
    b1, b2 = a1[r], a2[r]
    ev = P["eventID"][r].astype(np.int64)
    out = dict(eventID=ev, event_type=P["event_type"][r], inv_mass=P["inv_mass"][r], theta=P["theta"][r],
               em_ke=P["em_ke"][r], ep_ke=P["ep_ke"][r], V=P["V"][r], legs=P["legs"][r],
               nok=ok[r].sum(1).astype(np.int8), a1=b1.astype(np.int8), a2=b2.astype(np.int8),
               E1=Earm[r, b1].astype(np.float32), E2=Earm[r, b2].astype(np.float32),
               E_sipm_a=np.stack([P["E_sipm"][r, b1], P["E_sipm"][r, b2]], 1).astype(np.float32),
               E_plast_a=np.stack([P["E_plast"][r, b1], P["E_plast"][r, b2]], 1).astype(np.float32),
               E_ls_a=np.stack([P["E_ls"][r, b1], P["E_ls"][r, b2]], 1).astype(np.float32),
               n_generated=P["n_generated"])
    C = P["seg_c_all"]
    out["reco_c"] = _ang(C[r, b1].astype(float), C[r, b2].astype(float)).astype(np.float32)
    for tag, b in (("1", b1), ("2", b2)):
        for k in ("c_dom", "d_dom", "c_all"):
            out[f"{k}{tag}"] = P[f"seg_{k}"][r, b].astype(np.float32)
    for k in ("em_arm", "ep_arm", "em_P", "ep_P"):
        if k in P:
            out[k] = P[k][r]

    # event -> (row, arm1, arm2) lookup
    order = np.argsort(ev)
    ev_s = ev[order]
    acc = {k: [] for k in ("row", "slot", "bar", "E", "t", "u", "v", "w", "gx", "gy", "gz")}
    if len(ev):
        with uproot.open(a.file) as f:
            for ic, t in enumerate(f["HitTree"].iterate(BR, library="np", step_size="300 MB")):
                if a.max_chunks and ic >= a.max_chunks:
                    break
                m = (t["edep"] > 0) & np.isin(t["eventID"], ev_s)
                if not m.any():
                    continue
                det = _s(t["detType"][m])
                k = det == "PlasticScint"
                if not k.any():
                    continue
                idx = np.nonzero(m)[0][k]
                e = t["eventID"][idx].astype(np.int64)
                arm = t["armID"][idx].astype(np.int64)
                j = order[np.searchsorted(ev_s, e)]
                slot = np.where(arm == b1[j], 0, np.where(arm == b2[j], 1, -1))
                keep = slot >= 0
                idx, j, slot, arm = idx[keep], j[keep], slot[keep], arm[keep]
                u = t["u"][idx]
                bar = np.floor((u - PIN_MM[arm]) / BAR_W + N_BARS / 2).astype(np.int64)
                acc["row"].append(j); acc["slot"].append(slot); acc["bar"].append(bar)
                acc["E"].append(t["edep"][idx] * 1e-6); acc["t"].append(t["time"][idx])
                for c in ("u", "v", "w", "gx", "gy", "gz"):
                    acc[c].append(t[c][idx])
    if acc["row"]:
        H = {k: np.concatenate(v) for k, v in acc.items()}
        key = (H["row"] * 2 + H["slot"]) * 64 + (H["bar"] + 20)
        uk, inv = np.unique(key, return_inverse=True)
        E = np.bincount(inv, H["E"])
        tmin = np.full(len(uk), np.inf)
        np.minimum.at(tmin, inv, H["t"])
        wav = {c: np.bincount(inv, H["E"] * H[c]) / np.maximum(E, 1e-30) for c in ("u", "v", "w", "gx", "gy", "gz")}
        out.update(w_row=(uk // 128).astype(np.int32), w_slot=((uk // 64) % 2).astype(np.int8),
                   w_bar=(uk % 64 - 20).astype(np.int8), w_E=E.astype(np.float32), w_t=tmin.astype(np.float32),
                   w_u=wav["u"].astype(np.float32), w_v=wav["v"].astype(np.float32), w_w=wav["w"].astype(np.float32),
                   w_g=np.stack([wav["gx"], wav["gy"], wav["gz"]], 1).astype(np.float32))
    else:
        for k, dt in (("w_row", np.int32), ("w_slot", np.int8), ("w_bar", np.int8), ("w_E", np.float32),
                      ("w_t", np.float32), ("w_u", np.float32), ("w_v", np.float32), ("w_w", np.float32)):
            out[k] = np.zeros(0, dt)
        out["w_g"] = np.zeros((0, 3), np.float32)
    np.savez_compressed(a.out, **out)
    nb = len(out["w_row"])
    print(f"{a.file}: {len(ev)} selected events, {nb} bar hits, bars {out['w_bar'].min() if nb else '-'}"
          f"..{out['w_bar'].max() if nb else '-'} -> {a.out}")


if __name__ == "__main__":
    main()
