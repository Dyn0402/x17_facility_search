#!/usr/bin/env python3
"""
dashboard.py -- the data behind the neutron-facility dashboard on the site
(dylan-neff.web.cern.ch/facilities/neutron-facilities.html).

    PY=~/PycharmProjects/nTof_x17/.venv/bin/python
    $PY survey/catalogue.py          # first, if the catalogue or a model changed
    $PY survey/dashboard.py          # -> survey/out/dashboard.csv and the site's data/facilities-survey.json

The catalogue (catalogue.py: verdict, status, reason, source) and the model reach (out/triage.csv)
are read as they are.  This file adds what the page needs on top: where each facility is, the flux
the crude headline is computed from, how far we have looked into it (EFFORT), the links, the next
step and a dated log.  **Keep it updated:** when a facility is studied further, edit its EXTRA entry
(effort, links, next, updated), add a LOG line, rerun, then rebuild and deploy the site.

The headline, "X17 per day*", is deliberately the crudest number there is:

    X17/day = (neutrons/s on the n_TOF capsule) × <P> × X17/IPC × 86400

  * the n_TOF capsule: 500 bar ³He, Ø2 cm × 8 cm, beam along its axis (survey_yield.CELLS);
    neutrons/s = particle flux at the experiment position × π cm² (the full beam over the
    capsule face), or the facility's own n/s into the capsule where that is what is known;
  * <P>: IPC pairs per entering neutron folded over the source spectrum (survey_yield);
    cold/thermal neutrons are all absorbed and give 4.8e-11;
  * X17/IPC = 1.5e-3 (ATOMKI ⁴He, PRC 104 044003), the same at every E_n;
  * no acceptance, trigger, background, dead time or rate limit.  It ranks raw production only.
    The model reach (out/triage.csv) is the figure of merit; the page shows both.
"""
from __future__ import annotations

import json
import math
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import survey_yield as Y                                     # noqa: E402

OUT = HERE / 'out'
SITE = Path.home() / 'PycharmProjects/dylan-cern-site'
SITE_JSON = SITE / 'data' / 'facilities-survey.json'

CAPSULE = 'n_TOF capsule 500 bar × 8 cm'
A_CAP = math.pi * 1.0 ** 2          # cm², Ø2 cm capsule face
X17_IPC = 1.5e-3                    # ATOMKI ⁴He
DAY = 86400.0
WINDOW_EN = 2.75                    # MeV: E* ≤ 22.1 MeV, θ_min ≥ 99°
A_PF1B_SPOT = 19.6                  # cm², the Ø5 cm spot R_max is quoted for (survey_absorbed)

G = Y.E_GRID
SPECTRA = {
    'thermal': ('cold/thermal, all absorbed', Y.mono(e0=2.53e-8, width=1e-9)),
    'epithermal': ('1/E, 0.5 eV–10 keV', Y.epithermal()),
    'keV': ('near-threshold ⁷Li(p,n), kT ≈ 25 keV', Y.maxwell_flux()),
    'li7pn': ('thick ⁷Li(p,n), E_p 2.6 MeV, ≤ 0.85 MeV', Y.li7pn_thick()),
    'fission': ('²³⁵U fission (Watt)', Y.watt()),
    'dd': ('D-D, 2.45 MeV', Y.mono()),
    'tpn2': ('³H(p,n), 2.0 MeV', Y.mono(e0=2.0)),
    'dt': ('D-T, 14.1 MeV', Y.mono(e0=14.1, width=0.2)),
    'backn': ('Back-n ES#1, measured per decade', Y.per_decade(fr=Y.BACKN)),
    'ntof': ('n_TOF, isolethargic to 45 MeV', Y.per_decade(fr=Y.NTOF)),
    'nfs': ('NFS d(40)+Be', Y.nfs()),
    'wnr': ('LANSCE WNR 30° (estimated split)', Y.per_decade(fr=Y.WNR)),
    'bepn': ('⁹Be(p,n) 30 MeV (guess)', Y.per_decade(fr={(0.1, 1.0): 0.30, (1.0, 10.0): 0.55, (10.0, 28.0): 0.15})),
}


