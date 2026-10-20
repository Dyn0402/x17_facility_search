# MX17 run budget (LNL as the case)

Started 2026-10-16, after the budget discussion at the n_TOF meeting. The aim is a complete list of what it takes
to run the apparatus again away from n_TOF: every component, borrow or buy, a priority and a budgetary price, with
the open questions marked.

**Live page:** <https://dylan-neff.web.cern.ch/facilities/budget.html> (unlisted). Its four views are the apparatus
map (click a part), the list (one option per item), the charts (scenarios, priority order, €1k blocks) and the
follow-ups (checklist). The default scenario is Self-sufficient. Link to a scenario with `?preset=lean|self|upgrade` and to a subsystem with `?g=<group>`,
e.g. `budget.html?preset=upgrade&g=back#map`.

## Update 2026-10-20: build the big plates ourselves

Pierfrancesco's comment (2026-10-16): buy the raw plates (Scionix, ~€2k each, €8k for four), make the detectors
ourselves, and borrow the PMTs again.
- The back-scintillator item has new **built-in-house** options:
  - 4 × 78 × 80 × 5 cm, €30k (14–68k). This is now the Upgrade default.
  - Split in two, €41k.
  - 4 cm thick, €27k.
  - The vendor-finished plates stay as a comparison.
- **Upgrade: €286k → €234k** (144–371k). Lean and Self-sufficient are unchanged at €98k and €174k (the table below predates the MM items).
- The LS item gets his rebuild option (€7k for cases + 16 PMTs). He recalls low light and position
  dependence rather than pile-up.
- New confidence level "collaborator's estimate".
- The analysis behind the options: `trigger_scint/TRIGGER_OPTIONS.md` §8.
- Stephan's two comments (MM re-bulk risk, new readout-PCB batch) are not folded in yet.

## Read this first (2026-10-16, second pass, after Dylan's answers)

| scenario | central | range |
|---|---|---|
| Lean: borrow everything we can | **€95k** | 62–140k |
| Self-sufficient: buy everything except DREAM | **€172k** | 112–249k |
| Upgrade: + big 5 cm plates, 320 SiPM channels, all 20 bars | **€286k** | 179–427k |

What Dylan's answers changed:
- **Lean went up** from €68k: the N1081Bs and linear FIFOs were rented from CERN, which is probably no longer possible,
  so even Lean buys them. Lean also buys the premixed gas, since there is no mixer and LNL's policy is unknown.
- **SiPM bias is ~63 V.** It is still needed with FERS: the A5202's onboard A7585D (20–85 V, ~10 mA) biases only SiPMs
  wired into its input, and ours sit behind the wall preamps. A 320 W EA-PS 3080-10 (€0.9k) is the default; the
  current draw is still to be confirmed.
- **DREAM LV:** 8 FEUs × ~5 A + TCM ~5 A ≈ 45 A, so 5 V / 60 A has margin. The M1 cards are unpowered.
- **From CEA, with DREAM:** the DAQ PC (confirmed) and one large NIM bin. A second bin is optional.
- **Borrowed from a colleague in Italy:** the 20 × 30 plastics and their PMTs.
- **Still open:** the target chamber and the Li targets (€?).

**Collaborator feedback** goes in a Google Sheet in Dylan's Drive, ["MX17 run budget — collaborator
feedback"](https://docs.google.com/spreadsheets/d/1ruV_J7cC5FnxiLDSF9arRIFDGfyGPwVTUNxzKT8tqFE/edit), made from
`out/feedback_sheet.csv`:
- one row per item: what we have, the open questions, then empty columns for a comment, a suggested price, the
  source and the commenter's name;
- 10 blank rows at the bottom for anything missing.

The page links each item's ✎ to its row (item i → row i + 2). Read the sheet back with the Drive connector,
`read_file_content`, and fold the answers into `items.py`. Don't re-upload the CSV once people have written in it:
add rows by hand instead, and set an item's `row` if the order changes.

**MM status (2026-10-16, third pass):**
- A (det3) is good: 92.9 % on the bench.
- B (det2) needs its drift fixed: 91.3 %.
- C (det6) needs re-bulking: 57.8 %, spark-limited.
- D (det7) needs re-bulking and is the worst: 43.1 %; at n_TOF ~130 of 512 X channels were dead.
- All four get new aluminised-mylar-only drift windows.

The data is `MM_STATUS` in `items.py`, shown on the map, in the Micromegas panel and above the list. The feedback sheet
is now **v2**, because the MM items changed the row order. v1 ("…collaborator feedback", no "(v2)") is superseded,
empty and private; Dylan can delete it.

## Comments backend (replaces editing the sheet, 2026-10-16)

The page has comment buttons: a general comment, a suggested missing item, and 💬 on every item. The commenter's name
is remembered in their browser. Comments are visible to everyone with the link, on their item and in a Comments tab.
They are stored by a Google Apps Script web app, `feedback_apps_script.gs`, bound to the v2 sheet, which appends one
row per comment to its "Comments" tab. Delete a row to hide a comment; write anything (e.g. "done") in its `status`
column to grey it out. Nobody edits the sheet directly; the item rows in it are only a reference.

**One-time deploy (Dylan):**
1. Open the [v2 sheet](https://docs.google.com/spreadsheets/d/1ruV_J7cC5FnxiLDSF9arRIFDGfyGPwVTUNxzKT8tqFE/edit)
   → Extensions → Apps Script.
2. Replace the editor contents with `budget/feedback_apps_script.gs` → Save.
3. Deploy → New deployment → type **Web app**:
   - Execute as: **Me**;
   - Who has access: **Anyone**;
   - Deploy, then authorise it with your Google account.
4. Copy the `…/exec` URL into `FEEDBACK_ENDPOINT` in `items.py`, rebuild and redeploy (or give the URL to Claude).
   With the endpoint empty, the buttons are hidden.

After editing the script, use Deploy → Manage deployments → edit → New version, so the URL stays the same.

**Shared with the detector-spec page (2026-10-16).** The script also serves `notes/mx17-detector-spec.html`
(source `nTof_x17/docs/detector_spec/`): requests with `page: "detector"` go to a separate "Detector" tab. A request
with no `page` is the budget, so this page is unchanged. Redeploy as a new version to switch the detector comments on.

To test locally with a mock backend, run `BUDGET_FEEDBACK_ENDPOINT=http://127.0.0.1:8765/mock python3 budget/build_budget.py`
with a small server that answers GET (list) and POST (append).

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
