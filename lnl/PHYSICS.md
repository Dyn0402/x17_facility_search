# ⁷Li(p,e⁺e⁻)⁸Be: the reaction, what has been seen, and what it means for us

The "production mechanism" in one page, then the numbers. Model numbers come
from `lnl_rates.py` (`out/*.csv`). Literature numbers carry their source (list at
the bottom; text extractions in `refs/`).

---

## 1. What actually happens

1. **A proton of ~0.4–1.2 MeV hits a ⁷Li nucleus** in a thin lithium-compound film
   (see `TARGETS.md`). Most protons just slow down in the film and the backing. About
   one in 10⁹–10¹⁰ is captured.
2. **Capture makes ⁸Be at E\* = Q + E_cm**, with Q = 17.2551 MeV and E_cm = (7/8)·E_p.
   This is the same compound-nucleus bookkeeping as n + ³He → ⁴He\*, but the
   proton has to tunnel through the Coulomb barrier. That is why the cross section
   is µb–mb, not barns.
3. **Two 1⁺ resonances make capture selective.** Tilley 2004 (Tables 8.10, 8.12):

   | E_p (lab) | Γ_lab | ⁸Be\* | J^π; T | Γ_γ0 → g.s. | Γ_γ1 → 3.0 MeV | σ_peak(γ₀+γ₁) |
   |---|---|---|---|---|---|---|
   | **441.4 keV** | 12.2 keV | **17.640** | 1⁺; 1 (isovector) | 15.0 eV | 6.7 eV | **5.9 mb** |
   | **1030 keV** | 168 keV | **18.150** | 1⁺; 0 (isoscalar) | 1.9 eV | 4.3 eV | ~0.06 mb (resonant) |

   The two states are isospin-mixed (~95/5 %). Both decay by **M1**. The ATOMKI
   anomaly is claimed in the isoscalar 18.15 MeV one.
4. **Direct (non-resonant) capture runs underneath everything.** It is mostly **E1**,
   σ(γ₀) ≈ 15–20 µb, nearly flat from 0.5 to 1.5 MeV. Our split of the Zahnow 1995
   data (`out/figures/excitation.png`): **at the 1030 keV peak only ~half of the γ₀
   capture is the resonance; the other half is direct E1 capture.** Off resonance
   (0.65–0.8 MeV, 1.2 MeV) it is 85–90 % direct. This matters, because E1 IPC is much
   flatter in opening angle than M1, so it fills the 140° region.
5. **The excited ⁸Be then decays** (all branches are relative to γ₀):
   - **γ₀**: a real γ to the ground state, 17.6 / 18.15 MeV. This is the normalisation.
   - **γ₁**: to the broad (Γ ≈ 1.5 MeV) 2⁺ state at 3.0 MeV, a 14.6 / 15.1 MeV γ. It is
     **~2× γ₀ at 1 MeV** (Zahnow), 0.45× at 441 keV.
   - **IPC**: the same transitions with a virtual photon → e⁺e⁻, at **α ≈ 3.5×10⁻³ (M1)
     to 4.4×10⁻³ (E1)** per γ. Born values from nTof_x17 `ipc_born` at W = 18.15 MeV;
     ATOMKI used the Rose 3.9×10⁻³.
   - **X17** (if it exists): ⁸Be\* → ⁸Be(gs) + X, X → e⁺e⁻. ATOMKI's best fit is
     **R = Γ_X/Γ_γ = 5.8×10⁻⁶** at 18.15 MeV, i.e. X17/IPC ≈ 1.5×10⁻³.
   - Also ⁸Be\* → p + ⁷Li (elastic, dominant) and p′ + ⁷Li\*(478 keV): Γ_p′ ≈ 6 keV in
     18.15. These emit no pairs. The 478 keV γ is the classic target-content monitor.
   - The ⁸Be ground state falls apart into two α (~46 keV each, no γ). Nothing to see.
6. **No neutrons.** ⁷Li(p,n)⁷Be opens at 1.881 MeV, ¹⁹F(p,n) at 4.2 MeV, so a
   ≤ 1.3 MeV run is neutron-free. That is the opposite of every other facility in this
   repo, and it is why the radiation-protection current limits in the CN paper (all
   from neutrons at 5.5 MeV) do not apply.

## 2. Kinematics: why 140°, and why it barely moves

The ⁸Be\* moves at β ≈ 0.006, which is negligible (MEG II also neglects it). The X17
is emitted from a nucleus at rest with E_X ≈ E\*, so its decay pairs have an
opening-angle **edge at θ_min = 2·asin(m_X/E_X)**, with most pairs piling up just
above it (`out/kinematics.csv`, `out/figures/theta_min.png`):

