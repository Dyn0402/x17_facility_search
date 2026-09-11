"""NFS (Neutrons For Science, GANIL/SPIRAL-2) beam model.

Everything needed to put an NFS neutron beam into a simulation:

  * the thick-target d+Be double-differential neutron yield, from the
    Serber-hybrid parameterisation of Morrell & Bernstein, PRC 108, 024616
    (2023) / arXiv:2212.00218, integrated over the deuteron slowing-down;
  * the facility geometry (converter, collimator, flight paths, spot sizes);
  * time-of-flight / wrap-around / energy-resolution helpers.

The model is *shape* physics.  It is renormalised to the measured NFS flux
(Pavon-Rodriguez et al., EPJ A 61, 277 (2025)) by `absolute_scale()`, so the
absolute numbers this module produces are anchored to data, not to theory.

Units, everywhere: MeV, cm, sr, seconds.  Yields are per uC of *deuteron*
charge on the converter unless stated otherwise.

See README.md for provenance of every number and for the measured anchors
this model is checked against.
"""

from __future__ import annotations

import numpy as np

# --------------------------------------------------------------------------
# Physical constants
# --------------------------------------------------------------------------
M_D = 1875.612928        # deuteron mass, MeV
M_N = 939.56542          # neutron mass, MeV
M_E = 0.51099895         # electron mass, MeV
C_CM_S = 2.99792458e10   # cm/s
E_B_DEUTERON = 2.225     # deuteron binding energy, MeV
R0 = 1.25                # fm, radius parameter used by the Serber model
Q_9BE_DN = 4.36          # MeV, Q value of 9Be(d,n)10B used for the nuclear temp.
ELEM_CHARGE = 1.602176634e-19   # C

# --------------------------------------------------------------------------
# Converter material (9Be, the NFS thick rotating converter)
# --------------------------------------------------------------------------
BE_Z = 4
BE_A = 9.0121831         # g/mol
BE_RHO = 1.848           # g/cm3
BE_I = 63.7e-6           # mean excitation energy, MeV
N_AVO = 6.02214076e23

BE_NUMBER_DENSITY = BE_RHO * N_AVO / BE_A     # nuclei / cm3


# --------------------------------------------------------------------------
# Deuteron stopping in the converter
# --------------------------------------------------------------------------
def stopping_power_d_be(e_d):
    """Deuteron mass stopping power in Be, MeV cm^2/g (Bethe, no shell/Barkas).

    Good to a few percent above ~5 MeV; below ~2 MeV it is not to be trusted,
    but that region contributes almost nothing to the neutron yield because
    the breakup cross section has already switched off (Eq. 4 of Morrell).
    """
    e_d = np.atleast_1d(np.asarray(e_d, dtype=float))
    out = np.zeros_like(e_d)
    good = e_d > 0.5
    t = e_d[good]
    gamma = 1.0 + t / M_D
    beta2 = 1.0 - 1.0 / gamma**2
    tmax = 2.0 * M_E * beta2 * gamma**2       # non-relativistic-limit Tmax
    arg = np.maximum(tmax / BE_I, 1.0 + 1e-12)
    out[good] = (
        0.307075 * (BE_Z / BE_A) / beta2 * (np.log(arg) - beta2)
    )
    return np.maximum(out, 1e-6) if out.size > 1 else float(np.maximum(out, 1e-6)[0])


def deuteron_range_be(e_d, n_steps=4000, e_low=1.0):
    """CSDA range in cm of a deuteron of energy `e_d` (MeV) in Be.

    Integrated down to `e_low`; the residual range below 1 MeV is a few
    microns and is ignored.
    """
    e = np.linspace(e_low, e_d, n_steps)
    dedx = np.asarray(stopping_power_d_be(e)) * BE_RHO   # MeV/cm
    return float(np.trapezoid(1.0 / dedx, e))


# --------------------------------------------------------------------------
# Component cross sections (Morrell & Bernstein, Eqs. 4, 8, 9), mb
# --------------------------------------------------------------------------
ETA_BU = 9.4             # MeV, breakup slope parameter
W_D = 0.37 * E_B_DEUTERON  # MeV, breakup energy-distribution width parameter

