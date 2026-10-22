"""opt_tables.py — the markdown tables of TARGET_OPTIONS.md §7 from opt_geant.py's outputs.
    python lnl/target/opt_tables.py    (prints them)"""
from pathlib import Path

import pandas as pd

O = Path(__file__).resolve().parents[1] / 'out' / 'target' / 'options'
a = pd.read_csv(O / 'geant_acceptance.csv')
a = a[a['sample'] == 'x17'].set_index('config')
r = pd.read_csv(O / 'geant_reach.csv').set_index('config')
r['eq'] = r.days_ref_1uA / r.uA_for_baseline_rate
R1 = ['base', 'al10_y120', 'dia50', 'li20_dia50', 'li20_ta_dia300', 'li20_dia1', 'li20_dia1_y120', 'li20_mch_y120', 'cublock_y120']
R2 = ['li20_dia50', 'li20_dia1', 'li20_dia1_y120', 'li20_dia1_y180', 'li20_dia1_r8', 'li20_dia1_r8_y120', 'li20_mo8_dia50', 'li20_ta8_dia50']


def table(keys):
    out = ['| configuration | X17 acc. | σ68 | pairs with a leg through the backing (σ68 of those) | EPC share of B | '
           '**days per µA** | days, same X17 rate |', '|---|---|---|---|---|---|---|']
    for k in keys:
        if k not in r.index:
            out.append(f'| {k} | (running) | | | | | |')
            continue
        x = a.loc[k]
        out.append(f'| {r.loc[k, "label"]} | {x.acc:.3f} | {x.sigma68_deg:.1f}° | {1 - x.frac_true_up:.0%} '
                   f'({x.sigma68_true_down:.1f}°) | {r.loc[k, "B_epc_share"]:.1%} | **{r.loc[k, "days_ref_1uA"]:.2f}** | '
                   f'{r.loc[k, "eq"]:.2f} |')
    return '\n'.join(out)


if __name__ == '__main__':
    print(table(R1))
    print()
    print(table(R2))
