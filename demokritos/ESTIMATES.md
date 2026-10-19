# Demokritos: the pre-Geant4 estimates

Written 2026-10-19. Code: `demokritos_rates.py` → `out/*.csv`, `out/figures/`. Run with the nTof_x17 venv python
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
