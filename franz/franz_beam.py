#!/usr/bin/env python3
"""
franz_beam.py -- the Frankfurt Neutron Source FRANZ (near-threshold ⁷Li(p,n)) for the X17 study
(franz/FACILITY.md, FEASIBILITY.md), and its reach with the shared Geant4 soft-beam background.

    python franz/franz_beam.py                 # beam model + reach -> franz/out/franz_*.{csv,png}
    python franz/franz_beam.py --beam-only     # the beam model only (no Geant4 tables needed)

Beam model.  ⁷Li(p,n)⁷Be on a Li layer on Cu, protons 1.9-2.2 MeV (threshold 1.881 MeV).  The
slowing-down Monte Carlo and the σ(E_p) stand-in are Birmingham's (`birmingham/bham_beam.py`): each
proton energy between the beam energy and the exit energy from the Li contributes ∝ σ/S, the
neutron is emitted isotropically in the CM (near threshold the reaction is s-wave, so this is a fair
stand-in here) and carried to the lab.  Near threshold the CM speed of the neutron is below that of
the CM, so every neutron goes forward: at 1.912 MeV into a 60° half-cone ("kinematic collimation",
the Karlsruhe quasi-stellar 25 keV field).

Absolute yield: the σ/S integral with S(Li, 2 MeV) = 0.19 MeV cm²/mg (PSTAR-like, estimate) gives
~7×10¹⁰ n/s per mA at 2.0 MeV; FRANZ's own design number is 10¹² n/s at 20 mA (5×10¹⁰ n/s/mA;
Reifarth et al. 2014, arXiv:1403.5670) and LiLiT measured ~2×10¹⁰ n/s/mA at ~1.92-1.94 MeV.  The
model is normalised to FRANZ's 5×10¹⁰ n/s/mA at 2.0 MeV; its energy dependence sets the other E_p.

γ from the target:
  478 keV  ⁷Li(p,p'γ): 6×10⁻⁵/p thick at 2.5 MeV (Taskaev 2006), scaled ∝ ((E_p − 0.55)/1.95)² below
           (stand-in), plus ⁷Be decay (10.4 %) at the saturated activity (one ⁷Be per neutron).
  14.6-18.2 MeV ⁷Li(p,γ)⁸Be: a THICK Li target slows every proton through the 441 and 1030 keV
           resonances: ~1×10⁻⁷ γ/p (the Birmingham stand-in).  A THIN Li layer that stops protons
           only at the (p,n) threshold (FRANZ: ~10 µm evaporated Li on Cu) never reaches them; then
           only direct capture at 1.88-2.2 MeV is left: n σ_DC Δx ≈ 5×10⁻¹⁰ /p (σ_DC ≈ 10 µb, estimate).

Time structure.  Today's ion source (CHORDIS) runs 0.5-1 ms macro-pulses at 10 Hz (0.5-1 % duty; Hähnel,
LINAC 2024), and the licence allows < 5 % duty and 10¹² n/s (IPAC 2025).  Inside a pulse the
175 MHz bunches are continuous for MX17.  A pulsed source is handled here, not in soft_reach.py:
the Geant4 components are computed at the in-pulse rate, then per day
    signal, IPC, correlated   × duty
    accidentals               × duty (∝ in-pulse rate²)
    cosmics                   × duty (the DAQ is gated on the macro-pulse)
    DREAM live time, occupancy at the in-pulse rate.
"""
from __future__ import annotations

import argparse
import functools
import sys
from pathlib import Path

import numpy as np
import pandas as pd
if not hasattr(np, 'trapezoid'):
    np.trapezoid = np.trapz

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'out'
sys.path.insert(0, str(ROOT / 'birmingham'))
import bham_beam as BB                                        # noqa: E402

E_TH = BB.E_TH
E_CHARGE = BB.E_CHARGE
P_PER_MA = 1e-3 / E_CHARGE                                    # protons/s per mA
Y_DESIGN = 1e12 / 20.0                                        # n/s per mA at 2.0 MeV (FRANZ design: 1e12 n/s, 20 mA)
S_LI = 0.19                                                   # MeV cm²/mg, p in Li at ~2 MeV (estimate)
N_LI7 = 0.925 * 6.022e23 / 6.94 * 1e-3                        # ⁷Li atoms per mg of natural Li
G478_25 = 6e-5                                                # 478 keV γ/p, thick Li, 2.5 MeV (Taskaev 2006)
G15_THICK = 1e-7                                              # 14.6-18.2 MeV γ/p, thick Li (Birmingham stand-in)
SIG_DC_CM2 = 1e-29                                            # ⁷Li(p,γ) direct capture at ~2 MeV, ~10 µb (estimate)
N_LICENCE = 1e12                                              # n/s, the licence limit (IPAC 2025)
AREA = 50.0                                                   # cm², the Ø8 cm cell spot
TAU_BE7 = 53.22 / np.log(2) * 86400                           # s
MU_PB = {'n': 0.36, 'g478': 1.76, 'g15': 0.57}                # /cm, Pb: keV n uncollided (σ ≈ 11 b; estimate),
                                                              # γ 478 keV, γ 15-18 MeV (NIST XCOM)
