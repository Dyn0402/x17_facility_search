#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ill_rates.py -- what the n_TOF thermal results say about running at the ILL.

    python ill/ill_rates.py            # print every table (+ cross-checks)
    python ill/ill_rates.py --write    # and write CSV/JSON to ill/out/

Self-contained: the nTof_x17 inputs (the Geant4 thermal contract, the ³He
pair cross sections) are carried as constants with their provenance.  When an
nTof_x17 checkout is found (``$NTOF_X17``, default ~/PycharmProjects/nTof_x17)
every one of them is re-derived and compared on each run.

ONE IDEA CARRIES THE WHOLE PROJECTION.  Every neutron the ILL can give us is
below ~0.1 eV, which is exactly the regime of n_TOF's >1 ms gate.  There, all
the numbers that matter are ratios of 1/v cross sections, so they are the same
per neutron whatever the wavelength:

  * ³He absorbs essentially every neutron that enters (optical depth ~150 at
    500 bar, still >~5 for a few-bar cell at 4 Å), and the fraction of
    absorptions that are radiative is sigma_ng/sigma_np = 55 ub / 5333 b,
    1.03e-8, at any wavelength;
  * the pair yield per absorption is fixed by the two s-wave channels
    (:mod:`sept26_prelim_analysis.ipc_channels`), at any wavelength.

So nothing about the SIGNAL changes between n_TOF's gate and a reactor beam,
except how many neutrons per day there are.  What changes the BACKGROUND is that
a thin wall is not opaque: its capture probability per neutron goes as
``n sigma_th t <lambda/lambda_th>``, and a 4 Å beam carries ~3.6x the 1/v weight
of n_TOF's in-gate spectrum.  That one factor is the bridge from the Geant4
thermal campaign (``MX17_Full_Geant``, nose-first, 1e9 neutrons) to the ILL.

TWO CONFIGURATIONS, deliberately:

  A  ``ntof_capsule``  the as-built 500 bar capsule, unchanged.  Every number
     is the Geant4 thermal-accounting contract scaled by the 1/v weight.  This
     is the "pack the experiment in a truck" option and it is *measured* (by
     simulation) rather than estimated.
  B  ``cell_<mat>``    a low-pressure ³He cell with a thin entrance window.
     At a reactor the gas does not need 500 bar to be opaque, so the 5.5 mm Al
     nose is no longer forced on us.  The background ladder is the same Geant4
     contract scaled by the window's capture probability relative to the
     capsule's -- an ANALYTIC SCALING, labelled as such everywhere, which is
     precisely what the lxplus campaign in GEANT_PLAN.md replaces.

WHAT IS NOT HERE, ON PURPOSE.  No ambient guide-hall background, no cosmic
two-arm rate, no beam-borne gamma: all three are site properties that do not
scale from n_TOF and are listed as open in README.md.  Configuration B makes
the capsule background small enough that these become the floor, so they are
the first thing to measure, not the last.

The X17 yield uses the rate table's ``X17 / IPC = 2.5e-2``, applied to the M1
(1+) pairs only, because a vector, axial or pseudoscalar X17 cannot be emitted
from the 0+ (1S0) entrance channel.  It is a REFERENCE NORMALISATION, not a
prediction; the sensitivity table quotes the smallest ratio a cycle can see so
that the conclusion does not hang on it.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
#: the nTof_x17 checkout the constants below were copied from -- optional
NTOF_X17 = Path(os.environ.get('NTOF_X17',
                               Path.home() / 'PycharmProjects' / 'nTof_x17'))

SCHEMA = 'x17_facility_search/ill/ill_rates/1'

# --------------------------------------------------------------------------- #
# physical constants
# --------------------------------------------------------------------------- #
LAMBDA_TH_A = 1.7982            # Å, v = 2200 m/s
SECONDS_PER_DAY = 86400.0
CYCLE_DAYS = 50.0               # a typical ILL cycle (2026: 48, 56, 58 days)
BARN = 1e-24                    # cm^2
T_HALF_TRITIUM_S = 12.32 * 365.25 * SECONDS_PER_DAY

