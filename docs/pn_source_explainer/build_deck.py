"""Explainer slide note: how a proton beam on a light target (⁷Li(p,n), ⁹Be(p,n)) makes neutrons, and why
lithium beats beryllium for the X17 search.  No new physics: it reads the outputs of the dedicated
studies (birmingham/, franz/, bepn_cyclotron/, lansce_wnr/, survey/soft_sim/) and draws them for a
newcomer.  Writes docs/pn_source_explainer/out/pn-neutron-sources-explained.html:

    ~/PycharmProjects/nTof_x17/.venv/bin/python docs/pn_source_explainer/build_deck.py
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py \\
        docs/pn_source_explainer/out/pn-neutron-sources-explained.html --slug pn-neutron-sources-explained --force --deploy
"""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'survey' / 'soft_sim'))
import deck_common as C  # noqa: E402
from deck_common import sd, sci  # noqa: E402

OUT = HERE / 'out'
LI, BE, OTH = sd.GREEN, sd.ORANGE, sd.GREY        # one colour per source type, on every slide
PCOL, NCOL = sd.RED, sd.BLUE                      # protons, neutrons in the nucleus cartoons
WIN = 2.75                                        # MeV: the studies' ATOMKI window (E* ≤ 22 MeV)

# --------------------------------------------------------------------------- #
# numbers, all from the studies' outputs
# --------------------------------------------------------------------------- #
d = C.load()
bepn_reach = pd.read_csv(ROOT / 'bepn_cyclotron/out/bepn_reach.csv')
bepn_comp = pd.read_csv(ROOT / 'bepn_cyclotron/out/bepn_components.csv')
franz_reach = pd.read_csv(ROOT / 'franz/out/franz_reach.csv')
wnr_reach = pd.read_csv(ROOT / 'lansce_wnr/out/wnr_reach.csv')


def r_soft(key, col='rho3'):
    return C.R(d, key, col=col)


def r_bepn(key, col='rho3'):
    q = bepn_reach[(bepn_reach.key == key) & (bepn_reach.hw == C.HW) & (bepn_reach.days == 50)
                   & (bepn_reach.signal == 'E* ≤ 22 MeV')]
    return float(q[col].iloc[0])


def r_franz(col='rho3'):
    q = franz_reach[(franz_reach.key == 'franz_2000_thin_pb0') & (franz_reach.scen == 'design')
                    & (franz_reach.dist_m == 0.5) & (franz_reach.hw == C.HW) & (franz_reach.days == 50)]
    return float(q[col].iloc[0])


def r_wnr(key='90L_10m'):
    q = wnr_reach[(wnr_reach.key == key) & (wnr_reach.gate == '0.2-2.75') & (wnr_reach.hw == C.HW)
                  & (wnr_reach.days == 50) & (wnr_reach.signal == 'E* ≤ 22 MeV')]
    return float(q.rho3.iloc[0])


BH, NPI = 'bham_28_2m_pb5', 'npi18_0_2m'
rho = dict(bham=r_soft(BH), franz=r_franz(), medapp=r_soft('medapp_std'), wnr=r_wnr(),
           npi=r_bepn(NPI), kur=r_bepn('kur30_130_2m'), u120=r_bepn('u120_0_3m'))
live = dict(bham=r_soft(BH, 'live'), npi=r_bepn(NPI, 'live'))
thr_npi = r_bepn(NPI, 'throttle')
legs = dict(bham=C.Cp(d, BH, 'legs_per_arm'),
            npi=float(bepn_comp[(bepn_comp.key == NPI) & (bepn_comp.hw == C.HW)].legs_per_arm.iloc[0]))

bham_beam = pd.read_csv(ROOT / 'birmingham/out/bham_beam.csv').set_index('ep')
bepn_beam = pd.read_csv(ROOT / 'bepn_cyclotron/out/bepn_beam.csv')
b18 = bepn_beam[(bepn_beam.key == 'npi18') & (bepn_beam.theta == 0) & (bepn_beam.dist_m == 2)].iloc[0]
n_bham = float(bham_beam.loc[2.8].n_tot)
n_bham_cell = float(bham_beam.loc[2.8].n_cell)

# shield: neutrons that would hit one bare arm vs the ones sent through the cell
sh_b = pd.read_csv(ROOT / 'bepn_cyclotron/out/bepn_shield.csv')
sh_b = sh_b[(sh_b.key == NPI) & (sh_b.tvl_cm == 20)]
sh_l = pd.read_csv(ROOT / 'birmingham/out/bham_shield.csv')
arm_x_be = float(sh_b.n_arm_unshielded.iloc[0]) / float(b18.n_cell)
arm_x_li = float(sh_l.n_arm_unshielded.iloc[0]) / n_bham_cell
wall_be = (sh_b.thickness_cm.min(), sh_b.thickness_cm.max())
wall_li = (sh_l.bpe_cm.min(), sh_l.bpe_cm.max())

# --------------------------------------------------------------------------- #
# spectra (0°), as fraction per unit ln E, each normalised to its own total
# --------------------------------------------------------------------------- #
def per_lnE(E, dYdE):
    E, y = np.asarray(E, float), np.asarray(dYdE, float)
    tot = np.trapezoid(y, E)
    return E, E * y / tot, tot


sb = pd.read_csv(ROOT / 'birmingham/out/bham_spectra.csv')
sf = pd.read_csv(ROOT / 'franz/out/franz_spectra.csv')
se = pd.read_csv(ROOT / 'bepn_cyclotron/out/bepn_spectra.csv')
s_li = sb[sb.E_p == 2.8]
s_fr = sf[sf.E_p == 2.0]
s_be = se[(se.E_p == 18.0) & (se.th_lo == 0)]
E_li, f_li, _ = per_lnE(s_li.E_n, s_li.dYdE_0deg_per_sr_per_mA)
E_fr, f_fr, _ = per_lnE(s_fr.E_n_keV / 1e3, s_fr.dYdE_0deg_per_sr_per_mA_per_keV)
E_be, f_be, _ = per_lnE(s_be.E_n, s_be.dYdEdO_per_uC)


def frac_below(E, dYdE, cut):
    E, y = np.asarray(E, float), np.asarray(dYdE, float)
    m = E <= cut
    return np.trapezoid(y[m], E[m]) / np.trapezoid(y, E)


win_li = frac_below(s_li.E_n, s_li.dYdE_0deg_per_sr_per_mA, WIN)
win_be = frac_below(s_be.E_n, s_be.dYdEdO_per_uC, WIN)
mean_be = float(np.trapezoid(s_be.E_n * s_be.dYdEdO_per_uC, s_be.E_n) / np.trapezoid(s_be.dYdEdO_per_uC, s_be.E_n))
mean_li = float(bham_beam.loc[2.8].mean_En0)

