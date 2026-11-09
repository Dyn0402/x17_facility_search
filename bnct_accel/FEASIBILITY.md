# Accelerator BNCT machines as X17 sources — feasibility

Facility record: `FACILITY.md`. Slides (built, not published): `out/bnct-accel-x17-feasibility.html` (`deck/build_deck.py`). Beam model and reach: `bnct_accel_beam.py`,
on top of the shared engine `survey/soft_sim/soft_reach.py` (imported, unchanged).

## 0. Answer — 2026-11-09

**Overall call: WATCH.** Not a top-3 option. The survey's hunch is right about the physics and wrong about the opportunity.

- **The bare Li target is ×2–4 better in reach than the moderated port at the same machine class.** A bare 2.8 MeV / 15 mA Li target 2 m from the 30 bar cell with 5 cm Pb gives X17/IPC = 5.1×10⁻⁴ at
  3σ in 50 d (big plastics; as built 1.6×10⁻³), 5.7 d to ATOMKI. Birmingham in the same engine: 3.3×10⁻⁴, 2.4 d (5.5×10⁻⁴, 6.7 d in its full-room Geant4).
- **But no hospital machine offers a bare target.** The Li sits inside the beam-shaping assembly. The bare options that exist are Birmingham itself (already the reference) and BINP VITA (works today,
  but CERN ended relations with Russian institutes on 30 Nov 2024, and sanctions limit what can be shipped). Nagoya NUANS is the only other Li research machine worth asking.
- **The moderated port, replacing the ILL-scaled 2.5×10⁻³, reaches 1.3×10⁻³ with the IAEA contamination (Li port, 10⁹ n/cm²/s, cell 40 cm from the port: 39 d to ATOMKI; as built 3.0×10⁻³), in a
  bracket of 8.3×10⁻⁴ (fast-neutron dose at the 7×10⁻¹³ Gy cm² limit) to 1.8×10⁻³ (no fast tail at all).** Limit: DREAM live time (0.5), from legs made by the beam at 2×10¹⁰ n/s through the spot.
  A pessimistic sub-keV background (×10) gives 2.6×10⁻³. The signal comes largely from the contamination: in the 7×10⁻¹³ case the fast tail supplies 64 % of the ³He captures.
- **What would have to be true to make top-3:** a university/national Li machine (Nagoya is the candidate) would have to agree to remove its BSA or provide a beam tube, with arms 2 m from the target and weeks of beam. Then it is a Birmingham-class site at ×1.5 lower reach, a backup and never a replacement.

| 50 d, E\* ≤ 22 MeV, 30 bar cell: big plastics (as built) | X17/IPC at 3σ | days to ATOMKI | limit |
|---|---|---|---|
| Birmingham, 2 m, 5 cm Pb (engine; full Geant4 5.5×10⁻⁴, 6.7 d) | 3.3×10⁻⁴ (1.0×10⁻³) | 2.4 (22) | statistics |
| **Bare: Nagoya 15 mA, 2.8 MeV, 2 m, 5 cm Pb** (needs the BSA off) | **5.1×10⁻⁴** (1.6×10⁻³) | 5.7 (59) | statistics; ESTIMATE with room ×1.67 → 8.5×10⁻⁴, 16 d |
| Bare: Nagoya 11 mA (last published) | 6.2×10⁻⁴ (2.1×10⁻³) | 8.7 (94) | statistics |
| Bare: nuBeam class 2.6 MeV, 30 mA, 2 m, 5 cm Pb (hypothetical) | 3.8×10⁻⁴ (1.2×10⁻³) | 3.2 (31) | statistics |
| Bare: CICS class 2.5 MeV, 20 mA, 2 m, 5 cm Pb (hypothetical) | 5.4×10⁻⁴ (1.8×10⁻³) | 6.6 (69) | statistics |
| Bare: Alphabeam class 2.5 MeV, 10 mA (ESTIMATE, hypothetical) | 8.8×10⁻⁴ (3.1×10⁻³) | 17 (207) | statistics |
| Bare: VITA 2.2 MeV, 10 mA, thin Li, 0.5 m (exists; not accessible) | 2.3×10⁻⁴ (6.4×10⁻⁴) | 1.1 (9) | statistics; no shielding room at 0.5 m |
| **Moderated Li port, 10⁹, 40 cm, IAEA 2×10⁻¹³** (the central moderated case) | **1.3×10⁻³** (3.0×10⁻³) | 39 (198) | DREAM live 0.53 |
| Moderated Li port, 10⁹, 40 cm, D_f at 7×10⁻¹³ | 8.3×10⁻⁴ (1.8×10⁻³) | 15 (74) | DREAM live 0.52 |
| Moderated Li port, 10⁹, 40 cm, no fast tail | 1.8×10⁻³ (4.3×10⁻³) | 76 (403) | DREAM live 0.53 |
| Moderated Be port (NeuCure Kansai 1.4×10⁹), 40 cm, 7×10⁻¹³ | 1.1×10⁻³ (2.0×10⁻³) | 27 (90) | DREAM live 0.41 |
| Moderated Li 7×10⁻¹³, sub-keV background ×10 | 2.6×10⁻³ (1.9×10⁻³) | 151 (81) | DREAM (throttled to 0.5) |
| Moderated Li 7×10⁻¹³, n_TOF capsule, 40 cm | 2.3×10⁻³ (8.4×10⁻³) | 113 (1554) | statistics (cosmics) |

