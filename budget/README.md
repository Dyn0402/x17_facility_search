# MX17 run budget (LNL as the case)

Started 2026-10-16, after the budget discussion at the n_TOF meeting. The aim is a complete list of what it takes
to run the apparatus again away from n_TOF: every component, borrow or buy, a priority and a budgetary price, with
the open questions marked.

**Live page:** <https://dylan-neff.web.cern.ch/facilities/budget.html> (unlisted). Its four views are the apparatus
map (click a part), the list (one option per item), the charts (scenarios, priority order, €1k blocks) and the
follow-ups (checklist). The default scenario is Self-sufficient. Link to a scenario with `?preset=lean|self|upgrade` and to a subsystem with `?g=<group>`,
e.g. `budget.html?preset=upgrade&g=back#map`.

## Update 2026-10-30 (evening): public prices

Three web searches for public prices (catalogues, tenders, posted quotes). Tables with sources:
`quotes/catalog_2026-10-30.md`; the CAEN request is `quotes/caen_rfq_2026-10-30.txt`.
- **Now `catalog`:** GEN6-100/LN €1,850; NIM bin €4,390 (GANIL tender) or used (new option); 54 V supply €750; LEMO 00
  cables €49 made up (the patch line goes €3k → €5.5k); transport €3.5k → €2k; gas notes (premix is quote-only).
- **New options, presets unchanged:** 2 × DT5730SB desktops instead of V1730S + VME (~€10k vs €19k, reseller price);
  iseg SHR for the MM HV; an aluminium-profile stand (€2.5k).
- **Price warning:** an EJ-200 plate 80 × 80 × **2** cm was ≈ 6k CHF, far above Pierfrancesco's ~€2k per 5 cm plate.
  Check before the Upgrade's plates go in a proposal.
- CAEN: almost nothing public (A5202 ≈ €70/ch, 2021; DT5742B €4.9k, ~2019). The CAEN reply is the real source.

Totals: **Lean €82k, Self €191k, Upgrade €243k**.

## Update 2026-10-30: the SiPM-wall readout and the DAQ plan folded in (`daq_trigger/SIPM_READOUT.md`, `PLAN.md` §9)

The presets now follow the staging in SIPM_READOUT §7 and PLAN architecture D:
- **Lean = path 1b:** ganged walls as n_TOF, the wall digitizer borrowed from the LNL pool (`sipmdaq` €0), a V1730S
  bought for the PMTs into the borrowed crate. The analog trigger as n_TOF: used 428Fs, passive splits, 5 N1081Bs.
- **Self = architecture D (path 3):** a custom micro-coax → FERS board (€4 k) and 4 × A5202 + DT5215 (€21 k), one board
  per wall, read per bar end, all 20 bars lit. The FERS forms the wall OR, so M1 and all FIFOs go (5 N1081Bs; one N979
  splits the PMTs; LEMO patch only, no splitters; CEA bin + 1). The PMT digitizer now includes the VME crate and bridge.
- **Upgrade:** as Self with 4 × A5204 (path 3b) instead of 8 boards for 320 ch: per SiPM channel buys nothing.
- Corrections from the wall documentation: bias is 53–54 V at µA (`lvsipm`; FERS biases on its own path), no preamp
  respin (`sipmcomp` €0–2.5 k, only if planes 2–4 lack arrays), `lemo` is now the micro-coax board.
- Dropped options: 5 × V1742 and 3 × VX2745 for the walls (the VX2745 has 20 MHz bandwidth). New item `n979`.

Totals: **Lean €82k, Self €190k, Upgrade €242k** (were €104k / €202k / €271k). Every FERS, N979 and V1730S price is
still a guess: these are the first quotes to chase.

## Update 2026-10-29: the DAQ/trigger plan (`daq_trigger/PLAN.md`)

- **Prescaler:** the N1081B SCALER function is a frequency divider (manual UM8139 p. 34; API `scale` 1…10⁸), so
  a spare N1081B section is the prescaler (€0, after bench test T1). Lean and Self now use it; Upgrade keeps the
  DT5495.
- **Dual timer (N93B class), priority 1:** a 330–350 µs non-retriggerable busy after every trigger, because DREAM
  has no busy output. It locks the DREAM and digitizer event lists 1:1. Used in Lean (€0.6 k), new in Self and
  Upgrade (€2 k).
