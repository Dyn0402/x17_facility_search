#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
items.py -- the MX17 hardware budget for a run away from n_TOF (LNL as the case).

    python budget/build_budget.py      # items.py -> budget/out/budget.html

This file is the single source of the numbers on the budget page. Edit an item
here, rebuild, recopy to the site (see budget/README.md).

Every item has one or more OPTIONS (borrow / buy variants). Each option has a
cost (low, central, high) in EUR, 2026, before VAT, no labour, and a confidence:

  confirmed  settled (e.g. a loan already agreed)
  quote    a quote or invoice we hold
  catalog  a public catalogue / distributor price was found (source given)
  model    the budgetary model in trigger_scint/costs.py (deck numbers)
  dylan    Dylan's own figure, to be checked
  guess    my estimate, no public price (CAEN, iseg, Wiener quote on request)
  unknown  no number yet

PRESETS pick one option per item:
  lean      borrow everything that can be borrowed; buy only what can't be
  self      self-sufficient: buy everything except the DREAM DAQ
  upgrade   self-sufficient + the big plastics and the full SiPM readout

Priorities:
  1 critical   no run without it
  2 needed     the run is degraded or risky without it
  3 upgrade    buys physics reach (X17/day, background rejection)
  4 optional   unproven or nice to have
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "trigger_scint"))
import costs as CO  # noqa: E402

UPDATED = "2026-10-27"

# Collaborator comments: the page's buttons POST to a Google Apps Script web app (feedback_apps_script.gs, bound to
# the Google Sheet below), which appends each comment to that sheet's "Comments" tab; the page GETs them back.
# Empty endpoint = comment buttons hidden.
FEEDBACK_SHEET = "https://docs.google.com/spreadsheets/d/1ruV_J7cC5FnxiLDSF9arRIFDGfyGPwVTUNxzKT8tqFE/edit"
FEEDBACK_ENDPOINT = "https://script.google.com/macros/s/AKfycby6urhEQy27p2JtRg2o4W60exJZgpk1ALF-YGcUrHJQE2rBKHbfvmI3SJwzo_kET3Gt/exec"   # the Apps Script /exec URL, after deploying


def _r(x, step=100):
    return int(round(x / step) * step)


def slabs(n, W, L, T, pmt, n_pmt, material, parts=("scint", "guides", "mech", "pmts")):
    """n slabs from costs.slab_cost, without HV and digitizer (separate items here)."""
    return tuple(_r(n * sum(CO.slab_cost(W, L, T, pmt, n_pmt, material, k)[p] for p in parts)) for k in range(3))


def times(n, c):
    return tuple(_r(n * v) for v in c)


FERS = CO.DAQ[[k for k in CO.DAQ if k.startswith("160 ch: FERS")][0]]
PETSYS = CO.DAQ[[k for k in CO.DAQ if k.startswith("160 ch: PETsys")][0]]
V1742_GANG = CO.DAQ[[k for k in CO.DAQ if k.startswith("ganged")][0]]
V1742_5 = CO.DAQ[[k for k in CO.DAQ if k.startswith("160 ch: 5x V1742")][0]]
VX2745 = CO.DAQ[[k for k in CO.DAQ if k.startswith("160 ch: 3x VX2745")][0]]

# unit guesses for quote-only electronics (no public prices; see README "Sources")
N1470 = (3500, 4800, 6500)       # CAEN 4 ch reversible 8 kV / 3 mA NIM, USB
DT1471 = (2500, 3600, 5000)      # CAEN 4 ch 5.5 kV / 300 uA desktop, Ethernet
N1081B = (2500, 3500, 5000)      # CAEN programmable logic, double-width NIM
FIFO = (1500, 2200, 3000)        # quad linear fan-in/fan-out (CAEN N625 / LeCroy 428F class)
NIM_CRATE = (3000, 4000, 6000)   # 12-slot NIM bin + power supply

# Per-detector status (2026-10-16, Dylan). Bench numbers: nTof_x17/mx_june_cosmic_qa (JUNE_RESULTS_SUMMARY.md,
# engineer_package/figures/FIGURE_GUIDE.md), 2026-07-14 recipe: chi2<1 + NClus=4 telescope tracks, hit within 5 mm.
# Letter -> bench number from nTof_x17_DAQ/run_config_beam.py (alias). n_TOF dead channels: sept26_prelim_analysis/STATUS.md.
MM_STATUS = [
    dict(arm="A", det="det3", state="good", label="good",
         plan="Keep. New aluminised-mylar drift window only.",
         bulk="Bulked by Stephan, 15 June 2026.",
         bench="92.9 % within 5 mm (22.3k tracks), spatially uniform; spark 3.9 % of crossings. HV-scan peak 81 % @ 490 V.",
         ntof="Best chamber at n_TOF; its 4 M1 cards were the clean CERN ones."),
    dict(arm="B", det="det2", state="fix", label="drift fix",
         plan="Fix the drift (easy) + new window.",
         bulk="Bulked by Arnaud, 12 June 2026. Giant pillars on parts of the detector.",
         bench="91.3 % within 5 mm, uniform across the active area; spark 7.4 %. HV-scan peak 78 % @ 490 V.",
         ntof="Noisy Italian M1 cards."),
    dict(arm="C", det="det6", state="rebulk", label="re-bulk (better of the two)",
         plan="Re-bulk at CEA + new window.",
         bulk="Bulked by Stephan, ~24 June 2026; lamination redone several times; a column of waves in the mesh, maybe a spot without pillar caps.",
         bench="57.8 % within 5 mm, patchy 40–90 % with a dead line near y ≈ 10 mm; fires on ~100 % of muons, so the loss is "
               "sparks (23 % of crossings). HV-scan peak 78.8 % @ 480 V. X plane (FEU 3) shows no drift-time development.",
         ntof="Noisy Italian M1 cards."),
    dict(arm="D", det="det7", state="rebulk", label="re-bulk (worst)",
         plan="Re-bulk at CEA + new window.",
         bulk="Bulked by Stephan, 22 June 2026 (batch of 3); one or two bubbles, pillars present but without caps.",
         bench="43.1 % within 5 mm with low bands (bottom edge dark); the most spark-limited, 33 % of crossings. HV-scan peak 64.1 % @ 440 V.",
         ntof="~130 of 512 X-plane channels dead (13.9 % of the area); noisy Italian M1 cards."),
]

