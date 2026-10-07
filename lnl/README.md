# LNL (Legnaro): the ATOMKI ⁸Be search with the MX17 apparatus

Started 2026-10-07. Could the n_TOF X17 apparatus repeat the ATOMKI measurement,
⁷Li(p,e⁺e⁻)⁸Be at the 18.15 MeV resonance, on a low-energy proton beam at INFN
Laboratori Nazionali di Legnaro? What is the beam, what does a lithium target look
like, and how far would we get before any Geant4?

## Bottom line (pre-Geant4, good to ~×2)

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
| `GEANT_PREP.md` | What to build in MX17_Full_Geant (branch `lnl` from `ill_ring`), the run list L0–L6, decisions needed first |
| `lnl_rates.py` | The model: kinematics, Zahnow σ split into resonances + direct capture, PSTAR stopping, thin/thick yields, Born IPC (from nTof_x17 `ipc_born`), four-arm toy acceptance, counting reach |
| `out/*.csv`, `out/figures/` | `kinematics`, `excitation`, `yields`, `ipc_alpha`, `acceptance(_hist)`, `reach`; figures with their CSVs |
| `data/exfor_A0639_Zahnow1995.txt` | ⁷Li(p,γ)⁸Be S-factors, γ₀ and γ₀+γ₁, 98–1500 keV (EXFOR) |
| `data/pstar_stopping.csv` | NIST PSTAR proton stopping for LiF, Teflon, C, O, Al, Be, Cu, Ti, Mo, W, Au, Ag, Kapton, Mylar, air, H |
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

## Tomorrow

1. **Slides.** Use the `publish-note` skill (it exists on this machine; it publishes
   to dylan-neff.web.cern.ch/notes via `~/PycharmProjects/dylan-cern-site`). Build with
   `slidedoc.py` like `../ill/deck/build_deck.py`.
2. **Geant4.** `GEANT_PREP.md` §2 (target region, point vertices, γ-line source),
   then runs L0–L2.
3. **Emails.** Anna Selva / pacbeams@lnl.infn.it (machines, hall, next PAC);
   T. Marchi (their 2023–24 data, collaboration); our own collaboration (the ATOMKI
   demonstrator test).
