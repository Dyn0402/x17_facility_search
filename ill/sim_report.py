#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sim_report.py -- figures and tables for the ILL feasibility question, from the
Geant4 campaign (runs on lxplus next to the data; only the outputs travel).

    python3 sim_report.py --s1 /eos/.../ill/S1/summary --contracts /eos/.../ill/contracts \\
        -o out_sim

Writes PNG + CSV per figure (figstyle.save) and results.json:
  scatter_vs_ke      pre-gap multiple scattering of the leptons vs kinetic energy
  resolution_vs_ke   sigma68(theta_reco - theta_true) vs the softer lepton's KE
  esum               energy deposited in the two lepton arms: signal vs backgrounds
  spectrum_<cfg>     expected reconstructed opening angle, one cycle, best rate
  reach_vs_rate      3-sigma X17/IPC(M1) reach against absorbed rate, per config
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import figstyle as FS  # noqa: E402
import sim_feasibility as SF  # noqa: E402

CFG_COLOR = {"G1": "#0072B2", "G2": "#56B4E9", "G3": "#009E73", "G4": "#8fd17f",
             "G5": "#D55E00", "G6": "#E69F00"}
CFG_LABEL = {"G1": "G1 1 bar R40 mylar", "G2": "G2 1 bar R100 mylar",
             "G3": "G3 2 bar R40 Kapton 0.11", "G4": "G4 2 bar R100 Kapton 0.29",
             "G5": "G5 3 bar R40 Kapton 0.23", "G6": "G6 3 bar R100 Kapton 0.57"}
R_BEAM = 1.9e10                      # Ø2 cm spot at 46 MW, HANDOFF_SIM.md
KE_EDGES = np.array([1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 19.6])


def ang(a, b):
    a = a / np.linalg.norm(a, axis=1)[:, None]
    b = b / np.linalg.norm(b, axis=1)[:, None]
    return np.degrees(np.arccos(np.clip((a * b).sum(1), -1, 1)))


def scatter_table(s1all):
    rows = []
    for cfg, s1 in s1all.items():
        ke, sc = [], []
        for ch in ("X17", "M1", "E0"):
            z = s1[ch]
            for lp in ("em", "ep"):
                ke.append(z[f"{lp}_ke"])
                sc.append(ang(z[f"{lp}_d"].astype(float), z[f"{lp}_d0"].astype(float)))
        ke, sc = np.concatenate(ke), np.concatenate(sc)
        for lo, hi in zip(KE_EDGES[:-1], KE_EDGES[1:]):
            m = (ke >= lo) & (ke < hi) & np.isfinite(sc)
            if m.sum() < 50:
                continue
            q = np.percentile(sc[m], [16, 50, 84])
            rows.append(dict(config=cfg, ke_lo=lo, ke_hi=hi, n=int(m.sum()),
                             scat_p16=q[0], scat_median=q[1], scat_p84=q[2]))
    return pd.DataFrame(rows)


def resolution_table(s1all, menu="sipm2", ecut=0.0):
    rows = []
    for cfg, s1 in s1all.items():
        z = s1["X17"]
        m = SF.s1_select(z, menu, ecut)
        soft = np.minimum(z["em_ke"], z["ep_ke"])
        for est in ("vline", "nomline", "xing", "xing_s"):
            d = (z[f"reco_{est}"] - z["theta"])
            for lo, hi in zip(KE_EDGES[:-1], KE_EDGES[1:]):
                k = m & (soft >= lo) & (soft < hi) & np.isfinite(d)
                if k.sum() < 50:
                    continue
                q = np.percentile(d[k], [16, 50, 84])
                rows.append(dict(config=cfg, estimator=est, ke_lo=lo, ke_hi=hi, n=int(k.sum()),
                                 sigma68=0.5 * (q[2] - q[0]), bias=q[1]))
            k = m & np.isfinite(d)
            q = np.percentile(d[k], [16, 50, 84])
            rows.append(dict(config=cfg, estimator=est, ke_lo=0, ke_hi=99, n=int(k.sum()),
                             sigma68=0.5 * (q[2] - q[0]), bias=q[1]))
    return pd.DataFrame(rows)


