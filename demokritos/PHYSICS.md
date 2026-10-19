# The physics at Demokritos: ³H(p,e⁺e⁻)⁴He, the ATOMKI ⁴He anomaly

Compiled 2026-10-19. Numbers come from `demokritos_rates.py` (→ `out/`) unless a source is given.

---

## 1. Why this reaction, here

- **It is the other ATOMKI claim, and the same nucleus as n_TOF and the ILL.**
  - ATOMKI saw an e⁺e⁻ excess at ~115° in ³H(p,e⁺e⁻)⁴He at E_p = 510, 610 and 900 keV. Their papers are
    arXiv:1910.10459 and PRC 104, 044003 (2021).
  - They quote m_X = 16.94 ± 0.12 ± 0.21 MeV and **B_x = Γ_X/Γ_γ = 5.1(13)×10⁻⁶**, at 7.3σ, 6.6σ and 8.9σ.
  - No one has checked it independently. MEG II, Hanoi and LNL all work on ⁸Be.
  - n_TOF reaches the same ⁴He\* from n + ³He, and the ILL at thermal energy. A p + t run at Demokritos would test
    the claim with the same apparatus, through the conjugate entrance channel.
- **Demokritos already runs p + t.** It makes 2–5 MeV neutrons with ³H(p,n) on its own Ti-T targets (2.1 mg/cm² Ti-T
  on 1 mm Cu, 373 GBq). Tritium handling, licences and shielding are in place (`FACILITY.md` §3).
- **No neutrons.** Below **E_p = 1.019 MeV** the ³H(p,n)³He channel is closed. ATOMKI stayed below it for the same
  reason. The backings (Cu, Mo, Ti) have no (p,n) channel open below ~2 MeV either.
- **One γ line.** ⁴He has no bound excited state, so every capture γ goes to the ground state. There is no
  γ₁ (15 MeV) background as in ⁸Be: the E_sum window sees one transition.
- **Ruled out: the neutron beams** (10⁵–10⁶ n/cm²/s, ≲ 0.5 X17/day into 4π; `out/neutron_option.csv`).
- **Also possible, not estimated in detail:**
  - ⁷Li(p,e⁺e⁻)⁸Be at 1.03–1.1 MeV. This is exactly the LNL case, so at 1 µA the LNL numbers apply (`../lnl`).
  - ¹¹B(p,e⁺e⁻)¹²C at 1.5–2.5 MeV, the third ATOMKI anomaly (17.23 MeV 1⁻, excess at 155–160°). It is easy for the
    tandem.

## 2. The reaction

| | |
|---|---|
| Q(³H(p,γ)⁴He) | **19.814 MeV** (AME masses) |
| E\* | Q + (3/4)·E_p: 20.20 / 20.27 / 20.49 MeV at 510 / 610 / 900 keV; 20.56 MeV at 1000 keV, just below the (p,n) threshold and **the same E\* as thermal n + ³He (20.58)** |
| ⁴He\* recoil | β = 0.011 at 900 keV. The lab boost is negligible: the X17 opening angle is set by E\* alone. |
| States | 0⁺ at **20.21 MeV** (Γ = 0.50 MeV, T = 0), decaying to the ground state **only by E0 pairs**. 0⁻ at **21.01 MeV** (Γ = 0.84 MeV), 0⁻ → 0⁺ has no one-photon decay at all: ATOMKI attributes the X17 to it. Both are reached through their wide tails. |
| γ | **direct E1 capture** (p-wave), smooth in E_p. |
| σ(p,γ) | Hahn *et al.* (PRC 51, 1624, 1995) S-factor fit: S(E) = 1.30×10⁻⁶ MeV b (1 + 25 E + 38.8 E²), fitted to 0.1–0.75 MeV (`refs/Poon1999…`). It gives **24 µb at 900 keV** and 11 µb at 510 keV. ATOMKI quote "about 2 µb/sr at 900 keV", i.e. 17 µb for an E1 sin² pattern at 90° or 25 µb isotropic. So the model is good to ~30 %. Above 0.75 MeV it is extrapolated. |
| E1 IPC | Born α_E1(20.5 MeV) = **4.6×10⁻³** pairs per γ (nTof_x17 `ipc_born`). Viviani *et al.*'s ab initio n + ³He σ_pair/σ_γ is ~2.1×10⁻³ at 0.2–1 MeV, so the true p + t IPC could be ~2× lower. That would be better for us. |
| E0 pairs | a single-level Breit–Wigner for the 0⁺ with Γ_ee = 4.7×10⁻⁶ eV, from M(E0) = 1.53 fm². This gives σ_ee ≈ 2×10⁻⁵ µb, **~4×10⁻⁴ of the E1 IPC**. Negligible: unlike thermal n + ³He, where σ_np = 5333 b feeds the 0⁺, p + t at 0.4 MeV feeds it with only ~2 b. It is an order-of-magnitude stand-in, and its size is what matters here. |

