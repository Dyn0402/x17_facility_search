# Polarised n + polarised ³He at the ILL — everything found, 2026-10-01

The idea: ³He(n,p) and the E0 pairs come **only** from the spin-singlet
entrance channel (0⁺, ¹S₀). The radiative capture and the M1 pairs come
**only** from the triplet (1⁺, ³S₁). Polarise both the neutrons and the ³He,
and the spin orientation selects the channel. This file records what the ILL
has, what the hardware looks like, what is known about running it in a beam,
and what the arithmetic says. The numbers are in `ill_rates.polarised()` /
`polarised_table()`.

---

## 1. The physics the idea rests on — and how solid it is

**(n,p) is singlet-only.** Passell & Schermer (Phys. Rev. 150, 146 (1966))
sent polarised thermal neutrons through ³He polarised by adsorption on
zeolite. They found the absorption "essentially all associated with the
I − ½ = 0 channel": σ_singlet-share/σ₀ = **1.010 ± 0.032**. Every modern ³He
neutron spin filter is built on this. Neutron polarimetry with ³He (P_n =
tanh(P₃σ₀t λ/λ₀)) is quoted to < 0.1% absolute (NIST interferometry, Huber et
al. 2014), which would not close if the triplet absorption were appreciable.
The working form, Sharma et al. PRL 101 083002 Eq. 1:

    σ_a = σ₀ (λ/λ₀) (1 ∓ P₃),   σ₀ = 5333 ± 7 b at λ₀ = 1.8 Å
    − : neutron spin parallel to ³He,  + : antiparallel  (10 666 b at P₃ = 1)

Our model carries a residual triplet absorption ε_t = σ_t/σ₀ as a parameter.
At 1–3% it trims the gains below by 5–15%; nothing qualitative changes.

**(n,γ) is triplet-only.** This is a selection rule, not a measurement. The
¹S₀ entrance is 0⁺, the ⁴He ground state is 0⁺, and 0⁺→0⁺ cannot emit a real
photon. So the whole 55 μb is the ³S₁ (1⁺) M1, and σ_γ(triplet) = (4/3)·55 μb.
The E0 pairs (0⁺→0⁺) are the singlet's only electromagnetic outlet
(nTof_x17 `sept26_prelim_analysis/ipc_channels.py`, and `MX17_Full_Geant/docs/e0_branch/`).

**Nobody seems to have measured ³He(n,γ) or ³He(n,e⁺e⁻) with polarised
beam and target.** Searches found the spin filters themselves, the
NPDGamma / n-³He parity programmes (spin filter as beam polariser,
unpolarised or ⁴He targets) and the NIST spin-dependent scattering length.
I found no spin-dependent radiative-capture or pair measurement. That makes
the measurement novel, but it also means no existing data set calibrates the
idea. **(Worth a proper literature check with the ILL NPP group.)**

## 2. The arithmetic

For a neutron with spin along the ³He polarisation axis, the singlet fraction
of its n–³He spin states is f_s = (1 − P)/4. Against the axis it is (1 + P)/4.
Unpolarised it is 1/4. In an **opaque** cell every neutron is absorbed, so the
radiative-to-(n,p) competition decides the yield **per absorbed neutron**:

    M1 gain G(f_s) = (1 − f_s) / (3 f_s)          (ε_t = 0; =1 when unpolarised)
    E0 pairs per absorbed neutron: unchanged (both they and (n,p) are singlet)

With PF1B's P_n = 0.997 (from `polarised_table()`, ε_t = 0):

| P(³He) | M1 gain, spins parallel | M1 gain, antiparallel | **flip contrast** | **unpolarised beam on polarised cell** | absorption length, parallel |
|---|---|---|---|---|---|
| 0.60 | 3.0× | 0.50× | 6 | **1.75×** | 2.5× longer |
| 0.70 | 4.1× | 0.45× | 9 | **2.3×** | 3.3× |
| 0.75 | 5.0× | 0.43× | 11.5 | **2.7×** | 4× |
| 0.80 | 6.3× | 0.41× | 15 | **3.4×** | 5× |
| 0.85 | 8.6× | 0.39× | 21 | **4.5×** | 6.7× |

Four things to read off it:

1. **The flip contrast measures E0 against M1 directly.** Same cell, same
   detector, same background; only the neutron spin changes. The M1 share
   moves 9–21×, and the E0 yield per absorption does not move at all. That is
   the E0 fraction nTof_x17 `IPC_MISSING.md` brackets at 6–52% and cannot close by
   calculation.
