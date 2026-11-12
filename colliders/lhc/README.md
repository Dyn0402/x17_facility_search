# LHC experiments: ALICE (Run 3, ALICE 3), LHCb, ATLAS/CMS, FASER

*2026-11-12.* Part of [`colliders/`](../README.md); results in [`../X17_COLLIDERS.md`](../X17_COLLIDERS.md) §6.

## Read this first

- **ALICE** is the only LHC detector built for soft central dielectrons. Run 3 ITS2 has 3 inner
  MAPS layers at 2.2–3.8 cm, 0.36 % X₀ each, right outside a 0.8 mm Be pipe. At 0.5 T an
  ITS-standalone track needs pT ≳ 18 MeV and an ITS+TPC track pT ≳ 0.12 GeV. ALICE has taken
  special **0.2 T** pp runs for low-mass dielectrons; there the thresholds drop to 7 and 48 MeV.
  Pipe conversions at 0.5 T land at m_fake ≈ 6 MeV (2.3 MeV at 0.2 T), below the X17 window.
- **ALICE reach (10¹² pp, 3σ):**
  - ITS standalone: BR(π⁰ → γX17) 2.8×10⁻⁸ stat / 6.8×10⁻⁷ with a 0.1 % systematic;
    BR(η → γX17) 1.5×10⁻⁷ / 3.9×10⁻⁶;
  - ITS+TPC: 6.1×10⁻⁸ / 4.7×10⁻⁷ for π⁰, with σ_M 0.32 MeV and TPC electron ID.
  This is the best Run-3 option (write-up §6).
- **ALICE 3** (Run 5+, LoI level): vertex layers in the beam vacuum at r = 0.5–2.5 cm, 0.1 % X₀.
  It has essentially no material before the first hit. At 2 T, conversions on the layer at 1.2 cm
  fake m ≈ 14 MeV.
- **LHCb**: the dipole sweeps soft leptons out of the forward spectrometer, and the VELO RF foil
  is the material. Dark-photon proposals cover m < 2m_μ through D*⁰ → D⁰A′(e⁺e⁻) (Ilten, Thaler,
  Williams, Xue, PRD 92 (2015) 115017, from memory: verify). The X17 coupling to charm is
  unconstrained, so this probes a different combination. It is not simulated here.
- **ATLAS / CMS**: tracking thresholds of 0.1–0.5 GeV in 2–3.8 T. An X17 with E ≳ 5 GeV opens
  < 7 mrad, and pipe conversions fake m ≈ 0.6·B·r_c ≈ 30–50 MeV. They have no soft-dielectron
  programme, so no.
- **FASER**: needs a long-lived X17. The ATOMKI-favoured ε_e ≳ 7×10⁻⁴ gives cτ ≲ 10 µm, so FASER's
  dark-photon band (ε ~ 10⁻⁵–10⁻⁴) sits below the X17 band. No.

## ALICE as modelled (`toy/detectors.py: alice(), alice3()`)

| element | r | x/X₀ | resolution | source |
|---|---|---|---|---|
| Be beam pipe | 1.9 cm (ask) | 0.23 % (0.8 mm) | n/a | ALICE Run 3 pipe, from memory (ask) |
| ITS2 inner barrel ×3 | 2.24, 3.01, 3.78 cm | 0.36 % | 5 µm, \|z\| < 13.5 cm | ITS2 TDR (from memory: verify) |
| ITS2 middle + outer ×4 | 19.6, 24.5, 34.4, 39.3 cm | 0.8 % | 5 µm | ITS2 TDR (from memory: verify) |
| TPC inner containment | 80 cm | 0.8 % (ask) | n/a | |
| TPC Ne-CO₂-N₂ | 85–247 cm, 152 rows | X₀ ≈ 314 m | σ_rφ 0.8 mm, σ_z 1 mm (ask) | |
| field | 0.5 T; 0.2 T special runs | | | |
| track cuts | ITS+TPC: IB ≥ 2 + TPC ≥ 70; ITS-SA: IB 3 + OB ≥ 2 | | vertex σ 20 µm | |
| ALICE 3 vertex | 0.5, 1.2, 2.5 cm in vacuum | 0.1 % | 2.5 µm | ALICE 3 LoI (arXiv:2211.02491), approximate |
| ALICE 3 outer | 3.7 cm vessel, then 7–80 cm, 7 layers | 0.1 %, 1 % | 5 µm | approximate |

## Open (ask)

- ITS2 layer radii and X₀ from the TDR (the values above are from memory).
- ALICE Run 3 minimum-bias pp and Pb–Pb samples with ITS-standalone tracks kept down to ~20 MeV.
  Also the 0.2 T pp sample size. The toy uses 10¹² pp at both fields.
- ALICE 3 field options (is 0.5 T foreseen?) and the iris geometry.