E_FINE = np.linspace(0.0, 0.7, 351)                           # 2 keV bins


# --------------------------------------------------------------------------- #
@functools.lru_cache(maxsize=None)
def mc(ep0, e_exit=E_TH, n=4_000_000, seed=2):
    """slowing-down MC from ep0 down to e_exit (≥ threshold): (E_n, cosθ_lab, w), w in n/p (absolute σ/S)."""
    rng = np.random.default_rng(seed)
    lo = max(e_exit, E_TH + 1e-5)
    ep = rng.uniform(lo, ep0, n)
    # absolute: dY = n_Li7 σ dE / S, with S ∝ E^-0.8 anchored at S_LI (MeV cm²/mg) at 2 MeV
    s = S_LI * (ep / 2.0) ** -0.8
    w = N_LI7 * BB.sigma_mb(ep) * 1e-27 / s * (ep0 - lo) / n
    e_cm_f = ep * BB.M_LI / (BB.M_P + BB.M_LI) + BB.Q
    ok = e_cm_f > 0
    mu_f = BB.M_N * BB.M_BE / (BB.M_N + BB.M_BE)
    v_n_cm = np.sqrt(2 * mu_f * np.clip(e_cm_f, 0, None)) / BB.M_N
    v_cm = np.sqrt(2 * ep / BB.M_P) * BB.M_P / (BB.M_P + BB.M_LI)
    cth = rng.uniform(-1, 1, n)
    vx = v_n_cm * np.sqrt(1 - cth ** 2)
    vz = v_n_cm * cth + v_cm
    v2 = vx ** 2 + vz ** 2
    return 0.5 * BB.M_N * v2[ok], (vz / np.sqrt(v2))[ok], w[ok]


def model_yield_per_ma(ep0, e_exit=E_TH):
    return mc(ep0, e_exit)[2].sum() * P_PER_MA


NORM = Y_DESIGN / model_yield_per_ma(2.0)                     # applied to every E_p


@functools.lru_cache(maxsize=None)
def spectra(ep0, e_exit=E_TH):
    """0° spectrum (cosθ > 0.99) per sr, and the angular distribution, in n/s per mA (design-normalised)."""
    e, c, w = mc(ep0, e_exit)
    w = w * P_PER_MA * NORM
    sel = c > 0.99
    dom = 2 * np.pi * 0.01
    h0, _ = np.histogram(e[sel], E_FINE, weights=w[sel])
    dyde0 = h0 / dom / np.diff(E_FINE)
    cb = np.linspace(-1, 1, 81)
    ha, _ = np.histogram(c, cb, weights=w)
    x = 0.5 * (E_FINE[1:] + E_FINE[:-1])
    return dict(dyde0=dyde0, y0=float(h0.sum() / dom), ytot=float(w.sum()), cbins=cb,
                dydo=ha / (2 * np.pi * np.diff(cb)), mean0=float((h0 * x).sum() / max(h0.sum(), 1e-30)),
                emax0=float(e[sel].max()), cmin=float(c.min()),
                f_below_1keV=float(w[sel & (e < 1e-3)].sum() / max(w[sel].sum(), 1e-300)))


def spectrum_on_grid(ep0, e_grid, e_exit=E_TH):
    s = spectra(ep0, e_exit)
    x = 0.5 * (E_FINE[1:] + E_FINE[:-1])
    f = np.interp(e_grid, x, s['dyde0'], left=0.0, right=0.0)
    return f / np.trapezoid(f, e_grid)


def gammas_per_p(ep0, thick):
    """(478 keV prompt γ/p, 14.6-18.2 MeV γ/p)."""
    g478 = G478_25 * max(0.0, (ep0 - 0.55) / 1.95) ** 2
    if thick:
        g15 = G15_THICK
    else:
        dx_mg = (ep0 - E_TH) / S_LI                           # mg/cm² of Li to reach the threshold
        g15 = N_LI7 * dx_mg * SIG_DC_CM2
    return g478, g15


