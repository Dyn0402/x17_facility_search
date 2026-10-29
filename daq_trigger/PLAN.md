# Trigger and DAQ for a run away from n_TOF: a plan with options and contingencies

**Started 2026-10-29.** Facility-independent, written with LNL as the first case. Numbers: `daq_plan.py` →
`out/live.csv`, `out/randoms.csv`, `out/power.csv`, `out/costs.csv`, `out/figures/live_and_randoms.png`.

The question (Dylan, 29 Oct): at n_TOF the trigger worked, but almost none of that equipment comes with us. We
assume DREAM is borrowed from CEA again. We must read out some number of scintillator channels and trigger on
scintillator coincidences. DREAM has no trigger output to another DAQ, and the Micromegas are far too noisy to
trigger on. So the scintillators make the trigger and send it to DREAM. We liked the N1081Bs because Claude could
drive them directly over their API. We need a power switch we can cycle remotely. And is splitting the scintillator
signals (as at n_TOF) the only reasonable way, or can a digitizer make the trigger itself?

Facility facts not found publicly are marked **(ask)**; prices without a public source are **guess**.

---

## 0. Bottom line

1. **Keep the n_TOF trigger logic, and fix what hurt us there.** The logic carries over unchanged: wall OR
   (½ MIP), plastic OR (½ MIP), leg = wall AND plastic in 20 ns, PAIR = ≥ 2 legs, SINGLE = ≥ 1 leg, with a 1 Hz
   clock. Three things are new:
   - **a prescaler on SINGLE.** The N1081B can do this itself (§3.2): its SCALER function is a frequency divider
     (`configure_scaler(section, scale=1…10⁸)` in the API), and the budget wrongly says no N1081B function divides
     by N.
   - **an artificial DREAM busy (§4.2)** of ~330–350 µs, started by every trigger. DREAM then never refuses a
     trigger, so its event *k* is the digitizer's event *k*. It costs 0.5–1 % live time at LNL.
   - **a trigger word** written into spare digitizer channels.
2. **Splitting is not the only way, but for the first run it is still the one to commit to (§5).** Do it with
   an **active** split, CAEN N979-class amplifiers with two bridged outputs per channel, not BNC-Ts: the passive
   split halved the plastic amplitude at n_TOF. There are three ways to make the trigger:
   - **A/B: analog split + NIM logic.** Proven at n_TOF, independent of the digitizer, 20 ns windows.
   - **C: the digitizer makes the trigger primitives.** The V1730 can put its per-channel-pair discriminator
     outputs on LVDS, and an FPGA unit (DT5495) forms the trigger. It needs no splits and is ~€25 k cheaper
     (§9), but it rests on firmware we have not run and on a single board.
   - **D: the front end makes the trigger.** FERS (Citiroc) gives a trigger out per board. This is *forced*
     once the walls are read bar end by bar end (the 160-channel upgrade): SiPM inputs cannot be split.
   - **Plan:** commit to **B** (active split + N1081B logic) for the first run. Bench-test **C** before buying
     the second and third digitizers (§10). Use **D** for the walls if they are un-ganged.
3. **The scintillator DAQ:**
   - for the as-built detector (32 ganged wall channels + 8 PMTs), one **V1742** (DRS4, 32 ch) for the walls and
     one **16-ch V1730S** for the PMTs, the trigger word and spares, in a small VME crate. The busy lock (≥ 330 µs)
     hides the V1742's dead time (~110 µs, guess), so the cheap DRS4 costs no live time.
   - for the upgrade, FERS on the 160 bar ends.
   - LNL's electronics pool may lend CAEN digitizers **(ask)**.
4. **Remote power (§7):**
   - **Cheapest:** one switched PDU on the NIM bin that holds the N1081Bs (NETIO PowerPDU 8KS, ~€520; Gude
     8226-1, 12 outlets on 2 × 16 A, €741 ex VAT).
   - **Better:** buy the logic units as **DT1081B desktops**. Each draws 20 W from its own mains plug, so a PDU
     can cycle *one board* at a time. That also saves a NIM bin.
   - **Whole DAQ:** about 2.1 kW (~9 A at 230 V). Put it on two 16 A switched PDUs: one for trigger + readout,
     one for computing.
   - **Recovery script:** power-cycle the board, re-apply its configuration from the repo, read it back to
     verify, then resume. Our tooling already has the session hygiene this needs.
5. **Synchronisation is the hidden cost.** At n_TOF, matching DREAM to the scintillator data took a per-bunch
   clock fit and reached 95.8 % (§1). A DC beam has no bunches to align on. Hence the busy lock, the trigger word
   and both timestamps on every event, from day one.
6. **Cost, trigger + scintillator DAQ, central (range):**
   - B €86 k (62–116 k);
   - B with DT1081Bs €82 k;
   - C €58 k (44–76 k);
   - n_TOF clone A €83 k.

   The budget's Self-sufficient preset has €51 k (trigger) + €31 k (scintillator DAQ) = €82 k for the same scope.
   So B costs what the budget already holds; C would save ~€25 k if its bench test passes (§10, T5).

---

