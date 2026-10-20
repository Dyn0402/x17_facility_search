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

## 8. Refresh (2026-10-20): building the plates ourselves, γ sensitivity, splitting, light uniformity

Prompted by Pierfrancesco's comments on the budget page (2026-10-16) and the discussion with Dylan on
2026-10-19. New code: `costs.py` (DIY route), `sim/trig_threshold.py` (threshold and seam scan on the T1
Geant4 tables), `gamma_toy.py` (Compton toy, an analytic stand-in), `optics_toy.py --refresh`. The ILL
background runs P5L/P5B (5 cm with a ⁶LiF or B₄C wrap), which finished on 2026-10-02, are now in
`sim/bkg/` and the `bkg_*` figures.

### 8.1 Bottom line

1. **Build the plates in-house.** Buy raw cast plates, polish the edges, wrap them, glue on bought custom
   fishtail guides, and reuse the 8 borrowed PMTs. Four 78 × 80 × 5 cm plates cost
   **~€30k (14–68k)** this way, against €82k (54–142k) for vendor-finished polystyrene with new 3" PMTs.
   HV and digitizer are not included in either.
   - Pierfrancesco's ~€2k per plate (€8k for four, Scionix) is the low end. It is consistent with
     cast scintillator at ~$40/kg in 2001 (≈ €65/kg today).
   - The budget page's Upgrade scenario drops from €286k to **€234k**.
2. **Thickness does not break the light collection.** With a PMT at both ends, the response (PVT) stays
   uniform to 4–5 % across the face and ~1.5–2 % in depth, from 2 to 6 cm. What thickness costs is light
   per MeV: the same PMT covers a larger end face, so pe/MeV ∝ ~1/T. Polystyrene's shorter attenuation
   length (~1 m) is the real uniformity risk: ~10 % across a 78 × 80 plate (12–18 % with edges we polish
   ourselves), and a third of the light lost. One polystyrene plate on the borrowed 2" tubes is marginal for
   timing (~240 ps in the toy); a split, 3" tubes or PVT each fix it (§8.4).
3. **γ sensitivity is real, but thickness is not the main lever.**
   - At a fixed threshold, a 5 cm plate sees **×2.4–2.8** the γ singles of a 2 cm plate.
   - The threshold cannot scale with thickness. X17 leptons stop in a thick plate: even a 10 cm
     slab collects a median 7.6 MeV per lepton (middle half 4.7–10.8 MeV; the T1 tables). At 5 cm, raising the leg threshold from 1.67 to 2.5 MeV costs **6 %** of
     the E_sum > 13 MeV signal; 3 MeV costs 15 %, and 4 MeV 35 %.
   - **2.5 MeV makes the plate blind to H-capture (2.22 MeV) and natural (≤ 2.61 MeV) γ.** This
     includes the ~2×10⁷ H(n,γ)/s a bare 5 cm plate makes at the ILL.
   - Only γ above ~3 MeV remain: capture lines (¹⁴N 10.8, Fe/Al 7.6–7.7 MeV), ³He(n,γ), ⁸Be.
4. **At the ILL, Geant4 says the shielded 5 cm plate wins, ×2 in reach over as built.** Timing
   scenario, best menu, E_sum > 13 MeV:

   | geometry | air, G = 0 | air, G = 10 ns | He tube (air × 0.1), G = 0 | He tube, G = 10 ns |
   |---|---|---|---|---|
   | n_TOF as built | 8.4e-3 | 1.12e-2 | 7.3e-3 | 9.0e-3 |
   | 70 × 70 × 2 (P2) | 1.59e-2 | 2.17e-2 | — | — |
   | 75 × 75 × 5 + 2 mm ⁶LiF (P5L) | 7.4e-3 | 1.03e-2 | 3.9e-3 | 5.5e-3 |
   | **75 × 75 × 5 + 2 mm B₄C (P5B)** | **4.1e-3** | 5.5e-3 | **3.3e-3** | 4.0e-3 |

   - Slab singles per arm above 1.67 MeV: 0.23 MHz as built, 0.33 MHz with P5L/P5B.
   - The bare 5 cm plate (P5) was never analysed: its C1w contract is missing (§8.6).
