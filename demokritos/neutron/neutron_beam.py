#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
neutron_beam.py -- can the Demokritos neutron beams drive the n_TOF 3He capsule
to an X17 measurement?  An upper bound, every assumption in the neutrons' favour.

    ~/PycharmProjects/nTof_x17/.venv/bin/python demokritos/neutron/neutron_beam.py

The chain, per uA of beam on the neutron-production target:

  1. the source: neutrons per sr per s toward the capsule, Y0
       * 'lab':  the flux the lab quotes, 1e6 n/cm2/s at the 1.7 cm sample position
                 (Vlastou IAEA; Amanatidis 2024), so Y0 = 1e6 x 1.7^2
       * 'max':  computed from the target itself -- the full Ti-T tritium content
                 x sigma(p,n), or the thick-Li yield, with the forward peaking of
                 the lab frame -- an upper bound on what the target can give
  2. the capsule: the n_TOF 500 bar capsule (gas profile from MX17_Full_Geant
     DetectorConstruction.cc), tip-on to the source, rate = Y0 n sigma_pair G
     with G = integral dV / r^2 over the gas (the flux at every point taken at
     its 0-degree value)
  3. the pair cross section: Viviani et al. PRC 105 014001 Table V
  4. the reach: days to 3 sigma at ATOMKI's strength, scaled from the Demokritos
     p + t Geant4 result (same 4He*, same apparatus, same X17/IPC):
         days = days_ref x IPC_ref / IPC
     This ignores every neutron-induced background, the capsule's thicker walls
     and the E_n spread.  It is the most the neutrons could do.
  5. the production target itself: the same protons on the same tritium make
     4He* directly through 3H(p,gamma).  Compare those pairs with the capsule's.

