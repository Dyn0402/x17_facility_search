#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
opt_practical.py -- can each LNL target design actually be built?  TARGET_OPTIONS.md §21.  For every design of the
comparison deck (lnl-target-compare, keys of build_compare_deck.DES): what holds 1 bar and with what margin, how hot
the Li runs through the real heat path, which parts must be bought, from whom, at what cost and lead time, and what
safety or other gate stands in the way.  Physics (Geant4 days per µA) stays in the deck; this file is the practical
half.  Everything here is ESTIMATE: closed-form shell and plate formulas, 1D heat paths, and cost / lead-time ranges
from public prices and quotes (sources in §21) -- ask for real quotes before ordering.

    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/opt_practical.py

Writes out/target/options/practical.csv (one row per design), practical_parts.csv (the bill of parts) and
practical_checks.csv (every 1 bar and heat check behind the rows).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import opt_shapes as SH            # noqa: E402
import opt_shell_material as SM    # noqa: E402

OUT = SH.OUT
P_BAR = 0.1013                      # MPa
KNOCK_CYL, KNOCK_SPH = 0.56, 0.2    # buckling knockdowns: SP-8007 cylinders / cones; spheres (SP-8032 range 0.14–0.3)
H_AIR = 100.0                       # W/m²/K, a fan on the outside (§17, §20)
I_CHECK = 4.0                       # µA: LNL's ceiling; the 20 µm Li runs at 0.12–0.5 µA (§5)
EP = 1.10                           # MeV (the deck's energy)
DIA_STRENGTH = (280., 690.)         # MPa, CVD diamond, growth / nucleation side in tension (membrane burst tests)
MATS = {**SM.MAT,
        'CFRP (hoop)': dict(E=50., nu=0.30, sy=500., k=5., alpha=2., X0=267.),       # quasi-isotropic layup, ESTIMATE
        'Ti grade 2': SM.MAT['Ti grade 2']}


# ---- 1 bar ------------------------------------------------------------------------------------------------
def cyl_buckle_bar(m, r_mm, t_mm, L_mm):
    """external-pressure buckling of a tube with held ends: Windenburg–Trilling (short) or the long-tube limit
    2E/(1−ν²)(t/D)³, whichever is larger, × the SP-8007 knockdown.  bar."""
    E, nu, D = m['E'] * 1e3, m['nu'], 2 * r_mm
    wt = 2.42 * E / (1 - nu ** 2) ** 0.75 * (t_mm / D) ** 2.5 / max(L_mm / D - 0.45 * (t_mm / D) ** 0.5, 1e-3)
    lg = 2 * E / (1 - nu ** 2) * (t_mm / D) ** 3
    return 10 * KNOCK_CYL * max(wt, lg)


def sph_buckle_bar(m, R_mm, t_mm):
    E, nu = m['E'] * 1e3, m['nu']
    return 10 * KNOCK_SPH * 2 * E / np.sqrt(3 * (1 - nu ** 2)) * (t_mm / R_mm) ** 2


def diamond_margin(t_um, a_mm):
    e, c, y = SH.plate_stress(t_um, a_mm)
    return e, DIA_STRENGTH[0] / e, DIA_STRENGTH[1] / e


# ---- heat: chains of 1D paths, each a temperature rise for the beam power Q -----------------------------------
def tube_fin(m, r_mm, t_mm, L_mm, h=H_AIR):
    """thermal resistance [K/W] of a thin tube carrying heat from its free end to a base held at the air, cooled by
    air on its outside along the way (a straight fin): 1/(k A m tanh(mL)), m = √(h/(k t))."""
    k, t, r, L = m['k'], t_mm * 1e-3, r_mm * 1e-3, L_mm * 1e-3
    A = 2 * np.pi * r * t
    mm = np.sqrt(h / (k * t))
    return 1 / (k * A * mm * np.tanh(mm * L))


def annulus(k, t_mm, r1_mm, r2_mm):
    return np.log(r2_mm / r1_mm) / (2 * np.pi * k * t_mm * 1e-3)


def glue(w_mm, r_mm, t_mm=0.1, k=0.5):
    """an epoxy line of thickness t over a collar of width w at radius r: K/W"""
    return t_mm * 1e-3 / (k * 2 * np.pi * r_mm * 1e-3 * w_mm * 1e-3)


