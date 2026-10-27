#!/usr/bin/env python3
"""
bham_geant.py -- Birmingham target study, the reach (TARGET_GEANT.md §4).

    bash birmingham/geant/fetch_sel.sh
    ~/PycharmProjects/nTof_x17/.venv/bin/python birmingham/geant/bham_geant.py   # -> birmingham/out/geant/reach*.csv

The LNL machinery (lnl/target/opt_geant.py, SHAPES_GEANT.md §2) with the vertex of a gas target:
  * calorimetry: LNL-calibrated response (lnl_calo 'LNL calibrated');
  * MM segments smeared by 15°; each segment's closest approach to the beam axis gives (y_k, r_k); pointing
    r_k < D (90 % of the target's own X17 segments), collinearity ≥ 20°, arm-to-arm TOF (0.3 ns) cosmic veto;
  * vertex (0, ȳ, 0), ȳ = mean of y_k clipped to the gas; opening angle from the vertex to the two MM charge
    centroids;
  * Asimov/Fisher in θ (90-180°, 2° bins) × |y| (6 bins) × n_down (0-2), IPC(E1) and the correlated beam term
    free, cosmics and accidentals fixed; best E_sum window.
Signal: X17 = ρ · IPC(E1) at W = E*(0.5 MeV), ρ_ATOMKI = 1.5×10⁻³; IPC from the analytic capture rate
(bham_targets.py, thin target) × α_E1.  Days to 3σ at ρ_ATOMKI at full current (30 mA), with the DREAM live time
and the Micromegas occupancy from bham_rates.py (exposure factor), and ρ at 3σ in 14 and 50 days.
"""
from __future__ import annotations

import zlib

import numpy as np
import pandas as pd

import bham_common as C
import lnl_calo as LC           # noqa: E402
import lnl_geant as G           # noqa: E402
import survey_yield as Y        # noqa: E402

RESP = 'LNL calibrated'
SEG_DEG = 15.0
BINS = np.arange(70, 181, 2.0)
XC = 0.5 * (BINS[1:] + BINS[:-1])
FIT = XC >= 90.0
YB = np.array([0.0, 0.15, 0.3, 0.45, 0.6, 0.8, 1.0])
ECUTS = [(lo, hi) for lo in (8, 10, 11, 12, 13, 14) for hi in (18, 19, 20, 22, 99)]
W05 = float(Y.F.w_of_en(np.array([0.5]))[0])
WITH_PILEUP = True
MM_PENALTY = False


def DAQ_DIR():
    """bham_rates.py outputs of this wall variant (the --mm sensitivity writes one level down)."""
    return C.OUT.parent if MM_PENALTY else C.OUT
          # True: exposure × e^(−2·occ_MM) (sensitivity; --mm)


def ipc_f40(mult):
    from sept26_prelim_analysis import ipc_born
    return float(ipc_born.frac_above(ipc_born.grid_spectrum(mult, W05), 40.0))


def axis_point(c, d):
    """closest approach of the line c + t d to the beam (y) axis: (y, r)."""
    den = d[:, 0] ** 2 + d[:, 2] ** 2
    t = -(c[:, 0] * d[:, 0] + c[:, 2] * d[:, 2]) / np.where(den > 0, den, np.nan)
    p = c + t[:, None] * d
    return p[:, 1], np.hypot(p[:, 0], p[:, 2])


PILEUP: dict = {}     # (target, det) -> [(mean hits per gate, energy-bin centres MeVee, probabilities)], per arm


def pileup_model(target, det, scale=1.0):
    """beam pile-up in each arm's calorimeter gate (100 ns): the quenched per-channel spectra of the busiest arm
    (bham_rates.py) for the back plastic(s) and the LS; the SiPM bars are left out (≤ 2×10⁴ /s each)."""
    import bham_rates as BR
    out = []
    by = {}
    eE = None
    for src, name, kind, rate, pdf, sc in BR.sources(target, det):
        r = BR.chan_rates(name, kind, rate, pdf, sc)
        if r is None:
            continue
        H, P, eE = r
        by[src] = H if src not in by else by[src] + H
    if not by:
        return []
    tot = sum(np.clip(h, 0, None) for h in by.values())
    ec = np.sqrt(eE[1:] * eE[:-1])
    for ch in ((20,) if det == 'bigP' else (20, 21, 22)):
        h = np.clip(tot[:, ch, :], 0, None)
        a = int(np.argmax(h.sum(1)))
        hh = h[a] * (ec > 0.01)
        if hh.sum() > 0:
            out.append((hh.sum() * BR.T_INT * scale, ec, hh / hh.sum()))
    return out


