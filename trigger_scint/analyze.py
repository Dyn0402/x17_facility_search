#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze.py -- acceptance vs cost for the trigger-scintillator options.

    python trigger_scint/analyze.py [--acc trigger_scint/sim/accept]

Inputs
  sim/accept/summary.json, scan_{X17,M1}.csv   trig_accept.py on lxplus (T0/T1)
  out/optics.csv                               optics_toy.py
  costs.py                                     budgetary prices
Outputs (out/)
  options.csv                one row per option: acceptance, Esum efficiency, cost
  figures/acc_vs_width       X17 acceptance vs plastic width, per length (T = 2 cm)
  figures/acc_vs_length      ... vs length along the beam, per width
  figures/calorimetry        X17 acc x P(Esum > 13 MeV) vs plastic thickness
  figures/acc_vs_cost        the headline: acceptance against cost, every option
  figures/optics             photoelectrons/MeV and timing vs slab size and readout
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "ill"))
sys.path.insert(0, str(HERE))
import figstyle as fs          # noqa: E402
import costs as C              # noqa: E402

OUT = HERE / "out"
FIG = OUT / "figures"
SEQ = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#1b2430"]   # Okabe-Ito + ink, fixed order
MARK = ["o", "s", "^", "D", "v", "P", "X"]


def load(acc_dir: Path):
    S = json.load(open(acc_dir / "summary.json"))
    scans = {ch: pd.read_csv(acc_dir / f"scan_{ch}.csv") for ch in ("X17", "M1")}
    return S, scans


def pick(scan, W, L, T, sipm="SiPM20"):
    r = scan[(scan.W_cm == W) & (scan.L_cm == L) & (scan.T_cm == T) & (scan.sipm == sipm)]
    return r.iloc[0]


def refs(S, ch="X17"):
    t0 = S[ch]["T0"]
    return {
        "MM only": t0["MM only (ceiling)"]["acc"],
        "MM + SiPM20 (ceiling)": t0["MM + SiPM20"]["acc"],
        "n_TOF as built": t0["n_TOF as built: MM + SiPM16 + 2cm plastics"]["acc"],
        "LS working (+ plastics)": t0["LS working: MM + SiPM20 + (plastic OR LS)"]["acc"],
    }


def ref_lines(ax, R, xmax):
    sty = {"MM only": (fs.MUTED, ":"), "MM + SiPM20 (ceiling)": (fs.INK, "--"),
           "n_TOF as built": (fs.COPPER, "-."), "LS working (+ plastics)": (fs.ACCENT, (0, (5, 2, 1, 2)))}
    for k, v in R.items():
        c, ls = sty[k]
        ax.axhline(100 * v, color=c, ls=ls, lw=1.1, zorder=1)
        ax.text(xmax, 100 * v, f" {k} {100*v:.1f}%", color=fs.MUTED, va="center", ha="left", fontsize=8.5)


def fig_width(S, scan):
    T = 2.0
    Ls = [30, 50, 60, 80, 120]
    fig, ax = fs.figure(figsize=(7.6, 4.4))
    rows = []
    for i, L in enumerate(Ls):
        d = scan[(scan.L_cm == L) & (scan.T_cm == T) & (scan.sipm == "SiPM20")].sort_values("W_cm")
        ax.plot(d.W_cm, 100 * d.acc, color=SEQ[i], marker=MARK[i], ms=5, lw=1.6, label=f"L = {L} cm")
        rows += [dict(L_cm=L, W_cm=w, acc=a) for w, a in zip(d.W_cm, d.acc)]
    ref_lines(ax, refs(S), 79)
    ax.set_xlim(28, 79)
    ax.set_xlabel("plastic width W (transverse, cm)")
    ax.set_ylabel("X17 acceptance (% of pairs)")
    ax.set_ylim(0, None)
    ax.legend(loc="upper left", frameon=False, title="length along beam", fontsize=8.5)
    fs.title(ax, "Wider plastics: acceptance climbs to the SiPM-wall ceiling",
             "MM + all 20 SiPM bars + plastic > 1.67 MeV in both lepton arms, T = 2 cm, G1 cell")
    fig.subplots_adjust(right=0.74)
    fs.save(fig, FIG / "acc_vs_width", data=pd.DataFrame(rows))