def fold(key):
    f = SPECTRA[key][1]
    p = f * Y.pairs_per_neutron(G, CAPSULE)
    tot = float(np.trapezoid(p, G))
    m = G <= WINDOW_EN
    return tot, float(np.trapezoid(p[m], G[m])) / tot


P = {k: fold(k) for k in SPECTRA}

# --------------------------------------------------------------------------- #
# How far each facility has been looked into.  The page draws these as 0-4 pips.
EFFORT = {
    1: 'Catalogued: status and a literature number',
    2: 'Scaled model: survey_absorbed / survey_fast reach',
    3: 'Dedicated study: analytic write-up',
    4: 'Geant4 study: full-apparatus simulation, write-up and slides',
}

# Per catalogue key.  beam: how the headline is computed —
#   flux  n/cm²/s at the experiment position (particle flux, whole spectrum) × π cm²
#   rate  n/s into the capsule
#   pairs IPC pairs/day in the capsule (from a study)
#   bound (op, ref, factor): no number of its own; ≤ / ≈ another row × factor
# sites: (name, lat, lon); scen: other scenarios shown in the detail panel.
EXTRA = {
    # ---- cold / thermal
    'ill_pf1b': dict(beam=('rate', 1.2e11 * A_CAP / A_PF1B_SPOT, 'thermal'),
                     geom='R_max 1.2e11 absorbed n/s on a Ø5 cm spot (survey_absorbed), scaled to the capsule face',
                     sites=[('ILL', 45.2073, 5.6929)], effort=4,
                     effort_note='Geant4 campaign of the whole apparatus on PF1B: rate walls, backgrounds, reach. Verdict in: feasible, ×3.2 short of the ⁸Be level in one 50-day cycle.',
                     links=[('The ILL study', 'ill.html'), ('Feasibility slides', '../notes/ill-x17-feasibility.html'),
                            ('3D: the ILL beams', 'ill-beams-3d.html')],
                     next='Closed unless the detector changes (Micromegas occupancy ÷10, 10 µs DAQ) or polarisation is used.',
                     contact='ILL contacts during the study', updated='2026-10-20'),
    'ill_fipps': dict(beam=('rate', 1.8e8, 'thermal'), geom='1.8e8 n/s into the capsule (ill/FACILITY.md)',
                      sites=[('ILL', 45.2073, 5.6929)], effort=3,
                      effort_note='Covered in the ILL study as the alternative beam.',
                      links=[('The ILL study', 'ill.html')], next='None: ×600 below PF1B.', updated='2026-10-20'),
    'frm2_mephisto': dict(beam=('rate', 1.091e11 * A_CAP / A_PF1B_SPOT, 'thermal'), geom='expected ≈ PF1B',
                          sites=[('FRM II', 48.2660, 11.6760)], effort=2,
                          next='Nothing until the reactor restarts; it would reach the same walls as PF1B.'),
    'ess_anni': dict(beam=('rate', 1.364e11 * A_CAP / A_PF1B_SPOT, 'thermal'), geom='2.5e10 capture flux at 5 MW (simulated)',
                     sites=[('ESS', 55.7339, 13.2500)], effort=2, next='Watch: ESS users from 2028.'),
    'nist_ngc': dict(beam=('rate', 4.418e10 * A_CAP / A_PF1B_SPOT, 'thermal'), sites=[('NIST NCNR', 39.1340, -77.2170)],
                     effort=2),
    'sns_fnpb': dict(beam=('rate', 5.455e9 * A_CAP / A_PF1B_SPOT, 'thermal'), sites=[('SNS', 35.9310, -84.3100)], effort=2),
    'jparc_nop': dict(beam=('bound', '≲', 'sns_fnpb', 1.0), sites=[('J-PARC MLF', 36.4500, 140.6040)], effort=1),
    'hfir': dict(beam=('bound', '≲', 'ill_pf1b', 1.0), sites=[('HFIR', 35.9180, -84.3040)], effort=1),
    'psi_sinq': dict(beam=('bound', '≲', 'ill_pf1b', 1.0), sites=[('PSI', 47.5360, 8.2230)], effort=1),
    'carr': dict(beam=('rate', 5.455e9 * A_CAP / A_PF1B_SPOT, 'thermal'), sites=[('CIAE', 39.7300, 116.0300)], effort=2),
    'cmrr': dict(beam=('bound', '≲', 'ill_pf1b', 1.0), sites=[('CAEP', 31.5000, 104.7000)], effort=1),
    'opal': dict(beam=('bound', '≲', 'ill_pf1b', 1.0), sites=[('ANSTO', -34.0510, 150.9810)], effort=1),
    'hanaro': dict(beam=('bound', '≲', 'ill_pf1b', 1.0), sites=[('KAERI', 36.4250, 127.3700)], effort=1),
    'jrr3': dict(beam=('bound', '≲', 'ill_pf1b', 1.0), sites=[('JAEA Tokai', 36.4600, 140.5930)], effort=1),
    'lansce_lujan': dict(beam=('bound', '≲', 'sns_fnpb', 1.0), sites=[('LANSCE', 35.8740, -106.3240)], effort=1),
    'isis': dict(beam=('bound', '≲', 'sns_fnpb', 1.0), sites=[('ISIS', 51.5720, -1.3150)], effort=1),
    'mitr': dict(beam=('bound', '≲', 'ill_pf1b', 1.0), sites=[('MIT', 42.3600, -71.0940)], effort=1),
    'murr': dict(beam=('bound', '≲', 'ill_pf1b', 1.0), sites=[('MURR', 38.9400, -92.3300)], effort=1),
    'brr': dict(beam=('bound', '≲', 'ill_pf1b', 1.0), sites=[('Budapest', 47.4900, 18.9700)], effort=1),
    'lvr15': dict(beam=('bound', '≲', 'ill_pf1b', 1.0), sites=[('Řež', 50.1800, 14.3100)], effort=1),
    'kur': dict(beam=None, sites=[('KURNS', 34.3900, 135.3500)], effort=1),
    'trigas': dict(beam=('bound', '≈', 'ill_pf1b', 0.01),
                   sites=[('Mainz', 49.9910, 8.2370), ('Pavia', 45.2010, 9.1370), ('Ljubljana', 46.0420, 14.4880),
                          ('Vienna', 48.2000, 16.3700)], effort=1),
    'pik': dict(beam=None, sites=[('PNPI', 59.5600, 30.1000)], effort=1),
    'ra10': dict(beam=('bound', '≲', 'ill_pf1b', 1.0), sites=[('Ezeiza', -34.8500, -58.5200)], effort=1),
    'closed_reactors': dict(beam=None, sites=[('BER II', 52.4100, 13.1300), ('Orphée', 48.7100, 2.1500),
                                              ('JEEP II', 59.9700, 11.0500), ('FiR-1', 60.1900, 24.8300),
                                              ('LENS', 39.1700, -86.5200)], effort=1),
    # ---- epithermal
    'bnct_reactor': dict(beam=('flux', 1e9, 'epithermal'), geom='1e9 n/cm²/s epithermal (IAEA design floor)',
                         sites=[('THOR', 24.7900, 120.9900), ('RA-6', -41.1300, -71.4000), ('LVR-15', 50.1800, 14.3100),
                                ('MITR', 42.3600, -71.0940)], effort=2,
                         next='Only after the fast candidates: ×3.6 per neutron, not ×100.'),
    'bnct_accel': dict(beam=('flux', 1e9, 'epithermal'), geom='1e9 n/cm²/s epithermal (moderated)',
                       sites=[('Southern Tohoku', 37.3900, 140.3600), ('Helsinki', 60.1900, 24.9500),
                              ('Tsukuba', 36.0800, 140.1100), ('Xiamen', 24.4800, 118.0900),
                              ('BINP Novosibirsk', 54.8500, 83.1000)], effort=2,
                       next='The unmoderated source behind the moderator is the real prize: see Birmingham.'),
    # ---- fast pulsed
    'ntof_ear2': dict(beam=('flux', 1e7 * 19290 / DAY, 'ntof'), geom='1e7 n/cm²/pulse, 19 290 pulses/day (average)',
                      sites=[('CERN n_TOF', 46.2340, 6.0460)], effort=4,
                      effort_note='Where the apparatus ran in 2026: data on disk, full Geant4 of the setup, analysis under way.',
                      links=[('The n_TOF campaign', '../x17/'), ('Analysis board', '../x17/analysis.html')],
                      next='The 2026 data analysis.', contact='home facility', updated='2026-10-20'),
    'ntof_ear1': dict(beam=('flux', 8e5 * 19290 / DAY, 'ntof'), geom='8e5 n/cm²/pulse at 185 m',
                      sites=[('CERN n_TOF', 46.2340, 6.0460)], effort=2),
    'ntof_near': dict(beam=None, sites=[('CERN n_TOF', 46.2340, 6.0460)], effort=1),
    'ganil_nfs': dict(beam=('flux', 3.518e8 / 50.0, 'nfs'), geom='3.5e8 n/s through the 50 cm² NFS spot at 50 µA',
                      sites=[('GANIL', 49.2120, -0.3640)], effort=4,
                      effort_note='Gate-2 fold, Geant4 X17 / IPC / beam campaigns incl. a forced-collision background run; reach with accidentals. ×2.2 short of ATOMKI (all E*), ×20 in the ATOMKI window.',
                      links=[('The GANIL/NFS study', 'ganil-nfs.html'),
                             ('Feasibility slides', '../notes/ganil-nfs-x17-feasibility.html')],
                      next='Cosmic veto and coincidence-window scan; ask GANIL about the current at 440 kHz.',
                      contact='question for GANIL drafted, not sent', updated='2026-10-19'),
    'csns_backn': dict(beam=('flux', 1.8e7 * 1.85, 'backn'), geom='1.8e7 n/cm²/s per 100 kW, 185 kW, Φ50 mm',
                       sites=[('CSNS', 22.9600, 113.9000)], effort=2),
    'lansce_wnr': dict(beam=('flux', 5e6 / 0.85, 'wnr'), geom='5e6 n/cm²/s above 1 MeV; split below 1 MeV estimated', est='the spectrum below 1 MeV and the beam size are estimates',
                       sites=[('LANSCE', 35.8740, -106.3240)], effort=2,
                       next='Ask LANSCE: the 30° flux below 1 MeV, beam size at ICE, micropulse spacing.',
                       contact='email drafted, not sent'),
    'gelina': dict(beam=('flux', 2.5e13 / (4 * math.pi * 1e6), 'ntof'), geom='2.5e13 n/s isotropic, 10 m (upper bound)', est='isotropic upper bound at 10 m',
                   sites=[('JRC Geel', 51.2177, 4.9739)], effort=2),
    'nelbe': dict(beam=('flux', 2.5e4, 'fission'), geom='2.5e4 n/cm²/s at the target', sites=[('HZDR', 51.0640, 13.9490)],
                  effort=2),
    'rpi': dict(beam=('bound', '≲', 'gelina', 1.0), sites=[('RPI', 42.7300, -73.6800)], effort=1),
    'kurns_linac': dict(beam=('bound', '≲', 'gelina', 1.0), sites=[('KURNS', 34.3900, 135.3500)], effort=1),
    'jparc_annri': dict(beam=('bound', '≲', 'csns_backn', 1.0), sites=[('J-PARC MLF', 36.4500, 140.6040)], effort=1),
    'iren': dict(beam=None, sites=[('JINR', 56.7400, 37.1900)], effort=1),
    # ---- fast CW
    'frm2_medapp': dict(beam=('flux', 3.2e8, 'fission'), geom='3.2e8 n/cm²/s at the irradiation position (field up to 20 × 30 cm)',
                        sites=[('FRM II', 48.2660, 11.6760)], effort=2,
                        effort_note='Scaled NFS model only. Top of the potential list with Birmingham.',
                        next='Geant4 soft-beam singles run (fission spectrum on the NFS geometry); ask FRM II for the restart date, MEDAPP access and space.',
                        contact='email drafted, not sent', updated='2026-10-20'),
    'birmingham': dict(beam=('flux', 4.8e12 / 4e4, 'li7pn'), geom='> 3e13 n/s, target shielded, capsule 2 m away (realistic)', est='the 0° yield (×2 the 4π average) is an estimate; no collimated port exists yet',
                       scen=[('unshielded, 1 m', ('flux', 4.8e12 / 1e4, 'li7pn'))],
                       sites=[('Birmingham', 52.4500, -1.9300)], effort=2,
                       effort_note='Scaled NFS model only. Operating today: the strongest candidate on the list.',
                       next='Geant4 soft-beam singles run (thick ⁷Li(p,n)); target shield and γ filter; ask for an unmoderated collimated port.',
                       contact='email drafted, not sent', updated='2026-10-20'),
    'saraf': dict(beam=('flux', 1e10 / 2500, 'keV'), geom='LiLiT, ~1e10 n/sr/s, capsule 0.5 m away', est='LiLiT yield into the forward cone estimated (~1e10 n/sr/s)',
                  scen=[('Phase II, d(40) 5 mA', ('flux', 100 * 3.518e8 / 50.0, 'nfs'))],
                  sites=[('SARAF', 31.9050, 34.6990)], effort=2),
    'franz': dict(beam=('flux', 7e10 / 2500, 'keV'), geom='~7e10 n/s forward (design), 0.5 m', est='design current; the 2 MeV stage is not built', sites=[('Frankfurt', 50.1730, 8.6300)],
                  effort=2),
    'lenos': dict(beam=('bound', '≈', 'birmingham', 1.0), sites=[('LNL', 45.3530, 11.9480)], effort=1,
                  next='Ask LNL whether LENOS is still planned.'),
    'bepn_cyc': dict(beam=('flux', 1e13 / 1e4, 'bepn'), geom='1e13 n/sr/s at 1 mA (guess), 1 m', est='the ⁹Be(p,n) thick-target yield and spectrum are guesses; no table found',
                     sites=[('Southern Tohoku', 37.3900, 140.3600), ('Kansai BNCT', 34.8500, 135.6000)], effort=2,
                     next='Find a thick-target ⁹Be(p,n) yield table; ask Sumitomo about an unmoderated port.'),
    'dd_gen': dict(beam=('flux', 3e11 / (4 * math.pi * 250 ** 2), 'dd'), geom='3e11 n/s, shielded, 2.5 m',
                   scen=[('unshielded, 1 m', ('flux', 3e11 / (4 * math.pi * 1e4), 'dd'))],
                   sites=[('Phoenix, Madison', 43.0700, -89.3600)], effort=2,
                   next='Ask Phoenix/SHINE about D-D above 1e12 n/s.'),
    'dt_gen': dict(beam=('flux', 4.6e13 / (4 * math.pi * 1e4), 'dt'), geom='4.6e13 n/s, 1 m',
                   sites=[('SHINE, Janesville', 42.6800, -89.0200), ('FNG Frascati', 41.8200, 12.6700)], effort=2),
    'maria_conv': dict(beam=None, sites=[('NCBJ Świerk', 52.1000, 21.3500)], effort=1),
    # ---- fast mono, low current
    'demokritos': dict(beam=('pairs', 504.0, 'tpn2'), geom='³H(p,n) at 2 MeV, lab flux, capsule 1.7 cm from the target, per µA',
                       sites=[('Demokritos', 37.9990, 23.8170)], effort=3,
                       effort_note='Neutron route: analytic study, closed (34 years to 3σ). The proton route p + ³H has a Geant4 study.',
                       links=[('Why the neutron beams are closed', '../notes/demokritos-neutron-beam.html'),
                              ('Proton route (Geant4)', '../notes/demokritos-x17-feasibility.html')],
                       next='Neutrons: none. Protons: systematics at S/B ≈ 1 %.', updated='2026-10-19'),
    'lnl_cn': dict(beam=('bound', '≲', 'demokritos', 4.0), sites=[('LNL', 45.3530, 11.9480)], effort=4,
                   effort_note='Geant4 study of the proton route, ⁷Li(p,e⁺e⁻)⁸Be (not neutrons): the ATOMKI ratio at 3σ in ~8 days at 1 µA.',
                   links=[('The LNL study', 'lnl.html'), ('3D: the arms around a Li target', 'lnl-setup-3d.html')],
                   next='As a neutron source: none (the target makes the pairs itself).', updated='2026-10-12'),
    'mono_labs': dict(beam=('bound', '≈', 'demokritos', 1.0),
                      sites=[('PTB', 52.2950, 10.4600), ('NPL', 51.4250, -0.3420), ('TUNL', 36.0010, -78.9400),
                             ('Ohio Edwards', 39.3240, -82.1000), ('PKU', 39.9900, 116.3100), ('Tohoku FNL', 38.2550, 140.8450),
                             ('Kyushu', 33.5970, 130.2180), ('AIST', 36.0600, 140.1300)], effort=1),
    'licorne': dict(beam=('bound', '≲', 'demokritos', 1.0), sites=[('IJCLab', 48.6990, 2.1730)], effort=1),
    # ---- high energy, future
    'high_e_qmn': dict(beam=None, sites=[('TSL', 59.8400, 17.6500), ('iThemba', -34.0240, 18.7180), ('RCNP', 34.8210, 135.5220)],
                       effort=1),
    'isis_chipir': dict(beam=None, sites=[('ISIS', 51.5720, -1.3150), ('LANSCE', 35.8740, -106.3240)], effort=1),
    'ifmif_dones': dict(beam=None, sites=[('Granada', 37.0600, -3.7600)], effort=1),
    'nephir': dict(beam=('bound', '≈', 'ganil_nfs', 1.0), sites=[('LNL', 45.3530, 11.9480)], effort=1),
    'csns2': dict(beam=('flux', 1.8e7 * 5.0, 'backn'), geom='500 kW', sites=[('CSNS', 22.9600, 113.9000)], effort=2),
    'ess_fast': dict(beam=None, sites=[('ESS', 55.7339, 13.2500)], effort=1),
    'minerva': dict(beam=None, sites=[('SCK CEN', 51.2180, 5.0900)], effort=1),
}

