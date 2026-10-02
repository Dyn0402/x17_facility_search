# trigger_scint — run log and handoff

State at 2026-10-02 (end of the first session). The answer is in
`TRIGGER_OPTIONS.md`. This file records how it was produced, and what to pick
up next.

## Code

- **Simulation:** `~/CLionProjects/MX17_Full_Geant`, branch
  `trigger_plastics` (branched from `ill` at `faac5ba`; local, not pushed).
  New options:
  - `--big-plastic U V T` [cm]: one wrapped PVT slab per arm in place of the
    two 20 × 30 × 2 cm bars. Same front face, centred on the pinwheel-shifted
    MM, scored as `BackScintL`.
  - `--no-ls`: omit the LS vessels and PMTs.
  - `--sipm-readout N SHIFT`: instrumented SiPM bars. The default `16 1` is
    n_TOF; all 20 bars is `20 0`.
- **lxplus clone:** `/afs/cern.ch/work/d/dneff/git/x17_trig/` (rsync copies
  of MX17_Full_Geant and MX17_Geant; build in `MX17_Full_Geant/build`).
  - Frozen binary: `bin/mx17_full_sim_trig1`.
  - Copies of `trig_reduce.py` and `trig_accept.py` at the top level.
  - Condor reduction in `condor/` (= `sim/lxplus/reduce.{sh,sub}` here).

## Runs (all G1 cell, ILL G1 vertex library `libs/C1_G1_gas.csv`)

| run | extra args | channels | jobs | where |
|---|---|---|---|---|
| T0 | `--sipm-readout 20 0` | X17 (`--ipc 0`), M1 (`--ipc 1 --ipc-multipole M1`) | 10 × 100k each | `/eos/experiment/ntof/data/x17/ill/T0/G1_{X17,M1}/` |
| T1 | `--big-plastic 78 120 10 --no-ls --sipm-readout 20 0` | X17, M1 | 10 × 100k each | `/eos/experiment/ntof/data/x17/ill/T1/G1_{X17,M1}/` |

- All 40 jobs finished with no errors. The raw ROOT is ~35 GB per T1
  channel.
- Reduced parts: `/eos/experiment/ntof/data/x17/ill/trig/{T0,T1}/G1_*/parts/`
  (85 MB).
- Acceptance tables: `/eos/experiment/ntof/data/x17/ill/trig/accept/`,
  copied to `sim/accept/`.
- **Overlap check:** 78 cm wide slabs at the surveyed arm positions pass.
  80+ cm was not tried and would hit the neighbouring arm's slab.

Reproduce:
```bash
# on lxplus, in x17_trig/MX17_Full_Geant (setup_lxplus.sh sourced)
python3 scripts/submit_ill.py --run T1 --config G1 --tag X17 --mode pairs --njobs 10 \
  --nevents 100000 --flavour longlunch --exe bin/mx17_full_sim_trig1 -- --ipc 0 \
  --pair-vertex-lib /eos/experiment/ntof/data/x17/ill/libs/C1_G1_gas.csv \
  --big-plastic 78 120 10 --no-ls --sipm-readout 20 0
# reduce: condor_submit sim/lxplus/reduce.sub  (list.txt = "<root>, <out.npz>, <tag>" per file)
# accept: python3 trig_accept.py --t0 $E/trig/T0 --t1 $E/trig/T1 -o $E/trig/accept
# locally: python trigger_scint/optics_toy.py && python trigger_scint/analyze.py
```

`sim/lxplus/run_accept.sh` is the first post-processing driver. It waits for
the sims, reduces with `xargs -P 10` on the login node, then runs
`trig_accept.py`. Its reduction step died silently when the ssh session
dropped, so the condor reduction replaced it. Keep its last line (the accept
step) and use condor for the rest.

## Validation

- **Against the ILL campaign (G1, 16 bars, no plastic requirement):** 11.8 %
  here vs 12 % in `ill/FEASIBILITY_SIM.md`.