def beam(ep0=2.0, i_ma=10.0, dist_m=0.5, thick=False, pb_cm=0.0):
    """in-pulse neutron and γ rates through the Ø8 cm spot at dist_m on the 0° axis."""
    s = spectra(ep0)
    om = AREA / (dist_m * 100) ** 2
    n_cell = s['y0'] * i_ma * om * np.exp(-MU_PB['n'] * pb_cm)
    p_s = i_ma * P_PER_MA
    g478, g15 = gammas_per_p(ep0, thick)
    be7 = s['ytot'] * i_ma * 0.104                            # saturated ⁷Be activity × 478 keV branch
    f4 = om / (4 * np.pi)
    return dict(ep=ep0, i_mA=i_ma, dist_m=dist_m, thick=thick, pb_cm=pb_cm,
                n_tot=s['ytot'] * i_ma, n_per_sr_0deg=s['y0'] * i_ma, forward_gain=s['y0'] * 4 * np.pi / s['ytot'],
                n_cell=n_cell, flux_at_cell=n_cell / AREA, mean_En0_keV=s['mean0'] * 1e3, max_En0_keV=s['emax0'] * 1e3,
                cos_min=s['cmin'], f_below_1keV=s['f_below_1keV'],
                g478_cell=(g478 * p_s + be7) * f4 * np.exp(-MU_PB['g478'] * pb_cm),
                g15_cell=g15 * p_s * f4 * np.exp(-MU_PB['g15'] * pb_cm), g15_per_p=g15)


def shield(ok_pencil_per_arm, n_per_sr, dist_m, arm_cm2=75 * 75, eps=(1e-6, 1e-5, 1e-4), tvl_cm=5.0, margin=0.1):
    """Birmingham's estimate for the field around the target (not Geant4), with a keV tenth-value layer
    of borated PE (5 cm, stand-in: σ_H ≈ 18 b at 30 keV, ¹⁰B 1/v)."""
    n_arm = n_per_sr / (dist_m * 100) ** 2 * arm_cm2
    rows = []
    for e in eps:
        T = margin * ok_pencil_per_arm / (n_arm * e)
        rows.append(dict(eps=e, n_arm_unshielded=n_arm, T_needed=T, bpe_cm=max(0.0, -tvl_cm * np.log10(T))))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# Reach: the soft_reach.py engine, with a duty factor.
SCEN = {  # name: (in-pulse current mA, duty, what); capped at the licence (10¹² n/s average)
    'first':   (10.0, 0.01, 'today: 10 mA macro-pulses, 1 ms at 10 Hz (CHORDIS, 1 %)'),
    'licence': (10.0, 0.05, 'licence limit: 10 mA at 5 % duty'),
    'design':  (20.0, 1.00, 'design: 20 mA DC (10¹² n/s)'),
}


REF = dict(i_ma=1.0, dist_m=1.0)                              # components are computed once at 1 mA in pulse, 1 m


def sources():
    """one Geant4 re-weighting per (E_p, Li thickness, Pb): every rate scales with I·Ω, so the
    scenarios and distances are the same source at another intensity (k = rate / reference)."""
    import soft_reach as SR
    S = []
    hi = [(17.64, 0.6 / 3), (18.15, 0.4 / 3), (14.64, 1.2 / 3), (15.15, 0.8 / 3)]
    for ep in (1.912, 2.0, 2.2):
        for thick in (False, True):
            for pb in (0.0, 5.0):
                b = beam(ep, REF['i_ma'], REF['dist_m'], thick, pb)
                fg, g_tot = SR._mix([(SR._lines([(0.478, 1.0)]), b['g478_cell']), (SR._lines(hi), b['g15_cell'])])
                key = f'franz_{ep * 1000:.0f}_{"thick" if thick else "thin"}_pb{pb:.0f}'
                src = SR.Soft(key, f'FRANZ E_p {ep} MeV, {"thick" if thick else "thin"} Li, {pb:.0f} cm Pb; 1 mA, 1 m',
                              spectrum_on_grid(ep, SR.E_GRID), b['n_cell'], fg, g_tot, 'franz',
                              note=f'per mA at 1 m: γ 478 {b["g478_cell"]:.2g}/s, 15-18 MeV {b["g15_cell"]:.2g}/s')
                src.ep, src.thick, src.pb = ep, thick, pb
                S.append(src)
    return S


def at_pulsed(SR, src, C, M, cap, s, duty):
    """soft_reach.at_throttle for a macro-pulsed beam: components at the in-pulse rate × s, then
    signal, IPC, cosmics (gated DAQ), accidentals and correlated × duty per day."""
    st = SR.at_throttle(src, C, M, cap, s)
    st['c_sig'] = st['c_sig'] * duty
    st['B'] = {k: v * duty for k, v in st['B'].items()}
    return st


