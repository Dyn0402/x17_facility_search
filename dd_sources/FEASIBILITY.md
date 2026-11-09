# Intense D-D sources — X17 feasibility with the shared Geant4 soft-beam background

**Update 2026-11-09 (Dylan: only existing beams, no money for new machines, no outreach for now):** the "KEEP AS BACKUP" call below is superseded: CLOSED for now.

Facility record: `FACILITY.md`. Beam model and reach: `dd_beam.py`; robustness: `sens.py`; figures: `dd_figs.py`.
Slides (built, not published): `out/dd-sources-x17-feasibility.html`.

## 0. Answer — 2026-11-09

**A measured 3×10¹¹ n/s D-D generator, with the 30 bar × 40 cm cell 35 cm from the source behind a shadow shield and the
cell at 90° to the deuteron beam: X17/IPC = 6.5×10⁻⁴ at 3σ in 50 d (big plastics; as built 1.8×10⁻³), 9.5 days to the
ATOMKI strength.** At the more robust 50 cm: 8.5×10⁻⁴ (as built 2.6×10⁻³), 16 days. Limited by statistics (IPC and
cosmics) at ≥ 35 cm; inside ~30 cm the direct flux through the shield takes the DREAM live time to 0.2–0.3 and sets the limit.

**The catalogue's reason ("×10 too weak", 9×10⁻³ shielded at 2.5 m) is outdated for geometry.** No collimated beam is needed, so
the cell can sit at 35–50 cm. That is worth ×10 on 2.5 m. But the class has a practical problem instead: **nobody offers
3×10¹¹ D-D beam time**, and the one European D-D station (FNG) is ×500 weaker.

**Call: KEEP AS BACKUP.** The reach is close to Birmingham's (5.5×10⁻⁴ in full Geant4, 6.7 d) on an estimate that is not yet a
Geant4 result, and it needs a machine that must be bought or contracted. Birmingham's machine exists and is at hand.

