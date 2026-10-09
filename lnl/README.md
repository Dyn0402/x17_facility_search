# LNL (Legnaro): the ATOMKI ⁸Be search with the MX17 apparatus

Started 2026-10-07. Could the n_TOF X17 apparatus repeat the ATOMKI measurement,
⁷Li(p,e⁺e⁻)⁸Be at the 18.15 MeV resonance, on a low-energy proton beam at INFN
Laboratori Nazionali di Legnaro? What is the beam, what does a lithium target look
like, and how far would we get before any Geant4?

## Read this first: the Geant4 result (2026-10-08, `FEASIBILITY_SIM.md`)

Days to show the ATOMKI ratio R = 5.8×10⁻⁶ at **3σ**, Li₂O 300 µg/cm² at 1.10 MeV, **1 µA**,
data-like selection on Geant4 L1–L6:

| hardware | counting / template fit | at CN 4 µA |
|---|---|---|
| **n_TOF as built** (LS read out), with 3° MM segments **or** a 0.3 ns TOF veto | **15 / 22 d** | 4 / 6 d |
| as built, LS dead | 19 / 25 d | 5 / 6 d |
| **4 big plastics 75×75×5 cm + all 20 SiPM bars** (trigger_scint, ~€90–140k) | **1.2 / 1.6 d** | **0.3 / 0.4 d** |

- **Signal acceptance as built: 3.3 % pair-tag** (2.4× below the toy × `EPS_REST`). The
  two 20×30 cm plastics are the bottleneck; the big plastics give 23 %.
- **E_sum separates the γ₁ (15 MeV) IPC.** It is removed as built (with LS) and with the
  big plastics; with the LS off it is not.
- **Cosmics are the one danger:**
  - 8×10⁴/day in 125–155° at trigger level, against ~120 IPC/day after cuts;
  - the measured chambers' 15° segments do not stop them;
  - an upper E_sum edge (muons leave 20–35 MeV), 3° segments or TOF do.
- EPC, accidentals, DREAM dead time, the 478 keV line: negligible.
- Keep the **CFRP chamber and a low-Z backing**. Al 1 mm doubles σ_θ (5° → 12°).
- The E0 6.05 MeV calibration line is invisible to the n_TOF trigger. Calibrate on 441 keV.
- **2026-10-09** (`FEASIBILITY_SIM.md` §9–10, deck slides 12–13 and 15–16):
  - The big plastics' ×13–17 is **acceptance**. The X17 rate goes ×15, but the IPC goes ×14 with it.
  - ~65–70 cm is enough at 41 cm, and ~55–60 cm right behind the SiPM wall. Past that, the
    Micromegas set the acceptance (toy calibrated on Geant4).
  - The CFRP chamber widens the X17 edge to σ68 4.6° and costs ~11 % in time. Al 1 mm costs ×1.33.
  - (§11, slide 16) In one week at 1 µA the smeared X17 is a 3–4σ excess per 4° bin. The 1.2 d is
    counting with the IPC known exactly; the fit with M1/E1/γ₁ free needs 3.7 d. S/B ≈ 7 %, so the
    IPC shape has to be known to ~1 %. Slide 13 now shows only the current bar position (optimum ~78 cm).

The pre-Geant4 estimate below is kept for the record. Its detector factors are superseded.

## Bottom line (pre-Geant4, good to ~×2; detector part superseded above)

- **The beam is easy.**
  - AN2000: 0.2–2 MV, up to 1 µA H⁺, self-service.
  - CN: 0.8–5.5 MV, 1 µA at 0.8–2 MeV in the beam sheet; ~4 µA authorised; also a
    3 MHz, < 2 ns **pulsed** mode.
  - Both cover 441–1225 keV. There are **no neutrons below the 1.88 MeV ⁷Li(p,n)
    threshold**, so radiation protection does not cap the current.
  - Access is through the LNL PAC (yearly, autumn) `FACILITY.md`.
- **LNL already did this.**
  - The LNL-INFN pair spectrometer (Marchi, Góngora-Servín, Tagnani *et al.*;
    ATOMKI-style plastic ΔE–E clovers) ran on **AN2000 in 2023–24**: LiF targets,
    441 keV and 1.03 MeV, ~800 nA, ~790 h.
  - It is still unpublished as of Oct 2026.
  - They are the first people to talk to.
- **The physics.**
  - A ~1 MeV proton is captured on ⁷Li, making ⁸Be\* at E\* = 17.255 + 0.875·E_p MeV.
  - It does so mostly via two M1 resonances (441 keV → 17.64; 1030 keV → 18.15),
    on top of a flat **E1 direct capture that is ~half of the γ₀ at 1.03–1.10 MeV**.
  - X17 pairs pile up above an edge at **~134–138°**.
  - Details in `PHYSICS.md`.
