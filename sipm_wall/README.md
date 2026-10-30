# sipm_wall: what reading the SiPM wall bar by bar buys

**Started 2026-10-30.** Today each SiPM wall is read in 8 channels: 4 groups of 4 bars, top and bottom. The
alternatives are every bar end (160 channels) or every SiPM (320). What does the extra granularity buy in physics?
The DAQ that reads it is in `../daq_trigger/SIPM_READOUT.md`.

## Read this first (2026-10-30)

- **Measured on Geant4, not guessed.** The raw LNL HitTrees store every SiPM-wall step (u, v, time, edep), so the
  per-bar readout can be emulated on events already simulated: X17 m = 16.7 (L1) and one live day of cosmic muons
  (L4), as built and with big plastics. The selection is the `lnl_merge` two-arm selection; the reference rows
  reproduce `lnl/FEASIBILITY_SIM.md` §4 (MM 15°: 576 vs 570 cosmics/day; MM 3°: 1 vs 1).
- **Verdict: at LNL, reading the walls bar by bar does not change the reach, once the plastics' PMT time is used
  for the time of flight.** The case for 160 channels is the trigger, the MM road at high-rate sites, the
  4 dark bars and a second independent timer (§4), not cosmic rejection.
- **What would have been the uplift: timing.** As built, a bar-end time at σ_t ≈ 0.25 ns (vs ~0.45 ns ganged) lets
  the time-of-flight veto alone leave 11 cosmics/day against ~110 IPC. The MM 15° segment cut, which costs 30 % of
  the X17, can then be dropped: days to 3σ ×0.65 against the reference (ganged, MM 15° + TOF).
- **But the plastic time does the same** (§2.2): TOF on the plastic PMT time at 0.25 ns also leaves 11 /day, and
  17 /day at 0.4 ns. The n_TOF plastics measured 0.14–0.29 ns (`nTof_x17/ntof_scint_recovery`). So the ×0.65 is
  available as built **without** un-ganging. The wall time becomes a cross-check, or the fallback if the plastic
  timing disappoints.
- **A finding for `lnl/` (not about the walls):** with any timer at ≤ 0.3–0.4 ns, TOF alone beats the analysis's
  reference "MM 15° + TOF": ×0.65 as built, ×0.78 with big plastics. The MM 15° pointing cut costs 25–30 % of the
  X17 and removes nothing that TOF and the E_sum window leave. (The big plastics' window already removes the
  cosmics; TOF alone leaves 25–37 /day there against ~2 000 IPC.) Worth folding into `lnl_geant.py`'s levels.
- **Per SiPM (320) adds nothing over per bar end (160)** in any number here.
- **The wall as a second space point is weak.** The line MM centroid → wall bar points to the true lepton direction
  only to σ68 ≈ 21–27° per bar (45° ganged), because the electrons scatter in the MM readout stack. The pointing cut
  barely touches cosmics. A muon crossing two arms is collinear to the bar width, but an X17 pair at 140° is itself
  only ~35 mm off collinear, so the collinearity veto gains ×1.1–1.4 at most.
- **Road for MM pile-up: the one real position gain.** A wall hit confines the lepton's MM cluster to **9 %** of the
  chamber per bar end (8 % per SiPM), against **25 %** ganged. Most of the gain is v from the top/bottom Δt
  (±7 vs ±15 cm), not the bar width. It matters where stray MM clusters are dense: at Birmingham (0.6 neutron-recoil
  clusters per arm per 1.2 µs, `birmingham/TARGET_GEANT.md` §7), the chance that a stray cluster lands in the road
  drops from 14 % to 5 %. Not yet turned into days (§5).
- **Estimates in force:** σ_t and σ_v per bar end and per SiPM, and the plastic σ_t for the big plates. Bench test S3
  (`../daq_trigger/SIPM_READOUT.md` §5) measures the first two; the big-plate prototype on the cosmic bench measures
  the third.

## 1. Method

`sim/lxplus/wall_reduce.py` (condor via `wall_pipe.sh`, 220 jobs, 2026-10-30) applies, per file, the `lnl_merge`
selection to the existing `parts_lnl`:
- an ok arm = a trigger leg (SiPM AND plastic ≥ 0.5 MIP) and an MM segment in the active area;
- ≥ 2 ok arms;
- the pair = the two with the most scintillator energy.

It then reads every `PlasticScint` step of the two pair arms from the raw HitTree and sums by bar: energy, earliest
time, energy-weighted local (u, v, w) and global position. The bar index is floor((u − pinwheel shift)/25 mm + 10):
hits sit within ±12.5 mm of their bar centre, bars 1–16 as built (`--sipm-readout 16 1`) and 0–19 with big plastics.
Merged tables: `/eos/experiment/ntof/data/x17/lnl/sel_wall/` (X17 32 565 / 231 556 events, cosmics 228 014 / 964 417).
Copy them with `sim/fetch_wall.sh`.

`wall_uplift.py` emulates each readout:

