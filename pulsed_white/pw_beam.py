#!/usr/bin/env python3
"""
pw_beam.py -- pulsed white neutron sources re-examined with time of flight: JRC GELINA, CSNS Back-n
(ES#1/ES#2, CSNS-II), plus nELBE and RPI for completeness, on the LANSCE WNR engine.

    python pulsed_white/pw_beam.py --check       # reproduce WNR 90L 10 m (8.4e-4) and a Birmingham soft_reach row
    python pulsed_white/pw_beam.py               # -> pulsed_white/out/pw_*.csv/png

Engine: lansce_wnr/wnr_beam.py (imported, not copied).  It folds the source into one period, turns the
NFS E_n bins into time windows, and re-weights N5 (< 8.5 MeV), N4 (8.5-45 MeV) and the 25-45 MeV value above
45 MeV (K_HI); correlated events and triggers keep their Geant4 delay.  Three things are changed here, per source:

  1. the beam: `spec` [n/s/MeV through the spot] and the true period (GELINA 1.25 ms, Back-n 40 ms);
  2. DREAM: a single-pulse source gives at most one readout per pulse (298 µs dead time << period), so
     live = (1 - exp(-mu)) / mu with mu = gated triggers per pulse (the engine's non-paralysable formula
     assumes randomly spread triggers, which does not apply);
  3. the flash: the WNR note ignored it.  Here every bin's exposure is multiplied by the fraction of its
     time window after t_dead (after L/c).  t_dead = 0: the WNR convention.  0.87 µs: the measured Micromegas
     chamber recovery after the n_TOF γ flash (nTof_x17 ntof_processing/mm_flash).  The DREAM chain's own
     recovery was 0.5-25 ms at n_TOF and scales as Q^1.2; it is scanned (`pw_flash_scan.csv`) because the
     flash size at these machines is not known.  MODELLED AS A WINDOW CUT ONLY.

Normalisations (FACILITY.md gives the source of each):
  GELINA    3.4e13 n/s into 4π at the published 100 MeV, 100 µA, 800 Hz (JRC); spectrum "peak at 1-2 MeV"
            modelled as a Watt spectrum (ESTIMATE, Maxwellian T = 0.8-1.5 as a variation).  f_dir = 1 is the
            isotropic upper bound with no moderator shadowing; 0.5 is an ESTIMATE of a real direct path.
            No measured MeV flux at a named station could be retrieved (Ene et al. 2010 is paywalled): **(ask)**.
  Back-n    Table 1 of arXiv:2101.06567 (measured): 1.8e7 n/cm²/s at ES#1 Φ50, 6.9e6 at ES#2 Φ60, per 100 kW;
            the survey's measured per-decade spectrum (Y.BACKN).
"""
from __future__ import annotations

import argparse
import multiprocessing as mp
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'out'
sys.path.insert(0, str(ROOT / 'lansce_wnr'))
sys.path.insert(0, str(ROOT / 'survey' / 'soft_sim'))
sys.path.insert(0, str(ROOT / 'ill'))
import wnr_beam as W                                           # noqa: E402

SF, R, Y = W.SF, W.R, W.Y
SOFT = W.SOFT
NB = W.NB
C_M_NS = W.C_M_NS
RHO = R.RHO_REF
A50 = 50.0                     # cm², the Ø8 cm spot
T_RECOVER = 0.87e3             # ns, measured MM chamber recovery after the n_TOF flash
GRID = np.geomspace(1e-3, 1.0, 19)
FLASH_SCAN_US = (0.0, 0.3, 0.87, 2.0, 5.0, 10.0, 30.0)
GATES = {'0.2-2.75': SOFT, '0.2-25': list(range(NB))}
SIGNALS = {True: 'E* ≤ 22 MeV', False: 'all E*'}
E_GRID_BN = Y.E_GRID
BN_F = Y.per_decade(fr=Y.BACKN)                 # normalised dN/dE on Y.E_GRID
BN_NORM = float(np.trapezoid(BN_F, E_GRID_BN))


