#!/usr/bin/env python3
"""
soft_beam_merge.py -- nfs_beam_merge.py plus the per-row tables a re-weighted soft-source
analysis needs (x17_facility_search/survey/soft_sim): every leg cluster (lg_*: weight,
parent E, arm, time, energy) and every two-arm trigger pair (tr_*), so the trigger rate,
not only the "ok" singles, can be re-weighted by the parent energy.

    python3 soft_beam_merge.py <parts_beam/*.npz> -o <sample>_sel.npz

A cluster is an "ok" single when it has a leg (kept by the reducer) and a
Micromegas segment (dominant track >= 3 steps) whose charge centroid lies in
the active area (nfs_merge.py definitions).  Two clusters of the same event in
different arms within COINC_NS form a correlated two-arm event (every such
pair; an event can have more than one, e.g. prompt and delayed).  Accidental
pairs of singles from different neutrons are built in the analysis
(nfs_reach.py) from the sg_* table.

Weights: w per row (forced/roulette event weight; 1 in analog runs).  Rates per
generated neutron are sums of w over n_generated.
"""
from __future__ import annotations

import argparse

import numpy as np

from nfs_merge import HALF_ALONG, HALF_TRANS, SHIFT, TRANS_AX, _ang

COINC_NS = 5.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("parts", nargs="+")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    R, D, ngen, ncl = {}, {}, 0, np.zeros(4)
    for i, p in enumerate(a.parts):
        z = np.load(p)
        ngen += int(z["n_generated"].sum())
        ncl += z["n_clusters_arm"].sum(0)
        for k in z.files:
            if k.startswith("diag_"):
                D.setdefault(k, []).append(z[k])
            elif k.startswith("cl_"):
                R.setdefault(k[3:], []).append(z[k])
        if "cl_ev" in z.files:
            R.setdefault("file", []).append(np.full(len(z["cl_ev"]), i, np.int64))
    R = {k: np.concatenate(v) for k, v in R.items()}
    N = len(R.get("ev", []))
    gev = R["file"] * 10**9 + R["ev"] if N else np.zeros(0, np.int64)
    C = R["c_all"].astype(float) if N else np.zeros((0, 3))
    arm = R["arm"].astype(int) if N else np.zeros(0, int)
    trans = C[np.arange(N), TRANS_AX[arm]] - SHIFT[arm] if N else np.zeros(0)
    active = (np.abs(C[:, 1]) < HALF_ALONG) & (np.abs(trans) < HALF_TRANS)
    ok = (R["n_dom"] >= 3) & (R["mm_e"] > 0) & active if N else np.zeros(0, bool)
    w = R["w"] if N else np.zeros(0)
    E = (R["E_sipm"] + R["E_plast"] + R["E_ls"]).astype(float) if N else np.zeros(0)

    def coinc(mask):
        """index pairs (i, j) of clusters passing mask: same event, different arm, |Δt| < COINC_NS"""
        idx = np.nonzero(mask)[0]
        o = idx[np.lexsort((R["t0"][idx], gev[idx]))]
        I, J = [], []
        for s in range(1, 8):                       # neighbours in (event, time) order
            a_, b_ = o[:-s], o[s:]
            m = (gev[a_] == gev[b_]) & (np.abs(R["t0"][b_] - R["t0"][a_]) < COINC_NS) & (arm[a_] != arm[b_])
            I.append(a_[m])
            J.append(b_[m])
        return np.concatenate(I), np.concatenate(J)

    li, lj = coinc(np.ones(N, bool)) if N else (np.zeros(0, int),) * 2       # two-arm triggers
    I, J = coinc(ok) if N else (np.zeros(0, int),) * 2
    sw = E[I] < E[J]                                  # arm 1 = more energy
    I, J = np.where(sw, J, I), np.where(sw, I, J)

    counts = dict(n_generated=ngen, n_rows=len(I), clusters_arm=ncl.tolist(),
                  leg_arm=np.bincount(arm, minlength=4).tolist(),
                  ok_arm=np.bincount(arm[ok], minlength=4).tolist(),
                  w_leg_any=float(w.sum()), w_leg_arm=np.bincount(arm, w, minlength=4).tolist(),
                  w_ok_arm=np.bincount(arm[ok], w[ok], minlength=4).tolist(),
                  trig2=len(li), w_trig2=float(w[li].sum()), n_ok2=len(I), w_n_ok2=float(w[I].sum()),
                  leg_any=N)
    out = dict(w=w[I], En=R["En"][I], event_type=np.full(len(I), 2, np.int8),
               V=np.zeros((len(I), 3), np.float32), a1=arm[I].astype(np.int8), a2=arm[J].astype(np.int8),
               reco_c=_ang(C[I], C[J]).astype(np.float32), E1=E[I].astype(np.float32), E2=E[J].astype(np.float32),
               t_sipm1=R["t0"][I], t_sipm2=R["t0"][J])
    for tag, b in (("1", I), ("2", J)):
        for k in ("c_dom", "d_dom", "c_all"):
            out[f"{k}{tag}"] = R[k][b].astype(np.float32)
        out[f"fdom{tag}"] = R["fdom"][b]
        out[f"ndom{tag}"] = R["n_dom"][b]
    for k in ("E_sipm", "E_plast", "E_ls"):
        out[f"{k}_a"] = np.stack([R[k][I], R[k][J]], 1).astype(np.float32)
    s = np.nonzero(ok)[0]
    out.update(sg_w=w[s], sg_En=R["En"][s], sg_ev=gev[s], sg_arm=arm[s].astype(np.int8),
               sg_E=E[s].astype(np.float32), sg_E_sipm=R["E_sipm"][s], sg_E_plast=R["E_plast"][s],
               sg_E_ls=R["E_ls"][s], sg_c_all=R["c_all"][s], sg_c_dom=R["c_dom"][s],
               sg_d_dom=R["d_dom"][s], sg_t_sipm=R["t0"][s])
    out.update(lg_w=w, lg_En=R["En"], lg_arm=arm.astype(np.int8), lg_t=R["t0"], lg_E=E.astype(np.float32),
               lg_ok=ok, tr_w=w[li], tr_En=R["En"][li], tr_t=np.fmin(R["t0"][li], R["t0"][lj]))
    if "force_vol" in R:
        out["force_vol"] = R["force_vol"][I]
        out["first_vol"] = R["force_vol"][I]
        out["sg_force_vol"] = R["force_vol"][s]
    if D:
        dd = {k: np.concatenate(v) for k, v in D.items()}
        nd = dd["diag_n_done"].sum()
        counts.update(diag_w_sum=float(dd["diag_w_sum"].sum()), diag_n_host=int(dd["diag_n_host"].sum()),
                      diag_n_done=int(nd), diag_n_killed=int(dd["diag_n_killed"].sum()),
                      diag_fw_dev_mean=float((dd["diag_fw_dev_mean"] * dd["diag_n_done"]).sum() / max(nd, 1)),
                      diag_fw_dev_max=float(dd["diag_fw_dev_max"].max()),
                      diag_n_arms=dd["diag_n_arms"].sum(0).tolist())
    for k, v in counts.items():
        out[f"cnt_{k}"] = np.array(v)
    np.savez_compressed(a.out, **out)
    print(f"{a.out}: {ngen:,} generated, {N:,} leg clusters, {int(ok.sum()):,} ok singles, "
          f"{len(li):,} two-arm triggers, {len(I):,} ok pairs")
    print("  ", counts)


if __name__ == "__main__":
    main()
