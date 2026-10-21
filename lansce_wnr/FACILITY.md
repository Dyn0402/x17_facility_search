# LANSCE WNR Target 4 — the facility record

Started 2026-10-21. Every number has its source; **(ask)** marks what could not be found publicly.
Confidence codes as in `survey/SOURCES.md`: V verified (document read), S search summary, E estimate.

## 1. Where and what

- **Site:** Weapons Neutron Research facility (WNR, now also styled "Neutron and Nuclear Science"),
  Los Alamos Neutron Science Center (LANSCE), Los Alamos National Laboratory, New Mexico, USA
  (35.874 N, 106.324 W). WNR has two stations: **Target 4**, the unmoderated "white" neutron source with
  six flight paths, and Target 2 (proton irradiations, the lead slowing-down spectrometer).
  <https://www.lanl.gov/science-engineering/science-facilities/lansce/facilities/wnr>. **V** (page read).
- **Driver:** the LANSCE 800 MeV H⁻ linac. Target 4 is a **bare tungsten cylinder, 7.5 cm long, 3 cm in
  diameter, in a 4 mm water jacket**, giving neutrons from ~100 keV to ~800 MeV. Nowicki, Wender & Mocko,
  Physics Procedia 90 (2017) 374, LA-UR-17-20620 (`refs/Nowicki2017_LANSCE.pdf`). **V**.
- **Programme:** nuclear data (fission cross sections and spectra: Chi-Nu, the NIFFTE fission TPC,
  fission chambers), γ-ray spectroscopy after neutron reactions, and accelerated neutron testing of
  electronics (ICE House and ICE-II, the 30° paths). Proposals through the annual LANSCE user calls.

## 2. Beam numbers

| quantity | value | source | conf. |
|---|---|---|---|
| proton energy | 800 MeV | Nowicki 2017 | V |
| macropulses | **625 µs, 40 per second** for Target 4 (the linac can do 120) → duty **2.5 %** | LANL time-of-flight page | V |
| micropulses | **1.8 µs apart (typical); 3.6 µs and up to 7.2 µs on request**; width < 100 ps at the linac exit; **7×10⁸ protons each** | LANL time-of-flight page; GEANIE description; ⁵⁹Ni(n,p) paper (3.6 µs data taken to measure wrap-around) | V/S |
| micropulse rate | 40 × 625 µs / 1.8 µs = **13 889 per second** | LANL time-of-flight page | V |
| current | **~1.5 µA** (7×10⁸ × 13 889 = 9.7×10¹² p/s = 1.56 µA). Older documents say ~4 µA and ~35 000 pulses/s (100 Hz operation). The LANL WNR page: an RF upgrade "will increase the beam current to Target 4 by a factor of 2.5 to provide beam currents up to 5 µA" | LANL WNR page; Nowicki 2017 ("~4 µA"); arXiv:1511.07772 | V/S |
| yield vs angle | Y(E) in n/proton/MeV/sr at 15, 30, 60 and 90° (0.1–800 MeV): the more forward, the harder | Nowicki 2017 Fig. 2 (digitised in `wnr_beam.py`) | V (digitised by eye, ±10 %) |
| ICE House (4FP30L) | 1.5×10⁶ n/cm²/s above 1.5 MeV; beam Ø 2.5–8 cm adjustable | Nowicki 2017 §2.1 | V |
| ICE-II (4FP30R) | 4.7×10⁶ n/cm²/s above 1.5 MeV ("shorter flight path"); beam Ø 2.5–6.4 cm | Nowicki 2017 §2.1 | V |
| wrap-around energy | 1.8 µs: 161 keV at 10 m, 645 keV at 20 m; 3.6 µs: 40 keV at 10 m, 161 keV at 20 m | LANL time-of-flight page | V |
| γ flash | every micropulse; intensity at 90° **(ask)** | — | (ask) |

**Cross-check of the digitised yield.** At 30°, 20 m and 1.56 µA, `wnr_beam.py` gives 1.23×10⁶ n/cm²/s
above 1.5 MeV against the quoted 1.5×10⁶ for ICE House; ICE-II's 4.7×10⁶ then puts it at ~10 m. So Fig. 2
is per proton at today's current, and the absolute scale holds to ~20 %.

**What the angle does** (`out/wnr_spectra_summary.csv`, fraction of neutrons above 0.1 MeV):

| angle | 0.2–2.75 MeV | > 8.5 MeV | > 45 MeV | n/sr/proton > 0.1 MeV |
|---|---|---|---|---|
| 15° | 36 % | 42 % | 29 % | 0.67 |
| 30° | 43 % | 33 % | 19 % | 0.73 |
| 60° | 51 % | 23 % | 10 % | 0.77 |
| **90°** | **55 %** | **16 %** | **3.8 %** | 0.74 |

