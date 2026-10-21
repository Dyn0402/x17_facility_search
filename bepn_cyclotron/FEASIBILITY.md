# Cyclotron ⁹Be(p,n) — X17 feasibility with its own Geant4 beam background

Facility record: `FACILITY.md`. Slides: `deck/build_deck.py` → `out/bepn-cyclotron-x17-feasibility.html`
(built, not yet published). Simulation and analysis: `bepn_beam.py`, `bepn_reach.py` (on top of
`survey/soft_sim/`, shared with `frm2_medapp/` and `birmingham/`).

## 0. Answer — 2026-10-21

**At NPI Řež's TR-24 cyclotron (18 MeV protons on its bare Be converter, cell 2 m downstream at 0°,
Ø8 cm collimator, beam throttled to ~0.19 mA), the reach is X17/IPC = 8.7×10⁻⁴ at 3σ in 50 days (big
plastics; as built 1.3×10⁻³): ×1.7 past ATOMKI's ⁴He value, ~17 days of beam to reach the ATOMKI
strength.** It is a weaker candidate than Birmingham (3.3×10⁻⁴) or FRM II MEDAPP (4.2×10⁻⁴), for one
reason: 57 % of the neutrons are above 2.75 MeV. They bring no ATOMKI-window signal, but they fire the
trigger plastics (~3×10⁵ legs per arm per second at full current), and the DREAM dead time caps the
usable rate (live 0.45). With the X17 signal counted at every E\* (the NFS convention), 5.2×10⁻⁴.

| 50 d, big plastics (as built) | E\* ≤ 22 MeV | all E\* | throttle | limit |
|---|---|---|---|---|
| **NPI TR-24, 18 MeV, 0°, 2 m** | **8.7×10⁻⁴** (1.3×10⁻³) | 5.2×10⁻⁴ (7.4×10⁻⁴) | 0.63 | DREAM live time |
| NPI TR-24, 18 MeV, 130°, 2 m | 8.9×10⁻⁴ (2.3×10⁻³) | 4.9×10⁻⁴ | 1 | statistics + live |
| NPI TR-24, 24 MeV, 0°, 2 m | 2.3×10⁻³ (2.9×10⁻³) | 1.2×10⁻³ | 0.16 | correlated beam (> 16 MeV n) |
| NPI TR-24, 24 MeV, 130°, 2 m | 9.8×10⁻⁴ (2.1×10⁻³) | 4.9×10⁻⁴ | 1 | statistics + live |
| NPI TR-24, 24 MeV, 130°, 1 m | 9.7×10⁻⁴ (1.1×10⁻³) | 4.8×10⁻⁴ | 0.32 | DREAM live time |
| KURNS HM-30, 30 MeV 1 mA, 130°, 2 m | 1.5×10⁻³ (1.5×10⁻³) | 6.8×10⁻⁴ | 0.25 | correlated beam + live |
| KURNS HM-30, 0°, 2 m | 5.0×10⁻³ (5.8×10⁻³) | 2.4×10⁻³ | 0.025 | correlated beam |
| NPI U-120M, 18 MeV, 35 µA, 0°, 3 m (collimated beam exists) | 2.8×10⁻³ (9.3×10⁻³) | 1.6×10⁻³ | 1 | statistics |

14 days at the baseline: 1.6×10⁻³ (just short of ATOMKI). The survey's scaled bracket was 1.3×10⁻³ –
4.5×10⁻³ for 30 MeV/1 mA at 1 m (`survey/SURVEY.md` §4.2): the Geant4 answer at the same machine
(1.5×10⁻³ at 130°) sits at the bracket's optimistic end, and the best configuration is a *lower* proton
energy, not a bigger machine.

## 1. Beam model — 2026-10-21

`bepn_beam.py` → `out/bepn_spectra.{csv,png}`, `out/bepn_angles*.csv`, `out/bepn_beam.csv`,
`out/bepn_gamma.{csv,png}`, `out/bepn_anchors.csv`.

- **Nuclear data, not a stand-in shape.** ENDF/B-VIII.0 p + ⁹Be (LANL LA150 evaluation; GNDS from
  Geant4's LEND data on CVMFS): ⁹Be(p,n)⁹B to six levels (CM Legendre distributions) and the MT 5
  continuum (neutron multiplicity, Kalbach-Mann energy-angle tables, Kalbach-1988 slope), photons.
  Thick target: Bethe stopping in Be, 0.1 MeV slices from 2.06 MeV to E_p; 4×10⁴ neutrons per slice;
  non-relativistic CM→lab.
- **Anchors:** 0° yield above 0.4 MeV at 16 MeV 1.44×10⁻³ n/sr/p vs 1.45×10⁻³ (Brede-based, Fenyvesi);
  4π yield at 30 MeV 0.0300 n/p vs 0.0304 (Sumitomo/KURRI 1.9×10¹⁴ n/s at 1 mA). NPI's design
  "5×10¹² n/s/sr forward" at 24 MeV, 0.3 mA is ×1.5 below the model's θ < 8° yield and matches its 30–40°
  value. Peaks at ~1.5 and ~6 MeV in the spectra come from the evaluation's MT 5 tables (sequential decay
  through ⁹B/⁸Be states); measured thick-target spectra are smoother **(check with Majerle 2023)**.
- **Hard at every angle:** 31–48 % below 2.75 MeV, for every E_p and θ (the evaporation part is
  isotropic and so is the 2.75–10 MeV bulk, to within ×2). Going to 130° removes most of the > 10 MeV
  tail (6 % at 24 MeV) but costs ×4 in flux. Going to 18 MeV removes everything above 16.3 MeV.
