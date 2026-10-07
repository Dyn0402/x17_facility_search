# LNL (Legnaro), as far as an X17 run needs to know it

Research record, compiled 2026-10-07 from public LNL documents, papers and talks.
Sources are at the bottom, and the text extractions are in `refs/`. Anything
marked **(ask)** could not be found publicly and has to come from LNL.

---

## The laboratory

| | |
|---|---|
| What | INFN Laboratori Nazionali di Legnaro, one of INFN's four national labs. Founded 1968. ~250 staff. Nuclear physics, nuclear astrophysics and applied physics with ion beams. |
| Where | Viale dell'Università 2, 35020 Legnaro (PD), Italy, ~10 km from Padova. Tel. +39 049 8068311, prot@lnl.infn.it |
| Director | Prof. Faïçal Azaiez |
| Accelerators | Two small single-ended Van de Graaffs, **CN** (bldg. 008) and **AN2000** (bldg. 013), the "blue zone" for users. Plus the Tandem–ALPI–PIAVE heavy-ion complex (bldg. 022 and Hall 3) and the SPES 70 MeV proton cyclotron (commissioning). |
| Who runs CN/AN2000 | Scientific coordinator **Anna Selva** (anna.selva@lnl.infn.it). Accelerator Division: **pacbeams@lnl.infn.it** |

**For us:** only CN and AN2000 matter. The physics needs 0.44–1.2 MeV protons on
lithium. The Tandem's minimum energy is far too high, and SPES is 70 MeV.

## The two machines

Numbers from LNL's own beam sheet (`refs/LNL_Beams_AN2000_CN.txt`, linked from the
2025 PAC call) unless marked.

### AN2000: the natural home (and the one LNL already uses for this)

| | |
|---|---|
| Type | High Voltage Engineering single-stage belt Van de Graaff, operating since **1971**. 2.5 MV design, **2.0 MV max** today. |
| Voltage range | **0.2–2.0 MV**: the whole 441–1225 keV range of interest, with no column shorting |
| Beams | ¹H⁺ up to **1000 nA**; ⁴He⁺ up to 1000 nA; ³He⁺ up to 30 nA (also ²H⁺ per older slides) |
| Current limits | "Up to 1000 nA on all beamlines **except 0°**. At small spot radius ~150 nA. The **0° line is limited to 20 nA** (1 nA with the microbeam)." |
| Beam lines | One dedicated room. Lines at angles off a switching magnet; the 0° line has the microbeam and a new precision chamber (≤10⁻⁷ mbar, ±0.5 °C water). The other lines and their free floor space: **(ask)** |
| Operation | **Self-service mode** in the 2025–26 period: "one energy change per day will be provided by the operating staff". |
| Energy spread | Not quoted for AN2000 **(ask)**. For a belt VdG with analysing magnet, ~1 keV is typical. That is well inside the 12 keV width of the 441 resonance. |
| Already doing X17 | **Yes.** The LNL-INFN e⁺e⁻ pair spectrometer (Góngora-Servín, Marchi, Tagnani, Celentano, Goasduff, Valiente-Dobón) ran on AN2000 in **2023–2024**: LiF targets of 34–935 µg/cm², 441 keV and 1.03 MeV (mid-target), **typical 800 nA**, ~790 h of beam. Analysis "ongoing, results soon" as of the Dec 2024 proceedings. |

### CN: more current, and a pulsed beam

