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