def watt(e):
    a, b = 0.988, 2.249
    f = np.exp(-np.asarray(e, float) / a) * np.sinh(np.sqrt(b * np.asarray(e, float)))
    return f / np.trapezoid(f, e)


def maxw(e, t):
    x = np.asarray(e, float)
    f = np.sqrt(x) * np.exp(-x / t)
    return f / np.trapezoid(f, x)


def maxw08(e):
    return maxw(e, 0.8)


def maxw15(e):
    return maxw(e, 1.5)


class Src:
    """duck-typed for wnr_beam.beam_of."""
    def __init__(self, key, label, L, rep_hz, f_e, n_total, du_ns, area=A50, double_ns=0.0, n_macro=None, full_window=False):
        self.key, self.label, self.L, self.rep_hz = key, label, L, rep_hz
        self.f_e, self.n_total, self.du_ns, self.area = f_e, n_total, du_ns, area
        self.double_ns = double_ns
        self.full_window = full_window  # the whole ToF window read as one long DREAM event: no per-pulse loss
        self.T_us = 1e6 / rep_hz
        self.up_per_s = rep_hz
        self.duty = 1.0
        self.macro = n_macro

    def n_spec(self, e=W.E_FINE):
        return self.f_e(np.asarray(e, float)) * self.n_total

    @property
    def per_pulse(self):
        return self.n_total / self.rep_hz


class MacroSrc:
    """WNR's own Config, with its macropulse DAQ; used for the reference row only."""
    def __init__(self, cfg, du_ns=2.0):
        self.cfg, self.key, self.label, self.L, self.du_ns, self.double_ns = cfg, cfg.key, cfg.label, cfg.L, du_ns, 0.0
        self.T_us, self.up_per_s, self.duty = cfg.T_us, cfg.up_per_s, cfg.duty
        self.rep_hz = cfg.up_per_s

    def n_spec(self, e=W.E_FINE):
        return self.cfg.n_spec(e)

    @property
    def per_pulse(self):
        return float(np.trapezoid(self.cfg.n_spec(W.E_FINE), W.E_FINE)) / self.cfg.up_per_s


def gelina(L, f_dir=1.0, current=100.0, f_e=watt, tag=''):
    """the isotropic 3.4e13 n/s at 100 µA (JRC) on a Ø8 cm spot at L metres."""
    n = 3.4e13 * (current / 100.0) * f_dir * A50 / (4 * np.pi * (L * 100.0) ** 2)
    lab = f'GELINA {L:g} m, {current:g} µA, f_dir {f_dir:g}{tag}'
    key = f'gelina_{L:g}m' + ('' if f_dir == 1.0 else f'_fd{f_dir:g}') + ('' if current == 100 else f'_{current:g}uA') + tag.replace(' ', '_')
    return Src(key, lab, L, 800.0, f_e, n, 5.0)


def _bn_f(e):
    # the survey's measured per-decade Back-n spectrum, normalised on its own grid, extended to E_FINE
    return np.interp(e, E_GRID_BN, BN_F, left=0.0, right=0.0) / BN_NORM


def backn(key, label, L, flux_100, power_kw, dia_mm, double=True, single_bunch=False):
    area = np.pi * (dia_mm / 20.0) ** 2
    n = flux_100 * power_kw / 100.0 * area
    if single_bunch:
        n *= 0.5     # single-bunch mode: half the protons per pulse (Back-n papers); bunch-merging would keep them
    return Src(key, label, L, 25.0, _bn_f, n, 20.0, area=area, double_ns=0.0 if (single_bunch or not double) else 410.0)


