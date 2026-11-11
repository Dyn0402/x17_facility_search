"""Data for the "Review + flat cap (11 Nov)" tab of lnl_target_design.html, and the LNL target blocks of the site.

Everything comes from lnl/target/review_data.py (verdicts, the proposed cap, the Li → LiOH table, the baseline) and
lnl/target/shapes/nd_reach_io.py (days to 3σ, the reference fit).  Nothing here touches the 3D pair data of the other
tabs (SHAPES / SKETCH / CULINER blocks), so it is safe to re-run after every new Geant4 result (L13, L14, thin Li).

Writes, between marker comments only:
  1. lnl/viz/lnl_target_design.html      // REVIEW_DATA_BEGIN … // REVIEW_DATA_END     (const RVD = {...})
  2. the site copy pages/facilities/lnl-target.html = the page with the import map pointed at the vendored three.js
  3. pages/facilities/lnl.html           <!-- LNL_TARGET_STATS_BEGIN/END -->, <!-- LNL_TARGET_STATUS_BEGIN/END -->
  4. pages/facilities/index.html         <!-- LNL_HUB_LINE_BEGIN/END -->

    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/viz/export_review_viz.py            # all four
    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/viz/export_review_viz.py --no-site  # the repo page only

It does not run the site build or deploy.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LNL = HERE.parent
sys.path.insert(0, str(LNL / 'target'))
import review_data as R  # noqa: E402

nd = R.nd
HTML = HERE / 'lnl_target_design.html'
SITE = Path.home() / 'PycharmProjects' / 'dylan-cern-site'
CDN = ('"three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js"',
       '"three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"')
VENDORED = ('"three": "../js/vendor/three/three.module.js"', '"three/addons/": "../js/vendor/three/addons/"')

# design rows of the verdict table, live options first, in the order we would build them.
# (verdict key, name, who, [(Geant4 tag, variant label), ...]).  Tags without a row in nd_reach are skipped.
DESIGNS = [
    ('cu_ogive', 'Cu ogive 200 µm, Ø50 × 63 mm (his CAD), electroformed in hard copper', 'Pierfrancesco, 27 Oct',
     [('ogCu200_tip', 'Li pressed on the tip only'), ('ogCu200', 'Li over the inside, as simulated in run L11')]),
    ('al_cu_plated', 'Al ogive, Cu plated over the whole inside, Li pressed on the tip', 'us (option B of 4 Nov)',
     [('ogAl400cu12_tip', 'wall 0.4 mm'), ('ogAl300cu12_tip', 'wall 0.3 mm')]),
    ('cu_cup', 'Cu cup (hemisphere), rolled Li pressed on: the target of the CN neutron line', 'LNL, exists',
     [('dome300', '300 µm, as it exists'), ('dome200', '200 µm')]),
    ('al_cu_liner', 'Al ogive, Cu patch at r ≤ 8 mm, Li evaporated through a mask to r ≤ 4 mm', 'us, sent 4 Nov',
     [('ogAl400cu12r8m4', 'wall 0.4 mm'), ('ogAl300cu12r8m4', 'wall 0.3 mm')]),
    ('al_ti', 'Al ogive 0.3 mm with a 15 µm Ti stop', 'us', [('ogAl300ti15r8m4', '')]),
    ('diamond', 'CVD diamond window Ø20 at 45°, Mo 8 µm stop, Ti rings', 'his idea 2, our choice of 26 Oct',
     [('win45d200', 'diamond 200 µm'), ('win45d300', 'diamond 300 µm')]),
    ('diamond', 'Flat Li / Mo 8 µm / diamond 50 µm on a Cu ring in a CFRP chamber', 'us, 22 Oct',
     [('li20_mo8_dia50', 'ideal chamber'), ('flat1mm', 'a chamber that holds vacuum')]),
    ('mo', 'Al ogive with a Mo 8 µm liner', 'us, 27 Oct', [('ogAl300mo8_los', 'wall 0.3 mm')]),
    ('be', 'Beryllium ogive, hemisphere or end piece, with a Mo stop', 'us, the "upgrade"',
     [('ogBe300mo8_los', 'Be ogive 0.3 mm'), ('domeBe200mo8', 'Be hemisphere 0.2 mm'), ('win45be', 'window on a Be end piece')]),
    ('thin_film', 'Thin Li₂O film (300 µg/cm²) on 10 µm Al in a CFRP chamber, beam to a dump', 'ATOMKI style, our October baseline',
     [('base', '')]),
]
LI_UM = (10, 12, 15, 20)


def _n(x: float):
    return None if (x is None or x != x or math.isinf(x)) else round(float(x), 4)


def _days(tag: str) -> dict:
    b, a, an = R.days3(tag)
    return dict(big=_n(b), asb=_n(a), asb_ntof=_n(an))


def cap_variants() -> list[dict]:
    """the cap rows: the reference tag, then the alternatives that have Geant4 rows; est=True while L14 is missing."""
    out = []
    labs = {R.CAP['tag']: 'face 0.4 mm', 'cap45al500cu': 'face 0.5 mm', 'cap45al400cu_ep03': 'face 0.4 mm, end piece 0.3 mm'}
    for tag in (R.CAP['tag'],) + tuple(R.CAP['alt']):
        if tag != R.CAP['tag'] and not nd.has(tag):
            continue
        c = R.cap_days(tag=tag)
        out.append(dict(tag=tag, lab=labs.get(tag, tag), big=_n(c['big']), asb=_n(c['asb']), asb_ntof=_n(c['asb_ntof']),
                        est=not c['g4'], src=c['tag']))
    return out


def cap_thin() -> list[dict]:
    """days for the cap against the Li thickness (along the beam): Geant4 L14 thin-Li rows, else the window's."""
    out = []
    for um in LI_UM:
        sfx = '' if um == 20 else f'_li{um}'
        own, proxy = R.CAP['tag'] + sfx, R.CAP['proxy'] + sfx
        tag = own if nd.has(own) else proxy
        if not nd.has(tag):
            continue
        out.append(dict(um=um, est=tag != own, src=tag, **_days(tag)))
    return out