def window_chain(t_um, tilt, tube, r_tube=10.0, t_tube=0.5, L_tube=55.0, plate=None, joint='glue'):
    """Li peak rise above the air for the diamond window: the disc (Gaussian spot, cooled at its rim and on its outer
    face by air), two 0.5 mm Ti rings 5 mm wide (radial conduction), the ring → end-piece joint, then the end piece as
    a fin to the line.  Returns (total K, dict of parts)."""
    Q = EP * I_CHECK
    sig = 2.0 * (2 ** 0.25 if tilt else 1.0)
    a = 10.0 * (1.19 if tilt else 1.0)
    disc = SH.shell_temp(1800 * t_um * 1e-6 + 138 * 8e-6, H_AIR, P=Q, sigma=sig, Rarc=a, T_edge=0.0)
    ring = annulus(MATS['Ti grade 2']['k'], 1.0, 10.0, 15.0) * Q
    jt = (glue(5.0, 12.5) if joint == 'glue' else 0.05) * Q
    parts = dict(disc=disc, Ti_rings=ring, joint=jt)
    if plate is not None:                                     # wide adapter: 2 mm Al plate r 12.5 → 30
        parts['Al_plate'] = annulus(MATS['Al 6061-T6']['k'], plate, 12.5, 30.0) * Q
    parts['end_piece'] = tube_fin(MATS[tube], r_tube, t_tube, L_tube) * Q
    return sum(parts.values()), parts