| | |
|---|---|
| Type | Single-stage Van de Graaff, LNL's oldest (installed **1961**), refurbished. 7 MV design. |
| Voltage | **0.8–5.5 MV** routinely (6 MV by agreement). Below 3 MV the column is partially shorted, and returning to high voltage needs reconditioning (1 day to 4.6 MV, 3 days to 5.5 MV). "Between 3 and 5 MV the machine slowly deconditions." So **parking it at ~1 MV for weeks is fine; mixing with high-energy users is not**. |
| Beams | ¹H⁺ up to **4000 nA**; ²H⁺ up to 1000 nA; ⁴He⁺ up to 1000 nA, all continuous. **At 0.8–2 MeV: up to 1000 nA** in the beam sheet. The radiation-protection limits come from neutrons; there are **none below the 1.88 MeV ⁷Li(p,n) threshold**. |
| Technical max | "Continuous proton currents up to ~6 µA are technically achievable … the authorised continuous-beam limit is presently ~4 µA" (CN paper, 2026). |
| Beam lines | One experimental hall, **seven beam lines**. Small-angle lines (−15°, 0°, +15°) get full current; larger-angle lines can drop to 30 %. |
| Pulsed mode | **3 MHz, < 2 ns FWHM**, up to **700 nA**. A secondary chopper gives 1.5 MHz–500 kHz with ~1 ns pulses. This is a cosmic-ray and accidental handle that no previous ⁸Be experiment had (see `PHYSICS.md`). "A limited number of pulsed-beam days" per PAC period. |
| Energy spread | σ_E/E ~ 10⁻³ (σ_E = 5.5 keV quoted at 5.5 MeV; ~1 keV at 1 MeV) |
| Spot | 2–8 mm FWHM standard |
| Schedule | "Available for experiments on working days (Mon–Fri), mainly during daytime. Running beyond those hours requires authorisation." **(ask)** whether multi-week continuous running at 1 MeV is possible. |
| Lithium expertise | The CN 0° line already runs **metallic-lithium targets** (10–40 µm Li pressed on 300 µm Cu, made in an Ar glovebox; 10 W, i.e. 5 µA at 2 MeV) for quasi-monoenergetic neutrons. LENOS/BNCT work at LNL (P. Mastinu) built high-power Li targets. |

## Getting beam time

- **Route:** the LNL **Program Advisory Committee (PAC)** allocates both the Tandem complex
  and CN/AN2000. In the 2025 cycle the call deadline was **3 Sept 2025**, the PAC met
  **8–10 Oct 2025**, and it allocated **Oct 2025 – Jul 2026**. The PAC page says the next
  meeting is "in fall 2026". **(ask)**: the 2026 deadline has probably passed.
  When is the next call, and is there an out-of-cycle route for CN/AN2000? Small
  machines are often scheduled more flexibly.
- **Proposal:** LNL Word/LaTeX templates (`call-for-pac-proposals`). Content:
  - motivation;
  - technical details;
  - expected results;
  - **beam days justified by count-rate estimates** (this directory gives them).

  An internal LNL technical review comes before the PAC: beam availability,
  intensity, energy, radioprotection.
- **Procedures:**
  - access registration at least 15 days ahead;
  - radiation-protection training certificate;
  - a Declaration of Responsibility per shift, plus a safety data sheet for a new
    experiment;
  - personal dosimeters from the RP service;
  - shifts communicated to RP ≥ 3 days ahead.
- **Contract:** Dylan will have an LNL contract, which presumably makes the access
  paperwork internal **(ask)** what that changes in practice.

## Who is already there