# Coulomb barrier at R = r0 (A^1/3 + 2^1/3), for the incident deuteron (Z=1)
_R_COUL = R0 * (BE_A ** (1.0 / 3.0) + 2.0 ** (1.0 / 3.0))
E_COUL = 1.43996 * 1 * BE_Z / _R_COUL      # MeV  (~1.38 MeV for Be)


def sigma_breakup(e_d):
    """Total breakup neutron-production cross section, mb (Eq. 4)."""
    e_d = np.asarray(e_d, dtype=float)
    return 57.2 * (BE_A ** (1.0 / 3.0) + 2.0 ** (1.0 / 3.0)) / (
        1.0 + np.exp((22.3 - e_d) / ETA_BU)
    )


def sigma_compound(e_d):
    """Total compound (evaporation) neutron-production cross section, mb (Eq. 8)."""
    e_d = np.asarray(e_d, dtype=float)
    return 80.6 * (
        np.exp(-0.5 * ((18.0 - e_d) / 14.0) ** 2)
        + 0.3 / (1.0 + np.exp((18.0 - e_d) / 7.0))
    )


def sigma_preeq(e_d):
    """Total pre-equilibrium neutron-production cross section, mb (Eq. 9)."""
    e_d = np.asarray(e_d, dtype=float)
    return 34.2 / (1.0 + np.exp((22.0 - e_d) / 6.0))


def sigma_total_reaction(e_d):
    """Total reaction cross section used for the transmission factor, mb (Eq. 17)."""
    e_d = np.asarray(e_d, dtype=float)
    c1, a1, a2 = 5.643, 131.3, 1.354
    geom = R0**2 * (BE_A ** (1.0 / 3.0) + 0.8) ** 2 * 10.0  # fm^2 -> mb
    return sigma_breakup(e_d) + geom * c1 * np.exp(-e_d / a1) * (
        1.0 - np.exp(-e_d / a2)
    )


# --------------------------------------------------------------------------
# Energy distributions
# --------------------------------------------------------------------------
def _p_breakup_raw(e_n, e_d):
    eps = e_d - E_COUL
    num = eps * W_D
    den = np.pi * ((np.asarray(e_n, dtype=float) - 0.5 * eps) ** 2 + W_D * eps) ** 1.5
    return np.where(np.asarray(e_n, dtype=float) > 0, num / den, 0.0)


_NORM_GRID_N = 2000


def p_breakup_energy(e_n, e_d):
    """Serber breakup neutron energy PDF, 1/MeV (Eq. 5).

    Normalised on the physical support [0, e_d] using a fixed internal grid,
    so the result does not depend on the grid the caller asks for.
    """
    ref = np.linspace(0.0, e_d, _NORM_GRID_N)
    norm = np.trapezoid(_p_breakup_raw(ref, e_d), ref)
    p = _p_breakup_raw(e_n, e_d)
    return p / norm if norm > 0 else p * 0.0


def _kT(e_d, kind):
    """Nuclear temperature, MeV (Eqs. 13, 14)."""
    s = np.sqrt(max(e_d + Q_9BE_DN, 0.0))
    return 0.1 + 0.27 * s if kind == "compound" else 0.75 + 0.63 * s


def _p_watt_raw(e_n, e_d, kt):
    e_n = np.asarray(e_n, dtype=float)
    return np.where(
        (e_n > 0) & (e_n <= e_d),
        np.sinh(np.sqrt(2.0 * np.abs(e_n))) * np.exp(-e_n / kt),
        0.0,
    )


def p_watt_energy(e_n, e_d, kind):
    """Watt neutron energy PDF, 1/MeV (Eq. 12), normalised on [0, e_d]
    using a fixed internal grid (caller-grid independent)."""
    kt = _kT(e_d, kind)
    ref = np.linspace(0.0, e_d, _NORM_GRID_N)
    norm = np.trapezoid(_p_watt_raw(ref, e_d, kt), ref)
    p = _p_watt_raw(e_n, e_d, kt)
    return p / norm if norm > 0 else p * 0.0


