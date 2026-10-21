# bepn_cyclotron — cyclotron-driven thick-Be ⁹Be(p,n) sources (NPI Řež TR-24, BNCT HM-30s)

**Read this first (2026-10-21):** with the cell 2 m downstream of NPI Řež's TR-24 Be converter at 0°,
18 MeV protons throttled to ~0.19 mA and a Ø8 cm collimator, the reach is **X17/IPC = 8.7×10⁻⁴ at 3σ in
50 days** (big plastics; as built 1.3×10⁻³): ×1.7 past ATOMKI ⁴He, **~17 days** to the ATOMKI strength.
It passes, but it is ×2.6 behind Birmingham (3.3×10⁻⁴) and ×2 behind FRM II MEDAPP: 57 % of a Be(p,n)
spectrum is above the ATOMKI window at every angle and proton energy, and those neutrons fire the trigger
plastics, so DREAM's dead time sets the usable rate (live 0.45). A 30 MeV / 1 mA BNCT cyclotron does
worse (1.5×10⁻³ at 130°): its extra current goes into the hard tail. The beam model is ENDF/B-VIII.0
(LA150) p + ⁹Be, checked to 1 % against two published thick-target yields; the Geant4 background is the
soft-beam runs re-weighted (no new run). Open: whether NPI's high-power converter runs in 2026, and a
port through the TR-24 vault wall (U-120M has a collimated beam today, at 35 µA: 2.8×10⁻³). Slides:
`out/bepn-cyclotron-x17-feasibility.html` (built, not published).

| file | what |
|---|---|
| `FACILITY.md` | the candidates (NPI TR-24 / U-120M, KURNS and the clinical HM-30s, Atomki, TENMAK), NPI's machines and converter, beam numbers, what hosting MX17 needs, contacts, sources |
| `FEASIBILITY.md` | the answer, beam model, Geant4 re-weighting, reach (energy × angle × distance), levers, the shield estimate |
| `bepn_beam.py` | thick-Be spectra vs angle from the ENDF/B-VIII.0 GNDS file (σ, Legendre, Kalbach-Mann, photons) + Bethe slowing-down; anchors; `beam()`, `shield()` → `out/bepn_*` |
| `bepn_reach.py` | the `survey/soft_sim/soft_reach.py` engine with the E grid to 30 MeV and NFS N4 above 20 MeV → `out/bepn_reach.csv`, `bepn_components.csv`, `bepn_throttle.csv`, `bepn_reach_fig.*`; `--tau-scale 0.25 --tag tau4` → `out_tau4/` |
| `deck/build_deck.py`, `deck/cartoon.py` | the slide note (→ `out/bepn-cyclotron-x17-feasibility.html`) and the TR-24 cartoon |
| `refs/` | `p-004_Be_009.endf.gnds.xml` (ENDF/B-VIII.0 p + ⁹Be, from Geant4's LEND data on CVMFS), Fenyvesi arXiv:1504.07399 |

```bash
PY=~/PycharmProjects/nTof_x17/.venv/bin/python
bash survey/soft_sim/fetch_sel.sh                       # N5/G5/G6 tables (EOS); N4 is in ganil_nfs/sim/sel_beam/
$PY bepn_cyclotron/bepn_beam.py                         # ~20 s
$PY bepn_cyclotron/bepn_reach.py                        # ~1 min, both hardware sets
$PY bepn_cyclotron/bepn_reach.py --hw 'big plastics' --days 50 --tau-scale 0.25 --tag tau4 \
    --only npi18_0_2m npi18_130_2m npi24_130_2m npi24_130_1m kur30_130_2m kur30_90_2m
$PY bepn_cyclotron/bepn_beam.py                         # again, for out/bepn_shield.csv
$PY bepn_cyclotron/deck/build_deck.py
python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py bepn_cyclotron/out/bepn-cyclotron-x17-feasibility.html \
    --slug bepn-cyclotron-x17-feasibility --force --deploy
```
