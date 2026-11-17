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
6. **Recommended package: Tier 1 + gas fixes + Tier 2 ≈ €9.5k (6–13k)** (§6). Tier 1 alone is the floor.

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
- **n_TOF's tubing material, lengths and flow were not recorded (ask).** That gap is why this stays a hypothesis.
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
| DS18B20 (1-Wire) | ±0.5 K | ~€5 | one per FEU crate. Ask CEA first whether the FEUs report their own temperature |
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
| Copper (€3–6/m) or stainless (€8–15/m) lines, brass/Swagelok fittings; PFA/FEP jumpers < 0.5 m | €0.3–1.2k for ~30 m + 30 fittings | removes tube permeation (§2); LHC gas systems are all stainless; Belle fixed its water with copper |
| Parallel feeds, one needle valve + rotameter per chamber | in `gas` already | stops D collecting everyone's water; makes per-chamber sensors meaningful |
| 3A molecular-sieve trap at the inlet (Restek €250–360, Agilent CP17971 ~€300) | €0.25–0.4k | takes the bottle's water. **Not 13X or 5A, which adsorb isobutane.** It does nothing for water entering downstream. |
| Bottles kept indoors / warm | €0.1–0.5k | §2 condensation |
| High-barrier window metallisation | ask CEA | §2 |

## 6. Packages

| tier | contents | € (central, range) |
|---|---|---|
| **1: no-brainer** | Pi readout (€250); 2 × Yocto-Meteo (€130); 5 × SHT85 + BMP585 stainless cells (€0.6–0.9k); 4 × Pt100 + MAX31865 (€260); SDP810 (€26); 6 × DS18B20 (€30); 2 × WIKA A-10 (€0.3–0.5k); bubbler (€100) | **€1.9k (1.6–2.3k)** |
| **gas fixes** | metal lines, 3A trap, warm bottles (§5) | **€1.3k (0.7–2.1k)** |
| **2: recommended** | DIY galvanic O₂ cell + span gas (€0.8–1.2k) **or** GPR-1500 / Microx (€2–2.6k); water anchor FA510 (€1.4–2k, €0 if the CERN GMS is lent); 2 × digital flow meters, inlet and exhaust (€2.4–2.8k); ⁵⁵Fe gain monitor (€0.5–1.5k) | **€6.3k (3.7–8.9k)** |
| 3: upgrade | BGA244 (€4.3k); two-source v monitor (€1.5–3k); Keller PAA-33X (€0.7–1k); PT-104 + 1/10 DIN probes (€1.2k); per-chamber MFCs (+€4–6k) | +€12k (8–16k) |
| overkill | RGA/QMS, micro-GC, chilled mirror, CRDS | €4–60k each |

**Recommendation:** Tier 1, the gas fixes and Tier 2, **≈ €9.5k (central; 6.0–13.3k)**. Buy the long-lead items first:
the SDP810 (20 weeks), the span cylinder and the premix.

**Next steps:**
1. Ask the CERN EP-DT gas group (Rigoletti / Salomon / Brunbauer) to lend the DRD1 GMS. It will need its zirconia O₂
   sensor bypassed for isobutane.
2. Ask LNL about flammable-gas and intrinsic-safety rules for sensors in the line.
3. Ask CEA about FEU temperature readback and window metallisation.
4. Recover n_TOF's tubing material, lengths and flow.
5. Bench-test 2 SHT85 cells and a GPR-12-333 on the bottle gas before the run: the isobutane cross-sensitivity tests.
