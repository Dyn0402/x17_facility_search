"""Barrel tracker descriptions for the collider X17 toy (2026-11-12).

Every detector is a solenoid (uniform B along the beam, z) and a list of
cylindrical layers.  A layer is one or both of:

* a scatterer: thickness t = x/X0 at normal incidence, applied with the
  actual crossing angle (multiple scattering + Bethe-Heitler bremsstrahlung);
* a measurement: a hit with Gaussian sigma in r-phi and z.

TPC pad rows are measurement-only; the TPC gas is lumped into a few
scatterer slabs.  To keep the fit fast, rows are *decimated*: one effective
row stands for `rep` real rows, with sigma / sqrt(rep).  Hit-count
requirements are counted in real rows.

Numbers are the public ones found on 2026-11-12 (see colliders/*/README.md for
sources).  Anything not found publicly is marked (ask) in the README tables.
Units: metres, GeV, tesla.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Layer:
    r: float                 # radius [m]
    t: float = 0.0           # x/X0 at normal incidence (0 = no material)
    meas: bool = False       # gives a hit
    s_rphi: float = 0.0      # hit sigma r-phi [m]
    s_z: float = 0.0         # hit sigma z [m]
    zmax: float = 10.0       # half length [m]
    group: str = ''          # 'bp', 'mvtx', 'intt', 'tpc', 'its_ib', ...
    rep: int = 1             # real rows represented by this effective row


@dataclass
class Detector:
    key: str
    label: str
    B: float
    layers: list
    # track requirements: {group: minimum hits (real rows)}
    need: dict
    s_vtx_xy: float = 50e-6  # primary-vertex sigma used in the fit [m]
    s_vtx_z: float = 50e-6
    vz_sigma: float = 0.10   # luminous-region sigma in z [m]
    eta_note: str = ''
    notes: list = field(default_factory=list)

    def __post_init__(self):
        self.layers = sorted(self.layers, key=lambda L: L.r)


def tpc_rows(r0, r1, n, s_rphi, s_z, zmax, rep, group='tpc'):
    """n real pad rows between r0 and r1, decimated by rep."""
    r_real = np.linspace(r0, r1, n)
    out = []
    for i in range(0, n, rep):
        chunk = r_real[i:i + rep]
        out.append(Layer(r=float(chunk.mean()), meas=True,
                         s_rphi=s_rphi / np.sqrt(len(chunk)),
                         s_z=s_z / np.sqrt(len(chunk)), zmax=zmax,
                         group=group, rep=len(chunk)))
    return out


def gas_slabs(r0, r1, X0_gas, nslab, zmax, group='gas'):
    """Lump the gas between r0 and r1 into nslab scatterers at the slab centres."""
    edges = np.linspace(r0, r1, nslab + 1)
    return [Layer(r=float(0.5 * (a + b)), t=float((b - a) / X0_gas), zmax=zmax, group=group)
            for a, b in zip(edges[:-1], edges[1:])]


# ---------------------------------------------------------------- STAR
def star(B=0.5, key='star', label=None):
    """STAR as run since 2019 (iTPC), no inner silicon (HFT/IST/SSD removed after 2016)."""
    zt = 2.10
    L = [Layer(r=0.020, t=0.0028, group='bp'),                 # Be beam pipe ~1 mm, 0.28 % X0 (STAR TPC page); r = 2.0 cm (ask)
         Layer(r=0.470, t=0.0062, group='ifc', zmax=zt)]       # inner field cage, 0.62 % X0 incl. gas
    L += gas_slabs(0.50, 1.90, 118.0, 6, zt)                   # P10, X0 ~ 118 m
    L += tpc_rows(0.555, 1.190, 40, 0.7e-3, 1.0e-3, zt, 2)     # iTPC inner sector, 40 rows from 55 cm
    L += tpc_rows(1.272, 1.896, 32, 0.6e-3, 1.0e-3, zt, 2)     # outer sector, 32 rows
    return Detector(key=key, label=label or f'STAR (iTPC, {B:g} T)', B=B, layers=L,
                    need={'tpc': 15}, s_vtx_xy=200e-6, s_vtx_z=200e-6, vz_sigma=0.15,
                    eta_note='|eta| < 1.5 (iTPC)')


# ---------------------------------------------------------------- sPHENIX
def sphenix(mode='tpc', material='design', key=None, label=None):
    """sPHENIX: MVTX (3 MAPS layers) + INTT (4 strip layers) + compact TPC, 1.4 T.

    mode     'tpc'  : MVTX >= 2 + TPC >= 20 clusters (standard)
             'si'   : silicon only, MVTX 3 + INTT >= 2 (soft tracks that curl before the TPC)
    material 'design': Be pipe 0.76 mm (0.22 % X0), MVTX 0.3 % per layer
             'quoted': sPHENIX 2025 INTT paper (arXiv:2504.02240): pipe 1.8 %, MVTX 2.0 % in total
    """
    zt = 1.05
    if material == 'design':
        t_bp, t_mvtx = 0.0022, 0.0030
    else:
        t_bp, t_mvtx = 0.018, 0.020 / 3
    L = [Layer(r=0.020, t=t_bp, group='bp')]                   # Be pipe r = 2.0 cm (ask)
    for r in (0.02461, 0.03198, 0.03993):                      # MVTX r_min of the staves
        L.append(Layer(r=r, t=t_mvtx, meas=True, s_rphi=5e-6, s_z=5e-6, zmax=0.135, group='mvtx'))
    for r in (0.072, 0.078, 0.097, 0.103):                     # INTT, 1.14 % X0 per ladder
        L.append(Layer(r=r, t=0.0114, meas=True, s_rphi=78e-6 / np.sqrt(12), s_z=16e-3 / np.sqrt(12),
                       zmax=0.228, group='intt'))
    L.append(Layer(r=0.200, t=0.006, group='ifc', zmax=zt))   # TPC inner field cage (ask: 0.6 % assumed)
    L += gas_slabs(0.20, 0.78, 100.0, 3, zt)                   # Ar/CF4 60:40, X0 ~ 100 m
    L += tpc_rows(0.305, 0.775, 48, 0.20e-3, 0.5e-3, zt, 4)    # 48 layers, 30-78 cm
    if mode == 'tpc':
        need = {'mvtx': 2, 'tpc': 20}
        lab = 'sPHENIX TPC tracks'
    else:
        need = {'mvtx': 3, 'intt': 2}
        lab = 'sPHENIX silicon only'
    if material != 'design':
        lab += ' (quoted material)'
    return Detector(key=key or f'sphenix_{mode}' + ('' if material == 'design' else '_q'),
                    label=label or lab, B=1.4, layers=L, need=need,
                    s_vtx_xy=20e-6, s_vtx_z=30e-6, vz_sigma=0.10, eta_note='|eta| < 1.1')


# ---------------------------------------------------------------- ALICE (Run 3) and ALICE 3
def alice(B=0.5, mode='tpc', key=None, label=None):
    """ALICE Run 3: ITS2 (7 MAPS layers) + TPC.  B = 0.5 T standard, 0.2 T special runs."""
    zt = 2.50
    L = [Layer(r=0.0190, t=0.0023, group='bp')]               # Be pipe 0.8 mm (ask r)
    for r in (0.0224, 0.0301, 0.0378):                         # ITS2 inner barrel, 0.36 % X0
        L.append(Layer(r=r, t=0.0036, meas=True, s_rphi=5e-6, s_z=5e-6, zmax=0.135, group='its_ib'))
    for r, z in ((0.1960, 0.42), (0.2450, 0.42), (0.3440, 0.73), (0.3930, 0.73)):
        L.append(Layer(r=r, t=0.0080, meas=True, s_rphi=5e-6, s_z=5e-6, zmax=z, group='its_ob'))
    L.append(Layer(r=0.800, t=0.008, group='ifc', zmax=zt))   # TPC inner containment + field cage (ask)
    L += gas_slabs(0.85, 2.47, 314.0, 4, zt)                   # Ne-CO2-N2, X0 ~ 314 m
    L += tpc_rows(0.85, 2.47, 152, 0.8e-3, 1.0e-3, zt, 4)
    if mode == 'tpc':
        need = {'its_ib': 2, 'tpc': 70}
        lab = f'ALICE ITS+TPC ({B:g} T)'
    else:
        need = {'its_ib': 3, 'its_ob': 2}
        lab = f'ALICE ITS standalone ({B:g} T)'
    return Detector(key=key or f'alice_{mode}_{B:g}T'.replace('.', 'p'), label=label or lab,
                    B=B, layers=L, need=need, s_vtx_xy=20e-6, s_vtx_z=30e-6, vz_sigma=0.05,
                    eta_note='|eta| < 0.9')


def alice3(B=2.0, key=None, label=None):
    """ALICE 3 (Run 5, LoI level, approximate): vertex layers inside the beam pipe."""
    L = []
    for r in (0.005, 0.012, 0.025):                            # retractable iris tracker, 0.1 % X0
        L.append(Layer(r=r, t=0.001, meas=True, s_rphi=2.5e-6, s_z=2.5e-6, zmax=0.25, group='vd'))
    L.append(Layer(r=0.0370, t=0.001, group='bp'))             # outer vacuum vessel (ask)
    for r in (0.07, 0.12, 0.20, 0.30, 0.45, 0.60, 0.80):       # outer tracker, 1 % X0 per layer
        L.append(Layer(r=r, t=0.010, meas=True, s_rphi=5e-6, s_z=5e-6, zmax=1.3, group='ot'))
    return Detector(key=key or f'alice3_{B:g}T'.replace('.', 'p'), label=label or f'ALICE 3 ({B:g} T, approx.)',
                    B=B, layers=L, need={'vd': 3, 'ot': 2}, s_vtx_xy=5e-6, s_vtx_z=10e-6, vz_sigma=0.05,
                    eta_note='|eta| < 4 (barrel part used here)')


def registry():
    d = {}
    for det in (star(0.5), star(0.25, key='star_lowB', label='STAR (iTPC, 0.25 T, hypothetical)'),
                sphenix('tpc'), sphenix('si'), sphenix('tpc', 'quoted'), sphenix('si', 'quoted'),
                alice(0.5, 'tpc'), alice(0.2, 'tpc'), alice(0.5, 'its'), alice(0.2, 'its'),
                alice3(2.0), alice3(0.5)):
        d[det.key] = det
    return d


DETECTORS = registry()