| E_p [keV] | E\* [MeV] | Σ KE(e⁺e⁻) [MeV] | θ_min, m = 16.7 | 16.85 | 17.0 |
|---|---|---|---|---|---|
| 441 | 17.64 | 16.62 | 142.4° | 145.6° | 149.0° |
| 800 | 17.96 | 16.93 | 137.0° | 139.6° | 142.5° |
| 1030 | 18.16 | 17.13 | 133.8° | 136.3° | 138.9° |
| 1100 | 18.22 | 17.20 | 133.0° | 135.4° | 137.9° |
| 1225 | 18.33 | 17.30 | 131.4° | 133.7° | 136.2° |

Compare n_TOF ³He: E\* = 20.58 MeV, edge at 109.6°. Here the edge sits **~25° higher**,
where the IPC continuum is ~3× lower (M1 falls steeply with angle). The leptons are
similar, ~8.6 MeV each. **The resolution argument is the same as n_TOF, but the
geometry differs:**
- The vertex is a **point**: the beam spot, a few mm, on a µm film.
- There is no 500 bar capsule, so the only material before the arms is a thin
  chamber wall and air.
- The chord estimator is therefore essentially exact (ILL: an ideal vertex was worth
  only ~13 %, but here it comes for free).

## 3. What has been measured

| when, who | beam / target | what they saw |
|---|---|---|
| **2016, ATOMKI** (Krasznahorkay *et al.*, PRL 116, 042501) | 5 MV VdG, **1.0 µA**. 15 µg/cm² LiF and 300 µg/cm² Li₂O on 10 µm Al. E_p = 0.441, 0.80, 1.04, 1.10, 1.20 MeV. 5 plastic ΔE–E telescopes + MWPCs, ⊥ beam. | **6.8σ** excess at ~140° at **1.10 MeV**; m = 16.70 ± 0.35 ± 0.5 MeV, R = 5.8×10⁻⁶. None at 17.64. |
| **2022, ATOMKI** (Sas *et al.*, arXiv:2205.07744) | upgraded (DSSD), **5 µA**, ~50 h per energy. 30 µg/cm² (on-res), 300 µg/cm² (off) LiF/Li₂O on 10 µm Al, now on Al rods for cooling. E_p = 0.45, 0.65, 0.80, 1.10 MeV. | Excess at ~140° at **every off-resonance energy**, i.e. in **direct (E1) capture**, I(X17)/I(E1) ≈ 0.4–0.5. They admit the 2016 1.04/1.10 MeV targets were oxidised **metallic Li** that had diffused into the backing ("actual thickness = 10 µm"), so the beam also hit the 441 keV resonance. Their background model was therefore wrong in 2016. |
| **2024, Hanoi VNU** (Tran The Anh *et al.*) | two-arm spectrometer built with ATOMKI; E_p = **1.225 MeV** | ≥ 4σ at ~135°, m = 16.66 ± 0.47 ± 0.35; none at 17.6 |
| **2023 data, MEG II** (EPJC 85, 763 (2025)) | 1 MV Cockcroft-Walton, 1.08 MeV, **8–11 µA**. 7 µm LiPON on 25 µm Cu. 75 % H⁺ / 25 % H₂⁺ beam, so mostly the 441 resonance. Magnetic spectrometer, 4 weeks. | **No signal.** R(18.1) < 1.2×10⁻⁵, R(17.6) < 1.8×10⁻⁶ (90 % CL). ATOMKI hypothesis p = 6.2 %. |
| **2023–24, LNL** (Góngora-Servín *et al.*, APPB Supp 18, 2-A13) | **AN2000**, 800 nA. LiF 34–935 µg/cm², 441 keV and 1.03 MeV. 4 clovers of plastic ΔE–E, ~790 h. | Analysis ongoing; nothing published by Oct 2026. |
| **2026, MEG II members** (Benmansour *et al.*, arXiv:2609.18383) | Geant4 of ATOMKI's five- and six-arm spectrometers + sea-level muons | **Cosmic two-arm coincidences make a peak near 140°** in the ⁸Be energy window. Normalised to ATOMKI running (1 µA, ~300 h), **cosmics ≳ IPC there**. A "bump" built from IPC + cosmics peaks at 140°. |

