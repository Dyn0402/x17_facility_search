# Target options for MX17 at LNL: film, backing, cooling, vacuum and monitoring

Started 2026-10-22, after Pierfrancesco's reply to the LNL slides. He named the target as the critical issue and asked:
which compound (no fluorine; Li₂O), how to remove the heat, what background the backing makes and which backing is best,
a cold trap against carbon build-up, PIGE monitoring (does it need germanium?), whether a thicker Al Micromegas window
would help against "441 keV gammas", why the strip/clamp design on slide 7 is not convincing, and his own proposal:
**20 µm of metallic Li on a 1 mm diamond, water-cooled through micro-channels**.

This file is the options study. It builds on `TARGET_STUDY.md` (fluorine, heat on thin foils, diffusion, fit bias),
which it does not repeat. Numbers come from the code in this directory (§13). Facts that could not be found
publicly are marked **(ask)**. Analytic stand-ins are marked **ESTIMATE**. Sections say which numbers come from
Geant4 and which from measured nuclear data: Geant4 cannot make the target's own γ-rays (§11).

---

## 0. Bottom line (2026-10-22)

1. **Pierfrancesco's diamond idea is the right one, and the heat is not the hard part.**
   - LNL's beam is only 1–4 W (1.1 MeV × 1–4 µA). The heat problem of thin targets is one of *conduction path*,
     not of power: a 10 µm Al disk reaches 300 °C at 5 µA because 10 µm of Al conducts badly.
   - CVD diamond (k ≈ 1800 W/m/K) fixes it outright (§3). With a σ = 2 mm spot, keeping 20 µm of Li below 150 °C:

     | backing, cooling | max current |
     |---|---|
     | 50 µm diamond membrane, Cu clamp at r ≥ 8 mm | 29 µA (Li₂O at 300 °C: 53 µA) |
     | 300 µm diamond, clamped rim | 120 µA |
     | **1 mm diamond, dry clamp at r ≥ 15 mm** | **270 µA** |
     | 1 mm diamond brazed to a water-cooled Cu ring | 480 µA |
     | diamond with micro-channels under the face (h_eff ≈ 3×10⁴ W/m²/K) | 350 µA |

     At LNL's 4 µA every diamond option keeps the film at 21–35 °C. **Micro-channels are not needed at LNL;** an
     edge-cooled diamond does the same job up to a few hundred µA, because diamond spreads the heat sideways.
     Micro-channels matter for a 100 µA-class machine (ATOMKI's Tandetron, §10), and even there a brazed rim matches them.
   - **But a thick diamond costs the leptons (Geant4 L9, §7).** Legs leaving below 90° cross it nearly edge-on
     (σ68 13.5° for those pairs). 1 mm of diamond is ×1.9 slower per µA than a 50 µm membrane, and moving it 12–18 cm
     downstream or shrinking it to r = 8 mm recovers only part of that (best ×1.4). **For LNL: a thin (50–100 µm) diamond
     membrane at the centre; the 1 mm/micro-channel plate is the design for a ≥ 30 µA machine.**
2. **A thick metallic Li film is a large win, and 20 µm is about the right thickness.**
   - 20 µm of Li (1.07 mg/cm²) at E_p = 1.10 MeV takes the beam down to 0.87 MeV. That spans the whole 18.15 MeV
     resonance and stays far above the 441 keV one: the 441-keV share of γ₀ is 0.85 % (0.6 % for the thin Li₂O).
   - **γ₀ per proton is ×8.2 the thin Li₂O baseline** (×6.7 counting the resonant part only). So the same X17 rate
     needs ~0.12 µA instead of 1 µA: ×8 less heat, hydrogen, carbon, and ⁷Li(p,p′γ) per X17 is unchanged.
   - 40 µm gives ×14.5 but the 441 share rises to 3.3 %; a target that stops the beam is 77 % 441 keV. Stay at 15–25 µm.
3. **The backing's own background is small and can be made zero (§4).** None of the backing reactions reaches the
   13–18 MeV E_sum window. Per ⁸Be γ₀:
   - diamond: 0.37 γ at 2.37 MeV (¹²C(p,γ), 457 keV resonance) and 0.04 at 8.06 MeV (¹³C(p,γ), 556 keV resonance;
     0.0004 with ¹²C-enriched CVD diamond);
   - Al (today's baseline backing): 4.8 γ of 10.8 MeV (the 992 keV resonance) plus ~140 γ of 843 keV;
   - Ta, Mo, W, Cu: nothing above 1 MeV (Coulomb barrier); a 10 µm Ta layer stops the beam before it reaches the diamond.
   - The dominant low-energy line in every option is the Li itself: ~330–440 γ of 478 keV per γ₀.
   - The pair background from the backing is external conversion of the ⁸Be γ-rays: Geant4 L9 sizes it (§7).
4. **The open materials questions are hydrogen and adhesion, not heat (§5).**
   - Where the beam stops it implants 2×10¹⁸ H/cm² per day per µA (σ = 2 mm). Cu blisters from ~10¹⁹ (5 days at 1 µA),
     Ta not up to ≥ 3.4×10¹⁹. **Nobody seems to have measured MeV-proton blistering of diamond at 20–150 °C (gap).**
   - Diamond is an insulator: the stopped beam charges it. A thin metal layer (Mo or Ta, 8 µm; the range is 6 µm) between
     Li and diamond stops the protons, collects the charge, holds the hydrogen and gives Li something to wet. In Geant4 the
     8 µm of Mo costs ×1.1 in days.
   - **Recommended for LNL: Li 15–25 µm / Mo (or Ta) 8 µm / CVD diamond 50–100 µm, clamped or brazed at r ≥ 8 mm to a
     water-cooled Cu ring, at the centre of the arms.** 3σ at R(ATOMKI) in **0.22 d per µA** (the thin Li₂O baseline:
     1.0 d); below 150 °C up to 30–40 µA (35 °C at 4 µA). For a ≥ 30 µA machine: 300 µm–1 mm diamond, brazed rim.
5. **Vacuum chemistry matters more than carbon for metallic Li (§6).** Li is a getter. At 10⁻⁷ mbar of water it
   turns ~1.4 µm of Li a day into LiOH (ESTIMATE, sticking ≈ 1): a 20 µm target is converted in ~2 weeks. A LN₂ cold
   shroud around the target, the same one Pierfrancesco wants against carbon, brings both water and carbon down ~×10–100.
   Carbon is otherwise harmless for the thick target: with no trap, a week at 1 µA moves the beam 64 keV and costs 5 % of γ₀.
   Thin Li₂O also hydrates (Hanoi measured ×1.47), so the cold shroud is needed for either film.
6. **Geant4 L9 (§7): the backing must be thin where the leptons cross it, and for ⁸Be no offset avoids that.** At the
   centre ~70 % of selected X17 pairs have a leg through the backing. Moving a thick target 12 cm downstream (Demokritos'
   fix for ⁴He) still leaves 37 % of ⁸Be pairs with a leg crossing it nearly edge-on, and costs acceptance. Per µA, days to
   3σ at R(ATOMKI) (baseline thin Li₂O / Al 10 µm = 1.0): **20 µm Li on 50 µm diamond 0.20; + Mo 8 µm 0.22**; 1 mm diamond
   0.32–0.37 (0.27 at best, r = 8 mm at +12 cm); a water-cooled Cu block at +12 cm 2.9.
7. **Monitoring (§8):** the 478 keV PIGE line gives the Li content to 1 % in 10–60 s with either a HPGe or a LaBr₃
   at 25–50 cm. Germanium is not needed for Li alone; it is needed to separate Na (440), ¹⁰B (429) and Li (478), and is
   safe here: no reaction makes neutrons below E_p = 1.88 MeV. Add a Si detector for elastic backscattering (carbon, O/Li ratio).
8. **"441 keV gammas" and a thicker Al window (§9):** a window cannot help. 1 mm of Al stops 2 % of 478 keV γ and 0.6 %
   of 17.6 MeV γ, while it converts 0.9 % of 18 MeV γ into pairs and adds ~8° of scattering. The 17.64 MeV line from the 441 keV
   resonance is a calibration and a physics point, not a background to absorb.

---

## 1. Pierfrancesco's points, and where each is answered

| point | answer | § |
|---|---|---|
| run near 1 MeV; PTB, PSI, Debrecen too | all three are in the proton survey (`survey/proton/`): PTB PIAF, PSI MEG II CW (already ran ⁷Li(p,e⁺e⁻) with LiPON), ATOMKI Debrecen | 10 |
| no fluorine; Li₂O; a lot of heat | Li₂O or metallic Li; the heat is a conduction-path problem that diamond solves | 2, 3 |
| background from the backing; best backing | per-line yields for C, ¹²C-diamond, Al, Ta, Cu; Ta-on-diamond is clean | 4 |
| cold trap against carbon | carbon and water rates by vacuum class; one LN₂ shroud handles both | 6 |
| PIGE monitoring; germanium? | count rates, time to 1 %, which lines need Ge | 8 |
| 441 keV γ and the MM window | a window cannot attenuate them; it adds pairs | 9 |
| strips: diffusion, dead layer, background; the clamp | agreed: strips are out (TARGET_STUDY §5); the clamp works only through a conducting backing | 3 |
| 20 µm Li on 1 mm diamond, micro-channels | modelled thermally, in nuclear yields and in Geant4 (L9) | 2–7 |

## 2. The film

### 2.1 Which compound

| film | Li per keV of beam (rel.) | stability | handling | notes |
|---|---|---|---|---|
| **Li metal** | 2.2 | melts 180 °C; getter (H₂O, O₂, CO₂ at sticking ~1; N₂ slowly) | make in situ or move under vacuum/Ar | the most Li per keV; soft, wets metals; LiH forms where H stops |
| **Li₂O** | 1.0 | melts 1438 °C; hygroscopic (→ LiOH) | move under Ar | the FEAS baseline; insulating; porous evaporated films conduct heat poorly (k ~ 2 W/m/K, ESTIMATE) |
| LiH | 1.5 | melts 689 °C; hygroscopic | as Li₂O | a candidate to ask the target lab about **(ask)** |
| Li₃N | 1.3 | reacts with water | | brings ¹⁴N(p,γ) (1058 keV resonance, ≤ 7.6 MeV γ), below the window |
| LiPON (MEG II) | 0.4 | stable | sputtered | thick and rough; P and N add lines below the window |
| LiF | — | stable | easy | **excluded above 441 keV** (¹⁹F, TARGET_STUDY §3) |
| Li-Al, Li on Al | — | — | — | **excluded**: ²⁷Al(p,γ) 992 keV resonance and (p,p′γ) |

"Li per keV" is the ⁸Be γ₀ yield per keV of beam energy lost in the film, relative to Li₂O (`stacks.csv`: 1.07×10⁻¹¹
per keV for Li, 4.9×10⁻¹² for Li₂O); the other compounds scale by Li atoms per unit stopping at 1 MeV.

### 2.2 How thick (`out/target/options/stacks.csv`, E_p = 1.10 MeV unless stated)

| film | beam leaves at | γ₀ per proton | × baseline | 441 keV share | resonant (18.15) share |
|---|---|---|---|---|---|
| Li₂O 300 µg/cm² (1.5 µm), the FEAS baseline | 1039 keV | 2.96×10⁻¹⁰ | 1 | 0.60 % | 47 % |
| Li 10 µm | 990 keV | 1.24×10⁻⁹ | 4.2 | 0.61 % | 48 % |
| **Li 20 µm (Pierfrancesco)** | **872 keV** | **2.43×10⁻⁹** | **8.2** | **0.85 %** | 38 % |
| Li 20 µm at E_p 1.20 MeV | 988 keV | 2.10×10⁻⁹ | 7.1 | 0.61 % | 38 % |
| Li 40 µm | 596 keV | 4.31×10⁻⁹ | 14.6 | 3.3 % | 25 % |
| Li, stopping the beam | 0 | 2.3×10⁻⁸ | 78 | **77 %** | 5 % |

- The thick film integrates over the resonance, so the direct-capture (E1) share grows. The X17 normalisation here,
  as in FEAS, is per total γ₀ (ATOMKI 2022 reported the anomaly off resonance too). If the X17 came from the M1
  resonance only, the gain at 20 µm is ×6.7 instead of ×8.2.
- The 3D fit handles a known energy profile; the TARGET_STUDY §8 fit-bias test showed a drifting 441 share up to 20 %
  biases it by < 0.06 R_ATOMKI. At 0.85 % this is negligible.
- **Thickness uniformity and the exit energy matter less than for a thin target**: the yield per µC changes by 7 % for a
  10 % thickness change (§8).

## 3. Heat (`opt_thermal.py`)

**Model.** Axisymmetric finite-volume solver in (r, z) for a layered disk: the beam power is deposited at the depth where
the protons lose it (PSTAR stopping), k(T) per layer, an anisotropic graphite foil, contact conductances (dry clamp
5×10³–10⁴ W/m²/K; braze 2×10⁵; water 2×10⁴; micro-channels as an effective h), radiation from both faces.
**Checks:** a conduction-only thin disk agrees with the analytic Gaussian-source result to 0.7 % (103.7 vs 103.0 K);
the 10 µm Al disk of TARGET_STUDY §5 gives 97.6 °C against 95 °C from the earlier 1D model.

**Film temperature (°C) at E_p 1.10 MeV, σ = 2 mm** (`thermal_scan.csv`):

| option | 1 µA | 4 µA | 10 µA | 30 µA | 100 µA | 300 µA |
|---|---|---|---|---|---|---|
| A. Li₂O / 10 µm Al disk, clamped r ≥ 8 mm | 76 | 243 | 552 | — | — | — |
| B. Li₂O / 25 µm graphite foil (k_r 400, k_z 5) | 39 | 101 | 238 | 770 | — | — |
| C. Li₂O / 50 µm diamond, Cu clamp | 24 | 35 | 59 | 153 | 759 | — |
| D. Li 20 µm / 50 µm diamond | 24 | 35 | 58 | 150 | 724 | — |
| E. Li 20 µm / 300 µm diamond, clamped r ≥ 11 mm | 21 | 24 | 29 | 48 | 124 | 451 |
| **F. Li 20 µm / 1 mm diamond, dry clamp r ≥ 15 mm** | 20 | 22 | 24 | 32 | **63** | 166 |
| G. as F, brazed to a water-cooled Cu ring | 20 | 21 | 22 | 27 | 42 | 93 |
| H. Li 20 µm / diamond with micro-channels 300 µm under the face | 20 | 21 | 23 | 29 | 53 | 126 |
| I. Li 20 µm / 10 µm Ta / 300 µm diamond, brazed rim | 21 | 22 | 26 | 38 | 84 | 261 |
| J. Li₂O / 1 mm Cu, water on the back | 20 | 22 | 25 | 35 | 69 | 169 |

**Maximum current** (film at 150 °C for Li, 300 °C for Li₂O; `thermal_limits.csv`):

| option | σ = 2 mm | σ = 1 mm |
|---|---|---|
| A. 10 µm Al disk | 5.0 µA | 3.3 µA |
| B. graphite foil | 12 µA | 8.5 µA |
| C. Li₂O / 50 µm diamond | 53 µA | 38 µA |
| D. Li / 50 µm diamond | 29 µA | 22 µA |
| E. Li / 300 µm diamond | 119 µA | 93 µA |
| F. Li / 1 mm diamond, dry clamp | 268 µA | 220 µA |
| G. ... brazed rim | 485 µA | 343 µA |
| H. micro-channels | 352 µA | 210 µA |
| I. Li / Ta / 300 µm diamond | 181 µA | 128 µA |
| J. Li₂O / Cu, water | 548 µA | 311 µA |

**A focused spot.** If the beam collapses to σ = 0.5 mm at 4 µA: 10 µm Al disk 466 °C, 50 µm diamond 46–47 °C,
1 mm diamond 23 °C. Diamond does not need a wobbler for heat at LNL.

**Sensitivities** (`thermal_sensitivity.csv`, option F at 100 µA, 110 W):
- the clamp: h = 10³ → 3×10⁵ W/m²/K takes the film from 260 °C to 42 °C. **The clamp contact, not the diamond, is the
  bottleneck above ~30 µA**, so braze it (CVD-diamond gyrotron windows are brazed to Cu cuffs and edge-cooled the same way) or use indium;
- the diamond grade: k = 1000 instead of 1800 adds ~20 K at 100 µA;
- **the Li/diamond interface**: an interface conductance of 10⁴ W/m²/K adds 83 K at 100 µA, 10⁵ adds 9 K. Nobody seems to
  have measured evaporated Li on diamond **(gap)**; a carbide-forming metal layer (Ta, Mo, Ti) between them is the
  standard fix and is also wanted for hydrogen and charge (§5).

**Micro-channels** (`thermal_microchannel.csv`, ESTIMATE): 50 channels 200 × 300 µm at 400 µm pitch, 1 L/min: laminar
(Re ≈ 1300), h_wall ≈ 1.4×10⁴ and h_eff ≈ 2.7×10⁴ W/m²/K on the face, Δp ≈ 1.2 bar, ΔT_water 0.7 K at 50 W. The
300 µm face over a 200 µm channel at 3 bar sees 0.07 MPa (diamond: 400–1000 MPa). Thermal stress across the plate
(E α ΔT/(1−ν)) is ~20 MPa at 50 W. The real engineering issue is the diamond-to-metal water seal, not the diamond.

**Thin membrane with a beam stop** (the LNL recommendation): Li 20 µm / Ta 10 µm / diamond 50 µm, clamped at r ≥ 8 mm:
24 / 35 / 58 °C at 1 / 4 / 10 µA, I_max 30 µA (dry clamp), 40 µA (brazed); diamond 100 µm brazed: 76 µA. A 1 mm diamond of
r = 8 mm (§7.2): 91 µA dry, 590 µA brazed.

**Reading.** At LNL (≤ 4 µA, or ≤ 0.5 µA with the 20 µm Li) every diamond option is cold. The micro-channel plate
earns its complexity only above ~100 µA, and even there a 1 mm diamond brazed to a cooled ring matches it with no
water inside the target. Pierfrancesco's objection to the clamp on slide 7 is right for the Li film alone (20 µm of Li
cannot carry the heat sideways: k t = 1.7 mW/K against 1.8 W/K for 1 mm diamond), and that is why the backing must be
the conductor.

## 4. What the film and the backing emit (`opt_backing.py`, measured nuclear data)

**Inputs.** ⁷Li(p,p′γ)478 from the thick-Li yield of Bykov et al., ARI 175 (2021) 109821 (4.9×10⁶ /µC at 1.0 MeV, 15 %);
¹³C(p,γ)¹⁴N 556 keV resonance from Skowronski et al., PRC 111 064611 (2025) Table I (Γ = 34.9 keV, Γγ₀ = 9.1 eV, Γγ 11.8 eV);
¹²C(p,γ)¹³N 457 keV resonance (Γ 34 keV, ωγ 0.6 eV; 1953HU18 and the Felsenkeller 2023 re-measurement);
²⁷Al(p,γ) 632/773/992 keV resonances (ωγ 0.26/0.13/1.91 eV, the first two ESTIMATE) and (p,p′γ)843 (2 mb, ESTIMATE ×3).
Thick-target resonance yields are integrated analytically per step and checked against (λ²/2)ωγ/ε (992 keV: 1.14×10⁻⁹/p).

**Per ⁸Be γ₀** (`lines.csv`, `stacks.csv`):

| stack (E_p 1.10 MeV) | 478 keV (Li) | 843 keV (Al) | 2.37 MeV (¹²C) | 8.06 MeV (¹³C) | 10.8 MeV (²⁷Al) |
|---|---|---|---|---|---|
| Li₂O 300 / Al 10 µm (FEAS baseline) | 438 | ~140 | — | — | **4.8** |
| Li₂O 300 / diamond 50 µm | 438 | — | 3.1 | 0.34 | — |
| Li₂O 300 / Ta 10 / diamond | 438 | — | — | — | — |
| **Li 20 µm / diamond 1 mm** | 328 | — | 0.37 | 0.041 | — |
| Li 20 µm / ¹²C-enriched diamond (99.99 %) | 328 | — | 0.38 | 0.0004 | — |
| **Li 20 µm / Ta 10 µm / diamond** | 328 | — | — | — | — |
| Li 20 µm / Cu 1 mm | 328 | — | — | — | — |

- **None of these reaches the 13–18 MeV window.** They matter only as singles (trigger legs, DREAM load, Micromegas
  occupancy) and as accidental pairs. The Geant4 `bklines` run (L9) turns them into per-arm rates (§7.3).
- **The thick Li film makes the backing almost silent:** protons reach the diamond at 0.87 MeV, below most of what the
  thin film lets through, and per γ₀ everything is ×8 smaller.
- **Ta (or Mo, W) in front of the diamond removes the carbon lines** and is the only clean choice for where the beam stops.
  Heavy-element Coulomb excitation (¹⁸¹Ta 136/165 keV, Cu 670–1116 keV) is ≤ 1.1 MeV and was not quantified (ESTIMATE:
  small against the 478 keV line).
- **Neutrons: none.** ⁷Li(p,n) opens at 1.881 MeV, ¹³C(p,n) at 3.24, ⁶³Cu(p,n) at 4.2; ¹⁸¹Ta(p,n) (~1.0 MeV) is
  Coulomb-suppressed to < 10⁻¹² per proton. A HPGe near the target is safe (§8).
- **Charged particles**: ⁷Li(p,α)α (σ ≈ 8 mb, 8.7 MeV α) and ⁶Li(p,³He)α (~100 mb) on the film, backscattered protons.
  All stop in the chamber wall; they matter only for detectors inside the vacuum.

**Which backing is best** (all criteria):

| backing | heat (k, W/m/K) | leptons (X₀) | γ background | hydrogen | Li compatibility | charge | verdict |
|---|---|---|---|---|---|---|---|
| **CVD diamond** | **1800** | 12.2 cm | 2.37 / 8.06 MeV lines (or none behind Ta) | unknown **(gap)** | inert; adhesion unknown | insulator | **best, with a metal layer** |
| Ta (10 µm layer) | 57 | 0.41 cm | none | ≥ 3.4×10¹⁹ /cm² | excellent (Li containment metal) | conducts | **the beam stop on top of diamond** |
| Mo | 138 | 0.96 cm | none | similar to Ta (ESTIMATE) | excellent | conducts | alternative to Ta |
| Cu | 400 | 1.44 cm | none | blisters ~10¹⁹ | dissolves slowly in hot Li | conducts | thick + offset only |
| Al | 237 | 8.9 cm | **992 keV resonance, 10.8 MeV** | blisters ~10¹⁸ | **alloys with Li** | conducts | avoid where the beam is |
| graphite foil | 400 in plane, 5 across | 19 cm | as diamond | outgasses | inert | conducts | thin option only |
| Be | 200 | 35 cm | ⁹Be(p,γ) 330 keV resonance, (p,α), (p,d) | — | — | conducts | no; toxic |
| Si / SiC | 150 / 400 | 9.4 / 8.8 cm | ²⁸⁻³⁰Si(p,γ) lines | — | Li alloys with Si | semi | no |

## 5. Hydrogen and charge where the beam stops (`hydrogen.csv`)

- Peak fluence at the spot centre (σ = 2 mm): **2.1×10¹⁸ H/cm² per day per µA**.
- Days to blister onset at 1 µA (σ 2 mm): Al 0.5, Cu 4.7, **Ta ≥ 16** (no blisters seen up to 3.4×10¹⁹ at 600 °C; ≥ 6.7×10²⁰
  claimed), diamond **unknown**. At the ~0.12–0.5 µA the 20 µm Li needs, Ta lasts ≥ 30–130 days.
- Diamond: H is immobile in diamond at these temperatures; 1.2×10¹⁷ H/cm² at 350 keV blistered natural diamond only after
  a > 1400 °C anneal (Tech. Phys. 2006); "smart-cut" exfoliation needs implantation plus annealing. No data were found for
  10¹⁸–10²⁰ /cm² of ~1 MeV protons at 20–150 °C **(gap: a one-day irradiation of a diamond sample on AN2000/CN answers it)**.
- **Charge:** 1 µA stopping inside an insulator must leak through it. A metal layer that stops the beam (the range in Ta is 6 µm at
  0.87 MeV and 7.5 µm at 1.04 MeV, so 8–10 µm stops either) solves charge, hydrogen and Li wetting together.
- A beam wobbler over ±6 mm spreads the dose by ~×6 (ESTIMATE).

## 6. Vacuum: carbon, water, and lithium as a getter (`li_chemistry.csv`, `carbon_shift.csv`)

**Carbon.** Peterson & Laubert (PAC 1977) measured ~1 C atom retained per proton (~2 µg/cm²/h) in a diffusion-pumped
chamber, ~×10 less with a cooled shield or the target at 150 °C; Redigolo 2024 saw none with a LN₂ trap at 10⁻⁷ mbar.

| vacuum class (C per proton) | C per day at 1 µA | Li₂O 300, 14 d: γ₀ / 441 share | Li 20 µm, 14 d: γ₀ / 441 share |
|---|---|---|---|
| diffusion pumps, no trap (1) | 43 µg/cm² (9 keV) | ×1.06 / 1.1 % | ×0.85 / 2.3 % |
| cold shield or hot target (0.1) | 4.3 µg/cm² | ×1.06 / 0.6 % | ×1.00 / 0.9 % |
| LN₂ trap, 10⁻⁷ mbar (0.01) | 0.4 µg/cm² | ×1.01 / 0.6 % | ×1.00 / 0.85 % |

Carbon on the 168 keV-wide 18.15 MeV resonance is harmless with any trap. With the 20 µm Li at ~0.12 µA it is ×8 smaller
again. It matters for the 441 keV calibration target (TARGET_STUDY §7).

**Water and oxygen on metallic Li** (Hertz–Knudsen flux × sticking, ESTIMATE):

| partial pressure | H₂O: Li consumed per day | days to convert 20 µm | O₂ | CO₂ (s = 0.5) | N₂ (s = 10⁻³) |
|---|---|---|---|---|---|
| 10⁻⁶ mbar | 13.5 µm | 1.5 | 1.0 d | 4.6 d | 600 d |
| 10⁻⁷ mbar | 1.35 µm | 15 | 10 d | 46 d | — |
| 10⁻⁸ mbar | 0.14 µm | 150 | 100 d | 460 d | — |

- The products (LiOH, Li₂O, Li₂CO₃) stay on the target, so the Li is not lost: the yield per µC drops slowly as the film
  dilutes, and the 3D fit absorbs it (TARGET_STUDY §8: fully hydrated Li₂O biases it by +0.002).
- **Spec: water partial pressure ≤ 10⁻⁸ mbar at the target**, which in practice means a LN₂-cooled shroud around it
  (also the carbon trap), a bake of the chamber, and the target made or loaded without air exposure.
- Thin Li₂O hydrates too (LiOH): same spec.

## 7. Geant4 L9: leptons through the target assembly (big plastics)

**Runs** (2026-10-22, MX17_Full_Geant branch `lnl_target`, binary `mx17_full_sim_lnltgt_97a41fa`): per configuration
5×10⁵ X17 (m 16.8, W 18.15), 5×10⁵ M1 and 5×10⁵ E1 Born IPC at 18.15 MeV, 2×10⁷ ⁸Be γ (EPC); big plastics; plus one
10⁷-γ run of the backing lines (§7.3). Configurations in `lxplus/l9_configs.sh`.

**Analysis** (`opt_geant.py`): LNL-calibrated calorimetry, MM 15° + TOF, the opening angle and the pointing taken about
the target position. Reach: Asimov/Fisher fit in θ × |y| × n_down (M1, E1, γ₁ and EPC norms free, cosmics fixed), best
E_sum window, scaled so the baseline equals the FEAS §14 reference 3D fit (1.0 d at 1 µA; the raw fit gives 1.02 d, a
good anchor). γ₁ uses the baseline L2 templates everywhere. **Relative comparison**: the full template refit of the
chosen design is a follow-up.

### 7.1 Results

| configuration | X17 acc. | σ68 | pairs with a leg through the backing (σ68 of those) | EPC share of B | **days per µA** | days, same X17 rate |
|---|---|---|---|---|---|---|
| Li₂O 300 / Al 10 µm (FEAS baseline) | 0.162 | 4.8° | 76% (5.2°) | 0.9% | **1.00** | 1.00 |
| Li₂O 300 / Al 10 µm, target +12 cm | 0.088 | 4.8° | 52% (6.2°) | 2.5% | **1.50** | 1.50 |
| Li₂O 300 / diamond 50 µm, Cu ring | 0.124 | 5.4° | 70% (6.2°) | 4.3% | **1.17** | 1.17 |
| Li 20 µm / diamond 50 µm, Cu ring | 0.123 | 5.4° | 69% (6.3°) | 1.2% | **0.20** | 1.60 |
| Li 20 µm / Ta 10 µm / diamond 300 µm | 0.111 | 9.2° | 66% (12.4°) | 8.5% | **0.34** | 2.77 |
| Li 20 µm / diamond 1 mm, Cu ring (centre) | 0.090 | 9.0° | 58% (13.5°) | 11.2% | **0.37** | 3.06 |
| Li 20 µm / diamond 1 mm, target +12 cm | 0.067 | 8.1° | 37% (13.7°) | 5.1% | **0.34** | 2.76 |
| Li 20 µm / diamond micro-channel plate, +12 cm | 0.065 | 7.8° | 36% (13.5°) | 4.4% | **0.34** | 2.82 |
| Li₂O 300 / water-cooled Cu block, +12 cm | 0.087 | 15.1° | 51% (20.4°) | 11.5% | **2.89** | 2.89 |

- "Days, same X17 rate" divides out the film's ×8.2 γ₀ gain: it compares assemblies at equal signal rate.
- **Thin is right for LNL.** A 50 µm diamond at the centre costs ×1.17 against the 10 µm Al (σ68 5.4° vs 4.8°). The 20 µm
  Li on it reaches 3σ at R(ATOMKI) in **0.2 d per µA**.
- At equal X17 rate the 20 µm Li film is ×1.37 slower than Li₂O on the same backing (1.60 vs 1.17): the thick film
  integrates more direct (E1) capture, whose IPC is larger (α 4.4×10⁻³ vs 3.5×10⁻³) and flatter at large angles. Per µA it
  is still ×6 faster.
- **A 1 mm diamond costs ×1.9 per µA against 50 µm**, at the centre or 12 cm downstream: the legs that leave downstream
  cross it at grazing angles (σ68 of those pairs 13.5°, against 6.3° on 50 µm).
- **Moving it 12 cm downstream does not rescue ⁸Be** (unlike Demokritos' ⁴He, §6 there). Truth: at +12 cm still 37 % of
  selected X17 pairs have a leg leaving below 90° and crossing the diamond nearly edge-on; the offset also loses ×0.74
  of the acceptance. The ⁸Be pairs open at ~140°, so a leg at 75–90° is common.
- The water-cooled Cu block at +12 cm is the worst option (σ68 15°, 2.9 d): a thick metal backing must stay out of the
  leptons' way entirely.
- EPC from the backing stays ≤ 12 % of the background in the window even for 1 mm of diamond.

### 7.2 Can geometry rescue the 1 mm diamond? And the thin design with a beam stop

| configuration | X17 acc. | σ68 | pairs with a leg through the backing (σ68 of those) | EPC share of B | **days per µA** | days, same X17 rate |
|---|---|---|---|---|---|---|
| Li 20 µm / diamond 50 µm, Cu ring | 0.123 | 5.4° | 69% (6.3°) | 1.2% | **0.20** | 1.60 |
| Li 20 µm / diamond 1 mm, Cu ring (centre) | 0.090 | 9.0° | 58% (13.5°) | 11.2% | **0.37** | 3.06 |
| Li 20 µm / diamond 1 mm, target +12 cm | 0.067 | 8.1° | 37% (13.7°) | 5.1% | **0.34** | 2.76 |
| Li 20 µm / diamond 1 mm, target +18 cm | 0.062 | 8.6° | 37% (14.2°) | 2.2% | **0.32** | 2.62 |
| Li 20 µm / diamond 1 mm, r = 8 mm disk (centre) | 0.089 | 11.3° | 58% (17.3°) | 17.4% | **0.32** | 2.63 |
| Li 20 µm / diamond 1 mm, r = 8 mm, +12 cm | 0.084 | 11.4° | 50% (16.9°) | 3.8% | **0.27** | 2.22 |
| Li 20 µm / Mo 8 µm / diamond 50 µm | 0.131 | 6.6° | 71% (8.1°) | 5.2% | **0.22** | 1.78 |
| Li 20 µm / Ta 8 µm / diamond 50 µm | 0.135 | 7.9° | 72% (9.8°) | 4.3% | **0.24** | 1.95 |

- **No geometry rescues the 1 mm diamond for ⁸Be.** +18 cm (the arms' downstream edge) leaves 37 % of pairs with a
  leg through it and loses acceptance; a small r = 8 mm disk shortens the grazing path but brings the Cu ring close to the
  beam (σ68 11°). The best, r = 8 mm at +12 cm, is 0.27 d per µA: ×1.4 the thin membrane.
- **The thin design with a beam stop costs little**: 8 µm of Mo under the Li (σ68 6.6°, EPC 5 %) gives 0.22 d per µA, ×1.1
  the bare 50 µm diamond. Mo (X₀ 0.96 cm) scatters less than Ta (0.41 cm) at equal stopping: Ta 8 µm gives 0.24 d (σ68 7.9°), so
  **Mo is the better beam stop** unless its hydrogen tolerance turns out worse (no MeV data found for Mo: gap).
- So the thick, actively cooled diamond is a **high-current** option: per µA it is ×1.4–1.9 slower, which a machine giving
  ≥ 5–10× LNL's current repays many times over. At LNL the thin membrane wins on every count.

### 7.3 The backing γ lines in the detector (`opt_rates.py`, L9 `bklines`)

Per γ and per arm (big plastics): a trigger leg needs ≥ 2.4 MeV (2×10⁻³–2.6×10⁻³ for 4–11 MeV γ, 7×10⁻⁵ at 2.37 MeV,
0 below); a Micromegas hit 5×10⁻⁴ at 0.14–0.48 MeV rising to 1.5×10⁻³ above 2 MeV (`line_response.csv`). At the same X17
rate (baseline at 1 µA; 20 µm Li at 0.125 µA):

| target | backing legs /arm/s | Micromegas hits /arm/s | occupancy (1.2 µs) |
|---|---|---|---|
| Li₂O / Al 10 µm (baseline) | **23** (the 10.8 MeV line of the 992 keV resonance) | 640 | 7.7×10⁻⁴ |
| Li 20 µm / diamond 1 mm | 0.24 | 300 | 3.5×10⁻⁴ |
| Li 20 µm / Ta 10 µm / diamond | 0 | 290 | 3.5×10⁻⁴ |

Cosmics make ~15 legs/arm/s, so **the Al backing of the FEAS baseline was the largest single-arm trigger source**; any
diamond or Ta option removes it. The 478 keV line costs < 0.1 % Micromegas occupancy.

## 8. Monitoring the target on the beam (`opt_monitor.py`)

**PIGE, 478 keV** (`pige.csv`; full-energy efficiency at 10 cm: 60 % HPGe 4×10⁻³, 3″×3″ LaBr₃ 6×10⁻³, ±30 %):

| film, 1 µA | 478 γ/s (4π) | HPGe at 50 cm: peak cps, time to 1 % | LaBr₃ at 50 cm |
|---|---|---|---|
| Li₂O 300 | 8.1×10⁵ | 130 cps, 77 s | 190 cps, 52 s |
| Li 20 µm | 5.0×10⁶ | 800 cps, 13 s | 1200 cps, 8 s |

- **Sensitivity** (`pige_sensitivity.csv`): 10 % less Li → −9 % (Li₂O) / −7 % (Li 20 µm) of 478 yield; 10 µg/cm² of
  carbon in front → −0.6 %. PIGE tracks the Li content; it cannot see carbon at a useful level.
- **Is germanium needed?** For Li alone, no: LaBr₃ is enough and takes higher rates. For contaminants, yes: ²³Na
  (440 keV), ¹⁰B(p,αγ) (429 keV) and ⁷Li (478 keV) sit within 50 keV, and ¹⁹F (110/197 keV) needs a good low-energy
  response. **A HPGe is safe here**: nothing makes neutrons below E_p = 1.88 MeV (§4), so there is no neutron damage.
  Keep total rates < 3×10⁴ /s: 50–100 cm, or a collimator.
- **Carbon and oxygen**: a Si surface-barrier detector at a backward angle inside the chamber sees elastically scattered
  protons; the C and O edges in front of the Li give the build-up and the oxidation directly (RBS/EBS).
- **The ⁸Be γ₀ line shape** in a large LaBr₃ or NaI (ATOMKI's trick) tracks the energy profile in the film.
- Placement: outside the chamber in a gap between the arms or at 0°/backward; the 1 mm diamond plus Ta absorb ~3 % of
  478 keV γ, so a HPGe behind the target (0°) also works.

## 9. "441 keV γ" and a thicker Micromegas window (`al_window.csv`)

Two readings of the question, and the same answer for both:

| Al thickness | 478 keV absorbed | 17.6 MeV absorbed | 18 MeV γ converted to e⁺e⁻ | Highland θ₀ at 8.6 MeV |
|---|---|---|---|---|
| 60 µm (for scale; today's window is 60 µm aluminised mylar) | 0.1 % | 0.04 % | 0.05 % | 1.7° |
| 1 mm | 2.2 % | 0.6 % | 0.9 % | 8.0° |
| 5 mm | 11 % | 3.0 % | 4.4 % | 19° |

- **If "441 keV γ" means the 17.64 MeV γ from the 441 keV resonance:** no window can stop 17 MeV γ, and every mm of Al
  converts ~1 % of them into pairs at the Micromegas and adds ~8° of scattering to the real leptons. Above 441 keV the
  17.64 MeV line is 0.6–0.9 % of γ₀ (§2.2); a dedicated 441 keV run is a physics point (ATOMKI saw no anomaly there) and
  the energy calibration.
- **If it means sub-MeV γ (the 478 keV Li line, the only intense one):** 1 mm of Al removes 2 %. The Micromegas gas is
  nearly blind to them anyway; the Geant4 `bklines` run gives the per-γ Micromegas hit probability (§7.3).
- So: keep the window thin.

## 10. Other machines

PTB PIAF, PSI's MEG II Cockcroft–Walton (it has run ⁷Li(p,e⁺e⁻)⁸Be on LiPON) and ATOMKI's 2 MV Tandetron (200 µA)
are in `survey/proton/PROTON_SURVEY.md`. The survey's conclusion stands: above a few µA the target, not the
accelerator, sets the reach. **This study raises the target cap**: a diamond-backed 20 µm Li target is thermally fine to
~270 µA with a dry clamp (~480 µA brazed), i.e. ×8 × (60–120) in ⁸Be rate over the thin Li₂O at 4 µA, if hydrogen,
adhesion and Li chemistry hold. The survey's 20 µA "cooled" cap (ESTIMATE) is therefore conservative for ⁸Be.

## 11. What Geant4 can and cannot simulate here

`lxplus/g4tendl_check.py` → `g4tendl_check.csv` reads G4TENDL1.4, the proton data the `*_AllHP` physics lists use below
200 MeV:

| nucleus | what G4TENDL has below 1.2 MeV |
|---|---|
| ⁷Li | a smooth total inelastic σ (5–8 mb at 0.8–1.1 MeV, the (p,α) channel); **no 441 or 1030 keV resonance, no (p,γ), no (p,p′) 478 keV** |
| ¹²C, ¹⁶O | **zero** below 4.8 MeV |
| ¹³C | one point per MeV (63 µb); **no 556 keV resonance** (true peak ~1.4 mb) |
| ¹⁹F, ²⁷Al, ¹¹B | 2–6 points; no resonances |
| ⁶³Cu, ¹⁸¹Ta | ~0 |

**So Geant4 cannot produce the target's own γ-rays at these energies, with any physics list.** The method used here, and
the only reliable one: nuclear yields from measured cross sections and resonance strengths (§4, TARGET_STUDY §3), and
Geant4 for everything electromagnetic: the transport of those γ-rays, external conversion, the leptons' scattering and
energy loss in the film, backing, holder and chamber, and the detector response.

| quantity | how reliable | source |
|---|---|---|
| lepton scattering, energy loss, EPC in the target assembly | good (Geant4 EM, validated at n_TOF) | L9 |
| detector response to a γ line | good | L3/L8/L9 |
| ⁷Li(p,γ) γ₀/γ₁ yields | good (Zahnow 1995, ±10 %) | target_model |
| ⁷Li(p,p′γ) 478 keV | ±15 % | Bykov 2021 |
| ¹²C, ¹³C(p,γ) resonances | ±10–20 % | Skowronski 2025, 1953HU18 |
| ²⁷Al(p,γ) 632/773 keV, (p,p′)843 | ×2–3 | ESTIMATE |
| Coulomb excitation of Ta/Cu | not computed | — |
| ¹⁹F α_π below E_cm 1.0 MeV, ¹¹B(p,γ) | ×2–3 | TARGET_STUDY |
| temperatures | ±20 % at fixed contact; the contacts dominate | opt_thermal |
| H blistering of diamond, Li adhesion on diamond | **unknown** | gap |
| Li/Li₂O reaction rates with residual gas | ×3 (sticking) | ESTIMATE |

## 12. Gaps, follow-ups and questions

**Measurements that would close the gaps (cheap, on AN2000/CN or a bench):**
1. Irradiate a CVD diamond sample (bare and Mo/Ta-coated) with ~1 MeV protons to 10¹⁹–10²⁰ /cm² at 20–150 °C; inspect for
   blisters/graphitisation and measure its thermal contact afterwards.
2. Evaporate 20 µm Li on Mo/Ta-coated diamond; measure adhesion and the interface thermal resistance (laser flash or a
   heater test in vacuum).
3. Run a Li target at a known water partial pressure and follow the 478 keV PIGE yield and EBS: calibrates §6.
4. Mount a 50–100 µm diamond membrane on a cooled Cu ring (clamp and braze) and thermal-cycle it; for a high-current
   machine, braze a 0.3–1 mm disk (as the gyrotron-window makers do).

**Simulation follow-ups:**
- Rerun the reference 3D fit (FEAS §14) with the chosen target's full template set (L9 gives X17, M1, E1 and EPC; γ₁ and
  the cosmics geometry with the offset are approximations here).
- A holder/cooling-ring CAD → Geant4 once the design exists; the chamber at +12 cm with the real LNL beam line.
- Update `survey/proton/proton_reach.py` CAP for cooled targets once the diamond/H question is answered.

**Questions for Pierfrancesco and Stephan:**
1. Is 20 µm Li made in situ (evaporated in the chamber) or moved under vacuum? Does LNL have a Li evaporator?
2. Can LNL's target lab put 8 µm of Mo or Ta on a CVD diamond membrane and mount it on a cooled ring? Who supplies the diamond?
3. Is a LN₂ shroud around the target possible in the planned chamber, and what water partial pressure is typical there?
4. Is there a HPGe that can sit 0.5–1 m from the target during the run?
5. Can AN2000 or CN do the diamond irradiation test (item 1) before the run?

## 13. Code, runs, outputs

| what | where |
|---|---|
| heat | `lnl/target/opt_thermal.py` → `out/target/options/thermal_{check,scan,limits,sensitivity,microchannel}.csv` |
| film and backing yields, hydrogen, Li chemistry | `lnl/target/opt_backing.py` → `stacks.csv`, `lines.csv`, `hydrogen.csv`, `li_chemistry.csv` |
| PIGE, carbon, Al window | `lnl/target/opt_monitor.py` → `pige.csv`, `pige_sensitivity.csv`, `carbon_shift.csv`, `al_window.csv` |
| Geant4 L9 analysis | `lnl/target/opt_geant.py` → `geant_acceptance.csv`, `geant_reach.csv` |
| G4TENDL contents | `lnl/target/lxplus/g4tendl_check.py` → `g4tendl_check.csv` |
| Geant4 branch | MX17_Full_Geant `lnl_target` (from `demokritos`): multi-layer `--backing`, Diamond/Water/W/Pd/Ni/Ag/Au/Si/SS; binary `bin/mx17_full_sim_lnltgt_97a41fa` |
| runs | `$E/L9/<sample>_<config>` (E = `/eos/experiment/ntof/data/x17/lnl`), merged in `$E/target/sel_l9/` |

## Sources

- T. Bykov et al., Appl. Radiat. Isot. 175 (2021) 109821 (⁷Li(p,p′γ) 478 keV thick-Li yield and σ, 0.7–1.85 MeV).
- J. Skowronski et al., Phys. Rev. C 111, 064611 (2025), arXiv:2512.17288 (¹³C(p,γ) 551/556 keV resonance parameters).
- ¹²C(p,γ)¹³N 457 keV resonance: ENSDF (1953HU18), Felsenkeller 2023 (arXiv:2306.09022).
- Budker INP, "In situ blistering observations on metals under proton irradiation", RSI 2017 (Cu ~10¹⁹, Ta > 3.4×10¹⁹ /cm²);
  Metals 7, 558 (2017).
- Hydrogen in diamond: Tech. Phys. 51 (2006) (350 keV H, 1.2×10¹⁷ /cm², blistering after annealing).
- J. Peterson and P. Laubert (PAC 1977): carbon build-up ~1 C per proton, ×10 less with a cold shield or a hot target.
- L. Redigolo et al., J. Phys. G 51, 075106 (2024) (no carbon with a LN₂ trap at 10⁻⁷ mbar).
- Everything in `TARGET_STUDY.md` Sources.
