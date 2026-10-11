#!/usr/bin/env python3
"""
single_arm_trigger.py -- FEASIBILITY_SIM §14: a single-arm trigger at the ILL.

Reads the lxplus outputs of sim/lxplus/single_arm.py (copied to
sim/analysis_v3/single_arm/sa_*.csv) and the two-arm rate scans
(sim/analysis_v3/cons/walls_*_e14.csv), and writes to out/single_arm/:

  trigger_vs_T.{png,csv}   single-arm trigger rate vs the arm threshold T at
                           6e10 n/s, by source (neutrons per variant,
                           ³He(n,γ), cosmics), against the DREAM limits
  live.csv                 two-arm vs two-arm OR single-arm: rate, live time,
                           the exposure cost, per variant / T / R
  yields.csv               same-arm IPC per cycle vs T, and the ³He(n,γ)
                           single-arm events with MM charge (the background
                           before any two-track cut)
  theta_spectra.{png,csv}  0-180 deg opening-angle spectra per cycle: the
                           two-arm sample (Esum > 13) and the same-arm one
                           (E_arm > 13 / 10, first gap hits >= 5 mm apart)

    ~/PycharmProjects/nTof_x17/.venv/bin/python ill/single_arm_trigger.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import figstyle as fs  # noqa: E402

HERE = Path(__file__).resolve().parent
SA = HERE / "sim" / "analysis_v3" / "single_arm"
CONS = HERE / "sim" / "analysis_v3" / "cons"
OUT = HERE / "out" / "single_arm"
DAQ_TAU = 298e-6          # s per trigger, DREAM RAW 20 samples
DAQ_MAX = 3.35e3          # Hz
DAY = 86400.0
DAYS = 50.0
PANEL_INEFF = 1e-2        # ceiling-panel veto, as §8 (here used in the trigger)
RATES = (1.9e10, 6e10)
VARIANTS = {"ringCFRP": "CFRP (air path)", "tubeBe": "tube + Be 0.5", "tubeBe25": "tube + Be 0.25",
            "tubeMy": "tube + mylar"}
WALLS = {"ringCFRP": "walls_CFRP_e14.csv", "tubeBe": "walls_tubeBe_e14.csv",
         "tubeBe25": "walls_tubeBe25_e14.csv", "tubeMy": "walls_tubeMy_e14.csv"}


def two_arm_trigger(v, R):
    """Two-arm hardware trigger rate (Hz) at R from the rate scan (panel row, Esum > 14; the
    hardware rate does not depend on the offline cut).  Log-log interpolation."""
    w = pd.read_csv(CONS / WALLS[v])
    w = w[(w.scenario == "as is") & (w.knobs == "MM occ + DREAM") & w.hw.str.contains("per-arm")]
    w = w.sort_values("R")
    return float(np.exp(np.interp(np.log(R), np.log(w.R), np.log(w.trig_Hz.clip(1e-9)))))


def main():
    fs.use()
    OUT.mkdir(parents=True, exist_ok=True)
    trg = pd.read_csv(SA / "sa_trigger.csv")
    sig = pd.read_csv(SA / "sa_signal.csv")
    th = pd.read_csv(SA / "sa_theta.csv")
    cos = trg[trg.variant == "cosmics_K1"].set_index("T")
    neu = trg[trg.variant != "cosmics_K1"]

    # ---- live time: two-arm vs two-arm OR single-arm ------------------------------------
    rows = []
    for v in VARIANTS:
        for R in RATES:
            f2 = two_arm_trigger(v, R)
            live2 = 1 / (1 + f2 * DAQ_TAU)
            for _, r in neu[neu.variant == v].iterrows():
                T = r["T"]
                fn = r.single_per_abs * R
                fg = r.he3ng_single_per_abs * R
                for panel in (False, True):
                    fc = cos.loc[T, "single_Hz"] * (PANEL_INEFF if panel else 1.0)
                    f1 = fn + fg + fc
                    lv = 1 / (1 + (f2 + f1) * DAQ_TAU)
                    rows.append(dict(variant=v, R=R, T=T, panel_in_trigger=panel, two_arm_Hz=f2,
                                     single_neutron_Hz=fn, single_he3ng_Hz=fg, single_cosmic_Hz=fc,
                                     single_total_Hz=f1, live_two_arm=live2, live_or=lv,
                                     exposure_cost=1 - lv / live2,
                                     reach_factor=float(np.sqrt(live2 / lv)),
                                     over_daq_max=(f2 + f1) > DAQ_MAX))
    live = pd.DataFrame(rows)
    live.to_csv(OUT / "live.csv", index=False)

    # ---- same-arm yields per cycle --------------------------------------------------------
    yrows = []
    g = neu[neu.variant == "tubeBe25"].set_index("T")
    for R in RATES:
        nabs = R * DAYS * DAY
        for T in sorted(sig["T"].unique()):
            s = sig[(sig["T"] == T)]
            d = dict(R=R, T=T)
            for ch in ("M1", "E0", "X17"):
                d[f"{ch}_same_sep5"] = float(s[(s.channel == ch) & (s.kind == "same") & (s.sep_mm == 5.0)].per_abs.iloc[0] * nabs)
                d[f"{ch}_same_sep0"] = float(s[(s.channel == ch) & (s.kind == "same") & (s.sep_mm == 0.0)].per_abs.iloc[0] * nabs)
                d[f"{ch}_two"] = float(s[(s.channel == ch) & (s.kind == "two")].per_abs.iloc[0] * nabs)
            d["he3ng_single_mm"] = float(g.loc[T, "he3ng_single_mm_per_abs"] * nabs)
            d["he3ng_over_ipc_same"] = d["he3ng_single_mm"] / (d["M1_same_sep5"] + d["E0_same_sep5"])
            yrows.append(d)
    yields = pd.DataFrame(yrows)
    yields.to_csv(OUT / "yields.csv", index=False)

    # ---- figure 1: single-arm trigger rate vs T at 6e10 -----------------------------------
    R = 6e10
    fig, ax = fs.figure(fs.FIG)
    data = {}
    Ts = np.array(sorted(neu["T"].unique()))
    for v, lab in VARIANTS.items():
        y = neu[neu.variant == v].set_index("T").loc[Ts, "single_per_abs"].to_numpy() * R
        data[f"neutrons_{v}_Hz"] = y
        ax.semilogy(Ts, np.where(y > 0, y, np.nan), marker="o", ms=3.5, label=f"neutron singles, {lab}")
    yg = g.loc[Ts, "he3ng_single_per_abs"].to_numpy() * R
    yc = cos.loc[Ts, "single_Hz"].to_numpy()
    data["he3ng_Hz"], data["cosmic_Hz"] = yg, yc
    ax.semilogy(Ts, yg, color=fs.COPPER, ls="--", label="³He(n,γ) 20.6 MeV γ")
    ax.semilogy(Ts, yc, color=fs.MUTED, ls=":", label="cosmics (no panel in trigger)")
    ax.axhline(DAQ_MAX, color=fs.BAND_DEAD, lw=1)
    ax.text(0.2, DAQ_MAX * 1.25, "DREAM max 3.35 kHz", color=fs.BAND_DEAD, fontsize=8.5)
    f10 = 1 / (9 * DAQ_TAU)
    ax.axhline(f10, color=fs.MUTED, lw=0.8, ls="-.")
    ax.text(0.2, f10 * 1.25, "10 % dead time", color=fs.MUTED, fontsize=8.5)
    ax.set_xlabel("single-arm threshold T: E(SiPM + plastic + LS) in the arm [MeV]")
    ax.set_ylabel("trigger rate at 6×10¹⁰ n/s [Hz]")
    ax.set_ylim(0.3, 3e5)
    ax.legend(fontsize=8, loc="upper right")
    fs.title(ax, "A single-arm trigger needs E_arm ≳ 10 MeV",
             "per-arm leg (SiPM AND plastic ≥ 0.5 MIP) and E_arm > T; points at 0 are < 1 MC event")
    fs.save(fig, OUT / "trigger_vs_T.png", data=pd.DataFrame(dict(T=Ts, **data)))
    plt.close(fig)

    # ---- figure 2: 0-180 opening-angle spectra per cycle at 6e10 --------------------------
    nabs = 6e10 * DAYS * DAY
    per = dict(M1=sig[sig.channel == "M1"].per_abs.iloc[0] / sig[sig.channel == "M1"].frac.iloc[0],
               E0=sig[sig.channel == "E0"].per_abs.iloc[0] / sig[sig.channel == "E0"].frac.iloc[0],
               X17=sig[sig.channel == "X17"].per_abs.iloc[0] / sig[sig.channel == "X17"].frac.iloc[0])
    x17_ratio = 1.64e-3      # ⁸Be-equivalent X17/IPC(M1), §12
    fig, ax = fs.figure(fs.FIG)
    out = {}
    for sel, lab, ls in (("two13", "two arms, Esum > 13", "-"), ("13.0", "same arm, E_arm > 13", "--")):
        tot = 0
        for ch, col, sc in (("M1", fs.DET_COLOR["A"], 1.0), ("E0", fs.DET_COLOR["C"], 1.0),
                            ("X17", fs.ACCENT, x17_ratio)):
            h = th[(th.channel == ch) & (th.sel == sel) & (th.est == "true")].sort_values("th_lo")
            y = h.frac.to_numpy() * per[ch] * nabs * sc
            x = h.th_lo.to_numpy() + 2.0
            out[f"{ch}_{sel}"] = y
            if ch != "X17":
                tot = tot + y
            ax.step(x, np.where(y > 0, y, np.nan), where="mid", color=col, ls=ls, lw=1.2,
                    label=f"{ch}{' ×1.6e-3' if ch == 'X17' else ''}, {lab}")
    out["theta_centre"] = x
    ax.set_yscale("log")
    ax.set_xlim(0, 180)
    ax.set_ylim(1, 3e6)
    ax.set_xlabel("true opening angle θ [deg]")
    ax.set_ylabel("pairs per 4° per 50-day cycle at 6×10¹⁰ n/s")
    ax.legend(fontsize=7.5, loc="upper right", ncol=1)
    fs.title(ax, "A same-arm trigger adds ~10× the IPC, almost all below 60°",
             "G1, before MM segment / occupancy / live time; same arm: first gap hits ≥ 5 mm apart")
    fs.save(fig, OUT / "theta_spectra.png", data=pd.DataFrame(out))
    plt.close(fig)

    # ---- figure 3: the same-arm sample, IPC vs ³He(n,γ) two-track fakes (chord angle) -----
    # hs_*.csv: sim/lxplus/he3ng_samearm.py merge on the C1g HitTree, per cycle at 6e10 n/s
    hs = pd.read_csv(SA / "hs_theta.csv")
    hc = pd.read_csv(SA / "hs_counts.csv")
    fig, ax = fs.figure(fs.FIG)
    out = {}
    for ch, col in (("M1", fs.DET_COLOR["A"]), ("E0", fs.DET_COLOR["C"])):
        h = th[(th.channel == ch) & (th.sel == "13.0") & (th.est == "chord")].sort_values("th_lo")
        y = h.frac.to_numpy() * per[ch] * nabs
        out[f"{ch}_T13"] = y
        ax.step(h.th_lo + 2.0, np.where(y > 0, y, np.nan), where="mid", color=col, lw=1.2,
                label=f"IPC {ch}, same arm, E_arm > 13")
    for T, ls in ((13.0, "-"), (10.0, "--")):
        g3 = hs[hs["T"] == T].sort_values("th_lo")
        out[f"he3ng_T{T:g}"] = g3.per_cycle.to_numpy()
        out[f"he3ng_T{T:g}_nmc"] = g3.n_mc.to_numpy()
        ax.step(g3.th_lo + 2.0, np.where(g3.per_cycle > 0, g3.per_cycle, np.nan), where="mid", color=fs.COPPER,
                ls=ls, lw=1.4, label=f"³He(n,γ) γ, two tracks, E_arm > {T:g}")
    out["theta_centre"] = np.arange(2.0, 180.0, 4.0)
    ax.set_yscale("log")
    ax.set_xlim(0, 90)
    ax.set_ylim(5e2, 3e5)
    ax.set_xlabel("chord opening angle from the origin [deg]")
    ax.set_ylabel("per 4° per 50-day cycle at 6×10¹⁰ n/s")
    ax.legend(fontsize=7.5, loc="upper right")
    f13 = hc[(hc["T"] == 13.0) & (hc.sep_mm == 5.0)].per_cycle.iloc[0]
    fs.title(ax, "In one arm, the ³He(n,γ) γ fakes the IPC almost 1 : 1",
             f"two tracks ≥ 5 mm apart in the gap; {f13:.2g}/cycle at 13 MeV, mostly Al end-cap conversions")
    fs.save(fig, OUT / "samearm_fakes.png", data=pd.DataFrame(out))
    plt.close(fig)

    pd.set_option("display.width", 200)
    print(live[(live["T"].isin([8, 10, 12, 13])) & ~live.panel_in_trigger][
        ["variant", "R", "T", "two_arm_Hz", "single_neutron_Hz", "single_he3ng_Hz", "single_cosmic_Hz",
         "live_two_arm", "live_or", "reach_factor"]].round(4).to_string(index=False))
    print(yields[yields.R == 6e10][["T", "M1_same_sep5", "E0_same_sep5", "M1_two", "E0_two", "X17_same_sep5",
                                    "he3ng_single_mm", "he3ng_over_ipc_same"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
