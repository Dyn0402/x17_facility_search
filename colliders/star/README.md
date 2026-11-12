# STAR: X17 → e⁺e⁻ in the iTPC

*2026-11-12.* Part of [`colliders/`](../README.md); results in [`../X17_COLLIDERS.md`](../X17_COLLIDERS.md) §5.

## Read this first

- STAR's only tracker today is the TPC (HFT, IST and SSD left after 2016). A lepton needs ~15 pad
  rows, i.e. it must reach r ≈ 79 cm, so **pT ≳ 60 MeV at 0.5 T**. That matches the iTPC design
  figure of 60 MeV/c.
- Consequence: **X17 at rest (the ATOMKI nuclear physics, 8.4 MeV leptons) is invisible**. X17
  from π⁰ → γX17 survives only for boosted π⁰ (p_X ≳ 0.15 GeV). X17 from η → γX17 is well
  inside the acceptance: p* = 274 MeV, so a typical lepton has 0.1–0.3 GeV.
- Scattering is not the limit. 0.28 % X₀ of Be pipe plus 0.62 % of inner field cage give
  σ(m_ee) ≈ 1.2 MeV at 17 MeV with the vertex constraint (§3 of the write-up).
- Beam-pipe conversions reconstructed as primary pairs land at m_fake ≈ 0.6·B·r_c ≈ 6 MeV.
  ~90 % of them pass a vertex χ², because the first TPC hit is 55 cm out. A pair fit under the
  conversion hypothesis leaves 1.5 %, and those sit below the X17 window.
- **Reach (10¹⁰ Au+Au MB, 3σ):** BR(π⁰ → γX17) 1.2×10⁻⁷ on statistics, 2.4×10⁻⁶ with a 0.1 %
  background-shape systematic. BR(η → γX17) 5.3×10⁻⁷ and 1.1×10⁻⁵. STAR is the weakest of the
  configurations once systematics count, because its 1.2 MeV resolution lets ×3 more Dalitz
  pairs into the window than silicon does.
- Electron ID at 60–300 MeV comes from TPC dE/dx alone (TOF needs pT ≳ 0.2 GeV), and the e/π bands
  cross near 0.15–0.2 GeV/c. Hadron pairs and combinatorics are **not** in this toy.

## Detector as modelled (`toy/detectors.py: star()`)

| element | r | x/X₀ | resolution | source |
|---|---|---|---|---|
| Be beam pipe | 2.0 cm (ask) | 0.28 % | n/a | STAR TPC field-cage page, "~1 mm Be, 0.28 % X₀" |
| TPC inner field cage | 47 cm | 0.62 % (with gas) | n/a | same page; STAR TPC NIM (nucl-ex/0301015) |
| P10 gas, 50–190 cm | 6 slabs | 1.19 % total (X₀ ≈ 118 m) | n/a | standard |
| iTPC inner sector | 40 rows, 55.5–119 cm | n/a | σ_rφ 0.7 mm, σ_z 1 mm (ask) | first row at 55 cm (STAR distortion study); 40 rows (iTPC proposal) |
| outer sector | 32 rows, 127–190 cm | n/a | σ_rφ 0.6 mm, σ_z 1 mm (ask) | STAR TPC NIM |
| field | 0.5 T (0.25 T as a what-if) | | | |
| track cut | ≥ 15 fit points | | primary vertex σ 0.2 mm (ask) | STAR standard nHitsFit ≥ 15 |

## Sources

- [STAR TPC field cages: material](https://www.star.bnl.gov/public/tpc/hard/tpcrings/page2.html)
- [The STAR TPC (NIM A 499, nucl-ex/0301015)](https://arxiv.org/abs/nucl-ex/0301015)
- [iTPC proposal (2015)](https://drupal.star.bnl.gov/STAR/files/STAR_iTPC_proposal_06_09_2015.pdf): 13 → 40 rows, |η| < 1.5
- [R. Pak, DNP 2018](https://drupal.star.bnl.gov/STAR/files/PakHAW2018.pdf): iTPC "reduces pT threshold to 60 MeV/c"

## Open (ask)

- Beam-pipe radius and wall in the current (post-HFT) configuration.
- Recorded Au+Au 200 GeV minimum-bias sample (2023 + 2025) usable for soft dielectrons. The toy
  uses 10¹⁰.
- Low-pT e/π separation from dE/dx with the iTPC at 60–200 MeV/c. Was any reduced-field running
  ever done with the iTPC?