- **Who has looked so far.**
  - ATOMKI: 6.8σ in 2016; also off-resonance in 2022.
  - Hanoi: > 4σ in 2024.
  - **MEG II: nothing**, R(18.1) < 1.2×10⁻⁵ (2025).
  - MEG II members showed in **Sept 2026** that cosmic rays make a 140° bump in
    ATOMKI-type spectrometers.
- **Targets** (`TARGETS.md`).
  - A few-hundred-nm film of LiF or Li₂O (or Li metal, or sputtered LiPON) on a
    10–25 µm Al/C/Cu foil, in a thin carbon-fibre chamber.
  - Keep it thin (≲ 300 µg/cm² ≈ 60 keV), so the beam never slows into the 50×
    stronger 441 keV resonance. ATOMKI's 2016 metallic-Li targets did exactly that.
  - Use **boron-free** Li: ¹¹B(p,γ) puts 16–17 MeV γ in the window.
- **Rates.** At ATOMKI conditions (Li₂O 300 µg/cm², 1.10 MeV, 1 µA):
  - ~1.9×10³ γ₀/s and ~7 IPC/s into 4π;
  - **~900 X17/day** at the ATOMKI ratio R = 5.8×10⁻⁶.
- **Our apparatus.**
  - The four big Micromegas arms see the 140° region through opposite arms, at
    **~40 % geometric acceptance** (ATOMKI's spectrometer: ~2.5 %).
  - After the as-built trigger stack, ~46 X17/day are accepted at 1 µA, against
    ~1.1k (γ₀) + 2.1k (γ₁) IPC and ~200 cosmics per day in 125–155°.
- **Reach.** Days to show the ATOMKI ratio at **3σ / 5σ**, 1 µA:

  | stack | days, 3σ / 5σ |
  |---|---|
  | as built (cannot separate 15 from 18 MeV) | **~15 / ~40** |
  | with calorimetry | **~6 / ~16** |

  - ×4 faster at CN's 4 µA.
  - MEG II's 90 % limit is crossed in ~¼ of that time.
  - Off-resonance points (0.8, 1.225 MeV) are 3–4× slower.
  - Full table in `ESTIMATES.md`.
- **The MM tracking is the decisive advantage.**
  - With segment + collinearity cuts (ILL §10), cosmics drop below the IPC.
  - Without them the reach is 2.5× worse and cosmics dominate, which is the failure
    mode the 2026 paper attributes to ATOMKI.
  - CN's pulsed beam and the point-vertex cut add margin.
- **For comparison:** this is a much easier experiment for MX17 than the ILL thermal
  search (`../ill`). It has ~3× the accepted signal per day and no neutron
  backgrounds, and it is the measurement that decides the claim.

**Biggest unknowns, and what replaces them** (`GEANT_PREP.md`):
1. the trigger × E_sum × reconstruction factor carried from the ILL (`EPS_REST` = 0.14);
2. whether the stack can separate 15 MeV from 18 MeV pairs;
3. cosmics in the LNL hall;
4. hall space at AN2000/CN.

## Files

| file | what it is |
|---|---|
| `FACILITY.md` | LNL: AN2000 and CN specs, current/energy limits, pulsed beam, lines, schedule, PAC route and contacts, the local ⁸Be group, open questions **(ask)** |
| `PHYSICS.md` | The reaction step by step, ⁸Be levels and widths, direct capture, IPC, X17 kinematics vs E_p, every measurement so far (ATOMKI 2016/2022, Hanoi, MEG II, LNL, MEG-2026 cosmics), what a new measurement must get right |
| `TARGETS.md` | What a Li target is and how it is made; LiF vs Li₂O vs Li vs LiPON; contaminant reactions (¹⁹F, ¹¹B, ²⁷Al…); backings, heat, dose; recommendation |
| `ESTIMATES.md` | The pre-Geant4 numbers: 4π rates per configuration, toy acceptance, reach and days-to-significance, assumption table |
| `FEASIBILITY_SIM.md` | **The Geant4 result** (L1–L6, big plastics, 20-bar readout): acceptance, E_sum, cosmics, EPC, accidentals, DAQ, material, reach |
| `sim/lnl_geant.py` | The Geant4 analysis → `out/geant/` (tables + figures); `sim/fetch_sel.sh` copies the merged tables from EOS; `sim/lxplus/` = condor reduce/merge (`lnl_pipe.sh`) |
| `plastic_size.py` | Why the big plastics win, and days against square-plastic size and distance, with the plates' footprint: a geometric trigger-leg toy calibrated on the Geant4 pair-tags (analytic stand-in) → `out/plastics/` (`--figs` = figure only). `FEASIBILITY_SIM.md` §9 |
| `sim/lnl_week.py` | One week of pseudo-data at 1 µA (measured angle), the excess over the IPC, Z against time for counting and the two template fits, and with an IPC shape systematic → `out/scatter/week*.csv`. `FEASIBILITY_SIM.md` §11 |
| `sim/lnl_scatter.py` | X17 peak widening from the target region: Geant4 truth vs reco on the same events, Al-tube residuals, days cost per wall, Highland layer budget → `out/scatter/`. `FEASIBILITY_SIM.md` §10 |
| `deck/` | `build_deck.py` (main slides) + `appendix.py` (basics) + `plastics_scatter.py` (slides 12–13, 15–16; slide 16 needs `sim/lnl_week.py` run first) → `out/lnl-x17-feasibility.html` |
| `GEANT_PREP.md` | What to build in MX17_Full_Geant (branch `lnl` from `ill_ring`), the run list L0–L6, decisions needed first |
| `lnl_rates.py` | The model: kinematics, Zahnow σ split into resonances + direct capture, PSTAR stopping, thin/thick yields, Born IPC (from nTof_x17 `ipc_born`), four-arm toy acceptance, counting reach |
| `out/*.csv`, `out/figures/` | `kinematics`, `excitation`, `yields`, `ipc_alpha`, `acceptance(_hist)`, `reach`; figures with their CSVs; `viewer_yield_grid.json` (the `Y` table in the 3D viewer) |
| `data/exfor_A0639_Zahnow1995.txt` | ⁷Li(p,γ)⁸Be S-factors, γ₀ and γ₀+γ₁, 98–1500 keV (EXFOR) |
| `data/pstar_stopping.csv` | NIST PSTAR proton stopping for LiF, Teflon, C, O, Al, Be, Cu, Ti, Mo, W, Au, Ag, Kapton, Mylar, air, H |
| `viz/lnl_setup_3d.html` | 3D view to scale: MX17 arms + trigger stack around the Li target and chamber, vs the LNL 2023–24 clovers and ATOMKI 2016; live rates per machine/energy/film from `lnl_rates.py`; illustrative X17 / IPC / cosmic events |
| `refs/*.txt` | Text extractions of every source (PDFs in `refs/pdf/`, not committed) |

```bash
PY=~/PycharmProjects/nTof_x17/.venv/Scripts/python.exe   # Linux: .venv/bin/python
$PY lnl/lnl_rates.py          # tables + CHECK lines + figures (~3 min)
$PY lnl/lnl_rates.py --quick  # tables only, small MC
```

`lnl_rates.py` imports `sept26_prelim_analysis/ipc_born.py` from the nTof_x17 checkout
(`$NTOF_X17`, default `~/PycharmProjects/nTof_x17`). The CHECK lines compare it with
Tilley (σ at 441 keV, branching), Rose (IPC α), MEG II's own normalisation, and a
measured thick-target yield.

## Status and next steps (2026-10-08)

1. **Slides: done.** `deck/build_deck.py` → `out/lnl-x17-feasibility.html`, live at
   dylan-neff.web.cern.ch/notes/lnl-x17-feasibility.html and linked from `/facilities/lnl.html`.
   Rebuild after any change to `lnl_rates.py` outputs, then republish with `add-note.py … --force --deploy`.
   Slides 12–13 (why big plastics win, plastic size) and 15–16 (peak widening from the chamber) were
   added 2026-10-09 from `plastic_size.py` and `sim/lnl_scatter.py`. Rerun both first if the Geant4
   tables change.
   Slides 19–37 are a "basics" appendix (beam, targets, chamber, the physics channel incl. where the
   beam energy goes (E*, C1a–c), glossary),
   built by `deck/appendix.py` from `appendix_calc.py` → `out/appendix/*.csv` (2026-10-08). Its
   chamber-wall resolutions other than the three Geant4 walls are a Highland model fitted to L5
   (an analytic stand-in).
2. **Geant4: done** (2026-10-08), `FEASIBILITY_SIM.md`. Open: the SiPM-wall time
   resolution and whether the LS can be read (ask); the Zhang–Miller IPC shapes.
3. **Emails** (not sent). Anna Selva / pacbeams@lnl.infn.it (machines, hall, next PAC);
   T. Marchi (their 2023–24 data, the Góngora-Servín thesis, collaboration); our own
   collaboration (the ATOMKI demonstrator test).