Every row with neutrons ≤ 2.75 MeV has E\* ≤ 22 MeV = all E\*. The Be port with a tail to 10 MeV: all E\* 9.9×10⁻⁴ (vs 1.1×10⁻³).

## 1. Is the engine called correctly? — 2026-11-09

`bnct_accel_beam.py --check` rebuilds the Birmingham sources from `soft_reach.sources()`, runs `components`, `at_throttle` and the throttle scan, and compares with the published
`survey/soft_sim/out/soft_reach.csv`: bham_26_2m_pb5 and bham_28_2m_pb5, big plastics and as built, **ratio 1.0000 ± 0.0001** in ρ₅₀ and floor (`out/bnct_repro_check.csv`). Thin-Li sources come from
`franz/franz_beam.py` and thick-Li from `birmingham/bham_beam.py`, reused without edits.

## 2. Beam model — 2026-11-09

`bnct_accel_beam.py` → `out/bnct_reach.csv`, `bnct_components.csv`, `bnct_spectra.csv`, `bnct_capture_value.{csv,png}`, `bnct_reach_fig.{csv,png}`.

**Bare target.** Birmingham's slowing-down MC, 10¹² n/s/mA at 2.6 MeV (Nagoya's PHITS 1.13×10¹²/mA at 2.8 MeV agrees with this normalisation to 3 %; `FACILITY.md`). Thin Li: FRANZ's model (5×10¹⁰ n/s/mA at 2.0 MeV; VITA's quoted thick-target 1.1×10¹¹ n/mC at 2 MeV p is ×2 higher, so our VITA 2.0 and 2.2 MeV rows lean low).
Target γ: 478 keV and 1×10⁻⁷/p ⁸Be lines (thick; ESTIMATE), direct capture only for thin Li.

**Moderated port (ESTIMATE; no broad-band spectrum of any accelerator port is published).** 1/E, 0.5 eV–10 keV, normalised to Φ_epi; fast tail 10 keV to E_max ∝ E⁻¹ (or E⁻²·⁵), size set so its tissue kerma gives D_f/Φ_epi (2×10⁻¹³ IAEA; 7×10⁻¹³ Tanaka 2025, the quoted limit). E_max 0.9 MeV for Li, 10 MeV for Be (the Be spectrum at 30 MeV is hard). Fast/epithermal neutron ratio: 2.1 % and 7.3 % (Li), 3.0 % (Be).
γ from D_γ/Φ_epi = 2×10⁻¹³ as 2.2 and 7.7 MeV lines (70:30; ESTIMATE), plus for Li machines the ⁸Be lines at 15 mA through the BSA with T = 0.1 (ESTIMATE).
Φ_epi: 10⁹ (IAEA floor; Nagoya goal) and 1.4×10⁹ (Kansai Ø12 cm). Port-to-cell geometry: cell at the port (g = 1, not physically possible with the upstream arms) and at 40 cm (g = 0.4; ESTIMATE from a Ø12–20 cm diverging beam).