def configs():
    C = [gelina(L) for L in (10.0, 15.0, 30.0, 50.0, 60.0)]
    C += [gelina(10.0, 0.5), gelina(30.0, 0.5), gelina(10.0, 1.0, 40.0)]
    C += [backn('backn_es1_185', 'Back-n ES#1, 185 kW, Φ50, double bunch', 55.0, 1.8e7, 185.0, 50.0),
          backn('backn_es1_185_sb', 'Back-n ES#1, 185 kW, Φ50, single bunch', 55.0, 1.8e7, 185.0, 50.0, single_bunch=True),
          backn('backn_es2_185', 'Back-n ES#2, 185 kW, Φ60', 76.0, 6.9e6, 185.0, 60.0),
          backn('backn_es1_500', 'CSNS-II Back-n ES#1, 500 kW, Φ50', 55.0, 1.8e7, 500.0, 50.0),
          backn('backn_es2_500', 'CSNS-II Back-n ES#2, 500 kW, Φ60', 76.0, 6.9e6, 500.0, 60.0),
          backn('backn_es1_185_d20', 'Back-n ES#1, 185 kW, Φ20 small spot', 55.0, 1.6e6, 185.0, 20.0),
          backn('backn_es2_185_d30', 'Back-n ES#2, 185 kW, Φ30 small spot', 76.0, 6.1e5, 185.0, 30.0)]
    # the upstream irradiation platform (8e7 n/cm²/s per 100 kW, arXiv:2101.06567) as an MX17 host: a hypothetical
    # (the platform is outside the shutter aperture, in the tunnel; L ~ 30 m is an ESTIMATE, the area is Φ50 equivalent)
    C.append(backn('backn_platform_185', 'Back-n upstream platform, 185 kW, ~30 m (hypothetical)', 30.0, 8e7, 185.0, 50.0))
    # full-window readout: every trigger in a pulse kept (one long DREAM event, see FEASIBILITY §4)
    for c in list(C):
        if c.key in ('gelina_10m', 'gelina_15m', 'backn_es1_185', 'backn_es2_185', 'backn_es1_500', 'backn_es2_500'):
            f = Src(c.key + '_fw', c.label + ', full-window readout', c.L, c.rep_hz, c.f_e, c.n_total, c.du_ns,
                    area=c.area, double_ns=c.double_ns, full_window=True)
            C.append(f)
    # GELINA spectrum shape (ESTIMATE): Maxwellians instead of Watt
    C.append(gelina(10.0, f_e=maxw08, tag='_T0.8'))
    C.append(gelina(10.0, f_e=maxw15, tag='_T1.5'))
    # completeness: nELBE (2.5e4 n/cm²/s, 7 cm², 102 kHz) and RPI (≤ 1e13 n/s bound, 10 m, 400 Hz ESTIMATE)
    C.append(Src('nelbe', 'nELBE, 2.5e4 n/cm²/s, 7 cm²', 6.0, 102e3, watt, 2.5e4 * 7.0, 2.0, area=7.0))
    C.append(Src('rpi_10m', 'RPI, 1e13 n/s bound, 10 m', 10.0, 400.0, watt, 1e13 * A50 / (4 * np.pi * 1e6), 5.0))
    return C


def run_analyse(src, tab, M, hw, s, gate):
    """W.analyse with this source's period, then the single-pulse DREAM model."""
    W.DU_NS = src.du_ns
    b = W.beam_of(src)
    a = W.analyse(b, tab, M, hw, s, gate)
    if isinstance(src, Src):
        mu = (a['trig_corr'] + a['trig_rand']) / src.rep_hz
        a['live'] = 1.0 if src.full_window else (float(-np.expm1(-mu) / mu) if mu > 1e-12 else 1.0)
        a['mu'] = mu
        a['expo'] = a['live'] * np.exp(-2 * a['occ'])
    return a


def with_flash(a, src, t_dead_ns):
    """multiply exposure per bin by the part of its window after the flash (and its double-bunch twin)."""
    a = dict(a)
    tf = src.L / C_M_NS + src.double_ns + t_dead_ns
    frac = np.ones(NB)
    for k, (w0, w1) in enumerate(a['W']):
        frac[k] = float(np.clip((w1 - max(w0, tf)) / (w1 - w0), 0.0, 1.0)) if np.isfinite(w0) else 0.0
    a['expo'] = a['expo'] * frac
    a['frac'] = frac
    return a


