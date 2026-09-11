# Plan — feasibility of an X17 search at GANIL/NFS with the n_TOF apparatus

**Repo:** `x17_facility_search` · **Drafted:** 2026-09-09 · **Author:** Claude, for D. Neff
**Predecessor work:** `~/CLionProjects/MX17_Full_Geant` (full Geant4 sim of the n_TOF
apparatus), `~/PycharmProjects/nTof_x17` (fast MC `MX17_Simulation/`, measured
detector response `geant4_response.json`).

The organising question: **how low a material budget do we need in front of the
Micromegas TPCs for the X17 shoulder to survive, and can a low-pressure,
large-volume ³He cell at GANIL/NFS deliver it without giving up rate?**

Current working answer, from the anchor calculations in `docs/`: a 40 cm cell at
**30 bar and 5 cm radius** with a beryllium barrier reaches **0.21 % X₀** against
the n_TOF cell's 1.23 %, at 0.60× the areal density. Below ~30 bar the wall hits its
manufacturing floor and further pressure reduction buys **no resolution at all**,
only lost rate — so the "trade statistics for sharpness" lever is smaller than it
looks, and the real levers are the barrier material and the Micromegas window.

---

## Part 0 — What the previous campaign already established

Read before starting; these are the constraints the study inherits.

**The resolution is hardware-frozen at n_TOF.** `docs/angular_resolution/angular_resolution_note.md`
in the Geant repo: σ68(Δθ) ≈ 14.5° over the full accepted X17 spectrum, ≈ 11.5–12.5°
for the most symmetric pairs, *with the vertex known exactly*. Seven reconstruction
methods land within 2° of each other. The at-rest X17 truth shoulder at
θ_min ≈ 109° becomes a 40°-FWHM bump at ¼ the peak height. Cut-and-count is dead;
only a template fit survives.

**Where it is lost.** Highland budget along the radial exit path, normal incidence,
as-built n_TOF geometry (reproduced and re-checked here):

| layer | x/X₀ | share | θ₀ at p = 10 MeV/c |
|---|---|---|---|
| ³He gas, 500 bar, 1.0 cm | 0.089 % | 7.0 % | 1.72° |
| **Al barrel 0.6 mm** | **0.675 %** | **53.4 %** | **5.24°** |
| **CFRP wrap 0.9 mm** | **0.327 %** | **25.9 %** | **3.51°** |
| air gap 23.9 cm | 0.079 % | 6.2 % | 1.61° |
| Mylar 40 µm | 0.014 % | 1.1 % | 0.62° |
| Kapton 50 µm | 0.018 % | 1.4 % | 0.70° |
| Cu cathode 9 µm | 0.063 % | 5.0 % | 1.42° |
| **total upstream** | **1.263 %** | | **7.31°** |

The measured Geant4 `first`-estimator median (7.9° at KE ≈ 10 MeV) sits on the
Highland prediction, so **the analytic budget is trustworthy** — that is what makes
a cheap Python study meaningful before any Geant4 work.

**The scatter sits ~11 mm from the vertex**, so a chord from the true vertex
retains ≈ 96 % of it. No vertex trick recovers anything. Important consequence for
this study: the *vertex-free* estimator (PCA fit of the drift-volume track) is only
0.5–1° worse than the true-vertex oracle. **A physically larger cell does not, by
itself, destroy the measurement** — it only kills the chord estimators.

**Rate physics.** `docs/he3_self_shielding_note.md`: below ~1 keV the gas is
optically thick to ³He(n,p)t and the radiative-capture probability saturates at
σ_nγ/σ_np ≈ 1.0×10⁻⁸ regardless of thickness. **Above ~100 keV the gas is thin**
and the yield is linear in areal density, `N ∝ Φ_area · (nL) · σ_nγ`. Everything
below assumes the MeV region, where areal density is the only rate knob.

**Normalisation constants in use, and the one that is unsourced.** The Geant repo
uses α_IPC ≈ 3.5×10⁻³ (pairs per γ at ~20.6 MeV, anchored to the measured ¹²C
15.1 MeV M1 and ⁸Be 18.15 MeV points) and `BR_X17 = 0.025` X17 per IPC pair,
labelled "the project benchmark" with no citation. ATOMKI's ⁴He paper
(Krasznahorkay et al., PRC **104** (2021) 044003) quotes **B_x = 5.1(13)×10⁻⁶**,
which with α_IPC gives X17/IPC ≈ 1.5×10⁻³ — a factor ~17 below the benchmark, and
~30 below it at the pessimistic end of both bands. **This study runs on the
pessimistic value** (§1.3); reconciling the two is deferred, not blocking.

---

## Part 1 — The truth opening-angle distribution, done properly

Deliverable: the combined IPC + X17 opening-angle spectrum with no scattering,
normalised to the ATOMKI-inferred X17 strength, as a function of neutron energy.
This is the reference every later plot degrades away from.

### 1.0 Working simplification — read this first

**Decision (2026-09-09): for the first pass we do not need the true background
shape.** What the study has to answer is whether a sharp bump survives on a smooth
continuum, and that question is insensitive to the exact continuum. So:

- **Background:** keep the existing dN/dM ∝ 1/M virtual-photon sampling with
  isotropic decay. It produces a smooth, monotonic, structureless opening-angle
  continuum, which is all the smearing study needs. **Placeholder — see §1.1 for
  what a real treatment requires.**
- **Signal normalisation:** use the **most pessimistic** X17 strength available
  (§1.3). If the bump survives at the pessimistic normalisation, every better
  number is upside; if it does not, no amount of normalisation argument saves it.

