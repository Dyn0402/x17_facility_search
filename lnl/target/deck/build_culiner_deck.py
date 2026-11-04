"""Slide note: Pierfrancesco's ogive in Al with a Cu liner where the beam stops (CU_LINER.md, 2026-11-04).

Reads lnl/out/target/options/culiner_*.csv (opt_cu_liner.py), pixe_testem5.csv and the Geant4 L11/L12 summaries
(lnl/out/target/shapes/geant_reach.csv, geant_acceptance.csv); writes lnl/out/target/lnl-cu-liner.html:

    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/deck/build_culiner_deck.py
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py lnl/out/target/lnl-cu-liner.html \\
        --slug lnl-cu-liner --force --deploy
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.expanduser(os.environ.get('SLIDEDOC_DIR', '~/PycharmProjects/dylan-cern-site/scripts')))
import slidedoc as sd  # noqa: E402

HERE = Path(__file__).resolve().parent
LNL = HERE.parents[1]
SH = LNL / 'out' / 'target' / 'shapes'
OP = LNL / 'out' / 'target' / 'options'
OUTF = LNL / 'out' / 'target' / 'lnl-cu-liner.html'
sys.path.insert(0, str(LNL / 'target'))
import opt_cu_liner as CL  # noqa: E402

GR = pd.read_csv(SH / 'geant_reach.csv')
GA = pd.read_csv(SH / 'geant_acceptance.csv')
PROF = pd.read_csv(OP / 'culiner_profile.csv')
LIMIX = pd.read_csv(OP / 'culiner_li_mix.csv')
CU, AL, LI, BEAM, MO, TI = sd.GOLD, '#8a96a8', sd.BLUE, sd.RED, sd.GREY, '#3f8f9b'


def g4(cfg, ep=1100.0, col='days_fit'):
    q = GR[(GR.config == cfg) & (GR.det == 'bigP') & (GR.Ep_keV == ep)]
    return float(q[col].iloc[0]) if len(q) else np.nan


def sig(cfg):
    q = GA[(GA.config == cfg + '_bigP') & (GA['sample'] == 'x17')]
    return float(q.sigma68_deg.iloc[0]) if len(q) else np.nan


DES = [  # label, reach config, σ config, colour, MM occupancy per arm per µA (Geant4 L12 libraries / calibrated model)
    ('his Cu ogive 200 µm', 'ogCu200_los', 'ogCu200', sd.RED, 0.001),
    ('Al 300 + Mo 8', 'ogAl300mo8_los', 'ogAl300mo8', MO, 0.19),
    ('Al 300 + Cu 12, Li r ≤ 4', 'ogAl300cu12r8m4', 'ogAl300cu12r8m4', CU, 0.12),
    ('Al 400 + Cu 12, Li r ≤ 4', 'ogAl400cu12r8m4', 'ogAl400cu12r8m4', sd.GREEN, 0.025),
    ('Al 300 + Cu 30, Li r ≤ 4', 'ogAl300cu30r8m4', 'ogAl300cu30r8m4', sd.ORANGE, 0.05),
    ('Al 300 + Ti 15, Li r ≤ 4', 'ogAl300ti15r8m4', 'ogAl300ti15r8m4', TI, 0.0),
    ('Be 300 + Mo 8', 'ogBe300mo8_los', 'ogBe300mo8', sd.PURPLE, 0.35),
]
for i, d in enumerate(DES):
    DES[i] = dict(name=d[0], days=g4(d[1]), days103=g4(d[1], 1030.0), sigma=sig(d[2]), color=d[3], occ=d[4],
                  epc=g4(d[1], col='B_epc_share'))
BY = {d['name']: d for d in DES}
CUOG, ALCU, AL4 = BY['his Cu ogive 200 µm'], BY['Al 300 + Cu 12, Li r ≤ 4'], BY['Al 400 + Cu 12, Li r ≤ 4']


def best_days(d, cap=0.10, imax=4.0, live=0.97):
    I = imax if d['occ'] <= 0 else min(imax, cap / d['occ'])
    return d['days'] / (I * live), I


# ---- drawing of the tip region, to scale (thin layers thickened) ------------------------------------------------
def drawing(W=860, H=560, s=24.0, r_cu=8.0, r_li=4.0, t_al=0.4):
    cx, cy = W / 2, 40.0
    X = lambda r: cx + r * s                     # noqa: E731
    Y = lambda y: cy - y * s                     # noqa: E731  (y up = beam direction)
    rr = np.linspace(0, 13.0, 400)
    y, nr, ny, _ = CL.surface(rr)
    out = []
    # Al wall (offset outward along the normal by t_al, drawn ×3 for visibility)
    ta = t_al * 3
    for sg in (1, -1):
        xi, yi = X(sg * rr), Y(y)
        xo, yo = X(sg * (rr - nr * ta)), Y(y - ny * ta)
        pts = ' '.join(f'{a:.1f},{b:.1f}' for a, b in zip(np.r_[xi, xo[::-1]], np.r_[yi, yo[::-1]]))
        out.append(f'<polygon points="{pts}" fill="{AL}" stroke="none"{sd.tipattr(f"Al 6061-T6 wall, {t_al*1000:.0f} µm (drawn ×3)")}/>')
        m = rr <= r_cu
        tc = 0.012 * 25
        xc, yc = X(sg * (rr[m] + nr[m] * tc)), Y(y[m] + ny[m] * tc)
        pts = ' '.join(f'{a:.1f},{b:.1f}' for a, b in zip(np.r_[X(sg * rr[m]), xc[::-1]], np.r_[Y(y[m]), yc[::-1]]))
        out.append(f'<polygon points="{pts}" fill="{CU}"{sd.tipattr(f"Cu ≥ 12 µm along the beam, r ≤ {r_cu:.0f} mm (drawn ×25)")}/>')
        m = rr <= r_li
        tl = 0.012 * 25 + 0.02 * 12
        xl, yl = X(sg * (rr[m] + nr[m] * tl)), Y(y[m] + ny[m] * tl)
        xc2, yc2 = X(sg * (rr[m] + nr[m] * tc)), Y(y[m] + ny[m] * tc)
        pts = ' '.join(f'{a:.1f},{b:.1f}' for a, b in zip(np.r_[xc2, xl[::-1]], np.r_[yc2, yl[::-1]]))
        out.append(f'<polygon points="{pts}" fill="{LI}"{sd.tipattr(f"Li 20 µm along the beam, through a mask r ≤ {r_li:.0f} mm (drawn ×12)")}/>')
    # beam spot ±2σ
    for xx in (-4, -2, 0, 2, 4):
        yb = float(CL.surface(np.array([abs(xx)]))[0][0])
        out.append(sd.arrow(X(xx), H - 30, X(xx), Y(yb) + 8, BEAM, 2.5 if xx == 0 else 1.5, 10))
    out.append(sd.T(X(0), H - 8, 'beam, σ 2 mm (arrows at 0, ±1σ, ±2σ)', 20, BEAM))
    out.append(sd.T(X(9.5), Y(-11.5), f'Cu to r {r_cu:.0f} mm', 22, CU, 'start', 600))
    out.append(sd.T(X(5.0), Y(-3.0), f'Li to r {r_li:.0f} mm', 22, LI, 'start', 600))
    out.append(sd.T(X(-17.5), Y(-12), 'Al 0.35–0.4 mm', 22, sd.MUT, 'start', 600))
    # scale bar
    out.append(sd.line(X(-17), Y(-19), X(-12), Y(-19), sd.INK, 3))
    out.append(sd.T(X(-14.5), Y(-19) - 10, '5 mm', 18, sd.INK))
    return sd.svg(W, H, ''.join(out), 'the tip region of the ogive with the Cu liner and the Li mask')


D = sd.Deck('LNL: his ogive in Al, Cu only where the beam stops',
            'Pierfrancesco’s ogive made of Al with a 12 µm Cu liner over the tip and a masked Li film: Geant4 L12, PIXE, '
            'x-rays, how to make it.')

# ---- 1. the proposal ------------------------------------------------------------------------------------------------
bd_cu, I_cu = best_days(CUOG)
bd_al4, I_al4 = best_days(AL4)


def kpi(v, label, color, tip=None):
    return (f'<div{sd.tipattr(tip)} style="flex:1;border-top:4px solid {color};padding-top:10px">'
            f'<p style="font-size:46px;font-weight:600;color:{color};line-height:1.05">{v}</p>'
            f'<p style="font-size:21px;color:{sd.MUT};line-height:1.25">{label}</p></div>')


k = sd.row(kpi(f'{ALCU["sigma"]:.1f}°', f'σ68 opening angle (his Cu ogive {CUOG["sigma"]:.1f}°)', CU,
               'Geant4 L12, X17 m 16.8, big plastics'),
           kpi(f'{ALCU["days"]:.2f} d', f'per µA to 3σ at ATOMKI, 1.10 MeV (his {CUOG["days"]:.2f})', CU,
               'statistics only, norms free; line-of-sight Li for both'),
           kpi(f'×{CUOG["days"] / ALCU["days"]:.1f}', 'faster than his Cu ogive at the same current', sd.GREEN), gap=24)
k2 = sd.row(kpi(f'{100 * ALCU["epc"]:.0f} %', f'of the background from γ converting in the shell (his {100 * CUOG["epc"]:.0f} %)', sd.INK),
            kpi('590', 'single-arm legs/s per µA into DREAM (his 1630)', sd.INK),
            kpi(f'{100 * AL4["occ"]:.1f} %', 'MM x-ray occupancy per arm per µA with a 0.4 mm wall (0.3 mm: 12 %)', sd.ORANGE), gap=24)
D.slide('proposal',
        sd.title('His ogive in Al, with Cu only where the beam stops',
                 'Same shape. Al 6061-T6 0.35–0.4 mm; ≥ 12 µm Cu (along the beam) over r ≤ 8–10 mm; 20 µm Li through a mask r ≤ 4 mm; both laid down from the beam axis') +
        sd.row(drawing(), sd.col(k, k2, sd.callout(
            f'The leptons see the Al shell, not the Cu: the resolution of the Al + Mo ogive without a Mo coat inside a 63 mm deep cone. '
            f'The price is Cu K x-rays (8 keV), which a 0.4 mm Al wall stops: then up to 4 µA ({bd_al4:.2f} d to 3σ).', sd.BLUE, 24),
            gap=26, w=880), gap=40),
        notes='Geant4 run L12 (MX17_Full_Geant lnl_culiner): the CAD ogive in Al with a 12 µm Cu liner only where the shell radius is ≤ 8 mm, '
              'vertices only where the beam lands at r ≤ 4 mm (the Li mask). Big plastics, MM 15° + TOF, the 3D fit with free norms '
              '(statistics only). Days for his Cu ogive with a line-of-sight Li film (1.13 d); with L11’s uniform film it is 0.95 d. '
              'The drawing is to scale except the layers (Al ×3, Cu ×25, Li ×12). CU_LINER.md §0.', short='proposal')

# ---- 2. where and how much Cu ---------------------------------------------------------------------------------------
P = sd.Plot(900, 560, x=(0, 12), y=(0, 36), xlabel='radius on the shell where the beam lands (mm)',
            ylabel='Cu thickness (µm)')
P.xticks([(v, str(v)) for v in (0, 2, 4, 6, 8, 10, 12)]).yticks([(v, str(v)) for v in (0, 6, 12, 18, 24, 30, 36)])
pr = PROF[PROF.rho_mm <= 12]
P.line(pr.rho_mm, pr.Cu_beam_uniform, sd.GREY, tips=[f'r {a:.1f}: {b:.1f} µm along the beam (uniform 12 µm coat)' for a, b in zip(pr.rho_mm, pr.Cu_beam_uniform)])
P.line(pr.rho_mm, pr.Cu_beam_los150, CU, tips=[f'r {a:.1f}: {b:.1f} µm along the beam (line of sight, 150 mm)' for a, b in zip(pr.rho_mm, pr.Cu_beam_los150)])
P.line(pr.rho_mm, pr.Cu_normal_los150, CU, dash='6 5', tips=[f'r {a:.1f}: {b:.1f} µm along the normal' for a, b in zip(pr.rho_mm, pr.Cu_normal_los150)])
P.hline(10.7, sd.RED, dash='4 4', label='needed along the beam: 10.7 µm')
lt = pd.read_csv(OP / 'culiner_landing.csv')
s2 = lt[lt.sigma_mm == 2.0].iloc[0]
tab = sd.table(['', 'Cu needed along the beam'],
               [['after 20 µm Li (872 keV)', '6.0 µm'], ['no Li, 1.15 MeV', '8.7 µm'], ['design (×1.12 + 1 µm)', '<b>10.7 → 12 µm</b>'],
                ['beam σ 2 mm: 99.9 % inside', f'r {s2.r999:.1f} mm'], ['on bare Al beyond r 8 mm', f'{s2.share_beyond_8mm:.1e}']],
               size=23)
D.slide('cu', sd.title('Where the Cu goes: r ≤ 8–10 mm, ≥ 12 µm along the beam',
                       'A coat laid from the beam axis lands ∝ cos(incidence): thin on the steep flank, constant along the beam') +
        sd.row(sd.col(P.svg('Cu thickness against radius'),
                      sd.legend([('uniform 12 µm (plating): along the beam', sd.GREY, 'line'), ('line of sight: along the beam', CU, 'line'),
                                 ('line of sight: along the normal', CU, 'dash')], size=19), gap=4),
               sd.col(tab, sd.p('Outside the Cu the beam hits Al: ²⁷Al(p,γ) 10.76 MeV. Even with a 1 % halo that is 0.4 % of the ⁸Be γ₀: '
                                'the Al does not set the extent, the Li mask and its alignment do (Cu ≥ 3 mm beyond the Li).', 23, sd.MUT),
                      gap=24, w=760), gap=48),
        notes='PSTAR ranges; ×1.12 covers straggling (~4 %) and a 10 % thickness error, +1 µm roughness. A Li-free beam at 1.15 MeV '
              'must still stop in the Cu (film gone, protons outside the mask). Profiles for a small source on the axis 150 mm '
              'upstream of the tip (400 mm: ±10 % to r 8). CU_LINER.md §1–2, §4.', short='where the Cu goes')

# ---- 3. the Li ----------------------------------------------------------------------------------------------------
lm = LIMIX[LIMIX.Ep_keV == 1100.0].set_index('film')
lm3 = LIMIX[LIMIX.Ep_keV == 1030.0].set_index('film')
rows = []
for f, lab in (('uniform film, no mask (L11)', 'uniform along the normal (L11)'), ('line of sight (150 mm), no mask', 'line of sight, no mask'),
               ('line of sight (150 mm), mask r<=4', '<b>line of sight, mask r ≤ 4</b>')):
    rows.append([lab, f'{lm.loc[f].Yg0_rel_flat:.2f}', sd.pct(lm.loc[f].f17, 1), sd.pct(lm3.loc[f].f17, 1)])
D.slide('li', sd.title('Laid from the axis, the Li behaves like a flat film',
                       'L11’s flank problem (17.64 MeV) came from assuming a uniform film, not from the shape') +
        sd.row(sd.table(['Li film', 'γ₀ per proton / flat', '17.64 share, 1.10 MeV', '1.03 MeV'], rows, size=24),
               sd.col(sd.p('On the flank the beam meets the wall at ~65°. A film of fixed normal thickness is ×2.4 longer along the beam, '
                           'the protons leave it below 441 keV and 29–71 % of the γ₀ moves to 17.64 MeV.', 24),
                      sd.p('Evaporated from the axis, the Li lands ∝ cos(incidence), as the Cu: ~20 µm along the beam everywhere.', 24),
                      sd.p('Mask it to r ≤ 4 mm: beyond that the Li sits 5–14 mm upstream of the tip and the opening angle, taken from '
                           'the nominal vertex, degrades (Geant4: ~25 % in days).', 24, sd.MUT), gap=20, w=700), gap=48),
        notes='opt_cu_liner.li_mix_table / los_yield_mix: share-weighted ⁸Be yields (target_model.layered_yield) over the σ 2 mm spot. '
              'CU_LINER.md §3 and §7.', short='the Li')

# ---- 4. Geant4 reach --------------------------------------------------------------------------------------------------
vmax = 1.3
hb = sd.hbars([(d['name'], d['days'], d['color'], f'{d["days"]:.2f} d/µA at 1.10 MeV, {d["days103"]:.2f} at 1.03; σ68 {d["sigma"]:.1f}°') for d in DES],
              vmax, width=480, label_w=360, fmt=lambda v: f'{v:.2f}', size=24)
tb = sd.table(['design', 'σ68', '1.03 MeV', 'EPC'],
              [[d['name'], f'{d["sigma"]:.1f}°', f'{d["days103"]:.2f}', sd.pct(d['epc'])] for d in DES], size=21,
              widths=[330, 90, 110, 80])
D.slide('reach', sd.title('Geant4 L12: the Cu liner costs nothing against Mo; the Al wall sets the resolution',
                          'days per µA to 3σ at the ATOMKI ratio, big plastics, 1.10 MeV (line-of-sight Li everywhere)') +
        sd.row(hb, sd.col(tb, w=620), gap=40),
        notes='geant_reach.csv. Statistics only, norms free; the fit that floats the background shape has not been run on L11/L12 '
              '(FEASIBILITY_SIM §15: it penalises poor resolution far more). +0.1 mm Al: +1° and +36 % days; Cu 30 instead of 12: '
              '+1.6° and +58 %. As built (small plastics) every ogive is 2–3 d: the acceptance limits, not the target.',
        short='Geant4 reach')

# ---- 5. x-rays -------------------------------------------------------------------------------------------------------
xr = [(d['name'], 100 * d['occ'], d['color'], f'{100 * d["occ"]:.1f} % per arm per µA') for d in DES]
pt = pd.read_csv(OP / 'pixe_testem5.csv')


def py(el, model='Empirical', e=870.0):
    q = pt[(pt.el == el) & (pt.model == model) & (pt.E_keV == e)]
    return float(q.K_per_p.iloc[0]) if len(q) else np.nan


rows = [['Cu K, 8.0/8.9 keV', sd.sci(py('Cu')), '2.1 × 10⁻⁴'], ['Mo K, 17.5/19.6 keV', sd.sci(py('Mo')), '2.2 × 10⁻⁶'],
        ['Ti K, 4.5 keV', sd.sci(py('Ti')), '—']]
best = [(d['name'], *best_days(d)) for d in DES]
D.slide('xrays', sd.title('The price: Cu K x-rays, paid by the Al wall',
                          'Cu makes 45× more K x-rays than Mo, but at 8 keV, where Al stops them; 0.1 mm more Al divides them by ~4') +
        sd.row(sd.col(sd.p('MM occupancy per arm per µA (1.2 µs)', 24, sd.INK, 600),
                      sd.hbars(xr, 40, width=420, label_w=360, fmt=lambda v: f'{v:.1f} %', size=24), gap=8),
               sd.col(sd.p('PIXE per proton at 872 keV, Geant4 TestEm5', 24, sd.INK, 600),
                      sd.table(['', 'Geant4', 'estimate (L10/L11)'], rows, size=22),
                      sd.p('Mo is ×2 the estimate: the Mo designs’ published occupancies are ×2 low.', 22, sd.RED),
                      sd.p('Days to 3σ at the best current (≤ 4 µA, ≤ 10 % occupancy): ' +
                           '; '.join(f'{n}: {b:.2f} d ({I:.1f} µA)' for n, b, I in best[:4]), 20, sd.MUT), gap=14, w=640), gap=40),
        notes='Geant4 L12 x-ray libraries (photons from the film, MM hits per arm) × the TestEm5 PIXE yields, protons outside the Li '
              'mask entering the Cu at 1.10 MeV; the calibrated analytic model (opt_cu_liner.escape) agrees to ~20 %. 10 % per arm is '
              'a working limit until the MM point-cluster cut is measured with a source. CU_LINER.md §6–7.', short='x-rays')

# ---- 6. how to make it --------------------------------------------------------------------------------------------
D.slide('make', sd.title('How to make it', 'all of it with tools LNL already has') +
        sd.flow([dict(label='Al 6061-T6 ogive', sub='0.35–0.4 mm, collar at the base; LNL workshop, ~1 k€', color=AL),
                 dict(label='Cu from the axis', sub='Ar-ion etch, then 12–16 µm at the tip; a sleeve stops it at r ≈ 10 mm', color=CU),
                 dict(label='Li from the axis', sub='20 µm through a mask r ≤ 4 mm; same vacuum, or under Ar', color=LI),
                 dict(label='coupons + leak test', sub='thicknesses, tape test, 20–150 °C cycles; He leak test'),
                 dict(label='PIGE on the beam', sub='1.10 MeV: no Al lines (843, 1014 keV, 10.76 MeV); 478 keV present', color=sd.GREEN)], size=24, wrap=True) +
        sd.row(sd.card(sd.p('<b>Plating instead</b> (any shop): double zincate, Cu strike, acid Cu 15–20 µm with an anode wire on the axis; '
                            'uniform along the normal (×2.4 more Cu on the flank than needed), bake 150 °C. The Li still goes on from the axis.', 22), w=860),
               sd.card(sd.p('<b>Margins</b>: 1 bar ×4.8 (0.3 mm) / ×10 (0.4 mm); tip +54–69 K at 4 µA; Cu stress ≤ 150 MPa (sputtered, room T); '
                            'H in the Cu ~5 µA·day before blistering at σ 2 mm (a 3σ run needs ≲ 1).', 22), w=860), gap=40),
        notes='CU_LINER.md §5 and §8. Not a loose Cu cup: no thermal contact and a trapped volume. A Cu-clad Al sheet spun into the shape '
              'would also work if one exists thin enough (ask).', short='how to make it')

# ---- 7. questions / decision ---------------------------------------------------------------------------------------
D.slide('end', sd.kicker('For Pierfrancesco') +
        sd.row(sd.col(sd.p('Proposal', 34, sd.DINK, 600),
                      sd.p('Keep your ogive; make it in <b>Al 6061-T6, 0.35–0.4 mm</b>.', 28, sd.DINK),
                      sd.p('Put <b>≥ 12 µm Cu</b> (along the beam) on the inside over r ≤ 8–10 mm, from the axis.', 28, sd.DINK),
                      sd.p('Evaporate <b>20 µm Li</b> from the axis through a mask <b>r ≤ 4 mm</b>.', 28, sd.DINK),
                      sd.p(f'×{CUOG["days"] / ALCU["days"]:.1f} faster than the Cu ogive at equal current, σ68 {ALCU["sigma"]:.1f}° not {CUOG["sigma"]:.1f}°.', 28, sd.DINK), gap=20),
               sd.col(sd.p('Questions', 34, sd.DINK, 600),
                      sd.p('Beam spot σ and halo at the target? (sets the Cu and mask radii)', 26, sd.DMUT),
                      sd.p('Can the thin-film lab etch, then sputter/evaporate Cu and Li inside the ogive from the axis?', 26, sd.DMUT),
                      sd.p('What current do you expect? (≤ 1 µA: the x-rays never matter)', 26, sd.DMUT),
                      sd.p('Would Ti (15 µm) instead of Cu be easy? No x-rays at all, but it takes up hydrogen.', 26, sd.DMUT), gap=20), gap=80),
        dark=True, short='for Pierfrancesco')

D.write(OUTF, note_meta=dict(title='LNL target: his ogive in Al with a Cu liner',
                             summary='Pierfrancesco’s ogive made of Al with 12 µm of Cu only where the beam stops and a masked Li film: '
                                     'Geant4 L12 reach, PIXE and Micromegas x-rays, how to make it.',
                             tags='x17, lnl, target', date='2026-11-04'))
print(OUTF)
