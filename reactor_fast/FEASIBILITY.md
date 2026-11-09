# Operating reactor fast and epithermal beams — X17 feasibility

**Update 2026-11-09 (Dylan: only existing beams, no money for new machines, no outreach for now):** the TAPIRO "PURSUE enquiry" below is superseded: WATCH, enquiry on hold.

Facility record: `FACILITY.md`. Beam model and reach: `reactor_fast_beam.py`, `rf_scans.py` → `out/rf_*.csv`. Slides (built, not published):
`out/reactor-fast-x17-feasibility.html`.

## 0. Answer — 2026-11-09

**No operating reactor has a MEDAPP-class fast beam today. Two things are real: the operating BNCT epithermal beams, ~1×10⁻³, and one new idea, ENEA's
TAPIRO (5 kW fast reactor, Rome), which could match MEDAPP if a straight fast channel to its core is opened.**

| 50 d, E\* ≤ 22 MeV, shared engine (no room) | big plastics | days to ATOMKI | as built | limiting wall |
|---|---|---|---|---|
| **TAPIRO open channel + 5 cm Pb** (concept; flux ESTIMATE) | **4.8×10⁻⁴** (γ/n = 3: 5.0×10⁻⁴) | 5.1 | 1.4×10⁻³ | statistics (IPC + cosmics) |
| same, core-view factor ×0.3 lower | 1.0×10⁻³ | 23 | 3.3×10⁻³ | statistics |
| **LVR-15 BNCT beam** (operating; measured 2003 free beam), 35 cm from exit | 1.05×10⁻³ | 25 | 2.8×10⁻³ | statistics; DREAM live 0.68 |
| LVR-15 at the exit (arms against the wall, not realistic) | 8.2×10⁻⁴ | 15 | 1.1×10⁻³ | DREAM + accidentals (throttle ×0.8) |
| RA-6 design / THOR 1 MW / THOR 2 MW | 8.1×10⁻⁴ / 9.7×10⁻⁴ / 8.6×10⁻⁴ | 15 / 21 / 16 | 2.0 / 2.2 / 1.3×10⁻³ | statistics → DREAM at 2 MW |
| MITR FCB (2003 numbers; being converted to materials testing) | 1.2×10⁻³ | 30 | 1.1×10⁻³ | DREAM + accidentals (throttle ×0.4) |
| TAPIRO existing epithermal column | 1.2×10⁻³ | 33 | 3.5×10⁻³ | statistics |
| *reference:* FRM II MEDAPP / Birmingham engine (full Geant4) / FRANZ design | 4.2×10⁻⁴ / 3.3×10⁻⁴ (5.5×10⁻⁴) / 3.3×10⁻⁴ | 4 / 2.4 (6.7) / 2.4 | | |

All E\*: TAPIRO Pb 4.1×10⁻⁴; BNCT beams unchanged (they have almost nothing above 2.75 MeV).

**The catalogue's bnct_reactor reason was wrong in both directions.** "2.5×10⁻³ ILL-scaled" is replaced by the engine value 0.8–1.2×10⁻³ (big plastics): better than ILL scaling
because the fast and epithermal group (≥1 keV) gives most of the pairs (70–86 %), and the γ and fast neutron background of real beams is modest once the arms are off the beam.
But it is ×2 short of MEDAPP and ×3 short of Birmingham's engine number, and rests on a sub-keV background assumption (×10 in §3 → 3×10⁻³).

**Overall call: KEEP AS BACKUP for the class; PURSUE one enquiry: TAPIRO.** TAPIRO is the only operating-reactor route to a MEDAPP-equivalent, but it needs a modification of
the reactor (open a fast channel through the column region, Cu window) that only ENEA can judge. LVR-15 is the operating backup at 1×10⁻³ if the BNCT room can be had.

## 1. Survey — 2026-11-09

`FACILITY.md` §1. Only TAPIRO, LVR-15, MITR, THOR, RA-6 have enough flux to be worth the engine. University fast ports (OSU 2.1×10⁷ at 450 kW,
UT Austin 3.75×10⁶ design) are on the wrong side of the flux grid in §2. KUR ended on 23 April 2026. MARIA's H2 converter has no measured beam.

## 2. What a reactor fast beam must deliver (engine map) — 2026-11-09

`out/rf_flux_grid.csv`: Watt spectrum, Ø8 cm, 50 d, big plastics, E\* ≤ 22 MeV.

| flux at the cell (n/cm²/s) | γ/n = 0.3 | γ/n = 1 | γ/n = 3 | γ/n = 10 |
|---|---|---|---|---|
| 10⁶ | 6.9×10⁻³ | 6.9×10⁻³ | 7.0×10⁻³ | 7.1×10⁻³ |
| 10⁷ | 1.1×10⁻³ | 1.1×10⁻³ | 1.1×10⁻³ | 1.6×10⁻³ |
| 3×10⁷ | 5.5×10⁻⁴ | 5.7×10⁻⁴ | 6.9×10⁻⁴ | 1.5×10⁻³ |
| 10⁸ | 3.5×10⁻⁴ | 4.2×10⁻⁴ | 6.5×10⁻⁴ | 1.5×10⁻³ |
| 3×10⁸ and above | 3.5×10⁻⁴ | 4.2×10⁻⁴ | 6.5×10⁻⁴ | 1.5×10⁻³ |