# --------------------------------------------------------------------------- #
# the n_TOF side: the Geant4 thermal-accounting contract
# --------------------------------------------------------------------------- #
#: ntof_athens_26/data/thermal_accounting/accounting.json, per neutron ENTERING
#: the capsule (gun r < 11.5 mm), campaign neutrons_thermal_trig_2cm_nose,
#: 1e9 primaries, E_n in [1 meV, 2 eV].  Copied rather than read so this module
#: runs without the athens tree; ``check_contract()`` re-reads and compares.
ACCOUNTING = NTOF_X17 / 'ntof_athens_26' / 'data' / 'thermal_accounting' / 'accounting.json'
NTOF = dict(
    wall_al_captures=4.989e-3,       # F1.ncapture.wall_al
    wall_cfrp_captures=2.561e-4,     # F1.ncapture.wall_cfrp
    captures_elsewhere=2.877e-3,     # F1.ncapture.elsewhere (scattered out)
    gap_charge=1.691e-4,             # F2.charged_in_detector (>=1 keV, prompt)
    trigger_legs=3.186e-5,           # F5.legs (wall AND plastic, 0.5 MIP)
    pairtags_strict=2.885e-8,        # F5.pairtags (legs in two arms) -- 26 MC events
    capsule_ext_pairs_in_gap=2.581e-5,  # F4.external.al27
)
#: the looser production trigger menu ("2 SiPM >= 0.5 MIP + >= 1 plastic at
#: 1.0 MIP"): 1.8 pair-tags/pulse at 4.284e6 in-gate n/pulse
#: (MX17_Full_Geant/CAMPAIGN_STATUS.md, 2026-07-19 headline).  Used for the
#: trigger-rate limit because it is the HIGHER rate -- conservative.
NTOF_PAIRTAGS_MENU = 1.8 / 4.284e6
#: <sqrt(E_th/E)> of the EAR2 in-gate flux (flux_n_pulse_NOisolet_100bpd,
#: 1 meV - 2 eV) -- the 1/v weight of the spectrum the contract was made with.
#: Check: 5.5 mm Al nose x n sigma_th x 0.651 = 4.96e-3 against the contract's
#: 4.99e-3 Al captures per neutron.  ``ntof_lambda_weight()`` recomputes it.
K_NTOF = 0.651
#: in-gate neutrons entering the capsule per day at n_TOF (nominal 19 290
#: pulses/day, 4.284e6 n/pulse in the >1 ms window, 90.1 % inside r < 11.5 mm)
NTOF_ENTERING_PER_DAY = 4.284e6 * 0.90121 * 19290
#: the nose the capsule's own pairs convert in -- 5.5 mm Al, X0 = 8.897 cm
NTOF_NOSE_T_OVER_X0 = 0.55 / 8.897
#: pair-tag efficiency of the recommended thermal menu (signal X17), and the
#: MM-double (both legs in a drift gap) ceiling, nose-first geometry
EPS_X17_MENU = (0.040, 0.070)
EPS_MM_DOUBLE = 0.278

# --------------------------------------------------------------------------- #
# the ³He side -- copied from nTof_x17 sept26_prelim_analysis.ipc_channels
# --------------------------------------------------------------------------- #
X17_PER_M1_PAIR_REF = 2.5e-2     # rate table's X17/IPC -- REFERENCE ONLY
SIGMA_NP_B = 5333.0              # ³He(n,p) at 25.3 meV, ENDF/B
SIGMA_NGAMMA_UB = 55.0           # ³He(n,γ), Wervelman et al. 1991 (55 +- 3)
#: ipc_channels.thermal_channels() (Born pair spectra from ipc_born, sampled):
#: pair cross sections and the part above 109 deg, in ub.  M1 = 55 ub x
#: alpha_pair(M1, 20.58 MeV); E0 = the 1S0 -> 0+ monopole estimate (an order
#: of magnitude: see nTof_x17 sept26_prelim_analysis/IPC_MISSING.md).
HE3_PAIRS_UB = dict(m1=0.2014, e0=0.05519, m1_gt109=0.009268, e0_gt109=0.006294)


def he3_per_absorption() -> dict:
    """Everything the gas makes, per neutron it absorbs.  Wavelength-free."""
    per = 1e-6 / SIGMA_NP_B                    # ub -> per (n,p) absorption
    h = HE3_PAIRS_UB
    return dict(
        ngamma=SIGMA_NGAMMA_UB * per,
        pairs_m1=h['m1'] * per,
        pairs_e0=h['e0'] * per,
        pairs_total=(h['m1'] + h['e0']) * per,
        pairs_gt109=(h['m1_gt109'] + h['e0_gt109']) * per,
        x17_ref=X17_PER_M1_PAIR_REF * h['m1'] * per,
        e0_share=h['e0'] / (h['m1'] + h['e0']),
    )