def fig_length(S, scan):
    T = 2.0
    Ws = [40, 60, 78]
    fig, ax = fs.figure(figsize=(7.6, 4.4))
    rows = []
    for i, W in enumerate(Ws):
        d = scan[(scan.W_cm == W) & (scan.T_cm == T) & (scan.sipm == "SiPM20")].sort_values("L_cm")
        ax.plot(d.L_cm, 100 * d.acc, color=SEQ[i], marker=MARK[i], ms=5, lw=1.6, label=f"W = {W} cm")
        rows += [dict(W_cm=W, L_cm=l, acc=a) for l, a in zip(d.L_cm, d.acc)]
    ref_lines(ax, refs(S), 121)
    ax.set_xlim(28, 121)
    ax.set_xlabel("plastic length L (along the beam, cm)")
    ax.set_ylabel("X17 acceptance (% of pairs)")
    ax.set_ylim(0, None)
    ax.legend(loc="upper left", frameon=False, fontsize=8.5)
    fs.title(ax, "Along the beam the gain stops near 60-80 cm",
             "the 50 cm SiPM bars and the 36 cm MM set the edge; T = 2 cm")
    fig.subplots_adjust(right=0.74)
    fs.save(fig, FIG / "acc_vs_length", data=pd.DataFrame(rows))


def fig_calo(S, scan, W=78, L=80):
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 4.0), constrained_layout=True)
    d = scan[(scan.W_cm == W) & (scan.L_cm == L) & (scan.sipm == "SiPM20")].sort_values("T_cm")
    ax = axs[0]
    for col, lab, c, m in (("acc", "trigger only", SEQ[0], "o"), ("acc_E12", "+ Esum > 12 MeV", SEQ[1], "s"),
                           ("acc_E13", "+ Esum > 13 MeV", SEQ[2], "^")):
        ax.plot(d.T_cm, 100 * d[col], color=c, marker=m, ms=5, lw=1.6, label=lab)
    t0 = S["X17"]["T0"]["n_TOF as built: MM + SiPM16 + 2cm plastics"]
    ax.axhline(100 * t0["acc_E13"], color=fs.COPPER, ls="-.", lw=1.1)
    ax.text(10.2, 100 * t0["acc_E13"], " n_TOF as built,\n Esum > 13", fontsize=8, color=fs.MUTED, va="center")
    ax.set_xlabel("plastic thickness T (cm)")
    ax.set_ylabel("X17 acceptance (% of pairs)")
    ax.set_ylim(0, None)
    ax.set_xlim(0.5, 12.5)
    ax.legend(frameon=False, fontsize=8.5, loc="center right")
    fs.title(ax, f"{W} x {L} cm plastic: energy cut vs thickness", "MM + SiPM20 + plastic, X17")
    ax = axs[1]
    depth = S["X17"]["depth"]
    Ts = S["X17"]["T_cm"]
    rows = []
    for i, (k, v) in enumerate(depth.items()):
        v = np.array(v)
        frac = v / max(v[-1], 1e-9)
        ax.plot(Ts, frac, color=(SEQ + SEQ)[i], marker=(MARK + MARK)[i], ms=4, lw=1.4, label=f"{k} MeV")
        rows += [dict(ke_bin=k, T_cm=t, mean_edep_MeV=e) for t, e in zip(Ts, v)]
    ax.set_xlabel("plastic thickness T (cm)")
    ax.set_ylabel("deposit within T / deposit in 10 cm")
    ax.set_ylim(0, 1.02)
    ax.legend(frameon=False, fontsize=8, title="lepton KE", loc="lower right")
    fs.title(ax, "Containment depth by lepton energy", "leptons reaching the slab, X17")
    fs.save(fig, FIG / "calorimetry", data={"acc": d, "depth": pd.DataFrame(rows)})