2. **An unpolarised beam on a polarised cell already gives 2–4.5× more M1
   pairs** (and X17, if it couples like M1) per absorbed neutron. **No neutron
   polariser is needed for that.** The antiparallel half of the beam is eaten
   at the front of the cell by (n,p). The parallel half penetrates and
   captures mostly through the triplet. This is the only way found to beat the
   self-shielding ceiling at thermal energies, i.e. the 1.03×10⁻⁸ radiative
   captures per absorbed neutron that limits every unpolarised design.
3. **The asymmetry needs the polarised beam.** With an unpolarised beam,
   flipping the ³He changes nothing, by symmetry. With a polarised beam, flip
   the neutron (PF1B spin flipper, > 99.5%) or the ³He (AFP NMR, > 99% per
   flip in a magic box), or both, to cancel systematics.
4. **The cell must be longer.** The parallel neutrons see σ₀(1 − P). At
   P = 0.75 their absorption length is 4× the unpolarised one: at 4.25 Å,
   ~13 cm at 1 bar or ~4 cm at 3 bar. To absorb ≥ 95% of them, use ~3 bar ×
   15 cm or 1 bar × 40 cm. Anything that gets through hits the end window,
   and those are triplet-heavy neutrons, so the end cap's capture γ is a
   background that grows with P.

**Rate.** PF1B's polarised beam is 3×10⁹ capture flux over 6 × 8 cm²
(~1.3×10⁹ n/cm²/s particle flux, ~6×10¹⁰ n/s on the whole cross-section).
That is **6× more than the 10¹⁰ n/s design point** in `README.md`, so
polarisation costs no statistics at the design point.

**X17 by spin-parity.** V, A and P bosons can only leave the 1⁺ and S only the
0⁺ (see `FACILITY.md`). Under flip, a V/A/P excess therefore follows the M1
(×9–21), and an S excess follows the E0 (flat). There is a further handle,
**not yet computed**. The 1⁺ state is aligned along the spin axis, so the
boson's emission direction relative to that axis depends on its type:
roughly isotropic for A (L = 0), sin²θ-like for P (L = 1), transverse-plus-
longitudinal for V. With our detector the boson direction is only the pair's
summed momentum, and without lepton energies that is poorly measured. Treat
it as an idea for theory input, not a planned observable.

## 3. What the ILL has: polarised ³He

**Tyrex / Tyrex-2, the central MEOP filling station** (ILL ³He group):

| | |
|---|---|
| Method | Metastability-exchange optical pumping of **pure ³He at ~1 mbar** in ten optical-pumping cells, then mechanical compression |
| Laser | 1083 nm fibre laser (2³S₁ → 2³P), 100 W (10 × 10 W), 2 GHz bandwidth |
| Polarisation | **85% static, 80% on a neutron beam** (Tyrex-2); the original Tyrex gave ~70–75% |
| Production | **2.5 bar·L per hour** (Tyrex-2); the original Tyrex ≥ 1 bar·L/h; > 1000 bar·L delivered since 2002 |
| Compressor | Hydraulic titanium-alloy piston, Ø15 cm × 60 cm stroke, compression ratio > 15 000, positioned to 3 μm |
| Final pressure | **up to 4 bar** |
| Holding field at the station | nine 2 m coils, 10 G, gradient < 3×10⁻⁴ cm⁻¹ over 1.2 m × 2.5 m |
| Service model | The station fills cells **daily** and supplies them to instruments. A cell lasts 1–2 days on an instrument, then is swapped. |

**The cells: what they look like and how they are contained.** Three types
are in use at the ILL:

- **GE180** (boron-free aluminosilicate glass), reblown, valve-sealed
- **GE224 quartz**
- **Pyrex with single-crystal Si windows**: Pyrex contains boron, so the
  beam faces are Si wafers

The inside is coated with **Cs or Rb**; caesiated glass is weakly relaxing.
Standard size is **Ø5 cm × 10 cm**, and large cells are Ø14 × 12 cm. Typical
fill is 1–3 bar, sized by the "opacity" pressure × length × wavelength
≈ 3 bar·cm·nm.

