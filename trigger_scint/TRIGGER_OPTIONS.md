# Fixing the trigger acceptance: options, acceptance and cost

2026-10-02. Facility-independent: the detector is the n_TOF MX17 stack (4 arms:
Micromegas → SiPM wall → trigger scintillator), and the acceptance numbers are
for X17 / IPC pairs from a ³He target at the centre. The vertex distribution is
the ILL G1 cell (1 bar, R = 40 mm, 43 mm σ along the beam). A different target
shifts the absolute numbers slightly but not the ranking.

Inputs: Geant4 runs T0/T1 (`MX17_Full_Geant`, branch `trigger_plastics`),
`sim/trig_reduce.py`, `sim/trig_accept.py`, `optics_toy.py`, `costs.py`,
`analyze.py`. Outputs: `out/options.csv`, `out/figures/`. Full outputs on EOS
are in `/eos/experiment/ntof/data/x17/ill/{T0,T1,trig}/`.

## Bottom line

1. **The n_TOF trigger accepts 2.3 % of X17 pairs. The detector could accept
   ~14–17 %.** The two 20 × 30 × 2 cm plastics per arm are the bottleneck. They
   cover 40 × 30 cm at 41 cm from the beam, while the Micromegas cone at that
   depth is ~75 × 68 cm.
2. **Four large plastics (one per arm, where the 2 cm bars sit now) fix it:
   ×6 acceptance.** With all 20 SiPM bars in the trigger, acceptance saturates
   at **14.0 % for 70 × 70 cm** and 14.4 % for 78 × 80 cm (W × L,
   transverse × along the beam). 60 × 60 cm gives 12.0 % and 50 × 50 cm 7.6 %.
   Beyond ~70 cm wide and ~70–80 cm long, nothing more is gained.
3. **Reading all 20 SiPM bars matters: ×1.4.** With the n_TOF 16-bar window,
   the same 78 × 80 plastic gives 10.3 % instead of 14.4 %.
4. **The cap is the SiPM wall, not the Micromegas.**
   - MM alone: 27.6 % (both leptons in the active area, different arms).
   - MM + all 20 SiPM bars: 16.6 %. MM + the 16 n_TOF bars: 11.8 %.
   - A big plastic with no SiPM requirement reaches 17.1–17.7 %.
   - Only ~86 % of the leptons that cross the MM active area reach a plane
     20 cm further out. Those leptons are not soft (median 7.8 MeV), so the
     loss is edge geometry and scattering in the MM readout stack. Squared for
     the pair, that is why no back scintillator gets near 27.6 %.
5. **Getting the liquid scintillators working is not worth it for acceptance.**
   - The LS alone as the trigger leg gives 1.2 %, half of today's.
   - LS OR the 2 cm plastics gives 4.3 %.
   - Each LS slab is 45 × 45 cm, ~47 cm out, behind the plastics.
   - Their n_TOF problem was pile-up/rate (67–76 % of pulses had another pulse
     in their own tail). Hardware work does not fix that.
6. **Thick plastic is the calorimetry upgrade, and 4–5 cm is enough.** For
   the ILL-type analysis (Esum > 13 MeV against the 10.8 MeV ¹⁴N capture
   endpoint), on 78 × 80 cm (X17 acceptance × P(Esum > 13 MeV)):

   | thickness | 1 cm | 2 cm | 3 cm | 4 cm | 5 cm | 6 cm | 10 cm |
   |---|---|---|---|---|---|---|---|
   | acc × P(Esum > 13 MeV) | 0.07 % | 1.9 % | 7.4 % | 11.0 % | 12.5 % | 12.7 % | 12.9 % |

   - n_TOF as built gives 1.6 %, and only by counting the LS energy.
   - A 5 cm slab is ×7.7 over as-built. 4 cm gets 88 % of that.
   - 10 cm buys only 3 % more for ~€90k.
