# Slow-control sensors for the next run: options, costs, readout (2026-11-17)

Follows `ENVIRONMENT_SENSORS.md` (what n_TOF taught us, which measurements, ranked). This note answers **what to buy,
what it costs, and how to read it out**. Facility-independent; LNL is the case (Ar/iC₄H₁₀, four chambers, 2–10 L/h total).
Sourced detail, with every price link, is in `research/`:

| file | covers |
|---|---|
| `research/A_ambient_readout.md` | hall T/RH/p, chamber Pt100s, gas-line pressure, Raspberry Pi readout, radiation, FEU temperature |
| `research/B_trace_H2O.md` | water in the gas: RH chips in flow cells, dew-point transmitters, chilled mirrors, spectroscopy, CERN practice |
| `research/C_trace_O2.md` | O₂ in the gas: galvanic cells and analysers, why zirconia is out, attachment numbers |
| `research/D_analysers_flow_monitor.md` | RGA / GC / isobutane-fraction sensors, monitor chambers, flow meters, bottles, line materials, dryers |
| `water_units.py` | ppmv ↔ RH ↔ dew point (`out/water_units.csv`) |
| `estimates.py` | the back-of-envelope numbers in §2 (tube and window ingress, bottle condensation) |

Prices are 2026, ex VAT, mostly public distributor or US list prices converted to €; quote-only items are estimates and
marked (est.). Nothing here has been bench-tested.

## 0. Bottom line

1. **The no-brainer tier costs ~€1.5–2.5k and covers most of what n_TOF lacked.** It is: a Raspberry Pi logging to one
   UTC clock; hall T/RH/p; a cheap humidity + pressure chip in a small stainless cell at the gas inlet and after each
   chamber; Pt100s on the chamber bodies; and pressure gauges on the bottles. The humidity chips are the surprise
   (§3.2). Water at n_TOF was inferred at 0.2–1.5 %, i.e. 2,000–15,000 ppm, or 9–65 % RH at 20 °C. In that range a €25
   Sensirion chip, zeroed on dry bottle gas, reads water to ±3–10 %, and the chamber-to-chamber differences to
   ~±50 ppm. That is good enough to correct v.
2. **Fix the gas system before you measure it.** Metal lines, parallel feeds and a 3A dryer cost €0.6–1.6k (§2, §5).
   Measured ingress through plastic tube is ~50–100 ppm per metre at 0.5–1 L/h. A 60 µm mylar window passes
   10²–10⁴ ppm, depending on its metallisation (estimate). The LNL plan drops the 9 µm Cu cathode behind the window,
   which removes a barrier.
3. **O₂: one galvanic trace cell at the outlet, ~€1k DIY or ~€2–2.5k as an analyser.** Zirconia analysers are out,
   including the one in CERN's own DRD1 gas monitor: they burn the isobutane and read nothing (§3.3). O₂ is needed as
   well as H₂O. It is the quantity that attaches electrons, and the O₂:H₂O ratio tells a leak (≈17:1) from permeation
   (≪1).
4. **A traceable water reference is worth borrowing, not buying.** CERN EP-DT has a portable DRD1 Gas Monitoring System
   (Vaisala DMT143, Pi + Grafana) at the GDD lab. Otherwise one CS FA510 (±1 °C dew point, €1.4k) anchors the chips.
5. **Full gas analysers are overkill for a 4-week run.** An RGA/QMS system costs €25–60k, a micro-GC €30–45k and a
   chilled mirror €4–45k. None of them does the core job better than the tiers above at our 2–10 L/h. The exceptions
   worth their price are an isobutane-fraction meter (SRS BGA244, €4.3k) and a home-made ⁵⁵Fe gain-monitor chamber
   (€0.5–1.5k).
6. **Recommended package: Tier 1 + gas fixes + Tier 2 ≈ €9.2k (6–13k)** (§6). Tier 1 alone is the floor.
7. **Update (§7):** n_TOF's 5–10 m of plastic plus 0.5 m jumpers explain ≲ 300 ppm (unless it was PVC or silicone), so the water most likely entered at the chambers, and the per-chamber cells are the key measurement. The FEUs have on-board temperature sensors (MAX16031, readable with `MaxRead`). The n_TOF flow CSVs probably still exist on the DAQ PC.
8. **A vs C vs D (§7.5):** tubing alone predicts C/A ≤ 1.2 and D/A ≤ 1.3, but 3.0 and 2.9 were observed. The water enters in the chambers. Better tubing (§8; aluminium-barrier Synflex-type plus copper, €0.4k, budget `gaslines`) is cheap insurance, not the cure.

