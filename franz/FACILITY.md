# FRANZ (Frankfurt Neutron Source) — the facility record

Started 2026-10-21. Every number has its source; **(ask)** marks what could not be found publicly.
Confidence codes as in `survey/SOURCES.md`: V verified (document read), S search summary, E estimate.

## 1. Where and what

- **Site:** Frankfurter Neutronenquelle am Stern-Gerlach-Zentrum (FRANZ), Institut für Angewandte Physik (IAP),
  Goethe University Frankfurt, experimental hall of the physics building, Riedberg campus, Max-von-Laue-Str. 1,
  60438 Frankfurt am Main, Germany (≈ 50.17 N, 8.63 E). Initiated in the early 2000s. IPAC 2023 TUPM128;
  IPAC 2010 MOPEC059 ("the physics faculty new experimental hall"). **V/S**.
- **Purpose:** keV neutrons for nuclear astrophysics (s-process activations and TOF capture), applied physics.
  The Karlsruhe 4π BaF₂ array was moved here for TOF capture. Reifarth et al., *Neutron reactions in
  astrophysics*, arXiv:1403.5670 (`survey/refs/arxiv_1403.5670.pdf`) §5.1. **V**.
- **Accelerator (as built):** CHORDIS filament volume ion source (from GSI; up to 60 mA total, ~45 % protons,
  35 keV) + an electrostatic post-accelerator to 60 keV; LEBT with solenoids; a **coupled 175 MHz 4-rod RFQ
  (700 keV) + 1.3 MV IH-DTL → 2.0 MeV** in one cavity (single 250 kW amplifier). Hähnel et al., IPAC 2023
  TUPM128, LINAC 2024 TUPB021, IPAC 2025 TUPS039. **V**.
- **Original design (not all built):** 100–250 mA DC volume source, 1.8–2.2 MeV with 20 keV resolution via a
  drift-tube cavity after the IH, nominal ≤ 20 mA DC on target; a chopper + Mobley bunch compressor for
  1 ns, 250 kHz pulses (TOF mode, peak current several A). arXiv:1403.5670; arXiv:0909.5279. **V**.

## 2. Status (as of the last public report, June 2025)

| milestone | date | source | conf. |
|---|---|---|---|
| first 35 keV protons (CHORDIS) | 11/2020 | IPAC 2023 | V |
| 60 keV beam to the RFQ injection | 10/2021 – end 2021 | IPAC 2023, 2025 | V |
| new 60 keV RFQ electrodes mounted | summer 2023 | IPAC 2025 | V |
| **RFQ at 700 keV with beam, up to 11 mA macro-pulse; 7.1 mA matched, 92.7 % transmission** | end 2023 – 2024 | LINAC 2024 | V |
| RFQ bunch length 1.12 ns FWHM measured | 2024 | IPAC 2025 | V |
| IH-DTL conditioned standalone, 10 kW CW for 6 h | Dec 2024 – 2025 | IPAC 2025 | V |
| coupled RFQ-IH-DTL tuning; RF conditioning | "summer 2025" (planned) | IPAC 2025 | V |
| **2 MeV beam + first neutron experiments** | **"end of 2025" (planned)**; not confirmed found | IPAC 2025 | V (plan) / (ask) |
| radiation-safety preparation for 2 MeV and neutrons | "within 2025" | IPAC 2025 | V |

The 2023 paper had hoped for 2 MeV in 2024; the schedule has slipped by about a year at each step.
**No report of 2 MeV beam or first neutrons was found (searched 2026-10-21).** (ask)

## 3. Beam numbers

| quantity | value | source | conf. |
|---|---|---|---|
| reaction | ⁷Li(p,n)⁷Be, Q = −1.644 MeV, threshold 1.881 MeV | — | V |
| proton energy | 2.0 MeV (IH-DTL design 2.03 MeV); variable 1.8–2.2 MeV only in the original design | IPAC 2010/2025; arXiv:1403.5670 | V; energy variability (ask) |
| ion source duty today | CHORDIS 0.5–1 ms at 10 Hz (**0.5–1 %**); RFQ run at up to 2 % | LINAC 2024 | V |
| macro-pulse current | up to 11 mA (7.1 mA matched, behind the RFQ) | LINAC 2024 | V |
| **licence** | **< 5 % duty, 1×10¹² n/s** ("current regulatory limits") | IPAC 2025 | V |
| design activation mode | 10¹² n/s total at ≤ 20 mA DC | arXiv:1403.5670 | V |
| design TOF mode | 2×10¹¹ n/s, 1 ns at 250 kHz; 4×10⁷ n/cm²/s at 0.8 m | arXiv:1403.5670; arXiv:0909.5279 | V |
| spectrum | quasi-stellar, "thermal around 30 keV"; at 1.912 MeV a 25 keV Maxwellian into a 120° cone (kinematic collimation) | IPAC 2015 TUXB1 (Wiesner); IPAC 2025 | V |
| Li target | ~10 µm Li evaporated on Cu (thesis); solid and liquid Li studied | Frankfurt thesis (search); IPAC 2010 | S; as built (ask) |
| target cooling / power limit | not found | — | (ask) |
| bunch compressor installed? | not mentioned in 2023–2025 reports | — | (ask) |
| experimental areas | an activation position directly behind the target; a TOF area (0.8 m flight path) | arXiv:0909.5279 Fig. 3 | V; dimensions (ask) |
| neutron/γ monitors | six detectors acquired for the hall | IPAC 2025 | V |