Both simplifications are logged in the deferred list at the end of this document.
Neither may be carried into a published result.

### 1.1 Replace the toy IPC generator (deferred — do this properly later)

`X17PrimaryGenerator.cc` currently samples the virtual-photon mass as
dN/dM ∝ 1/M on [2mₑ, E*] and decays it isotropically in its rest frame. That is a
placeholder, not IPC. Two things are wrong and both move the opening-angle
continuum in the signal region:

- **The mass spectrum.** The correct differential coefficient is multipole-
  dependent; the Schlüter–Soff–Greiner high-energy Born treatment (Z. Phys. A **286**
  (1978) 149; ADNDT **24** (1979) 509) is the right tool at Z = 2, and gives
  dα/dM separately for E1, M1 and E0/M0.
- **The decay is not isotropic in the γ\* frame.** The e⁺e⁻ correlation carries the
  multipolarity. ATOMKI's own fits use exactly this; reproducing their IPC
  continuum shape is the validation that we have it right.

**Tasks**
1. Code the Schlüter–Soff differential IPC coefficients for E1, M1 and E0/M0 at
   E\* ≈ 20.6–24 MeV. Validate against BrIcc below 6 MeV (installed on lxplus at
   `/afs/cern.ch/work/d/dneff/tools/BrIcc`; its tables stop at 6 MeV) and against
   the ¹²C 15.1 MeV M1 datum α_π = (3.3 ± 0.5)×10⁻³.
2. Cross-validate the resulting opening-angle continuum against the published
   ATOMKI ⁴He angular-correlation spectra. If our continuum does not reproduce
   theirs, we do not understand the background.
3. Set the **multipole mix vs E_n**. M1 dominates s-wave thermal capture; E1 turns
   on toward MeV. Take the mix from Wervelman et al., NPA **526** (1991) 265 and
   the ENDF ³He evaluation already in the repo (`data/He3.h5`).

### 1.2 X17 kinematics vs neutron energy — checked explicitly

The reaction is capture followed by radiation: n + ³He → ⁴He\*, then
⁴He\* → ⁴He_gs + X17 (or → ⁴He_gs + γ\* → e⁺e⁻). The neutron kinetic energy enters
in **two** places, and they are not the same size. Both were checked numerically in
`docs/anchor_kinematics.py`.

**(a) The lab boost of the ⁴He\*, which is small — this part of the intuition holds.**
β_cm = p_n/E_tot. At E_n = 2 MeV, p_n = 61 MeV/c against a ~3.75 GeV total energy,
so β_cm = 0.0164. Its effect on the X17 lab energy is γβ·p_X, at most ±0.23 MeV.

**(b) The invariant mass of the compound system, which is not small.**
√s = √((m_n + m_3He)² + 2·m_3He·E_n), so the excitation energy above the ⁴He ground
state is E\* = √s − m_4He = **S_n + (A/(A+1))·E_n = 20.577 + 0.75·E_n**. The exact
calculation reproduces the 3/4 coefficient to four decimals over 0–40 MeV. This is
the standard compound-nucleus result, and the ⁴He\* really does radiate a harder
photon when it captures a faster neutron. The energy release is not fixed at
20.578 MeV.

Effect (b) beats effect (a) by a factor 2 to 6 across our range:

| E_n | E\* | shift from S_n | max boost shift of E_X | θ_min = 2·asin(m_X/E_X) |
|---|---|---|---|---|
| 0 (at rest) | 20.577 MeV | — | — | 109.6° |
| 0.2 MeV | 20.727 MeV | +0.150 MeV | ±0.063 MeV | 108.5° |
| 1.0 MeV | 21.327 MeV | +0.749 MeV | ±0.152 MeV | 104.1° |
| 2.0 MeV | 22.076 MeV | +1.498 MeV | ±0.234 MeV | 99.3° |
| 5.0 MeV | 24.322 MeV | +3.745 MeV | ±0.4 MeV | 87.6° |
| 14 MeV | 31.053 MeV | +10.48 MeV | ±0.8 MeV | 65.7° |

**Consequences.**

- The shoulder drifts **10° across a 0–2 MeV neutron window** — comparable to the
  resolution we are trying to buy with the whole material-budget exercise. Ignoring
  it would smear the signal about as badly as the scattering does.
- **But time of flight measures E_n event by event**, so θ_min is known per event.
  Bin in TOF, or transform to a variable in which the shoulder is stationary
  (e.g. θ/θ_min, or the reconstructed m_ee at the known E\*). This converts what
  looks like a smearing problem into bookkeeping, and it is a genuine advantage of
  a TOF facility over a reactor or a fixed-energy accelerator.
- At high E_n the shoulder slides toward small angle where the IPC continuum is
  largest, so **rate and separation pull in opposite directions with E_n**. That
  trade is the facility gate in §5.1.

Action: replace the fixed `transition_energy_MeV = 20.58` in the generator with
E\*(E_n), and add the β_cm boost along the beam. Both are already flagged as open
items in the Geant repo's angular note.

### 1.3 X17/IPC normalisation — pessimistic value now, proper treatment later

**Decision (2026-09-09): adopt the pessimistic end of the ATOMKI-inferred band.**

| input | value |
|---|---|
| ATOMKI ⁴He branching ratio | B_x = 5.1(13)×10⁻⁶ |
| B_x at −1σ | 3.8×10⁻⁶ |
| α_IPC at the pessimistic (high) end | 4.5×10⁻³ |
| **working X17 per IPC pair** | **8.4×10⁻⁴ ≈ 1×10⁻³** |

