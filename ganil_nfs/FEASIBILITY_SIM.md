# GANIL/NFS — X17 feasibility with Geant4

Gate 2 of `docs/PLAN_GANIL_NFS.md` (does NFS give usable neutrons?) and a first
Geant4 reach.  Beam reference: `README.md` in this directory.

**Status 2026-10-19.** Below 2.75 MeV, where the X17 edge sits at 99–108° and the
physics wants to be, NFS reaches X17/IPC ≈ 2.2×10⁻² in 14 days with big plastics.
That is **15× above ATOMKI ⁴He (1.5×10⁻³)**, even with no beam-induced background.
Using every neutron energy up to 25 MeV, with TOF tagging E_n event by event, the
reach improves to 2.5×10⁻³ (big plastics) / 6.3×10⁻³ (as built). That number rests on two
things nobody has checked: that X17/IPC stays constant up to E\* ≈ 40 MeV, and that
the beam-induced background is small. The Geant4 beam sample is too short to say
(§3.3).

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
