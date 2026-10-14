"""Pitch slides (2026-10-13), for the 15 Oct talk: the case for an LNL ⁸Be run, the run
plan, LNL against the 2026 n_TOF campaign, the hardware and its price, the signal-to-background
problem and what has to be studied, the target-region scattering, the open issues, and the
scintillator DAQ.

Called from build_deck.py right after the cover, so the rest of the deck is the backup.
Reads lnl/out/geant/reach_geant.csv (days_3d, the reference fit), lnl/out/syst/ycut.csv,
lnl/out/nd/nd_days_*.csv (through calo_slides.numbers), lnl/out/nd/smear_scan.csv
(lnl/sim/lnl_smear_nd.py), lnl/out/trigger/prescale_choice.csv and lnl/out/plastics/days_vs_size.csv.
"""
import math

import pandas as pd

import slidedoc as sd
from slidedoc import term

import maps_slides as MS
import pseudo_slides as PSD
import summary_slide as SUM
import plastics_scatter as PS

AB, BP = 'as built', 'big plastics'
REF = 'MM 15° + TOF'
A16 = 'ATOMKI 2016 anomaly'
ONRES = 'ATOMKI 2016, 18.15 res'
OFF_LO, OFF_HI = 'ATOMKI 2022 direct', 'Hanoi 2024'
# budgetary prices, trigger_scint/TRIGGER_OPTIONS.md §0 item 7 and §5 (trigger_scint/costs.py), k€
PRICE_PS = (93, 54, 142)        # 4 × 78×80×5 cm polystyrene, 2 × 3" PMT each: central (low, high)
PRICE_PVT = (136, 78, 217)      # same in cast PVT
PRICE_SIPM = (10, 5, 18)        # read all 20 bars, un-gang the preamps
PRICE_FERS160 = (18, 12, 25)    # FERS-5200 ×3 + DT5215 for 160 channels
PRICE_PETSYS = (22, 15, 32)
PRICE_V1742 = (75, 55, 90)      # 5 × V1742 DRS4 + crate
PRICE_VX2745 = (65, 50, 80)
DIGI_PER_PMT = (0.8, 0.5, 1.2)  # share of a 16-ch 500 MS/s-1 GS/s digitizer per PMT


def _days(G, scn, hw, I=1.0, m=16.7, col='days_3d'):
    r = G[(G.scenario == scn) & (G.hw == hw) & (G.level == REF) & (G.I_uA == I) & (G.mass == m)]
    return float(r[col].iloc[0])


def fd(d):
    return f'{d:.0f}' if d >= 10 else f'{d:.1f}'


def pitch_slides(D, O, ctx):
    G = pd.read_csv(O / 'geant' / 'reach_geant.csv')
    NC, R_ATOMKI = ctx['NC'], ctx['R_ATOMKI']
    d_bp, d_ab = _days(G, A16, BP), _days(G, A16, AB)
    r30b = R_ATOMKI * math.sqrt(d_bp / 30)
    r30a = R_ATOMKI * math.sqrt(d_ab / 30)
    plan = run_plan(G)

    cover_slide(D, ctx, d_bp, d_ab, r30b, plan)
    SUM.summary_slide(D, O)    # the one-slide closer for the n_TOF talk (2026-10-14 draft)
    why_slide(D, ctx)
    plan_slide(D, G, plan)
    ntof_table_slide(D, ctx, d_bp)
    lessons_slide(D, ctx)
    setup_slide(D, O, ctx, d_bp, d_ab)
    price_slide(D, ctx, d_bp, d_ab)
    sb_slide(D, O, ctx)
    MS.pitch_maps(D, O)
    PSD.pseudo_slides(D, O)
    smear_slide(D, O)
    studies_slide(D, O, ctx)
    unknowns_slide(D, ctx)
    daq_slide(D, O, ctx)
    return dict(r30b=r30b, r30a=r30a)


# --------------------------------------------------------------------------- #
# the run plan: 5σ on resonance, 3σ at both off-resonance energies, plus calibration
# --------------------------------------------------------------------------- #
CAL_DAYS = 1.0      # 441 keV (17.64 MeV line) calibration + cosmics: an assumption, not computed
SETUP_DAYS = 1.0    # beam tuning, target change, single-arm cosmics before beam: an assumption


def run_plan(G):
    out = {}
    for hw in (BP, AB):
        for I in (1.0, 4.0):
            blocks = [('setup', 'beam tune, cosmics', SETUP_DAYS, sd.GREY,
                       'Beam tuning, timing-in, single-arm cosmic MIPs for the arm gains. An allowance, not computed.'),
                      ('441 keV', 'calibration', CAL_DAYS / (I if I > 1 else 1), sd.GOLD,
                       '17.64 MeV resonance (E_p = 441 keV): the M1 IPC with a known shape and the γ line, to check the '
                       'acceptance, the energy scale and the |y| response. An allowance (scaled with current), not computed.')]
            on5 = _days(G, ONRES, hw, I) * 25 / 9
            blocks.append(('1.04 MeV', 'on resonance, 5σ', on5, sd.BLUE,
                           f'E_p = 1.04 MeV (18.15 MeV resonance), {hw}, {I:g} µA: 3σ in {fd(_days(G, ONRES, hw, I))} d, '
                           f'5σ in {fd(on5)} d (days × 25/9). θ × |y| × E_sum fit, calibrated response, S_θ 2 % + S_θy 1 %.'))
            for scn, lab, sub in ((OFF_LO, '0.80 MeV', 'off resonance, 3σ'), (OFF_HI, '1.225 MeV', 'off resonance, 3σ')):
                d = _days(G, scn, hw, I)
                blocks.append((lab, sub, d, sd.PURPLE,
                               f'{scn} ({lab}): direct capture, where ATOMKI 2022 and Hanoi 2024 report excesses. '
                               f'3σ at R(ATOMKI) in {fd(d)} d, {hw}, {I:g} µA.'))
            out[(hw, I)] = blocks
    return out


def plan_total(blocks):
    return sum(b[2] for b in blocks)