That is **~30× below the `BR_X17 = 0.025` benchmark** carried in the Geant repo.
Using it means every sensitivity number in this study is a lower bound. Good: it
makes a positive result robust and it prevents the material-budget target from
being set by an optimistic assumption.

**Deferred — the questions a real normalisation has to answer:**

- What B_x is quoted *relative to* in the ⁴He paper. The 21.01 MeV 0⁻ → 0⁺ ground
  state transition is **M0** — γ-forbidden — so the observed pairs come from IPC of
  the *direct capture* E1/M1 strength, not from a γ branch. A "per γ" convention
  cannot be applied naively.
- Whether the 0.025 benchmark is a signal *fraction in a fitted angular window*
  (which it plausibly is) rather than a true branching ratio. Those differ by the
  IPC fraction inside the window, which is where the factor ~30 probably lives.
- Whether the ⁴He result transfers from p+t to n+³He at all: different entrance
  channel, different population of the 0⁻/0⁺ states.
- The γ-dark E0/M0 channel, which has no competing photon mode and could rival the
  M1/E1 pair yield outright. The Geant repo's `docs/e0_branch/ipc_estimation_method.md`
  brackets it at f ~ 10⁻³–10⁻² and identifies the ⁴He R-matrix calculation that
  would replace the bracket with a number. **This is upside we are currently
  throwing away**, which is consistent with staying pessimistic.

Deliverable now: one pessimistic number, used consistently everywhere after.
Deliverable later: the band, with the E0/M0 channel included.

### 1.4 Products

- `opening_angle/truth_spectrum.py` — samples X17 and IPC pairs with correct
  kinematics and correlations, at a chosen E_n (or folded over a beam spectrum).
- Figure: truth θ spectrum, X17 on the IPC continuum, at E_n = 0.2, 1, 2, 5, 15 MeV.
- Figure: θ_min and peak-to-continuum ratio vs E_n. **This is the go/no-go plot for
  the choice of neutron energy window at any facility.**

---

## Part 2 — How the bump smears as scattering increases

Deliverable: a family of smeared spectra parameterised by upstream x/X₀, and from
it a **quantitative material-budget target**.

### 2.1 Smearing model

Do not smear the pair angle with a single σ. Smear **per leg**, because the pair
resolution is dominated by whichever leg is soft:

- per-leg plane-projected θ₀ from Highland at that leg's lab momentum;
- space angle ψ = √2 · θ₀ (Rayleigh; median 1.177·θ₀ — the existing
  `3he_material_budget/he3_material_budget.py` labels the plane-projected θ₀ as
  "RMS scattering angle", which is off by these factors and should be fixed when
  that script is folded into `common/`);
- combine the two legs into Δθ geometrically, not in naive quadrature, and reflect
  at the 0°/180° boundaries;
- include the non-Gaussian tail. Highland's Gaussian core underestimates the 30–40°
  tails that the Geant4 study attributes to sub-3 MeV legs. Add a Moliere/Lynch–Dahl
  tail, or calibrate the tail fraction against `geant4_response.json`.

**Validation gate:** at the as-built n_TOF budget (1.263 % X₀) the model must
reproduce the measured σ68 ≈ 15.0–15.5° and the +2.5–3.5° bias for symmetric pairs.
If it does not, the Highland extrapolation to a new design is not trustworthy.
`analysis/pairs_v2/geant4_response.json` in the Geant repo has the per-KE ψ tables
to calibrate against.

### 2.2 The figure of merit

σ68 alone is the wrong target — the angular note already showed that 15.5° and 12°
look nearly identical by eye. Define the target on what the analysis actually does:

1. **Primary:** expected significance of a template fit (smeared X17 shape + IPC
   continuum, IPC normalisation floated) per unit running time, as a function of
   x/X₀. The fast MC in `nTof_x17/MX17_Simulation/` already loads the response JSON
   and has the machinery.
2. **Secondary, cheap and readable:** maximum local excess over the fitted
   continuum, and the peak-to-FWHM ratio.

Deliverable: **"significance vs x/X₀" — the curve that tells us what a budget
reduction is worth.** Expect diminishing returns; find the knee. That knee, not a
round number, is the material-budget target.

### 2.3 Products

- `opening_angle/smear_scan.py` — the truth spectrum smeared at
  x/X₀ ∈ {0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.26, 2.0} %.
- The money plot: truth, n_TOF as-built, and the GANIL design candidate, on one axis.
- The significance-vs-budget curve with the knee marked.

---

## Part 3 — Scattering contribution breakdown

Deliverable: per-layer attribution for the current apparatus, refreshed and
extended, then the same accounting for each GANIL design candidate.

Beyond the flat table in Part 0, three things need doing that the flat table hides:

1. **Path length, not thickness.** A pair born off-axis in a big cell exits at
   oblique incidence through the cell wall and the MM window. Weight each layer by
   the *actual* path-length distribution over the vertex distribution and the
   accepted solid angle, not by normal incidence. In a 10 cm-diameter cell this is
   a large effect and it is the main reason the cheap estimate could be optimistic.
2. **Where the scatter sits along the flight path.** The 96 %-retention argument
   depends on the scatterer being close to the vertex. In a large cell, the gas
   itself is distributed and the wall is 5 cm out, not 1.1 cm — the geometry of the
   argument changes and the chord estimators recover some ground. Recompute the
   effective scatter point s_eff for each candidate.