# --------------------------------------------------------------------------- #
# two-body kinematics: neutron energy at 0° to the ground state of the daughter (non-relativistic)
# --------------------------------------------------------------------------- #
U = 931.494
MP, MH, MN = 1.007276, 1.007825, 1.008665           # proton, ¹H atom, neutron (u)
RX = {'li': dict(mt=7.016003, mr=7.016929, label='⁷Li(p,n)⁷Be'),
      'be': dict(mt=9.012183, mr=9.013330, label='⁹Be(p,n)⁹B')}
for k, r in RX.items():
    r["Q"] = (MH + r["mt"] - MN - r["mr"]) * U       # atomic masses: the electrons cancel
    r['thr'] = -r['Q'] * (MP + r['mt']) / r['mt']


def En0(ep, r):
    a = math.sqrt(MP * MN * ep)
    disc = MP * MN * ep + (r['mr'] + MN) * (r['mr'] * r['Q'] + (r['mr'] - MP) * ep)
    if disc < 0:
        return float('nan')
    return ((a + math.sqrt(disc)) / (r['mr'] + MN)) ** 2


Q_li, Q_be = -RX['li']['Q'], -RX['be']['Q']
T_li, T_be = RX['li']['thr'], RX['be']['thr']

D = sd.Deck('Proton-beam neutron sources, explained',
            'How a proton beam on lithium or beryllium makes neutrons, and why lithium sources lead the X17 '
            'facility ranking: a picture-first introduction for newcomers.')

# --------------------------------------------------------------------------- #
# 1. cover
# --------------------------------------------------------------------------- #
cover = (sd.kicker('Accelerator neutron sources for X17 · an introduction · 21 Oct 2026')
         + '<h1 style="font-size:64px;font-weight:600;line-height:1.08;letter-spacing:-1.5px">'
           'Fire protons at a light metal and it gives off neutrons. Lithium gives slow ones, which is what '
           'X17 needs. Beryllium gives mostly fast ones.</h1>'
         + sd.p('The principle behind Birmingham and FRANZ (lithium) and NPI Řež (beryllium), the (p,n) '
                'sources studied for MX17, and why the lithium ones come out ahead.', 30, sd.DMUT)
         + sd.row(
             sd.bignum(f'{T_li:.2f} MeV', 'the proton energy at which lithium starts giving neutrons', sd.DGREEN,
                       f'beryllium: {T_be:.2f} MeV',
                       tip=f'threshold = −Q × (m_p + m_target)/m_target; Q = −{Q_li:.3f} MeV (Li), −{Q_be:.3f} MeV (Be)'),
             sd.bignum(sci(n_bham, 1).replace('×', ' × '), 'neutrons per second from Birmingham’s lithium',
                       sd.DGREEN, '2.8 MeV protons, 30 mA',
                       tip='birmingham/out/bham_beam.csv: thick-target ⁷Li(p,n) model normalised to the facility’s 3×10¹³ n/s at 2.6 MeV'),
             sd.bignum(f'{100 * win_be:.0f} %', 'of beryllium’s neutrons are slow enough to use', sd.DRED,
                       f'lithium: {100 * win_li:.0f} %',
                       tip=f'fraction below {WIN} MeV at 0°: NPI Řež 18 MeV thick Be (ENDF/B-VIII.0 model) vs Birmingham 2.8 MeV thick Li'),
             gap=56))
D.slide('cover', cover, dark=True, short='cover',
        notes=f"""This is a primer, not a new study. Every number comes from the dedicated feasibility studies in this repo
(<code>birmingham/</code>, <code>franz/</code>, <code>bepn_cyclotron/</code>, <code>lansce_wnr/</code>,
<code>frm2_medapp/</code>), whose slide notes are live on the site.

A correction to a common reading of the ranking: the sites at the top (Birmingham HF-ADNeF, FRANZ) use
<b>lithium</b>, ⁷Li(p,n). The beryllium sources, ⁹Be(p,n) at NPI Řež and the Japanese BNCT cyclotrons, pass
ATOMKI too but sit ×{rho['npi'] / rho['bham']:.1f} behind. Both work the same way, which is what the next slides
explain, and the last slides show why the difference matters.""")

# --------------------------------------------------------------------------- #
# 2. what the neutrons are for
# --------------------------------------------------------------------------- #
def nucleus(cx, cy, z, n, r=15, tip=None, order=None):
    """a cluster of z protons and n neutrons in a hexagonal packing."""
    offs = [(0, 0), (1, 0), (0.5, 0.87), (-0.5, 0.87), (-1, 0), (-0.5, -0.87), (0.5, -0.87),
            (1.5, 0.87), (0, 1.73), (-1.5, 0.87)]
    kinds = order or (['p', 'n'] * 10)
    seq, np_, nn_ = [], 0, 0
    for k in kinds:
        if k == 'p' and np_ < z:
            seq.append('p'); np_ += 1
        elif k == 'n' and nn_ < n:
            seq.append('n'); nn_ += 1
        if len(seq) == z + n:
            break
    while np_ < z:
        seq.append('p'); np_ += 1
    while nn_ < n:
        seq.append('n'); nn_ += 1
    k = z + n
    mx = sum(o[0] for o in offs[:k]) / k
    my = sum(o[1] for o in offs[:k]) / k
    o = [f'<g{sd.tipattr(tip)}>']
    for (ox, oy), t in zip(offs[:k], seq):
        c = PCOL if t == 'p' else NCOL
        o.append(f'<circle cx="{cx + (ox - mx) * 2 * r * 0.95:.1f}" cy="{cy + (oy - my) * 2 * r * 0.95:.1f}" r="{r}" '
                 f'fill="{c}" stroke="#fff" stroke-width="2"/>')
    o.append('</g>')
    return ''.join(o)


def particle(cx, cy, kind, r=15, tip=None):
    c = {'n': NCOL, 'p': PCOL}.get(kind, sd.GOLD)
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}" stroke="#fff" stroke-width="2"{sd.tipattr(tip)}/>'
            + sd.T(cx, cy + 7, kind, 19, '#fff', weight=600))


def lepton(x0, y0, ang, L, color, lab):
    x1, y1 = x0 + L * math.cos(math.radians(ang)), y0 - L * math.sin(math.radians(ang))
    return sd.arrow(x0, y0, x1, y1, color, 4, 16) + sd.T(x1 + 14 * math.cos(math.radians(ang)), y1 - 14 * math.sin(math.radians(ang)) + 7, lab, 24, color, 'middle', 600)


