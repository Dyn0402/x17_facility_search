#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bkg_reach.py -- do big trigger slabs drown the ILL pair search in background?

Runs on lxplus next to the data (the tables are too big for the laptop):

    python3 bkg_reach.py --geoms asbuilt P2 P5 P5L P5B -o $E/TB/analysis

It reuses ill/sim_feasibility.py (same signal/background model, same Fisher
reach) and adds what a large, H-rich trigger slab at a reactor changes:

1. SLAB SINGLES.  Every simulated neutron that deposits energy in a slab
   (capture γ from the cell, the air, the frames; H(n,γ) 2.2 MeV inside the
   plastic itself; activation β) is a single, at R absorbed n/s.  Reported as
   rate per arm above thresholds, and as a spectrum.

2. PILE-UP IN THE ENERGY SUM.  The slab is read as one charge per arm, so any
   deposit inside the integration gate G is added to that arm's energy.  The
   number of foreign deposits per arm is Poisson(mu = R * G * r_slab) with
   energies from the singles spectrum (compound Poisson, built by FFT).  It is
   applied to the signal (sampled per lepton arm) and to every background
   (the Esum pass probability is averaged over the two-arm pile-up
   distribution), so single-neutron fakes at <= 10.8 MeV can be lifted over
   the Esum cut.  G = 0 reproduces sim_feasibility.

3. TRIGGER RATES.  Hardware two-arm trigger (SiPM wall >= 0.5 MIP in two arms;
   "strict": and slab >= 1.67 MeV), correlated + accidental in a 20 ns
   coincidence, and the Micromegas occupancy (gap rate, already in the model).

Geometries (all G1 cell):
  asbuilt  n_TOF stack, 16 SiPM bars, 2 x 20x30x2 cm plastics + LS (ILL campaign)
  P2       70x70x2 cm PVT,  20 bars, no LS          (TB runs)
  P5       75x75x5 cm PVT,  20 bars, no LS
  P5L      P5 + 2 mm 6LiF around each slab
  P5B      P5 + 2 mm B4C  around each slab
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from scipy.special import ndtr

HERE = Path(__file__).resolve().parent
for p in (HERE, HERE.parent / "ill"):
    if (p / "sim_feasibility.py").exists():
        sys.path.insert(0, str(p))
        break
import sim_feasibility as SF  # noqa: E402

E = Path("/eos/experiment/ntof/data/x17/ill")

# per geometry: S1 base + cfg name, contracts base + cfg name, K1 source
GEOMS = {
    "asbuilt": dict(s1=(E / "S1/summary", "G1"), c=(E / "contracts", "G1"),
                    k1=(E / "contracts", "G5")),
    "P2":  dict(s1=(E / "TB/summary", "P2"),  c=(E / "TB/contracts", "P2"),  k1=(E / "TB/contracts", "P2")),
    "P5":  dict(s1=(E / "TB/summary", "P5"),  c=(E / "TB/contracts", "P5"),  k1=(E / "TB/contracts", "P5")),
    "P5L": dict(s1=(E / "TB/summary", "P5L"), c=(E / "TB/contracts", "P5L"), k1=(E / "TB/contracts", "P5")),
    "P5B": dict(s1=(E / "TB/summary", "P5B"), c=(E / "TB/contracts", "P5B"), k1=(E / "TB/contracts", "P5")),
}

SCEN = {   # timing scenarios of ill/FEASIBILITY_SIM.md
    "base":   dict(tau_ns=2.5, sigma_t_ns=0.5, dt_cut_ns=1.5, cos_scale=1.0),
    "timing": dict(tau_ns=0.6, sigma_t_ns=0.2, dt_cut_ns=0.6, cos_scale=0.01),
}
R_MAX = 1.9e10                   # beam maximum, absorbed n/s
DX = 0.05                        # MeV, singles / pile-up grid
NX = 1600                        # 0 .. 80 MeV
X = np.arange(NX) * DX
E_MIN = 0.02                     # MeV, a slab deposit counted as a pile-up pulse
HW_2TAU_NS = 20.0                # hardware coincidence window
THRS = (0.1, 0.5, 1.0, 1.67, 3.0, 5.0, 8.0, 11.0)