## 3. Kinematics

| E_p (keV) | E\* (MeV) | θ_min, m = 16.7 / 16.94 / 17.2 MeV |
|---|---|---|
| 250 (PAPAP) | 20.00 | 113.4 / 115.9 / 118.8° |
| 510 | 20.20 | 111.7 / 114.2 / 116.9° |
| 610 | 20.27 | 111.1 / 113.5 / 116.2° |
| 900 | 20.49 | 109.3 / 111.7 / 114.3° |
| 1000 | 20.56 | 108.8 / 111.1 / 113.7° |

The X17 edge is at **~110–115°**, against ~135–140° in ⁸Be. In the four-arm pinwheel this is the region **between
adjacent (90°) and opposite (180°) arms**. Half the accepted X17 pairs use adjacent arms, half opposite
(`out/arm_pairs.csv`). The IPC E1 continuum is flatter in angle than the ⁸Be M1, so a wider window (105–160°) holds
more of it. **S/B in the window is ~1.1 %**, against ~7 % at LNL.

## 4. What ATOMKI did

| | 2019 (arXiv:1910.10459) | 2021 (PRC 104, 044003) |
|---|---|---|
| machine | 5 MV Van de Graaff, Debrecen | 2 MV Tandetron, ATOMKI |
| E_p | 900 keV | 510, 610, 900 keV |
| beam | 1.0 µA typical | 1.0 µA, ~100 h per energy |
| target | ³H in 3 mg/cm² Ti on 0.4 mm Mo, LN₂-cooled | ³H in **4.2 mg/cm² Ti on 0.4 mm Mo, Ø 50 mm**, LN₂-cooled; stops the beam |
| quoted T density | 2.66×10²⁰ /cm² | ~2.7×10²⁰ /cm² |
| spectrometer | six ΔE–E telescopes: DSSD 50 × 50 mm plus 82 × 86 × 80 mm plastic, ⊥ beam at 60° steps, CFRP 1 mm chamber | the same |
| cuts | E_sum 19.5–22 MeV, −0.5 ≤ y ≤ 0.5; 120° − 60° telescope-pair subtraction | E_sum gate, \|y\| ≤ 0.3; target shifted 20 mm upstream, max angle ~140° |
| background | external pairs from γ in the Mo backing **dominate** below ~90° | EPC fixed on 45–70°; IPC from Viviani's event files |
| result | m = 16.84 MeV, Γ_X = 3.9×10⁻⁵ eV | B_x = 6.2 / 4.1 / 6.5 ×10⁻⁶; IPCC = 2.5 / 1.0 / 1.1 ×10⁻⁴ |

Notes:
- The quoted 2.7×10²⁰ T/cm² is impossible in 4.2 mg/cm² of Ti: that holds 5.3×10¹⁹ Ti/cm², so it would need
  T/Ti ≈ 5, while the maximum is ~2. This model uses T/Ti = 1.5, which gives 7.9×10¹⁹ T/cm².
