"""Build the Demokritos neutron-beam slide note: why the lab's neutron beams cannot drive the
3He capsule to an X17 measurement.

Reads demokritos/out/neutron/*.csv (demokritos/neutron/neutron_beam.py) and writes
demokritos/out/demokritos-neutron-beam.html:

    ~/PycharmProjects/nTof_x17/.venv/bin/python demokritos/neutron/neutron_beam.py
    ~/PycharmProjects/nTof_x17/.venv/bin/python demokritos/deck/build_neutron_deck.py
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py \\
        demokritos/out/demokritos-neutron-beam.html --slug demokritos-neutron-beam --force --deploy
"""
import math
import os
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, os.path.expanduser(os.environ.get(
    'SLIDEDOC_DIR', '~/PycharmProjects/dylan-cern-site/scripts')))
import slidedoc as sd  # noqa: E402
from slidedoc import term, sci  # noqa: E402

HERE = Path(__file__).resolve().parent
DEM = HERE.parent
O = DEM / 'out'
N = O / 'neutron'

ref = pd.read_csv(N / 'reference.csv').iloc[0]
src = pd.read_csv(N / 'sources.csv').set_index('key')
rt = pd.read_csv(N / 'rates.csv').set_index('key')
bm = pd.read_csv(N / 'benchmarks.csv').set_index('key')
sw = pd.read_csv(N / 'swamp.csv')
shell = pd.read_csv(N / 'shell.csv').set_index('L_cm')
li = pd.read_csv(N / 'li_target.csv').iloc[0]
th = pd.read_csv(N / 'theta_min.csv')

GOAL = 50.0
need_bp = ref.ipc_day * ref.days_bp / GOAL           # pairs/day for 3 sigma in 50 days, big plastics
need_ab = ref.ipc_day * ref.days_ab / GOAL
lab, mx, mli = rt.loc['lab_tpn'], rt.loc['max_tpn'], rt.loc['max_li']
sw_mid = sw[sw.estimate.str.startswith('S-factor')].iloc[0]
sw_lo, sw_hi = sw.target_over_capsule.min(), sw.target_over_capsule.max()
li_ratio = li.target_over_capsule
C = dict(lab=sd.RED, max=sd.ORANGE, bench=sd.GREY, pt=sd.GREEN, need=sd.INK, therm=sd.PURPLE)


def fdays(d):
    if d >= 730:
        return f'{d / 365:,.0f} years'
    return f'{d:,.0f} days' if d >= 10 else f'{d:.1f} days'


def fn(v):
    return f'{v:,.0f}' if v >= 10 else f'{v:.1f}'


D = sd.Deck('Demokritos neutron beams for ³He: no',
            'Can the NCSR Demokritos neutron beams drive the n_TOF ³He capsule to an X17 measurement? '
            'An upper bound with every assumption in the neutrons’ favour.')

# --------------------------------------------------------------------------- #
# 1 cover
# --------------------------------------------------------------------------- #
cover = (sd.kicker('MX17 · NCSR Demokritos neutron beams on ³He · 19 Oct 2026')
         + '<h1 style="font-size:62px;font-weight:600;line-height:1.08;letter-spacing:-1.5px">'
           'The Demokritos neutron beams cannot do the ³He X17 measurement: too few pairs at the lab’s flux, '
           'and a stronger source makes its own target the experiment</h1>'
         + sd.p(f'n_TOF’s 500 bar ³He capsule placed at the lab’s sample position, X17 at ATOMKI’s strength '
                f'(X17/IPC = {sci(ref.x17_per_ipc)}), statistics only and no neutron-induced background: '
                'the most the neutrons could do.', 30, sd.DMUT)
         + sd.row(
             sd.bignum(f'{lab.ipc_per_day_1uA:,.0f}', '³He pairs per day at 1 µA', sd.DRED,
                       f'the lab’s quoted flux, 10⁶ n/cm²/s; n_TOF EAR2 gave {bm.loc["ntof"].ipc_per_day:,.0f}. '
                       f'That is {lab.x17_per_day_1uA:.1f} X17 per day.'),
             sd.bignum(fdays(lab.days_big_plastics_1uA), 'to 3σ with big plastics, at 1 µA', sd.DRED,
                       f'{fdays(lab.days_as_built_1uA)} as built. 50 days would need '
                       f'{lab.uA_for_50d_big_plastics:,.0f} µA.'),
             sd.bignum(f'×{sw_lo:,.0f}–{li_ratio:,.0f}', 'more pairs from the production target itself', sd.DGREY,
                       'at the strongest source: p + ³H → ⁴He* (or ⁷Li(p,γ)⁸Be) in the target, '
                       '1 cm from the capsule.'),
             gap=56))