# --------------------------------------------------------------------------- #
# slab singles and pile-up
# --------------------------------------------------------------------------- #
def slab_E(t, tag="a"):
    """Per (event, arm) energy in the slab-type counters (plastic + LS)."""
    return (t[f"plast_{tag}"] + t[f"ls_{tag}"]).astype(np.float64)


def singles_spectrum(t):
    """Arm-averaged slab deposits per absorbed neutron per arm, on the X grid
    (bin i = [X_i, X_i + DX)).  All times: a reactor is a steady state."""
    e = slab_E(t)
    w = t["w"].astype(float)[:, None] * np.ones_like(e)
    m = e > E_MIN
    h, _ = np.histogram(e[m], np.r_[X, X[-1] + DX], weights=w[m])
    return h / t["absorbed"] / 4.0


def pileup_pmf(spec, mu_scale, narms=1):
    """pmf on X of the summed foreign energy in `narms` independent arms, with
    mu = mu_scale * (rate per abs n per arm) * ... folded in by the caller:
    mu_scale = R * G.  Compound Poisson via FFT on a 2x padded grid."""
    r = spec.sum()
    mu = mu_scale * r * narms
    if mu <= 0 or r <= 0:
        out = np.zeros(NX)
        out[0] = 1.0
        return out, 0.0
    p1 = np.zeros(2 * NX)
    p1[:NX] = spec / r
    F = np.fft.rfft(p1)
    pu = np.fft.irfft(np.exp(mu * (F - 1.0)), 2 * NX)[:NX]
    pu = np.clip(pu, 0, None)
    pu /= pu.sum()
    return pu, mu / narms


