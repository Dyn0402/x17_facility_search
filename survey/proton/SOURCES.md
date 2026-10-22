# Sources ledger — proton survey (2026-10-22)

Confidence: **verified** (read in the source), **search** (search summary of the source, not re-read in full),
**estimate** (ours), **(ask)** (needs the facility). Raw notes: `RESEARCH_NOTES.md`.

## Physics and model

| number | value | used in | source | confidence |
|---|---|---|---|---|
| ⁸Be days at 1 µA | 1.00 d big plastics / 17.0 d as built | `proton_reach.REACTIONS` | `lnl/FEASIBILITY_SIM.md` §15 | verified (repo Geant4) |
| ⁴He days at 1 µA | 3.6 / 35 d (1 mm Cu at +12 cm); thin Cu 3.4 / 45 | same; OFFSET = 3.6/3.4 | `demokritos/ESTIMATES.md` §6.2 | verified (repo Geant4) |
| ⁸Be γ₀ yield | 1.85×10³ /s/µA, Li₂O 300 µg/cm², 1.10 MeV; 920 X17/day/µA | ¹²C scaling, headline | `lnl/ESTIMATES.md` §1 | verified |
| ⁴He X17 | 2.0×10³ /day/µA (2.1 mg/cm² Ti-T, 0.9 MeV) | headline | `demokritos/README.md` | verified |
| ¹²C claim | B_x = 3.4(3)×10⁻⁶, m 16.86, E_p 1.5–2.5 MeV, 2 mg/cm² ¹¹B on 5 µm Ta, 2 µA, ~50 h/energy, ΔE ≈ 300 keV | §1.3 | ATOMKI, PRC 106 L061601 (arXiv:2209.10795) | verified (pdf) |
| ¹²C 17.23 MeV level | Γ = 1150 keV, Γγ0 = 44 eV, Γp = 1 MeV, Γγ1 = 5 eV | σ(p,γ₀) ≈ 28 µb peak | NNDC `11b_p_g_res.pdf` (1965Se06) | verified |
| κ (¹²C vs ⁸Be shape penalty) | 2 (1–4) | §1.3 | ours | estimate |
| DAQ rates | legs 88 + 65 I, pairs 22 + 0.29 I (big); 36 + 22 I, 3.5 + 0.03 I (as built) | `live()` | `lnl/FEASIBILITY_SIM.md` §14.1 table (fit) | verified |
| thin-target limit | ~4 µA | I_THIN | `lnl/target/TARGET_STUDY.md` §5 | verified (repo model) |
| cooled-target cap | 20 µA (Li₂O, B), 10 µA (Ti-T) | CAP | ours | **estimate** |

## Facilities