# ------------------------------------------------------------------------- #
_G = {}


def _init(hw):
    if hw not in _G:
        M = W.calib(SF.nfs_model(hw))
        _G[hw] = (M, W.response(hw, M))


def scan(args):
    src, hw = args
    M, tab = _G[hw]
    out = []
    for soft in (True, False):
        gates = {'0.2-2.75': SOFT} if soft else GATES
        for gname, gate in gates.items():
            for s in GRID:
                a = run_analyse(src, tab, M, hw, s, gate)
                for k in ('rho', 'uc', 'gate'):
                    a.pop(k, None)
                out.append((soft, gname, s, a))
    return src, hw, out


def results(src, hw, out, t_dead, days=(50.0, 14.0), flash_label=''):
    """best (throttle, gate) rows at this flash dead time."""
    M, tab = _G[hw]
    rows = []
    for soft in (True, False):
        cands = []
        for sf, gname, s, a in out:
            if sf != soft:
                continue
            x = with_flash(a, src, t_dead)
            x['gate_name'] = gname
            S, B = W.components(x, M, soft)
            cands.append((gname, s, x, S, B))
        for dd in days:
            best = min(((W.rho3(S, B, dd, GATES[g]), g, s, x, S, B) for g, s, x, S, B in cands), key=lambda z: z[0])
            r, g, s, x, S, B = best
            gate = GATES[g]
            rows.append(dict(key=src.key + flash_label, label=src.label, hw=hw, days=dd, signal=SIGNALS[soft], gate=g,
                             rho3=r, vs_ATOMKI=r / RHO, days_to_atomki=dd * (r / RHO) ** 2 if np.isfinite(r) else np.inf,
                             throttle=s, live=float(x['live']), occ_max=float(x['occ'][gate].max()), mu=float(x.get('mu', np.nan)),
                             t_dead_us=t_dead / 1e3, n_cell_full=float(np.trapezoid(src.n_spec(W.E_FINE), W.E_FINE)),
                             n_pulse=src.per_pulse, X17_per_day=float(S[gate].sum()),
                             **{f'{k}_per_day': float(v[gate].sum()) for k, v in B.items()}))
    # the floor: full beam, no DAQ or occupancy loss, the flash cut kept, IPC + cosmics only
    for soft in (True, False):
        a = next(a for sf, gname, s, a in out if sf == soft and s == 1.0 and gname == ('0.2-2.75' if soft else '0.2-25'))
        x = with_flash(dict(a, expo=np.ones(NB)), src, t_dead)
        S, B = W.components(x, M, soft)
        B = dict(IPC=B['IPC'], cosmic=B['cosmic'])
        for r in rows:
            if r['signal'] == SIGNALS[soft]:
                r['rho3_floor'] = W.rho3(S, B, r['days'], SOFT if soft else GATES['0.2-25'])
    return rows