- **MM two-arm acceptance:** 27.6 % with the active-area cut
  (|u| < 199.7, |v| < 180 mm), against 32 % there without it. The drift-gas
  volume extends to ±203.4 mm, beyond the active area. The ILL numbers did
  not apply the active-area cut, which inflates them by ~15 %.
- **Lepton reach:** of leptons crossing the MM active area, 86 % reach the
  plastic plane and 82 % pass 1.67 MeV. Those not reaching it have median
  7.8 MeV, so the loss is geometry and scattering, not range-out.

## Open / next session

1. **Reach with the new geometry (ILL).** Run C1 (beam backgrounds) and K1
   (cosmics) with the T1 geometry, with the slab cut to the chosen size and
   thickness, then rerun `ill/sim_feasibility.py`.
   - Needs `ill_accounting.py` / the arm tables to read the big-plastic grid,
     or a T2 run at the chosen size.
   - Expected up to ~2.5–2.8× better reach from ×6–8 signal, but cosmics and
     accidentals grow with plastic area.
2. **Trigger rate in a big H-rich slab at a reactor** (neutron captures and
   Compton in the plastic): comes from the same C1-on-T1 run.
3. **Pick a size and thickness, then build T2** at exactly that size, e.g.
   75 × 75 × 4 or 5 cm, as a check on the cut-out method.
4. **Quotes:**
   - Eljen/Luxium (PVT) and Nuvia/Epic (PS) for 4 × 78 × 80 × {2, 4, 5} cm;
   - Hamamatsu/ET for 8 × 3" PMTs;
   - CAEN for FERS-5200 (A5202 vs A5204) ×3;
   - PETsys as the alternative.
   - Confirm the maximum single-piece width at 4–5 cm.
5. **Prototype:** one slab with two-ended readout on the cosmic bench, with
   the M3 telescope giving position. This anchors `optics_toy.py`'s absolute
   pe/MeV and timing.
6. **Mechanics:** the real frame clearance for 70–78 cm slabs. Thick slabs
   weigh 25–32 kg.
7. **Other targets:** the acceptance used the ILL G1 vertex distribution.
   Rerunning T0/T1 pairs for the n_TOF capsule, or another facility's target,
   is one `submit_ill.py --config capsule` per channel.

---

## Session 2 (2026-10-02 afternoon): backgrounds with big slabs — IN PROGRESS

Question (Dylan): at the ILL, does a large, thick (H-rich) trigger slab bring
so much background that the pair search drowns?

### What is running (all on lxplus, nothing local)

- **Geant4 TB campaign** (`sim/lxplus/submit_tb.sh`), G1 cell, 20 SiPM bars,
  no LS. Outputs `/eos/experiment/ntof/data/x17/ill/TB/G1_<geom>_<kind>/`.
  - geoms: `P2` 70×70×2, `P5` 75×75×5, `P5L` P5 + 2 mm ⁶LiF wrap,
    `P5B` P5 + 2 mm B₄C wrap;
  - kinds: C1 (beam, ³He(n,γ) ×1e5), C1w (+ wall/air biasing), C1g
    (³He(n,γ) ×1e7), X17/M1/E0 (10 × 1e5 pairs), K1 (cosmics, P2 and P5 only,
    40 × 1.3e6 μ).
  - binaries: `x17_trig/MX17_Full_Geant/bin/mx17_full_sim_trig2` (P2, P5),
    `..._trig3` (P5L, P5B; includes the arm-ID fix below).
- **Pipeline** `x17_trig/pipeline_tb.sh` (nohup on lxplus989, log
  `x17_trig/pipeline_tb.log`): reduces + merges into `TB/contracts/<kind>_<geom>`
  and `TB/summary/<geom>_<ch>`. Restart it if it died: it is idempotent.
