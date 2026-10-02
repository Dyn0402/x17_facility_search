#!/usr/bin/env python3
"""
acc_sources.py -- where do the accidental singles come from?

The accidental background (sim_feasibility ACC) is two single arms from two
different neutrons inside 2*tau.  This splits it by the volume where each
single's neutron was captured (the table's `capvol`), and asks what the reach
would be if one material's singles were gone.

    python3 acc_sources.py --cfg G1 -o acc_sources_G1.json     # on lxplus, ~3 min

Attribution is by the capture volume of the event's neutron, not traced per
particle.  Selection: sipm2 arm, Esum > 13 MeV, chord angle 60-180 deg (the
fit window), as in sim_feasibility.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sim_feasibility as sf          # noqa: E402
R_MAX = 1.9e10                        # beam maximum, as sim_variants.R_MAX

E = Path("/eos/experiment/ntof/data/x17/ill")
MENU, ECUT = "sipm2", 13.0
HARD = 6.0                            # MeV: a single that can reach the cut with a typical partner


def volume(v):
    """capvol -> (fine source, material)."""
    v = str(v)
    if v == "He3Gas":
        return "³He gas", "³He"
    if v.startswith("He3Cell_Window"):
        return "Be entrance window", "Be"
    if v.startswith("He3Cell_End"):
        return "Al cell end caps + ring", "Al"
    if v.startswith("He3Cell"):
        return "cell skin / rod / ⁶LiF scraper", "other"
    if v in ("", "World") or "Air" in v:
        return "air", "air (¹⁴N)"
    if v.endswith("_Al") or "ScintAl" in v:
        return "Al frames, flange, plates", "Al"
    if v.startswith(("PCB_Cu", "DriftCathode_Cu")) or v == "Micromesh":
        return "Cu (PCB, cathode, mesh)", "Cu"
    if v.startswith(("LiqScint", "LS_")):
        return "LS + vessel", "other"
    if "Scint" in v:
        return "plastic scint + tape", "other"
    return "PCB, Kapton, Mylar, gas", "other"


def singles(t, he3):
    ok = sf.arm_ok(t, MENU, "p")
    hr = sf.he3ng_rows(t)[:, None]
    ok &= hr if he3 else ~hr
    En = sf.arm_E(t, "p")
    if he3:
        src = np.full(len(t["w"]), "³He(n,γ) 20.6 MeV γ")
        mat = np.full(len(t["w"]), "³He")
    else:
        lut = {v: volume(v) for v in np.unique(t["capvol"])}
        src = np.array([lut[v][0] for v in t["capvol"]])
        mat = np.array([lut[v][1] for v in t["capvol"]])
    w = t["w"].astype(float) / t["absorbed"]
    return [dict(w=w[ok[:, a]], E=En[ok[:, a], a], pos=t["gpos"][ok[:, a], a],
                 src=src[ok[:, a]], mat=mat[ok[:, a]], row=np.nonzero(ok[:, a])[0]) for a in range(4)]


def pair_hists(S, key, labels):
    """{(i, j): angle histogram} over unordered label pairs; sums to the total."""
    out = {}
    for i, ci in enumerate(labels):
        for cj in labels[i:]:
            h = np.zeros(len(sf.CENTRES))
            for a in range(4):
                for b in range(a + 1, 4):
                    for x, y in {(ci, cj), (cj, ci)}:
                        ma, mb = S[a][key] == x, S[b][key] == y
                        if not ma.any() or not mb.any():
                            continue
                        SS = [(np.zeros(0),) * 3] * 4
                        SS[a] = (S[a]["w"][ma], S[a]["E"][ma], S[a]["pos"][ma])
                        SS[b] = (S[b]["w"][mb], S[b]["E"][mb], S[b]["pos"][mb])
                        h += sf.accidental_hist(SS, ECUT)
            if h.sum() > 0:
                out[(ci, cj)] = h
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cfg", default="G1")
    ap.add_argument("-o", "--out", type=Path, required=True)
    a = ap.parse_args()
    cfg = a.cfg
    tabs = {r: sf.load_table(E / "contracts", r, cfg) for r in ("C1", "C1w", "C1g")}
    c1 = sf.concat([tabs["C1"], tabs["C1w"]])
    c1["capvol"] = np.concatenate([tabs["C1"]["capvol"], tabs["C1w"]["capvol"]])
    biased = np.r_[np.zeros(len(tabs["C1"]["w"]), bool), np.ones(len(tabs["C1w"]["w"]), bool)]
    A, B = singles(c1, False), singles(tabs["C1g"], True)
    S = []
    for x, y in zip(A, B):
        d = {k: np.concatenate([x[k], y[k]]) for k in ("w", "E", "pos", "src", "mat")}
        d["c1row"] = np.r_[x["row"], np.full(len(y["w"]), -1)]
        S.append(d)
    win = (sf.CENTRES >= 60) & (sf.CENTRES <= 180)

    srcs = sorted(set(np.concatenate([s["src"] for s in S])))
    mats = sorted(set(np.concatenate([s["mat"] for s in S])))
    cat = lambda k: np.concatenate([s[k] for s in S])
    w_all, E_all, src_all, mat_all, row_all = cat("w"), cat("E"), cat("src"), cat("mat"), cat("c1row")

    # --- singles per source
    sing = {}
    for c in srcs:
        m = src_all == c
        h = m & (E_all > HARD)
        rows = row_all[h]
        ww = w_all[h]
        sing[c] = dict(material=str(mat_all[m][0]), rate_per_arm=float(w_all[m].sum() / 4),
                       hard_rate_per_arm=float(ww.sum() / 4), hard_raw=int(h.sum()),
                       hard_neff=float(ww.sum() ** 2 / (ww * ww).sum()) if h.any() else 0.0,
                       hard_from_biased=float(ww[rows >= 0][biased[rows[rows >= 0]]].sum() / ww.sum())
                       if h.any() else 0.0)
    # --- per-arm energy spectra by material (rate weighted, per arm per absorbed n per MeV)
    ebins = np.arange(0, 21.01, 0.5)
    spec = {m: (np.histogram(E_all[mat_all == m], ebins, weights=w_all[mat_all == m])[0] / 4 / 0.5).tolist()
            for m in mats}

    # --- accidental pairs
    tot_h = sf.accidental_hist([(s["w"], s["E"], s["pos"]) for s in S], ECUT)
    tot = float(tot_h[win].sum())
    pm = pair_hists(S, "mat", mats)
    ps = pair_hists(S, "src", srcs)
    pairs_mat = [dict(a=i, b=j, share=float(h[win].sum() / tot)) for (i, j), h in pm.items()]
    pairs_src = [dict(a=i, b=j, share=float(h[win].sum() / tot)) for (i, j), h in ps.items()]
    inv_mat = {m: float(sum(h[win].sum() for k, h in pm.items() if m in k) / tot) for m in mats}
    inv_src = {c: float(sum(h[win].sum() for k, h in ps.items() if c in k) / tot) for c in srcs}

    # --- reach if one material's singles were gone (timing + veto, and baseline)
    s1 = {c: sf.load_s1(E / "S1" / "summary", cfg, c) for c in ("X17", "M1", "E0")}
    tabs["K1"] = sf.load_table(E / "contracts", "K1", "G5")
    designs = {"timing": (0.6, 0.2, 0.6, 1e-2), "baseline": (2.5, 0.5, 1.5, 1.0)}
    removals = {"none": ()} | {m: (m,) for m in mats if m != "³He"} | {"Al + air": ("Al", "air (¹⁴N)")}
    sm_tot = sf.smooth(tot_h, 6.0)
    reach = {}
    for dname, (tau, sig, dtc, cs) in designs.items():
        cache = {}
        reach[dname] = {}
        for rname, gone in removals.items():
            keep = tot_h - sum((h for k, h in pm.items() if set(k) & set(gone)), np.zeros_like(tot_h))
            f = np.where(sm_tot > 0, sf.smooth(np.clip(keep, 0, None), 6.0) / np.maximum(sm_tot, 1e-300), 0)
            best = None
            for R in np.logspace(8, np.log10(R_MAX), 22):
                mod = sf.model(cfg, s1, tabs, MENU, ECUT, R, 50.0, tau, sig, dtc, cache=cache)
                mod["COS"] = mod["COS"] * cs
                mod["ACC"] = mod["ACC"] * f
                s = sf.reach(mod)
                if best is None or s < best[1]:
                    best = (R, s, float(mod["ACC"][win].sum()), float(mod["COS"][win].sum()),
                            float((mod["M1"] + mod["E0"])[win].sum()))
            reach[dname][rname] = dict(R=best[0], reach3=3 * best[1], acc=best[2], cos=best[3], ipc=best[4])
            print(f"{cfg} {dname:8s} remove {rname:12s} R {best[0]:.2g}  3σ {3 * best[1]:.2e}  ACC {best[2]:.3g}",
                  flush=True)

    out = dict(cfg=cfg, menu=MENU, ecut=ECUT, hard_MeV=HARD, window_deg=[60, 180],
               note="attribution by the capture volume of the event's neutron; C1 + C1w (+ C1g for ³He(n,γ))",
               acc_total_per_abs2=tot, singles=sing, ebins=ebins.tolist(), spectra=spec,
               pairs_material=pairs_mat, pairs_source=pairs_src,
               involvement_material=inv_mat, involvement_source=inv_src,
               acc_angle_total=tot_h.tolist(),
               acc_angle_material={f"{i}|{j}": h.tolist() for (i, j), h in pm.items()},
               reach=reach)
    a.out.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
