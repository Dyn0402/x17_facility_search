#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sipm_readout.py -- the numbers behind daq_trigger/SIPM_READOUT.md: reading the SiPM walls
channel by channel (every bar end, or every SiPM) instead of the n_TOF ganged groups.

    python daq_trigger/sipm_readout.py      # -> daq_trigger/out/sipm_channels.csv, out/sipm_costs.csv

Two small tables, no simulation:

  sipm_channels.csv  channels, boards per wall, data per event and per second at the trigger rate,
                     for each granularity x front end.
  sipm_staged.csv    LNL with the ganged walls first, then per-channel walls: cost per stage and what is left
                     unused, for each upgrade path (SIPM_READOUT.md §8).
  sipm_costs.csv     the wall readout + the trigger parts it changes, central and range (EUR 2026),
                     from budget/items.py unit prices plus the new items marked here (guess unless marked).

Each option replaces the "V1742 (32 wall ch)" and the M1 wall-sum path of PLAN.md architecture B; the PMT
side (N979 + V1730S, M2-M6) is common to all and not repeated.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
sys.path.insert(0, str(HERE.parent / "budget"))

N_WALLS, N_BARS = 4, 20
GRAN = {                     # channels per wall
    "ganged 4 bars (n_TOF, 16 bars)": 8,
    "ganged 4 bars, 20 bars lit": 10,
    "per bar end": 2 * N_BARS,
    "per SiPM (2 per bar end)": 4 * N_BARS,
}
TRIG_HZ = (100, 250, 1000)   # LNL 1 uA, LNL 4 uA, a high-rate facility (PLAN.md §2.2)

# bytes per channel per event (zero suppression off: the walls are read on every trigger)
BYTES = {
    "FERS A5204 (Radioroc + picoTDC)": 12,       # LG + HG 2 B each, ToA 4 B, ToT 2 B, header share: guess
    "FERS A5202 (Citiroc)": 10,
    "V1742 waveform (1024 x 2 B)": 2048,
    "VX2745 waveform (~200 ns x 125 MS/s x 2 B)": 60,
}
CH_PER_BOARD = {"FERS A5204 (Radioroc + picoTDC)": 64, "FERS A5202 (Citiroc)": 64,
                "V1742 waveform (1024 x 2 B)": 32, "VX2745 waveform (~200 ns x 125 MS/s x 2 B)": 64}


