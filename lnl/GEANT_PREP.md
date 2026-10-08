# Getting to useful Geant4 runs for LNL

Written 2026-10-07, for the session after the slides.

## 0. Status (2026-10-08)

**Done overnight 2026-10-08: L1–L6, the big-plastic and 20-bar variants, timing. Results in
`FEASIBILITY_SIM.md`; analysis `sim/lnl_geant.py`; pipeline `sim/lxplus/lnl_pipe.sh`.**

**Built: §2a–c** on MX17_Full_Geant branch **`lnl`** (from `ill_ring`; commits 5722bef, 1577274, 079db11, pushed).
- `--target li` with `--film Li2O|LiF|Li:ug_cm2`, `--backing Mat:um|none`, `--holder Mat:mm|none`,
  `--holder-r rin:rout`, `--chamber Mat:t_mm:r_mm`, `--chamber-len`, `--flange Mat:mm`,
  `--dump Mat:mm|none`, `--dump-dist`, `--spot-sigma`. Defaults = the §4 baseline:
  Li₂O 300 µg/cm² (1.49 µm) on Al 10 µm, Al 1 mm holder annulus r 10–20 mm, CFRP 0.4 mm chamber of bore
  25 mm, |y| ≤ 300 mm, Al 5 mm flanges (upstream hole r 10 mm), Ta 2 mm dump at y = 250 mm.
  Volumes: `LiTarget_Film/Backing/Holder`, `LiChamber_Vac/Wall/Flange`, `BeamDump`.
- Pair vertices (`--ipc`, X17) and γ vertices come from a Gaussian beam spot (σ 2 mm) uniform through the
  film depth; the film's downstream face is y = 0. Neither the beam pipe upstream of the flange nor the
  hall is modelled.
- `--gamma-lines E:w,...` (event_type 3, `inv_mass` = E_γ). `ConvPairTree` is now filled in these runs
  too, for the EPC.
- Driver: `scripts/submit_lnl.py --run Lk --sample X17_m16.7 | M1_18.15 | gam_8Be | cosmic`.
  Reduce with the ILL scripts unchanged: `scripts/submit_reduce_ill.py <dir> --kind pairs`, then
  `ill_pairs.py merge parts/*.npz -o <out> --config lnl` (the assumed vertex (0,0,0) is the beam spot).
- lxplus clone: `/afs/cern.ch/work/d/dneff/git/x17_lnl/{MX17_Full_Geant,MX17_Geant}` (separate from
  `x17_ill`, which is detached with local edits). Frozen binary `bin/mx17_full_sim_lnl_079db11`.

**L0 smoke (done, `/eos/experiment/ntof/data/x17/lnl/L0/`):** no overlaps (217 volumes checked);
vertices in y ∈ [−1.49 µm, 0], spot rms 2.0 mm; the X17 opening angle starts at 133.8° (θ_min for
m = 16.7 at 18.15 MeV); IPC M1 and γ-line modes run; 2000 γ give 52 conversions, in the arms and
also the holder, backing and dump. **First hint (500 X17, 18 tagged, ±25 %):** both leptons in the
MM gaps 47 % (toy: 45 %); trigger pair-tag 3.6 %. That is a post-geometry factor ~0.08 against
EPS_REST = 0.14, i.e. days ×~1.8 if L1 confirms it.

**Running (submitted 2026-10-08 ~01:00, clusters 4405805–4405815, 10 × 10⁵ each, ~20 GB per sample):**
L1 `X17_m{16.6,16.7,16.8,17.0}`; L2 `{M1,E1}_18.15`, `M1_17.64`, `{M1,E1}_15.1`, `{M1,E1}_14.6`.
Outputs `/eos/experiment/ntof/data/x17/lnl/L{1,2}/<sample>/`.

**Next:** reduce L1/L2 → acc × ε against opening angle with the per-arm trigger, and the E_sum
(SiPM + plastic + LS) spectra of 18.15 vs 15.1 MeV IPC → put the measured factor in place of
`EPS_REST` and the γ₁ leak in `lnl_rates.py`, rerun, rebuild the deck. Then L3 (`gam_8Be`, `gam_19F`)
and L4 (`cosmic`).

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
