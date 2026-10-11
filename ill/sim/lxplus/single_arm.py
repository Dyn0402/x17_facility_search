#!/usr/bin/env python3
"""
single_arm.py -- what a single-arm trigger would cost and buy at the ILL (G1).

Every reach so far uses a two-arm trigger (a per-arm SiPM x plastic leg in two
different arms) and fits 60-180 deg, so the small-angle part of the pair
spectrum (both leptons in one arm) is never recorded.  Here, for a single-arm
trigger "one arm with a leg (SiPM AND plastic >= 0.5 MIP) and E_arm > T":

  signal   S1 G1_{X17,M1,E0} parts: per channel, the fraction of pairs with both
           leptons in the gap of ONE arm, a leg there, E_arm > T and the two
           first gap hits >= SEP mm apart (two resolvable tracks); and the
           two-arm reference (the present pair-tag).  Opening-angle spectra
           0-180 deg (true, and the chord to the origin) for both.
  trigger  per absorbed n, per variant (C1 + C1w biased-only + the C1g
           ³He(n,γ) rows, which the two-arm trigger model leaves out), and
           cosmics per second (K1): rate of events with >= 1 arm passing.
  (n,γ)    the C1g ³He(n,γ) rows that fire one arm with MM charge: the 20.6 MeV
           γ converting in front of / in an arm.  The tables keep no
           per-arm track count, so this is the background BEFORE any
           two-track requirement (an upper bound on the same-arm EPC fakes).

Output: <out>_{signal,trigger,theta}.csv.  Light enough for the login node but
run under condor (cons_submit-style) to respect the lxplus rules.

    python3 single_arm.py -o $E/analysis/single_arm/sa
"""
from __future__ import annotations

import argparse
import glob
from pathlib import Path

import numpy as np
import pandas as pd

import conservative as C
import sim_feasibility as SF

E = C.E
T_LIST = (0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 13.0, 14.0, 16.0)
SEP_MM = (0.0, 5.0, 10.0)
VARIANTS = ("ringCFRP", "tubeBe", "tubeBe25", "tubeMy")
TH_BINS = np.arange(0.0, 181.0, 4.0)
PER_ABS = dict(X17=SF.M1_PER_ABS, M1=SF.M1_PER_ABS, E0=SF.E0_PER_ABS)   # X17 at X17/IPC = 1


def chord(p1, p2):
    c = (p1 * p2).sum(-1) / (np.linalg.norm(p1, axis=-1) * np.linalg.norm(p2, axis=-1))
    return np.degrees(np.arccos(np.clip(c, -1, 1)))


def signal(out):
    rows, th_rows = [], []
    for ch in ("X17", "M1", "E0"):
        acc = {}
        hist = {}
        N = 0
        for p in sorted(glob.glob(str(E / "S1" / f"G1_{ch}" / "parts" / "*.npz"))):
            z = np.load(p)
            N += len(z["eventID"])
            am, ap = z["em_arm"].astype(int), z["ep_arm"].astype(int)
            legs = z["legs"].astype(int) & 0xF
            Ea = z["E_sipm"] + z["E_plast"] + z["E_ls"]           # MeV per arm, all particles
            th = z["theta"].astype(float)
            sep = np.linalg.norm(z["em_P"] - z["ep_P"], axis=1)
            rc = chord(z["em_P"].astype(float), z["ep_P"].astype(float))
            r = np.arange(len(am))
            same = (am >= 0) & (am == ap)
            a = np.where(same, am, 0)
            leg_same = same & (((legs >> a) & 1) == 1)
            E_same = np.where(same, Ea[r, a], 0.0)
            two = (am >= 0) & (ap >= 0) & (am != ap)
            nleg = sum((legs >> k) & 1 for k in range(4))
            E_two = np.where(two, Ea[r, np.clip(am, 0, 3)] + Ea[r, np.clip(ap, 0, 3)], 0.0)
            for T in T_LIST:
                for s in SEP_MM:
                    k = ("same", T, s)
                    m = leg_same & (E_same > T) & (sep >= s)
                    acc[k] = acc.get(k, 0) + m.sum()
                    if T in (0.0, 13.0) and s == 5.0:
                        hist[(T, "true")] = hist.get((T, "true"), 0) + np.histogram(th[m], TH_BINS)[0]
                        hist[(T, "chord")] = hist.get((T, "chord"), 0) + np.histogram(rc[m], TH_BINS)[0]
                k = ("two", T, 0.0)
                m = two & (nleg >= 2) & (E_two > T)
                acc[k] = acc.get(k, 0) + m.sum()
                if T == 13.0:
                    hist[("two13", "true")] = hist.get(("two13", "true"), 0) + np.histogram(th[m], TH_BINS)[0]
                    hist[("two13", "chord")] = hist.get(("two13", "chord"), 0) + np.histogram(rc[m], TH_BINS)[0]
            hist[("all", "true")] = hist.get(("all", "true"), 0) + np.histogram(th, TH_BINS)[0]
        for (kind, T, s), n in acc.items():
            rows.append(dict(channel=ch, kind=kind, T=T, sep_mm=s, frac=n / N, n=int(n),
                             per_abs=n / N * PER_ABS[ch]))
        for (sel, est), h in hist.items():
            for lo, v in zip(TH_BINS[:-1], h):
                th_rows.append(dict(channel=ch, sel=str(sel), est=est, th_lo=lo, frac=v / N))
        print(f"{ch}: N {N}; same-arm (leg, T=0, sep 5) {acc[('same', 0.0, 5.0)] / N:.4f}, "
              f"(T=13) {acc[('same', 13.0, 5.0)] / N:.4f}; two-arm (T=13) {acc[('two', 13.0, 0.0)] / N:.4f}",
              flush=True)
    pd.DataFrame(rows).to_csv(f"{out}_signal.csv", index=False)
    pd.DataFrame(th_rows).to_csv(f"{out}_theta.csv", index=False)


