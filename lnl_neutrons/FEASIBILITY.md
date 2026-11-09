# Neutron route at Legnaro: ³He(n,e⁺e⁻) with the MX17 apparatus — feasibility

**Update 2026-11-09 (Dylan: only existing beams, no money for new machines, no outreach for now):** read the ANTHEM 1.7×10⁻⁴ below with the `FACILITY.md` addendum: not an existing beam; defensible range 6.6×10⁻⁴ to 1.3×10⁻³ (estimate).

Facility record: `FACILITY.md`. Code: `lnl_neutrons_beam.py` (beam, geometry, reach with the shared engine). Slides (built, not published):
`out/lnl-neutrons-x17-feasibility.html`. Numbers: `out/lnl_neutrons_reach.csv` (CN), `out/lnl_neutrons_other_reach.csv` (LENOS, ANTHEM, SPES).

## 0. Answer — 2026-11-09

**The accelerators on site today cannot do it.** CN at its authorised ~3.3 µA, 3.0 MeV on a thin-stop Li layer, 30 bar × 40 cm cell at 20 cm: X17/IPC = **1.1×10⁻²** at 3σ in 50 d (big plastics;
as built 4.3×10⁻²), ×7 short of ATOMKI ⁴He, **~2 600 days to ATOMKI**, statistics-limited by cosmics. With a 90 % cosmic veto 4.4×10⁻³ (×2.9 short, ~430 d). At the current actually usable on Li today (~0.5 µA, ESTIMATE) it is 7×10⁻².

**The Demokritos verdict holds, for the same two reasons, but with different numbers:** the CN source is too weak (×6 000 fewer neutrons per second than Birmingham, 5×10⁹ n/s in 4π), and moving the cell closer to win that back puts it next to a production
target whose own ⁷Li(p,γ) IPC pairs outnumber the cell's by ×650 per day (×16–42 after geometry at 5–10 cm). Not 34 years here (the 40 cm cell and 3 µA give 7 years without a veto), but not a viable run either.

**LENOS and MUNES at Legnaro are not coming.** The TRASCO RFQ is being prepared at LNL to be **shipped to Caserta** for the clinical ANTHEM BNCT facility (HB2025). MUNES was never funded as a facility. LENOS exists only as the CN beam line. NEPIR ("NEPHIR") phase 0
is ≤ 1 µA at 70 MeV on a thick Be target, and the SPES cyclotron has a crack in its pit floor with no timeline (Feb 2026).

**The one interesting finding is off-site: ANTHEM at Caserta, if an INFN apparatus can ever use it.** 30 mA, 5 MeV, Be, 1×10¹⁴ n/s (model 8.6×10¹³, ×0.86 of the design value): engine reach **1.7×10⁻⁴** (130°, 2 m, big plastics; 4.6×10⁻⁴ as built), 0.6 d to ATOMKI, ×2 better than the engine's Birmingham. Even 3 mA gives
3.9×10⁻⁴ (0°, 2 m). The clinical building is due ~2027 and no user programme exists. Full Birmingham-style room Geant4 would move this up, not down (§6).

