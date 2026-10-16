# MX17 run budget (LNL as the case)

Started 2026-10-16, after the budget discussion at the n_TOF meeting. The aim is a complete list of what it takes
to run the apparatus again away from n_TOF: every component, borrow or buy, a priority and a budgetary price, with
the open questions marked.

**Live page:** <https://dylan-neff.web.cern.ch/facilities/budget.html> (unlisted). Its four views are the apparatus
map (click a part), the list (one option per item), the charts (scenarios, priority order, €1k blocks) and the
follow-ups (checklist). Link to a scenario with `?preset=lean|self|upgrade` and to a subsystem with `?g=<group>`,
e.g. `budget.html?preset=upgrade&g=back#map`.

## Read this first (2026-10-16)

| scenario | central | range |
|---|---|---|
| Lean: borrow everything we can | **€68k** | 43–101k |
| Self-sufficient: buy everything except DREAM | **€176k** | 115–257k |
| Upgrade: + big 5 cm plates, 320 SiPM channels, all 20 bars | **€295k** | 185–441k |

- Two items have no number at all: the thin target chamber and the Li targets. Both depend on what LNL provides.
- The DREAM loan is never a cost, but it carries a €72k liability.
- In Lean, the biggest purchases are the M1 cards (€24k for 12), the SiPM DAQ (FERS, €18k) and the PMT digitizer (€13k).
- Most of the price confidence is low, for two reasons:
  - CAEN, iseg and Wiener publish no prices. Every HV, N1081B, FIFO and NIM-bin price is my guess until quoted.
  - Dylan's figures (M1 ~€2k each, cables €400 each, re-bulk "a few k") still need checking.
- Items marked **added** are not on Dylan's list: gas, NIM bins, the chamber, the targets, PCs, cabling, transport
  and the stand. Check whether each is needed at all.

## Files

| file | what |
|---|---|
| `items.py` | **The data.** Groups, items, options (borrow / buy variants), priorities, confidence, questions, presets. Edit here. |
| `build_budget.py` | `items.py` + `budget_template.html` → `out/budget.html`, plus `out/budget_items.csv` (one row per option) |
| `budget_template.html` | The page: standalone, no external loads. The data is injected at `/*__DATA__*/null`. |

Scintillator and SiPM-DAQ prices are imported from `../trigger_scint/costs.py`, the model behind the LNL deck's
price slide, so the two stay consistent. The plates here **exclude** HV and digitizer channels, which are separate
items. The deck's "€93k" for the 5 cm polystyrene plates includes them; here they come to €82k plus the HV and
digitizer lines.

## Update and redeploy

```bash
python3 budget/build_budget.py
cp budget/out/budget.html ~/PycharmProjects/dylan-cern-site/pages/facilities/budget.html
cd ~/PycharmProjects/dylan-cern-site && python3 scripts/build.py && git add -A pages/facilities facilities && git commit -m "budget: …"
rsync -t facilities/budget.html lxplus:/eos/user/d/dneff/www/facilities/   # or scripts/deploy-eos.sh if the site repo is clean
```

## Public price points used (2026-10-16)

- TDK-Lambda GEN6-200/LN, 6 V / 200 A: €2,385 ex VAT on RS Italy. The GEN6-100/LN is the size we need. A used
  Delta SM15-100 sells for ~€550.
- EA-PS 3080-10 C, 80 V / 10 A / 320 W: €770 (Datatec AT) to €1,026 (RS DE) ex VAT. It gives only ~4.5 A at 70 V,
  so 700 W needs the 1 kW class.
- An old Wiener/iseg quote to SLAC (2013): an EHS 16-channel module at $7.6k and an MPOD crate at $6.8k. These were
  only a cross-check on the HV guesses.
- CAEN N1470, DT1471ET, SY5527, N1081B, FERS A5202: quote on request, no public price.