def checks():
    """every 1 bar and heat check, per design key."""
    Be, Al, Cu, Ti, CF = (MATS[k] for k in ('Be S-200FH', 'Al 6061-T6', 'Cu OFHC ann.', 'Ti grade 2', 'CFRP (hoop)'))
    rows = []

    def add(key, what, value, unit, margin=np.nan, note='', tag='both'):
        """tag: 'sim' = the geometry Geant4 ran, 'rec' = the variant recommended to build, 'both', or '' (other)"""
        rows.append(dict(key=key, check=what, value=value, unit=unit, margin=margin, note=note, tag=tag))

    # flat: the target sits inside a CFRP chamber, which is the vacuum wall
    for t, L in ((0.4, 600), (0.4, 300), (0.6, 300), (1.0, 600), (1.0, 300)):
        b = cyl_buckle_bar(CF, 25.0, t, L)
        add('flat', f'CFRP chamber r 25, wall {t} mm, {L} mm long: buckling', b, 'bar', b / 1.013,
            'as simulated in L9' if (t, L) == (0.4, 600) else '',
            tag={(0.4, 600): 'sim', (1.0, 300): 'rec'}.get((t, L), ''))
    add('flat', 'Li rise at 4 µA (Li/Mo/diamond 50, clamped holder, §3 option D)', 15.0, 'K', np.nan,
        'holder clamp held at ambient; the Cu arm to the flange adds ~5–15 K (ESTIMATE)')
    # windows
    for k2 in ('w45', 'w0', 'w45be', 'w45wide'):
        for t in (200, 300):
            e, m0, m1 = diamond_margin(t, 10.0)
            add(k2, f'diamond {t} µm over Ø20, 1 bar: edge stress', e, 'MPa', m0,
                f'margin {m0:.1f} (growth side in tension) – {m1:.1f} (nucleation side)', tag='sim' if t == 200 else 'rec')
    for key, tube, t_tube in (('w45', 'Al 6061-T6', 0.5), ('w45be', 'Be S-200FH', 0.5)):
        b = cyl_buckle_bar(MATS[tube], 10.0, t_tube, 55.0)
        add(key, f'{tube} end piece r 10 × {t_tube} × 55 mm: buckling', b, 'bar', b / 1.013)
    for key, tilt, tube, plate, r_tube, L in (('w45', True, 'Al 6061-T6', None, 10.0, 55.0),
                                              ('w45be', True, 'Be S-200FH', None, 10.0, 55.0),
                                              ('w0', False, 'Al 6061-T6', None, 10.0, 55.0),
                                              ('w45wide', True, 'Al 6061-T6', 2.0, 30.0, 60.0)):
        for joint in ('glue', 'braze'):
            T, parts = window_chain(300, tilt, tube, r_tube=r_tube, L_tube=L, plate=plate, joint=joint)
            add(key, f'Li rise at 4 µA, ring {joint}d to the end piece', T, 'K', np.nan,
                ', '.join(f'{k} {v:.0f}' for k, v in parts.items()), tag='rec' if joint == 'glue' else '')
    b = cyl_buckle_bar(Al, 30.0, 0.5, 60.0)
    add('w45wide', 'Al tube r 30 × 0.5 × 60 mm: buckling', b, 'bar', b / 1.013)
    s = 0.75 * P_BAR * 30.0 ** 2 / 2.0 ** 2
    add('w45wide', 'Al plate 2 mm, r 10–30, 1 bar: bending stress', s, 'MPa', Al['sy'] / s)
    # hemispheres, R 11
    for key, m, t, lab in (('hemi', Cu, 0.2, 'Cu 200 µm'), ('hemi', Cu, 0.3, 'Cu 300 µm (the CN cup)'),
                           ('hemibe', Be, 0.2, 'Be 200 µm')):
        b = sph_buckle_bar(m, 11.0, t)
        sg = P_BAR * 11.0 / (2 * t)
        tg = '' if t == 0.3 else 'both'
        add(key, f'{lab} hemisphere R 11: buckling', b, 'bar', b / 1.013, tag=tg)
        add(key, f'{lab} hemisphere R 11: membrane stress pR/2t', sg, 'MPa', m['sy'] / sg, tag=tg)
    for key, k_w, t in (('hemi', Cu['k'], 0.2), ('hemibe', Be['k'], 0.2)):
        kt = k_w * t * 1e-3 + (138 * 8e-6 if key == 'hemibe' else 0)
        T = SH.shell_temp(kt, H_AIR, P=EP * I_CHECK, sigma=2.0, Rarc=np.pi / 2 * 11.0, T_edge=10.0)
        add(key, 'Li rise at 4 µA (shell fin, rim 10 K above the air)', T, 'K', tag='both')
    # ogives (§20)
    for key, name, t in (('ogcu', 'Cu OFHC ann.', 0.2), ('ogbe', 'Be S-200FH', 0.3), ('ogbe', 'Be S-200FH', 0.2),
                         ('ogal', 'Al 6061-T6', 0.3), ('ogal', 'Al 6061-T6', 0.2)):
        m = SM.MAT[name]
        pr = SM.pressure(m, t)
        tg = 'both' if key == 'ogcu' else 'rec' if t == 0.3 else 'sim'
        add(key, f'{name} ogive {t * 1000:.0f} µm: buckling', pr['buckle_bar'], 'bar', pr['buckle_bar'] / 1.013, tag=tg)
        add(key, f'{name} ogive {t * 1000:.0f} µm: clamped-base stress', pr['clamp_MPa'], 'MPa', m['sy'] / pr['clamp_MPa'], tag=tg)
        kt = m['k'] * t * 1e-3 + (SM.K_MO * SM.T_MO if key != 'ogcu' else 0)
        T = SM.tip_heat(kt, H_AIR, I_CHECK * EP / SM.EP_MEV)[2][0] + 10.0
        add(key, f'Li rise at 4 µA, {t * 1000:.0f} µm (fin along the meridian, base joint +10 K)', T, 'K', tag=tg)
    return pd.DataFrame(rows)


