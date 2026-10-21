#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
target_rates.py -- what the fluorine of a LiF target does to the trigger, the
Micromegas and the DAQ, for MX17 (Geant4 singles libraries) and for an
LNL-2023-like ΔE-E telescope array (a toy).  (TARGET_STUDY.md §4)

    python lnl/target/target_rates.py           # -> lnl/out/target/rates_*.csv

Inputs
  * yields per proton from target_model.py (¹⁹F α_π pairs, ¹⁹F αγ γ, ⁸Be γ₀/γ₁);
  * the singles libraries (target/lxplus/target_singles.py) of the L3/L8 ¹⁹F
    γ-line runs and the L6/L8 6.05 MeV E0 pair runs: per event and arm the
    trigger-leg bit, the SiPM + plastic energy, the MM drift-gap charge;
  * cosmics: ~9-22 legs/s per arm from FEASIBILITY_SIM.md §4 (one number, 15/s);
  * DREAM: τ = 298 µs per event, non-paralysable; MM window 20 × 60 ns = 1.2 µs;
    two-arm coincidence 2τ = 20 ns (FEASIBILITY_SIM §4).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
LNL = HERE.parent
sys.path.insert(0, str(HERE))
import target_model as TM   # noqa: E402

OUT = LNL / 'out' / 'target'
SEL = HERE / 'sel'
TAU_DREAM = 298e-6
MM_WIN = 1.2e-6
TWO_TAU = 20e-9
TOF_KEEP = 0.6 / 20.0          # a 0.3 ns arm-to-arm TOF cut keeps ~3 % of 20 ns accidentals
T_INT = 100e-9                 # calorimeter integration time for energy pile-up
WINDOW = (13.0, 18.0)          # E_sum window (big plastics; as built 13-17)
COSMIC_LEGS = 15.0
ALPHA_8BE = 3.5e-3
LIBS = {
    'as built': dict(E0='L6_E0_6.05', gam='L3_gam_19F'),
    'big plastics': dict(E0='L8_E0_6.05_bigP', gam='L8_gam_19F_bigP'),
}


def lib_stats(name):
    f = SEL / f'{name}_singles.npz'
    if not f.exists():
        return None
    z = np.load(f)
    n = int(z['n_generated'][0])
    legs = z['legs'].astype(int)
    e = z['E_sipm'] + z['E_plast']
    out = dict(n=n,
               p_leg_arm=np.mean([((legs >> a) & 1).sum() / n for a in range(4)]),
               p_leg_any=((legs & 0xF) != 0).sum() / n,
               p_leg_2arm=(np.array([bin(x & 0xF).count('1') for x in legs]) >= 2).sum() / n,
               p_mm_arm=np.mean([(z['seg_e'][:, a] > 0).sum() / n for a in range(4)]))
    # energy of a leg (MeV): its distribution, for pile-up
    el = np.concatenate([e[((legs >> a) & 1) == 1, a] for a in range(4)])
    out['E_leg'] = el
    out['E_leg_max'] = float(el.max()) if len(el) else 0.0
    return out


def mx17_rates(scen: pd.DataFrame, I_list=(0.8, 1.0, 4.0)) -> pd.DataFrame:
    rows = []
    for hw, lib in LIBS.items():
        sE0, sg = lib_stats(lib['E0']), lib_stats(lib['gam'])
        if sE0 is None or sg is None:
            print(f'skip {hw}: singles library missing')
            continue
        for _, r in scen.iterrows():
            for I in I_list:
                pps = I * 1e-6 / TM.E_CH
                Rg, Rp = r.Y_F_gamma * pps, r.Y_F_pairs * pps
                R8 = (r.Y_g0 + r.Y_g1) * pps
                legs_F = Rg * sg['p_leg_arm'] + Rp * sE0['p_leg_arm']
                legs_8 = R8 * 0.0039 / 4                           # §4: 0.39 % of ⁸Be γ make a leg somewhere
                R_arm = legs_F + legs_8 + COSMIC_LEGS
                acc2 = 6 * TWO_TAU * R_arm ** 2                    # two-arm accidental triggers /s (6 arm pairs)
                mm_trk = Rg * sg['p_mm_arm'] + Rp * sE0['p_mm_arm']
                occ = 1 - np.exp(-mm_trk * MM_WIN)                # P(extra track in an arm's readout window)
                # singles prescale needed to keep DREAM ≥ 90 % live with the pair triggers unprescaled
                pairs_trig = acc2 + 22.0 * I                       # §4: ~22 two-arm /s big plastics (cosmic-dominated)
                P = 1
                while 1 / (1 + (4 * R_arm / P + pairs_trig) * TAU_DREAM) < 0.9 and P < 1e6:
                    P *= 2
                live = 1 / (1 + (4 * R_arm / P + pairs_trig) * TAU_DREAM)
                # accidental two-arm events whose E_sum lands in the window: two ¹⁹F/⁸Be legs, or
                # two legs plus a third hit piling up in one arm within T_INT
                fF = legs_F / R_arm
                pool = np.concatenate([sg['E_leg'], sE0['E_leg']])
                wpool = np.concatenate([np.full(len(sg['E_leg']), Rg * sg['p_leg_arm'] / len(sg['E_leg'])),
                                        np.full(len(sE0['E_leg']), Rp * sE0['p_leg_arm'] / len(sE0['E_leg']))])
                in2 = in3 = 0.0
                if wpool.sum() > 0:
                    rng = np.random.default_rng(3)
                    e2 = rng.choice(pool, (400_000, 3), p=wpool / wpool.sum())
                    in2 = ((e2[:, 0] + e2[:, 1] > WINDOW[0]) & (e2[:, 0] + e2[:, 1] < WINDOW[1])).mean()
                    in3 = ((e2.sum(1) > WINDOW[0]) & (e2.sum(1) < WINDOW[1])).mean()
                acc2F = 6 * TWO_TAU * legs_F ** 2
                win2 = acc2F * in2
                win3 = acc2F * 2 * legs_F * T_INT * in3
                tri = (win2 + win3) * TOF_KEEP * 86400
                rows.append(dict(hw=hw, scenario=r.scenario, I_uA=I, R_8Be_gamma=R8, R_F_gamma=Rg, R_F_pairs=Rp,
                                 F_legs_per_arm=legs_F, legs_per_arm_total=R_arm, two_arm_accidentals=acc2,
                                 mm_tracks_per_arm=mm_trk, mm_extra_track_prob=occ, prescale_for_90pc_live=P,
                                 dream_live=live, F_acc_in_window_per_day_afterTOF=tri,
                                 F_acc_in_window_per_day_noTOF=(win2 + win3) * 86400,
                                 F_leg_Emax_MeV=max(sE0['E_leg_max'], sg['E_leg_max'])))
    return pd.DataFrame(rows)


