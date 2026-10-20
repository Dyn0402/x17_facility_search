#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gamma_toy.py -- how gamma-sensitive is a big trigger plastic, vs thickness, threshold and segmentation?

    python trigger_scint/gamma_toy.py            # -> out/gamma_toy.csv, out/gamma_rates.csv, figures

AN ANALYTIC STAND-IN until Geant4 (the TB campaign covers the ILL beam; nothing covers hall gammas).

THE MODEL.  Photons of one energy enter a W x L x T PVT plate (C9H10, 1.023 g/cm3) through its front face,
uniformly over the face, either normally ("beam": from the target region) or with a cosine-weighted isotropic
direction ("room": a diffuse hall field).  They are tracked through the box:
  * Compton scattering, Klein-Nishina (total and differential), on 3.33e23 e/cm3;
  * pair production, from a table of mu/rho (nuclear + triplet) for polystyrene-like plastic (XCOM-level,
    +-10 %); the pair's kinetic energy is split evenly, the two 511 keV photons are tracked;
  * photoabsorption and Rayleigh are ignored (negligible above 150 keV in plastic).
Every electron deposits min(T_e, 2 MeV/cm x its straight path to the box surface): a CSDA, straight-line
electron, so thin plates leak the tail of high-energy Compton electrons.  Brems is ignored (it escapes).

Outputs, per photon entering the face: P(E_dep > thr) for E_gamma x T x thr.  Rates: a field of
D [uSv/h] of photons of energy E has fluence rate phi = D / h*(10)(E) per cm2 per s; through a plate in a
diffuse field (both faces, cosine law) the crossing rate is ~ phi/2 x W x L.  Singles per channel for a plate
split into N bars are rate / N.  h*(10) from ICRP 74 (pSv cm2): 0.5 MeV 2.93, 1 MeV 5.20, 2 MeV 8.6,
3 MeV 11.1, 5 MeV 14.8, 6 MeV 16.4, 10 MeV 20.4 (interpolated in log-log).
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"

ME = 0.51099895
RE2 = (2.8179403262e-13) ** 2           # cm2
NE = 1.023 * 6.02214e23 * (9 * 6 + 10 * 1) / (9 * 12.011 + 10 * 1.008)   # e / cm3 in PVT
RHO = 1.023
DEDX = 2.0                              # MeV / cm, electrons
# pair production (nuclear + triplet) in polystyrene-like plastic, cm2/g (XCOM-level, +-10 %)
PAIR_E = np.array([1.022, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 15.0, 20.0, 30.0])
PAIR_MU = np.array([0.0, 2.5e-5, 2.7e-4, 9.0e-4, 1.45e-3, 1.9e-3, 2.3e-3, 2.95e-3, 3.5e-3, 4.5e-3, 5.3e-3, 6.4e-3])
H10_E = np.array([0.5, 1.0, 2.0, 3.0, 5.0, 6.0, 10.0, 20.0])
H10 = np.array([2.93, 5.20, 8.6, 11.1, 14.8, 16.4, 20.4, 27.0])     # pSv cm2 (ICRP 74; 20 MeV extrapolated)


def sigma_kn(E):
    """Klein-Nishina total cross section per electron, cm2."""
    k = np.asarray(E, float) / ME
    a = (1 + k) / k ** 2 * (2 * (1 + k) / (1 + 2 * k) - np.log(1 + 2 * k) / k)
    b = np.log(1 + 2 * k) / (2 * k) - (1 + 3 * k) / (1 + 2 * k) ** 2
    return 2 * np.pi * RE2 * (a + b)


def mu_parts(E):
    mc = NE * sigma_kn(E)
    mp = np.interp(E, PAIR_E, PAIR_MU, left=0.0) * RHO
    return mc, mp


def sample_kn(E, rng):
    """Scattered-photon energy fraction eps = E'/E, Kahn-type rejection on the KN distribution."""
    k = E / ME
    eps0 = 1 / (1 + 2 * k)
    out = np.empty_like(E)
    todo = np.arange(len(E))
    while len(todo):
        kk, e0 = k[todo], eps0[todo]
        a1, a2 = -np.log(e0), (1 - e0 ** 2) / 2
        r1, r2, r3 = rng.random((3, len(todo)))
        eps = np.where(r1 < a1 / (a1 + a2), np.exp(-a1 * r2), np.sqrt(e0 ** 2 + (1 - e0 ** 2) * r2))
        t = (1 - eps) / (kk * eps)
        sin2 = t * (2 - t)
        g = 1 - eps * sin2 / (1 + eps ** 2)
        ok = r3 < g
        out[todo[ok]] = eps[ok]
        todo = todo[~ok]
    return out


def rotate(d, cth, rng):
    """New direction at polar angle acos(cth) from d, random azimuth."""
    phi = 2 * np.pi * rng.random(len(d))
    sth = np.sqrt(np.clip(1 - cth ** 2, 0, 1))
    a = np.where(np.abs(d[:, 2:3]) < 0.9, np.array([[0, 0, 1.0]]), np.array([[1.0, 0, 0]]))
    u = np.cross(d, a)
    u /= np.linalg.norm(u, axis=1)[:, None]
    v = np.cross(d, u)
    return cth[:, None] * d + sth[:, None] * (np.cos(phi)[:, None] * u + np.sin(phi)[:, None] * v)


def exit_dist(p, d, box):
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.where(d > 0, (box - p) / d, np.where(d < 0, -p / d, np.inf))
    return t.min(1)