class PileUp:
    """The pile-up state SF's patched functions read."""
    x2 = np.array([0.0])
    q2 = np.array([1.0])
    pmf1 = None
    margin = 0.0
    tag = "none"

    @classmethod
    def set(cls, spec, R, gate_ns, tag):
        cls.tag = tag
        if gate_ns <= 0:
            cls.x2, cls.q2, cls.pmf1, cls.margin = np.array([0.0]), np.array([1.0]), None, 0.0
            return 0.0
        s = R * gate_ns * 1e-9
        p1, mu = pileup_pmf(spec, s, 1)
        p2, _ = pileup_pmf(spec, s, 2)
        # two-arm sum: rebin to 0.2 MeV (bin centres), drop < 1e-9
        k = 4
        q = p2[: NX // k * k].reshape(-1, k).sum(1)
        xc = (np.arange(len(q)) * k + 0.5 * k) * DX
        xc[0] = 0.0 if p2[0] > 0.5 * q[0] else xc[0]
        keep = q > 1e-9
        cls.x2, cls.q2 = xc[keep], q[keep] / q[keep].sum()
        cls.pmf1 = p1
        c = np.cumsum(cls.q2)
        cls.margin = float(cls.x2[min(np.searchsorted(c, 1 - 1e-7), len(c) - 1)])
        # P(pass) = sum_k q_k ndtr((b + x_k)/s), b = e1 + e2 - ecut: tabulated
        # on (log s, b) and interpolated bilinearly (the direct sum is ~100x slower)
        cls.ls = np.linspace(math.log(0.05), math.log(8.0), 60)
        lo = -cls.margin - 45.0
        cls.b = np.arange(lo, 45.0, 0.02)
        S = np.exp(cls.ls)[:, None]
        T = np.zeros((len(cls.ls), len(cls.b)))
        for x, q in zip(cls.x2, cls.q2):
            T += q * ndtr((cls.b[None, :] + x) / S)
        cls.T = T
        return mu


_orig_pass_prob = SF.pass_prob
_orig_margin = SF.ecut_margin


def pass_prob_pu(e1, e2, ecut):
    if ecut <= 0:
        return np.ones(np.broadcast(e1, e2).shape)
    s = np.maximum(np.sqrt(SF.eres_var(e1) + SF.eres_var(e2)), 1e-9)
    b = e1 + e2 - ecut
    if len(PileUp.q2) == 1:
        return ndtr(b / s)
    P = PileUp
    u = np.clip((np.log(s) - P.ls[0]) / (P.ls[1] - P.ls[0]), 0, len(P.ls) - 1.001)
    v = np.clip((b - P.b[0]) / (P.b[1] - P.b[0]), 0, len(P.b) - 1.001)
    i, j = u.astype(int), v.astype(int)
    fu, fv = u - i, v - j
    T = P.T
    return ((1 - fu) * ((1 - fv) * T[i, j] + fv * T[i, j + 1])
            + fu * ((1 - fv) * T[i + 1, j] + fv * T[i + 1, j + 1]))


def ecut_margin_pu(ecut):
    return _orig_margin(ecut) + (PileUp.margin if ecut > 0 else 0.0)


_rng = np.random.default_rng(23)


def s1_select_pu(z, menu, ecut):
    """sim_feasibility.s1_select with foreign slab energy added to each lepton
    arm before the resolution smearing."""
    if z.get("_pu_tag") != PileUp.tag:
        n = len(z["E_sipm_em"])
        if PileUp.pmf1 is None:
            a = b = np.zeros(n)
        else:
            cdf = np.cumsum(PileUp.pmf1)
            a = X[np.searchsorted(cdf, _rng.random(n) * cdf[-1])] + 0.5 * DX
            b = X[np.searchsorted(cdf, _rng.random(n) * cdf[-1])] + 0.5 * DX
            a[a < DX] = 0
            b[b < DX] = 0
        z["_e_em"] = SF.smear_E(z["E_sipm_em"] + z["E_plast_em"] + z["E_ls_em"] + a)
        z["_e_ep"] = SF.smear_E(z["E_sipm_ep"] + z["E_plast_ep"] + z["E_ls_ep"] + b)
        z["_pu_tag"] = PileUp.tag
    e_em, e_ep = z["_e_em"], z["_e_ep"]
    if menu == "strict":
        m = SF.legs_count(z["legs"]) >= 2
    elif menu == "sipm2":
        m = (z["E_sipm_em"] > SF.SIPM_THR) & (z["E_sipm_ep"] > SF.SIPM_THR)
    else:
        m = np.ones(len(e_em), bool)
    return m & (e_em + e_ep > ecut)


EB = np.arange(0.0, 40.0001, 0.25)            # accidental energy classes [MeV]
_ACC_CACHE = {}


def accidental_hist_pu(S, ecut, rng=None):
    """sim_feasibility.accidental_hist for any pile-up state.  With pile-up the
    Esum pre-cut falls to ~0, so every pair of singles counts (~1e9 per point).
    The pair weights are therefore histogrammed once per singles set in
    (E_a class, E_b class, chord angle), with 0.25 MeV classes carrying their
    weighted mean energy, and each pile-up state only applies P(pass)."""
    key = tuple((len(S[a][0]), float(S[a][0].sum())) for a in range(4))
    if key not in _ACC_CACHE:
        nE, nT = len(EB) - 1, len(SF.CENTRES)
        H = {}
        for a in range(4):
            for b in range(a + 1, 4):
                wa, ea, pa = S[a]
                wb, eb, pb = S[b]
                ia = np.clip(np.digitize(ea, EB) - 1, 0, nE - 1)
                ib = np.clip(np.digitize(eb, EB) - 1, 0, nE - 1)
                acc = np.zeros(nE * nE * nT)
                ua = pa / np.linalg.norm(pa, axis=1, keepdims=True)
                ub = pb / np.linalg.norm(pb, axis=1, keepdims=True)
                b0, bw = SF.BINS[0], SF.BINS[1] - SF.BINS[0]     # uniform angle bins
                step = max(1, 10_000_000 // max(len(wb), 1))
                for i0 in range(0, len(wa), step):
                    sl = slice(i0, i0 + step)
                    th = np.degrees(np.arccos(np.clip(ua[sl] @ ub.T, -1, 1)))
                    it = np.floor((th - b0) / bw).astype(np.int64)
                    ok = (it >= 0) & (it < nT)
                    idx = (ia[sl][:, None] * nE + ib[None, :]) * nT + it
                    ww = wa[sl][:, None] * wb[None, :]
                    acc += np.bincount(idx[ok], ww[ok], minlength=nE * nE * nT)
                Ea = np.bincount(ia, wa * ea, nE) / np.maximum(np.bincount(ia, wa, nE), 1e-300)
                Eb = np.bincount(ib, wb * eb, nE) / np.maximum(np.bincount(ib, wb, nE), 1e-300)
                H[(a, b)] = (acc.reshape(nE, nE, nT), Ea, Eb)
        _ACC_CACHE[key] = H
    h = np.zeros(len(SF.CENTRES))
    for (a, b), (Hab, Ea, Eb) in _ACC_CACHE[key].items():
        P = pass_prob_pu(Ea[:, None], Eb[None, :], ecut)
        h += np.einsum("ijt,ij->t", Hab, P)
    return h


SF.accidental_hist = accidental_hist_pu
SF.pass_prob = pass_prob_pu
SF.ecut_margin = ecut_margin_pu
SF.s1_select = s1_select_pu


# --------------------------------------------------------------------------- #
# trigger rates
# --------------------------------------------------------------------------- #
def trigger_rates(t, k1):
    """Per absorbed neutron (beam) and per live second (cosmics)."""
    w = t["w"].astype(float)
    A = t["absorbed"]
    s_ok = t["sipm_a"] > SF.SIPM_THR
    p_ok = slab_E(t) > SF.PLAST_THR
    out = {}
    for name, leg in (("sipm2", s_ok), ("strict", s_ok & p_ok)):
        out[f"{name}.corr"] = float(w[leg.sum(1) >= 2].sum() / A)
        out[f"{name}.single_arm"] = ((w[:, None] * leg).sum(0) / A).tolist()
    e = slab_E(t)
    for thr in THRS:
        out[f"slab>{thr:g}"] = float((w[:, None] * (e > thr)).sum() / A / 4)
    out["slab_any"] = float((w[:, None] * (e > E_MIN)).sum() / A / 4)
    if k1 is not None:
        live = k1["N_sim"] * SF.COSMIC_S_PER_MU
        ek = slab_E(k1)
        out["cos.slab>1.67_per_s_arm"] = float((ek > SF.PLAST_THR).sum() / live / 4)
        sk = k1["sipm_a"] > SF.SIPM_THR
        out["cos.sipm2_per_s"] = float((sk.sum(1) >= 2).sum() / live)
        out["cos.strict_per_s"] = float(((sk & (ek > SF.PLAST_THR)).sum(1) >= 2).sum() / live)
    return out


def trig_at(tr, R):
    """Hardware trigger rates [Hz] at R absorbed n/s."""
    res = {}
    for name in ("sipm2", "strict"):
        r = np.array(tr[f"{name}.single_arm"]) * R
        acc = sum(r[a] * r[b] for a in range(4) for b in range(a + 1, 4)) * HW_2TAU_NS * 1e-9
        res[name] = dict(corr=tr[f"{name}.corr"] * R, acc=acc,
                         cos=tr.get(f"cos.{name}_per_s", float("nan")))
    res["slab_per_arm"] = {f">{thr:g}": tr[f"slab>{thr:g}"] * R for thr in THRS}
    res["slab_per_arm"]["any"] = tr["slab_any"] * R
    return res


# --------------------------------------------------------------------------- #
def load_geom(g):
    G = GEOMS[g]
    s1 = {c: SF.load_s1(G["s1"][0], G["s1"][1], c) for c in ("X17", "M1", "E0")}
    tabs = {r: SF.load_table(G["c"][0], r, G["c"][1]) for r in ("C1", "C1w", "C1g")}
    tabs["K1"] = SF.load_table(G["k1"][0], "K1", G["k1"][1])
    return s1, tabs


def scale_air(tabs, f):
    """Weight every neutron captured in air ('World': 14N(n,γ), 10.8 MeV) by f.
    f = 0.1 is the He / vacuum flight tube (he4_bag/: ~90 % of the air
    captures are the direct beam between the aperture and the window)."""
    for t in tabs.values():
        if t is None or "capvol" not in t:
            continue
        if "_w0" not in t:
            t["_w0"] = t["w"].copy()
        t["w"] = np.where(t["capvol"] == "World", t["_w0"] * f, t["_w0"]).astype(np.float32)


def run_geom(g, gates, menus, ecuts, rates, days, air=1.0):
    t0 = time.time()
    s1, tabs = load_geom(g)
    scale_air({k: v for k, v in tabs.items() if k != "K1"}, air)
    miss = [k for k, v in {**s1, **tabs}.items() if v is None]
    if any(s1[c] is None for c in s1) or tabs["C1"] is None:
        print(f"{g}: missing {miss}, skipped", flush=True)
        return None
    if miss:
        print(f"{g}: missing {miss}", flush=True)
    c1 = SF.concat([tabs.get("C1"), tabs.get("C1w")])
    spec = singles_spectrum(c1)
    tr = trigger_rates(c1, tabs["K1"])
    out = dict(geom=g, air=air, spectrum=spec.tolist(), dx=DX, trig=tr, gap_arm=SF.gap_rate_per_arm(c1),
               budget=json.load(open(G_acc(g)))["per_absorbed"] if G_acc(g).exists() else {},
               rows=[])
    print(f"{g} air×{air:g}: slab singles per arm per abs n: any {tr['slab_any']:.3g}, >1.67 MeV "
          f"{tr['slab>1.67']:.3g}; gap/arm {out['gap_arm']:.3g}  ({time.time() - t0:.0f} s)", flush=True)
    for sc, P in SCEN.items():
        for gate in gates:
            for menu in menus:
                for ecut in ecuts:
                    cache = {} if gate == 0 else None
                    row = []
                    for R in rates:
                        mu = PileUp.set(spec, R, gate, f"{g}/{gate}/{R:g}")
                        mod = SF.model(g, s1, tabs, menu, ecut, R, days, P["tau_ns"],
                                       P["sigma_t_ns"], P["dt_cut_ns"], cache=cache)
                        mod["COS"] = mod["COS"] * P["cos_scale"]
                        s = SF.reach(mod)
                        row.append(dict(R=R, sigma=s, mu_pu=mu, occ=mod["occ"],
                                        **{k: float(np.sum(mod[k])) for k in
                                           ("X17", "M1", "E0", "G", "WALL", "ACC", "COS")}))
                    b = min(row, key=lambda r: r["sigma"])
                    out["rows"].append(dict(scen=sc, gate_ns=gate, menu=menu, ecut=ecut,
                                            best=b, scan=row, trig=trig_at(tr, b["R"])))
                    print(f"  {g:7s} air{air:g} {sc:6s} G={gate:3g} ns {menu:6s} E>{ecut:g}: R {b['R']:.2g} "
                          f"3σ {3 * b['sigma']:.2e} | X17ref {SF.X17_REF * b['X17']:.0f} IPC "
                          f"{b['M1'] + b['E0']:.0f} G {b['G']:.0f} acc {b['ACC']:.0f} cos {b['COS']:.0f} "
                          f"wall {b['WALL']:.0f} | occ {b['occ']:.2f} mu_pu {b['mu_pu']:.2f} "
                          f"({time.time() - t0:.0f} s)", flush=True)
    return out


def G_acc(g):
    return GEOMS[g]["c"][0] / f"C1_{GEOMS[g]['c'][1]}" / "accounting.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geoms", nargs="+", default=list(GEOMS))
    ap.add_argument("--gates", nargs="+", type=float, default=[0, 50, 100])
    ap.add_argument("--menus", nargs="+", default=["sipm2", "strict"])
    ap.add_argument("--ecuts", nargs="+", type=float, default=[13.0])
    ap.add_argument("--nrates", type=int, default=10)
    ap.add_argument("--days", type=float, default=50.0)
    ap.add_argument("--air", nargs="+", type=float, default=[1.0],
                    help="scale on air (14N) captures; 0.1 = He flight tube")
    ap.add_argument("-o", "--outdir", type=Path, required=True)
    a = ap.parse_args()
    a.outdir.mkdir(parents=True, exist_ok=True)
    rates = np.logspace(9, math.log10(R_MAX), a.nrates)
    for g in a.geoms:
        for air in a.air:
            r = run_geom(g, a.gates, a.menus, a.ecuts, rates, a.days, air)
            if r is not None:
                f = a.outdir / (f"{g}.json" if air == 1 else f"{g}_air{air:g}.json")
                f.write_text(json.dumps(r, default=float))
                print(f"wrote {f}", flush=True)


if __name__ == "__main__":
    main()
