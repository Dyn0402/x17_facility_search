# SARAF (Soreq Applied Research Accelerator Facility) — the facility record

Started 2026-11-09. Every number has its source; **(ask)** marks what could not be found publicly.
Confidence codes as in `survey/SOURCES.md`: V verified (document read), S search summary, E estimate.

## 1. Where and what

- **Site:** Soreq Nuclear Research Center (SNRC), Yavne, Israel (≈ 31.905 N, 34.699 E), a centre of the Israel Atomic Energy
  Commission (IAEC). Hosted LINAC'12. **V/S**
- **Machine:** CW superconducting proton/deuteron linac in two phases.
- **Purpose (as published):** nuclear astrophysics (s-process MACS), fundamental interactions, radiopharmaceuticals,
  neutron imaging and diffraction, irradiation; "a user facility for basic and applied nuclear physics"
  (Mardor et al., EPJA 54 (2018) 91, arXiv:1801.06493). **V**

### 1.1 Phase I (ran 2010–~2019; being replaced)

- ECR source, LEBT, four-rod RFQ (1.5 MeV/u), prototype SC module with 6 half-wave cavities, D-plate. arXiv:1801.06493; arXiv:2211.16774. **V**
- **Delivered:** protons up to ~4 MeV, deuterons up to ~5 MeV, currents up to 2 mA (Tessler et al., arXiv:2211.16774);
  M. Paul (CERN n_TOF talk, 2021): "1 mA, ~4 MeV or 1.5–2 mA at 2 MeV (3–4 kW)", deuterons commissioned to < 50 % duty at
  4.8 MeV. Mardor Table 5: Phase I+ rows (with the Phase I target room) protons 1.5–4 MeV, 0.04–2 mA; deuterons 3–5 MeV,
  0.04–2 mA, thick-target rate ~10¹³ n/s (0.03–20 MeV; the deuteron row). **V**
- **Status:** "SARAF Phase I, presently undergoing a major upgrade to its Phase II" (arXiv:2211.16774, 2022). The LiLiT
  experiments are dated 2014–18 ("SARAF I, 2013-2018"; Paul 2021). The new RFQ/MEBT + SC linac replaces the Phase I RFQ/PSM
  chain, so **the Phase I beam (a 1.9–4 MeV CW mA proton beam on LiLiT) is not available today**. **V (2022 text)**, no 2023+
  report of Phase I beam found. **(ask)** whether the PSM can still be operated.

### 1.2 LiLiT, the liquid-lithium target

- Windowless film of liquid Li (~200 °C), **1.5 mm thick, 18 mm wide**, 2–5 m/s on a 0.3 mm stainless wall; beam dump and target
  in one. Tessler et al., PLB 751 (2015), arXiv:1511.04701. **V**
- **Operated:** 1–2 mA, 1.91–1.94 MeV (2–4 kW), runs up to ~10 h continuous; σ_x ≈ 2.8 mm, σ_y ≈ 3.8 mm. arXiv:1511.04701, 1801.06493. **V**
- **Measured yield: 3–5 × 10¹⁰ n/s** at 1–2 mA (quasi-Maxwellian kT ≈ 30–34 keV), ~2 × 10¹⁰ n/s/mA, 30–50× earlier sources;
  same in arXiv:2211.16774, 2406.17646. **V**. The spectrum itself is SimLiT/Geant4, benchmarked by TOF at 180 cm (the
  spectrum at the target "not measurable"). **V**
- **Measured ⁷Li(p,γ)⁸Be γ:** ~3×10⁸ γ/s/mA at 17.6 MeV, ~4×10⁸ γ/s/mA at 14.6 MeV (via ⁹⁰Zr(γ,n)). arXiv:1511.04701. **V**
  = 1.1×10⁻⁷ γ/p. The Birmingham / FRANZ stand-in of 1×10⁻⁷ is therefore **measured here**.
- **Neutron-shielding limit:** in 2013–17 the flux "was limited by the available concreted radiation shielding in the beam
  corridor" (arXiv:1801.06493). **V**
- **A 50 kW LiLiT design exists:** 2.5 MeV, ~20 mA (BNCT and materials); "a low power (6 kW) model of the new design with a
  narrower nozzle" operating at SARAF (Paul et al., EPJ WoC 231 (2020) 03004; search summary only). **S**. Where it would be
  installed: **(ask)**.
