# Handoff — ILL Geant4 campaign on lxplus

Written 2026-10-01, revised the same day after the reconstruction argument
below. Nothing here has been run. This is the brief for the session that
builds and runs the ILL simulations in `~/CLionProjects/MX17_Full_Geant`
(lxplus: `/afs/cern.ch/work/d/dneff/git/MX17_Full_Geant`). Where it disagrees
with `GEANT_PLAN.md`, this file wins.

Read first: `README.md` (the projection), `FACILITY.md` (PF1B),
`cell_length.py` and `beam_spot.py` (the numbers below),
`../vessel_design/mylar_wrap_vessel.py` (the 1 bar cell concept),
`MX17_Full_Geant/docs/angular_resolution/angular_resolution_note.md` (how the
opening angle is reconstructed and what limits it). The feasibility doc:
<https://claude.ai/code/artifact/f0e02b00-2700-41d3-89c7-f1fea8b2fedd>.

**Scope: the unpolarised PF1B search only.** The polarised search is
deferred.

---

## 1. What the campaign has to decide

We have not fixed the target. The first campaign maps a small design space and
returns the same set of numbers for every point, so the choice can be made on
results:

- **Pressure and length.** 1, 2 or 3 bar, each long enough to stop 99.5 % of
  the beam.
- **Wall.** A zero-Δp 12 µm mylar skin at 1 bar, or a thin pressure-bearing
  Kapton wall at 2–3 bar.
- **Radius.** 40 mm or 100 mm.

The trade being tested (§3): low pressure gives the thinnest wall but the
longest source along the beam, and with the vertex-to-hit reconstruction that
source length costs opening-angle resolution. Dylan has doubts about the
high-pressure / small-radius corner. That is why it is scanned and not
assumed.

Every configuration is placed so that its (n,γ) production is centred in the
Micromegas along the beam (§4).

## 2. Decisions already taken

1. **No 500 bar capsule.** In an opaque target every neutron is absorbed at
   any pressure, and ³He(n,p) and ³He(n,γ) both go as 1/v. So the yields per
   absorbed neutron are pressure-independent. The capsule's 5.5 mm Al nose and
   its 1 % X₀ barrel buy nothing at the ILL. The capsule appears only in a
   local generator smoke test.
2. **The beam is as realistic as the public record allows** (§5a): the
   measured H113 spectrum, exit dimensions and wavelength-dependent
   divergence.
3. **Keep the n_TOF coordinate convention** (beam = +Y, origin at the detector
   centre). At the ILL the beam is horizontal. One flag carries that (§5a, §5e).
4. **Thermal capture is at rest** (E* = 20.58 MeV, no boost), so the existing
   at-rest pair generator is exactly right here.
5. **Rate is not optimised in this campaign.** Results are per absorbed
   neutron, and rate comes later from `beam_spot.py` and the Stage-4 pile-up
   model. The Micromegas occupancy limit in `ill_rates.py` is a placeholder
   (10 % occupancy in a 1 µs window) and must not steer anything here.

## 3. Why pressure is the main lever (the reconstruction argument)

On n_TOF data the Micromegas measure positions well (0.6–0.8 mm) and directions
poorly: single tracks miss the capsule by a median of 44 / 75 / 114 mm (A / C /
D) at about 235 mm, which is 11–26° of direction error. The working opening
angle is therefore the vertex-to-hit chord ("nomline" in the angular note),
which needs an assumed vertex. Its per-leg error at 10 MeV/c, from Highland
estimates:

| term | n_TOF capsule | 1 bar mylar | 3 bar, 0.23 mm Kapton |
|---|---|---|---|
| target wall (multiple scattering) | ~6.4° | 0.3° | ~1.4° |
| air, ~20 cm, on the chord | ~0.8° | ~0.8° | ~0.8° |
| hit position | 0.2° | 0.2° | 0.2° |
| vertex ⊥ beam, Ø2 cm spot | — | ~1.4° | ~1.4° |
| **vertex along beam** (half the 16–84 % depth span / 204 mm) | ~3° | **~8.7°** | **~2.9°** |