# A dated log for the page; newest first.
LOG = [
    ('2026-10-20', 'Dashboard started: 59 catalogue rows, crude X17/day for each, effort levels.'),
    ('2026-10-20', 'World survey: thermal class closed by the rate walls, pulsed white sources by duty; FRM II MEDAPP and Birmingham HF-ADNeF on the potential list.'),
    ('2026-10-19', 'GANIL/NFS: Geant4 reach with beam backgrounds, ×2.2 short of ATOMKI (all E*).'),
    ('2026-10-19', 'Demokritos: neutron beams on ³He closed (34 years to 3σ); proton route Geant4.'),
    ('2026-10-12', 'LNL proton route: ATOMKI ratio at 3σ in ~8 days at 1 µA (Geant4).'),
    ('2026-10-08', 'ILL PF1B: Geant4 verdict, ×3.2 short of the ⁸Be level per 50-day cycle.'),
]

CLASS_LABEL = {'cold/thermal': 'Cold / thermal', 'epithermal': 'Epithermal', 'fast pulsed': 'Fast, pulsed white',
               'fast CW': 'Fast, continuous', 'fast mono low-current': 'Fast, mono-energetic (µA)',
               'high-E': 'High energy (≫ 10 MeV)', 'future': 'Future / no beam yet'}


