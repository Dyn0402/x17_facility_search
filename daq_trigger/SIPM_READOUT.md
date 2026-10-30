# Reading the SiPM walls channel by channel: a DAQ and trigger plan

**2026-10-30; updated the same afternoon from the wall documentation (§0, §1), and with the LNL-first staging (§7).**
Companion to `PLAN.md` (architecture D, §5.4, worked out). Numbers: `sipm_readout.py` → `out/sipm_channels.csv`,
`out/sipm_costs.csv`, `out/sipm_staged.csv`. What the extra granularity buys in physics is a separate study:
`../sipm_wall/README.md`.

The question (Dylan, 30 Oct): read each bar of the SiPM wall individually, top and bottom, and maybe each of the
2 SiPMs per bar end, instead of the n_TOF groups. What DAQ and trigger does that take?

Facts not found publicly are marked **(ask)**; prices without a public source are **guess**.

---

## 0. Bottom line

**Updated 2026-10-30 (afternoon) from the wall documentation** (`~/PycharmProjects/MX17_Documentation/sipm_wall/`: the
INFN–CEA DAQ meeting notes of Sep 2025, the INFN note on the rebuilt first plane of 9 May 2026, the n_TOF ISD). Main
change: **inside the wall every SiPM channel already has its own micro-coax.** No preamp board has to be built. INFN
has used CAEN FERS (Citiroc) on the bench to test the bars and the rebuilt plane. It ran the AND2_OR32 trigger (pairs
of channels ANDed, then ORed), which is the per-bar top·bottom trigger proposed here. FERS has not been the
experiment's readout.

**Clarification (Dylan, 30 Oct).** At n_TOF, external boards took the blue micro-coax and summed it into the ganged
LEMO outputs. A future DAQ therefore has two starting points:
- **(a) the short blue micro-coax:** every channel. This needs a custom board that takes the micro-coax and feeds the
  FERS (or another readout);
- **(b) the existing ganged LEMO outputs:** the n_TOF scheme, 4 bars per channel.

Per-bar readout needs (a).

1. **What a wall is (§1).**
   - 20 bars. Each end is read by a 16-pixel linear SiPM array (pixels ~3.2 mm, ~52 mm long) wired as 4 channels
     of 4 pixels. One array covers 2 bars (new clamps, May 2026), so **each bar end has 2 channels**: these are the
     "2 SiPMs per bar end".
   - That makes 20 arrays and **80 channels per wall, 320 in all**. Each channel leaves the wall on its own blue
     micro-coax to the external bias/interface boards: 20 boards per wall, in 4 towers of 5, above and below the
     plane. At n_TOF these summed the micro-coax into the ganged LEMO outputs.
   - Bias ~53–54 V, ~8 µA per array.
2. **Today (n_TOF, PLAN.md B):** 8 channels per wall (16 bars, 4 groups of 4, top and bottom). The ganging is done
   *outside* the light-tight wall, on the external boards that take the micro-coax and give ganged LEMO outputs.
   M1 then discriminated 428F pair sums of those (`nTof_x17_DAQ/n1081b/RUN_MODES_2026-07.md`). **So un-ganging means
   a new board on the micro-coax side plus readout channels, not a rebuild of the bars and SiPMs.** The 4 dark bars were most likely
   a readout-channel limit, not missing SiPMs (the rebuilt plane has all 20 arrays; **ask** about the other three).
3. **The readout: a SiPM front-end ASIC board, not a digitizer.**
   - **CAEN FERS-5200.** INFN has run it on these SiPMs on the bench: 8 arrays (32 channels) per pass with
     `TLOGIC AND2_OR32` on a Sr-90 source at 54 V bias, during the May 2026 rebuild. A single test bar was read the
     same way in Sep 2025.
   - **160 ch** (the two channels of a bar end paired on the new micro-coax board; INFN's "next planes" list
     already considers pairing adjacent channels): **one board per wall**.
   - **320 ch** (every channel): two per wall.
   - The **A5204** (Radioroc 2 + picoTDC) times best. The **A5202** (Citiroc) is the kind INFN tested with
     (model to confirm).
