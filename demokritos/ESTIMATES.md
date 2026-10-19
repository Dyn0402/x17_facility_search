# Demokritos: the pre-Geant4 estimates, and the Geant4 check

Written 2026-10-19. **§6 has the Geant4 result, which replaces the toy's days.** Code: `demokritos_rates.py` → `out/*.csv`, `out/figures/`. Run with the nTof_x17 venv python
(about 1 min).

These are analytic yields and a toy acceptance. They are **calibrated on the LNL Geant4 result**: the same hardware,
the same 9–10 MeV leptons, and the same reference 3D fit, with MM 15° + TOF. The calibration takes two numbers from
`lnl/out/talk/numbers.json`:

- **selected X17 per day.** ε after the two-arm geometry: 0.042 as built, 0.33 with the big plastics. It is the LNL
  Geant4 selected rate divided by the toy's two-arm X17 acceptance.
- **days to 3σ.** k = Geant4 days / toy counting days on the LNL reference: 30.2 as built, 1.77 big plastics.
  Days at Demokritos = k × the same toy's counting days for ⁴He.

So every number below says "as fast as LNL would be, scaled by what is different in ⁴He". The differences are:

- the window: 105–160° instead of 130–180°;
- the E1 IPC instead of M1;
- no γ₁;
- the yield;
- the target backing.

Geant4 replaces the scaling (`GEANT_PREP.md`).

---

## 1. Yields (1 µA, T/Ti = 1.5)

| scenario | E_p | Ti | E\* (mean) | γ/s | IPC/s | E0 pairs/s | **X17/day, 4π** at B_x |
|---|---|---|---|---|---|---|---|
| ATOMKI 2021 | 510 | 4.2 mg/cm² (stops) | 20.1 | 1.3×10³ | 6.1 | 0.005 | 590 |
| ATOMKI 2021 | 610 | 4.2 | 20.1 | 2.1×10³ | 9.7 | 0.006 | 930 |
| ATOMKI 2019/21 | 900 | 4.2 | 20.3 | 5.7×10³ | 26 | 0.008 | 2.5×10³ |
| **Demokritos Ti-T as is** | **900** | **2.1** (exits at 470 keV) | 20.4 | **4.6×10³** | **21** | 0.003 | **2.0×10³** |
| Demokritos Ti-T | 800 | 2.1 | 20.3 | 3.8×10³ | 18 | 0.004 | 1.7×10³ |
| Demokritos Ti-T | 1000 | 2.1 | 20.4 | 5.4×10³ | 25 | 0.002 | 2.4×10³ |
| thick Ti-T | 1000 | 4.2 (stops) | 20.4 | 7.4×10³ | 34 | 0.008 | 3.3×10³ |
| PAPAP, **100 µA** | 250 | 2.1 (stops) | 19.9 | 2.1×10⁴ | 98 | 0.27 | 9.4×10³ |

- For comparison, LNL (Li₂O 300 µg/cm², 1.10 MeV) gives 1.9×10³ γ₀/s and **920 X17/day**. **A Ti-T target gives
  ~2× the X17 per µA** of the ⁸Be case, because it is thick: the beam crosses ~400 keV of tritide.
- Beam power is I × E_p, 0.9 W per µA at 900 keV. On a 1 mm Cu backing that is nothing. On thin backings with rim
  cooling (`out/heat.csv`, spot r = 2.5 mm, rim r = 12.5 mm):

  | backing | 1 µA | 3 µA | 10 µA |
  |---|---|---|---|
  | Al 25 µm | +39 K | +117 K | +390 K |
  | Cu 50 µm | +12 K | +35 K | +115 K |
  | Cu 100 µm | +6 K | +17 K | +58 K |

  So Cu 100 µm takes ~10 µA if the tandem can give it; Cu 50 µm takes ~3 µA.

## 2. Acceptance and the backing (toy, four n_TOF arms)

- The X17 edge is at 111.7° (m = 16.94, E\* = 20.49). The **two-arm acceptance for X17 pairs is 38 %**, about half
  through adjacent arms. For the E1 IPC it is 13 %.
