"""Sources for the collider X17 toy: meson spectra, X17 and Dalitz decays, conversions.

Parent mesons (pi0, eta) are thrown with a Tsallis (Levy) pT spectrum,
dN/dpT ~ pT [1 + (mT - m_pi0)/(n T)]^-n, the same function of mT for both
mesons (mT scaling), and flat in rapidity over |y| < Y_GEN.  Yields are later quoted
per unit rapidity at mid-rapidity, so the flat-y throw only sets the
normalisation: produced per unit y = N_thrown / (2 Y_GEN).

Decays:
* P -> gamma X17, X17 isotropic in the P frame; X17 -> e+e- with 1 + cos^2
  about the X17 direction (transverse X17, as for a real photon);
* P -> gamma gamma* -> gamma e+e- (Dalitz) with the Kroll-Wada mass spectrum
  over a mass band, the same angular law;
* P -> gamma gamma for conversions.
"""
from __future__ import annotations

import numpy as np

ME = 0.000511
MPI0 = 0.1349768
META = 0.547862
ALPHA = 1 / 137.036
BR_GG = {'pi0': 0.98823, 'eta': 0.3936}
MASS = {'pi0': MPI0, 'eta': META}
M_X17 = 0.0168
Y_GEN = 2.0

# (n, T) per collision system: tuned to <pT>(pi) ~ 0.36 (pp 200), 0.41 (Au+Au 200 MB),
# 0.46 (pp 13.6 TeV), 0.50 GeV (Pb-Pb MB).  Shapes only; see README.
SPECTRA = {
    'auau200': dict(n=11.0, T=0.150),
    'pp200': dict(n=9.0, T=0.120),
    'pp13600': dict(n=6.8, T=0.135),
    'pbpb5360': dict(n=9.0, T=0.170),
}


def tsallis_pt(rng, n_ev, m, n, T, ptmax=6.0):
    """Sample pT [GeV] by inverse CDF on a grid."""
    pt = np.linspace(0, ptmax, 60001)
    mt = np.sqrt(pt ** 2 + m ** 2)
    f = pt * (1 + (mt - MPI0) / (n * T)) ** (-n)
    c = np.cumsum(f)
    c /= c[-1]
    return np.interp(rng.random(n_ev), c, pt)


def mean_pt(m, n, T):
    pt = np.linspace(0, 6, 60001)
    mt = np.sqrt(pt ** 2 + m ** 2)
    f = pt * (1 + (mt - MPI0) / (n * T)) ** (-n)
    return float((pt * f).sum() / f.sum())


def random_unit(rng, n):
    c = rng.uniform(-1, 1, n)
    s = np.sqrt(1 - c ** 2)
    ph = rng.uniform(0, 2 * np.pi, n)
    return np.stack([s * np.cos(ph), s * np.sin(ph), c], axis=1)


def sample_1pcos2(rng, n):
    """cos(theta*) distributed as 1 + cos^2."""
    out = np.empty(n)
    k = 0
    while k < n:
        c = rng.uniform(-1, 1, 2 * (n - k) + 10)
        keep = c[rng.random(c.size) * 2 < 1 + c ** 2]
        take = min(keep.size, n - k)
        out[k:k + take] = keep[:take]
        k += take
    return out


def boost(p4, beta):
    """Boost four-vectors p4 (N,4: E,px,py,pz) by velocity beta (N,3)."""
    b2 = np.sum(beta ** 2, axis=1)
    g = 1 / np.sqrt(1 - b2)
    bp = np.sum(beta * p4[:, 1:], axis=1)
    g2 = np.where(b2 > 0, (g - 1) / np.where(b2 > 0, b2, 1), 0)
    E = g * (p4[:, 0] + bp)
    p = p4[:, 1:] + (g2 * bp + g * p4[:, 0])[:, None] * beta
    return np.column_stack([E, p])


def two_body(rng, M, m1, m2, n):
    """Isotropic two-body decay at rest; returns p4 of daughter 1 and 2."""
    M = np.broadcast_to(M, (n,)).astype(float)
    m1 = np.broadcast_to(m1, (n,)).astype(float)
    m2 = np.broadcast_to(m2, (n,)).astype(float)
    p = np.sqrt(np.maximum((M ** 2 - (m1 + m2) ** 2) * (M ** 2 - (m1 - m2) ** 2), 0)) / (2 * M)
    u = random_unit(rng, n)
    p1 = np.column_stack([np.sqrt(p ** 2 + m1 ** 2), p[:, None] * u])
    p2 = np.column_stack([np.sqrt(p ** 2 + m2 ** 2), -p[:, None] * u])
    return p1, p2


def decay_to_ee(rng, pV):
    """Vector (or virtual photon) four-vector pV (N,4) -> e+ e-, 1 + cos^2 about its flight direction."""
    n = pV.shape[0]
    M = np.sqrt(np.maximum(pV[:, 0] ** 2 - np.sum(pV[:, 1:] ** 2, axis=1), 0))
    pmag = np.sqrt(np.maximum(M ** 2 / 4 - ME ** 2, 0))
    # axis = flight direction
    pv = pV[:, 1:]
    nv = np.linalg.norm(pv, axis=1)
    ax = pv / np.where(nv > 0, nv, 1)[:, None]
    ax[nv == 0] = [0, 0, 1]
    # orthonormal frame
    tmp = np.where(np.abs(ax[:, 2:3]) < 0.9, np.array([[0, 0, 1.0]]), np.array([[1.0, 0, 0]]))
    e1 = np.cross(ax, tmp)
    e1 /= np.linalg.norm(e1, axis=1)[:, None]
    e2 = np.cross(ax, e1)
    c = sample_1pcos2(rng, n)
    s = np.sqrt(1 - c ** 2)
    ph = rng.uniform(0, 2 * np.pi, n)
    u = c[:, None] * ax + (s * np.cos(ph))[:, None] * e1 + (s * np.sin(ph))[:, None] * e2
    E = np.sqrt(pmag ** 2 + ME ** 2)
    a = np.column_stack([E, pmag[:, None] * u])
    b = np.column_stack([E, -pmag[:, None] * u])
    beta = pv / pV[:, 0:1]
    return boost(a, beta), boost(b, beta)


