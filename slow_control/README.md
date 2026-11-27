# slow_control/: environment and gas sensors for the next run

Facility-independent (LNL is the case). Started 2026-11-17 from the n_TOF drift-velocity study.

**Read this first**
1. `ENVIRONMENT_SENSORS.md`: what n_TOF taught us, and which measurements to log, ranked. v moved 15 % with outdoor
   water vapour and hall temperature, and no gas property was measured.
2. `SENSOR_OPTIONS.md` (2026-11-17): what to buy, what it costs and how to read it out. §0 has the bottom line; §6 has
   the tiers.
   - **Tier 1 (~€1.9k).** A Pi logger on the DAQ clock, hall T/RH/p, an SHT85 + BMP585 stainless cell at the inlet and
     after each chamber, Pt100s and bottle gauges.
   - **Gas fixes (~€1.0k).** Aluminium-barrier Synflex-type / copper lines (€0.4k, budget item `gaslines`, §8), parallel feeds and a 3A dryer.
   - **Tier 2 (~€6.3k).** A galvanic trace-O₂ cell, a water anchor (FA510, or borrow CERN EP-DT's DRD1 gas monitor),
     inlet and exhaust flow meters, and a ⁵⁵Fe gain monitor.
   - **Recommended: ≈ €9.2k (6–13k).**
   - **Overkill:** RGA, GC and chilled mirrors.
   - **Zirconia O₂ sensors cannot be used with isobutane.**
3. `SENSOR_OPTIONS.md` §7 (17 Nov, evening): n_TOF tubing (5–10 m + 0.5 m jumpers) explains ≲ 300 ppm, so the chambers are the likely water source; the FEUs *do* have temperature sensors (MAX16031, `MaxRead`); the n_TOF flow CSVs probably exist on the DAQ PC; gas still open (CO₂ needs a CO₂-tolerant O₂ cell).
4. §7.5: A, C and D compared. Tubing alone gives C/A ≤ 1.2 and D/A ≤ 1.3, against 3.0 and 2.9 observed, so the water entered in the chambers. §7.2 also covers polling the FEUs' `MaxRead` between sub-runs.
5. `GAS_PANEL.md` (2026-11-26): the gas panel for a premixed non-flammable gas (probably the NSW Ar/CO₂/iC₄H₁₀ 93/5/2),
   with no mixer. An inlet MFC sized for running plus a flush bypass, 4 needle valves, a bubbler for the overpressure
   (absolute p measured, not controlled), filters and valves on each detector, and one exhaust sensor per chamber
   (water, p, T, flow). The exhaust sensor's own hardware design is kept in a private repository.
6. `research/A–D`: the sourced research behind it, with a link for every price.

| file | what |
|---|---|
| `water_units.py` | ppmv ↔ RH ↔ dew point table (`out/water_units.csv`) |
| `estimates.py` | water ingress through tube and windows, isobutane condensation in bottles (estimates) |

The budget items are `slowctl` and `gaslines` in `budget/items.py` (group Micromegas, P2).
