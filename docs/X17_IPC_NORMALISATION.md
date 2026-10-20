# X17/IPC: the 2.5×10⁻² rate-table value against ATOMKI's 1.5×10⁻³

*2026-10-20.* Records why the facility survey and its dashboard use **X17/IPC = 1.5×10⁻³** and
not the 2.5×10⁻² found in the older n_TOF numbers, and what is still open.

## 1. The two values

| value | where it is used | source |
|---|---|---|
| **2.5×10⁻²** ("the project benchmark") | header of the December 2025 n_TOF rate table (`nTof_x17/mpgd26/data/x17_rate_3He.txt`, original `/media/dylan/data/x17/calculation_tables/results_3He`); `nTof_x17/MX17_Simulation/{dead_time_sim,MX17_Simulator}.py` (`X17_FRACTION_OF_IPC`, first in commit 5439e45, 2026-05-27); the mpgd26 and Athens figures; the ILL deck's "reference ratio" | **none found.** The rate table states it with no citation; every later copy repeats the header. The code that made the table is not in any repo (the table seems to come from Alberto's calculation: the same block of `MX17_Simulator.py` cites "Alberto scaled down…"; unconfirmed). |
| **1.5×10⁻³** | `survey/` (dashboard, catalogue, fast and thermal reach), `ganil_nfs/` | ATOMKI ⁴He, Krasznahorkay et al., PRC **104** (2021) 044003: B_x = 5.1(13)×10⁻⁶, ÷ α_IPC ≈ 3.5×10⁻³ |

Cross-check from ⁸Be: Γ_X/Γ_γ = 5.8×10⁻⁶ at 18.15 MeV, ÷ α_IPC(M1) gives 1.6×10⁻³ (the ILL
"⁸Be level"). Pessimistic end (B_x at −1σ, α_IPC = 4.5×10⁻³): 8.4×10⁻⁴ ≈ 1×10⁻³, the working value
of `docs/PLAN_GANIL_NFS.md` §1.3 (decision of 2026-09-09).

The rate-table value is **×17 above** the ATOMKI-derived one (×30 above the pessimistic one).

## 2. What 2.5×10⁻² probably is (unverified)

A quantity other than X17 per IPC pair over the whole spectrum. Two candidates:

1. **The signal fraction inside an angular window.** Near 115–140° the IPC opening-angle
   spectrum has fallen steeply, so ATOMKI's excess is percents of the *local* pair counts while
   being ~10⁻³ of all pairs. Reading a ratio off an ATOMKI angular plot gives percents.
   PLAN_GANIL_NFS §1.3 already suspects this.
2. **A ratio to a single pair branch.** The 2019 ⁴He paper (arXiv:1910.10459) normalised to the E0
   transition of the 20.21 MeV 0⁺ state (from memory; not checked against the paper). A ratio to
   one small branch is much larger than a ratio to all IPC.

Either way, 2.5×10⁻² applied per IPC pair over the full spectrum overstates the signal ~17×.

## 3. Numbers that carry the 2.5×10⁻² and are therefore ~17× optimistic

- The rate table's **42 X17/day** at n_TOF EAR2 (production in the old Ø4 cm sphere, no
  acceptance). At 1.5×10⁻³ it is **2.5/day**.
- `MX17_Simulator.py` / `dead_time_sim.py` X17 rates and significances.
- The mpgd26 and Athens rate figures (they use the table only for ratios between windows, which
  the normalisation does not affect).
- `demokritos/neutron/`: 22.5 X17/day at n_TOF EAR2, 0.2–2 MeV (it converts back to IPC pairs,
  so the ranking there is unaffected).

## 4. The same comparison for the dashboard's n_TOF row

The dashboard (`survey/dashboard.py`) gives 7.7 X17/day for EAR2: 7.0×10⁶ n/s on the Ø2 cm capsule
face × ⟨P⟩ = 8.4×10⁻⁹ IPC pairs per entering neutron × 1.5×10⁻³ × 86400, so 5,100 IPC pairs/day.
The rate table has 1,690 IPC pairs/day. Factor by factor:

| | rate table | dashboard | ratio |
|---|---|---|---|
| X17/IPC | 2.5×10⁻² | 1.5×10⁻³ | ÷16.7 |
| ³He areal density | 0.032 at/b (Ø4 cm sphere) | 0.099 at/b (500 bar × 8 cm) | ×3.1 |
| pairs per capture | 2.1×10⁻³ | 4.9×10⁻³ (Born E1 at W) | ×2.3 |
| captures/n per at/b (spectrum) | measured EAR2 (50 % in 0.1–10 MeV) | isolethargic stand-in (25 %) | ÷2.3 |
| neutrons/pulse on the cell | 3.3×10⁷ | 3.1×10⁷ | ≈1 |

Two known approximations in the dashboard, both open:
- `survey_yield.CELLS` takes the capsule as 8 cm long; the Geant4 bore (`SimConfig.hh`
  `he3_half_length_cm = 2.0`, r = 1 cm hemispherical caps) averages ~5.3 cm along the beam. This
  overstates every fast facility ×1.5 against the thermal ones.
- n_TOF is folded with the isolethargic stand-in; the measured EAR2 spectrum of the rate table
  gives 12/day at 8 cm and 8.4/day at 5.3 cm.

Neither number includes acceptance, trigger or dead time.

## 5. Open

- Ask the author of the rate table what the 2.5 % is relative to.
- Pull PRC 104 044003 and the 2019 ⁴He paper into `survey/refs/` and confirm what B_x is
  normalised to (PLAN_GANIL_NFS §1.3, "deferred").
- Until then: **1.5×10⁻³ everywhere in this repo**; 2.5×10⁻² only ever as a labelled reference.
