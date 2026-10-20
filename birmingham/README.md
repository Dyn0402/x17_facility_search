# birmingham — HF-ADNeF, the 30 mA ⁷Li(p,n) source at the University of Birmingham

**Read this first (2026-10-20):** with the cell 2 m from the Li, 2.8 MeV protons at 30 mA and 5 cm of Pb in a
Ø8 cm collimator, the reach is **X17/IPC = 3.3×10⁻⁴ at 3σ in 50 days** (big plastics; as built 1.0×10⁻³),
×4.5 past ATOMKI ⁴He, statistics-limited at full current, with its own Geant4 beam background. ~2.4 days of beam
reach the ATOMKI strength. The facility operates today, but has no beam port: the arms need ~50 cm of borated PE
between them and the target (an estimate; simulate the wall and room next). Slides:
<https://dylan-neff.web.cern.ch/notes/birmingham-x17-feasibility.html>.

| file | what |
|---|---|
| `FACILITY.md` | the facility record: site, accelerator, Li target, beam numbers, what hosting MX17 needs, sources |
| `FEASIBILITY.md` | the answer, beam model, Geant4 singles, reach (distance × Pb filter × E_p), the shield estimate |
| `bham_beam.py` | thick-target ⁷Li(p,n) 0° spectrum (slowing-down MC), rates through the spot, target γ, `shield()` → `out/bham_*` |
| `deck/build_deck.py`, `deck/cartoon.py` | the slide note (→ `out/birmingham-x17-feasibility.html`) and the facility cartoon |
| `refs/` | Wheldon, JINST 17 (2022) C10010 |

The Geant4 runs and the reach engine are shared with `frm2_medapp/`: [`survey/soft_sim/`](../survey/soft_sim/README.md).

```bash
PY=~/PycharmProjects/nTof_x17/.venv/bin/python
$PY birmingham/bham_beam.py                # (rerun after soft_reach.py for out/bham_shield.csv)
$PY survey/soft_sim/soft_reach.py
$PY birmingham/deck/build_deck.py
python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py birmingham/out/birmingham-x17-feasibility.html \
    --slug birmingham-x17-feasibility --force --deploy
```