| facility | number | source | confidence |
|---|---|---|---|
| LNGS Bellotti IBF | 3.5 MV Singletron, TV 0.3–3.5 MV, H⁺ 1000 µA (0.5–3.5 MV) / 500 µA (0.3–0.5 MV), 2 lines, operating since 2023 | Frontiers Phys 2023 (10.3389/fphy.2023.1291113); Junker, EuNPC 2025 | search |
| LUNA-MV for ³H(p,e⁺e⁻) | proposed in the X17 community report | EPJC 83 (2023) 230 §2.4.2 | verified (pdf) |
| Felsenkeller | 5 MV Pelletron, internal RF source, "several tens of µA", design 50 µA; 45 m rock; free TA | arXiv:2412.19874; chetec-infra.eu | search |
| LUNA 400 kV | ~1 mA H⁺, ≤ 400 keV | JUNA 2016 slide | search |
| JUNA | 400 keV 10 mA p (2019); 2.1 mA at 270 keV underground (2020) | Yuanzineng kexue jishu 2019; CJPL news | search |
| CASPAR | 1 MV, design 0.1 mA H⁺; withdrawn from SURF for construction | JUNA 2016 slide; status page | search |
| JRC MONNET | 3.5 MV tandem, ≤ 100 µA DC / 10 µA pulsed; p,d on ⁷Li, T, D; EUFRAT calls 2024, 2025 | JRC lab pages; CERIC-ERIC | search |
| PTB PIAF | Tandetron p,d ≤ 4 MeV "similar currents" to CV28 (≤ 80 µA); 3.75 MV VdG; Ti-T, D, ⁷Li targets | ChETEC facility directory; PTB 6.42 | search |
| NPL | 3.5 MV VdG retired; new 2 MV Tandetron, p,d 0.2–4 MeV, DC ≥ 300 µA (tender) | find-tender 005794-2023; STFC indico 1939 (2026) | search |
| AMANDE | 2 MV Tandetron p,d 0.1–4 MeV DC/pulsed; Sc, Li, D, T targets, wobbling | arXiv:1203.2443; Lebreton 2011 | search |
| TUNL LENA | 2 MV Singletron, "DC beams of mA intensity" or 2 ns pulses; ECR ≤ 230 kV, 2–3 mA | arXiv:2211.10327; LENA II abstract 2025 | search |
| Notre Dame 5U | 5 MV single-ended Pelletron, ECR in terminal, "high intensities" | isnap.nd.edu | search; current (ask) |
| Bochum | 500 kV: 100–150 µA p at 318 keV; 4 MV Dynamitron tandem | arXiv:0804.1934 | search |
| HZDR IBC | 3 and 6 MV Tandetrons 24 h/day, 2 MV VdG; free proposals | hzdr.de | search |
| iThemba LABS | 3 MV Tandetron, 200 eµA p, 25 eµA He at 3 MV; astrophysics line (2023) | SAIP 2023 | search |
| ATOMKI | Tandetron 0.2–4 MeV, 200 µA p at 2 MV; VdG-5 0.6–5 MeV | ATOMKI X17 talk (Krasznahorkay) | search |
| PSI MEG II CW | ≤ 1.1 MeV, 1–100 µA; 50 µA at 1.1, 100 µA at 1.05 MeV tested | EPJC 83 230 §2.2.3 | verified (pdf) |
| MEG II result | R(18.1) < 1.2e-5, R(17.6) < 1.8e-6; Feb 2023, 4 weeks | EPJC 85 763; arXiv:2411.07994 | search |
| Hanoi | 5SDH-2 1.7 MV, p 0.35–3.4 MeV | arXiv:2401.11676 | search |
| Montréal | p 0.4–1.0 MeV, 2 µA (10 possible), 2 keV | arXiv:2211.11900 | search |
| IEAP CTU | HV2500 VdG, 2.5 MeV p; X17 spectrometer | arXiv:2606.18821; EPJC 83 230 | search |
| Melbourne | 5 MV Pelletron, "comfortably 2 µA"; TPC proposal | arXiv:2302.13281 | verified (pdf) |
| Gustavino 2026 | Aipac8Be on AN2000 (0.2–2 MeV, ~1 µA); MX17 demonstrator tested at ATOMKI | indico.atomki.hu event 2 | verified (pdf) |
| Ohio | 4.5 MV tandem, 10 µA typical max; T targets | arXiv:1707.04255 | search |
| Kentucky | 7 MV CN, several µA bunched | pa.uky.edu | search |
| PKU | 4.5 MV VdG, p 0.7–3.5 MeV ≤ 10 µA | 2015 irradiation paper | search |
| Tokyo Tech | 3.2 MV Pelletron, ~5 µA DC | EXFOR 22272 | search |
| Cologne | FN tandem ≤ ~800 nA p | chetec-infra.eu | search |
| Birmingham | 2.6 MeV, 30 mA nominal | Neutron Therapeutics, Dec 2023 | search |
| Nagoya NUANS | 2.8 MeV, 15 mA Dynamitron | AESJ 2017 | search |
| BINP VITA | 0.3–2.3 MeV, nA–10 mA DC | BINP PHPL 2025; PTE 2024 | search |
| BNCT projects | 33 accelerator BNCT projects (mid-2026) | isnct.net table | search |
| census | 267 electrostatic machines | IAEA Accelerator Knowledge Portal, "Accelerators Public List" (REST, 2026-10-22) | verified (data) |

Every other current in `proton_catalogue.py` marked "class default" is an **estimate**.
