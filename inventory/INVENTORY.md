# MX17 hardware inventory (generated from `inventory.py`, 2026-11-19)

What exists, who owns it, where it is and whether a run may take it. Edit `inventory.py`, then rerun it.

## Micromegas

| id | item | qty | owner | where | condition | availability | contact | note |
|---|---|---|---|---|---|---|---|---|
| `mmA` | Micromegas A (det3) | 1 | MX17 collaboration | (ask) | good | ours to take | Dylan | Best chamber: 92.9 % within 5 mm on the cosmic bench. Bulked by Stephan (CEA), 15 Jun 2026. |
| `mmB` | Micromegas B (det2) | 1 | MX17 collaboration | (ask) | fix | ours to take | Dylan / Stephan (CEA) | 91.3 % on the bench. Drift needs a repair, likely just an electrical connection (Dylan, 19 Nov 2026). |
| `mmC` | Micromegas C (det6) | 1 | MX17 collaboration | (ask) | rebulk | ours to take | Dylan / CEA | 57.8 % within 5 mm, spark-limited; needs re-bulking at CEA. |
| `mmD` | Micromegas D (det7) | 1 | MX17 collaboration | (ask) | rebulk | ours to take | Dylan / CEA | 43.1 % within 5 mm; ~130 of 512 X channels dead. Needs re-bulking. |

## Micromegas readout

| id | item | qty | owner | where | condition | availability | contact | note |
|---|---|---|---|---|---|---|---|---|
| `m1cern` | M1 multiplex cards, CERN design | 4 | MX17 collaboration (ask) | on Micromegas A | good | ours to take | Dylan | The clean cards; ran on A at n_TOF. |
| `m1ital` | M1 multiplex cards, Italian | 12 | MX17 collaboration (ask) | on Micromegas B, C, D | partial | ours to take | Dylan | Noisy at n_TOF; replacing them is budget item m1. |
| `dream` | DREAM DAQ: FEUs + trigger/clock unit (TCM) | 8 FEUs, 1 TCM | CEA Saclay | (ask) | good | lent on request | Stephan (CEA) | Lent for n_TOF 2026, liability ~€72k for the full system. The TCM busy output has no LEMO fitted yet (daq_trigger/PLAN.md §4.2). |
| `dreamcab` | FEU ↔ M1 cables, 2 m | 64 | CEA Saclay (ask) | (ask) | good | lent on request | Stephan (CEA) | Come with the DREAM loan (ask). |

## Scintillators

| id | item | qty | owner | where | condition | availability | contact | note |
|---|---|---|---|---|---|---|---|---|
| `walls` | SiPM walls, 20 EJ-212 bars each, + summing boards | 4 | INFN (bars bought by INFN Torino) | (ask) | partial | lent on request | Pierfrancesco / G. Gervino | 16 of 20 bars read per wall (ganged LEMO outputs). Pierfrancesco: usable for the LNL run (18 Nov 2026). |
| `bars_spare` | EJ-212 spare bars 3 × 26 × 500 mm | 8 | INFN Torino | (ask) | good | lent on request | G. Gervino | TNE 00412/2025: 88 bought = 80 + 8 spares. |
| `plast_small` | Plastic scintillators 20 × 30 × 2 cm | 8 | (ask) lender | (ask) | good | lent on request | Pierfrancesco | Two per arm at n_TOF. Available again for LNL (Pierfrancesco). |
| `pmt_small` | PMTs for the small plastics | 8 | (ask) lender | back with the lender | good | returned, ask again | Pierfrancesco | Went back after n_TOF; must be found again. |
| `ls` | Liquid scintillator cells 45 × 45 cm | 4 | (ask) | (ask) | unknown | ours to take | Dylan | Unusable at n_TOF from pile-up (γ-flash); untested at low rates. |

## Trigger logic

| id | item | qty | owner | where | condition | availability | contact | note |
|---|---|---|---|---|---|---|---|---|
| `n1081b_cern` | CAEN N1081B programmable logic | 6 | CERN electronics pool | CERN pool | good | returned, ask again | CERN pool | Rented for n_TOF; none comes with us. |
| `fifo_cern` | Linear fan-in/fan-outs (428F) | 6 | CERN electronics pool | CERN pool | good | returned, ask again | CERN pool | Rented for n_TOF. |
| `n93b_cern` | CAEN N93B dual timer | 1 | CERN electronics pool | CERN pool | good | returned, ask again | CERN pool | Rented for n_TOF. |

## DAQ computing

| id | item | qty | owner | where | condition | availability | contact | note |
|---|---|---|---|---|---|---|---|---|
| `adq14` | n_TOF ADQ14 digitizers | (n_TOF) | CERN n_TOF | CERN n_TOF | good | stays at its facility | n_TOF | Recorded the scintillators at n_TOF; they stay there. |
| `daqpc` | DAQ PC (DREAM + run control) | 1 | CEA Saclay | (ask) | good | lent on request | Stephan (CEA) | Not Dylan's: borrow it from CEA for each run (Dylan, 19 Nov 2026). |
| `switch` | Network switch | 1 | Dylan | with Dylan | good | ours to take | Dylan | Dylan's own (19 Nov 2026). |

## Power

| id | item | qty | owner | where | condition | availability | contact | note |
|---|---|---|---|---|---|---|---|---|
| `hv_ntof` | CAEN HV mainframe (MM, PMTs) | 1 | (ask) CERN / n_TOF | CERN n_TOF | good | stays at its facility | n_TOF | Driven by our caen_hv_py at n_TOF. |

## Target

| id | item | qty | owner | where | condition | availability | contact | note |
|---|---|---|---|---|---|---|---|---|
| `cu_hemi` | Cu hemisphere target holder (beam-line end) | 1 | INFN LNL | LNL | good | lent on request | Pierfrancesco | Already built (Dylan, 19 Nov 2026); the 'Cu ogive' of the Geant4 study (lnl/FEASIBILITY_SIM.md §19.3). |
