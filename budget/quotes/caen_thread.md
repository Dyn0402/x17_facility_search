# CAEN budgetary quote: thread log

Contact: **Ferdinando Giordano**, Head of Innovation & Sales Manager, responsible for CERN–CAEN relations
(f.giordano@caen.it). He visits CERN often.

| date | who | what |
|---|---|---|
| 2026-10-30 | Dylan → info@caen.it | The request, `caen_rfq_2026-10-30.txt` (the sent text asked for "quotes"; 14 lines, plus demo units). |
| 2026-11-02 | Giordano → Dylan | Long list: is it for budgeting a proposal? It mixes NIM and VME: do we have both, or is it a ballpark? Offers a coffee at CERN or a Zoom with the LNL colleagues. |
| 2026-11-02 | Dylan → Giordano | Sent (full text in Thunderbird, CERN account). Yes, ballpark estimates to give the collaboration several costed options; we have NIM bins and could probably borrow a VME crate, but want a crate price in case. Last paragraph: rough per-unit list prices are enough, no formal quotes until an option is chosen; if the list is too long, the big-budget items are the priority (below); happy to meet for a coffee or a Zoom with LNL. |

## The priority items named in the reply

These set the budget totals in `budget/items.py`:
- FERS ×4 (A5202 or A5204) + DT5215;
- V1730S (PMT digitizer);
- N1081B ×5–6;
- HV: 2 × DT1471ET (Micromegas) and 2 × N1470 (PMTs).

## Notes from preparing the reply

- **NIM vs VME:** the only VME items on the list are the V1730S/VX2730, the V1742 and the crate + A3818. The N-modules go in
  our NIM bins; FERS, DT5495, DT1081B and DT1471ET are standalone. The Self/Upgrade presets read the walls with FERS, so the
  V1742 matters only for Lean path 1b (borrowed). The one VME item left is the 16-ch PMT digitizer, and it has non-VME
  equivalents with the same chip: 2 × DT5730SB (desktop, 8 ch) or 2 × N6730 (NIM, 8 ch, double width, 4 slots in an
  already-full bin). Both read out over USB or the optical link (A3818/A4818). Not yet an option in `items.py` (N6730).
- **The two HV units do different jobs:** DT1471ET (4 ch, 5.5 kV / 300 µA, desktop, per-channel polarity) for the 8 MM
  channels (≲1.5 kV, µA); N1470 (4 ch, 8 kV / 3 mA, NIM) for the 8 PMTs (−2 kV, mA). The RFQ's "N1470 2–4" covers the
  N1470 as an MM alternative too.
