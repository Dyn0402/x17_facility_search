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
| **World survey** (59 rows, every class) | Cold, thermal, epithermal, pulsed white, CW fast, generators | **2026-10-20.** ILL and NFS Geant4 carried to every facility. Thermal is closed: no facility beats PF1B, because the detector walls sit below PF1B's rate. Pulsed white sources are closed by their duty factor. **Potential: FRM II MEDAPP fission beam and Birmingham HF-ADNeF (30 mA ⁷Li(p,n))**, continuous soft spectra, 2×10⁻⁴–4.6×10⁻³ in 50 d. Marginal: LANSCE WNR, D-D generators, Be(p,n) cyclotrons, BNCT epithermal. | [`survey/`](survey/README.md) |

## Layout

| directory | what it is |
|---|---|
| [`ill/`](ill/README.md) | ILL feasibility: facility record (`FACILITY.md`), analytic projection (`ill_rates.py`), the Geant4 answer (`FEASIBILITY_SIM.md`), polarised option (`POLARISED.md`), lxplus drivers (`sim/lxplus/`), slide deck (`deck/build_deck.py`) |
| [`lnl/`](lnl/README.md) | LNL feasibility for the ⁸Be search: facility (`FACILITY.md`), reaction (`PHYSICS.md`), lithium targets (`TARGETS.md`), the rate/acceptance/reach model (`lnl_rates.py` → `ESTIMATES.md`), and the Geant4 plan (`GEANT_PREP.md`) |
| [`demokritos/`](demokritos/README.md) | Demokritos feasibility for the ⁴He search: facility (`FACILITY.md`), reaction and ATOMKI ⁴He (`PHYSICS.md`), the yield/acceptance/reach model calibrated on LNL Geant4 (`demokritos_rates.py` → `ESTIMATES.md`), and the Geant4 campaign (`GEANT_PREP.md`, `sim/`) |
| [`ganil_nfs/`](ganil_nfs/README.md) | NFS beam reference: spectra, converters, timing, backgrounds, rates for our geometry, with sources (`refs/`) and a beam model (`nfs_beam.py`) |
| `docs/` | The GANIL/NFS plan and its anchor calculations (`anchor_kinematics.py`, `anchor_numbers.py`, `anchor_vessel.py`) |
| [`survey/`](survey/README.md) | World survey of neutron facilities: the yield per neutron vs E_n, the ILL-scaled thermal model, the NFS-scaled fast model, the catalogue with verdicts (`SURVEY.md`) |
| [`trigger_scint/`](trigger_scint/README.md) | Facility-independent: fixing the trigger-scintillator acceptance. The as-built stack accepts 2.3 % of X17 pairs; four ~75 cm plastics give ~14 %. Includes big-slab backgrounds at the ILL. |
| [`he4_bag/`](he4_bag/README.md) | A ⁴He bag / flight tube against air ¹⁴N, and the ³He-tight cell skin (12 µm PET + 6–7 µm Al) |
| `vessel_design/` | Parametric CAD of the 1 bar mylar-wrap, carbon-rod-cage ³He cell (STEP/STL/FreeCAD in `out/`) |
| `3he_material_budget/` | Early Highland material-budget script for the ³He target |
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
