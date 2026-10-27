# LNL (Legnaro): the ATOMKI ⁸Be search with the MX17 apparatus

Started 2026-10-07. Could the n_TOF X17 apparatus repeat the ATOMKI measurement,
⁷Li(p,e⁺e⁻)⁸Be at the 18.15 MeV resonance, on a low-energy proton beam at INFN
Laboratori Nazionali di Legnaro? What is the beam, what does a lithium target look
like, and how far would we get before any Geant4?

## Read this first: the two target designs in Geant4 (2026-10-27, `target/SHAPES_GEANT.md`)

- **Geant4 run L10** (MX17_Full_Geant `lnl_shapes`): Pierfrancesco's Cu hemisphere and the flat diamond window with the
  photographed beam line, as built and with the big plastics, at 1.03 and 1.10 MeV. Deck: note `lnl-target-shapes`.
- **Build the 45° window; drop the Cu dome.** Days per µA to 3σ at ATOMKI (big plastics, 1.10 MeV): window 45° 200 µm
  **0.27** (σ68 9.1°; 6.2° ≈ 0.21 d without its Ø20 Al end piece in view, §4.1), 300 µm 0.28, 0° 0.36; **Cu dome 200 µm 2.4** (σ68 22°; every lepton crosses the shell, and EPC in
  the Cu is 46 % of the background); flat L9 design 0.22. As built: window 1.5, dome 3.2. 1.03 MeV is 15–18 % slower.
- **DREAM:** the ⁸Be γ make 720 legs/s per µA (window, big plastics): live 83 % at P = 1, 97 % at P = 10; pairs 25–80 /s up to
  4 µA. Prescale the single-arm output.
- **Scintillators do not saturate:** 478 keV (5 × 10⁶ γ/s/µA) gives the big slab 3 × 10⁵ hits/s per µA, all below the leg
  threshold, ~0.5 µA anode current at 4 µA.
- **Watch:** the window's Mo K x-rays in the Micromegas (16 % occupancy per arm per µA, ESTIMATE); fluorine at the Li/stop
  interface at 1.10 MeV (exit energy = the 872 keV ¹⁹F resonance: 1 µg/cm² → 60 % of γ₀); the 0° window's Mo margin.

## Read this first: target options after Pierfrancesco's reply (2026-10-22, `target/TARGET_OPTIONS.md`)

- **2026-10-26, the beam line as photographed** (TARGET_OPTIONS §18, `target/opt_beamline.py`, 3D: `viz/lnl_beamline_3d.html`
  → site `facilities/lnl-beamline.html`): the target stays **at the detector centre**. The cup is at the *left* end of the photo,
  so the nearest steel is ~17 cm upstream and **no accepted lepton crosses the steel tube, valve, tees or flanges**. Only the
  grey flange (~2–3 cm back) is seen: 22 % of pairs at 3.4 % X₀ if PVC, +0.2° behind the Cu cup, which alone costs 9°.
  With a thin window, the window and a 0.5 mm Al end piece each put ~0.6 % X₀ on half the legs. The **Ø20 window in Ti rings
  (200 µm diamond) traces at 7.1°, 0.21 d/µA** and is safe at 1 bar (resolves audit B1). Clash: the floor stand at 17 cm
  goes through the bottom arm; supports must be ≥ 27 cm upstream. **Update:** the post may just be dangling; his "glue the cup
  straight onto the CF tube" takes the tube out of view (even steel), but the 300 µm Cu shell still costs σ68 14°: only a thinner
  or Be/Al+Mo cup helps. **Decided: the window is Ø20 mm, 200–300 µm diamond in Ti rings** (design page updated).
- **2026-10-26, audit (`AUDIT_2026-10-26.md`):** Pierfrancesco's photos (`pictures/`) confirm the §17 reading of the Cu dome
  (concave, Li at the apex, the cup is the end of the vacuum) but the existing cup is **300 µm with a thick rim** and the Li
  disc is only Ø 6–8 mm (a σ = 2 mm beam puts 13–32 % of the protons on bare Cu). **One error found:** the diamond-window
  stress in §17 was membrane-only, ×3 too low; 100–200 µm over Ø35 mm is 0.6–1.0 GPa at 1 bar. Use ≥ 400 µm at Ø35 or
  200–300 µm over Ø20–25 mm in thin Ti rings. Fix §17 and the page before sending the links. The beam-line photo: keep
  ≥ 30 cm of plain pipe before the target (the gate valve and stub clash with the top arm). Everything else checked is right.
