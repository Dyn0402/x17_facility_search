# Proposed dashboard changes for dd_gen (not applied; coordinator applies)

## survey/dashboard.py, EXTRA['dd_gen'] (replace the entry, keep `beam`/`scen`/`sites`)

```python
effort=3,
effort_note='Dedicated study (shared Geant4 soft-beam background re-weighted to thick-target D-D, plus ESTIMATE direct-arm and room terms): 3e11 n/s measured, 30 bar cell, 35 cm, shadow shield, 90°: 6.5e-4 in 50 d (9.5 d to ATOMKI); 50 cm 8.5e-4. Beam term only; the 2.45 MeV correlated term is unresolved by N5.',
g4=[('Study: Phoenix 3e11, 35 cm, shadow shield, 90° (estimate terms)', 'phoenix_3e11_35cm_shadow_full', ('dd_sources/out/dd_reach.csv', {})),
    ('Study: Phoenix 3e11, 50 cm (robust)', 'phoenix_3e11_50cm_shadow_full', ('dd_sources/out/dd_reach.csv', {}))],
links=[('slide note (not yet published)', 'dd_sources/out/dd-sources-x17-feasibility.html')],
next='Ask Phoenix/SHINE: is a 3e11 D-D system for sale or hostable today, current and target length, price with vault? Run a mono-energetic 2.45 MeV Geant4 with shield and room to fix the correlated term.',
contact='Phoenix LLC / SHINE (Madison, Janesville); ENEA FNG for the ×500-weaker D-D station.',
updated='2026-11-09',
```

The CSV has `key, hw, days, signal, rho3, rho3_floor`; `signal` is `E* ≤ 22 MeV`.

## survey/facilities.csv, row dd_gen

- verdict: MARGINAL (keep) until the machine question resolves. Status stays `commercial`.
- reason → `clean (2.45 MeV) and close-coupled: 6.5e-4 (9.5 d) with 3e11 n/s at 35 cm behind a shadow shield, 8.5e-4 at 50 cm; the "×10 short" assumed 2.5 m. Estimate terms pending a 2.45 MeV Geant4 run. No user programme: a dedicated machine must be bought or contracted`

## LOG line

`2026-11-09 D-D sources (dd_sources/): dedicated study. 3e11 n/s close-coupled reaches 6.5e-4 (9.5 d) with a shadow shield at 35 cm, ×10 better than the catalogue's 2.5 m; call KEEP AS BACKUP (no user programme; arm, room and correlated terms are estimates).`

## README table row

`| dd_sources/ | intense 2.45 MeV D-D sources | 3e11 n/s at 35 cm: 6.5e-4 in 50 d (9.5 d, estimate terms), KEEP AS BACKUP | dd_sources/README.md |`