The along-beam error is correlated between the legs. It roughly doubles for
back-to-back legs in a plane containing the beam and nearly cancels for
perpendicular arms. A wall kink at radius R moves the Micromegas hit by
ψ(L − R) but the track's back-pointing by ψR, so a large R helps the chord and
hurts pointing.

All of this is analytic. **The campaign's first job is to measure it.**

## 4. The configurations

Lengths stop 99.5 % of the H113 beam (`cell_length.py`). The stop-depth law is
the same for (n,p) and (n,γ), since both go as 1/v, and it does not depend on
radius. **Placement rule:** put the entrance window at y_w = −(median depth),
so the median (n,γ) vertex sits at the detector centre, y = 0. The Micromegas
active length is ±180 mm.

| id | p [bar] | gas L [mm] | wall | R [mm] | wall x/X₀ | ³He [bar·L] | median / mean depth [mm] | 10 / 90 / 99 % [mm] | **y_w [mm]** |
|---|---|---|---|---|---|---|---|---|---|
| G1 | 1 | 300 | 12 µm mylar on rod cage, 6 rods | 40 | 4.2×10⁻⁵ (+rods) | 1.5 | 21.6 / 36.4 | 3.0 / 88.9 / 211 | **−21.6** |
| G2 | 1 | 300 | 12 µm mylar on rod cage, 15 rods | 100 | 4.2×10⁻⁵ (+rods) | 9.4 | same | same | **−21.6** |
| G3 | 2 | 150 | Kapton 0.11 mm | 40 | 3.8×10⁻⁴ | 1.5 | 10.8 / 18.2 | 1.5 / 44.5 / 105 | **−10.8** |
| G4 | 2 | 150 | Kapton 0.29 mm | 100 | 1.0×10⁻³ | 9.4 | same | same | **−10.8** |
| G5 | 3 | 100 | Kapton 0.23 mm | 40 | 8.0×10⁻⁴ | 1.5 | 7.2 / 12.1 | 1.0 / 29.6 / 70 | **−7.2** |
| G6 | 3 | 100 | Kapton 0.57 mm | 100 | 2.0×10⁻³ | 9.4 | same | same | **−7.2** |

Notes:
- **Kapton thickness** is t = Δp·R/σ with σ = 35 MPa, about half the Kapton
  HN yield. This is a placeholder until an engineer sizes it; simulate the
  thicknesses as listed. The rod count for the mylar cells scales with R to
  keep the 40 mm design's facet span.
- **Common to all configurations:** an entrance window of 0.5 mm Be, which
  holds 2 bar over the aperture. A downstream end cap of 8 mm Al. A ⁶LiF
  scraper ring on the upstream cap (§5b).
- **Escaping neutrons:** 0.5 % of the beam reaches the end cap.
- **G1/G2 run past the Micromegas.** The back cap sits at y = +278 mm, beyond
  the +180 mm edge, and 1.2 % of vertices lie beyond +180 mm.
- **V0 target:** `out/cell_depth.csv` holds the predicted depth PDF/CDF for
  each pressure.

## 5. Code changes (branch `ill` in MX17_Full_Geant)

Follow `GEOMETRY_CHANGE_CHECKLIST.md` for every geometry item; `SimConfig.hh`
stays the source of truth. 5a, 5b and 5c gate everything.

### 5a. Beam: `--beam ill` (realistic H113)

Source: Abele et al., *Characterization of a ballistic supermirror neutron
guide*, nucl-ex/0510072, the H113 guide that feeds PF1B.

- **Wavelength.** Sample from `data/beam/h113_spectrum.csv` (copy of
  `ill/out/h113_spectrum.csv`). That file is the paper's Eq. 11 fit to the
  measured capture-flux spectrum (λ₁ = 3.3 Å, λ₂ = 4.0 Å, p = 3), converted to
  particle flux, normalised, 1–25 Å in 0.025 Å bins. Check: particle mean
  4.9 Å, capture/particle 2.71 (paper: 2.7), 10 % of neutrons below 2 Å. The fit
  is not defined below 1 Å. Replace it with the ILL's own table when the
  instrument responsible sends one.
