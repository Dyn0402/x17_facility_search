#!/usr/bin/env python3
"""
bham_rates.py -- Birmingham target study: what the beam and the room do to the detector (TARGET_GEANT.md §5-6).

    ~/PycharmProjects/nTof_x17/.venv/bin/python birmingham/geant/bham_rates.py   # -> birmingham/out/geant/*.csv

Per target × detector, at 2.8 MeV × 30 mA, cell centre 2 m from the Li, 5 cm Pb in the bore, four sources:
  beam    the collimated beam through the target region (B2 neutrons, B3 478 keV and ⁸Be photons)
  room    the same beam after the target: dump, concrete, wall faces (R3 on the 30 bar cell minus B2/B3 of the same
          cell, scaled by the beam area)
  wall    what crosses the shield wall from the 4π source (R2: the staged neutron and ⁸Be-γ sources, both leaking
          neutrons and photons)
  cosmic  μ legs and two-arm triggers from L4; per channel the μ flux through the area (as shapes_rates.py)
Outputs:
  rates_channels.csv   per channel (busiest arm): clusters/s above 50 keV and above the leg threshold, deposited
                       MeV/s, the PMT anode current, the pile-up probability in 100 ns
  rates_legs.csv       legs and two-arm triggers per arm and source; Micromegas clusters per arm (occupancy)
  daq_live.csv         DREAM live time against the single-arm prescale P (inf = PAIR only), the P kept; the reach
                       uses the live time (exposure) and, as a sensitivity, live × e^(−2·occ_MM) (exposure_mm)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import bham_common as C

TAU = 298e-6                         # DREAM RAW, 20 samples (nTof_x17_DAQ report)
FMAX = 1 / TAU
TWO_TAU = 20e-9                      # hardware two-arm coincidence
MM_WIN = 1.2e-6                      # Micromegas memory (30 mm drift + shaping)
T_INT = 100e-9                       # scintillator integration (pile-up)
PRESCALES = (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, np.inf)     # inf: PAIR only, no single-arm output
PE_PER_MEV = {'plastic': 10.0, 'ls': 150.0}       # photo-electrons per MeV at the PMT (lnl_calo light yield; LS ×15)
GAIN = 1e6
E_CHARGE = 1.602176634e-19
THR = {'bar': 0.2376, 'plastic': 1.675, 'ls': 0.5, 'mm': 0.002}     # MM: a MIP leaves ~8 keV in 30 mm
MU_FLUX = 1.0 / 60                   # μ /cm²/s through a horizontal surface
MU_AREA = {'bigP': {'bar': 125.0, 'plastic': 5625.0}, 'asb': {'bar': 125.0, 'plastic': 600.0, 'ls': 2030.0}}


def chan_name(ch):
    return 'bar' if ch < 20 else ('plastic' if ch in (20, 21) else ('ls' if ch == 22 else 'mm'))


QUENCH = True                        # use the quenched light (MeVee) where the kept ROOT files were re-reduced


def chan_rates(name, kind, rate, pdf, scale=1.0, nsub=None):
    """per (arm, ch): clusters/s per energy bin [4, 24, nE] and MeV/s [4, 24] for one beam sample; in light (MeVee,
    from the 2 kept ROOT files, <name>_chanq.npz) where available and QUENCH, else in deposited energy."""
    hq = C.load_chanq(name) if QUENCH else None      # 2 kept files, quenched
    h = C.load_chan(name)                            # all files, deposited energy
    if h is None:
        return None
    if hq is not None and hq['hq'].sum() > 0:
        # scintillators: the quenched shape of the kept files, normalised to all files' cluster count per
        # (primary-energy bin, arm, channel); the Micromegas (ch 23) stays in deposited energy from all files
        nk, nf = float(hq['n_generated'][0]), float(h['n_generated'][0])
        full, kept = h['h'].sum(-1) / nf, hq['h'].sum(-1) / nk
        with np.errstate(divide='ignore', invalid='ignore'):
            f = np.where(kept > 0, full / kept, 0.0)
        Hq = hq['hq'] / nk * f[..., None] * nf
        Pq = hq['pq'] / nk * f * nf
        Hq[:, :, 23] = h['h'][:, :, 23]
        Pq[:, :, 23] = h['p'][:, :, 23]
        h = dict(h, h=Hq, p=Pq)
    N = float(h['n_generated'][0])
    en = h['en_edges']
    if kind is None:                                  # R2 leak: weights already per source particle
        f = np.ones(len(en) - 1) * rate / N
    elif pdf is None:                                 # a line: every primary is the line
        f = np.ones(len(en) - 1) * rate / N
    else:
        form, lo, hi = C.GEN[kind]
        f = np.zeros(len(en) - 1)
        for i in range(len(en) - 1):
            a, b = max(en[i], lo), min(en[i + 1], hi)
            if b <= a:
                continue
            m = (C.E_GRID >= a) & (C.E_GRID < b)
            src = np.trapezoid(pdf[m], C.E_GRID[m]) if m.sum() > 1 else 0.0
            f[i] = rate * src / ((b - a) / (hi - lo)) / N
    H = np.einsum('i,iacE->acE', f, h['h']) * scale
    P = np.einsum('i,iac->ac', f, h['p']) * scale
    return H, P, h['e_edges']


def table_rates(name, kind, rate, pdf, scale=1.0):
    """legs per arm, two-arm triggers, ok singles per arm [1/s] from a merged beam table."""
    z = C.load(name)
    if z is None:
        return None
    out = {}
    if kind is None:
        N = float(z['cnt_n_generated'])
        lg = rate * np.asarray(z['lg_w'], float) / N
        tr = rate * np.asarray(z['tr_w'], float) / N
        sg = rate * np.asarray(z['sg_w'], float) / N
    else:
        lg = C.row_rate(z, kind, rate, pdf, 'lg_En', 'lg_w')
        tr = C.row_rate(z, kind, rate, pdf, 'tr_En', 'tr_w')
        sg = C.row_rate(z, kind, rate, pdf, 'sg_En', 'sg_w')
    out['legs'] = np.bincount(z['lg_arm'].astype(int), lg, minlength=4) * scale
    # legs stay in deposited energy (the trigger definition): in the 2 kept ROOT files per sample the quenched
    # legs equal the deposited ones to a few %, since a leg needs a ≥ 1.675 MeV plastic deposit that only capture
    # γ (2.2 MeV on H) and multiple recoils reach (quench_check() prints the ratio)
    out['trig2'] = float(tr.sum()) * scale
    out['ok'] = np.bincount(z['sg_arm'].astype(int), sg, minlength=4) * scale
    return out


def quench_check():
    """Σ quenched legs / Σ deposited legs over every kept file (all targets, both detectors), unweighted."""
    e = q = 0
    for t in C.TARGETS:
        for det in C.DETS:
            h = C.load_chanq(f'B2_n_{t}_{det}')
            if h is not None and len(h['lg_e']):
                e += h['lg_e'].sum()
                q += h['lg_q'].sum()
    return q / max(e, 1), int(e)


def sources(target, det):
    """[(source, sample name, kind, rate, pdf, scale)] for one target and detector."""
    rates = C.source_rates(target)
    r30 = C.source_rates('c30')
    out = []
    for kind, run in (('n', 'B2'), ('g478', 'B3'), ('g8be', 'B3')):
        rate, pdf = rates[kind]
        out.append(('beam', f'{run}_{kind}_{target}_{det}', kind, rate, pdf, 1.0))
        # room return: R3 (c30, room) − B2/B3 (c30, no room), scaled by the beam rate (once R3 exists)
        if C.load_chan(f'R3_{kind}_c30_{det}') is not None:
            out.append(('room', f'R3_{kind}_c30_{det}', kind, r30[kind][0], r30[kind][1], rate / r30[kind][0]))
            out.append(('room', f'{run}_{kind}_c30_{det}', kind, r30[kind][0], r30[kind][1], -rate / r30[kind][0]))
    srcs = C.leak_sources()
    for src in ('nsrc', 'gsrc'):
        for t in ('n', 'g'):
            out.append(('wall', C.leak_name(src, t, det), None, srcs[src], None, 1.0))
    return out


def cosmic_legs(det):
    z = np.load(C.LSEL / f"L4_cosmic{'_bigP' if det == 'bigP' else ''}_sel.npz", allow_pickle=True)
    live = int(z['cnt_n_generated']) * 60.0 / (300.0 * 300.0)
    return np.array(z['cnt_leg_arm']) / live, int(z['cnt_trig2']) / live, np.array(z['cnt_ok_arm']) / live


def one(target, det):
    S = sources(target, det)
    ch, legs, rows = {}, {}, []
    eE = None
    for src, name, kind, rate, pdf, scale in S:
        r = chan_rates(name, kind, rate, pdf, scale)
        if r is not None:
            H, P, eE = r
            ch.setdefault(src, [np.zeros_like(H), np.zeros_like(P)])
            ch[src][0] += H
            ch[src][1] += P
        t = table_rates(name, kind, rate, pdf, scale)
        if t is not None:
            L = legs.setdefault(src, dict(legs=np.zeros(4), trig2=0.0, ok=np.zeros(4)))
            L['legs'] += t['legs']
            L['trig2'] += t['trig2']
            L['ok'] += t['ok']
    for src in ('room',):            # the difference can go slightly negative from MC noise
        if src in ch:
            ch[src][0] = np.clip(ch[src][0], 0, None)
            ch[src][1] = np.clip(ch[src][1], 0, None)
        if src in legs:
            for k in ('legs', 'ok'):
                legs[src][k] = np.clip(legs[src][k], 0, None)
            legs[src]['trig2'] = max(legs[src]['trig2'], 0.0)
    lm, tm, om = cosmic_legs(det)
    legs['cosmic'] = dict(legs=lm, trig2=tm, ok=om)
    # per channel, busiest arm
    if eE is not None:
        ec = np.sqrt(eE[1:] * eE[:-1])
        tot = sum(v[0] for v in ch.values())
        totP = sum(v[1] for v in ch.values())
        for c in range(24):
            nm = chan_name(c)
            if nm == 'mm':
                continue
            for src, (H, P) in list(ch.items()) + [('all', (tot, totP))]:
                a = int(np.argmax(tot[:, c, :].sum(1)))
                h = H[a, c]
                r50 = h[ec > 0.05].sum()
                rthr = h[ec > THR[nm]].sum()
                pw = P[a, c]
                cur = pw * PE_PER_MEV.get(nm, 0) * GAIN * E_CHARGE * 1e6 if nm in PE_PER_MEV else np.nan
                rows.append(dict(target=target, det=det, source=src, channel=c, kind=nm, arm=a, rate_50keV=r50,
                                 rate_thr=rthr, MeV_per_s=pw, anode_uA=cur, pileup_100ns=r50 * T_INT))
        mm = tot[:, 23, ec > THR['mm']].sum(1)
        mm_src = {s: v[0][:, 23, ec > THR['mm']].sum(1) for s, v in ch.items()}
    else:
        mm, mm_src = np.zeros(4), {}
    # cosmic μ per channel (analytic)
    for nm, a_mu in C_MU(det).items():
        rows.append(dict(target=target, det=det, source='cosmic', channel=-1, kind=nm, arm=-1,
                         rate_50keV=MU_FLUX * a_mu * 0.75, rate_thr=MU_FLUX * a_mu * 0.75, MeV_per_s=np.nan,
                         anode_uA=np.nan, pileup_100ns=np.nan))
    lg = []
    for src, L in legs.items():
        lg.append(dict(target=target, det=det, source=src, legs_max_arm=L['legs'].max(), legs_sum=L['legs'].sum(),
                       trig2_corr=L['trig2'], ok_max_arm=L['ok'].max(),
                       mm_clusters_max_arm=float(mm_src.get(src, np.zeros(4)).max()) if src != 'cosmic' else np.nan))
    Ltot = sum(L['legs'] for L in legs.values())
    corr = sum(L['trig2'] for L in legs.values())
    okt = sum(L['ok'] for L in legs.values())
    return rows, lg, Ltot, corr, okt, mm


def C_MU(det):
    return MU_AREA[det]


def daq(target, det, Ltot, corr, okt, mm, scales=(1.0, 0.5, 0.25, 0.1, 0.03, 0.01)):
    """DREAM live time vs the single-arm prescale P, at beam fraction s (cosmics not scaled)."""
    lm, tm, _ = cosmic_legs(det)
    out = []
    for s in scales:
        L = (Ltot - lm) * s + lm
        rand = sum(L[a] * L[b] for a in range(4) for b in range(a + 1, 4)) * TWO_TAU
        pair = rand + (corr - tm) * s + tm
        occ = float(mm.max()) * s * MM_WIN
        for P in PRESCALES:
            R = L.sum() / P + pair
            live = 1 / (1 + R * TAU)
            out.append(dict(target=target, det=det, beam_fraction=s, P=P, legs_max_arm=L.max(), legs_sum=L.sum(),
                            pair_trig=pair, rand_pair=rand, dream_rate=R, live=live, mm_occ=occ,
                            exposure=live, exposure_mm=live * np.exp(-2 * occ), MB_s_per_feu=R * 83.0 / 3350.0))
    return out


def pick_prescale(d):
    """per (target, det[, beam_fraction]): the smallest P with live ≥ 95 %, else the P with the best exposure."""
    out = []
    for _, g in d.groupby([c for c in ('target', 'det', 'beam_fraction') if c in d.columns]):
        ok = g[g.live >= 0.95]
        out.append(ok.sort_values('P').iloc[0] if len(ok) else g.sort_values('exposure').iloc[-1])
    return pd.DataFrame(out)


def room_variants():
    """the room return of the 30 bar cell's beam neutrons: dump at 2.5 m (R3) and at 6 m in a longer room (R4)."""
    r30 = C.source_rates('c30')
    rows = []
    for det in C.DETS:
        b = table_rates(f'B2_n_c30_{det}', 'n', *r30['n'])
        hb = chan_rates(f'B2_n_c30_{det}', 'n', *r30['n'])
        ec = np.sqrt(hb[2][1:] * hb[2][:-1])
        for run, lab in (('R3', 'dump at 2.5 m, room to 4 m'), ('R4', 'dump at 6 m, room to 7 m')):
            a = table_rates(f'{run}_n_c30_{det}', 'n', *r30['n'])
            ha = chan_rates(f'{run}_n_c30_{det}', 'n', *r30['n'])
            if a is None or ha is None:
                continue
            ch = 20
            sl = lambda H: H[:, ch][:, ec > 0.05].sum(1).max()       # noqa: E731
            mm = lambda H: H[:, 23][:, ec > THR['mm']].sum(1).max()  # noqa: E731
            rows.append({'detector': C.DETS[det], 'room': lab,
                         'legs /s, busiest arm': f"{(a['legs'] - b['legs']).max():,.0f}",
                         'correlated 2-arm /s': f"{a['trig2'] - b['trig2']:,.0f}",
                         'plastic > 50 keVee /s': f'{sl(ha[0]) - sl(hb[0]):.2g}',
                         'MM clusters /s': f'{mm(ha[0]) - mm(hb[0]):.2g}'})
    t = pd.DataFrame(rows)
    t.to_csv(C.OUT / 'room_variants.csv', index=False)
    return t