Answers two questions directly. (a) **Where is the γ limit?** The reach saturates at ~10⁸ n/cm²/s; above it the beam is throttled (DREAM), and the plateau is set by γ/n, exactly MEDAPP's
situation. (b) **What flux is needed to beat ATOMKI (1.5×10⁻³)?** ≳ 5×10⁶ n/cm²/s with γ/n ≲ 3; 3×10⁷ reaches 5.7×10⁻⁴. This is the yardstick for every future fast port.

## 3. Beam models and the sub-keV treatment — 2026-11-09

`reactor_fast_beam.py` (docstring has the sources); summary in `out/rf_beam.csv`, the capture budget by energy in `out/rf_budget.csv`.

**Engine check:** I reproduce `medapp_std` and `bham_28_2m_pb5` of `soft_reach.csv`, both hardware sets, 50 d (`out/rf_engine_check.csv`: ratio 1.000 to 4 digits).

- **BNCT beams.** Thermal (Maxwellian), 1/E epithermal 0.4 eV–10 keV, 1/E·exp(−E/E_c) fast above 10 keV. E_c is fitted to the measured dose per fast neutron (LVR-15 1.3×10⁻¹² Gy cm²
  per epi, fast/epi 0.15 → E_c = 1.4 MeV, ESTIMATE ±30 %), applied to all BNCT beams; for MITR, THOR, RA-6 and the TAPIRO column the fast flux comes from the published fast dose.
  With E_c = 0.3 MeV LVR-15 becomes 1.3×10⁻³ (the fast group gives ~40 % of its pairs). γ: dose/(1×10⁻¹¹ Gy cm²), MEDAPP's spectrum stand-in.
