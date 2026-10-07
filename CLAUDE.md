# x17_facility_search — working notes for Claude

Which facility other than CERN n_TOF could host the MX17 X17 apparatus, and what
would it reach? See `README.md` for the map of the repo. **Read `HANDOFF.md`
first.** Its newest entry says what is running on lxplus and what to do next.

## The detector lives in the CLion / Geant repos, not here

This repo has **no detector description of its own**. Every geometry, material,
response and trigger fact comes from the sibling repos. Look there before
assuming, re-deriving or hard-coding a detector number:

| repo | path | what it owns |
|---|---|---|
| **MX17_Full_Geant** | `~/CLionProjects/MX17_Full_Geant` (GitHub `Dyn0402/MX17_Full_Geant`; the local clone is on `main`, so `git checkout ill` / `ill_ring` for the ILL code) | The full Geant4 simulation of the n_TOF apparatus: target, arms, scintillators, beam, physics list. `include/SimConfig.hh` is the **source of truth** for geometry. Follow `GEOMETRY_CHANGE_CHECKLIST.md` for any geometry change. Reductions: `scripts/thermal_accounting.py` (the "contract": `accounting.json` + `F1…F5.csv`); condor submission `scripts/submit_ill.py` and `scripts/submit_reduce_ill.py` (ILL branches only). Angular resolution: `docs/angular_resolution/angular_resolution_note.md`. E0 branch: `docs/e0_branch/`. |
| **MX17_Geant** | `~/CLionProjects/MX17_Geant` (GitHub `Dyn0402/MX17_Geant`) | The Micromegas module sim. **`shared/MX17ModuleGeometry.hh` is the single MM module description**, used by both sims. As-built geometry from CAD: `design/GEOMETRY_FROM_CAD.md`, `design/GEOMETRY_IMPLEMENTATION_NOTES.md`, `design/NEEDED_INPUTS.md`, `design/mx17_geometry.json`. Detector response / digitiser: `response/`. |
| **nTof_x17** | `~/PycharmProjects/nTof_x17` | n_TOF data analysis, fast MC (`MX17_Simulation/`), measured response (`geant4_response.json`), ³He pair cross sections (`sept26_prelim_analysis/ipc_channels.py`), Garfield++ sims. Its `CLAUDE.md` and `RECONSTRUCTION_BASIS.md` set the reconstruction rules. |
| **nTof_x17_DAQ** | `~/PycharmProjects/nTof_x17_DAQ` | DREAM characterisation. `docs/REPORT_2026-07-28_pulser_daq_characterization.md` is the dead-time source. |

Branches of MX17_Full_Geant used here:
- **`ill`**: ILL work. Adds `--beam ill`, `--target cell`, the G1–G6 cells, the cosmics generator,
  the bias options and the per-event arm tables.
- **`ill_ring`**, from `ill`: `--ring <Mat>` and `--ring-liner <mm>` (the upstream end ring, e.g.
  CFRP or a ⁶LiF liner), `--flight-tube He|Vac[:r]`, `--tube-wall`, `--tube-window`. The current
  ILL work is on this branch.
- **`trigger_plastics`**, from `ill`: adds `--big-plastic U V T`, `--no-ls` and
  `--sipm-readout N SHIFT`.
- **`lnl`** (planned, from `ill_ring`): the LNL target region (Li film + backing in a thin
  chamber, point beam-spot vertices, a γ-line source). Spec in `lnl/GEANT_PREP.md`.
  The pair generator already takes `--energy 18.15 --mass 16.7` and the Born
  `--ipc-multipole M1|E1`.

When this repo changes the simulation, the change goes in MX17_Full_Geant. Only copies
of the lxplus drivers live here (`ill/sim/lxplus/`, `trigger_scint/sim/lxplus/`).

## The apparatus in one screen (n_TOF as built)

Use these for orientation only. The Geant repos above are authoritative.

- **Four arms** around the target (pinwheel layout). Each arm, going outward:
  - air;
  - Micromegas TPC, 30 mm drift, 60 µm aluminised mylar window, 9 µm Cu cathode. The
    active area is 399.4 × 359.9 mm: the strip plane is passivated ~19 mm at each Y end.
    The faces sit at ±204 mm.
  - SiPM scintillator wall, 20 bars; 16 are read out at n_TOF (`--sipm-readout 16 1`).
  - two 20 × 30 × 2 cm plastic bars;
  - liquid scintillators.
- **n_TOF target:** 500 bar ³He capsule. Radial budget 1.26 % X₀, dominated by
  0.6 mm Al + 0.9 mm CFRP (`docs/PLAN_GANIL_NFS.md` Part 0).
- **Coordinates:** beam = +Y, origin at the detector centre. Kept at the ILL, with a
  flag for the horizontal beam.
- **Reconstruction:** the MM measure position well (0.6–0.8 mm) and direction poorly.
  The opening angle is the vertex-to-hit chord, so it needs an assumed vertex.
  σ68(Δθ) ≈ 14.5° at n_TOF, set by the capsule's material.
- **DREAM DAQ:**
  - RAW at 20 samples × 60 ns: 3.35 kHz max, τ ≈ 298 µs per event;
  - non-paralysable, live = 1/(1 + f·τ);
  - τ ∝ number of samples;
  - ~83 MB/s per FEU.
- **Trigger acceptance:** the as-built stack accepts 2.3 % of X17 pairs. Lepton energy
  containment is ~40 %, so an Esum > 13 MeV cut keeps ~25 % of X17.

## Physics numbers in common use

