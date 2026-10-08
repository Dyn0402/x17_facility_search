# Handoff

## LNL ⁸Be: Geant4 campaign done, deck and site republished — 2026-10-08 night (dylan-MS-7C84)

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

**Next steps:**
1. Ask the collaboration:
   - the SiPM-wall time resolution (TOF needs ≲ 0.4 ns);
   - whether the LS can be read at LNL. Without them: 19 d, and no cosmic E_sum edge.
2. Emails (Dylan's): LNL (Selva/pacbeams), T. Marchi.
3. The IPC shape: the fit with M1/E1 free is ×2.3–3 slower. Add Zhang–Miller M1–E1 interference, or plan
   0.8 MeV E1-shape runs.
4. Optional: rerun cosmics for `_sipm20` (it uses the as-built cosmics now); ¹¹B and beam-halo sims.
5. **EOS:** the 2 TB of raw ROOT in `…/x17/lnl/L*/` can go once the tables are final. Only the `sel/` and
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
`lnl/out/geant/reach_geant.csv`, `lnl/deck/build_deck.py`.

## LNL ⁸Be: site deployed, slides published, Geant4 L1/L2 running — 2026-10-08 (dylan-MS-7C84, Ubuntu)

**Resume:** when the L1/L2 condor jobs finish, reduce them and replace `EPS_REST` and the γ₁ leak in
`lnl/lnl_rates.py` with the Geant4 numbers (`lnl/GEANT_PREP.md` §0 "Next").

**Goal:** follow the 2026-10-08 Windows handoff below: deploy `/facilities/`, make the LNL slides,
start Geant4 (L0–L2).

**Done:**
- **Website deployed** (`dylan-cern-site` c968914 + 28554e9). `/facilities/` (index, ill, lnl, ganil-nfs) and
  both 3D viewers are live, byte-identical to local, and render with the vendored three.js (headless check).
- **LNL slide note**, 11 slides: `lnl/deck/build_deck.py` → `lnl/out/lnl-x17-feasibility.html`, every number
  read from `lnl/out/*.csv`. Live at https://dylan-neff.web.cern.ch/notes/lnl-x17-feasibility.html,
  linked from `facilities/lnl.html`.
- **MX17_Full_Geant `lnl` branch** (5722bef, 1577274, 079db11; pushed): `--target li`, beam-spot
  vertices, `--gamma-lines`, conversion truth in γ-line runs, `scripts/submit_lnl.py` (copy in
  `lnl/sim/lxplus/`). Details in `lnl/GEANT_PREP.md` §0.
- **L0 smoke passed** on lxplus (no overlaps; vertices in the 1.49 µm film; X17 edge 133.8°).
  First hint from 500 events: pair-tag 3.6 % with 47 % in both MM gaps, so a post-geometry
  factor ~0.08 against EPS_REST = 0.14.

**In progress:** L1 (`X17_m16.6/16.7/16.8/17.0`) and L2 (`M1/E1_18.15`, `M1_17.64`, `M1/E1_15.1`,
`M1/E1_14.6`), 10 × 10⁵ each. Clusters 4405805–4405815, submitted ~01:00. Outputs in
`/eos/experiment/ntof/data/x17/lnl/L{1,2}/`.

**Next steps:**
1. `condor_q dneff`; when done: `python3 scripts/submit_reduce_ill.py /eos/.../lnl/L1/* /eos/.../lnl/L2/* --kind pairs`
   (from the `x17_lnl` clone), then `ill_pairs.py merge` per sample.
2. Write a small LNL analysis (`lnl/sim/`): acc × ε vs opening angle (125–155°) for X17 and each IPC,
   the E_sum spectra 18.15 vs 15.1 → put both into `lnl_rates.py`, rerun, rebuild and republish the deck,
   update `facilities/lnl.html` numbers.
3. L3 `gam_8Be`/`gam_19F` (EPC, singles) and L4 `cosmic`, with `submit_lnl.py`.
4. Emails (Selva/pacbeams; Marchi) — Dylan's to send.

**Gotchas:**
- `dylan-cern-site` still has uncommitted edits to `notes/ill-x17-feasibility.html`, the X17 board
  (`x17/analysis.html`) and `sw.js`, from an earlier session. They are already live (identical to the
  deployed files); commit them when convenient.
- The lxplus ILL clone `x17_ill/MX17_Full_Geant` is detached with uncommitted edits and a stray
  `dneff.cc`; the LNL work uses its own clone `x17_lnl/` so it does not touch them.
- Each 10⁵-pair job writes ~2 GB (full HitTree), like the ILL S1 runs.
- `EventTree.inv_mass` is E_γ in `--gamma-lines` runs.

**Key files:** `lnl/deck/build_deck.py`, `lnl/GEANT_PREP.md` §0, `lnl/README.md`,
MX17_Full_Geant `lnl`: `src/DetectorConstruction.cc` (`BuildLiTarget`), `src/X17PrimaryGenerator.cc`
(`SampleHe3Vertex`, `GenerateGammaLines`), `scripts/submit_lnl.py`.

## LNL (Legnaro) ⁸Be feasibility — updated 2026-10-08 (DESKTOP-BCED9EL → continuing on Ubuntu)

**Resume (on the Ubuntu box):**
1. **Deploy the website.** In `~/PycharmProjects/dylan-cern-site`: `git pull`, then `kinit dneff@CERN.CH` and
   `./scripts/deploy-eos.sh`. That puts the new unlisted `/facilities/` section live (the commit is `c968914` on
   master; it was built and checked on Windows but never deployed). Then check
   https://dylan-neff.web.cern.ch/facilities/ and the two 3D viewers (`ill-beams-3d.html`, `lnl-setup-3d.html`).
2. **Make the LNL slides.** Use the publish-note skill + slidedoc, like `ill/deck/build_deck.py`. The story is the
   bottom line in `lnl/README.md`; the figures are in `lnl/out/figures/`. Link the deck from
   `dylan-cern-site/pages/facilities/lnl.html`.
3. **Start Geant4.** Follow `lnl/GEANT_PREP.md` §2 on a new MX17_Full_Geant branch `lnl`, from `ill_ring`.
   Run L0–L2 first.
4. **Emails.**
   - To LNL (A. Selva / pacbeams): hall plans, AN2000 vs CN, the next PAC.
   - To T. Marchi: the LNL 2023–24 ⁸Be data, and the Góngora-Servín thesis (it returned 403 online).

**Website, done 2026-10-08.** `dylan-cern-site` now has `/facilities/`:
- **Pages:** a landing page plus `ill.html`, `lnl.html` and `ganil-nfs.html`.
- **The 3D viewers:** copies of `ill/viz/ill_beams_3d.html` and `lnl/viz/lnl_setup_3d.html`. Their import map points
  at the vendored `js/vendor/three/` (three.js 0.160.0), and the Google Fonts links are dropped.
- **Unlisted** like the notes: `UNLISTED` / `STANDALONE_OK` in `build.py`. The hub has a "Facility studies" block,
  and the private-page nav gains a "Facilities" link.
- **Figures** are copied by hand into `facilities/{ill,lnl,ganil}/`. **They do not update by themselves**: after
  new results, re-copy them and edit the pages. The procedure is in the site README, "Facility studies".

**LNL 3D viewer, done 2026-10-08.** `lnl/viz/lnl_setup_3d.html` shows the MX17 arms with the trigger stack around
the Li target and chamber, against the LNL 2023–24 clovers and ATOMKI 2016. It has live yields per
machine/energy/film (the grid is precomputed from `lnl_rates.thin_yield`) and illustrative X17/IPC/cosmic events.
It was checked with a headless Chrome screenshot; the Chrome extension was unavailable, so nothing was clicked
through interactively. **If `lnl_rates.py` changes, update the `Y` grid embedded in the viewer.** `lnl_rates.py` writes it to
`out/viewer_yield_grid.json` (`viewer_grid()`). Paste that JSON over `const Y = …`, then re-copy the viewer to the site.

**Goal:** Dylan has an LNL contract. The idea is to run the ATOMKI reaction ⁷Li(p,e⁺e⁻)⁸Be there with
the MX17 apparatus. Research the beam and facility, the reaction and the Li targets. Estimate as much as
possible without Geant4, then get ready for useful Geant4 runs.

**Done 2026-10-07 (all in `lnl/`, committed `5994ddd`):**
- `FACILITY.md`:
  - AN2000: 0.2–2 MV, ≤ 1 µA, self-service; 0° line ≤ 20 nA.
  - CN: 0.8–5.5 MV, 1 µA in the beam sheet, ~4 µA authorised, pulsed 3 MHz < 2 ns, Mon–Fri daytime.
  - PAC route; contacts Anna Selva and pacbeams@lnl.infn.it.
  - **The LNL ⁸Be spectrometer (Marchi / Góngora-Servín) already ran on AN2000 in 2023–24** (LiF,
    800 nA, 790 h), unpublished.
- `PHYSICS.md`: the resonances (Tilley 2004), direct capture, IPC, kinematics, the experimental record
  (ATOMKI 2016/2022, Hanoi, MEG II null, the MEG-2026 cosmic-bump paper), theory.
- `TARGETS.md`:
  - LiF / Li₂O / Li / LiPON, backings, heat and dose.
  - Contaminants: ¹¹B is the dangerous one; ¹⁹F gives the free E0 calibration line.
  - Keep the film thin so the beam never reaches the 441 keV resonance.
- `lnl_rates.py` → `out/`, `ESTIMATES.md`:
  - Zahnow σ (EXFOR) split into BW resonances + direct capture.
  - PSTAR stopping.
  - Born IPC from nTof_x17 `ipc_born`.
  - Four-arm toy acceptance.
  - Counting reach.
  - CHECKs pass vs Tilley (5.93 vs 5.9 mb) and Rose α; the MEG-2026 normalisation is explained.
- **Result:** ATOMKI R = 5.8×10⁻⁶ at 3σ in ~15 d at 1 µA as built, ~6 d if γ₁ (15 MeV) IPC can be
  separated, ×4 faster on CN at 4 µA. IPC-limited once MM segment + collinearity cuts kill cosmics
  (2.5× worse without).
- `GEANT_PREP.md`: what already works in MX17_Full_Geant (`--energy`, `--mass`, `--ipc-multipole`,
  `--cosmic`, `--pair-vertex-lib`) and what to write (`--target li`, a point vertex, `--gamma-lines`),
  plus runs L0–L6.
- Top-level `README.md` and `CLAUDE.md` updated. `refs/*.txt` hold all sources; the PDFs are in the
  gitignored `refs/pdf/`.


**Gotchas / decisions:**
- `EPS_REST = 0.14` (ILL G1 trigger × E_sum × reco over MM geometry) carries the whole ×2 uncertainty.
- Reach counts only 18.15 + direct captures as signal: R(17.6) is already MEG-limited.
- The resonance/direct split is not meaningful below ~500 keV (BW tail vs data); harmless at 1 MeV.
- The Tk backend is broken in the nTof_x17 venv on this machine, so `lnl_rates.py` forces Agg.
- The Góngora-Servín PhD thesis (Ferrara) returned 403. Ask for it; it has the full LNL target/chamber
  description.

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