def build() -> dict:
    cd = R.cap_days()
    rows = [dict(key='cap', level='propose', label=R.LEVELS['propose'], short=R.VERDICT['cap']['short'],
                 why=R.VERDICT['cap']['why'], name='One-piece Al end cap, flat face at 45°, Cu stop, rolled Li pressed on',
                 who='new, 11 Nov', var=cap_variants())]
    for key, name, who, tags in DESIGNS:
        var = [dict(tag=t, lab=lab, est=False, **_days(t)) for t, lab in tags if nd.has(t)]
        if not var:
            continue
        v = R.verdict(tags[0][0])
        assert v['key'] == key, (key, v['key'])
        rows.append(dict(key=key, level=v['level'], label=v['label'], short=v['short'], why=v['why'], name=name, who=who, var=var))
    # what the 4 Nov liner design gains on his Cu ogive (both Li assumptions for his; like for like with big plastics)
    his, lin = ('ogCu200', 'ogCu200_los'), ('ogAl400cu12r8m4', 'ogAl300cu12r8m4')
    asb = [nd.best(h, 'asb', 1100, r) / nd.best(a, 'asb', 1100, r) for h in his for a in lin for r in (nd.CAL, nd.AS_NTOF)]
    big = [nd.best('ogCu200_los', 'bigP', 1100) / nd.best(a, 'bigP', 1100) for a in lin]
    li = {}
    for ep in (1100, 1030):
        s, e = R.li_table(ep), R.li_eout(ep)
        li[str(ep)] = dict(share=[[round(float(x), 4) for x in s.loc[um]] for um in LI_UM],
                           eout=[[round(float(x), 1) for x in e.loc[um]] for um in LI_UM])
    conv = [float(c) for c in R.li_table().columns]
    return dict(
        date=R.DATE, review=R.REVIEW, levels=R.LEVELS, rows=rows,
        cap=dict(name=R.CAP['name'], sub=R.CAP['sub'], stack=R.CAP['stack'], pros=R.CAP['pros'], cons=R.CAP['cons'],
                 press=R.CAP['press'], heat=R.CAP['heat_K'], cost=R.CAP['cost'], trace=R.CAP['trace_sigma_vs_diamond'],
                 g4=bool(cd['g4']), note=cd['note'], thin=cap_thin()),
        liner_gain=dict(asb=[round(min(asb), 2), round(max(asb), 2)], big=[round(min(big), 2), round(max(big), 2)]),
        li=dict(um=list(LI_UM), conv=conv, ep=li, yield_rel={str(k): round(v, 3) for k, v in R.li_yield_rel().items()},
                headline=R.LI['headline'], fix=R.LI['fix'], rate=R.LI['rate']),
        baseline=[list(b) for b in R.BASELINE], beam_pipe=R.BEAM_PIPE, fit=nd.LABEL, asb_note=nd.ASB_NOTE)


def splice(text: str, a: str, b: str, body: str, where: str) -> str:
    if a not in text or b not in text:
        sys.exit(f'{where}: markers {a} / {b} not found')
    i, j = text.index(a), text.index(b) + len(b)
    return text[:i] + a + '\n' + body + '\n' + b + text[j:]