7. **Acceptance vs cost (four slabs; trigger hardware only, budgetary):**

   | option | X17 acc | acc × P(E > 13) | cost [k€] (range) |
   |---|---|---|---|
   | n_TOF as built | 2.3 % | 1.6 % | 0 |
   | LS working, OR plastics | 4.3 % | 2.2 % | 6 (2–12) |
   | 4 × 60 × 60 × 2 cm PVT, 2 × 3" | 12.0 % | 1.2 % | 67 (39–103) |
   | **4 × 70 × 70 × 2 cm PVT, 2 × 3"** | **14.0 %** | 1.7 % | **79 (46–121)** |
   | 4 × 78 × 80 × 2 cm PVT, 2 × 2" | 14.4 % | 1.9 % | 77 (44–122) |
   | **4 × 78 × 80 × 4 cm PS, 2 × 3"** | **14.4 %** | **11.0 %** | **87 (50–132)** |
   | 4 × 78 × 80 × 5 cm PS, 2 × 3" | 14.5 % | 12.5 % | 93 (54–142) |
   | 4 × 70 × 70 × 5 cm PVT, 2 × 3" | 14.1 % | 12.1 % | 120 (69–190) |
   | 4 × 78 × 80 × 5 cm PVT, 2 × 3" | 14.5 % | 12.5 % | 136 (78–217) |
   | 4 × 78 × 80 × 10 cm PVT, 2 × 5" | 14.6 % | 12.9 % | 230 (136–371) |

   On top of any option there is a **common block for the SiPM walls**:
   - instrumenting the 4 dark bars per wall and un-ganging the preamps:
     ~€10k (5–18);
   - a DAQ for 160 channels: ~€18–22k with FERS-5200 or PETsys, ~€65–75k
     with waveform digitizers (§5).
   - The DAQ is not optional elsewhere: n_TOF read the walls on the facility's
     own digitizers.
8. **Recommendation.**
   - If the experiment needs a calorimetric Esum cut (the ILL, any thermal
     ³He(n,γ) run): **4 cm or 5 cm thick slabs, ~75 × 75 cm, each read by a
     3" PMT at both ends.** Polystyrene-based scintillator brings this to
     ~€90k; cast PVT costs ~€120–140k.
   - If only acceptance matters (MeV-range runs where the Esum cut is not the
     discriminant): **70 × 70 × 2 cm, ~€80k.**
   - In both cases read all 20 SiPM bars.
   - The PMT choice does not change the acceptance. It sets the energy and
     timing resolution, and at this size those still meet the ILL ~200 ps
     requirement (§4).

## 1. What was simulated

| run | geometry | events |
|---|---|---|
| T0 | as built: MM, SiPM wall (all 20 bars present), 2 × 20 × 30 × 2 cm plastics, LS vessels | 1M X17 + 1M IPC M1 |
| T1 | MM, SiPM wall (20 bars), **one 78 × 120 × 10 cm PVT slab per arm** at the plastics' front face, no LS | 1M X17 + 1M IPC M1 |

- **Why one oversized slab.** T1 cuts every smaller plastic out of the same
  events. Per lepton, the energy deposited inside a centred sub-slab
  (|u| < W/2, |v| < L/2, depth < T) is kept on a W × L × T grid
  (`trig_reduce.py`). What the cut-out misses is only backscatter from
  material that would not exist.
  - 78 cm is the widest that fits: the G4 overlap check passes with all four
    slabs at the surveyed arm positions. The real frame needs checking, but
    70 cm gives the same acceptance with margin.
- **Selection per lepton arm:**
  - first drift-gas hit inside the measured MM active area (39.9 × 36.0 cm);
  - SiPM edep over the read bars > 0.5 MIP;
  - trigger scintillator > 1.67 MeV (0.5 MIP of 2 cm PVT, the ILL "strict"
    leg threshold);
  - both leptons, in different arms.
- **Esum** = SiPM + plastic (+ LS in T0), smeared by 10 %/√E ⊕ 5 % per arm,
  as in `ill/FEASIBILITY_SIM.md`.
- **Cross-check against the ILL campaign (G1):** MM + 16 bars is 11.8 % here,
  12 % there. MM gap acceptance is 27.6 % here after the active-area cut,
  32 % there without it.

IPC M1 acceptances scale similarly: 0.32 % as built, 2.14 % for 78 × 80 × 2.
They are ~7× below X17 because M1 pairs are mostly at small opening angles.

## 2. How big the plastics need to be (`acc_vs_width`, `acc_vs_length`)

X17 acceptance [%], T = 2 cm, MM + 20 SiPM bars + plastic:

| W \ L [cm] | 30 | 40 | 50 | 60 | 70 | 80 | 100 | 120 |
|---|---|---|---|---|---|---|---|---|
| 30 | 1.3 | 2.0 | 2.8 | 3.5 | 3.7 | 3.8 | 3.8 | 3.8 |
| 40 | 2.3 | 3.7 | 5.1 | 6.3 | 6.8 | 6.8 | 6.9 | 6.9 |
| 50 | 3.5 | 5.5 | 7.6 | 9.4 | 10.1 | 10.2 | 10.2 | 10.3 |
| 60 | 4.4 | 7.1 | 9.7 | 12.0 | 12.9 | 13.0 | 13.1 | 13.1 |
| 70 | 4.8 | 7.7 | 10.6 | 13.0 | 14.0 | 14.2 | 14.2 | 14.3 |
| 78 | 4.9 | 7.8 | 10.7 | 13.2 | 14.2 | 14.4 | 14.4 | 14.4 |

