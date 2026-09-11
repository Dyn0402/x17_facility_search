"""Parametric model of the mylar-wrap / carbon-rod-cage 3He cell for GANIL/NFS.

The concept: no pressure shell at all.  Six pultruded carbon-fibre rods run the
length of the cell between two endcaps and act as longitudinal formers.  A
double-aluminised mylar sheet is bonded to the flat rod at top, wrapped once
around the rod cage, and bonded again on top of itself over that same flat rod.
The mylar is the entire gas barrier, so the radial material budget collapses to
the foil plus the 3He column.

The price is that a foil cannot carry hoop stress at any real overpressure, so
this is a near-zero-differential cell (see `membrane_stress`); the trade against
the 30 bar Be/CFRP option in ../docs/anchor_vessel.py is rate, not resolution.

Geometry convention: z along the beam, +y up, the flat bonding rod at top.
All lengths in mm unless stated.  Run directly for the design report.
"""

import json
from dataclasses import dataclass, asdict, field

import numpy as np

# ---------------------------------------------------------------- materials --
# Radiation lengths in g/cm2 and densities in g/cm3 (PDG), matching
# docs/anchor_vessel.py so the two studies stay comparable.
X0 = {'He3': 70.7, 'Mylar': 39.95, 'Al': 24.01, 'CFRP': 42.70, 'He4': 94.32}
RHO = {'Mylar': 1.40, 'Al': 2.699, 'CFRP': 1.55}

M_HE3 = 3.016e-3          # kg/mol
R_GAS = 8.314             # J/(mol K)
ME = 0.51099895           # MeV

LAND_DEFAULT = 15.0   # axial length of the endcap land the mylar skirt bonds onto

# n_TOF as-built radial budget, from docs/PLAN_GANIL_NFS.md, for reference.
NTOF_BUDGET = 0.0123      # x/X0
NTOF_AREAL = 0.2508       # g/cm2 of 3He


def he3_density(p_bar, T=293.15):
    """3He density in g/cm3 at p_bar absolute."""
    return p_bar * 101325.0 * M_HE3 / (R_GAS * T) / 1000.0


def highland(p_mev, x_over_x0):
    """Highland RMS projected scattering angle in degrees for an e+/e-."""
    x = max(x_over_x0, 1e-12)
    beta = p_mev / np.sqrt(p_mev * p_mev + ME * ME)
    return np.degrees((13.6 / (beta * p_mev)) * np.sqrt(x) * (1 + 0.038 * np.log(x)))


# ------------------------------------------------------------------ params ---
@dataclass
class VesselParams:
    """Design parameters.  Defaults sit mid-range of the GANIL beam spec."""

    # beam and envelope
    d_beam: float = 60.0          # beam diameter, spec is 40-80
    clearance: float = 4.0        # radial gap, beam envelope -> mylar inner face
    l_cyl: float = 300.0          # rod length between endcap faces, spec 200-400

    # rod cage
    n_rod: int = 6                # total rods, one of which is the flat one
    d_thin: float = 2.0           # round carbon rod diameter
    w_flat: float = 12.0          # flat bonding rod width (tangential)
    t_flat: float = 1.5           # flat bonding rod thickness (radial)

    # skin
    t_mylar: float = 0.012        # mylar foil thickness (12 um)
    t_al: float = 4.0e-5          # aluminium per side (40 nm), double aluminised
    seam_overlap: float = 10.0    # mylar-on-mylar bond width over the flat rod
    t_glue: float = 0.03          # glue bondline thickness
    bulge: float = 0.0            # facet sagitta from overpressure, 0 = taut

    # endcaps (material TBD - placeholder geometry only)
    t_endcap: float = 8.0
    endcap_margin: float = 6.0    # radial land outside the rod envelope

    # operating point
    p_bar: float = 1.0            # absolute 3He fill pressure
    dp_mbar: float = 10.0         # differential across the mylar
    t_kelvin: float = 293.15
    p_ref_mev: float = 10.0       # momentum for the Highland quote

    # render-only: the real foil is invisible, so thicken it for the CAD/viewer
    t_skin_render: float = 0.20

    # ------------------------------------------------------------ derived ---
    @property
    def r_thin(self):
        return 0.5 * self.d_thin

    @property
    def dtheta(self):
        """Angular pitch of the rod cage."""
        return 2.0 * np.pi / self.n_rod

    @property
    def r_centre_min(self):
        """Smallest rod-centre radius that still clears the beam.

        The skin's closest approach to the axis is the common external tangent
        between two adjacent round rods: it sits at r_c*cos(dtheta/2) + r_thin.
        """
        need = 0.5 * self.d_beam + self.clearance
        return (need - self.r_thin) / np.cos(0.5 * self.dtheta)

    @property
    def r_centre(self):
        """Rod-centre radius, rounded up to the next whole mm."""
        return float(np.ceil(self.r_centre_min))

    @property
    def r_env(self):
        """Envelope radius: outer surface of the round rods, and the plane of
        the flat rod's outer (bonding) face."""
        return self.r_centre + self.r_thin

    @property
    def facet_clearance(self):
        """Actual radial gap between the beam envelope and the taut skin."""
        return (self.r_centre * np.cos(0.5 * self.dtheta) + self.r_thin
                - 0.5 * self.d_beam)

    def rod_angles(self):
        """Rod azimuths in radians; index 0 is the flat rod, at top (+y)."""
        return np.pi / 2.0 + np.arange(self.n_rod) * self.dtheta


