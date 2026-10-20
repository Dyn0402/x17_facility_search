# Birmingham HF-ADNeF — the facility record

Started 2026-10-20. Every number has its source; **(ask)** marks what could not be found publicly.
Confidence codes as in `survey/SOURCES.md`: V verified (document read), S search summary, E estimate.

## 1. Where and what

- **Site:** High Flux Accelerator-Driven Neutron Facility (HF-ADNeF), School of Physics and Astronomy,
  University of Birmingham, Edgbaston, Birmingham B15 2TT, UK (52.45 N, 1.93 W). The accelerator sits
  in a new underground bunker extension; the neutron target room is in the Medical Physics building,
  one floor below the MC40 cyclotron's switching-magnet room. Wheldon, JINST 17 (2022) C10010
  (`refs/Wheldon2022_JINST.pdf`). **V**.
- **Commissioned 7 December 2023.** Cost ~€15M (85 % UK science council via NNUF/EPSRC, 15 % university).
  A national user facility for fission/fusion materials, with nuclear data, medical physics and nuclear
  astrophysics among its uses. Wheldon, STFC Accelerator Institute seminar, 6 Feb 2025
  (<https://indico.cern.ch/event/1503042/contributions/6326813/>). **V**.
- **Accelerator:** Neutron Therapeutics "hyperion"-type electrostatic machine (the nuBeam BNCT
  accelerator, as installed in Helsinki): ECR source, 14 HV stages, protons (and deuterons) at
  **0.4–2.6 MeV nominal, 2.8 MeV maximum**, < 50 mA; 117 kW on target at 45 mA, 2.6 MeV; 40 % wall-plug
  efficiency. A dipole switching magnet sends the beam to the target. Seminar 2025; Brooks et al.,
  poster (CERN Indico 1388874). **V**.
- **Target:** a 1 m rotating wheel of 16 micro-channel water-cooled Cu petals (10 × 10 cm²) with
  ~300 µm natural Li bonded on; 600 rpm, 300 l/min of water, ~100 kW removed; target life > 1000 h.
  The wheel turns inside a titanium vacuum vessel; neutrons leave through its wall (4 mm Ti in the
  seminar, "6 mm Ti exit window" in the Nuclear Physics News portrait). A graphite moderator under the
  target gives ~10⁹ n/cm²/s thermal at the same time. A robot (TWEAK) changes petals: ⁷Be reaches
  6 TBq per target. Lead shielding around the target. Seminar; poster; portrait (Nucl. Phys. News 34 (2024) 4). **V/S**.

## 2. Beam numbers

| quantity | value | source | conf. |
|---|---|---|---|
| reaction | ⁷Li(p,n)⁷Be, Q = −1.644 MeV, threshold 1.881 MeV | seminar | V |
| yield | **> 3×10¹³ n/s at 30 mA, 2.6 MeV** (seminar slide 10: "> 1×10¹³"; 2026 article: up to 1×10¹⁴ n/s) | Wheldon 2025; poster; J. Radioanal. Nucl. Chem. (2026) | V/S |
| flux | "up to 1×10¹² n/cm²/s" at the target position | seminar; JINST 2022 | V |
| spectrum | 0.1–0.9 MeV, forward 0–55°; max E_n 0.9 MeV at 2.6 MeV (1.1 MeV at 2.8 MeV) | seminar; poster; 2026 article | V |
| user positions | "user end stations are positioned [at the Ti target structure] to utilise the high-flux fast neutron beam"; target room "about 4 m³ in which equipment and testing rigs can be mounted" | poster; portrait | V/S |
| room shielding | borated polyethylene lines the target room and beam-switching area walls | poster | V |
| collimated port | **none described** | — | (ask) |
| target γ, 478 keV | ⁷Li(p,p'γ) ≈ 6×10⁻⁵ γ/p (thick Li, 2.5 MeV: 3.66×10¹² /s at 10 mA) plus ⁷Be decay (10.4 % of up to 6 TBq) | Taskaev et al. 2006 (BINP), search summary | S |
| target γ, 14.6–18.2 MeV | ⁷Li(p,γ)⁸Be through the 441 and 1030 keV resonances + direct capture: ~1×10⁻⁷ γ/p | `demokritos/neutron/NEUTRON_BEAM.md` §5 | E |
| deuterons | planned: ⁷Li(d,n) to ~17 MeV, ×2–5 flux, needs shielding upgrades | seminar; STFC workshop Sep 2026 | V |
| team | M. Freer (PI), C. Wheldon (director), J. Bishop (neutron lead), B. Phoenix (technical lead), T. Kokalova | seminar | V |

`bham_beam.py` models the thick-target 0° spectrum (slowing-down Monte Carlo, CM-isotropic stand-in,
normalised to 3×10¹³ n/s at 30 mA, 2.6 MeV): **4.8×10¹² n/s/sr at 0°** (×2.0 the 4π average), mean
0.49 MeV, max 0.89 MeV; at 2.8 MeV 5.6×10¹² n/s/sr, max 1.10 MeV. Through the Ø8 cm cell spot
2 m from the target: **6.0×10⁹ n/s** (7.1×10⁹ at 2.8 MeV).

## 3. What it would take to host MX17

- **There is no beam line.** Users mount rigs at the Ti vessel, in the 4π field of a 3×10¹³ n/s source.
  The arms cannot sit there: at 1 m every arm would see ~10¹¹ n/s. The X17 set-up needs a
  **shield wall with a collimator** between target and apparatus (the same thing a BNCT beam-shaping
  assembly does, without the moderator), the cell ≥ 2 m from the target, and a beam dump behind it.
  `FEASIBILITY.md` §3 sizes it. Room dimensions **(ask)**.
- **γ filter.** Through an open Ø8 cm collimator at 2 m: ~1×10⁹ γ/s at 478 keV and ~2×10⁶ γ/s at
  15–18 MeV cross the cell. A Pb (or Bi) filter in the collimator trades γ for neutrons (§3).
- **Beam energy.** Choose 2.8 MeV (the maximum): ×1.17 the neutrons and a harder spectrum, still
  entirely below the 2.75 MeV window edge.
- **Duty.** DC beam; target change by robot every > 1000 h.
- **Deuterons** would move the source towards NFS's hard spectrum (up to 17 MeV): keep protons.

## 4. Sources

- C. Wheldon, *University neutrons: the high-flux accelerator facility at Birmingham*, STFC Accelerator
  Institute seminar, 6 Feb 2025 (22 slides; not kept: 17 MB).
- A. D. Brooks, Tz. Kokalova, C. Wheldon, J. Bishop, B. Phoenix, M. Freer, *Neutron beams at Birmingham:
  HF-ADNeF*, poster, <https://indico.cern.ch/event/1388874/contributions/5883545/> (not kept: 6.5 MB).
- C. Wheldon, *Position sensitive detector applications in nuclear physics at Birmingham*, JINST 17 (2022)
  C10010. `refs/Wheldon2022_JINST.pdf`.
- C. Wheldon et al., *A Birmingham Laboratory Portrait*, Nucl. Phys. News 34 (2024) 4 (paywalled; quotes
  from a search summary).
- *Radioisotope research at the Birmingham accelerator facilities*, J. Radioanal. Nucl. Chem. (2026),
  doi:10.1007/s10967-026-11140-3 (abstract via search).
- C. L. Lee, X.-L. Zhou, NIM B 152 (1999) 1 (thick-target ⁷Li(p,n) kinematics; max 787 keV at 2.5 MeV):
  `survey/refs/LeeZhou1999_thickLi.pdf`.
- S. Taskaev et al. (BINP), 478 keV yield of thick Li targets (2006 table; 2021 NIM B, 0.65–2.225 MeV).
