"""Build the Demokritos ⁴He feasibility slide note.

Reads demokritos/out/*.csv (demokritos_rates.py) and demokritos/out/geant/ (sim/demok_geant.py,
when it has run) and writes demokritos/out/demokritos-x17-feasibility.html:

    python3 demokritos/deck/build_deck.py
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py \\
        demokritos/out/demokritos-x17-feasibility.html --slug demokritos-x17-feasibility --force --deploy
"""
import json
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
F = O / 'figures'
OG = O / 'geant'

BX = 5.1e-6
SCN = 'Demokritos Ti-T (2.1 mg/cm2), 900 keV'
C = dict(x17=sd.GREEN, ipc=sd.BLUE, e0=sd.ORANGE, epc=sd.GOLD, cos=sd.GREY, ab=sd.GREY, bp=sd.PURPLE)

ytab = pd.read_csv(O / 'yields.csv').set_index('scenario')
reach = pd.read_csv(O / 'reach.csv')
kin = pd.read_csv(O / 'kinematics.csv').set_index('Ep_keV')
ex = pd.read_csv(F / 'excitation.csv')
acch = pd.read_csv(O / 'acceptance_hist.csv')
heat = pd.read_csv(O / 'heat.csv')
nopt = pd.read_csv(O / 'neutron_option.csv')
cal = json.loads((O / 'lnl_calibration.json').read_text())
LNL = json.loads((DEM.parent / 'lnl' / 'out' / 'talk' / 'numbers.json').read_text())
lnl_ab, lnl_bp = LNL['cases']['as built|1']['days_3sigma'], LNL['cases']['big plastics|1']['days_3sigma']
lnl_x17 = LNL['cases']['as built|1']['produced_per_day']

y9 = ytab.loc[SCN]
THICK = 'Cu 1 mm, blocks downstream (Demokritos target)'


def rr(backing, z0=0.0, scn=SCN):
    return reach[(reach.scenario == scn) & (reach.backing == backing) & (reach.z0_mm == z0)].iloc[0]


r_id, r50, r100 = rr('none (ideal)'), rr('Cu 50 um'), rr('Cu 100 um')
r_thk, r_thk12 = rr(THICK), rr(THICK, 120.0)
r_sc = rr('Cu 1 mm, scatters downstream')
r_pap = rr('Cu 50 um', scn='PAPAP 250 keV, thick Ti-T')
r_thick_target = rr('Cu 50 um', scn='ATOMKI 2019/21, 900 keV')


def fd(d):
    return f'{d:.0f}' if d >= 10 else (f'{d:.1f}' if d >= 1 else f'{d:.2f}')


GEANT = (OG / 'reach_geant.csv').exists()
if GEANT:
    GS = pd.read_csv(OG / 'reach_scan.csv')
    GA = pd.read_csv(OG / 'acceptance_geant.csv')
    GT = pd.read_csv(OG / 'figures' / 'geant_theta.csv')

    def gr(cfg, hw):
        """the E_sum window with the fewest theta x |y| fit days; .days is the best counting over all windows"""
        s = GS[(GS.config == cfg) & (GS.hw == hw)]
        if s.empty:
            return None
        r = s.loc[s.days_fit_theta_y.idxmin()].copy()
        r['days'] = s.days.min()
        return r

D = sd.Deck('Demokritos ⁴He feasibility',
            'Could the MX17 apparatus test the ATOMKI ⁴He anomaly, ³H(p,e⁺e⁻)⁴He, on the 5.5 MV tandem of NCSR Demokritos? '
            'Facility, physics, Ti-T targets, rates, and the reach with the n_TOF hardware and with big plastics.')

# --------------------------------------------------------------------------- #
# 1 cover
# --------------------------------------------------------------------------- #
if GEANT and gr('cu50', 'big plastics') is not None:
    g_bp, g_ab = gr('cu50', 'big plastics'), gr('cu50', 'as built')
    d_bp, d_ab, src = g_bp.days_fit_theta_y, g_ab.days_fit_theta_y, 'Geant4, θ × |y| fit, statistics only'
else:
    d_bp, d_ab, src = r50.days_3sigma_big_plastics, r50.days_3sigma_as_built, 'LNL-calibrated toy'
