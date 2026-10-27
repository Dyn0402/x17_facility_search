#!/usr/bin/env python3
"""
bham_common.py -- shared pieces of the Birmingham target study (TARGET_GEANT.md): the source, the targets,
the Geant4 tables and the per-row rates.

The facility case (§1): 2.8 MeV protons at 30 mA on the thick Li, the cell centre 2 m from the Li, 5 cm of Pb
in the collimator bore (uncollided transmission: n 0.37, 478 keV 1.5×10⁻⁴, 15-18 MeV 0.058).

Geant4 tables (fetch_sel.sh → sel/):
  B1_<X17|E1|M1>_En0.5_<target>_<det>_sel.npz   pairs (nfs_merge.py + lnl_time.py)
  B2_n_<target>_<det>_sel.npz / _chan.npz        beam neutrons, flat 0.01-1.3 MeV, forced first collision
  B3_<g478|g8be>_<target>_<det>_sel.npz / _chan  beam photons
  R3_<n|g8be|g478>_c30_<det>_sel.npz / _chan     the same beam into the experimental room (wall, dump, concrete)
  R2_leak_<n|g>src_<n|g>_<det>_sel.npz / _chan   what leaks through the wall (the 4π source, staged)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BHAM = HERE.parent
ROOT = BHAM.parent
SEL = HERE / 'sel'
OUT = BHAM / 'out' / 'geant'
LSEL = ROOT / 'lnl' / 'sim' / 'sel_v3'
for p in (BHAM, ROOT / 'survey', ROOT / 'lnl' / 'sim', ROOT / 'lnl', ROOT / 'ill', ROOT / 'ganil_nfs' / 'sim',
          Path.home() / 'PycharmProjects' / 'nTof_x17'):
    sys.path.insert(0, str(p))
import bham_beam as BB          # noqa: E402
import bham_targets as BT       # noqa: E402

DAY = 86400.0
EP, CURRENT, DIST_M = 2.8, 30e-3, 2.0
P_PER_S = CURRENT / BB.E_CHARGE
PB_CM = 5.0
MU_PB = {'n': 0.20, 'g478': 1.76, 'g15': 0.57}                 # /cm (soft_reach.py)
RHO_REF = 1.5e-3                                              # X17/IPC(E1), ATOMKI ⁴He (pessimistic)
DETS = {'bigP': 'big plastics', 'asb': 'as built'}
TARGETS = list(BT.TARGETS)
LABEL = {k: v[0] for k, v in BT.TARGETS.items()}
GAS_Y = {'cap500': (-30.0, 30.0)}                              # vertex clip [mm]; cells: ±200
ROOM_VOLS = ('Room_', 'BeamDump_Room', 'Shield_')
E_GRID = np.linspace(0.005, 20.0, 8000)
GEN = {'n': ('flat', 0.01, 1.3), 'g478': ('line', 0.4775, 0.4785), 'g8be': ('flat', 14.0, 19.0)}
LINES_8BE = [(17.64, 0.6 / 3), (18.15, 0.4 / 3), (14.64, 1.2 / 3), (15.15, 0.8 / 3)]
SRC_N_PER_P = 1.9614e-4                                       # bham_beam.src_tables(2.8): n per proton (4π)


def beam_area(t):
    return BT.TARGETS[t][5] ** 2 * np.pi                       # cm²


def source_rates(t, pb_cm=PB_CM):
    """per beam particle kind: (rate through the target's beam spot [1/s], normalised pdf on E_GRID)."""
    b, _ = BB.beam(EP, CURRENT, DIST_M)
    A = beam_area(t)
    om = A / (DIST_M * 100) ** 2 / (4 * np.pi)
    fn = BB.spectrum_on_grid(EP, E_GRID)
    n = b['flux_at_cell'] * A * np.exp(-MU_PB['n'] * pb_cm)
    g478 = (6e-5 * P_PER_S + 6e11 * 0.104) * om * np.exp(-MU_PB['g478'] * pb_cm)
    g15 = BB.GAMMA_PER_P * P_PER_S * om * np.exp(-MU_PB['g15'] * pb_cm)
    f8 = np.zeros_like(E_GRID)
    for e0, w in LINES_8BE:
        f8 += w * np.exp(-0.5 * ((E_GRID - e0) / (0.01 * e0)) ** 2) / (0.01 * e0 * np.sqrt(2 * np.pi))
    return {'n': (n, fn), 'g478': (g478, None), 'g8be': (g15, f8 / np.trapezoid(f8, E_GRID))}


def gen_density(kind, e):
    form, lo, hi = GEN[kind]
    e = np.asarray(e, float)
    return np.where((e >= lo) & (e <= hi), 1.0 / (hi - lo), 0.0)


def row_rate(z, kind, rate, pdf, e_key='En', w_key='w'):
    """per-row rate [1/s]: rate · f(E)/g(E) · w / N_gen (lines: rate · w / N_gen)."""
    w = np.asarray(z[w_key], float) if w_key in z else np.ones(len(z[e_key]))
    N = float(z['cnt_n_generated'])
    if pdf is None:
        return rate * w / N
    e = np.asarray(z[e_key], float)
    fe = np.interp(e, E_GRID, pdf, left=0.0, right=0.0)
    g = gen_density(kind, e)
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.where(g > 0, rate * fe / g * w / N, 0.0)


def sel_path(name):
    return SEL / f'{name}_sel.npz'


def load(name):
    p = sel_path(name)
    if not p.exists():
        return None
    z = dict(np.load(p, allow_pickle=True))
    z['name'] = name
    return z


def load_chan(name):
    p = SEL / f'{name}_chan.npz'
    return dict(np.load(p)) if p.exists() else None


def leak_sources():
    """the R2 samples and their source rate [particles/s]: the 4π neutron source and the ⁸Be γ."""
    return {'nsrc': SRC_N_PER_P * P_PER_S, 'gsrc': BB.GAMMA_PER_P * P_PER_S}


def room_mask(z, prefix=''):
    """rows whose event first interacted in the room, the wall or the dump (R3: the room return only; the cell part
    is the B2/B3 runs)."""
    k = prefix + 'force_vol' if (prefix + 'force_vol') in z else prefix + 'first_vol'
    if k not in z:
        return None
    v = np.array([x.decode() if isinstance(x, bytes) else str(x) for x in z[k]])
    return np.array([any(s.startswith(r) for r in ROOM_VOLS) for s in v])


def load_chanq(name):
    """the quenched per-channel spectra and legs of the kept ROOT files (requench.sh)."""
    p = SEL / f'{name}_chanq.npz'
    return dict(np.load(p)) if p.exists() else None


WALL = 'leakr'        # the wall variant: leakr (as built in the model), leakpb (+10 cm Pb), leakbpe (+10 cm BPE)


def leak_name(src, t, det, kind=None):
    """the R2 sample of what leaks through the wall.  'leakr': only the exit-plane records inside the experimental
    room's footprint that interacted (the uncollided bore beam is in B2/B3/R3; what crossed the plane outside the room
    leaked through the model's 50 cm target-room side walls and went round the wall: 'leak' keeps it, as a bound)."""
    kind = kind or WALL
    if kind == 'combo':         # Pb + BPE on the exit: photons behind the Pb, neutrons behind the BPE (estimate)
        kind = 'leakpb' if t == 'g' else 'leakbpe'
    if not sel_path(f'R2_{kind}_{src}_{t}_{det}').with_name(f'R2_{kind}_{src}_{t}_{det}_chan.npz').exists():
        kind = 'leakr'          # variants were run for the neutron source only (the ⁸Be-γ source is ×50 smaller)
    return f'R2_{kind}_{src}_{t}_{det}'