# --------------------------------------------------------------- geometry ----
def _hull(points):
    """Convex hull of a 2D point set, CCW, via Andrew's monotone chain.

    A membrane pulled taut over convex formers lies exactly on their convex
    hull, so this *is* the mylar cross-section for bulge = 0.
    """
    pts = sorted(set(map(tuple, np.round(points, 9))))
    if len(pts) < 3:
        return np.array(pts)

    def half(seq):
        out = []
        for p in seq:
            while len(out) >= 2:
                (ax, ay), (bx, by) = out[-2], out[-1]
                if (bx - ax) * (p[1] - ay) - (by - ay) * (p[0] - ax) > 1e-12:
                    break
                out.pop()
            out.append(p)
        return out

    lower, upper = half(pts), half(reversed(pts))
    return np.array(lower[:-1] + upper[:-1])


def flat_rod_corners(p: VesselParams):
    """The four corners of the flat bonding rod, outer face on the envelope."""
    th = p.rod_angles()[0]
    rad = np.array([np.cos(th), np.sin(th)])       # radially outward
    tan = np.array([-np.sin(th), np.cos(th)])      # tangential
    outer, inner = p.r_env, p.r_env - p.t_flat
    return np.array([outer * rad + 0.5 * p.w_flat * tan,
                     outer * rad - 0.5 * p.w_flat * tan,
                     inner * rad - 0.5 * p.w_flat * tan,
                     inner * rad + 0.5 * p.w_flat * tan])


def skin_section(p: VesselParams, n_arc=64):
    """Mylar cross-section as a closed CCW polygon (inner surface of the foil).

    Taut: the convex hull of the rod cross-sections.  With p.bulge > 0 each free
    span between contact points is replaced by a circular arc of that sagitta,
    which is what a uniformly loaded membrane actually does.
    """
    cloud = [flat_rod_corners(p)]
    for th in p.rod_angles()[1:]:
        c = p.r_centre * np.array([np.cos(th), np.sin(th)])
        a = np.linspace(0, 2 * np.pi, n_arc, endpoint=False)
        cloud.append(c + p.r_thin * np.column_stack([np.cos(a), np.sin(a)]))
    hull = _hull(np.vstack(cloud))

    if p.bulge <= 0:
        return hull

    # Bow out every edge long enough to be a free span, not an arc facet.
    span_min = 3.0 * max(p.t_flat, p.d_thin)
    out = []
    for i, a in enumerate(hull):
        b = hull[(i + 1) % len(hull)]
        out.append(a)
        chord = np.hypot(*(b - a))
        if chord < span_min:
            continue
        s = p.bulge * chord / (p.r_centre)      # scale sagitta with span length
        rho = (chord ** 2 / 4.0 + s ** 2) / (2.0 * s)
        half = np.arcsin(min(1.0, chord / (2.0 * rho)))
        mid, d = 0.5 * (a + b), (b - a) / chord
        nrm = np.array([d[1], -d[0]])           # outward for a CCW hull
        cen = mid - nrm * (rho - s)
        a0 = np.arctan2(*(a - cen)[::-1])
        for f in np.linspace(0, 1, 12)[1:-1]:
            ang = a0 - 2 * half * f if np.cross(d, nrm) > 0 else a0 + 2 * half * f
            out.append(cen + rho * np.array([np.cos(ang), np.sin(ang)]))
    return np.array(out)


def offset_polygon(poly, t):
    """Offset a convex CCW polygon by t (positive = outward), by vertex bisector."""
    n = len(poly)
    out = np.zeros_like(poly)
    for i in range(n):
        a, b, c = poly[(i - 1) % n], poly[i], poly[(i + 1) % n]
        n1 = np.array([(b - a)[1], -(b - a)[0]]); n1 /= np.linalg.norm(n1)
        n2 = np.array([(c - b)[1], -(c - b)[0]]); n2 /= np.linalg.norm(n2)
        bis = n1 + n2
        norm = np.linalg.norm(bis)
        if norm < 1e-9:
            out[i] = b + t * n1
        else:
            bis /= norm
            out[i] = b + t * bis / max(1e-6, float(np.dot(bis, n1)))
    return out


