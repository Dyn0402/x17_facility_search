"""Build the D-D sources X17 feasibility slide note: out/dd-sources-x17-feasibility.html (not published)."""
import sys
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'survey' / 'soft_sim')); sys.path.insert(0, str(ROOT / 'survey'))
import deck_common as C  # noqa: E402
from deck_common import sd, sci  # noqa: E402
O = HERE.parent / 'out'
t = pd.read_csv(O / 'dd_reach.csv')
k = pd.read_csv(O / 'dd_kinematics.csv')
g = pd.read_csv(O / 'dd_geometry.csv')
s = pd.read_csv(O / 'dd_sens.csv')


def R(src, d, hw='big plastics', col='rho3', mode='shadow'):
    q = t[(t.source == src) & (t.d_cm == d) & (t.hw == hw) & (t.days == 50) & (t.model == 'full') & (t.shield == mode)]
    return float(q[col].iloc[0])


days = lambda r: 50 * (r / 1.5e-3) ** 2  # noqa: E731
r35, r50 = R('phoenix_3e11', 35), R('phoenix_3e11', 50)
D = sd.Deck('D-D sources: X17 feasibility', 'Could MX17 run on an intense 2.45 MeV D-D generator, close-coupled, and what would it take?')
D.slide('cover', sd.kicker('MX17 on D-D neutron generators · feasibility · 9 Nov 2026')
        + f'<h1 style="font-size:58px;font-weight:600;line-height:1.08">A measured 3×10¹¹ n/s D-D source, close-coupled, reaches {sci(r35, 1)} in 50 days. Nobody offers that beam.</h1>'
        + sd.row(sd.bignum(sci(r35, 1), 'X17/IPC, 3σ, 50 d, 35 cm', sd.DGREEN, f'{days(r35):.1f} days to ATOMKI; as built {sci(R("phoenix_3e11", 35, "as built"), 1)}'),
                 sd.bignum(sci(r50, 1), 'at the robust 50 cm', sd.DGREEN, f'{days(r50):.0f} days to ATOMKI'),
                 sd.bignum('CLOSED', 'for now', sd.DRED, 'no user programme; no budget to buy a machine'), gap=56),
        dark=True, short='cover',
        notes='Geometry fixes the catalogue reason (×10 from 2.5 m to 35 cm). The arm, room and correlated terms are estimates pending a 2.45 MeV Geant4 run. Files: dd_sources/FEASIBILITY.md, FACILITY.md.')

rows = [[n, f'{y}', st, a] for n, y, st, a in [
    ('Phoenix gas target', '3×10¹¹ measured', '2013–2018; today (ask)', 'buy/contract'),
    ('Adelphi DD-110', '~1×10¹⁰ rated', 'commercial', 'buy'),
    ('Astral Mk2', '~1×10¹⁰ (vendor)', 'for sale 2025', 'buy'),
    ('Avalanche Lando', 'licensed 10¹⁰', 'development', 'future'),
    ('LBNL HFNG', '3×10⁸ measured', 'research', 'collaboration'),
    ('ENEA FNG D-D', '5.7×10⁸ measured', 'operating (2023)', 'programme')]]
D.slide('machines', sd.title('Only one D-D machine reaches 10¹¹ n/s', 'the rest are ×30–×1000 weaker')
        + sd.table(['source', 'yield n/s', 'status', 'access'], rows, size=30, align=['left', 'left', 'left', 'left']), short='machines',
        notes='Full list and URLs: FACILITY.md §1. No operating 5-10 mA deuteron machine with a D₂ gas neutron target was found.')

P = sd.Plot(1500, 620, (15, 250, 'log'), (3e-4, 3e-1, 'log'), 'source to cell front d [cm]', 'X17/IPC reach, 3σ, 50 d, big plastics')
P.xticks([(15, '15'), (25, '25'), (35, '35'), (50, '50'), (100, '100'), (250, '250')])
P.yticks([(1e-3, '10⁻³'), (1e-2, '10⁻²'), (1e-1, '10⁻¹')])
P.hline(1.5e-3, label='ATOMKI ⁴He'); P.hline(5.5e-4, dash='3 5', label='Birmingham Geant4')
for sk, c in (('phoenix_3e11', sd.BLUE), ('need_1e12', sd.RED), ('dacc_1p5_5mA_135', sd.ORANGE), ('adelphi_1e10', sd.MUT)):
    q = t[(t.source == sk) & (t.days == 50) & (t.model == 'full') & (t.shield == 'shadow') & (t.hw == 'big plastics')].sort_values('d_cm')
    P.line(list(q.d_cm), list(q.rho3), c)
