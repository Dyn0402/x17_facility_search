"""Design review 2026-11-11 (TARGET_REVIEW.md §4.2): a metallic Li film that turns into LiOH or Li2O.

TARGET_OPTIONS §6 says the products stay on the target, so the Li is not lost.  True, but the oxygen and hydrogen
add stopping: the same Li atoms then take more energy from the beam, and a film that was safely above the 441 keV
resonance can reach it.  This script puts numbers on that with the repo's yield model (target_model.layered_yield,
PSTAR stopping, the Zahnow cross sections): the outer fraction x of the Li atoms is converted (the reaction front
moves in from the vacuum side), the rest stays metal.

Run:  ~/PycharmProjects/nTof_x17/.venv/bin/python review_li_conversion.py
Output: ../out/target/options/review_li_conversion.csv
"""
from pathlib import Path

import pandas as pd

import target_model as TM

OUT = Path(__file__).resolve().parent.parent / 'out' / 'target' / 'options'
RHO_LI = 0.534
M = {'Li': 6.941, 'LiOH': 23.948, 'Li2O': 29.881 / 2}      # g per mole of Li atoms


def stack(t_um, x, prod):
    li = t_um * 1e-4 * RHO_LI * 1e6                         # µg/cm² of Li metal before conversion
    lay = []
    if x > 0:
        lay.append((TM.FILMS[prod]['comp'], li * x * M[prod] / M['Li']))
    if x < 1:
        lay.append((TM.FILMS['Li']['comp'], li * (1 - x)))
    return lay


def main():
    rows = []
    for ep in (1100, 1030):
        for t in (10, 12, 15, 20):
            y0 = TM.layered_yield(ep, stack(t, 0, 'LiOH'))['Y_g0']
            for prod in ('LiOH', 'Li2O'):
                for x in (0, 0.25, 0.5, 0.75, 1.0):
                    r = TM.layered_yield(ep, stack(t, x, prod))
                    rows.append(dict(Ep_keV=ep, li_um=t, product=prod, converted=x, E_out_keV=round(r['E_out_keV'], 1),
                                     g0_rel_fresh=round(r['Y_g0'] / y0, 3), share_17p64=round(r['f17'], 4),
                                     g0_per_proton=r['Y_g0']))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / 'review_li_conversion.csv', index=False)
    pd.set_option('display.width', 200)
    for ep in (1100, 1030):
        for prod in ('LiOH', 'Li2O'):
            d = df[(df.Ep_keV == ep) & (df['product'] == prod)]
            print(f'\nE_p {ep} keV, product {prod}: beam energy leaving the film (keV) / 17.64 MeV share of gamma0')
            a = d.pivot(index='li_um', columns='converted', values='E_out_keV')
            b = d.pivot(index='li_um', columns='converted', values='share_17p64')
            print(pd.concat({'E_out': a, 'share17': b}, axis=1).to_string())


if __name__ == '__main__':
    main()