- **A thick backing blocks every downstream lepton.** The X17 acceptance drops to 9.5 %. Moving the target 6–18 cm
  downstream of the arm centre, so that the arms look at it from upstream, wins back to 12–14 %.
- **Days to 3σ at B_x(ATOMKI)**, 900 keV, Demokritos Ti-T (2.1 mg/cm²), **1 µA**, LNL-calibrated. Figure:
  `figures/reach_backing.png`.

  | backing | window | X17 acc | S/B | n_TOF stack **as built**: X17 sel/day, days | **big plastics**: X17 sel/day, days |
  |---|---|---|---|---|---|
  | none (ideal) | 105–160 | 0.38 | 1.1 % | 32, **33 d** | 250, **1.9 d** |
  | Al 25 µm | 105–160 | 0.38 | 1.1 % | 32, 34 d | 250, 2.0 d |
  | **Cu 50 µm** | 105–180 | 0.38 | 1.0 % | 32, **39 d** | 250, **2.3 d** |
  | Cu 100 µm | 100–180 | 0.38 | 0.9 % | 32, 43 d | 250, 2.5 d |
  | Cu 1 mm, scattering | 100–180 | 0.38 | 0.8 % | 32, 69 d | 250, 4.1 d |
  | **Cu 1 mm, blocking (the target as it is)** | 105–150 | 0.095 | 1.3 % | 8, **121 d** | 63, **7.1 d** |
  | Cu 1 mm, blocking, target +6 cm | 105–150 | 0.12 | 1.3 % | 10, 91 d | 80, 5.3 d |
  | Cu 1 mm, blocking, target +12 cm | 105–150 | 0.14 | 1.3 % | 11, 81 d | 90, 4.7 d |

  - "scattering" treats the 1 mm Cu as Highland smearing on the downstream legs (path capped by the disk radius) and
    ignores energy loss and EPC. "blocking" throws those legs away. The truth is in between, and Geant4 will tell.
  - 5σ is ×2.8 the 3σ days. Days scale as 1/I.

- **Against the X17 mass** (900 keV, ideal backing): m = 16.6 → 17.3 gives 36 → 28 d as built, 2.1 → 1.6 d with the
  big plastics (`out/mass_scan.csv`). The edge moves 109 → 117°.

## 3. Reach: the summary

At **1 µA, 900 keV, a thin Cu 50 µm backing, 3σ at ATOMKI's B_x**:

| | X17 selected/day | **3σ** | 5σ |
|---|---|---|---|
| n_TOF stack as built | 32 | **39 d** | ~110 d |
| **big plastics** (trigger_scint, the LNL upgrade) | 250 | **2.3 d** | ~6.4 d |
| big plastics, thick ATOMKI-type target (4.2 mg/cm²) | 310 | 1.9 d | 5.2 d |
| big plastics, the existing 1 mm Cu target, +12 cm | 90 | 4.7 d | 13 d |
| big plastics, PAPAP 100 µA at 250 keV (Cu 50 µm) | 1.2×10³ | 0.5 d | 1.4 d |

- **Against LNL** (⁸Be, 1 µA): 17 d as built, 1.0 d big plastics. **⁴He at Demokritos is ~2× slower per µA**, though
  it has ~2× the X17. The ⁴He edge sits where the E1 IPC is flatter and higher, so S/B is 1 % against 7 %.
- **If ATOMKI's own fitted IPC is right** (IPCC 1.1×10⁻⁴ at 900 keV, 24× below the Born E1, `PHYSICS.md` §4), every
  background drops ×42. Then 3σ takes **~0.9 d as built and ~1.3 h with the big plastics** (Cu 50 µm). The
  first day of running decides which normalisation is true, because MX17 measures the absolute IPC from 40° to 180°.
