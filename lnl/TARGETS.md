# Lithium targets: what they are, and which one we want

The numbers come from `lnl_rates.py` (PSTAR stopping, Zahnow cross sections) or the
cited papers. This file is meant to be readable by someone who has never seen a
target ladder.

---

## 1. What a "lithium target" physically is

- **A film a fraction of a micron to a few microns thick**, of a lithium compound
  (LiF, Li₂O, LiPON) or of lithium metal. It is laid on a **backing**: a metal or
  carbon foil or disk.
- The beam spot is mm-sized, so the target is coin-sized or a strip. It sits on a
  holder at the centre of a vacuum chamber, usually perpendicular to the beam.
- Examples:
  - **ATOMKI:** a strip of 10 µm Al foil carrying an evaporated LiF or Li₂O layer,
    held on an Al rod. It sits inside a **carbon-fibre tube** (the vacuum chamber),
    with the detectors outside the tube. The chamber is reduced to Ø48 mm in the 2023+
    two-arm setup.
  - **MEG II:** 7 µm LiPON sputtered on 25 µm Cu. The Cu holder is cooled through the
    flanges, and the target sits in a 400 µm carbon-fibre cylinder.
  - **LNL CN neutron line:** 10–40 µm metallic Li, rolled in an argon glovebox and
    pressed onto a 300 µm Cu cup that is also the beam stop.
- **How the film is made:**
  - LiF and Li₂O are **vacuum-evaporated** (thermal or e-beam) onto the backing, and
    the thickness is set by the evaporated mass.
  - LiPON is **RF-sputtered** from Li₃PO₄ in N₂. It is the battery-electrolyte
    material, and is chemically stable.
  - Li metal is evaporated in vacuum or rolled and pressed under argon.
  - Thickness and composition are then **measured with the beam itself**: RBS,
    NRA, or the 478 keV ⁷Li(p,p′γ) yield (PIGE). The AN2000 and CN are used for exactly
    this at LNL.

## 2. What the target has to do

1. **Put ⁷Li atoms where the beam has the right energy.** Every 100 µg/cm² costs ~20 keV
   of beam energy at 1 MeV. The 18.15 MeV resonance is 168 keV wide (lab), so a
   **thin target (≲ 300 µg/cm², ≲ 60 keV) samples one energy**. A **thick** one
   (one that stops the beam) also integrates down through the **441 keV resonance**.
   That resonance is 50× stronger and pure M1, and swamps the 18 MeV data.
   ATOMKI's 2016 accident was exactly this: metallic Li diffused into the backing.
   In `out/yields.csv` the "Li metal stops beam" row has **77 % of its γ₀ from
   17.64 MeV**.
2. **Make as few other γ-rays and pairs as possible.** Every other element in the
   compound and the backing is a γ source (§4). Every gram in the leptons' way is
   scattering and external pair conversion.
3. **Survive weeks of µA beam.** Heat, hydrogen implantation, oxidation, and lithium
   diffusing or evaporating.

## 3. The compounds compared

At 1.07 MeV, natural Li, per 100 µg/cm² (`lnl_rates.py`):

| film | ρ [g/cm³] | 100 µg/cm² is | ⁷Li atoms/cm² | ΔE [keV] | γ₀/proton | **γ₀ per keV of ΔE** | chemistry |
|---|---|---|---|---|---|---|---|
| **Li metal** | 0.534 | 1.9 µm | 8.0×10¹⁸ | 20 | 2.2×10⁻¹⁰ | **1.1×10⁻¹¹ (×3.6)** | Oxidises in seconds in air, melts at 180 °C, diffuses into Al. Handle and transport under Ar. |
| **Li₂O** | 2.01 | 0.50 µm | 3.7×10¹⁸ | 21 | 1.0×10⁻¹⁰ | 5.0×10⁻¹² (×1.6) | Hygroscopic: picks up H₂O/CO₂ → LiOH / Li₂CO₃. O is inert at 1 MeV. ATOMKI 2016/2022. |
| **LiF** | 2.64 | 0.38 µm | 2.2×10¹⁸ | 19 | 5.8×10⁻¹¹ | 3.0×10⁻¹² (×1) | Stable, easy to evaporate, the PIGE standard. But **¹⁹F** (§4). ATOMKI, LNL 2023–24, Zahnow, Montreal. |
| Li₂CO₃ | 2.11 | 0.47 µm | 1.5×10¹⁸ | 21 | 4.1×10⁻¹¹ | 2.0×10⁻¹² | What Li₂O turns into in air |
| LiPON | ~2.4 | — | — | ~40 keV/µm (MEG II) | — | ~LiF | Stable, sputtered; MEG II |

