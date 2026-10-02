# Can we measure X17 at the ILL? — what the Geant4 campaign says

2026-10-02, from the lxplus campaign in `SIM_STATUS.md` (S1, C1, C1w, C1g, K1,
S1p, S1s; all six cell configurations G1–G6). Model: `sim_feasibility.py`;
figures: `sim_report.py`; robustness: `sim_variants.py`; table:
`results/scan_v1.csv`. Outputs: `/eos/experiment/ntof/data/x17/ill/analysis/`
(local copies of the small files: `ill/sim/analysis_v3/`).

## Bottom line

**Yes, with two detector requirements that the current design does not yet
meet: ~200 ps per-arm timing and a cosmic-muon veto.** With both, one 50-day
cycle at ~10¹⁰ absorbed n/s reaches **X17/IPC(M1) ≈ 0.8–1.2 × 10⁻² at 3σ**.
That puts the rate table's reference value, 2.5 × 10⁻², at **~6–9σ** in a
single cycle. The R = 40 mm cells (G1, G3, G5) are equally good. The
R = 100 mm cells are 30–50 % worse.

With the timing assumed so far (σt = 0.5 ns, |Δt| < 1.5 ns, 2τ = 5 ns) and no
veto, the reach is only ~5 × 10⁻² at 3σ. That is **not enough**: the reference
value would be a ~1.5σ effect. The limit there is **cosmic rays**, not neutron
backgrounds, scattering or statistics.

Scattering of the leptons is **not** the limiting factor. The X17 leptons are
not 1–3 MeV: the X17 is boosted (p ≈ 11.7 MeV), so the softer lepton always
carries ≳ 3.5 MeV (median 6.3 MeV). The opening-angle resolution (σ68 ≈ 5–8°)
is small next to the X17's own angular spread, which runs from a sharp edge at
110° up to ~150°. Even perfect vertex knowledge improves the reach by only
~13 %.

## 1. Scattering (the 1–10 MeV leptons)

Median angle between a lepton's initial direction and its direction at the
first drift-gap hit (`scatter_vs_ke`):

| lepton KE [MeV] | 1–2 | 2–3 | 3–4 | 4–5 | 5–6 | 6–8 | 8–10 | 10–12 | 15–19.6 |
|---|---|---|---|---|---|---|---|---|---|
| G1 (1 bar, 12 µm mylar) | 18.7° | 12.1° | 8.5° | 6.9° | 5.8° | 4.7° | 3.8° | 3.2° | 2.2° |
| G5 (3 bar, 0.23 mm Kapton) | 22.9° | 14.7° | 10.4° | 8.4° | 7.1° | 5.8° | 4.7° | 3.9° | 2.8° |

- About 70–75 % of this comes from the Micromegas entrance (40 µm mylar, 50 µm
  Kapton, 9 µm Cu) and ~16 cm of air. The Highland estimate for those two
  alone sits just below the G1 curve. The cell wall adds the rest; it is
  noticeable only for the thick Kapton skins (G4, G6).
- The chord estimator takes the vertex-to-gap-hit line. It is barely hurt
  because the scattering happens just before the measured point.
- **Which leptons matter.** Accepted X17 pairs (sipm2, Esum > 12 MeV) have a
  softer lepton of 4.1 / 6.3 / 9.1 MeV (p10/50/90) and a harder one of
  10.4 / 13.3 / 15.5 MeV. No accepted X17 lepton is below ~3.5 MeV. The
  1–3 MeV leptons that scatter by 12–20° belong to the backgrounds (Compton
  electrons, wall pairs), not to the signal.

Opening-angle resolution, X17, sipm2 menu, σ68 of θ_reco − θ_true:

| | G1 | G2 | G3 | G4 | G5 | G6 |
|---|---|---|---|---|---|---|
| true vertex (scattering + 0.5 mm hits) | 2.2° | 1.5° | 3.0° | 3.7° | 4.4° | — |
| vertex assumed at the cell centre (the default) | 7.8° | 8.7° | 6.8° | 7.6° | 6.9° | 7.8° |

- With the vertex assumed at the centre, the source length dominates: 43 mm
  (σ, along the beam) at 1 bar, 14 mm at 3 bar.
- The X17 true opening angle is 110 / 121 / 151° (p16/50/84) with a hard edge
  at 110°. IPC M1 is 52 / 77 / 111°. So the signal sits on the falling IPC
  tail, and the ~7° resolution only rounds the 110° edge.
