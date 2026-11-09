#!/usr/bin/env python3
"""
bnct_accel_beam.py -- accelerator BNCT machines as X17 sources (bnct_accel/FACILITY.md, FEASIBILITY.md):
the bare ⁷Li(p,n) target (Birmingham class) and the moderated epithermal port, through the shared Geant4 engine.

    python bnct_accel/bnct_accel_beam.py               # beam model + reach -> bnct_accel/out/bnct_*.{csv,png}
    python bnct_accel/bnct_accel_beam.py --check       # only the reproduction of the published Birmingham row

Bare target.  Thick Li: birmingham/bham_beam.py (slowing-down MC, 3e13 n/s at 30 mA, 2.6 MeV).  Thin Li, near threshold:
franz/franz_beam.py.  γ as there: 478 keV, and 14.6-18.2 MeV ⁸Be lines at 1e-7/p for a thick target (ESTIMATE).

Moderated port (ESTIMATE: no BNCT port has a published full spectrum we could use).  1/E from 0.5 eV to 10 keV normalised
to the quoted epithermal flux, plus a fast tail 10 keV to E_max whose size is fixed by the published fast-neutron dose
per epithermal neutron D_f/Φ_epi (IAEA 2e-13, the C-BENS class limit 7e-13 Gy cm²) with a tissue kerma table; γ from
D_γ/Φ_epi = 2e-13 Gy cm² as H-capture 2.2 MeV + 7.7 MeV (Al/Fe capture) lines, and for Li machines the ⁸Be lines through
the moderator.  Thermal neutrons (< 0.5 eV, a few %) are left out.

Sub-keV handling.  N5 starts at 1 keV.  Three things are done about the 0.5 eV - 1 keV part (about 3/4 of the 1/E flux):
  signal/IPC  analytic: survey_yield.captures_per_neutron integrated from 0.5 eV (below 1 keV the 30 bar cell absorbs nearly
              everything), added to the lowest analysis bin, times SUB_ACC, because those vertices pile up at the upstream
              end of the cell (attenuation length 1.6 cm at 1 eV, 16 cm at 100 eV) and the arms see them worse (ESTIMATE);
  background  the same number of neutrons is placed in N5's 1-3 keV bins, ×1 (nominal) or ×10 (pessimistic), because the
              per-neutron singles there are dominated by the same capture γ chain; not a calculation of the sub-keV response;
  rate        they count in the n/s through the spot.
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
for p in ('birmingham', 'franz', 'survey', 'survey/soft_sim', 'ill'):
    sys.path.insert(0, str(ROOT / p))
import bham_beam as BB                                        # noqa: E402
import franz_beam as FB                                       # noqa: E402
import soft_reach as SR                                       # noqa: E402
import survey_yield as Y                                      # noqa: E402

SF, R = SR.SF, SR.R
AREA = 50.0                                                   # cm², the Ø8 cm spot of the Geant4 gun
A_CAPS = np.pi                                                # cm², the n_TOF capsule face
CAPS = 'n_TOF capsule 500 bar × 8 cm'
REF_CELL = Y.REF_CELL
ROOM_FACTOR = 5.5 / 3.3                                       # Birmingham, engine → full-room Geant4 (27 Oct): ESTIMATE when carried over
SUB_ACC = 0.5                                                 # acceptance of sub-keV vertices relative to the mid-cell tables (ESTIMATE)
E_SUB = np.geomspace(0.5e-6, 1e-3, 1500)
MU_PB = SR.MU_PB
HI = [(17.64, 0.6 / 3), (18.15, 0.4 / 3), (14.64, 1.2 / 3), (15.15, 0.8 / 3)]
P_MA = 1e-3 / BB.E_CHARGE
# tissue kerma coefficient [Gy cm²] vs E_n [MeV]: ICRU-44-like soft tissue, rounded (ESTIMATE; only the ratio matters)
KERMA = np.array([[1e-3, 3e-13], [1e-2, 1.2e-12], [3e-2, 2.9e-12], [0.1, 7e-12], [0.3, 1.5e-11], [1.0, 3.3e-11],
                  [3.0, 5e-11], [10.0, 7e-11], [20.0, 7.5e-11]])
G_KERMA = {2.2: 9.3e-12, 7.7: 2.1e-11}                       # Gy cm² per photon, E·μen/ρ (NIST, tissue; rounded)
BSA_G15_T = 0.1                                              # ⁸Be 15-18 MeV γ transmission through moderator + Pb (ESTIMATE)


# --------------------------------------------------------------------------- #
# Bare target machines: (key, what, E_p, mA, kind, status/evidence)
BARE = [
    ('bham_28_30', 'Birmingham HF-ADNeF (reference)', 2.8, 30.0, 'thick', 'operating; the reference'),
    ('nubeam_26_30', 'nuBeam class (Helsinki, Shonan), 2.6 MeV / 30 mA', 2.6, 30.0, 'thick', 'operating clinical; target inside the BSA'),
    ('nagoya_28_15', 'Nagoya NUANS, 2.8 MeV / 15 mA design', 2.8, 15.0, 'thick', 'design current'),
    ('nagoya_28_11', 'Nagoya NUANS, 2.8 MeV / 11 mA reached (2016)', 2.8, 11.0, 'thick', 'last published current'),
    ('cics_25_20', 'CICS-1 / NCC class, 2.5 MeV / 20 mA', 2.5, 20.0, 'thick', 'clinical; current quoted 12-20 mA'),
    ('cics_25_12', 'CICS-1 / NCC class, 2.5 MeV / 12 mA', 2.5, 12.0, 'thick', 'clinical; low quoted value'),
    ('alpha_25_10', 'Alphabeam class (Xiamen, CNAO), 2.5 MeV / 10 mA (ESTIMATE, ask)', 2.5, 10.0, 'thick', 'spec not public'),
    ('vita_23_10', 'BINP VITA, 2.3 MeV / 10 mA, thick Li', 2.3, 10.0, 'thick', 'bare target exists (position B)'),
    ('vita_20_10', 'BINP VITA, 2.0 MeV / 10 mA, thin Li (near threshold)', 2.0, 10.0, 'thin', 'energy tunable 0.3-2.3 MeV'),
    ('vita_22_10', 'BINP VITA, 2.2 MeV / 10 mA, thin Li', 2.2, 10.0, 'thin', 'energy tunable 0.3-2.3 MeV'),
]
BARE_D = {'thick': (1.0, 2.0), 'thin': (0.5, 1.0)}
BARE_PB = (0.0, 5.0)

# Moderated shapes: key, (D_f/Φ Gy cm², E_max MeV, ⁸Be lines?, sub-keV bkg factor, label)
# (…, tail power index: dN/dE ∝ E^-idx above 10 keV; acceptance of the sub-keV vertices)
MOD = {
    'li_iaea':   (2e-13, 0.9, True, 1.0, 'Li port, D_f/Φ = 2e-13 (IAEA)', 1.0, SUB_ACC),
    'li_7':      (7e-13, 0.9, True, 1.0, 'Li port, D_f/Φ = 7e-13', 1.0, SUB_ACC),
    'li_7_soft': (7e-13, 0.9, True, 1.0, 'Li port, 7e-13, steep tail E^-2.5', 2.5, SUB_ACC),
    'li_iaea_soft': (2e-13, 0.9, True, 1.0, 'Li port, 2e-13, steep tail E^-2.5', 2.5, SUB_ACC),
    'li_nofast': (0.0, 0.9, True, 1.0, 'Li port, no fast tail at all (epithermal only)', 1.0, SUB_ACC),
    'li_7_acc1': (7e-13, 0.9, True, 1.0, 'Li port, 7e-13, sub-keV acceptance = 1', 1.0, 1.0),
    'li_7_sub10': (7e-13, 0.9, True, 10.0, 'Li port, 7e-13, sub-keV bkg ×10', 1.0, SUB_ACC),
    'be_7':      (7e-13, 10.0, False, 1.0, 'Be port, D_f/Φ = 7e-13, tail to 10 MeV', 1.0, SUB_ACC),
}
# Φ_epi at the port [n/cm²/s] (source in FACILITY.md); g = flux at the cell / at the port
FLUX = {'iaea1e9': 1.0e9, 'kansai14e8': 1.4e9}
GEOM = {'port': 1.0, '40cm': 0.4}                             # 0.4: ESTIMATE, a 12-20 cm port diverging over 40 cm
LI_MA = 15.0                                                  # mA driving a Li port, for the ⁸Be lines (ESTIMATE, ~1e9/cm²/s)


def f_epi():
    """(normalised ≥ 1 keV pdf on SR.E_GRID 1 keV - 10 keV part of 1/E, the fraction of Φ_epi above 1 keV)."""
    e = SR.E_GRID
    lo, hi = 0.5e-6, 1e-2
    f = np.where(e < hi, 1 / e, 0.0)
    frac = np.log(hi / 1e-3) / np.log(hi / lo)
    return f / np.trapezoid(f, e), frac


def f_fast(emax, idx=1.0):
    e = SR.E_GRID
    f = np.where((e >= 1e-2) & (e < emax), e ** -idx, 0.0)
    return f / np.trapezoid(f, e)


def fast_fraction(df_phi, emax, idx=1.0):
    """fast neutrons per epithermal neutron so that their kerma gives D_f/Φ_epi."""
    e = SR.E_GRID
    f = f_fast(emax, idx)
    kav = np.trapezoid(f * np.exp(np.interp(np.log(e), np.log(KERMA[:, 0]), np.log(KERMA[:, 1]))), e)
    return df_phi / kav


def mod_source(key, shape, cell='cell'):
    """Soft source per 1 n/cm²/s epithermal at the cell (Φ_epi = 1), and its captures function."""
    df, emax, li, subf, lab, idx, sacc = MOD[shape]
    fe, f_ge = f_epi()
    r_fast = fast_fraction(df, emax, idx)
    ff = f_fast(emax, idx)
    a = AREA if cell == 'cell' else A_CAPS
    N_ge_epi = a * f_ge                                        # 1-10 keV part
    N_fast = a * r_fast
    N_sub = a * (1 - f_ge)
    N_ge = N_ge_epi + N_fast
    fge = (N_ge_epi * fe + N_fast * ff) / N_ge
    e = SR.E_GRID
    pile = np.where(e < 3e-3, 1 / e, 0.0)
    pile = pile / np.trapezoid(pile, e)
    n_tot = N_ge + N_sub * subf
    fn = (N_ge * fge + N_sub * subf * pile) / n_tot
    # γ per epithermal n: 70 % 2.2 MeV, 30 % 7.7 MeV
    kg = 0.7 * G_KERMA[2.2] + 0.3 * G_KERMA[7.7]
    r_g = 2e-13 / kg
    parts = [(SR._lines([(2.2, 0.7), (7.7, 0.3)]), r_g * a)]
    if li:                                                      # per Φ=1e9: LI_MA mA, spot; scaled in cap_scale
        parts.append((SR._lines(HI), BB.GAMMA_PER_P * LI_MA * P_MA / (4 * np.pi * 1e4) * BSA_G15_T * a / 1e9))
    fg, g = SR._mix(parts)
    s = SR.Soft(key, f'{lab} ({cell})', fn, n_tot, fg, g, 'bnct', note=f'r_fast {r_fast:.3g}')
    cn = Y.CELLS[REF_CELL if cell == 'cell' else CAPS]
    cname = REF_CELL if cell == 'cell' else CAPS
    return s, dict(fge=fge, N_ge=N_ge, N_sub=N_sub, cell=cname, r_fast=r_fast, subf=subf, sub_acc=sacc), cn


def mod_captures(info, sub_acc=SUB_ACC):
    """capture rate per analysis bin (at Φ_epi = 1)."""
    e = SR.E_GRID
    cpn = Y.captures_per_neutron(e, info['cell'])
    edges = np.array([0.0] + R.EDGES[1:-1] + [99.0])
    f = info['fge'] * info['N_ge'] * cpn
    cap = np.array([np.trapezoid(f[(e >= edges[k]) & (e < edges[k + 1])], e[(e >= edges[k]) & (e < edges[k + 1])]) for k in range(SR.NB)])
    fs = 1 / E_SUB / np.trapezoid(1 / E_SUB, E_SUB)
    csub = np.trapezoid(fs * Y.captures_per_neutron(E_SUB, info['cell']), E_SUB)
    cap_sub = info['N_sub'] * csub * sub_acc
    cap[0] += cap_sub
    return cap, cap_sub


def bare_source(ep, kind, pb, mA_ref=1.0):
    if kind == 'thick':
        b, _ = BB.beam(ep, mA_ref * 1e-3, 1.0)
        fn = BB.spectrum_on_grid(ep, SR.E_GRID)
        n = b['n_cell'] * np.exp(-MU_PB['n'] * pb)
        om = 50.0 / 1e4 / (4 * np.pi)
        p_s = mA_ref * P_MA
        g478 = (6e-5 * p_s + 6e11 * 0.104 * mA_ref / 30.0) * om * np.exp(-MU_PB['g478'] * pb)
        g15 = BB.GAMMA_PER_P * p_s * om * np.exp(-MU_PB['g15'] * pb)
    else:
        b = FB.beam(ep, mA_ref, 1.0, False, pb)
        fn = FB.spectrum_on_grid(ep, SR.E_GRID)
        n, g478, g15 = b['n_cell'], b['g478_cell'], b['g15_cell']
    fg, g = SR._mix([(SR._lines([(0.478, 1.0)]), g478), (SR._lines(HI), g15)])
    return SR.Soft(f'bare_{kind}_{ep * 1000:.0f}_pb{pb:.0f}', f'{kind} Li E_p {ep}', fn, n, fg, g, 'bnct')


# --------------------------------------------------------------------------- #
def scan(src, C, M, cap, k, days, soft):
    best = None
    for s in np.geomspace(1e-3, 1.0, 31):
        st = SR.at_throttle(src, C, M, cap, s * k)
        r = SR.rho3(M, st, days, soft)
        if best is None or r < best[0]:
            best = (r, s, st)
    r, s, st = best
    C0 = dict(C, acc_th=C['acc_th'] * 0, corr_th=C['corr_th'] * 0, ok_arm=C['ok_arm'] * 0, leg_arm=C['leg_arm'] * 0, corr_trig=0.0)
    st0 = SR.at_throttle(src, C0, M, cap, k)
    fl = SR.rho3(M, st0, days, soft)
    return r, s, st, fl


def limit_of(st, r, fl, s):
    w = {k: float(v.sum()) for k, v in st['B'].items()}
    tot = sum(w.values()) or 1.0
    if s < 0.95:
        return 'DREAM/accidentals (throttled)' if st['live'] < 0.7 or w['acc'] > 0.3 * tot else 'correlated beam (throttled)'
    if st['live'] < 0.6:
        return 'DREAM live time'
    if w['corr'] > 0.3 * tot:
        return 'correlated beam'
    if w['acc'] > 0.3 * tot:
        return 'accidentals'
    if r > 1.3 * fl:
        return 'beam background (legs/singles)'
    return 'statistics (IPC + cosmics)' if w['cosmic'] < 2 * w['IPC'] else 'statistics (cosmics dominate)'


def check():
    """rebuild Birmingham rows from soft_reach.sources() and compare with the published soft_reach.csv."""
    pub = pd.read_csv(ROOT / 'survey/soft_sim/out/soft_reach.csv')
    srcs = {s.key: s for s in SR.sources()}
    rows = []
    for key in ('bham_26_2m_pb5', 'bham_28_2m_pb5'):
        for hw in ('big plastics', 'as built'):
            M, runs = SF.nfs_model(hw), SR.load_runs(hw)
            src = srcs[key]
            C = SR.components(src, runs, hw, M)
            cap = SR.captures(src)
            r, s, st, fl = scan(src, C, M, cap, 1.0, 50.0, True)
            p = pub[(pub.key == key) & (pub.hw == hw) & (pub.days == 50) & (pub.signal == 'E* ≤ 22 MeV')].iloc[0]
            rows.append(dict(key=key, hw=hw, rho3_here=r, rho3_published=p.rho3, ratio=r / p.rho3, floor_here=fl, floor_published=p.rho3_floor))
            print(rows[-1], flush=True)
    t = pd.DataFrame(rows)
    t.to_csv(OUT / 'bnct_repro_check.csv', index=False, float_format='%.4g')
    return t


def reach(days=(14.0, 50.0)):
    rows, comps = [], []
    for hw in ('big plastics', 'as built'):
        M, runs = SF.nfs_model(hw), SR.load_runs(hw)
        # --- bare
        cache = {}
        for name, what, ep, mA, kind, stat in BARE:
            for pb in BARE_PB:
                ck = (ep, kind, pb)
                if ck not in cache:
                    src = bare_source(ep, kind, pb)
                    C = SR.components(src, runs, hw, M)
                    cache[ck] = (src, C, SR.captures(src))
                src, C, cap = cache[ck]
                for d in BARE_D[kind]:
                    k = mA * (1.0 / d) ** 2
                    key = f'{name}_{d:g}m_pb{pb:.0f}'
                    for dd in days:
                        for soft in (True, False):
                            r, s, st, fl = scan(src, C, M, cap, k, dd, soft)
                            rows.append(dict(key=key, mode='bare', machine=what, ep=ep, mA=mA, target=kind, dist_m=d, g=np.nan, pb_cm=pb,
                                             cell='30 bar', hw=hw, days=dd, signal='E* ≤ 22 MeV' if soft else 'all E*', rho3=r, rho3_floor=fl,
                                             vs_ATOMKI=r / R.RHO_REF, throttle=s, live=st['live'], occ=st['occ'], limit=limit_of(st, r, fl, s),
                                             n_cell=src.n_cell * k, cap_per_s=float(cap.sum() * k), rho3_room=r * ROOM_FACTOR,
                                             days_to_atomki=50 * (r / R.RHO_REF) ** 2 if dd == 50 else np.nan, **SR.window_counts(st, M, soft)))
        print(hw, 'bare done', flush=True)
        # --- moderated
        for shape in MOD:
            for cell in ('cell', 'capsule'):
                if cell == 'capsule' and shape != 'li_7':
                    continue
                src, info, _ = mod_source(f'mod_{shape}_{cell}', shape, cell)
                # reference Φ = 1e9 so the Geant4 selection has sane numbers; k is relative to that
                ref = 1e9
                src.n_cell *= ref
                src.g_cell *= ref
                C = SR.components(src, runs, hw, M)
                cap1, csub = mod_captures(info, info['sub_acc'])
                cap = cap1 * ref
                comps.append(dict(shape=shape, cell=cell, hw=hw, n_cell_ref=src.n_cell, r_fast=info['r_fast'], ok_arm=C['ok_arm'].mean(),
                                  legs_arm=C['leg_arm'].mean(), corr_trig=C['corr_trig'], corr_fact_per_day=C['corr_fact'], corr_mc=C['corr_n_mc'],
                                  acc_mc=C['acc_n_mc'], ok_g_frac=C['ok_g_frac'], cap_tot=float(cap.sum()), cap_sub=csub * ref))
                for fl_name, phi in FLUX.items():
                    for gn, g in GEOM.items():
                        k = phi * g / ref
                        key = f'mod_{shape}_{fl_name}_{gn}_{cell}'
                        for dd in days:
                            for soft in (True, False):
                                r, s, st, fl = scan(src, C, M, cap, k, dd, soft)
                                rows.append(dict(key=key, mode='moderated', machine=MOD[shape][4], ep=np.nan, mA=np.nan, target=shape, dist_m=np.nan, g=g, pb_cm=0.0,
                                                 cell='30 bar' if cell == 'cell' else 'capsule', hw=hw, days=dd, signal='E* ≤ 22 MeV' if soft else 'all E*',
                                                 rho3=r, rho3_floor=fl, vs_ATOMKI=r / R.RHO_REF, throttle=s, live=st['live'], occ=st['occ'],
                                                 limit=limit_of(st, r, fl, s), n_cell=src.n_cell * k, cap_per_s=float(cap.sum() * k),
                                                 rho3_room=r * ROOM_FACTOR, days_to_atomki=50 * (r / R.RHO_REF) ** 2 if dd == 50 else np.nan,
                                                 **SR.window_counts(st, M, soft)))
                print(hw, shape, cell, f'n_cell {src.n_cell:.3g} ok/arm {C["ok_arm"].mean():.3g} legs/arm {C["leg_arm"].mean():.3g} corr {C["corr_fact"]:.3g}/d ({C["corr_n_mc"]} MC) gfrac {C["ok_g_frac"]:.2f} captures {cap.sum():.3g}/s (sub {csub*ref:.3g})', flush=True)
    t = pd.DataFrame(rows)
    t.to_csv(OUT / 'bnct_reach.csv', index=False, float_format='%.4g')
    pd.DataFrame(comps).to_csv(OUT / 'bnct_components.csv', index=False, float_format='%.4g')
    return t


def spectra_table():
    e = np.geomspace(0.5e-6, 2.0, 400)
    fe, f_ge = f_epi()
    rows = []
    for sh, (df, emax, _li, _sf, _l, idx, _a) in MOD.items():
        if sh.endswith(('sub10', 'acc1')):
            continue
        r = fast_fraction(df, emax, idx)
        epi = np.where(e < 1e-2, 1 / e, 0.0) / np.log(1e-2 / 0.5e-6)
        fast = np.where((e >= 1e-2) & (e < emax), e ** -idx, 0.0)
        fast = r * fast / np.trapezoid(fast, e)
        rows += [dict(shape=sh, E_MeV=x, dPhi_dE_per_Phi_epi=v) for x, v in zip(e, epi + fast)]
    t = pd.DataFrame(rows)
    x26 = np.linspace(1e-3, 1.3, 400)
    f26 = BB.spectrum_on_grid(2.6, x26)
    t = pd.concat([t, pd.DataFrame(dict(shape='bare Li 2.6 MeV, 0° (norm. to 1 n)', E_MeV=x26, dPhi_dE_per_Phi_epi=f26))])
    t.to_csv(OUT / 'bnct_spectra.csv', index=False, float_format='%.4g')
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use()
    fig, ax = fs.figure()
    ec = np.geomspace(1e-6, 20, 300)
    ax.loglog(ec, Y.captures_per_neutron(ec, REF_CELL), color=fs.ACCENT, lw=2, label='³He(n,γ) per neutron, 30 bar × 40 cm')
    ax.axvspan(0.5e-6, 1e-3, color=fs.MUTED, alpha=0.15)
    ax.axvline(2.75, color=fs.COPPER, ls=':')
    ax.text(3e-6, 3e-7, 'below N5 (1 keV):\nanalytic capture,\n1-3 keV background proxy', fontsize=8)
    ax.set_xlabel('E_n [MeV]')
    ax.set_ylabel('captures per neutron')
    ax.legend(frameon=False, fontsize=8)
    fs.title(ax, 'A moderated neutron is worth 100× less', 'captures per neutron through the 30 bar cell: 10⁻⁸ below 1 keV, 1.5×10⁻⁶ at 0.5 MeV')
    fs.save(fig, OUT / 'bnct_capture_value', data=pd.DataFrame(dict(E_MeV=ec, captures_per_n=Y.captures_per_neutron(ec, REF_CELL))))
    return t


def reach_figure(t):
    import figstyle as fs
    import matplotlib.pyplot as plt
    q = t[(t.days == 50) & (t.signal == 'E* ≤ 22 MeV') & (t.hw == 'big plastics')].set_index('key')
    rows = [('Birmingham, 2 m + 5 cm Pb (engine)', 'bham_28_30_2m_pb5', 'bare'),
            ('Nagoya 15 mA, 2 m + 5 cm Pb', 'nagoya_28_15_2m_pb5', 'bare'),
            ('Nagoya 11 mA, 2 m + 5 cm Pb', 'nagoya_28_11_2m_pb5', 'bare'),
            ('nuBeam class, 2 m + 5 cm Pb', 'nubeam_26_30_2m_pb5', 'bare'),
            ('CICS 12 mA, 2 m + 5 cm Pb', 'cics_25_12_2m_pb5', 'bare'),
            ('VITA 2.2 MeV thin, 0.5 m', 'vita_22_10_0.5m_pb0', 'bare'),
            ('Li port 1.4e9, 40 cm, D_f 7e-13', 'mod_li_7_kansai14e8_40cm_cell', 'mod'),
            ('Li port 1e9, 40 cm, D_f 7e-13', 'mod_li_7_iaea1e9_40cm_cell', 'mod'),
            ('Be port 1.4e9, 40 cm (NeuCure)', 'mod_be_7_kansai14e8_40cm_cell', 'mod'),
            ('Li port 1e9, 40 cm, IAEA 2e-13', 'mod_li_iaea_iaea1e9_40cm_cell', 'mod'),
            ('Li port, epithermal only (no fast)', 'mod_li_nofast_iaea1e9_40cm_cell', 'mod'),
            ('Li port 1e9, sub-keV bkg ×10', 'mod_li_7_sub10_iaea1e9_40cm_cell', 'mod')]
    d = pd.DataFrame([dict(case=c, key=k, mode=m, rho3=q.loc[k, 'rho3'], days=q.loc[k, 'days_to_atomki']) for c, k, m in rows])
    fs.use()
    fig, ax = plt.subplots(figsize=(9, 4.6))
    y = np.arange(len(d))[::-1]
    ax.barh(y, d.rho3, color=[fs.ACCENT if m == 'bare' else fs.COPPER for m in d['mode']])
    ax.set_yticks(y, d.case, fontsize=8)
    ax.set_xscale('log')
    ax.axvline(1.5e-3, color=fs.MUTED, ls='--')
    ax.text(1.55e-3, y[-1] - 0.45, 'ATOMKI', fontsize=8, color=fs.MUTED)
    ax.set_xlabel('X17/IPC reach at 3σ, 50 d (big plastics; beam-only engine)')
    ax.set_xlim(1e-4, 4e-3)
    fs.fig_title(fig, 'Bare ⁷Li beats the moderated port; only research machines offer a bare target',
                 'purple: unmoderated target (hypothetical at hospitals); copper: moderated port (ESTIMATE tail)')
    fs.save(fig, OUT / 'bnct_reach_fig', data=d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    print('epi fraction above 1 keV:', f_epi()[1])
    for sh in MOD:
        print(sh, 'fast/epi', fast_fraction(MOD[sh][0], MOD[sh][1], MOD[sh][5]))
    spectra_table()
    c = check()
    print(c.to_string(index=False))
    if a.check:
        return
    t = reach()
    reach_figure(t)
    pd.set_option('display.width', 280)
    q = t[(t.days == 50) & (t.hw == 'big plastics') & (t.signal == 'E* ≤ 22 MeV')]
    print(q[['key', 'rho3', 'rho3_floor', 'throttle', 'live', 'occ', 'limit', 'n_cell']].to_string(index=False))


if __name__ == '__main__':
    main()