def check_he3() -> list[str]:
    """Re-derive HE3_PAIRS_UB from nTof_x17's ipc_channels, if it is there."""
    if not (NTOF_X17 / 'sept26_prelim_analysis' / 'ipc_channels.py').exists():
        return ['nTof_x17 not found -- ³He constants not re-checked']
    sys.path.insert(0, str(NTOF_X17))
    try:
        from sept26_prelim_analysis import ipc_channels
        t = ipc_channels.thermal_channels().set_index('channel')
    except Exception as e:               # a broken checkout must not stop us
        return [f'ipc_channels import failed ({e!r}) -- not re-checked']
    got = dict(m1=t.loc['M1', 'sigma_pair_ub'], e0=t.loc['E0', 'sigma_pair_ub'],
               m1_gt109=t.loc['M1', 'pairs_gt109_ub'],
               e0_gt109=t.loc['E0', 'pairs_gt109_ub'])
    # the >109 deg parts are Monte Carlo fractions: 2 % tolerance
    return [f'{k}: ipc_channels {got[k]:.4g} vs copied {v:.4g}'
            for k, v in HE3_PAIRS_UB.items() if abs(got[k] / v - 1) > 0.02]


# --------------------------------------------------------------------------- #
# the ILL side
# --------------------------------------------------------------------------- #
@dataclass
class Beam:
    key: str
    label: str
    capture_flux: float     # thermal-equivalent n/cm^2/s at nominal power
    mean_lambda_A: float    # sets capture-flux / particle-flux
    max_area_cm2: float     # the whole beam
    source: str

    @property
    def k(self) -> float:
        """1/v weight relative to 2200 m/s (= capture flux / particle flux)."""
        return self.mean_lambda_A / LAMBDA_TH_A

    @property
    def particle_flux(self) -> float:
        return self.capture_flux / self.k


BEAMS = {
    'PF1B': Beam('PF1B', 'PF1B (H113, cold, unpolarised)', 2.0e10, 4.25,
                 6 * 20, 'ILL PF1B characteristics: 2e10 n/cm2/s capture flux, '
                 '6x20 cm2, mean wavelength 4.0-4.5 Å'),
    'PF1B_pol': Beam('PF1B_pol', 'PF1B polarised (99.7 %)', 3.0e9, 4.25,
                     6 * 8, 'ILL PF1B characteristics: 3e9 n/cm2/s, 6x8 or 3x4.5 cm2'),
    'FIPPS': Beam('FIPPS', 'FIPPS (H22, thermal pencil)', 1.0e8 * 1.3, 2.3,
                  math.pi * 0.75 ** 2,
                  'ILL FIPPS: 1e8 n/cm2/s at target, halo-free, 1.5 cm '
                  'diameter; wavelength on H22 assumed ~2.3 Å'),
}
#: the flux above is quoted at full power; 2025-26 cycles ran 41-56 MW
NOMINAL_MW = 57.0
CYCLE_201_MW = 46.2


@dataclass
class Window:
    key: str
    label: str
    sigma_b: float          # thermal (2200 m/s) capture cross section
    n_per_cm3: float
    x0_cm: float
    t_mm: float
    sn_mev: float           # hardest capture photon available
    note: str
    #: for a compound (glass): the thermal macroscopic capture cross section,
    #: cm^-1, used instead of n*sigma when set
    sigma_macro_cm: float = 0.0

    def captures_per_neutron(self, k: float) -> float:
        sig = self.sigma_macro_cm or self.n_per_cm3 * self.sigma_b * BARN
        return sig * self.t_mm / 10 * k

    @property
    def t_over_x0(self) -> float:
        return self.t_mm / 10 / self.x0_cm


