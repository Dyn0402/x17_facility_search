# Which neutron facility could do the ³He X17 search? A world survey

Started 2026-10-20. Code: `survey_yield.py`, `survey_absorbed.py`, `survey_fast.py`, `catalogue.py`.
Outputs: `out/`. Sources ledger: `SOURCES.md`. Catalogue: `facilities.csv`; catalogue with the model numbers: `out/triage.csv`.

**Question (Dylan, 2026-10-20).** The neutron facilities studied so far are not feasible for an X17 search
with realistic statistics in a few weeks of ³He running. Survey every current and near-future neutron
facility in the world. Use the best studied ones (thermal: ILL PF1B; fast: GANIL NFS) to eliminate the
rest, and put on a "potential" list only those worth a dedicated study.

---

## 0. Answer — read this first

**The thermal class is closed, the pulsed white sources are closed, and two facilities nobody had
looked at go on the potential list.** Both are continuous sources with a soft spectrum: the FRM II
fission-converter beam (MEDAPP) and the Birmingham 30 mA ⁷Li(p,n) source (HF-ADNeF).

1. **Thermal and cold beams (§3): no facility in the world beats ILL PF1B.**
   - The yield per absorbed neutron is the same everywhere (both channels are 1/v).
   - The apparatus's own rate walls (Micromegas occupancy + DREAM) put the best reach at ~6×10¹⁰
     absorbed n/s, and PF1B already delivers 1.2×10¹¹. So MEPHISTO and ESS ANNI, which match PF1B,
     reach the same 5.3×10⁻³ (×3.2 short); everything else is lower.
   - The class reopens only if the detector and DAQ change.
   - Epithermal (BNCT) beams gain ×3.6 per neutron: 2.5×10⁻³, **MARGINAL**.
2. **Per neutron, thermal is the worst energy (§2).** A 1 MeV neutron crossing a 30 bar × 40 cm cell
   gives ~200× the pairs of a thermal neutron absorbed in it. At thermal, (n,p) takes every neutron; at
   MeV the cell is thin and σ_nγ is ×1.5 larger.
3. **Fast sources (§4), scaled from the NFS Geant4 analysis (it reproduces NFS exactly):**
   - **Pulsed white sources are throttled by their duty factor**, not their flux. n_TOF EAR2 reaches
     0.12, CSNS Back-n 3.6×10⁻³ (at 185 or 500 kW), GELINA 3.2×10⁻³ at best. LANSCE WNR comes out
     best at 1.7–8.5×10⁻³ (**MARGINAL**, on estimated inputs).
   - **NFS's problem is its spectrum:** 2 % of its neutrons are in the ATOMKI-like window and 87 % are
     above 8.5 MeV. SARAF-II (×100 the current, same spectrum, CW) gains nothing.
   - **Continuous, soft sources come out on top.** They put 70–80 % of the neutrons in the window and
     nothing above 8.5 MeV:

     | facility | 50 d, X17 at E\* ≤ 22 MeV | state |
     |---|---|---|
     | **FRM II MEDAPP** (fission, 3.2×10⁸ n/cm²/s) | 2×10⁻⁴ – 4.6×10⁻³ | reactor off since 2020 |
     | **Birmingham HF-ADNeF** (⁷Li(p,n), > 3×10¹³ n/s, cell 2 m from a shielded target) | 2.5×10⁻⁴ – 3.7×10⁻³ | operating since Dec 2023 |

     ATOMKI's ⁴He value is 1.5×10⁻³; NFS gets 0.016 in the same convention.
   - The range is the model's one big unknown: the singles that < 3 MeV neutrons make in the arms
     (§4.1). N4 sees too few soft neutrons to measure it.
     - Low end: N4's per-energy table.
     - High end: every neutron as bad as NFS's average.
     - Even the high end is 2–3× ATOMKI's value, ×4 better than PF1B.
4. **Generators and near-threshold Li (§4.2):**
   - D-D generators are clean but too weak by ~×10 once shielded (**MARGINAL**).
   - D-T has no window signal (**WINDOW**).
   - LiLiT and FRANZ: keV neutrons still give ×40 thermal (**WATCH**).
5. **Catalogue (§5): 59 rows.**

   | verdict | rows |
   |---|---|
   | STUDIED | 4 |
   | POTENTIAL | 2 |
   | MARGINAL | 5 |
   | WATCH | 8 |
   | DOMINATED | 24 |
   | DUTY | 4 |
   | WINDOW | 4 |
   | TARGET | 2 |
   | ACCESS | 6 |

**Next (§6.3):**
1. One Geant4 run with a soft (fission / ⁷Li(p,n)) beam on the NFS geometry. It measures the
   soft-neutron singles and collapses every CW bracket at once.
2. Add the room and dump.
3. Ask FRM II (restart, MEDAPP access) and Birmingham (an unmoderated collimated port).

**For the paper (§7):** the requirement can be stated as a figure of merit: pairs in the ATOMKI window
per single in the arms. Thermal and pulsed sources fail it for structural reasons, and continuous soft
sources pass it.

---

## 1. Method

### 1.1 The figure of merit

Every facility runs the same nuclear reaction: n + ³He → ⁴He\* → ⁴He + e⁺e⁻, IPC or X17. The facility
sets three things:

1. **How many IPC pairs per second it makes in the ³He.** That is neutrons/s through the cell times the
   pair yield per neutron, P(E_n) (§2).
2. **What else it makes, per second, in the arms.** Singles from scattered beam neutrons and source γ.
   They feed the accidentals, the Micromegas occupancy and the DREAM dead time: the **rate walls**.
3. **Where in E\* the pairs sit.** ATOMKI measured ⁴He at E\* ≈ 20.5–21 MeV. E_n ≤ 2.75 MeV keeps
   E\* ≤ 22.1 MeV and θ_min ≥ 99°. Above that, the X17 signal depends on an unknown evolution of
   X17/IPC with E\*.

The reach is quoted as **X17/IPC at 3σ in 50 days** (one ILL cycle, "~weeks"), against ATOMKI's ⁴He value
1.5×10⁻³ (the NFS convention), or ⁸Be's level 1.64×10⁻³ (the ILL convention).
The 2.5×10⁻² of the old n_TOF rate table is not used anywhere here: it has no source and is ~17×
above ATOMKI's own numbers (`docs/X17_IPC_NORMALISATION.md`, 2026-10-20).

