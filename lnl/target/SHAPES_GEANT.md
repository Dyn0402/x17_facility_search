# The two LNL target designs in Geant4: Pierfrancesco's Cu hemisphere and the flat diamond window

Started 2026-10-27 (overnight run, laptop dylan-Yoga + lxplus). Dylan asked for a full Geant4 study of the two designs on
the table, and for anything that could go wrong: contamination, material backgrounds nobody is thinking of, the
trigger rate against what DREAM can take (from n_TOF), and the γ load on the scintillators, especially with the big
plastics. Choices (Dylan, 27 Oct): the Cu hemisphere at **200 µm** (300 µm, the CN-paper value, as a variant), 20 µm Li
inside; the diamond window as decided on 26 Oct (Ø20, 200–300 µm in 0.5 mm Ti rings) **both tilted 45° and
perpendicular**; **both E_p = 1.03 and 1.10 MeV**; detectors **as built and with the big plastics**.

Earlier estimates of the same shapes (ray-trace of L9 legs, TARGET_OPTIONS §17–18) are replaced here by Geant4.
Code: `lnl/target/shapes/` (§9). Facts not found publicly are **(ask)**; analytic stand-ins are **ESTIMATE**.

## 0. Bottom line (2026-10-27)

1. **Build the 45° diamond window; drop the Cu hemisphere.** Geant4 (run L10, big plastics, 1.10 MeV), days per µA to
   3σ at R(ATOMKI):

   | | σ68 | days per µA, big plastics | as built |
   |---|---|---|---|
   | **window 45°, Ø20, 200 µm diamond, Ti rings** | 9.1° | **0.27** | 1.5 |
   | window 45°, 300 µm | 9.7° | 0.28 | 2.5 |
   | window 0°, 200 µm | 10.7° | 0.36 | 3.3 |
   | **Cu hemisphere 200 µm** (Pierfrancesco) | **22°** | **2.4** | 3.2 |
   | Cu hemisphere 300 µm / glued on the steel tube | 24° / 22° | 3.4 / 1.7 | 4.1 / 4.3 |
   | *flat Li 20 / Mo 8 / C 50 in a CFRP chamber (L9)* | 6.6° | 0.22 | — |

   The copper shell is crossed by every lepton (tangentially near 90°) and converts the ⁸Be γ: EPC is 46 % of the
   background. The §17 ray-trace (0.40 d) was far too kind. 45° beats 0° by ×1.35. 300 µm costs only 7 %.
   **The window is +22 % against the flat design only because of its 55 mm Al end piece** (§4.1): without it
   σ68 drops from 9.1° to 6.2° (≈ 0.21 d/µA), the bare window is 5.7°. Mount it on a wide, short adapter.
2. **1.03 vs 1.10 MeV:** 1.03 is 15–18 % slower (more direct capture), but it avoids the one serious contamination
   trap (item 4). Default 1.10, with a short check of the 6.13 MeV line; 1.03 if fluorine shows up.
3. **DREAM copes, if the single-arm output is prescaled.** With 20 µm Li the trigger is made by the ⁸Be γ themselves
   (×8 per µA against the FEAS film): 720 legs/s at 1 µA (big plastics, window), 1160 for the dome. Live time 83 % at
   P = 1, 97 % at P = 10. Pairs (never prescaled) stay at 25–80 /s up to 4 µA. 478 keV never makes a leg.
4. **Scintillators: no saturation, big plastics included.** The film makes 5 × 10⁶ γ/s/µA of 478 keV (×330 the
   signal line): 2.9 × 10⁵ hits/s per µA in each big slab, all below 311 keV, 0.5 µA anode current at 4 µA, 12 %
   pile-up of +0.03 MeV. Above the leg threshold: ~900 /s per µA.
5. **Three new things to watch:**
   - **the window's Mo K x-rays** (17.5 keV, ~1.4 × 10⁷ /s/µA, PIXE ESTIMATE ×2–3) cross the diamond and reach the
     Micromegas: 16 % occupancy per arm per µA. Run ≤ 0.5 µA, or put 50 µm of Cu on the MM windows; the dome keeps its
     Cu x-rays (§7);
   - **fluorine at the Li/stop interface at 1.10 MeV**: the beam leaves 20 µm Li at 872 keV, the strongest
     ¹⁹F(p,αγ) resonance; 1 µg/cm² gives 60 % of the γ₀ rate in 6–7 MeV γ. No fluoride cleaning, no PFPE oil (§3);
   - **the 0° window's Mo margin**: without Li a 1.10 MeV beam needs 7.5 of the 8 µm (at 45°: 11.3 µm).
6. **Harmless, checked:** no beam neutrons (all thresholds above 1.88 MeV); α-induced neutrons ~40 /s/µA; Na, N, B, C
   contaminants at any plausible level; ⁷Be activation; H in the stop over a 3σ run (~0.3 µA·d against ~10¹⁸–10¹⁹ H/cm²
   blistering).
7. **Current:** the window with the big plastics reaches 3σ at ATOMKI in 0.28 d at 1 µA, 1.1 d at 0.25 µA. With the
   x-rays, 0.5 µA (0.55 d, 8 % MM occupancy) is a reasonable working point.

**Update 2026-10-27, run L11 (§10): his ogive, the light shells, the window's tube.** Days per µA (big plastics, 1.10 MeV):
- **Pierfrancesco's ogive in Be 300 µm + Mo 8 µm is the fastest target simulated: 0.15 d (σ68 7°)**; Al 300 µm + Mo 0.26; Cu
  0.94 (×2.6 better than his hemisphere, EPC 23 %). Its flank Li doubles γ₀ per proton but puts 28 % of it at 17.64 MeV
  (69 % at 1.03 MeV); with the Li masked to the tip (flat yields) the Be ogive gives 0.20 d.
- **His cup in Be + Mo: 0.29 d** (Cu: 2.4).
- **The window's tube can only be made lighter, not moved out of view**: on a Ø20 × 0.5 mm Be end piece the window gives
  **0.22 d** (Al 0.27); the "wide adapter" gives 0.37. The flat L9 design in a chamber that holds vacuum (1 mm × 300 mm) is 0.28.