g = []
y = 250
g.append(particle(80, y, 'n', 18, 'a neutron from the source'))
g.append(sd.arrow(105, y, 250, y, NCOL, 5, 16))
g.append(sd.T(175, y - 22, 'neutron', 22, NCOL, weight=600))
g.append(nucleus(310, y, 2, 1, 18, '³He: 2 protons + 1 neutron, the gas in the MX17 cell'))
g.append(sd.T(310, y + 80, '³He in the cell', 22, sd.INK, weight=600))
g.append(sd.arrow(380, y, 520, y, sd.MUT, 4, 16))
g.append(sd.T(450, y - 22, 'captured', 22, sd.MUT))
g.append(f'<circle cx="610" cy="{y}" r="74" fill="{sd.GOLD}" fill-opacity="0.18"/>')
g.append(nucleus(610, y, 2, 2, 18, '⁴He*: an excited helium-4 nucleus. Its energy is 20.6 MeV (the neutron’s binding) plus about ¾ of the neutron’s kinetic energy.'))
g.append(sd.T(610, y + 104, '⁴He*, excited helium', 22, sd.INK, weight=600))
g.append(sd.T(610, y + 132, '20.6 MeV + ¾ × neutron energy', 21, sd.MUT))
# the two ways out
bx = 760
g.append(sd.T(bx + 30, 70, 'it sheds its energy as an electron–positron pair:', 24, sd.INK, 'start', 600))
g.append(f'<rect x="{bx + 20}" y="96" width="820" height="150" rx="14" fill="{sd.CARD}" stroke="{sd.RULE}"/>')
g.append(sd.T(bx + 50, 136, 'usually: directly (“IPC”)', 24, sd.INK, 'start', 600,
              tip='internal pair creation: the nucleus makes an e⁺e⁻ pair through a virtual photon; ~3.5×10⁻³ pairs per γ at 20.6 MeV'))
g.append(sd.T(bx + 50, 168, 'any opening angle, mostly small', 22, sd.MUT, 'start'))
g.append(lepton(bx + 560, 210, 18, 200, sd.RED, 'e⁺'))
g.append(lepton(bx + 560, 210, -2, 200, sd.BLUE, 'e⁻'))
g.append(f'<circle cx="{bx + 560}" cy="210" r="8" fill="{sd.GOLD}"/>')
g.append(f'<rect x="{bx + 20}" y="272" width="820" height="200" rx="14" fill="{sd.CARD}" stroke="{sd.PURPLE}" stroke-width="2.5"/>')
g.append(sd.T(bx + 50, 312, 'the hope: through an X17 particle', 24, sd.PURPLE, 'start', 600,
              tip='ATOMKI reported an excess of wide-angle pairs from ⁸Be and ⁴He, read as a 16.8 MeV boson; MX17 tests the ⁴He claim'))
g.append(sd.T(bx + 50, 344, 'a bump at a large opening angle', 22, sd.MUT, 'start'))
g.append(f'<circle cx="{bx + 470}" cy="410" r="8" fill="{sd.GOLD}"/>')
g.append(sd.arrow(bx + 478, 410, bx + 580, 410, sd.PURPLE, 4, 14))
g.append(sd.T(bx + 530, 398, 'X17', 22, sd.PURPLE, weight=600))
g.append(f'<circle cx="{bx + 590}" cy="410" r="6" fill="{sd.PURPLE}"/>')
g.append(lepton(bx + 590, 410, 65, 110, sd.RED, 'e⁺'))
g.append(lepton(bx + 590, 410, -30, 70, sd.BLUE, 'e⁻'))
diagram = sd.svg(1664, 490, ''.join(g), 'neutron capture on ³He and the two ways the excited ⁴He makes a pair')

# energy strip: where a neutron must sit
P = sd.Plot(1664, 210, x=(0.01, 30, 'log'), y=(0, 1), xlabel='neutron energy (MeV)',
            margin=(10, 30, 96, 30))
P.xticks([(0.01, '0.01'), (0.1, '0.1'), (1, '1'), (2.75, '2.75'), (10, '10'), (30, '30')])
P.band([0.01, WIN], [0, 0], [1, 1], LI, 0.22, tip=f'below {WIN} MeV: the helium is formed close to the energy ATOMKI studied; the feasibility studies count X17 only from these neutrons')
P.band([WIN, 30], [0, 0], [1, 1], sd.RED, 0.10, tip='above: the excited helium sits higher than the ATOMKI state; these neutrons bring background and no counted signal')
P.text(0.03, 0.42, 'useful: “slow” (below 2.75 MeV)', 26, LI, weight=600)
P.text(4.0, 0.42, 'too fast: background only', 26, sd.RED, weight=600)
D.slide('why', sd.title('The neutron’s only job: be captured by ³He, slowly',
                        'what happens in the MX17 cell; hover the dotted words, points and shapes for details throughout')
        + diagram + P.svg('neutron energy window'),
        short='why neutrons',
        notes=f"""MX17 fills a cell with ³He gas and sends neutrons through it. A captured neutron turns ³He into an
excited ⁴He nucleus, ⁴He*. That nucleus gets rid of its energy, sometimes by emitting an electron–positron pair.
The ordinary way (internal pair creation, IPC) gives pairs at all opening angles. If the X17 boson exists, some
pairs come from X17 → e⁺e⁻ instead, and they all have a large opening angle: a bump on a smooth curve. The four
MX17 arms measure the angle.

The neutron's energy matters because about ¾ of it goes into the helium (E* = 20.58 MeV + 0.75·E_n). ATOMKI
saw its signal for helium formed at about 20–21 MeV, so the studies count X17 only from neutrons below
{WIN} MeV. Faster neutrons still make pairs, but at a different helium energy, so they count only as background.
They also cause trouble in the detector (slide 7).

That's why a neutron source for X17 should give as many slow neutrons as possible and few fast ones.""")

# --------------------------------------------------------------------------- #
# 3. the principle: a proton goes in, a neutron comes out
# --------------------------------------------------------------------------- #
g = []
y = 230
g.append(f'<rect x="0" y="{y - 90}" width="330" height="180" rx="18" fill="#e7eef7" stroke="{sd.BLUE}" stroke-width="2.5"'
         f'{sd.tipattr("an electrostatic accelerator (Birmingham: Dynamitron, FRANZ: RFQ) or a cyclotron (NPI Řež TR-24) gives protons a few to tens of MeV")}/>')
g.append(sd.T(165, y - 20, 'accelerator', 30, sd.BLUE, weight=600))
g.append(sd.T(165, y + 18, 'speeds protons up', 22, sd.MUT))
g.append(sd.T(165, y + 46, 'to a few MeV', 22, sd.MUT))
g.append(sd.arrow(335, y, 520, y, PCOL, 6, 18))
g.append(particle(430, y, 'p', 18, 'a proton'))
g.append(sd.T(430, y - 36, 'proton', 22, PCOL, weight=600))
# target nucleus
g.append(f'<rect x="530" y="{y - 150}" width="60" height="300" rx="6" fill="#d9d4ca" stroke="{sd.MUT}" stroke-width="2"'
         f'{sd.tipattr("the target: a thin layer of lithium metal or a beryllium disk, water-cooled (kW of beam power)")}/>')