- **Systematics.** At S/B ≈ 1 % the IPC shape must be known to a fraction of a percent. The calibration factor k
  carries the LNL 3D fit with its 2 % shape-error model, but that was tested at S/B = 7 %. At 1 %, a 2 % unknown
  shape error is **2× the signal**: the angle-only fit would fail, and only the |y| and E_sum dimensions save it.
  Treat the baseline days as optimistic by an unknown factor until the Geant4 templates and a 3D-fit pseudo-data
  test (as in LNL §14–17) are redone for ⁴He. This is the main open risk.

## 4. What is not in these numbers

| assumption | stand-in for | replaced by |
|---|---|---|
| ε and k from LNL (opposite-arm pairs at ~140°) | trigger and selection efficiency for ~50 % adjacent-arm pairs at ~115° | D1/D2 Geant4 |
| γ\* direction isotropic | E1 sin²θ about the beam | Geant4 generator with the anisotropy (as LNL L7) |
| backing blocks or Highland-scatters | EPC, energy loss, backscatter in the backing and holder | D3 (γ at 20.5 MeV) |
| σ(p,γ) from the Hahn fit, ±30 % | the absolute γ yield | the in-run γ monitor |
| T/Ti = 1.5 | the real loading of a new target | **(ask)** the supplier |
| 1 µA | the post-upgrade current at 0.9 MeV | **(ask)** the lab |
| cosmics ~1/day after MM 15° + TOF + E_sum (from LNL L4) | — | the same L4 sample, re-cut with the ⁴He window |

## 5. Ruled out: the neutron beams

The Demokritos neutron beams give 10⁵–10⁶ n/cm²/s at the sample. Take the n_TOF 500 bar × 1 cm capsule and a 5 cm²
beam at 0.35 MeV, with Viviani's σ_pair = 0.062 µb: that is **36–360 IPC pairs/day and 0.05–0.5 X17/day into 4π**
(X17/IPC = 1.5×10⁻³). It is ~10⁴× below p + t on Ti-T at 1 µA (`out/neutron_option.csv`).

## 6. Geant4 result (D1–D3, 2026-10-19)

Code: `sim/demok_geant.py` → `out/geant/` (`acceptance_geant.csv`, `reach_scan.csv`, `reach_geant.csv`,
`figures/geant_theta.png`). Tables fetched with `sim/fetch_sel.sh`. The selection is the LNL one: MM 15° + TOF, the
LNL-calibrated calorimetry, and an E_sum window, scanned. Weights are per day at 1 µA, 900 keV, on Demokritos' Ti-T.
The γ\* anisotropy of E1 capture is applied to the IPC. Cosmics come from LNL L4. **Statistics only.**

### 6.1 Acceptance

| target | hardware | X17 selected/day (MM 15° + TOF, before the E_sum window) | σ68(Δθ) | opposite-arm fraction | both legs upstream |
|---|---|---|---|---|---|
| Cu 50 µm | as built | 32 | 10.2° | 0.34 | 0.40 |
| Cu 50 µm | big plastics | 259 | 8.8° | 0.43 | 0.34 |
| Cu 1 mm | as built | 20 | 13.5° | 0.38 | 0.76 |
| Cu 1 mm | big plastics | 155 | 13.4° | 0.46 | 0.70 |
| Cu 1 mm, +12 cm | as built | 42 | 11.3° | 0.47 | 0.97 |
| Cu 1 mm, +12 cm | big plastics | 167 | 10.4° | 0.53 | 0.94 |

- For Cu 50 µm, Geant4 reproduces the toy's selected rate: 32 and 259 per day, against the toy's 32 and 250.
- The 1 mm Cu blocks the downstream legs, as the toy assumed. Moving the target to +12 cm keeps 0.97 of the pairs
  fully upstream, and it **gains rate**: 42/day as built, against 32 for Cu 50 µm. The as-built trigger stack
  covers the upstream faces of the arms better.

### 6.2 Days to 3σ at B_x(ATOMKI), 1 µA

