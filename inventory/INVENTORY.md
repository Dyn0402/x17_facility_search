# MX17 hardware inventory (generated from `inventory.py`, 2026-11-25)

What exists, who owns it, where it is and whether a run may take it. Edit `inventory.py`, then rerun it.

## Micromegas

| id | item | qty | owner | where | condition | availability | contact | note |
|---|---|---|---|---|---|---|---|---|
| `mmA` | Micromegas A (det3) | 1 | MX17 collaboration | CEA Saclay | good | ours to take | Dylan | Best chamber: 92.9 % within 5 mm on the cosmic bench. Bulked by Stephan (CEA), 15 Jun 2026. |
| `mmB` | Micromegas B (det2) | 1 | MX17 collaboration | CEA Saclay | fix | ours to take | Dylan / Stephan (CEA) | 91.3 % on the bench. Drift needs a repair, likely just an electrical connection (Dylan, 19 Nov 2026). |
| `mmC` | Micromegas C (det6) | 1 | MX17 collaboration | CEA Saclay | rebulk | ours to take | Dylan / CEA | 57.8 % within 5 mm, spark-limited; needs re-bulking at CEA. |
| `mmD` | Micromegas D (det7) | 1 | MX17 collaboration | CEA Saclay | rebulk | ours to take | Dylan / CEA | 43.1 % within 5 mm; ~130 of 512 X channels dead. Needs re-bulking. |
| `mmE` | Micromegas E (det4) | 1 | MX17 collaboration | CEA Saclay | partial | ours to take | Dylan / CEA | 62 % of the area does not amplify, in fixed stripes along X; the rest is a normal chamber (77 % efficient). Ran in the banco/P2 DREAM crate at the SPS, Jul 2026 (nTof_x17/mx_june_cosmic_qa/det4_sps_assessment/DET4_SPS_ASSESSMENT.md). All five chambers A–E are at CEA Saclay (Dylan, 25 Nov 2026). |

## Micromegas readout

| id | item | qty | owner | where | condition | availability | contact | note |
|---|---|---|---|---|---|---|---|---|
| `m1cern` | M1 multiplex cards, good (CERN design) | 4 | MX17 collaboration (ask) | CEA Saclay | good | ours to take | Dylan | The clean cards; ran on A at n_TOF. 4 good M1 cards at CEA (Dylan, 25 Nov 2026). |
| `m1ital` | M1 multiplex cards, bad (Italian) | 20 | MX17 collaboration (ask) | CEA Saclay | partial | ours to take | Dylan | Noisy at n_TOF (B, C, D) and on E; replacing them is budget item m1. 20 bad M1 cards at CEA (Dylan, 25 Nov 2026; was counted as 12). |
| `m4card` | M4 cards | 4 | MX17 collaboration (ask) | CEA Saclay | unknown | ours to take | Dylan | At CEA (Dylan, 25 Nov 2026). Role and condition to write down (ask). |
| `m2card` | M2 cards | 16 | MX17 collaboration (ask) | CEA Saclay | unknown | ours to take | Dylan | At CEA (Dylan, 25 Nov 2026). Role and condition to write down (ask). |
| `dream` | DREAM DAQ core: TCM + network card + large NIM module | 1 TCM, 1 network card, 1 NIM module | CEA Saclay | CEA Saclay | good | held for MX17 by its owner | Stephan (CEA) | Kept for MX17 at CEA (Dylan, 25 Nov 2026). The FEUs and the cables are separate (dream_feu, dreamcab). Is the large NIM module the NIM bin that the budget counts on with DREAM (ask)? Liability ~€72k for the full n_TOF system. The TCM busy output has no LEMO fitted yet (daq_trigger/PLAN.md §4.2). |
| `dream_feu` | DREAM FEUs | 8 used at n_TOF | CEA Saclay | CEA Saclay (common pool) | good | lent on request | Stephan (CEA) | Back in CEA's common pool after n_TOF (Dylan, 25 Nov 2026): ask for them for each run. |
| `dreamcab` | FEU ↔ M1 cables, 2 m | 64 used at n_TOF | CEA Saclay | CEA Saclay (common pool) | good | lent on request | Stephan (CEA) | Back in CEA's common pool with the FEUs (Dylan, 25 Nov 2026): ask for them for each run. |

## Scintillators

| id | item | qty | owner | where | condition | availability | contact | note |
|---|---|---|---|---|---|---|---|---|
| `walls` | SiPM walls, 20 EJ-212 bars each, + summing boards | 4 | INFN (bars bought by INFN Torino) | (ask) | partial | lent on request | Pierfrancesco / G. Gervino | 16 of 20 bars read per wall (ganged LEMO outputs). Pierfrancesco: usable for the LNL run (18 Nov 2026). |
| `bars_spare` | EJ-212 spare bars 3 × 26 × 500 mm | 8 | INFN Torino | (ask) | good | lent on request | G. Gervino | TNE 00412/2025: 88 bought = 80 + 8 spares. |
| `plast_small` | Plastic scintillators 20 × 30 × 2 cm | 8 | (ask) lender | (ask) | good | lent on request | Pierfrancesco | Two per arm at n_TOF. Available again for LNL (Pierfrancesco). |
| `pmt_small` | PMTs for the small plastics | 8 | (ask) lender | back with the lender | good | returned, ask again | Pierfrancesco | Went back after n_TOF; must be found again. |
| `ls` | Liquid scintillator cells 45 × 45 cm | 4 | (ask) | (ask) | unknown | ours to take | Pierfrancesco | Unusable at n_TOF from pile-up (γ-flash); untested at low rates. PF (20 Nov 2026): the liquid is there (~60 L, ask), the cans must be remade, PMTs are short. |