D.slide('cover', cover, dark=True, short='cover',
        notes=f"""<b>Verdict.</b> With the flux the lab quotes (10⁵–10⁶ n/cm²/s at the sample), the n_TOF capsule makes {lab.ipc_per_day_1uA:,.0f} ³He pairs per day: half of n_TOF EAR2, and {need_bp / lab.ipc_per_day_1uA:,.0f}× fewer than a 3σ test in 50 days needs with the big plastics. Pushed to the most any target could give (all the tritium, the capsule 1 cm from the beam spot), the rate rises ×{mx.ipc_per_day_1uA / lab.ipc_per_day_1uA:.0f}, and then the target's own p + ³H capture makes {sw_lo:,.0f}–{sw_hi:,.0f}× more of the same ⁴He* pairs than the capsule. The measurement becomes the proton measurement, done worse.

<b>How the days are made.</b> Days to 3σ at ATOMKI's strength are scaled from the Demokritos p + t Geant4 result (same ⁴He*, same apparatus, same X17/IPC): days = {ref.days_bp:.1f} d (big plastics) or {ref.days_ab:.0f} d (as built) × {ref.ipc_day:.2e} / (³He pairs per day). This leaves out every neutron-induced background, the capsule's thick walls and the E_n spread, so it favours the neutrons. For the ILL, the same scaling gives {fdays(bm.loc['ill'].days_as_built)} as built, against the full ILL study's ~4,000 days at this strength (reach 1×10⁻² per 50 d): the scaling is optimistic by ~×2.

Code: <code>demokritos/neutron/neutron_beam.py</code> → <code>demokritos/out/neutron/</code>; write-up <code>demokritos/neutron/NEUTRON_BEAM.md</code>.""")

# --------------------------------------------------------------------------- #
# 2 setup
# --------------------------------------------------------------------------- #
W, H = 1040, 660
cy = 330
k = 40                                     # px per cm near the target
tx = 240                                   # production target x
s = []
for yy, lab_ in ((40, 'arm: MM + SiPM + plastics, ~20 cm from the target'), (H - 80, 'arm')):
    s.append(f'<rect x="150" y="{yy}" width="700" height="40" fill="{sd.BG2}" stroke="{sd.INK}" stroke-width="2"/>')
    s.append(sd.T(500, yy + 28, lab_, 21, sd.INK))
# neutron cone
s.append(sd.poly([tx + 4, tx + 640, tx + 640], [cy, cy - 230, cy + 230], sd.PURPLE, fill=sd.PURPLE + '18'))
s.append(sd.T(tx + 600, cy + 175, 'neutrons, 10⁸–10⁹ per s into 4π', 22, sd.PURPLE, 'end', 600))
# beam and target
s.append(sd.arrow(10, cy, tx - 6, cy, sd.BLUE, 5))
s.append(sd.T(16, cy - 16, 'p, ~1 µA', 22, sd.BLUE, 'start', 600))
s.append(f'<rect x="{tx - 5}" y="{cy - 45}" width="10" height="90" fill="{sd.GOLD}"{sd.tipattr("Ti-T (2.1 mg/cm² Ti, T/Ti 1.5) on 1 mm Cu, or LiF / Li metal")}/>')
s.append(sd.T(tx - 44, cy + 80, 'production target', 22, sd.INK, 'end', 600))
s.append(sd.T(tx - 44, cy + 106, 'Ti-T or Li', 21, sd.MUT, 'end'))
# capsule: gas tip 1.0 cm from the spot, 6 cm long, 2 cm diameter
c0 = tx + 5 + 1.0 * k
s.append(f'<rect x="{c0:.0f}" y="{cy - k}" width="{6 * k}" height="{2 * k}" rx="{k}" fill="{sd.BLUE}" fill-opacity="0.22" '
         f'stroke="{sd.BLUE}" stroke-width="3"{sd.tipattr("n_TOF capsule: 17 cm³ of ³He at 500 bar (1.07 g), Ø 2 cm; gas tip 1.0 cm (best case) or 1.7 cm (the lab’s sample position) from the beam spot")}/>')