- **2026-10-24, Pierfrancesco's two shapes** (TARGET_OPTIONS §17, `target/opt_shapes.py`; a ray-trace calibrated on Geant4 L9,
  ESTIMATE): a **200 µm Cu dome** puts 1.4–8 % X₀ on every lepton (σ68 ~14°, 0.40 d/µA vs 0.22). Make it Be or Al + Mo and it
  matches the design. The **tilted diamond window** matches the design (7.2°, 0.21 d; diamond 100–200 µm over the full Ø35 mm) **if the last ~40 mm of tube is ≤ 0.5 mm Al
  or CFRP** (a steel CF tube: 14°). **The LN₂ trap goes upstream in the pipe, not around the target** (a Cu shroud costs 13–15°).
- **2026-10-23: the design page** `viz/lnl_target_design.html` (live at `facilities/lnl-target.html`): the stack built
  up layer by layer, open questions, answers to Pierfrancesco, dropped ideas. **No water needed at LNL** (TARGET_OPTIONS §14):
  a Cu arm from the ring to the flange keeps the film at 56 °C at 4 µA.
- **2026-10-23, Pierfrancesco's follow-ups** (TARGET_OPTIONS §15–16, on the page): **Cu substrate**: a 25 µm Cu foil matches the
  diamond design in Geant4 (0.21 vs 0.22 d/µA), ≤ ~5 µA and 1–3 weeks per target; machined Cu ≥ 100 µm costs ×1.6–1.9.
  **Li thickness**: keep it thin (20 µm, out at 872 keV) and stop the beam in the backing; a stopping-thick film is 77 % 441 keV.
- **Film: 20 µm metallic Li** (his proposal) at E_p 1.10 MeV gives ×8.2 the ⁸Be γ₀ per proton of the 1.5 µm Li₂O baseline;
  the beam leaves it at 0.87 MeV, so the 441 keV share stays at 0.85 %. The same X17 rate needs ~0.12 µA.
- **Heat is a conduction-path problem, and diamond solves it** (`target/opt_thermal.py`, finite-volume, checked to 0.7 %):
  20 µm Li below 150 °C up to 30–40 µA on a 50 µm membrane, ~270 µA on 1 mm with a dry rim clamp, ~480 µA brazed.
  Micro-channels are not needed below ~100 µA.
- **But a thick backing costs the leptons (Geant4 L9, branch `lnl_target`)**: days to 3σ at R(ATOMKI) per µA, baseline
  1.0 → **0.20 (Li 20 µm / diamond 50 µm), 0.22 with an 8 µm Mo beam stop**, 0.32–0.37 on 1 mm diamond (0.27 at best,
  r = 8 mm at +12 cm). For ⁸Be no offset moves a thick backing out of the way (legs cross it edge-on).
- **Recommended for LNL: Li 20 µm / Mo (or Ta) 8 µm / CVD diamond 50–100 µm on a cooled Cu ring, at the centre, with a LN₂ cold trap upstream in the beam pipe (§17: not a shroud around the target).**
- **Backing γ never reaches the 13–18 MeV window** (measured σ; Geant4 itself has no (p,γ) data at 1 MeV, G4TENDL checked).
  The old Al backing was the largest single-arm trigger source (10.8 MeV line, ~23 legs/arm/s at 1 µA).
- **Open, for bench tests:** MeV-proton blistering of diamond, Li adhesion on coated diamond, residual water (Li is a getter:
  1.4 µm/day at 10⁻⁷ mbar H₂O). PIGE (478 keV) watches the Li to 1 % in a minute; Ge only for Na/B lines.
- Code: `target/opt_{thermal,backing,rates,monitor,geant,tables}.py`; runs `target/lxplus/`; note `lnl-target-options`
  (`target/deck/build_options_deck.py`).

## Then: the lithium target, and what probably stopped the LNL 2023–24 run (2026-10-22, `target/TARGET_STUDY.md`)

- The LNL ⁸Be group ran **LiF at 1.03 MeV**. There ¹⁹F(p,α_π) makes **2.5–3.5×10³ 6.05 MeV E0 pairs per ⁸Be pair**, and
  ATOMKI/Hanoi say it "would overload" a ΔE–E array. That is the likeliest reason for no result (an inference: ask them).
- Strip targets (ATOMKI-style 10 µm Al) run at 400–700 °C per µA: Li diffuses into the backing and the beam reaches 441 keV.
- For MX17:
  - Li₂O (no fluorine) on an edge-clamped, cooled disk (< 150 °C up to 2 µA; graphite or Cu at 4 µA), moved under Ar,
    monitored by PIGE and a 441 keV scan;
  - the 3D fit is biased < 0.06 R_ATOMKI by a drifting target, where an angle-only fit is biased up to 0.2.