def check():
    import soft_reach as SR
    # 1. WNR 90L 10 m through this wrapper: must give the published 8.4e-4
    pub = pd.read_csv(ROOT / 'lansce_wnr' / 'out' / 'wnr_reach.csv')
    q = pub[(pub.key == '90L_10m') & (pub.days == 50)]
    cfg = [c for c in W.configs() if c.key == '90L_10m'][0]
    for hw in R.HW:
        _init(hw)
        src = MacroSrc(cfg)
        _, _, out = scan((src, hw))
        rows = results(src, hw, out, 0.0, days=(50.0,))
        for r in rows:
            p = q[(q.hw == hw) & (q.signal == r['signal'])].rho3.iloc[0]
            print(f'WNR 90L 10 m  {hw:13s} {r["signal"]:12s}  here {r["rho3"]:.4g}  published {p:.4g}')
        # and with the flash dead time, the fair comparison:
        for t in (0.0, T_RECOVER):
            rr = results(src, hw, out, t, days=(50.0,))
            print(f'   t_dead {t / 1e3:.2f} µs: E* ≤ 22 {rr[0]["rho3"]:.4g}')
    # 2. the shared soft-beam engine on a Birmingham row of soft_reach.csv
    pubs = pd.read_csv(ROOT / 'survey' / 'soft_sim' / 'out' / 'soft_reach.csv')
    key = 'bham_28_2m_pb5'
    for hw in R.HW:
        src = [s for s in SR.sources() if s.key == key][0]
        M = SF.nfs_model(hw)
        C = SR.components(src, SR.load_runs(hw), hw, M)
        cap = SR.captures(src)
        res = []
        for s in np.geomspace(1e-4, 1.0, 41):
            st = SR.at_throttle(src, C, M, cap, s)
            res.append(SR.rho3(M, st, 50.0, True))
        p = pubs[(pubs.key == key) & (pubs.hw == hw) & (pubs.days == 50) & (pubs.signal == 'E* ≤ 22 MeV')].rho3.iloc[0]
        print(f'{key} {hw:13s} soft_reach here {min(res):.4g}  published {p:.4g}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--procs', type=int, default=8)
    ap.add_argument('--figs', action='store_true', help='redraw the figures from the CSVs')
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    if a.check:
        return check()
    if a.figs:
        return figures()
    for hw in R.HW:
        _init(hw)
    cfgs = configs()
    wnr = [MacroSrc(c) for c in W.configs() if c.key in ('90L_10m', '30L_20m')]
    tasks = [(c, hw) for c in cfgs + wnr for hw in R.HW]
    print(f'{len(tasks)} tasks', flush=True)
    with mp.get_context('fork').Pool(a.procs) as pool:
        done = pool.map(scan, tasks, chunksize=1)
    rows, flash = [], []
    pulses = []
    for src, hw, out in done:
        # headline: flash dead time 0 (the WNR convention, key suffix _nf) and 0.87 µs (key = headline)
        rows += results(src, hw, out, 0.0, flash_label='_nf')
        rows += results(src, hw, out, T_RECOVER)
        for t in FLASH_SCAN_US:
            for r in results(src, hw, out, t * 1e3, days=(50.0,), flash_label=''):
                if r['signal'].startswith('E*'):
                    flash.append(dict(key=src.key, hw=hw, t_dead_us=t, rho3=r['rho3'], days_to_atomki=r['days_to_atomki'],
                                      throttle=r['throttle'], live=r['live'], occ_max=r['occ_max']))
        if hw == 'big plastics':
            a0 = next(aa for sf, gn, s, aa in out if sf and s == 1.0)
            pulses.append(dict(key=src.key, n_per_pulse_full=src.per_pulse, n_cell_full=rows[-1]['n_cell_full'],
                               occ_full=float(a0['occ'][SOFT].max()), trig_per_s_full=float(a0['trig_corr'] + a0['trig_rand']),
                               mu_full=float(a0.get('mu', np.nan)), live_full=float(a0['live'])))
        print('done', src.key, hw, flush=True)
    t = pd.DataFrame(rows)
    t.to_csv(OUT / 'pw_reach.csv', index=False, float_format='%.4g')
    pd.DataFrame(flash).to_csv(OUT / 'pw_flash_scan.csv', index=False, float_format='%.4g')
    pd.DataFrame(pulses).to_csv(OUT / 'pw_pulse_table.csv', index=False, float_format='%.4g')
    pd.set_option('display.width', 250)
    print(t[(t.days == 50) & (t.hw == 'big plastics') & (t.signal == 'E* ≤ 22 MeV')][['key', 'rho3', 'days_to_atomki', 'throttle', 'live', 'occ_max', 'mu', 'rho3_floor']].to_string(index=False))
    figures()


