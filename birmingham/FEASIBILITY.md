# Birmingham HF-ADNeF — X17 feasibility with its own Geant4 beam background

Facility record: `FACILITY.md`. Slides: <https://dylan-neff.web.cern.ch/notes/birmingham-x17-feasibility.html>
(`deck/build_deck.py`). Simulation and analysis: `survey/soft_sim/` (shared with `frm2_medapp/`).

## 0. Answer — 2026-10-20

**With the cell 2 m from the Li target, 2.8 MeV protons at 30 mA and 5 cm of Pb in a Ø8 cm collimator, the
reach is X17/IPC = 3.3×10⁻⁴ at 3σ in 50 days (big plastics): ×4.5 past ATOMKI's ⁴He value. ~2.4 days of
beam reach the ATOMKI strength (statistics only).** As built: 1.0×10⁻³, still past ATOMKI. The facility
operates today. What it lacks is a beam port: users mount rigs at the target, in the 4π field of a
3.7×10¹³ n/s source, and the arms need roughly 50 cm of borated PE between them and it (an estimate).

| 50 d, big plastics (as built) | no Pb | 5 cm Pb | 10 cm Pb |
|---|---|---|---|
| 2.8 MeV, cell at 1 m | 1.0×10⁻⁴ (2.6×10⁻⁴) | 1.6×10⁻⁴ (4.3×10⁻⁴) | 2.6×10⁻⁴ (7.8×10⁻⁴) |
| **2.8 MeV, cell at 2 m** | 2.0×10⁻⁴ (5.5×10⁻⁴) | **3.3×10⁻⁴** (1.0×10⁻³) | 6.2×10⁻⁴ (2.1×10⁻³) |
| 2.6 MeV, cell at 2 m | 2.3×10⁻⁴ (6.3×10⁻⁴) | 3.8×10⁻⁴ (1.2×10⁻³) | 7.3×10⁻⁴ (2.5×10⁻³) |

Every neutron is below 1.1 MeV, so the E\* ≤ 22 MeV and all-E\* conventions agree. 14 days at the baseline:
6.3×10⁻⁴. The survey's scaled bracket was 2.5×10⁻⁴ – 3.7×10⁻³ (`survey/SURVEY.md` §4.2).

## 1. Beam model — 2026-10-20

`bham_beam.py` → `out/bham_beam.csv`, `out/bham_spectra.{csv,png}`, `out/bham_shield.csv`.

- Thick-target ⁷Li(p,n) slowing-down Monte Carlo: σ(E_p) stand-in (Macklin–Gibbons shape), S ∝ E_p^−0.8,
  CM-isotropic emission (stand-in; the real distribution is forward-peaked above 2.3 MeV), normalised to the
  facility's 3×10¹³ n/s at 30 mA, 2.6 MeV. End points check: 0.79 MeV at 2.5 (Lee & Zhou 787 keV),
  0.89 at 2.6, 1.10 at 2.8 MeV (facility: 0.9 / 1.1).
- 0° yield 5.6×10¹² n/s/sr at 2.8 MeV (×1.9 the 4π average); through the Ø8 cm spot at 2 m: **7.0×10⁹ n/s**
  (6.0×10⁹ at 2.6 MeV). 2.8 MeV wins: ×1.17 the neutrons and a harder spectrum.
- Target γ through the spot at 2 m, no filter: 478 keV ~1.1×10⁹/s (⁷Li(p,p′γ) ~6×10⁻⁵/p plus ⁷Be decay),
  14.6–18.2 MeV ~1.9×10⁶/s (⁷Li(p,γ)⁸Be ~1×10⁻⁷/p; estimate). Pb: μ = 1.76 /cm (478 keV), 0.57 /cm
  (15–18 MeV), neutrons Σ = 0.20 /cm uncollided (conservative).

## 2. Geant4 — 2026-10-20

The broad-band runs N5 (neutrons), G5 (photons 0.1–20 MeV) and G6 (photons 14–19 MeV, for the ⁸Be lines),
re-weighted to this source (`survey/soft_sim/README.md`).

- Neutrons below 1.7 MeV cannot fire the back plastic (half a MIP); they give 2–5×10⁻⁷ singles per arm per
  neutron, through capture γ. Baseline at full current: **615 singles and 4 500 legs per arm per second.**
- The 478 keV photons make no legs. The 15–18 MeV lines convert in the cell's end cap and window: without a
  filter they give the correlated beam term, 8.6×10³ per day after cuts at 2 m (factorised; 25 MC events
  pass every cut directly, and the direct estimate agrees: 2.07×10⁻⁴ vs 2.01×10⁻⁴).

## 3. Reach — 2026-10-20

`survey/soft_sim/soft_reach.py`. DC beam: one θ histogram. Vertex DCA < 60 mm, E_sum > W/2.

Baseline, full current (no throttle needed), per day in θ = 100–150°, big plastics:

| X17 at ATOMKI | IPC | cosmics (no veto) | accidentals | correlated beam |
|---|---|---|---|---|
| 204 | 10 500 | 5 270 | 1.5 | 194 |

DREAM live 0.99, Micromegas occupancy 6×10⁻⁴. **Statistics-limited:** the reach is the IPC + cosmics floor
(3.3×10⁻⁴). So the levers are flux through the cell (distance, filter, beam energy) and a cosmic veto,
which would remove a third of the background.

## 4. The shield the 4π field needs — 2026-10-20 (estimate, not Geant4)

`bham_beam.shield()` → `out/bham_shield.csv`. With no wall, one arm (75 × 75 cm face) 2 m away sees
7.9×10¹¹ n/s, ×300 what goes through the cell. To keep its singles below 10 % of the beam's own (62/s per
arm), for 10⁻⁶ / 10⁻⁵ / 10⁻⁴ singles per neutron entering an arm, the transmission must be 7.8×10⁻⁵ /
7.8×10⁻⁶ / 7.8×10⁻⁷: **41 / 51 / 61 cm of borated PE** at a 10 cm tenth-value layer (stand-in), plus Pb for
the capture γ. A port through a wall into a second room is the clean version; a local wall in the target
room leaves the room return. This is the first thing to simulate next (wall + room in Geant4).

## 5. What it needs, and what is not settled

1. **A shielded beam port** with a Ø8 cm collimator and a Pb filter; room for the arms ≥ 2 m from the Li;
   room dimensions are not public (ask).
2. Protons at 2.8 MeV kept available after the deuteron upgrade (deuterons give an NFS-like hard spectrum).
3. Measured 0° spectrum and γ yields (478 keV, 15–18 MeV) to replace the stand-ins.
4. Micromegas occupancy from the 478 keV flood (no legs) is not in the model; it argues for the 5 cm Pb
   baseline over no filter.
5. Not simulated: the wall, the room, the dump, air in front of the cell (the tube is evacuated).
6. No cosmic veto yet.
