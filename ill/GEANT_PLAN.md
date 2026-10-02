# Geant4 plan for the ILL study (lxplus / HTCondor)

Everything in `ill_rates.py` that is labelled *analytic scaling* exists to be
replaced by this campaign. The code is `~/CLionProjects/MX17_Full_Geant`, and
the reduction is the existing `scripts/thermal_accounting.py`, run unchanged,
so every ILL configuration produces the **same contract**
(`accounting.json` + `F1…F5.csv`) as the n_TOF thermal campaign. `ill_rates.py`
then reads one contract per configuration instead of scaling the n_TOF one.

Written 2026-10-01. Nothing below has been run. **Superseded in part by `HANDOFF_SIM.md`** (no capsule configurations; the cell scan and beam model there win).

---

## 0. Principle

Geant4 owns per-neutron physics. Python owns time, as in
`PLAN_NEUTRON_CAMPAIGN.md`. The only structural change at a reactor is that
time is **continuous**: Stage 4's pile-up layer draws Poisson arrivals at a
rate R instead of filling pulses. Nothing in Geant4 needs to know about time.

## 1. Code changes (MX17_Full_Geant, a branch `ill`)

Follow `GEOMETRY_CHANGE_CHECKLIST.md` for every geometry item; the source of
truth stays `include/SimConfig.hh`.

### 1a. A reactor beam: `--beam ill`
- **Energy:** sample λ from a table (`data/beam/pf1b_spectrum.csv`, dΦ/dλ,
  **to be requested from the PF1B instrument responsible**). Until it arrives,
  use a guide-transmitted Maxwellian whose mean λ is set by `--lambda-mean`
  (default 4.25 Å). Also `--lambda-flat lo hi` for scans.
- **Profile:** flat disk `--beam-radius` (default 10 mm, the capsule bore) or
  rectangle `--beam-rect w h`. Divergence from the guide's m-value:
  θ ≈ m · 0.1°/Å · λ, uniform within ±θ (`--guide-m 2`).
- **Gun position:** at the last collimator, `--gun-dist` upstream (default
  300 mm), so window scattering and the collimator shadow are inside the world.
- Keep `event_type = 2`. Store λ in EventTree (the energy column already
  exists).

### 1b. A low-pressure cell: `--target cell`
The capsule stays the default (`--target capsule`). The new solid is parametric:

| flag | default | meaning |
|---|---|---|
| `--cell-pressure` | 1.0 bar | ³He density (ideal gas, 293 K) |
| `--cell-length` | 150 mm | gas column along the beam |
| `--cell-radius` | 25 mm | bore |
| `--window` | `Be:0.5` | entrance window material:thickness_mm (Be, Al, C, Mg, Si, diamond) |
| `--cell-wall` | `Al:0.5` | side wall, which the pairs exit through |
| `--cell-end` | `Al:2` | downstream end cap (sees only what the gas misses) |

Name the volumes `He3Gas` (reused, so the nCapture biasing and every
reduction keep working), `He3Cell_Window`, `He3Cell_Wall` and `He3Cell_End`.
Add the three to `thermal_accounting.py`'s "near capsule" logical-volume list
(see the gotcha in `CAMPAIGN_STATUS.md`: always classify by logical volume,
never by radius).

### 1c. Physics: thermal scattering for solids
The current list has HP neutrons but **no S(α,β) for solids**. At 4 Å this
matters: Be is transparent above its 3.96 Å Bragg edge, and Al/C have Bragg
structure too. A free-gas Be window would scatter far too much into the
scintillators. Register `G4ParticleHPThermalScattering` with the G4NDL TS data
for `G4_Be` (TS_Be_metal), graphite and Al. Check which are in the lxplus
G4NDL. **Validation:** transmission of a 0.5 mm Be/Al slab against
tabulated values at 2, 4 and 6 Å, one local 10⁶-neutron run each.

### 1d. Gamma source: more cascades
`--gamma-source` knows only `kAlLines` and `kCfrpLines`. Add `kBeLines`
(⁹Be(n,γ): 6.810, 3.367, 3.443, 5.957, 2.590 MeV…), `kCLines` (4.945,
3.684, 1.262), `kMgLines` and `kSiLines` from EGAF/IAEA PGAA (`ipc_aluminium`
already reads EGAF; reuse its line lists). Select by the library's capture
volume.