g.append(sd.T(560, y + 186, 'target', 24, sd.INK, weight=600))
g.append(nucleus(700, y, 3, 4, 20, '⁷Li: 3 protons + 4 neutrons'))
g.append(sd.T(700, y + 90, '⁷Li nucleus', 24, sd.INK, weight=600))
g.append(sd.T(700, y + 120, '3 p + 4 n', 22, sd.MUT))
g.append(sd.arrow(790, y, 960, y, sd.MUT, 5, 18))
g.append(sd.T(875, y - 50, 'the proton', 22, sd.INK, weight=600))
g.append(sd.T(875, y - 22, 'swaps in', 22, sd.INK, weight=600))
g.append(sd.T(875, y + 40, f'costs {Q_li:.2f} MeV', 22, sd.RED,
              tip=f'Q = −{Q_li:.3f} MeV: ⁷Be + n weigh more than ⁷Li + p, so this much of the proton’s energy is spent on mass'))
g.append(nucleus(1060, y, 4, 3, 20, '⁷Be: 4 protons + 3 neutrons (radioactive, half-life 53 days; it stays in the target)'))
g.append(sd.T(1060, y + 90, '⁷Be stays behind', 24, sd.INK, weight=600))
g.append(sd.T(1060, y + 120, '4 p + 3 n', 22, sd.MUT))
g.append(sd.arrow(1150, y - 20, 1500, y - 110, NCOL, 6, 20))
g.append(particle(1520, y - 115, 'n', 20, 'the free neutron: it carries off the energy the proton had left over'))
g.append(sd.T(1520, y - 160, 'free neutron!', 28, NCOL, weight=600))
g.append(sd.T(1360, y + 6, 'carries the leftover energy', 22, NCOL, 'middle'))
pic = sd.svg(1664, 440, ''.join(g), 'a proton hits a lithium nucleus and knocks out a neutron')


def rxcard(name, col, lines, tip):
    return sd.card(sd.p(f'<b>{name}</b>', 32, col) + ''.join(sd.p(l, 24, sd.MUT) for l in lines), tip=tip)


cards = sd.row(
    rxcard('Lithium: ⁷Li(p,n)⁷Be', LI,
           [f'costs {Q_li:.2f} MeV, starts at {T_li:.2f} MeV', 'Birmingham (2.8 MeV), FRANZ (2.0 MeV)'],
           'the classic low-energy neutron source; also used for BNCT and for keV neutron astrophysics'),
    rxcard('Beryllium: ⁹Be(p,n)⁹B', BE,
           [f'costs {Q_be:.2f} MeV, starts at {T_be:.2f} MeV', 'NPI Řež (18 MeV), Japanese BNCT cyclotrons (30 MeV)'],
           'beryllium is solid and robust, so it takes cyclotron power (kW); its nucleus also breaks up, giving extra neutrons'),
    gap=32)
D.slide('principle', sd.title('A proton swaps into the nucleus and pushes a neutron out',
                              'the reaction behind every source in this deck (lithium shown; beryllium works the same way)')
        + pic + cards, short='the principle',
        notes=f"""A light nucleus hit by a fast enough proton can absorb the proton and release one of its neutrons.
For lithium: p + ⁷Li → n + ⁷Be. One proton in, one neutron out; the nucleus left behind has one more
proton and one fewer neutron.

It isn't free. The products weigh slightly more than what went in, so the proton must bring at least that
mass-energy (the "cost", −Q): {Q_li:.3f} MeV for lithium, {Q_be:.3f} MeV for beryllium. A little more than that
is needed in practice (the threshold, {T_li:.3f} and {T_be:.3f} MeV), because some energy is always tied up in
the motion of the whole system. Below the threshold: no neutrons at all.

Above it, whatever energy the proton has beyond the cost is shared between the neutron and the recoiling
nucleus. The neutron, being much lighter, gets most of it. That one rule sets the whole story: <b>how far above
threshold you run sets how fast the neutrons are.</b>

Other practical points: the target heats up (Birmingham puts ~80 kW on a rotating lithium target), and ⁷Be is
radioactive, so a lithium target gets hot in both senses. Beryllium is a robust metal that takes high power.""")

# --------------------------------------------------------------------------- #
# 4. energy budget: leftover proton energy goes to the neutron
# --------------------------------------------------------------------------- #
P = sd.Plot(1664, 700, x=(1.5, 40, 'log'), y=(0.01, 60, 'log'),
            xlabel='proton energy (MeV)', ylabel='neutron energy, straight ahead (MeV)', margin=(24, 40, 96, 120))
P.xticks([(1.5, '1.5'), (2, '2'), (3, '3'), (5, '5'), (10, '10'), (20, '20'), (30, '30'), (40, '40')])
P.yticks([(0.01, '0.01'), (0.1, '0.1'), (1, '1'), (WIN, '2.75'), (10, '10'), (40, '40')])
P.band([1.5, 40], [0.01, 0.01], [WIN, WIN], LI, 0.13, tip=f'the useful window: below {WIN} MeV')
P.text(28, 1.9, 'useful (slow)', 24, LI, 'end', 600)
for k, col in (('li', LI), ('be', BE)):
    r = RX[k]
    ep = np.geomspace(r['thr'] * 1.00005, 40, 400)
    en = [En0(e, r) for e in ep]
    en = [max(v, 0.0105) for v in en]
    P.line(ep, en, col, 4.5, markers=False, tip=f"{r['label']}: neutron energy at 0° to the ground state of the daughter (two-body kinematics)")
    P.vline(r['thr'], col, '6 6', 2)
ops = [('FRANZ', 2.0, 'li', None, 0, 0), ('Birmingham', 2.8, 'li', 'start', 16, 36),
       ('NPI Řež', 18.0, 'be', 'start', 12, 44), ('KURNS', 30.0, 'be', 'end', -16, -18)]
for name, ep, k, anc, dx, dy in ops:
    v = En0(ep, RX[k])
    col = LI if k == 'li' else BE
    tp = f'{name}: protons at {ep:g} MeV give neutrons up to {v:.2f} MeV straight ahead'
    P.points([ep], [v], col, 11, tips=[tp], marker='open')
    if anc is None:                                  # FRANZ: label off to the right, with a leader line
        P.raw(sd.line(P.X(ep) + 8, P.Y(v) + 8, P.X(2.45) - 6, P.Y(0.05) - 8, col, 2))
        P.text(2.45, 0.045, f'{name}, {ep:g} MeV', 24, col, 'start', 600)
        continue
    P.raw(sd.T(P.X(ep) + dx, P.Y(v) + dy, f'{name}, {ep:g} MeV', 24, col, anc, 600))