| readout | u | v (along the bar) | arm time |
|---|---|---|---|
| ganged 4 bars (n_TOF) | group centre (4 groups of 4) | truth + σ_v = 11.5 cm (n_TOF measured 10–13 cm) | earliest + σ_t = 0.45 ns (n_TOF control 0.4 ns) |
| per bar end (160 ch) | bar centre | σ_v = 4 cm (**estimate**) | σ_t = 0.25 ns (**estimate**) |
| per SiPM (320 ch) | bar centre | σ_v = 3 cm (**estimate**) | σ_t = 0.20 ns (**estimate**) |

- **Bar or group threshold:** 0.1 MeV. The highest-energy channel per arm gives the point.
- **The cuts:**
  - wall pointing: DCA to the spot of the line MM → wall, cut at 90 % of X17 arms;
  - collinearity: both wall points within C of the MM₁–MM₂ line, transverse to the beam, with C losing 3 % of X17;
  - TOF: `lnl_geant.pass_tof` with this σ_t;
  - MM 15°: as `lnl_geant`.
- **Window and energy:** 125–155°, E_sum 13–17 MeV (with LS as built).
- **days_rel:** days ∝ B/ε², with B = IPC + cosmics. The IPC passes like the X17 (both come from the spot), and is
  scaled from 110 /day (as built) and 1 480 /day (big plastics) at the reference level, ganged MM 15° + TOF.

## 2. Results

### 2.1 Cosmic rejection (`out/cosmic_rejection.csv`; per day in 125–155°, E_sum 13–17, 1 µA)

| | X17 eff | cosmics/day as built | days_rel | X17 eff | cosmics/day big plastics | days_rel |
|---|---|---|---|---|---|---|
| after trigger + E_sum + window | 1 | 3 665 | 14 | 1 | 462 | 0.90 |
| MM 15° | 0.73 | 576 | 4.9 | 0.76 | 67 | 1.01 |
| MM 3° (an MM upgrade) | 0.81 | 1 | 0.73 | 0.82 | 2 | 0.90 |
| **ganged: MM 15° + TOF (reference)** | 0.70 | 22 | **1** | 0.74 | 3 | **1** |
| ganged: TOF alone (0.45 ns) | 0.97 | 144 | 1.18 | 0.97 | 49 | 0.78 |
| per bar end: MM 15° + TOF | 0.70 | 1 | 0.84 | 0.73 | 0 | 1.01 |
| **per bar end: TOF alone (0.25 ns)** | 0.97 | 11 | **0.65** | 0.96 | 27 | **0.78** |
| **plastic PMT time: TOF alone (0.25 ns), walls ganged** | 0.96 | 11 | **0.65** | 0.95 | 27 | **0.79** |
| per SiPM: TOF alone (0.20 ns) | 0.96 | 11 | 0.65 | 0.95 | 25 | 0.78 |
| per bar end: wall pointing | 0.83 | 2 278 | 13 | 0.84 | 178 | 0.97 |
| per bar end: wall collinearity | 0.98 | 2 612 | 11 | 0.98 | 413 | 0.91 |

One live day of cosmics: entries of 0–2 are single events.

### 2.2 How it scales with the resolutions (`out/resolution_scan.csv`, `out/figures/cosmics_vs_resolution.png`)

- **TOF alone, as built:** 10–13 cosmics/day for σ_t ≤ 0.3 ns, then 62 at 0.4, 310 at 0.5 and 1 270 at 0.7. The
  step between 0.3 and 0.5 ns is exactly where ganged and per-bar sit. **So the result rests on σ_t; measure it.**
- **TOF alone, big plastics:** 25–37 /day up to 0.4 ns, 71 at 0.5, against ~2 000 IPC/day: harmless at any σ_t.
- **The plastic time instead of the wall's** (`sigma_t_plastic` rows; truth = earliest plastic hit, its light
  propagation assumed corrected with the MM position, `trigger_scint` §4): as built 11 /day at ≤ 0.3 ns, 17 at 0.4,
  62 at 0.5. It is slightly better than the wall at the same σ_t, because the plastics sit ~6 cm further out, so the
  muon's flight between arms is longer. Big plastics: 25–38 /day up to 0.5 ns.
- **Pointing + collinearity against σ_v:** almost flat as built. With big plastics, 230 → 70 /day from σ_v = 15 to 1 cm:
  nothing that TOF does not already do.

### 2.3 The wall as a direction (`out/direction_resolution.csv`)

σ68 of the angle between the line MM centroid → wall point and the lepton's true direction (X17, as built / big
plastics, higher-energy / lower-energy arm):

| readout | arm 1 | arm 2 |
|---|---|---|
| ganged | 43–46° | 44–47° |
| per bar end | 21–23° | 25–27° |
| per SiPM | 18–20° | 23–24° |
| per bar, perfect v | 12° | 18–19° |

Multiple scattering in the MM readout stack and the wall container sets the floor (~12–19° even with a perfect v).
The wall does not give the "3° segments" that kill cosmics in `lnl/FEASIBILITY_SIM.md`. It cannot replace the
vertex-to-hit chord for the opening angle either (that chord is good to 0.2–0.4° from a 2 mm spot).

