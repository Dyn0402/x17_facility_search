# The lithium target: what probably stopped the LNL 2023–24 ⁸Be run, and what could stop ours

Started 2026-10-22, after Pierfrancesco's question: the LNL ⁸Be pair spectrometer took ~790 h of beam on
AN2000 in 2023–24 and has published no result. Was it the lithium target, and would the same problem hit
MX17 at LNL? This file is the write-up. The numbers come from the code in this directory (§12). Anything
that could not be found publicly is marked **(ask)**. Analytic stand-ins are marked **ESTIMATE**.

---

## 0. Bottom line (2026-10-22)

1. **The most likely culprit is the fluorine in their LiF, not the lithium.**
   - LNL ran **LiF targets (34–935 µg/cm²) at E_p = 1.03 MeV** (Góngora-Servín 2025). As far as we can find,
     no other group ran LiF at the 18.15 MeV resonance.
   - ATOMKI's own two-arm paper (Tran The Anh *et al.* 2024, Hanoi spectrometer built with ATOMKI) says why
     nobody does: from 441 keV to 1.04 MeV *"the cross-section of the ¹⁹F(p,α)¹⁶O reaction increases very
     fast and the created e⁺e⁻ pairs from the 6.05 MeV E0 transition would overload our electronics and data
     acquisition, and observing e⁺e⁻ pairs from the 18.15 MeV transition would not be feasible."* They switched
     to Li₂O above 441 keV.
   - From measured cross sections (§3), LNL's LiF at 1.03 MeV gives **2.5–3.5×10³ ¹⁹F E0 pairs per ⁸Be pair**,
     and **27–42 ¹⁹F γ (6–7 MeV) per ⁸Be γ**.
   - In an LNL-like ΔE–E clover array (a toy, §4.2), the thick target at 0.8 µA gives:
     - ~2×10³ two-clover E0 coincidences per second, against **0.36/s ⁸Be pairs (×6×10³)**;
     - ~8×10³ triple coincidences per second in each clover.

   Their 441 keV (17.64 MeV) data are clean: ¹⁹F pairs ≈ ⁸Be pairs there. So **the 17.64 MeV calibration was
   probably fine, and the 18.15 MeV data were the problem.** This is an inference from public facts. It needs
   confirming with the LNL group (§11).
2. **The second suspect is heat, and it bites every thin-backing target.**
   - A 10 µm Al strip like ATOMKI's (5 × 50 mm between rods) reaches **440–660 °C at 1 µA** in our model (§5).
     The Al melts at 660 °C.
   - Above ~330 °C, metallic Li diffuses through 10 µm of Al in a day. That is exactly ATOMKI's admitted 2016
     mishap: the targets became 10 µm thick and the beam reached the 441 keV resonance.
   - It also explains Hanoi's "target burned out (punctured) many times" at 1–1.5 µA.
   - LNL's backing and holder are not published **(ask)**.
3. **For MX17 the target is a manageable risk**, provided we:
   - **use no fluorine.** Li₂O, LiPON or capped Li all work. LiF is acceptable only for the 441 keV calibration.
   - **keep the film below ~150 °C.** Use an edge-clamped disk (10 µm Al gives ≤ 160 °C up to 2 µA), or a
     graphite or Cu backing at CN's 4 µA. Never a strip on rods.
   - **move Li₂O under argon.** In air it turns into LiOH or Li₂CO₃: Hanoi measured 0.30 → 0.44 mg/cm².
   - **monitor it:** the 478 keV PIGE line, the γ₀ line shape, and a short 441 keV resonance scan per target.
4. **MX17's fit is robust to a drifting target. ATOMKI-style θ-only analyses are not** (§8).
   - Fit with big plastics and the reference 3D fit (θ × |y| × E_sum), over 30 days:

     | true target | fake X17, in units of R_ATOMKI | χ² rejecting the wrong model |
     |---|---|---|
     | 20 % of γ₀ from the 441 keV resonance | **−0.06** | ≈ 900 |
     | fully hydrated or carbonated Li₂O | ≤ 0.004 | 30–80 |
     | 100 µg/cm² of carbon on the front | ≤ 0.004 | ~120 |

     The large χ² values mean the data themselves flag the wrong model.
   - The same errors in a θ-only fit give **+0.07 to +0.20** of the ATOMKI signal, at χ² ≈ 1–6, which is
     invisible. A thin target that changes during the run biases an ATOMKI-type angle fit by up to 20 % of the
     claim. It cannot create the 6.8σ claim on its own.
