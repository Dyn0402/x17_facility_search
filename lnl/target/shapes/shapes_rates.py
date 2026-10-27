#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shapes_rates.py -- what the beam does to the scintillators, the Micromegas and DREAM for the two LNL target
designs, as built and with the big plastics, against the beam current.  SHAPES_GEANT.md §6-7 (2026-10-27).

    bash lnl/target/shapes/lxplus/fetch_l10.sh
    LNL_SEL=lnl/sim/sel_v3 ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/shapes/shapes_rates.py

Inputs
  * the L10 γ-line response libraries (gam_lib, 26 lines 0.2-17.64 MeV, and the K x-ray lines): per γ, the
    deposit in every channel (20 SiPM bars, the plastic(s), the LS, the drift gas) of every arm;
  * the line spectrum per µA (shapes_backgrounds.py): ⁸Be γ₀/γ₁, ⁷Li 478 keV, ⁶Li(p,γ), the contaminants at a
    stated level, PIXE;
  * cosmics: per-arm trigger legs and two-arm triggers from L4 (one live day, as built and big plastics);
  * the environment (room γ): an ANALYTIC stand-in, Φ = 2 γ/cm²/s omnidirectional (ask LNL for a survey).

Trigger (FEAS §14.1): an arm leg = a SiPM bar ≥ 0.5 MIP (0.238 MeV) AND a plastic ≥ 0.5 MIP (1.67 MeV, the 2 cm
bar MIP, as every LNL run; the 5 cm slab's own 0.5 MIP ≈ 4.2 MeV is shown as a variant); PAIR = ≥ 2 legs in
20 ns, never prescaled; SINGLE = ≥ 1 leg, prescale P; 1 Hz clock.  DREAM RAW 20 samples: τ = 298 µs,
non-paralysable, live = 1/(1 + f τ), max 3.35 kHz, 83 MB/s per FEU at 3.35 kHz.
Accidental legs: (any bar fired) × (plastic fired) × 2τ_leg in the same arm, 2τ_leg = 20 ns.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent / 'sim'))
import shapes_backgrounds as SB   # noqa: E402

OUT = HERE.parent.parent / 'out' / 'target' / 'shapes'
SEL = Path(os.environ.get('L10_SEL', HERE / 'sel'))
LSEL = Path(os.environ.get('LNL_SEL', HERE.parent.parent / 'sim' / 'sel_v3'))
TAU = 298e-6
FMAX = 3350.0
MB_EV = 83.0 / 3350.0
TWO_TAU = 20e-9
MM_WIN = 1.2e-6
T_INT = 100e-9                       # scintillator integration time (pile-up)
SIPM_T, PL_T = 0.2376, 1.675          # 0.5 MIP: 3 mm bar, 2 cm bar (MeV)
PL_T_5CM = 4.19                      # 0.5 MIP of the 5 cm slab
THR = (0.05, 0.1, 0.2376, 0.5, 1.0, 1.675, 3.0, 4.19, 6.0, 10.0)
CURRENTS = (0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0)
PRESCALES = (1, 2, 5, 10, 20, 50, 100, 200)
ROOM_PHI = 2.0                       # γ/cm²/s, omnidirectional, > 50 keV (ESTIMATE; ask LNL)
MU_FLUX = 1.0 / 60                   # /cm²/s, horizontal detector
LIBS = {'dome': 'dome200', 'window': 'win45d200', 'ogive_cu': 'ogCu200', 'ogive_be': 'ogBe200mo8', 'window_be': 'win45be'}
XLIBS = {'dome': 'xray_dome200', 'window': 'xray_win45d200', 'window0': 'xray_win0d200', 'ogive_cu': 'xray_ogCu200',
         'ogive_be': 'xray_ogBe200mo8', 'window_be': 'xray_win45be', 'window_wide': 'xray_win45wide'}


def design_of(config):
    """the rates design (LIBS key) that stands for a reach configuration (geant_reach.csv)"""
    if config.startswith('ogCu'):
        return 'ogive_cu'
    if config.startswith('og'):
        return 'ogive_be'
    if config.startswith('win45be') or config.startswith('win45wide'):
        return 'window_be'
    return 'dome' if config.startswith('dome') else 'window'
CHAN = {**{c: f'SiPM bar {c}' for c in range(20)}, 20: 'plastic L / big slab', 21: 'plastic R', 22: 'LS',
        23: 'MM drift gas'}