D.slide('reach', sd.title('Optimum 35–50 cm: closer and the shield cannot fit; farther and the flux falls')
        + P.svg('reach vs distance') + sd.legend([('Phoenix 3×10¹¹, 90°', sd.BLUE), ('1×10¹²', sd.RED), ('d 1.5 MeV 5 mA 135° (hypothetical)', sd.ORANGE), ('1×10¹⁰ compact', sd.MUT)]),
        short='reach', notes='Limiting wall at ≥35 cm: statistics (IPC and cosmics at about equal share). Inside ~30 cm: direct flux through the shield loads DREAM. Above ~1×10¹² the reach stops improving. Table: FEASIBILITY.md §0.')

krows = [[f'{a:.0f}°', f'{k[(k.E_d_keV == 300) & (k.theta == a)].mean_En.iloc[0]:.2f} MeV',
          f'{100 * k[(k.E_d_keV == 300) & (k.theta == a)].f_in_window.iloc[0]:.0f} %'] for a in (0, 45, 90, 135)]
D.slide('kin', sd.title('The cell must be at 90–135° to the deuteron beam', 'thick D₂ gas, 300 keV')
        + sd.row(sd.table(['angle', 'mean E_n', 'E_n ≤ 2.75 MeV'], krows, size=34),
                 sd.col(sd.callout('0° puts E_n at 3.1 MeV: out of the window, the reach collapses (×50).'),
                        sd.callout('At 135° the neutrons are softer (2.2 MeV), best for the physics.')), gap=60),
        short='kinematics', notes='Higher-energy deuteron machines gain yield but only 135° keeps the neutrons in the window. See FEASIBILITY.md §2.')

g2 = g[g.d_cm.isin((15, 25, 35, 50, 100))]
grows = [[f'{r.d_cm:.0f} cm', f'{r.G_over_naive_frontface:.2f}', f'{r.G_over_naive_center:.2f}', f'{r.arm_T_shadow:.1e}', f'{r.arm_T_tvl_20:.1e}'] for r in g2.itertuples()]
D.slide('geom', sd.title('Close coupling: the Ø8 cm parallel-beam assumption is off by ×2', 'G = (1/L)∫dV/4πr² replaces the engine’s spot; shield only upstream of the cell (tracks need the rest)')
        + sd.table(['d', 'G/naive (front face)', 'G/naive (centre)', 'shield T, TVL 12 cm', 'TVL 20 cm'], grows, size=32),
        short='geometry', notes='ESTIMATE. Without the upstream-only keep-out the first version overestimated the shield by ×10. See FEASIBILITY.md §3.')

sr = s[s.case == 'phoenix 90deg']
srows = [[v, *[sci(float(sr[(sr.variant == v) & (sr.d_cm == d)].rho3.iloc[0]), 1) for d in (35, 50, 100)]]
         for v in ['nominal', 'TVL 20 cm', 'room ×3', 'room ×10', 'correlated at the N5 90% bound']]
D.slide('sens', sd.title('The correlated term is the unknown: N5 has no event at 2.45 MeV', '')
        + sd.table(['variant (Phoenix 90°)', '35 cm', '50 cm', '100 cm'], srows, size=32)
        + sd.callout('The last row is a limit on the MC, not a prediction. A mono-energetic 2.45 MeV Geant4 run settles it.', sd.RED),
        short='sensitivity', notes='N5 has zero two-arm rows from 1.5 to 10 MeV. The bound charges all pre-cut pairs. FEASIBILITY.md §4.')

score = [['Beam today?', '3×10¹¹ demonstrated 2018, availability (ask)'],
         ['Access', 'no user programme; buy or contract'],
         ['Cost', 'compact 10⁵ $ scale (ask); 3×10¹¹ several M€ with vault (ESTIMATE)'],
         ['Shielding', 'new vault ~2 m concrete; 3.4 Sv/h at 1 m (ESTIMATE)'],
         ['vs Birmingham', '5.5×10⁻⁴ full Geant4, machine exists']]
D.slide('end', sd.title('CLOSED FOR NOW', 'Reopens only if an existing 3×10¹¹ system can be used; a 2.45 MeV Geant4 confirmation would still be needed')
        + sd.table(['item', 'assessment'], score, size=32, align=['left', 'left']),
        short='call', notes='Full scorecard FEASIBILITY.md §7.')
print(D.write(O / 'dd-sources-x17-feasibility.html', note_meta=dict(title='D-D sources X17 feasibility', summary='Could MX17 run on an intense 2.45 MeV D-D generator? Source survey, close-coupled reach, and the open questions.', tags='x17, dd, feasibility', date='2026-11-09'),
              footer='Built by x17_facility_search/dd_sources/deck/build_deck.py.'))