# --------------------------------------------------------------------------- #
def cover_slide(D, ctx, d_bp, d_ab, r30b, plan):
    tot = plan_total(plan[(BP, 1.0)])
    tot_cn = plan_total(plan[(BP, 4.0)])
    body = (sd.kicker('The pitch · MX17 at LNL Legnaro · 15 Oct 2026')
            + '<h1 style="font-size:64px;font-weight:600;line-height:1.08;letter-spacing:-1.5px">'
              'Test the ATOMKI ⁸Be anomaly with an independent detector, on ATOMKI\'s own reaction, '
              'in days of beam at LNL</h1>'
            + sd.p('⁷Li(p,e⁺e⁻)⁸Be on a thin lithium film at the LNL Van de Graaffs, with the MX17 apparatus built for n_TOF: '
                   'Micromegas tracking, four large arms, and four new large plastic scintillators. Numbers are Geant4 of the full '
                   'apparatus with an n_TOF-anchored detector response and a fit that lets the background shape float.', 30, sd.DMUT)
            + sd.row(
                sd.bignum(f'~{d_bp:.0f} day', '3σ at the ATOMKI ratio, 1 µA', sd.DGREEN,
                          f'With four 75×75×5 cm plastics. The n_TOF hardware as built needs ~{d_ab:.0f} days, and only with a repaired liquid scintillator.',
                          tip=f'θ × |y| × E_sum fit (reach_geant.csv days_3d), calibrated response, 2 % + 1 % unknown structure in the '
                              f'background shape. Big plastics {d_bp:.2f} d, as built {d_ab:.1f} d.'),
                sd.bignum(f'~{tot:.0f} days', 'for the whole programme on AN2000', sd.DBLUE,
                          f'5σ on resonance, 3σ at both off-resonance energies ATOMKI and Hanoi used, and a calibration line. ~{tot_cn:.0f} days on CN at 4 µA.'),
                sd.bignum(f'×{R_ATOMKI_over(ctx, r30b):.0f}', 'below the ATOMKI ratio in 30 days', sd.DGREY,
                          f'3σ reach R ≈ {sd.sci(r30b)} after a month at 1 µA; MEG II\'s 90 % CL limit at 18.1 MeV is 1.2×10⁻⁵.'),
                gap=56))
    D.slide('pitch', body, f"""<p>This block (the next twenty slides, the first a one-slide summary for the n_TOF talk) is the pitch for the 15 Oct talk. Everything after it is the
backup: the full feasibility study. The days come from <code>lnl/out/geant/reach_geant.csv</code> column <code>days_3d</code>
(FEASIBILITY_SIM.md §14.5): Geant4 of the full apparatus around a Li₂O 300 µg/cm² target, a selection with no Monte Carlo
truth, the per-layer calorimeter response anchored on the n_TOF measurements, and an event-level Fisher fit in opening angle
× energy split × energy sum with the M1/E1/γ₁ normalisations, the anisotropy, a cubic acceptance and Gaussian-process structure
all free. The programme total assumes 1 day of setup and 1 day of 441 keV calibration; both are allowances, not computed.</p>""",
            dark=True, short='Pitch')


def R_ATOMKI_over(ctx, r):
    return ctx['R_ATOMKI'] / r


# --------------------------------------------------------------------------- #
def why_slide(D, ctx):
    tag_bp, ATOMKI_ACC = ctx['tag_bp'], ctx['ATOMKI_ACC']
    rec = sd.col(
        sd.p('The record, as of Oct 2026', 28, weight=600),
        sd.callout('<b>ATOMKI 2016, 2022</b>: a 6.8σ excess at ~140° in ⁸Be (1.10 MeV), then excesses at every off-resonance energy '
                   '(direct capture). Also ⁴He and ¹²C.', sd.ORANGE, 24),
        sd.callout('<b>Hanoi 2024</b>: ≥ 4σ at 1.225 MeV, with a two-arm spectrometer built by ATOMKI.', sd.ORANGE, 24),
        sd.callout('<b>MEG II 2025</b>: nothing. R(18.1) &lt; 1.2×10⁻⁵ at 90 % CL; the ATOMKI value has p = 6.2 %.', sd.RED, 24),
        sd.callout('<b>MEG II members, Sept 2026</b>: cosmic two-arm coincidences make a 140° bump in ATOMKI-type geometries.', sd.RED, 24),
        sd.callout('<b>LNL 2023–24</b>: an ATOMKI-like spectrometer already ran this reaction on the AN2000. Unpublished.', sd.GREY, 24),
        gap=14, w=760)
    brings = sd.col(
        sd.p('What MX17 at LNL adds', 28, weight=600),
        sd.flow([dict(label='Same reaction, same beam', sub='⁷Li(p,e⁺e⁻)⁸Be at 1.0–1.2 MeV, 1 µA: ATOMKI\'s own conditions', color=sd.BLUE,
                      tip='The AN2000 and CN Van de Graaffs both cover 0.44–1.2 MeV routinely. No neutrons below E_p = 1.88 MeV.')], size=24),
        sd.flow([dict(label='Tracks, not just hits', sub='Micromegas TPCs point each lepton back to the target: the cosmic critique answered', color=sd.BLUE,
                      tip='MM 15° segments + 0.3 ns time of flight leave < 1 cosmic/day in the window (FEASIBILITY_SIM §4).')], size=24),
        sd.flow([dict(label=f'~{tag_bp / ATOMKI_ACC:.0f}× ATOMKI\'s pair acceptance', sub='four large arms with 75 cm plastics', color=sd.GREEN,
                      tip=f'X17 pairs with both legs tagged: {tag_bp * 100:.0f} % (Geant4, big plastics) against ~{ATOMKI_ACC * 100:.1f} % for a 5-telescope ATOMKI setup (ESTIMATES.md §2).')], size=24),
        sd.flow([dict(label='A different detector', sub='different geometry, acceptance and systematics from every result so far', color=sd.BLUE,
                      tip='Every positive result so far comes from ATOMKI-built or ATOMKI-like ΔE–E telescope spectrometers.')], size=24),
        sd.flow([dict(label='Hardware that exists', sub='the n_TOF apparatus moves as is; the new items are the plastics and a scintillator DAQ', color=sd.GREY)], size=24),
        gap=14)
    D.slide('pitch-why', sd.title('The X17 record contradicts itself; ⁸Be at LNL is where an independent detector can check it',
                                  'Left: what has been seen and not seen. Right: what the MX17 apparatus brings to ATOMKI\'s reaction. Hover the boxes.')
            + sd.row(rec, brings, gap=56),
            """<p>Sources in <code>lnl/PHYSICS.md</code>: Krasznahorkay <i>et al.</i>, PRL 116, 042501 (2016); Sas <i>et al.</i>,
arXiv:2205.07744 (2022); Tran The Anh <i>et al.</i> (Hanoi, 2024); MEG II, EPJC 85, 763 (2025); Benmansour <i>et al.</i>,
arXiv:2609.18383 (2026). The LNL group (T. Marchi <i>et al.</i>, INFN-CSN3 NUCLEX) ran on the AN2000 in 2023–24
(<code>lnl/FACILITY.md</code>): partners or competitors, and the first people to talk to.</p>""",
            short='Why')


