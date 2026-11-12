#!/usr/bin/env python3
"""Run one (detector, source) point of the collider X17 toy.

  python colliders/toy/run.py --det star --source x17_eta --system auau200 --n 400000 --nfit 3000

Sources: x17_pi0, x17_eta, dal_pi0, dal_eta (Kroll-Wada band 8-30 MeV), conv
(pi0 photons converting in the beam pipe and the first silicon layer), scan:<p GeV>.
Writes colliders/out/pairs/<det>__<source>__<system>.csv (one row per fitted pair)
and a .json summary (thrown, both-leptons-accepted, weights).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kinematics as kin  # noqa: E402
import tracking as trk  # noqa: E402
from detectors import DETECTORS  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / 'out' / 'pairs'


def conv_layers(det):
    """Indices of the conversion layers: the beam pipe and the first measuring layer if inside 5 cm."""
    idx = [i for i, L in enumerate(det.layers) if L.group == 'bp']
    for i, L in enumerate(det.layers):
        if L.meas and L.t > 0 and L.r < 0.05:
            idx.append(i)
            break
    return idx


def make_sample(det, source, system, n, rng):
    """Return lepton four-vectors, start points, start layer, weights and truth info."""
    vz = rng.normal(0, det.vz_sigma, n)
    if source != 'conv':
        g = kin.gen_pairs(rng, n, source, system)
        start = np.column_stack([np.zeros(n), np.zeros(n), vz])
        V = g['ep'] + g['em']
        return [dict(ep=g['ep'], em=g['em'], start=start, start_layer=None, w=g['w'],
                     mtrue=g['mtrue'], pV=V, vz=vz, conv_r=np.zeros(n))], n
    # conversions: every photon of n pi0 converts in each conversion layer, weighted by P(conv)
    gam = kin.gen_photons(rng, n, system)
    vzg = np.concatenate([vz, vz])
    out = []
    for li in conv_layers(det):
        Ly = det.layers[li]
        uT = np.hypot(gam[:, 1], gam[:, 2])
        E = gam[:, 0]
        ux, uy, uz = gam[:, 1] / E, gam[:, 2] / E, gam[:, 3] / E
        sT = Ly.r / np.maximum(uT / E, 1e-9)
        X = np.column_stack([ux * sT, uy * sT, vzg + uz * sT])
        inz = np.abs(X[:, 2]) < Ly.zmax
        cosl = uT / E
        w = 7 / 9 * Ly.t / np.maximum(cosl, 0.02) * inz
        xs = kin.bh_split(rng, len(E))
        Ee = np.maximum(xs * E, kin.ME * 1.01)
        Ep = np.maximum((1 - xs) * E, kin.ME * 1.01)
        u = np.column_stack([ux, uy, uz])
        pe = np.sqrt(Ee ** 2 - kin.ME ** 2)
        pp = np.sqrt(Ep ** 2 - kin.ME ** 2)
        em = np.column_stack([Ee, pe[:, None] * u])
        ep = np.column_stack([Ep, pp[:, None] * u])
        out.append(dict(ep=ep, em=em, start=X, start_layer=li, w=w, mtrue=np.zeros(len(E)),
                        pV=gam, vz=vzg, conv_r=np.full(len(E), Ly.r)))
    return out, n


_W = {}


def _init(det_key):
    _W['det'] = DETECTORS[det_key]


def _fit_pair(args):
    det = _W['det']
    (hp, hm, qp_list, vtx, init_p, init_m, pp_prior, pm_prior) = args
    res = []
    for hits, q, init, pprior in ((hp, +1, init_p, pp_prior), (hm, -1, init_m, pm_prior)):
        f = trk.TrackFit(det, hits, q, vtx, init, pprior).fit()
        res.append(f)
    # conversion hypothesis on each candidate layer (beam pipe, first silicon layer); keep the best
    a = np.array([res[0]['px'], res[0]['py'], res[0]['pz']])
    b = np.array([res[1]['px'], res[1]['py'], res[1]['pz']])
    u = a / np.linalg.norm(a) + b / np.linalg.norm(b)
    phi = math.atan2(u[1], u[0])
    lam = math.atan2(u[2], math.hypot(u[0], u[1]))
    best = (np.inf, 1)
    for li in conv_layers(det):
        zc = vtx[2] + det.layers[li].r * math.tan(lam)
        c2, ndf = trk.ConvPairFit(det, li, [(hp, +1), (hm, -1)], (phi, lam),
                                  (float(np.linalg.norm(a)), float(np.linalg.norm(b))), zc).fit()
        if c2 < best[0]:
            best = (c2, ndf)
    res[0]['chi2_conv'], res[0]['ndf_conv'] = best
    return res


def hits_of(sim, j):
    return [(int(i), float(sim['hphi'][j, i]), float(sim['hz'][j, i])) for i in np.where(sim['hit'][j])[0]]


def init_of(p4, start):
    pt = math.hypot(p4[1], p4[2])
    p = math.sqrt(pt ** 2 + p4[3] ** 2)
    # a primary-track fit starts from the vertex; for conversions we start at the measured vertex
    return (0.0, 0.0, float(start[2]), math.atan2(p4[2], p4[1]), math.atan2(p4[3], pt), p)


def run(det_key, source, system, n, nfit, seed, nproc):
    det = DETECTORS[det_key]
    rng = np.random.default_rng(seed)
    samples, n_thrown = make_sample(det, source, system, n, rng)
    rows = []
    summ = dict(det=det_key, label=det.label, source=source, system=system, n_thrown=n_thrown,
                y_gen=kin.Y_GEN, w_produced=0.0, w_accepted=0.0, n_accepted=0, n_fitted=0)
    jobs = []
    meta = []
    for smp in samples:
        N = smp['ep'].shape[0]
        simp = trk.simulate(det, smp['ep'], np.full(N, 1.0), start=smp['start'],
                            start_layer=smp['start_layer'], rng=rng)
        simm = trk.simulate(det, smp['em'], np.full(N, -1.0), start=smp['start'],
                            start_layer=smp['start_layer'], rng=rng)
        acc = trk.passes(det, simp) & trk.passes(det, simm)
        summ['w_produced'] += float(smp['w'].sum())
        summ['w_accepted'] += float(smp['w'][acc].sum())
        summ['n_accepted'] += int(acc.sum())
        idx = np.where(acc & (smp['w'] > 0))[0]
        meta.append((smp, simp, simm, idx))
    # fit a subsample of accepted pairs; each fitted pair carries weight w * (n_acc_w / fitted_w)
    all_idx = [(k, j) for k, (_, _, _, idx) in enumerate(meta) for j in idx]
    if len(all_idx) > nfit:
        pick = rng.choice(len(all_idx), nfit, replace=False)
        all_idx = [all_idx[i] for i in sorted(pick)]
    for k, j in all_idx:
        smp, simp, simm, _ = meta[k]
        vtx = (rng.normal(0, det.s_vtx_xy), rng.normal(0, det.s_vtx_xy),
               smp['vz'][j] + rng.normal(0, det.s_vtx_z))
        pp = float(np.linalg.norm(smp['ep'][j, 1:]))
        pm = float(np.linalg.norm(smp['em'][j, 1:]))
        jobs.append((hits_of(simp, j), hits_of(simm, j), None, vtx,
                     init_of(smp['ep'][j], smp['start'][j]), init_of(smp['em'][j], smp['start'][j]), pp, pm))
    with Pool(nproc, initializer=_init, initargs=(det_key,)) as pool:
        fits = pool.map(_fit_pair, jobs, chunksize=8)
    wsum_fit = sum(meta[k][0]['w'][j] for k, j in all_idx)
    scale = summ['w_accepted'] / wsum_fit if wsum_fit > 0 else 0.0
    for (k, j), (fp, fm) in zip(all_idx, fits):
        smp = meta[k][0]
        a = np.array([fp['px'], fp['py'], fp['pz']])
        b = np.array([fm['px'], fm['py'], fm['pz']])
        Ea = math.sqrt(a @ a + kin.ME ** 2)
        Eb = math.sqrt(b @ b + kin.ME ** 2)
        m2 = (Ea + Eb) ** 2 - np.sum((a + b) ** 2)
        ep, em = smp['ep'][j], smp['em'][j]
        cos_true = float(ep[1:] @ em[1:] / np.linalg.norm(ep[1:]) / np.linalg.norm(em[1:]))
        cos_reco = float(a @ b / np.linalg.norm(a) / np.linalg.norm(b))
        pV = smp['pV'][j]
        rows.append(dict(w=smp['w'][j] * scale, mtrue=smp['mtrue'][j], mreco=math.sqrt(max(m2, 0.0)),
                         p_true_ep=float(np.linalg.norm(ep[1:])), p_true_em=float(np.linalg.norm(em[1:])),
                         p_reco_ep=float(np.linalg.norm(a)), p_reco_em=float(np.linalg.norm(b)),
                         pt_true_ep=float(np.hypot(ep[1], ep[2])), pt_true_em=float(np.hypot(em[1], em[2])),
                         open_true=math.degrees(math.acos(max(-1, min(1, cos_true)))),
                         open_reco=math.degrees(math.acos(max(-1, min(1, cos_reco)))),
                         pV=float(np.linalg.norm(pV[1:])), ptV=float(np.hypot(pV[1], pV[2])),
                         chi2_ep=fp['chi2'], ndf_ep=fp['ndf'], chi2_em=fm['chi2'], ndf_em=fm['ndf'],
                         chi2_conv=fp['chi2_conv'], ndf_conv=fp['ndf_conv'],
                         conv_r=smp['conv_r'][j]))
    summ['n_fitted'] = len(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    tag = f'{det_key}__{source.replace(":", "")}__{system}'
    pd.DataFrame(rows).to_csv(OUT / f'{tag}.csv', index=False)
    (OUT / f'{tag}.json').write_text(json.dumps(summ, indent=1))
    acc_dy = summ['w_accepted'] / (summ['n_thrown'] / (2 * kin.Y_GEN)) if source != 'conv' else None
    print(f'{tag}: thrown {n_thrown}, accepted {summ["n_accepted"]}, fitted {len(rows)}, '
          f'w_acc/(N/2Y) = {summ["w_accepted"] / (summ["n_thrown"] / (2 * kin.Y_GEN)):.3e}')
    return summ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--det', required=True)
    ap.add_argument('--source', required=True)
    ap.add_argument('--system', default='auau200')
    ap.add_argument('--n', type=int, default=200000)
    ap.add_argument('--nfit', type=int, default=2000)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--nproc', type=int, default=max(1, (os.cpu_count() or 2) - 2))
    a = ap.parse_args()
    run(a.det, a.source, a.system, a.n, a.nfit, a.seed, a.nproc)


if __name__ == '__main__':
    main()