### 2.4 The MM road (`out/mm_road.csv`)

Half-widths containing 95 % of X17 MM centroids around the spot → wall-point line, and the road's share of the MM
active area (399.4 × 359.9 mm):

| readout | ±u | ±v | road / MM | P(a stray cluster in the road) at 0.6 per arm |
|---|---|---|---|---|
| ganged | 56–60 mm | 152–154 mm | 24–25 % | 13–14 % |
| per bar end | 46–47 mm | 69–72 mm | 9 % | 5 % |
| per SiPM | 46–47 mm | 59–60 mm | 8 % | 4–5 % |

## 3. Why these σ values, and what would change them

- **Ganged** is measured: `nTof_x17/mx_july_beam_qa/slides/vertical_slides.tex` (σ_y 10–13 cm from Δt or the
  amplitude ratio, v_eff = 15 cm/ns, λ_eff = 1.0–1.6 m) and `ntof_scint_recovery/ANALYSIS_PLAN.md` (wall time 0.4 ns
  in the control, 2.5–4.5 ns in beam).
- **Per bar end:** one bar's SiPMs on one channel, against 4 bars' worth on today's channel. That means ¼ of the
  capacitance and dark noise (if they are ganged passively), the same light, and a dedicated SiPM front end
  (A5204: picoTDC; 55 ps FWHM at 1 p.e.). σ_v = 4 cm corresponds to σ(Δt) ≈ 0.53 ns. **Estimate.** The scans
  cover 0.1–1 ns and 1–15 cm.
- **Per SiPM:** the 2 SiPMs of a bar end timed separately and averaged: at most √2 on the photostatistics term.
  **Estimate.**
- **What we don't know:** the light yield per bar end at the SiPM (p.e. per MIP), and whether the ganging is passive
  (`../daq_trigger/SIPM_READOUT.md` §1).

## 4. What the study does not count (and why it may still decide for 160)

- **The trigger.** A per-bar top·bottom AND is 99.8 % pure MIP (n_TOF). Thresholds no longer have to sit above the
  summed noise of 4 bars. The board makes the wall OR, so M1 and the sum FIFOs go (`SIPM_READOUT.md` §3).
- **The 4 dark bars.** Lighting all 20 bars is ×1.4 trigger acceptance with big plastics (`trigger_scint` §bottom
  line 3). It is the same board work, but a 5 × 4 ganging would give it too, so it is not credited here (the
  big-plastic samples already read 20 bars).
- **Per-channel occupancy at high-rate sites.** Birmingham's busiest bar sees 7×10⁴ /s above the leg threshold. A
  ganged channel sums 4 bars (×4 pile-up); a SiPM channel halves it again.
- **Calibration:** per-bar gain, offsets and v_eff from cosmics, against a 4-bar average.
- **A second timer** in each arm, independent of the plastic, for the TOF and for the event-time window against
  randoms.
- **Not studied:** two leptons in one arm (same-chamber pairs, conversions). Bar multiplicity could tag them.
  Neither are extended targets (ILL cell, Birmingham 30 bar cell), where the wall direction might help find the
  vertex. At 20–25° it is unlikely to beat an assumed centre.

## 5. Next

1. **Bench test S3** (`SIPM_READOUT.md` §5): σ_t and σ_v per bar end on cosmics. That settles §2.1 as built.
2. **`lnl/`:** add a "TOF only" level (plastic time) to `lnl_geant.py` and redo the reach. §2.1 says ×0.65 as
   built, ×0.78 with big plastics against MM 15° + TOF.
3. **Birmingham / FRM II:** emulate the MM road with the `bham` neutron-recoil MM clusters (R-runs) to turn §2.4 into
   days.
4. Same-arm pairs and bar multiplicity on the L1/L2 samples, if the same-chamber analysis (nTof_x17
   `SAME_CHAMBER_PAIRS.md`) needs it.

## Files

| file | what |
|---|---|
| `wall_uplift.py` | the emulation and every table / figure below |
| `sim/lxplus/wall_reduce.py`, `wall_merge.py`, `wall_pipe.sh` | the lxplus reduction (copies in `…/work/git/x17_lnl/analysis/sipm_wall/`) |
| `sim/fetch_wall.sh` | copies the merged tables to `sim/sel/` (gitignored) |
| `out/cosmic_rejection.csv` | §2.1 |
| `out/resolution_scan.csv`, `out/figures/cosmics_vs_resolution.png` (+ `.csv`) | §2.2 |
| `out/direction_resolution.csv` | §2.3 |
| `sim/sel/*_tplast.npz` | the plastic and wall truth times per pair arm, from `lnl/…/sel_v3` (same rows), for §2.2 |
| `out/mm_road.csv` | §2.4 |

```bash
bash sipm_wall/sim/fetch_wall.sh
~/PycharmProjects/nTof_x17/.venv/bin/python sipm_wall/wall_uplift.py     # ~10 min (1M cosmic events)
```