#: candidate entrance windows for a low-pressure cell.  sigma: Mughabghab /
#: NIST thermal capture; X0: PDG.  Be is transparent to coherent scattering
#: above its 3.96 Å Bragg cutoff, which is most of PF1B's beam.
WINDOWS = {
    'al05': Window('al05', '0.5 mm Al', 0.231, 6.026e22, 8.897, 0.5, 7.725,
                   'the cheap default; same lines as the capsule'),
    'si05': Window('si05', '0.5 mm Si (single crystal)', 0.171, 4.994e22, 9.370,
                   0.5, 8.474, 'transparent, but harder line'),
    'mg05': Window('mg05', '0.5 mm Mg', 0.063, 4.306e22, 14.39, 0.5, 11.09,
                   '25Mg line at 11.1 MeV'),
    'be05': Window('be05', '0.5 mm Be', 0.0076, 1.236e23, 35.28, 0.5, 6.812,
                   'standard pressure-window material'),
    'c05': Window('c05', '0.5 mm graphite / CVD diamond', 0.00350, 1.108e23,
                  19.32, 0.5, 4.946, 'softest line; diamond is 1.6x denser'),
    # --- what a POLARISED cell is made of (metal walls relax 3He; glass and
    # Si do not).  GE180: ~60 SiO2 / 14 Al2O3 / 18 BaO / 6.5 CaO wt %,
    # 2.76 g/cm3 -> Sigma_th ~ 6.8e-3 /cm (Si 2.8, Ba 2.1, Al 1.1, Ca 0.8),
    # X0 ~ 7.2 cm.  Fused quartz: Si only, 3.8e-3 /cm, X0 12.3 cm.  Treat the
    # glass compositions as +-20 %.
    'ge180_1': Window('ge180_1', '1 mm GE180 glass (polarised cell)', 0, 0, 7.2,
                      1.0, 9.2, 'boron-free aluminosilicate; Ba lines',
                      sigma_macro_cm=6.8e-3),
    'quartz_1': Window('quartz_1', '1 mm fused quartz (polarised cell)', 0, 0,
                       12.3, 1.0, 8.474, 'the ILL quartz cell type',
                       sigma_macro_cm=3.8e-3),
}


def ntof_wall_captures() -> float:
    return NTOF['wall_al_captures'] + NTOF['wall_cfrp_captures']


# --------------------------------------------------------------------------- #
# per-neutron ladders
# --------------------------------------------------------------------------- #
def ladder(config: str, beam: Beam) -> dict:
    """Detector-side background per neutron absorbed in the gas.

    ``config`` is ``ntof_capsule`` or a key of :data:`WINDOWS`.
    """
    kr = beam.k / K_NTOF
    if config == 'ntof_capsule':
        s_cap = kr
        s_conv = kr
        wall = ntof_wall_captures() * kr
        label = 'as-built 500 bar capsule (Geant4 contract x 1/v weight)'
        basis = 'Geant4, rescaled'
    else:
        w = WINDOWS[config]
        wall = w.captures_per_neutron(beam.k)
        s_cap = wall / ntof_wall_captures()
        s_conv = s_cap * w.t_over_x0 / NTOF_NOSE_T_OVER_X0
        label = f'low-pressure cell, {w.label} window (analytic scaling)'
        basis = 'analytic scaling of the Geant4 contract'
    return dict(
        config=config, label=label, basis=basis,
        wall_captures=wall,
        captures_elsewhere=NTOF['captures_elsewhere'] * s_cap,
        gap_charge=NTOF['gap_charge'] * s_cap,
        trigger_legs=NTOF['trigger_legs'] * s_cap,
        pairtags=NTOF_PAIRTAGS_MENU * s_cap,
        wall_ext_pairs_in_gap=NTOF['capsule_ext_pairs_in_gap'] * s_conv,
        # wide-angle (>109 deg) INTERNAL pairs from wall captures: 2.1-3.8e-4
        # per 27Al capture (ipc_aluminium, all-M1..all-E1 secondaries); the
        # midpoint is applied to every material -- Al-like, flagged.
        wall_int_pairs_gt109=wall * 3.0e-4,
    )


# --------------------------------------------------------------------------- #
# limits on the neutron rate
# --------------------------------------------------------------------------- #
DREAM_MAX_HZ = 1.0e3        # ~1.2 kHz seen in-burst at n_TOF; continuous: unmeasured
MM_WINDOW_S = 1.0e-6        # 30 mm drift at ~44 um/ns + shaping
MM_MAX_OCC = 0.10           # tolerated probability of a second event per chamber
N_ARMS = 4


def rate_limits(L: dict, beam: Beam, area_cm2: float,
                power_mw: float = NOMINAL_MW) -> dict:
    """Absorbed-neutron rate allowed by each constraint, n/s."""
    beam_rate = beam.particle_flux * min(area_cm2, beam.max_area_cm2) \
        * power_mw / NOMINAL_MW
    trig = DREAM_MAX_HZ / L['pairtags']
    mm = MM_MAX_OCC / (MM_WINDOW_S * L['gap_charge'] / N_ARMS)
    lim = dict(beam=beam_rate, trigger=trig, micromegas=mm)
    k = min(lim, key=lim.get)
    return dict(limits=lim, binding=k, rate=lim[k])