**γ₀ per keV of energy loss** is the figure of merit, because the energy window
that the physics tolerates sets the thickness. By that measure Li metal is 3.6× LiF,
and Li₂O is 1.6× LiF. In practice that buys less than it seems:
- the rate is not our limit (`ESTIMATES.md`);
- the stable compounds keep the energy profile known, which is limit #2 above.

**Enrichment.** Natural Li is 92.4 % ⁷Li. Enriched ⁷LiF or ⁷Li₂CO₃ (99.9 %) is
commercial and gains 8 %. The 7.6 % ⁶Li only does ⁶Li(p,α)³He (charged particles
that stop in the target), so it is harmless.

## 4. The other nuclei: what else lights up below 1.3 MeV

| source | reaction | what it emits | does it matter? |
|---|---|---|---|
| ⁷Li itself | (p,p′γ) | **478 keV γ**, σ ~ 50 mb near 1 MeV (estimate from Γ_p′ ≈ 6 keV in the 18.15 resonance; check Bykov 2021 / EXFOR). **~10⁶–10⁷ γ/s at 1 µA.** | By far the largest γ flux. It is below every trigger threshold and makes ~10² Hz of Micromegas hits, which is negligible. Also the standard **Li-content monitor** (ATOMKI watch it with HPGe). |
| ⁷Li | (p,γ₁) | 14.6 / 15.1 MeV γ and their IPC, **2× γ₀** | **Yes.** Same physics, 3 MeV less energy. It needs E_sum resolution to separate (`PHYSICS.md` §4.3). |
| ¹⁹F (LiF) | (p,αγ)¹⁶O | 6.13, 6.92, 7.12 MeV γ; resonances at 340, 484, 598, 669, 872, 935 keV… with σ up to ~0.1–0.5 b | Below the 16–20 MeV window, but **tens to hundreds of times the 17–18 MeV γ flux**: singles and accidentals. Also gives the **6.05 MeV E0 pair line** from ¹⁶O(0⁺₂), a calibration LNL uses on purpose. |
| ¹¹B (contamination) | (p,γ)¹²C, Q = 15.96 MeV; resonances at 163 keV (Γ 7 keV) and **675 keV (Γ 300 keV)** | **16.1–17.0 MeV γ and IPC**, right in the signal window | **The dangerous one.** Zahnow's commercial ⁷LiF had **B/Li = 0.24 in atoms**. Specify B-free material and measure it (NRA, ¹¹B(p,α)). |
| ²⁷Al (backing, holder) | (p,γ)²⁸Si, Q = 11.58 MeV; strong resonance at 992 keV | up to ~12.6 MeV γ | Below the window. ATOMKI see a ²⁸Si 11 MeV pair peak, and their Al rods raised the background. |
| ¹²C, ¹³C (backing, chamber, carbon build-up) | (p,γ) Q = 1.94 / 7.55 MeV | ≤ 8.5 MeV | Below the window |
| ¹⁶O (Li₂O) | (p,γ)¹⁷F, Q = 0.60 MeV | < 2 MeV | No |
| ¹⁵N (LiPON, air) | (p,αγ)¹²C, resonance at 429 keV | 4.43 MeV | No (and only on the 441 keV run) |
| ⁶³,⁶⁵Cu, Ta, Au (backing) | (p,γ), high Coulomb barrier | tiny | No, but they are high-Z for the leptons (§5) |

**Neutrons: none.** ⁷Li(p,n) opens at 1.881 MeV, and ¹⁹F(p,n) at 4.2 MeV.

## 5. The backing and the chamber

The leptons that matter leave at 50–130° to the beam and cross the backing obliquely,
if at all. The 17–18 MeV γ-rays cross it too and convert (external pair creation,
EPC). The EPC pairs are collimated (a few degrees) and sit at small opening angles,
far from 140°. MEG II: EPC trigger efficiency 0.026 %, negligible in the signal box.

| backing | x/X₀ | EPC/γ (≈ 7/9·x/X₀) | stops 1.1 MeV p? | remarks |
|---|---|---|---|---|
| 10 µm Al (ATOMKI) | 0.011 % | 9×10⁻⁵ | no (range 17 µm): beam goes on to a dump | ²⁸Si γ; Li diffuses into Al when hot |
| 20 µm C | 0.011 % | 8×10⁻⁵ | no (range 17 µm) | Lowest-Z; graphite/glassy C are good evaporation substrates |
| 25 µm Cu (MEG II) | 0.17 % | 1.4×10⁻³ | yes (range 8 µm) | good heat path |
| 300 µm Cu (LNL Li-metal) | 2.1 % | 1.6×10⁻² | yes | a heat sink, not a thin target: too much material |
| 100 µm Ta | 2.4 % | 1.9×10⁻² | yes | classic beam stop; worst for leptons |