- **Exit window.** 60 mm wide (horizontal) × 200 mm high, flat to ~5 %, with a
  slight rise toward the outer, concave face of the curved guide. Model it as a
  weight 1 + 0.05·(x_h / 30 mm) across the width. The paper measured flatness
  at 0.5 m; the gradient is a ±5 % placeholder.
- **Divergence.** At each λ, uniform within |θ_h|, |θ_v| ≤ κ_eff·λ, with
  κ_eff = 0.017 rad/nm (0.0017 rad/Å). That is the paper's model (Eqs. 17–18,
  Figs. 6–8), giving HWHM ≈ 0.007 rad at the mean. Long wavelengths diverge
  most.
- **Defining aperture (analytic).** A round aperture of radius `--beam-radius`
  (default 10 mm, Ø2 cm) at the gun plane, `--gun-dist` 300 mm upstream of the
  entrance window.
  - Sample the position uniform in the disk and the direction uniform in the
    cone.
  - Back-project each ray by `--exit-dist` (default 1200 mm, aperture to guide
    exit). Reject rays whose origin falls outside the 60 × 200 mm exit, and
    apply the exit weight.
  - Count thrown and accepted rays in the run metadata.
  - This reproduces `beam_spot.py`'s profile, penumbra included, without
    tracking the ~97 % of the beam the collimator stops. Those collimator
    captures are not simulated: a site background, §8.
- **Orientation.** `--vertical-axis x|z` maps the exit's 200 mm (vertical)
  side onto a sim transverse axis. The cosmic generator uses the same flag
  (§5e).
- **Not modelled, with reasons.**
  - Gravity: a 10 Å neutron falls ~0.2 mm over 2.5 m.
  - γ carried down the guide: unknown, ask the ILL.
  - Air scattering upstream of the gun: the gun is 300 mm away.
- **Metadata.** Keep `event_type = 2`, and store λ (the energy column exists)
  and the thrown count.

`beam_spot.py` gives the absolute rate for any `--beam-radius` and distance.
Ø2 cm ≈ 1.9×10¹⁰ n/s at 46 MW, 1 m from the exit.

### 5b. Target: `--target cell`

The capsule code stays behind `--target capsule`.

| flag | meaning | values in this campaign |
|---|---|---|
| `--cell-pressure` | ³He fill, ideal gas, 293 K | 1, 2, 3 bar |
| `--cell-length` | gas column along the beam | 300, 150, 100 mm |
| `--cell-radius` | inner radius of the wall | 40, 100 mm |
| `--cell-yw` | entrance-window position along the beam | §4 table; placement scan in S1 |
| `--skin` | material:thickness_mm of the cylindrical wall | `Mylar:0.012`, `Kapton:<t>` per §4 |
| `--rods` | mylar cells only: N rods (one 12 × 1.5 mm flat, the rest Ø2 mm CFRP), at the skin radius | 6 (R 40), 15 (R 100); geometry from `mylar_wrap_vessel.py` (`VesselParams.rod_angles`) |
| `--window` | entrance window material:mm | `Be:0.5` (C1); `Be:0.25`, `Al:0.1`, `Al:0.3` (C2) |
| `--end-cap` | downstream cap | `Al:8` (C1); `Al:8+LiF6:3` (C2) |
| `--scraper` | ⁶LiF ring on the upstream cap, inner radius:thickness | `12:5` (halo scraper just outside the 10 mm spot) |
| `--endcap-ring` | upstream cap outside the window aperture | Al, 8 mm, 6 mm land |

- **Volume names.** Reuse `He3Gas`, so nCapture biasing and every reduction
  keep working. Add `He3Cell_Window`, `He3Cell_Skin`, `He3Cell_Rod`,
  `He3Cell_EndUp`, `He3Cell_EndDown`, `He3Cell_LiF`, `He3Cell_Scraper`. Put
  all of them in `thermal_accounting.py`'s near-target list; classify by
  logical volume, never by radius (`CAMPAIGN_STATUS.md`).
