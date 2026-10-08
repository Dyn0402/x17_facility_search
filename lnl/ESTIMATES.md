# What the MX17 apparatus would see at LNL: the pre-Geant4 estimate

> **2026-10-08: superseded for the detector by `FEASIBILITY_SIM.md` (Geant4).** As built: pair-tag
> 3.3 % (not 0.14 × 36 %), γ₁ removed by the E_sum window, cosmics need 3° segments or TOF;
> 15 d → 15 d (counting), big plastics 1.2 d. The rates and yields here (§1) still stand.

From `lnl_rates.py`, run 2026-10-07. Tables: `out/*.csv`; figures: `out/figures/`.
Every input is listed in §4 with what replaces it. **Treat every reach number here
as good to a factor ~2.** The biggest single uncertainty is `EPS_REST`, the
trigger × E_sum × reconstruction efficiency carried over from the ILL campaign.

---

## 1. Rates (4π, per µA, before any detector)

`out/yields.csv`. 1 µA = 6.24×10¹² p/s.

| configuration | ΔE in film | γ₀/s | γ₀+γ₁/s | where γ₀ comes from (17.64 res / 18.15 res / direct) | ⟨E\*⟩ |
|---|---|---|---|---|---|
| **ATOMKI 2016 anomaly**: Li₂O 300 µg/cm², 1.10 MeV | 61 keV | 1.85×10³ | 5.7×10³ | 0.6 % / 47 % / 52 % | 18.2 MeV |
| ATOMKI 2016 on-res: Li₂O 300, 1.04 MeV | 64 keV | 2.2×10³ | 6.4×10³ | 0.7 / 47 / 52 | 18.1 |
| ATOMKI 2022 direct: LiF 300, 0.80 MeV | 72 keV | 860 | 2.7×10³ | 4 / 8 / 88 | 17.9 |
| Hanoi: LiF 300, 1.225 MeV | 54 keV | 740 | 2.8×10³ | 0.5 / 14 / 85 | 18.3 |
| LNL 2023–24 thick: LiF 935, 1.09 MeV | 189 keV | 3.6×10³ | 1.1×10⁴ | 0.8 / 41 / 59 | 18.1 |
| MEG-2026 normalisation: Li₂O 700, 1.03 MeV | 155 keV | 4.7×10³ | 1.4×10⁴ | 1 / 34 / 65 | 18.1 |
| 441 keV calibration: LiF 30 | 10 keV | 1.2×10⁴ | 1.7×10⁴ | 99 / 0 / 1 | 17.6 |
| **thick Li metal at 1.10 MeV (don't)** | stops | 1.4×10⁵ | 2.6×10⁵ | **77** / 5 / 18 | 17.7 |

So at ATOMKI conditions:
- ~2×10³ ground-state γ/s;
- **~7 IPC pairs/s** from those transitions (~21/s counting γ₁);
- at R = 5.8×10⁻⁶, **~0.011 X17/s, ~900/day into 4π.**

Cross-checks:
- **σ(γ₀+γ₁) at 441 keV.** The model gives 5.93 mb; Tilley gives 5.9 ± 0.5 mb.
- **γ₀/(γ₀+γ₁) at 441 keV.** The model gives 0.69; Tilley gives 0.69–0.72.
- **MEG II's own 2026 normalisation** of ATOMKI running gives R_γ ≈ 1 kHz and
  R_IPC ≈ 4 Hz at 1 µA, with "σ ≈ 20 µb" at 1030 keV and n = 1×10¹⁹ /cm². We
  get 2.2 kHz.
  - Our σ(γ₀) = 33 µb includes the direct capture under the resonance.
  - With their n and σ we reproduce their 1.5×10⁻¹⁰/p.
  - So the factor 2 is in the inputs, not the method.

## 2. The detector, as a toy

`out/acceptance.csv`, `out/figures/acceptance.png`. The four n_TOF arms:
- Micromegas faces at 204 mm from the beam axis;
- active area 399.4 (⊥ beam) × 359.9 mm (along the beam);
- a point source;
- both leptons in two **different** arms with KE > 1 MeV;
- σ_θ = 5°.

| | two-arm geometric | in 125–155° (measured) | generated in 125–155° |
|---|---|---|---|
| X17, m = 16.7, 18.15 MeV | 45 % | **36 %** | 85 % |
| X17, m = 17.0 | 47 % | 36 % | 81 % |
| IPC M1, 18.15 | 10 % | 0.69 % | 2.1 % |
| IPC E1, 18.15 | 13 % | 1.8 % | 4.6 % |
| IPC M1, 15.1 (γ₁) | 10 % | 0.68 % | 2.2 % |

The four big arms around a point target **see the 140° region through opposite
arms**, with ~40 % geometric acceptance for the signal. ATOMKI's 5-telescope
spectrometer has ~2.5 % pair acceptance. **Geometry is not our problem; the
trigger stack is.** As built it accepts 2.3 % of X17 pairs against 27.6 % for the
Micromegas (`../trigger_scint`). The toy multiplies everything after geometry by one
factor, `EPS_REST = 0.038/0.276 = 0.14`, the ILL G1 ratio of X17 acc × ε to
Micromegas acceptance. The E1 IPC has 2.5× the M1 rate at 140°, which is why the
direct-capture half of the γ₀ matters.

## 3. Reach

`out/reach.csv`. This is a counting experiment in 125–155°, with background = IPC (M1
from the resonances, E1 from direct capture) + cosmics. A template fit over all
angles, which is what everyone actually does, is typically ~1.5× better.

- **Cosmics:** n_TOF hardware with the ILL §10 cuts (MM segments ≤ 3° + 20°
  collinearity veto) gives ~200/day in the analysis window. That is conservative,
  because the ILL window was 60–180°.
- **γ₁ IPC:** the γ₁ (15 MeV) IPC is either counted in full (**g1 leak = 1**, the
  n_TOF stack, ~40 % containment) or removed (**0**, a calorimeter).

**Days to reach the ATOMKI ratio R = 5.8×10⁻⁶** at 3σ / 5σ:

| configuration | I | g1 leak = 1 (as built) | g1 leak = 0 (calorimetry) | X17/day accepted | IPC (γ₀) / γ₁-IPC / cosmic per day |
|---|---|---|---|---|---|
| ATOMKI 2016 anomaly (Li₂O 300, 1.10 MeV) | 1 µA | **15 / 41 d** | **6 / 16 d** | 46 | 1.1k / 2.1k / 200 |
|  | 4 µA (CN) | 3.6 / 10 d | 1.3 / 3.5 d | 184 | 4.6k / 8.6k / 200 |
| ATOMKI 2016 on-res (Li₂O 300, 1.04 MeV) | 1 µA | 11 / 31 d | 4.7 / 13 d | 55 | 1.4k / 2.2k / 200 |
| LNL-style thick LiF 935, 1.09 MeV | 1 µA | 7.7 / 21 d | 2.9 / 8 d | 90 | 2.4k / 4.4k / 200 |
| Li₂O 700, 1.03 MeV | 1 µA | 6.3 / 18 d | 2.3 / 6.4 d | 117 | 3.3k / 6.2k / 200 |
| ATOMKI 2022 direct (LiF 300, 0.80 MeV) | 1 µA | 52 / 143 d | 20 / 55 d | 21 | 0.7k / 1.5k / 200 |
| Hanoi (LiF 300, 1.225 MeV) | 1 µA | 67 / 186 d | 22 / 60 d | 18 | 0.6k / 1.7k / 200 |

How to read it:

1. **At ATOMKI's ratio, the X17 is a 3σ effect in about two weeks at 1 µA with
   the n_TOF hardware**, and 5σ in ~6 weeks. If the 15 MeV transitions can be
   separated it is a week or less.
   - CN's ~4 µA cuts the times by ~4.
   - The MEG II 90 % limit (1.2×10⁻⁵) is 2× the ATOMKI value, so it is crossed in
     ~¼ of these times.
2. **We are IPC-limited, not cosmic-limited.**
   - This holds once the MM tracks are used: the vetoes leave ~200/day against
     1–3×10³ IPC/day in the window.
   - **Without any cosmic veto** (~1.8×10⁴/day) the reach is **2.5× worse**: cosmics
     dominate exactly as the MEG II 2026 paper says they do for ATOMKI.
   - The point-vertex cut and CN pulsing (columns 3–4 of `reach.csv`) change nothing
     further at 1 µA. They matter only at lower current or with worse tracking.
3. **Thicker films help, up to the point where the E\* spread matters.** 935 µg/cm²
   LiF spans 1.09 → 0.90 MeV, i.e. E\* 18.2 → 18.0. The E1/M1 mix then varies across
   the film, and the background shape gets harder to model. That is ATOMKI's 2016
   lesson in miniature.
4. **The off-resonance points are 3–4× slower.**
   - These are 0.8 and 1.225 MeV, where ATOMKI 2022 and Hanoi see their excesses.
   - The reason is that σ(γ₀) halves and E1 (flat) IPC dominates the background.
   - They are the decisive test of "X17 from direct capture", and worth a few weeks
     once the 1.04/1.10 MeV running works.

**Compared with the ILL thermal search** (`../ill`):
- **Signal:** ~45 accepted X17/day here at R(ATOMKI), against ~14/day at the ILL
  at its 2.5×10⁻² reference.
- **Background:** ~10³/day IPC here; the ILL has a background zoo of neutron
  captures.
- **The ⁸Be measurement is a far easier experiment for this apparatus.** It is also
  the one with the claim and the direct null results (MEG II), so it is the one
  that decides.

## 4. What is assumed, and what replaces it

| input | value used | uncertainty | replaced by |
|---|---|---|---|
| σ(γ₀), σ(γ₀+γ₁) | Zahnow 1995 (EXFOR), 8–11 % | small | — |
| resonance/direct split | BW with constant widths + remainder; not meaningful below ~500 keV | ~20 % on the M1/E1 mix at 1 MeV | Zhang–Miller / NCSMC E1/M1 decomposition; ATOMKI's fitted I(E1)/I(M1) |
| stopping | PSTAR, Li by Bragg subtraction | ~5–10 % | SRIM / measured film thickness (RBS) |
| IPC α | Born (Z → 0): 3.47×10⁻³ M1 vs Rose 3.9×10⁻³ | ~10 % | Coulomb-corrected tables |
| IPC angular shape | Born M1/E1, no M1–E1 interference | interference shifts the large-angle tail by tens of % (Gysbers 2023) | Zhang–Miller generator (MEG II used it) |
| acceptance | toy planes, no pinwheel offset, no scattering, KE > 1 MeV | ~20 % | **Geant4** with the real arm placement |
| **EPS_REST** | **0.14 (ILL G1)** | **×2** | **Geant4 S1-type pair runs at W = 18.15 MeV with the per-arm trigger and the E_sum cut** |
| γ₁ separation | 1 (none) or 0 (perfect) | the whole factor 2.5 | Geant4 E_sum response for 15 vs 18 MeV IPC |
| cosmics | ILL §10 after cuts, 200/day | ×3 (window, hall overburden) | Geant4 K1-type run with the LNL geometry; a beam-off run at LNL |
| EPC, ¹⁹F/¹¹B, accidentals | neglected | small at 140° for EPC; ¹¹B could be large if the target is dirty | Geant4 γ-source runs (17.6, 18.15, 14.6, 15.1, 6.13 MeV) through the chamber/target |
| R for direct capture | same R as the resonance | unknown, a physics question | — |