cover = (sd.kicker('MX17 at NCSR Demokritos, Athens · feasibility · 19 Oct 2026')
         + '<h1 style="font-size:64px;font-weight:600;line-height:1.08;letter-spacing:-1.5px">'
           'Demokritos can test the ATOMKI ⁴He claim with its own tritium targets: '
           f'~{fd(d_bp)} days at 1 µA with big plastics, ~{fd(d_ab)} days as built</h1>'
         + sd.p('³H(p,e⁺e⁻)⁴He at E_p = 900 keV, below the (p,n) threshold: the same ⁴He* as n_TOF and the ILL, '
                'through the conjugate entrance channel. Days to 3σ at ATOMKI’s B_x = 5.1×10⁻⁶, '
                f'on a thin Cu 50 µm backing ({src}).', 30, sd.DMUT)
         + sd.row(
             sd.bignum(f'{y9.x17_per_day_1uA_4pi / 1e3:.1f}k', 'X17 per day into 4π at 1 µA', sd.DGREEN,
                       f'{y9.gamma_per_s_1uA / 1e3:.1f}k γ/s on the lab’s 2.1 mg/cm² Ti-T; '
                       f'LNL ⁸Be gives {lnl_x17:.0f}/day.',
                       tip='N_γ × B_x(ATOMKI), Hahn 1995 S-factor, T/Ti = 1.5, thick-target integration 900 → 470 keV'),
             sd.bignum('0', 'neutrons', sd.DBLUE, 'E_p < 1.019 MeV closes ³H(p,n); no γ₁ either (⁴He has no bound excited state).'),
             (sd.bignum(f'{fd(gr("cu1000_y120", "big plastics").days_fit_theta_y)} d', 'on the lab’s existing 1 mm Cu target, moved 12 cm',
                        sd.DGREEN, 'the thick backing blocks the downstream legs; seen from upstream it costs nothing (Geant4).')
              if GEANT else
              sd.bignum(f'×{r_thk.days_3sigma_as_built / r50.days_3sigma_as_built:.1f}', 'slower on the existing 1 mm Cu target',
                        sd.DRED, 'the backing blocks every downstream lepton: a thin-backed target is the one item to build.')),
             gap=56))
D.slide('cover', cover, dark=True, short='cover',
        notes=f"""The reach numbers on this cover come from {src}. Days scale as 1/I.

LNL ⁸Be for comparison (Geant4, 3D fit): {lnl_ab:.0f} d as built, {lnl_bp:.1f} d with big plastics at 1 µA.

Files: <code>demokritos/README.md</code>, <code>ESTIMATES.md</code>, <code>PHYSICS.md</code>, <code>FACILITY.md</code>, <code>GEANT_PREP.md</code>.""")

# --------------------------------------------------------------------------- #
# 2 setup diagram
# --------------------------------------------------------------------------- #
W, H = 1664, 600
cx, cy = 520, 300
s = []
# arms (top view: beam along x to the right; arms above/below and the two others drawn as boxes)
for (x0, y0, w, h, lab) in ((cx - 200, cy - 250, 400, 40, 'arm (MM + SiPM + plastics)'),
                            (cx - 200, cy + 210, 400, 40, 'arm'),):
    s.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{sd.BG2}" stroke="{sd.INK}" stroke-width="2"/>')
    s.append(sd.T(x0 + w / 2, y0 + h / 2 + 8, lab, 22, sd.INK))
# upstream / downstream halves
s.append(f'<rect x="{cx - 200}" y="{cy - 205}" width="200" height="410" fill="{sd.GREEN}" opacity="0.08"/>')
s.append(f'<rect x="{cx}" y="{cy - 205}" width="200" height="410" fill="{sd.RED}" opacity="0.08"/>')
s.append(sd.T(cx - 100, cy + 150, 'upstream:', 21, sd.GREEN, weight=600))
s.append(sd.T(cx - 100, cy + 176, 'µm of Ti-T only', 21, sd.GREEN))
s.append(sd.T(cx + 100, cy + 150, 'downstream:', 21, sd.RED, weight=600))
s.append(sd.T(cx + 100, cy + 176, 'through the backing', 21, sd.RED))
# chamber + beam
s.append(f'<rect x="{cx - 330}" y="{cy - 25}" width="660" height="50" fill="none" stroke="{sd.GREY}" stroke-width="3" stroke-dasharray="10 6"/>')
s.append(sd.arrow(40, cy, cx - 8, cy, sd.BLUE, 4))
s.append(sd.T(110, cy + 40, 'p, 0.9 MeV, ~1 µA', 22, sd.BLUE))
s.append(f'<rect x="{cx - 3}" y="{cy - 22}" width="4" height="44" fill="{sd.RED}"/>')
s.append(f'<rect x="{cx + 1}" y="{cy - 22}" width="8" height="44" fill="{sd.GOLD}"/>')
s.append(sd.T(cx + 12, cy + 58, 'Ti-T + Cu backing', 22, sd.INK, 'start'))
s.append(sd.T(cx - 330, cy - 36, 'CFRP 0.4 mm chamber', 20, sd.GREY, 'start'))
# an X17 pair
import math
for ang, col in ((-125, sd.GREEN), (-10, sd.GREEN)):
    a = math.radians(ang)
    s.append(sd.line(cx, cy, cx + 230 * math.cos(a), cy + 230 * math.sin(a), col, 4))
