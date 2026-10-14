# LNL ⁸Be with MX17: the Geant4 feasibility

Written 2026-10-08, from the overnight Geant4 campaign on the MX17_Full_Geant `lnl`
branch. This replaces the detector half of `ESTIMATES.md`: the toy acceptance ×
`EPS_REST`, the γ₁ "leak" and the borrowed ILL cosmic rate. The physics weights are
unchanged: cross sections, yields, the direct/resonant split and the IPC α all come
from `lnl_rates.py` (`out/yields.csv`, `out/ipc_alpha.csv`).

Code: `sim/lnl_geant.py`. Outputs: `out/geant/*.csv` and `out/geant/figures/`.
The lxplus reduction is in `sim/lxplus/`.

---

## 0. Bottom line

**Update 2026-10-12, third pass (§14): realistic calorimetry, a single-arm trigger, and a 3D fit.**
- **Calorimetry.** The arm energies now get an n_TOF-anchored response:
  - plastic bars: a = 0.32 √MeV, 2–5 % face terms;
  - the liquid: as measured, or repaired;
  - per-arm gains as fit nuisances.

  Big plastics hold: 0.83 → 1.4 d for the m_ee fit, calibrated. **As built does not:** 8 → 35 d with a
  repaired liquid, ~190 d with the liquid as at n_TOF, ~490 d without it.
- **Fit θ × |y| × E_sum instead of m_ee alone.** With the background-shape error defined once on the
  events, the 3D fit is faster and robust:

  | | 3D fit, calibrated | worst structure tried | m_ee alone, worst |
  |---|---|---|---|
  | **big plastics** | **1.0 d** | 1.2 d | 3.1 d |
  | **as built** (liquid repaired) | **17 d** | 21 d | 529 d |

  It is also stable between Monte Carlo halves, where the angle-only fits are not.
- **Trigger.** Every arm leg triggers; pairs are never prescaled; singles are prescaled 1/P. At P = 1,
  DREAM is 91–98 % live up to 4 µA. The single-arm cosmics give each arm's gain to ~1 % per hour.
- **The n_TOF data have given what they can.** The open numbers need bench tests: the 5 cm plate
  response, and whether a liquid cell can be repaired.

**Update 2026-10-12, second pass (§13): fit the pair mass.** With W = 18.15 MeV known, the opening
angle θ and the energy split y = (E₁ − E₂)/(E₁ + E₂) give the pair mass, m_ee² = W²(1 − y²)(1 − cos θ)/2.
In θ the X17 is a smeared edge on the IPC, and S/B ≈ 7 %. In m_ee it is a peak 0.6 MeV wide, so a few %
of unknown structure in the IPC shape costs little.

Days to 3σ at R(ATOMKI), 1 µA, from the L7 IPC samples (×10–20 the statistics above 90°, with the γ*
anisotropy about the beam):

| | statistics only | 2 % unknown shape | 2 % shape + in-run controls |
|---|---|---|---|
| big plastics, θ fit, all pairs | 1.07 | 13.9 | 6.1 |
| big plastics, θ fit, \|y\| < 0.3 | 0.76 | 4.3 | 1.2 |
| **big plastics, m_ee fit** | **0.52** | **0.93** | **0.83** |
| as built, θ fit, all pairs | 13.7 | 1590 | 353 |
| as built, θ fit, \|y\| < 0.3 | 13.3 | 43 | 17 |
| **as built, m_ee fit** | **5.8** | **9.4** | **8.0** |

The §12 numbers were the first pass: θ fit, |y| < 0.3, on L2 templates without the anisotropy.
ATOMKI's own bump is only +25–35 % over their IPC curve, and their 6.8σ also assumes that curve's
shape (§12.2). The text below is the 2026-10-08 statistics-only result (§11: one week of pseudo-data).

1. **As built, the n_TOF hardware reaches the ATOMKI ratio at 3σ in about 2–3 weeks
   at 1 µA**, provided the cosmics are killed by either of two cuts:
   - Micromegas segments good to ≲ 3°;
   - a ~0.3 ns time-of-flight cut between the arms.

   This is the same as the pre-Geant4 guess (15 d), but for different reasons:
   - The signal acceptance is **2.4× lower than the toy**.
   - The **energy sum separates the 15 MeV (γ₁) IPC almost completely**, which the
     toy did not assume.

   | 1 µA, Li₂O 300 µg/cm² at 1.10 MeV | counting, best window | template fit (IPC norm free) |
   |---|---|---|
   | as built, LS working | **15 d** | 22–24 d |
   | as built, LS off | 19 d | 25 d |
   | **big plastics (4 × 75×75×5 cm), all 20 SiPM bars** | **1.0–1.2 d** | **1.4–1.6 d** |

2. **The four big plastics are worth ×13–15 in running time.**
   - The trigger acceptance goes from 3.3 % to 23 % of X17 pairs (×7).
   - 5 cm of plastic is a calorimeter: 15 and 18 MeV transitions land 3 MeV apart
     (§3).
   - At CN's 4 µA, a 3σ test of ATOMKI takes **hours**, and the 0.8 / 1.225 MeV
     off-resonance points (ATOMKI 2022, Hanoi) take ~1 day each.
3. **Cosmics are the only background that can sink the as-built setup.**
   - Without vetoes, ~8×10⁴/day pass into 125–155°, against ~120 IPC/day after the
     same cuts (§4).
   - An E_sum *window* (13–17 MeV) works only if the LS work; muons leave 20–35 MeV.
   - **15° segments (the chambers as measured) do not stop them. 3° segments or TOF
     do**: with the E_sum window, either brings them to ~1/day; together, to 0 in a
     live day.
   - This is MEG II's 2026 point about ATOMKI, now quantified for MX17.
4. **Everything else is small:**
   - EPC from the target region: ≤ 10⁻² of the IPC in the window.
   - Accidentals: ≲ 0.02/day.
   - DREAM dead time: 3.5 (as built) or 22 (big plastics) two-arm triggers/s, from
     cosmics. That means < 1 % dead.
   - The 478 keV ⁷Li line never makes a leg.
5. **Material.**
   - The chamber wall sets the opening-angle resolution: CFRP 0.4 mm gives 5.1°,
     Al 0.5 mm 8.8°, Al 1 mm 12.2°.
   - A Cu backing costs 2.4° over Al/C.
   - Acceptance does not change.
   - **Keep the CFRP chamber and a low-Z backing.**
   - Against no scattering at all, the CFRP chamber costs ~11 % in running time, and an Al 1 mm
     tube ×1.33 (§10).
6. **Why the big plastics win (§9, 2026-10-09).**
   - It is acceptance. The X17 rate per day goes ×15, and the IPC ×14 with it, so S/B is unchanged.
   - About 65–70 cm square is enough where the bars are now (41 cm), and ~55–60 cm right behind
     the SiPM wall. Past that, the 40 × 36 cm Micromegas set the acceptance.
   - The neighbouring plates' footprint never binds first.
   - This is a toy calibrated on Geant4. A Geant4 oversized-plate run should confirm it before
     buying.

## 1. Runs (2026-10-08, lxplus condor)

All runs use the `--target li` baseline:
- Li₂O 300 µg/cm² on Al 10 µm;
- Al 1 mm holder annulus;
- CFRP 0.4 mm chamber of bore 25 mm;
- Ta 2 mm dump;
- σ_spot = 2 mm;
- n_TOF arms at the surveyed positions.

Binaries:
- `bin/mx17_full_sim_lnl_079db11` for L1/L2 as built;
- `bin/mx17_full_sim_lnl_a424eed` for everything else. It is the `lnl` branch with
  `trigger_plastics` merged; the physics is identical.

Outputs are in `/eos/experiment/ntof/data/x17/lnl/<run>/<sample>/`.

| run | samples | events | notes |
|---|---|---|---|
| L1 | X17 at W = 18.15, m = 16.6 / 16.7 / 16.8 / 17.0 | 10⁶ each | |
| L2 | Born IPC M1/E1 at 18.15, M1 at 17.64, M1/E1 at 15.1 and 14.6 | 10⁶ each | |
| L1/L2 `_bigP` | the same with `--big-plastic 75 75 5 --no-ls --sipm-readout 20 0` | 10⁶ each | the trigger_scint calorimeter option |
| L1/L2 `_sipm20` | X17 16.7/17.0 and the 18.15/17.64/15.1 IPC, with all 20 SiPM bars read | 10⁶ each | |
| L3 | γ lines from the spot: 8Be (18.15, 17.64, 15.1, 14.6), ¹⁹F (6.13, 6.92, 7.12), ⁷Li 0.478, ²⁸Si 10.76 + 1.78 | 2.1×10⁸ 8Be γ as built, 1.1×10⁸ big plastics; 5×10⁶ each other set | EPC, singles, accidentals |
| L4 | cosmic μ (3×3 m plane, 1 /cm²/min, zenith ⊥ beam), as built and big plastics | 1.3×10⁸ each = 1.00 live day | |
| L5 | X17 16.7 and M1 18.15 with chamber Al 0.5 / Al 1.0 mm, backing C 20 µm / Cu 25 µm | 5×10⁵ each | |
| L6 | E0 IPC at 6.05 MeV (¹⁶O 0⁺₂, the LiF calibration line) | 10⁶ | |

**Reduction** (`sim/lxplus/`, all on condor):
- `lnl_reduce.py`: per file, `ill_pairs.py` reduce + the ILL `seg_reduce.py`.
- `lnl_time.py`: earliest SiPM-wall and plastic time per arm.
- `lnl_merge.py`: one compact table per sample.
- `lnl_pipe.sh` drives them; it is idempotent.

Copy the tables locally with `sim/fetch_sel.sh` (gitignored `sim/sel/`).

## 2. Selection, data-like

Nothing uses Monte Carlo truth to select.
- **Ok arm:**
  - a trigger leg in that arm: a SiPM bar AND a plastic, each ≥ 0.5 MIP, the
    thermal_accounting definition;
  - a Micromegas dominant-track segment (≥ 3 steps);
  - its charge centroid in the active area (|along beam| < 180 mm, |transverse −
    pinwheel shift| < 199.7 mm).
- **Pair:** ≥ 2 ok arms; the two with the most scintillator energy.
- **Opening angle:** the chord from the beam spot (0,0,0) to the two MM charge centroids.
  - Resolution for the X17: **σ68 = 5.3°, bias +0.5°**.
  - The arm choice matches the true lepton arms in 99.8 % of events.
