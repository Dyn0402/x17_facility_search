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

## 9. Why the big plastics win, and how big they need to be (2026-10-09)

Code: `plastic_size.py` → `out/plastics/` (figure `out/plastics/figures/plastics_size.png`).
Deck slides 12–13 ("Why big", "Plastic size").

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
Deck slides 15–16 ("Scattering", "Scattering 2"). It is the LNL version of the n_TOF capsule
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
