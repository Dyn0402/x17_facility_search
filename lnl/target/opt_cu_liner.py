#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
opt_cu_liner.py -- Pierfrancesco's ogive in Al with a Cu liner where the beam stops (TARGET_OPTIONS.md §22,
CU_LINER.md).  Dylan (4 Nov): "a careful study of this new design ... where and how we must put Cu", as the
compromise to send back: his Cu ogive (cheap, no Mo, but every lepton crosses 200 µm Cu, σ68 18.5°) against the
Al + Mo ogive (σ68 10.5°, but a Mo coat inside a deep cone and Mo K x-rays in the Micromegas).

    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/opt_cu_liner.py

Everything here is analytic and ESTIMATE; Geant4 run L12 (MX17_Full_Geant `lnl_culiner`, shapes/lxplus/l12_*.sh)
gives the leptons, the γ backgrounds and the x-rays in the Micromegas.  What this file answers:

  1. where the beam lands on the ogive, for spot σ 1/2/3 mm (share on the tip cap, radius containing 99/99.9 %);
  2. how thick the Cu has to be, point by point: the proton range after the Li along the beam direction, with a
     Li-free (worst) case, straggling and a beam-energy margin -> the thickness *along the beam*, and what that
     is along the wall normal for (a) a uniform coat (plating) and (b) a line-of-sight coat from a source on the
     beam axis (sputtering / evaporation), whose normal thickness falls as cos(incidence);
  3. the Li film on the flank: a uniform film (L11's assumption) against a line-of-sight film (same source
     geometry), which keeps the Li path along the beam constant: the 17.64 MeV share of L11 §10.2 item 4 is a
     property of the coating method, not of the shape;
  4. what reaches bare Al outside the Cu (halo), and the ²⁷Al(p,γ) 10.76 MeV γ it makes, against the ⁸Be γ0;
  5. PIXE: the K x-rays the stop makes (BEA-scaled ESTIMATE; the Geant4 TestEm5 ECPSSR check replaces it when
     present, out/target/options/pixe_testem5.csv), with the depth they start at, and the fraction that leaves
     the shell toward a Micromegas face (self-absorption in the stop, the Al wall, at every exit angle);
  6. heat (the fin of opt_shell_material with the Cu in parallel), the bimetal stress, 1 bar, and hydrogen.

Writes out/target/options/culiner_*.csv.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / 'shapes'))
import opt_sketch as SK            # noqa: E402
import opt_shell_material as SM    # noqa: E402
import target_model as TM          # noqa: E402

OUT = SK.OUT
RNG = np.random.default_rng(20261104)
P_PER_UA = 1e-6 / 1.602176634e-19