*2026-10-20.* The dashboard also quotes **days to the ATOMKI strength**: the reach falls as 1/√T at a
fixed beam rate (Fisher, background-dominated), so days = 50 × (ρ₅₀ / 1.5×10⁻³)². It is a statistics-only
time: no systematic floor, setup or beam-off days. FRM II MEDAPP < 1 d – 1.3 yr, Birmingham 1.4 – 300 d, CSNS Back-n 290 d – 350 yr, n_TOF EAR2 ~900 yr (duty),
ILL PF1B 620 d (≈ 12 cycles).

### 1.2 Two anchors, two scaled models

| class | anchor (Geant4) | model | carries over |
|---|---|---|---|
| neutrons absorbed in the ³He (cold, thermal, epithermal) | ILL PF1B, `ill/FEASIBILITY_SIM.md` §13 | `survey_absorbed.py` | reach vs absorbed rate per class (walls_tubeMy_e14.csv) |
| neutrons that cross the cell (≳ 10 keV) | GANIL NFS, `ganil_nfs/FEASIBILITY_SIM.md` §4 | `survey_fast.py` | the full NFS event lists per E_n bin, re-weighted |

Neither model is a new simulation. Each carries one Geant4 campaign over to other beams. They are
triage tools: a facility they put well behind an anchor is eliminated; one they put near or past
ATOMKI's strength goes on the potential list for its own Geant4 study.

### 1.3 Verdicts

`STUDIED`, `POTENTIAL`, `MARGINAL`, then the elimination reasons:
- `DOMINATED`: same class as an anchor and below it;
- `DUTY`: a pulsed white source, throttled by its per-pulse load;
- `WINDOW`: neutrons only far above E\* ≈ 22 MeV;
- `TARGET`: the flux needs the cell next to the production target, which makes the same pairs;
- `ACCESS`: closed, no extracted beam, or not open to a CERN collaboration;
- `WATCH`: not running yet; the verdict it would get is given.

Definitions in `catalogue.py`.

## 2. The yield curve: a 1 MeV neutron is worth ~200 thermal ones

`survey_yield.py` → `out/yield_vs_En.png`, `out/spectra_summary.csv`.

For a cell of areal density nL, the IPC pairs per neutron entering it are

P(E) = σ_nγ/σ_tot · (1 − e^(−nLσ_tot)) · α(W),

with ENDF/B σ and the Born pairs per photon α (E1; the thermal M1 + E0 value comes out within 3 %).

| E_n | what happens in the cell | P, 30 bar × 40 cm cell |
|---|---|---|
| thermal | (n,p) = 5316 b absorbs every neutron; σ_nγ/σ_np = 1.0×10⁻⁸ | **4.8×10⁻¹¹** (the repo value) |
| 1 eV–1 keV | both 1/v: nothing changes | 4.8–8×10⁻¹¹ |
| 1–100 keV | direct E1 capture grows faster than 1/v | 1×10⁻¹⁰ → 3×10⁻⁹ |
| 0.2–2.75 MeV | the cell is thin: P ≈ nLσ_nγα, σ_nγ = 30–90 µb | **0.5–1.3×10⁻⁸** |

Folded over source spectra (P relative to thermal):