def arm_pass(t, T, tag="a"):
    ok = (t[f"sipm_{tag}"] > SF.SIPM_THR) & (t[f"plast_{tag}"] > SF.PLAST_THR)
    Ea = (t[f"sipm_{tag}"] + t[f"plast_{tag}"] + t[f"ls_{tag}"]).astype(float)
    return ok & (Ea > T)


def trigger(out):
    rows = []
    g = SF.load_table(E / "contracts", "C1g", "G1")
    he = SF.he3ng_rows(g)
    for v in VARIANTS:
        c1 = SF.load_table(E / "contracts", "C1", f"G1_{v}")
        c1w = SF.load_table(E / "contracts", "C1w", f"G1_{v}")
        C.use_biased_only(c1, c1w)
        c = SF.concat([c1, c1w])
        nohe = ~SF.he3ng_rows(c)
        w = c["w"].astype(float)
        corr2, per_arm = SF.trigger_rates(c, "strict")
        for T in T_LIST:
            p = arm_pass(c, T)
            any1 = p.any(1) & nohe
            ge2 = (p.sum(1) >= 2) & nohe
            pg = arm_pass(g, T)
            g1 = pg.any(1) & he
            g1mm = (pg & (g["gap"] > SF.GAP_THR)).any(1) & he
            rows.append(dict(variant=v, T=T,
                             single_per_abs=float(w[any1].sum() / c["absorbed"]),
                             two_arm_corr_per_abs=float(w[ge2].sum() / c["absorbed"]),
                             per_arm_singles_per_abs=float((w[:, None] * (p & nohe[:, None])).sum() / c["absorbed"] / 4),
                             he3ng_single_per_abs=float(g["w"][g1].astype(float).sum() / g["absorbed"]),
                             he3ng_single_mm_per_abs=float(g["w"][g1mm].astype(float).sum() / g["absorbed"])))
            print(f"{v:9s} T {T:4.1f}  single {rows[-1]['single_per_abs']:.3e}/n  "
                  f"³He(n,γ) single {rows[-1]['he3ng_single_per_abs']:.3e}/n (with MM {rows[-1]['he3ng_single_mm_per_abs']:.3e})",
                  flush=True)
        print(f"{v}: two-arm hw trigger model (strict, T=0, C1+C1w only): corr {corr2:.3e}/n", flush=True)
    k = SF.load_table(E / "contracts", "K1", "G5")
    live = k["N_sim"] * SF.COSMIC_S_PER_MU
    for T in T_LIST:
        p = arm_pass(k, T)
        rows.append(dict(variant="cosmics_K1", T=T, single_Hz=float(p.any(1).sum() / live),
                         two_arm_Hz=float((p.sum(1) >= 2).sum() / live)))
        print(f"cosmics T {T:4.1f}: single-arm {rows[-1]['single_Hz']:.1f} Hz, two-arm {rows[-1]['two_arm_Hz']:.2f} Hz",
              flush=True)
    pd.DataFrame(rows).to_csv(f"{out}_trigger.csv", index=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", required=True, help="output prefix")
    ap.add_argument("--only", choices=("signal", "trigger"), default=None)
    a = ap.parse_args()
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    if a.only in (None, "trigger"):
        trigger(a.out)
    if a.only in (None, "signal"):
        signal(a.out)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