# ---- materials -----------------------------------------------------------------------------------------------
RHO = {'Cu': 8.96, 'Al': 2.70, 'Mo': 10.22, 'Ti': 4.51, 'Be': 1.848, 'Li': 0.534}
X0_MM = {'Cu': 14.36, 'Al': 88.97, 'Mo': 9.594, 'Ti': 35.6, 'Be': 352.8}
# mass attenuation μ/ρ [cm²/g] at the K lines (NIST XCOM, read off the tables, ±5–10 %): Ti Kα 4.51, Cu Kα 8.05,
# Cu Kβ 8.91, Mo Kα 17.48, Mo Kβ 19.61 keV.  Cu Kα/Kβ sit just below the Cu K edge (8.98): Cu is semi-transparent
# to its own lines; Ti's line sits below its own edge as well.
MU = {
    #        Ti Kα   Cu Kα   Cu Kβ   Mo Kα   Mo Kβ
    'Al':   (258.,   49.4,   36.8,   5.08,   3.65),
    'Cu':   (690.,   51.8,   39.0,   48.6,   35.5),
    'Mo':   (560.,  157.,   115.,    19.0,   13.8),
    'Ti':   ( 85.,  225.,   165.,    26.0,   18.9),
    'Be':   (  6.0,   1.1,    0.8,    0.20,   0.17),
    'PET':  ( 40.,    6.7,    4.9,    0.82,   0.65),
    'Air':  ( 66.,    9.6,    7.1,    1.05,   0.80),
    'Ar':   (480.,   87.,    66.,     9.6,    7.0),
}
# detector-side calibration per line: Geant4 L11 x-ray library (xray_ogBe200mo8, photons from the film through Mo 8 +
# Be 200, MM hits per arm) / this model with the same inputs (escape(..., mono=...)): 2.77e-3/2.27e-3, 4.63e-3/3.90e-3,
# 8.53e-3/3.33e-3, 8.0e-3/3.1e-3.  The Mo lines are low here because the 9 µm Cu cathode's photoelectrons (and the
# mesh's) also make hits in Geant4.  The Cu ogive (200 µm) agrees: ≲ 2e-6 per arm in both.
CAL = {4.51: 1.0, 8.05: 1.22, 8.91: 1.19, 17.48: 2.56, 19.61: 2.58}
LINES = {'Ti': [(0, 4.51, 1.0)], 'Cu': [(1, 8.05, 0.88), (2, 8.91, 0.12)], 'Mo': [(3, 17.48, 0.84), (4, 19.61, 0.16)]}

# ---- the beam on the ogive -------------------------------------------------------------------------------------
RCE = float(np.sqrt(SK.TIP_RI ** 2 - (SK.Y_CAP_I - SK.TIP_C) ** 2))      # tip-cap edge radius (2.52 mm)


def surface(rho):
    """inner-surface point above radius rho (beam along +y): y, unit inward normal (nr, ny), cos(incidence)."""
    rho = np.asarray(rho, float)
    on_cap = rho <= RCE
    y_cap = SK.TIP_C + np.sqrt(np.maximum(SK.TIP_RI ** 2 - rho ** 2, 0))
    y_fl = SK.YC + np.sqrt(np.maximum(SK.A_IN ** 2 - (rho + SK.RM) ** 2, 0))
    y = np.where(on_cap, y_cap, y_fl)
    n_cap = np.stack([-rho, -(y - SK.TIP_C)]) / SK.TIP_RI
    nf = np.hypot(rho + SK.RM, y - SK.YC)
    n_fl = np.stack([-(rho + SK.RM), -(y - SK.YC)]) / nf
    n = np.where(on_cap, n_cap, n_fl)
    return y, n[0], n[1], np.abs(n[1])


def spot(n, sigma):
    x, z = RNG.normal(0, sigma, n), RNG.normal(0, sigma, n)
    return x, z, np.hypot(x, z)


def landing_table():
    rows = []
    for sig in (1.0, 2.0, 3.0):
        _, _, r = spot(400_000, sig)
        _, _, _, c = surface(r)
        rows.append(dict(sigma_mm=sig, share_cap=float((r <= RCE).mean()), r50=np.quantile(r, .5),
                         r99=np.quantile(r, .99), r999=np.quantile(r, .999), r99999=np.quantile(r, .99999),
                         cos_inc_median=float(np.median(c)), cos_inc_p01=float(np.quantile(c, .01)),
                         share_beyond_8mm=float((r > 8).mean()), share_beyond_6mm=float((r > 6).mean()),
                         share_beyond_4mm=float((r > 4).mean())))
    return pd.DataFrame(rows)


# ---- ranges -----------------------------------------------------------------------------------------------------
_P = pd.read_csv(HERE.parent / 'data' / 'pstar_stopping.csv')


def range_um(mat, e_mev):
    g = _P[_P.material == mat]
    r = np.interp(np.log(e_mev), np.log(g.E_MeV.values), g.csda_g_cm2.values)
    return r / RHO[mat] * 1e4


