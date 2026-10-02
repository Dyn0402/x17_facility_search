# ILL feasibility — the thermal X17 search on a reactor beam

Started 2026-10-01. Can the n_TOF X17 apparatus run at the Institut
Laue-Langevin (Grenoble), and what do our own n_TOF results and Geant4
campaigns say it would see?

| file | what it is |
|---|---|
| `FACILITY.md` | Everything found about the ILL: reactor and cycles, PF1B / FIPPS beams, proposal routes (EBTA), tritium, polarised ³He, theory context, alternatives, sources |
| `ill_rates.py` | The projection: the n_TOF Geant4 thermal contract carried to a cold beam, two target configurations, rate limits, yields, sensitivity, the polarised option |
| `make_report.py` | Builds `report.html` + figures from `ill_rates` |
| `POLARISED.md` | Polarised n + polarised ³He: the physics, ILL hardware (Tyrex, cells, magic box, PF1B polariser), in-beam relaxation risk, the arithmetic, open questions |
| `GEANT_PLAN.md` | The lxplus campaign that replaces every *analytic scaling* in `ill_rates` with a simulation |
| `HANDOFF_SIM.md` | The brief for the first lxplus campaign (2026-10-01): no capsule; a pressure × wall × radius scan (1–3 bar, mylar vs Kapton, R 40/100 mm), each cell centred on its (n,γ) production; realistic H113 beam; what to bring back (supersedes `GEANT_PLAN.md` where they differ) |
| `cell_length.py` | ³He length needed against the measured H113 spectrum, and the stop-depth law per scan cell -> `out/cell_length.csv`, `out/cell_depth.csv`, `out/h113_spectrum.csv` |
| `beam_spot.py` | H113 open-beam profile vs distance and the rate into a collimated spot -> `out/beam_spot.csv`, `out/figures/beam_profile.png` |
| **`FEASIBILITY_SIM.md`** | **The Geant4 answer (2026-10-02): can we measure X17 at the ILL? Scattering, rates, backgrounds, reach per configuration, detector requirements** |
| `SIM_STATUS.md` | Log of the lxplus campaign: paths, MX17 code (branch `ill`), validation (V0/V1), every run, deviations from the handoff, overnight fixes |
| `sim_feasibility.py` | The counting model behind the Geant4 answer: S1 pair libraries + C1/C1w/C1g/K1 per-event arm tables -> X17, IPC, ³He(n,γ), accidentals, cosmics vs opening angle, for any trigger menu / Esum cut / timing; Asimov reach |
| `sim_report.py` | Figures and `results.json` from `sim_feasibility` (spectra, reach vs rate, Esum, scattering and resolution vs KE) |
| `sim_variants.py` | One assumption changed at a time (timing, μ veto, vertex estimator, backgrounds off) -> `variants_v3.csv` |
| `make_scan.py` | `results/scan_v1.csv`: one row per cell configuration G1–G6 (the table `HANDOFF_SIM.md` §7 asks for) |
| `results/scan_v1.csv` | Contract ladders, acceptance × efficiency per menu, angular resolution per estimator, vertex σ, reach |
| `sim/analysis_v3/` | Small copies of the lxplus analysis outputs (`v3_base`, `v3_timing`, `variants_v3.csv`, `contract_ladders.csv`); the full set is on EOS |
| `deck/build_deck.py` | The slide summary (claude.ai Slides files in `deck/build/`, standalone `out/feasibility_deck.html`, live at dylan-neff.web.cern.ch/notes/ill-x17-feasibility.html) from `analysis_v3` + `xtra_artifact.json` |
| `sim/lxplus/` | The lxplus drivers: condor pipelines, `run_final.sh` (reproduces `analysis_v3` + `scan_v1`) and the one-off diagnostics quoted in `FEASIBILITY_SIM.md` (incl. `xtra_artifact.py`: cosmic geometry, veto panels, segment collinearity, vertex/radius acceptance, §8) |

```bash
python ill/ill_rates.py --write     # all tables + cross-checks -> ill/out/*.csv
python ill/make_report.py           # -> ill/out/report.html + figures
python ill/ill_rates.py --contract /eos/experiment/ntof/data/x17/ill/contracts/C1_G*
                                    # Geant4 vs analytic ladders -> contract_ladders.csv
```

The Geant4 campaign runs on lxplus (CERN):