def channels_table() -> pd.DataFrame:
    rows = []
    for g, chw in GRAN.items():
        for fe, cpb in CH_PER_BOARD.items():
            if g.startswith("ganged") and fe.startswith("FERS"):
                continue           # ganged sums are preamplified analog: not a FERS input
            boards_wall = -(-chw // cpb)
            # boards are not shared between walls: each wall's trigger out is its own OR
            n_boards = boards_wall * N_WALLS if fe.startswith("FERS") else -(-(chw * N_WALLS) // cpb)
            ev = chw * N_WALLS * BYTES[fe]
            rows.append(dict(granularity=g, front_end=fe, channels=chw * N_WALLS, boards=n_boards,
                             spare_channels=n_boards * cpb - chw * N_WALLS, kB_per_event=round(ev / 1e3, 2),
                             **{f"MB_s_at_{f}Hz": round(ev * f / 1e6, 2) for f in TRIG_HZ}))
    return pd.DataFrame(rows)


def costs_table() -> pd.DataFrame:
    import items as IT
    T = IT.times
    add = lambda *xs: tuple(sum(x[k] for x in xs) for k in range(3))   # noqa: E731
    # new unit prices (guess unless marked): CAEN quotes on request only
    A5202 = (3500, 4500, 6000)             # per board; budget FERS item is 3 x A5202 + DT5215 = 12-25k
    A5204 = (4500, 6500, 9000)             # per board, Radioroc 2 + picoTDC: dearer than the A5202 (guess)
    DT5215 = (2000, 3000, 4500)            # TDlink concentrator, up to 128 boards
    # Every SiPM channel leaves the wall on its own micro-coax: 20 SiPM cards x 4 channels = 80 per wall
    # (MX17_Documentation/sipm_wall, May 2026).  At n_TOF external boards summed them into ganged LEMO outputs
    # (Dylan, 30 Oct), so per-channel readout needs a custom board on the micro-coax (guess):
    ADAPT = (2000, 4000, 8000)             # micro-coax -> FERS-input board, 4 walls: design + fab + flats; for 160 ch
                                           #   it pairs the two channels of a bar end
    ADAPT_320 = (2500, 5000, 10000)
    AMP = (3000, 6000, 10000)              # x10 amplifiers (the INFN 2-ch, +-6 V design) for 160 ch into a digitizer
    AMP_320 = (5000, 10000, 16000)
    DARK_SIPMS = (0, 0, 2500)              # the rebuilt plane has all 20 SiPMs fitted (5 spares exist); ask for the others
    LEMO160 = (2000, 4000, 8000)           # budget lemo item c160
    LEMO320 = (3500, 7000, 13000)          # budget lemo item c320
    VME = (5000, 6500, 8000)
    FIFO4 = T(4, IT.FIFO)                  # the 4 wall-sum FIFOs that the ganged path needs (PLAN.md §5.2)
    N1081B = IT.N1081B                     # M1 (wall OR on the sums) is dropped when the front end makes the wall OR
    opts = {
        "G  ganged as n_TOF (PLAN B): V1742, 4 sum FIFOs, M1": [
            ("V1742 (32 ch) share", IT.V1742_GANG), ("4 x linear FIFO (wall sums)", FIFO4), ("M1 N1081B", N1081B)],
        "F160  per bar end, 4 x A5204 on the walls": [
            ("4 x A5204", T(4, A5204)), ("DT5215", DT5215), ("custom micro-coax -> FERS boards, 4 walls", ADAPT),
            ("SiPMs for the 4 dark bars (if missing)", DARK_SIPMS)],
        "F320  per SiPM channel, 8 x A5204": [
            ("8 x A5204", T(8, A5204)), ("DT5215", DT5215), ("custom micro-coax -> FERS boards, 320 ch", ADAPT_320),
            ("SiPMs for the 4 dark bars (if missing)", DARK_SIPMS)],
        "F160c  as F160 with the A5202 (Citiroc; INFN's bench board)": [
            ("4 x A5202", T(4, A5202)), ("DT5215", DT5215), ("custom micro-coax -> FERS boards, 4 walls", ADAPT),
            ("SiPMs for the 4 dark bars (if missing)", DARK_SIPMS)],
        "P160  per bar end, x10 amplifiers -> 5 x V1742 (waveforms)": [
            ("5 x V1742 + VME", IT.V1742_5), ("x10 amplifiers, 160 ch", AMP), ("custom micro-coax -> LEMO boards", ADAPT), ("LEMO 160", LEMO160),
            ("4 x linear FIFO (sums)", FIFO4), ("M1 N1081B", N1081B)],
        "P320  per SiPM channel, x10 amplifiers -> 5 x VX2745 (64 ch, 125 MS/s)": [
            ("5 x VX2745 (VX2745 160-ch price x 5/3) + crate", tuple(IT._r(v * 5 / 3) for v in IT.VX2745)),
            ("x10 amplifiers, 320 ch", AMP_320), ("custom micro-coax -> LEMO boards", ADAPT_320), ("LEMO 320", LEMO320), ("M1 N1081B", N1081B)],
        "T160  PETsys TOFPET2 256-ch (trigger-less: no hardware wall OR, ask)": [
            ("PETsys 256 ch", IT.PETSYS), ("custom micro-coax -> PETsys boards, 4 walls", ADAPT),
            ("SiPMs for the 4 dark bars (if missing)", DARK_SIPMS)],
    }
    rows = []
    for o, parts in opts.items():
        for name, c in parts:
            rows.append(dict(option=o, part=name, low=c[0], central=c[1], high=c[2]))
        tot = add(*(c for _, c in parts))
        rows.append(dict(option=o, part="TOTAL", low=tot[0], central=tot[1], high=tot[2]))
    return pd.DataFrame(rows)


def staged_table() -> pd.DataFrame:
    """LNL first with the ganged walls, then per-channel walls: what each path costs at each stage, and what it
    leaves unused.  Stage costs include the PMT digitizer (8-16 PMTs + trigger word), which every path needs."""
    import items as IT
    T = IT.times
    add = lambda *xs: tuple(sum(x[k] for x in xs) for k in range(3))   # noqa: E731
    V1730S = (10000, 12800, 16000)         # daq_plan.py
    VX2730 = (15000, 20000, 26000)         # 32 ch, 500 MS/s, 14 bit, 2nd generation (guess; CAEN quotes only)
    VME = (5000, 6500, 8000)
    A5202, A5204, DT5215 = (3500, 4500, 6000), (4500, 6500, 9000), (2000, 3000, 4500)
    BOARD = (2000, 4000, 8000)             # custom micro-coax board, 4 walls (as costs_table ADAPT)
    WALL_TRIG = add(T(4, IT.FIFO), IT.N1081B)   # 4 sum FIFOs + M1: the ganged path's analog wall OR
    fers160 = add(T(4, A5202), DT5215, BOARD)
    fers_more = T(4, A5202)                # 160 -> 320: a second board per wall (not recommended, §0)
    paths = {
        "1  PLAN B: V1742 (ganged walls) + V1730S (PMTs); FERS added later": dict(
            lnl=add(IT.V1742_GANG, V1730S, VME, WALL_TRIG), up160=fers160, up320=fers_more,
            stranded="V1742 + sum FIFOs + M1 after the upgrade (~EUR 26 k)"),
        "1b as 1, the V1742 borrowed (LNL pool, ask); FERS added later": dict(
            lnl=add(V1730S, VME, WALL_TRIG), up160=fers160, up320=fers_more,
            stranded="sum FIFOs + M1 (~EUR 12 k); nothing if those are borrowed too"),
        "2  2 x VX2730 for walls + PMTs (500 MS/s); FERS added later": dict(
            lnl=add(T(2, VX2730), VME, WALL_TRIG), up160=fers160, up320=fers_more,
            stranded="one VX2730 becomes a spare; sum FIFOs + M1"),
        "3  FERS from day one: micro-coax board + 4 x A5202 at LNL (per bar end), V1730S for PMTs": dict(
            lnl=add(fers160, V1730S, VME), up160=(0, 0, 0), up320=fers_more,
            stranded="nothing; but the first run relies on the FERS trigger out (bench test S2 first)"),
        "3b as 3 with A5204 (better time)": dict(
            lnl=add(T(4, A5204), DT5215, BOARD, V1730S, VME), up160=(0, 0, 0), up320=T(4, A5204),
            stranded="nothing; as 3"),
        "4  ganged walls into FERS through an attenuator (ask CAEN), then micro-coax": dict(
            lnl=add(T(2, A5202), DT5215, V1730S, VME), up160=add(T(2, A5202), BOARD), up320=fers_more,
            stranded="nothing; untested: Citiroc is built for SiPM charge, not an amplified voltage pulse"),
    }
    rows = []
    for name, d in paths.items():
        rows.append(dict(path=name,
                         lnl_central=d["lnl"][1], lnl_low=d["lnl"][0], lnl_high=d["lnl"][2],
                         to160_central=d["lnl"][1] + d["up160"][1],
                         to320_central=d["lnl"][1] + d["up160"][1] + d["up320"][1],
                         stranded=d["stranded"]))
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(exist_ok=True)
    ch, co = channels_table(), costs_table()
    ch.to_csv(OUT / "sipm_channels.csv", index=False)
    co.to_csv(OUT / "sipm_costs.csv", index=False)
    st = staged_table()
    st.to_csv(OUT / "sipm_staged.csv", index=False)
    with pd.option_context("display.width", 220, "display.max_columns", 20, "display.max_colwidth", 70):
        print(ch, "\n")
        print(co[co.part == "TOTAL"][["option", "low", "central", "high"]], "\n")
        print(st)


if __name__ == "__main__":
    main()
