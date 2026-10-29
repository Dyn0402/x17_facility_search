#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
daq_plan.py -- the numbers behind daq_trigger/PLAN.md.

    python daq_trigger/daq_plan.py          # -> daq_trigger/out/*.csv, out/figures/*.png (+ .csv)

Four small tables, no simulation:

  live.csv        DREAM live fraction for each facility's trigger rate, with DREAM left to drop triggers
                  on its own (tau = 298 us, non-paralysable) and with an artificial busy of T us made in the
                  trigger logic, which locks the DREAM and digitizer event lists 1:1 (PLAN.md §4.2).
  randoms.csv     two-arm accidental triggers against the coincidence window, for the leg rates of each
                  facility: what a wider (digitizer-formed) window would cost (PLAN.md §5.3).
  power.csv       mains load of the DAQ racks, to size the switched PDUs (PLAN.md §7).
  costs.csv       the trigger + scintillator-DAQ hardware of each architecture (PLAN.md §5, §9), central and
                  range, from the budget's unit prices (budget/items.py) plus the new items marked here.

Rates are copied from the facility write-ups (source column); nothing is re-derived.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
sys.path.insert(0, str(HERE.parent / "budget"))
sys.path.insert(0, str(HERE.parent / "ill"))

TAU_DREAM = 298e-6          # s, mean event spacing at saturation, RAW 20 samples (nTof_x17_DAQ REPORT_2026-07-28 §3.3)
TAU_FLOOR = 210e-6          # s, SCA readout floor at IPD 5 (same report, run_90)
VETO_T = (330e-6, 350e-6)   # s, artificial busy candidates: > the wire-limited 298 us with margin (to be measured, §10 T2)

# offered trigger rate f [Hz] = PAIR + SINGLE/P + clock, per facility and configuration.
# legs and pairs are totals over the four arms.
SCEN = [
    # name, legs/s, pairs/s, P (None = PAIR only), source
    ("LNL window, big plastics, 1 uA", 720, 25, 10, "lnl/target/SHAPES_GEANT.md §5"),
    ("LNL window, big plastics, 4 uA", 2880, 100, 20, "SHAPES_GEANT §5 (legs x4, pairs 25-80/s)"),
    ("LNL Be ogive + Mo, big plastics, 4 uA", 4080, 96, 50, "SHAPES_GEANT §10.3"),
    ("LNL window, as built, 1 uA", 250, 3.8, 1, "SHAPES_GEANT §5"),
    ("ILL PF1B, as built (no tube)", None, 249, None, "ill/FEASIBILITY_SIM.md §13 (trigger 249 Hz)"),
    ("ILL PF1B, He tube + segments", None, 8, None, "ill/FEASIBILITY_SIM.md §13"),
    ("Birmingham 30 bar cell, big plastics", None, 616, None, "birmingham/TARGET_GEANT.md §5 (PAIR only)"),
    ("FRM II MEDAPP (throttled x0.3)", None, 3200, None, "frm2_medapp/FEASIBILITY.md (randoms 3.2e3/s)"),
]
CLOCK_HZ = 1.0


def live_table() -> pd.DataFrame:
    rows = []
    for name, legs, pairs, P, src in SCEN:
        f = pairs + CLOCK_HZ + (legs / P if (legs and P) else 0.0)
        r = dict(scenario=name, legs_per_s=legs, pairs_per_s=pairs, prescale=P if P else "PAIR only",
                 offered_hz=round(f, 1), live_dream_native=1 / (1 + f * TAU_DREAM))
        for T in VETO_T:
            r[f"live_veto_{T * 1e6:.0f}us"] = 1 / (1 + f * T)
        r["extra_dead_pct_at_350"] = 100 * (r["live_dream_native"] - r["live_veto_350us"])
        r["source"] = src
        rows.append(r)
    df = pd.DataFrame(rows)
    for c in [c for c in df.columns if c.startswith("live")]:
        df[c] = df[c].round(4)
    df["extra_dead_pct_at_350"] = df["extra_dead_pct_at_350"].round(2)
    return df


