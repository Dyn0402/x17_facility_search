import numpy as np, sim_feasibility as SF
from pathlib import Path
C = Path("/eos/experiment/ntof/data/x17/ill/contracts")
c1 = SF.load_table(C, "C1", "G5"); g = SF.load_table(C, "C1g", "G5")
S = SF.merge_singles(SF.singles(c1, "sipm2"), SF.singles_he3ng(g, "sipm2"))
print("singles per arm:", [len(x[0]) for x in S], " E>6:", [(x[1] > 6).sum() for x in S])
for ec in (8.0, 12.0, 13.0, 14.0):
    v = [SF.accidental_hist(S, ec, np.random.default_rng(i)).sum() for i in range(4)]
    print(f"E>{ec}: per R^2 2tau, 4 seeds: " + " ".join(f"{x:.3e}" for x in v))
