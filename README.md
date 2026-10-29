# x17_facility_search

Where else could the n_TOF X17 apparatus make an X17 measurement?

The MX17 setup (a ³He target, four arms of Micromegas TPCs, SiPM and plastic
trigger scintillators, and a DREAM readout) ran at CERN n_TOF in 2026 to look for
the X17 boson in n + ³He → ⁴He\* → ⁴He + e⁺e⁻. This repo asks which other neutron
facilities could host the same hardware, possibly with a new target and modest
upgrades, and how far each one could reach in X17/IPC.

The studies start analytic (Highland scattering budgets, rate scaling, published
beam data). Each one is then checked against Geant4 campaigns of the full
apparatus, run on lxplus/HTCondor.

## Facilities

| facility | beam | status | where |
|---|---|---|---|
| **ILL Grenoble, PF1B** (also FIPPS) | Continuous cold reactor beam, ~10¹⁰ absorbed n/s, thermal capture at rest (E\* = 20.58 MeV) | **Most developed.** Full Geant4 campaign done. One unpolarised 50-day cycle reaches X17/IPC(M1) ≈ 1.2×10⁻² at 3σ with n_TOF hardware, Micromegas-segment cuts and a CFRP end cap. That is ~7× short of ATOMKI's ⁸Be level, and ×3–4 short even with zero background. Current work: rate walls, flight tube, window choice, polarised option. | [`ill/`](ill/README.md) |
| **LNL Legnaro, AN2000 / CN** | DC ~1 MeV protons on a thin ⁷Li film, the ATOMKI reaction ⁷Li(p,e⁺e⁻)⁸Be at the 18.15 MeV resonance; up to 1 µA (AN2000) / ~4 µA (CN, also pulsed) | **Started 2026-10-07.** Facility, reaction and targets researched; pre-Geant4 estimate: the ATOMKI ratio at 3σ in ~2 weeks at 1 µA with the n_TOF hardware (~1 week with calorimetry), IPC-limited once the MM tracks veto cosmics. LNL's own ⁸Be spectrometer already ran there in 2023–24. Next: slides, Geant4 target region. | [`lnl/`](lnl/README.md) |
| **GANIL / SPIRAL-2 NFS** (Caen) | Pulsed fast neutrons, d+Be or quasi-monoenergetic, 1–40 MeV | Plan plus a literature beam reference. The open issue is the sub-2 MeV flux the physics wants: it is unmeasured. Options include a lower deuteron energy, D(d,n), and ⁷Li(p,n) near threshold. | [`docs/PLAN_GANIL_NFS.md`](docs/PLAN_GANIL_NFS.md), [`ganil_nfs/`](ganil_nfs/README.md) |
| **NCSR Demokritos, Athens, 5.5 MV tandem** | DC ~1 µA protons at 0.8–1.0 MeV on Ti-T: the ATOMKI ⁴He reaction ³H(p,e⁺e⁻)⁴He, the same ⁴He\* as n_TOF/ILL; the lab owns Ti-T targets for ³H(p,n). Neutron beams (10⁵–10⁶ n/cm²/s) ruled out | **Started 2026-10-19.** Facility and reaction researched; pre-Geant4: 2.0×10³ X17/day into 4π at 1 µA, S/B ≈ 1 %, 3σ at ATOMKI's B_x in ~39 d as built / ~2.3 d with big plastics on a thin Cu 50 µm backing (the existing 1 mm Cu target ×3.6 slower). ATOMKI's fitted IPC is 20–45× below QED, so the first day decides. Geant4 D1–D3 running. | [`demokritos/`](demokritos/README.md) |
| **FRM II MEDAPP, Garching** | SR10 fission-converter beam, continuous, 3.2×10⁸ n/cm²/s, mean 1.9 MeV | **Dedicated study 2026-10-20**, own Geant4 beam background (soft-beam runs N5/G5/G6): **4.2×10⁻⁴ in 50 d** (big plastics), ×3.6 past ATOMKI ⁴He, ~4 d to its strength; γ-limited, beam throttled ×0.3. Reactor off since 2020, no restart date. | [`frm2_medapp/`](frm2_medapp/README.md) |
| **Birmingham HF-ADNeF** | 30 mA, 2.6–2.8 MeV protons on Li: > 3×10¹³ n/s, all ≤ 1.1 MeV, continuous | **Dedicated study 2026-10-20**, own Geant4 beam background: **3.3×10⁻⁴ in 50 d** (2.8 MeV, cell 2 m, 5 cm Pb), ×4.5 past ATOMKI, ~2.4 d; statistics-limited. Operating; needs a shielded beam port (~50 cm borated PE, estimate). | [`birmingham/`](birmingham/README.md) |
| **FRANZ, Frankfurt** | near-threshold ⁷Li(p,n), 2.0 MeV p, ≤ 20 mA DC (design), keV neutrons | **Dedicated study 2026-10-21** (soft-beam Geant4 re-weighted, duty factor): **3.3×10⁻⁴ in 50 d** at design DC, cell 0.5 m (ties Birmingham, ~2.4 d); 2.2×10⁻³ at the licence's < 5 % duty. 2 MeV beam not yet reported. | [`franz/`](franz/README.md) |
| **Cyclotron ⁹Be(p,n), NPI Řež** | TR-24 18–24 MeV / 0.3 mA on thick Be (also KURNS 30 MeV / 1 mA) | **Dedicated study 2026-10-21** (ENDF/B-VIII.0 beam model + soft-beam Geant4): **8.7×10⁻⁴ in 50 d** (18 MeV, 0°, 2 m), ~17 d; DREAM-limited by > 2.75 MeV neutrons. | [`bepn_cyclotron/`](bepn_cyclotron/README.md) |
| **LANSCE WNR, Los Alamos** | spallation white source, 1.8 µs micropulses in 2.5 %-duty macropulses | **Dedicated study 2026-10-21** (ToF 0.2–2.75 MeV, N4/N5 re-weighted): **8.4×10⁻⁴ in 50 d** at 4FP90L, 10 m, ~16 d; statistics-limited; operating, 90L beam time scarce. | [`lansce_wnr/`](lansce_wnr/README.md) |
| **Proton world survey** (60 named machines + 267-machine IAEA census) | Electrostatic, underground, metrology, BNCT, RFQ: anything giving 0.4–2.5 MeV protons on ⁷Li, ³H or ¹¹B | **2026-10-22.** LNL/Demokritos Geant4 scaled by current. **The target, not the beam, sets the reach**: ~4 µA thin, ~20 µA cooled (est.); above that every machine tests ⁸Be at 3σ in ~1.3 h (big plastics) / ~0.9 d (as built). Machines differ in the claims they reach (⁴He needs tritium; ¹²C at ~1.9 MeV is an estimate and may be fastest). **Potential: LNGS Bellotti IBF (LUNA-MV), JRC MONNET, Felsenkeller, PTB, TUNL LENA, Notre Dame 5U, iThemba.** Six labs run their own X17 experiments. | [`survey/proton/`](survey/proton/README.md) |
| **World survey** (59 rows, every class) | Cold, thermal, epithermal, pulsed white, CW fast, generators | **2026-10-20.** ILL and NFS Geant4 carried to every facility. Thermal is closed: no facility beats PF1B, because the detector walls sit below PF1B's rate. Pulsed white sources are closed by their duty factor. **Potential: FRM II MEDAPP fission beam and Birmingham HF-ADNeF (30 mA ⁷Li(p,n))**, continuous soft spectra, 2×10⁻⁴–4.6×10⁻³ in 50 d. Marginal: LANSCE WNR, D-D generators, Be(p,n) cyclotrons, BNCT epithermal. | [`survey/`](survey/README.md) |

