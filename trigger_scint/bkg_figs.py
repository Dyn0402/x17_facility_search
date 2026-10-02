#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bkg_figs.py -- figures and tables for the big-slab background study.

    python trigger_scint/bkg_figs.py              # reads sim/bkg/<geom>.json

Inputs are the small JSONs written by bkg_reach.py on lxplus
(/eos/experiment/ntof/data/x17/ill/TB/analysis/), copied to sim/bkg/.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "ill"))
import figstyle as fs          # noqa: E402

IN = HERE / "sim" / "bkg"
FIG = HERE / "out" / "figures"
GEOMS = ["asbuilt", "P2", "P5", "P5L", "P5B"]
LABEL = {"asbuilt": "n_TOF as built", "P2": "70x70x2 cm", "P5": "75x75x5 cm",
         "P5L": "75x75x5 + 2 mm 6LiF", "P5B": "75x75x5 + 2 mm B4C"}
COL = {"asbuilt": fs.INK, "P2": "#0072B2", "P5": "#D55E00", "P5L": "#009E73", "P5B": "#CC79A7"}
MARK = {"asbuilt": "o", "P2": "s", "P5": "^", "P5L": "D", "P5B": "v"}
R_REF = 1e10
SCEN_LAB = {"base": "σt 0.5 ns, no μ veto", "timing": "σt 0.2 ns + μ veto 10⁻²"}


def load(air=1.0):
    D = {}
    for g in GEOMS:
        f = IN / (f"{g}.json" if air == 1 else f"{g}_air{air:g}.json")
        if f.exists():
            D[g] = json.load(open(f))
    return D


def rows_df(D):
    out = []
    for g, d in D.items():
        for r in d["rows"]:
            b = r["best"]
            out.append(dict(geom=g, air=d.get("air", 1.0), scen=r["scen"], gate_ns=r["gate_ns"], menu=r["menu"], ecut=r["ecut"],
                            R_best=b["R"], reach3=3 * b["sigma"], X17_ref=0.025 * b["X17"],
                            IPC=b["M1"] + b["E0"], He3ng=b["G"], ACC=b["ACC"], COS=b["COS"], WALL=b["WALL"],
                            mm_occ=b["occ"], mu_pu=b["mu_pu"],
                            trig_sipm2_hz=sum(b2 for b2 in (r["trig"]["sipm2"]["corr"], r["trig"]["sipm2"]["acc"])),
                            trig_strict_hz=r["trig"]["strict"]["corr"] + r["trig"]["strict"]["acc"]))
    return pd.DataFrame(out)


def fig_spectrum(D):
    fig, ax = fs.figure(fs.FIG)
    rows = []
    for g, d in D.items():
        s = np.array(d["spectrum"]) * R_REF / d["dx"]          # Hz per MeV per arm
        x = np.arange(len(s)) * d["dx"]
        # 0.25 MeV display bins
        k = 5
        n = len(s) // k * k
        xs = x[:n].reshape(-1, k).mean(1) + 0.5 * d["dx"]
        ys = s[:n].reshape(-1, k).mean(1)
        m = xs < 16
        ax.step(xs[m], np.where(ys[m] > 0, ys[m], np.nan), where="mid", color=COL[g], lw=1.3, label=LABEL[g])
        rows += [dict(geom=g, E_MeV=a, Hz_per_MeV_per_arm=b) for a, b in zip(xs[m], ys[m])]
    ax.set_yscale("log")
    ax.set_xlabel("energy deposited in one arm's slab (plastic + LS) [MeV]")
    ax.set_ylabel("rate per arm at 10¹⁰ abs n/s [Hz / MeV]")
    ax.axvline(1.67, color=fs.MUTED, ls=":", lw=1)
    ax.text(1.75, ax.get_ylim()[1] * 0.3, "trigger leg\n1.67 MeV", color=fs.MUTED, fontsize=8, va="top")
    ax.legend(frameon=False, fontsize=8.5)
    fs.title(ax, "Slab singles at a reactor beam", "all times (steady state), arm average, G1 cell")
    fs.save(fig, FIG / "bkg_singles_spectrum", data=pd.DataFrame(rows))


def fig_reach_vs_gate(df):
    fig, axs = plt.subplots(1, 2, figsize=fs.WIDE, constrained_layout=True, sharey=False)
    for ax, sc in zip(axs, ("base", "timing")):
        for g in GEOMS:
            for air, ls in ((1.0, "-"), (0.1, "--")):
                d = df[(df.geom == g) & (df.scen == sc) & (df.air == air)]
                if not len(d):
                    continue
                best = d.groupby("gate_ns").reach3.min()
                ax.plot(best.index, best.values, marker=MARK[g], color=COL[g], lw=1.3 if air == 1 else 1.0,
                        ls=ls, ms=5 if air == 1 else 3.5, mec="white", mew=0.7,
                        label=LABEL[g] if air == 1 else None)
        ax.set_yscale("log")
        ax.set_xlabel("pile-up window per slab [ns]")
        ax.set_ylabel("3σ reach, X17/IPC(M1), 50 d")
        fs.title(ax, SCEN_LAB[sc], "best rate and trigger menu, Esum > 13 MeV")
    axs[0].plot([], [], color=fs.MUTED, ls="--", label="He flight tube (air × 0.1)")
    axs[0].legend(frameon=False, fontsize=8)
    fs.save(fig, FIG / "bkg_reach_vs_gate", data=df)


