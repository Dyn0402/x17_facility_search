#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sim_feasibility.py -- can the ILL cell see an X17?  From the Geant4 campaign.

    python ill/sim_feasibility.py                    # ill/sim/{S1,contracts}
    python ill/sim_feasibility.py --s1 ill/sim/s1test --write

Inputs (copied from /eos/experiment/ntof/data/x17/ill/):
  sim/S1/<cfg>_<ch>/events.npz     ill_pairs.py merge dump, ch = X17, M1, E0
  sim/contracts/<run>_<cfg>/       ill_accounting.py merge: accounting.json and
                                   table.npz (per event, per arm: gap charge,
                                   SiPM / plastic / LS energy, gap centroid,
                                   first scintillator time), runs C1, C1w, C1g, K1

THE MODEL.  The observable is the reconstructed opening angle (vertex-to-hit
chord, "nomline": vertex assumed at the detector centre) of two-arm events
passing a trigger menu and a cut on the energy deposited in the two lepton
arms' scintillators.  Expected counts per bin,

    n_i = mu*X17_i + a*M1_i + b*E0_i + c*G_i  +  ACC_i + COS_i + WALL_i

  X17, M1, E0  S1 (Born-level ³He internal pairs, yields per absorbed neutron
               from ill_rates: M1 0.2014 ub, E0 0.0552 ub over sigma_np 5333 b);
               mu = X17/IPC(M1)
  G            fakes from the ³He(n,γ) 20.6 MeV photon itself (Compton +
               conversion in two arms), C1g (³He(n,γ) biased 1e7)
  ACC          accidentals: two single arms (MM charge + SiPM) from different
               neutrons within 2*tau, R^2 * 2tau * sum_ij p_i p_j, energies and
               angles paired event by event (C1 + C1w singles)
  COS          cosmics (K1), after the arm-to-arm timing cut
  WALL         every other single-neutron fake (C1 + C1w); kinematically
               bounded by the hardest capture line (14N, 10.8 MeV)

mu, a, b, c float; ACC and COS are measured off-time / beam-off and enter as
known (they add variance only).  sigma(mu) from the inverse Fisher matrix at
mu = 0 (Asimov); the k-sigma reach in X17/IPC(M1) is k*sigma(mu).

Efficiency loss at rate R: Micromegas occupancy, P(no foreign hit in either
lepton arm within the 1 us drift window).  It applies to every class, since
accidental, cosmic and wall pairs also need two clean tracks (before 2026-10-08
only the signal side carried it, which made §11/§12 pessimistic).
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy.special import ndtr

np.seterr(invalid="ignore")

HERE = Path(__file__).resolve().parent
SIGMA_NP_B = 5333.0
M1_PER_ABS = 0.2014e-6 / SIGMA_NP_B
E0_PER_ABS = 0.05519e-6 / SIGMA_NP_B
X17_REF = 2.5e-2                     # rate table's X17/IPC(M1) -- reference only
DAY = 86400.0
CONFIGS = ("G1", "G2", "G3", "G4", "G5", "G6")
SIPM_THR = 0.5 * 0.4751              # MeV, 0.5 MIP
PLAST_THR = 0.5 * 3.3494
GAP_THR = 1e-3                       # MeV, Tier A
MM_WINDOW_S = 1.0e-6
COSMIC_S_PER_MU = 6.667e-4           # K1 live seconds per simulated muon
BINS = np.arange(40.0, 181.0, 4.0)
CENTRES = 0.5 * (BINS[1:] + BINS[:-1])


# --------------------------------------------------------------------------- #
# loading
# --------------------------------------------------------------------------- #
def load_s1(base: Path, cfg: str, ch: str):
    f = base / f"{cfg}_{ch}" / "events.npz"
    if not f.exists():
        return None
    z = dict(np.load(f))
    z["N"] = int(z["n_generated"].sum())
    return z


def load_table(base: Path, run: str, cfg: str):
    d = base / f"{run}_{cfg}"
    if not (d / "table.npz").exists():
        return None
    z = dict(np.load(d / "table.npz"))
    acc = json.load(open(d / "accounting.json"))
    z["absorbed"] = acc["counts"].get("absorbed_np", 0.0)
    z["N_sim"] = acc["N_sim"]
    z["run"] = run
    return z


def concat(tables):
    tables = [t for t in tables if t is not None]
    if not tables:
        return None
    keys = [k for k in tables[0] if not k.startswith("_")
            and isinstance(tables[0][k], np.ndarray) and tables[0][k].ndim >= 1]
    out = {k: np.concatenate([t[k] for t in tables]) for k in keys}
    out["absorbed"] = sum(t["absorbed"] for t in tables)
    return out