P.raw(sd.T(P.X(T_li) - 8, P.Y(0.015), f'Li starts {T_li:.2f}', 21, LI, 'end'))
P.raw(sd.T(P.X(T_be) + 8, P.Y(0.015), f'Be starts {T_be:.2f}', 21, BE, 'start'))
P.text(5.2, 0.08, 'Lithium runs just above its threshold;', 28, sd.INK, weight=600)
P.text(5.2, 0.045, 'beryllium cyclotrons run ×9–15 above it', 28, sd.INK, weight=600)
D.slide('budget', sd.title('Every MeV the proton has beyond the cost goes to the neutron',
                           'fastest neutron energy straight ahead, against proton energy, for the two reactions')
        + sd.legend([('lithium ⁷Li(p,n)', LI), ('beryllium ⁹Be(p,n)', BE), ('studied facility', sd.INK, 'open')])
        + P.svg('neutron energy vs proton energy'),
        short='energy budget',
        notes=f"""The curves are the textbook two-body result: a neutron emitted straight ahead (0°), leaving the
daughter nucleus in its ground state. Each curve starts at the threshold and climbs nearly one-for-one: above
a few MeV, an extra MeV of proton gives about an extra MeV of neutron.

Lithium sources live in the bottom-left corner. FRANZ plans 2.0 MeV protons (neutrons up to
{En0(2.0, RX['li']):.2f} MeV straight ahead), Birmingham runs 2.8 MeV (up to {En0(2.8, RX['li']):.2f} MeV). Every neutron
is in the useful window.

Beryllium sources are cyclotrons that run at 18–30 MeV, because that's what those machines are built for and
where beryllium gives lots of neutrons. Straight-ahead neutrons then reach {En0(18, RX['be']):.0f}–{En0(30, RX['be']):.0f} MeV.
You could run a beryllium target at 3 MeV, but it would give very few neutrons: the reaction is weak near
its threshold, while lithium has a strong resonance right there.

The curve is the maximum. A real target gives a whole spread of energies below it (next slide), and
beryllium also has break-up reactions (⁹Be → 2α + n) that add many neutrons at a few MeV.""")

# --------------------------------------------------------------------------- #
# 5. thick target: the proton slows down, so you get a spread
# --------------------------------------------------------------------------- #
g = []
x0, x1, yc = 60, 640, 300
g.append(f'<rect x="{x0 + 120}" y="{yc - 200}" width="{x1 - x0 - 120}" height="400" rx="8" fill="#e9e5dc" stroke="{sd.MUT}" stroke-width="2"'
         f'{sd.tipattr("a thick lithium layer: thick enough to stop the protons completely")}/>')
g.append(sd.T((x0 + 120 + x1) / 2, yc - 216, 'thick lithium target', 24, sd.INK, weight=600))
g.append(sd.arrow(x0 - 40, yc, x0 + 120, yc, PCOL, 6, 18))
g.append(sd.T(x0 + 30, yc - 22, 'p, 2.8 MeV', 22, PCOL, weight=600))
steps = [(2.8, 0.0), (2.6, 0.27), (2.4, 0.5), (2.2, 0.7), (2.0, 0.86), (T_li, 0.95)]
xs = [x0 + 120 + f * (x1 - x0 - 160) for _, f in steps]
for i in range(len(steps) - 1):
    t = i / (len(steps) - 1)
    g.append(sd.line(xs[i], yc, xs[i + 1], yc, PCOL, 9 - 6 * t, extra=f' stroke-opacity="{1 - 0.6 * t:.2f}" stroke-linecap="round"'))
for (ep, _), x in zip(steps, xs):
    en = En0(ep, RX['li']) if ep > T_li + 1e-3 else 0.03
    L = 40 + 150 * en
    g.append(f'<circle cx="{x:.1f}" cy="{yc}" r="7" fill="{PCOL}"/>')
    g.append(sd.T(x, yc + 40, f'{ep:.1f}', 21, PCOL, tip=f'proton energy here: {ep:.2f} MeV → neutrons up to {En0(ep, RX["li"]):.2f} MeV straight ahead'))
    if ep > T_li + 1e-3:
        g.append(sd.arrow(x, yc - 12, x + 0.55 * L, yc - 12 - 0.83 * L, NCOL, 3.5, 13))
g.append(sd.T(xs[-1] - 4, yc + 80, 'below 1.88:', 21, sd.MUT, 'end'))
g.append(sd.T(xs[-1] - 4, yc + 104, 'no more neutrons', 21, sd.MUT, 'end'))
g.append(sd.T((x0 + x1) / 2 + 60, yc + 170, 'proton energy (MeV) as it slows', 22, PCOL))
g.append(sd.T((x0 + 120 + x1) / 2, yc + 250, 'neutron arrows: longer = faster', 22, NCOL))
left = sd.svg(700, 640, ''.join(g), 'a proton slowing down in a thick target, emitting neutrons at each depth')

P = sd.Plot(900, 600, x=(0, 1.2), y=(0, 1.25), xlabel='neutron energy (MeV)',
            ylabel='neutrons per MeV (straight ahead, scaled)', margin=(24, 30, 96, 104))
P.xticks([(v, f'{v:.1f}') for v in (0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2)])
P.yticks([(0, '0'), (0.5, '0.5'), (1, '1')])
ymax = sb.dYdE_0deg_per_sr_per_mA.max()
shades = {2.3: '#a9d8bd', 2.5: '#6fbd92', 2.6: '#3f9d6b', 2.8: LI}
for ep in (2.3, 2.5, 2.6, 2.8):
    s = sb[sb.E_p == ep]
    y = s.dYdE_0deg_per_sr_per_mA / ymax
    n = float(bham_beam.loc[ep].n_tot)
    P.line(s.E_n, y, shades[ep], 4, markers=False,
           tip=f'protons at {ep} MeV: {sci(n, 1)} n/s in total at 30 mA, fastest {float(bham_beam.loc[ep].max_En0):.2f} MeV')
P.text(0.6, 1.16, 'more beam energy:', 26, sd.INK, weight=600)
P.text(0.6, 1.08, 'more and faster neutrons', 26, sd.INK, weight=600)
D.slide('thick', sd.title('A thick target gives a spread of neutron energies, not one',
                          'left: the proton loses energy as it ploughs in, making neutrons all the way down; '
                          'right: Birmingham’s lithium spectrum for four beam energies')
        + sd.row(left, sd.col(sd.legend([(f'{ep} MeV protons', shades[ep]) for ep in (2.3, 2.5, 2.6, 2.8)], size=22),
                              P.svg('Birmingham spectra vs proton energy'), w=900), gap=64),
        short='thick target',
        notes=f"""High-current sources use a target thick enough to stop the protons. That gives the most neutrons per proton,
but the proton loses energy continuously on the way in. At each depth it can still knock out a neutron, with
the energy it has at that depth, until it falls below the {T_li:.2f} MeV threshold. So the source makes a spread
from about zero up to the maximum of the previous slide.

The right panel is Birmingham's thick-lithium model (<code>birmingham/bham_beam.py</code>, normalised to the
facility's quoted yield). Raising the beam from 2.3 to 2.8 MeV more than doubles the neutron output
({sci(float(bham_beam.loc[2.3].n_tot), 1)} → {sci(n_bham, 1)} n/s) and pushes the end point from
{float(bham_beam.loc[2.3].max_En0):.2f} to {float(bham_beam.loc[2.8].max_En0):.2f} MeV. Still all slow, so the
study picks 2.8 MeV.

The same happens in beryllium, from 18 MeV down to {T_be:.2f} MeV, so its spread runs across 0–16 MeV.""")

