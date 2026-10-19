#!/usr/bin/env python3
"""
nfs_beam_reduce.py -- one NFS beam ROOT file -> per-arm scintillator time clusters.

    python3 nfs_beam_reduce.py <neutrons_jobNNN_t0.root> -o <parts_beam/stem.npz>

Beam histories spread over µs to seconds (moderated neutrons, capture γ,
activation decays), so summing an arm's deposits over the whole event (as
ill_pairs.py does for prompt pairs) would glue a prompt recoil to a capture γ
200 µs later.  Here each arm's scintillator hits (SiPM wall, back plastics or
big plastic, LS) are split in time: hits sorted in time, a gap > GAP_NS starts
a new cluster.  Per cluster:

  t0 [ns]                    earliest hit (global time, the gun at t = 0)
  E_sipm, E_plast, E_ls      MeV within the cluster
  leg                        SiPM bar >= 0.5 MIP AND back plastic >= 0.5 MIP
                             (ill_pairs.py definition, per cluster)
  mm_e, mm_n, c_all, c_dom,  the arm's charged DriftGas steps with |t - t0| <
  d_dom, n_dom, fdom         MM_WIN_NS, fitted as seg_reduce.py does (0.5 mm smear,
                             PCA of all steps and of the dominant track)

Only clusters with a leg are kept (a single needs one).  Per event with a kept
cluster: En [MeV], w (EventTree ev_weight; 1 in analog runs), force_vol.
n_generated and the --force-beam checks are over all events (as nfs_reduce.py).
"""
from __future__ import annotations

import argparse
import sys
import zlib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from seg_reduce import _pca, SMEAR_MM, NEUTRAL      # noqa: E402

GAP_NS = 50.0
MM_WIN_NS = 100.0
MIP_S_EV, MIP_P_EV, LEG_MIP = 0.4751e6, 3.3494e6, 0.5    # ill_pairs.py
SCINT = ("PlasticScint", "BackScintL", "BackScintR", "LiqScint_1")
BR = ["eventID", "trackID", "armID", "detType", "particle", "u", "edep", "gx", "gy", "gz", "time"]


def _s(a):
    return np.array([x.decode() if isinstance(x, bytes) else str(x) for x in a])