def S_kev_um(mat, e_mev):
    g = _P[_P.material == mat]
    s = np.exp(np.interp(np.log(e_mev), np.log(g.E_MeV.values), np.log(g.S_tot_MeVcm2_g.values)))
    return s * RHO[mat] * 1e3 / 1e4         # keV/µm


def li_exit(ep_kev, li_ug_along):
    return TM.layered_yield(ep_kev, [TM.film('Li', li_ug_along)])['E_out_keV']


def thickness_table(li_ug=1068.0):
    """Cu (and Mo, Ti) needed along the beam.  Requirement: stop a Li-free beam at E_p + 50 keV (machine setting
    and a spare) with 3 straggling widths (Bohr, ~4 % of the range at 1 MeV in Cu) and 1 µm for roughness and the
    coat's own scatter -> t_beam.  Then the wall-normal thickness for a uniform coat and for a line-of-sight coat
    (t_n = t_beam cos i).  The case with Li present stops ~1.4 µm (Cu) shallower."""
    rows = []
    for ep in (1030.0, 1100.0):
        e_after = li_exit(ep, li_ug)
        for m in ('Cu', 'Mo', 'Ti'):
            r_bare, r_li = range_um(m, (ep + 50) / 1e3), range_um(m, e_after / 1e3)
            t_beam = r_bare * 1.12 + 1.0
            rows.append(dict(Ep_keV=ep, mat=m, E_after_Li_keV=e_after, range_after_Li_um=r_li,
                             range_bare_Ep50_um=r_bare, t_along_beam_um=t_beam,
                             xX0_pct_per_leg_normal=100 * t_beam * 1e-3 / X0_MM[m]))
    return pd.DataFrame(rows)


# ---- deposition profiles: uniform vs line of sight from an on-axis source --------------------------------------
def los_profile(rho, d_src_mm):
    """normal thickness relative to the tip for a small source on the beam axis at y = −d_src (upstream of the inner
    tip): flux ∝ cos(angle between the inward normal and the direction to the source) / distance²."""
    y, nr, ny, _ = surface(rho)
    vx, vy = -rho, -d_src_mm - y                      # surface point → source
    L = np.hypot(vx, vy)
    cosn = np.clip((nr * vx + ny * vy) / L, 0, None)
    y0, _, _, _ = surface(np.array([0.0]))
    L0 = d_src_mm + y0[0]
    return cosn / L ** 2 * L0 ** 2


def profile_table(t_beam_um=12.0, li_ug=1068.0, ep=1100.0):
    """Cu along the beam and Li along the beam on the meridian, uniform coat vs line of sight (source 70 / 150 /
    400 mm from the tip; 70 mm = in the ogive's base, 150 mm = a DN40 tee, 400 mm = far down the pipe)."""
    rho = np.r_[0.0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 7, 8, 10, 12, 15]
    _, _, _, c = surface(rho)
    rows = []
    for r_, c_ in zip(rho, c):
        d = dict(rho_mm=r_, cos_inc=c_, inc_deg=np.degrees(np.arccos(c_)),
                 Cu_normal_uniform=t_beam_um, Cu_beam_uniform=t_beam_um / c_,
                 Li_beam_uniform_ug=li_ug / c_, Eout_uniform=li_exit(ep, li_ug / c_))
        for D in (70, 150, 400):
            f = float(los_profile(np.array([r_]), D)[0])
            d[f'Cu_normal_los{D}'] = t_beam_um * f
            d[f'Cu_beam_los{D}'] = t_beam_um * f / c_
            d[f'Li_beam_los{D}_ug'] = li_ug * f / c_
        d['Eout_los150'] = li_exit(ep, d['Li_beam_los150_ug'])
        rows.append(d)
    return pd.DataFrame(rows)


