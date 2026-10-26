#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_funding.py -- schemes.py -> funding/out/funding.html (standalone, no external loads).

    python funding/build_funding.py
    cp funding/out/funding.html ~/PycharmProjects/dylan-cern-site/pages/facilities/funding.html

Also writes funding/out/funding_schemes.csv (one row per scheme and person) for spreadsheets.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import schemes as S

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
STATUSES = {"yes", "likely", "check", "ask", "no"}


def main():
    OUT.mkdir(exist_ok=True)
    people = {p["id"] for p in S.PEOPLE}
    for s in S.SCHEMES:
        assert s["region"] in S.REGIONS and s["kind"] in S.KINDS, s["id"]
        assert set(s["elig"]) == people, s["id"]
        assert all(v[0] in STATUSES for v in s["elig"].values()), s["id"]
        assert s["conf"] in {"set", "indicative", "expected"}, s["id"]
    data = dict(updated=S.UPDATED, dylan=S.DYLAN, people=S.PEOPLE, kinds=S.KINDS, regions=S.REGIONS,
                schemes=S.SCHEMES, plan=S.PLAN, todo=S.TODO)
    html = (HERE / "funding_template.html").read_text(encoding="utf-8")
    html = html.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False))
    (OUT / "funding.html").write_text(html, encoding="utf-8")

    with open(OUT / "funding_schemes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["scheme", "region", "kind", "size", "deadline", "deadline_conf", "when", "fit", "person", "status", "why"])
        for s in S.SCHEMES:
            for pid, (st, why) in s["elig"].items():
                w.writerow([s["name"], s["region"], s["kind"], s["size"], s["deadline"] or "", s["conf"], s["when"], s["fit"],
                            pid, st, why])
    print(f"wrote {OUT / 'funding.html'} ({len(S.SCHEMES)} schemes)")


if __name__ == "__main__":
    main()
