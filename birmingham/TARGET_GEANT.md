# Birmingham: which ³He target, and what the beam, the room and the wall do to MX17 (Geant4)

Started 2026-10-27 (dylan-Yoga + lxplus). Dylan asked: model the Birmingham feasibility with the rigour of the
LNL L10 study (`lnl/target/SHAPES_GEANT.md`). Do we need the 500 bar capsule there, or would a mylar balloon do and scatter
less? Run Geant4 once a design looks plausible and see the background. Can DREAM take the rate? Are the scintillators
flooded?

The facility record and the first study (soft-beam re-weighting, 3.3×10⁻⁴ in 50 d) are `FACILITY.md`, `FEASIBILITY.md`.
This study replaces its target, background and DAQ parts. Unknowns are **(ask)**, analytic stand-ins **ESTIMATE**.
Slides: <https://dylan-neff.web.cern.ch/notes/birmingham-target-geant.html>.

## 0. Bottom line (2026-10-27)

1. **No capsule, no balloon: build the densest thin-walled cell the ³He budget allows.** At a broad fast-neutron beam the
   ³He is a thin target, so the capture rate is the number of ³He atoms *inside the beam*, whatever the pressure (§1).
   Geant4, big plastics, 30 mA, days of beam to 3σ at the ATOMKI strength, with every background below and the shield
   wall of item 3:

   | target | ³He [L STP] | ³He cost | σ68 | days | X17/IPC at 3σ, 50 d | as built |
   |---|---|---|---|---|---|---|
   | **30 bar cell, R 5 × 40 cm, Be/CFRP** (NFS build C) | 87 | 217 k€ | 11.4° | **6.7** | 5.5×10⁻⁴ | 30 d |
   | 10 bar cell, R 5 × 40 cm | 29 | 72 k€ | 11.3° | 23 | 1.0×10⁻³ | 90 d |
   | n_TOF capsule, 500 bar (Ø2 cm beam) | 7.8 | 20 k€ | 14.4° | 58 | 1.6×10⁻³ | 203 d |
   | 1 bar mylar balloon, R 10 × 40 cm (Ø18 cm beam) | 11.6 | 29 k€ | 18.2° | 245 | 3.3×10⁻³ | 507 d |
   | 1 bar mylar balloon, R 5 × 40 cm | 2.9 | 7 k€ | 10.8° | 247 | 3.3×10⁻³ | 3 y |

   - **The balloon does scatter less, and it does not matter.** Every R 5 cell, balloon included, reconstructs at
     σ68 ≈ 11°: over a 40 cm gas column the vertex comes from the Micromegas segments (15°), not from the walls (0.16 % X₀
     for the 30 bar cell). What the balloon loses is gas: ×30 less per volume. Widening it to hold more gas spreads the
     vertex across the beam (18°) and widens the beam through the room.
   - **The capsule is the worst choice per day of beam.** Its 1 % X₀ of walls costs resolution (14°) and converts the ⁸Be γ
     of the target into pairs. It is not in hand anyway (nothing from n_TOF comes with us).
   - Per litre of ³He in the beam all the R 5 designs are within 20 % of each other. The ³He (~2.5 k€/L) is the real
     price of the measurement.
