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
          lend       owner lends it on request (ask each time); a pool item goes back into the owner's pool after a run
          held       the owner keeps it set aside for MX17 (at the owner's site); tell them before taking it
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

UPDATED = "2026-11-25"
HERE = Path(__file__).resolve().parent

CATS = dict(mm="Micromegas", readout="Micromegas readout", scint="Scintillators", trigger="Trigger logic and cables",
            daq="DAQ computing", power="Power", gas="Gas", target="Target", site="Site and mechanics")

ASSETS = [
    # --- Micromegas (budget/items.py MM_STATUS holds the bench numbers)
    dict(id="mmA", name="Micromegas A (det3)", qty="1", cat="mm", owner="MX17 collaboration", where="CEA Saclay", cond="good",
         avail="ours", contact="Dylan", budget="windows",
         note="Best chamber: 92.9 % within 5 mm on the cosmic bench. Bulked by Stephan (CEA), 15 Jun 2026."),
    dict(id="mmB", name="Micromegas B (det2)", qty="1", cat="mm", owner="MX17 collaboration", where="CEA Saclay", cond="fix",
         avail="ours", contact="Dylan / Stephan (CEA)", budget="driftfix",
         note="91.3 % on the bench. Drift needs a repair, likely just an electrical connection (Dylan, 19 Nov 2026)."),
    dict(id="mmC", name="Micromegas C (det6)", qty="1", cat="mm", owner="MX17 collaboration", where="CEA Saclay", cond="rebulk",
         avail="ours", contact="Dylan / CEA", budget="rebulk", note="57.8 % within 5 mm, spark-limited; needs re-bulking at CEA."),
    dict(id="mmD", name="Micromegas D (det7)", qty="1", cat="mm", owner="MX17 collaboration", where="CEA Saclay", cond="rebulk",
         avail="ours", contact="Dylan / CEA", budget="rebulk", note="43.1 % within 5 mm; ~130 of 512 X channels dead. Needs re-bulking."),
    dict(id="mmE", name="Micromegas E (det4)", qty="1", cat="mm", owner="MX17 collaboration", where="CEA Saclay", cond="partial",
         avail="ours", contact="Dylan / CEA", budget="rebulk",
         note="62 % of the area does not amplify, in fixed stripes along X; the rest is a normal chamber (77 % efficient). Ran in the "
              "banco/P2 DREAM crate at the SPS, Jul 2026 (nTof_x17/mx_june_cosmic_qa/det4_sps_assessment/DET4_SPS_ASSESSMENT.md). "
              "All five chambers A–E are at CEA Saclay (Dylan, 25 Nov 2026)."),
    # --- Micromegas readout
    dict(id="m1cern", name="M1 multiplex cards, good (CERN design)", qty="4", cat="readout", owner="MX17 collaboration (ask)", where="CEA Saclay",
         cond="good", avail="ours", contact="Dylan", budget="m1", note="The clean cards; ran on A at n_TOF. 4 good M1 cards at CEA (Dylan, 25 Nov 2026)."),
    dict(id="m1ital", name="M1 multiplex cards, bad (Italian)", qty="20", cat="readout", owner="MX17 collaboration (ask)", where="CEA Saclay",
         cond="partial", avail="ours", contact="Dylan", budget="m1",
         note="Noisy at n_TOF (B, C, D) and on E; replacing them is budget item m1. 20 bad M1 cards at CEA (Dylan, 25 Nov 2026; was counted as 12)."),
    dict(id="m4card", name="M4 cards", qty="4", cat="readout", owner="MX17 collaboration (ask)", where="CEA Saclay", cond="unknown",
         avail="ours", contact="Dylan", budget="", note="At CEA (Dylan, 25 Nov 2026). Role and condition to write down (ask)."),
    dict(id="m2card", name="M2 cards", qty="16", cat="readout", owner="MX17 collaboration (ask)", where="CEA Saclay", cond="unknown",
         avail="ours", contact="Dylan", budget="", note="At CEA (Dylan, 25 Nov 2026). Role and condition to write down (ask)."),
    dict(id="dream", name="DREAM DAQ core: TCM + network card + large NIM module", qty="1 TCM, 1 network card, 1 NIM module", cat="readout",
         owner="CEA Saclay", where="CEA Saclay", cond="good", avail="held", contact="Stephan (CEA)", budget="dream",
         note="Kept for MX17 at CEA (Dylan, 25 Nov 2026). The FEUs and the cables are separate (dream_feu, dreamcab). Is the large NIM "
              "module the NIM bin that the budget counts on with DREAM (ask)? Liability ~€72k for the full n_TOF system. The TCM busy "
              "output has no LEMO fitted yet (daq_trigger/PLAN.md §4.2)."),
    dict(id="dream_feu", name="DREAM FEUs", qty="8 used at n_TOF", cat="readout", owner="CEA Saclay", where="CEA Saclay (common pool)",
         cond="good", avail="lend", contact="Stephan (CEA)", budget="dream",
         note="Back in CEA's common pool after n_TOF (Dylan, 25 Nov 2026): ask for them for each run."),
    dict(id="dreamcab", name="FEU ↔ M1 cables, 2 m", qty="64 used at n_TOF", cat="readout", owner="CEA Saclay", where="CEA Saclay (common pool)",
         cond="good", avail="lend", contact="Stephan (CEA)", budget="dreamcab",
         note="Back in CEA's common pool with the FEUs (Dylan, 25 Nov 2026): ask for them for each run."),
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
         avail="ours", contact="Pierfrancesco", budget="ls", note="Unusable at n_TOF from pile-up (γ-flash); untested at low rates. PF (20 Nov 2026): the liquid is there (~60 L, ask), the cans must be remade, PMTs are short."),
    dict(id="adq14", name="n_TOF ADQ14 digitizers", qty="(n_TOF)", cat="daq", owner="CERN n_TOF", where="CERN n_TOF", cond="good",
         avail="stays", contact="n_TOF", budget="sipmdaq", note="Recorded the scintillators at n_TOF; they stay there."),
    # --- Trigger logic (all rented from CERN for n_TOF)
    dict(id="n1081b_cern", name="CAEN N1081B programmable logic", qty="6", cat="trigger", owner="CERN electronics pool", where="CERN pool",
         cond="good", avail="returned", contact="CERN pool", budget="n1081b", note="Rented for n_TOF; none comes with us. Dylan's rentals (CERN epool, read 25 Nov 2026): CEP-05940009 and CEP-05940016, 30 Jun–13 Aug 2026. Pool catalogue CEP-0594: 70.30 CHF/month, SPECIAL support category, 5 in stock."),
    dict(id="fifo_cern", name="Linear fan-in/fan-outs (428F)", qty="6", cat="trigger", owner="CERN electronics pool", where="CERN pool",
         cond="good", avail="returned", contact="CERN pool", budget="fifo", note="Rented for n_TOF. Dylan's rentals (CERN epool, 25 Nov 2026): 7 × LeCroy 428F (CEP-45460169, -207, -217, -227, -246, -313, -346) and 1 × LeCroy 628 (CEP-49000002), 30 Jun–13 Aug 2026; one 428F returned on 7 Jul. Pool catalogue: 428F CEP-4546 14.76 CHF/month, 16 in stock; 628 CEP-4900 1.08 CHF/month, none in stock."),
    dict(id="n93b_cern", name="CAEN N93B dual timer", qty="1", cat="trigger", owner="CERN electronics pool", where="CERN pool",
         cond="good", avail="returned", contact="CERN pool", budget="gate", note="Rented for n_TOF: CEP-48690173, 30 Jun–13 Aug 2026 (CERN epool, 25 Nov 2026). Pool catalogue CEP-4869 14.96 CHF/month, 19 in stock."),
    # --- Cables and connectors (n_TOF's own)
    dict(id="lemo_ntof", name="LEMO 00 coax cables, by delay", qty="~60 × 16 ns, ~60 × 5 ns, ~20 × 2 ns, ~20 × 1 ns", cat="trigger",
         owner="CERN n_TOF", where="CERN n_TOF", cond="good", avail="lend", contact="n_TOF", budget="splitters",
         note="The cables of the 2026 set-up. The lengths are Dylan's estimate (25 Nov 2026), not a count. They agree with the "
              "connections in use: ~120 N1081B inputs and outputs (nTof_x17_DAQ/n1081b/n1081b_module_map.py) plus the wall, "
              "plastic and FIFO links, ~150 in all (budget/items.py splitters). At ~5 ns/m: 16 ns ≈ 3.2 m, 5 ns ≈ 1 m, "
              "2 ns ≈ 40 cm, 1 ns ≈ 20 cm. n_TOF lends them if we return them (Dylan, 25 Nov 2026)."),
    dict(id="lemo_t_ntof", name="LEMO T connectors and small adapters", qty="~30 Ts (+ adapters: count)", cat="trigger",
         owner="CERN n_TOF", where="CERN n_TOF", cond="good", avail="lend", contact="n_TOF", budget="splitters",
         note="Dylan's estimate (25 Nov 2026). Lent with the cables, to be returned."),
    # --- Power
    dict(id="lv_dream", name="Wiener PL512 LV supply (DREAM FEUs + TCM)", qty="1", cat="power", owner="CERN electronics pool (ask)",
         where="(ask)", cond="good", avail="returned", contact="CERN pool", budget="lvfeu",
         note="The low-voltage supply that powered DREAM at n_TOF (read by nTof_x17_DAQ/weiner_ps_monitor.py; model to confirm). "
              "To rent again from CERN and take to LNL, as the NIM modules (Dylan, 25 Nov 2026). The CERN pool catalogue has no Wiener PL512 (epool, 25 Nov 2026), so the PL512 may not be a pool item (ask). Dylan's epool history has a Delta Elektronika SM3545-D (0–35 V, 45 A; CEP-01270008) rented 25 Mar–13 Aug 2026 on budget code T299563 and a TTi TSX3510P (35 V, 10 A) 30 Jun–17 Jul; the SM3545-D may be the DREAM supply (ask). Catalogue CEP-0127: 24.88 CHF/month, 3 in stock."),
    dict(id="hv_ntof", name="CAEN HV mainframe (MM, PMTs)", qty="1", cat="power", owner="(ask) CERN / n_TOF", where="CERN n_TOF", cond="good",
         avail="stays", contact="n_TOF", budget="hvmm", note="Driven by our caen_hv_py at n_TOF."),
    # --- DAQ computing
    dict(id="daqpc", name="DAQ PC (DREAM + run control)", qty="1", cat="daq", owner="CEA Saclay", where="CEA Saclay", cond="good",
         avail="held", contact="Stephan (CEA)", budget="daqpc",
         note="Not Dylan's (19 Nov 2026); kept for MX17 at CEA with the DREAM core (Dylan, 25 Nov 2026)."),
    dict(id="switch", name="Network switch", qty="1", cat="daq", owner="Dylan", where="with Dylan", cond="good", avail="ours",
         contact="Dylan", budget="", note="Dylan's own (19 Nov 2026)."),
    # --- Target
    dict(id="cu_hemi", name="Cu hemisphere target holder (beam-line end)", qty="1", cat="target", owner="INFN LNL", where="LNL",
         cond="good", avail="lend", contact="Pierfrancesco", budget="chamber",
         note="Already built (Dylan, 19 Nov 2026); the 'Cu ogive' of the Geant4 study (lnl/FEASIBILITY_SIM.md §19.3)."),
]

AVAIL = dict(ours="ours to take", held="held for MX17 by its owner", lend="lent on request", returned="returned, ask again",
             stays="stays at its facility")


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