# --------------------------------------------------------------------------- #
def plan_slide(D, G, plan):
    W, H = 1664, 470
    x0, x1 = 360, 1600
    dmax = 20.0
    X = lambda d: x0 + min(d, dmax) / dmax * (x1 - x0)
    o = []
    for d in range(0, int(dmax) + 1, 2):
        o.append(sd.line(X(d), 40, X(d), H - 60, sd.RULE, 1))
        o.append(sd.T(X(d), H - 26, str(d), 21, sd.MUT))
    o.append(sd.T((x0 + x1) / 2, H + 4, 'days of beam', 22, sd.MUT))
    o.append(sd.line(X(14), 30, X(14), H - 60, sd.GOLD, 2, '6 6'))
    o.append(sd.T(X(14) + 8, 30, 'two weeks', 20, sd.GOLD, 'start'))
    rows = [((BP, 1.0), 'big plastics, AN2000 1 µA', sd.GREEN), ((BP, 4.0), 'big plastics, CN 4 µA', sd.GREEN),
            ((AB, 1.0), 'n_TOF as built, 1 µA', sd.RED)]
    for i, (key, lab, col) in enumerate(rows):
        y = 60 + i * 122
        o.append(sd.T(x0 - 20, y + 42, lab, 24, sd.INK, 'end', 600))
        tot = plan_total(plan[key])
        o.append(sd.T(x0 - 20, y + 72, f'total {fd(tot)} d', 21, col, 'end'))
        t = 0.0
        for name, sub, d, c, tp in plan[key]:
            xa, xb = X(t), X(t + d)
            if xa >= x1:
                break
            o.append(f'<g{sd.tipattr(tp)}><rect x="{xa:.1f}" y="{y}" width="{max(xb - xa - 2, 1):.1f}" height="74" rx="6" '
                     f'fill="{c}" fill-opacity="0.85"/>')
            if xb - xa > 80:
                o.append(sd.T((xa + xb) / 2, y + 36, name, 21, '#fff', 'middle', 600))
                o.append(sd.T((xa + xb) / 2, y + 62, f'{fd(d)} d', 19, '#fff'))
            o.append('</g>')
            t += d
        if tot > dmax:
            o.append(sd.T(x1 + 10, y + 50, '→', 34, sd.RED, 'start'))
            o.append(sd.T(x1 - 6, y + 98, f'off the axis: {fd(tot)} days in all', 21, sd.RED, 'end'))
    side = sd.row(
        sd.callout('<b>One fixed energy per day suits a self-service AN2000:</b> each setting is held for days. '
                   'The off-resonance points test the X17 claim directly: the edge moves with E_p, an IPC artefact would not.', sd.BLUE, 23),
        sd.callout(f'<b>With the n_TOF hardware as built</b> the on-resonance 5σ alone takes ~{plan[(AB, 1.0)][2][2] / 7:.0f} weeks, and needs a liquid '
                   'scintillator that worked at n_TOF only in part. The big plastics are what make it a two-week proposal.', sd.RED, 23),
        gap=40)
    D.slide('pitch-plan', sd.title(f'Two weeks on AN2000 cover the whole programme',
                                   f'Beam days per step: 5σ on the 18.15 MeV resonance, 3σ at both off-resonance energies, setup and the 441 keV '
                                   f'calibration; ~{plan_total(plan[(BP, 4.0)]):.0f} days on CN at 4 µA. Geant4 reference fit; hover the blocks.')
            + sd.svg(W, H + 10, ''.join(o), 'run plan in beam days') + side,
            """<p>Days to 3σ at R(ATOMKI) from <code>reach_geant.csv</code> (<code>days_3d</code>: θ × |y| × E_sum fit, calibrated
response, S_θ 2 % + S_θy 1 %, DAQ live time included); 5σ = 3σ days × 25/9. On resonance is the 'ATOMKI 2016, 18.15 res'
target (Li₂O 300 µg/cm² at 1.04 MeV); the off-resonance points are the ATOMKI 2022 (LiF 300, 0.80 MeV) and Hanoi 2024 (LiF 300,
1.225 MeV) configurations. Setup and 441 keV calibration are one-day allowances each (the calibration scaled with current);
they are not computed. The off-resonance reach assumes the same R as on resonance, which is ATOMKI's claim.</p>""",
            short='Plan')


# --------------------------------------------------------------------------- #
def ntof_table_slide(D, ctx, d_bp):
    tag_ab, tag_bp = ctx['tag_ab'], ctx['tag_bp']
    rows = [
        ['Reaction', 'n + ³He → ⁴He* → ⁴He e⁺e⁻', '⁷Li + p → ⁸Be* → ⁸Be e⁺e⁻ (ATOMKI\'s)'],
        ['Beam', 'white neutron beam, EAR2: E_n from meV to MeV', 'DC protons at one energy, 0.44–1.2 MeV'],
        ['Excitation and X17 edge', 'E* = 20.58 + 0.75·E_n: the edge moves 110° → 66° event by event', 'E* fixed by E_p: the edge sits at 133–139°'],
        ['Target', '500 bar ³He capsule, Al 0.6 + CFRP 0.9 mm (1.26 % X₀)', '1.5 µm Li₂O film in vacuum, CFRP 0.4 mm chamber'],
        ['X17 angle resolution σ68', '14.5° (the capsule wall)', '4.6° (the chamber wall)'],
        ['What else makes pairs', 'n capture in the capsule: Al and C (n,γ), 10⁴–10⁶ × the ³He captures', 'only the reaction itself (IPC) and cosmics: no neutrons below 1.88 MeV'],
        ['X17 pairs triggered', f'{tag_ab * 100:.1f} % (as-built stack; 2.3 % for the n_TOF kinematics)', f'{tag_bp * 100:.0f} % with big plastics'],
        ['Running conditions', 'a γ flash every bunch; the DREAM noise floor doubled on 23 July for all of production', 'DC beam, ~150 arm legs/s and 22 pairs/s at 1 µA: > 96 % live'],
        ['The two leptons', 'often in one chamber: two-track reconstruction loses close pairs', 'at ~140° always in different arms'],
        ['Result', 'no X17 result yet: angle scale and two-track reconstruction still open', f'3σ at the ATOMKI ratio in ~{d_bp:.0f} day (Geant4)'],
    ]
    tips = [None,
            'n_TOF EAR2: every neutron energy in each bunch, sorted by time of flight.',
            'docs/anchor_kinematics.py: θ_min 109.6° at rest, 99.3° at E_n = 2 MeV, 65.7° at 14 MeV. At LNL, 133° (m = 16.7) to 139° (17.0) at 1.03 MeV.',
            'n_TOF: docs/PLAN_GANIL_NFS.md Part 0. LNL: lnl/TARGETS.md, GEANT_PREP.md §4.',
            'n_TOF: MX17_Full_Geant angular_resolution_note.md, vertex known exactly. LNL: Geant4 big plastics, MM 15° + TOF (FEASIBILITY_SIM §10).',
            'nTof_x17 sept26_prelim_analysis STATUS.md / IPC_MISSING.md: the capsule wall captures far more neutrons than the ³He; its continuum describes the data below 109°.',
            'Both legs tagged by the trigger scintillators, Geant4 X17 m = 16.7.',
            'LNL: lnl/out/trigger/prescale_choice.csv (big plastics, 1 µA, every single-arm trigger taken). n_TOF: nTof_x17 CLAUDE.md / ntof_pedestal_qa (RdClk_Div 6 → 4, residual noise ×2.0 on all eight FEUs from run_69).',
            'nTof_x17 OCTOBER_2026.md §1: production found both tracks of a pair ≥ 24 mm apart 39–47 % of the time, ~0 below 12 mm. LNL: 4 arms at 90°, so a 140° pair never shares one.',
            'nTof_x17 sept26_prelim_analysis STATUS.md (2026-10-12): the re-pass is running; the angle-scale calibration and the same-chamber pairs are the open items.']
    D.slide('pitch-vs-ntof', sd.title('The same apparatus, a cleaner problem: LNL against the 2026 n_TOF run',
                                      'Row by row: what made n_TOF hard, and what replaces it at LNL. Hover a row for the source.')
            + sd.table(['', 'n_TOF EAR2, 2026 (ran)', 'LNL AN2000 / CN (proposed)'], rows, size=23, widths=[330, 640, 640],
                       align=['left', 'left', 'left'], tips=tips),
            """<p>The n_TOF column is the 2026 campaign as measured and as simulated (MX17_Full_Geant; nTof_x17
<code>sept26_prelim_analysis/</code>). The data-taking ended on 10 Aug 2026; the analysis is still in progress, and its
open items are the angle-scale calibration and the reconstruction of two tracks in one chamber. The LNL column is the Geant4
study in this deck. The n_TOF yield question (the ³He self-shielding in the rate table, IPC_MISSING.md item 1) is not
listed: it does not change the comparison.</p>""",
            short='vs n_TOF')