5. **Splitting each plate in two helps, and costs ~€11k.**
   - Each channel sees half the singles.
   - The in-gate pile-up window G is effectively halved. P5B at G = 10 ns then moves to about the
     G = 5 ns value, roughly 4.8e-3 instead of 5.5e-3.
   - Matching a SiPM bar to its plastic bar halves the random legs.
   - With the same PMTs, each bar gets ×2 the light per MeV, because the same tube covers twice the
     fraction of a smaller end face. Timing improves from ~240 to ~160 ps (§8.4).
   - Cost: 3.9 % of legs land within 1 cm of the seam. The arm's E_sum is the sum of both bars, so only
     a per-bar trigger threshold would care. A split costs 8 more PMTs, 4 more guides and 4 more
     housings.
6. **Recommendation, unchanged in shape:**
   - 75–78 × 80 cm, 4–5 cm thick, a PMT at both ends, built in-house;
   - PVT rather than polystyrene if the quote difference is small (uniformity, §8.4);
   - leg threshold ~2.5 MeV;
   - a B₄C or ⁶LiF wrap wherever there are thermal neutrons;
   - **decide the split in two per facility, after the γ follow-up (§8.6).**

### 8.2 Cost: raw plates, in-house finishing (`costs.py`, `arms_diy`)

| item (per piece) | low | central | high | basis |
|---|---|---|---|---|
| raw cast plate, €/cm³ | 0.064 | 0.13 | 0.30 | Pierfrancesco/Scionix; cast ~$40/kg (NIM A 466, 482); CERN 2025, 80 × 80 × 2 EJ-200 at 6k CHF (high) |
| edge machining/polish | 0 | 300 | 1000 | CERN/INFN workshop; labour in kind |
| wrapping, €/m² | 60 | 150 | 300 | ESR/Tyvek or Al + black film |
| cement, grease | 50 | 100 | 200 | EJ-500 $81/300 g |
| custom fishtail guide (each) | 300–500 | 600–1000 | 1200–2000 | Eljen/Shalom make them to order (no list price) |
| light-tight housing | 300 | 800 | 2000 | the arm frames are a separate budget item |
| extra PMT (economy 2") | 300 | 600 | 1200 | Pierfrancesco's LS rebuild: 16 PMTs + cases ~€7k |

| four arms, no HV/digitizer | central [k€] | range |
|---|---|---|
| 1 × 78 × 80 × 2 cm, 8 borrowed PMTs | 20 | 9–45 |
| 1 × 78 × 80 × 4 cm, 8 borrowed PMTs | 27 | 12–60 |
| **1 × 78 × 80 × 5 cm, 8 borrowed PMTs** | **30** | 14–68 |
| 2 × 39 × 80 × 5 cm, 16 PMTs (8 bought) | 41 | 18–94 |
| 3 × 26 × 80 × 5 cm, 24 PMTs (16 bought) | 56 | 25–126 |
| vendor-finished PS 78 × 80 × 5, 8 new 3" (old plan) | 82 | 54–142 |

- The raw plate is ~55 % of a DIY plate (central). The guides are next, ~€2k per plate.
- **Before trusting this, ask Pierfrancesco** whether his ~€2k is for 78 × 80 × **5** cm, and in which
  material (PVT/EJ-200 class or polystyrene). Then get the Scionix quote in writing.
- Scionix has built 5 cm, 0.5–1 m² EJ-200 panels before (the Felsenkeller muon veto,
  arXiv:2301.03905). With one PMT, >90 % of the area responded within 0.7–1.2× of the centre.
- What doing it ourselves costs instead: an edge-finishing setup (diamond fly-cut, or sanding to
  600 grit + polish) and a gluing jig for the guides. The edges matter most where the guide is glued.
  Raw cast plates come with cast (optical) faces, so only the edges need work.

### 8.3 Signal: how high can the leg threshold go (`sim/trig_threshold.py`, `sim/accept/thr_*.csv`)

X17, 78 × 80, MM + 20 SiPM bars, both legs; acc / acc × P(E_sum > 13 MeV), %:

| leg threshold [MeV] | 1.0 | 1.67 | 2.5 | 3.0 | 4.0 | 5.0 |
|---|---|---|---|---|---|---|
| 2 cm | 15.0 / 1.9 | 14.4 / 1.9 | 13.0 / 1.8 | 11.4 / 1.8 | 5.3 / 1.5 | 1.2 / 0.8 |
| 4 cm | 15.1 / 11.2 | 14.5 / 11.0 | 13.1 / 10.6 | 11.6 / 9.8 | 8.5 / 7.9 | 5.9 / 5.7 |
| 5 cm | 15.1 / 12.7 | 14.5 / 12.5 | 13.2 / 11.7 | 11.6 / 10.6 | 8.6 / 8.1 | 5.9 / 5.8 |

The deposit is the lepton's residual energy, not 2 MeV/cm × T. After the MM and the wall, an accepted lepton
leaves a median 7.6 MeV even in 10 cm of plastic (middle half 4.7–10.8 MeV), and most of them stop in it.

### 8.4 Light: thickness, material, edges, splitting (`optics_toy.py --refresh`, `out/optics_refresh.csv`)

Toy ray-trace (§4), now with emission at three depths (0.1, 0.5, 0.9 T). A PMT at both ends. "xy" is
the rms across the face; "depth" is the rms between the three depths. Absolute pe/MeV are
optimistic by ~1.5–2×.

Single plate, 78 × 80 cm, 2 × 3" (2 × 2" in brackets):