## 1. What n_TOF taught us

Sources: `~/PycharmProjects/nTof_x17_DAQ` (`n1081b/README.md`, `n1081b/CLAUDE.md`, `RUN_MODES_2026-07.md`,
`docs/REPORT_2026-07-28_pulser_daq_characterization.md`, `VETO_TEST_RESULTS_2026-07-02.md`),
`nTof_x17/ntof_dream_merge/DREAM_NTOF_CALIBRATION.md`, `budget/README.md`.

| # | Lesson | What it means for the next run |
|---|---|---|
| 1 | **The trigger chain worked**: 6 N1081Bs (M1 wall OR on the 428F segment sums, M2 plastic discriminators, M3 sector AND 20 ns, M4 Singles/Doubles/veto/master, M5 scalers and time tags, M6 pulser, mesh injection, SiPM blanking), 6 linear FIFOs, dozens of splits. All rented from CERN. | The same logic, re-bought. We own no NIM module. |
| 2 | **N1081B control over the websocket API is excellent until a client disconnects dirtily.** The board's daemon is libwebsock 1.0.7 (2014, abandoned). A handful of dirty disconnects wedges it. Recovery took hours of isolation or a physical reboot, and **there is no remote reboot.** M5 waited 2 days for someone at the crate; M3 went link-dead and needed physical attention. | Keep `board_session()` hygiene. **Add a remote power cycle** (§7). Ask CAEN whether the open SSH port (22) can reboot the board. |
| 3 | **Two enable layers** (per-channel `status` and function `lemo_enables`), ANDed, plus a firmware alias on M6 B→C. An evening was lost to them. | Configuration as code, with read-back of *both* layers; one board per function where possible. |
| 4 | **Front-end inputs die**: M2's D1 input broke (wall D dead above −24 mV). | Keep one spare N1081B section per function, and a spare board. |
| 5 | **The passive split halved the plastic amplitude**; replacing the BNC-T with a linear FIFO gave ~2× and a cleaner pulse (2026-07-17), and the thresholds had to be recalibrated. | Split actively from the start (§5.2). |
| 6 | **DREAM**: non-paralysable, τ = 298 µs per event (RAW, 20 samples), set by a per-FEU wire limit of ~83 MB/s. IPD, watermark and MultiPack "improvements" all failed. `LocThrot` must stay 1. | live = 1/(1 + f·τ). Above ~300 Hz offered, prescale or select harder. |
| 7 | **DREAM has no busy output we could find**: the three suspect TCM LEMOs showed nothing under 97 % dead time, on every standard and threshold (2026-07-02). | The trigger cannot see DREAM's busy. Make the busy ourselves (§4.2). |
| 8 | **The N1081B time-tag stream goes silent above ~50 Hz** (at stream start); counters work at any rate. | Don't use time tags as the trigger record; use the digitizer (trigger word, §4.3). |
| 9 | **Matching DREAM to the scintillator DAQ was hard**: independent clocks, a per-bunch clock fit, 95.8 % efficiency for wall AND plastic. It relied on the n_TOF bunch structure. | A DC beam has no bunches. Lock the event lists 1:1 and record both timestamps (§4). |
| 10 | **Unattended failures cost data**: FEU 3 dropped off the network and `daq_control` wrote 51 empty sub-runs; the HV CFE server crashed and hung a scan for 2 h. | Watchdogs that stop the run, alert and (where safe) power-cycle (§7.4). |
| 11 | **The MM signal arrives ~1.4 µs before the trigger reaches the TCM** (scint mode, latency 35 at 60 ns). | The DREAM latency register absorbs a slower trigger path; µs-scale extra latency is fine (§4.1). |
| 12 | **Mode switching by script** (`trigger_mode.py`), per-sub-run config snapshots (`poll_modules`), a live trigger diagram in the GUI. | Carry over as they are. That tooling is the reason to stay with N1081Bs. |

---

## 2. What the next site needs

### 2.1 Channels

| detector state | wall channels | PMT channels | analog total | note |
|---|---|---|---|---|
| as built (16 of 20 bars, ganged in 4, top/bottom) | 4 × 8 = 32 | 8 (2 per arm: small plastics or big 2-PMT plates) | **40** | the first-run case |
| split big plates | 32 | 16 | 48 | `trigger_scint/TRIGGER_OPTIONS.md` §8 |
| un-ganged walls, all 20 bars | 4 × 40 = 160 | 8–16 | 168–176 | upgrade (`sipmcomp`); SiPM inputs, cannot be split |
| + liquid scintillators | +4 | | | not in the plan until proven |

Plus 3–4 channels of trigger word and ~4 spares.

### 2.2 Rates and live time (`out/live.csv`)

Offered trigger rate f = PAIR + SINGLE/P + 1 Hz clock, from each facility's Geant4 write-up:

| scenario | offered | DREAM live, native | with the 350 µs busy lock |
|---|---|---|---|
| LNL window, big plastics, 1 µA, P = 10 | 98 Hz | 97.2 % | 96.7 % |
| LNL window, big plastics, 4 µA, P = 20 | 245 Hz | 93.2 % | 92.1 % |
| LNL Be ogive, big plastics, 4 µA, P = 50 | 179 Hz | 95.0 % | 94.1 % |
| ILL PF1B, as built | 250 Hz | 93.1 % | 92.0 % |
| Birmingham 30 bar cell, PAIR only | 617 Hz | 84.5 % | 82.2 % |
| FRM II MEDAPP, PAIR only | 3.2 kHz | 51.2 % | 47.2 % |

- **The scintillator DAQ records only on the global trigger** (≤ 1 kHz at LNL), not every self-trigger. Any
  digitizer keeps up. Waveforms of 40 channels × ~200 ns ≈ 20 kB per event = 2–20 MB/s.
- **Where self-triggered singles matter** is the channel occupancy (pile-up inside a gate): Birmingham's big slab
  sees 5.5 hits per 100 ns (`birmingham/TARGET_GEANT.md` §6). That is a detector and gate-length problem, not a
  DAQ-rate problem.

### 2.3 Timing

- **Leg coincidence:** 20 ns (n_TOF M3, after the FIFO timing scan). PAIR window 50 ns.
- **Randoms against the window (`out/randoms.csv`):**
  - At LNL a wider window costs nothing: 0.25 → 1 two-arm randoms /s from 20 to 80 ns at 4 µA.
  - At Birmingham it is decisive: 350 → 1 390 /s, live 91 → 71 %.
  - **So a trigger with coarse timing (digitizer-formed, 8–16 ns clock steps) is acceptable at LNL but not at
    the high-rate DC facilities.**

### 2.4 Functions the trigger must provide

1. PAIR, never prescaled. SINGLE, prescaled 1/P, with P a run parameter (`lnl/FEASIBILITY_SIM.md` §14.1).
2. A 1 Hz clock (pedestals, MIP gain from random cosmics) and a pulser for tests.
3. A trigger word per event: which outputs fired (PAIR, SINGLE, SINGLE/P, CLOCK, PULSER) and which legs.
4. Scalers on every leg, PAIR, SINGLE, offered and accepted triggers, so that the live time is measured, not
   modelled.
5. A busy/veto that keeps DREAM and the scintillator DAQ on the same event list (§4.2).
6. At a pulsed facility (NFS, LANSCE, n_TOF-like), a beam gate and a T0 (the n_TOF N93B and M6 jobs).

---

## 3. The trigger logic (unchanged from n_TOF, three additions)

### 3.1 Logic

```
 walls (per arm: 4 segments x top+bottom) ── split ──> digitizer
                                           └─> linear FIFO (sum top+bottom) ─> M1 discr. ½ MIP, OR per wall ─┐
 plastics (2 PMT per arm)               ── split ──> digitizer                                               │
                                           └─> M2 discr. ½ MIP, OR per arm ──────────────────────────────────┤
                                                                                                             ▼
                                      M3: leg_i = wall_i AND plastic_i (20 ns, wall leg delayed +20 ns)
                                                                                                             │
           M4.A SINGLE = OR(legs) ──> M5' SCALER ÷P ──┐                                                       │
           M4.B PAIR = MAJ≥2(legs, 50 ns) ────────────┤                                                       │
           M6  CLOCK 1 Hz, PULSER ────────────────────┤                                                       │
                                                      ▼                                                       │
                              M4.C TRIG = OR(...) with VETO = BUSY ──> fan-out: DREAM TCM, digitizer TRG-IN,
                                                      │               N93B start (BUSY 330–350 µs), scalers
                              copies of PAIR / SINGLE / SINGLE÷P / CLOCK, stretched ~200 ns ─> digitizer spare ch
```

### 3.2 The prescaler is in the N1081B (correction to the budget)

- **The manual says it can:** "The SCALER function acts on the enabled input channels CH 1,2,4,5 as counter and
  **frequency divider** … scaled by a user-defined integer even factor. Scaled-down signals are sent to the
  correspondent output" (UM8139 rev. 1, p. 34).
- **The API agrees:** `configure_scaler(section, scale, …)`, scale 1…100 000 000 (SDK websocket API,
  "CONFIGURE SCALER").
- **To test on the bench (§10, T1):**
  - does an odd P work, or only even P as the manual says? Even is enough: P = 2, 4, 10, 20, 50;
  - the output width;
  - that the divider counter is reset at run start (CH5 = RESET).
- **If it works**, the budget's prescaler item (N1145 preset counter, €2.5 k, or a DT5495, €8 k) drops to €0:
  one N1081B section.

### 3.3 Where each N1081B function goes

| board | n_TOF role | next run |
|---|---|---|
| M1 | wall OR on 16 segment sums | same (or removed if FERS makes the wall OR, §5.4) |
| M2 | plastic discriminators | same; 8 or 16 PMT inputs (split plates need 2 sections more) |
| M3 | sector AND 20 ns | same |
| M4 | Singles, Doubles, veto, final OR → TCM | same, with VETO = BUSY |
| M5 | scalers + time tags | scalers only (counters work at any rate); **one section = SCALER ÷P** |
| M6 | γ-flash countermeasures, pulser, PS fan-out | clock, pulser, spare sections; at pulsed sites the beam-gate fan-out again |