GROUPS = [
    dict(id="mm", name="Micromegas detectors", icon="mm", color="#1f8a7a",
         ntof="Four 40 × 36 cm Micromegas TPCs (A–D), 30 mm drift, Ar/iC₄H₁₀, bulked at CEA in June 2026.",
         blurb="A is good, B needs its drift fixed, C and D need re-bulking. All four get new aluminised-mylar drift windows."),
    dict(id="mmro", name="Micromegas readout (DREAM)", icon="board", color="#2a78d6",
         ntof="Per detector 4 M1 multiplex cards → 2 FEUs (8 FEUs, 512 ch each), 64 cables, CEA's DREAM system.",
         blurb="The noisy M1 cards are the big item. DREAM itself is a loan with a €72k liability."),
    dict(id="hv", name="High voltage", icon="hv", color="#d03b3b",
         ntof="A CAEN mainframe (slots 5/7/9) driven by our own control software: MM drift + resist, plastic PMTs.",
         blurb="8 Micromegas channels (4 + / 4 −) and 8–16 PMT channels (all −)."),
    dict(id="sipm", name="SiPM walls", icon="wall", color="#3d6fb6",
         ntof="Four walls of 20 bars; 16 read, ganged in fours, summed top/bottom, LEMO out.",
         blurb="Power, the 4 dark bars per wall, and getting from LEMO into a new DAQ."),
    dict(id="sipmdaq", name="Scintillator DAQ", icon="digi", color="#8a5cd6",
         ntof="n_TOF's own ADQ14 digitizers recorded the walls, plastics and LS. They stay at n_TOF.",
         blurb="Not optional elsewhere: we have nothing that records the scintillators."),
    dict(id="back", name="Back scintillators", icon="slab", color="#d08a1c",
         ntof="Two borrowed 20 × 30 × 2 cm plastics per arm, one PMT each (8 PMTs).",
         blurb="Borrow the small ones again, or the big plates (×7 X17/day at LNL)."),
    dict(id="ls", name="Liquid scintillators", icon="ls", color="#7a7f8c",
         ntof="One 45 × 45 cm LS cell per arm. Pile-up made them unusable.",
         blurb="Not in the plan until proven."),
    dict(id="trig", name="Trigger logic", icon="nim", color="#eb6834",
         ntof="Dozens of BNC/LEMO splits → 6 linear FIFOs (4 × 428F wall sums, 2 plastic fan-outs) → 6 × CAEN N1081B "
              "→ DREAM; N93B gate. All rented from CERN; none of it comes with us.",
         blurb="As n_TOF, plus a prescaler and trigger word for the LNL SINGLE trigger. ~€51k central in Self-sufficient (was €28k)."),
    dict(id="site", name="Integration & site", icon="truck", color="#5b6275",
         ntof="Supplied by n_TOF or CERN: mechanics, cabling, racks, computing, the beam line.",
         blurb="Things we got for free at CERN. Added by me: check what LNL provides."),
]


def opt(id, label, kind, cost, conf, note="", liability=None):
    return dict(id=id, label=label, kind=kind, cost=list(cost) if cost else None, conf=conf, note=note,
                liability=liability)


