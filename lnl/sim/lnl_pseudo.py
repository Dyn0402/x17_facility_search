#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lnl_pseudo.py -- the LNL X17 analysis run end to end on pseudo-data, as if it
were real data whose background we do not know exactly.  (FEASIBILITY_SIM.md
§17, 2026-10-14)

    LNL_SEL=$PWD/lnl/sim/sel_v3 python lnl/sim/lnl_pseudo.py [--ntoys 200]   # -> lnl/out/pseudo/

Binning: θ (2°, 90–180) × |y| (0.05) × E_sum (two γ₁ side-band bins, two
window bins), from the reference fit's event list (lnl_nd.collect: big
plastics, calibrated response, MM 15° + TOF).

The model is linear in its parameters: per day, μ + Σ_j θ_j g_j (lnl_nd.fisher_nd
templates).  θ_0 = r = R/R_ATOMKI, then the M1 / E1 / γ₁ norms, the γ*
anisotropy, the θ and |y| resolution, the E scale, four arm gains, an
acceptance cubic, a |y| tilt, and the reference unknown structure
(S_θ 2 % + S_θy 1 %).

The truth that makes the pseudo-data is NOT the fit model:
  * every background parameter is shifted at random: norms by 10 %, the
    acceptance cubic by 3 % per term, the constrained nuisances by their prior,
    the modelled structure modes by N(0, 1);
  * plus structure the fit does not contain at all: S_θE 2 % (local in angle ×
    energy sum: response, γ₁ leakage) and S_m 2 % (local in pair mass, ℓ =
    0.55 MeV: the shape most like an X17).
  * variant 'mc halves': the fit model is built from one half of the Monte
    Carlo and the truth from the other, so the templates also carry the MC's
    statistical noise.

The analysis, as on real data:
  1. look at the data in (θ, |y|) and at the signal region;
  2. blind the signal region (the cells holding 70 % of the expected X17 in
     the E_sum window), fit background only (r = 0) to everything else, and
     predict the background inside, with its uncertainty;
  3. unblind: data − predicted background;
  4. the full fit (r free) over all bins: r̂, σ, Z, and the 90 % CL upper
     limit (one-sided, Δχ² = 2.71), the profile likelihood in its quadratic
     approximation.
Then the coupling scan: many pseudo-experiments at each injected r.

Bins where a 1σ detector nuisance moves the template by > 30 % (kinematic
edges, almost no background) are left out of every fit: stable_bins().

Outputs (out/pseudo/): walk_bins.csv (one pseudo-experiment, every bin),
walk_proj.csv (1D projections with bands), walk_summary.json, toys.csv,
scan.csv.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lnl_nd as N      # noqa: E402
import lnl_calo as C    # noqa: E402
import lnl_syst as S    # noqa: E402

OUT = N.OUT.parent / 'pseudo'
HW = 'big plastics'
YB = np.r_[np.arange(0, 1.0, 0.05), 1.0001]
UNMODELLED = [('S_θE', 0.02), ('S_m', 0.02)]
NORM_SIG, ACC_SIG = 0.10, 0.03
SR_FRAC = 0.70
Q90 = 2.706
WALK = dict(r=1.0, days=7.0, seed=20261015)
R_SCAN = (0.0, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5)
DAYS_SCAN = (1.0, 7.0, 30.0)
KIND = re.compile(r'^(S_θy|S_θE|S_θ|S_m)\d+$')


def analysis(ec):
    lo, hi = ec
    eb = np.array([lo - 4, lo - 2, lo, 0.5 * (lo + hi), hi])
    return dict(axes=[('th', N.TH_B), ('y', YB), ('E', eb)], E=(eb[0], eb[-1])), eb


def kind_of(n):
    m = KIND.match(n)
    return m.group(1) if m else None


def build(ev, an, sel=None):
    st = N.STRUCTS[N.REF_STRUCT] + UNMODELLED
    _, _, names, o = N.fisher_nd(ev, an, st, sigma_g=S.PRIOR_G, sel=sel, templates=True)
    unm = np.array([kind_of(n) in ('S_θE', 'S_m') for n in names])
    return dict(g=np.asarray(o['g']), mu=np.asarray(o['mu']), names=names, prior=o['prior'], unm=unm)


def truth_params(M, rng, r):
    x = np.zeros(len(M['names']))
    for j, (n, p) in enumerate(zip(M['names'], M['prior'])):
        if n == 'r':
            x[j] = r
        elif n in ('M1', 'E1', 'g1'):
            x[j] = rng.normal(0, NORM_SIG)
        elif n.startswith('acc'):
            x[j] = rng.normal(0, ACC_SIG)
        elif kind_of(n):
            x[j] = rng.normal()
        elif p is not None:
            x[j] = rng.normal(0, p)
    return x


