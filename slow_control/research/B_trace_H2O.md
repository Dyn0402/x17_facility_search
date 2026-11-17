# Research notes B: water in the chamber gas, 10–20,000 ppmv (2026-11-17)

Web research (agent report, lightly edited). $1 ≈ €0.86, ex VAT unless marked. "quote only" = no public price.
Synthesis: `../SENSOR_OPTIONS.md`. Unit table: `../water_units.py` → `../out/water_units.csv`.

## 1. What the requirement means

1000 ppmv at 1013 hPa = 1.01 hPa = 4.3 % RH at 20 °C (3.2 % at 25 °C); 1 %RH = 230 ppm (20 °C) / 312 ppm (25 °C).

| ppmv | dew/frost pt | RH 20 °C | ±2 °C dew-pt error | ±1.5 %RH error | ±0.2 %RH (after zero-cal) |
|---|---|---|---|---|---|
| 100 | −42 °C | 0.43 % | +26/−21 % | ±470 % | ±62 % |
| 1,000 | −20 °C | 4.3 % | +21/−18 % | ±47 % | ±6 % |
| 2,000 | −13 °C | 8.7 % | +20/−17 % | ±23 % | ±3 % |
| 10,000 | +7 °C | 43 % | +15/−13 % | ±5 % | ±0.6 % |
| 20,000 | +18 °C | 87 % | +13/−12 % | ±2 % | ±0.3 % |

- A ±2 °C dew-point transmitter (Vaisala, Michell Easidew, E+E class) is ±15–20 % of the ppm value everywhere: it does
  not meet "≤ 10 % of reading". Only ±1 °C units (CS FA510 above −20 °C Td) or chilled mirrors (±1–2 %) do.
- A polymer RH chip as shipped (±1–1.5 %RH) is useless below ~1000 ppm in absolute terms. With an in-situ zero on dry
  bottle gas and cross-calibration of all chips on one gas: ~±10 % at 1000 ppm, ±3–5 % at ≥ 2000 ppm.
- At 20,000 ppm the dew point is +18 °C: cells must sit warmer than that. RH at fixed water changes ~6 %/K: read T at the
  die (SHT chips do). Total pressure to ±1 % for the ppm conversion.

## 2. Options

### 2.1 Polymer RH chips in a flow cell (cheapest)

