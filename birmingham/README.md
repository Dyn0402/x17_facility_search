# birmingham — HF-ADNeF, the 30 mA ⁷Li(p,n) source at the University of Birmingham

**Read this first (2026-10-27): `TARGET_GEANT.md`.** Full Geant4 of the target, the room and a shield wall.
- **Target:** no capsule, no balloon. The capture rate is the ³He inside the beam. The 30 bar Be/CFRP cell (87 L of ³He,
  ~217 k€) reaches the ATOMKI strength in **6.7 days** at 30 mA with the big plastics: X17/IPC 5.5×10⁻⁴ at 3σ in 50 d.
  The 1 bar mylar balloon matches its resolution (σ68 ≈ 11°; the vertex, not the walls, sets it) but holds ×30 less
  gas: 247 d. The n_TOF capsule: 58 d.
- **Background:** what floods the detector is the room (the beam returning from the dump and concrete) and the shield
  wall, not the target.
- **Wall:** the 20 cm BPE + 80 cm concrete + 5 cm Pb wall first modelled is not enough (28 d, DREAM 37 % live). +10 cm Pb
  and +10 cm borated PE on the exit recover it.
- **DREAM:** pair trigger only, 85 % live.
- **Scintillators:** the big slab takes 5×10⁷ hits/s and 33 µA at gain 10⁶, so run it at 10⁵.
- **New risk:** neutron recoils in the Micromegas, 0.6 cluster per arm per µs.

Slides: <https://dylan-neff.web.cern.ch/notes/birmingham-target-geant.html>.
**Target engineering (2026-10-29): `../he3_target/FEASIBILITY_PLAN.md`.** How to build, fill, approve and empty the ³He
cell. Build C re-sized to a pressure code costs ~8 % in days. Baseline: 30 bar R 4 Al-lined CFRP, 62 L, ~7 d (est), with a
closed cryopump gas loop. The ³He is not consumed (borrow it). Next Geant4: the code-sized cell and a 200 bar R 2 tube.
The first study (2026-10-20, beam-only re-weighting, 3.3×10⁻⁴) is `FEASIBILITY.md`:
<https://dylan-neff.web.cern.ch/notes/birmingham-x17-feasibility.html>.

| file | what |
|---|---|
| `FACILITY.md` | the facility record: site, accelerator, Li target, beam numbers, what hosting MX17 needs, sources |
| `TARGET_GEANT.md` | **the target choice and the full background in Geant4** (2026-10-27): targets, wall, room, DREAM, scintillators, Micromegas |
| `bham_targets.py` | the analytic target trade (³He in the beam, cost, walls) |
| `geant/` | the Geant4 analysis (`bham_geant.py` reach, `bham_rates.py` rates, `deck/`, `lxplus/` copies, `fetch_sel.sh`) |
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
