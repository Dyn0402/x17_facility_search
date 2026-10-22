# Raw research notes (proton survey, 2026-10-22) — feeds SOURCES.md and catalogue

## Physics inputs
- 12C: ATOMKI PRC 106 L061601 (arXiv:2209.10795): 2 MV Tandetron, 11B 2 mg/cm² on 5 µm Ta, ΔE≈300 keV,
  Ep = 1.5/1.7/1.88/2.1/2.5 MeV, 2 µA, ~50 h each; Bx = 2.7–4.7e-6, avg 3.4(3)e-6, m 16.86(17); Al rods.
- 12C 17.23 MeV 1−: Γ=1150 keV, Γγ0=44 eV, Γp=1 MeV, Γγ1=5 eV (1965Se06 via NNDC 11b_p_g_res.pdf).
  → BW peak σ(γ0) ≈ 28 µb (g=3/8, ƛ=4.22 fm at Ecm 1.272).
- Community report EPJC 83 (2023) 230 (arXiv 2305.?): MEG II CW 1.1 MeV, 1–100 µA; tested 50 µA @1.1, 100 µA @1.05 MeV.
  LNL 2 MV VdG (AN2000) 1 µA; IEAP COPE; LUNA-MV for 3H(p,e+e-) "max 100 µA" (but HVEE spec is 1 mA); UdeM 6 MV tandem 3He beam,
  7Li(3He,γ)10B? line dedicated to X17.
- Montreal (arXiv 2211.11900): UdeM tandem, p 0.4–1.0 MeV, 2 µA (maybe 10 µA), 2 keV resolution; water-cooled 7LiF; MWPC+DAPHNE bars,
  ~4π; Geant4 ~2 weeks at 2 µA. Status Feb 2024 "setting up".
- MEG II result EPJC 85 (2025) 763, arXiv 2411.07994: 2023 run 4 weeks, Ep 0.5–1.08 MeV, LiPON 7 µm; R17.6<1.8e-6, R18.1<1.2e-5.
- IEAP CTU: X17 apparatus at the IEAP Van de Graaff (TPX3 + OFTPC), arXiv 2606.18821; aladdin.utef.cvut.cz/projekty/vdg/x17
- Hanoi VNU: arXiv 2401.11676 (Universe 10 168 2024), 1.7 MV Pelletron (5SDH-2), LiF / Li2O, 1–1.5 µA, punctured targets.

## Machines
- LUNA-MV / Bellotti IBF (LNGS): HVEE 3.5 MV Singletron, TV 0.3–3.5 MV, H+ 1000 µA (0.5–3.5 MV), 500 µA (0.3–0.5 MV); 2 lines;
  operative June 2023, inaugurated Oct 2023; user facility (Frontiers Phys 2023 10.3389/fphy.2023.1291113; Junker EuNPC2025).
- Felsenkeller (HZDR Dresden): 5 MV Pelletron, internal RF source (single-ended H, He) "up to several tens of µA", design 50 µA;
  45 m rock; ChETEC-INFRA TA, beam time free via advisory board. arXiv 2412.19874.
- JUNA (CJPL, China): 400 kV, ECR, p & He+ 400 keV 10 mA demonstrated (2019 paper), 2.1 mA @270 keV first underground (Dec 2020).
  Max 400 keV → below the 441 keV ⁸Be resonance; no ³H(p,γ) ≥0.5 MeV. ACCESS (China, CJPL) + energy.
- LUNA 400 kV (LNGS): ~1 mA H+ (JUNA 2016 slide), max 400 keV → below 441.
- CASPAR (SURF, 1 MV KN): ~150 µA (He?), design 0.1 mA H+, 1 MeV; temporarily withdrawn from SURF (construction).
- Bochum Dynamitron-Tandem-Labor (RUB): 4 MV Dynamitron tandem + 500 kV accelerator (100–150 µA p at 318 keV, 2008).
- TUNL LENA: ECR ≤ 230 kV, 2–3 mA DC (LENA II up to 20 mA expected); 2 MV HVEE Singletron, "DC beams of mA intensity" H, He, or 2 ns pulsed.
  (arXiv 2211.10327; tunl.duke.edu/nuclear-astrophysics/lena-accelerators)
- JRC Geel MONNET: 3.5 MV HVEE electrostatic tandem (single-ended?) DC up to 100 µA on target, 10 µA pulsed (2.5/1.25/0.625 MHz, <2 ns);
  p/d on ⁷Li, T, D targets; EUFRAT open access calls (2024, 2025). CERIC-ERIC listed.
- PTB PIAF (Braunschweig): CV28 cyclotron (p<19 MeV, <80 µA) + 3.75 MV VdG / HVEE Tandetron (p,d to 4 MeV, "similar currents");
  Ti-T, D gas, ⁷Li targets; open-geometry big hall; neutron reference fields.
- IRSN/ASNR AMANDE (Cadarache): 2 MV Tandetron, p/d 100 keV–4 MeV DC or pulsed; Sc, Li, D, T targets on wobbling air-cooled holder;
  Ti-T up to 5.9e8 n/s at 2 MeV (Lebreton 2011).
- NPL Teddington: 3.5 MV VdG retired (2026 abstract, indico.stfc.ac.uk/event/1939/contributions/11135); new 2 MV Tandetron,
  p/d 200 keV–4 MeV, DC ≥ 300 µA (2023 tender find-tender 005794-2023); T(p,n) heritage.