def options(S, scans):
    """The option table: acceptance (X17, M1), Esum efficiency, incremental cost."""
    X, M = S["X17"]["T0"], S["M1"]["T0"]
    rows = []

    def add(name, kind, accX, accM, accX13, cost, note=""):
        rows.append(dict(option=name, kind=kind, acc_X17=accX, acc_M1=accM, acc_X17_E13=accX13,
                         cost_lo=cost[0], cost=cost[1], cost_hi=cost[2], note=note))

    k0 = "n_TOF as built: MM + SiPM16 + 2cm plastics"
    add("n_TOF as built (16 bars ganged, 2 x 20x30x2 plastics)", "baseline",
        X[k0]["acc"], M[k0]["acc"], X[k0]["acc_E13"], (0, 0, 0))
    k1 = "as built, SiPM20 + 2cm plastics"
    add("as built + all 20 SiPM bars", "baseline",
        X[k1]["acc"], M[k1]["acc"], X[k1]["acc_E13"], (0, 0, 0), "SiPM completion counted in the common block")
    k2 = "LS working: MM + SiPM20 + LS"
    add("LS working, LS alone as trigger", "LS", X[k2]["acc"], M[k2]["acc"], X[k2]["acc_E13"], C.LS_REVIVAL)
    k3 = "LS working: MM + SiPM20 + (plastic OR LS)"
    add("LS working, plastic OR LS", "LS", X[k3]["acc"], M[k3]["acc"], X[k3]["acc_E13"], C.LS_REVIVAL)
    sx, sm = scans["X17"], scans["M1"]
    for (W, L, T, pmt, mat) in [(50, 50, 2, '3"', "PVT"), (60, 60, 2, '3"', "PVT"), (70, 70, 2, '3"', "PVT"),
                                (78, 80, 2, '2"', "PVT"), (78, 80, 2, '3"', "PVT"), (78, 100, 2, '3"', "PVT"),
                                (70, 70, 4, '3"', "PVT"), (78, 80, 4, '3"', "PVT"), (78, 80, 4, '3"', "PS"),
                                (70, 70, 5, '3"', "PVT"), (78, 80, 5, '3"', "PVT"), (78, 80, 5, '5"', "PVT"),
                                (78, 80, 5, '3"', "PS"), (78, 80, 10, '5"', "PVT")]:
        rx, rm = pick(sx, W, L, T), pick(sm, W, L, T)
        kind = "plastic 2 cm" if T == 2 else ("plastic 4-5 cm" if T in (4, 5) else f"plastic {T:g} cm")
        add(f"4 x {W}x{L}x{T:g} cm {mat}, 2 x {pmt} PMT each", kind, rx.acc, rm.acc, rx.acc_E13,
            C.four_slabs(W, L, T, pmt=pmt, material=mat))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "options.csv", index=False)
    return df


def fig_cost(df):
    kinds = ["baseline", "LS", "plastic 2 cm", "plastic 4-5 cm", "plastic 10 cm"]
    fig, axs = plt.subplots(1, 2, figsize=(10.4, 4.4), constrained_layout=True)
    for ax, col, lab in ((axs[0], "acc_X17", "X17 acceptance (% of pairs)"),
                         (axs[1], "acc_X17_E13", "X17 acceptance x P(Esum > 13 MeV) (%)")):
        for i, k in enumerate(kinds):
            d = df[df.kind == k]
            if not len(d):
                continue
            x = d.cost / 1e3
            xerr = np.vstack([(d.cost - d.cost_lo) / 1e3, (d.cost_hi - d.cost) / 1e3])
            ax.errorbar(x, 100 * d[col], xerr=xerr, fmt=MARK[i], color=SEQ[i], ms=6, lw=1.0,
                        capsize=2, label=k, mec="white", mew=0.8)
        ax.set_xlabel("incremental cost (kEUR, budgetary; bars = low-high)")
        ax.set_ylabel(lab)
        ax.set_ylim(0, None)
        ax.set_xlim(-8, None)
    # direct labels on a curated subset (the rest are identified by the legend + options.csv)
    LAB = {"acc_X17": [("n_TOF as built", "n_TOF as built", (6, -10)),
                       ("plastic OR LS", "LS working, OR plastics", (6, 2)),
                       ("LS alone", "LS alone", (6, -4)),
                       ("50x50x2 cm PVT", "50x50x2", (6, -11)),
                       ("60x60x2 cm PVT", "60x60x2", (6, -11)),
                       ("70x70x2 cm PVT", "70x70x2", (-20, -13)),
                       ("78x80x2 cm PVT, 2 x 3", "78x80x2", (8, -13)),
                       ("78x80x4 cm PS", "4-5 cm, PS or PVT", (-30, 8)),
                       ("78x80x10", "78x80x10", (-14, 7))],
           "acc_X17_E13": [("n_TOF as built", "n_TOF as built", (4, -13)),
                           ("plastic OR LS", "LS working", (6, 4)),
                           ("78x80x2 cm PVT, 2 x 3", "2 cm slabs", (10, -12)),
                           ("70x70x4 cm PVT", "70x70x4", (-16, -14)),
                           ("78x80x4 cm PS", "78x80x4 PS", (-22, -14)),
                           ("78x80x5 cm PS", "78x80x5 PS", (-26, 7)),
                           ("78x80x5 cm PVT, 2 x 3", "78x80x5", (-4, 7)),
                           ("78x80x10", "78x80x10", (-14, 7))]}
    for ax, col in ((axs[0], "acc_X17"), (axs[1], "acc_X17_E13")):
        for key, txt, off in LAB[col]:
            r = df[df.option.str.contains(key, regex=False)]
            if len(r):
                r = r.iloc[0]
                ax.annotate(txt, (r.cost / 1e3, 100 * r[col]), xytext=off, textcoords="offset points",
                            fontsize=7.5, color=fs.MUTED)
    axs[0].legend(frameon=False, fontsize=8.5, loc="lower right")
    fs.title(axs[0], "Acceptance vs cost", "trigger-scintillator hardware only; DAQ + SiPM completion are common")
    fs.title(axs[1], "With the ILL energy cut", "the thick slabs pay back here")
    fs.save(fig, FIG / "acc_vs_cost", data=df)


