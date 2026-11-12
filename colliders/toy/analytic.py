#!/usr/bin/env python3
"""Back-of-envelope numbers for the collider X17 note (2026-11-12).

Writes colliders/out/analytic_*.csv and prints them:
  1. X17 kinematics by source (momentum in the parent frame, lepton momentum, minimum opening angle);
  2. tracking thresholds: the pT at which a primary lepton reaches the radius a detector needs
     (2R = r_need, R = pT / (0.3 B));
  3. Highland theta0 of the material before the first hit, and the scattering floor on m_ee;
  4. the fake mass of a conversion at radius r_c reconstructed as a primary pair:
     m_fake ~ 0.3 B r_c (p1 + p2) / sqrt(p1 p2) >= 0.6 B r_c   [GeV, T, m].
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import kinematics as kin  # noqa: E402
from detectors import DETECTORS  # noqa: E402

OUT = HERE.parent / 'out'
M = kin.M_X17


def kinematics_table():
    rows = []
    for name, mP in (('at rest (nuclear de-excitation)', None), ('pi0 -> gamma X17', kin.MPI0),
                     ('eta -> gamma X17', kin.META), ('omega -> pi0 X17', 0.78266)):
        if mP is None:
            pX = 0.0
        elif name.startswith('omega'):
            pX = np.sqrt((mP ** 2 - (kin.MPI0 + M) ** 2) * (mP ** 2 - (kin.MPI0 - M) ** 2)) / (2 * mP)
        else:
            pX = (mP ** 2 - M ** 2) / (2 * mP)
        EX = np.hypot(pX, M)
        rows.append(dict(source=name, p_X_parent_frame_MeV=pX * 1e3, E_X_MeV=EX * 1e3,
                         lepton_p_symmetric_MeV=EX / 2 * 1e3,
                         theta_min_deg=np.degrees(2 * np.arcsin(min(1.0, M / EX)))))
    return pd.DataFrame(rows)


def thresholds():
    rows = []
    for key, D in DETECTORS.items():
        need = []
        for grp, nmin in D.need.items():
            # radius of the nmin-th real row/layer of this group (effective rows count rep times)
            rows_r = []
            for L in D.layers:
                if L.meas and L.group == grp:
                    rows_r += [L.r] * L.rep
            rows_r = sorted(rows_r)
            need.append(rows_r[min(nmin, len(rows_r)) - 1])
        r_need = max(need)
        first = min(i for i, L in enumerate(D.layers) if L.meas)
        t_before = max(sum(L.t for L in D.layers[:first]), 1e-6)  # ALICE 3: first layer in vacuum
        rows.append(dict(det=key, label=D.label, B_T=D.B, r_needed_cm=r_need * 100,
                         pT_min_MeV=0.3 * D.B * r_need / 2 * 1e3,
                         t_before_first_hit_pct=t_before * 100,
                         r_first_hit_cm=D.layers[first].r * 100,
                         sigM_ms_floor_MeV=np.sqrt(2) * 13.6 * np.sqrt(t_before) * (1 + 0.038 * np.log(t_before)),
                         theta0_at_50MeV_mrad=0.0136 / 0.05 * np.sqrt(t_before) * (1 + 0.038 * np.log(t_before)) * 1e3))
    return pd.DataFrame(rows)


def fake_mass():
    rows = []
    for key, D in DETECTORS.items():
        for L in D.layers:
            if L.t > 0 and L.r < 0.05 or L.group == 'ifc':
                rows.append(dict(det=key, layer=L.group, r_cm=L.r * 100, t_pct=L.t * 100,
                                 m_fake_symmetric_MeV=0.6 * D.B * L.r * 1e3,
                                 m_fake_3to1_MeV=0.3 * D.B * L.r * 4 / np.sqrt(3) * 1e3))
    return pd.DataFrame(rows)


def eta_protophobic():
    """Rough BR(eta -> gamma X17) for the protophobic vector of Feng et al. 2016 (eps_n ~ 1.1e-2).

    Anomaly amplitudes A(P -> gamma V) ~ sum_q N_c Q_q eps_q c_q / f, eta = cos(th) eta8 - sin(th) eta1,
    one mixing angle th = -20 deg, f8 = 1.26 f_pi, f1 = 1.17 f_pi.  BR(gamma X)/BR(gamma gamma) =
    2 (A_X/A_gg)^2 (1 - m^2/m_eta^2)^3.  eps_s is free in the model: eps_s = eps_d (couplings ~ B - Q) and
    eps_s = 0 bracket it.  Estimate only; the protophobic vector is excluded by SINDRUM pi+ -> e+ nu e+e-
    (Hostert & Pospelov 2023), so this band shows the scale a vector X17 would have, not a prediction.
    """
    th = np.radians(-20.0)
    f8, f1 = 1.26, 1.17
    Q = np.array([2 / 3, -1 / 3, -1 / 3])
    c8 = np.array([1, 1, -2]) / np.sqrt(6)
    c1 = np.array([1, 1, 1]) / np.sqrt(3)
    rows = []
    for eps_n in (1.1e-2,):
        for lab, eps_s in (('eps_s = eps_d', 2 / 3 * eps_n), ('eps_s = 0', 0.0)):
            eps = np.array([-eps_n / 3, 2 / 3 * eps_n, eps_s])
            Agg = np.cos(th) * (Q ** 2 @ c8) / f8 - np.sin(th) * (Q ** 2 @ c1) / f1
            AX = np.cos(th) * ((Q * eps) @ c8) / f8 - np.sin(th) * ((Q * eps) @ c1) / f1
            ratio = 2 * (AX / Agg) ** 2 * (1 - (M / kin.META) ** 2) ** 3
            rows.append(dict(eps_n=eps_n, case=lab, BR_ratio_to_gg=ratio, BR_eta_gamma_X=ratio * kin.BR_GG['eta']))
    # pi0 check: protophobic -> 0; dark photon eps = 8e-4 -> NA48/2 ceiling
    rows.append(dict(eps_n=np.nan, case='pi0, dark photon eps=8e-4 (NA48/2)', BR_ratio_to_gg=2 * 8e-4 ** 2 * (1 - (M / kin.MPI0) ** 2) ** 3,
                     BR_eta_gamma_X=2 * 8e-4 ** 2 * (1 - (M / kin.MPI0) ** 2) ** 3 * kin.BR_GG['pi0']))
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(exist_ok=True)
    pd.set_option('display.width', 220)
    for name, df in (('kinematics', kinematics_table()), ('thresholds', thresholds()), ('fake_mass', fake_mass()),
                     ('eta_protophobic', eta_protophobic())):
        df.to_csv(OUT / f'analytic_{name}.csv', index=False)
        print(f'--- {name}')
        print(df.to_string(index=False, float_format=lambda v: f'{v:.3g}'))


if __name__ == '__main__':
    main()