def yields(rate: float, he3: dict, L: dict) -> dict:
    day = rate * SECONDS_PER_DAY
    cyc = day * CYCLE_DAYS
    n_t = rate * CYCLE_DAYS * SECONDS_PER_DAY        # tritons made per cycle
    lam = math.log(2) / T_HALF_TRITIUM_S
    return dict(
        absorbed_per_day=day,
        ntof_days_per_day=day / NTOF_ENTERING_PER_DAY,
        he3_ngamma_per_day=day * he3['ngamma'],
        ipc_per_day=day * he3['pairs_total'],
        ipc_gt109_per_day=day * he3['pairs_gt109'],
        x17_ref_per_day=day * he3['x17_ref'],
        x17_ref_detected_per_cycle_lo=cyc * he3['x17_ref'] * EPS_X17_MENU[0],
        x17_ref_detected_per_cycle_hi=cyc * he3['x17_ref'] * EPS_X17_MENU[1],
        wall_int_gt109_per_day=day * L['wall_int_pairs_gt109'],
        wall_over_he3_gt109=L['wall_int_pairs_gt109'] / he3['pairs_gt109'],
        trigger_hz=rate * L['pairtags'],
        mm_hz_per_arm=rate * L['gap_charge'] / N_ARMS,
        legs_hz=rate * L['trigger_legs'],
        tritium_GBq_per_cycle=n_t * lam / 1e9,
        # trigger-level purity: X17 (reference) in the menu against every
        # pair-tag the menu fires on.  Wall INTERNAL pairs carry <= 6.7 MeV
        # between both legs and cannot satisfy a >=~4 MeV-per-leg menu, so the
        # pair-tags (92 % two Compton photons of one capture) are the wall
        # background that reaches the offline analysis.
        s_over_b_trigger=he3['x17_ref'] * EPS_X17_MENU[0] / L['pairtags'],
    )


def min_ratio_3sigma(rate: float, he3: dict, days: float = CYCLE_DAYS,
                     eps: float = EPS_X17_MENU[0]) -> float:
    """Smallest X17/IPC(M1) a run can see at 3 sigma against the ³He wide-angle
    continuum ALONE (same efficiency for both).  A floor: any wall pair that
    survives the cuts only raises it."""
    n = rate * days * SECONDS_PER_DAY * eps
    b = n * he3['pairs_gt109']
    return 3 * math.sqrt(b) / (n * he3['pairs_m1'])


# --------------------------------------------------------------------------- #
# polarised option
# --------------------------------------------------------------------------- #
def polarised(p_he: float, p_n: float = 1.0, eps_t: float = 0.0) -> dict:
    """Spin-selected entrance channel with polarised ³He (and neutrons).

    Physics: ³He(n,p) and the E0 pairs go through the singlet 0+ (¹S₀) only;
    the (n,γ) and the M1 pairs through the triplet 1+ (³S₁) only.  For a
    neutron with spin along the ³He polarisation axis the singlet fraction of
    its n-³He spin states is f_s = (1 - P)/4; against it, (1 + P)/4
    (unpolarised: 1/4).  In an OPAQUE cell every neutron is absorbed, so the
    yield per absorbed neutron is the ratio of the two channels' cross
    sections for that spin state:

        M1 gain  G(f_s) = (4/3)(1 - f_s) / (4 f_s (1 - 3 eps/4) + (1 - f_s) eps)

    relative to unpolarised, with ``eps_t`` = sigma_triplet(n,p) / sigma_0
    (Passell & Schermer 1966: consistent with 0, ~3 % precision; spin-filter
    practice treats it as 0).  A finite eps_t caps the gain at high P.

    Returned:
      parallel / antiparallel  -- a neutron with spin along / against ³He
      unpolarised_beam_m1_gain -- the plain average: what an UNPOLARISED beam
                                  on a polarised opaque cell gives (no
                                  neutron polariser needed; no asymmetry)
      m1_contrast              -- parallel / antiparallel, i.e. what flipping a
                                  polarised beam does; p_n < 1 dilutes it
      parallel_length_factor   -- how much longer the absorption length is for
                                  the parallel neutrons (cell length driver)
    """
    def gain(fs):
        return (4 / 3) * (1 - fs) / (4 * fs * (1 - 0.75 * eps_t) + (1 - fs) * eps_t)

    def abs_rel(fs):        # sigma_abs / sigma_0
        return 4 * fs * (1 - 0.75 * eps_t) + (1 - fs) * eps_t

    fs_par, fs_anti = (1 - p_he) / 4, (1 + p_he) / 4
    g_par, g_anti = gain(fs_par), gain(fs_anti)
    # a beam of polarisation p_n: (1+p_n)/2 parallel, (1-p_n)/2 antiparallel
    up, dn = (1 + p_n) / 2, (1 - p_n) / 2
    g_beam_plus = up * g_par + dn * g_anti
    g_beam_minus = dn * g_par + up * g_anti
    return dict(
        p_he=p_he, p_n=p_n, eps_t=eps_t,
        parallel_m1_gain=g_par, antiparallel_m1_gain=g_anti,
        parallel_abs_xs_rel=abs_rel(fs_par), antiparallel_abs_xs_rel=abs_rel(fs_anti),
        parallel_length_factor=1 / abs_rel(fs_par),
        unpolarised_beam_m1_gain=(g_par + g_anti) / 2,
        beam_spin_plus_m1_gain=g_beam_plus, beam_spin_minus_m1_gain=g_beam_minus,
        m1_contrast=g_beam_plus / g_beam_minus,
    )


