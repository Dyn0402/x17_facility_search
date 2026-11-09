# Proposed dashboard changes for `bnct_accel` (2026-11-09; not applied)

## `survey/dashboard.py`, EXTRA entry (replaces the current `'bnct_accel'`)

```python
'bnct_accel': dict(beam=('flux', 1e9, 'epithermal'), geom='1e9 n/cm²/s epithermal (moderated)',
                   sites=[('Southern Tohoku', 37.3900, 140.3600), ('Helsinki', 60.1900, 24.9500),
                          ('Tsukuba', 36.0800, 140.1100), ('Xiamen', 24.4800, 118.0900),
                          ('BINP Novosibirsk', 54.8500, 83.1000), ('Nagoya', 35.1540, 136.9640), ('CNAO Pavia', 45.2000, 9.1400)],
                   effort=3,
                   effort_note='Dedicated study (bnct_accel/, 9 Nov) with the shared Geant4 soft-beam engine: real epithermal + contamination spectrum (ESTIMATE), sub-keV by analytic capture and a 1-3 keV background proxy; bare Li from the Birmingham/FRANZ models; machine status checked by web search.',
                   g4=[('Study: moderated Li port, 1e9, 40 cm, IAEA contamination', 'mod_li_iaea_iaea1e9_40cm_cell', ('bnct_accel/out/bnct_reach.csv', {})),
                       ('Study: bare Nagoya 15 mA, 2 m, 5 cm Pb (BSA off, hypothetical)', 'nagoya_28_15_2m_pb5', ('bnct_accel/out/bnct_reach.csv', {}))],
                   links=[('slide note (not yet published)', 'bnct_accel/out/bnct-accel-x17-feasibility.html')],
                   next='Ask Nagoya NUANS: operating? current? can the BSA be removed or by-passed? Only then a Geant4 run below 1 keV for the moderated case. Ask INFN about CNAO once Alphabeam is installed.',
                   contact='none yet', updated='2026-11-09'),
```

## `survey/facilities.csv` / `catalogue.py`, row `bnct_accel`

- **verdict:** MARGINAL (unchanged)
- **status:** `operating: clinical NeuCure (Southern Tohoku, Kansai), nuBeam Helsinki (first patients May 2025); research Li at Birmingham, BINP VITA, NUANS (ask); CNAO Alphabeam not yet confirmed installed`
- **reason:** `Dedicated study (bnct_accel/, 2026-11-09). Moderated Li port with the real contamination (ESTIMATE): 1.3e-3 in 50 d, big plastics (bracket 8.3e-4 to 1.8e-3; 39 d to ATOMKI), DREAM-limited (live 0.5); replaces the ILL-scaled 2.5e-3. Bare Li target 5.1e-4 (Nagoya class, 15 mA, 2 m, 5 cm Pb), but hospital machines have the target inside the BSA; the bare options are Birmingham and BINP VITA (no CERN relations since Nov 2024). Overall WATCH.`

## LOG line for `survey/dashboard.py`

```python
('2026-11-09', 'Accelerator BNCT, dedicated look (bnct_accel/): the moderated port with its real contamination reaches 1.3e-3 in 50 days (big plastics, bracket 8.3e-4 to 1.8e-3, DREAM-limited; estimate), replacing the ILL-scaled 2.5e-3. A bare Li target is ×2–4 better but no clinical machine offers one (target inside the moderator). Only Birmingham and BINP VITA have bare targets. WATCH: ask Nagoya.', 'bnct_accel'),
```

## README table row (top-level `README.md`)

```markdown
| [`bnct_accel/`](bnct_accel/README.md) | Accelerator BNCT machines (nuBeam, NeuCure, CICS, Nagoya, Alphabeam/CNAO, VITA) as X17 sources: 2026 status, bare-target and moderated-port reach (`bnct_accel_beam.py`), slides. Call: WATCH |
```

Reach CSV for the `g4` tuples: `bnct_accel/out/bnct_reach.csv`, with columns `key, hw, days, rho3, rho3_floor, signal` as `dashboard.g4_reach` reads (rows exist for `hw = 'big plastics'` and `days = 50` for both keys above).