# --------------------------------------------------------------------------- #
# the site's LNL page and hub line (plain HTML, same numbers)
# --------------------------------------------------------------------------- #
f = nd.fmt


def _f(x):
    return '–' if x is None else f(x)


def _rng(vals):
    """'a' or 'a–b' over the variants that have a number."""
    v = sorted(x for x in vals if x is not None)
    if not v:
        return '–'
    lo, hi = f(v[0]), f(v[-1])
    return lo if lo == hi else f'{lo}–{hi}'


def site_blocks(D: dict) -> tuple[str, str, str]:
    cap = D['rows'][0]
    c0 = cap['var'][0]
    thin = {t['um']: t for t in D['cap']['thin']}
    est = c0['est']
    how = ('estimate from the 45° diamond window’s Geant4, Geant4 for the cap is running (run L14)' if est
           else 'Geant4 run L14')
    t12 = thin.get(12)
    cu = next(r for r in D['rows'] if r['key'] == 'cu_ogive')
    cu0 = cu['var'][0]
    li = D['li']
    half20 = li['ep']['1100']['share'][li['um'].index(20)][li['conv'].index(0.5)]
    full12 = li['ep']['1100']['share'][li['um'].index(12)][-1]
    y10, y12 = li['yield_rel']['10'], li['yield_rel']['12']
    stats = f'''    <ul class="stats">
      <li><span class="n">~{_f(c0['big'])} d</span><span class="k">ATOMKI ratio at 3σ, big plastics</span>
        <span class="s">the proposed flat Al end cap, 1 µA, 1.10 MeV, 20 µm Li ({how}){f"; {_f(t12['big'])} d with 12 µm of Li" if t12 else ""}</span></li>
      <li><span class="n">{_f(c0['asb'])} / {_f(c0['asb_ntof'])} d</span><span class="k">n_TOF hardware as built</span>
        <span class="s">liquid scintillators repaired / as they ran at n_TOF{f"; {_f(t12['asb'])} / {_f(t12['asb_ntof'])} d with 12 µm of Li" if t12 else ""}. Assumes a 0.3 ns arm-to-arm time of flight that is not measured yet</span></li>
      <li><span class="n">{_f(cu0['asb'])} / {_f(cu0['asb_ntof'])} d</span><span class="k">the Cu ogive, buildable now</span>
        <span class="s">as built, same two liquid states; {_f(cu0['big'])} d with big plastics (Geant4 run L11, Li on the tip)</span></li>
      <li><span class="n">0</span><span class="k">neutrons</span>
        <span class="s">below E_p = 1.88 MeV</span></li>
    </ul>'''

    def tr(r):
        v = r['var']
        return (f'<tr><td>{"<b>" if r["level"] == "propose" else ""}{r["name"]}{"</b>" if r["level"] == "propose" else ""}'
                f'{" (estimate, Geant4 running)" if any(x["est"] for x in v) else ""}</td>'
                f'<td>{_rng(x["big"] for x in v)}</td><td>{_rng(x["asb"] for x in v)}</td><td>{_rng(x["asb_ntof"] for x in v)}</td>'
                f'<td>{r["short"]}</td></tr>')
    live = '\n        '.join(tr(r) for r in D['rows'] if r['level'] != 'drop')
    drop = '\n        '.join(tr(r) for r in D['rows'] if r['level'] == 'drop')
    status = f'''    <h2>The target: where it stands ({D['date']})</h2>
    <p>On 11 Nov every target design was checked against how lithium targets are really made, at LNL and elsewhere
      (<code>lnl/target/TARGET_REVIEW.md</code>). <b>This is a proposal. It has not been discussed with Pierfrancesco yet.</b></p>
    <ul>
      <li><b>Proposed: a one-piece aluminium end cap with a flat face at 45°.</b> Al 6061-T6, face 0.4–0.5 mm over a Ø20 bore,
        a Cu layer (≥ 12 µm along the beam) that stops the beam, and LNL's own rolled lithium pressed on with flat moulds.
        Flat parts only, and the film is uniform along the beam by geometry. Days: {_f(c0['big'])} d with big plastics,
        {_f(c0['asb'])} / {_f(c0['asb_ntof'])} d as built ({how}).</li>
      <li><b>If the ogive is kept</b>, the order is: first Pierfrancesco's Cu ogive, electroformed in hard copper, with the Li pressed on
        the tip only. Then the Al ogive (0.4 mm) with Cu plated over the whole inside. The 4 Nov design (Cu patch, masked evaporated Li)
        is possible but a development project of months, and as built it gains only ×{D['liner_gain']['asb'][0]:.1f}–{D['liner_gain']['asb'][1]:.1f} on the Cu ogive.</li>
      <li><b>Lithium 10–12 µm, not 20.</b> Residual water turns lithium into LiOH, which slows the beam more. With half of a 20 µm film
        converted, {100 * half20:.0f} % of the γ₀ comes from the 441 keV resonance at 1.10 MeV. A 12 µm film stays at {100 * full12:.0f} % even fully
        converted, for {100 * y10:.0f}–{100 * y12:.0f} % of the yield (10–12 µm). How fast the film converts at LNL's vacuum is not known. A one-week film test decides.</li>
      <li><b>Dropped:</b> every beryllium part (no supplier of machined Be vacuum parts since 2023), every molybdenum stop at 1 µA
        (its K x-rays fill the Micromegas) and the diamond (at 1.1 W an aluminium face is enough). The thin LiF / Li₂O film of the
        October study is not a fallback at LNL: such films lasted hours to two days on AN2000.</li>
      <li><b>Nothing is deposited inside the beam pipe.</b> No laboratory does that. LNL rolls and presses lithium in an argon glovebox.</li>
    </ul>
    <div class="table-scroll">
    <table class="data-table">
      <thead><tr><th>Target design (1 µA, 1.10 MeV, 20 µm Li)</th><th>3σ, big plastics</th><th>as built, liquid repaired</th><th>as built, liquid as at n_TOF</th><th>verdict, 11 Nov</th></tr></thead>
      <tbody>
        {live}
        <tr><td colspan="5"><b>Dropped on 11 Nov</b> (kept as a record)</td></tr>
        {drop}
      </tbody>
    </table>
    </div>
    <p class="note-summary">Days to 3σ at the ATOMKI ratio, {D['fit']} (θ × |y| × E_sum), m_X 16.8. A range covers the variants
      simulated. {D['asb_note']} The interactive page has the drawing, the build sequence and the questions for Pierfrancesco:
      <a href="lnl-target.html#review">the target designs, reviewed</a>.</p>'''
    hub = (f'          <li><a href="lnl.html">LNL Legnaro</a><span>⁸Be at 3σ, 1 µA: flat Al cap {_f(c0["big"])} d (big plastics), '
           f'{_f(c0["asb"])} / {_f(c0["asb_ntof"])} d as built ({"estimate" if est else "Geant4"}); Cu ogive {_f(cu0["big"])} d, '
           f'{_f(cu0["asb"])} / {_f(cu0["asb_ntof"])} d</span></li>')
    return stats, status, hub


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--no-site', action='store_true', help='only splice the data block into lnl/viz/lnl_target_design.html')
    a = ap.parse_args()
    D = build()
    blob = 'const RVD = ' + json.dumps(D, separators=(',', ':'), ensure_ascii=False) + ';'
    html = splice(HTML.read_text(encoding='utf-8'), '// REVIEW_DATA_BEGIN', '// REVIEW_DATA_END', blob, HTML.name)
    HTML.write_text(html, encoding='utf-8')
    c = D['rows'][0]['var'][0]
    print(f'{HTML}: {len(D["rows"])} designs; cap {c["big"]} / {c["asb"]} / {c["asb_ntof"]} d '
          f'({"ESTIMATE via " + c["src"] if c["est"] else "Geant4 L14"}); thin Li rows {[t["src"] for t in D["cap"]["thin"]]}')
    if a.no_site:
        return
    if not SITE.exists():
        print(f'{SITE} not found: site copies not written')
        return
    for old, new in zip(CDN, VENDORED):
        if old not in html:
            sys.exit(f'import map line not found: {old}')
        html = html.replace(old, new)
    (SITE / 'pages/facilities/lnl-target.html').write_text(html, encoding='utf-8')
    stats, status, hub = site_blocks(D)
    p = SITE / 'pages/facilities/lnl.html'
    t = p.read_text(encoding='utf-8')
    t = splice(t, '<!-- LNL_TARGET_STATS_BEGIN -->', '<!-- LNL_TARGET_STATS_END -->', stats, p.name)
    t = splice(t, '<!-- LNL_TARGET_STATUS_BEGIN -->', '<!-- LNL_TARGET_STATUS_END -->', status, p.name)
    p.write_text(t, encoding='utf-8')
    q = SITE / 'pages/facilities/index.html'
    t = q.read_text(encoding='utf-8')
    q.write_text(splice(t, '<!-- LNL_HUB_LINE_BEGIN -->', '<!-- LNL_HUB_LINE_END -->', hub, q.name), encoding='utf-8')
    print(f'site: {p.parent}/lnl-target.html (copy, vendored three.js), lnl.html (2 blocks), index.html (1 line)')


if __name__ == '__main__':
    main()