s.append(sd.T(c0 + 3 * k, cy + 8, '³He, 500 bar', 22, sd.INK, weight=600))
s.append(sd.T(c0 + 6 * k + 14, cy + 8, 'n_TOF capsule', 22, sd.BLUE, 'start', 600))
s.append(sd.line(tx, cy + 52, tx, cy + 64, sd.INK, 1.5))
s.append(sd.line(c0, cy + 52, c0, cy + 64, sd.INK, 1.5))
s.append(sd.line(tx, cy + 58, c0, cy + 58, sd.INK, 1.5))
s.append(sd.T((tx + c0) / 2, cy + 52 - 4 + 30, '1 cm', 18, sd.INK))
# the two pair sources
s.append(sd.line(tx, cy, tx - 70, 80, sd.RED, 4))
s.append(sd.line(tx, cy, tx - 30, H - 80, sd.RED, 4))
s.append(sd.T(tx - 70, 170, 'target pairs', 22, sd.RED, 'end', 600))
s.append(sd.T(tx - 70, 196, 'p + ³H → ⁴He*', 21, sd.RED, 'end'))
ac = c0 + 3 * k
s.append(sd.line(ac, cy, ac + 70, 80, sd.GREEN, 4))
s.append(sd.line(ac, cy, ac - 60, H - 80, sd.GREEN, 4))
s.append(sd.T(ac + 80, 170, 'capsule pairs', 22, sd.GREEN, 'start', 600))
s.append(sd.T(ac + 80, 196, 'n + ³He → ⁴He*', 21, sd.GREEN, 'start'))
diag = sd.svg(W, H, ''.join(s), 'neutron production target, the 3He capsule, the arms')
side = sd.col(
    sd.flow([dict(label='Y₀', sub='neutrons per sr per s toward the capsule', color=sd.PURPLE,
                  tip='the lab’s quoted flux × (1.7 cm)², or computed from the target'),
             dict(label='× n σ G', sub='³He density × pair σ × ∫dV/r²', color=sd.BLUE,
                  tip=f'n = 1.25×10²² /cm³; σ_pair from Viviani et al. PRC 105 014001; G = {lab.G_cm:.2f} cm (tip at 1.7 cm), {mx.G_cm:.2f} cm (tip at 1.0 cm)'),
             dict(label='pairs/day → days', sub='scaled from the p + t Geant4 reach', color=sd.GREEN,
                  tip=f'days = {ref.days_bp:.1f} d (big plastics) × {ref.ipc_day:.2e} / pairs per day')],
            size=22),
    sd.p(f'The neutrons make the same ⁴He* as at n_TOF. The {term("production target", "the beam stops there: p + ³H, or p + ⁷Li")} '
         'makes it too, 1–2 cm upstream of the capsule.', 24),
    sd.p('Hover the dotted terms, boxes and bars for numbers and sources.', 22, sd.MUT),
    w=560, gap=28)
D.slide('setup', sd.title('The neutrons come from a target the beam stops in, 1–2 cm from the capsule',
                          'side view, roughly to scale near the target: the Demokritos neutron set-up with the n_TOF ³He capsule')
        + sd.row(diag, side, gap=40),
        short='setup',
        notes=f"""The Demokritos neutron facility (Vlastou et al., IAEA; Amanatidis 2024; FACILITY.md §3) makes quasi-monoenergetic neutrons by stopping the tandem beam in a production target: ⁷Li(p,n) (120–650 keV), ³H(p,n) on Ti-T (2.0–5.3 MeV), ²H(d,n) in a gas cell (4–11.5 MeV), ³H(d,n) on Ti-T (15–21 MeV). There is no time of flight. Samples sit ~1.7 cm from the target; the quoted maximum flux there is 10⁵–10⁶ n/cm²/s at 0.7–1 µA.

The capsule is n_TOF's: the gas profile from MX17_Full_Geant DetectorConstruction.cc, {17.0:.0f} cm³, 1.07 g of ³He. Its nose (5.5 mm of Al) goes toward the source. The flux at every point of the gas is taken at its 0° value: a generous simplification.""")

