# Accelerator BNCT machines as X17 sources — facility record (2026-11-09)

Which accelerator BNCT installations exist, what runs in 2026, and which of them could host the MX17 arms around a ³He cell. Status
was checked by web search on 2026-11-09; every "(ask)" could not be found publicly. The list of projects below is ISNCT's, reproduced in
Tanaka's BIPM webinar of January 2025, and is partly dated (a 2021 list). The reach is in `FEASIBILITY.md`.

## 1. Why this class needed a separate look

The survey (`survey/SURVEY.md`) rated accelerator BNCT MARGINAL with an ILL-scaled number (2.5×10⁻³ at 10⁹ n/cm²/s) and said "the
unmoderated source behind the moderator is the real prize". Two claims to test: (a) what the moderated port does with its real spectrum
and contamination, and (b) whether any machine actually lets us reach the unmoderated source.

**Hardware fact that decides (b):** in a treatment machine the target sits inside the beam-shaping assembly (BSA: moderator, reflector,
Pb, delimiter, on-line monitors). There is no "research port" on the unmoderated side; to use the bare target the BSA has to come off.

## 2. The machines

| machine | where | accelerator, beam | target | status 2026 | research time? | can we reach a bare target? |
|---|---|---|---|---|---|---|
| **nuBeam** (Neutron Therapeutics) | Helsinki University Hospital (HUS), FI | electrostatic, 2.6 MeV, 30 mA "reliable operation" (vendor) | rotating solid Li | **clinical**: first patients May 2025, 10-patient H&N study, CE mark pending | none known; a hospital **(ask)** | no: target in the BSA, monitors embedded in the delimiter |
| nuBeam | Shonan Kamakura, JP | same | same | "commissioning" on the 2021 list; no newer report **(ask)** | no | no |
| **Birmingham HF-ADNeF** (same vendor family) | Birmingham, UK | electrostatic, 2.6–2.8 MeV, > 30 mA | rotating solid Li | **operating**, research (reference study) | yes | **yes**: this is the reference, see `birmingham/` |
| **NeuCure** (Sumitomo) | Southern Tohoku (Koriyama), Kansai BNCT (Osaka), Boao under construction | cyclotron, 30 MeV, 1 mA | 5.5 mm Be | **clinical, insured since June 2020**; > 463 patients at Southern Tohoku by Feb 2026 (promotional source) | none known **(ask)** | no: covered by `bepn_cyclotron/` as a bare-Be case only |
| **CICS-1 / CICS-2** | NCC Tokyo; Edogawa Hospital, JP | RFQ, 2.5 MeV, 12 or 20 mA (sources disagree) | Li | clinical trials (NCC phase II angiosarcoma from Nov 2022; Edogawa Jul 2023–Mar 2024) | none known | no |
| **NUANS** | Nagoya University, JP | Dynamitron, 2.8 MeV, rated 15 mA; 2.8 MeV × 11 mA reached Jan 2016 | sealed Li (2 mm Li under Ti foil, on Ta) | listed "experimental use" (research machine); no 2026 report found **(ask)** | **possible: a university machine (ask)** | unknown: BSA fitted **(ask)** |
| **iBNCT** | Tsukuba / Ibaraki, JP | linac RFQ+DTL, 8 MeV, 2.1 mA avg (2022; goal ≥ 5 mA) | Be | "clinical trial" on the list; no 2025 report found **(ask)** | possible **(ask)** | no information |
| **NeuPEX** (Neuboron, TAE accelerator) | Xiamen Humanity Hospital, CN | electrostatic tandem | Li | phase I from Apr 2024, phase II scheduled 2025, approval target late 2025–26 (company PR) | no | no |
| **Alphabeam** (TAE) | **CNAO Pavia, IT**; UW–Madison MoU | electrostatic tandem; energy/current not public **(ask)** | Li | CNAO: definitive agreement Dec 2024, install planned 2025, trials 2026; "soon be installed" later; **no confirmation of installation found** | none known **(ask)**; partners include INFN, UniPV, PoliMi | no |
| **A-BNCT** (DawonMedax) | Gachon Gil, Songdo, KR | RF linac (RFQ+DTL), 10 MeV (one source) | Be? **(ask)** | clinical trials (POSTECH page) | no | no |
| **VITA** (BINP) | Novosibirsk, RU | vacuum-insulated tandem, p up to 2.3 MeV, up to 10 mA (d 1.5 MeV, 1.5 mA) | evaporated Li on 144 mm Cu | **operating, experimental use**; 2022 fast-neutron run, 18 working days, 8 h/day | **has carried external users** (LHC cables and SiPMs, ITER samples) | **yes**: position B in an irradiation room, concentrator of Pb and wood. Plain fact: CERN ended all relations with Russian institutes on 30 Nov 2024 |
| VITAmin (BINP) | Novosibirsk | new compact tandem, ~0.9 MeV d, 10 mA, 3×10¹² n/s | Li | under development | — | — |
| **ANTHEM / ex-MUNES** (INFN) | LNL RFQ, Caserta site, IT | RFQ 5 MeV, 30 mA (150 kW) | Be/Pd/Cu | under construction (LINAC 2024) | INFN project **(ask)**; relevant to our LNL links | not modelled here; first beam date unknown **(ask)** |
| Others on the ISNCT list | LU AB-BNCT (Putian), D-BNCT01/02 (Dongguan, IHEP), X-TANS (Xi'an), CYCIAE-14B, Heron (Taiwan), KIRAMS, NeMeSis (Granada), SARAF-LiLiT (Soreq) | various | Li or Be | D-BNCT01 and LiLiT are listed "experimental use", the others clinical, commissioning or under construction | LiLiT, D-BNCT01 **(ask)** | LiLiT is a bare liquid-Li target; belongs with FRANZ near-threshold sources |

## 3. Beam numbers we use, and how solid they are

- **nuBeam 2.6 MeV / 30 mA**: vendor page; a 2024 Kyoto paper says 2.8 MeV for a nuBeam-developed system. Yield not quoted publicly; taken
  from the Birmingham normalisation (3×10¹³ n/s at 30 mA, 2.6 MeV). Helsinki port flux and spectrum: no published number found **(ask)**.
- **Nagoya**: 1.13×10¹² n/s/mA at 2.8 MeV (PHITS calculation); the Birmingham model gives 1.17×10¹². Goal 1×10⁹ n/cm²/s epithermal.
- **Kansai NeuCure**: Φ_epi up to 1.4×10⁹ n/cm²/s through a Ø12 cm collimator at 1 mA (Kyoto/Kansai papers; design statement).
- **BSA quality**: Tanaka's BIPM webinar (Jan 2025) gives Φ_epi > 5×10⁸, D_f/Φ_epi < 7×10⁻¹³, D_γ/Φ_epi < 2×10⁻¹³ Gy cm². IAEA-TECDOC-1223 recommends
  2×10⁻¹³ each (used as the survey did; not re-fetched). **These are limits, not measurements.**
- **No measured broad-band port spectrum was found for any accelerator machine**: only a C-BENS peak "near 40 keV" (Fujiwara), the iBNCT Bonner-sphere
  statement that measurement agrees with MC, and 10 keV fast/epithermal band definitions. The epithermal + fast shape we use is therefore an ESTIMATE.
- **VITA fast mode**: 1.4×10¹² n/s (d on Li), limited by the deuteron current; thick-target 1.1×10¹¹ n/mC at 2 MeV p on Li (their Fig. 2 and text).

## 4. Space and geometry

- Treatment rooms: the port is a Ø12–20 cm aperture in the wall of the BSA/room face, at couch height, with a patient delimiter. Room dimensions are not public
  **(ask)**. The arms need ±~90 cm in the two transverse directions and the cell window ≥ ~30 cm from anything that would shadow the upstream arms.
- Hospitals run the room for patients; apparatus installed for weeks, a ³He pressure cell in a patient room, and a detector-sized object at the aperture are outside any published
  arrangement.
- Bare-target positions exist at Birmingham and VITA. At VITA position B the room has borated-concrete walls and a borated-PE door; size **(ask)**. First VITA fast run had to stop
  after 10 s because the dose in the control room was too high: 4π shielding is the issue, as at Birmingham.

## 5. Access routes

- **Hospitals (Helsinki, Southern Tohoku, Kansai, NCC, Edogawa, Xiamen, CNAO, Gachon):** no user programme; medical devices in clinical use or trial.
- **University/national labs:** Nagoya, Tsukuba, Kyoto, Dongguan, Soreq: conceivable by collaboration, nothing published **(ask)**.
- **Birmingham:** a user-facility route already studied.
- **BINP:** hosted Western hardware until the war; CERN ended institutional ties 30 Nov 2024, and Western trade sanctions restrict shipping detectors and electronics there.
  We note this as a fact and do not model an access path.
- **CNAO:** interesting only because of INFN/UniPV links; a clinical, not a research installation, with the machine not yet confirmed installed **(ask)**.
- People: the FACILITY records of Birmingham, LNL and NPI hold our existing contacts. No contact at Helsinki, Nagoya, CNAO **(ask)**.

## 6. Unknowns, in order of importance

1. Whether any BSA-equipped research machine can run bare or swap the BSA for a beam tube **(ask Nagoya; CNAO/INFN)**.
2. The measured port spectrum and D_f/Φ of a real Li port (Helsinki, NUANS, CICS) **(ask)**, which sets the moderated reach.
3. Room dimensions and whether apparatus can be installed for weeks at a clinical machine **(ask)**.
4. ³He cell safety in a room built for patients; the hospital's licence does not cover a pressurised gas experiment **(ask)**.
5. Whether NUANS is still operating, and at what current **(ask)**; Alphabeam energy/current **(ask)**.

## 7. Sources

- Neutron Therapeutics nuBeam product page: <https://neutrontherapeutics.com/?p=240>; first-patient release (May 2025): <https://neutrontherapeutics.com/neutron-therapeutics-and-helsinki-university-hospital-treat-first-head-and-neck-cancer-patients-using-accelerator-based-boron-neutron-capture-therapy/>; trial NCT07058116: <https://clinicaltrials.gov/study/NCT07058116>; Helsinki facility and BSA monitors: Acta Oncol. 2021, <https://informahealthcare.com/doi/full/10.1080/0284186X.2021.1979646>.
- Kansai/Kyoto: Kyoto NIMA 2024, <https://repository.kulib.kyoto-u.ac.jp/dspace/bitstream/2433/291657/1/j.nima.2024.170126.pdf> (statement about nuBeam 2.8 MeV and the 1.4e9 Kyoto C-BENS design); CYCLOTRONS 2022 WEBI02, <https://accelconf.web.cern.ch/cyclotrons2022/papers/webi02.pdf> (Kansai characterisation); JNR 2022, <https://repository.kulib.kyoto-u.ac.jp/dspace/bitstream/2433/283976/1/jnr-220037.pdf>.
- Tanaka, BIPM webinar 23 Jan 2025 (project list, BSA parameters): <https://www.bipm.org/documents/20126/267637838/20250123+Webinar+BNCT+-+H+TANAKA/91dcec71-dd2a-d6b0-657e-f5ca5d8c0ed8>; list origin: <https://isnct.net/bnct-boron-neutron-capture-therapy/accelerator-based-bnct-projects-2021/>. Patients: <https://maj.emergency.co.jp/en/?p=3775> (promotional).
- Nagoya: IBIC/PASJ 2016 WEOL16, <https://ibic12.kek.jp/mirror/www.pasj.jp/web_publish/pasj2016/proceedings/PDF/WEOL/WEOL16.pdf>; HPTW Tsuchida: <https://indico.fnal.gov/event/15204/contributions/30238/contribution.pdf>; PHITS yield: <https://www.mdpi.com/2673-4362/3/3/12>.
- Tsukuba: JNR 2022 <https://content.iospress.com/articles/journal-of-neutron-research/jnr220029>, PFR 2018 <https://www.jspf.or.jp/PFR/PDF2018/pfr2018_13-2406006>; review: Kumada, Sakae, Sakurai, EPJ TI 2023, <https://link.springer.com/article/10.1140/epjti/s40485-023-00105-5>.
- Xiamen/NeuPEX: <https://www.businesswire.com/news/home/20240409400741/en/Neuboron-Medical-Group-Advances-Cancer-Treatment-Introducing-Next-Generation-Boron-Neutron-Capture-Therapy>.
- CNAO/TAE: agreement <https://www.businesswire.com/news/home/20241217878109/en/TAE-Life-Sciences-and-CNAO-Announce-Definitive-Agreement-on-BNCT-a-Next-Generation-Cancer-Therapy>; UW-Madison MoU <https://www.businesswire.com/news/home/20250925542671/en>; TAE page <https://tae.com/tae-life-sciences/>.
- Korea: AAPPS Bull. 2022, <https://doi.org/10.1007/s43673-022-00063-2>; POSTECH <https://e-dane.postech.ac.kr/research/research_view.php?wr_id=7>.
- VITA: Kolesnikov et al., EDM 2024, <https://bnct.inp.nsk.su/publics/2024/Generation_of_a_High-Yield_Fast_Neutron_Flux_on_the_Accelerator_Based_Neutron_Source_VITA.pdf>; Kasatov et al., PHPL 22(4) 2025, <https://star.inp.nsk.su/~bnct/publics/2025/PHPL_VITAmin_en.pdf>; NIM B 2026, <https://star.inp.nsk.su/~bnct/publics/2026/NIM_B_2026.pdf>.
- CERN–Russia: <https://international-relations.web.cern.ch/fr/node/66>.
- INFN/ANTHEM: LINAC 2024 TUAA003, <https://accelconf.web.cern.ch/linac2024/pdf/TUAA003.pdf>.
- C-BENS 40 keV spectrum (Fujiwara), BMRR and BSS: search results on BNCT spectrum (Kyoto repository: <https://repository.kulib.kyoto-u.ac.jp/dspace/bitstream/2433/201950/1/j.apradiso.2015.06.020.pdf>).
