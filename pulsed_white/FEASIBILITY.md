# Pulsed white neutron sources: X17 feasibility with time of flight

Facility record: `FACILITY.md`. Slides: `out/pulsed-white-x17-feasibility.html` (`deck/build_deck.py`; built, not published).
Beam model and reach: `pw_beam.py`, on the LANSCE WNR engine.

## 0. Answer (2026-11-09)

Dylan's rule for the overall call: only existing beams count for now, no money for new machines, no facility contact yet.

**CSNS Back-n was closed for the wrong reason, and GELINA's closure stands.**

- **Back-n: WATCH.** The wall is not Micromegas occupancy. It is one DREAM readout per 25 Hz pulse, filled by random two-arm triggers. With today's DAQ the reach is 3.0×10⁻³ (ES#2), which confirms the catalogue's 3.6×10⁻³. If the whole time-of-flight window is read as one long event, **ES#2 at today's 185 kW reaches 9.4×10⁻⁴ in 50 days (big plastics, 20 d to ATOMKI; as built 2.5×10⁻³)**, on its statistics floor (8.9×10⁻⁴) and without a throttle. ES#1 reaches 8.4×10⁻⁴ (16 d) but at occupancy 0.93, where the exponential correction is not reliable. This needs two things nobody has shown: that DREAM can run that readout, and that it survives the γ flash (§5).
- **GELINA: CLOSED as a host (dominated).** With the real source strength and spectrum the catalogue's 3.2×10⁻³ improves, but only to 1.2×10⁻³ (33 d), and that is an upper bound on the flux with no flash loss. With the measured 0.87 µs chamber recovery it is 3.0×10⁻³ (201 d). WNR under the same two assumptions is 8.4×10⁻⁴ and 1.8×10⁻³. "Below WNR" is confirmed.
- **nELBE, RPI, KURNS-LINAC, J-PARC ANNRI: CLOSED.** **CSNS-II (500 kW)** is not an existing beam, so it does not count; for the record it would give 6.2×10⁻⁴ at ES#2 (8.6 d) with the full-window readout.

| 50 d, E\* ≤ 22 MeV | big plastics | days to ATOMKI | as built | limiting wall |
|---|---|---|---|---|
| **Back-n ES#2, 185 kW, full-window readout (ASSUMED mode)** | **9.4×10⁻⁴** | **20** | 2.5×10⁻³ | statistics (IPC floor 8.9×10⁻⁴), then the flash |
| Back-n ES#1, 185 kW, full-window readout (ASSUMED mode) | 8.4×10⁻⁴ | 16 | 2.1×10⁻³ | Micromegas occupancy 0.93 |
| Back-n ES#2, 185 kW, today's DAQ | 3.0×10⁻³ (throttle 0.15) | 198 | 2.9×10⁻³ | DREAM: one readout per pulse |
| Back-n ES#1, 185 kW, today's DAQ | 3.2×10⁻³ (throttle 0.07) | 224 | 3.1×10⁻³ | DREAM: one readout per pulse |
| GELINA 10 m, flux upper bound, no flash loss | 1.2×10⁻³ | 33 | 3.1×10⁻³ | statistics |
| GELINA 10 m, flux upper bound, 0.87 µs flash cut | 3.0×10⁻³ | 201 | 8.3×10⁻³ | the flash, then statistics |
| GELINA 30 m (station exists), flux upper bound | 3.5×10⁻³ | 270 | 1.1×10⁻² | statistics |
| WNR 90L 10 m, no flash loss (published) | 8.4×10⁻⁴ | 16 | 2.4×10⁻³ | statistics |
| WNR 90L 10 m, 0.87 µs flash cut (new) | 1.8×10⁻³ | 73 | 6.1×10⁻³ | the flash, then statistics |

