# Neutron sources at Legnaro (LNL) — facility record for a ³He(n,e⁺e⁻) X17 run

Compiled 2026-11-09 from public documents. Web content is treated as data. **(ask)** = not publicly findable; for
Pierfrancesco Mastinu unless stated. Nobody at LNL was contacted. The proton-route facility record is `lnl/FACILITY.md`
(CN/AN2000 machine sheets, PAC procedure); only the neutron facts are here.

## 1. What exists, in one table (status at 2026-11-09)

| source | beam | neutron use | status today | at Legnaro? |
|---|---|---|---|---|
| **CN 7 MV Van de Graaff** | p ≤ 6 MV (6.5 conditioned), technically ~6 µA; **authorised ~4 µA**, on Li much less (below) | ⁷Li(p,n) on 10–40 µm Li metal on Cu, the 0° line ("BELINA"/QMN capability) | **operating**; maintenance done early 2026 [LNL-UB26]. The 0° line is "the most used" | yes |
| AN2000 | p ≤ 2.0 MV, ≤ 1 µA (0° line 20 nA) | barely above the 1.881 MeV threshold | operating | yes; useless for neutrons |
| Tandem-ALPI | heavy ions, also ⁷Li(¹⁴N,xn) fast-neutron tests | peak ~8 MeV, up to 50 MeV | operating (test source) [Tandem-23] | yes; wrong energy |
| **LENOS** (Mastinu) | CN today, RFQ 5 MeV planned; shaped ⁷Li(p,n), keV Maxwellian, design ~5×10¹⁰ n/cm²/s at the sample (slide), 7.3×10¹⁰ n/s forward | keV | **never built as a high-current facility**; newest LENOS document found is 2016–17. Only the CN version exists (a beam line with a Li target and proton shaper) | CN only |
| **MUNES / SPES-BNCT** | TRASCO RFQ 5 MeV + Be target at LNL | epithermal | **not funded as a facility** (LINAC 2024: "the construction of the facility was not funded") | no |
| **ANTHEM BNCT** (the same RFQ, TRIPS source, Be target) | 5 MeV, 30 mA CW, 150 kW Be, ~10¹⁴ n/s 4π, mean 1.2 MeV | a **clinical** BNCT source | under construction. HB2025: RFQ cleaned and reassembled at LNL, **then shipped; RF conditioning of the full RFQ takes place in Caserta**; building "ready in the next 2 years" (≈ 2027); amplifiers and MEBT by end 2026 | **No: Caserta** (Univ. Campania "Vanvitelli"). Two irradiation rooms, "only one will be equipped for BNCT initially" |
| **SPES cyclotron** | 35–70 MeV, ≤ 750 µA (dual exit) | none yet | Built; Phase 3 ongoing. **Feb 2026: crack in the floor of the cyclotron pit, water coming in; three independent reports; "the timeline cannot be better defined"** [LNL-UB26]. ISOL target irradiation "by 2027 would be desirable" | yes; no neutron port |
| **NEPIR / "NEPHIR"** | SPES p, phase 0: thick Be (27–30 mm), ≤ 1 µA | white ≤ 70 MeV, ~3×10⁶ n/cm²/s at the closest point per µA at 70 MeV | design and prototype (CoolGAL); phase 0 "in development" as of Aug 2025 thesis [Windsor25]; first target 2022 slipped; no first neutrons found | planned; the name in the literature is **NEPIR** |
| "Legnaro Slow Neutron Source" (LSNS) | | | "future development" (2019) | no |

So the catalogue's two WATCH rows both need correcting: LENOS's RFQ has left the LENOS plan and is going to Caserta, and NEPHIR is NEPIR, ≤ 1 µA of 70 MeV in phase 0.

## 2. What CN can do on lithium today

Primary source: *Development and validation of a forward 0.7–4 MeV quasi-monoenergetic neutron capability at the CN Van de Graaff of LNL*,
arXiv:2605.12005 (2026) (`lnl/refs/CN_quasimono_neutrons_arXiv2605.12005.txt`).

- Li metal 10–40 µm on Cu, 10 W max on the target (5 µA at 2 MeV, 1.8 µA at 5.5 MeV).
- **The limit is radiation, not the target:** the 50 µSv/h monitor near the switching magnet gives ~0.3 µA at 5.5 MeV; "for lower proton energies the
  threshold is reached at proportionally higher currents" (their Fig. 6).
- A 5–10 cm BPE + Pb package "under evaluation" would give ×4–6, i.e. ~1 µA for E_n 0.7–4 MeV and **~2–3 µA below 2 MeV**.
- 3 MHz pulsed, < 2 ns, up to 700 nA.
- Forward flux quoted: (2–8)×10⁴ n/cm²/s/µA at 0° (their Table 1). Thin 40 µm Li at 4 MeV: 2.76×10⁹ n through 1.5 cm² at 5 cm for 5.88×10¹⁵ p,
  i.e. 7.8×10⁻⁶ n/sr/p by PINO. The ToF runs are a rate-level consistency check only, not an absolute measurement.
