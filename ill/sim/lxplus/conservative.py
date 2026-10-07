#!/usr/bin/env python3
"""
conservative.py -- the ILL reach under n_TOF-like hardware, plus two levers.

Re-runs the sim_feasibility model (G1) with:

  timing    per-arm sigma_t from the n_TOF SiPM wall (~5 ns per arm, ~7 ns on the
            arm-to-arm difference; nTof_x17/ntof_cosmics/README.md), with
            |dt| < 2.5 sigma_dt and the accidental window equal to the cut.
  trigger   per-arm coincidence only, no energy sum:
              strict  SiPM wall AND plastic in an arm, in >= 2 arms (n_TOF-like)
              sipm2   SiPM wall in >= 2 arms (the old analysis menu)
            The DREAM live time 1 / (1 + f tau), tau = 298 us (RAW, 20 samples),
            with f = correlated + accidental hardware triggers (2tau_hw window)
            scales the exposure.  The offline Esum > 13 MeV cut is kept: it needs
            only the digitised scintillator amplitudes.
  cosmics   ceiling-panel veto as in FEASIBILITY_SIM §8 (inefficiency 1e-2).
  segments  per-arm Micromegas segment (seg_reduce.py, dominant track): the line
            must pass within D of the beam axis inside the cell's y range, and
            (optionally) the dominant track must carry >= fq of the arm's charge.
            The fitted direction is smeared by sigma_theta (the data-like error).
  end cap   drop every row whose neutron was captured in He3Cell_EndUp/EndDown
            (an oracle: the Al is replaced by something with no hard gamma).

    python3 conservative.py -o cons_G1.csv          # lxplus, needs parts_seg/
"""
from __future__ import annotations

import argparse
import glob
import itertools
import math
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sim_feasibility as SF          # noqa: E402

E = Path("/eos/experiment/ntof/data/x17/ill")
CFG = "G1"
R_MAX = 1.9e10
DAQ_TAU_S = 298e-6
Y_RANGE = (-60.0, 200.0)              # mm along the beam: X17 vertices are -21..153 (p1..p99)
SEG_KEYS = ("c_dom", "d_dom", "fdom", "n_dom")


