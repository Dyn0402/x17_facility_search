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

**2026-11-25: slot 1 in June or July 2027.** The January call allocates beam from 20 Feb to 30 Jul 2027 (the call page prints
2026; Pierfrancesco confirmed on 25 Nov that it schedules only up to July). The proposal therefore asks for June or July 2027, not
the second half of 2027. Plan: both arms on cosmics by 14 May, installation from 14 Jun, beam ~5–14 Jul (lnl_x17
`slot1_feasibility/PLAN.md` §5).

**2026-11-25: slot 1 moves to the CN.** AN2000 is probably not available (Dylan). The allocation is 8 days: the
proposal asks 8 working days at 1 µA (8 h of beam per working day assumed), with one day of H₂⁺ at 0.883 MV for the
441 keV point (else 1.10 MeV). 46 h at 1.10 MeV give 3.8 × R(ATOMKI) with the built hemisphere (2.35 × with 24-hour
days; 1.7 × at 4 µA, an ask). lnl_x17
`slot1_feasibility/CN_BEAM.md`.

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
| Beams | ¹H⁺ up to **4000 nA** (the 5.5 MV row); ²H⁺ up to 1000 nA; ⁴He⁺ up to 1000 nA, all continuous. **At 0.8–2 MeV: up to 1000 nA.** The sheet's footnote: "Maximum current can be limited by radio-protection constraints in case of high neutron fluxes generation. Energy from 0,8 to 2 MeV up to 1000nA, Energy from 2 to 3 MeV up to 500nA, Energy from 3 to 5.5 MeV up to 200nA limited by radio-protection constraints". **So the documented current at 1.0–1.1 MeV is 1 µA** (corrected 2026-11-10: this file used to read it as 4 µA). ⁷Li(p,n) makes no neutrons below 1.88 MeV, so the limit may be negotiable for us: **(ask)**. The CN paper projects ~2–3 µA below 2 MeV only after planned shielding. |
| Technical max | "Continuous proton currents up to ~6 µA are technically achievable … the authorised continuous-beam limit is presently ~4 µA" (CN paper, 2026). |
| Beam lines | One experimental hall, **seven beam lines**. Small-angle lines (−15°, 0°, +15°) get full current; larger-angle lines can drop to 30 %. |
| Pulsed mode | **3 MHz, < 2 ns FWHM**, up to **700 nA** (CN paper §2 and §4.2; the buncher raises the energy spread). The paper does not say at what energy; its pulsed data are at 3.5–5.5 MeV, so **pulsing at ~1 MV is unverified (ask)**. A secondary chopper on the 0° line removes pulses: 1.5 MHz–500 kHz, ~1 ns. Pick-up signals exist (paper Fig. 10); whether users get one is **(ask)**. "A limited number of pulsed-beam days will be available in selected time periods" (PAC calls of Oct 2025 and Jan 2027). **What it is worth (2026-11-10, `FEASIBILITY_SIM.md` §19):** a gate on the bunch removes cosmics by the duty factor, but the average current is 0.7 of the continuous 1 µA and beam-induced accidentals rise by T/2τ (8–170×, still small). It is a cross-check and an insurance against poor cosmic rejection, not the baseline. Every earlier ⁸Be measurement we could check (ATOMKI, Hanoi, MEG II, LNL 2023–24) used a continuous beam. |
| Energy spread | σ_E/E ~ 10⁻³ (σ_E = 5.5 keV quoted at 5.5 MeV; ~1 keV at 1 MeV) |
| Spot | 2–8 mm FWHM standard |
| Schedule | "Available for experiments on working days (Mon–Fri), mainly during daytime. Running beyond those hours requires authorisation." **(ask)** whether multi-week continuous running at 1 MeV is possible. |
| Lithium expertise | The CN 0° line already runs **metallic-lithium targets** (10–40 µm Li pressed on 300 µm Cu, made in an Ar glovebox; 10 W, i.e. 5 µA at 2 MeV) for quasi-monoenergetic neutrons. LENOS/BNCT work at LNL (P. Mastinu) built high-power Li targets. |

## Getting beam time

- **Route:** the LNL **Program Advisory Committee (PAC)** allocates both the Tandem complex
  and CN/AN2000. In the 2025 cycle the call deadline was **3 Sept 2025**, the PAC met
  **8–10 Oct 2025**, and it allocated **Oct 2025 – Jul 2026**. The PAC page says the next
  meeting is "in fall 2026". **The current call (call page and call text re-read 2026-11-13):**
  - deadline **10 Dec 2026, 23:59 CET**; PAC meets **25–29 Jan 2027**;
  - it selects experiments for the Tandem-ALPI-PIAVE complex (**only the +20 AGATA line** this time) and for
    **CN and AN2000**; "a limited number of pulsed-beam days" at the CN in selected periods (contact the
    Accelerator Division before planning shifts);
  - submit on Indico (`https://agenda.infn.it/event/50487/`) with the LNL LaTeX/Word templates; beam questions to
    pacbeams@lnl.infn.it. Call page `https://www.lnl.infn.it/en/call-for-pac-proposals/`, text `Text_Call_Jan2027.pdf`;
  - the run period it allocates is not stated **(ask)**. The previous call was 15 months earlier (Sep 2025), so the
    next one after Dec 2026 is probably about a year later: missing this deadline likely costs a year.
  All PAC calls of the studied facilities are on the funding page's Timeline tab (`funding/schemes.py`, `BEAM`).
  **(ask)**: is there an out-of-cycle route for CN/AN2000?
  Small machines are often scheduled more flexibly.
