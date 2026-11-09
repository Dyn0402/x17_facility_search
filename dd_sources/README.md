# dd_sources — intense 2.45 MeV D-D neutron sources (Phoenix/SHINE class, compact generators, D(d,n) accelerators)

**Update 2026-11-09 (Dylan: only existing beams, no money for new machines, no outreach for now):** call changed from KEEP AS BACKUP to **CLOSED for now**: a machine would have to be bought. Physics numbers stand.

**Read this first (2026-11-09):** a measured 3×10¹¹ n/s D-D generator with the 30 bar × 40 cm cell 35 cm from the source, a
shadow shield upstream of the cell, and the cell at 90° to the deuteron beam reaches **X17/IPC = 6.5×10⁻⁴ at 3σ in 50 days**
(big plastics; as built 1.8×10⁻³), 9.5 days to the ATOMKI strength, statistics-limited (IPC + cosmics). 50 cm is the robust choice:
8.5×10⁻⁴, 16 days. The catalogue's "×10 too weak" assumed 2.5 m; geometry fixes that. Call: **KEEP AS BACKUP**: no user programme exists for 3×10¹¹ D-D, the machine would have to be bought or contracted,
and the arm, room and correlated terms are estimates until a 2.45 MeV Geant4 run. Slides (built, not published): `out/dd-sources-x17-feasibility.html`.

| file | what |
|---|---|
| `FACILITY.md` | the machines, 2026 status, access, cost, sources |
| `FEASIBILITY.md` | the answer, source model, close-coupling correction, reach, sensitivities, scorecard, next steps |
| `dd_beam.py` | thick-target D(d,n), kinematics, geometry, reach through `soft_reach.py` → `out/dd_*` |
| `sens.py` | sensitivities, N5 correlated bound, capsule → `out/dd_sens.csv`, `dd_capsule.csv`, `dd_corr_bound.csv` |
| `dd_figs.py` | `out/dd_reach_vs_d.png`, `out/dd_geometry.png` (with .csv) |
| `deck/build_deck.py` | slide note → `out/dd-sources-x17-feasibility.html` |
| `DASHBOARD_PROPOSAL.md` | proposed `dashboard.py` / `facilities.csv` changes |

```bash
PY=~/PycharmProjects/nTof_x17/.venv/bin/python
$PY dd_sources/dd_beam.py --check   # reproduces bham_26_2m_pb5: 3.82e-4 / 1.177e-3
$PY dd_sources/dd_beam.py           # ~5 min
$PY dd_sources/sens.py
$PY dd_sources/dd_figs.py
$PY dd_sources/deck/build_deck.py
```

The Geant4 runs N5/G5/G6 and the engine are shared: [`survey/soft_sim/`](../survey/soft_sim/README.md).