- S_n = 20.577 MeV. The excitation is E\* = S_n + 0.75·E_n, which beats the lab boost by
  2–6×. θ_min = 2·asin(m_X/E_X) is 109.6° at rest, 99.3° at 2 MeV and 65.7° at 14 MeV
  (`docs/anchor_kinematics.py`). So **the physics wants E_n ≲ 2 MeV or thermal.**
- m_X = 16.8 MeV.
- α_IPC ≈ 3.5×10⁻³ pairs per γ at ~20.6 MeV.
- X17/IPC normalisation:
  - The Geant "benchmark" is 0.025 (unsourced).
  - ATOMKI ⁴He (PRC 104 044003) gives ~1.5×10⁻³.
  - ATOMKI ⁸Be level: 1.6×10⁻³. The ILL verdict is quoted in these units.
  - Plans use the pessimistic value.
- Thermal: radiative captures per absorbed n are 1.03×10⁻⁸; pairs per absorption
  4.8×10⁻¹¹. Both channels go as 1/v, so the yields per absorbed neutron do not depend
  on pressure or wavelength.
- Reach is quoted as X17/IPC(M1) at 3σ per 50-day ILL cycle, Asimov/Fisher.
- **⁸Be (LNL, `lnl/`)**:
  - Q(⁷Li(p,γ)) = 17.2551 MeV, so E\* = Q + (7/8)·E_p.
  - 1⁺ resonances at E_p = 441.4 keV (17.64 MeV, Γ_lab 12.2 keV, σ 5.9 mb) and
    1030 keV (18.15, Γ_lab 168 keV).
  - Direct E1 capture is ~half of γ₀ at 1.03–1.10 MeV.
  - γ₁ (to 3.0 MeV) ≈ 2× γ₀.
  - X17 edge 133–139° at 1.03 MeV for m = 16.7–17.0.
  - The claim is quoted as R = Γ_X/Γ_γ: ATOMKI 5.8×10⁻⁶ (18.15); MEG II limits
    R(18.1) < 1.2×10⁻⁵ and R(17.6) < 1.8×10⁻⁶ (90 % CL).
  - No neutrons below E_p = 1.881 MeV.

## lxplus / EOS

Geant4 and heavy reductions run **only** on lxplus as HTCondor jobs. Never run them
locally. Reach lxplus with `ssh lxplus` (Kerberos; see the global CLAUDE.md).
`lxplus926`/`lxplus989` can't be reached by name.

| what | where |
|---|---|
| all sim output (`$E`) | `/eos/experiment/ntof/data/x17/ill/<run>/<config>/`; contracts `…/ill/contracts/`, analysis `…/ill/analysis/`, trigger `…/ill/trig/`, TB `…/ill/TB/` |
| AFS work | `/afs/cern.ch/work/d/dneff` (= `/afs/cern.ch/user/d/dneff/work`) |
| ILL clones (branch `ill`) | `…/work/git/x17_ill/{MX17_Full_Geant,MX17_Geant}`; analysis scripts in `…/work/git/x17_ill/analysis/` |
| trigger clone | `…/work/git/x17_trig/` (binary `bin/mx17_full_sim_trig1`) |
| condor files and logs | `/afs/cern.ch/user/d/dneff/condor/ill/<run>/<config>/` |

Gotchas:
- C1w reductions need ~36–40 GB of memory; C1w fits need ~14 GB.
- Driver shell scripts die with the ssh session. Use nohup, or condor.
- Check `condor_q dneff -hold`.
- Before rerunning a pipeline, check `parts/` so the reduce isn't resubmitted.
- Classify volumes by logical volume, never by radius.

## Working here

- **Python:** no local venv. Use `~/PycharmProjects/nTof_x17/.venv/Scripts/python.exe`
  (numpy, pandas, matplotlib).
- **Figures:** `ill/figstyle.py` and `ill/report_style.py` are vendored copies of the
  nTof_x17 house style. Every figure writes a `.csv` beside its `.png`.
- **Write-ups:** results go into a markdown write-up in the study directory
  (`FEASIBILITY_SIM.md`, `TRIGGER_OPTIONS.md`, …). Number the sections and date each
  update. Then update the subdirectory README's "read this first" block.
- **Decks:**
  - Built with `dylan-cern-site/scripts/slidedoc.py`: `ill/deck/build_deck.py`,
    `he4_bag/make_he4_bag_deck.py`.
  - Publish with `python ~/PycharmProjects/dylan-cern-site/scripts/add-note.py <html> --slug <slug> --force --deploy`,
    or the `publish-note` skill.
  - Live: `ill-x17-feasibility`, `ill-he4-bag-3he-leak`.
  - Analysis decisions go on the X17 board (`x17-board` skill).
- **The website:** the studies have an unlisted section at
  `dylan-neff.web.cern.ch/facilities/` (source `~/PycharmProjects/dylan-cern-site/pages/facilities/`):
  - a landing page plus `ill.html`, `lnl.html` and `ganil-nfs.html`;
  - the 3D viewers, copied from `*/viz/` with the import map pointed at the site's vendored
    three.js (see the site README, "Facility studies").

  After changing a viewer or a headline result here, update the site copy too. Deploy runs from
  the Linux machine (`scripts/deploy-eos.sh`).
- **Small copies only:** copy small outputs back from EOS into `*/sim/` and `*/out/`.
  The raw copies (`ill/sim/contracts/`, `ill/sim/s1test/`) are gitignored.
- **Unknowns:** mark facility facts that could not be found publicly as **(ask)**. Mark
  analytic stand-ins as such until Geant4 replaces them. `docs/PLAN_GANIL_NFS.md`
  lists the simplifications in force; none may reach a published note.
- **Handoffs:** at the end of a session, add a dated section at the top of `HANDOFF.md`:
  - Goal
  - Done
  - In progress / where it stopped
  - Next steps
  - Gotchas
  - Key files
