# Handoff

## Budget: what it takes to run again, at LNL — updated 2026-10-16 (dylan-MS-7C84)

**Resume:** live and taking comments. Next: fold collaborator comments and quotes into `budget/items.py`, rebuild, redeploy.

**Goal (Dylan, after the meeting budget discussion):** a complete budget for running the apparatus again (LNL as the case), as a
site page collaborators can comment on. Every component gets borrow or buy options, a priority, a cost, and "?" where a follow-up is
needed.

**Done:**
- The page is live: `dylan-neff.web.cern.ch/facilities/budget.html` (unlisted), linked from `facilities/index.html` and `lnl.html`.
  - Five views: apparatus map, list, charts, follow-ups and comments.
  - Scenarios: Lean €98k, **Self-sufficient €174k (the default)**, Upgrade €286k.
- Dylan's answers are in:
  - SiPM bias ~63 V, still needed even with FERS;
  - DREAM LV ~45 A (8 FEUs + TCM);
  - the N1081Bs and FIFOs were rented from CERN, so they are bought now;
  - the plastics and PMTs were lent by a colleague in Italy;
  - from CEA: the DAQ PC (confirmed) and one NIM bin;
  - premixed Ar/iC₄H₁₀ gas is bought;
  - the target chamber and Li targets stay at €?.
- Per-MM status (`MM_STATUS`), with June-bench efficiencies:
  - A (det3) good, 92.9 %;
  - B (det2) needs its drift fixed, 91.3 %;
  - C (det6) re-bulk, 57.8 %;
  - D (det7) re-bulk and the worst, 43.1 %; ~130 of 512 X channels were dead at n_TOF;
  - all four get new aluminised-mylar-only drift windows.
- Comments: a general comment, a suggested missing item, and 💬 on every item; the name is remembered in the browser.
  - They are POSTed to a Google Apps Script web app (`budget/feedback_apps_script.gs`), bound to the sheet "MX17 run budget —
    collaborator feedback (v2)" in Dylan's Drive, which appends rows to its "Comments" tab.
  - Endpoint: `FEEDBACK_ENDPOINT` in `items.py`. Verified live: GET works, and the validation and honeypot behave on POST.

**Next steps:**
1. Dylan posts one real test comment to confirm the full round trip, then deletes the row in the sheet.
2. As comments and quotes arrive: read the "Comments" tab (Drive `read_file_content` on the v2 sheet), update `items.py`, rebuild,
   copy to the site, redeploy. Mark a handled comment with `status` = done in the sheet.
3. Get quotes: M1 cards (CERN), the FEU cables, CAEN HV / N1081B / FIFOs, the plates (Nuvia/Epic), FERS.

**Gotchas / decisions:**
- The plates exclude HV and digitizer, which are separate items; the deck's €93k includes them.
- An Apps Script deployment needs the owner to authorise it once (Run `doGet` in the editor). Without that, "Anyone" access still
  returns 403. After editing the script, use Manage deployments → New version, so the URL stays the same.
- Testing the POST with curl needs `--data` without `-X POST` (curl must switch to GET on the 302, as a browser does).
- The selected options are stored in localStorage under `mx17-budget-sel2`, so the earlier "lean" picks reset.
- Superseded: feedback sheet v1 (empty, private); Dylan can delete it. Sheet editing as the feedback channel was dropped at Dylan's
  request.
- The site repo's branch is `master`, not `main`.
- The Apps Script is shared with the detector-spec page (`nTof_x17/docs/detector_spec/`): `page: "detector"` goes to
  a "Detector" tab. Redeployed 2026-10-16 (same URL); the budget GET is unchanged.

**Key files & commands:**
- `budget/items.py` — all the data (items, options, presets, MM_STATUS, endpoint); `budget/README.md` — how to update.
- `python3 budget/build_budget.py && cp budget/out/budget.html ~/PycharmProjects/dylan-cern-site/pages/facilities/budget.html`, then
  in the site repo `python3 scripts/build.py`, commit, `bash scripts/deploy-eos.sh`.
- Local test with a mock backend: `BUDGET_FEEDBACK_ENDPOINT=http://127.0.0.1:8765/mock python3 budget/build_budget.py`.

## LNL: one closing slide for the n_TOF talk (§18) — updated 2026-10-14 (dylan-MS-7C84)

**Resume:** the figures and the draft slide are done and deployed. Dylan will build the real slide himself.

**Goal (Dylan):** one slide, "Possible measurement at LNL", to end the 15 Oct n_TOF talk. It should cover:
- ⁷Li + p, an exact ATOMKI re-measurement;
- X17 per day in acceptance and the days to the ATOMKI sensitivity, for the n_TOF stack and for the big plastics;
- the trigger-acceptance factor and the price;
- scattering and calorimetry as the open studies.

Most of all he wanted the figures and scripts, so he can regenerate them.

**Done:**
- `lnl/talk/lnl_summary_figs.py` → `lnl/out/talk/`:
  - figures `x17_per_day`, `significance_days` and `lnl_summary`, each as png, pdf and csv;
  - `numbers.json`.
  - All numbers are read from `reach_geant.csv` (`days_3d`, `S3d_per_day`), `acceptance_geant.csv` (`pair_tag`) and `trigger_scint/costs.py`.
- `lnl/deck/summary_slide.py`: the slide `lnl-summary` (deck slide 3, after the pitch cover). It uses the same `numbers()`.
- Headline, 1 µA:
  - X17/day: 17 → 135 (×7.8);
  - 3σ at R(ATOMKI): 17.0 → 1.00 d;
  - pair trigger: 3.3 → 23.2 % (×7.1);
  - plates: €93k in polystyrene, ~€121k with the SiPM readout.
- FEASIBILITY_SIM §18 and the README "read this first" block are updated.
- Deck deployed: site commit 59b6907, with only the note file rsynced. The site repo still has the other session's
  uncommitted work, which was left untouched.

**Next steps:** Dylan pastes the figures into the talk. Rerun the script if `reach_geant.csv` changes.

**Gotchas:**
- The significance curve uses Z ∝ √t. Past ~a week this is optimistic unless the wider fit is used (§17.3).
- "X17 in acceptance" means inside the 3D fit after MM 15° + TOF, not just triggered.

**Key files:** `lnl/talk/lnl_summary_figs.py`, `lnl/deck/summary_slide.py`, `lnl/out/talk/`.

## LNL: analysis end to end on pseudo-data (§17) — updated 2026-10-14 (dylan-MS-7C84)

**Resume:** §17 and its 5 slides are done, committed and deployed; next: review slides, optionally write §17.4 (controls).

**Goal (Dylan):** a full step-by-step analysis on simulated data "as if experimental, without perfect knowledge of the
background", plus a scan of X17 couplings, for the 15 Oct talk.

**Done:**
- `lnl/sim/lnl_pseudo.py` (→ `lnl/out/pseudo/`): walkthrough (blind, predict, unblind, full fit) and toy scans. Variants:
  reference (1, 7, 30 d), MC halves (7 d), and `--widened-only` (the fit also floats S_θE and S_m; 7 and 30 d, 500 toys).
- `lnl_nd.fisher_nd(..., templates=True)` returns μ, the parameter rows g and the priors. Default path unchanged.
- `lnl/deck/pseudo_slides.py`: five slides after the impostor ones; `price_slide` added to `pitch_slides.py` (reads
  `trigger_scint/costs.py`). The pitch block is now 19 slides. Deck rebuilt OK (17.0 d / 1.00 d headline unchanged).
- FEASIBILITY_SIM §17: the previous session's usage ran out mid-way, so its §17.3 table was from an older run. This
  session rewrote it from `scan.csv`, `scan_widened.csv` and `walk_summary.json` and added the wider-fit result.

**In progress / where it stopped:**
- §17.4 ("validate the width of the wider fit on the controls") is referred to but not written. No code for it.
- Deployed 2026-10-14 13:04: only `notes/lnl-x17-feasibility.html` was rsynced to EOS (the site repo had another session's
  uncommitted `mx17-feedback-and-ions`, hub/index and sw.js, so no full `deploy-eos.sh`). Redeploy decks liberally (CLAUDE.md).

**Next steps:**
1. Dylan: look at the new slides (pseudo block and price) in `lnl/out/lnl-x17-feasibility.html`.
2. Optional: §17.4, a realistic wider fit (not spanning the truth exactly); a bigger template MC.

**Gotchas:**
- Run with `LNL_SEL=$PWD/lnl/sim/sel_v3` (gitignored, fetch with `lnl/sim/fetch_sel.sh`) and the nTof_x17 venv python
  (`.venv/bin/python` on Linux); system python has no pandas.
