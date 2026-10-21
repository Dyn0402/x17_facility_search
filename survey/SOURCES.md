# Sources ledger for the world survey

Written 2026-10-20; every web source was accessed on that date. This is the bookkeeping behind
`SURVEY.md`, `catalogue.py` and the model inputs in `survey_*.py`. For each fact it gives:
- the value;
- where it enters the survey;
- the source (URL, and local copy in `refs/` when kept), with the quote or table location;
- the confidence, and what is still open.

**Confidence codes**
- **V** (verified): read in the source itself (the page, or the PDF in `refs/`) this session.
- **S** (search summary): from a web-search result snippet/summary, not opened in full. The number is as
  the snippet gave it; re-check before publishing.
- **L** (literature knowledge): from general knowledge, not looked up this session. Marked "(lit.)" in
  `catalogue.py`.
- **E** (estimate): our own assumption or stand-in; marked "(est.)".
- **R** (repo): taken from an earlier study in this repo.

**Local copies (`refs/`, 8.9 MB).** Large PDFs were not kept; their quotes are below, so they can be
refetched by URL.

| file | what it is |
|---|---|
| `arxiv_2101.06567_backn.pdf` | Tang et al., "Back-n white neutron source at CSNS and its applications" (NST 2021): Table 1 collimators/fluxes |
| `IHEP2024_BackN_status_p2_p5.pdf` | pp. 2 and 5 of the IHEP 2024 Back-n status talk: beamline table; per-decade flux at ES#1 |
| `arxiv_1811.11692.pdf` | Soldner et al., "ANNI – a pulsed cold neutron beam facility for particle physics at the ESS" (EPJ WoC 219, 2019) |
| `arxiv_2403.09759.pdf` | sTED for (n,γ) at n_TOF EAR2 (2024): EAR1/EAR2 neutrons per pulse |
| `arxiv_1712.06351.pdf` | J-PARC BL05 NOP fundamental-physics activities (2017) |
| `arxiv_1311.3325.pdf` | LiLiT liquid-lithium target, near-threshold ⁷Li(p,n) (2013) |
| `arxiv_1403.5670.pdf` | Reifarth et al., "Neutron reactions in astrophysics" (2014): FRANZ design currents |
| `LeeZhou1999_thickLi.pdf` | Lee & Zhou, thick-target ⁷Li(p,n) yields near threshold, NIM B 152 (1999) 1 |
| `Wagner2007_MEDAPP.pdf` | Wagner et al., MEDAPP therapy beam, J. Nucl. Phys. At. Energy (Kyiv) 2007 3(21) 30 |
| `BayernLandtag_2026-03_FRM2.pdf` | Bavarian parliament Drucksache 19/11406 (23 Mar 2026), question 29: FRM II central channel |

---

## 1. Physics inputs (both models)

| fact | value | used in | source | conf. |
|---|---|---|---|---|
| ³He σ(n,γ), σ(n,p), σ_el vs E | ENDF/B, e.g. σ_nγ 55 µb (thermal), 2.5 µb (1 keV), 12 µb (30 keV), 74 µb (1 MeV), 93 µb (2.5 MeV); σ_np 5316 b (thermal), 25.5 b (1 keV), 0.84 b (1 MeV) | `survey_yield.py` | `~/CLionProjects/MX17_Full_Geant/data/He3.h5` via `ganil_nfs/nfs_fold.py::sigma` | V (file) |
| IPC pairs per photon α | E1: 4.63×10⁻³ (W = 20.6) … 5.5×10⁻³ (36 MeV); M1: 3.66×10⁻³ at 20.58 | `survey_yield.alpha` | nTof_x17 `sept26_prelim_analysis/ipc_born.py` (Born) | R |
| pairs per absorbed thermal n | 4.8×10⁻¹¹ (M1 + E0); our E1-α curve gives 4.78×10⁻¹¹ | §2 check | `CLAUDE.md`, ILL study | R |
| X17 edge θ_min(E_n) | 109° (thermal) … 99° (2.75 MeV) … 66° (14 MeV) | window definition | `docs/anchor_kinematics.py`, `nfs_fold.theta_min_deg` | R |
| ATOMKI ⁴He X17/IPC | 1.5×10⁻³ (PRC 104 044003) | fast reference line | `ganil_nfs/sim/nfs_reach.py` RHO_REF | R |
| ATOMKI ⁸Be level in ILL units | 1.64×10⁻³ | thermal reference | `ill/FEASIBILITY_SIM.md` §12 | R |