## Trigger logic and cables

| id | item | qty | owner | where | condition | availability | contact | note |
|---|---|---|---|---|---|---|---|---|
| `n1081b_cern` | CAEN N1081B programmable logic | 6 | CERN electronics pool | CERN pool | good | returned, ask again | CERN pool | Rented for n_TOF; none comes with us. Dylan's rentals (CERN epool, read 25 Nov 2026): CEP-05940009 and CEP-05940016, 30 Jun–13 Aug 2026. Pool catalogue CEP-0594: 70.30 CHF/month, SPECIAL support category, 5 in stock. |
| `fifo_cern` | Linear fan-in/fan-outs (428F) | 6 | CERN electronics pool | CERN pool | good | returned, ask again | CERN pool | Rented for n_TOF. Dylan's rentals (CERN epool, 25 Nov 2026): 7 × LeCroy 428F (CEP-45460169, -207, -217, -227, -246, -313, -346) and 1 × LeCroy 628 (CEP-49000002), 30 Jun–13 Aug 2026; one 428F returned on 7 Jul. Pool catalogue: 428F CEP-4546 14.76 CHF/month, 16 in stock; 628 CEP-4900 1.08 CHF/month, none in stock. |
| `n93b_cern` | CAEN N93B dual timer | 1 | CERN electronics pool | CERN pool | good | returned, ask again | CERN pool | Rented for n_TOF: CEP-48690173, 30 Jun–13 Aug 2026 (CERN epool, 25 Nov 2026). Pool catalogue CEP-4869 14.96 CHF/month, 19 in stock. |
| `lemo_ntof` | LEMO 00 coax cables, by delay | ~60 × 16 ns, ~60 × 5 ns, ~20 × 2 ns, ~20 × 1 ns | CERN n_TOF | CERN n_TOF | good | lent on request | n_TOF | The cables of the 2026 set-up. The lengths are Dylan's estimate (25 Nov 2026), not a count. They agree with the connections in use: ~120 N1081B inputs and outputs (nTof_x17_DAQ/n1081b/n1081b_module_map.py) plus the wall, plastic and FIFO links, ~150 in all (budget/items.py splitters). At ~5 ns/m: 16 ns ≈ 3.2 m, 5 ns ≈ 1 m, 2 ns ≈ 40 cm, 1 ns ≈ 20 cm. n_TOF lends them if we return them (Dylan, 25 Nov 2026). |
| `lemo_t_ntof` | LEMO T connectors and small adapters | ~30 Ts (+ adapters: count) | CERN n_TOF | CERN n_TOF | good | lent on request | n_TOF | Dylan's estimate (25 Nov 2026). Lent with the cables, to be returned. |

## DAQ computing

| id | item | qty | owner | where | condition | availability | contact | note |
|---|---|---|---|---|---|---|---|---|
| `adq14` | n_TOF ADQ14 digitizers | (n_TOF) | CERN n_TOF | CERN n_TOF | good | stays at its facility | n_TOF | Recorded the scintillators at n_TOF; they stay there. |
| `daqpc` | DAQ PC (DREAM + run control) | 1 | CEA Saclay | CEA Saclay | good | held for MX17 by its owner | Stephan (CEA) | Not Dylan's (19 Nov 2026); kept for MX17 at CEA with the DREAM core (Dylan, 25 Nov 2026). |
| `switch` | Network switch | 1 | Dylan | with Dylan | good | ours to take | Dylan | Dylan's own (19 Nov 2026). |

## Power

| id | item | qty | owner | where | condition | availability | contact | note |
|---|---|---|---|---|---|---|---|---|
| `lv_dream` | Delta Elektronika SM3545-D LV supply, 0–35 V / 45 A (DREAM FEUs + TCM) | 1 | CERN electronics pool | CERN pool | good | returned, ask again | CERN pool | The low-voltage supply that powered DREAM at n_TOF (Dylan, 25 Nov 2026): CEP-01270008, rented 25 Mar–13 Aug 2026 (CERN epool). To rent again and take to LNL with the NIM modules. Catalogue CEP-0127: 24.88 CHF/month, 3 in stock (epool, 25 Nov 2026). Not the Wiener PL512 assumed before. |
| `hv_ntof` | CAEN HV mainframe (MM, PMTs) | 1 | (ask) CERN / n_TOF | CERN n_TOF | good | stays at its facility | n_TOF | Driven by our caen_hv_py at n_TOF. |

## Target

| id | item | qty | owner | where | condition | availability | contact | note |
|---|---|---|---|---|---|---|---|---|
| `cu_hemi` | Cu hemisphere target holder (beam-line end) | 1 | INFN LNL | LNL | good | lent on request | Pierfrancesco | Already built (Dylan, 19 Nov 2026); the 'Cu ogive' of the Geant4 study (lnl/FEASIBILITY_SIM.md §19.3). |