def wall_depth():
    """per source particle at each plane through the wall: neutrons and photons, inside the experimental room's
    footprint and off the bore, near the bore (r < 30 cm), and outside the footprint (round the model's wall)."""
    Y = {('s1', 1): -1450, ('s2', 1): -1050, ('s3', 1): -650, ('s3', 2): -600}
    LAB = {-1450: 'after 20 cm BPE', -1050: '+ 40 cm concrete', -650: '+ 80 cm concrete', -600: 'exit (+ 5 cm Pb)'}
    rows = []
    for src in ('n', 'g'):
        for (st, pl), y in Y.items():
            f = C.SEL / f'{st}_{src}_planes.npz'
            if not f.exists():
                continue
            z = np.load(f)
            m0 = z['plane'] == pl
            for t, nm in ((0, 'n'), (1, 'γ')):
                m = m0 & (z['type'] == t) & (z['uncol'] == 0)
                x, zz, w = z['x'][m], z['z'][m], z['w'][m]
                r = np.hypot(x, zz)
                out = (np.abs(x) > 2500) | (zz > 2500) | (zz < -1700)
                rows.append({'source': '4π neutrons' if src == 'n' else '⁸Be γ', 'plane': LAB[y], 'particle': nm,
                             'room, off bore': f'{w[~out & (r >= 300)].sum():.2g}', 'within 30 cm of the bore':
                             f'{w[r < 300].sum():.2g}', 'outside the room': f'{w[out].sum():.2g}'})
    t = pd.DataFrame(rows)
    t.to_csv(C.OUT / 'wall_depth.csv', index=False)
    return t