3. **Energy weighting.** Everything scales as 1/(βp), so the budget matters most
   for the soft leg. Report the breakdown weighted by the actual accepted pair
   spectrum, not at a nominal 10 MeV/c.

Products: `scattering_budget/breakdown.py` (absorbs and corrects the existing
`3he_material_budget/he3_material_budget.py`), a stacked per-layer figure per
design, and a table of "θ₀ removed per gram removed" so we can rank engineering
effort by physics return.

---

## Part 4 — The ³He cell for NFS: pressure, size, and the helium barrier

This is the core design work and the reason the facility change is attractive.
Numbers below come from `docs/anchor_vessel.py`.

### 4.1 The scaling law

Three relations govern the whole design.

- **Rate** (thin-target MeV regime) ∝ areal density along the beam × neutrons
  intercepted ∝ **P · L · R²**, if the beam is collimated to fill the cell.
- **Radial gas budget** ∝ ρ · R ∝ **P · R**.
- **Structural wall budget**: hoop stress σ = P·R/t, so the wall mass per unit area
  is ρ_w·P·R/σ ∝ **P · R**.

Both scattering terms scale with the same product **P·R**, while rate scales with
P·L·R². Two consequences, and they are not the ones I assumed in the first draft:

1. **At fixed scattering budget, rate ∝ R · L.** Make the cell as long as the
   Micromegas allow and as wide as the beam allows. This is the correct form of the
   "use the whole 8 cm beam over the whole 40 cm detector" instinct — but it only
   holds if the NFS collimation can actually be opened to fill the larger cell. If
   the aperture is fixed, a bigger cell at a longer flight path intercepts the *same*
   neutrons over more wall, and is strictly worse. **Confirm the collimator options
   with NFS before committing to a diameter** (§5.2).
2. **There is a floor, and it changes the answer.** The wall cannot be made thinner
   than what is manufacturable and handleable, call it t_min ≈ 0.30 mm for a wound
   CFRP shell. Below P·R = σ·t_min the budget stops improving, and lowering pressure
   further buys **no resolution at all** while costing rate linearly.

### 4.2 Where the floor sits — the answer to "can we hold the pressure?"

At R = 5 cm, t_min = 0.30 mm and an allowable hoop stress of 500 MPa (wound carbon,
safety factor ~3–4 on a ~1500–2000 MPa laminate), the floor sits at

> **P_floor = σ·t_min/R = 500 × 0.30 / 50 = 30 bar**

Scan of the radial budget, 0.30 mm floor enforced, 50 µm Al barrier included:

| P [bar] | R [cm] | shell t [mm] | gas | shell | barrier | **total x/X₀** |
|---|---|---|---|---|---|---|
| 5 | 5.0 | 0.30 (floor) | 0.0044 % | 0.109 % | 0.056 % | **0.170 %** |
| 10 | 5.0 | 0.30 (floor) | 0.0089 % | 0.109 % | 0.056 % | **0.174 %** |
| 20 | 5.0 | 0.30 (floor) | 0.0177 % | 0.109 % | 0.056 % | **0.183 %** |
| 30 | 5.0 | 0.30 (floor) | 0.0266 % | 0.109 % | 0.056 % | **0.192 %** |
| 50 | 5.0 | 0.50 | 0.0443 % | 0.182 % | 0.056 % | **0.282 %** |

**Read this table as the answer to the pressure worry.** Dropping from 30 bar to
5 bar costs a factor 6 in rate and buys 0.192 % → 0.170 %, which is a 6 % improvement
in θ₀. That is a terrible trade. Conversely 50 bar costs 47 % more budget than 30 bar
for 67 % more rate — roughly break-even, and it leaves the comfortable regime.

> **Working design point: R = 5 cm, P ≈ 30 bar, L = 40 cm.** Sitting exactly at the
> wall floor is where the physics stops paying for pressure. If the vessel engineering
> says 30 bar is not achievable, **10–20 bar costs almost nothing in resolution** —
> the budget is floor-dominated there — and only costs rate. That is a much more
> comfortable place to be squeezed than the first draft's 50 bar suggested.
>
> Areal density at 30 bar × 40 cm = 0.150 g/cm² = **0.60× the n_TOF cell**, so we
> give up 40 % of the per-neutron rate and expect to win it back several times over
> from the NFS flux (§5.3).

The requested "be open to fewer events for a sharper peak" trade therefore has a
specific and slightly surprising shape: **below the wall floor there is no sharper
peak to buy.** The lever that still works below the floor is the *barrier*, §4.3.

### 4.3 Is aluminium the only ³He barrier? No.

Short answer: **any continuous metal is an excellent helium barrier at room
temperature**, and beryllium is four times better than aluminium per unit thickness.
Aluminium is conventional, not uniquely capable.

The physics: helium is a noble gas. It does not dissociate or dissolve appreciably
in a metal lattice, so permeation through sound metal at room temperature is
negligible — this is precisely why helium leak detection works, and why every
composite overwrapped pressure vessel for helium service uses a metal or thermoplastic
liner rather than relying on the composite. What actually leaks is the **epoxy matrix
of the CFRP**, elastomer seals, glass and quartz, and pinholes or grain boundaries in
evaporated thin films. The engineering problem is continuity over ~1500 cm², not the
choice of metal.

Barrier candidates ranked by scattering cost per unit thickness:

| material | ρ [g/cm³] | X₀ [g/cm²] | x/X₀ per 100 µm | relative to Al |
|---|---|---|---|---|
| **Be** | 1.848 | 65.19 | **0.028 %** | **×0.25** |
| Al | 2.699 | 24.01 | 0.112 % | ×1.00 |
| Ti | 4.54 | 16.16 | 0.281 % | ×2.50 |
| stainless | 7.9 | 13.84 | 0.571 % | ×5.08 |
| Cu / Ni | ~8.9 | ~12.8 | ~0.70 % | ×6.2 |

So: **everything heavier than aluminium is worse, and only beryllium is better.**

**Beryllium is the interesting option, because it can be the barrier *and* the
structure**, removing the CFRP floor entirely. Thin-wall Be tubes at exactly this
diameter are established technology — accelerator beam pipes and X-ray windows —
and Be is helium-tight. Hoop check at R = 5 cm:

| P | t | σ_hoop | verdict (Be yield ~240–345 MPa) |
|---|---|---|---|
| 10 bar | 0.25 mm | 200 MPa | tight but plausible |
| 10 bar | 0.50 mm | 100 MPa | comfortable |
| 30 bar | 0.50 mm | 300 MPa | at the limit |
| 30 bar | 1.00 mm | 150 MPa | comfortable |

Against Be: cost, procurement lead time, brittleness, toxicity of machining dust
(a real safety-case item at a user facility), and joining to end flanges.

**Non-metal barriers worth one bench test, because they are essentially massless:**
atomic-layer-deposited Al₂O₃ at 10–50 nm is conformal and pinhole-free and is the
standard OLED encapsulation barrier; ALD/polymer multilayers do better still. Applied
to the CFRP inner surface or to a polymer liner, the mass contribution is nil. It is
unproven at 30 bar over this area and over months, but the test is cheap and the
payoff is removing the barrier term from the budget entirely.

**Reframe the requirement.** We do not need hermetic, we need a **leak budget**.
A 3 litre cell at 30 bar holds ~90 bar·litre, about 3.7 mol of ³He. Losing 1 % per
month is entirely acceptable with a top-up and recovery system. Computing the
tolerable permeation rate and testing candidates against *that* is far more likely
to succeed than demanding zero. Note also that ³He is expensive and supply-limited,
so a closed recovery loop is probably wanted regardless.

### 4.4 Candidate builds

Radial exit budget, 40 cm cell, helium bag in the gap where noted. The last column is
the rate penalty relative to the n_TOF cell at equal neutron flux.

| build | gas | barrier | shell | gap | window | **total** | θ₀ @10 MeV/c | areal (× n_TOF) |
|---|---|---|---|---|---|---|---|---|
| n_TOF as built | 0.089 % | 0.674 % Al 0.6 mm | 0.327 % | 0.049 % | 0.094 % | **1.233 %** | 7.22° | ×10.0 |
| A: 50 bar, R=5, Al 100 µm | 0.044 % | 0.112 % | 0.182 % | 0.049 % | 0.094 % | **0.482 %** | 4.32° | ×1.00 |
| B: 30 bar, R=5, Al 50 µm | 0.027 % | 0.056 % | 0.109 % | 0.003 % | 0.094 % | **0.289 %** | 3.26° | ×0.60 |
| C: 30 bar, R=5, Be 100 µm | 0.027 % | 0.028 % | 0.109 % | 0.003 % | 0.043 % | **0.210 %** | 2.74° | ×0.60 |
| D: 10 bar, R=5, Be 250 µm structural | 0.009 % | 0.071 % | — | 0.003 % | 0.043 % | **0.126 %** | 2.06° | ×0.20 |
| E: 10 bar, R=4, Al 25 µm + CFRP 0.3 | 0.007 % | 0.028 % | 0.109 % | 0.003 % | 0.043 % | **0.190 %** | 2.59° | ×0.20 |

θ₀ falls from 7.2° to 2.1–3.3°, a factor **2.2 to 3.5**. Naively that maps σ68 ≈ 15°
onto **4–7°** — but only if nothing else takes over, which is exactly what Part 6
exists to check, and which the D-vs-E comparison already hints at: builds D and E
differ by 50 % in budget and buy very little, because by then the **MM window and the
drift gas dominate**, not the cell.

**Build C is the current recommendation to carry forward**: 30 bar sits at the wall
floor, beryllium removes the barrier as a significant term, and the areal density is
within 40 % of the n_TOF cell. Build D is the "spend statistics for sharpness" option
and the table says it is **not worth it** — it costs a factor 3 in rate for 0.7° in θ₀.

### 4.5 Remaining engineering questions

- **Code compliance.** A 30 bar, ~3 litre vessel is a pressure vessel under EU/GANIL
  rules. Find out early what safety factor and certification path GANIL requires,
  because that sets t_min and therefore the entire optimisation above. A composite or
  beryllium vessel in a user facility may face a harder review than a steel one.
- **Which barrier, and proven how.** Rank Be foil, Al foil, ALD-coated liner and
  metallised polyimide against the leak budget from §4.3. Bench test required.
- **Geometry.** Is a cylinder right? A rectangular cell matched to the four-arm MM
  layout shortens the exit path for the pairs that matter, at the cost of a harder
  pressure design. Worth one comparison.
- **End windows.** The beam enters and exits along the axis, so those windows are not
  in the pair exit path and can be thick. Confirm — with a 40 cm cell they also set
  the neutron in-scattering background.
- **³He inventory.** ~90 bar·litre. Compare against what we already hold; plan
  recovery.
