#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
optics_toy.py -- does a large trigger plastic still perform?  Light yield,
uniformity and timing vs slab size and PMT readout, from a photon ray-trace.

    python trigger_scint/optics_toy.py            # -> out/optics.csv, figures

THE MODEL.  A rectangular PVT slab (EJ-200/BC-408 class: n = 1.58, 10 000
photons/MeV, rise 0.9 ns, decay 2.1 ns, bulk attenuation 250 cm -- the
technical length of a large cast sheet, below the 380 cm datasheet value).
Photons are emitted isotropically from points on a grid over the face, at
mid-depth, and traced bounce by bounce:

  * polished faces: total internal reflection when the incidence angle exceeds
    the critical angle (39.3 deg), with 0.98 per bounce for surface quality;
  * otherwise the photon leaves into the wrapping (Al foil, specular,
    reflectivity 0.85) or is lost;
  * readout:
      - "edge"  a fishtail light guide glued over a whole short end (W x T),
                one or both ends.  The guide passes  min(1, A_pmt/A_end) x 0.85
                of what enters it (Liouville: étendue cannot shrink);
      - "back"  PMTs glued directly to the back face (disks, grease n = 1.50).

Fishtail guides add a per-photon delay, uniform in [0, 0.25 W n/c] (path
differences across a guide as long as the slab is wide), and every channel a
30 ps electronics jitter.