- The current plastics (40.3 × 30) correspond to ~2.3 %.
- **Length along the beam matters as much as width.** The as-built 30 cm is
  the single worst dimension.
- The plateau sits where the plastic covers the SiPM wall's cone: 50 × 50 cm
  at 33 cm projects to ~64 × 64 cm at the plastic.
- **Without the SiPM requirement** (plastic-only trigger), 78 × 80 gives
  17.1 % and 78 × 120 gives 17.7 %. That is the true ceiling for a back
  scintillator. The SiPM coincidence costs ~16 % of it, and in exchange
  provides position and timing.

## 3. Thick plastics as a calorimeter (`calorimetry`)

- **Containment.** Leptons reaching the slab carry median ~10 MeV. In PVT,
  2 cm holds ~95 % of the deposit of a 4–6 MeV lepton but only ~42 % of a
  14–17 MeV one. 4 cm holds ~79 % of that, 5 cm ~91 %, 6 cm ~97 %.
- **The deposit is not the kinetic energy.** Each lepton loses a few MeV in
  the MM, air and SiPM wall before reaching the slab, and some brem escapes.
  That is why 10 cm is still not "full calorimetry". 5 cm is ~97 % of the
  10 cm result for the Esum > 13 MeV efficiency.
- **Availability.**
  - Cast PVT (EJ-200 / BC-408 class) is made in sheets and blocks well beyond
    5 cm. Polystyrene-based (cast/extruded, e.g. Nuvia, Epic PS) is ~2.5×
    cheaper per volume, with ~70 % of the light. At these photoelectron
    counts that is acceptable (§4).
  - **Confirm the maximum single-piece width at 4–5 cm with the vendor.**
    The fallback is two 35–39 × 75 cm bars side by side, each with a PMT at
    both ends (+2 PMTs per arm, about +€50k in total for 3" tubes, guides and
    channels). Smaller bars give
    better light collection and timing.
  - Weight: 78 × 80 × 5 cm is 32 kg per arm, so the support frame needs
    rework.
- **Expected effect at the ILL.** The X17 rate passing the cut rises ×6.6
  over 2 cm big slabs and ×7.7 over as-built, at fixed beam rate. In the
  IPC/accidental-limited (200 ps + μ-veto) scenario, the 3σ reach would
  improve by up to √(gain) ≈ 2.5–2.8×, from 8.4 × 10⁻³ to ~3 × 10⁻³ per
  cycle. **Not yet computed.** Cosmics and accidentals also see the larger
  plastic, so this needs `sim_feasibility.py` rerun with T1-geometry C1/K1
  tables.

## 4. Does performance depend on size or PMT? (`optics`, `optics_toy.py`)

- **Acceptance:** no. It depends only on geometry and threshold.
- **Energy and timing:** yes, both. A photon ray-trace (TIR, Al-foil wrapping,
  fishtail guides with étendue loss, PMT QE/TTS) gives, per slab, light yield
  and the position-corrected time resolution at 5 MeV:

| slab | readout | pe/MeV (toy) | non-uniformity | σt @ 5 MeV |
|---|---|---|---|---|
| 40 × 30 × 2 (as built, for scale) | 2 × 2" | 198 | 2 % | 58 ps |
| 70 × 70 × 2 | 2 × 2" | 91 | 5 % | 101 ps |
| 70 × 70 × 2 | 2 × 3" | 198 | 5 % | 73 ps |
| 78 × 80 × 2 | 1 × 2" | 53 | 15 % | 151 ps |
| 78 × 80 × 2 | 2 × 3" | 168 | 6 % | 84 ps |
| 78 × 80 × 5 | 2 × 2" | 35 | 4 % | 172 ps |
| 78 × 80 × 5 | 2 × 3" | 77 | 4 % | 124 ps |
| 78 × 80 × 5 | 2 × 5" | 181 | 4 % | 93 ps |
| 78 × 80 × 5 | 4 × 3" on the back face | 206 | 53 % | 132 ps |

- **Edge readout through fishtails.** Light scales with the ratio of PMT area
  to end-face area. A 2 cm slab is fine with 3" tubes. A 5 cm slab has 2.5×
  the end face, so it wants 3" at minimum, and 5" for the energy resolution.
  - 78 × 80 × 5 cm with 2 × 3": ~77 pe/MeV in the toy, which is optimistic
    by ~1.5–2×. That is roughly 15 %/√E in reality. Thick-slab deposits are
    ~10 MeV per lepton, so ~5 % at the deposit, comparable to the 10 %/√E ⊕
    5 % the ILL model assumed.
- **Read both ends.**
  - One end gives a 15 % light non-uniformity and a 1.5–1.8 ns time offset
    across the slab.
  - Both MM-correctable, but two ends make the mean time and the summed
    light nearly position-independent (4–6 %), for one extra PMT.