| 50 d, E\* ≤ 22 MeV (all E\* the same below 3.2 MeV) | big plastics | as built | days to ATOMKI | limit |
|---|---|---|---|---|
| CN today, ~0.5 µA, 3.0 MeV, D = 20 cm | 7.0×10⁻² | 2.8×10⁻¹ | ~10⁵ | statistics |
| **CN authorised, 3.3 µA, 3.0 MeV, D = 20 cm** | **1.1×10⁻²** | 4.3×10⁻² | 2 600 | cosmics |
| + 90 % cosmic veto | 4.4×10⁻³ | 1.6×10⁻² | 430 | IPC + cosmics |
| CN authorised, D = 5 cm, no target pairs (not credible) | 2.6×10⁻³ | 9.7×10⁻³ | 150 | target pairs if counted |
| same, with target pairs (ESTIMATE) | 8.3×10⁻³ | 2.4×10⁻² | 1 500 | target pairs |
| CN technical max, 6 µA, 3.0 MeV, D = 20 cm | 6.2×10⁻³ | 2.5×10⁻² | 850 | cosmics |
| LENOS design, 7.3×10¹⁰ n/s forward, 20 cm (not built) | 5.0×10⁻⁴ | 1.6×10⁻³ | 5.5 | statistics |
| **ANTHEM 30 mA, Caserta, 130°, 2 m (design; not at LNL)** | **1.7×10⁻⁴** | 4.6×10⁻⁴ | **0.6** | statistics |
| ANTHEM 3 mA, 0°, 2 m | 3.9×10⁻⁴ | 1.1×10⁻³ | 3.4 | statistics |
| ANTHEM 1 mA, 0°, 2 m | 7.6×10⁻⁴ | 2.3×10⁻³ | 13 | statistics |
| SPES 35 MeV, 750 µA on Be, 130°, 2 m (hypothetical port; throttled ×0.24) | 2.1×10⁻³ | 2.2×10⁻³ | 99 | correlated beam, DREAM |

Comparison at the same engine: Birmingham 3.3×10⁻⁴ (5.5×10⁻⁴, 6.7 d after the full Geant4 room), FRANZ design 3.3×10⁻⁴ (licence 2.2×10⁻³), FRM II MEDAPP 4.2×10⁻⁴. CN sits ×30 behind them.

**Overall call: WATCH.** Do not build a neutron plan on CN. Ask Pierfrancesco one question that could change this: whether the ANTHEM second room / experimental branch could take a non-clinical experiment.

## 1. Engine check — 2026-11-09

`lnl_neutrons_beam.py` calls `survey/soft_sim/soft_reach.py` directly (and `bepn_cyclotron/bepn_reach.py` for > 20 MeV). Reproduced: `bham_28_2m_pb5`, big plastics, 50 d, E\* ≤ 22 MeV: 3.318×10⁻⁴ here, 3.318×10⁻⁴ in `soft_reach.csv` (ratio 0.9999; `out/lnl_neutrons_engine_check.csv`).
ANTHEM's Be source from `bepn_beam` (ENDF/B-VIII.0): 8.6×10¹³ n/s against the design ~10¹⁴; mean E_n 1.1–1.6 MeV against 1.2 quoted; E_max 3.2 MeV.

## 2. CN beam model and yield normalisation — 2026-11-09

`out/lnl_neutrons_yield_check.csv`. `franz_beam.mc` (Birmingham's σ/S slowing-down MC, CM-isotropic), rescaled to 5×10⁷ n/s/µA at 2.0 MeV (FRANZ) and 9×10⁸ at 2.5 MeV (Lee & Zhou; Birmingham's 1×10⁹ at 2.6 agrees to 3 %). LiLiT 0.75; the published CN 40 µm thin target at 4 MeV (PINO): my thin-slice estimate 1.3× high.
**No absolute LNL thick-Li measurement below 3 MeV was found (ask).** The bham σ table ends at 3 MeV, and the n₁ (⁷Be\* 429 keV) channel above 2.38 MeV is not modelled (a ~10–20 % soft addition).

Forward yield (per µA): 1.4×10⁷ /sr at 2.0 MeV, 1.2×10⁸ /sr at 3.0 MeV. Every neutron below 1.3 MeV: all inside the X17 window.

**Current (the real limit):** radiation at the switching magnet, not the target. arXiv:2605.12005: ~0.3 µA at 5.5 MeV on Li today, higher at lower E; ×4–6 with a BPE + Pb package "under evaluation" → 1 µA (E_n ≤ 4 MeV), 2–3 µA (E_n < 2 MeV). So: today ~0.5 µA (2.5 / 5, ESTIMATE),
shielded 2.5, authorised 4 (min with a 10 W target: 3.3 µA at 3 MeV), technical 6.

