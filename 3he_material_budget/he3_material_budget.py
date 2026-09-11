import numpy as np
import matplotlib.pyplot as plt


def highland_scattering_angle(E_k, x, X0, z=1):
    """
    Calculate the RMS scattering angle using the Highland formula.

    Parameters:
    E_k : float or array-like, kinetic energy of the electron/positron in MeV
    x   : float or array-like, material thickness in cm
    X0  : float, radiation length of the material in cm
    z   : int, charge of the incident particle (1 for e-/e+)

    Returns:
    Scattering angle in degrees.
    """
    m_e = 0.51099895  # Electron mass in MeV/c^2

    # Calculate momentum and velocity (beta)
    E_tot = E_k + m_e
    p = np.sqrt(E_tot ** 2 - m_e ** 2)
    beta = p / E_tot

    ratio = x / X0
    ratio = np.maximum(ratio, 1e-12)  # Prevent log(0) for zero-thickness evaluation

    # Highland formula (returns radians)
    theta_rad = (13.6 / (beta * p)) * z * np.sqrt(ratio) * (1 + 0.038 * np.log(ratio))

    return np.degrees(theta_rad)


# Material dictionary: { 'Name': X0_in_cm }
materials = {
    'Kapton': 28.6,
    'Mylar': 28.5,
    'Aluminum': 8.9,
    'Beryllium': 35.28,
    'Carbon Fiber': 25.0  # Approximate average for typical composites
}

# ---------------------------------------------------------
# Plot 1: Scattering Angle vs. Energy (Fixed Thickness)
# ---------------------------------------------------------
fixed_thickness_um = 10.0  # 10 microns
x_fixed = fixed_thickness_um * 1e-4  # convert to cm
energies = np.linspace(1, 10, 500)

plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
for mat, X0 in materials.items():
    angles = highland_scattering_angle(energies, x_fixed, X0)
    plt.plot(energies, angles, label=mat, linewidth=2)

plt.title(f'Scattering Angle vs. Energy\n(Thickness = {fixed_thickness_um} $\mu$m)')
plt.xlabel('Kinetic Energy (MeV)')
plt.ylabel(r'RMS Scattering Angle $\theta_0$ (degrees)')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

# ---------------------------------------------------------
# Plot 2: Scattering Angle vs. Thickness (Fixed Energy)
# ---------------------------------------------------------
fixed_energy_mev = 1.0  # 1 MeV
thicknesses_um = np.linspace(1, 100, 500)  # 1 to 100 microns
x_var = thicknesses_um * 1e-4

plt.subplot(1, 2, 2)
for mat, X0 in materials.items():
    angles = highland_scattering_angle(fixed_energy_mev, x_var, X0)
    plt.plot(thicknesses_um, angles, label=mat, linewidth=2)

# Highlight the 1-degree target limit
plt.axhline(1.0, color='red', linestyle=':', label='1 Degree Target')

plt.title(f'Scattering Angle vs. Thickness\n(Energy = {fixed_energy_mev} MeV)')
plt.xlabel(r'Thickness ($\mu$m)')
plt.ylabel(r'RMS Scattering Angle $\theta_0$ (degrees)')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

plt.tight_layout()
plt.show()