s.append(sd.T(cx - 170, cy - 92, 'e⁺', 24, sd.GREEN))
s.append(sd.T(cx + 250, cy - 52, 'e⁻', 24, sd.GREEN))
s.append(sd.T(cx + 70, cy - 70, '~112°', 24, sd.GREEN, weight=600))
diag = sd.svg(1000, H, ''.join(s), 'top view: beam, Ti-T target, arms')
side = sd.col(
    sd.flow([dict(label='p + ³H', sub='E_cm = ¾ E_p', color=sd.BLUE),
             dict(label='⁴He*', sub=f'E* = 19.814 + ¾ E_p = {kin.loc[900.0, "Estar_MeV"]:.2f} MeV', color=sd.INK,
                  tip='0⁺ at 20.21 MeV (Γ 0.50) decays only by E0 pairs; 0⁻ at 21.01 (Γ 0.84) has no one-photon decay: ATOMKI puts the X17 there'),
             dict(label='γ / IPC / X17', sub='direct E1 capture to the ground state', color=sd.GREEN)], size=22),
    sd.p(f'The X17 edge is at {kin.loc[900.0, "theta_min_deg_m16.94"]:.0f}°: between {term("adjacent", "arms 90° apart")} '
         f'and opposite arms. Half the accepted X17 pairs use each.', 24),
    sd.p('Hover the dotted terms and the data points for numbers and sources.', 22, sd.MUT),
    w=620, gap=28)
D.slide('setup', sd.title('A thick Ti-T target at the arm centre; the backing shadows half the sky',
                          'top view, to scale only roughly: the four n_TOF arms around a Ti-T film on a backing in a thin chamber')
        + sd.row(diag, side, gap=40),
        short='setup',
        notes="""The target is the lab's own kind: Ti tritide, 2.1 mg/cm² of Ti loaded with tritium (T/Ti ≈ 1.5 assumed), on a backing that conducts the heat away. The beam stops in the tritide or the backing.

Coordinates as at n_TOF and LNL: beam along +Y, arms around it. The leptons that reach the arms leave the target near 90° to the beam, so the downstream ones cross the backing at grazing incidence.""")

# --------------------------------------------------------------------------- #
# 3 the options at Demokritos
# --------------------------------------------------------------------------- #
nmax = nopt.x17_per_day_4pi_at_1p5em3.max()
pap = ytab.loc['PAPAP 250 keV, thick Ti-T']
opts = [('³H(p,e⁺e⁻), tandem 1 µA', y9.x17_per_day_1uA_4pi, sd.GREEN, '900 keV, the lab’s Ti-T (2.1 mg/cm² on 1 mm Cu)', 'the case'),
        ('³H(p,e⁺e⁻), PAPAP 100 µA', pap.x17_per_day_Iref_4pi, sd.GREEN, '250 keV; 25 W into Ti-T; licensing open', 'option'),
        ('⁷Li(p,e⁺e⁻), tandem 1 µA', lnl_x17, sd.BLUE, 'the LNL case: Li₂O 300 µg/cm² at 1.10 MeV', 'as LNL'),
        ('³He(n,e⁺e⁻), neutron beams', nmax, sd.RED, '10⁶ n/cm²/s on the 500 bar capsule, 0.35 MeV', 'ruled out')]
bars = sd.hbars([(o[0], o[1], o[2], o[3], o[4]) for o in opts], vmax=2e4, vmin=0.1, log=True, width=760,
                label_w=480, h=56, size=30, fmt=lambda v: f'{v:,.0f}' if v >= 10 else f'{v:.1f}')
limits = sd.row(
    sd.card(sd.p('<b>Tandem, ³H(p,e⁺e⁻)</b>', 26) + sd.p('needs a Ti-T target on a thin backing; 1 µA demonstrated on Ti-T', 24, sd.MUT)),
    sd.card(sd.p('<b>PAPAP, 250 keV</b>', 26) + sd.p('25 W into Ti-T and no tritium licence yet; E* 0.2 MeV below any ATOMKI point', 24, sd.MUT)),
    sd.card(sd.p('<b>Tandem, ⁷Li(p,e⁺e⁻)</b>', 26) + sd.p('repeats the LNL plan; no tritium, but tests ⁸Be, not ⁴He', 24, sd.MUT)),
    sd.card(sd.p('<b>Neutron beams</b>', 26) + sd.p('10⁵–10⁶ n/cm²/s: the ILL gives ~10¹⁰ absorbed n/s', 24, sd.MUT)), gap=28)