5. **Boron, carbon build-up and hydrogen** are second-order (§6, §7, §9).
   - **Boron:** at Zahnow's B/Li = 0.24 (commercial ⁷LiF, 1995), ¹¹B(p,γ₀) adds a 16.9 MeV E1 line at ~5 % of
     the ⁸Be γ₀ (ESTIMATE). At B/Li ≤ 10⁻² it is ≤ 0.2 %. In the fit it is harmless: a fake r of −0.02 at B/Li = 0.24 (§6.2).
   - **Carbon:** 10 µg/cm² shifts the beam by 2 keV at 1.07 MeV (no effect) and by 4 keV at 441 keV (−18 %
     yield on a 30 µg/cm² calibration target).
   - **Hydrogen:** the fluence where the beam stops passes 10¹⁸–10¹⁹ /cm² in days. That matters only for a
     metal backing that stops the beam.

---

## 1. What is known about the LNL run

| | |
|---|---|
| Who | B. Góngora-Servín (PhD Ferrara 2024), T. Marchi, D. Tagnani, A. Celentano, A. Goasduff, J.J. Valiente-Dobón (INFN LNL, Roma 3, Genova; NUCLEX/CSN3) |
| Machine | AN2000, typical 800 nA |
| Targets | **LiF, 34–935 µg/cm²**. Backing, holder and preparation are not published **(ask)** |
| Energies | 441 keV and **1.03 MeV "at the centre of the target"** (for 935 µg/cm²: in at ~1.12, out at ~0.93 MeV) |
| Physics | "IPC in ⁷Li(p,e⁺e⁻)⁸Be **and ¹⁹F(p,αe⁺e⁻)¹⁶O**": they knew the E0 line was there and also wanted it |
| Detector | 4 clovers × 4 ΔE–E telescopes (ΔE: 2 × 10 bars, 2 × 5 × 50 mm; E: 10 × 5 × 5 cm EJ-200), 12.5–13 cm from target, ⊥ beam or at 45°; "designed to work in vacuum" |
| Selection | triple coincidence ΔE-front, ΔE-back, E in each telescope; exactly two telescopes; ΔE sum 1.2–2.2 MeV; add-back over the clover; \|y\| < 0.75 |
| Running | three configurations (2 clovers; 4 clovers ⊥ beam; 4 clovers at 45°), ~790 h beam in total |
| Status | "analysis ongoing, results soon" (Dec 2024 proceedings). Marchi talked at LDMA 2025 (Genova, 10 Apr 2025, agenda.infn.it/event/43758). The agenda server was unreachable from here and from lxplus, so **the slides are still to get (ask)**. Nothing published by Oct 2026. |
| Their own worry | "drastic drops [in acceptance] … can produce artifacts in the final angular distribution" (GS25 §4) |

The PhD thesis (Góngora-Servín, Ferrara 2024) has the full target description and is behind a 403. **Ask for it.**

## 2. The candidate explanations, ranked

| # | hypothesis | evidence for | evidence against / unknown | how to check |
|---|---|---|---|---|
| 1 | **¹⁹F in LiF swamps the 18 MeV data at 1.03 MeV** (DAQ load, pile-up, an E0-dominated pair sample) | Hanoi/ATOMKI state it as fact; LNL is the only LiF run at 1.03 MeV; §3–4: ×2.5–3.5×10³ in pairs | Their ΔE-sum and E-sum cuts remove single E0 pairs. The cost is the DAQ, and pile-up at ~10⁻³ per window. Their DAQ limits are unknown | Ask: trigger rate and dead time at 1.03 MeV vs 441 keV |
| 2 | **Target heating → Li loss, LiF evaporation, puncture, Li diffusion** | ATOMKI 2016 and Hanoi 2024 both had it; §5: strips run at 400–700 °C per µA | LiF melts at 845 °C and is much more stable than Li metal (§5.2). A clamped disk or thick backing would be fine | Ask: backing, holder, 478 keV PIGE vs time |
| 3 | The target thickness/energy profile drifts, so the M1/E1 mix moves | Thick LiF (935) spans 190 keV | A drift moves an angle-only fit by ≤ 0.2 R_ATOMKI (§8). It is a systematic, not a killer | — |
| 4 | Not the target: acceptance structure at 120–160°, cosmics (MEG II 2026: cosmic two-arm events peak near 140°), statistics | Their own paper flags acceptance drops; 1.2 % pair acceptance | — | Ask |
| 5 | Boron, carbon build-up, H blistering | — | §6, §7, §9: second order | — |