def add_pileup(E, model, rng):
    """E [n, 2] arm energies (MeV, after the response) + the pile-up of the model in each arm."""
    for mu, ec, pr in model:
        k = rng.poisson(mu, E.shape)
        tot = k.sum()
        if tot:
            e = rng.choice(ec, tot, p=pr)
            idx = np.repeat(np.arange(E.size), k.ravel())
            E.ravel()[:] += np.bincount(idx, e, minlength=E.size)
    return E


def recon(z, hw, target, D=None, seed=0, tof=True):
    """reconstructed θ, |y|, n_down, E_sum and the pass mask of every two-arm row of z."""
    rng = np.random.default_rng(seed)
    z = LC.respond(dict(z, Esum=z['E1'] + z['E2'], name=z.get('name', 'x')), hw, RESP, seed=seed)
    det = 'bigP' if hw == 'big plastics' else 'asb'
    if PILEUP.get((target, det)):
        E = add_pileup(np.stack([z['E1'], z['E2']], 1).astype(float), PILEUP[(target, det)], rng)
        z = dict(z, E1=E[:, 0], E2=E[:, 1])
    d1, d2 = z['d_dom1'].astype(float), z['d_dom2'].astype(float)
    good = np.isfinite(d1).all(1) & np.isfinite(d2).all(1)
    s1 = G.smear_dir(np.where(np.isfinite(d1), d1, 1.0), SEG_DEG, rng)
    s2 = G.smear_dir(np.where(np.isfinite(d2), d2, 1.0), SEG_DEG, rng)
    c1 = np.where(np.isfinite(z['c_dom1']), z['c_dom1'], 0.0).astype(float)
    c2 = np.where(np.isfinite(z['c_dom2']), z['c_dom2'], 0.0).astype(float)
    y1, r1 = axis_point(c1, s1)
    y2, r2 = axis_point(c2, s2)
    lo, hi = C.GAS_Y.get(target, (-200.0, 200.0))
    yv = np.clip(np.nan_to_num(0.5 * (y1 + y2)), lo, hi)
    v = np.zeros((len(yv), 3))
    v[:, 1] = yv
    a, b = z['c_all1'].astype(float) - v, z['c_all2'].astype(float) - v
    cs = (a * b).sum(1) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1))
    th = np.degrees(np.arccos(np.clip(cs, -1, 1)))
    rr = np.maximum(np.nan_to_num(r1, nan=1e9), np.nan_to_num(r2, nan=1e9))
    ok = good & (G.line_angle(s1, s2) >= G.COLL_DEG)
    if D is not None:
        ok &= rr < D
    if tof:
        ok &= G.pass_tof(z, G.LEVELS['MM 15° + TOF'], seed)
    E1, E2 = z['E1'], z['E2']
    nd = (z['c_all1'][:, 1] > yv).astype(int) + (z['c_all2'][:, 1] > yv).astype(int)
    return dict(th=th, absy=np.abs(E1 - E2) / np.maximum(E1 + E2, 1e-9), ndown=nd, Es=E1 + E2, ok=ok, rr=rr,
                yv=yv, ytrue=z['V'][:, 1] if 'V' in z else np.zeros(len(yv)))


def pointing_D(target, det):
    """90 % of the X17 pairs' larger axis distance (the pointing cut, per target)."""
    z = C.load(f'B1_X17_En0.5_{target}_{det}')
    if z is None:
        return None
    r = recon(z, C.DETS[det], target, None, seed=1, tof=False)
    return float(np.percentile(r['rr'][np.isfinite(r['rr']) & (r['rr'] < 1e8)], 90))


def kde(x, w):
    from scipy.special import ndtr
    if len(x) == 0:
        return np.zeros(len(XC))
    xx, ww = np.r_[x, 360.0 - x], np.r_[w, w]
    c = ndtr((BINS[None, :] - xx[:, None]) / G.KDE_BW_DEG)
    return ((c[:, 1:] - c[:, :-1]) * ww[:, None]).sum(0)


