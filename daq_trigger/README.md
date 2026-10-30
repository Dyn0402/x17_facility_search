# daq_trigger — trigger and DAQ for a run away from n_TOF

> **Read this first (2026-10-29).** [`PLAN.md`](PLAN.md) §0 is the plan:
> - keep the n_TOF N1081B logic, adding three things:
>   - the SINGLE prescaler, in an N1081B SCALER section (it divides; the budget said it could not);
>   - a 330–350 µs busy lock from a dual timer. DREAM has no busy output, so this locks the DREAM and digitizer
>     events 1:1, for ≤ 1 % live time at LNL;
>   - a trigger word in spare digitizer channels;
> - split the scintillators actively (N979, two outputs per channel), not passively;
> - record the as-built walls on a V1742 and the PMTs on a V1730S;
> - add remote power: switched PDUs, or DT1081B desktops for a per-board power cycle.
>
> **Update, same day:**
> - The DREAM TCM *has* a busy output: **TODO, solder a LEMO onto it before the next run**. The trigger then
>   vetoes on it plus a short hold gate, and the N93B becomes the fallback.
> - Interactive page: <https://dylan-neff.web.cern.ch/notes/mx17-daq-trigger.html>, with the modules, the flow
>   per architecture, the live-time and randoms calculators, power and cost.
>
> A digitizer-formed trigger (V1730 LVDS → DT5495) needs no splits and saves ~€25 k, but has to pass bench test
> T5 first. The 160-channel un-ganged walls force the FERS T-OUT route. §10 lists the bench tests, §11 the
> contingencies, §12 the questions for CEA, CAEN and LNL.

> **Update 2026-10-30: reading the walls channel by channel.** [`SIPM_READOUT.md`](SIPM_READOUT.md): 160 ch (every
> bar end) or 320 (every SiPM) on CAEN FERS A5204 boards mounted on the walls, fed by passive SiPM carriers; the
> board's paired-channel AND (top·bottom per bar) is the wall OR, replacing M1 and the sum FIFOs. ~€37 k for 160 ch
> (+€10 k over the ganged path), ~€64 k for 320. Gated on bench tests S1–S3 and on what is inside the walls (§1).
> The physics it buys: [`../sipm_wall/`](../sipm_wall/README.md).

The question (Dylan, 2026-10-29): at n_TOF the trigger worked, but none of that equipment comes with us. DREAM is
borrowed from CEA again; the scintillators must be read out and must make the trigger, since DREAM has no trigger
output and the Micromegas are too noisy to trigger on. How, with what, and what can go wrong?

## Files

| file | what |
|---|---|
| `PLAN.md` | the write-up: n_TOF lessons, requirements, the DREAM interface, split vs digitizer-formed trigger, scintillator DAQ, remote power, facility variants, architectures and cost, bench tests, contingencies, questions |
| `daq_plan.py` | the numbers: DREAM live time native vs busy lock per facility, randoms vs coincidence window, rack power, architecture costs (unit prices from `budget/items.py`) |
| `out/live.csv`, `out/randoms.csv`, `out/power.csv`, `out/costs.csv` | its tables |
| `out/figures/live_and_randoms.png` (+ `.csv`) | live time vs offered rate; randoms vs window |
| `SIPM_READOUT.md`, `sipm_readout.py` → `out/sipm_channels.csv`, `out/sipm_costs.csv` | per-channel SiPM wall readout: front end, FERS A5204, trigger, sync, bench tests S1–S5, cost per option |
| `page/template.html`, `page/build_page.py` | the interactive page → `out/mx17-daq-trigger.html` (embeds `out/costs.csv`, `out/live.csv`); publish with `add-note.py … --slug mx17-daq-trigger --force --deploy`. Open a tab directly with `#arch=C`, `Cp` or `D`. |

```bash
~/PycharmProjects/nTof_x17/.venv/bin/python daq_trigger/daq_plan.py
```

## Sources outside this repo

- `~/PycharmProjects/nTof_x17_DAQ/n1081b/` (README, CLAUDE.md, `RUN_MODES_2026-07.md`, the wedge and time-tag
  handoffs; the N1081B manual, datasheet and API in `docs/`)
- `~/PycharmProjects/nTof_x17_DAQ/docs/REPORT_2026-07-28_pulser_daq_characterization.md` (DREAM dead time)
- `~/PycharmProjects/nTof_x17_DAQ/n1081b/VETO_TEST_RESULTS_2026-07-02.md` (no DREAM busy output)
- `~/PycharmProjects/nTof_x17/ntof_dream_merge/DREAM_NTOF_CALIBRATION.md` (how hard the n_TOF match was)
- The budget: `budget/items.py` (updated 2026-10-29 with the prescaler correction, the busy-lock timer and PDUs)
