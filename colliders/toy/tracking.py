"""Helix tracking toy: vectorised simulation + per-track broken-line fit.

Simulation (vectorised over tracks): a lepton leaves its start point on a helix in
the uniform solenoid field; at every cylinder it reaches on its *outbound* arc it
gets multiple scattering (Highland, with the real crossing angle) and
Bethe-Heitler bremsstrahlung, and leaves a smeared hit if the layer measures.
Loopers are cut at the first turning point (the outbound half-turn only).

Fit (one track at a time, scipy least_squares): the track is assumed primary.
Parameters are the vertex (x0, y0, z0), the direction (phi, lambda) and 1/p at the
vertex, plus two kink angles at every scatterer the track crosses.  Residuals are
the hits, the measured primary vertex, and the kinks over their Highland prior.
This is the optimal (Kalman-equivalent) fit for Gaussian scattering; brems is not
modelled in the fit, as in a standard Kalman without a GSF.

Units: m, GeV, T.  Charge q = +1 for e+.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.optimize import least_squares

K_B = 0.299792458  # GeV / (T m)


def highland(p, t):
    t = np.maximum(t, 1e-12)
    return 0.0136 / p * np.sqrt(t) * (1 + 0.038 * np.log(t))


# ------------------------------------------------------------------ geometry helpers
def _next_crossing(x, y, phi, rho, r):
    """Arc length s > 0 to the first crossing of radius r, the crossing point and new phi.

    Works on numpy arrays.  rho = signed curvature [1/m] (phi increases at rate rho)."""
    sphi, cphi = np.sin(phi), np.cos(phi)
    Cx = x - sphi / rho
    Cy = y + cphi / rho
    Rh = 1 / np.abs(rho)
    d = np.hypot(Cx, Cy)
    ok = (d > 0) & (d <= r + Rh) & (d >= np.abs(r - Rh))
    dd = np.where(d > 0, d, 1)
    a = (r ** 2 - Rh ** 2 + d ** 2) / (2 * dd)
    h = np.sqrt(np.maximum(r ** 2 - a ** 2, 0))
    bx, by = Cx * a / dd, Cy * a / dd
    px, py = -Cy / dd, Cx / dd
    a0 = np.arctan2(y - Cy, x - Cx)
    best_s = np.full(np.shape(x), np.inf)
    best_x = np.zeros(np.shape(x))
    best_y = np.zeros(np.shape(x))
    for sgn in (1, -1):
        X = bx + sgn * h * px
        Y = by + sgn * h * py
        al = np.arctan2(Y - Cy, X - Cx)
        dl = np.where(rho > 0, al - a0, a0 - al) % (2 * np.pi)
        s = dl * Rh
        s = np.where(dl > 1e-9, s, np.inf)
        better = s < best_s
        best_s = np.where(better, s, best_s)
        best_x = np.where(better, X, best_x)
        best_y = np.where(better, Y, best_y)
    ok = ok & np.isfinite(best_s)
    return ok, best_s, best_x, best_y


def _next_crossing_scalar(x, y, phi, rho, r):
    sphi, cphi = math.sin(phi), math.cos(phi)
    Cx = x - sphi / rho
    Cy = y + cphi / rho
    Rh = 1 / abs(rho)
    d = math.hypot(Cx, Cy)
    if d <= 0 or d > r + Rh or d < abs(r - Rh):
        return None
    a = (r * r - Rh * Rh + d * d) / (2 * d)
    h = math.sqrt(max(r * r - a * a, 0.0))
    bx, by = Cx * a / d, Cy * a / d
    px, py = -Cy / d, Cx / d
    a0 = math.atan2(y - Cy, x - Cx)
    best = None
    for sgn in (1, -1):
        X = bx + sgn * h * px
        Y = by + sgn * h * py
        al = math.atan2(Y - Cy, X - Cx)
        dl = ((al - a0) if rho > 0 else (a0 - al)) % (2 * math.pi)
        if dl > 1e-9:
            s = dl * Rh
            if best is None or s < best[0]:
                best = (s, X, Y)
    return best


# ------------------------------------------------------------------ simulation
def simulate(det, ep4, q, start=None, start_layer=None, rng=None, brems=True, ms=True):
    """Propagate N leptons (four-vectors ep4 (N,4), charges q (N,)) through det.

    start: (N,3) start points (default: vertex points given in 'start'); start_layer:
    index of the layer the start point sits on (conversions), or None for a vertex start.
    Returns a dict of per-layer arrays.
    """
    N = ep4.shape[0]
    L = det.layers
    nl = len(L)
    p = np.linalg.norm(ep4[:, 1:], axis=1)
    pt = np.hypot(ep4[:, 1], ep4[:, 2])
    phi = np.arctan2(ep4[:, 2], ep4[:, 1])
    lam = np.arctan2(ep4[:, 3], pt)
    x, y, z = start[:, 0].copy(), start[:, 1].copy(), start[:, 2].copy()
    alive = np.ones(N, bool)
    reached = np.zeros((N, nl), bool)
    hphi = np.zeros((N, nl))
    hz = np.zeros((N, nl))
    hit = np.zeros((N, nl), bool)
    p_at = np.zeros((N, nl))
    t_at = np.zeros((N, nl))

    def interact(i, sel, frac=1.0):
        nonlocal phi, lam, p
        Ly = L[i]
        if Ly.t <= 0:
            return
        cosl = np.cos(lam[sel])
        rr = np.hypot(x[sel], y[sel])
        cosa = np.abs(x[sel] * np.cos(phi[sel]) + y[sel] * np.sin(phi[sel])) / np.maximum(rr, 1e-9)
        teff = frac * Ly.t / (np.maximum(cosa, 0.02) * np.maximum(cosl, 0.02))
        p_at[sel, i] = p[sel]
        t_at[sel, i] = teff
        if ms:
            th0 = highland(p[sel], teff)
            k1 = rng.normal(0, 1, sel.sum()) * th0
            k2 = rng.normal(0, 1, sel.sum()) * th0
            phi[sel] = phi[sel] + k1 / np.maximum(cosl, 0.02)
            lam[sel] = lam[sel] + k2
        if brems:
            g = rng.gamma(teff / math.log(2), 1.0)
            p[sel] = p[sel] * np.exp(-g)

    first = 0
    if start_layer is not None:
        i = start_layer
        Ly = L[i]
        reached[:, i] = True
        if Ly.meas:
            hit[:, i] = np.abs(z) < Ly.zmax
            hphi[:, i] = np.arctan2(y, x) + rng.normal(0, Ly.s_rphi / Ly.r, N)
            hz[:, i] = z + rng.normal(0, Ly.s_z, N)
        interact(i, alive.copy(), 0.5)
        first = i + 1
    for i in range(first, nl):
        Ly = L[i]
        if start_layer is None:
            pass
        sel = alive.copy()
        if not sel.any():
            break
        ptc = p[sel] * np.cos(lam[sel])
        rho = -q[sel] * K_B * det.B / np.maximum(ptc, 1e-6)
        ok, s, X, Y = _next_crossing(x[sel], y[sel], phi[sel], rho, Ly.r)
        idx = np.where(sel)[0]
        dead = idx[~ok]
        alive[dead] = False
        idx = idx[ok]
        s, X, Y, rho = s[ok], X[ok], Y[ok], rho[ok]
        x[idx], y[idx] = X, Y
        phi[idx] = phi[idx] + rho * s
        z[idx] = z[idx] + s * np.tan(lam[idx])
        out = np.abs(z) > 3.0
        alive[out] = False
        inz = np.zeros(N, bool)
        inz[idx] = np.abs(z[idx]) < Ly.zmax
        reached[inz, i] = True
        if Ly.meas:
            m = inz
            hit[m, i] = True
            hphi[m, i] = np.arctan2(y[m], x[m]) + rng.normal(0, Ly.s_rphi / Ly.r, m.sum())
            hz[m, i] = z[m] + rng.normal(0, Ly.s_z, m.sum())
        interact(i, inz)
    return dict(reached=reached, hit=hit, hphi=hphi, hz=hz, p_at=p_at, t_at=t_at)


def hit_counts(det, sim):
    groups = {}
    for i, Ly in enumerate(det.layers):
        if Ly.meas:
            groups.setdefault(Ly.group, np.zeros(sim['hit'].shape[0], int))
            groups[Ly.group] += sim['hit'][:, i] * Ly.rep
    return groups


def passes(det, sim):
    g = hit_counts(det, sim)
    ok = np.ones(sim['hit'].shape[0], bool)
    for grp, nmin in det.need.items():
        ok &= g.get(grp, 0) >= nmin
    return ok


# ------------------------------------------------------------------ fit
class TrackFit:
    """Broken-line fit of one track to its hits, assuming a primary track."""

    def __init__(self, det, hits, q, vtx_meas, init, p_prior):
        """hits: list of (layer index, phi, z); init: (x,y,z,phi,lam,p); p_prior: p for the kink priors."""
        self.det = det
        self.q = q
        self.B = det.B
        self.hits = hits
        self.vtx = vtx_meas
        rmax = max(det.layers[i].r for i, _, _ in hits)
        hit_layers = {i for i, _, _ in hits}
        self.use = [i for i, Ly in enumerate(det.layers)
                    if Ly.r <= rmax + 1e-9 and (Ly.t > 0 or i in hit_layers)]
        self.scat = [i for i in self.use if det.layers[i].t > 0]
        self.init = np.array(list(init) + [0.0] * (2 * len(self.scat)))
        self.init[5] = 1 / init[5]
        # kink priors from a no-kink propagation of the initial track
        teff = self._teffs(self.init)
        self.th0 = np.array([float(highland(p_prior, max(t, 1e-6))) for t in teff])
        self.hidx = {i: k for k, (i, _, _) in enumerate(hits)}

    def _teffs(self, par):
        x, y, z, phi, lam, ip = par[:6]
        out = []
        p = 1 / ip
        for i in self.use:
            Ly = self.det.layers[i]
            rho = -self.q * K_B * self.B / (p * math.cos(lam))
            c = _next_crossing_scalar(x, y, phi, rho, Ly.r)
            if c is None:
                if Ly.t > 0:
                    out.append(Ly.t)
                continue
            s, x, y = c
            phi += rho * s
            z += s * math.tan(lam)
            if Ly.t > 0:
                cosa = abs(x * math.cos(phi) + y * math.sin(phi)) / Ly.r
                out.append(Ly.t / (max(cosa, 0.02) * max(math.cos(lam), 0.02)))
        return out

    def residuals(self, par):
        det = self.det
        x, y, z, phi, lam, ip = par[:6]
        ip = max(ip, 1e-3)
        p = 1 / ip
        kinks = par[6:]
        res = [(x - self.vtx[0]) / det.s_vtx_xy, (y - self.vtx[1]) / det.s_vtx_xy,
               (z - self.vtx[2]) / det.s_vtx_z]
        hres = [None] * len(self.hits)
        k = 0
        failed = False
        for i in self.use:
            Ly = det.layers[i]
            if not failed:
                rho = -self.q * K_B * self.B / (p * max(math.cos(lam), 1e-3))
                c = _next_crossing_scalar(x, y, phi, rho, Ly.r)
                if c is None:
                    failed = True
                else:
                    s, x, y = c
                    phi += rho * s
                    z += s * math.tan(lam)
            if i in self.hidx:
                j = self.hidx[i]
                _, hp, hz = self.hits[j]
                if failed:
                    hres[j] = (50.0, 50.0)
                else:
                    dphi = (math.atan2(y, x) - hp + math.pi) % (2 * math.pi) - math.pi
                    hres[j] = (dphi * Ly.r / Ly.s_rphi, (z - hz) / Ly.s_z)
            if Ly.t > 0:
                k1, k2 = kinks[2 * k], kinks[2 * k + 1]
                if not failed:
                    phi += k1 / max(math.cos(lam), 0.02)
                    lam += k2
                k += 1
        for hr in hres:
            res.extend(hr)
        res.extend(list(kinks / np.repeat(self.th0, 2)))
        return np.array(res)

    def fit(self):
        sc = np.concatenate([[1e-4, 1e-4, 1e-4, 1e-3, 1e-3, 0.1 * abs(self.init[5])],
                             np.repeat(np.maximum(self.th0, 1e-5), 2)])
        r = least_squares(self.residuals, self.init, method='lm', x_scale=sc, max_nfev=300)
        chi2 = float(np.sum(r.fun ** 2))
        ndf = len(r.fun) - len(r.x)
        x, y, z, phi, lam, ip = r.x[:6]
        p = 1 / ip
        pt = p * math.cos(lam)
        return dict(px=pt * math.cos(phi), py=pt * math.sin(phi), pz=pt * math.tan(lam),
                    chi2=chi2, ndf=ndf, ok=r.success)


def fit_track(det, sim, j, q, vtx_meas, init, p_prior):
    hits = [(i, sim['hphi'][j, i], sim['hz'][j, i]) for i in np.where(sim['hit'][j])[0]]
    return TrackFit(det, hits, q, vtx_meas, init, p_prior).fit()


class ConvPairFit:
    """Fit both legs as a photon conversion on the cylinder of layer `li`: a common start point
    (phi_c, z_c on radius r_L), a common direction, zero opening angle, separate momenta, kinks on
    every scatterer outside r_L (half the start layer's thickness at the start).  No vertex constraint.
    Its chi2 is the conversion-hypothesis test: real conversions fit (chi2 ~ ndf), X17 / Dalitz pairs
    with a real opening angle do not."""

    def __init__(self, det, li, legs, init_dir, init_p, init_z):
        """legs: [(hits, q), (hits, q)]; init_dir: (phi, lam); init_p: (p1, p2)."""
        self.det = det
        self.li = li
        self.rL = det.layers[li].r
        self.B = det.B
        self.legs = []
        for (hits, q), p in zip(legs, init_p):
            rmax = max(det.layers[i].r for i, _, _ in hits)
            hl = {i for i, _, _ in hits}
            use = [i for i, Ly in enumerate(det.layers)
                   if self.rL < Ly.r <= rmax + 1e-9 and (Ly.t > 0 or i in hl)]
            scat = [i for i in use if det.layers[i].t > 0]
            start_hit = [h for h in hits if h[0] == li]
            other = [h for h in hits if h[0] != li and det.layers[h[0]].r < self.rL]
            self.legs.append(dict(hits={h[0]: h for h in hits if h[0] != li}, q=q, use=use, scat=scat,
                                  start_hit=start_hit[0] if start_hit else None, inner=other, p=p))
        phi, lam = init_dir
        self.init = [math.atan2(math.sin(phi), math.cos(phi)), init_z, phi, lam, 1 / init_p[0], 1 / init_p[1]]
        for L in self.legs:
            tstart = 0.5 * det.layers[li].t / max(math.cos(lam), 0.02)
            th = [highland(L['p'], max(tstart, 1e-6))]
            for i in L['scat']:
                th.append(highland(L['p'], max(det.layers[i].t / max(math.cos(lam), 0.02), 1e-6)))
            L['th0'] = np.array(th, float)
            self.init += [0.0] * (2 * len(th))
        self.init = np.array(self.init)

    def residuals(self, par):
        det = self.det
        phic, zc, phi0, lam0 = par[:4]
        ips = par[4:6]
        res = []
        off = 6
        for L, ip in zip(self.legs, ips):
            nk = len(L['th0'])
            kinks = par[off:off + 2 * nk]
            off += 2 * nk
            x, y, z = self.rL * math.cos(phic), self.rL * math.sin(phic), zc
            phi, lam = phi0, lam0
            p = 1 / max(ip, 1e-3)
            if L['start_hit'] is not None:
                Ly = det.layers[self.li]
                _, hp, hz = L['start_hit']
                dphi = (phic - hp + math.pi) % (2 * math.pi) - math.pi
                res += [dphi * Ly.r / Ly.s_rphi, (z - hz) / Ly.s_z]
            # hits inside the conversion radius cannot belong to this hypothesis
            res += [30.0, 30.0] * len(L['inner'])
            phi += kinks[0] / max(math.cos(lam), 0.02)
            lam += kinks[1]
            k = 1
            failed = False
            for i in L['use']:
                Ly = det.layers[i]
                if not failed:
                    rho = -L['q'] * K_B * self.B / (p * max(math.cos(lam), 1e-3))
                    c = _next_crossing_scalar(x, y, phi, rho, Ly.r)
                    if c is None:
                        failed = True
                    else:
                        s, x, y = c
                        phi += rho * s
                        z += s * math.tan(lam)
                if i in L['hits']:
                    _, hp, hz = L['hits'][i]
                    if failed:
                        res += [50.0, 50.0]
                    else:
                        dphi = (math.atan2(y, x) - hp + math.pi) % (2 * math.pi) - math.pi
                        res += [dphi * Ly.r / Ly.s_rphi, (z - hz) / Ly.s_z]
                if Ly.t > 0:
                    if not failed:
                        phi += kinks[2 * k] / max(math.cos(lam), 0.02)
                        lam += kinks[2 * k + 1]
                    k += 1
            res += list(kinks / np.repeat(L['th0'], 2))
        return np.array(res)

    def fit(self):
        sc = [1e-3, 1e-3, 1e-3, 1e-3, 0.1 * abs(self.init[4]), 0.1 * abs(self.init[5])]
        for L in self.legs:
            sc += list(np.repeat(np.maximum(L['th0'], 1e-5), 2))
        r = least_squares(self.residuals, self.init, method='lm', x_scale=np.array(sc), max_nfev=600)
        return float(np.sum(r.fun ** 2)), len(r.fun) - len(r.x)
