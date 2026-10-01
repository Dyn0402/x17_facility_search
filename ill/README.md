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

```bash
python ill/ill_rates.py --write     # all tables + cross-checks -> ill/out/*.csv
python ill/make_report.py           # -> ill/out/report.html + figures
```

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

## The answer so far

**Feasible. It is also the only way the thermal measurement becomes
statistics-rich. But it covers the s-wave half of the physics only.**

1. **Our thermal results transfer directly.** Every ILL neutron is below
   0.1 eV, the regime of n_TOF's >1 ms gate. There, both ³He channels and every
   wall capture go as 1/v. The gas absorbs every neutron, and radiative
   captures per absorption (1.03×10⁻⁸), pairs per absorption (4.8×10⁻¹¹,
   2.9×10⁻¹² above 109°) and the M1/E0 mix are all wavelength-independent.
   The only thing that changes is the **wall**: its capture probability per
   neutron grows with λ, by 2.36/0.651 = **3.6×** from n_TOF's in-gate
   spectrum to PF1B's 4.25 Å. That factor carries the Geant4 thermal contract
   (10⁹ neutrons, nose-first) across.

2. **With the as-built capsule** (configuration A), PF1B is
   **detector-limited at ~6.5×10⁸ absorbed n/s**. Micromegas pile-up and a
   1 kHz DREAM trigger bind together. **One ILL day = ~760 n_TOF thermal-gate
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
| A: capsule @ PF1B | 6.5×10⁸ | Micromegas | 760 | 1.3×10⁻² | 2×10⁻⁸ | 5 MBq |
| B: Be cell @ PF1B, design | 10¹⁰ | chosen | 1.2×10⁴ | 3.3×10⁻³ | 4×10⁻⁶ | 77 MBq |
| B: Be cell @ PF1B, ceiling | 1.1×10¹¹ | Micromegas | 1.3×10⁵ | 1.0×10⁻³ | 4×10⁻⁶ | 0.86 GBq |

(`report.html` has the full table, the figures and the reasoning.)

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
3. **The trigger-level S/B.** Pair-tags are 92 % two Comptons from one wall
   capture. Even the Be cell leaves S/B ~4×10⁻⁶ at the trigger, so offline
   rejection (two MM tracks pointing at the cell, opening angle, LS energy) must
   supply ≳10⁶. This is the **same open problem as at n_TOF**, and the ILL's
   statistics would finally let it be measured on data rather than simulation.
4. **Configuration B is an analytic scaling.** That covers window captures,
   t/X₀ for conversion, and the Al-like cascades. `GEANT_PLAN.md` R2–R5
   replace it, including cold-neutron thermal scattering in the window, which
   the current physics list lacks.
5. **DREAM's sustained continuous trigger rate** is assumed to be 1 kHz
   (~1.2 kHz was seen inside a beam burst). Measure it on the cosmic bench.
6. **Extended-source acceptance.** Below ~0.3 bar the absorption length
   exceeds our ~28 mm pair-vertex blur along the beam, so window and gas pairs
   separate by vertex. But the detector was designed for a point source. R4/R5
   settle the trade.

## Next steps

1. **Ask Viviani / Marcucci / Schiavilla** for the thermal (E_n < 10 eV)
   ³He(n,e⁺e⁻) prediction for their S/P/V/A fits, and for the E0
   (C0000, ¹S₀→0⁺) matrix element. Gustavino is a co-author of both the
   paper and n_TOF X17.
2. **Contact the PF1B instrument responsible:** dΦ/dλ table, divergence,
   casemate dimensions, ambient background data, line of sight of H113,
   polarised-³He cell options via Tyrex, and how the two-thirds rule treats a
   CERN-hosted team.
3. **Run `GEANT_PLAN.md` R0** first (cheap, and it validates the 1/v bridge),
   then R2/R3 for configuration B.
4. **Measure DREAM's continuous rate** on the bench.
5. **Target the 2027 EBTA annual call** (PF1B, one full cycle, three years of
   preparation allowed). Use EASY/DDT for a background day before it.