## 2. The two Geant4 anchors

| anchor | value | file | conf. |
|---|---|---|---|
| ILL reach vs absorbed rate, per class (X17, M1, E0, ACC, COS, WALL, live, occ) | He tube + mylar window, panel, E_sum > 14, n_TOF 5 ns + veto. As-is optimum 5.3×10⁻³ at 6.2×10¹⁰ n/s; MM occ ÷10 + 10 µs DAQ: 3.4×10⁻³ at 1.2×10¹¹ | `ill/sim/analysis_v3/cons/walls_tubeMy_e14.csv` | R |
| PF1B deliverable absorbed rate | 7.5×10¹⁰ (Ø4 cm) / 1.2×10¹¹ (Ø5 cm) | `ill/out/beam_spot.csv`, ILL §13.4 | R |
| NFS event lists (X17, E1 IPC, beam, accidentals, cosmics per E_n bin) | big plastics: 3.3×10⁻³ all E\*, 0.031 at E_n ≤ 2.75 MeV (14 d) | `ganil_nfs/sim/nfs_reach.py --beam-fact`; tables `ganil_nfs/sim/sel*` from EOS `…/x17/nfs/{sel,sel_beam}` | R |
| NFS singles per neutron vs E_n | N4 forced run (`N4_beam_force[_bigP]_sel.npz`): 54 % prompt (< 50 ns), 46 % delayed (ms–s); 4×10⁻⁵ per neutron averaged over the NFS spectrum; 1–8×10⁻⁷ below 4 MeV (few MC events; 0 in 0.75–1.5 MeV) | `survey_fast.py::nfs_model` | R; the soft-neutron values are statistics-poor |
| NFS spectrum through the cell | 3.5×10⁸ n/s (0.1–45 MeV), 50 µA, Ω = 2.82×10⁻⁵ sr | `ganil_nfs/out/fold_table.csv` | R |
| n_TOF EAR2 measured pair rate | ~700–900 IPC/day with the capsule (0.037 IPC/pulse × 1.93×10⁴ pulses/day; plan §5.3 quotes 900 in 0.2–2 MeV) | nTof_x17 `MX17_Simulation/MX17_Simulator.py`; `docs/PLAN_GANIL_NFS.md` §5.3 | R |
| LNL cosmics tables | `L4_cosmic[_bigP]_sel.npz` | EOS `…/x17/lnl/sel_v3/`, copied into `ganil_nfs/sim/sel/` | R |

## 3. Cold and thermal facilities

### ILL (Grenoble)
- **PF1B capture flux: 2.2×10¹⁰ n/cm²/s at the guide exit, 6 × 20 cm².** Petoukhov et al. 2023, cited in
  the PF1B McStas paper: <https://pmc.ncbi.nlm.nih.gov/articles/PMC13060404/>. ILL's own page says
  2×10¹⁰ (`ill/FACILITY.md`). Conf. S + R.
- **ILL operations extended to 2033.** UKRI (`ill/FACILITY.md` sources). Conf. R.
- **FIPPS: 1.8×10⁸ n/s into the capsule.** `ill/FACILITY.md`. Conf. R.

### FRM II / MLZ (Garching)
- **No power operation since 16 March 2020.** IGORR 2025, Pichlmaier "status and outlook":
  <https://igorr.com/_media/proceedings:2025_igorr22:s06-01-pichlmaier-status_and_outlook.pdf>. Conf. S.
- **Restart still open (23 Mar 2026).** The new central channel had not been delivered by the external
  firms. TUM will give a restart date only after it is installed and accepted. The question notes that its
  production was announced in December 2025. Source: Bavarian parliament Drucksache 19/11406, question 29,
  `refs/BayernLandtag_2026-03_FRM2.pdf`. Conf. **V**.