# --------------------------------------------------------------------------- #
# 3 energy window
# --------------------------------------------------------------------------- #
P = sd.Plot(1500, 600, x=(0.05, 25, 'log'), y=(40, 120), xlabel='neutron energy E_n [MeV]',
            ylabel='X17 minimum opening angle θ_min [deg]')
P.xticks([(0.1, '0.1'), (0.3, '0.3'), (1, '1'), (3, '3'), (10, '10'), (20, '20')]).yticks([(v, f'{v}') for v in range(40, 121, 20)])
bands = [(0.12, 0.65, sd.GREEN, '⁷Li(p,n)'), (2.0, 5.3, sd.GOLD, '³H(p,n)'), (4.0, 11.5, sd.RED, '²H(d,n)'),
         (15, 21, sd.RED, '³H(d,n)')]
for i, (lo, hi, c, nm) in enumerate(bands):
    P.band([lo, hi], [40, 40], [120, 120], c, 0.13, tip=f'{nm}: E_n = {lo}–{hi} MeV at Demokritos')
    P.text(math.sqrt(lo * hi), 47 + 7 * (i % 2), nm, 21, c, 'middle', 600)
P.band([0.2, 2.0], [116, 116], [120, 120], sd.GREY, 0.6, tip='n_TOF EAR2 window used in the reach, 0.2–2 MeV')
P.text(2.15, 117, 'n_TOF window', 20, sd.MUT, 'start')
sel = th[th.En_MeV >= 0.05]
P.line(sel.En_MeV.tolist(), sel.theta_min_deg.tolist(), sd.INK, markers=False,
       tip='θ_min = 2 asin(m_X / E_X), m_X = 16.94 MeV, X17 from ⁴He* at rest')
th0 = float(th[th.En_MeV == 0].theta_min_deg.iloc[0])
P.hline(th0, sd.BLUE, '4 4', label=f'thermal (ILL): {th0:.0f}°', anchor='end', where='above')
P.text(0.07, 64, 'Above ~2 MeV the edge falls into the IPC', 24, sd.INK, 'start', 600)
P.text(0.07, 58, 'and the E_n spread smears it out', 24, sd.INK, 'start', 600)
D.slide('energy', sd.title('Only ⁷Li(p,n) and the bottom of ³H(p,n) are in the X17 window',
                           'X17 edge vs neutron energy for n + ³He, with the energy ranges of the four Demokritos neutron sources')
        + sd.legend([('θ_min (m = 16.94 MeV)', sd.INK), ('thermal', sd.BLUE, 'dash'), ('⁷Li(p,n)', sd.GREEN, 'box'),
                     ('³H(p,n)', sd.GOLD, 'box'), ('deuteron beams', sd.RED, 'box'), ('n_TOF window', sd.GREY, 'box')], 22)
        + P.svg('theta_min vs E_n'),
        short='energy window',
        notes="""The physics wants E_n ≲ 2 MeV or thermal (CLAUDE.md): there the X17 edge sits at 100–111°, well above the bulk of the IPC, and the ⁴He* excitation is narrow. The deuteron sources (²H(d,n), ³H(d,n)) put E* at 23–37 MeV, where the edge is at 60–90° and the excitation is broad: out. The rest of this note uses ³H(p,n) at E_n = 2.0 MeV (E_p = 2.79 MeV at 0°) and ⁷Li(p,n) at 0.35–0.7 MeV.""")

