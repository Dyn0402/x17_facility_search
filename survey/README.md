# survey — every neutron facility in the world, triaged for the ³He X17 search

Started 2026-10-20. Which neutron facilities could reach ATOMKI's X17 strength with the MX17 apparatus
and a ³He target in ~weeks? The best-studied facility of each class (ILL PF1B, cold; GANIL NFS, fast) is
carried over to every other facility with two scaled models, and the rest are eliminated or put on a
"potential" list for a dedicated Geant4 study.

**Read first: `SURVEY.md` §0. Every number and its source: `SOURCES.md`.**

| file | what it is |
|---|---|
| `SURVEY.md` | The write-up: method, the yield curve, the thermal class, the fast class, the catalogue, the potential list, open questions, sources |
| `survey_yield.py` | IPC pairs per neutron entering the cell vs E_n (ENDF/B ³He, Born α), the source spectra -> `out/yield_vs_En.*`, `out/spectra_summary.csv` |
| `survey_absorbed.py` | Cold/thermal/epithermal beams on the ILL Geant4 rate walls -> `out/absorbed_reach.*` |
| `survey_fast.py` | Fast sources: the NFS Geant4 analysis re-weighted to each source's spectrum, intensity and time structure, throttled to its best rate -> `out/fast_reach.*`, `out/fast_throttle.*` |
| `catalogue.py` | Every facility found (class, status, number, verdict, source) -> `facilities.csv`, `out/triage.csv` |
| **`SOURCES.md`** | **The sources ledger: every number, its value, where it is used, the source with quote/table location, confidence (verified / search / literature / estimate), and what is open** |
| `refs/` | Local copies of the key papers (list in `SOURCES.md`) |

```bash
PY=~/PycharmProjects/nTof_x17/.venv/bin/python
$PY survey/survey_yield.py
$PY survey/survey_absorbed.py
bash ganil_nfs/sim/fetch_sel.sh            # NFS Geant4 tables from EOS (+ lnl L4_cosmic, see SURVEY.md §4.1)
$PY survey/survey_fast.py --check          # must reproduce the NFS reach: 3.3e-3 / 0.031 (big plastics)
$PY survey/survey_fast.py                  # ~25 min; caches the NFS inputs in survey/.cache
$PY survey/catalogue.py
```

The scripts run with numpy 1.26 (the Linux desktop's system numpy): each aliases `np.trapezoid` to
`np.trapz` when needed. `survey_fast.py` imports `ganil_nfs/sim/nfs_reach.py` and needs its tables
(`ganil_nfs/sim/sel*`, gitignored) and the LNL cosmic tables copied into `ganil_nfs/sim/sel/`.
