"""How long a low-pressure 3He cell has to be to stop the PF1B beam.

Folds the measured H113 spectrum with the 1/v 3He absorption cross section and
reports, per fill pressure, the gas length that absorbs a given fraction of the
*neutrons* (particle flux, not capture flux), and where along the beam they stop.

Spectrum: Abele et al., nucl-ex/0510072, Eq. (11) fitted to the H113 capture
flux spectrum (Fig. 4): dPhi_C/dlambda ~ (l/l2)^p / (1 + (l/l2)^p) * exp(-l/l1),
l1 = 0.33 nm, l2 = 0.40 nm, p = 3, valid above 0.1 nm.  Particle flux is
dPhi/dlambda = (lambda0/lambda) dPhi_C/dlambda with lambda0 = 1.8 A.

    python ill/cell_length.py           # table to stdout, CSV + figure to ill/out/
"""

from pathlib import Path

import numpy as np

SIGMA0_B = 5333.0          # 3He(n,p) at 1.8 A, b
LAMBDA0_A = 1.8
KB = 1.380649e-23
T_K = 293.15
L1, L2, P_EXP = 3.3, 4.0, 3.0      # A (paper's nm x 10)

lam = np.linspace(1.0, 25.0, 4801)            # A; the fit holds above 1 A
cap = (lam / L2) ** P_EXP / (1 + (lam / L2) ** P_EXP) * np.exp(-lam / L1)
part = cap * LAMBDA0_A / lam                   # particle-flux spectrum
part /= np.trapezoid(part, lam)


def n_per_cm3(p_bar):
    return p_bar * 1e5 / (KB * T_K) * 1e-6


def mu_cm(p_bar, lam_A, spin_factor=1.0):
    """Absorption coefficient, 1/cm.  spin_factor = 1 -/+ P for polarised 3He."""
    return n_per_cm3(p_bar) * SIGMA0_B * 1e-24 * (lam_A / LAMBDA0_A) * spin_factor


def absorbed(p_bar, L_cm, spin_factor=1.0):
    return np.trapezoid(part * (1 - np.exp(-mu_cm(p_bar, lam, spin_factor) * L_cm)), lam)


def length_for(frac, p_bar, spin_factor=1.0):
    lo, hi = 0.0, 1e4
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if absorbed(p_bar, mid, spin_factor) < frac else (lo, mid)
    return 0.5 * (lo + hi)


def depth_quantile(q, p_bar, L_cm, spin_factor=1.0):
    """Depth below which a fraction q of the neutrons absorbed in a cell of length L stop."""
    tot = absorbed(p_bar, L_cm, spin_factor)
    return length_for(q * tot, p_bar, spin_factor)


#: the three cells of the first Geant4 scan (HANDOFF_SIM.md): pressure [bar],
#: gas length [cm] for 99.5 % absorption
SCAN_CELLS = ((1.0, 30.0), (2.0, 15.0), (3.0, 10.0))


def depth_pdf(p_bar, L_cm, n=3001, spin_factor=1.0):
    """Stop-depth density of the absorbed neutrons (same law for (n,p) and
    (n,gamma): both are 1/v), normalised over [0, L]."""
    y = np.linspace(0, L_cm, n)
    pdf = np.array([np.trapezoid(part * mu_cm(p_bar, lam, spin_factor)
                                 * np.exp(-mu_cm(p_bar, lam, spin_factor) * yy), lam) for yy in y])
    return y, pdf / np.trapezoid(pdf, y)