Six boards: five in use and one whose sections are spares. n_TOF showed that we need them (M2 D1, M3 link loss).

---

## 4. The DREAM interface

### 4.1 What DREAM gives us, and what it doesn't

| | status | source |
|---|---|---|
| external trigger input (NIM LEMO on the TCM) | yes, used at n_TOF | `RUN_MODES_2026-07.md` |
| trigger latency the SCA can absorb | latency register in 60 ns units; 35 used at n_TOF; the SCA is 512 cells (30.7 µs at 60 ns); CLAS12 runs a 16 µs latency | TWEPP 2014 DREAM talk; **max (ask CEA)** |
| busy / veto output | **none found** on the three TCM LEMOs (2026-07-02 test) | `VETO_TEST_RESULTS_2026-07-02.md` |
| per-event timestamp | yes, 10 ns ticks (`nt.timestamp`) | pulser report §1.4 |
| per-event trigger pattern / input latch | **(ask CEA)** | budget question |
| external clock in / timestamp reset in | **(ask CEA)**: the CLAS12 MVT FEU manual has a "Dream clock module" section | MVT FEU User Manual §3.9 |
| derandomiser depth | ~24 events; with Hwm 1 the FEU takes exactly one at a time | pulser report §3.4 |

### 4.2 The busy lock: make DREAM's dead time ourselves

**Problem.** The trigger is sent to two DAQs. DREAM refuses triggers for ~298 µs after each one and tells nobody.
The digitizer records every trigger. The two event lists then differ, and only a timestamp fit can match them.
At n_TOF that fit needed the bunch structure.

**Fix.** Every accepted trigger starts a **non-retriggerable gate of T = 330–350 µs**. It is longer than DREAM's
wire-limited 298 µs spacing; the readout floor is 210 µs. The gate is ORed with the digitizer's own BUSY and fed to
the VETO of the final OR (M4.C, `or_veto`, CH6). DREAM then never sees a trigger while busy, so:
- event *k* in DREAM = event *k* in the digitizer: the trigger word, the leg pattern and the scintillator
  energies attach by index;
- the live time is measured exactly by the scalers: accepted / offered;
- the cost is 0.5–1.1 % of live time at LNL and ILL rates, 2.2 % at Birmingham, 4 % at FRM II (`out/live.csv`).

**How to make a 350 µs gate.** The N1081B cannot: monostable 15 ns–1 µs, gate 15 ns–10 µs (datasheet). Options:
1. **A NIM dual timer (CAEN N93B class)**, 50 ns–10 s, non-retriggerable. It is the n_TOF beam-gate module, and
   it also covers the beam gate at a pulsed facility. ~€2 k new (guess), ~€0.5 k used. **Recommended.**
2. An N1081B workaround: CHRONOMETER (RUN output high from START to STOP) with the STOP from a COUNTER TIMER
   target. Bench-test only (T2); it ties up two sections.
3. The DT5495 FPGA unit (option C), where it is a few lines of firmware.

**Check, always.** Record DREAM's timestamp and the digitizer's timestamp on every event, and compare the Δt
sequences online (a running check in the stats page). If DREAM ever drops an event anyway (an FEU drop, an eventId
gap), the comparison finds where and re-syncs. That is the n_TOF matcher, simplified because the sequences are
meant to be identical.

**Set T from a measurement** (T2): the pulser method of the 2026-07-28 report gives DREAM's spacing distribution
at the run's sample count and FEU set. T = p99.9 + 20 µs. T scales with the samples (τ ∝ n_samples).

### 4.3 The trigger word

- Copies of PAIR, SINGLE, SINGLE÷P, CLOCK (and PULSER), each stretched to ~200 ns by an N1081B monostable, go
  into spare channels of the PMT digitizer. They are read with every event at zero extra cost, whatever the
  firmware.
- The leg pattern is in the digitizer data itself: which walls and plastics crossed threshold.
- Prescale bookkeeping: the scaler counts SINGLE before and after ÷P, so the normalisation is exact for any P.
- If CEA confirms the TCM latches an input pattern **(ask)**, add the word there too.

### 4.4 Clocks

- **The busy lock makes a common clock unnecessary for the match.** Timestamps are only a check.
- **If the TCM takes an external clock or reset (ask)**, distribute one 10 MHz/62.5 MHz reference and a run-start
  reset from M6, so that both timestamps count the same time.
- **Cosmic TOF between arms** needs only the digitizer's own clock: all PMT channels on one board, or boards
  daisy-chained on CLK-IN/OUT.

---

## 5. Splitting the signals, or letting the DAQ make the trigger

### 5.1 Three ways to get a trigger out of a scintillator channel

