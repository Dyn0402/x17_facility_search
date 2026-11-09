# lnl_neutrons — a neutron-route ³He(n,e⁺e⁻) X17 run at Legnaro

**Update 2026-11-09 (Dylan: only existing beams, no money for new machines, no outreach for now):** ANTHEM is not an existing beam. The 1.7×10⁻⁴ assumes a bare 30 mA view; the papers show a research room but one target, and clinical current maybe 2–5× lower. Defensible range 6.6×10⁻⁴ to 1.3×10⁻³ (estimate). See `FACILITY.md` addendum.

**Read this first (2026-11-09):** the machines on site cannot do it. CN at the authorised ~3.3 µA, 3.0 MeV, thin-stop Li, 30 bar cell at 20 cm reaches
**1.1×10⁻²** at 3σ in 50 d (big plastics), ×7 short of ATOMKI (~2 600 d), cosmics-limited; with a 90 % veto 4.4×10⁻³ (×2.9 short). Close-coupling loses to the production target's own IPC pairs: the Demokritos verdict holds.
LENOS's RFQ is being shipped to **Caserta** for ANTHEM (clinical BNCT), MUNES was never funded, NEPIR-0 is ≤ 1 µA at 70 MeV, SPES has a pit crack with no date. The real lead: **ANTHEM at 30 mA gives 1.7×10⁻⁴ (0.6 d to ATOMKI)**, Birmingham class on paper, but it is not at LNL and has no user programme. **Overall: WATCH.** Slides (built, not published): `out/lnl-neutrons-x17-feasibility.html`.

| file | what |
|---|---|
| `FACILITY.md` | every LNL neutron source: 2026 status, sources, questions for Pierfrancesco |
| `FEASIBILITY.md` | the answer, the CN model and geometry, target pairs, scans, walls, the scorecard |
| `lnl_neutrons_beam.py` | CN/Li, LENOS, ANTHEM, SPES sources with the shared engine → `out/lnl_neutrons_*` |
| `deck/build_deck.py` | slide note → `out/lnl-neutrons-x17-feasibility.html` |
| `DASHBOARD_PROPOSAL.md` | proposed text for `survey/dashboard.py` and `survey/facilities.csv` |

```bash
PY=~/PycharmProjects/nTof_x17/.venv/bin/python
$PY lnl_neutrons/lnl_neutrons_beam.py                  # ~9 min
$PY lnl_neutrons/deck/build_deck.py
```

The Geant4 tables (N5/G5/G6, N4) and engine are shared: [`survey/soft_sim/`](../survey/soft_sim/README.md); nothing there is modified.