| | |
|---|---|
| Wall relaxation T₁ | **100–300 h** routinely (≈ 200 h for Ø5 × 10 cm); **> 1000 h** for the large Ø14 × 12 cm cell (a record for a valved cell) |
| Gradient relaxation | 1/T₁ ≈ D·(\|∇B⊥\|/B)², D ≈ 1.9 cm²/s/bar. Typical cavity gradients of 2–6×10⁻⁴ cm⁻¹ give 3700 h down to a few hundred h (RMP review) |
| Field dependence | T₁ falls exponentially with field, constant (30 mT)⁻¹, mostly from magnetisation in the glass valve's plastic and O-ring |

**The containment on the beam line is a magnetostatic cavity, the "Magic
Box"** (Petoukhov et al., NIM A 560 (2006) 480). It is a μ-metal box whose
top and bottom plates are magnetised by coils or permanent magnets, acting as
a magnetic parallel-plate capacitor. That gives a uniform field (1 mT in the
original) transverse to the beam, shielded from moderate stray fields. The
original was 80 cm long. A permanent-magnet version (Hutanu et al. 2008) was
40 cm at 1.7 mT, and an end-compensated version (McIver et al. 2009) was
28.4 cm, up to 3.6 mT (Chen et al. 2014). T₁ ≈ 800 h reported in a magic box,
with **AFP polarisation reversal at > 99% efficiency** per flip. Cells travel
between Tyrex and the instrument in battery-powered shielded solenoids.

**For us this is the awkward part.** A magic box is a closed **μ-metal shell
around the cell**, and the pairs have to get out through it. 1–2 mm of Ni-Fe
is ~0.07–0.14 X₀ (multiple scattering plus conversion), and Fe/Ni capture
scattered neutrons with hard γ (Fe 2.6 b, Ni 4.5 b). Three alternatives:

1. Large open coils around the whole apparatus. Tyrex itself holds 3×10⁻⁴
   cm⁻¹ over 1.2 m × 2.5 m with nine 2 m coils at 10 G. That leaves no
   material in the pair path, but the coils, the four arms and the beam line
   all have to fit together.
2. A magic box with apertures facing the arms. Gradients near the openings
   would need a field calculation.
3. Plates outside the arm acceptance only (top and bottom), relying on the
   parallel-plate geometry.

A ~1–4 mT field does nothing to the leptons (a 10 MeV track has a radius of
~10–30 m). **Watch for magnetised parts in our own apparatus**: steel
fasteners, connector shells, the SS mesh. Each adds gradient and costs T₁.

**Glass is a worse window than Be.** Metal walls relax polarised ³He, so a
polarised cell is glass or Si, not the Be/C windows that make configuration B
clean (`ill_rates.WINDOWS`, ±20% on compositions):

| entrance window | wall captures / absorbed n (PF1B) | relative to the as-built capsule |
|---|---|---|
| 1 mm GE180 | 1.6×10⁻³ | 1/12 |
| 1 mm fused quartz | 9×10⁻⁴ | 1/21 |
| 0.5 mm Si wafer (Pyrex cell) | 1.0×10⁻³ | 1/19 |
| 0.5 mm Be (unpolarised cell, for comparison) | 1.1×10⁻⁴ | 1/170 |

So the polarised cell gives back ~10× of the wall reduction that Be bought.
It is still 12–21× better than the n_TOF capsule, and the 2–4.5× M1 gain
offsets part of it. GE180's Ba lines (up to ~9 MeV) are harder than Al's. A
Pyrex body with Si windows keeps the boron away from the beam; any boron hit
by scattered neutrons gives only the 478 keV line, which is below pair
threshold and harmless.

## 4. What the ILL has: polarised neutrons

**PF1B** (H113, cold, mean λ ≈ 4.0–4.5 Å):

| | |
|---|---|
| Polarisers | Supermirror bender (P = 98%), or **crossed super-mirror polarisers, P = 99.7%** (Petukhov/Soldner et al.). The newer solid-state supermirror polariser (arXiv:2208.14305) reaches **P_n ≈ 0.997 over the full divergence, wavelength-independent over 3–20 Å**. It has > 30% transmission of the good spin state and has been in user operation **since 2020**. |
| Polarised flux | **3×10⁹ n/cm²/s capture flux** (vs 2×10¹⁰ unpolarised) |
| Polarised cross-section | **3 × 4.5 cm² or 6 × 8 cm²** |
| Spin flippers | current-sheet and adiabatic RF, **> 99.5%** |
| Whole polarised beam | ≈ 1.3×10⁹ n/cm²/s particle flux × 48 cm² ≈ **6×10¹⁰ n/s**, before any derating for the 46–56 MW cycles |