# --------------------------------------------------------------------------- #
def lessons_slide(D, ctx):
    pairs = [
        ('The target sets the resolution', 'The capsule wall smeared the X17 edge into a 40°-wide bump (σ68 14.5°).',
         'A 1.5 µm film in a 0.4 mm carbon chamber: σ68 4.6°. The edge stays a step.'),
        ('The target makes its own background', 'Neutron capture in the Al/C capsule made pairs 10⁴–10⁶ × more often than ³He.',
         'Protons below 1.88 MeV make no neutrons. The background is the reaction\'s own IPC, which QED predicts.'),
        ('A white beam smears the kinematics', 'Each neutron energy has its own X17 edge, 110° → 66°.',
         'One proton energy, one edge. Moving E_p on purpose is the test.'),
        ('The trigger saw a few % of pairs', f'Two 20×30 cm bars per arm tagged {ctx["tag_ab"] * 100:.1f} % of X17 pairs.',
         f'Four 75×75×5 cm plates: {ctx["tag_bp"] * 100:.0f} %, and a calorimeter for |y| and E_sum.'),
        ('Close tracks merge', 'Pairs in one chamber below ~12 mm were not reconstructed as two.',
         'At 140° the leptons are always in different arms.'),
        ('Calibration was improvised', 'The angle scale is still being fixed from muons and the capsule.',
         'Calibration lines on tap: the 441 keV resonance, the γ lines, and cosmic MIPs from the single-arm trigger.'),
    ]
    cards = []
    for t, a, b in pairs:
        cards.append(sd.row(
            sd.p(f'<b>{t}</b>', 24, sd.INK, extra='width:330px'),
            sd.p(a, 22, sd.RED, extra='width:560px'),
            sd.p('→', 30, sd.MUT),
            sd.p(b, 22, sd.GREEN, extra='width:640px'), gap=20, align='center'))
    D.slide('pitch-lessons', sd.title('What n_TOF taught us is built into the LNL design',
                                      'Each n_TOF difficulty (red) and what the LNL setup does about it (green).')
            + sd.col(*cards, gap=26)
            + sd.callout('<b>n_TOF was not wasted:</b> its measured scintillator response anchors every LNL energy in this study, its cosmics '
                         'calibrate the arms, and its reconstruction is the one LNL would run.', sd.BLUE, 24),
            """<p>n_TOF sources: MX17_Full_Geant <code>docs/angular_resolution/angular_resolution_note.md</code>; nTof_x17
<code>sept26_prelim_analysis/OCTOBER_2026.md</code>, <code>STATUS.md</code>, <code>IPC_MISSING.md</code>;
<code>trigger_scint/TRIGGER_OPTIONS.md</code>. The LNL calorimeter response uses nTof_x17 <code>ntof_calorimetry</code> (C1, C4) and
the scint-stack per-cell maps (FEASIBILITY_SIM §14.2).</p>""",
            short='Lessons')


# --------------------------------------------------------------------------- #
def setup_slide(D, O, ctx, d_bp, d_ab):
    dv = pd.read_csv(O / 'plastics' / 'days_vs_size.csv')
    opt = dv[dv.placement.str.startswith('where the bars are now')]
    opt = opt.loc[opt.days.idxmin()]
    p_ntof, p_big = PS.config_slide(opt, panels_only=True)
    tag_ab, tag_bp = ctx['tag_ab'], ctx['tag_bp']
    c, lo, hi = PRICE_PS
    cv, lov, hiv = PRICE_PVT
    price_tip = (f'Budgetary, 2026, no labour or VAT (trigger_scint/costs.py): four 78×80×5 cm slabs with two 3" PMTs each, '
                 f'fishtail guides, wrapping, mechanics, HV and digitizer channels. Polystyrene €{c}k ({lo}–{hi}k); cast PVT €{cv}k '
                 f'({lov}–{hiv}k). Plus reading all 20 SiPM bars (~€{PRICE_SIPM[0]}k) and the SiPM DAQ (next-but-one slides). '
                 'Get two vendor quotes before deciding.')
    tag = (f'<p{sd.tipattr(price_tip)} style="font-size:22px;color:{sd.MUT};border:1px solid {sd.RULE};border-radius:20px;'
           f'padding:4px 16px;align-self:flex-start">≈ €{c}–{cv}k</p>')
    left = sd.col(sd.p('<b>n_TOF as built</b>: two 20×30×2 cm bars per arm + liquid scintillator', 24, sd.RED), p_ntof,
                  sd.p(f'X17 pairs triggered {tag_ab * 100:.1f} % · 3σ in ~{d_ab:.0f} d (liquid repaired)', 23, sd.MUT), gap=4)
    right = sd.col(sd.row(sd.p('<b>LNL</b>: one 75×75×5 cm plastic per arm, no liquid', 24, sd.GREEN), tag, gap=18, align='center'),
                   p_big,
                   sd.p(f'X17 pairs triggered {tag_bp * 100:.0f} % · 3σ in ~{d_bp:.0f} d', 23, sd.MUT), gap=4)
    D.slide('pitch-setup', sd.title('One change to the apparatus: a 75 cm plastic behind each arm',
                                    'To scale. Micromegas (blue) and the SiPM wall (purple) stay; the bars and the liquid are replaced. Hover the parts and the price.')
            + sd.row(left, right, gap=36),
            f"""<p>Drawings as the 'Configs' backup slide (MX17_Full_Geant SimConfig.hh). The plate is {opt.S_mm / 10:.0f} cm square, 5 cm
thick, front at {opt.R_front_mm / 10:.0f} cm (where the bars are now); the Geant4 runs use 75×75×5 cm. 5 cm of plastic stops most
of a ~10 MeV lepton, so the plate is also the calorimeter that the energy split |y| and E_sum need; 2 cm bars stop neither
lepton (FEASIBILITY_SIM §14.2). Read each plate at both ends (2 × 3" PMTs through fishtail guides): one end gives 15 %
non-uniformity and a 1.5–1.8 ns time offset across the plate (trigger_scint/TRIGGER_OPTIONS.md §4).</p>
<p>Price (budgetary, k€): {price_tip}</p>
<p>Weight: ~32 kg per plate, so the arm frames need rework. Confirm the largest single-piece 5 cm sheet with the vendor;
the fallback is two 37×75 cm bars per arm (+2 PMTs per arm, ~+€50k in all).</p>""",
            short='Setup')