`franz_beam.py` models the target (`FEASIBILITY.md` §1): the slowing-down MC normalised to the design
5×10¹⁰ n/s per mA at 2.0 MeV (the model's own σ/S gives 7.5×10¹⁰; LiLiT measured ~2×10¹⁰ at ~1.92–1.94 MeV,
the model gives 1.5×10¹⁰ there). At 2.0 MeV: 1.4×10¹⁰ n/s/sr/mA at 0°, ×3.6 the 4π average, mean 143 keV,
max 231 keV at 0°; through the Ø8 cm spot at 0.5 m, **2.9×10⁸ n/s per mA**.

## 4. What it would take to host MX17

- **A thin Li layer.** A Li layer just thick enough to bring the protons to the (p,n) threshold (~0.6 mg/cm²,
  ~12 µm at 2.0 MeV) never lets them cross the 441 and 1030 keV ⁷Li(p,γ)⁸Be resonances, so the 15–18 MeV γ
  drop from ~10⁻⁷ to ~5×10⁻¹⁰ per proton (direct capture only, estimate). This is FRANZ's own target style
  (~10 µm evaporated Li) — confirm (ask). With a thick target the γ correlated term dominates (`FEASIBILITY.md` §3).
- **Beam on target for weeks at the licence limit,** better at DC. Today's ion source gives ≤ 1 % duty; the
  licence allows 5 %; the design (and the reach headline) is 20 mA DC = 10¹² n/s, which is also the licence's
  neutron limit.
- **Room for the arms 0.5 m from the target, behind ~20–30 cm of borated PE.** Keyed to the hall layout
  (ask). The beam-line end, target chamber and shielding are FRANZ's to define.
- **Energy:** 2.0 MeV fixed (the IH-DTL). 2.2 MeV would raise the neutrons per mA ×3.8 but the 10¹² n/s cap
  then binds: it only helps in the pulsed regime (ask whether energy variation exists).
- **Timing:** a DC or macro-pulsed beam (the DAQ can be gated on the macro-pulse); the 250 kHz bunched mode
  is not needed.

## 5. People (public)

- Accelerator: H. Hähnel (commissioning lead, haehnel@iap.uni-frankfurt.de, on the papers), H. Podlech,
  U. Ratzinger, C. Zhang (IAP / HFHF / GSI).
- Nuclear astrophysics users: T. Heftrich (DPG 2025 group report "Neutron activations for nuclear
  astrophysics"), K. Göbel; R. Reifarth (founding user; current affiliation (ask)).

## 6. Sources

- H. Hähnel et al., *Current status of beam commissioning at the Frankfurt Neutron Source*, IPAC 2025 TUPS039,
  doi:10.18429/JACoW-IPAC2025-TUPS039, <https://proceedings.jacow.org/ipac2025/pdf/TUPS039.pdf> (licence < 5 %
  duty, 10¹² n/s; 2 MeV planned end of 2025). PDF not kept (read 2026-10-21).
- H. Hähnel et al., LINAC 2024 TUPB021, doi:10.18429/JACoW-LINAC2024-TUPB021,
  <https://proceedings.jacow.org/linac2024/pdf/TUPB021.pdf> (CHORDIS 0.5–1 ms at 10 Hz; 11 mA; 92.7 %).
- H. Hähnel et al., IPAC 2023 TUPM128, <https://proceedings.jacow.org/ipac2023/pdf/TUPM128.pdf> (history, CHORDIS).
- C. Wiesner et al., *FRANZ and small-scale accelerator-driven neutron sources*, IPAC 2015 TUXB1,
  <https://accelconf.web.cern.ch/IPAC2015/papers/tuxb1.pdf> (1.912 MeV 25 keV Maxwellian, 120° cone).
- R. Reifarth et al., arXiv:1403.5670 (`survey/refs/`) (≤ 20 mA DC, 10¹² n/s, 2×10¹¹ n/s TOF).
- R. Reifarth et al., *Opportunities for nuclear astrophysics at FRANZ*, PASA 26 (2009) 255, arXiv:0909.5279.
- U. Ratzinger et al., IPAC 2010 MOPEC059, <https://accelconf.web.cern.ch/ipac10/papers/mopec059.pdf>.
- S. Alzubaidi et al., *The Frankfurt neutron source FRANZ*, EPJ Plus 131 (2016) 124 (paywalled; not read).
- LiLiT check: `survey/SOURCES.md` (SARAF, ~2×10¹⁰ n/s/mA).
- Thin-target ⁸Be γ: the ⁷Li(p,γ) resonances from `lnl/` (441 keV σ 5.9 mb, Γ 12.2 keV; 1030 keV Γ 168 keV).