2. **What floods the detector is the room and the shield wall, not the target.** Every capture comes with ~36 000
   neutrons scattered off the ³He itself (σ_el/σ_nγ). The beam leaving the cell returns from the dump and the concrete
   as capture γ. The 4π source behind the wall leaks neutrons (mostly along the collimator bore) and concrete capture γ.
   30 bar cell, big plastics, 30 mA, busiest arm (§5):

   | source | legs /s | Micromegas clusters /s |
   |---|---|---|
   | beam through the target region | 4.8×10³ | 8×10⁴ |
   | room return (dump at 2.5 m, concrete) | 2.0×10⁴ | 1.1×10⁵ |
   | through the wall (with item 3's exit layers) | 1.3×10⁴ | 3.1×10⁵ |
   | cosmics | 38 | — |

3. **The wall decides.** 20 cm borated PE + 80 cm concrete + 5 cm Pb, 0.4 m from the Li, is not enough. It passes
   ~6×10⁸ hard γ/s (concrete capture lines up to 10 MeV) and ~2×10⁹ collided neutrons/s, mostly within 30 cm of the
   Ø8 cm bore (§3). With it the 30 bar cell needs 28 d, DREAM is 37 % live, and the Micromegas see ~1 cluster per arm per
   1.2 µs. **+10 cm Pb and +10 cm borated PE on the exit face** recover 6.7 d: Pb cuts the γ legs ×33, PE the neutron legs ×9.
   Each layer was simulated on its own, and the headline combines them (an estimate). A real port also needs a lined,
   stepped collimator (the halo) and a bunker thicker than the model's 50 cm target-room walls.
4. **DREAM: switch off the single-arm output.** With the 30 bar cell it would need P > 1000. The pair trigger alone gives
   ~620 two-arm triggers/s (correlated room γ and 20 ns randoms): 84 % live as built, 85 % with big plastics, 15 MB/s per
   FEU. Cosmic calibration runs go separately, beam off.
5. **Scintillators: not saturated, but at the edge with the big plastics.** The 75 × 75 × 5 cm slab takes 5.5×10⁷ hits/s
   above 50 keVee (quenched proton recoils from the leaking neutrons), 33 µA anode current at gain 10⁶ and 5.5 hits per
   100 ns gate. Run it at gain ~10⁵ with a ≤ 30 ns gate. The pile-up is in the reach (it pushes the best E_sum cut to
   14 MeV). As built: 4×10⁶ /s and 1.8 µA per 20 × 30 × 2 cm plastic, but the LS cells take 10⁷ /s (88 µA at the assumed
   150 pe/MeV, so lower their gain).
6. **The new risk: neutron recoils in the Micromegas.** 0.3–1 cluster per arm per 1.2 µs at 30 mA, mostly from the wall.
   They are short, dense proton and argon recoils, which a charge/size cut should remove (not modelled). Charged in full
   (e^(−2·occ)), the 30 bar cell needs 23 d instead of 6.7. A bench test with a neutron source decides it.
7. **Full current is still best:** days fall ~1/current (6.7 d at 30 mA, 11.5 at 15, 21 at 7.5, 50 at 3). Pile-up and
   dead time grow more slowly than the signal.
8. **Compared with 20 Oct:** 3.3×10⁻⁴ in 50 d (2.4 d to ATOMKI, beam only) becomes **5.5×10⁻⁴ (6.7 d)** with the room,
   the wall, DREAM and pile-up, still ×2.7 past ATOMKI in 50 days. The beam-only reach of this study's machinery is 4.1 d
   (no pile-up) and 5.1 d (with it).

---

## 1. The target question (analytic, `bham_targets.py` → `out/targets/target_trade.csv`)

At 2.8 MeV × 30 mA, the cell centre 2 m from the Li: φ = 1.4×10⁸ n/cm²/s on the axis (`bham_beam.py`),
⟨σ_nγ⟩ = 53 µb, ⟨α_E1⟩ = 4.7×10⁻³ pairs per capture. n L σ_tot ≤ 0.1 for every candidate, so the captures are
N(³He in the beam) · φ · ⟨σ_nγ⟩. Pressure only sets the volume the same gas needs, and with it the beam size and the
vertex spread.

| target | p | gas | beam Ø | ³He [L STP] (in beam) | captures/s (no Pb) | radial x/X₀ | θ₀ at 10 MeV/c |
|---|---|---|---|---|---|---|---|
| cap500: n_TOF capsule as built | 500 bar | R 1, L 4 + domes | 2 cm | 7.8 (7.8) | 1 560 | 1.09 % | 6.7° |
| c30: NFS build C, Be 0.1 + CFRP 0.3, Be 3 window, Al 4 cap | 30 bar | R 5 × 40 | 8 cm | 87 (55) | 11 100 | 0.16 % | 2.4° |
| c10: Al 25 µm + CFRP 0.3, Be 3 window, Al 2 cap | 10 bar | R 5 × 40 | 8 cm | 29 (18) | 3 690 | 0.15 % | 2.2° |
| bal5: PET 12 + Al 7 µm on 6 CFRP rods (`vessel_design/`), PET 100 µm ends, CFRP 3 mm ring | 1 bar | R 5 × 40 | 8 cm | 2.9 (1.8) | 370 | 0.013 % | 0.6° |
| bal10: the same at R 10 | 1 bar | R 10 × 40 | 18 cm | 11.6 (9.4) | 1 870 | 0.014 % | 0.6° |

A mylar membrane holds no pressure (25 MPa allowable on 12 µm at R 5 cm ≈ 60 mbar). A "balloon" is therefore a 1 bar
cell, and its ³He per volume is fixed at 1/30 of the 30 bar cell. ³He at 2.5 k€/L(STP) (`he4_bag`): 87 L is 217 k€,
which is not in the budget page yet.

## 2. Runs (MX17_Full_Geant branch `bham`, from `soft`)

Code added on `bham` (pushed; binary `…/x17_nfs/MX17_Full_Geant/bin/mx17_full_sim_bham_7182359`, the target runs used
`mx17_full_sim_soft_8f96537`):
- `--room`: a concrete target room around the source (±0.8 m, 1 m deep, 0.5 m walls); a layered shield wall
  (`--shield BPE:200+Concrete:800+Pb:50`, upstream face 0.4 m from the Li, full cross-section) with a collimator bore
  (`--bore`) and a Pb plug in it (`--plug Pb:50`); an experimental room (±2 m, floor −1.2 m, to y = 4 m, 0.5 m concrete);
  a borated-PE beam dump (`--room-dump BPE:2500:600:300`). PE/BPE carry H bound for S(α,β). Volumes `Room_*`, `Shield_*`,
  `Shield_Plug`, `BeamDump_Room`.
- `--src <table>`: the Li spot as a point source with the (cos θ, E) table of `bham_beam.src_tables()`. The neutrons are
  1.96×10⁻⁴ per proton (3.7×10¹³ /s at 30 mA), CM-isotropic stand-in. The ⁸Be γ are 10⁻⁷ per proton, isotropic, ESTIMATE.
- `--ps-plane y` (repeatable; the last one kills) and `--ps-gun file [--ps-drop-uncol]`, with `--ps-gkeep p`: splitting by
  stages through the wall. Each stage writes the n/γ crossing its planes; `bham_ps_merge.py` normalises the weights per
  source particle; the next stage draws from them.
- Scripts: `submit_bham.py` (targets × samples), `submit_room.py` (stages and room runs), `bham_chan_reduce.py` /
  `bham_chan_merge.py` (per-channel time clusters, deposited and quenched light, quenched legs), `bham_ps_merge.py`.

| run | what | size |
|---|---|---|
| B1 | X17 (m 16.8), Born E1 and M1 IPC at W = E\*(0.5 MeV), boosted; 5 targets × as built / big plastics | 5×10⁵ each |
| B2 | beam neutrons, flat 0.01–1.3 MeV, forced first collision + roulette (Ø of each target's beam, vacuum tube) | 3×10⁷ each |
| B3 | beam photons: 478 keV (2×10⁷), 14–19 MeV flat (5×10⁷) | per target × detector |
| R1 | the wall in stages: source → after BPE (1×10⁸ n, 1×10⁷ γ) → +40 cm concrete → exit (4×10⁷ each) | |
| R2 | what crosses the exit face, into the room with the 30 bar cell and the arms: as built, +10 cm Pb, +10 cm BPE | 10⁷ each |
| R3 | the 30 bar cell's beam into the room (dump at 2.5 m), n / 478 keV / ⁸Be γ | as B2/B3 |
| R4 | the same neutrons, dump at 6 m in a 7 m room | 3×10⁷ |
| — | cosmics: the LNL L4 tables (same arms) | |

Outputs `/eos/experiment/ntof/data/x17/bham/<run>/`, merged `…/bham/sel/` (local `birmingham/geant/sel/` via
`fetch_sel.sh`; the wall planes `R1/guns/*_planes.npz`). The jobs reduce in the condor scratch dir and keep 2 ROOT files
per sample, which were re-reduced for quenched light (`lxplus/requench.sh`).

## 3. The wall, in stages (`bham_rates.wall_depth()` → `out/geant/wall_depth.csv`)

Per source neutron, first crossings in +y at each plane, collided particles only:

| plane | n, room, off the bore | n, within 30 cm of the bore | γ, room, off the bore | γ, outside the room |
|---|---|---|---|---|
| after 20 cm BPE | 2×10⁻⁵ | 6×10⁻⁴ | 0.14 | 1×10⁻³ |
| + 40 cm concrete | 1.4×10⁻⁵ | 1.9×10⁻⁴ | 2.1×10⁻³ | 4.7×10⁻⁴ |
| + 80 cm concrete | 1×10⁻⁵ | 8×10⁻⁵ | 1.6×10⁻⁴ | 1.6×10⁻⁴ |
| exit (+ 5 cm Pb) | 4×10⁻⁶ | 5×10⁻⁵ | 1.1×10⁻⁵ | 1.6×10⁻⁴ |

- **The bulk wall works for neutrons; the collimator leaks.** Through the bulk, 20 cm of borated PE already stops the
  sub-MeV neutrons (2×10⁻⁵). What reaches the exit is the halo scattered in the bore walls and the plug (5×10⁻⁵, ×10 the
  bulk), plus the uncollided beam (1.4×10⁻⁴, already in B2/R3 and dropped from R2).
- **The γ come from the wall itself.** The BPE makes 0.17 capture γ per source neutron (2.2 MeV H, 478 keV ¹⁰B). 80 cm of
  concrete takes them to 2×10⁻⁴, but the concrete adds its own capture lines (Si, Ca, Fe; 60 % of the exit γ are above
  1.5 MeV). 5 cm of Pb leaves 1.5×10⁻⁵ per source neutron (bore region included) = 6×10⁸ γ/s into the room.
- **Outside the room:** γ that crossed the exit plane beside the experimental room leaked out through the model's 50 cm
  target-room side walls and went round the wall. The R2 runs use only the records inside the room's footprint. The
  unfiltered runs give the same legs, so this route does not reach the arms in this geometry. A real bunker has thicker
  walls; this is an artefact, not a facility fact.
- The ⁸Be γ source (×2000 fewer particles) leaks 7×10⁻⁴ per γ through the room footprint: 1.5×10³ legs per arm, ×70
  below the neutron source's γ.

Exit-face variants (R2, the neutron source, 30 bar cell geometry), legs in the busiest arm, big plastics:

| exit face | legs from leaking n | legs from leaking γ | slab > 50 keVee /s | MM clusters /s |
|---|---|---|---|---|
| 5 cm Pb (as modelled) | 8.6×10⁴ | 1.0×10⁵ | 5×10⁷ | 8×10⁵ |
| + 10 cm Pb | 6.5×10⁴ | 3.1×10³ | 2.5×10⁷ | 4.3×10⁵ |
| + 10 cm borated PE | 9.4×10³ | 7.5×10⁴ | 5×10⁷ | 6×10⁵ |
| headline: Pb for γ, PE for n (combined, ESTIMATE) | 9.4×10³ | 3.1×10³ | 3.8×10⁷ | 3.1×10⁵ |

## 4. Reach (`geant/bham_geant.py` → `out/geant/<wall>/reach.csv`)

The LNL machinery (`lnl/target/opt_geant.py`) with a gas vertex:
- LNL-calibrated calorimetry, plus the beam pile-up of each arm's channels in a 100 ns gate, drawn from the quenched
  spectra.
- MM segments smeared by 15°. Each segment's closest approach to the beam axis gives (y, r); pointing r < D (90 % of the
  target's own X17, 155–172 mm); collinearity ≥ 20°; arm-to-arm TOF (0.3 ns) against cosmics.
- Vertex (0, ȳ, 0) clipped to the gas; opening angle to the two MM charge centroids.
- Asimov/Fisher in θ (90–180°) × |y| × n_down. IPC(E1) and the beam term are free norms; cosmics fixed; best E_sum window.
- X17 = ρ·IPC(E1) at W(0.5 MeV), ρ_ATOMKI = 1.5×10⁻³. Exposure = DREAM live time at the best prescale.
- The correlated beam term (target-region, room and wall two-arm events) rests on a few MC events per target. It is
  factorised: each event at its own θ, |y|, n_down × the pass fractions pooled over the targets, per source.

| 30 mA, 100–150° per day | X17 at ATOMKI | IPC | cosmics | beam (all) |
|---|---|---|---|---|
| 30 bar cell, big plastics | 178 | 9 390 | 148 | 1 050 |
| capsule, big plastics | 30 | 1 700 | 66 | 3 220 |
| balloon R 5, big plastics | 6 | 330 | 144 | 680 |

The full table is in §0. E1 is the conservative IPC: with the M1 shape (and α) instead, the days fall ×2.3–3.4. Doubling the
factorised beam term moves them by 2 % (30 bar cell) to 10 % (capsule). Wall as first modelled: 28 d
(30 bar cell), 252 d (capsule), 1150 d (balloon R 5). With the MM occupancy charged in full: 23 d (30 bar cell).

## 5. DREAM and the trigger (`geant/bham_rates.py` → `daq_scan.csv`, `daq_live.csv`, `rates_legs.csv`)

Legs (SiPM bar ≥ ½ MIP AND back plastic ≥ ½ MIP, deposited energy as everywhere): from the beam tables, the room
(R3 − B2 of the same cell, scaled by beam rate), the wall (R2) and L4 cosmics. Two-arm randoms at 20 ns. DREAM τ = 298 µs,
non-paralysable. Prescale scan 1…1000 and PAIR only.

| | legs /s, busiest arm | two-arm /s | best P | live | MB/s per FEU |
|---|---|---|---|---|---|
| 30 bar cell, big plastics | 3.8×10⁴ | 616 | PAIR only | 85 % | 15 |
| 30 bar cell, as built | 1.3×10⁴ | 656 | PAIR only | 84 % | 16 |
| capsule, big plastics | 1.5×10⁴ | 98 | 1000 | 96 % | 4 |
| balloon R 10, big plastics | 1.1×10⁵ | 3 240 | PAIR only | 51 % | 80 |

- Neutrons below 1.1 MeV never fire a leg by themselves: the legs are 2.2 MeV H-capture γ in the plastics and concrete
  capture γ. In the kept files the quenched legs are 98 % of the deposited ones.
- **The room term goes with the beam rate (beam area), not with the ³He.** It is ×5 heavier for the Ø18 cm balloon
  beam, for a fifth of the 30 bar cell's signal, and ×16 lighter for the capsule's Ø2 cm beam.
- Moving the dump from 2.5 m to 6 m (R4) cuts the room legs by a quarter (2.0 → 1.5×10⁴) and the slab hits by half
  (8.8 → 4.3×10⁶ /s).

## 6. The scintillators (`rates_channels.csv`)

Quenched light: protons by the Cecil et al. plastic curve, d/t scaled, ions 2 %. Shape from the 2 kept files per sample,
rate from all files. Busiest channel, 30 mA, headline wall:

| | > 50 keVee /s | > leg threshold /s | anode µA (gain 10⁶) | hits per 100 ns |
|---|---|---|---|---|
| big slab, 30 bar cell | 5.5×10⁷ | 3.0×10⁶ | 33 | 5.5 |
| big slab, capsule | 3.9×10⁷ | 9×10⁵ | 17 | 3.9 |
| as built plastic, 30 bar cell | 4.3×10⁶ | 1.2×10⁵ | 1.8 | 0.43 |
| as built LS cell, 30 bar cell | 1.1×10⁷ | 1.2×10⁶ | 88 (150 pe/MeV) | 1.1 |
| SiPM bar, 30 bar cell | 3.4×10⁵ | 7×10⁴ | — | 0.03 |

Light yield is 10 pe/MeV in the plastics (the `lnl_calo` value) and 150 in the LS (**ESTIMATE**). **(ask)** the PMTs and
bases of the big slabs: at gain 10⁶ and 33 µA a passive divider sags; run at 10⁵. Gate: the slab's own pulses are
~10–20 ns, so a 30 ns gate cuts the pile-up ×3. The target region alone gives 8.6×10⁶ /s and 5.6 µA; the rest is the room and,
mostly, the wall.

## 7. The Micromegas

Clusters above 2 keV per arm (a MIP leaves ~8 keV in the 30 mm gap; ~65 % of the neutron clusters are above 5 keV):
1.9×10⁵ /s from the target region and the room, 3.1×10⁵ /s through the wall (headline). That is 0.6 per arm per
1.2 µs for the 30 bar cell, 0.4 for the capsule and 1.1 for the wide balloon. These are proton recoils off the isobutane
and argon recoils: short, heavily ionising, point-like, unlike a lepton track crossing the gap. A charge/size cut is the
obvious defence, untested. Charged in full the reach drops ×3.4. **Bench test first** (AmBe or a D-D generator on one
chamber).

## 8. Risks, ranked

| # | risk | size | what to do |
|---|---|---|---|
| 1 | Neutron recoils in the Micromegas | 0.6 cluster per arm per µs (30 bar cell, 30 mA) | cluster cut on a neutron-source bench; more PE on the exit and round the bore |
| 2 | The wall / collimator design is ours, not the facility's | ×4 in days between the walls tried | **(ask)** the real wall, room and where a port could go; simulate a stepped, lined collimator and a thicker bunker |
| 3 | The room return of the beam (dump, concrete) | 2×10⁴ legs per arm; 360 correlated two-arm /s | dump far away (6 m: −25 % legs, −50 % slab), lined with borated PE or ⁶Li; line the room |
| 4 | Big-slab PMT current | 33 µA at gain 10⁶ | gain 10⁵, active base, 30 ns gate |
| 5 | ³He inventory and cost | 87 L ≈ 217 k€ for the 30 bar cell | budget it; 30 L (10 bar) gives 23 d |
| 6 | Source model | CM-isotropic ⁷Li(p,n); ⁸Be γ yield 10⁻⁷/p ESTIMATE | measured 0° spectrum and γ yields from Birmingham (ask) |
| 7 | The factorised beam term | few MC events | doubling it costs 2–10 % in days (free norm) |

Not modelled: the real room, its floor and air activation; the accelerator's own γ/x-ray background; the target vessel
and the moderator (the source is a bare point); the cell mount and the beam tube's upstream window inside the room;
a cosmic veto.

## 9. Code and outputs

| file | what |
|---|---|
| `bham_targets.py` | §1, the analytic trade → `out/targets/target_trade.csv` |
| `bham_beam.py` | the source (now also `src_tables()`: the Geant4 point-source tables) |
| `geant/bham_common.py` | source rates, targets, tables, per-row rates, `WALL` variant |
| `geant/bham_geant.py` | §4 reach (`--wall leakr|leakpb|combo`, `--mm`, `--scan`) → `out/geant/[<wall>/]reach.csv`, `days_vs_current.csv` |
| `geant/bham_rates.py` | §3, §5–7 → `rates_channels.csv`, `rates_legs.csv`, `daq_scan.csv`, `daq_live.csv`, `room_variants.csv`, `wall_depth.csv` |
| `geant/deck/build_target_deck.py` | the slide note `birmingham-target-geant` |
| `geant/lxplus/` | `bham_pipe.sh` (merges), `bham_driver.sh` (stage chain), `requench.sh`, `bham_ps_filter.py` (copies) |
| `geant/fetch_sel.sh` | EOS → `geant/sel/` (gitignored) |

`out/geant/` is the wall as first modelled, `out/geant/leakpb/` adds 10 cm Pb, and `out/geant/combo/` is the headline
(Pb + PE).