## 3. Fluorine: the numbers

**Cross sections** (`out/target/cross_sections.csv`; ⁷Li from Zahnow 1995 via `lnl_rates.py`):

| E_p (keV) | ⁷Li γ₀ (µb) | ⁷Li γ₀+γ₁ (µb) | ¹⁹F(p,α_π) → 6.05 MeV pairs (mb) | ¹⁹F(p,αγ), 6.13+6.92+7.12 MeV (mb) |
|---|---|---|---|---|
| 441 | 3900 | 5650 | 0.016 | 0.15 |
| 800 | 21 | 67 | 0.29 | 1.0 |
| 935 (¹⁹F resonance) | 28 | 87 | 0.53 | 26 |
| 1030 | 33 | 93 | 0.74 | 2.3 |
| 1100 | 25 | 78 | 1.6 | 3.3 |
| 1125 | 21 | 82 | 3.5 | 3.5 |

- **α_π** (¹⁶O left in its 6.05 MeV 0⁺ state, which decays only by e⁺e⁻): Redigolo *et al.*, J. Phys. G 51 (2024)
  075106. Their Figs 6 and 8 are digitised in `data/f19/redigolo2024_alpha_pi_digitised.csv`, covering
  E_cm 1.04–1.25 MeV, with the R-matrix fit below that. Below E_cm 1.0 MeV the cross section is extrapolated at
  constant S-factor: an upper-side ESTIMATE, ±×3.
- **αγ:** TUNL compilation, 2021PH03 dσ/dΩ(90°) for the 6.13 MeV line, 0.84–1.52 MeV, × 4π (isotropic, ±30 %),
  × (1 + 0.6) for the 6.92 and 7.12 MeV lines (ESTIMATE, ×2). Below 0.9 MeV: 1991HE16.
- At 1.03 MeV a fluorine nucleus is **~25× more likely to make a 6 MeV E0 pair than a lithium nucleus is to make
  any γ**. A ⁸Be γ then makes a pair only 3.5×10⁻³ of the time.

**Per target** (`out/target/scenarios.csv`):

| target | ¹⁹F pairs per ⁸Be IPC pair | ¹⁹F γ per ⁸Be γ |
|---|---|---|
| ATOMKI/LNL LiF 30–34 at 441 keV | **1.1–1.3** | 0.03 |
| Hanoi LiF 30 at 800 keV | 1.3×10³ | 16 |
| **LNL LiF 34 at 1.03 MeV** | **2.5×10³** | 27 |
| **LNL LiF 935, 1.03 at centre** | **3.5×10³** | 42 |
| LiF 100 at 1.05 (hypothetical MX17) | 2.7×10³ | 29 |
| Li₂O / Li / LiPON | 0 | 0 |

## 4. Fluorine in a detector

### 4.1 MX17 (Geant4 singles libraries, `target_rates.py`)

From L6 (as built) and L8 (big plastics) runs of 6.05 MeV E0 pairs and of ¹⁹F γ lines (§12):

- **As built:**
  - an E0 pair makes a trigger leg in a given arm 2.0 % of the time (8.3 % in any arm), **and never in two arms
    (0 in 10⁶)**;
  - each pair crosses an arm's Micromegas 28 % of the time;
  - a ¹⁹F γ makes a leg 0.08 % of the time per arm;
  - a ¹⁹F leg carries ≤ 6.9 MeV.
- **Big plastics:**
  - an E0 pair makes a leg 4.5 % per arm (18 % in any arm), again never in two arms (0 in 1.8×10⁶);
  - a ¹⁹F γ makes a leg 0.22 % per arm;
  - a ¹⁹F leg carries ≤ 7.1 MeV.

  The thicker, larger plastics see about 2.3× more fluorine than the as-built stack.

Rates (`out/target/rates_mx17.csv`), as built:

| target, current | ¹⁹F legs / arm / s | prescale for ≥ 90 % live | MM: extra track in the 1.2 µs window | ¹⁹F accidentals in E_sum 13–18 per day, after TOF |
|---|---|---|---|---|
| LiF 100 at 1.05, 1 µA | 260 | 4 | 0.4 % | 3×10⁻⁴ |
| LiF 100 at 1.05, 4 µA | 1.0×10³ | 16 | 1.5 % | 5×10⁻³ |
| LNL LiF 935, 1 µA | 3.1×10³ | 64 | 4.5 % | 0.02 |
| LNL LiF 935, 4 µA | 1.2×10⁴ | 256 | 17 % | 1.4 (45 without TOF) |
| Li₂O 300 at 1.07, 4 µA | 0 | 1 | 0 | 0 |

With the big plastics (the configuration the reach assumes):

| target, current | ¹⁹F legs / arm / s | prescale | ¹⁹F accidentals in E_sum 13–18 per day, after TOF (without) |
|---|---|---|---|
| LiF 100 at 1.05, 1 µA | 580 | 8 | 0.007 (0.25) |
| LiF 100 at 1.05, 4 µA | 2.3×10³ | 64 | 0.14 (4.6) |
| LNL LiF 935, 1 µA | 7.0×10³ | 128 | 2.1 (70) |
| LNL LiF 935, 4 µA | 2.8×10⁴ | 1024 | **70** (2.3×10³) |

The window holds ~1.5×10³ IPC per day per µA. A thick LiF target at CN currents would therefore put about
1 % of the IPC into the window as fluorine accidentals with their own shape, even after TOF.

For MX17, fluorine is a **cost, not a killer**:
- it forces a single-arm prescale;
- it adds Micromegas occupancy;
- a thick LiF target at CN currents would feed ~1 accidental per day into the window even after TOF.

The design's ×7 pair trigger and the E_sum window do the work. There is still no reason to accept any of
these costs: **Li₂O removes them all.**

### 4.2 An LNL-like ΔE–E array (TOY)

Inputs:
- 4 clovers with 10 × 10 cm faces at 12.75 cm (4.9 % of 4π each);
- a lepton above 1 MeV passes the triple coincidence;
- a 6–7 MeV γ passes it with 6×10⁻⁴ (Marchi 2021, slide 14) and deposits something in an E block 30 % of the time;
- the two-clover acceptance for 18 MeV IPC is 1.2 % (Marchi 2021, slide 20);
- for wide-angle E0 pairs, 3 % × 0.64.

All to ×2. Results at 0.8 µA (`out/target/rates_lnl_like.csv`):

| target | ¹⁹F pairs/s (4π) | ¹⁹F γ/s | ⁸Be IPC pairs/s (4π) | triples per clover /s | two-clover E0 /s | two-clover ⁸Be /s | ratio |
|---|---|---|---|---|---|---|---|
| LiF 34 at 441 | 65 | 540 | 61 | 5 | 1.2 | 0.73 | 1.7 |
| LiF 34 at 1.03 | 2.9×10³ | 9.0×10³ | 1.2 | 230 | 56 | 0.014 | 4×10³ |
| LiF 935, 1.03 at centre | 1.1×10⁵ | 3.6×10⁵ | 30 | 8.4×10³ | 2.0×10³ | 0.36 | 6×10³ |

- The thin target at 1.03 MeV gives **0.014 ⁸Be pairs/s, ~1200 per day** in the array, before any cuts.
- The thick one gives a clover-level rate of ~10⁴/s, mostly 2–5 MeV leptons.
- With 100 ns integration, each clover has a ~10⁻³ chance of piling up per event. That is enough to put an
  E0 + γ pile-up continuum under the 16–20 MeV region at the 10⁻³–10⁻² level of the IPC. It is also enough for
  a digitiser-based DAQ to spend most of its time on fluorine.
- **One more unknown (ask):** detectors in vacuum see the charged particles too, unless a foil stops them:
  - ¹⁹F(p,α₀) α of ~7 MeV (σ ~ few mb);
  - ⁷Li(p,α)α at 8.7 MeV (σ ~ 3–5 mb at 1 MeV);
  - backscattered protons.

  On a 935 µg/cm² target that is ~10⁵ α/s into 4π.

## 5. Heat

`target_model.py` solves the steady-state temperature of the backing:
- conduction to the clamp, plus radiation from both faces;
- a Gaussian beam of σ 1.5 mm;
- power = beam current × the energy lost in the film plus the foil.

The beam stops in 10 µm Al at 0.8 MeV (0.77 W/µA) and leaves at 0.48 MeV at 1.1 MeV (0.53 W/µA).
Results (`out/target/thermal.csv`), peak °C:

| holder | 0.8 MeV, 1 µA | 1.05 MeV, 1 µA | 1.05 MeV, 4 µA |
|---|---|---|---|
| **ATOMKI 2016: 10 µm Al strip, 5 × 50 mm, Plexiglas rods** | **657** | 561 | 1070 |
| ATOMKI 2022: same strip, Al rods | 552 | 439 | 1020 |
| 1 µm Ni disk, r = 10 mm (Hanoi Li₂O) | 314 | 282 | 690 |
| 20 µm glassy C disk | 509 | 581 | 1010 |
| **10 µm Al disk clamped at r = 10 mm** | 122 | **95** | 298 |
| **25 µm graphite foil disk** | 57 | **56** | **142** |
| **25 µm Cu disk (MEG II-like)** | 50 | 57 | **149** |

- **Sensitivity.** The emissivity of the coated foil is uncertain: we used 0.08 for Al.
  - At ε = 0.3–0.6 the strips at 1 µA, 1.1 MeV drop to 240–350 °C, and at 5 µA they are still 590–800 °C.
  - A σ of 3 mm instead of 1.5 mm takes off 10–25 %.
  - The disk and graphite results barely move: they are conduction-dominated.
- **Cross-checks:**
  - ATOMKI 2016 saw Li diffuse into the Al.
  - Hanoi 2024 had LiF/Al targets "punctured many times" at 1–1.5 µA.
  - ATOMKI 2022 needed Al rods for their 5 µA runs and still saw the rods in the background.

  Strip targets at µA run hot, and the model agrees.

### 5.1 What the temperature does (`out/target/limits.csv`)

| process | threshold |
|---|---|
| Li metal melts | 180 °C |
| Li diffuses through 10 µm Al in a day (D = 4.5 e^(−139 kJ/RT) cm²/s, Costas 1963) | **≥ 327 °C** (in a week: 287 °C) |
| 1 µm (53 µg/cm²) of Li evaporates in 10 h (Hertz-Knudsen, CRC vapour pressure) | ≥ 277 °C |
| 300 µg/cm² LiF evaporates in a week (ESTIMATE: ΔH_sub 256 kJ/mol, ±×3) | ≥ 477 °C |
| Al melts | 660 °C |
| Li₂O melts | 1438 °C; LiOH melts at 462 °C and dehydrates to Li₂O above ~400 °C |

**So:**
- Li metal on a strip is gone or diffused at any µA.
- LiF on a strip survives at 1 µA but not at 2 µA, and above ~1.5 µA the Al itself is at risk.
- Li₂O tolerates heat, but a hot backing still ages it.
- An edge-clamped disk keeps any of them cool up to ~2 µA. Graphite or Cu does so up to 4 µA.

## 6. Contaminants

### 6.1 Boron: the one in the signal window

- ¹¹B(p,γ₀)¹²C has Q = 15.96 MeV, so at E_p ≈ 1.05 MeV **γ₀ = 16.9 MeV**. It is E1, through the broad 17.23 MeV 1⁻
  level.
- Our ESTIMATE: σ(γ₀) ≈ 7.6 µb at 1.05 MeV, from a Breit-Wigner with:
  - Γ = 1.15 MeV;
  - (2J+1)Γγ₀ ≥ 115 eV (Kelley 2017);
  - Γp/Γ = 0.5 assumed.

  That is ~¼ of ⁷Li(p,γ₀).