**The sub-keV part (N5 starts at 1 keV).** 77 % of a 1/E flux is below 1 keV. Handled in three steps, none a Geant4 result:
1. *Signal and IPC*: `survey_yield.captures_per_neutron` integrated from 0.5 eV, added to the lowest analysis bin, times an acceptance 0.5 because those vertices sit near the upstream window (attenuation length 1.6 cm at 1 eV, 16 cm at 100 eV; ESTIMATE). Sub-keV gives only 22 % of the epithermal captures at this acceptance (329 of 1520 /s at 10⁹), so the choice matters little: acceptance 1.0 moves 8.3×10⁻⁴ to 7.9×10⁻⁴.
2. *Background*: the same neutrons go into the 1–3 keV bins of N5 (25 MC singles there in big plastics, ±20 %). The ×1 proxy assumes the capture-γ chain is unchanged; the ×10 row is the sensitivity. **This is the largest uncertainty in the moderated reach.**
3. *Rate*: they count in the n/s through the spot.

**Why the bare target wins.** One 0.5 MeV neutron is worth ~150 sub-keV neutrons in ³He(n,γ) (`out/bnct_capture_value.png`: 10⁻⁸ captures/n below 1 keV, 1.5×10⁻⁶ at 0.5 MeV). Moderation trades that for ×6 more neutrons through the spot (2×10¹⁰ n/s at 40 cm from a 10⁹ port, against 3.5×10⁹ from a bare 15 mA target at 2 m), far short of the ×150.

## 3. The scan — 2026-11-09

- **Machine, energy and current (bare):** 2.3–2.8 MeV thick Li, 2.0 and 2.2 MeV thin (VITA), 10–30 mA. Reach follows n/s through the spot. Throttle scanned (never needed for bare rows).
- **Distance and filter (bare):** 1 and 2 m (thick), 0.5 and 1 m (thin); 0 and 5 cm Pb. At 2 m no Pb is ×1.7 better than 5 cm Pb in the engine (nuBeam class 2.3×10⁻⁴ vs 3.8×10⁻⁴), but the 15–18 MeV lines (3.3×10³ per day in the window at 2 m unfiltered; 194 with Pb) and the room lesson argue for keeping Pb. 1 m is ×2 better still but puts the arms in the 4π field: the reach of those rows (1.2–1.4×10⁻⁴) is not claimed.
- **Cell:** the capsule loses ×2.7 at 40 cm (2.3×10⁻³ vs 8.3×10⁻⁴) in the moderated case: it covers π cm² of a 50 cm² beam and its 3.3× areal density does not pay for it. The engine's background tables assume the 30 bar geometry, so the capsule row is an ESTIMATE; its worse angular resolution is not included (it would hurt further).
- **Duty:** every accelerator here is DC (electrostatic, cyclotron), so no gate gain; iBNCT is a 50 Hz linac, not modelled.
- **Moderated Φ and geometry:** at the port (g = 1, not realisable) the reach is throttled by DREAM; 40 cm is the honest position. Raising Φ to 1.4×10⁹ gains 7–9 % (DREAM again): more neutrons per second are not the lever. The lever is fewer legs per neutron (a veto or faster DAQ, as in `daq_trigger/`).
- **As built:** moderated rows are only ×1.8–2.3 worse than big plastics (legs are ×7 fewer), and none reaches ATOMKI in 50 days: 1.8–4.3×10⁻³ (74–403 d).

## 4. Backgrounds and walls — 2026-11-09

- Bare at 2 m + 5 cm Pb, Nagoya 15 mA: statistics, cosmics = IPC (5.3×10³ each per day in the window, no veto). A cosmic veto is the lever, as at Birmingham.
- Moderated at 10⁹: live 0.5, Micromegas occupancy 1 %; legs per arm 1.7×10⁵/s at the port. Beam-correlated events: 1.7×10³/day after the vertex and E_sum cuts (all θ, at the port, big plastics; from 25 MC events), about 150/day in the 100–150° window.
  The limit is the DREAM wall. A faster DREAM mode would help the moderated port as it would everywhere.