- **Fit.** Check the R = 100 mm cell against the MM faces (±204 mm) and the
  arm frames.
- **Materials.** Add Kapton (`G4_KAPTON`) and ⁶Li-enriched LiF (95 % ⁶Li) to
  the material list.

### 5c. Physics: thermal scattering for solids

Register `G4ParticleHPThermalScattering` with the G4NDL 4.7 TS data.
Nothing is registered today (no `ThermalScattering` in src/include).
- **Present on lxplus (checked 2026-10-01):** Al (`al_metal`), Be
  (`be_metal`), graphite, Mg, Fe, and Si in SiO₂.
- **Absent:** H in polyimide or mylar, O in SiO₂, LiF. Those run free-gas;
  record it.

Be is transparent above its 3.96 Å Bragg edge, and free-gas Be over-scatters
into the detector.

### 5d. Gamma-source cascades

Add `kBeLines` (⁹Be(n,γ): 6.810, 3.367, 3.443, 5.957, 2.590 MeV …), H 2.223 MeV
for Kapton and mylar, and Kapton's C/N/O lines from EGAF, reusing
`ipc_aluminium`'s readers. ⁶Li(n,t) emits no γ. Select by capture volume.

### 5e. Cosmics: `--cosmic`

cos²θ muons on a 3 × 3 m plane 1.5 m above the target, sea-level spectrum (or
CRY if it is on lxplus), weighted by live seconds. The zenith lies along
`--vertical-axis`, perpendicular to the beam, unlike at n_TOF.

### 5f. Signal vertices

`--pair-vertex-lib`: one library per configuration, from that configuration's
C1 `He3Gas` (n,p) positions. These carry the realistic depth and transverse
profile. Write the generator input from `ipc_born` with **M1 and E0 kept
separate**.

### 5g. Reconstruction options in `analyze_pairs.py`

Add `--assumed-vertex x,y,z` (default: beam axis, y = 0) to the chord
estimator. Run every S1 output through:
- `nomline`: the realistic chord, to the assumed vertex.
- `vline`: the oracle chord, to the true vertex.
- `first` / `fit`: direction-only.
- A chord to a per-event y from the two legs' crossing with the beam axis.

## 6. Runs

10⁷ neutrons or 10⁵ pairs per `workday` job. Keep the ³He(n,γ) nCapture bias
(×10⁵ in He3Gas) for neutron runs.

| run | what | primaries | jobs | answers | gate |
|---|---|---|---|---|---|
| **V0** generator + ³He | G1, G3, G5, unbiased, local; also the capsule once | 10⁶ each | local | Absorbed fraction 0.995, Geant stop-depth CDF against `out/cell_depth.csv`, spot profile at the window against `beam_spot.py` | first |
| **V1** slabs | 0.5 mm Be, Al; 0.1 mm Al; at 2, 4, 6 Å | 3×10⁶ | local | TS physics is live (transmission against tables) | before C1 |
| **C1** neutrons | G1–G6 at their y_w, Be 0.5 window, Al cap | 10⁸ each | 60 | Capture budget by volume, singles and MM charge per n, end-cap share, vertex libraries | V0, V1 |
| **C2** window / cap | G1 and G5: window {Be 0.25, Al 0.1 or Al 0.3}, cap Al vs Al+⁶LiF | 10⁸ × 6 | 60 | Window and cap choice | C1 |
| **Gγ** γ-source | capture libraries from C1 (window, skin, rods, caps, scraper) | 10⁸ γ per material | ~400 | Fake pair-tags and wall pairs at high statistics (direct counts ~10⁻¹⁰/n) | C1 |
| **S1** signal | G1–G6 at y_w; X17, M1, E0 as separate samples; C1 vertex library | 10⁷ per configuration (split X17 / M1 / E0) | 600 | **The headline: opening-angle σ68 and bias per estimator, acceptance × ε, per configuration** | C1 |
| **S1p** placement | G1, G5 at y_w = −mean and y_w = 0 | 10⁷ × 4 | 400 | Is median-centring right? | S1 |
| **S1s** spot | G5 with `--beam-radius` 17.5 and 25 mm (new 10⁷-neutron vertex libraries) | 10⁷ × 2 | 200 | What a wider spot costs the chord | S1 |
| **S2** window pairs | internal pairs from Be window captures (`ipc_born`) | 10⁷ | 100 | Vertex separation of window and gas pairs | C1 |
| **K1** cosmics | `--cosmic` | ≥ 1 live day | 100 | Two-arm cosmic rate through the trigger menu | 5e |

