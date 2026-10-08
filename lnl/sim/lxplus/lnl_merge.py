#!/usr/bin/env python3
"""
lnl_merge.py -- lnl_reduce parts of one sample -> compact two-arm table.

    python3 lnl_merge.py <parts/*.npz> -o <sample>_sel.npz

Data-like selection, the same for pairs, γ lines and cosmics:
  an arm is "ok" if it has a trigger leg (SiPM AND plastic, ill_pairs) and a
  Micromegas segment (dominant track, >= 3 steps) whose charge centroid lies in
  the active area (|along beam| < 180 mm, |transverse - pinwheel shift| < 199.7 mm).
  Events with >= 2 ok arms are kept; the two arms with the most scintillator
  energy are the pair.

Kept per event: truth (type, W or E_γ, θ, lepton KE), the reconstructed opening
angle from the assumed vertex (0,0,0) to the two MM charge centroids (reco_c),
the same with the truth first hits (reco_first, pairs only), the two arms'
segments (c_dom, d_dom, fdom, n_dom) for the pointing / collinearity cuts,
and the calorimetry (E_sipm, E_plast, E_ls of the two arms, E of all arms).
counts: n_generated; per-arm leg singles; MM-geometry acceptance (pairs).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

HALF_ALONG, HALF_TRANS = 180.0, 199.7
#: transverse pinwheel offset of each arm's MM centre, mm (geometry log:
#: arm front faces at (20.4,0,1.55) (-20.4,0,-1.575) (-1.635,0,20.45) (1.73,0,-20.45) cm)
SHIFT = np.array([15.5, -15.75, -16.35, 17.3])
TRANS_AX = np.array([2, 2, 0, 0])          # arms 0/1 sit at ±x (transverse = z), 2/3 at ±z


def _ang(a, b):
    c = (a * b).sum(-1) / (np.linalg.norm(a, axis=-1) * np.linalg.norm(b, axis=-1))
    return np.degrees(np.arccos(np.clip(c, -1, 1)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("parts", nargs="+")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    R, ngen = {}, 0
    have_t = all((Path(p).parent.parent / "parts_time" / Path(p).name).exists() for p in a.parts)
    for p in a.parts:
        z = np.load(p)
        ngen += int(z["n_generated"].sum())
        for k in z.files:
            if k != "n_generated":
                R.setdefault(k, []).append(z[k])
        if have_t:                        # lnl_time.py: earliest scintillator time per arm
            T = np.load(Path(p).parent.parent / "parts_time" / Path(p).name)
            ev = z["eventID"]
            i = np.clip(np.searchsorted(T["ev"], ev), 0, max(len(T["ev"]) - 1, 0))
            hit = (T["ev"][i] == ev) if len(T["ev"]) else np.zeros(len(ev), bool)
            for k in ("t_sipm", "t_plast"):
                arr = np.full((len(ev), 4), np.nan, np.float32)
                arr[hit] = T[k][i[hit]]
                R.setdefault(k, []).append(arr)
    R = {k: np.concatenate(v) for k, v in R.items()}
    N = len(R["eventID"])
    C = R["seg_c_all"].astype(float)                       # (N,4,3)
    arms = np.arange(4)
    trans = C[:, arms, TRANS_AX] - SHIFT[None, :]
    active = (np.abs(C[:, :, 1]) < HALF_ALONG) & (np.abs(trans) < HALF_TRANS)
    mm_ok = (R["seg_n_dom"] >= 3) & (R["seg_e"] > 0) & active
    legs = R["legs"].astype(np.int64)
    leg = ((legs[:, None] >> arms[None, :]) & 1).astype(bool)
    ok = leg & mm_ok
    Earm = (R["E_sipm"] + R["E_plast"] + R["E_ls"]).astype(float)
    nok = ok.sum(1)
    sel = nok >= 2
    E_ = np.where(ok, Earm, -1.0)
    o = np.argsort(-E_, axis=1)
    a1, a2 = o[:, 0], o[:, 1]
    r = np.arange(N)

    counts = dict(n_generated=ngen, n_rows=N,
                  leg_any=int((legs != 0).sum()), leg_arm=leg.sum(0).tolist(),
                  mm_ok_arm=mm_ok.sum(0).tolist(), ok_arm=ok.sum(0).tolist(),
                  n_ok2=int(sel.sum()), trig2=int((leg.sum(1) >= 2).sum()))
    if (R["event_type"] == 3).any():           # γ lines: singles per line (lines drawn ∝ w)
        lines = np.unique(np.round(R["inv_mass"], 4))
        lm = [np.isclose(R["inv_mass"], L, atol=1e-3) for L in lines]
        counts.update(lines=lines.tolist(),
                      line_leg_any=[int((legs[m] != 0).sum()) for m in lm],
                      line_leg_arm=[leg[m].sum(0).tolist() for m in lm],
                      line_trig2=[int((leg[m].sum(1) >= 2).sum()) for m in lm],
                      line_ok2=[int(sel[m].sum()) for m in lm],
                      line_mm_any=[int(mm_ok[m].any(1).sum()) for m in lm])
    if "em_arm" in R and np.isin(R["event_type"], (0, 1)).all():
        ea, pa = R["em_arm"].astype(int), R["ep_arm"].astype(int)
        two = (ea >= 0) & (pa >= 0) & (ea != pa)
        two_act = two & active[r, np.clip(ea, 0, 3)] & active[r, np.clip(pa, 0, 3)]
        counts.update(mm_2arm=int(two.sum()), mm_2arm_active=int(two_act.sum()))

    s = sel
    rs, b1, b2 = r[s], a1[s], a2[s]
    out = dict(event_type=R["event_type"][s], inv_mass=R["inv_mass"][s], theta=R["theta"][s],
               em_ke=R["em_ke"][s], ep_ke=R["ep_ke"][s], V=R["V"][s], legs=R["legs"][s],
               nok=nok[s].astype(np.int8), a1=b1.astype(np.int8), a2=b2.astype(np.int8),
               reco_c=_ang(C[rs, b1], C[rs, b2]).astype(np.float32),
               E1=Earm[rs, b1].astype(np.float32), E2=Earm[rs, b2].astype(np.float32),
               E_all=Earm[s].astype(np.float32),
               E_sipm2=(R["E_sipm"][rs, b1] + R["E_sipm"][rs, b2]).astype(np.float32),
               E_plast2=(R["E_plast"][rs, b1] + R["E_plast"][rs, b2]).astype(np.float32),
               E_ls2=(R["E_ls"][rs, b1] + R["E_ls"][rs, b2]).astype(np.float32),
               seg_e=R["seg_e"][s])
    for tag, b in (("1", b1), ("2", b2)):
        for k in ("c_dom", "d_dom", "c_all"):
            out[f"{k}{tag}"] = R[f"seg_{k}"][rs, b].astype(np.float32)
        out[f"fdom{tag}"] = R["seg_fdom"][rs, b].astype(np.float32)
        out[f"ndom{tag}"] = R["seg_n_dom"][rs, b].astype(np.float32)
    if "t_sipm" in R:
        for k in ("t_sipm", "t_plast"):
            out[f"{k}1"] = R[k][rs, b1]
            out[f"{k}2"] = R[k][rs, b2]
    if "em_P" in R:
        Pm, Pp = R["em_P"][s].astype(float), R["ep_P"][s].astype(float)
        out["reco_first"] = _ang(Pm, Pp).astype(np.float32)
        ea, pa = R["em_arm"][s].astype(int), R["ep_arm"][s].astype(int)
        out["truth_arms"] = (((ea == b1) & (pa == b2)) | ((ea == b2) & (pa == b1))).astype(np.int8)
    if not np.isin(R["event_type"], (0, 1)).all():
        # γ lines / cosmics: every ok arm as a single (for accidental pairing)
        ie, ia = np.nonzero(ok)
        out.update(sg_arm=ia.astype(np.int8), sg_E=Earm[ie, ia].astype(np.float32),
                   sg_line=R["inv_mass"][ie].astype(np.float32),
                   sg_c_all=R["seg_c_all"][ie, ia].astype(np.float32),
                   sg_c_dom=R["seg_c_dom"][ie, ia].astype(np.float32),
                   sg_d_dom=R["seg_d_dom"][ie, ia].astype(np.float32),
                   sg_nok=nok[ie].astype(np.int8))
        if "t_sipm" in R:
            out["sg_t_sipm"] = R["t_sipm"][ie, ia]
    for k, v in counts.items():
        out[f"cnt_{k}"] = np.array(v)
    np.savez_compressed(a.out, **out)
    print(f"{a.out}: {ngen:,} generated, {N:,} rows, {int(sel.sum()):,} with >= 2 ok arms")
    print("  ", counts)


if __name__ == "__main__":
    main()