#: per-arm scintillator energy resolution, sigma/E = A/sqrt(E) (+) B.  The
#: simulation's deposits are exact; the accidental Esum tail falls ~4x per MeV
#: near 12-14 MeV, so the cut must see a realistic resolution.
ERES = [0.10, 0.05]
_SMEAR_RNG = np.random.default_rng(11)


def smear_E(E):
    A, B = ERES
    if A <= 0 and B <= 0:
        return E
    E = np.asarray(E, float)
    s = np.sqrt(A * A * np.clip(E, 1e-6, None) + (B * E) ** 2)
    return np.clip(E + s * _SMEAR_RNG.standard_normal(E.shape), 0, None)


# --------------------------------------------------------------------------- #
# selections
# --------------------------------------------------------------------------- #
def legs_count(legs):
    legs = legs.astype(np.int64) & 0xF
    return sum((legs >> k) & 1 for k in range(4))


def s1_select(z, menu, ecut):
    if "_e_em" not in z:                 # smear once per sample
        z["_e_em"] = smear_E(z["E_sipm_em"] + z["E_plast_em"] + z["E_ls_em"])
        z["_e_ep"] = smear_E(z["E_sipm_ep"] + z["E_plast_ep"] + z["E_ls_ep"])
    e_em, e_ep = z["_e_em"], z["_e_ep"]
    if menu == "strict":
        m = legs_count(z["legs"]) >= 2
    elif menu == "sipm2":
        m = (z["E_sipm_em"] > SIPM_THR) & (z["E_sipm_ep"] > SIPM_THR)
    elif menu == "mm2":
        m = np.ones(len(e_em), bool)
    else:
        raise ValueError(menu)
    return m & (e_em + e_ep > ecut)


def arm_ok(t, menu, tag="p"):
    """Per (event, arm): what the menu asks of one lepton arm."""
    ok = (t["gap"] > GAP_THR) & (t[f"sipm_{tag}"] > SIPM_THR)
    if menu == "strict":
        ok &= t[f"plast_{tag}"] > PLAST_THR
    elif menu == "mm2":
        ok = t["gap"] > GAP_THR
    return ok


def arm_E(t, tag="p"):
    """True (unsmeared) per-arm scintillator energy, cached per table.  The
    backgrounds apply the resolution as a pass probability (pass_prob), so
    their Esum tails carry no smearing noise."""
    k = f"_E_{tag}"
    if k not in t:
        t[k] = (t[f"sipm_{tag}"] + t[f"plast_{tag}"] + t[f"ls_{tag}"]).astype(np.float64)
    return t[k]


def eres_var(E):
    """sigma^2 of one arm's measured energy (MeV^2)."""
    A, B = ERES
    E = np.clip(E, 0, None)
    return A * A * E + (B * E) ** 2


def pass_prob(e1, e2, ecut):
    """P(smeared e1 + smeared e2 > ecut), arms smeared independently."""
    if ecut <= 0:
        return np.ones(np.broadcast(e1, e2).shape)
    s = np.sqrt(eres_var(e1) + eres_var(e2))
    return ndtr((e1 + e2 - ecut) / np.maximum(s, 1e-9))


def ecut_margin(ecut):
    """How far below ecut a true Esum can still pass (5 sigma at the cut)."""
    return 0.0 if ecut <= 0 else 5.0 * math.sqrt(2 * eres_var(0.5 * ecut))


def chord_angle(p1, p2):
    c = (p1 * p2).sum(-1) / (np.linalg.norm(p1, axis=-1) * np.linalg.norm(p2, axis=-1))
    return np.degrees(np.arccos(np.clip(c, -1, 1)))


def two_arm_events(t, menu, ecut, tag="p"):
    """Correlated two-arm events: the two highest-energy arms passing the
    per-arm menu.  Returns (row mask, theta, Esum, dt, P(pass the Esum cut))."""
    ok = arm_ok(t, menu, tag)
    E = np.where(ok, arm_E(t, tag), -1.0)
    order = np.argsort(-E, axis=1)
    a1, a2 = order[:, 0], order[:, 1]
    r = np.arange(len(E))
    e1, e2 = E[r, a1], E[r, a2]
    m = (e1 >= 0) & (e2 >= 0)
    esum = e1 + e2
    m &= esum > ecut - ecut_margin(ecut)
    p = np.where(m, pass_prob(np.clip(e1, 0, None), np.clip(e2, 0, None), ecut), 0.0)
    th = chord_angle(t["gpos"][r, a1], t["gpos"][r, a2])
    dt = t["t_scint"][r, a1] - t["t_scint"][r, a2]
    return m, th, esum, dt, p


