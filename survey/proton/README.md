# survey/proton — every proton machine, triaged for the MX17 X17 search

Started 2026-10-22. The proton counterpart of `survey/` (neutrons). **Read first: `PROTON_SURVEY.md` §0.**

## Read this first (2026-10-22)

- **The target, not the beam, sets the reach.** Days to 3σ at the ATOMKI strength fall as 1/current until the
  target saturates: ~4 µA thin (LNL CN is there), ~20 µA with a cooled thick backing downstream (ESTIMATE). Above
  that every machine gives ⁸Be in ~1.3 h (big plastics) / ~0.9 d (as built). The best machine beats LNL CN by ≤ ×5.
- **What separates machines is the claims they reach:** ⁸Be (1.03–1.10 MeV), ⁴He (0.9 MeV on Ti-T: needs tritium),
  ¹²C (~1.9 MeV on ¹¹B: an ESTIMATE, possibly the fastest).
- **POTENTIAL (7):** LNGS Bellotti IBF (LUNA-MV, 1 mA, no cosmics), JRC MONNET (100 µA, Ti-T routine, open calls),
  Felsenkeller, PTB PIAF, TUNL LENA, Notre Dame 5U, iThemba. **X17 LAB (6):** ATOMKI, MEG II, Hanoi, Montréal,
  Prague, Melbourne. WATCH: NPL's new ≥ 300 µA Tandetron.
- Census: ~180 of 267 electrostatic machines in the IAEA list could test ⁸Be at LNL-like currents.

| file | what it is |
|---|---|
| `PROTON_SURVEY.md` | The write-up: method, anchors, caps, classes, verdicts, census, X17 labs, next steps |
| `proton_reach.py` | The model: three claims, Geant4 anchors, ¹²C scaling, DREAM live time, target caps → `out/current_scan.*` |
| `proton_catalogue.py` | 60 named machines + verdicts; the IAEA census → `facilities.csv`, `out/triage.csv`, `out/census.csv`, `out/ranking.*` |
| `iaea_electrostatic.csv` | The IAEA Accelerator Knowledge Portal electrostatic list (267 rows, 2026-10-22) |
| `SOURCES.md` | Every number and its source, with confidence |
| `RESEARCH_NOTES.md` | Raw search notes |

```bash
PY=~/PycharmProjects/nTof_x17/.venv/bin/python
$PY survey/proton/proton_reach.py
$PY survey/proton/proton_catalogue.py
$PY survey/dashboard.py        # writes the site's data/facilities-proton.json too; then build + deploy the site
```
