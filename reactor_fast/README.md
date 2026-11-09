# reactor_fast — operating reactor fast and epithermal beams

**Update 2026-11-09 (Dylan: only existing beams, no money for new machines, no outreach for now):** TAPIRO becomes WATCH and the ENEA enquiry is on hold. LVR-15 is the backup that exists.

**Read this first (2026-11-09):** no operating reactor has a MEDAPP-class fast beam today. Epithermal BNCT beams (LVR-15, THOR, RA-6) give 0.8–1.2×10⁻³ in the shared engine (big plastics, 50 d),
replacing the catalogue's ILL-scaled 2.5×10⁻³, but depend on sub-keV neutrons being quiet (×10 assumption gives 3×10⁻³). **ENEA's TAPIRO** (5 kW fast source reactor, Rome) reaches **4.8×10⁻⁴**
(5.1 d to ATOMKI, ESTIMATE, as built 1.4×10⁻³) *if* a straight fast channel to the core is opened with 5 cm of Pb in place: comparable to MEDAPP, which has been off since 2020, but a concept that needs a reactor modification. Call: KEEP AS BACKUP (class), PURSUE an enquiry to ENEA.

| file | what |
|---|---|
| `FACILITY.md` | survey of all candidates, verified 2026 status, sources, contacts |
| `FEASIBILITY.md` | answer, flux grid (what a beam must deliver), beams, sub-keV treatment, scans, scorecard |
| `reactor_fast_beam.py` | beam models + reach with the shared engine (`survey/soft_sim/soft_reach.py`) → `out/rf_beam.csv`, `rf_reach.csv`, `rf_flux_grid.csv`, `rf_engine_check.csv` |
| `rf_scans.py` | cells, capture budget, spectra figure, `--refresh` to re-score keys → `out/rf_cells.csv`, `rf_budget.csv`, `rf_spectra.{csv,png}` |
| `deck/build_deck.py` | slide note → `out/reactor-fast-x17-feasibility.html` |
| `DASHBOARD_PROPOSAL.md` | text for `survey/dashboard.py` and `survey/facilities.csv` |

```bash
PY=~/PycharmProjects/nTof_x17/.venv/bin/python
$PY reactor_fast/reactor_fast_beam.py     # ~10 min (engine check, scans)
$PY reactor_fast/rf_scans.py
$PY reactor_fast/deck/build_deck.py
```
