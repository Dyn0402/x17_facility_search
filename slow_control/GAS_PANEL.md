# Gas panel for a premixed, non-flammable gas (2026-11-26, split 2026-11-27)

Follows `SENSOR_OPTIONS.md` (17 Nov). That note chose the sensors. This note asks how the gas system fits together if
we run a **non-flammable, premixed gas** (for example Ar/CO₂), so that no mixer is needed. It is a design sketch:
nothing here is bought, drawn in CAD or bench-tested. Prices marked (est.) are guesses.

The hardware design of the per-chamber exhaust sensor (the "exhaust module": what is in it, how it is built and read
out) is kept in a separate, private repository since 2026-11-27. This note only uses what the panel needs from it: each
chamber's exhaust carries a sensor that logs the water content, the absolute pressure, the temperature and the flow.

## 1. What a premixed, non-flammable gas changes

- **No mixer is needed.** One bottle (or two on a changeover manifold) feeds the whole system.
- **The safety questions mostly disappear.** The sensors no longer sit in a flammable-gas line, so intrinsically safe
  (IS) versions are not needed and the exhaust can be vented to the hall extraction. LNL still has to agree to the
  gas itself (CO₂ is an asphyxiant at high flow; at 2–10 L/h it is negligible).
- **Some sensor choices change** (`SENSOR_OPTIONS.md` §7.4). A CO₂ mixture needs a CO₂-tolerant galvanic O₂ cell, and
  the humidity chips' cross-sensitivity has to be tested in the chosen gas.

## 2. Flow and pressure control: what we have, what we need

### 2.1 What was already researched

Flow **meters** were priced on 17 Nov (Sensirion SFC5500 €1.4k, Alicat €1.2–2k, rotameters €60–150; `research/D` §3).
Flow **control** for the four chambers and **pressure control** were not studied. This section fills that gap.

### 2.2 The n_TOF MFCs (superseded: they were borrowed, see §6.1)

The n_TOF mixer (`~/PycharmProjects/nTof_x17_DAQ/gas_mixer_control/README.md`) used two Bronkhorst thermal MFCs on one
FLOW-BUS cable, with Python control and CSV logging already written:

| controller | full scale | calibrated for |
|---|---|---|
| F-201CI (argon) | 7.6 ln/h | Ar, 3.0 bar-a in / 1.5 bar-a out |
| F-201DI (isobutane) | 10.5 ln/h | C₄H₁₀ |

With a premix, the argon MFC can control the **total flow** into the system. Its full scale of 7.6 ln/h matches our
2–10 L/h plan. Two points need care:
- The MFC needs its calibrated inlet pressure (~3 bar-a). At n_TOF the argon supply was only ~0.7 bar, so the valve
  pinned open at ~5.3 ln/h. A proper two-stage regulator set to ~2 bar gauge fixes this.