## Layout

| directory | what it is |
|---|---|
| [`ill/`](ill/README.md) | ILL feasibility: facility record (`FACILITY.md`), analytic projection (`ill_rates.py`), the Geant4 answer (`FEASIBILITY_SIM.md`), polarised option (`POLARISED.md`), lxplus drivers (`sim/lxplus/`), slide deck (`deck/build_deck.py`) |
| [`lnl/`](lnl/README.md) | LNL feasibility for the ⁸Be search: facility (`FACILITY.md`), reaction (`PHYSICS.md`), lithium targets (`TARGETS.md`), the rate/acceptance/reach model (`lnl_rates.py` → `ESTIMATES.md`), and the Geant4 plan (`GEANT_PREP.md`) |
| [`demokritos/`](demokritos/README.md) | Demokritos feasibility for the ⁴He search: facility (`FACILITY.md`), reaction and ATOMKI ⁴He (`PHYSICS.md`), the yield/acceptance/reach model calibrated on LNL Geant4 (`demokritos_rates.py` → `ESTIMATES.md`), and the Geant4 campaign (`GEANT_PREP.md`, `sim/`) |
| [`frm2_medapp/`](frm2_medapp/README.md) | FRM II fission beam: facility (`FACILITY.md`), beam model (`medapp_beam.py`), reach (`FEASIBILITY.md`), slides (`deck/`) |
| [`birmingham/`](birmingham/README.md) | Birmingham HF-ADNeF: facility (`FACILITY.md`), ⁷Li(p,n) source and shield estimate (`bham_beam.py`), reach (`FEASIBILITY.md`), slides (`deck/`) |
| [`franz/`](franz/README.md) | FRANZ: facility, near-threshold ⁷Li(p,n) beam + duty factor (`franz_beam.py`), reach (`FEASIBILITY.md`), slides (`deck/`) |
| [`bepn_cyclotron/`](bepn_cyclotron/README.md) | Cyclotron ⁹Be(p,n) (NPI Řež, KURNS): ENDF thick-Be beam model (`bepn_beam.py`), reach, slides |
| [`lansce_wnr/`](lansce_wnr/README.md) | LANSCE WNR: per-angle yield, ToF window, macropulse live time (`wnr_beam.py`), reach, slides |
| [`survey/soft_sim/`](survey/soft_sim/README.md) | Geant4 soft-beam runs (N5 neutrons, G5/G6 photons) shared by those two, and the re-weighted reach engine (`soft_reach.py`) |
| [`ganil_nfs/`](ganil_nfs/README.md) | NFS beam reference: spectra, converters, timing, backgrounds, rates for our geometry, with sources (`refs/`) and a beam model (`nfs_beam.py`) |
| `docs/` | The GANIL/NFS plan and its anchor calculations (`anchor_kinematics.py`, `anchor_numbers.py`, `anchor_vessel.py`) |
| [`survey/proton/`](survey/proton/README.md) | World survey of proton machines: reach model scaled from LNL/Demokritos (`proton_reach.py`), catalogue + IAEA census (`proton_catalogue.py`), write-up `PROTON_SURVEY.md`, sources |
| [`survey/`](survey/README.md) | World survey of neutron facilities: the yield per neutron vs E_n, the ILL-scaled thermal model, the NFS-scaled fast model, the catalogue with verdicts (`SURVEY.md`) |
| [`trigger_scint/`](trigger_scint/README.md) | Facility-independent: fixing the trigger-scintillator acceptance. The as-built stack accepts 2.3 % of X17 pairs; four ~75 cm plastics give ~14 %. Includes big-slab backgrounds at the ILL. |
| [`daq_trigger/`](daq_trigger/README.md) | Facility-independent: the trigger and DAQ plan for a run away from n_TOF (DREAM borrowed, everything else new). Keeps the n_TOF N1081B logic plus a SCALER prescaler, a 350 µs busy lock (DREAM has no busy out) and a trigger word; active split (N979) vs a digitizer-formed trigger; scintillator digitizers; remote power (switched PDUs, DT1081B); bench tests, contingencies, costs (`PLAN.md`, `daq_plan.py`). |
| [`he4_bag/`](he4_bag/README.md) | A ⁴He bag / flight tube against air ¹⁴N, and the ³He-tight cell skin (12 µm PET + 6–7 µm Al) |
| `vessel_design/` | Parametric CAD of the 1 bar mylar-wrap, carbon-rod-cage ³He cell (STEP/STL/FreeCAD in `out/`) |
| `3he_material_budget/` | Early Highland material-budget script for the ³He target |
| [`funding/`](funding/README.md) | External funding: who in the group can apply for which EU, Italian and US scheme, and when (`OPTIONS.md`) |
| `HANDOFF.md` | Running session handoffs, newest first: what is in flight on lxplus and the next steps |

