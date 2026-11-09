# saraf — SARAF (Soreq, Yavne): the LiLiT liquid-lithium keV source and the Phase II linac

**Read this first (2026-11-09):** the catalogue's LiLiT row (near-threshold, 6.7×10⁻³) was the wrong operating point. LiLiT is a thick stopping jet; at the demonstrated ≤ 4 kW linac
power, raising the proton energy from 1.925 to 2.6–4 MeV raises the yield ×40–100, with every neutron still in the ATOMKI window. **Thick Li at 4 MeV, 1 mA, cell 1 m downstream: X17/IPC = 3.5×10⁻⁴ at 3σ in 50 days (big plastics;
as built 9.8×10⁻⁴), 2.6 days to the ATOMKI strength, statistics-limited**, equal to Birmingham's engine value (Birmingham's full-room Geant4: 5.5×10⁻⁴). LiLiT as it actually ran: 3.8×10⁻³ (×2.5 short). Phase II d(40) at 5 mA: 0.11 in the ATOMKI window (confirms "≈ NFS"; 0.05 % of the current is usable). **Overall call: WATCH.** The beam does not exist today:
Phase I was converted to Phase II and the first cryomodule was still "commissioning ongoing" in October 2025; no user programme; a nuclear-research site in an active conflict zone. Slides (built, not published): `out/saraf-x17-feasibility.html`.

| file | what |
|---|---|
| `FACILITY.md` | the machine (Phase I, LiLiT, Phase II), status with sources, access facts, contacts |
| `FEASIBILITY.md` | the answer, beam model, all options, shield, scorecard, what would have to be true |
| `saraf_beam.py` | thick-Li (LiLiT), p+Be, d+Be sources normalised to published LiLiT numbers; reach through the shared engine → `out/saraf_*`; `--check` reproduces the Birmingham and FRANZ rows; `--post` shield + summary figure |
| `deck/build_deck.py` | the slide note (→ `out/saraf-x17-feasibility.html`) |
| `DASHBOARD_PROPOSAL.md` | exact proposed dashboard text (not applied) |

The Geant4 runs (N5/G5/G6, N4) and the reach engine are shared: [`survey/soft_sim/`](../survey/soft_sim/README.md). `saraf_beam.py` imports `soft_reach.py` and `bepn_reach.py` (no change to them).

```bash
PY=~/PycharmProjects/nTof_x17/.venv/bin/python
bash survey/soft_sim/fetch_sel.sh          # Geant4 tables from EOS, once
$PY saraf/saraf_beam.py --check            # engine check (Birmingham, FRANZ reproduced)
$PY saraf/saraf_beam.py                    # ~10 min, both hardware sets
$PY saraf/saraf_beam.py --post             # shield estimate, summary figure
$PY saraf/deck/build_deck.py
```
