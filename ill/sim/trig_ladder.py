"""Hardware-trigger rate vs per-arm / two-arm energy threshold, and the X17
fraction each keeps (G5, local C1 table + s1test X17 sample).  Feeds the DREAM
live-time question (HANDOFF.md, "ILL rate vs DREAM dead time").

    cd ill && PYTHONPATH=. python sim/trig_ladder.py

Caveat: the C1 table is importance-weighted; above ~2 MeV per arm the
correlated rate comes from ONE unit-weight row, so it is a ~100 Hz-scale
order of magnitude, not a measurement.
"""
import numpy as np, sim_feasibility as SF
from pathlib import Path
C = Path("sim/contracts")
R = 1.0e10; tau2 = 5e-9
t = SF.load_table(C, "C1", "G5")
w = t["w"].astype(float) / t["absorbed"]
E = SF.arm_E(t, "a"); s = t["sipm_a"] > SF.SIPM_THR
print("rows", len(w), "absorbed", t["absorbed"])
# X17 signal
z = SF.load_s1(Path("sim/s1test"), "G5", "X17")
emx = z["E_sipm_em"]+z["E_plast_em"]+z["E_ls_em"]; epx = z["E_sipm_ep"]+z["E_plast_ep"]+z["E_ls_ep"]
base = (z["E_sipm_em"]>SF.SIPM_THR)&(z["E_sipm_ep"]>SF.SIPM_THR)&(emx+epx>13)
print("X17 analysis-selected", base.sum())
for thr in (0, 1, 2, 3, 4, 5, 6):
    sel = s & (E > thr)
    p = (w[:, None]*sel).sum(0)
    corr = float((w*(sel.sum(1) >= 2)).sum())
    acc = sum(p[a]*p[b] for a in range(4) for b in range(a+1, 4))*R*R*tau2
    keep = (base & (emx > thr) & (epx > thr)).sum()/base.sum()
    print(f"per-arm>{thr} MeV: corr {corr*R:8.1f} Hz  acc {acc:7.2f} Hz  total@1e10 {corr*R+acc:8.1f} Hz   X17 kept {keep:.3f}")
# two-arm sum trigger (analog sum of the two hit arms)
for st in (4, 6, 8, 10, 12):
    Es = np.where(s, E, 0); top2 = -np.sort(-Es, 1)[:, :2].sum(1)
    sel2 = (s.sum(1) >= 2) & (top2 > st)
    corr = float((w*sel2).sum())
    keep = (base & (emx+epx > st)).sum()/base.sum()
    print(f"2-arm Esum>{st} MeV: corr {corr*R:8.1f} Hz  X17 kept {keep:.3f}")
