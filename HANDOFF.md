# Handoff

## ILL conservative reach — segments, collinearity, end cap — updated 2026-10-06 (dylan-MS-7C84)

**Resume:** condor jobs for collinearity (4399226) + ring end-cap sims (4399221-4) — collect results, then reduce/merge/reach the ring variants.

**Goal:** redo the ILL X17 reach with n_TOF-like hardware, and test two levers. The hardware is ~5 ns SiPM-wall timing per arm, a per-arm SiPM×plastic coincidence trigger with no energy-sum trigger, and the DREAM live time. The levers are an offline Micromegas segment selection and removing the Al end cap. Write-up: `ill/FEASIBILITY_SIM.md` §10.

**Done (all G1, Esum > 13 MeV offline, 50 days, 3σ reach; CSVs in `ill/sim/analysis_v3/cons/`):**
- Validation: `conservative.py` reproduces the old 5.18e-2 (baseline) and 8.34e-3 (200 ps + veto).
- Conservative hardware, no segment cut: 5.3e-2 (per-arm trigger 87 Hz, live 0.97). A SiPM-wall-only trigger runs at 6 kHz with live 0.36, giving 9.3e-2. With end-cap captures removed (oracle): 3.6e-2.
- Segment cut (both arms' segments point within D of the beam axis, y in [-60, 200] mm), conservative hardware + μ veto:
  2°/25 mm 1.6e-2 (end cap off 1.0e-2); 5°/40 mm 1.7e-2 (1.1e-2); 10°/60 mm ~2.8e-2 (1.4e-2); 20° ≥ 3.9e-2.
  Accidentals ↓ ~20×, cosmics ↓ ~7×. X17 keeps ≤ 81–85 % even at perfect direction (scattering before the gap).
- With 5°/40 mm + end cap off: 1 ns → 8.7e-3, 2 ns → 9.7e-3, no μ veto → 3.5e-2. Remaining per cycle: COS 11k > IPC 6k ≈ ACC 6k vs X17@ref ~500.
- Dylan: cosmic-bench MM angular resolution < 3°, so use the 2–5° rows (~1.6e-2, ~1.0e-2 with no Al end cap).
- Upstream Al ring (He3Cell_EndUp, 1.8e-4/abs n) dominates the end-cap captures; the downstream cap is 5e-5.

**In progress (remote, keeps running):**
- Collinearity veto grid, cluster 4399226 (12 jobs) → `$C/coll_<deg>_<D>_0_c<α>.csv`, logs in `/afs/cern.ch/user/d/dneff/condor/ill/cons/coll/logs/`. α = 0/10/20/30°, segs 2:25, 3:30, 5:40, rows "per-arm" (+veto) and "no veto".
- End-cap geometry sims, clusters 4399221–4399224 (40 jobs × 1e7 n, ~3 h each) → `$E/C1{,w}/G1_ringCFRP` (ring + cap CFRP) and `$E/C1{,w}/G1_ringLiF` (Al + 2 mm ⁶LiF gas-side liner on ring and cap). Binary: `x17_ill/MX17_Full_Geant/bin/mx17_full_sim_ring`, built from MX17_Full_Geant branch `ill_ring`.
- `$E` = /eos/experiment/ntof/data/x17/ill, `$C` = $E/analysis/cons. The local driver `ill/sim/lxplus/ring_chain.sh` died with the session; rerun it, or do its steps by hand (below).

**Next steps:**
1. Collinearity: `ssh lxplus 'grep "3σ" /afs/cern.ch/user/d/dneff/condor/ill/cons/coll/logs/*.out'`; copy the CSVs to `ill/sim/analysis_v3/cons/`. Key question: can collinearity replace the ceiling panel?
2. Ring variants: once 40 `Run Summary` logs exist, run `ill/sim/lxplus/ring_chain.sh` locally (light ssh only). It submits `submit_reduce_ill.py --kind accounting` + `seg_submit.sh C1/G1_ringCFRP ...`, then `merge_submit.sh C1:G1_ringCFRP ...`.
3. Then reach: `bash cons_submit.sh ring "ringCFRP_3_30|--variant ringCFRP --segs 3:30:0 --coll 20 --hw per-arm" "ringLiF_3_30|--variant ringLiF ..." "base_3_30|--segs 3:30:0 --coll 20 --hw per-arm"` (pick α from step 1). Compare with the end-cap oracle.
4. Fold into the slides (`ill/deck/build_deck.py`) and FEASIBILITY_SIM §10; update the ILL memory.

**Gotchas / decisions:**
- Heavy work only as condor jobs. Four interactive runs on lxplus969 drew a PSI memory warning (2026-10-06). Jobs loading K1 need ~12 GB.
- `conservative.py` monkeypatches `sim_feasibility.arm_ok / s1_select / two_arm_events`. The segment flag is `segok` and the smeared directions `segd`, with no leading "_" so `SF.concat` keeps them.
- Segments use the dominant track's PCA (0.5 mm hit smear), plus a Gaussian direction smear σθ = detector term. Gas scattering is already in the MC.
- The single-track cut (fdom > 0.7) costs ~20 % of X17 for little gain; dropped.
- MC noise: neighbouring cuts scatter ±30 % (≈370 raw hard singles carry the accidental tail). The ³He(n,γ) template has 1 raw two-arm event left; it flips 0 ↔ ~150.
- The end-cap "oracle" zeroes weights of capvol He3Cell_End*; it is an upper bound on the gain (replacement assumed γ-free). The ring sims test real materials.
- Timing: n_TOF wall ~5 ns/arm, ~7 ns on Δt (nTof_x17/ntof_cosmics/README.md). The cut is |Δt| < 2.5σ_Δt, and the accidental half-window equals the cut. The hardware coincidence window is 50 ns (assumed).

**Key files & commands:**
- `ill/sim/lxplus/seg_reduce.py`: per-arm MM segment fit from ROOT (parts_seg/); `seg_submit.sh [run/cfg ...]` submits it.
- `ill/sim/lxplus/conservative.py`: the reach driver (`--segs deg:D:fq --coll α --variant tag --hw substr`); `cons_submit.sh <name> "<tag>|<args>" ...`.
- `ill/sim/lxplus/seg_diag.py`: pass fractions vs σθ, D (→ cons/seg_diag_G1.json).
- `ill/sim/lxplus/merge_variant.sh`, `merge_submit.sh`, `ring_chain.sh`: reduce/merge chain for geometry variants.
- Copies of the scripts run from `/afs/cern.ch/work/d/dneff/git/x17_ill/analysis/` (scp after edits).

## trigger_scint — big-slab backgrounds at the ILL — updated 2026-10-02 (dylan-MS-7C84)

**Goal:** decide whether a large, thick (H-rich) trigger slab drowns the ILL
pair search in background, compared with the detector as built (P2 70×70×2,
P5 75×75×5, P5L/P5B = P5 + 2 mm ⁶LiF/B₄C wrap). The answer goes in
`trigger_scint/BACKGROUNDS.md`. Full run log: `trigger_scint/STATUS.md`
("Session 2" and "Session 2 restart").

**Done:**
- All TB Geant4 runs finished. Analysis done for asbuilt (air ×1, ×0.1) and P2.
  JSONs are in `trigger_scint/sim/bkg/`, and `bkg_figs.py` has been run on them.
- P2 result: no better than as built at Esum > 13 MeV (timing reach 1.6e-2 vs
  8.4e-3). That is expected: a 2 cm slab has as-built signal acceptance.
- Restart at 18:30: released the held P5_C1w reductions at 40 GB, and dropped
  4 truncated raw files (merged partially with `merge_partial.sh`).

**In progress / where it stopped (on lxplus926, nohup):**
- `x17_trig/pipeline_tb.sh`: P5L/P5B C1w reductions running (condor 4354874,
  4354876, 42 GB). P5_C1w reduction (4354038) has left the queue and should
  merge on the next pass.
- `x17_trig/analysis/run_bkg.sh P5 P5L P5B`: each geometry starts once its
  `.merged` markers exist and takes ~40 min. Output:
  `/eos/experiment/ntof/data/x17/ill/TB/analysis/{P5,P5L,P5B}[_air0.1].json`
  and `.log`.
- Expected done ~20:30–21:00 on 2026-10-02.

**Next steps:**
1. Check that the outputs exist. If the drivers died, restart them (commands
   in STATUS.md) and check `condor_q dneff -hold`.
2. `scp lxplus:/eos/experiment/ntof/data/x17/ill/TB/analysis/P5*.json trigger_scint/sim/bkg/`,
   then run `python trigger_scint/bkg_figs.py`.
3. Compare P2/P5/P5L/P5B with as built: reach vs gate G, trigger rates, MM
   occupancy, budget.
4. Write `trigger_scint/BACKGROUNDS.md`. Include the unsimulated hall-γ
   caveat (STATUS.md). Update README and the TRIGGER_OPTIONS recommendation,
   then log it on the x17 board.

**Gotchas / decisions:**
- C1w reductions need ~36 GB. The pipeline now asks 40 GB.
- The truncated raw files (P5_C1 job008, P5_K1 jobs 003/024/032) were not
  rerun. The merge normalises by summed N.sim, so they cost statistics only.
  `pipeline_tb.sh` keeps looping on those two directories, which is harmless.
- `lxplus989` and `lxplus926` can't be reached by name (host key); use `ssh lxplus` and work from AFS.

**Key files & commands:**
- `trigger_scint/bkg_reach.py` — reach model with pile-up (runs on lxplus).
- `trigger_scint/bkg_figs.py` — figures and tables from `sim/bkg/*.json`.
- `trigger_scint/sim/lxplus/{submit_tb,pipeline_tb,merge_partial,run_bkg}.sh` — copies of the lxplus drivers.

## ILL rate vs DREAM dead time — updated 2026-10-02 (dylan-MS-7C84)

**Goal:** check whether the DREAM DAQ, which reads full Micromegas waveforms for the
TPC tracking, limits the usable ILL absorbed rate. Dylan feared it would change
the reach by orders of magnitude.

**Done (analysis only; no change to the feasibility code yet):**
- **DREAM limits**, from `~/PycharmProjects/nTof_x17_DAQ/docs/REPORT_2026-07-28_pulser_daq_characterization.md`,
  `DAQ_OPTIMIZATION_SUMMARY_2026-07-23.md`, `CLOCK_RATE_SCAN_2026-07-23.md`,
  `CLOCK_WINDOW_RESULT_2026-07-24.md` and `METHOD_readout_window_optimization.md`:
  - The ceiling is ~83 MB/s **per FEU**, wire-limited. It is not set by IPD, host, network or disk.
  - RAW production point (20 samples × 60 ns = 1.2 µs, Hwm 1): **3.35 kHz max, τ ≈ 298 µs** per event.
    Readout is non-paralysable, one event at a time, so live = 1/(1 + f·τ).
  - τ scales linearly with the number of samples.
  - ZS reached 10.8 kHz at 32 samples on the pulser. ZS at real occupancy is unmeasured, and the
    `PedSub` double-subtraction question is still open.
  - The 20-sample window holds 95 % of the drift charge at 700 V drift.
- **Trigger rate per 10¹⁰ absorbed n/s**, G5 tables, from `ill/sim/trig_ladder.py`:

  | trigger | rate | X17 kept |
  |---|---|---|
  | bare SiPM 0.5 MIP, both arms | 5.6 kHz | 100 % |
  | + ≥ 1 plastic (n_TOF-like menu) | ~1.1 kHz | 99 % |
  | + plastic in both arms | ~110 Hz | 66 % |
  | arm energy > 1 MeV, each arm | 1.2 kHz | 95 % |
  | arm energy > 2 MeV, each arm | ~120 Hz | 91 % |
  | sum of the two arms > 8 MeV | ≲ 110 Hz | 100 % |

- **Live fraction** (cosmics ~16 Hz added):
  - 2 MeV per-arm threshold: 0.97 at 0.9e10 n/s, 0.93 at 1.9e10, with the 1.2 µs window.
  - Same threshold, 4.8 µs window: 0.87 and 0.78.
  - Bare SiPM trigger, 1.2 µs window: 0.40 and 0.24.
  - The n_TOF-like menu: ~0.78 at 0.9e10.
  - All fitted components scale with live time, so reach ∝ 1/√live.
- **Conclusion:** DREAM costs an O(1) factor, not orders of magnitude, as long as the hardware
  trigger cuts on arm energy at ~2 MeV.
  - With that cut: ~2 % in reach (1.2 µs window), ~7 % (4.8 µs).
  - Worst case, a bare trigger at 1.2 µs: ~×1.6 in reach.

**In progress / where it stopped:** answered in chat; not yet written into `ill/FEASIBILITY_SIM.md`.
That file and `ill/README.md` have uncommitted edits from another session, so they were left untouched.
Open question to Dylan: what drift window the ILL TPC needs (the study only went to 4.8 µs).

**Next steps:**
1. Add a DREAM live-time factor to `ill/sim_feasibility.py` `model()`: τ = 298 µs × n_samples/20,
   trigger rate per absorbed n from the menu. Then re-optimise the rate and redo `scan_v1`.
2. Run a larger **unbiased** C1 sample on lxplus to measure the trigger rate above 2 MeV per arm.
   It currently rests on one unit-weight Monte Carlo row.
3. In `ill/ill_rates.py`, set `DREAM_MAX_HZ` from 1e3 to the measured 3.35 kHz (RAW, 20 samples),
   scaled by n_samples.
4. Write it up as a new §10 in `FEASIBILITY_SIM.md`, plus a slide in the deck (`ill/deck/build_deck.py`).

**Gotchas / decisions:**
- The 5.5 kHz in FEASIBILITY_SIM §2 is the SiPM-only menu. It is not a realistic ILL trigger.
- A plastic-in-both-arms trigger loses 34 % of X17, because the leptons often miss the plastic.
  Use arm energy (sum of the arm's scintillators) or a two-arm sum instead.
- The ILL hall's ambient γ and fast-neutron rate is unknown (`ill/FACILITY.md`). It could raise the
  low-threshold singles above the Monte Carlo.

**Key files & commands:**
- `cd ill && PYTHONPATH=. python sim/trig_ladder.py` — the trigger ladder (uses local
  `sim/contracts/C1_G5` and `sim/s1test/G5_X17`)
- `ill/sim_feasibility.py` — reach model (no DAQ live time yet)
- `ill/beam_spot.py` — beam rate vs spot diameter (Ø2 cm ≈ 1.9e10 n/s)

## he4_bag — ³He cell skin choice (Al foil) — updated 2026-10-02 (dylan-MS-7C84)

**Goal:** choose a 1 bar ³He cell skin that stops ³He permeation without adding neutron-capture
background or lepton scattering. Dylan's questions: alternatives to Al, the thinnest foil, what the
scattering "base" is, and whether 1 bar needs any strength.

**Done (analytic; published):**
- `he4_bag/he4_bag.py` §6 (metals, foil_gauge, chord_budget, hoop) → `he4_bag/out/{metals,foil_gauge,chord_budget,chord_ladder,hoop}.csv`.
- Slides 11–15 added to the note, republished at https://dylan-neff.web.cern.ch/notes/ill-he4-bag-3he-leak.html.
- `he4_bag/README.md` §6; pointers in `ill/FEASIBILITY_SIM.md` §5 and §9, `ill/README.md`, and the `vessel_design/mylar_wrap_vessel.py` docstring.
- Results:
  - The skin is already outside the beam (R 40 mm vs r99 12.9 mm) and adds ~1e-8 captures/n.
  - The Al that matters is the 8 mm end caps: upstream cap + ring are in 63 % of G1 accidentals.
  - Al is the right metal (only Be is better, and it can't be wrapped).
  - Skin: 12 µm PET + 6–7 µm converter foil, no PE sealant.
  - Scattering base: Micromegas 9 µm Cu 39 %, air 33 %, skin 8 %.
  - ±50 mbar is fine with the PET as the load layer. The cell can't be pumped out to fill it.

**Next steps:**
1. Geant4 (ILL branch of MX17_Full_Geant, lxplus): run C1 on G1 with the laminate skin. This needs a
   two-layer `--skin`; `Al:0.007` alone gives a bound.
2. Geant4: run G1 with the upstream Al cap lined with ⁶LiF, or trimmed, then rerun `ill/sim/lxplus/acc_sources.py`.
3. Check that the 9 µm Cu in the Micromegas entrance is the drift cathode, and whether it can be aluminised.
4. Bench-leak-test a short PET/Al prototype with a He leak detector.

**Gotchas / decisions:**
- Pinhole densities, thinnest foils and yields are catalogue-level (order of magnitude). The barrel
  crossing rate (1e-4/n) is analytic.
- Neither run is set up yet.

**Key files & commands:**
- `python3 he4_bag/he4_bag.py && python3 he4_bag/make_he4_bag_deck.py`
- `python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py he4_bag/out/he4_bag_deck.html --slug ill-he4-bag-3he-leak --force --deploy`