- Code: `target/target_model.py`, `target/target_rates.py`, `target/target_fit_bias.py`. Geant4 run L8. Deck:
  `target/deck/build_deck.py` → note `lnl-lithium-target`.

## Then: one closing slide for the n_TOF talk (2026-10-14, `FEASIBILITY_SIM.md` §18)

- `talk/lnl_summary_figs.py` → `out/talk/` makes the figures for the slide: X17 per day in acceptance, and significance
  against beam days, each as png, pdf and csv, plus `numbers.json`. Rerun it after `reach_geant.csv` changes.
- The draft slide `lnl-summary` (`deck/summary_slide.py`) is slide 3 of the deck.
- Headline at 1 µA:
  - the n_TOF stack selects 17 X17/day and reaches 3σ at R(ATOMKI) in 17 d;
  - the big plastics select 135/day (pair trigger ×7.1) and reach it in 1.0 d;
  - the plates cost ~€93k (~€121k with the SiPM readout).

## Then: the analysis end to end on pseudo-data (2026-10-14, `FEASIBILITY_SIM.md` §17)

- `sim/lnl_pseudo.py` → `out/pseudo/`: a blinded, step-by-step analysis of one simulated week, then a coupling scan
  (1000 toys per point). The truth differs from the fit model (shifted norms, acceptance, nuisances, plus 2 % S_θE and
  S_m structure the fit lacks); a variant builds the templates from half of the MC.
- One week at R(ATOMKI): r̂ = 0.87 ± 0.14 (6.1σ). Up to a week the errors are honest (pull width 1.15). **At 30 days the
  unmodelled shape errors dominate** (pull 1.35, 1.7 % false 3σ); a wider fit that floats them restores 1.06 / 0.2 % for
  a 10–20 % larger σ(r). The template MC should be ≥ 10× the data exposure.
- Five pitch slides (`deck/pseudo_slides.py`) and a price slide (`price_slide` in `deck/pitch_slides.py`) are in the deck.

## Then: can a mismodelled background fake the X17? (2026-10-14, `FEASIBILITY_SIM.md` §16)

- **Three new pitch slides** (`deck/maps_slides.py`, after "S/B"):
  - one week in θ × |y|: background counts, X17 counts, S/B;
  - an "impostor", a background error that copies the X17 angle spectrum exactly, in angle, |y| and E_sum;
  - the same in 2D, window against γ₁ side band, with the fake X17 each fit reports.
- **The angle-only fit reads the impostor as 100 % of an X17. The 3D reference fit reads 13 % (acceptance-type) or 24 %
  (18 MeV-only)**, ~1–2σ in a week while the real X17 is 7.5σ, and is left with χ² ≈ 20 it cannot absorb
  (big plastics). `sim/lnl_nd_maps.py` → `out/nd/maps/`.
- No fit separates a background error shaped like the X17 in all three variables. The checks for that are QED and the
  E_p scan.

## Earlier: the pitch slides and target-region scattering (2026-10-13, `FEASIBILITY_SIM.md` §15)

- **Pitch block in the deck** (`deck/pitch_slides.py`, slides 2–15 since 2026-10-14, for the 15 Oct talk; the rest of the deck is backup):
  - the case and the run plan: ~12 days on AN2000 for 5σ on resonance + both off-resonance points;
  - LNL against the n_TOF run, and the n_TOF lessons;
  - the setup with the plastics' price (~€93–136k);
  - S/B as the real limit, and what to study;
  - scattering, open issues, and the scintillator DAQ.
- **Scattering matters much more once the background shape floats** (`sim/lnl_smear_nd.py`). The 3D fit goes
  1.0 d (CFRP 0.4 mm, 4.5°) → 2.5 d (9°) → 6.8 d (~14°, n_TOF capsule) → 31 d (~27°, a 1 mm steel pipe). m_ee alone
  goes 1.7 → 7.7 → 28 → 284 d. The thin chamber over the region the leptons cross is the design driver.

## Earlier: realistic calorimetry, every single arm triggered, and a 3D fit (2026-10-12, `FEASIBILITY_SIM.md` §14)

- **The arm energies now carry an n_TOF-anchored response** (`sim/lnl_calo.py`; per-arm layers in `$E/sel_v3`).
  The 5 cm big plastics keep the m_ee result (0.83 → 1.4 d calibrated). **As built loses it** (8 → 35 d with a
  repaired liquid, ~190 d with the liquid as at n_TOF): 2 cm bars stop neither lepton.
