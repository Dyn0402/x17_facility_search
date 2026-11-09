#!/usr/bin/env python3
"""dd_figs.py -- the two study figures (reach vs distance, close-coupling geometry), each with its .csv."""
import sys
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'ill'))
import figstyle as fs
import matplotlib.pyplot as plt
fs.use()
O = HERE / 'out'
t = pd.read_csv(O / 'dd_reach.csv')
q = t[(t.days == 50) & (t.model == 'full') & (t.shield == 'shadow') & (t.hw == 'big plastics')]
SRC = [('phoenix_3e11', 'Phoenix 3×10¹¹ (measured), 90°', fs.ACCENT), ('phoenix_135', 'Phoenix 3×10¹¹, 135°', fs.COPPER),
       ('need_1e12', '1×10¹² (hypothetical)', fs.TRACK), ('dacc_1p5_5mA_135', 'd 1.5 MeV, 5 mA, gas, 135° (hypothetical)', fs.MUTED),
       ('adelphi_1e10', '1×10¹⁰ compact (Adelphi class)', 'k')]
fig, ax = plt.subplots(figsize=(8, 4.6))
for k, lab, c in SRC:
    x = q[q.source == k].sort_values('d_cm')
    ax.plot(x.d_cm, x.rho3, 'o-', color=c, label=lab)
ax.axhline(1.5e-3, color='gray', ls='--', lw=1); ax.text(16, 1.6e-3, 'ATOMKI ⁴He 1.5×10⁻³', fontsize=8)
ax.axhline(5.5e-4, color='gray', ls=':', lw=1); ax.text(16, 3.9e-4, 'Birmingham 5.5×10⁻⁴ (full Geant4)', fontsize=8)
ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlabel('source to cell front d [cm]'); ax.set_ylabel('X17/IPC at 3σ, 50 d, big plastics')
ax.legend(frameon=False, fontsize=8)
fs.fig_title(fig, 'D-D sources: reach against source distance (shadow shield, ESTIMATE arm and room terms)',
             '30 bar × 40 cm cell; shield allowed only upstream of the cell front plane')
fs.save(fig, O / 'dd_reach_vs_d', data=q[['source', 'd_cm', 'rho3', 'rho3_floor', 'live', 'throttle']])
g = pd.read_csv(O / 'dd_geometry.csv')
fig, axs = plt.subplots(1, 2, figsize=(10, 4))
axs[0].plot(g.d_cm, g.G_over_naive_frontface, 'o-', color=fs.ACCENT, label='G / naive at front face')
axs[0].plot(g.d_cm, g.G_over_naive_center, 'o-', color=fs.COPPER, label='G / naive at cell centre')
axs[0].axhline(1, color='gray', ls='--', lw=1); axs[0].set_xscale('log'); axs[0].set_xlabel('d [cm]'); axs[0].set_ylabel('close-coupling correction')
axs[0].legend(frameon=False, fontsize=8)
axs[1].plot(g.d_cm, g.arm_T_shadow, 'o-', color=fs.ACCENT, label='TVL 12 cm'); axs[1].plot(g.d_cm, g.arm_T_tvl_8, 'o-', color=fs.TRACK, label='TVL 8 cm')
axs[1].plot(g.d_cm, g.arm_T_tvl_20, 'o-', color=fs.MUTED, label='TVL 20 cm')
axs[1].set_xscale('log'); axs[1].set_yscale('log'); axs[1].set_xlabel('d [cm]'); axs[1].set_ylabel('shadow-shield transmission to the arms'); axs[1].legend(frameon=False, fontsize=8)
fs.fig_title(fig, 'Close coupling: the Ø8 cm spot assumption, and what shield fits', 'G = (1/L)∫dV/4πr²; the shield may only sit upstream of the cell (keep-out for the tracks)')
fs.save(fig, O / 'dd_geometry', data=g)