def headline(beam):
    """(x17/day, n/s on the capsule, IPC pairs/day, fraction of pairs from E_n ≤ 2.75 MeV, spectrum key)."""
    kind, val, spec = beam
    p, win = P[spec]
    if kind == 'pairs':
        pairs = val
        n = pairs / DAY / p
    else:
        n = val * A_CAP if kind == 'flux' else val
        pairs = n * p * DAY
    return dict(x17=pairs * X17_IPC, n_cap=n, ipc_day=pairs, win=win, spectrum=spec, spectrum_label=SPECTRA[spec][0])


def main():
    cat = pd.read_csv(HERE / 'facilities.csv')
    tri = pd.read_csv(OUT / 'triage.csv')
    missing = set(cat.key) - set(EXTRA)
    assert not missing, f'no EXTRA entry for {missing}'
    rows, flat = {}, []
    for r in cat.itertuples():
        e = EXTRA[r.key]
        d = dict(key=r.key, name=r.facility, site=r.site, kind=r.kind, beam=r.beam, cls=r.cls,
                 cls_label=CLASS_LABEL.get(r.cls, r.cls), status=r.status, number=r.number, verdict=r.verdict,
                 reason=r.reason, source=r.source, effort=e['effort'], effort_label=EFFORT[e['effort']],
                 effort_note=e.get('effort_note', ''), links=[dict(t=t, href=h) for t, h in e.get('links', [])],
                 next=e.get('next', ''), contact=e.get('contact', 'not contacted'), est=e.get('est', ''), updated=e.get('updated', '2026-10-20'),
                 geom=e.get('geom', ''), sites=[dict(name=n, lat=la, lon=lo) for n, la, lo in e['sites']])
        b = e['beam']
        if b and b[0] != 'bound':
            d.update(headline(b))
            d['scen'] = [dict(label=lab, **headline(sb)) for lab, sb in e.get('scen', [])]
        else:
            d.update(x17=None, scen=[])
        # model reach (best-throttle 50-day X17/IPC at 3σ, big plastics), every scenario the triage has
        t = tri[tri.key == r.key]
        d['reach'] = [dict(model=m.model, soft=_f(m.rho_soft), soft_flat=_f(m.rho_soft_flat), all=_f(m.rho_all),
                           floor=_f(m.rho_floor)) for m in t.itertuples() if isinstance(m.model, str) and m.model]
        d['reach'] = [x for x in d['reach'] if x['soft'] is not None]
        rows[r.key] = d
    for k, d in rows.items():              # bounds after every computed row exists
        b = EXTRA[k]['beam']
        if b and b[0] == 'bound':
            ref = rows[b[2]]
            d['bound'] = dict(op=b[1], ref=b[2], ref_name=ref['name'])
            d['x17'] = ref['x17'] * b[3]
            d['win'] = ref.get('win')
        flat.append(dict(key=k, name=d['name'], verdict=d['verdict'], effort=d['effort'], x17_per_day=d['x17'],
                         bound=d.get('bound', {}).get('op', ''), n_capsule=d.get('n_cap'), ipc_per_day=d.get('ipc_day'),
                         frac_window=d.get('win'), spectrum=d.get('spectrum')))
    doc = dict(generated=date.today().isoformat(), x17_ipc=X17_IPC, capsule='500 bar ³He, Ø2 cm × 8 cm, beam along the axis',
               window_En=WINDOW_EN, atomki=1.5e-3, effort_levels=EFFORT, log=[dict(date=a, text=b) for a, b in LOG],
               facilities=list(rows.values()))
    OUT.mkdir(exist_ok=True)
    pd.DataFrame(flat).sort_values('x17_per_day', ascending=False).to_csv(OUT / 'dashboard.csv', index=False,
                                                                          float_format='%.3g')
    SITE_JSON.parent.mkdir(parents=True, exist_ok=True)
    SITE_JSON.write_text(json.dumps(doc, ensure_ascii=False, separators=(',', ':'), allow_nan=False, default=_json), encoding='utf-8')
    print(pd.DataFrame(flat).sort_values('x17_per_day', ascending=False).to_string(index=False))
    print('->', SITE_JSON)


def _f(x):
    return None if x is None or not math.isfinite(float(x)) else float(x)


def _json(o):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    raise TypeError(type(o))


if __name__ == '__main__':
    main()
