# X17 → e⁺e⁻ at high-energy colliders: STAR, sPHENIX, ALICE (and why not ATLAS/CMS/LHCb/FASER)

*2026-11-12, first pass.* A rough feasibility study: how far the leptons scatter in each
detector's material, how much of the signal can be tracked, and how. It uses analytic estimates
plus a helix-tracking toy MC with real fits (`toy/`, §4). Detector numbers and their sources are
in [`star/`](star/README.md), [`sphenix/`](sphenix/README.md) and [`lhc/`](lhc/README.md).
Every figure has its `.csv` beside it in `out/`.

## 0. Bottom line

1. **The ATOMKI X17 is invisible at a collider.** The ATOMKI signal is a nuclear de-excitation
   with the X17 almost at rest, so each lepton carries 8.4 MeV. No tracker here follows an
   8.4 MeV lepton far enough, except ALICE's ITS standalone tracking in a 0.2 T run (23 % pair
   acceptance) and possibly ALICE 3. A collider can only look for X17 made **in meson decays**
   (π⁰, η → γX17) or by some other boosted mechanism.
2. **Meson radiative decays test only a *vector* X17.** C-parity forbids P → γX for an axial
   vector, and gauge invariance forbids it for a pseudoscalar (§1). The vector option is the one
   SINDRUM π⁺ → e⁺νe⁺e⁻ already excludes for protophobic couplings (Hostert & Pospelov 2023). A
   collider search is therefore a clean, independent test of the vector case and of a generic
   17 MeV dark photon. It is not a test of the axial-vector X17 that best survives.
3. **Scattering is not the problem.** For a boosted pair, both the opening angle and the scattering
   angle scale as 1/E. The mass smear from the material before the first hit is then
   **σ_M ≈ 19 MeV·√(x/X₀)·(1 + 0.038 ln x/X₀)**, whatever the X17 momentum: 0.7 MeV for a 0.2 %
   X₀ beryllium pipe (§3). With the vertex constraint, the toy gets **σ(m_ee) = 0.3–0.5 MeV**
   with silicon (sPHENIX, ALICE) and **1.2 MeV** with STAR's TPC alone. This is the opposite of
   n_TOF, where the X17 is at rest, the opening angle is 110–180° and scattering sets σ(Δθ) ≈ 15°.
4. **The tracking threshold sets the acceptance.** A lepton needs pT ≳ 60 MeV in STAR (0.5 T,
   15 TPC rows) and ≳ 100 MeV for sPHENIX TPC tracks (1.4 T). Silicon only needs **~16–20 MeV in
   sPHENIX** (MVTX + 2 INTT layers) and ~18 MeV in ALICE (ITS standalone; 7 MeV at 0.2 T). As you
   guessed, sPHENIX should do it with silicon alone: it tracks ×6 more X17 from π⁰ and ×3.5 more
   from η than its TPC does.
5. **Conversions fake an X17.** A beam-pipe conversion reconstructed as a primary pair gets
   m_fake ≈ 0.6·B·r_c. That is **16.8 MeV in sPHENIX**, exactly the X17 mass; 6 MeV in STAR;
   2–6 MeV in ALICE. A per-track vertex χ² does not remove them, because the broken-line fit
   absorbs the conversion into two ~3σ kinks. A **pair fit under the conversion hypothesis**
   (common point on the pipe or the first silicon layer, zero opening angle) removes 98–99 % of
   them and keeps 75–90 % of the X17.
6. **Reach (3σ, statistics only).** For 10¹⁰ minimum-bias Au+Au events or 10¹² pp events:
   BR(π⁰ → γX17) ≈ (0.3–1.5)×10⁻⁷, i.e. **10–40× below the NA48/2 ceiling of 1.2×10⁻⁶**;
   BR(η → γX17) ≈ (1.5–6)×10⁻⁷, i.e. **50–500× below the (2.6–9)×10⁻⁵ a protophobic vector X17
   would give**.
