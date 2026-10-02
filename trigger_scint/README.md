# trigger_scint — fixing the trigger-scintillator acceptance

Started 2026-10-02. Facility-independent: what it takes to make the MX17
trigger scintillators cover the Micromegas acceptance, for any of the
facilities in this repo. Options compared:
- the n_TOF as-built stack;
- getting the liquid scintillators working;
- large 2 cm plastics;
- 4–10 cm plastics that also do the calorimetry.

The SiPM walls are kept and fully read out in every option.

**Read `TRIGGER_OPTIONS.md` first.** Headline: the as-built trigger accepts
2.3 % of X17 pairs. Four ~70–80 cm plastics give ~14 % (×6) for ~€80k. At 4–5
cm thick they also give ×7.7 on the ILL Esum > 13 MeV analysis, for ~€90k
(polystyrene) to ~€140k (PVT). The LS route is not worth pursuing. The SiPM
wall, not the Micromegas, sets the cap.

| file | what it is |
|---|---|
| `STATUS.md` | Run log and handoff: code/branch, lxplus paths, the T0/T1 runs, validation, open items for the next session |
| `TRIGGER_OPTIONS.md` | The write-up: acceptance vs size, thickness and calorimetry, optics/PMT, DAQ, costs, recommendation |
| `analyze.py` | Builds `out/options.csv` and the figures from the acceptance tables, the optics toy and the cost model |
| `costs.py` | Budgetary price model (EUR, low/central/high) with its public reference points |
| `optics_toy.py` | Photon ray-trace: light yield, uniformity and timing vs slab size and PMT readout -> `out/optics.csv` |
| `sim/trig_reduce.py` | Per ROOT file -> per-lepton table (MM entry, 20 SiPM bars, plastic W × L × T grid or as-built plastics + LS) |
| `sim/trig_accept.py` | Acceptance × efficiency for every option and the W × L × T scan -> `sim/accept/` |
| `sim/accept/` | The small outputs copied from EOS (`summary.json`, `scan_{X17,M1}.csv`) |
| `sim/lxplus/` | The condor reduction (`reduce.{sh,sub}`) and the first post-processing driver (`run_accept.sh`; see `STATUS.md`) |

```bash
python trigger_scint/optics_toy.py     # ~3 min -> out/optics.csv
python trigger_scint/analyze.py        # -> out/options.csv, out/figures/*.png (+ .csv)
python trigger_scint/costs.py          # price table
```

Simulation (lxplus):
- **code:** `MX17_Full_Geant`, branch `trigger_plastics` (from `ill`), which
  adds `--big-plastic U V T`, `--no-ls` and `--sipm-readout N SHIFT`;
- **clone:** `/afs/cern.ch/work/d/dneff/git/x17_trig/`;
- **runs:** `submit_ill.py --run T0|T1 --config G1 --mode pairs`, 10 × 100k
  per channel;
- **outputs:** `/eos/experiment/ntof/data/x17/ill/{T0,T1}/G1_{X17,M1}/`,
  reduced parts and acceptance in `/eos/experiment/ntof/data/x17/ill/trig/`.

Figures use the house style vendored in `../ill/figstyle.py`.