- **Off-axis vertices.** A vertex 5 cm off axis exits obliquely through the cell wall
  and hits the MM at a different angle. Part 3 handles this; it is the main way the
  cheap estimate could be optimistic.

### 4.6 The other levers, now that the cell is small

Once the cell reaches ~0.2 %, the ranking inverts and the detector dominates:

1. **MM window stack** (0.094 % as built) — now 30–45 % of the total. The **9 µm Cu
   cathode alone is 0.063 %**. Replacing it with aluminium at equal conductance is
   ~3× less x/X₀ and takes the window stack to 0.043 %. Nobody has had a reason to
   care about this before; now it is one of the two biggest terms.
2. **Air gap** (0.049 % over 15 cm) — a helium bag removes it almost entirely
   (0.003 %) and is cheap. Do it.
3. **CFRP shell** (0.109 % at the floor) — only beryllium or a thinner floor beats it.
4. **Drift gas and gap** — not in the upstream budget at all, but it is where the new
   resolution floor probably lives. Part 6.

Products: `vessel_design/cell_optimizer.py` — scans (P, R, L, barrier, shell) with the
manufacturing floor and an allowable-stress parameter, returns x/X₀, hoop stress, areal
density and a rate index; `common/materials.py` with X₀ in g/cm² (not cm — the current
`3he_material_budget` convention hides the density trade that drives all of §4.3).

---

## Part 5 — The facility: does NFS deliver the right neutrons?

### 5.1 The gating question

NFS with the 8 mm rotating Be converter and 40 MeV deuterons gives a **breakup
spectrum spanning ~1.5–42 MeV, peaking near 14–17 MeV** (max
(17.3 ± 0.5)×10⁹ n/µC/sr/MeV at 17 MeV; >10⁹ over 1.5–35 MeV). Our physics wants
E\* near 20.6 MeV, i.e. **E_n below ~2 MeV**, which is the thin bottom edge of that
spectrum. Above it the shoulder slides toward the IPC-rich small-angle region (§1.2).

**This is the go/no-go, and it must be answered first.** Three possible outcomes:

1. The 1.5–2 MeV tail carries enough flux → run there, accept ~17× below the
   spectral peak, keep the favourable θ_min ≈ 108°.
2. It does not → consider the **p+Li quasi-monoenergetic option** (0.5–30 MeV,
   thin ⁷Li converter, ~1.42×10⁵ n/cm²/s at 5 m — an order of magnitude below thick
   Be) tuned to a chosen E_n. Lower flux, but the *right* flux.
3. Neither works → NFS is the wrong facility for this measurement and the study
   should say so plainly and redirect. That is a legitimate and cheap outcome.

Quantify by folding the measured NFS spectrum against σ_nγ(E_n) from `data/He3.h5`
and against the θ_min-vs-E\* separation from §1.2, in one plot: **X17 yield per day
× peak-to-continuum, vs the E_n window selected**.

### 5.2 Beam and geometry numbers gathered so far

From Ledoux et al., *First beams at Neutrons For Science* (arXiv:2110.02282) and
the 2026 PS-PPAC beam-monitor paper (arXiv:2601.07896):

| quantity | value |
|---|---|
| TOF hall length / usable flight paths | 28 m / 5–30 m |
| converter | 8 mm rotating ⁹Be, 40 MeV deuterons |
| deuteron current (2026 monitor run) | 7.60 ± 0.05 µA; facility max 50 µA |
| flux, thick Be, at 5 m | 5.88×10⁶ n/cm²/s |
| flux, thin Be (0.5 mm) / thin Li (1.5 mm) at 5 m | 3.22×10⁵ / 1.42×10⁵ n/cm²/s |
| beam spot | 1.7 cm radius at collimator exit; 44.4 ± 0.4 mm diameter at 7.41 m with the 25.55 mm collimator; ~13 cm at the hall end |
| beam divergence | 3.08 ± 0.07 mrad |
| edge fall-off (10–90 %) | 4.9 ± 0.4 mm |
| TOF repetition rate | 22 kHz (N = 400 bunch selection), 45 µs period |
| electronic time resolution | 80 ps |
| energy resolution | better than 0.4 MeV FWHM at 30 MeV, L = 15.7 m |
| thermal contamination | (3.85 ± 0.43)×10⁻⁵ of fast |

**The ~8 cm spot the design is aimed at** sits around 10–12 m from the converter
with the existing collimator, or closer with a larger aperture. Two things follow
and both need checking with the NFS team:

- Flux falls as 1/L², so an 8 cm spot at ~10 m gives roughly 1.5×10⁶ n/cm²/s
  (~9×10⁷ n/s over the spot). Opening the collimator instead of moving back keeps
  more flux — ask what apertures exist.
- The **sharp 4.9 mm edge fall-off is excellent news**: a well-defined beam that
  fills a 40 cm cell uniformly in one dimension and is cleanly bounded in the other.

### 5.3 Rate estimate (order of magnitude, to be replaced by a folded calculation)

At 1.5×10⁶ n/cm²/s over an 8 cm spot, for the **build C cell** (30 bar × 40 cm,
3.0×10²² ³He/cm², i.e. 0.60× the n_TOF areal density), and σ_nγ in the 10–50 µb range:

| σ_nγ | captures/s | IPC pairs/day (α = 3.5×10⁻³) | X17/day at 0.025 | X17/day at 1×10⁻³ (working) |
|---|---|---|---|---|
| 10 µb | 15 | 4.6×10³ | 114 | 4.6 |
| 20 µb | 30 | 9.1×10³ | 228 | 9.1 |
| 50 µb | 76 | 2.3×10⁴ | 571 | 23 |