# --------------------------------------------------------------------------
# Angular distributions, all normalised so that int P dOmega = 1  [1/sr]
# --------------------------------------------------------------------------
def theta0_breakup(e_d):
    """Serber breakup angular width parameter, radians (Eq. 6)."""
    eps = e_d - E_COUL
    return 0.72 * np.sqrt(E_B_DEUTERON / eps) * (1.0 - e_d / (8.0 * M_D))


def p_breakup_angle(theta, e_d):
    """Serber breakup angular PDF, 1/sr (Eq. 6)."""
    th0 = theta0_breakup(e_d)
    theta = np.asarray(theta, dtype=float)
    return th0 / (2.0 * np.pi * (th0**2 + theta**2) ** 1.5)


def kalbach_a(e_d, e_n):
    """Kalbach 'little a' slope parameter (Kalbach, PRC 37, 2350 (1988)).

    Entrance channel d + 9Be -> 11B*, exit channel n + 10B.  Separation
    energies from the 1988 systematics' mass table are approximated with the
    experimental values: S_d(11B) = 15.32 MeV, S_n(11B) = 11.45 MeV.
    """
    s_a, s_b = 15.32, 11.45
    # channel energies in the CM
    e_a_cm = e_d * BE_A / (BE_A + 2.0)
    e_a = e_a_cm + s_a
    e_b = np.asarray(e_n, dtype=float) + s_b
    e_a = max(e_a, 1e-6)
    x1 = e_b * min(e_a, 130.0) / e_a
    x3 = e_b * min(e_a, 41.0) / e_a
    m_b = 1.0                      # neutron ejectile
    return 0.04 * x1 + 1.8e-6 * x1**3 + 6.7e-7 * m_b * x3**4


def p_kalbach_angle(theta, a, kind):
    """Kalbach-Mann angular PDF, 1/sr (Eqs. 10, 11), with the Morrell
    beryllium adjustments a_CM = 1.1 a, a_PE = 1.8 a."""
    a = np.asarray(a, dtype=float) * (1.1 if kind == "compound" else 1.8)
    a = np.clip(a, 1e-6, 60.0)
    mu = np.cos(np.asarray(theta, dtype=float))
    if kind == "compound":
        return (a / np.sinh(a)) * np.cosh(a * mu) / (4.0 * np.pi)
    return (a / np.sinh(a)) * np.exp(a * mu) / (4.0 * np.pi)


# --------------------------------------------------------------------------
# Thick-target integration
# --------------------------------------------------------------------------
def transmission(e_d_grid, e_d0):
    """Deuteron transmission factor tau (Eq. 16) on a descending energy grid."""
    dedx = np.asarray(stopping_power_d_be(e_d_grid)) * BE_RHO  # MeV/cm
    integrand = sigma_total_reaction(e_d_grid) * 1e-27 * BE_NUMBER_DENSITY / dedx
    tau = np.empty_like(e_d_grid)
    for i, _ in enumerate(e_d_grid):
        mask = e_d_grid >= e_d_grid[i]
        tau[i] = np.exp(-np.trapezoid(integrand[mask], e_d_grid[mask]))
    return np.clip(tau, 0.0, 1.0)