PMT: QE 25 %, collection 0.9 (2"), 0.85 (3"), 0.8 (5"); TTS sigma 0.15 /
0.30 / 0.60 ns -- a fast 2" timing tube, a standard 3", a large 5".

Timing estimator: the time of the k-th photoelectron, k = max(1, 5 % of Npe)
(a low leading-edge / CFD threshold), per end; two ends are averaged.  The
mean time at each position is subtracted (the Micromegas gives the hit
position, so the position dependence is a calibration), and the residual
sigma is reported at E_dep = 5 MeV (a typical X17 lepton deposit) and 1 MeV.

What it is for: RELATIVE comparisons between sizes and readouts.  Absolute
photoelectron numbers from a toy like this are good to a factor ~1.5; anchor
them with a bench measurement before trusting the energy resolution.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"

N_IDX = 1.58
C_MM_NS = 299.792458
PHOT_PER_MEV = 10_000
TAU_R, TAU_D = 0.9, 2.1
ATT_MM = 2500.0
R_TIR, R_WRAP = 0.98, 0.85
N_GREASE = 1.50
GUIDE_T = 0.85
QE = 0.25
GUIDE_DISP = 0.25    # fishtail path spread, fraction of W
JITTER_NS = 0.030
PMTS = {  # name: (photocathode diameter mm, collection eff, TTS sigma ns)
    '2"': (46.0, 0.90, 0.15),
    '3"': (70.0, 0.85, 0.30),
    '5"': (110.0, 0.80, 0.60),
}


def trace(dims, src, n_ph, readouts, rng, max_bounce=400):
    """Trace n_ph photons from point src in a box [0,W]x[0,L]x[0,T] (mm).
    readouts: list of (face, test) -- face index 0..5 = (-x,+x,-y,+y,-z,+z),
    test(points) -> bool array (inside the coupled area).  Returns, per
    readout, the arrival times (ns, path only) of photons reaching it, and the
    incidence cosine there."""
    W, L, T = dims
    lo = np.zeros(3)
    hi = np.array([W, L, T], float)
    u = rng.normal(size=(n_ph, 3))
    d = u / np.linalg.norm(u, axis=1)[:, None]
    p = np.repeat(np.asarray(src, float)[None, :], n_ph, 0)
    path = np.zeros(n_ph)
    alive = np.ones(n_ph, bool)
    hits = [([], []) for _ in readouts]
    cos_c = np.sqrt(1 - 1 / N_IDX ** 2)          # TIR if |cos| < cos_c
    cos_g = np.sqrt(1 - (N_GREASE / N_IDX) ** 2)  # TIR on grease
    for _ in range(max_bounce):
        idx = np.flatnonzero(alive)
        if not len(idx):
            break
        P, D = p[idx], d[idx]
        with np.errstate(divide="ignore", invalid="ignore"):
            tl = np.where(D < 0, (lo - P) / D, np.inf)
            th = np.where(D > 0, (hi - P) / D, np.inf)
        t2 = np.concatenate([tl, th], 1)          # faces: -x,-y,-z,+x,+y,+z
        f6 = np.argmin(t2, 1)
        s = t2[np.arange(len(idx)), f6]
        axis = f6 % 3
        face = 2 * axis + (f6 >= 3)              # -> 0..5 = -x,+x,-y,+y,-z,+z
        P = P + s[:, None] * D
        path[idx] += s
        # bulk absorption along this leg
        surv = rng.random(len(idx)) < np.exp(-s / ATT_MM)
        cosi = np.abs(D[np.arange(len(idx)), axis])
        absorbed = ~surv
        done = absorbed.copy()
        # readout faces
        for k, (rf, test) in enumerate(readouts):
            m = surv & (face == rf) & ~done
            if m.any():
                inside = np.zeros(len(idx), bool)
                inside[m] = test(P[m])
                det = inside & (cosi > cos_g)
                hits[k][0].append(path[idx][det] * N_IDX / C_MM_NS)
                hits[k][1].append(cosi[det])
                done |= det
        # reflection
        live = surv & ~done
        tir = cosi < cos_c
        refl = np.where(tir, rng.random(len(idx)) < R_TIR, rng.random(len(idx)) < R_WRAP)
        lost = live & ~refl
        done |= lost
        D[np.arange(len(idx)), axis] *= -1
        p[idx], d[idx] = P, D
        alive[idx[done]] = False
    return [(np.concatenate(a) if a else np.zeros(0)) for a, _ in hits]


def readout_set(kind, pmt, n_end, dims):
    """List of (face, test, guide_eff, pmt key)."""
    W, L, T = dims
    dpc, ce, tts = PMTS[pmt]
    apmt = np.pi * dpc ** 2 / 4
    if kind == "edge":
        geff = min(1.0, apmt / (W * T)) * GUIDE_T
        faces = [3, 2][:n_end]            # +y end, then -y end (ends along the beam axis v)
        return [(f, (lambda P: np.ones(len(P), bool)), geff, pmt) for f in faces]
    # back face (+z), n_end PMTs spread along y at x = W/2
    out = []
    ys = (np.arange(n_end) + 0.5) * L / n_end
    for y0 in ys:
        def test(P, y0=y0):
            return (P[:, 0] - W / 2) ** 2 + (P[:, 1] - y0) ** 2 < (dpc / 2) ** 2
        out.append((5, test, 1.0, pmt))
    return out


def evaluate(dims, kind, pmt, n_end, rng, n_ph=6000, grid=(5, 5)):
    W, L, T = dims
    rd = readout_set(kind, pmt, n_end, dims)
    _, ce, tts = PMTS[pmt]
    xs = (np.arange(grid[0]) + 0.5) * W / grid[0]
    ys = (np.arange(grid[1]) + 0.5) * L / grid[1]
    pe_per_mev, sig5, sig1, offs = [], [], [], []
    for x in xs:
        for y in ys:
            res = trace(dims, (x, y, T / 2), n_ph, [(f, t) for f, t, _, _ in rd], rng)
            eff = [len(r) / n_ph * g * QE * ce for r, (_, _, g, _) in zip(res, rd)]
            pe_per_mev.append(sum(eff) * PHOT_PER_MEV)
            offs.append(np.mean([np.median(r) if len(r) else np.nan for r in res]))
            for E, store in ((5.0, sig5), (1.0, sig1)):
                store.append(time_sigma(res, eff, E, tts, rng, kind,
                                        W * GUIDE_DISP * N_IDX / C_MM_NS if kind == "edge" else 0.0))
    pe = np.array(pe_per_mev)
    return dict(W_cm=W / 10, L_cm=L / 10, T_cm=T / 10, readout=kind, pmt=pmt, n_pmt=n_end,
                pe_per_MeV=float(pe.mean()), nonunif_rms=float(pe.std() / pe.mean()),
                min_over_max=float(pe.min() / pe.max()),
                stoch_at_1MeV=float(1 / np.sqrt(pe.mean())),
                sigma_t_5MeV_ns=float(np.nanmean(sig5)), sigma_t_1MeV_ns=float(np.nanmean(sig1)),
                offset_spread_ns=float(np.nanstd(offs)))


def time_sigma(res, eff, E, tts, rng, kind, guide_ns=0.0, n_trial=300):
    """sigma of the (averaged over readouts) k-th-pe time at deposit E."""
    ts = []
    for _ in range(n_trial):
        tt = []
        for r, e in zip(res, eff):
            npe = rng.poisson(e * PHOT_PER_MEV * E)
            if npe < 1 or not len(r):
                continue
            t = (rng.choice(r, npe) + rng.exponential(TAU_D, npe) + rng.exponential(TAU_R, npe)
                 + rng.normal(0, tts, npe) + rng.uniform(0, guide_ns, npe))
            k = max(1, int(round(0.05 * npe)))
            tt.append(np.partition(t, k - 1)[k - 1] + rng.normal(0, JITTER_NS))
        if tt:
            ts.append(np.mean(tt) if kind == "edge" else np.min(tt))
    return float(np.std(ts)) if len(ts) > 10 else np.nan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    rng = np.random.default_rng(3)
    OUT.mkdir(exist_ok=True)
    rows = []
    sizes = [(40.3, 30, 2), (60, 60, 2), (70, 70, 2), (78, 80, 2), (70, 70, 5), (78, 80, 5)]
    if a.quick:
        sizes = sizes[:2]
    configs = [("edge", '2"', 1), ("edge", '2"', 2), ("edge", '3"', 2), ("edge", '5"', 2),
               ("back", '3"', 2), ("back", '3"', 4), ("back", '5"', 4)]
    for W, L, T in sizes:
        for kind, pmt, n in configs:
            if kind == "back" and T < 3:
                continue        # back-face PMTs only make sense on the thick slabs
            r = evaluate((W * 10, L * 10, T * 10), kind, pmt, n, rng)
            rows.append(r)
            print(f"{W:5.1f}x{L:4.0f}x{T:.0f} {kind:4s} {n}x{pmt:3s}  {r['pe_per_MeV']:6.0f} pe/MeV  "
                  f"nonunif {r['nonunif_rms']:.2f}  min/max {r['min_over_max']:.2f}  "
                  f"sig_t(5MeV) {r['sigma_t_5MeV_ns']*1e3:4.0f} ps  (1MeV) {r['sigma_t_1MeV_ns']*1e3:4.0f} ps  "
                  f"offset spread {r['offset_spread_ns']*1e3:4.0f} ps", flush=True)
    with open(OUT / "optics.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    # the as-built bars, for calibration of the toy against reality: one 20 x 30 x 2 bar, one 2" end
    r = evaluate((200, 300, 20), "edge", '2"', 1, rng)
    print("as-built 20x30x2 bar, one 2\" PMT:", {k: round(v, 3) if isinstance(v, float) else v
                                               for k, v in r.items()})


if __name__ == "__main__":
    main()