- Beam-on-target distance for activation: 6–8 mm (a target is usually *inside* the neutron cone, not 0.5 m away). **V**
  There is no precedent for anything like a 75 cm-arm apparatus around LiLiT.

### 1.3 Phase II (SARAF-LINAC)

- **Design:** p 1.3–35 MeV, d 2.6–40 MeV (Paul talk 2021, from Pichoff IPAC 2019); Table 1 of Mardor: 5–35 MeV p, 5–40 MeV d,
  0.04–5 mA CW + pulsed; pulsed 0–200 kHz single 1 ns (Paul 2021), macro-pulsed. Four cryomodules, CEA/IRFU responsible
  for MEBT and linac; SNRC for source, LEBT, HEBT and targets. arXiv:1801.06493, LINAC 2024 THAA007. **V**
- **Planned neutron stations** (Paul 2021, Mardor 2018): Thermal Neutron Source with a **liquid Ga-In jet**, water moderator,
  Be + PE reflector, 200 kW CW (5 mA × 40 MeV d), 10¹⁵ n/s, thermal camera (4×10⁵ n/cm²/s at L/D 250), diffractometer, rabbit
  (~10¹² n/cm²/s); a neutron TOF facility with solid Li or LiF (up to 200 W average, 1 ns at 200 kHz, 18 m flight path);
  "LiLiT 2" and GaLiT targets at SARAF II; beam dump design. The Phase I "target room" was to be commissioned 2018. **V**
  (The HPTW 2023 talk: main source planned is GaIn; Phase II "in its early commissioning stage" **S**.)
- **Mardor 2018:** thick-Li yield ~10¹⁵ n/s, d on Li peaks at "the beam energy divided by 2.5" (~17 MeV at 40 MeV). **V**

### 1.4 Status of Phase II, 2026

| milestone | date | source | conf. |
|---|---|---|---|
| MEBT delivered | Aug 2020; commissioned with p (CW) and d (pulsed) to end of MEBT | LINAC 2024 THAA007 | V |
| Injector + MEBT p beam commissioning | published 2023 | JINST 18 T12003 | S |
| all CM1–4 qualified at Saclay; **CM1 in the linac tunnel** at Soreq | July 2024 | LINAC 2024 | V |
| "first beam expected at the end of the year" (2024) | plan | LINAC 2024 | V (plan) |
| "Recent events in Israel complicate significantly the commissioning" | July 2024 | LINAC 2024 | V |
| "first cryomodule was installed on the beam line, the commissioning is ongoing" | Oct 2025 | CEA, LCWS2025 (N. Bazin) | V |
| CM2–4 delivered, RF, cryo plant | not found | | (ask) |
| Beam through CM1 (> 1.3 MeV/u) | no report found (searched 2026-11-09) | | (ask) |
| GaIn target / HEBT / LiLiT 2 installed | not found | | (ask) |

Schedules have slipped: 2018 → "~2023" (Mardor 2018) → 2025 (LINAC 2019 status, "operation during 2025") → first beam
"end 2024" → commissioning "ongoing" Oct 2025. A full 40 MeV, 5 mA machine in the 2020s looks unrealistic; a date for neutron
production is unknown. **(ask)**

## 2. Beam numbers used in this study

| quantity | value | source |
|---|---|---|
| LiLiT n/s per mA (1.925 MeV) | 2.5×10¹⁰ (3–5×10¹⁰ at 1–2 mA) | measured, §1.2 |
| LiLiT ⁸Be γ | 7×10⁸ γ/s/mA (3:4 at 17.6:14.6 MeV) | measured, §1.2 |
| LiLiT mean/max E_n at 0° (1.925 MeV) | 90 / 130 keV | MC, `saraf_beam.py` E |
| Phase I p energy/current limit (≤ 4 kW) | min(2 mA, 4 MeV·mA/E_p) | Paul 2021 |
| Phase I d | ~1 mA, ≤ 5 MeV | Paul 2021 |
| Phase II p/d | 5 mA CW (design) | Mardor 2018 |
| target power demonstrated, Li | 2–4 kW (LiLiT 1), 6 kW model | §1.2 |
| LiLiT-50 design | 50 kW, 2.5 MeV, ~20 mA | search summary S |

