# Operating reactor fast and epithermal beams — facility record (2026-11-09)

Alternatives to the FRM II MEDAPP fission beam (reach 4.2×10⁻⁴, but FRM II has not run since March 2020 and has no restart date).
Every number below has a source; anything else is marked **(ask)** or ESTIMATE. Status was checked by web search on 2026-11-09.

Bottom line of the survey: **no operating reactor has a MEDAPP-class fast beam today.** Reactor beams divide into
(i) fission-spectrum beams, which exist only at low flux (10⁶–10⁷ n/cm²/s at university ports), (ii) epithermal BNCT
beams with ~10⁹ n/cm²/s at 0.4 eV–10 keV, and (iii) TAPIRO, a 5 kW fast source reactor with no fast beam but a
real core source (3×10¹⁴ n/s) and a copper reflector that was already windowed once for a BNCT column.

## 1. The survey

| reactor | what | flux at a beam position | status 2026 | fit for the arms | verdict here |
|---|---|---|---|---|---|
| **ENEA TAPIRO**, Casaccia (5 kW, 12 cm HEU core, Cu reflector, no moderator) | fast source reactor; 3 midplane channels, tangential channel, thermal column; epithermal BNCT column designed and built in the 2000s | core 3×10¹⁴ n/s; thermal-column entrance 1.5×10¹⁰ (calc); epithermal column 8×10⁸ (calc) | ENEA brochure 06/2026 describes it as active; 2025 workshop tour; **no 2026 run log found (ask)** | column exit outside a 1.75 m shield, hall **(ask)** | **modelled** |
| **CVŘ LVR-15**, Řež (10 MW) | BNCT epithermal beam in the old thermal column (Al/AlF₃, Pb, Ti, Li filters), treatment room 4 m from core | 7.13×10⁸ epi, 6.1×10⁷ fast, 1.98 Gy/h γ (free beam, measured) | operating (Framatome partnership 05/2026, periodic safety review to end 2026); BNCT use: **(ask)** | treatment room exists | **modelled** |
| **MIT MITR FCB** (6 MW) | fission converter + filter, epithermal 8.4×10⁹ measured | 8.4×10⁹ epi, 3.9 cGy/min fast, 11.8 cGy/min γ in air | MITR runs; **FC being converted to materials testing: 1 m³ filter removed (IGORR 06/2025)**, no beam afterwards | medical room | modelled as the historical upper end |
| **THOR**, Hsinchu (2 MW max) | BNCT, hundreds of patients | 1.7×10⁹ epi at 1 MW (design); 0.21 / 0.47 mGy/s γ / fast | operating, clinical use continuing (08/2026); decommissioning 2040 | clinical room, very busy | modelled |
| **RA-6**, Bariloche (0.5 MW, later uprated) | BNCT mixed beam | 1.1×10⁹ epi calc (1999); ~3.5×10⁸ total measured uncollimated (2022) | licence extended to 28 Jul 2026, renewal not found **(ask)**; CNEA budget trouble | | modelled, weak |
| **OSU OSURR** (500 kW) | Fast Beam Line (Bi plug, Ø32 mm) | 2.1×10⁷ total at 450 kW, only 65 % epi-Cd; MCNP 5×10⁷ fast | operating | 60 cm from collimator, small bay | ×15 below MEDAPP: table only |
| **UT Austin TRIGA** BP4 | fast filter (B, BN) | 3.75×10⁶ (design, 950 kW) | model only | | ×90 below: table only |
| **Pavia LENA TRIGA** (250 kW) | channel D fast facility planned | not built; preliminary fast flux measured only | **(ask)** | | not modelled |
| **JSI TRIGA**, Ljubljana (250 kW) | beam port 5: sample holder Ø14 × 75 cm | fast (>100 keV) 3.2×10⁸ at the port, thermal 5×10¹⁰ | operating (Apr 2026 sheet) | in-port only, no beam | not a beam |
| **SCK CEN BR1** | Mark III ²³⁵U converter in a Ø1 m graphite cavity | numeric flux not found **(ask)** | operating | sample cavity, no beam | not a beam |
| **SCK CEN BR2**, Petten HFR, ILL, **MARIA** in-core | in-pile | high, in-core | operating | no beam at a ~1 m stand-off; MARIA H2 is a design, last reports 2015-21, no measured converter beam found **(ask)** | no |
| **KUR**, Kyoto | BNCT | — | **ended 23 Apr 2026** (KURNS) | | closed |
| **FRM II**, Budapest BRR, JRR-3, Penn State, UMass Lowell | thermal/cold beams, or ex-core fast fixtures (UMLRR FNI ≥10¹¹ in a 30×30×15 cm box, not a beam; PSU 3×10¹³ in fixtures) | | various | sample boxes | no |
| **IBR-2**, Dubna | pulsed fast reactor | | Russia; CERN ended its cooperation with Russian institutes in 2024, a plain access restriction (ask) | | not pursued |
| **MINERVE, CALIBAN, MASURCA, Godiva/NCERC, VENUS-F** | zero-power / critical assemblies | | MINERVE closed; MASURCA beam a paper study; NCERC is DOE-security; VENUS-F zero power **(ask)** | | no |