- **Avoid back-face PMTs** on thick slabs: 40–60 % non-uniformity.
- **Timing stays inside the ~200 ps ILL requirement** for every two-ended
  option, after the MM-position correction. The toy is optimistic: guide
  dispersion is crude and there is no electronics walk. Treat the numbers as
  a ranking: bigger is worse, bigger PMTs are better.
- **Before buying,** measure one prototype slab on the cosmic bench, with
  the M3 telescope giving position.

## 5. DAQ for reading every channel

At n_TOF:
- **Walls:** each wall recorded 8 channels, 16 of 20 bars ganged in groups of
  4, each group summed top and bottom. The **facility's** ADQ14 digitizers
  (1 GS/s) recorded them.
- **Plastics and LS:** 2 plastic PMTs and 1 LS PMT per arm.
- **Trigger:** formed in an N1081B plus 428F fan-in.
- **Elsewhere,** none of the digitizers come with us.

Full readout means 4 walls × 20 bars × 2 ends = **160 SiPM channels**, plus
8 PMT channels.

| option | channels | timing | rate | cost [k€] |
|---|---|---|---|---|
| ganged sums as at n_TOF, 1 × V1742 (DRS4) | 32 | ~50 ps-class | ~1 kHz (DRS4 dead time) | 14 (10–18) |
| **FERS-5200 A5202/A5204 × 3 + DT5215** | 192 | ToA 0.5 ns LSB (Citiroc) / picoTDC (A5204) | ≫ kHz | **18 (12–25)** |
| PETsys TOFPET2 system | 256 | ~30 ps binning, built for SiPM TOF | ≫ kHz | 22 (15–32) |
| 5 × V1742 + VME crate | 160 | best (full waveform) | ~1 kHz | 75 (55–90) |
| 3 × VX2745 (125 MS/s) + crate | 192 | marginal for 200 ps | high | 65 (50–80) |
| big-plastic PMTs: 16-ch 500 MS/s–1 GS/s digitizer | 8 | waveform | — | in each option (0.8/ch) |

- **Recommendation:** FERS-5200 (or PETsys) for the 160 bar-ends, with bias
  supply and per-channel charge and time. Add one fast waveform digitizer for
  the big-plastic PMTs and the analog trigger sums. Keep the N1081B logic.
  ~€30–40k including the PMT digitizer.
- Waveform digitizers on every SiPM channel cost 3–4× more and add little
  once the trigger plastics carry the precise timing.
- Choose the SiPM front end against the walls' ~0.6 MeV MIP signal (~31 mV
  per end at n_TOF gains). Confirm the A5202/A5204 dynamic range on one wall
  before buying three.

## 6. Cost model (`costs.py`)

Budgetary EUR, 2026, no labour or VAT. The vendors quote on request, so these
are ranges.
- **Scintillator:**
  - cast PVT 0.6 €/cm³ (0.35–1.0), polystyrene 0.25 €/cm³ (0.15–0.4);
  - anchored on a $369 polished 30 × 15 × 0.5 cm EJ-200-equivalent piece and
    $74–131 rough-cut 25 × 25 × 0.6 cm EJ-200 sheets.
- **PMT + divider:** 2" fast €2.2k, 3" €3.3k, 5" €4.6k.
  - The 2013 budgetary R9779 price was ~$1k at quantity 180.
- **Fishtail guides:** €0.8–1.5k each.
- **Wrapping and mechanics:** €1.5–5k per slab.
- **HV and digitizer:** €1.4k per PMT channel.
- **The scintillator dominates** the 4–5 cm PVT options (~60 %), which is why
  polystyrene is the lever. For 2 cm slabs, PMTs and guides are about half.
- **Get two quotes** (Eljen/Luxium for PVT, Nuvia or Epic for PS) on
  4 × 78 × 80 × 4 and × 5 cm before deciding. The thickness choice is a
  ~€30–50k question.

## 7. Caveats

- One target geometry (G1 cell). A capsule target, or the MeV-range n_TOF
  kinematics, change absolute acceptances by tens of percent but not the
  ranking.
- The trigger-leg threshold is fixed at 1.67 MeV for every scintillator.
  Background trigger rates (Compton γ, neutron captures in H-rich plastic,
  cosmics ∝ area) were not simulated for the big slabs.
  - Cosmic singles per 78 × 80 cm slab are ~50–100 Hz, depending on its
    orientation: fine for a two-arm trigger.
  - The neutron-induced rate at a reactor needs the T1 geometry in C1.
- The optics toy is relative. One prototype measurement anchors it.
- Mechanical fit of 78 cm slabs is checked only in Geant4. 70 cm loses
  < 3 % relative to 78 cm.