## 3. Access

| item | fact | conf. |
|---|---|---|
| owner | Soreq NRC, under the IAEC (government) | V |
| user programme | Described as a future "user facility"; no published call, proposal route or PAC found | (ask) |
| transnational access | none found; not in EURO-LABS / EU TNA lists searched | (ask) |
| past outside users | the LiLiT programme had many international collaborators (ANL, ANU, GUF, HZDR, ILL, PSI, U Seville, CERN, U Bern; Paul 2021) | V |
| site rules | A nuclear research centre of a state atomic-energy commission; foreign-visitor and security rules: not public **(ask)** | E |
| Israel is a CERN Member State (since 2014) | plain fact | V (general knowledge) |
| security situation | LINAC 2024 states events in Israel complicate commissioning; Iranian missile strikes hit Dimona and Arad on 2026-03-21 (AP/PBS); the region is in active conflict | V |
| reported strikes on Soreq itself | an unconfirmed social-media claim was found (Airwars); no reliable report of damage to Soreq or SARAF | (ask) |
| ³He transport and a high-pressure cell at a nuclear site | no public information | (ask) |

## 4. What hosting MX17 needs

- A neutron source that a 40 cm cell can be placed in front of at 0.3–1 m, with free space for four arms (~1.5 m across) and a
  shield. The LiLiT chamber geometry assumes foils at 6–8 mm: the vacuum chamber and duct must allow a flange and a tube to the
  cell. **(ask)** the Phase I target room dimensions.
- A CW machine: no macro-pulse gating (cosmics all day) unless it is run pulsed (Phase II allows pulses).
- Neutron shield: the 2013–17 corridor limit is a warning: a Birmingham-class 10¹³ n/s source needs a real target room. Which room
  Phase II provides: **(ask)**.

## 5. Contacts (public, none contacted)

M. Paul (Hebrew University, LiLiT), M. Friedman (HUJI; n-rich/n-deficient programmes), M. Tessler, I. Mardor (Soreq/TAU, facility
overview), L. Weissman, A. Kreisel, S. Halfon, A. Shor (Soreq accelerator/target), N. Pichoff (CEA, SARAF-LINAC).

## 6. Sources

- Mardor et al., EPJA 54, 91 (2018): https://arxiv.org/abs/1801.06493
- Tessler et al., PLB 751 (2015): https://arxiv.org/abs/1511.04701
- Tessler et al. Ga MACS, PRC (2022): https://arxiv.org/abs/2211.16774
- Ce MACS, 2024: https://arxiv.org/abs/2406.17646
- Halfon et al., RSI 84 (2013) 123507: https://arxiv.org/abs/1311.3325
- M. Paul, LiLiT@SARAF (CERN n_TOF seminar, 2021): https://indico.cern.ch/event/1073008/contributions/4596694/attachments/2350927/4009867/CERN_nTOF_LiLiT@SARAF.pdf
- Paul et al., A 50 kW liquid-lithium target, EPJ WoC 231 (2020) 03004: https://doaj.org/article/7d921877c5734f2e9842e192502a92ad
- Pichoff et al., The SARAF-LINAC project July 2024 status, LINAC 2024 THAA007: https://proceedings.jacow.org/linac2024/pdf/THAA007.pdf
- N. Bazin, CEA cryomodules, LCWS 2025: https://agenda.linearcollider.org/event/10594/contributions/57614/attachments/40559/64542/LCWS2025-NBazin.pdf
- JINST 18 T12003 (injector and MEBT commissioning): https://iopscience.iop.org/article/10.1088/1748-0221/18/12/T12003
- HPTW 2023 (GaIn main source; early commissioning): https://indico2.riken.jp/event/3102/contributions/21933/
- AP via PBS, 2026-03-21: https://www.pbs.org/newshour/world/dozens-injured-in-israel-after-iranian-missile-strikes-target-two-areas-near-main-nuclear-research-center
- Meadows, ⁹Be(d,n) thick-target spectra 2.6–7 MeV: https://www.osti.gov/biblio/5796157 (tables not retrievable here).
