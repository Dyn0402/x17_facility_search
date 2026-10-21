# FRANZ — X17 feasibility with the shared Geant4 soft-beam background

Facility record: `FACILITY.md`. Slides (built locally, not published): `out/franz-x17-feasibility.html`
(`deck/build_deck.py`). Simulation and reach engine: `survey/soft_sim/` (shared with `frm2_medapp/`,
`birmingham/`); the FRANZ sources, the duty factor and the licence cap are in `franz_beam.py`.

## 0. Answer — 2026-10-21

**At its design intensity (20 mA DC at 2.0 MeV, 10¹² n/s, which is also the licence's neutron limit) on a
thin Li target, with the ³He cell 0.5 m from the target: X17/IPC = 3.3×10⁻⁴ at 3σ in 50 days (big plastics;
as built 9.4×10⁻⁴). ×4.5 past ATOMKI ⁴He; ~2.4 days of beam reach the ATOMKI strength. That ties Birmingham.**
But FRANZ has not yet run at 2 MeV (planned end of 2025, not confirmed), and today's licence and ion source
allow only a few % duty. At the licence duty limit (10 mA at 5 %), the reach is 2.2×10⁻³ (×1.5 short of
ATOMKI; 108 days to ATOMKI); with today's 1 % ion source, 4.9×10⁻³.

| 50 d, thin Li, no filter: big plastics (as built) | cell at 0.3 m | **0.5 m** | 1.0 m |
|---|---|---|---|
| **design: 20 mA DC, 2.0 MeV (10¹² n/s)** | 2.1×10⁻⁴ (5.0×10⁻⁴) | **3.3×10⁻⁴** (9.4×10⁻⁴) | 7.7×10⁻⁴ (2.6×10⁻³) |
| licence: 10 mA at 5 % duty, 2.0 MeV | 1.3×10⁻³ (3.4×10⁻³) | 2.2×10⁻³ (6.9×10⁻³) | 5.8×10⁻³ (2.1×10⁻²) |
| licence, 2.2 MeV (if the energy can be raised) | 6.4×10⁻⁴ (1.6×10⁻³) | 1.0×10⁻³ (2.9×10⁻³) | 2.3×10⁻³ (7.3×10⁻³) |
| today: 10 mA at 1 % (CHORDIS), 2.0 MeV | 2.8×10⁻³ (7.7×10⁻³) | 4.9×10⁻³ (1.6×10⁻²) | 1.3×10⁻² (4.8×10⁻²) |
| design, 1.912 MeV (25 keV "stellar" field) | 4.9×10⁻⁴ | 9.5×10⁻⁴ | 2.9×10⁻³ |

Days to the ATOMKI strength at 0.5 m (statistics only, ∝ ρ²): design 2.4 d; licence 108 d (2.0 MeV) or 23 d
(2.2 MeV); today 540 d. The survey's scaled bracket (10 mA design, 0.5 m) was 1.2×10⁻³ – 1.1×10⁻²
(`survey/SURVEY.md` §4.2). Every neutron is below 0.5 MeV, so E\* ≤ 22 MeV and all-E\* agree.

## 1. Beam model — 2026-10-21

`franz_beam.py` → `out/franz_beam.csv`, `out/franz_spectra.{csv,png}`, `out/franz_angular.csv`,
`out/franz_yield_check.csv`.

- Birmingham's slowing-down MC (`birmingham/bham_beam.py`: σ(E_p) stand-in, S ∝ E_p^−0.8, CM-isotropic,
  which near threshold, s-wave, is fair) with absolute σ/S (S = 0.19 MeV cm²/mg at 2 MeV, estimate) and fine
  2 keV bins. The protons stop at the (p,n) threshold (thin Li); the neutron yield is the same as a thick target.
- **Normalisation:** FRANZ design 10¹² n/s at 20 mA = 5×10¹⁰ n/s/mA at 2.0 MeV. Checks: the absolute σ/S model
  gives 7.5×10¹⁰ (×1.5); at 1.93 MeV the normalised model gives 1.5×10¹⁰, LiLiT measured ~2×10¹⁰.
- **Kinematic collimation:** at 1.912 MeV all neutrons are within 64° (Karlsruhe: 60°); at 2.0 MeV backward
  emission starts but 0° still gets ×3.6 the 4π average. 0° spectrum at 2.0 MeV: mean 143 keV, max 231 keV;
  1.912 MeV: mean 77, max 109 keV; 2.2 MeV: mean 274, max 463 keV.
- Per mA in pulse, through the Ø8 cm spot: 7.2×10⁷ n/s at 1 m, 2.9×10⁸ at 0.5 m (2.0 MeV).
- **N5 covers the spectrum.** N5 starts at 1 keV; the fraction of the 0° spectrum below 1 keV is 0.03 % (2.0 MeV)
  to 0.1 % (1.912 MeV), dropped. Each 1–30 keV log bin of N5 holds 12–26 MC singles (big plastics), ~4×10⁻⁷ per
  arm per neutron: enough.
- **Target γ:** 478 keV (⁷Li(p,p′γ), scaled from 6×10⁻⁵/p at 2.5 MeV, + saturated ⁷Be) ~3×10⁹ /s in pulse
  through the spot at 0.5 m, 10 mA: no legs (§2). 15–18 MeV: thick Li 10⁻⁷/p (Birmingham stand-in); **thin Li
  only direct capture across 1.88–2.0 MeV: ~5×10⁻¹⁰/p** (σ_DC ≈ 10 µb, estimate).