def highland_deg(p_mev, x_over_x0):
    return np.degrees(13.6 / p_mev * np.sqrt(x_over_x0) * (1 + 0.038 * np.log(x_over_x0)))


def fig_scatter(T, od):
    FS.use()
    fig, ax = FS.figure(FS.FIG)
    for cfg in T.config.unique():
        t = T[T.config == cfg]
        x = 0.5 * (t.ke_lo + t.ke_hi)
        ax.plot(x, t.scat_median, "-o", ms=3.5, color=CFG_COLOR[cfg], label=CFG_LABEL[cfg])
    # Highland (space-angle median ~ 1.18 theta0) for the chamber entrance + 16 cm air
    ke = np.linspace(1.5, 19, 100)
    p = np.sqrt((ke + 0.511) ** 2 - 0.511 ** 2)
    x0 = 0.04 / 287 + 0.05 / 286 + 0.009 / 14.36 + 164 / 303900
    ax.plot(ke, 1.18 * highland_deg(p, x0), ":", color=FS.MUTED,
            label="Highland: MM entrance + 16 cm air")
    ax.set_xlabel("lepton kinetic energy [MeV]")
    ax.set_ylabel("median scattering before the drift gap [deg]")
    ax.set_ylim(0, None)
    ax.legend(frameon=False, fontsize=8)
    FS.title(ax, "The chamber entrance and the air, not the cell, scatter the leptons",
             "angle between the lepton's initial direction and its direction at the first drift-gap hit")
    FS.save(fig, od / "scatter_vs_ke", data=T)
    plt.close(fig)


def fig_resolution(R, od):
    FS.use()
    fig, axs = plt.subplots(1, 3, figsize=FS.WIDE, sharey=True)
    for ax, est, lab in zip(axs, ("vline", "nomline", "xing_s"),
                            ("true vertex (scattering only)", "vertex assumed at centre",
                             "per-event vertex, data-like directions")):
        FS.strip(ax)
        for cfg in R.config.unique():
            t = R[(R.config == cfg) & (R.estimator == est) & (R.ke_hi < 90)]
            ax.plot(0.5 * (t.ke_lo + t.ke_hi), t.sigma68, "-o", ms=3, color=CFG_COLOR[cfg],
                    label=cfg)
        ax.set_title(lab, fontsize=9.5, loc="left")
        ax.set_xlabel("softer lepton KE [MeV]")
    axs[0].set_ylabel("σ68 of θ_reco − θ_true [deg]")
    axs[0].legend(frameon=False, fontsize=8)
    FS.fig_title(fig, "X17 opening-angle resolution: scattering ~2–6°, vertex knowledge on top",
                 "sipm2 menu; vertex-to-hit chord with 0.5 mm hit smearing")
    FS.save(fig, od / "resolution_vs_ke", data=R)
    plt.close(fig)


