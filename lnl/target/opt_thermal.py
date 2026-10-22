"""
opt_thermal.py — temperatures of the LNL Li target options (TARGET_OPTIONS.md §3).

An axisymmetric (r, z) finite-volume heat solver for a layered disk under a
Gaussian proton beam:

  * layers from the beam side: film (Li, Li₂O), optional interlayer (Ta, Pd, ...),
    backing (Al, Cu, diamond, graphite foil, ...), each with k(T) = k300 (300/T)^n
    and an optional anisotropy (graphite foil: in-plane k_r, through-plane k_z);
  * the beam power is deposited where the protons lose it: the depth profile
    comes from the PSTAR stopping powers (Bragg additivity) through the stack;
    what leaves the back of a thin stack goes to the dump and is not counted;
  * cooling: any mix of
      - a clamp: annulus r ∈ [r_clamp, R] on the back face (and the front face, for
        a two-sided clamp) with a contact conductance h_c to a sink at T_sink;
      - a cooled back: the whole back face r < r_back with h_back to T_sink (a water-
        cooled block, or a micro-channel plate as an effective h);
      - radiation from every exposed face to 293 K;
  * steady state by Picard iteration on k(T) and the linearised radiation.

Checked against the analytic thin-disk result ΔT = P/(2π k t) [ln(R/σ) + ...]
(`check()`), and against `target_model.temp_disk` for the 10 µm Al disk.

    python lnl/target/opt_thermal.py      → out/target/options/thermal_*.csv, figures
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp
import scipy.sparse.linalg as spla

import target_model as TM

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'out' / 'target' / 'options'
SIGMA_SB = 5.670374e-8
T_ENV = 293.15

# --------------------------------------------------------------------------- #
# materials: k300 [W/m/K], exponent n of k ∝ (300/T)^n, anisotropy k_z/k_r,
# emissivity, density [g/cm³], stopping-power stand-in (PSTAR material or
# compound), heat capacity [J/g/K]
# --------------------------------------------------------------------------- #
MAT = {
    # CVD diamond, thermal grade (Element Six TM180/TM200: 1800–2000 at RT; ~1500 at 100 °C)
    'Diamond':   dict(k=1800., n=1.1, az=1.0, eps=0.10, rho=3.515, stp={'C': 1}, cp=0.51),
    'Cu':        dict(k=398., n=0.1, az=1.0, eps=0.05, rho=8.96, stp={'Cu': 1}, cp=0.385),
    'Al':        dict(k=237., n=0.0, az=1.0, eps=0.08, rho=2.70, stp={'Al': 1}, cp=0.90),
    'Ta':        dict(k=57.5, n=0.0, az=1.0, eps=0.15, rho=16.65, stp={'W': 1}, cp=0.14),
    'Mo':        dict(k=138., n=0.2, az=1.0, eps=0.10, rho=10.22, stp={'Mo': 1}, cp=0.25),
    'Pd':        dict(k=72., n=0.0, az=1.0, eps=0.10, rho=12.02, stp={'Ag': 1}, cp=0.24),
    'Ni':        dict(k=90., n=0.3, az=1.0, eps=0.15, rho=8.90, stp={'Cu': 1}, cp=0.44),
    'Si':        dict(k=148., n=1.3, az=1.0, eps=0.60, rho=2.33, stp={'Al': 1}, cp=0.71),
    # flexible / pyrolytic graphite sheet: in-plane 400 (foil) – 1500 (PGS), through-plane ~5
    'Graphite foil': dict(k=400., n=0.5, az=5. / 400., eps=0.85, rho=1.0, stp={'C': 1}, cp=0.71),
    'Glassy C':  dict(k=6.3, n=-0.3, az=1.0, eps=0.85, rho=1.5, stp={'C': 1}, cp=0.71),
    # films
    'Li':        dict(k=85., n=0.0, az=1.0, eps=0.10, rho=0.534, stp={'Li': 1}, cp=3.58),
    # Li₂O: bulk ~7.5 at RT; evaporated films are porous: 2 (ESTIMATE)
    'Li2O':      dict(k=2.0, n=0.0, az=1.0, eps=0.50, rho=2.013, stp={'Li': 2, 'O': 1}, cp=1.9),
}


def S_mat(name, e_mev):
    """MeV cm²/g by Bragg additivity of the PSTAR elements (Ta≈W, Pd≈Ag, Ni≈Cu, Si≈Al)."""
    comp = MAT[name]['stp']
    aw = {'Li': 6.941, 'O': 15.999, 'C': 12.011, 'Al': 26.982, 'Cu': 63.546, 'W': 183.84,
          'Mo': 95.95, 'Ag': 107.87, 'Au': 196.97}
    if len(comp) == 1:
        return float(TM.STP.element(next(iter(comp)), e_mev))
    mt = sum(aw[e] * n for e, n in comp.items())
    return sum(aw[e] * n / mt * float(TM.STP.element(e, e_mev)) for e, n in comp.items())


def depth_profile(ep_kev, layers, dz_um=0.05):
    """Proton energy deposited vs depth: returns (z_edges [m], keV per proton per
    sub-slab) on a fine grid, the energy leaving the back (keV), and the range end."""
    e = float(ep_kev)
    zs, de = [0.0], []
    z = 0.0
    for name, t_um in layers:
        rho = MAT[name]['rho']
        left = t_um
        while left > 1e-9:
            h = min(dz_um, left)
            if e > 1.0:
                s = S_mat(name, e / 1e3)                 # MeV cm²/g
                d = min(e, s * rho * h * 1e-4 * 1e3)     # keV
            else:
                d = 0.0
            e -= d
            z += h
            left -= h
            zs.append(z * 1e-6)
            de.append(d)
            if e <= 1.0 and left > 0:
                # protons stopped: jump to the end of the layer, nothing more deposited
                z += left
                zs.append(z * 1e-6)
                de.append(0.0)
                left = 0
    return np.array(zs), np.array(de), max(e, 0.0)


# --------------------------------------------------------------------------- #
# the solver
# --------------------------------------------------------------------------- #
@dataclass
class Target:
    layers: list                 # [(material, thickness µm), ...] from the beam side
    R_mm: float = 20.0           # disk radius
    r_clamp_mm: float | None = 10.0   # clamp annulus starts here (None = no clamp)
    h_clamp: float = 5e3         # W/m²/K, contact to the sink (dry metal clamp in vacuum ~10³–10⁴)
    clamp_front: bool = False    # two-sided clamp
    r_back_mm: float | None = None    # cooled back face r < r_back (None = no cooled back)
    h_back: float = 2e4          # W/m²/K (turbulent water ~1–3×10⁴; micro-channels 5×10⁴–10⁵)
    T_sink: float = 293.15
    h_int: float | None = None   # W/m²/K between the film and the next layer (None = perfect contact)
    label: str = ''
    nz_per_layer: dict = field(default_factory=dict)


def _grid_r(R, sig):
    a = np.linspace(0, min(4 * sig, 0.9 * R), 60)
    b = np.geomspace(max(a[-1], 1e-6), R, 40)[1:] if R > a[-1] * 1.01 else np.array([])
    return np.unique(np.r_[a, b, R])


def _grid_z(layers):
    edges, mat = [0.0], []
    for name, t_um in layers:
        t = t_um * 1e-6
        n = 3 if t_um < 3 else (8 if t_um < 60 else 16)
        # geometric from the beam side: fine where the protons stop
        if t_um >= 3:
            g = np.geomspace(min(0.5e-6, t / 50), t, n)
            loc = np.unique(np.r_[0, g])
        else:
            loc = np.linspace(0, t, n + 1)
        z0 = edges[-1]
        edges += list(z0 + loc[1:])
        mat += [name] * (len(loc) - 1)
    return np.array(edges), mat


def solve(tg: Target, I_uA: float, ep_kev: float = 1100.0, sig_mm: float = 2.0,
          return_field=False, it_max=600):
    sig = sig_mm * 1e-3
    R = tg.R_mm * 1e-3
    re = _grid_r(R, sig)
    ze, mats = _grid_z(tg.layers)
    nr, nz = len(re) - 1, len(ze) - 1
    rc = 0.5 * (re[1:] + re[:-1])
    zc = 0.5 * (ze[1:] + ze[:-1])
    dr, dz = np.diff(re), np.diff(ze)
    # heat: depth profile × radial Gaussian (the beam is a 2D Gaussian of σ in x and y)
    zf, def_kev, e_out = depth_profile(ep_kev, tg.layers)
    cum = np.r_[0, np.cumsum(def_kev)]
    dep_cell = np.diff(np.interp(ze, zf, cum))            # keV per proton per z cell
    P_tot = I_uA * dep_cell.sum() / 1e3                   # W (µA × MeV)
    frac_r = np.exp(-re[:-1] ** 2 / (2 * sig ** 2)) - np.exp(-re[1:] ** 2 / (2 * sig ** 2))
    frac_r = frac_r / (1 - np.exp(-R ** 2 / (2 * sig ** 2)))   # the beam is all on the disk
    Q = np.outer(frac_r, dep_cell) * I_uA / 1e3           # W per cell [nr, nz]

    k300 = np.array([MAT[m]['k'] for m in mats])
    nexp = np.array([MAT[m]['n'] for m in mats])
    az = np.array([MAT[m]['az'] for m in mats])
    eps_f, eps_b = MAT[mats[0]]['eps'], MAT[mats[-1]]['eps']
    A_face = np.pi * (re[1:] ** 2 - re[:-1] ** 2)
    clamp = np.zeros(nr, bool) if tg.r_clamp_mm is None else rc >= tg.r_clamp_mm * 1e-3
    back = np.zeros(nr, bool) if tg.r_back_mm is None else rc <= tg.r_back_mm * 1e-3
    idx = np.arange(nr * nz).reshape(nr, nz)
    j_film_last = mats.index(next(m for m in mats if m != mats[0])) - 1 if len(set(mats)) > 1 else -1
    T = np.full((nr, nz), tg.T_sink + 5.0)
    for it in range(it_max):
        k_r = k300[None, :] * (300.0 / T) ** nexp[None, :]
        k_z = k_r * az[None, :]
        rows, cols, vals = [], [], []
        b = Q.copy()
        diag = np.zeros((nr, nz))

        def link(i1, i2, G):
            rows.extend([i1, i2, i1, i2]); cols.extend([i2, i1, i1, i2])
            vals.extend([-G, -G, G, G])
        # radial links
        for i in range(nr - 1):
            Gr = 2 * np.pi * re[i + 1] * dz / (dr[i] / 2 / k_r[i] + dr[i + 1] / 2 / k_r[i + 1])
            for j in range(nz):
                link(idx[i, j], idx[i + 1, j], Gr[j])
        # axial links (the film/backing interface may carry a contact resistance 1/h_int)
        for j in range(nz - 1):
            Rint = 1.0 / tg.h_int if (tg.h_int and j == j_film_last) else 0.0
            Gz = A_face / (dz[j] / 2 / k_z[:, j] + dz[j + 1] / 2 / k_z[:, j + 1] + Rint)
            for i in range(nr):
                link(idx[i, j], idx[i, j + 1], Gz[i])
        # faces: front (j=0) and back (j=nz-1)
        for j, eps, side in ((0, eps_f, 'front'), (nz - 1, eps_b, 'back')):
            Tj = T[:, j]
            h_rad = eps * SIGMA_SB * (Tj ** 2 + T_ENV ** 2) * (Tj + T_ENV)
            G_rad = h_rad * A_face
            diag[:, j] += G_rad
            b[:, j] += G_rad * T_ENV
            hc = np.zeros(nr)
            if side == 'back' or tg.clamp_front:
                hc = np.where(clamp, tg.h_clamp, 0.0)
            if side == 'back':
                hc = hc + np.where(back, tg.h_back, 0.0)
            # contact in series with the half cell
            Gc = np.where(hc > 0, A_face / (1 / np.maximum(hc, 1e-30) + dz[j] / 2 / k_z[:, j]), 0.0)
            diag[:, j] += Gc
            b[:, j] += Gc * tg.T_sink
        A = sp.coo_matrix((vals, (rows, cols)), shape=(nr * nz, nr * nz)).tocsr()
        A = A + sp.diags(diag.ravel())
        Tn = spla.spsolve(A.tocsc(), b.ravel()).reshape(nr, nz)
        d = np.abs(Tn - T).max()
        T = 0.5 * T + 0.5 * Tn          # under-relaxed: radiation and k(T) both make it nonlinear
        if d < 1e-3:
            break
    converged = d < 1e-2
    res = dict(label=tg.label, I_uA=I_uA, Ep_keV=ep_kev, sigma_mm=sig_mm, P_W=P_tot,
               E_out_keV=e_out, T_film_C=T[0, 0] - 273.15, T_max_C=T.max() - 273.15,
               T_back_C=T[0, -1] - 273.15, iters=it + 1, converged=bool(converged))
    if return_field:
        res['field'] = (re, ze, T, mats)
    return res


# --------------------------------------------------------------------------- #
# checks
# --------------------------------------------------------------------------- #
def check():
    """Thin disk, conduction only, sink at the rim: the analytic Gaussian-source result
    T(0) − T(R) = P/(4π k t) [ln(R²/(2σ²)) + γ_E] (exponential-integral form)."""
    P_target = 1.0
    tg = Target([('Al', 10.0)], R_mm=10.0, r_clamp_mm=9.5, h_clamp=1e9, label='check')
    MAT['Al_ne'] = dict(MAT['Al'], eps=0.0)
    tg.layers = [('Al_ne', 10.0)]
    r = solve(tg, 1.0, ep_kev=700.0, sig_mm=1.0)
    P = r['P_W']
    k, t, R, s = 237., 10e-6, 9.5e-3, 1e-3   # sink at the clamp's inner edge
    dT = P / (4 * np.pi * k * t) * (np.log(R ** 2 / (2 * s ** 2)) + 0.5772)
    out = dict(P_W=P, fv_dT=r['T_film_C'] - 20.0, analytic_dT=dT)
    # against target_model.temp_disk (σ 1.5, 1.05 MeV, 1 µA; 95 °C in TARGET_STUDY §5)
    tg2 = Target([('Li2O', 1.49), ('Al', 10.0)], R_mm=10.5, r_clamp_mm=10.0, h_clamp=1e9)
    r2 = solve(tg2, 1.0, ep_kev=1050.0, sig_mm=1.5)
    out.update(fv_al10_disk_C=r2['T_film_C'], target_model_C=95.0)
    del MAT['Al_ne']
    return out


# --------------------------------------------------------------------------- #
# the options
# --------------------------------------------------------------------------- #
LI20 = ('Li', 20.0)            # Pierfrancesco's 20 µm metallic Li (1.07 mg/cm²)
LI2O = ('Li2O', 1.49)          # 300 µg/cm² Li₂O (the FEAS baseline)

OPTIONS = {
    # key: (Target, film limit °C, note)
    'A_al10_disk': (Target([LI2O, ('Al', 10)], R_mm=10, r_clamp_mm=8, h_clamp=5e3,
                           label='Li₂O on 10 µm Al disk, clamped r ≥ 8 mm'), 300,
                    'TARGET_STUDY baseline, thin'),
    'B_graphite25': (Target([LI2O, ('Graphite foil', 25)], R_mm=10, r_clamp_mm=8, h_clamp=5e3,
                            label='Li₂O on 25 µm graphite foil, clamped'), 300, 'TARGET_STUDY 4 µA option'),
    'C_dia50_li2o': (Target([LI2O, ('Diamond', 50)], R_mm=10, r_clamp_mm=8, h_clamp=1e4,
                            label='Li₂O on 50 µm CVD diamond, Cu clamp r ≥ 8 mm'), 300, 'thin diamond membrane'),
    'D_dia50_li20': (Target([LI20, ('Diamond', 50)], R_mm=10, r_clamp_mm=8, h_clamp=1e4,
                            label='20 µm Li on 50 µm diamond, Cu clamp'), 150, 'thick Li, thin diamond'),
    'E_dia300_li20': (Target([LI20, ('Diamond', 300)], R_mm=15, r_clamp_mm=11, h_clamp=1e4,
                             label='20 µm Li on 300 µm diamond, clamped r ≥ 11 mm'), 150, ''),
    'F_dia1000_li20_clamp': (Target([LI20, ('Diamond', 1000)], R_mm=20, r_clamp_mm=15, h_clamp=1e4,
                                    label='20 µm Li on 1 mm diamond, dry clamp r ≥ 15 mm'), 150,
                             'Pierfrancesco, rim-cooled, dry clamp'),
    'G_dia1000_li20_braze': (Target([LI20, ('Diamond', 1000)], R_mm=20, r_clamp_mm=15, h_clamp=2e5,
                                    label='20 µm Li on 1 mm diamond, brazed to a water-cooled Cu ring'), 150,
                             'rim brazed (active braze)'),
    'H_dia_mch_li20': (Target([LI20, ('Diamond', 300)], R_mm=20, r_clamp_mm=None, r_back_mm=20, h_back=3e4,
                              label='20 µm Li on diamond with micro-channels 300 µm under the face'), 150,
                       'Pierfrancesco: micro-channel cooling (effective h, see unit cell)'),
    'I_ta_dia300_li20': (Target([LI20, ('Ta', 10), ('Diamond', 300)], R_mm=15, r_clamp_mm=11, h_clamp=2e5,
                                label='20 µm Li / 10 µm Ta / 300 µm diamond, brazed rim'), 150,
                         'Ta stops the beam (H sink)'),
    'J_cu_block': (Target([LI2O, ('Cu', 1000)], R_mm=20, r_clamp_mm=None, r_back_mm=20, h_back=2e4,
                          label='Li₂O on a 1 mm Cu plate, water on the back'), 300, 'conventional thick target'),
    'K_cu_block_li20': (Target([LI20, ('Cu', 1000)], R_mm=20, r_clamp_mm=None, r_back_mm=20, h_back=2e4,
                               label='20 µm Li on a 1 mm Cu plate, water on the back'), 150, 'BNCT-style'),
}
CURRENTS = [0.25, 1, 4, 10, 30, 100, 300]


def max_current(tg, limit_C, ep=1100.0, sig=2.0):
    """largest current (µA) keeping the film below limit_C (bisection in log I)."""
    lo, hi = 1e-2, 3e3
    if solve(tg, hi, ep, sig)['T_film_C'] < limit_C:
        return hi
    for _ in range(30):
        mid = np.sqrt(lo * hi)
        if solve(tg, mid, ep, sig)['T_film_C'] < limit_C:
            lo = mid
        else:
            hi = mid
        if hi / lo < 1.03:
            break
    return lo


def scan():
    rows = []
    for key, (tg, lim, note) in OPTIONS.items():
        for sig in (2.0, 1.0):
            for I in CURRENTS:
                r = solve(tg, I, 1100.0, sig)
                r.update(key=key, film_limit_C=lim, note=note)
                rows.append(r)
    return pd.DataFrame(rows)


def limits():
    rows = []
    for key, (tg, lim, note) in OPTIONS.items():
        for sig in (2.0, 1.0):
            Imax = max_current(tg, lim, 1100.0, sig)
            r = solve(tg, min(Imax, 1e4), 1100.0, sig)
            rows.append(dict(key=key, label=tg.label, film_limit_C=lim, sigma_mm=sig,
                             I_max_uA=Imax, P_at_Imax_W=r['P_W'], W_per_uA=r['P_W'] / Imax,
                             E_out_keV=r['E_out_keV'], note=note))
    return pd.DataFrame(rows)


def sensitivity():
    """The 1 mm diamond with a rim clamp: how the contact and the diamond grade move it."""
    rows = []
    for h in (1e3, 3e3, 1e4, 3e4, 1e5, 3e5):
        for kd in (1000., 1800.):
            MAT['Diamond_x'] = dict(MAT['Diamond'], k=kd)
            tg = Target([LI20, ('Diamond_x', 1000)], R_mm=20, r_clamp_mm=15, h_clamp=h)
            for I in (10, 100):
                r = solve(tg, I, 1100.0, 2.0)
                rows.append(dict(h_clamp=h, k_diamond=kd, h_int=None, I_uA=I, P_W=r['P_W'],
                                 T_film_C=r['T_film_C']))
    del MAT['Diamond_x']
    # the Li/diamond interface (adhesion of evaporated Li on diamond is unknown: (ask))
    for hi in (1e4, 3e4, 1e5, 1e6, None):
        tg = Target([LI20, ('Diamond', 1000)], R_mm=20, r_clamp_mm=15, h_clamp=1e4, h_int=hi)
        for I in (4, 10, 100):
            r = solve(tg, I, 1100.0, 2.0)
            rows.append(dict(h_clamp=1e4, k_diamond=1800., h_int=hi, I_uA=I, P_W=r['P_W'],
                             T_film_C=r['T_film_C']))
    return pd.DataFrame(rows)


def microchannel(P_W=(5., 50., 500.), w_um=200., h_um=300., pitch_um=400., L_mm=40., n_ch=50,
                 flow_lpm=1.0, p_bar=3.0, face_um=300.):
    """Pierfrancesco's micro-channel diamond plate, analytically (ESTIMATE, ±×2 on h):
    laminar rectangular channels (Nu ≈ 5.4 for aspect 1.5, uniform flux), diamond fins at
    efficiency ≈ 1 (k 1800, 200 µm fins), so the face sees h_eff = h_w (w + 2h)/pitch.
    Pressure drop (f Re = 60), water temperature rise, the face sheet as a clamped strip
    under the water pressure, and the thermal stress E α ΔT/(1 − ν)."""
    k_w, nu, rho_w, cp_w = 0.60, 1.0e-6, 1000., 4186.
    w, h, pitch = w_um * 1e-6, h_um * 1e-6, pitch_um * 1e-6
    Dh = 2 * w * h / (w + h)
    h_w = 5.4 * k_w / Dh
    h_eff = h_w * (w + 2 * h) / pitch
    Q = flow_lpm / 60e3
    v = Q / (n_ch * w * h)
    Re = v * Dh / nu
    dp = 60.0 / Re * (L_mm * 1e-3 / Dh) * rho_w * v ** 2 / 2
    face = face_um * 1e-6
    sig_p = 0.5 * p_bar * 1e5 * (w / face) ** 2          # clamped-strip edge stress
    rows = []
    for P in P_W:
        dT_w = P / (rho_w * Q * cp_w)
        rows.append(dict(P_W=P, Dh_um=Dh * 1e6, h_wall=h_w, h_eff=h_eff, v_m_s=v, Re=Re,
                         dp_bar=dp / 1e5, dT_water_K=dT_w, face_stress_MPa=sig_p / 1e6,
                         # diamond: E 1050 GPa, α 1.0e-6 /K, ν 0.1; ΔT across the plate from the scan (~P/2.5 W/K)
                         thermal_stress_MPa=1050e3 * 1.0e-6 * (P / 2.5) / 0.9,
                         diamond_strength_MPa='400-1000 (CVD, thickness dependent)'))
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    mc = microchannel()
    mc.to_csv(OUT / 'thermal_microchannel.csv', index=False)
    print(mc.to_string(index=False))
    c = check()
    print('check:', {k: round(v, 2) for k, v in c.items()})
    pd.DataFrame([c]).to_csv(OUT / 'thermal_check.csv', index=False)
    s = scan()
    s.to_csv(OUT / 'thermal_scan.csv', index=False)
    lim = limits()
    lim.to_csv(OUT / 'thermal_limits.csv', index=False)
    print(lim[lim.sigma_mm == 2.0][['key', 'film_limit_C', 'I_max_uA', 'P_at_Imax_W', 'E_out_keV']]
          .to_string(index=False))
    sen = sensitivity()
    sen.to_csv(OUT / 'thermal_sensitivity.csv', index=False)
    print(sen.to_string(index=False))
    piv = s[s.sigma_mm == 2.0].pivot(index='key', columns='I_uA', values='T_film_C').round(0)
    print(piv.to_string())


if __name__ == '__main__':
    main()