def main():
    C.OUT.mkdir(parents=True, exist_ok=True)
    R, Lg, D = [], [], []
    for det in C.DETS:
        for t in C.TARGETS:
            rows, lg, Ltot, corr, okt, mm = one(t, det)
            R += rows
            Lg += lg
            D += daq(t, det, Ltot, corr, okt, mm)
    r, lg, d = pd.DataFrame(R), pd.DataFrame(Lg), pd.DataFrame(D)
    r.to_csv(C.OUT / 'rates_channels.csv', index=False, float_format='%.4g')
    lg.to_csv(C.OUT / 'rates_legs.csv', index=False, float_format='%.4g')
    # the prescale kept: the smallest P with live ≥ 95 % at full beam
    keep = pick_prescale(d[d.beam_fraction == 1.0])
    d.to_csv(C.OUT / 'daq_scan.csv', index=False, float_format='%.4g')
    keep.to_csv(C.OUT / 'daq_live.csv', index=False, float_format='%.4g')
    pd.set_option('display.width', 250)
    print(lg.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    print(keep.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    big = r[(r.source == 'all') & (r.kind != 'bar')]
    print(big.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    print(room_variants().to_string(index=False))
    if not (C.OUT / 'wall_depth.csv').exists():
        print(wall_depth().to_string(index=False))
    q, n = quench_check()
    print(f'quenched / deposited legs in the kept files: {q:.3f} ({n} legs)')


if __name__ == '__main__':
    import sys as _s
    if '--wall' in _s.argv:
        C.WALL = _s.argv[_s.argv.index('--wall') + 1]
        C.OUT = C.OUT / C.WALL
        C.OUT.mkdir(parents=True, exist_ok=True)
    main()