D.slide('options', sd.title('Three proton routes work; the neutron beams are 10⁴× too weak',
                            'X17 produced per day into 4π at ATOMKI’s ratios (⁴He: B_x = 5.1×10⁻⁶; ⁸Be: R = 5.8×10⁻⁶)')
        + bars + limits, short='options',
        notes=f"""Neutron beams: 10⁵–10⁶ n/cm²/s at the sample (no time of flight), ⁷Li(p,n), ³H(p,n), D(d,n), T(d,n). On a 5 cm² beam and the n_TOF capsule (1.35×10²² ³He/cm²) with Viviani's σ_pair = 0.062 µb at 0.35 MeV: {nopt[(nopt.flux_n_cm2_s == 1e6) & (nopt.En_MeV == 0.35) & nopt.cell.str.contains('capsule')].ipc_pairs_per_day_4pi.iloc[0]:.0f} IPC pairs/day, X17/IPC = 1.5×10⁻³.

⁷Li(p,e⁺e⁻)⁸Be at the tandem: identical to the LNL case if the tandem gives ~1 µA at 1.03–1.10 MeV (it measured ⁷Li(p,p′γ) from 1010 keV). See the LNL deck for its reach.

¹¹B(p,e⁺e⁻)¹²C (17.23 MeV, the third ATOMKI anomaly) is also within the tandem's range and not estimated here.

<code>demokritos/out/yields.csv</code>, <code>out/neutron_option.csv</code>.""")

# --------------------------------------------------------------------------- #
# 4 cross sections
# --------------------------------------------------------------------------- #
P = sd.Plot(1060, 640, x=(100, 1200), y=(1e-6, 100, 'log'), xlabel='proton energy, lab [keV]', ylabel='σ [µb]')
P.xticks([(v, f'{v}') for v in (200, 400, 600, 800, 1000, 1200)]).yticks(sd.log_ticks(-6, 2))
P.band([750, 1200], [1e-6, 1e-6], [100, 100], sd.GREY, 0.08, tip='S-factor extrapolated past the 0.1–0.75 MeV fit range')
P.vline(1019, sd.GREY, label='(p,n) opens', tip='³H(p,n)³He threshold 1.019 MeV')
for col_, c, nm in (('sigma_gamma_ub', sd.INK, 'σ(p,γ₀)'), ('sigma_ipc_E1_ub', C['ipc'], 'E1 IPC'),
                    ('sigma_E0_pairs_ub', C['e0'], 'E0 pairs'), ):
    sub = ex.iloc[::5]
    P.line(sub.Ep_keV, sub[col_], c, markers=True, r=4,
           tips=[f'{nm}: {v:.3g} µb at {e:.0f} keV' for e, v in zip(sub.Ep_keV, sub[col_])])
sub = ex.iloc[::5]
P.line(sub.Ep_keV, sub.sigma_gamma_ub * BX, C['x17'], markers=True, r=4,
       tips=[f'X17 at B_x: {v * BX:.2g} µb' for v in sub.sigma_gamma_ub])
P.points([900], [16.8], sd.RED, r=9, tips=['ATOMKI: "about 2 µb/sr at 900 keV" × 8π/3 = 17 µb (E1 at 90°)'])
P.text(330, 20, 'σ(p,γ₀)', 24, sd.INK, weight=600)
P.text(330, 0.3, 'E1 IPC (Born α = 4.6×10⁻³)', 24, C['ipc'], weight=600)
P.text(330, 4e-4, 'X17 at B_x(ATOMKI)', 24, C['x17'], weight=600)
P.text(330, 7e-6, 'E0 pairs (0⁺, 20.21 MeV)', 24, C['e0'], weight=600)
D.slide('xs', sd.title('A smooth E1 capture; the E0 pairs are 4×10⁻⁴ of the IPC',
                       'σ(p,γ₀) from the Hahn 1995 S-factor fit, its IPC, the X17 at ATOMKI’s B_x, and E0 pairs through the 0⁺ resonance')
        + sd.row(P.svg('cross sections'),
                 sd.col(sd.legend([('σ(p,γ₀), Hahn fit', sd.INK), ('E1 IPC', C['ipc']), ('E0 pairs', C['e0']),
                                   ('X17 at B_x', C['x17']), ('ATOMKI 900 keV', sd.RED, 'dot')], 22),
                        sd.p(f'{fd(float(ex.set_index("Ep_keV").loc[900.0].sigma_gamma_ub))} µb at 900 keV, within ~30 % of ATOMKI’s own number.', 24),
                        w=520, gap=24), gap=40),
        short='cross sections',
        notes="""S(E) = 1.30×10⁻⁶ MeV b (1 + 25E + 38.8E²), E_cm in MeV, the fit to Hahn et al. PRC 51, 1624 (1995) in arXiv:physics/9910011. Valid 0.1–0.75 MeV; extrapolated above.

E1 IPC: the Born multipole of nTof_x17 <code>ipc_born</code>. Viviani et al.'s ab initio n + ³He σ_pair/σ_γ is ~2.1×10⁻³ at 0.2–1 MeV, so the true p + t IPC may be ~2× lower.

E0: single-level Breit–Wigner for the 0⁺ (Γ = 0.50 MeV, Γ_p = Γ), Γ_ee = 4.7×10⁻⁶ eV from M(E0) = 1.53 fm². An order-of-magnitude stand-in: p + t feeds the 0⁺ with ~2 b, against 5333 b for thermal n + ³He.""")

