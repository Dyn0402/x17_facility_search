# mechanics/: running MX17 with a horizontal beam

Facility-independent. n_TOF EAR2 has a vertical beam, and every other site has a horizontal one. The whole
apparatus therefore turns 90°, and gravity acts across detector faces that stood vertical at n_TOF.

## Read this first (2026-11-18)

- **Brainstorm started:** `BRAINSTORM.md`.
- **Roll angle.** The physics acceptance does not depend on the roll about the beam. The choice is
  **plus** (one arm on top, one on the bottom) or **X** (rolled 45°). Leaning X: it keeps the LS bubble in the
  neck, the SiPM bars sag ×0.7 less, and all four arms are alike. Pending a cosmic simulation with a rolled
  zenith.
- **Most sensitive items** (ESTIMATES):
  - LS vessels lying flat: the expansion bubble spreads over the slab.
  - SiPM bars held only at their ends sag 0.9–4.4 mm lying flat.
  - The MM drift cathode: 0.15–3 mm sag depending on its unknown foil tension, i.e. 0.5–10 % of the 30 mm
    gap, with opposite sign on the top and bottom arms.
- **Mass** is ~16 kg per arm known (FEUs and enclosures **(ask)**). Big plastics add 29 kg each. The issue
  is the overhead mass, not the total.
- **Next:**
  1. a flat-module bench test (MM up/down, LS flat);
  2. the cosmic sim at 45° roll;
  3. the (ask) list for the n_TOF builders and the facilities (`BRAINSTORM.md` §5).

## Files

| file | what |
|---|---|
| `BRAINSTORM.md` | the problem, plus vs X, frame concept, subsystem issues, safety, what settles each point |
| `mech_estimates.py` | cathode sag vs tension, readout-board deflection, SiPM bar sag, per-arm masses, envelope → `out/*.csv` |

```bash
~/PycharmProjects/nTof_x17/.venv/bin/python mechanics/mech_estimates.py
```