- **Delay history.** Restart originally aimed for August 2024. The original French maker could not do some
  steps; an Austrian firm was supervised by it; the weld heat treatment was open. Sources:
  <https://mlz-garching.de/englisch/news-und-press/news-articles/first-phase-of-central-channel-completed-project-still-delayed.html>,
  <https://www.frm2.tum.de/frm2/news-single-view/article/neutronen-aus-garching-wieder-ab-sommer-2024>.
  Conf. S.
- **MEPHISTO is expected to perform like PF1B.** ANNI paper, `refs/arxiv_1811.11692.pdf`. Conf. V (statement).

### ESS (Lund)
- **ANNI capture flux.** Simulated 2.5×10¹⁰ n/cm²/s over the full spectrum and 2.0×10¹⁰ for 2–8 Å, at
  5 MW, "comparable to the capture flux density at the guide exit of PF1B". Source:
  `refs/arxiv_1811.11692.pdf` (§ on beam performance). Conf. V.
- **ANNI is not built.** The E5 port is shared with HIBEAM; ESS asked in Dec 2022 for a redesign of the E5
  ANNI beamline for HIBEAM: <https://indico.phy.ornl.gov/event/233/contributions/1237/attachments/962/2598/YK_ESS_news.pdf>.
  Conf. S.
- **ESS schedule.** Beam on target planned for 27 January 2027 (driven by MRP2 delivery, 15 Oct 2026); user
  programme from the beginning of 2028 with 7–10 instruments. Source: ESS STAP introduction, April 2026:
  <https://indico.ess.eu/event/4007/contributions/24588/attachments/17817/35512/intro-STAPs-apr-2026.pdf>
  (behind a login; not saved). Conf. S.

### NIST NCNR
- **NG-C.** An 11 × 11 cm ballistic supermirror guide with a measured capture flux of 8.1×10⁹ cm⁻²s⁻¹;
  6.7×10⁹ in the aCORN decay region (3.1 cm beam). This is before the 2023 cold-source upgrade, which NIST
  says made NG-C "comparable to best in the world". Source: aCORN, <https://arxiv.org/pdf/2012.14379>
  (§ "NG-C"; PDF not kept, 6 MB). Conf. **V** (text). Open: the post-upgrade NG-C capture flux.