ITEMS = [
    # ------------------------------------------------------------------ Micromegas
    dict(id="rebulk", group="mm", icon="mm", priority=1, name="Re-bulk Micromegas C and D",
         qty="2 detectors (C, D)",
         ntof="C (det6) and D (det7), bulked by Stephan in June 2026, were spark-limited: bench efficiency 57.8 % and 43.1 %.",
         need="Re-laminate the mesh on C and D (D is the worse of the two). Labour by CEA; we cover materials and shipping.",
         options=[opt("cea", "CEA re-bulks C and D, we pay consumables + shipping", "buy", (1000, 3000, 5000), "dylan",
                      "Dylan: \"should be covered by CEA but expect a few thousand\".")],
         presets=dict(lean="cea", self="cea", upgrade="cea"),
         questions=["Does CEA invoice anything, or only materials? Lead time?",
                    "Re-bulk C too, or only D if time is short? C is the better of the two (57.8 % vs 43.1 % on the bench)."]),
    dict(id="driftfix", group="mm", icon="wrench", priority=1, name="Fix B's drift",
         qty="1 detector (B)",
         ntof="B (det2) ran at n_TOF; its drift needs fixing (Dylan: pretty easy).",
         need="Repair B's drift stage. B's amplification is good: 91.3 % on the bench.",
         options=[opt("fix", "Repair in house / at CEA", "buy", (0, 300, 1000), "guess")],
         presets=dict(lean="fix", self="fix", upgrade="fix"),
         questions=["What exactly is wrong with B's drift (short, leak, cathode contact)? Can it be combined with the new window?"]),
    dict(id="windows", group="mm", icon="mm", priority=2, name="New drift windows: aluminised mylar only, all four",
         qty="4 detectors",
         ntof="60 µm aluminised mylar window + a 9 µm Cu cathode on every detector.",
         need="Remake all four drift windows as aluminised mylar only, the aluminium being the cathode. Dropping the 9 µm Cu "
              "removes 0.063 % X₀ per crossing, three times the 60 µm mylar's 0.021 %. Scattering is the design driver at LNL (§15).",
         options=[opt("cea", "Remake 4 windows (mylar, frames, gluing)", "buy", (1000, 2500, 5000), "guess",
                      "Aluminised mylar is ~€100–300 per m²; most of the cost is frames, glue and labour.")],
         presets=dict(lean="cea", self="cea", upgrade="cea"),
         questions=["Who builds the windows (CEA)? Mylar thickness? Is the aluminium a good enough cathode (resistance, HV contact)?",
                    "Do it at the same time as the C/D re-bulk and B's drift fix, so each detector is opened once?"]),
    dict(id="gas", group="mm", icon="gas", priority=1, name="Gas: premixed Ar/iC₄H₁₀ bottles, regulators, flow",
         qty="~4–8 bottles + panel",
         ntof="Mixed on site from the n_TOF gas system (Ar/iC₄H₁₀; CF₄ also available). No mixer comes with us.",
         need="Assume we buy premixed argon–isobutane: bottles, 2 regulators, a 4-way flowmeter panel, bubblers.",
         options=[opt("buy", "Buy premixed Ar/iC₄H₁₀ + panel", "buy", (2000, 3500, 6000), "guess",
                      "Premix bottles ~€300–600 each (50 L), regulators ~€500 each, flowmeters/bubblers ~€1k."),
                  opt("lnl", "LNL supplies bottles and panel", "borrow", (0, 500, 1500), "guess",
                      "We may still pay for the gas itself.")],
         presets=dict(lean="buy", self="buy", upgrade="buy"),
         questions=["LNL policy on flammable gas (isobutane) and on CF₄ in the hall?",
                    "Flow rate and mix at n_TOF? How many bottles for a ~4-week run?"]),

    # ------------------------------------------------------------------ MM readout
    dict(id="m1", group="mmro", icon="board", priority=1, name="M1 multiplex cards (CERN design)",
         qty="12 minimum · 20 comfortable",
         ntof="16 in use (4 per detector). Det A had the clean CERN M1s; B/C/D had the Italian-made ones, with huge noise.",
         need="Replace the noisy cards: 12 covers B/C/D, 20 is all 16 + 4 spares.",
         options=[opt("min12", "12 cards from CERN", "buy", times(12, (1500, 2000, 2500)), "dylan",
                      "~€2k each, to be checked."),
                  opt("rec20", "20 cards from CERN", "buy", times(20, (1500, 2000, 2500)), "dylan",
                      "~€2k each, to be checked.")],
         presets=dict(lean="min12", self="rec20", upgrade="rec20"),
         questions=["Unit price from CERN (Dylan thinks ~€2k) and lead time.",
                    "Can the Italian cards be fixed (grounding / filtering) instead, or returned?"]),
    dict(id="dream", group="mmro", icon="crate", priority=1, name="DREAM DAQ (8 FEUs + trigger/clock unit)",
         qty="1 system",
         ntof="Borrowed from CEA.",
         need="Borrow again. Not a cost unless something breaks: the liability is €72k.",
         options=[opt("borrow", "Borrow from CEA", "borrow", (0, 0, 0), "dylan",
                      "€72k liability if it breaks.", liability=72000)],
         presets=dict(lean="borrow", self="borrow", upgrade="borrow"),
         questions=["Does CEA need insurance or a deposit? Does the institute's insurance cover equipment at LNL?",
                    "Are the TCM, optical fibres and the DAQ server included in the loan?"]),
    dict(id="dreamcab", group="mmro", icon="cable", priority=1, name="FEU ↔ M1 cables, 2 m",
         qty="64",
         ntof="Borrowed from CEA (8 per FEU × 8 FEUs).",
         need="64 cables, probably 2 m. CEA may not lend them again.",
         options=[opt("borrow", "Borrow from CEA again", "borrow", (0, 0, 0), "dylan"),
                  opt("buy", "Buy 64", "buy", times(64, (250, 400, 550)), "dylan",
                      "Placeholder €400 each from Dylan; to be looked up.")],
         presets=dict(lean="borrow", self="buy", upgrade="buy"),
         questions=["Cable type / connector part number and real price.",
                    "Is 2 m long enough with the LNL rack positions?"]),
    dict(id="lvfeu", group="mmro", icon="psu", priority=1, name="Low voltage, 5 V / 60 A",
         qty="1 (or 2, split by arm pair)",
         ntof="Powered the 8 FEUs (~5 A each) and the TCM (~5 A): ~45 A. The M1 cards need no power.",
         need="5 V, ≥ 45 A, so ~60 A with margin. Low noise: noise was the n_TOF problem, so no switching bricks.",
         options=[opt("borrow", "Borrow (CEA / LNL / CERN pool)", "borrow", (0, 0, 0), "guess"),
                  opt("buy", "TDK-Lambda Genesys GEN6-100/LN class (6 V / 100 A, low noise)", "buy",
                      (1500, 2200, 3200), "catalog",
                      "GEN6-200/LN lists at €2,385 ex VAT on RS Italy; the 100 A unit is smaller. Delta SM15-100 is the "
                      "alternative (~€500 used).")],
         presets=dict(lean="borrow", self="buy", upgrade="buy"),
         questions=["Does CEA lend a supply with the DREAM system? One supply, or one per arm pair to keep noise apart?"]),

    # ------------------------------------------------------------------ HV
    dict(id="hvmm", group="hv", icon="hv", priority=1, name="HV for the Micromegas",
         qty="8 ch (4 + , 4 −), ≲ 1.5 kV, µA",
         ntof="CAEN mainframe channels, driven by our control software (caen_hv_py).",
         need="8 low-current channels. Our software talks CAENHVWrapper, which also drives the N1470 and DT1471ET.",
         options=[opt("borrow", "Borrow a CAEN unit (LNL / CERN pool)", "borrow", (0, 0, 0), "guess"),
                  opt("dt1471", "2 × CAEN DT1471ET (4 ch, 5.5 kV / 300 µA, desktop)", "buy", times(2, DT1471), "guess",
                      "Polarity set per channel. Same software library. Quote on request."),
                  opt("n1470", "2 × CAEN N1470 (4 ch, 8 kV / 3 mA, NIM)", "buy", times(2, N1470), "guess",
                      "Needs a NIM bin. Quote on request."),
                  opt("sy5527", "SY5527LC mainframe + boards (what we had)", "buy", (15000, 22000, 30000), "guess",
                      "Overkill for 16–24 channels.")],
         presets=dict(lean="borrow", self="dt1471", upgrade="dt1471"),
         questions=["Exact voltages and currents per channel (drift / resist / mesh)?",
                    "Get CAEN quotes for DT1471ET and N1470 (and an iseg MPOD/EHS alternative)."]),
    dict(id="hvpmt", group="hv", icon="hv", priority=1, name="HV for the scintillator PMTs",
         qty="8 (small plastics or big plates) to 16 ch, all −, ~2 kV, mA",
         ntof="CAEN mainframe slot 7 (plastic PMTs).",
         need="8 channels for the 8 PMTs; 16 if the LS or more PMTs come back.",
         options=[opt("borrow", "Borrow (with the PMTs, or LNL pool)", "borrow", (0, 0, 0), "guess"),
                  opt("n1470x2", "2 × CAEN N1470 (8 ch)", "buy", times(2, N1470), "guess", "Quote on request."),
                  opt("n1470x4", "4 × CAEN N1470 (16 ch)", "buy", times(4, N1470), "guess", "Quote on request.")],
         presets=dict(lean="borrow", self="n1470x2", upgrade="n1470x2"),
         questions=["If the PMTs are borrowed, does their HV come with them?"]),

    # ------------------------------------------------------------------ SiPM walls
    dict(id="lvsipm", group="sipm", icon="psu", priority=1, name="SiPM bias supply for the walls, ~63 V",
         qty="1",
         ntof="~63 V bias to the walls' preamp boards (Dylan, fairly sure).",
         need="A standard lab supply. Still needed with FERS: its onboard bias (A7585D, 20–85 V, ~10 mA) only reaches SiPMs "
              "wired straight into the FERS input, and ours sit behind the wall preamp boards.",
         options=[opt("borrow", "Borrow (standard nuclear-physics model)", "borrow", (0, 0, 0), "guess"),
                  opt("ea320", "EA-PS 3080-10 C (80 V / 10 A, 320 W)", "buy", (770, 900, 1100), "catalog",
                      "€770 (Datatec) – €1,026 (RS) ex VAT. 320 W: up to ~5 A at 63 V."),
                  opt("ea1k", "1 kW class, 80 V / 20 A (EA-PS 10080-20, TDK GEN80-19)", "buy", (1500, 2200, 3000),
                      "guess", "Only if the walls really draw ~10 A.")],
         presets=dict(lean="borrow", self="ea320", upgrade="ea320"),
         questions=["Current drawn at 63 V (the 10 A guess decides between the 320 W and 1 kW units)?",
                    "Do the preamp boards need a separate low voltage too?"]),
    dict(id="sipmcomp", group="sipm", icon="wall", priority=3, name="Light the 4 dark bars per wall; un-gang the preamps",
         qty="16 bars, 32 bar-ends",
         ntof="16 of 20 bars read, ganged in groups of 4.",
         need="Reading all 20 bars: ×1.4 acceptance with the big plates (TRIGGER_OPTIONS §bottom line 3).",
         options=[opt("skip", "Keep 16 bars", "skip", (0, 0, 0), "model"),
                  opt("do", "SiPMs + preamps for 32 bar-ends, board respin", "buy", CO.SIPM_COMPLETION, "model",
                      "trigger_scint/costs.py SIPM_COMPLETION.")],
         presets=dict(lean="skip", self="skip", upgrade="do"),
         questions=["Who built the walls, and can they respin the preamp boards?"]),
    dict(id="lemo", group="sipm", icon="board", priority=1, name="LEMO → DAQ adapter boards + cables",
         qty="160 or 320 channels",
         ntof="Walls have LEMO outputs into NIM.",
         need="Any multi-channel SiPM DAQ needs an adapter (e.g. LEMO → FERS input connector) and LEMO cables.",
         options=[opt("c160", "Adapters + cables for 160 ch", "buy", (2000, 4000, 8000), "guess",
                      "Small PCB run (~€100–300/board) + ~€15–25 per LEMO cable."),
                  opt("c320", "Adapters + cables for 320 ch", "buy", (3500, 7000, 13000), "guess")],
         presets=dict(lean="c160", self="c160", upgrade="c320"),
         questions=["Can the FERS (Citiroc) take the preamplified LEMO signal, or do we bypass the preamps?",
                    "How many LEMO cables per wall, and what lengths at LNL?"]),

    # ------------------------------------------------------------------ Scintillator DAQ
    dict(id="sipmdaq", group="sipmdaq", icon="digi", priority=1, name="SiPM wall DAQ",
         qty="160 or 320 channels",
         ntof="n_TOF ADQ14s recorded 8 summed channels per wall. They stay at n_TOF.",
         need="Charge + time per bar end. Rates are low (any option keeps up); the plates carry the precise timing.",
         options=[opt("gang", "As n_TOF: ganged sums, 1 × V1742 (32 ch)", "buy", V1742_GANG, "model",
                      "Cheapest; loses bar position."),
                  opt("fers160", "FERS-5200 A5202 × 3 + DT5215 (160 ch, bias incl.)", "buy", FERS, "model",
                      "Recommended (TRIGGER_OPTIONS §5). Has trigger-OR outputs. CAEN expects to supply the "
                      "Citiroc A5202 for only 2–3 more years."),
                  opt("fers320", "FERS-5200 A5202 × 5 + DT5215 (320 ch)", "buy", tuple(_r(v * 5 / 3) for v in FERS),
                      "model", "160-ch price × 5/3."),
                  opt("petsys", "PETsys TOFPET2, 256 ch (160 ch used)", "buy", PETSYS, "model"),
                  opt("v1742", "5 × V1742 DRS4 + VME crate (160 ch, waveforms)", "buy", V1742_5, "model",
                      "~1 kHz dead time."),
                  opt("vx2745", "3 × VX2745 + crate (192 ch)", "buy", VX2745, "model", "Marginal timing.")],
         presets=dict(lean="fers160", self="fers160", upgrade="fers320"),
         questions=["160 or 320 channels: two SiPMs per bar end read separately?",
                    "Borrow option: does LNL or a collaborating group have FERS / PETsys units?",
                    "Test the Citiroc range on one wall (~31 mV per end at the MIP) before buying."]),
    dict(id="pmtdigi", group="sipmdaq", icon="digi", priority=1, name="PMT digitizer (plates + trigger sums)",
         qty="16 ch, 500 MS/s–1 GS/s",
         ntof="n_TOF ADQ14s.",
         need="Energy + time of the 8 back-scintillator PMTs (E_sum, cosmic TOF) and analog trigger sums.",
         options=[opt("borrow", "Borrow (LNL / CAEN pool)", "borrow", (0, 0, 0), "guess"),
                  opt("v1730", "1 × 16-ch V1730S-class (or 2 × DT5730)", "buy", times(16, CO.DIGI_PER_PMT_CH), "model",
                      "costs.py: €0.8k per channel share.")],
         presets=dict(lean="v1730", self="v1730", upgrade="v1730"),
         questions=["Desktop (DT5730) or VME? A VME crate + bridge adds ~€5–8k."]),

    # ------------------------------------------------------------------ Back scintillators
    dict(id="plastics", group="back", icon="slab", priority=1, name="Back scintillators (trigger leg + energy)",
         qty="4 arms",
         ntof="8 × 20 × 30 × 2 cm plastics + 8 PMTs, borrowed from a colleague in Italy. Pair trigger 2.3 % (3.3 % at LNL).",
         need="Something behind each wall to close the trigger leg. Big plates: X17/day ×7.8, 3σ in 1 day instead of 17. "
              "Build them ourselves (Pierfrancesco, 2026-10-16): buy raw plates, polish/wrap/couple in-house, buy only "
              "the light guides, borrow the PMTs. Analysis: trigger_scint/TRIGGER_OPTIONS.md §8 (2026-10-20).",
         options=[opt("borrow", "Borrow the 20 × 30 plastics + PMTs again (Italian lender)", "borrow", (0, 0, 0), "dylan"),
                  opt("buysmall", "Buy the same: 8 × 20 × 30 × 2 cm PVT, 1 × 2\" PMT each", "buy",
                      slabs(8, 20, 30, 2, '2"', 1, "PVT"), "model"),
                  opt("diy5", "Big plates, built in-house: 4 × 78 × 80 × 5 cm raw plates, bought guides, 8 borrowed PMTs", "buy",
                      CO.arms_diy(1, 78, 80, 5), "model",
                      "Pierfrancesco: ~€2k per plate from Scionix, €8k for 4, PMTs borrowed (the low end here). The range "
                      "adds 8 custom guides, wrapping, cement and light-tight housings; workshop labour in kind."),
                  opt("diy5split", "Big plates split in 2, built in-house: 8 × 39 × 80 × 5 cm, 16 PMTs (8 borrowed + 8 bought)", "buy",
                      CO.arms_diy(2, 78, 80, 5, pmts_bought_per_arm=2), "model",
                      "Halves the γ/neutron singles and in-gate pile-up per channel, ×2 the light per bar; "
                      "4 % of legs land within 1 cm of the seam (the arm sum is unaffected)."),
                  opt("diy4", "Big plates, built in-house, 4 cm thick", "buy", CO.arms_diy(1, 78, 80, 4), "model",
                      "88 % of the 5 cm calorimetry; ~20 % fewer high-energy γ singles."),
                  opt("big5ps", "Big plates finished by the vendor: 4 × 78 × 80 × 5 cm polystyrene, 2 × 3\" PMTs", "buy",
                      slabs(4, 78, 80, 5, '3"', 2, "PS"), "model", "The 2026-10-02 plan (vendor-finished, new PMTs). "
                      "The deck's ~€93k includes HV + digitizer, counted separately here."),
                  opt("big5pvt", "Big plates finished by the vendor: 4 × 78 × 80 × 5 cm cast PVT, 2 × 3\" PMTs", "buy",
                      slabs(4, 78, 80, 5, '3"', 2, "PVT"), "model")],
         presets=dict(lean="borrow", self="borrow", upgrade="diy5"),
         questions=["Pierfrancesco: is the ~€2k per plate for 78 × 80 × 5 cm, and which material (PVT EJ-200 class or polystyrene)? Get the Scionix quote in writing.",
                    "Which PMTs are the 8 borrowed ones (2\" or 3\", model)? Light per plate: 2\" gives ~half of 3\" on a 5 cm end face.",
                    "Who machines/polishes the plate edges (CERN or INFN workshop) and glues the guides?",
                    "γ sensitivity at the chosen facility: hall dose rate and spectrum (ask), and a Geant4 run with the plate split in 2.",
                    "Build and test one prototype plate on the cosmic bench before buying four."]),
    dict(id="frames", group="back", icon="wrench", priority=3, name="Arm frames for ~32 kg plates",
         qty="4",
         ntof="Frames sized for the 20 × 30 plastics.",
         need="Only with the big plates.",
         options=[opt("skip", "Not needed (small plastics)", "skip", (0, 0, 0), "guess"),
                  opt("do", "Rework the 4 arm frames", "buy", (2000, 5000, 9000), "guess")],
         presets=dict(lean="skip", self="skip", upgrade="do"),
         questions=["Who designs the frames: CEA, CERN workshop or LNL?"]),

    # ------------------------------------------------------------------ LS
    dict(id="ls", group="ls", icon="ls", priority=4, name="Liquid scintillators",
         qty="4 cells",
         ntof="4 × 45 × 45 cm, one PMT each. 67–76 % of pulses had pile-up; unusable.",
         need="Not counted on. Alone they give 1.2 % pair acceptance; their problem was rate, not hardware.",
         options=[opt("skip", "Leave them out", "skip", (0, 0, 0), "model"),
                  opt("revive", "Revival: new PMTs + bases, coupling, refill", "buy", CO.LS_REVIVAL, "model",
                      "costs.py LS_REVIVAL."),
                  opt("rebuild", "Rebuild (Pierfrancesco): new cases, TiO2 paint, 2 PMTs per cell", "buy", (5000, 7000, 10000), "collab",
                      "Pierfrancesco, 2026-10-16: \"7000 euros only for the case+16 PMT\". He recalls low signal and a strong "
                      "position dependence, not pile-up.")],
         presets=dict(lean="skip", self="skip", upgrade="skip"),
         questions=["Bench test of one cell before spending anything?",
                    "Pile-up (n_TOF data) or low light + position dependence (Pierfrancesco's memory)? Probably both."]),

    # ------------------------------------------------------------------ Trigger
    dict(id="n1081b", group="trig", icon="nim", priority=1, name="Programmable trigger logic (CAEN N1081B)",
         qty="6 (as n_TOF); 5 if the FERS forms the wall ORs",
         ntof="6 × N1081B, rented from CERN (nTof_x17_DAQ/n1081b/n1081b_module_map.py): M1 wall OR (discriminates the "
              "16 428F segment sums), M2 plastic discriminators, M3 sector AND (20 ns), M4 Singles / Doubles / veto / master "
              "trigger → DREAM TCM, M5 scalers + time tags, M6 pulser and γ-flash countermeasures (mesh injection, SiPM blanking).",
         need="The same chain: M1–M5 carry over one for one. M6's γ-flash jobs go away with a DC beam, but the 1 Hz pedestal "
              "clock, the random pulser and a spare section for a dead input (M2's D1 input died at n_TOF; M1 was offline "
              "for 3 days) still need a 6th board. A FERS that forms the per-wall OR itself saves M1. The N1081B firmware "
              "has no prescaler and its time-tag stream stops above ~50 Hz, so the prescale and the trigger word are a "
              "separate item.",
         options=[opt("borrow", "Rent from CERN again (probably no longer possible) / LNL pool", "borrow", (0, 0, 0), "dylan"),
                  opt("buy4", "Buy 4: FERS forms the wall ORs, clock from the TCM, no spare", "buy", times(4, N1081B), "guess",
                      "Quote on request. Only if the FERS can give one OR per wall (A5202 boards are 64 ch, a wall is 40 ends)."),
                  opt("buy5", "Buy 5: M1–M5 as n_TOF, clock/pulser in the TCM, no spare", "buy", times(5, N1081B), "guess",
                      "Quote on request."),
                  opt("buy6", "Buy 6 (as n_TOF): M1–M5 + clock, pulser and spare sections", "buy", times(6, N1081B), "guess",
                      "Quote on request.")],
         presets=dict(lean="buy5", self="buy6", upgrade="buy6"),
         questions=["Any chance CERN rents outside CERN, or LNL has N1081Bs in its pool?",
                    "Can the FERS give one trigger OR per wall (one A5202 per wall = 4 boards, not 3)? That saves M1.",
                    "Can the DREAM TCM generate the 1 Hz clock / random trigger itself?",
                    "CAEN quote for 6, and whether the boards ship on the current firmware (M6 was stuck on 2022.3)."]),
    dict(id="prescale", group="trig", icon="nim", priority=1, name="Prescaler + trigger word (PAIR / SINGLE 1/P)",
         qty="1 unit + spare digitizer channels",
         ntof="Not needed: DREAM took every Single. The trigger was rebuilt offline from the digitizer hits "
              "(ntof_dream_merge/dream_trigger.py); the N1081B time tags dropped out above ~50 Hz.",
         need="The LNL trigger (FEASIBILITY_SIM §14.1): PAIR never prescaled, SINGLE prescaled 1/P (P = 5–10 at 1 µA, "
              "20–50 at 4 µA; SHAPES_GEANT §0), every event tagged with which output fired and the prescale count. "
              "No N1081B function divides by N. Cheapest: a preset counter as the divide-by-P, and the PAIR, SINGLE and "
              "prescaled outputs copied into 3–4 spare channels of the PMT digitizer as the trigger word.",
         options=[opt("n1145", "Preset counter as prescaler (CAEN N1145 class) + word on spare digitizer channels", "buy",
                      (1500, 2500, 3500), "guess", "Quote on request. Uses 3–4 of the 8 free channels of the 16-ch PMT digitizer."),
                  opt("fpga", "FPGA logic unit (CAEN DT5495 / V2495 class): prescale, trigger word, busy, time stamps", "buy",
                      (5000, 8000, 12000), "guess",
                      "Unit + NIM/LVDS mezzanines; firmware written in-house (weeks). Could also absorb M3–M5 later.")],
         presets=dict(lean="n1145", self="n1145", upgrade="fpga"),
         questions=["Can any N1081B function (COUNTER_TIMER, LUT) be made to divide by N? Then this unit drops.",
                    "Does the DREAM TCM record an external trigger pattern / latch input bits per event?"],
         added=True),
    dict(id="fifo", group="trig", icon="nim", priority=1, name="Linear fan-in/fan-outs (428F / N625 class)",
         qty="6 modules (4 wall sums + 2 plastics); 8 with split plates",
         ntof="6, rented from CERN: one LeCroy 428F per wall summed the top + bottom ends of each 4-bar segment (16 sums "
              "into M1); two more fanned the 8 plastic PMTs out to the digitizer and M2 from 2026-07-17 (the BNC-T split "
              "had halved the amplitude; the FIFO gave ~2× and a cleaner pulse).",
         need="The same 6 for the as-built walls and plastics. The big 2-PMT plates keep 8 PMTs, so 2 plastic FIFOs still "
              "do; the split plates (16 PMTs) need 4. If the FERS forms the wall ORs, the 4 wall-sum FIFOs go.",
         options=[opt("borrow", "Borrow from the LNL electronics pool (CERN rental probably over)", "borrow", (0, 0, 0), "guess"),
                  opt("used", "Buy 6 used LeCroy 428F (surplus market)", "buy", times(6, (400, 700, 1200)), "guess",
                      "Surplus prices; condition and calibration unknown, so buy 7 for a spare."),
                  opt("buy2", "Buy 2 new (plastics only; FERS forms the wall ORs)", "buy", times(2, FIFO), "guess",
                      "Quote on request."),
                  opt("buy6", "Buy 6 new quad linear FIFOs (CAEN N625 class)", "buy", times(6, FIFO), "guess",
                      "Quote on request.")],
         presets=dict(lean="used", self="buy6", upgrade="buy6"),
         questions=["Does LNL have linear fan-in/fan-outs to lend?"]),
    dict(id="splitters", group="trig", icon="cable", priority=1, name="Signal splitters + trigger patch cables",
         qty="~40 splits, ~150 LEMO cables, adapters",
         ntof="Dozens of BNC-T / LEMO splitters (each wall channel to the ADQ14 and to the 428F; the plastics until "
              "2026-07-17) and the LEMO patch between the 6 N1081Bs (~100 cables); all CERN's.",
         need="Every signal that goes to both a digitizer and the trigger needs a split: the 32 ganged wall channels and "
              "spares (~40), passive 50 Ω resistive splitters rather than BNC-Ts. The patch: ~70 inputs and ~50 outputs "
              "in use across the 6 N1081Bs (module map) plus the FIFO and DAQ links, so ~150 LEMO cables of 0.5–3 m, "
              "plus LEMO↔BNC adapters. The trigger delays are set in the N1081B gate&delay, so no delay boxes.",
         options=[opt("borrow", "Borrow (LNL pool)", "borrow", (0, 0, 0), "guess"),
                  opt("buy", "40 resistive splitters + 150 LEMO cables + adapters", "buy",
                      tuple(_r(40 * a + 150 * b + c) for a, b, c in zip((10, 60, 90), (12, 20, 30), (300, 500, 1000))),
                      "guess", "Splitter €10 (home-made / BNC-T) to €60–90 (Mini-Circuits ZFRSC class); LEMO 00 cable "
                      "€12–30 made up.")],
         presets=dict(lean="buy", self="buy", upgrade="buy"),
         questions=["Does the LNL electronics pool lend LEMO cables and splitters?",
                    "With the FERS reading bar ends, where is the split: on the LEMO adapter boards (lemo item) or in front of them?"],
         added=True),
    dict(id="nimcrate", group="trig", icon="crate", priority=1, name="NIM bins (crates + power)",
         qty="3 bins: the CEA one + 2",
         ntof="n_TOF / CERN.",
         need="We own no NIM modules or bins. Slots: 6 N1081B × 2 = 12, 6 FIFOs = 6, the prescaler 1, 2–4 N1470 × 2 = 4–8: 23–27 slots, so three "
              "12-slot bins (two are full with no room for a spare). One comes with the DREAM loan from CEA.",
         options=[opt("cea", "The CEA bin only (with DREAM)", "borrow", (0, 0, 0), "dylan", "Not enough slots."),
                  opt("cea_lnl", "CEA bin + borrow 2 at LNL", "borrow", (0, 0, 0), "guess"),
                  opt("cea_buy1", "CEA bin + borrow 1 at LNL + buy 1", "buy", NIM_CRATE, "guess"),
                  opt("cea_buy", "CEA bin + buy 2", "buy", times(2, NIM_CRATE), "guess")],
         presets=dict(lean="cea_lnl", self="cea_buy", upgrade="cea_buy"),
         questions=["Can LNL lend NIM bins? Is the CEA bin a full 12-slot one with enough current for the N1081Bs?"]),
    dict(id="gate", group="trig", icon="nim", priority=4, name="Beam-gate timer (N93B)",
         qty="—",
         ntof="N93B 30 ms gate on the n_TOF PS pulse.",
         need="Not needed: the LNL beam is DC. A random/clock trigger comes from the N1081B.",
         options=[opt("skip", "Not needed at LNL", "skip", (0, 0, 0), "model")],
         presets=dict(lean="skip", self="skip", upgrade="skip"),
         questions=[]),

    # ------------------------------------------------------------------ site
    dict(id="chamber", group="site", icon="target", priority=1, name="Thin target chamber + beam pipe section",
         qty="1",
         ntof="The ³He capsule and n_TOF beam line.",
         need="A thin CFRP section ±5 cm around the target, nothing thick in the 49° cone. The design driver for scattering (§15).",
         options=[opt("lnl", "LNL builds / lends it", "borrow", None, "unknown"),
                  opt("build", "We build it (CFRP tube, flanges, holder)", "buy", (4000, 8000, 15000), "guess")],
         presets=dict(lean="lnl", self="build", upgrade="build"),
         questions=["Ask LNL: existing chambers on AN2000 / CN, and who pays for a new thin one."],
         added=True),
    dict(id="targets", group="site", icon="target", priority=1, name="Lithium targets (Li₂O / LiF films)",
         qty="~5–10 films",
         ntof="—",
         need="Li₂O 300–700 µg/cm² on a backing; spares for lifetime at 1 µA; a thin LiF for the 441 keV calibration.",
         options=[opt("lnl", "LNL target lab", "borrow", None, "unknown"),
                  opt("buy", "Buy / commission films", "buy", (1000, 3000, 6000), "guess")],
         presets=dict(lean="lnl", self="lnl", upgrade="lnl"),
         questions=["LNL target lab: cost per film, lifetime at 1 µA, ¹¹B / ¹⁹F contamination."],
         added=True),
    dict(id="daqpc", group="site", icon="pc", priority=1, name="DAQ computers + storage",
         qty="DAQ PC + disks",
         ntof="CEA's DAQ PC + CERN EOS.",
         need="The DAQ computer comes from CEA with DREAM (confirmed). Local disks, copy to EOS.",
         options=[opt("cea", "Borrow from CEA with DREAM", "borrow", (0, 0, 0), "confirmed"),
                  opt("buy", "Fallback: 1 new PC + disks", "buy", (2000, 3500, 6000), "guess")],
         presets=dict(lean="cea", self="cea", upgrade="cea"),
         questions=[]),
    dict(id="cabling", group="site", icon="cable", priority=2, name="HV, signal and network cabling",
         qty="SHV ×24, LEMO patch, Ethernet",
         ntof="Mostly CERN's.",
         need="SHV cables for 16–24 HV channels, long signal runs to the rack, a network switch. The trigger patch is in \"Signal splitters + trigger patch cables\".",
         options=[opt("borrow", "Borrow", "borrow", (0, 0, 0), "guess"),
                  opt("buy", "Buy", "buy", (1500, 3000, 5000), "guess")],
         presets=dict(lean="borrow", self="buy", upgrade="buy"),
         questions=["Does LNL supply SHV / signal cables and network in the hall? Nothing from n_TOF comes with us."]),
    dict(id="transport", group="site", icon="truck", priority=2, name="Transport CERN → LNL (and back), insurance",
         qty="1 return trip",
         ntof="—",
         need="A truck or van for the arms, electronics and racks; insurance for the DREAM loan.",
         options=[opt("buy", "Van / courier both ways", "buy", (1500, 3500, 7000), "guess")],
         presets=dict(lean="buy", self="buy", upgrade="buy"),
         questions=["Does LNL or the institute pay transport? Insurance for borrowed items?"]),
    dict(id="mech", group="site", icon="wrench", priority=2, name="Support structure and alignment",
         qty="1",
         ntof="The n_TOF stand. It stays at CERN: nothing from n_TOF comes with us.",
         need="Hold the four arms around the LNL beam line at 1.4 m beam height (or whatever it is).",
         options=[opt("new", "New stand", "buy", (4000, 8000, 15000), "guess"),
                  opt("lnl", "Adapt an LNL support / profile frame", "buy", (1500, 4000, 8000), "guess")],
         presets=dict(lean="lnl", self="new", upgrade="new"),
         questions=["Beam height and floor space at LNL? Does LNL have a frame or optical table to adapt?"], added=True),
]

PRESETS = [
    dict(id="lean", name="Lean", sub="borrow everything we can"),
    dict(id="self", name="Self-sufficient", sub="buy all but DREAM"),
    dict(id="upgrade", name="Upgrade", sub="+ big plates, 320 ch, 20 bars"),
]
