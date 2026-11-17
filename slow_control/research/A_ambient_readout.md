# Research notes A: ambient T/RH/p, chamber temperature, gas pressure, readout (2026-11-17)

Web research (agent report, lightly edited). Prices are snapshots; "≈" = converted (1 CHF ≈ €1.07, 1 GBP ≈ €1.17,
1 USD ≈ €0.87); "(est.)" = not verified on a distributor page; "from memory" = datasheet value not re-fetched.
Synthesis and recommendation: `../SENSOR_OPTIONS.md`.

**Key point:** drift velocity depends on the gas *inside the chamber*, so measure outlet-gas T, p and H₂O directly; the
hall sensors explain *why* it changes. Absolute pressure accuracy matters less than stability; a one-off offset against a
reference barometer (LNL, or Venice/Padova METAR) brings a MEMS barometer to ~±0.2 hPa.

## A1. Bare chips / breakouts

| Chip (breakout) | T | RH | p abs / rel | Drift | Price | Source |
|---|---|---|---|---|---|---|
| **Sensirion SHT45** (Adafruit 5665) | ±0.1 °C typ (0–75 °C) | ±1.0 %RH typ (25–75 %) | – | <0.2 %RH/yr (from memory) | £10.50 ≈ €12 | [Pimoroni](https://shop.pimoroni.com/products/adafruit-sensirion-sht45-precision-temperature-humidity-sensor-stemma-qt-qwiic); PTFE-membrane version [Jameco](https://www.jameco.com/z/6174-Adafruit-Industries-Adafruit-Sensirion-SHT45-Precision-Temp-Humidity-with-PTFE_2883783.html) |
| SHT41 | ±0.2 °C | ±1.8 %RH | – | similar | ~€8 (est.) | – |
| **Sensirion SHT85** (pin module) | ±0.1 °C | ±1.5 %RH | – | <0.25 %RH/yr, <0.03 K/yr | ~$32 ≈ €28 | [Findchips](https://www.findchips.com/search/SHT85), [datasheet](https://psl.noaa.gov/data/obs/instruments/SensirionSHT85.pdf); Farnell: no longer stocked |
| **TI HDC3022** (Adafruit) | ±0.1 °C typ | ±0.5 %RH typ | – | – | £8.60 ≈ €10 | [TI](https://www.ti.com/product/HDC3022), [Pi Hut](https://thepihut.com/products/adafruit-hdc3021-precision-temperature-humidity-sensor-stemma-qt-qwiic) |
| **Bosch BMP390** | – | – | ±0.50 hPa / ±0.03 hPa | ±0.16 hPa / 12 mo | ~€12 (est.) | [Bosch](https://bosch-sensortec.com/products/environmental-sensors/pressure-sensors/bmp390) |
| **Bosch BMP585** (Adafruit 6413, ported) | – | – | ±0.6 hPa typ / ±0.06 hPa | – | £13.80 ≈ €16 | [Adafruit](https://learn.adafruit.com/adafruit-bmp580-bmp581-and-bmp585-temperature-and-pressure-sensor/overview), [Pi Hut](https://thepihut.com/products/adafruit-bmp585-ported-i2c-spi-temperature-and-pressure-sensor-stemma-qt) |
| Infineon DPS310 | – | – | ±1 hPa / 0.002 hPa | – | $6.95 | [Adafruit](https://www.adafruit.com/products/4494) |
| Bosch BME280 / BME680 | ±1 K | ±3 %RH | ±1 hPa / ±0.12 hPa | – | ~€15–20 (est.) | skip: T self-heating limited |
| TE MS5611 / MS5837 | – | – | ~±1.5 hPa (unverified) | – | ~€10–25 (est.) | no better than BMP390; clone boards common |

Best per euro: SHT45 or HDC3022 for T/RH; BMP390/BMP585 for p.

## A2. Ready-made loggers

| Device | Specs | Interface | Price | Verdict |
|---|---|---|---|---|
| **Yoctopuce Yocto-Meteo-V2** | SHT35 (±0.2 °C, ±1.5 %RH) + TDK ICP-10100 (±0.01 mbar rel; abs ~±1 hPa per TDK) | USB, Python API | CHF 60.64 ≈ €65 ([Yoctopuce](https://www.yoctopuce.com/EN/products/usb-sensors/yocto-meteo-v2)) | best plug-and-play value |
| Comet T7511 (Ethernet) / T7611 (PoE) | ±0.4 °C, ±2.5 %RH, ±1.3 hPa | Modbus TCP, SNMP, HTTP, internal log | €440 / €482 ex VAT ([T7511](https://didactum-security.com/en/T7511_comet-t7511-websensor-cable-probe-for-temperature-humidity-and-barometric-pressure), [T7611](https://didactum-security.com/en/T7611_comet-t7611-poe-websensor-for-temperature-humidity-and-barometric-pressure)) | robust, misses ±0.2 K / ±0.5 hPa; good independent backup |
| Comet T7510 (T/RH only) | – | Ethernet | €425 ([Didactum](https://didactum-security.com/en/T7510_comet-t7510-ethernet-websensor-for-temperature-30-to-80-0c)) | – |
| Papouch TH2E | accuracy not published | Ethernet, Modbus TCP | €224 ([Chip Electronics](https://chipelectronics.com/en_US/p/TH2E-Ethernet-thermometer-and-hygrometer/246)) | skip |
| Lascar EL-USB-2 / 2+ | ±0.5 (0.3) °C, ±2.25 %RH | standalone USB | €70 ex VAT ([RS IE](https://ie.rs-online.com/web/p/data-loggers/4901064)) | cheap black-box spare |
| Vaisala PTB330 | ~±0.15 hPa (from memory) | RS-232/485 | ~$3,760 ([Selectum](https://selectumllc.com/i/vaisala-ptb330)) | reference; borrow from LNL instead |
| Vaisala PTB110 | ~±0.3 hPa | analog | ~$1,424 ([Transcat](https://www.transcat.com/vaisala-ptb1105f0ab-ptb1105f0ab)) | MEMS + one-off offset is as good |
| Shelly / Govee (consumer) | ~±0.5 K, ±3 %RH | Wi-Fi/BLE, cloud | €20–40 (est.) | not suitable |

## A3. Chamber-body / gas-outlet temperature (±0.1 K)

| Option | Accuracy | Price / ch | Source |
|---|---|---|---|
| **Pico PT-104** (4 ch, USB + Ethernet) | 0.01 K res., ~±0.015 K instrument | €689 / 4 ≈ €172 + probe | [Farnell](https://es.farnell.com/en-ES/pico-technology/usb-pt-104/data-logger-temperature-rtd/dp/1830984) |
| **Yocto-PT100-C** (1 ch, USB) | 0.03 °C with 1/10 DIN probe | CHF 81.62 ≈ €87 + probe | [Yoctopuce](https://www.yoctopuce.com/EN/products/usb-environmental-sensors/yocto-pt100-c) |
| **MAX31865** breakout (SPI) | ~±0.1 K with 4-wire + 1-point cal | €18.80 ([Opencircuit](https://opencircuit.shop/product/adafruit-pt100-rtd-temperature-sensor)) | – |
| Pt100 1/10 DIN 4-wire probe (RS 236-4299) | ±0.03 K at 0 °C | £112.58 ≈ €132 | [RS](https://uk.rs-online.com/web/p/rtd-sensors/2364299) |
| Pt100 Class B 4-wire probe (RS 123-5589) | ±0.3 K | £39.29 ≈ €46 | [RS](https://uk.rs-online.com/web/p/platinum-resistance-temperature-sensors/1235589/) |
| DS18B20 (1-Wire) | ±0.5 K abs; 0.0625 K res.; cross-cal ~0.1 K | ~€3–8 (est.) | – |

Class A/B probes cross-calibrated in one block against a single 1/10 DIN probe give ~0.05 K relative.

## A4. Gas-line pressure

| Device | Range / accuracy | Interface | Price | Notes |
|---|---|---|---|---|
| **Keller PAA-33X** 0.8–1.2 bar abs | ±0.05 %FS, ±0.1 % TEB | RS-485 (Modbus) + analog | quote only; ~€700–1,000 (est.) | stainless wetted; [datasheet](https://tech.dk/wp-content/uploads/2020/11/Datenblatt_Serie-33X-35X_e.pdf); ask whether %FS is of 1.2 bar or of the span |
| Keller LEO 2 | ±0.1 %FS ≈ ±3 hPa | display | €441 ([Novapart](https://novapart.co/products/LEO2%20/%20-1...3BAR%20/%2081021/pressure-sensor-ip65-0-to-50c-4-bar-digital)) | handheld |
| Druck UNIK 5000 1 bar abs | ~±0.04 %FS (est.) | analog | ~€700–900 (est.) | [RS](https://uk.rs-online.com/web/p/pressure-sensors/7463524) |
| Honeywell MPRLS / ABP2 / HSC | ±0.25–1 %FS ≈ ±4–16 hPa | I²C/SPI | $14–56 | too coarse for absolute |
| **BMP390 / BMP585 in a gas cell** | ±0.5 hPa abs, 0.03–0.06 hPa rel | I²C | ~€15 + cell | best value; gel/silicon wetted, isobutane long-term **not verified** — treat as replaceable |
| **Sensirion SDP810-500Pa** (differential, overpressure) | ±500 Pa, ~3 % of reading | I²C | €26.23 ([DigiKey](https://www.digikey.at/en/products/detail/sensirion-ag/SDP810-500PA/6605489)) | 20-week lead time listed: order early |

## B. Readout

| Option | Cost | Pros | Cons |
|---|---|---|---|
| **Raspberry Pi 5 4 GB** + I²C/SPI/1-Wire/USB | €100 ([heise, Apr 2026](https://heise.de/-11243959)) + ~€60–80 PSU/case/SSD/PoE (est.) | native buses, RTC header, chrony, Python | SD wear; SEU-sensitive |
| Arduino / ESP32 / RP2040 → USB serial to DAQ PC | €10–30 | no extra Linux box | firmware; host timestamps |
| LabJack T4 / T7 | $305 / $570 ([LabJack](https://labjack.com/collections/t-series-devices)) | analog in, Modbus TCP | overkill for digital sensors |
| Yoctopuce + YoctoHub-Ethernet | hub ~€100–150 (est.) | no soldering, PoE | fewer sensors |
| Modbus TCP devices | €300–500 / point | industrial | expensive per channel |

Data path: daemon reads every 10 s, writes 1-min means to a daily CSV (epoch + ISO-8601 UTC), rsynced to the DAQ PC;
optionally InfluxDB + Grafana. chrony with the DAQ PC (or LNL NTP) as server; log chrony's offset as a channel.

Precedent: CMS RPC at GIF++ logs gas + environment T/p/RH and corrects HV to an effective HV
([arXiv:1605.09138](https://arxiv.org/pdf/1605.09138), [ECOgas](https://arxiv.org/pdf/2311.17574)); T2K ND280 TPC gain
vs T/p ([arXiv:1901.03750](https://arxiv.org/pdf/1901.03750)); STAR iTPC β = 3.74 gain slope in T/p
([arXiv:1805.03938](https://arxiv.org/pdf/1805.03938)); T2K resistive MM gain linear in T/p
([arXiv:2303.04481](https://arxiv.org/pdf/2303.04481)); ACTAR TPC MM ±2.5 % gain over 2 days ≈ 1 K
([EPJ WoC](https://www.epj-conferences.org/10.1051/epjconf/201817401010/pdf)). ATLAS NSW: drivers listed, no coefficients found.

Radiation: COTS SoCs (Pi 3B+, Pi Zero 2W) show SEUs/crashes under n/p ([arXiv:2503.03722](https://arxiv.org/html/2503.03722v1)).
Keep the Pi outside the shielding, read-only root (overlayfs), boot from USB SSD, hardware watchdog, I²C re-init on error,
PoE. Only cheap MEMS chips near the beam, via **PCA9615 differential I²C over CAT5** (SparkFun QwiicBus EndPoint €12.81,
[DigiKey](https://www.digikey.de/en/products/detail/sparkfun-electronics/16988/13998111), ~30 m). USB ≤ 5 m; RS-485 for long runs.

## C. FEU crate temperature

One DS18B20 per crate on a 1-Wire chain (~€5 each). First ask CEA whether the FEUs report an on-board temperature.
