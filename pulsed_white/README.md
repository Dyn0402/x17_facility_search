# pulsed_white: GELINA, CSNS Back-n and the rest of the pulsed white class

**Read this first (2026-11-09):** the class was closed on duty factor, and that was only half right. **CSNS Back-n** was stopped by one DREAM readout per 25 Hz pulse, not by Micromegas occupancy: 3.0×10⁻³ with today's DAQ, but **9.4×10⁻⁴ in 50 d (ES#2, 185 kW, big plastics, 20 d to ATOMKI; as built 2.5×10⁻³)** if the whole time-of-flight window is read as one event, a mode not yet tested, and only if the γ flash dead time stays below about 3 µs. **Call: WATCH.** **GELINA** stays below WNR: 1.2×10⁻³ at the isotropic upper bound with no flash loss, 3.0×10⁻³ with the measured 0.87 µs chamber recovery. **Call: CLOSED (dominated).** The same flash cut moves WNR's published 8.4×10⁻⁴ to 1.8×10⁻³. Beam-only re-weighting of N4/N5; engine checked against WNR and Birmingham rows. Slides built, not published: `out/pulsed-white-x17-feasibility.html`.

| file | what |
|---|---|
| `FACILITY.md` | the facility records, with sources; access (EUFRAT, CSNS), unknowns marked **(ask)** |
| `FEASIBILITY.md` | answer, validation, per-pulse walls, configurations, flash scan, scorecard, caveats, next steps |
| `pw_beam.py` | beams and periods, single-pulse DREAM model, flash cut, on `lansce_wnr/wnr_beam.py` → `out/pw_*` |
| `deck/build_deck.py` | the slide note |
| `DASHBOARD_PROPOSAL.md` | proposed dashboard and catalogue text |
| `out/pw_reach.csv` | all configurations (`_nf`: no flash loss; `_fw`: full-window readout) |
| `out/pw_flash_scan.csv`, `out/pw_pulse_table.csv` | reach vs flash dead time; the per-pulse table |

```bash
PY=~/PycharmProjects/nTof_x17/.venv/bin/python
$PY pulsed_white/pw_beam.py --check         # WNR 90L 10 m 8.42e-4, Birmingham bham_28_2m_pb5 3.32e-4
$PY pulsed_white/pw_beam.py --procs 8       # ~10 min, then the figures
$PY pulsed_white/deck/build_deck.py
```

Needs `survey/.cache/nfs_*.pkl` and the N5 tables in `survey/soft_sim/sel/` (see `lansce_wnr/README.md`).