- **E_sum:** SiPM + plastic + LS energy of the two arms, in a window [E_lo, E_hi].
  - The window is chosen per hardware and analysis level on the reference setting.
  - In "LS off", the LS energy is dropped.
- **Analysis levels:**
  - **trigger:** nothing more.
  - **MM 15° / MM 3°:**
    - each segment, with its direction smeared by 15° (the measured chambers:
      11–26°) or 3° (the ILL upgrade scenario), must point back to the spot within
      D;
    - D keeps 90 % of X17 segments per arm (135 mm at 15°, 57 mm at 3°; at 3°,
      scattering in the window and gas dominates);
    - plus a 20° collinearity veto on the two segments.
  - **+ TOF:** each arm's earliest SiPM-wall time, smeared by σ_t = 0.3 ns.
    - A pair is vetoed if the lower arm fires > 2√2 σ_t = 0.85 ns after the upper
      arm (|Δt| for arms at the same height).
    - X17: |Δt| < 0.15 ns (95 %).
    - Cosmics: the lower arm fires 2.3 ns later (median).
    - **σ_t = 0.3 ns is an assumption (ask):** what the n_TOF SiPM wall achieves
      with its digitiser is not documented here.
- **Reach:**
  - **Counting** in the window that maximises S/√B (typically 130–165°).
  - **Asimov template fit** over 90–180° in 2° bins:
    - IPC normalisation and γ₁ free, M1/E1 mix fixed: "fit, 1 norm";
    - or M1, E1 and γ₁ all free: "fit, 3 norms", in `reach_geant.csv`.
  - Background templates are smoothed with a 5° Gaussian KDE: the IPC samples leave
    only 10–200 MC events per 10° above 90°, and empty bins would fake infinite
    sensitivity.
  - Days are scaled to 3σ at R = 5.8×10⁻⁶ and divided by the DREAM live fraction.

## 3. Acceptance and energy

`out/geant/acceptance_geant.csv`, `figures/geant_chain.png`, `figures/geant_esum.png`.

| X17 m = 16.7 at 18.15 MeV | as built | 20 SiPM bars | big plastics |
|---|---|---|---|
| both leptons in the MM active area, different arms | 38.7 % | 38.8 % | 38.8 % |
| + a trigger leg in both arms (pair-tag) | **3.3 %** | 3.3 % | **23.2 %** |
| + E_sum window, + MM 15° + TOF, in 125–155° | 0.7 % | 1.2 % | **10.9 %** |

- **The toy was right about geometry:** 39 % against 45 %, the toy having no
  active-area cut.
- **The toy was wrong about what follows.**
  - The ILL `EPS_REST` = 0.14 was really 0.084 here (pair-tag over MM).
  - The four-arm geometry favours back-to-back pairs, so the accepted X17 spreads to
    170°. Only 64 % of the tagged pairs fall in 125–155°.
- **Reading all 20 SiPM bars buys nothing as built.** The two 20 × 30 cm plastics are
  the bottleneck (trigger_scint §1). With the big plastics, all 20 bars are used.
- **E_sum separates 15 from 18 MeV.**
  - **As built (with LS):** the 18.15 MeV pairs (X17 and IPC) peak at 14–15 MeV, and
    the 15.1 MeV IPC at 11–12 MeV with nothing above 13. A 13–16/17 MeV window keeps
    54 % of the X17 and removes the γ₁ IPC to < 0.5/day.
  - **LS off:** the peaks merge at 8–10 MeV and γ₁ stays in full.
  - **Big plastics:** sharp peaks at 15.3 and 12.3 MeV. A 13–17 MeV window keeps 83 %
    of X17 and 1.5 % of γ₁.
- **The mass scan** (`reach_geant.csv`): acceptance rises from m = 16.6 to 17.0 (3.1 →
  4.0 % pair-tag as built) because the edge moves to larger angles. Days to 3σ:
  16.7 → 16 d, 17.0 → 8.5 d as built; 1.2 → 0.9 d with the big plastics.

## 4. Backgrounds other than IPC

**Cosmics** (L4, one live day, `out/geant/cosmics_*.csv`). Pairs in 125–155° per day,
as built:

| level | no E_sum cut | E_sum 13–17 (LS on) | E_sum 8–16 (LS off) | big plastics, 13–17 |
|---|---|---|---|---|
| trigger | 82,000 | 3,700 | 71,000 | 460 |
| MM 15° (+20° coll.) | 14,600 | 570 | 12,600 | 61 |
| MM 3° | 41 | 1 | 37 | 2 |
| MM 15° + TOF | 10 | 1 | 7 | 0 |
| MM 3° + TOF | 0 | 0 | 0 | 0 |

One live day: the entries of 0–2 are single events (±100 %). The reach uses a smoothed
template scaled to max(n, 1) per day.

- The cosmic two-arm events have E_sum 20–34 MeV with the LS (median 26).
- **The upper edge of the E_sum window is the cheapest cut.**
- The 20° collinearity veto is ineffective at 15° segment resolution: two smeared
  segments of one straight muon differ by ~20° anyway.
- With the big plastics (5 cm), muons leave ~10 MeV per arm, and the 13–17 MeV
  window alone removes 99.8 %. With MM 15° + TOF, < 1/day remains, against 1,480 IPC/day.

**EPC and Compton from the target region** (L3, 5×10⁷ γ per line as built):
- per γ of 18.15 MeV, 3×10⁻⁶ two-arm events pass, all at 25–92° (adjacent arms);
- **none in 125–155° in 5×10⁷ γ** (< 6×10⁻⁸ per γ, against ~10⁻⁶ per γ for IPC in
  the window).
- With the big plastics (2.75×10⁷ γ per line), a few events land in the window:
  ~4×10⁻⁸ per γ after E_sum 13–18, ~10/day, < 1 % of the 1,480 IPC/day.

**Singles, accidentals, DAQ** (`out/geant/daq_load.csv`):
- Per 8Be γ: 0.39 % make a leg in some arm, and 0.04 % per arm are "ok" (leg + MM).
- At ATOMKI conditions (~6×10³ γ/s at 1 µA), each arm sees ~9–22 legs/s, the top and
  bottom arms mostly from cosmics.
- Two-arm hardware triggers are **3.5/s** as built and **22/s** with the big
  plastics. Both are cosmic-dominated; the beam adds < 0.3/s.
- DREAM at 298 µs → live ≥ 99 %.
- Accidental pairs with 2τ = 20 ns: ≲ 0.02/day in the window.
- **The other γ sources:**
  - ⁷Li(p,p′) 0.478 MeV: 5×10⁶ γ, **no leg**.
  - ²⁸Si 10.76 MeV, from ²⁷Al(p,γ) at the 992 keV resonance, when an Al backing is
    crossed at E_p > 992 keV: 0.36 % legs per γ, like the 8Be lines, at ~3× the γ₀
    rate. It is harmless after the E_sum window (its pairs have ≤ 10.8 MeV).
  - ¹⁹F lines (LiF targets): 0.3 % legs per γ, no two-arm events in 5×10⁶. **They
    matter only through singles:** at 10⁵–10⁶ γ/s (a LiF target crossing a strong
    ¹⁹F(p,αγ) resonance), legs reach 10²–10³/s per arm. Use Li₂O.

## 5. Material (L5)

`out/geant/material_scan.csv`, MM 15°:

| | X17 σ68(Δθ) | M1 σ68 | X17 acc (two-arm, MM 15°) |
|---|---|---|---|
| baseline: CFRP 0.4 mm chamber, Al 10 µm backing | **5.1°** | 6.6° | 2.09 % |
| Al 0.5 mm chamber | 8.8° | 12.6° | 2.12 % |
| Al 1.0 mm chamber | 12.2° | 17.6° | 2.16 % |
| C 20 µm backing | 5.1° | 6.2° | 2.08 % |
| Cu 25 µm backing | 7.5° | 11.7° | 2.10 % |

The resolution sets how sharp the X17 edge at 134–139° is. It matters for the mass and
for any IPC-shape systematic. **CFRP chamber, Al or C backing.**

## 6. What the trigger cannot see

- **The E0 6.05 MeV calibration line** (L6, ¹⁶O 0⁺₂ from F or O): **0 pair-tags in
  10⁶ pairs**, as built. The ~2.5 MeV leptons do not reach 0.5 MIP in both the SiPM
  bar and the 2 cm plastic behind ~2 g/cm² of MM stack.
- The 441 keV (17.64 MeV) M1 line *is* visible (L2 M1_17.64: same acceptance as
  18.15). It is the calibration point of choice.

## 7. Caveats

- **The LS energy.** The as-built E_sum, and so the as-built cosmic rejection, assume
  the LS work. At n_TOF they suffered pile-up (67–76 % of pulses). At LNL the rates
  are 10³× lower, so they should, but this was never shown. Without LS, the as-built
  setup needs the 3° segments or TOF *and* loses the γ₁ separation: 19 d instead of
  15 d.
- **TOF σ_t = 0.3 ns** is assumed (ask). The scan below is cosmics per day in 125–155°
  after MM 15° + E_sum 13–17 + TOF (cut at 2√2 σ_t), with the X17 efficiency of the TOF cut:

  | σ_t per arm | 0.2 ns | 0.3 | 0.5 | 0.7 | 1.0 | 1.5 |
  |---|---|---|---|---|---|---|
  | as built (MM 15° alone: 569) | 1 | 1 | 53 | 189 | 350 | 465 |
  | big plastics (MM 15° alone: 61) | 0 | 0 | 3 | 22 | 39 | 52 |
  | X17 efficiency of the cut | 0.96 | 0.97 | 0.97 | 0.97 | 0.97 | 0.97 |

  As built, TOF needs **σ_t ≲ 0.4 ns**: at 0.5 ns, 53 cosmics/day remain against ~110 IPC
  (~+25 % in time). At ≥ 1 ns it does little, and the 3° segments are needed.
- **IPC shapes are Born M1 and E1 without interference**, with the M1/E1 mix fixed by
  the Zahnow decomposition.
  - If the fit has to learn the mix (M1, E1, γ₁ all free), the days go up ×2.3–3
    (`days_fisher_live`). The accepted E1 IPC has its own hump at 140–170°, from the
    back-to-back geometry.
  - A measured off-resonance E1 shape (0.8 MeV runs) or the Zhang–Miller generator
    fixes this.