def reach(days=(14.0, 50.0), only=None):
    sys.path.insert(0, str(ROOT / 'survey' / 'soft_sim'))
    import soft_reach as SR
    SF, R, Y = SR.SF, SR.R, SR.Y
    srcs = sources()
    if only:
        srcs = [s for s in srcs if any(o in s.key for o in only)]
    rows, comps = [], []
    grid = np.geomspace(1e-3, 1.0, 31)
    for hw in R.HW:
        M = SF.nfs_model(hw)
        runs = SR.load_runs(hw)
        for src in srcs:
            C = SR.components(src, runs, hw, M)
            cap = SR.captures(src)
            print(f'{hw:13s} {src.key:24s} per mA at 1 m: n_cell {src.n_cell:.3g}/s  ok/arm {C["ok_arm"].mean():.3g}/s  '
                  f'legs/arm {C["leg_arm"].mean():.3g}/s  corr {C["corr_fact"]:.3g}/d ({C["corr_n_mc"]} MC)  '
                  f'γ share of ok {C["ok_g_frac"]:.2f}', flush=True)
            for scen, (i_ma, duty, what) in SCEN.items():
                i_ma = min(i_ma, N_LICENCE / duty / spectra(src.ep)['ytot'])   # average yield ≤ 10¹² n/s
                for d in (0.3, 0.5, 1.0):
                    k = i_ma / REF['i_ma'] * (REF['dist_m'] / d) ** 2
                    comps.append(dict(key=src.key, scen=scen, ep=src.ep, dist_m=d, i_pulse_mA=i_ma,
                                      n_tot_avg=spectra(src.ep)['ytot'] * i_ma * duty, thick=src.thick, pb_cm=src.pb,
                                      hw=hw, duty=duty, n_cell_pulse=src.n_cell * k, n_cell_avg=src.n_cell * k * duty,
                                      g_cell_pulse=src.g_cell * k, ok_singles_per_arm=C['ok_arm'].mean() * k,
                                      legs_per_arm=C['leg_arm'].mean() * k, ok_singles_gamma_frac=C['ok_g_frac'],
                                      corr_trig_per_s=C['corr_trig'] * k, corr_fact_per_day_pulse=C['corr_fact'] * k,
                                      corr_mc=C['corr_n_mc'], corr_gamma_frac=C['corr_g_frac'],
                                      ipc_per_day=float((cap * Y.alpha(np.array(R.NODES))).sum() * SR.DAY * k * duty)))
                    for dd in days:
                        res = []
                        for s in grid:
                            st = at_pulsed(SR, src, C, M, cap, s * k, duty)
                            res.append((SR.rho3(M, st, dd, True), s, st))
                        r, s, st = min(res, key=lambda x: x[0])
                        st0 = at_pulsed(SR, src, dict(C, acc_th=C['acc_th'] * 0, corr_th=C['corr_th'] * 0,
                                                      ok_arm=C['ok_arm'] * 0, leg_arm=C['leg_arm'] * 0, corr_trig=0.0),
                                        M, cap, k, duty)
                        rows.append(dict(key=src.key, scen=scen, ep=src.ep, dist_m=d, thick=src.thick, pb_cm=src.pb,
                                         duty=duty, i_pulse_mA=i_ma, hw=hw, days=dd, rho3=r, vs_ATOMKI=r / R.RHO_REF, throttle=s,
                                         rho3_floor=SR.rho3(M, st0, dd, True),
                                         days_to_atomki=50 * (r / R.RHO_REF) ** 2 if dd == 50 else np.nan,
                                         live=st['live'], occ=st['occ'], **SR.window_counts(st, M, True)))
    t, cp = pd.DataFrame(rows), pd.DataFrame(comps)
    t.to_csv(OUT / 'franz_reach.csv', index=False, float_format='%.4g')
    cp.to_csv(OUT / 'franz_components.csv', index=False, float_format='%.4g')
    return t, cp