FRAGILE = 0.3      # drop bins where a 1σ detector shift moves the template by more than this fraction


def stable_bins(M):
    """bins where the linearised detector nuisances (θ and |y| resolution, E scale,
    arm gains) stay a small perturbation: |prior × derivative| < FRAGILE × μ.  The
    rest sit at kinematic edges with almost no expected background, where a linear
    Poisson model breaks down (2026-10-14: these bins alone inflated the pull of r
    to ×1.4)."""
    worst = np.zeros(len(M['mu']))
    for j, (n, p) in enumerate(zip(M['names'], M['prior'])):
        if p is not None and (n in ('k', 'e', 'ky') or n.startswith('gain')):
            worst = np.maximum(worst, np.abs(p * M['g'][j]))
    return worst < FRAGILE * np.maximum(M['mu'], 1e-30)


class Fitter:
    """Binned Poisson likelihood, model λ = T (μ + Gᵀ x), Gaussian priors on the
    constrained parameters.  Maximum likelihood by iteratively reweighted least
    squares (weights 1/λ, the Poisson ML fixed point for a linear model);
    intervals from the quadratic approximation of the profile likelihood."""

    def __init__(self, M, T, mask=None, widened=False):
        keep = np.ones(len(M['names']), bool) if widened else ~M['unm']
        self.names = [n for n, k in zip(M['names'], keep) if k]
        self.G = M['g'][keep]
        self.mu = M['mu']
        self.T = T
        ok = (self.mu > self.mu.max() * 1e-6) & stable_bins(M)
        self.mask = ok if mask is None else ok & mask
        self.P = np.array([0.0 if p is None else 1 / p ** 2 for p, k in zip(M['prior'], keep) if k])

    def fit(self, data, fix=None, iters=4):
        """fix: {index: value}.  -> (x, χ², cov over free params, free index)"""
        m = self.mask
        n = data[m]
        A = self.T * self.G[:, m]
        b0 = self.T * self.mu[m]
        p = len(self.names)
        fix = fix or {}
        free = np.array([j not in fix for j in range(p)])
        x = np.zeros(p)
        for j, v in fix.items():
            x[j] = v
        res0 = n - b0 - A[~free].T @ x[~free]
        Af, Pf = A[free], self.P[free]
        w = 1.0 / np.maximum(b0, 1.0)
        for _ in range(iters):
            H = (Af * w) @ Af.T + np.diag(Pf)
            x[free] = np.linalg.solve(H, (Af * w) @ res0)
            lam = b0 + A.T @ x
            w = 1.0 / np.maximum(lam, 1.0)
        H = (Af * w) @ Af.T + np.diag(Pf)
        chi2 = float(np.sum(w * (n - lam) ** 2) + np.sum(self.P * x ** 2))
        return x, chi2, np.linalg.inv(H), free

    def result(self, data):
        """full fit: r̂, σ, Z = r̂/σ, 90 % CL upper limit (one-sided, Δχ² = 2.71 from max(r̂, 0))."""
        x, chi2, cov, free = self.fit(data)
        rhat, sig = float(x[0]), float(np.sqrt(cov[0, 0]))
        ul = rhat + np.sqrt(Q90) * sig if rhat >= 0 else rhat + np.sqrt(rhat ** 2 + Q90 * sig ** 2)
        return dict(r_hat=rhat, sigma=sig, Z=rhat / sig, UL90=ul, x=x, cov=cov, free=free, chi2=chi2)


# --------------------------------------------------------------------------- #
def signal_region(M, shape):
    """cells (θ, |y|) in the E_sum window holding SR_FRAC of the expected X17,
    ranked by S/B.  Returns a bin mask over the flattened (y, E, θ) grid."""
    ny, ne, nt = shape
    s = M['g'][0].reshape(shape)[:, 2:, :].sum(1)
    b = M['mu'].reshape(shape)[:, 2:, :].sum(1)
    sb = np.where(b > 0, s / np.maximum(b, 1e-12), 0)
    order = np.argsort(sb.ravel())[::-1]
    cum = np.cumsum(s.ravel()[order]) / s.sum()
    cells = np.zeros(ny * nt, bool)
    cells[order[:np.searchsorted(cum, SR_FRAC) + 1]] = True
    cells = cells.reshape(ny, nt)
    m = np.zeros(shape, bool)
    m[:, 2:, :] = cells[:, None, :]
    return m.ravel(), cells