# leg rate per arm [/s] for the accidental estimate (busiest arm stated in the write-ups; arms taken equal,
# which over-states randoms by up to x2 where one arm dominates)
LEG_ARM = [
    ("LNL Be ogive, big plastics, 4 uA", 4080 / 4, "SHAPES_GEANT §10.3"),
    ("Birmingham 30 bar cell, big plastics", 3.8e4, "TARGET_GEANT §5 (busiest arm)"),
    ("Birmingham capsule, big plastics", 1.5e4, "TARGET_GEANT §5"),
]
WINDOWS_NS = (10, 20, 30, 40, 60, 80, 100)


def randoms_table() -> pd.DataFrame:
    rows = []
    for name, r, src in LEG_ARM:
        for w in WINDOWS_NS:
            # two-arm randoms among 4 arms, each pair of arms: 2 w r_i r_j (overlap of two windows of width w)
            acc = 6 * 2 * w * 1e-9 * r * r
            rows.append(dict(scenario=name, leg_rate_per_arm=r, window_ns=w, randoms_per_s=round(acc, 2),
                             live_native=round(1 / (1 + acc * TAU_DREAM), 4), source=src))
    return pd.DataFrame(rows)


# mains load, W (typical, AC side). Sources: N1081B datasheet 1.5 A @ 12 V; DT1081B 90 mA @ 220 VAC;
# DREAM 8 FEU ~5 A + TCM ~5 A at 5 V (budget/items.py lvfeu); the rest are typical catalogue figures (guess).
POWER = [
    # rack, item, n, W each (AC), note
    ("trigger", "N1081B (in a NIM bin)", 6, 18 / 0.75, "1.5 A @ 12 V, bin PSU ~75 % efficient"),
    ("trigger", "linear FIFO / N979 / N93B (NIM)", 8, 15, "guess"),
    ("trigger", "NIM bin fans + PSU idle", 2, 40, "guess"),
    ("trigger", "NETIO / Gude PDU + network switch", 1, 30, "guess"),
    ("readout", "DREAM 8 FEU + TCM via 5 V / 60 A supply", 1, 45 * 5 / 0.8, "~45 A at 5 V, supply ~80 % efficient"),
    ("readout", "VME crate with 3 x V1730S + bridge", 1, 350, "guess: ~60 W per board + crate"),
    ("readout", "HV: 2 x DT1471ET + 2 x N1470", 1, 120, "guess"),
    ("readout", "SiPM bias supply (63 V)", 1, 100, "guess; up to 320 W unit"),
    ("computing", "DAQ PC + scintillator-DAQ PC", 2, 350, "guess"),
    ("computing", "10 GbE switch, NAS", 1, 150, "guess"),
]


def power_table() -> pd.DataFrame:
    df = pd.DataFrame(POWER, columns=["rack", "item", "n", "W_each", "note"])
    df["W"] = (df.n * df.W_each).round(0)
    df["A_at_230V"] = (df.W / 230).round(2)
    tot = df.groupby("rack", as_index=False)[["W", "A_at_230V"]].sum()
    tot["item"] = "TOTAL " + tot.rack
    return pd.concat([df, tot.assign(n="", W_each="", note="")], ignore_index=True)


