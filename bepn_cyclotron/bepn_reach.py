#!/usr/bin/env python3
"""
bepn_reach.py -- X17 reach of a thick-Be ⁹Be(p,n) cyclotron source with its own Geant4 beam background,
re-weighted from the broad-band runs of survey/soft_sim/ (the same engine as FRM II MEDAPP and Birmingham).

    python bepn_cyclotron/bepn_reach.py                 # -> bepn_cyclotron/out/bepn_reach.csv, bepn_components.csv,
                                                        #    bepn_throttle.csv, bepn_reach_fig.{png,csv}
    python bepn_cyclotron/bepn_reach.py --only npi24_90_2m --hw 'big plastics'

What is different from soft_reach.py:

* The spectrum reaches 28 MeV (30 MeV protons); the soft runs stop at 20 MeV.  Neutrons below 20 MeV are
  re-weighted from N5 (log-flat 1 keV-20 MeV, forced collisions), those above from the NFS forced run N4
  (`ganil_nfs/sim/sel_beam/N4_beam_force*`, generated on the NFS spectrum 0.1-40 MeV), each energy
  counted once.  N4 has no leg or hardware-trigger tables: its legs are its ok singles × the leg/ok ratio
  of N5 at 10-20 MeV, and its two-arm triggers are its two-arm ok events (a lower bound).  At 24 MeV the
  > 20 MeV share is 3 % at 0° and 0 at 90°; at 18 MeV nothing is above 20 MeV.
* γ from the target: ENDF/B-VIII.0 MT 5 photons (lines below ~7 MeV), isotropic, from G5.
* Sources: bepn_beam.SITES at several angles θ to the proton beam and distances, Ø8 cm collimator.

Not in the model (as for Birmingham): the 4π field reaching the arms around the collimator (the shield,
`bepn_beam.shield()`), the room, the target backing / cooling water (a moderated component), air in front
of the cell, ⁹Be(p,γ)¹⁰B (absent from the evaluation; ≲ 10⁻⁸ γ/p, estimate).
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
sys.path.insert(0, str(ROOT / 'survey' / 'soft_sim'))
sys.path.insert(0, str(HERE))
import soft_reach as SR                                       # noqa: E402
import bepn_beam as BB                                        # noqa: E402

OUT = HERE / 'out'
SR.E_GRID = np.unique(np.concatenate([np.geomspace(1e-3, 20.0, 3000), np.linspace(20.0, 30.0, 201)]))
SR.GEN['f'] = (20.0, 40.0)
SR.RUN['f'] = 'N4_beam_force'
SR.PART['f'] = 'n'
E_HI = 20.0
MU_PB_FAST = 0.18          # /cm, Pb for 1-20 MeV neutrons (σ_tot ≈ 5.5 b; uncollided, conservative)
MU_PB_G4 = 0.48            # /cm, Pb at ~4 MeV γ (NIST XCOM 0.042 cm²/g)

_fold = pd.read_csv(ROOT / 'ganil_nfs' / 'out' / 'fold_table.csv')
_F_NFS = (_fold.E_n.values, _fold.n_per_s_MeV.values / np.trapezoid(_fold.n_per_s_MeV.values, _fold.E_n.values))
_gen0 = SR.gen_density


def gen_density(p, e, runs=None):
    if p != 'f':
        return _gen0(p, e, runs)
    e = np.asarray(e, float)
    g = np.interp(e, *_F_NFS, left=0.0, right=0.0)
    return np.where(e > E_HI, g, 0.0)


SR.gen_density = gen_density


def load_runs(hw):
    runs = {}
    for p in ('n', 'g', 'h'):
        z = SR.R.load(SR.RUN[p] + SR.R.HW[hw], SR.SEL)
        if z is None:
            if p == 'h':
                continue
            sys.exit(f'missing {SR.SEL}/{SR.RUN[p] + SR.R.HW[hw]}_sel.npz (survey/soft_sim/fetch_sel.sh)')
        runs[p] = z
    z4 = SR.R.load('N4_beam_force' + SR.R.HW[hw], SR.R.SEL_BEAM)
    if z4 is None:
        sys.exit('missing ganil_nfs/sim/sel_beam/N4_beam_force*_sel.npz (ganil_nfs/sim/fetch_sel.sh)')
    z4 = {k: np.asarray(z4[k]) for k in z4}
    n5 = runs['n']
    m_ok = (np.asarray(n5['sg_En']) > 10) & (np.asarray(n5['sg_En']) <= 20)
    m_lg = (np.asarray(n5['lg_En']) > 10) & (np.asarray(n5['lg_En']) <= 20)
    k_leg = float(np.asarray(n5['lg_w'])[m_lg].sum() / max(np.asarray(n5['sg_w'])[m_ok].sum(), 1e-300))
    z4.update(lg_En=z4['sg_En'], lg_w=z4['sg_w'] * k_leg, lg_arm=z4['sg_arm'], tr_En=z4['En'], tr_w=z4['w'])
    runs['f'] = z4
    return runs, k_leg


def sources():
    S = []
    E = SR.E_GRID

    def add(key, ep, cur, th, d, pb=0.0):
        b = BB.beam(ep, cur, th, d)
        fn = BB.spectrum_on_grid(ep, th, E)
        fg = BB.gamma_on_grid(ep, E)
        lab = dict((k, l) for k, l, *_ in BB.SITES)[key.split('_')[0]]
        S.append(SR.Soft(f'{key}' + (f'_pb{pb:.0f}' if pb else ''),
                         f'{lab}, θ = {th:.0f}°, cell at {d:.0f} m' + (f', {pb:.0f} cm Pb' if pb else ''),
                         fn, b['n_cell'] * np.exp(-MU_PB_FAST * pb), fg, b['g_cell'] * np.exp(-MU_PB_G4 * pb),
                         site='bepn', note=f'mean E_n {b["mean_En"]:.2f} MeV; <2.75 MeV {b["f_below_2p75"]:.2f}; '
                                           f'>10 MeV {b["f_above_10"]:.3f}; >20 MeV {b["f_above_20"]:.3f}'))
    for key, lab, ep, cur in BB.SITES[:3]:
        for th in (0.0, 90.0, 130.0):
            add(f'{key}_{th:.0f}_2m', ep, cur, th, 2.0)
    for d in (1.0, 3.0):
        add(f'npi24_130_{d:.0f}m', 24.0, 0.3e-3, 130.0, d)
    add('npi24_130_2m', 24.0, 0.3e-3, 130.0, 2.0, pb=5.0)
    add('u120_0_3m', 18.0, 35e-6, 0.0, 3.0)
    return S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--days', type=float, nargs='+', default=[14.0, 50.0])
    ap.add_argument('--only', nargs='+')
    ap.add_argument('--hw', choices=list(SR.R.HW))
    ap.add_argument('--tau-scale', type=float, default=1.0, help='DREAM dead time × this (fewer samples)')
    ap.add_argument('--tag', default='', help='suffix for the output files')
    a = ap.parse_args()
    global OUT
    SR.R.TAU_DAQ *= a.tau_scale
    if a.tag:
        OUT = OUT.parent / f'out_{a.tag}'
    hws = [a.hw] if a.hw else list(SR.R.HW)
    OUT.mkdir(exist_ok=True)
    srcs = sources()
    if a.only:
        srcs = [s for s in srcs if s.key in a.only]
    rows, curves, comps = [], [], []
    grid = np.geomspace(1e-4, 1.0, 41)
    for hw in hws:
        M = SR.SF.nfs_model(hw)
        runs, k_leg = load_runs(hw)
        print(f'{hw}: N4 leg/ok ratio from N5 10-20 MeV = {k_leg:.3g}', flush=True)
        for src in srcs:
            C = SR.components(src, runs, hw, M)
            cap = SR.captures(src)
            ipc_day = cap * SR.Y.alpha(np.array(SR.R.NODES)) * SR.DAY
            comps.append(dict(key=src.key, hw=hw, n_cell=src.n_cell, g_cell=src.g_cell,
                              ok_singles_per_arm=C['ok_arm'].mean(), legs_per_arm=C['leg_arm'].mean(),
                              ok_singles_gamma_frac=C['ok_g_frac'], corr_trig_per_s=C['corr_trig'],
                              corr_sel_per_day=C['corr_sel'], corr_sel_mc=C['corr_n_mc'], corr_fact_per_day=C['corr_fact'],
                              corr_gamma_frac=C['corr_g_frac'], acc_raw_per_day=C['acc_raw'], acc_pass=C['acc_pass'],
                              acc_sel_mc=C['acc_n_mc'], ipc_per_day=float(ipc_day.sum()),
                              ipc_soft_per_day=float(ipc_day[SR.SOFT].sum()), note=src.note))
            for days in a.days:
                for soft in (True, False):
                    res = []
                    for s in grid:
                        st = SR.at_throttle(src, C, M, cap, s)
                        res.append((SR.rho3(M, st, days, soft), s, st))
                        if days == 50 and hw == 'big plastics':
                            curves.append(dict(key=src.key, signal='E* ≤ 22' if soft else 'all E*', throttle=s,
                                               n_cell=src.n_cell * s, rho3=res[-1][0]))
                    r, s, st = min(res, key=lambda x: x[0])
                    st0 = SR.at_throttle(src, dict(C, acc_th=C['acc_th'] * 0, corr_th=C['corr_th'] * 0,
                                                   ok_arm=C['ok_arm'] * 0, leg_arm=C['leg_arm'] * 0, corr_trig=0.0),
                                         M, cap, 1.0)
                    rows.append(dict(key=src.key, source=src.label, hw=hw, days=days,
                                     signal='E* ≤ 22 MeV' if soft else 'all E*', rho3=r, vs_ATOMKI=r / SR.R.RHO_REF,
                                     days_to_atomki=days * (r / 1.5e-3) ** 2,
                                     throttle=s, rho3_floor=SR.rho3(M, st0, days, soft), live=st['live'], occ=st['occ'],
                                     rand_trig_per_s=st['rand'], **SR.window_counts(st, M, soft)))
            print(f'{hw:13s} {src.key:22s} ok/arm {C["ok_arm"].mean():.3g}/s  legs/arm {C["leg_arm"].mean():.3g}/s  '
                  f'corr sel {C["corr_sel"]:.3g}/d ({C["corr_n_mc"]} MC)  acc pass {C["acc_pass"]:.2g} ({C["acc_n_mc"]} MC)  '
                  f'best soft {rows[-2]["rho3"]:.3g} @ s={rows[-2]["throttle"]:.2g} ({rows[-2]["days"]:.0f} d)', flush=True)
    t, cv, cp = pd.DataFrame(rows), pd.DataFrame(curves), pd.DataFrame(comps)
    if a.only and (OUT / 'bepn_reach.csv').exists():
        t = pd.concat([pd.read_csv(OUT / 'bepn_reach.csv').query('key not in @a.only'), t], ignore_index=True)
        cv = pd.concat([pd.read_csv(OUT / 'bepn_throttle.csv').query('key not in @a.only'), cv], ignore_index=True)
        cp = pd.concat([pd.read_csv(OUT / 'bepn_components.csv').query('key not in @a.only'), cp], ignore_index=True)
    t.to_csv(OUT / 'bepn_reach.csv', index=False, float_format='%.4g')
    cv.to_csv(OUT / 'bepn_throttle.csv', index=False, float_format='%.4g')
    cp.to_csv(OUT / 'bepn_components.csv', index=False, float_format='%.4g')
    pd.set_option('display.width', 250)
    print(cp.drop(columns='note').to_string(index=False))
    print(t[t.days == 50].pivot_table(index='key', columns=['hw', 'signal'], values='rho3', sort=False).to_string())
    print(t[t.days == 50].pivot_table(index='key', columns=['hw', 'signal'], values='throttle', sort=False).to_string())
    figure(cv)


def figure(cv):
    sys.path.insert(0, str(ROOT / 'ill'))
    import figstyle as fs
    fs.use()
    fig, ax = fs.figure()
    q = cv[cv.signal == 'E* ≤ 22']
    for key, col, lab in (('npi18_0_2m', fs.ACCENT, 'NPI TR-24 18 MeV, 0° (baseline)'), ('npi24_130_2m', fs.MUTED, 'NPI TR-24 24 MeV, 130°'),
                          ('npi24_0_2m', fs.COPPER, 'NPI TR-24 24 MeV, 0°'), ('kur30_130_2m', fs.TRACK, 'HM-30 30 MeV 1 mA, 130°')):
        r = q[q.key == key]
        if len(r):
            ax.plot(r.n_cell, r.rho3, color=col, lw=1.6, label=lab)
    ax.axhline(1.5e-3, color=fs.INK, lw=0.8, ls='--')
    ax.text(2e5, 1.6e-3, 'ATOMKI ⁴He', fontsize=8, color=fs.INK)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('neutrons / s through the Ø8 cm cell (beam throttled)')
    ax.set_ylabel('X17/IPC at 3σ in 50 d')
    ax.legend(frameon=False, fontsize=8)
    fs.title(ax, 'Reach vs beam on the cell (big plastics, E* ≤ 22 MeV signal)', 'cell 2 m from the Be target')
    fs.save(fig, OUT / 'bepn_reach_fig', data=cv)


if __name__ == '__main__':
    main()