- A thermal MFC reads the gas's heat capacity. For Ar/CO₂ 90/10 the correction from the argon calibration is roughly
  8 % (estimate from the usual mixture rule; Bronkhorst's FLUIDAT gives the exact factor). This is a fixed number, not
  a drift.

The isobutane MFC is spare. It could feed a monitor chamber (the ⁵⁵Fe gain monitor of `SENSOR_OPTIONS.md` §3.5) or a
flushing line. **Update 26 Nov: these MFCs were borrowed from the CERN gas group and cannot go to LNL (§6.1).**

### 2.3 Splitting the flow over four chambers

We feed the chambers **in parallel**, as `SENSOR_OPTIONS.md` §5 already decided. There are two ways to split the flow:

| option | hardware | cost | comment |
|---|---|---|---|
| **A (recommended)** | one total-flow MFC + a manifold with 4 needle valves (+ rotameters for a visual check), and a **flow sensor on each chamber's exhaust** (§3) | needle valves and rotameters are in the `gas` budget item; flow sensors €45 each | The needle valves are set once. Each chamber's real flow is then read back digitally. |
| B | one MFC per chamber | +€1.2–2k per chamber (€5–8k) | Hands-off and exact, but the flow through a needle valve is stable once set, and option A already measures it. |

Option A also gives a **leak check**. The sum of the four exhaust flows should equal the MFC's flow. A leak of a few %
in one chamber shows up as a missing few % in that chamber's exhaust.

### 2.4 Pressure: keep the overpressure fixed, measure the absolute pressure

There are two pressures one could control:
- the **absolute pressure** of the gas, which sets the gas density, and so the gain and the drift velocity;
- the **overpressure** of the chamber relative to the hall, which pushes on the 60 µm mylar windows.

**We should control the overpressure and only measure the absolute pressure.** The barometric pressure moves by
±20–30 hPa over a run. A controller that held the absolute pressure constant would therefore push the windows by up to
±20–30 hPa, which is far more than a 40 × 36 cm, 60 µm window should see. For this reason small MPGD set-ups keep
a few hPa of overpressure and correct the gain and drift velocity for p/T in the analysis (density moves by 0.1 %/hPa).

The overpressure is set passively. Each chamber's exhaust goes to a common manifold, and the manifold ends in an oil
**bubbler**. The oil height sets a few hPa of overpressure, and the bubbler stops air from diffusing back. Two
additions are cheap and worth having:
- **A relief bubbler (or relief valve) at ~10–20 hPa** on the inlet manifold. It protects the windows if the exhaust is
  blocked or a valve is closed by mistake. **(ask CEA: the largest overpressure the windows may see.)**
- The overpressure is **measured** for free by the exhaust sensors (§3): the sensor's barometer minus the hall
  barometer gives it to ~0.1 hPa. This replaces the Sensirion SDP810 differential sensor of `SENSOR_OPTIONS.md` §3.4,
  which has a 20-week lead time.

An electronic back-pressure controller (Bronkhorst EL-PRESS, or an Alicat PCD in differential mode; quote only,
~€2–4k (est.)) would hold the overpressure more tightly and could be changed remotely. We do not think it is needed:
the bubbler does the same job, and its small pulsing at each bubble (a fraction of a hPa) will be visible in the data
but does not matter. Alicat's own material describes the dual-valve PCD as a controller for closed volumes, and
recommends a back-pressure regulator for flowing low-flow systems
([Alicat PCD](https://www.alicat.com/pressure-products/dual-valve-pressure-controllers/),
[Alicat + Equilibar note](https://alicat.com/?p=38345)).

### 2.5 The panel, end to end

```
bottle(s) ─ 2-stage regulator (~2 bar g) ─ WIKA HP gauge (logged) ─ 3A dryer ─ MFC (total flow, logged)
   ─ INLET SENSOR (reference H₂O, T, p) ─ relief bubbler (10–20 hPa)
   ─ manifold: 4 × needle valve + rotameter
        ├─ chamber A ─ EXHAUST SENSOR A ─┐
        ├─ chamber B ─ EXHAUST SENSOR B ─┤
        ├─ chamber C ─ EXHAUST SENSOR C ─┼─ exhaust manifold ─ O₂ cell ─ bubbler (few hPa) ─ vent
        └─ chamber D ─ EXHAUST SENSOR D ─┘
   HALL SENSOR (open to air): hall T, RH, p
```

All lines are Synflex-type aluminium-barrier tube or copper (budget item `gaslines`).

## 3. The exhaust sensors: one per chamber

We put one sensor on each chamber's exhaust, as `SENSOR_OPTIONS.md` already planned on 17 Nov (an SHT85 + BMP585 cell
after each chamber), with a flow reading added. The exhaust is the right place for four reasons:
1. The exhaust gas is the gas that was in the chamber. The **difference between a chamber's exhaust and the inlet
   sensor** is the water that chamber added. That is exactly the measurement `SENSOR_OPTIONS.md` §7.5 says would
   settle where the n_TOF water came from.
2. At 1–2 L/h the pressure drop along a short metal line is negligible (~0.02 hPa for 2 m of 4 mm bore). **This holds
   only if there is no filter or other restriction between the chamber and the sensor** (corrected in §6.3).
3. With parallel feeds, each chamber's exhaust carries only that chamber's flow, so **a flow sensor there reads that
   chamber's flow**.
4. The sensor adds no material or volume upstream of the chamber, so it cannot contaminate the gas the chamber sees.

Their barometers, minus a hall barometer, give each chamber's overpressure. This replaces the Sensirion SDP810
differential sensor of `SENSOR_OPTIONS.md` §3.4 (20-week lead time). The per-chamber flow readings replace the Tier 2
inlet and exhaust flow meters (€2.4–2.8k). The budget item `slowctl` has not been changed yet.

## 4. Status of the water measurement

- **Chosen, not bought.** The plan is SHT85 chips zeroed on dry bottle gas, cross-calibrated in series, and anchored to
  a reference hygrometer (a Vaisala DMT143, borrowed from CERN EP-DT's DRD1 gas monitor, or a bought CS FA510).
- **Not bench-tested.** The two open tests are the chips' cross-sensitivity to the chosen gas (CO₂ instead of
  isobutane now) and their recovery after humid exposure at our low flows.
- **Not yet asked.** The CERN EP-DT loan has not been requested.

## 5. Next steps

1. Choose the gas. Everything above assumes a non-flammable premix (Ar/CO₂ or similar).
2. **(ask CEA)** The largest overpressure the drift windows may see. This sets the relief bubbler.
3. Bench-test the exhaust sensors with dry bottle gas: water zero and recovery, flow against the MFC, barometer offset
   against the hall barometer.
4. Then update `slowctl` in `budget/items.py`.

## 6. Update 2026-11-26 (b): Dylan's answers

### 6.1 Flow control: the Bronkhorst MFCs were borrowed

The two Bronkhorst MFCs belong to the CERN gas group and cannot come to LNL. We need our own controller. Per-chamber
control would be ideal, but the cheaper layout is **one flow controller on the inlet and one flow meter (or back-pressure
controller) on the common exhaust**, with a pressure sensor on each detector. The exhaust sensors (§3) give each
detector's pressure and, with a flow reading, each detector's flow as well.

| role | candidates | price | comment |
|---|---|---|---|
| inlet MFC, ~0–200 mln/min (0–12 L/h) | Vögtlin red-y smart GSC (0–25 … 600 mln/min ranges, [datasheet](https://voegtlin.com/data/329-2023_en_infosmart.pdf)); Sensirion SFC5500 (low ranges exist, €1.4k, `research/D` §3); Alicat MC (has Ar/CO₂ gas tables, ~€1.95k) | €0.8–2k (Vögtlin quote only, est. €0.8–1.2k) | The cheap Sensirion SFC6000D (£278 for 5 slm, [DigiKey](https://www.digikey.co.uk/en/products/detail/sensirion-ag/SFC6000D-5SLM/17829202)) is **too coarse**: its smallest range is 5 slm, and its accuracy floor of 0.2 % FS is 10 sccm, ~10 % of our flow ([datasheet](https://admin.sensirion.com/media/documents/442A3611/64958B2C/DS_SFC6000D_SFM6000D.pdf)). |
| exhaust, option A | the same-family **meter** on the common exhaust, + oil bubbler | €0.7–1.4k (est.) | Same model in and out: the gas factor cancels and a few-% leak of the whole system shows. The bubbler sets the overpressure. |
| exhaust, option B | a **back-pressure controller with flow measurement** (Vögtlin red-y smart pressure controller, [sheet](https://voegtlin.com/data/329-2060_en_infosmartpressure.pdf)) | quote, est. €1.5–2.5k | Holds the common exhaust at a set overpressure **and** measures the returned flow, in one device. Whether it can regulate relative to the hall (gauge) at a few hPa: **(check with Vögtlin)**. A bubbler stays behind it to stop back-diffusion. |
| per chamber | a small flow sensor in each exhaust sensor | (private design) | Readback only. The needle valves are set once against these readings. |
| cheap fallback | used Bronkhorst / Brooks MFC (auction sites) | €0.3–0.8k (est.) | Needs recalibration for our gas; its condition is unknown. |

**Recommended:** an inlet MFC and option A (€1.5–3k), with the per-chamber flow in the exhaust sensors. Option B is worth a
quote, because it would also make the overpressure adjustable from the DAQ.

### 6.2 Water: expect CO₂, and plan without a CERN loan

- **CO₂ is a known problem for the SHT85.** A DLR study in simulated Martian air found that the SHT85 and the SHT75
  "show a strong cross-sensitivity to CO₂" ([Lorek & Garland, egusphere-2024-3944](https://egusphere.copernicus.org/preprints/2025/egusphere-2024-3944/egusphere-2024-3944.pdf)).
  That was ~95 % CO₂ at low pressure, not 10 % at 1 bar. However, it means the chips must be zeroed and spanned in the
  **actual mixture**, not in argon:
  1. zero in dry Ar 5.0 and in dry premix, and record the difference (this is the CO₂ offset);
  2. span in wet premix against a reference (below).
- **The reference hygrometer, without a CERN loan.** We keep three options open:
  | option | price | accuracy | comment |
  |---|---|---|---|
  | buy a CS FA510 dew-point transmitter | €1.4k | ±1 °C dew point (≈ ±7 % of reading) | the 17 Nov choice |
  | buy a Vaisala DMT143, or a used DMT340 | €1.3–1.8k; used $0.75–1k | ±2 °C dew point | |
  | **DIY humidity generator**: saturate a small stream of the premix in water at a known temperature (an ice-water bath at 0.0 °C gives 6.11 hPa, ~6,000 ppm at 1 atm), then dilute it with dry premix at a measured flow ratio | €0.1–0.3k + a second flow reading | ~±3–5 % (est.), set by the flow ratio and the saturation efficiency | Cheap and traceable to a temperature and two flows. |
  Our recommendation is to build the DIY generator in any case, and to buy the FA510 only if the generator does not
  reach ±5 %.

### 6.3 Pressure drop: filters matter (correction)

The statement in §3 that the exhaust sensor's pressure equals the chamber's was too strong. It is true for the tube and
false for a filter. The estimates at 1 L/h of argon (viscosity 2.2×10⁻⁵ Pa·s) are:

| element | Δp at 1 L/h | basis |
|---|---|---|
| 2 m of 4 mm bore tube | 0.02 hPa | Poiseuille |
| 10 m of 4 mm bore tube | 0.1 hPa | Poiseuille |
| 7 µm sintered filter, 5 cm² cylinder, 2 mm wall | ~0.2 hPa | Darcy, Kozeny–Carman permeability ~10⁻¹² m² (estimate) |
| 7 µm sintered disk, 1 cm² | ~1 hPa | same |
| 0.5 µm disk, 1 cm² | ~10 hPa | permeability ~10⁻¹³ m² (estimate) |
| needle valve | set by us, typically 100s of hPa | deliberate: it is the flow splitter |
| oil bubbler | the oil height, a few hPa | deliberate: it is the overpressure |

The drop grows linearly with flow and grows as a filter clogs. A clean coarse filter is comparable to the
overpressure itself, and a fine or clogged one exceeds it. So:
- **Put the filters on the inlet side of each chamber**, after the needle valve. There they protect the mesh, and their
  drop adds to the needle valve's, where it does no harm.
- **Keep the exhaust path from the chamber to the sensor free of filters.** Then the sensor reads the chamber pressure
  to ~0.02 hPa.
- If a chamber does need an exhaust filter, the sensor's barometer goes **upstream** of it. A second barometer after the
  filter then measures the filter's drop, which also tells us when it is clogging.
- These are estimates. The bench test measures the real drops with the exhaust sensors' own barometers.
- **(ask)** Where the filters sat at n_TOF, and their grade.

## 7. Update 2026-11-26 (c): NSW gas, flushing, filters and valves on each detector

- **Gas: probably the NSW mixture, Ar/CO₂/iC₄H₁₀ 93/5/2** (not final). ATLAS chose it for the New Small Wheel partly
  because it is classified as non-flammable; confirm that with the supplier and LNL. Consequences:
  - the chips are zeroed in dry Ar 5.0 and in dry premix; the difference is the CO₂ + isobutane offset together;
  - the O₂ cell must be the CO₂-tolerant type (5 % CO₂);
  - the flow devices need an Ar/CO₂/iC₄H₁₀ gas factor (Alicat and Bronkhorst-type tables have one);
  - bottle condensation (`SENSOR_OPTIONS.md` §2) matters much less at 2 % isobutane.
- **Flushing at ~30 L/h built up a lot of pressure (Dylan).** The windows are only glued, though normally they see
  little pressure. The §6.3 estimates at 30 L/h: 2 m tube 0.6 hPa, 7 µm filter 7–37 hPa, 0.5 µm filter ~370 hPa. If the
  30 L/h was the total over four detectors, divide by four. So the outlet filter and valve explain the flushing pressure.
- **Each detector has a filter and an on/off valve on its inlet and its outlet (Dylan).** Therefore the exhaust sensor goes
  **directly on the detector outlet, before the outlet filter and valve**. Then:
  - it reads the detector pressure even when the outlet filter clogs;
  - with both valves closed it measures the detector's pressure decay (a leak test per detector);
  - the logger alarms on overpressure, which is the protection during a flush.
- **Flushing hardware:** a manual bypass around the inlet MFC (needle valve + 0–60 L/h rotameter, ~€150), so that the
  MFC stays sized for running (0–200 mln/min) where it is accurate. The exhaust sensors' flow readings saturate at ~6 L/h during
  a flush, which is acceptable.
- The relief valve is set below the windows' limit, which is still **(ask CEA)**.
