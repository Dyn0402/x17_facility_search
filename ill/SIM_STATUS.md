# ILL Geant4 campaign — status

Live log of the runs briefed in `HANDOFF_SIM.md`. Started 2026-10-01.

> **PATHS (lxplus)**
> - outputs (unlimited): **`/eos/experiment/ntof/data/x17/ill/<run>/<config>/`**
> - AFS work dir: **`/afs/cern.ch/user/d/dneff/work`**; isolated build at
>   `…/work/git/x17_ill/MX17_Full_Geant` (branch `ill`), its sibling
>   `…/work/git/x17_ill/MX17_Geant`. The main lxplus checkout
>   `…/work/git/MX17_Full_Geant` (uncommitted analysis work) was not touched.
> - condor files/logs: `/afs/cern.ch/user/d/dneff/condor/ill/<run>/<config>/`
> - each output dir has a `RUN_INFO.txt` (binary, args, seeds).

## Code (MX17_Full_Geant, branch `ill`, pushed to `origin/ill` 2026-10-02)

| commit | what |
|---|---|
| `067b382` | `--beam ill` (H113/PF1B), `--target cell`, thermal scattering, `--slab`, Born IPC `--ipc-multipole M1/E0/E1`, scripts `submit_ill.py`, `ill_validate.py`, `ill_accounting.py`, `ill_pairs.py` |
| `16d07e2` | `submit_reduce_ill.py`: condor submitter for the per-file reductions |
| `0873e54` | `--bias-wall/--bias-thick/--bias-air` (high-statistics wall γ, replaces Gγ) |
| `7892a77` | `--cosmic` (K1), `--pair-vertex-vol` (S2) |
| `ef29314` | `ill_make_lib.py`: vertex libraries for S1/S2 (thinned, optional y shift) |
| `faac5ba` | per-event, per-arm tables from `ill_accounting.py` (gap energy + centroid, SiPM/plastic/LS, scintillator time, capture volume) and per-arm calorimetry in `ill_pairs.py`; read by `sim_feasibility.py` |

The lxplus clone (`…/work/git/x17_ill/MX17_Full_Geant`) was synced by copying
the working tree, so it shows these as uncommitted changes on `15bd0c2`; its
files are identical to the commits above.

Running jobs use frozen binaries (`bin/mx17_full_sim_<hash>`, or `build/` for
C1 = `067b382`), so rebuilding cannot touch them.

### Deviations from the handoff, and why

- **Thermal-scattering materials.** G4NDL 4.7 keys S(α,β) on *element* names
  (`TS_Beryllium_Metal`, `TS_Aluminium_Metal`, …), not on `G4_Be`/`G4_Al`.
  The cell's Be/Al/C/Fe are built from TS-named elements; the detector's own
  `G4_Al` stays free-gas. TS is on by default only with `--beam ill`,
  `--target cell` or `--slab`, so n_TOF runs are unchanged.
- **Gγ replaced by wall biasing (C1w).** The local PGAA subset has only
  H/He/C/Al, so it has no Be, N or O lines. Instead, nCapture is occurrence-biased in
  the cell's solids and in the air, using Geant4's own HP capture photons
  (the same physics as C1). Thin walls ×300, the 8 mm Al and ⁶LiF ×20, air
  ×100. A ×300 factor on 8 mm Al saturates, and the survivors then carry
  weights ~e⁹. Checked against analog V0 on G5: the weighted window, ring,
  cap and air capture rates reproduce it, with max weight 6.9.
- **Skin geometry.** The mylar wrap is modelled as a cylinder, with the
  flat rod's corners on r = R. The real wrap is a taut polygon; the
  difference is < 1 mm in radius.
- **Cell details the handoff left open.** Window aperture r = 15 mm; the
  ⁶LiF scraper spans r 12 mm → the ring's outer radius. A `+LiF6` end-cap
  layer sits on the gas side.
- **S2 kinematics.** The window internal pairs use the dominant ⁹Be(n,γ)
  ground-state primary only (6.81 MeV, E1 Born). No Be line list is at hand.

## Validation

**V0** (10⁶ unbiased neutrons each, G1/G3/G5): passed.