def li_mix_table(ep_list=(1030.0, 1100.0), li_ug=1068.0):
    """⁸Be γ0 per proton and the 17.64 MeV share for the ogive: uniform film (L11), line-of-sight film, and a mask
    to the cap / to r <= 4 mm, against the flat film.  Weighted over the σ 2 mm spot (vertices beyond the mask make
    nothing)."""
    _, _, r = spot(200_000, 2.0)
    _, _, _, c = surface(r)
    flat = {ep: TM.layered_yield(ep, [TM.film('Li', li_ug)]) for ep in ep_list}
    rows = []
    for ep in ep_list:
        for lab, path, keep in (
                ('flat film (reference)', np.full_like(r, li_ug), np.ones_like(r, bool)),
                ('uniform film, no mask (L11)', li_ug / c, np.ones_like(r, bool)),
                ('uniform film, mask r<=4', li_ug / c, r <= 4),
                ('uniform film, mask to the cap (r<=2.5)', li_ug / c, r <= RCE),
                ('line of sight (150 mm), no mask', li_ug * los_profile(r, 150) / c, np.ones_like(r, bool)),
                ('line of sight (150 mm), mask r<=4', li_ug * los_profile(r, 150) / c, r <= 4)):
            q = np.unique(np.quantile(path[keep], np.linspace(0, 1, 13)))
            if len(q) == 1:
                q = np.r_[q[0] * 0.999, q[0] * 1.001]
            g0 = f17 = 0.0
            for a, b in zip(q[:-1], q[1:]):
                s = keep & (path >= a) & (path <= b)
                if not s.any():
                    continue
                y = TM.layered_yield(ep, [TM.film('Li', float(np.median(path[s])))])
                g0 += s.mean() * y['Y_g0']
                f17 += s.mean() * y['Y_g0'] * y['f17']
            rows.append(dict(Ep_keV=ep, film=lab, share_on_Li=float(keep.mean()), Yg0_rel_flat=g0 / flat[ep]['Y_g0'],
                             f17=f17 / g0, f17_flat=flat[ep]['f17'], Yg0_flat=flat[ep]['Y_g0']))
    return pd.DataFrame(rows)


# ---- Al outside the Cu --------------------------------------------------------------------------------------------
AL992_THICK = 1.14e-9        # 10.76 MeV γ per proton through the 992 keV resonance, thick Al (opt_backing §4)


def halo_table(li_ug=1068.0):
    """γ from protons that land on bare Al (r > R_Cu), Gaussian core plus a flat halo of 10⁻³ / 10⁻² of the beam
    spread out to r = 25 mm (a badly tuned beam), against the ⁸Be γ0."""
    yg0 = TM.layered_yield(1100.0, [TM.film('Li', li_ug)])['Y_g0']
    rows = []
    for R in (4.0, 6.0, 8.0, 10.0, 25.0):
        for halo in (0.0, 1e-3, 1e-2):
            core = np.exp(-R ** 2 / 8.0)
            hal = halo * max(0.0, 1 - (R / 25.0) ** 2)
            f = core * (1 - halo) + hal
            rows.append(dict(R_Cu_mm=R, halo=halo, f_on_Al=f, g10p8_per_p=f * AL992_THICK,
                             ratio_to_8Be_g0=f * AL992_THICK / yg0, g10p8_per_s_uA=f * AL992_THICK * P_PER_UA))
    return pd.DataFrame(rows)


# ---- PIXE ---------------------------------------------------------------------------------------------------------
def pixe_depth(el, e_in_kev, step=2.0):
    """K x-rays per proton (BEA scaling, shapes_backgrounds.pixe_yield) and their depth distribution [µm]."""
    import shapes_backgrounds as SB
    e, x, ys, xs = e_in_kev, 0.0, [], []
    n_g = 6.02214076e23 / {'Cu': 63.55, 'Mo': 95.95, 'Ti': 47.87}[el]
    while e > 50:
        s = S_kev_um(el, e / 1e3)               # keV/µm
        dx = step / s
        dEx = SB.sigma_k(el, e - step / 2) * 1e-24 * n_g * RHO[el] * dx * 1e-4
        ys.append(dEx * SB.OMEGA_K[el])
        xs.append(x + dx / 2)
        x += dx
        e -= step
    return np.array(xs), np.array(ys)


