#!/usr/bin/env python3
"""
bham_beam.py -- the Birmingham HF-ADNeF neutron and γ source for the X17 study
(birmingham/FACILITY.md, FEASIBILITY.md).

    python birmingham/bham_beam.py            # -> birmingham/out/bham_spectra.{csv,png}, bham_beam.csv

Thick ⁷Li(p,n)⁷Be on the rotating Li target (~0.3 mm natural Li on Cu: protons stop in it).
A Monte Carlo of the slowing-down: each proton energy E_p between the beam energy and the
1.881 MeV threshold contributes ∝ σ(E_p)/S(E_p); the neutron is emitted isotropically in the
CM (stand-in: the real CM distribution is forward-peaked above ~2.3 MeV, which would raise
the 0° yield) and carried to the lab by non-relativistic two-body kinematics.  The absolute
yield is normalised to the facility's own number (> 3×10¹³ n/s at 30 mA, 2.6 MeV; Wheldon,
STFC seminar 2025-02-06), not to the σ/S model.

σ_tot(E_p): a smooth stand-in for the Macklin & Gibbons shape quoted by Lee & Zhou (1999):
270 mb within 50 keV of threshold, the 580 mb resonance at 2.25 MeV, ~290 mb at 2.6 MeV.
S(E_p) ∝ E_p^-0.8 (the Bethe slope for protons in Li at 2-3 MeV).

γ from the target (⁷Li(p,γ)⁸Be through the 441 keV and 1030 keV 1⁺ resonances and the direct
capture; demokritos/neutron/NEUTRON_BEAM.md §5 and lnl/PHYSICS.md): ~1×10⁻⁷ γ/p at
14.6-18.2 MeV for a thick target above 1.1 MeV, split γ₀:γ₁ ≈ 1:2.  Isotropic.
"""
from __future__ import annotations

import functools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / 'out'
M_P, M_N, M_LI, M_BE = 938.272, 939.565, 6533.83, 6534.18      # MeV (nuclear masses)
Q = -1.644                                                    # MeV
E_TH = 1.8807                                                 # MeV
Y_REF = 3e13 / 30e-3                                          # n/s per A at 2.6 MeV (facility: > 3e13 n/s at 30 mA)
GAMMA_PER_P = 1e-7                                            # 14.6-18.2 MeV γ per proton, thick target
E_CHARGE = 1.602176634e-19

SIG_TAB = np.array([[1.8807, 0], [1.89, 90], [1.90, 170], [1.92, 270], [1.95, 285], [2.0, 300], [2.1, 360],
                    [2.2, 520], [2.25, 580], [2.3, 545], [2.4, 430], [2.5, 340], [2.6, 290], [2.7, 270],
                    [2.8, 260], [3.0, 250]])


def sigma_mb(ep):
    return np.interp(ep, SIG_TAB[:, 0], SIG_TAB[:, 1])


def stopping(ep):
    return ep ** -0.8


def mc(ep0, n=2_000_000, seed=1):
    """(E_n, cosθ_lab, weight) for neutrons from a thick target at beam energy ep0; weights sum to
    the yield per proton in units of the model's σ/S integral (normalised later)."""
    rng = np.random.default_rng(seed)
    ep = rng.uniform(E_TH + 1e-4, ep0, n)
    w = sigma_mb(ep) / stopping(ep) * (ep0 - E_TH) / n
    # CM: total kinetic energy after the reaction, neutron CM speed
    mu_i = M_P * M_LI / (M_P + M_LI)
    e_cm_i = ep * M_LI / (M_P + M_LI)
    e_cm_f = e_cm_i + Q
    ok = e_cm_f > 0
    mu_f = M_N * M_BE / (M_N + M_BE)
    p_cm = np.sqrt(2 * mu_f * np.clip(e_cm_f, 0, None))           # MeV/c, both products
    v_n_cm = p_cm / M_N
    v_cm = np.sqrt(2 * ep / M_P) * M_P / (M_P + M_LI)             # c units (non-rel.)
    cth = rng.uniform(-1, 1, n)                                   # isotropic CM (stand-in)
    vx = v_n_cm * np.sqrt(1 - cth ** 2)
    vz = v_n_cm * cth + v_cm
    v2 = vx ** 2 + vz ** 2
    e_n = 0.5 * M_N * v2
    cl = vz / np.sqrt(v2)
    # dΩ_lab weighting is implicit: we histogram in the lab
    del mu_i
    return e_n[ok], cl[ok], w[ok]