# ---- what has to be bought or made (ESTIMATE ranges: k€ per first unit, weeks) -----------------------------------
# who: LNL = LNL workshop / thin-film lab; V-dia = CVD-diamond window vendor (Diamond Materials, Element Six, Coherent);
# V-Be = Be shop (Materion, IBC); V-CF = composite tube maker.
PARTS = {
    'dia300': ('CVD diamond Ø20–25 × 0.3 mm, thermal grade, brazed into two 0.5 mm Ti rings', 'V-dia', 3, 8, 8, 14),
    'dia50': ('free-standing CVD diamond Ø40 × 50 µm (fragile; handle on a frame)', 'V-dia', 2, 5, 8, 14),
    'mo_flat': ('Mo 8 µm sputtered on the diamond (flat)', 'LNL / V-dia', 0.5, 2, 2, 6),
    'mo_in': ('Mo 8 µm sputtered inside the shell, at least on the tip / cap', 'LNL thin-film lab', 0.5, 2, 3, 8),
    'al_end': ('Al end piece Ø20 × 0.5 × 55 mm cut on the window plane, Al reducer', 'LNL', 0.3, 1, 2, 4),
    'be_end': ('Be end piece Ø20 × 0.5 × 55 mm with brazed Ti/SS transitions (window ring, flange)', 'V-Be', 8, 25, 12, 26),
    'wide': ('wide adapter: 2 mm Al plate r 10–30 in the window plane + r 30 × 0.5 mm Al tube', 'LNL', 0.5, 1.5, 3, 6),
    'cfrp': ('CFRP chamber r 25, ≥ 1 mm wall, Al flanges glued, inner coating, leak test', 'V-CF + LNL', 2, 6, 6, 12),
    'holder': ('Cu holder ring, cooled arm and feed-through inside the chamber', 'LNL', 1, 3, 4, 8),
    'cu_cup': ('Cu cup R 11 × 0.2–0.3 mm (exists: CN paper; more pressed / spun at LNL)', 'LNL', 0, 0.5, 0, 3),
    'be_cup': ('Be hemisphere R 11 × 0.2 mm with an integral collar, bonded into a Ti/SS ring', 'V-Be', 5, 20, 12, 26),
    'cu_og': ('Cu ogive 0.2 mm, electroformed or spun on a mandrel', 'LNL / electroformer', 1, 3, 3, 8),
    'be_og': ('Be ogive 0.3 mm (machined + etched) with an integral collar, bonded into a Ti/SS CF ring', 'V-Be', 8, 30, 12, 26),
    'al_og': ('Al 6061-T6 ogive 0.3 mm, CNC on a mandrel; Li evaporated through a mask onto the tip only', 'LNL', 0.5, 1.5, 3, 6),
    'og_adapt': ('Ø50 → DN40 adapter at the ogive base (out of the arms\' view)', 'LNL', 0.3, 1, 2, 4),
    'grey': ('existing grey flange / DN40 line (PF\'s)', 'LNL', 0, 0, 0, 0),
}
COMMON = ('Li evaporation (LNL, every design); a fast-closing valve upstream (~5–10 k€ if LNL has none: in every design '
          'a crack vents the line, since the target or its chamber is the vacuum wall); 2–3 spare targets per campaign.')

DESIGN = {   # key: parts, difficulty 1–5, the gate, failure mode, what to do first
    'flat': (['dia50', 'mo_flat', 'holder', 'cfrp'], 3, 'none',
             'chamber collapse (CFRP) vents the line; the target itself is not loaded',
             'the L9 chamber (0.4 mm, 600 mm) buckles at ~0.3 bar: make it ≥ 1 mm and ≤ 300 mm, or ribbed'),
    'w45': (['dia300', 'mo_flat', 'al_end', 'grey'], 2, 'none',
            'diamond crack or Mo blistering vents the line (window = beam stop = vacuum wall)',
            'order 300 µm, not 200 µm diamond: ×2 margin at 1 bar for +0.01 d/µA'),
    'w45be': (['dia300', 'mo_flat', 'be_end', 'grey'], 4, 'Be: LNL safety (RSPP) approval; Be shop quote',
              'as w45, plus Be fragments in the line if it breaks',
              'quote the Be end piece; ask RSPP early'),
    'w45wide': (['dia300', 'mo_flat', 'wide', 'grey'], 2, 'none',
                'as w45', 'machine the plate in the window plane; glue or braze the ring to the plate'),
    'w0': (['dia300', 'mo_flat', 'al_end', 'grey'], 1, 'none', 'as w45', 'simplest window to make and align'),
    'hemi': (['cu_cup', 'grey'], 1, 'none', 'Cu blisters where the beam stops (~5 d at 1 µA, §5): a consumable',
             'exists today; can serve as the commissioning target'),
    'hemibe': (['be_cup', 'mo_in', 'grey'], 4, 'Be: RSPP approval; Be shop quote',
               'brittle: a crack vents the line and leaves Be fragments', 'quote it with the ogive'),
    'ogcu': (['cu_og', 'og_adapt'], 2, 'none', 'as hemi (Cu blisters)', 'electroform on a mandrel: the natural way to make it'),
    'ogbe': (['be_og', 'mo_in', 'og_adapt'], 5, 'Be: RSPP approval; Be shop quote (deep thin shell, at the edge of what shops do)',
             'brittle: a crack vents the line and leaves Be fragments', '0.3 mm wall; quote with the STEP'),
    'ogal': (['al_og', 'mo_in', 'og_adapt'], 2, 'none',
             'Li alloys with Al where it touches: mask the Li to the Mo-coated tip', '0.3–0.4 mm wall (0.2 mm buckles at 1.8 bar)'),
}