- **Cosmic flux:** 1 /cm²/min, sea-level vertical, no building overburden. LNL is at
  sea level; the hall roof would lower it slightly.
- **σ68 counts the MM centroid only.** A per-event vertex (two-track crossing) is not
  needed at LNL: the spot is σ = 2 mm.
- Not simulated: ¹¹B contamination (16 MeV γ, `TARGETS.md`), beam halo on the
  holder/flanges, and the beam pipe beyond the chamber.

## 8. Next

1. **Ask the collaboration:** the SiPM-wall time resolution in the n_TOF DAQ, and
   whether the LS can be read at LNL.
2. **Run the ATOMKI demonstrator data** through the same selection, if the test
   recorded MM + scintillators.
3. If the big plastics are bought: a T2 run at the final size, and the L4 cosmics
   with the real frame.
4. The Zhang–Miller IPC generator (M1–E1 interference) for the template systematic.
5. **The PAC case: with the big plastics, a week of AN2000 or a few days of CN covers
   the resonance, both off-resonance points and the 441 keV calibration.**
6. (2026-10-09) **Plastic size in Geant4:** one `--big-plastic 100 100 5` run with the front at
   ~35 cm (X17 + M1/E1 IPC). Cut smaller squares offline from the hits; it replaces the §9 toy.
7. (2026-10-09) **A no-wall (or CFRP 0.2 mm) L5 run**, to replace the 3.5° model floor in §10.
8. (2026-10-09) **Ask:** can the 5 cm plastics alone give the TOF and the leg coincidence? A
   plastic-only leg (no SiPM wall) gains ~1.4× in X17 (§9).
9. (2026-10-09) **The IPC shape systematic (§11).** S/B ≈ 7 %, so a 2 % shape error under the edge
   caps Z at 3.5σ. Plan the control data (sidebands, E_sum slices, off-resonance) and quote ε.

## 9. Why the big plastics win, and how big they need to be (2026-10-09)

Code: `plastic_size.py` → `out/plastics/` (figure `out/plastics/figures/plastics_size.png`).
Deck slides 12–14 ("Why big", "Configs", "Plastic size").

**It is acceptance.** Geant4, X17 m = 16.7, MM 15° + TOF, counting in 125–155°, as built →
big plastics (`out/plastics/chain.csv`):

| stage | as built | big plastics | factor |
|---|---|---|---|
| pair-tag (a leg in both arms) | 3.3 % | 23.2 % | **×7.1** |
| E_sum window kept (of tagged) | 54 % | 83 % | ×1.5 (5 cm is a calorimeter) |
| MM 15° + TOF kept | 60 % | 67 % | ×1.1 |
| in 125–155° (of the above) | 69 % | 85 % | ×1.24 (small plates favour back-to-back pairs) |
| **X17 per day in the window** | 6.5 | 99 | **×15.3** |
| **background per day** (IPC γ₀ + γ₁, cosmics, EPC) | 109 | 1,534 | **×14.1** |

- The IPC comes from the same spot into the same arms, so it is tagged as often as the X17
  (Geant4 pair-tag: M1 ×7.6, E1 ×6.8, X17 ×7.1). S/B stays at ~0.06.
- So days ∝ B/S² fall like 1/S: 23.5 → 1.4 d in 125–155° (×17). In the best window
  it is 15.5 → 1.2 d (×13).
- The picture: of the X17 leptons that cross a Micromegas (and have enough energy to make a leg),
  the as-built bars are hit by 36 %, the 20-bar SiPM wall shadow by 83 %, and 75×75 by 92 %. A pair
  needs both legs, so roughly 0.36² against 0.83².

**Size scan: a geometric toy, an analytic stand-in for Geant4.**
- The toy:
  - X17 and Born M1/E1 IPC with the generator kinematics of `X17PrimaryGenerator.cc`;
  - the surveyed arm geometry;
  - Highland kicks behind the MM (x/X₀ fitted: 0.03) and in the SiPM wall;
  - a lepton energy threshold (fitted: 5.25 MeV).
- It is fitted to the two Geant4 X17 pair-tags (3.0 vs 3.3 %, 22.6 vs 23.2 %).
- Checks (`calib.csv`):
  - The IPC pair-tags are ~40 % low in absolute terms. The big/as-built ratios (the only thing
    the scan uses) match Geant4 to ~3 %.
  - The 125–155° fractions are ~10 % high in absolute terms.
- Refitting with a 3 MeV threshold or less scattering moves the relative days by < 7 %.
- Days scale as (B/B₇₅)/(S/S₇₅)² from the Geant4 1.20 d at 75×75. E_sum/MM/TOF efficiencies are held
  at the big-plastic values (geometry only).

| square side (5 cm thick) | 40 | 50 | 60 | 70 | 75 | 100 |
|---|---|---|---|---|---|---|
| at R = 41 cm (where the bars are) | 5.6 d | 2.3 | 1.4 | 1.2 | **1.2** | 1.2 (pushed back) |
| at R = 35 cm (right behind the SiPM wall) | 2.9 | 1.4 | 1.2 | 1.2 | 1.2 | 1.2 |
| no SiPM wall in the leg, R = 26 cm | 1.1 | 0.86 | 0.88 | 0.92 | 0.94 | 1.0 |

(`days_vs_size.csv` has every 2.5 cm.)

- **It saturates.** At 41 cm, nothing is gained past ~65–70 cm: the plastic already covers the
  Micromegas cone, so the 40 × 36 cm Micromegas set the acceptance.
- **The footprint never binds first.**
  - Centred square plates at front distance R touch their neighbours once
    S/2 + 1.7 cm (pinwheel) + 1 cm (wrap) > R (`footprint.csv`): 77 cm at 41 cm.
  - The Micromegas cone at R is only ~0.91·R wide on each side, so the size worth buying always
    fits.
  - Larger plates have to move back and lose a little.
- **Closer is cheaper.** Right behind the SiPM wall (35 cm), ~55–60 cm does the job of 75 cm:
  1.2–1.4 m² of plastic for four arms instead of 2.25 m².
- **The SiPM wall is now the limit.** With the big plastics, the 50 cm wall cuts ~10 % of the
  leptons (83 % vs 92 %). A plastic-only leg at 26 cm, 45–50 cm square, would reach ~0.86 d.
  But then TOF and the SiPM × plastic coincidence must come from the plastic alone (ask).
- **To confirm before buying:** one Geant4 run with an oversized plate at 35 cm
  (`--big-plastic` was built for this; smaller plates are cut offline from the hits).

## 10. How much the target region widens the X17 peak (2026-10-09)

Code: `sim/lnl_scatter.py` → `out/scatter/` (figures `scatter_widen.png`, `scatter_budget.png`).
Deck slides 16–17 ("Scattering", "One week"). It is the LNL version of the n_TOF capsule
"dilution" figure (MX17_Full_Geant `docs/angular_resolution/figs/fig_theta_dilution.png`,
`fig_theta_money.png`).

The beam is in vacuum. The leptons cross the CFRP 0.4 mm chamber tube (r = 25 mm), not a
500 bar ³He capsule. Per event, Geant4 truth is compared with the reconstructed chord for the
same events (big plastics, MM 15° + TOF, E_sum 13–18):

| | X17 σ68 | X17 in 125–155° | counting days at 1 µA |
|---|---|---|---|
| no scattering (Geant4 truth) | 0 | 87 % | 0.90 |
| no chamber wall (Gaussian 3.5°, the appendix model floor) | 3.5° | 87 % | 1.08 |
| **CFRP 0.4 mm chamber (Geant4 reco, the baseline)** | **4.6°** | **85 %** | **1.20** |
| Al 0.5 mm chamber (Geant4 L5 residuals on the same events) | 9.0° | 74 % | 1.43 |
| Al 1.0 mm chamber (same) | 12.2° | 66 % | 1.60 |
| n_TOF-like 14.5° (Gaussian) | 14.5° | 63 % | 1.76 |

- 4.6° here against 5.1° in §5: same chamber, different selection. §5 is as built at MM 15°, no E_sum
  window; this table uses big plastics, MM 15° + TOF and E_sum 13–18, which keeps more symmetric pairs.
- **The CFRP wall costs ~11 % in time** (1.08 → 1.20 d). All the smearing together, against a
  perfect detector, costs ×1.34.
- **The peak halves in height** (11 → 5 %/°), but the X17 stays above its ~134° edge and inside the
  window.
- Even n_TOF-level smearing would cost only ×1.5 here. The edge sits where the IPC is already
  falling smoothly. At n_TOF it sits on the steep small-angle IPC.
- Layer budget (Highland at 8.6 MeV × lever (L − r)/L × k = 1.67, the appendix model):

  | layer | term |
  |---|---|
  | **chamber wall** | **3.8°** |
  | Al backing (backward leptons only) | 1.5° |
  | air | 1.4° |
  | MM window, cathode, gas | ≤ 0.1° each: they sit at the end of the lever |
  | n_TOF capsule wall, for scale | 11.8° |

- Caveats:
  - The no-wall and n_TOF rows are Gaussian illustrations.
  - The Al rows borrow residuals from the as-built L5 runs.
  - The IPC histograms are raw Geant4 MC (no KDE), so the best windows are noisy at the ±1 bin
    level.
  - A Geant4 run with no chamber wall would replace the model floor.

## 11. One week as measured, and what "significance" means here (2026-10-09)

Code: `sim/lnl_week.py` → `out/scatter/week.csv`, `week_z.csv`, figure `scatter_week.png`. It reads
`stacked.csv` (§10) and `reach_geant.csv`, so it needs no Geant4 tables. Deck slide 17 ("One week")
replaces the per-day stacked plots. The per-day plot could not show the bump: √B per 2° bin (~11)
is about the size of the X17 per bin.

**One week at 1 µA** (big plastics, MM 15° + TOF, E_sum 13–18, live 0.993):
- 750 X17 on 10,700 IPC pairs in 130–172°, so **S/B ≈ 7 %**.
- The measured X17 (CFRP chamber) is a 3–4σ excess per 4° bin at 130–146°.
- In one Poisson pseudo-experiment (seed 17) the counting Z is 7.7σ, against 7.3σ expected.
- The IPC expectation is the Geant4 reco histogram with the same 5° Gaussian smoothing as the
  reach templates (`KDE_BW_DEG`). The raw MC is noisier than a week of data.