def hist3(r, m, w, smooth):
    iy = np.clip(np.digitize(r['absy'][m], YB) - 1, 0, len(YB) - 2)
    cat = iy * 3 + r['ndown'][m]
    th, ww = r['th'][m], w[m]
    out = []
    for c in range(3 * (len(YB) - 1)):
        k = cat == c
        out.append(kde(th[k], ww[k]) if smooth else np.histogram(th[k], BINS, weights=ww[k])[0])
    return np.stack(out)


def per_day(target, det):
    """per-row weights [1/day] and reconstructions of every component, before the E_sum cut."""
    hw = C.DETS[det]
    D = pointing_D(target, det)
    if D is None:
        return None
    tt = {r['key']: r for _, r in __import__('bham_targets').rows(C.EP, C.CURRENT, C.DIST_M)[0].iterrows()}
    cap = tt[target]['captures_per_s'] * np.exp(-C.MU_PB['n'] * C.PB_CM)
    alpha = float(Y.alpha(np.array([0.5]))[0])
    ipc_day = cap * alpha * C.DAY
    comp = {'_meta': dict(D=D, captures_per_s=cap, ipc_per_day=ipc_day)}
    for kind, nm, wfun in (('x17', 'X17_En0.5', lambda n: C.RHO_REF * ipc_day / n),
                           ('E1', 'E1_En0.5', lambda n: ipc_day * ipc_f40('E1') / n),
                           ('M1', 'M1_En0.5', lambda n: ipc_day * ipc_f40('M1') / n)):
        z = C.load(f'B1_{nm}_{target}_{det}')
        if z is None:
            return None
        n = int(z['cnt_n_generated'])
        r = recon(z, hw, target, D, seed=zlib.crc32(f'{nm}{target}{det}'.encode()))
        comp[kind] = (r, np.full(len(r['th']), wfun(n)))
        if kind == 'x17':
            comp['_meta']['x17_ngen'] = n
            comp['_meta']['x17_theta'] = z['theta']
    zc = dict(np.load(C.LSEL / f"L4_cosmic{'_bigP' if det == 'bigP' else ''}_sel.npz", allow_pickle=True))
    rc = recon(zc, hw, target, D, seed=77)
    comp['cos'] = (rc, np.full(len(rc['th']), C.DAY / (int(zc['cnt_n_generated']) * G.MU_LIVE_S)))
    # correlated beam: the beam's own two-arm events (B2 neutrons, B3 photons) + the room return (R3 − nothing:
    # R3 rows whose first collision is in the room, the wall or the dump), scaled to this target's beam area
    rates = C.source_rates(target)
    parts = []
    for kind, run in (('n', 'B2'), ('g478', 'B3'), ('g8be', 'B3')):
        rate, pdf = rates[kind]
        z = C.load(f'{run}_{kind}_{target}_{det}')
        if z is not None and len(z['En']):
            r = recon(z, hw, target, D, seed=5)
            r['src'] = np.full(len(r['th']), 'cell')
            parts.append((r, C.row_rate(z, kind, rate, pdf) * C.DAY))
        zr = C.load(f'R3_{kind}_c30_{det}')
        if zr is not None and len(zr['En']):
            m = C.room_mask(zr)
            if m is not None and m.any():
                rate30, pdf30 = C.source_rates('c30')[kind]
                r = recon(zr, hw, target, D, seed=6)
                r['src'] = np.full(len(r['th']), 'room')
                w = C.row_rate(zr, kind, rate30, pdf30) * C.DAY * m * (rate / rate30)
                parts.append((r, w))
    # leakage through the wall (R2): two-arm events of the leaking particles
    srcs = C.leak_sources()
    for src in ('nsrc', 'gsrc'):
        for t in ('n', 'g'):
            z = C.load(C.leak_name(src, t, det))
            if z is not None and len(z['En']):
                r = recon(z, hw, target, D, seed=8)
                r['src'] = np.full(len(r['th']), 'wall')
                parts.append((r, srcs[src] * np.asarray(z['w'], float) / float(z['cnt_n_generated']) * C.DAY))
    if parts:
        rb = {k: np.concatenate([p[0][k] for p in parts]) for k in parts[0][0]}
        comp['beam'] = (rb, np.concatenate([p[1] for p in parts]))
    return comp


