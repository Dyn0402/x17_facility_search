# Cyclotron ⁹Be(p,n) sources — the facility record

Started 2026-10-21. Survey key `bepn_cyc` (`survey/SURVEY.md` §6.2, MARGINAL: "the yield and spectrum are
guesses; is there an unmoderated port?"). Every number has its source; **(ask)** marks what could not be
found publicly. Confidence codes as in `survey/SOURCES.md`: V verified (document read), S search summary,
E estimate.

## 1. Which site

A 30 MeV / 1 mA BNCT cyclotron (Sumitomo HM-30) is the strongest p+Be source, but every one built so far
has its Be target buried in a moderator for epithermal BNCT beams. The most concrete site with a **bare,
forward-open Be converter, a research programme in fast-neutron physics and an open-access policy** is the
**Nuclear Physics Institute of the Czech Academy of Sciences (NPI CAS), Řež near Prague**. It is the
baseline here. The KURNS HM-30 is carried as the high-intensity variant, and U-120M as the
"collimated beam today" variant.

| site | machine | p energy, current | Be target | port | status | conf. |
|---|---|---|---|---|---|---|
| **NPI Řež, TR-24** | ACSI TR-24 (H⁻, stripping extraction) | **18–24 MeV, 300 µA** | high-power static Be disk, 4 mm × Ø40 mm, ≤ 7.2 kW, submerged-jet water cooling; open in the forward direction | none (samples at the target); the vault (ask) | cyclotron since Oct 2015; the high-power converter "not operational yet" (Apr 2019), prototype tested at 24 MeV (2020), a p(24)+Be field measured with foils (2018 poster) | V |
| NPI Řež, U-120M | isochronous cyclotron, K = 40 | H⁻/p extraction **6–37 MeV, 40–30 µA**; p external 6–25 MeV, 5 µA | thick Be, 8 mm (stops 35 MeV p) | **collimated beam, 15 m flight path to a dump, movable shielding blocks, Ø3–25 cm**, beam into the adjacent hall | operating, ~3000 h beam/yr | V |
| KURNS (Kyoto Univ.), Kumatori | Sumitomo HM-30 (C-BENS) | **30 MeV, 1 mA** | Be, water-cooled, 30 kW | epithermal only (Pb, Fe, Al, CaF₂ moderator/filter); a fast port **(ask)** | since 2009; clinical trials from 2012; KURNS plans fundamental research on it after KUR shut down (May 2026) | S |
| Southern Tohoku BNCT Research Center; Kansai BNCT Medical Center (Osaka) | Sumitomo HM-30 / NeuCure | 30 MeV, 1 mA | Be + moderator | clinical | clinical, no research port | S |
| Atomki Debrecen | MGC-20E | p(16–18 MeV)+Be, µA class | 3 mm Be, He-cooled window | irradiation position at 13 cm | operating | V |
| TENMAK-NUKEN Ankara | IBA Cyclone-30 class | 30 MeV, 150 µA (thesis) | Be target station | (ask) | METU thesis | S |

## 2. NPI Řež: what is known

- **Institute:** Nuclear Physics Institute of the CAS, Husinec-Řež 130, 250 68 Řež, Czech Republic
  (≈ 50.18 N, 14.36 E). Department of Accelerators (cyclotrons: J. Štursa) and the Laboratory of Fast
  Neutron Generators (M. Ansorge, P. Bém, D. Hladík, **M. Majerle**, J. Novák, E. Šimečková,
  **M. Štefánik**). Its programme: fast-neutron cross-section validation for IFMIF-DONES, ITER, DEMO;
  activation, delayed neutrons, (n,xγ) with HPGe on collimated beams, a light-ion chamber "inspired by
  MEDLEY" for 18–35 MeV collimated beams. Ansorge, Barrande workshop 2019
  (<https://barrandewks2019.sciencesconf.org/data/Barrande_WKS_M_Ansorge.pdf>). **V**.
- **TR-24:** Advanced Cyclotron Systems Inc. (Canada), H⁻ multi-cusp source, 85 MHz, **18–24 MeV
  (stripping-foil radius), 300 µA**, two simultaneous beams; output 1 on the vacuum chamber (3 target
  positions), output 2 through a beamline and switching magnet (3 more). Commissioned October 2015.
  NPI TR-24 page (<https://www.ujf.cas.cz/en/departments/department-of-accelerators/TR-24/>); Štursa,
  NPB EPS workshop 2017 (<https://www.ujf.cas.cz/export/sites/ujf/.content/files/novinky/stursa-cyclotrons-prezentace-2017.pdf>, read). **V**.
- **High-power Be converter (CANAM project):** "static target (beryllium disk, thickness 4 mm, φ 40 mm)
  … open at forward direction … up to 7.2 kW … total flux densities ~3×10¹² n/cm²/s along the axis of
  irradiation zone for the beam spot of φ 1.6 cm" (Štursa 2017). "Intensity of 5×10¹² n/s/sr in forward
  direction … neutron-flux up to 2×10¹² n/cm²/s nearby the target output" with a 20 mm source-to-sample
  distance (UCANS-8, EPJ WoC 231 (2020) 03005, abstract). The CANAM page: "being developed … 10¹²
  n/cm²/s". Ansorge 2019: "Not operational yet". **Present status (ask).** **V/S**.
- **U-120M:** p internal 2–37 MeV > 200 µA; **H⁻/p external 6–37 MeV, 40–30 µA**; neutron generators
  Li, Be, D₂O. Thick-Be (8 mm) station: continuous spectrum to 35 MeV, ~10¹¹ n/cm²/s maximum (7.25×10¹⁰
  at 15 mm, 2×10⁹ at 156 mm; RPC 104 (2014)). Collimated-beam option: "flight path (15 m) to beam dump …
  transportable shielding (blocks), collimated beam size from diam. 3 cm to 25 cm … extraction of the
  accelerated beams into the adjacent experimental hall – low electromagnetic noise". Beam time ~3000 h/yr.
  Štursa 2017; Ansorge 2019. **V**. Spectrum measured by TOF at 3–7.5 m: Majerle et al., NIM A 1053 (2023)
  (abstract). **S**.
- **Access:** NPI's accelerators belong to **CANAM** (Center of Accelerators and Nuclear Analytical
  Methods), a Czech large research infrastructure with an open-access call
  (<https://www.vyzkumne-infrastruktury.cz/en/?p=1280>); EU transnational access to NPI's neutron
  sources has run through **RADNEXT** (CAEN electronics test at NPI, radnext.eu). Beam-time terms,
  costs, and whether a multi-week nuclear-physics run is possible **(ask)**. **S**.
- **Rooms:** the TR-24 vault was built 2012–2014 with MCNPX-designed shielding; its size, a wall port and
  whether a ~2 × 2 m apparatus can stand 2 m downstream of the converter behind a wall **(ask)**. U-120M's
  adjacent hall exists (dimensions **(ask)**).

## 3. Beam numbers (this study's model)

`bepn_beam.py`: thick-target slowing-down over **ENDF/B-VIII.0 p + ⁹Be (LANL LA150, Young & Arthur)**,
the GNDS file Geant4 ships (`refs/p-004_Be_009.endf.gnds.xml`): MT 50–55 ⁹Be(p,n)⁹B levels with CM
Legendre distributions, MT 5 continuum with Kalbach-Mann, Bethe stopping in Be. A bare target (no backing,
cooling water or room).

| check | model | reference | ratio |
|---|---|---|---|
| 16 MeV, 0°, E_n > 0.4 MeV | 1.44×10⁻³ n/sr/p | 9.07×10¹⁵ n/sr/C = 1.45×10⁻³ (Fenyvesi, arXiv:1504.07399, from Brede et al. NIM A 274 (1989) 332 TOF data) | **0.99** |
| 30 MeV, 4π | 0.0300 n/p | 1.9×10¹⁴ n/s at 1 mA (Sumitomo/KURRI, Cyclotrons 2010 FRM2CCO04) | **0.99** |
| 24 MeV, "forward" | 3.98×10⁻³ n/sr/p at θ < 8° | 5×10¹² n/s/sr at 0.3 mA = 2.67×10⁻³ (NPI design, UCANS-8) | 1.49 (NPI's figure is likely a cone average; at 30–40° the model gives 2.9×10⁻³) |

| at 2 m, Ø8 cm (50 cm²) | n/s total | n/s/sr at θ | n/s through the cell | < 2.75 MeV | > 10 MeV | > 20 MeV | mean E_n | max E_n |
|---|---|---|---|---|---|---|---|---|
| NPI TR-24, 18 MeV, 0.3 mA, 0° | 2.3×10¹³ | 3.8×10¹² | **4.8×10⁹** | 43 % | 14 % | 0 | 4.9 MeV | 16.3 |
| NPI TR-24, 24 MeV, 0.3 mA, 0° | 3.9×10¹³ | 7.4×10¹² | 9.3×10⁹ | 36 % | 28 % | 3 % | 7.0 MeV | 22.3 |
| NPI TR-24, 24 MeV, 130° | | 1.8×10¹² | 2.3×10⁹ | 40 % | 6 % | 0 | 4.2 MeV | |
| KURNS HM-30, 30 MeV, 1 mA, 0° | 1.9×10¹⁴ | 4.0×10¹³ | 5.0×10¹⁰ | 31 % | 40 % | 15 % | 9.5 MeV | 28.4 |
| KURNS HM-30, 130° | | 8.2×10¹² | 1.0×10¹⁰ | 36 % | 12 % | 0 | 5.0 MeV | |
| NPI U-120M, 18 MeV, 35 µA, 0°, 3 m | 2.6×10¹² | 4.5×10¹¹ | 5.6×10⁸ | 43 % | 14 % | 0 | 4.9 MeV | 16.3 |

- **The spectrum is hard at every angle.** Only 31–48 % of the neutrons are below 2.75 MeV (E* ≤ 22.1 MeV).
  The low-energy part (evaporation, ⁹Be break-up) is nearly isotropic; the forward peak is the hard
  (p,n) continuum and the ⁹B ground-state line. Going sideways removes the > 10 MeV tail but not the
  2.75–10 MeV bulk. Lowering E_p does the same, at fewer neutrons.
- **Target γ** (MT 5 photons: discrete lines ≤ ~7 MeV, e.g. 3.56 MeV ⁶Li*): 3.1×10⁻⁴ γ/p at 24 MeV,
  isotropic; ~5×10⁷ γ/s through the spot at 2 m, ×100 fewer than neutrons. ⁹Be(p,γ)¹⁰B (E_γ up to
  ~28 MeV) is not in the evaluation: estimate ≲ 10⁻⁸ γ/p, ≲ 10³ γ/s through the spot. **E**.
- The survey's guess (`survey_fast.py` `bepn`): 10¹³ n/sr/s at 0° for 30 MeV, 1 mA, and 30/55/15 % in
  0.1–1 / 1–10 / 10–28 MeV. The model gives **4.0×10¹³** at 0° and 5/55/40 %: ×4 the neutrons and harder.

## 4. What it would take to host MX17

- **A port through a wall.** A 2–4×10¹³ n/s source with a fast spectrum: one arm 2 m away sees
  ~3–5×10¹¹ n/s, and 1–20 MeV neutrons make trigger legs. ~1–2 m of concrete-equivalent between the
  converter and the arms (`FEASIBILITY.md` §5, estimate). U-120M has exactly this (collimator in movable
  shielding doors, beam into the next hall) but at ~1/10 the current; TR-24 would need one built **(ask)**.
- **Proton energy:** the lowest the TR-24 gives (18 MeV) is best; ⁷Li(p,n) at 2–3 MeV (Birmingham) is
  softer still.
- **Space:** the arms ~2 × 2 m, the cell 2 m from the Be, vacuum flight tube, dump behind **(ask)**.
- **Beam time:** 2–3 weeks of 0.2–0.3 mA (`FEASIBILITY.md` §0) through CANAM / EU transnational access.

## 5. Contacts (public)

- Mitja Majerle, Milan Štefánik (Laboratory of Fast Neutron Generators, NPI CAS); Jan Štursa (cyclotrons,
  Department of Accelerators). Emails from the NPI staff pages **(ask)**.
- KURNS: H. Tanaka (C-BENS, accelerator BNCT; BIPM webinar Jan 2025).

## 6. Sources

- ENDF/B-VIII.0 incident-proton ⁹Be (MAT 425, LANL LA150, P. G. Young, E. D. Arthur, LA-11753-MS 1990),
  GNDS 2.0 from `/cvmfs/geant4.cern.ch/share/data/LEND_GNDS2.0_ENDF.BVIII.0/protons/`.
  `refs/p-004_Be_009.endf.gnds.xml`.
- A. Fenyvesi, *Estimations and integral measurements for the spectral yield of neutrons from thick
  beryllium target bombarded with 16 MeV protons*, arXiv:1504.07399 (read). `refs/Fenyvesi2015_pBe16.pdf`.
- H. J. Brede et al., NIM A 274 (1989) 332 (thick-Be TOF yields 17–22 MeV; cited via Fenyvesi).
- J. Štursa, *Status report: isochronous cyclotron U-120M, cyclotron TR-24*, NPB EPS workshop, Řež,
  13 Jun 2017 (read; not kept, 2 MB).
- M. Ansorge et al., *Laboratory of Fast Neutron Generators at NPI Řež*, Barrande workshop 2019 (read; not kept, 2 MB).
- *High-power TR-24 cyclotron-based p-n converter cooled by submerged orifice jet*, EPJ WoC 231 (2020)
  03005 (UCANS-8; abstract via search, the PDF is behind a bot check).
- M. Štefánik et al., p(24)+Be multi-foil field study, SOFT 2018 poster (ENEA agenda, abstract);
  *Neutron spectrum determination of p+Be reaction for 30 MeV protons*, ND2019, EPJ WoC (2020)
  (8.6×10¹⁰ n/cm²/s near the target).
- M. Majerle et al., *Measurements of the neutron spectra from the p+Be neutron generator of the NPI CAS*,
  NIM A 1053 (2023) (abstract).
- Sumitomo/KURRI, Cyclotrons 2010, FRM2CCO04 (1.9×10¹⁴ n/s at 30 MeV, 1 mA, 30 kW Be target).
- KURNS, AESJ 2026 spring meeting 3F08 (C-BENS for fundamental research after KUR's shutdown, May 2026).
- METU thesis <https://open.metu.edu.tr/handle/11511/115507> (30 MeV, 150 µA).
