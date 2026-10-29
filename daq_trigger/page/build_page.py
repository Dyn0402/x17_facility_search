#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_page.py -- the interactive trigger/DAQ page (daq_trigger/page/template.html -> out/mx17-daq-trigger.html).

    python daq_trigger/daq_plan.py               # tables first
    python daq_trigger/page/build_page.py        # embeds out/costs.csv and out/live.csv into the page
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py daq_trigger/out/mx17-daq-trigger.html \
        --slug mx17-daq-trigger --force --deploy

The page is self-contained (no external scripts or fonts), so it works offline from the site's notes.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "out"


def main():
    costs = pd.read_csv(OUT / "costs.csv")
    live = pd.read_csv(OUT / "live.csv")
    arch = []
    for a, g in costs.groupby("architecture", sort=False):
        parts = g[g.part != "TOTAL"]
        tot = g[g.part == "TOTAL"].iloc[0]
        arch.append(dict(name=a, total=[int(tot.low), int(tot.central), int(tot.high)],
                         parts=[dict(part=r.part, c=[int(r.low), int(r.central), int(r.high)]) for r in parts.itertuples()]))
    pres = [dict(name=r.scenario, f=float(r.offered_hz)) for r in live.itertuples()]
    html = (HERE / "template.html").read_text(encoding="utf-8")
    html = html.replace("/*COSTS*/[]", json.dumps(arch, ensure_ascii=False))
    html = html.replace("/*PRESETS*/[]", json.dumps(pres, ensure_ascii=False))
    out = OUT / "mx17-daq-trigger.html"
    out.write_text(html, encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