- **Analysis driver** `x17_trig/analysis/run_bkg.sh` (nohup on lxplus989):
  one `bkg_reach.py` per geometry once its inputs are merged, air × 1 and
  × 0.1, gates 0/10/25/50/100 ns, menus sipm2/strict, Esum > 13 MeV.
  Output `TB/analysis/<geom>[_air0.1].json` + `<geom>.log`.
  Takes ~40 min per geometry.
- If the login-node processes are gone (reboot / token expiry), rerun:
  `cd x17_trig && nohup setsid bash pipeline_tb.sh > pipeline_tb.log 2>&1 &`
  then `cd analysis && nohup setsid bash run_bkg.sh [geoms] > run_bkg.log 2>&1 &`.
- **Watch for held reductions:** P5_K1 reductions needed ~18 GB (released at
  30 GB, cluster 4353832). The P5* C1/C1w reductions request 16 GB and may
  need the same: `condor_q -hold`, then `condor_qedit <id> RequestMemory 30000;
  condor_release <id>`.

### Code changes

- MX17_Full_Geant `trigger_plastics` (local commits, not pushed):
  `200fd70` `--plastic-shield MAT:mm` (LiF6 or B4C box around each plastic);
  `0c348d7` arm ID one level further up for shielded plastics (before it,
  every shielded slab hit went to arm 0; the first P5L/P5B runs were deleted
  and resubmitted).
- `bkg_reach.py`: the ill/sim_feasibility model plus slab singles, hardware
  trigger rates, **in-gate pile-up** (compound Poisson of foreign slab
  deposits in a window G, added to signal and every background), and an air
  (¹⁴N) capture scale. G = 0, air 1 reproduces FEASIBILITY_SIM exactly
  (5.18e-2 base, 8.40e-3 timing).
- `bkg_figs.py`: figures/tables from `sim/bkg/*.json` (copy the JSONs from
  `TB/analysis/`).

### Results so far

- Captures in the slabs (smoke test, 2e5 n): as-built plastics 2.5e-4 /abs n;
  75×75×5 2.1e-3 (×8.5 → ~2e7 H(n,γ)/s at 1e10 n/s). 2 mm ⁶LiF removes them.
  Gap rate (MM occupancy) roughly doubles with the bare thick slab.
- **In-gate pile-up is a new background class, already for the as-built
  detector.** A soft correlated two-arm event (true Esum ~1–6 MeV) plus a hard
  (8–11 MeV) slab single in the window passes Esum > 13 MeV. Timing scenario
  (σt 0.2 ns + μ veto), best menu:

  | as built | G = 0 | 10 ns | 25 ns | 50 ns | 100 ns |
  |---|---|---|---|---|---|
  | air × 1 | 8.4e-3 | 1.12e-2 | 1.31e-2 | 1.57e-2 | 2.02e-2 |
  | air × 0.1 (He flight tube) | 7.3e-3 | 9.0e-3 | 1.07e-2 | 1.28e-2 | 1.62e-2 |

  - 92 % of slab singles > 8 MeV are air ¹⁴N(n,γ) (5466 raw events).
  - The MC statistics of this class are thin (n_eff ≈ 2–11). Order of
    magnitude, not precision.
  - G is the double-pulse resolving time: ~10 ns with waveform digitizers on
    the slab PMTs, 50–100 ns with a shaping QDC. Segmenting a slab into N bars
    divides the effective G by N.
- P2 slab singles: 9.9e-5 /abs n/arm vs 8.2e-5 as built (similar).

### Still to do when the runs finish

1. Copy `TB/analysis/*.json` to `sim/bkg/`, run `bkg_figs.py`.
2. Compare P2 / P5 / P5L / P5B against as built: reach vs G, trigger rates,
   MM occupancy, budget at the best rate.
3. Not simulated, to state in the write-up: hall γ background. 1 µSv/h of
   ~1 MeV γ ≈ 60 γ/cm²/s → ~3e5 Hz on a 75×75 face. Ask ILL for the PF1B
   casemate dose rate or measure it.
4. Write `BACKGROUNDS.md` (the answer), update README / TRIGGER_OPTIONS
   recommendation, then commit.