# --------------------------------------------------------------------------- #
# 4 rates
# --------------------------------------------------------------------------- #
rows = [
    ('⁷Li(p,n), lab flux', rt.loc['lab_li'].ipc_per_day_1uA, C['lab'], f'E_n 0.35 MeV, 10⁶ n/cm²/s at 1.7 cm; σ_pair {rt.loc["lab_li"].sigma_pair_ub} µb', ''),
    ('³H(p,n), lab flux', lab.ipc_per_day_1uA, C['lab'], f'E_n 2 MeV, 10⁶ n/cm²/s at 1.7 cm; σ_pair {lab.sigma_pair_ub} µb', ''),
    ('³H(p,n), moderated', rt.loc['therm_tpn'].ipc_per_day_1uA, C['therm'],
     f'every one of {src.loc["max_tpn"].S_n_per_s:.1e} n/s thermalised and absorbed in ³He (impossible), 4.8×10⁻¹¹ pairs each', ''),
    ('n_TOF EAR2, 2026', bm.loc['ntof'].ipc_per_day, C['bench'], bm.loc['ntof'].basis, 'benchmark'),
    ('³H(p,n), all tritium', mx.ipc_per_day_1uA, C['max'],
     f'{src.loc["max_tpn"].S_n_per_s:.2e} n/s (N_T × 0.6 b), 0° ×{src.loc["max_tpn"].Y0_n_sr_s / (src.loc["max_tpn"].S_n_per_s / 4 / math.pi):.1f}; capsule tip at 1.0 cm', 'best case'),
    ('⁷Li(p,n), thick Li', mli.ipc_per_day_1uA, C['max'],
     f'10⁹ n/s at 2.5 MeV, 0° ×3; capsule tip at 1.0 cm; σ at 0.7 MeV', 'best case'),
    ('ILL, design', bm.loc['ill'].ipc_per_day, C['bench'], bm.loc['ill'].basis, 'benchmark'),
    ('3σ in 50 d, big plastics', need_bp, C['need'], f'{ref.ipc_day:.2e} × {ref.days_bp:.2f} / 50', 'needed'),
    ('p + ³H direct, 0.9 MeV', ref.ipc_day, C['pt'], 'the proton route at Demokritos, Ti-T, 1 µA', 'proton route'),
]
bars = sd.hbars(rows, vmax=3e6, vmin=50, log=True, width=900, label_w=430, h=44, size=26, fmt=fn)
D.slide('rates', sd.title(f'At the lab’s flux the capsule gets ~{round(lab.ipc_per_day_1uA, -2):,.0f} pairs a day: n_TOF-class, {need_bp / lab.ipc_per_day_1uA:,.0f}× short',
                          '³He pairs per day per µA of beam (4π, before any selection); grey: benchmarks; black: what 3σ in 50 days needs')
        + sd.legend([('lab’s quoted flux', C['lab'], 'box'), ('best case the target allows', C['max'], 'box'),
                     ('impossible bound', C['therm'], 'box'), ('benchmark', C['bench'], 'box'),
                     ('needed', C['need'], 'box'), ('proton route', C['pt'], 'box')], 22)
        + bars,
        short='pair rates', foot='demokritos/out/neutron/rates.csv, benchmarks.csv',
        notes=f"""All per µA. The lab runs its Ti-T neutron targets at 0.7–1 µA.

<b>Lab flux.</b> 10⁶ n/cm²/s at 1.7 cm is the top of the quoted range, so Y₀ = {lab.Y0_n_sr_s:.2e} n/sr/s. The capsule's nose at 1.7 cm gives G = {lab.G_cm:.2f} cm.

<b>Best case.</b> ³H(p,n): all {sci(3.96e19)} T/cm² of the lab's Ti-T at σ = 0.6 b (Brune et al. 1999 give 0.5–0.6 b near E_p = 2.8 MeV), forward-peaked ×2 in the c.m. and ×{src.loc['max_tpn'].Y0_n_sr_s / (src.loc['max_tpn'].S_n_per_s / 4 / math.pi) / 2:.1f} by the Jacobian: Y₀ = {mx.Y0_n_sr_s:.2e} n/sr/s, ×{mx.Y0_n_sr_s / lab.Y0_n_sr_s:.0f} the quoted flux. ⁷Li(p,n): a thick metallic Li target at 2.5 MeV, ~9×10⁸ n/s/µA (Lee & Zhou 1999), rounded to 10⁹ and ×3 forward. Both with the capsule's gas tip 1.0 cm from the beam spot (1 mm backing, cooling, 5.5 mm Al nose).

<b>Moderated.</b> Thermalising the neutrons helps nothing: even if every source neutron were absorbed in ³He, 4.8×10⁻¹¹ pairs per absorption gives {rt.loc['therm_tpn'].ipc_per_day_1uA:,.0f} (³H(p,n)) or {rt.loc['therm_li'].ipc_per_day_1uA:,.0f} (thick Li) pairs per day. The E0 channel adds tens of percent at thermal.

<b>Needed.</b> The Demokritos p + t Geant4 reach, {ref.days_bp:.2f} d at {ref.ipc_day:.2e} pairs/day with big plastics, scaled to 50 days: {need_bp:.2e} pairs/day ({need_ab:.2e} as built).""")