| what | where |
|---|---|
| **all simulation output (unlimited space)** | **`/eos/experiment/ntof/data/x17/ill/<run>/<config>/`**; contracts in `…/ill/contracts/`, analysis in `…/ill/analysis/` |
| **AFS working directory** | **`/afs/cern.ch/user/d/dneff/work`** (= `/afs/cern.ch/work/d/dneff`) |
| simulation code | `MX17_Full_Geant`, branch `ill` (GitHub `Dyn0402/MX17_Full_Geant`); isolated lxplus clone in `…/work/git/x17_ill/` |
| analysis scripts on lxplus | `…/work/git/x17_ill/analysis/` (copies of `sim_*.py`, `make_scan.py`, `ill_rates.py`; `sim/lxplus/run_final.sh`) |

Needs numpy, pandas and matplotlib (the nTof_x17 `.venv` works). The study
is self-contained: its nTof_x17 inputs (the Geant4 thermal-accounting contract
and the ³He pair cross sections from `ipc_channels`) are carried as constants
with provenance. When an nTof_x17 checkout is present (`$NTOF_X17`, default
`~/PycharmProjects/nTof_x17`), each run re-derives them and prints
`CONTRACT CHECK` / `³He CHECK`. `figstyle.py` and `report_style.py` are
vendored copies of the nTof_x17 house style.

Paths below that are not in this directory refer to the **nTof_x17** repo
(`sept26_prelim_analysis/…`, `ntof_athens_26/…`) or to
`~/CLionProjects/MX17_Full_Geant`. Moved here from nTof_x17 on 2026-10-01,
next to `../ganil_nfs/`.

---

## The Geant4 answer (2026-10-02) — read this first

Full write-up: **`FEASIBILITY_SIM.md`**. It supersedes the analytic
configuration-B numbers below wherever they differ.

- **Feasible only with ~200 ps per-arm timing and a cosmic-muon veto.** Then
  one 50-day cycle at ~10¹⁰ absorbed n/s reaches X17/IPC(M1) ≈ 0.85–1.3 × 10⁻²
  at 3σ, and the reference ratio 2.5 × 10⁻² is a ~6–9σ effect.
- **With the timing assumed so far (σt 0.5 ns, 2τ 5 ns) and no veto, it is
  not:** the reach is ~5 × 10⁻² (the reference would be ~1.5σ). Cosmic rays
  dominate (~10⁶ events per cycle passing Esum > 13 MeV).
- **Lepton scattering is not the limit.** X17 leptons carry ≳ 3.5 MeV
  (softer lepton median 6.3 MeV), scattering before the gap is ~5° at 6 MeV
  and comes mostly from the Micromegas entrance and the air, and an ideal
  vertex improves the reach by only ~13 %.
- **Single-neutron fakes** are kinematically capped at 10.83 MeV (¹⁴N), and
  none survive Esum > 12 MeV in the wall/air-biased MC. Cut at Esum > 13 MeV.
- **The Micromegas ceiling is ~1.4 × 10¹⁰ n/s, not ~10¹¹.** The simulated gap
  rate is ~7× the analytic window scaling: captures of scattered neutrons in
  air and in the detector itself dominate. So the "ceiling" row below is not
  reachable; ~10¹⁰ is also the optimum once cosmics are suppressed.
- **Cells:** R = 40 mm (G1, G3, G5) are equivalent and best; R = 100 mm is
  30–50 % worse. Recommended: G1 (1 bar, 12 µm mylar), or G5 if ³He
  permeation through mylar is a problem.
  - It is a problem for bare mylar (~22 L/cycle). The fix is a 1 bar
    Al-foil-laminate skin, and the air ¹⁴N fix is a He flight tube; see
    `../he4_bag/README.md`.
- **Follow-up (§8 of `FEASIBILITY_SIM.md`).** A time-ordered ceiling panel
  of ~2 × 2 m at 0.6 m covers 99.3 % of faking muons. A free offline veto
  (are the two Micromegas segments one straight line?) keeps 91 % of X17 at a
  20° cut; it works if the chambers measure muon direction to ≲ 5°, which the
  cosmic bench can measure. The radius does not set the vertex (the beam spot
  does). R = 100 mm loses backward leptons, probably to the upstream Al cap.
- **Accidentals (§9 of `FEASIBILITY_SIM.md`).** With the cosmics vetoed,
  accidentals are the next fixed background. They are pile-up of two singles
  from two different neutrons, not one-neutron pairs: no single capture
  passes 13 MeV. Al (80 % of the pairs in G1; the 8 mm upstream end cap alone
  63 %) and air ¹⁴N carry them. With an oracle removing the Al singles, the
  reach goes from 8.3 to 6.0 × 10⁻³; removing Al and air gives 5.2 × 10⁻³.
  Line the cap with ⁶LiF and add a He flight tube.
- **Biggest remaining lever:** energy containment. The stack holds ~40 % of the
  lepton energy, so the Esum cut keeps only 25 % of X17 pairs; a calorimeter
  could give ×4 signal.

