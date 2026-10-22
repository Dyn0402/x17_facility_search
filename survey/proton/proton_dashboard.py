#!/usr/bin/env python3
"""
proton_dashboard.py -- the data behind the proton-facility dashboard on the site
(dylan-neff.web.cern.ch/facilities/proton-facilities.html).  Called by survey/dashboard.py; writes
the site's data/facilities-proton.json and returns the short PROTON list the hub page shows.

Rows have the neutron dashboard's schema, so js/facilities-survey.js draws both pages:
  x17     X17 produced per day into 4π at the machine's full DC current, best claim it reaches, at the ATOMKI
          strength (no acceptance, no target cap): raw production only
  reach   one entry per claim the machine reaches, best first: soft = √(days/50), the strength (in units of
          ATOMKI's) reached at 3σ in 50 beam days; days = beam days to 3σ at the ATOMKI strength (big plastics);
          days_built = the same with the n_TOF stack as built
**Keep PEXTRA and PLOG current** as proton facilities are studied or contacted, then rerun survey/dashboard.py.
"""
from __future__ import annotations

import json
import math
from datetime import date
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / 'out'

EFFORT = {
    1: 'Catalogued: machine, energy range and a published current',
    2: 'Scaled model: proton_reach.py from the LNL / Demokritos Geant4',
    3: 'Dedicated study: analytic write-up',
    4: 'Geant4 study: full-apparatus simulation, write-up and slides',
}
CLASS_LABEL = {'underground': 'Underground', 'single-ended': 'Single-ended electrostatic', 'tandem': 'Tandem electrostatic',
               'BNCT / high-current': 'BNCT / high-current DC', 'linac / RFQ': 'Linac / RFQ'}
SHORT = {'be8': '⁸Be', 'he4': '⁴He', 'c12': '¹²C'}

# per key: effort, links, next, contact, updated (default effort 2: every modelled row; 1 if no claim is reachable)
PEXTRA = {
    'lnl_cn': dict(effort=4, links=[('LNL page', 'lnl.html'), ('Lithium target study', '../notes/lnl-lithium-target.html'),
                                    ('Target options', '../notes/lnl-target-options.html'),
                                    ('LNL feasibility deck', '../notes/lnl-x17-feasibility.html')],
                   next='Bench tests: MeV-proton blistering of diamond, Li adhesion on Ta-coated diamond; ask the LNL target lab (Li evaporation, Ta on diamond, braze)',
                   contact='in contact (LNL is a collaboration partner)', updated='2026-10-22'),
    'demokritos': dict(effort=4, links=[('Demokritos feasibility', '../notes/demokritos-x17-feasibility.html')],
                       next='3D fit and pseudo-data systematics at S/B ≈ 1 %; ask the post-upgrade current at 0.9 MeV',
                       updated='2026-10-19'),
    'luna_mv': dict(next='Ask LNGS: Ti-T targets underground, hall space for a 1.6 m apparatus, beam-time cycle (LUNA contact: Gustavino)'),
    'jrc_monnet': dict(next='Ask JRC: EUFRAT call, lowest proton energy, Ti-T and Li targets at 10-20 µA'),
    'felsenkeller': dict(next='Ask HZDR: proton current from the terminal RF source at 1-2 MeV; ChETEC/EURO-LABS TA'),
    'ptb_piaf': dict(next='Ask PTB: Tandetron proton current at 0.9-1.9 MeV; collaboration terms'),
    'npl': dict(next='Ask NPL: commissioning date of the 2 MV Tandetron; tritium targets'),
    'tunl_lena': dict(next='Ask TUNL: Singletron beam time for an external apparatus; tritium'),
    'notre_dame': dict(next='Ask ISNAP: 5U proton current at 1-2 MeV'),
    'ithemba_tandetron': dict(next='Ask iThemba: current at 0.5 MV terminal; astrophysics line space'),
    'irsn_amande': dict(next='Ask ASNR: DC proton current at 0.9-1.1 MeV, Ti-T targets, room for a 1.6 m apparatus in the hall '
                             '(also on the neutron dashboard: its fields are too weak for the ³He route)', updated='2026-10-22'),
    'atomki': dict(next='Collaboration question: a joint run on the Tandetron (our µRWELL demonstrator was already tested there)'),
}