7. **The catch is the background shape, not statistics.** S/B at the reach is only 10⁻⁴ (π⁰
   Dalitz under a 1 MeV-wide peak). With a 0.1 % uncertainty on the background shape, the π⁰
   reach falls back to (0.5–2.4)×10⁻⁶, NA48/2 level. The η reach falls to (2–15)×10⁻⁶, which
   still covers the vector scale. The η channel is the case worth making: tag the γ, or require
   m(γe⁺e⁻) = m_η, to cut the π⁰ Dalitz background (§7).
8. **Ranking.** ALICE ITS-standalone (pp, either field) and sPHENIX silicon-only have the best mix
   of acceptance and resolution, then ALICE ITS+TPC, then STAR. In the toy, ALICE 3 gains ×10 from
   its 10¹⁴-event sample. ATLAS, CMS, LHCb and FASER are out (§6.3).

## 1. Which X17 a collider can make

| hypothesis | P → γX17 (π⁰, η, η′) | ω → π⁰X17 | status of the X17 interpretation |
|---|---|---|---|
| vector (protophobic, Feng et al. 2016) | allowed. BR(π⁰) = 2ε_p²(1−m²/m_π²)³ BR(γγ); BR(η) depends on ε_s and η–η′ mixing | allowed | ε_p is capped by NA48/2: BR(π⁰ → γX17) < 1.2×10⁻⁶. The protophobic vector is excluded by SINDRUM π⁺ → e⁺νX (Hostert & Pospelov, PRD 108 (2023) 055011), unless the electron coupling is tuned to cancel |
| axial vector (C-even) | forbidden by C (π⁰: +, γ: −, X: +) | forbidden by C | strongly constrained but alive (Hostert & Pospelov; "The X17 with chiral couplings", arXiv:2602.11263) |
| pseudoscalar | forbidden (0 → 0 + γ) | allowed only via mixing | n/a here |
| chiral (V and A) | through its vector part | through its vector part | arXiv:2602.11263: 99 % region in tension with atomic parity violation and electron-beam searches |

**The η is where a vector X17 would show up.** For the Feng et al. protophobic point
(ε_u = −ε_n/3, ε_d = 2ε_n/3, |ε_n| ≈ 1.1×10⁻²), π⁰ → γX vanishes. The η keeps a singlet piece.
With θ_P = −20°, f₈ = 1.26 f_π and f₁ = 1.17 f_π, this gives **BR(η → γX17) ≈ 2.6×10⁻⁵
(ε_s = ε_d) to 9×10⁻⁵ (ε_s = 0)** (`toy/analytic.py`, `out/analytic_eta_protophobic.csv`). This
is an estimate, not a prediction: ε_s is free in the model, and the model itself is excluded.
REDTOP lists η → γX17 as a flagship channel. As of Feng et al. 2016, the η searches (HADES,
WASA) applied only above m ≈ 20 MeV. Whether a direct η → γe⁺e⁻ limit at 17 MeV has appeared
since is **(ask/verify)**.

**What colliders do not reach:**
- X17 from nuclear de-excitation in the detector material: at rest, 8.4 MeV leptons (§2).
- X17 from excited spectator fragments: at beam rapidity, outside every central barrel.
- Bremsstrahlung or thermal X17 in the fireball: not estimated. Its S/B against the real-photon
  equivalent goes as ε², like the meson channels.

## 2. Kinematics and tracking thresholds

`out/analytic_kinematics.csv`, `out/analytic_thresholds.csv`, figures `out/fig_lepton_pt.png` and
`out/fig_scan_acceptance_resolution.png`.

| X17 source | p_X in the parent frame | lepton p (symmetric) | minimum opening angle |
|---|---|---|---|
| at rest (ATOMKI nuclei) | 0 | 8.4 MeV | 180° |
| π⁰ → γX17 | 66 MeV | 34 MeV | 28° |
| η → γX17 | 274 MeV | 137 MeV | 7.0° |
| ω → π⁰X17 | 379 MeV | 190 MeV | 5.1° |

A primary track reaches radius r if 2R ≥ r, with R = pT/(0.3B). The pT needed to reach the
layers a track cut requires:

| detector | B | track cut | reach r | pT_min |
|---|---|---|---|---|
| STAR iTPC | 0.5 T (0.25 T) | 15 rows | 79 cm | **59 MeV** (30) |
| sPHENIX TPC tracks | 1.4 T | MVTX ≥ 2 + 20 TPC layers | 48 cm | 101 MeV |
| sPHENIX silicon only | 1.4 T | MVTX 3 + INTT ≥ 2 | 7.8 cm | **16 MeV** |
| ALICE ITS+TPC | 0.5 T (0.2 T) | 70 TPC rows | 160 cm | 120 MeV (48) |
| ALICE ITS standalone | 0.5 T (0.2 T) | IB 3 + OB 2 | 24.5 cm | 18 MeV (7.4) |
| ALICE 3 (approx.) | 2 T (0.5 T) | 3 vertex + 2 outer | 12 cm | 36 MeV (9) |

The softer lepton of a π⁰ → γX17 pair has a median pT of ~30 MeV in Au+Au. For η it is
~70 MeV (`fig_lepton_pt`). So STAR and the sPHENIX TPC lose most π⁰-made X17, while silicon
tracking keeps them. Pair acceptance for |η_X| < 0.5, from the scan runs:

| p_X [GeV] | 0 | 0.05 | 0.1 | 0.2 | 0.4 | 0.8 |
|---|---|---|---|---|---|---|
| STAR 0.5 T | 0 | 0 | 0 | 0.30 | 0.60 | 0.79 |
| sPHENIX TPC | 0 | 0 | 0 | 0 | 0.28 | 0.51 |
| sPHENIX silicon only | 0 | 0.20 | 0.45 | 0.62 | 0.71 | 0.77 |
| ALICE ITS-SA 0.5 T | 0 | 0.18 | 0.51 | 0.73 | 0.85 | 0.92 |
| ALICE ITS-SA 0.2 T | **0.23** | 0.60 | 0.77 | 0.88 | 0.94 | 0.96 |
| ALICE 3, 0.5 T | 0.002 | 0.54 | 0.74 | 0.86 | 0.93 | 0.97 |

The sPHENIX silicon plateau at ~0.8 is the MVTX length (|z| < 13.5 cm) against a 10 cm vertex spread.

## 3. How much the pairs scatter

The Highland angle per lepton is θ₀ = 13.6 MeV/p · √t·(1 + 0.038 ln t). For t = 0.22 % X₀ (a
0.76 mm Be pipe) θ₀ is 3.3° at 8.4 MeV, 0.56° at 50 MeV and 0.14° at 200 MeV
(`out/analytic_thresholds.csv`, θ₀ at 50 MeV per detector).

**What matters is the angle relative to the opening angle.** For a boosted symmetric pair,
θ_open ≈ 2m/E and m ≈ E·θ/2. Each lepton (p = E/2) scatters by θ₀ ∝ 2/E, so

  σ_M ≈ √2 · 13.6 MeV · √t (1 + 0.038 ln t) ≈ 19 MeV·√(x/X₀),

**independent of the X17 energy and mass** (`out/fig_ms_mass_floor.png`). Material before the
first measurement:

| detector | before first hit | σ_M floor (no vertex constraint) | toy σ(m_ee), π⁰ / η source |
|---|---|---|---|
| STAR | 0.28 % pipe + 0.62 % IFC + gas = 0.9 % (first hit at 55 cm) | 1.5 MeV | 1.17 / 1.19 MeV |
| sPHENIX, design | 0.22 % pipe (MVTX L0 at 2.46 cm) | 0.7 MeV | Si 0.51 / 0.55; TPC 0.34 / 0.39 |
| sPHENIX, quoted 1.8 % pipe | 1.8 % | 2.2 MeV | Si 0.98 / 0.99; TPC 0.62 / 0.68 |
| ALICE Run 3 | 0.23 % pipe (ITS L0 at 2.24 cm) | 0.7 MeV | ITS-SA 0.40 (0.5 T), 0.50 (0.2 T); ITS+TPC 0.32–0.36 |
| ALICE 3 | ~0 (vertex layers in vacuum) | n/a | 0.30 (2 T), 0.75 (0.5 T) |