- Per B atom per Li atom, the ¹¹B γ₀ rate is 0.21 × the ⁸Be γ₀ rate:

  | B/Li | ¹¹B γ₀ / ⁸Be γ₀ |
  |---|---|
  | 10⁻³ | 2×10⁻⁴ |
  | 10⁻² | 2×10⁻³ |
  | **0.24** (Zahnow's commercial ⁷LiF) | **5 %** |

- Sources of boron:
  - lithium from brines: raw Li₂CO₃ carries up to ~500 ppm B;
  - BN crucibles, which are common for evaporating Li;
  - borosilicate glassware.
- **Specify battery-grade or "low-B" material and measure it** with ¹¹B(p,α) NRA on the AN2000, or with
  ¹¹B(p,γ) at the 163 keV resonance.

### 6.2 What the fit makes of it

Geant4 L8 `E1_16.9_bigP` (10⁶ E1 IPC pairs at W = 16.9 MeV, big plastics) is added to the truth with the
estimated weight. The model has no such line. Fake X17 after 30 days (`fit_bias.csv`):

| B/Li | 3D fit | 3D χ² left | θ only | m_ee |
|---|---|---|---|---|
| 10⁻³ | −0.000 | 0 | −0.000 | +0.000 |
| 10⁻² | −0.001 | 0 | −0.001 | +0.000 |
| 0.1 | −0.008 | 16 | −0.012 | +0.002 |
| 0.24 (Zahnow) | −0.019 | 93 | −0.029 | +0.004 |

**Boron cannot fake an X17.** A 16.9 MeV E1 IPC falls steeply with opening angle, so it adds background at small
angles and pulls r slightly negative. Even at the worst purity on record, the bias is 2–3 % of the ATOMKI signal,
and the 3D χ² flags it. Spec B/Li < 10⁻³ anyway: it is cheap to check.

### 6.3 Others

| nucleus | where from | lines | verdict |
|---|---|---|---|
| ¹⁹F | LiF; also CaF₂/PTFE near the beam | §3 | avoid in the production target |
| ²⁷Al | backing, holder | ²⁷Al(p,γ) 992 keV resonance → 10.76 MeV | below the window (FEAS §4); an Al holder near the beam adds singles |
| ¹²C, ¹³C | backing, build-up, carbonate | Q 1.94 / 7.55 MeV | below the window |
| ¹⁴N | LiPON, air leaks, Li₃N on Li metal | ¹⁴N(p,γ)¹⁵O 1058 keV resonance → ≤ 7.6 MeV | below the window |
| ³¹P | LiPON | ≤ 9 MeV | below the window |
| ¹⁶O, ¹⁸O | Li₂O, oxides | ¹⁸O(p,γ) ≤ 9 MeV, tiny | none |
| ⁶Li | 7.6 % of natural Li | ⁶Li(p,³He)α, charged | none behind the chamber wall; enrichment gains 8 % rate |

## 7. Carbon build-up

- Cracked hydrocarbons deposit carbon on the beam spot. Reported rates run from ~10¹⁴ C/cm²/µC (an old
  systematic study, quoted in arXiv:1708.09303) to "not measurable" with a cold trap at 10⁻⁷ mbar (Redigolo
  2024). We scan 0–100 µg/cm² (`out/target/carbon.csv`):

  | C on front (µg/cm²) | shift at 441 keV | 441 yield, LiF 30, beam not retuned | shift at 1.07 MeV | γ₀ yield, Li₂O 300 at 1.07 |
  |---|---|---|---|---|
  | 2 | 0.8 keV | −1 % | 0.4 keV | +0.2 % |
  | 10 | 3.8 keV | **−18 %** | 2.2 keV | +0.8 % |
  | 20 | 7.6 keV | −50 % | 4.3 keV | +1.4 % |
  | 100 | 39 keV | −97 % | 22 keV | +3.9 % |

- **Carbon is a calibration-run problem only.** On the 12 keV-wide 441 keV resonance, carbon moves a thin
  target off resonance. On the 168 keV-wide 1.03 MeV resonance it does nothing that matters.
- Use a cold trap and a biased suppressor ring, and repeat a short 441 keV scan whenever a target is changed.

## 8. A target that changes during the run: what the fit reports

`target_fit_bias.py`:
- The truth is a degraded target; the model is always Li₂O 300 at 1.10 MeV (`lnl_syst.SIG_RUN`).
- For each case we form Δ = background(truth) − background(model). The Fisher bias after T days is
  (TF + P)⁻¹ T b, as in the impostor test (FEAS §16).
- Big plastics, LNL-calibrated response, 30 days, reference structure (S_θ 2 % + S_θy 1 %). Output:
  `out/target/fit_bias.csv`.

| truth | 3D fit: fake r | 3D: χ² left | θ only: fake r | θ: χ² left | m_ee: fake r |
|---|---|---|---|---|---|
| 441 keV share of γ₀ 1 % (nominal 0.6 %) | −0.001 | 0.2 | +0.003 | 0.0 | −0.001 |
| 5 % | −0.011 | 32 | +0.038 | 0.2 | −0.006 |
| 10 % | −0.025 | 165 | +0.086 | 1.1 | −0.014 |
| 20 % | −0.058 | 891 | **+0.20** | 5.8 | −0.033 |
| all LiOH (hydrated) | +0.002 | 31 | +0.075 | 0.9 | −0.039 |
| all Li₂CO₃ | +0.004 | 78 | +0.115 | 2.2 | −0.043 |
| 100 µg/cm² carbon on the front | +0.002 | 118 | +0.072 | 1.2 | −0.047 |

How the "441 keV share" maps onto the diffusion scenarios (`scenarios.csv`):
- Li metal fully diffused through 10 µm Al: 10–16 %;
- the same on a backing that stops the beam: up to **78 %**, which is ATOMKI 2016.

**Reading.**
- In the 3D fit the E_sum axis sees the 17.64 MeV line and the shifted E1/M1 mix. The fit stays unbiased and the
  χ² flags the mismodelling.
- An angle-only analysis absorbs the same errors silently, at up to +0.2 of the claimed ATOMKI signal.
- This is the quantitative form of Hanoi's own excuse: "the effective energy of the protons was changing and
  may have washed out the anomaly". A drifting target can move an angle-only result by 10–20 % of the claim.
  It cannot make or erase a 6.8σ effect.

## 9. Hydrogen dose and blistering

- At 1 µA on a σ = 2 mm spot, the fluence where the beam stops is (`out/target/fluence.csv`):
  - 2×10¹⁸ /cm² per day;
  - 1.5×10¹⁹ /cm² per week;
  - at 4 µA, 6×10¹⁹ /cm² per week.
- Blistering thresholds for Cu run from ~10¹⁸ /cm² (low energy) to 1.7–3.4×10¹⁹ /cm² (2 MeV, Budker/OIST).
- **It matters only where the beam stops in a metal:** a Cu or Ta backing, or MEG II's 25 µm Cu.
- With a 10 µm Al backing at 1.1 MeV the beam leaves at 0.48 MeV and stops in the distant dump.
- On graphite, hydrogen saturates and outgasses rather than blistering the film off.

## 10. Making the target: thin, known, and kept that way

- **Thickness.** 100–300 µg/cm² Li₂O (0.5–1.5 µm; ΔE 20–60 keV) is routine. LiF was evaporated to 184 µg/cm² with
  6 % non-uniformity onto Ag (arXiv:2208.03425), with a rotating substrate and a quartz monitor.
- **The composition is the hard part.**
  - "Li₂O" at ATOMKI was Li metal evaporated and then oxidised: "milky white" when it went wrong.
  - Prefer **e-beam evaporation of Li₂O or reactive deposition of Li in O₂**, or **RF-sputtered LiPON**
    (stable; MEG II's choice, but then thick and rough).
- **Handling.** Make, store and mount Li₂O under Ar or vacuum, with a transfer vessel to the chamber.
  - Hanoi's "0.3 mg/cm²" Li₂O measured 0.44 mg/cm² by the width of the 441 keV resonance: ×1.47, close to full
    conversion to LiOH (×1.6).
  - Hydration costs little in the 3D fit (§8). It changes the yield per keV and the E1 share, so measure it
    rather than assume it.
- **Measure each target before and during the run, all on AN2000 or CN:**
  1. a 441 keV resonance scan: the yield edge gives the thickness and any carbon, and its width gives the
     composition (Hanoi's method);
  2. RBS/NRA for Li, O, F, B and C;
  3. the 478 keV ⁷Li(p,p′γ) PIGE line in a HPGe or LaBr₃ as a continuous Li monitor (ATOMKI's choice);
  4. the shape of the 17.6/18.15 MeV γ₀ line, which tracks the proton energy profile in the target (ATOMKI's
     trick).
- **Mounting.** An edge-clamped disk or a graphite/Cu backing, not a strip (§5). Keep Al and fluorine-bearing
  parts (PTFE, Viton) away from the beam spot and halo.

## 11. For MX17 at LNL: the target spec and the questions

**Spec:**
- **film:** Li₂O (natural Li, or ⁷Li-enriched for +8 %), 100–300 µg/cm²;
- **calibration target:** LiF 30 µg/cm² at 441 keV only (¹⁹F there is ≈ ⁸Be);
- **backing:**
  - 10 µm Al disk edge-clamped at r ≤ 10 mm to a cooled ring, up to 2 µA;
  - 25–50 µm graphite foil or 25 µm Cu at 4 µA. The Cu costs 2.4° of opening-angle resolution (FEAS §5) and
    blisters, so prefer graphite.
- **film temperature:** < 150 °C;
- **handling:** move under Ar;
- **boron:** spec B/Li < 10⁻³ and measure it;
- **vacuum:** a cold trap;
- **monitoring:** PIGE, LaBr₃ γ₀ line shape, and a 441 keV scan per target change.

**Ask the LNL group (Marchi, Góngora-Servín):**
1. the trigger rate and dead time at 1.03 MeV, compared with 441 keV;
2. backing, holder, beam spot and target temperature; the target lifetime and PIGE history;
3. whether the telescopes saw α particles and scattered protons, and what absorber was used;
4. the thesis and the LDMA 2025 slides.

**Ask the LNL target lab:**
- Li₂O deposition (e-beam or reactive);
- Ar transfer;
- B analysis.

## 12. Code, runs, outputs

| what | where |
|---|---|
| physics and materials model | `lnl/target/target_model.py` → `out/target/{cross_sections,scenarios,fluorine_scan,thermal,limits,fluence,carbon}.csv` |
| detector rates | `lnl/target/target_rates.py` → `out/target/rates_mx17.csv`, `rates_lnl_like.csv` |
| fit bias | `LNL_SEL=lnl/sim/sel_v3 python lnl/target/target_fit_bias.py` → `out/target/fit_bias.csv` |
| singles extractor (lxplus) | `lnl/target/lxplus/target_singles.py` (copy in `…/work/git/x17_lnl/analysis/`) → `$E/target/*_singles.npz`, copied to `lnl/target/sel/` (gitignored) |
| Geant4 (L8, 2026-10-22, binary `mx17_full_sim_lnl_bc4cd6c`, `submit_lnl.py`) | `E0_6.05_bigP` 20×10⁵, `gam_19F_bigP` 20×5×10⁵, `E1_16.9[_bigP]` 10×10⁵ each, `E1_16.9_bigP_open70` 24×10⁵ (θ > 70°, like L7) |
| data | `lnl/data/f19/` (TUNL ¹⁹F γ files, Redigolo α_π digitisation) |
| deck | `lnl/target/deck/build_deck.py` → note `lnl-lithium-target` |

## Sources

- Tran The Anh *et al.*, "Checking the ⁸Be anomaly with a two-arm electron positron pair spectrometer",
  Universe 10 (2024) 168, arXiv:2401.11676 (`refs/TranTheAnh2024_Hanoi_twoarm_arXiv2401.11676.txt`): ¹⁹F overload
  quote, LiF/Al 30 µg/cm² and Li₂O/Ni 0.3 mg/cm² targets, burned-out targets, the 441 keV width method.
- B. Góngora-Servín *et al.*, APPB Proc. Suppl. 18, 2-A13 (2025); T. Marchi, "Experiments on ⁸Be IPC at LNL",
  Rome 2021 (`refs/`).
- N.J. Sas *et al.*, arXiv:2205.07744 (ATOMKI 2022: diffused Li, Al rods, 5 µA); J. Gulyás *et al.*,
  NIM A 808, 21 (2016) (the 10 µm × 5 × 50 mm strip between Plexiglas rods).
- L. Redigolo *et al.*, J. Phys. G 51, 075106 (2024) (¹⁹F(p,α_π) and (p,α₀), CaF₂ fluorine loss under beam)
  (`refs/Redigolo2024_19Fpalpha_JPhysG51.txt`).
- TUNL nuclear data, ¹⁹F(p,αγ) compilations 2021PH03, 1991HE16 (`data/f19/`); J.H. Kelley *et al.*, "Energy levels
  of light nuclei A = 12", NPA 968 (2017) 71 (¹²C 17.23 MeV).
- MEG II, EPJC 85, 763 (2025) (LiPON on Cu, "no significant deterioration").
- J.D. Costas, "The diffusion of lithium in aluminum" (1963, UNT digital library) (D₀ = 4.5 cm²/s, 33.3 kcal/mol).
- Budker INP / OIST blistering of Cu under 2 MeV protons (bnct.inp.nsk.su, Metals 7, 558 (2017)).
- Carbon build-up: arXiv:1708.09303 (citing a systematic 10¹⁴ C/cm²/µC); Redigolo 2024 (10⁻⁷ mbar, none).
- Boron in Li₂CO₃: US patents 5,219,550 and 2001/0028871 (~500 ppm in brine carbonate, 1 ppm after purification).
- LiF target preparation: arXiv:2208.03425.