# --------------------------------------------------------------------------- #
# 5 days vs current
# --------------------------------------------------------------------------- #
P = sd.Plot(1500, 600, x=(0.1, 1000, 'log'), y=(1, 1e6, 'log'), xlabel='beam current on the production target [µA]',
            ylabel='days to 3σ at ATOMKI’s strength, big plastics')
P.xticks([(v, f'{v:g}') for v in (0.1, 1, 10, 100, 1000)]).yticks(sd.log_ticks(0, 6))
P.band([0.7, 1.0], [1, 1], [1e6, 1e6], sd.BLUE, 0.15, tip='the current the lab runs on its Ti-T neutron targets: 0.7–1 µA')
P.text(0.83, 4e5, 'lab today', 21, sd.BLUE, 'middle', 600)
P.hline(GOAL, sd.INK, '8 6', label='50 days', anchor='start', where='below')
cur = [0.1, 1000]
for key, c, dash, nm in (('lab_li', C['lab'], '10 6', '⁷Li(p,n), lab flux'), ('lab_tpn', C['lab'], None, '³H(p,n), lab flux'),
                         ('max_tpn', C['max'], None, '³H(p,n), all tritium'), ('max_li', C['max'], '10 6', '⁷Li(p,n), thick Li')):
    r = rt.loc[key]
    d1 = r.days_big_plastics_1uA
    xe = min(1000.0, d1)                                         # stop at 1 day
    P.line([0.1, xe], [d1 / 0.1, d1 / xe], c, dash=dash, markers=False)
    P.points([1.0], [d1], c, r=8, tips=[f'{nm}: {fdays(d1)} at 1 µA (as built {fdays(r.days_as_built_1uA)}); '
                                         f'50 days needs {r.uA_for_50d_big_plastics:,.0f} µA ({r.uA_for_50d_as_built:,.0f} as built)'])
    P.points([r.uA_for_50d_big_plastics], [GOAL], c, r=8, marker='open',
             tips=[f'{nm}: {r.uA_for_50d_big_plastics:,.1f} µA for 50 days'])
P.text(3, 3e5, f'Lab flux: 50 days needs {lab.uA_for_50d_big_plastics:,.0f} µA', 24, sd.RED, 'start', 600)
P.text(3, 1.3e5, f'Best case: {mli.uA_for_50d_big_plastics:.0f}–{mx.uA_for_50d_big_plastics:.0f} µA, then the target swamps it', 24, sd.ORANGE, 'start', 600)
D.slide('current', sd.title(f'50 days needs {lab.uA_for_50d_big_plastics:,.0f} µA at the lab’s flux; Ti-T targets run at 1 µA',
                            'days to 3σ against beam current, big plastics (as built is ×13 slower); open circles: the current for 50 days')
        + sd.legend([('³H(p,n), lab flux', C['lab']), ('⁷Li(p,n), lab flux', C['lab'], 'dash'),
                     ('³H(p,n), all tritium', C['max']), ('⁷Li(p,n), thick Li', C['max'], 'dash'),
                     ('at 1 µA', sd.INK, 'dot'), ('current for 50 days', sd.INK, 'open')], 22)
        + P.svg('days vs current'),
        short='days vs current', foot='demokritos/out/neutron/rates.csv; days scale as 1/I',
        notes=f"""Days scale as 1/I as long as nothing else changes. Ti-T neutron targets are run at 0.7–1 µA because the tritium leaves a hot target; at E_p = 2.8 MeV, {lab.uA_for_50d_big_plastics:,.0f} µA is {lab.uA_for_50d_big_plastics * 2.8:,.0f} W into a ~1 cm² spot.

The best-case lines need {mx.uA_for_50d_big_plastics:.0f} µA (³H(p,n)) or {mli.uA_for_50d_big_plastics:.0f} µA (thick Li) for 50 days. They are not achievable in practice (the capsule's gas 1 cm from a water-cooled target, all of the target's yield counted, every factor rounded up), and even granting them, the next slide shows the target's own pairs dominating.

As built, with the n_TOF trigger stack: {fdays(lab.days_as_built_1uA)} at the lab's flux, {fdays(mx.days_as_built_1uA)} in the ³H(p,n) best case.""")

