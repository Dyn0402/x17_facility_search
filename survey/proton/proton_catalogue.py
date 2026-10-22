#!/usr/bin/env python3
"""
proton_catalogue.py -- every proton machine found in the 2026-10-22 survey that could put 0.4-2.5 MeV protons
on a thin target in front of the MX17 apparatus, with what decides it, the verdict and the source.

    PY=~/PycharmProjects/nTof_x17/.venv/bin/python
    $PY survey/proton/proton_catalogue.py   # -> survey/proton/facilities.csv, out/triage.csv, out/census.csv, out/ranking.{csv,png}

Verdicts (PROTON_SURVEY.md §4):
  STUDIED     a dedicated study exists in this repo
  POTENTIAL   reaches the ATOMKI strength faster than the LNL baseline, or tests a claim LNL cannot
              (⁴He on tritium, ¹²C), with a known ≥ 10 µA DC and an access route: worth a dedicated study
  MARGINAL    tests ⁸Be (and maybe more) at LNL-like currents (~1-10 µA), or the current is unknown
  X17 LAB     runs its own X17 pair experiment: a partner or a competitor, not a host
  ENERGY      cannot deliver 1.03-1.10 MeV protons (≤ 0.4 MV machines, fixed-energy BNCT/RFQ, big tandems)
  CURRENT     < 0.5 µA of protons at the energy (AMS and heavy-ion tandems)
  ACCESS      hospital, defence, sanctions, or closed
  WATCH       not running yet; the verdict it would get is given

Numbers: `i_dc` is the DC proton current at ~1 MeV in µA.  When it is a class default rather than a published
number, `i_note` says "class default" and `i_est` is set (ESTIMATE, ask).  `tritium`: yes (runs Ti-T targets) / ask / no.  Coordinates are
city-level.  SOURCES.md has every number with its source; RESEARCH_NOTES.md has the raw search notes.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / 'out'
sys.path.insert(0, str(HERE))
import proton_reach as pr  # noqa: E402

C = ['key', 'facility', 'site', 'lat', 'lon', 'cls', 'machine', 'e_lo', 'e_hi', 'i_dc', 'i_note', 'tritium', 'access',
     'status', 'x17', 'verdict', 'reason', 'source']

# class defaults for an unpublished current (ESTIMATE): a Tandetron with a duoplasmatron/H⁻ source, a single-ended
# machine with an RF source, a Pelletron tandem with a sputter/Alphatross source (IBA practice)
I_CLASS = {'tandetron': 10., 'single': 10., 'pelletron': 1.}

ROWS = [
    # ---------------- studied ----------------------------------------------------------------------------------
    ('lnl_cn', 'LNL Legnaro (AN2000 / CN)', 'Legnaro, IT', 45.353, 11.948, 'single-ended',
     'AN2000 2 MV and CN 7 MV single-ended Van de Graaffs', 0.2, 7.0, 4.0, '', 'ask', 'LNL PAC (INFN user lab)',
     'operating', 'Aipac8Be (LNL) ran on AN2000 2023-24, ~790 h at 0.8 µA, LiF; no result', 'STUDIED',
     'Geant4 study: ⁸Be at 3σ in 1.0 d (big plastics) / 17 d (as built) at 1 µA; CN authorised to 4 µA; target study done',
     'lnl/FACILITY.md; lnl/FEASIBILITY_SIM.md §15; Gustavino 2026'),
    ('demokritos', 'NCSR Demokritos 5.5 MV tandem', 'Athens, GR', 37.999, 23.817, 'tandem',
     '5.5 MV tandem (2022 Pelletron upgrade, TORVIS 100 µA H⁻) + PAPAP 250 kV', 0.6, 11.0, 1.0, 'post-upgrade current at 0.9 MeV (ask)',
     'yes', 'collaboration (Greek national lab)', 'operating',
     '', 'STUDIED', 'Geant4 study of ³H(p,e⁺e⁻)⁴He on the lab\'s own Ti-T: 3.6 d (big) / 35 d (as built) at 1 µA; S/B ≈ 1 %',
     'demokritos/FACILITY.md; demokritos/ESTIMATES.md §6'),
    # ---------------- labs with their own X17 experiment ------------------------------------------------------
    ('atomki', 'ATOMKI Debrecen (Tandetron 2 MV, VdG-5)', 'Debrecen, HU', 47.543, 21.626, 'tandem',
     'HVEE 2 MV Tandetron (2015) + 5 MV single-ended VdG', 0.2, 4.0, 200., '200 µA is at 2 MV terminal; at 0.5 MV (ask)',
     'yes', 'collaboration; ChETEC-INFRA TA', 'operating',
     'the original ATOMKI ⁸Be/⁴He/¹²C claims; new 6-telescope DSSD and E-θ spectrometers (2025); our µRWELL demonstrator was beam-tested here',
     'X17 LAB', 'the claim\'s own lab: every reaction, tritium in hand, 200 µA Tandetron. A host only by agreement',
     'ATOMKI X17 talk (Tandetron 200 µA p); PRC 104 044003; PRC 106 L061601; Gustavino 2026'),
    ('psi_meg2', 'PSI MEG II Cockcroft-Walton', 'Villigen, CH', 47.536, 8.222, 'single-ended',
     '1 MV Cockcroft-Walton inside the MEG II spectrometer', 0.4, 1.1, 100., '', 'no', 'MEG II only (beam pipe inserted into the detector)',
     'operating (calibration machine)', 'MEG II X17 run Feb 2023: R(18.1) < 1.2e-5, R(17.6) < 1.8e-6 (EPJC 85 763)',
     'X17 LAB', 'built into the MEG II detector; 50 µA at 1.1 and 100 µA at 1.05 MeV tested',
     'EPJC 83 230 (2023) §2.2.3; arXiv:2411.07994'),
    ('hanoi', 'VNU Hanoi 5SDH-2 Pelletron', 'Hanoi, VN', 20.996, 105.807, 'tandem',
     'NEC 1.7 MV 5SDH-2 tandem Pelletron (2011)', 0.35, 3.4, 1.0, 'targets punctured at 1-1.5 µA', 'ask', 'collaboration',
     'operating', 'two-arm 140° spectrometer with ATOMKI: ⁸Be anomaly at 18.15 confirmed (Universe 10 168, 2024)',
     'X17 LAB', '~1 µA tandem; ATOMKI-partnered X17 program', 'arXiv:2401.11676'),
    ('montreal', 'Université de Montréal tandem', 'Montréal, CA', 45.504, -73.613, 'tandem',
     '6 MV EN tandem; X17 beamline', 0.4, 12.0, 2.0, 'up to 10 µA possible', 'no', 'collaboration',
     'operating', 'own ⁸Be IPC experiment (MWPC + DAPHNE bars, ~4π, water-cooled ⁷LiF): set up 2022-24, no result found',
     'X17 LAB', '2 µA (10 possible) at 0.4-1.0 MeV, 2 keV spread; own 4π ⁸Be setup', 'arXiv:2211.11900; EPJC 83 230'),
    ('ctu_ieap', 'IEAP CTU Van de Graaff', 'Prague, CZ', 50.117, 14.443, 'single-ended',
     'HVEE HV2500 Van de Graaff', 0.4, 2.5, 1.0, 'class default (ask)', 'ask', 'collaboration (Czech national)',
     'operating', 'X17 spectrometer for ⁸Be and ⁴He IPC under construction (6 TPCs + MWPC, Timepix3 tracker, OFTPC)',
     'X17 LAB', 'its own X17 apparatus is being built on this machine', 'arXiv:2606.18821; EPJC 83 230; IEAP job posting'),
    ('melbourne', 'University of Melbourne 5 MV Pelletron', 'Melbourne, AU', -37.797, 144.961, 'single-ended',
     '5 MV Pelletron', 1.0, 5.0, 2.0, '"comfortably 2 µA"', 'ask', 'collaboration', 'operating',
     'X17 TPC proposal (Sevior et al., 2023): ⁸Be at 1.05 MeV, 30-d run, "one year after funding"',
     'X17 LAB', 'proposed TPC X17 program on this machine; 2 µA', 'arXiv:2302.13281'),
    # ---------------- underground ------------------------------------------------------------------------------
    ('luna_mv', 'LNGS Bellotti IBF (LUNA-MV)', 'Assergi (Gran Sasso), IT', 42.454, 13.575, 'underground',
     'HVEE 3.5 MV Singletron, 2 beamlines, 1400 m rock', 0.3, 3.5, 1000., '500 µA at 0.3-0.5 MV', 'ask',
     'LNGS user facility (PAC), since Oct 2023', 'operating',
     '', 'POTENTIAL',
     'mA DC over 0.3-3.5 MeV: every claim at the apparatus cap, and no cosmics (the as-built setup needs no veto). Named for ³H(p,e⁺e⁻)⁴He in the 2023 X17 community report. Tritium at LNGS (ask)',
     'Frontiers Phys 2023 10.3389/fphy.2023.1291113; Junker EuNPC 2025; EPJC 83 230'),
    ('felsenkeller', 'Felsenkeller 5 MV Pelletron (HZDR)', 'Dresden, DE', 51.034, 13.700, 'underground',
     'NEC 5 MV Pelletron, internal RF source (single-ended H, He), 45 m rock', 0.4, 5.0, 30., 'design 50 µA; "several tens of µA" (ask p)', 'ask',
     'ChETEC-INFRA / EURO-LABS TA, free via advisory board', 'operating', '', 'POTENTIAL',
     'tens of µA single-ended, cosmic muons ÷40: all three claims at or near the cap; free TA beam time',
     'arXiv:2412.19874; chetec-infra.eu Felsenkeller page; HELIUM25 Boeltzig'),
    ('luna400', 'LNGS LUNA 400 kV', 'Assergi (Gran Sasso), IT', 42.454, 13.575, 'underground',
     '400 kV inline Cockcroft-Walton', 0.05, 0.4, 500., '~1 mA H⁺ class', 'ask', 'LUNA collaboration', 'operating',
     '', 'ENERGY', 'tops out at 400 keV: below the 441 keV calibration and the 1.03 MeV resonance', 'JUNA 2016 talk; LUNA'),
    ('juna', 'CJPL JUNA 400 kV', 'Jinping, CN', 28.15, 101.71, 'underground',
     '400 kV ECR, 10 mA p (2019); 2.1 mA at 270 keV underground (2020)', 0.05, 0.4, 2000., '', 'ask', 'JUNA collaboration',
     'operating', '', 'ENERGY', '≤ 400 keV: no ⁸Be resonance, no ⁴He/¹²C window', 'Yuanzineng kexue jishu 53 (2019); CJPL news Dec 2020'),
    ('caspar', 'CASPAR (SURF)', 'Lead SD, US', 44.353, -103.751, 'underground',
     '1 MV KN Van de Graaff, RF source', 0.15, 1.0, 100., 'design 0.1 mA H⁺', 'ask', 'collaboration', 'withdrawn from SURF for construction',
     '', 'WATCH', 'tops out at ~1.0-1.1 MeV (⁸Be only at the edge) and is off-site for now: would be MARGINAL',
     'JUNA 2016 talk; CASPAR status'),
    # ---------------- neutron metrology labs (Ti-T targets) ------------------------------------------------------
    ('jrc_monnet', 'JRC Geel MONNET', 'Geel, BE', 51.220, 5.040, 'tandem',
     'HVEE 3.5 MV electrostatic tandem', 0.4, 7.0, 100., 'DC on target; 10 µA pulsed. Lowest p energy (ask)', 'yes',
     'EUFRAT open-access calls (2024, 2025); CERIC-ERIC', 'operating', '', 'POTENTIAL',
     '100 µA DC, Ti-T and ⁷Li targets routine, open calls: all three claims at the cap',
     'JRC MONNET pages; EPJ Web Conf 284 06002 (ND2023)'),
    ('ptb_piaf', 'PTB PIAF (Tandetron / VdG)', 'Braunschweig, DE', 52.296, 10.461, 'tandem',
     'HVEE Tandetron (p, d ≤ 4 MeV) + 3.75 MV VdG; CV28 cyclotron', 0.3, 4.0, 20., '"similar currents" to the cyclotron (≤ 80 µA): ask', 'yes',
     'national metrology institute: collaboration', 'operating', '', 'POTENTIAL',
     'Ti-T, D and ⁷Li targets routine in a big open hall; all three claims if ~20 µA holds',
     'ChETEC facility directory (PTB PIAF); PTB 6.42 pages'),
    ('npl', 'NPL neutron metrology (new 2 MV Tandetron)', 'Teddington, UK', 51.426, -0.343, 'tandem',
     'new 2 MV Tandetron replacing the 3.5 MV VdG (retired after 60 yr)', 0.2, 4.0, 300., 'tender spec ≥ 300 µA DC', 'yes',
     'national metrology institute: collaboration', 'installed; commissioning 2026 (ask)', '', 'WATCH',
     '≥ 300 µA DC over 0.2-4 MeV with a T(p,n) heritage: POTENTIAL once running',
     'UK tender 005794-2023; NPL abstract, STFC indico event 1939 (2026)'),
    ('irsn_amande', 'ASNR (IRSN) AMANDE', 'Cadarache, FR', 43.687, 5.762, 'tandem',
     'HVEE 2 MV Tandetron, p/d 0.1-4 MeV, DC or pulsed', 0.1, 4.0, 10., 'class default (ask)', 'yes',
     'national metrology lab: collaboration', 'operating', '', 'MARGINAL',
     'all reactions incl. Ti-T on a wobbling holder; current and access unknown', 'arXiv:1203.2443; Lebreton 2011'),
    ('cea_dam', 'CEA DAM Bruyères-le-Châtel 4 MV', 'Bruyères-le-Châtel, FR', 48.594, 2.190, 'single-ended',
     '4 MV Van de Graaff (neutron standards)', 0.5, 4.0, 10., 'class default', 'yes', 'defence site', 'operating (ask)',
     '', 'ACCESS', 'defence laboratory', 'literature'),
    ('tohoku_fnl', 'Tohoku FNL 4.5 MV Dynamitron', 'Sendai, JP', 38.256, 140.840, 'single-ended',
     '4.5 MV Dynamitron (monoenergetic neutrons)', 0.5, 4.5, 10., 'class default (ask)', 'ask', 'collaboration', 'operating',
     '', 'MARGINAL', 'Dynamitron, neutron-standards targets; current and tritium unknown', 'JSAP 2025 abstract 9p-P08-6'),
    ('aist', 'AIST/NMIJ 4 MV Pelletron', 'Tsukuba, JP', 36.060, 140.130, 'single-ended',
     '4 MV Pelletron (neutron fluence standards)', 0.5, 4.0, 10., 'class default (ask)', 'ask', 'collaboration', 'operating',
     '', 'MARGINAL', 'neutron-standards machine; current, tritium and access unknown', 'BIPM CCRI reports; AIST neutron pages'),
    ('pku', 'Peking University 4.5 MV Van de Graaff', 'Beijing, CN', 39.992, 116.306, 'single-ended',
     '4.5 MV single-stage VdG', 0.7, 3.5, 10., '', 'ask', 'collaboration', 'operating', '', 'MARGINAL',
     'p 0.7-3.5 MeV up to 10 µA: ⁸Be and ¹²C (⁴He at 0.7-0.9 only)', 'Yuanzineng kexue jishu 42 (2008); 2015 irradiation paper'),
    # ---------------- high-current research machines -------------------------------------------------------------
    ('tunl_lena', 'TUNL LENA 2 MV Singletron', 'Durham NC, US', 36.003, -78.940, 'single-ended',
     'HVEE 2 MV Singletron (mA DC or 2 ns pulsed) + ≤ 230 kV ECR (2-3 mA)', 0.15, 2.0, 1000., '"mA intensity"', 'ask',
     'TUNL (DOE): collaboration', 'operating', '', 'POTENTIAL',
     'mA DC up to 2 MeV: ⁸Be and ¹²C at the cap; ⁴He if a Ti-T target is allowed (ask)',
     'arXiv:2211.10327; tunl.duke.edu LENA accelerators; LENA II abstract 2025'),
    ('notre_dame', 'Notre Dame ISNAP 5U (St. ANA)', 'Notre Dame IN, US', 41.700, -86.238, 'single-ended',
     'NEC 5 MV vertical single-ended Pelletron, ECR in the terminal (2012)', 0.4, 5.0, 50., '"high intensities" (ask)', 'ask',
     'NSF user lab: collaboration', 'operating', '', 'POTENTIAL',
     'single-ended high-intensity ECR machine for (p,γ) astrophysics: all claims near the cap if ~50 µA holds',
     'isnap.nd.edu accelerators; JINA newsletter Oct 2012'),
    ('bochum', 'Bochum Dynamitron-Tandem-Labor (RUBION)', 'Bochum, DE', 51.445, 7.262, 'tandem',
     '4 MV Dynamitron tandem + 500 kV (100-150 µA p at 318 keV)', 0.2, 8.0, 10., 'tandem current at 1 MeV: class default (ask)', 'ask',
     'university lab: collaboration', 'operating (ask)', '', 'MARGINAL',
     'nuclear-astrophysics lab with a high-current 500 kV (calibration only) and a 4 MV tandem of unknown low-E current',
     'arXiv:0804.1934 (500 kV, 100-150 µA)'),
    ('hzdr_ibc', 'HZDR Ion Beam Center (3 MV Tandetron, 2 MV VdG)', 'Dresden-Rossendorf, DE', 51.064, 13.950, 'tandem',
     '3 MV and 6 MV Tandetrons, 2 MV single-ended VdG', 0.2, 6.0, 10., 'class default (ask)', 'ask',
     'free user proposals (HZDR-GATE), fast track', 'operating', '', 'MARGINAL',
     'big user facility with free access and a 2 MV single-ended VdG; currents not published', 'hzdr.de IBC user access'),
    ('ithemba_tandetron', 'iThemba LABS 3 MV Tandetron', 'Cape Town, ZA', -34.025, 18.720, 'tandem',
     'HVEE 3 MV Tandetron, astrophysics line (2023)', 0.3, 6.0, 200., '200 eµA p at 3 MV terminal; at low terminal (ask)', 'ask',
     'national user facility (PAC)', 'operating', '', 'POTENTIAL',
     'a 200 µA Tandetron with a low-energy astrophysics line: ⁸Be and ¹²C at the cap',
     'SAIP 2023 iThemba talks; Conradie 2018'),
    ('ifin_hh', 'IFIN-HH 3 MV Tandetron', 'Măgurele, RO', 44.348, 26.030, 'tandem',
     'HVEE 3 MV Tandetron + 1 MV Tandetron; salt-mine low-background lab', 0.2, 6.0, 10., 'class default (ask)', 'ask',
     'national lab; ChETEC/RADIATE TA', 'operating', '', 'MARGINAL',
     'nuclear-astrophysics Tandetron with TA access; current not published', 'arXiv:1907.03596'),
    ('cna_sevilla', 'CNA Sevilla 3 MV Pelletron', 'Seville, ES', 37.410, -6.000, 'tandem',
     'NEC 9SDH-2 3 MV tandem (HiSPANOS neutron line, 1 ns pulsing)', 0.5, 6.0, 1.0, 'Pelletron class default; a listing says "up to 1 mA" (ask)', 'ask',
     'Spanish ICTS user facility', 'operating', '', 'MARGINAL',
     'tandem with a ⁷Li(p,n) neutron line (HiSPANOS); current at 1 MeV unknown', 'arXiv:1906.05716; OMA facility listing'),
    ('cmam', 'CMAM Madrid 5 MV Tandetron', 'Madrid, ES', 40.546, -3.690, 'tandem',
     'HVEE 5 MV Tandetron, six lines incl. a nuclear-physics line', 0.3, 10.0, 10., 'class default (ask)', 'ask',
     'Spanish ICTS user facility', 'operating', '', 'MARGINAL', 'Tandetron with a nuclear-physics line; current not published',
     'ciencia.gob.es ICTS accelerators'),
    ('labec', 'INFN LABEC 3 MV Tandetron', 'Florence, IT', 43.818, 11.202, 'tandem',
     'HVEE 3 MV Tandetron (IBA, AMS)', 0.3, 6.0, 10., 'class default (ask)', 'ask', 'INFN: collaboration', 'operating',
     '', 'MARGINAL', 'INFN Tandetron, IBA-focused; current not published', 'IAEA accelerator list'),
    ('circe', 'CIRCE 3 MV Pelletron (ERNA)', 'Caserta, IT', 41.073, 14.334, 'tandem',
     'NEC 3 MV Pelletron (AMS + ERNA recoil separator)', 0.5, 6.0, 1.0, 'Pelletron class default', 'ask', 'INFN/university',
     'operating', '', 'MARGINAL', 'AMS/astrophysics tandem: ~µA protons at best', 'IAEA accelerator list'),
    ('rbi_zagreb', 'Ruđer Bošković 1 MV Tandetron / 6 MV EN', 'Zagreb, HR', 45.835, 15.985, 'tandem',
     'HVEE 1 MV Tandetron + 6 MV EN tandem', 0.2, 2.0, 10., 'class default (ask)', 'ask', 'RADIATE TA', 'operating',
     '', 'MARGINAL', 'Tandetron to 2 MeV: ⁸Be and ¹²C (to 2 MeV); current not published', 'IAEA accelerator list; RADIATE'),
    ('jsi', 'Jožef Stefan 2 MV Tandetron', 'Ljubljana, SI', 46.090, 14.600, 'tandem',
     'HVEE 2 MV Tandetron', 0.2, 4.0, 10., 'class default (ask)', 'ask', 'RADIATE TA', 'operating', '', 'MARGINAL',
     'IBA Tandetron with TA access; current not published', 'IAEA accelerator list; RADIATE news 2022'),
    ('npi_tandetron', 'NPI Řež 3 MV Tandetron (CANAM)', 'Řež, CZ', 50.180, 14.310, 'tandem',
     'HVEE 3 MV Tandetron', 0.2, 6.0, 10., 'class default (ask)', 'ask', 'CANAM open access', 'operating', '', 'MARGINAL',
     'Tandetron at the lab that also runs the TR-24 Be(p,n) source', 'IAEA accelerator list'),
    ('uppsala', 'Uppsala Tandem Laboratory', 'Uppsala, SE', 59.840, 17.650, 'tandem',
     'NEC 5 MV Pelletron tandem + 350 kV implanter', 0.5, 10.0, 1.0, 'Pelletron class default', 'ask', 'user lab',
     'operating', '', 'MARGINAL', 'IBA/AMS tandem: ~µA protons', 'uu.se tandemlab'),
    ('lund_libaf', 'Lund LIBAF 3 MV single-ended Pelletron', 'Lund, SE', 55.711, 13.210, 'single-ended',
     'NEC 3 MV single-ended Pelletron', 0.5, 3.0, 10., 'class default (ask)', 'ask', 'user lab', 'operating', '', 'MARGINAL',
     'single-ended to 3 MeV: ⁸Be and ¹²C; current not published', 'IAEA accelerator list'),
    ('helsinki', 'Helsinki 5 MV tandem (Kumpula)', 'Helsinki, FI', 60.204, 24.962, 'tandem',
     '5 MV tandem (+ 2 MV)', 0.5, 10.0, 1.0, 'class default', 'ask', 'user lab', 'operating', '', 'MARGINAL',
     'IBA tandem: ~µA protons', 'IAEA accelerator list'),
    ('surrey', 'Surrey Ion Beam Centre 2 MV Tandetron', 'Guildford, UK', 51.243, -0.589, 'tandem',
     'HVEE 2 MV Tandetron (UK national IBC)', 0.2, 4.0, 10., 'class default (ask)', 'ask', 'UK national facility; RADIATE TA',
     'operating', '', 'MARGINAL', 'national ion-beam facility; current not published', 'IAEA accelerator list'),
    ('cologne', 'Cologne 10 MV FN tandem', 'Cologne, DE', 50.928, 6.928, 'tandem',
     'HVEC 10 MV FN tandem (+ 6 MV Tandetron for AMS)', 2.0, 20.0, 0.8, '"up to about 800 nA" p', 'no', 'ChETEC TA',
     'operating', '', 'CURRENT', '≤ 0.8 µA and no low-energy protons: neither the 1.03 MeV resonance nor useful current',
     'chetec-infra.eu UoC page'),
    ('kentucky', 'Kentucky UKAL 7 MV Van de Graaff', 'Lexington KY, US', 38.033, -84.503, 'single-ended',
     'HVEC 7 MV CN single-ended (1.875 MHz pulsing)', 1.0, 7.0, 5.0, '"several µA" bunched', 'ask', 'university lab', 'operating',
     '', 'MARGINAL', 'single-ended to 7 MeV, a few µA', 'pa.uky.edu accelerator facilities'),
    ('ohio', 'Ohio University Edwards Accelerator Lab', 'Athens OH, US', 39.324, -82.101, 'tandem',
     '4.5 MV tandem, Cs sputter source', 0.5, 9.0, 10., 'typical max on target; at 0.5-1 MeV (ask)', 'yes', 'university lab',
     'operating', '', 'MARGINAL', 'solid and gas T targets for neutrons, 10 µA: all three claims if the tandem runs at 0.5 MV terminal',
     'arXiv:1707.04255; ohio.edu neutron source capabilities'),
    ('lanl_ibml', 'LANL Ion Beam Materials Laboratory', 'Los Alamos NM, US', 35.875, -106.300, 'tandem',
     'NEC 3.2 MV Pelletron tandem + 200 kV implanter', 0.4, 6.4, 1.0, 'Pelletron class default', 'ask', 'national lab (CINT user program)',
     'operating', '', 'MARGINAL', 'IBA tandem; tritium expertise on site', 'cint.lanl.gov'),
    ('sandia_ibl', 'Sandia Ion Beam Laboratory', 'Albuquerque NM, US', 35.050, -106.540, 'single-ended',
     'NEC 3 MV single-ended Pelletron, 6 MV tandem, 1 MV tandem', 0.4, 3.0, 10., 'class default (ask)', 'ask',
     'national lab', 'operating', '', 'MARGINAL', 'single-ended 3 MV at a national lab; access uncertain', 'SNL INFUSE 2020'),
    ('tokyo_tech', 'Tokyo Tech 3.2 MV Pelletron', 'Tokyo, JP', 35.605, 139.684, 'single-ended',
     'NEC 3U-HC Pelletron (keV-neutron source)', 0.5, 3.2, 5.0, '~5 µA DC on ⁷Li', 'ask', 'university lab', 'operating',
     '', 'MARGINAL', '~5 µA single-ended to 3.2 MeV: ⁸Be and ¹²C', 'EXFOR 22272; Tokyo Tech Pelletron talk'),
    ('sichuan', 'Sichuan University 3 MV Tandetron', 'Chengdu, CN', 30.630, 104.080, 'tandem',
     'HVEE 3 MV Tandetron, nuclear-physics line', 0.2, 6.0, 10., 'class default (ask)', 'ask', 'collaboration', 'operating',
     '', 'MARGINAL', 'Tandetron with a nuclear-physics line; current not published', 'NIM B 2018 (Sichuan 3 MV Tandetron)'),
    ('ciae', 'CIAE Beijing (1.7 MV tandem)', 'Beijing, CN', 39.730, 116.010, 'tandem',
     'NEC 1.7 MV Pelletron (+ 13 MV HI-13 tandem)', 0.4, 3.4, 1.0, 'Pelletron class default', 'ask', 'collaboration',
     'operating', '', 'MARGINAL', '~µA tandem', 'IAEA accelerator list'),
    ('kigam', 'KIGAM Daejeon (1.7 / 6 MV)', 'Daejeon, KR', 36.370, 127.360, 'tandem',
     '1.7 MV Pelletron, 6 MV tandem', 0.4, 3.4, 1.0, 'Pelletron class default', 'ask', 'collaboration', 'operating',
     '', 'MARGINAL', '~µA IBA tandems', 'IAEA accelerator list'),
    ('iuac', 'IUAC New Delhi (1.7 MV Pelletron)', 'New Delhi, IN', 28.540, 77.170, 'tandem',
     '1.7 MV Pelletron (PARAS) + 15UD', 0.4, 3.4, 1.0, 'Pelletron class default', 'ask', 'national user facility',
     'operating', '', 'MARGINAL', '~µA IBA tandem', 'IAEA accelerator list'),
    ('unam', 'UNAM Mexico (5.5 MV VdG, 3 MV Pelletron)', 'Mexico City, MX', 19.326, -99.180, 'single-ended',
     '5.5 MV single-ended VdG + 3 MV Pelletron tandem', 0.5, 5.5, 5.0, 'class default (ask)', 'ask', 'collaboration',
     'operating (ask)', '', 'MARGINAL', 'single-ended 5.5 MV; current unknown', 'IAEA accelerator list'),
    ('usp', 'São Paulo LAMFI / Pelletron', 'São Paulo, BR', -23.560, -46.730, 'tandem',
     '1.7 MV Pelletron (LAMFI) + 8 MV Pelletron', 0.4, 3.4, 1.0, 'Pelletron class default', 'ask', 'collaboration',
     'operating', '', 'MARGINAL', '~µA IBA tandem', 'IAEA accelerator list'),
    ('ansto', 'ANSTO CAS (STAR 2 MV, 1 MV, 6 MV)', 'Lucas Heights, AU', -34.050, 150.980, 'tandem',
     '2 MV STAR Tandetron, 1 MV Tandetron, 6 MV SIRIUS', 0.2, 4.0, 10., 'class default (ask)', 'ask', 'user program',
     'operating', '', 'MARGINAL', 'Tandetrons with a user program; current not published', 'IAEA accelerator list'),
    ('anu_14ud', 'ANU 14UD tandem', 'Canberra, AU', -35.280, 149.120, 'tandem',
     'NEC 14UD Pelletron', 4.0, 30.0, 1.0, 'low-E protons need modifications', 'ask', 'national facility', 'operating',
     '', 'ENERGY', 'needs modifications for low-energy protons (~8 MeV used)', 'arXiv:0911.5325'),
    # ---------------- BNCT and other high-current fixed-energy machines ---------------------------------------
    ('birmingham_adnef', 'Birmingham HF-ADNeF (Neutron Therapeutics)', 'Birmingham, UK', 52.450, -1.930, 'BNCT / high-current',
     'electrostatic, nominal 2.6 MeV, 30 mA', 2.6, 2.6, 30000., '', 'ask', 'NNUF research facility', 'operating',
     '', 'ENERGY', 'fixed ~2.6 MeV: no ⁸Be resonance, ¹²C only off the resonance; POTENTIAL if it can run at 1.0-2.1 MeV (ask)',
     'Neutron Therapeutics/Birmingham Dec 2023'),
    ('nagoya_nuans', 'Nagoya NUANS (IBA Dynamitron)', 'Nagoya, JP', 35.155, 136.965, 'BNCT / high-current',
     'IBA Proton-Dynamitron 2.8 MeV, 15 mA', 2.8, 2.8, 15000., '', 'no', 'BNCT research', 'operating',
     '', 'ENERGY', 'fixed 2.8 MeV BNCT machine', 'AESJ 2017; Nagoya NUANS'),
    ('binp_vita', 'BINP VITA (vacuum-insulated tandem)', 'Novosibirsk, RU', 54.850, 83.110, 'BNCT / high-current',
     'vacuum-insulated tandem, p/d 0.3-2.3 MeV, nA-10 mA DC', 0.3, 2.3, 10000., '', 'ask', 'Russian institute', 'operating',
     '', 'ACCESS', 'physically ideal (0.3-2.3 MeV, 10 mA DC, variable), but CERN-Russia cooperation ended', 'PHPL VITAmin 2025; PTE 2024'),
    ('cnao_alphabeam', 'CNAO Alphabeam (TAE)', 'Pavia, IT', 45.200, 9.140, 'BNCT / high-current',
     'TAE electrostatic tandem 2.5 MeV (BNCT)', 2.5, 2.5, 10000., '', 'no', 'hospital', 'under construction', '', 'ACCESS',
     'hospital BNCT machine at fixed energy', 'ISNCT AB-BNCT table 2026'),
    ('helsinki_nubeam', 'Helsinki nuBeam (Neutron Therapeutics)', 'Helsinki, FI', 60.190, 24.910, 'BNCT / high-current',
     'electrostatic 2.6 MeV, 30 mA (BNCT)', 2.6, 2.6, 30000., '', 'no', 'hospital', 'clinical trials', '', 'ACCESS',
     'hospital BNCT machine at fixed energy', 'ISNCT AB-BNCT table 2026'),
    ('franz', 'FRANZ Frankfurt (RFQ-IH)', 'Frankfurt, DE', 50.173, 8.633, 'linac / RFQ',
     '2.0 MeV RFQ-IH linac, ≤ 20 mA DC design', 1.8, 2.2, 20000., 'design', 'no', 'university', '2 MeV beam not yet reported',
     '', 'WATCH', 'fixed ~2 MeV: no ⁸Be, but ¹¹B at 2.0 MeV is the ¹²C claim (1.88/2.1 MeV points) at the cap',
     'franz/FACILITY.md'),
    ('saraf', 'SARAF (Soreq)', 'Yavne, IL', 31.900, 34.700, 'linac / RFQ',
     'RFQ + SC linac; LiLiT at ~1.9 MeV, 1-2 mA CW', 1.9, 1.9, 1500., '', 'no', 'collaboration', 'phase II commissioning',
     '', 'ENERGY', 'fixed-energy linac (LiLiT 1.9 MeV)', 'survey/SOURCES.md (SARAF)'),
    ('lnl_anthem', 'LNL ANTHEM RFQ', 'Legnaro, IT', 45.353, 11.948, 'linac / RFQ',
     '5 MeV RFQ, 30 mA (Be target, BNCT)', 5.0, 5.0, 30000., '', 'no', 'INFN', 'under development', '', 'ENERGY',
     'fixed 5 MeV', 'ISNCT AB-BNCT table 2026'),
]

assert len({r[0] for r in ROWS}) == len(ROWS), 'duplicate key'


def evaluate(r):
    """Reach for one catalogue row: per-claim days (big plastics, as built) at the usable current."""
    d = dict(zip(C, r))
    out = dict(key=d['key'])
    best = None
    claims = []
    for rk, R in pr.REACTIONS.items():
        ok = pr.covers(rk, d['e_lo'], d['e_hi'], d['tritium'])
        out[f'{rk}_ok'] = ok
        if not ok:
            out[f'{rk}_days_big'] = out[f'{rk}_days_built'] = np.nan
            continue
        claims.append(rk)
        i_use = min(d['i_dc'], pr.CAP[rk])
        out[f'{rk}_iuse'] = i_use
        out[f'{rk}_days_big'] = pr.days(rk, d['i_dc'], 'big')
        out[f'{rk}_days_built'] = pr.days(rk, d['i_dc'], 'built')
        if best is None or out[f'{rk}_days_big'] < out[f'{best}_days_big']:
            best = rk
    out['claims'] = ','.join(claims)
    out['n_claims'] = len(claims)
    out['best'] = best or ''
    out['days_big'] = out[f'{best}_days_big'] if best else np.nan
    out['days_built'] = out[f'{best}_days_built'] if best else np.nan
    # every claim the machine reaches, each to 3σ at the ATOMKI strength, back to back (big plastics)
    out['days_all_big'] = sum(out[f'{k}_days_big'] for k in claims) if claims else np.nan
    # crude headline: X17 produced per day into 4π at the machine's full current, best claim, no cap (ranks raw production)
    xs = [d['i_dc'] * pr.REACTIONS[k]['x17_day'] for k in claims]
    out['x17_day'] = max(xs) if xs else np.nan
    return out


# ---- the IAEA census of electrostatic machines: a class verdict for each --------------------------------------
AMS_WORDS = ('AMS', 'Radiocarbon', 'Radioacarbon', 'Dating', 'Carbon', 'Isotope', 'C-14', '14C', 'Geoscience', 'Earth',
             'Marine', 'Environment', 'Heritage', 'Louvre', 'AGLAE', 'Archaeology', 'Woods Hole', 'Tono', 'Geolog')


def census():
    """Class verdicts for every electrostatic machine in the IAEA Accelerator Knowledge Portal list."""
    src = HERE / 'iaea_electrostatic.csv'
    if not src.exists():
        return None
    rows = []
    for x in csv.DictReader(open(src, encoding='utf-8')):
        name, tv, typ = x['facility'], x['tv_mv'], x['type']
        try:
            v = float(tv.replace(',', '.'))
        except ValueError:
            v = np.nan
        tandem = typ == 'Tandem'
        e_hi = 2 * v if tandem else v
        if any(w.lower() in name.lower() for w in AMS_WORDS) or (tandem and v <= 0.6):
            cls, verdict = 'AMS / dating', 'CURRENT'
        elif not np.isfinite(v):
            cls, verdict = 'unknown', 'unknown'
        elif e_hi < 1.10:
            cls, verdict = 'low voltage', 'ENERGY'
        elif tandem and v >= 7:
            cls, verdict = 'large tandem', 'ENERGY'
        else:
            cls, verdict = ('tandem ≤ 6 MV' if tandem else 'single-ended ≤ 7 MV'), 'MARGINAL'
        c12 = e_hi >= 2.1 and cls not in ('AMS / dating', 'large tandem')
        rows.append(dict(iaea_id=x['iaea_id'], facility=name, city=x['city'], country=x['country'], type=typ, tv_mv=v,
                         e_hi=e_hi, cls=cls, verdict=verdict, c12_reach=c12))
    return pd.DataFrame(rows)


def ranking_figure(tri):
    sys.path.insert(0, str(HERE.parent.parent / 'ill'))
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use()
    t = tri[tri.n_claims > 0].sort_values(['days_big', 'n_claims'], ascending=[True, False]).copy()
    fig, ax = fs.figure(figsize=(7.2, 0.21 * len(t) + 1.2))
    vcol = {'STUDIED': '#0072B2', 'POTENTIAL': '#009E73', 'MARGINAL': '#E69F00', 'X17 LAB': '#CC79A7', 'WATCH': '#56B4E9'}
    y = np.arange(len(t))[::-1]
    for yi, (_, r) in zip(y, t.iterrows()):
        c = vcol.get(r.verdict, '0.6')
        ax.plot([r.days_big, r.days_built], [yi, yi], color=c, lw=1.2, alpha=0.5)
        ax.plot(r.days_big, yi, 'o', color=c, ms=5)
        ax.plot(r.days_built, yi, 'o', mfc='white', mec=c, mew=1.3, ms=5.5, zorder=3)
        ax.text(r.days_built * 1.25, yi, r.claims.replace('be8', '⁸Be').replace('he4', '⁴He').replace('c12', '¹²C'),
                va='center', fontsize=7, color='0.4')
    ax.set_yticks(y)
    ax.set_yticklabels([f"{n}{' *' if e else ''}" for n, e in zip(t.facility, t.i_est)], fontsize=7.5)
    ax.set_xscale('log')
    ax.set_xlabel('days to 3σ at ATOMKI strength (● big plastics, ○ as built)')
    ax.axvline(1, color='0.6', lw=0.8, ls=':')
    ax.set_xlim(0.02, 60)
    fs.fig_title(fig, 'Proton machines ranked for the MX17 apparatus', '* current is a class default (ask); scaled from LNL/Demokritos Geant4')
    fs.save(fig, OUT / 'ranking', data=t[['key', 'facility', 'verdict', 'i_dc', 'i_est', 'claims', 'days_big', 'days_built', 'days_all_big', 'x17_day']])


def main():
    cat = pd.DataFrame(ROWS, columns=C)
    cat['i_est'] = cat.i_note.str.contains('class default')
    tri = cat.merge(pd.DataFrame([evaluate(r) for r in ROWS]), on='key')
    OUT.mkdir(exist_ok=True)
    cat.to_csv(HERE / 'facilities.csv', index=False)
    tri.to_csv(OUT / 'triage.csv', index=False, float_format='%.4g')
    cen = census()
    if cen is not None:
        cen.to_csv(OUT / 'census.csv', index=False)
        print('census:', cen.verdict.value_counts().to_dict(), '| c12 reach:', int(cen.c12_reach.sum()))
    ranking_figure(tri)
    print(tri.verdict.value_counts().to_dict())
    show = tri[tri.n_claims > 0].sort_values('days_big')[['key', 'verdict', 'i_dc', 'claims', 'days_big', 'days_built', 'days_all_big', 'x17_day']]
    print(show.to_string(index=False, float_format=lambda v: f'{v:.3g}'))


if __name__ == '__main__':
    main()