Outputs: `/eos/user/d/dneff/x17/ill/<run>/<config>/` (create `ill/`);
contracts to `/eos/user/d/dneff/x17/ill/contracts/<config>/`.

## 7. What to bring back

One row per configuration, G1–G6, in a single table (`ill/results/scan_v1.csv`
in this repo, plus a short note). This is what the design choice gets made on.

- **Absorption:** absorbed fraction; Geant median and 16–84 % stop depth
  (against §4).
- **Background per absorbed neutron:**
  - wall captures by volume (window, skin, rods, caps, scraper);
  - charged particles in a gap;
  - trigger legs and pair-tags;
  - wall pairs reaching the gaps.
- **Signal:** for X17, M1 and E0, acceptance × trigger ε, and opening-angle
  σ68 and bias for each §5g estimator. Give these overall, in the 100–180°
  window, and against the softer leg's kinetic energy.
- **Vertex:** σ of the pair vertex along and across the beam.

Then run `ill_rates.py --contract <dir>` per configuration. The basis becomes
"Geant4", and the analytic scaling stays as a cross-check column.

**Before that cross-check,** fix `ill_rates.py`'s PF1B capture/particle ratio
k: it uses 2.36 (λ̄ = 4.25 Å) where the H113 spectrum gives 2.71. Wall factors
are +15 % against the n_TOF contract (4.2× rather than 3.6×), and particle
flux is 15 % lower at fixed capture flux.

## 8. Not simulation, but blocks a design freeze

- **³He permeation** through 12 µm mylar and through Kapton over a 50-day
  cycle. Both polymers pass helium. The 1.5 bar·L cells are cheap to top up if
  the rate is known; the 9.4 bar·L R = 100 mm cells less so.
- **Pressure-wall engineering** for the Kapton thicknesses in §4.
- **From the ILL:** the PF1B dΦ/dλ table, the guide-exit-to-casemate distances
  (`--exit-dist`), γ carried down H113, and a casemate γ/fast-n measurement
  (EASY/DDT day). The collimator's own captures are a site background in that
  last item.
- **Tritium:** ~0.08 GBq per cycle at 10¹⁰ n/s. Containment in a polymer-walled
  cell needs ILL health-physics sign-off.

## 9. Environment (checked 2026-10-01)

- **Access.** `ssh lxplus` works non-interactively from the laptop (Kerberos).
  New ssh masters need a 2FA OTP, which needs Dylan at the keyboard.
- **Build.** `source scripts/setup_lxplus.sh` → Geant4 11.2.1, G4NDL 4.7
  (`/cvmfs/geant4.cern.ch/share/data/G4NDL4.7`). Build on lxplus only.
- **Checkout.** The lxplus checkout is at `3d97437` (nose-first) with
  uncommitted analysis directories. Commit or stash them before branching
  `ill`.
- **Batch.** `scripts/submit_neutrons.py` / `submit_pairs.py` drive HTCondor.
  The queue was empty.
- **Gotchas** from `HANDOFF_THERMAL_TRIGGER.md` §5:
  - run single-threaded (`-t 1`);
  - outputs are `<base>_t0.root`;
  - the 24 h Kerberos TGT silently wedges nohup'd jobs (condor jobs are
    immune);
  - validate EventTree entry counts before analysis;
  - lxplus `/tmp` is node-local.