def pred_band(F, x, cov, free, rows_sel):
    """background prediction (r = 0 part) summed over a set of bins, with σ."""
    G = F.G[:, rows_sel]
    v = F.T * (F.mu[rows_sel].sum() + G.sum(1) @ x - G[0].sum() * x[0])
    gsum = F.T * G.sum(1)
    gsum[0] = 0
    gf = gsum[free]
    return v, float(np.sqrt(max(gf @ cov @ gf, 0)))


def walkthrough(M, eb, shape):
    rng = np.random.default_rng(WALK['seed'])
    T, r = WALK['days'], WALK['r']
    xt = truth_params(M, rng, r)
    lam_b = T * (M['mu'] + M['g'][1:].T @ xt[1:])
    lam_s = T * M['g'][0] * r
    lam = np.clip(lam_b + lam_s, 0, None)
    data = rng.poisson(lam).astype(float)
    srm, cells = signal_region(M, shape)
    # 2. blinded background-only fit on the control regions
    Fb = Fitter(M, T, mask=~srm)
    xb, _, covb, freeb = Fb.fit(data, fix={0: 0.0})
    Fall = Fitter(M, T)
    pred = T * (M['mu'] + Fall.G[1:].T @ xb[1:])
    gf = (T * Fall.G[:, :])[freeb]                          # per-bin σ of the prediction
    psig = np.sqrt(np.maximum(np.einsum('ij,ik,kj->j', gf, covb, gf), 0))
    # 4. full fit
    res = Fall.result(data)
    xf = res['x']
    fit_b = T * (M['mu'] + Fall.G[1:].T @ xf[1:])
    fit_s = T * Fall.G[0] * xf[0]
    nominal = T * M['mu']
    ny, ne, nt = shape
    th_lo, y_lo = N.TH_B[:-1], YB[:-1]
    iy, ie, it = np.unravel_index(np.arange(ny * ne * nt), shape)
    bins = pd.DataFrame(dict(theta_lo=th_lo[it], y_lo=y_lo[iy], E_lo=eb[ie], E_hi=eb[ie + 1], ebin=ie, data=data,
                             truth_bkg=lam_b, truth_sig=lam_s, nominal_mc=nominal, blind_pred=pred, blind_sig=psig,
                             fit_bkg=fit_b, fit_sig=fit_s, sr=srm))
    # 1D projections in θ, with bands
    rows = []
    sel_defs = {'window, |y|<0.3': (ie >= 2) & (y_lo[iy] < 0.299), 'window, |y|>0.45': (ie >= 2) & (y_lo[iy] >= 0.449),
                'window, all |y|': ie >= 2, 'side band, all |y|': ie < 2}
    for lab, sm in sel_defs.items():
        for k in range(nt):
            b = sm & (it == k)
            v, sg = pred_band(Fall, xb, covb, freeb, b)
            rows.append(dict(sel=lab, theta_lo=th_lo[k], data=data[b].sum(), nominal_mc=nominal[b].sum(),
                             truth_bkg=lam_b[b].sum(), truth_sig=lam_s[b].sum(), blind_pred=v, blind_sig=sg,
                             fit_bkg=fit_b[b].sum(), fit_sig=fit_s[b].sum(), in_sr=bool(srm[b].any())))
    proj = pd.DataFrame(rows)
    # the SR as a whole
    vS, sS = pred_band(Fall, xb, covb, freeb, srm)
    summ = dict(r_inj=r, days=T, seed=WALK['seed'], r_hat=res['r_hat'], sigma=res['sigma'], Z=res['Z'], UL90=res['UL90'],
                sr_cells=int(cells.sum()), sr_frac_signal=SR_FRAC,
                sr_data=float(data[srm].sum()), sr_pred=float(vS), sr_pred_sigma=float(sS),
                sr_truth_bkg=float(lam_b[srm].sum()), sr_truth_sig=float(lam_s[srm].sum()),
                sr_excess=float(data[srm].sum() - vS), chi2_full=res['chi2'],
                n_par_fit=len(Fall.names), n_par_unmodelled=int(M['unm'].sum()), n_bins=int(Fall.mask.sum()),
                truth_norms={n: float(xt[j]) for j, n in enumerate(M['names']) if n in ('M1', 'E1', 'g1')},
                blind_norms={n: float(xb[j]) for j, n in enumerate(Fall.names) if n in ('M1', 'E1', 'g1')})
    return bins, proj, summ