# --------------------------------------------------------------------------- #
# joining segments to the tables
# --------------------------------------------------------------------------- #
def seg_for_table(run_dir: Path, t):
    """Per table row, per arm: segment arrays (NaN where none).  Table rows carry
    ev + i * 1e9 with i the index in sorted(parts/*.npz) (pipeline.sh)."""
    parts = sorted(glob.glob(str(run_dir / "parts" / "*.npz")))
    n = len(t["ev"])
    out = {k: np.full((n, 4, 3) if k in ("c_dom", "d_dom") else (n, 4), np.nan, np.float32)
           for k in SEG_KEYS}
    fi = (t["ev"] // 10**9).astype(np.int64)
    ev = t["ev"] % 10**9
    missing = 0
    for i, p in enumerate(parts):
        rows = np.flatnonzero(fi == i)
        if not len(rows):
            continue
        sp = run_dir / "parts_seg" / Path(p).name
        if not sp.exists():
            missing += 1
            continue
        z = np.load(sp)
        if not len(z["ev"]):
            continue
        j = np.searchsorted(z["ev"], ev[rows])
        j = np.clip(j, 0, len(z["ev"]) - 1)
        ok = z["ev"][j] == ev[rows]
        for k in SEG_KEYS:
            out[k][rows[ok]] = z[k][j[ok]]
    if missing:
        print(f"  WARNING {run_dir}: {missing} part(s) without segments", flush=True)
    return out


def seg_for_s1(ch: str):
    """Segments for the em/ep arms of every row of S1/summary/<cfg>_<ch>/events.npz
    (rows = parts in sorted order, two-arm events only, as ill_pairs.merge)."""
    d = E / "S1" / f"{CFG}_{ch}"
    out = {f"{lp}_{k}": [] for lp in ("em", "ep") for k in SEG_KEYS}
    for p in sorted(glob.glob(str(d / "parts" / "*.npz"))):
        z = np.load(p)
        arm2 = (z["em_arm"] >= 0) & (z["ep_arm"] >= 0) & (z["em_arm"] != z["ep_arm"])
        evs = z["eventID"][arm2].astype(np.int64)
        sp = d / "parts_seg" / Path(p).name
        s = np.load(sp) if sp.exists() else None
        for lp in ("em", "ep"):
            arm = z[f"{lp}_arm"][arm2].astype(np.int64)
            for k in SEG_KEYS:
                shp = (len(evs), 3) if k in ("c_dom", "d_dom") else (len(evs),)
                a = np.full(shp, np.nan, np.float32)
                if s is not None and len(s["ev"]):
                    j = np.clip(np.searchsorted(s["ev"], evs), 0, len(s["ev"]) - 1)
                    ok = s["ev"][j] == evs
                    a[ok] = s[k][j[ok], arm[ok]]
                out[f"{lp}_{k}"].append(a)
    return {k: np.concatenate(v) for k, v in out.items()}


# --------------------------------------------------------------------------- #
# the segment cut
# --------------------------------------------------------------------------- #
def smear_dir(d, deg, rng):
    if deg <= 0:
        return d
    d = d / np.linalg.norm(d, axis=-1, keepdims=True)
    a = np.where(np.abs(d[..., :1]) < 0.9, np.array([1.0, 0, 0]), np.array([0, 1.0, 0]))
    u = np.cross(d, a)
    u /= np.linalg.norm(u, axis=-1, keepdims=True)
    v = np.cross(d, u)
    s = math.radians(deg)
    g = rng.normal(0, s, d.shape[:-1] + (2,))
    out = d + g[..., :1] * u + g[..., 1:] * v
    return out / np.linalg.norm(out, axis=-1, keepdims=True)


def dca_beam(c, d):
    """Distance of closest approach of the line c + s d to the beam (y) axis,
    and the y where it happens."""
    dx, dz = d[..., 0], d[..., 2]
    den = np.maximum(dx * dx + dz * dz, 1e-12)
    s = -(c[..., 0] * dx + c[..., 2] * dz) / den
    x = c[..., 0] + s * dx
    z = c[..., 2] + s * dz
    return np.hypot(x, z), c[..., 1] + s * d[..., 1]


def seg_pass(c, d, f, n, deg, D, fq, rng, with_dir=False):
    """Pointing (+ optional single-track) cut; with_dir also returns the
    smeared directions so the collinearity veto sees the same draw."""
    ok = (n >= 3) & np.isfinite(d).all(-1)
    dd = smear_dir(np.where(np.isfinite(d), d, 1.0), deg, rng)
    r, y = dca_beam(np.where(np.isfinite(c), c, 0.0), dd)
    ok &= (r < D) & (y > Y_RANGE[0]) & (y < Y_RANGE[1])
    if fq > 0:
        ok &= np.nan_to_num(f) >= fq
    return (ok, dd.astype(np.float32)) if with_dir else ok


def line_angle(d1, d2):
    """Acute angle [deg] between two lines (direction sign ignored)."""
    c = np.abs((d1 * d2).sum(-1)) / (np.linalg.norm(d1, axis=-1) * np.linalg.norm(d2, axis=-1))
    return np.degrees(np.arccos(np.clip(c, 0, 1)))


#: collinearity veto [deg]: a two-arm event whose two segment lines are within
#: COLL_DEG of parallel is one straight track (a through-going muon).  Applied
#: to correlated two-arm events (cosmics, ³He(n,γ), wall) and to the signal;
#: NOT to accidental pairs (conservative: it would remove a few of them too).
COLL_DEG = 0.0

# --------------------------------------------------------------------------- #
# patched selections: arm_ok and s1_select honour a per-arm / per-event flag
# --------------------------------------------------------------------------- #
_arm_ok, _s1_select = SF.arm_ok, SF.s1_select


def arm_ok(t, menu, tag="p"):
    ok = _arm_ok(t, menu, tag)
    return ok & t["segok"] if "segok" in t else ok


def s1_select(z, menu, ecut):
    m = _s1_select(z, menu, ecut)
    return m & z["segok"] if "segok" in z else m


_two_arm_events = SF.two_arm_events


def two_arm_events(t, menu, ecut, tag="p"):
    m, th, esum, dt, p = _two_arm_events(t, menu, ecut, tag)
    if COLL_DEG > 0 and "segd" in t:
        ok = SF.arm_ok(t, menu, tag)          # same arm choice as the original
        E_ = np.where(ok, SF.arm_E(t, tag), -1.0)
        o = np.argsort(-E_, axis=1)
        r = np.arange(len(E_))
        ang = line_angle(t["segd"][r, o[:, 0]], t["segd"][r, o[:, 1]])
        veto = ang < COLL_DEG
        m = m & ~veto
        p = np.where(veto, 0.0, p)
    return m, th, esum, dt, p


SF.arm_ok, SF.s1_select, SF.two_arm_events = arm_ok, s1_select, two_arm_events


# --------------------------------------------------------------------------- #
def hw_trigger_rate(c1, menu, R, two_tau_hw_s):
    """Hardware triggers per second at R absorbed n/s: correlated two-arm
    triggers + accidental pairs of per-arm singles.  No Micromegas condition."""
    corr, per_arm = SF.trigger_rates(c1, "strict" if menu == "strict" else "sipm2")
    acc = sum(per_arm[a] * per_arm[b] for a in range(4) for b in range(a + 1, 4))
    return corr * R + acc * R * R * two_tau_hw_s


def best_reach(s1, tabs, menu, ecut, sig_t, cos_scale, live, two_tau_hw, days=50.0, rng=None,
               dt_cut=None, tau=None, zero=()):
    """dt_cut defaults to 2.5 sigma of the arm-to-arm difference; the accidental
    half-window tau to the cut."""
    dt_cut = dt_cut if dt_cut is not None else 2.5 * math.sqrt(2) * sig_t
    tau = tau if tau is not None else dt_cut
    cache = {}
    c1 = SF.concat([tabs.get("C1"), tabs.get("C1w")])
    best = None
    for R in np.logspace(8, math.log10(R_MAX), 22):
        f = hw_trigger_rate(c1, menu, R, two_tau_hw) if live else 0.0
        lv = 1.0 / (1.0 + f * DAQ_TAU_S)
        mod = SF.model(CFG, s1, tabs, menu, ecut, R, days * lv, tau, sig_t, dt_cut,
                       rng=rng, cache=cache)
        mod["COS"] = mod["COS"] * cos_scale
        for k in zero:                      # oracle: this background is gone
            mod[k] = mod[k] * 0.0
        s = SF.reach(mod)
        if best is None or s < best[1]:
            best = (R, s, lv, f, {k: float(np.sum(mod[k])) for k in
                                  ("X17", "M1", "E0", "G", "WALL", "ACC", "COS")})
    return best


def use_biased_only(c1, c1w):
    """In place: volumes whose C1w rows carry weight < 1 (biased nCapture, not
    the ³He(n,γ) rows) are estimated from C1w only.  concat() divides the summed
    weights by the pooled absorbed count, so C1w's rows there are scaled by
    (A1 + A2) / A2 and C1's rows there are dropped: same expectation, far
    smaller variance when the bias factor is large."""
    he3 = SF.he3ng_rows(c1w)
    v2 = c1w["capvol"].astype(str)
    biased = sorted({v for v in np.unique(v2[(c1w["w"] < 0.5) & ~he3])})
    a1, a2 = c1["absorbed"], c1w["absorbed"]
    m2 = np.isin(v2, biased) & ~he3
    m1 = np.isin(c1["capvol"].astype(str), biased) & ~SF.he3ng_rows(c1)
    c1w["w"] = np.where(m2, c1w["w"] * (a1 + a2) / a2, c1w["w"]).astype(c1w["w"].dtype)
    c1["w"] = np.where(m1, 0, c1["w"]).astype(c1["w"].dtype)
    print(f"biased-only: {len(biased)} volumes from C1w alone ({', '.join(biased[:8])}"
          f"{' ...' if len(biased) > 8 else ''}); C1 rows dropped {m1.sum()}, C1w rows scaled {m2.sum()}", flush=True)


def run_budget(a, build, raw, seg, hw, rng):
    """Reach with one background source taken away at a time.  Capture sources
    are dropped by zeroing the weight of every C1/C1w neutron captured there
    (all of that neutron's arms go: singles, so accidentals; correlated fakes
    from those volumes are already ~0 above 13 MeV).  Oracles zero a whole
    background class in the fit model."""
    import acc_sources as AS
    s1v, tv0 = build(*seg, False)
    src = {}
    for r in ("C1", "C1w"):
        u, inv = np.unique(tv0[r]["capvol"].astype(str), return_inverse=True)
        src[r] = np.array([AS.volume(v)[0] for v in u])[inv]
    present = sorted({x for r in src for x in np.unique(src[r])} - {"³He gas"})
    scen = [("as is", (), ())] + [(f"no {x}", (x,), ()) for x in present]
    scen += [("no Be window + air", ("Be entrance window", "air"), ()),
             ("oracle: no accidentals", (), ("ACC",)), ("oracle: no cosmics", (), ("COS",)),
             ("oracle: no ACC, no COS", (), ("ACC", "COS")),
             ("oracle: IPC only", (), ("ACC", "COS", "G", "WALL"))]
    rows = []
    for label, sig, live, menu, cs, *win in hw:
        if a.hw and not any(h in label.replace(" ", "-") for h in a.hw.split(",")):
            continue
        for name, drop, zero in scen:
            tv = {r: dict(t) for r, t in tv0.items()}
            for r in ("C1", "C1w"):
                if drop:
                    tv[r]["w"] = np.where(np.isin(src[r], drop), 0, tv[r]["w"]).astype(tv[r]["w"].dtype)
            R, s, lv, f, n = best_reach(s1v, tv, menu, a.ecut, sig, cs, live, 2 * 25e-9, rng=rng,
                                       dt_cut=win[0] if win else None, tau=win[1] if win else None, zero=zero)
            row = dict(variant=a.variant or "baseline", coll=COLL_DEG, hw=label, seg=f"{seg[0]}deg D<{seg[1]}mm",
                       scenario=name, biased_only=a.biased_only, ecut=a.ecut, best_R=R, live=lv, trig_Hz=f, reach3=3 * s, **n)
            rows.append(row)
            print(f"{row['variant']:9s} {label:42s} {name:34s} R {R:.2g}  3σ {3 * s:.2e}  "
                  f"X17 {n['X17'] * SF.X17_REF:6.0f} IPC {n['M1'] + n['E0']:7.0f} ACC {n['ACC']:7.0f} "
                  f"COS {n['COS']:7.0f} G {n['G']:5.0f}", flush=True)
            pd.DataFrame(rows).to_csv(a.out, index=False)
    print("wrote", a.out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", type=Path, required=True)
    ap.add_argument("--quick", action="store_true", help="small grid")
    ap.add_argument("--no-seg", action="store_true", help="hardware scenarios and end cap only")
    ap.add_argument("--segs", default=None, help="explicit cut list deg:D:fq,... (overrides the grid)")
    ap.add_argument("--hw", default=None, help="comma list of substrings selecting hardware rows")
    ap.add_argument("--coll", type=float, default=0.0, help="collinearity veto [deg], 0 = off")
    ap.add_argument("--variant", default="", help="C1/C1w geometry variant tag, e.g. ringCFRP")
    ap.add_argument("--biased-only", action="store_true",
                    help="for capture volumes that C1w biases, take them from C1w alone (rescaled to the "
                         "pooled C1+C1w exposure) instead of the plain pool, where a handful of unit-weight "
                         "C1 events outweigh thousands of biased ones")
    ap.add_argument("--ecut", type=float, default=13.0, help="offline Esum cut [MeV] (budget mode)")
    ap.add_argument("--budget", action="store_true",
                    help="what limits the reach: rerun the first --segs cut and --hw rows with each capture "
                         "source removed (acc_sources.volume classes) and with oracles that zero ACC / COS")
    a = ap.parse_args()
    global COLL_DEG
    COLL_DEG = a.coll
    rng = np.random.default_rng(3)

    s1 = {c: SF.load_s1(E / "S1" / "summary", CFG, c) for c in ("X17", "M1", "E0")}
    s1seg = {c: seg_for_s1(c) for c in s1}
    for c in s1:
        assert len(s1seg[c]["em_n_dom"]) == len(s1[c]["theta"]), (c, "row mismatch")
        print(f"S1 {c}: {len(s1[c]['theta'])} rows, segments on "
              f"{np.mean(s1seg[c]['em_n_dom'] >= 3):.3f} (e-) / {np.mean(s1seg[c]['ep_n_dom'] >= 3):.3f} (e+)",
              flush=True)
    vcfg = {r: CFG + (f"_{a.variant}" if a.variant and r in ("C1", "C1w") else "")
            for r in ("C1", "C1w", "C1g")}
    vcfg["K1"] = "G5"
    raw = {r: SF.load_table(E / "contracts", r, vcfg[r]) for r in ("C1", "C1w", "C1g")}
    raw["K1"] = SF.load_table(E / "contracts", "K1", "G5")
    if a.biased_only:
        use_biased_only(raw["C1"], raw["C1w"])
    tseg = {}
    for r, t in raw.items():
        run, cfg = r, vcfg[r]
        tseg[r] = seg_for_table(E / run / cfg, t)
        have = np.isfinite(tseg[r]["n_dom"]) & (t["gap"] > SF.GAP_THR)
        print(f"{r}: {len(t['ev'])} rows; arms with gap charge that have a segment "
              f"{have.sum() / max(1, (t['gap'] > SF.GAP_THR).sum()):.3f}", flush=True)

    def build(deg, D, fq, endcap_off):
        s1v = {}
        for c, z in s1.items():
            z = dict(z)
            if deg is not None:
                g = s1seg[c]
                pm, dm = seg_pass(g["em_c_dom"], g["em_d_dom"], g["em_fdom"], g["em_n_dom"], deg, D, fq, rng, True)
                pp, dp = seg_pass(g["ep_c_dom"], g["ep_d_dom"], g["ep_fdom"], g["ep_n_dom"], deg, D, fq, rng, True)
                z["segok"] = pm & pp
                if COLL_DEG > 0:
                    z["segok"] &= line_angle(dm, dp) >= COLL_DEG
            s1v[c] = z
        tv = {}
        for r, t in raw.items():
            t = dict(t)
            if endcap_off and r != "K1":
                cut = np.char.startswith(t["capvol"].astype(str), "He3Cell_End")
                t["w"] = np.where(cut, 0, t["w"]).astype(t["w"].dtype)
            if deg is not None:
                g = tseg[r]
                t["segok"], t["segd"] = seg_pass(g["c_dom"], g["d_dom"], g["fdom"], g["n_dom"], deg, D, fq, rng, True)
            tv[r] = t
        return s1v, tv

    if a.segs:
        segs = [tuple(float(x) for x in g.split(":")) for g in a.segs.split(",")]
    elif a.no_seg:
        segs = [None]
    elif a.quick:
        segs = [None, (5, 40, 0.0), (5, 40, 0.7)]
    else:
        segs = [None] + [(deg, D, fq) for deg in (2, 5, 10, 20)
                         for D in (25, 40, 60) for fq in (0.0, 0.7)]
    hw = [  # label, sigma_t per arm, live-time on, menu, cos_scale[, dt_cut, tau]
        ("old baseline (0.5 ns, sipm2, no DAQ)", 0.5, False, "sipm2", 1.0, 1.5, 2.5),
        ("200 ps + veto, sipm2, no DAQ", 0.2, False, "sipm2", 1e-2, 0.6, 0.6),
        ("nTOF 5 ns + veto, sipm2 trigger", 5.0, True, "sipm2", 1e-2),
        ("nTOF 5 ns + veto, per-arm coinc (strict)", 5.0, True, "strict", 1e-2),
        ("nTOF 5 ns, no veto, strict", 5.0, True, "strict", 1.0),
        ("2 ns + veto, strict", 2.0, True, "strict", 1e-2),
        ("1 ns + veto, strict", 1.0, True, "strict", 1e-2),
    ]
    if a.budget:
        return run_budget(a, build, raw, segs[0], hw, rng)
    rows = []
    for (seg, endcap) in itertools.product(segs, (False, True)):
        if not a.segs and seg is not None and seg[0] in (2, 20) and endcap:
            continue
        s1v, tv = build(*(seg if seg else (None, None, None)), endcap)
        for label, sig, live, menu, cs, *win in hw:
            if a.hw and not any(h in label.replace(" ", "-") for h in a.hw.split(",")):
                continue
            if not (a.quick or a.segs) and seg is not None and label.startswith(("old", "nTOF 5 ns, no", "1 ns", "2 ns")) \
                    and seg != (5, 40, 0.7):
                continue
            R, s, lv, f, n = best_reach(s1v, tv, menu, 13.0, sig, cs, live, 2 * 25e-9, rng=rng,
                                       dt_cut=win[0] if win else None, tau=win[1] if win else None)
            row = dict(variant=a.variant or "baseline", coll=COLL_DEG, hw=label, menu=menu, sigma_t=sig, seg="none" if seg is None else
                       f"{seg[0]}deg D<{seg[1]}mm fdom>{seg[2]}", endcap_off=endcap,
                       best_R=R, live=lv, trig_Hz=f, reach3=3 * s, **n)
            rows.append(row)
            print(f"{row['variant']:9s} coll {COLL_DEG:4.0f} {row['hw']:42s} seg {row['seg']:22s} endcap_off {endcap!s:5s} R {R:.2g} "
                  f"live {lv:.2f} trig {f:7.0f} Hz  3σ {3 * s:.2e}  X17 {n['X17'] * SF.X17_REF:7.0f} "
                  f"IPC {n['M1'] + n['E0']:8.0f} ACC {n['ACC']:8.0f} COS {n['COS']:8.0f} G {n['G']:6.0f}",
                  flush=True)
            pd.DataFrame(rows).to_csv(a.out, index=False)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
