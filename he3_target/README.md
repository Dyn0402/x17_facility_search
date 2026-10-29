# he3_target — can the ³He target be built, filled, approved and emptied?

**Read this first (2026-10-29): `FEASIBILITY_PLAN.md`.** The engineering side of the ³He target for a fast-neutron
beam, worked for Birmingham HF-ADNeF (`../birmingham/TARGET_GEANT.md`).
- **Not a physics blocker:** about a year of procurement and engineering with known technology.
- **Days ≈ 33 · σ68 / (L of ³He in the beam).** Walls only move σ68 between 11° and 16°.
- **Build C (6.7 d) is under-sized** for a pressure code. Sized properly it costs ~8 % in days.
- **Baseline:** 30 bar, R 4 cm, Al-lined CFRP with domes. 62 L of ³He, ~7 d (est), PED Cat I.
- **Fallback:** 10 bar, 21 L, ~21 d. **To simulate:** a 200 bar R 2 cm tube with a Ø4 cm beam.
- **Gas in and out:** a closed cryopump loop with a dump tank, losing ≲ 0.2 % per campaign.
- **The ³He is not consumed,** so it can be borrowed. It is a controlled dual-use item (1C232).
- **The gas picks up ~1 MBq of tritium:** below the UK exemption values.

| file | what |
|---|---|
| `FEASIBILITY_PLAN.md` | the plan: requirements, design space, vessel and legal path, gas panel, ³He supply, tritium, safety, what to simulate, asks, phases, budget, risks |
| `he3_target.py` | the engineering model → `out/designs.csv`, `out/calibration.csv`, `out/he3_designs.png` |

```bash
PY=~/PycharmProjects/nTof_x17/.venv/bin/python
$PY he3_target/he3_target.py
```