POOL: dict = {}


def pool_beam(comps, det):
    """pooled pass fractions of the correlated beam events over every target of one detector set (a handful of MC
    events per target pass all cuts, so the beam term is factorised: each two-arm event at its own θ, |y|, n_down ×
    the pooled fraction passing pointing + TOF, and the pooled fraction inside the E_sum window, per window)."""
    rs = [c['beam'][0] for c in comps if c is not None and 'beam' in c]
    if not rs:
        return
    src = np.concatenate([r['src'] for r in rs])
    ok = np.concatenate([r['ok'] for r in rs])
    es = np.concatenate([r['Es'] for r in rs])
    POOL[det] = {}
    for k in np.unique(src):
        m = src == k
        POOL[det][k] = dict(f_ok=ok[m].mean(), n=int(m.sum()),
                            f_E={ec: float(((es[m] > ec[0]) & (es[m] < ec[1])).mean()) for ec in ECUTS})


def templates(comp, ec, expo=1.0, det=None):
    T = {}
    for k in ('x17', 'E1', 'M1', 'cos', 'beam'):
        if k not in comp:
            T[k] = np.zeros((3 * (len(YB) - 1), len(XC)))
            continue
        r, w = comp[k]
        if k == 'beam' and det in POOL:
            f = np.zeros(len(w))
            for src, pl in POOL[det].items():
                f[r['src'] == src] = pl['f_ok'] * pl['f_E'][ec]
            T[k] = hist3(r, np.ones(len(w), bool), w * f * expo, smooth=True)
            continue
        m = r['ok'] & (r['Es'] > ec[0]) & (r['Es'] < ec[1])
        T[k] = hist3(r, m, w * (1.0 if k == 'cos' else expo), smooth=k != 'x17')
    return T


def fisher_days(T, ipc='E1'):
    s = T['x17'][:, FIT].ravel()
    comps = [T[ipc][:, FIT].ravel(), T['beam'][:, FIT].ravel()]
    mu = s + sum(comps) + T['cos'][:, FIT].ravel()
    sig = G.fisher_sigma(s, comps, mu)           # σ(ρ/ρ_ATOMKI) in one day
    return 9 * sig ** 2


def sigma68(comp):
    r, _ = comp['x17']
    th = comp['_meta']['x17_theta']
    m = r['ok']
    d = (r['th'] - th)[m]
    q = np.percentile(d, [16, 84]) if m.sum() > 50 else [np.nan] * 2
    return 0.5 * (q[1] - q[0]), m.sum() / comp['_meta']['x17_ngen']