_DEPTH: dict = {}


def _depth(el, e_kev):
    if (el, e_kev) not in _DEPTH:
        _DEPTH[(el, e_kev)] = pixe_depth(el, float(e_kev), step=5.0)
    return _DEPTH[(el, e_kev)]


def pixe_scale(el, e_in_kev=872.0):
    """K x-ray yield correction: Geant4 TestEm5 (thick target, emstandard_opt4, PIXE) / BEA at the energy that enters
    the stop, from out/target/options/pixe_testem5.csv (points with >= 30 counts).  ECPSSR_FormFactor if present,
    else the Geant4 'Empirical' model; 1 (BEA) if neither."""
    f = OUT / 'pixe_testem5.csv'
    if not f.exists():
        return 1.0, 'BEA ESTIMATE ×2–3'
    t = pd.read_csv(f)
    for model in ('ECPSSR_FormFactor', 'Empirical'):
        q = t[(t.el == el) & (t.model == model) & (t.counts >= 30)].sort_values('E_keV')
        if len(q):
            ratio = np.array([y / _depth(el, int(round(e)))[1].sum() for e, y in zip(q.E_keV, q.K_per_p)])
            return float(np.interp(e_in_kev, q.E_keV, ratio)), f'Geant4 {model} (TestEm5)'
    return 1.0, 'BEA ESTIMATE ×2–3'


# ---- x-ray escape toward the Micromegas faces ---------------------------------------------------------------------
ARM_D, ARM_HY, ARM_HT = 204.0, 180.0, 200.0        # MM faces at ±204 mm (x, z), ±180 mm along the beam, ±200 across
MM_GAP, MM_WIN_PET, MM_CATH_CU = 30.0, 0.060, 0.009


def arm_dirs(n):
    """isotropic directions from the target that hit one of the four MM faces; returns u, arm id, path to the face."""
    u = RNG.normal(size=(n, 3))
    u /= np.linalg.norm(u, axis=1, keepdims=True)
    arm = np.full(n, -1)
    L = np.full(n, np.inf)
    for k, (ax, sg) in enumerate(((0, 1), (0, -1), (2, 1), (2, -1))):
        with np.errstate(divide='ignore', invalid='ignore'):
            t = ARM_D / (sg * u[:, ax])
        ok = (t > 0)
        other = 2 - ax
        hit = ok & (np.abs(t * u[:, 1]) <= ARM_HY) & (np.abs(t * u[:, other]) <= ARM_HT) & (t < L)
        arm[hit], L[hit] = k, t[hit]
    m = arm >= 0
    return u[m], arm[m], L[m], m.mean()


def mm_detect(li, cos_face):
    """window (PET 60 µm + Cu 9 µm cathode, at the angle) × absorbed in 30 mm Ar."""
    t = np.exp(-(MU['PET'][li] * 1.39 * MM_WIN_PET * 0.1 + MU['Cu'][li] * RHO['Cu'] * MM_CATH_CU * 0.1) / cos_face)
    a = 1 - np.exp(-MU['Ar'][li] * 1.66e-3 * MM_GAP * 0.1 / cos_face)
    return t * a


