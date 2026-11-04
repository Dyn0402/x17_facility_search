# Pierfrancesco's ogive in Al, with a Cu liner where the beam stops

Started 2026-11-04. Dylan asked (4 Nov) for a careful study of a compromise between Pierfrancesco's
**Cu ogive** (cheap and simple, but every lepton crosses 200 µm of Cu: σ68 18.5°, 0.95 d/µA) and the **Al ogive
with a Mo liner** (σ68 10.5°, 0.26 d/µA, but it needs 8 µm of Mo sputtered into a 63 mm deep cone, and the Mo K x-rays
reach the Micromegas). The idea: make the shell Al, and put Cu only where the beam stops. Where must the Cu go, how
thick, how do we put it there, and what does it cost us?

Slides: note **`lnl-cu-liner`** (`deck/build_culiner_deck.py`, https://dylan-neff.web.cern.ch/notes/lnl-cu-liner.html).
Code: `opt_cu_liner.py` (analytic, ESTIMATE) → `out/target/options/culiner_*.csv`; Geant4 run **L12**
(MX17_Full_Geant branch `lnl_culiner`, `shapes/lxplus/l12_*.sh`) through `shapes/shapes_geant.py` and
`shapes/shapes_rates.py`; the PIXE yields from a Geant4 TestEm5 check (`out/target/options/pixe_testem5.csv`).

## 0. Bottom line (2026-11-04)

**The design to send back:** his ogive, unchanged in shape, made of **Al 6061-T6 with a 0.35–0.4 mm wall**, with
**≥ 12 µm of Cu (measured along the beam) over the tip region, r ≤ 8–10 mm**, and **20 µm of Li (along the beam)
evaporated from the axis through a mask r ≤ 4 mm**. Cu and Li both laid down by line of sight from a source on the
beam axis, through the open base, in one vacuum system.

| big plastics, 3σ at ATOMKI | σ68 | days per µA, 1.10 / 1.03 MeV | EPC share | legs/s per µA (DREAM) | MM x-ray occupancy per arm per µA | days at the best allowed current¹ |
|---|---|---|---|---|---|---|
| his Cu ogive 200 µm | 18.5° | 0.95 / 1.70 (line-of-sight Li: 1.13 / 1.29) | 23 % | 1630 | 0.1 % | 0.25–0.30 (4 µA, P 20–50) |
| Al 300 + Mo 8 (L11) | 10.5° | 0.26 / 0.40 (line-of-sight Li: 0.34 / 0.39) | 2 % | 1020 | 16–19 %² | 0.5–0.6 (0.5–0.6 µA) |
| **Al 300 + Cu 12, Li r ≤ 4 (L12)** | **10.5°** | **0.33 / 0.38** | 3 % | **590** | 11–12 % | 0.38 (0.9 µA) |
| **Al 400 + Cu 12, Li r ≤ 4 (L12)** | 11.5° | **0.45 / 0.52** | 4 % | 590 | **2.5–3 %** | **0.12** (4 µA) |
| Al 350 + Cu 12 (interpolated) | ~11° | ~0.39 / ~0.45 | | 590 | ~5 % | ~0.2 (2 µA) |
| Al 300 + Cu 30 (L12) | 12.1° | 0.52 / 0.60 | 5 % | 590 | 5 % | 0.27 (2 µA) |
| Al 300 + Ti 15 (L12) | 9.8° | 0.34 / 0.40 | 2 % | 590 | 0 | 0.09 (4 µA) |

¹ ≤ 4 µA, MM x-ray occupancy ≤ 10 % per arm (a working assumption until the point-cluster cut is measured), single-arm
prescale for ≥ 95 % DREAM live time. ² With the Geant4 PIXE yield (×2 the L11 estimate) and the line-of-sight Li.

1. **The Cu liner does what it was meant to.** The leptons see the Al ogive, not the Cu: σ68 10.5° against his 18.5°,
   EPC 3 % against 23 %, and the same days as the Al + Mo ogive with the same Li. At 1 µA it is ×2.9–3.4 faster than his
   Cu ogive (0.33 against 0.95–1.13 d), and ×1.6–2.0 with the Al at 0.4 mm.
2. **Cu sits only where the beam stops: r ≤ 8–10 mm, ≥ 12 µm along the beam** (§1–2). Outside it, Al is harmless
   (§4: even a 1 % halo makes 0.4 % of the γ₀ in Al lines). Coating the whole inside costs ~10–30 % (§7).
3. **Coat by line of sight from the axis, both Cu and Li** (§2–3, §8). The thickness along the beam then comes out
   constant on the steep flank, for the Cu (what the stopping needs) and for the Li. That removes L11's flank problem:
   the 17.64 MeV share drops from 29 % (1.10 MeV) / 71 % (1.03) to 0.9 % / 1.5 %, and 1.03 MeV costs only ~15 %.
4. **Mask the Li to r ≤ 4 mm.** Li further out sits on the flank up to 9 mm upstream of the tip (r 6 mm): the
   opening angle, measured from the nominal vertex, degrades. The whole-spot runs are ~30 % slower at equal σ68 (§7).
5. **The Cu K x-rays are the price, and the Al wall pays it.** Cu makes ~45× more K x-rays than Mo (Geant4 PIXE, §6),
   but at 8 keV Al stops them: 11–12 % MM occupancy per arm per µA through 0.3 mm, 2.5–3 % through 0.4 mm (Geant4 L12
   x-ray libraries and the calibrated model agree to ~20 %). **Make the wall 0.35–0.4 mm**: it also doubles the buckling
   margin (×4.8 → ×10). 0.4 mm costs 1° of σ68 and +36 % days at fixed current, and buys ×4 in current.
6. **New, for every Mo design:** the Geant4 PIXE check gives Mo K ×2.0–2.2 the BEA estimate used in L10/L11. The
   window's and the Mo-lined shells' MM occupancies (16–22 % per arm per µA as published) are ~×2 low: ~30–45 %.
7. **Ti instead of Cu** (15 µm) makes no x-rays that escape and gives σ68 9.8°, 0.34 d/µA: on paper the best of all
   at high current. Its unknowns are practical (H uptake under MeV implantation, film stress, Ti(p,γ) lines): keep it as
   the variant to ask the thin-film lab about, next to Cu.
8. **Honest caveat on speed:** at full current (4 µA) his Cu ogive is not slow (0.25–0.30 d): no x-rays, so nothing
   limits the current but DREAM. The Al + Cu design wins clearly at ≲ 1–2 µA, and at any current on what matters more
   for a claim: a resolution the fit can live with when the background shape floats (FEASIBILITY_SIM §15: ×2.5 at 9°,
   ×6.8 at 14°; his 18.5° is beyond that table), EPC from the shell 3 % instead of 23 %, and ×2.8 fewer trigger legs.
   The days here are statistics with free norms; the floating-shape fit has not been run on L11/L12 yet.

## 1. Where the beam lands (`culiner_landing.csv`)

The beam runs along the axis into the open base and meets the inside of the ogive at the radius it travels at. The
tip cap (the R 2.8 mm inner sphere) ends at r = 2.52 mm; beyond it the flank is hit at ~65° incidence.

| spot σ (per axis) | on the tip cap | r holding 99 % | 99.9 % | 99.999 % | beyond r = 6 mm | beyond 8 mm |
|---|---|---|---|---|---|---|
| 1 mm | 96 % | 3.0 mm | 3.7 mm | 4.8 mm | 0 | 0 |
| **2 mm** (assumed so far) | 55 % | 6.1 mm | 7.4 mm | 9.7 mm | 1.1 % | 3.4 × 10⁻⁴ |
| 3 mm | 30 % | 9.1 mm | 11.1 mm | 14.5 mm | 13 % | 2.8 % |

So everything that matters happens within **r ≲ 8–10 mm of the axis**, i.e. the tip and the first ~10 mm of flank
(the ogive is 63 mm deep and 25 mm in radius). The spot size is the number to get from LNL: it sets the liner's extent.

## 2. How much Cu (`culiner_thickness.csv`, `culiner_profile.csv`)

The requirement is on the thickness **along the beam**, not along the wall normal: a proton crosses the Li, then
must stop in the Cu before the Al. Ranges (PSTAR CSDA):

| | after 20 µm Li (1.10 MeV beam → 872 keV) | bare, 1.15 MeV (no Li, +50 keV) | design, ×1.12 + 1 µm |
|---|---|---|---|
| **Cu** | 6.0 µm | 8.7 µm | **10.7 µm → 12 µm** |
| Mo | 5.4 µm | 8.2 µm | 10.2 µm (the 8 µm of L11 is not enough without Li) |
| Ti | 8.7 µm | 13.2 µm | 15.8 µm |

The bare case covers a film that has gone (sputtered, reacted, evaporated) and protons outside the Li mask: the beam
must still never reach the Al. The ×1.12 covers range straggling (~4 % rms) and a ×1.1 thickness error; the 1 µm the
roughness. **12 µm of Cu along the beam** is the design value. It is 0.08 % X₀ per leg at normal exit: nothing.

**The coating method decides the profile on the flank.** On the flank the wall is hit at ~65°, so 12 µm along the
beam is only ~5 µm along the normal:

| r (mm) | incidence | uniform coat 12 µm (plating): along the beam | line of sight from the axis, source 150 mm: normal / along the beam | source 400 mm |
|---|---|---|---|---|
| 0 | 0° | 12.0 | 12.0 / 12.0 | 12.0 / 12.0 |
| 2 | 46° | 17.1 | 8.6 / 12.3 | 8.5 / 12.1 |
| 3 | 65° | 28.7 | 5.4 / 13.0 | 5.2 / 12.4 |
| 5 | 66° | 29.5 | 5.8 / 14.2 | 5.2 / 12.8 |
| 8 | 67° | 30.9 | 6.4 / 16.5 | 5.2 / 13.5 |
| 10 | 68° | 32.0 | 6.9 / 18.5 | 5.3 / 14.1 |

- A **line-of-sight coat** (sputtering or evaporation from a source on the beam axis, through the open base) lands
  ∝ cos(incidence), the same factor by which the beam's path lengthens: **the thickness along the beam comes out
  constant by construction** (±15 % to r = 8 mm with the source 150 mm back, ±10 % at 400 mm). It puts the least Cu on
  the flank, exactly what the beam needs.
- A **uniform coat** (electroplating) must be 12 µm on the tip and is then ×2.4 thicker than needed along the beam on
  the flank: harmless for the stopping, a little more Cu for the leptons and less x-ray escape.

## 3. The Li film on the flank: a property of the coating, not of the shape (`culiner_li_mix.csv`)

L11 (SHAPES_GEANT §10) assumed 20 µm of Li **along the wall normal** everywhere. On the flank a proton then crosses
~50 µm of Li, leaves it below the 441 keV resonance, and the 17.64 MeV line becomes 29 % (1.10 MeV) to 71 % (1.03 MeV)
of the γ₀. **Li evaporated from the axis lands the same way as the Cu**: its path along the beam is ~20 µm everywhere.

| E_p | Li film | share of the beam on Li | ⁸Be γ₀ per proton / flat film | 17.64 MeV share |
|---|---|---|---|---|
| 1.10 | uniform along the normal, no mask (L11) | 100 % | 2.28 | 29 % |
| 1.10 | **line of sight, no mask** | 100 % | 1.05 | **0.9 %** |
| 1.10 | line of sight, mask r ≤ 4 mm | 86 % | 0.90 | 0.9 % |
| 1.10 | **line of sight, mask r ≤ 6 mm** | 99 % | **1.04** | 0.9 % |
| 1.03 | uniform, no mask (L11) | 100 % | 5.32 | 71 % |
| 1.03 | line of sight, no mask | 100 % | 1.05 | 1.5 % |

So with a line-of-sight Li coat the ogive behaves like the flat film (×1.05: the steepest flank is a little thicker
along the beam), at either energy. L11's extra yield (×2.3) came with the 17.64 line; the line-of-sight coat gives up
both. That is the right trade: a clean 18.15 MeV line, and 1.03 MeV costs only ~15 % (direct capture), not ×1.7.
**The Li mask exists only to keep Li off the bare Al** (Li alloys with Al): put it at r ≤ 6 mm (99 % of a σ 2 mm
beam), with the Cu reaching ≥ 3 mm further.

## 4. Al outside the Cu (`culiner_halo.csv`)

Protons that miss the Cu hit bare Al at the full energy and make ²⁷Al(p,γ) 10.76 MeV γ through the 992 keV resonance
(1.14 × 10⁻⁹ per proton in thick Al), against 2.4 × 10⁻⁹ ⁸Be γ₀ per proton on the Li.

| Cu out to | Gaussian σ 2 mm: share on Al | 10.76 MeV γ / ⁸Be γ₀ | with a 1 % flat halo to r 25 mm |
|---|---|---|---|
| 4 mm | 13.5 % | 6.3 % | 6.7 % |
| 6 mm | 1.1 % | 0.5 % | 1.0 % |
| **8 mm** | 3 × 10⁻⁴ | 0.02 % | 0.4 % |
| 10 mm | 4 × 10⁻⁶ | ~0 | 0.4 % |

Even a badly tuned beam with 1 % of halo puts only 0.4 % of the γ₀ rate into 10.76 MeV γ (~60 /s per µA, below the
X17 window, a few single-arm legs). **The Al is not what sets the liner's extent.** The Li mask and its alignment are:
Cu to r ≥ 9–10 mm, Li to r ≤ 6 mm. Coating the whole inside with Cu is also fine physically (§7 measures its cost).

## 5. Heat, stress, pressure, hydrogen (`culiner_thermal.csv`, `culiner_stress.csv`)

- **Heat** (the §20.4 fin, air h = 10 W/m²/K outside, the beam's E_p × I in the wall): the tip runs **+69 K at 4 µA**
  (σ 2 mm) for Al 300 + Cu 12 (75 K without the Cu; Al 400 + Cu 12: 54 K), +17 K at 1 µA. Li stays below ~100 °C.
  Cu over the tip region helps a little; it is not needed for heat. A σ 1 mm spot: +81 K at 4 µA.
- **Bimetal stress** (Δα = 6.6 × 10⁻⁶/K): an electroplated layer (deposited ~50 °C) carries −35 MPa at room temperature,
  +40 MPa on beam at 4 µA, +115 MPa in a 150 °C bake; a sputtered layer (~150 °C) −150 MPa at room temperature and 0 in
  the bake. All below the yield of fine-grained deposited Cu (150–400 MPa). The adhesion is what has to be checked:
  thermal-cycle a witness coupon 20–150 °C.
- **1 bar** is carried by the Al (§20.3): Al 6061-T6 0.3 mm ×4.8 on buckling, 0.4 mm ×10. The Cu adds nothing to rely on.
  Not 0.2 mm.
- **Hydrogen** stops in the Cu, ~6 µm deep, as in his Cu ogive: 2.2 × 10¹⁸ H/cm² per day at 1 µA at the centre of a
  σ 2 mm spot (σ 3 mm: 9.5 × 10¹⁷). Cu blisters from ~10¹⁹ (Budker, 2 MeV): ~5 µA·day (σ 2) to ~10 µA·day (σ 3) at the
  spot centre. A 3σ test of ATOMKI needs ≲ 1 µA·day; a long run needs a wobbled or wider spot, or fresh ogives (they
  cost ~1 k€ each).

## 6. The K x-rays the stop makes (`pixe_testem5.csv`, `culiner_xray.csv`)

**PIXE yields, checked in Geant4 (TestEm5, thick target, emstandard_opt4, PIXE on; 2026-11-04, lxplus condor)**, per
proton entering the stop at 872 keV (the energy after 20 µm of Li):

| | Geant4 "Empirical" | Geant4 ECPSSR | BEA ESTIMATE used in L10/L11 |
|---|---|---|---|
| Cu K (8.0/8.9 keV) | 2.15 × 10⁻⁴ (±15 %) | (ECPSSR_FormFactor is slow; still running) | 2.1 × 10⁻⁴ |
| Mo K (17.5/19.6 keV) | 4.8 × 10⁻⁶ (±5 %) | 4.5 × 10⁻⁶ (±5 %) | 2.2 × 10⁻⁶ |
| Ti K (4.5 keV) | 1.7 × 10⁻³ | | |

- **Cu K is as estimated; Mo K is ×2.0–2.2 higher than the estimate.** The L10/L11 Micromegas occupancies from Mo
  (window 16 %, window on the Be tube 22 %, Be/Al ogive + Mo 15 % per arm per µA) were therefore ~×2 too low.
- Cu makes ~45× more K x-rays than Mo per proton, but at 8 keV, just under the Cu K edge, where Al absorbs them
  ×10 harder than Mo's 17.5 keV (μ/ρ 49 against 5 cm²/g).

**What reaches the Micromegas.** Model (`opt_cu_liner.escape`): production depth from the stopping, the photon's way
out through the rest of the stop and the Al at every exit angle (the CAD solids), across the cavity to the far wall
for photons emitted inward, air, the MM window and cathode, absorption in 30 mm of gas; calibrated per line on the
Geant4 L11 x-ray library (Cu K ×1.2, Mo K ×2.6: in Geant4 the cathode's photoelectrons also make hits). All rows with
the same Li (line of sight, mask r ≤ 4, protons outside it enter the stop at the full 1.10 MeV), stop over r ≤ 8 mm:

| stop / wall | MM hits per arm per µA | occupancy per arm per µA (1.2 µs) |
|---|---|---|
| Cu 12 / Al 300 (plated) | 1.0 × 10⁵ | 11 % |
| Cu 12 / Al 300 (line of sight: thinner on the flank) | 1.3 × 10⁵ | 14 % |
| **Cu 12 / Al 400** | **2.7 × 10⁴** | **3.2 %** |
| Cu 12 / Al 500 | 7 × 10³ | 0.8 % |
| Cu 30 / Al 300 | 4.1 × 10⁴ | 4.8 % |
| Cu 50 / Al 300 | 1.9 × 10⁴ | 2.3 % |
| Ti 15 / Al 300 | 0 | 0 |
| Mo 10 / Al 300 | 1.45 × 10⁵ | 16 % |
| Mo 10 / Be 300 | 2.8 × 10⁵ | 29 % |
| his Cu 200 ogive | ~10³ | 0.1 % |

- **On x-rays the Cu liner is no worse than Mo on the same Al wall, and one extra 0.1 mm of Al takes it ×3.7 lower.**
  The lever is the Al: each 0.1 mm divides the 8 keV escape by ~3.7. A thicker Cu layer also works (it absorbs its own
  line), at a little more lepton cost.
- Ti would make no x-rays at all (4.5 keV does not leave), but it takes up hydrogen and is a worse stop per µm; keep it
  as the fallback if the MM point-cluster cut does not work.
- **Geant4 L12 x-ray libraries** give the same numbers directly for the simulated variants (§7).

Same model for the Li mask r ≤ 6 and the Cu to r ≤ 10 (`culiner_xray_m6.csv`; fewer protons hit bare Cu at full
energy): Cu 12 / Al 300 8.4 %, Al 350 3.8 %, Al 400 1.9 %, Cu 20 / Al 350 2.4 %, Mo 10 / Al 300 11 %, Mo 10 / Al 400
8.5 % per arm per µA.

## 7. Geant4 run L12: the leptons, the backgrounds, the trigger (2026-11-04)

**Runs.** MX17_Full_Geant branch `lnl_culiner` (from `lnl_ogive`, commits 6373bb1, 812488b): `--ogive-liner-r R`
builds the liner (and the film) only where the shell's inner radius is ≤ R, on the shell's own polycone planes (no
overlap; checked); `--li-mask-r R` keeps the pair and γ vertices where the beam lands at r ≤ R. Binary
`bin/mx17_full_sim_culiner_812488b` in `…/x17_lnl/MX17_Full_Geant`. Same samples and analysis as L11 (X17 m16.8,
Born M1/E1 at 18.15 and 15.1, 2 × 10⁷ ⁸Be γ, both detectors), the γ-line library for the r ≤ 8 design, and the K x-ray
libraries (Cu, Mo, Ti lines) for every configuration plus the L11 Al + Mo ogive. `shapes/lxplus/l12_configs.sh`;
output `/eos/…/lnl/L12/`, tables `…/lnl/target/sel_l12/`. Analysis `shapes/shapes_geant.py` (L12 tags; '_los' =
the same events with a line-of-sight Li film's yields, `opt_cu_liner.los_yield_mix`), `shapes/shapes_rates.py`.

**Reach** (big plastics, days per µA to 3σ at R(ATOMKI); as built in brackets, statistics-limited ±30–50 %):

| configuration | σ68 | acc | 1.10 MeV | 1.03 MeV | EPC |
|---|---|---|---|---|---|
| Al 300 + Cu 12 over the whole inside, Li everywhere (uniform film, L11-like) | 10.5° | 0.152 | 0.29 (1.2) | 0.44 | 2 % |
| same, line-of-sight Li | 10.5° | 0.152 | 0.37 (1.6) | 0.43 | 1 % |
| **Al 300 + Cu 12 at r ≤ 8, Li r ≤ 4 (line of sight)** | **10.5°** | 0.152 | **0.33** (2.4) | **0.38** | 3 % |
| Al 400 + Cu 12 at r ≤ 8, Li r ≤ 4 | 11.5° | 0.150 | 0.45 (3.2) | 0.52 | 4 % |
| Al 300 + Cu 30 at r ≤ 8, Li r ≤ 4 | 12.1° | 0.149 | 0.52 (2.2) | 0.60 | 5 % |
| Al 300 + Ti 15 at r ≤ 8, Li r ≤ 4 | 9.8° | 0.153 | 0.34 (2.0) | 0.40 | 2 % |
| *references (L11, line-of-sight Li): Cu ogive 200* | 18.5° | 0.140 | 1.13 (2.8) | 1.29 | 22 % |
| *Al 300 + Mo 8* | 10.5° | 0.152 | 0.34 (2.1) | 0.39 | 3 % |
| *Be 300 + Mo 8* | 7.0° | 0.156 | 0.20 (1.5) | 0.23 | 3 % |
| *window 45° on a Be tube (L11)* | 7.2° | 0.150 | 0.23 (2.2) | 0.27 | 2 % |

- **12 µm of Cu costs nothing measurable against 8 µm of Mo** (10.5° both; 0.37 against 0.34 d with the whole inside
  coated). The Al wall sets the resolution: +0.1 mm of Al costs 1.0° and +36 % days; +18 µm of Cu costs 1.6° and +58 %.
- **Restricting the Li to r ≤ 4 helps beyond its yield.** Per unit yield the r ≤ 4 runs are ~25 % faster than the
  whole-spot runs at the same σ68: flank vertices sit 5–14 mm upstream of the nominal vertex (y = −4.8 mm at r 4,
  −9.3 at r 6, −14 at r 8) and spoil the vertex-to-hit opening angle in the tails. The yields-only "mask r ≤ 6"
  variant (0.28 d) keeps the r ≤ 4 vertices and is optimistic: do not use it. A reconstruction that knows the tip
  shape could recover part of this (not tried).
- As built the Al + Cu ogive is no faster than his Cu ogive within the statistics (2.0–2.4 against 2.1–2.8 d): with the
  small plastics the acceptance, not the target, limits the reach.
- **Trigger/DREAM** (`daq_live.csv`, big plastics, 1.10 MeV, 1 µA, with the contaminant levels of SHAPES_GEANT §3):
  590 legs/s and 23 pairs/s: 86 % live at prescale 1, 98 % at 10 (his Cu ogive: 1630 legs/s, 68 % / 95 %; the window
  690). The line-of-sight Li has no 17.64 MeV excess, and the Al converts less than his Cu.
- **X-rays in the MM, Geant4 L12 libraries** (MM hits per arm per emitted x-ray, photons started in the film, so they
  cross the whole liner; × the Geant4 PIXE yield, protons outside the mask entering the Cu at 1.10 MeV):

  | | Cu Kα / Kβ per x-ray per arm | MM hits per arm per µA | occupancy per µA |
  |---|---|---|---|
  | Al 300 + Cu 12 at r ≤ 8 | 3.6 × 10⁻⁵ / 1.7 × 10⁻⁴ | ~1.0 × 10⁵ | ~12 % |
  | Al 300 + Cu 12 everywhere | 4.3 × 10⁻⁵ / 1.8 × 10⁻⁴ | ~1.1 × 10⁵ | ~13 % |
  | Al 400 + Cu 12 at r ≤ 8 | 5.3 × 10⁻⁶ / 5.0 × 10⁻⁵ | ~2.1 × 10⁴ | ~2.5 % |
  | Al 300 + Cu 30 at r ≤ 8 | 1.4 × 10⁻⁵ / 7.5 × 10⁻⁵ | ~4.2 × 10⁴ | ~5 % |
  | Al 300 + Ti 15 | Ti K: 0 in 8 × 10⁵ | 0 | 0 |
  | Al 300 + Mo 8 (Mo K 17.5 / 19.6) | 4.2 × 10⁻³ / 4.8 × 10⁻³ | 1.6 × 10⁵ with line-of-sight Li | ~19 % |

  The calibrated model of §6 agrees to ~20 %. Cu Kβ (8.9 keV, 12 % of the lines) makes about half of what gets through:
  Al absorbs it ~25 % less than Kα.

## 8. How to make it, and how to check it

**Option A, recommended: coat the inside by line of sight from the axis, at LNL.**
1. Machine (or spin) the ogive in Al 6061-T6, wall 0.35–0.4 mm, with a thick collar at the base for the joint
   (§20.7). Several at once; ~0.5–1 k€ each in the LNL workshop.
2. In one vacuum system, base toward the source, source on the axis 150–400 mm away: Ar-ion etch the inside (removes
   the Al oxide; needed for adhesion), then **sputter or evaporate Cu to 12 µm at the tip** (14–16 µm is a fine
   target), through a sleeve mask that stops it at r ≈ 10 mm (or let it cover the whole inside: §7 says what that
   costs). At 0.1–0.3 µm/min that is 1–2 h. LNL's thin-film lab sputters Cu and Nb onto cavities routinely (ask).
3. Without breaking vacuum if possible (or transfer under Ar), **evaporate 20 µm of Li from the same axis** through an
   aperture mask that stops it at r ≈ 6 mm. The line-of-sight geometry gives the constant Li path along the beam of §3.
4. A witness coupon at the tip's position in steps 2 and 3 gives the thicknesses (profilometer, XRF or β backscatter).

**Option B: electroplate (any plating shop).** Double zincate on the Al, a Cu strike, then acid Cu to 15–20 µm on the
tip, with an anode wire on the axis (the tip is the deepest point and plates thinnest without it); mask the outside and
r > 10 mm with lacquer. Uniform along the normal (×2.4 more Cu than needed along the beam on the flank, §2). Bake at
150 °C to outgas the deposit before it goes on the beam line. Cheapest, but the plating chemistry leaves Zn under the
Cu, and the Li still has to be evaporated as in A.3.

**Option C, if someone has the sheet: Cu-clad Al (roll-bonded) spun into the ogive**, Cu inside. A metallurgical bond
and no coating step, but the Cu is wherever the sheet is (~30–40 µm over the whole wall for a 10 % clad), and thin
clad sheet that survives a 63 mm deep spin is not a catalogue item (ask).

**Not a loose Cu cup pressed into the tip**: no thermal contact, and a trapped volume under vacuum.

**Checks before it goes on the beam:** the coupon thicknesses (Cu ≥ 12 µm along the axis at the tip); a tape test and
10 cycles 20–150 °C on a coupon; the usual helium leak test of the assembly; then **on the beam, a 1.10 MeV PIGE look
with a LaBr₃ or Ge**: Al lines (843 / 1014 keV from ²⁷Al(p,p′), 10.76 MeV) must be absent, and the 478 keV Li line
present. That proves the Cu covers where the beam lands, in minutes.

## 9. What to ask Pierfrancesco and LNL

1. The beam spot at the target (σ, and the halo): it sets the liner and mask radii (§1).
2. Can the LNL thin-film lab sputter (or evaporate) ~15 µm of Cu inside the ogive from the axis, after an ion etch,
   and then Li through a mask, ideally without breaking vacuum?
3. Al 6061-T6 at 0.35–0.4 mm for the shell (not 0.2 mm), with a collar at the base.
4. The beam current he expects (≤ 1 µA makes the x-rays a non-issue for any variant).

## Sources

- Geometry: the 27 Oct CAD (`lnl/mech_models/sketch li target X17.step`), `opt_sketch.py` (TARGET_OPTIONS §19).
- Ranges and stopping: PSTAR (`lnl/data/pstar_stopping.csv`).
- PIXE: Geant4 TestEm5 (scripts in `lxplus/pixe_check/`) (`G4EmParameters` PIXE on, `pixeXSmodel` Empirical / ECPSSR_FormFactor), lxplus condor,
  `/afs/cern.ch/work/d/dneff/pixe_check/`; the BEA scaling of `shapes_backgrounds.py`.
- X-ray attenuation: NIST XCOM (read off the tables, ±5–10 %).
- ²⁷Al(p,γ) 992 keV: `opt_backing.py` (TARGET_OPTIONS §4). Blistering: TARGET_OPTIONS §5 (Budker INP).
