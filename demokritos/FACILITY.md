# NCSR "Demokritos" (Athens): the facility, as far as an X17 run needs to know it

Research record, compiled 2026-10-19 from public papers and proceedings. The sources are at the bottom, and the
text extractions are in `refs/`. Anything marked **(ask)** could not be found publicly and has to come from the
lab.

---

## 1. The laboratory

| | |
|---|---|
| What | **Tandem Accelerator Laboratory (TAL)**, Institute of Nuclear and Particle Physics (INPP), National Centre for Scientific Research "Demokritos" (NCSRD). Greece's only nuclear-physics accelerator lab. |
| Where | Patriarchou Grigoriou & Neapoleos, 153 10 Aghia Paraskevi, Athens. |
| Building | Two storeys, ≈ 5520 m², of which ≈ 900 m² is the accelerator hall and two target rooms. The walls are borated concrete up to 1.2 m thick, built for neutron production. |
| Rooms | Tandem hall 35 × 9 m. Two target rooms, **"Green" and "Red", each 17.5 × 17 m, 6.8 m high**. That is plenty of floor for the ~2 × 2 m MX17 footprint. |
| People | **A. Lagoyannis** (lab head, lagoya@inp.demokritos.gr), **M. Axiotis**, **S. Harissopulos** (sharisop@inp.demokritos.gr, earlier director), M. Andrianis, A. Laoutaris. Users from **NTUA** (R. Vlastou, M. Kokkoris, M. Diakaki: the neutron-activation programme, n_TOF members). |
| Machines | the **5.5 MV HVEC T11/25 tandem** (1973), the **PAPAP 250 kV** single-stage p/d accelerator (from CSNSM Orsay), and, being installed, a donated **17 MeV MC-17 cyclotron** (p, 8.5 MeV d) and a **2.5 MV Tandetron AMS** machine. |

**For us:** the tandem is the machine. PAPAP is a possible high-current option (§4).

## 2. The 5.5 MV tandem

| | |
|---|---|
| Type | HVEC T11/25 Van de Graaff tandem, one of only two built (the other is at Ohio University). First beam March 1973. |
| Upgrade (CALIBRA, ≈ €3.4 M, finished 9/2022) | Belt replaced by **three Pelletron chains**. New terminal stabilisation: capacitive pick-off, generating voltmeter, corona probe and analysing slits. New terminal foil (80 foils) and N₂ gas strippers. Turbo pumps, < 10⁻⁷ mbar. Full computer control (AccelNet), with remote operation. |
| Ion sources | **TORVIS** (H⁻, D⁻, He⁻) and **SNICS** sputter source, both at 55 kV. TORVIS tests gave **100 µA of H⁻ and D⁻** with low divergence. SNICS gave 40 µA of C and O. |
| Proton energies | Quoted as "stable, high-current proton beams between **0.8 and 10 MeV**" (Radiation 6, 7, 2026). The lab measured ⁷Li(p,p′γ) from **1010 keV** up. E_p = 0.9 MeV needs a terminal at ≈ 0.42 MV. **(ask)** 0.51 and 0.61 MeV, ATOMKI's other two points, are below the quoted minimum. |
| Current on target | The neutron programme runs at **700 nA – 1 µA** through 5–6 mm collimators (Vlastou et al., before the upgrade). "The beam current is expected to be considerably increased" after it. **(ask)** the current at 0.9 MeV, and whether it is still ~1 µA. |
| Energy spread | Not quoted **(ask)**. With slit stabilisation it is ~1 keV, which does not matter here: the ⁴He states are 0.5–0.8 MeV wide, and a thick target integrates over hundreds of keV anyway. |
| Beam lines | Switching magnet with ports at 0°, +15°, −25°, +32.5°, ±45°, ±60° (Table 1 of the 2021 paper). |
| | **R60**: GASPAR BGO ball. **R45**: microprobe. **R32.5**: RBS/PIXE, ToF-ERDA. **R15**: NeoPtolemos 4π NaI. |
| | **L25**: large scattering chamber and HPGe array. **L45**: ZAPS atomic physics. **L60**: multipurpose irradiation and **neutron production**: the D₂ gas cell and the Ti-T targets. The Avgitas 2026 neutron run was in the Red room on a **45° line**. |
| | Which line could host a 2 × 2 m apparatus with free space around the target **(ask)**. L60 already has the neutron-production licence and shielding. |

## 3. The neutron facility, and why it is not the X17 route here

| reaction | E_n | target |
|---|---|---|
| ⁷Li(p,n)⁷Be | ~120–650 keV (tens of keV – 4 MeV, 2026) | ⁷LiF on Al |
| ³H(p,n)³He | 2.0–5.3 MeV | **Ti-T: 2.1 mg/cm² on 1 mm Cu**, 373 GBq (10 Ci) |
| ²H(d,n)³He | 4–11.5 MeV | D₂ gas cell, ~1 atm, 5 µm Mo window, Pt stop |
| ³H(d,n)⁴He | 15–21 MeV | the same Ti-T target |

- **Flux: 10⁵–10⁶ n/cm²/s at the sample.** There is no time-of-flight; the spectra are characterised by foil activation
  and MCNP.
- Run on a ³He cell this gives **at best ~0.5 X17 per day into 4π** (500 bar × 1 cm capsule, 10⁶ n/cm²/s at
  0.35 MeV, `out/neutron_option.csv`). The ILL beam is ~10¹⁰ absorbed n/s, about 10⁵× more. **The neutron beams are
  ruled out.**