| | how | trigger timing | independent of the DAQ? | used where |
|---|---|---|---|---|
| **1. analog split** | passive (BNC-T, resistive), or active (linear FIFO, fast amp with two outputs) → NIM discriminator → logic | analog, ~ns; 20 ns windows proven | yes: the trigger survives a digitizer crash | n_TOF |
| **2. front-end discriminator exported** | the readout's own per-channel discriminators come out as logic signals: FERS T-OUT LEMO; V1730 LVDS (per channel pair) | FPGA-synchronous: 2–16 ns steps (**bench-test**) | no | needed for SiPM inputs (FERS) |
| **3. trigger inside the digitizer FPGA** | coincidence/majority among channels in one board, TRG-OUT to DREAM; across boards via LVDS + a logic unit | as 2, + ~0.2–1 µs latency | no | V1730 (validation logic), VX2745, DT5560SE (open FPGA) |

### 5.2 The split, done properly (architectures A and B)

- **Passive split (A):** cheap (€0.5–3 k for 40), but each copy gets half the amplitude. That was a problem
  at n_TOF: the plastics needed a FIFO, and the wall thresholds sit at ½ MIP ≈ 15 mV per end after a split.
- **Active split (B):** the CAEN **N979** is a 16-channel fast amplifier, 1 U NIM, with **two bridged outputs
  per channel**. Its data:
  - 250 MHz bandwidth, < 3 ns delay, ±2 V swing;
  - default gain ×10, with ×2…×9 on request; the N979B has groups of ×2/×4/×8/×10.
  - **Ask for ×2.** The big-plate PMT pulses (≲ 0.5 V for a 15 MeV lepton, from the n_TOF post-FIFO thresholds)
    then stay inside the swing, and both outputs carry the full amplitude.
  - Three N979s cover 32 wall + 8 PMT channels with 8 spare. They replace ~40 splitters and the 2 PMT FIFOs.
- The 4 wall-sum FIFOs (428F / N625 class) stay: M1 discriminates the top + bottom sum of each segment, as at
  n_TOF.

### 5.3 The digitizer makes the primitives (architecture C)

- **The CAEN x730 does this in hardware.**
  - It has 16 LVDS I/O pairs. Per the product page, their programmable functions include "self-trigger outputs,
    trigger validations, veto, busy, … pattern input".
  - The channel-pair ("couple") trigger requests can go out on LVDS.
  - The mapping fits: put a segment's top and bottom in one couple (couple = segment discriminator), and the two
    plastics of an arm in one couple (the arm OR). An arm is then 5 couples (10 channels); 4 arms are 20 couples
    on three 16-ch boards.
