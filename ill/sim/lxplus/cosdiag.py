import sys, numpy as np, sim_feasibility as SF
from pathlib import Path
E = Path("/eos/experiment/ntof/data/x17/ill")
k1 = SF.load_table(E/"contracts", "K1", "G5")
live = k1["N_sim"]*SF.COSMIC_S_PER_MU
print("K1 rows", len(k1["w"]), "live s", live, "keys", sorted(k for k in k1 if not k.startswith("_")))
m, th, es, dt = SF.two_arm_events(k1, "sipm2", 12.0)
ok = SF.arm_ok(k1, "sipm2", "p")
E_ = np.where(ok, SF.arm_E(k1, "p"), -1.0)
o = np.argsort(-E_, 1); r = np.arange(len(E_)); a1, a2 = o[:,0], o[:,1]
ls1, ls2 = k1["ls_p"][r,a1], k1["ls_p"][r,a2]
pl1, pl2 = k1["plast_p"][r,a1], k1["plast_p"][r,a2]
nhit = (k1["sipm_p"] > SF.SIPM_THR).sum(1)
print("cosmic sipm2 E>12 rate Hz", m.sum()/live)
for name, c in [("Esum<21", es < 21), ("Esum<18", es < 18), ("noLS(both<0.5MeV)", (ls1 < .5) & (ls2 < .5)),
                ("|dt|<1.5 true", np.abs(dt) < 1.5), ("|dt|<0.5 true", np.abs(dt) < .5),
                ("only 2 sipm arms", nhit == 2), ("theta 60-180", th > 60)]:
    print(f"  pass {name:20s} {(m & c).sum()/m.sum():.3f}")
cc = m & (es < 21) & (ls1 < .5) & (ls2 < .5)
print("  Esum<21 & noLS:", cc.sum()/m.sum(), " +|dt|<1.5:", (cc & (np.abs(dt) < 1.5)).sum()/m.sum(),
      " +|dt|<0.5:", (cc & (np.abs(dt) < .5)).sum()/m.sum())
print("  dt pct (true) of passing:", np.nanpercentile(np.abs(dt[m]), [10, 50, 90]))
print("  Esum pct:", np.percentile(es[m], [10, 50, 90]), " LS max pct", np.percentile(np.maximum(ls1, ls2)[m], [10, 50, 90]))
for cfg in ("G1", "G5"):
    z = SF.load_s1(E/"S1"/"summary", cfg, "X17")
    s = SF.s1_select(z, "sipm2", 12.0)
    es2 = z["_e_em"] + z["_e_ep"]
    nols = (z["E_ls_em"] < .5) & (z["E_ls_ep"] < .5)
    print(cfg, "X17 sipm2 E>12 n", s.sum(), " Esum<21", (s & (es2 < 21)).sum()/s.sum(), " noLS", (s & nols).sum()/s.sum(),
          " both", (s & nols & (es2 < 21)).sum()/s.sum())
    print("   X17 LS pct", np.percentile(np.maximum(z["E_ls_em"], z["E_ls_ep"])[s], [50, 75, 90]))