- `sim_variants`: using the true vertex instead of the assumed centre improves
  the 3σ reach by ~13 %. The per-event vertex from the axis crossing changes
  it by < 2 %.

## 2. Rates and statistics (per 50-day cycle)

Signal and IPC per absorbed neutron:

| quantity | per absorbed n |
|---|---|
| M1 pairs | 3.78 × 10⁻¹¹ |
| E0 pairs | 1.03 × 10⁻¹¹ |
| ³He(n,γ) | 1.03 × 10⁻⁸ |

Acceptance × efficiency for X17 (G1 / G5):

| stage | G1 | G5 |
|---|---|---|
| both leptons in a gap, different arms | 32 % | 27 % |
| SiPM ≥ 0.5 MIP in both lepton arms (sipm2) | 12 % | 10 % |
| sipm2 and Esum > 12 MeV | 3.1 % | 2.4 % |

The Esum cut keeps only ~25 % of the X17 pairs because the stack is not a
calorimeter: it contains a median of 40 % of the lepton kinetic energy, and
leptons punch through to the LS.

**Expected counts at the optimum rate, G1, sipm2, Esum > 13 MeV, 1 cycle:**

| | baseline timing, no veto | σt 0.2 ns, μ veto 10⁻² |
|---|---|---|
| absorbed rate (optimum) | 1.9 × 10¹⁰ n/s (beam max) | 0.9 × 10¹⁰ n/s |
| Micromegas occupancy per arm (1 µs) | 0.29 | 0.15 |
| IPC (M1 + E0) | 14 600 | 9 700 |
| X17 at the reference ratio | 1 050 | 700 |
| ³He(n,γ) photon fakes | 1 070 | 710 |
| accidentals | 87 000 | 5 100 |
| **cosmics** | **1 150 000** | 360 |
| other single-neutron fakes | 0 (see §4) | 0 |
| **3σ reach, X17/IPC(M1)** | **5.2 × 10⁻²** | **8.4 × 10⁻³** |

Rate limits we checked:

- **Micromegas pile-up.** The simulated gap rate is 2.8–3.0 × 10⁻⁵ prompt
  charged hits per absorbed n (5.4 × 10⁻⁵ including activation). So occupancy
  stays ≤ 0.3 per arm up to the beam's 1.9 × 10¹⁰ n/s; the model charges it as
  a signal loss, exp(−2·occ).
  - That gap rate is ~7× the analytic be05 scaling in `ill_rates.py`. Captures
    in air (2.7 × 10⁻⁴/n) and in the detector itself (LS, plastics, Al frames:
    ~1 × 10⁻³/n), from scattered beam neutrons, dominate over the window.
  - `ill_rates.py --contract` now prints both: the 10 %-occupancy limit is
    1.3–1.45 × 10¹⁰ n/s (Geant4) against 9.8 × 10¹⁰ (analytic).
- **Trigger.** At 10¹⁰ n/s, a bare SiPM two-arm trigger fires at ~5.5 kHz:
  ~5 kHz correlated Compton hits, ~0.4 kHz accidentals, 16 Hz cosmics. A 2 MeV
  per-arm hardware threshold brings it to ~130 Hz.
- **Accidentals** scale as R² · 2τ. They set an optimum rate below the beam
  maximum once cosmics are suppressed.

## 3. What drives the reach (`variants_v3.csv`, G1, sipm2, Esum > 12 MeV)

| assumption changed | 3σ reach |
|---|---|
| baseline (σt 0.5 ns, \|Δt\| < 1.5 ns, 2τ 5 ns, no veto) | 4.8 × 10⁻² |
| 2τ 3 ns | 4.6 × 10⁻² |
| σt 0.3 ns, \|Δt\| < 0.9 ns | 1.6 × 10⁻² |
| σt 0.2 ns, \|Δt\| < 0.6 ns | 1.3 × 10⁻² |
| baseline + μ veto 10⁻² | 1.7 × 10⁻² |
| **σt 0.2 ns + μ veto 10⁻²** | **9.2 × 10⁻³** |
| true vertex (ideal reconstruction) | 4.2 × 10⁻² |
| no cosmics | 1.5 × 10⁻² |
| no cosmics, no accidentals | 4.5 × 10⁻³ |
| IPC only (pure statistics) | 4.4 × 10⁻³ |