# per-channel geometry for the analytic cosmic / room rates: (area for μ, cm²; total surface / 4, cm²; P(int))
GEO = {'bigP': {'bar': (125.0, 70.0, 0.15), 'plastic': (5625.0, 3190.0, 0.35)},
       'asb': {'bar': (125.0, 70.0, 0.15), 'plastic': (600.0, 425.0, 0.2), 'ls': (1500.0, 1500.0, 0.4)}}


# --------------------------------------------------------------------------- #
def lib_table(name, det):
    """per library line: per-γ probabilities and mean deposits."""
    f = next((SEL / f'{run}_gam_lib_{name}_{det}_sng.npz' for run in ('L10', 'L11')
              if (SEL / f'{run}_gam_lib_{name}_{det}_sng.npz').exists()), None)
    if f is None:
        return None
    z = np.load(f)
    ev, arm, ch, e, line = z['ev'], z['arm'].astype(int), z['ch'].astype(int), z['e'], z['line']
    out = {}
    for L, n in zip(z['lines'], z['n_line']):
        m = np.isclose(line, L, rtol=1e-4)
        E, A, C, V = e[m], arm[m], ch[m], ev[m]
        r = dict(n=int(n))
        r['p_thr'] = np.array([[[np.sum((A == a) & (C == c) & (E > t)) / n for t in THR] for c in range(24)]
                               for a in range(4)])                  # [arm, ch, thr]
        r['mean_e'] = np.array([[E[(A == a) & (C == c)].sum() / n for c in range(24)] for a in range(4)])
        bar = (C < 20) & (E >= SIPM_T)
        pl = ((C == 20) | (C == 21)) & (E >= PL_T)
        pl5 = (C == 20) & (E >= PL_T_5CM)
        mm = (C == 23) & (E > 0)
        for key, sel in (('bar', bar), ('pl', pl), ('pl5', pl5), ('mm', mm)):
            r[f'p_{key}'] = np.array([len(np.unique(V[sel & (A == a)])) / n for a in range(4)])
        legs, legs5 = [], []
        for a in range(4):
            vb, vp, vp5 = set(V[bar & (A == a)]), set(V[pl & (A == a)]), set(V[pl5 & (A == a)])
            legs.append(vb & vp)
            legs5.append(vb & vp5)
        r['p_leg'] = np.array([len(s) / n for s in legs])
        r['p_leg5'] = np.array([len(s) / n for s in legs5])
        allv = np.concatenate([np.fromiter(s, np.int64, len(s)) for s in legs]) if any(legs) else np.zeros(0, int)
        u, k = np.unique(allv, return_counts=True)
        r['p_pair'] = np.sum(k >= 2) / n
        out[round(float(L), 5)] = r
    return out


def nearest(lib, E):
    Ls = np.array(sorted(lib))
    return float(Ls[np.argmin(np.abs(np.log(Ls) - np.log(E)))])


def spectrum(design, ep, contam=True):
    """γ/s per µA by physical line (E MeV -> rate), from shapes_backgrounds."""
    if SB.DESIGNS[design].get('ogive'):
        import opt_sketch as OS
        b = OS.ogive_yield_mix(ep, lambda t: SB.TM.layered_yield(ep, [SB.TM.film('Li', t)]), SB.DESIGNS[design]['li_ug'], name='tm')
        f = OS.ogive_yield_mix(ep, lambda t: SB.film_yields(ep, t), SB.DESIGNS[design]['li_ug'], name='sb')
    else:
        b = SB.TM.layered_yield(ep, [SB.TM.film('Li', SB.DESIGNS[design]['li_ug'])])
        f = SB.film_yields(ep, SB.DESIGNS[design]['li_ug'])
    p = SB.P_PER_UA
    g0, g1, f17 = b['Y_g0'] * p, b['Y_g1'] * p, b['f17']
    s = {18.15: g0 * (1 - f17), 17.64: g0 * f17, 15.1: g1 * (1 - f17), 14.6: g1 * f17,
         0.478: f['L478'] * p, 5.6: f['Li6_pg'] * p}
    if contam:
        x = dict(F=1e-4, N=1e-2, Na=1e-4, B=1e-5)
        s[6.13] = f['F_gam_per_x'] * x['F'] * p / 1.6
        s[7.0] = f['F_gam_per_x'] * x['F'] * p * 0.6 / 1.6
        s[4.44] = f['N15_pag_897_per_x'] * x['N'] * p
        s[7.3] = f['N14_pg_1058_per_x'] * x['N'] * p
        s[0.44] = f['Na_pp_440_per_x'] * x['Na'] * p
        s[1.634] = f['Na_pag_1634_per_x'] * x['Na'] * p
        s[12.7] = f['Na_pg_12.7_per_x'] * x['Na'] * p
        s[16.9] = f['B_g0_per_x'] * x['B'] * p
    return s


