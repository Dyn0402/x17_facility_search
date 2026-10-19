# Demokritos: the Geant4 campaign

Written 2026-10-19. The aim is to replace the LNL-calibrated toy in `ESTIMATES.md` with the full apparatus
around a Ti-T target. The questions:

1. **Acceptance.** What are the pair-tag acceptance and selection for ⁴He pairs at ~115°, where half use adjacent arms?
2. **The backing.** What does it do to the X17 edge and to the IPC: thin Cu 50 µm, the existing 1 mm Cu, and the
   1 mm Cu moved 12 cm downstream?
3. **EPC.** ATOMKI's dominant background was external pairs from the 20 MeV γ in their 0.4 mm Mo. How much reaches
   two arms at large angle in MX17?

## 1. Code: MX17_Full_Geant branch `demokritos` (from `lnl`, 2026-10-19, commit 4bad297)

- `--film TiT:<µg/cm²>`: Ti tritide TiT₁.₅, built by atom count with a ³H isotope, 4.0 g/cm³. The default
  2300 µg/cm² is Demokritos' 2.1 mg/cm² Ti loaded to T/Ti = 1.5, which is 5.75 µm.
- `--backing Mo:<µm>` is now possible (the ATOMKI backing).
- `--target-y <mm>` moves the film, backing and holder, and the pair and γ vertices, along the beam. The chamber stays
  put.
- `scripts/submit_demokritos.py`. Its baseline:
  - `--target li --film TiT:2300 --backing Cu:50 --holder Al:1 --chamber CFRP:0.4:25 --dump none --spot-sigma 2`;
  - W = 20.49 MeV (E_p = 900 keV).
- lxplus: a worktree of the `x17_lnl` clone at `/afs/cern.ch/work/d/dneff/git/x17_demok/MX17_Full_Geant`, with
  `MX17_Geant` symlinked from `x17_lnl`. The frozen binary is `bin/mx17_full_sim_demok_4bad297`.
- **Physics left as at LNL:**
  - the Born IPC generator (`--ipc 1 --ipc-multipole E1`);
  - X17 two-body decay from rest. The recoil mass is the generator's; the 0.01 MeV difference is ignored.
  - The beam is not tracked: vertices are uniform through the film depth in a σ = 2 mm spot.
  - The γ\* anisotropy is applied in the analysis by reweighting on the truth lepton momenta, as for LNL L7.

## 2. Configurations

| tag | target | why |
|---|---|---|
| `cu50` | TiT on **Cu 50 µm**, target at the arm centre | the proposed thin target (≤ 3 µA with rim cooling) |
| `cu1000` | TiT on **Cu 1 mm**, at the centre | Demokritos' existing target as is |
| `cu1000_y120` | Cu 1 mm, **target 120 mm downstream** | the arms see the target from upstream |
| `…_bigP` | + `--big-plastic 75 75 5 --no-ls --sipm-readout 20 0` | the trigger_scint upgrade, as at LNL |

## 3. Runs (submitted 2026-10-19, 164 jobs, clusters 4502887–4502907)

Outputs: `/eos/experiment/ntof/data/x17/demokritos/<run>/<sample>_<tag>/`. Condor files:
`/afs/cern.ch/user/d/dneff/condor/demokritos/`. Driver: `sim/lxplus/submit_all.sh`.

| run | sample | per config | configs |
|---|---|---|---|
| D1 | X17 m = 16.94 at W = 20.49 | 5×10⁵ | all six (3 targets × as built / big plastics) |
| D1 | X17 m = 16.7, 17.2 | 3×10⁵ | `cu50`, `cu50_bigP` |
| D2 | Born E1 IPC at 20.49, `--ipc-min-open 70` | 10⁶ | all six |
| D2 | the same, unbiased (`cu50_all`) | 2×10⁵ | normalisation check of the 70° cut |
| D3 | 20.49 MeV γ from the beam spot (EPC) | 10⁷ | `cu50`, `cu1000`, `cu1000_y120`, as built |
| — | cosmics | reuse LNL L4 (1.00 live day, as built and big plastics) | |

- **Not run:**
  - E0 pairs: they are 4×10⁻⁴ of the IPC (`PHYSICS.md` §2).
  - M1 IPC: the p + t capture at 0.5–1 MeV is E1.
  - Other E\*: the shape changes little between 20.2 and 20.56 MeV. Rerun at 20.2 if the 510 keV point matters.

## 4. Reduction and analysis

1. **Reduce, arm times, merge.** These are the LNL scripts unchanged (`lnl_reduce.py`, `lnl_time.py`,
   `lnl_merge.py` in `x17_lnl/analysis`). The wrapper is `sim/lxplus/demok_pipe.sh` (`reduce`, `time`, `merge`,
   `status`).

   The merge reconstructs the angle from (0,0,0). For `cu1000_y120` the analysis recomputes it from the true target
   position (0,120,0), using the stored charge centroids `c_all1/2`. The MM pointing cut is shifted the same way.
2. **Analysis.** `sim/demok_geant.py` uses the `lnl_geant` selection levels (MM 15° + TOF) and per-arm calorimetry,
   with:
   - an E_sum window around 19.5 MeV;
   - the yields from `out/yields.csv`;
   - B_x per γ;
   - the Born E1 IPC with the γ\* anisotropy (E1 direct capture: a sin²θ photon about the beam);
   - EPC from D3 scaled by γ/s;
   - cosmics from LNL L4 re-cut with the ⁴He window.

   Its outputs are the acceptance per config, S and B per day, and the counting and template-fit days to 3σ. The
   3D fit (`lnl_nd`) follows once the templates exist.