def main(expo_table=None):
    C.OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    ex = {}
    if expo_table is None and (DAQ_DIR() / 'daq_live.csv').exists():
        d = pd.read_csv(DAQ_DIR() / 'daq_live.csv')
        ex = {(r.target, r.det): (r.exposure_mm if MM_PENALTY else r.exposure) for r in d.itertuples()}
    for det in C.DETS:
        if WITH_PILEUP:
            for t in C.TARGETS:
                PILEUP[(t, det)] = pileup_model(t, det)
                print(f'{det} {t}: pile-up per 100 ns gate ' + ', '.join(f'{m[0]:.3g}' for m in PILEUP[(t, det)]))
        comps = {t: per_day(t, det) for t in C.TARGETS}
        pool_beam(list(comps.values()), det)
        for k, pl in POOL.get(det, {}).items():
            print(f"{det}: beam term '{k}': {pl['n']} two-arm MC events pooled over the targets, "
                  f"pointing + TOF {pl['f_ok']:.3f}")
        for t in C.TARGETS:
            comp = comps[t]
            if comp is None:
                print(f'{t} {det}: tables missing')
                continue
            s68, acc = sigma68(comp)
            expo = ex.get((t, det), 1.0)
            best = None
            for ec in ECUTS:
                T = templates(comp, ec, expo, det)
                d = fisher_days(T)
                if best is None or d < best[0]:
                    best = (d, ec, T)
            d, ec, T = best
            dM1 = fisher_days(T, 'M1')
            w = (XC >= 100) & (XC < 150)
            per = {k: float(T[k][:, w].sum()) for k in T}
            rho50 = C.RHO_REF * np.sqrt(d / 50.0)
            rows.append(dict(target=t, label=C.LABEL[t], det=det, D_mm=comp['_meta']['D'],
                             captures_per_s=comp['_meta']['captures_per_s'], ipc_per_day=comp['_meta']['ipc_per_day'],
                             x17_acc=acc, sigma68_deg=s68, exposure=expo, esum=f'{ec[0]}-{ec[1]}',
                             days_3sigma_ATOMKI=d, days_M1_shape=dM1, rho3_14d=C.RHO_REF * np.sqrt(d / 14.0),
                             rho3_50d=rho50, x17_win_day=per['x17'], ipc_win_day=per['E1'], cos_win_day=per['cos'],
                             beam_win_day=per['beam']))
            print(f'{det:5s} {t:7s} D {comp["_meta"]["D"]:5.0f} mm  acc {acc:.3f}  σ68 {s68:5.1f}°  E_sum {ec}  '
                  f'days {d:8.3g}  ρ50 {rho50:.2g}  per day in 100-150°: X17 {per["x17"]:.3g} IPC {per["E1"]:.3g} '
                  f'cos {per["cos"]:.3g} beam {per["beam"]:.3g}', flush=True)
    t = pd.DataFrame(rows)
    t.to_csv(C.OUT / 'reach.csv', index=False, float_format='%.4g')
    # the survey dashboard's study format (survey/dashboard.py g4_reach): key, hw, days, rho3
    pd.DataFrame(dict(key=t.target, hw=t.det.map(C.DETS), days=50, rho3=t.rho3_50d, rho3_floor=np.nan)).to_csv(
        C.OUT / 'dashboard_reach.csv', index=False, float_format='%.4g')
    return t


def current_scan(fracs=(1.0, 0.5, 0.25, 0.1)):
    """days to 3σ at ρ_ATOMKI against the beam current (fraction of 30 mA): signal, IPC and the beam term ∝ s;
    cosmics fixed; pile-up per gate ∝ s; DREAM live (smallest prescale with ≥ 95 %) and MM occupancy at s."""
    d = pd.read_csv(DAQ_DIR() / 'daq_scan.csv') if (DAQ_DIR() / 'daq_scan.csv').exists() else None
    rows = []
    for det in C.DETS:
        for t in C.TARGETS:
            base = pileup_model(t, det) if WITH_PILEUP else []
            for s in fracs:
                PILEUP[(t, det)] = [(m[0] * s, m[1], m[2]) for m in base]
                comp = per_day(t, det)
                if comp is None:
                    continue
                expo = 1.0
                if d is not None:
                    import bham_rates as BR
                    q = d[(d.target == t) & (d.det == det) & np.isclose(d.beam_fraction, s)]
                    if len(q):
                        k = BR.pick_prescale(q).iloc[0]
                        expo = float(k.exposure_mm if MM_PENALTY else k.exposure)
                for k in ('x17', 'E1', 'M1', 'beam'):
                    if k in comp:
                        comp[k] = (comp[k][0], comp[k][1] * s)
                best = min((fisher_days(templates(comp, ec, expo, det)), ec) for ec in ECUTS)
                rows.append(dict(target=t, det=det, beam_fraction=s, current_mA=30 * s, exposure=expo,
                                 pileup_slab=base[0][0] * s if base else 0.0, days=best[0],
                                 esum=f'{best[1][0]}-{best[1][1]}'))
                print(rows[-1], flush=True)
    out = pd.DataFrame(rows)
    out.to_csv(C.OUT / 'days_vs_current.csv', index=False, float_format='%.4g')
    return out


if __name__ == '__main__':
    import sys as _s
    if '--wall' in _s.argv:
        C.WALL = _s.argv[_s.argv.index('--wall') + 1]
        C.OUT = C.OUT / C.WALL
        C.OUT.mkdir(parents=True, exist_ok=True)
    import sys
    if '--mm' in sys.argv:
        MM_PENALTY = True
        C.OUT = C.OUT / 'mm_penalty'
    t = main()
    if '--scan' in sys.argv:
        current_scan()