def kroll_wada(M, mP):
    """d BR / dM per unit BR(gamma gamma) [1/GeV] (form factor = 1)."""
    x = (M / mP) ** 2
    r = (ME / M) ** 2
    return 4 * ALPHA / (3 * np.pi * M) * (1 - x) ** 3 * (1 + 2 * r) * np.sqrt(np.maximum(1 - 4 * r, 0))


def sample_kw(rng, n, mP, lo, hi):
    M = np.linspace(lo, hi, 20001)
    f = kroll_wada(M, mP)
    c = np.cumsum(f)
    c /= c[-1]
    return np.interp(rng.random(n), c, M)


def kw_integral(mP, lo, hi):
    M = np.linspace(lo, hi, 20001)
    return float(np.trapezoid(kroll_wada(M, mP), M))


def parents(rng, n, kind, system):
    """Parent four-vectors (N,4) with Tsallis pT, flat y in |y| < Y_GEN, flat phi."""
    m = MASS[kind]
    sp = SPECTRA[system]
    pt = tsallis_pt(rng, n, m, sp['n'], sp['T'])
    y = rng.uniform(-Y_GEN, Y_GEN, n)
    ph = rng.uniform(0, 2 * np.pi, n)
    mt = np.sqrt(pt ** 2 + m ** 2)
    return np.column_stack([mt * np.cosh(y), pt * np.cos(ph), pt * np.sin(ph), mt * np.sinh(y)])


def p_to_gamma_v(rng, P, mP, mV):
    """P (N,4) -> gamma + V(mass mV, scalar or array); returns (gamma p4, V p4) in the lab."""
    n = P.shape[0]
    g, v = two_body(rng, mP, 0.0, mV, n)
    beta = P[:, 1:] / P[:, 0:1]
    return boost(g, beta), boost(v, beta)


def gen_pairs(rng, n, source, system, m_x=M_X17, dal_band=(0.008, 0.030)):
    """Return dict with e+ / e- lab four-vectors (N,4) and a per-pair weight.

    source: 'x17_pi0', 'x17_eta' (weight = 1 per X17 produced; multiply by BR later),
            'dal_pi0', 'dal_eta' (weight = Dalitz BR per parent in the band / N),
            'scan:<p>' monochromatic X17 at |p| = p GeV, |eta_X| < 0.5.
    Weights are 'per parent produced per unit rapidity' once divided by n/(2 Y_GEN).
    """
    if source.startswith('scan:'):
        p = float(source.split(':')[1])
        eta = rng.uniform(-0.5, 0.5, n)
        ph = rng.uniform(0, 2 * np.pi, n)
        th = 2 * np.arctan(np.exp(-eta))
        u = np.column_stack([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)])
        V = np.column_stack([np.full(n, np.sqrt(p ** 2 + m_x ** 2)), p * u])
        ep, em = decay_to_ee(rng, V)
        return dict(ep=ep, em=em, w=np.full(n, 1.0), mtrue=np.full(n, m_x))
    kind = source.split('_')[1]
    mP = MASS[kind]
    P = parents(rng, n, kind, system)
    if source.startswith('x17'):
        _, V = p_to_gamma_v(rng, P, mP, m_x)
        w = np.full(n, 1.0)
        mt = np.full(n, m_x)
    else:
        M = sample_kw(rng, n, mP, *dal_band)
        _, V = p_to_gamma_v(rng, P, mP, M)
        w = np.full(n, BR_GG[kind] * kw_integral(mP, *dal_band))
        mt = M
    ep, em = decay_to_ee(rng, V)
    return dict(ep=ep, em=em, w=w, mtrue=mt)


def gen_photons(rng, n, system):
    """Photons from pi0 -> gamma gamma (both photons), weight 1 per photon per pi0 thrown."""
    P = parents(rng, n, 'pi0', system)
    g1, g2 = two_body(rng, MPI0, 0.0, 0.0, n)
    beta = P[:, 1:] / P[:, 0:1]
    g = np.vstack([boost(g1, beta), boost(g2, beta)])
    return g


def bh_split(rng, n):
    """Energy fraction of the electron in a high-energy conversion: dsigma/dx ~ 1 - 4/3 x(1-x)."""
    out = np.empty(n)
    k = 0
    while k < n:
        x = rng.random(2 * (n - k) + 10)
        keep = x[rng.random(x.size) < 1 - 4 / 3 * x * (1 - x)]
        take = min(keep.size, n - k)
        out[k:k + take] = keep[:take]
        k += take
    return out


def eta_over_pi0(system, high_pt_ratio=0.48):
    """Integrated eta/pi0 under mT scaling, normalised to 0.48 at high pT (PHENIX/ALICE)."""
    sp = SPECTRA[system]
    pt = np.linspace(0, 20, 200001)
    out = []
    for m in (MPI0, META):
        mt = np.sqrt(pt ** 2 + m ** 2)
        out.append(np.trapezoid(pt * (1 + (mt - MPI0) / (sp['n'] * sp['T'])) ** (-sp['n']), pt))
    return high_pt_ratio * out[1] / out[0]