@functools.lru_cache(maxsize=None)
def spectra(ep0, ebins=tuple(np.linspace(0.0, 1.3, 66)), n=8_000_000):
    """0° spectrum (per sr, cosθ > 0.99) and angular distribution, absolute (n/s per A per sr per MeV)."""
    ebins = np.asarray(ebins)
    e, c, w = mc(ep0, n)
    tot_model = w.sum()
    # absolute normalisation: total yield at 2.6 MeV = Y_REF; the energy dependence from the model
    w26 = mc(2.6, n)[2] if ep0 != 2.6 else w
    scale = Y_REF / w26.sum()
    w = w * scale
    sel = c > 0.99                                                      # within 8°: the Ø8 cm spot at ≥ 1 m is < 2.3°
    dom = 2 * np.pi * (1 - 0.99)
    h0, _ = np.histogram(e[sel], ebins, weights=w[sel])
    dyde0 = h0 / dom / np.diff(ebins)                                   # n/s/A/sr/MeV at 0°
    k = np.ones(5) / 5                                                  # 5-bin running mean: MC noise only
    sm = np.convolve(dyde0, k, 'same')
    edge = np.nonzero(dyde0 > 0)[0]
    if len(edge):                                                       # keep the kinematic end point sharp
        sm[edge[-1] + 1:] = 0
        sm[edge[-1] - 1:edge[-1] + 1] = dyde0[edge[-1] - 1:edge[-1] + 1]
    dyde0 = sm * (dyde0.sum() / max(sm.sum(), 1e-300))
    cb = np.linspace(-1, 1, 41)
    ha, _ = np.histogram(c, cb, weights=w)
    dyd_omega = ha / (2 * np.pi * np.diff(cb))                          # n/s/A/sr vs cosθ
    return dict(ebins=ebins, dyde0=dyde0, y0=float(dyde0 @ np.diff(ebins)), ytot=float(tot_model * scale),
                cbins=cb, dydo=dyd_omega, mean0=float((h0 * 0.5 * (ebins[1:] + ebins[:-1])).sum() / max(h0.sum(), 1e-30)),
                emax0=float(e[sel].max()))


def beam(ep0=2.6, current_a=30e-3, dist_m=2.0, area_cm2=50.0):
    """neutrons/s through a collimated area at dist_m on the 0° axis, and the γ field."""
    s = spectra(ep0)
    omega = area_cm2 / (dist_m * 100) ** 2
    n_cell = s['y0'] * current_a * omega
    g_tot = GAMMA_PER_P * current_a / E_CHARGE
    g_cell = g_tot / (4 * np.pi) * omega
    return dict(ep=ep0, current_mA=current_a * 1e3, dist_m=dist_m, n_tot=s['ytot'] * current_a,
                n_per_sr_0deg=s['y0'] * current_a, forward_gain=s['y0'] * 4 * np.pi / s['ytot'],
                n_cell=n_cell, flux_at_cell=n_cell / area_cm2, mean_En0=s['mean0'], max_En0=s['emax0'],
                gamma_tot=g_tot, gamma_cell=g_cell), s


def spectrum_on_grid(ep0, e_grid):
    """normalised 0° dN/dE on an arbitrary grid (MeV), for the reach model."""
    s = spectra(ep0)
    x = 0.5 * (s['ebins'][1:] + s['ebins'][:-1])
    f = np.interp(e_grid, x, s['dyde0'], left=0.0, right=0.0)
    return f / np.trapezoid(f, e_grid)


def shield(ok_pencil_per_arm, dist_m=2.0, arm_cm2=75 * 75, eps=(1e-6, 1e-5, 1e-4), tvl_cm=10.0, margin=0.1,
           ep0=2.6, current_a=30e-3):
    """How much shield the 4π field needs (an estimate, not Geant4): neutrons per second that would reach
    one arm (75 × 75 cm face) at dist_m with no shield, the transmission T that keeps their ok singles
    below margin × the pencil beam's own (ok_pencil_per_arm, from soft_reach), for a range of ok singles
    per neutron entering an arm (eps), and the borated-PE thickness for that T at one tenth-value layer
    of tvl_cm (fast 0.1-1 MeV neutrons, with build-up; stand-in)."""
    b, _ = beam(ep0, current_a, dist_m)
    flux = b['n_per_sr_0deg'] / (dist_m * 100) ** 2          # forward flux, n/cm²/s (the arms sit near 0°)
    n_arm = flux * arm_cm2
    rows = []
    for e in eps:
        T = margin * ok_pencil_per_arm / (n_arm * e)
        rows.append(dict(eps=e, n_arm_unshielded=n_arm, T_needed=T, bpe_cm=max(0.0, -tvl_cm * np.log10(T))))
    return pd.DataFrame(rows)


