"""Build the target-options slide note (lnl/target/TARGET_OPTIONS.md).

Reads lnl/out/target/options/ (opt_thermal.py, opt_backing.py, opt_rates.py, opt_monitor.py,
opt_geant.py), writes lnl/out/target/lnl-target-options.html:

    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/deck/build_options_deck.py
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py \\
        lnl/out/target/lnl-target-options.html --slug lnl-target-options --force --deploy
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.expanduser(os.environ.get(
    'SLIDEDOC_DIR', '~/PycharmProjects/dylan-cern-site/scripts')))
import slidedoc as sd  # noqa: E402
from slidedoc import sci  # noqa: E402

HERE = Path(__file__).resolve().parent
O = HERE.parents[1] / 'out' / 'target' / 'options'
TS = pd.read_csv(O / 'thermal_scan.csv')
TL = pd.read_csv(O / 'thermal_limits.csv')
TSEN = pd.read_csv(O / 'thermal_sensitivity.csv')
ST = pd.read_csv(O / 'stacks.csv').set_index('stack')
HY = pd.read_csv(O / 'hydrogen.csv')
LC = pd.read_csv(O / 'li_chemistry.csv')
CS = pd.read_csv(O / 'carbon_shift.csv')
PG = pd.read_csv(O / 'pige.csv')
AW = pd.read_csv(O / 'al_window.csv')
RO = pd.read_csv(O / 'rates_options.csv')
GT = pd.read_csv(O / 'g4tendl_check.csv')
GR = pd.read_csv(O / 'geant_reach.csv') if (O / 'geant_reach.csv').exists() else None
GA = pd.read_csv(O / 'geant_acceptance.csv') if (O / 'geant_acceptance.csv').exists() else None

LI, DIA, TA, AL, CU, HEAT, OK, BAD = sd.BLUE, sd.PURPLE, sd.GREY, sd.ORANGE, sd.GOLD, sd.ORANGE, sd.GREEN, sd.RED
BASE = 'Li2O 300 / Al 10 µm (FEAS baseline)'
PF = 'Li 20 µm / diamond 1 mm (Pierfrancesco)'
REC = 'Li 20 µm / Ta 10 µm / diamond 1 mm'
gain = ST.loc[PF, 'rel_g0_vs_baseline']
f441_pf = ST.loc[PF, 'f441']


def tlim(key, sig=2.0):
    q = TL[(TL.key == key) & (TL.sigma_mm == sig)]
    return float(q.I_max_uA.iloc[0])


def tfilm(key, I, sig=2.0):
    q = TS[(TS.key == key) & (TS.sigma_mm == sig) & np.isclose(TS.I_uA, I)]
    return float(q.T_film_C.iloc[0])


I_F = tlim('F_dia1000_li20_clamp')
I_G = tlim('G_dia1000_li20_braze')
I_H = tlim('H_dia_mch_li20')
I_A = tlim('A_al10_disk')

D = sd.Deck('Target options for MX17 at LNL',
            'Film, backing, cooling, vacuum and monitoring for the ⁷Li(p,e⁺e⁻)⁸Be target: thermal model, nuclear yields '
            'from measured data, and Geant4 of the target assembly.')

# --------------------------------------------------------------------------- #
# cover
if GR is not None and 'li20_mo8_dia50' in set(GR.config):
    g = GR.set_index('config')
    d_rec = g.loc['li20_mo8_dia50', 'days_ref_1uA']
    big3 = sd.bignum(f'{d_rec:.2g} d', 'to 3σ at ATOMKI per µA: 20 µm Li / 8 µm Mo / 50 µm diamond', sd.DGREEN,
                     f'thin Li₂O baseline {g.loc["base", "days_ref_1uA"]:.2g} d; 1 mm diamond {g.loc["li20_dia1", "days_ref_1uA"]:.2g} d (Geant4 L9)')
else:
    big3 = sd.bignum('0', 'backing lines in the 13–18 MeV window', sd.DGREEN, 'C, Ta, Cu, Al: all below 11 MeV')
cover = (sd.kicker('MX17 at LNL · target options · 22 Oct 2026')
         + '<h1 style="font-size:56px;font-weight:600;line-height:1.1;letter-spacing:-1.5px">'
           'Pierfrancesco’s 20 µm lithium on diamond is the right target, on a thin membrane rather than 1 mm: at LNL the heat is easy, '
           'a thick backing costs the leptons, and the open questions are hydrogen, adhesion and vacuum.</h1>'
         + sd.p('A thermal model of every backing, nuclear yields from measured data for what the film and backing emit, '
                'and Geant4 (run L9) of the leptons through the target assembly.', 28, sd.DMUT)
         + sd.row(
             sd.bignum(f'×{gain:.1f}', '⁸Be γ₀ per proton, 20 µm Li vs 1.5 µm Li₂O', sd.DBLUE,
                       f'beam 1.10 → 0.87 MeV; 441-keV share {f441_pf:.2%}'),
             sd.bignum(f'{I_F:.0f} µA', 'keeps 20 µm Li below 150 °C on 1 mm diamond', '#f0a35e',
                       f'dry rim clamp; {I_G:.0f} µA brazed; LNL runs ≤ 4 µA'),
             big3, gap=56))
D.slide('cover', cover, '''
<p>Pierfrancesco's reply to the LNL slides: the target is the critical issue. No fluorine; heat; the backing's background
and the best backing; a cold trap for carbon; PIGE monitoring; the 441 keV γ and the window; the strip/clamp design; and his
proposal of 20 µm Li on 1 mm diamond with micro-channel cooling. Each slide answers one of these. Write-up:
<code>lnl/target/TARGET_OPTIONS.md</code>; the earlier fluorine/heat study is the note <code>lnl-lithium-target</code>.</p>''',
        dark=True, short='cover')

# --------------------------------------------------------------------------- #
# the recommended assembly, drawn
W, H = 1664, 400


def stack_diagram():
    s = []
    y0, x0, top, bot = 200, 300, 80, 320
    s.append(sd.arrow(20, y0, x0 - 20, y0, sd.INK, 5, 18))
    s.append(sd.T(150, y0 - 22, 'p, 1.10 MeV, ≤ 0.5 µA', 22, sd.INK))
    layers = [(40, LI, 'metallic Li, 1.07 mg/cm²: the beam leaves it at 0.87 MeV, above the 441 keV resonance'),
              (14, TA, 'Mo or Ta 8 µm: stops the beam (range 6 µm), holds the hydrogen, collects the charge, wets Li'),
              (40, DIA, 'CVD diamond 50–100 µm, k ≈ 1800 W/m/K: carries the heat to the ring; thin, so the leptons barely see it')]
    x = x0
    for w, c, tip in layers:
        s.append(f'<rect x="{x}" y="{top}" width="{w}" height="{bot - top}" fill="{c}" opacity=".85"{sd.tipattr(tip)}/>')
        x += w
    s.append(sd.T(x0 - 12, 268, 'Li 20 µm', 22, LI, anchor='end'))
    s.append(sd.T(x0 - 12, 298, 'Mo/Ta 8 µm', 22, TA, anchor='end'))
    s.append(sd.T(x0 + 120, 210, 'CVD diamond 50–100 µm', 22, DIA, anchor='start'))
    for yy in (top - 40, bot):
        s.append(f'<rect x="{x0 + 54}" y="{yy}" width="{x - x0 - 54 + 70}" height="40" fill="{CU}" opacity=".8"'
                 f'{sd.tipattr("Cu ring clamped or brazed to the membrane rim (r ≥ 8 mm), water-cooled")}/>')
        s.append(f'<circle cx="{x + 40}" cy="{yy + 20}" r="12" fill="#5aa9e6"{sd.tipattr("cooling water")}/>')
    s.append(sd.T(x + 90, top - 14, 'Cu ring, water-cooled', 21, CU, anchor='start'))
    s.append(f'<rect x="{x0 - 140}" y="16" width="{x - x0 + 330}" height="{H - 32}" fill="none" stroke="#5aa9e6" '
             f'stroke-width="4" stroke-dasharray="12 8" rx="20"{sd.tipattr("LN₂-cooled shroud: pumps water (Li getter) and hydrocarbons (carbon)")}/>')
    s.append(sd.T(x0 - 125, H - 30, 'LN₂ shroud', 21, '#3b86c6', anchor='start'))
    xt = x + 300
    for i, (t, c) in enumerate((('HPGe / LaBr₃ at 0.5–1 m: 478 keV PIGE (Li content)', sd.INK),
                                ('Si detector, backward: elastic protons (C, O on the Li)', sd.INK),
                                ('at the centre of the arms: < 0.15 % X₀ in the leptons’ path', sd.INK),
                                ('1 mm / micro-channel diamond: for ≥ 30 µA machines', sd.MUT))):
        s.append(sd.T(xt, 130 + 44 * i, t, 23, c, anchor='start'))
    return sd.svg(W, H, ''.join(s), 'recommended target assembly')


D.slide('design', sd.title('For LNL: 20 µm Li on 8 µm Mo on a thin CVD diamond membrane, ring-cooled, in a cold shroud',
                           'Every element answers one of Pierfrancesco’s points. Hover the layers.')
        + stack_diagram()
        + sd.table(['his point', 'answer here'], [
            ['no fluorine; a lot of heat', 'metallic Li (×2.2 Li per keV of beam) on 50 µm diamond: 35 °C at 4 µA, < 150 °C to 30–40 µA'],
            ['background from the backing', 'Mo/Ta stops the beam: no backing line above 1 MeV; bare diamond: 2.37 and 8.06 MeV, below the window'],
            ['1 mm diamond, micro-channels', 'not needed below ~30 µA, and ×1.4–1.9 slower per µA: legs cross it edge-on (Geant4 L9)'],
            ['carbon; cold trap', 'one LN₂ shroud pumps carbon and water (Li is a getter)'],
            ['PIGE; germanium?', '478 keV to 1 % in 10–60 s; Ge only for the Na/B lines, and safe: no neutrons below 1.88 MeV'],
        ], size=21, align=['left', 'left'], widths=[400, 1260]),
        '''<p>Mo (or Ta) between the Li and the diamond does three jobs: it stops the 0.87 MeV protons (range 6 µm), so the hydrogen
lands in a metal that tolerates ≥ 3.4×10¹⁹ /cm²; it carries the beam current away (diamond is an insulator); and it gives
lithium something to wet, which an untreated diamond surface may not. The diamond's only job is to carry the heat.</p>''',
        short='design')

# --------------------------------------------------------------------------- #
# film thickness
rows = []
for k, lab in (('Li2O 300 / Al 10 µm (FEAS baseline)', 'Li₂O 1.5 µm (FEAS baseline)'),
               ('Li 10 µm / diamond 1 mm', 'Li 10 µm'), (PF, 'Li 20 µm'),
               ('Li 20 µm / diamond, E_p 1.20 MeV', 'Li 20 µm, E_p 1.20'), ('Li 40 µm / diamond 1 mm', 'Li 40 µm')):
    v = ST.loc[k]
    col = LI if v.f441 < 0.02 else HEAT
    rows.append((lab, v.rel_g0_vs_baseline, col,
                 f'{k}: beam leaves the film at {v.E_after_film_keV:.0f} keV; γ₀ {v.Y_g0_per_p:.3g}/p; '
                 f'441-keV share {v.f441:.2%}; 18.15 resonant share {v.f18res:.0%}',
                 f'out at {v.E_after_film_keV:.0f} keV · 441 share {v.f441:.1%}'))
rows.append(('Li stopping the beam', 78, BAD, '441 keV dominates: 77 % of γ₀', 'out at 0 · 441 share 77 %'))
D.slide('film', sd.title(f'A 20 µm lithium film gives ×{gain:.1f} the ⁸Be rate per proton and stays clear of the 441 keV resonance',
                         'γ₀ per proton relative to the 1.5 µm Li₂O baseline, E_p = 1.10 MeV (Zahnow 1995 cross sections)')
        + sd.hbars(rows, vmax=80, vmin=0.8, log=True, width=560, h=40, label_w=360,
                   fmt=lambda v: f'×{v:.1f}' if v < 50 else f'×{v:.0f}', size=26)
        + sd.callout('Statistics were never LNL’s limit (1 d to 3σ at 1 µA). The gain buys a lower current: the same X17 rate at '
                     '~0.12 µA, with ×8 less heat, hydrogen and carbon. 15–25 µm keeps the 441 share below 1 %.', LI, 25),
        '''<p><code>opt_backing.py</code> + <code>target_model.layered_yield</code> → <code>stacks.csv</code>. The X17 is normalised per
total γ₀ as in FEAS (ATOMKI 2022 reported the anomaly in direct capture too). If it came from the M1 resonance only, the
20 µm gain is ×6.7. The 3D fit absorbs a known energy profile; a 20 % 441 share biases it by < 0.06 R_ATOMKI
(TARGET_STUDY §8), so 0.85 % is negligible.</p>''', short='film')

# --------------------------------------------------------------------------- #
# heat
P = sd.Plot(1060, 560, x=(0.25, 300, 'log'), y=(0, 400), xlabel='beam current (µA), 1.10 MeV, σ = 2 mm',
            ylabel='film temperature (°C)')
P.xticks([(v, f'{v:g}') for v in (0.25, 1, 4, 10, 30, 100, 300)]).yticks([(v, str(v)) for v in range(0, 401, 100)])
OPTS = [('A_al10_disk', 'Li₂O / 10 µm Al disk', AL), ('B_graphite25', 'Li₂O / 25 µm graphite foil', sd.GREY),
        ('C_dia50_li2o', 'Li₂O / 50 µm diamond', sd.GREEN), ('E_dia300_li20', 'Li 20 µm / 300 µm diamond', sd.BLUE),
        ('F_dia1000_li20_clamp', 'Li 20 µm / 1 mm diamond, dry clamp', DIA),
        ('H_dia_mch_li20', 'Li 20 µm / micro-channel diamond', '#5aa9e6'),
        ('G_dia1000_li20_braze', 'Li 20 µm / 1 mm diamond, brazed rim', sd.INK)]
for k, lab, c in OPTS:
    q = TS[(TS.key == k) & (TS.sigma_mm == 2.0)].sort_values('I_uA')
    q = q[q.T_film_C < 420]
    P.line(q.I_uA, q.T_film_C, c, tips=[f'{lab}: {t:.0f} °C at {i:g} µA ({pw:.1f} W)' for i, t, pw in zip(q.I_uA, q.T_film_C, q.P_W)])
P.hline(150, BAD, label='Li film limit 150 °C (melts 180)', tip='metallic Li melts at 180.5 °C', anchor='start')
P.hline(300, sd.MUT, label='Li₂O working limit 300 °C', tip='LiOH / diffusion / evaporation', anchor='start')
P.vline(4, sd.MUT, label='LNL CN 4 µA', tip='AN2000 ~1 µA, CN up to ~4 µA')
leg = sd.legend([(lab, c) for _, lab, c in OPTS], 19)
lims = [[lab, f'{tlim(k):.0f}', f'{tlim(k, 1.0):.0f}'] for k, lab, _ in OPTS]
D.slide('heat', sd.title('Diamond makes the heat a non-problem: below 30 °C at LNL’s 4 µA, below 150 °C up to a few hundred µA',
                         'Axisymmetric finite-volume model: beam deposited where the protons stop, k(T), contacts, radiation')
        + sd.row(sd.col(P.svg('film temperature'), leg, gap=8, w=1060),
                 sd.col(sd.table(['option', 'I max, σ 2 mm', 'σ 1 mm'], lims, size=20, widths=[330, 120, 90]),
                        sd.callout(f'Micro-channels ({I_H:.0f} µA) are not needed at LNL; a 1 mm diamond brazed to a cooled ring '
                                   f'({I_G:.0f} µA) does as well with no water in the target.', DIA, 22), w=560, gap=20), gap=36),
        f'''<p><code>opt_thermal.py</code>. Checks: a conduction-only disk agrees with the analytic Gaussian-source result to 0.7 %;
the 10 µm Al disk of the earlier study gives 97.6 °C against 95 °C. Contacts: dry clamp 5×10³–10⁴ W/m²/K, braze 2×10⁵,
water 2×10⁴, micro-channels as h_eff = 3×10⁴ (laminar, 200 × 300 µm channels at 400 µm pitch, 1 L/min, Δp 1.2 bar).
Limits: Li film 150 °C, Li₂O 300 °C. LNL beam power is 1.1 W/µA: the issue on a thin foil is the conduction path, not the power.</p>
<p>Why the slide-7 clamp failed: 20 µm of Li conducts k·t = 1.7 mW/K sideways, 1 mm of diamond 1.8 W/K. The backing must be the conductor.</p>''',
        foot='thermal_scan.csv, thermal_limits.csv · CVD diamond k 1800 W/m/K (thermal grade)', short='heat')

# --------------------------------------------------------------------------- #
# sensitivities
s1 = TSEN[TSEN.h_int.isna() & (TSEN.k_diamond == 1800.0) & (TSEN.I_uA == 100)].sort_values('h_clamp')
s2 = TSEN[TSEN.h_int.notna() & (TSEN.I_uA == 100)].sort_values('h_int')
P2 = sd.Plot(760, 520, x=(1e3, 1e6, 'log'), y=(0, 300), xlabel='conductance (W/m²/K)', ylabel='film °C at 100 µA (110 W)')
P2.xticks([(v, sci(v, 0)) for v in (1e3, 1e4, 1e5, 1e6)]).yticks([(v, str(v)) for v in range(0, 301, 50)])
P2.line(s1.h_clamp, s1.T_film_C, CU, tips=[f'rim clamp h = {h:.0e}: {t:.0f} °C' for h, t in zip(s1.h_clamp, s1.T_film_C)])
P2.line(s2.h_int, s2.T_film_C, LI, tips=[f'Li/diamond interface h = {h:.0e}: {t:.0f} °C' for h, t in zip(s2.h_int, s2.T_film_C)])
P2.hline(150, BAD, label='150 °C', anchor='start')
D.slide('contacts', sd.title('Above ~30 µA the contacts set the temperature, not the diamond: braze the rim, metallise the face',
                             '1 mm diamond, 20 µm Li, 100 µA: vary the rim-clamp contact and the Li/diamond interface')
        + sd.row(sd.col(P2.svg('contacts'), sd.legend([('rim clamp to the cooled ring', CU), ('Li/diamond interface', LI)], 22), w=760),
                 sd.col(sd.callout('A dry clamp in vacuum (10³–10⁴) is the bottleneck: braze or indium. CVD-diamond gyrotron windows '
                                   'are brazed to Cu cuffs and edge-cooled the same way.', CU, 24),
                        sd.callout('Nobody seems to have measured evaporated Li on diamond. A Ta/Mo/Ti layer (carbide-forming) is the '
                                   'standard fix, and the same layer stops the beam: one bench test answers it.', LI, 24),
                        sd.callout('Diamond grade: k = 1000 instead of 1800 adds ~20 K at 100 µA. Irrelevant at LNL.', sd.GREY, 24),
                        w=820, gap=24), gap=60),
        '<p><code>thermal_sensitivity.csv</code>. At LNL’s ≤ 4 µA none of this matters (≤ 25 °C for any contact ≥ 10⁴).</p>',
        short='contacts')

# --------------------------------------------------------------------------- #
# backing emissions
def cell(v, d=2):
    return '—' if not v or v <= 0 else (f'{v:.{d}g}' if v < 100 else f'{v:,.0f}')


rows, tips = [], []
for k, lab in ((BASE, 'Li₂O / Al 10 µm (FEAS baseline)'), ('Li2O 300 / diamond 50 µm', 'Li₂O / diamond 50 µm'),
               (PF, 'Li 20 µm / diamond 1 mm'), ('Li 20 µm / ¹²C diamond 1 mm (99.99 %)', 'Li 20 µm / ¹²C-enriched diamond'),
               (REC, 'Li 20 µm / Ta 10 µm / diamond'), ('Li 20 µm / Cu 1 mm (BNCT-style)', 'Li 20 µm / Cu 1 mm')):
    v = ST.loc[k]
    rows.append([lab, cell(v.L478_per_g0, 3), cell(v.Al_843_per_g0), cell(v.C12_237_per_g0), cell(v.C13_806_per_g0),
                 cell(v.Al_res_per_g0)])
    tips.append(f'{k}: beam stops in {v.beam_stops_in}')
eq = RO[((RO['stack'] == BASE) & (RO.I_uA == 1.0)) | ((RO['stack'].isin([PF, REC])) & (RO.I_uA == 0.125))]
eqrows = [[r[1].replace('Li2O', 'Li₂O').replace(' (FEAS baseline)', '').replace(' (Pierfrancesco)', ''), f'{r.I_uA:g}',
           f'{r.g0_per_s:,.0f}', f'{r.legs_per_arm_s:.2g}', f'{r.mm_hits_per_arm_s:,.0f}', f'{r.mm_occupancy:.1e}'] for r in eq.itertuples()]
D.slide('backing', sd.title('Nothing the backing emits reaches the 13–18 MeV window, and a Ta layer silences it entirely',
                            'γ-rays per ⁸Be γ₀ from measured cross sections; then trigger legs and Micromegas hits from Geant4 (L9 bklines, big plastics)')
        + sd.table(['film / backing', '478 keV (Li)', '843 keV (Al)', '2.37 MeV (¹²C)', '8.06 MeV (¹³C)', '10.8 MeV (²⁷Al)'],
                   rows, size=22, tips=tips, widths=[520, 200, 200, 220, 220, 220])
        + sd.table(['at the same X17 rate', 'µA', 'γ₀ /s', 'backing legs /arm/s', 'MM hits /arm/s', 'MM occupancy'],
                   eqrows, size=21, widths=[560, 90, 150, 260, 230, 200])
        + sd.p('Cosmics give ~15 legs/arm/s. The Al backing’s 10.8 MeV line (992 keV resonance) alone makes ~23 at 1 µA. '
               'The 478 keV line costs < 0.1 % Micromegas occupancy.', 23, sd.MUT),
        '''<p>Inputs: ⁷Li(p,p′γ) from Bykov et al. ARI 175 (2021) (thick Li 4.9×10⁶ /µC at 1.0 MeV); ¹³C(p,γ) 556 keV resonance from
Skowronski et al. PRC 111 064611 (2025); ¹²C(p,γ) 457 keV resonance (ωγ 0.6 eV); ²⁷Al(p,γ) 632/773/992 keV (ωγ 0.26/0.13/1.91 eV,
the first two ESTIMATE) and (p,p′)843 keV (2 mb, ESTIMATE ×3). Resonances are integrated analytically per energy step (checked
against (λ²/2)ωγ/ε). Ta/Cu Coulomb excitation (≤ 1.1 MeV) not computed. No neutrons below E_p = 1.88 MeV.</p>
<p>Detector response: Geant4 L9 <code>gam_7Li_bklines</code>, 10⁷ γ in nine lines from the spot, big plastics; a leg = SiPM bar AND
plastic ≥ 0.5 MIP. <code>opt_rates.py</code> → <code>line_response.csv</code>, <code>rates_options.csv</code>.</p>''',
        foot='stacks.csv, lines.csv, rates_options.csv', short='backing γ')

# --------------------------------------------------------------------------- #
# which backing
D.slide('which', sd.title('Which backing: diamond to carry the heat, a heavy metal layer to stop the beam',
                          'Every criterion that matters for a ⁷Li(p,γ) target at 1 MeV')
        + sd.table(['backing', 'k (W/m/K)', 'X₀', 'γ background', 'hydrogen', 'with Li', 'charge', 'verdict'], [
            ['<b>CVD diamond</b>', '1800', '12 cm', '2.37, 8.06 MeV lines', 'unknown (gap)', 'inert; adhesion?', 'insulator', '<b>best, under a metal layer</b>'],
            ['<b>Ta 10 µm</b> (or Mo)', '57 (138)', '0.4 cm', 'none', '≥ 3.4×10¹⁹ /cm²', 'excellent', 'conducts', '<b>the beam stop</b>'],
            ['Cu', '400', '1.4 cm', 'none', 'blisters ~10¹⁹', 'slow dissolution', 'conducts', 'thick + offset only'],
            ['Al', '237', '8.9 cm', '992 keV res. → 10.8 MeV', 'blisters ~10¹⁸', '<b>alloys with Li</b>', 'conducts', 'avoid in the beam'],
            ['graphite foil', '400 ∥ / 5 ⊥', '19 cm', 'as diamond', 'outgasses', 'inert', 'conducts', 'thin option'],
            ['Be, Si, SiC', '150–400', '9–35 cm', '(p,γ), (p,α) lines', '—', 'Si alloys with Li', '—', 'no'],
        ], size=21, align=['left'] * 8, widths=[230, 150, 100, 280, 230, 210, 140, 300]),
        '<p>X₀ only matters for a backing in the leptons’ path, i.e. a target at the centre; at +12 cm (Geant4 L9) the backing is behind the leptons.</p>',
        short='which backing')

# --------------------------------------------------------------------------- #
# hydrogen and vacuum
h1 = HY[(HY.sigma_mm == 2.0) & (HY.I_uA == 1.0)].set_index('stop_material')
lc = LC.set_index(['p_partial_mbar', 'gas'])
cs = CS[(CS.I_uA == 1.0) & (CS.days == 14)]


def csv_(vac, film, col):
    return float(cs[(cs.vacuum.str.startswith(vac)) & (cs.film.str.startswith(film))][col].iloc[0])


D.slide('vacuum', sd.title('Lithium is a getter: the cold shroud Pierfrancesco wants for carbon must also pump the water',
                           'Hydrogen where the beam stops, residual-gas chemistry on metallic Li, and carbon build-up')
        + sd.row(
            sd.col(sd.p('Hydrogen at the spot: 2.1×10¹⁸ /cm² per day per µA', 26, sd.INK, 600),
                   sd.table(['beam stops in', 'days to blister onset, 1 µA'], [
                       ['Al', f'{h1.loc["Al", "days_to_onset"]:.1f}'], ['Cu', f'{h1.loc["Cu", "days_to_onset"]:.1f}'],
                       ['Ta', f'≥ {h1.loc["Ta", "days_to_onset"]:.0f}'], ['diamond', 'unknown (gap)'], ['Li (thick)', 'LiH, no blisters']],
                       size=22, widths=[280, 330]),
                   sd.p('At ~0.12 µA (20 µm Li) Ta lasts months.', 22, sd.MUT), w=640, gap=14),
            sd.col(sd.p('Water and O₂ eat metallic Li', 26, sd.INK, 600),
                   sd.table(['partial pressure', 'H₂O: Li → LiOH per day', '20 µm gone in'], [
                       [f'{p:.0e} mbar', f'{lc.loc[(p, "H2O"), "Li_consumed_um_per_day"]:.2g} µm',
                        f'{lc.loc[(p, "H2O"), "days_to_eat_20um"]:.0f} d'] for p in (1e-6, 1e-7, 1e-8)],
                       size=22, widths=[220, 300, 200]),
                   sd.p('Spec: H₂O ≤ 10⁻⁸ mbar at the target: LN₂ shroud + bake. Li₂O hydrates too.', 22, sd.MUT), w=760, gap=14),
            gap=60)
        + sd.callout(f'Carbon, 14 days at 1 µA with no trap: γ₀ ×{csv_("diffusion", "Li 20", "g0_rel"):.2f} on the 20 µm Li, '
                     f'441 share {csv_("diffusion", "Li 20", "f441"):.1%}; with a cold shield ×{csv_("cold", "Li 20", "g0_rel"):.2f}. '
                     'Carbon is a 441 keV-calibration problem, not a 1 MeV one.', sd.GREY, 23),
        '''<p>Hydrogen: Budker INP in-situ blistering under 2 MeV protons (Cu from 10¹⁹ /cm², dense at 3×10¹⁹; Ta unchanged at 3.4×10¹⁹,
≥ 6.7×10²⁰ claimed); diamond: 1.2×10¹⁷ /cm² at 350 keV blistered only after a > 1400 °C anneal, no MeV/room-temperature data
found. Water/O₂: Hertz–Knudsen flux × sticking ≈ 1 on fresh Li (ESTIMATE ×3); the products stay on the target and dilute it.
Carbon: ~1 C retained per proton without a trap (Peterson & Laubert 1977), ×10 less with a cold shield, none seen with a LN₂ trap
at 10⁻⁷ mbar (Redigolo 2024). <code>opt_backing.py</code>, <code>opt_monitor.py</code>.</p>''',
        short='vacuum')

# --------------------------------------------------------------------------- #
# Geant4 L9
if GR is not None and GA is not None and len(GR) > 1:
    LAB = dict(zip(GR.config, GR.label))
    order = [c for c in ('base', 'al10_y120', 'dia50', 'li20_dia50', 'li20_mo8_dia50', 'li20_ta8_dia50', 'li20_ta_dia300',
                         'li20_dia1', 'li20_dia1_y120', 'li20_dia1_y180', 'li20_dia1_r8_y120', 'li20_mch_y120',
                         'cublock_y120') if c in set(GR.config)]
    g = GR.set_index('config')
    a = GA[GA['sample'] == 'x17'].set_index('config')
    ep = GA[GA['sample'].str.startswith('EPC') & GA['sample'].str.contains(r'\(13, 18\)')].set_index('config')
    rows = []
    for c in order:
        dd = g.loc[c, 'days_ref_1uA']
        col = sd.GREY if c == 'base' else (OK if dd < 0.25 else (DIA if dd < 1.0 else HEAT))
        rows.append((LAB[c].replace('Li₂O 300', 'Li₂O'), dd, col,
                     f'{LAB[c]}: X17 acceptance {a.loc[c, "acc"]:.3f}, σ68 {a.loc[c, "sigma68_deg"]:.1f}°, '
                     f'{a.loc[c, "frac_any_down"]:.0%} with a leg downstream; EPC share of B {g.loc[c, "B_epc_share"]:.1%}; '
                     f'E_sum {g.loc[c, "ecut"]}; per µA: {g.loc[c, "days_fit"]:.2g} d raw fit',
                     f'σ68 {a.loc[c, "sigma68_deg"]:.1f}° · acc {a.loc[c, "acc"] / a.loc["base", "acc"]:.2f}× · '
                     f'{g.loc[c, "uA_for_baseline_rate"]:.2g} µA for the baseline rate'))
    vmax = max(r[1] for r in rows) * 1.2
    D.slide('geant', sd.title('Geant4: keep the backing thin where the leptons cross it; for ⁸Be no offset moves a thick one out of the way',
                              'Days to 3σ at R(ATOMKI) per µA (big plastics), scaled to the FEAS 3D-fit reference; the film sets the yield')
            + sd.legend([('reference', sd.GREY), ('thin backing, 20 µm Li', OK), ('thick diamond', DIA),
                         ('slower than the reference', HEAT)], 20)
            + sd.hbars(rows, vmax=vmax, width=520, h=22, label_w=560, fmt=lambda v: f'{v:.2g} d', size=20),
            '''<p>Geant4 L9 (MX17_Full_Geant branch <code>lnl_target</code>, multi-layer backings): per configuration 5×10⁵ X17 (m 16.8),
5×10⁵ M1 and 5×10⁵ E1 Born IPC at 18.15 MeV, 2×10⁷ ⁸Be γ (EPC). Big plastics, LNL-calibrated calorimetry, MM 15° + TOF, the
opening angle and pointing about the target position. Reach: Asimov/Fisher fit in θ × |y| × n_down with M1, E1, γ₁ and EPC
norms free, cosmics fixed, best E_sum window; scaled so the baseline equals the reference 3D fit (FEAS §14, 1.0 d at 1 µA).
γ₁ uses the baseline L2 templates for every configuration. Per µA: the 20 µm Li films make ×8.2 the γ₀, so their days per
µA include that gain; "µA for the baseline rate" is the current that gives the baseline's X17 rate.</p>
<p><code>opt_geant.py</code> → <code>geant_acceptance.csv</code>, <code>geant_reach.csv</code>.</p>''',
            foot='Geant4 L9, 2026-10-22 · relative comparison; the full template refit for the chosen design is a follow-up', short='Geant4')

# --------------------------------------------------------------------------- #
# monitoring + window
pg = PG[(PG.I_uA == 1.0) & (PG.d_cm == 50)]
prow = [[r.film.replace(' at 1.10 MeV', ''), r.det, f'{r.peak_cps:,.0f}', f'{r.s_to_1pct:.0f} s', f'{r.total_cps_est:,.0f}'] for r in pg.itertuples()]
aw = AW[AW.Al_mm.isin([0.06, 1.0, 5.0])]
arow = [[f'{r.Al_mm:g} mm', f'{r.att_478:.1%}', f'{r.att_17p6:.1%}', f'{r.pair_conv_18MeV:.2%}', f'{r.highland_theta0_deg_8MeV:.1f}°'] for r in aw.itertuples()]
D.slide('monitor', sd.title('PIGE watches the lithium to 1 % in a minute; a thicker Al window would only add pairs',
                            'Left: 478 keV line at 50 cm, 1 µA. Right: what Al in front of the Micromegas does')
        + sd.row(sd.col(sd.table(['film', 'detector', 'peak cps', 'to 1 %', 'total cps'], prow, size=21,
                                 widths=[230, 180, 140, 110, 150]),
                        sd.callout('Ge is needed for Na (440), ¹⁰B (429) next to Li (478), not for Li alone. It is safe: nothing makes '
                                   'neutrons below E_p = 1.88 MeV. Add a backward Si detector for C and O (elastic p).', LI, 22), w=800, gap=18),
                 sd.col(sd.table(['Al', '478 keV absorbed', '17.6 MeV absorbed', '18 MeV → e⁺e⁻', 'θ₀ at 8.6 MeV'], arow, size=21,
                                 widths=[110, 190, 190, 180, 150]),
                        sd.callout('The 17.64 MeV line of the 441 keV resonance is 0.6–0.9 % of γ₀ above 441 keV and a calibration '
                                   'point; no window absorbs it. Sub-MeV γ go through mm of Al. Keep the window thin.', HEAT, 22), w=800, gap=18),
                 gap=40),
        '''<p>Full-energy efficiency at 478 keV, 10 cm: 60 % HPGe 4×10⁻³, 3″×3″ LaBr₃ 6×10⁻³ (±30 %), scaled as 1/d². Total rate ~4× the
peak (ESTIMATE). Sensitivity: 10 % less Li → −7 to −9 % in the 478 yield; 10 µg/cm² carbon → −0.6 %. Window: XCOM μ/ρ(Al) 0.0838
(0.478 MeV), 0.0227 cm²/g (17.6 MeV); pair conversion (7/9) t/X₀; Highland at 8.6 MeV. <code>opt_monitor.py</code>.</p>''',
        short='monitoring')

# --------------------------------------------------------------------------- #
# what geant4 can do
gt = GT.set_index('nucleus')
D.slide('g4', sd.title('Geant4 cannot make the target’s own γ-rays at 1 MeV; they come from measured data, Geant4 transports them',
                       'G4TENDL1.4, the proton data behind the *_AllHP physics lists below 200 MeV')
        + sd.table(['nucleus', 'σ_inel at 1.03 MeV in G4TENDL', 'what is missing'], [
            ['⁷Li', f'{gt.loc["3_7_Lithium", "sigma_b_1030keV"] * 1e3:.1f} mb, smooth ((p,α) only)', 'the 441 and 1030 keV resonances, (p,γ), (p,p′) 478 keV'],
            ['¹²C, ¹⁶O', '0 (nothing below 4.8 MeV)', '¹²C(p,γ) 457 keV resonance'],
            ['¹³C', f'{gt.loc["6_13_Carbon", "sigma_b_1030keV"] * 1e6:.0f} µb, one point per MeV', '556 keV resonance (peak ~1.4 mb)'],
            ['¹⁹F, ²⁷Al, ¹¹B', '2–6 points', 'all resonances (¹⁹F 872/935, ²⁷Al 992)'],
            ['⁶³Cu, ¹⁸¹Ta', '≈ 0', 'Coulomb excitation'],
        ], size=22, align=['left', 'left', 'left'], widths=[220, 560, 820])
        + sd.table(['quantity', 'reliability', 'from'], [
            ['lepton scattering, EPC, energy loss in the assembly', 'good', 'Geant4 L9'],
            ['⁷Li(p,γ) γ₀/γ₁; 478 keV; ¹²C/¹³C resonances', '±10–20 %', 'Zahnow 1995, Bykov 2021, Skowronski 2025'],
            ['²⁷Al minor resonances, (p,p′)843; Ta/Cu Coulex', '×2–3; not computed', 'ESTIMATE'],
            ['temperatures', '±20 % at fixed contacts', 'opt_thermal'],
            ['H blistering of diamond; Li adhesion on diamond; Li + water rate', 'unknown / ×3', 'gaps: bench tests'],
        ], size=21, align=['left', 'left', 'left'], widths=[760, 330, 510]),
        '<p><code>lxplus/g4tendl_check.py</code> → <code>g4tendl_check.csv</code>.</p>', short='Geant4 limits')

# --------------------------------------------------------------------------- #
end = (sd.kicker('gaps to close, and questions for Pierfrancesco and Stephan')
       + sd.row(
           sd.col(sd.p('Bench / beam tests that close the gaps', 32, sd.DINK, 600),
                  sd.p('1. ~1 MeV protons on bare and Mo/Ta-coated CVD diamond to 10¹⁹–10²⁰ /cm²: blisters? graphitisation?', 24, sd.DMUT),
                  sd.p('2. 20 µm Li on Mo/Ta-coated diamond: adhesion and interface thermal resistance.', 24, sd.DMUT),
                  sd.p('3. A Li target at known water pressure, followed by PIGE + elastic p.', 24, sd.DMUT),
                  sd.p('4. Clamp or braze a 50–100 µm diamond membrane to a cooled Cu ring; thermal-cycle it.', 24, sd.DMUT),
                  sd.p('5. Simulation: the full 3D template refit for the chosen design; the real holder and LNL beam line in Geant4.', 24, sd.DMUT),
                  w=820, gap=16),
           sd.col(sd.p('Questions', 32, sd.DINK, 600),
                  sd.p('1. Li evaporated in situ, or moved under vacuum? Is there a Li evaporator at LNL?', 24, sd.DMUT),
                  sd.p('2. Can the LNL target lab coat a CVD diamond membrane with 8 µm Mo/Ta and mount it? Diamond supplier?', 24, sd.DMUT),
                  sd.p('3. A LN₂ shroud in the chamber; typical water partial pressure?', 24, sd.DMUT),
                  sd.p('4. A HPGe at 0.5–1 m during the run?', 24, sd.DMUT),
                  sd.p('5. Beam time on AN2000/CN for the diamond test before the run?', 24, sd.DMUT),
                  w=760, gap=16), gap=64))
D.slide('end', end, '', dark=True, short='open')

out = D.write(HERE.parents[1] / 'out' / 'target' / 'lnl-target-options.html', note_meta=dict(
    title='Target options for MX17 at LNL',
    summary=('Film, backing, cooling, vacuum and monitoring for the ⁷Li(p,e⁺e⁻)⁸Be target: 20 µm Li gives ×8 the rate per proton; '
             'diamond backings stay cold far beyond LNL currents; backing γ-rays never reach the signal window; Geant4 L9 of the '
             'assembly; and the hydrogen/adhesion/vacuum gaps still to test.'),
    tags='x17, lnl, target', date='2026-10-22'),
    footer='Built by x17_facility_search/lnl/target/deck/build_options_deck.py from the opt_*.py outputs.')
print(out)