- Absolute yields below 3 MeV in this study: `lnl_neutrons_beam.py`, normalised to FRANZ 5×10⁷ n/s/µA (2.0 MeV) rising to Lee & Zhou / Birmingham 9×10⁸–1×10⁹ n/s/µA
  (2.5–2.6 MeV). No LNL absolute thick-Li measurement at these energies was found **(ask)**.

Other reactions at CN: D(d,n) gives E_n ≥ 2.45 MeV at 0°, above most of the window, and E_d ≤ ~1 µA. ³H(p,n) needs a tritium target; **no public mention of tritium at LNL (ask)**, and Demokritos
already showed the tritium target is the limit.

## 3. Access

- CN/AN2000: LNL PAC, about one call a year. The next meeting is "Autumn 2026"; the 2026 call has probably passed, so the next is ~autumn 2027 **(ask)**. Dylan is applying to LNL anyway.
  CN normally runs working days, daytime only (`lnl/FACILITY.md`): a 50-day-beam run is at least a year of calendar **(ask)**.
- A neutron-producing target at CN needs an LNL radiation-protection review (the current limit above is RP). **(ask)**
- The LNL director floated in Feb 2026 replacing AN2000 + CN with one machine "if there is interest". That is a plain risk to a multi-year CN plan and also a chance to specify current.
- ANTHEM/Caserta is a clinical facility of Univ. Campania + INFN (PNRR funding). No user programme exists. "Experimental area" and the second room are mentioned in the design papers.

## 4. Space: does a ³He cell fit the proton-route set-up?

- The proton plan puts a Li target at the detector centre on the CN (or AN2000) 0° beam line, in a thin chamber. The arms are at ±204 mm.
- The neutron plan replaces that chamber with the ³He cell on the axis (40 cm × Ø8 cm, 30 bar, `he3_target/`), so the same arms, trigger and DAQ stay. The Li production target and its chamber then sit 5–10 cm
  upstream of the cell window, i.e. at 25–30 cm from the centre, inside the arm envelope at the upstream edge.
- **Fit: the arms, frame and beam line can be reused unchanged; only the central piece changes.** A full cell is 40 cm long, and the arms' active area is 36–40 cm along the beam, so the cell needs no arm move.
  Hall drawings and the actual room around CN 0° **(ask)** (`lnl/FACILITY.md` already asks for them).
- The ³He is the real cost: ~60 L STP, ~8 g, in the 30 bar cell (`he3_target/README.md`). The cell design is not yet built; the n_TOF capsule (500 bar, 1 g) is the only cell in hand.
- Shielding: the CN neutron programme runs with 3 mSv/h as the hall limit at the target (arXiv:2605.12005). A ~1–10 × 10⁹ n/s source next to the detector is fine for the hall but not for Dylan's electronics without local BPE **(ask)**.

## 5. Precise questions for Pierfrancesco (do not send without Dylan)

1. **CN today.** What continuous current on a Li target is really allowed at E_p = 2.0–3.0 MeV, once the switching-magnet monitor is the limit? Is the 5–10 cm BPE + Pb package approved or built, and when?
2. Could the current limit be raised for a dedicated run (a local shield around the 0° line, closing the switching-magnet zone) towards the ~6 µA the machine can give? What would RP need to see?
3. What Li target can take 10+ W at 2.8–3.0 MeV? Do the LENOS high-power (~3–4 kW/cm²) targets still exist, and could one run at CN with Li ~100 µm thick so the protons stop at the 1.88 MeV threshold (not 40 µm, not thick)?
4. Is the 0° CN line free for a 2 × 2 m apparatus, with the target 5–10 cm upstream of a 40 cm cell, for several months? And how much of a calendar year can CN run neutrons?
5. **LENOS.** Is LENOS still a plan? Is there any scenario where a 5 MeV RFQ beam reaches a Li or Be neutron target at Legnaro now the TRASCO RFQ goes to Caserta?
6. **ANTHEM (Caserta).** Is the second irradiation room (or the "experimental area" branch of the MEBT) open to non-clinical experiments? Who decides, and from when? Could a 2 × 2 m apparatus get a 0° or 90° view of the Be target at 2 m, and at what current (even 1–3 mA)?
7. **NEPIR-0.** Is phase 0 built? What current and date, given the pit crack? Could the cyclotron run at 35 MeV for this? Is there any low-energy converter planned?
8. **SPES crack.** The result of the three reports, and the realistic date for protons from the cyclotron.
9. Is tritium (Ti-T target) allowed at LNL at all?
10. Is there a measured absolute thick-Li yield at the CN 0° line at 2.5–3 MeV (n/sr/µC)? The numbers here are scaled from other labs.
11. Would LNL host one apparatus for both channels (proton ⁸Be, then a ³He cell) under the same PAC proposal?