- **New item: switched PDUs** for remote power cycling: a NETIO 4KS on the N1081B bin (Lean, €0.3 k), or a NETIO
  8KS + Gude 8226-1 (Self and Upgrade, €1.3 k).

Totals: **Lean €104k, Self €202k, Upgrade €271k**.

Later the same day: the DREAM TCM has a busy output (a LEMO to solder on, TODO Dylan). The dual timer drops to
priority 3, as the fallback busy and the pulsed-facility beam gate, and Self takes a used one. Still to fold in from the plan, once quotes and bench tests
are in: the N979 active split instead of passive splitters and 2 FIFOs; a V1742 for the as-built ganged walls
(FERS kept for the un-ganged upgrade); and the digitizer-formed trigger (C, ~€25 k less) if test T5 passes.

## Update 2026-10-27 (second pass): nothing from n_TOF comes with us

Dylan: we have none of the things we had at n_TOF. The detectors are ours; DREAM, its PC and one large NIM bin may come
from CEA, with no NIM modules; the 20 × 30 plastics and PMTs are from the Italian lender. Everything else is bought or
borrowed anew.
- The support stand was "bring the n_TOF stand" (€2k) in every scenario. It is now bought: a new stand (€8k) in Self
  and Upgrade; adapting an LNL frame (€4k) in Lean.
- The questions that asked whether n_TOF items were ours (M1 cards, 428Fs, splitters, LEMO cables) are gone.
- The trigger group already bought every module in Self and Upgrade, so its numbers don't change.

Totals: **Lean €106k, Self €203k, Upgrade €268k**.

## Update 2026-10-27: the trigger logic, counted in full

The trigger group was under-counted: 4 N1081Bs, 4 FIFOs and €0.5–3k of splitters. The n_TOF trigger was actually
built from 6 N1081Bs, 6 linear FIFOs and dozens of splitters, all rented from CERN. The as-built map is in
`nTof_x17_DAQ/n1081b/n1081b_module_map.py` and `RUN_MODES_2026-07.md`:
- **6 × N1081B.**
  - M1: wall OR on the 16 428F segment sums.
  - M2: plastic discriminators.
  - M3: sector AND, 20 ns.
  - M4: Singles, Doubles, the veto and the master trigger to the DREAM TCM.
  - M5: scalers and time tags.
  - M6: pulser, mesh injection and SiPM blanking.
- **6 linear FIFOs:**
  - one LeCroy 428F per wall, summing the top and bottom ends of each segment;
  - two for the 8 plastic PMTs (from 2026-07-17, replacing the BNC-T split).
- **Splitters:** BNC-T / LEMO splits on every wall channel, plus ~100 LEMO patch cables between the boards.

The estimate for a run away from n_TOF:
- **N1081B: 6 in Self and Upgrade, 5 in Lean.** M1–M5 carry over one for one. M6's γ-flash jobs go away with a DC beam,
  but the clock, the pulser and spare sections still need a 6th board: at n_TOF, M2's D1 input died and M1 was offline
  for 3 days. A FERS that forms the wall ORs would save M1 (option "buy 4").
- **New item: a prescaler and trigger word.** The LNL trigger prescales SINGLE by 1/P, never PAIR, and tags every
  event. The N1081B firmware has no divide-by-N function, and its time-tag stream stops above ~50 Hz.
  - Self: an N1145-class preset counter (€2.5k), with the trigger bits on spare PMT-digitizer channels.
  - Upgrade: a DT5495-class FPGA unit (€8k).
- **FIFOs: 6.** Lean buys used 428Fs (€4.2k); Self and Upgrade buy new N625-class units (€13.2k). The big 2-PMT plates
  keep 8 PMTs, so 6 is still enough. Split plates would need 8.
- **New item: splitters and trigger patch cables (€5.9k):** ~40 resistive splitters, ~150 LEMO cables and adapters.
  The "cabling" item no longer counts the trigger patch.
- **NIM bins: 3.** The modules take 23–27 slots: N1081B 12, FIFOs 6, prescaler 1, N1470 4–8. That is the CEA bin plus
  2 (bought in Self and Upgrade, €8k).

Trigger group, central (range): Lean €24k → **€30k** (19–45k); Self €28k → **€51k** (34–73k);
Upgrade €28k → **€56k** (38–81k). The totals move to **Lean €104k, Self €197k, Upgrade €262k**. All the trigger
prices are guesses (CAEN quotes on request).

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