For comparison, n_TOF EAR2 gave **22.5 X17/day in the 0.2–2 MeV window** at the
0.025 normalisation. Like for like, NFS is plausibly **comparable to several times
better in rate** despite the thinner cell, because the flux is higher. At the
pessimistic normalisation we are adopting, the absolute numbers fall to a few X17 per
day and **the exposure needed becomes the binding constraint** — which is exactly why
the smeared-bump study in Part 2 has to be done before any hardware is designed.

Every entry is hostage to §5.1 (which E_n window is usable) and to D7 (σ_nγ is a flat
band here, not a folded evaluation). Do not quote these outside the group.

### 5.4 Timing and background environment

- **TOF window.** At 10 m, 2 MeV neutrons arrive at 512 ns and 0.2 MeV at 1.6 µs,
  inside the 45 µs bunch period — **no wrap-around**, unlike EAR2 where the >1 ms
  thermal gate was a whole analysis in itself.
- **The thermal background largely disappears.** The 3.9×10⁻⁵ thermal fraction means
  the Al(n,γ) 7.72 MeV capture line that dominated the n_TOF trigger background is
  strongly suppressed. This is a significant simplification and it should be stated
  as one of the main arguments for the facility change.
- **New backgrounds to assess:** fast-neutron elastic recoils in the drift gas and
  vessel, ³He(n,p)t protons in the cell (huge rate, but low energy and contained),
  (n,xn) and (n,charged) in the Al/CFRP, the γ flash from the converter at 40 MeV,
  and beam-correlated room background over 28 m of hall.
- **Trigger and readout.** The n_TOF decision was trigger-free ~10 µs per-pulse
  readout. At 22 kHz that becomes a 45 µs period — check the DREAM readout can live
  with the duty cycle, or whether the rep rate should be lowered further.

---

## Part 6 — What the new resolution floor actually is

Once the upstream budget drops from 1.26 % to ~0.3 %, the terms that were
negligible stop being negligible. This part exists so we do not design a beautiful
0.3 % cell and then discover the detector cannot use it.

Terms to evaluate, all of which were buried under the wall before:

1. **Drift-gas multiple scattering** over the 30 mm ArIso gap, and the case for a
   lighter drift gas (He/isobutane is already defined in `DetectorConstruction.cc`).
2. **MM point resolution and track length.** The Geant4 study measured that a
   0.5 mm hit smear costs ≤ 0.5° at 15.5°; at 7° it is a much larger fraction.
   `nTof_x17/angle_res_vs_drift_gap.py` is the existing starting point.
3. **Reconstruction reality.** Per `nTof_x17/CLAUDE.md`, angles must come from the
   waveform-first forward model in `wft/`, not from combined-hit times, which read
   ~4° too steep. Any resolution claim in this study has to be stated against the
   reconstruction we will actually run.
4. **Vertex spread.** In a 10 cm-diameter, 40 cm-long cell, the chord estimators
   (`vline`, `nomline`) become useless — the transverse vertex is unknown to ±5 cm
   at L ≈ 20 cm. The **PCA fit estimator is vertex-free and becomes the primary**;
   confirm it holds up, and check whether two-track vertexing becomes viable once
   the tracks are straighter.
5. **Geometry re-optimisation.** With a large source and a low budget, the optimum
   MM distance is not necessarily the current 20.4 cm. Longer lever arm dilutes the
   vertex ignorance and the point resolution but costs solid angle and adds gap
   material. Scan it.

Deliverable: **total σ68 vs upstream x/X₀** with the floor terms included — the
curve that says where further material reduction stops paying. Overlay it on the
Part 2 significance curve.

---

## Part 7 — Geant4 hand-off (down the road, not now)

When the cheap study converges on a design, port it. The changes needed in
`MX17_Full_Geant` are well-scoped:

- `SimConfig.hh` / `DetectorConstruction.cc`: replace the STEP polycone capsule with
  a parameterised low-pressure cell (P, R, L, liner material and thickness,
  structure thickness); the ³He material is currently hard-coded at 62.7 mg/cm³.
- `X17PrimaryGenerator.cc`: the corrected IPC differential coefficients from §1.1
  and the E_n-dependent kinematics from §1.2 (E\* and the CM boost). This is
  already flagged as an open item in the angular note.
- Neutron mode: swap the EAR2 flux and radial-profile ROOT files for NFS spectra
  and the measured beam profile.
- Optionally a helium bag in the gap and a thinner cathode.

Then re-run the pairs campaign, re-extract `geant4_response.json`, and close the
loop against the analytic prediction. **The value of Parts 1–6 is that we arrive at
Geant4 with one design to validate rather than a scan to explore.**

---

## Proposed repo structure

```
x17_facility_search/
  docs/PLAN_GANIL_NFS.md          this file
  common/
    materials.py                  X0 in g/cm2, densities, gas mixtures
    highland.py                   theta0, space angle, tails (absorbs 3he_material_budget)
    kinematics.py                 E* vs E_n, CM boost, pair kinematics
    ipc.py                        Schlueter-Soff differential coefficients
  opening_angle/                  Parts 1-2
  scattering_budget/              Part 3
  vessel_design/                  Part 4 (cell_optimizer.py, barrier ranking)
  facility/                       Part 5 (NFS spectra, rates, TOF)
  resolution_floor/               Part 6
  docs/anchor_kinematics.py       E*(E_n), boost, theta_min table
  docs/anchor_vessel.py           P*R scaling, barrier ranking, candidate builds
  docs/anchor_numbers.py          budget tables, NFS rate scoping
```