## The analytic answer (2026-10-01)

**Feasible. It is also the only way the thermal measurement becomes
statistics-rich. But it covers the s-wave half of the physics only.**

1. **Our thermal results transfer directly.** Every ILL neutron is below
   0.1 eV, the regime of n_TOF's >1 ms gate. There, both ³He channels and every
   wall capture go as 1/v. The gas absorbs every neutron, and radiative
   captures per absorption (1.03×10⁻⁸), pairs per absorption (4.8×10⁻¹¹,
   2.9×10⁻¹² above 109°) and the M1/E0 mix are all wavelength-independent.
   The only thing that changes is the **wall**: its capture probability per
   neutron grows with λ, by 2.71/0.651 = **4.2×** from n_TOF's in-gate
   spectrum to PF1B's 4.87 Å (the H113 spectrum's capture-weighted k; it was
   2.36 / 4.25 Å from the instrument sheet until 2026-10-02). That factor
   carries the Geant4 thermal contract (10⁹ neutrons, nose-first) across.

2. **With the as-built capsule** (configuration A), PF1B is
   **detector-limited at ~5.7×10⁸ absorbed n/s**. Micromegas pile-up and a
   1 kHz DREAM trigger bind together. **One ILL day = ~660 n_TOF thermal-gate
   days.** FIPPS's halo-free 1.5 cm pencil beam fits the capsule bore and gives
   ~210 gate-days per day, beam-limited.

3. **A reactor lets us drop the 500 bar vessel** (configuration B). At 4 Å a
   few bar of ³He absorbs everything within centimetres. A 0.5 mm Be window
   makes **170× fewer wall captures** than the 5.5 mm Al nose, and the cell is
   its own γ-free beam stop. At a conservative 10¹⁰ n/s that is **~12,000
   gate-days per day**. One 50-day cycle then reaches X17/IPC(M1) ≈ 3×10⁻³ at
   3σ against the ³He continuum, against 0.35 for 50 days of n_TOF's thermal
   gate. At the rate table's reference (2.5×10⁻²) that is ~1,600–2,900 X17 in
   the trigger per cycle.

4. **No time-of-flight, no flash.** The whole n_TOF flash/HV-recovery story
   (0–1 ms veto, 1–5 ms recovery) is moot. The price is cosmics: continuous
   running gives ~150× the daily live time of n_TOF's gate, though per absorbed
   neutron it is ~10× less.

5. **What the ILL cannot do:** reach the p-wave 0⁻ / 1⁻ / 2⁻ states, which are
   suppressed ~10⁻⁵ below 2 eV and drive the ATOMKI ³H(p,e⁺e⁻) fit. That is
   n_TOF's MeV window, and the ILL complements it rather than replacing it.

6. **What the ILL can do that n_TOF cannot: choose the entrance channel.**
   E0 pairs come only from the singlet 0⁺, and M1 pairs only from the triplet
   1⁺. With PF1B's 99.7 % polarised beam and Tyrex-polarised ³He at 70–75 %,
   flipping the neutron spin swings the M1 share ~9–12×. That measures the E0
   fraction directly (the 6–52 % band nTof_x17 `IPC_MISSING.md` cannot close by
   calculation). And because V/A/P bosons come only from 1⁺ and S only from 0⁺,
   a spin asymmetry in an angular excess would give the boson's quantum
   numbers. Even with an **unpolarised** beam, a polarised opaque cell gives
   2–4.5× more M1 pairs per absorbed neutron, the only way found past the
   thermal self-shielding ceiling. The costs: glass cell walls (~10× the
   wall captures of Be) and beam-induced ³He relaxation. Full record in
   `POLARISED.md`.

| | rate (absorbed n/s) | set by | n_TOF gate-days / day | min X17/IPC, 3σ, 1 cycle | S/B at trigger | tritium / cycle |
|---|---|---|---|---|---|---|
| n_TOF >1 ms gate | 8.6×10⁵ | duty cycle | 1 | 0.35 | 9×10⁻⁸ | — |
| A: capsule @ FIPPS | 1.8×10⁸ | beam | 210 | 2.4×10⁻² | 5×10⁻⁸ | 1.4 MBq |
| A: capsule @ PF1B | 5.7×10⁸ | Micromegas | 660 | 1.4×10⁻² | 2×10⁻⁸ | 4 MBq |
| B: Be cell @ PF1B, design | 10¹⁰ | chosen | 1.2×10⁴ | 3.3×10⁻³ | 4×10⁻⁶ | 77 MBq |
| B: Be cell @ PF1B, ceiling | 9.8×10¹⁰ | Micromegas | 1.1×10⁵ | 1.0×10⁻³ | 4×10⁻⁶ | 0.75 GBq |