Outputs: demokritos/out/neutron/*.csv (+ a PNG for each figure).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DEM = HERE.parent
ROOT = DEM.parent
OUT = DEM / 'out' / 'neutron'
sys.path.insert(0, str(DEM))
sys.path.insert(0, str(ROOT / 'lnl'))
sys.path.insert(0, str(ROOT / 'ill'))

import demokritos_rates as DR    # noqa: E402

# --------------------------------------------------------------------------- #
# constants and inputs
# --------------------------------------------------------------------------- #
E_CHARGE = 1.602176634e-19
PPS_UA = 1e-6 / E_CHARGE                       # protons per s per uA
DAY = 86400.0

M_N, M_P, M_T, M_HE3, M_HE4 = 939.5654, 938.2721, 2808.9211, 2808.3913, 3727.3794
M_X = 16.94                                    # ATOMKI 4He
Q_PN = M_P + M_T - M_N - M_HE3                 # -0.7638 MeV

#: 500 bar 3He in the n_TOF capsule: 62.7 mg/cm3 (nTof_x17 run_ipc_background_study.py)
N_HE3 = 62.7e-3 / 3.016 * 6.022e23            # 1.25e22 /cm3
#: gas bore profile (z along the beam, tip first; r), mm -- DetectorConstruction.cc, capsule
CAPS_Z = np.array([-29.5, -28, -26, -24, -22, -20, -15, -5, 5, 15, 20, 22, 24, 26, 28, 30, 32, 34,
                   36, 38, 40, 44, 50.7])
CAPS_R = np.array([0.001, 6, 8, 9.165, 9.798, 10, 10, 10, 10, 10, 10, 9.798, 9.165, 8, 6.299, 4.842,
                   3.66, 2.711, 1.967, 1.41, 1.026, 0.75, 0.75])

#: Viviani et al. PRC 105, 014001, Table V (ub)
VIV = pd.DataFrame({'En_MeV': [0.17, 0.35, 0.70, 1.00, 2.00],
                    'sigma_pair_ub': [0.0431, 0.0616, 0.0893, 0.108, 0.146],
                    'sigma_gamma_ub': [20.2, 29.0, 42.0, 50.8, 67.7]})

#: the lab's quoted maximum flux at the sample (Vlastou et al., IAEA; foils at 1.7 cm, Amanatidis 2024)
PHI_LAB = 1e6
D_LAB_CM = 1.7

#: Demokritos Ti-T: 2.1 mg/cm2 Ti loaded to T/Ti = 1.5 (FACILITY.md section 3)
N_T = 2.1e-3 / 47.867 * 6.022e23 * 1.5        # 3.96e19 /cm2
#: 3H(p,n) total cross section near E_p = 2.8 MeV: 0.5-0.6 b (Brune et al. 1999, nucl-ex/9902010;
#: detailed balance on ENDF 3He(n,p)).  The upper end is used.
SIG_PN_B = 0.6
#: c.m. forward peaking of 3H(p,n) at 0 deg relative to isotropic (generous; Drosg & Otuka evaluation ~1.5-2)
FWD_CM_PN = 2.0
#: 7Li(p,n) thick metallic Li at E_p = 2.5 MeV: ~9e8 n/s/uA (Lee & Zhou NIM B 152 (1999) 1;
#: Liskien & Paulsen).  Rounded up.
S_LI_THICK = 1.0e9
FWD_LI = 3.0                                    # lab forward peaking, generous

#: closest approach of the gas tip to the beam spot: 1 mm backing + water cooling + the 5.5 mm Al nose
TIP_MAX_CM = 1.0

#: benchmarks, 3He pairs per day
NTOF_EAR2 = 22.5 / 0.025                        # PLAN_GANIL_NFS.md 5.3: 22.5 X17/day at 0.025, 0.2-2 MeV
ILL_ABS_PER_S = 1e10                            # ill/README.md: the 50-day-cycle design
PAIRS_PER_ABS_THERMAL = 4.8e-11                 # CLAUDE.md, M1 only

REF_SCENARIO = 'Demokritos Ti-T (2.1 mg/cm2), 900 keV'
#: pairs per gamma for the 8Be lines (17.6-18.2 MeV; M1 resonances and E1 direct), round
ALPHA_8BE = 3.5e-3
DAYS_GOAL = 50.0                                # one ILL-style cycle, as the facility studies quote


# --------------------------------------------------------------------------- #
# kinematics
# --------------------------------------------------------------------------- #
def theta_min_n3he(en):
    """X17 minimum opening angle (deg) for n + 3He at E_n (MeV); the anchor_kinematics formula."""
    en = np.asarray(en, float)
    etot = M_N + en + M_HE3
    pn = np.sqrt((M_N + en) ** 2 - M_N ** 2)
    w = np.sqrt(etot ** 2 - pn ** 2)
    ex = (w ** 2 + M_X ** 2 - M_HE4 ** 2) / (2 * w)
    return 2 * np.degrees(np.arcsin(np.clip(M_X / ex, 0, 1)))


def pn_zero_degree(ep):
    """3H(p,n): E_n at 0 deg (MeV) and the lab/c.m. solid-angle Jacobian there."""
    s = (M_P + ep + M_T) ** 2 - (ep ** 2 + 2 * ep * M_P)
    w = np.sqrt(s)
    pp = np.sqrt(ep ** 2 + 2 * ep * M_P)
    beta = pp / (M_P + ep + M_T)
    g = 1 / np.sqrt(1 - beta ** 2)
    en_cm = (s + M_N ** 2 - M_HE3 ** 2) / (2 * w)
    pn_cm = np.sqrt(en_cm ** 2 - M_N ** 2)
    pn_lab = g * (pn_cm + beta * en_cm)          # forward
    en_lab = np.sqrt(pn_lab ** 2 + M_N ** 2) - M_N
    jac = (pn_lab / pn_cm) ** 2                  # dOmega_cm / dOmega_lab at 0 deg (p_T is invariant)
    return en_lab, jac


def ep_for_en(en_target):
    lo, hi = 1.1, 6.0
    for _ in range(60):
        m = 0.5 * (lo + hi)
        if pn_zero_degree(m)[0] < en_target:
            lo = m
        else:
            hi = m
    return 0.5 * (lo + hi)


# --------------------------------------------------------------------------- #
# the capsule
# --------------------------------------------------------------------------- #
def capsule_g(tip_cm, nz=4000, nr=200):
    """G = integral dV / r^2 (cm) over the gas, source on the axis tip_cm before the gas tip.
    Also returns the gas volume (cm3)."""
    z = np.linspace(CAPS_Z[0], CAPS_Z[-1], nz) / 10.0          # cm
    rmax = np.interp(z * 10, CAPS_Z, CAPS_R) / 10.0
    zz = z - z[0] + tip_cm                                     # distance along the axis from the source
    dz = z[1] - z[0]
    g = vol = 0.0
    for zi, ri in zip(zz, rmax):
        r = np.linspace(0, ri, nr + 1)
        rc = 0.5 * (r[1:] + r[:-1])
        dA = 2 * np.pi * rc * np.diff(r)
        g += float((dA / (zi ** 2 + rc ** 2)).sum()) * dz
        vol += float(dA.sum()) * dz
    return g, vol


def sigma_pair_ub(en):
    """Viviani Table V, log-interpolated; held flat outside 0.17-2 MeV (generous above 2 MeV)."""
    return float(np.exp(np.interp(np.log(en), np.log(VIV.En_MeV), np.log(VIV.sigma_pair_ub))))


# --------------------------------------------------------------------------- #
# the reference: p + t at Demokritos, Geant4
# --------------------------------------------------------------------------- #
def reference():
    y = pd.read_csv(DEM / 'out' / 'yields.csv').set_index('scenario').loc[REF_SCENARIO]
    ipc_day = float(y.Y_ipc_E1) * PPS_UA * DAY
    x17_day = float(y.Y_gamma) * PPS_UA * DAY * 5.1e-6
    r = pd.read_csv(DEM / 'out' / 'geant' / 'reach_scan.csv')
    r = r[r.config == 'cu50']
    days = {hw: float(g.days_fit_theta_y.min()) for hw, g in r.groupby('hw')}
    return dict(ipc_day=ipc_day, x17_day=x17_day, x17_per_ipc=x17_day / ipc_day,
                days_ab=days['as built'], days_bp=days['big plastics'])


# --------------------------------------------------------------------------- #
# the three numbers
# --------------------------------------------------------------------------- #
def sources():
    """Y0 (n/sr/s per uA toward the capsule) and E_n for each source."""
    ep_tpn = ep_for_en(2.0)
    en_tpn, jac = pn_zero_degree(ep_tpn)
    s_tpn = N_T * SIG_PN_B * 1e-24 * PPS_UA
    rows = [
        dict(key='lab_tpn', source='³H(p,n), the lab’s quoted flux', reaction='3H(p,n)3He',
             En_MeV=2.0, Ep_MeV=ep_tpn, S_n_per_s=np.nan, Y0_n_sr_s=PHI_LAB * D_LAB_CM ** 2,
             basis=f'{PHI_LAB:.0e} n/cm2/s at {D_LAB_CM} cm (the lab’s maximum)'),
        dict(key='lab_li', source='⁷Li(p,n), the lab’s quoted flux', reaction='7Li(p,n)7Be',
             En_MeV=0.35, Ep_MeV=np.nan, S_n_per_s=np.nan, Y0_n_sr_s=PHI_LAB * D_LAB_CM ** 2,
             basis=f'{PHI_LAB:.0e} n/cm2/s at {D_LAB_CM} cm (the lab’s maximum)'),
        dict(key='max_tpn', source='³H(p,n), all the target’s tritium', reaction='3H(p,n)3He',
             En_MeV=float(en_tpn), Ep_MeV=ep_tpn, S_n_per_s=s_tpn,
             Y0_n_sr_s=s_tpn / (4 * np.pi) * FWD_CM_PN * float(jac),
             basis=f'N_T {N_T:.2e}/cm2 x {SIG_PN_B} b; 0 deg x{FWD_CM_PN} (c.m.) x{float(jac):.2f} (Jacobian)'),
        dict(key='max_li', source='⁷Li(p,n), thick metallic Li', reaction='7Li(p,n)7Be',
             En_MeV=0.7, Ep_MeV=2.5, S_n_per_s=S_LI_THICK, Y0_n_sr_s=S_LI_THICK / (4 * np.pi) * FWD_LI,
             basis=f'{S_LI_THICK:.0e} n/s/uA at 2.5 MeV, 0 deg x{FWD_LI}; E_n <= 0.79 MeV, sigma at 0.7 MeV'),
    ]
    return pd.DataFrame(rows)


def rates(src, ref):
    g_lab, vol = capsule_g(D_LAB_CM)
    g_max, _ = capsule_g(TIP_MAX_CM)
    rows = []
    for _, s in src.iterrows():
        g = g_lab if s.key.startswith('lab') else g_max
        sp = sigma_pair_ub(s.En_MeV)
        ipc = s.Y0_n_sr_s * N_HE3 * sp * 1e-30 * g * DAY             # pairs/day per uA
        ratio = ref['ipc_day'] / ipc
        rows.append(dict(key=s.key, source=s.source, En_MeV=s.En_MeV, Y0_n_sr_s=s.Y0_n_sr_s,
                         tip_cm=D_LAB_CM if s.key.startswith('lab') else TIP_MAX_CM, G_cm=g,
                         sigma_pair_ub=sp, ipc_per_day_1uA=ipc,
                         x17_per_day_1uA=ipc * ref['x17_per_ipc'],
                         days_as_built_1uA=ref['days_ab'] * ratio, days_big_plastics_1uA=ref['days_bp'] * ratio,
                         uA_for_50d_big_plastics=ref['days_bp'] * ratio / DAYS_GOAL,
                         uA_for_50d_as_built=ref['days_ab'] * ratio / DAYS_GOAL,
                         theta_min_deg=float(theta_min_n3he(s.En_MeV))))
    # moderated to thermal: every source neutron absorbed in the 3He (cannot be done; a bound)
    for _, s in src[src.key.str.startswith('max')].iterrows():
        ipc = s.S_n_per_s * PAIRS_PER_ABS_THERMAL * DAY
        ratio = ref['ipc_day'] / ipc
        rows.append(dict(key='therm_' + s.key[4:], source=s.source.split(', ')[0] + ', moderated, every n absorbed',
                         En_MeV=2.5e-8, Y0_n_sr_s=np.nan, tip_cm=np.nan, G_cm=np.nan, sigma_pair_ub=np.nan,
                         ipc_per_day_1uA=ipc, x17_per_day_1uA=ipc * ref['x17_per_ipc'],
                         days_as_built_1uA=ref['days_ab'] * ratio, days_big_plastics_1uA=ref['days_bp'] * ratio,
                         uA_for_50d_big_plastics=ref['days_bp'] * ratio / DAYS_GOAL,
                         uA_for_50d_as_built=ref['days_ab'] * ratio / DAYS_GOAL,
                         theta_min_deg=float(theta_min_n3he(0.0))))
    return pd.DataFrame(rows), vol


def benchmarks(ref):
    ill = ILL_ABS_PER_S * PAIRS_PER_ABS_THERMAL * DAY
    rows = [dict(key='ntof', label='n_TOF EAR2, 0.2–2 MeV (the 2026 campaign)', ipc_per_day=NTOF_EAR2,
                 basis='PLAN_GANIL_NFS.md 5.3: 22.5 X17/day at X17/IPC = 0.025'),
            dict(key='ill', label='ILL, thermal, 10¹⁰ absorbed n/s (design)', ipc_per_day=ill,
                 basis='4.8e-11 pairs per absorbed n (M1 only)'),
            dict(key='pt', label='Demokritos p + t, 0.9 MeV, 1 µA (the proton route)', ipc_per_day=ref['ipc_day'],
                 basis='demokritos_rates.py yields.csv; Geant4 reach in ESTIMATES.md 6')]
    b = pd.DataFrame(rows)
    b['days_big_plastics'] = ref['days_bp'] * ref['ipc_day'] / b.ipc_per_day
    b['days_as_built'] = ref['days_ab'] * ref['ipc_day'] / b.ipc_per_day
    return b


def swamp(src, rt):
    """3H(p,gamma)4He in the production target vs the capsule's pairs, same beam."""
    s = src.set_index('key').loc['max_tpn']
    ep = float(s.Ep_MeV)
    sg_hahn = float(DR.sigma_gamma_ub(ep * 1e3))               # S-factor fit, extrapolated
    # detailed balance on 4He(gamma,p)3H: sigma(p,g) = sigma(g,p) x 2(2J+1)/((2s_p+1)(2s_t+1)) x k_g^2/k_p^2
    mu = M_P * M_T / (M_P + M_T)
    ecm = ep * M_T / (M_P + M_T)
    eg = DR.e_star(ep * 1e3)
    kp2 = 2 * mu * ecm
    db = {gp: gp * 1e3 * 0.5 * eg ** 2 / kp2 for gp in (0.6, 1.2)}   # ub, sigma(gamma,p) = 0.6-1.2 mb
    alpha = float(DR.alpha_e1(eg))
    rows = []
    for lab, sg in (('S-factor fit, extrapolated', sg_hahn), ('detailed balance, σ(γ,p) = 0.6 mb', db[0.6]),
                    ('detailed balance, σ(γ,p) = 1.2 mb', db[1.2])):
        pairs = N_T * sg * 1e-30 * alpha * PPS_UA * DAY
        rows.append(dict(estimate=lab, Ep_MeV=ep, Estar_MeV=eg, sigma_pg_ub=sg, alpha_E1=alpha,
                         target_pairs_per_day_1uA=pairs))
    d = pd.DataFrame(rows)
    caps = float(rt.set_index('key').loc['max_tpn'].ipc_per_day_1uA)
    d['capsule_pairs_per_day_1uA'] = caps
    d['target_over_capsule'] = d.target_pairs_per_day_1uA / caps
    # the 4pi shell that cannot be built: every source neutron through L cm of 500 bar 3He
    shell = []
    for L in (1, 5, 10):
        p = float(s.S_n_per_s) * N_HE3 * L * sigma_pair_ub(float(s.En_MeV)) * 1e-30 * DAY
        shell.append(dict(L_cm=L, he3_grams=4 / 3 * np.pi * ((2 + L) ** 3 - 2 ** 3) * 62.7e-3,
                          shell_pairs_per_day_1uA=p,
                          target_over_shell=float(d.target_pairs_per_day_1uA.min()) / p))
    return d, pd.DataFrame(shell)


def li_target_pairs():
    """7Li(p,gamma)8Be pairs per day per uA in a thick Li target at 2.5 MeV (LNL cross sections;
    the direct-capture remainder is held flat above the last Zahnow point)."""
    import lnl_rates as LR
    xs, stp = LR.CrossSection(), LR.Stopping()
    r = LR.thin_yield(xs, stp, 'Li metal', 2500.0, 1e6, step_kev=1.0)
    r['gamma_per_s_1uA'] = (r['Y_g0'] + r['Y_g1']) * PPS_UA
    r['alpha_pair'] = ALPHA_8BE
    r['pairs_per_day_1uA'] = r['gamma_per_s_1uA'] * ALPHA_8BE * DAY
    return r


def days_vs_current(rt, b, ref):
    cur = np.logspace(-1, 2, 61)
    rows = []
    for _, r in rt.iterrows():
        for hw, d1 in (('as built', r.days_as_built_1uA), ('big plastics', r.days_big_plastics_1uA)):
            for i in cur:
                rows.append(dict(key=r.key, source=r.source, hw=hw, I_uA=i, days=d1 / i))
    return pd.DataFrame(rows)


def theta_curve():
    en = np.r_[0, np.logspace(-2, np.log10(20), 120)]
    return pd.DataFrame({'En_MeV': en, 'theta_min_deg': theta_min_n3he(en)})


# --------------------------------------------------------------------------- #
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ref = reference()
    src = sources()
    rt, vol = rates(src, ref)
    b = benchmarks(ref)
    sw, shell = swamp(src, rt)
    dv = days_vs_current(rt, b, ref)
    th = theta_curve()
    try:
        li = pd.DataFrame([li_target_pairs()])
        caps = float(rt.set_index('key').loc['max_li'].ipc_per_day_1uA)
        li['capsule_pairs_per_day_1uA'] = caps
        li['target_over_capsule'] = li.pairs_per_day_1uA / caps
    except Exception as e:                                       # noqa: BLE001
        print('  Li thick-target yield skipped:', e)
        li = pd.DataFrame()
    pd.DataFrame([ref]).to_csv(OUT / 'reference.csv', index=False)
    src.to_csv(OUT / 'sources.csv', index=False)
    rt.to_csv(OUT / 'rates.csv', index=False)
    b.to_csv(OUT / 'benchmarks.csv', index=False)
    sw.to_csv(OUT / 'swamp.csv', index=False)
    shell.to_csv(OUT / 'shell.csv', index=False)
    dv.to_csv(OUT / 'days_vs_current.csv', index=False)
    th.to_csv(OUT / 'theta_min.csv', index=False)
    if len(li):
        li.to_csv(OUT / 'li_target.csv', index=False)
    pd.set_option('display.width', 250)
    pd.set_option('display.max_columns', 30)
    f = lambda v: f'{v:.3g}'                                     # noqa: E731
    print(f'capsule gas volume {vol:.1f} cm3 = {vol * 62.7e-3:.2f} g 3He; '
          f'G(tip {D_LAB_CM} cm) = {capsule_g(D_LAB_CM)[0]:.2f} cm, G(tip {TIP_MAX_CM} cm) = {capsule_g(TIP_MAX_CM)[0]:.2f} cm')
    print('reference', {k: f(v) for k, v in ref.items()})
    print('\n== sources ==\n', src.drop(columns='basis').to_string(index=False, float_format=f))
    print('\n== rates (per uA) ==\n', rt.drop(columns='source').to_string(index=False, float_format=f))
    print('\n== benchmarks ==\n', b.drop(columns='basis').to_string(index=False, float_format=f))
    print('\n== production target vs capsule (3H(p,n) at max) ==\n', sw.to_string(index=False, float_format=f))
    print('\n== 4pi shell bound ==\n', shell.to_string(index=False, float_format=f))
    if len(li):
        print('\n== thick Li target, 7Li(p,gamma) ==\n', li.to_string(index=False, float_format=f))
    return 0


if __name__ == '__main__':
    sys.exit(main())
