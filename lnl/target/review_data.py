"""The buildability review of 2026-11-11 (TARGET_REVIEW.md) as data, for every deck and page generator.

One place for: the verdict on each target design, the proposed flat Al end cap and its numbers, the Li → LiOH
table, and the baseline facts (how Li targets are really made).  The days always come from nd_reach_io (reference
fit; L13 / L14 / thin-Li rows win when their files exist), so a rebuild picks up new Geant4 results by itself.

    from review_data import VERDICT, verdict, CAP, cap_days, li_table, BASELINE, DROPPED
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'shapes'))
import nd_reach_io as nd  # noqa: E402

OPT = HERE.parent / 'out' / 'target' / 'options'
REVIEW = 'TARGET_REVIEW.md (11 Nov 2026)'
DATE = '11 Nov 2026'

# --------------------------------------------------------------------------- #
# verdicts.  level: 'propose' (build this), 'ok' (feasible now), 'later' (feasible, not worth it with today's
# detector), 'drop' (do not build).  Keyed by the Geant4 configuration tags (shapes_geant.SHAPES); VERDICT_OF maps
# every tag to its entry.
# --------------------------------------------------------------------------- #
LEVELS = {'propose': 'proposed', 'ok': 'buildable now', 'later': 'possible, a development project',
          'drop': 'dropped'}
VERDICT = {
    'cap': dict(level='propose', short='proposed: flat parts, LNL’s own Li method',
                why='One piece of aluminium with a flat face at 45°, a flat Cu stop and rolled Li pressed on with flat '
                    'moulds. Every step is something LNL or any workshop already does. The Li is uniform along the '
                    'beam by geometry, so there is no flank, no mask and no line-of-sight coating.'),
    'cu_cup': dict(level='ok', short='exists; slow',
                   why='The CN neutron-line target: 20 µm of rolled Li pressed on a 300 µm Cu cup. It works today and '
                       'is the commissioning target, but every lepton crosses the copper.'),
    'cu_ogive': dict(level='ok', short='buildable now; the simplest step up',
                     why='Electroform it in hard copper (a 200 µm annealed shell has only ×2–3 on buckling). Pressing '
                         'a rolled foil into a tip of R 2.8 mm needs new moulds, and Li that overlaps the 65° flank is '
                         '×2.4 thicker along the beam.'),
    'al_cu_plated': dict(level='ok', short='the ogive to try after the Cu one',
                         why='Al 0.4 mm with Cu plated over the whole inside (sputtered seed, then electroplating: the '
                             'route with a precedent), Li pressed on the tip. No sputtering deep in the cone, no '
                             'masks, no lithium evaporator.'),
    'al_cu_liner': dict(level='later', short='three steps LNL has not shown',
                        why='A 0.35 mm wall turned 63 mm deep, ≥ 12 µm of Cu stuck to aluminium at the bottom of the '
                            'cone, and Li evaporated through a mask from far out on the axis (0.8–5 g of lithium per '
                            'coating). With today’s detector it gains ×1.0–1.7 on the Cu ogive; the ×2.4–3.5 needs '
                            'the big plastics.'),
    'al_ti': dict(level='later', short='only if LNL already coats thick Ti',
                  why='Titanium takes up hydrogen without blistering and makes no x-rays that escape, but nobody has '
                      'tested a 15 µm Ti film under MeV protons and evaporated Ti has peeled from smooth substrates.'),
    'mo': dict(level='drop', short='dropped: Mo K x-rays at 1 µA',
               why='The Geant4 x-ray check of 4 Nov doubled the Mo K yield: 19–45 % Micromegas occupancy per arm per '
                   'µA, and no thin wall absorbs 17.5 keV. These designs would have to run at 0.2–0.5 µA.'),
    'diamond': dict(level='drop', short='dropped: the diamond buys nothing at 1.1 W',
                    why='At 1 µA the beam is 1.1 W; a 0.4 mm aluminium face carries it with a 5 K rise. The diamond is '
                        'brittle, has never been hydrogen-tested, costs 6–15 k€ mounted (estimate), and carries the '
                        'Mo stop. The 45° geometry is kept, in aluminium.'),
    'be': dict(level='drop', short='dropped: no supplier, 6–12 months',
               why='The last supplier of machined and welded beryllium vacuum tubes stopped in 2023 (CERN now makes its '
                   'own). A custom thin shell is 20–60 k€ and 6–12 months (estimate), plus a safety case, and all the '
                   'Be designs carry the Mo stop.'),
    'thin_film': dict(level='drop', short='not a fallback: films broke in hours at LNL',
                      why='The AN2000 group ran 24 thin LiF films on self-supporting backings: most gave 6–8 h of '
                          'stable rate, the best two days; their one Li₂O film broke at once. Hanoi’s films were '
                          '"punctured many times".'),
}
VERDICT_OF = {
    'cap45al400cu': 'cap', 'cap45al500cu': 'cap', 'cap45al400cu_ep03': 'cap',
    'dome200': 'cu_cup', 'dome300': 'cu_cup', 'dome200glued': 'cu_cup',
    'ogCu200': 'cu_ogive',
    'ogAl300cu12': 'al_cu_plated', 'ogAl400cu12': 'al_cu_plated',
    'ogAl300cu12r8m4': 'al_cu_liner', 'ogAl400cu12r8m4': 'al_cu_liner', 'ogAl300cu30r8m4': 'al_cu_liner',
    'ogAl300ti15r8m4': 'al_ti',
    'ogAl200mo8': 'mo', 'ogAl300mo8': 'mo',
    'win45d200': 'diamond', 'win45d300': 'diamond', 'win0d200': 'diamond', 'win0d300': 'diamond',
    'win45wide': 'diamond', 'li20_mo8_dia50': 'diamond', 'flat1mm': 'diamond',
    'ogBe200mo8': 'be', 'ogBe300mo8': 'be', 'domeBe200mo8': 'be', 'win45be': 'be',
    'base': 'thin_film',
}
DROPPED = sorted(k for k, v in VERDICT_OF.items() if VERDICT[v]['level'] == 'drop')


def verdict(config: str) -> dict:
    """the verdict entry for a Geant4 configuration tag (yield-variant suffixes are ignored)."""
    c = config
    for sfx in ('_li10', '_li12', '_li15', '_tip', '_los', '_m6'):
        c = c.removesuffix(sfx)
    v = dict(VERDICT[VERDICT_OF[c]])
    v['key'] = VERDICT_OF[c]
    v['label'] = LEVELS[v['level']]
    return v


# --------------------------------------------------------------------------- #
# the proposed design
# --------------------------------------------------------------------------- #
CAP = dict(
    tag='cap45al400cu', alt=('cap45al500cu', 'cap45al400cu_ep03'), proxy='win45d200',
    name='Flat aluminium end cap at 45°',
    sub='one piece, Cu stop, LNL’s pressed Li',
    stack='Li 10–12 µm (along the beam) / Cu ≥ 12 µm (along the beam; 8.5 µm on the face) / Al 6061-T6 0.4–0.5 mm, '
          'a flat face at 45° closing a Ø20 tube end with a 0.5 mm wall, machined in one piece',
    pros=['flat parts only: a milled face, an ordinary Cu coating, rolled Li pressed with flat moulds as LNL does now',
          'the Li is uniform along the beam by geometry: no flank, no mask, no line-of-sight coating',
          'no diamond, no rings, no glue, no Mo: Cu K x-rays stop in the 0.4–0.5 mm of aluminium',
          'the 45° geometry is the best buildable shape simulated; vertices within ±3 mm along the beam'],
    cons=['the Ø20 end piece stays in the leptons’ view, as for the diamond window (a 0.3 mm wall is the lever)',
          'the cap is the vacuum wall and the beam stop: a fast valve upstream, a pressure test of every cap',
          'Cu on aluminium must be done cool (6061-T6 softens above ~200 °C): a Ti or Cr adhesion layer, or plating'],
    press=dict(t400=(80, 3.5), t500=(51, 5.4), t300=(142, 1.9)),      # MPa, margin on 276 MPa yield; clamped ellipse 20 × 28
    heat_K=dict(t400=(4.6, 18.6), t500=(3.7, 14.9)),                  # centre-to-edge rise at 1.1 W / 4.4 W
    cost='< 1 k€ a piece, 1–3 weeks (estimate)',
    trace_sigma_vs_diamond={'Al 300': 0.0, 'Al 400': 0.3, 'Al 500': 0.5},   # degrees, review_alt.py
)


def cap_days(ep: float = 1100.0, tag: str | None = None) -> dict:
    """days to 3σ at R(ATOMKI), 1 µA, for the cap: Geant4 L14 if nd_reach_L14.csv has it, else the 45° diamond
    window's (same geometry class; the ray-trace says Al for diamond changes σ68 by 0.0–0.5°).  Keys: big, asb,
    asb_ntof (floats), g4 (True if L14), note."""
    tag = tag or CAP['tag']
    g4 = nd.has(tag)
    src = tag if g4 else CAP['proxy']
    return dict(big=nd.best(src, 'bigP', ep), asb=nd.best(src, 'asb', ep), asb_ntof=nd.best(src, 'asb', ep, nd.AS_NTOF),
                g4=g4, tag=src,
                note='Geant4 run L14' if g4 else 'estimate: the 45° diamond window’s Geant4 days (same geometry; '
                                                  'ray-trace: aluminium for diamond changes σ68 by 0.0–0.5°); Geant4 run L14 pending')


def days3(config: str, ep: float = 1100.0) -> tuple[float, float, float]:
    """(big plastics, as built with the liquid repaired, as built with the liquid as at n_TOF)."""
    return (nd.best(config, 'bigP', ep), nd.best(config, 'asb', ep), nd.best(config, 'asb', ep, nd.AS_NTOF))


def fmt3(config: str, ep: float = 1100.0) -> str:
    return ' / '.join(nd.fmt(x) for x in days3(config, ep))


# --------------------------------------------------------------------------- #
# Li → LiOH (review_li_conversion.py)
# --------------------------------------------------------------------------- #
def li_table(ep: int = 1100, product: str = 'LiOH') -> pd.DataFrame:
    """index Li thickness (µm), columns converted fraction: share of γ0 from the 17.64 MeV (441 keV) resonance."""
    d = pd.read_csv(OPT / 'review_li_conversion.csv')
    d = d[(d.Ep_keV == ep) & (d['product'] == product)]
    return d.pivot(index='li_um', columns='converted', values='share_17p64')


def li_eout(ep: int = 1100, product: str = 'LiOH') -> pd.DataFrame:
    d = pd.read_csv(OPT / 'review_li_conversion.csv')
    d = d[(d.Ep_keV == ep) & (d['product'] == product)]
    return d.pivot(index='li_um', columns='converted', values='E_out_keV')


def li_yield_rel(ep: int = 1100) -> dict:
    """fresh-film γ0 per proton relative to 20 µm, by thickness."""
    d = pd.read_csv(OPT / 'review_li_conversion.csv')
    d = d[(d.Ep_keV == ep) & (d['product'] == 'LiOH') & (d.converted == 0)].set_index('li_um').g0_per_proton
    return {int(k): float(v / d.loc[20]) for k, v in d.items()}


LI = dict(
    headline='Half of a 20 µm Li film turned to LiOH by residual water takes a 1.10 MeV beam down to 454 keV: 52 % of '
             'the γ₀ then comes from the 441 keV resonance (fresh 0.85 %; 91 % at 1.03 MeV).',
    fix='10–12 µm of Li stays at or below 10 % even fully converted, for 51–61 % of the yield.',
    rate='The rate is unknown: 1.35 µm a day at 10⁻⁷ mbar of water if every molecule sticks (an upper limit; LiOH '
         'passivates). A one-week film test on the LNL line decides the thickness.',
)

# --------------------------------------------------------------------------- #
# the baseline: how lithium targets are really made (TARGET_REVIEW.md §2, sources §10)
# --------------------------------------------------------------------------- #
BASELINE = [
    ('LNL CN, Mastinu’s group', 'metal, rolled to ~20 µm (10–40) in an argon glovebox, pressed on a 300 µm Cu cup with '
     'paired moulds; air-cooled, ~10 W', 'arXiv:2605.12005'),
    ('LNL AN2000, X17 group', '24 evaporated LiF films, 34–935 µg/cm², on thin self-supporting backings: 6–8 h of stable '
     'rate, the best two days', 'Góngora-Servín, thesis 2025'),
    ('BINP Novosibirsk', 'metal, 7–200 µm evaporated on a separate stand; the target leaves under vacuum behind its own '
     'gate valve', 'JINST 15 P10006'),
    ('MEG II (PSI)', 'LiPON 7 µm sputtered on 25 µm Cu, 8–11 µA for 4 weeks, no significant deterioration',
     'arXiv:2411.07994'),
    ('ATOMKI', 'LiF, Li₂O; metal Li on 10 µm Al diffused into the backing', 'arXiv:2205.07744'),
    ('PTB, Karlsruhe, Notre Dame', 'metal, 5–100 µm evaporated on Ta or Cu for neutron production', 'see §10'),
]
BEAM_PIPE = ('No laboratory was found that deposits Li, Cu or Ti inside the beam pipe. Li metal is always made off the '
             'line (glovebox, or an evaporation stand with a vacuum transfer). A 20 µm film does not need more: a few '
             'nm to ~0.5 µm of surface compound from the transfer is ≤ 3 % of it.')

if __name__ == '__main__':
    print('cap:', cap_days())
    for c in ('ogCu200', 'ogAl300cu12r8m4', 'win45d200', 'ogBe300mo8', 'base'):
        print(c, fmt3(c), verdict(c)['label'], '|', verdict(c)['short'])
    print((100 * li_table()).round(1).to_string())
    print(li_yield_rel())
