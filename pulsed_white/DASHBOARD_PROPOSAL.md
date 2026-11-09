# Proposed dashboard and catalogue changes (pulsed_white, 2026-11-09)

Nothing here has been applied. Reach CSV: `pulsed_white/out/pw_reach.csv` (columns key, hw, days, signal, rho3, rho3_floor, as `dashboard.g4_reach` reads). The contact field reflects Dylan's decision: no facility contact yet.

## survey/dashboard.py EXTRA

```python
'csns_backn': dict(  # keep the existing beam, geom, sites
    effort=3,
    effort_note='Dedicated study, no new Geant4 (pulsed_white/, 2026-11-09): measured Table 1 flux and per-decade spectrum, ToF 0.2–2.75 MeV, per-pulse DREAM and Micromegas occupancy, correlated events re-weighted from N4/N5. The wall is one DREAM readout per 25 Hz pulse (47 random two-arm triggers per pulse at ES#2), not occupancy (0.07 at ES#2). Today’s DAQ: 3.0e-3. Whole ToF window read as one event (mode not tested): ES#2 9.4e-4, 20 d to ATOMKI, if the γ flash dead time stays below ~3 µs.',
    g4=[('Study: ES#2, 185 kW, full-window readout (assumed mode)', 'backn_es2_185_fw', ('pulsed_white/out/pw_reach.csv', {})),
        ('Study: ES#1, 185 kW, full-window readout (assumed mode; occupancy 0.93)', 'backn_es1_185_fw', ('pulsed_white/out/pw_reach.csv', {})),
        ('Study: ES#2, 185 kW, today’s DAQ', 'backn_es2_185', ('pulsed_white/out/pw_reach.csv', {}))],
    links=[('study', 'pulsed_white/FEASIBILITY.md')],
    next='No facility contact for now. Bench-test a ~150-sample beam-synchronous DREAM readout; Geant4 the flash at ES#2 with Pb filters.',
    contact='none yet (Dylan, 2026-11-09)', updated='2026-11-09'),

'gelina': dict(  # keep sites; beam: replace the flux by 3.4e13 / (4 * math.pi * 1e6), still an upper bound
    geom='3.4e13 n/s isotropic, 10 m (upper bound; no measured MeV flux at a station retrieved)',
    effort=3,
    effort_note='Dedicated study, no new Geant4 (pulsed_white/, 2026-11-09): JRC source strength, Watt-shape stand-in, ToF 0.2–2.75 MeV, 800 Hz per-pulse model. 10 m, flux upper bound: 1.2e-3 with no flash loss, 3.0e-3 with the measured 0.87 µs chamber recovery. WNR under the same assumptions: 8.4e-4 and 1.8e-3.',
    g4=[('Study: 10 m, flux upper bound, 0.87 µs flash cut', 'gelina_10m', ('pulsed_white/out/pw_reach.csv', {})),
        ('Study: 10 m, flux upper bound, no flash loss', 'gelina_10m_nf', ('pulsed_white/out/pw_reach.csv', {})),
        ('Study: 30 m, flux upper bound', 'gelina_30m', ('pulsed_white/out/pw_reach.csv', {}))],
    links=[('study', 'pulsed_white/FEASIBILITY.md')],
    next='None: dominated by WNR. Reopen only with a measured direct flux at 10 m and a flash recovery below 0.3 µs.',
    contact='none yet (Dylan, 2026-11-09)', updated='2026-11-09'),

'csns2': dict(next='Not an existing beam; not counted for now. Full-window readout at 500 kW would give 6.2e-4 at ES#2 (pulsed_white/).', updated='2026-11-09'),
'nelbe': dict(next='Closed: 0.24 at best (pulsed_white/).', updated='2026-11-09'),
'rpi': dict(next='Closed: 2.1e-3 at a 1e13 n/s isotropic upper bound with no flash loss (pulsed_white/).', updated='2026-11-09'),
```

Merge these fields into the existing entries. `kurns_linac` and `jparc_annri` need no number: not computed, reasons below.

Effort is 3 for both: there is no dedicated Geant4 run.

## survey/facilities.csv (via survey/catalogue.py)

| key | verdict | status | reason |
|---|---|---|---|
| `csns_backn` | **POTENTIAL** (was DUTY) | operating, 185 kW | Dedicated ToF study (pulsed_white/, 2026-11-09): the wall is one DREAM readout per 25 Hz pulse, not Micromegas occupancy. 3.0e-3 with today's DAQ; 9.4e-4 at ES#2 (20 d) if the whole ToF window is read as one event, an untested mode, with the γ flash dead time below ~3 µs. Call: WATCH |
| `gelina` | DOMINATED (unchanged) | operating; EUFRAT calls, Euratom relevance required | With JRC's 3.4e13 n/s and a real spectrum: 1.2e-3 at the isotropic upper bound with no flash loss, 3.0e-3 with a 0.87 µs flash cut; WNR is 8.4e-4 and 1.8e-3 under the same assumptions. Still below WNR |
| `csns2` | DUTY (unchanged) | upgrade under way; SC linac installation 2027–28 | Not an existing beam, not counted for now. The power does not help with today's DAQ; with a full-window readout 6.2e-4 at ES#2 |
| `nelbe` | DOMINATED (unchanged) | operating | 0.24 in 50 d with a time-of-flight window (statistics) |
| `rpi` | DOMINATED (unchanged) | operating | ≥ 2.1e-3 at a 1e13 n/s isotropic upper bound, no flash loss |
| `kurns_linac` | DOMINATED (unchanged) | operating (lit.) | Not computed: source weaker than RPI's bound |
| `jparc_annri` | DUTY (unchanged) | operating | Not computed: moderated beam, little flux in 0.2–2.75 MeV, 25 Hz |

## LOG line

```python
('2026-11-09', 'Pulsed white sources re-examined with time of flight (pulsed_white/): Back-n was limited by one DREAM readout per pulse, not occupancy (3.0e-3 today; 9.4e-4 at ES#2, 20 d, with an untested full-window readout and a flash dead time below ~3 µs). GELINA stays below WNR (1.2e-3 upper bound, 3.0e-3 with a 0.87 µs flash cut). The same flash cut moves WNR from 8.4e-4 to 1.8e-3.', 'csns_backn,gelina,csns2,lansce_wnr'),
```

## README table row

| `pulsed_white/` | GELINA and CSNS Back-n with time of flight: Back-n wall is DREAM per pulse (9.4e-4 at ES#2 with a full-window readout, untested; WATCH); GELINA dominated by WNR (1.2e-3 upper bound, 3.0e-3 with a flash cut; CLOSED); the flash cut also moves WNR to 1.8e-3 |
