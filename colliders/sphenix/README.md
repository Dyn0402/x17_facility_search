# sPHENIX: X17 → e⁺e⁻ with MVTX + INTT (+ TPC)

*2026-11-12.* Part of [`colliders/`](../README.md); results in [`../X17_COLLIDERS.md`](../X17_COLLIDERS.md) §5.

## Read this first

- 1.4 T curls soft leptons fast. A TPC track (≥ 20 of 48 layers) needs pT ≳ 0.1 GeV. The
  **silicon alone** (3 MVTX + ≥ 2 INTT layers, out to r ≈ 8–10 cm) needs only **pT ≳ 16–20 MeV**.
  Silicon-only tracking is the natural way to see X17 here, as guessed. It reaches π⁰ → γX17 and
  η → γX17 leptons that the TPC loses.
- Momentum resolution from silicon alone is MS- and brems-limited (INTT is 1.14 % X₀ per ladder),
  but the pair mass of a boosted, small-angle pair is set mostly by the opening angle. The MVTX
  measures that 5 mm outside the beam pipe, with 5 µm hits.
- **Trap:** a conversion in the beam pipe (r = 2.0 cm) reconstructed as a primary pair has
  m_fake ≈ 0.6·B·r_c = **16.8 MeV**, right on the X17 mass. MVTX layer 0 conversions land at
  ~21 MeV. These must be removed by vertex compatibility (χ²/DCA with 5 µm MVTX hits) or by a
  pair-vertex fit. In the toy a per-track χ² fails: the fit hides the conversion in two ~3σ kinks
  and ~40 % pass. A pair fit under the conversion hypothesis (common point on the pipe or L0, zero
  opening angle) leaves < 1 % and keeps 77–80 % of the X17 (write-up §5).
- **Reach (10¹⁰ Au+Au MB, 3σ):**
  - silicon only (σ_M 0.5 MeV): BR(π⁰ → γX17) 6.2×10⁻⁸ stat / 8.6×10⁻⁷ with a 0.1 % systematic;
    BR(η → γX17) 4.1×10⁻⁷ / 5.0×10⁻⁶;
  - TPC tracks (σ_M 0.34 MeV, ×6 less acceptance): 1.3×10⁻⁷ / 6.9×10⁻⁷ for π⁰. This is the best
    systematics-limited π⁰ reach of any RHIC configuration.
- No dE/dx in MVTX/INTT, so silicon-only tracks have no electron ID. Soft pions (pT < 60 MeV) are
  a few % of all pions, and hadron pairs are not in the toy.
- The material quoted in the sPHENIX 2025 INTT paper (pipe 1.8 % X₀, MVTX 2.0 % in total, "before
  the INTT") is ×8 the Be-pipe design value. Both versions are run (`_q` = quoted).

## Detector as modelled (`toy/detectors.py: sphenix()`)

| element | r | x/X₀ | resolution | source |
|---|---|---|---|---|
| Be beam pipe | 2.0 cm (ask) | 0.22 % design (0.76 mm Be); 1.8 % quoted | n/a | design value (ask); arXiv:2504.02240 for 1.8 % |
| MVTX L0–L2 | 2.461, 3.198, 3.993 cm | 0.3 % / layer design; 2.0 % total quoted | 5 µm × 5 µm, \|z\| < 13.5 cm | MVTX stave r_min (sPHENIX MVTX design / PRR 2020); arXiv:2504.02240 |
| INTT 4 layers | 7.2, 7.8, 9.7, 10.3 cm | 1.14 % per ladder | 78 µm/√12 rφ, 16 mm/√12 z, \|z\| < 22.8 cm | arXiv:2504.02240, Table 1 |
| TPC inner field cage | 20 cm | 0.6 % (ask) | n/a | IFC at r = 20 cm (sPHENIX TPC design, arXiv:2110.02082) |
| Ar/CF₄ 60:40 gas | 3 slabs | X₀ ≈ 100 m | n/a | gas switch Ne → Ar/CF₄ (CIPANP 2022) |
| TPC | 48 layers, 30.5–77.5 cm | n/a | σ_rφ 0.2 mm, σ_z 0.5 mm (ask) | 48 layers, instrumented from 30 cm (arXiv:2110.02082) |
| field | 1.4 T | | | BaBar coil |
| track cuts | TPC: MVTX ≥ 2 + TPC ≥ 20; Si-only: MVTX 3 + INTT ≥ 2 | | vertex σ 20 µm (ask) | |

## Sources

- [sPHENIX, charged-hadron multiplicity with the INTT (arXiv:2504.02240)](https://arxiv.org/pdf/2504.02240): INTT radii, 1.14 %/ladder, "beam pipe (1.8 % X/X₀) and the MVTX (2.0 % X/X₀)"
- [sPHENIX INTT specification table](https://www.sphenix.bnl.gov/sites/default/files/2025-04/sPH-BULK-2025-01-Tab1.pdf)
- [Overview and Design of the sPHENIX TPC (arXiv:2110.02082)](https://arxiv.org/pdf/2110.02082)
- [sPHENIX MVTX installation PRR (2020)](https://www.phenix.bnl.gov/WWW/publish/mxliu/sPHENIX/Reviews/BNL-PRR-12152020/20201215_PRR_MVTX_Installation_r1.pdf)

## Open (ask)

- Which material number is right at normal incidence: 0.22 % or 1.8 % for the pipe? It is the
  difference between a 0.7 MeV and a 2.2 MeV scattering floor.
- Does the sPHENIX tracking (ACTS) seed silicon-only tracks down to ~20 MeV, and are
  streaming-readout Au+Au and pp events stored with MVTX + INTT for a soft-pair analysis?
- Usable minimum-bias Au+Au sample with full silicon readout. The toy uses 10¹⁰.
