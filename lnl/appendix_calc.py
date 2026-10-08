#!/usr/bin/env python3
"""appendix_calc.py -- the numbers behind the deck's "basics" appendix.

    python lnl/appendix_calc.py        # -> lnl/out/appendix/*.csv

Small analytic tables, no Monte Carlo of the detector:

  depth.csv        proton energy and gamma0 production against depth, for a thin
                   Li2O film and for a Li-metal target that stops the beam
                   (lnl_rates.thin_yield's integration, step by step).
  offres.csv       thin Li2O 300 ug/cm2 yields against E_p, split into the 17.64
                   resonance, the 18.15 resonance and direct capture.
  highland.csv     multiple scattering of an 8.6 MeV lepton in chamber-wall options
                   (Highland), turned into an opening-angle resolution with a
                   two-parameter model calibrated on the Geant4 L5 chamber scan.
                   An analytic stand-in, not Geant4.
  x17_decay.csv    lab opening angle of the X17 pair against the decay angle in the
                   X17 frame, for three excitation energies.
  energy.csv       where the beam energy goes: E_p -> centre-of-mass energy + recoil of
                   the 8Be*, E*, the gamma0 energy, and the X17 energy, kinetic energy,
                   speed and smallest opening angle (m = 16.7 and 17.0), against E_p.
  boost.csv        recoil velocities (8Be* here, 4He* at n_TOF) and what the 8Be*
                   recoil does to the X17 opening angle (toy MC).
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

import lnl_rates as lr

OUT = lr.OUT / 'appendix'
M_E = lr.M_E
P_LEP = 8.6                      # MeV/c, one lepton of an 18 MeV pair
L_MM = 215.0                     # mm, mid-drift of the Micromegas (faces at 204, 30 mm drift)
X0_CM = {'CFRP': 42.7 / 1.55,    # carbon X0 at the Geant4 CFRP density (1.55 g/cm3)
         'Al': 8.897, 'Be': 35.28, 'Kapton': 28.57, 'Mylar': 28.54}


def depth_profile(xs, stp, target, ep0, t_ug, step_kev=1.0):
    """E(x) and dY/dx, split by origin; mirrors lnl_rates.thin_yield."""
    comp = lr.TARGETS[target]['comp']
    rho = lr.TARGETS[target]['rho']
    n7 = lr.n7_per_gram(target)
    m, e, rows = 0.0, float(ep0), []
    while m < t_ug * 1e-6 and e > 60:
        s = float(stp.compound(comp, e / 1e3))
        dm = min(step_kev / 1e3 / s, t_ug * 1e-6 - m)
        de = dm * s * 1e3
        em = e - de / 2
        k = n7 * dm * 1e-30
        rows.append(dict(target=target, depth_ug_cm2=(m + dm / 2) * 1e6, depth_um=(m + dm / 2) / rho * 1e4,
                         E_keV=em, dE_keV=de,
                         g0_17_64=float(xs.res(em, '17.64')) * k, g0_18_15=float(xs.res(em, '18.15')) * k,
                         g0_direct=float(xs.direct(em)) * k))
        m += dm
        e -= de
    d = pd.DataFrame(rows)
    tot = d[['g0_17_64', 'g0_18_15', 'g0_direct']].sum(axis=1)
    d['cum_g0'] = tot.cumsum()
    d['cum_frac_17_64'] = d.g0_17_64.cumsum() / d.cum_g0
    return d


def highland(x_over_x0, p=P_LEP):
    """Plane-projected rms scattering angle [rad], beta = 1."""
    return 13.6 / p * math.sqrt(x_over_x0) * (1 + 0.038 * math.log(x_over_x0))


def chamber_table():
    """sigma68(opening angle) = sqrt(s0^2 + (k * theta0 * lever)^2), fitted to L5."""
    scan = pd.read_csv(lr.OUT / 'geant' / 'material_scan.csv')
    scan = scan[(scan['sample'] == 'X17_m16.7') & (scan.level == 'MM 15°')].set_index('variant').sigma68
    geant = {('CFRP', 0.4, 25): scan['baseline (CFRP 0.4, Al 10 µm)'],
             ('Al', 0.5, 25): scan['chAl0.5'], ('Al', 1.0, 25): scan['chAl1']}

    def term(mat, t, r):
        th = math.degrees(highland(t / 10 / X0_CM[mat]))
        return th, th * (L_MM - r) / L_MM

    # linear least squares in (s0^2, k^2) on the three Geant4 points
    A = np.array([[1.0, term(*key)[1] ** 2] for key in geant])
    b = np.array([v ** 2 for v in geant.values()])
    (s02, k2), *_ = np.linalg.lstsq(A, b, rcond=None)
    s0, k = math.sqrt(s02), math.sqrt(k2)
    opts = [('CFRP', 0.4, 25, 'baseline (Geant4 L1)'), ('Al', 0.5, 25, 'Al tube (Geant4 L5)'),
            ('Al', 1.0, 25, 'Al tube (Geant4 L5)'), ('CFRP', 0.2, 25, 'thinner CFRP'),
            ('CFRP', 0.4, 60, 'wider CFRP tube'), ('CFRP', 0.4, 100, 'much wider CFRP tube'),
            ('Kapton', 0.05, 25, 'CFRP tube with a Kapton window band'),
            ('Be', 0.25, 25, 'Be tube'), (None, 0.0, 25, 'no wall at all (vacuum to the MM)')]
    rows = []
    for mat, t, r, what in opts:
        if mat is None:
            th = eff = 0.0
            xx0 = 0.0
        else:
            xx0 = t / 10 / X0_CM[mat]
            th, eff = term(mat, t, r)
        s68 = math.sqrt(s0 ** 2 + (k * eff) ** 2)
        rows.append(dict(material=mat or 'none', t_mm=t, r_mm=r, what=what, x_over_X0=xx0,
                         theta0_deg=th, lever=(L_MM - r) / L_MM, sigma68_model_deg=s68,
                         sigma68_geant_deg=geant.get((mat, t, r), np.nan), s0_deg=s0, k=k))
    return pd.DataFrame(rows)


def x17_opening(w, mx, cos_star):
    """Lab opening angle [deg] of X -> e+e- with the X17 emitted from rest at E_X = w."""
    g = w / mx
    b = math.sqrt(1 - 1 / g ** 2)
    ps = math.sqrt((mx / 2) ** 2 - M_E ** 2)
    es = mx / 2
    out = []
    for c in cos_star:
        s = math.sqrt(max(0.0, 1 - c * c))
        v = []
        for sgn in (1, -1):
            pz = g * (sgn * ps * c + b * es)
            v.append(np.array([sgn * ps * s, pz]))
        ang = math.degrees(math.acos(max(-1.0, min(1.0, float(np.dot(v[0], v[1]) / np.linalg.norm(v[0]) / np.linalg.norm(v[1]))))))
        out.append(ang)
    return out


def energy_table():
    """The energy bookkeeping of p + 7Li -> 8Be* -> 8Be + (gamma | X17), against E_p."""
    mp = lr.M_P_U * lr.U_MEV
    rows = []
    for ep in sorted(set(np.arange(300.0, 1501.0, 10.0)) | {441.4, 1030.0, 1225.0}):
        ecm = float(lr.e_cm(ep))
        es = float(lr.e_star(ep))
        tp = ep / 1e3
        pp = math.sqrt(tp ** 2 + 2 * tp * mp)
        wtot = lr.M_BE8 + es                                     # 8Be* mass
        r = dict(Ep_keV=ep, p_proton_MeVc=pp, Ecm_keV=ecm, recoil_keV=ep - ecm, Estar_MeV=es,
                 Q_MeV=lr.Q_PG, beta_8Be=float(lr.beta_cm(ep)),
                 Egamma0_MeV=(wtot ** 2 - lr.M_BE8 ** 2) / (2 * wtot))
        for mx in (16.7, 17.0):
            ex_ = float(lr.x17_energy(es, mx))
            r[f'EX_m{mx}'] = ex_
            r[f'KE_X_m{mx}'] = ex_ - mx
            r[f'beta_X_m{mx}'] = math.sqrt(1 - (mx / ex_) ** 2)
            r[f'theta_min_m{mx}'] = float(lr.theta_min(es, mx))
        rows.append(r)
    return pd.DataFrame(rows)


def boost_table(n=200_000, seed=3):
    rng = np.random.default_rng(seed)
    rows = []
    # 8Be* from 7Li + p; 4He* from 3He + n
    for ep in (441.4, 1030.0, 1225.0):
        rows.append(dict(system='p + 7Li -> 8Be*', E_beam_MeV=ep / 1e3, beta=float(lr.beta_cm(ep))))
    m_n, m_he4 = 939.565, 3727.379
    for en in (2.5e-8, 2.0, 14.0):
        p = math.sqrt(en ** 2 + 2 * m_n * en)
        rows.append(dict(system='n + 3He -> 4He*', E_beam_MeV=en, beta=p / (m_he4 + 20.577 + 0.75 * en)))
    b = pd.DataFrame(rows)
    # what beta(8Be*) = 0.0059 does to the X17 opening angle
    mx, w, beta = 16.7, 18.15, float(lr.beta_cm(1030.0))
    gx = w / mx
    px = math.sqrt(w ** 2 - mx ** 2)
    ps, es = math.sqrt((mx / 2) ** 2 - M_E ** 2), mx / 2

    def iso(k):
        c = rng.uniform(-1, 1, k)
        ph = rng.uniform(0, 2 * math.pi, k)
        s = np.sqrt(1 - c * c)
        return np.stack([s * np.cos(ph), s * np.sin(ph), c], 1)

    dx, de = iso(n), iso(n)
    # leptons in the X frame, then boost along dx (X momentum), then along z (8Be* recoil)
    def boost(e, p, bvec):
        bb = np.linalg.norm(bvec, axis=-1, keepdims=True)
        g = 1 / np.sqrt(1 - bb ** 2)
        nhat = bvec / bb
        pl = np.sum(p * nhat, -1, keepdims=True)
        return g * (e + bb * pl), p + ((g - 1) * pl + g * bb * e) * nhat
    lep = []
    for sgn in (1, -1):
        e = np.full((n, 1), es)
        p = sgn * ps * de
        e, p = boost(e, p, dx * (px / w))
        lep.append((e, p))

    def opening(l1, l2):
        c = np.sum(l1 * l2, -1) / np.linalg.norm(l1, axis=-1) / np.linalg.norm(l2, axis=-1)
        return np.degrees(np.arccos(np.clip(c, -1, 1)))
    th0 = opening(lep[0][1], lep[1][1])
    bz = np.tile([0, 0, beta], (n, 1))
    th1 = opening(boost(*lep[0], bz)[1], boost(*lep[1], bz)[1])
    dth = th1 - th0
    b.attrs['dtheta'] = dict(beta_8Be=beta, beta_X=px / w, mean_abs_dtheta_deg=float(np.mean(np.abs(dth))),
                             p99_abs_dtheta_deg=float(np.percentile(np.abs(dth), 99)),
                             theta_min_deg=float(th0.min()), gamma_X=gx)
    return b


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    xs, stp = lr.CrossSection(), lr.Stopping()
    d = pd.concat([depth_profile(xs, stp, 'Li2O', 1100.0, 300.0, 0.25),
                   depth_profile(xs, stp, 'Li metal', 1100.0, 20000.0, 1.0)])
    d.to_csv(OUT / 'depth.csv', index=False)
    for t, g in d.groupby('target'):
        print(f'{t}: {g.depth_um.max():.2f} um, E {g.E_keV.max():.0f} -> {g.E_keV.min():.0f} keV, '
              f'frac 17.64 {g.cum_frac_17_64.iloc[-1]:.3f}')

    rows = []
    for ep in np.arange(400, 1501, 10.0):
        y = lr.thin_yield(xs, stp, 'Li2O', ep, 300.0)
        rows.append(dict(Ep_keV=ep, Y_g0=y['Y_g0'], frac_17_64=y['frac_17_64'],
                         frac_18_15_res=y['frac_18_15_res'], frac_direct=y['frac_direct'],
                         g0_per_s_1uA=y['Y_g0'] * 1e-6 / lr.E_CHARGE))
    pd.DataFrame(rows).to_csv(OUT / 'offres.csv', index=False)

    ch = chamber_table()
    ch.to_csv(OUT / 'highland.csv', index=False)
    print(ch[['material', 't_mm', 'r_mm', 'theta0_deg', 'sigma68_model_deg', 'sigma68_geant_deg']].round(2).to_string())

    cs = np.linspace(-1, 1, 201)
    xd = pd.DataFrame({'cos_star': cs})
    for w in (17.64, 18.15, 18.33):
        xd[f'open_deg_W{w}'] = x17_opening(w, 16.7, cs)
    xd.to_csv(OUT / 'x17_decay.csv', index=False)

    en = energy_table()
    en.to_csv(OUT / 'energy.csv', index=False)
    print(en[en.Ep_keV.isin([441.4, 800.0, 1030.0, 1225.0])].round(4).T.to_string())

    b = boost_table()
    b.to_csv(OUT / 'boost.csv', index=False)
    pd.DataFrame([b.attrs['dtheta']]).to_csv(OUT / 'boost_dtheta.csv', index=False)
    print(b.to_string(), b.attrs['dtheta'])


if __name__ == '__main__':
    main()