- **Cosmics.** They pass Esum > 12 MeV easily: through-going muons deposit
  ~8 MeV per arm. The rate is 7.2 Hz two-arm before timing.
  - The strongest handle is **time of flight**: a muon crosses between arms in
    2–3 ns (median 2.8 ns), while both pair leptons arrive within ~0.05 ns.
    Only 0.1 % of cosmics have true |Δt| < 0.5 ns.
  - An LS veto does not work, because X17 leptons reach the LS too (median
    5.8 MeV there). An upper Esum < 21 MeV cut removes only 27 %.
  - Cosmics are a fixed template, measurable with the reactor off. They still
    cost statistics.
- **Accidentals.** Two uncorrelated singles: ~2.4 × 10⁻⁶ per arm per absorbed
  n with a gap hit and SiPM. Better timing helps here too (2τ = 1.2 ns).
- **Pure statistics** set a floor of ~4.4 × 10⁻³ per cycle (∝ 1/√cycles).

## 4. Single-neutron fakes and the energy cut

- **The kinematic argument.** Every capture except ³He(n,γ) releases
  ≤ 10.83 MeV: ¹⁴N in air and Kapton is the hardest line among the materials
  present. So a two-arm Esum above ~12–13 MeV cannot come from one neutron
  (`esum` figure).
- **The Monte Carlo agrees.** C1w biases the cell walls ×300 and the air
  ×100, and has no correlated wall/air/detector event above 12 MeV in any
  configuration.
- **What the MC cannot do** is constrain these below ~10⁻⁹ per absorbed n,
  i.e. 0 raw events is not a useful upper limit at 10¹⁷ absorbed neutrons. The
  physics argument carries them.
  - With σ/E ≈ 6 % at 11 MeV, Esum > 12 MeV is only ~2σ above the ¹⁴N
    endpoint for a fully contained capture.
  - **Esum > 13 MeV (3.5σ) is the safer choice.** It costs at most ~7 % in
    reach, and with good timing it is slightly better than 12 MeV.
    A He bag or vacuum flight tube (removing air ¹⁴N) helps further.
- **³He(n,γ)** (20.58 MeV γ, 1.03 × 10⁻⁸/n) is the irreducible correlated
  fake: a γ converting or Compton-scattering into two arms. It is ~7 % of IPC
  after the cut and is floated in the fit. Its template rests on few raw
  events (C1g, ×10⁷ bias: 1–10 events after cuts). It does not drive the
  reach: removing it changes the reach by 0–12 % (G1–G3).

## 5. Configuration choice

Best-rate 3σ reach per 50-day cycle, Esum > 13 MeV (`v3_base`, `v3_timing`):

| | G1 | G2 | G3 | G4 | G5 | G6 |
|---|---|---|---|---|---|---|
| cell | 1 bar R40 mylar | 1 bar R100 mylar | 2 bar R40 Kapton | 2 bar R100 Kapton | 3 bar R40 Kapton | 3 bar R100 Kapton |
| X17 acc × ε (sipm2, E > 12) | 3.1 % | 2.5 % | 2.8 % | 2.1 % | 2.4 % | 1.9 % |
| baseline timing, sipm2 | 5.2e-2 | 8.7e-2 | 6.5e-2 | 8.7e-2 | 6.2e-2 | 9.2e-2 |
| baseline timing, strict | 4.8e-2 | 5.3e-2 | 4.9e-2 | 6.9e-2 | 5.9e-2 | 7.8e-2 |
| **σt 0.2 ns + μ veto, sipm2** | **8.4e-3** | 1.1e-2 | 1.0e-2 | 1.3e-2 | **8.6e-3** | 1.3e-2 |
| **σt 0.2 ns + μ veto, strict** | 9.6e-3 | **8.8e-3** | **8.7e-3** | 1.4e-2 | 1.0e-2 | 1.3e-2 |
| optimum rate (timing+veto) | 0.9–1.3 × 10¹⁰ n/s | | | | | |

- **The pressure barely matters.** At 1 bar the 43 mm source length costs ~1°,
  but the thin mylar skin and the larger acceptance pay it back.
- **The radius matters:** R = 100 mm loses 20–25 % acceptance (the gaps
  subtend less) and gains nothing.