# --------------------------------------------------------------------------- #
# 6. the spectra side by side
# --------------------------------------------------------------------------- #
P = sd.Plot(1664, 700, x=(0.005, 25, 'log'), y=(0, 1.15), xlabel='neutron energy (MeV)',
            ylabel='share of neutrons (per log-energy step, scaled)', margin=(24, 40, 96, 110))
P.xticks([(0.01, '0.01'), (0.1, '0.1'), (1, '1'), (WIN, '2.75'), (10, '10'), (25, '25')])
P.yticks([(0, '0'), (0.5, '0.5'), (1, '1')])
P.band([0.005, WIN], [0, 0], [1.15, 1.15], LI, 0.10, tip=f'useful window: below {WIN} MeV')
P.band([WIN, 25], [0, 0], [1.15, 1.15], sd.RED, 0.05, tip='too fast: background only')
for E, f, col, dash, lab in ((E_fr, f_fr, LI, '10 7', 'FRANZ, Li, 2.0 MeV'),
                             (E_li, f_li, LI, None, 'Birmingham, Li, 2.8 MeV'),
                             (E_be, f_be, BE, None, 'NPI Řež, Be, 18 MeV')):
    sc = f.max()
    m = (E >= 0.005) & (E <= 25)
    E, f = E[m], f[m]
    P.line(E, f / sc, col, 4.5, dash=dash, markers=False, tip=lab + ' (0°, thick target; each curve scaled to its own peak)')
P.text(0.0075, 1.06, 'FRANZ', 24, LI, 'start', 600)
P.text(0.35, 1.06, 'Birmingham', 24, LI, 'start', 600)
P.text(11, 0.8, 'NPI Řež (Be)', 24, BE, 'start', 600)
P.text(0.007, 0.55, f'Lithium: {100 * win_li:.0f} % useful', 32, LI, weight=600)
P.text(0.007, 0.45, f'Beryllium: {100 * win_be:.0f} % useful', 32, BE, weight=600)
P.text(3.0, 0.2, f'{100 * (1 - win_be):.0f} % of Be neutrons', 24, sd.RED, weight=600)
P.text(3.0, 0.13, 'land here: no signal,', 24, sd.RED)
P.text(3.0, 0.06, 'only background', 24, sd.RED)
D.slide('spectra', sd.title('Lithium: all neutrons slow. Beryllium: most too fast',
                            'neutron energy spectra straight ahead from the three (p,n) sources studied, each scaled to its peak')
        + sd.legend([('lithium (solid: Birmingham; dashed: FRANZ)', LI), ('beryllium (NPI Řež)', BE),
                     ('useful window', LI, 'box')])
        + P.svg('neutron spectra of lithium and beryllium sources'),
        short='the spectra',
        notes=f"""Each curve is plotted as the share of neutrons per equal step in log-energy, so the area under a curve is
proportional to the number of neutrons, and wildly different energies fit on one axis. Each is scaled to its own
peak: this slide compares shapes, not how many neutrons each machine makes.

<b>FRANZ</b> (dashed) runs close to threshold: its neutrons are tens to a few hundred keV.
<b>Birmingham</b> runs higher: up to {float(bham_beam.loc[2.8].max_En0):.1f} MeV, mean {mean_li:.2f} MeV. Both are entirely
inside the useful window.

<b>NPI Řež</b> at 18 MeV: mean {mean_be:.1f} MeV, and only {100 * win_be:.0f} % below {WIN} MeV. The bumps near 1.5 and
6 MeV are features of the nuclear-data evaluation (ENDF/B-VIII.0, sequential break-up through ⁹B and ⁸Be states);
measured spectra are smoother, which doesn't change the fraction much. The study checked that the fraction is
31–48 % at every angle and beam energy: you can't steer around it.

Sources: <code>birmingham/out/bham_spectra.csv</code>, <code>franz/out/franz_spectra.csv</code>,
<code>bepn_cyclotron/out/bepn_spectra.csv</code> (0–8° bin).""")

# --------------------------------------------------------------------------- #
# 7. why fast neutrons hurt: they jam the trigger
# --------------------------------------------------------------------------- #
steps = [dict(label='fast neutron', sub='above ~1.7 MeV', color=BE,
              tip='slow neutrons can’t do this: a recoil proton below ~1.7 MeV gives less light than half a minimum-ionising particle'),
         dict(label='hits the plastic', sub='kicks out a proton from the hydrogen', color=sd.MUT,
              tip='the trigger scintillators are plastic (CH): a neutron transfers its energy to a hydrogen nucleus'),
         dict(label='looks like an electron', sub='the light flash fires the trigger', color=sd.MUT,
              tip='“leg” = SiPM wall ≥ 0.5 MIP AND back plastic ≥ 0.5 MIP'),
         dict(label='DAQ is busy', sub='0.3 ms reading each event out', color=sd.RED,
              tip='DREAM reads 20 samples per event: τ ≈ 298 µs, non-paralysable, live = 1/(1 + f·τ)'),
         dict(label='real pairs missed', sub='so the beam must be turned down', color=sd.RED)]
fl = sd.flow(steps, size=30)
bars1 = sd.hbars([('Birmingham (Li)', legs['bham'], LI, f'{legs["bham"]:.0f} per arm per second at full current'),
                  ('NPI Řež (Be)', legs['npi'], BE, f'{legs["npi"]:.2g} per arm per second at full current')],
                 vmax=1e6, vmin=1e3, log=True, width=400, label_w=300, h=80, size=30,
                 fmt=lambda v: sci(v, 1))
bars2 = sd.hbars([('Birmingham (Li)', live['bham'], LI, 'fraction of time the DAQ can record; full current'),
                  ('NPI Řež (Be)', live['npi'], BE, f'even after turning the beam down to {thr_npi:.2f} of full current')],
                 vmax=1, width=400, label_w=300, h=80, size=30, fmt=lambda v: f'{100 * v:.0f} %')
panels = sd.row(sd.card(sd.p('<b>Trigger hits per arm, per second</b>', 28) + bars1, w=800),
                sd.card(sd.p('<b>Time the DAQ is listening</b>', 28) + bars2, w=800), gap=64)