- **Restart.** The reactor restarted in 2026 (Physics Today, Sep 2026, says August; NIST's page says May),
  is ramping to 20 MW, and takes users from late November 2026. FY2027 budget pressure.
  <https://physicstoday.aip.org/news/nist-neutron-source-restarts-after-prolonged-closure>. Conf. S.

### ORNL SNS FnPB (BL13)
- **~10⁹ n/cm²/s (polarised), 10 × 12 cm².** Source: ORNL BL13 flyer (2024),
  <https://neutrons.ornl.gov/sites/default/files/24-G00726-Physics%20Division%20BL13%20Flyer-8.5x11-pcg-02-21-24.pdf>.
  Also 1.92×10⁸ n/cm²/s/MW/Å at 8.9 Å. Conf. S. Open: the unpolarised capture flux.

### Others in the cold/thermal class
- **J-PARC NOP (BL05).** Views the coupled moderator; three branches; no flux number found. Source:
  `refs/arxiv_1712.06351.pdf`. Conf. V (no number). Listed below FnPB: L.
- **CARR (Beijing).** Cold-guide exit > 10⁹ n/cm²/s (2003 design simulation); operation overview at
  IGORR 2025:
  <https://igorr.com/_media/proceedings:2025_igorr22:s01-03-zhou-overview_of_carr_operation_and_applications.pdf>,
  <https://yznkxjs.xml-journal.net/en/article/doi/10.7538/yzk.2003.37.04.0361>. Conf. S.
- **PIK (Gatchina).** At power since February 2021. Design: 100 MW, 5×10¹⁵ n/cm²/s in the central trap,
  up to 50 stations. Source: <https://world-nuclear-news.org/articles/russian-pik-research-reactor-upgraded>,
  Voronin 2020 slides <https://indico.desy.de/event/13420/sessions/1300/attachments/8747/10307/Voronin_PIK.pdf>.
  Conf. S.
  - "Not accessible": CERN ended its cooperation agreements with Russia and JINR in 2024. Conf. L.
- **KUR (Kyoto).** Stopped in May 2026: spent fuel, ageing, cost. A 10 MW successor is planned at the Monju
  site. Source: <https://www.rri.kyoto-u.ac.jp/en/outline/preface>; KEK talk Nov 2024
  <https://conference-indico.kek.jp/event/301/contributions/6152/>. Conf. S. The shutdown itself was not
  confirmed after the fact.
- **No flux looked up: listed as ≤ PF1B, conf. L.** HFIR, PSI SINQ, CMRR, OPAL, HANARO, JRR-3, LANSCE
  Lujan, ISIS, MURR, Budapest BRR, LVR-15, TRIGAs, RA-10, and the closed reactors (BER II, Orphée, JEEP II,
  FiR-1, ORELA, LENS). The elimination does not depend on their exact numbers: PF1B is already past the
  walls. **For a paper, add a cited capture flux for each.**

### Epithermal (BNCT)
- **Design floor Φ_epi ≥ 10⁹ n/cm²/s at the port.** IAEA-TECDOC-1223 (via search). Facility list: reactor
  BNCT review <https://tro.amegroups.org/article/view/4646/html>.
  - MIT: 2×10⁸ quoted for an older beam; BMRR: 1.8×10⁹.
  - Conf. S. The 5×10⁹ "best case" is E.
- **Accelerator BNCT.**
  - Over 25 facilities in 13 countries; most choose Li.
  - nuBeam 2.8 MeV solid Li; Tsukuba 8 MeV Be linac.
  - Sources: Kyoto 2024, NIM A 170126:
    <https://repository.kulib.kyoto-u.ac.jp/dspace/bitstream/2433/291657/1/j.nima.2024.170126.pdf>;
    DawonMedax 10 MeV, 2 mA linac, Φ_epi > 10⁹ (AAPPS Bulletin 2022):
    <https://doaj.org/article/7c9fee6dd61b495f8d05f0e01390ec52>. Conf. S.

## 4. Fast white (pulsed) sources

### CERN n_TOF
- **Neutrons per nominal pulse (7×10¹² p).** ~8×10⁵ (EAR1) and ~4×10⁷ (EAR2), from
  `refs/arxiv_2403.09759.pdf`. Other quotes: 2×10⁵ / 5×10⁶ n/cm²/pulse (arXiv:1905.00491) and
  10⁵ / 10⁷ (IAEA nBHEAM slides). The model uses 10⁷ (EAR2) and 8×10⁵ (EAR1) n/cm²/pulse on Ø5 cm, with
  an isolethargic spectrum (E). Conf. V/S.
  - Open: which of "per pulse" and "per cm² per pulse" each quote means. Use the EPJ A 2025 EAR2
    commissioning paper (<https://eprints.whiterose.ac.uk/id/eprint/237140>) for the post-LS2 flux.
- **NEAR station.** 3 m from the target; flux by multi-foil activation and SAND-II unfolding. Source:
  <https://hnps2022.physics.uoi.gr/wp-content/uploads/2022/09/HNPS2022_FRANTZISNeutron-Flux-Determination-for-NEAR-Station-at-the-CERN-n_TOF-Facility-Using-the-SAND-II-Unfolding-Code.pdf>.
  Conf. S.
- **Repetition.** 1.93×10⁴ pulses/day (0.22 Hz average), from the nTof_x17 fast MC. Conf. R.

### CSNS Back-n (Dongguan)
- **Flux and spot (100 kW).** Table 1 of `refs/arxiv_2101.06567_backn.pdf`:

  | config | ES#1 (55 m) | ES#2 (76 m) |
  |---|---|---|
  | Φ50 large spot | Φ50 mm, 1.8×10⁷ n/cm²/s | Φ60 mm, 6.9×10⁶ |
  | small spot | Φ20, 1.6×10⁶ | Φ30, 6.1×10⁵ |

  Also: 25 Hz, double bunch 410 ns apart (single-bunch mode exists), spectrum 0.5 eV–200 MeV peaked at
  ~1 MeV, ~45 % above 1 MeV, and an 8×10⁷ n/cm²/s parasitic irradiation position upstream of the shutter.
  Conf. **V**.
- **Measured per-decade flux at ES#1, 100 kW, small collimators.** From NIM A 1060 (2024) 169045, slide 5
  of `refs/IHEP2024_BackN_status_p2_p5.pdf`:

  | band | n/cm²/s |
  |---|---|
  | 0.1–1 eV | 4.08×10³ |
  | 1–10 eV | 1.79×10⁴ |
  | 10–100 eV | 3.01×10⁴ |
  | 0.1–1 keV | 5.01×10⁴ |
  | 1–10 keV | 1.23×10⁵ |
  | 10–100 keV | 4.30×10⁵ |
  | 0.1–1 MeV | 2.98×10⁶ |
  | 1–10 MeV | 2.77×10⁶ |
  | 10–200 MeV | 6.21×10⁵ |
  | **total** | **7.03×10⁶** |

  Used as the spectrum shape (`survey_yield.BACKN`) and applied to the Φ50 mm flux. Conf. **V**.
  Open: the shape for the large spot.
- **ND2019.** ES#1 integral 0.1 eV–30 MeV = 1.55×10⁷ n/cm²/s at 100 kW:
  <https://www.epj-conferences.org/10.1051/epjconf/202023917018>. Conf. S.
- **Power.** 185 kW held stably from 4 March 2026 (160 and 170 kW in 2024); CSNS-II to 500 kW, upgrade
  launched 2024, no completion date. Source: <https://english.ihep.ac.cn/nw/han/y26/202603/t20260317_1152755.html>.
  Conf. S.

### LANSCE WNR (Los Alamos)
- **Flight-path naming and spectra.** 4FP15R etc.; forward paths are hardest; 60R at ~19 m.
  <https://lansce.lanl.gov/facilities/wnr/flight-paths/index.php>. Conf. S.
- **ICE House (±30°): ≈ 5×10⁶ n/cm²/s above 1 MeV.**
  <https://lansce.lanl.gov/facilities/Radiation%20Effects/index.php>. Conf. S.
- **Pulse structure.** ~1.5 µA, micropulses 1.8 µs apart, ~14 000 micropulses/s (the page's "1.8 sec" is
  read as µs). The model uses 1.8 µs micropulses inside a 2.5 % macropulse duty. Conf. S + E.
- **Estimates (E):** the spectrum split (15 % 0.1–1 MeV, 35 % 1–10, 50 % > 10 MeV), the 50 cm² beam and
  the 20 m flight path. **This is the input to check before WNR can move up or down** (SURVEY §6.2).
- **Dedicated study, 2026-10-21 (`lansce_wnr/FACILITY.md`):**
  - Nowicki, Wender & Mocko, Physics Procedia 90 (2017) 374, LA-UR-17-20620: bare W target 7.5 cm × Ø3 cm;
    Fig. 2 per-proton yield at 15/30/60/90° (digitised, ±20 %); ICE House 1.5×10⁶ and ICE-II 4.7×10⁶ n/cm²/s
    above 1.5 MeV, beam Ø 2.5–8 / 2.5–6.4 cm. Local copy `lansce_wnr/refs/`. Conf. V.
  - LANL ToF page: 625 µs macropulses at 40 Hz, 7×10⁸ p per micropulse, 1.8 µs spacing (3.6/7.2 µs on
    request), 13 889 micropulses/s ≈ 1.5 µA. Conf. V. WNR page: six flight paths, 90L at 7–15 m (softest),
    ×2.5 upgrade to ~5 µA. Conf. V. 2026 call: 90L beam time "very limited". Conf. S.
  - **Corrections:** the 5×10⁶ above 1 MeV above is ICE-II, not ICE House; the estimated split is replaced by
    the Fig. 2 yields; the survey's live time averages triggers over the second (optimistic for WNR).

### JRC GELINA (Geel)
- **Source and flight paths.** 1.6×10¹²–2.5×10¹³ n/s; 10 flight paths, 10–400 m; 800 Hz. Source:
  <https://publications.jrc.ec.europa.eu/repository/handle/JRC36942> (flux per flight path in that paper,
  not read). The model uses an isotropic bound at 10 m (E). Conf. S.

### HZDR nELBE (Dresden)
- **Flux at target ≈ 2.5×10⁴ n/cm²/s; source ~1.6×10¹¹ n/s.** 10 keV–15 MeV; 102/203/406 kHz; 5–11 m.
  Source: HZDR nELBE page <https://www.hzdr.de/db/Cms?pNid=2802>. Older design papers quoted
  1–1.5×10⁷ n/cm²/s at 3.9 m; the official table wins. Conf. S.

### RPI LINAC
- **Up to 10¹³ n/s.** <https://arxiv.org/pdf/1801.03424> (PDF not kept). Conf. S.

## 5. Continuous fast sources

### FRM II MEDAPP / NECTAR fission-converter beam
- **Flux at the irradiation position: ≈ 3.2×10⁸ n/cm²/s.**
  <https://www.frm2.tum.de/en/frm2/the-neutron-source/irradiation-facilities/irradiation-with-fast-neutrons/>.
  Conf. **V** (page fetched). This is the model input.
- **Flux in the beam tube: up to 7×10⁸ n/cm²/s** (depends on filters and collimation). Doses at 2 cm in
  water: 0.54 Gy/min (n), 0.20 Gy/min (γ). Source: `refs/Wagner2007_MEDAPP.pdf`, abstract. Conf. **V**.
- **The converter.** Two uranium-silicide plates (93 % ²³⁵U, 540 g) at the moderator-tank edge, moved in
  when needed; "unique beamline converter facility worldwide"; one paper quotes ≈ 1.5×10⁹ n/cm²/s and a
  20 × 30 cm beam. Source: <https://www.frm2.tum.de/en/frm2/the-neutron-source/neutrons/secondary-sources/converter-facility/>.
  Conf. S.
- **Mean energy 1.8–2.3 MeV; total γ flux at NECTAR ≈ fast-neutron flux.** Sources: NECTAR/GIANT
  (<https://www.nature.com/articles/s41598-023-47237-y>), JLSRF MEDAPP (<https://jlsrf.org/index.php/lsf/article/view/43>).
  Conf. S. The model uses k_γ = 1 (E).
- **Field.** MLC maximum 30 × 20 cm (another page: 27 × 20); new MLC, NIM A 2023,
  doi:10.1016/j.nima.2023.168717. Conf. S.
- **Spectrum: Watt (a = 0.988, b = 2.249).** Conf. E (standard ²³⁵U thermal fission).

### Birmingham HF-ADNeF
- **UCANS11 abstract (Feb 2025).** High-power electrostatic accelerator, 2.6 MeV, > 30 mA, rotating Li
  target, > 3×10¹³ n/s. Construction from March 2020, first neutrons December 2023. Research areas:
  materials damage, medical physics/radiobiology, nuclear physics. Source:
  <https://indico.triumf.ca/event/575/contributions/6394/>. Conf. **V** (page fetched).
- **STFC talk (Sep 2026).** "User facility"; ~10¹¹ n/s/cm²; neutrons up to 0.9 MeV, broad thick-target
  spectrum. A planned deuteron beam would raise E_n to ≈ 18 MeV. Source:
  <https://indico.stfc.ac.uk/event/1939/contributions/11131/>. Conf. **V** (page fetched).
- **Estimates (E):**
  - 0° yield = 2 × the 4π average (4.8×10¹² n/sr/s);
  - a flat 0.05–0.85 MeV spectrum;
  - the cell at 1 m (unshielded bound) or 2 m (shielded);
  - k_γ = 0.3.
- **Supporting numbers.** Thick-Li yield ~9×10⁸ n/s/µA at 2.5 MeV, mean/max E_n 326/787 keV:
  `refs/LeeZhou1999_thickLi.pdf` (via `demokritos/neutron/NEUTRON_BEAM.md`). The ⁸Be γ per proton
  (~1×10⁻⁷ at 2.5 MeV) is from the LNL cross sections (`demokritos/neutron/NEUTRON_BEAM.md` §5). Conf. R.
- **Open:** an unmoderated collimated port, the 0° spectrum, beam time.

### SARAF (Soreq)
- **Phase II and LiLiT.**
  - Phase II: 40 MeV / 5 mA CW p/d SC linac; GaIn jet > 10¹⁵ n/s.
  - LiLiT (Phase I): ~3×10¹⁰ n/s total, ~2×10¹⁰ n/s/mA, 5×10¹⁰ epithermal n/s; quasi-Maxwellian ~30 keV.
  - Source: <https://arxiv.org/pdf/1801.06493> (§ LiLiT; PDF not kept); `refs/arxiv_1311.3325.pdf`.
    Conf. **V**.
- **July 2024 status.** MEBT commissioned with p and d; CM1 being integrated; first beam expected end of
  2024; "recent events in Israel complicate significantly the commissioning". Source:
  <https://inspirehep.net/files/a4ad488a9e20fee312e86513d3771f9b>. Conf. S. No 2025–26 status found.
- **Estimates (E):** the LiLiT 0° yield, 10¹⁰ n/sr/s.

### FRANZ (Frankfurt)
- **Status.** The 700 keV RFQ was commissioned with a 10 mA beam; the IH cavity was conditioned to 10 kW.
  Source: IPAC 2025 TUPS039, <https://indico.jacow.org/event/81/contributions/7842/>. Conf. S.
- **Design.** Nominal ≤ 20 mA DC (`refs/arxiv_1403.5670.pdf`); older talks quote 3–30 mA CW. Conf. V/S.
- **Estimates (E):** 7×10¹⁰ n/s and the 0.5 m distance.
- **Dedicated study, 2026-10-21 (`franz/FACILITY.md`):** IPAC 2025 TUPS039 (licence < 5 % duty, 10¹² n/s;
  2 MeV planned end 2025, not reported since), LINAC 2024 TUPB021 (CHORDIS 0.5–1 ms at 10 Hz; 11 mA
  macropulse), IPAC 2023 TUPM128, IPAC 2015 TUXB1 (1.912 MeV → 25 keV Maxwellian in a 120° cone),
  arXiv:0909.5279 (layout), arXiv:1403.5670 §5.1 (≤ 20 mA DC, 10¹² n/s). Conf. V. Estimates (E): S(Li),
  σ_DC(⁷Li(p,γ)) ≈ 10 µb, borated-PE and Pb attenuation at keV, 478 keV yield scaling.

### LENOS (LNL)
- **Design.** 5 MeV, 50 mA RFQ; high-power target tested. Sources: Physics Procedia 26 (2012) 261,
  <https://produccioncientifica.ugr.es/documentos/63b9970a4386723d2da37e3d>; NEPHIR (35–70 MeV, 750 µA
  cyclotron), Mastinu abstract <https://elamatscience.ifj.edu.pl/abstracts/Mastinu_abs.pdf>. Conf. S.
  No status after 2017.

### Generators
- **D-D.** Phoenix measured 3×10¹¹ DD n/s with a gas target (goal 5×10¹¹); DT systems 5×10¹³ n/s each.
  Source: Phoenix RADEL slides <https://trinity.ans.org/file/1445/radel-150616.pdf> (PDF not kept; quotes
  from its text). Conf. **V**.