- **Pb:** at keV, Pb removes neutrons (Σ ≈ 0.36 /cm uncollided, estimate) almost as fast as 15–18 MeV γ
  (0.57 /cm), so a filter never pays with a thin target (table below).

## 2. Geant4 — 2026-10-21

The broad-band runs N5 / G5 / G6 re-weighted to each FRANZ source (`survey/soft_sim/README.md`), components
computed once per (E_p, Li thickness, Pb) at 1 mA, 1 m and scaled with I·Ω.

- keV neutrons give ~4×10⁻⁷ singles per arm per neutron (capture γ), and **no** same-event two-arm pair in
  the MC (N5, 0 events with weight in the spectrum).
- At the design baseline (2.0 MeV, 20 mA, 0.5 m), big plastics: 2 300 singles and 17 700 legs per arm per
  second; DREAM live 0.88, Micromegas occupancy 2.3×10⁻³.
- The correlated beam term is the thin target's direct-capture γ converting in the end cap and window:
  159 per day in the window at the baseline (1.6 % of IPC). A thick target makes it 3.0×10⁴/day (×3 the IPC)
  and costs ×1.6 in reach.

| 50 d, 2.0 MeV, 0.5 m, big plastics | thin Li | thick Li | thin + 5 cm Pb | thick + 5 cm Pb |
|---|---|---|---|---|
| design | **3.3×10⁻⁴** | 5.4×10⁻⁴ | 1.0×10⁻³ | 1.3×10⁻³ |
| licence (5 %) | 2.2×10⁻³ | 3.4×10⁻³ | 8.1×10⁻³ | 9.5×10⁻³ |

## 3. Reach — 2026-10-21

`franz_beam.py` (the soft_reach.py engine with a duty factor): the components at the in-pulse rate, then
signal, IPC, correlated, accidentals and cosmics (DAQ gated on the macro-pulse) × duty per day; DREAM live time
and occupancy at the in-pulse rate. Average yield capped at 10¹² n/s (binding only for DC above 2.0 MeV).
Vertex DCA < 60 mm, E_sum > W/2, θ-histogram fit (no TOF), throttle scanned (never needed).

Per day in θ = 100–150°, baseline (design, 0.5 m), big plastics:

| X17 at ATOMKI | IPC | cosmics (no veto) | accidentals | correlated beam |
|---|---|---|---|---|
| 203 | 10 160 | 4 650 | 34 | 159 |

**Statistics-limited everywhere** (reach = 0.92–0.98 × the IPC + cosmics floor). The levers are neutrons
through the cell (distance, duty, energy) and a cosmic veto (a third of the background at DC; at a few % duty
the gate already cuts cosmics ×20–100).

Why FRANZ ties Birmingham with 37× fewer neutrons per second: kinematic collimation puts the 10¹² n/s in a
forward cone, so 0.5 m sees 5.8×10⁹ n/s through the spot (Birmingham at 2 m: 7.0×10⁹ before its 5 cm Pb),
and the thin target removes the 15–18 MeV γ that forced Birmingham's Pb filter. Per neutron, the 2.0 MeV
spectrum makes 3.4×10⁻⁹ pairs, ×2 fewer than a 0.5 MeV neutron (`survey_yield.py`).

## 4. The field around the target — 2026-10-21 (estimate, not Geant4)

`out/franz_shield.csv`, Birmingham's `shield()` with a keV tenth-value layer of 5 cm of borated PE (stand-in).
At the design baseline, one arm (75 × 75 cm face) 0.5 m from the target would see 6.5×10¹¹ n/s, ×110 the
beam through the cell. Keeping the leakage singles below 10 % of the beam's own needs **17 / 22 / 27 cm of
borated PE** for 10⁻⁶ / 10⁻⁵ / 10⁻⁴ singles per entering neutron. With the arms reaching ~0.2 m upstream of
the cell window, a 0.5 m target–window distance leaves ~0.3 m for the target chamber and that shield: tight.
At 1 m (7.7×10⁻⁴, 13 d to ATOMKI) there is room.

## 5. What it needs, and what is not settled

1. **2 MeV beam on target at all** (planned end of 2025; not confirmed), then a licence for DC or ≥ 5 % duty
   at ~10¹² n/s and an ion source that delivers it (CHORDIS today: ≤ 1 %).
2. A thin Li target that stops the protons near the (p,n) threshold (FRANZ's own design style; confirm).
3. Room in the hall: the arms ~0.5 m downstream of the target with ~20–30 cm of borated PE around the target
   chamber, a vacuum flight tube and a dump (ask for the hall layout).
4. Whether the energy can be raised to 2.2 MeV (×2.2 better at 5 % duty).
5. **Not simulated:** the target chamber, the shield, the hall and room return (keV neutrons thermalise; their
   2.2 MeV H-capture γ cannot make legs), air before the cell (the tube is evacuated), and a diverging beam (the
   Geant4 gun is parallel; at 0.5 m the Ø8 cm spot is ±4.6°). The signal and IPC tables are NFS's lowest bin
   (E_n 0.2–0.75 MeV), applied at keV energies (θ_min 109.6° vs ~110°: a small shift).
6. The 478 keV flood (~3×10⁹ γ/s through the spot at 10 mA, plus ⁷Be) makes no legs; its Micromegas occupancy is
   not in the model.
7. σ_DC for ⁷Li(p,γ) at 1.9–2.0 MeV (10 µb assumed) sets the correlated term; ×10 would still leave it < 20 % of IPC.