def thick_target_yield(
    e_n,
    theta=0.0,
    e_d0=40.0,
    n_ed=200,
    e_d_min=2.0,
    components=False,
):
    """Thick-target double-differential neutron yield d2Y/dOmega/dE_n.

    Returns n / (uC sr MeV) at neutron energies `e_n` (MeV) and emission
    angle `theta` (rad), for an incident deuteron energy `e_d0` (MeV) fully
    stopped in Be.

    With `components=True`, returns (total, dict of the three components).
    """
    e_n = np.asarray(e_n, dtype=float)
    e_d_grid = np.linspace(e_d_min, e_d0, n_ed)
    dedx = np.asarray(stopping_power_d_be(e_d_grid)) * BE_RHO   # MeV/cm
    tau = transmission(e_d_grid, e_d0)

    # deuterons per uC
    d_per_uC = 1e-6 / ELEM_CHARGE

    acc = {k: np.zeros_like(e_n) for k in ("breakup", "compound", "preeq")}
    for i, ed in enumerate(e_d_grid):
        # path-length weight: number of target nuclei per unit dE
        w = BE_NUMBER_DENSITY / dedx[i] * tau[i] * 1e-27   # (mb -> cm2) * cm/MeV
        acc["breakup"] += (
            sigma_breakup(ed) * w
            * p_breakup_energy(e_n, ed) * p_breakup_angle(theta, ed)
        )
        a_kal = kalbach_a(ed, e_n)
        acc["compound"] += (
            sigma_compound(ed) * w
            * p_watt_energy(e_n, ed, "compound")
            * p_kalbach_angle(theta, a_kal, "compound")
        )
        acc["preeq"] += (
            sigma_preeq(ed) * w
            * p_watt_energy(e_n, ed, "preeq")
            * p_kalbach_angle(theta, a_kal, "preeq")
        )

    de = e_d_grid[1] - e_d_grid[0]
    for k in acc:
        acc[k] *= de * d_per_uC
    total = acc["breakup"] + acc["compound"] + acc["preeq"]
    return (total, acc) if components else total


# --------------------------------------------------------------------------
# Absolute normalisation against the measured NFS flux
# --------------------------------------------------------------------------
NFS_PEAK_EN = 17.0                 # MeV
NFS_PEAK_YIELD = 17.3e9            # n / uC / sr / MeV   (+-0.5e9)
NFS_PEAK_YIELD_ERR = 0.5e9


def absolute_scale(e_d0=40.0, **kw):
    """Scale factor bringing the model onto the measured NFS flux at 17 MeV."""
    model = float(thick_target_yield(np.array([NFS_PEAK_EN]), e_d0=e_d0, **kw)[0])
    return NFS_PEAK_YIELD / model


def nfs_flux_0deg(e_n, e_d0=40.0, normalise=True, **kw):
    """NFS 0-degree thick-target d+Be spectrum, n/uC/sr/MeV, data-normalised."""
    y = thick_target_yield(e_n, theta=0.0, e_d0=e_d0, **kw)
    return y * absolute_scale(e_d0=e_d0, **kw) if normalise else y


# --------------------------------------------------------------------------
# Facility geometry and derived rates
# --------------------------------------------------------------------------
COLLIMATOR_DIAMETER_CM = 2.555     # as used for the 2025 PS-PPAC campaign
COLLIMATOR_TO_TARGET_CM = 305.29   # collimator exit -> first U target
CONVERTER_TO_TARGET_CM = 740.6     # converter -> first U target
BEAM_DIAMETER_AT_740_CM = 4.44     # measured spot diameter there
BEAM_DIVERGENCE_RAD = 3.08e-3      # measured, half-angle
BEAM_EDGE_1090_CM = 0.49           # 10-90% fall-off width
SOLID_ANGLE_AT_740 = 28.2e-6       # sr, measured


def converter_to_collimator_exit_cm():
    """Distance converter -> collimator exit implied by the measured geometry."""
    return CONVERTER_TO_TARGET_CM - COLLIMATOR_TO_TARGET_CM


def beam_diameter_cm(distance_cm, collimator_diameter_cm=COLLIMATOR_DIAMETER_CM):
    """Umbra+penumbra beam diameter at `distance_cm` from the converter,
    for a pinhole collimator of the given aperture.

    Straight-line projection from a point source at the converter through the
    collimator aperture; the measured 44.4 mm spot at 740.6 cm is reproduced
    to better than 1 mm by this, so the source can be treated as a point.
    """
    l_c = converter_to_collimator_exit_cm()
    return collimator_diameter_cm * distance_cm / l_c


def solid_angle_sr(distance_cm, collimator_diameter_cm=COLLIMATOR_DIAMETER_CM):
    """Solid angle subtended by the collimated beam at the converter, sr."""
    r = 0.5 * beam_diameter_cm(distance_cm, collimator_diameter_cm)
    return np.pi * r**2 / distance_cm**2