- **The puzzle in ATOMKI's own numbers.** Their fitted IPC coefficients (1–2.5×10⁻⁴) are **20–45× below the Born E1
  value** (4.6×10⁻³). In their Fig. 4 at 900 keV, the X17 excess is ~10× the remaining IPC at 110–120°. With
  B_x = 5.1×10⁻⁶ per γ and the QED IPC, the excess should be **~1 %** of the IPC in a 10° bin.
  - Either their IPCC is not the IPC-per-γ ratio, or the IPC in their gate is suppressed far beyond what the
    multipolarity allows. Note that the X17 count itself is consistent with B_x per γ: ~10⁴ X17 produced in 100 h,
    ~300 seen at a few % acceptance.
  - MX17 sees the IPC from 40° to 180° with a known acceptance, so it **measures the absolute IPC/γ directly**. That
    test of ATOMKI's background model needs no X17 at all.
  - **This study's baseline is the pessimistic one**: B_x per γ, with the Born IPC. `ESTIMATES.md` §3 also gives the
    reach if ATOMKI's IPCC is right.

## 5. What a new measurement must get right

1. **The backing.**
   - A Ti-T layer must sit on something. ATOMKI used 0.4 mm Mo; Demokritos' targets are on 1 mm Cu (7 % X₀).
   - Every lepton going downstream crosses it, at grazing incidence near 90°, which is where the arms are. A thick
     backing either blocks the downstream hemisphere (×4 in acceptance, ×3.6 in days) or scatters it.
   - **A thin backing (Cu 50–100 µm) costs only ×1.2–1.3 in days** and carries ~1–3 µA with rim cooling
     (`out/heat.csv`).
   - It is the design driver, just as the chamber wall is at LNL. See `ESTIMATES.md` §2.
2. **EPC from the backing** dominated ATOMKI's spectra at small angles. In MX17 a converted pair goes into one arm
   and is rejected by the two-arm requirement, unless it scatters. Geant4 must check this (`GEANT_PREP.md` D3).
3. **The IPC shape.**
   - S/B is ~1 % in the window in the baseline normalisation. The E1 IPC shape, the γ\* anisotropy about the beam
     (E1 direct capture is sin²θ), and the acceptance must be known well, as at LNL (§12–17 there).
   - The 3D fit θ × |y| × E_sum carries over. The 1000 keV point (E\* = 20.56) and the IPC side bands are in-run
     controls.
4. **Cosmics.** As at LNL, with MM 15° + TOF + an E_sum window (now 18–21 MeV) they are ~1/day. Negligible against
   ~10⁴–10⁵ IPC/day in the window.
5. **Target lifetime and tritium.**
   - Ti-T loses tritium when hot (keep it ≲ 150–200 °C **(ask)**) and under beam (sputtering, isotope exchange with
     the beam's protons).
   - At 1 µA over weeks that is ~10¹⁷ protons/cm². ATOMKI ran ~300 h on one target.
   - Monitor the γ yield on a NaI or LaBr₃ at 20 MeV; it is the normalisation anyway.
   - Tritium contamination of the chamber: the arms are outside a sealed CFRP chamber, so only the chamber is exposed.
6. **Beam energy.**
   - 900 keV is ATOMKI's best point and the highest yield below the (p,n) threshold.
   - **1000 keV** gives E\* = 20.56 MeV ≈ thermal n + ³He: the same E\* as the ILL/n_TOF thermal point, with a
     different entrance channel and multipolarity. **(ask)** whether the tandem holds 1000 keV within ~5 keV of the
     threshold. A 10 keV slip opens (p,n), so 980 keV is safer.
   - 510 and 610 keV (ATOMKI's other points) may be below the tandem's range.

## 6. Contaminant lines

| reaction | Eγ | matters? |
|---|---|---|
| ³H(p,γ)⁴He | 20.0–20.5 | the signal γ and the EPC source |
| D(p,γ)³He (D in the Ti-T) | 5.5–6.1 | no: below the E_sum window |
| ¹²C/¹³C(p,γ) (carbon build-up) | 2.4 / 8.1 | no |
| ¹⁹F(p,αγ) (if F present) | 6.1–7.1 | no |
| **¹¹B(p,γ)¹²C** | 16.1–17.2 (163 and 675 keV resonances) | **yes: below the window but close; keep boron out** |
| ⁶³,⁶⁵Cu(p,γ) | ~7–8 | no |
| ⁴⁸Ti(p,γ)⁴⁹V | ~6.8 | no |
| T β⁻ (18.6 keV endpoint) and Ti X-rays | < 20 keV | no: stopped in the target and chamber |