# --------------------------------------------------------------------------- #
# 5 acceptance spectra
# --------------------------------------------------------------------------- #
P = sd.Plot(1060, 640, x=(0, 180), y=(1e-4, 0.3, 'log'), xlabel='measured opening angle [deg] (σ = 5.1°)',
            ylabel='fraction of accepted pairs / 5°')
P.xticks([(v, f'{v}') for v in range(0, 181, 30)]).yticks(sd.log_ticks(-4, -1))
for bk, z0, dash in (('none (ideal)', 0.0, None), (THICK, 120.0, '10 7')):
    g = acch[(acch.backing == bk) & (acch.z0_mm == z0)]
    x = (g.theta_lo_deg + 2.5).tolist()
    for k, c in (('X17', C['x17']), ('IPC E1', C['ipc'])):
        yv = (g[k] / g[k].sum()).clip(lower=1e-4).tolist()
        P.line(x, yv, c, dash=dash, markers=False,
               tip=f'{k}, {"no backing" if dash is None else "Cu 1 mm, target +12 cm"}')
P.vline(kin.loc[900.0, 'theta_min_deg_m16.94'], sd.GREEN, label='θ_min, m = 16.94')
P.text(10, 0.15, 'S/B in 105–160°: ~1 % (⁸Be at LNL: ~7 %)', 26, sd.INK, weight=600)
D.slide('acceptance', sd.title('The ⁴He edge sits on a flat, high E1 continuum: S/B is ~1 %',
                               'toy: two different arms, KE > 1 MeV; solid = no backing, dashed = Cu 1 mm with the target 12 cm downstream')
        + sd.row(P.svg('accepted opening angle'),
                 sd.col(sd.legend([('X17, m = 16.94', C['x17']), ('E1 IPC', C['ipc']), ('no backing', sd.INK),
                                   ('Cu 1 mm, +12 cm', sd.INK, 'dash')], 22),
                        sd.p(f'Two-arm acceptance: {r_id.acc_2arm_x17:.0%} of X17 pairs, {r_id.acc_2arm_ipc:.0%} of IPC pairs.', 24),
                        w=520, gap=24), gap=40),
        short='acceptance',
        notes=f"""The toy is lnl_rates' four-arm model (faces at 204 mm, 399.4 × 359.9 mm active) with the backing as a shadow or a Highland scatterer. X17 pairs are isotropic; the γ* direction is isotropic (Geant4 adds the sin²θ of E1 capture).

S/B in the best counting window ({r_id.window}°) is {r_id.SoverB:.2%}. At LNL the ⁸Be edge is at ~137°, where the M1 IPC is lower, so S/B ≈ 7 %.

<code>demokritos/out/acceptance_hist.csv</code>, <code>out/arm_pairs.csv</code>.""")

# --------------------------------------------------------------------------- #
# 6 backing (toy)
# --------------------------------------------------------------------------- #
cfgs = [('none (ideal)', 0.0, 'no backing (ideal)'), ('Al 25 um', 0.0, 'Al 25 µm'), ('Cu 50 um', 0.0, 'Cu 50 µm'),
        ('Cu 100 um', 0.0, 'Cu 100 µm'), ('Cu 1 mm, scatters downstream', 0.0, 'Cu 1 mm, scattering'),
        (THICK, 0.0, 'Cu 1 mm, blocking'), (THICK, 120.0, 'Cu 1 mm, blocking, +12 cm')]
rows = []
for bk, z0, lab in cfgs:
    r = rr(bk, z0)
    rows.append([lab, f'{r.acc_2arm_x17:.0%}', f'{r.x17_sel_per_day_as_built:.0f}', f'<b>{fd(r.days_3sigma_as_built)}</b>',
                 f'{r.x17_sel_per_day_big_plastics:.0f}', f'<b>{fd(r.days_3sigma_big_plastics)}</b>'])