def figures():
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use()
    # 1. the beams through the spot
    e = np.geomspace(0.01, 200, 400)
    cfg = [c for c in W.configs() if c.key == '90L_10m'][0]
    C = {c.key: c for c in configs()}
    lines = [('GELINA 10 m (isotropic bound)', C['gelina_10m'].n_spec(e), fs.ACCENT), ('Back-n ES#1, 185 kW, Φ50', C['backn_es1_185'].n_spec(e), fs.COPPER),
             ('Back-n ES#2, 185 kW, Φ60', C['backn_es2_185'].n_spec(e), fs.TRACK), ('WNR 90L, 10 m', cfg.n_spec(e), fs.MUTED)]
    fig, ax = plt.subplots(figsize=fs.FIG)
    d = dict(E=e)
    for n, y, c in lines:
        ax.plot(e, np.where(y > 0, y * e, np.nan), color=c, lw=1.5, label=n)
        d[n] = y * e
    ax.axvspan(0.2, 2.75, color=fs.BAND_SIGNAL, alpha=0.07, lw=0)
    ax.set_xscale('log'); ax.set_yscale('log'); ax.set_ylim(1e5, 3e9)
    ax.set_xlabel('E_n [MeV]'); ax.set_ylabel('E·dN/dE through the spot [n/s]')
    ax.legend(frameon=False, fontsize=8)
    fs.title(ax, 'The beams at the cell', 'GELINA is an upper bound; the 0.2-2.75 MeV window is shaded')
    fig.tight_layout()
    fs.save(fig, OUT / 'pw_spectra', data=pd.DataFrame(d))
    # 2. reach vs flash dead time
    f = pd.read_csv(OUT / 'pw_flash_scan.csv')
    f = f[f.hw == 'big plastics']
    fig, ax = plt.subplots(figsize=fs.FIG)
    keep = [('gelina_10m', fs.ACCENT), ('gelina_15m', '#0072B2'), ('gelina_30m', fs.TRACK), ('backn_es1_185', fs.COPPER), ('backn_es2_185', fs.MUTED), ('90L_10m', 'black')]
    for k, c in keep:
        q = f[f.key == k].sort_values('t_dead_us')
        ax.plot(q.t_dead_us + 0.1, np.clip(q.rho3.replace(np.inf, 1.0), 1e-4, 1.0), '-o', ms=3, color=c, lw=1.4, label=k)
    ax.axhline(RHO, color=fs.MUTED, lw=0.8)
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel('dead time after the flash + 0.1 [µs]'); ax.set_ylabel('X17/IPC at 3σ, 50 d, E* ≤ 22')
    ax.legend(frameon=False, fontsize=8)
    fs.title(ax, 'The flash decides the short paths', 'big plastics, best throttle; ATOMKI 1.5e-3 marked')
    fig.tight_layout()
    fs.save(fig, OUT / 'pw_flash_fig', data=f)
    # 3. headline bars
    t = pd.read_csv(OUT / 'pw_reach.csv')
    q = t[(t.hw == 'big plastics') & (t.days == 50) & (t.signal == SIGNALS[True])].sort_values('rho3', ascending=False)
    q = q[np.isfinite(q.rho3) & (q.rho3 < 0.1)]
    fig, ax = plt.subplots(figsize=(fs.FIG[0], 0.2 * len(q) + 1))
    ax.barh(q.key, q.rho3, color=fs.ACCENT)
    ax.axvline(RHO, color=fs.MUTED, lw=0.8)
    ax.set_xscale('log'); ax.set_xlabel('X17/IPC at 3σ, 50 d, E* ≤ 22, big plastics'); ax.tick_params(axis='y', labelsize=6)
    fs.title(ax, 'All configurations', '_nf: no flash loss; others: 0.87 µs after the flash')
    fig.tight_layout()
    fs.save(fig, OUT / 'pw_reach_bars', data=q)


if __name__ == '__main__':
    main()