def lnl_like_toy(scen: pd.DataFrame, I=0.8) -> pd.DataFrame:
    """An LNL-2023-like array: 4 clovers, 10 × 10 cm faces at 12.75 cm, ΔE (2 × 2 mm
    bars) + 10 cm E blocks, triple coincidence per telescope (GS25).  A lepton above
    ~1 MeV passes the triple coincidence; a γ does so with ε ≈ 6×10⁻⁴ per clover
    hit (Marchi 2021, slide 14); a 6-7 MeV γ deposits something in the E block with
    ~30 %.  Pair acceptance for two clovers: 1.2 % for 18 MeV IPC (Marchi 2021,
    slide 20); for 6.05 MeV E0 pairs we take 3 % × 0.64 (both leptons > 1 MeV), as
    E0 pairs are wide-angle.  Everything here is a TOY, to ×2."""
    om = 100.0 / (4 * np.pi * 12.75 ** 2)
    pps = I * 1e-6 / TM.E_CH
    rows = []
    for _, r in scen.iterrows():
        Rg, Rp, R8 = r.Y_F_gamma * pps, r.Y_F_pairs * pps, (r.Y_g0 + r.Y_g1) * pps
        hits_clover = Rp * 2 * om * 0.8 + Rg * om * 0.30          # anything in a clover
        trig_clover = Rp * 2 * om * 0.8 + Rg * om * 6e-4           # triple coincidences
        e0_coinc = Rp * 0.03 * 0.64
        be_coinc = ALPHA_8BE * R8 * 0.012
        rows.append(dict(scenario=r.scenario, I_uA=I, R_F_pairs=Rp, R_F_gamma=Rg, R_8Be_pairs=ALPHA_8BE * R8,
                         clover_hits_per_s=hits_clover, clover_triples_per_s=trig_clover,
                         two_clover_E0_per_s=e0_coinc, two_clover_8Be_per_s=be_coinc,
                         E0_over_8Be_coinc=e0_coinc / be_coinc if be_coinc else np.nan,
                         pileup_prob_100ns=hits_clover * 100e-9))
    return pd.DataFrame(rows)


def main():
    sc = pd.read_csv(OUT / 'scenarios.csv')
    pick = sc[sc.scenario.str.contains('LNL 2023|MX17 candidate|ATOMKI 2022, Li2O|Hanoi 2024, LiF')]
    t = mx17_rates(pick)
    t.to_csv(OUT / 'rates_mx17.csv', index=False)
    with pd.option_context('display.width', 250, 'display.max_columns', 30, 'display.max_colwidth', 45):
        print(t[['hw', 'scenario', 'I_uA', 'R_F_pairs', 'R_F_gamma', 'F_legs_per_arm', 'two_arm_accidentals',
                 'mm_extra_track_prob', 'prescale_for_90pc_live', 'dream_live', 'F_acc_in_window_per_day_noTOF',
                 'F_acc_in_window_per_day_afterTOF',
                 'F_leg_Emax_MeV']].to_string(float_format=lambda v: f'{v:.3g}'))
    toy = lnl_like_toy(pick)
    toy.to_csv(OUT / 'rates_lnl_like.csv', index=False)
    with pd.option_context('display.width', 250, 'display.max_columns', 30, 'display.max_colwidth', 45):
        print(toy.to_string(float_format=lambda v: f'{v:.3g}'))


if __name__ == '__main__':
    main()