| T | PVT pe/MeV | PVT xy / depth | PS pe/MeV | PS xy | PS, DIY edges, pe/MeV | PS DIY xy |
|---|---|---|---|---|---|---|
| 2 cm | 169 (77) | 5.0 % / 1.7 % | 113 (51) | 11.8 % | 92 (42) | 18 % |
| 3 cm | 121 (55) | 4.5 % / 1.7 % | 80 (36) | 10.5 % | 69 (31) | 15 % |
| 4 cm | 94 (43) | 4.5 % / 1.8 % | 62 (28) | 10.4 % | 55 (25) | 13 % |
| 5 cm | 77 (35) | 4.3 % / 1.5 % | 51 (23) | 9.7 % | 46 (21) | 12 % |
| 6 cm | 66 (30) | 3.9 % / 1.7 % | 43 (20) | 9.1 % | 39 (18) | 12 % |

The same 5 cm plate split into N bars of (78/N) × 80, DIY edges, per bar, 2 × 2" [2 × 3"]:

| N | PVT pe/MeV | PVT xy | PVT σt(5 MeV) | PS pe/MeV | PS xy | PS σt(5 MeV) |
|---|---|---|---|---|---|---|
| 1 (PS DIY, from above) | — | — | — | 21 [46] | 12 % | 238 [170] ps |
| 2 | 61 [134] | 7 % | 122 [87] ps | 41 [90] | 13 % | 158 [114] ps |
| 3 | 90 [197] | 7 % | 100 [73] ps | 60 [132] | 14 % | 126 [92] ps |
| 4 | 117 [256] | 7.5 % | 86 [64] ps | 79 [174] | 14 % | 110 [81] ps |

- **Thickness does not degrade uniformity.** Across the face it even improves slightly; in depth it stays at
  ~1.5–2 %, from 2 to 6 cm. A fishtail at both ends mixes the light from every depth. Light per MeV falls ~1/T,
  because the PMT covers a smaller fraction of a thicker end face. The lepton deposit is larger in a thick
  plate (§8.3), so pe per lepton falls more slowly than 1/T.
- **Width is not a problem either:** 78 cm with both ends read is 4–5 % (PVT). Light is lost along the
  80 cm length (attenuation, reflections), not across the width.
- **The material is.** Polystyrene with a ~1 m technical attenuation length gives ~10 % across the plate
  (min/max 0.75) and 2/3 of the PVT light. Edges finished in-house (TIR 0.95 per bounce instead of 0.98) cost
  another ~10 % of light and push it to 12–18 %. Most of that non-uniformity is a smooth function of the hit
  position, which the Micromegas measure. It can be mapped with cosmics and corrected, but it eats into the
  resolution.