def cosmic(det):
    z = np.load(LSEL / f"L4_cosmic{'_bigP' if det == 'bigP' else ''}_sel.npz", allow_pickle=True)
    live = int(z['cnt_n_generated']) * 60.0 / (300.0 * 300.0)
    return np.array(z['cnt_leg_arm']) / live, int(z['cnt_trig2']) / live


def analytic_singles(det):
    """cosmic μ and room γ per channel (Hz): μ through the area (×0.5 for vertical arms), room γ ROOM_PHI × S/4 ×
    P(interaction)."""
    out = {}
    for k, (a_mu, s4, p) in GEO[det].items():
        out[k] = dict(mu=MU_FLUX * a_mu * 0.75, room=ROOM_PHI * s4 * p)
    return out


# --------------------------------------------------------------------------- #
def rates(design, det, ep, contam=True):
    lib = lib_table(LIBS[design], det)
    if lib is None:
        return None
    spec = spectrum(design, ep, contam)
    tot = {k: 0.0 for k in ('p_thr', 'mean_e', 'p_bar', 'p_pl', 'p_pl5', 'p_mm', 'p_leg', 'p_leg5', 'p_pair')}
    by_line = []
    for E, R in spec.items():
        L = nearest(lib, E)
        r = lib[L]
        for k in tot:
            tot[k] = tot[k] + R * r[k]
        by_line.append(dict(design=design, det=det, Ep_keV=ep, contam=contam, line_MeV=E, lib_line=L,
                            gamma_per_s_uA=R, legs_per_s_uA=float(np.sum(R * r['p_leg'])),
                            bar_per_s_uA=float(np.sum(R * r['p_bar'])), pl_per_s_uA=float(np.sum(R * r['p_pl'])),
                            mm_per_s_uA=float(np.sum(R * r['p_mm'])),
                            sipm_MeV_per_s_uA=float(np.sum(R * r['mean_e'][:, :20])),
                            plastic_MeV_per_s_uA=float(np.sum(R * r['mean_e'][:, 20:22]))))
    return tot, by_line


def xray_mm(design, det='bigP'):
    """MM hits per arm per µA from the PIXE line of the beam stop (Geant4 x-ray library)."""
    lib = lib_table(XLIBS[design], det)
    if lib is None:
        return None
    el = SB.DESIGNS[design]['stop']
    return lib, el