# --------------------------------------------------------------------------- #
# 6 the production target swamps the capsule
# --------------------------------------------------------------------------- #
sh5 = shell.loc[5]
rows = [
    ('³He capsule', mx.ipc_per_day_1uA, sd.GREEN, f'n + ³He, best case, capsule tip at 1.0 cm', '³H(p,n) source'),
    ('³He shell, 5 cm, 4π', sh5.shell_pairs_per_day_1uA, sd.GREEN,
     f'every source neutron through 5 cm of 500 bar ³He: {sh5.he3_grams:.0f} g of ³He, cannot be built', 'impossible bound'),
    ('Ti-T target itself', sw_mid.target_pairs_per_day_1uA, sd.RED,
     f'p + ³H → ⁴He* at E* = {sw_mid.Estar_MeV:.1f} MeV: σ(p,γ) {sw.sigma_pg_ub.min():.0f}–{sw.sigma_pg_ub.max():.0f} µb, α_E1 {sw_mid.alpha_E1:.2e}', 'same ⁴He*'),
    ('³He capsule', mli.ipc_per_day_1uA, sd.GREEN, 'n + ³He, thick-Li best case', '⁷Li(p,n) source'),
    ('Li target itself', li.pairs_per_day_1uA, sd.RED,
     f'⁷Li(p,γ)⁸Be through both resonances: {li.gamma_per_s_1uA:.2e} γ/s, α ≈ 3.5×10⁻³', '⁸Be pairs'),
]
bars = sd.hbars(rows, vmax=3e8, vmin=1e3, log=True, width=880, label_w=400, h=50, size=26, fmt=lambda v: sci(v))
D.slide('swamp', sd.title(f'Any source strong enough makes the target the experiment: ×{sw_lo:,.0f}–{li_ratio:,.0f} more pairs than the capsule',
                          'pairs per day per µA: the ³He capsule against the production target, same beam; the target sits 1 cm upstream of the capsule')
        + sd.legend([('pairs from n + ³He', sd.GREEN, 'box'), ('pairs from the beam in the production target', sd.RED, 'box')], 22)
        + bars
        + sd.callout(f'With ³H(p,n), the target makes the same ⁴He* as the capsule (E* {sw_mid.Estar_MeV:.1f} against 22.1 MeV): '
                     'the “neutron” measurement is the proton measurement with ×' + f'{sw_mid.target_over_capsule:,.0f}' + ' less signal.', sd.RED, 26),
        short='target swamps',
        foot='demokritos/out/neutron/swamp.csv, shell.csv, li_target.csv',
        notes=f"""<b>³H(p,n) source.</b> The same protons that make the neutrons capture on the target's tritium: ³H(p,γ)⁴He, E* = {sw_mid.Estar_MeV:.2f} MeV at E_p = {sw_mid.Ep_MeV:.2f} MeV. Two estimates of σ(p,γ): the Hahn S-factor fit extrapolated ({sw_mid.sigma_pg_ub:.0f} µb), and detailed balance on ⁴He(γ,p)³H with σ(γ,p) = 0.6–1.2 mb near 22 MeV (Shima et al. PRC 72 (2005) 044004; Raut et al. PRL 108 (2012) 042502; the data disagree by up to ~50 %), giving {sw.sigma_pg_ub.min():.0f}–{sw.sigma_pg_ub.max():.0f} µb. With the Born E1 pair fraction {sw_mid.alpha_E1:.2e}: {sw.target_pairs_per_day_1uA.min():.1e}–{sw.target_pairs_per_day_1uA.max():.1e} pairs/day, against {mx.ipc_per_day_1uA:.2e} from the capsule: ×{sw_lo:,.0f}–{sw_hi:,.0f}.

The two vertices are 1–7 cm apart. MX17 cannot separate them: the MM pointing cut accepts tracks within 135 mm of the assumed vertex, and the angular resolution is 9–14°. So the target's pairs are signal and background in the capsule's analysis, with the same X17 edge.

<b>4π shell bound.</b> Even if every source neutron crossed L cm of 500 bar ³He: {shell.loc[1].shell_pairs_per_day_1uA:.1e} / {shell.loc[5].shell_pairs_per_day_1uA:.1e} / {shell.loc[10].shell_pairs_per_day_1uA:.1e} pairs/day for L = 1 / 5 / 10 cm ({shell.loc[1].he3_grams:.0f} / {shell.loc[5].he3_grams:.0f} / {shell.loc[10].he3_grams:.0f} g of ³He), still ×{shell.loc[1].target_over_shell:.0f} / ×{shell.loc[5].target_over_shell:.0f} / ×{shell.loc[10].target_over_shell:.0f} below the target.

<b>⁷Li(p,n) source.</b> A thick Li target at 2.5 MeV captures through the 441 keV (17.64 MeV) and 1030 keV (18.15 MeV) resonances on the way down: {li.Y_g0:.2e} γ₀ + {li.Y_g1:.2e} γ₁ per proton (the LNL cross sections; direct capture held flat above the last measured point). Those are ⁸Be pairs at E* = 17.6–18.2 MeV, ×{li_ratio:,.0f} the capsule's. Their E_sum is 3–4 MeV lower, but the arms contain ~40 % of the lepton energy, so an E_sum cut cannot remove ×10³.""")