# --------------------------------------------------------------------------- #
# per-configuration background model
# --------------------------------------------------------------------------- #
def he3ng_rows(t):
    """Rows whose neutron made ³He(n,γ) (biased: weight << 1)."""
    return (t["capvol"] == "He3Gas") & (t["w"] < 0.01)


def correlated(t, menu, ecut, which):
    """Histogram (per absorbed neutron) of correlated two-arm fakes."""
    if t is None:
        return np.zeros(len(CENTRES)), 0
    sel = he3ng_rows(t) if which == "he3ng" else ~he3ng_rows(t)
    m, th, _, _, p = two_arm_events(t, menu, ecut)
    m &= sel
    h, _ = np.histogram(th[m], BINS, weights=t["w"][m].astype(float) * p[m])
    return h / t["absorbed"], int((m & (p > 0.5)).sum())


def singles(t, menu, tag="a"):
    """Per-arm single hits (any time: activation is steady state):
    list over arms of (weight per absorbed n, E, gap position)."""
    ok = arm_ok(t, menu, tag) & ~he3ng_rows(t)[:, None]
    E = arm_E(t, tag)
    out = []
    for a in range(4):
        m = ok[:, a]
        out.append((t["w"][m].astype(float) / t["absorbed"], E[m, a], t["gpos"][m, a]))
    return out


def singles_he3ng(t, menu, tag="p"):
    ok = arm_ok(t, menu, tag) & he3ng_rows(t)[:, None]
    E = arm_E(t, tag)
    return [(t["w"][ok[:, a]].astype(float) / t["absorbed"], E[ok[:, a], a],
             t["gpos"][ok[:, a], a]) for a in range(4)]


def merge_singles(*lists):
    return [tuple(np.concatenate([L[a][k] for L in lists if L is not None])
                  for k in range(3)) for a in range(4)]