The toy comes in **below** the floor because the fit uses the primary vertex (σ 20 µm with
silicon). A kink in the pipe at 2.0 cm, measured again at 2.46 cm, is mostly recovered: the
chord from the vertex to the first hit fixes the initial direction. STAR has no such hit, and its
resolution is ~1.2 MeV. Bremsstrahlung shifts the peak 0.1–0.4 MeV low and adds a low-mass tail
(INTT, 1.14 % X₀ per ladder, is the main source in silicon-only sPHENIX). Even so, every
configuration resolves 17 MeV to ≤ 7 %. For comparison, at n_TOF the X17 is at rest and the
leptons are at 8.4 MeV, so the 1.26 % X₀ capsule gives θ₀ ≈ 9° per lepton on a 110–180°
opening angle.

## 4. The toy (`toy/`)

- **Sources** (`kinematics.py`): π⁰ and η with a Tsallis pT spectrum, the same function of m_T
  for both. ⟨pT⟩_π = 0.42 GeV (Au+Au 200, minimum bias) and 0.46 GeV (pp 13.6 TeV). Integrated
  η/π⁰ = 0.126 (RHIC) and 0.141 (LHC), normalised to 0.48 at high pT. Flat in |y| < 2.
  - P → γX17, with X17 → e⁺e⁻ ∝ 1 + cos²θ*.
  - Dalitz P → γe⁺e⁻ with the Kroll–Wada spectrum over 8–30 MeV (form factor = 1).
  - π⁰ photons converting in the pipe and in the first silicon layer: P = 7/9·t/cos λ,
    Bethe–Heitler energy split.
- **Detector** (`detectors.py`): cylinders with x/X₀ and hit σ. TPC rows are decimated ×2 to ×4
  with σ/√rep. The track cuts are those in the §2 table. Vertex z is Gaussian, σ = 10 cm (RHIC)
  or 5 cm (LHC).
- **Simulation** (`tracking.simulate`): exact helix crossings, the outbound arc only (loopers
  stop at the turning point). At each material crossing: Highland scattering with the real path
  length, and Bethe–Heitler brems (−ln z ~ Γ(t/ln 2)).
- **Fit** (`tracking.TrackFit`): the track is assumed primary. Parameters are the vertex
  (Gaussian prior, 20 µm with silicon, 200 µm for STAR), the direction and 1/p at the vertex, and
  two kink angles per scatterer with a Highland prior. This is equivalent to a Kalman filter for
  Gaussian scattering; brems is not modelled in the fit (no GSF). Closure without scattering:
  δp/p = 0.2 %, χ²/ndf = 1.0 with scattering.
- **Pair cuts:** per-leg χ² p-value > 10⁻³. Then a **conversion veto** (`tracking.ConvPairFit`):
  both legs are fitted from a common point on the pipe or the first silicon layer, with one
  common direction and free momenta. A pair is rejected if that fit has p > 10⁻³.
- **Reach** (`analyze.py`): the window is the one that maximises S/√B around the fitted peak.
  B counts π⁰ and η Dalitz pairs plus conversions surviving all cuts. BR₃σ = 3√B/(N_P·A·f). The
  systematic versions use 3√(B + δ²B²) with δ = 10⁻⁴ and 10⁻³.
- **Numbers:** A_dy is "accepted pairs per X17 produced per unit rapidity", so A_dy = 1.6 means
  the acceptance is worth 1.6 units of y. Runtime is ~1.5 h on 16 cores for 12 configurations ×
  13 sources (`campaign.sh`).

## 5. RHIC: STAR and sPHENIX (10¹⁰ minimum-bias Au+Au, π⁰ dN/dy = 85)

`out/reach.csv`, `out/fig_reach.png`, `out/fig_mass_spectra.png`.