hrow = heat[(heat.I_uA == 3)].set_index('backing')
D.slide('backing', sd.title(f'Against no backing: Cu 50 µm costs ×{r50.days_3sigma_as_built / r_id.days_3sigma_as_built:.1f}, the existing 1 mm Cu ×{r_thk.days_3sigma_as_built / r_id.days_3sigma_as_built:.1f}',
                            'days to 3σ at B_x(ATOMKI), 1 µA, 900 keV; the toy calibrated on the LNL Geant4 result')
        + sd.table(['backing', 'X17 two-arm acc.', 'as built: X17/day', 'as built: days', 'big plastics: X17/day', 'big plastics: days'],
                   rows, size=28)
        + sd.callout(f'Heat: 3 µA on Cu 50 µm warms the spot by {hrow.loc["Cu 50 um"].dT_K:.0f} K (rim-cooled), '
                     f'on Cu 100 µm by {hrow.loc["Cu 100 um"].dT_K:.0f} K.', sd.GOLD, 26),
        short='backing', foot='demokritos/out/reach.csv, heat.csv. "blocking": every downstream lepton is lost; "scattering": Highland only, no EPC.',
        notes=f"""Calibration: ε after the two-arm geometry = LNL Geant4 selected X17/day ÷ the toy's LNL two-arm acceptance ({cal['as built']['eps_after_2arm']:.3f} as built, {cal['big plastics']['eps_after_2arm']:.3f} big plastics). Days = k × toy counting days, k = {cal['as built']['k_days']:.1f} / {cal['big plastics']['k_days']:.2f} from the LNL reference (17 d / 1.0 d).

Heat: ΔT = P ln(R/r)/(2π k t), spot r = 2.5 mm, rim R = 12.5 mm. Ti-T loses tritium when hot; ATOMKI cooled to LN₂ temperature.""")

# --------------------------------------------------------------------------- #
# 7-8 Geant4
# --------------------------------------------------------------------------- #
if GEANT:
    panels = []
    for cfg, lab in (('cu50', 'Cu 50 µm'), ('cu1000_y120', 'Cu 1 mm, target +12 cm')):
        g = GT[(GT.config == cfg) & (GT.hw == 'big plastics')]
        if g.empty:
            g = GT[(GT.config == cfg) & (GT.hw == 'as built')]
        if g.empty:
            continue
        hw = g.hw.iloc[0]
        P = sd.Plot(810, 560, x=(60, 180), y=(1e-1, 1e5, 'log'), xlabel='reconstructed opening angle [deg]',
                    ylabel='pairs per day per 2°', title=f'{lab}, {hw}, E_sum {g.ecut.iloc[0]} MeV')
        P.xticks([(v, f'{v}') for v in range(60, 181, 20)]).yticks(sd.log_ticks(-1, 5))
        for k, c, nm in (('ipc', C['ipc'], 'E1 IPC'), ('epc', C['epc'], 'EPC'), ('cos', C['cos'], 'cosmics'),
                         ('x17', C['x17'], 'X17')):
            gg = g[g.comp == k]
            P.line(gg.theta.tolist(), gg.per_day.clip(lower=0.1).tolist(), c, markers=False,
                   tip=f'{nm}: {gg.per_day.sum():.3g} per day in 60–180° (0 drawn at the floor)')
        panels.append(P.svg(lab))
    D.slide('geant-theta', sd.title('Geant4: the X17 edge on the IPC, with EPC and cosmics below it',
                                    'per day at 1 µA, MM 15° + TOF, LNL-calibrated calorimetry, the best E_sum window')
            + sd.legend([('X17 at B_x', C['x17']), ('E1 IPC', C['ipc']), ('EPC (20.5 MeV γ)', C['epc']), ('cosmics', C['cos'])], 24)
            + sd.row(*panels, gap=44), short='Geant4 spectra',
            notes="""Geant4 of the full apparatus (MX17_Full_Geant branch <code>demokritos</code>, commit 4bad297): D1 X17 m = 16.94 at W = 20.49 MeV, D2 Born E1 IPC generated above 70° (scaled by the Born fraction), D3 the 20.49 MeV γ line from the spot (EPC), LNL L4 cosmics (1.00 live day). The opening angle is the chord from the target position to the MM charge centroids. The γ* anisotropy of E1 capture (1 + 0.1 P₁ − 0.9 P₂, a stand-in) weights the IPC.

<code>demokritos/sim/demok_geant.py</code> → <code>out/geant/</code>.""")

    rows = []
    for cfg, lab in (('cu50', 'Cu 50 µm'), ('cu1000', 'Cu 1 mm'), ('cu1000_y120', 'Cu 1 mm, +12 cm')):
        cells = [lab]
        for hw in ('as built', 'big plastics'):
            r = gr(cfg, hw)
            a = GA[(GA.config == cfg) & (GA.hw == hw) & (GA['sample'] == 'x17')]
            if r is None or a.empty:
                cells += ['—', '—', '—']
                continue
            cells += [f'{a.pair_tag.iloc[0]:.1%}', f'{r.S_tot:.0f}', f'<b>{fd(r.days_fit_theta_y)}</b> ({fd(r.days)})']
        rows.append(cells)
    D.slide('geant-reach', sd.title('Geant4: the existing 1 mm Cu target, moved 12 cm downstream, is as good as a thin one',
                                    'days to 3σ at B_x(ATOMKI), 1 µA: θ × |y| template fit (θ ≥ 80°) with the IPC and EPC norms free, statistics only; counting in the best window in brackets')
            + sd.table(['target', 'as built: pair-tag', 'X17/day sel.', 'days', 'big plastics: pair-tag', 'X17/day sel.', 'days'],
                       rows, size=28)
            + sd.callout('Statistics only. At S/B ≈ 1 % a 1–2 % error in the IPC shape is as large as the signal: '
                         'the 3D fit and its pseudo-data test (LNL §14–17) must be redone for ⁴He.', sd.RED, 26),
            short='Geant4 reach', foot='demokritos/out/geant/reach_scan.csv, acceptance_geant.csv',
            notes='The toy (LNL-calibrated) said 39 d / 2.3 d for Cu 50 µm and 81 d / 4.7 d for Cu 1 mm at +12 cm; Geant4 confirms the first within ×1.2–1.5 and finds the second ×2.3 better: with the target downstream 97 % of the selected pairs have both legs upstream, and the as-built trigger stack covers the upstream faces better. A θ-only fit is ×3 slower: the |y| asymmetry of the E1 IPC is what separates it from X17. EPC is 1–15 % of the background in the window (D3 has only 30–190 selected MC events; one event ≈ 40 pairs/day). ESTIMATES.md §6. Pair-tag: fraction of generated X17 pairs with two arms that each have a trigger leg (SiPM AND plastic) and an MM segment in the active area. X17/day sel.: after MM 15° + TOF and the E_sum window, at B_x(ATOMKI). The E_sum window is chosen per row to minimise the fit days (a mild look-elsewhere bias).')