def _pair_hist(wa, ea, pa, wb, eb, pb, ecut, chunk=4_000_000):
    """sum of w_i w_j P(E_i + E_j > ecut) over the product of two lists, binned
    in chord angle.  Exact (chunked over the first list)."""
    h = np.zeros(len(CENTRES))
    na, nb = len(wa), len(wb)
    if na == 0 or nb == 0:
        return h
    step = max(1, chunk // nb)
    for i0 in range(0, na, step):
        i1 = min(na, i0 + step)
        m = ea[i0:i1, None] + eb[None, :] > ecut - ecut_margin(ecut)
        ia, ib = np.nonzero(m)
        ia += i0
        th = chord_angle(pa[ia], pb[ib])
        h += np.histogram(th, BINS, weights=wa[ia] * wb[ib] * pass_prob(ea[ia], eb[ib], ecut))[0]
    return h


def accidental_hist(S, ecut, rng=None):
    """sum over arm pairs of p_i p_j P(E_i + E_j > ecut) binned in chord angle;
    multiply by R^2 * 2tau for a rate.

    Stratified, because the Esum tail is carried by rare hard singles: every
    passing pair has a member above ecut/2, so the sum splits exactly into
    (hard a) x (b able to reach ecut) + (soft a) x (hard b), and each product
    is restricted to partners that can pass.  Exact; `rng` is unused."""
    h = np.zeros(len(CENTRES))
    for a in range(4):
        for b in range(a + 1, 4):
            wa, ea, pa = S[a]
            wb, eb, pb = S[b]
            if len(wa) == 0 or len(wb) == 0:
                continue
            lo = ecut - ecut_margin(ecut)      # lowest true Esum that can pass
            half = 0.5 * lo
            ha, hb = ea > half, eb > half
            # hard a with any b that can still pass
            if ha.any():
                kb = eb > lo - ea[ha].max()
                h += _pair_hist(wa[ha], ea[ha], pa[ha], wb[kb], eb[kb], pb[kb], ecut)
            # soft a (that can pass) with hard b
            if hb.any():
                ka = ~ha & (ea > lo - eb[hb].max())
                h += _pair_hist(wa[ka], ea[ka], pa[ka], wb[hb], eb[hb], pb[hb], ecut)
    return h


def cosmic_hist(k1, menu, ecut, sigma_t_ns, dt_cut_ns, rng=None):
    """Cosmic two-arm events per live second after |dt| < dt_cut, with dt
    smeared by sqrt(2)*sigma_t: each event is weighted by its probability to
    pass (no sampling noise).  ``n_raw`` is the effective number of MC events."""
    if k1 is None:
        return None
    m, th, _, dt, pe = two_arm_events(k1, menu, ecut)
    s = math.sqrt(2) * sigma_t_ns
    d = dt[m]
    p = ndtr((dt_cut_ns - d) / s) - ndtr((-dt_cut_ns - d) / s)
    p = np.nan_to_num(p) * pe[m]
    live = k1["N_sim"] * COSMIC_S_PER_MU
    h_all, _ = np.histogram(th[m], BINS, weights=pe[m])
    h, _ = np.histogram(th[m], BINS, weights=p)
    h = smooth(h, 6.0)
    n_eff = float(p.sum() ** 2 / max((p * p).sum(), 1e-300))
    return dict(h=h / live, h_notime=h_all / live, n_raw=int(round(n_eff)), n_raw_notime=int(round(pe[m].sum())))


def gap_rate_per_arm(t):
    """Charged deposits >= 1 keV per arm per absorbed neutron (any time)."""
    w = t["w"][:, None].astype(float)
    return float((w * (t["gap"] > GAP_THR)).sum() / t["absorbed"] / 4)


def trigger_rates(t, menu_trig="sipm2"):
    """Per absorbed n: correlated SiPM-in-2-arms triggers, and per-arm SiPM
    singles (for accidental triggers).  No MM condition (the trigger cannot
    see the chambers)."""
    s = t["sipm_a"] > SIPM_THR
    if menu_trig == "strict":
        s &= t["plast_a"] > PLAST_THR
    w = t["w"].astype(float)
    corr = float(w[s.sum(1) >= 2].sum() / t["absorbed"])
    per_arm = (w[:, None] * s).sum(0) / t["absorbed"]
    return corr, per_arm


def smooth(h, sigma_deg=6.0):
    """Gaussian kernel smoothing of a background template (limited MC
    statistics must not create empty bins the Fisher matrix would exploit).
    Normalisation-preserving inside the histogram range."""
    if sigma_deg <= 0 or not np.any(h):
        return h
    d = CENTRES[:, None] - CENTRES[None, :]
    K = np.exp(-0.5 * (d / sigma_deg) ** 2)
    K /= K.sum(0, keepdims=True)
    return K @ h


# --------------------------------------------------------------------------- #
# Fisher
# --------------------------------------------------------------------------- #
def sigma_mu(float_templates, fixed):
    """sigma of the first template's amplitude, all amplitudes floating,
    evaluated at amplitudes (0, 1, 1, ...)."""
    n = sum(float_templates[1:]) + fixed
    ok = n > 0
    D = np.stack([f[ok] for f in float_templates])
    F = (D[:, None, :] * D[None, :, :] / n[ok]).sum(-1)
    keep = np.abs(D).sum(1) > 0
    keep[0] = True
    F = F[np.ix_(keep, keep)]
    try:
        return math.sqrt(np.linalg.inv(F)[0, 0])
    except (np.linalg.LinAlgError, ValueError):
        return math.inf


def s1_hist(z, per_abs, menu, ecut, est="nomline"):
    m = s1_select(z, menu, ecut)
    h, _ = np.histogram(z[f"reco_{est}"][m], BINS)
    return h * per_abs / z["N"]


def model(cfg, s1, tabs, menu, ecut, R, days, tau_ns, sigma_t_ns, dt_cut_ns,
          est="nomline", rng=None, cache=None):
    """Everything expected in `days` at R absorbed n/s.  Histograms in counts."""
    rng = rng or np.random.default_rng(1)
    T = days * DAY
    nabs = R * T
    X, M, E = (s1[c] for c in ("X17", "M1", "E0"))
    key = (cfg, menu, ecut)
    if cache is not None and key in cache:
        base = cache[key]
    else:
        c1 = concat([tabs.get("C1"), tabs.get("C1w")])
        g_src = tabs.get("C1g") or tabs.get("C1")
        S = merge_singles(singles(c1, menu), singles_he3ng(g_src, menu))
        base = dict(
            x=s1_hist(X, M1_PER_ABS, menu, ecut, est),
            m1=smooth(s1_hist(M, M1_PER_ABS, menu, ecut, est), 3.0),
            e0=smooth(s1_hist(E, E0_PER_ABS, menu, ecut, est), 3.0),
            g=(lambda r: (smooth(r[0], 8.0), r[1]))(correlated(g_src, menu, ecut, "he3ng")),
            wall=(lambda r: (smooth(r[0], 8.0), r[1]))(correlated(c1, menu, ecut, "wall")),
            acc=smooth(accidental_hist(S, ecut, rng), 6.0),
            gap_arm=gap_rate_per_arm(c1),
            cos=cosmic_hist(tabs.get("K1"), menu, ecut, sigma_t_ns, dt_cut_ns, rng),
        )
        if cache is not None:
            cache[key] = base
    occ = R * base["gap_arm"] * MM_WINDOW_S
    eff_occ = math.exp(-2 * occ)          # no foreign MM hit in either lepton arm
    out = dict(
        X17=base["x"] * nabs * eff_occ, M1=base["m1"] * nabs * eff_occ,
        E0=base["e0"] * nabs * eff_occ, G=base["g"][0] * nabs * eff_occ,
        WALL=base["wall"][0] * nabs * eff_occ,
        ACC=base["acc"] * R * R * 2 * tau_ns * 1e-9 * T * eff_occ,
        COS=(base["cos"]["h"] * T if base["cos"] is not None else np.zeros(len(CENTRES))) * eff_occ,
        occ=occ, eff_occ=eff_occ, raw_g=base["g"][1], raw_wall=base["wall"][1],
        raw_cos=base["cos"]["n_raw"] if base["cos"] is not None else None,
    )
    return out


def reach(mod, window=(60, 180)):
    w = (CENTRES >= window[0]) & (CENTRES <= window[1])
    fl = [mod["X17"][w], mod["M1"][w], mod["E0"][w], mod["G"][w]]
    fixed = mod["ACC"][w] + mod["COS"][w] + mod["WALL"][w]
    return sigma_mu(fl, fixed)


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s1", type=Path, default=HERE / "sim" / "S1")
    ap.add_argument("--contracts", type=Path, default=HERE / "sim" / "contracts")
    ap.add_argument("--days", type=float, default=50.0)
    ap.add_argument("--tau-ns", type=float, default=2.5, help="coincidence half-window")
    ap.add_argument("--sigma-t-ns", type=float, default=0.5, help="per-arm time resolution")
    ap.add_argument("--dt-cut-ns", type=float, default=1.5)
    ap.add_argument("--write", type=Path, default=None, help="JSON output")
    a = ap.parse_args()
    rng = np.random.default_rng(7)
    rates = np.logspace(8, 11, 13)
    results = dict(args={k: str(v) for k, v in vars(a).items()}, configs={})
    for cfg in CONFIGS:
        s1 = {c: load_s1(a.s1, cfg, c) for c in ("X17", "M1", "E0")}
        if any(v is None for v in s1.values()):
            continue
        tabs = {r: load_table(a.contracts, r, cfg) for r in ("C1", "C1w", "C1g")}
        tabs["K1"] = load_table(a.contracts, "K1", "G5")
        if tabs["C1"] is None and tabs["C1w"] is None:
            continue
        have = [k for k, v in tabs.items() if v is not None]
        print(f"\n=== {cfg}  (tables: {', '.join(have)})")
        cache = {}
        res = {}
        for menu in ("strict", "sipm2"):
            for ecut in (0.0, 8.0, 11.0, 12.0, 13.0, 14.0):
                row = []
                for R in rates:
                    mod = model(cfg, s1, tabs, menu, ecut, R, a.days, a.tau_ns,
                                a.sigma_t_ns, a.dt_cut_ns, rng=rng, cache=cache)
                    s = reach(mod)
                    row.append(dict(R=R, sigma=s, **{k: float(np.sum(mod[k])) for k in
                                                      ("X17", "M1", "E0", "G", "WALL", "ACC", "COS")},
                                    occ=mod["occ"]))
                best = min(row, key=lambda r: r["sigma"])
                res[f"{menu}/E>{ecut:g}"] = dict(scan=row, best=best)
                b = best
                print(f"  {menu:6s} Esum>{ecut:4.1f}: best R {b['R']:.2g} n/s -> 3σ reach "
                      f"{3 * b['sigma']:.2e} (5σ {5 * b['sigma']:.2e});  per {a.days:g} d: "
                      f"IPC {b['M1'] + b['E0']:.3g}  ³He(n,γ) fakes {b['G']:.3g}  acc {b['ACC']:.3g}  "
                      f"cos {b['COS']:.3g}  wall {b['WALL']:.3g}  X17@ref {X17_REF * b['X17']:.3g}  "
                      f"MM occ {b['occ']:.2f}")
        results["configs"][cfg] = res
    if a.write:
        a.write.write_text(json.dumps(results, indent=1, default=float))
        print(f"\nwrote {a.write}")


if __name__ == "__main__":
    main()
