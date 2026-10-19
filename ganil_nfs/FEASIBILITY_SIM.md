# GANIL/NFS — X17 feasibility with Geant4

Gate 2 of `docs/PLAN_GANIL_NFS.md` (does NFS give usable neutrons?) and a first
Geant4 reach.  Beam reference: `README.md` in this directory.

**Status 2026-10-19 (evening, §4).** With the beam-induced background from a forced-collision
Geant4 run included, big plastics reach X17/IPC = **3.3×10⁻³ using every E_n ≤ 25 MeV (×2.2 short of
ATOMKI ⁴He, 1.5×10⁻³)** and **3.1×10⁻² below 2.75 MeV (×20 short)**. As built: 8.5×10⁻³ and 0.16.
The all-energy number still assumes X17/IPC constant up to E* ≈ 40 MeV. Slides:
https://dylan-neff.web.cern.ch/notes/ganil-nfs-x17-feasibility.html (`deck/build_deck.py`).

---

## 1. The fold — 2026-10-19

`nfs_fold.py` → `out/fold_table.csv`, `out/fold_vs_En.png`, `out/fold_windows.csv`, `out/ed_scan.png`.

d(40 MeV) + thick Be at 0°, 50 µA (the NFS maximum; the current at our repetition rate is
README §10 Q3, **(ask)**), beam solid angle Ω = 2.82×10⁻⁵ sr, on the baseline cell (PLAN §4.4
build C: 30 bar ³He × 40 cm, R = 50 mm).

| E_n window [MeV] | n/s on cell | ³He(n,γ)/s | IPC/day (before acceptance) | θ_min [°] | vs ILL captures |
|---|---|---|---|---|---|
| 0.2–1 | 1.9×10⁶ | 3.1 (1.1 low) | 1 230 | 104–108 | 0.016 |
| 0.2–2 | 5.1×10⁶ | 10.8 (6.4 low) | 4 380 | 99–108 | 0.055 |
| 2–5 | 1.3×10⁷ | 30 | 12 400 | 88–99 | 0.15 |
| 5–10 | 4.8×10⁷ | 67 | 28 800 | 74–88 | 0.34 |
| 10–20 | 2.1×10⁸ | 210 | 96 100 | 57–74 | 1.07 |
| 0.2–40 | 3.5×10⁸ | 368 | 166 000 | 39–108 | 1.9 |

"low": the model's compound part only, below 1.5 MeV, where the d+Be spectrum is
unmeasured. Below 2 MeV NFS gives ~5 % of the ILL capture rate. Lowering E_d does
not help (`ed_scan.png`): at 10 MeV deuterons the sub-2 MeV fraction rises to 28 %
but the absolute sub-2 MeV yield drops 10×.

## 2. Geant4 samples — 2026-10-19

MX17_Full_Geant branch **`nfs`** (`e26c6eb`: `--beam nfs`, `--cm-beta`, `--pair-r`,
multi-layer skin; `ea9f761`: `scripts/submit_nfs.py`).  lxplus clone
`…/work/git/x17_nfs/`, binary `bin/mx17_full_sim_nfs_e26c6eb`.  Driver copies in
`sim/lxplus/`.  Output `/eos/experiment/ntof/data/x17/nfs/<run>/<sample>`, merged
tables in `…/nfs/sel/` (copy them with `sim/fetch_sel.sh`).

| run | sample | what |
|---|---|---|
| N1 | `X17_En<E>` | X17 (16.8 MeV) at W = E\*(E_n), ⁴He\* boosted by β_cm; E_n = 0.5, 1, 2, 3.5, 5, 7, 10, 14, 20 |
| N2 | `E1_En<E>` (+ `M1_En0.5`) | Born IPC at the same W, generated at opening angle ≥ 40° |
| N3 | `beam` | 10⁸ NFS d(40)+Be neutrons, 0.1–45 MeV, r = 40 mm, vacuum flight tube |
| — | cosmics | the LNL `L4_cosmic` tables (same arms) |

Each comes as built (`--sipm-readout 16 1`) and with big plastics (`_bigP`: 75 × 75 × 5 cm, no LS).

## 3. Reach — 2026-10-19

`sim/nfs_reach.py` → `out/reach/{reach,bins,beam}.csv`, `out/reach/reach_vs_window.png`.

Vertex: the beam-axis point closest to the two MM segments (DCA < 60 mm each).
Calorimetry: the LNL-calibrated response. Cut E_sum > W/2. ρ = X17/IPC(E1), constant
in E\*. 14 days, DREAM live time from the two-arm beam trigger rate.  Asimov over histogram bins.

### 3.1 ρ at 3σ, windows starting at 0.2 MeV (δ = 0)