def costs_table() -> pd.DataFrame:
    import items as IT   # budget/items.py unit prices (EUR, low/central/high)
    # new unit prices for this plan (guess unless marked)
    N979 = (2000, 2800, 3800)          # CAEN 16-ch fast amp, 2 bridged outputs per channel; x2 gain on request
    N93B = (1200, 2000, 3000)          # dual timer / gate generator (the n_TOF one was CERN's); used ~0.5k
    V1730S = (10000, 12800, 16000)     # 16 ch 500 MS/s 14 bit VME; costs.py 0.8 k/ch share
    VME = (5000, 6500, 8000)           # crate + optical bridge (A3818 + link); budget: "adds ~5-8k"
    DT5495 = IT.ITEMS[[i["id"] for i in IT.ITEMS].index("prescale")]["options"][1]["cost"]  # FPGA unit, 5-12k
    FERS4 = tuple(IT._r(v * 4 / 3) for v in IT.FERS)  # one A5202 per wall: 4 boards + concentrator
    PDU8 = (450, 520, 650)             # NETIO PowerPDU 8KS (catalog: ~GBP 438 ex VAT; US $460-600)
    PDU_GUDE = (700, 750, 900)         # Gude 8226-1, 12 outlets, 2 x 16 A (catalog: EUR 741 ex VAT)
    SPLIT = (500, 1500, 3000)          # 40 passive resistive splitters, made up
    CABLES = (1500, 3000, 4500)        # ~150 LEMO patch cables + adapters (budget splitters item, cable part)
    T = IT.times
    # walls (32 ganged ch) on a DRS4 V1742, PMTs + trigger word on one V1730S: the busy lock (>= 330 us) hides
    # the V1742 dead time (~110 us per event, guess), so the cheap DRS4 costs no live time (PLAN.md §6)
    WALLDIG = tuple(a + b + c for a, b, c in zip(IT.V1742_GANG, V1730S, VME))

    def total(parts):
        return tuple(sum(p[k] for _, p in parts) for k in range(3))

    arch = {
        "A  n_TOF clone (passive splits, 6 N1081B)": [
            ("6 x N1081B", T(6, IT.N1081B)), ("6 x linear FIFO", T(6, IT.FIFO)), ("40 passive splitters", SPLIT),
            ("LEMO patch", CABLES), ("N93B (busy, gates)", N93B), ("V1742 (32 wall ch) + V1730S (PMTs, word) + VME", WALLDIG),
            ("2 NIM bins (+ CEA)", T(2, IT.NIM_CRATE)), ("2 x PDU", T(2, PDU8))],
        "B  recommended: active split (N979) + N1081B logic, NIM": [
            ("6 x N1081B", T(6, IT.N1081B)), ("3 x N979 (x2 gain)", T(3, N979)), ("4 x linear FIFO (wall sums)", T(4, IT.FIFO)),
            ("LEMO patch", CABLES), ("N93B (busy, gates)", N93B), ("V1742 (32 wall ch) + V1730S (PMTs, word) + VME", WALLDIG),
            ("2 NIM bins (+ CEA)", T(2, IT.NIM_CRATE)), ("PDU 8KS + Gude 12", tuple(a + b for a, b in zip(PDU8, PDU_GUDE)))],
        "B' as B with 6 x DT1081B desktop (per-board power cycle)": [
            ("6 x DT1081B (price as N1081B, ask)", T(6, IT.N1081B)), ("3 x N979 (x2 gain)", T(3, N979)),
            ("4 x linear FIFO (wall sums)", T(4, IT.FIFO)), ("LEMO patch", CABLES), ("N93B (busy, gates)", N93B),
            ("V1742 (32 wall ch) + V1730S (PMTs, word) + VME", WALLDIG),
            ("1 NIM bin (+ CEA)", T(1, IT.NIM_CRATE)), ("PDU 8KS + Gude 12", tuple(a + b for a, b in zip(PDU8, PDU_GUDE)))],
        "C  digitizer-formed trigger (V1730 LVDS -> DT5495), no splits": [
            ("3 x V1730S + VME", tuple(a + b for a, b in zip(T(3, V1730S), VME))), ("DT5495 + mezzanines", DT5495),
            ("1 x N1081B (scalers, spare, NIM glue)", IT.N1081B), ("LEMO / LVDS cables", T(1, (800, 1500, 2500))),
            ("0 NIM bins (CEA bin)", (0, 0, 0)), ("PDU 8KS", PDU8)],
        "D  upgrade: FERS on 160 bar ends (T-OUT per wall) + B for the PMTs": [
            ("FERS 4 x A5202 + DT5215", FERS4), ("5 x N1081B (no M1)", T(5, IT.N1081B)), ("1 x N979 (PMTs)", N979),
            ("LEMO patch", CABLES), ("N93B (busy, gates)", N93B), ("1 x V1730S (PMTs + word) + VME", tuple(a + b for a, b in zip(V1730S, VME))),
            ("1 NIM bin (+ CEA)", T(1, IT.NIM_CRATE)), ("PDU 8KS + Gude 12", tuple(a + b for a, b in zip(PDU8, PDU_GUDE)))],
    }
    rows = []
    for a, parts in arch.items():
        for name, c in parts:
            rows.append(dict(architecture=a, part=name, low=c[0], central=c[1], high=c[2]))
        lo, ce, hi = total(parts)
        rows.append(dict(architecture=a, part="TOTAL", low=lo, central=ce, high=hi))
    return pd.DataFrame(rows)