def flat_chamber_trace():
    """what a buildable chamber costs the flat design: the §17 trace of L9's flat target with a CFRP chamber of 0.4
    (as simulated), 0.6 and 1.0 mm.  σ68 via the same calibration as opt_sketch (ESTIMATE)."""
    V, U, T = SH.legs()
    tr = pd.read_csv(OUT / 'shapes_trace.csv')
    cal = tr[tr.kind.str.startswith('flat')]
    A = np.c_[np.ones(len(cal)), cal.sig_ms ** 2]
    (s2, k2), *_ = np.linalg.lstsq(A, cal.sigma68_g4 ** 2, rcond=None)
    rows = []
    for t in (0.4, 0.6, 1.0):
        ch = [SH.Solid('CFRP', [SH.S(SH.cyl, SH.Y, 25.0 + t), SH.S(SH.slab, SH.Y, -300, 300)], [SH.S(SH.cyl, SH.Y, 25.0)])]
        geo = SH.flat([('Mo', 8), ('Dia', 50)], 2, chamber=False) + ch
        r = SH.trace(geo, V, U, T, SH.on_film)
        rows.append(dict(chamber_mm=t, x_med_pct=100 * r['x_med'], sigma68_trace=float(np.sqrt(s2 + k2 * r['sig_ms'] ** 2)),
                         p_conv=r['p_conv']))
    return pd.DataFrame(rows)


def main():
    pd.set_option('display.width', 250)
    pd.set_option('display.max_colwidth', 90)
    ck = checks()
    ck.to_csv(OUT / 'practical_checks.csv', index=False)
    print(ck.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    prow, rows = [], []
    for key, (parts, diff, gate, fail, first) in DESIGN.items():
        lo = sum(PARTS[p][2] for p in parts)
        hi = sum(PARTS[p][3] for p in parts)
        wk_lo = max(PARTS[p][4] for p in parts)
        wk_hi = max(PARTS[p][5] for p in parts)
        for p in parts:
            prow.append(dict(key=key, part=PARTS[p][0], who=PARTS[p][1], keur_lo=PARTS[p][2], keur_hi=PARTS[p][3],
                             weeks_lo=PARTS[p][4], weeks_hi=PARTS[p][5]))
        c = ck[ck.key == key]
        mech = c[c.unit.isin(['bar', 'MPa']) & c.margin.notna()]
        heat = c[(c.unit == 'K') & c.tag.isin(['rec', 'both'])].value

        def gov(tags):                                        # the governing (smallest) 1 bar margin of a variant
            q = mech[mech.tag.isin(tags)]
            return (float(q.margin.min()), q.loc[q.margin.idxmin(), 'check']) if len(q) else (np.nan, '')
        ms, cs = gov(['sim', 'both'])
        mr, cr = gov(['rec', 'both'])
        rows.append(dict(key=key, keur_lo=lo, keur_hi=hi, weeks_lo=wk_lo, weeks_hi=wk_hi, difficulty=diff, gate=gate,
                         failure=fail, first=first, margin_sim=ms, margin_sim_check=cs, margin_rec=mr, margin_rec_check=cr,
                         dT_4uA=float(heat.max()) if len(heat) else np.nan))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / 'practical.csv', index=False)
    pd.DataFrame(prow).to_csv(OUT / 'practical_parts.csv', index=False)
    print()
    print(df.drop(columns=['failure', 'first', 'gate']).to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    print('\ncommon to all:', COMMON)
    fc = flat_chamber_trace()
    fc.to_csv(OUT / 'practical_flat_chamber.csv', index=False)
    print(fc.to_string(index=False, float_format=lambda v: f'{v:.3g}'))


if __name__ == '__main__':
    main()
