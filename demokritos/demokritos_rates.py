#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
demokritos_rates.py -- what the MX17 apparatus would see at the Demokritos Tandem.

    python demokritos/demokritos_rates.py            # tables -> demokritos/out/*.csv, figures
    python demokritos/demokritos_rates.py --quick    # tables only, small MC

The case is the ATOMKI 4He anomaly, 3H(p,e+e-)4He, on a Ti-tritide target.
A sub-MeV proton is captured on 3H and makes 4He at E* = Q + E_cm
(Q = 19.814 MeV), which decays by a real gamma (direct E1 capture), by internal
pair creation, by E0 pairs from the 20.21 MeV 0+ resonance, or -- the claim --
by an X17 (ATOMKI: B_x = Gamma_X/Gamma_gamma = 5.1(13)e-6, PRC 104, 044003).
Below E_p = 1.019 MeV the 3H(p,n) channel is closed: no neutrons.

Everything here is analytic or a toy MC, anchored to data where data exist.
Every anchor is printed as a CHECK line:

  cross section    the Hahn et al. (PRC 51, 1624, 1995) S-factor fit,
                   S(E) = 1.30e-6 MeV b (1 + 25 E + 38.8 E^2), E_cm in MeV, as
                   fitted in arXiv:physics/9910011 Table 1 to the 0.1-0.75 MeV
                   data.  Used up to 1.0 MeV (extrapolated above 0.75 MeV).
                   CHECKed against ATOMKI's "about 2 ub/sr at 900 keV".
  E0 pairs         single-level Breit-Wigner for the 20.21 MeV 0+ (Gamma = 0.50
                   MeV, Gamma_p = Gamma below the n threshold) with the pair width
                   from M(E0) = 1.53 fm^2 (nTof_x17 ipc_born / ipc_channels).
                   An order-of-magnitude stand-in; replaced by Viviani et al.
                   event files when we have them.
  stopping         NIST PSTAR Ti and H (Bragg additivity; T stops like H per atom).
  IPC              the Born E1 multipole of nTof_x17 ipc_born at W = E*.
  detector         the four n_TOF Micromegas arms (lnl_rates toy, faces at 204 mm,
                   active 399.4 x 359.9 mm), plus the Ti-T backing: a thick
                   backing (Demokritos' own targets are Ti-T on 1 mm Cu) blocks
                   every lepton going downstream.  Everything after geometry is
                   CALIBRATED ON THE LNL GEANT4 RESULT: the same hardware, the
                   same ~9-10 MeV leptons, the same 3D fit (lnl/out/talk/numbers.json).
  cosmics          as LNL after MM 15 deg + TOF + E_sum window (~1/day): negligible.

See README.md, FACILITY.md, PHYSICS.md, ESTIMATES.md and GEANT_PREP.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'out'
FIGS = OUT / 'figures'
sys.path.insert(0, str(ROOT / 'lnl'))
sys.path.insert(0, str(ROOT / 'ill'))

import lnl_rates as L                                  # noqa: E402

# --------------------------------------------------------------------------- #
# constants
# --------------------------------------------------------------------------- #
U_MEV = L.U_MEV
M_E = L.M_E
N_AVO = L.N_AVO
E_CHARGE = L.E_CHARGE
ALPHA = 1 / 137.035999084
HBARC = 197.3269804
M_P_U = 1.007276467                    # proton, nuclear
M_T_ATOM_U = 3.01604928                # 3H atomic
M_HE4_ATOM_U = 4.00260325413
M_H1_ATOM_U = 1.00782503207
Q_PT = (M_T_ATOM_U + M_H1_ATOM_U - M_HE4_ATOM_U) * U_MEV      # 19.814 MeV
M_T_U = M_T_ATOM_U - M_E / U_MEV
MU_MEV = M_P_U * M_T_U / (M_P_U + M_T_U) * U_MEV
M_HE4 = M_HE4_ATOM_U * U_MEV - 2 * M_E                         # nuclear, MeV
EP_PN_THRESHOLD = 1019.0               # keV, 3H(p,n)3He

# 4He levels (TUNL A=4, Tilley 1992), the two that matter below E_p = 1 MeV
E_0P2 = 20.21                          # MeV, 0+ (T=0), Gamma 0.50 MeV
G_0P2 = 0.50
E_0M = 21.01                           # MeV, 0-, Gamma 0.84 MeV (the ATOMKI X17 state)
M_E0_FM2 = 1.53                        # 4He 0+_2 -> g.s. monopole matrix element
S0_MEVB, S1, S2 = 1.30e-6, 25.0, 38.8  # Hahn 1995 fit, physics/9910011 Table 1
E_GAMOW = 2 * MU_MEV * (np.pi * ALPHA) ** 2                  # MeV

# the claim
BX_ATOMKI = 5.1e-6                     # Gamma_X / Gamma_gamma, PRC 104, 044003 (average)
BX_ATOMKI_ERR = 1.3e-6
MX_ATOMKI = 16.94                      # MeV (+-0.12 stat +-0.21 syst)
#: ATOMKI's fitted IPC coefficients (PRC 104, 044003 Table I), per gamma.  They are
#: 20-45x below the Born E1 value; the upside scenario scales the IPC to them.
IPCC_ATOMKI = {510: 2.5e-4, 610: 1.0e-4, 900: 1.1e-4}
IPCC_ATOMKI_DEFAULT = 1.5e-4

# hardware calibration from the LNL Geant4 campaign (lnl/out/talk/numbers.json):
# selected X17 per day in the reference 3D fit, MM 15 deg + TOF, and the days to
# 3 sigma at R(ATOMKI) = 5.8e-6, 1 uA, Li2O 300 ug/cm2 at 1.10 MeV.
LNL_NUMBERS = ROOT / 'lnl' / 'out' / 'talk' / 'numbers.json'
LNL_YIELDS = ROOT / 'lnl' / 'out' / 'yields.csv'
LNL_SCENARIO = 'ATOMKI 2016 anomaly'

SIGMA_THETA_DEG = 5.1                  # CFRP 0.4 mm chamber, LNL Geant4 L1 (sigma68)
CHAMBER_NOTE = 'CFRP 0.4 mm chamber, as LNL'
DISK_R_MM = 12.5                       # Ti-T disk radius (ask; Demokritos target size unknown)


# --------------------------------------------------------------------------- #
# kinematics
# --------------------------------------------------------------------------- #
def e_cm(ep_kev):
    """Centre-of-mass energy (keV) for a lab proton energy (keV)."""
    return np.asarray(ep_kev, float) * M_T_U / (M_T_U + M_P_U)


def e_star(ep_kev):
    """4He excitation energy (MeV) reached by capture at lab energy ep (keV)."""
    return Q_PT + e_cm(ep_kev) / 1e3


def beta_cm(ep_kev):
    tp = np.asarray(ep_kev, float) / 1e3
    mp = M_P_U * U_MEV
    pp = np.sqrt(tp ** 2 + 2 * tp * mp)
    return pp / (tp + mp + M_T_U * U_MEV)


def x17_energy(w, mx):
    """X17 total energy (MeV) in 4He* -> 4He(gs) + X, 4He* at rest, E* = w."""
    big_w = M_HE4 + w
    return (big_w ** 2 + mx ** 2 - M_HE4 ** 2) / (2 * big_w)


def theta_min(w, mx):
    ex = x17_energy(w, mx)
    return np.degrees(2 * np.arcsin(np.clip(mx / ex, 0, 1)))


def kinematics_table() -> pd.DataFrame:
    rows = []
    for ep in (250.0, 510.0, 610.0, 800.0, 900.0, 1000.0):
        w = float(e_star(ep))
        row = dict(Ep_keV=ep, Ecm_keV=float(e_cm(ep)), Estar_MeV=w,
                   beta_4He=float(beta_cm(ep)), pair_KE_sum_MeV=w - 2 * M_E,
                   below_pn_threshold=ep < EP_PN_THRESHOLD)
        for mx in (16.7, 16.94, 17.2):
            row[f'theta_min_deg_m{mx}'] = float(theta_min(w, mx))
        rows.append(row)
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# cross sections
# --------------------------------------------------------------------------- #
def s_factor_mevb(ecm_mev):
    e = np.asarray(ecm_mev, float)
    return S0_MEVB * (1 + S1 * e + S2 * e ** 2)


def sigma_gamma_ub(ep_kev):
    """3H(p,gamma)4He, all to the ground state (4He has no bound excited state)."""
    e = np.maximum(e_cm(ep_kev) / 1e3, 1e-4)
    return s_factor_mevb(e) / e * np.exp(-np.sqrt(E_GAMOW / e)) * 1e6


def _ib():
    return L._ipc_born()


def gamma_ee_e0_ev(w=E_0P2):
    return _ib().e0_pair_width_eV(M_E0_FM2, w)


def sigma_e0_ub(ep_kev):
    """E0 pairs through the 20.21 MeV 0+ resonance (single level, Gamma_p = Gamma).

    sigma = (pi/k^2) g Gamma_p Gamma_ee / ((E - E_r)^2 + Gamma^2/4), g = 1/4.
    No Coulomb penetrability in Gamma_p(E): an order-of-magnitude stand-in.
    """
    e = np.maximum(e_cm(ep_kev) / 1e3, 1e-4)
    k2 = 2 * MU_MEV * e / HBARC ** 2                     # fm^-2
    er = E_0P2 - Q_PT
    gee = gamma_ee_e0_ev() * 1e-6                        # MeV
    bw = G_0P2 * gee / ((e - er) ** 2 + G_0P2 ** 2 / 4)
    return np.pi / k2 * 0.25 * bw * 1e4                  # fm^2 -> ub


_ALPHA_CACHE: dict = {}


def alpha_e1(w):
    key = round(float(w), 2)
    if key not in _ALPHA_CACHE:
        _ALPHA_CACHE[key] = _ib().alpha_pair('E1', key)
    return _ALPHA_CACHE[key]


# --------------------------------------------------------------------------- #
# stopping and targets
# --------------------------------------------------------------------------- #
AW_TI, AW_T = 47.867, 3.01605


class TiTStopping:
    """Proton stopping in TiT_x, MeV cm2/g.  T stops like H per atom (electrons)."""

    def __init__(self):
        self.s = L.Stopping()

    def per_gram(self, x, e_mev):
        m = AW_TI + x * AW_T
        s_ti = self.s.element('Ti', e_mev)
        s_t = self.s.element('H', e_mev) * (1.008 / AW_T)
        return (AW_TI * s_ti + x * AW_T * s_t) / m


def thick_yield(stp: TiTStopping, ep0_kev, ti_mg_cm2, x=1.5, step_kev=0.5) -> dict:
    """Integrate captures while the proton slows through a TiT_x layer.

    ti_mg_cm2 is the Ti areal density; the layer's mass is ti * (1 + x*3.016/47.87).
    """
    m_tot = ti_mg_cm2 * 1e-3 * (AW_TI + x * AW_T) / AW_TI
    n_t = x * N_AVO / (AW_TI + x * AW_T)                       # T atoms per gram of layer
    e, m_left = float(ep0_kev), m_tot
    acc = dict(Y_g=0.0, Y_ipc=0.0, Y_e0=0.0, w_estar=0.0)
    while m_left > 0 and e > 20:
        s = float(stp.per_gram(x, e / 1e3))
        dm = min(step_kev / 1e3 / s, m_left)
        de = dm * s * 1e3
        em = e - de / 2
        k = n_t * dm * 1e-30
        yg = float(sigma_gamma_ub(em)) * k
        acc['Y_g'] += yg
        acc['Y_ipc'] += yg * alpha_e1(float(e_star(em)))
        acc['Y_e0'] += float(sigma_e0_ub(em)) * k
        acc['w_estar'] += yg * float(e_star(em))
        e -= de
        m_left -= dm
    return dict(Ep_keV=ep0_kev, Ti_mg_cm2=ti_mg_cm2, x_T_per_Ti=x,
                T_atoms_cm2=n_t * m_tot, E_exit_keV=max(e, 0.0), dE_keV=ep0_kev - max(e, 0.0),
                Y_gamma=acc['Y_g'], Y_ipc_E1=acc['Y_ipc'], Y_E0_pairs=acc['Y_e0'],
                mean_Estar_MeV=acc['w_estar'] / acc['Y_g'] if acc['Y_g'] else np.nan)


#: the scenarios: what ATOMKI ran, what Demokritos' existing targets give, and options
SCENARIOS = [
    # name, Ep keV, Ti mg/cm2, T/Ti, current uA (reference), machine
    ('ATOMKI 2021, 510 keV', 510, 4.2, 1.5, 1.0, 'ATOMKI Tandetron'),
    ('ATOMKI 2021, 610 keV', 610, 4.2, 1.5, 1.0, 'ATOMKI Tandetron'),
    ('ATOMKI 2019/21, 900 keV', 900, 4.2, 1.5, 1.0, 'ATOMKI 5 MV VdG / Tandetron'),
    ('Demokritos Ti-T (2.1 mg/cm2), 900 keV', 900, 2.1, 1.5, 1.0, 'Demokritos 5.5 MV Tandem'),
    ('Demokritos Ti-T (2.1 mg/cm2), 800 keV', 800, 2.1, 1.5, 1.0, 'Demokritos 5.5 MV Tandem'),
    ('Demokritos Ti-T (2.1 mg/cm2), 1000 keV', 1000, 2.1, 1.5, 1.0, 'Demokritos 5.5 MV Tandem'),
    ('thick Ti-T (4.2 mg/cm2), 1000 keV', 1000, 4.2, 1.5, 1.0, 'Demokritos 5.5 MV Tandem'),
    ('PAPAP 250 keV, thick Ti-T', 250, 2.1, 1.5, 100.0, 'Demokritos PAPAP 250 kV'),
]


def yields_table(stp) -> pd.DataFrame:
    rows = []
    for name, ep, ti, x, cur, mach in SCENARIOS:
        r = thick_yield(stp, ep, ti, x)
        r.update(scenario=name, machine=mach, I_ref_uA=cur)
        rows.append(r)
    d = pd.DataFrame(rows)
    pps = 1e-6 / E_CHARGE
    d['gamma_per_s_1uA'] = d.Y_gamma * pps
    d['ipc_per_s_1uA'] = d.Y_ipc_E1 * pps
    d['e0_per_s_1uA'] = d.Y_E0_pairs * pps
    d['x17_per_day_1uA_4pi'] = d.Y_gamma * pps * 86400 * BX_ATOMKI
    d['x17_per_day_Iref_4pi'] = d.x17_per_day_1uA_4pi * d.I_ref_uA
    d['heat_W_per_uA'] = d.Ep_keV * 1e-3
    return d[['scenario', 'machine', 'Ep_keV', 'Ti_mg_cm2', 'x_T_per_Ti', 'T_atoms_cm2',
              'dE_keV', 'E_exit_keV', 'mean_Estar_MeV', 'Y_gamma', 'Y_ipc_E1', 'Y_E0_pairs',
              'gamma_per_s_1uA', 'ipc_per_s_1uA', 'e0_per_s_1uA', 'x17_per_day_1uA_4pi',
              'I_ref_uA', 'x17_per_day_Iref_4pi', 'heat_W_per_uA']]


def excitation_table() -> pd.DataFrame:
    ep = np.arange(100, 1201, 10.0)
    sg = sigma_gamma_ub(ep)
    return pd.DataFrame(dict(Ep_keV=ep, Estar_MeV=e_star(ep), sigma_gamma_ub=sg,
                             sigma_ipc_E1_ub=sg * np.array([alpha_e1(float(w)) for w in e_star(ep)]),
                             sigma_E0_pairs_ub=sigma_e0_ub(ep),
                             S_factor_eVb=s_factor_mevb(e_cm(ep) / 1e3) * 1e6,
                             fit_range=ep <= 750))


# --------------------------------------------------------------------------- #
# detector toy: four arms, a vertex at (0, 0, z0), beam along +z, backing shadow
# --------------------------------------------------------------------------- #
def x17_vectors(n, w, mx, seed=2):
    rng = np.random.default_rng(seed)
    ex = x17_energy(w, mx)
    k = np.sqrt(ex ** 2 - mx ** 2)
    cs = rng.uniform(-1, 1, n)
    return L._pair_from_rest(np.full(n, mx), np.full(n, k), ex, cs, rng, np.ones(n))


def arm_hit(p, z0=0.0):
    """Arm (0-3) a straight lepton from (0, 0, z0) lands in, or -1."""
    d = p / np.linalg.norm(p, axis=1, keepdims=True)
    best_t = np.full(len(d), np.inf)
    arm = np.full(len(d), -1)
    for i, (ax, sg) in enumerate([(0, 1), (0, -1), (1, 1), (1, -1)]):
        dn = d[:, ax] * sg
        t = np.where(dn > 0, L.MM_FACE_MM / np.where(dn > 0, dn, 1), np.inf)
        other = 1 - ax
        ok = (np.abs(d[:, other] * t) < L.MM_HALF_U) & (np.abs(z0 + d[:, 2] * t) < L.MM_HALF_Z)
        better = t < best_t
        arm = np.where(better & ok, i, np.where(better, -1, arm))
        best_t = np.minimum(best_t, t)
    return arm


def highland_rad(ke, x_x0):
    p = np.sqrt((ke + M_E) ** 2 - M_E ** 2)
    beta = p / (ke + M_E)
    x = np.maximum(x_x0, 1e-12)
    return 13.6 / (beta * p) * np.sqrt(x) * (1 + 0.038 * np.log(x))


#: backing options: name -> (X0 in mm, thickness mm, mode).  mode 'block' throws away
#: every lepton going downstream (p_z > 0); 'scatter' smears it by Highland over its path.
X0_MM = {'Cu': 14.36, 'Mo': 9.594, 'Al': 88.97, 'C': 213.5, 'Ti': 35.6}
BACKINGS = {
    'none (ideal)': (None, 0.0, 'none'),
    'Cu 1 mm, blocks downstream (Demokritos target)': ('Cu', 1.0, 'block'),
    'Mo 0.4 mm, blocks downstream (ATOMKI target)': ('Mo', 0.4, 'block'),
    'Cu 1 mm, scatters downstream': ('Cu', 1.0, 'scatter'),
    'Cu 50 um': ('Cu', 0.05, 'scatter'),
    'Cu 100 um': ('Cu', 0.10, 'scatter'),
    'Al 25 um': ('Al', 0.025, 'scatter'),
}


def acceptance(ev, backing, z0=0.0, rng=None):
    """Two different arms, both KE > 1 MeV, downstream legs per the backing.

    Returns (ok, measured opening angle)."""
    rng = rng or np.random.default_rng(5)
    mat, t, mode = BACKINGS[backing]
    a1, a2 = arm_hit(ev['p1'], z0), arm_hit(ev['p2'], z0)
    ok = (a1 >= 0) & (a2 >= 0) & (a1 != a2) & (ev['ke1'] > L.KE_MIN) & (ev['ke2'] > L.KE_MIN)
    sig = np.full(len(ok), np.radians(SIGMA_THETA_DEG)) ** 2
    for p, ke in ((ev['p1'], ev['ke1']), (ev['p2'], ev['ke2'])):
        cz = p[:, 2] / np.linalg.norm(p, axis=1)
        down = cz > 0
        if mode == 'block':
            ok &= ~down
        elif mode == 'scatter':
            sz = np.sqrt(np.clip(1 - cz ** 2, 1e-9, None))
            path = np.minimum(t / np.maximum(cz, 1e-6), DISK_R_MM / sz)
            sig = sig + np.where(down, highland_rad(ke, path / X0_MM[mat]) ** 2, 0.0)
    th = ev['theta'] + np.degrees(rng.normal(0, 1, len(ok)) * np.sqrt(sig))
    return ok, th


BINS = np.arange(0, 181, 5)


def best_window(s_h, b_h, lo_range=(80, 135), min_width=10):
    """Counting window [lo, hi) on 5-degree bins that maximises S/sqrt(B)."""
    best = (0, 0, 0.0)
    edges = BINS
    cs, cb = np.concatenate([[0], np.cumsum(s_h)]), np.concatenate([[0], np.cumsum(b_h)])
    for i, lo in enumerate(edges[:-1]):
        if not lo_range[0] <= lo <= lo_range[1]:
            continue
        for j in range(i + min_width // 5, len(edges)):
            s, b = cs[j] - cs[i], cb[j] - cb[i]
            if b > 0 and s / np.sqrt(b) > best[2]:
                best = (lo, edges[j], s / np.sqrt(b))
    return best


def spectra(cases, n):
    """Generated samples, once per case (shared across the backing scans)."""
    out = {}
    for name, fn in cases.items():
        out[name] = fn(n)
    return out


def he4_samples(n, w=20.49, mx=MX_ATOMKI):
    return spectra({
        'X17': lambda m: x17_vectors(m, w, mx),
        'IPC E1': lambda m: L.ipc_vectors('E1', 4 * m, w, seed=11),
        'E0': lambda m: L.ipc_vectors('E0', 4 * m, w, seed=13),
    }, n)


def histos(sam, backing, z0, rng_seed=5):
    h, acc_tot = {}, {}
    for name, ev in sam.items():
        ok, th = acceptance(ev, backing, z0, np.random.default_rng(rng_seed))
        w = ev['w'] / ev['w'].sum()
        h[name], _ = np.histogram(th[ok], BINS, weights=w[ok])
        acc_tot[name] = float(w[ok].sum())
    return h, acc_tot


def he4_rates_per_day(yrow, cur_ua):
    """Produced per day into 4pi: X17 at B_x(ATOMKI), E1 IPC, E0 pairs."""
    pps = cur_ua * 1e-6 / E_CHARGE * 86400
    return {'X17': yrow.Y_gamma * pps * BX_ATOMKI,
            'IPC E1': yrow.Y_ipc_E1 * pps,
            'E0': yrow.Y_E0_pairs * pps}


# --------------------------------------------------------------------------- #
# LNL calibration: the same toy, run on the LNL reference case
# --------------------------------------------------------------------------- #
def lnl_calibration(n) -> dict:
    nums = json.loads(LNL_NUMBERS.read_text())
    y = pd.read_csv(LNL_YIELDS).set_index('scenario').loc[LNL_SCENARIO]
    pps = 1e-6 / E_CHARGE * 86400
    ng0 = y.Y_g0 * pps                                  # gamma0 per day, 1 uA
    alpha = pd.read_csv(ROOT / 'lnl' / 'out' / 'ipc_alpha.csv').set_index(['W_MeV', 'multipole']).alpha_pair
    rates = {'X17': ng0 * L.R_ATOMKI_2016 * (1 - y.frac_17_64),
             'IPC M1 18.15': ng0 * y.frac_18_15_res * alpha[(18.15, 'M1')],
             'IPC M1 17.64': ng0 * y.frac_17_64 * alpha[(17.64, 'M1')],
             'IPC E1 18.15': ng0 * y.frac_direct * alpha[(18.15, 'E1')]}
    sam = spectra({'X17': lambda m: L.x17_vectors(m, 18.15, 16.7),
                   'IPC M1 18.15': lambda m: L.ipc_vectors('M1', 4 * m, 18.15),
                   'IPC M1 17.64': lambda m: L.ipc_vectors('M1', 4 * m, 17.64),
                   'IPC E1 18.15': lambda m: L.ipc_vectors('E1', 4 * m, 18.15)}, n)
    h, acc = histos(sam, 'none (ideal)', 0.0)
    s_h = rates['X17'] * h['X17']
    b_h = sum(rates[k] * h[k] for k in rates if k != 'X17')
    lo, hi, z1 = best_window(s_h, b_h, lo_range=(110, 150))
    days_toy = 9 / z1 ** 2
    out = dict(produced_x17_per_day=rates['X17'], acc_2arm_x17=acc['X17'],
               window=f'{lo}-{hi}', days_toy=days_toy)
    for hw in ('as built', 'big plastics'):
        c = nums['cases'][f'{hw}|1']
        out[hw] = dict(days_geant=c['days_3sigma'], x17_sel_per_day=c['x17_per_day'],
                       k_days=c['days_3sigma'] / days_toy,
                       eps_after_2arm=c['x17_per_day'] / (rates['X17'] * acc['X17']))
    return out


# --------------------------------------------------------------------------- #
# reach
# --------------------------------------------------------------------------- #
CONFIGS = [
    # backing, z0 (mm, target downstream of the arm centre)
    ('none (ideal)', 0.0),
    ('Al 25 um', 0.0),
    ('Cu 50 um', 0.0),
    ('Cu 100 um', 0.0),
    ('Cu 1 mm, scatters downstream', 0.0),
    ('Cu 1 mm, blocks downstream (Demokritos target)', 0.0),
    ('Cu 1 mm, blocks downstream (Demokritos target)', 60.0),
    ('Cu 1 mm, blocks downstream (Demokritos target)', 120.0),
    ('Cu 1 mm, blocks downstream (Demokritos target)', 180.0),
]


def reach_tables(ytab, cal, n):
    rows, hrows = [], []
    sam = he4_samples(n)
    for backing, z0 in CONFIGS:
        h, acc = histos(sam, backing, z0)
        for _, y in ytab.iterrows():
            r = he4_rates_per_day(y, 1.0)
            s_h = r['X17'] * h['X17']
            b_ipc = r['IPC E1'] * h['IPC E1']
            b_e0 = r['E0'] * h['E0']
            lo, hi, z1 = best_window(s_h, b_ipc + b_e0)
            sel = (BINS[:-1] >= lo) & (BINS[:-1] < hi)
            days_toy = 9 / z1 ** 2 if z1 > 0 else np.inf
            row = dict(scenario=y.scenario, backing=backing, z0_mm=z0, window=f'{lo}-{hi}',
                       acc_2arm_x17=acc['X17'], acc_2arm_ipc=acc['IPC E1'], acc_2arm_e0=acc['E0'],
                       x17_4pi_per_day=r['X17'], S_toy_per_day=s_h[sel].sum(),
                       B_ipc_toy_per_day=b_ipc[sel].sum(), B_e0_toy_per_day=b_e0[sel].sum(),
                       SoverB=s_h[sel].sum() / (b_ipc + b_e0)[sel].sum(), days_toy_1uA=days_toy)
            for hw in ('as built', 'big plastics'):
                c = cal[hw]
                tag = hw.replace(' ', '_')
                row[f'x17_sel_per_day_{tag}'] = r['X17'] * acc['X17'] * c['eps_after_2arm']
                row[f'days_3sigma_{tag}'] = days_toy * c['k_days']
                row[f'days_3sigma_{tag}_at_Iref'] = days_toy * c['k_days'] / y.I_ref_uA
            row['I_ref_uA'] = y.I_ref_uA
            # upside: the IPC as ATOMKI fitted it (B scales, S does not; days ~ B)
            f_ipcc = IPCC_ATOMKI.get(int(y.Ep_keV), IPCC_ATOMKI_DEFAULT) / (y.Y_ipc_E1 / y.Y_gamma)
            row['ipc_scale_atomki'] = f_ipcc
            for hw in ('as built', 'big plastics'):
                tag = hw.replace(' ', '_')
                row[f'days_3sigma_{tag}_atomki_ipcc'] = row[f'days_3sigma_{tag}'] * f_ipcc
            rows.append(row)
        if backing in ('none (ideal)', 'Cu 1 mm, blocks downstream (Demokritos target)') and z0 in (0.0, 120.0):
            for i, lo in enumerate(BINS[:-1]):
                hrows.append(dict(backing=backing, z0_mm=z0, theta_lo_deg=lo,
                                  **{k: h[k][i] for k in h}))
    return pd.DataFrame(rows), pd.DataFrame(hrows)


def mass_scan(ytab, cal, n):
    """Days against the X17 mass at 900 keV, ideal backing (shape of the reach only)."""
    y = ytab.set_index('scenario').loc['Demokritos Ti-T (2.1 mg/cm2), 900 keV']
    r = he4_rates_per_day(y, 1.0)
    rows = []
    bg = spectra({'IPC E1': lambda m: L.ipc_vectors('E1', 4 * m, y.mean_Estar_MeV, seed=11),
                  'E0': lambda m: L.ipc_vectors('E0', 4 * m, y.mean_Estar_MeV, seed=13)}, n)
    hb, _ = histos(bg, 'none (ideal)', 0.0)
    for mx in (16.6, 16.8, 16.94, 17.1, 17.3):
        hx, ax = histos({'X17': x17_vectors(n, y.mean_Estar_MeV, mx)}, 'none (ideal)', 0.0)
        s_h = r['X17'] * hx['X17']
        b_h = r['IPC E1'] * hb['IPC E1'] + r['E0'] * hb['E0']
        lo, hi, z1 = best_window(s_h, b_h)
        d = 9 / z1 ** 2
        rows.append(dict(m_X=mx, theta_min=float(theta_min(y.mean_Estar_MeV, mx)), window=f'{lo}-{hi}',
                         acc_2arm=ax['X17'], days_toy=d,
                         days_as_built=d * cal['as built']['k_days'],
                         days_big_plastics=d * cal['big plastics']['k_days']))
    return pd.DataFrame(rows)


def arm_pairs(n) -> pd.DataFrame:
    """Which arm pairs the accepted X17 and IPC use: adjacent (90 deg apart) or opposite."""
    sam = he4_samples(n)
    rows = []
    for backing, z0 in (('none (ideal)', 0.0), ('Cu 1 mm, blocks downstream (Demokritos target)', 120.0)):
        for name in ('X17', 'IPC E1'):
            ev = sam[name]
            ok, th = acceptance(ev, backing, z0)
            a1, a2 = arm_hit(ev['p1'], z0), arm_hit(ev['p2'], z0)
            opp = ok & ((a1 // 2) == (a2 // 2))
            w = ev['w'] / ev['w'].sum()
            win = (th >= 105) & (th < 160)
            rows.append(dict(backing=backing, z0_mm=z0, sample=name,
                             acc_2arm=float(w[ok].sum()),
                             frac_opposite=float(w[opp].sum() / w[ok].sum()),
                             frac_opposite_in_105_160=float(w[opp & win].sum() / max(w[ok & win].sum(), 1e-30))))
    return pd.DataFrame(rows)


def heat_table() -> pd.DataFrame:
    """Temperature rise of a thin backing cooled at its rim (radial conduction).

    dT = P ln(R/r_spot) / (2 pi k t).  Ti-T loses tritium above ~200-300 C (ask the
    target supplier); the beam power is I x E_p, all of it deposited in the layer.
    """
    k_w_mk = {'Cu': 400.0, 'Al': 237.0, 'Mo': 138.0}
    rows = []
    for mat, t_um in (('Al', 25), ('Cu', 50), ('Cu', 100), ('Mo', 400), ('Cu', 1000)):
        for cur in (1, 3, 10, 30):
            pw = cur * 0.9
            dt = pw * np.log(DISK_R_MM / 2.5) / (2 * np.pi * k_w_mk[mat] * t_um * 1e-6)
            rows.append(dict(backing=f'{mat} {t_um} um', I_uA=cur, P_W=pw, dT_K=dt,
                             spot_r_mm=2.5, rim_r_mm=DISK_R_MM))
    return pd.DataFrame(rows)


def neutron_option() -> pd.DataFrame:
    """The Demokritos neutron beams on a 3He cell, for the record (Viviani Table V)."""
    v = pd.DataFrame({'En_MeV': [0.17, 0.35, 0.70, 1.00, 2.00],
                      'sigma_pair_ub': [0.0431, 0.0616, 0.0893, 0.108, 0.146]})
    rows = []
    for flux in (1e5, 1e6):
        for areal, cell in ((1.35e22, 'n_TOF capsule 500 bar x 1 cm'), (2.7e20, '1 bar x 10 cm')):
            for _, r in v.iterrows():
                pairs = flux * 5.0 * areal * r.sigma_pair_ub * 1e-30 * 86400   # 5 cm2 beam
                rows.append(dict(flux_n_cm2_s=flux, cell=cell, En_MeV=r.En_MeV,
                                 ipc_pairs_per_day_4pi=pairs,
                                 x17_per_day_4pi_at_1p5em3=pairs * 1.5e-3))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# figures
# --------------------------------------------------------------------------- #
def figures(ex, kin, ytab, reach, hist, ms):
    import matplotlib
    matplotlib.use('Agg')
    import figstyle as fs
    fs.use()

    fig, ax = fs.figure()
    ax.plot(ex.Ep_keV, ex.sigma_gamma_ub, color=fs.ACCENT, label='σ(p,γ₀), Hahn 1995 S-factor fit')
    ax.plot(ex.Ep_keV, ex.sigma_ipc_E1_ub, '--', color='#0072B2', label='E1 IPC pairs (Born α)')
    ax.plot(ex.Ep_keV, ex.sigma_E0_pairs_ub, ':', color='#D55E00', label='E0 pairs, 20.21 MeV 0⁺ (stand-in)')
    ax.plot(ex.Ep_keV, ex.sigma_gamma_ub * BX_ATOMKI, color='#009E73', label='X17 at B_x(ATOMKI)')
    ax.axvspan(750, 1200, color=fs.MUTED, alpha=0.08)
    ax.axvline(EP_PN_THRESHOLD, color=fs.MUTED, lw=0.8)
    ax.text(EP_PN_THRESHOLD - 10, 3e-4, '(p,n) opens', ha='right', fontsize=8, color=fs.MUTED)
    ax.errorbar([900], [16.8], yerr=[[5], [5]], fmt='s', ms=4, color='k',
                label='ATOMKI "2 µb/sr" at 900 keV (×8π/3)')
    ax.set_yscale('log')
    ax.set_ylim(1e-6, 100)
    ax.set_xlabel('proton energy, lab [keV]')
    ax.set_ylabel('σ [µb]')
    ax.legend(frameon=False, fontsize=8, loc='center left', bbox_to_anchor=(0.0, 0.42))
    fs.title(ax, 'Every γ in ³H(p,γ)⁴He goes to the ground state',
             'shaded: S-factor extrapolated past the 0.1-0.75 MeV fit range')
    fs.save(fig, FIGS / 'excitation', data=ex)

    fig, ax = fs.figure()
    names = ['X17', 'IPC E1', 'E0']
    cols = ['#009E73', '#0072B2', '#D55E00']
    for (bk, z0), ls in ((('none (ideal)', 0.0), '-'),
                         (('Cu 1 mm, blocks downstream (Demokritos target)', 120.0), '--')):
        g = hist[(hist.backing == bk) & (hist.z0_mm == z0)]
        for nm, c in zip(names, cols):
            y = g[nm] / max(g[nm].sum(), 1e-30)
            ax.step(g.theta_lo_deg + 2.5, y, where='mid', color=c, ls=ls,
                    label=f'{nm}, {"no backing" if ls == "-" else "Cu 1 mm, target +12 cm"}')
    ax.set_yscale('log')
    ax.set_xlabel('measured opening angle [deg] (σ = 5.1°)')
    ax.set_ylabel('fraction of accepted pairs / 5°')
    ax.legend(frameon=False, fontsize=7, loc='lower left', ncol=2)
    fs.title(ax, 'At 20.5 MeV the X17 edge is at 111°, between adjacent and opposite arms',
             'toy: two different arms, KE > 1 MeV; shape only')
    fs.save(fig, FIGS / 'acceptance', data=hist)

    sel = reach[reach.scenario == 'Demokritos Ti-T (2.1 mg/cm2), 900 keV'].copy()
    sel['label'] = sel.backing.str.replace(' (Demokritos target)', '', regex=False) + \
        np.where(sel.z0_mm > 0, ', target +' + (sel.z0_mm / 10).map('{:.0f}'.format) + ' cm', '')
    fig, ax = fs.figure()
    yy = np.arange(len(sel))
    ax.barh(yy - 0.2, sel.days_3sigma_as_built, 0.4, color=fs.MUTED, label='n_TOF stack as built')
    ax.barh(yy + 0.2, sel.days_3sigma_big_plastics, 0.4, color=fs.ACCENT, label='big plastics')
    ax.set_yticks(yy, sel.label, fontsize=8)
    ax.invert_yaxis()
    ax.set_xscale('log')
    ax.set_xlabel('days to 3σ at B_x(ATOMKI), 1 µA, 900 keV (LNL-calibrated toy)')
    ax.legend(frameon=False, fontsize=8, loc='upper right', bbox_to_anchor=(1.0, 1.0))
    ax.set_xlim(1, 400)
    fs.title(ax, 'The target backing is the design driver',
             'a thick backing blocks every downstream lepton; moving the target downstream wins some back')
    fs.save(fig, FIGS / 'reach_backing', data=sel)

    fig, ax = fs.figure(figsize=fs.HALF)
    rows = []
    for ep in (250, 510, 610, 800, 900, 1000):
        for mx in np.arange(16.0, 17.81, 0.05):
            rows.append(dict(Ep_keV=ep, m_X=mx, theta_min=float(theta_min(float(e_star(ep)), mx))))
    tm = pd.DataFrame(rows)
    for i, (ep, g) in enumerate(tm.groupby('Ep_keV')):
        ax.plot(g.m_X, g.theta_min, color=['#CC79A7', '#0072B2', '#56B4E9', '#009E73', fs.ACCENT, '#D55E00'][i],
                label=f'{ep:g} keV')
    ax.set_xlabel('m(X17) [MeV]')
    ax.set_ylabel('θ_min [deg]')
    ax.legend(frameon=False, fontsize=8)
    fs.title(ax, 'The ⁴He edge sits at 105–120°')
    fs.save(fig, FIGS / 'theta_min', data=tm)


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--quick', action='store_true', help='small MC, no figures')
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    n = 40_000 if args.quick else 300_000

    stp = TiTStopping()
    print(f'CHECK  Q(3H(p,g)4He) = {Q_PT:.4f} MeV  (AME: 19.8139)')
    print(f'CHECK  E* at 510/610/900 keV = {float(e_star(510)):.2f}/{float(e_star(610)):.2f}/'
          f'{float(e_star(900)):.2f} MeV  (ATOMKI: 20.21/20.29/20.49 -- 510 quoted as 20.21)')
    s900 = float(sigma_gamma_ub(900))
    print(f'CHECK  sigma(p,g) at 900 keV = {s900:.1f} ub; ATOMKI "about 2 ub/sr" x 8pi/3 (E1, 90 deg) '
          f'= 16.8 ub; x 4pi (isotropic) = 25 ub')
    print(f'CHECK  sigma at Ep 25/30 keV = {float(sigma_gamma_ub(25)):.2f}/{float(sigma_gamma_ub(30)):.2f} ub '
          f'(physics/9910011: 0.19/0.30, with E_cm = 0.75 Ep -- they may quote E_cm)')
    print(f'CHECK  Gamma_ee(E0, 0+_2) = {gamma_ee_e0_ev():.2e} eV from M(E0) = {M_E0_FM2} fm2')
    print(f'CHECK  alpha_E1(20.49) = {alpha_e1(20.49):.2e}  (nTof_x17 Born; Viviani n+3He '
          f'sigma_pair/sigma_gamma ~ 2.1e-3 at 0.17-1 MeV)')
    print(f'CHECK  S(Ti, 0.9 MeV) = {float(stp.s.element("Ti", 0.9)):.0f}, '
          f'S(TiT1.5) = {float(stp.per_gram(1.5, 0.9)):.0f} MeV cm2/g')

    kin = kinematics_table()
    ex = excitation_table()
    ytab = yields_table(stp)
    cal = lnl_calibration(n)
    print(f'CHECK  LNL toy days (counting, {cal["window"]}) = {cal["days_toy"]:.1f}; Geant4 3D: '
          f'as built {cal["as built"]["days_geant"]:.1f} d (k = {cal["as built"]["k_days"]:.2f}), '
          f'big plastics {cal["big plastics"]["days_geant"]:.2f} d (k = {cal["big plastics"]["k_days"]:.3f})')
    print(f'CHECK  LNL toy 2-arm X17 acceptance = {cal["acc_2arm_x17"]:.3f} (Geant4 mm_2arm 0.476); '
          f'eps after 2-arm: as built {cal["as built"]["eps_after_2arm"]:.3f}, '
          f'big plastics {cal["big plastics"]["eps_after_2arm"]:.3f}')
    reach, hist = reach_tables(ytab, cal, n)
    ms = mass_scan(ytab, cal, n)
    nopt = neutron_option()
    ap_ = arm_pairs(n)
    ht = heat_table()

    for name, d in (('kinematics', kin), ('excitation', ex), ('yields', ytab), ('reach', reach),
                    ('acceptance_hist', hist), ('mass_scan', ms), ('neutron_option', nopt),
                    ('arm_pairs', ap_), ('heat', ht)):
        d.to_csv(OUT / f'{name}.csv', index=False)
        print(f'  -> {OUT / (name + ".csv")}')
    (OUT / 'lnl_calibration.json').write_text(json.dumps(cal, indent=1, default=float))

    pd.set_option('display.width', 220)
    pd.set_option('display.max_columns', 40)
    f = lambda v: f'{v:.3g}'                                           # noqa: E731
    print('\n== kinematics ==\n', kin.round(3).to_string(index=False))
    print('\n== yields ==\n', ytab.to_string(index=False, float_format=f))
    cols = ['scenario', 'backing', 'z0_mm', 'window', 'acc_2arm_x17', 'x17_4pi_per_day', 'SoverB',
            'x17_sel_per_day_as_built', 'days_3sigma_as_built', 'x17_sel_per_day_big_plastics',
            'days_3sigma_big_plastics']
    print('\n== reach, 1 uA ==\n', reach[cols].to_string(index=False, float_format=f))
    print('\n== mass scan, 900 keV, no backing ==\n', ms.to_string(index=False, float_format=f))
    print('\n== arm pairs ==\n', ap_.to_string(index=False, float_format=f))
    print('\n== backing heat, 900 keV ==\n', ht.to_string(index=False, float_format=f))
    print('\n== neutron option ==\n', nopt[nopt.En_MeV.isin([0.35])].to_string(index=False, float_format=f))
    if not args.quick:
        figures(ex, kin, ytab, reach, hist, ms)
    return 0


if __name__ == '__main__':
    sys.exit(main())