def polarised_table() -> pd.DataFrame:
    """The polarised option over the range the ILL can actually deliver."""
    rows = []
    for p_he in (0.6, 0.7, 0.75, 0.8, 0.85):
        for eps in (0.0, 0.01, 0.03):
            rows.append(polarised(p_he, p_n=0.997, eps_t=eps))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# scenarios
# --------------------------------------------------------------------------- #
#: (name, config, beam, beam spot cm^2, reactor MW[, rate cap n/s])
#: The cap is a deliberate design point: configuration B's detector-limited
#: ceiling ignores ambient, cosmic and beam-borne backgrounds that do not
#: scale from n_TOF, so 1e10 n/s is what a first proposal should assume.
DESIGN_RATE_B = 1.0e10
SCENARIOS = [
    ('A: capsule @ PF1B', 'ntof_capsule', 'PF1B', math.pi * 1.0 ** 2, NOMINAL_MW),
    ('A: capsule @ FIPPS', 'ntof_capsule', 'FIPPS', math.pi * 0.75 ** 2, NOMINAL_MW),
    ('B: Al-window cell @ PF1B', 'al05', 'PF1B', 20.0, NOMINAL_MW),
    ('B: Be-window cell @ PF1B', 'be05', 'PF1B', 20.0, NOMINAL_MW),
    ('B: C-window cell @ PF1B', 'c05', 'PF1B', 20.0, NOMINAL_MW),
    ('B: Be-window cell @ PF1B, 46 MW', 'be05', 'PF1B', 20.0, CYCLE_201_MW),
    ('B: Be-window cell @ PF1B, design point', 'be05', 'PF1B', 20.0,
     CYCLE_201_MW, DESIGN_RATE_B),
]


def scenario_table() -> pd.DataFrame:
    he3 = he3_per_absorption()
    rows = []
    for name, cfg, bk, area, mw, *cap in SCENARIOS:
        b = BEAMS[bk]
        L = ladder(cfg, b)
        R = rate_limits(L, b, area, mw)
        if cap and cap[0] < R['rate']:
            R = dict(R, rate=cap[0], binding='design cap')
        Y = yields(R['rate'], he3, L)
        rows.append(dict(
            scenario=name, config=cfg, beam=bk, spot_cm2=area, power_mw=mw,
            basis=L['basis'],
            wall_captures_per_n=L['wall_captures'],
            limit_beam=R['limits']['beam'], limit_trigger=R['limits']['trigger'],
            limit_mm=R['limits']['micromegas'], binding=R['binding'],
            rate=R['rate'], **Y,
            min_ratio_3sigma_cycle=min_ratio_3sigma(R['rate'], he3)))
    # n_TOF's own thermal gate, for scale
    L = ladder('ntof_capsule', Beam('nTOF', 'n_TOF EAR2 >1 ms', 0, K_NTOF * LAMBDA_TH_A, 0, ''))
    r = NTOF_ENTERING_PER_DAY / SECONDS_PER_DAY
    Y = yields(r, he3, L)
    rows.append(dict(scenario='n_TOF EAR2, >1 ms gate (reference)',
                     config='ntof_capsule', beam='nTOF', spot_cm2=np.nan,
                     power_mw=np.nan, basis='Geant4',
                     wall_captures_per_n=ntof_wall_captures(),
                     limit_beam=r, limit_trigger=np.nan, limit_mm=np.nan,
                     binding='beam (duty cycle)', rate=r, **Y,
                     min_ratio_3sigma_cycle=min_ratio_3sigma(r, he3)))
    return pd.DataFrame(rows)


