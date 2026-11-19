#!/usr/bin/env python3
"""inventory.py -- the MX17 hardware that exists: what we have, who owns it, where it is, whether we may take it.

    python3 inventory/inventory.py        # -> inventory/out/inventory.json + inventory/INVENTORY.md

The single list of physical assets, for every facility study. It records facts about things, not plans:
  - a study's plan (e.g. lnl_x17/planning/plan.py HARDWARE) refers to assets here by id (`inv=[...]`) and adds
    what that run needs, by when, and who we ask;
  - budget/items.py prices what we do NOT have (buy / borrow options). `budget` below names the items.py id.

Fields
  id      short, stable; never reuse one
  name    what it is; qty how many (text)
  cat     mm | readout | scint | trigger | daq | power | gas | target | site
  owner   who owns it (the lender if we borrow it)
  where   where it is now (last known); (ask) if unknown
  cond    good | fix | rebulk | partial | unknown
  avail   ours       ours to take to any run
          lend       owner lends it on request (ask each time)
          returned   was lent for n_TOF and has gone back; must be asked for again
          stays      stays where it is (facility equipment), not available to other runs
  contact our contact for it
  budget  the budget/items.py item id that prices a replacement or the missing part, if any
  note    facts; sources in brackets

Unknown facts are written (ask). Dates are absolute. Update `UPDATED` and the note when a fact changes.
"""
from __future__ import annotations

import json
from pathlib import Path

UPDATED = "2026-11-19"
HERE = Path(__file__).resolve().parent

CATS = dict(mm="Micromegas", readout="Micromegas readout", scint="Scintillators", trigger="Trigger logic",
            daq="DAQ computing", power="Power", gas="Gas", target="Target", site="Site and mechanics")

ASSETS = [
    # --- Micromegas (budget/items.py MM_STATUS holds the bench numbers)
    dict(id="mmA", name="Micromegas A (det3)", qty="1", cat="mm", owner="MX17 collaboration", where="(ask)", cond="good",
         avail="ours", contact="Dylan", budget="windows",
         note="Best chamber: 92.9 % within 5 mm on the cosmic bench. Bulked by Stephan (CEA), 15 Jun 2026."),
    dict(id="mmB", name="Micromegas B (det2)", qty="1", cat="mm", owner="MX17 collaboration", where="(ask)", cond="fix",
         avail="ours", contact="Dylan / Stephan (CEA)", budget="driftfix",
         note="91.3 % on the bench. Drift needs a repair, likely just an electrical connection (Dylan, 19 Nov 2026)."),
    dict(id="mmC", name="Micromegas C (det6)", qty="1", cat="mm", owner="MX17 collaboration", where="(ask)", cond="rebulk",
         avail="ours", contact="Dylan / CEA", budget="rebulk", note="57.8 % within 5 mm, spark-limited; needs re-bulking at CEA."),
    dict(id="mmD", name="Micromegas D (det7)", qty="1", cat="mm", owner="MX17 collaboration", where="(ask)", cond="rebulk",
         avail="ours", contact="Dylan / CEA", budget="rebulk", note="43.1 % within 5 mm; ~130 of 512 X channels dead. Needs re-bulking."),
    # --- Micromegas readout
    dict(id="m1cern", name="M1 multiplex cards, CERN design", qty="4", cat="readout", owner="MX17 collaboration (ask)", where="on Micromegas A",
         cond="good", avail="ours", contact="Dylan", budget="m1", note="The clean cards; ran on A at n_TOF."),
    dict(id="m1ital", name="M1 multiplex cards, Italian", qty="12", cat="readout", owner="MX17 collaboration (ask)", where="on Micromegas B, C, D",
         cond="partial", avail="ours", contact="Dylan", budget="m1", note="Noisy at n_TOF; replacing them is budget item m1."),
    dict(id="dream", name="DREAM DAQ: FEUs + trigger/clock unit (TCM)", qty="8 FEUs, 1 TCM", cat="readout", owner="CEA Saclay", where="(ask)",
         cond="good", avail="lend", contact="Stephan (CEA)", budget="dream",
         note="Lent for n_TOF 2026, liability ~€72k for the full system. The TCM busy output has no LEMO fitted yet (daq_trigger/PLAN.md §4.2)."),
    dict(id="dreamcab", name="FEU ↔ M1 cables, 2 m", qty="64", cat="readout", owner="CEA Saclay (ask)", where="(ask)", cond="good",
         avail="lend", contact="Stephan (CEA)", budget="dreamcab", note="Come with the DREAM loan (ask)."),
    # --- Scintillators
    dict(id="walls", name="SiPM walls, 20 EJ-212 bars each, + summing boards", qty="4", cat="scint", owner="INFN (bars bought by INFN Torino)",
         where="(ask)", cond="partial", avail="lend", contact="Pierfrancesco / G. Gervino", budget="sipmcomp",
         note="16 of 20 bars read per wall (ganged LEMO outputs). Pierfrancesco: usable for the LNL run (18 Nov 2026)."),
    dict(id="bars_spare", name="EJ-212 spare bars 3 × 26 × 500 mm", qty="8", cat="scint", owner="INFN Torino", where="(ask)", cond="good",
         avail="lend", contact="G. Gervino", budget="", note="TNE 00412/2025: 88 bought = 80 + 8 spares."),
    dict(id="plast_small", name="Plastic scintillators 20 × 30 × 2 cm", qty="8", cat="scint", owner="(ask) lender", where="(ask)", cond="good",
         avail="lend", contact="Pierfrancesco", budget="plastics", note="Two per arm at n_TOF. Available again for LNL (Pierfrancesco)."),
    dict(id="pmt_small", name="PMTs for the small plastics", qty="8", cat="scint", owner="(ask) lender", where="back with the lender",
         cond="good", avail="returned", contact="Pierfrancesco", budget="plastics", note="Went back after n_TOF; must be found again."),
    dict(id="ls", name="Liquid scintillator cells 45 × 45 cm", qty="4", cat="scint", owner="(ask)", where="(ask)", cond="unknown",
         avail="ours", contact="Dylan", budget="ls", note="Unusable at n_TOF from pile-up (γ-flash); untested at low rates."),
    dict(id="adq14", name="n_TOF ADQ14 digitizers", qty="(n_TOF)", cat="daq", owner="CERN n_TOF", where="CERN n_TOF", cond="good",
         avail="stays", contact="n_TOF", budget="sipmdaq", note="Recorded the scintillators at n_TOF; they stay there."),
    # --- Trigger logic (all rented from CERN for n_TOF)
    dict(id="n1081b_cern", name="CAEN N1081B programmable logic", qty="6", cat="trigger", owner="CERN electronics pool", where="CERN pool",
         cond="good", avail="returned", contact="CERN pool", budget="n1081b", note="Rented for n_TOF; none comes with us."),
    dict(id="fifo_cern", name="Linear fan-in/fan-outs (428F)", qty="6", cat="trigger", owner="CERN electronics pool", where="CERN pool",
         cond="good", avail="returned", contact="CERN pool", budget="fifo", note="Rented for n_TOF."),
    dict(id="n93b_cern", name="CAEN N93B dual timer", qty="1", cat="trigger", owner="CERN electronics pool", where="CERN pool",
         cond="good", avail="returned", contact="CERN pool", budget="gate", note="Rented for n_TOF."),
    # --- Power
    dict(id="hv_ntof", name="CAEN HV mainframe (MM, PMTs)", qty="1", cat="power", owner="(ask) CERN / n_TOF", where="CERN n_TOF", cond="good",
         avail="stays", contact="n_TOF", budget="hvmm", note="Driven by our caen_hv_py at n_TOF."),
    # --- DAQ computing
    dict(id="daqpc", name="DAQ PC (DREAM + run control)", qty="1", cat="daq", owner="CEA Saclay", where="(ask)", cond="good",
         avail="lend", contact="Stephan (CEA)", budget="daqpc", note="Not Dylan's: borrow it from CEA for each run (Dylan, 19 Nov 2026)."),
    dict(id="switch", name="Network switch", qty="1", cat="daq", owner="Dylan", where="with Dylan", cond="good", avail="ours",
         contact="Dylan", budget="", note="Dylan's own (19 Nov 2026)."),
    # --- Target
    dict(id="cu_hemi", name="Cu hemisphere target holder (beam-line end)", qty="1", cat="target", owner="INFN LNL", where="LNL",
         cond="good", avail="lend", contact="Pierfrancesco", budget="chamber",
         note="Already built (Dylan, 19 Nov 2026); the 'Cu ogive' of the Geant4 study (lnl/FEASIBILITY_SIM.md §19.3)."),
]