- IAEA Accelerator Knowledge Portal, list "Accelerators Public List" via SharePoint REST (anonymous): 469 rows visible,
  271 electrostatic (200 tandem, 70 single-ended). No currents filled. Entries mostly 2015 vintage. → census iaea_electrostatic.csv.
- ISNCT accelerator-BNCT project table (mid-2026): 33 projects (copied in notes below catalogue): mostly hospitals; research:
  VITA Novosibirsk, NUANS Nagoya (Dynamitron), SARAF-LiLiT, D-BNCT01 Dongguan, HF-ADNeF Birmingham, CPHS Tsinghua, IE-BNCT Hefei,
  ANTHEM LNL (RFQ, dev), ESQ CNEA (constr), KIRAMS (constr), C-BENS Kyoto (cyclotron).
- BINP VITA: vacuum-insulated tandem, p/d 0.3–2.3 MeV adjustable, nA–10 mA DC (PHPL_VITAmin_en 2025; PTE_VITA_2024). Russia → ACCESS.
- ATOMKI: Tandetron 2 MV (2015) 0.2–4 MeV, 200 µA p / 40 µA He at 2 MV (ATOMKI X17 talk); VdG-5 0.6–5.0 MeV (1971).
  New 6-telescope DSSD spectrometer; Acta Phys Pol B 2025 new E-θ pair spectrometer. Hanoi two-arm check arXiv 2401.11676 (with ATOMKI).
- Notre Dame ISNAP: 5U vertical single-ended NEC Pelletron "St. ANA", 5 MV, ECR in terminal, "high intensities" (no µA public; ask).
  Also 10 MV FN tandem.
- IEAP CTU Prague: HVEE HV2500 Van de Graaff, max 2.5 MeV p (single-ended); p 0.5–1.9 MeV used 2024; X17 spectrometer
  (6 TPC+MWPC, TPX3 inner tracker, OFTPC) for 8Be and 4He IPC (job posting). Current not public.
- HZDR IBC: 3 MV and 6 MV Tandetrons 24 h/day; 2 MV VdG 16 h/day; free proposals via HZDR-GATE; fast track.
- Kentucky UKAL: 7 MV CN single-stage VdG, p/d/He up to 7 MeV, pulsed 1.875 MHz ~ several µA avg.
- Ohio Edwards lab: 4.5 MV tandem, Cs sputter, typ. max 10 µA p/d on target; solid and gas T targets for neutrons (arXiv 1707.04255).
- Gustavino (INFN Roma, our collaboration), "The X17 search in Italy", LUNA meeting at ATOMKI Debrecen 28 Jan 2026
  (indico.atomki.hu/event/2/contributions/11): LNL experiment name "Aipac8Be", AN2000 Ep 0.2–2 MeV, I ~1 µA, no result;
  MEG II used 5 µm LiF on 10 µm Cu (LNL) and >2 µm LiPON on 25 µm Cu (PSI), 4 weeks Feb 2023, 300k pairs;
  "MX17" µRWELL + scintillator demonstrator **tested at n_TOF and on ATOMKI neutron and proton beams**; magnet demonstrator
  tested at LNL proton beam 2025. n_TOF 2 months 2026 before LS3. Workshops: LNF "X17 What if?" 19–20 Mar 2026; ECT* 23–27 Mar 2026.
- Montreal: no result found after 2023 (Zacek Guineapig23 talk); 7LiF on Al, water cooled, thin CF beam pipe section.
- ATOMKI 4He: PRC 104 044003 (2021) at Ep 510/610/900 keV; no new T data found 2025–26. Krasznahorkay 2025 review: 2023 run analysis "last phase".
- Tohoku FNL: 4.5 MV Dynamitron, monoenergetic neutrons (2025 JSAP abstract, pulsing planned). Current not found.
- AIST NMIJ: 4 MV Pelletron (pulsing), neutron fluence standards (144, 565 keV, 5 MeV); CW 14.8 MeV. T target not confirmed.
- PKU 4.5 MV single-stage VdG: p/He 0.7–3.5 MeV up to 10 µA (2015); neutron cross sections.
- Sichuan Univ.: HVEE 3 MV Tandetron, 3 HE lines incl. nuclear physics (NIM B 2018).
- Tokyo Tech: 3.2 MV 3U-HC Pelletron, ~5 µA p on 7Li DC, 2 mA peak pulsed, keV-neutron source.
- Kyushu: 11 MV tandem (too high).
- iThemba LABS: HVEE 3 MV Tandetron, 200 eµA p, 25 eµA He; IBA + low-energy astrophysics line (2023 commissioning).
- ANU 14UD: low-E protons need modifications (~8 MeV used) → ENERGY.
- IFIN-HH 3 MV Tandetron: nuclear astrophysics + ultra-low background lab (arXiv 1907.03596).
- Melbourne/ANU proposal arXiv 2302.13281 (Sevior et al.): TPC on the **University of Melbourne 5 MV Pelletron**, p+7Li at 1.05 MeV,
  "comfortably supply 2 µA", 17,000 X17 per 30 d if ATOMKI; ANU 14UD for higher E; "in one year following funding". Status unknown.
- Birmingham HF-ADNeF: Neutron Therapeutics, nominal 2.6 MeV, 30 mA, 3e13 n/s, final acceptance Dec 2023; no variable range published (ask).
  Also MC40 cyclotron.
- Hanoi VNU HUS: NEC 5SDH-2 1.7 MV tandem Pelletron, p 0.35–3.4 MeV (2011); two-arm 140° spectrometer, Universe 10 168 (2024).
