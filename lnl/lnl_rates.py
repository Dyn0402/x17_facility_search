#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lnl_rates.py -- what the MX17 apparatus would see on a proton beam at LNL.

    python lnl/lnl_rates.py            # all tables -> lnl/out/*.csv, figures
    python lnl/lnl_rates.py --quick    # tables only, small MC

The reaction is the ATOMKI one, 7Li(p,e+e-)8Be.  A ~1 MeV proton is captured by
7Li and makes 8Be at E* = Q + E_cm (Q = 17.2551 MeV), which decays by a real
gamma, by internal pair creation (IPC), or -- the claim -- by an X17.

Everything here is analytic or a toy MC.  It is anchored to data wherever data
exist, and every anchor is printed as a CHECK line:

  cross sections   Zahnow et al., Z. Phys. A 351, 229 (1995), EXFOR A0639:
                   measured S-factors for gamma0 and gamma0+gamma1, 98-1500 keV
                   (data/exfor_A0639_Zahnow1995.txt).  Split into the two 1+
                   resonances (Breit-Wigner with the Tilley 2004 widths) and a
                   smooth non-resonant remainder (direct capture, E1).
  stopping         NIST PSTAR (data/pstar_stopping.csv).  PSTAR has no lithium,
                   so Li is derived from LiF minus F, and F from Teflon minus C
                   (Bragg additivity; ~5-10 % for compounds at 1 MeV).
  IPC              the Born multipole generator of nTof_x17
                   (sept26_prelim_analysis/ipc_born.py) at W = 17.64 / 18.15 MeV.
                   CHECKed against the Rose value ATOMKI uses (3.9e-3, M1 18.15).
  detector         a toy of the four n_TOF Micromegas arms (faces at 204 mm,
                   active 399.4 x 359.9 mm).  Everything after geometry
                   (trigger, energy sum, reconstruction) is ONE factor carried
                   over from the ILL Geant4 campaign: EPS_REST.  Replace it with
                   Geant4 before believing any reach to better than x2.
  cosmics          the n_TOF-hardware cosmic rates after the MM segment and
                   collinearity cuts, from ../ill/FEASIBILITY_SIM.md section 10.

See README.md (bottom line), PHYSICS.md, TARGETS.md, FACILITY.md, and
GEANT_PREP.md for what Geant4 has to replace.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE / 'data'
OUT = HERE / 'out'
FIGS = OUT / 'figures'
sys.path.insert(0, str(HERE.parent / 'ill'))

NTOF_X17 = Path(os.environ.get('NTOF_X17',
                               Path.home() / 'PycharmProjects' / 'nTof_x17'))

# --------------------------------------------------------------------------- #
# constants
# --------------------------------------------------------------------------- #
U_MEV = 931.49410242
M_E = 0.51099895
M_P_U = 1.007276467            # proton (nuclear) mass, u
M_LI7_U = 7.016003434          # 7Li atomic mass, u
M_BE8 = 8.005305102 * U_MEV - 4 * M_E   # 8Be nuclear mass, MeV
Q_PG = 17.2551                 # MeV, 7Li(p,g)8Be, Tilley 2004 (NPA 745, 155)
MU_U = M_P_U * M_LI7_U / (M_P_U + M_LI7_U)
N_AVO = 6.02214076e23
E_CHARGE = 1.602176634e-19
F_LI7_NAT = 0.9241             # 7Li atom fraction, natural lithium
F_LI7_ENR = 0.9999

# the two 1+ resonances, Tilley 2004 Tables 8.10 and 8.12 (cm widths in keV,
# gamma widths in eV).  Gamma_p' (inelastic to 7Li*(478)) ~6 keV for 18.15.
RES = {
    '17.64': dict(ep=441.4, ex=17.640, gam=10.7, gp=10.7, gg0=15.0, gg1=6.7, T=1),
    '18.15': dict(ep=1030.0, ex=18.150, gam=138.0, gp=132.0, gg0=1.9, gg1=4.3, T=0),
}
OMEGA = 3.0 / 8.0              # (2J+1)/((2s_p+1)(2s_7Li+1)), J = 1

# the claim and the null results, all as R = Gamma(X17)/Gamma(gamma), ground state
R_ATOMKI_2016 = 5.8e-6         # PRL 116, 042501 (18.15 MeV, best fit)
R_MEG_181 = 1.2e-5             # MEG II, EPJC 85, 763 (2025), 90 % CL
R_MEG_176 = 1.8e-6
ALPHA_ROSE_181 = 3.9e-3        # IPC/gamma, 18.15 MeV M1, the value ATOMKI used
ALPHA_ZM_176 = 3.4e-3          # MEG II's Zhang-Miller-scaled value, 17.64 MeV