**How the significance is computed.** Every figure is Asimov (expected) and statistical only, and
Z grows as √t.

| method | 3σ in | Z after 1 d | 3 d | 7 d |
|---|---|---|---|---|
| counting, S/√B in the best window (130–172°), IPC known exactly (the headline) | 1.2 d | 2.7 | 4.7 | 7.3 |
| template fit 90–180°, one IPC norm and γ₁ free | 1.6 d | 2.4 | 4.1 | 6.3 |
| template fit, M1, E1 and γ₁ norms each free | 3.7 d | 1.6 | 2.7 | 4.2 |
| counting with ε = 2 % on B in the window, Z = S/√(B + ε²B²) | 4.5 d (cap 3.5σ) | 2.2 | 2.8 | 3.2 |

- **The real limit is the IPC shape.** At S/B ≈ 7 %, an uncertainty ε on the IPC under the edge,
  relative to the sidebands, caps Z at S/(εB): 3.5σ for ε = 2 %, 1.4σ for 5 %. So the measurement needs the
  IPC angular shape to ~1 %. It has to come from the data (sidebands, E_sum slices, off-resonance
  points) and from an IPC calculation better than Born (M1–E1 interference, §8 item 4).
- The look-elsewhere effect for a scanned mass is not included.
- The headline "1.2 d" stays the counting number. Quote it with the 3.7 d of the free-mix fit and
  the shape caveat beside it.

**Plastic size (slides 13–14).** Slide 13 ("Configs") draws the as-built bars against the optimal plates, to scale, viewed along the beam and face-on. Slide 14 shows only the plastics where the bars are now
(fronts at R = 41 cm), with the SiPM wall kept in the leg for the TOF. The closer placements and
the no-SiPM-wall placement are dropped as impractical; their rows stay in `days_vs_size.csv`. The
curve's minimum is at 77.5 cm (1.19 d, 2.4 m² for four arms; just past the point where the plates
collide), and it is within 10 % of that from ~65 cm (1.7 m²).

## 12. Is the significance real? The background shape, the symmetric cut and the controls (2026-10-12)

Code: `sim/lnl_syst.py` → `out/syst/` (`atomki_repro.csv`, `ycut.csv`, `ladder.csv`, `delta_scan.csv`,
`spectra_10d.csv`, `summary.json`; figures `out/syst/figures/`). Deck slides 17–20 ("ATOMKI bump",
"Symmetric pairs", "Systematics", "Controls").

Dylan's question: the X17 peak can't be seen by eye, yet §0 claimed 3σ in a day. §11 already showed
that a 2 % IPC shape error caps counting at 3.5σ; this section asks what the cap is with a full shape
fit, and what the |y| cut and control samples buy. Were we assuming the
background is known perfectly? **Yes.** The §0 counting days are S/√B with B exact. The template fit
fixed the IPC shapes to Geant4. At S/B ≈ 7 % in the window, that assumption carries the whole result.

### 12.1 Why the peak is invisible: S/B ≈ 7 %

Big plastics, per day in the best window: 134 X17 against 1930 background (S/B 0.07). As built:
8.9 against 141 (0.06). A 3σ excess at that S/B is ~1σ per bin. Scattering is not the cause: at
Geant4 truth (no scattering at all) the best 2° bin has S/B 0.24 and the rest 0.05–0.10 (§10). The
small S/B comes from R = 5.8×10⁻⁶ against our IPC model.

A uniform fractional error δ on B caps the counting significance at Z_max = (S/B)/δ, at any running
time. All pairs, big plastics: δ = 2 % gives Z_max = 3.5.

### 12.2 What ATOMKI plot, and why their bump shows

- **Not raw counts, not background-subtracted.** These are acceptance-corrected angular correlations:
  - the acceptance comes from event-mixed singles;
  - in 2022 the cosmic background is subtracted first (Sas *et al.*, arXiv:2205.07744);
  - the y axis is log.

  The IPC is a simulated M1 + E1 curve fitted below ~110°, and the anomaly is defined as data minus
  that curve. **Their 6.8σ also assumes the IPC shape.** Their E1 share at 1.10 MeV went from 23 %
  (2016) to ≳ 50 % (2022).
- **Same scattering as ours:** a carbon-fibre tube chamber, 300 µg/cm² Li₂O on 10 µm Al, and MWPC or
  DSSD positions.
- **The bump is small.** Fig. 4 of PRL 116 042501, digitised at 300 dpi (±3 %): the data sit
  **+26 %, +35 % and +21 %** above the no-boson curve at 135°, 145° and 155°. That is S/B ≈ 0.3, not a
  peak. It reads as a bump because of 10° bins with ~3 % errors.
- **Truth-level reproduction** (Born IPC + X17 from rest, 2×10⁶ each, acceptance-corrected, both
  leptons > 2 MeV): the excess at 135° / 145° is

  | case | 135° | 145° |
  |---|---|---|
  | ATOMKI as published: M1 + 23 % E1, \|y\| ≤ 0.5, σ 3° | +21 % | +17 % |
  | … σ 6° | +16 % | +18 % |
  | … no \|y\| cut | +11 % | +9 % |
  | our mix: 52 % E1 (direct capture), \|y\| ≤ 0.5 | +13 % | +10 % |
  | our mix, no \|y\| cut, σ 5° (≈ our Geant4 selection) | +6 % | +6 % |
  | pure M1, \|y\| ≤ 0.5 | +46 % | +43 % |

  The gap between our ~6 % and their ~30 % breaks down as follows:
  - **×2 from the |y| cut;**
  - **×1.7 from the E1 share** (23 % against our 52 %);
  - **×~2 left over:** in our generator, their figure needs R ≈ 1.2×10⁻⁵ with their stated cuts
    and mix.

  The leftover factor could come from their efficiency against lepton energy, the definition of the
  E1 share, or the 3.9×10⁻³ IPC coefficient. **Our R = 5.8×10⁻⁶ is the conservative end.** If the
  bump in their figure is real, our signal is up to ×2 larger.
- Our signal counts the resonance and direct capture with the same R (the `(1 − f17)` factor). That
  matches how R was extracted at 1.10 MeV, and ATOMKI 2022's picture (X17 from direct capture). If
  the X17 came from the 1⁺ resonance alone, the signal would be ×2 lower.

### 12.3 The symmetric-pair cut

|y| = |E₁ − E₂| / (E₁ + E₂) from the two measured arm energies; no charge sign needed. In 130–160°:

- 99 % of the X17 have measured |y| < 0.5 (truth 100 %);
- ~60 % of the M1 IPC and ~77 % of the E1 IPC have |y| < 0.5.

| big plastics | X17 kept | background kept | best window | S/B there | counting days |
|---|---|---|---|---|---|
| all pairs | 100 % | 100 % | 130–172° | 7 % | 1.20 |
| \|y\| < 0.5 | 99 % | 74 % | 130–164° | 10 % | 0.92 |
| **\|y\| < 0.3** | **69 %** | **42 %** | **130–146°** | **18 %** | **0.79** |
| \|y\| < 0.2 | 45 % | 27 % | 130–142° | 22 % | 1.01 |

As built the S/B values are the same within ±1 %. The statistics barely move (S/√B ×1.2), but **S/B
goes ×2.6, and S/B is what a shape systematic eats.** The best window shrinks to the edge: symmetric
X17 pairs sit at the minimum opening angle.

### 12.4 The fit with shape nuisances

The fit is an Asimov/Fisher fit on 2° bins over 90–180°, with a background-only expectation. σ(R)
comes from the inverse Fisher matrix with the priors added. Live time enters the data term only, so
the priors set a ceiling. The freedoms, added row by row:

- **M1, E1 and γ₁ normalisations free.** EPC is tied to M1; cosmics are fixed (≤ 1/day).
- **Calibrated detector:**
  - angular-resolution scale ±10 % (Geant4 reco − truth residuals scaled by 1 + k);
  - E_sum scale ±2 %;
  - multiplicative acceptance 1 + Σ aₙ Pₙ(x), n = 1–3, at ±2 % each, or free.
- **Unknown structure δ:** a Gaussian process on the background shape, with relative amplitude δ and
  correlation length ℓ = 10° (≈ the X17 peak width). It stands for detector effects and contributions
  nobody has thought of. Polynomials and scales alone never cap Z, because the signal-free bins pin
  them. Structure at the scale of the peak does.
