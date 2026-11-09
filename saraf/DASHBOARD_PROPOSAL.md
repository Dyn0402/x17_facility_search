# Proposed dashboard text for SARAF (for the coordinator; not applied)

## survey/dashboard.py EXTRA['saraf']

```python
'saraf': dict(beam=('flux', 1.9e9 / 2500 / 1.0, 'nfs'), geom='thick Li, 4 MeV p, 1 mA, 1 m, 1.9e9 n/s through Ø8 cm', est='LiLiT scale measured at 1.925 MeV; 4 MeV yield from slowing-down MC (σ flat above 3 MeV, ESTIMATE)',
              scen=[('Phase II 5 mA on the same jet', ('flux', 5 * 1.9e9 / 2500 / 1.0, 'nfs'))],
              sites=[('SARAF', 31.9050, 34.6990)],
              effort=3,
              effort_note='Dedicated study with the shared Geant4 soft-beam engine, no Geant4 of its own: thick Li at 4 MeV, 1 mA, 1 m: 3.5e-4 in 50 d (as built 9.8e-4), ties Birmingham\'s engine value. Near threshold (LiLiT as ran): 3.8e-3. No beam today: Phase I linac converted, Phase II in commissioning.',
              g4=[('Study: thick Li, E_p 4 MeV, 1 mA (≤ 4 kW), cell 1 m', 'lilit_4000_pb0', ('saraf/out/saraf_reach.csv', {'scen': 'phaseI', 'dist_m': 1.0})),
                  ('Study: LiLiT as ran, 1.925 MeV, 1.5 mA, 0.5 m', 'lilit_1925_pb0', ('saraf/out/saraf_reach.csv', {'scen': 'as_ran', 'dist_m': 0.5})),
                  ('Study: Phase II, 5 mA on Li jet, 4 MeV, 1 m (not demonstrated)', 'lilit_4000_pb0', ('saraf/out/saraf_reach.csv', {'scen': 'phaseII', 'dist_m': 1.0}))],
              links=[('slide note', 'https://dylan-neff.web.cern.ch/notes/saraf-x17-feasibility.html')],
              next='Ask SNRC (Weissman, Mardor; M. Paul at HUJI): has CM1 delivered beam; can it give ≥ 1 mA at 2–5 MeV protons; will LiLiT be re-installed and where; is a ≥ 1 m free 0° path available; is external access possible at all. Then a Birmingham-style room Geant4 with a thick-Li 4 MeV source.',
              contact='none contacted', updated='2026-11-09'),
```

(The `beam` tuple is the catalogue's flux-per-cm² placeholder; the dashboard headline should come from the `g4` rows. Adjust the `est` type to whatever the page uses.)

## survey/facilities.csv (saraf row)

- verdict: **WATCH** (unchanged)
- status: `Phase II commissioning (Oct 2025): first cryomodule installed, no beam report found; Phase I linac converted (no ≥ 1.9 MeV p beam today)`
- number: `LiLiT 3-5e10 n/s measured (1.92 MeV, 1-2 mA); 1 mA at 4 MeV ~3e12 n/s (model); Phase II 1e15 n/s (design)`
- reason: `Dedicated study 2026-11-09: engine re-weight. LiLiT as ran 3.8e-3 (×2.5 short); thick Li at 4 MeV, 1 mA, 1 m: 3.5e-4 in 50 d (ties Birmingham engine value, 2.6 d to ATOMKI); Phase II d(40): 0.11 (E*≤22), confirms ≈ NFS. No beam today, no user programme, active conflict zone`
- source: append `; saraf/FEASIBILITY.md; LINAC 2024 THAA007; arXiv:1511.04701`

## LOG line

`2026-11-09 SARAF: dedicated study (saraf/) with the shared Geant4 engine: the catalogue's near-threshold LiLiT row was the wrong operating point; thick Li at 4 MeV, 1 mA, 1 m: 3.5e-4 (ties Birmingham engine value); Phase II d(40) confirms ≈ NFS. WATCH: no ≥ 1.9 MeV proton beam today (Phase II commissioning, Oct 2025).`

## README table row

`| **SARAF, Soreq** | CW SC linac p/d: LiLiT thick Li jet (Phase I, converted), Phase II p 1.3–35 / d 2.6–40 MeV, 5 mA (commissioning) | **Dedicated study 2026-11-09** (shared Geant4 soft-beam engine, no own Geant4): the lever is the proton energy, not 40 MeV: thick Li at 4 MeV, 1 mA, 1 m: **3.5×10⁻⁴ in 50 d** (2.6 d to ATOMKI, ties Birmingham's engine value; as built 9.8×10⁻⁴); LiLiT as ran 3.8×10⁻³; Phase II d(40) ≈ NFS. WATCH: no such beam today. [`saraf/`](saraf/README.md) |`