def fig_budget(df, gate, sc="timing", air=1.0):
    d = df[(df.scen == sc) & (df.gate_ns == gate) & (df.air == air)]
    d = d.loc[d.groupby("geom").reach3.idxmin()].set_index("geom").reindex([g for g in GEOMS if g in set(d.geom)])
    comp = [("IPC", "IPC (M1 + E0)", "#56B4E9"), ("He3ng", "³He(n,γ) fakes", "#E69F00"),
            ("ACC", "accidentals", "#D55E00"), ("WALL", "one-neutron + pile-up", "#8a3f8f"),
            ("COS", "cosmics", fs.MUTED)]
    fig, ax = fs.figure(fs.FIG)
    y = np.arange(len(d))
    left = np.zeros(len(d))
    for k, lab, c in comp:
        v = d[k].values
        ax.barh(y, v, left=left, color=c, label=lab, height=0.6)
        left += v
    ax.scatter(d.X17_ref.values, y, marker="|", s=250, color=fs.INK, zorder=5, label="X17 at the reference ratio")
    ax.set_yticks(y, [f"{LABEL[g]}\n{d.loc[g, 'menu']}, R {d.loc[g, 'R_best']:.1g}" for g in d.index], fontsize=8)
    ax.set_xlabel("events per 50-day cycle passing all cuts")
    ax.set_ylim(-0.6, len(d) - 0.4)
    ax.invert_yaxis()
    ax.legend(frameon=False, fontsize=7.5, loc="upper left", bbox_to_anchor=(1.01, 1.0))
    fs.title(ax, f"What is under the signal ({SCEN_LAB[sc]}, {gate:g} ns)",
             "at each geometry's best rate" + ("" if air == 1 else ", He flight tube"))
    fs.save(fig, FIG / (f"bkg_budget_{sc}_{int(gate)}ns" + ("" if air == 1 else f"_air{air:g}")),
            data=d.reset_index())


def tables(D, df):
    rows = []
    for g, d in D.items():
        t = d["trig"]
        b = d.get("budget", {})
        rows.append(dict(
            geom=g,
            slab_capt_per_abs=sum(v for k, v in b.items() if k.startswith(("budget.BackScint",)) and "nCapture" in k),
            shield_abs_per_abs=sum(v for k, v in b.items() if k.startswith("budget.BackScintShield")),
            gap_per_arm_per_abs=d["gap_arm"],
            slab_any_hz=t["slab_any"] * R_REF, slab_167_hz=t["slab>1.67"] * R_REF,
            slab_3_hz=t["slab>3"] * R_REF, slab_8_hz=t["slab>8"] * R_REF,
            trig_sipm2_corr_hz=t["sipm2.corr"] * R_REF,
            trig_strict_corr_hz=t["strict.corr"] * R_REF,
            trig_strict_acc_hz=sum(a * b for i, a in enumerate(np.array(t["strict.single_arm"]) * R_REF)
                                   for j, b in enumerate(np.array(t["strict.single_arm"]) * R_REF) if j > i) * 20e-9,
            cos_strict_hz=t.get("cos.strict_per_s"),
        ))
    T = pd.DataFrame(rows)
    T.to_csv(HERE / "out" / "bkg_rates.csv", index=False)
    df.to_csv(HERE / "out" / "bkg_reach.csv", index=False)
    with pd.option_context("display.width", 200, "display.max_columns", 30):
        print(T.to_string(index=False, float_format=lambda v: f"{v:.3g}"))
        piv = df.loc[df.groupby(["geom", "air", "scen", "gate_ns"]).reach3.idxmin()]
        print(piv[["geom", "air", "scen", "gate_ns", "menu", "R_best", "reach3", "X17_ref", "IPC", "He3ng", "ACC",
                   "WALL", "COS", "mm_occ", "mu_pu"]].to_string(index=False, float_format=lambda v: f"{v:.3g}"))


def main():
    fs.use()
    FIG.mkdir(parents=True, exist_ok=True)
    D = load()
    Da = load(0.1)
    df = pd.concat([rows_df(D), rows_df(Da)], ignore_index=True)
    tables(D, df)
    fig_spectrum(D)
    fig_reach_vs_gate(df)
    for gate in (10, 50):
        for air in (1.0, 0.1):
            if len(df[(df.gate_ns == gate) & (df.air == air)]):
                fig_budget(df, gate, air=air)


if __name__ == "__main__":
    main()