| target | hardware | counting (B known) | fit θ | **fit θ × \|y\|** | fit θ × \|y\| × n_down | S/B in window | EPC share of B |
|---|---|---|---|---|---|---|---|
| Cu 50 µm | as built | 36 d | 121 d | **45 d** | 36 d | 1.1 % | 3 % |
| Cu 50 µm | big plastics | 3.0 d | 9.5 d | **3.4 d** | 3.0 d | 1.5 % | 2 % |
| Cu 1 mm | as built | 83 d | 314 d | **94 d** | 59 d | 1.0 % | 7 % |
| Cu 1 mm | big plastics | 6.4 d | 23 d | **7.5 d** | 6.2 d | 1.3 % | 4 % |
| **Cu 1 mm, +12 cm** | as built | 31 d | 84 d | **35 d** | 31 d | 1.2 % | 15 % |
| **Cu 1 mm, +12 cm** | big plastics | 4.2 d | 10 d | **3.6 d** | 3.5 d | 2.3 % | 1 % |

The fits float the IPC and EPC normalisations and hold the cosmics fixed. They use θ ≥ 80° (§6.4). n_down counts the
legs whose MM centroid lies downstream of the target, so it tells which legs crossed the backing. Each column is the
best E_sum window for that column. 5σ is ×2.8 the 3σ days. Days scale as 1/I.

### 6.3 What it says

- **The toy holds for the thin target.** As built it takes 45 d (toy 39 d); with the big plastics 3.4 d (toy 2.3 d).
  Geant4 is ×1.2–1.5 slower.
- **The existing target is good enough if it is moved 12 cm downstream.** Cu 1 mm at +12 cm reaches 35 d as built
  and 3.6 d with the big plastics. That is as fast as Cu 50 µm, and ×2.3 faster than the toy's 81 d / 4.7 d. So no
  thin-backed target is needed: the lab's Ti-T on 1 mm Cu, on a longer stalk, does the job. The thick backing also
  takes the beam power, where Cu 50 µm stops at ~3 µA.
- **The target as it is, at the centre, costs ×2.**
- **The angle alone does not do it.** With the IPC norm free, a θ-only fit is ×3 slower than θ × |y|. The X17 is
  symmetric in energy and the E1 IPC is not, and that is what the fit uses. Adding n_down helps most when the
  downstream legs carry a different response, as for the thick target at the centre.
- **EPC is minor.** ATOMKI's dominant background is 1–15 % of the background in the X17 window here. The two arms
  at ~110° with MM pointing reject most of it, and it sits below 110° where the IPC is falling.
- **S/B is 1–2 %.** The systematics warning of §3 stands. It is the open item.

### 6.4 Checks and caveats

- **IPC normalisation (D2's 70° bias).** The unbiased `cu50_all` sample agrees with the biased one within 1–3 %
  above 80°, which is within the unbiased statistics (220–430 events). Between 60° and 80° the biased sample is short
  by ~18 %, because smearing carries pairs generated below 70° into that range. The fits therefore start at 80°.
  The days barely move: 42 → 45 d and 3.3 → 3.4 d for Cu 50 µm.
- **EPC statistics.** D3 has 10⁷ γ per config, so **one MC event is ~40 pairs/day**. Only 30–190 events pass the
  selection, and the template is a kernel-smoothed shape from them. For example, the 150–165° bump for Cu 50 µm as
  built is a few events. Because EPC is ≤15 % of B, this changes the days by much less than that. A 10⁸ rerun is
  needed only if EPC comes to matter. The big-plastics EPC is the as-built table scaled by the IPC's big/as-built
  ratio.
- **The window scan is optimistic.** The best of ~40 E_sum windows on templates with few EPC and cosmic events.
  With the window held at the LNL-like 13–23 MeV, Cu 50 µm with big plastics is 3.4 d, the same.
- **Not included:**
  - the systematics of the IPC shape at S/B ≈ 1 %;
  - the γ\* anisotropy, which is a stand-in (1 + 0.1 P₁ − 0.9 P₂);
  - pile-up and the DREAM dead time at the IPC rate. The selected background is ~10⁴/day, so the dead time does not
    matter, but the raw single-arm rate is not yet checked;
  - the 510 and 610 keV points.