AVAIL = dict(ours="ours to take", lend="lent on request", returned="returned, ask again", stays="stays at its facility")


def by_id() -> dict[str, dict]:
    ids = [a["id"] for a in ASSETS]
    assert len(ids) == len(set(ids)), "duplicate inventory id"
    return {a["id"]: a for a in ASSETS}


def main() -> None:
    by_id()
    out = HERE / "out"; out.mkdir(exist_ok=True)
    (out / "inventory.json").write_text(json.dumps(dict(updated=UPDATED, cats=CATS, avail=AVAIL, assets=ASSETS), ensure_ascii=False, indent=1))
    lines = [f"# MX17 hardware inventory (generated from `inventory.py`, {UPDATED})", "",
             "What exists, who owns it, where it is and whether a run may take it. Edit `inventory.py`, then rerun it.", ""]
    for c, cn in CATS.items():
        rows = [a for a in ASSETS if a["cat"] == c]
        if not rows:
            continue
        lines += [f"## {cn}", "", "| id | item | qty | owner | where | condition | availability | contact | note |",
                  "|---|---|---|---|---|---|---|---|---|"]
        lines += [f"| `{a['id']}` | {a['name']} | {a['qty']} | {a['owner']} | {a['where']} | {a['cond']} | {AVAIL[a['avail']]} | "
                  f"{a['contact']} | {a['note']} |" for a in rows]
        lines.append("")
    (HERE / "INVENTORY.md").write_text("\n".join(lines))
    n = {k: sum(a["avail"] == k for a in ASSETS) for k in AVAIL}
    print(f"{len(ASSETS)} assets: " + ", ".join(f"{v} {AVAIL[k]}" for k, v in n.items()))


if __name__ == "__main__":
    main()
