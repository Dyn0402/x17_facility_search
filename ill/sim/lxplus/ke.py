import numpy as np, sim_feasibility as SF
from pathlib import Path
E = Path("/eos/experiment/ntof/data/x17/ill/S1/summary")
for cfg in ("G1", "G5"):
    z = SF.load_s1(E, cfg, "X17")
    allm = np.ones(len(z["theta"]), bool)
    for lab, m in (("2-arm MM", allm), ("sipm2", SF.s1_select(z, "sipm2", 0)), ("sipm2 E>12", SF.s1_select(z, "sipm2", 12))):
        soft = np.minimum(z["em_ke"], z["ep_ke"])[m]; hard = np.maximum(z["em_ke"], z["ep_ke"])[m]
        print(f"{cfg} {lab:11s} n={m.sum():7d} softer KE p10/50/90 {np.percentile(soft,[10,50,90]).round(1)}  harder {np.percentile(hard,[10,50,90]).round(1)}  "
              f"frac soft<3 {np.mean(soft<3):.2f} <5 {np.mean(soft<5):.2f}  theta_true p16/50/84 {np.percentile(z['theta'][m],[16,50,84]).round(1)}")
    zm = SF.load_s1(E, cfg, "M1"); m = SF.s1_select(zm, "sipm2", 12)
    print(f"{cfg} M1 sipm2 E>12 theta_true p16/50/84 {np.percentile(zm['theta'][m],[16,50,84]).round(1)}  reco nomline {np.percentile(zm['reco_nomline'][m],[16,50,84]).round(1)}")
