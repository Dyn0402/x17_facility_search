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
import os
import json
from pathlib import Path

import items as I

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"


def main():
    OUT.mkdir(exist_ok=True)
    for i, it in enumerate(I.ITEMS):
        it.setdefault("row", i + 2)
    data = dict(updated=I.UPDATED, groups=I.GROUPS, items=I.ITEMS, presets=I.PRESETS, feedback_endpoint=os.environ.get("BUDGET_FEEDBACK_ENDPOINT", I.FEEDBACK_ENDPOINT),
                mm_status=I.MM_STATUS)
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

    write_feedback_csv()

    for p in I.PRESETS:
        tot = [0, 0, 0]
        for it in I.ITEMS:
            o = next(o for o in it["options"] if o["id"] == it["presets"][p["id"]])
            if o["cost"]:
                tot = [a + b for a, b in zip(tot, o["cost"])]
        print(f"{p['name']:16s} €{tot[1]/1e3:6.1f}k  ({tot[0]/1e3:.1f}–{tot[2]/1e3:.1f}k)")
    print("wrote", OUT / "budget.html")


def opt_summary(it):
    def c(o):
        return f"€{o['cost'][1] / 1e3:.1f}k" if o["cost"] else "€?"
    return " | ".join(f"{o['kind']}: {o['label']} ({c(o)})" for o in it["options"])


def write_feedback_csv():
    """The collaborator feedback sheet: one row per item (row = FEEDBACK_ROW0 + index), then blank rows for new items.
    Uploaded once to Google Drive; the page links each item to its row."""
    conf = dict(confirmed="confirmed", quote="quoted", catalog="catalogue price", model="cost model",
                dylan="Dylan's estimate", guess="guess, to check", unknown="unknown")
    with open(OUT / "feedback_sheet.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Subsystem", "Item", "Priority", "Options (central price)", "Confidence", "Open questions",
                    "YOUR COMMENT / CORRECTION", "Suggested price (EUR)", "Source / quote / who to ask", "Your name"])
        G = {g["id"]: g["name"] for g in I.GROUPS}
        for it in I.ITEMS:
            confs = sorted({conf[o["conf"]] for o in it["options"]})
            w.writerow([G[it["group"]], it["name"], f"P{it['priority']}", opt_summary(it), ", ".join(confs),
                        " / ".join(it["questions"]), "", "", "", ""])
        for _ in range(10):
            w.writerow(["(something missing?)", "", "", "", "", "", "", "", "", ""])


if __name__ == "__main__":
    main()