A **³He spin filter can also polarise the beam** (that is what it is for).
That is useful if the supermirror's > 30% transmission or the 6 × 8 cm² size
ever binds. It costs a second cell and its own decay curve.

## 5. Running polarised ³He *in* an intense beam — the real risk

All the in-beam data are for spin filters, which absorb a fraction of the
beam. **Our cell absorbs all of it**, so the energy deposited per incident
neutron (764 keV of p + t in the gas) is the same, but none of it leaves.

**SEOP cells (alkali-pumped, in-situ).**
- Sharma et al., PRL 101, 083002 (2008), and Babcock et al., PRA 80,
  033414 (2009, measured **at PF1B**). The (n,p) ionisation relaxes the
  **alkali** vapour. The extra alkali relaxation scales as **√(capture flux)**,
  consistent with a recombination-limited ion density. At 4.7×10⁹ n/cm²/s the
  alkali relaxation rose **100 → 1000 s⁻¹**, and at full PF1B flux a K-Rb hybrid
  cell's alkali polarisation fell **~20%**.
- There are two time scales: a fast component (< 1 s) and a slow one
  (hundreds of s) that grows with N₂ density.
- A **white film** builds up on the walls over long exposure, probably RbH or
  azides from the H/T the reaction itself makes. It is less severe in K-Rb
  hybrid cells.
- At NPDGamma's (1–3)×10⁸ the ³He polarisation dropped only 2–6% (relative).
  The authors judge 10⁶–10⁷ n/cm²/s "largely unaffected".
- **Fix demonstrated: the double cell.** The pumping chamber sits out of
  the beam and the target chamber in it, joined by diffusion. It was "found to
  be unaffected by the neutron beam". This is the standard design for polarised
  ³He electron-scattering targets.

**MEOP cells (pure ³He, what Tyrex fills).**
- Ionisation relaxes the ³He *nuclei* directly, through hyperfine coupling in
  ³He⁺ and spin-rotation coupling in ³He₂⁺ (Bonin et al. 1988). The RMP review
  (Gentile, Nacher, Saam, Walker, RMP 89, 045004 (2017), §IV.E) states:
  *"Due to the much greater sensitivity of pure ³He cells to ionization,
  large effects on ³He relaxation have been observed in MEOP cells due to
  neutron beams"*. The source cited is Petukhov 2016, which is
  **unpublished** as far as I can find.
- **The known mitigation is N₂ at [N₂]/[³He] ≈ 10⁻⁴**, added after
  compression (Meyerhoff et al. 1994, for electron-scattering targets).
  Nitrogen destroys the molecular ions. SEOP cells already contain N₂, which
  is why they are less sensitive.

**Where our design point sits.** 10¹⁰ n/s over a 20 cm² face is 5×10⁸
n/cm²/s, between NPDGamma (benign for SEOP) and the full-flux PF1B tests (a
20% alkali loss). The rate can be traded against the beam spot: the same
absorbed rate over a larger face means a lower flux density, and the alkali
effect goes as √φ. **Ask A. Petoukhov / E. Babcock** (both on the PF1B
papers) for the unpublished MEOP numbers and for what N₂ buys. Their answer
decides between offline MEOP cells swapped daily and an in-situ SEOP double
cell.

## 6. Two ways to build it

| | **A. Tyrex cells, swapped** | **B. In-situ SEOP double cell** |
|---|---|---|
| ³He polarisation | 80% at fill, decaying with T₁ ~ 100–300 h; ~70% average over 1–2 days | 70–80% steady, continuous |
| Beam effects | Pure ³He: direct ionisation relaxation ("large", unpublished); N₂ trace helps | Target chamber has no alkali → bypassed |
| Logistics | ~25–50 swaps per 50-day cycle, each a break in running and a re-alignment; the infrastructure is routine at the ILL | Lasers (~100 W at 795 nm), oven, interlocks on the beam line; a bespoke build, but demonstrated |
| Geometry | Standard Ø5 × 10 cm cells are close to what we need; a 3 bar × 15 cm custom cell is plausible (Tyrex compresses to 4 bar) | The target chamber can be shaped for us; transfer tube to an out-of-beam pumping chamber |
| What it costs us | Changing cells every day or two; the T₁ decay is a systematic, monitored by NMR FID | A project, at the scale of the PF1B in-situ polariser work (a collaboration with the ILL ³He group) |

