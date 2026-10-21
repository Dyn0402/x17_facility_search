# lansce_wnr — the LANSCE WNR Target 4 white spallation source (Los Alamos)

**Read this first (2026-10-21):** on the softest flight path, 4FP90L, with the cell 10 m from the bare W
target, 1.8 µs micropulses and a time-of-flight window of 0.2–2.75 MeV, the reach is **X17/IPC = 8.4×10⁻⁴ at
3σ in 50 days** (big plastics; as built 2.4×10⁻³ at 10 m, 1.6×10⁻³ at 7 m): ×1.8 past ATOMKI ⁴He, ~16 days of
beam to the ATOMKI strength. Statistics-limited: the background is the IPC; the 2.5 % macropulse duty and the
ToF window keep accidentals and the fast neutrons out. Operating today; 90L beam time is scarce. No new
Geant4: re-weighted from the NFS (N4) and soft-beam (N5) runs. Slides built, not published:
`out/lansce-wnr-x17-feasibility.html`.

| file | what |
|---|---|
| `FACILITY.md` | the facility record: Target 4, time structure, flight paths, access, contacts, sources |
| `FEASIBILITY.md` | the answer, beam model, response, reach vs path/distance/spacing, robustness, open questions |
| `wnr_beam.py` | yield per angle (Nowicki 2017 Fig. 2), time folding, ToF reach engine → `out/wnr_*` |
| `deck/build_deck.py`, `deck/cartoon.py` | the slide note and the Target 4 / timing cartoons |
| `refs/` | Nowicki, Wender & Mocko, Physics Procedia 90 (2017) 374, and its Figs. 2 and 3 |

```bash
PY=~/PycharmProjects/nTof_x17/.venv/bin/python
$PY lansce_wnr/wnr_beam.py --check        # the engine on NFS's beam: 3.3e-3 / 0.030 (big plastics, 14 d)
$PY lansce_wnr/wnr_beam.py                # ~25 min with the distance scan (--no-scan: ~12 min)
$PY lansce_wnr/deck/build_deck.py
python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py lansce_wnr/out/lansce-wnr-x17-feasibility.html \
    --slug lansce-wnr-x17-feasibility --force --deploy
```

Needs `survey/.cache/nfs_*.pkl` (or the NFS tables: `ganil_nfs/sim/fetch_sel.sh`) and the N5 tables in
`survey/soft_sim/sel/` (`survey/soft_sim/fetch_sel.sh`).