def run(Eg, dims_cm, n, rng, mode="room"):
    """Deposited energy per photon entering the front face (z = 0)."""
    box = np.asarray(dims_cm, float)
    p = np.column_stack([rng.random(n) * box[0], rng.random(n) * box[1], np.zeros(n)])
    if mode == "beam":
        d = np.tile([0.0, 0.0, 1.0], (n, 1))
    else:                                           # cosine-weighted inward
        ct = np.sqrt(rng.random(n))
        ph = 2 * np.pi * rng.random(n)
        st = np.sqrt(1 - ct ** 2)
        d = np.column_stack([st * np.cos(ph), st * np.sin(ph), ct])
    E = np.full(n, float(Eg))
    owner = np.arange(n)
    dep = np.zeros(n)
    for _ in range(60):
        if not len(E):
            break
        mc, mp = mu_parts(E)
        mu = mc + mp
        s = -np.log(rng.random(len(E))) / mu
        live = s < exit_dist(p, d, box)
        p, d, E, owner, mc, mu = p[live] + s[live, None] * d[live], d[live], E[live], owner[live], mc[live], mu[live]
        if not len(E):
            break
        pair = rng.random(len(E)) > mc / mu
        # Compton
        c = ~pair
        if c.any():
            Ec = E[c]
            eps = sample_kn(Ec, rng)
            Te = Ec * (1 - eps)
            cth_g = 1 - (1 - eps) / (eps * Ec / ME)
            th_g = np.arccos(np.clip(cth_g, -1, 1))
            # electron angle: cot(phi_e) = (1 + k) tan(theta/2)
            k = Ec / ME
            phi_e = np.arctan2(1.0, (1 + k) * np.tan(th_g / 2))
            de = rotate(d[c], np.cos(phi_e), rng)
            np.add.at(dep, owner[c], np.minimum(Te, DEDX * exit_dist(p[c], de, box)))
            d_new = rotate(d[c], np.clip(cth_g, -1, 1), rng)
            Ec_new = Ec * eps
        # pair
        if pair.any():
            Ep = E[pair]
            for _side in range(2):
                np.add.at(dep, owner[pair], np.minimum((Ep - 2 * ME) / 2, DEDX * exit_dist(p[pair], d[pair], box)))
            u = rng.normal(size=(pair.sum(), 3))
            u /= np.linalg.norm(u, axis=1)[:, None]
            pa_p = np.concatenate([p[pair], p[pair]])
            pa_d = np.concatenate([u, -u])
            pa_E = np.full(2 * pair.sum(), ME)
            pa_o = np.concatenate([owner[pair], owner[pair]])
        nxt_p, nxt_d, nxt_E, nxt_o = [], [], [], []
        if c.any():
            keep = Ec_new > 0.02
            nxt_p.append(p[c][keep]); nxt_d.append(d_new[keep]); nxt_E.append(Ec_new[keep]); nxt_o.append(owner[c][keep])
        if pair.any():
            nxt_p.append(pa_p); nxt_d.append(pa_d); nxt_E.append(pa_E); nxt_o.append(pa_o)
        if not nxt_E:
            break
        p, d, E, owner = (np.concatenate(nxt_p), np.concatenate(nxt_d), np.concatenate(nxt_E),
                          np.concatenate(nxt_o))
    return dep


def h10(E):
    return float(np.exp(np.interp(np.log(E), np.log(H10_E), np.log(H10))))


EG = [0.478, 1.0, 1.461, 2.223, 2.614, 4.44, 6.13, 7.6, 10.83, 17.64]
TS = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
THRS = [0.5, 1.0, 1.67, 2.5, 3.0, 4.0]
SIDE = (75.0, 75.0)


def main():
    quick = "--quick" in sys.argv
    n = 20000 if quick else 200000
    rng = np.random.default_rng(11)
    OUT.mkdir(exist_ok=True)
    rows = []
    for mode in ("room", "beam"):
        for Eg in EG:
            for T in TS:
                dep = run(Eg, (*SIDE, T), n, rng, mode)
                r = dict(mode=mode, E_gamma=Eg, T_cm=T, p_interact=float(np.mean(dep > 0)))
                for thr in THRS:
                    r[f"p_gt_{thr:g}"] = float(np.mean(dep > thr))
                rows.append(r)
                print(f"{mode:4s} E={Eg:6.3f} T={T:3.0f}  any {r['p_interact']:.3f}  "
                      + "  ".join(f">{t:g}: {r[f'p_gt_{t:g}']:.4f}" for t in THRS), flush=True)
    with open(OUT / "gamma_toy.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    # rates per plate at 1 uSv/h of a diffuse field of one line, 75 x 75 plate
    rr = []
    for r in rows:
        if r["mode"] != "room":
            continue
        phi = 1e6 / 3600 / h10(r["E_gamma"])          # gamma / cm2 / s per uSv/h
        cross = phi / 2 * SIDE[0] * SIDE[1]
        rr.append(dict(E_gamma=r["E_gamma"], T_cm=r["T_cm"], phi_per_uSvh=round(phi, 1),
                       **{f"Hz_gt_{t:g}": round(cross * r[f"p_gt_{t:g}"]) for t in THRS}))
    with open(OUT / "gamma_rates.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rr[0]))
        w.writeheader()
        w.writerows(rr)
    print("wrote", OUT / "gamma_toy.csv", OUT / "gamma_rates.csv")


if __name__ == "__main__":
    main()