4. **The trigger: the wall OR comes from the FERS board** (§3). Pair a bar's top and bottom and AND them (the
   AND2_OR32 logic INFN used on the bench), then OR over the bars, out on T-OUT. That replaces M1 and the 4 wall-sum FIFOs. n_TOF showed the
   top-bottom coincidence is 99.8 % pure MIPs. M3 and later are unchanged. Unknown: T-OUT latency and jitter
   (**ask CAEN / INFN, bench test S2**).
5. **Cost** (`out/sipm_costs.csv`, wall readout plus the trigger parts it replaces, central and range; every FERS
   price a guess):

   | option | channels | central | range | vs ganged |
   |---|---|---|---|---|
   | G: ganged as n_TOF (V1742 + 4 sum FIFOs + M1) | 32 | €26 k | 19–35 k | — |
   | **F160c: per bar end, custom micro-coax board + 4 × A5202** | 160 | **€25 k** | 18–39 k | **−€1 k** (−€19 k if INFN lends the boards) |
   | **F160: per bar end, custom micro-coax board + 4 × A5204** | 160 | **€33 k** | 22–51 k | **+€7 k** |
   | F320: every channel, 8 × A5204 | 320 | €60 k | 41–89 k | +€34 k |
   | P160: custom board + ×10 amplifiers → 5 × V1742 (waveforms) | 160 | €101 k | 71–133 k | +€75 k |
   | P320: custom board + ×10 amplifiers → 5 × VX2745 | 320 | €134 k | 97–177 k | +€108 k |
   | T160: PETsys TOFPET2 256 ch | 160 | €26 k | 17–43 k | ±0, but no hardware trigger out (§3.3) |

6. **What it buys (`../sipm_wall/README.md`, Geant4 on the LNL samples):**
   - **No change in LNL reach, once the plastics' PMT time makes the TOF.** Per-bar timing would cut as-built
     running time ×0.65, but the plastic time at the n_TOF-measured 0.14–0.29 ns does the same with the walls ganged.
   - The MM road shrinks from 25 % to 9 % of the chamber. That matters at high-rate neutron sites (Birmingham:
     stray neutron-recoil clusters in the road go 14 % → 5 %).
   - Also: a cleaner trigger (per-bar top·bottom), all 20 bars lit (×1.4 trigger acceptance with big plastics), and
     an independent second timer.
   - **Reading the 2 channels of a bar end separately (320) buys nothing:** they share the light of one bar end, so
     separately each has half of it.
7. **Recommendation: go to F160.** Per bar end on FERS, including a custom micro-coax board (~€4 k, guess),
   costs about the same as re-buying the ganged path (the V1742, sum FIFOs and M1 all go). It lights all 20 bars, cleans up the trigger and gives per-bar calibration and
   the MM road.
   - **Start with A5202s:** ask INFN whether the FERS they used on the bench can be lent, for the bench test and
     ideally the run.
   - **Design the micro-coax board with INFN.** They know the connectors and the bias distribution, and their
     Samtec-flat collector card is a ready concept for it.
   - Buy A5204s only if bench test S3 shows the Citiroc timing is not enough. The plastics carry the TOF anyway.
   - Don't go to 320.

8. **Staging (§7): LNL with the ganged walls first.** FERS is what scales from 160 to 320. Plan the first run on a
   borrowed ganged-wall digitizer plus a bought PMT digitizer (path 1b, ~€32 k, nothing stranded). In parallel,
   develop FERS on the micro-coax (path 3, about the same money at LNL); switch when bench test S2 passes.

---

## 1. What is in the walls (from the documentation, 2026-10-30)

