"""One reader for the LNL target-design reach (days to 3σ at R(ATOMKI), 1 µA, m_X = 16.8, level 'MM 15° + TOF').

Source: lnl/out/target/shapes/nd_reach.csv (shapes_nd.py reach: the reference fit, θ × |y| × E_sum, background shape
floating, MC-safe; FEASIBILITY_SIM.md §19). Rows of the files in EXTRA (same directory) win where they exist for the same
(config, det, Ep_keV, resp): nd_reach_L13.csv (run L13, larger as-built Monte Carlo), nd_reach_L14.csv (run L14, the
flat Al end cap), nd_reach_thinli.csv (10 / 12 / 15 µm Li yield variants).

Every deck and page generator takes its days from here, not from geant_reach.csv (statistics only, norms free; its
as-built rows are a Monte Carlo artefact).

    from nd_reach_io import nd_days
    nd_days('ogCu200', 'bigP', 1100)                    # (best, lo, hi), 'LNL calibrated'
    nd_days('ogCu200', 'asb', 1100, AS_NTOF)            # liquid as it ran at n_TOF
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import math

import pandas as pd

SH = Path(__file__).resolve().parents[2] / 'out' / 'target' / 'shapes'
CAL = 'LNL calibrated'     # big plastics; as built: liquid scintillator repaired
AS_NTOF = 'n_TOF as is'    # as built: liquid as it ran at n_TOF
LABEL = 'reference fit, background shape floating'
ASB_NOTE = ('As built assumes a 0.3 ns arm-to-arm time of flight that no measurement backs; with track pointing alone '
            'the liquid-as-at-n_TOF value is about 20 d for the Cu ogive (FEASIBILITY_SIM.md §19.4).')
KEY = ['config', 'det', 'Ep_keV', 'resp']
#: files that override or extend nd_reach.csv, first wins: L13 (larger as-built Monte Carlo for the Cu ogive and the
#: Al ogive + Cu liner), L14 (the flat Al end cap, TARGET_REVIEW.md §6.1), the thinner-Li yield variants (§4.2)
EXTRA = ['nd_reach_L13.csv', 'nd_reach_L14.csv', 'nd_reach_thinli.csv']


@lru_cache(maxsize=1)
def table() -> pd.DataFrame:
    """nd_reach.csv with nd_reach_L13.csv rows taking precedence; column 'src' says which file."""
    d = pd.read_csv(SH / 'nd_reach.csv').dropna(subset=['Ep_keV', 'days_best'])
    d['src'] = 'nd_reach.csv'
    for name in reversed(EXTRA):          # earlier entries of EXTRA win
        f = SH / name
        if f.exists():
            e = pd.read_csv(f).dropna(subset=['Ep_keV', 'days_best'])
            e['src'] = name
            d = pd.concat([e, d], ignore_index=True).drop_duplicates(subset=KEY, keep='first')
    d['Ep_keV'] = d['Ep_keV'].round().astype(int)
    return d.set_index(KEY).sort_index()


def nd_days(config: str, det: str, Ep: float, resp: str = CAL) -> tuple[float, float, float]:
    """(days_best, days_lo, days_hi) per µA; NaNs if the configuration has no row."""
    try:
        r = table().loc[(config, det, int(round(Ep)), resp)]
    except KeyError:
        return (math.nan, math.nan, math.nan)
    return (float(r['days_best']), float(r['days_lo']), float(r['days_hi']))


def best(config: str, det: str, Ep: float, resp: str = CAL) -> float:
    return nd_days(config, det, Ep, resp)[0]


def has(config: str) -> bool:
    return config in table().index.get_level_values('config')


def src(config: str, det: str, Ep: float, resp: str = CAL) -> str:
    """which file the row came from ('' if none)."""
    try:
        return str(table().loc[(config, det, int(round(Ep)), resp)]['src'])
    except KeyError:
        return ''


def fmt(x: float) -> str:
    """days as the decks print them: 2 decimals below 1, 1 decimal below 10, integer above."""
    if x != x:
        return '–'
    return f'{x:.2f}' if x < 1 else (f'{x:.1f}' if x < 10 else f'{x:.0f}')


def asb_pair(config: str, Ep: float, sep: str = ' / ') -> str:
    """'liquid repaired / liquid as at n_TOF' days as built, formatted."""
    return fmt(best(config, 'asb', Ep, CAL)) + sep + fmt(best(config, 'asb', Ep, AS_NTOF))


if __name__ == '__main__':
    t = table().reset_index()
    print(t.pivot_table(index='config', columns=['det', 'resp', 'Ep_keV'], values='days_best').round(2).to_string())