- **Splitting doubles the light per bar** (PS, DIY, like for like: 21 → 41 pe/MeV with 2"). Each bar's end face
  is half the size for the same tube. Timing improves from ~240 to ~160 ps. Uniformity stays set by the
  material.
- **The weakest combination is one polystyrene plate per arm read by the borrowed 2" tubes.** That gives
  ~21 pe/MeV in the toy, i.e. ~10–14 pe/MeV real: ~100 pe for a median 7.6 MeV lepton, ~10 % stochastic,
  ~240 ps. It works for the trigger and the E_sum > 13 MeV cut, but is marginal for timing at the ILL. A split,
  3" tubes or PVT each fix it.

### 8.5 γ sensitivity (`gamma_toy.py`, `out/gamma_toy.csv`, `out/gamma_rates.csv`)

A toy, until Geant4 does the room. Photons of one energy enter a 75 × 75 cm PVT plate. The model has
Klein–Nishina Compton, pair production and straight-line electrons. A diffuse field ("room") is
normalised per µSv/h of that line (ICRP 74 h*(10)).

Singles per plate [kHz] per µSv/h of a diffuse field of one line:

| E_γ [MeV] | 2 cm, > 1.67 | 5 cm, > 1.67 | 5 cm, > 2.5 | 5 cm, > 3 |
|---|---|---|---|---|
| 1.46 (⁴⁰K) | 0 | 0 | 0 | 0 |
| 2.22 (H capture) | 4.0 | 11.0 | 0 | 0 |
| 2.61 (²⁰⁸Tl) | 4.6 | 11.8 | 0.6 | 0 |
| 4.44 | 3.8 | 9.4 | 7.8 | 6.8 |
| 6.13 | 3.0 | 7.4 | 6.6 | 6.1 |
| 7.6 (Fe/Al capture) | 2.6 | 6.2 | 5.6 | 5.3 |
| 10.8 (¹⁴N capture) | 2.0 | 4.8 | 4.5 | 4.3 |
| 17.6 (⁸Be) | 1.4 | 3.4 | 3.3 | 3.2 |

- Per γ, a 5 cm plate fires ×2.4–2.8 as often as a 2 cm one, and a 4 cm plate ×2.0–2.2.
- The deposits in the toy are not smeared by the energy resolution. With ~10 %/√E, a few % of
  2.6 MeV γ still pass a 2.5 MeV threshold. Use 2.7–3 MeV where ²⁰⁸Tl dominates.
- **Splitting into N bars divides each channel's rate, and the pile-up into a lepton's bar, by N.**
  It does not change the total per arm. That matters for trigger rates if the arm's analog sum forms
  the leg; then match the SiPM bar to the plastic bar.

### 8.6 Follow-up: γ (and neutron) sensitivity per facility, before choosing thickness and split

| facility | what is known | what to do |
|---|---|---|
| **ILL PF1B** | Geant4 TB: P5L/P5B ×2 better than as built; 0.33 MHz/arm > 1.67 MeV, mostly air ¹⁴N(n,γ). The bare P5 slab has ~2×10⁷ H(n,γ)/s. | Produce `C1w_P5` (the pipeline never made it) and run `bkg_reach.py` for P5. Rerun P5B with the leg at 2.5 MeV. Ask the ILL for the casemate γ dose rate: 1 µSv/h of hard γ is ~5–10 kHz per plate. |
| **LNL** | Geant4 L3: beam γ negligible with big plastics (0.39 % legs per ⁸Be γ at ~10⁴ γ/s); two-arm triggers 22/s, cosmic-dominated. ⁷Li(p,p′) 0.478: no legs. | Low risk. Use Li₂O, not LiF (the ¹⁹F lines). Run at 2.5 MeV. Measure the hall background on the bench plate. |
| **GANIL NFS** | Geant4 N3: singles 156 kHz/arm with 75 × 75 × 5 vs 32 kHz as built (×5). Mostly fast neutrons: n–p recoils ∝ T, plus capture γ. | Rerun N3/N4 with 4 cm, the 2-bar split and a 2.5 MeV leg, and add the singles to the accidentals (FEASIBILITY_SIM §3.3). |
| **survey POTENTIAL** (FRM II MEDAPP, Birmingham) | Not simulated. Birmingham's target makes 1.9×10¹⁰ γ/s at 15–18 MeV; MEDAPP carries fission γ in the beam. | Include the big plate (1 vs 2 bars) in the planned soft-beam Geant4 run (`survey/SURVEY.md`). |
| any | The hall γ field is not simulated anywhere. | A 1 m² bench plate with a 2.5 MeV threshold at each site, or a dose-rate number from the facility (ask). |

- The obvious Geant4 job: `--big-plastic` with a two-bar option. MX17_Full_Geant `trigger_plastics`
  cuts plates offline from one oversized slab. A seam needs either a real two-volume plate, or
  per-bar scoring of the hits, which `trig_reduce.py` could do with `ent_uv` and the step positions.
- **Not done here:** neutron sensitivity of the plastic itself (n–p recoils, quenched). It matters only
  at the fast-neutron facilities, and Geant4 already includes it there.