else:
    D.slide('geant-pending', sd.title('Geant4: pending', 'D1–D3 submitted 2026-10-19 (164 jobs); this slide fills when demok_geant.py has run')
            + sd.p('MX17_Full_Geant branch demokritos: TiT film, --target-y; Cu 50 µm, Cu 1 mm, Cu 1 mm at +12 cm; as built and big plastics.', 28),
            short='Geant4')

# --------------------------------------------------------------------------- #
# 9 the ATOMKI IPC puzzle
# --------------------------------------------------------------------------- #
f_ip = r50.ipc_scale_atomki
rows = [('B_x per γ, QED (Born) IPC: our baseline', r50.days_3sigma_big_plastics, sd.PURPLE,
         f'as built {fd(r50.days_3sigma_as_built)} d'),
        ('… if ATOMKI’s fitted IPC is right', r50.days_3sigma_big_plastics_atomki_ipcc, sd.GREEN,
         f'as built {fd(r50.days_3sigma_as_built_atomki_ipcc)} d')]
D.slide('puzzle', sd.title(f'ATOMKI fit an IPC {1 / f_ip:.0f}× below QED; MX17 measures it on day one',
                           'days to 3σ with big plastics, Cu 50 µm, 1 µA, under the two normalisations')
        + sd.hbars([(a, b, c, None, d) for a, b, c, d in rows], vmax=5, width=700, label_w=560, h=56, size=30,
                   fmt=lambda v: f'{v * 24:.1f} h' if v < 1 else f'{v:.1f} d')
        + sd.p('<b>X17 excess ÷ IPC</b> at the edge (110–120°):', 28)
        + sd.hbars([('ATOMKI 900 keV, measured', 10.0, sd.RED, 'Fig. 4 of PRC 104, 044003: ~70 vs ~5 counts per 5° (read off the figure)'),
                    ('QED, B_x per γ', 0.01, sd.BLUE, 'X17 at B_x(ATOMKI) / Born E1 IPC in a 10° bin above the edge')],
                   vmax=30, vmin=1e-3, log=True, width=700, label_w=560, h=56, size=30, fmt=lambda v: f'{v:g}')
        + sd.callout('MX17 sees the IPC from 40° to 180° with a known acceptance: it measures IPC/γ directly, X17 or not.', sd.GREEN, 26),
        short='IPC puzzle',
        notes="""ATOMKI's Table I: IPCC = 2.5(3), 1.0(7), 1.1(11) ×10⁻⁴ at 510, 610, 900 keV, B_x = 6.2, 4.1, 6.5 ×10⁻⁶. The Born E1 IPC coefficient at 20.5 MeV is 4.6×10⁻³ (Rose-type values are 3–5×10⁻³). Either their IPCC is a gated quantity and not IPC per γ, or the IPC in their gate is suppressed far beyond what any multipolarity allows.

Their X17 count is consistent with B_x per γ: ~10⁴ X17 produced in 100 h at 1 µA, ~300 seen at a few % acceptance. So the open question is the IPC, not the X17.

The upside row scales every background by IPCC/α_E1 at 900 keV (×1/42). It is an upper bound on how fast this could go, not a prediction.""")