# the detector toy: n_TOF Micromegas, see ../ill/HANDOFF_SIM.md and MX17_Geant
MM_FACE_MM = 204.0
MM_HALF_U = 399.4 / 2          # transverse to the beam
MM_HALF_Z = 359.9 / 2          # along the beam (passivated strip ends removed)
#: gamma1 transitions (to the broad 3.0 MeV 2+ state, W ~ 14.6-15.1 MeV) are ~2x
#: the gamma0 ones.  The n_TOF stack contains ~40 % of the lepton energy, so its
#: energy sum cannot tell 15 from 18 MeV: their IPC counts as background in
#: full (1.0).  A real calorimeter (trigger_scint thick plastics) takes this to ~0.
F_G1_LEAK = 1.0
SIGMA_THETA_DEG = 5.0          # opening-angle resolution, point vertex (ILL: 5-8)
KE_MIN = 1.0                   # MeV, a lepton must at least reach the arm
#: Everything after geometry: trigger, energy-sum cut, reconstruction.  From the
#: ILL G1 Geant4 campaign: X17 acc x eff 3.8 % on the plateau, against 27.6 %
#: two-arm Micromegas geometric acceptance (trigger_scint/STATUS.md).  It is the
#: number Geant4 must replace first.
EPS_REST = 0.038 / 0.276

#: Cosmic pairs passing the analysis, n_TOF hardware, per day (ILL section 10:
#: ~9e5 per 50 d without vetoes, 3-10e3 with 3-deg MM segments + 20-deg
#: collinearity veto).  The ILL fit window is 60-180 deg; the window here is
#: narrower, so these are conservative.
COSMICS_PER_DAY = {
    'no veto': 9e5 / 50,
    'MM segments + collinearity (ILL §10)': 1e4 / 50,
    '+ point-vertex cut (est. /25)': 1e4 / 50 / 25,
    '+ CN pulsed beam, 2 ns in 333 ns (est.)': 1e4 / 50 / 25 * (2.0 / 333.0) * 3,
}


# --------------------------------------------------------------------------- #
# kinematics
# --------------------------------------------------------------------------- #
def e_cm(ep_kev):
    """Centre-of-mass energy (keV) for a lab proton energy (keV)."""
    return np.asarray(ep_kev, float) * M_LI7_U / (M_LI7_U + M_P_U)


def e_star(ep_kev):
    """8Be excitation energy (MeV) reached by capture at lab energy ep (keV)."""
    return Q_PG + e_cm(ep_kev) / 1e3


def beta_cm(ep_kev):
    """Velocity of the 8Be* in the lab."""
    tp = np.asarray(ep_kev, float) / 1e3
    mp = M_P_U * U_MEV
    pp = np.sqrt(tp ** 2 + 2 * tp * mp)
    return pp / (tp + mp + M_LI7_U * U_MEV - 3 * M_E)


def x17_energy(w, mx):
    """X17 total energy (MeV) in 8Be* -> 8Be(gs) + X, 8Be* at rest, E* = w."""
    big_w = M_BE8 + w
    return (big_w ** 2 + mx ** 2 - M_BE8 ** 2) / (2 * big_w)


def theta_min(w, mx):
    """Smallest e+e- opening angle (deg) of an X17 of mass mx from E* = w."""
    ex = x17_energy(w, mx)
    return np.degrees(2 * np.arcsin(np.clip(mx / ex, 0, 1)))


def kinematics_table() -> pd.DataFrame:
    rows = []
    for ep in (441.4, 650.0, 800.0, 1030.0, 1040.0, 1080.0, 1100.0, 1225.0):
        w = float(e_star(ep))
        row = dict(Ep_keV=ep, Ecm_keV=float(e_cm(ep)), Estar_MeV=w,
                   beta_8Be=float(beta_cm(ep)),
                   pair_KE_sum_MeV=w - 2 * M_E)
        for mx in (16.7, 16.85, 17.0):
            row[f'theta_min_deg_m{mx}'] = float(theta_min(w, mx))
        rows.append(row)
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# cross sections
# --------------------------------------------------------------------------- #
def two_pi_eta(ecm_kev):
    return 31.29 * 3 * np.sqrt(MU_U / np.asarray(ecm_kev, float))


def s_to_sigma_mb(s_mb_mev, ep_kev):
    ecm = e_cm(ep_kev)
    return np.asarray(s_mb_mev) / (ecm / 1e3) * np.exp(-two_pi_eta(ecm))


def read_zahnow() -> pd.DataFrame:
    """EXFOR A0639 subentry 002: S(E) for gamma0 (E-LVL 0) and gamma0+gamma1
    (E-LVL 0 and 3.0).  EN is the lab proton energy in keV."""
    rows, take = [], False
    for line in (DATA / 'exfor_A0639_Zahnow1995.txt').read_text().splitlines():
        body = line[:66]
        if line.startswith('SUBENT        A0639002'):
            take = True
        elif line.startswith('ENDSUBENT') and take and rows:
            break
        if not take or not body.strip() or not body.strip()[0].isdigit():
            continue
        f = body.split()
        if len(f) == 5:
            rows.append(dict(chan='g0', ep=float(f[1]), S=float(f[2]), dS=float(f[3])))
        elif len(f) == 6:
            rows.append(dict(chan='g01', ep=float(f[2]), S=float(f[3]), dS=float(f[4])))
    d = pd.DataFrame(rows)
    d['sigma_ub'] = s_to_sigma_mb(d.S, d.ep) * 1e3
    return d


