# Research notes C: trace O₂ in the chamber gas (2026-11-17)

Web research (agent report, lightly edited). US list prices × 0.87, ex VAT; EU prices typically 10–30 % higher.
"quote-only" = no public price; the figure is an estimate. Synthesis: `../SENSOR_OPTIONS.md`.

**Bottom line:** a galvanic (electrochemical) trace cell in-line at the chain outlet. It is passive, flow-independent and
hydrocarbon-rated. Zirconia is out. Coulometric and most bench analysers want 0.5–1 L/min (bypass pump + dumped gas).
Optical trace sensors work in principle but have a documented organic-vapour cross-sensitivity.

## 1. Flow decides most of it (chain: 33–170 mL/min)

- **Galvanic** cells read O₂ partial pressure through a membrane: flow only sets response (2–5 mL cell at 50 mL/min → τ ≈ 3–6 s).
- **Coulometric** (Delta F / Servomex DF) measure O₂ flux: regulated 0.5–1 L/min ([DF-310E manual](https://www.servomex.com/wp-content/uploads/2023/01/DF-310E-Manual_02172017.pdf)).
- **Zirconia / Rapidox** pump ~1 L/min ([Rapidox 3100](https://cambridge-sensotec.co.uk/product/rapidox-3100-multigas-analyser)).
- At ppm level a bypass pump is itself a leak source. Back-diffusion from the vent looks like a leak: bubbler or several
  metres of 1/8″ tube after the sensor. All-metal fittings, no plastic between chambers and sensor.

## 2. Options

| Option | Principle | Range / LDL | Flow | Hydrocarbons | Life | Interface | Price |
|---|---|---|---|---|---|---|---|
| **DIY: AII GPR-12-333 cell** | galvanic | 0–10 ppm … 1 %; LDL 0.05 ppm (in the GPR-1500) | any, in-line | hydrocarbon streams listed | 24 mo < 1000 ppm ([PST](https://www.processsensing.com/en-us/sensors/GPR-12-333.htm), [manual](https://manualmachine.com/analyticalindustriesincaii/gpr1500ais/6557838-operating-manual)) | current (≈3–4.5 nA/ppm) → own TIA + ADC | **$315 ≈ €275** ([Instrumart](https://www.instrumart.com/products/46233)) |
| DIY: Teledyne B-2C | galvanic micro-fuel | 0–10 ppm (B-2CXL 0–1 ppm) | any | "inert gas and hydrocarbon streams" ([Teledyne](https://teledyne-ai.com/en-us/products/oxygen-sensors)) | 6-mo warranty | current | quote, ~€250–350; compatibles AST SRX-MT22 $117 ([OxyCheq](https://www.oxycheq.com/products/ast-srx-mt22-ppm-o2-sensor)), Maxtec $225 ([Maxtec](https://shop.maxtec.com/compatible-oxygen-sensor/b2c/teledyne/r109p02/)) |
| Alphasense O2-A2 / LFO2-AH | galvanic % level | zero offset ≈ 5000 ppm equiv. ([Alphasense](https://www.alphasense.com/products/view-by-target-gas/lfo2-ah-lead-free-oxygen-sensor)) | — | — | 2 yr | — | €50–100; **not usable at ppm** |
| **Ntron Microx (EC option)** | galvanic | 0–10 ppm min range | 100 mL/min | EC option for HC backgrounds | cell swap | 4–20 mA, RS232, relays | **$2,091 ≈ €1.8k** ([Instrumart](https://www.instrumart.com/products/47017/ntron-microx-oxygen-analyzer)) |
| AII GPR-1500 | galvanic | 0–10/100/1000 ppm, LDL 0.05 | 1–2 SCFH rec., "not flow sensitive" | inert, HC, H₂, CO₂ | ~24 mo; cell $315 | 0–1 V, 4–20 mA | **$2,700 ≈ €2.35k** ([Instrumart](https://www.instrumart.com/products/46233)) |
| Panametrics oxy.IQ | galvanic 2-wire transmitter | 0–10 … 0–1000 ppm | 500 cc/min rec. | "unaffected by hydrocarbons"; IS option | cell $450 | 4–20 mA | $4,170–5,018 ≈ €3.6–4.4k; IS +$990 ([Instrumart](https://www.instrumart.com/products/39384/ge-panametrics-oxyiq-oxygen-transmitter), [datasheet](https://instrumart.com/assets/Oxy-IQ-Datasheet.pdf)) |
| Systech EC900 / EC92DIS | galvanic | ppm | ~140–150 mL/min, own pump | HC/combustibles; EC92DIS ATEX ([brochure](https://www.terrauniversal.com/media/asset-library/S/y/Systech-illinois-EC900-Series-Process-Oxygen-Analyzers-Product-Line-Brochure.pdf)) | cell | 4–20 mA, RS | quote, ~€5–8k |
| Teledyne 3000TA / -XL | micro-fuel (InstaTrace) | low ppm; XL 0–1 ppm | ~0.5–1 L/min (check) | HC-rated | 6–12 mo | 4–20 mA, RS232 | quote, ~€6–9k ([Chromservis](https://www.chromservis.eu/en/trace-oxygen-analyzer-model-3000ta-ce-marked-with-instatrace-sensor)) |
| Southland OMD-640/507/580 | galvanic portable | 0–1000 ppm, USB log | — | — | — | USB | OMD-580 $3,000 new; used OMD-507 $500 ([reach.dog](https://reach.dog/shop/buysso2com/products/omd-580-portable-ppm-oxygen-analyzer)) |
| Delta F DF-310E | coulometric | LDL ~1 ppm | 0.5–1 L/min | HC OK; acid gases attack | electrolyte | analog, RS | new ~€8–12k; used $400–470 ([eBay](https://www.ebay.com/itm/295217504110)) |
| Used galvanic analysers | — | — | — | — | cell usually dead: budget a new one | — | AMI 1000RS $2,975 ([eBay](https://www.ebay.com/p/5048915732)); AOI 3000 $2,120 ([eBay](https://ebay.com/itm/285849594316)) |
| PreSens Fibox 4 trace + SP-PSt9 | luminescence | 0–200 ppm, LDL 0.5, ±2 ppm/±5 %, t90 < 3 s | any (spot in flow cell) | **cross-sensitive to "organic vapour"** ([PreSens](https://www.presens.de/products/detail/ultra-trace-oxygen-sensor-spot-sp-pst9)) — test in 10 % iC₄H₁₀ | consumes no O₂ | USB/RS485; OXYPro UT 4–20 mA ([link](https://www.presens.de/products/detail/ultra-trace-oxygen-probe-oxypro-ut)) | quote, ~€5–8k + €300–600/spot |
| PyroScience FireSting trace | luminescence | "trace" is 0–10 % class | — | — | — | USB | ~€2–3k; too coarse |
| Zirconia (Rapidox, ZR800, AMI 65, SST, 3000ZA) | ~700 °C solid electrolyte | — | 0.1–1 L/min | **unusable** (§3) | — | — | — |

## 3. Why not zirconia with isobutane

"The gas to be measured must not contain combustible gases" ([Industrial Physics](https://industrialphysics.com/knowledgebase/articles/zirconia-oxygen-analysis/),
[ZR800](https://industrialphysics.com/product/oxygen-analyzer-zr800-and-sensor/)). The hot Pt electrode burns the
hydrocarbon with the available O₂ ([SST](https://sstsensing.com/?p=2669); Rapidox: VOCs "burn on the hot surface… all
the oxygen locally consumed", [Cambridge Sensotec](https://cambridge-sensotec.co.uk/gas-analysis-help/troubleshooting/rapidox-2100/)):
with 10 % iC₄H₁₀ vs 160 ppm O₂ the reading is near zero / meaningless. Also coking, and an ignition source (~700 °C vs
isobutane autoignition 460 °C, LEL 1.8 %, [Air Liquide](https://encyclopedia.airliquide.com/isobutane)). **CERN's DRD1
open-source gas monitor uses a Systech Senz-Tx zirconia and says it "is not compatible with flammable gases"**
([report](https://repository.cern/records/abnr5-8s651/files/Summer_Project_Report.pdf)): don't copy it for Ar/iC₄H₁₀.

## 4. Galvanic cells with isobutane

- Isobutane is not electroactive at room temperature; Teledyne, AII, Panametrics, Systech, Ntron list HC backgrounds.
- Interferences: acid gases (CO₂, H₂S, SO₂) neutralise KOH — none here unless the mixture changes; condensed HC liquid
  blocks the membrane ([PST](https://www.processsensing.com/en-us/blog/Hydrocarbon-liquids-affecting-Aii-Galvanic-Oxygen-sensors-What-is-the-effect-and-how-to-avoid-it.htm)) — not at 0.1 bar partial pressure.
- Life ∝ integrated O₂: 12–24 months < 1000 ppm. Air exposure shortens it and needs hours to recover. Keep capped/purged.
- Calibration: zero with purified Ar; span 100–500 ppm O₂ in Ar/N₂ (small cylinder, SIAD/Sapio, ~€200–400 est.). Reads
  partial pressure: log p and T (uncompensated cells ~2–3 %/°C).
- Accuracy ~±1 ppm + 2–5 % of reading; plumbing tightness limits first.
- Electronics are not ATEX unless an IS version (oxy.IQ IS, GPR-1500 IS, EC92DIS).

## 5. What others use

- CERN LHC: standard analysis racks for O₂ and H₂O (+ IR), multi-point sampling
  ([Mandelli](https://indico.ihep.ac.cn/event/6387/contributions/83702/attachments/43536/50137/PosterTIPP_BMandelli.pdf));
  CERN gas lab has O₂/H₂O meters, GC, MS ([EP-DT](https://ep-dep-dt.web.cern.ch/node/790)).
- **T2K TPC** (Micromegas, Ar/CF₄/iC₄H₁₀ 95/3/2): MecSens 511 (electrochemical O₂), Manalytical Picoview (H₂O),
  ADC MGA3000 IR (composition); analyser branch on its own MFC; spec O₂ < 10 ppm, H₂O < 100 ppm
  ([arXiv:1012.0865](https://arxiv.org/abs/1012.0865) §3.2).
- Other TPCs: Teledyne 3190 (0–100 ppm), oxy.IQ ([arXiv:2212.02385](https://arxiv.org/pdf/2212.02385)). ALICE ~1 % loss
  per ppm O₂ per m of drift in Ne/CO₂ ([arXiv:1001.1950](https://arxiv.org/pdf/1001.1950)).
- Borrow: CERN EP-DT gas group; INFN groups running He/iC₄H₁₀ drift chambers (MEG II Pisa/Lecce, ex-KLOE Frascati).
  Personal request; no public scheme.

## 6. Is O₂ needed if H₂O is measured? Yes.

Huk et al. NIM A267 (1988) 107, as in [arXiv:2501.05791](https://arxiv.org/pdf/2501.05791) eq. 2.1:
η = P²·f_O₂·A_gas·(1 + f_H₂O[ppm]/1000)/v_d (three-body Bloch–Bradbury; iC₄H₁₀ or H₂O as third body).

- H₂O does not attach by itself at TPC fields; it enhances O₂ attachment (×2 at 1000 ppm). Its main effect is on v_d.
- Ar/iC₄H₁₀ 99/1 at 100 V/cm/bar: A_gas = 48.4 µs⁻¹bar⁻², v_d 4.97 cm/µs → η ≈ 1×10⁻⁵ cm⁻¹ per ppm O₂. A_gas ∝ additive
  fraction; doubles from 100 to 50 V/cm/bar.
- **Extrapolation (not measured):** 90/10 at 200–300 V/cm, η ≈ (2–10)×10⁻⁵ cm⁻¹ ppm⁻¹ → 160 ppm over 3 cm ≈ 1–5 % loss
  from the cathode; ×2 at 1000 ppm H₂O. If n_TOF's late-charge loss was much larger, re-check the 160 ppm inference.
  Magboltz needs the three-body term set by hand ([ROOT forum](https://root-forum.cern.ch/t/addition-of-oxygen-with-not-substantial-effect-on-a-2-ll-plate-detector/63315));
  Garfield misses measured O₂ attachment by 6–100× ([arXiv:2511.07082](https://arxiv.org/html/2511.07082v2)).
- Leak vs permeation: an air leak gives O₂:H₂O ≈ 20.9 % : ~1.2 % (50 % RH) ≈ 17:1; permeation through mylar/plastic and
  outgassing of FR4/Kapton give mostly water (ratio ≪ 1). Needs both.

## 7. Ranking (agent's)

1. **Cheapest credible, ~€0.8–1.2k:** AII GPR-12-333 (€275) or B-2C-class cell (€100–300); stainless low-volume flow
   cell with Swagelok (€150–300); TIA + 24-bit ADC (ADS1220-class), thermistor, baro, read by the Pi (€100); 100–500 ppm
   span cylinder (€250). Second cell at the inlet +€500.
2. **Mid, ~€2.5–5k:** Ntron Microx EC (~€1.8–2.5k) or AII GPR-1500 (~€2.35k) + span gas; oxy.IQ (~€4–5k) if LNL wants IS.
3. **Reference, €6–12k or borrowed:** Teledyne 3000TA-XL, Systech EC900; PreSens Fibox trace (test cross-sensitivity);
   best: borrow a CERN EP-DT / INFN analysis module and cross-check the DIY cell.

Not recommended: zirconia (incl. the CERN DRD1 design), Alphasense % cells, coulometric DF at this flow, PyroScience.
Uncertain: B-2C and 3000TA prices; used prices are asking prices; PyroScience LDL; the 90/10 attachment figure.