D.slide('trigger', sd.title(f'Fast neutrons jam the trigger: ×{legs["npi"] / legs["bham"]:.0f} more fake hits',
                            'how a fast neutron fakes an electron in the MX17 arms, and what it costs (Geant4, big plastics)')
        + fl + panels
        + sd.callout('A neutron below ~1.7 MeV can’t fake an electron, so a lithium source never runs into this.', LI, 30),
        short='why fast hurts',
        notes=f"""MX17 decides to record an event when two arms each see a "leg": light in the SiPM wall and in the big
plastic behind it, as an electron would make. A neutron above ~1.7 MeV can knock a proton out of the plastic
hard enough to make that much light. A slow neutron can't.

Recording takes time: the DREAM electronics need ~0.3 ms per event, and during that time nothing else is
recorded. With hundreds of thousands of fake legs per arm per second, random coincidences between arms keep
the DAQ busy. At NPI Řež the study's best compromise turns the beam down to {thr_npi:.2f} of full current and still
records only {100 * live['npi']:.0f} % of the time. Birmingham doesn't need to turn anything down: {100 * live['bham']:.0f} % live.

Numbers: Geant4 runs of the MX17 arms (the broad-band "soft" runs) re-weighted to each source,
<code>survey/soft_sim/out/soft_components.csv</code> and <code>bepn_cyclotron/out/bepn_components.csv</code>.
A faster DAQ (5 samples) or a higher leg threshold would help Be most; see the cyclotron study.""")

# --------------------------------------------------------------------------- #
# 8. neutrons go everywhere: the shielding wall
# --------------------------------------------------------------------------- #
ang = pd.read_csv(ROOT / 'bepn_cyclotron/out/bepn_angles.csv')
a18 = ang[ang.E_p == 18].copy()
a18['th'] = 0.5 * (a18.th_lo + a18.th_hi)
g = []
cx, cy, S = 330, 330, 250 / a18.Y_per_sr_per_p.max()
th = np.concatenate([[0], a18.th.values, [180]])
yv = np.concatenate([[a18.Y_per_sr_per_p.iloc[0]], a18.Y_per_sr_per_p.values, [a18.Y_per_sr_per_p.iloc[-1]]])
up = [(cx + S * v * math.cos(math.radians(t)), cy - S * v * math.sin(math.radians(t))) for t, v in zip(th, yv)]
dn = [(cx + S * v * math.cos(math.radians(t)), cy + S * v * math.sin(math.radians(t))) for t, v in zip(th[::-1], yv[::-1])]
pp = up + dn
g.append(sd.poly([p_[0] for p_ in pp], [p_[1] for p_ in pp], BE, fill=BE + '33',
                 tip='how many neutrons go in each direction (NPI Řež, 18 MeV): distance from the target ∝ neutrons per steradian; ×3.3 more forward than backward'))
g.append(sd.poly([p_[0] for p_ in pp] + [pp[0][0]], [p_[1] for p_ in pp] + [pp[0][1]], BE, 3))
for t, v in zip(a18.th, a18.Y_per_sr_per_p):
    x_, y_ = cx + S * v * math.cos(math.radians(t)), cy - S * v * math.sin(math.radians(t))
    g.append(f'<circle cx="{x_:.1f}" cy="{y_:.1f}" r="12" fill="transparent"{sd.tipattr(f"{t:.0f}°: {v:.2e} neutrons per steradian per proton")}/>')
for t_ in range(0, 360, 30):
    v_ = float(np.interp(min(t_, 360 - t_), th, yv))
    L_ = S * v_ * 0.8
    g.append(sd.arrow(cx + 14 * math.cos(math.radians(t_)), cy - 14 * math.sin(math.radians(t_)),
                      cx + L_ * math.cos(math.radians(t_)), cy - L_ * math.sin(math.radians(t_)), NCOL, 3, 12))
g.append(sd.arrow(cx - 300, cy, cx - 12, cy, PCOL, 6, 18))
g.append(sd.T(cx - 200, cy - 18, 'protons', 22, PCOL, weight=600))
g.append(sd.T(cx + 170, cy - 140, 'more go forward', 22, BE, 'start'))
g.append(f'<rect x="{cx - 8}" y="{cy - 28}" width="16" height="56" fill="{sd.INK}"/>')
g.append(sd.T(cx, cy + 290, 'neutrons fly out in every direction', 24, BE, weight=600))
# wall + port + arms
wx = 700
g.append(f'<rect x="{wx}" y="40" width="160" height="580" fill="#d9d4ca" stroke="{sd.INK}" stroke-width="2.5"'
         f'{sd.tipattr("shielding wall: borated plastic (stops slow neutrons) + iron or concrete (slows fast ones)")}/>')
g.append(f'<rect x="{wx}" y="{cy - 10}" width="160" height="20" fill="{sd.BG}" stroke="{sd.GREEN}" stroke-width="2"'
         f'{sd.tipattr("a Ø8 cm hole (collimator): only this narrow beam reaches the cell")}/>')
g.append(sd.T(wx + 80, 28, 'shielding wall', 24, sd.INK, weight=600))
g.append(sd.T(wx + 80, cy - 26, 'hole', 21, sd.GREEN, weight=600))
g.append(sd.arrow(cx + 260, cy, wx + 290, cy, NCOL, 5, 16))
g.append(C.arms(wx + 390, cy, 1.4))
g.append(sd.T(wx + 390, cy + 178, 'MX17, cell 2 m', 24, sd.PURPLE, weight=600))
g.append(sd.T(wx + 390, cy + 206, 'from the target', 24, sd.PURPLE, weight=600))
diag = sd.svg(1180, 650, ''.join(g), 'neutrons leave the target in all directions; a wall with a hole lets only a beam through')
side = sd.col(
    sd.card(sd.p('<b>Without the wall, one arm would get</b>', 26)
            + sd.p(f'<b>×{arm_x_be:.0f}</b>', 48, sd.RED)
            + sd.p('more neutrons than the beam sent through the cell (Li or Be: same geometry)', 24, sd.MUT)),
    sd.card(sd.p('<b>Wall needed (estimate)</b>', 26)
            + sd.p(f'Be: ~{wall_be[0] / 100:.1f}–{wall_be[1] / 100:.1f} m', 34, BE, 600)
            + sd.p(f'Li: ~{wall_li[0] / 100:.1f}–{wall_li[1] / 100:.1f} m', 34, LI, 600)
            + sd.p('borated plastic (+ iron for Be)', 24, sd.MUT)),
    w=440, gap=24)
D.slide('shield', sd.title('Neutrons fly everywhere: MX17 needs a wall with a hole',
                           'how many neutrons go each way from the beryllium target (NPI Řež, 18 MeV), and the set-up it forces')
        + sd.row(diag, side, gap=40, align='center'),
        short='shielding',
        notes=f"""Unlike a proton beam, neutrons have no charge, so nothing can steer or focus them. They leave the target in
every direction, somewhat more forward than backward (×3.3 for beryllium at 18 MeV; the lobe is drawn from
<code>bepn_cyclotron/out/bepn_angles.csv</code>). The experiment takes a pencil of them through a Ø8 cm hole in
a thick wall, 2 m away. Everything else must be stopped before it reaches the arms.

Fast neutrons are much harder to stop than slow ones, so the beryllium wall is about twice as thick. Both wall
thicknesses are estimates: tenth-value layers and the detector's response to the leaking neutrons are stand-ins
(<code>bepn_shield.csv</code>, <code>bham_shield.csv</code>). The Birmingham wall plus the room around it is the next
thing to simulate in Geant4.

In practice, this means none of these sites can just put MX17 next to the target. Each one needs a port through a wall
into a second room, which is one of the questions for each facility.""")