| | G1 (1 bar) | G3 (2 bar) | G5 (3 bar) |
|---|---|---|---|
| (n,p) in He3Gas per primary | 0.9387 | 0.9401 | 0.9405 |
| median depth, Geant / analytic [cm] | 2.16 / 2.16 | 1.08 / 1.08 | 0.72 / 0.72 |
| 16 / 84 % [cm] | 0.51 / 6.68 (0.50 / 6.68) | 0.25 / 3.33 (0.25 / 3.34) | 0.17 / 2.22 (0.17 / 2.23) |
| 99 % [cm] | 21.04 (21.08) | 10.52 (10.54) | 6.99 (7.03) |

- Median vertex y = 0.04 mm, so the placement rule centres the vertices.
- Beam at the window: r50/90/99 = 7.1/10.2/12.9 mm, with 12 % outside
  r = 10 mm (penumbra). Aperture acceptance (thrown → accepted) is 0.950.
- The λ mean after the aperture is 4.85 Å, below the exit's 4.9 Å: the
  divergent long-λ rays are the ones that miss the guide exit.
- **Air.** The 300 mm air path from the aperture to the window costs
  0.6 % of the beam in ¹⁴N(n,p) and ~2 % in scattering. It also produces
  2.5×10⁻⁴/n of ¹⁴N(n,γ) (10.8 MeV γ), more than the Be window
  (1.4×10⁻⁴) or the Al ring (1.5–1.9×10⁻⁴). **A He bag or evacuated flight
  tube is worth considering.**
- The ⁶LiF scraper absorbs 2.8 % of the beam (halo beyond r = 12 mm).
- Capsule smoke test: 21 % of the Ø2 cm spot misses the Ø21 mm capsule.

**V1** (10⁵ pencil neutrons per point, uncollided transmission →
σ = −ln T / nt): passed; S(α,β) is live.

| slab | λ | σ, TS on | σ, free gas |
|---|---|---|---|
| Be 0.5 mm | 2 Å | 5.8 b | 6.6 b |
| Be 0.5 mm | 4 Å (past the 3.96 Å Bragg edge) | **0.50 b** | 7.9 b |
| Be 0.5 mm | 6 Å | **0.65 b** | 9.8 b |
| Al 0.5 mm | 2 Å | 1.65 b | 1.81 b |
| Al 0.5 mm | 4 Å | 2.33 b | 2.10 b |
| Al 0.5 mm | 6 Å (past the 4.67 Å edge) | **0.95 b** | 2.54 b |

Al 0.1 mm agrees. So the Be window scatters ~0.3 % of the H113 beam, not ~5 %.

**Born IPC generator** (20k each, truth opening angle, fraction above 109°):
M1 4.40 ± 0.14 % (ipc_born 4.61), E0 11.48 % (11.42), E1 9.31 % (9.38);
medians agree to 0.2°.

**³He(n,γ) bias:** the weighted (n,γ)/(n,p) is 9.5×10⁻⁹, i.e. σ ≈ 50 µb
(evaluated ~54 µb).

## Runs

| run | what | size | state |
|---|---|---|---|
| V0 | G1/G3/G5 unbiased + capsule | 10⁶ ×3 + 10⁵ | done |
| V1 | Be 0.5, Al 0.5, Al 0.1 × 2/4/6 Å × TS on/off | 10⁵ × 18 | done |
| S1test | G1–G6 × X17/M1/E0, V0 vertex libraries | 2×10⁴ × 18 | done (below) |
| C1 | G1–G6, ³He(n,γ) ×10⁵ | 10⁸ each (10 × 10⁷) | done, merged → `contracts/C1_<G>` |
| C1g | G1–G6, ³He(n,γ) ×10⁷ | 10⁸ each | done, merged → `contracts/C1g_<G>` |
| C1w | G1–G6, ³He ×10⁵ + walls ×300 / thick ×20 / air ×100 | 10⁸ each | done, merged → `contracts/C1w_<G>` |
| V0s | G5 with spot r = 17.5, 25 mm (S1s vertex libraries) | 2×10⁶ each | done |
| K1 | cosmics, G5 geometry | 1.3×10⁸ μ = 1 live day | done → `contracts/K1_G5` |
| S1 | G1–G6 × X17/M1/E0, C1 vertex libraries | 3.4×10⁶ per channel | done → `S1/summary/<G>_<ch>` |
| S1p | G1, G5 at y_w = 0 and y_w = −mean | 10⁶ per channel | done → `S1p/summary` |
| S1s | G5, spot r = 17.5, 25 mm | 10⁶ per channel | done → `S1s/summary` |
| S2 | Be-window internal pairs | | **not run**: ≤ 6.8 MeV total, removed by the Esum cut by construction |