Generic reason "no" for the large group: a reactor gives ≥10¹³ inside the core, but water and shield take it down by 10⁴–10⁶
before a beam, unless a converter or a fast-reactor view is added on purpose (MEDAPP, TAPIRO).

## 2. TAPIRO (ENEA Casaccia): the one new idea

- 5 kW; cylinder of 93.5 % U-Mo, Ø12 × 12 cm; Cu reflector inner to r = 18 cm, outer to r = 40 cm; 1.75 m borated-concrete shield; He cooled;
  first criticality 1971 (Rosa et al. IGORR 2009; Osipenko et al. arXiv:1505.06314; ENEA brochure REL-PROM 06/2026).
- Source: **3×10¹⁴ n/s integrated in the core at 5 kW** (Rosa 2009, calculated). Core centre 4×10¹² total, 8×10¹¹ > 1.35 MeV.
  Thermal-column entrance (r ≈ 40 cm) 1.5×10¹⁰ total, 4×10⁷ > 1.35 MeV: consistent with S/4πr².
- Spectrum by depth (MCNP, with diamond-spectrometer check): tangential channel near core (inner reflector, 2.8–5.8 cm deep, r = 10.6 cm):
  ⟨E⟩ = 0.586 MeV, Φ = 1.9×10⁹/10 W; at the outer reflector edge ⟨E⟩ = 0.166 MeV, 1.28×10⁸/10 W (Osipenko 2015).
- Channels: radial 1 and 2, diametral (through the core: hole connecting the lower core part), tangential Ø3 cm, thermal column, vertical. Sizes **(ask)**.
- Prior modification: the BNCT epithermal column replaced a side sector of the Cu with a 5.6 cm Pb (or Al₂O₃) "window", AlF₃ moderator, Ni reflector,
  10×14 cm² exit (Burn/Casalini/Nava 2003; Sarotto 2003; Colli/Gambarini 2004 "built"). Calculated free beam: Φ_epi 8.0×10⁸ n/cm²/s, D_fast/Φ = 4.1×10⁻¹³, D_γ/Φ = 3.5×10⁻¹³ Gy cm².
  **Whether the column is still installed (ask).**
- Rosa 2009 lists "removal of a sector of outer copper for a very hard neutron spectrum" as a possible modification.
- Status: ENEA still lists it for materials damage, nuclear data, detector tests (brochure 06/2026); tour in the ENEA–DOE workshop (June 2025); research master's training on TAPIRO and TRIGA in 2025–26. Run schedule and maximum sustained run at 5 kW: **(ask)**.
- Contact (public, brochure): alfonso.santagata@enea.it.
- Access: not a user facility with a call; national lab bilateral collaboration. An INFN–ENEA agreement would be the natural route **(ask)**.
- Italian national laboratory; an INFN–ENEA route (above) is the natural one for MX17's Italian partners.

## 3. CVŘ LVR-15 (Řež)