- The wider fit is idealised: it contains exactly the structure the truth has, so its good coverage is an upper bound.
- The walkthrough seed 20261015 was not chosen; r̂ was 0.87, not a lucky draw.

**Key files:** `lnl/sim/lnl_pseudo.py`, `lnl/deck/pseudo_slides.py`, `lnl/out/pseudo/`, `lnl/FEASIBILITY_SIM.md` §17.

## LNL: 2D views of the 3D fit and the impostor test, for the 15 Oct talk — updated 2026-10-14 (dylan-MS-7C84)

**Resume:** three pitch slides (9–11) are in the deck. Dylan: review them before the talk.

**Goal (Dylan):** show the θ × |y| × E_sum fit as 2D plots, raw counts as well as S/B. Answer "how do you know your excess
isn't poorly modelled background?", and say why LNL can work where n_TOF did not.

**Done:**
- New `lnl/sim/lnl_nd_maps.py` → `lnl/out/nd/maps/{maps,proj,bias}.csv` (FEASIBILITY_SIM §16). It uses the reference
  fit's event list.
  - The **impostor** is a background error that copies the X17 angle spectrum exactly. Each X17 event takes |y| and
    E_sum from a background event at the same angle. A: acceptance-type (all E_sum). B: 18 MeV-only.
  - The angle-only fit reads it as 100 % of an X17. The 3D fit reads 13 % (A) or 24 % (B), ~1–2σ in a week against 7.5σ
    for a real X17, with χ² ≈ 20 left over (big plastics).
- `lnl_nd.fisher_nd(delta=(v, w))` returns `b` and `dd` for the linear bias. The default path is unchanged: the deck
  still quotes 1.00 / 17.0 d.
- `lnl/deck/maps_slides.py`: slides `pitch-2d`, `pitch-impostor`, `pitch-impostor-2d`, called from `pitch_slides`
  after "S/B". The pitch block is now slides 2–15.

**Next steps:**
1. Dylan: review slides 9–11 (wording of the n_TOF contrast in the Details of slide 11).
2. Earlier list still open: confirm the SiPM count, LNL beam-line drawings → Geant4, bench-test a 5 cm plate.
3. Optional: run the impostor at 1 and 30 days (in `bias.csv`), or with a Poisson pseudo-data map, if a "what you would
   see" figure is wanted.

**Gotchas:**
- The impostor is defined against the X17 at R(ATOMKI); the bias is linear, so it scales.
- Rendering slides for checking: headless Chrome on a copy of the deck HTML with a CSS override that shows one
  `.frame` and removes the scale transform.

**Key files:** `lnl/sim/lnl_nd_maps.py`, `lnl/deck/maps_slides.py`, `lnl/out/nd/maps/`, `lnl/FEASIBILITY_SIM.md` §16.

## LNL pitch slides, 3D-fit reference, scattering scan — updated 2026-10-13 (dylan-MS-7C84)

**Resume:** pitch slides live for the 15 Oct talk; next: confirm SiPM count (160/320), Geant4 with the real LNL beam line.

**Goal (Dylan):** pitch slides for the 15 Oct talk in the LNL deck. They cover:
- the case;
- LNL against n_TOF;
- issues and unknowns, especially beam-pipe scattering smearing the bump;
- S/B as the real limit, and what to study;
- n_TOF against the big-plastic setup, with a price;
- DAQ options for the plates and the SiPM walls.

**Done:**
- `lnl/deck/pitch_slides.py`, 11 slides inserted after the cover (slides 2–12); the rest of the deck is backup:
  - pitch, why, plan, vs n_TOF, lessons, setup (price tag ≈ €93–136k from trigger_scint/costs.py);
  - S/B, smearing, studies, unknowns, DAQ.
  - The run plan reads `reach_geant.csv` `days_3d`. Setup and the 441 keV calibration are 1-day allowances, not computed.
- `plastics_scatter.config_slide(..., panels_only=True)` reuses the to-scale drawings.
- **New result** (`lnl/sim/lnl_smear_nd.py` → `out/nd/smear_scan.csv`, FEASIBILITY_SIM §15):
  - Scaling each event's reco−truth residual by f, the 3D fit goes 1.0 → 2.5 → 6.8 → 31 d at
    σ68 4.5 / 9 / 14 / 27°; m_ee alone 1.7 → 7.7 → 28 → 284 d.
  - With the shape free, the wall is the design driver; the §10 counting estimate (×1.5 at 14.5°) was optimistic.
  - Cone rule: accepted leptons fly at ≥ 48.6° to the beam axis, so thick material is harmless inside r < 1.1·|z|.
- Deck rebuilt and deployed: site commit e3c024e. Only `notes/lnl-x17-feasibility.html` was rsynced to EOS, because another
  session had uncommitted site work (same-chamber-pairs, mx17-feedback-and-ions, mx17-response-chain), which was left
  untouched. The next full `deploy-eos.sh` will also push whatever that session has committed by then.

**Next steps:**
1. Dylan: review the n_TOF comparison table and the "lessons" slide before Thursday.
2. Confirm SiPMs per bar end (160 or 320 channels); update `pitch_slides.daq_slide` if 320.
3. Ask LNL for the beam-line and chamber drawings; run Geant4 (L5-type) with them, and a no-wall run.
4. Bench-test a 5 cm plate (response and timing).

**Gotchas:**
- **The SiPM channel count is open.** Dylan said 80 per wall / 320 in all; trigger_scint assumed 1 SiPM per bar end
  (160). The DAQ slide shows both. Confirm.
- The n_TOF column of the comparison table cites nTof_x17 STATUS/OCTOBER/IPC_MISSING as of 2026-10-12. "No X17 result
  yet" is the analysis status, not a final verdict.
- `lnl_smear_nd.py` monkeypatches `lnl_nd.kvary`. Cosmics (no truth angle) are not smeared.

**Key files:** `lnl/deck/pitch_slides.py`, `lnl/sim/lnl_smear_nd.py`, `lnl/out/nd/smear_scan.csv`, `lnl/FEASIBILITY_SIM.md` §15.

### Earlier the same day: the 3D fit is the reference in `reach_geant.csv` (§14.5)

Still open from it: the 441 keV run and the mass scan (look-elsewhere) in `lnl_nd.py`; a bench test of a 5 cm plate.

**Goal (Dylan):** deploy the §14 deck, then make the θ×|y|×E_sum fit the reference in `lnl_geant.py`.

