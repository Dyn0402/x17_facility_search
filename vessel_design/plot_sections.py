"""Cross-section and longitudinal section of the mylar-wrap 3He cell."""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Polygon, Rectangle

from mylar_wrap_vessel import (LAND_DEFAULT, VesselParams, acceptance, budget,
                               flat_rod_corners, inventory, offset_polygon,
                               skin_section)

C_CARBON = "#23262b"
C_MYLAR = "#9aa7b4"
C_GAS = "#8fd3ff"
C_BEAM = "#f0b429"
C_CAP = "#b0a08c"
C_GLUE = "#d1495b"


def draw_cross_section(ax, p):
    lim0 = p.r_env + p.endcap_margin + 10
    inner = skin_section(p)
    outer = offset_polygon(inner, 0.35)          # drawn thick to be visible

    ax.add_patch(Polygon(inner, closed=True, fc=C_GAS, ec="none", alpha=0.30, zorder=1))
    ax.add_patch(Polygon(outer, closed=True, fc="none", ec=C_MYLAR, lw=2.6, zorder=4))
    ax.add_patch(Circle((0, 0), 0.5 * p.d_beam, fc=C_BEAM, ec=C_BEAM,
                        alpha=0.16, lw=1.4, ls="--", zorder=2))

    for th in p.rod_angles()[1:]:
        c = p.r_centre * np.array([np.cos(th), np.sin(th)])
        ax.add_patch(Circle(c, p.r_thin, fc=C_CARBON, ec="k", lw=0.5, zorder=5))
    ax.add_patch(Polygon(flat_rod_corners(p), closed=True, fc=C_CARBON,
                         ec="k", lw=0.5, zorder=5))

    # the two glue lines on the flat rod: sheet-to-rod, then sheet-to-sheet
    th = p.rod_angles()[0]
    rad = np.array([np.cos(th), np.sin(th)]); tan = np.array([-np.sin(th), np.cos(th)])
    for k, lab in ((0, "bond 1: mylar to flat rod"), (1, "bond 2: mylar onto mylar")):
        r0 = p.r_env + k * 0.75
        a = r0 * rad + 0.5 * p.w_flat * tan
        b = r0 * rad - 0.5 * p.w_flat * tan
        ax.plot(*np.column_stack([a, b]), color=C_GLUE, lw=3.0, solid_capstyle="butt",
                zorder=6, label=lab)
    # the second wrap, riding over the first on top of the flat rod
    w = 0.5 * (p.w_flat + p.seam_overlap)
    r0 = p.r_env + 1.15
    ax.plot([r0 * rad[0] + w * tan[0], r0 * rad[0] - w * tan[0]],
            [r0 * rad[1] + w * tan[1], r0 * rad[1] - w * tan[1]],
            color=C_MYLAR, lw=3.0, zorder=7, solid_capstyle="butt")
    ax.annotate("seam: wrap ends here,\n%.0f mm overlap" % p.seam_overlap,
                xy=(w * tan[0], r0 * rad[1]), xytext=(0.62 * lim0, 0.93 * lim0),
                fontsize=7.5, ha="left", va="bottom",
                arrowprops=dict(arrowstyle="->", lw=0.9, color="#555",
                                connectionstyle="arc3,rad=-0.25"))

    # annotate the tight dimension: mid-facet clearance
    thm = p.rod_angles()[2] - 0.5 * p.dtheta
    n = np.array([np.cos(thm), np.sin(thm)])
    r_in = p.r_centre * np.cos(0.5 * p.dtheta) + p.r_thin
    ax.annotate("", xy=tuple(r_in * n), xytext=tuple(0.5 * p.d_beam * n),
                arrowprops=dict(arrowstyle="<->", color="k", lw=1.1))
    ax.annotate("%.1f mm\nclearance\n(tightest)" % p.facet_clearance,
                xy=tuple((r_in + 1) * n), xytext=(-0.90 * lim0, 0.42 * lim0),
                fontsize=7.5, ha="left", va="bottom",
                arrowprops=dict(arrowstyle="->", lw=0.9, color="#555"))

    ax.set_xlim(-lim0, lim0); ax.set_ylim(-lim0, lim0)
    ax.set_aspect("equal"); ax.axis("off")
    a = acceptance(p)
    ax.set_title("Cross-section: %d-rod cage\n$r_c$ = %.0f mm, envelope $\\varnothing$ %.1f mm\n"
                 "%.1f %% of the azimuth blocked by rods"
                 % (p.n_rod, p.r_centre, 2 * p.r_env, 100 * a["dead_frac"]), fontsize=9)
    ax.legend(loc="lower left", fontsize=7, frameon=False)