- **Room/shield caveat.** The engine is beam-only with a vacuum tube and a Ø8 cm spot. Birmingham's full-room Geant4 moved the reach ×1.67 (3.3→5.5×10⁻⁴), and that factor is applied as `rho3_room` to all rows in `bnct_reach.csv`, as an ESTIMATE. It is if anything too low for a moderated port: the arms would stand in a treatment room with no beam dump, right in front of the BSA, and the patient-side leakage is unknown.

## 5. Practical scorecard — 2026-11-09

| | bare target at a BNCT machine | moderated port at a BNCT machine |
|---|---|---|
| Beam exists today? | Li: yes, but inside the BSA. VITA operates; Birmingham is the reference. | Yes: NeuCure insured clinical service, Helsinki first patients May 2025. |
| Time to first beam for us | ≥ 2–3 y at a university machine (BSA change, shielding) (ask) | ≥ 2 y at best; realistically never for an active clinic |
| Access realistic? | Only Birmingham or (with an agreement) Nagoya; VITA blocked by politics | No user programme at hospitals; regulated medical device |
| Space/shielding/port work | Must remove or by-pass the BSA, then build a Birmingham-type shield wall | Arms in the treatment room at the port; no dump; room layout unknown (ask) |
| Cost | Birmingham-scale wall and dump + machine re-fit, order €300k+ (ESTIMATE) | €100k–300k shielding/rig if allowed at all (ESTIMATE) |
| Radiation safety, ³He | Bare target activates; ⁷Be ~ few TBq (Birmingham numbers) | Patient-room licence does not cover a pressurised ³He cell; 30 bar × 40 cm is not a medical device (ask) |
| Competition for beam time | University machines: BNCT development; clinics: patients | Patients every day |
| Restrictions | BINP: CERN ended relations with Russian institutes 30 Nov 2024; trade sanctions on electronics | Clinical regulation; investigational devices |
| Compared with Birmingham | ×1.5 weaker at Nagoya current; same shielding work; not obviously cheaper | ×4 weaker (1.3×10⁻³ vs 3.3×10⁻⁴ engine; ×2.3 against the full-room 5.5×10⁻⁴), ×6 the days against the full-room figure, before any room penalty on the port |
| FRM II MEDAPP / FRANZ | FRM II MEDAPP 4.2×10⁻⁴ (reactor off); FRANZ 3.3×10⁻⁴ (design, not yet at 2 MeV), 2.2×10⁻³ licence | — |

**Overall: WATCH.** Reasons: (1) the physics reach of the moderated port is real but DREAM-limited and reaches ATOMKI only with big plastics and some fast contamination (15–39 d; 76 d with no fast tail); (2) the bare mode is a good source only where it already exists, at Birmingham; (3) no machine that is not Birmingham has a route to install the arms. The single thing that would change it: a yes from Nagoya (or another Li research machine) to run without the BSA.

## 6. What the catalogue said, and what changes

The catalogue's MARGINAL and its reason were broadly right (a neutron-rich but low-value beam) with an ILL-scaled number of 2.5×10⁻³. The real-spectrum number is 1.3×10⁻³ in the central case, in a bracket 8.3×10⁻⁴–1.8×10⁻³ that the moderator cannot settle, because the contamination is the signal: "×3.6 per neutron" over thermal undercounts what the fast tail contributes.

## 7. Next steps

1. Ask Nagoya University (NUANS) **(ask)**: is the Dynamitron operating, at what current, can the BSA be removed or by-passed; and who runs it.
2. Ask INFN/UniPV about Alphabeam at CNAO **(ask)**, only after it is installed: research time, energy and current.
3. If a real port spectrum becomes available, replace the ESTIMATE tail in `bnct_accel_beam.py` (`MOD`).
4. One new Geant4 run decides the moderated case, replacing the 1–3 keV proxy: MX17_Full_Geant branch `soft`, `scripts/submit_nfs.py --spectrum` with a log-flat neutron gun 0.5 eV–1 keV, same NFS cell and arms as N5 (forced first collision not needed below 1 keV, the cell absorbs them; keep the roulette), big plastics and as built, ≥ 3×10⁸ primaries for ~100 ok singles per decade (N5 had 25 singles in 1–3 keV from 9×10⁷).
5. Do not spend Geant4 on the bare rows until a real bare target exists: they would follow Birmingham's TARGET_GEANT.md.