| configuration | A_dy (π⁰ / η) | σ_M [MeV] (π⁰ / η) | ε(cuts), η source | conversions surviving | BR₃σ π⁰, stat | π⁰, 0.1 % syst | BR₃σ η, stat | η, 0.1 % syst |
|---|---|---|---|---|---|---|---|---|
| STAR (0.5 T) | 0.81 / 1.48 | 1.17 / 1.19 | 0.89 | 1.5 % | 1.2e-07 | 2.4e-06 | 5.3e-07 | 1.1e-05 |
| STAR (0.25 T, hypothetical) | 1.45 / 2.12 | 1.27 / 1.33 | 0.91 | 0.7 % | 8.8e-08 | 2.3e-06 | 4.9e-07 | 1.2e-05 |
| sPHENIX TPC tracks | 0.26 / 0.58 | 0.34 / 0.39 | 0.80 | 0.0 % | 1.3e-07 | 6.9e-07 | 4.8e-07 | 2.9e-06 |
| **sPHENIX silicon only** | **1.61 / 2.04** | 0.51 / 0.55 | 0.77 | 0.7 % | **6.2e-08** | 8.6e-07 | **4.1e-07** | 5.0e-06 |
| sPHENIX TPC (quoted material) | 0.24 / 0.55 | 0.62 / 0.68 | 0.80 | 0.2 % | 1.5e-07 | 8.8e-07 | 5.8e-07 | 3.3e-06 |
| sPHENIX silicon (quoted material) | 1.56 / 2.00 | 0.98 / 0.99 | 0.73 | 1.7 % | 9.7e-08 | 1.9e-06 | 6.3e-07 | 1.5e-05 |

**STAR.**
- Tracks only boosted X17: π⁰ parents above pT ≈ 0.3 GeV, and most η.
- The 1.2 MeV resolution is fine for statistics, but it lets ×3 more Dalitz pairs into the window
  than silicon does, so STAR is the weakest once systematics count.
- Beam-pipe conversions fake ~6.7 MeV. 92 % of them pass the per-track χ² (the first hit is
  55 cm out), but the conversion-hypothesis fit removes them: 1.5 % survive, and they fall below
  the window.
- Halving the field halves the threshold and doubles π⁰ acceptance, but gains < 30 % in reach.
- For 60–200 MeV electrons there is only dE/dx for electron ID (TOF needs pT ≳ 0.2 GeV). That is
  not in the toy (§8).

**sPHENIX.**
- Silicon-only tracking is the way in: ×6 the TPC acceptance for π⁰-made X17, with 0.5 MeV
  resolution.
- The TPC-matched subset has the best resolution (0.34 MeV), hence the best systematics-limited
  reach (π⁰ 6.9×10⁻⁷). Analysed together, the two would be complementary.
- In the toy, the pipe conversions at 16.8 MeV are fully removed by the pair veto. Before the
  veto, ~40 % of them passed the per-track χ² (`out/pairs/sphenix_si__conv__auau200.csv`).
- With the material quoted in arXiv:2504.02240 (pipe 1.8 % X₀), resolution doubles and the
  surviving conversions become 20–25 % of the background. That number needs pinning down (ask).
- The silicon has no electron ID. Soft pions (pT < 60 MeV) are a few % of all pions and would
  pair combinatorially; this is not in the toy.

## 6. LHC

### 6.1 ALICE Run 3 (10¹² minimum-bias pp at 13.6 TeV, π⁰ dN/dy = 3.2)

| configuration | A_dy (π⁰ / η) | σ_M (π⁰ / η) | ε(cuts), η | conv. surviving | π⁰ stat | π⁰ 0.1 % | η stat | η 0.1 % |
|---|---|---|---|---|---|---|---|---|
| ITS+TPC 0.5 T | 0.23 / 0.53 | 0.32 / 0.36 | 0.82 | 0.1 % | 6.1e-08 | 4.7e-07 | 2.1e-07 | 2.0e-06 |
| ITS+TPC 0.2 T | 0.69 / 1.21 | 0.36 / 0.40 | 0.86 | 0.3 % | 4.0e-08 | 5.8e-07 | 1.7e-07 | 3.0e-06 |
| **ITS standalone 0.5 T** | 1.56 / 2.10 | 0.40 / 0.40 | 0.77 | 1.2 % | **2.8e-08** | 6.8e-07 | **1.5e-07** | 3.9e-06 |
| ITS standalone 0.2 T | 2.09 / 2.40 | 0.50 / 0.52 | 0.81 | 1.7 % | 2.9e-08 | 8.8e-07 | 1.6e-07 | 5.0e-06 |