Others in preparation: Montreal (near-4π MWPC, 2 µA ⁷LiF, "2 weeks for a clear
signal"), Prague (TPX3 + TPCs), Melbourne (TPC), JEDI at GANIL, and **us at n_TOF**.

**Theory.**
- Zhang & Miller (PLB 773 (2017), PRC 2021): the IPC model with E1 direct capture and
  M1 resonances, used by MEG II.
- Gysbers *et al.* (ab initio NCSMC, arXiv:2308.13751): reproduces σ(p,γ) and the
  resonance angular correlations; between resonances the IPC is "completely E1
  dominated", flat in angle. A vector X17 could appear between and at the 2nd
  resonance; at 17.64 it would be swamped by M1.

## 4. What a new ⁸Be measurement has to get right

From the record above, ranked:

1. **Cosmics.** A beam-independent two-arm coincidence that lands at ~140° and in
   the 16–20 MeV window. Without tracking you cannot tell it from a pair. We have
   tracks:
   - the ILL study's MM segment + collinearity cuts take cosmics from ~9×10⁵ to
     ~10⁴ per 50 days;
   - a point target allows a 3-D vertex cut (estimated ×25 more);
   - CN's pulsed beam (2 ns in 333 ns) is another ×~50.
   - **This is our strongest argument.**
2. **The background shape: M1 vs E1 vs where the protons stop.** The target must be
   thin and stable, so the captures happen where you think. ATOMKI 2016 got this
   wrong (diffused metallic Li). The E1 direct-capture share of the background is
   ~50 % at 1.03–1.10 MeV and must be fitted, not assumed.
3. **Separate the 18 MeV transitions from the 15 MeV (γ₁) ones.**
   - γ₁ is 2× γ₀, and its IPC also reaches large angles.
   - ATOMKI and MEG II cut on E_sum with plastic/BGO resolution.
   - **The n_TOF stack contains only ~40 % of the lepton energy**, so as built it
     cannot do this. In the model it doubles the background (`F_G1_LEAK`).
   - The thick plastics of `../trigger_scint` fix it.
4. **Acceptance known as a function of angle.** Pair acceptance has structure at the
   arm boundaries, so it must be measured with uncorrelated pairs, or calibrated on
   the 441 keV M1 line, which is IPC-only and has a known shape.
5. **Calibration lines for free:**
   - 17.64 MeV M1 at 441 keV (pure IPC reference);
   - ¹⁹F(p,αe⁺e⁻)¹⁶O 6.05 MeV **E0** if LiF is used (LNL uses it as a reference);
   - ¹¹B(p,γ)¹²C 4.44 / 15.1 MeV with a boron target (ATOMKI's calibration).

---

## Sources

| key | reference | file |
|---|---|---|
| Ti04 | D.R. Tilley *et al.*, "Energy levels of light nuclei A = 8, 9, 10", NPA **745**, 155 (2004), ⁸Be §14 and Tables 8.10, 8.12, 8.13 | `refs/Tilley2004_A8.txt` |
| Za95 | D. Zahnow *et al.*, Z. Phys. A **351**, 229 (1995); EXFOR A0639 (S-factors γ₀ and γ₀+γ₁, 98–1500 keV; 10 µg/cm² ⁷LiF on Cu) | `data/exfor_A0639_Zahnow1995.txt` |
| AK16 | A.J. Krasznahorkay *et al.*, PRL **116**, 042501 (2016); arXiv:1504.01527 | `refs/Krasznahorkay2016_PRL_arXiv1504.01527.txt` |
| Gu16 | J. Gulyás *et al.*, NIM A **808**, 21 (2016); arXiv:1504.00489 (the ATOMKI spectrometer) | `refs/Gulyas2016_ATOMKI_spectrometer_arXiv1504.00489.txt` |
| Sa22 | N.J. Sas *et al.*, arXiv:2205.07744 (direct-capture anomaly; target history) | `refs/Sas2022_ATOMKI_directcapture_arXiv2205.07744.txt` |
| Sa25 | N.J. Sas *et al.*, APPB Supp **18**, 2-A14 (2025) (new ATOMKI spectrometer) | `refs/Sas2025_ActaPPB_ATOMKI_newspectrometer.txt` |
| AK24 | A.J. Krasznahorkay *et al.*, arXiv:2409.16300 (world status 2024) | `refs/Krasznahorkay2024_update_arXiv2409.16300.txt` |
| MEG25 | MEG II, "Search for the X17 particle in ⁷Li(p,e⁺e⁻)⁸Be …", EPJC **85**, 763 (2025); arXiv:2411.07994 | `refs/MEGII2024_X17_arXiv2411.07994.txt` |
| MEG26 | H. Benmansour *et al.*, "On the importance of cosmic-ray background in the Atomki anomaly", arXiv:2609.18383 (Sept 2026) | `refs/MEGII2026_cosmics_Atomki_arXiv2609.18383.txt` |
| GS25 | B. Góngora-Servín *et al.*, APPB Supp **18**, 2-A13 (2025) | `refs/GongoraServin2025_ActaPPB_LNLspectrometer.txt` |
| Gy23 | P. Gysbers *et al.*, "Ab initio investigation of the ⁷Li(p,e⁺e⁻)⁸Be process and the X17 boson", arXiv:2308.13751 | `refs/Gysbers2023_abinitio_7Lipee_arXiv2308.13751.txt` |
| Rv26 | "The X17 anomaly: experimental evidence and theoretical interpretations", arXiv:2606.20423 | `refs/Review2026_X17_arXiv2606.20423.txt` |
| Gus20 | C. Gustavino, "Search of the X17 boson @ n_TOF" (2020 proposal slides) | `refs/Gustavino2020_X17_nTOF_proposal_slides.txt` |
