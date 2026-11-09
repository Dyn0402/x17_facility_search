# bnct_accel — accelerator BNCT machines as X17 sources

**Read this first (2026-11-09):** overall call **WATCH**, not a top-3 option. A bare ⁷Li target is ×2–4 better in reach than the moderated port (Nagoya-class 15 mA, 2 m, 5 cm Pb:
X17/IPC = 5.1×10⁻⁴ at 3σ in 50 days, big plastics; as built 1.6×10⁻³; 5.7 d to ATOMKI), but no hospital machine offers one, since the target sits inside the beam-shaping assembly. The bare sources that
exist are Birmingham (the reference) and BINP VITA (operating; CERN ended relations with Russian institutes on 30 Nov 2024). The moderated port, replacing the ILL-scaled 2.5×10⁻³ in the catalogue, reaches
**1.3×10⁻³** (bracket 8.3×10⁻⁴–1.8×10⁻³; 39 d to ATOMKI; DREAM live 0.5; as built 3.0×10⁻³), with the fast tail supplying up to 64 % of the captures, and with a sub-keV background proxy that can push it to 2.6×10⁻³.
What would change it: a yes from Nagoya NUANS (or another Li research machine) to run without the BSA. Slides (built, not published): `out/bnct-accel-x17-feasibility.html`.

| file | what |
|---|---|
| `FACILITY.md` | every machine: accelerator, target, 2026 status, research time, whether a bare target is reachable; port/room facts; access; unknowns marked (ask); sources |
| `FEASIBILITY.md` | the answer, reproduction check, beam model (sub-keV handling), scan, walls, scorecard, what would make it top-3, next steps |
| `bnct_accel_beam.py` | bare (`birmingham/bham_beam.py`, `franz/franz_beam.py`) and moderated sources, through the shared engine → `out/bnct_*` |
| `deck/build_deck.py` | the slide note → `out/bnct-accel-x17-feasibility.html` |
| `DASHBOARD_PROPOSAL.md` | proposed text for `survey/dashboard.py` and `facilities.csv` (not applied) |
| `out/bnct_reach.csv` | reach for every configuration (columns key, hw, days, rho3, rho3_floor, signal, as `dashboard.g4_reach` reads, plus limit, live, occ, rho3_room) |

The Geant4 runs (N5/G5/G6) and the engine are shared: [`survey/soft_sim/`](../survey/soft_sim/README.md). The bare and moderated sources are added here without changing it.

```bash
PY=~/PycharmProjects/nTof_x17/.venv/bin/python
bash survey/soft_sim/fetch_sel.sh                    # Geant4 tables from EOS, once
$PY bnct_accel/bnct_accel_beam.py --check            # reproduce the published Birmingham rows (ratio 1.0000)
$PY bnct_accel/bnct_accel_beam.py                    # ~8 min: full scan → out/bnct_*
$PY bnct_accel/deck/build_deck.py
```

Caveats: the moderated spectrum is an ESTIMATE (no broad-band port spectrum of an accelerator machine is published); the engine is beam-only (`rho3_room` applies Birmingham's ×1.67 room factor as an ESTIMATE).