(`report.html` has the full table, the figures and the reasoning.) The
min-X17/IPC column counts the ³He continuum only. The Geant4 campaign adds
cosmics, accidentals and the trigger/Esum efficiency, and moves the design
point to 0.85×10⁻² (with 200 ps timing + μ veto) or 5×10⁻² (without); the
Micromegas ceiling is ~1.4×10¹⁰, not 9.8×10¹⁰. See `FEASIBILITY_SIM.md`.

## What is *not* settled — in order of how much it could move the answer

1. **The X17 rate at thermal energies is not known, and nobody has asked.**
   Viviani et al. (PRC 105, 014001) have the machinery but tabulate from
   E_n = 0.17 MeV, where the p-wave 1⁻ dominates. The thermal 1⁺→0⁺ photon
   is strongly hindered (meson-exchange dominated), so the X17/γ ratio there
   could differ from the MeV value by a lot, in either direction. **One run of
   their code at E_n < 10 eV, for their fitted V and A couplings**, is the single
   most valuable input to an ILL proposal. It is the same request
   nTof_x17 `IPC_MISSING.md` already makes for the E0 matrix element, so make it once.
2. **Background floor at the site.** Ambient γ/fast-n in the PF1B casemate,
   beam-borne γ down H113, and the two-arm cosmic rate do not scale from n_TOF.
   In configuration B they are probably the floor. They can only be measured:
   ask for an EASY/DDT day with a bare arm or two.
   *2026-10-02:* the simulated sea-level cosmic rate (K1) is the floor that
   matters: ~7 Hz two-arm above 12 MeV. It needs ~200 ps timing and a μ veto
   (`FEASIBILITY_SIM.md` §3).
3. **The trigger-level S/B.** Pair-tags are 92 % two Comptons from one wall
   capture. Even the Be cell leaves S/B ~4×10⁻⁶ at the trigger, so offline
   rejection (two MM tracks pointing at the cell, opening angle, LS energy) must
   supply ≳10⁶. This is the **same open problem as at n_TOF**, and the ILL's
   statistics would finally let it be measured on data rather than simulation.
   *2026-10-02:* above Esum > 12–13 MeV no single-neutron event survives in
   the Geant4 campaign (the hardest non-³He line is ¹⁴N at 10.83 MeV); what
   remains is ³He(n,γ), accidentals and cosmics (`FEASIBILITY_SIM.md` §4).
4. **Configuration B is an analytic scaling.** That covers window captures,
   t/X₀ for conversion, and the Al-like cascades. `GEANT_PLAN.md` R2–R5
   replace it, including cold-neutron thermal scattering in the window, which
   the current physics list lacks.
   *2026-10-02:* done for the G1–G6 cells (C1/C1w/C1g, thermal scattering
   on); see `SIM_STATUS.md` and `results/scan_v1.csv`.
5. **DREAM's sustained continuous trigger rate** is assumed to be 1 kHz
   (~1.2 kHz was seen inside a beam burst). Measure it on the cosmic bench.
6. **Extended-source acceptance.** Below ~0.3 bar the absorption length
   exceeds our ~28 mm pair-vertex blur along the beam, so window and gas pairs
   separate by vertex. But the detector was designed for a point source. R4/R5
   settle the trade.
   *2026-10-02:* at 1–3 bar the source length costs only ~1° of opening-angle
   resolution; S2 (window pairs) was not needed, since they carry ≤ 6.8 MeV.

## Next steps

1. **Ask Viviani / Marcucci / Schiavilla** for the thermal (E_n < 10 eV)
   ³He(n,e⁺e⁻) prediction for their S/P/V/A fits, and for the E0
   (C0000, ¹S₀→0⁺) matrix element. Gustavino is a co-author of both the
   paper and n_TOF X17.
2. **Contact the PF1B instrument responsible:** dΦ/dλ table, divergence,
   casemate dimensions, ambient background data, line of sight of H113,
   polarised-³He cell options via Tyrex, and how the two-thirds rule treats a
   CERN-hosted team.
3. ~~Run `GEANT_PLAN.md` R0, then R2/R3.~~ Done (2026-10-02,
   `FEASIBILITY_SIM.md`). Next simulation: a calorimeter behind the gaps
   (energy containment, ×4 signal) and a He bag in the beam path.
4. **Establish ~200 ps per-arm timing** on the plastics and design a cosmic
   veto (inefficiency ≤ 10⁻²). These are what make the measurement work.
5. **Measure DREAM's continuous rate** on the bench.
6. **Target the 2027 EBTA annual call** (PF1B, one full cycle, three years of
   preparation allowed). Use EASY/DDT for a background day before it.