def bw_sigma_ub(ep_kev, res: str, branch: str) -> np.ndarray:
    """Single-level Breit-Wigner, constant widths, in the cm frame."""
    r = RES[res]
    ecm = e_cm(ep_kev) / 1e3                                   # MeV
    k = np.sqrt(2 * MU_U * U_MEV * ecm) / 197.3269804          # fm^-1
    lam2_b = (1.0 / k) ** 2 / 100.0                            # barn
    er = e_cm(r['ep']) / 1e3
    gam = r['gam'] / 1e3
    gg = {'g0': r['gg0'], 'g1': r['gg1'], 'g01': r['gg0'] + r['gg1']}[branch] * 1e-6
    s = np.pi * lam2_b * OMEGA * (r['gp'] / 1e3) * gg / ((ecm - er) ** 2 + gam ** 2 / 4)
    return s * 1e6                                             # microbarn


class CrossSection:
    """sigma_g0 and sigma_g01 (ub) as resonances + a smooth remainder.

    The remainder is the measured cross section minus both Breit-Wigners,
    interpolated through the 441 keV peak (where the 0.5 keV-resolution data
    cannot be subtracted cleanly).  It is the non-resonant direct capture --
    E1, and it does not interfere with the M1 resonances in the
    angle-integrated cross section.
    """

    def __init__(self):
        self.z = read_zahnow()
        self.rem = {}
        for ch in ('g0', 'g01'):
            d = self.z[self.z.chan == ch].sort_values('ep')
            bw = sum(bw_sigma_ub(d.ep.values, r, ch) for r in RES)
            rem = d.sigma_ub.values - bw
            keep = np.abs(d.ep.values - 441.4) > 40
            self.rem[ch] = (d.ep.values[keep], np.clip(rem[keep], 0, None))

    def direct(self, ep, ch='g0'):
        x, y = self.rem[ch]
        ep = np.asarray(ep, float)
        # below the first point, scale with the Coulomb barrier (S constant)
        lo = s_to_sigma_mb(1.0, ep) / s_to_sigma_mb(1.0, x[0]) * y[0]
        return np.where(ep < x[0], lo, np.interp(ep, x, y))

    def res(self, ep, which, ch='g0'):
        return bw_sigma_ub(ep, which, ch)

    def total(self, ep, ch='g0'):
        return self.direct(ep, ch) + sum(self.res(ep, r, ch) for r in RES)


# --------------------------------------------------------------------------- #
# stopping and targets
# --------------------------------------------------------------------------- #
def _pstar() -> pd.DataFrame:
    return pd.read_csv(DATA / 'pstar_stopping.csv')


class Stopping:
    """Electronic + nuclear proton stopping, MeV cm2/g, by Bragg additivity."""

    def __init__(self):
        p = _pstar()
        self.tab = {m: (g.E_MeV.values, g.S_tot_MeVcm2_g.values)
                    for m, g in p.groupby('material')}

    def _el(self, m, e_mev):
        x, y = self.tab[m]
        return np.exp(np.interp(np.log(e_mev), np.log(x), np.log(y)))

    def element(self, el, e_mev):
        if el in self.tab:
            return self._el(el, e_mev)
        if el == 'F':                                           # Teflon C2F4
            wc = 2 * 12.011 / (2 * 12.011 + 4 * 18.998)
            return (self._el('Teflon', e_mev) - wc * self._el('C', e_mev)) / (1 - wc)
        if el == 'Li':                                          # LiF
            wli = 6.941 / (6.941 + 18.998)
            return (self._el('LiF', e_mev) - (1 - wli) * self.element('F', e_mev)) / wli
        raise KeyError(el)

    def compound(self, comp: dict, e_mev):
        aw = {'Li': 6.941, 'F': 18.998, 'O': 15.999, 'C': 12.011, 'H': 1.008,
              'Al': 26.982, 'Cu': 63.546}
        mtot = sum(aw[e] * n for e, n in comp.items())
        return sum(aw[e] * n / mtot * self.element(e, e_mev) for e, n in comp.items())


#: The target options.  Density in g/cm3 (bulk; evaporated films are lower).
TARGETS = {
    'LiF':        dict(comp={'Li': 1, 'F': 1}, rho=2.635),
    'Li2O':       dict(comp={'Li': 2, 'O': 1}, rho=2.013),
    'Li metal':   dict(comp={'Li': 1}, rho=0.534),
    'Li2CO3':     dict(comp={'Li': 2, 'C': 1, 'O': 3}, rho=2.11),
}


def n7_per_gram(name, f7=F_LI7_NAT):
    t = TARGETS[name]
    aw = {'Li': 6.941, 'F': 18.998, 'O': 15.999, 'C': 12.011}
    m = sum(aw[e] * n for e, n in t['comp'].items())
    return t['comp']['Li'] * f7 * N_AVO / m