def rate_scan(configs=('ntof_capsule', 'al05', 'be05', 'c05'),
              rates=None) -> pd.DataFrame:
    """X17 (reference) detected per cycle against absorbed rate, per config,
    with each config's own ceiling -- the figure's table."""
    he3 = he3_per_absorption()
    rates = np.logspace(6, 12, 61) if rates is None else rates
    rows = []
    b = BEAMS['PF1B']
    for cfg in configs:
        L = ladder(cfg, b)
        R = rate_limits(L, b, 1e9)        # detector limits only
        for r in rates:
            rows.append(dict(config=cfg, rate=r,
                             allowed=r <= min(R['limits']['trigger'],
                                              R['limits']['micromegas']),
                             x17_det_cycle=r * CYCLE_DAYS * SECONDS_PER_DAY
                             * he3['x17_ref'] * EPS_X17_MENU[0],
                             min_ratio=min_ratio_3sigma(r, he3)))
    return pd.DataFrame(rows)


def window_table() -> pd.DataFrame:
    b = BEAMS['PF1B']
    rows = [dict(window='n_TOF capsule (5.5 mm Al nose + CFRP)',
                 captures_per_n=ntof_wall_captures() * b.k / K_NTOF,
                 t_over_x0=NTOF_NOSE_T_OVER_X0, sn_mev=7.725)]
    for w in WINDOWS.values():
        rows.append(dict(window=w.label, captures_per_n=w.captures_per_neutron(b.k),
                         t_over_x0=w.t_over_x0, sn_mev=w.sn_mev))
    t = pd.DataFrame(rows)
    he3 = he3_per_absorption()
    t['over_he3_ngamma'] = t.captures_per_n / he3['ngamma']
    t['vs_capsule'] = t.captures_per_n / t.captures_per_n.iloc[0]
    return t


def he3_cell_design(lambdas_A=(2.0, 4.25, 6.0), pressures_bar=(0.25, 1, 3, 10)):
    """1/e absorption length of ³He gas, cm, at 293 K."""
    rows = []
    for p in pressures_bar:
        n = 2.505e19 * p                       # cm^-3, ideal gas at 293 K
        for lam in lambdas_A:
            mu = n * SIGMA_NP_B * BARN * lam / LAMBDA_TH_A
            rows.append(dict(pressure_bar=p, lambda_A=lam, abs_length_cm=1 / mu))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# checks
# --------------------------------------------------------------------------- #
def ntof_lambda_weight() -> float | None:
    """Recompute K_NTOF from the EAR2 flux file, if it is reachable."""
    f = Path.home() / 'CLionProjects/MX17_Full_Geant/data/fluxEAR2-Ph3_in_different_units.root'
    try:
        import uproot
        w, e = uproot.open(f)['flux_n_pulse_NOisolet_100bpd'].to_numpy()
    except Exception:
        return None
    lo, hi = e[:-1], e[1:]
    m = (hi > 1e-3) & (lo < 2.0)
    c = np.sqrt(lo * hi)[m]
    return float(np.sum(w[m] * np.sqrt(0.0253 / c)) / w[m].sum())


def check_contract() -> list[str]:
    """Compare the copied constants against the contract on disk."""
    msgs = []
    try:
        d = json.load(open(ACCOUNTING))
    except OSError:
        return ['nTof_x17 accounting.json not found -- contract not re-checked']
    N = d['normalisation']['neutrons_entering_capsule']
    nodes = {n['id']: n for n in d['nodes'] + d['trigger_nodes']}
    for key, nid in (('wall_al_captures', 'F1.ncapture.wall_al'),
                     ('wall_cfrp_captures', 'F1.ncapture.wall_cfrp'),
                     ('captures_elsewhere', 'F1.ncapture.elsewhere'),
                     ('gap_charge', 'F2.charged_in_detector'),
                     ('trigger_legs', 'F5.legs'),
                     ('pairtags_strict', 'F5.pairtags'),
                     ('capsule_ext_pairs_in_gap', 'F4.external.al27')):
        v = nodes[nid]['weight'] / N
        if abs(v / NTOF[key] - 1) > 0.01:
            msgs.append(f'{key}: contract {v:.4e} vs copied {NTOF[key]:.4e}')
    k = ntof_lambda_weight()
    if k is not None and abs(k / K_NTOF - 1) > 0.01:
        msgs.append(f'K_NTOF: flux file {k:.4f} vs copied {K_NTOF}')
    return msgs


