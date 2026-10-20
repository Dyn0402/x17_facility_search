# FRM II MEDAPP — X17 feasibility with its own Geant4 beam background

Facility record: `FACILITY.md`. Slides: <https://dylan-neff.web.cern.ch/notes/frm2-medapp-x17-feasibility.html>
(`deck/build_deck.py`). Simulation and analysis: `survey/soft_sim/` (shared with `birmingham/`).

## 0. Answer — 2026-10-20

**The SR10 fission beam would reach X17/IPC = 4.2×10⁻⁴ at 3σ in 50 days (big plastics, E\* ≤ 22 MeV):
×3.6 past ATOMKI's ⁴He value (1.5×10⁻³). ~4 days of beam reach the ATOMKI strength (statistics only).**
As built: 5.4×10⁻⁴. With three photons per neutron instead of one: 6.5×10⁻⁴. The obstacle is not the
physics but the reactor: FRM II has not run since March 2020 and has no restart date.

| | big plastics | as built |
|---|---|---|
| 50 d, E\* ≤ 22 MeV (X17 only from E_n ≤ 2.75 MeV) | **4.2×10⁻⁴** | 5.4×10⁻⁴ |
| 50 d, all E\* (X17/IPC constant in E\*) | 3.3×10⁻⁴ | 4.1×10⁻⁴ |
| 14 d, E\* ≤ 22 MeV | 7.9×10⁻⁴ | — |
| γ/n = 3 (pessimistic γ field), 50 d | 6.5×10⁻⁴ | 1.0×10⁻³ |
| Pb filter out (7×10⁸ n/cm²/s, γ/n = 3), 50 d | 6.5×10⁻⁴ | 1.0×10⁻³ |
| statistics floor (IPC + cosmics, full beam, no dead time) | 1.5×10⁻⁴ | — |

The survey's scaled bracket (`survey/SURVEY.md` §4.2) was 2×10⁻⁴ (Geant4 N4 table) to 4.6×10⁻³ (flat):
the dedicated Geant4 run lands near the optimistic end.

## 1. Beam model — 2026-10-20

`medapp_beam.py` → `out/medapp_beam.csv`, `out/medapp_spectra.{csv,png}`.

- Neutrons: ²³⁵U Watt spectrum + 5 % of a 1/E part on 1 keV–0.5 MeV (stand-in for the measured
  "intermediate" component; ask). Mean 1.93 MeV; **68 % in 0.2–2.75 MeV, 24 % above**.
- 3.2×10⁸ n/cm²/s (standard filters) over the Ø8 cm cell spot (50 cm², MLC): **1.6×10¹⁰ n/s**.
- γ: 1 photon per neutron (from the 3:1 n:γ dose ratio), spectrum exp(−E/2.45 MeV) on 0.1–10 MeV,
  mean 2.4 MeV (the measured mean). Stand-in for the shape.

## 2. Geant4 — 2026-10-20

Broad-band runs re-weighted to this source (`survey/soft_sim/README.md`): N5 (9×10⁷ forced-collision
neutrons per hardware set, 1/E on 1 keV–20 MeV), G5 (2×10⁸ photons, 1/E on 0.1–20 MeV), G6 (2×10⁸
photons flat on 14–19 MeV). NFS cell (30 bar × 40 cm), arms, vacuum flight tube.

- **Soft neutrons are quiet:** below 2 MeV a neutron gives 2–5×10⁻⁷ "ok" singles (leg + Micromegas
  segment) per arm, ×30 below the survey's flat bound (1.0×10⁻⁵). Above ~2 MeV the n-p recoils start
  to fire the back plastic: 3×10⁻⁵ legs per arm per neutron at 2–3 MeV, 1×10⁻⁴ above 5 MeV.
- **Photons below ~2.7 MeV make no leg** (half a MIP in the back plastic). 3–5 MeV: 5×10⁻⁶ singles per
  arm per photon; 5–10 MeV 4×10⁻⁵.
- At full beam: 8.2×10⁴ singles and 5.2×10⁵ legs per arm per second; **95 % of the singles come from the
  γ tail**, most legs from the fission tail above 2 MeV.

## 3. Reach — 2026-10-20

`survey/soft_sim/soft_reach.py` → `out/soft_reach.csv`, `soft_components.csv`, `soft_throttle.csv`.
DC beam: one θ histogram (no TOF). Vertex DCA < 60 mm, E_sum > W/2 (W = 20.95 MeV).

At the best rate (throttle ×0.32, 5.1×10⁹ n/s through the cell), per day in θ = 100–150°, big plastics:

| X17 at ATOMKI | IPC | cosmics (no veto) | accidentals | correlated beam |
|---|---|---|---|---|
| 174 | 13 900 | 2 550 | 2 470 | 7 |

DREAM live time 0.51 (random two-arm triggers 3.2×10³/s), Micromegas occupancy 0.026. The throttle is set by
the trigger: at full beam the legs keep DREAM mostly dead. The correlated term is factorised (~1 MC event
passes every cut directly; the direct estimate gives the same reach to 1 %).

## 4. What it needs, and what is not settled

1. **The reactor** (FACILITY.md §3). Nothing runs before it.
2. **Room for the arms** in MEDAPP (treatment room) or NECTAR behind it; vacuum tube from the MLC; a dump
   behind the arms. The model has the beam line only from 1 m upstream of the cell: no MLC, room or dump.
3. **The γ field at the cell:** it is 95 % of the singles here and a stand-in (γ/n = 1, exponential shape).
   ×3 more γ costs ×1.5 in reach.
4. Micromegas occupancy from γ that make no leg is not in the model (only ok singles count).
5. No cosmic veto yet: an arm-to-arm TOF veto would remove most of the 2 550 cosmics per day in the window.
6. X17 is taken only from E_n ≤ 2.75 MeV; 24 % of the neutrons are above.