| window [MeV] | as built, m_ee \| E_n | as built, θ no TOF | big plastics, m_ee \| E_n | big plastics, θ no TOF |
|---|---|---|---|---|
| 0.2–1.5 | 0.38 | 0.48 | 0.068 | 0.12 |
| 0.2–2.75 | 0.10 | 0.16 | **0.022** | 0.046 |
| 0.2–6 | 0.025 | 0.046 | 0.0078 | 0.015 |
| 0.2–12 | 0.0096 | 0.015 | 0.0038 | 0.0061 |
| 0.2–25 | 0.0063 | 0.0088 | **0.0025** | 0.0037 |

Adding a 2 % uncorrelated shape error per bin changes these by ≤ 25 %. Background
is cosmics in m_ee (they sit at θ = 150–180°, so θ separates them), IPC elsewhere.
Using TOF (E_n per event) gains ×1.5 over an untagged θ fit.

### 3.2 What the gain at high E_n assumes

- **X17/IPC constant in E\*.** ATOMKI measured ⁴He at E\* ≈ 20.5–21 MeV. Above that the
  capture runs through broader ⁴He levels, and how the X17 branching changes is unknown.
  The 0.2–25 MeV number is a statement about a model, not about the ATOMKI claim.
- **50 µA at the repetition rate we need** (ask, README §10 Q3).
- **Beam background negligible** (§3.3).

### 3.3 Beam-induced background: not constrained

10⁸ neutrons is 0.28 s of beam. Two-arm events: 4 as built, 30 with big plastics
(14 and 106 /s), none passing vertex + E_sum. A zero from 0.28 s bounds nothing:
the IPC it competes with is ~10² per day per E_n bin. A crude factorised estimate
(two-arm rate × vertex-pass × E_sum-pass, each taken from this small sample) gives
~10⁴ per day as built, mostly at θ > 150°. One of the 30 big-plastics events is
X17-like: θ = 84°, vertex at y = +187 mm (the Al end cap). All 34 events come from
E_n > 10 MeV neutrons, so the prompt part hits the high-E_n bins, which are the
bins the full-window reach depends on.

Single-arm rates are 32 kHz as built and 156 kHz with big plastics. These are fine
with prescaled singles (the LNL baseline), but random two-arm coincidences inside a
bunch are not in the reach yet.

Brute force does not scale: 10⁶ neutrons cost ~10 min and 100–170 MB per job, so a
day of beam is ~10¹³ neutrons. Options, cheapest first:

1. **Factorise properly**: per-arm tables from N3 at loose cuts (E_arm, segment
   DCA, timing), then build two-arm backgrounds as products, separately for
   correlated (same neutron) and random (same bunch) pairs.
2. **Biased N3**: start the neutrons at their first interaction in the material
   near the arms (end cap, window, skin, tube), with the interaction-probability
   weight. This needs a new option in MX17_Full_Geant `nfs`.
3. Reduce in the job and delete the ROOT file, so that 10¹⁰ neutrons (28 s of beam) are
   affordable as a check of 1–2.

The low-E_n window (≤ 2.75 MeV) is the window that matters for physics. It is 15× short
**before** any beam background, so step 1–3 only matter if the high-E_n reach is
worth pursuing.

### 3.4 Not yet included

Delayed beam-correlated background (moderated neutrons, capture γ, spread over
the whole bunch period and wrap-around); the γ flash; the M1 IPC component (only
E1 is used; `M1_En0.5` exists); a θ×|y|×E_sum 3D fit (LNL §14 style); systematics
on ρ(E\*).

## 4. Beam-induced background with a forced-collision Geant4 run — 2026-10-19

### 4.1 Method

MX17_Full_Geant branch `nfs` (9d183c8): `--force-beam` and `--roulette p1 p0`.

* **Forced first collision.** The generator walks the neutron's straight line through the geometry,
  takes τ_i = Σ_tot(E)·ℓ for every leaf volume from `G4HadronicProcessStore` (the tracking's own cross
  sections), draws volume i ∝ P_i = e^(−Σ_{j<i} τ_j)(1 − e^(−τ_i)), starts the neutron 0.1 µm inside it, and
  `BeamForceOperator` forces the collision there (G4BOptnForceCommonTruncatedExp: GB02's forced branch
  without the free-flight clone). Event weight = Σ P_i, ⟨ΣP⟩ = 0.137. One history per event, so
  coincidences stay physical. First collisions in air are not sampled.
* **Roulette.** `StackingAction` holds the primary's secondaries until it is done, predicts the arms
  they reach (straight line into a generous box per arm), keeps ≥ 2-arm histories, 1-arm ones with
  p1 = 0.2, 0-arm ones with p0 = 0.05 (weight 1/p). Whole histories, so unbiased for any observable.