def summary() -> dict:
    he3 = he3_per_absorption()
    return dict(schema=SCHEMA, he3_per_absorption=he3,
                beams={k: dict(asdict(b), k=b.k, particle_flux=b.particle_flux)
                       for k, b in BEAMS.items()},
                k_ntof=K_NTOF, ntof_entering_per_day=NTOF_ENTERING_PER_DAY,
                limits=dict(dream_max_hz=DREAM_MAX_HZ, mm_window_s=MM_WINDOW_S,
                            mm_max_occ=MM_MAX_OCC),
                eps_x17_menu=EPS_X17_MENU, x17_per_m1_pair_ref=X17_PER_M1_PAIR_REF,
                polarised={str(p): polarised(p) for p in (0.7, 0.8)},
                contract_check=check_contract(), he3_check=check_he3())


def out_dir() -> Path:
    """ill/out/ -- small (a page, two PNGs, CSVs) and kept with the code, as
    ganil_nfs/data is.  $ILL_OUT overrides."""
    p = Path(os.environ.get('ILL_OUT', HERE / 'out'))
    p.mkdir(parents=True, exist_ok=True)
    return p


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    ap.add_argument('--write', action='store_true')
    a = ap.parse_args()
    pd.set_option('display.width', 250)
    fmt = lambda x: f'{x:.3g}'  # noqa: E731

    S = summary()
    print('CONTRACT CHECK:', S['contract_check'] or 'all constants match')
    print('³He CHECK:     ', S['he3_check'] or 'all constants match')
    print('\n³He, PER ABSORBED NEUTRON (any wavelength)')
    for k, v in S['he3_per_absorption'].items():
        print(f'  {k:<14s} {v:.3e}')
    print('\nBEAMS')
    for k, b in BEAMS.items():
        print(f'  {k:<9s} k = {b.k:.2f}  particle flux {b.particle_flux:.2e} n/cm2/s'
              f'  x {b.max_area_cm2:.0f} cm2 = {b.particle_flux * b.max_area_cm2:.2e} n/s')
    print('\nWINDOWS at PF1B, per neutron')
    print(window_table().to_string(index=False, float_format=fmt))
    print('\n³He ABSORPTION LENGTH, cm')
    print(he3_cell_design().pivot(index='pressure_bar', columns='lambda_A',
                                  values='abs_length_cm').to_string(float_format=fmt))
    T = scenario_table()
    print('\nSCENARIOS')
    cols = ['scenario', 'rate', 'binding', 'ntof_days_per_day', 'x17_ref_per_day',
            'x17_ref_detected_per_cycle_lo', 'x17_ref_detected_per_cycle_hi',
            'ipc_gt109_per_day', 'wall_over_he3_gt109', 'trigger_hz',
            'mm_hz_per_arm', 'tritium_GBq_per_cycle', 's_over_b_trigger',
            'min_ratio_3sigma_cycle']
    print(T[cols].to_string(index=False, float_format=fmt))
    print('\nLIMITS (absorbed n/s)')
    print(T[['scenario', 'limit_beam', 'limit_trigger', 'limit_mm']]
          .to_string(index=False, float_format=fmt))
    print('\nPOLARISED (P_n = 0.997, PF1B)')
    print(polarised_table().to_string(index=False, float_format=fmt))

    if a.write:
        od = out_dir()
        T.to_csv(od / 'scenarios.csv', index=False)
        window_table().to_csv(od / 'windows.csv', index=False)
        he3_cell_design().to_csv(od / 'he3_absorption_length.csv', index=False)
        rate_scan().to_csv(od / 'rate_scan.csv', index=False)
        polarised_table().to_csv(od / 'polarised.csv', index=False)
        json.dump(S, open(od / 'summary.json', 'w'), indent=1, default=float)
        print(f'\nwrote -> {od}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
