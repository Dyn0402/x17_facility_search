# Reading the SiPM walls channel by channel: a DAQ and trigger plan

**2026-10-30.** Companion to `PLAN.md` (architecture D, §5.4, worked out). Numbers: `sipm_readout.py` →
`out/sipm_channels.csv`, `out/sipm_costs.csv`. What the extra granularity buys in physics is a separate study:
`../sipm_wall/README.md`.

The question (Dylan, 30 Oct): read each bar of the SiPM wall individually, top and bottom, and maybe each of the
2 SiPMs per bar end, instead of the n_TOF groups. What DAQ and trigger does that take?

Facts not found publicly are marked **(ask)**; prices without a public source are **guess**.

---

## 0. Bottom line

1. **Today (n_TOF, and PLAN.md B):** each wall is 8 channels: 16 of its 20 bars, ganged in 4 groups of 4, each
   group read at the top and the bottom. 32 channels in all. The ganging is done on the wall's preamp boards.
2. **Per bar end is 160 channels (4 walls × 20 bars × 2 ends); per SiPM is 320.** At these counts the cheap,
   natural readout is a SiPM front-end ASIC board, not a digitizer: **CAEN FERS-5200 A5204** (64 ch, Weeroc
   Radioroc 2 + CERN picoTDC, SiPM bias on board, 3.125 ps TDC LSB).
   - **160 ch: one A5204 per wall** (40 of 64 inputs). **320 ch: two per wall.** A DT5215 concentrator reads them
     all over optical TDlink.
   - **Mount each board on its wall** and connect the SiPMs through short passive carrier boards. No preamps, no
     160–320 LEMO cables: each wall then has one fibre, one low-voltage cable, a trigger out and a trigger in.
3. **The trigger: the wall OR comes from the FERS board.** The A5204 logic has a *paired-channel AND*. With a bar's
   top and bottom on a channel pair, the board trigger out is "any bar with both ends fired". n_TOF showed that the
   top-bottom coincidence is 99.8 % pure MIPs (`nTof_x17/mx_july_beam_qa/sipm_sum_threshold/SUMMARY.md`), so the
   threshold can go low without dark-count triggers. This T-OUT replaces M1 and the 4 wall-sum FIFOs. M3 (wall
   AND plastic), M4 (PAIR/SINGLE/÷P/veto) and the rest of the N1081B logic are unchanged.
4. **The SiPM inputs cannot be split**, so this trigger path is forced (PLAN.md §5.4). Its unknowns are the T-OUT
   latency and jitter, and whether the logic can AND the right channels (**ask CAEN, bench test S2**). The
   fallback that keeps today's proven analog trigger is new per-channel **preamp boards with an on-board group-sum
   output** (option P160). It costs 3× more because every channel then needs a digitizer.
5. **Cost** (`out/sipm_costs.csv`, wall readout plus the trigger parts it replaces, central and range):

   | option | channels | central | range | vs ganged |
   |---|---|---|---|---|
   | G: ganged as n_TOF (V1742 + 4 sum FIFOs + M1) | 32 | €26 k | 19–35 k | — |
   | **F160: per bar end, 4 × A5204 on the walls** | 160 | **€37 k** | 24–55 k | **+€10 k** |
   | F160c: as F160 with the A5202 (Citiroc, coarser time) | 160 | €29 k | 20–43 k | +€2 k |
   | **F320: per SiPM, 8 × A5204** | 320 | **€64 k** | 42–93 k | +€37 k |
   | P160: per-channel preamp respin → 5 × V1742 (waveforms) | 160 | €101 k | 71–133 k | +€75 k |
   | P320: per-channel preamp respin → 5 × VX2745 | 320 | €134 k | 97–176 k | +€108 k |
   | T160: PETsys TOFPET2 256 ch | 160 | €30 k | 19–46 k | +€3 k, but no hardware trigger out (§3.3) |

   The F options include SiPMs for the 4 dark bars per wall. Every FERS price is a guess: CAEN quotes on request.
6. **What it buys (`../sipm_wall/README.md`, Geant4 on the LNL samples):**
   - **No change in LNL reach, once the plastics' PMT time makes the TOF.** Per-bar timing would cut as-built
     running time ×0.65, but the plastic time at the n_TOF-measured 0.14–0.29 ns does the same with the walls ganged.
   - The MM road shrinks from 25 % to 9 % of the chamber. That matters at high-rate neutron sites (Birmingham:
     stray neutron-recoil clusters in the road go 14 % → 5 %).
   - Also: a cleaner trigger (per-bar top·bottom), all 20 bars lit (×1.4 trigger acceptance with big plastics), and
     an independent second timer.
   - **Per SiPM (320) buys nothing measurable over per bar end.**