# --------------------------------------------------------------------------- #
# 9. the scoreboard
# --------------------------------------------------------------------------- #
rows = [('Birmingham', 'bham', LI, 'lithium, 2.8 MeV, 30 mA, cell at 2 m, 5 cm Pb'),
        ('FRANZ', 'franz', LI, 'lithium, 2.0 MeV, design 20 mA DC, cell at 0.5 m (the 2 MeV stage is not built yet)'),
        ('FRM II MEDAPP', 'medapp', OTH, 'reactor fission beam (for comparison), standard filters'),
        ('LANSCE WNR', 'wnr', OTH, 'spallation source (for comparison), 4FP90L at 10 m, time-of-flight cut'),
        ('NPI Řež', 'npi', BE, f'beryllium, 18 MeV TR-24, 0°, 2 m, beam at {thr_npi:.2f} of 0.3 mA'),
        ('KURNS', 'kur', BE, 'beryllium, 30 MeV 1 mA BNCT cyclotron, 130°, 2 m'),
        ('NPI U-120M', 'u120', BE, 'beryllium, 18 MeV, 35 µA, the collimated beam that exists today')]
hb = []
for name, k, col, tp in rows:
    x = C.RHO / rho[k]
    dd = C.days_to_atomki(rho[k])
    note = f'{C.fmt_days(dd)} to the ATOMKI strength'
    hb.append((name, x, col, f'{tp}\nX17/IPC reach at 3σ in 50 days: {sci(rho[k], 1)}', note))
xmax = max(r[1] for r in hb) * 1.1
bars = sd.hbars(hb, vmax=xmax, width=820, label_w=300, h=58, size=30, fmt=lambda v: f'×{v:.1f}')
D.slide('ranking', sd.title(f'The two lithium sources lead; beryllium trails by ×{rho["npi"] / rho["bham"]:.1f}',
                            'how far past ATOMKI’s ⁴He signal each site can see in 50 days (higher is better; ×1 = just enough)')
        + sd.legend([('lithium (p,n)', LI, 'box'), ('beryllium (p,n)', BE, 'box'), ('other kinds of source', OTH, 'box')])
        + bars,
        foot='×N = ATOMKI X17/IPC (1.5×10⁻³) ÷ the 3σ reach in 50 days, big plastics, statistics + Geant4 background. Days: 50 × (reach/ATOMKI)².',
        short='ranking',
        notes=f"""The figure of merit of all the studies: the smallest X17 signal (as a fraction of the ordinary pairs, X17/IPC)
that a 50-day run would see at 3σ. ATOMKI's ⁴He claim corresponds to 1.5×10⁻³. Here it is turned into "×N past
ATOMKI": ×2 means the run would see a signal half as strong as ATOMKI's. The note on each bar is how many days of
beam would be enough to see ATOMKI's own signal (the reach improves as 1/√time).

Lithium at Birmingham and FRANZ: {sci(rho['bham'], 1)} and {sci(rho['franz'], 1)}. Beryllium at NPI Řež:
{sci(rho['npi'], 1)}. Grey bars are the two non-(p,n) sources studied in the same way, for scale.

What the bars don't show: the arms need a port through a wall at every one of these sites, and none has offered
one yet. FRANZ's number is for its design current, which it doesn't reach today. The verdicts and caveats are
in each study's own slide note.""")

# --------------------------------------------------------------------------- #
# 10. the three things to remember
# --------------------------------------------------------------------------- #
take = sd.row(
    sd.card(sd.p('1', 56, sd.DGREEN, 600) + sd.p('<b>Proton in, neutron out</b>', 30, sd.DINK)
            + sd.p(f'A proton above threshold ({T_li:.2f} MeV for Li) swaps into a light nucleus and knocks a neutron free.', 24, sd.DMUT),
            bg='#1f2533'),
    sd.card(sd.p('2', 56, sd.DGREEN, 600) + sd.p('<b>Leftover energy = neutron speed</b>', 30, sd.DINK)
            + sd.p('Run just above threshold (lithium, 2–3 MeV) and every neutron is slow, which is what X17 needs.', 24, sd.DMUT),
            bg='#1f2533'),
    sd.card(sd.p('3', 56, sd.DRED, 600) + sd.p('<b>Fast neutrons cost twice</b>', 30, sd.DINK)
            + sd.p(f'No signal, and they jam the trigger. Beryllium cyclotrons make {100 * (1 - win_be):.0f} % of them.', 24, sd.DMUT),
            bg='#1f2533'),
    gap=32)
open_q = sd.p('<b>What this primer leaves out:</b> the room and wall around each target (not simulated yet); the 478 keV '
              'γ flood from lithium; whether any site can give MX17 a port through a wall; and FRANZ’s 2 MeV stage, which '
              'isn’t built yet. Each study’s slide note has the details.', 26, sd.DMUT)
D.slide('remember', sd.kicker('Three things to remember')
        + '<h1 style="font-size:56px;font-weight:600;line-height:1.1;letter-spacing:-1px">Lithium near threshold is the '
          'natural X17 neutron source. Beryllium works, but pays for its fast tail.</h1>'
        + take + open_q, dark=True, short='remember',
        notes="""Where to go next:
<ul>
<li>Birmingham: <a href="https://dylan-neff.web.cern.ch/notes/birmingham-x17-feasibility.html">birmingham-x17-feasibility</a></li>
<li>FRANZ: <a href="https://dylan-neff.web.cern.ch/notes/franz-x17-feasibility.html">franz-x17-feasibility</a></li>
<li>NPI Řež and the Be cyclotrons: <a href="https://dylan-neff.web.cern.ch/notes/bepn-cyclotron-x17-feasibility.html">bepn-cyclotron-x17-feasibility</a></li>
<li>All facilities: <a href="https://dylan-neff.web.cern.ch/facilities/neutron-facilities.html">the neutron-facility dashboard</a></li>
</ul>""")

path = D.write(OUT / 'pn-neutron-sources-explained.html',
               note_meta=dict(title='Proton-beam neutron sources, explained',
                              summary='How a proton beam on lithium or beryllium makes neutrons, why X17 wants slow ones, '
                                      'and why the lithium (p,n) sources lead the facility ranking. A picture-first primer.',
                              tags='x17, facilities, neutron sources, explainer', date='2026-10-21'),
               footer='Built by x17_facility_search/docs/pn_source_explainer/build_deck.py from the Birmingham, FRANZ, '
                      'cyclotron Be(p,n), LANSCE WNR and FRM II study outputs.')
print(path)
print({k: f'{v:.2e}' for k, v in rho.items()}, 'win', win_li, win_be, 'thr', T_li, T_be, 'arm×', arm_x_be, arm_x_li)