def src_tables(ep0=2.8, out_dir=OUT):
    """(cosθ, E) tables for the Geant4 point source (MX17_Full_Geant bham --src; TARGET_GEANT.md §3):
    neutrons from the slowing-down MC (yield per proton in w, so the table's sum is n per proton) and the
    ⁸Be γ lines (isotropic, GAMMA_PER_P per proton, γ0:γ1 = 1:2, the 441 and 1030 keV resonances 0.6:0.4)."""
    e, c, w = mc(ep0, 4_000_000)
    s = spectra(ep0)
    w = w * s['ytot'] / w.sum() * E_CHARGE                       # n per proton
    cb, eb = np.linspace(-1, 1, 41), np.arange(0.0, 1.26, 0.02)
    h, _, _ = np.histogram2d(c, e, (cb, eb), weights=w)
    rows = [(cb[i], cb[i + 1], eb[j], eb[j + 1], h[i, j]) for i in range(len(cb) - 1) for j in range(len(eb) - 1)
            if h[i, j] > 0]
    pn = out_dir / f'bham_src_n_{ep0 * 10:.0f}.csv'
    with open(pn, 'w') as f:
        f.write(f'# Birmingham thick-Li 7Li(p,n) at E_p = {ep0} MeV: neutrons per proton in (cos theta, E_n [MeV]) cells\n'
                '# (bham_beam.py slowing-down MC, CM-isotropic stand-in, normalised to 3e13 n/s at 30 mA, 2.6 MeV)\n'
                f'# total {h.sum():.4g} n/p\ncos_lo,cos_hi,E_lo,E_hi,w\n')
        for r in rows:
            f.write('%.4g,%.4g,%.4g,%.4g,%.5g\n' % r)
    lines = [(17.64, 0.6 / 3), (18.15, 0.4 / 3), (14.64, 1.2 / 3), (15.15, 0.8 / 3)]
    pg = out_dir / 'bham_src_g8be.csv'
    with open(pg, 'w') as f:
        f.write(f'# Birmingham 7Li(p,gamma)8Be lines, isotropic, {GAMMA_PER_P:g} gamma per proton (ESTIMATE)\n'
                'cos_lo,cos_hi,E_lo,E_hi,w\n')
        for E, fr in lines:
            f.write(f'-1,1,{E - 0.01:.3f},{E + 0.01:.3f},{GAMMA_PER_P * fr:.4g}\n')
    return pn, pg, float(h.sum())


def main():
    OUT.mkdir(exist_ok=True)
    rows, sp = [], []
    for ep in (2.3, 2.5, 2.6, 2.8):
        b, s = beam(ep)
        rows.append(b)
        x = 0.5 * (s['ebins'][1:] + s['ebins'][:-1])
        sp += [dict(E_p=ep, E_n=xi, dYdE_0deg_per_sr_per_mA=v * 1e-3) for xi, v in zip(x, s['dyde0'])]
    t = pd.DataFrame(rows)
    t.to_csv(OUT / 'bham_beam.csv', index=False, float_format='%.4g')
    print(src_tables(2.8))
    sr = HERE.parent / 'survey' / 'soft_sim' / 'out' / 'soft_components.csv'
    if sr.exists():
        c = pd.read_csv(sr)
        c = c[(c.key == 'bham_28_2m_pb5') & (c.hw == 'big plastics')]
        if len(c):
            sh = shield(float(c.ok_singles_per_arm.iloc[0]), ep0=2.8)
            sh.to_csv(OUT / 'bham_shield.csv', index=False, float_format='%.4g')
            print(sh.to_string(index=False))
    d = pd.DataFrame(sp)
    pd.set_option('display.width', 200)
    print(t.to_string(index=False))
    sys.path.insert(0, str(HERE.parent / 'ill'))
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use()
    fig, ax = fs.figure()
    for ep, col in zip((2.3, 2.5, 2.6, 2.8), (fs.MUTED, fs.COPPER, fs.ACCENT, fs.TRACK)):
        q = d[d.E_p == ep]
        ax.plot(q.E_n, q.dYdE_0deg_per_sr_per_mA, color=col, lw=1.6, label=f'E_p = {ep} MeV')
    ax.set_xlabel('E_n [MeV]')
    ax.set_ylabel('dY/dE dΩ at 0° [n / (s mA sr MeV)]')
    ax.legend(frameon=False, fontsize=8)
    fs.title(ax, 'Thick-Li ⁷Li(p,n) at 0°: everything below ~1 MeV',
             'CM-isotropic stand-in, normalised to 3×10¹³ n/s at 30 mA, 2.6 MeV')
    fs.save(fig, OUT / 'bham_spectra', data=d)


if __name__ == '__main__':
    main()