- SHT45 ([datasheet](https://cdn.sparkfun.com/assets/9/7/7/a/d/SHT45-AD1B-R2_datasheet.pdf)): ±1.0 %RH typ, repeatability
  0.08 %RH (3σ), **hysteresis 0.8 %RH (~190–250 ppm, after humid exposure)**, drift < 0.2 %RH/yr, t63 4 s, heater.
- SHT85 ([datasheet](https://psl.noaa.gov/data/obs/instruments/SensirionSHT85.pdf)): ±1.5 %RH, membrane, pin package;
  €22 ([SOS](https://soselectronic.com/de-at/products/sensirion/sht85-305843)), €27 ([DigiKey](https://www.digikey.de/en/products/detail/sensirion-ag/SHT85/9666378)).
- **Isobutane: no published data.** Sensirion warns VOCs in the polymer shift offset and sensitivity
  ([handling](https://www.sos.sk/docs/1/1872/Sensirion_Humidity_Sensors_Handling_Instructions_V4.pdf)); Vaisala uses
  heated purges against small hydrocarbons ([note](https://www.esis.com.au/how-to-measure-humidity-in-environments-with-chemicals/)).
  Test: dry Ar 5.0 vs dry Ar/iC₄H₁₀ from the bottle (both a few ppm); any offset is the cross-sensitivity.
- Precedent: DLR runs SHT85s in stainless flow cells against a dew-point mirror ([Lorek & Garland 2025](https://gi.copernicus.org/articles/14/131/2025/)).
  No HEP gas system found using Sensirion in the stream.
- Ready-made: Rotronic HC2A-S (±0.8 %RH) €342 ([RS](https://ie.rs-online.com/web/p/products/1365501)) + flow chamber (quote).

### 2.2 Industrial dew-point transmitters

| Model | Principle | Range | Accuracy | Interface | Price | Notes |
|---|---|---|---|---|---|---|
| **CS Instruments FA510** | polymer | −80…+20 °Ctd | **±1 °C (+50…−20)**, ±2 (−20…−50) | 4–20 mA + RS-485 Modbus | **€1,424 net** ([Filcom](https://www.filcom-technik.de/en/shop/0699-0510-cs-instruments-fa-510-dew-point-sensor-for-adsorption-dryers-incl-factory-certificate-4-20-ma-111341)) | only ±1 °C unit with an EU price; ask about Ar/iC₄H₁₀ |
| **Vaisala DMT143** | DRYCAP polymer, auto-cal | −70…+60 °C Td | ±2 °C | mA/V + RS-485 | ~€1.3–1.8k ([Selectum $1,868](https://selectumllc.com/i/vaisala-dmt143)); eBay "new" €440–540, unverified | used by CERN EP-DT's GMS; flow "no effect" ([spec](https://www.vaisala.com/sites/default/files/documents/DMT143-2024Bid.pdf)) |
| Vaisala DMT152/153 | polymer | −80…−10 °C Td | ±2 °C | – | quote | too dry (top ~2600 ppm) |
| Vaisala DMT340 | polymer | −70…+80 °C Td | ±2 °C | mA, RS-232/485 | used $750–1,000 ([reuzeit](https://reuzeit.com/product/2019862780)) | best used buy |
| Michell Easidew EA2/M12 | ceramic | −110…+20 °C | ±2 °C | 4–20 mA / Modbus | M12 $2,556; **I.S. $3,231–3,985** ([Instrumart](https://www.instrumart.com/products/all-part-numbers/46006)) | ATEX Ex ia version ([datasheet](https://www.processsensing.com/docs/datasheet/Michell_Instruments_Easidew_Transmitters_EN_Datasheet.pdf)) |
| Michell SF82 | ceramic | to −60 °C | ±2 °C | – | $2,556 ([Dwyer](https://www.dwyeromega.com/en-us/sf82-transmitter-2-wire/p/SF82-TX)) | compressed air |
| Michell Pura | ceramic | ppb–~1000 ppm | ±1–2 °C | 4–20 mA | $3,092–6,826 ([Instrumart](https://www.instrumart.com/products/all-part-numbers/46032)) | too dry |
| E+E EE371 | polymer | −60…+60 °C | ±2 °C | mA, Modbus | $2,313–2,892 ([Alpha Controls](https://usa.alphacontrols.com/products/ee371-dew-point-temperature-transmitter)) | |
| Rotronic HF532 | RH | – | ±0.8 %RH | mA | $804–1,009 + probe ([Kele](https://www.kele.com/product/humidity/humidity-temperature/rotronic-instrument/hf532-da6xx24x)) | same physics as 2.1 |
| Panametrics MMS35 / M-probe | Al₂O₃ | −110…+20 °C | ±2–3 °C, drifts | mA | retired; dew.IQ $4,040; used $179–3,419 ([Instrumart](https://www.instrumart.com/products/18494/panametrics-mms-35)) | frequent recal |

All can sit in-line at 2–10 L/h. **But CERN saw a low-flow effect:** two DMT143s on dry Ar read 6000 and 8000 ppm for the
first 2 h at 3 L/h, converging to 75 ppm only at ≥ 5 L/h ([CERN summer report](https://repository.cern/records/abnr5-8s651/files/Summer_Project_Report.pdf)).
Budget hours of stabilisation; small-volume cells.

### 2.3 Chilled mirrors

Edgetech DewMaster $3,750–6,385 ([Alpha Controls](https://usa.alphacontrols.com/products/dewmaster-chilled-mirror-hygrometer));
Michell S8000 from CAD 24,289 ≈ €15k ([link](https://www.alphacontrols.com/S8000-Chilled-Mirror-Hygrometer/model/5666));
MBW 373 quote (~€30–45k; MBW 473 $21,965, [Instrumart](https://www.instrumart.com/products/48878/mbw-calibration-473-dew-point-hygrometer)).
±1–2 % of ppm; want ~0.25–1 L/min. Traps: frost vs supercooled water between 0 and −20 °C (1000–6000 ppm, our range, ~10 %
ambiguity); isobutane at 0.1 bar condenses on the mirror below ~−55 °C (floor ~20 ppm).

### 2.4 QCM, spectroscopy, portables

- Michell QMA601: 300 mL/min + 3 Nl/min bypass; trace range. Unsuitable.
- Tiger Optics HALO CRDS: ~$25k, 0–2.5 ppm, ~1 L/min ([Fermilab note](https://indico.cern.ch/event/617303/attachments/1420922/2231395/Gas_analysers.pdf)). Unsuitable.
- LI-COR LI-850 (NDIR, 0–60,000 ppm, ±1.5 %, 14.5 mL cell; [specs](https://www.licor.com/support/LI-850/topics/specifications.html)):
  used $1,500 ([eBay](https://www.ebay.de/itm/226979412980)); calibrated in air, Ar broadening and isobutane C–H bands need
  own calibration. A cheap second opinion.
- Vaisala DM70 portable: new $4,259–5,634, used ~$1,000, rentable ([Electrorent](https://electrorent.com/uk/products/electrical-and-power-quality/transformer-and-motor-testing/vaisala/dm70/01t1O000004Tf9rQAC)). Spot checks.
- Michell MDM300 IS $9,186 ([DwyerOmega](https://www.dwyeromega.com/en-us/portable-and-intrinsically-safe-advanced-dew-point-hygrometer-for-industrial-gas-applications/MDM300/p/MDM300-IS)).

### 2.5 CERN / HEP practice, borrowing

- LHC analysis modules monitor O₂ and H₂O continuously, analysers switched between zones; models not public. EP-DT minutes
  17 Sep 2026 mention an "O2+H2O analyser" and "CMS DT vaisala" ([minutes](https://indico.cern.ch/event/1732867/note/)).
- **CERN EP-DT portable Gas Monitoring System for DRD1 users**
  ([slides](https://events.camk.edu.pl/event/124/contributions/1185/attachments/804/2177/Rigoletti%20-%20Salomon%20-%206th%20DRD1%20collaboration%20meeting.pdf),
  [report](https://repository.cern/records/abnr5-8s651/files/Summer_Project_Report.pdf)): stainless 6 mm Swagelok in a Peli
  case, Vaisala DMT143 in-line, zirconia O₂ (**not usable with isobutane**), p, flow, ambient, Raspberry Pi + Grafana,
  < 5,000 CHF. One unit "available at the GDD", a second being built. Contacts: G. Rigoletti, O. Salomon, F. Brunbauer.
- TUM (ALICE TPC) measured 0–5000 ppm water in Ar/CO₂ with a Rapidox 3100 after the detector at 10 L/h
  ([arXiv:2503.03012](https://arxiv.org/abs/2503.03012)).

## 3. Plumbing and permeation

- **Belle** (¼″ polyolefin, 0.89 mm wall): Q(ppm) ≈ 2080·l·R/F (l in m, R ambient RH fraction, F in cc/min); predicted
  842, measured 940 ppm. BaBar's Teflon line ~30–200 ppm. "Copper permeates no water vapor."
  ([Lu & McDonald 2007](https://project-cms-rpc-endcap.web.cern.ch/RPC/Chambers/OtherEXP/Belle/HumidityTest-10022007.pdf))
- 10 m of PE at 50 % RH: 62 ppm at 10 L/h, 315 ppm at 2 L/h.
- Relative to PE (handbook film data; the measured tube numbers in `../SENSOR_OPTIONS.md` §2 are what to trust):
  PU ~50–300× ([Covestro](https://solutions.covestro.com/en/products/platilon/platilon-m-2202-ac-t_000000000000802469)),
  nylon ~5–15× ([CMC](https://www.cmc.de/en/blog/know-how-5/water-vapor-permeability-of-various-plastic-films-181);
  [CERN pipe materials](https://detector-gas-systems.web.cern.ch/Material%20and%20Standards/pipematerials.htm)),
  PTFE/PFA/FEP ~0.1–0.3× ([CERN talk](https://indico.cern.ch/event/843711/contributions/3607901/attachments/1931441/3199038/talk.pdf)),
  metal 0. CERN: water permeation "largely independent of the gas flow" (i.e. the ingress rate; ppm ∝ 1/flow).
- **One sensor per point, not stream switching:** no spare flow for a bypass; each switch re-equilibrates walls (Fermilab:
  water analysers "can't be switched between sources on a short time scale").
- Dead volume: 1/8″ SS ≈ 2.4 cm³/m (4 s at 33 sccm); a 10 cm³ cell is 20 s at 10 L/h, 1.2 min at 0.5 L/h. Wall adsorption dominates.
- Stainless / electropolished Swagelok or VCR; each fitting is an O₂ leak point: leak-check. Vent analyser exhaust into the
  detector exhaust. Analysers wanting 0.5–1 L/min can only sample at the inlet (extra gas from the regulator).
- ATEX: no O₂ inside the line, total isobutane 0.1–1 L/h; whether I.S. units are needed is LNL safety's call.
- After each chamber separates tubing permeation from chamber sources (windows, FR4, glue).

## 4. Ranking (agent's)

| | Per point | Inlet + outlet | 5 points |
|---|---|---|---|
| (a) SHT85/SHT45 in stainless cells (+ shared Pi, mux, p sensor ~€80) | ~€100–150 | ~€300–400 | ~€600–900 |
| (b) CS FA510 + cell | ~€1.7–2.0k | ~€3.5–4k | ~€8.5–10k |
| (b′) DMT143 / used DMT340 + cell | ~€1–2k | ~€2–4k | ~€5–10k |
| (c) chilled mirror, switched | – | DewMaster ~€4–6k; S8000/MBW €16–46k | same |

Plan: (a) at all 5 points; cross-calibrate all chips in series on one gas; zero on dry bottle gas; isobutane test; span
anchored to one traceable unit at the outlet (borrow the CERN GDD GMS, or buy one FA510). ~€0.7k borrowed / ~€2.5k bought.
Meets ±10 % above ~1000 ppm and per-chamber differences to ~±50 ppm. A mirror only if tubing is fixed and ≤ 10 % below
~300 ppm is needed.
