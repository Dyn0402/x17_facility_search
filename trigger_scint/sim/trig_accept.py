#!/usr/bin/env python3
"""
trig_accept.py -- acceptance x efficiency of every trigger-scintillator option
==============================================================================
    python3 trig_accept.py --t0 <T0 parts dir> --t1 <T1 parts dir> -o <outdir>

Input: trig_reduce.py parts for T0 (as-built stack, all 20 SiPM bars in the
geometry) and T1 (oversized 78 x 120 x 10 cm slab per arm, no LS), channels
X17 and M1 (G1 cell, ILL beam vertex library).  Every number is per generated
pair.

Per lepton arm:
  MM      first drift-gas hit inside the measured active area
          |u| < 199.7 mm, |v| < 180 mm (SimConfig mm_size_u/v)
  SiPM    edep summed over the read bars > 0.5 MIP (0.2376 MeV); "16" = the
          n_TOF read-out window (bars 1-16), "20" = every bar
  trigger scintillator (plastic / LS) > THR (0.5 MIP of 2 cm PVT, 1.67 MeV,
          the ILL "strict" leg threshold)
  Esum    SiPM + plastic (+ LS), each arm smeared by 10 %/sqrt(E) (+) 5 %
          (the ILL campaign's assumed resolution)
"""
import argparse
import glob
import json
from pathlib import Path

import numpy as np

SIPM_THR = 0.5 * 0.4751
THR = 0.5 * 3.3494
ERES = (0.10, 0.05)
MM_U, MM_V = 199.7, 180.0
BARS16 = np.arange(1, 17)


def load(d, ch):
    parts = sorted(glob.glob(f"{d}/G1_{ch}/parts/*.npz"))
    R = {}
    N = 0
    for p in parts:
        z = np.load(p)
        N += int(z["n_generated"][0])
        for k in z.files:
            if k in ("n_generated", "big", "W_cm", "L_cm", "T_cm"):
                R[k] = z[k]
                continue
            R.setdefault(k, []).append(z[k])
    R = {k: (np.concatenate(v) if isinstance(v, list) else v) for k, v in R.items()}
    R["N"] = N
    return R


def smear(E, rng):
    A, B = ERES
    s = np.sqrt(A * A * np.clip(E, 1e-9, None) + (B * E) ** 2)
    return np.clip(E + s * rng.standard_normal(E.shape), 0, None)


def mm_ok(R, p):
    u, v = R[f"{p}_gap_uv"][:, 0], R[f"{p}_gap_uv"][:, 1]
    return (np.abs(u) < MM_U) & (np.abs(v) < MM_V)


def sipm(R, p, nbars):
    s = R[f"{p}_sipm"]
    return s[:, BARS16].sum(1) if nbars == 16 else s.sum(1)


def summarize(R, legs, esum, rng):
    """legs: per-lepton bool pairs (em, ep); esum: (E_em, E_ep) true."""
    m = legs[0] & legs[1]
    es = smear(esum[0], rng) + smear(esum[1], rng)
    N = R["N"]
    th = R["theta"]
    out = dict(acc=m.sum() / N,
               acc_E12=(m & (es > 12)).sum() / N,
               acc_E13=(m & (es > 13)).sum() / N,
               n=int(m.sum()))
    # in the X17 signal window of the reconstructed... use truth 100-180 deg
    w = (th >= 100)
    out["acc_th100"] = (m & w).sum() / N
    return out


def t0_options(R, rng):
    o = {}
    mm = [mm_ok(R, p) for p in ("em", "ep")]
    s16 = [sipm(R, p, 16) for p in ("em", "ep")]
    s20 = [sipm(R, p, 20) for p in ("em", "ep")]
    pl = [R[f"{p}_plastL"] + R[f"{p}_plastR"] for p in ("em", "ep")]
    ls = [R[f"{p}_ls"] for p in ("em", "ep")]
    e16 = [s16[i] + pl[i] + ls[i] for i in range(2)]
    e20 = [s20[i] + pl[i] + ls[i] for i in range(2)]
    L = lambda f: [f(i) for i in range(2)]          # noqa: E731
    o["MM only (ceiling)"] = summarize(R, L(lambda i: mm[i]), e20, rng)
    o["MM + SiPM16"] = summarize(R, L(lambda i: mm[i] & (s16[i] > SIPM_THR)), e16, rng)
    o["MM + SiPM20"] = summarize(R, L(lambda i: mm[i] & (s20[i] > SIPM_THR)), e20, rng)
    o["n_TOF as built: MM + SiPM16 + 2cm plastics"] = summarize(
        R, L(lambda i: mm[i] & (s16[i] > SIPM_THR) & (pl[i] > THR)), e16, rng)
    o["as built, SiPM20 + 2cm plastics"] = summarize(
        R, L(lambda i: mm[i] & (s20[i] > SIPM_THR) & (pl[i] > THR)), e20, rng)
    o["LS working: MM + SiPM20 + LS"] = summarize(
        R, L(lambda i: mm[i] & (s20[i] > SIPM_THR) & (ls[i] > THR)), e20, rng)
    o["LS working: MM + SiPM20 + (plastic OR LS)"] = summarize(
        R, L(lambda i: mm[i] & (s20[i] > SIPM_THR) & ((pl[i] > THR) | (ls[i] > THR))), e20, rng)
    o["LS, no SiPM: MM + LS"] = summarize(R, L(lambda i: mm[i] & (ls[i] > THR)), e20, rng)
    return o