### 1e. Cosmics: `--cosmic`
Continuous running gives cosmics ~150× n_TOF's daily live time, and a muon
through two opposite arms is a back-to-back pair. Add a cos²θ muon generator
on a 3×3 m plane 1.5 m above the target (or CRY, if it is available on lxplus),
with E from a sea-level spectrum. Score as usual. Event weight = live seconds
per event.

### 1f. Pairs from an extended source
`--pair-vertex-lib` already samples vertices from a library. Build the
library from the cell runs' (n,p) vertices (`F1`'s gas positions), one per
(pressure, λ). For the pair kinematics, write the generator's input from
`ipc_born` (M1 and E0 separately), not from the 1/M ansatz, so the
polarised analysis (§3, R5) can reweight channel by channel.

## 2. Runs

Event counts are sized from the n_TOF campaign's per-job rates (10⁷ neutrons
per `workday` job; 10⁵ pairs per job).

| run | config | primaries | jobs | purpose |
|---|---|---|---|---|
| **R0 bridge** | `--target capsule --beam ill` | 10⁹ n | 100 × 10⁷ | Validate the 1/v bridge: every contract ratio should be 2.36/0.651 = **3.6×** the n_TOF contract. If not, `ill_rates`' configuration A is wrong. |
| **R1 slab check** | window slabs only, 2/4/6 Å | 3 × 10⁶ | local | §1c validation |
| **R2 cell scan** | window ∈ {Be, C, Al} × t ∈ {0.25, 0.5, 1 mm} × P ∈ {0.3, 1, 3 bar} | 10⁸ n each (27 points) | 27 × 10 × 10⁷ | Capture budget + direct singles/MM charge per neutron for each point. Pair-tags will be too rare to count directly in config B (~10⁻¹⁰/n); that is what R3 is for. |
| **R3 γ-source** | `--gamma-source` from each R2 point's capture library | 10⁸ γ per material | 3 × 100 × 10⁶ | High-statistics wall pair-tags and wall pairs reaching the gaps, weighted by captures/γ from R2 (as Run C was at n_TOF) |
| **R4 signal** | `pairs`, X17 + M1 + E0, vertices from each pressure | 10⁷ per pressure | 3 × 100 × 10⁵ | Acceptance and trigger ε against source length: the extended-source cost |
| **R5 window pairs** | internal pairs from window captures (Be/C lines, `ipc_born` M1/E1) | 10⁷ | 100 × 10⁵ | Vertex separation of window against gas pairs at each pressure |
| **R6 cosmics** | `--cosmic` | ≥ 1 live day | 100 jobs | Two-arm cosmic rate passing the menu, and what pointing/timing removes |
| **R7 FIPPS** | `--target capsule --beam ill --lambda-mean 2.3 --beam-radius 7.5` | 10⁹ n | 100 × 10⁷ | The plug-and-play option with the real pencil beam |

Storage and CPU are well inside what the n_TOF campaign used, so none of this
needs justification against condor quota. Outputs go to
`/eos/experiment/ntof/data/x17/ill/<run>/`.

## 3. Analysis chain

1. `thermal_accounting.py reduce` per file on condor, then `merge` →
   one contract per configuration (`/eos/experiment/ntof/data/x17/ill/contracts/<cfg>/`).
2. `ill_rates.py`: add `--contract <dir>` per configuration. When present, the
   ladder comes from it and `basis` reads "Geant4". The analytic scaling stays
   as a cross-check column, and the report shows both.
3. Stage-4 pile-up (`MX17_Simulation`): Poisson time at R, a 1 µs drift
   window and the DREAM dead-time model. This gives the real ceiling in place
   of the 10 %-occupancy rule.
4. Polarised (R5 + R4 reweighted): no Geant4 polarisation needed. The
   channels are generated separately and weighted by `ill_rates.polarised()`.

## 4. Before any of it: ask the ILL

The gun needs the PF1B dΦ/dλ table and the divergence after the last
collimator. The background floor needs a casemate γ/fast-n measurement. Neither
can be simulated, so request both in the first contact with the instrument
responsible.