| spectrum | P / P_thermal | fraction in 0.2–2.75 MeV | fraction > 8.5 MeV |
|---|---|---|---|
| epithermal 1/E, 0.5 eV–10 keV (BNCT) | 3.6 | 0 | 0 |
| LiLiT / near-threshold ⁷Li(p,n), kT 25 keV | 39 | 0.5 % | 0 |
| thick ⁷Li(p,n), E_p 2.6 MeV | 128 | 81 % | 0 |
| ²³⁵U fission (Watt) | 208 | 71 % | 0.4 % |
| D-D, 2.45 MeV | 263 | 100 % | 0 |
| CSNS Back-n (measured per-decade, ES#1) | 144 | 47 % | 12 % |
| NFS d(40)+Be | 115 | **2.2 %** | **87 %** |
| D-T, 14.1 MeV | 111 | 0 | 100 % |

Three consequences organise the whole survey:

1. **Thermal is the worst energy per neutron.** Only flux can make up the ×200, and §3 shows the
   detector, not the facility, caps the usable flux.
2. **Epithermal beams gain only ×3.6.** The E1 rise starts above ~1 keV, where a 1/E spectrum has
   little weight.
3. **Among fast beams, the spectrum shape matters as much as the flux.** NFS puts 2 % of its neutrons in
   the ATOMKI-like window and 87 % above 8.5 MeV, where they make the accidentals and the correlated
   background. A fission or ⁷Li(p,n) spectrum puts 70–80 % in the window and almost nothing above.

## 3. Cold, thermal and epithermal beams: closed by the rate walls

`survey_absorbed.py` → `out/absorbed_reach.{csv,png}`.

The ILL study (`ill/FEASIBILITY_SIM.md` §13.4) gives the 50-day reach vs absorbed rate R, with the
He flight tube, a mylar window, the ceiling panel and E_sum > 14. With as-is Micromegas and DREAM,
**the best reach, 5.3×10⁻³, is at R ≈ 6×10¹⁰ n/s**. PF1B can deliver 1.2×10¹¹ with a Ø5 cm spot.
**The detector, not the beam, sets the reach.** The yield per absorbed neutron is the same everywhere
(1/v), so a facility reaches the same curve up to R_max = 1.2×10¹¹ · Φ/Φ_PF1B:

| facility | capture flux [n/cm²/s] | R_max [n/s] | 50-d reach, as-is walls | × ⁸Be level | with MM occ ÷10 and a 10 µs DAQ |
|---|---|---|---|---|---|
| **ILL PF1B** | 2.2×10¹⁰ | 1.2×10¹¹ | **5.3×10⁻³** | ×3.2 | 3.4×10⁻³ |
| FRM II MEPHISTO | ≈ PF1B (expected) | 1.1×10¹¹ | 5.3×10⁻³ | ×3.2 | 3.6×10⁻³ |
| ESS ANNI (proposed) | 2.5×10¹⁰ (5 MW) | 1.4×10¹¹ | 5.3×10⁻³ | ×3.2 | 3.4×10⁻³ |
| NIST NG-C | 8.1×10⁹ | 4.4×10¹⁰ | 5.5×10⁻³ | ×3.3 | 4.5×10⁻³ |
| SNS FnPB, CARR | ~1×10⁹ | 5×10⁹ | 1.2×10⁻² | ×7.3 | 1.2×10⁻² |
| ILL FIPPS | (1.8×10⁸ n/s) | 1.8×10⁸ | 6×10⁻² | ×38 | 6×10⁻² |
| BNCT epithermal, 1×10⁹ (k = 3.6) | 1×10⁹ epi | 7.9×10¹⁰ | **2.5×10⁻³** | ×1.5 | 1.7×10⁻³ |
| BNCT epithermal, 5×10⁹ (k = 3.6) | 5×10⁹ epi | 3.9×10¹¹ | 2.5×10⁻³ | ×1.5 | **1.2×10⁻³** |

- **No cold or thermal facility in the world beats PF1B, and none could with this apparatus.** The two
  that match it (MEPHISTO, ANNI) reach the same wall. The class is closed unless the detector and DAQ
  change: occupancy ÷10 and a 10 µs DAQ give 3.4×10⁻³ (×2.1), and the IPC-only floor at 1.2×10¹¹ is
  ×1.3 (`ill/FEASIBILITY_SIM.md` §13.5). Polarisation (spin selection of E0) is the remaining physics
  lever, and PF1B has it.
- **Epithermal (BNCT) beams: marginal.** The ×3.6 per neutron brings the as-is wall to ×1.5 of ATOMKI,
  and the upgraded walls past it. Three assumptions carry this and none is checked:
  - the background per entering neutron is the ILL one;
  - the cell is the 30 bar × 40 cm one (keV neutrons cross a 1 bar cell);
  - the beam's fast-neutron and γ contamination does not matter.

  Worth a dedicated look only after the fast candidates (§4), which gain ×100, not ×3.6.

## 4. Fast neutrons: the NFS Geant4 analysis carried to every source

`survey_fast.py` → `out/fast_reach.csv`, `out/fast_reach_fig.png`, `out/fast_throttle_fig.png`.

### 4.1 Method

The NFS analysis (`ganil_nfs/sim/nfs_reach.py`, factorised correlated term) is rebuilt once per hardware
set. It gives event lists per E_n bin (0.2–25 MeV) with per-day weights for five classes: X17, E1 IPC,
correlated beam, accidentals and cosmics. A source is the same arms and the same 30 bar × 40 cm cell with
another beam, so each class is re-weighted:

| class | scaled by |
|---|---|
| X17, IPC | the source's ³He(n,γ) rate per E_n bin (neutrons/s through the cell × P(E)); below 0.2 MeV into the 0.5 MeV bin (same kinematics) |
| accidentals | the pairing rate 2δ Σ r_a r_b of singles in each bin's time window, × the NFS pass fraction (vertex + E_sum) of that bin |
| correlated beam | neutrons/s above 8.5 MeV (every NFS correlated event came from E_n > 10 MeV) |
| cosmics | the fraction of time each bin's window is open (all of it for a DC source) |
| exposure | DREAM live time (correlated + random two-arm triggers, 298 µs) × exp(−2·occ), with occ the Micromegas occupancy (singles per arm in 1 µs; the ILL convention) |

**Singles.** The forced-collision N4 run gives, per arm, singles per neutron vs the parent E_n. They are
split into two kinds:
- prompt (54 %), within 100 ns of the neutron's arrival, which travel with it;
- delayed (46 %; captures and activation at ms–s), spread uniformly in time.

A pulsed source's rate profile is built over one period, with wrap-around (WNR, 1.8 µs micropulses inside
2.5 %-duty macropulses). A DC source has no E_n tag, so it uses the summed θ fit ('θ, no TOF'); pulsed
sources use m_ee | E_n.

**Throttle.** Each source is scanned from 10⁻⁶ to 1 of its intensity (collimator, current), and the best
reach is kept.

**Validation.** `--check` reproduces the published NFS reach exactly: 3.31×10⁻³ / 0.0312 with big
plastics and 8.54×10⁻³ / 0.164 as built (14 d). The occupancy and random-trigger terms, which the NFS
analysis did not have, move NFS's 50-d E\* ≤ 22 MeV reach from 0.0164 to 0.0165.

**The one big unknown: singles from soft neutrons.** The NFS beam has 2 % of its neutrons below 2.75 MeV.
N4 therefore measures the singles of 0.2–4 MeV neutrons with a handful of MC events: zero in 0.75–1.5 MeV,
1–8×10⁻⁷ per neutron elsewhere, against 4×10⁻⁵ averaged over NFS. Every source is therefore run twice:
- **Geant4 singles:** the N4 table vs E_n, the optimistic end;
- **flat singles:** every neutron gets the NFS average, set by its > 10 MeV neutrons. This is a
  pessimistic bound for a soft source.

The truth lies between. One Geant4 run with a soft beam (§6.3) settles it for every CW source at once.

**Not in the model:** room and beam-dump return (NFS: vacuum flight tube, no hall), the source's own γ
(a crude extra-singles factor k_γ: 1 for the reactor, 0.3 for Li targets), the γ flash, and a cosmic veto
(none; cosmics sit at θ = 150–180°).

### 4.2 Results (big plastics, 50 days, best throttle)

X17/IPC at 3σ. ATOMKI ⁴He = 1.5×10⁻³. "E\* ≤ 22": X17 only from E_n ≤ 2.75 MeV (the ATOMKI-like
window; IPC everywhere). "all E\*": X17/IPC constant at every E_n (the NFS 3.3×10⁻³ convention).