| big plastics (as built) in 50 d | d = 25 cm | **35 cm** | 50 cm | 100 cm |
|---|---|---|---|---|
| **Phoenix 3×10¹¹ measured, 90°** | 1.0×10⁻³ (2.9×10⁻³) | **6.5×10⁻⁴ (1.8×10⁻³)** | 8.5×10⁻⁴ (2.6×10⁻³) | 1.9×10⁻³ (6.3×10⁻³) |
| Phoenix 3×10¹¹, 135° | 9.4×10⁻⁴ (2.7×10⁻³) | 6.0×10⁻⁴ (1.7×10⁻³) | 7.9×10⁻⁴ (2.4×10⁻³) | 1.8×10⁻³ (5.8×10⁻³) |
| 1×10¹² (hypothetical) | 1.0×10⁻³ (2.9×10⁻³) | 5.4×10⁻⁴ (1.3×10⁻³) | 5.2×10⁻⁴ (1.3×10⁻³) | 9.4×10⁻⁴ (2.7×10⁻³) |
| 3×10¹² (the catalogue's "need") | 1.0×10⁻³ | 5.4×10⁻⁴ | 5.1×10⁻⁴ (1.2×10⁻³) | 8.5×10⁻⁴ |
| Deuteron 1.5 MeV, 5 mA, gas, 135° (hypothetical) | 9.0×10⁻⁴ | 4.4×10⁻⁴ (1.1×10⁻³) | **4.1×10⁻⁴ (1.1×10⁻³)** | 7.6×10⁻⁴ |
| Compact 1×10¹⁰ (Adelphi / Astral class, d = 15 cm: 3.7×10⁻³) | 5.4×10⁻³ | 8.3×10⁻³ | 1.4×10⁻² | 4.2×10⁻² |

Days to ATOMKI at 3σ: Phoenix 35 cm **9.5 d** (as built 74 d); 50 cm 16 d (as built 144 d); Phoenix 135°, 35 cm 7.9 d.
Above ~1×10¹² the reach stops improving (5×10⁻⁴): the throttle is set by the DREAM dead time and direct and room load, so more yield is not the fix.
Every row keeps E_n in the window except where noted (§2). All-E\* is identical at 90° and 135°, since no neutrons lie above the window.

## 1. Engine check — 2026-11-09

`dd_beam.py --check` calls `soft_reach.py` for `bham_26_2m_pb5`: 3.82×10⁻⁴ big plastics, 1.177×10⁻³ as built (50 d), identical to `soft_reach.csv`.

## 2. Source model and kinematics (ESTIMATE where marked) — `out/dd_kinematics.csv`

- σ: Bosch & Hale 1992 (published fit). Stopping of D in D: velocity-scaled Andersen–Ziegler form (ESTIMATE, ±15 %).
- Thick D₂ gas: 8.7×10⁹ n/s per mA at 300 keV, so Phoenix's measured 3×10¹¹ implies ~35 mA **(ask the current)**. Solid Ti-D is ×0.07 of gas, from FNG (model 6.1×10⁸, measured 5.7×10⁸ at 1 mA, 300 keV).
- CM angular W = 1 + A cos²θ (A ESTIMATE, rising with E_d). Thick-target E_n at the cell, 300 keV deuterons:
  0° mean 3.06 MeV (1.4 % ≤ 2.75 MeV); 45°: 11 %; **90°: mean 2.50 MeV, 100 % in window; 135°: mean 2.18 MeV**.
- **Directionality decides the window.** At 0° the reach collapses to 3.6×10⁻² in the E\*≤22 metric (the engine's E_n ≤ 2.75 MeV bin edge is hard),
  though the "all E\*" column gives 5.5×10⁻⁴: E_n 3.1 MeV is outside the window as we define it, not useless physics. The honest choice is 90–135°.
- Higher deuteron energy, 1.5–2 MeV: the yield rises ×37–67 per mA over 300 keV, but at 90° only 50–62 % of the thick-target neutrons remain ≤ 2.75 MeV. **135° keeps 100 % and E_n ~ 2.0 MeV** (the best physics, softer E\*), at the cost of a beamline running on the cell side at 45° to the cell axis (**(ask)** engineering).
- Bin caveat: E_n 2.45 MeV falls in the 1.5–2.75 MeV analysis bin, whose signal tables are at the 2 MeV node. θ_min at 2.45 MeV is a few degrees below 99.3°; the reach used is the bin's.

## 3. Geometry: the Ø8 cm spot assumption fails, and its correction — `out/dd_geometry.csv`, `out/dd_geometry.png`

The engine takes "n/s through the Ø8 cm spot" as a parallel beam along the cell. A 4π source close by is not that.

**Correction (ESTIMATE):** use G = (1/L)∫_V dV / (4πr²), the parallel-beam-equivalent fraction of source neutrons (with the angular factor §2).
Versus the naive Ω = 50 cm² / (4πd²) taken at the front face it is ×0.42 (15 cm), ×0.60 (25), ×0.73 (35), ×0.87 (50), ×1.12 (100). Versus the naive figure at the cell centre, ×2.3, ×1.9, ×1.8, ×1.7, ×1.6. So the correction is a factor ~2 either way, and it is in the numbers above. A 40 cm line source transverse to the cell costs ×0.84 at 15 cm and ×0.91 at 25 cm, and is small at ≥ 35 cm.

**Arms and shadow shield (ESTIMATE, `arm_transmission`).** The arms see the source directly, which N5 does not contain.
Tracks need the volume between the cell and the arms clear, so the shield may only sit upstream of the cell front plane (first version of this model ignored this and was ×10 optimistic in transmission; corrected).
With a borated-PE shield of tenth-value length 12 cm (ESTIMATE; 8–20 cm bracket) and an 11 cm source shroud:

| d | arm exposure unshielded (per source n) | transmission (TVL 12 / 8 / 20 cm) |
|---|---|---|
| 15 cm | 3.9 % | 0.19 / 0.09 / 0.36 |
| 25 cm | 2.2 % | 0.030 / 0.006 / 0.12 |
| 35 cm | 1.3 % | 4.9×10⁻³ / 3.5×10⁻⁴ / 0.04 |
| 50 cm | 0.6 % | 3.1×10⁻⁴ / 5.5×10⁻⁶ / 7.8×10⁻³ |

Arm response per neutron striking an arm (ESTIMATE from N5 and an assumed scatter fraction): legs 1.6×10⁻³, "ok" singles 3×10⁻⁶ (5 MC events, ±×3).
Room return (ESTIMATE, 150 m² surfaces): 1×10⁻⁷ legs per arm per source neutron, ok/legs = 0.05. The Birmingham Geant4 lesson is that room and wall dominate, so this is the softest number in the study.
Without a shield the reach at Phoenix yield is 7–13×10⁻³ (direct-flux-limited): the shield is the design.

## 4. Reach and the limiting wall — `out/dd_reach.csv`, `out/dd_reach_vs_d.png`

Phoenix 3×10¹¹, 90°, big plastics, 50 d:

| d | ρ | floor (no beam background) | live | IPC / day | cosmics / day | X17 / day (at ATOMKI, window) |
|---|---|---|---|---|---|---|
| 25 cm (s = 0.63) | 1.0×10⁻³ | 4.5×10⁻⁴ | 0.33 | 1 376 | 1 736 | 21 |
| 35 cm | 6.5×10⁻⁴ | 5.9×10⁻⁴ | 0.81 | 3 471 | 4 289 | 53 |
| 50 cm | 8.5×10⁻⁴ | 8.2×10⁻⁴ | 0.94 | 2 406 | 4 966 | 37 |
| 100 cm | 1.9×10⁻³ | 1.9×10⁻³ | 0.96 | 813 | 5 094 | 12 |

At ≥ 35 cm the limiting wall is **statistics: IPC plus cosmics at about equal share, within ~10 % of the floor**. Cosmics are constant and a cosmic veto would help directly.
Inside 25 cm the direct arm flux through the thin shield limits it (DREAM live 0.2–0.3). Micromegas occupancy is ≤ 0.2 % throughout.
Accidentals in N5 are 0.01/day in the window at these rates, because 2.45 MeV recoils cannot reach E_sum > W/2; they would be larger with hard capture γ, but raising them ×100 changes nothing (`out/dd_sens.csv`).

**Sensitivity (`out/dd_sens.csv`, Phoenix 90°):**

| variant | 35 cm | 50 cm | 100 cm |
|---|---|---|---|
| nominal | 6.5×10⁻⁴ | 8.5×10⁻⁴ | 1.9×10⁻³ |
| shield TVL 20 cm | 1.2×10⁻³ | 8.9×10⁻⁴ | 1.9×10⁻³ |
| arm response ×3 | 7.7×10⁻⁴ | 8.6×10⁻⁴ | 1.9×10⁻³ |
| room ×3 | 7.7×10⁻⁴ | 9.7×10⁻⁴ | 2.2×10⁻³ |
| room ×10 | 1.3×10⁻³ | 1.8×10⁻³ | 4.0×10⁻³ |
| correlated at the N5 90 % bound, before cuts | 1.2×10⁻² | 1.4×10⁻² | 2.4×10⁻² |

**The correlated term is the single biggest unknown.** N5 has **zero** two-arm same-event rows between 1.5 and 10 MeV (9 at 10–20 MeV), so the engine's correlated background at 2.45 MeV is 0, and its 90 % bound, charged in full with no cut efficiency, would give the last row: ×20 worse. That row is a limit on our MC statistics, not a prediction. E_sum > W/2 needs ~10 MeV visible, which a 2.45 MeV neutron can reach only through capture cascades (H 2.2, Al 7.7, Fe 7.6, N 10.8 MeV γ in the same event), so the real term is likely well below it, and a real room would contribute through such γ. Only a dedicated 2.45 MeV Geant4 run settles it.

## 5. Scan summary (all in `out/dd_reach.csv`, `dd_sens.csv`)

- **Distance:** 25 cm is too close for the shield that fits, 35–50 cm is the optimum, 250 cm is the catalogue's and loses ×12.
- **Shield:** essential; without it 7–13×10⁻³ at 3×10¹¹.
- **Angle:** 90° or 135°, 0° is out of the window.
- **Energy:** 300 keV (Phoenix) fine; 0.75–2 MeV deuteron accelerators at 135° give up to 4.1×10⁻⁴ with higher yield, hypothetical machines. Above ~1×10¹² equivalent, the reach saturates.
- **Yield:** 1×10¹⁰ (commercial, cheap) reaches only 3.7×10⁻³ at 15 cm, 310 d to ATOMKI, not useful for the search but a possible commissioning source.
- **Cell vs capsule (ESTIMATE, `out/dd_capsule.csv`):** with the source where the shield fits, the n_TOF capsule (500 bar, R 1, L 4 cm, on the arm centre) gets ×0.054–0.064 the captures of the 30 bar cell, so **×4 worse reach** (statistics scaling; ~2.5×10⁻³). Pulling the capsule to the source to win flux puts the source inside the arm envelope, where no shield fits. Take the 30 bar cell (87 L ³He, ~217 k€).

## 6. Caveats (read before quoting)

- Beam-only N5/G5/G6 with a vacuum tube and Ø8 cm spot; the Ø8 cm correction, direct-arm flux and room return are **ESTIMATE** add-ons. Birmingham moved from 3.3×10⁻⁴ (engine) to 5.5×10⁻⁴ (full Geant4 with room): expect a similar correction here, ×1.5–3 worse is plausible, and this is why the call is not PURSUE.
- 3×10¹¹ is measured for the Phoenix system (2018); today's D-D availability is unknown **(ask)**.
- The neutron statistics at 2.45 MeV are thin: 5 MC "ok" singles in the 1.7–3.1 MeV bin (1 404 legs).
- No T(d,n) 14 MeV tail is modelled; T grows in a recirculated D₂ target **(ask)**.
- 2.45 MeV is above the 2 MeV node of the signal bin (§2); θ_min sits a few degrees lower than at the node.

## 7. Practical scorecard

| item | assessment | evidence |
|---|---|---|
| Beam exists today? | Partly. 3×10¹¹ D-D demonstrated (2018); 1×10¹⁰ commercial exists (Adelphi, Astral) | §FACILITY 1 |
| Time to first beam | 2–4 years to buy, install and shield a 3×10¹¹ system (ESTIMATE) | vendor and vault not costed |
| Access realistic? | Not as a user programme. Purchase or contract; FNG is ×500 weaker | FACILITY §2 |
| Space / shielding | New vault, ~2 m concrete; 5×5 m around the source (ESTIMATE); beamline at 90–135° to the cell | FACILITY §3 |
| Cost | Compact 10¹⁰ unit: ~10⁵ $ scale (**ask**); 3×10¹¹ system: several M€ with vault (ESTIMATE); ³He 217 k€ | Starfire quote; not a Phoenix quote |
| Radiation / ³He | ~3.4 Sv/h at 1 m (ESTIMATE); ~2 GBq T in the D₂ loop; standard ³He cell | FACILITY §3 |
| Competition for beam | None, a dedicated machine | |
| Access restrictions (plain fact) | US vendor (ITAR/EAR on the hardware **(ask)**); radiation licence wherever it is sited | |
| vs Birmingham (5.5×10⁻⁴ full Geant4, 6.7 d) | Slightly worse, on estimate terms; machine must be bought | |
| vs FRANZ (design 3.3×10⁻⁴, today 4.9×10⁻³) | Better than FRANZ today; worse than its design | |
| vs FRM II MEDAPP | See dashboard row; D-D needs a new site where MEDAPP exists | |

**To be top-3:** (a) a 3×10¹¹ D-D system purchasable or hostable at ≤ ~2 M€ with a vault at a partner lab, (b) a mono-energetic 2.45 MeV Geant4 run with a real shield and room confirming ≲ 1×10⁻³, (c) a cosmic veto. Cosmics are half the background at 35–50 cm.

## 8. Next steps (Geant4, not run)

Run on `bham`-branch with the room: `--beam-particle n` 2.45 MeV mono-energetic, the gun at 35 and 50 cm, isotropic (or 4π with forced collision into the cell), the 30 bar cell, the arms, a BPE shadow shield upstream of the cell front plane, and a concrete room (Birmingham style). 10⁹ primaries for two-arm correlated events with E_sum > W/2; at least 3 000 "ok" singles per arm. This fixes the correlated term, the arm response, the shield and the room together.