- **Through the Ø8 cm spot at 2 m, full current:** 4.8×10⁹ n/s (18 MeV, 0°), 9.3×10⁹ (24 MeV, 0°),
  2.3×10⁹ (24 MeV, 130°), 5.0×10¹⁰ (HM-30, 0°). Target γ: 3.1×10⁻⁴ γ/p, lines ≤ 7 MeV, ~5×10⁷ γ/s
  through the spot: < 0.2 % of the singles.

## 2. Geant4 — 2026-10-21

No new run. The neutron and γ rows of the broad-band runs are re-weighted to each source
(`bepn_reach.py`, the `soft_reach.py` engine):

- **≤ 20 MeV:** N5 (log-flat 1 keV–20 MeV, forced collisions, 9×10⁷ per hardware set) and G5/G6.
- **> 20 MeV** (only 24 MeV at θ < 45° and the HM-30): the NFS forced run N4, generated on the NFS
  spectrum (0.1–40 MeV), each energy counted once. N4 has no leg or hardware-trigger tables: its legs are
  its ok singles × 10.3 (the leg/ok ratio of N5 at 10–20 MeV) and its triggers its two-arm ok events.
  This is why 18 MeV is the clean baseline: nothing above 16.3 MeV, so N5 alone carries it.
- **What the fast neutrons do:** > 1.7 MeV neutrons fire the back plastic. At the baseline, full
  current, 9.1×10³ ok singles and **2.9×10⁵ legs per arm per second**: random two-arm triggers (2τ = 20 ns)
  are ~10⁴/s, and DREAM (298 µs per event) is live 26 % of the time. The optimum throttle (0.63) trades
  statistics against live time: live 0.45, 3.9×10³ random triggers/s.
- **Correlated beam background** comes from > ~16 MeV neutrons: none at 18 MeV (0.02 per day in the
  window), 1.8×10⁵ per day at 24 MeV, 0° (the NFS limit again), 25 per day at 24 MeV, 130°. MC statistics
  are thin (5–29 events pass all cuts per sample; factorised as for NFS).

## 3. Reach — 2026-10-21

`bepn_reach.py` → `out/bepn_reach.csv`, `out/bepn_components.csv`, `out/bepn_throttle.csv`,
`out/bepn_reach_fig.{png,csv}`. DC beam: one θ histogram; vertex DCA < 60 mm, E_sum > W/2.

Baseline (NPI 18 MeV, 0°, 2 m), best throttle, per day in θ = 100–150°, big plastics:

| X17 at ATOMKI | IPC | cosmics (no veto) | accidentals | correlated beam |
|---|---|---|---|---|
| 60 | 7 170 | 2 340 | 890 | 0.02 |

X17 is 0.8 % of the IPC in the window (Birmingham: 1.9 %): half the IPC comes from E\* > 22 MeV, where
the ATOMKI-like signal is not counted. Statistics-only floor (live 1, no beam background): 4.2×10⁻⁴.

**Levers:**
1. **A faster DAQ** (τ/4, 5 samples): baseline 6.2×10⁻⁴ (no throttle, live 0.57); 24 MeV at 1 m 6.7×10⁻⁴
   (`out_tau4/`).
2. **A higher leg threshold** (2.5–3 MeV, `trigger_scint/TRIGGER_OPTIONS.md` §8) would cut the
   proton-recoil legs that dominate here; not simulated.
3. **A cosmic veto**: cosmics are a quarter of the background.
4. Not a bigger machine: the HM-30's extra current is spent on its harder tail.

## 4. Against

- **The spectrum.** 57 % of the neutrons are above the ATOMKI window, at every angle. ⁷Li(p,n) near
  threshold (Birmingham) puts all of them below 1.1 MeV. A Be(p,n) source competes only where it is the
  one available.
- **The converter is a sample irradiator.** NPI's high-power target is built to put samples 20 mm from
  the Be; its status in 2026 is unknown, and a collimated port through the TR-24 vault wall does not exist
  (U-120M has one, at ~1/10 the current: 2.8×10⁻³).
- **The 4π field** (§5).
- **No BNCT cyclotron has a fast port**: KURNS's HM-30 is moderated for epithermal beams.

## 5. The shield the 4π field needs — 2026-10-21 (estimate, not Geant4)

`bepn_beam.shield()` → `out/bepn_shield.csv`. With no wall, one arm (75 × 75 cm) 2 m from the Be at 0°
sees 5.4×10¹¹ n/s (18 MeV, 0.3 mA), ×110 what goes through the cell. To keep its singles below 10 % of the
beam's own (915/s per arm), at 10⁻⁴–10⁻³ ok singles per 1–20 MeV neutron entering an arm, the transmission
must be 2×10⁻⁵–2×10⁻⁶: **~1.0–1.2 m of borated PE + Fe (TVL ~20 cm) or 1.7–2.0 m of concrete (TVL ~35 cm)**.
That is a wall between rooms, not a local shield: the set-up must sit beyond the vault wall, on a
collimated port. Both TVLs and the singles per entering neutron are stand-ins.

## 6. What it needs, and what is not settled

1. **A collimated port through the TR-24 vault wall** (or U-120M's existing collimated beam at higher
   current), the arms ≥ 2 m downstream, a dump behind (ask NPI).
2. Status of the high-power Be converter, and its usable current at 18 MeV (ask NPI).
3. A measured thick-target spectrum at 18–24 MeV to replace the LA150 model (NPI has TOF data:
   Majerle et al. 2023).
4. Not simulated: the wall, the room, the target backing and cooling water (they add a moderated
   component: more soft neutrons per fast one, likely helping), air in front of the cell.
5. MC statistics of the correlated term above 16 MeV (thin; irrelevant at 18 MeV).
6. The same physics question as everywhere: X17/IPC for E1 capture at E\* = 20.6–22 MeV.