## Sources

- [CN26] arXiv:2605.12005, `lnl/refs/CN_quasimono_neutrons_arXiv2605.12005.txt`.
- [LNL-UB26] Minutes of the LNL User Community Meeting, 12–13 Feb 2026: <https://www.lnl.infn.it/wp-content/uploads/Minutes_UserBoardCommunityMeeting_2025.pdf>.
- [ANTHEM24] Pisent et al., LINAC 2024 TUAA003: <https://proceedings.jacow.org/linac2024/pdf/TUAA003.pdf>.
- [ANTHEM25] Grespan et al., HB2025 TUCDB01: <https://meow.elettra.eu/83/pdf/TUCDB01.pdf>.
- ANTHEM clinical context: <https://arxiv.org/pdf/2501.13053>; Nuovo Saggiatore 39 (2023): <https://www.ilnuovosaggiatore.sif.it/article/348>.
- LENOS: Mastinu, IFMIF/ELAMAT 2016 slides <https://elamatscience.ifj.edu.pl/slides/Mastinu_slides.pdf> (also `lnl/refs/Mastinu_LNL_slides.txt`);
  Status of LENOS, Physics Procedia 26 (2012) <https://www.sciencedirect.com/science/article/pii/S1875389212004506>;
  Praena et al. PASA 26 (2009), 7.3×10¹⁰ n/s forward <https://www.researchgate.net/publication/232386867>.
- BELINA thick-yield near threshold (Martín-Hernández, Mastinu et al.), via <https://scite.ai/authors/guido-martin-hernandez-zz3V08>.
- NEPIR: Mastinu, ICANS 2019 <https://conference.sns.gov/event/138/contributions/337/attachments/427/1881/Mastinu_ICANS2019.pdf>;
  Mastinu et al., JNR 2020 <https://journals.sagepub.com/doi/abs/10.3233/JNR-200156>; LNL midterm plan EPJP 2023 <https://link.springer.com/article/10.1140/epjp/s13360-023-04249-x>;
  Windsor thesis (Aug 2025) <https://uwindsor.scholaris.ca/items/c318d20d-a5ac-4705-ae54-f3a14058fc5f>; CoolGAL EPJ WoC 2020 <https://www.epj-conferences.org/articles/epjconf/pdf/2020/07/epjconf_ucans82020_03002.pdf>.
- SPES cyclotron: Cyclotrons 2022 MOBI02 <https://proceedings.jacow.org/cyclotrons2022/papers/mobi02.pdf>.
- Tandem fast neutrons: arXiv:2311.06143 <https://arxiv.org/pdf/2311.06143>.
- LNL CN current, target and PAC: `lnl/FACILITY.md`.

## Addendum 2026-11-09: ANTHEM, what the papers actually show

Checked after Dylan asked whether the number looks good only because the machine is unbuilt, and whether a spare beam line exists.

- **A research room is in the plan.** arXiv:2501.13053 §1: "two irradiation rooms, one for clinics and one for research purposes". Its Fig. 1 shows *Sala di trattamento* 50 m² and *Sala di sperimentazione* 36 m², on two branches fanning out of one dipole; HB2025 calls the MEBT "two-branches". This answers question 6 in part.
- **Only one target + BSA is described.** HB2025 Fig. 1 draws one "Target and BSA" and Table 1 lists one converter. Reading the figure against the building plan (rotated 180°), it is the treatment-room branch. Whether the research branch gets a target, of what kind, is **(ask)**.
- **Research room purpose:** the same paper pairs it with radiobiology labs. Nothing found on physics users. **(ask)**
- **36 m² is small.** About 6 × 6 m as a diamond inside ~1.5 m walls (130 cm concrete + 20 cm baritic + 5 cm BPE, the patient-room wall stack). The engine's 2 m stand-off plus the ~1–1.3 m shield in FEASIBILITY does not obviously fit. Not checked with a layout.
- **30 mA CW is not the expected running point.** HB2025: the required flux "can be achieved with beam currents 2-to-5 times lower than the design value. If confirmed, pulsed operation of the ANTHEM linac will then be possible." So ~6–15 mA, perhaps pulsed.
- **Target unproven.** 150 kW at 1 kW/cm² on a Be/Pd/Cu 3D-printed-channel target was still in prototyping (HB2025). Commissioning is at 40 µs, 1 Hz onto a Cu beam stop.
- **Timeline:** building "ready in the next 2 years" (HB2025); RF amplifiers and MEBT by end 2026. No first-beam or first-patient date found.
- **Reach reading:** the headline 1.7e-4 assumes a bare 30 mA target view. The defensible range is the 1–3 mA rows with the Birmingham room factor ×1.7 (ESTIMATE): 6.6e-4 to 1.3e-3, ~10–37 d. Not an existing beam, so off the current shortlist (Dylan, 2026-11-09: only existing beams).