`3he_material_budget/he3_material_budget.py` folds into `common/highland.py`, with
the plane-projected-vs-space-angle labelling corrected and X₀ moved to g/cm².

---

## Ordering and gates

| # | Work | Gate |
|---|---|---|
| 1 | Truth spectrum with E*(E_n) kinematics, simplified continuum, pessimistic normalisation (§1.0, §1.2) | the money plot exists |
| 2 | NFS flux folded against σ_nγ and the θ_min separation (§5.1) | **go/no-go on the facility** |
| 3 | Smearing model validated against `geant4_response.json` (§2.1) | reproduces σ68 = 15° at 1.26 % |
| 4 | Significance vs x/X₀ → the budget target (§2.2) | a knee, with a number |
| 5 | Breakdown with real path lengths and off-axis vertices (§3) | ranked list of what to remove |
| 6 | Cell design scan + barrier bench test (§4) | a candidate build with a budget |
| 7 | Resolution floor: window, drift gas, MM distance (§6) | the design is actually usable |
| 8 | Proper IPC continuum and normalisation band (§1.1, §1.3) | before anything is published |
| 9 | Geant4 port (§7) | later |

Steps 1 and 2 are independent and can run in parallel. **Step 2 should not wait** —
if NFS cannot give us neutrons in a usable energy window, Parts 4 and 6 are moot, and
that answer is a few hours of folding, not weeks.

---

## Deferred — simplifications currently in force

Every entry here is a knowing approximation taken to get a first answer quickly.
**None of them may survive into the CERN-site note or any external presentation.**

| # | Simplification | Why it is acceptable now | What a proper job needs |
|---|---|---|---|
| D1 | IPC continuum from dN/dM ∝ 1/M with isotropic decay | we only need *a* smooth continuum to test whether a sharp bump survives | Schlüter–Soff differential coefficients per multipole, validated against BrIcc ≤6 MeV and the ¹²C datum, cross-checked against ATOMKI's measured angular correlation (§1.1) |
| D2 | X17 strength fixed at the pessimistic ~1×10⁻³ per IPC pair | a positive result at the pessimistic value is robust; an optimistic one proves nothing | resolve the 0.025 benchmark against ATOMKI's B_x, settle what B_x is relative to for an M0 transition, quote a band (§1.3) |
| D3 | E0/M0 γ-dark channel omitted entirely | omitting it is conservative — it can only add signal | ⁴He R-matrix for the ¹S₀ n+³He → g.s. E0 amplitude, normalised by the measured (e,e′) monopole form factor |
| D4 | Multipole mix vs E_n not modelled | affects the continuum shape, not the presence of a bump | M1/E1 content from Wervelman et al. and the ENDF evaluation in `data/He3.h5` |
| D5 | Highland Gaussian core, no Molière tail | the tails matter for the soft-leg population, not for the peak position | calibrate the tail fraction against the measured per-KE ψ tables |
| D6 | Normal-incidence path lengths | fine for the small n_TOF cell | off-axis vertices in a 10 cm cell exit obliquely; weight by the real vertex and acceptance distribution (§3) |
| D7 | σ_nγ taken as a flat 10–50 µb band | order-of-magnitude rate scoping only | fold the ENDF evaluation against the measured NFS spectrum (§5.1) |
| D8 | Detector response frozen at the n_TOF geometry | the response JSON is measured and trustworthy there | re-extract after the Geant4 port with the new cell and any window changes (§7) |
| D9 | Wall model is thin-wall hoop stress with a single allowable | correct scaling, adequate for ranking designs | real laminate design, end caps, buckling, and whatever safety factor GANIL's pressure code demands (§4.5) |
| D10 | Beam assumed to fill the cell exactly | the scaling law in §4.1 depends on it | actual NFS collimator apertures and the measured profile at the chosen flight path (§5.2) |

---

## Publication

The end product is a note on the CERN site (`dylan-neff.web.cern.ch/notes/`), via the
`publish-note` skill. **Do not publish until D1, D2 and D7 are closed** — the
pessimistic normalisation and the placeholder continuum are fine for an internal
working document and not fine for anything with a URL. Interim figures can go on the
X17 analysis board instead.

---

## Open questions for you

1. **Is the 0.025 X17-per-IPC benchmark yours, Alberto's, or inherited?** Knowing its
   provenance is faster than re-deriving it, and it is a factor ~30 against the
   ATOMKI-inferred value we are now using.
2. **Is E_n above ~2 MeV acceptable physics?** The shoulder moves from 109.6° to 99.3°
   over 0–2 MeV and to 65.7° at 14 MeV, sliding into the IPC-rich region. If we
   specifically want the 20.2/21.0 MeV ⁴He states ATOMKI implicated, we are confined
   to E_n ≲ 1.7 MeV and NFS's spectrum is a poor match. This decides the study.
3. **Beryllium: acceptable at GANIL, and can we procure a thin-wall tube?** It is the
   only barrier material better than aluminium, and it can double as the structure.
   Toxicity and cost are the obstacles, not physics.
4. **What does GANIL's pressure code demand?** It sets the minimum wall thickness,
   which sets P_floor ≈ 30 bar, which sets the whole design point in §4.2.
5. **Do we have an NFS contact?** The collimator apertures and the achievable spot at
   a given flight path are the two numbers the public papers do not pin down, and the
   §4.1 scaling law depends on them.
