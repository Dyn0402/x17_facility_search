#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_scan.py -- results/scan_v1.csv: one row per cell configuration G1-G6, the
table HANDOFF_SIM.md §7 asks for, from the lxplus campaign outputs.

    python3 make_scan.py --base /eos/experiment/ntof/data/x17/ill \\
        --reach analysis/v3_base/results.json analysis/v3_timing/results.json \\
        -o scan_v1.csv

Sources: contracts/C1_<cfg>/accounting.json (analog neutrons, ³He(n,γ) x1e5),
contracts/C1w_<cfg> (wall-biased; preferred for wall pairs when present),
contracts/C1g_<cfg> (³He(n,γ) x1e7), S1/summary/<cfg>_<ch>/{pairs.json,events.npz},
and sim_report.py results.json for the reach columns.  All rates are per
neutron absorbed in the gas.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

import sim_feasibility as SF

GEOM = {"G1": (1, 40, "mylar 12 µm"), "G2": (1, 100, "mylar 12 µm"),
        "G3": (2, 40, "Kapton 0.11 mm"), "G4": (2, 100, "Kapton 0.29 mm"),
        "G5": (3, 40, "Kapton 0.23 mm"), "G6": (3, 100, "Kapton 0.57 mm")}
WALLS = ("He3Cell_Window", "He3Cell_Skin", "He3Cell_Rods", "He3Cell_EndUp",
         "He3Cell_EndDown", "He3Cell_Scraper")


def contract(base: Path, run: str, cfg: str):
    f = base / "contracts" / f"{run}_{cfg}" / "accounting.json"
    return json.load(open(f)) if f.exists() else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--reach", type=Path, nargs="*", default=[],
                    help="sim_report.py results.json files (labelled by their dir name)")
    ap.add_argument("-o", "--out", type=Path, required=True)
    a = ap.parse_args()
    reach = {p.parent.name: json.load(open(p)) for p in a.reach if p.exists()}
    rows = []
    for cfg in SF.CONFIGS:
        bar, R, skin = GEOM[cfg]
        r = dict(config=cfg, pressure_bar=bar, radius_mm=R, skin=skin)
        c1 = contract(a.base, "C1", cfg)
        if c1:
            pa = c1["per_absorbed"]
            r["absorbed_per_primary"] = c1["absorbed_np_per_primary"]
            r["aperture_acceptance"] = c1["aperture_acceptance"]
            for w in WALLS:
                r[f"cap_{w.split('_')[1].lower()}"] = pa.get(f"budget.{w}.nCapture", 0.0)
            r["cap_air"] = pa.get("budget.World.nCapture", 0.0)
            r["cap_detector"] = sum(v for k, v in pa.items() if k.endswith(".nCapture")
                                    and k.startswith("budget.") and k[7:-9] not in WALLS
                                    and k[7:-9] not in ("He3Gas", "World"))
            r["lif6_absorbed"] = pa.get("budget.He3Cell_Scraper.neutronInelastic", 0.0)
            for k in ("gap.prompt", "gap.all", "legs.prompt", "pairtags.prompt",
                      "wallpair_gaps", "wallpair_gaps_2arm"):
                r[k.replace(".", "_")] = pa.get(k, np.nan)
        cw = contract(a.base, "C1w", cfg)
        if cw:
            pw = cw["per_absorbed"]
            r["wallpair_gaps_C1w"] = pw.get("wallpair_gaps", np.nan)
            r["wallpair_gaps_2arm_C1w"] = pw.get("wallpair_gaps_2arm", np.nan)
            r["pairtags_prompt_C1w"] = pw.get("pairtags.prompt", np.nan)
        cg = contract(a.base, "C1g", cfg)
        if cg:
            r["pairtags_he3ng_C1g"] = cg["per_absorbed"].get("pairtags.prompt", np.nan)
        for ch in ("X17", "M1", "E0"):
            d = a.base / "S1" / "summary" / f"{cfg}_{ch}"
            if not (d / "pairs.json").exists():
                continue
            pj = json.load(open(d / "pairs.json"))["channels"]
            pj = pj.get(ch) or pj["IPC"]           # M1/E0 summaries are keyed "IPC"
            r[f"{ch}_acc_mm_2arm"] = pj["acc_mm_2arm"]
            r[f"{ch}_acc_x_eff_strict"] = pj["acc_x_eff"]
            z = SF.load_s1(a.base / "S1" / "summary", cfg, ch)
            for menu, ec in (("sipm2", 0.0), ("sipm2", 12.0), ("strict", 12.0)):
                r[f"{ch}_acc_x_eff_{menu}_E{ec:g}"] = SF.s1_select(z, menu, ec).sum() / z["N"]
            if ch == "X17":
                r["vertex_sigma_along_mm"] = pj["vertex_sigma_along_mm"]
                r["vertex_sigma_across_mm"] = pj["vertex_sigma_across_mm"]
            for est, e in pj["estimators"].items():
                for win in ("all", "win_100_180"):
                    r[f"{ch}_{est}_{win}_sigma68"] = e[win]["sigma68"]
                    r[f"{ch}_{est}_{win}_bias"] = e[win]["bias"]
        for lab, res in reach.items():
            for key in ("sipm2/E>12", "sipm2/E>13", "strict/E>12"):
                b = res["configs"].get(cfg, {}).get(key, {}).get("best")
                if b:
                    k = f"{lab}_{key.replace('/', '_').replace('>', 'gt')}"
                    r[f"{k}_reach3"] = 3 * b["sigma"]
                    r[f"{k}_bestR"] = b["R"]
                    r[f"{k}_x17_at_ref"] = SF.X17_REF * b["X17"]
                    for comp in ("M1", "E0", "G", "ACC", "COS", "WALL"):
                        r[f"{k}_{comp}"] = b[comp]
        rows.append(r)
    df = pd.DataFrame(rows)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(a.out, index=False)
    print(df.T.to_string(float_format=lambda x: f"{x:.3g}"))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
