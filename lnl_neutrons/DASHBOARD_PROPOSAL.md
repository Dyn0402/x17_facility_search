# Proposed dashboard changes (lnl_neutrons, 2026-11-09)

Not applied: the coordinator edits `survey/dashboard.py` and `survey/facilities.csv`.

## `survey/facilities.csv`

- `lenos`: status `RFQ going to Caserta (ANTHEM); LENOS exists only on CN`, verdict **WATCH**, reason `CN beam line only; design 7.3e10 n/s forward 5.0e-4 if ever built; LNL RFQ goes to Caserta (HB2025).`
- `nephir` (rename **NEPIR**): status `phase 0 not built; SPES pit crack (Feb 2026)`, verdict **WATCH→CLOSED for X17**, reason `≤ 1 µA of 70 MeV, spectrum ≫ 2.75 MeV; a 35 MeV port would give 2.1e-3 (hypothetical).`
- `lnl_cn`: status `operating, ~0.5 µA on Li today (RP limit)`, verdict stays **TARGET** for the proton route, add reason `neutron route 1.1e-2 at 3 µA (×7 short of ATOMKI): lnl_neutrons/`.
- add `anthem_caserta` (new): `ANTHEM BNCT, Caserta, IT` / `RFQ 5 MeV 30 mA CW, Be, ~1e14 n/s` / fast ≤ 3.2 MeV / `under construction, building ~2027` / **WATCH** / `1.7e-4 engine if a user could get a 130° view at 2 m; no user programme; clinical` / HB2025.

## `survey/dashboard.py`, `EXTRA`

```python
'lenos': dict(beam=('bound', '≈', 'birmingham', 1.0), sites=[('LNL', 45.3530, 11.9480)], effort=3,
              effort_note='Dedicated study (lnl_neutrons/): no high-current LENOS will exist at Legnaro, its RFQ goes to Caserta (ANTHEM). Modelled at the 7.3e10 n/s forward design value: 5.0e-4 (cell 20 cm). CN today, the only LENOS version that exists, reaches 1.1e-2 at 3.3 µA.',
              g4=[('Study: LENOS design, 7.3e10 n/s forward, 20 cm (not built)', 'lenos_20cm', ('lnl_neutrons/out/lnl_neutrons_other_reach.csv', {})),
                  ('Study: CN today-authorised 3.3 µA, 3.0 MeV thin-stop Li, D = 20 cm', 'cn_3000_thin', ('lnl_neutrons/out/lnl_neutrons_reach.csv', {'scen': 'authorised', 'D_cm': 20, 'variant': 'base'}))],
              links=[('slide note', 'https://dylan-neff.web.cern.ch/notes/lnl-neutrons-x17-feasibility.html')],
              next='Ask Pierfrancesco: CN current on Li once shielded; whether ANTHEM (Caserta) second room can take an experiment.',
              contact='P. Mastinu (mastinu@lnl.infn.it)', updated='2026-11-09'),
'nephir': dict(beam=('bound', '≈', 'ganil_nfs', 1.0), sites=[('LNL', 45.3530, 11.9480)], effort=3,
               effort_note='NEPIR phase 0 is ≤ 1 µA at 70 MeV (white, ~3e6 n/cm²/s), far above the X17 window. The SPES cyclotron has a pit-floor crack (Feb 2026) with no timeline. A hypothetical 35 MeV, 750 µA port gives 2.1e-3 (correlated beam + DREAM).',
               g4=[('Study: hypothetical SPES 35 MeV, 750 µA on Be, 130°, 2 m', 'spes35_130_2m', ('lnl_neutrons/out/lnl_neutrons_other_reach.csv', {}))],
               links=[('slide note', 'https://dylan-neff.web.cern.ch/notes/lnl-neutrons-x17-feasibility.html')],
               next='Nothing for X17 until SPES protons return.', updated='2026-11-09'),
```

## `LOG` line

```python
('2026-11-09', 'Neutron route at Legnaro looked at properly (lnl_neutrons/): the machines on site cannot do it. CN at the authorised 3.3 µA, 3.0 MeV on thin-stop Li, cell 20 cm: 1.1e-2 in 50 d (×7 short of ATOMKI), cosmics-limited; 4.4e-3 with a 90 % veto; close-coupling loses to the production target\'s own IPC pairs (the Demokritos verdict holds). LENOS\'s RFQ is being shipped to Caserta (ANTHEM), MUNES was never funded, NEPIR-0 is ≤ 1 µA at 70 MeV, SPES has a pit crack. New lead off site: ANTHEM Be source at Caserta gives 1.7e-4 (0.6 d) on paper, no user programme.', 'lenos,nephir,lnl_cn'),
```

## README table row (`survey/README.md` or top-level)

`| [lnl_neutrons/](lnl_neutrons/README.md) | Neutron route at Legnaro: CN cannot reach ATOMKI (1.1e-2 at 3.3 µA); LENOS RFQ goes to Caserta; ANTHEM 1.7e-4 on paper, no user programme. WATCH. |`