# --------------------------------------------------------------------------- #
# 7 end
# --------------------------------------------------------------------------- #
pt = bm.loc['pt']
end = (sd.kicker('verdict')
       + '<h2 style="font-size:56px;font-weight:600;line-height:1.12">Close the neutron-beam option at Demokritos. '
         'If Demokritos, then protons on its tritium.</h2>'
       + sd.row(
           sd.col(sd.p('<b>Why it is closed</b>', 30, sd.DINK),
                  sd.p(f'• The lab’s flux gives {lab.ipc_per_day_1uA:,.0f} ³He pairs/day: {fdays(lab.days_big_plastics_1uA)} to 3σ with big plastics.', 26, sd.DINK),
                  sd.p(f'• Moderating to thermal gives no more: ≤ {rt.loc["therm_tpn"].ipc_per_day_1uA:,.0f} pairs/day even if every neutron is absorbed.', 26, sd.DINK),
                  sd.p(f'• A source strong enough makes ×{sw_lo:,.0f}+ more pairs in its own target, 1 cm away.', 26, sd.DINK),
                  sd.p('• Every neutron-induced background was left out; each would make it worse.', 26, sd.DINK), gap=16),
           sd.col(sd.p('<b>What this does not rule out</b>', 30, sd.DINK),
                  sd.p(f'• p + ³H on the lab’s Ti-T at 0.9 MeV, below the (p,n) threshold: '
                       f'{pt.days_big_plastics:.1f} d with big plastics, {pt.days_as_built:.0f} d as built (Geant4, statistics only).', 26, sd.DINK),
                  sd.p('• ³He with neutrons where the flux is 10⁴× higher and no target sits next to the cell: the ILL, GANIL-NFS.', 26, sd.DINK),
                  sd.p('• Nothing here needs the lab’s input: the numbers are the lab’s own quoted flux and physics.', 26, sd.DINK), gap=16),
           gap=80))
D.slide('end', end, dark=True, short='verdict',
        notes='Proton route: demokritos/README.md and the deck demokritos-x17-feasibility. ILL: ill/README.md. GANIL-NFS: docs/PLAN_GANIL_NFS.md.')

out = D.write(O / 'demokritos-neutron-beam.html',
              note_meta=dict(title='Demokritos neutron beams for ³He: no',
                             summary='Can the Demokritos neutron beams drive the n_TOF ³He capsule to an X17 measurement? No: ~500 pairs/day at the lab’s flux, and any stronger source makes its own target the experiment.',
                             tags='x17, demokritos, feasibility', date='2026-10-19'),
              footer='Built by x17_facility_search/demokritos/deck/build_neutron_deck.py from demokritos/neutron/neutron_beam.py outputs.')
print(out)
