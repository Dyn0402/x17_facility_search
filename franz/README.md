# franz — FRANZ, the Frankfurt near-threshold ⁷Li(p,n) keV-neutron source

**Read this first (2026-10-21):** at its design intensity (20 mA DC at 2.0 MeV = 10¹² n/s, also the licence's
neutron limit) on a thin Li target, with the ³He cell 0.5 m from the target, the reach is **X17/IPC = 3.3×10⁻⁴
at 3σ in 50 days** (big plastics; as built 9.4×10⁻⁴): ×4.5 past ATOMKI ⁴He, ~2.4 days to the ATOMKI strength,
statistics-limited. That ties Birmingham. But FRANZ has **not yet run at 2 MeV** (RFQ at 0.7 MeV since 2023;
2 MeV planned for end 2025, no report found), and the licence allows < 5 % duty: at 10 mA × 5 % the reach is
2.2×10⁻³ (×1.5 short of ATOMKI), 1.0×10⁻³ if the energy can go to 2.2 MeV. The thin Li target (protons stop at
the (p,n) threshold) removes the 15–18 MeV ⁸Be γ, so no Pb filter is needed. Slides (built, not published):
`out/franz-x17-feasibility.html`.

| file | what |
|---|---|
| `FACILITY.md` | the facility record: accelerator, commissioning history, licence, beam numbers, what hosting MX17 needs, sources |
| `FEASIBILITY.md` | the answer, beam model, Geant4 singles, reach (duty × distance × E_p × target), the shield estimate |
| `franz_beam.py` | near-threshold ⁷Li(p,n) slowing-down MC (from `bham_beam.py`), target γ (thin/thick), and the reach with a duty factor and the 10¹² n/s cap → `out/franz_*` |
| `deck/build_deck.py`, `deck/cartoon.py` | the slide note (→ `out/franz-x17-feasibility.html`) and the facility cartoon |

The Geant4 runs (N5/G5/G6) and the reach engine are shared: [`survey/soft_sim/`](../survey/soft_sim/README.md).
`franz_beam.py` imports `soft_reach.py` and adds the duty factor itself (no change to the shared engine).

```bash
PY=~/PycharmProjects/nTof_x17/.venv/bin/python
bash survey/soft_sim/fetch_sel.sh          # Geant4 tables from EOS, once
$PY franz/franz_beam.py                    # ~1 min (first run builds survey/.cache, ~1 min)
$PY franz/deck/build_deck.py
python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py franz/out/franz-x17-feasibility.html \
    --slug franz-x17-feasibility --force --deploy
```