def thin_yield(xs: CrossSection, stp: Stopping, target, ep0_kev, t_ug_cm2,
               f7=F_LI7_NAT, step_kev=0.1) -> dict:
    """Integrate captures while the proton slows through t_ug_cm2 of target.

    Returns gamma0 / gamma1 yields per proton, split by origin (17.64
    resonance, 18.15 resonance, direct capture), the energy loss, and the
    mean excitation energy of the gamma0 captures.
    """
    comp = TARGETS[target]['comp']
    n7 = n7_per_gram(target, f7)
    m_left = t_ug_cm2 * 1e-6
    e = float(ep0_kev)
    acc = dict(g0_17=0.0, g0_18=0.0, g0_dc=0.0, g1_res=0.0, g1_dc=0.0, w_estar=0.0)
    while m_left > 0 and e > 60:
        s = float(stp.compound(comp, e / 1e3))                   # MeV cm2/g
        dm = min(step_kev / 1e3 / s, m_left)
        de = dm * s * 1e3
        em = e - de / 2
        k = n7 * dm * 1e-30                                       # per ub
        r17 = float(xs.res(em, '17.64')) * k
        r18 = float(xs.res(em, '18.15')) * k
        dc = float(xs.direct(em)) * k
        acc['g0_17'] += r17
        acc['g0_18'] += r18
        acc['g0_dc'] += dc
        g1_res = sum(float(xs.res(em, rr, 'g1')) for rr in RES) * k
        acc['g1_res'] += g1_res
        acc['g1_dc'] += (float(xs.total(em, 'g01')) * k - r17 - r18 - dc - g1_res)
        acc['w_estar'] += (r17 + r18 + dc) * float(e_star(em))
        e -= de
        m_left -= dm
    g0 = acc['g0_17'] + acc['g0_18'] + acc['g0_dc']
    return dict(target=target, Ep_keV=ep0_kev, t_ug_cm2=t_ug_cm2,
                dE_keV=ep0_kev - e, Y_g0=g0, Y_g1=acc['g1_res'] + acc['g1_dc'],
                frac_g1_direct=acc['g1_dc'] / max(acc['g1_res'] + acc['g1_dc'], 1e-300),
                frac_17_64=acc['g0_17'] / g0 if g0 else np.nan,
                frac_18_15_res=acc['g0_18'] / g0 if g0 else np.nan,
                frac_direct=acc['g0_dc'] / g0 if g0 else np.nan,
                mean_Estar_MeV=acc['w_estar'] / g0 if g0 else np.nan)


# --------------------------------------------------------------------------- #
# IPC: Born multipoles from nTof_x17
# --------------------------------------------------------------------------- #
def _ipc_born():
    sys.path.insert(0, str(NTOF_X17))
    try:
        from sept26_prelim_analysis import ipc_born       # noqa: E402
    except Exception as exc:                              # pragma: no cover
        raise SystemExit(f'needs nTof_x17 (ipc_born) at {NTOF_X17}: {exc}')
    return ipc_born


def ipc_vectors(kind, n, w, seed=1):
    """Weighted IPC pairs with full lab momenta, decaying nucleus at rest.

    The same master formula as nTof_x17 ipc_born.sample, but keeping the
    directions (the toy needs them), with the virtual-photon direction
    isotropic.
    """
    ib = _ipc_born()
    rng = np.random.default_rng(seed)
    lo = 2 * M_E * (1 + 1e-12)
    M = np.exp(rng.uniform(np.log(lo), np.log(w), n))
    k = np.sqrt(np.clip(w ** 2 - M ** 2, 0, None))
    cs = rng.uniform(-1, 1, n)
    s_t, s_l, bstar = ib._lepton_tensors(M, cs)
    n_t, n_l = ib.nuclear_factors(kind, k, M, w)
    wt = np.clip((n_t * s_t + n_l * s_l) / M ** 4 * k * bstar * 2 * M ** 2, 0, None)
    return _pair_from_rest(M, k, w, cs, rng, wt)


def x17_vectors(n, w, mx, seed=2):
    """X17 from 8Be* at rest, isotropic, decaying isotropically to e+e-."""
    rng = np.random.default_rng(seed)
    ex = x17_energy(w, mx)
    k = np.sqrt(ex ** 2 - mx ** 2)
    cs = rng.uniform(-1, 1, n)
    return _pair_from_rest(np.full(n, mx), np.full(n, k), ex, cs, rng, np.ones(n))


def _pair_from_rest(M, k, w, cs, rng, wt):
    n = len(M)
    phi = rng.uniform(0, 2 * np.pi, n)
    ss = np.sqrt(1 - cs ** 2)
    e_s = M / 2
    p_s = np.sqrt(np.clip(e_s ** 2 - M_E ** 2, 0, None))
    gam = np.sqrt(M ** 2 + k ** 2) / M
    bet = k / np.sqrt(M ** 2 + k ** 2)
    # leptons in the frame where k is along z
    p1 = np.stack([p_s * ss * np.cos(phi), p_s * ss * np.sin(phi),
                   gam * (p_s * cs + bet * e_s)], 1)
    p2 = np.stack([-p1[:, 0], -p1[:, 1], gam * (-p_s * cs + bet * e_s)], 1)
    e1 = gam * (e_s + bet * p_s * cs)
    e2 = gam * (e_s - bet * p_s * cs)
    # rotate z -> isotropic k direction
    ct = rng.uniform(-1, 1, n)
    st = np.sqrt(1 - ct ** 2)
    ph = rng.uniform(0, 2 * np.pi, n)
    kz = np.stack([st * np.cos(ph), st * np.sin(ph), ct], 1)
    a = np.where(np.abs(kz[:, :1]) < 0.9, [[1, 0, 0]], [[0, 1, 0]])
    u = np.cross(kz, a)
    u /= np.linalg.norm(u, axis=1, keepdims=True)
    v = np.cross(kz, u)

    def rot(p):
        return p[:, :1] * u + p[:, 1:2] * v + p[:, 2:3] * kz
    q1, q2 = rot(p1), rot(p2)
    cosang = np.sum(q1 * q2, 1) / np.linalg.norm(q1, axis=1) / np.linalg.norm(q2, axis=1)
    return dict(p1=q1, p2=q2, ke1=e1 - M_E, ke2=e2 - M_E, w=wt,
                theta=np.degrees(np.arccos(np.clip(cosang, -1, 1))))


