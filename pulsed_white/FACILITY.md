# Pulsed white neutron sources: facility record (GELINA, CSNS Back-n, and the rest of the class)

Started 2026-11-09. Every number has a source; **(ask)** marks what could not be found publicly.
Confidence as in `survey/SOURCES.md`: V verified (document read), S search summary only, E estimate.

## 1. JRC GELINA (Geel, Belgium)

| quantity | value | source | conf. |
|---|---|---|---|
| Machine | Electron linac on a rotating, mercury-cooled depleted-U(Mo) target; neutrons from (γ,xn) and (γ,f) | [JRC lab page](https://joint-research-centre.ec.europa.eu/laboratories-z/jrc-neutron-time-flight-facility_en); Nyman, iTL workshop 2019 (slides) | V |
| Electrons | **100 MeV average** in the typical mode; the machine is also described as 150 MeV | [JRC lab page](https://joint-research-centre.ec.europa.eu/laboratories-z/jrc-neutron-time-flight-facility_en), [EUFRAT call page](https://joint-research-centre.ec.europa.eu/calls-proposals/gelina-neutron-time-flight-facility-high-resolution-neutron-measurements-eufrat_en) | V |
| Current, time structure | **100 µA average, 12 A peak, 10 ns, compressed to ~1 ns (120 A)**; **800 Hz** typical; "typically 50 Hz or 400 (800) Hz" | JRC lab page; Nyman 2019 | V |
| Neutron output | **3.4×10¹³ n/s** average, 4.3×10¹⁰ n per pulse (4π) | JRC lab page; Nyman 2019 | V |
| Spectrum | "from subthermal to about 20 MeV, with a peak at 1–2 MeV"; dedicated flight paths for **fast (200 keV–20 MeV)** or moderated (1 meV–300 keV) | JRC lab page; Nyman 2019 | V (shape only) |
| Flight paths | 12, at 10, 30, 50, 60, 100, 200, 300, 400 m; up to 10–12 experiments at once; 24 h/day, ~100 h/week | JRC lab page; [CERIC](https://www.ceric-eric.eu/lab-instrument/jrc-gelina-neutron-time-of-flight-facility/) | V |
| Spectrum/flux at a station | MCNP5 characterisation of all flight paths exists: Ene et al., NIM A 618 (2010) 54 ([JRC36942](https://publications.jrc.ec.europa.eu/repository/handle/JRC36942)); the full text could not be fetched; a measured direct-flux comparison agrees within 20 % (Flaska et al., MCNP4C3, NIM A 531) | abstract only | S |

**The flux at the cell is therefore an upper bound.** Published as a source strength, not a fast-neutron flux at a named station; the isotropic 3.4×10¹³ n/s at 10 m gives 1.35×10⁸ n/s through a Ø8 cm spot. **(ask)** the direct-flux spectrum on a 10 m path and the actual beam size there. Which of the 12 paths view the target directly or the moderator, and which can be collimated to Ø8 cm, are **(ask)**.

**γ flash:** an electron machine; no public number for the flash per pulse at a station. It is the deciding unknown (FEASIBILITY §5). **(ask; Geant4)**

**Access:** the EUFRAT open-access programme, relevance-driven only. Reference `2025-1-RD-EUFRAT-GELINA` (deadline 14 Feb 2025, [call page](https://joint-research-centre.ec.europa.eu/calls-proposals/gelina-jrc-neutron-time-flight-facility-eufrat-2025-1-rd-eufrat-gelina_en), **V**). A call `2026-1-RD-EUFRAT-GELINA` (28 Jan – 28 Feb 2026) appears in the JRC Work Programme 2025–27 according to one search summary (**S**, the call page itself not read); no 2027 call found. Annual calls in the first weeks of the year are the pattern: **next round probably early 2027 (ask)**.

Facts from the 2025 call: an access unit is a measurement week (~100 h beam, setup included; 24 h × 5 days); 0 €/AU for JRC-operated use (consumables excluded); average 8 AU per project, 50 AU in the call; max 36 months; users may not operate the facility themselves ("not possible"). Eligibility: lead user and institution established in an EU Member State or Euratom-associated country (Ukraine, Switzerland conditional); the work "must be in line with the activities defined in Annex I of Council Regulation (Euratom) 2021/765". **Restriction as a plain fact:** access is tied to Euratom-programme relevance. A BSM-physics search is not an obvious fit; a CEA/IN2P3 lead institution with a nuclear-data angle (³He(n,γ) and IPC cross sections) would be the route. Which institution would lead is **(ask Dylan)**.

Contacts (from the call page and CERIC): feasibility `JRC-OPEN-EUFRAT@ec.europa.eu`; submission `JRC-RI-OPEN-ACCESS@ec.europa.eu`; JRC scientists A. Plompen, C. Paradela Dobarro.

Space and shielding: **(ask)**. Existing setups are ND stations (NRTA, NRCA, GAINS, etc.), and hosting a four-arm 2×2 m apparatus at a 10 m station is not described anywhere.

## 2. CSNS Back-n (Dongguan, China)

| quantity | value | source | conf. |
|---|---|---|---|
| Machine | 1.6 GeV protons, 25 Hz, back-streaming neutrons off the W target (Ta-clad) at 180° | Tang et al., [arXiv:2101.06567](https://arxiv.org/abs/2101.06567) (`survey/refs/arxiv_2101.06567_backn.pdf`) | V |
| Power | 185 kW on target (RCS, 2026, from the survey and JACoW pages); CSNS-II to 500 kW | [IHEP CSNS-II slides](https://indico.ihep.ac.cn/event/27262/contributions/202641/attachments/95425/125693/CSNS-II%20%E5%B7%A5%E7%A8%8B2025%E5%8A%A0%E9%80%9F%E5%99%A8%E8%BF%9B%E5%B1%95-%E4%B8%8A%E4%BC%A0%E7%89%88.pdf) | S |
| Stations | ES#1 ~55 m, ES#2 ~76 m (some slides ~70 m) | Tang 2021; Fan, NOPTREX 2023 | V |
| Flux (per 100 kW, measured and FLUKA) | ES#1 Φ50: **1.8×10⁷ n/cm²/s**, ES#2 Φ60: **6.9×10⁶**; ES#1 Φ20: 1.6×10⁶; ES#2 Φ30: 6.1×10⁵ | Tang 2021 Table 1 (the ES#1 Φ20 ~ value "1.642×10⁶ n/cm²/s" also measured, [EPJ A 60 (2024)](https://epja.epj.org/articles/epja/abs/2024/03/10050_2024_Article_1272/10050_2024_Article_1272.html)) | V |
| Spectrum | 0.5 eV–~200 MeV, peak ~1 MeV, ~45 % above 1 MeV; per-decade measured values in `survey/survey_yield.py` | Tang 2021 | V |
| Time structure | **two bunches 410 ns apart** in each pulse (standard; unfolded); **single-bunch mode exists** (fewer protons); bunch-merge studies for CSNS-II (PRAB 26, 024201, 2023) | Tang 2021; Fan 2023 | V |
| γ flash | "similar level of neutrons, ~10⁶–10⁷/cm²/s"; a 30–100 mm Pb absorber in the upstream line largely suppresses the in-beam γ and "reduces the neutron flux only modestly" | Tang 2021 §2.3 | V |
| Upstream platform | irradiation between window and shutter: ~8×10⁷ n/cm²/s, parasitic, "outside the shutter aperture"; position not given | Tang 2021 | V; L ≈ 30 m is E |

Status 2026: operating, 185 kW, about 50 experiments/year on Back-n. **CSNS-II:** 5 y 9 m construction, SC linac installation July 2027–April 2028 (IHEP slides, S); 500 kW ~2029–2030 (E). No shorter station or close-position plan found. Bunch merging would double the single-bunch intensity.

Access: CSNS user calls through the CSNS User Service System ([IHEP](https://english.ihep.cas.cn/csns)); foreign users existed in 2019 (UK, Canada; [CERN talk](https://indico.cern.ch/event/829348/attachments/1880442/3098090/CSNS_Back-n-Chen.pdf), S). Current terms for a foreign experiment with a 30 bar ³He cell: **(ask)**. Plain fact: the site is in China; sending the MX17 apparatus and a pressurised ³He target there is a logistical and export-control question for each home institution.

## 3. The rest of the class

| key | status and source | numbers used |
|---|---|---|
| `nelbe` | HZDR nELBE, 30 MeV SRF, 100–400 kHz, 5–11 m, 2.5×10⁴ n/cm²/s at target, 7 cm² (hzdr.de page, per catalogue) | as catalogue (~10⁵ n/s total) |
| `rpi` | RPI LINAC, 60 MeV, ≤1×10¹³ n/s (arXiv:1801.03424, per catalogue) | scaled to GELINA at 10 m, 400 Hz (E) |
| `kurns_linac` | KURNS-LINAC 46 MeV, weaker source than GELINA (lit.) | not computed: source ≤ RPI, same class |
| `jparc_annri` | J-PARC ANNRI, 25 Hz moderated (keV-optimised), 21.5 m | not computed: a moderated beam has little flux in 0.2–2.75 MeV; 25 Hz gives the Back-n duty problem |
| `csns2` | as Back-n at 500 kW (above) | ×2.7 of 185 kW |

## 4. Machine-independent inputs

- **The Micromegas flash recovery (n_TOF, measured):** the chamber signal returns below threshold 0.87 µs after the flash peak (`nTof_x17/ntof_processing/mm_flash`), but the **DREAM front end rails** for 0.5 ms to >25 ms depending on the resistive HV (`nTof_x17_DAQ/docs/flash_recovery_run57_HV_map_2026-07-20.md`), with dead time ∝ Q^1.2 (`nTof_x17/ntof_july_analysis/flash_charge/`).
- **n_TOF EAR2:** ~1.6×10⁷ n through Ø5 cm above 0.1 MeV per pulse per the survey, neutrons per pulse only as a proxy for the flash size; the flash ratio itself is **(ask; Geant4)**.