With "all E\*" (X17/IPC constant at every E_n), the headline rows do not change for big plastics (Back-n ES#2 9.4×10⁻⁴, GELINA 10 m 1.2×10⁻³). As built, Back-n ES#2 is 2.5×10⁻³ and GELINA 10 m without a flash loss is 2.9×10⁻³.

**What would make Back-n top-3:** a demonstrated long beam-synchronous DREAM readout, a flash dead time below about 3 µs at ES#2 (with whatever Pb filter that needs), and a real way to bring a 30 bar ³He cell to Dongguan. Even then it trails Birmingham (5.5×10⁻⁴, 6.7 d, full Geant4). **The new finding that also touches WNR:** the published 8.4×10⁻⁴ assumes no flash loss. The same 0.87 µs cut gives 1.8×10⁻³, which no longer reaches ATOMKI in 50 days.

## 1. Engine and validation (2026-11-09)

`pw_beam.py` imports `lansce_wnr/wnr_beam.py` and changes three things per source: the beam and true period, the DREAM model for single-pulse sources, and a flash cut.

Reproduced before any new number (`--check`):

| row | here | published |
|---|---|---|
| WNR 90L 10 m, big plastics, E\* ≤ 22 | 8.421×10⁻⁴ | 8.421×10⁻⁴ |
| WNR 90L 10 m, as built, E\* ≤ 22 | 2.396×10⁻³ | 2.396×10⁻³ |
| Birmingham `bham_28_2m_pb5`, big plastics (soft_reach) | 3.318×10⁻⁴ | 3.318×10⁻⁴ |
| Birmingham `bham_28_2m_pb5`, as built (soft_reach) | 1.001×10⁻³ | 1.001×10⁻³ |

One difference is expected: WNR as built with all E\* gives 2.40×10⁻³ against the published 2.04×10⁻³, because this scan offers only the gates 0.2–2.75 and 0.2–25 MeV. The published value uses a 0.2–6 MeV gate.

## 2. The beams (2026-11-09)

- **GELINA:** 3.4×10¹³ n/s at 100 µA into 4π (JRC), giving 1.35×10⁸ n/s through Ø8 cm at 10 m. This replaces the catalogue's 2.5×10¹³ n/s and n_TOF spectrum. **The flux is an upper bound (isotropic, no moderator shadowing).** The measured flux at a station could not be retrieved; Ene et al. 2010 has it, but the full text was out of reach. Shape: a Watt spectrum, as an ESTIMATE of "peak at 1–2 MeV". Maxwellians with T = 0.8 and 1.5 MeV give 1.10×10⁻³ and 1.27×10⁻³ without a flash loss, 2.2×10⁻³ and 3.1×10⁻³ with the cut. Half the bound (f_dir 0.5, ESTIMATE): 1.6×10⁻³, or 4.0×10⁻³ with the cut. At 40 µA instead of 100: 1.8×10⁻³, or 4.5×10⁻³ with the cut.
- **Back-n:** Tang et al. 2021 Table 1, measured, per 100 kW, scaled to 185 kW. The spectrum is the measured per-decade one in `survey_yield.py`. 6.4×10⁸ n/s at ES#1 Φ50, 3.6×10⁸ at ES#2 Φ60. 2.6×10⁷ and 1.4×10⁷ neutrons per pulse.
- **Frame overlap:** none in the window at 800 Hz or 25 Hz.
- **Figure:** `out/pw_spectra.png`.

## 3. Pile-up neutrons, per pulse (2026-11-09)

The time-of-flight window selects 0.2–2.75 MeV, so faster neutrons have left the 1 µs Micromegas memory before most of the window. The occupancy is set by the window neutrons themselves. `out/pw_pulse_table.csv`, full beam:

| | neutrons per pulse | window after the flash | MM occupancy | gated triggers per pulse | DREAM live, one readout per pulse |
|---|---|---|---|---|---|
| GELINA 10 m (bound) | 1.7×10⁵ | 0.4–1.6 µs | 0.025 | 0.30 | 0.87 |
| GELINA 30 m (bound) | 1.9×10⁴ | 1.3–4.8 µs | 0.003 | 0.001 | 1.00 |
| Back-n ES#1, 185 kW | 2.6×10⁷ | 2.4–8.9 µs | 0.93 | 175 | 0.006 |
| Back-n ES#2, 185 kW | 1.4×10⁷ | 3.3–12 µs | 0.074 | 47 | 0.021 |
| WNR 90L 10 m | 2.6×10⁴ | 0.4–1.6 µs | 0.040 | macropulse model | 0.98 |

So the catalogue's reason is wrong for ES#2: the occupancy is 0.07 at the full beam. The survey's ×13 throttle comes from the DAQ, once the DREAM limit is counted properly.

GELINA's 800 Hz does help as expected: the beam never reaches the DREAM wall. At 100 µA the live fraction is 0.87 at 10 m under the conservative one-trigger-per-pulse count, and 1.0 if the 1.2 µs readout simply contains all the triggers of that pulse (1.14×10⁻³ against 1.22×10⁻³).

## 4. The configurations scanned (2026-11-09)

`out/pw_reach.csv` (keys ending `_nf`: no flash loss; others: 0.87 µs cut, plus the double-bunch 410 ns for Back-n).

- **Distance (GELINA):** 10, 15, 30, 50, 60 m. 15 m is not a listed station. Best is 10 m without a flash loss. With the 0.87 µs cut, the optimum moves to about 15 m (2.4×10⁻³), but the real stations are 10 and 30 m (3.0 and 3.5×10⁻³).
- **Station and collimation (Back-n):** ES#1 Φ50, Φ20; ES#2 Φ60, Φ30. The small spots are statistics-limited at 5.8 and 6.2×10⁻³.
- **Bunch mode:** single bunch halves the protons per pulse and gives the same reach as the throttled double bunch (3.15 against 3.17×10⁻³): the wall is per pulse.
- **Throttle:** 19 points from 10⁻³ to 1, best chosen per row.
- **The upstream irradiation platform (hypothetical, L ≈ 30 m ESTIMATE):** 4.2×10⁻³, throttled ×0.015, occupancy 1.0. Being closer does not help.
- **Full-window readout:** one beam-synchronous event covering the window, so every trigger in a pulse is kept. ES#2 needs about 150 samples at 60 ns, inside the 512-cell DREAM buffer. Since τ ∝ samples, τ ≈ 2.2 ms, a 5.6 % loss at 25 Hz that is **not included** (about 3 % on the reach). ASSUMED: this mode has not been run. Accidentals rise (76 per day at ES#2 against 2 600 IPC, 319 against 3 400 at ES#1) and are included.
- **Pb filter (ESTIMATE, not simulated):** √flux scaling with the uncollided 0.20 /cm of `soft_reach.py` gives 1.3×10⁻³ (3 cm) to 1.5×10⁻³ (5 cm) at ES#2. Tang 2021 says Pb reduces the neutron flux "only modestly", so the uncollided figure is probably pessimistic.
- **Cell:** only the 30 bar × 40 cm cell. N4/N5 do not cover the n_TOF capsule, so it was not computed.
- **GELINA at 150 MeV:** not scanned; the yield is not published.

## 5. The γ flash decides the short paths (2026-11-09)

This is measured input the WNR study did not have. At n_TOF the Micromegas chamber recovers 0.87 µs after the flash (`nTof_x17/ntof_processing/mm_flash`), but the DREAM front end rails for 0.5 ms to over 25 ms, depending on the resistive HV, with dead time ∝ Q^1.2 (`nTof_x17_DAQ/docs/flash_recovery_run57_HV_map_2026-07-20.md`, `nTof_x17/ntof_july_analysis/flash_charge/`).

`out/pw_flash_scan.csv`, big plastics, 50 d, reach against dead time after the flash:

| dead time | 0 | 0.87 µs | 2 µs | 5 µs | 10 µs | 30 µs |
|---|---|---|---|---|---|---|
| Back-n ES#2, full-window | 9.4×10⁻⁴ | 9.4×10⁻⁴ | 9.4×10⁻⁴ | 1.3×10⁻³ | 2.8×10⁻³ | dead |
| Back-n ES#1, full-window | 8.4×10⁻⁴ | 8.4×10⁻⁴ | 8.4×10⁻⁴ | 1.3×10⁻³ | dead | dead |
| GELINA 10 m | 1.2×10⁻³ | 3.0×10⁻³ | dead | dead | dead | dead |
| GELINA 30 m | 3.5×10⁻³ | 3.5×10⁻³ | 5.9×10⁻³ | dead | dead | dead |
| WNR 90L 10 m | 8.4×10⁻⁴ | 1.8×10⁻³ | dead | dead | dead | dead |

**ESTIMATE of the flash size, neutrons per pulse as a proxy.** Relative to n_TOF EAR2 (about 7×10⁷ above 0.1 MeV per pulse, derived from the survey): Back-n ES#2 ×0.2, ES#1 ×0.36, GELINA 10 m ×2×10⁻³, WNR ×4×10⁻⁴. Scaling the shortest measured DREAM recovery (0.5 ms) as Q^1.2 gives about 70 µs for unfiltered ES#2, longer than its window. It would have to drop about ×25 in dead time, ×15 in charge, for ES#2 to work. A 3–10 cm Pb absorber is the existing Back-n option, and is of the right order, but this extrapolates far below the measured range. For GELINA the proxy is a lower bound, because an electron machine makes many more γ per neutron. The flash is modelled only as a time cut.

## 6. Scorecard (2026-11-09)

| | CSNS Back-n ES#2 | JRC GELINA 10 m |
|---|---|---|
| Beam exists today? | Yes, 185 kW (Tang 2021; survey Mar 2026) | Yes; about 100 h/week, multi-user (JRC page) |
| Time to first beam | Unknown: next CSNS call **(ask)**; apparatus shipped to China | Next EUFRAT call probably early 2027 **(ask)**; 2026 closed 28 Feb (one source) |
| Access realistic for our group? | Uncertain: foreign users existed in 2019; terms today **(ask)** | Uncertain: EU/Euratom-associated lead institution, Euratom Annex I relevance required |
| Space, shielding, port work | Two existing halls with low off-beam background (0.01 n/cm²/s at ES#2, Tang 2021); room for 2×2 m arms **(ask)** | Nothing public about hosting a 2×2 m apparatus at 10 m **(ask)** |
| Cost estimate (ESTIMATE) | Shipping, travel, a Pb filter, DAQ effort; no new machine | No access fee (0 €/AU), travel and shipping |
| Radiation safety, ³He target | 30 bar ³He pressure vessel in a foreign user facility **(ask)** | Same, in a nuclear site **(ask)** |
| Competition for beam time | About 50 experiments a year; ES#2 can run parasitically in some modes | 50 AU per call, 8 AU average: 12 weeks for 50 d would be heavy |
| Access restriction, plain fact | Site in China; export-control check for each home institution | Euratom relevance; EU-based lead; users cannot operate the facility themselves |
| Reach, best honest | 9.4×10⁻⁴ if both ASSUMED items hold; 3.0×10⁻³ today | 3.0×10⁻³ (flash cut, flux bound); 1.2×10⁻³ only with no flash loss |
| **Overall call** | **WATCH** | **CLOSED (dominated by WNR)** |

Comparison: Birmingham 5.5×10⁻⁴, 6.7 d (full Geant4 with room); FRANZ 3.3×10⁻⁴ at its 20 mA design, 2.2×10⁻³ at its licence; FRM II MEDAPP 4.2×10⁻⁴ (reactor off since 2020). The Birmingham full-room study moved its reach ×1.7 from the beam-only number, so the figures here are beam-only and could worsen similarly.

GELINA in 50 days of beam means 12 access weeks at ~100 h/week, 1.5 average projects. Beam days here mean full days of beam.

## 7. Caveats (2026-11-09)

1. **Beam-only.** N4/N5 re-weighting with a vacuum flight tube and the NFS spot. No room, dump or air. Birmingham's lesson applies.
2. **The flash** is a window cut, uniform inside each E_n bin. The ionisation in the drift from the flash, and the DREAM rail, are not simulated.
3. **The exposure correction exp(−2·occ)** is the survey convention, and it is not reliable near occupancy 1. That is why ES#2, not ES#1, is the headline.
4. **The GELINA flux is an upper bound**; the spectrum is a stand-in.
5. **Double-bunch time-of-flight smearing** (410 ns) is not applied to the bins. It is small against the 2.4–12 µs window but not zero; the single-bunch row is the control.
6. **Above 45 MeV** the response is the 25–45 MeV value (K_HI = 1). Back-n has more neutrons up there than WNR at 90°; the window gate removes them in time, but this was not varied here.
7. **Physics:** X17/IPC for E1 capture at E\* 20.6–22 MeV against ATOMKI's p + t (`survey/SURVEY.md` §6.3).

## 8. Next steps (2026-11-09)

No facility contact for now (Dylan). What can be done without one:

1. **Bench test:** a beam-synchronous DREAM readout of about 150 samples on the pulser. Dead time and data volume at 25 Hz.
2. **Geant4 (specified, not run):** on lxplus, the MX17_Full_Geant `soft` branch with `--beam-particle gamma`. A flash spectrum at ES#2 with 0, 3, 5, 10 cm of Pb upstream; record deposited charge per Micromegas per pulse, for comparison with the n_TOF `flash_charge` scale.
3. **Re-state the WNR note** with the flash cut (§5), or at least flag it. It sets WNR's rank.

Questions held until contact is allowed: Back-n hall size, Pb filter options, foreign-user terms and ³He rules; GELINA direct flux at 10 m (Ene 2010), beam size, and flash.