def escape(stop, t_stop_um, wall, t_wall_um, R_liner=8.0, profile='uniform', d_src=150.0, ep=1100.0,
           li_ug=1068.0, sigma=2.0, mask=4.0, n_v=4000, n_dir=200_000, mono=None, li_profile="los"):
    """K x-rays per proton that end in one MM drift gap (summed over the four arms), from the stop under the Li.
    Vertices: the σ spot inside the mask (the stop under the bare flank, outside the mask, also makes x-rays:
    those protons enter it at the full E_p).  The photon starts at the production depth z below the Li/stop face,
    goes along u: through (t_stop − z) and the wall if it heads out through the local wall; through z of stop back
    into the cavity, then the far wall (stop where r_exit <= R_liner, then the wall) if it heads inward.  Path
    factors from the CAD solids (opt_sketch.ogive_path: the 200 µm shell, so g = path / 0.2 mm)."""
    sc, src = pixe_scale(stop)
    if mono:                       # Geant4 library mimic: one photon per line from the film (z = 0), no PIXE weight
        sc = 1.0
    x, z_, r = spot(n_v, sigma)
    y, nr, ny, c = surface(r)
    with np.errstate(invalid='ignore', divide='ignore'):
        ex, ez = np.where(r > 0, x / r, 1.0), np.where(r > 0, z_ / r, 0.0)
    P = np.c_[x, y + 0.010 * ny, z_] + 0.0
    N = np.c_[nr * ex, ny, nr * ez]                           # inward normal
    u, arm, L, f_arm = arm_dirs(n_dir)
    cos_face = np.abs(np.where(arm < 2, u[:, 0], u[:, 2]))
    lines = LINES[stop] if not mono else [(j, E, 1.0) for j, E in mono]
    acc = np.zeros(len(lines))
    for i in range(n_v):
        if r[i] > R_liner and not mono:
            continue                                          # lands on bare wall (counted in the halo table)
        path = li_ug / c[i] * (float(los_profile(np.array([r[i]]), d_src)[0]) if li_profile == 'los' else 1.0)
        e_in = li_exit(ep, path) if r[i] <= mask else ep
        zd, yd = _depth(stop, round(e_in))
        if mono:
            zd, yd = np.array([0.0]), np.array([1.0])
        zn = zd * c[i]                                        # production depth along the beam -> along the normal
        tloc = t_stop_um if profile == 'uniform' else t_stop_um * float(los_profile(np.array([r[i]]), d_src)[0])
        if zn.max() > tloc:
            continue                                          # the stop is too thin there (flagged elsewhere)
        p = np.repeat(P[i][None], len(u), 0)
        cn = u @ N[i]                                          # > 0: into the cavity
        g_far = SK.ogive_path(p, u) / 0.200
        si = SK._exit(lambda q: SK._in_ogive(q, SK.A_IN, SK.Y_CAP_I, SK.TIP_RI), p, u)
        q = p + si[:, None] * u
        r_ex = np.hypot(q[:, 0], q[:, 2])
        through_base = q[:, 1] <= SK.Y_BASE + 1e-3
        frac = (r_ex <= R_liner) * (1.0 if profile == 'uniform' else los_profile(r_ex, d_src))
        out_dir = cn <= 0
        g_loc = 1.0 / np.maximum(np.abs(cn), 1e-3)
        for k, (idx, E_line, br) in enumerate(lines if not mono else [(j, E, 1.0) for j, E in mono]):
            mu_s = MU[stop][idx] * RHO[stop] * 1e-4           # /µm
            mu_w = MU[wall][idx] * RHO[wall] * 1e-4
            mu_air = MU['Air'][idx] * 1.205e-3 * 0.1          # /mm
            far = np.where(through_base, 1.0, np.exp(-(mu_s * t_stop_um * frac + mu_w * t_wall_um) * g_far))
            T = np.zeros(len(u))
            for zz, w in zip(zn, yd):
                T += w * np.where(out_dir, np.exp(-(mu_s * (tloc - zz) + mu_w * t_wall_um) * g_loc),
                                  np.exp(-mu_s * zz * g_loc) * far)
            D = mm_detect(idx, cos_face) * np.exp(-mu_air * (L - MM_GAP / cos_face))
            acc[k] += br * np.mean(T * D) * f_arm
    out_by_line = {E: sc * a / n_v * (CAL[E] if not mono else 1.0) for (_, E, _), a in zip(lines, acc)}
    tot = float(sum(out_by_line.values()))
    return tot, out_by_line, src