- The Mo liner's K x-rays cross 200 µm of Be as they cross the diamond: 15 % MM occupancy per arm per µA for the Be ogive.


---

## 1. The two designs as simulated

Both close the beam pipe: vacuum on the beam side, air outside, no chamber. The beam (+y, σ = 2 mm, not tracked)
hits the film; pair and γ vertices are drawn on the film where the spot lands, uniform through its depth.

| | Cu hemisphere ("dome") | diamond window ("window") |
|---|---|---|
| film | Li 20 µm (1068 µg/cm²) lining the inside | Li 14 µm along the normal at 45° (19.8 µm along the beam); 20 µm at 0° |
| beam stop | the Cu shell (range 5.8 µm at 0.87 MeV) | Mo 8 µm (range 5.3 µm at 0.87 MeV) |
| structure | hemisphere R 11 mm, 200 µm (300 µm variant), Cu rim 4 × 5 mm at the equator | CVD diamond 200 µm (300 µm variant), aperture Ø20, Ti rings 0.5 × 5 mm on both faces, 0.1 mm epoxy |
| mount | grey flange r 15–33 mm, y −27…−16 (PVC assumed), grey tube r 21–24 to −165 mm, KF clamp, DN40 steel | 55 mm Al end piece (0.5 mm, cut on the window plane), Al reducer, then the same line 39 mm further back |
| variant | R 17.5 glued straight on the DN40 steel tube (his 26 Oct suggestion) | tilt 0° and 45°, 200 and 300 µm |

The line upstream is the photographed one (TARGET_OPTIONS §18): DN40 steel to −620 mm and the DN63 flanges, as coaxial
tubes. The valve, tees, bellows and floor stand are not in Geant4: no accepted lepton crosses them (§18), and they only
scatter γ.

Geant4: MX17_Full_Geant branch **`lnl_shapes`** (from `lnl_target`), `--shape dome|window`, `--dome Mat:R:t_um`,
`--dome-rim w:h`, `--win-plane R:tilt`, `--win-ring Mat:t:w`, `--win-glue mm`, `--win-endpiece Mat:t:len`,
`--line Mat:rin:rout:y0:y1,...`. Overlap check clean for every configuration. Binary `bin/mx17_full_sim_shapes_39662ea`.

## 2. Runs (L10, 2026-10-27)

Per configuration × detector (as built `asb`: 16 SiPM bars, two 20 × 30 × 2 cm plastics, LS; big plastics `bigP`:
75 × 75 × 5 cm slab, 20 bars, no LS, as every earlier LNL big-plastic run):
- X17 (m 16.8, W 18.15), Born M1 and E1 IPC at 18.15 (γ₀) and at 15.1 (γ₁): 5 × 10⁵ each;
- 2 × 10⁷ ⁸Be γ (18.15, 17.64, 15.1, 14.6 MeV, equal mix): EPC, legs, two-arm triggers.

Plus γ-line response libraries (26 lines 0.2–17.64 MeV, 2.6 × 10⁷ γ) for the dome and the 45° window, both
detectors, and K x-ray lines (4.5, 8.05, 8.9, 17.5, 19.6 keV; 4 × 10⁶) for the dome and both windows.
Configurations: `shapes/lxplus/l10_configs.sh`. Output `/eos/experiment/ntof/data/x17/lnl/L10/`, merged
`…/lnl/target/sel_l10/`.

Analysis as TARGET_OPTIONS §7 (LNL-calibrated calorimetry, MM 15° + TOF, opening angle about (0, 0, 0), Asimov/Fisher
in θ × |y| × n_down, best E_sum window), but each configuration uses its own γ₁ templates and the yields of its own
film at each E_p. Reach is the raw fit (no anchoring): the references re-run the same way give 1.01 d (FEAS
baseline, big plastics; FEAS §14 says 1.0) and 0.217 d (the L9 flat design; L9 said 0.22).

## 3. What the beam makes besides ⁸Be (`shapes_backgrounds.py` → `out/target/shapes/backgrounds_inventory.csv`)

Per µA (6.24 × 10¹² p/s), the window at 45° (the dome is within 2 %: the same Li along the beam). Measured cross
sections unless marked.

| reaction | 1.03 MeV | 1.10 MeV | what it does |
|---|---|---|---|
| ⁷Li(p,γ₀)⁸Be (signal line; direct share 71 % / 61 %) | 1.4 × 10⁴ /s | 1.5 × 10⁴ /s | the measurement |
| ⁷Li(p,γ₁)⁸Be (15.1/14.6 MeV) | 3.0 × 10⁴ /s | 3.0 × 10⁴ /s | γ₁ IPC background; most of the trigger legs |
| ⁷Li(p,p′γ) **478 keV** (Bykov 2021) | 3.9 × 10⁶ /s | **5.0 × 10⁶ /s** | ×330 the γ₀ rate: singles, PMT current, MM hits (§6) |
| ⁷Li(p,α)α, ⁶Li(p,α)³He (NACRE S-factors) | 2.4 / 5.3 × 10⁶ /s | 2.6 / 5.3 × 10⁶ /s | charged, stopped in the film/stop; no γ |
| ⁶Li(p,γ)⁷Be (5.6 MeV) | 260 /s | 270 /s | negligible; ⁷Be activity ≈ 4 Bq after 10 days |
| α-induced n: ⁷Li(α,n)¹⁰B, ¹³C(α,n) in the diamond | ~40 n/s | ~45 n/s | ESTIMATE ×3; ~10⁻³ n/cm²/s at the arms: nothing |
| **PIXE**: Mo Kα 17.5 keV (window) | 8 × 10⁶ /s | **1.4 × 10⁷ /s** | escapes through the diamond into the MM (§7). ESTIMATE ×2–3 |
| PIXE: Cu Kα 8.05 keV (dome) | 8 × 10⁸ /s | 1.3 × 10⁹ /s | absorbed in the 200 µm Cu: none reaches an MM (§7) |