7. **Recommendation:**
   - **If the walls are reworked at all (to light the 4 dark bars, or because the preamp boards must be rebuilt),
     go to F160:** ~€10 k over the ganged path for a simpler trigger, per-bar calibration and the road.
   - **Don't do it for the LNL reach alone,** and don't go to 320. Wire the carriers with a pad per SiPM anyway: it
     costs nothing and keeps 320 open.
   - **Gate it on bench tests S1–S3** (one wall, an A5204 demo unit, cosmics, the M3 telescope), and on what is
     inside the walls (§1).

---

## 1. What is in the walls today, and what we have to find out

| | known | source |
|---|---|---|
| bars | 20 per wall, 2.5 cm wide × 50 cm long (along the beam) × 3 mm active, in a 3.5 cm deep container | MX17_Full_Geant `SimConfig.hh` |
| read at n_TOF | 16 bars (window shifted 1 bar toward the MM), ganged in 4 groups of 4, top and bottom: 8 ch per wall | same; `nTof_x17/mx_july_beam_qa/README.md` |
| SiPMs per bar end | 2 (Dylan, 30 Oct; the earlier "80 per wall / 320 in all") | HANDOFF 2026-10-13 |
| signal | 22–31 mV per MIP per end after the preamp (0.47 MeV in 3 mm) | `nTof_x17/ntof_scint_recovery/ANALYSIS_PLAN.md` |
| bias | ~63 V into the preamp boards | budget `lvsipm` |
| ganged timing | σ_y ≈ 10–13 cm along the bar from either the top/bottom Δt or the amplitude ratio; v_eff ≈ 15 cm/ns, λ_eff ≈ 1.0–1.6 m; σ_t ≈ 0.4 ns (clean control) | `nTof_x17/mx_july_beam_qa/slides/vertical_slides.tex`; scint_recovery |

**To find out, before any design (ask whoever built the walls):**
1. The SiPM model and size (Hamamatsu S13360 / S14160 class?), its V_bd, gain, capacitance and dark count. This
   sets the Radioroc gain range and whether ~63 V is the SiPM bias or the preamp supply.
2. Where the ganging happens: are the 8 SiPMs of a group (4 bars × 2) wired in parallel before one preamp, or
   preamplified separately and then summed? Passive parallel ganging adds capacitance (slow edges, worse timing)
   and dark noise. That alone may explain the ganged timing.
3. How the SiPMs are mounted: soldered to the preamp board, or on their own small boards with a connector?
   That decides whether a passive carrier can replace the preamp board without touching the bars.
4. Whether the dark 4 bars per wall have SiPMs at all.
5. Who can respin the boards, and the drawings.

---

## 2. The front end: what replaces the preamp board

| | F: passive carrier → FERS on the wall | P: per-channel preamp boards → LEMO → digitizer |
|---|---|---|
| what is built | 4 (or 8) small boards per wall: SiPM pads, a bias trace, a connector to a short flat coax or Samtec cable | a respin of today's preamp board with one amplifier per bar end (or per SiPM) and LEMO outputs |
| bias | FERS on-board A7585D (20–80 V, 10 mA), per-channel trim ~0.55 V (A5204) | the 63 V lab supply, as now |
| signal processing | Radioroc: preamp, two gains, shaper, discriminators; picoTDC time | preamp on the wall; a digitizer does the rest |
| cabling | ≲ 1 m per channel inside the wall frame | 160–320 LEMO cables to the rack (budget `lemo` item) |
| trigger | the board's own logic, T-OUT per wall (§3) | an on-board analog sum per group can feed M1 as now (proven) |
| risk | cable length and pickup between SiPM and ASIC; ASIC dynamic range for a shower (Radioroc ≲ 2000 p.e.) | board design effort; 3× the money in digitizers |

**F is the better design.** SiPM ASICs exist for this job: they bias, trim and time each SiPM, and the board can sit
on the wall. **P keeps today's trigger exactly**, which is its only real advantage.

### 2.1 The board: A5204 rather than A5202

| | A5202 | **A5204** |
|---|---|---|
| ASIC | 2 × Citiroc 1A | Radioroc 2 + picoTDC |
| charge | 13-bit, 160 fC–400 pC (1–2500 p.e. at 10⁶), LG/HG | 12-bit peak sensing, HG 5–80 / LG 0.5–8, up to ~2000 p.e. |
| time | ToA/ToT, 0.5 ns LSB, ~250 ps RMS (CAEN page) | picoTDC, 3.125 ps LSB; 55 ps FWHM at 1 p.e. |
| trigger logic | AND / OR / majority | OR, plane coincidence, **paired-channel AND**, programmable majority, T0/T1 in |
| conversion | ~10 µs (spectroscopy) | ~10 µs |
| supply status | CAEN expects 2–3 more years of Citiroc A5202 (budget note) | current |

