# Dashboard proposal: reactor fast / epithermal beams (2026-11-09)

Numbers: `reactor_fast/out/rf_reach.csv` (columns key, variant, hw, days, signal, rho3, rho3_floor; `g4_reach` reads it with sel `{'variant': 'subkev'}`).

## survey/dashboard.py, EXTRA

```python
'bnct_reactor': dict(effort=3,
    effort_note='Shared-engine study (N5/G5/G6 re-weighted, sub-keV treated explicitly): LVR-15 1.05e-3 (35 cm from exit), THOR 0.9e-3, RA-6 design 8e-4, MITR 1.2e-3 historical; ×10 on the sub-keV background gives ~3e-3. Replaces the ILL-scaled 2.5e-3.',
    g4=[('Study: LVR-15 BNCT beam, 35 cm from exit (subkev)', 'lvr15', ('reactor_fast/out/rf_reach.csv', {'variant': 'subkev'})),
        ('Study: THOR 1 MW, design values (subkev)', 'thor_1mw', ('reactor_fast/out/rf_reach.csv', {'variant': 'subkev'}))],
    links=[('reactor_fast study', 'reactor_fast/FEASIBILITY.md')],
    next='Ask CVŘ for BNCT line and room availability, beam time for weeks, flux with filter blocks removed.',
    contact='CVŘ reactor division; public names on BNCT papers: L. Viererbl, M. Marek',
    updated='2026-11-09'),
'tapiro': dict(beam=('flux', 1.64e8, 'fission'), geom='ESTIMATE: 1.6e8 n/cm²/s at a cell 2.7 m from the core through an open channel (concept)',
    est='S = 3e14 n/s (Rosa 2009, calculated), view factor 0.5 (ESTIMATE), no such channel exists', sites=[('ENEA Casaccia', 42.0449, 12.3024)],
    effort=3,
    effort_note='Shared-engine study: open core-view channel with 5 cm Pb (as the published BNCT column already has in the Cu window) 4.8e-4 (5.1 d, ×3.1 past ATOMKI), robust to γ/n ≤ 3; as built 1.4e-3. Concept, not a beam: needs a reactor modification.',
    g4=[('Study: open channel + 5 cm Pb (concept)', 'tapiro_open_pb5', ('reactor_fast/out/rf_reach.csv', {'variant': 'subkev'}))],
    links=[('reactor_fast study', 'reactor_fast/FEASIBILITY.md')],
    next='Ask ENEA: column installed? channel sizes; sustained run at 5 kW; measured γ; openness to modification.',
    contact='alfonso.santagata@enea.it (ENEA brochure)',
    updated='2026-11-09'),
```
Coordinates approximate: check before publishing (ask).

## survey/facilities.csv

```
bnct_reactor,"Reactor BNCT epithermal beams (LVR-15, THOR, RA-6, MITR FCB)","CZ, TW, AR, US",reactor,"epithermal 0.4 eV-10 keV, Ø12-20 cm",epithermal,"LVR-15, THOR operating; MITR FCB being converted; KUR ended Apr 2026; RA-6 licence to Jul 2026 (ask)",7e8-8e9 n/cm²/s epithermal at exit,abs:bnct1,MARGINAL,"Engine with real fast/γ: 1.05e-3 LVR-15 (35 cm from exit), 0.9e-3 THOR, 8e-4 RA-6 design; ×10 sub-keV background gives ~3e-3. Replaces ILL-scaled 2.5e-3 (reactor_fast/, 2026-11-09)",reactor_fast/FACILITY.md
tapiro,ENEA TAPIRO fast source reactor,"Casaccia, IT",reactor 5 kW fast (HEU + Cu reflector),"fast leakage, ⟨E⟩ ~0.2-0.8 MeV",fast CW,operating (brochure 06/2026; run log (ask)); no beam exists,3e14 n/s core source; open channel ~1.6e8 n/cm²/s (ESTIMATE),,POTENTIAL,"Concept only: straight channel + 5 cm Pb reaches 4.8e-4 (×3.1 past ATOMKI) if ENEA can open it; needs a reactor modification. As built 1.4e-3 (reactor_fast/, 2026-11-09)",reactor_fast/FACILITY.md
```

## LOG

```python
('2026-11-09', 'Reactor fast/epithermal beam class studied (reactor_fast/): LVR-15, THOR, RA-6 ~1e-3 with engine; TAPIRO (new) open channel + Pb 4.8e-4 as a concept; KUR ended Apr 2026.'),
```

## Top-level README row

| `reactor_fast/` | Operating reactor beams, epithermal ~1e-3 with the engine; TAPIRO open channel concept 4.8e-4; call KEEP AS BACKUP, PURSUE TAPIRO enquiry |