| source | n/s through cell (full) | IPC/day in window (full) | E* ≤ 22: Geant4 singles | flat singles | floor | best throttle | all E* (Geant4) |
|---|---|---|---|---|---|---|---|
| GANIL NFS, d(40)+Be, 50 µA (Geant4 reference) | 3.5e+08 | 6.9e+03 | **0.016** | 0.018 | 0.011 | 1 | 0.0018 |
| SARAF-II, d(40) 5 mA CW on Li/Be, NFS-like spectrum | 3.5e+10 | 6.9e+05 | **0.035** | 0.034 | 0.0022 | 0.056 | 0.002 |
| CERN n_TOF EAR2 (1e7 n/cm²/pulse, Ø5 cm) | 1.6e+07 | 4.8e+03 | **0.12** | 1.46 | 0.0046 | 0.0056 | 0.11 |
| CERN n_TOF EAR1 (8e5 n/cm²/pulse, Ø5 cm) | 1.3e+06 | 3.8e+02 | **0.068** | 0.49 | 0.017 | 0.18 | 0.061 |
| CSNS Back-n ES#1, 185 kW, Φ50 mm | 5.9e+08 | 2.3e+05 | **0.0036** | 0.076 | 0.00065 | 0.075 | 0.0034 |
| CSNS-II Back-n ES#1, 500 kW, Φ50 mm | 1.6e+09 | 6.3e+05 | **0.0036** | 0.076 | 0.00039 | 0.032 | 0.0034 |
| LANSCE WNR 30° (ICE), 5e6 n/cm²/s >1 MeV, 50 cm² | 2.9e+08 | 6.4e+04 | **0.0017** | 0.0085 | 0.0014 | 1 | 0.0013 |
| JRC GELINA, 2.5e13 n/s, 10 m (isotropic bound), 50 cm² | 3.7e+07 | 1.1e+04 | **0.0032** | 0.031 | 0.0031 | 1 | 0.0029 |
| HZDR nELBE, 2.5e4 n/cm²/s, 7 cm² | 1.8e+05 | 1e+02 | **0.26** | 0.26 | 0.26 | 1 | 0.21 |
| FRM II MEDAPP fission beam, 3.2e8 n/cm²/s, 50 cm² | 1.6e+10 | 9.4e+06 | **0.0002** | 0.0046 | 0.00015 | 1 | 0.00016 |
| Birmingham ⁷Li(p,n) 2.6 MeV, 30 mA, unmoderated, cell at 1 m | 2.4e+10 | 1.1e+07 | **0.00014** | 0.0037 | 0.00011 | 1 | 0.00014 |
| Birmingham ⁷Li(p,n), shielded, cell at 2 m | 6e+09 | 2.8e+06 | **0.00025** | 0.0037 | 0.00023 | 1 | 0.00025 |
| D-D generator 3e11 n/s (Phoenix-class), cell at 1 m | 1.2e+08 | 1.3e+05 | **0.0018** | 0.0022 | 0.0018 | 1 | 0.0018 |
| D-D generator 3e11 n/s, shielded, cell at 2.5 m | 1.9e+07 | 2.1e+04 | **0.009** | 0.0091 | 0.009 | 1 | 0.009 |
| D-T generator 4.6e13 n/s (SHINE record), cell at 1 m | 1.8e+10 | 0 | **—** | — | — | 1e-06 | 0.00087 |
| Cyclotron ⁹Be(p,n), 30 MeV 1 mA, unmoderated, cell at 1 m (est.) | 5e+10 | 1.8e+07 | **0.0013** | 0.0045 | 0.00012 | 0.075 | 0.00086 |
| SARAF-I LiLiT, 1.9 MeV p, ~1.5 mA, keV n, cell at 0.5 m | 2e+08 | 3.3e+04 | **0.0067** | 0.013 | 0.0067 | 1 | 0.0067 |
| FRANZ Frankfurt, 2.0 MeV p, 10 mA (design), keV n, 0.5 m | 1.4e+09 | 2.3e+05 | **0.0012** | 0.011 | 0.0012 | 1 | 0.0012 |

What the table says:

1. **Pulsed white sources lose to their duty factor.**
   - n_TOF (0.2 Hz) and Back-n (25 Hz) deliver their neutrons in µs bursts. A full Ø5 cm EAR2 pulse
     puts ~12 singles per arm inside one 1 µs Micromegas memory (occupancy 12.5), so the model throttles
     EAR2 ×180 and Back-n ×13.
   - Back-n has the best window flux of any white source (×34 NFS) and still stops at 3.6×10⁻³. The
     CSNS-II power upgrade gains nothing: the throttle just tightens.
   - LANSCE WNR (14 000 micropulses/s) and GELINA (800 Hz) spread the load. WNR comes out the best
     white source, 1.7×10⁻³ (Geant4 singles), but its spectrum split and beam size are estimates (§6.2).
2. **NFS's spectrum, not its flux, is its problem.** SARAF-II would put ×100 NFS's current on the same
   d(40) spectrum, CW. It ends at the same walls: 0.035 in the window (no TOF), 2.0×10⁻³ all-E\*.
3. **Continuous sources with a soft spectrum top the table:**
   - **MEDAPP** (fission spectrum, 3.2×10⁸ n/cm²/s): 2×10⁻⁴ (Geant4 singles) to 4.6×10⁻³ (flat).
   - **Birmingham HF-ADNeF** (⁷Li(p,n), >30 mA): 2.5×10⁻⁴ to 3.7×10⁻³, with the cell 2 m from a
     shielded target.

   In the flat case both are wall-limited: the beam is throttled ×7–40 and stops at ~3×10⁴ singles/s.
   There the figure of merit is pairs per single, ∝ window fraction × P(E) / singles per neutron. A soft
   spectrum wins it by ×30 over NFS.
4. **Compact generators are clean but weak.**
   - D-D at 2.45 MeV has no hard tail. D(d,γ)⁴He makes only ~3×10⁴ γ/s at 3×10¹¹ n/s.
   - It is statistics-limited: 1.8×10⁻³ with an unshielded source 1 m away, 9×10⁻³ shielded at 2.5 m.
     It needs ~×10 today's best generator.
   - D-T (14 MeV) has no ATOMKI-window signal at all.
5. **Near-threshold ⁷Li(p,n) (LiLiT, FRANZ) works despite keV neutrons.** P(30 keV) is still ×40 thermal,
   and there is no hard tail. LiLiT at 1.5 mA: 6.7×10⁻³. FRANZ at 10 mA, if built: 1.2×10⁻³ to 1.1×10⁻².

