# LANSCE WNR Target 4 — X17 feasibility with time of flight

Facility record: `FACILITY.md`. Slides: `out/lansce-wnr-x17-feasibility.html` (`deck/build_deck.py`; built,
not yet published). Beam model and reach: `wnr_beam.py`.

## 0. Answer — 2026-10-21

**On the 90° flight path (4FP90L) with the cell 10 m from the tungsten target, 1.8 µs micropulses and a
time-of-flight window of 0.2–2.75 MeV, the reach is X17/IPC = 8.4×10⁻⁴ at 3σ in 50 days (big plastics):
×1.8 past ATOMKI's ⁴He value, ~16 days of beam to reach the ATOMKI strength (statistics only).** As built:
2.4×10⁻³ at 10 m, 1.6×10⁻³ at 7 m (the ATOMKI strength). The facility operates today and 90L hosts
TPC-sized fission detectors, but its beam time is scarce.

| 50 d, E* ≤ 22 MeV | big plastics | as built | days to ATOMKI (big P) |
|---|---|---|---|
| 90L, 7 m | 9.1×10⁻⁴ (throttle 0.5) | 1.6×10⁻³ | 18 |
| 90L, 8 m | 9.0×10⁻⁴ (throttle 0.63) | 1.9×10⁻³ | 18 |
| **90L, 10 m** | **8.4×10⁻⁴** | 2.4×10⁻³ | **16** |
| 90L, 12 m | 1.0×10⁻³ | 3.0×10⁻³ | 22 |
| 90L, 15 m | 1.3×10⁻³ | 3.9×10⁻³ | 37 |
| 90L, 10 m, 100 Hz (×2.5 current) | 5.5×10⁻⁴ | 1.5×10⁻³ | 6.6 |
| 90L, 8 m, 3.6 µs | 1.1×10⁻³ | 2.7×10⁻³ | 26 |
| 30R ICE-II, ~10 m | 1.0×10⁻³ | 2.8×10⁻³ | 22 |
| 60R, 15 m | 1.3×10⁻³ | 4.1×10⁻³ | 39 |
| 30L ICE House, ~20 m | 2.2×10⁻³ | 7.1×10⁻³ | 105 |
| 15L, 22 m | 2.9×10⁻³ | 9.7×10⁻³ | 182 |

With X17/IPC constant at every E\* ("all E\*", the NFS convention) the best analysis is the same soft
window for big plastics (8.4×10⁻⁴): opening the trigger gate to faster neutrons costs more DREAM live time
than their X17 adds. As built, "all E\*" reaches 2.0×10⁻³ at 10 m (gate 0.2–6 MeV). 14 days, 90L 10 m:
1.6×10⁻³ (big plastics). The survey's scaled bracket was 1.7×10⁻³ – 8.5×10⁻³ (30°, estimated spectrum,
`survey/SURVEY.md` §4.2).

**Limiting factor: statistics.** The background is the IPC itself (plus cosmics, which fall outside the
m_ee peak). Accidentals and the beam's correlated two-arm events are ×100–1000 below the IPC. Closer than
~10 m with big plastics, DREAM dead time from random two-arm triggers sets in and the beam is throttled.

## 1. Beam model — 2026-10-21

`wnr_beam.py` → `out/wnr_spectra.{csv,png}`, `out/wnr_spectra_summary.csv`.

- **Yield per angle:** Nowicki, Wender & Mocko (2017) Fig. 2, n/proton/MeV/sr at 15/30/60/90°, digitised by eye
  at 20 energies (0.1–780 MeV, ±10 %); below 0.1 MeV Y ∝ √E (assumption, only affects wrap-around and
  singles).
- **Check:** at 30°, 20 m, 1.56 µA it gives 1.23×10⁶ n/cm²/s above 1.5 MeV; LANL quotes 1.5×10⁶ for ICE
  House. ICE-II's 4.7×10⁶ places it at ~10 m. So the figure is per proton at today's current to ~20 %.
- **Time structure:** 40 macropulses/s × 625 µs (duty 2.5 %), 7×10⁸ p per micropulse every 1.8 µs:
  13 889 micropulses/s, 9.7×10¹² p/s = 1.56 µA. Options: 3.6/7.2 µs (same protons per pulse, fewer pulses);
  100 Hz (×2.5, the LANL RF upgrade).
