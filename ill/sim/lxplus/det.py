import numpy as np, sim_feasibility as SF
from pathlib import Path
E = Path("/eos/experiment/ntof/data/x17/ill")
s1 = {c: SF.load_s1(E / "S1/summary", "G5", c) for c in ("X17", "M1", "E0")}
tabs = {r: SF.load_table(E / "contracts", r, "G5") for r in ("C1", "C1w", "C1g")}
tabs["K1"] = SF.load_table(E / "contracts", "K1", "G5")
for ec in (12.0, 13.0):
    for tau, sig, dtc in ((2.5, .5, 1.5), (0.6, .2, .6), (2.5, .5, 1.5)):
        m = SF.model("G5", s1, tabs, "sipm2", ec, 1.9e10, 50, tau, sig, dtc, cache={})
        print(ec, tau, sig, "ACC/2tau", m["ACC"].sum() / (2 * tau), "COS", m["COS"].sum(), "G", m["G"].sum(),
              "WALL", m["WALL"].sum(), "3σ", 3 * SF.reach(m))