### 4.3 γ from the compact sources (not in the model)

- **Birmingham.** Thick Li at 2.6 MeV gives ~1×10⁻⁷ γ per proton at 14.6–18.2 MeV (⁷Li(p,γ)⁸Be through
  both 1⁺ resonances; demokritos/neutron/NEUTRON_BEAM.md §5), so 1.9×10¹⁰ γ/s at 30 mA.
  - Unshielded at ~1 m: ~10⁸ γ/s through each arm, which is fatal.
  - With 20 cm of Pb around the target (µ = 0.57 cm⁻¹ at 17 MeV): < 10³ γ/s per arm at 2 m.
  - Through the Ø8 cm collimator, ~2×10⁶ γ/s cross the cell. Their external conversions point forward,
    into the dump. A Pb filter in the beam (10 cm: γ ×3×10⁻³, neutrons ×~0.2–0.5) is the usual remedy.
  - The ⁸Be IPC pairs made in the target stay 2 m upstream, outside the arms.
- **D-D generator.** The γ yield is negligible. The 4π neutron leakage (3×10¹¹ n/s) is the issue: the
  source needs ~1 m of shielding around it, hence 2.5 m.
- **MEDAPP.** γ ≈ n in flux (the NECTAR estimate), modelled as k_γ = 1. The converter's thermal leakage
  needs the Cd/B filter NECTAR already uses.

## 5. The catalogue

`catalogue.py` → `facilities.csv` (59 rows; a few rows group like facilities), `out/triage.csv` (with the model numbers).