* **Check.** The primary's track weight after the forced collision equals 1 − e^(−τ) to 3×10⁻⁵ on average
  (max 0.25 in a handful of events).
* **Cost.** 3.6 ms per forced event, 0.8 ms with roulette: ×7.6 the beam time per event, ×30–40 per CPU-s.
  2×10⁸ events per hardware variant (N4, 250 jobs × 4×10⁵, ~20 CPU-h) ≈ 2.2 s of beam. A day of beam is
  3×10¹³ neutrons, so the correlated term after all cuts still rests on a handful of MC events.

### 4.2 Reduction in time clusters

Half of the single-arm hits come µs to s after the neutron (captures, activation decays: radioactive
decay is on). The old whole-event reduction (ill_pairs.py) summed an arm's deposits over all time.
`sim/lxplus/nfs_beam_reduce.py` splits each arm's scintillator hits into time clusters (a gap > 50 ns
starts a new one); leg, E_sipm/E_plast/E_ls and the MM segment (DriftGas steps within ±100 ns) are per
cluster. `nfs_beam_merge.py` makes singles (leg + MM segment in the active area) and same-event pairs
in different arms within ±5 ns. The jobs reduce in the condor scratch dir and delete the ROOT file
(`submit_nfs.py --reduce-in-job`; first 2 jobs keep theirs).

Validation, per second at 50 µA (analog N3 10⁸ n in clusters vs forced N4 2×10⁸):

| | analog | forced |
|---|---|---|
| as built: single-arm legs | 31 390 | 30 250 |
| as built: two-arm triggers | 21.1 | 16.2 |
| as built: two arms with MM tracks | 14.1 (4 ev) | 9.0 (22 ev) |
| big plastics: single-arm legs | 151 400 | 148 900 |
| big plastics: two-arm triggers | 274 | 248 |
| big plastics: two arms with MM tracks | 81 (23 ev) | 63 (138 ev) |

### 4.3 In the reach (`sim/nfs_reach.py`)

* Beam events are binned by their measured time (earliest SiPM hit of the pair + flight from the
  source to the gun), folded into the 2.27 µs bunch period, converted to E_n over 13.6 m.
* **Accidentals:** singles from different neutrons of one bunch, |Δt| < 5 ns (assumed), taken
  uniform in time within each E_n bin's TOF window; every MC pair weighted n_i n_j 2δ/Δt_k × rep rate.
* **Correlated:** direct (cuts per event, 200 calorimeter-response draws each) or `--beam-fact`
  (every two-arm event × pooled f_vertex × f_E_sum, at its own θ and m_ee).

Per day after vertex + E_sum > W/2, big plastics (factorised; `out/reach_fact/bins.csv`):

| E_n bin [MeV] | IPC | accidentals | correlated beam | cosmics (no veto) |
|---|---|---|---|---|
| 0.2–0.75 | 16 | 2 280 | 68 | 97 000 |
| 1.5–2.75 | 103 | 415 | 0 | 19 000 |
| 12–17 | 1 200 | 880 | 2 100 | 4 100 |
| 17–25 | 910 | 640 | 2 500 | 3 700 |

f_vertex = 0.26, f_E_sum = 0.0038 (big plastics); 25 % of two-arm beam events have θ in 55–110°.
The events passing every cut directly (1–2 MC events per bin) are at θ = 25°, 149°, 161°.

### 4.4 Reach, 14 days, 50 µA (m_ee | E_n)

| | no beam | + beam, direct | + beam, factorised |
|---|---|---|---|
| big plastics, 0.2–25 MeV | 2.4×10⁻³ | 3.0×10⁻³ | **3.3×10⁻³** |
| big plastics, 0.2–2.75 MeV | 0.020 | 0.031 | **0.031** |
| as built, 0.2–25 MeV | 6.2×10⁻³ | 7.4×10⁻³ | **8.5×10⁻³** |
| as built, 0.2–2.75 MeV | 0.10 | 0.12 | **0.16** |

Outputs: `out/reach_nobeam/`, `out/reach/` (direct), `out/reach_fact/`, `out/reach_n3c/` (analog check).

### 4.5 Open

* Coincidence window ±5 ns and the 50 ns cluster gap are assumptions; accidentals scale with the window.
* No cosmic veto (arm-to-arm TOF as at LNL); no γ flash; no beam dump or room; air collisions not forced.
* The correlated term in the X17 θ window is factorised (independence of vertex, E_sum, θ assumed).
* X17/IPC above E* ≈ 21 MeV is unknown; the current at 440 kHz is a question for GANIL.