## Running

Python 3 with numpy, pandas and matplotlib. The repo has no venv of its own; use
the nTof_x17 one:

```bash
~/PycharmProjects/nTof_x17/.venv/Scripts/python.exe ill/ill_rates.py --write   # Windows
~/PycharmProjects/nTof_x17/.venv/bin/python        ill/ill_rates.py --write   # Linux
```

Each subdirectory README lists its commands and outputs. Geant4 runs only on
lxplus (see `CLAUDE.md` for paths). The small analysis outputs are copied back
into `*/sim/` and `*/out/`; the full outputs stay on EOS.

## Related repositories

- **`MX17_Full_Geant`** (GitHub `Dyn0402/MX17_Full_Geant`, `~/CLionProjects/`):
  the full Geant4 simulation of the n_TOF apparatus. The `ill` and
  `trigger_plastics` branches carry the facility-search geometry.
- **`MX17_Geant`** (`~/CLionProjects/MX17_Geant`): the Micromegas module Geant4
  sim and the one shared module geometry (`shared/MX17ModuleGeometry.hh`).
- **`nTof_x17`** (`~/PycharmProjects/nTof_x17`): the n_TOF data analysis, the fast
  MC and the measured detector response.
- **`nTof_x17_DAQ`**: DREAM DAQ characterisation (dead time, rate limits).
- **`dylan-cern-site`**: publishes the notes and decks
  (`dylan-neff.web.cern.ch/notes/`).