- **Fit θ × |y| × E_sum** (`sim/lnl_nd.py`). The same background-shape error is put on the events and seen by
  every analysis. The 3D fit is faster and robust:

  | | 3D fit, calibrated response | worst structure tried | m_ee alone, worst |
  |---|---|---|---|
  | **big plastics** | **1.0 d** | 1.2 d | 3.1 d |
  | **as built**, liquid repaired | **17 d** | 21 d | 529 d |

  It is stable between Monte Carlo halves (angle-only fits swing ×2–3).
- **Trigger** (`sim/lnl_trigger.py`): every arm leg; pairs never prescaled; singles prescaled 1/P. At P = 1,
  DREAM is 91–98 % live up to 4 µA. Single-arm cosmics give each arm's gain to ~1 %/h.
- **No more n_TOF analysis needed** for this. Bench-test a 5 cm plate, and decide whether the liquid can be
  repaired.
- Deck slides "Trigger", "Calorimetry", "2D fit"; the cover and record quote the 3D numbers.
- **2026-10-13: `out/geant/reach_geant.csv` column `days_3d` is the reference** (every scenario, current and
  mass; `lnl_geant.py --nd`, §14.5). It is close to the old counting numbers: 13–17 % faster with big plastics, 6–25 % slower as built.

## Earlier: fit the pair mass; the background shape no longer sets the reach (2026-10-12, `FEASIBILITY_SIM.md` §12–13)

The 2026-10-08 days assumed the IPC angular shape is known exactly. In the opening angle S/B is only ≈ 7 %, so
a few % of shape error looks like the signal (§12). Two things fix it, both offline (same trigger, same data):

- **The energy split** y = (E₁ − E₂)/(E₁ + E₂) from the arm energies. The X17 shares its energy evenly at the edge;
  the IPC does not.
- **Combined with θ into the pair mass** m_ee = W √((1 − y²)(1 − cos θ)/2), W = 18.15 MeV. The X17 becomes a
  0.6 MeV-wide peak on a smooth continuum.

Days to 3σ at R(ATOMKI), 1 µA, MM 15° + TOF. The L7 IPC samples have ×10–20 the statistics, and the γ* anisotropy
is included:

| | statistics only | θ fit, 2 % unknown shape | **m_ee fit, 2 % shape + in-run controls** |
|---|---|---|---|
| big plastics | 1.1 d | 14 d | **0.83 d** (11.7σ at 30 d) |
| as built | 14 d | ~4 years | **8.0 d** (5.2σ at 30 d) |

- **ATOMKI's bump is only +25–35 %** over their simulated IPC curve. Their 6.8σ also assumes that shape (§12.2).
- **The γ* anisotropy about the beam** is a₂ = 0.36 (Hayes et al. 2021). The interference P₁ term cancels in our
  symmetric arms; the P₂ term reshapes the IPC by +3 to +10 % in the window (§13.2).
- **Event mixing** of single-arm events reproduces the acceptance's local structure to 1–2 % after a smooth cubic.
  It gets the tilt wrong (§13.3). So the run needs a prescaled single-arm trigger.
- **Next:**
  - a per-arm gain nuisance;
  - make m_ee the reference in `lnl_geant.py` (superseded: the 3D fit is, §14.5);
  - a mass scan with the look-elsewhere effect.
- Deck slides 18–24. The animation (`viz/lnl_run_animation.html`) switches between angle, angle |y| < 0.3, and
  pair mass.