def t1_scan(R, rng):
    W, Lc, T = R["W_cm"], R["L_cm"], R["T_cm"]
    mm = [mm_ok(R, p) for p in ("em", "ep")]
    s20 = [sipm(R, p, 20) for p in ("em", "ep")]
    s16 = [sipm(R, p, 16) for p in ("em", "ep")]
    g = [R[f"{p}_grid"] for p in ("em", "ep")]
    rows = []
    for iw, w in enumerate(W):
        for il, l in enumerate(Lc):
            for it, t in enumerate(T):
                pl = [g[i][:, iw, il, it] for i in range(2)]
                for req_sipm, s in (("SiPM20", s20), ("SiPM16", s16), ("none", None)):
                    if req_sipm == "SiPM16" and not (it == 1):
                        continue           # the 16-bar variant only at T = 2 cm
                    legs = [mm[i] & (pl[i] > THR) & ((s[i] > SIPM_THR) if s is not None else True)
                            for i in range(2)]
                    es = [(s20[i] if s is None else s[i]) + pl[i] for i in range(2)]
                    r = summarize(R, legs, es, rng)
                    rows.append(dict(W_cm=float(w), L_cm=float(l), T_cm=float(t), sipm=req_sipm, **r))
    # ceilings in the T1 geometry
    ceil = {"MM only": summarize(R, mm, s20, rng),
            "MM + SiPM20": summarize(R, [mm[i] & (s20[i] > SIPM_THR) for i in range(2)], s20, rng),
            "MM + SiPM16": summarize(R, [mm[i] & (s16[i] > SIPM_THR) for i in range(2)], s16, rng)}
    return rows, ceil


def entry_hist(R):
    """Where accepted leptons enter the slab (u, v), for the optics weighting."""
    uv = np.concatenate([R["em_ent_uv"], R["ep_ent_uv"]])
    ok = np.isfinite(uv[:, 0])
    H, xe, ye = np.histogram2d(uv[ok, 0] / 10, uv[ok, 1] / 10, bins=[np.arange(-40, 41, 2), np.arange(-60, 61, 4)])
    return H, xe, ye


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t0", required=True)
    ap.add_argument("--t1", required=True)
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(17)
    res = {}
    import csv
    for ch in ("X17", "M1"):
        R0 = load(a.t0, ch)
        R1 = load(a.t1, ch)
        o0 = t0_options(R0, rng)
        rows, ceil = t1_scan(R1, rng)
        res[ch] = dict(N_T0=R0["N"], N_T1=R1["N"], T0=o0, T1_ceilings=ceil)
        with open(out / f"scan_{ch}.csv", "w", newline="") as f:
            wr = csv.DictWriter(f, fieldnames=list(rows[0]))
            wr.writeheader()
            wr.writerows(rows)
        H, xe, ye = entry_hist(R1)
        np.savez(out / f"entry_{ch}.npz", H=H, xe=xe, ye=ye)
        # depth profile of the deposit: fraction of the 10 cm deposit within T (accepted leptons)
        g = np.concatenate([R1["em_grid"][:, -1, -1, :], R1["ep_grid"][:, -1, -1, :]])
        ke = np.concatenate([R1["em_ke"], R1["ep_ke"]])
        res[ch]["depth"] = {f"{lo}-{hi}": [float(np.mean(g[(ke >= lo) & (ke < hi) & (g[:, -1] > THR), it]))
                                           for it in range(len(R1["T_cm"]))]
                            for lo, hi in ((2, 4), (4, 6), (6, 8), (8, 10), (10, 12), (12, 14), (14, 17))}
        res[ch]["T_cm"] = R1["T_cm"].tolist()
        print(ch, json.dumps({k: round(v["acc"], 4) for k, v in o0.items()}, indent=1))
        print(ch, "ceilings", {k: round(v["acc"], 4) for k, v in ceil.items()})
    json.dump(res, open(out / "summary.json", "w"), indent=1)


if __name__ == "__main__":
    main()