- **Test-run request for the Jan 2027 PAC (2026-11-18).** Call text re-read: it says nothing for or against
  test / R&D requests, and it does not state the allocation period (last cycle the beam started right after the PAC, so
  probably ~Feb–Mar 2027 through most of 2027; inference, **(ask)**). Dylan emailed Pierfrancesco on 18 Nov: not ready
  for the full experiment, so propose a short run (a few days) with **one Micromegas module + a scintillator layer on a
  ⁷Li(p,γ) target**, to see the detector and trigger in the real beam environment, measure backgrounds and rates, and test
  the Li target; it would also back the funding proposals. Asked: does a test request fit this PAC, will he be local
  contact / co-proponent, what period the allocation covers. **Waiting for his reply.** If yes, the Indico proposal
  (LNL template, beam days justified by rates, `FEASIBILITY_SIM.md`) must be in by 10 Dec, 23:59 CET.
- **Pierfrancesco's answer (18 Nov, evening):** submit, stating we measure in the second half of 2027 (the PAC probably covers
  ~6 months); frame it as an **X17 feasibility study**, not detector tests; ~8 days; he makes the informal contact; a positive
  answer starts the 2-branch full detector and backs a request to "commission II" (ask which). The proposal is written in
  `~/PycharmProjects/lnl_x17` (`proposal/STRUCTURE.md` has the LNL rules: 1-page abstract with spokesperson and GLIMOS,
  ≤ 5-page body in 12 pt, online Beam Time Request + Targets Request Form, INFN-AAI account, technical review ~7 d before the PAC).
- **Two-arm run simulated (19 Nov, lnl_x17 `sim2arm/TWO_ARM_STUDY.md`):** 5 days at 1.10 MeV give an expected 90 % limit
  of 0.9–1.2 × R(ATOMKI) with liquid cells, 1.8 × without (11 µm Li); a limit, not a 3σ test. Plan: vertical cosmic nights
  before the beam, horizontal arms for the beam, 441 keV one day (~600 pairs/day), ½ day adjacent.
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

0. **The target holder is the limit (2026-11-20, lnl_x17 `sim2arm/TWO_ARM_STUDY.md` §0, Geant4 run L18).** The Cu
   hemisphere that LNL already has (R 11 mm, 300 µm wall, rim) costs ×6 in running time against the Cu ogive the 19 Nov
   two-arm numbers used by mistake: two arms, 5 days at 1.10 MeV, 11 µm Li give an expected 90 % limit of 2.35 / 3.10 /
   4.32 × R(ATOMKI) (liquid working / as at n_TOF / none), about MEG II's 2.07 ×. A lighter Al end piece (Al ogive + Cu
   liner, or the flat 45° Al cap) would give ~0.6–0.8 × (estimate). **Simulated on 25 Nov** (lnl_x17 `sim2arm/R10_AL_OGIVE.md`, the Al ogive + Cu
   liner's own ×30 tables L12 + L13): 0.88 / 1.19 / 1.70 ×, 21 / 39 / 79 days to 3σ; the scaling was optimistic. With the
   hemisphere the slot-1 run is a feasibility test; the light end piece would give about the ATOMKI ratio in five days,
   not below it. For a physics limit, ask LNL for (or build) the light end piece.
   **Pierfrancesco (20 Nov):** the hemisphere works, "at least for the forward angles"; he has asked for an engineering
   thesis on the holder. **Liquid cells are in the proposal:** the liquid exists, the cans are remade; baseline two
   45 × 45 × 2 cm cells (the "liquid working" row). Thicker (4 cm) and wider cells from ~60 L, possibly in place of the big
   plastics: lnl_x17 `slot1_feasibility/LIQUID_CELLS.md`.
1. **The beam is not the limit.**
   - A 1 µA proton beam at 1.04–1.10 MeV is routine on both machines.
   - It is the same current ATOMKI used in 2016, and 1/5 of what they used in 2022.
   - CN's 4 µA is the authorised limit at high energy. At 0.8–2 MeV the beam sheet gives
     1 µA on CN too (corrected 2026-11-10). More than 1 µA at 1.1 MeV is an **(ask)**:
     there are no neutrons below 1.88 MeV, so the radiation-protection argument behind
     the limit may not apply to us.
   - CN also has a pulsed beam (3 MHz, ≤ 700 nA; unverified at 1 MV).
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