## 3. Geometry and the signal — 2026-11-09

The engine assumes a parallel Ø8 cm beam. At CN the rate forces the cell close, so each MC neutron is carried from a point Li target to the cell and scored with its real path (n_eff = Σ w·path/40 cm; backgrounds scaled with n_win through the window).
3.0 MeV, 3.3 µA: n_win = 9.5×10⁸ (5 cm), 3.3×10⁸ (10), 9.0×10⁷ (20); n_eff/n_win = 0.15–0.34. IPC pairs/day (4π): 9.2×10⁴ (D = 5), 1.9×10⁴ (20). A 30 bar × 40 cm cell (~8 g ³He) is used because it is what the engine models.

**n_TOF capsule** (`out/lnl_neutrons_capsule.csv`, Demokritos' analytic method: 500 bar, gas tip 1 cm from the Li, G = 1.82 cm, days from the p+t scaling). At 2.5 MeV (thick), 1 µA: 6.2×10⁴ pairs/day against Demokritos' 4.2×10⁴ (our σ average is a little higher), reproducing their row.
At 2.8 MeV, 4 µA: 3.7×10⁵ pairs/day → 17 d (big plastics), 226 d as built. **This is an upper bound with every background off; a 1 cm capsule-to-target gap also means the target pairs below are in the same place**, and it cannot be measured.

## 4. Target pairs: the Demokritos argument, redone — 2026-11-09

The protons make pairs in the production Li too. **Thin-stop Li** (~110 µm at 3 MeV, stopping at the 1.881 MeV threshold; the CN line uses 10–40 µm, so a thicker-than-usual target) avoids the 441 and 1030 keV resonances:
direct capture only, ~5×10⁻⁹ γ/p (σ_DC ≈ 10 µb, **ESTIMATE, the single largest number here**), × α ≈ 3.5×10⁻³. Rates at 3.0 MeV, 3.3 µA: 3.0×10⁷ target pairs/day, against 1.9×10⁴–9.2×10⁴ IPC in the cell (×320–1 600).

A toy geometric acceptance (`out/lnl_neutrons_target_acceptance.csv`, 100–150° pairs on two arms) gives 13 % (D = 5 cm) and 2.5 % (10 cm) of the cell's, and zero at ≥ 20 cm, where the vertex is behind the arm envelope. After that: ×42 and ×16 the cell's IPC for D = 5, 10 cm (a ×25 thick-target case: 1 100), so close-coupling
loses all the gain. At D = 20 cm target pairs leave the acceptance and cosmics limit. σ_DC needs measuring; a thick target (Demokritos) is worse: ×25.

## 5. Scans — 2026-11-09

- **Energy:** 3.0 MeV is best; below 2.0 MeV yield collapses (reach ×10 worse at 2.0 than 2.3 MeV).
- **Distance:** ∝ D at D ≥ 10 cm in reach (fewer neutrons); inside 10 cm target pairs bite. Sweet spot 20 cm.
- **Thin vs thick:** 2.8 MeV thick gives 1.3×10⁻² vs 1.2×10⁻² thin (D = 20) and far more target pairs at close range. Thin wins.
- **Pb filter:** irrelevant here: statistics are the limit.
- **Pulsed CN** (700 nA, 3 MHz): gate of ~60 ns (neutron ToF spread at D ~ 30 cm) cuts cosmics ×0.18 but loses ×5 in current: ×2.4 worse in reach (ESTIMATE). No use.
- **As built vs big plastics:** ×4 worse as built; big plastics are required.

## 6. Walls and what this does not model — 2026-11-09

- **CN**: statistics (cosmics 5 300/d in window against IPC 130–630). DREAM live ≥ 0.99, MM occupancy 10⁻⁴: irrelevant. Beam accidentals ≈ 0, correlated ≤ 18/d.
- **ANTHEM**: at 130°, 2 m statistics-limited (IPC 3.8×10⁴, cosmics 5.3×10³/d). At 0° the DREAM wall (live 0.45): throttled.
- **SPES 35 MeV**: correlated beam neutrons (8×10⁴/d) and DREAM, as for the 30 MeV cyclotrons.
- **Room/shield caveat (Birmingham lesson).** The engine is beam-only: vacuum tube, parallel Ø8 cm beam. Birmingham's full Geant4 lost ×1.7 to room return even after added shielding. **For ANTHEM at 2 m:** a source of 8.6×10¹³ n/s feeds an arm at 2 m with ~2×10¹² n/s (no shield); keeping leakage below 10 % of the pencil's own singles needs ~1–1.3 m of BPE/concrete-equivalent shield (T ≈ 6×10⁻⁷, stand-in TVL 10–20 cm; `bepn_beam.shield` convention). The clinical beam shaper (BSA) room is not this.
- **CN room:** 5×10⁹ n/s 4π, arm neutrons ~10⁸/s without a shield; ε ≤ 10⁻⁴ gives ≤ 10⁴ singles/s, tolerable. Lower priority.
- Not modelled: target chamber, air, n₁ branch, the diverging beam's angle to the Geant4 table, LENOS's real Maxwellian shape, γ from Cu backing.

## 7. Practical scorecard — 2026-11-09

| | CN (today) | ANTHEM (Caserta) | NEPIR / SPES |
|---|---|---|---|
| beam exists today | **yes** (operating, Li targets in use) | no; RFQ pre-shipping, building ~2027 (HB2025) | cyclotron built; pit crack, no timeline |
| time to first neutrons | now, at ≤ 0.5 µA on Li | ≥ 2028 realistic (ESTIMATE) | unknown |
| access for us | **PAC; Dylan's LNL contract helps** | no user programme; clinical **(ask)** | not a user station yet |
| space / shielding | same arms as the proton plan; local BPE | second room unknown; ~1 m shield + collimator if it exists | conduit, ≤ 1 µA |
| cost estimate | 30 bar cell + ~60 L STP ³He (~8 g): ≥ €100k class (ESTIMATE, see `he3_target/`, not yet built), no beam fee | shield + cell, ≥ €200k (ESTIMATE) | n/a |
| radiation / ³He | RP limit is the current cap; tritium unlikely | clinical licence **(ask)** | — |
| competition | CN 0° line is "the most used"; working-day operation; director floated replacing CN + AN2000 | clinical priority | SPES first |
| access restriction (fact) | LNL PAC, RP review | clinical facility, Univ. Campania + INFN | SPES programme |

Overall: **WATCH.** CN alone does not reach ATOMKI in any plausible configuration (×2.9 short with a veto; ×7 without). It could validate the ³He cell and the target-pair calculation, and give an IPC measurement if a cell exists anyway.

**What would have to be true for top-3:** ANTHEM gives a user a ≥ 1 mA view of the Be target with room for 1 m of shield, before ~2030. Or LNL builds a local ~mA source, which is not on any public plan. CN alone cannot: it needs ≳ 10× current and a veto.

## 8. Next steps — 2026-11-09

1. Dylan asks Pierfrancesco (`FACILITY.md` §5, questions 1, 3, 6). Question 6 (ANTHEM) is the only one that can change the call.
2. Measure or find σ_DC(⁷Li(p,γ)) at 2–3 MeV and the target-pair yield: it decides close coupling. A short CN run with the proton-route set-up already gives this.
3. If ANTHEM opens: a Geant4 run (branch `bham`, `--src` Be 5 MeV table, 2 m, room and 1 m shield) to replace the engine number. Spec: 30 mA, ⁹Be(p,n) table from `bepn_beam.spectra(5.0)`, 130° and 0°, big plastics, cell at 2 m, shield of BPE + concrete, room walls 2 m.