| | known | source |
|---|---|---|
| bars | 20 per wall, 500 × 25 × 3 mm (Dylan; Geant4; two bars per 52 mm array; a 50 cm wall). The Sep 2025 test bar was 17.5 mm wide: an earlier prototype, so the design probably changed after it (**ask**). The ISD's 12 mm is ignored | `SimConfig.hh`; DAQ notes |
| wrapping | 3M DF2000MA reflective adhesive film on the rebuilt plane; it also holds the 20 bars together as one plane. No significant light cross-talk between bars | INFN note May 2026 |
| SiPM | linear array, 16 pixels (~52 × 3.2 mm), 4 channels × 4 pixels (2 pins each); one array per 2 bar ends (new clamps); coupled with EJ-560 silicone. Model not named (V_bias ~53–54 V suggests a Hamamatsu S13360-class 3 mm pixel: **ask**) | DAQ notes; INFN note |
| channels | 2 per bar end → 80 per wall, 320 in all; 20 arrays per wall; SiPM cards carry I²C temperature sensors | INFN note ("80 cavetti blu"); DAQ notes |
| cabling | blue micro-coax per channel (80 per wall) → external bias/interface boards, 20 per wall in 4 towers of 5 above and below the plane. **At n_TOF they summed the micro-coax into the ganged LEMO outputs** (Dylan). Proposed by INFN for a final detector: Samtec 20-ch coax flats + a collector card per 5 SiPM cards (20 signals + I²C) | INFN note; DAQ notes; Dylan 30 Oct |
| bias | ~53 V (Sep 2025), 54 V (May 2026); ~0.008 mA per array dark, +0.0005 mA under a Sr-90 source. Per wall ~0.16 mA. The budget's "~63 V, up to 10 A" is wrong by ~10⁴ in current | INFN note |
| amplifier | INFN 2-channel board, ×10, DC coupled, ±6 V (< 100 mA), outputs ch1, ch2 and (ch1 + ch2)/2 | DAQ notes |
| n_TOF chain | 16 bars per wall summed outside the wall into 4 groups, top and bottom; M1 = 428F pair sums | `nTof_x17_DAQ/n1081b/RUN_MODES_2026-07.md` |
| signal | 22–31 mV per MIP per ganged end at n_TOF (0.47 MeV in 3 mm); Sr-90 on INFN's bench FERS: a clear peak at HG > 4000 ADC | scint_recovery; INFN note |
| noise | EM pickup on the blue coax and the interface boards, present with the SiPMs unbiased. Shielding the boards and cables cut it ×5 | INFN note |
| optical cross-talk | an edge pixel of a channel can see the neighbouring bar if the clamp is misaligned; masked with ~3 mm of Al tape on the rebuilt plane | INFN note |
| ganged timing | σ_y ≈ 10–13 cm from the top/bottom Δt or the amplitude ratio; v_eff ≈ 15 cm/ns, λ_eff ≈ 1.0–1.6 m; σ_t ≈ 0.4 ns (clean control) | `nTof_x17/mx_july_beam_qa/slides/vertical_slides.tex`; scint_recovery |