def current_scan():
    """days to 3σ at R(ATOMKI) against current: the Geant4 fit at 1 µA (geant_reach.csv, beam terms ∝ I, cosmics
    ~1 % of B neglected) divided by I × live(I, P), P the smallest prescale keeping 95 % live; with the dome's / window's trigger rates."""
    gr, dq = OUT / 'geant_reach.csv', OUT / 'daq_live.csv'
    if not (gr.exists() and dq.exists()):
        return None
    g, d = pd.read_csv(gr), pd.read_csv(dq)
    d = d[d.contam]
    rows = []
    for _, r in g.iterrows():
        des = design_of(r.config)
        q = d[(d.det == r.det) & (d.design == des) & (d.Ep_keV == r.Ep_keV)]
        for I, qi in q.groupby('I_uA'):
            ok = qi[qi.live >= 0.95].sort_values('prescale')   # the smallest prescale that keeps 95 % live
            best = ok.iloc[0] if len(ok) else qi.sort_values('prescale').iloc[-1]
            p1 = qi[qi.prescale == 1].iloc[0]
            rows.append(dict(det=r.det, config=r.config, Ep_keV=r.Ep_keV, I_uA=I, days_1uA=r.days_fit,
                             days_P1=r.days_fit / (I * p1.live), live_P1=p1.live,
                             days_bestP=r.days_fit / (I * best.live), bestP=int(best.prescale), live_bestP=best.live,
                             trig_P1=p1.trig_per_s, trig_bestP=best.trig_per_s))
    t = pd.DataFrame(rows)
    t.to_csv(OUT / 'days_vs_current.csv', index=False)
    return t


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows, lines, chans, daq = [], [], [], []
    for det in ('bigP', 'asb'):
        leg_mu, pair_mu = cosmic(det)
        an = analytic_singles(det)
        for design in LIBS:
            for ep in SB.EPS:
                for contam in (False, True):
                    res = rates(design, det, ep, contam)
                    if res is None:
                        print(f'{design} {det}: library missing')
                        continue
                    tot, bl = res
                    lines += bl
                    # x-rays into the MM (per µA, per arm)
                    xr = xray_mm(design)
                    mm_x = np.zeros(4)
                    if xr is not None:
                        lib, el = xr
                        f = SB.film_yields(ep, SB.DESIGNS[design]['li_ug'])
                        yk = SB.pixe_yield(el, f['E_out']) * SB.P_PER_UA
                        L = nearest(lib, SB.E_KA[el] / 1e3)
                        mm_x = yk * lib[L]['p_mm']
                    for I in CURRENTS:
                        bar = tot['p_bar'] * I + 20 * (an['bar']['mu'] + an['bar']['room'] * 0.5)
                        pl = tot['p_pl'] * I + an['plastic']['mu'] + an['plastic']['room'] * 0.02
                        leg_true = tot['p_leg'] * I + leg_mu
                        leg_acc = bar * pl * TWO_TAU
                        leg = leg_true + leg_acc
                        pair_true = tot['p_pair'] * I + pair_mu
                        pair_acc = TWO_TAU * sum(leg[i] * leg[j] for i in range(4) for j in range(i + 1, 4))
                        pair = pair_true + pair_acc
                        single = max(leg.sum() - 2 * pair, 0.0)
                        mm = tot['p_mm'] * I + mm_x * I
                        base = dict(det=det, design=design, Ep_keV=ep, contam=contam, I_uA=I)
                        for P in PRESCALES:
                            ftr = pair + single / P + 1.0
                            live = 1 / (1 + ftr * TAU)
                            daq.append(dict(**base, prescale=P, leg_per_s=leg.sum(), leg_true_per_s=leg_true.sum(),
                                            leg_acc_per_s=leg_acc.sum(), leg_cosmic_per_s=leg_mu.sum(),
                                            pair_per_s=pair, pair_acc_per_s=pair_acc, single_per_s=single,
                                            trig_per_s=ftr, live=live, over_fmax=ftr > FMAX,
                                            MB_per_s_FEU=ftr * MB_EV))
                        rows.append(dict(**base, bar_fired_per_s_arm=float(bar.max()), plastic_fired_per_s_arm=float(pl.max()),
                                         mm_hits_per_s_arm=float(mm.max()), mm_xray_per_s_arm=float((mm_x * I).max()),
                                         mm_occupancy=float(mm.max() * MM_WIN),
                                         legs_per_s=float(leg.sum()), pair_per_s=float(pair)))
                    if contam is False:
                        continue
                    for a in range(1):
                        for c in list(range(20)) + [20, 21, 22, 23]:
                            for it, t in enumerate(THR):
                                chans.append(dict(det=det, design=design, Ep_keV=ep, arm=a, ch=c, chan=CHAN[c],
                                                  thr_MeV=t, rate_per_uA=tot['p_thr'][a, c, it],
                                                  MeV_per_s_uA=tot['mean_e'][a, c]))
    pd.DataFrame(rows).to_csv(OUT / 'rates_summary.csv', index=False)
    pd.DataFrame(lines).to_csv(OUT / 'rates_by_line.csv', index=False)
    pd.DataFrame(chans).to_csv(OUT / 'rates_channels.csv', index=False)
    pd.DataFrame(daq).to_csv(OUT / 'daq_live.csv', index=False)
    pd.set_option('display.width', 250)
    d = pd.DataFrame(daq)
    if len(d):
        print(d[(d.prescale == 1) & d.contam].to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    print(pd.DataFrame(rows).to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    current_scan()
    return 0


if __name__ == '__main__':
    sys.exit(current_scan() is None if '--scan' in sys.argv else main())
