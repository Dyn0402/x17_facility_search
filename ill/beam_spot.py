"""PF1B (H113) open-beam flux density away from the guide exit, and what a
collimated spot of a given size delivers.

Model: Abele et al., nucl-ex/0510072, Eqs. (17)-(18).  At wavelength lambda the
guide exit (2d0 x 2h0 = 6 cm wide x 20 cm high) emits uniformly over its area and
isotropically within |theta|, |theta'| <= kappa_eff * lambda, kappa_eff =
0.017 rad/nm.  The paper validates this against the measured horizontal profile
at 0.5 m (flat to ~5 %).  Brightness spectrum: Eq. (11) fit to the on-axis
capture brightness, lambda1 = 2.6 A, lambda2 = 2.4 A, p = 3.  Neutron (particle)
counts weight it by lambda0/lambda.

    python ill/beam_spot.py      # tables to stdout, CSV + figure to ill/out/
"""

from pathlib import Path

import numpy as np

KAPPA = 0.0017            # rad per Angstrom (0.017 rad/nm)
D0, H0 = 3.0, 10.0        # half width, half height of the H113 exit [cm]
L1, L2, P_EXP = 2.6, 2.4, 3.0
LAMBDA0 = 1.8
PHI_PART_0 = 2.0e10 / 2.71     # particle flux density at the exit, full power [n/cm2/s]
POWER = 46.2 / 57.0            # recent cycles

lam = np.linspace(1.0, 25.0, 2401)
bright_part = (lam / L2) ** P_EXP / (1 + (lam / L2) ** P_EXP) * np.exp(-lam / L1) * LAMBDA0 / lam


def opening(half, x, z, lam_A):
    """Eq. (18): accepted angle in one plane at transverse offset x, distance z [cm]."""
    k = KAPPA * lam_A
    if z <= 0:
        return np.where(np.abs(x) <= half, 2 * k, 0.0)
    hi = np.minimum(k, (half - x) / z)
    lo = np.maximum(-k, -(half + x) / z)
    return np.clip(hi - lo, 0.0, None)


def flux(x, y, z):
    """Particle flux density relative to the exit centre."""
    num = np.trapezoid(bright_part * opening(D0, x, z, lam) * opening(H0, y, z, lam), lam)
    den = np.trapezoid(bright_part * (2 * KAPPA * lam) ** 2, lam)
    return num / den


def main():
    out = Path(__file__).parent / 'out'
    zs = [0.0, 50.0, 100.0, 200.0, 300.0]

    print("On-axis particle flux density vs distance from the H113 exit (relative to the exit):")
    zz = np.linspace(0, 400, 81)
    onaxis = np.array([flux(0, 0, z) for z in zz])
    for z in (0, 25, 50, 100, 150, 200, 300, 400):
        print(f"  z = {z:4.0f} cm : {flux(0, 0, z):.3f}")

    print("\nHorizontal profile (the 6 cm direction), relative to the exit centre:")
    xs = np.linspace(-6, 6, 241)
    prof = {z: np.array([flux(x, 0, z) for x in xs]) for z in zs}
    print("  x[cm]  " + "  ".join(f"z={z:3.0f}" for z in zs))
    for x in (0, 1, 2, 2.5, 3, 3.5, 4, 5):
        print(f"  {x:4.1f}   " + "  ".join(f"{flux(x, 0, z):5.3f}" for z in zs))

    # spot: a round aperture of radius a, at distance z (the aperture defines the
    # spot; inside it the density is the open-beam density there)
    print(f"\nRate into a round spot, particle n/s at {POWER*57:.1f} MW "
          f"(exit density {PHI_PART_0*POWER:.2e} n/cm2/s):")
    print("  Ø[cm]   " + "  ".join(f"z={z:3.0f}" for z in zs))
    rows = []
    for dia in (1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0):
        a = dia / 2
        rr = np.linspace(0, a, 41)
        line = []
        for z in zs:
            # average over the disk: azimuthal samples at each radius
            ph = np.linspace(0, 2 * np.pi, 48, endpoint=False)
            vals = np.array([[flux(r * np.cos(p), r * np.sin(p), z) for p in ph] for r in rr]).mean(axis=1)
            mean = np.trapezoid(vals * rr, rr) / np.trapezoid(rr, rr) if a > 0 else vals[0]
            rate = mean * PHI_PART_0 * POWER * np.pi * a * a
            rows.append(dict(diameter_cm=dia, z_cm=z, mean_rel_density=mean, rate_n_per_s=rate))
            line.append(f"{rate:8.2e}")
        print(f"  {dia:4.1f}  " + "  ".join(line))

    import csv
    with open(out / 'beam_spot.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    with open(out / 'beam_profile_h.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['x_cm'] + [f'z{z:.0f}cm' for z in zs])
        for i, x in enumerate(xs):
            w.writerow([f'{x:.2f}'] + [f'{prof[z][i]:.4f}' for z in zs])

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8))
    for z in zs:
        a1.plot(xs, prof[z], label=f'{z:.0f} cm')
    a1.axvspan(-3, 3, color='0.92', zorder=0)
    a1.set_xlabel('horizontal position [cm]  (exit is ±3 cm, shaded)')
    a1.set_ylabel('flux density / exit centre')
    a1.legend(title='distance from exit', frameon=False, fontsize=8)
    a1.set_title('Open H113 beam, horizontal profile', loc='left', fontsize=10)
    a2.plot(zz, onaxis)
    a2.set_xlabel('distance from guide exit [cm]')
    a2.set_ylabel('on-axis flux density / exit')
    a2.set_ylim(0, 1.05)
    a2.set_title('On-axis density falls once the exit no longer fills the divergence', loc='left', fontsize=10)
    fig.tight_layout()
    fig.savefig(out / 'figures' / 'beam_profile.png', dpi=150)


if __name__ == '__main__':
    main()