# --------------------------------------------------------------------------- #
def beam_tables():
    rows, sp, ang = [], [], []
    for ep in (1.912, 1.95, 2.0, 2.1, 2.2):
        for d in (0.3, 0.5, 1.0):
            for thick in (False, True):
                rows.append(beam(ep, 1.0, d, thick))
        s = spectra(ep)
        x = 0.5 * (E_FINE[1:] + E_FINE[:-1])
        sp += [dict(E_p=ep, E_n_keV=xi * 1e3, dYdE_0deg_per_sr_per_mA_per_keV=v * 1e-3) for xi, v in zip(x, s['dyde0'])]
        xc = 0.5 * (s['cbins'][1:] + s['cbins'][:-1])
        ang += [dict(E_p=ep, theta_deg=np.degrees(np.arccos(c)), dYdOmega_per_mA=v) for c, v in zip(xc, s['dydo'])]
    t = pd.DataFrame(rows)
    t.to_csv(OUT / 'franz_beam.csv', index=False, float_format='%.4g')
    chk = dict(model_abs_per_mA_2p0=model_yield_per_ma(2.0), model_abs_per_mA_1p93=model_yield_per_ma(1.93),
               design_norm=NORM, lilit_check_per_mA=model_yield_per_ma(1.93) * NORM)
    print({k: f'{v:.3g}' for k, v in chk.items()})
    pd.Series(chk).to_csv(OUT / 'franz_yield_check.csv', header=['value'], float_format='%.4g')
    sys.path.insert(0, str(ROOT / 'ill'))
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use()
    d = pd.DataFrame(sp)
    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    cols = (fs.MUTED, fs.COPPER, fs.ACCENT, fs.TRACK, fs.INK if hasattr(fs, 'INK') else 'k')
    for ep, col in zip((1.912, 1.95, 2.0, 2.1, 2.2), cols):
        q = d[d.E_p == ep]
        axs[0].plot(q.E_n_keV, q.dYdE_0deg_per_sr_per_mA_per_keV, color=col, lw=1.5, label=f'E_p = {ep} MeV')
        a = pd.DataFrame(ang).query('E_p == @ep')
        axs[1].plot(a.theta_deg, a.dYdOmega_per_mA, color=col, lw=1.5)
    axs[0].set_xlabel('E_n [keV]')
    axs[0].set_ylabel('dY/dE dΩ at 0° [n / (s mA sr keV)]')
    axs[0].set_xlim(0, 600)
    axs[0].legend(frameon=False, fontsize=8)
    axs[1].set_xlabel('θ_lab [deg]')
    axs[1].set_ylabel('dY/dΩ [n / (s mA sr)]')
    axs[1].set_yscale('log')
    fs.fig_title(fig, 'FRANZ near-threshold ⁷Li(p,n): keV neutrons, kinematically collimated',
                 'thin Li (stops at threshold), CM-isotropic, normalised to 5×10¹⁰ n/s/mA at 2.0 MeV (design)')
    fs.save(fig, OUT / 'franz_spectra', data=d)
    pd.DataFrame(ang).to_csv(OUT / 'franz_angular.csv', index=False, float_format='%.4g')
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--beam-only', action='store_true')
    ap.add_argument('--only', nargs='+', help='substrings of source keys')
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    pd.set_option('display.width', 250)
    t = beam_tables()
    print(t[(t.dist_m == 0.5) & (~t.thick)].to_string(index=False))
    if a.beam_only:
        return
    r, cp = reach(only=a.only)
    q = r[(r.days == 50) & (r.hw == 'big plastics')]
    print(q.pivot_table(index=['scen', 'ep', 'dist_m'], columns=['thick', 'pb_cm'], values='rho3').to_string())
    # the field around the target, for the two baselines (thin Li, 2.0 MeV, cell at 0.5 m)
    sh = []
    for scen in ('licence', 'design'):
        x = q[(q.key == 'franz_2000_thin_pb0') & (q.scen == scen) & (q.dist_m == 0.5)].iloc[0]
        c = cp[(cp.key == x.key) & (cp.hw == 'big plastics') & (cp.scen == scen) & (cp.dist_m == 0.5)].iloc[0]
        b = beam(2.0, c.i_pulse_mA, 0.5)
        h = shield(c.ok_singles_per_arm * x.throttle, b['n_per_sr_0deg'] * x.throttle, 0.5)
        h['scen'] = scen
        sh.append(h)
    sh = pd.concat(sh, ignore_index=True)
    sh.to_csv(OUT / 'franz_shield.csv', index=False, float_format='%.4g')
    print(sh.to_string(index=False))
    cols = ['scen', 'ep', 'dist_m', 'hw', 'i_pulse_mA', 'duty', 'rho3', 'rho3_floor', 'throttle', 'days_to_atomki', 'live',
            'occ', 'X17_win_per_day', 'IPC_win_per_day', 'cosmic_win_per_day', 'acc_win_per_day', 'corr_win_per_day']
    print(r[(r.days == 50) & (r.key == 'franz_2000_thin_pb0') | (r.days == 50) & (r.key == 'franz_2200_thin_pb0')
            & (r.dist_m == 0.5)][cols].to_string(index=False))

if __name__ == '__main__':
    main()
