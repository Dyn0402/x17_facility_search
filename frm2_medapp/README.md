# frm2_medapp — the FRM II fission-neutron beam (MEDAPP / NECTAR, Garching)

**Read this first (2026-10-20):** the SR10 fission beam would reach **X17/IPC = 4.2×10⁻⁴ at 3σ in 50 days**
(big plastics; as built 5.4×10⁻⁴), ×3.6 past ATOMKI ⁴He, with its own Geant4 beam background. ~4 days of beam
reach the ATOMKI strength. The reactor has been off since March 2020 with no restart date; space for the arms
is the next question. Slides: <https://dylan-neff.web.cern.ch/notes/frm2-medapp-x17-feasibility.html>.

| file | what |
|---|---|
| `FACILITY.md` | the facility record: site, SR10 converter, beam numbers, status, what hosting MX17 needs, sources |
| `FEASIBILITY.md` | the answer, beam model, Geant4 singles, reach, open items (numbered, dated) |
| `medapp_beam.py` | neutron (Watt + 5 % intermediate) and γ (stand-in) spectra and rates → `out/medapp_*` |
| `deck/build_deck.py`, `deck/cartoon.py` | the slide note (→ `out/frm2-medapp-x17-feasibility.html`) and the beamline cartoon |
| `refs/` | MLZ JLSRF A18 (MEDAPP), A19 (NECTAR), Wagner 2011 slides, MLZ 2025 poster |

The Geant4 runs and the reach engine are shared with `birmingham/`: [`survey/soft_sim/`](../survey/soft_sim/README.md).

```bash
PY=~/PycharmProjects/nTof_x17/.venv/bin/python
$PY frm2_medapp/medapp_beam.py
$PY survey/soft_sim/soft_reach.py          # after survey/soft_sim/fetch_sel.sh
$PY frm2_medapp/deck/build_deck.py
python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py frm2_medapp/out/frm2-medapp-x17-feasibility.html \
    --slug frm2-medapp-x17-feasibility --force --deploy
```