| verdict | facility | class | status (2026) | why |
|---|---|---|---|---|
| **STUDIED** | ILL PF1B | cold/thermal | operating; ILL extended to 2033 | world reference cold beam; Geant4 reach 5.3e-3 per 50-d cycle (×3.2 short of ⁸Be level) |
| **STUDIED** | CERN n_TOF EAR2 | fast pulsed | operating; 2026 MX17 campaign site | measured 2026; per-pulse MM occupancy forces a ×200 throttle in the model: 0.12 |
| **STUDIED** | GANIL / SPIRAL2 NFS | fast pulsed | operating | Geant4 reach 3.3e-3 (all E*) / 0.031 (E* ≤ 22 MeV) in 14 d |
| **STUDIED** | NCSR Demokritos 5.5 MV tandem | fast mono low-current | operating | neutron route closed (34 yr); production-target pairs ×360-4400 — the proton route is the option |
| **POTENTIAL** | FRM II MEDAPP / NECTAR fission-converter beam | fast CW | reactor off since 2020; restart open | continuous, 71 % of the flux in 0.2-2.75 MeV, ×1400 NFS in the window: 2e-4 (Geant4 singles) to 4.6e-3 (flat singles, beam throttled ×40) in 50 d. The only beamline fission converter in the world |
| **POTENTIAL** | Birmingham High Flux Accelerator-Driven Neutron Facility | fast CW | operating since Dec 2023 (BNCT, fusion materials) | DC, 81 % of the neutrons in the window; with the target shielded and the cell 2 m away, ×400 NFS in the window: 2.5e-4 (Geant4 singles) to 3.7e-3 (flat) in 50 d. The target’s 1.9e10 γ/s at 15-18 MeV need ~20 cm Pb around it and an in-beam filter |
| **MARGINAL** | Reactor BNCT epithermal beams (THOR, RA-6, LVR-15, MITR FCB) | epithermal | operating (KUR stopped May 2026) | k = 3.6 pairs per neutron over thermal, ILL walls: 2.5e-3 (×1.6 ATOMKI) as is, 1.7e-3 with a faster DAQ; assumes ILL-like background per neutron and ignores the beam’s fast-n and γ contamination |
| **MARGINAL** | Accelerator BNCT (NeuCure/Sumitomo, Neutron Therapeutics, CICS, TAE, Tsukuba, Dawonsys, BINP) | epithermal | > 25 facilities operating or in development | as reactor BNCT in moderated mode; the unmoderated source is the real prize: see birmingham |
| **MARGINAL** | LANSCE WNR (Target 4, 30° ICE House) | fast pulsed | operating | best existing white beam on the model: 1.7e-3 (Geant4 singles) to 8.5e-3 (flat), floor 1.4e-3; rests on an estimated spectrum split and beam size, frame overlap at 1.8 µs (ask LANSCE) |
| **MARGINAL** | Cyclotron ⁹Be(p,n) sources (BNCT 30 MeV/1 mA; isotope cyclotrons) | fast CW | many operating; unmoderated ports (ask) | 1.3e-3 to 4.5e-3 on the model, but the yield (1e13 n/sr/s at 1 mA) and spectrum are guesses; needs a thick-target table and an unmoderated port |
| **MARGINAL** | High-yield D-D generators (Phoenix/SHINE class) | fast CW | commercial | clean (2.45 MeV, no hard tail, D(d,γ) γ negligible) but statistics-limited: 9e-3 with the source shielded at 2.5 m, 1.8e-3 at an unshielded 1 m; needs ~×10 the yield of today’s best generator |
| **WATCH** | ESS ANNI | cold/thermal | proposed (port E5 shared with HIBEAM); ESS beam on target Jan 2027, users 2028 | ≈ PF1B: would be DOMINATED (the walls, not the flux, set the reach) |
| **WATCH** | CNEA RA-10 | cold/thermal | under construction (lit.) | thermal: would be DOMINATED |
| **WATCH** | SARAF (Phase I LiLiT; Phase II linac) | fast CW | Phase-II first beam slipped past 2024 | LiLiT keV neutrons: 6.7e-3; Phase II d(40): NFS-like spectrum, CW (no TOF), wall-limited: ≈ NFS |
| **WATCH** | FRANZ | fast CW | RFQ commissioned at 10 mA (2025); 2 MeV stage not yet | keV neutrons: 1.2e-3 (Geant4 singles) to 1.1e-2 (flat) if it reaches 10 mA at 2 MeV; near-threshold Li(p,n) is forward-focused, so the target–cell distance can be short |
| **WATCH** | LNL LENOS | fast CW | status unknown after 2017 (ask) | Birmingham class if built |
| **WATCH** | LNL NEPHIR / SPES cyclotron | future | partially financed (2017) | NFS-like hard spectrum: ≈ NFS |
| **WATCH** | ESS (fast?) | future | users 2028 | cold: ANNI row |
| **WATCH** | SCK CEN MINERVA (MYRRHA phase 1) | future | ~2027+ (lit.) | no neutron beam for physics announced (ask) |
| **DOMINATED** | ILL FIPPS | cold/thermal | operating | ×600 below PF1B in absorbed rate |
| **DOMINATED** | FRM II MEPHISTO | cold/thermal | reactor off since 16 Mar 2020; central channel delayed (Bavarian parliament, Mar 2026); restart open | at best equal to PF1B, and PF1B is already past the rate walls |
| **DOMINATED** | NIST NCNR NG-C | cold/thermal | restarted 2026 after 5.5 yr; users from late Nov 2026 | below PF1B; reach 5.5e-3 at its maximum rate |
| **DOMINATED** | ORNL SNS FnPB (BL13) | cold/thermal | operating; Second Target Station 2030s | ×20 below PF1B |
| **DOMINATED** | J-PARC MLF BL05 NOP | cold/thermal | operating | below PF1B |
| **DOMINATED** | ORNL HFIR cold guide hall | cold/thermal | operating | no guide beats PF1B |
| **DOMINATED** | PSI SINQ | cold/thermal | operating | no guide beats PF1B |
| **DOMINATED** | CIAE CARR | cold/thermal | operating | below PF1B |
| **DOMINATED** | CAEP CMRR | cold/thermal | operating | no guide beats PF1B |
| **DOMINATED** | ANSTO OPAL | cold/thermal | operating | no guide beats PF1B |
| **DOMINATED** | KAERI HANARO | cold/thermal | operating (lit.) | no guide beats PF1B |
| **DOMINATED** | JAEA JRR-3 | cold/thermal | operating (restarted 2021, lit.) | no guide beats PF1B |
| **DOMINATED** | LANSCE Lujan Center | cold/thermal | operating | below PF1B |
| **DOMINATED** | ISIS | cold/thermal | operating; ISIS-II planned | below PF1B; ChipIR is an atmospheric (≫ 10 MeV) spectrum: WINDOW |
| **DOMINATED** | MIT Reactor | cold/thermal | operating | thermal ports below PF1B |
| **DOMINATED** | MURR | cold/thermal | operating | below PF1B |
| **DOMINATED** | Budapest BRR | cold/thermal | operating (lit.) | below PF1B |
| **DOMINATED** | CVR LVR-15 | cold/thermal | operating (lit.) | below PF1B |
| **DOMINATED** | TRIGA reactors (Mainz, Pavia, Ljubljana, …) | cold/thermal | operating | ×100 below PF1B |
| **DOMINATED** | JRC GELINA | fast pulsed | operating | even the isotropic bound at 10 m has a statistics floor of 3.1e-3 (×2 ATOMKI); below WNR |
| **DOMINATED** | HZDR nELBE | fast pulsed | operating | ×10⁴ below NFS |
| **DOMINATED** | RPI LINAC | fast pulsed | operating | source ≤ GELINA |
| **DOMINATED** | KURNS-LINAC | fast pulsed | operating (lit.) | source < GELINA |
| **DOMINATED** | IJCLab LICORNE (ALTO) | fast mono low-current | operating (lit.) | ≤ Demokritos-class flux, and p(⁷Li,γ)⁸Be in the gas cell |
| **DUTY** | CERN n_TOF EAR1 | fast pulsed | operating | 0.07 at best throttle |
| **DUTY** | CSNS Back-n ES#1 | fast pulsed | operating (185 kW Mar 2026); CSNS-II to 500 kW, no date | best fast white beam (×34 NFS in the window, measured spectrum) but 25 Hz: MM occupancy forces a ×13 throttle; 3.6e-3 (Geant4 singles) to 7.6e-2 (flat) at 50 d, either power |
| **DUTY** | J-PARC ANNRI (BL04) | fast pulsed | operating | moderated spectrum, 25 Hz: Back-n class at best |
| **DUTY** | CSNS-II | future | upgrade launched 2024, no date | the throttle, not the power, sets Back-n: no gain |
| **WINDOW** | D-T generators (SHINE record 4.6e13 n/s; FNG Frascati 1e11) | fast CW | operating | E* = 31 MeV: no ATOMKI-window signal at all; all-E* reach only if X17/IPC holds at 31 MeV |
| **WINDOW** | NCBJ MARIA 14 MeV converter | fast CW | operating | 14 MeV, and an irradiation position, not a beam |
| **WINDOW** | TSL Uppsala, iThemba LABS, RCNP Osaka | high-E | operating (lit.) | E_n ≫ 3 MeV |
| **WINDOW** | ISIS ChipIR / LANSCE ICE House 15° | high-E | operating | spectrum ≫ 10 MeV |
| **TARGET** | LNL CN / AN2000 | fast mono low-current | operating | Demokritos argument; LNL is the ⁸Be proton study (lnl/) |
| **TARGET** | PTB PIAF, NPL, JRC MONNET, TUNL, Ohio Edwards, CIAE, PKU, Tohoku FNL, Kyushu, AIST | fast mono low-current | operating | same as Demokritos: flux needs the cell at the target |
| **ACCESS** | Kyoto KUR | cold/thermal | shut down May 2026; 10 MW successor at Monju planned | shut down |
| **ACCESS** | PNPI PIK | cold/thermal | at power since 2021; stations commissioning | CERN–Russia cooperation ended 2024; and thermal is wall-limited anyway |
| **ACCESS** | BER II, Orphée, JEEP II, FiR-1, ORELA, LENS | cold/thermal | closed (2008-2019) | closed |
| **ACCESS** | CERN n_TOF NEAR | fast pulsed | operating (activation only) | irradiation position in the target shielding: no room for the arms; same 0.2 Hz pulse load as EAR2 |
| **ACCESS** | JINR IREN / IBR-2 | fast pulsed | operating | CERN–JINR cooperation ended 2024 |
| **ACCESS** | IFMIF-DONES | future | construction started 2023-25; first beam 2030s (lit.) | no extracted beam: irradiation test cell |