- **Recommendation: G1 if the ³He permeation through 12 µm mylar is
  manageable over a cycle, otherwise G5.** G3 is equivalent.
  - Follow-up (`../he4_bag/`): bare 12 µm mylar loses ~22 L of ³He per cycle
    (τ ≈ 3.4 d). Keep the 1 bar cell, but with a 12 µm PET + 6–7 µm Al
    converter-foil skin (no PE sealant layer). That cuts the loss >1000× for
    +3 % scattering.
  - The foil sits at R = 40 mm, outside the beam (r99 12.9 mm), and adds
    ~10⁻⁸ captures/n. Al is the right metal: only Be is better, and it can't
    be wrapped. Most of the lepton scattering is the Micromegas 9 µm Cu (39 %)
    and the 16 cm of air (33 %), not the skin (8 %). The cell can't be pumped
    out to fill it. See `../he4_bag/README.md` §6.
- Absorption is 94 % per primary everywhere. The ⁶LiF scraper takes 3 %, and
  2.5 % escapes.

## 6. What would make it robust

1. **Timing ≤ 200–300 ps per arm**, on the 2 cm plastics (SiPMs at both bar
   ends), and a coincidence window of ~1 ns. This is the single biggest lever:
   it cuts cosmics and accidentals together.
2. **A cosmic veto** (scintillator panels, inefficiency ≤ 10⁻²), and a
   reactor-off cosmic run to measure the template.
3. **Energy containment.** A real calorimeter behind the gaps would keep
   ~100 % of X17 pairs above the cut instead of 25 %: ×4 signal at fixed
   rate, and a sharper Esum edge against the 10.8 MeV endpoint. This needs a
   new geometry run before it can be quantified.
4. **Air out of the beam path** (He bag), removing the hardest single-neutron
   line (¹⁴N, 2.7 × 10⁻⁴/n).
   - `../he4_bag/` shows ~90 % of that comes from the 30 cm aperture →
     window path. So a He flight tube is enough, and a balloon around the
     target is not worth it.
5. Analysis cut at **Esum > 13 MeV**.

## 7. Caveats

- **Assumed parameters, not measured ones:**
  - per-arm energy resolution 10 %/√E ⊕ 5 %;
  - timing as stated;
  - Micromegas 1 µs window;
  - cosmic flux at sea level with no hall overburden.
- **Correlated fakes.** The ³He(n,γ) template and the "other single-n" class
  rest on few or zero raw MC events after cuts; see §4.
- **IPC normalisation.** E0 is an order-of-magnitude estimate. It floats in
  the fit, so it affects the reach only through its shape.
- **The reference ratio** 2.5 × 10⁻² is a normalisation, not a prediction.
  The reach is quoted as a ratio so that the conclusion does not hang on it.
- **Statistics model.** The reach is σ(μ) from an Asimov Fisher matrix:
  M1, E0 and ³He(n,γ) float; accidentals, cosmics and wall are fixed. No
  systematics on the background shapes are included.
- **Not simulated:**
  - S2 (Be-window internal pairs): ≤ 6.8 MeV in total, so removed by the Esum
    cut by construction;
  - site γ/fast-neutron backgrounds in the casemate.

## 8. Follow-up (2026-10-02): cosmic vetoes, vertices, radius

Questions after the first read: why the timing matters, whether a cheap veto
exists, where the pairs are made and what the radius buys. Script:
`sim/lxplus/xtra_artifact.py` (run on lxplus next to EOS, like the other
diagnostics); output `sim/analysis_v3/xtra_artifact.json`. Slides:
`deck/build_deck.py` → `out/feasibility_deck.html`, published at
<https://dylan-neff.web.cern.ch/notes/ill-x17-feasibility.html> (the claude.ai
Slides version: <https://claude.ai/artifact/65SAfoogKQrtYHekYfScWF>).

**Why ~200 ps.** It is time of flight, not Micromegas pile-up.
- Pair leptons reach their arms within ~0.05 ns of each other. A muon crossing
  two arms takes a median of 2.8 ns.
- Faking muons (sipm2, Esum > 12 MeV, 7.2 Hz) hit top + bottom in 57 % of
  cases and top/bottom + side in 43 %; side + side is 0.1 %. The zenith is
  along sim z, and arms 2/3 sit at z = ±224 mm.
- 3.1 % of them have a true |Δt| < 1.5 ns, and 0.15 % have < 0.5 ns.
- The other gain from timing is accidentals, which go as R²·2τ. Micromegas
  occupancy (≤ 0.3 per µs) is charged only as a signal loss.

