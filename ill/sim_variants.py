#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sim_variants.py -- how robust is the reach?  Re-runs the sim_feasibility model
with one assumption changed at a time (coincidence window, angle estimator,
backgrounds switched off) and prints the best-rate 3-sigma reach.

    python3 sim_variants.py --s1 /eos/.../ill/S1/summary --contracts /eos/.../ill/contracts \\
        -o variants.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import sim_feasibility as SF


R_MAX = 1.9e10                      # Ø2 cm spot at 46 MW (HANDOFF_SIM.md)


def scan(cfg, s1, tabs, menu, ecut, tau, est, zero=(), days=50.0, cache=None, rng=None,
         sigma_t=0.5, dt_cut=1.5, cos_scale=1.0):
    best = None
    for R in np.logspace(8, np.log10(R_MAX), 22):
        mod = SF.model(cfg, s1, tabs, menu, ecut, R, days, tau, sigma_t, dt_cut, est=est,
                       rng=rng, cache=cache)
        mod["COS"] = mod["COS"] * cos_scale
        for k in zero:
            mod[k] = np.zeros_like(mod[k])
        s = SF.reach(mod)
        if best is None or s < best[1]:
            best = (R, s, {k: float(np.sum(mod[k])) for k in
                           ("X17", "M1", "E0", "G", "WALL", "ACC", "COS")})
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s1", type=Path, required=True)
    ap.add_argument("--contracts", type=Path, required=True)
    ap.add_argument("-o", "--out", type=Path, required=True)
    ap.add_argument("--configs", default="G1,G3,G5")
    a = ap.parse_args()
    rng = np.random.default_rng(11)
    k1 = SF.load_table(a.contracts, "K1", "G5")
    rows = []
    for cfg in a.configs.split(","):
        s1 = {c: SF.load_s1(a.s1, cfg, c) for c in ("X17", "M1", "E0")}
        tabs = {r: SF.load_table(a.contracts, r, cfg) for r in ("C1", "C1w", "C1g")}
        tabs["K1"] = k1
        caches = {}
        variants = []
        for menu, ecut in (("sipm2", 12.0), ("sipm2", 13.0), ("strict", 12.0)):
            base = len(variants)
            # (tau, sigma_t, dt_cut, cos_scale, est, zero, label); tau = dt_cut when
            # the timing is varied: the accidental window is the cut window.
            variants += [
                (2.5, 0.5, 1.5, 1, "nomline", (), "baseline (sig_t 0.5, |dt|<1.5, 2tau 5)"),
                (1.5, 0.5, 1.5, 1, "nomline", (), "sig_t 0.5, |dt|<1.5, 2tau 3"),
                (0.9, 0.3, 0.9, 1, "nomline", (), "sig_t 0.3, |dt|<0.9, 2tau 1.8"),
                (0.6, 0.2, 0.6, 1, "nomline", (), "sig_t 0.2, |dt|<0.6, 2tau 1.2"),
                (2.5, 0.5, 1.5, 1e-2, "nomline", (), "baseline + mu veto 1e-2"),
                (0.6, 0.2, 0.6, 1e-2, "nomline", (), "sig_t 0.2 + mu veto 1e-2"),
                (2.5, 0.5, 1.5, 1, "xing_s", (), "per-event vertex (xing_s)"),
                (2.5, 0.5, 1.5, 1, "vline", (), "true vertex (ideal)"),
                (2.5, 0.5, 1.5, 1, "nomline", ("COS",), "no cosmics"),
                (2.5, 0.5, 1.5, 1, "nomline", ("COS", "ACC"), "no cosmics, no accidentals"),
                (2.5, 0.5, 1.5, 1, "nomline", ("COS", "G"), "no cosmics, no 3He(n,g)"),
                (2.5, 0.5, 1.5, 1, "nomline", ("ACC", "G", "COS", "WALL"), "IPC only"),
            ]
            variants[base:] = [(menu, ecut) + v for v in variants[base:]]
        for v in variants:
            menu, ecut, tau, sig, dtc, cs, est, zero, label = v
            cache = caches.setdefault((est, sig, dtc), {})
            R, s, n = scan(cfg, s1, tabs, menu, ecut, tau, est, zero, cache=cache, rng=rng,
                           sigma_t=sig, dt_cut=dtc, cos_scale=cs)
            rows.append(dict(cfg=cfg, menu=menu, ecut=ecut, variant=label, best_R=R, sigma_t=sig,
                             reach3=3 * s, **n))
            print(f"{cfg} {menu:6s} E>{ecut:4.1f} {label:40s} R {R:.2g}  3σ {3 * s:.2e}  "
                  f"IPC {n['M1'] + n['E0']:.3g}  ACC {n['ACC']:.3g}  COS {n['COS']:.3g}  G {n['G']:.3g}", flush=True)
    pd.DataFrame(rows).to_csv(a.out, index=False)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
