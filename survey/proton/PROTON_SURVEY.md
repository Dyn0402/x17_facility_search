# Which proton machine could host the MX17 apparatus? A world survey

Started 2026-10-22. Code: `proton_reach.py` (the model), `proton_catalogue.py` (the catalogue and the census).
Outputs: `out/`. Sources: `SOURCES.md`. Raw search notes: `RESEARCH_NOTES.md`.

**Question (Dylan, 2026-10-22).** Do for proton beams what `survey/SURVEY.md` did for neutron beams: find every
facility that could put protons on a ⁷Li, ³H or ¹¹B target in front of the MX17 apparatus, and rank them.

---

## 0. Answer — read this first

1. **Statistics do not pick the proton host. The target does.** The two Geant4 anchors (LNL ⁸Be, Demokritos ⁴He)
   reach the ATOMKI strength at 3σ in 1.0 d / 3.6 d per µA with big plastics, 17 d / 35 d as built. Days fall as
   1/current until the target stops taking beam:
   - a thin film on a thin backing: **~4 µA** (`lnl/target/TARGET_STUDY.md` §5). LNL CN is already there;
   - a water-cooled thick backing moved downstream (Demokritos' trick, ×1.06 in days): **~20 µA** for Li₂O or B,
     ~10 µA for Ti-T. This cap is an **ESTIMATE** (§2.2).

   DREAM is not the limit below ~1 mA (pairs are never prescaled, singles are). So **every machine with ≳ 20 µA DC at
   the right energy gives the same answer: ⁸Be in ~1.3 h with big plastics, ~0.9 d as built**, and the best proton
   machine in the world beats LNL CN by at most ×5 in running time (`out/current_scan.png`).
2. **What separates machines is which claims they can test, and how.**

   | claim | needs | days at the cap (big / as built) | status |
   |---|---|---|---|
   | ⁸Be 18.15 MeV (R = 5.8×10⁻⁶) | 1.03–1.10 MeV, Li₂O | 0.053 / 0.90 | Geant4 (LNL) |
   | ⁴He 20.5–20.8 MeV (B_x = 5.1×10⁻⁶) | 0.9 MeV, **a Ti-T target and a tritium licence** | 0.38 / 3.7 | Geant4 (Demokritos); S/B ≈ 1 %, systematics open |
   | ¹²C 17.23 MeV (B_x = 3.4×10⁻⁶) | ~1.9 MeV (1.5–2.5), ¹¹B | 0.033 / 0.57 | **ESTIMATE** scaled from ⁸Be (§1.3), ×2 either way |

   ¹²C may be the fastest of the three (×1.6 faster than ⁸Be per µA) because the broad 17.23 MeV resonance and a thick
   ¹¹B target give ×9 the γ₀ of the ⁸Be target. Nobody but ATOMKI has measured it. It wants a Geant4 run.
3. **Catalogue: 60 named machines + a census of 267 electrostatic accelerators** (IAEA list, §5).

   | verdict | named rows | meaning |
   |---|---|---|
   | STUDIED | 2 | LNL, Demokritos |
   | **POTENTIAL** | **7** | LUNA-MV, Felsenkeller, JRC MONNET, PTB PIAF, TUNL LENA, Notre Dame 5U, iThemba Tandetron |
   | X17 LAB | 6 | ATOMKI, PSI MEG II, Hanoi, Montréal, IEAP Prague, Melbourne: their own X17 experiments |
   | MARGINAL | 30 | ⁸Be at LNL-like currents, or the current is unpublished |
   | WATCH | 3 | NPL (new 2 MV Tandetron, ≥ 300 µA, T heritage), FRANZ (¹²C only), CASPAR (moving) |
   | ENERGY / CURRENT / ACCESS | 7 / 1 / 4 | ≤ 400 kV (LUNA 400, JUNA), fixed-energy BNCT/RFQ, Cologne FN; BINP VITA, hospitals, defence |

4. **The shortlist, in order of what each adds over LNL:**
   1. **LNGS Bellotti IBF (LUNA-MV)**: 3.5 MV Singletron, 1 mA H⁺ over 0.3–3.5 MeV, a user facility since 2023,
      1400 m of rock. Every claim at the cap, and **no cosmics**: the as-built stack needs neither the 3° MM segments
      nor TOF, which LNL found are the only thing that can sink it (`lnl/FEASIBILITY_SIM.md` §0.3). Already named for
      ³H(p,e⁺e⁻) in the 2023 X17 community report; our collaboration (Gustavino) is in LUNA. Ask: tritium at LNGS,
      hall space, beam time.
   2. **JRC Geel MONNET**: 3.5 MV tandem, 100 µA DC, Ti-T and ⁷Li targets routine, open EUFRAT calls. The easiest
      route to **⁴He at 10 µA (0.4 d)**: the tritium problem is already solved there.
   3. **Felsenkeller (HZDR)**: 5 MV Pelletron with a terminal RF source (tens of µA), 45 m of rock (muons ÷40),
      free ChETEC/EURO-LABS beam time.
   4. **PTB PIAF**, **NPL** (when running): metrology labs with Ti-T and big open halls.
   5. **TUNL LENA (2 MV Singletron, mA)** and **Notre Dame 5U**: US nuclear-astrophysics machines built for exactly
      this kind of (p,γ) work. **iThemba LABS**: a 200 µA Tandetron with an astrophysics line.
5. **ATOMKI itself** has every ingredient (200 µA Tandetron, tritium, boron, the claims) and our µRWELL demonstrator
   was already beam-tested there. It is classed X17 LAB, not POTENTIAL, because it is the lab being checked: a run there
   is a joint measurement, which is a choice for the collaboration (§6).
6. **For the paper:** the proton route is limited by the target and by systematics, not by the beam. The MX17 3D fit
   (θ × |y| × E_sum) is what makes a 3σ test in hours meaningful; the open systematic is ⁴He at S/B ≈ 1 %.

**Next (§7):** a Geant4 ¹¹B(p,γ)¹²C run (the ESTIMATE in §1.3); a thick-cooled-backing target run to fix the 20 µA cap;
emails to LNGS (tritium, space), JRC (EUFRAT call) and Felsenkeller.

---

## 1. Method

### 1.1 The figure of merit

The neutron survey quotes X17/IPC reached in 50 days. The proton studies quote **beam days to 3σ at the ATOMKI
strength** (LNL: R = 5.8×10⁻⁶ in Γ_X/Γ_γ; Demokritos: B_x = 5.1×10⁻⁶), from Fisher fits of the full event lists. This
survey keeps the proton convention, since R and B_x are not X17/IPC. The dashboard also shows the "50-day reach in
units of the ATOMKI strength", √(days/50), which falls as 1/√T like the neutron reach.

All days are statistics only (the calibrated fits, MM 15° + TOF), with no setup or beam-off time, no systematic floor.

### 1.2 The anchors

| claim | anchor | days at 1 µA (big / as built) | where |
|---|---|---|---|
| ⁸Be | LNL Geant4: Li₂O 300 µg/cm² on 10 µm Al, 1.10 MeV, 3D fit, calibrated response, m = 16.7 | 1.00 / 17.0 | `lnl/FEASIBILITY_SIM.md` §15 |
| ⁴He | Demokritos Geant4: the lab's 2.1 mg/cm² Ti-T on 1 mm Cu moved 12 cm downstream, θ × \|y\| fit | 3.6 / 35 | `demokritos/ESTIMATES.md` §6.2 |
| ¹²C | ESTIMATE from ⁸Be (§1.3) | 0.63 / 10.7 | `proton_reach.py` |

### 1.3 ¹²C, scaled (ESTIMATE until Geant4)

- The 17.23 MeV 1⁻ state: E_p,res = 1.388 MeV, Γ = 1.15 MeV, Γ_p = 1 MeV, Γ_γ0 = 44 eV (NNDC, 1965Se06). The
  Breit-Wigner peak is σ(p,γ₀) ≈ 28 µb; 25 µb over ATOMKI's 300 keV-thick target.
- ATOMKI's 2 mg/cm² ¹¹B (on 5 µm Ta, 2 µA, ~50 h per energy, E_p = 1.5–2.5 MeV; PRC 106 L061601) gives
  **1.7×10⁴ γ₀/s per µA**, against 1.85×10³ for the ⁸Be anchor target.
- Fisher days ∝ 1/(N_γ B_x²) at the same S/B shape: (1.85×10³ / 1.7×10⁴) × (5.8 / 3.4)² = 0.32.
- κ = 2 (range 1–4) for the E1 IPC shape near the X17 angle (150–160° for ¹²C, ~140° for ⁸Be) and the thicker
  target. So **¹²C days = 0.63 × ⁸Be days**.
- X17 produced: 5.0×10³/day per µA into 4π (⁸Be: 920; ⁴He: 2.0×10³).
- No neutrons below the ¹¹B(p,n) threshold at 3.02 MeV. The ¹¹B(p,α) α flux stops in the chamber.

## 2. The apparatus caps the current

### 2.1 DREAM

From the LNL trigger study (`lnl/FEASIBILITY_SIM.md` §14.1): arm legs/s = 88 + 65·I (big plastics) and pair
triggers/s = 22 + 0.29·I, with I in µA. Pairs are never prescaled; singles are prescaled to 20/s. Live time
1/(1 + fτ), τ = 298 µs, is 0.988 at 1 µA and 0.986 at 20 µA. It only matters near 1 mA (live 0.91). Accidentals grow as
I² (0.02/day at 1 µA, 8/day at 20 µA, against ~3×10⁴ IPC/day in the window): negligible. MM occupancy from the
478 keV ⁷Li line at 20 µA is ~10⁻³ (rough, not modelled).

### 2.2 The target

- Thin film on a thin backing (the Geant4 baseline): ~4 µA (TARGET_STUDY §5: edge-clamped 10 µm Al ≤ 2 µA,
  graphite/Cu to 4 µA).
- Water-cooled thick backing moved downstream: Demokritos showed that 1 mm Cu at +12 cm costs ×1.06 in days with
  big plastics. 20 µA at 1 MeV is 20 W, easy to cool. What stops it is the hydrogen fluence (blistering of the
  backing, film loss: ~4×10¹⁹ /cm² per day at 20 µA on σ = 2 mm) and, for Ti-T, tritium release. Wobbling or
  rotating the target spreads that. **CAP = 20 µA (Li₂O, B), 10 µA (Ti-T) is an ESTIMATE**, not a measurement.
  At 100 µA everything POTENTIAL gains another ×5; at 4 µA nothing beats LNL CN.

So the reach curve (`out/current_scan.png`) is flat above the cap. The MeV-class mA machines (LUNA-MV, TUNL LENA,
BINP VITA, BNCT accelerators) buy nothing extra in statistics; they buy a wide energy range and margin.

## 3. Classes

| class | examples | what decides it |
|---|---|---|
| underground | LUNA-MV, Felsenkeller; LUNA 400, JUNA, CASPAR | energy (≤ 400 kV machines miss 441 keV and 1.03 MeV); no cosmics |
| neutron metrology | JRC MONNET, PTB, NPL, AMANDE, Tohoku, AIST | Ti-T targets and licences already in place |
| high-current single-ended | TUNL LENA, Notre Dame 5U, Bochum | mA-class DC in the right range |
| Tandetron (HVEE) | ATOMKI, iThemba, HZDR, IFIN, CMAM, Surrey... | 10–200 µA at 2–3 MV terminal; at 0.5 MV terminal (ask) |
| Pelletron tandem (IBA/AMS) | Uppsala, CNA, CIRCE, Helsinki, IUAC... | ~1 µA protons; LNL-AN2000-like |
| BNCT / RFQ | Birmingham, Nagoya, Helsinki nuBeam, CNAO, FRANZ, SARAF | fixed 1.9–2.8 MeV energy; hospitals |
| large tandem / cyclotron | Cologne FN, ANU 14UD, NPI TR-24 | minimum energy too high, nA protons |

## 4. Verdicts

`proton_catalogue.py` header. POTENTIAL needs a known ≥ 10 µA DC at 0.9–1.9 MeV, a route to beam time, and either a
gain over LNL (current past the 4 µA thin-target limit) or a claim LNL cannot test. MARGINAL rows mostly have an
unpublished current; a class default stands in (Tandetron 10 µA, single-ended 10 µA, Pelletron tandem 1 µA; ESTIMATE,
marked * in `out/ranking.png`). Tandems' lowest usable energy (terminal at 0.45–0.55 MV) is **(ask)** everywhere.

## 5. The census

The IAEA Accelerator Knowledge Portal list (read 2026-10-22 through its public SharePoint API; mostly 2015 entries,
`iaea_electrostatic.csv`) has 267 electrostatic machines. By class (`out/census.csv`):

| class | n | verdict |
|---|---|---|
| tandem ≤ 6 MV | 132 | MARGINAL |
| single-ended ≤ 7 MV | 44 | MARGINAL |
| AMS / dating | 40 | CURRENT |
| large tandem ≥ 7 MV | 27 | ENERGY |
| ≤ 0.55 MV | 12 | ENERGY |
| no voltage given | 12 | — |

So ~180 machines in the world can test ⁸Be at LNL-like currents. That is the point: the proton route is not short of
hosts. The named rows are those with a published current, a reason to stand out, or an X17 program.

## 6. Labs with their own X17 experiments

| lab | machine | experiment | state (Oct 2026) |
|---|---|---|---|
| ATOMKI | 2 MV Tandetron (200 µA), 5 MV VdG | the claims; new DSSD and E-θ spectrometers | 2023 run analysis "in its last phase" (2025) |
| PSI | 1 MV CW in MEG II | MEG II | null: R(18.1) < 1.2×10⁻⁵, R(17.6) < 1.8×10⁻⁶ (EPJC 85 763, 2025) |
| VNU Hanoi | 1.7 MV Pelletron | two-arm spectrometer with ATOMKI | confirmed the 18.15 excess (Universe 10 168, 2024) |
| Montréal | 6 MV tandem, 2–10 µA | MWPC + DAPHNE bars | set up 2022–24; no result found |
| IEAP CTU Prague | 2.5 MV VdG | TPC + Timepix3 spectrometer | under construction |
| Melbourne | 5 MV Pelletron, 2 µA | TPC proposal | proposed 2023 |
| LNL | AN2000 | Aipac8Be (LiF, 2023–24) | no result (see `lnl/target/`) |

## 7. Open questions and next steps

1. Geant4: ¹¹B(p,γ)¹²C at 1.88 MeV on the `lnl` branch (thick ¹¹B on Ta or C, cooled, downstream), to replace §1.3.
2. Geant4/bench: a cooled thick backing at 20–100 µA, to fix the cap (§2.2).
3. Ask LNGS: tritium (Ti-T) underground, hall space for a 1.6 m apparatus, beam-time cycle. Ask JRC: EUFRAT call,
   the lowest proton energy of the tandem. Ask Felsenkeller: proton current from the terminal source.
4. Tandem low-energy transmission at 0.45–0.55 MV terminal for every Tandetron on the list.
5. Not modelled: room background at each site, MM occupancy from the 478 keV line at high current.