**Opening angle does not reject cosmics.** The chord estimator turns any
straight line through two arms into a "pair".
- The cosmic chord-angle distribution peaks at 110–130°, right on the X17
  edge. A vertical muon 6–15 cm off-axis gives 2·atan(22/offset) = 110–150°.
- The muon line misses the cell centre by 65 / 168 / 287 mm (p10/50/90).
  Only 1.1 % pass within 2 cm, so cosmics do not pile up at 180°.

**Segment collinearity is a candidate data veto.** It needs no hardware.
- A muon's two Micromegas segments lie on one line. X17 legs leave radially,
  so their segments meet at 180° − θ.
- Signal efficiency of a cut on that angle, from S1 G1 with ideal PCA
  directions including scattering: > 10° keeps 98 %, > 15° keeps 95 %,
  > 20° keeps 91 %, > 25° keeps 87 %.
- Muon leak from a toy model, Rayleigh with scale √2·σ, where σ is the
  per-segment direction resolution:
  - σ = 2°: < 0.1 % above 15°;
  - σ = 5°: 1.8 % above 20°;
  - σ = 10°: 37 % above 20°.
- The decisive unknown is the Micromegas direction resolution on a MIP. The
  n_TOF electron numbers (11–26°) are dominated by scattering. **Measure it on
  the cosmic bench.**
- Related handle: each segment's angle to the radial chord from the cell
  centre is a median of 35° for muons (10 % below 14°).

**Panel veto: put it on the ceiling.** These are coverage fractions: the K1
muon line (through the two Micromegas hits) extended to a horizontal plane.
Faking muons are steep, with zenith 8 / 22 / 44° (p10/50/90).

| panel, height | 1 × 1 m | 2 × 2 m | 3 × 3 m |
|---|---|---|---|
| ceiling, +0.6 m | 85.4 % | 99.3 % | 99.6 % |
| ceiling, +1.0 m | 69.8 % | 95.1 % | 99.2 % |
| floor, −0.6 m | 72.2 % | 95.6 % | 99.5 % |
| floor, −1.0 m | 67.5 % | 82.7 % | 96.8 % |

A ceiling panel is hit *before* the arms, and an escaping pair lepton could
only hit it after. So a time-ordered ceiling veto needs no electron stopper.
A floor panel needs an absorber, and bremsstrahlung γ still leak through it.

**Statistics per cycle at 0.9 × 10¹⁰ n/s** (3.9 × 10¹⁶ absorbed):

| stage | count |
|---|---|
| ³He(n,p) | 3.9 × 10¹⁶ |
| captures elsewhere (1.8 × 10⁻³/n) | 7 × 10¹³ |
| ³He(n,γ) | 4.0 × 10⁸ |
| IPC pairs | 1.9 × 10⁶ |
| X17 at the reference ratio | 3.7 × 10⁴ |
| X17 detected | ~700 |

The (n,p) products stop inside the cell: a few cm at 1 bar, from an estimate
of the stopping power, not from the MC.

**Vertices and radius.**
- Every vertex sits in the beam spot: r50/90/99 = 7 / 10 / 12 mm in all six
  cells, whatever the radius. Pressure sets only the depth along the beam.
- X17 acc × ε as a function of vertex y is ~3.8 % on the plateau. It drops to
  ~1.6–2.5 % in the first ~15 mm behind the window (G1 and G5 alike).
- R = 100 mm loses 20–25 %. The ratio of accepted-lepton cos θ (G2/G1) shows
  the loss sits almost entirely in backward leptons, at cos θ between −0.8
  and −0.2, where the ratio is 0.55–0.7.
- Both effects point to the 8 mm Al upstream end cap and ring, which is
  larger for the larger cell, shadowing backward leptons. **This is inferred,
  not traced in the MC.** If it holds, trimming that cap could recover up to
  ~20 % of the G1 acceptance. That is worth a geometry run.
- A small radius is not needed to fix the vertex. It matters for acceptance,
  for the ³He inventory (1.5 vs 9.4 bar·L) and for the Kapton wall thickness.

## 9. Where the accidentals come from (2026-10-02)

Once timing and the veto have suppressed the cosmics, accidentals are the
largest fixed background: 5 100 per cycle against 9 700 IPC (G1, 200 ps +
μ veto). The question was whether they come from one neutron making two
particles, as the Al e⁺e⁻ background does at n_TOF, or from pile-up.