def arm_hit(p):
    """Index (0-3) of the Micromegas arm a straight lepton from the origin
    lands in, or -1.  Beam along z; arms are the planes x = +-D, y = +-D."""
    d = p / np.linalg.norm(p, axis=1, keepdims=True)
    best_t = np.full(len(d), np.inf)
    arm = np.full(len(d), -1)
    for i, (ax, sg) in enumerate([(0, 1), (0, -1), (1, 1), (1, -1)]):
        dn = d[:, ax] * sg
        t = np.where(dn > 0, MM_FACE_MM / np.where(dn > 0, dn, 1), np.inf)
        other = 1 - ax
        ok = (np.abs(d[:, other] * t) < MM_HALF_U) & (np.abs(d[:, 2] * t) < MM_HALF_Z)
        better = (t < best_t)
        arm = np.where(better & ok, i, np.where(better, -1, arm))
        best_t = np.minimum(best_t, t)
    return arm


def acceptance(ev, rng=None):
    """Two different arms hit, both leptons above KE_MIN; smeared angle."""
    rng = rng or np.random.default_rng(5)
    a1, a2 = arm_hit(ev['p1']), arm_hit(ev['p2'])
    ok = (a1 >= 0) & (a2 >= 0) & (a1 != a2) & (ev['ke1'] > KE_MIN) & (ev['ke2'] > KE_MIN)
    th = ev['theta'] + rng.normal(0, SIGMA_THETA_DEG, len(ok))
    return ok, th


# --------------------------------------------------------------------------- #
# the sums
# --------------------------------------------------------------------------- #
def yields_table(xs, stp) -> pd.DataFrame:
    """The scenarios: what earlier experiments ran, and what we might."""
    sc = [
        ('ATOMKI 2022, on 17.64', 'LiF', 450, 30, F_LI7_NAT),
        ('ATOMKI 2016, 18.15 res', 'Li2O', 1040, 300, F_LI7_NAT),
        ('ATOMKI 2016 anomaly', 'Li2O', 1100, 300, F_LI7_NAT),
        ('ATOMKI 2022 off-res', 'LiF', 1100, 300, F_LI7_NAT),
        ('ATOMKI 2022 direct', 'LiF', 800, 300, F_LI7_NAT),
        ('Hanoi 2024', 'LiF', 1225, 300, F_LI7_NAT),
        ('MEG II-2026 normalisation', 'Li2O', 1030, 700, F_LI7_NAT),
        ('LNL 2023-24, thin', 'LiF', 1031, 34, F_LI7_NAT),
        ('LNL 2023-24, thick', 'LiF', 1090, 935, F_LI7_NAT),
        ('Li metal 1 um, enriched', 'Li metal', 1050, 53.4, F_LI7_ENR),
        ('Li metal stops beam (ATOMKI 2016 mishap)', 'Li metal', 1100, 2.0e4, F_LI7_NAT),
        ('Li2O 300, enriched', 'Li2O', 1070, 300, F_LI7_ENR),
        ('Li2O 100, enriched', 'Li2O', 1050, 100, F_LI7_ENR),
    ]
    rows = []
    for name, tgt, ep, t, f7 in sc:
        r = thin_yield(xs, stp, tgt, ep, t, f7)
        r['scenario'] = name
        r['f7'] = f7
        rows.append(r)
    d = pd.DataFrame(rows)
    pps = 1e-6 / E_CHARGE                                          # p/s per uA
    d['g0_per_s_1uA'] = d.Y_g0 * pps
    d['g01_per_s_1uA'] = (d.Y_g0 + d.Y_g1) * pps
    d['heat_W_per_uA'] = d.dE_keV * 1e-3                           # in the layer
    return d[['scenario', 'target', 'f7', 'Ep_keV', 't_ug_cm2', 'dE_keV',
              'Y_g0', 'Y_g1', 'g0_per_s_1uA', 'g01_per_s_1uA',
              'frac_17_64', 'frac_18_15_res', 'frac_direct', 'frac_g1_direct', 'mean_Estar_MeV',
              'heat_W_per_uA']]


def excitation_table(xs) -> pd.DataFrame:
    ep = np.arange(100, 1501, 2.0)
    return pd.DataFrame(dict(
        Ep_keV=ep, sigma_g0_ub=xs.total(ep), sigma_g01_ub=xs.total(ep, 'g01'),
        res_17_64_g0_ub=xs.res(ep, '17.64'), res_18_15_g0_ub=xs.res(ep, '18.15'),
        direct_g0_ub=xs.direct(ep), direct_g01_ub=xs.direct(ep, 'g01')))