- **D-T record.** SHINE/Phoenix steady-state 4.6×10¹³ n/s:
  <https://physicsworld.com/a/record-breaking-fusion-reaction-could-transform-medical-isotope-production/>.
  Conf. S.
- **D(d,γ)⁴He.** Suppressed > 10⁷ against D(d,n): EPJ A 2006 via search; PRC 47, 29 (1993) measured the
  ratio at 100 keV (exponent cut in the snippet): <https://link.aps.org/doi/10.1103/PhysRevC.47.29>; σ at
  300 keV ≈ 2.5–4.4×10⁻³⁷ m² (AEST 2016,
  <https://yznkxjs.xml-journal.net/article/doi/10.7538/yzk.2016.50.03.0395>). The model uses ~10⁻⁷ per n.
  Conf. S.
- **Estimates (E):** the 1 m and 2.5 m distances, 50 cm².

### Cyclotron ⁹Be(p,n)
- **No thick-target yield table found.** METU thesis: 30 MeV, 150 µA → up to 3×10¹⁰ n/cm²/s at the outer
  surface of the target station (<https://open.metu.edu.tr/handle/11511/115507>). Conf. S.
- **Estimates (E):** 10¹³ n/sr/s at 1 mA and the spectrum split. **This is the open input.**
- **Resolved 2026-10-21 (`bepn_cyclotron/FACILITY.md`):** ENDF/B-VIII.0 p+⁹Be (LA150, Young & Arthur,
  LA-11753-MS; GNDS on CVMFS) with thick-target slowing-down, checked to 1 % against Fenyvesi
  arXiv:1504.07399 (9.07×10¹⁵ n/sr/C at 0°, 16 MeV, E_n > 0.4 MeV; Brede NIM A 274 (1989) 332) and Sumitomo/KURRI
  Cyclotrons 2010 FRM2CCO04 (1.9×10¹⁴ n/s at 30 MeV, 1 mA). Conf. V/S. The model gives 4×10¹³ n/sr/s at 0°
  at 30 MeV, 1 mA (×4 the guess, harder).
  - NPI Řež: Štursa 2017 (TR-24 18–24 MeV / 300 µA, Be converter 7.2 kW; U-120M H⁻ 6–37 MeV, collimated
    beam), Ansorge 2019 (TR-24 converter "not operational yet"), UCANS-8 EPJ WoC 231 (2020) 03005, Majerle
    NIM A 1053 (2023). KURNS AESJ 2026 3F08 (C-BENS for fundamental research). Conf. V/S.

## 6. Out of window / no beam

| facility | fact | source | conf. |
|---|---|---|---|
| NCBJ MARIA | Thermal-to-14 MeV converter (⁶Li + d), "sole device of its kind"; in-reactor | <https://www.ncbj.gov.pl/en/aktualnosci/ncbj-thermal-14-mev-neutron-converter-sole-device-its-kind-operated-world> | S |
| IFMIF-DONES | 40 MeV d, 125 mA, Li, 5 MW; construction approved 2023; test cell, no extracted beam | <https://ifmif-dones.es/> | S (first beam not found) |
| TSL, iThemba, RCNP, ChipIR | quasi-mono 20–400 MeV / atmospheric spectra | — | L |
| LICORNE | inverse-kinematics ⁷Li beam on H₂, 0.5–4 MeV forward cone | — | L (flux ~10⁶–10⁷ n/s/sr not looked up) |
| Mono-energetic labs (PTB PIAF, NPL, JRC MONNET, TUNL, Ohio, CIAE, PKU, Tohoku, Kyushu, AIST) | µA-class | — | L; eliminated by the Demokritos result (`demokritos/neutron/NEUTRON_BEAM.md`) |

## 7. What to look up first to turn this into a paper

1. A cited capture flux for every cold/thermal guide listed as "(lit.)".
2. LANSCE WNR: a measured spectrum below 1 MeV and the beam size at ICE.
3. n_TOF EAR2: the post-LS2 flux per cm² per pulse (EPJ A 2025).
4. MEDAPP: the spectrum and γ field at the beam exit; the restart date.
5. Birmingham: the 0° spectrum and yield; a port geometry.
6. ⁹Be(p,n) at 18–30 MeV: a thick-target yield table.
7. Soft-neutron singles: our own Geant4 run (SURVEY §6.3). This is not a literature item, but it moves
   more verdicts than any of the above.