def toys(Mt, Mf, days, rs, ntoys, seed, variant, widened=False):
    rng = np.random.default_rng(seed)
    out = []
    for T in days:
        F = Fitter(Mf, T, widened=widened)
        for r in rs:
            t0 = time.time()
            for i in range(ntoys):
                xt = truth_params(Mt, rng, r)
                lam = np.clip(T * (Mt['mu'] + Mt['g'].T @ xt), 0, None)
                data = rng.poisson(lam).astype(float)
                res = F.result(data)
                out.append(dict(variant=variant, days=T, r_inj=r, toy=i, r_hat=res['r_hat'], sigma=res['sigma'],
                                Z=res['Z'], UL90=res['UL90']))
            q = pd.DataFrame(out[-ntoys:])
            print(f'{variant:10s} {T:4.0f} d  r {r:4.2f}: r̂ median {q.r_hat.median():+.3f} (16–84 {q.r_hat.quantile(.16):+.3f}…{q.r_hat.quantile(.84):+.3f}), '
                  f'pull σ {((q.r_hat - r) / q.sigma).std():.2f}, P(Z>3) {(q.Z > 3).mean():.2f}, UL med {q.UL90.median():.3f}  '
                  f'[{time.time() - t0:.0f} s]', flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ntoys', type=int, default=200)
    ap.add_argument('--no-halves', action='store_true')
    ap.add_argument('--widened-only', action='store_true',
                    help='only the "widened" check: the fit also floats the S_θE and S_m structure -> scan_widened.csv')
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    N.load_windows()
    C.set_response(N.REF_RESP, sigma_g='auto')
    ec = C.BEST.get((HW, N.REF_RESP), S.HWS[HW][0])
    S.HWS[HW] = (ec, C.HWS0[HW][1])
    ev = N.collect(HW, erange=(ec[0] - 4, ec[1]))
    an, eb = analysis(ec)
    shape = (len(YB) - 1, len(eb) - 1, len(N.TH_B) - 1)
    M = build(ev, an)
    print(f'{len(M["names"])} parameters ({M["unm"].sum()} unmodelled), {len(M["mu"])} bins', flush=True)

    if a.widened_only:
        t = pd.DataFrame(toys(M, M, (7.0, 30.0), (0.0, 0.2, 0.5, 1.0), a.ntoys, 3, 'widened', widened=True))
        t.to_csv(OUT / 'toys_widened.csv', index=False)
        summarise(t).to_csv(OUT / 'scan_widened.csv', index=False)
        return
    bins, proj, summ = walkthrough(M, eb, shape)
    bins.to_csv(OUT / 'walk_bins.csv', index=False)
    proj.to_csv(OUT / 'walk_proj.csv', index=False)
    (OUT / 'walk_summary.json').write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1), flush=True)

    rows = toys(M, M, DAYS_SCAN, R_SCAN, a.ntoys, 1, 'reference')
    if not a.no_halves:
        rng = np.random.default_rng(5)
        half = rng.random(len(ev['w'])) < 0.5
        Ma, Mb = build(ev, an, sel=half), build(ev, an, sel=~half)
        rows += toys(Mb, Ma, (7.0,), R_SCAN, a.ntoys, 2, 'mc halves')
    t = pd.DataFrame(rows)
    t.to_csv(OUT / 'toys.csv', index=False)
    sc = summarise(t)
    sc.to_csv(OUT / 'scan.csv', index=False)
    with pd.option_context('display.width', 250, 'display.max_columns', 30):
        print(sc.round(3).to_string())
    S.HWS[HW] = C.HWS0[HW]
    C.set_response('ideal')


def summarise(t):
    return (t.groupby(['variant', 'days', 'r_inj'])
          .apply(lambda q: pd.Series(dict(n=len(q), r_med=q.r_hat.median(), r_16=q.r_hat.quantile(.16), r_84=q.r_hat.quantile(.84),
                                          sigma_med=q.sigma.median(), pull_mean=((q.r_hat - q.name[2]) / q.sigma).mean(),
                                          pull_sd=((q.r_hat - q.name[2]) / q.sigma).std(), p_Z3=(q.Z > 3).mean(),
                                          p_Z2=(q.Z > 2).mean(), Z_med=q.Z.median(), UL_med=q.UL90.median(),
                                          UL_16=q.UL90.quantile(.16), UL_84=q.UL90.quantile(.84),
                                          cover90=(q.UL90 >= q.name[2]).mean())), include_groups=False)
            .reset_index())


if __name__ == '__main__':
    main()
