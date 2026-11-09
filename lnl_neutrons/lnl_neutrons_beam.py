#!/usr/bin/env python3
"""
lnl_neutrons_beam.py -- a neutron-route ³He(n,e⁺e⁻) X17 measurement at Legnaro: what the existing CN Van de Graaff,
LENOS, the ANTHEM/MUNES RFQ + Be target and the SPES cyclotron can give, with the shared Geant4 soft-beam engine.

    python lnl_neutrons/lnl_neutrons_beam.py               # -> lnl_neutrons/out/lnl_neutrons_*.{csv,png}
    python lnl_neutrons/lnl_neutrons_beam.py --beam-only   # the beam model only

Sources (see FACILITY.md for the published numbers):
  CN        ⁷Li(p,n) on Li metal at E_p = 2.0-3.0 MeV.  franz_beam.mc (Birmingham's σ/S slowing-down MC, CM-isotropic),
            normalised to FRANZ's 5×10¹⁰ n/s/mA at 2.0 MeV (checks in out/lnl_neutrons_yield_check.csv).
  LENOS     7.3×10¹⁰ n/s forward, keV (Praena et al. 2009 design value), modelled by thin Li at 1.95 MeV.
  ANTHEM    ⁹Be(p,xn) at 5 MeV, 30 mA: bepn_beam (ENDF/B-VIII.0).  The machine is being built FOR CASERTA, not Legnaro.
  SPES      ⁹Be(p,xn) at 35 MeV, 750 µA (hypothetical port) at 90-130°.

Geometry.  At CN the rate forces the cell close to a point source, where a parallel beam through Ø8 cm is wrong:
each MC neutron is carried from the point target to the 30 bar × 40 cm × Ø8 cm cell, D cm upstream of its window,
and scored with its actual path in the gas:
    n_win  neutrons through the window (the rate seen by the Geant4 backgrounds)
    n_eff  Σ w·path/40 cm (the signal: captures ∝ path)
The Geant4 tables are the Ø8 cm parallel beam; the angle up to atan(4/D) is not in them.

Not in the engine: the 4π field into the arms, the room, the target chamber, air.  IPC pairs made IN the Li target
are added here as an ESTIMATE: target pair rate × a toy geometric acceptance relative to pairs in the cell.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
if not hasattr(np, 'trapezoid'):
    np.trapezoid = np.trapz

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'out'
for p in ('birmingham', 'franz', 'bepn_cyclotron', 'survey/soft_sim', 'ill'):
    sys.path.insert(0, str(ROOT / p))
import franz_beam as FB                                       # noqa: E402

E_CHARGE = 1.602176634e-19
P_PER_UA = 1e-6 / E_CHARGE
R_CELL, L_CELL = 4.0, 40.0                                    # cm, the 30 bar cell of N5/G5/G6
ALPHA_LI = 3.5e-3                                             # pairs per γ at 17-18 MeV (CLAUDE.md, ~20 MeV value; ESTIMATE)
EPS = (2.0, 2.3, 2.6, 2.8, 3.0)
DS = (5.0, 10.0, 20.0, 50.0, 100.0)                           # cm, Li target to cell window
# CN current scenarios (µA).  arXiv:2605.12005 §4: today 50 µSv/h monitor limits Li targets (0.3 µA at 5.5 MeV); the
# 5-10 cm BPE + Pb package (×4-6) gives ~1 µA up to E_n 4 MeV and 2-3 µA below 2 MeV.  'today' = 2.5/5 (ESTIMATE).
CN = {'today': (0.5, 'today: ~0.5 µA on Li (radiation limit at the switching magnet; ESTIMATE)'),
      'shielded': (2.5, 'with the shielding package under evaluation: 2-3 µA below E_n 2 MeV'),
      'authorised': (4.0, 'authorised continuous limit ~4 µA'),
      'technical': (6.0, 'technical maximum ~6 µA (needs a licence change and a better target)')}
VARIANTS = {'base': dict(veto=1.0, tgt=0.0), 'veto90': dict(veto=0.1, tgt=0.0), 'tgt_pairs': dict(veto=1.0, tgt=1.0),
            'veto90_tgt': dict(veto=0.1, tgt=1.0)}
LENOS_FORWARD = 7.3e10                                        # n/s forward (Praena 2009, design)
MU_PB_N = 0.20


def li_scale(ep):
    """absolute scale on top of FB.NORM: 1 at the FRANZ anchor (2.0 MeV) rising to ×1.89 at ≥ 2.5 MeV, where the model must match the
    measured thick-Li yields (Birmingham 1×10⁹, Lee & Zhou 9×10⁸ n/s/µA).  The σ(E_p) table of bham_beam is a stand-in; ESTIMATE."""
    return float(np.interp(ep, [2.0, 2.5], [1.0, 9e8 / (FB.model_yield_per_ma(2.5) * FB.NORM / 1e3)]))


# --------------------------------------------------------------------------- #
def geom(c, w, D, R=R_CELL, L=L_CELL):
    """(Σ w through the window, Σ w·path/L, the window's sub-sample mask)."""
    cw = D / np.hypot(D, R)
    m = c > cw
    th = np.arccos(np.clip(c[m], -1, 1))
    tn, cs = np.tan(np.clip(th, 1e-6, None)), c[m]
    z_out = np.minimum(D + L, R / tn)
    path = (z_out - D) / cs
    return w[m].sum(), (w[m] * path / L).sum()


def yield_checks():
    """the σ/S model against every published anchor."""
    rows = []
    nrm = FB.NORM
    y = lambda ep: FB.model_yield_per_ma(ep) * nrm / 1e3 * li_scale(ep)      # n/s/µA     # noqa: E731
    rows.append(dict(what='FRANZ design, 2.0 MeV (norm)', model_n_s_uA=y(2.0), reference=5e7, source='arXiv:1403.5670'))
    rows.append(dict(what='LiLiT, ~1.93 MeV', model_n_s_uA=y(1.93), reference=2e7, source='Paul et al. (SARAF LiLiT)'))
    rows.append(dict(what='Birmingham, 2.6 MeV', model_n_s_uA=y(2.6), reference=1e9, source='Wheldon 2025: > 3e13 n/s at 30 mA'))
    rows.append(dict(what='Lee & Zhou thick Li, 2.5 MeV', model_n_s_uA=y(2.5), reference=9e8, source='NIM B 152 (1999) 1'))
    # CN thin 40 µm Li at 4 MeV: PINO through 1.5 cm² at 5 cm (Table 2, arXiv:2605.12005) against a thin-slice estimate
    p = FB.N_LI7 * 40e-4 * 0.534 * 1e3 * 0.25e-24             # n/p, 40 µm Li, σ ≈ 250 mb (ESTIMATE, table ends at 3 MeV)
    pino = 2.76e9 / 5.88e15 / (1.5 / 25.0)                    # n/sr/p, 0°
    rows.append(dict(what='CN, thin 40 µm Li, 4 MeV: n/sr/p at 0° (σ·t, ×4π/4π)', model_n_s_uA=p / (4 * np.pi) * 3,
                     reference=pino, source='arXiv:2605.12005 Table 2 (PINO); model ×3 forward (ESTIMATE)'))
    t = pd.DataFrame(rows)
    t['ratio'] = t.model_n_s_uA / t.reference
    t.to_csv(OUT / 'lnl_neutrons_yield_check.csv', index=False, float_format='%.4g')
    return t


def li_beam(ep, i_ua, D, thick=False):
    e, c, w = FB.mc(ep)
    w = w * P_PER_UA * i_ua * FB.NORM * li_scale(ep)
    nw, ne = geom(c, w, D)
    om = 2 * np.pi * (1 - D / np.hypot(D, R_CELL))
    p_s = i_ua * P_PER_UA
    g478, g15 = FB.gammas_per_p(ep, thick)
    be7 = w.sum() * 0.104
    sel = c > 0.98
    dom = 2 * np.pi * 0.02
    return dict(ep=ep, i_uA=i_ua, D_cm=D, thick=thick, n_tot=float(w.sum()), y0_per_sr=float(w[sel].sum() / dom),
                n_win=float(nw), n_eff=float(ne), mean_En=float((e[sel] * w[sel]).sum() / w[sel].sum()), emax=float(e[sel].max()),
                om_sr=float(om), g478_win=(g478 * p_s + be7) * om / (4 * np.pi), g15_win=g15 * p_s * om / (4 * np.pi),
                g15_per_p=g15, tgt_pairs_per_s=g15 * ALPHA_LI * p_s)


def li_spectrum(ep, E):
    e, c, w = FB.mc(ep)
    sel = c > 0.95
    bins = np.linspace(0, 1.6, 321)
    h, _ = np.histogram(e[sel], bins, weights=w[sel])
    x = 0.5 * (bins[1:] + bins[:-1])
    f = np.interp(E, x, h, left=0, right=0)
    return f / np.trapezoid(f, E)


# Toy for the pairs made in the production target: acceptance of two-arm pairs at 100-150°, relative to the cell.
def _arm_of(p0, u):
    """first arm face hit (x = ±20.4 or z = ±20.4, |y| < 18, other coordinate < 20), else -1."""
    t = np.full(4, np.inf)
    for i, (ax, s) in enumerate(((0, 1), (0, -1), (2, 1), (2, -1))):
        with np.errstate(divide='ignore', invalid='ignore'):
            t[i] = (s * 20.4 - p0[ax]) / u[ax]
    t[(t <= 0) | ~np.isfinite(t)] = np.inf
    k = int(np.argmin(t))
    if not np.isfinite(t[k]):
        return -1
    h = p0 + t[k] * u
    other = 2 if k < 2 else 0
    return k if (abs(h[1]) < 18 and abs(h[other]) < 20) else -1


def pair_acceptance(y0_fn, n=30000, seed=3):
    rng = np.random.default_rng(seed)
    ok = 0
    for _ in range(n):
        p0 = y0_fn(rng)
        a = rng.normal(size=3)
        a /= np.linalg.norm(a)
        b = np.cross(a, [0.3, 0.5, 0.8])
        b /= np.linalg.norm(b)
        th = np.radians(rng.uniform(100, 150)) / 2
        phi = rng.uniform(0, 2 * np.pi)
        v = np.cos(phi) * b + np.sin(phi) * np.cross(a, b)
        u1 = np.cos(th) * a + np.sin(th) * v
        u2 = np.cos(th) * a - np.sin(th) * v
        k1, k2 = _arm_of(p0, u1), _arm_of(p0, u2)
        if k1 >= 0 and k2 >= 0 and k1 != k2:
            ok += 1
    return ok / n


def target_acceptance():
    cell = pair_acceptance(lambda r: np.array([0.0, r.uniform(-20, 20), 0.0]))
    rows = [dict(D_cm=d, acc=pair_acceptance(lambda r: np.array([0.0, -20.0 - d, 0.0]))) for d in DS]
    t = pd.DataFrame(rows)
    t['acc_cell'] = cell
    t['f'] = t.acc / cell
    t.to_csv(OUT / 'lnl_neutrons_target_acceptance.csv', index=False, float_format='%.4g')
    return t.set_index('D_cm').f.to_dict()


# Demokritos' capsule method: 500 bar capsule tip 1 cm from the source (the analytic bound).
def capsule_table(SR):
    n = 1.25e22
    rows = []
    for ep, thick_lab in ((2.5, 'thick Li'), (2.8, 'thin-stop Li'), (2.0, 'thin-stop Li')):
        e, c, w = FB.mc(ep)
        sel = c > 0.95
        s = SR.Y.sig(e[sel], 102) * SR.Y.alpha(e[sel])          # pair cross section [b]
        sig_pair = float((s * w[sel]).sum() / w[sel].sum()) * 1e-24
        for i_ua, G in ((1.0, 1.82), (4.0, 1.82)):
            y0 = float(w[c > 0.98].sum() / (2 * np.pi * 0.02) * P_PER_UA * i_ua * FB.NORM * li_scale(ep))
            pd_ = y0 * n * sig_pair * G * 86400
            rows.append(dict(ep=ep, target=thick_lab, i_uA=i_ua, G_cm=G, y0=y0, sig_pair_ub=sig_pair * 1e30,
                             pairs_per_day=pd_, days_bigP=3.44 * 1.84e6 / pd_, days_asbuilt=45.4 * 1.84e6 / pd_))
    t = pd.DataFrame(rows)
    t.to_csv(OUT / 'lnl_neutrons_capsule.csv', index=False, float_format='%.4g')
    return t


# --------------------------------------------------------------------------- #
def beam_tables():
    rows = [li_beam(ep, 1.0, d) for ep in EPS for d in DS]
    t = pd.DataFrame(rows)
    t.to_csv(OUT / 'lnl_neutrons_beam.csv', index=False, float_format='%.4g')
    chk = yield_checks()
    print(chk.to_string(index=False))
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use()
    E = np.linspace(0, 1.6, 321)
    sp = pd.DataFrame({'E_MeV': E, **{f'Ep_{ep}': li_spectrum(ep, E) for ep in EPS}})
    fig, ax = fs.figure()
    for ep, col in zip(EPS, (fs.MUTED, fs.COPPER, fs.ACCENT, fs.TRACK, fs.INK)):
        ax.plot(E, sp[f'Ep_{ep}'], color=col, lw=1.5, label=f'E_p = {ep} MeV')
    ax.set_xlabel('E_n [MeV]')
    ax.set_ylabel('normalised dN/dE, θ < 18° [1/MeV]')
    ax.legend(frameon=False, fontsize=8)
    fs.title(ax, 'CN ⁷Li(p,n): every neutron is inside the X17 window', 'thin-stop Li, CM-isotropic stand-in')
    fs.save(fig, OUT / 'lnl_neutrons_spectra', data=sp)
    return t


def sources(SR, E, BE, tgt_f):
    """(ref Soft, per-config dict). Every Li source is computed once at 1 µA, D = 10 cm and scaled."""
    S = []
    hi = [(17.64, 0.6 / 3), (18.15, 0.4 / 3), (14.64, 1.2 / 3), (15.15, 0.8 / 3)]
    for ep in EPS:
        for thick in (False, True) if ep == 2.8 else (False,):
            r = li_beam(ep, 1.0, 10.0, thick)
            fg, g = SR._mix([(SR._lines([(0.478, 1.0)]), r['g478_win']), (SR._lines(hi), r['g15_win'])])
            src = SR.Soft(f'cn_{ep * 1000:.0f}_{"thick" if thick else "thin"}', f'CN ⁷Li(p,n), {ep} MeV, {"thick" if thick else "thin-stop"} Li; 1 µA',
                          li_spectrum(ep, E), r['n_win'], fg, g, 'cn')
            src.kind, src.ep, src.thick = 'li', ep, thick
            S.append(src)
    return S


def run(SR, BE, BR, E, tgt_f, days_list=(14.0, 50.0)):
    rows, comps = [], []
    grid = np.geomspace(1e-3, 1.0, 25)
    for hw in SR.R.HW:
        M = SR.SF.nfs_model(hw)
        runs, _ = BR.load_runs(hw)
        for src in sources(SR, E, BE, tgt_f):
            C = SR.components(src, runs, hw, M)
            cap_ref = SR.captures(src)                         # per n_win (1 µA, 10 cm)
            ref = li_beam(src.ep, 1.0, 10.0, src.thick)
            scen_list = [('LENOS' , None)] if False else list(CN.items())
            for scen, (ia, what) in scen_list:
                ia = min(ia, 10.0 / src.ep) if scen in ('shielded', 'authorised') else ia   # 10 W target
                for D in DS:
                    b = li_beam(src.ep, ia, D, src.thick)
                    k = b['n_win'] / ref['n_win']
                    cap = cap_ref * (b['n_eff'] / b['n_win'])
                    _reach(SR, M, src, C, cap, k, hw, scen, what, ia, D, b, tgt_f, rows, comps, days_list, grid, ipc0=cap)
    return pd.DataFrame(rows), pd.DataFrame(comps)


def _reach(SR, M, src, C, cap, k, hw, scen, what, ia, D, b, tgt_f, rows, comps, days_list, grid, ipc0=None):
    ipc_day = float((cap * k * SR.Y.alpha(np.array(SR.R.NODES))).sum() * SR.DAY)
    tp_day = b.get('tgt_pairs_per_s', 0.0) * SR.DAY
    f = tgt_f.get(D, 0.0)
    Rt = tp_day * f / max(ipc_day, 1e-300)
    comps.append(dict(key=src.key, scen=scen, hw=hw, ep=src.ep, D_cm=D, i_uA=ia, n_tot=b['n_tot'], n_win=b['n_win'], n_eff=b['n_eff'],
                      ipc_per_day=ipc_day, tgt_pairs_per_day=tp_day, tgt_acc_f=f, tgt_over_ipc=Rt,
                      ok_singles_per_arm=C['ok_arm'].mean() * k, legs_per_arm=C['leg_arm'].mean() * k, corr_trig_per_s=C['corr_trig'] * k))
    for var, v in VARIANTS.items():
        if var != 'base' and scen != 'authorised' and scen != 'shielded':
            continue
        for days in days_list:
            for soft in (True, False):
                res = []
                for s in grid:
                    st = SR.at_throttle(src, C, M, cap, s * k)
                    st['B'] = dict(st['B'], cosmic=st['B']['cosmic'] * v['veto'])
                    if v['tgt']:
                        st['B']['tgt'] = st['B']['IPC'] * Rt
                    res.append((SR.rho3(M, st, days, soft), s, st))
                r, s, st = min(res, key=lambda x: x[0])
                st0 = SR.at_throttle(src, dict(C, acc_th=C['acc_th'] * 0, corr_th=C['corr_th'] * 0, ok_arm=C['ok_arm'] * 0,
                                               leg_arm=C['leg_arm'] * 0, corr_trig=0.0), M, cap, k)
                st0['B'] = dict(st0['B'], cosmic=st0['B']['cosmic'] * v['veto'])
                rows.append(dict(key=src.key, scen=scen, variant=var, ep=src.ep, thick=src.thick, D_cm=D, i_uA=ia, hw=hw, days=days,
                                 signal='E* ≤ 22 MeV' if soft else 'all E*', rho3=r, vs_ATOMKI=r / SR.R.RHO_REF,
                                 days_to_atomki=50 * (r / 1.5e-3) ** 2 if days == 50 else np.nan, throttle=s,
                                 rho3_floor=SR.rho3(M, st0, days, soft), live=st['live'], occ=st['occ'],
                                 n_win=b['n_win'], n_eff=b['n_eff'], tgt_over_ipc=Rt, **SR.window_counts(st, M, soft)))


def run_other(SR, BE, BR, E, days_list=(14.0, 50.0)):
    """LENOS (design forward yield), the ANTHEM 5 MeV Be source, SPES 35 MeV (keV source at ≥ 0.5 m; parallel-beam at ≥ 1 m)."""
    rows = []
    grid = np.geomspace(1e-4, 1.0, 33)
    cfgs = []
    # LENOS: thin Li at 1.95 MeV, the current that gives 7.3e10 n/s forward
    i_len = LENOS_FORWARD / (FB.model_yield_per_ma(1.95) * FB.NORM)      # mA
    for d in (0.1, 0.2, 0.5, 1.0):
        y0 = FB.spectra(1.95)['y0'] * i_len
        cfgs.append(('lenos', f'lenos_{d * 100:.0f}cm', d, 'LENOS design 7.3e10 n/s forward, keV (thin Li 1.95 MeV stand-in)', y0, 'li195'))
    for ep, cur, lab in ((5.0, 30e-3, 'ANTHEM design'), (5.0, 3e-3, '3 mA'), (5.0, 1e-3, '1 mA')):
        for th in (0.0, 90.0, 130.0):
            for d in (1.0, 2.0, 3.0):
                cfgs.append(('anthem', f'anthem{cur * 1e3:.0f}_{th:.0f}_{d:.0f}m', d, f'{lab} ⁹Be(p,n) {ep} MeV, θ={th:.0f}°, {d:.0f} m', None, (ep, cur, th, d)))
    for th in (90.0, 130.0):
        cfgs.append(('spes', f'spes35_{th:.0f}_2m', 2.0, f'SPES 35 MeV 750 µA, θ={th:.0f}°, 2 m (hypothetical port)', None, (35.0, 750e-6, th, 2.0)))
    for hw in SR.R.HW:
        M = SR.SF.nfs_model(hw)
        runs, _ = BR.load_runs(hw)
        for site, key, d, lab, y0, a in cfgs:
            if site == 'lenos':
                om = 50.0 / (d * 100) ** 2
                g478, g15 = FB.gammas_per_p(1.95, False)
                ps = i_len * FB.P_PER_MA
                fg, g = SR._mix([(SR._lines([(0.478, 1.0)]), g478 * ps * om / (4 * np.pi))])
                src = SR.Soft(key, lab, li_spectrum(1.95, E), y0 * om, fg, g, 'lenos')
            else:
                ep, cur, th, dd = a
                b = BE.beam(ep, cur, th, dd)
                src = SR.Soft(key, lab, BE.spectrum_on_grid(ep, th, E), b['n_cell'], BE.gamma_on_grid(ep, E), b['g_cell'], site)
            C = SR.components(src, runs, hw, M)
            cap = SR.captures(src)
            for days in days_list:
                for soft in (True, False):
                    res = [(SR.rho3(M, st := SR.at_throttle(src, C, M, cap, s), days, soft), s, st) for s in grid]
                    r, s, st = min(res, key=lambda x: x[0])
                    st0 = SR.at_throttle(src, dict(C, acc_th=C['acc_th'] * 0, corr_th=C['corr_th'] * 0, ok_arm=C['ok_arm'] * 0,
                                                   leg_arm=C['leg_arm'] * 0, corr_trig=0.0), M, cap, 1.0)
                    rows.append(dict(key=key, site=site, source=lab, hw=hw, days=days, signal='E* ≤ 22 MeV' if soft else 'all E*',
                                     rho3=r, vs_ATOMKI=r / SR.R.RHO_REF, days_to_atomki=50 * (r / 1.5e-3) ** 2 if days == 50 else np.nan,
                                     throttle=s, rho3_floor=SR.rho3(M, st0, days, soft), live=st['live'], occ=st['occ'], n_cell=src.n_cell,
                                     ok_singles_per_arm=C['ok_arm'].mean(), legs_per_arm=C['leg_arm'].mean(), **SR.window_counts(st, M, soft)))
            print(hw, key, f'rho3 50d soft {[x["rho3"] for x in rows if x["key"] == key and x["hw"] == hw and x["days"] == 50 and x["signal"].startswith("E*")]}', flush=True)
    t = pd.DataFrame(rows)
    t.to_csv(OUT / 'lnl_neutrons_other_reach.csv', index=False, float_format='%.4g')
    return t


def figure(t):
    import figstyle as fs
    fs.use()
    fig, ax = fs.figure()
    q = t[(t.key == 'cn_2800_thin') & (t.hw == 'big plastics') & (t.days == 50) & (t.signal == 'E* ≤ 22 MeV') & (t.variant == 'base')]
    for sc, col in (('today', fs.MUTED), ('shielded', fs.COPPER), ('authorised', fs.ACCENT), ('technical', fs.TRACK)):
        r = q[q.scen == sc].sort_values('D_cm')
        ax.plot(r.D_cm, r.rho3, '-o', color=col, lw=1.5, ms=3, label=f'{sc}: {r.i_uA.iloc[0]:.1f} µA')
    ax.axhline(1.5e-3, color=fs.INK, lw=0.8, ls='--')
    ax.text(5.5, 1.65e-3, 'ATOMKI ⁴He', fontsize=8, color=fs.INK)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Li target to cell window, D [cm]')
    ax.set_ylabel('X17/IPC at 3σ in 50 d')
    ax.legend(frameon=False, fontsize=8)
    fs.title(ax, 'CN at 2.8 MeV, thin-stop Li, 30 bar cell', 'big plastics, engine + point-source geometry, no target pairs, no room')
    fs.save(fig, OUT / 'lnl_neutrons_reach_D', data=q)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--beam-only', action='store_true')
    ap.add_argument('--skip-other', action='store_true')
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    pd.set_option('display.width', 280)
    pd.set_option('display.max_columns', 40)
    t0 = beam_tables()
    print(t0[t0.D_cm == 10].to_string(index=False))
    if a.beam_only:
        return
    # 1. reproduce a published row with the plain engine, before bepn_reach changes the grid
    import soft_reach as SR
    src = [s for s in SR.sources() if s.key == 'bham_28_2m_pb5'][0]
    M = SR.SF.nfs_model('big plastics')
    runs = SR.load_runs('big plastics')
    C = SR.components(src, runs, 'big plastics', M)
    cap = SR.captures(src)
    grid = np.geomspace(1e-4, 1.0, 41)
    r50 = min(SR.rho3(M, SR.at_throttle(src, C, M, cap, s), 50.0, True) for s in grid)
    pub = pd.read_csv(ROOT / 'survey/soft_sim/out/soft_reach.csv')
    pub = pub[(pub.key == 'bham_28_2m_pb5') & (pub.hw == 'big plastics') & (pub.days == 50) & (pub.signal == 'E* ≤ 22 MeV')].rho3.iloc[0]
    print(f'ENGINE CHECK bham_28_2m_pb5, big plastics, 50 d, E* ≤ 22: this script {r50:.4g}, soft_reach.csv {pub:.4g}, ratio {r50 / pub:.3f}')
    pd.DataFrame([dict(key='bham_28_2m_pb5', hw='big plastics', days=50, this_script=r50, published=float(pub), ratio=r50 / pub)]).to_csv(
        OUT / 'lnl_neutrons_engine_check.csv', index=False, float_format='%.4g')
    import bepn_reach as BR                                    # noqa: E402  (extends the engine to 30 MeV, as in bepn_cyclotron)
    import bepn_beam as BE
    E = SR.E_GRID
    print(capsule_table(SR).to_string(index=False))
    tgt_f = target_acceptance()
    print('target-pair acceptance rel. to cell:', tgt_f, flush=True)
    t, cp = run(SR, BE, BR, E, tgt_f)
    t.to_csv(OUT / 'lnl_neutrons_reach.csv', index=False, float_format='%.4g')
    cp.to_csv(OUT / 'lnl_neutrons_components.csv', index=False, float_format='%.4g')
    figure(t)
    q = t[(t.days == 50) & (t.signal == 'E* ≤ 22 MeV') & (t.variant == 'base') & (~t.thick)]
    print(q[q.hw == 'big plastics'].pivot_table(index=['scen', 'D_cm'], columns='ep', values='rho3').to_string())
    if not a.skip_other:
        o = run_other(SR, BE, BR, E)
        print(o[(o.days == 50) & (o.signal == 'E* ≤ 22 MeV')].pivot_table(index='key', columns='hw', values='rho3', sort=False).to_string())


if __name__ == '__main__':
    main()