# --------------------------------------------------------------------------- #
def price_slide(D, ctx, d_bp, d_ab):
    """What the four big plates cost, part by part (trigger_scint/costs.py), and the add-ons (2026-10-14)."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'trigger_scint'))
    import costs as CO
    parts = [('scint', 'scintillator (4 × 78×80×5 cm)', sd.BLUE), ('pmts', 'PMTs + bases (8 × 3")', sd.PURPLE),
             ('guides', 'light guides (fishtail)', sd.GOLD), ('mech', 'wrapping + mechanics', sd.GREY),
             ('elec', 'HV + digitizer channels', sd.GREEN)]
    mats = [('PS', 'polystyrene'), ('PVT', 'cast PVT (EJ-200 class)')]
    br = {m: [{k: 4 * v for k, v in CO.slab_cost(78, 80, 5, '3"', 2, m, j).items()} for j in range(3)] for m, _ in mats}
    sipm, daq = CO.SIPM_COMPLETION, CO.DAQ[[k for k in CO.DAQ if k.startswith('160 ch: FERS')][0]]
    W, H = 1000, 470
    x0, xw, vmax = 230, 700, 260e3
    X = lambda v: x0 + xw * v / vmax
    o = []
    for v in range(0, 260001, 50000):
        o.append(sd.line(X(v), 40, X(v), 400, sd.RULE, 1.2))
        o.append(sd.T(X(v), 430, f'€{v / 1e3:.0f}k', 20))
    rows_y = {'PS': 90, 'PVT': 250}
    for m, lab in mats:
        y = rows_y[m]
        c = br[m][1]
        o.append(sd.T(x0 - 16, y + 8, m, 28, sd.INK, 'end', 600))
        o.append(sd.T(x0 - 16, y + 36, lab, 18, sd.MUT, 'end'))
        cur = 0.0
        for k, name, col in parts:
            v = c[k]
            tip = f'{name}, {m}: €{v / 1e3:.0f}k central (€{br[m][0][k] / 1e3:.0f}–{br[m][2][k] / 1e3:.0f}k)'
            o.append(f'<rect x="{X(cur):.1f}" y="{y - 22}" width="{X(cur + v) - X(cur):.1f}" height="56" fill="{col}"{sd.tipattr(tip)}/>')
            if X(cur + v) - X(cur) > 60:
                o.append(sd.T(0.5 * (X(cur) + X(cur + v)), y + 13, f'{v / 1e3:.0f}', 20, '#ffffff', weight=600))
            cur += v
        # add-ons, hatched lighter
        for (lo_, c_, hi_), name, col in ((sipm, 'all 20 SiPM bars read, preamps un-ganged', sd.ORANGE),
                                          (daq, 'SiPM DAQ: FERS-5200 ×3 + DT5215 (160 ch)', sd.RED)):
            tip = f'{name}: €{c_ / 1e3:.0f}k ({lo_ / 1e3:.0f}–{hi_ / 1e3:.0f}k). Needed whichever plastic is chosen.'
            o.append(f'<rect x="{X(cur):.1f}" y="{y - 22}" width="{X(cur + c_) - X(cur):.1f}" height="56" fill="{col}" fill-opacity="0.85"{sd.tipattr(tip)}/>')
            cur += c_
        lo = br[m][0]['total'] + sipm[0] + daq[0]
        hi = br[m][2]['total'] + sipm[2] + daq[2]
        o.append(sd.line(X(lo), y + 52, X(hi), y + 52, sd.INK, 2.5))
        o.append(sd.line(X(lo), y + 44, X(lo), y + 60, sd.INK, 2.5) + sd.line(X(hi), y + 44, X(hi), y + 60, sd.INK, 2.5))
        o.append(sd.T(X(cur) + 14, y + 13, f'€{cur / 1e3:.0f}k', 26, sd.INK, 'start', 700,
                      tip=f'{m} plates €{c["total"] / 1e3:.0f}k + SiPM completion + SiPM DAQ. Range €{lo / 1e3:.0f}–{hi / 1e3:.0f}k (whisker).'))
        o.append(sd.T(X(lo), y + 84, f'low–high €{lo / 1e3:.0f}–{hi / 1e3:.0f}k', 18, sd.MUT, 'start'))
    chart = sd.svg(W, H, ''.join(o), 'price of the big plastics')
    leg = sd.legend([(n, c, 'box') for _, n, c in parts] + [('SiPM bars completed', sd.ORANGE, 'box'), ('SiPM DAQ (FERS)', sd.RED, 'box')], 19)
    tot_ps = br['PS'][1]['total'] + sipm[1] + daq[1]
    side = sd.col(
        sd.callout(f'<b>The plates: €{br["PS"][1]["total"] / 1e3:.0f}k in polystyrene, €{br["PVT"][1]["total"] / 1e3:.0f}k in PVT</b> '
                   '(central; four plates, two 3" PMTs each). In PVT the plastic itself is over half the price; '
                   'polystyrene gives ~70 % of the light, enough for a 5 cm calorimeter (bench test it).', sd.BLUE, 21),
        sd.callout(f'<b>With the SiPM side: ~€{tot_ps / 1e3:.0f}k all in</b> (polystyrene). Reading all 20 SiPM bars and a '
                   'slow 160-channel DAQ are needed in either case.', sd.ORANGE, 21),
        sd.callout(f'<b>What it buys:</b> X17 pairs triggered {ctx["tag_ab"] * 100:.1f} % → {ctx["tag_bp"] * 100:.0f} %, and 3σ at '
                   f'the ATOMKI ratio in ~{d_bp:.0f} day instead of ~{d_ab:.0f} days (which also needs a repaired liquid).', sd.GREEN, 21),
        sd.callout('<b>Budgetary only</b>: 2026 EUR, no labour, no VAT. No vendor publishes list prices; get two quotes '
                   '(Eljen/Luxium/Nuvia for the plastic, Hamamatsu/ET for the PMTs).', sd.GREY, 21),
        gap=14, w=600)
    D.slide('pitch-price', sd.title(f'The new plastics: ~€{br["PS"][1]["total"] / 1e3:.0f}k, ~€{tot_ps / 1e3:.0f}k with the SiPM readout',
                                    'Budgetary cost of four 78×80×5 cm plates with two 3" PMTs each, part by part (central values), plus the '
                                    'SiPM-side add-ons. Whiskers: low–high. Hover the segments.')
            + sd.row(sd.col(chart, leg, gap=10), side, gap=36),
            f"""<p><code>trigger_scint/costs.py</code> (<code>slab_cost(78, 80, 5, '3"', 2, material)</code> × 4; SIPM_COMPLETION; the FERS row
of DAQ). Unit prices and their public reference points are in that file's docstring and <code>trigger_scint/TRIGGER_OPTIONS.md</code>
§5: plastic €{CO.PS_PER_CM3[1]}/cm³ (PS) and €{CO.PVT_PER_CM3[1]}/cm³ (PVT) for large cast sheets with finished edges, 3" PMT + base
€{CO.PMT['3"'][1] / 1e3:.1f}k, a fishtail guide €{CO.GUIDE_LARGE[1] / 1e3:.1f}k each, wrapping and mechanics €{CO.WRAP_MECH_PER_SLAB[5][1] / 1e3:.0f}k per plate,
HV + a digitizer channel €{(CO.HV_PER_CH[1] + CO.DIGI_PER_PMT_CH[1]) / 1e3:.1f}k per PMT. If the 320-channel SiPM option holds (two SiPMs per bar end),
the FERS DAQ is ~€{daq[1] * 5 / 3 / 1e3:.0f}k instead of €{daq[1] / 1e3:.0f}k. Not included: reworking the arm frames for ~32 kg plates, and the
fallback of two 37×75 cm bars per arm (+2 PMTs per arm, ~+€50k).</p>""",
            foot='trigger_scint/costs.py (budgetary, 2026 EUR, no labour or VAT)', short='Price')


# --------------------------------------------------------------------------- #
def sb_slide(D, O, ctx):
    yc = pd.read_csv(O / 'syst' / 'ycut.csv')
    b = yc[yc.hw == BP].set_index('ycat')
    NC = ctx['NC']
    P = sd.Plot(900, 600, x=(0.005, 0.1, 'log'), y=(0.5, 30, 'log'), xlabel='uncertainty δ on the background shape under the edge',
                ylabel='largest Z reachable, any running time')
    P.xticks([(v, f'{v * 100:g} %') for v in (0.005, 0.01, 0.02, 0.05, 0.1)]).yticks([(v, f'{v:g}') for v in (0.5, 1, 2, 3, 5, 10, 20)])
    xs = [0.005 * 1.1 ** k for k in range(32) if 0.005 * 1.1 ** k <= 0.1]
    for cat, lab, col in (('all', 'all pairs', sd.GREY), ('y<0.3', 'symmetric pairs, |y| < 0.3', sd.BLUE)):
        sb = float(b.loc[cat].SB_best)
        xk = [x for x in xs if sb / x <= 30]
        P.line(xk, [sb / x for x in xk], col, 4, markers=False,
               tip=f'{lab}: S/B = {sb * 100:.0f} % in the best window ({b.loc[cat].best_win}°), big plastics. Z_max = (S/B)/δ.')
        if cat == 'all':
            P.text(0.06, sb / 0.06 * 0.62, f'{lab}: S/B {sb * 100:.0f} %', 21, col, anchor='end')
        else:
            P.text(0.0115, sb / 0.0115 * 1.25, f'{lab}: S/B {sb * 100:.0f} %', 21, col, anchor='start')
    P.hline(3, sd.GOLD, label='3σ', where='above')
    P.hline(5, sd.RED, label='5σ', where='above')
    s3d = NC['bp_nd_worst'] / NC['bp_nd']
    side = sd.col(
        sd.callout(f'<b>Statistics are not the problem.</b> One week at 1 µA with big plastics: ~750 X17 on ~10,700 IPC pairs '
                   f'in 130–172°. A 3σ excess is ~1σ per bin.', sd.GREY, 23),
        sd.callout(f'<b>The cap.</b> If the background shape under the edge is uncertain by δ relative to its sidebands, counting can never '
                   f'beat Z = (S/B)/δ. All pairs at 2 %: {b.loc["all"].SB_best / 0.02:.1f}σ, however long we run.', sd.ORANGE, 23),
        sd.callout(f'<b>What lifts it:</b> the energy split takes S/B from {b.loc["all"].SB_best * 100:.0f} % to {b.loc["y<0.3"].SB_best * 100:.0f} %, and '
                   f'the fit in θ × |y| × E_sum measures the shape from the signal-free parts of the data. With realistic shape errors '
                   f'it slows by at most ×{s3d:.1f}.', sd.BLUE, 23),
        sd.callout('<b>So the study list is about the background shape</b>, at the 1 % level: next slides.', sd.GREEN, 23),
        gap=16, w=640)
    D.slide('pitch-sb', sd.title('At LNL the limit is signal-to-background, not statistics',
                                 'Left: the most significance a counting analysis can ever reach if the background shape is known to δ (big plastics, '
                                 'best window). Hover the lines.')
            + sd.row(P.svg('Z cap against shape uncertainty'), side, gap=40),
            f"""<p>S/B in the best window from <code>lnl/out/syst/ycut.csv</code> (big plastics, MM 15° + TOF, ideal energies; as built is the
same within ±1 %). The cap Z_max = (S/B)/δ is for a uniform fractional error δ on the background in the window relative to the
sidebands (FEASIBILITY_SIM §11–12). The fit numbers (§14.3, calibrated response) are not capped this way because the fit
measures the shape: worst structure tried {NC['bp_nd_worst']:.1f} d against {NC['bp_nd']:.1f} d nominal (big plastics), {NC['ab_nd_worst']:.0f} against
{NC['ab_nd']:.0f} d as built. Those numbers hold only if the true shape error looks like the Gaussian-process structure assumed
(5 % at most, correlation length ≥ 5°).</p>""",
            foot='lnl/out/syst/ycut.csv; lnl/out/nd/nd_days_*.csv; FEASIBILITY_SIM §11–14', short='S/B')


# --------------------------------------------------------------------------- #
def smear_slide(D, O):
    f = O / 'nd' / 'smear_scan.csv'
    if not f.exists():
        D.slide('pitch-smear', sd.title('Target-region scattering: pending', 'Run lnl/sim/lnl_smear_nd.py.'), short='Smearing')
        return
    t = pd.read_csv(f)
    bp = t[t.hw == BP]
    P = sd.Plot(980, 620, x=(3, 32, 'log'), y=(0.5, 3000, 'log'), xlabel='X17 opening-angle resolution σ68 [deg]',
                ylabel='days to 3σ at R(ATOMKI), 1 µA, big plastics')
    P.xticks([(v, f'{v:g}°') for v in (3, 5, 10, 15, 20, 30)]).yticks([(v, f'{v:g}') for v in (1, 3, 10, 30, 100, 300, 1000)])
    cols = {'θ': sd.GREY, 'm_ee': sd.PURPLE, 'θ × |y|': sd.ORANGE, 'θ × |y| × E_sum': sd.BLUE}
    labs = {'θ': 'opening angle alone', 'm_ee': 'pair mass m_ee', 'θ × |y|': 'angle × energy split', 'θ × |y| × E_sum': 'angle × split × energy sum'}
    for a, col in cols.items():
        g = bp[bp.analysis == a].sort_values('x17_sigma68')
        g = g[g.days < 3000]
        if g.empty:
            continue
        tips = [f'{labs[a]}: {r.case}, σ68 {r.x17_sigma68:.1f}° → {fd(r.days)} d' for r in g.itertuples()]
        P.line(list(g.x17_sigma68), list(g.days), col, 4, tips=tips, r=7)
    P.vline(4.6, sd.GREEN, '6 6', label='CFRP 0.4 mm', tip='The baseline chamber: σ68 4.6° (Geant4)')
    P.vline(14.5, sd.RED, '6 6', label='n_TOF capsule', tip='The n_TOF capsule: σ68 14.5°')
    th = bp[bp.analysis == 'θ × |y| × E_sum'].set_index('factor').days
    md = bp[bp.analysis == 'm_ee'].set_index('factor').days
    side = sd.col(
        sd.legend([(labs[a], c) for a, c in cols.items()], 20),
        sd.callout(f'<b>The worry is justified.</b> Once the background shape may float, a wider edge looks like background structure. '
                   f'The reference fit goes {fd(th[1.0])} → {fd(th[2.0])} d at 9° and {fd(th[3.1])} d at ~14°, the n_TOF capsule.', sd.RED, 22),
        sd.callout(f'<b>The higher-dimensional fit is what keeps it alive.</b> |y| and E_sum come from the scintillators and do not smear. '
                   f'At ~14°: {fd(th[3.1])} d against {fd(md[3.1])} d for m_ee; the angle alone never gets there.', sd.BLUE, 22),
        sd.callout('<b>Design rule:</b> only the wall the leptons cross counts (3.8° of the 4.6° is the CFRP). Accepted leptons fly at '
                   '≥ 49° to the beam axis, so flanges, valves and pipe are harmless inside the cone r &lt; 1.1·|z|. A 1 mm stainless '
                   f'pipe crossing the arms would cost ×{th[6.0] / th[1.0]:.0f} (estimate).', sd.GREEN, 22),
        gap=14, w=600)
    D.slide('pitch-smear', sd.title('Beam-pipe scattering is the design driver; the 3D fit keeps it survivable',
                                    'Days to 3σ against the X17 resolution, for four fits with the same background-shape freedom (big plastics, calibrated response). Hover.')
            + sd.row(P.svg('days against smearing'), side, gap=36),
            """<p><code>lnl/sim/lnl_smear_nd.py</code> (FEASIBILITY_SIM §15): every event's reconstructed angle is moved away from its