def figures(live: pd.DataFrame, rnd: pd.DataFrame):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use()
    F = OUT / "figures"
    F.mkdir(parents=True, exist_ok=True)
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2))
    ax = axs[0]
    f = np.logspace(0, 4, 200)
    curve = pd.DataFrame(dict(offered_hz=f, native_298us=1 / (1 + f * TAU_DREAM),
                              veto_330us=1 / (1 + f * 330e-6), veto_350us=1 / (1 + f * 350e-6)))
    ax.plot(f, curve.native_298us, color="#0072B2", label="DREAM drops triggers itself (τ 298 µs)")
    ax.plot(f, curve.veto_350us, color="#D55E00", ls="--", label="artificial busy 350 µs (1:1 event lock)")
    for _, r in live.iterrows():
        ax.plot(r.offered_hz, r.live_dream_native, "o", color="#555", ms=4)
        ax.annotate(r.scenario.replace(", big plastics", "").replace(" (throttled x0.3)", ""), (r.offered_hz, r.live_dream_native),
                    fontsize=6, xytext=(3, 3), textcoords="offset points")
    ax.set_xscale("log")
    ax.set_xlabel("offered trigger rate [Hz]")
    ax.set_ylabel("live fraction")
    ax.set_ylim(0.2, 1.02)
    ax.legend(fontsize=7, loc="lower left")
    ax.set_title("DREAM live time: native vs locked to the trigger", fontsize=9)
    ax = axs[1]
    for name, g in rnd.groupby("scenario", sort=False):
        ax.plot(g.window_ns, g.randoms_per_s, "o-", ms=3, label=name)
    ax.set_yscale("log")
    ax.set_xlabel("arm-coincidence window [ns]")
    ax.set_ylabel("two-arm randoms [/s]")
    ax.legend(fontsize=7)
    ax.set_title("What a wider coincidence window costs", fontsize=9)
    fs.save(fig, F / "live_and_randoms.png", data=curve)
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    live, rnd, pw, co = live_table(), randoms_table(), power_table(), costs_table()
    live.to_csv(OUT / "live.csv", index=False)
    rnd.to_csv(OUT / "randoms.csv", index=False)
    pw.to_csv(OUT / "power.csv", index=False)
    co.to_csv(OUT / "costs.csv", index=False)
    with pd.option_context("display.width", 200, "display.max_columns", 20, "display.max_colwidth", 60):
        print(live.drop(columns="source"), "\n")
        print(rnd[rnd.window_ns.isin((20, 40, 80))].drop(columns="source"), "\n")
        print(pw[pw.item.str.startswith("TOTAL")][["item", "W", "A_at_230V"]], "\n")
        print(co[co.part == "TOTAL"][["architecture", "low", "central", "high"]])
    figures(live, rnd)


if __name__ == "__main__":
    main()