def main():
    out = Path(__file__).parent / 'out'
    out.mkdir(exist_ok=True)
    mean_lam_part = np.trapezoid(part * lam, lam)
    capw = cap / np.trapezoid(cap, lam)
    print(f"H113 spectrum: particle-mean lambda = {mean_lam_part:.2f} A, "
          f"capture/particle = {np.trapezoid(part * lam / LAMBDA0_A, lam):.2f} "
          f"(paper: 2.7), capture-weighted mean = {np.trapezoid(capw * lam, lam):.2f} A")
    print(f"10th percentile of neutrons below {lam[np.searchsorted(np.cumsum(part) / part.sum(), 0.1)]:.2f} A")

    rows = []
    cases = [('unpolarised', 1.0)] + [(f'polarised parallel, P={P}', 1 - P) for P in (0.70, 0.75, 0.80)]
    print("\ncase                         p[bar]  L90[cm]  L95[cm]  L99[cm]  L99.9[cm] | in L95: median / 90% depth [cm]")
    for name, sf in cases:
        for p in (0.5, 1.0, 1.5, 2.0, 3.0):
            Ls = {f: length_for(f, p, sf) for f in (0.90, 0.95, 0.99, 0.999)}
            d50 = depth_quantile(0.5, p, Ls[0.95], sf)
            d90 = depth_quantile(0.9, p, Ls[0.95], sf)
            rows.append(dict(case=name, p_bar=p, L90=Ls[0.90], L95=Ls[0.95], L99=Ls[0.99], L999=Ls[0.999],
                             median_depth_in_L95=d50, d90_in_L95=d90))
            print(f"{name:28s} {p:5.1f}  {Ls[0.90]:7.1f}  {Ls[0.95]:7.1f}  {Ls[0.99]:7.1f}  {Ls[0.999]:8.1f}  |  {d50:5.1f} / {d90:5.1f}")

    import csv
    # stop-depth law for each scan cell: the Geant4 validation target (V0) and
    # the placement rule (entrance window at -median)
    print("\nscan cells: depth of (n,p) = (n,gamma) production")
    with open(out / 'cell_depth.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['p_bar', 'L_cm', 'depth_cm', 'pdf_per_cm', 'cdf'])
        for p, L in SCAN_CELLS:
            y, pdf = depth_pdf(p, L)
            cdf = np.concatenate([[0], np.cumsum(0.5 * (pdf[1:] + pdf[:-1]) * np.diff(y))])
            q = lambda f: float(np.interp(f, cdf, y))
            print(f"  {p:.0f} bar x {L:.0f} cm: absorbed {absorbed(p, L):.4f}, median {q(.5):.2f}, "
                  f"mean {np.trapezoid(pdf * y, y):.2f}, 10/90/99 % {q(.1):.2f}/{q(.9):.2f}/{q(.99):.2f} cm")
            for i in range(0, len(y), 10):
                w.writerow([p, L, f'{y[i]:.3f}', f'{pdf[i]:.6g}', f'{cdf[i]:.6f}'])

    # the gun's input: H113 particle-flux spectrum, normalised to 1, 0.025 A bins, fit valid above 1 A
    with open(out / 'h113_spectrum.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['lambda_A', 'dPhi_dlambda_per_A', 'E_meV'])
        for l, v in zip(lam[::5], part[::5]):
            w.writerow([f'{l:.3f}', f'{v:.6g}', f'{81.804 / l**2:.5g}'])
    with open(out / 'cell_length.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

    # escape fraction vs length at 1 bar, for the figure
    Ls = np.linspace(0, 60, 241)
    curves = {p: np.array([1 - absorbed(p, L) for L in Ls]) for p in (0.5, 1.0, 2.0, 3.0)}
    with open(out / 'cell_escape.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['L_cm'] + [f'escape_{p}bar' for p in curves])
        for i, L in enumerate(Ls):
            w.writerow([f'{L:.2f}'] + [f'{curves[p][i]:.5g}' for p in curves])

    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7, 4.2))
        for p, c in curves.items():
            ax.semilogy(Ls, c, label=f'{p:g} bar')
        for fr in (0.1, 0.05, 0.01):
            ax.axhline(fr, color='0.75', lw=0.8, zorder=0)
        ax.axvline(36, color='0.5', ls='--', lw=0.8)
        ax.text(36.5, 0.5, 'MM active length', color='0.4', fontsize=8, rotation=90, va='top')
        ax.set_xlabel('³He length along the beam [cm]')
        ax.set_ylabel('fraction of PF1B neutrons that escape')
        ax.set_ylim(1e-4, 1)
        ax.set_title('Unpolarised ³He on the H113 spectrum, 293 K', loc='left', fontsize=11)
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(out / 'figures' / 'cell_escape.png', dpi=150)
    except ImportError:
        pass


if __name__ == '__main__':
    main()