- **Choose the A5204.** Its timing is what makes a per-bar TOF and v from Δt worth having. Its paired-channel AND is
  the per-bar top-bottom coincidence. And it is not the board about to go out of production.
- **Per SiPM (320):** two A5204 per wall. Put the two SiPMs of one bar end on the same board. **(ask CAEN)** whether
  the logic can form (top₁ OR top₂) AND (bot₁ OR bot₂) per bar, or only fixed adjacent pairs. If only pairs, pair
  the two SiPMs of one end (a dark-count cut) and OR the ends on the board.
- **The 24 spare inputs per board at 160 ch** can take the 2 plastic PMTs' dynode copies, or a test pulser.

---

## 3. The trigger

### 3.1 The logic

```
 wall w, bar b:  top_b, bot_b  ── A5204 (on the wall) ── pair AND (top_b · bot_b), OR over b ──> T-OUT_w (LVTTL)
                                         ^ T1-IN  <── global TRIG (fan-out)                          │
 plastics (2 PMT / arm) ── N979 ── V1730S                                                            │
                         └──────── M2 discr. ½ MIP, OR per arm ──────────────────────────────────────┤
                                                                                                     ▼
                       M3: leg_i = T-OUT_i AND plastic_i  (window set by the T-OUT jitter; 20 ns if it allows)
                       M4: PAIR / SINGLE ÷P / CLOCK, veto = BUSY (DREAM TCM busy OR FERS busy OR hold)
                       TRIG ──> DREAM TCM, V1730S TRG-IN, DT5215 / A5204 T1-IN, scalers
```

- **The wall OR moves from M1 into the FERS board.** M1 and the 4 linear FIFOs go away, and five N1081Bs remain
  (PLAN.md §9, D).
- **T-OUT is LVTTL.** The N1081B inputs take TTL directly.
- **Latency.** The FERS discriminator and FPGA add ~100–200 ns to the wall leg (**guess, ask CAEN**). Delay the
  plastic OR to match: the N1081B gate-and-delay, or cable. DREAM absorbs µs of latency (PLAN.md §1, lesson 11).
- **Jitter sets the M3 window.** If T-OUT is FPGA-synchronous (8 ns steps), the leg window grows from 20 to ~30–40 ns.
  At LNL this costs nothing: two-arm randoms are ≤ 1 /s up to 80 ns (PLAN.md §2.3). At Birmingham or FRM II it
  matters, and the per-bar times recorded on every event can tighten the window offline.

### 3.2 Readout on the global trigger

- The A5204s run triggered: **spectroscopy + timing on T1-IN = the global TRIG.** Every channel is converted on
  every accepted trigger: charge (LG, HG), time of arrival and time over threshold.
- **Dead time.** About 10 µs per event, hidden under DREAM's ≥ 298 µs busy. The FERS busy goes into the BUSY OR
  as a guard; it should never be the one that vetoes.
- **Event lock.** The FERS trigger ID counts the same triggers as DREAM and the V1730S, because nothing reaches
  any of them while any is busy (PLAN.md §4.2). Record the FERS timestamp too, for the Δt check.
- **Data** (`out/sipm_channels.csv`): 2 kB per event at 160 ch and 4 kB at 320, so 0.2–1 MB/s at 100–250 Hz.
  TDlink carries 3.125 Gb/s. A digitizer route would be 10 MB/s (VX2745) to 330 MB/s (V1742 waveforms).
- **Software.** CAEN's open FERS library (Janus is its reference GUI) under a Python service of ours, run and
  stopped by `daq_control` with DREAM's run and sub-run numbers, like the V1730S (PLAN.md §6).

### 3.3 Options considered and why not first

| | why not first |
|---|---|
| PETsys TOFPET2 (256 ch, ~30 ps TDC bins) | Built for trigger-less streaming with software coincidences: no per-wall hardware OR that we know of **(ask PETsys)**. It would need a separate analog trigger, which the SiPMs can't provide. Good timing and price. |
| Waveform digitizers (V1742 ×5–10, VX2745 ×3–5) | They need per-channel preamp boards and LEMO cabling, and cost €100–135 k. Waveforms add little once the ASIC gives charge and time per channel. |
| A5202 (Citiroc) | Cheaper (F160c, ~€29 k), but ~250 ps RMS time with a 0.5 ns LSB, and near end of supply. Fine if TOF is not needed. |
| NINO-type ToT boards + a TDC (V1190/picoTDC) | Proven timing (ALICE TOF), but a custom build. No charge measurement beyond ToT. |