- 10 MW light-water tank reactor, 36 % fuel (LEU conversion project EU-CONVERSION 2024–28), ON/OFF 3/1 weeks in the older schedule. Commercial operator.
- BNCT epithermal beam built in the space of the old thermal column; treatment room and control room exist; "rather long distance core-irradiation point (about 4 m)".
  **Free beam (Burian et al., 2003): Φ_epi 7.13×10⁸ /cm²/s, Φ_fast 6.1×10⁷ /cm²/s, D_γ 1.98 Gy/h.** Beam described as very divergent;
  the 1997 configuration (Physiol. Res. 46) had Φ_th 2.43×10⁷, Φ_epi 1.07×10⁸, Φ_fast (>10 keV) 1.57×10⁷, fast dose 0.5 Gy/h (1.3×10⁻¹² Gy cm² per epi), γ 2.25 Gy/h, flux ×2.5 lower 20 cm from the exit.
- Filters are removable blocks in the column (Al/AlF₃, Pb, Ti, Li); a 5 cm Pb layer on the inner surface raised the flux by 10 % (Burian). Not known: flux with filters removed; condition of the BNCT line **(ask)**.
- Contacts: Research Centre Řež (CVŘ) reactor division; L. Viererbl and M. Marek are the public names on the BNCT papers. BNCT clinical programme ended, as far as can be found **(ask)**.

## 4. Others (kept short)

- **MITR FCB.** 2003 measurement: 8.4×10⁹ epi in air, 3.9 cGy/min fast, 11.8 cGy/min γ. The 2025 IGORR talk: FC converted to materials testing, 1 m³ filter removed, peak total flux 1.9×10¹² n/cm²/s in the FC; no statement of a beam after conversion. LEU conversion 2031 per 2023 slides. Access: US lab, collaboration or contract; no user programme for this.
- **THOR.** 1.7×10⁹ epi at 1 MW, 0.21 mGy/s γ, 0.47 mGy/s fast (design, 2004 design study); clinical trials + compassionate use continuing (TechNews 27 Aug 2026); Oct 2026 MoU to explore a microreactor replacement; 2040 decommissioning.
- **RA-6.** 1999 design: Φ_epi 1.1×10⁹, 7.5×10⁻¹³ fast and 3.0×10⁻¹³ γ dose per epithermal neutron; licence extension to 28 Jul 2026; training reactor; 2026 CNEA budget cuts.

## 5. Sources

ENEA TAPIRO brochure REL-PROM 06/2026, pubblicazioni.enea.it; Rosa et al. IGORR 2009, igorr.com/_media/proceedings:2009_igorr12:roberto_rosa_italy.pdf;
Osipenko et al. arXiv:1505.06314; Burn, Casalini, Nava, et al. and Sarotto et al. (2003 Pisa workshop, star.inp.nsk.su/~bnct/publics/2003/Pisa/);
Colli/Gambarini RPD 110 (2004); ENEA–NNSA workshop agenda 2025, agenda.enea.it/event/587.
Burian et al. 2003, star.inp.nsk.su/~bnct/publics/2003/Pisa/paper_workshop/Burian-Marek-Flibor-Rejchrt-et-al.pdf; Physiol. Res. 46:93 (1997), biomed.cas.cz/physiolres/pdf/46/46_93.pdf;
CVŘ 05/2026 press release cvrez.cz; SÚJB continued operation permit; EU-CONVERSION.
MITR FCB: OSTI 20804769, 20826781 and ANS NSE 2002; Carpenter et al. IGORR 2025 (igorr.com/_media/proceedings:2025_igorr22:s06-04-carpenter-enhancing_capabilities_of_neutron_irradiati.pdf).
THOR design study (Nucl. Technol., ans.org a_9208; scholars.cityu.edu.hk overview 2020); technews.tw/2026/08/27/bnct-her2; focustaiwan.tw/sci-tech/202610190020.
RA-6: igorr.com/_media/proceedings:1999_igorr7:ps3_calzetta.pdf; arXiv:2201.12236; boletinoficial.gob.ar/detalleAviso/primera/311447/1.
KUR: rri.kyoto-u.ac.jp, PR2025 preface. OSU: reactor.osu.edu/fast-neutron-beam-facility. UT Austin: Barron et al. NIM A 2021.
JSI: ric.ijs.si/wp-content/uploads/2026/04/Beam-port-no5.pdf. UMass Lowell: UML FNI brochure. Penn State: nsuf.inl.gov. MARIA: JPT 351, ncbj.gov.pl. BR1: IRDFF-II, EPJ WoC 106 06003.