# --------------------------------------------------------------------------- #
# 10 the facility
# --------------------------------------------------------------------------- #
fac = [['machine', '5.5 MV HVEC T11/25 tandem, rebuilt 2022 (Pelletron chains, TORVIS 100 µA H⁻, computer control)'],
       ['protons', '0.8–10 MeV quoted; ⁷Li(p,p′γ) measured from 1010 keV; 0.5–0.6 MeV (ask)'],
       ['current', '0.7–1 µA on the neutron targets before the upgrade; "considerably increased" expected (ask)'],
       ['targets', 'Ti-T, 2.1 mg/cm² on 1 mm Cu, 373 GBq, used for ³H(p,n) and ³H(d,n) neutrons'],
       ['rooms', 'Green and Red target rooms, 17.5 × 17 m, 6.8 m high; borated concrete up to 1.2 m'],
       ['also', 'PAPAP 250 kV p/d, hundreds of µA; 17 MeV cyclotron and 2.5 MV AMS Tandetron being installed'],
       ['access', 'open; proposals any time, PAC twice a year; >1000 h/yr to external users'],
       ['people', 'A. Lagoyannis, M. Axiotis (TAL); R. Vlastou, M. Kokkoris (NTUA, n_TOF collaborators)']]
D.slide('facility', sd.title('The lab already puts protons on tritium', 'NCSR Demokritos Tandem Accelerator Laboratory, from public sources (FACILITY.md)')
        + sd.table(['', ''], [[f'<b>{a}</b>', b] for a, b in fac], size=26, widths=[200, None], align=['left', 'left']),
        short='facility',
        notes="""Sources: Harissopulos et al., EPJ Plus 136, 617 (2021); Lagoyannis et al., HNPS 29, 33 (2023); Vlastou et al. (neutron facility); Avgitas et al., arXiv:2609.07541 (2026 neutron run, Red room, 45° line); Radiation 6, 7 (2026). Text extractions in <code>demokritos/refs/</code>.""")

# --------------------------------------------------------------------------- #
# 11 closing
# --------------------------------------------------------------------------- #
end = (sd.title('What this does not settle yet', None)
       + sd.row(sd.col(sd.p('<b>Open physics</b>', 30, sd.DINK),
                       sd.p('• The IPC shape at S/B ≈ 1 %: redo the 3D fit and pseudo-data test for ⁴He.', 26, sd.DINK),
                       sd.p('• The IPC normalisation: ATOMKI’s fit vs QED (×20–45). Ask Viviani et al. for p + t IPC/γ.', 26, sd.DINK),
                       sd.p('• The γ* anisotropy of E1 capture is a stand-in.', 26, sd.DINK), gap=18),
                sd.col(sd.p('<b>Ask the lab</b>', 30, sd.DINK),
                       sd.p('• Current at 0.9–1.0 MeV after the upgrade; 0.5–0.6 MeV possible?', 26, sd.DINK),
                       sd.p('• Can the existing Ti-T on 1 mm Cu sit 12 cm downstream of the chamber centre (a longer stalk)?', 26, sd.DINK),
                       sd.p('• Which line and room, floor space, PAC dates, night running.', 26, sd.DINK), gap=18), gap=80))
D.slide('end', end, dark=True, short='open questions',
        notes='First contact: A. Lagoyannis (lagoya@inp.demokritos.gr) via the NTUA n_TOF group (Kokkoris, Vlastou). Emails not sent.')

out = D.write(O / 'demokritos-x17-feasibility.html',
              note_meta=dict(title='Demokritos ⁴He feasibility',
                             summary='Could the MX17 apparatus test the ATOMKI ⁴He anomaly, ³H(p,e⁺e⁻)⁴He, on the Demokritos tandem with the lab’s own tritium targets? Rates, backing, Geant4 reach.',
                             tags='x17, demokritos, feasibility', date='2026-10-19'),
              footer='Built by x17_facility_search/demokritos/deck/build_deck.py from demokritos_rates.py and sim/demok_geant.py outputs.')
print(out)