- **What the neutron programme does give us:**
  - **Ti-T targets.** The lab owns tritiated targets, handles them, and holds the licence to put protons and deuterons
    on them in the Tandem hall.
  - **³H(p,n) running.** It means p + t is a routine reaction there.

  This is the main reason Demokritos is a natural site for the ⁴He measurement (see `PHYSICS.md`).

## 4. PAPAP, the 250 kV machine

- A multicusp source with **hundreds of µA** of p and d, and up to 0.5 mA quoted.
- The lab plans to use it as a 14 MeV T(d,n) neutron generator with a 92.5 GBq Ti-T target, giving 10¹¹ n/s. That
  needs new shielding and probably a move. Radiation safety and tritium licensing are "under investigation".
- **For us:** ³H(p,γ) at E_p = 250 keV with ~100 µA. E\* = 20.0 MeV: inside the 0.5 MeV-wide 0⁺ resonance but below its
  centroid, and 200 keV below ATOMKI's lowest point (no X17 measurement exists there). It is ~5× faster than the tandem at 1 µA (`ESTIMATES.md` §4), but it puts
  25 W into a Ti-T target, which needs a thick cooled backing. **(ask)** whether PAPAP can take a Ti-T target at all,
  and on what timescale.

## 5. Getting beam time

- **TAL is open access.** "Research proposals can be submitted by external users at any time and beamtime is granted
  after evaluation by a Program Advisory Committee (PAC) that meets **twice a year**. The PAC members are
  knowledgeable scientists from abroad." Before the pandemic, more than 1000 h a year went to external users, and
  CALIBRA aims at more than 3000 h.
- **(ask)**:
  - the PAC dates and the template;
  - whether EU transnational-access money (EURO-LABS successor, ChETEC-INFRA, …) covers Demokritos;
  - the tritium-target rules for an external experiment: who owns the target, who mounts it, and contamination
    monitoring of our chamber.
- **Links into the lab:**
  - The NTUA group (Vlastou, Kokkoris, Diakaki) and Demokritos (Lagoyannis, Axiotis) are **n_TOF collaborators**.
  - Kokkoris is also an ion-beam-analysis user of the tandem.
  - That is the natural first contact.
- **Running pattern (ask):**
  - continuous multi-day running at ~0.9 MeV;
  - night and weekend operation, and whether it needs staff;
  - beam-time units.

  The neutron programme irradiates for 8+ hours at a time.

## 6. Open questions for the lab (ask)

1. Proton current at 0.9–1.0 MeV after the upgrade (the neutron programme quotes 0.7–1 µA). Is 0.5–0.6 MeV possible?
2. The Ti-T targets:
   - the size of the existing one;
   - whether a new one can be made on a **thin backing** (Cu 50–100 µm, or Mo/Ti foil) and loaded to T/Ti ≈ 1.5;
   - its tritium activity and the target-handling procedure.

   The supplier could be the lab itself, SODERN, or another.
3. Target cooling: is there water or LN₂ cooling at the target position? ATOMKI cooled to LN₂ temperature.
4. Which beamline and room, the free floor around the target, and the floor loading.

   MX17 is ~2 × 2 m around the target with ~1 t of plastics and liquid scintillator.
5. The PAC calendar, beam-time units, and running beyond working hours.
6. Contamination: a ¹¹B-free target and chamber (¹¹B(p,γ)¹²C puts 16–17 MeV γ in the window). Other contaminants:
   - Deuterium in the Ti-T (D(p,γ)³He at 5.5 MeV is harmless).
   - Carbon build-up (¹³C(p,γ) at 8 MeV is harmless).

## Sources

- S. Harissopulos *et al.*, "The Tandem Accelerator Laboratory of NCSR Demokritos: current status and perspectives",
  EPJ Plus 136, 617 (2021) — `refs/Harissopulos2021_EPJP_TandemLab_status.txt`
- A. Lagoyannis *et al.*, "Recent upgrades at the Tandem Laboratory of NCSR Demokritos", HNPS Adv. Nucl. Phys. 29,
  33 (2023) — `refs/Lagoyannis2023_HNPS_recent_upgrades.txt`
- R. Vlastou *et al.*, "The neutron facility at NCSR Demokritos and neutron activation research activities of NTUA",
  IAEA conference paper / EPJ Tech. Instrum. (2023) — `refs/Vlastou_IAEA_neutron_facility_Demokritos.txt`
- L. Amanatidis *et al.*, 18 MeV neutron flux after the upgrade, HNPS 30, 168 (2024) — `refs/Amanatidis2024_HNPS_18MeV_flux.txt`
- T. Avgitas *et al.*, N₂ spherical proportional counter with monoenergetic neutrons at the Demokritos tandem,
  arXiv:2609.07541 (Sept 2026) — `refs/Avgitas2026_arXiv2609.07541_N2_SPC_Demokritos.txt` (shows the tandem
  delivering ⁷Li(p,n) beams in 2026, Red room, 45° line)
- "Development and Evaluation of a Proton Irradiation Setup … 0–5.5 MeV", Radiation 6, 7 (2026), doi:10.3390/radiation6010007
  (search snippet only: "stable, high-current proton beams in the energy range between 0.8 and 10 MeV")