- **Stand-off, ESTIMATE:** a BNCT beam at its exit cannot host a cell with arms; LVR-15's flux falls ×2.5 in 20 cm; ×0.25 at ~35 cm. Used for the headline; the scan is in §0.
- **Below 1 keV (N5's lower edge), stated:** 60–90 % of an epithermal beam by number. Three variants in `rf_reach.csv`:
  - `subkev` (headline): pairs from ENDF cross sections of the 30 bar cell (the 1/v absorption in ³He is taken into account); each sub-keV neutron counts in the background as a 1–3 keV neutron. ESTIMATE.
  - `n5only`: everything below 1 keV removed: LVR-15 9.8×10⁻⁴, MITR 7.2×10⁻⁴ (the sub-keV flux adds more background than signal).
  - `subkev10`: ×10 background weight (capture γ in walls/dump that N5 cannot see): LVR-15 and THOR both → **2.9–3.3×10⁻³**.
  The ≥1 keV group gives 86 % of the pairs at LVR-15, 79 % at THOR, 70 % at MITR, so the headline does not lean on sub-keV pairs. It does lean on sub-keV neutrons being quiet.
  Pairs below 1 keV are put in the first analysis bin (E\* = 20.95 MeV vs the true 20.6): a small shape error, and X17/IPC is assumed constant in E\*, which at thermal energies is an assumption (M1 capture, E\* just above the 0⁺ doublet).
- **TAPIRO open channel, concept.** S = 3×10¹⁴ n/s (Rosa 2009, calculated), which reproduces the thermal-column-entrance flux 1.5×10¹⁰ at r = 40 cm as S/4πr². A straight channel to the shield face at L = 2.70 m gives Φ = f·S/4πL² = 1.64×10⁸ for a core-view factor f = 0.5 (ESTIMATE; f = 0.15 also shown). Spectrum: Watt + 1/E·exp(−E/1.5 MeV) with the Watt weight fixed by 20 % > 1.35 MeV at core centre (Rosa); ⟨E⟩ ≈ 0.8 MeV (see `out/rf_beam.csv`).
- **γ at TAPIRO: not published (ask).** Engine scan γ/n = 0.3 / 1 / 3 at the cell.

## 4. Filter and throttle scan — 2026-11-09

`out/rf_reach.csv` (big plastics, 50 d, E\* ≤ 22 MeV):

| TAPIRO open channel | no Pb | 5 cm Pb | 10 cm Pb |
|---|---|---|---|
| γ/n = 0.3 | 3.3×10⁻⁴ | — | — |
| γ/n = 1 | 4.6×10⁻⁴ (throttle 0.8) | **4.8×10⁻⁴** | 8.8×10⁻⁴ |
| γ/n = 3 | 8.8×10⁻⁴ (throttle 0.3) | **5.0×10⁻⁴** | 8.8×10⁻⁴ |

5 cm Pb gets the same answer without knowing γ/n, because the beam is on the plateau of §2. Pb costs ×2.7 in neutrons (uncollided only: conservative) but removes ×7 of the γ.
**Conveniently the published TAPIRO BNCT column keeps a 5.6 cm Pb layer in the copper window for criticality:** the filter and the reactivity compensation are the same object (ENEA to confirm).
The LVR-15 beam is flux-starved: 5 cm of Pb takes it to 1.9×10⁻³, no filter is the right choice. **Bi is equivalent in this model (within 10 % in μ_γ).**

## 5. Cell — 2026-11-09

`out/rf_cells.csv`. The n_TOF capsule (Ø2 cm) wastes a Ø8 cm beam: TAPIRO Pb 4.8×10⁻⁴ → 1.7×10⁻³; LVR-15 1.05×10⁻³ → 5×10⁻³. The 10 bar fallback: ×2.1. **The 30 bar × 40 cm cell is the right one here** (backgrounds kept at the NFS-cell Geant4 values: ESTIMATE).

## 6. Reactor-beam-specific caveats — 2026-11-09

- Birmingham's full Geant4 moved 3.3→5.5×10⁻⁴ (×1.7) when the room, dump and wall leakage were added. Engine numbers here have none of that, and a reactor adds a very large shield-face fast and γ field. Assume at least ×1.5.
- The engine's Ø8 cm parallel beam ignores the divergence of the BNCT beams.
- Sub-keV γ from cell-wall and dump capture is the main unknown of the BNCT case (§3).
- Micromegas occupancy from γ that make no leg is not in the model (the MEDAPP caveat also applies).
- No cosmic veto yet (a third of the BNCT background). A cosmic veto would help all of these beams.

## 7. Scorecard — 2026-11-09

| | TAPIRO (open channel) | LVR-15 BNCT | THOR | MITR FCB |
|---|---|---|---|---|
| beam exists today? | No: channel to be built (reactor runs; existing epithermal column calculated, status (ask)) | Yes, at least hardware (BNCT service (ask)) | Yes, clinical | Being removed |
| time to first beam | several years: safety case, licensing (Italian ISIN) (ESTIMATE) | ~1–2 years with arrangement | n/a | n/a |
| realistic for us? | **Yes in principle**: Italian national lab, not a user facility; ENEA bilateral route; MX17 has strong Italian ties. Sustained 50 d at 5 kW (ask) | commercial operator; arrangement via CVŘ; Czech collaborators (NPI) | clinical schedule rules it out for weeks of unrelated beam; Oct 2026 replacement talks | No |
| space/shielding/port | reactor hall (ask), exit at 2.2 m | existing treatment room 4 m from core (dimensions (ask)) | clinical room | — |
| cost | €100–300k for shutter/collimator (ESTIMATE); reactor work unknown | ~€50–100k (ESTIMATE) | — | — |
| radiation safety, ³He | HEU reactor site, security access for foreigners (ask); 5 kW source, field near the shield face (ask); pressurised ³He next to a reactor needs a safety case | operating controlled area | — | — |
| competition | ENEA programmes, low load | commercial irradiations, Mo-99 | patients | — |
| reach | 4.8×10⁻⁴ (ESTIMATE) | 1.05×10⁻³ | 0.9×10⁻³ | 1.2×10⁻³ (historical) |
| call | **PURSUE enquiry** | **KEEP AS BACKUP** | CLOSED for us (clinical) | CLOSED (beam being removed) |

**RA-6:** CLOSED for now (licence expiry 28 Jul 2026 unconfirmed, CNEA cuts; ask if reopened). **OSU:** a 2×10⁷ port would reach ~8×10⁻⁴ if its γ/n is ≲ 3 (flux grid); as measured it is thermal-rich (35 % thermal, 2.1×10⁷ total) and Ø32 mm, so ×15 below MEDAPP flux: WATCH.

**Compared with Birmingham (5.5×10⁻⁴, 6.7 d full Geant4) and FRANZ (3.3×10⁻⁴ design):** TAPIRO + Pb reaches a similar engine number but needs a reactor modification; LVR-15 is ×2–3 worse but could happen.

**To be top-3, TAPIRO needs:** a straight channel with ≥ 3×10⁷ n/cm²/s at the cell (flux grid), γ/n ≤ 3 behind ~5 cm of Pb, ENEA willing and licensed to modify the column and to run for a total of ~2–5 full-power weeks. Number to ask first: the column status and the maximum run length at 5 kW.

## 8. Next steps — 2026-11-09

1. **Ask ENEA (A. Santagata):** is the epithermal column still installed; thermal-column and window layout; channel diameters; sustained 5 kW operation; γ field measured at the column; openness to a modification.
2. **Ask CVŘ:** BNCT line and room availability; flux with the filter blocks removed; beam time for ~weeks.
3. Geant4: **N7, a sub-keV extension of N5** (log-flat 1 meV–1 keV neutrons, same geometry, forced collision off, with the wall-capture γ) to remove the §3 ×3 uncertainty; run with `MX17_Full_Geant` branch `soft`. Then a TAPIRO room model (reflector-face leak field + shield).