Either way: **AFP flips of the ³He every few minutes plus neutron spin flips**
give a four-state sequence that cancels detector asymmetries, as in
NPDGamma-style experiments.

## 7. Open questions, for the ILL ³He group and NPP

1. The unpublished MEOP in-beam relaxation numbers (Petukhov 2016): T₁ against
   absorbed power density, and with N₂ added.
2. Can Tyrex fill a **3 bar, ~15 cm, Ø3–5 cm** quartz or Si-window cell? Is
   there a precedent for a target cell (all neutrons absorbed) rather than a
   filter?
3. Field options that leave the four arms' acceptance free of μ-metal, and the
   gradient budget given our apparatus.
4. Has anyone measured spin-dependent ³He(n,γ) (any experiment, any facility)?
   And the best current limit on triplet (n,p), ε_t?
5. The polarised-beam spectrum and divergence after the polariser (for the
   Geant gun) and its usable cross-section with our collimation.

And for theory (Viviani/Marcucci/Schiavilla, same request as `README.md`):
the thermal ³He(n,e⁺e⁻) prediction **separately for the ¹S₀ and ³S₁
entrances**, which is what this measurement would compare against, and the
angular distribution of a V/A/P boson from the aligned 1⁺ state.

## 8. Simulation implications (add to `GEANT_PLAN.md` when run)

- Geant4 HP does not track the n–³He spin dependence, so do not try to
  simulate polarisation in Geant4. Generate the M1 and E0 pairs separately
  (`ipc_born`) and weight them with `ill_rates.polarised()`.
- The absorption *depth* does depend on spin (the parallel neutrons go
  ~4× deeper at P = 0.75). Build two vertex libraries by running the cell with
  ³He density scaled by (1 ∓ P), and combine them with the spin weights.
- Add the cell's glass (GE180/quartz/Si) as `--window` options, and the
  magic box or coil option as a passive volume.

---

## Sources

- Passell & Schermer, Phys. Rev. 150, 146 (1966): <https://journals.aps.org/pr/abstract/10.1103/PhysRev.150.146>
- Polarized-n on polarized-³He total cross sections (context): <https://arxiv.org/html/nucl-ex/9607011>
- Sharma et al., PRL 101, 083002 (2008), "Neutron beam effects on spin-exchange-polarized ³He": <https://arxiv.org/pdf/0802.3169>
- Babcock et al., PRA 80, 033414 (2009), "Effects of high-flux neutron beams on ³He cells polarized in situ" (PF1B): <https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=902968>
- Gentile, Nacher, Saam, Walker, "Optically polarized ³He", RMP 89, 045004 (2017): <https://arxiv.org/pdf/1612.04178>
- Gentile, PoS(PSTP 2013)022, "Polarized ³He spin filters for neutron science": <https://pos.sissa.it/182/022/pdf>
- NIST JRes 110 (2005), "Polarized ³He spin filters for slow neutron physics": <https://nvlpubs.nist.gov/nistpubs/jres/110/3/j110-3gen.pdf>
- ILL ³He spin filters: <https://www.ill.eu/neutrons-for-society/neutron-technology/optics/3he-spin-filters-1>
- Tyrex-2 technical details: <https://www2017.ill.eu/for-all-users/instruments/instruments-list/tyrex-2/technical-details>
- Tyrex history: <https://www.ill.eu/users/instruments/instruments-list/tyrex-2/history>
- Magic box (Petoukhov et al.): <https://www.researchgate.net/publication/222252984_Compact_magnetostatic_cavity_for_polarised_3He_neutron_spin_filter_cells>
- Recent advances in ³He spin filters at the ILL: <https://www.researchgate.net/publication/230734633_Recent_advances_in_polarised_3He_spin_filters_at_the_ILL>
- PF1B characteristics: <https://www2017.ill.eu/for-all-users/instruments/instruments-list/pf1b/characteristics>
- PF1B solid-state supermirror polariser: <https://arxiv.org/pdf/2208.14305>, <https://arxiv.org/pdf/1906.04690>
- ³He polarimetry by neutron transmission (double cell): <https://arxiv.org/html/2209.12484>