---

## 4. Synchronisation, power, mechanics

- **Clock.** The DT5215 can distribute a common clock to its boards. Whether it takes an external 62.5 MHz /
  10 MHz reference is **(ask)**. If yes, feed it the same reference as the V1730S, and the wall times line up with the
  plastics to the TDC level. If not, align them offline: each event has a plastic time in the V1730S and a bar
  time in the FERS.
- **Per-bar time calibration.** Cosmics through the wall and a plastic, per bar and per end: offsets, v_eff and λ
  per bar, as `16_wall_vertical.py` does for the groups at n_TOF.
- **Power.** ~10–15 W per A5204 (**guess**). One 12 V supply per wall or a single bus. Put the DT5215 and the
  FERS supply on the readout PDU (PLAN.md §7), so a hung board can be power-cycled with the rest.
- **Heat and light-tightness.** A board on the wall frame sits outside the light-tight container; only the carrier
  is inside. Leave 2–3 cm for the cable feed-through.
- **Material.** The board mounts behind the wall, outside the acceptance (the plastics are behind the wall, so
  mount it at the top or bottom of the frame, not behind the bars).

---

## 5. Bench tests (cosmic bench, one wall)

| # | test | pass | decides |
|---|---|---|---|
| S1 | One bar end on an A5204 demo board through a 0.5–1 m carrier cable: MIP charge, p.e. per MIP, noise, dark-count rate at ½ MIP | MIP ≫ noise; dark-trigger rate ≪ 1 kHz per bar after the top·bottom AND | the F front end |
| S2 | T-OUT latency, jitter and the logic: pair AND top·bottom, OR over 20 bars; and for 320, the 2-SiPM AND/OR | fixed latency; jitter ≲ 5 ns (20 ns window kept) or ≲ 10 ns (40 ns window) | the trigger path |
| S3 | Timing: σ_t per end and of the mean time, and σ_v from Δt, against the M3 telescope's track position | σ_v ≲ 4 cm, σ_t(mean) ≲ 0.25 ns per bar (the per-bar case in `../sipm_wall`) | whether TOF and v are as assumed |
| S4 | 2 SiPMs per end read separately vs summed on the carrier | the gain in σ_t, the dark-rate reduction from a 2-SiPM AND | 160 or 320 |
| S5 | Full-wall run: 40 (or 80) channels, triggered by the plastics, at 1 kHz with a pulser | no lost events, event IDs locked to the V1730S | readiness |

S1–S3 need one demo A5204 (CAEN lends them) and one opened wall. They can run alongside PLAN.md's T6, which was
the same test planned for the A5202.

---

## 6. What changes elsewhere

- **PLAN.md:** architecture D is this plan (A5204 instead of A5202; 4 or 8 boards; €37 k / €64 k for the wall part).
- **budget/items.py:** `sipmdaq` gets the A5204 option. `lemo` is not needed for F (carrier boards instead).
  `lvsipm` (63 V supply) is not needed for F: the FERS biases the SiPMs. `sipmcomp` becomes "carriers + SiPMs for
  the dark bars". Not changed yet: do it after the walls' make-up (§1) is known.
- **Trigger thresholds:** per bar, with the top·bottom AND. That replaces today's ~8–10 mV threshold on the group
  sum.

## 7. Questions

**Wall builders:** §1, items 1–5.

**CAEN:**
1. A5204 price (×4 and ×8) and DT5215; A5204 power draw.
2. A5204 trigger logic: paired-channel AND on arbitrary pairs or only adjacent channels; a 2-of-4 per bar for 320;
   T-OUT latency and jitter in spectroscopy+timing mode with an external trigger.
3. DT5215: external clock and reset input; busy output.
4. Maximum cable length SiPM → Radioroc input before noise and timing degrade; recommended connector.
5. A demo A5204 for S1–S3.

**PETsys:** a hardware trigger out per FEB (an OR of the channels), and its latency.

Sources: CAEN product pages ([A5202](https://www.caen.it/products/a5202/), [A5204](https://www.caen.it/products/a5204/));
PETsys TOFPET2 ([arXiv:1808.05833](https://arxiv.org/abs/1808.05833), [arXiv:1911.08156](https://arxiv.org/abs/1911.08156)).