def ipc_coefficients() -> pd.DataFrame:
    ib = _ipc_born()
    rows = []
    for w in (14.6, 15.1, 17.64, 18.15):
        for kind in ('M1', 'E1'):
            rows.append(dict(W_MeV=w, multipole=kind, alpha_pair=ib.alpha_pair(kind, w)))
    return pd.DataFrame(rows)


def acceptance_table(n=400_000) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Opening-angle acceptance and window fractions for signal and IPC."""
    bins = np.arange(0, 181, 5)
    hists, rows = {}, []
    cases = [('X17 m=16.7, 18.15', lambda: x17_vectors(n, 18.15, 16.7)),
             ('X17 m=17.0, 18.15', lambda: x17_vectors(n, 18.15, 17.0)),
             ('X17 m=16.7, 17.64', lambda: x17_vectors(n, 17.64, 16.7)),
             ('IPC M1, 18.15', lambda: ipc_vectors('M1', 4 * n, 18.15)),
             ('IPC E1, 18.15', lambda: ipc_vectors('E1', 4 * n, 18.15)),
             ('IPC M1, 17.64', lambda: ipc_vectors('M1', 4 * n, 17.64)),
             ('IPC M1, 15.1', lambda: ipc_vectors('M1', 4 * n, 15.1)),
             ('IPC E1, 15.1', lambda: ipc_vectors('E1', 4 * n, 15.1))]
    for name, gen in cases:
        ev = gen()
        ok, th = acceptance(ev)
        w = ev['w'] / ev['w'].sum()
        gen_h, _ = np.histogram(ev['theta'], bins, weights=w)
        acc_h, _ = np.histogram(th[ok], bins, weights=w[ok])
        hists[name] = acc_h
        hists[name + ' (generated)'] = gen_h
        for lo, hi in ((120, 160), (125, 155), (130, 150)):
            rows.append(dict(case=name, window=f'{lo}-{hi}',
                             gen_frac=float(w[(ev['theta'] >= lo) & (ev['theta'] < hi)].sum()),
                             acc_geom_total=float(w[ok].sum()),
                             acc_in_window=float(w[ok & (th >= lo) & (th < hi)].sum())))
    h = pd.DataFrame(hists)
    h.insert(0, 'theta_lo_deg', bins[:-1])
    return pd.DataFrame(rows), h


def reach_table(ytab, acc, alpha, days=(1, 7, 30), currents=(0.8, 1.0, 4.0),
                window='125-155', g1_leak=None) -> pd.DataFrame:
    """3 sigma reach on R = X17/gamma0 by counting in an opening-angle window.

    B = IPC pairs (M1 from the resonances, E1 from direct capture) + cosmics.
    Counting is conservative; a template fit over the full angular range
    (what ATOMKI, MEG II and the ILL study do) is typically ~1.5x better.
    """
    g1_leak = F_G1_LEAK if g1_leak is None else g1_leak
    a = acc[acc.window == window].set_index('case').acc_in_window
    am1 = alpha.set_index(['W_MeV', 'multipole']).alpha_pair
    rows = []
    for _, y in ytab.iterrows():
        f17 = y.frac_17_64
        # IPC per gamma0 in the window, weighted by where the captures happened
        ipc = (f17 * am1[(17.64, 'M1')] * a['IPC M1, 17.64']
               + y.frac_18_15_res * am1[(18.15, 'M1')] * a['IPC M1, 18.15']
               + y.frac_direct * am1[(18.15, 'E1')] * a['IPC E1, 18.15'])
        g1 = y.Y_g1 / y.Y_g0 * ((1 - y.frac_g1_direct) * am1[(15.1, 'M1')] * a['IPC M1, 15.1']
                                + y.frac_g1_direct * am1[(15.1, 'E1')] * a['IPC E1, 15.1'])
        # R here is the 18.15 MeV (and direct-capture) ratio, the ATOMKI claim.
        # Captures in the 17.64 resonance only add background: MEG II already
        # limits R(17.6) < 1.8e-6.
        sig = a['X17 m=16.7, 18.15'] * (1 - f17)
        for cur in currents:
            for dd in days:
                ng0 = y.Y_g0 * cur * 1e-6 / E_CHARGE * dd * 86400
                for cname, c in COSMICS_PER_DAY.items():
                    b = ng0 * (ipc + g1_leak * g1) * EPS_REST + c * dd
                    s_per_r = ng0 * sig * EPS_REST
                    rows.append(dict(scenario=y.scenario, I_uA=cur, days=dd,
                                     cosmics=cname, g1_leak=g1_leak, N_g0=ng0,
                                     B_ipc=ng0 * ipc * EPS_REST,
                                     B_ipc_g1=ng0 * g1_leak * g1 * EPS_REST, B_cosmic=c * dd,
                                     S_at_ATOMKI=s_per_r * R_ATOMKI_2016,
                                     R_3sigma=3 * np.sqrt(b) / s_per_r))
    return pd.DataFrame(rows)


def viewer_grid(xs, stp) -> dict:
    """The yield grid embedded as `Y` in viz/lnl_setup_3d.html (paste the JSON
    from out/viewer_yield_grid.json over it after any change to this model)."""
    films = {'li2o300': ('Li2O', 300, F_LI7_NAT), 'lif300': ('LiF', 300, F_LI7_NAT),
             'lif30': ('LiF', 30, F_LI7_NAT), 'lif935': ('LiF', 935, F_LI7_NAT),
             'li1um': ('Li metal', 53.4, F_LI7_ENR)}
    out = {}
    for key, (tgt, t, f7) in films.items():
        out[key] = {}
        for ep in (441, 650, 800, 1040, 1100, 1225):
            r = thin_yield(xs, stp, tgt, ep, t, f7, step_kev=0.2)
            out[key][str(ep)] = dict(g0=float(f"{r['Y_g0']:.3g}"), g1=float(f"{r['Y_g1']:.3g}"),
                                     dE=round(r['dE_keV'], 1), f17=round(r['frac_17_64'], 3),
                                     fdc=round(r['frac_direct'], 3), es=round(r['mean_Estar_MeV'], 3))
    return out


# --------------------------------------------------------------------------- #
# figures
# --------------------------------------------------------------------------- #
def figures(ex, kin, acc_h, ytab, xs, stp):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use()

    # 1. the excitation function: data, the model, and its parts
    fig, ax = fs.figure()
    z = xs.z
    for ch, c, lab in (('g0', fs.ACCENT, 'γ₀ data (Zahnow 1995)'),
                       ('g01', fs.MUTED, 'γ₀+γ₁ data')):
        d = z[z.chan == ch]
        ax.plot(d.ep, d.sigma_ub, 'o', ms=3, color=c, label=lab)
    ax.plot(ex.Ep_keV, ex.sigma_g0_ub, color=fs.ACCENT, lw=1.2, label='γ₀ model')
    ax.plot(ex.Ep_keV, ex.res_17_64_g0_ub, ':', color='#0072B2', label='17.64 resonance (BW)')
    ax.plot(ex.Ep_keV, ex.res_18_15_g0_ub, ':', color='#D55E00', label='18.15 resonance (BW)')
    ax.plot(ex.Ep_keV, ex.direct_g0_ub, '--', color=fs.COPPER, label='direct capture (rest)')
    ax.set_yscale('log')
    ax.set_ylim(0.3, 1e4)
    ax.set_xlabel('proton energy, lab [keV]')
    ax.set_ylabel('σ [µb]')
    ax.legend(frameon=False, fontsize=8, loc='upper right')
    fs.title(ax, 'At the 18.15 MeV resonance, half of γ₀ is direct capture',
             '⁷Li(p,γ)⁸Be: measured S-factors converted to σ, split into two Breit-Wigners + remainder')
    fs.save(fig, FIGS / 'excitation', data=ex)

    # 2. yield vs beam energy for thin targets
    rows = []
    for tgt, t in (('LiF', 30), ('LiF', 300), ('Li2O', 300), ('Li metal', 53.4)):
        for ep in np.arange(300, 1401, 10):
            r = thin_yield(xs, stp, tgt, ep, t, step_kev=0.25)
            rows.append(dict(target=f'{tgt} {t:g} µg/cm²', Ep_keV=ep, Y_g0=r['Y_g0'],
                             frac_17_64=r['frac_17_64']))
    yv = pd.DataFrame(rows)
    fig, ax = fs.figure()
    for i, (k, g) in enumerate(yv.groupby('target', sort=False)):
        ax.plot(g.Ep_keV, g.Y_g0, color=['#0072B2', '#D55E00', '#009E73', '#CC79A7'][i], label=k)
    ax.set_yscale('log')
    ax.set_xlabel('beam energy at the target face [keV]')
    ax.set_ylabel('γ₀ per proton')
    ax.legend(frameon=False, fontsize=8)
    fs.title(ax, 'The 18.15 MeV resonance is a 2x bump; the 441 keV one is 50x',
             'γ₀ yield per incident proton, natural Li; thicker layers reach 441 keV from above ~460-530 keV')
    fs.save(fig, FIGS / 'yield_vs_energy', data=yv)

    # 3. opening-angle acceptance
    fig, ax = fs.figure()
    x = acc_h.theta_lo_deg + 2.5
    for name, c in (('X17 m=16.7, 18.15', fs.ACCENT), ('X17 m=17.0, 18.15', '#CC79A7'),
                    ('IPC M1, 18.15', '#0072B2'), ('IPC E1, 18.15', '#D55E00')):
        y = acc_h[name] / max(acc_h[name].sum(), 1e-30)
        ax.step(x, y, where='mid', color=c, label=name)
    ax.set_yscale('log')
    ax.set_xlabel('measured opening angle [deg] (σ = 5°)')
    ax.set_ylabel('fraction of accepted pairs / 5°')
    ax.axvspan(125, 155, color=fs.BAND_SIGNAL, alpha=0.08)
    ax.legend(frameon=False, fontsize=8, loc='lower left')
    fs.title(ax, 'The four n_TOF arms see the 140° region through opposite arms',
             'toy: two different arms hit, KE > 1 MeV; shape only')
    fs.save(fig, FIGS / 'acceptance', data=acc_h)

    # 4. theta_min vs mass and energy
    rows = []
    for ep in (441.4, 800, 1030, 1100, 1225):
        for mx in np.arange(16.0, 17.81, 0.05):
            rows.append(dict(Ep_keV=ep, m_X=mx, theta_min=float(theta_min(float(e_star(ep)), mx))))
    tm = pd.DataFrame(rows)
    fig, ax = fs.figure(figsize=fs.HALF)
    for i, (ep, g) in enumerate(tm.groupby('Ep_keV')):
        ax.plot(g.m_X, g.theta_min, color=['#0072B2', '#009E73', '#D55E00', fs.ACCENT, '#CC79A7'][i],
                label=f'{ep:g} keV')
    ax.set_xlabel('m(X17) [MeV]')
    ax.set_ylabel('θ_min [deg]')
    ax.legend(frameon=False, fontsize=8)
    fs.title(ax, 'The X17 edge moves 10° per 0.5 MeV')
    fs.save(fig, FIGS / 'theta_min', data=tm)


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--quick', action='store_true', help='small MC, no figures')
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)

    xs, stp = CrossSection(), Stopping()

    # --- checks against anchors ---------------------------------------------
    pk = float(xs.total(441.4, 'g01'))
    print(f'CHECK  sigma(g0+g1) at 441.4 keV = {pk/1e3:.2f} mb   (Tilley: 5.9 +- 0.5 mb)')
    print(f'CHECK  g0/(g0+g1) at 441.4 keV = {float(xs.total(441.4))/pk:.2f}   (Tilley: 0.69-0.72)')
    print(f'CHECK  sigma(g0) at 1030 keV   = {float(xs.total(1030.0)):.1f} ub, of which '
          f'resonance {float(xs.res(1030.0, "18.15")):.1f} ub  (MEG-2026 uses "~20 ub")')
    for el in ('Li', 'F'):
        print(f'CHECK  S_{el}(1 MeV) = {float(stp.element(el, 1.0)):.0f} MeV cm2/g (derived)')
    s_lipon = float(stp.compound({'Li': 3, 'O': 4}, 1.0)) * 2.4 * 1e3 / 1e4
    print(f'CHECK  ~LiPON (Li3PO4-like, 2.4 g/cc) at 1 MeV: {s_lipon:.0f} keV/um   (MEG II: ~40)')
    thick = thin_yield(xs, stp, 'Li metal', 470, 2e3)
    print(f'CHECK  thick Li metal through 441: Y(g0+g1) = {thick["Y_g0"]+thick["Y_g1"]:.2e}/p, '
          f'Y(g0) = {thick["Y_g0"]:.2e}/p  (measured "17.6 MeV" thick yield 3.2e-9/p, target unknown)')
    for tg in ('LiF', 'Li2O'):
        th = thin_yield(xs, stp, tg, 470, 2e3)
        print(f'CHECK  thick {tg} through 441: Y(g0) = {th["Y_g0"]:.2e}/p, Y(g0+g1) = {th["Y_g0"]+th["Y_g1"]:.2e}/p')
    meg = thin_yield(xs, stp, 'Li2O', 1030, 700)
    print(f'CHECK  Li2O 700 ug/cm2 at 1030 keV: Y(g0) = {meg["Y_g0"]:.2e}/p  (MEG-2026 estimate 1.5e-10)')

    kin = kinematics_table()
    ex = excitation_table(xs)
    ytab = yields_table(xs, stp)
    alpha = ipc_coefficients()
    a181 = alpha[(alpha.W_MeV == 18.15) & (alpha.multipole == 'M1')].alpha_pair.item()
    print(f'CHECK  IPC alpha(M1, 18.15) Born = {a181:.2e}   (Rose, used by ATOMKI: 3.9e-3)')
    acc, acc_h = acceptance_table(60_000 if args.quick else 400_000)
    reach = pd.concat([reach_table(ytab, acc, alpha, g1_leak=1.0),
                       reach_table(ytab, acc, alpha, g1_leak=0.0)])

    import json
    (OUT / 'viewer_yield_grid.json').write_text(json.dumps(viewer_grid(xs, stp), separators=(',', ':')))
    for name, d in (('kinematics', kin), ('excitation', ex), ('yields', ytab),
                    ('ipc_alpha', alpha), ('acceptance', acc), ('acceptance_hist', acc_h),
                    ('reach', reach)):
        d.to_csv(OUT / f'{name}.csv', index=False)
        print(f'  -> {OUT / (name + ".csv")}')

    pd.set_option('display.width', 200)
    pd.set_option('display.max_columns', 30)
    print('\n== kinematics ==\n', kin.round(3).to_string(index=False))
    print('\n== yields ==\n', ytab.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    print('\n== IPC coefficients ==\n', alpha.to_string(index=False))
    print('\n== acceptance (125-155) ==\n',
          acc[acc.window == '125-155'].to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    sel = reach[(reach.I_uA == 1.0) & (reach.g1_leak == 1.0)]
    print('\n== reach, 1 uA ==\n', sel.pivot_table(index=['scenario', 'days'], columns='cosmics',
                                                   values='R_3sigma').to_string(float_format=lambda v: f'{v:.2e}'))
    if not args.quick:
        figures(ex, kin, acc_h, ytab, xs, stp)
    return 0


if __name__ == '__main__':
    sys.exit(main())