def fluence_rate(e_n, distance_cm, current_uA, e_d0=40.0, **kw):
    """Differential fluence rate at the beam axis, n / (cm2 s MeV).

    d2Y/dOmega/dE is per steradian, so on-axis the fluence rate is simply
    Y * I / L^2 -- independent of the collimator aperture (the aperture sets
    the *area* illuminated, not the on-axis intensity).
    """
    y = nfs_flux_0deg(np.asarray(e_n), e_d0=e_d0, **kw)
    return y * current_uA / distance_cm**2


def integrated_rate(e_lo, e_hi, distance_cm, current_uA, e_d0=40.0, n=400, **kw):
    """Neutrons / (cm2 s) on axis between `e_lo` and `e_hi` MeV."""
    grid = np.linspace(e_lo, e_hi, n)
    return float(
        np.trapezoid(fluence_rate(grid, distance_cm, current_uA, e_d0=e_d0, **kw), grid)
    )


# --------------------------------------------------------------------------
# Time of flight
# --------------------------------------------------------------------------
def tof_ns(e_n, flight_path_m):
    """Relativistic neutron time of flight, ns."""
    e_n = np.asarray(e_n, dtype=float)
    gamma = 1.0 + e_n / M_N
    beta = np.sqrt(1.0 - 1.0 / gamma**2)
    return flight_path_m * 100.0 / (beta * C_CM_S) * 1e9


def energy_from_tof(t_ns, flight_path_m):
    """Inverse of `tof_ns`: neutron kinetic energy, MeV."""
    beta = flight_path_m * 100.0 / (np.asarray(t_ns, dtype=float) * 1e-9) / C_CM_S
    beta = np.clip(beta, 1e-9, 1 - 1e-12)
    return M_N * (1.0 / np.sqrt(1.0 - beta**2) - 1.0)


def wraparound_limit_MeV(rep_rate_Hz, flight_path_m):
    """Slowest neutron energy that still arrives inside one beam period.

    Neutrons below this energy are overlapped by the next bunch and their
    time of flight is ambiguous.
    """
    period_ns = 1e9 / rep_rate_Hz
    gamma_flash_ns = flight_path_m * 100.0 / C_CM_S * 1e9
    return float(energy_from_tof(period_ns + gamma_flash_ns, flight_path_m))


def energy_resolution(e_n, flight_path_m, dt_ns=1.0, dL_cm=1.0):
    """Fractional neutron energy resolution dE/E from TOF (Ledoux & Ridikas).

        dE/E = gamma (gamma + 1) sqrt( (dt/t)^2 + (dL/L)^2 )
    """
    e_n = np.asarray(e_n, dtype=float)
    gamma = 1.0 + e_n / M_N
    t = tof_ns(e_n, flight_path_m)
    return gamma * (gamma + 1.0) * np.hypot(dt_ns / t, dL_cm / (flight_path_m * 100.0))


