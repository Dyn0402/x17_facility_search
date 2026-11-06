#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_erc_cog.py -- the ERC Consolidator Grant 2027 eligibility page -> funding/out/erc-cog-2027.html (standalone).

    python3 funding/build_erc_cog.py
    cp funding/out/erc-cog-2027.html ~/PycharmProjects/dylan-cern-site/pages/facilities/erc-cog-2027.html

The write-up is ERC_COG_2027.md; rules come from the ERC Work Programme 2027 (binding text). The stylesheet is
taken from funding_template.html so the two pages look the same. Also writes erc_windows.csv (the chart's data).
"""
from __future__ import annotations

import csv
import html
import re
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
UPDATED = "2026-11-06"
PHD = date(2023, 11, 10)          # Dylan, UCLA (schemes.DYLAN["phd"])
WP = "https://ec.europa.eu/info/funding-tenders/opportunities/docs/2021-2027/horizon/wp-call/2027/wp_horizon-erc-2027_en.pdf"

# Windows of accepted PhD defence dates, by call. lo/hi are years before the 1 Jan cut-off of the call year.
# 2027 rows are the WP 2027; later rows assume FP10 keeps the WP 2027 windows ("assumed"); the "old rule" row is the
# 7-12 y window of WP 2021-2026, shown for comparison.
CALLS = [
    ("StG 2027", 2027, 0, 10, "WP 2027", "closed 14 Oct 2026"),
    ("CoG 2027", 2027, 5, 15, "WP 2027", "deadline 12 Jan 2027"),
    ("StG 2028", 2028, 0, 10, "assumed", "expected ~mid Oct 2027"),
    ("CoG 2028", 2028, 5, 15, "assumed", "expected ~late 2027 / early 2028"),
    ("CoG 2029", 2029, 5, 15, "assumed", "expected ~late 2028 / early 2029"),
    ("CoG 2029, old 7–12 y rule", 2029, 7, 12, "old rule", "if FP10 went back to 7–12 y"),
]


def yrs(d: date, cut: date) -> float:
    return (cut - d).days / 365.25


def windows():
    rows = []
    for name, y, lo, hi, basis, when in CALLS:
        cut = date(y, 1, 1)
        start, end = date(y - hi, 1, 1), date(y - lo - 1, 12, 31)
        ok = start <= PHD <= end
        rows.append(dict(name=name, year=y, lo=lo, hi=hi, basis=basis, when=when, start=start, end=end,
                         at_cut=yrs(PHD, cut), ok=ok))
    return rows


def chart(rows) -> str:
    x0, x1, W, L, rh = 2011, 2030, 980, 210, 34
    H = 46 + rh * len(rows)
    X = lambda d: L + (W - L - 16) * ((d.year + (d.timetuple().tm_yday - 1) / 365.25) - x0) / (x1 - x0)
    s = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Accepted PhD defence dates per ERC call, with Dylan\'s PhD date">']
    for y in range(x0 + 1, x1 + 1):
        xx = X(date(y, 1, 1))
        s.append(f'<line x1="{xx:.1f}" x2="{xx:.1f}" y1="22" y2="{H - 18}" stroke="var(--rule)"/>')
        if y % 2 == 0:
            s.append(f'<text x="{xx:.1f}" y="{H - 4}" font-size="11.5" text-anchor="middle">{y}</text>')
    for i, r in enumerate(rows):
        yy = 30 + i * rh
        col = "var(--yes)" if r["ok"] else "var(--no)"
        dash = ' stroke-dasharray="5 4" fill-opacity="0.18"' if r["basis"] != "WP 2027" else ' fill-opacity="0.32"'
        tip = (f'{r["name"]} ({r["basis"]}): PhD defended {r["start"]:%d %b %Y} – {r["end"]:%d %b %Y}; '
               f'Dylan {r["at_cut"]:.1f} y at the cut-off: {"eligible" if r["ok"] else "not eligible"}')
        s.append(f'<g><title>{html.escape(tip)}</title>'
                 f'<text x="{L - 10}" y="{yy + 15}" font-size="13" text-anchor="end">{html.escape(r["name"])}</text>'
                 f'<rect x="{X(r["start"]):.1f}" y="{yy + 3}" width="{X(r["end"]) - X(r["start"]):.1f}" height="{rh - 12}" rx="5" '
                 f'fill="{col}" stroke="{col}"{dash}/></g>')
    xp = X(PHD)
    s.append(f'<line x1="{xp:.1f}" x2="{xp:.1f}" y1="18" y2="{H - 18}" stroke="var(--warn)" stroke-width="2.5"/>'
             f'<text x="{xp + 5:.1f}" y="15" font-size="12.5" font-weight="600" fill="var(--warn)" style="fill:var(--warn)">'
             f'Dylan’s PhD, 10 Nov 2023</text>')
    s.append("</svg>")
    return "\n".join(s)


def table(head, body, cls="") -> str:
    h = "".join(f"<th>{c}</th>" for c in head)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in body)
    return f'<div class="tbl-wrap"><table class="{cls}" style="min-width:0"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def chip(st, txt=None):
    return f'<span class="chip st-{st}">{txt or st}</span>'


def page(rows) -> str:
    style = re.search(r"<style>.*?</style>", (HERE / "funding_template.html").read_text(encoding="utf-8"), re.S).group(0)
    cut27 = date(2027, 1, 1)
    short = date(2021, 12, 31)
    gap_m = (PHD.year - short.year) * 12 + PHD.month - short.month - (PHD.day < short.day)  # full months: 1 y 10 m

    calls_tbl = table(
        ["call", "defence dates accepted", "Dylan at cut-off", "", "basis", "when"],
        [[f"<b>{r['name']}</b>", f"{r['start']:%d %b %Y} – {r['end']:%d %b %Y}", f"{r['at_cut']:.1f} y",
          chip("yes", "eligible") if r["ok"] else chip("no", "not eligible"), r["basis"], r["when"]] for r in rows])

    glance = table(["", "ERC-2027-CoG"], [
        ["Call", "opened 24 Sep 2026, <b>deadline 12 Jan 2027</b>"],
        ["Budget", "€618.5 M, ~296 grants"],
        ["Grant", "up to €2 M for 60 months (pro rata if shorter), + up to €1 M additional funding (major equipment, access to "
                  "facilities, …); up to €2 M additional if the PI moves to the EU/AC from outside"],
        ["Funding model", "actual costs: 100 % of direct costs + 25 % flat indirect (subcontracts excluded)"],
        ["PI time", "≥ 40 % of working time on the project, ≥ 50 % in an EU member state or associated country"],
        ["Host", "one legal entity in the EU/AC (INFN-LNL qualifies); team members from anywhere"],
        ["Proposal", "B1: Part I synopsis + CV and track record; B2: Part II + resources and time commitment"],
        ["Evaluation", "Step 1 on B1 (results 16 Jul 2027); Step 2 on B2 + interview (results 17 Dec 2027); signature ~8 Apr 2028"],
        ["Eligibility", "PhD defended &gt; 5 and ≤ 15 years before 1 Jan 2027, i.e. 1 Jan 2012 – 31 Dec 2021; extensions only for "
                        "documented leave, illness, national service, disability, clinical training, …"],
        ["Independence", "“A Consolidator Grant PI should have already shown evidence of research independence.”"],
        ["Once per career", "“A researcher may be the PI of only one ERC Consolidator Grant in their career.” (being awarded one)"],
    ])

    people = table(["person", "CoG 2027", "why"], [
        ["Dylan", chip("no"), "PhD 10 Nov 2023: 3.1 y at the cut-off, needs &gt; 5 y. His scheme is the StG (eligible to the 2033 call)."],
        ["Pierfrancesco", chip("check", "probably no"), "needs a PhD defended 2012–2021; as Dirigente di Ricerca probably older than "
                                                       "15 y <b style='color:var(--ask)'>(ask)</b>. His ERC routes: Advanced (26 Aug 2027), Synergy (11 May 2027)."],
        ["Italian post-doc", chip("ask"), "eligible if the PhD was defended 1 Jan 2012 – 31 Dec 2021 (earlier only with extensions). "
                                         "The INFN interest form is due 4 Dec 2026, the call closes 12 Jan 2027: very short for a first ERC proposal."],
        ["Dylan as team member", chip("likely", "possible"), "any eligible PI's CoG can include him as a team member."],
    ])

    restr = table(["WP 2027 rule", "what it means for us"], [
        ["One eligible proposal per PI in all main-grant calls of the WP 2027; one proposal under evaluation at a time",
         "whoever submits CoG 2027 cannot also submit Synergy 2027 (11 May) or Advanced 2027 (26 Aug)"],
        ["B or C at Step 1 in StG/CoG 2026, or C at Step 1 in StG/CoG/AdG 2025, bars every 2027 main call",
         "none of us has applied: no effect"],
        ["A PI who has held a StG (CoG) cannot apply to the StG (CoG) again", "no effect"],
        ["StG 2027 drew 7,710 applications (+60 % on 2026) for ~373 grants",
         "~4.8 % success if the numbers hold. Expect StG 2028 to be as crowded, not 2026's 8.8 %"],
    ])

    plan = """
      <ol>
        <li><b>Reply to Pierfrancesco</b>: not eligible for CoG 2027 or 2028. The target is the <b>ERC Starting Grant 2028
          (~mid Oct 2027)</b> with LNL (or UNIPD) as host. Ask whether to tell the LNL Director and the Servizio Fondi Esterni now,
          so the support letter and the internal approval are planned. Draft in <code>funding/ERC_COG_2027.md</code> §7.</li>
        <li><b>Ask the Italian post-doc's PhD defence date.</b> If it is 2012–2021 they could still try CoG 2027, but the INFN form
          is due 4 Dec 2026.</li>
        <li><b>Spring 2027</b>: read the FP10 ERC work programme for 2028 (StG window, date, resubmission rules) and the INFN July
          2026 course material for StG/CoG; choose the host.</li>
        <li><b>Get the UCLA document stating the defence date</b>: the ERC counts the defence, not the conferral.</li>
      </ol>"""

    infn = """
      <ul>
        <li>LNL Servizio Fondi Esterni (Silvia Zanella, <code>fondiesterni.lnl@lnl.infn.it</code>) circulated the call on 24 Sep 2026 with
          the WP 2027, the ERC <i>Information for Applicants</i> and APRE's <i>Preparing an ERC project</i>.</li>
        <li>An INFN-hosted applicant tells the LNL Director (through the Servizio Fondi Esterni), gets approval from the Director and the
          President of the CSN (here CSN3), then fills the INFN Servizio Progetti <b>manifestazione di interesse</b> form by <b>4 Dec 2026</b>.
          No one in our group needs it for CoG 2027.</li>
        <li>The INFN national course “Bandi ERC StG e CoG 2027” (July 2026) is on the INFN Progetti SharePoint (INFN login). It covers the
          StG too and is worth reading in spring 2027.</li>
        <li>Expect the same internal gate for StG 2028, around Aug–Sep 2027 <b style="color:var(--check)">(check)</b>.</li>
      </ul>"""

    srcs = [
        ("ERC Work Programme 2027 (binding text): §1.1, Tables 1–6, §1.4.2.2", WP),
        ("ERC: Consolidator Grant", "https://erc.europa.eu/apply-grant/consolidator-grant"),
        ("ERC: Starting Grant", "https://erc.europa.eu/apply-grant/starting-grant"),
        ("ERC: changes to the 2026 and 2027 Work Programmes (2 Jun 2025)", "https://erc.europa.eu/news-events/news/changes-2026-and-2027-work-programmes"),
        ("ERC: StG 2027 applications, facts and figures (23 Oct 2026)", "https://erc.europa.eu/news-events/news/starting-grants-2027-applications-facts-and-figures"),
        ("UZH Research: ERC WP 2027 eligibility changes", "https://www.research.uzh.ch/en/news/ERC-WP-2027--Changes-to-eligibility-rules.html"),
        ("LNL Servizio Fondi Esterni: the CoG 2027 call", "https://www.lnl.infn.it/bando-erc-consolidator-grant-2027-erc-2027-cog/"),
    ]
    src_html = "".join(f'<li><a href="{u}">{html.escape(t)}</a></li>' for t, u in srcs)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ERC Consolidator Grant 2027: eligibility</title>
<meta name="description" content="Can Dylan apply to the ERC Consolidator Grant 2027? The Work Programme 2027 windows checked against his PhD date, the call, the new restrictions, and what to do instead.">
{style}
<style>
.mbox svg text {{ fill: var(--ink2); }}
.pcol p {{ max-width: 920px; }}
.no-verdict {{ border-left-color: var(--warn); }}
</style>
</head>
<body>
<div class="wrap pcol">
  <header class="top">
    <p class="crumb"><a href="./">← Facility studies</a> · <a href="funding.html">Funding: all schemes</a></p>
    <h1>ERC Consolidator Grant 2027: can Dylan apply?</h1>
    <p class="lede">Pierfrancesco forwarded LNL's notice of the ERC-2027-CoG call (deadline 12 Jan 2027) on 5 Nov 2026 and asked to check
      the time since the PhD. The rules are quoted from the binding ERC Work Programme 2027.
      <b style="color:var(--check)">check</b> marks a rule not yet published; <b style="color:var(--ask)">ask</b> a fact about a person we don't have.
      Updated {UPDATED}.</p>
  </header>

  <div class="tiles" style="margin-top:16px">
    <div class="tile hl"><b>No</b><span>CoG 2027 for Dylan</span></div>
    <div class="tile"><b>{yrs(PHD, cut27):.1f} y</b><span>PhD (10 Nov 2023) to the 1 Jan 2027 cut-off</span></div>
    <div class="tile"><b>&gt; 5 – 15 y</b><span>CoG 2027 window: defended 1 Jan 2012 – 31 Dec 2021</span></div>
    <div class="tile"><b>{gap_m // 12} y {gap_m % 12} m</b><span>how much earlier he would have needed to defend</span></div>
    <div class="tile"><b>2029</b><span>first CoG call open to him (if FP10 keeps 5–15 y; 2031 under the old 7–12 y)</span></div>
    <div class="tile"><b>~Oct 2027</b><span>ERC Starting Grant 2028: his next ERC call</span></div>
  </div>

  <div class="verdict no-verdict">
    <p><b>Dylan is not eligible for CoG 2027, and not for the 2028 CoG either.</b> The WP 2027 accepts a PhD defended more than 5 and at
      most 15 years before 1 Jan 2027, i.e. between 1 Jan 2012 and 31 Dec 2021. His was 10 Nov 2023, 3.1 years before. The
      extensions (parental leave, illness, national service, …) only lengthen the window at its old end; nothing shortens the 5 years.</p>
    <p><b>His ERC scheme is the Starting Grant.</b> The WP 2027 StG window is “&gt; 0 and ≤ 10 years” since the defence, so he can apply
      to every StG up to the 2033 call. StG 2027 closed on 14 Oct 2026; the next is <b>StG 2028, ~mid Oct 2027</b>, the first under FP10
      (date and rules <b style="color:var(--check)">check</b>). Pierfrancesco is right that we wait for the next call. It should be a
      Starting Grant, not a Consolidator.</p>
  </div>

  <h2>1. The windows, call by call</h2>
  <p class="small">Each bar is the range of PhD defence dates a call accepts. Solid: WP 2027. Dashed: later calls, assuming FP10 keeps the
    WP 2027 windows, and the old 7–12 y rule for comparison. Green = Dylan's date falls inside. Hover a bar for the dates.</p>
  <div class="mbox">{chart(rows)}</div>
  <div style="margin-top:12px">{calls_tbl}</div>
  <p class="small">The ERC counts the date of the <b>successful defence</b> of the first PhD (certificate required). If 10 Nov 2023 is
    UCLA's conferral date and the defence was earlier, the answer is the same: it would need to be before 1 Jan 2022.</p>

  <h2>2. The call at a glance</h2>
  {glance}

  <h2>3. Who in the group could use CoG 2027</h2>
  {people}

  <h2>4. New WP 2027 restrictions</h2>
  {restr}

  <h2>5. The INFN / LNL process</h2>
  <div class="card">{infn}</div>

  <h2>6. What to do</h2>
  <div class="card">{plan}</div>

  <h2>Sources</h2>
  <ul class="small">{src_html}</ul>
  <p class="small">Repository: <code>x17_facility_search/funding/ERC_COG_2027.md</code> (write-up) and <code>build_erc_cog.py</code> (this page).</p>
</div>
</body>
</html>
"""


def main():
    OUT.mkdir(exist_ok=True)
    rows = windows()
    assert not rows[1]["ok"] and rows[0]["ok"] and rows[2]["ok"] and not rows[3]["ok"] and rows[4]["ok"]
    (OUT / "erc-cog-2027.html").write_text(page(rows), encoding="utf-8")
    with open(OUT / "erc_windows.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["call", "cutoff", "min_years", "max_years", "defence_from", "defence_to", "basis", "dylan_years_at_cutoff", "dylan_eligible"])
        for r in rows:
            w.writerow([r["name"], f"{r['year']}-01-01", r["lo"], r["hi"], r["start"], r["end"], r["basis"], f"{r['at_cut']:.2f}", r["ok"]])
    print(f"wrote {OUT / 'erc-cog-2027.html'}")


if __name__ == "__main__":
    main()
