# INFN Torino scintillator / PMT quotes (reference prices)

Received 2026-11-04. Pierfrancesco Mastinu forwarded (to dylan.neff@cern.ch, subject "Fwd: offerte scintillatori X-17")
a mail from Gianpiero Gervino (INFN Torino, gervino@to.infn.it, 28 Oct 2026). Pierfrancesco: "the quotation for PMT of the
scintillators, to be added to the budget".

**These are old quotes to INFN Torino for other items, not quotes for what we need.** They give real 2024–2026 Italian prices
from the same vendors (TNE Srl, Cassina de' Pecchi (MI), Scionix/Eljen's only Italian representative since 2025; Hamamatsu
Photonics Italia). All prices are ex VAT and delivered to the INFN site.

| file | vendor, ref, date | what | qty | unit € | total € | per-unit metric |
|---|---|---|---|---|---|---|
| `hamamatsu_offer_I118460_R1328U-53_2026-06-03.pdf` | Hamamatsu Italia I118460, 3 Jun 2026 (valid to 11 Aug 2026, delivery TBD) | R1328U-53, "biplanar phototube" | 3 | 4,043.45 | 12,130.35 | |
| `tne_offer_01012-2024_EJ-200_blocks_2024-07-11.pdf` | TNE 01012/2024, 11 Jul 2024 (10–14 weeks) | EJ-200, 50 × 50 × 200 mm, edges diamond-milled, faces as-cast | 80 | 131.00 | 10,480 + 120 shipping | **€0.262/cm³** |
| `tne_offer_00412-2025_EJ-212_wall_bars_2025-06-26.pdf` | TNE 00412/2025, 26 Jun 2025 (MePA RdO 5492592, 12–16 weeks) | EJ-212, 3 × 26 × 500 mm, edges diamond-milled, faces as-pressed | 88 | 175.00 | 15,400 | €4.49/cm³ (thin bars) |
| `tne_offer_00200-A-2026_EJ-550_EJ-560_2026-04-20.pdf` | TNE 00200-A/2026, 20 Apr 2026 (7–9 weeks) | EJ-550 optical grease, 150 g tube | 1 | 440.00 | 440 | |
| (same) | | EJ-560 optical interface sheet, 330 × 530 × 1 mm | 2 | 895.00 | 1,790 + 150 shipping | |

## What each one is (Gervino's notes)

- **TNE 00412/2025, EJ-212 bars: these are the SiPM-wall bars.** 88 bought = 4 walls × 20 + 8 spares (3 mm thick, 25 mm
  pitch, 500 mm long, matching `SimConfig.hh`). Evaristo and Giorgio De Angelis put the SiPMs on them. So the scintillator in
  the four walls is worth about €14k (€175 a bar), and a spare bar costs €175 plus 3–4 months' lead time.
- **TNE 01012/2024, EJ-200 blocks:** bars for an earlier design (when the detector was meant to sit in a magnet). They were
  never bought; the EJ-212 order replaced this quote.
- **TNE 00200-A/2026:** coupling material for the wall bars, sent to Evaristo and De Angelis. Gervino calls it "the adhesive
  reflective sheets + Scionix optical grease". On the quote the sheets are **EJ-560 silicone optical-interface pads, not
  reflector**. His comment: "Scionix charges a lot".
- **Hamamatsu I118460:** "3 fast PMTs (rise time 0.6–0.8 ns) like those optimised for the liquid scintillator at JUNO". Luigi
  chose not to show it to CSN3; Gervino wanted to put it in the 2027 requests.
  **Caution:** Hamamatsu's datasheet describes the R1328U series (TPT1028E) as a *biplanar phototube*. That is a vacuum photodiode
  with no dynodes, so gain ≈ 1 and rise time 60 ps; the -53 has a Na-K-Sb-Cs cathode. It cannot read a scintillator plate on
  its own. Either the part number is not the tube Gervino meant, or the order is for something else. Use the price only as a
  scale for a fast 2″ Hamamatsu tube in Italy in 2026 (~€4k), and ask which tube he meant.
- **Still open:** Gervino has asked TNE to quote **raw scintillator** (the plates we need). TNE has not answered yet, and he is
  chasing it. This is the quote that settles the big-plate price (`WAITING` in `items.py`).

## How they enter the budget (2026-11-04)

- `trigger_scint/costs.py` `RAW_PER_CM3`: 0.064 / 0.13 / 0.30 → **0.064 / 0.26 / 0.50 €/cm³**. The central value is now the TNE
  EJ-200 price (edges milled, faces as-cast). The high end is the CERN 2025 figure (80 × 80 × 2 cm for 6k CHF, ≈ €0.5/cm³). The
  low end is still Pierfrancesco's ~€2k per plate, which is not in writing. At €0.262/cm³ a 78 × 80 × 5 cm plate is about **€8.2k**
  (31,200 cm³), not €2k, unless large raw sheets are much cheaper per cm³ than milled 500 cm³ blocks.
- `CEMENT_PER_PIECE` 50 / 100 / 200 → **150 / 250 / 500 €** per piece, for two couplings. It is based on the EJ-550 tube
  (€440 + shipping, spread over the 4 plates) and the EJ-560 sheet (€895 + shipping, for 2″ pads).
- New reference option on the back-scintillator item: big plates built in-house with **8 bought fast 2″ PMTs at €4,043** (not in a
  preset).
- The SiPM-wall item records the replacement value of the bars (€15.4k for 88).