- ALICE has the 10¹² pp sample, pipe conversions far below the window (2–6 MeV), the lowest-mass
  ITS, and electron ID from TPC dE/dx for the ITS+TPC subset.
- Pb–Pb (1.2×10¹⁰ events × 200 π⁰/y ≈ 2.4×10¹² π⁰ per unit y vs 3.2×10¹² in pp) gives about
  the same statistics, at much higher combinatorics.
- The 0.2 T runs are what reach X17 at rest, at 23 % pair acceptance. They barely help the meson
  channels: the acceptance gain is ×1.1–1.3, and the reach does not move.

### 6.2 ALICE 3 (approximate geometry, 10¹⁴ pp)

BR₃σ ≈ 2×10⁻⁹ (π⁰) and 1×10⁻⁸ (η) on statistics, but S/B ~10⁻⁵, so it is fully
systematics-limited at 10⁻⁴–10⁻³. Vertex layers in vacuum give the best resolution (0.3 MeV at
2 T). The 2 T layer at 1.2 cm fakes 14 MeV conversions, and the veto handles them in the toy.
The geometry and field options are from memory of the LoI (ask).

### 6.3 LHCb, ATLAS, CMS, FASER (not simulated)

- **LHCb:** the dipole sweeps leptons below ~1 GeV out of the spectrometer, and the forward boost
  makes the pairs collinear. The inclusive dark-photon programme starts at 2m_μ. The D*⁰ → D⁰A′(ee)
  proposal (Ilten et al. 2015; verify) probes a charm–light coupling that the X17 fits do not fix.
- **ATLAS/CMS:** tracking from pT ~ 0.1–0.5 GeV in 2–3.8 T, with pipe-conversion fake masses of
  30–50 MeV. A 17 MeV pair at E ≳ 5 GeV opens < 7 mrad. No.
- **FASER:** needs a long-lived X17. The ATOMKI band ε_e ≳ 7×10⁻⁴ (NA64 excludes
  1.3–6.8×10⁻⁴) gives cτ ≲ 10 µm. No.

## 7. How the signal would be recovered

1. **Soft-track pairs from the primary vertex.**
   - sPHENIX: silicon-only seeds (MVTX + INTT) down to pT ≈ 20 MeV, plus the TPC-matched subset
     for resolution.
   - ALICE: ITS-standalone down to ~20 MeV, plus ITS+TPC for electron ID.
   - STAR: TPC tracks from 60 MeV with the vertex constraint.
2. **Kill conversions at the pair level**, not with per-track DCA. Fit each opposite-sign pair
   once as primary and once as a conversion on each material layer (pipe, MVTX/ITS L0), and veto
   pairs that fit as conversions. In the toy this rejects 98–99 % of conversions and keeps
   75–90 % of the X17.
   - This is essential in sPHENIX, where the pipe conversions sit at 16.8 MeV.
   - The φ_V (pair-plane orientation) cut is the cheap version.
3. **Bump hunt in m_ee against the smooth Kroll–Wada spectrum**, NA48/2 style. The statistics are
   ~10⁸–10⁹ Dalitz pairs per 1 MeV window, against NA48/2's 1.7×10⁷ in total. The limitation is
   then the background shape at 10⁻⁴–10⁻³. Narrow detector structures in m_ee (the conversion
   fake-mass edges at 0.6·B·r for each layer) are the dangerous systematic.
4. **For η → γX17, tag the photon.** Reconstruct the γ (EMCal, or a conversion) and require
   m(γe⁺e⁻) ≈ m_η. This removes the π⁰ Dalitz background, which is 70–95 % of B in every
   configuration, at the cost of the γ efficiency. Even a ×10 rejection moves S/B for a
   10⁻⁵ BR from ~0.5 % to ~4 %, and frees the η reach from the shape systematic. **This is the
   channel and method worth a real study.**