Geant4 truth by a factor f (1, 2, 3.1, 6), so the residual distribution, tails included, scales by f: a stand-in for a thicker wall,
not a Geant4 run of one. f = 2 is close to Geant4's Al 0.5 mm chamber (9.0°); f = 6 is a Highland estimate of a 1 mm stainless tube
(x/X₀ 5.7 % against Al 1 mm's 1.1 % at 12.2°). Fits as the reference: calibrated response, S_θ 2 % + S_θy 1 % structure (ℓ = 10°),
arm gains, free acceptance cubic, θ-resolution scale ±10 %. The old counting estimate (§10: ×1.5 at 14.5°) assumed the IPC
shape known exactly; with the shape free the cost is much larger.</p>
<p>The cone rule: the Micromegas active area spans ±180 mm along the beam at 204 mm, so accepted leptons have polar angles
48.6°–131.4° from the beam axis and cross the plane |z| = Z at r ≥ 1.13·Z. They leave the 25 mm chamber within |z| ≤ 22 mm of
the target. Flanges, valves and the beam pipe are harmless if they stay inside that cone; a geometric estimate, to be checked
with the real LNL beam line in Geant4 (ask for the drawings).</p>""",
            foot='lnl/out/nd/smear_scan.csv (lnl/sim/lnl_smear_nd.py)', short='Smearing')


# --------------------------------------------------------------------------- #
def studies_slide(D, O, ctx):
    rows = [
        ['IPC angular shape beyond Born', 'M1–E1 interference and higher orders change B under the edge', 'fit with M1/E1 free: ×2.3–3 in time',
         'Zhang–Miller generator; off-resonance runs measure the E1 shape in data'],
        ['γ* anisotropy about the beam', 'reshapes the IPC by +3 to +10 % in the window', 'floated in the fit (a₁, a₂)',
         'asymmetric pairs and the 441 keV run as controls'],
        ['Acceptance against θ', 'detector structure under the edge', '1–2 % local from event mixing; the tilt is wrong',
         'take every single-arm trigger; event mixing; cosmic maps'],
        ['Target-region scattering', 'a wider edge looks like background structure', '1.0 → 2.5 d at 9°, 6.8 d at ~14°',
         'Geant4 with the real LNL chamber and beam line; a no-wall run'],
        ['5 cm plate response', 'sets |y|, E_sum and m_ee; the γ₁ leak', 'calibrated 1.0 d; n_TOF-quality 2.4 d; poor plates 5 d',
         'bench-test one plate: light yield, uniformity, linearity to 12 MeV'],
        ['IPC Monte Carlo statistics', 'template noise is 3–5 % per bin, as large as the δ scanned', 'as-built fits swing ×2–3 between MC halves',
         '×10 more IPC Monte Carlo (L7-type, above 70°)'],
        ['Contaminant lines', '¹¹B 16 MeV γ and its IPC; ¹⁹F singles; beam halo on the holder', 'not simulated',
         'Li₂O target; blank-backing and off-target runs (ask LNL)'],
        ['Signal normalisation', 'ATOMKI\'s E1 share and our generator differ ×2 on the visible excess', 'reach could be ×2 better',
         'reproduce PRL 116 Fig. 4 from their acceptance'],
    ]
    D.slide('pitch-studies', sd.title('What has to be studied: the background shape at the 1 % level, and the wall',
                                      'Each item: why it matters for S/B, how big it is today, and what pins it down. Ordered by how much each can move the answer.')
            + sd.table(['item', 'why it matters', 'size today', 'what pins it down'], rows, size=21, widths=[320, 470, 380, 494],
                       align=['left', 'left', 'left', 'left']),
            """<p>Sizes: FEASIBILITY_SIM §7 (M1/E1 free), §12.5 (MC statistics, normalisation), §13.2 (anisotropy), §13.3 (event mixing),
§14.2 (plate response), §15 (scattering). The Gaussian-process structure in the fit is a model of ignorance, not a measurement:
the first three rows are what would tell us whether 2 % + 1 % is the right size.</p>""",
            short='Studies')


# --------------------------------------------------------------------------- #
def unknowns_slide(D, ctx):
    def card(t, body, col, tip=None):
        return sd.card(f'<p style="font-size:25px;font-weight:600;color:{col}">{t}</p>'
                       f'<p style="font-size:21px;line-height:1.35">{body}</p>', tip=tip, pad=24)
    hi, mid, lo = sd.RED, sd.ORANGE, sd.GREY
    grid = [
        [card('Beam line and chamber at LNL (ask)', 'The thin carbon section must reach ±5 cm around the target, and nothing thick may '
              'enter the 49° cone. A 1 mm steel pipe there: ~×30 (estimate).', hi),
         card('Big-plate response (bench)', 'No data on 5 cm plates. Calibrated: 1 d; n_TOF-quality: 2.4 d; poor plates: 5 d.', hi),
         card('IPC shape (theory + data)', 'Born M1/E1 without interference today. The fit with the mix free is ×2–3 slower.', hi)],
        [card('Timing for the cosmic veto (measure)', 'TOF needs σ_t ≲ 0.4 ns per arm; 0.3 ns is assumed. Else 3° Micromegas segments.', mid),
         card('Hall space and mounting (ask)', 'A ~1.2 m cube around the target with ~1 m clearance; 32 kg plates on reworked frames.', mid),
         card('Scintillator DAQ (buy)', 'n_TOF read the scintillators on its own digitizers, which stay there. Next slide.', mid)],
        [card('Target (ask LNL)', 'Li₂O lifetime at 1 µA; ¹¹B and ¹⁹F contamination; the backing above 992 keV (²⁷Al(p,γ)).', lo),
         card('Beam time', 'LNL PAC, next call this autumn (ask); AN2000 is the LNL group\'s machine.', lo),
         card('The LNL 2023–24 result', 'Their AN2000 data may answer part of the question first. Talk to them: partners, not competitors.', lo)],
    ]
    D.slide('pitch-unknowns', sd.title('Open issues: the wall, the plates and the IPC shape matter most',
                                       'Red: can change the answer. Orange: can change the schedule. Grey: to arrange.')
            + sd.col(*[sd.row(*r, gap=24) for r in grid], gap=22),
            """<p>From FEASIBILITY_SIM §7 (timing, LS), §10 and §15 (wall), §14.2 (plates), §12.5 (IPC MC and normalisation), and
<code>lnl/FACILITY.md</code> (hall, PAC, the LNL group), <code>lnl/TARGETS.md</code> (target lines). Not simulated anywhere yet: ¹¹B
contamination, beam halo on the holder and flanges, the beam pipe beyond the chamber, M1–E1 interference.</p>""",
            short='Unknowns')


# --------------------------------------------------------------------------- #
def daq_slide(D, O, ctx):
    ch = pd.read_csv(O / 'trigger' / 'prescale_choice.csv')
    r1 = ch[(ch.hw == BP) & (ch.scenario == A16) & (ch.I_uA == 1.0)].iloc[0]
    r4 = ch[(ch.hw == BP) & (ch.scenario == A16) & (ch.I_uA == 4.0)].iloc[0]
    W, H = 760, 540
    o = []
    # SiPM side
    o.append(f'<rect x="10" y="20" width="330" height="200" rx="14" fill="{sd.PURPLE}" fill-opacity="0.12" stroke="{sd.PURPLE}" stroke-width="2"/>')
    o.append(sd.T(175, 60, '4 SiPM walls', 26, sd.PURPLE, weight=600))
    o.append(sd.T(175, 98, '20 bars × 2 ends = 40 ch/wall', 21, sd.INK))
    o.append(sd.T(175, 130, '160 ch (320 if two SiPMs per end)', 21, sd.INK))
    o.append(sd.T(175, 170, 'position + energy, ~0.6 MeV MIP', 20, sd.MUT))
    o.append(sd.T(175, 198, 'timing not needed', 20, sd.MUT))
    o.append(f'<rect x="420" y="20" width="330" height="200" rx="14" fill="{sd.GREEN}" fill-opacity="0.12" stroke="{sd.GREEN}" stroke-width="2"/>')
    o.append(sd.T(585, 60, '4 big plates', 26, sd.GREEN, weight=600))
    o.append(sd.T(585, 98, '2 × 3" PMTs each = 8 ch', 21, sd.INK))
    o.append(sd.T(585, 130, 'energy + the time (≲ 0.4 ns)', 21, sd.INK))
    o.append(sd.T(585, 170, 'the cosmic TOF and the', 20, sd.MUT))
    o.append(sd.T(585, 198, 'trigger legs', 20, sd.MUT))
    # boxes below
    o.append(f'<rect x="10" y="300" width="330" height="110" rx="14" fill="{sd.CARD}" stroke="{sd.PURPLE}" stroke-width="2"/>')
    o.append(sd.T(175, 345, 'slow, many-channel', 23, sd.INK, weight=600))
    o.append(sd.T(175, 380, 'FERS-5200 (Citiroc) or PETsys', 21, sd.MUT))
    o.append(f'<rect x="420" y="300" width="330" height="110" rx="14" fill="{sd.CARD}" stroke="{sd.GREEN}" stroke-width="2"/>')
    o.append(sd.T(585, 345, 'fast waveform digitizer', 23, sd.INK, weight=600))
    o.append(sd.T(585, 380, '16 ch, 500 MS/s–1 GS/s', 21, sd.MUT))
    o.append(sd.arrow(175, 222, 175, 296, sd.PURPLE, 3))
    o.append(sd.arrow(585, 222, 585, 296, sd.GREEN, 3))
    o.append(f'<rect x="215" y="460" width="330" height="90" rx="14" fill="{sd.CARD}" stroke="{sd.INK}" stroke-width="2"/>')
    o.append(sd.T(380, 498, 'N1081B trigger logic', 23, sd.INK, weight=600))
    o.append(sd.T(380, 530, 'PAIR · SINGLE/P · clock → DREAM', 20, sd.MUT))
    o.append(sd.arrow(585, 412, 470, 458, sd.GREEN, 3))
    o.append(sd.arrow(175, 412, 290, 458, sd.PURPLE, 2, 10))
    o.append(sd.T(150, 446, 'fast-OR (optional)', 18, sd.PURPLE))
    diag = sd.svg(W, H, ''.join(o), 'scintillator readout scheme')

    def k(t):
        return f'€{t[0]}k ({t[1]}–{t[2]})'
    fers320 = tuple(round(v * 5 / 3) for v in PRICE_FERS160)
    rows = [['<b>FERS-5200</b> A5202/A5204 + DT5215', '64 per unit: 3 units (160) or 5 (320)', 'ToA 0.5 ns LSB (Citiroc), picoTDC (A5204); bias included',
             f'{k(PRICE_FERS160)} / ~€{fers320[0]}k'],
            ['<b>PETsys</b> TOFPET2', '256 per system', '~30 ps binning, built for SiPM TOF', k(PRICE_PETSYS)],
            ['5 × <b>V1742</b> DRS4 + crate', '32 per board', 'full waveform; ~1 kHz dead-time limit', k(PRICE_V1742)],
            ['3 × <b>VX2745</b> (125 MS/s) + crate', '64 per board', 'marginal for sub-ns', k(PRICE_VX2745)],
            ['PMT digitizer (V1730-class)', '16', 'waveform, CFD timing', f'~€{DIGI_PER_PMT[0]}k per PMT channel']]
    D.slide('pitch-daq', sd.title('A slow DAQ for the SiPMs, the timing from the big plates',
                                  'Left: the readout. Right: the options and budgetary prices. The rates are low enough for any of them.')
            + sd.row(diag,
                     sd.col(sd.table(['option', 'channels', 'timing', 'cost'], rows, size=19, widths=[290, 210, 300, 180],
                                     align=['left', 'left', 'left', 'left']),
                            sd.callout(f'<b>Rates:</b> {r1.leg_per_s:.0f} arm legs/s, {r1.pair_per_s:.0f} pairs/s at 1 µA ({r4.leg_per_s:.0f} legs/s at 4 µA): '
                                       f'any option keeps up. DREAM (Micromegas, unchanged) sets the live time, {r1.live_P1 * 100:.0f} %.', sd.BLUE, 20),
                            sd.callout('<b>Recommended:</b> FERS-5200 for the SiPMs, one fast digitizer for the 8 plate PMTs, the existing '
                                       'N1081B logic: ~€30–40k (160 ch). The plates carry the timing.', sd.GREEN, 20),
                            sd.callout('<b>To confirm:</b> SiPMs per bar end (160 or 320 ch), the Citiroc range on one wall '
                                       '(~31 mV per end at the MIP), the plate timing on the cosmic bench.', sd.ORANGE, 20),
                            gap=14), gap=36),
            """<p>From <code>trigger_scint/TRIGGER_OPTIONS.md</code> §5 and <code>trigger_scint/costs.py</code> (budgetary EUR, 2026, no
labour or VAT; vendors quote on request). At n_TOF each wall recorded 8 channels (16 of 20 bars ganged in fours, each group summed
top and bottom) on the facility's ADQ14 digitizers, and the plastics and liquid on the same; none of those come with us. The study
counted one SiPM per bar end (4 walls × 20 bars × 2 ends = 160); if each end has two SiPMs read separately, it is 320 and the FERS
option needs 5 units (the price above scales by 5/3, a rough estimate). Ganging the two SiPMs of one end into one channel keeps it
at 160.</p>
<p>Timing: the toy ray-trace gives σ_t ≈ 120 ps at 5 MeV for a 78×80×5 cm plate with two 3" PMTs after the Micromegas position
correction (optimistic by ~1.5–2×), inside the ≲ 0.4 ns the cosmic veto needs (FEASIBILITY_SIM §7). If the plates give the TOF,
the SiPM wall's role in the trigger leg is the coincidence and the position; a plate-only leg would gain ~1.4× in X17 acceptance
but take more singles (§8 item 8). The FERS units have trigger-OR outputs, so the SiPM wall can stay in the leg if wanted.</p>
<p>Rates: <code>lnl/out/trigger/prescale_choice.csv</code> (big plastics, ATOMKI 2016 anomaly target, every single-arm trigger
taken, DREAM RAW 20 samples, τ = 298 µs).</p>""",
            short='DAQ')