def polygon_area(poly):
    x, y = poly[:, 0], poly[:, 1]
    return 0.5 * abs(float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def polygon_perimeter(poly):
    return float(np.sum(np.hypot(*(np.roll(poly, -1, axis=0) - poly).T)))


# ------------------------------------------------------------- performance ---
def acceptance(p: VesselParams):
    """Azimuthal shadow of the rod cage, seen from the beam axis."""
    thin = (p.n_rod - 1) * 2.0 * np.arcsin(p.r_thin / p.r_centre)
    flat = 2.0 * np.arctan(0.5 * p.w_flat / p.r_env)
    return dict(thin_rad=thin, flat_rad=flat,
                thin_frac=thin / (2 * np.pi), flat_frac=flat / (2 * np.pi),
                dead_frac=(thin + flat) / (2 * np.pi))


def budget(p: VesselParams):
    """Radial x/X0 on the three distinct exit paths, at normal incidence."""
    rho_he3 = he3_density(p.p_bar, p.t_kelvin)
    r_gas_cm = 0.1 * (p.facet_clearance + 0.5 * p.d_beam)   # axis -> skin
    gas = rho_he3 * r_gas_cm / X0['He3']
    foil = RHO['Mylar'] * 0.1 * p.t_mylar / X0['Mylar']
    alu = RHO['Al'] * 0.1 * (2 * p.t_al) / X0['Al']

    facet = gas + foil + alu
    seam = gas + 2 * (foil + alu) + RHO['CFRP'] * 0.1 * p.t_flat / X0['CFRP']
    # worst chord through a round rod is its full diameter
    rod = gas + foil + alu + RHO['CFRP'] * 0.1 * p.d_thin / X0['CFRP']
    return dict(gas=gas, foil=foil, alu=alu, facet=facet, seam=seam, rod=rod,
                th_facet=highland(p.p_ref_mev, facet),
                th_rod=highland(p.p_ref_mev, rod),
                th_ntof=highland(p.p_ref_mev, NTOF_BUDGET))


def inventory(p: VesselParams):
    """Gas volume and 3He inventory - 3He is the budget line that hurts."""
    area_mm2 = polygon_area(skin_section(p))
    vol_l = area_mm2 * p.l_cyl * 1e-6
    std_l = vol_l * p.p_bar * (273.15 / p.t_kelvin)   # 0 C, 1 bar
    rho = he3_density(p.p_bar, p.t_kelvin)
    areal = rho * 0.1 * p.l_cyl                        # g/cm2 along the beam
    return dict(area_mm2=area_mm2, vol_l=vol_l, std_l=std_l,
                grams=rho * area_mm2 * p.l_cyl * 1e-3,
                areal=areal, areal_rel_ntof=areal / NTOF_AREAL)


def membrane_stress(p: VesselParams, sigma_allow=25.0):
    """Why this cell must run at near-zero differential.

    A taut facet has infinite radius of curvature, so it can carry no pressure
    at all: any overpressure has to bow it out until the hoop stress balances.
    sigma = dp * rho / t, with rho set by the sagitta of the bowed facet.
    PET yields near 100 MPa; hold sigma_allow ~25 MPa against long-term creep.
    """
    dp_mpa = p.dp_mbar * 1e-4                       # 1 mbar = 1e-4 MPa
    chord = 2.0 * p.r_centre * np.sin(0.5 * p.dtheta)
    rho_req = sigma_allow * p.t_mylar / max(dp_mpa, 1e-12)
    sag = chord ** 2 / (8.0 * rho_req)
    # the differential a taut-ish facet can hold if we cap the bulge instead
    dp_at_sag = lambda s: sigma_allow * p.t_mylar / ((chord ** 2 / 4 + s * s) / (2 * s)) * 1e4
    return dict(chord=chord, dp_mpa=dp_mpa, sigma_allow=sigma_allow,
                rho_req=rho_req, sagitta=sag,
                sagitta_frac_clear=sag / max(p.facet_clearance, 1e-9),
                dp_for_1mm_bulge=dp_at_sag(1.0))


def report(p: VesselParams):
    """One dict with everything, also used to seed the interactive viewer."""
    return dict(params=asdict(p),
                derived=dict(r_centre=p.r_centre, r_centre_min=p.r_centre_min,
                             r_env=p.r_env, facet_clearance=p.facet_clearance,
                             across_corners=2 * np.hypot(p.r_env, 0.5 * p.w_flat),
                             perimeter=polygon_perimeter(skin_section(p))),
                acceptance=acceptance(p), budget=budget(p),
                inventory=inventory(p), stress=membrane_stress(p))


# ------------------------------------------------------------------ main -----
def main():
    p = VesselParams()
    d, a, b, inv, s = (report(p)[k] for k in
                       ('derived', 'acceptance', 'budget', 'inventory', 'stress'))

    print("=" * 74)
    print(" 3He mylar-wrap cell, %d-rod carbon cage - GANIL/NFS" % p.n_rod)
    print("=" * 74)
    print("\n-- envelope ------------------------------------------------------")
    print("  beam diameter            %7.1f mm   (spec 40-80)" % p.d_beam)
    print("  cell length              %7.1f mm   (spec 200-400)" % p.l_cyl)
    print("  rod-centre radius        %7.1f mm   (minimum %.2f for %.1f mm clear)"
          % (d['r_centre'], d['r_centre_min'], p.clearance))
    print("  envelope radius          %7.1f mm   across corners %.1f mm"
          % (d['r_env'], d['across_corners']))
    print("  beam -> skin clearance   %7.2f mm   at the mid-facet, the tight spot"
          % d['facet_clearance'])
    print("  wrap length (1 turn)     %7.1f mm   + %.0f mm seam overlap"
          % (d['perimeter'], p.seam_overlap))

    print("\n-- what the rods kill (azimuthal shadow from the axis) -----------")
    print("  %d round rods, %.1f mm     %6.2f %%" % (p.n_rod - 1, p.d_thin, 100 * a['thin_frac']))
    print("  1 flat rod, %.1f mm wide   %6.2f %%" % (p.w_flat, 100 * a['flat_frac']))
    print("  total dead azimuth       %6.2f %%" % (100 * a['dead_frac']))
    print("  -> the single flat rod costs %.1fx one round rod; it dominates."
          % (a['flat_rad'] / (a['thin_rad'] / (p.n_rod - 1))))

    print("\n-- radial material budget at %g bar (x/X0, normal incidence) -----" % p.p_bar)
    print("  3He column (%.1f cm)      %8.5f %%" % (0.1 * (d['facet_clearance'] + 0.5 * p.d_beam), 100 * b['gas']))
    print("  mylar %.0f um              %8.5f %%" % (1000 * p.t_mylar, 100 * b['foil']))
    print("  Al, 2 x %.0f nm            %8.5f %%" % (1e6 * p.t_al, 100 * b['alu']))
    print("  " + "-" * 44)
    print("  through a facet          %8.5f %%   theta0(%.0f MeV) = %.2f deg"
          % (100 * b['facet'], p.p_ref_mev, b['th_facet']))
    print("  through the seam         %8.5f %%" % (100 * b['seam']))
    print("  through a round rod      %8.5f %%   theta0 = %.2f deg"
          % (100 * b['rod'], b['th_rod']))
    print("  n_TOF as built           %8.5f %%   theta0 = %.2f deg"
          % (100 * NTOF_BUDGET, b['th_ntof']))
    print("  -> facet path is %.0fx thinner than n_TOF; a rod is still %.1fx thinner."
          % (NTOF_BUDGET / b['facet'], NTOF_BUDGET / b['rod']))

    print("\n-- 3He inventory and the rate penalty ----------------------------")
    print("  gas volume               %7.2f l      (%.0f mm2 x %.0f mm)"
          % (inv['vol_l'], inv['area_mm2'], p.l_cyl))
    print("  3He inventory            %7.2f std-l  (%.2f g)" % (inv['std_l'], inv['grams']))
    print("  areal density on beam    %7.4f g/cm2  = %.3fx n_TOF"
          % (inv['areal'], inv['areal_rel_ntof']))
    print("  -> resolution is free, rate is not: %.0fx less 3He on the beam"
          % (1.0 / inv['areal_rel_ntof']))

    print("\n-- can the foil hold anything? (sigma_allow = %.0f MPa) ----------" % s['sigma_allow'])
    print("  free span (chord)        %7.1f mm" % s['chord'])
    print("  at dp = %.0f mbar the facet must bow to rho = %.0f mm," % (p.dp_mbar, s['rho_req']))
    print("  i.e. a sagitta of        %7.2f mm  (%.0f %% of the beam clearance)"
          % (s['sagitta'], 100 * s['sagitta_frac_clear']))
    print("  a 1.0 mm bulge holds     %7.1f mbar" % s['dp_for_1mm_bulge'])
    print("  -> a taut foil carries zero dp. Run pressure-balanced, and note the")
    print("     bulge is *outward*, so it costs envelope, never beam clearance.")
    print()

    with open("vessel_design/out/design_point.json", "w") as f:
        json.dump(report(p), f, indent=2, default=float)
    print("  wrote vessel_design/out/design_point.json")


if __name__ == "__main__":
    main()