**Still to find out (ask INFN: Cisbani, D'Incecco, Mastinu):**
1. Whether the design changed from the 17.5 mm test bar to 25 mm, and whether the other three planes were rebuilt
   like plane 1 (new clamps, 20 arrays, 80 channels) before the July 2026 run.
2. The SiPM model, gain and dark rate per channel.
3. Which FERS units INFN used on the bench (model, how many, whose), and whether they can lend them.
4. Their Sr-90 / cosmic results with FERS: charge per MIP, and timing if any (Laura Di Bartolomeo's thesis).
5. The external boards: their schematic (where the summing happens, whether a per-channel output can be tapped
   before the sum), and the micro-coax connector type, for the custom board of route (a).

---

## 2. The front end

The SiPM channels come out one by one on the blue micro-coax (§1); the n_TOF external boards then sum them into the
ganged LEMO outputs. There are two starting points:
- **(a) the micro-coax, every channel.** A custom board takes the micro-coax in place of the n_TOF summing boards.
  It distributes the bias and pairs the two channels of a bar end for 160 ch, then feeds the FERS (F) or amplifiers
  and a digitizer (P).
- **(b) the existing ganged LEMO outputs.** This is the n_TOF scheme, 4 bars per channel: PLAN.md B, on a V1742.
  Nothing new is built, and nothing per bar is gained.

Per-bar readout means (a):

| | F: micro-coax → custom board → FERS by the wall | P: micro-coax → custom board → ×10 amplifiers → LEMO → digitizer |
|---|---|---|
| what is built | a micro-coax → FERS-input board (bias distribution, bar-end pairing for 160 ch); INFN's Samtec-flat collector card is one design for it | the same board with LEMO out, plus 80–160 two-channel amplifier boards (the INFN design) |
| bias | through the custom board (a small 54 V supply), or the FERS A7585D (20–85 V, 10 mA) | as now |
| signal processing | Citiroc / Radioroc: preamp, two gains, shaper, discriminators; ToA (picoTDC on the A5204) | a digitizer does it |
| cabling | short: the FERS sits by the towers. Shield the towers (the May 2026 noise test) | 160–320 LEMO cables to the rack |
| trigger | the board's own logic, T-OUT per wall (§3) | sums for M1 as at n_TOF (proven) |
| risk | T-OUT latency/jitter; ASIC range for showers (Citiroc ≲ 2500 p.e.) | 3× the money in digitizers |

**F is the design.** INFN has exercised FERS + AND2_OR32 on these SiPMs on the bench. P keeps an analog path to
the trigger, and that is its only real advantage.

### 2.1 The board: A5202 to start, A5204 if the timing needs it

| | A5202 | A5204 |
|---|---|---|
| ASIC | 2 × Citiroc 1A | Radioroc 2 + picoTDC |
| charge | 13-bit, 160 fC–400 pC (1–2500 p.e. at 10⁶), LG/HG | 12-bit peak sensing, HG 5–80 / LG 0.5–8, up to ~2000 p.e. |
| time | ToA/ToT, 0.5 ns LSB, ~250 ps RMS (CAEN page) | picoTDC, 3.125 ps LSB; 55 ps FWHM at 1 p.e. |
| trigger logic | AND / OR / majority; **AND2_OR32 used by INFN on the bench with these SiPMs** | OR, plane coincidence, paired-channel AND, programmable majority, T0/T1 in |
| conversion | ~10 µs (spectroscopy) | ~10 µs |
| availability | INFN tested with FERS (whose? borrow?); CAEN expects 2–3 more years of supply | current |

- **Start with the A5202,** if INFN's bench FERS were A5202s and can be lent: they know the configuration and the
  trigger logic on these SiPMs.
- **Its timing (~250 ps RMS class) is enough for the wall's job.** The TOF comes from the plastics
  (`../sipm_wall`), and a 0.3–0.5 ns bar time still gives v to a few cm and the MM road.
- **Move to the A5204** only if bench test S3 shows the Citiroc time limits v, or if the run wants the wall as its
  TOF timer.
- **At 160 ch a board has 24 spare inputs per wall:** the plastic PMTs' dynode copies, a pulser, or the
  temperature-sensor lines are candidates.

---

## 3. The trigger

### 3.1 The logic

```
 wall w, bar b:  top_b, bot_b  ── FERS (by the wall) ─ pair AND (top_b · bot_b), OR over b ──> T-OUT_w (LVTTL)
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
| Waveform digitizers (V1742 ×5–10, VX2745 ×3–5) | They need ×10 amplifiers per channel and LEMO cabling, and cost €97–129 k. Waveforms add little once the ASIC gives charge and time per channel. |
| A5204 (Radioroc + picoTDC) from the start | Better time, but ~€8 k more than the A5202, and nobody has run it on these walls. Keep it for when S3 asks for it. |
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
- **Placement and light-tightness.** The FERS board sits by the interface-board towers, outside the light-tight
  container, as the towers do now. Shield the towers and the coax (the May 2026 noise test cut the pickup ×5).
- **Temperature.** The SiPM cards carry I²C temperature sensors. Log them with the run: SiPM gain drifts a few % per
  °C, and the FERS per-channel bias trim can compensate.
- **Material.** The board mounts behind the wall, outside the acceptance (the plastics are behind the wall, so
  mount it at the top or bottom of the frame, not behind the bars).

---

## 5. Bench tests (cosmic bench, one wall)

| # | test | pass | decides |
|---|---|---|---|
| S1 | One wall's micro-coax on a FERS (INFN's, or a CAEN demo) through a prototype of the custom board, shielded: MIP charge on cosmics, p.e. per MIP, noise, dark-count rate at ½ MIP, AND2_OR32 trigger rate | MIP ≫ noise; dark-trigger rate ≪ 1 kHz per bar after the top·bottom AND | the F front end (INFN has done the Sr-90 version) |
| S2 | T-OUT latency, jitter and the logic: pair AND top·bottom, OR over 20 bars; and for 320, the 2-SiPM AND/OR | fixed latency; jitter ≲ 5 ns (20 ns window kept) or ≲ 10 ns (40 ns window) | the trigger path |
| S3 | Timing: σ_t per end and of the mean time, and σ_v from Δt, against the M3 telescope's track position | σ_v ≲ 4 cm, σ_t(mean) ≲ 0.25 ns per bar (the per-bar case in `../sipm_wall`) | whether TOF and v are as assumed |
| S4 | The 2 channels of a bar end read separately vs paired on the custom board | no loss in charge or time from pairing | how to make 160 |
| S5 | Full-wall run: 40 (or 80) channels, triggered by the plastics, at 1 kHz with a pulser | no lost events, event IDs locked to the V1730S | readiness |

S1–S3 need one wall and INFN's FERS, or a CAEN demo unit. Repeat S3 on an A5204 demo only if the A5202 timing
falls short. These replace PLAN.md's T6.

---

## 6. What changes elsewhere

- **PLAN.md:** architecture D is this plan (4 × A5202, borrowed or ~€24 k, or 4 × A5204, ~€32 k, for the wall part).
- **budget/items.py** (not changed yet):
  - `lvsipm`: ~54 V at ~0.2 mA per wall, so any small precision supply, or the FERS bias. Not 63 V / 10 A.
  - `sipmcomp`: no preamp respin. The channels exist, and the dark bars probably have SiPMs (ask about planes 2–4).
  - `lemo`: becomes the custom micro-coax → FERS board (design + fab, a few k€).
  - `sipmdaq`: a "borrow INFN's FERS" option.
  - Change these after INFN answers §1.
- **Trigger thresholds:** per bar, with the top·bottom AND. That replaces today's ~8–10 mV threshold on the group
  sum.

---

## 7. Planning for growth: LNL with the ganged walls first, then per channel (2026-10-30)

The question (Dylan): LNL comes first, and the n_TOF ganged readout should be enough there. Is there something to
invest in now that reads the ganged walls and later scales to ~300 channels?

**Channel counts.** The ganged walls are 32 channels (40 with all 20 bars), plus 8–16 plastic PMTs and ~4 trigger-word
channels: 48–60 analog channels at LNL. Per bar end is 160, every channel 320.

**No single readout does both well.** The ganged outputs are amplified analog pulses on LEMO, which want a
digitizer. The per-channel signals are raw SiPMs on micro-coax, which want a SiPM ASIC (FERS). Each family is poor at
the other job:

| family | ganged LEMO (LNL) | 160–320 raw SiPM | note |
|---|---|---|---|
| **FERS-5200** (A5202/A5204 + DT5215) | not designed for it: an amplified voltage pulse into the Citiroc charge input through an attenuator might work (**ask CAEN, untested**) | **yes: 64 ch per board, one concentrator up to 128 boards, the same software from 160 to 320** | the scalable platform |
| VX2730 (32 ch, 500 MS/s, 250 MHz, open FPGA) | yes, with good timing | 5–10 boards plus ×10 amplifiers: ~€100–200 k | the modern analog board; keep for PMTs |
| VX2745 (64 ch, 125 MS/s) | yes, but **20 MHz bandwidth**: too slow for ns timing | 3–5 boards plus amplifiers | a spectroscopy digitizer, not for us |
| V1742 (DRS4, 32 ch) | yes, cheap (PLAN B) | 5–10 boards, ~1 kHz | does not scale |

**The paths** (`out/sipm_staged.csv`; wall + PMT readout + the analog wall-trigger parts, central, guesses as above):

| path | at LNL | to 160 ch | to 320 ch | left unused after the upgrade |
|---|---|---|---|---|
| 1. PLAN B: V1742 (ganged walls) + V1730S (PMTs); FERS later | €46 k | €71 k | €89 k | V1742, sum FIFOs, M1 (~€26 k) |
| **1b. as 1, ganged-wall digitizer borrowed (LNL pool)** | **€32 k** | **€57 k** | €75 k | sum FIFOs + M1 (~€12 k; nothing if borrowed) |
| 2. 2 × VX2730 for walls + PMTs; FERS later | €59 k | €84 k | €102 k | one VX2730 |
| **3. FERS from day one: micro-coax board + 4 × A5202 at LNL, read per bar end; V1730S for PMTs** | **€44 k** | **€44 k** | €62 k | nothing |
| 3b. as 3 with A5204 | €52 k | €52 k | €78 k | nothing |
| 4. ganged LEMO into FERS through an attenuator, then micro-coax | €31 k | €44 k | €62 k | nothing, but untested |

**What scales is FERS, plus one fast digitizer for the PMTs that never retires.** The PMT digitizer (V1730S, or
a VX2730) is needed in every path and keeps its job after the upgrade: the plastics, the trigger word and spares.
The wall readout is where the choice lies:

- **Path 3 is the scalable investment.** It costs about what PLAN B costs at LNL, reaches 160 channels on day one,
  and grows to 320 by adding boards. It needs two things before LNL:
  - the custom micro-coax board, designed with INFN;
  - **bench test S2**: the FERS trigger out as the wall leg, with its latency, jitter and pair-AND logic.

  It can also run ganged if that is ever wanted: the same board can sum channels by jumper (4 bars, 2 bars, 1 bar
  end) before the FERS.
- **Its fallback costs no hardware.** Keep the n_TOF summing boards. If S2 fails, or the FERS misbehaves at LNL,
  move the micro-coax back onto them, take the ganged LEMOs into a borrowed digitizer, and put M1 back in the trigger.
  That is path 1b, reached by re-cabling.
- **If the first run must use the proven analog trigger: path 1b.** Borrow the ganged-wall digitizer at LNL
  (V1742/V1730; LNL pool, **ask**). Buy only the PMT digitizer, and buy FERS when the walls go per channel. Nothing
  bought is stranded.
- **Avoid paths 1 and 2:** they buy wall digitizers (€14–20 k) that retire at the upgrade. Avoid the VX2745 for
  anything timed.
- **Path 4** (ganged LEMO into FERS) would be the cheapest single platform, but it rests on an untested input
  match. Ask CAEN, and try it in S1 if a FERS is on the bench anyway.

**Recommendation:**
- Plan the first LNL run as **1b** (proven trigger, ~€32 k, nothing stranded).
- Develop **3** in parallel: the micro-coax board with INFN, and S1–S3 on a borrowed FERS.
- Switch the walls to FERS for LNL itself if S2 passes in time (same money). Otherwise switch at the first upgrade.
- Either way, the money goes into FERS boards and a PMT digitizer, which both carry over.

---

## 8. Questions

**INFN (wall builders):** §1, items 1–5; the micro-coax board (§2, §7).

**CAEN:**
1. A5202 and A5204 prices (×4 and ×8) and the DT5215; power draw.
2. Trigger logic (A5202 and A5204): AND2 on arbitrary channel pairs or only adjacent ones (top and bottom of a bar
   need not be adjacent inputs); T-OUT latency and jitter in spectroscopy+timing mode with an external trigger.
3. DT5215: external clock and reset input; busy output.
4. Maximum cable length SiPM → Radioroc input before noise and timing degrade; recommended connector.
5. A demo A5204, if S3 on the A5202 falls short.

**PETsys:** a hardware trigger out per FEB (an OR of the channels), and its latency.

Sources: the wall documentation in `~/PycharmProjects/MX17_Documentation/sipm_wall/` (INFN–CEA DAQ meeting notes,
Sep 2025; "Appunto su aggiornamento primo piano di scintillazione", Cisbani et al., 9 May 2026; n_TOF ISD for the
X17 scintillator wall, Nov 2025); CAEN product pages ([A5202](https://www.caen.it/products/a5202/), [A5204](https://www.caen.it/products/a5204/));
PETsys TOFPET2 ([arXiv:1808.05833](https://arxiv.org/abs/1808.05833), [arXiv:1911.08156](https://arxiv.org/abs/1911.08156)).