No neutrons from the beam: ⁷Li(p,n) opens at 1.881 MeV, ⁶⁵Cu(p,n) at 2.17, ¹³C(p,n) at 3.2, Mo (p,n) above 2 MeV.
Cu and Mo (p,γ) and Coulomb excitation at < 0.9 MeV are below 10⁻¹⁰ per proton (Coulomb barrier ~7 / 9 MeV):
< 10³ γ/s, against 5 × 10⁶ of 478 keV.

**Contamination** (`contaminant_levels.csv`; the level at which each line reaches 1 % of the γ₀ rate, uniform in the
film):

| contaminant | line | level for 1 % of γ₀ | where it comes from | verdict |
|---|---|---|---|---|
| ¹⁹F (uniform) | 6.13/6.92/7.12 MeV γ; 6.05 MeV E0 pairs | F/Li = 2.5–3.5 × 10⁻⁵ | LiF in the Li, PTFE, Viton | trigger legs only; pairs far below the window |
| **¹⁹F layer at the Li/stop interface** | 6–7 MeV γ | **1 µg/cm² → 60 % of γ₀ at 1.10 MeV**, 1.5 % at 1.03 | fluoride cleaning or etching of the Mo/Cu, PFPE pump oil (Fomblin) on the stop before the Li goes on | **the exit energy at 1.10 MeV (872 keV) is the strongest ¹⁹F(p,αγ) resonance** |
| ¹⁹F layer on the beam face | 6–7 MeV γ | 1 µg/cm² → 3–4 % of γ₀ | PFPE back-streaming, Viton | singles; watch the 6.13 line |
| ¹⁵N (as Li₃N) | 4.44 MeV γ (897 keV res., ωγ 362 eV) | N/Li = 0.8 % | Li reacts with N₂ in air within minutes | harmless, visible in the singles |
| ¹⁴N | ¹⁴N(p,γ)¹⁵O, 1058 keV res. | N/Li = 3 % (1.10 only) | same | harmless |
| ²³Na | 440 keV, 1.63 MeV, capture γ ≤ 12.7 MeV | Na/Li = 10⁻⁵ (440 keV), 0.26 % (12.7 MeV) | Li metal carries 20–200 ppm Na **(check the vendor CoA)** | singles only; the capture IPC sits below the window |
| ¹¹B | 16.9 MeV γ₀ and its IPC (inside the window) | B/Li = 5–6 % | BN crucibles for Li evaporation, borosilicate | harmless at any plausible level (ppm) |
| C (cracked hydrocarbons, Li₂CO₃) | — | 10 µg/cm² shifts the beam by 2.6 keV | pump oil, CO₂ | harmless (TARGET_OPTIONS §6) |

Nothing a contaminant plausibly makes reaches the 13–18 MeV E_sum window with a signal-like opening angle. Boron
would, at a level (percent) no target will carry. Fluorine is the only contaminant that can change the trigger rate,
and only as a layer at the Li/stop interface at 1.10 MeV.

## 4. Geant4: the leptons through each design (`shapes_geant.py` → `geant_reach.csv`, `geant_acceptance.csv`)

X17 acceptance × efficiency (MM 15° + TOF), σ68 of the reconstructed opening angle, and **days per µA to 3σ at
R(ATOMKI)** (3D fit, best E_sum window; in brackets the EPC share of the background in the fit window):

| configuration | big plastics: acc, σ68 | days, 1.03 MeV | days, 1.10 MeV | as built: acc, σ68 | days, 1.03 | days, 1.10 |
|---|---|---|---|---|---|---|
| **window 45°, 200 µm** | 0.152, 9.1° | 0.31 (5 %) | **0.27** (6 %) | 0.022, 9.3° | 1.6 | **1.5** |
| window 45°, 300 µm | 0.148, 9.7° | 0.33 (5 %) | 0.28 (6 %) | 0.022, 9.8° | 2.9 | 2.5 |
| window 0°, 200 µm | 0.142, 10.7° | 0.42 (10 %) | 0.36 (11 %) | 0.018, 11.7° | 3.8 | 3.3 |
| window 0°, 300 µm | 0.138, 11.4° | 0.48 (9 %) | 0.41 (10 %) | 0.017, 12.1° | 2.7 | 2.4 |
| **Cu dome 200 µm** (R 11, rim, grey flange) | 0.104, **22.0°** | 2.8 (45 %) | **2.4** (46 %) | 0.018, 27.4° | 3.4 | **3.2** |
| Cu dome 300 µm | 0.087, 24.2° | 3.9 (60 %) | 3.4 (61 %) | 0.016, 30.0° | 4.4 | 4.1 |
| Cu dome 200 µm, R 17.5, glued on the steel tube | 0.113, 22.3° | 1.9 (49 %) | 1.7 (51 %) | 0.016, 27.4° | 4.7 | 4.3 |
| *flat Li 20 / Mo 8 / C 50 µm, CFRP chamber (L9)* | 0.131, 6.6° | 0.26 (5 %) | 0.22 (5 %) | — | — | — |
| *FEAS baseline, Li₂O 300 / Al 10 µm* | 0.162, 4.8° | 0.87 (1 %) | 1.01 (1 %) | 0.023, 5.0° | 9.7 | 11.5 |

The as-built column is statistics-limited: 2 % acceptance leaves ~10⁴ X17 and a few hundred selected IPC per
configuration, so its days move by ±30–50 % between neighbours (e.g. 0° 200 vs 300 µm). Read it as "×5–6 the big
plastics for the window, ×1.3 for the dome". The big-plastic column is good to ~10 %.