## 1. What precision we need

| quantity | n_TOF sensitivity | target for ≤ 0.5 % in v | achievable cheaply? |
|---|---|---|---|
| H₂O in gas | v −2 %/hPa of *outdoor* vapour. A July run read v ~12 % low, attributed to ~0.2 % water (≈ −6 % per 1000 ppm, inferred) | ~±100 ppm absolute, or better relative | yes: zeroed SHT-class chip ~±50 ppm relative, ±3–10 % of reading at ≥ 1000 ppm |
| gas T | −2.2 %/K | ±0.2 K | yes: Pt100 + MAX31865 or PT-104 |
| gas p | density: 0.1 %/hPa | ±0.5 hPa | yes: BMP390/585 ±0.5 hPa, 0.03–0.06 hPa relative |
| O₂ | attachment η ≈ (2–10)×10⁻⁵ cm⁻¹ per ppm in 90/10 (extrapolated, `research/C` §6). 160 ppm over 3 cm ≈ 1–5 % charge loss | ±5 ppm at 10–1000 ppm | yes: galvanic cell ±1 ppm + 2–5 % |
| iC₄H₁₀ fraction | ±2 % relative (certified premix) moves v ≪ 1 % | ±1 % relative | BGA244, if wanted |

Units: 1000 ppmv = 1.01 hPa = 4.3 % RH at 20 °C = −20 °C frost point; 1 %RH = 230 ppm at 20 °C (`water_units.py`).

## 2. Where the water probably comes from (estimates)

From `estimates.py`. The inputs are literature values (`research/B` §3, `research/D` §0, §5), not our plumbing:

| source | ppm of H₂O | basis |
|---|---|---|
| 6 mm PU tube, per metre | 96 / 48 / 19 at 0.5 / 1 / 2.5 L/h | CERN, measured: +16 ppm/m at 3 L/h ([arXiv:2202.12007](https://arxiv.org/abs/2202.12007)); ppm ∝ 1/flow |
| ¼″ polyolefin, 50 % RH, per metre | 125 / 62 / 25 | Belle, measured: Q = 2080·l·R/F |
| one 40 × 36 cm, 60 µm PET window, bare | ~12,000 / 6,000 / 2,400 | estimate: film WVTR ~0.8 g/m²/d at 22 °C / 50 % RH |
| the same, aluminised (×10 to ×100 better) | ~1,200–120 / 600–60 / 240–24 | estimate: depends on the coating's optical density |
| Cu / stainless line | 0 | |

- **Water ingress varies with outdoor humidity, and the series feed adds every chamber's water into D.** Both match
  what n_TOF saw: D and C moved ~3× more than A.
- **Windows.** At n_TOF a 9 µm Cu cathode sat behind each window. Whether the 5 mm gap between them is flushed is an
  open question in `nTof_x17/docs/detector_spec/spec.py`. The LNL plan (`budget/items.py`, `windows`) makes the
  aluminium of the mylar the cathode, so the window's metallisation becomes the only water barrier. Specify a
  high-barrier coat (ask CEA / the supplier for WVTR), or measure after each chamber and see.
- **n_TOF tubing (Dylan, 17 Nov):** 5–10 m of plastic in and out plus 0.5 m jumpers. At the measured rates that is ≲ 300 ppm, too little for the inferred ~2000 ppm or the A → D growth, unless the plastic was PVC or silicone. See §7.1.
- **Bottles can condense isobutane.** This is an ideal-mixture estimate, and real high-pressure mixtures differ.
  - A full CERN-store 95/5 bottle (2.15 m³ in 50 L, ~43 bar) has an isobutane dew point near **+9 °C**.
  - A 90/10 mixture at 30 bar is at ~20 °C.
  - In a cold Italian bottle store in winter, the gas can come out isobutane-lean, then turn rich as the bottle
    empties.
  - Ask the supplier for the fill pressure and the minimum storage temperature. Keep the bottles indoors, and log the
    bottle pressure and temperature.

## 3. The options, by measurement

### 3.1 Hall air and chamber temperature (Tier 1)

| item | spec | price | note |
|---|---|---|---|
| Yoctopuce Yocto-Meteo-V2 (USB) | T ±0.2 K, RH ±1.5 %, p rel. ±0.01 hPa | ≈ €65 | plug and play, Python API; 2–3 positions |
| SHT45 / HDC3022 + BMP390/585 breakouts | ±0.1 K, ±1 %RH, ±0.5 hPa | €10–16 each | the cheapest route to the same spec |
| Pt100 4-wire + MAX31865 | ±0.1 K after a 1-point calibration | €19 + €46 (class B) | one per chamber body (taped, under foam) and one in the outlet gas |
| Pico PT-104 (4 ch) + 1/10 DIN probes | 0.01 K resolution, ±0.03 K | €689 + €132 per probe | Tier 2 upgrade, if ±0.1 K is not enough |
| DS18B20 (1-Wire) | ±0.5 K | ~€5 | one per FEU crate (crate air). The FEUs' own MAX16031 board sensors (§7.2) are a bonus, not a replacement. |
| Comet T7611 PoE | ±0.4 K, ±2.5 %RH, ±1.3 hPa | €482 | an independent backup logger that keeps logging if the Pi dies (optional) |
| Reference barometer | – | borrow (Vaisala PTB330 €3.3k) | one-off offset for the MEMS barometers; or use the Venice/Padova METAR |

Consumer Wi-Fi sensors (Shelly, Govee) are out: they have no pressure, depend on a cloud, and give poor timestamps.

### 3.2 Water in the gas

| tier | hardware | per point | 5 points (inlet + after each chamber) |
|---|---|---|---|
| **1: SHT85/SHT45 in a stainless ¼″ tee or block cell** (+ a BMP585 in the same cell for p) | Sensirion chip; repeatability 0.08 %RH (≈ 20 ppm), hysteresis 0.8 %RH after humid exposure | ~€100–150 with the cell | **€0.6–0.9k** |
| 2: one traceable anchor at the outlet | CS FA510, ±1 °C Td (−20…+50 °C), Modbus, €1.4k; or Vaisala DMT143, ±2 °C, ~€1.3–1.8k (used DMT340 $750–1k) | €1.4–2k | – |
| borrow | CERN EP-DT DRD1 GMS (DMT143 in stainless, Pi + Grafana, < 5 kCHF to build; one unit at the GDD): G. Rigoletti, O. Salomon, F. Brunbauer | 0 | – |
| 3: chilled mirror | Edgetech DewMaster $3.8–6.4k; Michell S8000 ~€15k; MBW 373 ~€30–45k (est.) | – | one unit, switched |
| not suitable | QCM (Michell QMA601), CRDS (Tiger HALO): trace ranges, 0.3–3 L/min sample | | |
| second opinion | used LI-COR LI-850 NDIR (0–60,000 ppm, $1.5k used) | needs its own calibration in Ar/iC₄H₁₀ | |

How to make the chips trustworthy (`research/B` §4):
1. Run all of them in series on the same gas and cross-calibrate their offsets.
2. Zero them on dry bottle gas (a few ppm).
3. **Test isobutane cross-sensitivity**: dry Ar 5.0 against dry Ar/iC₄H₁₀. Sensirion and Vaisala both warn that small
   hydrocarbons diffuse into the polymer; there is no published data for 10 % isobutane.
4. Anchor the span to the borrowed or bought reference at the outlet.

The chips report their own die temperature, so the conversion from RH to ppm (RH·e_s(T_die)/p) needs no separate
thermometer. Keep the cells warmer than the gas dew point (+18 °C at 20,000 ppm).

**Use one sensor per point, not one analyser switched between points.** The chain has no spare flow for a bypass, and
each switch has to re-equilibrate the walls, so a switched analyser cannot give 1/min. CERN also saw two DMT143s read
6,000–8,000 ppm for 2 h at 3 L/h on dry Ar before settling at 75 ppm. Expect hours of stabilisation at low flow.

**ppm-class dew-point transmitters (±2 °C) are only ±15–20 % of reading.** A chilled mirror is the only route below
~300 ppm at ≤ 10 %. We need that only if the tubing fix works and the water drops to ~100 ppm, which would make the v
correction small anyway.

### 3.3 Oxygen

| tier | hardware | price | caveat |
|---|---|---|---|
| **1: DIY galvanic cell** | AII GPR-12-333 (€275) or a Teledyne B-2C-class cell (€100–350); stainless low-volume flow cell (€150–300); transimpedance amp + 24-bit ADC + thermistor on the Pi (€100); 100–500 ppm O₂ span cylinder (~€250) | **~€0.8–1.2k** | Calibration is ours to validate. 12–24 months of life below 1000 ppm, shortened by air exposure. Needs a vent check valve or bubbler. |
| **1′: galvanic analyser** | Ntron Microx EC (€1.8k, 100 mL/min, RS232) or AII GPR-1500 (€2.35k, 0–10/100/1000 ppm, LDL 0.05 ppm) | ~€2–2.6k with span gas | US list prices; EU prices +10–30 % |
| intrinsically safe | Panametrics oxy.IQ (€3.6–4.4k, IS +$990), Systech EC92DIS (ATEX) | €4–8k | only if LNL safety requires IS equipment |
| reference | Teledyne 3000TA-XL, Systech EC900 (~€5–9k); PreSens Fibox 4 trace (0–200 ppm, LDL 0.5, no gas consumed; **cross-sensitive to organic vapour**, so test it in 10 % iC₄H₁₀) | €5–9k | |
| **out** | zirconia (Rapidox, Systech ZR800 / Senz-Tx, AMI 65, CERN DRD1 GMS): runs at ~700 °C, burns isobutane against the O₂ (10 % HC against 160 ppm O₂ reads ~0), cokes, and is an ignition source; coulometric Delta F (needs 0.5–1 L/min); Alphasense % cells (~5000 ppm zero offset) | | |

Galvanic cells read partial pressure and do not depend on flow, so they sit in-line at any flow. T2K's Micromegas TPC
(Ar/CF₄/iC₄H₁₀) used an electrochemical O₂ analyser for exactly this.

### 3.4 Gas pressure, flow, bottles

| item | price | note |
|---|---|---|
| BMP585 in each water cell (absolute p) | €16 | relative ±0.06 hPa; wetted gel/silicon, so isobutane long-term not verified and treated as replaceable |
| Sensirion SDP810-500Pa (chamber overpressure) | €26 | **20-week lead time listed: order early** |
| Keller PAA-33X 0.8–1.2 bar abs, RS-485 | quote, ~€0.7–1k (est.) | stainless; Tier 2 traceable absolute p |
| WIKA A-10 0–250 bar on each regulator HP port | €140–260 | consumption, bottle-change times, condensation check (§2) |
| rotameter + needle valve per chamber | €60–150 | sets flow, no readback (already in the budget's `gas` item) |
| digital mass-flow meter on the inlet **and** the exhaust (same model) | Sensirion SFC5500 €1.4k; Alicat M €1.2–1.6k, MC €1.95k (has an i-butane/Ar gas table) | the gas factor cancels in the ratio, so a few-% leak shows. One per chamber for all-digital: ~€7–9k (Tier 3) |
| exhaust oil bubbler | €50–150 | stops air back-diffusing, which would look like a leak |
| log bottle lot / certificate numbers and connect times | 0 | in the e-log |

### 3.5 Whole-gas analysers and monitor chambers

| item | price | verdict |
|---|---|---|
| **⁵⁵Fe gain monitor** (single-wire tube or small Micromegas on the exhaust, 5.9 keV peak every few minutes, Red Pitaya €420 as the MCA) | €0.5–1.5k (est.) | **Tier 2.** CERN's own method: it saw the 20 % gain loss from PU tube. Gain has no in-situ monitor at all otherwise. |
| two-source v monitor (GOOFIE / CMS VDC style: two ²⁴¹Am or ⁹⁰Sr sources at 10 and 40 mm, SiPM/PIN t₀) | €1.5–3k (est.) + source paperwork | Tier 3. 0.1–0.3 % per 10–30 min. The TPCs' own cathode edge already gives v to ~0.5 % for free. |
| SRS BGA244 speed-of-sound binary gas analyser (isobutane in its table, ±0.1 %) | ~€4.3k | Tier 3. Logs bottle steps and condensation drift directly. |
| NDIR hydrocarbon module (SGX IR12, Dynament) | €130–550 | cheap isobutane % (±2–5 % after self-calibration) and leak sniffer |
| GC: micro-GC €30–45k; used SRI 8610C ~€2k | | borrow only. Ar and O₂ co-elute, and a TCD can't see trace water, so it is good for the iC₄H₁₀ fraction and N₂ |
| RGA/QMS (SRS UGA €29.5k; Pfeiffer GSD 350, Hiden HPR-20, MKS, INFICON €35–60k est.) | | overkill. N₂ is buried under isobutane fragments, and H₂O is limited by the instrument's own water. |

Radioactive sources at LNL: from EU exemption values (recollection, check), ²⁴¹Am and ⁹⁰Sr above 10 kBq, or ⁵⁵Fe above
1 MBq, need LNL radioprotection paperwork. Start it early, or borrow sources there.

## 4. Readout architecture

```
 hall / chambers (near beam)                      counting room (outside shielding)
 ─────────────────────────────                     ──────────────────────────────────
 SHT+BMP gas cells ×5 ─┐                            Raspberry Pi 5 (read-only root, USB SSD,
 SDP810, Pt100/MAX31865┼─ PCA9615 diff. I²C ─CAT5──▶  watchdog, PoE)  ── chrony ◀── DAQ PC NTP
 DS18B20 (FEU crates)  ┘   (QwiicBus, ~30 m)          │ 10 s reads → 1-min means
 O₂ cell TIA + ADS1220 ──── same bus                  │ daily CSV (epoch + ISO UTC) ──rsync──▶ DAQ PC
 Yocto-Meteo ×2 ─────────── USB (≤5 m, or a hub)      │ optional InfluxDB + Grafana on the DAQ PC
 Keller / FA510 / WIKA ──── RS-485 Modbus (long runs) │ latest values → sidecar per acquisition tag
```

- **One daemon, one clock.** Python (`smbus2`, `yoctopuce`, `minimalmodbus`, `picosdk`) reads every 10 s and writes
  1-min means with raw readings and calibration constants. The CSV is the master copy; Grafana is only a view.
  chrony syncs to the DAQ PC, and its offset is logged as a channel. That meets the "one UTC clock" lesson of
  `ENVIRONMENT_SENSORS.md`.
- **Join to the data.** At each DREAM acquisition start, write the latest values into a sidecar keyed on the
  acquisition tag.
- **Radiation.** COTS SoCs crash under neutrons (Pi 3B+, Pi Zero 2W, [arXiv:2503.03722](https://arxiv.org/html/2503.03722v1)).
  Only €10–30 chips go near the beam; the Pi stays outside the shielding.
- **Hardware for the readout:** Pi 5 (€100) + PSU/case/SSD/PoE (~€80) + QwiicBus pairs (€13 each) + USB-RS485 (€30).
  That is **~€250** (included in Tier 1 below). A LabJack T7 ($570) is needed only for analogue transmitters.
- **Safety (ask LNL).** These are powered, non-ATEX sensors inside a flammable-gas line. The gas holds no O₂, so the
  hazard is leaks and the vent. LNL's rules decide whether intrinsically safe (IS) versions are needed.

## 5. Gas-system changes (not sensors, but they remove the cause)

| change | cost | why |
|---|---|---|
| Low-permeation lines (§8): aluminium-barrier composite (Synflex 1300 type) or copper; budget item `gaslines` | €0.25–0.7k for ~30 m + fittings | removes tube permeation (§2); LHC gas systems are all stainless; Belle fixed its water with copper |
| Parallel feeds, one needle valve + rotameter per chamber | in `gas` already | stops D collecting everyone's water; makes per-chamber sensors meaningful |
| 3A molecular-sieve trap at the inlet (Restek €250–360, Agilent CP17971 ~€300) | €0.25–0.4k | takes the bottle's water. **Not 13X or 5A, which adsorb isobutane.** It does nothing for water entering downstream. |
| Bottles kept indoors / warm | €0.1–0.5k | §2 condensation |
| High-barrier window metallisation | ask CEA | §2 |

## 6. Packages

| tier | contents | € (central, range) |
|---|---|---|
| **1: no-brainer** | Pi readout (€250); 2 × Yocto-Meteo (€130); 5 × SHT85 + BMP585 stainless cells (€0.6–0.9k); 4 × Pt100 + MAX31865 (€260); SDP810 (€26); 6 × DS18B20 (€30); 2 × WIKA A-10 (€0.3–0.5k); bubbler (€100) | **€1.9k (1.6–2.3k)** |
| **gas fixes** | low-permeation lines (€0.4k, separate budget item `gaslines`, §8), 3A trap, warm bottles (§5) | **€1.0k (0.6–1.6k)** |
| **2: recommended** | DIY galvanic O₂ cell + span gas (€0.8–1.2k) **or** GPR-1500 / Microx (€2–2.6k); water anchor FA510 (€1.4–2k, €0 if the CERN GMS is lent); 2 × digital flow meters, inlet and exhaust (€2.4–2.8k); ⁵⁵Fe gain monitor (€0.5–1.5k) | **€6.3k (3.7–8.9k)** |
| 3: upgrade | BGA244 (€4.3k); two-source v monitor (€1.5–3k); Keller PAA-33X (€0.7–1k); PT-104 + 1/10 DIN probes (€1.2k); per-chamber MFCs (+€4–6k) | +€12k (8–16k) |
| overkill | RGA/QMS, micro-GC, chilled mirror, CRDS | €4–60k each |

**Recommendation:** Tier 1, the gas fixes and Tier 2, **≈ €9.2k (central; 5.9–12.8k)**. Buy the long-lead items first:
the SDP810 (20 weeks), the span cylinder and the premix.

**Next steps:**
1. Ask the CERN EP-DT gas group (Rigoletti / Salomon / Brunbauer) to lend the DRD1 GMS. It will need its zirconia O₂
   sensor bypassed for isobutane.
2. (Parked until the gas is chosen, §7.4.) LNL rules for sensors in a flammable-gas line.
3. Ask CEA about the window metallisation; try `MaxRead` for the FEU temperatures (§7.2).
4. Recover the n_TOF flow CSVs from the DAQ PC and the tubing's plastic type (§7.1).
5. Bench-test 2 SHT85 cells and a GPR-12-333 on the bottle gas before the run: the isobutane cross-sensitivity tests.

## 7. Update 2026-11-17 (evening): Dylan's answers, the FEU manual, the n_TOF tubing

### 7.1 n_TOF plumbing as built (Dylan)

- Plastic tubing: **~5–10 m in and out**, plus **0.5 m plastic jumpers** daisy-chaining A → B → C → D. The plastic type is
  not known (ask whoever plumbed it: PU, nylon, PVC/Tygon or silicone).
- **The flow was logged at n_TOF**, so it can be recovered. Our own Bronkhorst two-MFC mixer (`nTof_x17_DAQ/gas_mixer_control/`,
  commissioned 2026-07-07) wrote per-day CSVs to `daq:~/beam_july/slow_control/gas_flow/`. Each row has measured flow,
  setpoint, valve output and **the MFC temperature (propar dde 142)**. The argon bottle pressure was read off photos of
  the gauge (`bottle_gauge_reader/`). The argon MFC was capped at 4.0 ln/h by the low supply pressure (~0.7 bar), so the
  chain flow was ≤ ~4.4 L/h at 90/10. The `daq` machine did not answer from here (timeout, 17 Nov). If the files still
  exist, they give the flow history and a gas-temperature proxy at the mixer. Both belong in the nTof_x17
  drift-velocity study (`rerun/ntof/vt/`). **(ask: is the DAQ PC still reachable, or did it go back to CEA with DREAM?)**

What the tubing can account for, using the measured ingress rates (§2) at a chain flow of 2–4.4 L/h:

| segment | PU (CERN rate) | polyolefin, 50 % RH (Belle rate) |
|---|---|---|
| 5–10 m inlet | 55–240 ppm | 70–310 ppm |
| each 0.5 m jumper | 5–12 ppm | 7–16 ppm |
| A → D (3 jumpers) | 16–36 ppm | 21–47 ppm |

**So PU or polyolefin tubing explains ≲ 300 ppm, and almost none of the A → D growth.** At n_TOF, water was inferred at
~2000 ppm (July), and D moved ~3× more than A. If those readings hold, most of the water enters *at the chambers*:
windows, frames and glue, FR4, O-rings, or the jumper connections (a leak would also bring O₂, which an O₂ cell can
separate, §3.3). There are two caveats:
- PVC/Tygon and silicone tubing are 10–100× more permeable than PU. If that is what was used, the tubing is back in
  play. Find out the plastic type first.
- The ~6 %/1000 ppm v sensitivity is inferred, not measured.

That makes the per-chamber water cells (§3.2) and the window-barrier follow-up the two most informative items.

### 7.2 FEU temperature: the FEUs do have sensors (check)

Dylan's note was that the front-end cards don't report temperature. **The CEA FEU User's Manual (CLAS12 MVT, I.
Mandjavidze, v0.0, 17 Dec 2022, [clonwiki](https://clonwiki0.jlab.org/wiki/clondocs/Docs/MVT_FEU_User_Manual.pdf)) says otherwise:**
- p. ~6: one JTAG chain allows "reading FPGA core and IO voltages and its temperature values" (the Virtex-6 die).
  A second chain "comprises a single MAX16031 system monitor chip. The power consumption of the module, various onboard
  generated voltages, the values of three temperature sensors are monitored by this chain."
- §3.2.2: the SlowControl register (0x200004) drives the ADC, the DREAM ASICs and the MAX16031.
- §5.1.15 `MaxRead 0xRegAdr`: reads a MAX16031 register over the UDP slow-control link. The temperature registers are
  in Maxim's MAX16031 datasheet.

Nothing in `nTof_x17_DAQ` calls `MaxRead`, so it was simply never read at n_TOF.

**How to use it (Dylan, 17 Nov):** poll `MaxRead` (and the FPGA temperature) for every FEU **between sub-runs**, when
the DAQ is idle and slow-control traffic can't disturb data taking. Log it under the sub-run tag.
- The boards run far above ambient, so these readings track the electronics' own state: power, cooling, a failed fan.
  They help with pedestal and noise drifts (the 23 July noise step could not be checked against temperature).
- They are no substitute for the gas and chamber thermometers. A cheap dedicated sensor stays in Tier 1 for that. What still needs checking:
- whether the MX17 FEU firmware answers `MaxRead` (this manual is the CLAS12 version);
- whether the DREAM DAQ software can send it while running.

The detector-side M1 cards have no sensor. **Plan:** try `MaxRead` on the bench with CEA's DAQ. If it works, log three
board temperatures plus the FPGA temperature per FEU for free. Keep the DS18B20s (€30) as the fallback.

### 7.3 Window barrier: follow-up (open)

The aluminised-mylar WVTR (§2), and whether the window–cathode gap is flushed, is a separate follow-up. To-do items:
- the supplier's WVTR or optical density for the film;
- a bench measurement: one chamber, metal lines, an SHT85 cell before and after it, at a known flow and hall humidity.
  This is the same set-up as the Tier 1 bench test (§6, step 5).

### 7.4 Gas not decided: keep the plan gas-agnostic

LNL safety and flammability are parked until the gas is chosen. What changes with the gas:
- **CO₂ mixtures (Ar/CO₂, Ar/CF₄/CO₂ …): standard galvanic O₂ cells have a KOH electrolyte, which CO₂ above ~0.5 %
  neutralises.** Use the CO₂-tolerant variant (AII XLT-12-333 class, `research/C` §2) and confirm with the vendor.
- The 3A dryer is fine for argon, isobutane and CF₄. For CO₂, check the vendor's data before relying on it: CO₂
  (3.3 Å) is mostly excluded by 3A, but not completely.
- The SHT chips' cross-sensitivity test (§3.2) has to be redone in whatever gas is chosen.
- The bottle condensation point (§2) applies only to hydrocarbon premixes.
- The BGA244 handles any binary mixture.
- A non-flammable mixture removes the IS question entirely.

### 7.5 A, C and D compared: where in the chain the water enters

The tubing at n_TOF was the standard CERN yellow and blue pneumatic tube. Dylan guesses it is the same Festo-type PU
that CERN tested in [arXiv:2202.12007](https://arxiv.org/abs/2202.12007); assumed so here.

**Method.** If the water comes in through the walls, every source scales with the outdoor water vapour. Each chamber's
v swing is then proportional to the water accumulated up to that chamber. The ratio of swings depends only on *where*
the water enters, not on the permeability or the flow. The observed ratios are C 3.0× A and D 2.9× A
(`nTof_x17/rerun/ntof/vt/README.md`, shared-curve model). B has no v measurement. `estimates.py` (`chain_ratios`):

| model | B / A | C / A | D / A |
|---|---|---|---|
| **observed** | – | **3.0** | **2.9** |
| tubing only, same plastic everywhere, inlet 5 m + 0.5 m jumpers | 1.10 | 1.20 | 1.30 |
| tubing only, inlet 10 m + 0.5 m jumpers | 1.05 | 1.10 | 1.15 |
| equal source in every chamber, nothing from the inlet | 2.00 | 3.00 | 4.00 |
| equal source per chamber, inlet = ½ a chamber | 1.67 | 2.33 | 3.00 |
| equal source per chamber, inlet = 1 chamber | 1.50 | 2.00 | 2.50 |

What the table says:
- **Tubing cannot produce the chain ratios.** With the same plastic throughout, the swing grows by at most 10 % per
  0.5 m jumper: C/A ≤ 1.2 and D/A ≤ 1.3, against 3.0 and 2.9 observed. This holds for any permeability and any flow.
  The size argument of §7.1 (≲ 300 ppm from the tubing) points the same way.
- **The water enters in the chambers, and A's swing is mostly A's own.** C = 3.0 needs almost nothing from the inlet
  (inlet ≈ 0), so even the 5–10 m inlet line contributed little.
- **No single equal-source model fits both C and D.** C fits "inlet ≈ 0", which predicts D = 4.0. D fits "inlet ≈ ½ a
  chamber", which predicts C = 2.3. So either C lets in more water than the others, or D lets in less, or D's swing is
  under-measured. D's own v is the weakest of the three (15–45 clean tracks per acquisition, ±3.3 % per sub-run), so
  the last option is quite possible.
- **Caveats.** The model assumes v responds linearly and identically to water in every chamber (same gas, same
  233 V/cm), and that the temperature part of the swing is common to all of them. Both are untested. Temperature
  shared equally would pull every ratio towards 1, so the true water ratios would be larger still.

**What would settle it:** the Tier 1 SHT85 cells, one after each chamber. They measure these ratios directly in ppm,
chamber by chamber. If one chamber stands out, open that one. Whether the source is the windows, the frames and glue,
the FR4, the O-rings or the fittings is a follow-up. It is also hard: the front window has to stay thin for the
material budget (§7.3).

## 8. Better tubing: options and cost (2026-11-17)

Dylan's suggestion: the black tubing that is aluminium wrapped in plastic. That is **aluminium-barrier composite tube**,
the Eaton/Danfoss **Synflex 1300** class (Dekabon is the older name). The Campbell Scientific listing of the same tube
describes its construction as "overlapped aluminum tape, and ethylene copolymer liner. The aluminum layer limits
diffusion of gases through the wall of the tube"
([Campbell Sci 15702](https://campbellsci.com/products/15702); [Danfoss 1300 series](https://powersource.danfoss.com/products/hoses-and-fittings/hydraulic-hose-and-fittings/thermoplastic-hydraulic-hose-and-fittings/thermoplastic-hydraulic-hose/p/1300-04403)).
Gas analysers and weather-station sampling lines use it for exactly this reason. It is flexible, so it can run up to
the arms.

| tubing (≈ 6 mm / ¼″ OD) | water through the wall | €/m | fittings | ~30 m + ~30 fittings |
|---|---|---|---|---|
| PU (as at n_TOF, assumed) | ~15–16 ppm/m at 3–5 L/h (CERN, measured) | ~1–2 (est.) | push-in | – (the baseline) |
| PE / polyolefin | ~60 ppm·(L/h)/m at 50 % RH (Belle); "practically no" permeation in an ASTM comparison ([JTE](https://store.astm.org/jte103318.html)). The two disagree. | ~1–2 (est.) | push-in | – |
| **Synflex 1300 aluminium-barrier composite** | aluminium tape barrier, so very low. The overlapped seam and the ends are the only paths; no ppm/m figure found (ask, or measure) | **~€2.7** ($0.94/ft list, [Motion](https://www.motion.com/products/sku/06328680); 75 m coils [Flowtech UK](https://punchout.flowtech.co.uk/category/section-12-hose-tubing-couplings/eaton-synflex-pneumatic-tubing/imperial-eaton-synflex/75-metre-coils)) | brass compression with a tube insert, ~€5–10 (est.) | **€0.25–0.4k** |
| PFA (Versilon, Parker) | low, but some PFA tubes are sold as *moisture-diffusing* ([McMaster](https://www.mcmaster.com/products/moisture-diffusing-tubing)), so check the grade | £8.7–20.7/m ≈ €10–24 ([Tubing Intl](https://www.tubinginternational.com/product/versilon-pfa-tubing/), [RS](https://uk.rs-online.com/web/p/hose-pipe-flexible-tubes/1581901)) | PFA/PTFE or Swagelok | €0.5–1k |
| annealed copper | 0 | €3–6 | brass compression, €5–10 | €0.3–0.5k |
| stainless (electropolished optional) | 0, and the cleanest | €8–15 (est.) | Swagelok, €25–40 each | €1–1.6k |

- **Recommendation:** use **Synflex-type composite for everything near the arms** (it is flexible, cheap and has a metal
  barrier), **copper for the long fixed runs** if they are routed along walls, and short PFA jumpers only where a
  flexible clear tube is needed. Budget item `gaslines`, centred on Synflex + copper: **€0.4k (0.25–0.7k)**.
- **Feed the chambers in parallel.** That needs a small manifold (4 needle valves + rotameters, already in the budget's
  `gas` item) and about 4 × 2 m of line instead of 3 × 0.5 m. It is included in the ~30 m.
- **Verification is cheap:** run the same Tier 1 SHT85 cell before and after a 10 m coil of each candidate at 2 L/h,
  for a day in the lab.
- **The lines are probably not the main source.** By §7.5 most of the n_TOF water entered at the chambers. Better
  tubing is cheap insurance and removes one variable, but don't expect it alone to remove the drift.