**Feasibility answer: `FEASIBILITY_SIM.md`.** Table: `results/scan_v1.csv`.
Analysis outputs: `/eos/experiment/ntof/data/x17/ill/analysis/` (`v3_base`,
`v3_timing`, `variants_v3.csv`, `contract_ladders.csv`); small copies in
`ill/sim/analysis_v3/`. Scripts there run from
`/afs/cern.ch/work/d/dneff/git/x17_ill/analysis/` (`run_final.sh`).

### Reproducing the analysis

On lxplus, in `/afs/cern.ch/work/d/dneff/git/x17_ill/analysis/` (LCG_106
Python): `run_final.sh` (copy in `sim/lxplus/`) runs `sim_report.py` twice in parallel with `sim_variants.py`
(`v3_base`: σt 0.5 ns, 2τ 5 ns; `v3_timing`: σt 0.2 ns, |Δt| < 0.6 ns,
2τ 1.2 ns, cosmics × 10⁻²), then `make_scan.py`, into
`/eos/experiment/ntof/data/x17/ill/analysis/`.
The condor chain that produced the contracts and S1 summaries is
`sim/lxplus/pipeline*.sh` and `s1_driver.sh`. The other scripts in
`sim/lxplus/` are the one-off diagnostics behind numbers in
`FEASIBILITY_SIM.md`: `cosdiag.py` (cosmic Δt and energies), `ke.py` (lepton
KE of accepted X17), `contain.py` (energy containment), `trig.py` (trigger
rates), `placement.py` (S1p/S1s), `det.py` (detector capture budget),
`accstab.py` (accidental-estimate stability).

`ill_rates.py`: the PF1B wall factor k is now 2.71 (capture-weighted over
the H113 spectrum, mean λ 4.87 Å) instead of 2.36. `--contract` prints the
Geant4 ladder next to the analytic one (`contract_ladders.csv`).

### Overnight notes (2026-10-02)

- **C1w reductions** went over the 6 GB memory limit (11.6 GB used: the gap
  centroids added for the per-event table). They were resubmitted with 16 GB.
- **Transient EOS read errors.** One S1 reduction (G6_E0 job000) hung for
  90 min and one S1s reduction (r17.5_M1 job007) died on an EOS read error.
  Both were rerun by hand.
- **Placement and spot (S1p, S1s).** Both are second-order. Acceptance changes
  by < 5 % and the X17 nomline peak does not move.
  - G1 at y_w = 0 degrades nomline σ68 from 6.1° to 8.1° (centre-assumed
    vertex). xing_s is unaffected.
  - The G5 spot at r = 17.5/25 mm costs +0.3° nomline.
- **Background model fixes.** Accidentals are now an exact stratified sum, and
  the energy resolution is applied as a pass probability (no random smear) for
  every background; cosmic timing likewise. The first pass (`analysis/v1`)
  had sampling noise of up to ×2 in the Esum > 12 MeV accidentals.

### S1test (2×10⁴ per point; indicative only, 300–470 accepted X17 each)

X17, selection = both leptons in the gaps, different arms, pair-tag (legs in
≥ 2 arms). σ68 of θ_reco − θ_true [deg]:

| | G1 | G2 | G3 | G4 | G5 | G6 |
|---|---|---|---|---|---|---|
| acc × ε | 2.3 % | 1.9 % | 1.9 % | 1.5 % | 1.8 % | 1.4 % |
| vline (true vertex) | 2.2 | 1.2 | 2.6 | 2.9 | 3.5 | 3.8 |
| nomline (vertex at 0,0,0) | 6.3 | 5.8 | 5.5 | 5.5 | 5.3 | 6.2 |
| xing (per-event y on the axis) | 4.4 | 3.6 | 4.5 | 4.4 | 4.9 | 5.8 |
| first (direction at the gap) | 6.3 | 5.3 | 5.9 | 7.5 | 6.9 | 8.1 |

- With the true vertex, the wall dominates (mylar best). With the assumed
  vertex, the 1-bar source length costs ~1° against 3 bar. That is far less
  than the analytic §3 table implies (8.7° vs 2.9° per leg).
- The per-event axis crossing recovers 1–2° of the difference.
- Direction-only numbers use the simulation's ideal PCA directions, which
  are far better than the chambers' measured 11–26°.