def clusters(S):
    """S: scintillator hits.  Returns per-hit cluster index and the cluster table."""
    key = S["ev"] * 4 + S["arm"]
    o = np.lexsort((S["t"], key))
    S = {k: v[o] for k, v in S.items()}
    key = key[o]
    new = np.r_[True, (np.diff(key) != 0) | (np.diff(S["t"]) > GAP_NS)]
    cid = np.cumsum(new) - 1
    nc = int(cid[-1]) + 1
    first = np.nonzero(new)[0]
    C = dict(ev=S["ev"][first], arm=S["arm"][first], t0=S["t"][first])
    det = S["det"]
    for name, m in (("E_sipm", det == "PlasticScint"),
                    ("E_plast", (det == "BackScintL") | (det == "BackScintR")),
                    ("E_ls", det == "LiqScint_1")):
        C[name] = np.bincount(cid[m], S["e"][m] * 1e-6, minlength=nc).astype(np.float32)
    # legs: channel sums inside the cluster
    sc = det != "LiqScint_1"
    ch = np.where(det[sc] == "PlasticScint", np.clip((S["u"][sc] + 250.0) // 25.0, 0, 19),
                  np.where(det[sc] == "BackScintL", 20, 21)).astype(np.int64)
    k = cid[sc] * 22 + ch
    uk, inv = np.unique(k, return_inverse=True)
    s = np.bincount(inv, S["e"][sc])
    s_ok = (uk % 22 < 20) & (s >= LEG_MIP * MIP_S_EV)
    p_ok = (uk % 22 >= 20) & (s >= LEG_MIP * MIP_P_EV)
    leg = np.zeros(nc, bool)
    leg[np.intersect1d(uk[s_ok] // 22, uk[p_ok] // 22)] = True
    C["leg"] = leg
    return C


def mm_segments(C, M, rng):
    """Attach the DriftGas steps within MM_WIN_NS of each kept cluster and fit them."""
    nc = len(C["ev"])
    out = dict(mm_e=np.zeros(nc, np.float32), mm_n=np.zeros(nc, np.float32),
               c_all=np.full((nc, 3), np.nan, np.float32), c_dom=np.full((nc, 3), np.nan, np.float32),
               d_dom=np.full((nc, 3), np.nan, np.float32), n_dom=np.zeros(nc, np.float32),
               fdom=np.zeros(nc, np.float32))
    if not nc or not len(M["ev"]):
        return out
    ck = C["ev"] * 4 + C["arm"]
    o = np.argsort(ck, kind="stable")
    cks = ck[o]
    mk = M["ev"] * 4 + M["arm"]
    lo = np.searchsorted(cks, mk, "left")
    hi = np.searchsorted(cks, mk, "right")
    assign = np.full(len(mk), -1, np.int64)
    for j in range(int((hi - lo).max()) if len(mk) else 0):      # clusters per (ev, arm): few
        cand = lo + j
        ok = (cand < hi) & (assign < 0)
        c = o[np.clip(cand, 0, len(o) - 1)]
        hit = ok & (np.abs(M["t"] - C["t0"][c]) < MM_WIN_NS)
        assign[hit] = c[hit]
    m = assign >= 0
    if not m.any():
        return out
    inv, e, tid = assign[m], M["e"][m] * 1e-6, M["tid"][m]
    X = M["X"][m] + rng.normal(0, SMEAR_MM, M["X"][m].shape)
    out["mm_e"] = np.bincount(inv, e, minlength=nc).astype(np.float32)
    n, c, _, _ = _pca(inv, X, nc)
    out["mm_n"], out["c_all"] = n.astype(np.float32), c.astype(np.float32)
    # dominant track per cluster
    T = int(tid.max()) + 1
    k2 = inv * T + tid
    u2, i2 = np.unique(k2, return_inverse=True)
    e2 = np.bincount(i2, e)
    g2 = u2 // T
    order = np.lexsort((-e2, g2))
    firstk = np.r_[True, g2[order][1:] != g2[order][:-1]]
    dom = np.full(nc, -1, np.int64)
    dom[g2[order][firstk]] = u2[order][firstk]
    fd = np.zeros(nc)
    fd[g2[order][firstk]] = e2[order][firstk]
    out["fdom"] = (fd / np.maximum(out["mm_e"], 1e-30)).astype(np.float32)
    md = k2 == dom[inv]
    nd, cd, dd, _ = _pca(inv[md], X[md], nc)
    out["n_dom"], out["c_dom"], out["d_dom"] = nd.astype(np.float32), cd.astype(np.float32), dd.astype(np.float32)
    out["c_all"][n == 0] = np.nan
    return out


def main():
    import uproot
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    rng = np.random.default_rng(zlib.crc32(Path(a.file).name.encode()))
    S = {k: [] for k in ("ev", "arm", "t", "e", "det", "u")}
    M = {k: [] for k in ("ev", "arm", "t", "e", "tid", "X")}
    with uproot.open(a.file) as f:
        for t in f["HitTree"].iterate(BR, library="np", step_size="200 MB"):
            det = _s(t["detType"])
            ms = np.isin(det, SCINT) & (t["edep"] > 0)
            for k, v in (("ev", t["eventID"]), ("arm", t["armID"]), ("t", t["time"]),
                         ("e", t["edep"]), ("det", det), ("u", t["u"])):
                S[k].append(v[ms])
            mm = (det == "DriftGas") & ~np.isin(_s(t["particle"]), list(NEUTRAL))
            for k, v in (("ev", t["eventID"]), ("arm", t["armID"]), ("t", t["time"]),
                         ("e", t["edep"]), ("tid", t["trackID"])):
                M[k].append(v[mm])
            M["X"].append(np.stack([t["gx"][mm], t["gy"][mm], t["gz"][mm]], 1))
        et = f["EventTree"]
        forced = "ev_weight" in et.keys()
        T = et.arrays(["eventID", "neutron_E_eV"] + (["ev_weight", "force_vol", "force_tau", "force_w",
                                                     "force_done", "n_arms_pred", "killed"] if forced else []),
                      library="np")
    S = {k: np.concatenate(v) for k, v in S.items()}
    M = {k: np.concatenate(v) for k, v in M.items()}
    for D in (S, M):
        D["ev"] = D["ev"].astype(np.int64)
        D["arm"] = D["arm"].astype(np.int64)
        D["t"] = D["t"].astype(np.float64)
        D["e"] = D["e"].astype(np.float64)
    M["tid"] = M["tid"].astype(np.int64)
    M["X"] = M["X"].astype(np.float64)

    N = len(T["eventID"])
    P = {}
    if len(S["ev"]):
        C = clusters(S)
        n_cl_arm = np.bincount(C["arm"], minlength=4)
        keep = C["leg"]
        C = {k: v[keep] for k, v in C.items()}
        C.update(mm_segments(C, M, rng))
    else:
        C, n_cl_arm = {}, np.zeros(4, int)
    if C and len(C["ev"]):
        j = np.searchsorted(T["eventID"], C["ev"])
        P = {f"cl_{k}": v for k, v in C.items() if k != "leg"}
        P["cl_En"] = (T["neutron_E_eV"][j] * 1e-6).astype(np.float32)
        P["cl_w"] = (T["ev_weight"][j] if forced else np.ones(len(j))).astype(np.float64)
        if forced:
            P["cl_force_vol"] = np.array([x.decode() if isinstance(x, bytes) else str(x)
                                          for x in T["force_vol"][j]]).astype("U24")
    P["n_generated"] = np.array([N])
    P["n_clusters_arm"] = n_cl_arm[None, :]
    if forced:
        tau, fw, done = T["force_tau"], T["force_w"], T["force_done"].astype(bool)
        expect = -np.expm1(-tau)
        dev = np.abs(fw[done] / np.where(expect[done] > 0, expect[done], 1) - 1)
        nap = T["n_arms_pred"]
        P.update(diag_w_sum=np.array([T["ev_weight"].sum()]),
                 diag_n_host=np.array([(tau > 0).sum()]), diag_n_done=np.array([done.sum()]),
                 diag_fw_dev_mean=np.array([dev.mean() if len(dev) else 0.0]),
                 diag_fw_dev_max=np.array([dev.max() if len(dev) else 0.0]),
                 diag_n_killed=np.array([T["killed"].sum()]),
                 diag_n_arms=np.array([[(nap == k).sum() for k in (-1, 0, 1, 2, 3, 4)]]))
    np.savez_compressed(a.out, **P)
    nk = len(P.get("cl_ev", []))
    print(f"{a.file}: {N} events, {nk} leg clusters -> {a.out}")


if __name__ == "__main__":
    main()