- **Controls:**
  - The **in-run controls** are the asymmetric pairs (|y| ≥ 0.3; ATOMKI's own null) and the γ₁ E_sum
    side band (9–13 MeV) of the same run. They share the detector nuisances, the 2 % structure and
    the M1/E1/γ₁ normalisations. Each also gets 1 % structure of its own (the transfer error) and
    ±5 % normalisation (the MC category split).
  - The **441 keV run** is ¼ of the time on the 17.64 MeV resonance, with no X17 assumed. ATOMKI
    2016 saw none there; 2022 saw "much smaller". It is counted in the beam days.

Days to 3σ at R(ATOMKI), 1 µA, MM 15° + TOF, m = 16.7 (`out/syst/ladder.csv`). The significance after
30 days is in parentheses.

| fit assumption | as built, all | as built, \|y\| < 0.3 | big pl., all | big pl., \|y\| < 0.3 |
|---|---|---|---|---|
| counting, B exact (old headline) | 16 (4.2σ) | 15 (4.3σ) | 1.2 (15σ) | 0.8 (18σ) |
| fit, IPC shape exact | 24 | 16 | 1.6 | 1.1 |
| + M1, E1, γ₁ free | 72 | 20 | 3.7 | 1.2 |
| + calibrated detector (±2 % acceptance) | 145 | 22 | 4.2 | 1.2 |
| + acceptance cubic free | 346 | 60 | 10 | 1.8 |
| + 1 % unknown structure | 548 | 63 | 13 | 1.9 |
| + 2 % unknown structure | 1515 (0.9σ) | 76 (2.2σ) | 26 (3.1σ) | 2.0 (8.6σ) |
| … 2 % at ℓ = 5° (edge-like) | 7208 | 82 | 423 | 2.1 |
| **2 % + in-run controls** | 370 (1.5σ) | **20 (3.6σ)** | 5.7 (5.0σ) | **1.1 (11.8σ)** |
| … + 441 keV run (¼ time) | 246 | 25 | 6.4 | 1.4 |

Scan in δ, signal run only → + in-run controls with δ/2 transfer (`out/syst/delta_scan.csv`):

| δ | big pl. all | big pl. \|y\| < 0.3 | as built all | as built \|y\| < 0.3 |
|---|---|---|---|---|
| 0.5 % | 11 → 3.7 d | 1.9 → 1.1 | 385 → 80 | 61 → 18 |
| 1 % | 13 → 4.1 | 1.9 → 1.1 | 548 → 118 | 63 → 18 |
| 2 % | 26 → 5.7 | 2.0 → 1.1 | 1515 → 369 | 76 → 20 |
| 3 % | 53 → 8.8 | 2.2 → 1.2 | 2575 → 980 | 111 → 22 |
| 5 % | 126 → 26 | 3.0 → 1.4 | 4933 → 2447 | 561 → 27 |

What it means:

- **All pairs, the old selection, is limited by how well the IPC shape is known.**
  - With big plastics, a free acceptance shape costs ×8 and 2 % of unknown structure ×20.
  - As built, it becomes years.
  - Without the symmetric cut, the §0 headline does not survive a realistic shape uncertainty.
- **With |y| < 0.3 the result is robust.**
  - Big plastics stay at 1–2 days whatever the fit is allowed.
  - As built needs the in-run controls and then takes ~20 days (indicative: see the caveats below).
- **The in-run controls do most of the work, and they come free with the run.**
  - The 441 keV run adds little shape information.
  - Its value is as a physics null.
  - **0.80 MeV is not a null:** ATOMKI 2022 claim the X17 in direct capture.
- **New headline (2 % unknown structure, |y| < 0.3, in-run controls):**
  - **~1.1 d with big plastics, ~20 d as built.**
  - The 3σ reach in 30 days: R = 1.5×10⁻⁶ with big plastics (×4 below ATOMKI) and 4.8×10⁻⁶ as built.

### 12.5 Caveats

- **IPC MC statistics.** In 130–160° at |y| < 0.3 there are ~170 M1 and ~1400 E1 IPC events for big
  plastics, and **12 M1 and 112 E1 as built**. The templates are KDE-smoothed (5°), which is a smooth
  guess. MC noise alone is ~3–5 % per bin, the same size as the δ scanned. The as-built |y| < 0.3
  column is indicative until the L2 IPC runs are ×10–100 larger.
- The Gaussian-process δ and ℓ are a model of ignorance, not a measurement. ℓ = 5° (edge-like) is
  the dangerous case for all pairs (423 d) and harmless at |y| < 0.3 (2.1 d).
- The controls are assumed to share the detector structure exactly, up to their own δ/2 or 1 %
  transfer. Asymmetric pairs have a softer lepton, which scatters more and sits closer to threshold.
  The transfer error is the number to measure: event mixing, the 441 keV run, and the 6.05 MeV E0
  line (not visible to the trigger, §6).
- An unexpected *physics* source of symmetric 18 MeV pairs at ~140° is, by construction, the signal.
  No control removes it. The mass dependence (§0) and the E_p scan are the handles.
- The as-published ATOMKI E1 share and our generator disagree by ×2 on the visible excess (§12.2).
  The signal normalisation is uncertain by up to ×2 (upward).

### 12.6 Next

1. **L2 IPC ×20** (M1 and E1 at 18.15 and 17.64, both hardware configs) on lxplus. This is the
   template statistics the shape analysis needs.
2. **Event-mixing acceptance** in the Geant4 tables: pair singles from different events, and check
   that it reproduces the IPC acceptance against θ to ≲ 2 %.
3. A Zhang–Miller (M1–E1 interference) IPC shape as an alternative template. Its difference from Born
   is a direct measure of δ.
4. Add |y| < 0.3 to the reference selection in `lnl_geant.py` and in the run animation.

## 13. The second pass: L7 statistics, γ* anisotropy, event mixing, and the pair mass (2026-10-12)

Code:
- `sim/lnl_syst.py`: `use_var('theta' | 'mass')`, the anisotropy, L7 templates;
- `sim/lnl_mixing.py`;
- `viz/export_anim_data.py`.

Outputs: `out/syst/` (`ladder_mass.csv`, `delta_scan_mass.csv`, `spectra_10d_mass.csv`, `aniso.csv`,
`y_theta_map.csv`, `y_window.csv`, `y_scan.csv`) and `out/mixing/`. Deck slides 18–24: ATOMKI bump,
Symmetric pairs, **Why |y|**, **Mass fit**, Systematics, Controls, **Checks**. The animation has three
views: angle, angle |y| < 0.3, and pair mass.

### 13.1 L7: IPC generated above 70°

The Born IPC generator has a new option, `--ipc-min-open <deg>` (MX17_Full_Geant `lnl` bc4cd6c). It
rejects pairs on the lab opening angle, which gives exactly the Born distribution conditioned on
θ > 70°. Normalisation: × the Born fraction above 70° (M1 0.154, E1 0.240; `lnl_rates.ipc_vectors`).

- Runs, 10⁵ events per job (172 condor jobs, ~0.9 TB on EOS):
  - M1 18.15: 31 jobs;
  - E1 18.15: 24 jobs;
  - M1 17.64: 31 jobs;
  - each as built and with big plastics.
- Above 90° that is ×20 (M1) and ×10 (E1) the L2 statistics.
- The merge now keeps the truth lepton momenta (`em_p`, `ep_p`).
- **Check against L2, accepted fraction above 90°:**
  - trigger level: 0.98–0.99 (±0.01–0.05);
  - MM 15° + TOF: 0.95–0.96. That is because the L2 E1 tables have no arm times, so the TOF cut never
    applied to them; L7 has times for every sample.
- The real L7 deficit is pairs with true θ < 70° that reconstruct above 90°: 0.3–1.4 % in L2, and
  ≤ 0.8 % in 130–160°.

### 13.2 The γ* anisotropy about the beam

⁷Li(p,γ₀) photons are not isotropic: W(θ_k) = 1 + a₁P₁ + a₂P₂.
- **a₁:** Zahnow 1995 (EXFOR A0639 subentry 3) has σ(0°)/σ(150°) = 7.6 ± 1.3 at 1100 keV, so a₁ ≈ 1.0.
  This is the E1–M1 interference.
- **a₂:** Hayes, Friar, Hale, Garvey (arXiv:2106.06834) give 4πσ(90°)/σ_int = 1 − a₂/2 = 0.82 from
  their R-matrix fit, so a₂ = 0.36. The physical range is 0–0.5; 0.5 is pure ³P₁ M1.

Each γ₀ IPC event is weighted by W, using its true γ* direction.

- **P₁ cancels.** The arms are symmetric about 90° to the beam: ⟨P₁⟩ = −0.03 to +0.01 in every
  selection. That is Hayes et al.'s point about interference.
- **P₂ does not.** ⟨P₂⟩ is −0.25 to −0.42 in the side bands and −0.04 to +0.03 in the window. With
  a₂ = 0.36 the IPC rises in the window relative to the side band by:

  | | M1 | E1 |
  |---|---|---|
  | θ, all pairs (big plastics) | +3 % | +6 % |
  | θ, \|y\| < 0.3 | +10 % | +10 % |
  | m_ee | +8 % | +9 % |

- In the fit, a₁ ± 0.3 and a₂ ± 0.15 per run. This costs ×1.2 (big plastics, θ) and ×3 (as built, θ,
  all pairs). In m_ee it costs 5 %.
- *Bug found and fixed on the way:* the first anisotropy run used `lnl_geant.kde_hist`. That function
  drops negative-weight bins, so the P₁ and P₂ derivative templates were half missing. The local `kde()`
  keeps them.
- Not modelled: a different anisotropy for the virtual photon than for the real one, any anisotropy
  of the γ₁ IPC, and the X17's own angular distribution.

### 13.3 Event mixing: can the acceptance against θ come from data?

The true pair acceptance is compared with mixed pairs at two-arm trigger level (no E_sum, no
pointing), on L7 (`out/mixing/mixing_summary.csv`, ratio normalised over 125–175°, 5° bins). Two ways
to mix:
- **singles:** one-arm hits from the 8Be γ-line runs (L3). These stand in for a prescaled single-arm
  trigger.
- **pair legs:** legs of selected pairs, swapped between events of the same arm pair.

| big plastics | rms deviation | after a free cubic | MC stat./bin |
|---|---|---|---|
| M1 18.15, singles | 19 % | **1.2 %** (χ² 4/6) | 1.7 % |
| M1 18.15, pair legs | 8.9 % | 2.7 % (11/6) | 2.1 % |
| E1 18.15, singles | 4.7 % | **1.2 %** (11/6) | 1.2 % |
| E1 18.15, pair legs | 7.8 % | 1.4 % (10/6) | 1.2 % |
| M1 18.15 \|y\| < 0.3, singles | 6.1 % | 2.6 % (6/6) | 4.2 % |

- **Mixing gets the smooth tilt wrong,** by up to ~20 % across 125–175° for M1. The soft lepton's
  efficiency depends on its energy, and M1 pairs at large angles are lopsided. Mixing cannot see that.
- **After a free cubic, which the fit floats anyway,** singles mixing matches the true acceptance to
  1.2–1.7 % per 5° bin. That is at the MC statistics and at the δ the fit allows.
- **Pair legs are worse** (1.4–4.7 %): requiring the partner biases them.
- **So a prescaled single-arm trigger** (as in the ILL §14 study) gives the local acceptance structure
  from data. The smooth part floats in the fit, and the energy-dependent efficiency comes from MC and
  the 441 keV check.
- As built, the statistics limit the test to 2–4 %.

### 13.4 Why the |y| cut works, and where the statistics go

Slide "Why |y|"; `y_scan.csv`, big plastics:

| keep \|y\| below | X17 / day (130–160°) | background / day | statistics-only days | 2 % shape | + controls |
|---|---|---|---|---|---|
| 0.2 | 44 | 338 | 0.95 | 3.4 | 1.2 |
| **0.3** | **69** | **519** | **0.76** | **4.3** | **1.2** |
| 0.4 | 91 | 713 | 0.75 | 5.9 | 1.9 |
| 0.5 | 98 | 896 | 0.83 | 10.2 | 3.2 |
| none | 99 | 1197 | 1.07 | 13.8 | 6.1 |

- The X17 at its edge angle shares its energy equally. In (θ, |y|) it lies on the line of constant
  pair mass, |y| = √(1 − 2m²/(W²(1 − cos θ))). That line climbs from 0 at 134° to ~0.45 at 180°.
- The IPC at 140° fills all |y|.
- Statistics alone barely care about the cut between 0.3 and 0.5. S/B is what a shape error eats.
- The cut is **offline**. The trigger is unchanged, and E₁, E₂ are recorded for every pair. The
  rejected pairs become the control sample.
- It must be fixed blind: on Monte Carlo, at 441 keV, or on the asymmetric pairs.

### 13.5 The pair mass

m_ee² = W²(1 − y²)(1 − cos θ)/2, with W = 18.15 MeV. Direct capture at 1.10 MeV has W = 18.22 MeV, a
0.4 % shift. The variable uses the reconstructed θ and the measured y.

- The X17 (m = 16.7) reconstructs at 16.6 MeV with FWHM ≈ 0.6 MeV.
- The best counting window is 16.0–17.0 MeV. It keeps 96 % of the X17 at S/B ≈ 17 %, with no |y|
  cut.
- The fit uses 0.25 MeV bins over 8–20 MeV, KDE 0.27 MeV, and GP ℓ scaled to 0.55 MeV (= 10° at the
  edge).
- The γ₁ IPC sits below 15 MeV; the γ₁ E_sum side band is the in-run control.
- The full ladder (`ladder_mass.csv`) barely moves:
  - big plastics: 0.52 d (statistics only) → 0.93 d (2 % structure) → 0.83 d (with controls);
  - as built: 5.8 → 9.4 → 8.0 d.
- The 3σ reach in 30 days: R = 1.5×10⁻⁶ with big plastics (×4 below ATOMKI) and 3.4×10⁻⁶ as built
  (×1.7 below).
- **As built, the IPC has a broad hump at 16.5–17.5 MeV in m_ee**, right under the signal
  (`figures/syst_mass.png`). It comes from the back-to-back arm geometry: the accepted E1 IPC hump at
  140–170° (§7). The Monte Carlo template carries it, so the fit models it, but the as-built result
  leans on that template being right there. With big plastics the IPC falls smoothly through
  16–17 MeV.
- New sensitivity: the **arm-to-arm energy calibration**, because it moves y. dm/m = −y dy/(1 − y²), so
  it is small for symmetric pairs. It is not in the fit yet. Calibrate on the 441 keV pairs and on
  cosmics.

### 13.6 Next

1. A per-arm gain nuisance in the m_ee fit, and the arm-calibration plan (441 keV, cosmic MIPs).
2. Make the m_ee fit the reference analysis in `lnl_geant.py`. The days in `reach_geant.csv` and on
   the reach slide are still θ counting.
3. Re-merge L2 E1 with the arm times, or drop L2 for the IPC now that L7 exists.
4. Scan the mass hypothesis (16.6–17.0) in m_ee, with the look-elsewhere effect.
5. Ask: can the n_TOF DAQ take a prescaled single-arm trigger (for the event-mixing acceptance)?

## 14. Single-arm triggers, realistic calorimetry, and fits in two and three variables (2026-10-12)

Three questions from Dylan:
1. From now on, take every single-arm trigger, with a prescale always available. Design for it.
2. What calorimetry can we really expect, given what n_TOF measured?
3. Do the energy variables give a 2D (or 3D) fit with more discovery power, and in particular more
   robustness against an imprecise background spectrum?

Code:
- `sim/lnl_trigger.py` → `out/trigger/`;
- `sim/lnl_calo.py` (the response; the per-arm gain nuisance is in `lnl_syst.py`, `PRIOR_G`) →
  `out/calo/`;
- `sim/lnl_nd.py` → `out/nd/`;
- deck slides "Trigger", "Calorimetry", "2D fit" (`deck/calo_slides.py`).

New tables: `$E/sel_v3/` (EOS, condor re-merge 2026-10-12) keep each arm's SiPM, plastic and liquid
energies separately (`E_sipm_a`, `E_plast_a`, `E_ls_a`; `sg_E_*` for singles). Run everything with
`LNL_SEL=lnl/sim/sel_v3`; it is a superset of `sel` + `sel_v2` (L1–L4, L7).

### 14.1 The trigger: every single arm, with a prescale

Logic (two outputs ORed into DREAM, plus a 1 Hz clock for pedestals):
- **PAIR:** ≥ 2 arm legs within 20 ns. **Never prescaled.**
- **SINGLE:** ≥ 1 arm leg (SiPM bar AND plastic ≥ 0.5 MIP), prescaled 1/P. P = 1 (take everything) when
  the rate allows.
- Every event carries the trigger word: which legs fired, which output, and the prescale counter. The
  single-arm sample is then exactly normalised for any P. P is a run-condition parameter, not a
  firmware constant.

DREAM RAW (20 samples) is busy τ = 298 µs per event, non-paralysable. Live = 1/(1 + fτ) applies to both
outputs, so the pairs pay for the singles only through the live time (`prescale_choice.csv`; Li₂O
300 µg/cm² at 1.04 MeV, Geant4 8Be γ + cosmics):

| | arm legs /s | pairs /s | live at P = 1 | P for 95 % | P for 98 % |
|---|---|---|---|---|---|
| as built, 1 µA | 58 | 3.5 | 98.4 % | 1 | 1 |
| as built, 4 µA | 125 | 3.6 | 96.5 % | 1 | 2 |
| big plastics, 1 µA | 153 | 22 | 96.2 % | 1 | 5 |
| big plastics, 4 µA | 347 | 23 | 91.2 % | 2 | 10 |
| big plastics, 8 µA | 607 | 24 | 85.2 % | 5 | 20 |

(The thick "LNL 2023-24" target is ~1.5× these rates.)
- **P = 1 up to 2–4 µA.** Above that, P = 2–10 keeps 95 %.
- **Data:** 0.12 (as built) to 0.28 (big plastics) TB/day per FEU at 1 µA and P = 1.
- **What the singles buy:**
  - **Per-arm gain from cosmic MIPs.** Even at P = 10 that is ~1100 (as built) to ~3600 (big plastics)
    MIPs per arm per hour, so the MIP peak to ~1 % per hour. That is what makes σ_g = 1–2 % (§14.2)
    cheap.
  - The event-mixing acceptance (§13.3).
  - Per-arm efficiency maps, and the 8Be γ single-arm spectra as a high-energy check of the scale.
- Not included: ¹⁹F(p,αγ) 6–7 MeV γs on a LiF target or as contamination (ask). They could dominate the
  singles; the prescale is there for that.
- §13.6 item 5 ("can the DAQ take a prescaled single-arm trigger?") is answered: yes, and at LNL rates it
  can take all of them.

### 14.2 Calorimetry: the n_TOF response folded into the LNL tables

Until now every LNL energy was a Geant4 deposit. `lnl_calo.py` applies a per-arm, per-layer response,
E(1 + c·N) + a√E·N′, set to 0 below threshold. The parameters are anchored on the n_TOF measurements
(`nTof_x17/ntof_calorimetry` C1, C4; the scint-stack per-cell maps):

| layer | n_TOF measurement | model "n_TOF as is" | model "LNL calibrated" |
|---|---|---|---|
| plastic 2 cm | cosmic MIP Gauss σ/MPV 0.13–0.24 per bar; per-cell medians spread 4–5 % (A, C, D), 9.5 % (B); scale known to ~10 % (MIP vs source line 3–24 % apart) | a = 0.32 √MeV, c = 5 % | a = 0.32, c = 2 % (MM-position map) |
| SiPM wall 3 mm | MIP ~0.6 MeV; groups up to 35 % low before correction; run-to-run 2–2.5 % | a = 0.19, c = 8 % | a = 0.19, c = 4 % |
| liquid (as built) | MIP σ/MPV 0.46; 6–9 mV/MeV vs a 16–18 mV ZS (1.8–2.8 MeV threshold); MIP efficiency 14–56 %, position-dependent | thr 2.3 MeV, a = 0.78, log-normal light collection σ = 0.5 | "repaired": thr 0.5 MeV, a = 0.5, c = 15 % |
| big plates 5 cm | no data | a = 0.25, c = 10 % | a = 0.20, c = 5 % ("poor": a = 0.35, c = 15 %) |
| per-arm gain prior in the fit | | σ_g = 10 % | σ_g = 2 % (single-arm cosmics; poor plates 5 %) |

The E_sum window is re-optimised for each response (on the robust m_ee days); the §13 windows were tuned
on ideal deposits. The per-arm gain enters the fit as four nuisances (`lnl_syst.PRIOR_G`; the arms of
E₁, E₂ are `a1`, `a2`), which move y, m_ee and E_sum together.

Robust days to 3σ at R(ATOMKI), 1 µA (2 % structure + in-run controls, gain nuisance; `days.csv`,
`resolution.csv`):

| | E_sum window | σ₆₈(m_ee) X17 | corr(y, y_true) | γ₁/γ₀ E_sum separation | **m_ee fit** | θ fit, \|y\| < 0.3 |
|---|---|---|---|---|---|---|
| big plastics, ideal | 13–17 | 0.35 MeV | 0.91 | 1.6σ | **0.83** | 1.2 |
| big plastics, LNL calibrated | 14–19 | 0.40 | 0.86 | 1.2σ | **1.4** | 1.7 |
| big plastics, n_TOF as is | 14–19 | 0.48 | 0.78 | 1.0σ | **2.4** | 3.4 |
| big plastics, poor plates | 14–22 | 0.60 | 0.67 | 0.8σ | **5.0** | 4.0 |
| as built, ideal | 13–17 | 0.33 | 0.88 | 0.85σ | **8.0** | 17 |
| as built, LNL calibrated (LS repaired) | 13–19 | 0.59 | 0.67 | 0.62σ | **35** | 56 |
| as built, n_TOF as is | 13–22 | 0.81 | 0.52 | 0.40σ | **190** | 124 |
| as built, LS off | 13–20 | 0.53 | 0.45 | 0.0σ | **490** | 390 |

- **Big plastics survive a realistic response:** ×1.7 with a calibrated detector, ×3 with n_TOF-quality
  calibration, ×6 with poor plates. 5 cm stops the soft lepton and takes most of the hard one, so y and
  E_sum stay meaningful. The m_ee peak widens from 0.35 to 0.40 MeV.
- **As built does not.** The ideal 8 d becomes 35 d even with a repaired liquid, ~190 d with the
  liquid as it was at n_TOF, and ~490 d without it. 2 cm of plastic stops neither lepton: both legs leave
  ~4 MeV, so without the liquid γ₀ and γ₁ pairs have the same E_sum (separation 0.0σ) and y is mostly
  noise.
- **Where the as-built loss comes from** (`ls_scan.csv`, calibrated response, m_ee fit):

  | liquid | plastic + SiPM | m_ee robust days |
  |---|---|---|
  | ideal | real | 23 |
  | repaired, a = 0.5 √MeV, c = 15 % | ideal | 18 |
  | a = 0.2, c = 5 % | real | 31 |
  | a = 0.3, c = 10 % | real | 32 |
  | a = 0.5, c = 15 % (the reference) | real | 35 |

  - The 2 cm bars' photostatistics (~10 pe/MeV, a ≈ 0.32) cost about ×2–3 on their own.
  - A better liquid buys little while the bars stay as they are.
  - **As built has a floor of ~3 weeks** even with a perfect liquid. That makes the big plastics the
    calorimeter, not an option.
- **The per-arm gain is not the problem** (`calo_gain.png`): σ_g from 0 to 20 % costs ×1.17 for big
  plastics and ×1.25 as built (m_ee). The free M1/E1 norms and the controls absorb most of it, and the
  single-arm cosmics give σ_g ≈ 1–2 % anyway.
- Not modelled:
  - Birks quenching of stopping electrons (a few %);
  - the SiPM-wall leg efficiency, 75–91 % unbiased at n_TOF. If it stays there, ×1.2–1.8 in days;
  - plastic non-linearity above 5 MeV. n_TOF checked linearity only to 1.45 MIP, and the 5 cm plates
    see up to ~12 MeV.

**Do we need more n_TOF analysis first? No, with one small exception.** n_TOF has given what it can:
- the plastic MIP scale (C1);
- the liquid diagnosis (C4: threshold-limited, the signal never recorded);
- the per-cell face maps;
- the upstream-loss response (C2).

C3 has already shown that the n_TOF data hold no more energy information. The open numbers are not in
those data:
1. **The 5 cm plate response** (light yield, non-uniformity, linearity to 12 MeV). It sets
   1.4 d vs 5 d. Bench test: one plate with its PMTs on cosmics, plus a Sr-90/Bi-207 source and a
   position scan.
2. **Whether an LS cell can reach a ≲ 0.3 √MeV resolution** with a low threshold. This decides whether
   as built is worth taking at all. Bench test on cosmics.
3. **Linearity of electrons at 5–15 MeV.** No source covers it. In situ: the 8Be γ single-arm spectra
   (§14.1).

The exception is a cheap check on the n_TOF data: split the 2 cm bars' 19 % MIP width into
photostatistics and path/Landau-model terms, using the PMT charge of through-going cosmics at fixed
path. That would refine a = 0.32, which drives the as-built loss.

### 14.3 Fits in two and three kinematic variables

**The question.** Does adding the energies as fit axes, not just as cuts, give more discovery power? In
particular, does it make the result less sensitive to how well we know the background spectrum?

**The method** (`lnl_nd.py`). §12–13 put the "unknown structure" on the fitted variable itself, so a θ
fit and an m_ee fit were never tested against the *same* background error. Here the structure is a
weight 1 + Σ c_j φ_j on every background event. The φ_j are Gaussian-process modes in physical
variables:
- **S_θ:** in the reconstructed angle, the same at every |y| and E_sum (acceptance, geometry, material);
- **S_m:** in m_ee, the §13 assumption;
- **S_θy:** local in (θ, |y|), a background-physics shape error;
- **S_θE:** local in (θ, E_sum), response and γ₁ leakage.

The lengths are ℓ = 10° (0.55 MeV; 0.15 in |y|; 2 MeV in E_sum). The stress tests use 5 % amplitude and
ℓ/2 (edge-like).

Every analysis sees the same structure through its own binning. Every fit floats:
- the M1, E1, γ₁ norms;
- the anisotropy (a₁, a₂);
- the resolution and E scales;
- a **free** acceptance cubic in θ and a |y| tilt (±5 %);
- the four arm gains and the |y| resolution.

The axes are θ (2°) or m_ee (0.25 MeV), KDE-smoothed; |y| in 6 bins; E_sum in 4 bins (two in the γ₁ side
band, two in the window). Cross-check against `lnl_syst`: θ, |y| < 0.3 gives 4.07 d against 4.05 d.

Days to 3σ at R(ATOMKI), 1 µA, **calibrated response** (`out/nd/nd_days_*.csv`). The columns are the
structure:

| big plastics | none | S_θ 2 % | S_m 2 % | S_θ 2 % + S_θy 1 % | S_θ 5 % ℓ/2 | S_m 5 % ℓ/2 | S_θy 5 % ℓ/2 |
|---|---|---|---|---|---|---|---|
| θ | 26 | 28 | 26 | 29 | 120 | 29 | 40 |
| θ, \|y\| < 0.3 | 7.3 | 7.5 | 7.4 | 7.5 | 9.7 | 8.1 | 8.4 |
| m_ee | 1.7 | 1.7 | 1.9 | 1.7 | 1.9 | 3.1 | 2.0 |
| θ × \|y\| | 1.2 | 1.2 | 1.3 | 1.2 | 1.3 | 1.6 | 1.4 |
| m_ee × \|y\| | 1.04 | 1.07 | 1.10 | 1.07 | 1.16 | 1.36 | 1.17 |
| m_ee × E_sum | 1.10 | 1.15 | 1.23 | 1.16 | 1.28 | 1.49 | 1.28 |
| **θ × \|y\| × E_sum** | **0.99** | 0.99 | 1.04 | **1.00** | 1.03 | 1.16 | 1.09 |

| as built (liquid repaired) | none | S_θ 2 % | S_m 2 % | S_θ 2 % + S_θy 1 % | S_θ 5 % ℓ/2 | S_m 5 % ℓ/2 | S_θy 5 % ℓ/2 |
|---|---|---|---|---|---|---|---|
| θ | 695 | 1128 | 716 | 1187 | 5289 | 915 | 2742 |
| θ, \|y\| < 0.3 | 126 | 147 | 139 | 151 | 827 | 261 | 271 |
| m_ee | 38 | 40 | 53 | 41 | 50 | 529 | 59 |
| θ × \|y\| | 24 | 24 | 27 | 25 | 25 | 40 | 30 |
| m_ee × \|y\| | 20 | 21 | 23 | 22 | 23 | 35 | 26 |
| m_ee × E_sum | 21 | 23 | 26 | 23 | 26 | 31 | 27 |
| **θ × \|y\| × E_sum** | **16** | 17 | 18 | **17** | 18 | 21 | 20 |

With ideal Geant4 energies the same 3D fit gives 0.68 d (big plastics) and 7.5 d (as built); m_ee
alone gives 0.98 and 10 d.

- **Yes: more discovery power, once the energies are realistic.** With the calibrated response:
  - big plastics: m_ee 1.7 d → m_ee × |y| 1.07 → θ × |y| × E_sum **1.0 d** (×1.7);
  - as built: 41 → 22 → **17 d** (×2.4).

  The y resolution smears m_ee (m_ee folds θ and y into one number). A fit that keeps them apart does
  not lose the information. With ideal energies the gain is smaller (×1.4), because m_ee was then
  nearly sufficient (the 2026-10-12 handoff: m_ee × |y| ≈ m_ee).
- **Yes: robust where the 1D fits are not.** Under the worst structure tried, each fit's days are:

  | fit | big plastics | as built |
  |---|---|---|
  | m_ee alone (S_m 5 % ℓ/2) | 3.1 | 529 |
  | 3D | 1.2 | 21 |
  | θ alone (S_θ 5 % ℓ/2) | 120 | 5000+ |

  The geometry is why. At fixed E_sum the X17 is a curve θ_X(|y|) in the (θ, |y|) plane.
  - Acceptance structure is a vertical band;
  - a γ₁ leak is a band in E_sum;
  - an m_ee shape error is a diagonal.

  The fit separates them, and the signal-free regions of the plane measure each one.
- **The 2D and 3D results are stable against the Monte Carlo.** Templates built from the two random
  halves of the MC agree to ≲ 10 % (`half_a`, `half_b`). The angle-only fits swing ×2–3 between halves
  (θ, |y| < 0.3 big plastics ideal: 1.9 vs 6.0 d): they are near-degenerate with the free acceptance
  cubic. As built, m_ee alone also swings (56 vs 40 d).
- **Nothing new to record:** θ, E₁, E₂ are in every pair event already. The E_sum axis replaces the
  γ₁ side-band cut and the in-run control. The |y| axis replaces the |y| cut and keeps the asymmetric
  pairs as the control inside one fit.
- **Recommendation:** make **θ × |y| × E_sum** (or m_ee × |y| × E_sum, which is equivalent) the reference
  analysis. Quote m_ee alone as the cross-check that a reader can see as a peak.

### 14.4 What changed in the headline, and next

The deck cover and record now quote the realistic-calorimetry 3D fit (calibrated response,
S_θ 2 % + S_θy 1 %):
- **big plastics ~1.0 d**: 3σ reach in 30 days R = 1.1×10⁻⁶, ×5 below ATOMKI;
- **as built ~17 d, only with a repaired liquid**: R = 4.4×10⁻⁶, ×1.3 below ATOMKI.

R₃σ(30 d) ≈ R(ATOMKI) √(d/30). The §13 numbers (0.83 / 8.0 d) were for ideal energies.

Next:
1. **Bench-test a 5 cm plate** (light yield, uniformity with an MM-position map, linearity to 12 MeV).
   It is the single number between 1 d and 2–5 d.
2. **Decide on as built:** it needs a liquid repaired to a ≲ 0.5 √MeV resolution with a 0.5 MeV
   threshold, and still gives ~3 weeks. Alternatively, drop it for the big plastics.
3. ~~Make the 3D fit the reference in `lnl_geant.py` / `reach_geant.csv`~~ (done 2026-10-13, §14.5). Still to
   do: add the 441 keV run and the mass scan (look-elsewhere) to `lnl_nd.py`.
4. **More IPC MC for as built.** The as-built 1D fits are MC-limited; the 3D fit is stable, but at ±10 %.
5. **Fluorine singles** on LiF (ask): they set the prescale.
6. The cheap n_TOF check of §14.2: the 2 cm bar photostatistics vs path terms.

### 14.5 The 3D fit is the reference in `reach_geant.csv` (2026-10-13)

`lnl_geant.py` now writes the reference fit next to the old columns. The new column `days_3d` is the
θ × |y| × E_sum fit of §14.3, run through `lnl_nd.reference_days`:
- the calibrated response;
- structure S_θ 2 % + S_θy 1 %;
- the per-arm gain nuisances;
- the E_sum window from `out/calo/resolution.csv`.

It is filled for every scenario, current (1, 4 µA) and mass (16.6–17.0) at MM 15° + TOF, for as built and big
plastics. Other hardware gets NaN: there is no calorimeter response for it. The days include the DAQ live
fraction of the same row, so compare `days_3d` with `days_fisher_live`. The other new columns are
`S3d_per_day`, `B3d_per_day` and `esum_3d`. `summary.json` has a `reference` block. The old columns (ideal
energies, shape known) are unchanged, and the deck and `lnl_week.py` still read them.

`python lnl/sim/lnl_geant.py --nd` (with `LNL_SEL` pointing at `sel_v3`) recomputes only these columns on the
existing CSV, in ~10 min. A full run computes them at the end.

Days to 3σ at R(ATOMKI), 1 µA, m 16.7:

| scenario | as built: counting, shape known | as built: 3D | big plastics: counting, shape known | big plastics: 3D |
|---|---|---|---|---|
| ATOMKI 2016 anomaly (1.10 MeV) | 15.5 | **17.0** | 1.20 | **1.00** |
| ATOMKI 2016, on resonance | 13.0 | 13.8 | 1.00 | 0.83 |
| Li₂O 700, 1.03 MeV (MEG II-2026 norm.) | 7.3 | 7.9 | 0.55 | 0.47 |
| LNL 2023-24 thick LiF | 8.7 | 9.4 | 0.66 | 0.56 |
| ATOMKI 2022 direct (0.80 MeV) | 55 | 65 | 4.1 | 3.6 |
| Hanoi 2024 (1.225 MeV) | 58 | 73 | 4.4 | 3.8 |

The ATOMKI 2016 anomaly row reproduces §14.3 (1.00 / 17 d). The 3D fit lets the background shape float and
uses a realistic calorimeter, and it still lands near the old statistics-only counting numbers: 13–17 % faster with big plastics, 6–25 %
slower as built (the off-resonance runs the most). At 4 µA every number is ¼. 17.0 MeV is ~1.4× faster than 16.7 (big plastics 0.70 d).

## 15. Target-region scattering once the background shape may float (2026-10-13)

Code: `sim/lnl_smear_nd.py` → `out/nd/smear_scan.csv`. Deck pitch slide "Smearing".

§10 found that even n_TOF-level smearing costs only ×1.5 in time. That was counting with the IPC shape known
exactly. Here the same question is put to the reference fit of §14.3, where the background shape is allowed to
float (Dylan's worry: the bump smeared by beam-pipe scattering).

**Method.** Every event's reconstructed angle is moved away from its Geant4 truth by a factor f:
θ' = θ_true + f(θ_reco − θ_true). The whole residual scales, tails included. This stands in for a thicker wall;
it is not a Geant4 run of one. The fits are as §14.3: calibrated response, S_θ 2 % + S_θy 1 % (ℓ = 10°), the arm
gains, a free acceptance cubic, and the θ-resolution scale ±10 %.

Days to 3σ at R(ATOMKI), 1 µA. σ68 is half the 16–84 % interval of the X17 residual:

| case | f | σ68 big plastics | θ alone | m_ee | θ × \|y\| | **θ × \|y\| × E_sum** | as built, 3D |
|---|---|---|---|---|---|---|---|
| CFRP 0.4 mm (baseline) | 1 | 4.5° | 29 | 1.7 | 1.2 | **1.0** | 17 |
| ~Al 0.5 mm | 2 | 9.0° | > 6000 | 7.7 | 3.2 | **2.5** | 38 |
| n_TOF capsule | 3.1 | 14.0° | > 10⁴ | 28 | 9.9 | **6.8** | 71 |
| ~1 mm stainless (Highland) | 6 | 27° | > 10⁴ | 284 | 83 | **31** | 122 |

- **Smearing costs far more once the shape floats.** At ~14° the 3D fit is ×6.8 slower (counting with a known
  shape: ×1.5). A broad edge is close to the Gaussian-process structure (ℓ = 10°) and the acceptance cubic,
  so the fit cannot tell them apart as well.
- **The higher-dimensional fit is what survives.**
  - The energy split and E_sum come from the scintillators and do not smear.
  - At ~14° the 3D fit is ×4 faster than m_ee; at 27°, ×9.
  - The angle alone is dead from 9° on.
- **The wall is the design driver.** Keep the thin CFRP chamber, or equivalent, over the region the leptons cross.
  - Geometry: the MM active area spans ±180 mm along the beam at 204 mm. So accepted leptons fly at
    48.6–131.4° to the beam axis and cross the plane |z| = Z at r ≥ 1.13·Z.
  - They leave the 25 mm chamber within |z| ≤ 22 mm.
  - Flanges, valves and the beam pipe are harmless inside the cone r < 1.1·|z|. This is a geometric estimate,
    to check in Geant4 with the real LNL beam line.
- Caveats:
  - The ×f residual is not a Geant4 wall: a real wall changes the tails and the energy loss differently.
  - The stainless row is a Highland scaling (x/X₀ 5.7 % against Al 1 mm's 1.1 % at 12.2°).
  - The structure length ℓ = 10° is fixed. A wider true structure would make broad edges cheaper; a narrower
    one, dearer.
- Next: a Geant4 L5-type run with the LNL beam line as drawn (ask for the drawings), and one with no chamber
  wall (§8 item 7).


## 16. The 3D fit in 2D, and the impostor test: can a mismodelled background fake the X17? (2026-10-14)

Dylan's question for the 15 Oct talk: in the 1D opening-angle spectrum, getting the background shape a little wrong kills
any claim of an excess. How do we know an excess is not a poorly modelled background? `sim/lnl_nd_maps.py` →
`out/nd/maps/{maps,proj,bias}.csv`; three new pitch slides (`deck/maps_slides.py`, after "S/B").

### 16.1 Maps

The reference fit's own event list (`lnl_nd.collect`: calibrated response, big plastics, MM 15° + TOF, E_sum window
14–19 MeV, side band 10–14 MeV, 1 µA, live-corrected) is binned in θ × |y| (3° × 0.05 and 6° × 0.1) per E_sum slice.
The background is KDE-smoothed in θ as in the fit.

- One week, big plastics: ~23,000 background pairs and ~650 X17 in the window. At 125–155° in 1D, S/B ≈ 8 %.
- The X17 is a band along the constant-mass curve, smeared by the measured |y|. The background fills the plane up to
  |y| ≈ 0.8, where a lepton is too soft to make a trigger leg.
- The best 5 % of cells reach S/B ≈ 23 %; |y| < 0.3 at 125–155° gives 13 %.

### 16.2 The impostor

The impostor is a background error built to copy the X17 *exactly* in the 1D angle spectrum. Each X17 event in the window
keeps its reconstructed θ, and takes |y| and E_sum from a background event at the same angle (±1.5°, 30 draws).

- **A, "acceptance":** partners are drawn from the whole fitted E_sum range. This is a geometry, material or efficiency
  error, which does not know the lepton energies, so it also lands in the γ₁ side band: ×2.5 its window size there,
  against ×0.4 for the X17.
- **B, "18 MeV physics":** partners come from the window only. This is an error in the 18 MeV IPC shape that the
  side band does not share.

In |y| at 125–155°, 74 % of the X17 is below 0.3, against 45 % of the impostor.

### 16.3 What each fit reports

The response is linear (Asimov): the fitted strength moves by (T F + P)⁻¹ T Σ g Δ/μ (`lnl_nd.fisher_nd(delta=…)`).
"χ² left" is the part of Σ T Δ²/μ that the free parameters cannot absorb. The table gives the fake X17 as a fraction
of a real one at R(ATOMKI), big plastics, 7 days, with structure S_θ 2 % + S_θy 1 % (the reference):

| fit | impostor A | impostor B | χ² left (A) | real X17 Z |
|---|---|---|---|---|
| θ alone | **100 %** | **100 %** | 0.0 | 1.6σ |
| m_ee | 18 % | 18 % | 0.3 | 5.6σ |
| θ × \|y\| | 14 % | 14 % | 6.0 | 6.9σ |
| **θ × \|y\| × E_sum** | **13 %** (1.0σ) | **24 %** (1.8σ) | 20.5 | 7.5σ |

- Without any structure terms, the 3D fit reads A as 21 % (B 25 %). The |y| and E_sum axes do most of the work, not the
  Gaussian-process freedom.
- As built: θ alone 99–100 %, 3D 14 % (A) and 21 % (B). There χ² left is only 1.5–2.7: there are too few pairs to see the
  mismatch in a week.
- **What no fit catches:** an error that copies the X17 in θ, in |y| *and* in E_sum is a signal-shaped background. The
  checks for it are physics:
  - QED fixes the IPC shape;
  - the X17 edge moves with E_p (441 keV, and the off-resonance points), where a detector effect does not.

### 16.4 Caveats

- The impostor is as large as the X17 at R(ATOMKI). The numbers are linear, so they scale with it.
- The test assumes the background templates and the response model are right apart from Δ. The fake fraction is a
  property of the fit's design, not a measured systematic.
- The n_TOF contrast on the slide is qualitative: σ68 14.5°, E* varying with E_n, ~40 % containment, and a capsule
  background that QED does not predict. Taken together, the n_TOF search had to rest on the angle. No n_TOF data were
  refitted here.
