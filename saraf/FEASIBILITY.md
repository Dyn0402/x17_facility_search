# SARAF (Soreq) — X17 feasibility with the shared Geant4 soft-beam background

Facility record: `FACILITY.md`. Slides (built, not published): `out/saraf-x17-feasibility.html` (`deck/build_deck.py`).
Beam model and reach: `saraf_beam.py`. Engine: `survey/soft_sim/soft_reach.py` (imported, plus `bepn_reach.py`'s N4 extension above 20 MeV).

## 0. Answer — 2026-11-09

**Overall call: WATCH.** The physics is better than the catalogue said, the machine is not there.

**What the catalogue got right and wrong.** The catalogue's near-threshold LiLiT row (6.7×10⁻³) was the wrong operating point. With the
measured LiLiT yield and the same reasoning as `franz/`, LiLiT as it actually ran (1.925 MeV, 1.5 mA, cell at 0.5 m) gives **3.8×10⁻³**
(×2.5 short of ATOMKI), a bit better than the catalogue but still short. **The lever the catalogue did not try is the proton energy:** LiLiT is a thick
stopping jet, and raising E_p from 1.925 MeV to 2.6–4 MeV raises the yield ×40–100 for the same 4 kW linac power, with every neutron still ≤ 2.3 MeV (inside
the ATOMKI window).

**Best honest configuration:** thick liquid Li at **E_p = 4 MeV, 1 mA CW (4 kW, the demonstrated linac/target power), cell 1 m downstream, 30 bar × 40 cm:**
**X17/IPC = 3.5×10⁻⁴ at 3σ in 50 days (big plastics; as built 9.8×10⁻⁴), 2.6 days of beam to the ATOMKI strength (as built: 21 d).** Statistics-limited (IPC + cosmics), DREAM live
> 0.99. Equal to Birmingham's engine value (3.3×10⁻⁴). **All E\* and E\* ≤ 22 MeV are the same: every neutron is in the window.** Close the distance to 0.5 m: 1.6×10⁻⁴;
but 0.5 m needs ~50 cm of borated PE around a 4π MeV field and does not leave room for it. Birmingham's full-room Geant4 moved it from 3.3×10⁻⁴ to 5.5×10⁻⁴; apply the same ×1.7 here and SARAF at 1 m is ~6×10⁻⁴ (ESTIMATE).

**With Phase II's 5 mA on a jet good for ≥ 20 kW** (not demonstrated; a 50 kW Li design exists on paper): 1.5×10⁻⁴ at 1 m (as built 3.8×10⁻⁴), under a day to ATOMKI.

**Why it stays WATCH.** No beam exists today that could do this: the Phase I linac (the machine that delivered 1.9–4 MeV protons) has been converted to Phase II, and Phase II had only its first
cryomodule installed with commissioning "ongoing" in October 2025. No report of beam through it was found. There is no user programme, no transnational access, and the site is a nuclear research centre in an active conflict zone.

| 50 d, E\* ≤ 22 MeV, cell 1 m: big plastics (as built) | E_p 1.925 | 2.2 | 2.6 | 3.0 | **4.0 MeV** |
|---|---|---|---|---|---|
| Li jet, ≤ 4 kW (2 mA → 1 mA; Phase I class) | 9.6×10⁻³ | 1.1×10⁻³ (3.7×10⁻³) | 5.5×10⁻⁴ (1.7×10⁻³) | 4.5×10⁻⁴ (1.4×10⁻³) | **3.5×10⁻⁴** (9.8×10⁻⁴) |
| Li jet, 5 mA (≥ 10–20 kW, not demonstrated) | 4.4×10⁻³ | 5.6×10⁻⁴ | 2.7×10⁻⁴ (7.6×10⁻⁴) | 2.1×10⁻⁴ | **1.5×10⁻⁴** (3.8×10⁻⁴) |

| Other | reach, 1 m, big plastics (as built) | note |
|---|---|---|
| LiLiT as ran (1.925 MeV, 1.5 mA) at 0.5 m / 0.3 m | 3.8×10⁻³ / 1.8×10⁻³ | as built 1.2×10⁻² / 4.6×10⁻³; the near-threshold cone is not enough |
| p + thick Be, 4 MeV, 1 mA / 5 mA | 5.7×10⁻⁴ / 2.2×10⁻⁴ | no ⁸Be γ; 100 % of neutrons in the window; ESTIMATE (ENDF extrapolation) |
| p + Be, 8 MeV, 5 mA, 130° | 2.0×10⁻⁴ (throttled to 0.63) | DREAM-limited; 40 kW on Be: no such target planned |
| p + Be, 18 MeV, 5 mA, 0° | 8.7×10⁻⁴ (throttled 0.03) | reproduces NPI Řež 18 MeV: current does not help a hard spectrum |
| d + Be, 5 MeV, 1 mA / 5 mA | 8.0×10⁻⁴ / 3.3×10⁻⁴ | ESTIMATE ×3: Serber model extrapolated to 5 MeV, γ a stand-in |
| d + Be, 10 / 20 MeV, 5 mA, 0° | 1.0×10⁻³ / 6.6×10⁻³ | hardening fast |
| d + Be, 40 MeV, 5 mA, 0° | **0.11 (E\* ≤ 22); 4.9×10⁻³ (all E\*)** | throttle 5×10⁻⁴: confirms "≈ NFS" |

Limiting walls: statistics (IPC + cosmics floor) for every Li row up to 4 MeV, 1 m; DREAM dead time for p+Be above 5 MeV and all d+Be above ~10 MeV (throttled, live ≈ 0.4–0.6).
A cosmic veto would remove about a third of the background at this rate (cosmics 5 300 vs IPC 10 640 per day in the window).

## 1. Beam model — 2026-11-09

`saraf_beam.py` → `out/saraf_beam.csv`, `out/saraf_spectra.{csv,png}`, `out/saraf_yield_check.csv`.

**Engine check (done first).** `python saraf/saraf_beam.py --check` reproduces two published rows with the shared engine: Birmingham `bham_28_2m_pb5` 3.32×10⁻⁴ (ratio 0.9999) and FRANZ
design 2.0 MeV 0.5 m 3.31×10⁻⁴ (ratio 1.0001). The engine handles the keV spectrum identically to franz_beam.py: same N5 re-weighting, same `Soft` construction; the 0° keV spectrum is above N5's 1 keV lower limit (`saraf_beam.csv`, f_below_1keV ≈ 0).

**LiLiT family** (thick liquid Li): the `franz`/`bham` slowing-down MC (CM isotropic; σ(E_p) from Birmingham's table, extended flat to 4.5 MeV: **ESTIMATE**; ⁷Li(p,n₁) channel
not modelled, conservative for 0° at E_p ≥ 2.4 MeV) with the absolute scale **set by the measured LiLiT yield 2.5×10¹⁰ n/s/mA at 1.925 MeV** (FACILITY.md §1.2). Check: the same normalisation gives 1.07×10¹² n/s/mA at 2.6 MeV,
Birmingham's facility number is 1.0×10¹² (ratio 1.07), and the absolute σ/S gives 1.9×10¹⁰ at 1.925 MeV (×1.3).

| E_p | n/s/mA (4π) | 0° n/s/sr/mA | mean/max E_n at 0° | n through Ø8 cm at 1 m, 1 mA |
|---|---|---|---|---|
| 1.925 (as ran) | 2.5×10¹⁰ | 1.1×10¹⁰ | 90 / 130 keV | 5.6×10⁷ /s |
| 2.6 | 1.07×10¹² | 1.7×10¹¹ | 0.49 / 0.89 MeV | 8.5×10⁸ |
| 4.0 | 2.9×10¹² | 3.9×10¹¹ | 1.13 / 2.32 MeV | 1.9×10⁹ |

**⁸Be γ:** the same measured LiLiT value applies to all E_p ≥ 1.9 MeV, 7×10⁸ γ/s/mA (17.6:14.6 MeV = 3:4; arXiv:1511.04701): the Birmingham stand-in of 1×10⁻⁷ γ/p, now measured at the actual target.
A thin Li option does not exist at LiLiT (a 1.5 mm jet stops the protons; it would need a new target like FRANZ's).

**p + Be** (`bepn_cyclotron/bepn_beam.py`, ENDF/B-VIII.0 LA150, verified there at 16–30 MeV; **ESTIMATE** below 8 MeV): at 4 MeV 1.1×10¹² n/s/mA, all ≤ 2.16 MeV.

**d + Be** (`ganil_nfs/nfs_beam.py`, Serber + Watt, anchored to the measured NFS flux at 40 MeV; **ESTIMATE**, order of magnitude at E_d = 5 MeV). Total yields: 7×10¹¹ n/s/mA at 5 MeV, 1.0×10¹⁴ n/s/mA at 40 MeV (5 mA: 5×10¹⁴, cf. Mardor's 10¹⁵ n/s). Mardor's Table 5 d-on-Li row at 5 MeV is 10¹³ n/s at 2 mA with a 0.03–20 MeV spectrum. γ: 1 γ per neutron stand-in. Meadows' measured thick-target tables (2.6–7 MeV, OSTI 5796157) were not retrievable; they would replace this.

## 2. The options — 2026-11-09

Every row uses `SR.components` / `SR.at_throttle` at 1 mA, 1 m, then scales with I·Ω (throttle s ∈ [10⁻⁴, 1]); `out/saraf_reach.csv` has both hardware sets, 14 and 50 days, E\* ≤ 22 and all E\*.

- **Near threshold (the catalogue's point).** Confirmed negative: the 64° forward cone is a real gain (×~6 at 0° over 4π) but 2.5×10¹⁰ n/s/mA is too few neutrons.
  3.8×10⁻³ (0.5 m), 1.8×10⁻³ (0.3 m, ×1.2 short). 325 days of beam at 0.5 m to the ATOMKI strength.
- **Higher E_p on the same jet: the thing that changes the answer.** Phase I delivered "1 mA, ~4 MeV or 1.5–2 mA at 2 MeV (3–4 kW)" (Paul 2021), and the target handled that power at 1.9 MeV.
  Above ~2.4 MeV the ⁷Li(p,n) cross-section is high and every proton goes through the full range; yield rises ×40 by 2.6 MeV and ×100 by 4 MeV at equal power.
  Reach: 1.1×10⁻³ at 2.2 MeV already passes ATOMKI at 1 m; 5.5×10⁻⁴ at 2.6; 3.5×10⁻⁴ at 4. Birmingham-class spectrum and, at 4 MeV, comparable reach for 1/30 the current.
  **Caveat:** whether the LiLiT jet tolerates a 4 MeV beam (Bragg peak deeper, power density different) is untested. **(ask)**
- **Pb filter.** Thick Li's ⁸Be γ costs little here: correlated 3.5 % of IPC at 4 MeV. 5 cm Pb hurts (keV → MeV neutrons lose too): 4 MeV, 1 m: 6.3×10⁻⁴ vs 3.5×10⁻⁴. Not used.
- **Distance.** 0.3 m (1.0×10⁻⁴) and 0.5 m (1.6×10⁻⁴) are in the table, but the source is a 4π ~1 MeV field: see §3. 1 m is the honest headline.
- **Throttle.** Not needed for Li at ≤ 4 kW (live > 0.9); at 5 mA and 0.3 m, DREAM begins to bite (live 0.44).
- **Current.** Reach ∝ 1/√I while statistics-limited: 5 mA gains ×2.2. A 50 kW target design (EPJ WoC 2020) would not be needed.
- **Solid Be at 4 MeV:** 5.7×10⁻⁴ at 1 mA, 2.2×10⁻⁴ at 5 mA, with the ⁸Be γ gone (correlated = 0 in the sample). Be handles 4 kW easily. This is an alternative if LiLiT is not available, but the yield at 4 MeV is an ENDF extrapolation. A Be target gives ~9×10⁹ γ/s/mA (ENDF, above 2.7 MeV); included in the re-weighting; the 4 kW Be target is the standard form.
- **p + Be at higher energy** with SARAF's 5 mA: 8 MeV at 130° gets 2.0×10⁻⁴ (throttled to 0.63), better than the NPI 18 MeV row, but needs a 40 kW Be target (no such station planned). At E_p = 18 MeV the throttle is 0.03: SARAF's extra current is thrown away, and the reach (8.7×10⁻⁴) reproduces NPI's.
- **d(5) + Be** (Phase I-class deuterons): 8.0×10⁻⁴ at 1 m, 1 mA. Interesting, but ESTIMATE; the model's tail to 14 MeV is an artefact of the extrapolation, and the true d+Be 5 MeV spectrum would decide. d + Li at 5 MeV: Mardor's 0.03–20 MeV spectrum is too hard.
- **D-D:** SARAF's minimum d energy is 2.6 MeV; at 0° that gives E_n ~5.5–6 MeV, outside the window; to get E_n ≤ 2.75 needs > 90°. A mA-class gas or TiD target at low yield (~10⁹–10¹⁰ n/s/sr per mA, ESTIMATE) is not competitive. Not modelled further.
- **Phase II d(40) 5 mA at 0°:** 0.11 (E\* ≤ 22), 4.9×10⁻³ all E\*: 0.05 % of the current is usable (throttle 5×10⁻⁴); a real but useless beam for this signal, as the catalogue said ("≈ NFS"). Backward angle 130°: 1.2×10⁻³. A lower deuteron energy (20 MeV, 130°): 5.3×10⁻⁴, ESTIMATE.
  **So Phase II's value for MX17 is its low-energy range (2–8 MeV p, ≥ 1 mA), not the 40 MeV that defines it.** A filter cannot rescue it: Fe/Al windows do not remove > 3 MeV neutrons without removing the ones we want.
- **Cell.** Only the 30 bar × 40 cm NFS-style cell is in the engine. The n_TOF capsule (500 bar) is not in N5; with a spot and vessel not modelled here, the higher areal density is offset by angular resolution
  (σ68(Δθ) ≈ 14.5°) and not attempted. Not a decision point for SARAF.

## 3. The field around the target — 2026-11-09 (estimate, not Geant4)

`out/saraf_shield.csv`, the Birmingham `shield()` estimate (10 cm TVL of borated PE at ~1 MeV, stand-in). At 1 m, 1 mA, 4 MeV: one arm would see 2×10¹¹ n/s unshielded. Keeping leakage singles below 10 % of the beam's own (ε = 10⁻⁵–10⁻⁴ singles per entering n) takes **48–58 cm of borated PE** around the target and between target and arms.
At 0.5 m there is no room for this. At 1.925 MeV (kinematic cone; 5 cm TVL) only ~21–26 cm is needed. The 2013–17 LiLiT flux was itself limited by the corridor shielding (Mardor 2018): a 1–2 MeV, 10¹² n/s source needs a real target room.
**The Birmingham full-Geant4 lesson (TARGET_GEANT.md) applies: room return and wall leakage set the DREAM rate, moved 3.3→5.5×10⁻⁴.** No equivalent run exists for SARAF.

## 4. Scorecard — 2026-11-09

| question | answer | evidence |
|---|---|---|
| Beam exists today? | **No.** Phase I linac converted; Phase II commissioning | arXiv:2211.16774; LCWS2025: CM1 installed, "commissioning ongoing" (Oct 2025) |
| Time to first beam | unknown, earliest a few years **(ask)** | slipped 2018 → 2023 → 2025 → open |
| Neutrons at 2–4 MeV p, ≥ 1 mA? | needs CM1 tuned low + LiLiT re-installed + a neutron room | no public plan found; LiLiT 2 mentioned (Paul 2021) |
| Access for our group | no user programme or TNA; Soreq is an IAEC centre; site rules **(ask)** | FACILITY.md §3 |
| Space / shield | Phase I target room dimensions **(ask)**; ~50 cm borated PE needed at 1 m | §3; corridor limit 2013–17 |
| Cost | rough: shielding + flight tube + He cell + operations ~€100–300 k ESTIMATE; no machine costs | same as Birmingham-class installation |
| Radiation safety | Li jet + ⁷Be inventory (53 d), neutron field in a Soreq room; a site licence for the apparatus **(ask)** | §3; ⁷Be activity = one per neutron, ~3 TBq at saturation at 1 mA, 4 MeV (Birmingham 6 TBq) |
| ³He target issues | cell at 30 bar inside a nuclear-site experimental room; ³He transport **(ask)** | FACILITY.md §3 |
| Competition for beam | Phase II primary programmes: medical isotopes, thermal source, fission products; X17 would be a guest | Mardor 2018 |
| Access restriction (fact) | Israel (active conflict; Iranian strikes on Dimona 2026-03-21); commissioning reported as complicated by events | LINAC 2024; PBS 2026-03-21 |

**Compared with:** Birmingham (5.5×10⁻⁴, 6.7 d, full Geant4; operating, needs a port), FRM II MEDAPP (4.2×10⁻⁴ engine; reactor off) and FRANZ (3.3×10⁻⁴ design, 2 MeV not reported). SARAF at 1 m ~ Birmingham's reach on paper, but with no beam.

## 5. What would have to be true for top-3

1. Phase II's first cryomodule delivers **2–5 MeV protons at ≥ 1 mA CW** (Phase II design range: 1.3–35 MeV) and SNRC wants to run it.
2. **LiLiT (or a Be converter) is re-installed** in a room with a 0° path of ≥ 1 m and space for a borated-PE shield, and the jet is tested at ≥ 2.6 MeV.
3. Practical access for an external group: site rules, ³He, and the security situation allow a multi-week run.
Each of 1–3 is **(ask)**. Item 3 is outside physics.

## 6. Next steps (none done; nothing submitted)

- If Dylan wants this followed up: ask L. Weissman / I. Mardor / M. Paul whether CM1 can give ≥ 1 mA at 2–5 MeV p, whether LiLiT will be re-installed, and whether external X17-style experiments are possible at all.
- A Geant4 run (not submitted): `bham`-style `--room` geometry with a thick-Li source at E_p = 4 MeV, cell at 1 m, 50 cm BPE, SARAF room dimensions; or the Birmingham room re-used with this source to convert the ×1.7 ESTIMATE into a result.
- Replace the d+Be 5 MeV stand-in by Meadows' table (OSTI 5796157) if d(5) becomes relevant.

## 7. What is not settled

Room, shield, target chamber, parallel gun at ≤ 1 m (the spot subtends more at short distance), σ(E_p) above 3 MeV, ⁷Li(p,n₁), CM anisotropy above 2.3 MeV (would raise the 0° yield), LiLiT at ≥ 2 MeV, Micromegas occupancy from the 478 keV/⁷Be flood (not in the model), and the 5 MeV d+Be spectrum (ESTIMATE).
