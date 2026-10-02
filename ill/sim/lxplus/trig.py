import numpy as np, sim_feasibility as SF
from pathlib import Path
C = Path("/eos/experiment/ntof/data/x17/ill/contracts")
R, tau2 = 1.0e10, 5e-9
for cfg in ("G1", "G5"):
    t = SF.load_table(C, "C1", cfg)
    w = t["w"].astype(float)[:, None] / t["absorbed"]
    s = t["sipm_a"] > SF.SIPM_THR
    E = SF.arm_E(t, "a")
    print(cfg, "rows", len(w))
    for thr in (0.0, 2.0, 4.0, 6.0):
        sel = s & (E > thr)
        p = (w * sel).sum(0)                   # per absorbed n, per arm
        corr = float((w[:, 0] * (sel.sum(1) >= 2)).sum())
        acc = sum(p[a] * p[b] for a in range(4) for b in range(a + 1, 4)) * R * R * tau2
        print(f"  per-arm E>{thr}: singles/arm {p.mean():.2e}/n -> {p.mean()*R:.3g} Hz/arm; "
              f"correlated 2-arm {corr*R:.3g} Hz; accidental 2-arm (2tau 5ns) {acc:.3g} Hz")
    # mm-gated singles (what the offline analysis sees)
    sm = SF.arm_ok(t, "sipm2", "a")
    print(f"  MM+SiPM singles/arm {((w * sm).sum(0)).mean():.2e}/n")
k1 = SF.load_table(C, "K1", "G5")
live = k1["N_sim"] * SF.COSMIC_S_PER_MU
s = (k1["sipm_p"] > SF.SIPM_THR).sum(1) >= 2
print("cosmic sipm 2-arm trigger rate Hz", s.sum() / live, " any-arm sipm rate Hz", ((k1["sipm_p"] > SF.SIPM_THR).any(1)).sum() / live)
