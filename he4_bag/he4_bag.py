"""A ⁴He bag around the ILL ³He target: does it replace the air ¹⁴N background?

Three questions, one section each, all analytic and calibrated against the ILL
Geant4 campaign (../ill/SIM_STATUS.md, V0) where it has a number:

1. Neutrons.  Capture and scattering in air vs ⁴He on the H113 beam: the
   300 mm open flight path (collimator aperture -> Be window) and, per cm, the
   gas the scattered neutrons cross around the cell.
2. Leptons.  Highland scattering of an X17 lepton on the cell -> Micromegas
   chord with air, with ⁴He, and with ⁴He behind an extra bag foil.
3. ³He permeation.  Fick's law per species through the G1–G6 skins, with the
   cell in air or in the bag: what leaves, what comes in, what it costs.

Run directly; writes out/*.csv and out/figures/he4_bag.{png,csv}.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import erf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'ill'))
import figstyle  # noqa: E402

OUT = HERE / 'out'

# ------------------------------------------------------------- constants -----
N_GAS = 2.504e19          # molecules / cm³, 1 atm, 20 °C
KT_MEV = 25.26e-3 * 1e3   # kT at 20 °C in meV (25.26 meV)
LAM_TH = 1.798            # Å, 2200 m/s
ME = 0.51099895           # MeV
BARN = 1e-24

# Air by molecule count.
AIR = {'N2': 0.7808, 'O2': 0.2095, 'Ar': 0.0093}

# Thermal (2200 m/s) cross sections per atom [b], Sears / NIST tables.
#   abs: 1/v absorption; scat: bound scattering; A: atomic mass number.
#   N:  (n,p) 1.83 b + (n,γ) 0.0798 b, Q(n,γ) = 10.83 MeV (the hard line)
#   Ar: (n,γ) 0.675 b, Q = 6.10 MeV;  O: 0.19 mb;  ⁴He: no bound A = 5, abs = 0
XS = {
    'N':   dict(ng=0.0798, np=1.83, scat=11.51, A=14),
    'O':   dict(ng=0.00019, np=0.0, scat=4.232, A=16),
    'Ar':  dict(ng=0.675, np=0.0, scat=0.683, A=40),
    'He4': dict(ng=0.0, np=0.0, scat=1.34, A=4),
}
# Molecules: (atom, atoms per molecule, mass of the scattering unit).
MOLECULE = {'N2': ('N', 2, 28), 'O2': ('O', 2, 32), 'Ar': ('Ar', 1, 40),
            'He4': ('He4', 1, 4)}

# ILL geometry (../ill/HANDOFF_SIM.md, SIM_STATUS.md).
L_FLIGHT = 30.0           # cm, open air from the collimator aperture to the Be window
L_CHORD_AIR = 16.0        # cm, cell -> Micromegas entrance (FEASIBILITY_SIM §1)
SIM_V0 = {'14N(n,g) per n': 2.5e-4, '14N(n,p) per n': 6e-3, 'scattered': 2e-2}

# Radiation lengths [cm].
X0 = {'air': 36.62 / 1.205e-3, 'He4': 94.32 / 1.664e-4,
      'mylar': 28.54, 'kapton': 28.58, 'Cu': 1.436}
MM_ENTRANCE = [('mylar', 40e-4), ('kapton', 50e-4), ('Cu', 9e-4)]   # cm
G1_SKIN = [('mylar', 12e-4)]


# ============================================================ 1. neutrons ====
def h113_spectrum():
    """λ [Å] and normalised particle-flux weights of the H113 beam."""
    s = pd.read_csv(HERE.parent / 'ill' / 'out' / 'h113_spectrum.csv')
    w = s['dPhi_dlambda_per_A'].to_numpy()
    return s['lambda_A'].to_numpy(), w / w.sum()


def free_gas_factor(lam, mass):
    """Free-gas σ_eff/σ_free for a neutron of wavelength λ on a gas of `mass` at
    20 °C.  > 1 for cold neutrons: the gas molecules outrun them."""
    e_mev = 81.804 / lam ** 2
    x = np.sqrt(mass * e_mev / KT_MEV)
    return (1 + 1 / (2 * x ** 2)) * erf(x) + np.exp(-x ** 2) / (x * np.sqrt(np.pi))


def sigma_per_cm(gas, lam):
    """Σ [1/cm] for each channel at wavelength(s) λ.  gas = {molecule: fraction}."""
    out = {'14N(n,g)': 0.0, '14N(n,p)': 0.0, 'Ar(n,g)': 0.0, 'scatter': 0.0}
    for mol, frac in gas.items():
        atom, k, m = MOLECULE[mol]
        x = XS[atom]
        n_atom = N_GAS * frac * k
        v = lam / LAM_TH
        if atom == 'N':
            out['14N(n,g)'] = out['14N(n,g)'] + n_atom * x['ng'] * v * BARN
            out['14N(n,p)'] = out['14N(n,p)'] + n_atom * x['np'] * v * BARN
        if atom == 'Ar':
            out['Ar(n,g)'] = out['Ar(n,g)'] + n_atom * x['ng'] * v * BARN
        s_free = x['scat'] * (m / (m + 1)) ** 2
        out['scatter'] = out['scatter'] + n_atom * s_free * free_gas_factor(lam, m) * BARN
    return out


def bag_gas(f_air):
    """⁴He with an air contamination f_air (by molecule count)."""
    g = {k: f_air * v for k, v in AIR.items()}
    g['He4'] = 1.0 - f_air
    return g


def neutrons():
    lam, w = h113_spectrum()
    rows = []
    for label, gas in [('air', AIR), ('He, 5 % air', bag_gas(0.05)),
                       ('He, 1 % air', bag_gas(0.01)), ('He, 0.1 % air', bag_gas(0.001)),
                       ('pure ⁴He', bag_gas(0.0))]:
        s = sigma_per_cm(gas, lam)
        r = {'gas': label}
        for ch, sig in s.items():
            r[f'{ch} per n, 30 cm'] = float(np.sum(w * (1 - np.exp(-sig * L_FLIGHT))))
            r[f'{ch} per cm'] = float(np.sum(w * sig))
        rows.append(r)
    df = pd.DataFrame(rows)

    lam_mean = float(np.sum(w * lam))
    print(f'H113 mean λ (particle flux) = {lam_mean:.2f} Å  (Geant4 after aperture: 4.85 Å)')
    print('\n1. Neutrons on the 300 mm flight path, per beam neutron')
    cols = ['gas'] + [c for c in df.columns if c.endswith('30 cm')]
    print(df[cols].to_string(index=False, float_format=lambda v: f'{v:.2e}'))
    a = df.iloc[0]
    print(f'   Geant4 V0 (air): 14N(n,g) {SIM_V0["14N(n,g) per n"]:.1e}, '
          f'14N(n,p) {SIM_V0["14N(n,p) per n"]:.0e}, scattered ~{SIM_V0["scattered"]:.0%}'
          f'  -> analytic/G4 = {a["14N(n,g) per n, 30 cm"] / SIM_V0["14N(n,g) per n"]:.2f}, '
          f'{a["14N(n,p) per n, 30 cm"] / SIM_V0["14N(n,p) per n"]:.2f}, '
          f'{a["scatter per n, 30 cm"] / SIM_V0["scattered"]:.2f}')

    # Around the cell: a neutron scattered out of the beam crosses ~30 cm of gas
    # inside the detector before it leaves; the inner bag only acts on those.
    print('\n   Around the cell (per scattered neutron, 30 cm of gas inside the detector):')
    for i in (0, 4):
        print(f'     {df.gas[i]:10s} 14N(n,g) {df["14N(n,g) per cm"][i] * 30:.1e}')
    df.to_csv(OUT / 'neutrons.csv', index=False)
    return df


# ============================================================= 2. leptons ====
def highland(p, x):
    x = max(x, 1e-12)
    beta = p / np.sqrt(p * p + ME * ME)
    return np.degrees(13.6 / (beta * p) * np.sqrt(x) * (1 + 0.038 * np.log(x)))


def leptons():
    def budget(gas, bag_foil):
        layers = G1_SKIN + MM_ENTRANCE + [(gas, L_CHORD_AIR)]
        if bag_foil:
            layers.append(('mylar', bag_foil))
        return sum(t / X0[m] for m, t in layers)

    cases = {'air (as simulated)': budget('air', 0),
             '⁴He, bag sealed on the MM windows': budget('He4', 0),
             '⁴He + 25 µm mylar bag foil': budget('He4', 25e-4),
             '⁴He + 100 µm mylar bag foil': budget('He4', 100e-4)}
    rows = []
    for ke in (4.1, 6.3, 9.1, 13.3):
        p = np.sqrt((ke + ME) ** 2 - ME ** 2)
        r = {'KE [MeV]': ke}
        for k, x in cases.items():
            r[k] = highland(p, x)
        rows.append(r)
    df = pd.DataFrame(rows)
    print('\n2. Highland θ0 [deg] per leg, G1 skin + MM entrance + 16 cm gas')
    print('   x/X0: ' + ', '.join(f'{k} {v:.2e}' for k, v in cases.items()))
    print(df.to_string(index=False, float_format=lambda v: f'{v:.2f}'))
    df.to_csv(OUT / 'leptons.csv', index=False)
    return df


# ========================================================= 3. permeation ====
BARRER = 1e-10            # cm³(STP)·cm / (cm²·s·cmHg)
CMHG_PER_BAR = 75.006
DAY = 86400.0
CYCLE_D = 50.0
HE3_EUR_PER_L = 2500.0    # €/L(STP), order of magnitude; market price has been 2–5 k$

# Permeability [barrer] at 25 °C.  PET (Mylar): He ~0.6–1.3, O2 ~0.03, N2 ~0.006
# (DuPont Mylar sheet, Polymer Handbook).  Kapton HN He: sources disagree by
# ~10× (0.2–2.5); 1 is a placeholder.  ³He is taken 10 % faster than ⁴He
# (diffusivity isotope effect, roughly √(4/3)); unmeasured for these films.
PERM = {'mylar': {'He4': 1.0, 'N2': 0.006, 'O2': 0.03},
        'kapton': {'He4': 1.0, 'N2': 0.03, 'O2': 0.1}}
HE3_OVER_HE4 = 1.10

CELLS = pd.DataFrame([
    # id, p [bar], L [mm], R [mm], wall, t [mm]  (../ill/HANDOFF_SIM.md §4)
    ('G1', 1, 300, 40, 'mylar', 0.012), ('G2', 1, 300, 100, 'mylar', 0.012),
    ('G3', 2, 150, 40, 'kapton', 0.11), ('G4', 2, 150, 100, 'kapton', 0.29),
    ('G5', 3, 100, 40, 'kapton', 0.23), ('G6', 3, 100, 100, 'kapton', 0.57),
], columns=['id', 'p_bar', 'L_mm', 'R_mm', 'wall', 't_mm'])


def permeation(bif=1.0):
    """Per cell: ³He loss, ⁴He or air ingress, time constants.  `bif` is the
    barrier improvement factor of a metallisation (1 = bare film).  The barrel
    is the only polymer area: the Be window and the Al cap do not pass He."""
    rows = []
    for c in CELLS.itertuples():
        area = 2 * np.pi * (c.R_mm / 10) * (c.L_mm / 10)        # cm²
        vol = np.pi * (c.R_mm / 10) ** 2 * (c.L_mm / 10)        # cm³
        g = area / (c.t_mm / 10) / bif                          # cm
        P = PERM[c.wall]
        n_he3 = vol * c.p_bar                                   # cm³(STP), ≈ bar·L ×1000
        # Rates in cm³(STP)/day; partial-pressure difference in cmHg.
        q3 = P['He4'] * HE3_OVER_HE4 * BARRER * g * c.p_bar * CMHG_PER_BAR * DAY
        q4_in = P['He4'] * BARRER * g * 1.0 * CMHG_PER_BAR * DAY          # bag at 1 bar ⁴He
        qn2_in = P['N2'] * BARRER * g * AIR['N2'] * CMHG_PER_BAR * DAY    # cell in air
        qo2_in = P['O2'] * BARRER * g * AIR['O2'] * CMHG_PER_BAR * DAY
        tau3 = n_he3 / q3
        rows.append(dict(
            id=c.id, wall=c.wall, t_um=c.t_mm * 1e3, area_cm2=area, he3_barL=n_he3 / 1e3,
            he3_loss_L_per_day=q3 / 1e3,
            he3_loss_L_per_cycle=q3 * CYCLE_D / 1e3,
            he3_cost_eur_per_cycle=q3 * CYCLE_D / 1e3 * HE3_EUR_PER_L,
            tau_he3_days=tau3,
            he4_in_L_per_day_bag=q4_in / 1e3,
            air_in_L_per_day=(qn2_in + qo2_in) / 1e3,
            he4_over_air_ingress=q4_in / (qn2_in + qo2_in),
            # sealed cell kept a full cycle in the bag (rigid cell; for the
            # zero-Δp mylar cells the ⁴He refills the volume the ³He leaves)
            he3_frac_sealed_50d_bag=np.exp(-CYCLE_D / tau3),
            # N2 accumulated in a sealed cell over a cycle in air, as a fraction
            # of the ³He, and the in-cell 14N(n,γ) per absorbed neutron it causes
            n2_over_he3_50d_air=qn2_in * CYCLE_D / n_he3,
            in_cell_14Nng_per_n_50d=2 * qn2_in * CYCLE_D / n_he3 * XS['N']['ng'] / 5333.0,
        ))
    return pd.DataFrame(rows)


def he4_flush(perm_df, x4_max=0.05):
    """Fresh ³He flow that holds the in-cell ⁴He fraction at x4_max (well mixed):
    F ≈ q4_in / x4_max.  The outflow is a ³He/⁴He mix that has to go to recovery."""
    f = perm_df['he4_in_L_per_day_bag'] / x4_max
    return pd.DataFrame({'id': perm_df['id'], 'flow_L_per_day': f,
                         'flow_over_volume_per_day': f / perm_df['he3_barL']})


def report_permeation():
    print('\n3. ³He permeation through the barrel (Fick per species; '
          f'mylar He {PERM["mylar"]["He4"]} barrer, Kapton He {PERM["kapton"]["He4"]} barrer)')
    out = {}
    for bif in (1.0, 10.0):
        d = permeation(bif)
        out[bif] = d
        tag = 'bare film' if bif == 1 else f'metallised, BIF {bif:.0f}'
        print(f'\n   {tag}')
        print(d[['id', 'he3_barL', 'he3_loss_L_per_day', 'he3_loss_L_per_cycle',
                 'he3_cost_eur_per_cycle', 'tau_he3_days', 'he3_frac_sealed_50d_bag',
                 'he4_over_air_ingress', 'n2_over_he3_50d_air',
                 'in_cell_14Nng_per_n_50d']].to_string(
            index=False, float_format=lambda v: f'{v:.3g}'))
        d.to_csv(OUT / f'permeation_bif{bif:.0f}.csv', index=False)
    fl = he4_flush(out[1.0])
    print('\n   ³He flush to hold ⁴He < 5 % in the cell (bare film, bag at 1 bar ⁴He)')
    print(fl.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    fl.to_csv(OUT / 'he4_flush_bif1.csv', index=False)
    return out


# ============================================================== figure ======
def figure(nd, perm):
    figstyle.use()
    fig, (a1, a2) = figstyle.figure(figsize=(10.5, 4.0), ncols=2)

    gases = nd['gas'].tolist()
    y = np.arange(len(gases))
    v = nd['14N(n,g) per n, 30 cm'].to_numpy()
    a1.barh(y, np.maximum(v, 1e-9), color='#4a6fa5')
    a1.axvline(SIM_V0['14N(n,g) per n'], color='#c44e52', lw=1.2, ls='--')
    a1.text(SIM_V0['14N(n,g) per n'], len(gases) - 0.45, ' Geant4 V0 (air)',
            color='#c44e52', fontsize=8.5, va='bottom')
    a1.axvline(1.4e-4, color='#888', lw=1, ls=':')
    a1.text(1.4e-4, 3.9, 'Be window\n(any gas) ', color='#666', fontsize=8, ha='right')
    a1.set_xscale('log')
    a1.set_xlim(1e-8, 1e-3)
    a1.set_yticks(y, [g if v[i] > 0 else g + ' (0)' for i, g in enumerate(gases)])
    a1.invert_yaxis()
    a1.set_xlabel('¹⁴N(n,γ) 10.8 MeV per beam neutron, 30 cm path')
    figstyle.title(a1, 'The bag gas only has to be ~1 % clean')

    t = np.linspace(0, CYCLE_D, 201)
    data = {'day': t}
    for (cid, bif), ls in zip([('G1', 1), ('G1', 10), ('G5', 1), ('G5', 10)],
                              ['-', '--', '-', '--']):
        d = perm[bif].set_index('id').loc[cid]
        f = np.exp(-t / d.tau_he3_days)
        col = '#4a6fa5' if cid == 'G1' else '#dd8452'
        lab = f'{cid} {"bare" if bif == 1 else "BIF 10"}'
        a2.plot(t, f, ls=ls, color=col, label=lab)
        data[lab] = f
    a2.set_ylim(0, 1.02)
    a2.set_xlabel('days, sealed cell')
    a2.set_ylabel('³He left (bag: ⁴He takes its place)')
    a2.legend(loc='lower left')
    figstyle.title(a2, 'Bare 12 µm mylar empties in days')
    figstyle.save(fig, OUT / 'figures' / 'he4_bag',
                  data={'neutrons': nd, 'permeation': pd.DataFrame(data)})


# ================================================= 4. a better skin at 1 bar =
# The G1 geometry (R 40 mm, L 300 mm, 1 bar ³He) with other skins.  Loss is
# (barrel + seals); the barrel term uses a BIF range where it is unmeasured.
G1_GEOM = dict(R_cm=4.0, L_cm=30.0, p_bar=1.0)
X0['Al'] = 8.897
X0['PET'] = X0['mylar']

# Neutron capture per beam neutron in the barrel.  The beam (r99 = 12.9 mm)
# never reaches r = 40 mm; only neutrons scattered in the ³He do, before being
# absorbed.  σs/σa(³He) at 4.87 Å = 3.15 b (free) / 14 400 b = 2.2e-4, and
# about half of those reach the barrel (1/Σa = 2.8 cm at 1 bar): ~1e-4 hits/n,
# crossing at ~60° on average (path ≈ 2t).  Analytic, not from the MC.
BARREL_HITS_PER_N = 1e-4
LAM_FAC = 4.87 / LAM_TH
# Σ_abs at 2200 m/s [1/cm]: PET (C10H8O4, 1.40 g/cm³) is ~all H (0.332 b);
# Al 0.231 b; Kapton (C22H10N2O5, 1.42) has H and N.
SIG_ABS = {'PET': 0.0119, 'Al': 0.0139, 'kapton': 0.0160}
GAMMA_MAX = {'PET': 4.95, 'Al': 7.72, 'kapton': 10.83}   # MeV: C(n,γ) | Al | ¹⁴N

SKINS = [
    # name, layers [(material, cm)], BIF (lo, hi), p_bar, note
    ('12 µm PET, bare (G1 as simulated)', [('PET', 12e-4)], (1, 1), 1,
     'literature PET He ≈ 1 barrer'),
    ('12 µm PET, double-aluminised', [('PET', 12e-4), ('Al', 8e-6)], (1, 10), 1,
     '2 × 40 nm vapour Al; He BIF unmeasured, foil-balloon experience says a few ×'),
    ('50 µm PET', [('PET', 50e-4)], (1, 1), 1, 'thicker film: loss ∝ 1/t, x/X0 ∝ t'),
    ('12 µm PET + 9 µm Al foil laminate', [('PET', 12e-4), ('Al', 9e-4)], (1e4, 1e7), 1,
     'rolled foil is impermeable; leaks only at pinholes (~50/m² at 9 µm) and creases'),
    ('12 µm PET + 25 µm Al foil laminate', [('PET', 12e-4), ('Al', 25e-4)], (1e6, 1e8), 1,
     '≥ 25 µm foil is pinhole-free in practice'),
    ('G3: 0.11 mm Kapton, 2 bar', [('kapton', 0.011)], (1, 1), 2,
     'pressure wall, Kapton He 1 barrer placeholder (sources 0.2–2.5)'),
    ('G5: 0.23 mm Kapton, 3 bar', [('kapton', 0.023)], (1, 1), 3, 'pressure wall, as G3'),
]

# Seals and bonds of the G1 cell: conductance g = (area / path) [cm], He
# permeability [barrer].  Viton face O-ring: g ≈ 0.7 π D (1 − S)² (Parker
# rule, D = 9 cm, squeeze S = 0.2), He 9 barrer.  Epoxy bondlines: 30 µm
# thick, He ~5 barrer, path = bond width.
SEALS = [
    ('Viton O-rings, Be window + Al cap', 2 * 0.7 * np.pi * 9.0 * 0.8 ** 2, 9.0),
    ('epoxy: skin onto the two endcap lands', 2 * 2 * np.pi * 4.2 * 30e-4 / 1.5, 5.0),
    ('epoxy: overlap seam along the flat rod', 30.0 * 30e-4 / 1.0, 5.0),
]


def _loss_per_cycle(g_cm, perm_barrer, p_bar):
    """³He loss per 50-day cycle [L STP] through conductance g at ³He pressure p."""
    return perm_barrer * HE3_OVER_HE4 * BARRER * g_cm * p_bar * CMHG_PER_BAR * DAY * CYCLE_D / 1e3


def seals():
    rows = [dict(component=n, g_cm=g, perm_barrer=P,
                 he3_L_per_cycle=_loss_per_cycle(g, P, 1.0)) for n, g, P in SEALS]
    a = 2 * np.pi * G1_GEOM['R_cm'] * G1_GEOM['L_cm']
    rows.append(dict(component='barrel, bare 12 µm PET', g_cm=a / 12e-4, perm_barrer=1.0,
                     he3_L_per_cycle=_loss_per_cycle(a / 12e-4, 1.0, 1.0)))
    # pinholes in a 9 µm foil: ~50 /m², radius 5 µm, each fed through the
    # 12 µm PET by spreading conductance ≈ 4a; ×100 for creases on the rods
    for tag, n_m2 in (('9 µm Al laminate, 50 pinholes/m²', 50), ('… creased, 5000 pinholes/m²', 5000)):
        g = n_m2 * a / 1e4 * 4 * 5e-4
        rows.append(dict(component=f'barrel, {tag}', g_cm=g, perm_barrer=1.0,
                         he3_L_per_cycle=_loss_per_cycle(g, 1.0, 1.0)))
    df = pd.DataFrame(rows)
    print('\n5. Leak budget of a G1 cell, ³He L per cycle')
    print(df.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    df.to_csv(OUT / 'seals.csv', index=False)
    return df


def skins():
    seal_floor = sum(_loss_per_cycle(g, P, 1.0) for _n, g, P in SEALS)
    p63 = np.sqrt((6.3 + ME) ** 2 - ME ** 2)
    base_x = sum(t / X0[m] for m, t in MM_ENTRANCE) + L_CHORD_AIR / X0['air']
    rows = []
    for name, layers, (blo, bhi), pb, note in SKINS:
        R, L = G1_GEOM['R_cm'], G1_GEOM['L_cm'] * (1.0 / pb)   # same ³He bar·L
        a = 2 * np.pi * R * L
        t_poly = sum(t for m, t in layers if m != 'Al')
        perm = PERM['kapton' if layers[0][0] == 'kapton' else 'mylar']['He4']
        bare = _loss_per_cycle(a / t_poly, perm, pb)
        sf = seal_floor * pb
        x = sum(t / X0[m] for m, t in layers)
        cap = sum(t * SIG_ABS[m] for m, t in layers) * 2 * LAM_FAC * BARREL_HITS_PER_N
        rows.append(dict(
            skin=name, p_bar=pb, x_X0=x,
            theta0_6p3MeV_deg=highland(p63, x + base_x),
            loss_lo_L=bare / bhi + sf, loss_hi_L=bare / blo + sf,
            loss_cost_hi_eur=(bare / blo + sf) * HE3_EUR_PER_L,
            barrel_captures_per_n=cap,
            gamma_max_MeV=max(GAMMA_MAX[m] for m, _t in layers), note=note))
    df = pd.DataFrame(rows)
    print(f'\n4. Skins for the G1 cell (seal floor {seal_floor * 1e3:.1f} cm³/cycle at 1 bar; '
          f'θ0 with air, no skin: {highland(p63, base_x):.2f}°)')
    print(df.drop(columns='note').to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    df.to_csv(OUT / 'skins.csv', index=False)
    return df


# ============================================= 6. choosing the foil and base =
# Follow-up questions (2026-10-02): is there a better barrier metal than Al,
# how thin can the foil go, what dominates the lepton scattering, and does a
# 1 bar cell need any strength at all?
#
# Barrier metals: thermal σ_abs [b], ρ [g/cm³], A, X0 [cm], hardest capture
# line [MeV], thinnest foil one can buy in metre-size sheets [cm] (supplier
# catalogues, approximate), and a note.
METALS = [
    ('Al', 0.231, 2.699, 26.98, 8.897, 7.72, 6e-4,
     '6–7 µm converter foil is a commodity (PET/Al packaging laminates)'),
    ('Be', 0.0076, 1.848, 9.012, 35.28, 6.81, 8e-4,
     'X-ray-window foil: small discs only, brittle, toxic to machine; cannot be wrapped'),
    ('Mg', 0.063, 1.738, 24.31, 14.40, 11.09, 25e-4,
     'specialty foil, corrodes; ²⁵Mg(n,γ) has an 11.1 MeV line, harder than ¹⁴N'),
    ('Zr', 0.185, 6.506, 91.22, 1.566, 8.63, 10e-4,
     'specialty foil, 5× the scattering of Al per µm'),
    ('Cu', 3.78, 8.96, 63.55, 1.436, 7.92, 6e-4,
     'battery foil is cheap, but 16× the capture of Al'),
    ('Pb', 0.171, 11.35, 207.2, 0.5612, 7.37, 25e-4,
     'soft, creeps; 16× the scattering of Al per µm'),
]
N_A = 6.022e23
# Typical pinholes per m² of rolled Al foil vs gauge [cm] (order of magnitude:
# counts fall ~10× per few µm; ≥ 25 µm is pinhole-free in practice).
PINHOLES = {6e-4: 1000, 7e-4: 300, 9e-4: 50, 12e-4: 5, 25e-4: 0.1}
CREASE = 100                       # extra pinholes from wrapping on the rods
CHOSEN = [('PET', 12e-4), ('Al', 7e-4)]   # recommended skin
CATHODE_AL = 0.1e-4                # cm: aluminised drift cathode replacing 9 µm Cu
YIELD_MPA = {'PET': 100.0, 'Al': 35.0}    # biaxial PET film; annealed (O temper) foil


def _p63():
    return np.sqrt((6.3 + ME) ** 2 - ME ** 2)


def _sigma_cm(sig_b, rho, A):
    return sig_b * 1e-24 * rho * N_A / A


def metals():
    """Barrier metals at their thinnest buyable foil, on 12 µm PET, G1 barrel."""
    base_x = sum(t / X0[m] for m, t in MM_ENTRANCE) + L_CHORD_AIR / X0['air']
    pet = 12e-4 / X0['PET']
    rows = []
    for name, sig, rho, A, x0, gmax, tmin, note in METALS:
        cap = (tmin * _sigma_cm(sig, rho, A) + 12e-4 * SIG_ABS['PET']) * 2 * LAM_FAC * BARREL_HITS_PER_N
        rows.append(dict(metal=name, sigma_abs_b=sig, X0_cm=x0, gamma_max_MeV=gmax,
                         t_min_um=tmin * 1e4, x_X0=tmin / x0 + pet,
                         theta0_6p3MeV_deg=highland(_p63(), tmin / x0 + pet + base_x),
                         barrel_captures_per_n=cap,
                         capture_per_um_vs_Al=_sigma_cm(sig, rho, A) / _sigma_cm(0.231, 2.699, 26.98),
                         x_per_um_vs_Al=X0['Al'] / x0, note=note))
    df = pd.DataFrame(rows)
    print('\n6a. Barrier metals at the thinnest buyable foil, on 12 µm PET (G1 barrel)')
    print(df.drop(columns='note').to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    df.to_csv(OUT / 'metals.csv', index=False)
    return df


def foil_gauge():
    """Al foil gauge scan on 12 µm PET: scattering, captures, pinhole leak."""
    a = 2 * np.pi * G1_GEOM['R_cm'] * G1_GEOM['L_cm']
    seal_floor = sum(_loss_per_cycle(g, P, 1.0) for _n, g, P in SEALS)
    base_x = sum(t / X0[m] for m, t in MM_ENTRANCE) + L_CHORD_AIR / X0['air']
    g_per_hole = 4 * 5e-4                       # spreading conductance 4a, a = 5 µm
    rows = []
    for t, n in PINHOLES.items():
        x = 12e-4 / X0['PET'] + t / X0['Al']
        rows.append(dict(
            al_um=round(t * 1e4, 3), x_X0=x, theta0_6p3MeV_deg=highland(_p63(), x + base_x),
            barrel_captures_per_n=(12e-4 * SIG_ABS['PET'] + t * SIG_ABS['Al']) * 2 * LAM_FAC * BARREL_HITS_PER_N,
            pinholes_m2=n,
            barrel_loss_L=_loss_per_cycle(n * a / 1e4 * g_per_hole, 1.0, 1.0),
            barrel_loss_creased_L=_loss_per_cycle(CREASE * n * a / 1e4 * g_per_hole, 1.0, 1.0)))
    df = pd.DataFrame(rows)
    # pinhole density at which the barrel equals the O-ring floor
    n_crit = seal_floor / _loss_per_cycle(a / 1e4 * g_per_hole, 1.0, 1.0)
    print(f'\n6b. Al gauge on 12 µm PET (O-ring floor {seal_floor * 1e3:.1f} cm³/cycle; barrel reaches it '
          f'at {n_crit:.2g} pinholes/m²)')
    print(df.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    df.to_csv(OUT / 'foil_gauge.csv', index=False)
    return df, n_crit, seal_floor


def chord_budget():
    """x/X0 per layer of one lepton leg, and θ0 if the big layers are replaced."""
    layers = ([(f'{lbl}', m, t) for lbl, (m, t) in
               zip(['MM entrance: 9 µm Cu', 'cell → MM: 16 cm air', 'MM entrance: 50 µm Kapton',
                    'MM entrance: 40 µm mylar', 'skin: 7 µm Al foil', 'skin: 12 µm PET'],
                   [('Cu', 9e-4), ('air', L_CHORD_AIR), ('kapton', 50e-4), ('mylar', 40e-4),
                    CHOSEN[1], CHOSEN[0]])])
    x = {lbl: t / X0[m] for lbl, m, t in layers}
    tot = sum(x.values())
    bud = pd.DataFrame([dict(layer=k, x_X0=v, share=v / tot) for k, v in x.items()])
    skin = sum(t / X0[m] for m, t in CHOSEN)
    mm_nocu = 50e-4 / X0['kapton'] + 40e-4 / X0['mylar']
    steps = [
        ('no skin (air, MM as built)', tot - skin),
        ('12 µm PET (G1 as simulated)', tot - CHOSEN[1][1] / X0['Al']),
        ('12 µm PET + 7 µm Al (recommended)', tot),
        ('… and an aluminised MM cathode instead of 9 µm Cu', skin + mm_nocu + CATHODE_AL / X0['Al']
         + L_CHORD_AIR / X0['air']),
        ('… and He instead of air, cell → MM', skin + mm_nocu + CATHODE_AL / X0['Al']
         + L_CHORD_AIR / X0['He4']),
    ]
    lad = pd.DataFrame([dict(config=k, x_X0=v, theta0_6p3MeV_deg=highland(_p63(), v)) for k, v in steps])
    print('\n6c. Chord budget per leg (recommended skin) and θ0 at 6.3 MeV if the big layers go')
    print(bud.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    print(lad.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    bud.to_csv(OUT / 'chord_budget.csv', index=False)
    lad.to_csv(OUT / 'chord_ladder.csv', index=False)
    return bud, lad


def hoop():
    """Membrane stress at the small Δp a 1 bar cell still sees (T ≈ Δp·R)."""
    R = G1_GEOM['R_cm'] * 1e-2
    rows = []
    for dp_mbar, why in ((10, 'design value (mylar_wrap_vessel.py)'),
                         (30, 'weather swing of the hall pressure'),
                         (50, '30 mbar weather + 5 K warm-up of a sealed cell'),
                         (1000, 'pumping the cell out to fill it')):
        T = dp_mbar * 100 * R                    # N/m
        rows.append(dict(dp_mbar=dp_mbar, why=why, tension_N_per_m=T,
                         PET12_plus_Al7_MPa=T / 19e-6 / 1e6,
                         PET12_MPa=T / 12e-6 / 1e6, Al7_alone_MPa=T / 7e-6 / 1e6))
    df = pd.DataFrame(rows)
    print(f'\n6d. Membrane stress at R = {R * 1e3:.0f} mm (yield: PET ~{YIELD_MPA["PET"]:.0f}, '
          f'soft Al foil ~{YIELD_MPA["Al"]:.0f} MPa)')
    print(df.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    df.to_csv(OUT / 'hoop.csv', index=False)
    return df


if __name__ == '__main__':
    (OUT / 'figures').mkdir(parents=True, exist_ok=True)
    nd = neutrons()
    leptons()
    perm = report_permeation()
    skins()
    seals()
    metals()
    foil_gauge()
    chord_budget()
    hoop()
    figure(nd, perm)