- **The LNL ⁸Be pair spectrometer group.** T. Marchi (spokesperson in the 2021 talk),
  B. Góngora-Servín (PhD Ferrara 2024: "Searching for the Anomalous Internal Pair
  Creation in ⁸Be"), D. Tagnani (Roma Tre), A. Celentano (Genova), A. Goasduff,
  J.J. Valiente-Dobón. Funded by INFN-CSN3 (NUCLEX); groups from Padova, Genova,
  LNF, Roma 1, Roma 3, Catania.
  - Their apparatus is ATOMKI-like: 4–5 "clovers" of four EJ-200 ΔE–E telescopes
    with SiPM readout, at 12.5–15 cm, in vacuum.
  - Their AN2000 data (2023–24) are the obvious first thing to ask about. They are
    the natural partners, or competitors. Talk to them first.
- **P. Mastinu and A. Selva.** CN, lithium targets, neutron fields.
- **Our own collaboration.**
  - The n_TOF X17 proposal is from INFN Roma (C. Gustavino).
  - Part of our setup was **already tested at ATOMKI on ⁷Li(p,e⁺e⁻)⁸Be** (Krasznahorkay
    2024 review, §2.9). **(ask)** internally for those data and the geometry used.

## What it means for us

1. **The beam is not the limit.**
   - A 1 µA proton beam at 1.04–1.10 MeV is routine on both machines.
   - It is the same current ATOMKI used in 2016, and 1/5 of what they used in 2022.
   - CN can give up to ~4 µA, and also pulsed beam.
   - There are no neutrons below 1.88 MeV, so the radiation-protection limits that
     dominate the CN paper do not bite.
2. **AN2000 is LNL's choice** and their group is already installed there. If we
   go on CN, we get more current and the pulsed beam, but compete with
   neutron/irradiation users and with the CN's daytime schedule.
3. **The hall geometry is the unknown.** Our four arms have 44 cm Micromegas at
   ~20 cm, backed by SiPM walls and plastics, roughly a 1.2 m cube around the
   target. That needs a beam line ending in open floor with ~1 m clearance on every
   side, at a height and orientation we must pick (beam horizontal; cosmics mostly
   vertical). **(ask)** for floor plans of the AN2000 room and the CN hall.
4. **Self-service AN2000** means one energy change per day. That suits us: the plan
   is a few fixed energies (441 keV calibration, 1.04–1.10 MeV), each held for days.

## Open questions for LNL (ask)

- AN2000 room and CN hall floor plans, beam-line heights, free lines, crane, cable
  paths to a control room.
- AN2000 energy calibration/spread and current stability at 1 µA for days; is the
  20 nA 0° limit relevant to the line we would get?
- CN: can it sit at ~1 MV for weeks? Is weekend/overnight running allowed? How
  many pulsed-beam days are available, and with what current at 1 MeV (700 nA quoted
  at 3 MHz)?
- Target lab: can LNL evaporate Li₂O / LiF / enriched ⁷LiF on chosen backings and
  measure thickness (RBS/NRA on AN2000)? Who handles metallic Li (LENOS glovebox)?
- The 2023–24 LNL ⁸Be data: status, and whether a joint effort is welcome.
- Overburden of the halls (cosmic rate). LNL is at ground level.

---

## Sources

| key | reference | file |
|---|---|---|
| LNL-B | LNL, "Beams available AN2000–CN" (linked from the 2025 PAC call) | `refs/LNL_Beams_AN2000_CN.txt` |
| LNL-PAC | LNL PAC call, Oct 2025 meeting, A. Gottardo / A. Selva | `refs/LNL_PAC_Call.txt` |
| LNL-V | LNL Users Vademecum, Sept 2024; Procedures for LNL users | `refs/LNL_Vademecum_Users_2024_09.txt`, `refs/LNL_Procedures_for_users.txt` |
| LNL-Br | LNL brochure (EN) | `refs/LNL_Brochure_EN.txt` |
| LNL-acc | "LNL accelerator facilities" talk (IFJ indico) | `refs/LNL_accelerator_facilities_slides.txt` |
| CN26 | "Development and validation of a forward 0.7–4 MeV quasi-monoenergetic neutron capability at the CN Van de Graaff of LNL", arXiv:2605.12005 (2026) | `refs/CN_quasimono_neutrons_arXiv2605.12005.txt` |
| Ma21 | T. Marchi, "Experiments on ⁸Be IPC at INFN Legnaro Laboratory", Shedding light on X17, Rome, 4 Sep 2021 | `refs/Marchi2021_Aipac8Be_LNL_slides.txt` |
| GS25 | B. Góngora-Servín *et al.*, "e⁺e⁻ pair spectrometer for studying the internal pair creation in ⁸Be at LNL-INFN", Acta Phys. Pol. B Proc. Suppl. **18**, 2-A13 (2025) | `refs/GongoraServin2025_ActaPPB_LNLspectrometer.txt` |
| Mas | P. Mastinu, LENOS / LNL lithium-target slides | `refs/Mastinu_LNL_slides.txt` |
| AK24 | A.J. Krasznahorkay *et al.*, "An update on the hypothetical X17 particle", arXiv:2409.16300 (2024): world status incl. LNL, n_TOF, Montreal, Prague | `refs/Krasznahorkay2024_update_arXiv2409.16300.txt` |

Not retrieved: B. Góngora-Servín's PhD thesis (Ferrara, 2024), behind a 403 at
sfera.unife.it. It has the full detector and target description. Worth getting by
email.