- **A DT5495 (Cyclone V, LVDS ports on the motherboard) takes the LVDS** and forms everything in firmware:
  - legs, PAIR/SINGLE, ÷P, the 350 µs busy, the trigger word (output on LVDS to the digitizer's pattern input),
    scalers and timestamps;
  - it drives the TRIG to DREAM and the digitizers.
  - SCI-Compiler (graphical) or VHDL, weeks of work.
- **What it buys:**
  - no splits, no FIFOs, no N979s, 1 N1081B instead of 6, NIM bins down to the CEA one;
  - the thresholds *are* the digitizer's, so trigger and data agree by construction;
  - €58 k against €86 k.
- **What it risks:**
  1. The LVDS trigger-request timing (FPGA clock steps; is a 20 ns window still possible?). At LNL this does not
     matter (§2.3); at Birmingham or FRM II it would.
  2. Whether the x730 firmware we run (waveform vs DPP-PSD) exports couple triggers while recording.
  3. One FPGA design and one board are a single point of failure, and we would write the firmware ourselves.
  4. Claude can drive it (CAEN PLU library, Ethernet), but there is no ready API like the N1081B's, so we would
     write the configuration layer.
  5. The trigger dies with the digitizer.
- **Keep one N1081B in C anyway:** scalers, a NIM-level fallback (PAIR from the legs' LVDS→NIM copies), the clock
  and the pulser.

### 5.4 The front end makes the trigger (architecture D, the 160-channel walls)

- **This route is forced:** with every bar end read, the SiPMs connect straight into the FERS A5202 (Citiroc, 64
  ch, bias on board), and there is nothing to split.
- **One A5202 per wall** (40 ends of 64 inputs): 4 boards, not the budget's 3. The Citiroc discriminators form
  the board trigger, and the board's trigger out (LEMO) is the wall OR into M2/M3. That removes M1 and the 4
  wall-sum FIFOs.
- **(ask CAEN / check the Janus docs):** whether the board logic can require both ends of a bar (adjacent-channel
  AND) before the OR, the T-OUT latency and jitter, and the Citiroc dynamic range at ~31 mV per end at the MIP
  (budget question).
- **The PMTs stay on route 1** (N979 + V1730): they carry the precise time and the energy.

### 5.5 Answer to the question

- **Splitting is not the only way.**
  - A digitizer can form the primitives and send a trigger to DREAM (C).
  - For the SiPM walls read bar by bar, the front end *has* to make the trigger (D).
- **For the first run, still split, actively**, because:
  - the N1081B logic and its tooling are proven, and Claude drives them;
  - the analog path keeps 20 ns windows and survives a digitizer failure;
  - B costs no more than the budget already carries.
- **C is worth a bench test before buying digitizers 2 and 3:** if it passes T5, it saves ~€25 k and four NIM
  slots' worth of failure points.

---

## 6. The scintillator DAQ

| option | channels | per-event dead time | timing | cost [k€] | fit |
|---|---|---|---|---|---|
| **V1742 (DRS4, 5 GS/s, 32 ch) for walls + V1730S (16 ch, 500 MS/s) for PMTs + VME** | 48 | ~110 µs (V1742, guess), hidden by the 350 µs busy | best (waveforms) | 33 (25–42) | **recommended, as-built detector** |
| 3 × V1730S + VME | 48 | ≪ 350 µs | CFD, ~100 ps class on PMTs | 45 (35–56) | needed for C (LVDS primitives) |
| 1 × VX2745 (64 ch, 125 MS/s, open I/O) | 64 | small | marginal for bar position from end-time difference | ~20 + crate | cheaper per channel; test timing |
| FERS-5200: 4 × A5202 + DT5215 | 256 | ≫ kHz | ToA 0.5 ns LSB | 24 (16–33) | 160 bar ends (upgrade, D) |
| borrow from the LNL pool | | | | 0 | **(ask)**, likely V1730 / V1742 |

- **The busy lock changes the choice:** any digitizer with a dead time below ~330 µs costs nothing extra, so the
  DRS4's ~1 kHz ceiling is not a limit here.
- **Readout software:**
  - CAEN's open libraries (CAENDigitizer / FELib) under a Python service of ours, started and stopped by
    `daq_control` with the same run and sub-run numbers as DREAM.
  - Keep the raw waveforms of the PMTs and walls at LNL rates. They are small: 40 ch × 1024 × 2 B ≈ 80 kB per
    event on the V1742 at ~100 Hz = 8 MB/s.

---

## 7. Remote power

### 7.1 What has to be cyclable

| unit | why | how it reboots |
|---|---|---|
| **each N1081B** | websocket wedge: hours of isolation or a physical reboot (§1, 2) | mains off/on; it boots to a volatile state, so the configuration must be re-applied (`RUN_MODES` "re-apply after any power cycle") |
| DREAM FEUs + TCM | FEU network drops (FEU 3, 2026-07-24) | 5 V / 60 A supply: switch its mains input |
| HV supplies | CFE server crash (2026-07-05) needed a stack restart; a power cycle of HV is a last resort (ramp down first) | mains, after `emergency_hv_off.py` |
| digitizer crate | firmware hang | mains |
| DAQ PCs | kernel hang | IPMI / AMT, or a BIOS "power on after AC loss" + PDU |

### 7.2 Options

| option | granularity | price | API | note |
|---|---|---|---|---|
| **NETIO PowerPDU 4KS** | 4 outlets | ~£245 ex VAT (~€290) | REST/JSON, Modbus, MQTT, SNMP; Lua on board | zero-current switching (gentler inrush); ≤ 10 A per outlet, 16 A total (4C data; check 4KS) |
| **NETIO PowerPDU 8KS** | 8 outlets | ~£438 ex VAT (~€520) | same | **recommended for the trigger rack** |
| **Gude Expert Power Control 8226-1** | 12 outlets, 2 banks × 16 A | €741 ex VAT | REST, HTTPS, SNMP, MQTT | **recommended for the readout + computing rack** (two 16 A banks) |
| Wiener NIM bin with the Ethernet option | whole bin | +€1–2 k over a plain bin (guess) | SNMP (WIENER-CRATE-MIB `sysMainSwitch`), web | also monitors the bin's voltages, currents and fans; check that our bin model has it **(ask)** |
| **DT1081B instead of N1081B** | **one board** | as the N1081B **(ask the quote)** | each on its own outlet | 90 mA at 220 V (20 W) each; 6 boards free 12 NIM slots (one bin, €4 k) |
| SSH reboot of the N1081B | one board, no hardware | 0 | ssh | port 22 stayed alive through every wedge; credentials **(ask CAEN)**. Would make all of the above a fallback. |

**Amperage (`out/power.csv`, typical AC load):**

| rack | load | at 230 V |
|---|---|---|
| trigger | ~370 W | 1.6 A |
| readout (DREAM via its 5 V / 60 A supply ~280 W, VME digitizers ~350 W, HV ~120 W, SiPM bias ~100 W) | ~850 W | 3.7 A |
| computing (two DAQ PCs, switch, NAS) | ~850 W | 3.7 A |
| **total** | **~2.1 kW** | **~9 A** |

- One 16 A PDU would carry it all, but not the inrush of every supply at once with margin. Two PDUs on two
  circuits are the sensible split, and they leave room for a second VME crate or the big-plate PMT HV.
- **"Only the N1081Bs" is the cheap case:** a 6-board NIM bin draws ~200 W (1 A). A NETIO 4KS (~€290) on that bin,
  or DT1081Bs on an 8KS, are well within the outlet ratings.
- **Rule:** never cycle the bin that also powers the linear FIFOs or HV during a run. Put the N1081Bs (or DT1081Bs)
  on their own outlets.

### 7.3 Recommendation

1. **N1081B or DT1081B:** ask CAEN for both prices. If the DT1081B costs about the same, buy six. Each sits on an
   outlet of a NETIO 8KS (6 boards + 2 spare outlets: the N93B bin, the switch).
2. **Otherwise:** the N1081Bs share one NIM bin on its own NETIO 4KS outlet, and a wedge costs a whole-bin cycle
   (~2 min of trigger downtime between sub-runs).
3. **Gude 8226-1 for the rest:** the DREAM supply, the digitizer crate, the HV, the PCs (AC-loss power-on set in
   the BIOS).
4. **Ask CAEN for SSH reboot access.** It costs nothing and would make the PDU the second line of defence.

### 7.4 The recovery script

`n1081b_session` already detects `BoardWedgedError` and writes a quarantine marker. Extend it:
1. pause the run at the sub-run boundary (`.pause_run`);
2. cycle that board's outlet (PDU REST);
3. wait for login; re-apply the board's configuration from the repo (`trigger_mode.py` + the setup scripts);
4. read back **both** enable layers (§1, 3) and compare with the design model (`n1081b_module_map.py`);
5. clear the quarantine and resume; Telegram alert.

Same pattern for an FEU drop:
- stop the run (do not write empty sub-runs, §1, 10);
- cycle the DREAM supply;
- wait for all 8 FEUs on the network;
- restart RunCtrl.

**Never cycle the HV supply with HV on.**

---

## 8. Facility variants

| facility | beam | trigger | DAQ notes |
|---|---|---|---|
| **LNL** (first case), Demokritos | DC protons, ≤ 4 µA | PAIR + SINGLE ÷10–50, 100–250 Hz | B or C both fine; windows not critical; the busy lock costs ≤ 1 % |
| **ILL PF1B** | DC cold neutrons | PAIR, 8–250 Hz | as LNL; no prescale needed with the He tube |
| **Birmingham, FRANZ, FRM II** | DC fast/epithermal, high γ/n room load | PAIR only, 0.6–3.2 kHz | keep the analog 20 ns path (B): randoms grow linearly with the window (§2.3). Short gates against pile-up (slab 5.5 hits/100 ns). DREAM live 47–85 %: here a lower n_samples (τ ∝ n) is the lever. |
| **NFS, LANSCE, any pulsed source** | pulsed | PAIR (+ SINGLE) within a beam gate | the N93B also makes the beam gate; T0 into the digitizer; the γ-flash countermeasures (n_TOF M6: mesh injection, SiPM blanking) come back |

---

## 9. Architectures and cost (`out/costs.csv`)

Trigger + scintillator DAQ for the as-built detector (32 wall + 8 PMT channels), EUR 2026, central (range).
Unit prices from `budget/items.py`; the N979, N93B, V1730S, VME and PDU prices are new (guess, except the PDUs:
catalogue).

| | what | central | range |
|---|---|---|---|
| A | n_TOF clone: passive splits, 6 FIFO, 6 N1081B, N93B, V1742 + V1730S, 2 NIM bins, 2 PDUs | 83 k | 59–114 k |
| **B** | **active split (3 × N979), 4 FIFO, 6 N1081B, N93B, V1742 + V1730S, 2 NIM bins, 2 PDUs** | **86 k** | 62–116 k |
| B′ | B with 6 DT1081B (per-board power cycle), 1 NIM bin | 82 k | 59–110 k |
| C | 3 × V1730S + VME, DT5495, 1 N1081B, no splits/FIFOs/bins | 58 k | 44–76 k |
| D | upgrade: FERS 4 × A5202 for 160 bar ends, 5 N1081B, 1 N979 + V1730S for PMTs | 74 k | 52–101 k |

**The budget's Self-sufficient preset** carries the same scope as €51 k (trigger group) + €18 k (FERS) + €12.8 k
(PMT digitizer) = €82 k. B is the same money spent differently:
- an N979 instead of splitters and 2 FIFOs;
- an N93B instead of a prescaler (the prescaler moves into the N1081B);
- a V1742 for the as-built ganged walls instead of FERS, which waits for the un-ganged upgrade;
- PDUs added.

---

## 10. Bench tests before buying (cosmic bench, one arm; CAEN lends demo units)

| # | test | pass | decides |
|---|---|---|---|
| T1 | N1081B SCALER ÷P: P = 2, 4, 5, 10, 50; output width; reset | exact division, reset works | the prescaler item → €0 |
| T2 | DREAM spacing at the run's n_samples (pulser method, 2026-07-28); the busy lock with an N93B at T = p99.9 + 20 µs; 10⁶ triggers at 3 kHz offered: DREAM eventId vs digitizer event count | zero mismatches; live = accepted/offered to 0.1 % | the 1:1 event lock |
| T3 | N979 at ×2 vs passive split vs FIFO on a plastic PMT and a wall channel: amplitude, noise, MIP threshold | full amplitude on both outputs, no ringing | B's front end |
| T4 | trigger word into V1730 spare channels; prescale bookkeeping over a 1 h cosmic run | word on every event; SINGLE count / P = recorded | §4.3 |
| T5 | **C:** V1730 couple trigger requests on LVDS (waveform and DPP firmware) → DT5495 (CAEN demo) → leg coincidence; window width vs the analog chain on cosmics | ≤ 20–30 ns window, ≥ 99 % agreement with the analog leg | buy 3 × V1730S + DT5495 (C) or V1742 + N979 (B) |
| T6 | FERS A5202 on one wall: T-OUT per board, adjacent-channel AND, jitter, Citiroc range at 31 mV | wall OR within 20 ns of the plastic | D, the 160-ch walls |
| T7 | PDU drill: wedge a spare N1081B deliberately (on the bench only), auto-recover with §7.4 | back in the trigger, read-back clean, < 5 min | the recovery script |
| T8 | TCM questions to CEA: max latency, external clock/reset, pattern latch, busy | answers | §4.1, §4.4 |

Order: T8 and T1 cost nothing and come first. T2 needs DREAM at CEA or wherever it sits. T3–T5 need one digitizer
and a demo DT5495. Decide B or C after T5. Buy the remaining digitizers after that decision.

---

## 11. Contingencies

| failure | effect | contingency |
|---|---|---|
| CERN no longer rents N1081Bs; no budget for 6 | — | C (1 N1081B + DT5495), or B with 5 (M6's jobs into spare sections) |
| an N1081B wedges mid-run | trigger stops, or that function does | §7.4 auto-cycle; spare sections on M6; SSH reboot if CAEN allows |
| an N1081B input dies (n_TOF M2 D1) | one leg dead | re-patch to a spare section; the scripts address sections by role, not by fixed number |
| SCALER ÷P fails T1 | no hardware prescale | prescale in the N93B/N1145 or the DT5495 (budget options), or P = 1 at LNL ≤ 2 µA (as built) |
| DREAM drops an event despite the busy lock | event lists shift | both timestamps on every event, Δt-sequence comparison online, re-sync offline |
| DREAM's busy is longer than measured (more samples, more FEUs) | lock breaks | T from a pulser measurement at each configuration; `daq_control` refuses a run if T < τ_measured |
| the digitizer crashes | B: trigger continues and DREAM runs alone (MM-only data, flagged); C: trigger stops | B keeps an independent trigger; C keeps one N1081B that can make PAIR from LVDS→NIM copies |
| CEA does not lend DREAM | no MM readout | out of scope here; the scintillator chain is DAQ-agnostic: any trigger-input readout can take TRIG |
| high-rate facility (Birmingham, FRM II) | DREAM 50–85 % live, randoms | PAIR only; analog 20 ns windows (B, not C); fewer samples; split plates |
| pulsed facility | beam gate, γ-flash | N93B gate (already bought for the lock), M6 sections back to flash duties |
| a PDU fails | no remote cycle | two PDUs; the bins still have front-panel switches; a webcam on the crates shows the touchscreens |
| mains glitch | everything reboots into volatile state | BIOS AC-loss power-on, configuration-as-code restore, UPS for the PCs and the NAS (guess €0.5–1 k) |

---

## 12. Questions

**CEA (DREAM):**
1. The TCM's maximum trigger latency.
2. An external clock input and a timestamp / event-counter reset input.
3. Does the TCM latch an input pattern per event?
4. Is there any busy output (firmware option)?
5. Does the loan include the TCM, the fibres, the 5 V supply and the NIM bin?

**CAEN:**
1. Quotes for the N1081B and the DT1081B (×6), the N979 at ×2 gain (×3), the N93B, the V1742, the V1730S, a VME
   crate + bridge, and the DT5495 + LVDS mezzanine.
2. SSH reboot access to the N1081B.
3. Is SCALER ÷P limited to even P?
4. The x730 LVDS couple-trigger output with the waveform firmware, and its latency.
5. FERS A5202 T-OUT logic: adjacent-channel AND, latency, jitter.
6. Demo units for T5/T6.

**LNL (or the host):**
1. Does the electronics pool lend digitizers (V1730/V1742), NIM bins, linear FIFOs, N93Bs or LEMO cables?
2. Mains: how many 16 A circuits at the set-up, and is there a UPS?
3. Network: is a private DAQ subnet allowed, and remote access from CERN?

Sources for vendor data: CAEN product pages ([V1730](https://caen.it/products/v1730/),
[N979](https://caen.it/products/n979/), [DT5495](https://caen.it/products/dt5495/),
[N1081B/DT1081B](https://caen.it/products/n1081b/)); NETIO ([PowerPDU 8KS](https://www.netio-products.com/en/device/powerpdu-8ks),
[4KS](https://www.netio-products.com/en/device/powerpdu-4ks)); Gude ([8226](https://gude-systems.com/en/produkte/expert-power-control-8226));
Wiener crate Ethernet/SNMP ([JLab note](https://halldweb1.jlab.org/wiki/images/4/4d/WienerCrateEthernetControl.pdf));
DREAM ([TWEPP 2014](https://indico.cern.ch/event/299180/contributions/1659618/), [MVT FEU manual](https://clonwiki0.jlab.org/wiki/clondocs/Docs/MVT_FEU_User_Manual.pdf)).
The N1081B manual (UM8139), datasheet (DS8138) and API are in `~/PycharmProjects/nTof_x17_DAQ/n1081b/docs/`.