The soft (evaporation) part is nearly isotropic; the hard (cascade) part is forward. 90° gives the most
neutrons in the ATOMKI window and ×8 fewer above 45 MeV than 15°.

## 3. The flight paths

From the LANL WNR page (V) unless marked.

| path | what | length | beam | users |
|---|---|---|---|---|
| 4FP15L | CoGNAC | 22 m and 90 m (2 m deep pit under the 22 m floor) | rectangular shutter, collimator inserts | Chi-Nu, detector development |
| 4FP15R | LENZ | (ask) | up to 5 × 5 cm | charged-particle reactions; hardest spectrum |
| 4FP30L | ICE House (ICE-I) | ~20 m (from the flux, E) | Ø 2.5–8 cm | electronics testing (industry, full cost) |
| 4FP30R | ICE-II | ~10–12 m (from the flux, E) | Ø 2.5–6.4 cm | electronics testing |
| 4FP60R | radiography / CT | (ask) | 30 × 20 cm down to Ø 2.5 cm | defence programmes |
| **4FP90L** | **fission** | **~7–15 m** | (ask) | fission chambers, the NIFFTE fission TPC; **softest spectrum** |

- **4FP90L is the natural home**: softest spectrum, shortest flight path, used for TPC-sized detectors.
  The 2026 nuclear-science call warned that **90L has very limited beam time** and asked proposers to
  contact the instrument scientist first (search summary, S). Space around the beam for four 0.8 m arms
  at 7–10 m **(ask)**.
- The ICE paths are booked by industry at full cost; 15L hosts Chi-Nu.

## 4. Access

- **LANSCE user programme.** Annual calls; the 2026 nuclear-science call (WNR and Lujan) closed
  20 February 2026 for the run cycle of 18 June – 21 December 2026. Industry can apply at any time.
  Submissions through LEMS. <https://lansce.lanl.gov/users/become-a-user/proposals.php>. **S**.
- **Contacts (public):** LANSCE User Office, 505-667-6797, lansce-user-office@lanl.gov; P-3 Nuclear and
  Particle Physics group leader C. Lee (clee@lanl.gov); WNR physicists S. A. Wender and M. Mocko (authors
  of the 2017 paper). The 90L instrument scientist **(ask)**.
- A LANL site badge for foreign nationals takes time; whether an external collaboration can bring its own
  DAQ and gas system (³He at 30 bar) **(ask)**.

## 5. What it would take to host MX17

- **The 90L flight path at 7–10 m**, a Ø8 cm beam at the cell, a beam dump behind (the TPC users have one,
  (ask)), and room for the arms (~2 × 2 m).
- **1.8 µs micropulses** (the default). Below 10 m they leave the whole window clean: the next γ flash
  arrives after the 0.2 MeV neutrons. 3.6 µs costs half the protons and is not needed.
- **A trigger gate on time of flight** (the micropulse timing signal from LANSCE): accept two-arm
  triggers only 0.4–1.6 µs after each micropulse (0.2–2.75 MeV at 8 m). It keeps DREAM alive.
- **The γ flash** at every micropulse lands in the Micromegas drift (1 µs memory) just before the window
  opens. Its size at 90° and whether a Pb filter is needed **(ask; simulate)**.

## 6. Sources

- S. F. Nowicki, S. A. Wender, M. Mocko, *The Los Alamos Neutron Science Center spallation neutron
  sources*, Physics Procedia 90 (2017) 374 (CAARI 2016), LA-UR-17-20620,
  <https://www.osti.gov/pages/biblio/1406207>. `refs/Nowicki2017_LANSCE.pdf`; Fig. 2 (yield vs angle) and
  Fig. 3 (ICE spectra) as `refs/Nowicki2017_fig2_yield.png`, `refs/Nowicki2017_fig3_ice.png`.
- LANL, *Proton beam time-of-flight techniques*,
  <https://www.lanl.gov/science-engineering/science-facilities/lansce/facilities/time-of-flight>
  (macropulse, micropulse, wrap-around table). Page read 2026-10-21.
- LANL, *Weapons Neutron Research facility*,
  <https://www.lanl.gov/science-engineering/science-facilities/lansce/facilities/wnr> (flight paths,
  current, upgrade, contacts). Page read 2026-10-21. (The old lansce.lanl.gov flight-path pages redirect here
  or return 404.)
- P. W. Lisowski, K. F. Schoenberg, NIM A 562 (2006) 910 (the LANSCE overview; not read).
- 3.6 µs operation: the ⁵⁹Ni(n,p) LANSCE paper, <https://www.osti.gov/pages/servlets/purl/1866958>; the
  GEANIE description (1.8–7.2 µs useful range). Search summaries, S.
- 2026 LANSCE calls: <https://lansce.lanl.gov/users/become-a-user/proposals.php> (search summary; the PDFs
  returned 404 on 2026-10-21).