## The Geant4 result (2026-10-08, `FEASIBILITY_SIM.md`; statistics only)

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
- **2026-10-09** (`FEASIBILITY_SIM.md` §9–10, deck slides 12–14 and 16–17):
  - The big plastics' ×13–17 is **acceptance**. The X17 rate goes ×15, but the IPC goes ×14 with it.
  - ~65–70 cm is enough at 41 cm, and ~55–60 cm right behind the SiPM wall. Past that, the
    Micromegas set the acceptance (toy calibrated on Geant4).
  - The CFRP chamber widens the X17 edge to σ68 4.6° and costs ~11 % in time. Al 1 mm costs ×1.33.
  - (§11, slide 17) In one week at 1 µA the smeared X17 is a 3–4σ excess per 4° bin. The 1.2 d is
    counting with the IPC known exactly; the fit with M1/E1/γ₁ free needs 3.7 d. S/B ≈ 7 %, so the
    IPC shape has to be known to ~1 %. Slide 13 draws n_TOF as built against the big plates, to scale; slide 14 shows only the current bar position (optimum ~78 cm).

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
| `sim/lnl_geant.py` | The Geant4 analysis → `out/geant/` (tables + figures; `days_3d` in `reach_geant.csv` is the reference 3D fit, `--nd` refreshes it); `sim/fetch_sel.sh` copies the merged tables from EOS; `sim/lxplus/` = condor reduce/merge (`lnl_pipe.sh`) |
| `plastic_size.py` | Why the big plastics win, and days against square-plastic size and distance, with the plates' footprint: a geometric trigger-leg toy calibrated on the Geant4 pair-tags (analytic stand-in) → `out/plastics/` (`--figs` = figure only). `FEASIBILITY_SIM.md` §9 |
| `sim/lnl_week.py` | One week of pseudo-data at 1 µA (measured angle), the excess over the IPC, Z against time for counting and the two template fits, and with an IPC shape systematic → `out/scatter/week*.csv`. `FEASIBILITY_SIM.md` §11 |
| `sim/lnl_scatter.py` | X17 peak widening from the target region: Geant4 truth vs reco on the same events, Al-tube residuals, days cost per wall, Highland layer budget → `out/scatter/`. `FEASIBILITY_SIM.md` §10 |
| `sim/lnl_syst.py` | Is the significance real? ATOMKI 2016 at truth level vs their Fig. 4, the symmetric-pair (\|y\|) cut, an Asimov/Fisher fit with shape nuisances (M1/E1/γ₁, resolution and E scale, acceptance cubic, Gaussian-process "unknown structure") and control samples (asymmetric pairs, γ₁ side band, 441 keV run); the γ* anisotropy; the same fit in the pair mass m_ee (`use_var("mass")`); IPC templates from L7 when present → `out/syst/`. `FEASIBILITY_SIM.md` §12–13 |
| `sim/lnl_mixing.py` | Event mixing (single-arm events vs legs of triggered pairs) against the true pair acceptance in θ → `out/mixing/`. `FEASIBILITY_SIM.md` §13.3 |
| `viz/export_anim_data.py` | Inlines the `lnl_syst.py` spectra (angle, angle \|y\| < 0.3, m_ee) and robust days into `viz/lnl_run_animation.html` |
| `deck/` | `build_deck.py` (main slides) + `appendix.py` (basics) + `plastics_scatter.py` (slides 12–14, 16–17; slide 17 needs `sim/lnl_week.py` run first) + `syst_slides.py` (slides 18–24) → `out/lnl-x17-feasibility.html` |
| `GEANT_PREP.md` | What to build in MX17_Full_Geant (branch `lnl` from `ill_ring`), the run list L0–L6, decisions needed first |
| `lnl_rates.py` | The model: kinematics, Zahnow σ split into resonances + direct capture, PSTAR stopping, thin/thick yields, Born IPC (from nTof_x17 `ipc_born`), four-arm toy acceptance, counting reach |
| `out/*.csv`, `out/figures/` | `kinematics`, `excitation`, `yields`, `ipc_alpha`, `acceptance(_hist)`, `reach`; figures with their CSVs; `viewer_yield_grid.json` (the `Y` table in the 3D viewer) |
| `data/exfor_A0639_Zahnow1995.txt` | ⁷Li(p,γ)⁸Be S-factors, γ₀ and γ₀+γ₁, 98–1500 keV (EXFOR) |
| `data/pstar_stopping.csv` | NIST PSTAR proton stopping for LiF, Teflon, C, O, Al, Be, Cu, Ti, Mo, W, Au, Ag, Kapton, Mylar, air, H |
| `viz/lnl_setup_3d.html` | 3D view to scale: MX17 arms + trigger stack around the Li target and chamber, vs the LNL 2023–24 clovers and ATOMKI 2016; live rates per machine/energy/film from `lnl_rates.py`; illustrative X17 / IPC / cosmic events |
| `viz/lnl_run_animation.html` | Animated run (2026-10-10): beam line → target → reactions (γ₀, γ₁, p′, IPC, X17), a 2D toy event display at the real layer radii with trigger and chord reco, and the Geant4 opening-angle spectrum (`out/geant/figures/geant_theta.csv`, MM 15° + TOF) Poisson-filled day by day, as built vs big plastics. Data inlined; regenerate by hand if `geant_theta.csv` changes. Site copy: `facilities/lnl-run-animation.html` |
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