**Done:**
- **Site deployed** (site 6779af0): the deck with slides 25–27, and `facilities/lnl.html` (1.0 / 17 d, a "Fit in three
  variables" paragraph). Dylan's uncommitted `mx17-response-chain` edits were stashed for the deploy and restored,
  still uncommitted.
- **`lnl_geant.py`:** `add_nd()` writes `days_3d`, `S3d_per_day`, `B3d_per_day` and `esum_3d` into
  `reach_geant.csv`. They are on the REF_LEVEL rows of as built and big plastics, for every scenario, current and
  mass. `summary.json` gets a `reference` block. `--nd` recomputes only these columns on the existing CSV.
- **`lnl_nd.py`:** `collect()` takes `mx` (signal mass) and `live`. New `reference_days()`, `REF_*` constants and
  `load_windows()`.
- **The ATOMKI 2016 anomaly row reproduces §14.3:** 1.00 d (big plastics) and 17.0 d (as built). The old columns are
  byte-identical (checked with pandas). Write-up: `FEASIBILITY_SIM.md` §14.5; README "read this first".

**Not done:**
- The deck's "Statistics alone" reach slide (11) and `lnl_week.py` still read the old counting / ideal-energy
  columns. The cover already quotes the 3D numbers. Switching slide 11 to `days_3d` (it is within 6–25 %) is an
  optional next step.

**Gotchas:**
- Run with `LNL_SEL=<absolute path>/lnl/sim/sel_v3` and BLAS threads capped. A relative `LNL_SEL` breaks if you `cd`.
- `lnl_nd` imports `lnl_calo`, which monkeypatches `lnl_geant._load` at import. `add_nd` imports it lazily, at the
  end of `main()`, and `reference_days()` resets the response to 'ideal' afterwards.
- The `reach_geant.csv` base columns are still from the 2026-10-08 run on the old `sel/` tables. `--nd` did not
  rerun them.

**Key files:** `lnl/sim/lnl_geant.py` (`add_nd`, `print_reference`), `lnl/sim/lnl_nd.py` (`reference_days`),
`lnl/out/geant/{reach_geant.csv,summary.json}`.

## Facilities 3D viewers: label stacking fix — updated 2026-10-13 (dylan-MS-7C84)

**Resume:** done and confirmed working by Dylan; nothing further unless a viewer is added (reuse `dropLabels`).

**Goal:** labels in the facilities 3D viewers stacked up on every view/tab change.

**Done:**
- Cause: three.js CSS2DObject removes its DOM element only when removed directly from its parent; labels sit inside
  the `world`/`events` groups, so `scene.remove(group)` leaked them. Added `dropLabels(group)` before each
  `scene.remove` in `ill/viz/ill_beams_3d.html` and `lnl/viz/lnl_setup_3d.html` (pushed to main) and the site copies
  `facilities/` + `pages/facilities/` in dylan-cern-site (commit 416d546, pushed). Confirmed working by Dylan.
- `lnl-run-animation.html` uses canvases, no change needed.

**Gotchas:** any new viewer with CSS2D labels in a rebuilt group needs the same helper. dylan-cern-site had
unrelated uncommitted edits (`notes/mx17-response-chain.html`, `sw.js`) that were left alone.

## LNL §14: single-arm trigger, realistic calorimetry, 3D fit — updated 2026-10-12 (dylan-MS-7C84)

**Resume:** make the θ×|y|×E_sum fit the reference in `lnl_geant.py`.

**Site deployed 2026-10-13** (site commit 6779af0): the deck with slides 25–27 is live at `notes/lnl-x17-feasibility.html`.
`facilities/lnl.html` now quotes 1.0 d / 17 d and has a "Fit in three variables" paragraph with a table. The §13
pair-mass paragraph is marked "ideal Geant4 energies". The "site NOT deployed" step below is done.

**Goal (Dylan):**
1. Design for taking all single-arm triggers, with a prescale always available.
2. Realistic calorimetry from what n_TOF measured. Is more n_TOF analysis needed?
3. Do the energy variables give a 2D/3D fit with more discovery power, and robustness against an
   imprecise background spectrum?

**Done** (`lnl/FEASIBILITY_SIM.md` §14, §0 update, README "read this first"; deck slides 25–27 "Trigger",
"Calorimetry", "2D fit"; the cover, record and closing now quote the 3D numbers):
- **sel_v3 re-merge.** `lnl_merge.py` now keeps per-arm `E_sipm_a`, `E_plast_a`, `E_ls_a` (and `sg_E_*`).
  44 condor merges went to `$E/sel_v3` (L1–L4, L7). Local copy: main checkout `lnl/sim/sel_v3`, symlinked in
  the worktree. Run with `LNL_SEL=lnl/sim/sel_v3`.
- **Trigger** (`lnl/sim/lnl_trigger.py` → `out/trigger/`):
  - logic: PAIR (≥ 2 legs) never prescaled; SINGLE (≥ 1 leg) prescaled 1/P; a clock trigger;
  - P = 1 up to 2–4 µA, 91–98 % live;
  - cosmic MIPs give each arm's gain to ~1 %/h even at P = 10.
- **Calorimetry** (`lnl/sim/lnl_calo.py` → `out/calo/`): a per-layer response anchored on n_TOF C1/C4 and
  the scint-stack per-cell maps. The face term is 4–5 % (arm B 9.5 %), found this session. The per-arm gain
  nuisance is in `lnl_syst.py` (`PRIOR_G`, `gain_var`). The E_sum window is re-optimised per response.
  - Big plastics: 0.83 → 1.4 d (calibrated), 2.4 d (n_TOF-quality), 5 d (poor plates).
  - As built: 8 → 35 d (liquid repaired), 190 d (liquid as at n_TOF), 490 d (no liquid). The floor is
    ~3 weeks even with a perfect liquid (`ls_scan.csv`).
  - Gains cost ≤ 15–25 % even at σ_g = 10–20 %.
- **N-D fits** (`lnl/sim/lnl_nd.py` → `out/nd/`): an event-level Fisher in which the structure (Gaussian
  process) is defined on the events in θ, m_ee, (θ, |y|) and (θ, E_sum), so that every analysis sees the
  same background error.
  - Calibrated response, θ × |y| × E_sum: **1.0 d big plastics, 17 d as built**. m_ee alone gives 1.7 and
    41 d.
  - Under the worst structure (5 %, ℓ/2, in m_ee): 3D 1.2 / 21 d against m_ee alone 3.1 / 529 d.
  - The 2D/3D fits are stable between MC halves (≲ 10 %); the angle-only fits swing ×2–3.
- **n_TOF question answered:** no more n_TOF analysis is needed. The open numbers need bench tests: the
  5 cm plate response, and a repairable liquid. An optional cheap check is to split the 2 cm bar's 19 %
  MIP width into photostatistics and path terms.

**In progress / where it stopped:**
- Everything is committed and pushed to `main`. **The site is NOT deployed:** this session (a worktree) could not
  run git in dylan-cern-site, and deploying from a stale checkout regressed a note before. To do:
  `cd ~/PycharmProjects/dylan-cern-site && git pull --ff-only && python scripts/add-note.py
  <x17_facility_search>/lnl/out/lnl-x17-feasibility.html --slug lnl-x17-feasibility --force --deploy`.
  Also hand-edit `pages/facilities/lnl.html` (it still quotes 0.83 / 8.0 d), then commit the site.

**Next steps** (FEASIBILITY_SIM §14.4):
0. Site deploy (above).
1. Bench test of a 5 cm plate.
2. Decide on as built: a repaired liquid gives ~3 weeks at best.
3. Make the 3D fit the reference in `lnl_geant.py`, and add the 441 keV run and the mass scan to
   `lnl_nd.py`.
4. More as-built IPC MC.
5. Fluorine singles on LiF (ask).

**Gotchas:**
- **Cap BLAS threads** (`OMP_NUM_THREADS=4` etc.) when running two `lnl_nd.py` in parallel. Uncapped,
  the load hit 40 on 16 cores and each fit went from ~2 s to minutes.
- **`pkill -f <pattern>` kills your own shell** if the pattern appears in the command line. Use
  `ps -eo pid,args | grep "[l]nl_nd"`.
- **Re-rsync with `--checksum`.** An rsync started before a merge job finished left a truncated npz
  (BadZipFile).
- In the as-built "LS off" variant of `lnl_geant`, E1/E2 still contained the liquid; only Esum dropped
  it. `lnl_calo` does it consistently.
- `lnl_nd.py` reads the per-response E_sum windows from `out/calo/resolution.csv`, so run `lnl_calo.py`
  first.

**Key files:** `lnl/sim/lnl_{trigger,calo,nd}.py`, `lnl/sim/lnl_syst.py` (gain nuisance),
`lnl/sim/lxplus/lnl_merge.py`, `lnl/deck/calo_slides.py`, `lnl/out/{trigger,calo,nd}/`.

## LNL §13: L7 IPC statistics, γ* anisotropy, event mixing, the pair-mass fit — 2026-10-12 (dylan-MS-7C84)

**Goal (Dylan):**
- sync the laptop;
- do the four next steps of §12;
- add a slide explaining the |y| cut: how it correlates with the background, where the statistics go,
  and whether it is offline.

**Done:**
- **Laptop sync.**
  - Merged the unpushed dylan-Yoga branch `worktree-lnl-slides-13-16` ("Configs" and "One week" slides,
    `lnl_week.py`; its study became §11, so the systematics study is §12).
  - Committed Yoga's newer `mx17-detector-paper-status` note (10-10) to the site. My earlier deploy had
    regressed it; it is restored and deployed.
  - Yoga's site checkout was reset to master; its old diff is saved in `~/site-uncommitted-backup-2026-10-12.patch`
    on Yoga.
  - Both repos are pulled on Yoga.
- **L7 IPC samples** (`--ipc-min-open 70`, MX17_Full_Geant `lnl` bc4cd6c, pushed). 172 condor jobs, ~0.9 TB in
  `$E/L7/`, merged to `$E/sel/L7_*`. They agree with L2 (§13.1). The merge now keeps the truth momenta
  (`lnl_merge.py`; `lnl_pipe.sh` takes `SEL=` for re-merges into `$E/sel_v2/`).
- **γ* anisotropy** a₁ ≈ 1.0 (Zahnow 0°/150°) and a₂ = 0.36 (Hayes et al. 2021): P₁ cancels, P₂ reshapes
  the IPC by +3 to +10 %. They are fit nuisances.
- **Event mixing** (`lnl_mixing.py`): singles mixing gets the local acceptance structure to 1–2 %, but the
  tilt is wrong. A single-arm trigger is needed.
- **The pair mass** m_ee = W√((1 − y²)(1 − cos θ)/2) as the fitted variable. Robust result (2 % structure
  + in-run controls): **0.83 d big plastics, 8.0 d as built**. The θ fit with |y| < 0.3 gives 1.2 / 17 d.
- **Slides** 18–24: new "Why |y|" (S/B map with the iso-mass line, |y| in the window, the cut scan;
  offline), "Mass fit" and "Checks"; ladder with m_ee columns. The cover and record slides now quote m_ee.
- **Animation:** angle / angle |y| < 0.3 / pair mass views (`viz/export_anim_data.py`).

**Next steps:** `FEASIBILITY_SIM.md` §13.6:
1. a per-arm gain nuisance;
2. m_ee as the reference in `lnl_geant.py`;
3. re-time L2 E1 or retire L2 for the IPC;
4. a mass scan with the look-elsewhere effect;
5. ask whether the DAQ can take a prescaled single-arm trigger.

**Gotchas:**
- `lnl_syst.py` needs `LNL_SEL` pointing at a directory with `sel/` overlaid by `sel_v2/`; locally that is
  `lnl/sim/sel_all` (symlinks; rebuild with a loop over both dirs).
- The L2 E1 tables have no arm times, so TOF never applied to them.
- `lnl_geant.kde_hist` drops negative weights. Use `lnl_syst.kde` for signed weights.
- `ssh` inside a `while read` loop eats stdin. Use `ssh -n`.

**Key files:** `lnl/sim/lnl_syst.py`, `lnl/sim/lnl_mixing.py`, `lnl/deck/syst_slides.py`,
`lnl/viz/export_anim_data.py`, `lnl/FEASIBILITY_SIM.md` §13.

## LNL §12: is the significance real? Shape systematics, |y| cut, controls — 2026-10-12 (dylan-MS-7C84)

**Goal (Dylan):** the claimed significance sits on a peak you can't see by eye. Was the background assumed
known perfectly? Are ATOMKI's peaks raw data? Do they have less scattering? Do all four follow-ups and
put them in the slides.

**Done** (write-up `lnl/FEASIBILITY_SIM.md` §12, a new §0 preamble, README "read this first"):
- `lnl/sim/lnl_syst.py` → `lnl/out/syst/`. Local, about 10 s, from the `sim/sel` tables.
  1. **ATOMKI at truth level.** Their Fig. 4 was digitised: +26/35/21 % at 135/145/155°, i.e. S/B ≈ 0.3.
     - The data are acceptance-corrected and the IPC is a fitted simulation; their scattering is like ours.
     - Their |y| ≤ 0.5 cut gives ×2 in S/B and the 23 % E1 share ×1.7.
     - With their cuts and mix, our generator needs R ≈ 1.2×10⁻⁵ to match their figure.
  2. **Symmetric cut** |y| = |E₁−E₂|/(E₁+E₂) from the arm energies. At |y| < 0.3 it keeps 69 % of the
     X17 and 42 % of the background, so S/B goes 7 → 18 %.
  3. **Fisher fit with nuisances.** Each row adds freedom:
     - M1/E1/γ₁ normalisations free;
     - resolution ±10 %, E scale ±2 %;
     - an acceptance cubic;
     - Gaussian-process "unknown structure" δ (ℓ = 10°).
  4. **Controls.** In-run: asymmetric pairs and the γ₁ side band, sharing the structure (δ/2 or 1 %
     transfer, ±5 % category norm). Also a 441 keV run.
- Results:
  - **all pairs with 2 % structure:** big plastics 1.2 → 26 d, as built 16 d → 1500 d;
  - **|y| < 0.3 + in-run controls:** big plastics 1.1 d, as built ~20 d.
- **Deck** (`lnl/deck/syst_slides.py`, slides 17–20: ATOMKI bump, Symmetric pairs, Systematics, Controls).
  - The cover, reach, budget, scatter-stack, record and closing slides were reworded to the robust numbers.
  - Record: R₃σ(30 d) = 3/Z₃₀ × R_ATOMKI.
  - The deck is rebuilt and **deployed**: notes/lnl-x17-feasibility.html, plus a new "Is the significance
    real?" section in facilities/lnl.html and the facilities index verdict. Site commit 217ee59 is on
    `master`.
  - Local checkouts of both repos need `git pull --ff-only`. The work was done in worktrees.

**Next steps:**
1. **L2 IPC ×20** on lxplus (M1/E1 18.15 and 17.64, as built and bigP). As built has only 12 M1
   events in 130–160° at |y| < 0.3, so the as-built robust number is indicative.
2. An event-mixing acceptance check in the Geant4 tables (target ≲ 2 % in θ).
3. A Zhang–Miller IPC as an alternative template: its difference from Born measures δ.
4. Put |y| < 0.3 in `lnl_geant.py`'s reference selection and in `viz/lnl_run_animation.html`. The
   animation still shows the statistics-only all-pairs days (15.4 / 1.18 d).

**Gotchas:**
- Priors on a polynomial or on the scales never cap Z, because the signal-free bins pin them. Only
  peak-scale structure (the GP) gives a floor. ℓ = 5° is the dangerous "edge-like" case for all pairs.
- `lnl_syst.py` imports `lnl_geant` and needs `lnl/sim/sel` (`sim/fetch_sel.sh`).
- The dylan-Yoga site checkout may still hold the uncommitted "Configs" / "One week" deck edits. This
  rebuild of `lnl-x17-feasibility` does not contain them. Merge by hand if they are wanted.

**Key files:** `lnl/sim/lnl_syst.py`, `lnl/out/syst/`, `lnl/deck/syst_slides.py`, `lnl/FEASIBILITY_SIM.md` §12.

## ILL §14: ³He(n,γ) background + single-arm trigger — 2026-10-08 (dylan-MS-7C84)

**Goal:** the two loose ends of §13. Why G (³He(n,γ) fakes) was 143/cycle in the CFRP fit and 0 in the
tube fits. And what a single-arm trigger would cost and record (Dylan's open question: the unbiased
0–180° spectrum).

**Done** (write-up `ill/FEASIBILITY_SIM.md` §14; README "read this first" updated):
- **G resolved:** it is one C1g MC event, at a 40° chord with Esum 13.07, outside the 60–180° window.
  It passes the segment + collinearity cuts in 9 % of rng draws. The draws depend on the variant
  because one rng is shared across tables. Effect ≤ 1 %. Two-arm ³He(n,γ) < ~1000/cycle at 1.9e10
  (90 % CL, before segments). `sim/lxplus/gdiag.py`.
- **Single-arm trigger** (`sim/lxplus/single_arm.py`, condor 4406828; outputs in
  `sim/analysis_v3/single_arm/sa_*.csv`):
  - The trigger is a leg plus E_arm > T, ORed with the two-arm trigger.
  - At T = 10 MeV it costs ≤ 1 % on the reach at 6e10 with the tube (2 % for CFRP).
  - At T = 0 the rate is 57–230 kHz, so a bare leg trigger is impossible. At T = 8 it costs ×1.07 (tube)
    or ×1.6 (CFRP).
  - Same-arm IPC is ~10× the two-arm IPC (M1 8.5e5 / E0 8e4 per cycle at T = 10), all below 60°.
    X17 ≈ 0 in one arm.
- **³He(n,γ) same-arm fakes** (`sim/lxplus/he3ng_samearm.py` on the C1g HitTree, condor 4406831; parts
  in `$E/analysis/he3ng_samearm/`):
  - Two tracks ≥ 5 mm apart: 9.0e5 (T = 10) and 3.4e5 (T = 13) per cycle, about 1:1 with the
    same-arm IPC.
  - About 45 % are conversions or Compton electrons in the Al end cap. C1g uses the as-is geometry.
- **`conservative.py --ipc-known`** (fixes M1/E0 in the Fisher fit; condor 4406830 →
  `cons/walls_ipck_*_e14.csv`): **13–17 % better reach** at most. Tube + mylar 5.3e-3 → 4.6e-3
  (×3.2 → ×2.8 from ⁸Be).
- `ill/single_arm_trigger.py` → `ill/out/single_arm/{trigger_vs_T,theta_spectra,samearm_fakes}.png`
  plus `live.csv` and `yields.csv`.

**Not done:**
- Deck slides for §14; the deck and site are unchanged.
- Nothing is committed.

**Next steps:**
1. Rerun C1g with the CFRP cap + tube + Be 0.25, or run `--gamma-lines 20.578:1 --target cell` on the
   `lnl` branch (≥ 1e7 γ), to get the design's fake/IPC ratio. The as-is Al end cap dominates
   today's fakes.
2. A two-track vertex study: the fakes against the S1 same-arm IPC.
3. (ask) Can the n_TOF trigger form a per-arm analogue energy sum (SiPM + plastic + LS) at ~10 MeV?
4. If Dylan wants it, one deck slide "Single-arm trigger" after "Window & flight tube", then republish.

**Gotchas:**
- `single_arm.py`'s "two-arm" reference has no MM segment, occupancy or live-time cuts. Compare it
  only with the same-arm numbers from the same script, not with the fit's IPC counts.
- The neutron single-arm rates at T ≥ 10 rest on a few biased C1w events; "0" means < 1 MC event.
- The same-arm "two tracks" cut is truth-based: first gap hits of the two leptons (IPC), or of the two
  most energetic tracks (γ), ≥ 5 mm apart. It is not a reconstruction.
## LNL animated run page — updated 2026-10-10 (dylan-Yoga)

**Resume:** the animation is live at facilities/lnl-run-animation.html; pull both local checkouts, commit the pending deck edits.

**Goal:** (Dylan) try an animated page for the LNL study (beam, target, reactions, e⁺e⁻ through the arms), and put it on the site.

**Done:**
- `lnl/viz/lnl_run_animation.html`: standalone page with three linked canvases.
  - Beam line: a schematic, not to scale.
  - Event display: a 2D toy. Its acceptance is not the Geant4 one.
  - Opening-angle histogram: real data, Poisson-sampled from `out/geant/figures/geant_theta.csv`.
  - 3σ day from S/√B in the best window: 15.4 d as built and 1.18 d with big plastics (`summary.json`: 15.5 / 1.2).
- **Live:** `dylan-neff.web.cern.ch/facilities/lnl-run-animation.html`, linked from `facilities/lnl.html` (a new board-cta).
  - Deployed by rsyncing those two files only.
  - Site commit 9212f60 is merged into dylan-cern-site `master` and pushed.
- Also a private claude.ai artifact (same page): https://claude.ai/artifact/Dm1CXzANyeRnYjrQsfUX25

**Next steps:**
1. On dylan-Yoga, `git pull --ff-only` in both `x17_facility_search` and `dylan-cern-site`. The worktree session could not touch those checkouts.
2. Commit the pending site deck edits (see Gotchas), then run a normal `deploy-eos.sh`.
3. Optional: animate the energy sum, or add the 0.8 / 1.225 MeV off-resonance settings.

**Gotchas:**
- The dylan-Yoga site checkout had uncommitted, newer deck edits: the `lnl-x17-feasibility` note, with "Configs" and "One week" slides, plus `mx17-detector-paper-status`.
  - A full `deploy-eos.sh` from a clean clone would have overwritten them, so only the two files were pushed.
  - Commit those edits before the next full deploy.
- The θ spectra are inlined in the page. Re-export them by hand if `geant_theta.csv` changes.

**Key files:** `lnl/viz/lnl_run_animation.html`; site `pages/facilities/lnl-run-animation.html`, `pages/facilities/lnl.html`.
## LNL deck: slide 13 to one placement, slide 16 to one week with the significance spelled out — 2026-10-09 (dylan-Yoga)

**Resume:** read `lnl/FEASIBILITY_SIM.md` §11.

**Goal:** (Dylan)
- Slide 13: drop the no-SiPM-wall and closer placements. Show only the plastics where the bars are
  now, with a line at the optimum.
- Slide 16: three days did not look convincing with that smearing. How is the significance
  computed? Redo it per week so the smeared bump shows.

**Done:**
- Slide 13 ("Plastic size"): only R = 41 cm, with the SiPM wall kept for the TOF. The optimum line
  is at 77.5 cm (1.19 d); the curve is within 10 % of it from ~65 cm. Other placements are dropped
  from the slide; their rows stay in `days_vs_size.csv`.
- `lnl/sim/lnl_week.py` → `out/scatter/week.csv`, `week_z.csv`, `figures/scatter_week.png`.
  - One week of pseudo-data at 1 µA, measured angle, plus the excess over the IPC.
  - Z against time for three reach methods, and with an IPC shape systematic.
- Slide 16 ("One week") replaces the per-day stacked plots. The answer to "how":
  - The 1.2 d is Asimov counting, S/√B, with the IPC known exactly.
  - The template fit with one IPC norm free: 1.6 d. With M1/E1/γ₁ free: 3.7 d.
  - **S/B ≈ 7 %, so ε = 2 % on the IPC shape caps Z at 3.5σ.**
- `FEASIBILITY_SIM.md` §11, §8 item 9; README read-first and file map. Deck rebuilt and republished.
- Follow-up (Dylan): a new slide 13 ("Configs") draws n_TOF as built (2× 20×30 cm bars) against the
  77.5 cm plates. It is to scale, from the SimConfig constants: a view along the beam and one arm
  face-on. Every later slide moved up by one: plastic size is now 14, scattering 16, one week 17.
  Confirmed with Dylan that the SiPM wall stays (it gives the TOF) and the big plates replace the
  bars at ~41 cm.

**Next steps:**
1. Quantify the IPC shape systematic: what the sidebands, E_sum slices and off-resonance points
   constrain. Also the M1–E1 interference generator (§8 item 4).
2. The look-elsewhere effect for a mass scan (not in any number yet).

**Gotchas:**
- Headless Chrome screenshots of the deck come out blank via `#anchor`. Copy the HTML with
  `.frame:not(:has(#<id>)){display:none}` injected, then screenshot that copy.

**Key files:** `lnl/sim/lnl_week.py`, `lnl/deck/plastics_scatter.py`, `lnl/out/scatter/week*.csv`.

## LNL pitch: why big plastics win, plastic size, chamber scattering — 2026-10-09 (dylan-Yoga)

**Resume:** read `lnl/FEASIBILITY_SIM.md` §9–10. The deck has 4 new slides (12 "Why big", 13 "Plastic size",
15 "Scattering", 16 "Scattering 2").

**Goal:** (Dylan) make the pitch solid. (1) Show where the big-plastic speed-up comes from, plus days against the
size of a square plastic, with the footprint and the distance taken into account. (2) Estimate the scattering in
the carbon chamber, and draw the peak widening against no scattering, as for the n_TOF capsule.

**Done:**
- `lnl/plastic_size.py` (≈3 min; `--figs` rebuilds the figure only) → `lnl/out/plastics/`.
  - A geometric toy calibrated on the Geant4 pair-tags. Analytic stand-in.
  - Gain ×15 in S and ×14 in B, so it is acceptance.
  - It saturates at ~65–70 cm at R 41 cm and ~55–60 cm at R 35 cm. The footprint never binds first.
  - The SiPM wall now cuts ~10 % per lepton.
  - Robustness: a 3 MeV threshold or less scattering moves the relative days by < 7 %.
- `lnl/sim/lnl_scatter.py` → `lnl/out/scatter/`. Geant4 truth vs reco on the same events.
  - CFRP σ68 4.6°; the wall costs ~11 % in time.
  - Al 1 mm: 1.60 d against 1.20 d.
  - Layer budget: the chamber wall is the dominant term; the MM window/cathode cost nothing (lever).
- Deck slides via `lnl/deck/plastics_scatter.py`, hooked in `build_deck.py`. Merged into `main`.
- **Published:** the deck is live at notes/lnl-x17-feasibility.html (dylan-cern-site 9bacb91, deployed 2026-10-09).
  - The dylan-Yoga site checkout was ~40 commits behind; it is now synced with `master`.
  - Its never-committed `dream-pedestal-check-2026-10-05` note was committed (ec0f132) and indexed.
- Documented in `FEASIBILITY_SIM.md` §0 items 5–6, §8 items 6–8, §9–10; README read-first + file map.

**In progress / where it stopped:** nothing running. `/facilities/lnl.html` is unchanged; the headline numbers did
not change.

**Next steps:**
1. A Geant4 oversized-plate run at R ≈ 35 cm, to replace the toy curve (`--big-plastic` was made for this).
2. A Geant4 run with no chamber wall (or CFRP 0.2 mm), to replace the 3.5° model floor.
3. Ask: can a plastic-only leg (no SiPM wall) give the TOF? It would gain ~1.4× more X17.

**Gotchas:**
- The toy's absolute IPC pair-tag is ~40 % low. Use it for ratios only.
- Background-job sessions isolated in a worktree cannot run git in other repos; clone them into the job tmp.

**Key files:** `lnl/plastic_size.py`, `lnl/sim/lnl_scatter.py`, `lnl/deck/plastics_scatter.py`, `lnl/out/plastics/`,
`lnl/out/scatter/`.

## LNL ⁸Be Geant4 feasibility — updated 2026-10-08 (dylan-MS-7C84)

**Resume:** read `lnl/FEASIBILITY_SIM.md` §0. The LNL Geant4 feasibility is done. What is open are
the questions for the collaboration (SiPM-wall timing, LS readout), the emails, and the IPC shape.

**Goal:** Dylan (going to bed): follow through the LNL feasibility on lxplus overnight (condor only, outputs
on EOS), chase threads of interest, republish when the numbers change.

**Done:**
- **Runs** (all finished, `/eos/experiment/ntof/data/x17/lnl/`, 2.0 TB raw ROOT):
  - L1/L2 as built, then the same with big plastics (`_bigP`: `--big-plastic 75 75 5 --no-ls
    --sipm-readout 20 0`) and with 20 SiPM bars (`_sipm20`);
  - L3 γ lines: 8Be (+`_x20` 2×10⁸ γ; `_bigP_x10`), 19F, 7Li, `gam_Al28` (new line set);
  - L4 cosmics, one live day, as built and big plastics;
  - L5 chamber/backing scan; L6 E0 6.05.
- **MX17_Full_Geant `lnl`:** merged `trigger_plastics` (a424eed), frozen binary
  `bin/mx17_full_sim_lnl_a424eed`, `gam_Al28` added to `submit_lnl.py`. Pushed.
- **Pipeline** `lnl/sim/lxplus/`:
  - `lnl_reduce.py` = `ill_pairs` reduce + `seg_reduce`;
  - `lnl_time.py` = per-arm scintillator times;
  - `lnl_merge.py` → `$E/sel/<run>_<sample>_sel.npz`;
  - `lnl_pipe.sh reduce|time|remerge|merge|status`, idempotent.
  - lxplus copy: `/afs/cern.ch/work/d/dneff/git/x17_lnl/analysis/`.
- **Analysis** `lnl/sim/lnl_geant.py` (`--figs` rebuilds the figures only) → `lnl/out/geant/`.
  `lnl/sim/fetch_sel.sh` copies the tables to `lnl/sim/sel/` (gitignored, ~100 MB).
- **Result:** 3σ at R(ATOMKI), Li₂O 300 at 1.10 MeV, 1 µA:
  - as built: 15–24 d (counting – template fit);
  - big plastics: 1.2–1.6 d.
- **Findings:**
  - pair-tag is 3.3 % as built (EPS_REST was really 0.084), 23 % with big plastics;
  - E_sum removes γ₁ (with LS, or with big plastics);
  - **cosmics need an upper E_sum edge plus 3° segments or a ≤ 0.4 ns TOF**, because 15° segments fail;
  - EPC, accidentals and DAQ are negligible;
  - CFRP chamber (an Al wall doubles σ_θ);
  - the E0 6.05 line is invisible to the trigger.
- **Written up:**
  - `lnl/FEASIBILITY_SIM.md` (new);
  - `lnl/README.md` read-first block;
  - pointers in `ESTIMATES.md`, `GEANT_PREP.md` §0 and `lnl_rates.py`.
- **Published:**
  - the deck was rebuilt with 8 new or replaced slides and is live at notes/lnl-x17-feasibility.html;
  - `/facilities/lnl.html` was updated and deployed (dylan-cern-site 1977ee7).
- **Basics appendix** (2026-10-08, Dylan is new to the channel): deck slides 15–33, built by
  `lnl/deck/appendix.py` from `lnl/appendix_calc.py` → `lnl/out/appendix/*.csv`. It covers the Van de Graaff,
  energy/time structure, p vs n, the rate chain, thin vs stopping targets (main slide 6), why γ₀ is the
  unit, the chamber + Highland model fitted to L5 (**analytic stand-in** for walls not simulated), level
  schemes, E* bookkeeping (C1a–c: Q + ⅞E_p, any E_p vs resonances, X17 leverage E*−m), M1/E1/E0, the
  bump, boost (β 0.006 → 0.3°), edge vs E_p, off-resonance (a test, not more yield), glossary. Republished.

**Next steps:**
1. Ask the collaboration:
   - the SiPM-wall time resolution (TOF needs ≲ 0.4 ns);
   - whether the LS can be read at LNL. Without them: 19 d, and no cosmic E_sum edge.
2. Emails (Dylan's): LNL (Selva/pacbeams), T. Marchi.
3. The IPC shape: the fit with M1/E1 free is ×2.3–3 slower. Add Zhang–Miller M1–E1 interference, or plan
   0.8 MeV E1-shape runs.
4. Optional: rerun cosmics for `_sipm20` (it uses the as-built cosmics now); ¹¹B and beam-halo sims.
5. Optional: a Geant4 L5-type run of the improved chamber options (CFRP 0.2 mm, wider tube, Be) to
   replace the appendix's Highland stand-in, and see whether ~4° shortens the days.
6. **EOS:** the 2 TB of raw ROOT in `…/x17/lnl/L*/` can go once the tables are final. Only the `sel/` and
   `parts_*` are needed. Ask Dylan before deleting.

**Gotchas:**
- `condor_submit` from an EOS cwd hangs or fails. `lnl_pipe.sh` now `cd`s to the AFS job dir.
- The background templates are KDE-smoothed (5°). Without it, empty IPC bins faked a ×50 Fisher gain.
- The pointing cut D is calibrated to 90 % of X17 segments (135 mm at 15°, 57 mm at 3°), not from the
  nominal resolution.
- `pkill -f <pattern>` matches your own shell command. Use `pgrep` with a bracket trick, or a PID.
- dylan-cern-site still has the earlier session's uncommitted `x17/analysis.html`, `pages/x17/analysis.html`
  and `sw.js` (not mine; left alone). `ill/sim/lxplus/gdiag.py` and two `walls_CFRP_*.csv` here belong to
  the ILL session (uncommitted, left alone).

**Key files:** `lnl/FEASIBILITY_SIM.md`, `lnl/sim/lnl_geant.py`, `lnl/sim/lxplus/lnl_pipe.sh`,
`lnl/out/geant/reach_geant.csv`, `lnl/deck/build_deck.py` (+ `appendix.py`; run `lnl/appendix_calc.py` first
from `lnl/` with the nTof_x17 venv python, then `deck/build_deck.py`, then `add-note.py … --force --deploy`).

## ILL rate walls, He flight tube, entrance window — updated 2026-10-07 (dylan-MS-7C84)

**Resume:** condor sims (G1_tube{Be,Be25,My}) were running; finish the reduce → merge → fits chain, then write §13 + 2 slides.

**Goal:** Dylan's question after the §12 verdict: is the reach pure statistics, can more beam / pressure /
target size buy it back, or do pile-up and accidentals cap it irreducibly? And before calling it impossible,
chase the engineering levers: a He flight tube (../he4_bag) and a better or thinner entrance window than 0.5 mm Be.

**Done (answers so far, from a surrogate, not yet the real fit):**
- **Pressure buys nothing.** G1 is already opaque at 1 bar (99.5 % absorbed), and the yields per absorbed n
  don't depend on pressure. Pressure only shortens the source (≤ 13 % via the vertex).
- **There is plenty of beam.** R_MAX 1.9e10 is just the Ø2 cm spot (`out/beam_spot.csv`): Ø4 cm gives 7.5e10,
  Ø5 cm 1.2e11. S1s says a 25 mm spot radius costs < 5 % acceptance and +0.3°.
- **Three rate walls.** `ill/sim/rate_surrogate.py` is a counting stand-in for the Fisher fit, calibrated on
  the §11 oracle rows; it reproduces as-is to 1.5 %.
  1. **Accidentals ∝ R²·2τ.** As is, with infinite beam, a perfect MM and no dead time, the reach never goes
     below 1.1e-2 (no panel, Esum > 13) or 7.7e-3 (panel, > 14). The ceiling ∝ √(2τ·singles²).
  2. **MM occupancy, exp(−2·occ).** occ 0.22/arm at 1.9e10 caps the useful rate at ~3.3e10 (+7 %). From the
     X17 shifts in the budget rows, the occupancy split is: Al frames ~35 %, Cu ~24 %, air ~15 %,
     PCB/Kapton ~10 %, Be ~7 %. So it comes from stray neutrons captured in the detector.
  3. **DREAM, 298 µs/trigger** (trigger ≈ 7.9e-9/n·R + 2.8e-19·R²). With 1 and 2 fixed: optimum 1.1e11,
     live 0.44, floor 3.7e-3.
  - Only with all three gone is it pure 1/√R: ⁸Be's 1.6e-3 needs ~3e11 n/s (15× today).
- **Window options** (`ill/window_options.py`, analytic). The 0.5 mm Be was sized for 2 bar (G3–G6); G1 at
  1 bar with He behind it has no Δp. **25 µm mylar has no line above 4.95 MeV (C; H gives 2.2).** Any pair
  with a window capture then needs an ≥ 8 MeV partner, and once the air is gone only ³He(n,γ) remains.
  It scatters ~1 % of the beam (bound H, my estimate) against 0.3 % for Be. Kapton contains N (10.83): avoid.
  Be 0.25 mm halves the singles. Al is worse.
- **Geant: `--flight-tube He[:r]`, `--tube-wall Mat:mm` (default Al:1), `--tube-window Mat:mm` (default
  Mylar:0.025)** on MX17 `ill_ring` (commit 2c10ca1, pushed). A He tube runs from the gun plane + 1 mm to the
  cell's upstream face. Overlap-checked. Binary: lxplus `MX17_Full_Geant/bin/mx17_full_sim_tube`; the source
  was copied into the lxplus clone (it was identical to `ill_ring` HEAD beforehand).
- `conservative.py`:
  - `--rate-walls` (+ `--rmax`, default 2e12) writes every rate-grid point for 4 scenarios (as is,
    no Be+air, no ACC, IPC only) × 4 knob settings (MM occ + DREAM / MM ÷10 + 10 µs DAQ / no MM loss /
    no MM loss + no dead time).
  - `best_reach` gained `rates`, `daq_tau`, `occ_scale`, `curve`.
  - `acc_sources.volume` gained a "flight tube wall + window" class.

**In progress / where it stopped:**
- Condor sims submitted 2026-10-07 ~21:10, 10×1e7 each:
  - runs: `$E/C1/G1_tube{Be,Be25,My}` and `$E/C1w/G1_tube{Be,Be25,My}`, all G1 + CFRP ring/cap + He tube;
  - windows: Be 0.5 / Be 0.25 / Mylar 0.025;
  - C1w uses `--bias-wall 300 --bias-thick 20 --bias-air 100`;
  - none were finished at wrap-up.
- `walls` fits on the existing CFRP data (`$E/analysis/cons/walls_CFRP_e13.csv`, `walls_CFRP_e14.csv`) were
  running; the CSVs are written incrementally, so they are complete only once the log ends with `wrote`
  (`/afs/cern.ch/user/d/dneff/condor/ill/cons/walls/logs/*.out`).
- The local driver `ill/sim/lxplus/tube_chain.sh` (sims → submit_reduce_ill + seg_submit → merge_submit →
  cons_submit "tube" with bo_/e14_/walls_ jobs per variant) **died with the session**. Re-run it, or do its
  steps by hand. Careful: rerunning resubmits the reduce if the sims are done; seg_submit skips existing
  outputs, but submit_reduce_ill may not, so check `parts/` first and start from the right step.

**Next steps:**
1. Check the sims: `grep -l 'Run Summary' $E/C1*/G1_tube*/*_job*.log | wc -l` (60 = done). Then the reduce,
   merge and fits as in `tube_chain.sh`.
2. Compare the real fit with the surrogate on `walls_CFRP_*`.
3. For each variant, from the `bo_`/`e14_` budget and `walls_*`:
   - ACC (Be window, air, tube wall);
   - MM occupancy, from the X17 at fixed R;
   - trigger rate;
   - the best reach as is and per knob.

   Key question: does the tube + mylar make accidentals negligible, so the walls become MM occupancy and the
   DAQ? Check that the mylar's extra scattering doesn't add detector singles. G4_MYLAR uses free-gas H
   (S(α,β) only for Be/Al/C/Fe here), so Geant probably underestimates the H scattering by ~2×.
4. Write `FEASIBILITY_SIM.md` §13 "Rate walls and the window". Add slides "Rate walls" (reach vs R curves)
   and "Window & flight tube" after "blocking" in `ill/deck/build_deck.py`. Update "verdict"/"next" if it
   changes. Rebuild with the nTof_x17 venv python and republish (see the section below).
5. **Open design question (Dylan):** every number assumes a two-arm trigger: a per-arm SiPM×plastic
   coincidence in two *different* arms, and a 60–180° fit window. That hides the small-angle part of the
   opening-angle spectrum (both legs in one arm). Dylan would like the unbiased 0–180° spectrum. Study what
   a single-arm (or same-arm two-track) trigger costs: per-arm singles rate → DREAM dead time, and
   accidentals. The per-arm rates are already in `trigger_rates()`. This ties straight into wall 3.

**Gotchas / decisions:**
- The window class in `acc_sources` is still labelled "Be entrance window" even when the window is mylar.
  The label is kept so the scenario names, old CSVs and the deck still match.
- The occupancy model (any foreign MM hit in the 1 µs window kills the event) is pessimistic. A segment fit
  could likely tolerate an unrelated track, so wall 2 is partly a modelling choice.
- The tube wall is 1 mm Al (scattered neutrons → 7.7 MeV). If it shows up in the accidentals, try
  `--tube-wall CFRP:1` or a ⁶LiF lining.

**Key files & commands:**
- `ill/sim/rate_surrogate.py` — surrogate rate scan (reads `sim/analysis_v3/cons/{bo_ringCFRP,e14}.csv`).
- `ill/window_options.py` — window materials: captures/n by line, scattering.
- `ill/sim/lxplus/conservative.py --rate-walls` — the real rate scan (on lxplus via `cons_submit.sh`).
- `ill/sim/lxplus/tube_chain.sh` — the pipeline driver for the three tube variants.
- Copy results locally: `scp lxplus:$E/analysis/cons/{walls_*,bo_tube*,e14_tube*}.csv ill/sim/analysis_v3/cons/`.

## ILL conservative reach — wrapped up 2026-10-07 (dylan-MS-7C84)

**Status: done.** Write-up `ill/FEASIBILITY_SIM.md` §10–12; deck `ill/deck/build_deck.py` → live at
https://dylan-neff.web.cern.ch/notes/ill-x17-feasibility.html (slide 4 “Verdict”). No condor jobs pending.

**Result:** n_TOF hardware + ≤3° MM segments + 20° collinearity veto (no panel) + CFRP end cap → 1.2e-2
(3σ, 50 d). Accidentals left = Be window + air only; IPC floor 6.2e-3. In ⁸Be units: ×7.5 as is, ×3.8 with
zero background, ×2.7 for the 200 ps floor. Unpolarised, one cycle cannot reach ⁸Be's level.

**Follow-ups (none started):**
1. Theory: ask Viviani et al. for X17/γ at E_n ≈ 25 meV (hindered thermal M1 decides above/below ⁸Be).
2. Polarised ³He at PF1B (Tyrex-type cell + polarised beam): E0 suppression and J^π. Cell compatibility,
   polarisation, lifetime in beam.
3. Simulate the levers in `ill/sim/lxplus/conservative.py --budget`: an E0-removed oracle (floor ÷ ~1.6
   estimate) and an efficiency/containment scan (×4 containment → ÷ ~2 estimate).

**Gotchas:** local `python3` has no pandas; build the deck with
`~/PycharmProjects/nTof_x17/.venv/bin/python ill/deck/build_deck.py`. Publish with
`python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py ill/out/feasibility_deck.html --slug ill-x17-feasibility --force --deploy`.
Heavy work only as condor jobs; C1w jobs need ~14 GB. Scripts run from `/afs/cern.ch/work/d/dneff/git/x17_ill/analysis/`.

## trigger_scint — big-slab backgrounds at the ILL — updated 2026-10-02 (dylan-MS-7C84)

**Goal:** decide whether a large, thick (H-rich) trigger slab drowns the ILL
pair search in background, compared with the detector as built (P2 70×70×2,
P5 75×75×5, P5L/P5B = P5 + 2 mm ⁶LiF/B₄C wrap). The answer goes in
`trigger_scint/BACKGROUNDS.md`. Full run log: `trigger_scint/STATUS.md`
("Session 2" and "Session 2 restart").

**Done:**
- All TB Geant4 runs finished. Analysis done for asbuilt (air ×1, ×0.1) and P2.
  JSONs are in `trigger_scint/sim/bkg/`, and `bkg_figs.py` has been run on them.
- P2 result: no better than as built at Esum > 13 MeV (timing reach 1.6e-2 vs
  8.4e-3). That is expected: a 2 cm slab has as-built signal acceptance.
- Restart at 18:30: released the held P5_C1w reductions at 40 GB, and dropped
  4 truncated raw files (merged partially with `merge_partial.sh`).

**In progress / where it stopped (on lxplus926, nohup):**
- `x17_trig/pipeline_tb.sh`: P5L/P5B C1w reductions running (condor 4354874,
  4354876, 42 GB). P5_C1w reduction (4354038) has left the queue and should
  merge on the next pass.
- `x17_trig/analysis/run_bkg.sh P5 P5L P5B`: each geometry starts once its
  `.merged` markers exist and takes ~40 min. Output:
  `/eos/experiment/ntof/data/x17/ill/TB/analysis/{P5,P5L,P5B}[_air0.1].json`
  and `.log`.
- Expected done ~20:30–21:00 on 2026-10-02.

**Next steps:**
1. Check that the outputs exist. If the drivers died, restart them (commands
   in STATUS.md) and check `condor_q dneff -hold`.
2. `scp lxplus:/eos/experiment/ntof/data/x17/ill/TB/analysis/P5*.json trigger_scint/sim/bkg/`,
   then run `python trigger_scint/bkg_figs.py`.
3. Compare P2/P5/P5L/P5B with as built: reach vs gate G, trigger rates, MM
   occupancy, budget.
4. Write `trigger_scint/BACKGROUNDS.md`. Include the unsimulated hall-γ
   caveat (STATUS.md). Update README and the TRIGGER_OPTIONS recommendation,
   then log it on the x17 board.

**Gotchas / decisions:**
- C1w reductions need ~36 GB. The pipeline now asks 40 GB.
- The truncated raw files (P5_C1 job008, P5_K1 jobs 003/024/032) were not
  rerun. The merge normalises by summed N.sim, so they cost statistics only.
  `pipeline_tb.sh` keeps looping on those two directories, which is harmless.
- `lxplus989` and `lxplus926` can't be reached by name (host key); use `ssh lxplus` and work from AFS.

**Key files & commands:**
- `trigger_scint/bkg_reach.py` — reach model with pile-up (runs on lxplus).
- `trigger_scint/bkg_figs.py` — figures and tables from `sim/bkg/*.json`.
- `trigger_scint/sim/lxplus/{submit_tb,pipeline_tb,merge_partial,run_bkg}.sh` — copies of the lxplus drivers.

## ILL rate vs DREAM dead time — updated 2026-10-02 (dylan-MS-7C84)

**Goal:** check whether the DREAM DAQ, which reads full Micromegas waveforms for the
TPC tracking, limits the usable ILL absorbed rate. Dylan feared it would change
the reach by orders of magnitude.

**Done (analysis only; no change to the feasibility code yet):**
- **DREAM limits**, from `~/PycharmProjects/nTof_x17_DAQ/docs/REPORT_2026-07-28_pulser_daq_characterization.md`,
  `DAQ_OPTIMIZATION_SUMMARY_2026-07-23.md`, `CLOCK_RATE_SCAN_2026-07-23.md`,
  `CLOCK_WINDOW_RESULT_2026-07-24.md` and `METHOD_readout_window_optimization.md`:
  - The ceiling is ~83 MB/s **per FEU**, wire-limited. It is not set by IPD, host, network or disk.
  - RAW production point (20 samples × 60 ns = 1.2 µs, Hwm 1): **3.35 kHz max, τ ≈ 298 µs** per event.
    Readout is non-paralysable, one event at a time, so live = 1/(1 + f·τ).
  - τ scales linearly with the number of samples.
  - ZS reached 10.8 kHz at 32 samples on the pulser. ZS at real occupancy is unmeasured, and the
    `PedSub` double-subtraction question is still open.
  - The 20-sample window holds 95 % of the drift charge at 700 V drift.
- **Trigger rate per 10¹⁰ absorbed n/s**, G5 tables, from `ill/sim/trig_ladder.py`:

  | trigger | rate | X17 kept |
  |---|---|---|
  | bare SiPM 0.5 MIP, both arms | 5.6 kHz | 100 % |
  | + ≥ 1 plastic (n_TOF-like menu) | ~1.1 kHz | 99 % |
  | + plastic in both arms | ~110 Hz | 66 % |
  | arm energy > 1 MeV, each arm | 1.2 kHz | 95 % |
  | arm energy > 2 MeV, each arm | ~120 Hz | 91 % |
  | sum of the two arms > 8 MeV | ≲ 110 Hz | 100 % |

- **Live fraction** (cosmics ~16 Hz added):
  - 2 MeV per-arm threshold: 0.97 at 0.9e10 n/s, 0.93 at 1.9e10, with the 1.2 µs window.
  - Same threshold, 4.8 µs window: 0.87 and 0.78.
  - Bare SiPM trigger, 1.2 µs window: 0.40 and 0.24.
  - The n_TOF-like menu: ~0.78 at 0.9e10.
  - All fitted components scale with live time, so reach ∝ 1/√live.
- **Conclusion:** DREAM costs an O(1) factor, not orders of magnitude, as long as the hardware
  trigger cuts on arm energy at ~2 MeV.
  - With that cut: ~2 % in reach (1.2 µs window), ~7 % (4.8 µs).
  - Worst case, a bare trigger at 1.2 µs: ~×1.6 in reach.

**In progress / where it stopped:** answered in chat; not yet written into `ill/FEASIBILITY_SIM.md`.
That file and `ill/README.md` have uncommitted edits from another session, so they were left untouched.
Open question to Dylan: what drift window the ILL TPC needs (the study only went to 4.8 µs).

**Next steps:**
1. Add a DREAM live-time factor to `ill/sim_feasibility.py` `model()`: τ = 298 µs × n_samples/20,
   trigger rate per absorbed n from the menu. Then re-optimise the rate and redo `scan_v1`.
2. Run a larger **unbiased** C1 sample on lxplus to measure the trigger rate above 2 MeV per arm.
   It currently rests on one unit-weight Monte Carlo row.
3. In `ill/ill_rates.py`, set `DREAM_MAX_HZ` from 1e3 to the measured 3.35 kHz (RAW, 20 samples),
   scaled by n_samples.
4. Write it up as a new §10 in `FEASIBILITY_SIM.md`, plus a slide in the deck (`ill/deck/build_deck.py`).

**Gotchas / decisions:**
- The 5.5 kHz in FEASIBILITY_SIM §2 is the SiPM-only menu. It is not a realistic ILL trigger.
- A plastic-in-both-arms trigger loses 34 % of X17, because the leptons often miss the plastic.
  Use arm energy (sum of the arm's scintillators) or a two-arm sum instead.
- The ILL hall's ambient γ and fast-neutron rate is unknown (`ill/FACILITY.md`). It could raise the
  low-threshold singles above the Monte Carlo.

**Key files & commands:**
- `cd ill && PYTHONPATH=. python sim/trig_ladder.py` — the trigger ladder (uses local
  `sim/contracts/C1_G5` and `sim/s1test/G5_X17`)
- `ill/sim_feasibility.py` — reach model (no DAQ live time yet)
- `ill/beam_spot.py` — beam rate vs spot diameter (Ø2 cm ≈ 1.9e10 n/s)

## he4_bag — ³He cell skin choice (Al foil) — updated 2026-10-02 (dylan-MS-7C84)

**Goal:** choose a 1 bar ³He cell skin that stops ³He permeation without adding neutron-capture
background or lepton scattering. Dylan's questions: alternatives to Al, the thinnest foil, what the
scattering "base" is, and whether 1 bar needs any strength.

**Done (analytic; published):**
- `he4_bag/he4_bag.py` §6 (metals, foil_gauge, chord_budget, hoop) → `he4_bag/out/{metals,foil_gauge,chord_budget,chord_ladder,hoop}.csv`.
- Slides 11–15 added to the note, republished at https://dylan-neff.web.cern.ch/notes/ill-he4-bag-3he-leak.html.
- `he4_bag/README.md` §6; pointers in `ill/FEASIBILITY_SIM.md` §5 and §9, `ill/README.md`, and the `vessel_design/mylar_wrap_vessel.py` docstring.
- Results:
  - The skin is already outside the beam (R 40 mm vs r99 12.9 mm) and adds ~1e-8 captures/n.
  - The Al that matters is the 8 mm end caps: upstream cap + ring are in 63 % of G1 accidentals.
  - Al is the right metal (only Be is better, and it can't be wrapped).
  - Skin: 12 µm PET + 6–7 µm converter foil, no PE sealant.
  - Scattering base: Micromegas 9 µm Cu 39 %, air 33 %, skin 8 %.
  - ±50 mbar is fine with the PET as the load layer. The cell can't be pumped out to fill it.

**Next steps:**
1. Geant4 (ILL branch of MX17_Full_Geant, lxplus): run C1 on G1 with the laminate skin. This needs a
   two-layer `--skin`; `Al:0.007` alone gives a bound.
2. Geant4: run G1 with the upstream Al cap lined with ⁶LiF, or trimmed, then rerun `ill/sim/lxplus/acc_sources.py`.
3. Check that the 9 µm Cu in the Micromegas entrance is the drift cathode, and whether it can be aluminised.
4. Bench-leak-test a short PET/Al prototype with a He leak detector.

**Gotchas / decisions:**
- Pinhole densities, thinnest foils and yields are catalogue-level (order of magnitude). The barrel
  crossing rate (1e-4/n) is analytic.
- Neither run is set up yet.

**Key files & commands:**
- `python3 he4_bag/he4_bag.py && python3 he4_bag/make_he4_bag_deck.py`
- `python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py he4_bag/out/he4_bag_deck.html --slug ill-he4-bag-3he-leak --force --deploy`
