# Demokritos (Athens): the ATOMKI ⁴He search with the MX17 apparatus

Started 2026-10-19. Could the n_TOF X17 apparatus test the ATOMKI ⁴He anomaly, ³H(p,e⁺e⁻)⁴He, on the 5.5 MV
tandem of NCSR "Demokritos"? What is the beam, what is the target, and how far would we get before any Geant4?

## Read this first: the pre-Geant4 answer (2026-10-19, `ESTIMATES.md`)

- **The case is ³H(p,e⁺e⁻)⁴He, the other ATOMKI claim.**
  - ATOMKI's 2019/2021 result: B_x = 5.1×10⁻⁶, m = 16.94 MeV, an excess at ~115° at E_p = 510/610/900 keV.
  - It is the same ⁴He\* as n_TOF's ³He(n,e⁺e⁻) and the ILL's thermal capture. Nobody has checked it independently.
  - Demokritos owns Ti-T targets and puts protons on them routinely, for ³H(p,n) neutrons. The licences and
    shielding exist.
  - Below E_p = 1.019 MeV there are no neutrons. ⁴He has no γ₁.
- **The neutron beams are ruled out.** At 10⁵–10⁶ n/cm²/s they give ≲ 0.5 X17/day.
- **Rates at 1 µA, 900 keV**, on the lab's own 2.1 mg/cm² Ti-T: 4.6×10³ γ/s, 21 IPC pairs/s, and
  **2.0×10³ X17/day into 4π**. That is ~2× the LNL ⁸Be case per µA.
- **The X17 edge is at 112°**, between adjacent and opposite arms. The two-arm acceptance is 38 %. The E1 IPC is
  flat there: **S/B ≈ 1 %** in the 105–160° window, against 7 % at LNL.
- **The backing is the design driver.** The existing target (1 mm Cu) blocks the downstream hemisphere (acceptance
  ×0.25, days ×3.6). A **thin Cu 50 µm backing costs only ×1.2** and carries ~3 µA with rim cooling.
- **Days to 3σ at B_x(ATOMKI)**, 1 µA, Cu 50 µm, calibrated on the LNL Geant4 result:
  - **~39 d with the n_TOF stack as built;**
  - **~2.3 d with the big plastics.**
  - With the existing 1 mm Cu target moved 12 cm downstream: 81 d / 4.7 d.
  - LNL ⁸Be takes 17 d / 1.0 d, so ⁴He is ~2× slower.
- **ATOMKI's fitted IPC is 20–45× below the QED (Born E1) value.** Their own spectra show the X17 excess at ~10× the
  IPC, where B_x per γ predicts ~1 %. If their IPC is right, 3σ takes **~1 d as built and ~1 h with big plastics**.
  MX17 measures the absolute IPC/γ from 40° to 180°, so **the first day of running settles this**, X17 or not
  (`PHYSICS.md` §4).
- **Main risk: systematics at S/B ≈ 1 %.** The LNL 3D fit was validated at 7 %. Redo the template and pseudo-data
  tests for ⁴He before trusting the days.
- **Also at Demokritos:**
  - ⁷Li(p,e⁺e⁻)⁸Be at 1.03–1.1 MeV, which is the LNL case: 17 d / 1.0 d at 1 µA.
  - ¹¹B(p,e⁺e⁻)¹²C, not estimated.
  - PAPAP at 250 keV and ~100 µA: ~0.5 d with big plastics, if it can take a 25 W Ti-T target.

## Geant4 (2026-10-19, `GEANT_PREP.md`)

- Branch `demokritos` of MX17_Full_Geant (commit 4bad297) adds:
  - a TiT film;
  - Mo;
  - `--target-y`.
- 164 jobs were submitted 2026-10-19:
  - D1: X17 m = 16.94 (plus 16.7 and 17.2);
  - D2: E1 IPC above 70°;
  - D3: 20.49 MeV γ for EPC.

  Each runs on Cu 50 µm, Cu 1 mm, and Cu 1 mm at +12 cm, as built and with big plastics.
- Reduce with `sim/lxplus/demok_pipe.sh`, then analyse with `sim/demok_geant.py`.

## Files

| file | what it is |
|---|---|
| `FACILITY.md` | The lab: the 5.5 MV tandem after its 2022 upgrade (Pelletron, TORVIS 100 µA H⁻), beam lines and rooms, the neutron facility and its Ti-T targets, PAPAP, the PAC, contacts, questions to ask |
| `PHYSICS.md` | ³H(p,γ)⁴He: Q, E\*, the 0⁺/0⁻ states, σ (Hahn fit), E1 IPC and E0 pairs, kinematics, ATOMKI's two papers, the IPC puzzle, what a new measurement needs, contaminant lines |
| `ESTIMATES.md` | Yields, the backing and offset scan, the LNL-calibrated reach, PAPAP, the upside if ATOMKI's IPC is right, what is not included, why the neutrons are out |
| `GEANT_PREP.md` | The Geant4 branch, configurations, the D1–D3 run list, reduction and analysis plan |
| `demokritos_rates.py` | The model: kinematics, σ(p,γ), E0 pairs, thick Ti-T yields, the four-arm toy with the backing shadow/scattering and target offset, LNL calibration, reach, mass scan, heat, neutron option → `out/` |
| `out/*.csv`, `out/figures/` | `kinematics`, `excitation`, `yields`, `reach`, `acceptance_hist`, `mass_scan`, `arm_pairs`, `heat`, `neutron_option`, `lnl_calibration.json`; figures `excitation`, `acceptance`, `reach_backing`, `theta_min` (each with its CSV) |
| `sim/lxplus/` | `submit_all.sh` (the campaign) and `demok_pipe.sh` (reduce / time / merge on condor) |
| `refs/*.txt` | Text extractions of the sources: the lab papers (2021 status, 2023 upgrades, the neutron facility, 2026 neutron run), ATOMKI ⁴He 2019 and 2021, the Hahn S-factor fit |

```bash
PY=~/PycharmProjects/nTof_x17/.venv/bin/python
$PY demokritos/demokritos_rates.py          # tables + CHECK lines + figures (~1 min)
$PY demokritos/demokritos_rates.py --quick  # tables only, small MC
```

`demokritos_rates.py` imports `lnl/lnl_rates.py` (Born IPC through nTof_x17 `ipc_born`, stopping, the arm toy) and
reads the LNL Geant4 calibration from `lnl/out/talk/numbers.json` and `lnl/out/yields.csv`.

## Next steps

1. **Geant4 (running).** Reduce, then `sim/demok_geant.py`: acceptance, EPC, cosmics, days per configuration.
2. **Then:**
   - the 3D-fit and pseudo-data test at S/B ≈ 1 %;
   - the γ\* anisotropy;
   - the deck and the site page (`facilities/demokritos.html`).
3. **Emails** (not sent):
   - **A. Lagoyannis** (lagoya@inp.demokritos.gr): the current at 0.9 MeV, thin-backed Ti-T targets, which line and
     room, the PAC dates;
   - **M. Kokkoris / R. Vlastou** (NTUA, n_TOF): to introduce us.
4. **Physics:** ask Viviani *et al.* for the p + t IPC/γ at 0.5–1 MeV. It decides between the two normalisations.
