#!/usr/bin/env python3
"""
he3_target.py -- can the ³He targets of the Birmingham study be built, filled, run legally and emptied again?
(FEASIBILITY_PLAN.md, analytic.)

    PY=~/PycharmProjects/nTof_x17/.venv/bin/python
    $PY he3_target/he3_target.py            # -> he3_target/out/*.csv, out/he3_designs.png

The Birmingham Geant4 study (birmingham/TARGET_GEANT.md) found that at a broad fast-neutron beam the rate is the
number of ³He atoms inside the beam, whatever the pressure. It sized the walls with one thin-wall rule
(docs/anchor_vessel.py: CFRP at 500 MPa, 0.3 mm floor). This script re-sizes every design with rules a pressure
review would accept, and adds what the physics study left out:

  * walls: filament-wound CFRP by netting analysis (closed ends, t = 1.5 P R / σ_allow) on a metal liner, or
    monolithic Be / Al with allowables min(UTS/4, YS/1.5); hemispherical domes; flat-plate ends for comparison;
  * real-gas ³He (second virial coefficient), inventory in the beam and in total, cost;
  * the legal class: PED / UK PER 2016 Table 2 (group 2 gas) from PS·V, with PSSR 2000 applying in service;
  * stored energy (isentropic expansion to 1 atm) as a TNT equivalent;
  * the leak budget (1 % of the inventory per 30 days) against the permeation of an unlined CFRP wall;
  * tritium from ³He(n,p)t: the beam's fast neutrons (ENDF σ_np/σ_nγ over the Birmingham spectrum) and a
    room-return thermal flux that is not yet simulated;
  * days of beam to the ATOMKI strength, interpolated from the Geant4 rows (ESTIMATE for the new designs):
    σ68² = σv² + (k θ₀)² fitted on the balloon, the 30 bar cell and the capsule, and days = K · σ68 / L_beam with K
    from the 30 bar cell. Beam-term changes with the beam area are NOT in it (they are ~10 % of the background for
    the 30 bar cell; the room loads they drive need Geant4).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'out'
for p in (ROOT / 'birmingham', ROOT / 'survey', ROOT / 'ill'):
    sys.path.insert(0, str(p))
import bham_beam as BB            # noqa: E402
import bham_targets as BT         # noqa: E402
import survey_yield as Y          # noqa: E402

# ------------------------------------------------------------------ constants --
R_GAS = 8.314462618               # J/(mol K)
T_K = 293.15
M_HE3 = 3.01603e-3                # kg/mol
L_STP = 22.414                    # L/mol
NA = 6.02214076e23
DAY = 86400.0
B_VIRIAL = 11.8e-6                # m³/mol, ⁴He at 20 °C (³He within a few %; check against NIST/HEPAK)
EUR_PER_L = 2500.0                # bham_targets / he4_bag; purified grades quoted to ~10 k$/L
GAMMA = 5 / 3
TNT_J_PER_G = 4184.0
T_HALF_T = 12.32 * 365.25 * DAY   # s
SIG_TH_NP = 5316e-24              # cm², ³He(n,p) at 25 meV
RUN_D = 50.0                      # the reach convention's 50 days
LEAK_FRAC, LEAK_DAYS = 0.01, 30.0  # the leak budget: 1 % of the inventory per 30 days
X0 = {'He3': 70.7, 'Be': 65.19, 'CFRP': 42.70, 'Al': 24.01, 'Mylar': 39.95}
RHO = {'Be': 1.848, 'CFRP': 1.55, 'Al': 2.699, 'Mylar': 1.40}

# allowable stresses [MPa]
SIG_CFRP = 500.0     # fibre-direction lamina ~1500 MPa (T700, Vf 0.6) / burst factor 3 (industrial COPV practice)
SIG_BE = min(345 / 4, 207 / 1.5)      # Materion I-70-H guaranteed minimums (S-200-FH typical 414/296 is higher)
SIG_AL = min(455 / 4, 350 / 1.5)      # 2219-T851 (the JLab gas-cell alloy); ASME VIII-1 uses UTS/3.5
SIG_AL_PLATE = SIG_AL
T_CFRP_MIN = 0.30                     # mm, manufacturable wound wall (PLAN_GANIL_NFS §4.1)

# Birmingham case (birmingham/geant/bham_common.py): 2.8 MeV × 30 mA, cell 2 m, 5 cm Pb
BEAM_R_MAX = 4.0                      # cm, the Ø8 cm collimator
PB_N_TRANSMISSION = np.exp(-0.20 * 5.0)

# Geant4 anchors: bham reach (combo wall, big plastics) and the analytic trade
REACH = ROOT / 'birmingham' / 'out' / 'geant' / 'combo' / 'reach.csv'


def z_real(p_bar):
    """compressibility of ³He at 20 °C, pressure-explicit virial Z = 1 + B P / (R T)."""
    return 1 + B_VIRIAL * p_bar * 1e5 / (R_GAS * T_K)


def mol_per_L(p_bar):
    return p_bar * 1e5 / (z_real(p_bar) * R_GAS * T_K) * 1e-3


def highland(p_mev, x):
    x = max(x, 1e-9)
    beta = p_mev / np.hypot(p_mev, 0.51099895)
    return np.degrees(13.6 / (beta * p_mev) * np.sqrt(x) * (1 + 0.038 * np.log(x)))


def x_over_x0(walls):
    return sum(RHO[m] * t / 10 / X0[m] for m, t in walls)


# ------------------------------------------------------------------- designs --
@dataclass
class Design:
    key: str
    label: str
    family: str          # anchor | copv | mono-Be | mono-Al | balloon
    p_bar: float
    R_cm: float
    L_cm: float
    liner: tuple | None = None        # (mat, mm) non-structural liner
    walls: list | None = None         # fixed walls (anchors); else sized here
    beam_r_cm: float | None = None
    domes: bool = True                # hemispherical ends (gas volume + dome walls)
    geant: str | None = None          # Geant4 row this design is


def size_walls(d: Design):
    """radial walls [(mat, mm)] and the structural thickness, by family."""
    P = d.p_bar * 0.1                 # MPa
    R = d.R_cm * 10                   # mm
    if d.walls is not None:
        return d.walls, None
    if d.family == 'copv':            # netting: helical ±54.7° carries hoop + axial, t = 1.5 P R / σ
        t = max(T_CFRP_MIN, 1.5 * P * R / SIG_CFRP)
        return [d.liner, ('CFRP', t)] if d.liner else [('CFRP', t)], t
    if d.family == 'mono-Be':
        t = P * R / SIG_BE
        return [('Be', t)], t
    if d.family == 'mono-Al':
        t = P * R / SIG_AL
        return [('Al', t)], t
    raise ValueError(d.family)


def ped_class(ps_bar, v_l):
    """PED 2014/68/EU = UK PER 2016, Table 2 (vessels, group 2 gases). Boundaries above 200 bar·L to be confirmed."""
    if (v_l <= 1.0 and ps_bar <= 1000) or ps_bar * v_l <= 50:
        return 'SEP (Art 4.3)'
    psv = ps_bar * v_l
    for lim, cat in ((200, 'I'), (1000, 'II'), (3000, 'III')):
        if psv <= lim:
            return f'Cat {cat}'
    return 'Cat IV'


def designs():
    B = BT.TARGETS
    out = []
    # the five Geant4 targets, as simulated
    for k in ('cap500', 'c30', 'c10', 'bal5', 'bal10'):
        lab, p, R, L, walls, rb = B[k]
        out.append(Design(k, lab, 'anchor' if not k.startswith('bal') else 'balloon', p, R, L, walls=walls,
                          beam_r_cm=rb, domes=(k == 'cap500'), geant=k))
    al = ('Al', 0.2)
    out += [
        Design('c30-copv', '30 bar R 5, CFRP sized + 0.2 Al liner', 'copv', 30, 5.0, 40, al),
        Design('c30m-copv', '30 bar R 4 (beam-matched), CFRP + 0.2 Al', 'copv', 30, 4.0, 40, al),
        Design('c30-be', '30 bar R 5, monolithic Be', 'mono-Be', 30, 5.0, 40),
        Design('c30-al', '30 bar R 5, monolithic Al 2219', 'mono-Al', 30, 5.0, 40),
        Design('c10m-copv', '10 bar R 4, CFRP floor + 0.2 Al', 'copv', 10, 4.0, 40, al),
        Design('c60m-copv', '60 bar R 4, CFRP + 0.2 Al', 'copv', 60, 4.0, 40, al),
        Design('c100m-copv', '100 bar R 4, CFRP + 0.3 Al', 'copv', 100, 4.0, 40, ('Al', 0.3)),
        Design('t200-r2', '200 bar R 2 × 40 (Ø4 cm beam), CFRP + 0.4 Al', 'copv', 200, 2.0, 40, ('Al', 0.4)),
        Design('t500-r1', '500 bar R 1 × 40 ("long capsule", Ø2 cm beam), CFRP + 0.6 Al', 'copv', 500, 1.0, 40,
               ('Al', 0.6)),
    ]
    return out


# ---------------------------------------------------------- Geant4 calibration --
def calibrate():
    """σ68(θ₀) and the days constant K from the Geant4 rows (big plastics, combo wall)."""
    r = pd.read_csv(REACH)
    r = r[r.det == 'bigP'].set_index('target')
    t, meta = BT.rows()
    t = t.set_index('key')
    # σ68² = σv² + k² θ₀², least squares on the R ≤ 5 cm targets (bal10 has its own 18° vertex spread)
    keys = ['bal5', 'c10', 'c30', 'cap500']
    th2 = t.loc[keys, 'theta0_10MeV_deg'].values ** 2
    s2 = r.loc[keys, 'sigma68_deg'].values ** 2
    A = np.vstack([np.ones_like(th2), th2]).T
    (sv2, k2), *_ = np.linalg.lstsq(A, s2, rcond=None)
    K = {k: r.loc[k, 'days_3sigma_ATOMKI'] * t.loc[k, 'he3_L_in_beam'] / r.loc[k, 'sigma68_deg']
         for k in ('c30', 'c10', 'cap500', 'bal5')}
    cap_per_L = r.loc['c30', 'captures_per_s'] / t.loc['c30', 'he3_L_in_beam']
    return dict(sv=np.sqrt(sv2), k=np.sqrt(k2), K=K['c30'], K_all=K, cap_per_L=cap_per_L, reach=r, trade=t,
                meta=meta)


def sigma_np_over_ng():
    e = np.linspace(0.005, 1.3, 600)
    f = BB.spectrum_on_grid(2.8, e)
    return float(np.trapezoid(f * Y.sig(e, 103), e) / np.trapezoid(f * Y.sig(e, 102), e))


# --------------------------------------------------------------------- table --
def evaluate(cal):
    np_ng = sigma_np_over_ng()
    lam = np.log(2) / T_HALF_T
    rows = []
    for d in designs():
        walls, t_struct = size_walls(d)
        R, L = d.R_cm, d.L_cm
        rb = d.beam_r_cm if d.beam_r_cm is not None else min(R, BEAM_R_MAX)
        v_cyl = np.pi * R ** 2 * L / 1e3                         # L
        v_dome = 4 / 3 * np.pi * R ** 3 / 1e3 if d.domes else 0.0
        v = v_cyl + v_dome
        v_beam = np.pi * min(rb, R) ** 2 * L / 1e3
        if d.geant:                                              # keep the simulated inventory
            tr = cal['trade'].loc[d.geant]
            l_tot, l_beam = tr.he3_L_STP, tr.he3_L_in_beam
        else:
            n = mol_per_L(d.p_bar)
            l_tot, l_beam = n * v * L_STP, n * v_beam * L_STP
        l_real_cap = mol_per_L(500) * v * L_STP if d.key == 'cap500' else np.nan
        rho_gas = l_tot / L_STP * M_HE3 * 1e3 / (v * 1e3)        # g/cm³
        x = x_over_x0(walls) + rho_gas * R / X0['He3']
        th0 = highland(10.0, x)
        if d.geant:
            s68 = cal['reach'].loc[d.geant, 'sigma68_deg']
            days = cal['reach'].loc[d.geant, 'days_3sigma_ATOMKI']
            caps = cal['reach'].loc[d.geant, 'captures_per_s']
        else:
            s68 = np.hypot(cal['sv'], cal['k'] * th0)
            days = cal['K'] * s68 / l_beam
            caps = cal['cap_per_L'] * l_beam
        ps = 1.1 * d.p_bar                                       # design pressure: 10 % over the fill
        e_j = d.p_bar * 1e5 * v * 1e-3 / (GAMMA - 1) * (1 - (1.01325 / d.p_bar) ** ((GAMMA - 1) / GAMMA)) \
            if d.p_bar > 1.5 else 0.0
        # ends: hemispherical dome (half the hoop thickness) vs a flat clamped plate over the full radius
        Pm, Rm = d.p_bar * 0.1, R * 10
        dome = (1.5 * Pm * Rm / SIG_CFRP / 2) if d.family in ('copv', 'anchor') else Pm * Rm / 2 / (
            SIG_BE if d.family == 'mono-Be' else SIG_AL)
        plate = Rm * np.sqrt(0.75 * Pm / SIG_AL_PLATE) if d.p_bar > 1.5 else 0.0
        # leak budget and an unlined CFRP wall's permeation (epoxy He ~5 barrer × resin fraction 0.4, ³He ×1.10)
        budget_mbarL_s = LEAK_FRAC * l_tot * 1013.25 / (LEAK_DAYS * DAY)
        t_cf = dict(walls).get('CFRP', 0.0)
        area = 2 * np.pi * R * L
        perm = (5.0 * 0.4 * 1.10 * 1e-10 * area / (t_cf / 10) * d.p_bar * 75.006 * LEAK_DAYS * DAY / 1e3
                if t_cf > 0 else np.nan)                         # L(STP) per 30 d
        # tritium: fast-neutron (n,p) in the beam, plus a thermal flux of 10⁴ n/cm²/s over the whole cell
        t_fast = caps * np_ng
        n_atoms = l_tot / L_STP * NA
        t_th_1e4 = n_atoms * 1e4 * SIG_TH_NP
        a_fast = t_fast * RUN_D * DAY * lam
        a_th = t_th_1e4 * RUN_D * DAY * lam
        g_he3 = l_tot / L_STP * M_HE3 * 1e3
        rows.append(dict(
            key=d.key, design=d.label, family=d.family, geant4=bool(d.geant), p_bar=d.p_bar, R_cm=R, L_cm=L,
            beam_r_cm=rb, beam_area_cm2=np.pi * rb ** 2,
            walls=' + '.join(f'{m} {t:.2f}' for m, t in walls), wall_x_over_X0_pct=100 * x_over_x0(walls),
            total_x_over_X0_pct=100 * x, theta0_deg=th0, sigma68_deg=s68,
            Z=z_real(d.p_bar), V_L=v, he3_L_STP=l_tot, he3_L_in_beam=l_beam, he3_frac_in_beam=l_beam / l_tot,
            he3_g=g_he3, he3_keur=l_tot * EUR_PER_L / 1e3,
            cap500_real_gas_L=l_real_cap,
            captures_per_s=caps, days_ATOMKI=days, days_source='Geant4' if d.geant else 'ESTIMATE (interp.)',
            PS_bar=ps, PSV_barL=ps * v, ped=ped_class(ps, v) if d.p_bar > 1.5 else 'none (≤ 0.5 bar g)',
            stored_kJ=e_j / 1e3, tnt_g=e_j / TNT_J_PER_G,
            dome_mm=dome if d.p_bar > 1.5 else np.nan, flat_plate_Al_mm=plate,
            leak_budget_mbarL_s=budget_mbarL_s, unlined_cfrp_loss_L_per_30d=perm,
            tritons_per_s_fast=t_fast, tritium_MBq_50d_fast=a_fast / 1e6,
            tritons_per_s_th1e4=t_th_1e4, tritium_MBq_50d_th1e4=a_th / 1e6,
            tritium_Bq_per_g_50d=(a_fast + a_th) / g_he3))
    return pd.DataFrame(rows), np_ng


def fill_method(p):
    if p <= 1.5:
        return 'expand into a vacuum enclosure; recover by cryopump'
    if p <= 150:
        return 'cryopump (charcoal at 4–10 K) then warm: thermal compression; or a diaphragm compressor'
    return 'diaphragm compressor to ≥ 1.2 P (all-metal, ³He/T-rated) or cryo-condensation; recover by cryopump'


def figure(t):
    import figstyle as fs
    fs.use()
    import matplotlib.pyplot as plt
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.2))
    col = {'anchor': '#0072B2', 'balloon': '#999999', 'copv': '#009E73', 'mono-Be': '#E69F00', 'mono-Al': '#D55E00'}
    for _, r in t.iterrows():
        mk = 'o' if r.geant4 else 's'
        sty = dict(ms=7, mec=col[r.family], mew=1.6, mfc='white' if r.geant4 else col[r.family], ls='none')
        a1.loglog(r.he3_L_in_beam, r.days_ATOMKI, mk, **sty)
        a1.annotate(r.key, (r.he3_L_in_beam, r.days_ATOMKI), xytext=(4, 3), textcoords='offset points', fontsize=7.5)
        a2.semilogx(r.p_bar, r.total_x_over_X0_pct, mk, **sty)
        a2.annotate(r.key, (r.p_bar, r.total_x_over_X0_pct), xytext=(4, 3), textcoords='offset points', fontsize=7.5)
    lx = np.geomspace(1, 100, 50)
    a1.plot(lx, 372 / lx, ':', color='0.5', lw=1)
    a1.text(1.3, 372 / 1.3 * 0.55, '≈ 370 L·day / L', fontsize=8, color='0.4')
    a1.set_xlabel('³He inside the beam [L STP]')
    a1.set_ylabel('days of beam to the ATOMKI strength (3σ)')
    fs.title(a1, 'Days follow the ³He in the beam', 'open: Geant4 rows; filled: interpolated (ESTIMATE)')
    a2.set_xlabel('fill pressure [bar]')
    a2.set_ylabel('radial x/X₀ seen by a 90° lepton [%]')
    fs.title(a2, 'Walls sized to a pressure code', 'netting CFRP / Be / Al, allowables in he3_target.py')
    for fam, c in col.items():
        a2.plot([], [], 's', color=c, label=fam)
    a2.legend(fontsize=7.5, frameon=False, loc='upper left')
    fig.tight_layout()
    cols = ['key', 'family', 'geant4', 'p_bar', 'he3_L_in_beam', 'days_ATOMKI', 'total_x_over_X0_pct']
    fs.save(fig, OUT / 'he3_designs.png', data=t[cols])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cal = calibrate()
    t, np_ng = evaluate(cal)
    t['fill_method'] = t.p_bar.map(fill_method)
    t.to_csv(OUT / 'designs.csv', index=False, float_format='%.4g')
    pd.DataFrame([dict(sigma_v_deg=cal['sv'], k=cal['k'], K_anchor=cal['K'], **{f'K_{k}': v for k, v in cal['K_all'].items()},
                       captures_per_L_beam=cal['cap_per_L'], sigma_np_over_ng=np_ng, sig_cfrp=SIG_CFRP, sig_be=SIG_BE,
                       sig_al=SIG_AL)]).to_csv(OUT / 'calibration.csv', index=False, float_format='%.4g')
    figure(t)
    pd.set_option('display.width', 250)
    print(f"σ68 = √({cal['sv']:.2f}² + ({cal['k']:.2f} θ₀)²);  K = {cal['K']:.1f} (all: "
          + ', '.join(f'{k} {v:.1f}' for k, v in cal['K_all'].items()) + f");  σ_np/σ_nγ = {np_ng:.3g}")
    show = ['key', 'p_bar', 'R_cm', 'beam_r_cm', 'walls', 'total_x_over_X0_pct', 'sigma68_deg', 'he3_L_STP',
            'he3_L_in_beam', 'he3_keur', 'days_ATOMKI', 'PSV_barL', 'ped', 'tnt_g', 'dome_mm', 'flat_plate_Al_mm',
            'leak_budget_mbarL_s', 'unlined_cfrp_loss_L_per_30d', 'tritium_MBq_50d_fast', 'tritium_MBq_50d_th1e4']
    print(t[show].to_string(index=False, float_format=lambda v: f'{v:.3g}'))


if __name__ == '__main__':
    main()