def xray_table(quick=False):
    """MM hits per arm per µA for the stop options, all with the same Li (line of sight, mask r <= 4 mm; outside it the
    protons enter the stop at the full E_p) and the stop over r <= 8 mm.  The L11 references (Mo 8 over the whole
    inside, Cu 200 shell) are also shown with L11's own Li (uniform, no mask)."""
    nv, nd = (120, 20_000) if quick else (300, 40_000)
    cases = [
        ('Cu 12, Al 300', 'Cu', 12, 'Al', 300, 'uniform', {}),
        ('Cu 12, Al 300, Cu by line of sight', 'Cu', 12, 'Al', 300, 'los', {}),
        ('Cu 12, Al 400', 'Cu', 12, 'Al', 400, 'uniform', {}),
        ('Cu 12, Al 500', 'Cu', 12, 'Al', 500, 'uniform', {}),
        ('Cu 30, Al 300', 'Cu', 30, 'Al', 300, 'uniform', {}),
        ('Cu 50, Al 300', 'Cu', 50, 'Al', 300, 'uniform', {}),
        ('Ti 15, Al 300', 'Ti', 15, 'Al', 300, 'uniform', {}),
        ('Mo 10, Al 300', 'Mo', 10, 'Al', 300, 'uniform', {}),
        ('Mo 10, Be 300', 'Mo', 10, 'Be', 300, 'uniform', {}),
        ('Cu 200 ogive (his)', 'Cu', 200, 'Be', 0.001, 'uniform', dict(R_liner=1e9)),
        ('L11 Al 300 + Mo 8, L11 Li', 'Mo', 8, 'Al', 300, 'uniform', dict(R_liner=1e9, mask=1e9, li_profile='uniform')),
        ('L11 Be 200 + Mo 8, L11 Li', 'Mo', 8, 'Be', 200, 'uniform', dict(R_liner=1e9, mask=1e9, li_profile='uniform')),
    ]
    rows = []
    for lab, s, ts, w, tw, prof, kw in cases:
        kw = {**dict(R_liner=8.0, mask=4.0), **kw}
        tot, byl, src = escape(s, ts, w, tw, profile=prof, n_v=nv, n_dir=nd, **kw)
        sc, _ = pixe_scale(s)
        _, yk = _depth(s, int(round(li_exit(1100.0, 1068.0))))
        rows.append(dict(case=lab, stop=s, t_stop_um=ts, wall=w, t_wall_um=tw, profile=prof,
                         K_per_p_at_872keV=float(sc * yk.sum()), pixe_source=src,
                         mm_hits_per_p_all_arms=tot, mm_hits_per_s_arm_uA=tot * P_PER_UA / 4,
                         occupancy_1p2us_per_uA=1 - np.exp(-tot * P_PER_UA / 4 * 1.2e-6)))
    return pd.DataFrame(rows)


# ---- heat, stress, pressure, hydrogen -----------------------------------------------------------------------------
def thermal_table():
    rows = []
    k_al, k_cu = SM.MAT['Al 6061-T6']['k'], 391.0
    for t_al in (300, 400):
        for t_cu in (0, 12, 30):
            for I in (1.0, 4.0):
                for sig in (1.0, 2.0):
                    kt = k_al * t_al * 1e-6 + k_cu * t_cu * 1e-6      # Cu everywhere: an upper bound on its help
                    s, r, T = SM.tip_heat(kt, 10.0, I, sigma=sig)
                    rows.append(dict(t_Al_um=t_al, t_Cu_um=t_cu, I_uA=I, sigma_mm=sig, dT_tip_K=float(T[0]),
                                     dT_at_r8_K=float(np.interp(8.0, r, T))))
    return pd.DataFrame(rows)


