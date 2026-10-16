#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_budget.py -- items.py -> budget/out/budget.html (standalone, no external loads).

    python budget/build_budget.py
    cp budget/out/budget.html ~/PycharmProjects/dylan-cern-site/pages/facilities/budget.html

Also writes budget/out/budget_items.csv (one row per item option) for spreadsheets.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import items as I

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"


def main():
    OUT.mkdir(exist_ok=True)
    data = dict(updated=I.UPDATED, groups=I.GROUPS, items=I.ITEMS, presets=I.PRESETS)
    for it in I.ITEMS:
        ids = {o["id"] for o in it["options"]}
        for p, o in it["presets"].items():
            assert o in ids, f"{it['id']}: preset {p} -> unknown option {o}"
        assert it["group"] in {g["id"] for g in I.GROUPS}, it["id"]
    html = (HERE / "budget_template.html").read_text(encoding="utf-8")
    html = html.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False))
    (OUT / "budget.html").write_text(html, encoding="utf-8")

    with open(OUT / "budget_items.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["group", "item", "priority", "option", "kind", "eur_low", "eur_central", "eur_high", "confidence",
                    "in_lean", "in_self", "in_upgrade", "note"])
        for it in I.ITEMS:
            for o in it["options"]:
                c = o["cost"] or ["", "", ""]
                w.writerow([it["group"], it["name"], it["priority"], o["label"], o["kind"], *c, o["conf"],
                            *[int(it["presets"][p] == o["id"]) for p in ("lean", "self", "upgrade")], o["note"]])

    for p in I.PRESETS:
        tot = [0, 0, 0]
        for it in I.ITEMS:
            o = next(o for o in it["options"] if o["id"] == it["presets"][p["id"]])
            if o["cost"]:
                tot = [a + b for a, b in zip(tot, o["cost"])]
        print(f"{p['name']:16s} €{tot[1]/1e3:6.1f}k  ({tot[0]/1e3:.1f}–{tot[2]/1e3:.1f}k)")
    print("wrote", OUT / "budget.html")


if __name__ == "__main__":
    main()
