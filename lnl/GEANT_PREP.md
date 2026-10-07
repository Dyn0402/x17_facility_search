# Getting to useful Geant4 runs for LNL

Written 2026-10-07, for the session after the slides. **Nothing here has been run
or coded.**

**The goal:** replace the four soft numbers in `ESTIMATES.md` §4 with the
simulation, in this order:
1. `EPS_REST` (trigger × E_sum × reconstruction);
2. the γ₁ separation (15 vs 18 MeV);
3. cosmics in the LNL geometry;
4. EPC and γ singles from the target region.

Everything else in the estimate (cross sections, yields, the IPC Born shapes) is
already as good as Geant4 would make it.

The code is `~/CLionProjects/MX17_Full_Geant`. Branch from **`ill_ring`**, the current
ILL head (it has `--cosmic`, the Born IPC multipoles, `--slab`, the vertex
libraries). Call the branch `lnl`. Follow `GEOMETRY_CHANGE_CHECKLIST.md`.
`SimConfig.hh` stays the source of truth. It runs on lxplus, as in `../ill`.

## 1. What already works unchanged

| need | existing option | note |
|---|---|---|
| X17 pairs at 18.15 / 17.64 MeV | `--energy 18.15 --mass 16.7 --ipc 0` | `transition_energy_MeV` is a free parameter; the generator decays from rest, and the ⁸Be boost (β = 0.006) is negligible |
| IPC M1 / E1 continuum | `--ipc 1 --ipc-multipole M1` / `E1` | the same Born formula as `lnl_rates.py`; run E1 separately and weight by the direct-capture share (`out/yields.csv` `frac_direct`) |
| γ₁ IPC (to the 3.0 MeV state) | `--energy 15.1` (and 14.6) with M1/E1 | the final state is broad (Γ ≈ 1.5 MeV); a fixed W is fine for a first look |
| cosmics | `--cosmic` | the zenith must be perpendicular to the beam, as at the ILL (`--vertical-axis`) |
| arm distance | `--dist <cm>` | default 22 cm; keep as built for the first pass |

## 2. What has to be written (branch `lnl`)

**a. `--target li`: the LNL target region, replacing the capsule.**
- Chamber: a tube along the beam, `--chamber <Mat:t_mm:r_mm>`. Default `CFRP:0.4:25`,
  as MEG II and ATOMKI use; Al:0.5 as the alternative. ±300 mm long, with
  flanges/beam pipe beyond the arms modelled as Al tube.
- Film: `--film <Mat:ug_cm2>` (Li2O, LiF, Li), a disk ⊥ beam at the origin. Add the
  Li compounds to the material table: Li₂O 2.01, LiF 2.635, Li 0.534 g/cm³.
- Backing: `--backing <Mat:um>` (Al:10, C:20, Cu:25), right behind the film.
- Holder: a frame or rod (Al or CFRP) outside the beam spot. It should be in the
  geometry because ATOMKI saw its γ background.
- Beam dump / Faraday cup: `--dump-dist <mm>` downstream, thick Ta or Cu, so the
  γ-source runs can be pointed at it too.
- Volumes: `LiTarget_Film`, `LiTarget_Backing`, `LiTarget_Holder`, `LiChamber_Wall`,
  `BeamDump`. Classify by logical volume (the ILL rule).

**b. Point-like vertices.** Sample X17/IPC vertices from a 2-D Gaussian beam spot
(σ = `--spot-sigma`, default 2 mm, as in MEG II) at the film depth. Either add a
small mode, or write a vertex library CSV and use `--pair-vertex-lib` with
`--pair-vertex-vol LiTarget_Film`; that needs no C++ in the generator.

**c. `--gamma-lines <E:w,...>`: isotropic mono-energetic γ from the beam spot.**
- For EPC, γ singles and accidentals: 17.64, 18.15, 14.6, 15.1, and 6.13/6.92/7.12
  MeV (¹⁹F); 0.478 MeV (⁷Li p′γ).
- The existing `--gamma-source` re-emits capture cascades from a library. This is
  simpler: one vertex distribution, a line list with weights, and one weight per
  event.

**d. The beam is not tracked.** A 1 MeV proton deposits everything in the film or
backing. Tracking it buys nothing but the (p,γ) physics, which we put in by hand.
No `--beam` mode is needed.

## 3. Runs (lxplus, condor; sizes from the n_TOF pair runs, 10⁵ pairs/job)

| run | config | events | what it answers |
|---|---|---|---|
| **L0 smoke** | local, 10⁴ pairs, `--target li` defaults, overlap check | 10⁴ | geometry sane, vertices on the film |
| **L1 signal** | X17, W = 18.15, m = 16.6/16.7/16.8/17.0 | 10 × 10⁵ each | acceptance × ε vs opening angle with the per-arm trigger → **replaces EPS_REST** |
| **L2 IPC** | M1 and E1 at 18.15; M1 at 17.64; M1/E1 at 15.1 and 14.6 | 10 × 10⁵ each | background shapes in the analysis variables; **E_sum response: can the stack tell 15 from 18 MeV?** |
| **L3 γ lines** | `--gamma-lines` 18.15, 17.64, 15.1, 14.6, 6.13 | 10⁷ each | EPC and Compton into the arms, singles per arm per γ, trigger rate |
| **L4 cosmics** | `--cosmic`, LNL orientation | ≥ 1 live day | cosmic pairs passing the cuts, with the point-vertex cut on top of segments + collinearity |
| **L5 chamber scan** | L1 + L2 with chamber CFRP 0.4 / Al 0.5 / Al 1.0 and backing Al 10 / C 20 / Cu 25 | 5 × 10⁵ | how much material the measurement tolerates |
| L6 calibration | M1 at 17.64 (441 keV run); E0 at 6.05 (¹⁶O, LiF) | 10 × 10⁵ | what the calibration lines look like, for the run plan |

**The reduction is the ILL chain:**
- per-event arm tables (`ill_ring` already writes them);
- `seg_reduce`-style MM segments;
- then a small LNL version of `ill/sim_feasibility.py`: IPC + X17 + cosmics +
  accidentals, per energy point, weighted by `out/yields.csv`;
- a template-fit (Asimov/Fisher) reach as in `../ill/sim/lxplus/conservative.py`.

## 4. Before running: decisions that change the geometry

1. **Which machine/line.** AN2000 (where the LNL ⁸Be group is) or CN (4 µA, pulsed).
   It sets the beam height and orientation in the hall, and therefore the cosmic
   direction (**ask LNL**).
2. **Arm layout.** The n_TOF four-arm pinwheel ⊥ beam is the default. It already
   gives ~40 % geometric acceptance at 140°. Do not redesign before L1/L2 say what
   limits.
3. **Trigger stack.** As built, or the thick plastics of `../trigger_scint`. L2
   decides whether a calorimeter is needed for γ₁.
4. **Target.** Li₂O 300 µg/cm² on 10 µm Al as the baseline (`TARGETS.md` §6).

## 5. Things to bring from LNL / the collaboration

- AN2000/CN floor plans and beam-line heights.
- The LNL group's AN2000 setup and chamber drawings. They ran exactly this
  reaction in 2023–24, and their chamber may be reusable.
- What our demonstrator measured at ATOMKI on ⁷Li(p,e⁺e⁻): geometry, rates,
  opening-angle resolution.
- The MEG II IPC generator (Zhang–Miller) for the M1/E1 interference. Our Born
  shapes have none.