5. **pp or peripheral events** over central A+A. S/B against Dalitz is the same per meson, but
   the combinatorial e⁺e⁻ (and π mis-ID) background grows with multiplicity squared.

## 8. Simplifications (none may reach a published note)

- No combinatorial pairs, no hadron mis-ID, no electron-ID efficiency (the reach scales ~1/ε_pair),
  no pile-up or out-of-time hits, no track-finding efficiency (perfect pattern recognition).
- Loopers stop at the first turning point. Tracks with dip angles beyond ±60° use a capped path
  length.
- Conversions are generated only in the pipe and the first silicon layer. IFC conversions (STAR
  47 cm, sPHENIX 20 cm) fake ≥ 140 MeV and fail the silicon requirements. Conversions surviving
  the veto rest on 10–70 MC pairs, so their share of B is uncertain to ×2. Where it is shown as
  0 %, no surviving conversion fell in the window (upper limit ~1 % of B).
- The Dalitz form factor is set to 1. Radiative corrections to Kroll–Wada (which NA48/2 needed)
  are left out.
- Spectra are a Tsallis/m_T-scaling stand-in, the same for every A+A centrality. The pp
  acceptance is used for Pb–Pb.
- Detector numbers marked (ask) in the per-experiment READMEs: pipe radii and walls, TPC point
  resolutions, ITS2 radii (from memory), sPHENIX IFC X₀, the whole ALICE 3 geometry.
- Datasets are round benchmarks, all (ask): 10¹⁰ Au+Au, 10¹² pp, 10¹⁴ pp. The reach scales
  as 1/√N_ev on statistics and does not move once systematics dominate.

## 9. Next steps

1. Decide whether the vector-X17 / η → γX17 case is worth pursuing, given the SINDRUM exclusion of
   the protophobic vector (§1). Check for any η → γe⁺e⁻ limit at 17 MeV published since 2016.
2. If yes: add the η photon tag (EMCal resolution per detector) and the combinatorial background
   (event mixing with a realistic soft-electron multiplicity) to the toy, starting with ALICE pp
   and sPHENIX silicon.
3. Pin down the (ask) items: the sPHENIX pipe and MVTX X₀ (0.22 vs 1.8 %), the ITS2 radii,
   whether silicon-only soft tracks are kept in the stored data, and the recorded minimum-bias
   samples.
4. Talk to the collaborations' soft-dielectron people before investing more: ALICE (low-B pp),
   sPHENIX (silicon seeding), STAR (iTPC low-pT).

## Sources

- Feng et al., PRL 117 (2016) 071803, [arXiv:1604.07411](https://arxiv.org/abs/1604.07411): protophobic couplings, NA48/2 ε < 8×10⁻⁴ → |2ε_u + ε_d| < 8×10⁻⁴, 2×10⁻⁴ < |ε_e| < 1.4×10⁻³, HADES/WASA η limits only above 20 MeV.
- NA48/2, PLB 746 (2015) 178, [arXiv:1504.00607](https://arxiv.org/abs/1504.00607): 1.69×10⁷ π⁰ Dalitz decays; Dalitz decays are the irreducible background.
- Hostert & Pospelov, PRD 108 (2023) 055011, [arXiv:2306.15077](https://arxiv.org/abs/2306.15077): SINDRUM π⁺ → e⁺νX rules out vector explanations, strongly constrains axial ones.
- [arXiv:2602.11263](https://arxiv.org/abs/2602.11263), "The X17 with chiral couplings".
- [arXiv:2601.05288](https://arxiv.org/abs/2601.05288): NA64 excludes 1.3×10⁻⁴ ≤ ε_e ≤ 6.8×10⁻⁴ at 16.7 MeV (as quoted there).
- REDTOP, [arXiv:2203.07651](https://arxiv.org/abs/2203.07651): η/η′ → γX17, the dependence on ε_s/ε_n.
- Detector sources: [`star/README.md`](star/README.md), [`sphenix/README.md`](sphenix/README.md), [`lhc/README.md`](lhc/README.md).