def draw_long_section(ax, p):
    inv = inventory(p)
    half = 0.5 * p.l_cyl
    r_in = p.r_centre * np.cos(0.5 * p.dtheta) + p.r_thin
    r_disc = p.r_env + p.endcap_margin

    ax.add_patch(Rectangle((-half, -r_in), p.l_cyl, 2 * r_in, fc=C_GAS,
                           ec="none", alpha=0.30))
    ax.add_patch(Rectangle((-half - 40, -0.5 * p.d_beam), p.l_cyl + 80,
                           p.d_beam, fc=C_BEAM, ec="none", alpha=0.16))
    for s in (-1, 1):
        ax.plot([-half, half], [s * r_in, s * r_in], color=C_MYLAR, lw=2.6,
                label="mylar skin, %.0f $\\mu$m" % (1000 * p.t_mylar) if s > 0 else None)
        ax.add_patch(Rectangle((s * half - (p.t_endcap if s > 0 else 0), -r_disc),
                               p.t_endcap, 2 * r_disc, fc=C_CAP, ec="k", lw=0.6))
        ax.add_patch(Rectangle((s * half - (LAND_DEFAULT if s > 0 else 0), -r_in),
                               LAND_DEFAULT, 2 * r_in, fc=C_CAP, ec="k", lw=0.6,
                               alpha=0.55))
    # the flat rod in elevation, and one round rod behind it
    ax.add_patch(Rectangle((-half, p.r_env - p.t_flat), p.l_cyl, p.t_flat,
                           fc=C_CARBON, ec="none", label="carbon rods"))
    ax.add_patch(Rectangle((-half, -p.r_centre - p.r_thin), p.l_cyl, p.d_thin,
                           fc=C_CARBON, ec="none"))
    ax.annotate("", xy=(-half, -r_disc - 8), xytext=(half, -r_disc - 8),
                arrowprops=dict(arrowstyle="<->", color="k", lw=1.1))
    ax.text(0, -r_disc - 14, "L = %.0f mm  (spec 200-400)" % p.l_cyl,
            ha="center", va="top", fontsize=8)
    ax.text(0, 0, "$^3$He, %.2f l  (%.2f std-l)" % (inv["vol_l"], inv["std_l"]),
            ha="center", va="center", fontsize=8, color="#2a6f97")
    ax.text(half + 14, 0, "beam\n$\\varnothing$ %.0f mm" % p.d_beam,
            fontsize=8, color="#8a6d1f", va="center")
    ax.annotate("endcap, material TBD;\nmylar skirt bonds to this land",
                xy=(-half + 0.5 * LAND_DEFAULT, r_in), xytext=(-half + 26, r_disc + 6),
                fontsize=7, va="bottom",
                arrowprops=dict(arrowstyle="->", lw=0.9, color="#555"))

    ax.set_xlim(-half - 44, half + 52); ax.set_ylim(-r_disc - 30, r_disc + 26)
    ax.set_aspect("equal"); ax.axis("off")
    b = budget(p)
    ax.set_title("Longitudinal section — radial exit budget through a facet "
                 "%.4f %% $X_0$ ($\\theta_0$ = %.2f$^\\circ$ at 10 MeV)"
                 % (100 * b["facet"], b["th_facet"]), fontsize=9)
    ax.legend(loc="lower right", fontsize=7, frameon=False)


def main():
    p = VesselParams()
    fig = plt.figure(figsize=(14.5, 4.9), constrained_layout=True)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 2.45])
    draw_cross_section(fig.add_subplot(gs[0]), p)
    draw_long_section(fig.add_subplot(gs[1]), p)
    fig.suptitle("$^3$He mylar-wrap cell for the GANIL/NFS X17 search — "
                 "carbon rod cage, single-wrap double-aluminised mylar barrier",
                 fontsize=11)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "sections.png")
    fig.savefig(out, dpi=190)
    print("wrote", out)


if __name__ == "__main__":
    main()