**Reading.**
1. **The Cu dome is out: ×9 the window's days with the big plastics (2.4 vs 0.27 d/µA).** The ray-trace of §17
   (13.8°, 0.40 d) was far too kind, for two reasons Geant4 has and the trace did not:
   - every lepton crosses the shell, and legs near 90° from the apex run nearly tangent to it (√(2Rt) ≈ 2 mm of Cu each
     way, ~30 % X₀); a calibration fitted on flat foils cannot extrapolate there. σ68 is 22° for legs going upstream
     *and* downstream (truth split in `geant_acceptance.csv`);
   - **the shell converts the ⁸Be γ (EPC)**: 46 % of the background in the fit window is external conversion in the
     Cu, against 5 % for the window. EPC pairs have the IPC-like large-angle tail once one leg scatters.
   - Gluing the cup straight onto the steel tube (no rim, larger R) helps a little (1.7 d) but not the factor.
   - With the as-built arms the gap shrinks (3.2 vs 1.5 d): the as-built resolution is limited by the small plastics'
     acceptance, not the target. Only an Al/Be cup with a Mo liner could rescue the idea (§17's light domes); not run.
2. **The window: keep it at 45°.** 0° costs ×1.35 (0.36 d): the rings and the end-piece wall lie in the plane of the
   90° leptons, and EPC doubles (11 %). 300 µm costs +7 % (0.28 d) against 200 µm, cheap insurance for the vacuum
   wall.
3. **The 45° window is +22 % against the flat L9 design (0.27 vs 0.22 d), σ68 9.1° vs 6.6°, and the 55 mm Al end
   piece is the cause** (§4.1): without it σ68 is 6.2°, the bare window 5.7°.
4. **1.03 MeV costs +15–18 % against 1.10 MeV** for every Li-20 configuration: the direct (E1) share is 71 % against
   61 %, and E1 IPC is the broader background. The fluorine trap (§3) and the Mo margin (§8) argue the other way.

### 4.1 Where the window's extra degrees come from (diagnostic runs, X17 only, big plastics, 2026-10-27)

| window 45°, 200 µm | acceptance | σ68 | σ68, legs going upstream / downstream |
|---|---|---|---|
| as designed (Ti rings, 55 mm Al end piece 0.5 mm, grey line behind) | 0.152 | 9.1° | 8.7 / 9.2° |
| rings ~0 (1 µm) | 0.155 | 8.7° | 8.5 / 8.8° |
| end piece 1 mm CFRP instead of 0.5 mm Al | 0.151 | 8.3° | 8.0 / 8.4° |
| **no end piece** (rings kept, line behind) | 0.154 | **6.2°** | 5.6 / 6.4° |
| **bare window** (no end piece, rings ~0, no line) | 0.158 | **5.7°** | 5.3 / 5.8° |
| *flat L9 design in its CFRP chamber* | 0.131 | 6.6° | 3.9 / 8.1° |

**The end piece is the whole problem.** The leptons that leave toward the arms at 90–140° cross the 0.5 mm Al tube wall
(r = 10 mm) at grazing incidence, several mm of Al each. CFRP 1 mm only halves it. The Ti rings cost 0.4°. The window
itself (Mo 8 + diamond 200 µm at 45°) is at 5.7°, **better than the flat design** (6.6°, whose downstream legs cross
the 50 µm membrane and the Cu ring edge-on). On the σ68 → days relation of the full runs, 6.2° is ≈ 0.21 d/µA: the
window would match or beat the flat design.

So **the tube that carries the window must stay out of the leptons' view**: keep the window at the mouth of a wide,
short adapter instead of at the end of a Ø20 tube. The tube is in view for legs between ~90° and ~140°, so at
r = 10 mm anything within ~12 mm behind the window plane (y > −r·cot 40°) is seen. Options to simulate next: a conical
or stepped Al/CFRP adapter that opens from Ø20 to ≥ Ø60 within a few mm; the window directly on the grey flange (the
16 mm end piece of TARGET_OPTIONS §18); a thin (≤ 0.2 mm) Ti or Al bellows.

## 5. Trigger and DREAM against the beam current (`shapes_rates.py` → `daq_live.csv`, `days_vs_current.csv`)

Legs per arm from the Geant4 libraries × the line spectrum, cosmic legs and two-arm triggers from L4, accidentals
with 20 ns; DREAM τ = 298 µs non-paralysable (live = 1/(1 + fτ), max 3.35 kHz; nTof_x17_DAQ report). E_p 1.10 MeV
(1.03: −5 %):

| | arm legs /s at 1 µA (beam + 88 cosmic) | pairs /s at 1 µA | live at P = 1: 0.25 / 1 / 4 µA | live at P = 10: 1 / 4 µA |
|---|---|---|---|---|
| window, big plastics | 720 | 25 | 94 / 83 / 57 % | 97 / 92 % |
| dome, big plastics | 1160 | 36 | 91 / 75 / 44 % | 96 / 87 % |
| window, as built | 250 | 3.8 | 98 / 93 / 79 % | 99 / 97 % |
| dome, as built | 450 | 5.9 | 96 / 88 / 67 % | 99 / 95 % |

- **The legs are the ⁸Be γ themselves** (γ₁ at 15 MeV twice as many as γ₀): 1.4 % of them make a leg with the big
  plastics, 2.4 % in the dome, whose Cu converts them into charged particles. With 20 µm Li there are ×8 more ⁸Be γ per
  µA than with the FEAS Li₂O film, so the legs are ×4–5 the FEAS §14.1 table at the same current.
- **478 keV does not trigger.** It fires the SiPM bars (5 × 10³ /s per arm per µA) but cannot reach the plastic's
  1.67 MeV; the accidental bar × plastic legs are 0.4 /s at 1 µA and 6 /s at 4 µA. Accidental two-arm pairs:
  0.004–0.05 /s.
- **PAIR (never prescaled) stays at 25–80 /s up to 4 µA: DREAM is never the limit for the physics trigger.** The
  single-arm output needs P = 5–10 at 1 µA and 20–50 at 4 µA (big plastics) to keep 95 % live. With P = 10 there are
  still ~9 cosmic MIPs per arm per second for the gain calibration (FEAS §14.1).
- **Days against current** (big plastics, window 45°, P chosen per current for ≥ 95 % live): 2.8 d at 0.1 µA,
  1.1 d at 0.25, 0.55 d at 0.5, **0.28 d at 1 µA**, 0.07 d at 4 µA. As built: 15 / 6 / 3 / 1.5 / 0.38 d. The dome
  with the big plastics: 2.5 d at 1 µA, 0.64 d at 4 µA.
- Data: ~100 triggers/s at 1 µA with P = 10, 2.5 MB/s per FEU, 0.2 TB/day per FEU.

## 6. The scintillators: no saturation, even with the big plastics (`shapes_rates.py` → `rates_channels.csv`, `rates_by_line.csv`)

Geant4 γ libraries (dome and 45° window, each detector) folded with the §3 line spectrum, contaminants at F/Li 10⁻⁴,
N/Li 10⁻², Na/Li 10⁻⁴, B/Li 10⁻⁵ (they change nothing below; the clean rows are in the CSVs). Per channel, per µA,
E_p 1.10 MeV (1.03 is ×0.8 in the 478 keV terms), the busiest channel of an arm:

| channel | > 50 keV | > 0.5 MIP (leg threshold) | deposited power | what dominates |
|---|---|---|---|---|
| SiPM bar (3 mm), either detector | 1.1–1.4 × 10³ /s | 0.37–0.41 × 10³ /s (> 0.24 MeV) | ~0.2 × 10³ MeV/s | 478 keV |
| **big slab 75 × 75 × 5 cm** | **2.9 × 10⁵ /s** | 0.8–0.9 × 10³ /s (> 1.67 MeV); 0.6–0.7 × 10³ (> 4.2 MeV, its own 0.5 MIP) | **7 × 10⁴ MeV/s** | 478 keV below threshold; ⁸Be γ above |
| as built: 20 × 30 × 2 cm plastic | 2.0 × 10⁴ /s | 60–80 /s | 4 × 10³ MeV/s | the same |
| as built: LS cell | 6.3 × 10⁴ /s | 250–290 /s (> 0.5 MeV) | 1.4 × 10⁴ MeV/s | 478 keV |

What that means at 4 µA, the most LNL gives:
- **Counting rates.** The big slab sees 1.2 × 10⁶ /s above 50 keV, all 478 keV Compton electrons (≤ 311 keV). A
  discriminator set anywhere near the leg threshold sees ~3.5 × 10³ /s. In a 100 ns integration window there is a
  12 % chance of a 478 keV pile-up, adding on average 0.03 MeV: invisible against the 13–18 MeV E_sum window.
- **PMT anode current.** 2.9 × 10⁵ MeV/s × ~10 pe/MeV (the lnl_calo light yield) × gain 10⁶ ≈ 0.5 µA per slab;
  the LS (×10–20 the light per MeV) ~1–2 µA. Well below the 10–100 µA where gain drifts or the base sags.
  **(ask)** the PMT type and base of the big slabs once chosen: with a passive divider, keep the bleeder current ≥ 20×
  the anode current.
- **SiPM bars.** 5–6 × 10³ /s per bar above 50 keV at 4 µA: nothing for a SiPM.
- **The room.** An analytic stand-in (Φ = 2 γ/cm²/s, ask LNL for a survey) gives ~2 × 10³ /s per big slab above 50 keV:
  the beam dominates from 0.01 µA on.

Neither design changes this: the 478 keV rate is the film's, and 200 µm of Cu or diamond barely attenuate it. The
detector choice does: the big slab is ×14 the as-built plastic in singles and ×17 in deposited power, both fine.

## 7. The Micromegas: the window's Mo K x-rays (Geant4 x-ray lines; PIXE ESTIMATE)

The beam stops in the Mo (window) or the Cu (dome), and ionises their K shells on the way. A binary-encounter
scaling anchored on σ_K(Cu, 1 MeV) ≈ 70 b gives, per µA at 1.10 MeV, **1.4 × 10⁷ Mo Kα (17.5 keV)** from the window
and 1.3 × 10⁹ Cu Kα (8.05 keV) from the dome (ESTIMATE ×2–3; 1.03 MeV: ×0.6).

Geant4 (4 × 10⁶ x-rays per configuration, from the film):

| | reaches one MM drift gap, per x-ray | MM hits per arm per µA | occupancy per arm, 1.2 µs, per µA |
|---|---|---|---|
| dome: Cu K 8.05/8.9 keV | 0 in 1.6 × 10⁶ (< 2 × 10⁻⁶) | < 3 × 10³ (bound) | — |
| window 45°: Mo K 17.5/19.6 keV | **6.0–9.0 × 10⁻³** (the +z arm faces the diamond side: 9 × 10⁻³) | **1.3 × 10⁵** | **16 %** |
| window 0°: Mo K | 6.1 × 10⁻³ (all arms) | 0.9 × 10⁵ | 10 % |
| γ (478 keV and the rest), either design | — | 2.7 × 10³ | 0.3 % |

- 200 µm of diamond passes 96 % of 17.5 keV; the 60 µm mylar and 9 µm Cu cathode pass ~60 %; the 30 mm of gas stops ~8 %.
  The 200 µm Cu shell of the dome stops its own 8 keV line completely (e⁻⁹).
- Each x-ray is one 17 keV point cluster (~650 electrons), larger than a MIP track's ~8 keV in 30 mm. At 1 µA, one
  event in six has one in a given arm. It does not trigger anything (the trigger is the scintillators), and the
  hit rate (~90 /cm²/s) is nothing for the MM gain. But the segment finding (`c_dom`, `d_dom`) may pick it.
- **Mitigations:**
  - run at ≤ 0.5 µA (8 % per arm; the reach does not need more, §5);
  - a 50 µm Cu foil on each MM window passes ~10 % of 17.5 keV, and costs the leptons 0.35 % X₀ right at the
    measurement plane (it scatters after the vertex chord is fixed, so σ68 barely moves; check in Geant4);
  - or a stop that makes softer x-rays: Ti/V K lines (4.5–5 keV) do not escape (0 in 8 × 10⁵ at 4.5 keV), but Ti
    takes up hydrogen.
  - Ta instead of Mo is worse: its L lines (8–10 keV) pass the diamond at 3 × 10⁻⁴–5 × 10⁻³ per x-ray from a larger
    σ_L.
- The analysis should drop isolated point clusters with a charge and size cut. This is the first thing to check
  with a source: ⁵⁵Fe at 5.9 keV is in the MM gas line, and a Mo-anode x-ray tube or ¹⁰⁹Cd (22 keV) reproduces this.

## 8. Everything that could go wrong, ranked

| # | risk | design | size | what to do |
|---|---|---|---|---|
| 1 | **The Cu shell scatters every lepton and converts the γ** | dome | ×9 the days (2.4 vs 0.27 d/µA, big plastics) | drop the Cu dome; if a cup is wanted, Al or Be with a Mo liner (not yet in Geant4) |
| 2 | **Mo K x-rays in the Micromegas** (17.5 keV, 1.4 × 10⁷ /s/µA, ESTIMATE ×2–3) | window | 16 % occupancy per arm per µA | run ≤ 0.5 µA; a 50 µm Cu foil on the MM windows; a point-cluster cut; measure with ¹⁰⁹Cd or an x-ray tube |
| 3 | **¹⁹F at the Li/stop interface at 1.10 MeV** (exit energy 872 keV = the strongest ¹⁹F(p,αγ) resonance) | both | 1 µg/cm² → 60 % of γ₀ in 6–7 MeV γ (legs, trigger rate) | no fluoride cleaning/etch of the Mo or Cu, no PFPE/Fomblin in the evaporator; check the 6.13 MeV line in a short 1.10 MeV run; or run at 1.03 MeV (exit 790 keV), or adjust the Li thickness |
| 4 | **The window is the vacuum wall and the beam stop at once** | window | a crack vents the accelerator line | 200–300 µm over Ø20 (0.2 / 0.09 GPa at 1 bar, audit B1); brazed, not glued; a fast valve upstream; burst-test a spare |
| 5 | **Mo margin at 0°**: without Li the 1.10 MeV beam needs 7.5 µm of Mo, there are 8 | window 0° | protons into the diamond (H at the vacuum wall) if the Li is gone or the Mo is thin | tilt 45° (11.3 µm along the beam), or ≥ 10 µm Mo; verify the Mo thickness (RBS) |
| 6 | **Hydrogen in the beam stop** | both | 2 × 10¹⁸ H/cm²/day/µA at σ 2 mm; Cu blisters from ~10¹⁸–3 × 10¹⁹ | fine for the 3σ run (~0.3 µA·d); for longer runs widen the spot or wobble; Mo's H tolerance at MeV is not measured (gap) |
| 7 | **DREAM dead time from single-arm legs** | both | 75–83 % live at 1 µA, P = 1 (big plastics) | prescale the SINGLE output (P = 5–10 at 1 µA, 20–50 at 4 µA); PAIR never prescaled |
| 8 | **The 45° window's Ø20 Al end piece is in the leptons' view** | window | σ68 9.1° vs 6.2° without it (+22 % days) | a wide, short adapter (open to ≥ Ø60 within a few mm); CFRP only halves it (§4.1) |
| 9 | Li reacts with air during mounting (Li₃N, LiOH, Li₂CO₃) | both | ¹⁵N(p,αγ) 4.44 MeV at 0.8 % N/Li → 1 % of γ₀; more stopping, less Li | transfer under Ar; watch the 4.44 MeV line and PIGE 478 keV |
| 10 | Na in commercial Li (20–200 ppm) | both | 440 keV, 1.63 MeV singles; capture IPC below the window | vendor CoA; harmless |
| 11 | The grey flange (insulator?) under halo protons | both | charging, discharges = noise; PVC releases HCl if heated | **(ask)** its material; keep the halo off it (collimator upstream) |
| 12 | E_p mis-set above 1.881 MeV | both | ⁷Li(p,n): ~10⁻⁴ n/p, a neutron source | interlock on the analysing magnet |
| 13 | α from ⁷Li(p,α)α (2.6 × 10⁶ /s/µA) | both | (α,n) on Li and C: ~40 n/s/µA | nothing |
| 14 | ⁷Be activation | both | ~4 Bq after 10 days | nothing |
| 15 | B (BN crucibles), C build-up | both | B needs 5 % to matter; C shifts 2.6 keV per 10 µg/cm² | nothing |

Not modelled and worth a line each: the gate valve, tees and floor stand are not in Geant4 (they only scatter γ; no
lepton reaches them, TARGET_OPTIONS §18). The grey parts are assumed PVC. The PIXE yield is a scaling estimate; a
Geant4 PIXE run with protons (G4 ECPSSR) or one measurement with a Si(Li)/SDD at LNL would fix it. The room γ flux is a
stand-in. The diamond window's tilt axis is x (toward the ±z arms); the other axis was equivalent in the ray-trace.

## 9. Code, runs, outputs

| file | what |
|---|---|
| `shapes/shapes_geant.py` | the reach: opt_geant machinery on the L10 tables, both detectors, both energies → `geant_reach*.csv`, `geant_acceptance.csv` |
| `shapes/shapes_backgrounds.py` | the per-proton inventory (⁸Be, 478 keV, α, ⁶Li, contaminants, F layers, PIXE, α-n) → `backgrounds_inventory.csv`, `contaminant_levels.csv` |
| `shapes/shapes_rates.py` | singles per channel, legs, accidentals, DREAM live time, MM occupancy, days vs current → `rates_*.csv`, `daq_live.csv`, `days_vs_current.csv` |
| `shapes/deck/build_shapes_deck.py` | the slide note `lnl-target-shapes` |
| `shapes/lxplus/l10_configs.sh`, `submit_l10.sh` | the L10 configurations and submission (copies; they run from `…/x17_lnl/analysis/`) |
| `shapes/lxplus/l10_singles.py`, `l10_sng.sh`, `l10_sng_merge.py` | per-channel deposits of the γ runs (condor) and their merge |
| `shapes/lxplus/l10_driver.sh`, `fetch_l10.sh` | reduce/time/merge as runs finish; copy the tables to `shapes/sel/` (gitignored) |
| `shapes/lxplus/l11_configs.sh`, `submit_l11.sh`, `l11_driver.sh`, `fetch_l11.sh` | the same for L11 (§10): the ogives, the Be+Mo cup, the window's end pieces and the wide adapter, the 1 mm-chamber flat target, the X17-only mount diagnostics |

Outputs in `lnl/out/target/shapes/`. Geant4: MX17_Full_Geant `lnl_shapes`, binary `bin/mx17_full_sim_shapes_39662ea`;
data `/eos/experiment/ntof/data/x17/lnl/L10/` (~1 TB), tables `…/lnl/target/sel_l10/`. L11: branch `lnl_ogive`, binary
`bin/mx17_full_sim_ogive_b6b73e8`; data `…/lnl/L11/` (1.6 TB), tables `…/lnl/target/sel_l11/`.

## 10. Run L11 (2026-10-27): Pierfrancesco's ogive, the light shells, and the window's tube

Dylan asked (27 Oct) to run his new conical designs through Geant4 and to fill the gaps in the designs: the 45° window had no
background run without its 55 mm Ø20 Al end piece (§4.1), the Al/Be cup with a Mo liner (§8 risk #1) had never been simulated,
and the ogive of his CAD sketch (TARGET_OPTIONS §19) was only ray-traced. Same samples, detectors, energies and analysis as L10
(§2); MX17_Full_Geant branch **`lnl_ogive`** (from `lnl_shapes`): `--shape ogive`, `--ogive Mat:t_um[+Liner:um]` (the exact CAD
meridian as G4Polycone layers, `include/OgiveProfile.hh`; vertices on the inner surface where the σ 2 mm spot lands, cap and
flank), liners inside the dome (`--dome Be:11:200+Mo:8`), `--win-plate` and a radius for `--win-endpiece` (the wide adapter).
Binary `bin/mx17_full_sim_ogive_b6b73e8`; configurations `shapes/lxplus/l11_configs.sh`; output `/eos/…/lnl/L11/` (1.6 TB),
tables `…/lnl/target/sel_l11/`. Overlap check clean for every configuration.

**The yields of the ogive are not the flat film's.** The beam spot (rms 2.8 mm) lands 56 % on the tip sphere and 44 % on the flank
at ~65° incidence, where 20 µm of Li along the normal is ~50 µm along the proton (§19.4). The reach folds this in
(`opt_sketch.ogive_yield_mix`, share-weighted over the path): per proton γ₀ is ×2.2 the flat film at 1.10 MeV (×5.0 at 1.03),
and 28 % of it (69 % at 1.03) is the 17.64 MeV line, counted as M1 background and not as X17 signal. The rows "Li on the tip only"
use the flat 20 µm yields: a film masked to the tip sphere, no flank, no 441 keV. The two bracket what a real film will do.

### 10.1 Reach (big plastics; the as-built column is statistics-limited, ±30–50 %)

| configuration | σ68 | acc | days per µA, 1.10 MeV (EPC share) | 1.03 MeV | as built, 1.10 |
|---|---|---|---|---|---|
| *window 45°, Ø20 Al 0.5 mm end piece (L10)* | 9.1° | 0.152 | 0.27 (6 %) | 0.31 | 1.5 |
| **window 45°, Ø20 Be 0.5 mm end piece** | **7.2°** | 0.152 | **0.22** (2 %) | 0.26 | 2.2 |
| window 45° on a wide adapter (2 mm Al plate r 10–30 + 0.5 mm Al tube r 30) | 9.8° | 0.132 | 0.37 (6 %) | 0.43 | 2.4 |
| *flat Li 20 / Mo 8 / diamond 50 in the 0.4 mm CFRP chamber (L9)* | 6.6° | 0.131 | 0.22 (5 %) | 0.26 | — |
| flat design in a buildable 1 mm × 300 mm CFRP chamber (TARGET_OPTIONS §21) | 8.3° | 0.128 | 0.28 (9 %) | 0.33 | — |
| *Cu hemisphere 200 µm (L10)* | 22° | 0.104 | 2.4 (46 %) | 2.8 | 3.2 |
| **Be hemisphere 200 µm + Mo 8 µm liner**, same rim and grey flange | 9.7° | 0.152 | **0.29** (4 %) | 0.34 | 1.8 |
| **Cu ogive 200 µm** (the CAD), Al ring + DN40 line | 18.5° | 0.142 | **0.94** (23 %) | 1.7 | 2.2 |
| Cu ogive, Li on the tip only | 18.5° | 0.142 | 1.16 | 1.3 | 3.0 |
| **Be ogive 200 µm + Mo 8** | **6.6°** | 0.158 | **0.145** (0.3 %) | 0.22 | 1.1 |
| **Be ogive 300 µm + Mo 8** (the buildable wall, TARGET_OPTIONS §20) | 7.1° | 0.158 | **0.15** (2 %) | 0.23 | 1.25 |
| Be ogive 300 µm, Li on the tip only | 7.1° | 0.158 | 0.205 | 0.24 | 1.7 |
| Al ogive 200 µm + Mo 8 | 9.3° | 0.156 | 0.23 (2 %) | 0.35 | 1.6 |
| **Al ogive 300 µm + Mo 8** (buildable) | 10.5° | 0.154 | **0.26** (2 %) | 0.40 | 1.55 |
| Al ogive 300 µm, Li on the tip only | 10.5° | 0.154 | 0.35 | 0.41 | 2.1 |

X17-only diagnostics of the window's mount (big plastics, σ68): bare window 5.7°; no end piece 6.2°; end piece **Be 0.5 mm
7.2°** (full run above); CFRP 0.5 mm 7.4°; Al 0.25 mm 8.0°; CFRP 1 mm 8.3°; Al 0.5 mm 9.1° (L10); wide adapter 9.8°; Al 0.5 mm
cut to 16 mm, straight on the grey flange, 10.1°. The Cu ogive with a bare base (no ring, no line) gives 18.4° against 18.5°
with its mount: the mount is out of the arms' view, as the r > 1.13 d rule said.

### 10.2 Reading

1. **The window's tube cannot be moved out of the way; it can only be made lighter.** Any closed vacuum envelope around a tilted
   window must cross the arms' view on the downstream side of the tilt, and from the vertex it subtends the same solid angle
   whether it is a Ø20 tube, a cone or a wide step: the only radial surface, crossed by no lepton, is the window plane itself.
   Geant4 agrees: the wide adapter (0.37 d) is worse than the Ø20 tube (0.27), because its r 30 tube stands 30 mm in front of the
   vertex on the downstream side and is seen by the 55–130° legs of that arm; the 16 mm end piece on the grey flange (10.1°) is
   worse than the 55 mm one. What works is the wall itself: **0.5 mm Be instead of Al takes σ68 from 9.1° to 7.2° and the reach
   from 0.27 to 0.22 d/µA, the flat design's value.** Al 0.25 mm (8.0°) and CFRP 0.5 mm (7.4°) get part of the way if Be is
   not wanted; a Ø20 × 0.5 mm Be tube holds 1 bar with a margin of ~9 (buckling) and is a catalogue beam-pipe part.
2. **His cup is rescued by its metal:** the same R 11 hemisphere, rim and grey flange in Be 200 µm with an 8 µm Mo liner gives
   0.29 d/µA (9.7°) where Cu gave 2.4 d (22°). EPC drops from 46 % to 4 % of the background.
3. **The ogive is the best shape, and in Be it is the best target simulated**: 6.6–7.1° (200 / 300 µm), 0.145–0.15 d/µA at
   1.10 MeV, ×1.5 faster than the flat design and the Be-tube window (0.22). Two thirds of that gain is the shape (σ68 equal to
   the flat design's 6.6° with a 20 % larger acceptance and 0.3–2 % EPC), the rest is the flank Li path (×2.2 γ₀ per proton):
   with the Li masked to the tip (flat yields) it gives 0.20 d, still a little ahead of the flat design and the Be-tube window. In Al 300 µm (the practical wall) it is 0.26 d, about the window on
   its Al end piece; in Cu, 0.94 d: ×2.6 better than his hemisphere (the walls are steep, nothing grazes), still ×4 worse than
   the window, with 23 % of the background from γ converting in the Cu. The trace's ranking (§19.3) was right; its σ68 for Cu
   was not (10.6° traced, 18.5° in Geant4).
4. **1.03 MeV hurts the ogive more than the others:** with the flank Li, 69 % of γ₀ is the 17.64 MeV line (28 % at 1.10), so the
   Be ogive goes from 0.145 to 0.22 d and the Cu one from 0.94 to 1.7. At 1.10 MeV the flank protons leave the Li at ~450 keV,
   on the edge of the resonance; the mix depends on the spot size and on how thick the Li is on the flank (TARGET_OPTIONS §19.4).
   A film masked to the tip sphere, or a σ ≲ 1 mm spot, removes the issue and the yield gain together.
5. **The flat design's lead was its chamber's.** The 0.4 mm × 600 mm CFRP tube of L9 would buckle at 0.35 bar (§21); with a 1 mm × 300 mm chamber that holds vacuum, σ68 goes from 6.6° to 8.3° and the reach from 0.22 to 0.28 d/µA (EPC 9 %: the thicker wall converts more γ). The window on a Be tube (0.22) now leads among the thin targets, and the Be ogive leads everything.

### 10.3 Rates, DREAM, x-rays (`shapes_rates.py`, the L11 γ libraries)

Per µA at 1.10 MeV, big plastics (as built in brackets), from the L11 γ-line libraries of the Cu ogive, the Be ogive and the
window on its Be tube, with the ogive's line spectrum from the flank-mixed yields:

| | arm legs /s | pairs /s | live at P = 1 / 10, 1 µA | P for ≥ 95 % live at 1 / 4 µA | 478 keV γ/s | MM hits /s per arm (x-rays) | MM occupancy |
|---|---|---|---|---|---|---|---|
| window, Al tube (L10) | 720 (250) | 25 | 83 / 97 % | 5 / 20 | 5.0 × 10⁶ | 1.3 × 10⁵ (Mo K through the diamond) | 16 % |
| window, Be tube | 690 (240) | 25 | 83 / 97 % | 5 / 20 | 5.0 × 10⁶ | 1.8 × 10⁵ | 22 % |
| Cu ogive | 1630 (560) | 39 | 68 / 95 % | 20 / 100 | 6.5 × 10⁶ | 3.5 × 10³ (no x-rays: the Cu stops its own) | 0.4 % |
| Be ogive + Mo | 1020 (325) | 24 | 77 / 97 % | 10 / 50 | 6.5 × 10⁶ | 1.2 × 10⁵ (Mo K through 200 µm Be) | 15 % |

- **DREAM copes everywhere with the single-arm output prescaled** (§5 rule): the ogive's flank Li makes ×1.6 the ⁸Be γ per µA
  (and 9.5 × 10³ /s of 17.64 MeV γ where the window has 130), so its legs are ×1.4 the window's; the Cu shell converts more of
  them (1630 /s). PAIR stays at 24–39 /s. Days against current with the best prescale (`days_vs_current.csv`): Be ogive 0.16 d at
  1 µA, 0.039 d at 4 µA; window on the Be tube 0.23 / 0.058; Al ogive 0.27 / 0.067; Cu ogive 0.97 / 0.25.
- **The Mo liner's K x-rays are the window's problem all over again:** 200 µm of Be passes 17.5 keV as the diamond does, so the
  Be (and Al) ogive loads the Micromegas at 15 % per arm per µA (PIXE ESTIMATE ×2–3, §7). Same mitigations: ≤ 0.5 µA, a 50 µm Cu
  foil on the MM windows, a point-cluster cut. The Be tube on the window passes the x-rays the Al tube absorbed: 22 % against 16 %.
  The Cu ogive, like the Cu dome, has none.
- Scintillators: the 478 keV line is ×1.3 the window's for the ogive (the flank Li); nothing saturates (§6 scales by 1.3).

### 10.4 What changes in the verdict (§0)

- The window stays the recommendation **with a Be (or ≤ 0.25 mm Al / 0.5 mm CFRP) end piece**: 0.22 d/µA. Forget the wide adapter.
- If Pierfrancesco keeps the shell: **Be 300 µm + Mo on his ogive is the fastest target on the table (0.15 d/µA)** and Al
  300 µm + Mo (0.26 d) is the cheap version; never Cu (0.94 d). Both need the Li thickness on the flank (or a mask) and the
  spot size settled first, because they set the 17.64 MeV share.
- Risk table §8 #1 and #8 are answered; new risk: the flank Li (yield ×2.2 but 28–69 % of γ₀ at 17.64 MeV).