PLOG = [
    ('2026-10-22', 'LNL target options: 20 µm Li on Ta-coated CVD diamond (×8 γ₀ per proton; < 150 °C to ~270 µA with a dry rim clamp, ~480 µA brazed). The thermal cap on ⁸Be targets is far above the survey\'s 20 µA estimate; hydrogen and adhesion on diamond are the open questions.', 'lnl_cn'),
    ('2026-10-22', 'Proton survey: 60 named machines and a census of 267 electrostatic accelerators. The target (≈ 4 µA thin, ≈ 20 µA cooled, est.) caps the reach, so above ~20 µA every machine gives ⁸Be at 3σ in ~1.3 h (big plastics). POTENTIAL: LUNA-MV, JRC MONNET, Felsenkeller, PTB, TUNL LENA, Notre Dame, iThemba.', 'luna_mv,jrc_monnet,felsenkeller,ptb_piaf,tunl_lena,notre_dame,ithemba_tandetron'),
    ('2026-10-22', '"Studied" is now a flag (ring colour), not a verdict: LNL and Demokritos show as POTENTIAL. AMANDE (Cadarache) cross-listed on the neutron dashboard.', 'lnl_cn,demokritos,irsn_amande'),
    ('2026-10-22', 'LNL lithium target study: Li₂O on a cooled clamped disk, no LiF above 441 keV.', 'lnl_cn'),
    ('2026-10-19', 'Demokritos: ³H(p,e⁺e⁻)⁴He Geant4, 3.6 d (big plastics) / 35 d (as built) at 1 µA.', 'demokritos'),
    ('2026-10-12', 'LNL: Geant4 3D fit, ⁸Be at 3σ in 1.0 d (big plastics) / 17 d (as built) at 1 µA.', 'lnl_cn'),
]


def _f(x):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def build(site_json: Path):
    tri = pd.read_csv(OUT / 'triage.csv', keep_default_na=False, na_values=[''])
    rows = []
    for r in tri.itertuples():
        e = PEXTRA.get(r.key, {})
        claims = [c for c in str(r.claims).split(',') if c and c != 'nan']
        reach = []
        for c in claims:
            d, db = _f(getattr(r, f'{c}_days_big')), _f(getattr(r, f'{c}_days_built'))
            iu = _f(getattr(r, f'{c}_iuse'))
            reach.append(dict(model=f'{SHORT[c]} at {iu:g} µA', claim=c, soft=math.sqrt(d / 50), soft_flat=None, all=None,
                              floor=None, days=d, days_flat=None, days_built=db))
        reach.sort(key=lambda x: x['days'])
        i_note = '' if pd.isna(r.i_note) else str(r.i_note)
        beam = f'p {r.e_lo:g}–{r.e_hi:g} MeV, {r.i_dc:g} µA DC' + (' (class default)' if r.i_est else '')
        rows.append(dict(
            key=r.key, name=r.facility, site=r.site, kind=r.machine, beam=beam, cls=r.cls,
            cls_label=CLASS_LABEL.get(r.cls, r.cls), status=r.status, number=f'{r.i_dc:g} µA DC' + (f' ({i_note})' if i_note else ''),
            verdict=r.verdict, reason=r.reason, source=r.source,
            effort=e.get('effort', 2 if claims else 1), effort_label=EFFORT[e.get('effort', 2 if claims else 1)],
            effort_note=e.get('effort_note', ''), links=[dict(t=t, href=h) for t, h in e.get('links', [])],
            next=e.get('next', ''), contact=e.get('contact', 'not contacted'), est=('current is a class default' if r.i_est else ''),
            updated=e.get('updated', '2026-10-22'), geom='', sites=[dict(name=r.site, lat=r.lat, lon=r.lon)],
            x17=_f(r.x17_day), win=None, claims=[SHORT[c] for c in claims], tritium=r.tritium, access=r.access,
            x17lab=r.x17 if isinstance(r.x17, str) else '', e_lo=r.e_lo, e_hi=r.e_hi, i_dc=r.i_dc,
            days_all=_f(r.days_all_big), scen=[], reach=reach))
        rows[-1]['studied'] = rows[-1]['effort'] >= 3
    import proton_reach as pr
    doc = dict(generated=date.today().isoformat(), effort_levels=EFFORT,
               log=[dict(date=a, text=b, keys=[k for k in c.split(',') if k]) for a, b, c in PLOG],
               claims={k: dict(label=v['label'], short=v['short'], strength=v['strength'], status=v['status'],
                               window=v['window'], days_1ua=v['days'], cap_ua=pr.CAP[k]) for k, v in pr.REACTIONS.items()},
               i_thin=pr.I_THIN, facilities=rows)
    site_json.write_text(json.dumps(doc, ensure_ascii=False, separators=(',', ':'), allow_nan=False), encoding='utf-8')
    print('->', site_json, len(rows), 'rows')
    short = []
    for f in rows:
        if f['verdict'] == 'POTENTIAL' or f['studied']:
            b = f['reach'][0] if f['reach'] else None
            short.append(dict(key=f['key'], name=f['name'], reaction=', '.join(f['claims']), verdict=f['verdict'],
                              effort=f['effort'], updated=f['updated'], status=f['status'],
                              headline=(f"3σ at ATOMKI in {b['days']:.2g} d (big plastics) at {f['i_dc']:g} µA" if b else '')))
    return short