- **At 90°, 10 m, Ø8 cm:** 3.7×10⁸ n/s through the spot (all of NFS's 3.5×10⁸, but 55 % in 0.2–2.75 MeV
  against NFS's 2 %); 3.8 % above 45 MeV (15°: 29 %).
- **Frame overlap:** the analysis bins are time windows; each is cut at the next γ flash (T + L/c). At 10 m
  the 0.2 MeV neutrons arrive at 1.62 µs, before the next flash at 1.83 µs: no loss. Neutrons slower than the
  cut belong to the next frame: their captures stay as IPC-like background in the bin they fold into, their
  X17 is dropped.

## 2. The apparatus response — 2026-10-21

No new Geant4. Every response is per neutron entering the Ø8 cm spot of the NFS geometry (30 bar × 40 cm
cell, vacuum flight tube, both hardware sets), as a function of E_n:

| E_n | source | what |
|---|---|---|
| < 8.5 MeV | N5 soft forced run (`survey/soft_sim/sel/`, log-flat 1 keV–20 MeV) | ok singles, legs, two-arm triggers, two-arm ok pairs, each with its time |
| 8.5–45 MeV | N4 NFS forced run (`ganil_nfs/sim/sel_beam/`, the survey's singles table) | ok singles; pairs with their times; legs and triggers from the N5 leg/ok ratio and NFS's trigger/pair ratio |
| > 45 MeV | the 25–45 MeV values × K_HI (= 1) | no Geant4 there; K_HI = 0–10 checked (§4) |

Prompt singles (within 100 ns of the neutron reaching the detector) move with their neutron in time; later
ones (captures, activation) are spread flat. Correlated pairs and triggers keep their own Geant4 delay
(> 20 µs: flat).

**Validation (`--check`):** on NFS's own beam the engine reproduces the published NFS reach: big plastics
3.31×10⁻³ (all E\*) / 0.030 (E\* ≤ 22) at 14 d against 3.3×10⁻³ / 0.031; as built 8.6×10⁻³ / 0.127 against
8.5×10⁻³ / 0.16. The as-built soft-window difference is NFS's 643 correlated events/day in its 1.5–2.75 MeV
bin (a few delayed MC events), which this model spreads over the bins by their delay.

## 3. Reach — 2026-10-21

`wnr_beam.py` → `out/wnr_reach.csv`, `out/wnr_components.csv`, `out/wnr_throttle.csv`, `out/wnr_scan.csv`,
`out/wnr_reach_vs_L.png`, `out/wnr_time_profile.png`, `out/wnr_throttle_fig.png`.

Per configuration everything is folded into one micropulse period; the NFS E_n bins become time windows.

- **X17, IPC:** NFS's per-bin m_ee tables (vertex DCA < 60 mm, E_sum > W/2, m_ee with W from the ToF E_n)
  × captures here / captures at NFS.
- **Accidentals:** the pairing integral ∫Σ_{a<b} ρ_a ρ_b du of the ok-singles time profile over each bin's
  window, inside a macropulse, ×2δ (δ = 5 ns), divided by the same integral for NFS's beam: × NFS's
  accidental histogram of that bin (its vertex + E_sum pass fraction).
- **Correlated:** two-arm ok pairs per neutron × NFS's pooled vertex and E_sum pass fractions (the NFS
  factorised headline), placed in the bin their arrival folds into, with that bin's NFS m_ee shape.
- **Cosmics:** the LNL L4 tables × the fraction of time each bin's window is open (window × 13 889/s).
  No veto.
- **Trigger gate:** only two-arm triggers inside the analysed windows are read out (the micropulse timing
  comes from LANSCE). **DREAM:** non-paralysable 298 µs, with the triggers bunched into the 625 µs
  macropulses: live = the renewal count per macropulse at the in-macropulse rate. **Micromegas occupancy:**
  ok singles per arm in the 1 µs before each instant, averaged over the window; exposure × exp(−2·occ).
- **Fit:** Asimov over the m_ee histogram of each bin, summed; best throttle and (for all E\*) best gate.

Baseline, 90L at 10 m, big plastics, full beam, per day after cuts (all m_ee), 0.2–2.75 MeV bins:

| E_n bin | X17 at ATOMKI | IPC | cosmics | accidentals | correlated |
|---|---|---|---|---|---|
| 0.2–0.75 MeV | 5.8 | 786 | 2 124 | 5.1 | 0.57 |
| 0.75–1.5 MeV | 8.4 | 1 166 | 635 | 5.9 | 0.17 |
| 1.5–2.75 MeV | 9.8 | 1 439 | 401 | 0.8 | 0.11 |

DREAM live 0.98 (42 random + 0.3 correlated triggers/s in the gate), Micromegas occupancy 0.04, 556 ok
singles per arm per second (time-averaged). The reach (8.4×10⁻⁴) sits on its IPC + cosmics floor (8.0×10⁻⁴).
Cosmics are as many as the IPC but 1–2 % of them fall in m_ee 14–19 MeV, against 36 % of the IPC and 97 % of
the X17: a veto leaving 10 % of them gains 1 %.

**Distance and angle** (`out/wnr_scan.csv`): the reach goes as 1/L (statistics) beyond 10 m; closer, the
random triggers from capture γ (bunched in the macropulses) cost live time and the beam is throttled, so the
optimum is ~10 m (big plastics) and ≤ 7 m (as built). At equal distance the angle matters less: 90° beats
15° by ×1.3 at 15 m. 3.6 µs spacing halves the protons (×1.2–1.4 in reach) and gains nothing below ~11 m.

## 4. Robustness — 2026-10-21

`out/wnr_khi_sensitivity.csv`, 90L 10 m, 50 d, E\* ≤ 22, big plastics (as built):

| variation | reach |
|---|---|
| baseline | 8.4×10⁻⁴ (2.4×10⁻³) |
| response above 45 MeV × 0 / × 3 / × 10 | 8.3 / 8.7 / 9.9 ×10⁻⁴ |
| background shape uncertainty 0.5 / 1 / 2 % per m_ee bin (uncorrelated) | 8.6 / 9.3 / 11.5 ×10⁻⁴ |
| cosmic veto leaving 30 % / 10 % | 8.3 / 8.3 ×10⁻⁴ (2.3 / 2.25×10⁻³) |
| 100 Hz macropulses (×2.5 current) | 5.5×10⁻⁴ (1.5×10⁻³) |

S/B ≈ 0.7 % after cuts: the IPC m_ee shape must be known to ~1 % per bin, or fitted (the fast bins, which
carry no X17 in this convention, are an IPC control sample at the same apparatus settings).

## 5. What it needs, and what is not settled

1. **Beam time on 4FP90L** (the 2026 call: "very limited", contact the instrument scientist first), room for
   the arms (~2 × 2 m) at 7–10 m, a Ø8 cm collimator and a dump **(ask)**.
2. **The micropulse timing** for the ToF trigger gate (standard at WNR).
3. **The γ flash** at every micropulse is gated off in the trigger, but it lands in the Micromegas drift
   (1 µs memory) 0.4 µs before the window opens. Its size at 90° is unknown **(ask; Geant4)**. A guess
   (E): 0.1 γ/proton/sr at 90° gives ~4 γ per micropulse through the Ø8 cm spot at 10 m, and the G5 run gives
   ≤ 6×10⁻⁵ ok singles per γ, so negligible as singles; ionisation in the drift without a leg is not in the
   occupancy model.
4. **Not simulated:** the flight-path room, collimator and dump (re-weighted from the NFS geometry: vacuum
   tube, no hall); air in front of the cell; the beam's γ; the response above 45 MeV.
5. **The spectrum** is read by eye from one figure; the measured 90° spectrum below 1 MeV would firm up the
   flux (±20 %).
6. **Current:** 1.56 µA assumed (40 Hz). Older documents quote ~4 µA; the LANL page plans ×2.5. The reach
   scales as 1/√current here.
7. **Physics:** X17/IPC for E1 capture at E\* 20.6–22 MeV against ATOMKI's p + t (`survey/SURVEY.md` §6.3).
