# Environment and gas sensors for the next run: what n_TOF taught us (2026-11-17)

Facility-independent. Written from the n_TOF pass-1 drift-velocity study (nTof_x17
`rerun/ntof/vt/README.md`; slide note https://dylan-neff.web.cern.ch/notes/ntof-drift-velocity.html).
It lists which slow-control measurements a future run should log, ranked by how much each one would have helped at
n_TOF. Prices are not quoted here; items to buy go into `budget/items.py`.

## What happened at n_TOF

- **The drift velocity was not constant.** It was measured per acquisition from the duration of the charge column, and it
  moved far beyond its errors. Chamber C went from 27.7 to 32.0 µm/ns, A by about a third of that. The chamber HV
  never changed.
- **The chambers moved together.** They share one gas line (A → B → C → D), and the downstream chambers moved most:
  C 3.0× and D 2.9× as much as A.
- **The best predictor was the outdoor water vapour**, from the MeteoSwiss station at Genève-Cointrin, 5 km away,
  smoothed over ~24 h: r = −0.84 with C.
  - Adding the daily swing of the hall temperature explains 78 % of C's variation. We read that swing off the ³He
    target capsule's pressure gauge, a sealed volume that happened to work as a thermometer.
  - The sensitivities are −1.9 %/hPa of water vapour and −2.2 %/K on C.
- **Gas density was not the cause.** Barometric pressure and air temperature alone were weak predictors, with the wrong
  sign for a density effect.
- **The reading is water entering the gas,** more of it downstream and on warm, humid days, through permeable tubing or
  outgassing walls. It is a hypothesis: **no gas property was measured during the run**, so it cannot be confirmed.
- **Earlier n_TOF analyses hit the same blind spot.**
  - A July run read v ~12 % low, attributed to ~0.2 % water.
  - The beam-gas attachment study had to infer the beam gas composition (~1.5 % H₂O, ~160 ppm O₂) from the signals
    themselves.
- **What it cost.** v did not need a rerun at n_TOF, because the tracks themselves gave v per acquisition. But:
  - D (15–45 clean tracks per acquisition) and B (no column) could only be corrected by borrowing A's and C's history.
  - Gaps up to 22 h could only be interpolated.
  - The absolute scale of D is still open.
  - Gain (and so efficiency) depends on the same water and temperature, and it has no in-situ monitor at all.

## Recommended measurements, ranked

| # | measurement | why (n_TOF evidence) | spec to aim for | where |
|---|---|---|---|---|
| 1 | **Water content of the gas** (ppm H₂O, dew-point or capacitive trace hygrometer) | The one quantity that tracked v (r = −0.84, through a 5 km proxy). Sets v, gain and attachment. | 10–10,000 ppm, ≤ 10 % reading accuracy, ≥ 1/min | Gas **inlet** to the first chamber and **outlet** of the last; ideally after each chamber, to see the chain dependence directly |
| 2 | **Oxygen in the gas** (trace O₂ analyser, ppm) | Electron attachment (late-charge loss seen on beam, ~160 ppm inferred); also tells a leak from permeation | 1–1,000 ppm, ≥ 1/min | Outlet of the chain (one analyser, switched between points if needed) |
| 3 | **Gas temperature and absolute pressure** | E/N, gain. The capsule showed a ±0.6 K daily hall swing and v responded at −2 %/K | T: Pt100 ±0.1 K on each chamber body or gas outlet. p: absolute gauge ±0.1 hPa | Each chamber (T), the outlet manifold (p) |
| 4 | **Hall air: temperature, humidity, barometric pressure** | It drove the water uptake. We had only an airport 5 km away and an accidental thermometer | Integrated T/RH/p sensor; ±0.2 K, ±2 % RH, ±0.5 hPa; ≥ 1/min | Next to the chambers, at the gas panel, along the gas lines (2–3 points) |
| 5 | **Gas flow per line, and bottle pressure / batch** | Flow sets how fast permeated water is flushed; a bottle change can step the composition | Mass-flow meter per line (read back, not only set); log bottle changes with lot numbers | Gas panel |
| 6 | **A gas-monitor chamber with a source** | Gives v (and gain) in the actual gas at all times, independent of beam tracks, so no chamber depends on borrowed history (D's case). Large TPCs run one for this reason (e.g. ALICE's GOOFIE). | Small drift cell with a fixed drift length and a collimated source; v to ~0.2 % per 10 min | On the exhaust of the last chamber |
| 7 | **Front-end temperature** | Pedestal and noise shifts (the 23 July noise step at n_TOF was a configuration change, but temperature was never logged to exclude it) | One sensor per FEU crate | Electronics |
| 8 | **HV voltages and currents** | Already logged at n_TOF and useful (flash charge, gain checks). Keep. | As at n_TOF | — |

**If only two items can be bought, take #1 at the chain outlet and #4 in the hall.** Together they would have explained
the n_TOF v history directly instead of through proxies. #6 is the step up: it removes the need to infer v from tracks.

## How to log them (the n_TOF lessons)

- **One clock, in UTC.** At n_TOF the DAQ files, the capsule log and the weather data used two time zones, and the DREAM
  timestamps had to be joined by hand. Log every sensor with UTC timestamps from the same NTP-synced machine as the DAQ,
  and write the latest readings into each acquisition's header (or a sidecar keyed on the acquisition tag).
- **Sample at ≥ 1/min.** The daily cycle and the ~hours response need minutes, not hours.
- **Keep the raw readings and the sensor calibrations with the data,** as was done for the capsule (the raw 2 s log on
  EOS plus a 5-min reduction in the repo).
- **Log the gas plumbing as built.** Tubing material and length per chamber, the order of the chain, and any change
  during the run (with dates). The permeation hypothesis cannot be tested without it.

## Design choices this suggests (not measurements, but cheap)

- **Gas lines:** use metal (stainless or copper) or low-permeation tubing between the bottle and the chambers, and keep
  plastic runs short. If the water does come in through the lines, this removes most of the effect at the source.
- **Feed the chambers in parallel, not in series.** A → B → C → D made the downstream chambers carry the upstream
  chambers' contamination. Parallel feeds with one flow meter each keep the chambers equal, and they make #1 per
  chamber meaningful.
- **Keep the in-situ v monitor in the analysis.** The column-duration v per acquisition (nTof_x17 `rerun/ntof/vt/`)
  worked and should run from the first day of the next run, alongside the sensors.

## What this does not establish

- That water is the cause. The correlation is with outdoor air 5 km away; a gas measurement (#1) is exactly what would
  settle it.
- The sensitivities above are for Ar/iC₄H₁₀ 90/10 at n_TOF's 233 V/cm drift field and n_TOF's plumbing. A different gas,
  field or line layout changes them.