## 6. The potential list

### 6.1 POTENTIAL

**FRM II MEDAPP / NECTAR fission-converter beam (Garching).**
- **Beam:**
  - two ²³⁵U plates (540 g) at the moderator tank edge turn thermal neutrons into a fission spectrum;
  - mean energy ~1.9 MeV; 3.2×10⁸ n/cm²/s at the irradiation position; field up to 20 × 30 cm;
  - γ flux ≈ n flux;
  - the only beamline fission converter in the world (FRM II).
- **Model:** ×1400 NFS in the ATOMKI window. 2×10⁻⁴ to 4.6×10⁻³ in 50 d. Even the flat bound throttles the
  beam ×40.
- **Against:**
  - FRM II has not run since March 2020. The new central channel was still not delivered in March 2026,
    and no restart date is set.
  - MEDAPP is a medical/irradiation room, not a nuclear-physics hall: is there space for the arms?
  - The γ field.

**Birmingham HF-ADNeF (UK).**
- **Beam:**
  - an electrostatic accelerator, 2.6 MeV protons at > 30 mA on a rotating Li target: > 3×10¹³ n/s, all
    below 0.9 MeV;
  - first neutrons December 2023; a user facility listing nuclear physics among its uses;
  - a planned deuteron beam (to ~18 MeV neutrons) would move it towards NFS's spectrum. Ask that it stay
    available with protons.
- **Model:** with the target shielded and the cell 2 m away, ×400 NFS in the window. 2.5×10⁻⁴ to
  3.7×10⁻³ in 50 d.
- **Against:**
  - the 15–18 MeV γ from the target (§4.3);
  - room return from a 3×10¹³ n/s source;
  - whether an unmoderated, collimated port exists or can be built (ask).

**Operating today, it is the strongest candidate on the list.**

### 6.2 MARGINAL (one assumption from potential)

| facility | model | the assumption to check |
|---|---|---|
| LANSCE WNR (30° / ICE House) | 1.7×10⁻³ to 8.5×10⁻³ | flux below 1 MeV and the beam size are estimates (5×10⁶ n/cm²/s > 1 MeV is the only number found); frame overlap at 1.8 µs |
| Cyclotron ⁹Be(p,n), 30 MeV / 1 mA | 1.3×10⁻³ to 4.5×10⁻³ | the thick-target yield and spectrum are guesses; is there an unmoderated port at a BNCT cyclotron? |
| D-D generator (Phoenix/SHINE class) | 9×10⁻³ at 2.5 m | needs ~3×10¹² n/s, ×10 today's best |
| BNCT epithermal beams | 2.5×10⁻³ (as-is walls), 1.2–1.7×10⁻³ (faster DAQ) | ILL-like background per neutron; fast-n and γ contamination |

### 6.3 What a dedicated study needs, in order

1. **One Geant4 run that collapses the bracket for every CW soft source.**
   - **Setup:** a fission-spectrum and a ⁷Li(p,n) beam on the NFS geometry, with `--force-beam` and
     roulette as N4; ~2×10⁸ forced events (~20 CPU-h, MX17_Full_Geant branch `nfs`).
   - **Output:** singles per neutron below 3 MeV, the correlated background, and the MM occupancy.
   - **Then:** rerun `survey_fast.py` with that table in place of N4's.
2. **Add the room.**
   - A concrete hall and a beam dump 2–3 m downstream; for Birmingham, the target shield and a
     collimator; for MEDAPP, the γ beam.
3. **Ask the facilities** (§8).
4. **The physics question under every number:** X17/IPC for E1 capture at E\* = 20.6–22 MeV, compared
   with ATOMKI's ⁴He (which is p + t at E\* ≈ 20.5 MeV). Already open for NFS; ask Viviani et al.

## 7. For the paper

A world survey can make three general statements, each backed by a Geant4 anchor:

1. **Thermal capture is the worst energy per neutron.** P = 4.8×10⁻¹¹ against 1×10⁻⁸ at 1 MeV (§2).
   And the best cold beam (PF1B) already exceeds what a tracking pair spectrometer can take, so no
   reactor in the world helps (§3).
2. **Pulsed white sources are throttled by their duty factor**, not their average flux (§4.2).
3. **The right source is continuous, soft (0.1–3 MeV, no > 10 MeV tail), and ≳ 10⁹–10¹⁰ n/s through a
   ~50 cm² cell.** Two such facilities exist (a fission converter and a 30 mA ⁷Li(p,n) source). The
   requirement can be written as pairs per single, a figure of merit any facility can be scored on.

The survey also says where the ³He route stands against the proton routes the repo already has (LNL
⁷Li(p,e⁺e⁻), Demokritos ³H(p,e⁺e⁻)). There the target makes the pairs directly, with no neutron
background at all. A neutron facility has to beat that, and only the two on the potential list might.

## 8. Open questions (ask)

- FRM II: restart date; MEDAPP beam time for a 4π detector; space around the beam; the γ spectrum.
- Birmingham: an unmoderated collimated port; beam time; whether protons stay available after the
  deuteron upgrade; the neutron spectrum at 0°.
- LANSCE: WNR 30° flux below 1 MeV and beam size at ICE; micropulse spacing options (3.6 µs?).
- BNCT cyclotron vendors (Sumitomo): the ⁹Be(p,n) thick-target yield at 30 MeV, and any unmoderated port.
- Phoenix/SHINE: D-D at > 10¹² n/s.
- FRANZ, SARAF-II, LENOS: when, and at what current.

## 9. Sources

The full ledger (values, quotes, confidence, open items, local copies) is **`SOURCES.md`**. The main links:

Reactors and cold beams:
- PF1B capture flux: [PMC13060404](https://pmc.ncbi.nlm.nih.gov/articles/PMC13060404/); `ill/FACILITY.md`
- ANNI and MEPHISTO: [arXiv:1811.11692](https://arxiv.org/abs/1811.11692); [arXiv:2211.10396](https://arxiv.org/pdf/2211.10396)
- ESS schedule: [STAP Apr 2026](https://indico.ess.eu/event/4007/contributions/24588/attachments/17817/35512/intro-STAPs-apr-2026.pdf)
- NG-C: [aCORN, arXiv:2012.14379](https://arxiv.org/pdf/2012.14379); NCNR restart: [Physics Today](https://physicstoday.aip.org/news/nist-neutron-source-restarts-after-prolonged-closure)
- FRM II status: [Bavarian parliament, Mar 2026](https://www.bayern.landtag.de/www/ElanTextAblage_WP19/Drucksachen/Basisdrucksachen/0000009000/0000009042_029.pdf); [IGORR 2025](https://igorr.com/_media/proceedings:2025_igorr22:s06-01-pichlmaier-status_and_outlook.pdf); [MLZ central channel](https://mlz-garching.de/englisch/news-und-press/news-articles/first-phase-of-central-channel-completed-project-still-delayed.html)
- MEDAPP/NECTAR: [FRM II fast irradiation](https://www.frm2.tum.de/en/frm2/the-neutron-source/irradiation-facilities/irradiation-with-fast-neutrons/); [converter facility](https://www.frm2.tum.de/en/frm2/the-neutron-source/neutrons/secondary-sources/converter-facility/); [JLSRF](https://jlsrf.org/index.php/lsf/article/view/43); [Wagner 2007](https://jnpae.kinr.kyiv.ua/21(3)/Articles_PDF/jnpae-2007-3(21)-0030-Wagner.pdf); [GIANT/NECTAR](https://www.nature.com/articles/s41598-023-47237-y)
- FnPB: [ORNL BL13 flyer](https://neutrons.ornl.gov/sites/default/files/24-G00726-Physics%20Division%20BL13%20Flyer-8.5x11-pcg-02-21-24.pdf); NOP: [arXiv:1712.06351](https://arxiv.org/pdf/1712.06351)
- CARR: [IGORR 2025](https://igorr.com/_media/proceedings:2025_igorr22:s01-03-zhou-overview_of_carr_operation_and_applications.pdf); PIK: [WNN](https://world-nuclear-news.org/articles/russian-pik-research-reactor-upgraded)
- KUR shutdown: [KURNS](https://www.rri.kyoto-u.ac.jp/en/outline/preface)
- BNCT: [reactor review](https://tro.amegroups.org/article/view/4646/html); [Kyoto 2024](https://repository.kulib.kyoto-u.ac.jp/dspace/bitstream/2433/291657/1/j.nima.2024.170126.pdf); [DawonMedax](https://doaj.org/article/7c9fee6dd61b495f8d05f0e01390ec52)

White sources:
- Back-n: [arXiv:2101.06567](https://arxiv.org/abs/2101.06567) (`refs/arxiv_2101.06567_backn.pdf`); [ND2019](https://www.epj-conferences.org/10.1051/epjconf/202023917018); [IHEP 2024 slides](https://indico.ihep.ac.cn/event/23550/contributions/188440/attachments/91247/118967/Current%20Status%20and%20Experiments%20of%20the%20Back-n%20White%20Neutron%20Facility.pdf); [CSNS 185 kW](https://english.ihep.ac.cn/nw/han/y26/202603/t20260317_1152755.html)
- n_TOF: [arXiv:2403.09759](https://arxiv.org/pdf/2403.09759); [arXiv:1905.00491](https://arxiv.org/pdf/1905.00491); NEAR: [Frantzis, HNPS 2022](https://hnps2022.physics.uoi.gr/wp-content/uploads/2022/09/HNPS2022_FRANTZISNeutron-Flux-Determination-for-NEAR-Station-at-the-CERN-n_TOF-Facility-Using-the-SAND-II-Unfolding-Code.pdf)
- LANSCE WNR: [flight paths](https://lansce.lanl.gov/facilities/wnr/flight-paths/index.php); [ICE House](https://lansce.lanl.gov/facilities/Radiation%20Effects/index.php)
- GELINA: [JRC](https://publications.jrc.ec.europa.eu/repository/handle/JRC36942); nELBE: [HZDR](https://www.hzdr.de/db/Cms?pNid=2802); RPI: [arXiv:1801.03424](https://arxiv.org/pdf/1801.03424)

Accelerator and compact sources:
- Birmingham HF-ADNeF: [UCANS11 2025](https://indico.triumf.ca/event/575/contributions/6394/); [STFC Sep 2026](https://indico.stfc.ac.uk/event/1939/contributions/11131/)
- SARAF: [arXiv:1801.06493](https://arxiv.org/pdf/1801.06493); [2024 status](https://inspirehep.net/files/a4ad488a9e20fee312e86513d3771f9b); LiLiT: [arXiv:1311.3325](https://arxiv.org/pdf/1311.3325)
- FRANZ: [IPAC 2025](https://indico.jacow.org/event/81/contributions/7842/); [arXiv:1403.5670](https://arxiv.org/pdf/1403.5670); LENOS: [status](https://produccioncientifica.ugr.es/documentos/63b9970a4386723d2da37e3d)
- Thick ⁷Li(p,n): [Lee & Zhou 1999](https://bnct.inp.nsk.su/publics/other/Lee_Neutron_yeilds_near_threshold_NIM_B_1999_1_11.pdf)
- D-D: [Phoenix](https://trinity.ans.org/file/1445/radel-150616.pdf); D-T record: [Physics World](https://physicsworld.com/a/record-breaking-fusion-reaction-could-transform-medical-isotope-production/); D(d,γ): [PRC 47, 29](https://link.aps.org/doi/10.1103/PhysRevC.47.29), [AEST 2016](https://yznkxjs.xml-journal.net/article/doi/10.7538/yzk.2016.50.03.0395)
- IFMIF-DONES: [ifmif-dones.es](https://ifmif-dones.es/); MARIA converter: [NCBJ](https://www.ncbj.gov.pl/en/aktualnosci/ncbj-thermal-14-mev-neutron-converter-sole-device-its-kind-operated-world); ⁹Be(p,n): [METU thesis](https://open.metu.edu.tr/handle/11511/115507)

