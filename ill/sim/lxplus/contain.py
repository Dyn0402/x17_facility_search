import numpy as np, sim_feasibility as SF
from pathlib import Path
E = Path("/eos/experiment/ntof/data/x17/ill/S1/summary")
for cfg in ("G1", "G5"):
    for ch in ("X17", "M1"):
        z = SF.load_s1(E, cfg, ch)
        s = SF.s1_select(z, "sipm2", 0.0)
        dep = (z["E_sipm_em"] + z["E_plast_em"] + z["E_ls_em"] + z["E_sipm_ep"] + z["E_plast_ep"] + z["E_ls_ep"])[s]
        ke = (z["em_ke"] + z["ep_ke"])[s]
        print(cfg, ch, "N", z["N"], "sipm2 n", s.sum(), "acc", s.sum()/z["N"],
              "KEsum pct", np.percentile(ke, [10, 50, 90]).round(2),
              "dep/KE pct", np.percentile(dep/ke, [10, 50, 90]).round(2),
              "frac Esum>12", (z["_e_em"] + z["_e_ep"] > 12)[s].mean().round(3),
              "frac KEsum>14", (ke > 14).mean().round(3))
    print("  keys", [k for k in z if k.startswith("em_") or k.startswith("reco")])
