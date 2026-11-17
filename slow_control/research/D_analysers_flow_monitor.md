# Research notes D: composition analysers, monitor chambers, flow, bottles, line materials, dryers (2026-11-17)

Web research (agent report, lightly edited). €: $1 ≈ €0.87, £1 ≈ €1.15. **(est.)** = quote-only, estimated.
Synthesis: `../SENSOR_OPTIONS.md`.

## 0. Two findings that set the priorities

1. **CERN measured water ingress through PU tubing at our flows.** Guida, Mandelli, Corbetta, Mari: 6 mm Festo PU in front
   of a single-wire proportional chamber added **+16 ppm H₂O/m and +1 ppm O₂/m at 3 L/h** (+15 / +0.8 at 5 L/h); 12 m
   of tube dropped the gain by up to **20 %** ([arXiv:2202.12007](https://arxiv.org/abs/2202.12007)). Permeated water
   enters at a fixed rate, so ppm ∝ 1/flow: at 0.5–2.5 L/h it is ~20–100 ppm per metre, and in a series chain D collects
   every metre upstream. Estimate (not from a source): the 60 µm aluminised-mylar windows may matter as much — see
   `../SENSOR_OPTIONS.md` §2.
2. **A cold Ar/iC₄H₁₀ bottle can condense isobutane.** p_vap(iC₄H₁₀) ≈ 3.0 bar at 20 °C, 1.6 bar at 0 °C
   ([NIST](https://webbook.nist.gov/cgi/cbook.cgi?ID=C75285)). A 10 % mixture reaches its dew point at ~30 bar (20 °C) /
   ~16 bar (0 °C); 5 % at twice that. Composition then drifts with bottle temperature and fill level. Ask the supplier
   for fill pressure and certified tolerance; keep bottles warm. Premix tolerance: certified ±2 % rel, gravimetric ±1 % rel
   ([Matheson](https://www.mathesongas.com/pdfs/litcenter/Mixture-Grades.pdf),
   [BOC](https://help.boconline.co.uk/kb/guide/en/speciality-products-technical-information-hm1TG3nzyG/Steps/4097199,4097325)):
   ±2 % rel of 10 % iC₄H₁₀ moves v by ≪ 1 %, so bottle-to-bottle variation cannot explain 15 %.

## 1. Full-composition analysers

### 1a. RGA / QMS with atmospheric inlet

| Instrument | Price | Notes |
|---|---|---|
| SRS UGA100 (complete 1 bar sampler) | $33,950 ≈ €29.5k (UGA from $31.5k, ULT from $28k) | [catalogue](https://xdevs.com/doc/Stanford_Research_Systems/www.thinksrs.com-UGAc.pdf), [UGA](https://thinksrs.com/products/uga.html) |
| SRS RGA100 head only | from $4,950 | + turbo, capillary inlet, heater: +€8–15k (est.) ([SRS](https://www.thinksrs.com/products/RGA.htm)) |
| Pfeiffer OmniStar/ThermoStar GSD 350 | quote; €35–50k (est.) | [Pfeiffer](https://www.pfeiffer-vacuum.com/us/en/product/omnistar-thermostar-gsd-350.html) |
| Hiden HPR-20 | quote; €40–60k (est.) | capillary 1–15 mL/min ([Hiden](https://www.hidenanalytical.com/products/gas-analysis/hpr-20-epic/)) |
| MKS Cirrus, INFICON Transpector CPM | quote; €35–60k (est.); used €5–15k (est.) | [used example](https://americanlaboratorytrading.com/lab-equipment-products/pfeiffer-vacuum-thermostar-gsd-301-t3-benchtop-mass-spectrometer-6544/) |

In Ar/iC₄H₁₀ (isobutane base peak m/z 43, [spectrum](https://docbrown.info/page06/spectra2/2-methylpropane-ms.htm)):
O₂ at m/z 32 clean to ~1–10 ppm; H₂O at 18 limited by the instrument's own water (tens of ppm); N₂ at 28 buried under
C₂H₄⁺/C₂H₅⁺ fragments; isobutane fraction from 43/40 to ~1 % rel. Consumes 0.06–0.9 L/h. **Overkill.**

### 1b. Gas chromatographs

CERN: every LHC gas system has an analysis module — stream selection, automated O₂ + H₂O analysers, and GCs for mixture
stability and complex impurities; also single-wire chambers as performance monitors
([Guida 2016](https://indico.cern.ch/event/568177/contributions/2312543/attachments/1368013/2073300/The_gas_systems_for_LHC_experiments-RGuida_v1.pdf);
[Capeans/Guida/Mandelli](https://indico.ihep.ac.cn/event/6387/contributions/83702/attachments/43536/50137/PosterTIPP_BMandelli.pdf)).

| GC | Price |
|---|---|
| Agilent 990 Micro GC | £36,846 ≈ €42k ([Wolf Labs](https://wolflabs.co.uk/laboratory-equipment/micro-gas-analysers/990-micro-gc/10447515)) |
| INFICON Micro GC Fusion | quote/rental; €30–45k (est.) |
| SRI 8610C | used £1,540 (PID) – $2,295 (FID) ([Unigreen](https://shop.unigreenscheme.co.uk/chromatography/gas-chromatography-gc/gas-chromatography-gc-systems/sri-8610c-gas-chromatograph), [eBay](https://www.ebay.de/itm/236200553479)); new TCD €8–12k (est.) |

Catch: Ar and O₂ co-elute on mol-sieve at room temperature; TCD cannot see trace water. A GC gives the isobutane fraction
(~0.1 % rel) and N₂ as air marker (~10 ppm with HID). **Borrow only.**

### 1c. Isobutane-fraction (binary gas) sensors

- **SRS BGA244 (speed of sound): from $4,950 ≈ €4.3k** ([SRS](https://www.thinksrs.com/products/bga244.html)); isobutane is
  in its gas table ([app note](https://thinksrs.com/downloads/pdfs/applicationnotes/BGA244%20Creating%20User%20Defined%20Gases.pdf));
  ±0.1 % typical, 0–5000 sccm, USB/RS-232. Water is a third component (small bias). Put it on D's exhaust.
- Thermal conductivity: Hitech K1550 quote (€3–5k est.,
  [datasheet](https://pdf.directindustry.com/pdf/hitech-instruments/thermal-conductivity-gas-analyser-in-situ-meter-panel-mounted-measuring-hydrogen-carbon-dioxide-co2-argon-k1550/61075-615256.html));
  Michell XTC501 from $5,275.
- NDIR hydrocarbon modules: SGX IR12 0–100 % ~$154 ([DigiKey](https://www.digikey.at/en/product-highlight/s/sgx-sensortech/ir1-series-single-gas-sensors)),
  Dynament Platinum from £135 ([Omega](https://www.dwyeromega.com/en-gb/platinum-series-infrared-gas-sensors-hydrocarbon-co-detection/p/Platinum-Series-Hydrocarbon-Sensor)).
  Methane-calibrated: calibrate on our bottles (~2–5 % rel). Also a leak sniffer.

## 2. Gas monitor chambers

| System | Principle | Performance |
|---|---|---|
| GOOFIE (NA45/CERES, ALICE TPC/TRD) | two ²⁴¹Am sources at two drift distances, ≤ 700 V/cm; Δt → v, pulse height → gain | ~0.1 % ([STAR FTPC](https://www.star.bnl.gov/public/ftpc/Documentation/Obsolete/DriftVelocityMonitor/development.html); [arXiv:0802.1443](https://arxiv.org/abs/0802.1443); [arXiv:1709.02743](https://arxiv.org/abs/1709.02743)); ALICE with laser 2×10⁻⁴ ([arXiv:0809.5133](https://arxiv.org/abs/0809.5133)) |
| CMS DT VDC (Aachen) | 1 L drift cell, two e⁻ beams 4.8 cm apart, sci-fibre + 2 SiPM trigger | 54.8 ± 0.1 µm/ns (~0.2 %) every ~10 min ([arXiv:1107.0358](https://arxiv.org/abs/1107.0358)); saw sub-% shift on going open-loop ([arXiv:2309.05466](https://arxiv.org/abs/2309.05466)) |
| T2K ND280 GMC | inlet + outlet gas; two ⁹⁰Sr sources with fibre timing (v), ⁵⁵Fe (gain); every 30 min; Ar/CF₄/iC₄H₁₀ 95/3/2 | [RD51 2016](https://indico.cern.ch/event/532518/contributions/2184422/attachments/1286996/1914909/20160608.RD51.pdf) |

Compact design for us: 30–50 mm drift cell on D's exhaust; two collimated ²⁴¹Am at 10 and 40 mm with Si PIN or
scintillator + SiPM for t₀ (or two ⁹⁰Sr + SiPM); charge preamp → **Red Pitaya STEMlab 125-14, €415–430**
([RS](https://nl.rs-online.com/web/p/oscilloscopes/1271086)). 0.1–0.3 % per 10–30 min; build €1.5–3k (est.). CAEN DT5720
(€6–8k est.) not needed. Sources: ⁵⁵Fe 3.7 MBq $380 ([3B](https://3bscientific.com/bz/fe-55lds100-radioactive-source-u41537-spectrum-techniques-fe-55lds100,p_666_1747.html));
Am/Sr buttons €150–400 (est.). EU exemption (2013/59/Euratom, recollection): ²⁴¹Am, ⁹⁰Sr 10 kBq; ⁵⁵Fe 1 MBq — above
that, LNL radioprotection paperwork.

**⁵⁵Fe gain monitor on the exhaust** (single-wire tube or small MM, 5.9 keV peak every few min, T/p corrected): exactly
CERN's SWPC method; €0.5–1.5k (est.). Free cross-check: each TPC's max-drift-time edge (cathode at 30 mm) gives v at ~0.5 %.

## 3. Flow (0.5–3 L/h ≈ 8–50 sccm)

| Device | Price | Fit |
|---|---|---|
| Sensirion SFC5500 (50 sccm version exists) | €1,383 ex VAT ([RS](https://befr.rs-online.com/web/p/flow-controllers/2211595)); £1,110 ([Farnell](https://uk.farnell.com/sensirion/sfc5500-2slm/flow-controller-145-psi-digital/dp/3972512)) | good |
| Sensirion SFC6000D | $300–450 ([IBS](https://www.ibselectronics.com/part/sensirion/sfc6000d-5slm/2027880/)) | 5 slm minimum range: too coarse |
| Alicat MC 1 sccm / M meters | $2,245 ≈ €1.95k ([Alicat](https://store.alicat.com/products/mc-1sccm-d)); M $1,390–1,845 ([Instrumart](https://www.instrumart.com/products/all-part-numbers/48460)) | i-butane + Ar in Gas Select, mixtures via COMPOSER ([list](https://www.alicat.com/knowledge-base/gas-select-gas-list/)) |
| Bronkhorst EL-FLOW, Brooks, MKS, Vögtlin red-y | quote; €1.5–3k (est.); Vögtlin €0.8–1.2k (est.) | equivalent |
| Rotameter + needle valve | €60–150 | no readback |

ATEX: Alicat (Class I Div 2) and Bronkhorst (zone 2) sell certified versions (ask). Same-model meter on inlet and exhaust:
the gas factor cancels, a few-% leak shows. Oil bubbler on exhaust (€50–150), a few mbar overpressure (CMS DT: 2–10 mbar).
**Parallel feeds, one meter per chamber.**

## 4. Bottle pressure

WIKA A-10 0–250 bar, €138–261 (4–20 mA €260.67 ex VAT) ([RS](https://ie.rs-online.com/web/p/pressure-sensors/7255951),
[4–20 mA](https://ie.rs-online.com/web/p/pressure-sensors/2218286)), on the regulator HP port, logged with bottle-store
temperature: consumption, bottle-change times, and whether a 90/10 bottle is in its condensation region. Log lot numbers.

## 5. Line materials

PU: ~15 ppm H₂O/m, ~1 ppm O₂/m at 3–5 L/h ([arXiv:2202.12007](https://arxiv.org/abs/2202.12007)). CERN gas group
outgassing table: PUR "bad", Rilsan "OK" but water <100 ppm still seen
([CERN](https://detector-gas-systems.web.cern.ch/Equipment/outgassing.htm), via search snippet). Belle RPCs fixed water
with copper lines ([Lu & McDonald 2007](https://project-cms-rpc-endcap.web.cern.ch/RPC/Chambers/OtherEXP/Belle/HumidityTest-10022007.pdf));
LHC systems are almost all stainless. Water permeability, worst → best (handbook ranking, not verified line by line):
PU > nylon PA6/PA11 > PE ≈ PTFE (porous grades high for O₂) > PFA/FEP/PEEK > metal (≈ 0).

Cost: 6 mm annealed Cu ~€3–6/m ([Climaled 1/4" 50 m €158](https://climaled.fr/en/insulated-copper-refrigerant-roll-1-4-installation-air-conditioner-heat-pump-r32-r410-r134-r410a-r134a-r290-50mt));
SS 1/4" €8–15/m (est.); Swagelok SS-400-6 ~$11 surplus ([eBay](https://www.ebay.com/itm/267029679211)) / €25–40 new
(est.); brass €5–10. ~30 m + 30 fittings: €0.3–1.2k. Flexible jumpers in PFA/FEP, < 0.5 m.

## 6. Dryers / purifiers

- **3A molecular sieve** (3 Å pores) takes water and excludes isobutane (5.3 Å) and O₂
  ([pores](https://www.chem.rochester.edu/notvoodoo/pages/reagents/molecular_sieves.php),
  [kinetic diameters](https://pmc.ncbi.nlm.nih.gov/articles/PMC5724681)). **Avoid 13X and 5A**: they adsorb isobutane.
- Restek moisture traps €247–360 ([Avantor](https://www.avantorsciences.com/export/en/product/20614357/high-capacity-moisture-traps),
  [VWR](https://b2b-nl.vwr.com/store/product/17246332/null)) — check packing is 3A/4A; Agilent Gas Clean CP17971 $221–391
  ([Agilent](https://agilent.com/store/en_US/Prod-CP17971/CP17971)); Entegris GateKeeper / Messer Oxisorb quote, €0.7–2k (est.).
  O₂ catalysts/getters: confirm hydrocarbon rating (ask).
- A dryer only removes bottle/supply water: place it just before the first chamber, metal from there on.

## 7. Verdicts (agent's)

| Item | Category | € |
|---|---|---|
| Cu/SS lines + parallel feeds | worth it | 0.3–1.2k |
| Flow meter per chamber + exhaust | worth it | 7–9k all digital; ~3.5k rotameters + 2 digital |
| 2 × WIKA A-10 + lot log | worth it | 0.3–0.6k |
| 3A trap at inlet | worth it | 0.25–0.4k |
| Exhaust bubbler | worth it | 0.05–0.15k |
| ⁵⁵Fe gain monitor + Red Pitaya | worth it | 0.5–1.5k |
| Warm bottles | worth it | 0.1–0.5k |
| SRS BGA244 | nice, strong value | ~4.3k |
| Two-source v monitor | nice | 1.5–3k |
| NDIR HC module | nice, cheap | 0.15–0.5k |
| Used/borrowed GC | only if free | 0–2k |
| New micro GC | overkill | 30–45k |
| RGA/QMS system | overkill | 24–60k |