The ATOMKI-style choice is a **thin, low-Z backing that lets the beam through to a
distant, shielded beam dump**. Any (p,γ) in the dump then happens away from the
detectors. Otherwise the backing is the dump: a thick Cu or Ta disk that is cooled
and adds 2 % X₀ behind the target. That is fine for leptons going forward of 90°, and
bad for backward ones.

**Heat.** 1 µA × 1.1 MeV = **1.1 W**, mostly in the backing or dump; the film itself
takes ~0.02–0.2 W/µA. The LNL Li-metal cup handles **10 W**, i.e. 5 µA at 2 MeV, at
~10 °C per W. ATOMKI switched from Plexiglas to Al target rods for cooling, which
let one target survive on- and off-resonance runs at 5 µA. MEG II used 8–11 µA on
LiPON/Cu with "no significant deterioration" over 4 weeks.

**Dose to the film.** One month at 1 µA is 2.6 C ≈ 1.6×10¹⁹ protons. On a ~0.3 cm²
spot that is ~5×10¹⁹ H/cm², implanted mostly in the backing. Hydrogen blistering of
Li compounds is a known failure of high-current BNCT targets. **(ask LNL / Mastinu)**
Plan to rotate or replace targets weekly and monitor:
- the 478 keV PIGE line;
- the γ₀ line width in a HPGe/LaBr₃ (ATOMKI's trick: the width of the 18 MeV γ line
  tracks the proton energy profile in the target).

## 6. Recommendation, for the first estimates and the Geant4 geometry

- **Production target:** **Li₂O or ⁷LiF, 100–300 µg/cm²**, evaporated on **10–20 µm Al
  or C**. Strip or disk, ⊥ beam, on a cooled low-Z holder, inside a thin carbon-fibre
  (or ≤ 0.5 mm Al) chamber tube of Ø ~40–60 mm. The beam continues to a Faraday-cup
  dump ≥ 1 m downstream, shielded from the arms.
  - Prefer Li₂O for rate, and LiF for stability and the free ¹⁶O E0 calibration
    line. Decide with LNL's target lab.
  - **Specify B-free lithium** and check it.
- **Calibration target:** LiF 30 µg/cm² at 441 keV (the 17.64 MeV M1 IPC line,
  ~1.2×10⁴ γ₀/s at 1 µA).
- **Energy plan:** 441 keV (calibration); **1.04 and 1.10 MeV** (ATOMKI's anomaly
  points); 0.80 MeV (direct-capture-dominated control, where ATOMKI 2022 also claims
  the excess); optionally 1.225 MeV (Hanoi).
- Things to **avoid**:
  - thick metallic Li on Al;
  - H₂⁺ in the beam (MEG II's 25 % H₂⁺ put most of their data on 441 keV): require an
    analysing magnet tuned to H⁺;
  - Al anywhere close to the arms.

---

## Sources

- **Target recipes:**
  - ATOMKI: Krasznahorkay 2016 and Sas 2022 (§ Experiments; the oxidised-Li story is
    in Sas 2022 §V).
  - MEG II: EPJC 85, 763 §2.1.
  - LNL Li metal: arXiv:2605.12005 §4.1.
  - LNL LiF: Góngora-Servín 2025.
  - Zahnow 1995 target composition, incl. the boron: EXFOR A0639.
- **LiF evaporation on Ag** (thickness 184 µg/cm², 6 % non-uniformity): arXiv:2208.03425
  (`refs/LiF_target_prep_arXiv2208.03425.txt`).
- **Not yet retrieved** (paywalled):
  - Bykov *et al.*, Appl. Radiat. Isot. (2021), ⁷Li(p,p′γ) 0.7–1.85 MeV;
  - EPJA (2026), "Gamma ray production of ⁷Li and ¹⁹F … 700–2730 keV";
  - "Thick-target yield of 17.6 MeV γ … at 441 keV", NIM B (2022): 3.2×10⁻⁹ γ/p. We
    get 4.8×10⁻⁹ (γ₀, LiF) to 1.7×10⁻⁸ (Li metal); the paper's target composition
    is unknown to us.

  These would pin the 478 keV and ¹⁹F γ rates, which are background-only.