**They are pile-up.** The model's ACC term is two singles from two different
neutrons inside 2τ (∝ R²·2τ). One-neutron fakes are the separate WALL term,
and that term is zero above 12–13 MeV (§4):
- A thermal capture releases at most its Q-value: Be 6.81, Al 7.72, Cu 7.92
  and ¹⁴N 10.83 MeV.
- Two singles can sum above 13 MeV: Al + Al reaches 15.4 MeV and
  Al + ¹⁴N 18.6 MeV.
- So Al comes back through pile-up, not as a correlated pair. A passing pair
  needs two nearly fully contained capture γ, so the hard tail of the per-arm
  spectrum (above ~6 MeV) matters, not the total singles rate.

**Attribution.** `sim/lxplus/acc_sources.py` labels each single by its
neutron's capture volume. It uses the C1 + C1w singles (+ C1g for ³He(n,γ)),
pairs them exactly as `sim_feasibility.accidental_hist` does, and splits the
sum (sipm2, Esum > 13 MeV, 60–180°). Outputs:
`sim/analysis_v3/acc_sources_G{1,5}.json`.

Share of the accidental background with at least one single from each
material (a pair counts for both of its singles):

| material | G1 | G5 |
|---|---|---|
| Al: cell end caps + ring, frames, flange, plates | **80 %** | 73 % |
| …of which the 8 mm upstream end cap and ring | 63 % | 48 % |
| air ¹⁴N | 41 % | **82 %** |
| Cu: PCB pads, cathode, mesh | 22 % | 1 % |
| Be entrance window | 19 % | 18 % |
| ³He(n,γ) γ, LS, plastics, PCB, gas | ~3 % | ~2 % |

Top pairs:
- G1: Al×Al 29 %, Al×air 26 %, Al×Cu 14 %, Al×Be 9 %.
- G5: Al×air 56 %, Be×air 13 %, Al×Al 12 %, air×air 11 %.

**Statistics.** The tail rests on few MC events with more than 6 MeV in one
arm. In G1:

| source | raw events | n_eff (Σw)²/Σw² |
|---|---|---|
| air | 354 | 14 |
| Al end cap + ring | 33 | 9 |
| Al frames, flange, plates | 3 | 3 |
| Cu | 1 | 1 |
| Be window | 58 | 58 |

The robust statement is "Al and air carry it". Which of them leads differs
between G1 and G5, and Cu's 22 % in G1 is a single event: in G5 it is 1 %.
Read every share as uncertain to ~×2.

**What removing a material would buy.** This is an oracle: drop every pair
involving that material, re-run the model and re-optimise the rate. The
reach is 3σ, 200 ps + μ veto, Esum > 13 MeV:

| removed | G1 | G5 |
|---|---|---|
| nothing | 8.3 × 10⁻³ | 8.7 × 10⁻³ |
| Al | 6.0 × 10⁻³ | 6.7 × 10⁻³ |
| air | 7.5 × 10⁻³ | 6.4 × 10⁻³ |
| Al + air | 5.2 × 10⁻³ | 5.5 × 10⁻³ |
| (IPC-only floor) | 4.4 × 10⁻³ | |

Without Al and air, the optimum rate moves back up to the beam maximum.
With today's timing and no veto, removing materials barely moves the reach,
because cosmics dominate (G1: 5.2 → 5.0 × 10⁻²).

**What to do:**
- Line or replace the Al that sees neutrons, the upstream end cap first:
  ⁶LiF (⁶Li(n,t) emits no γ) or B₄C (0.48 MeV γ). Trimming the cap also
  recovers the backward-lepton acceptance (§8). The Al-foil skin proposed in
  `../he4_bag/` is not part of this: it sits outside the beam (~10⁻⁸
  captures/n).
- Fit a He or vacuum flight tube on the 30 cm beam air path
  (`../he4_bag/README.md`).
- Timing still cuts the accidentals as 2τ, whatever their source.
- To pin the split down, run a targeted γ-source simulation: throw each
  material's capture cascade from its volumes, or move the C1w bias onto the
  frames, which were not biased.

Caveats:
- The attribution is by capture volume, not traced per particle.
- A few Al-labelled arms sit at 11–12 MeV, above the Al line. Something else
  in the event added to them; this was not traced.
- The reach model here gives 8.3 × 10⁻³ for G1, against 8.4 × 10⁻³ in §2.
  The difference is the rate grid.

Slides 10–14 of the note
(https://dylan-neff.web.cern.ch/notes/ill-x17-feasibility.html) show this.
