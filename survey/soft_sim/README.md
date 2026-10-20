# soft_sim — Geant4 beam background for continuous soft-neutron sources

Shared by the two dedicated studies, [`frm2_medapp/`](../../frm2_medapp/README.md) (FRM II fission beam) and
[`birmingham/`](../../birmingham/README.md) (HF-ADNeF ⁷Li(p,n)). It replaces the survey's "one big unknown"
(`survey/SURVEY.md` §4.1: singles from < 3 MeV neutrons, bracketed by "Geant4 N4" and "flat") with two
broad-band Geant4 runs that every soft source is re-weighted from.

## Runs (2026-10-20)

MX17_Full_Geant branch **`soft`** (from `nfs`; `8f96537`): `--beam-particle gamma` for the NFS gun,
`submit_nfs.py --spectrum`, log-flat gun spectra `data/beam/soft_logflat_{n,g}.csv`. Binary
`…/work/git/x17_nfs/MX17_Full_Geant/bin/mx17_full_sim_soft_8f96537`. Same cell, arms and vacuum flight tube as
the NFS N4 run (`ganil_nfs/FEASIBILITY_SIM.md` §4).

| run | sample | what | events |
|---|---|---|---|
| N5 | `beam_soft[_bigP]` | neutrons, dN/dE ∝ 1/E on 1 keV–20 MeV, `--force-beam --roulette 0.2 0.05` | 300 × 3×10⁵ each |
| G5 | `beam_gamma[_bigP]` | photons, ∝ 1/E on 0.1–20 MeV, `--beam-particle gamma --roulette 0.2 0.05` | 200 × 10⁶ each |

Reduced in the job (`nfs_beam_reduce.py`, per-arm time clusters), merged with
`lxplus/soft_beam_merge.py` (`nfs_beam_merge.py` + every leg cluster `lg_*` and trigger pair `tr_*`) by
`lxplus/soft_pipe.sh merge` into `/eos/experiment/ntof/data/x17/nfs/sel_soft/`. Copy them here with
`./fetch_sel.sh`.

## Analysis

`soft_reach.py`: per source (neutron + γ spectra and rates through the Ø8 cm spot), every Geant4 row is
re-weighted by rate·f(E)/g(E)/N_gen; accidentals from the source's own singles, the correlated term from its
own two-arm events, DREAM live time and Micromegas occupancy, the NFS signal/IPC/cosmic tables; DC θ fit;
best throttle. Outputs `out/soft_reach.csv`, `out/soft_components.csv`, `out/soft_throttle.csv`.

```bash
./fetch_sel.sh
~/PycharmProjects/nTof_x17/.venv/bin/python survey/soft_sim/soft_reach.py
```

`deck_common.py`: the Europe map and cartoon pieces used by both slide notes.