def fig_esum(s1all, tabs, od, cfg="G5", menu="sipm2"):
    FS.use()
    fig, ax = FS.figure(FS.FIG)
    bins = np.arange(0, 30.5, 1.0)
    rows = {}
    z = s1all[cfg]["X17"]
    m = SF.s1_select(z, menu, 0.0)
    es = (z["E_sipm_em"] + z["E_plast_em"] + z["E_ls_em"] + z["E_sipm_ep"] + z["E_plast_ep"]
          + z["E_ls_ep"])[m]
    h, _ = np.histogram(es, bins)
    rows["X17"] = h / h.sum()
    c1 = SF.concat([tabs[cfg].get("C1"), tabs[cfg].get("C1w")])
    g = tabs[cfg].get("C1g") or tabs[cfg].get("C1")
    for name, t, which in (("³He(n,γ) fakes", g, "he3ng"), ("other single-neutron fakes", c1, "wall")):
        mm, th, esum, _, _ = SF.two_arm_events(t, menu, 0.0)
        sel = SF.he3ng_rows(t) if which == "he3ng" else ~SF.he3ng_rows(t)
        mm &= sel
        h, _ = np.histogram(esum[mm], bins, weights=t["w"][mm].astype(float))
        rows[name] = h / max(h.sum(), 1e-300)
    S = SF.merge_singles(SF.singles(c1, menu), SF.singles_he3ng(g, menu))
    # accidental Esum: every pair of singles from different arms (exact)
    acc = np.zeros(len(bins) - 1)
    for a in range(4):
        for b in range(a + 1, 4):
            wa, ea, _ = S[a]
            wb, eb, _ = S[b]
            step = max(1, 4_000_000 // max(len(wb), 1))
            for i0 in range(0, len(wa), step):
                es2 = ea[i0:i0 + step, None] + eb[None, :]
                ww = wa[i0:i0 + step, None] * wb[None, :]
                acc += np.histogram(es2.ravel(), bins, weights=ww.ravel())[0]
    rows["accidentals"] = acc / acc.sum()
    k1 = tabs[cfg].get("K1")
    if k1 is not None:
        mm, _, esum, _, _ = SF.two_arm_events(k1, menu, 0.0)
        h, _ = np.histogram(esum[mm], bins)
        rows["cosmics"] = h / max(h.sum(), 1)
    c = 0.5 * (bins[1:] + bins[:-1])
    sty = {"X17": dict(color=FS.ACCENT, lw=2.2), "³He(n,γ) fakes": dict(color="#0072B2"),
           "other single-neutron fakes": dict(color=FS.COPPER),
           "accidentals": dict(color=FS.MUTED), "cosmics": dict(color="#009E73")}
    for k, v in rows.items():
        ax.step(c, v, where="mid", label=k, **sty.get(k, {}))
    ax.axvline(10.83, color=FS.BAND_DEAD, ls="--", lw=1)
    ax.text(10.9, ax.get_ylim()[1] * 0.92, "¹⁴N(n,γ) endpoint", fontsize=8, color=FS.BAND_DEAD)
    ax.set_yscale("log")
    ax.set_xlabel("energy deposited in the two lepton arms' scintillators [MeV]")
    ax.set_ylabel("fraction per MeV")
    ax.legend(frameon=False, fontsize=8)
    FS.title(ax, "The energy sum is the only handle on capture-γ backgrounds",
             f"{cfg}, {menu} menu, two-arm events; true deposits, unit-normalised")
    FS.save(fig, od / "esum", data=pd.DataFrame(rows, index=c))
    plt.close(fig)


def fig_spectrum(mod, cfg, R, ecut, menu, sigma, od, scen=""):
    FS.use()
    fig, (ax, ax2) = FS.figure(FS.FULL, nrows=2, sharex=True,
                               gridspec_kw=dict(height_ratios=[1.6, 1], hspace=0.08))
    c = SF.CENTRES
    w = SF.BINS[1] - SF.BINS[0]
    comps = [("M1", "³He IPC M1", "#cbb6d6"), ("E0", "³He IPC E0", "#a78bb8"),
             ("G", "³He(n,γ) photon fakes", "#8fb8d8"), ("ACC", "accidentals", "#c9ced6"),
             ("COS", "cosmics (after timing)", "#a6d8b8"), ("WALL", "other single-n fakes", "#e8c9a0")]
    bottom = np.zeros(len(c))
    data = {}
    for k, lab, col in comps:
        ax.bar(c, mod[k], width=w, bottom=bottom, color=col, label=lab, align="center")
        bottom += mod[k]
        data[k] = mod[k]
    x_ref = SF.X17_REF * mod["X17"]
    ax.step(c, bottom + x_ref, where="mid", color=FS.ACCENT, lw=1.6,
            label=f"+ X17 at X17/IPC(M1) = {SF.X17_REF:g}")
    data["X17_ref"] = x_ref
    ax.set_xlim(60, 180)
    ax.set_ylabel(f"events / {w:g}° / 50 d")
    ax.legend(frameon=False, fontsize=7.5, loc="upper right", ncol=2)
    # background-subtracted view: the X17 peak against the statistical noise
    # of everything else (sqrt of the total per bin)
    err = np.sqrt(bottom + x_ref)
    ax2.axhline(0, color=FS.LINE, lw=0.8)
    ax2.fill_between(c, -err, err, step="mid", color="#e6e9ee", label="±1σ statistical, per bin")
    ax2.step(c, x_ref, where="mid", color=FS.ACCENT, lw=1.6, label=f"X17 at {SF.X17_REF:g}")
    ax2.step(c, 3 * sigma * mod["X17"], where="mid", color=FS.ACCENT, lw=1.0, ls="--",
             label=f"X17 at the 3σ reach ({3 * sigma:.1e})")
    data["stat_err"] = err
    ax2.set_xlabel("reconstructed opening angle (vertex-to-hit chord) [deg]")
    ax2.set_ylabel("minus background")
    ax2.legend(frameon=False, fontsize=7.5, loc="upper right")
    FS.title(ax, f"{cfg}: one 50-day ILL cycle at {R:.2g} absorbed n/s",
             f"{menu} menu, Esum > {ecut:g} MeV{scen}")
    FS.save(fig, od / f"spectrum_{cfg}", data=pd.DataFrame(data, index=c))
    plt.close(fig)


def fig_reach(scan, od, key, scen=""):
    FS.use()
    fig, ax = FS.figure(FS.FIG)
    rows = []
    for cfg, res in scan.items():
        s = res[key]["scan"]
        R = [r["R"] for r in s]
        y = [3 * r["sigma"] for r in s]
        ax.plot(R, y, "-o", ms=3, color=CFG_COLOR[cfg], label=CFG_LABEL[cfg])
        rows += [dict(config=cfg, **r) for r in s]
    ax.axhline(SF.X17_REF, color=FS.ACCENT, ls="--", lw=1)
    ax.text(1.1e8, SF.X17_REF * 1.08, "reference X17/IPC(M1)", fontsize=8, color=FS.ACCENT)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("absorbed neutrons per second")
    ax.set_ylabel("3σ reach in X17 / IPC(M1), 50 days")
    ax.legend(frameon=False, fontsize=8)
    ax.axvline(R_BEAM, color=FS.MUTED, ls=":", lw=1)
    ax.text(R_BEAM * 0.92, ax.get_ylim()[1] * 0.8, "Ø2 cm beam, 46 MW", fontsize=7.5,
            color=FS.MUTED, ha="right")
    FS.title(ax, "3σ reach against the absorbed-neutron rate",
             key.replace("/", ", ") + " MeV" + scen + "; M1, E0 and ³He(n,γ) floating")
    FS.save(fig, od / f"reach_vs_rate_{key.replace('/', '_').replace('>', 'gt')}", data=pd.DataFrame(rows))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s1", type=Path, required=True)
    ap.add_argument("--contracts", type=Path, required=True)
    ap.add_argument("-o", "--out", type=Path, required=True)
    ap.add_argument("--days", type=float, default=50.0)
    ap.add_argument("--tau-ns", type=float, default=2.5)
    ap.add_argument("--sigma-t-ns", type=float, default=0.5)
    ap.add_argument("--dt-cut-ns", type=float, default=1.5)
    ap.add_argument("--cos-scale", type=float, default=1.0,
                    help="residual cosmic fraction after an external muon veto")
    ap.add_argument("--r-max", type=float, default=1e11)
    ap.add_argument("--skip-common", action="store_true", help="only the rate scans")
    a = ap.parse_args()
    scen = (f"; σt {a.sigma_t_ns:g} ns, |Δt| < {a.dt_cut_ns:g} ns, 2τ {2 * a.tau_ns:g} ns"
            + (f", μ veto {a.cos_scale:g}" if a.cos_scale != 1 else ""))
    od = a.out
    od.mkdir(parents=True, exist_ok=True)
    s1all, tabs = {}, {}
    k1 = SF.load_table(a.contracts, "K1", "G5")
    for cfg in SF.CONFIGS:
        s1 = {c: SF.load_s1(a.s1, cfg, c) for c in ("X17", "M1", "E0")}
        if any(v is None for v in s1.values()):
            continue
        t = {r: SF.load_table(a.contracts, r, cfg) for r in ("C1", "C1w", "C1g")}
        if t["C1"] is None and t["C1w"] is None:
            continue
        t["K1"] = k1
        s1all[cfg], tabs[cfg] = s1, t
        print(cfg, "tables:", [k for k, v in t.items() if v is not None], flush=True)
    if not a.skip_common:
        T = scatter_table(s1all)
        fig_scatter(T, od)
        Rt = resolution_table(s1all)
        fig_resolution(Rt, od)
        print(Rt[Rt.ke_hi > 90].to_string(index=False), flush=True)
        T.to_csv(od / "scatter_vs_ke.csv", index=False)
        Rt.to_csv(od / "resolution_vs_ke.csv", index=False)
        if "G5" in s1all:
            fig_esum(s1all, tabs, od)
    rng = np.random.default_rng(7)
    rates = np.logspace(8, np.log10(a.r_max), 16)

    def run(cfg, menu, ecut, R, cache):
        mod = SF.model(cfg, s1all[cfg], tabs[cfg], menu, ecut, R, a.days, a.tau_ns,
                       a.sigma_t_ns, a.dt_cut_ns, rng=rng, cache=cache)
        mod["COS"] = mod["COS"] * a.cos_scale
        return mod
    results = dict(args={k: str(v) for k, v in vars(a).items()}, configs={})
    for cfg in s1all:
        cache = {}
        res = {}
        for menu in ("strict", "sipm2"):
            for ecut in (0.0, 8.0, 11.0, 12.0, 13.0, 14.0):
                row = []
                for R in rates:
                    mod = run(cfg, menu, ecut, R, cache)
                    s = SF.reach(mod)
                    row.append(dict(R=float(R), sigma=s, occ=mod["occ"],
                                    raw_g=mod["raw_g"], raw_wall=mod["raw_wall"], raw_cos=mod["raw_cos"],
                                    **{k: float(np.sum(mod[k])) for k in
                                       ("X17", "M1", "E0", "G", "WALL", "ACC", "COS")}))
                best = min(row, key=lambda r: r["sigma"])
                res[f"{menu}/E>{ecut:g}"] = dict(scan=row, best=best)
                b = best
                print(f"{cfg} {menu:6s} E>{ecut:4.1f}: best R {b['R']:.2g}  3σ {3 * b['sigma']:.2e}  "
                      f"5σ {5 * b['sigma']:.2e}  IPC {b['M1'] + b['E0']:.3g}  G {b['G']:.3g} (raw {b['raw_g']})  "
                      f"ACC {b['ACC']:.3g}  COS {b['COS']:.3g} (raw {b['raw_cos']})  WALL {b['WALL']:.3g} "
                      f"(raw {b['raw_wall']})  X17@ref {SF.X17_REF * b['X17']:.3g}  occ {b['occ']:.2f}",
                      flush=True)
        results["configs"][cfg] = res
        key = "sipm2/E>12"
        b = res[key]["best"]
        mod = run(cfg, "sipm2", 12.0, b["R"], cache)
        fig_spectrum(mod, cfg, b["R"], 12.0, "sipm2", b["sigma"], od, scen)
    for key in ("sipm2/E>12", "strict/E>12", "sipm2/E>13"):
        fig_reach(results["configs"], od, key, scen)
    (od / "results.json").write_text(json.dumps(results, indent=1, default=float))
    print("wrote", od)


if __name__ == "__main__":
    main()