def stress_table():
    """bimetal: the thin Cu on a thick Al shell takes σ ≈ E_Cu Δα ΔT / (1 − ν) (Δα = 23.6 − 17.0); ΔT from the
    coating temperature (plating 50 °C, sputtering 150 °C) to the hottest run point (tip +60 K over 25 °C) and
    to a 150 °C bake.  Electro-deposited Cu: σ_y 150–300 MPa (fine-grained); sputtered 200–400."""
    E, nu, da = 115e3, 0.34, (23.6 - 17.0) * 1e-6
    rows = []
    for proc, T_dep in (('electroplated', 50.0), ('sputtered', 150.0)):
        for state, T in (('room, 20 °C', 20.0), ('beam 4 µA tip, 85 °C', 85.0), ('bake, 150 °C', 150.0),
                         ('LN₂ trap nearby, 0 °C', 0.0)):
            sig = E * da * (T - T_dep) / (1 - nu)
            rows.append(dict(process=proc, T_dep_C=T_dep, state=state, T_C=T, sigma_Cu_MPa=sig,
                             note='tension' if sig > 0 else 'compression'))
    return pd.DataFrame(rows)


def main():
    pd.set_option('display.width', 250)
    pd.set_option('display.max_columns', 30)
    f = lambda v: f'{v:.3g}'                                 # noqa: E731
    outs = {}
    outs['landing'] = landing_table()
    outs['thickness'] = thickness_table()
    outs['profile'] = profile_table()
    outs['li_mix'] = li_mix_table()
    outs['halo'] = halo_table()
    outs['thermal'] = thermal_table()
    outs['stress'] = stress_table()
    outs['xray'] = xray_table(quick='--quick' in sys.argv)
    for k, d in outs.items():
        d.to_csv(OUT / f'culiner_{k}.csv', index=False)
        print(f'\n== {k}')
        print(d.to_string(index=False, float_format=f))


if __name__ == '__main__':
    main()


# ---- yields for the Geant4 reach (shapes_geant.py, L12) -----------------------------------------------------------
_LMIX: dict = {}


def los_yield_mix(ep_kev, fn, li_ug=1068.0, mask=None, d_src=150.0, sigma=2.0, nbins=12, name=None):
    """as opt_sketch.ogive_yield_mix, for a Li film laid down by line of sight from an on-axis source d_src upstream
    of the tip (its path along the beam is ~li_ug everywhere), optionally through a mask (vertices at r > mask make
    nothing: the extensive keys carry the share on Li).  Fractions (f17, f18res, fdc) are Y_g0-weighted."""
    key = (ep_kev, name or id(fn), li_ug, mask, d_src, sigma, nbins)
    if key in _LMIX:
        return dict(_LMIX[key])
    rng = np.random.default_rng(7)
    x, z = rng.normal(0, sigma, 200_000), rng.normal(0, sigma, 200_000)
    r = np.hypot(x, z)
    _, _, _, c = surface(r)
    path = li_ug * los_profile(r, d_src) / c
    keep = np.ones_like(r, bool) if mask is None else r <= mask
    q = np.unique(np.quantile(path[keep], np.linspace(0, 1, nbins + 1)))
    out, g0 = {}, 0.0
    frac = ('f17', 'f18res', 'fdc')
    for a, b in zip(q[:-1], q[1:]):
        s = keep & (path >= a) & (path <= b)
        if not s.any():
            continue
        w = s.mean()
        res = fn(float(np.median(path[s])))
        for k, v in res.items():
            if not isinstance(v, (int, float, np.floating, np.integer)) or not np.isfinite(v):
                continue
            out[k] = out.get(k, 0.0) + w * (res.get('Y_g0', 1.0) * v if k in frac else v)
        g0 += w * res.get('Y_g0', 1.0)
    for k in frac:
        if k in out:
            out[k] = out[k] / g0 if g0 else np.nan
    _LMIX[key] = dict(out)
    return out