def fig_optics(opt):
    opt = opt.copy()
    opt["label"] = opt.apply(lambda r: f"{r.readout}, {r.n_pmt}x{r.pmt}", axis=1)
    opt["size"] = opt.apply(lambda r: f"{r.W_cm:g}x{r.L_cm:g}x{r.T_cm:g}", axis=1)
    sizes = list(dict.fromkeys(opt["size"]))
    labels = list(dict.fromkeys(opt["label"]))
    fig, axs = plt.subplots(1, 2, figsize=(10.4, 4.2), constrained_layout=True)
    x = np.arange(len(sizes))
    for i, lab in enumerate(labels):
        d = opt[opt.label == lab].set_index("size").reindex(sizes)
        axs[0].plot(x, d.pe_per_MeV, marker=MARK[i], color=SEQ[i], lw=1.4, ms=5, label=lab,
                    ls="-" if "edge" in lab else "--")
        axs[1].plot(x, 1e3 * d.sigma_t_5MeV_ns, marker=MARK[i], color=SEQ[i], lw=1.4, ms=5,
                    label=lab, ls="-" if "edge" in lab else "--")
    for ax in axs:
        ax.set_xticks(x)
        ax.set_xticklabels(sizes, rotation=25, fontsize=8.5)
        ax.set_xlabel("slab W x L x T (cm)")
    axs[0].set_yscale("log")
    axs[0].set_ylabel("photoelectrons per MeV (toy, optimistic)")
    axs[1].set_ylabel("sigma_t at 5 MeV, position-corrected (ps)")
    axs[1].axhline(200, color=fs.COPPER, ls="-.", lw=1.0)
    axs[1].text(0, 205, "ILL requirement ~200 ps per arm", fontsize=8, color=fs.MUTED, va="bottom")
    axs[0].legend(frameon=False, fontsize=7.5, ncol=2)
    fs.title(axs[0], "Light yield falls with the end-face area", "edge = fishtail on the short ends; back = PMTs on the back face")
    fs.title(axs[1], "Timing degrades with size; two good PMTs keep it < 200 ps", "k-th pe at 5 % of Npe, TTS + guide spread + 30 ps jitter")
    fs.save(fig, FIG / "optics", data=opt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--acc", default=str(HERE / "sim" / "accept"))
    a = ap.parse_args()
    fs.use()
    S, scans = load(Path(a.acc))
    fig_width(S, scans["X17"])
    fig_length(S, scans["X17"])
    fig_calo(S, scans["X17"])
    df = options(S, scans)
    fig_cost(df)
    opt = pd.read_csv(OUT / "optics.csv")
    fig_optics(opt)
    pd.set_option("display.width", 200)
    print(df[["option", "acc_X17", "acc_M1", "acc_X17_E13", "cost"]].to_string(index=False))


if __name__ == "__main__":
    main()