def plot(path=None):
    """Overview figure: 0-deg spectrum with components, and the measured band."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    grid = np.geomspace(0.05, 45.0, 400)
    tot, comp = thick_target_yield(grid, components=True)
    s = absolute_scale()

    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.plot(grid, tot * s, "k-", lw=2, label="total (renormalised)")
    ax.plot(grid, comp["breakup"] * s, "-", color="C0", label="breakup (Serber)")
    ax.plot(grid, comp["compound"] * s, "-", color="C1", label="compound (Watt)")
    ax.plot(grid, comp["preeq"] * s, "-", color="C2", label="pre-equilibrium")
    ax.errorbar([NFS_PEAK_EN], [NFS_PEAK_YIELD], yerr=[NFS_PEAK_YIELD_ERR],
                fmt="r*", ms=16, zorder=5, label="measured peak (P25)")
    ax.axhline(1e9, color="0.6", ls=":", lw=1)
    ax.axvspan(1.5, 35.0, color="C3", alpha=0.06)
    ax.text(1.7, 1.15e9, "P25: > $10^9$ over 1.5-35 MeV", color="0.35", fontsize=8)
    ax.axvspan(0.05, 1.5, color="0.85", alpha=0.7, zorder=0)
    ax.text(0.09, 2.5e10, "unmeasured\nat NFS", fontsize=8, color="0.35")
    ax.axvspan(0.2, 2.0, color="C4", alpha=0.15, zorder=0)
    ax.text(0.23, 1.3e7, "X17 window", fontsize=8, color="C4")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.05, 45)
    ax.set_ylim(1e7, 4e10)
    ax.set_xlabel("neutron energy [MeV]")
    ax.set_ylabel(r"$d^2Y/d\Omega dE_n$  [n / $\mu$C / sr / MeV]")
    ax.set_title("NFS 0$^\\circ$ spectrum, d(40 MeV) + 8 mm Be")
    ax.legend(fontsize=8, loc="lower right", framealpha=0.95)
    ax.grid(alpha=0.25, which="both")
    fig.tight_layout()

    if path is None:
        import os
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "data", "nfs_spectrum.png")
    fig.savefig(path, dpi=150)
    return path


# --------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    print(f"Deuteron range in Be at 40 MeV : {deuteron_range_be(40.0)*10:.2f} mm"
          f"   (converter is 8 mm -> fully stopped)")
    print(f"Serber theta0 at 40 MeV        : {np.degrees(theta0_breakup(40.0)):.2f} deg")
    print(f"Coulomb term E_c               : {E_COUL:.3f} MeV")

    scale = absolute_scale()
    print(f"\nModel -> data scale factor     : {scale:.3f}"
          "   (1.0 would mean the parameterisation is absolutely correct)")

    grid = np.geomspace(0.05, 45.0, 400)
    flux = nfs_flux_0deg(grid)
    peak_i = int(np.argmax(flux))
    print(f"Model peak                     : {flux[peak_i]/1e9:.1f}e9 at "
          f"{grid[peak_i]:.1f} MeV   (measured: 17.3e9 at 17.0 MeV)")

    for lo, hi, want in ((1.5, 35.0, 1e9), (1.5, 42.0, 1e8)):
        sub = flux[(grid >= lo) & (grid <= hi)]
        print(f"  min flux over {lo}-{hi} MeV: {sub.min():.2e} "
              f"(paper says > {want:.0e})")

    print("\n  E_n [MeV]   Y0 [n/uC/sr/MeV]   TOF@7.4m [ns]   dE/E@7.4m")
    for e in (0.1, 0.2, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0, 17.0, 25.0, 35.0, 40.0):
        y = float(nfs_flux_0deg(np.array([e]))[0])
        print(f"  {e:8.2f}   {y:14.3e}   {float(tof_ns(e,7.4)):11.1f}   "
              f"{float(energy_resolution(e,7.4)):9.4f}")

    if "--write" in sys.argv:
        import os

        grid = np.geomspace(0.05, 45.0, 500)
        tot, comp = thick_target_yield(grid, components=True)
        s = absolute_scale()
        here = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(here, "data", "nfs_dbe40_0deg_model.csv")
        header = (
            "NFS 0-deg thick-target d(40 MeV)+Be neutron yield.\n"
            "Serber-hybrid model of Morrell & Bernstein, PRC 108 024616 (2023),\n"
            "renormalised by x%.4f to the measured NFS peak of 17.3e9 n/uC/sr/MeV\n"
            "at 17 MeV (Pavon-Rodriguez et al., EPJ A 61, 277 (2025)).\n"
            "Below 1.5 MeV this is an EXTRAPOLATION -- no NFS measurement exists there.\n"
            "E_n_MeV,Y_total,Y_breakup,Y_compound,Y_preeq   [n/uC/sr/MeV]" % s
        )
        np.savetxt(
            path,
            np.column_stack(
                [grid, tot * s, comp["breakup"] * s, comp["compound"] * s,
                 comp["preeq"] * s]
            ),
            delimiter=",",
            header=header,
            fmt="%.6e",
        )
        print(f"\nwrote {path}")
        print(f"wrote {plot()}")
