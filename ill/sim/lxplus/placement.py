import numpy as np, sim_feasibility as SF
from pathlib import Path
E = Path("/eos/experiment/ntof/data/x17/ill")
def s68(x):
    x = x[np.isfinite(x)]
    return 0.5 * (np.percentile(x, 84) - np.percentile(x, 16)) if len(x) else np.nan
rows = [("S1", "G1"), ("S1p", "G1_yw0"), ("S1p", "G1_ywmean"), ("S1", "G5"), ("S1p", "G5_yw0"),
        ("S1p", "G5_ywmean"), ("S1s", "G5_r17.5"), ("S1s", "G5_r25")]
print(f"{'sample':18s} {'acc sipm2':>9s} {'E>12':>7s} {'nomline s68':>11s} {'xing_s':>7s} {'vline':>6s}  peak(nomline) med/p16/p84   M1 acc")
for run, cfg in rows:
    z = SF.load_s1(E / run / "summary", cfg, "X17")
    if z is None:
        print(run, cfg, "missing"); continue
    m = SF.s1_select(z, "sipm2", 12.0); m0 = SF.s1_select(z, "sipm2", 0.0)
    th = z["theta"]
    d = {e: s68(z[f"reco_{e}"][m] - th[m]) for e in ("nomline", "xing_s", "vline")}
    pk = np.percentile(z["reco_nomline"][m], [50, 16, 84])
    zm = SF.load_s1(E / run / "summary", cfg, "M1")
    am = SF.s1_select(zm, "sipm2", 12.0).sum() / zm["N"] if zm is not None else np.nan
    print(f"{run+'/'+cfg:18s} {m0.sum()/z['N']:9.4f} {m.sum()/z['N']:7.4f} {d['nomline']:11.2f} {d['xing_s']:7.2f} {d['vline']:6.2f}  "
          f"{pk[0]:.1f}/{pk[1]:.1f}/{pk[2]:.1f}   {am:.5f}")
