#!/usr/bin/env python3
"""
nfs_reach.py -- X17 reach at GANIL/NFS from the Geant4 campaign, as a function
of the neutron-energy window, with and without using the TOF-tagged E_n.

    python ganil_nfs/sim/nfs_reach.py            # -> ganil_nfs/out/reach/

Inputs (merged tables from nfs_merge.py, copied from EOS into sim/sel/):
  N1_X17_En<E>[_bigP]   X17 (16.8 MeV) at W = E*(E_n), ⁴He* boosted by β_cm
  N2_E1_En<E>[_bigP]    Born E1 IPC at the same W, generated at θ ≥ 40°
  N3_beam[_bigP]        NFS d(40)+Be neutrons on the cell (beam-induced background)
  L4_cosmic[_bigP]      the LNL cosmic samples (same arms; target irrelevant)

Per event:
  * vertex: the beam-axis point closest to the two Micromegas segments (the
    40 cm cell makes the "vertex at the origin" chord useless);
  * θ: the angle between the two vertex → charge-centroid chords;
  * calorimetry: the lnl_calo 'LNL calibrated' response (repaired liquid for
    the as-built stack; the 75 × 75 × 5 cm plates for big plastics);
  * m_ee = W √((1 − y²)(1 − cos θ)/2), y = |E1 − E2|/(E1 + E2), with W from the
    event's E_n: TOF gives E_n event by event, so W is known.  The X17 sits at
    16.8 MeV whatever the neutron energy -- the "moving bump" becomes a fixed one.

Analyses compared, each Asimov over histogram bins:
  m_ee | E_n   m_ee histogram in each E_n bin (TOF used twice: binning and W)
  θ | E_n      θ histogram in each E_n bin: the edge moves, the bins follow it
  θ, no TOF    one θ histogram summed over E_n: what an untagged beam gives

Rates: the fold (ganil_nfs/nfs_fold.py: 50 µA, Ω = 2.82e-5 sr, 30 bar × 40 cm)
for the IPC, the X17 as ρ = X17 / IPC(E1) at every E_n (constant: an
assumption -- nobody knows how the X17 branching evolves with E*), DREAM
live time from the trigger rate the beam itself makes.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
NFS = HERE.parent
ROOT = NFS.parent
sys.path.insert(0, str(NFS))
sys.path.insert(0, str(ROOT / 'ill'))
sys.path.insert(0, str(Path.home() / 'PycharmProjects/nTof_x17'))
import nfs_fold as F                                         # noqa: E402

SEL = HERE / 'sel'
SEL_BEAM = HERE / 'sel_beam'     # beam tables in per-arm time clusters (nfs_beam_merge.py)
OUT = NFS / 'out' / 'reach'
DAY = 86400.0
NODES = [0.5, 1, 2, 3.5, 5, 7, 10, 14, 20]
EDGES = [0.2, 0.75, 1.5, 2.75, 4.25, 6.0, 8.5, 12.0, 17.0, 25.0]
RHO_REF = 1.5e-3            # X17 / IPC, ATOMKI ⁴He (PRC 104 044003), the pessimistic plan value
IPC_MIN_OPEN = 40.0         # deg, N2 generation cut
TAU_DAQ = 298e-6            # s, DREAM RAW 20 samples
FLIGHT_M = 13.6             # m, the 8 cm-spot position
REP_HZ = 440e3              # bunch rate (wrap-around ≥ 0.18 MeV at 13.6 m)
DCA_MAX = 60.0              # mm, each MM segment must pass this close to the beam axis
COSMIC_S_PER_EVENT = 60.0 / (300.0 * 300.0)   # s of live time per generated cosmic (3 × 3 m plane)
HW = {'as built': '', 'big plastics': '_bigP'}

# lnl_calo 'LNL calibrated' (per layer: a [√MeV], c, threshold [MeV])
SIPM = dict(a=0.19, c=0.04, thr=0.10)
PL2 = dict(a=0.32, c=0.02, thr=0.30)
LS = dict(a=0.50, c=0.15, thr=0.5)
BIG = dict(a=0.20, c=0.05, thr=0.30)


def _layer(e, p, rng):
    e = np.asarray(e, float)
    m = e * (1 + p['c'] * rng.standard_normal(e.shape))
    m = m + p['a'] * np.sqrt(np.clip(e, 0, None)) * rng.standard_normal(e.shape)
    m = np.clip(m, 0, None)
    return np.where(m > p['thr'], m, 0.0)


def respond(z, hw, seed=0):
    rng = np.random.default_rng(seed)
    es, ep, el = (z[k].astype(float) for k in ('E_sipm_a', 'E_plast_a', 'E_ls_a'))
    m = _layer(es, SIPM, rng) + _layer(ep, BIG if hw == 'big plastics' else PL2, rng)
    if hw != 'big plastics':
        m = m + _layer(el, LS, rng)
    return m[:, 0], m[:, 1]


def seg_y(c, d):
    """y where the segment line c + t d passes closest to the beam (y) axis, and that distance."""
    den = d[:, 0] ** 2 + d[:, 2] ** 2
    t = -(c[:, 0] * d[:, 0] + c[:, 2] * d[:, 2]) / np.where(den > 0, den, np.nan)
    p = c + t[:, None] * d
    return p[:, 1], np.hypot(p[:, 0], p[:, 2])


def events(z, hw, W, seed=0):
    """reconstructed variables for every two-arm event of a table; W per event (array or scalar)."""
    c1, c2 = z['c_all1'].astype(float), z['c_all2'].astype(float)
    y1, r1 = seg_y(z['c_dom1'].astype(float), z['d_dom1'].astype(float))
    y2, r2 = seg_y(z['c_dom2'].astype(float), z['d_dom2'].astype(float))
    ok = np.isfinite(y1) & np.isfinite(y2) & (r1 < DCA_MAX) & (r2 < DCA_MAX)
    yv = np.where(ok, 0.5 * (y1 + y2), 0.0)
    yv = np.clip(yv, -200, 200)
    v = np.zeros_like(c1)
    v[:, 1] = yv
    a, b = c1 - v, c2 - v
    cs = (a * b).sum(1) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1))
    th = np.degrees(np.arccos(np.clip(cs, -1, 1)))
    E1, E2 = respond(z, hw, seed)
    Es = E1 + E2
    y = np.abs(E1 - E2) / np.maximum(Es, 1e-9)
    W = np.broadcast_to(np.asarray(W, float), th.shape)
    m = W * np.sqrt(np.clip((1 - y ** 2) * (1 - np.cos(np.radians(th))) / 2, 0, None))
    return pd.DataFrame(dict(th=th, m=m, Es=Es, y=y, ok=ok, yv=yv, yv_true=z['V'][:, 1]))


def load(name, where=None):
    for d in ([where] if where else [SEL]):
        p = d / f'{name}_sel.npz'
        if p.exists():
            return dict(np.load(p, allow_pickle=True))
    return None


def ipc_frac_above(w, deg=IPC_MIN_OPEN):
    from sept26_prelim_analysis import ipc_born
    y = ipc_born.grid_spectrum('E1', float(w))
    return ipc_born.frac_above(y, deg)


def tof_s(e_mev, L=FLIGHT_M):
    g = 1 + e_mev / F.M_N
    return L / (299792458.0 * np.sqrt(1 - 1 / g ** 2))


# forced + roulette in time clusters first, then the analog run in clusters, then the old
# whole-event reduction of the analog run (arm energies summed over all time)
BEAM_SAMPLES = (('N4_beam_force', SEL_BEAM), ('N3_beam', SEL_BEAM), ('N3_beam', SEL))
L_GUN_M = FLIGHT_M - 1.2    # the gun sits 1.2 m upstream of the detector centre (cell window − 1 m)
T_BUNCH = 1.0 / REP_HZ
COINC_NS = 5.0              # two arms in coincidence: |Δt| < 5 ns (assumed; scintillator timing)


def tof_bin(En, t_ns):
    """E_n bin from the measured time: time since the bunch, folded into the bunch period,
    converted back to E_n over FLIGHT_M.  Without times (analog N3 tables), the true E_n."""
    En = np.asarray(En, float)
    if t_ns is None:
        return np.digitize(En, EDGES) - 1
    t = np.where(np.isfinite(t_ns), t_ns, 0.0) * 1e-9 + tof_s(En, L_GUN_M)
    t = np.mod(t, T_BUNCH)
    edges_t = tof_s(np.array(EDGES))                 # decreasing in E
    k = len(EDGES) - 1 - np.digitize(t, edges_t[::-1])   # bin index in E order
    k = np.where((t < edges_t[-1]) | (t > edges_t[0]), -1, k)
    return k


def accidentals(zb, hw, per_s, esum_frac, max_pairs=2_000_000, seed=1):
    """Random two-arm coincidences of beam singles from different neutrons of one bunch.
    Within an E_n bin (TOF window of width Δt_k) singles are taken as uniform in time:
    pairs/s = REP · Σ_{arm a<b} N_a N_b · 2δ/Δt_k, N = singles per bunch; every MC pair
    (i in a, j in b, different events) carries its share n_i n_j 2δ/Δt_k REP."""
    rng = np.random.default_rng(seed)
    t = zb['sg_t_sipm'].astype(float)
    k = tof_bin(zb['sg_En'], t)
    n = (zb['sg_w'] if 'sg_w' in zb else np.ones(len(zb['sg_En']))) * per_s / REP_HZ                    # expected singles per bunch, per MC single
    ev_id = zb['sg_ev']
    out = []
    for kb in range(len(NODES)):
        dt = tof_s(EDGES[kb]) - tof_s(EDGES[kb + 1])
        W = float(F.w_of_en(NODES[kb]))
        for a1 in range(4):
            for a2 in range(a1 + 1, 4):
                i = np.nonzero((k == kb) & (zb['sg_arm'] == a1))[0]
                j = np.nonzero((k == kb) & (zb['sg_arm'] == a2))[0]
                if not len(i) or not len(j):
                    continue
                npair = len(i) * len(j)
                if npair > max_pairs:
                    I, J = rng.choice(i, max_pairs), rng.choice(j, max_pairs)
                    scale = npair / max_pairs
                else:
                    I, J = (x.ravel() for x in np.meshgrid(i, j, indexing='ij'))
                    scale = 1.0
                keep = ev_id[I] != ev_id[J]
                I, J = I[keep], J[keep]
                z = {'c_all1': zb['sg_c_all'][I], 'c_all2': zb['sg_c_all'][J],
                     'c_dom1': zb['sg_c_dom'][I], 'd_dom1': zb['sg_d_dom'][I],
                     'c_dom2': zb['sg_c_dom'][J], 'd_dom2': zb['sg_d_dom'][J],
                     'E_sipm_a': np.stack([zb['sg_E_sipm'][I], zb['sg_E_sipm'][J]], 1),
                     'E_plast_a': np.stack([zb['sg_E_plast'][I], zb['sg_E_plast'][J]], 1),
                     'E_ls_a': np.stack([zb['sg_E_ls'][I], zb['sg_E_ls'][J]], 1),
                     'V': np.zeros((len(I), 3))}
                d = events(z, hw, W, seed=seed + kb)
                d['w'] = n[I] * n[J] * scale * (2 * COINC_NS * 1e-9 / dt) * REP_HZ * DAY
                d['kind'], d['bin'] = 'acc', kb
                out.append(d[d.ok & (d.Es > esum_frac * W)])
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()


# --------------------------------------------------------------------------- #
def build(hw, esum_frac=0.5):
    """per E_n bin: signal and background event lists with per-day weights."""
    tag = HW[hw]
    fold = pd.read_csv(NFS / 'out' / 'fold_table.csv')
    rows, ev = [], []
    for k, en in enumerate(NODES):
        lo, hi = EDGES[k], EDGES[k + 1]
        msk = (fold.E_n >= lo) & (fold.E_n <= hi)
        cap = float(np.trapezoid(fold.cap_per_s_MeV[msk], fold.E_n[msk]))
        w_ = float(F.w_of_en(en))
        ipc = cap * float(F.alpha_e1(w_)[0]) * DAY                # IPC pairs / day (beam-on)
        zx, zi = load(f'N1_X17_En{en:g}{tag}'), load(f'N2_E1_En{en:g}{tag}')
        if zx is None or zi is None:
            continue
        f40 = ipc_frac_above(w_)
        for kind, z, per_day in (('X17', zx, RHO_REF * ipc), ('IPC', zi, ipc * f40)):
            ngen = int(z['cnt_n_generated'])
            d = events(z, hw, w_)
            d['w'] = per_day / ngen
            d['kind'], d['bin'] = kind, k
            d = d[d.ok & (d.Es > esum_frac * w_)]
            ev.append(d)
        rows.append(dict(bin=k, E_n=en, lo=lo, hi=hi, W=w_, captures_per_s=cap, ipc_per_day=ipc,
                         f_ipc_above40=f40, theta_min=float(F.theta_min_deg(en))))
    bins = pd.DataFrame(rows)

    # beam-induced: every two-arm beam event, binned by its measured time of flight
    zb, beam_name = None, None
    for nm, where in BEAM_SAMPLES:
        zb = load(nm + tag, where)
        if zb is not None:
            beam_name = f'{nm}{tag} ({where.name})'
            break
    beam_info = {}
    if zb is not None:
        ngen = int(zb['cnt_n_generated'])
        n_per_s = float(np.trapezoid(fold.n_per_s_MeV, fold.E_n))     # gun: 0.1–45 MeV
        per_s = n_per_s / ngen                                       # per generated neutron
        wc = lambda k: float(zb[f'cnt_w_{k}']) if f'cnt_w_{k}' in zb else float(zb[f'cnt_{k}'])  # noqa: E731
        beam_info = dict(sample=beam_name, n_per_s=n_per_s, ngen=ngen,
                         # forced: each event stands for 1/⟨ΣP⟩ neutrons (its interacting share)
                         s_simulated=ngen / (float(zb['cnt_diag_w_sum']) / ngen if 'cnt_diag_w_sum' in zb else 1.0)
                         / n_per_s,
                         trig2_per_s=wc('trig2') * per_s, leg_any_per_s=wc('leg_any') * per_s,
                         ok2_per_s=wc('n_ok2') * per_s, n_ok2_mc=int(zb['cnt_n_ok2']))
        if len(zb['En']):
            w = zb['w'] if 'w' in zb else np.ones(len(zb['En']))
            t = np.fmin(zb['t_sipm1'], zb['t_sipm2']) if 't_sipm1' in zb else None
            kb = tof_bin(zb['En'], t)
            good = (kb >= 0) & (kb < len(NODES))
            Wb = np.array([F.w_of_en(NODES[i]) if g else 21.0 for i, g in zip(np.clip(kb, 0, 8), good)])
            d = events(zb, hw, Wb)
            d['w'] = w * per_s * DAY
            d['kind'], d['bin'] = 'beam', kb
            beam_info['ok2_any_bin_per_day'] = float(d.w[good].sum())
            beam_info['ok2_vertex_per_day'] = float(d.w[good & d.ok].sum())
            d = d[d.ok & good & (d.Es > esum_frac * Wb)]
            beam_info['ok2_sel_per_day'] = float(d.w.sum())
            beam_info['ok2_sel_mc'] = int(len(d))
            ev.append(d)
        if 'sg_En' in zb and len(zb['sg_En']) and 'sg_t_sipm' in zb:
            acc = accidentals(zb, hw, per_s, esum_frac)
            if len(acc):
                beam_info['acc_sel_per_day'] = float(acc.w.sum())
                ev.append(acc)
    # cosmics: flat in time, shared among the E_n bins by their TOF width within one bunch period
    zc = load(f'L4_cosmic{tag}')
    if zc is not None and len(bins):
        ngen = int(zc['cnt_n_generated'])
        per_day = DAY / (ngen * COSMIC_S_PER_EVENT)
        for _, b in bins.iterrows():
            frac = (tof_s(b.lo) - tof_s(b.hi)) * REP_HZ
            d = events(zc, hw, b.W)
            d['w'] = per_day * frac
            d['kind'], d['bin'] = 'cosmic', int(b.bin)
            d = d[d.ok & (d.Es > esum_frac * b.W)]
            ev.append(d)
    E = pd.concat(ev, ignore_index=True) if ev else pd.DataFrame()
    return bins, E, beam_info


def z2_asimov(s, b, delta=0.0):
    """Σ over bins; delta = uncorrelated relative background-shape uncertainty per bin."""
    s, b = np.asarray(s, float), np.asarray(b, float)
    m = b > 0
    if delta > 0:
        return float(np.sum(s[m] ** 2 / (b[m] + (delta * b[m]) ** 2)))
    return float(np.sum(2 * ((s[m] + b[m]) * np.log1p(s[m] / b[m]) - s[m])))


M_BINS = np.arange(0, 36.01, 0.5)
TH_BINS = np.arange(0, 180.01, 4)


def hists(E, bins_sel):
    """per E_n bin: (s_m, b_m, s_t, b_t) per day at ρ = RHO_REF; everything downstream is linear."""
    out = []
    for k in bins_sel:
        e = E[E.bin == k]
        sig, bkg = e[e.kind == 'X17'], e[e.kind != 'X17']
        out.append((np.histogram(sig.m, M_BINS, weights=sig.w)[0], np.histogram(bkg.m, M_BINS, weights=bkg.w)[0],
                    np.histogram(sig.th, TH_BINS, weights=sig.w)[0], np.histogram(bkg.th, TH_BINS, weights=bkg.w)[0]))
    return out


def z2_table(H, live, days, rho, delta=0.0):
    """Z² per analysis summed over the E_n bins of H (from hists)."""
    sc = rho / RHO_REF * live * days
    res = {}
    S_all, B_all = np.zeros(len(TH_BINS) - 1), np.zeros(len(TH_BINS) - 1)
    zm = zt = 0.0
    for s_m, b_m, s_t, b_t in H:
        zm += z2_asimov(s_m * sc, b_m * live * days, delta)
        zt += z2_asimov(s_t * sc, b_t * live * days, delta)
        S_all += s_t * sc
        B_all += b_t * live * days
    res['m_ee | E_n'] = zm
    res['θ | E_n'] = zt
    res['θ, no TOF'] = z2_asimov(S_all, B_all, delta)
    return res


def rho_3sigma(E, bins_sel, live, days, delta=0.0):
    H = hists(E, bins_sel)
    out = {}
    for key in ('m_ee | E_n', 'θ | E_n', 'θ, no TOF'):
        lo, hi = 1e-6, 10.0
        for _ in range(60):
            mid = np.sqrt(lo * hi)
            z = np.sqrt(z2_table(H, live, days, mid, delta)[key])
            lo, hi = (mid, hi) if z < 3 else (lo, mid)
        out[key] = np.sqrt(lo * hi)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--days', type=float, default=14.0)
    ap.add_argument('--esum-frac', type=float, default=0.5)
    ap.add_argument('--beam', default='auto', choices=('auto', 'N4', 'N3c', 'N3'),
                    help='beam sample: N4 forced (clusters), N3c analog (clusters), N3 analog (whole events)')
    ap.add_argument('--tag', default='', help='suffix for the output directory')
    a = ap.parse_args()
    global BEAM_SAMPLES, OUT
    pick = {'N4': 0, 'N3c': 1, 'N3': 2}
    if a.beam != 'auto':
        BEAM_SAMPLES = (BEAM_SAMPLES[pick[a.beam]],)
    if a.tag:
        OUT = OUT.parent / f'{OUT.name}_{a.tag}'
    OUT.mkdir(parents=True, exist_ok=True)
    allrows, binrows, beamrows = [], [], []
    for hw in HW:
        bins, E, beam = build(hw, a.esum_frac)
        if E.empty:
            print(f'{hw}: no tables in {SEL}')
            continue
        trig = beam.get('trig2_per_s', 0.0)
        live = 1 / (1 + trig * TAU_DAQ)
        beamrows.append(dict(hw=hw, live=live, **beam))
        for _, b in bins.iterrows():
            e = E[E.bin == b.bin]
            binrows.append(dict(hw=hw, **b.to_dict(),
                                **{f'{k}_per_day': float(e[e.kind == k].w.sum())
                                   for k in ('X17', 'IPC', 'beam', 'acc', 'cosmic')},
                                n_beam_mc=int((e.kind == 'beam').sum()), n_acc_mc=int((e.kind == 'acc').sum())))
        for hi_k in range(len(bins)):
            for lo_k in (0,):
                sel = list(range(lo_k, hi_k + 1))
                for delta in (0.0, 0.02):
                    r = rho_3sigma(E, sel, live, a.days, delta)
                    allrows.append(dict(hw=hw, window=f'{EDGES[lo_k]:g}-{EDGES[hi_k + 1]:g}', delta=delta,
                                        days=a.days, live=live, **{f'rho3_{k}': v for k, v in r.items()}))
    reach = pd.DataFrame(allrows)
    pd.DataFrame(binrows).to_csv(OUT / 'bins.csv', index=False, float_format='%.4g')
    pd.DataFrame(beamrows).to_csv(OUT / 'beam.csv', index=False, float_format='%.4g')
    reach.to_csv(OUT / 'reach.csv', index=False, float_format='%.4g')
    pd.set_option('display.width', 200)
    print(pd.DataFrame(beamrows).to_string(index=False))
    print(pd.DataFrame(binrows).to_string(index=False))
    print(reach.to_string(index=False))
    figure(reach)


def figure(reach):
    """ρ(3σ) vs the upper edge of the E_n window (lower edge 0.2 MeV), δ = 0."""
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use()
    r = reach[reach.delta == 0].copy()
    r['E_hi'] = r.window.str.split('-').str[1].astype(float)
    fig, ax = fs.figure()
    for hw, col in (('as built', fs.MUTED), ('big plastics', fs.ACCENT)):
        q = r[r.hw == hw]
        ax.plot(q.E_hi, q['rho3_m_ee | E_n'], 'o-', color=col, lw=1.6, ms=4, label=f'{hw}: m_ee | E_n')
        ax.plot(q.E_hi, q['rho3_θ, no TOF'], 's--', color=col, lw=1.0, ms=3, label=f'{hw}: θ, no TOF')
    ax.axhline(RHO_REF, color=fs.COPPER, lw=1.0)
    ax.text(0.8, RHO_REF * 1.15, 'ATOMKI ⁴He (1.5e-3)', color=fs.COPPER, fontsize=8)
    ax.axvspan(0.2, 2.75, color=fs.BAND_SIGNAL, alpha=0.06, lw=0)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('upper edge of the E_n window [MeV]  (lower edge 0.2 MeV)')
    ax.set_ylabel('X17 / IPC(E1) reached at 3σ')
    ax.legend(frameon=False, fontsize=8)
    days = r.days.iloc[0]
    fs.title(ax, 'NFS reach needs the fast neutrons; below 2.75 MeV it is 15× short',
             f'{days:g} days at 50 µA, ρ constant in E*, beam-induced background not yet constrained')
    fs.save(fig, OUT / 'reach_vs_window', data=r)


if __name__ == '__main__':
    main()
