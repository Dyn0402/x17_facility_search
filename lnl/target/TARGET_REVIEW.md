# Critical review of the LNL target designs: what can really be built

Started 2026-11-11. Dylan asked for a critical review of every target design we have for LNL: is any of them not
feasible for budget, mechanical or technological reasons? He has asked Pierfrancesco whether depositing the Li, Cu
or Ti "in vacuum in the beam pipe" is feasible and has no answer yet. So: find out how lithium targets have
actually been built at LNL and elsewhere, use that as the baseline for what is possible, then review our designs
against it and look for problems and better ideas.

This file is the review. It adds no Geant4. New numbers come from two small scripts (§9) and are marked
**ESTIMATE**; the days are the reference-fit days of `out/target/shapes/nd_reach.csv` (interim until run L13 is
folded in, `../FEASIBILITY_SIM.md` §19). Facts from the literature search carry their source (§10) and a tag:
**[read]** = read in the source, **[snippet]** = seen in a search result only.

## 0. Bottom line (2026-11-11)

1. **Nobody deposits lithium inside the beam pipe, and we do not need to.** The search found no laboratory that
   evaporates metallic Li in place on an accelerator line, and none that deposits Cu or Ti there. What exists is
   (a) a glovebox next to the accelerator (LNL: Li rolled to 20 µm and pressed onto Cu), and (b) a separate
   evaporation stand whose target leaves under vacuum behind its own gate valve (Novosibirsk). Our own write-up
   (`CU_LINER.md` §8) asks for "one vacuum system" with the source on the ogive's axis, which is a coating
   chamber, not the beam pipe, and the slides sent on 4 Nov say the same ("one vacuum system, the source on the
   axis"). If the question Pierfrancesco received says "in the beam pipe", he may say no to something we do not
   need (§3).
2. **The 20 µm of lithium metal on copper is already LNL's routine.** The CN neutron group rolls Li to "typically
   20 µm" in an argon glovebox and presses it onto a 300 µm Cu cup with paired moulds [read]. That is exactly our
   film and our stop, made without any evaporation. The same group wrote in 2015 that it was "depositing lithium
   by evaporation in a dedicated evaporator" [read]; no result from it was ever published, so whether it works
   today is a question for Pierfrancesco. LNL's targets group, separately, sputters thick films as a speciality
   (110–125 µm of Mo on flat Cu at 11 µm/h; 30–45 µm of Nb inside Cu cavities) [read], but hot (500–550 °C) and
   on copper, and shows no lithium work (§2.3).
3. **The design we sent back (Al ogive + Cu liner + masked, evaporated Li) stacks three things LNL has not shown
   it can do**: a 0.35 mm aluminium wall turned 63 mm deep, ≥ 12 µm of Cu stuck to aluminium at the bottom of that
   cone, and lithium *evaporated* through a mask from far out on the axis. Each is possible; together they are a
   development project of months. **As built it buys little**: with the 0.4 mm wall we recommended, 6.1 / 11 d
   against 6.1–7.6 / 11–14 d for his all-Cu ogive (×1.0–1.3, inside the Monte Carlo uncertainty); with a 0.3 mm
   wall, 4.4 / 8.7 d (×1.4–1.7). The ×2.4–3.5 gain exists only with the big plastics (0.43–0.64 d against
   1.4–1.5 d) (§4.1).
4. **New: a 20 µm Li film is not safe against its own chemistry.** When residual water turns lithium into LiOH the
   lithium atoms stay, but the oxygen and hydrogen add stopping. At 1.10 MeV, once half of a 20 µm film is LiOH the
   beam leaves it at 454 keV and **52 % of the γ₀ comes from the 441 keV resonance** (fresh: 0.85 %); at 1.03 MeV,
   91 %. This is the ATOMKI 2016 accident by another route, and it applies to every design here, his included.
   At 1.10 MeV a **10–12 µm film is immune** (10 % at worst, fully converted), for 51–61 % of the yield (§4.2).
5. **Three designs should be dropped:**
   - **Anything in beryllium.** The last supplier of machined and welded beryllium vacuum tubes stopped in 2023
     and CERN had to build its own facility [read]; a custom thin Be shell is 20–60 k€ and 6–12 months
     (ESTIMATE), plus a safety case.
   - **Anything with a molybdenum stop**, at 1 µA: with the corrected Geant4 x-ray yield the Micromegas occupancy
     is 19–45 % per arm per µA. This takes out the diamond window as drawn, the flat diamond design and the Al/Be
     + Mo ogives.
   - **The diamond.** At 1 µA the beam is 1.1 W. A 0.4 mm aluminium disc carries that with a 5 K rise. The diamond
     costs 6–15 k€ mounted (ESTIMATE), is brittle, has never been hydrogen-tested, and in the ray-trace buys
     0.0° of resolution over 0.3 mm of aluminium (§4.5).
6. **Nothing here is a budget problem except beryllium.** Every other target is 1–15 k€ against a 100–266 k€
   budget. The real cost is people and time in LNL's thin-film lab, and that is what should decide (§4.8).
7. **Better idea: keep his method, change the shape and the wall.** A **one-piece aluminium end cap with a flat
   face tilted 45°** (the "diamond window" design with the diamond, the Ti rings and the glue removed), 0.4–0.5 mm
   thick over a Ø20 bore, a flat Cu stop on the vacuum side, and LNL's own rolled Li pressed onto it with flat
   moulds. A flat face makes every step routine, the lithium is uniform along the beam by construction (no flank,
   no mask, no line-of-sight coating), and the 45° window is the best buildable geometry we have simulated
   (0.31–0.35 d with big plastics, 4–6 / 6.5–10 d as built; the ogive with the liner 0.43, 4.4 / 8.7). Not yet in
   Geant4 with aluminium; the config line is in §8.
8. **If Pierfrancesco wants to keep the ogive**, the order is: (i) his Cu ogive, electroformed in hard copper,
   Li pressed on the tip only; (ii) the Al ogive with Cu **plated over the whole inside** (seed + electroplate, no
   mask) and Li pressed on the tip. Neither gives up anything measurable against the masked-liner design as built.

## 1. What was reviewed

Every design in `TARGET_OPTIONS.md`, `SHAPES_GEANT.md` and `CU_LINER.md`. Days to 3σ at the ATOMKI strength,
1 µA, 1.10 MeV, m_X 16.8, reference fit (`nd_reach.csv`): big plastics / as built with the liquid repaired / as
built with the liquid as it ran at n_TOF.

| # | design | who | days: big / as built | status in our notes |
|---|---|---|---|---|
| 1 | Cu cup, 300 µm hemisphere, pressed Li (exists, CN neutron line) | LNL | 5.8 / 29 / 31 (200 µm: 3.2 / 20 / 25) | reference |
| 2 | Cu ogive 200 µm, Ø50 × 63, Li inside | Pierfrancesco, 27 Oct CAD | 1.4 / 6.1 / 11 | his default |
| 3 | Al ogive 0.3 mm + Mo 8 µm liner | us | 0.38–0.43 / 3.7–4.7 / 6.3–8.0 | superseded by 4 |
| 4 | Al ogive 0.35–0.4 mm + Cu 12 µm at r ≤ 8 + Li masked to r ≤ 4, coated from the axis | us, sent 4 Nov | 0.43 / 4.4 / 8.7 (0.4 mm: 0.64 / 6.1 / 11) | "the design to send back" |
| 4b | same shell, Cu plated over the whole inside, Li on the tip only | us (Option B) | 0.42 / 3.5 / 6.0 | fallback |
| 5 | Al ogive 0.3 mm + Ti 15 µm | us | 0.42 / 4.0 / 7.9 | variant to ask about |
| 6 | Be ogive / Be hemisphere / Be end piece + Mo | us | 0.18–0.37 / 2.4–3.6 / 3.8–6.5 | "upgrade" |
| 7 | CVD diamond window Ø20, 45°, Mo 8 µm, Ti rings, Al end piece | Pierfrancesco's idea 2, our sizing | 0.31–0.35 / 4.2–5.6 / 6.5–9.6 | our choice of 26 Oct |
| 8 | flat Li / Mo 8 / diamond 50 µm on a Cu ring in a CFRP chamber | us | 0.23 (0.35 with a chamber that holds vacuum) | first recommendation |
| 9 | thin Li₂O 300 µg/cm² on 10 µm Al in a CFRP chamber, beam to a dump | ATOMKI-style baseline | 0.85 / 14 / 29 | baseline |

Designs 1–8 use **~20 µm of metallic lithium**. In 1–7 the target is also the beam stop and the vacuum wall at
the end of the pipe; 8 and 9 sit inside a chamber.

## 2. The baseline: how lithium targets have actually been built

### 2.1 At LNL

- **CN 0° line, Mastinu's group** (arXiv:2605.12005 §4.1, in `../refs/`) [read]. "A metallic lithium layer
  pressed into a 300 µm-thick copper backing that also serves as the beam stopper." "Fabrication is performed
  inside an argon-filled glovebox from lithium stored under paraffin. The lithium is cleaned and rolled to the
  desired thickness, typically 20 µm (with thinner foils down to sub-10 µm), and pressed onto the copper backing
  using paired moulds." Foils of 10–40 µm. Air-cooled, ~10 °C per watt, safe to ~10 W. The assembly is a
  "removable Cu backing" on an "isolated PVC tube" behind a Ta collimator. Used at 0.07–0.43 µA and 4–5.5 MeV.
  The photo Pierfrancesco sent (`../pictures/`) is this cup: a pressed disc of about Ø 6–8 mm at the apex.
  No independent thickness measurement is described (the thickness enters the fluence error at ~5 %), and
  nothing on how the cup travels from the glovebox to the line.
- **The same recipe on a hemisphere** (LNL Tandem, arXiv:2311.06143) [read]: 200 µm of Li pressed between male
  and female moulds onto a hemispherical 300 µm Cu backing, the current read from the backing, a two-stage Ta
  collimator 10 cm upstream. The authors call glovebox-made Li targets a handling burden.
- **Evaporated lithium** (Mastinu et al., Nuovo Cimento C 38 (2015) 193, the micro-channel target paper)
  [read]: "We are currently depositing lithium by evaporation in a dedicated evaporator." Nothing published
  since on thickness, adhesion or a beam test. Not in a beam pipe.
- **AN2000, the LNL ⁸Be pair spectrometer** (Góngora-Servín, thesis Ferrara 2025 and Acta Phys. Pol. B Proc.
  Suppl. 18, 2-A13) [read]. This is the local experience with the *thin-film* route, and it is bad:
  - 24 LiF targets, 34–935 µg/cm², on self-supporting C or Cu backings of 10–60 µg/cm², tilted 45° on a ladder,
    beam through to a Faraday cup ~1 m behind; 0.4–1.1 MeV, up to ~800 nA, ~790 h on target.
  - Most LiF targets gave only 6–8 h of stable rate before degrading or breaking; the best (34–100 µg/cm² LiF on
    20–35 µg/cm² C) lasted about two days (the search's paraphrase of thesis §4.1). The one Li₂O target (486 µg/cm² on Al) broke immediately at 500 nA and 1.05 MeV.
  - Metallic Li was rejected there as air-reactive.
- **Lines.** AN2000: up to 1 µA, ~800 nA delivered at 0.4–1.1 MeV, spot a few mm, the 0° chamber at ≤ 10⁻⁷ mbar.
  CN: 2–8 mm FWHM; an LN₂ trap against carbon is part of the irradiation-line upgrade. The vacuum and any cold
  trap at the present CN Li station were not found (ask). A 2025 slide of Mastinu's gives a 9 µA radioprotection
  limit for the CN, against the 4 µA of the 2026 paper and the 1 µA of the beam sheet (ask).

### 2.2 Elsewhere

| laboratory | lithium | how it is made and moved | source |
|---|---|---|---|
| BINP Novosibirsk (BNCT) | metal, 7–200 µm on Ø82 Cu | separate "vacuum evaporation unit with a moving heater"; "the lithium target together with the gate valve under vacuum is disconnected from the evaporation unit and transported to the accelerator". Thickness from the weighed charge or a 478 keV scan. ~6 nm of Li₂O after transfer, growing during operation | [read] 1, 2, 7, 8 |
| Notre Dame | metal, 100 µm evaporated on Cu, 10–20 µA | | [read] 11 |
| Karlsruhe | metal, 20–30 µm on water-cooled Cu, ~100 µA | in place or not: not found | [snippet] 5 |
| PTB | metal, 5–10 µm evaporated on Ta, 0.5–1.5 µA; "gradual build-up of a surface layer on the metallic Li target" | in place or not: not found | [snippet] 4 |
| ATOMKI | LiF, Li₂O; metal 30 and 300 µg/cm² on 10 µm Al, 5 µA | "the metal Li diffused into the Al backing"; fix: cooling rods, argon transport | [read] 13 |
| MEG II | LiPON 7 µm sputtered on 25 µm Cu, 8–11 µA at 1080 keV, "chosen for its chemical stability" | "no significant target deterioration" in 4 weeks | [read] 16 |
| Hanoi | LiF ~30 µg/cm², Li₂O ~0.3 mg/cm² on 10 µm Al or 1 µm Ni, 1–1.5 µA | "burned out (punctured) many times" | [read] 15 |

What this says:
- **Metallic Li at 20 µm on Cu is established** (LNL pressed; BINP, Notre Dame, Karlsruhe evaporated). It is
  thicker in Li atoms than any X17 experiment has used; only ATOMKI tried metal, on Al, and it failed.
- **Li metal is always made off the beam line**, then moved under argon or under vacuum.
- **Compound films are what the pair experiments chose**, for chemical stability. They pay ×4–8 in yield, and
  on thin backings they break (Hanoi, LNL). The one that lasted, MEG II's, sat on 25 µm of copper that stopped
  the beam. **A film on a metal stop that carries the heat is the robust layout; Pierfrancesco is right about
  that.**

### 2.3 LNL's thin-film and target-making capability

- **The targets group** (J. Esposito and others; EURO-LABS talk, May 2026) [read]: rolling (a few mg/cm²),
  thermal and electron-beam evaporation (tens to hundreds of µg/cm²), ion-beam sputtering, and a magnetron
  chamber with five sources (HiPIMS, DC, pulsed DC, RF). TaN/TiN/ZrN targets for LUNA, PVD Ta thicker than
  2.5 µm. Films are characterised on the CN −15° line (EBS/PIXE/PIGE) and on AN2000 (EBS/ERDA/µ-RBS).
- **Thick sputtered films are a local speciality**, from the cyclotron-target and cavity work [read]:
  - 110–125 µm of Mo on flat Cu discs (Ø32 × 1.5 mm), ~98 % dense, **11 µm/h**, substrate at 500 °C, 1–2 µm Ti
    adhesion layers, grown as a pulsed multilayer to control stress; survived ~1 kW/cm² (Skliarova et al. 2019).
  - 30–45 µm of Nb **inside** 6 GHz copper cavities, at 550 °C (Garcia Diaz et al., SRF2021).
- **What that does and does not cover for us:**
  - 10–15 µm of Cu, Ti or Mo on a *flat* part is well inside what they do.
  - The same deep inside a Ø50 × 63 mm cone is plausible (both ingredients exist) but not documented.
  - The dense thick films were grown at 500–550 °C on copper. **6061-T6 loses its temper above ~200 °C**, and a
    0.35 mm wall would distort: on aluminium the coating has to be done cool, where adhesion and stress of a
    > 10 µm film are the open questions (§4.1).
  - No thick sputtered *copper* and no Ti above 2 µm were found in their papers.
  - **No lithium** (metal or compound) and no glovebox appear in the targets-group material. Lithium at LNL is
    the Mastinu group's glovebox, mill and (2015) evaporator.
- **Nearby:** LNS Catania makes ⁶,⁷LiF on C, Mylar or glass, ⁶LiH and ⁶Li₂O, and has a rolling mill in an inert
  glovebox [read / snippet]. LUNA uses evaporated Li₂O and Li₂WO₄ on Ta.

## 3. "Deposit the Li / Cu / Ti in vacuum in the beam pipe": is it feasible?

**Short answer: Li, in principle, but nobody does it and it would be a development project on LNL's accelerator
line; Cu or Ti, no. And none of it is needed.**

- **No precedent.** The search found no target station anywhere that evaporates metallic Li inside the beam pipe,
  and none that deposits Cu or Ti in place (§2.2). The closest is Novosibirsk's stand with a gate-valve transfer,
  and a surface-science chamber in Japan.
- **Lithium, the numbers (ESTIMATE).** A film of thickness t on the axis at distance d from a small source needs a
  charge m = π d² ρ t. For 20 µm of Li: **0.8 g at 150 mm, 5.4 g at 400 mm**. A Ø8 mm patch holds 0.5 mg. So 99.9 %
  of the lithium lands on the mask, the pipe, the Ta collimator and, on the CN line, the **PVC tube that isolates
  the target** so it can serve as a Faraday cup: a lithium film on that insulator shorts the current measurement.
  A boat on a retractable arm 40–50 mm from the target would cut the charge to ~55–85 mg, but that is a new
  mechanism in the accelerator vacuum, with a hot crucible (550–600 °C) next to a gate valve and Viton seals.
- **Copper or titanium, the numbers.** Sputtering needs 10⁻³–10⁻² mbar of argon, a water-cooled magnetron on the
  axis that then has to move out of the beam, and 7–30 h for 12 µm at a 150–200 mm throw (ESTIMATE, §4.4).
  Evaporating 12 µm of Cu needs 7.6 g at 150 mm from an electron-beam source. Neither belongs on a beam line.
- **Why it is not needed.**
  - The only reason to deposit in place is to keep the lithium from air. A 20 µm film does not need that:
    after a vacuum transfer BINP measured ~6 nm of Li₂O [read], and even ~0.5 µm of hydroxide from a short
    argon-bag or air transfer is 2–3 % of the film. It is the *thin* films (≤ 1 µm) that air destroys: a
    53 µg/cm² Li-on-Ta target became Li₂CO₃ [read, 9].
  - What converts a lithium film is the days it then spends in the beam-line vacuum (§4.2), and depositing in
    place does nothing about that.
  - LNL's glovebox route already delivers the film.
- **What our design actually asks for** is one *coating chamber* in which the Cu and then the Li are laid down from
  a source on the ogive's axis, without breaking vacuum between the two (`CU_LINER.md` §8, Option A). That is a
  thin-film-lab job, not a beam-line job. It is still the hard version (§4.1). The question to Pierfrancesco is
  better put as in §7.

## 4. Issues found, most important first

### 4.1 The Al ogive + Cu liner: three development items for a small as-built gain

What the design asks of LNL, against the baseline of §2:

| step | what we wrote | what the baseline says |
|---|---|---|
| shell | Al 6061-T6, wall 0.35–0.4 mm, Ø50 × 63 deep, "~0.5–1 k€ in the LNL workshop" | Machining guides put the comfortable wall for turned 6061 at 0.5–0.8 mm; one quotes 45 % scrap at 0.5 mm [read, vendor]. LHCb's VELO foil shows 0.25 mm can be milled from solid, as a project. A closed, pointed bore 63 mm deep needs a mandrel or a low-melt fill, spare blanks and a leak test per part. Feasible with care; 0.8–2.5 k€ (ESTIMATE) and one or two scrapped. |
| Cu | ≥ 12 µm at the tip, r ≤ 8–10 mm, "sputter or evaporate … 0.1–0.3 µm/min, 1–2 h", through a sleeve mask, after an argon etch | LNL's own close-coupled rate is 11 µm/h (Mo on flat Cu, 500 °C). At the 150–200 mm throw of a source outside the cone a magnetron gives 0.1–0.5 nm/s: **7–30 h** (ESTIMATE; the rate falls as 1/d²), and the aluminium must stay below ~200 °C. Sputtered atoms at 10⁻³–10⁻² mbar have a mean free path of 1–10 cm, so at this throw the flux is diffuse, **not line of sight**: the cos(incidence) profile of `CU_LINER.md` §2 holds for evaporation only, and a sleeve mask leaks. Cu straight onto Al's oxide adheres poorly (~6 MPa on alumina without pretreatment [read]); no adhesion or stress data were found for > 10 µm. The route with a precedent is a **1–3 µm sputtered seed (with a Ti or Cr adhesion layer), then electroplating** (CERN's standard Cu-on-Al sequence [read]). |
| Li | 20 µm *evaporated* from the axis through a Ø4–6 mm mask | LNL presses rolled foil. A "dedicated evaporator" was reported in 2015 with no result since (§2.1): ask. The far-source geometry needs gram charges (§4.4). The mask's job, a film that is constant along the beam on the steep flank, exists only because of the ogive's shape (§6.1). |

And what it buys (reference fit, `nd_reach.csv`, 1.10 MeV):

| | big plastics | as built, liquid repaired | as built, liquid as at n_TOF |
|---|---|---|---|
| his Cu ogive 200 µm, Li film as in L11 (uniform, with the flank's 17.64 MeV excess) | 1.4 d | 6.1 d | 11 d |
| his Cu ogive 200 µm, clean Li (tip only / line of sight) | 1.5–1.6 d | 7.4–7.6 d | 14–16 d |
| Al 300 + Cu 12 at r ≤ 8, Li r ≤ 4 | 0.43 d | 4.4 d | 8.7 d |
| **Al 400 + Cu 12, Li r ≤ 4 (the wall we recommend, for the x-rays)** | 0.64 d | **6.1 d** | **11 d** |
| Al 300 + Cu 12 plated everywhere, Li on the tip only | 0.42 d | 3.5 d | 6.0 d |

- With the detector we have, the recommended 0.4 mm version is **×1.0–1.3 faster than his copper ogive**
  (like for like on the lithium: ×1.2–1.3), which is inside the ±25 % spread of the two estimators; the 0.3 mm
  wall gives ×1.4–1.7 but 12 % x-ray occupancy per µA. The gain of ×2.4–3.5 is real only with the big plastics,
  which are the 266 k€ budget. L13 will firm up the as-built column.
- **Plating the whole inside loses nothing** (0.42 against 0.43 d; as built 3.5 / 6.0 against 4.4 / 8.7 d, within
  the Monte Carlo; simulated at 0.3 mm only). The r ≤ 8 Cu patch and its sleeve mask are complexity without a
  return: drop them.
- So the honest message to Pierfrancesco is not "your Cu ogive costs ×3.5". It is "with today's detector your Cu
  ogive is within a factor ~1.5 of anything we can build quickly; the light wall pays once the calorimeter is
  upgraded".

### 4.2 New: a 20 µm lithium film that turns into hydroxide reaches the 441 keV resonance

`TARGET_OPTIONS.md` §6 estimated how fast residual water converts metallic Li (1.35 µm a day at 10⁻⁷ mbar of
water, sticking 1) and concluded "the products stay on the target, so the Li is not lost: the yield per µC drops
slowly". That was checked for the thin Li₂O film only. For a 20 µm metal film it misses the main effect: the
oxygen and hydrogen add stopping power, so the same lithium atoms take much more energy from the beam.

`review_li_conversion.py` (the repo's yield model, PSTAR stopping; the outer fraction of the Li atoms converted,
the rest metal) → `out/target/options/review_li_conversion.csv`. Share of the γ₀ that comes from the 17.64 MeV
(441 keV) resonance, and in brackets the energy at which the beam leaves the film:

| E_p 1.10 MeV | fresh | 25 % LiOH | 50 % LiOH | 75 % LiOH | 100 % LiOH | 100 % Li₂O |
|---|---|---|---|---|---|---|
| Li 20 µm | 0.85 % (872 keV) | 2.8 % (684) | **52 % (454)** | 77 % (stops) | 77 % | 5.6 % (537) |
| Li 15 µm | 0.7 % (933) | 1.5 % (801) | 3.7 % (653) | **27 % (480)** | 77 % | 1.7 % (705) |
| Li 12 µm | 0.6 % (968) | 1.0 % (866) | 1.9 % (756) | 3.8 % (634) | 10 % (495) | 1.2 % (794) |
| Li 10 µm | 0.6 % (991) | 0.9 % (908) | 1.4 % (820) | 2.0 % (725) | 2.7 % (621) | 0.9 % (850) |

| E_p 1.03 MeV | fresh | 25 % LiOH | 50 % LiOH | 75 % LiOH | 100 % LiOH | 100 % Li₂O |
|---|---|---|---|---|---|---|
| Li 20 µm | 1.4 % (790) | 6.6 % (586) | **91 % (319)** | 79 % | 79 % | 78 % (421) |
| Li 15 µm | 1.0 % (854) | 2.7 % (713) | 10 % (552) | 83 % (350) | 79 % | 3.5 % (608) |
| Li 12 µm | 0.9 % (891) | 1.8 % (783) | 3.8 % (665) | 12 % (530) | 79 % (368) | 2.0 % (705) |
| Li 10 µm | 0.8 % (915) | 1.4 % (828) | 2.4 % (734) | 4.4 % (631) | 8.5 % (515) | 1.5 % (766) |

- **What it means.** The 441 keV resonance is ~50× stronger than the 18.15 MeV one. Once the beam reaches it
  inside the film, the 17.64 MeV γ-rays and their pairs become most of what the detector sees, the trigger rate
  rises several-fold, and the 18.15 MeV signal sits under a background that was not in the design. The fit bias
  test of `TARGET_STUDY.md` §8 covered a drift of the 441 share up to 20 %, not this.
- **How fast.** With the repo's own (upper-limit) rate, half of a 20 µm film is hydroxide after ~7 days at
  10⁻⁷ mbar of water and after less than a day at 10⁻⁶ mbar. The real rate is lower: an LiOH layer "has
  passivated the surface" in ultra-high-vacuum studies [read, 6], and BINP and PTB both report a compound layer
  that grows slowly during operation. Nobody has published the rate for a 20 µm film under a µA beam at 10⁻⁶–10⁻⁷
  mbar, which is the regime of an unbaked line ending in a PVC tube. **It is unknown, and a run lasts 6–50 days.**
- **It applies to every design**, including his Cu cup and Cu ogive: it is a property of the film, not the shell.
  It did not matter for the CN neutron work, where the film's energy loss only shapes the neutron spectrum.
- **What to do:**
  1. **Make the film 10–12 µm, not 20.** At 1.10 MeV a 12 µm film gives at most 10 % from 17.64 MeV even if all
     of it becomes LiOH, and 10 µm at most 2.7 %. LNL rolls "down to sub-10 µm" already. The cost is yield: 12 µm
     gives 61 % and 10 µm 51 % of the 20 µm γ₀. With big plastics, where the fit is limited by the background
     shape, that costs less than proportionally in days; as built, close to proportionally (×1.6–2).
  2. **Run at 1.10 MeV, not 1.03**: 70 keV more margin, for ~20 % fewer days anyway.
  3. **Watch it.** The γ₀ yield per µC is the alarm: it *rises* by several times as the beam reaches 441 keV. A
     LaBr₃ or the Ge planned for PIGE separates 17.64 from 18.15 MeV. Replace the target when the share passes a
     few per cent; targets are cheap.
  4. **Measure the rate before the run**: one film on the AN2000 or CN line for a week at the vacuum we will have,
     following 478 keV and γ₀. This was already "measurement 3" of `TARGET_OPTIONS.md` §12; it is now the one that
     decides the film thickness.
  5. The cold trap upstream (§17 of TARGET_OPTIONS) stays. No PVC next to the target if it can be avoided.

### 4.3 Molybdenum stops are out at 1 µA

The Geant4 PIXE check of 4 Nov found the Mo K x-ray yield ×2.0–2.2 the estimate used until then (`CU_LINER.md`
§6). Micromegas occupancy per arm per µA: Al 0.3 mm + Mo ~19 %, the diamond window ~30–45 %, Be + Mo ~29 %.
At 17.5 keV no thin low-Z wall absorbs them. With the working limit of 10 % per arm these designs run at
0.2–0.5 µA, which gives back their advantage. The correction was recorded but the designs were not withdrawn:
**designs 3, 6, 7 and 8 as drawn are not usable at the documented current.** With a Cu, Ta or Ti stop instead,
7 and 8 fall under §4.5; 3 becomes 4.

### 4.4 Sputtering is not "line of sight", and the lithium charge is large

Two assumptions of `CU_LINER.md` §2–3 and §8 do not hold as written:
- **Sputtered copper does not arrive ∝ cos(incidence) at a 150–400 mm throw** (gas scattering, §4.1). It does not
  matter for the stop: any profile with ≥ 12 µm along the beam at the tip works, and a uniform plated layer is
  fine (§4.1). It would matter if the same argument were used for the lithium.
- **Evaporated lithium is line of sight**, so the constant-along-the-beam film of `CU_LINER.md` §3 is right, but
  the source must then sit far out on the axis, and the charge is 0.8 g (150 mm) to 5.4 g (400 mm) per coating,
  nearly all of it on the mask and the chamber. BINP loses ≤ 2 % because its source is close-coupled, which gives
  a film along the normal, not along the beam. Whether the group's 2015 evaporator exists, works, and takes gram
  charges at a 150–400 mm throw is an (ask).

### 4.5 The diamond window: no longer justified

It came from Pierfrancesco's 1 mm micro-channel diamond for a high-power target. Our own study showed the cooling
is not needed at LNL; since then the current has become 1 µA (1.1 W).
- **Heat.** A flat Al 6061 disc 0.4 mm thick over Ø20 carries 1.1 W with a 5 K rise centre to edge (19 K at
  4 µA) (ESTIMATE, radial conduction).
- **Leptons.** Ray-trace, same method as TARGET_OPTIONS §17 (`review_alt.py` → `review_alt_trace.csv`, ESTIMATE):

  | 45° end cap, Ø20, Al end piece 0.5 mm | x/X₀ per leg (median) | σ68 (trace) | against the diamond |
  |---|---|---|---|
  | Mo 8 / diamond 300 in Ti rings (design 7; Geant4 9.1°, 0.31–0.35 d) | 0.62 % | 7.27° | reference |
  | **one-piece Al cap, Cu 12 / Al 300** | 0.63 % | 7.26° | 0.0° |
  | one-piece Al cap, Cu 12 / Al 400 | 0.66 % | 7.54° | +0.3° |
  | one-piece Al cap, Cu 12 / Al 500 | 0.69 % | 7.80° | +0.5° |
  | Cu foil 25 / Al 300 | 0.65 % | 7.49° | +0.2° |
  | Ta foil 10 / Al 300 | 0.67 % | 7.67° | +0.4° |
  | Cu 12 / Al 300 with a 0.3 mm end piece | 0.43 % | 6.88° | −0.4° |
  | Cu 12 / Al 300, face ⊥ beam | 0.66 % | 7.63° | +0.4° |

  The trace reads ~2° below Geant4 for these designs, so only the last column should be used. It says the
  diamond buys nothing: the end piece, not the window, is what the leptons see.
- **Risk and cost.** A brittle disc as the accelerator's vacuum wall and beam stop, glued in rings, with no
  measurement of MeV-proton hydrogen damage in diamond (our own "gap"), sputtered with 8–10 µm of a metal that
  needs a carbide-forming bond. Bare discs list at 5–7 k$ for Ø20–25 × 0.7 mm optical grade [vendor]; a mounted
  0.3 mm window is 6–15 k€ and 8–16 weeks (ESTIMATE; no mounted price is published).
- The 45° **geometry** is the valuable part of this design. Keep it; replace the diamond (§6.1).

### 4.6 Beryllium is a procurement dead end

- The last supplier of machined and welded UHV Be tubes stopped in 2023, so CERN built its own facility
  (CERN news page, [read]). Whether a Be shop would still quote a one-off shell is an (ask); it is not a
  catalogue or a short-lead-time item. Standard flat Be windows in CF flanges are still catalogue parts (a DN16, 0.127 mm one was 1.7 k€ in 2018
  [vendor quote]); a pointed 0.3 mm shell or a 0.5 mm end piece is not.
- A custom shell: 20–60 k€ and 6–12 months (ESTIMATE; our §20 said 5–25 k€ and 3–6 months, before this was
  known), plus LNL's safety office and the EU 0.2 µg/m³ limit in force since July 2026.
- All Be designs here also carry the Mo stop (§4.3).
- Drop designs 6. If a lighter wall than 0.4 mm Al is ever needed, a *catalogue flat Be window* at 45° is the
  only realistic beryllium part.

### 4.7 Smaller mechanical points

- **His Cu ogive at 200 µm has a buckling margin of ~2–3** at 1 bar (ours: ×2.9; an independent estimate: 2.6 bar
  for the equivalent cylinder, more with the curvature). Soft annealed spun copper with a dent could collapse.
  **Electroform it** on a turned aluminium mandrel that is then dissolved: CERN made a 200 µm-wall Cu chamber this
  way, DC-plated copper UTS 352 MPa [read]. 1.5–5 k€ commercial, ~0.5 k€ in-house (ESTIMATE). Or 0.25 mm.
- **Pressing a rolled foil into the ogive's tip.** The tip is a sphere of R 2.8 mm. A flat 20 µm disc pressed
  into it stretches and thins unevenly, and whatever overlaps the 65° flank is ×2.4 thicker along the beam, which
  is the 441 keV problem of TARGET_OPTIONS §19.4 again. A disc that stays on the tip cap (r ≤ 2.5 mm) takes 55 %
  of a σ 2 mm beam. His earlier hemisphere (R ~11 mm) does not have this problem; nor does a flat face.
- **Hydrogen in copper.** Our "blisters after ~5 days at 1 µA" uses thresholds measured at Novosibirsk at 2 MeV
  and BNCT current densities (0.4–3 × 10¹⁹ /cm² depending on purity [snippet, 18]; the current density is my
  recollection of that work, check the paper). At 1 µA on a σ 2 mm spot the flux is orders of magnitude lower, and MEG II stopped 8–11 µA in 25 µm of Cu for four weeks with "no
  significant target deterioration" [read]. It is a watch item, not a blocker, for all Cu stops. A 12 µm Cu
  *film* is the one case where a blister cap (6 µm) is half the film: one more reason for plated-through or foil
  copper, or for Ta, the standard backing in this energy range (threshold > 6.7 × 10²⁰ [snippet]).
- **Titanium as the stop** is better on hydrogen than our notes say: Ti is listed with Ta, V, Nb and Pd as
  dissolving hydrogen without blistering, and a Japanese BNCT design chose it for that [read, 12]. What is
  missing is any MeV-proton test of a 15 µm Ti *film*, and evaporated Ti has peeled from smooth substrates [read,
  20]. Sputtering 15 µm of Ti is also about twice as slow as Cu. Keep it as a variant only if LNL already coats Ti.
- **Fluorine next to the target.** With 20 µm of Li the beam reaches the stop at 872 keV, on the strongest
  ¹⁹F(p,αγ) resonance (risk 3 of SHAPES_GEANT §8). With 10–12 µm it arrives at 970–990 keV, off that one (the
  935 keV resonance is close below: check the table before relying on it), and a film that gains stopping
  (§4.2) drifts through both. Keep fluorinated greases and elastomers away from the target either way.

### 4.8 Budget

| design | first unit (ESTIMATE unless marked) | lead time | budget verdict |
|---|---|---|---|
| Cu cup (exists) | 0 | 0 | — |
| Cu ogive, electroformed | 1.5–5 k€ | 2–6 weeks | fine |
| Al ogive, turned, + Cu plated inside | 1–4 k€ + plating | 3–8 weeks | fine; the time is in making it work |
| Al ogive + sputtered patch + evaporated Li | parts 1–4 k€; **thin-film development not costed** | months | the hidden cost |
| tilted Al cap + Cu + pressed Li (§6.1) | < 1 k€ | 1–3 weeks | fine |
| diamond window, mounted | 6–15 k€ | 8–16 weeks | affordable, not justified |
| Be ogive / end piece | 20–60 k€ | 6–12 months | **no** |
| CFRP chamber + internal target (8, 9) | 4–15 k€ (budget line `chamber`) | 8–14 weeks | fine |

- The budget (`../../budget/items.py`: Lean 100 k€, Self 211 k€, Upgrade 266 k€) carries the target as "Lithium
  targets (Li₂O / LiF films), LNL target lab, borrowed" and a 4–15 k€ thin CFRP chamber. Both lines describe
  design 9, not what we now plan. They should be rewritten once a design is chosen; the totals will not move.
- A fast-closing valve upstream (5–10 k€ if LNL has none) is still not in the budget and is needed by every
  design in which the target is the vacuum wall.

## 5. Verdict by design

| # | design | budget | mechanics | technology at LNL | physics | verdict |
|---|---|---|---|---|---|---|
| 1 | Cu cup 300 µm, pressed Li | ✔ | ✔ exists | ✔ routine | 29–31 d as built | works today; slow. The commissioning target |
| 2 | Cu ogive 200 µm | ✔ | margin ×2–3: electroform in hard Cu | Li on a pointed tip is new moulds (ask) | 6–11 d as built, 1.4 d big | **feasible; the simplest step up** |
| 3 | Al ogive + Mo | ✔ | 0.3 mm wall needs care | Mo deep in a cone: development | x-rays 19 %/µA | drop (→ 4b) |
| 4 | Al ogive + Cu patch + masked evaporated Li | ✔ parts | 0.35–0.4 mm wall needs care | **three new steps** | 4–11 d as built, 0.4–0.6 d big | not now; gain is small as built |
| 4b | Al ogive, Cu plated everywhere, pressed Li on the tip | ✔ | same wall | seed + plate has a precedent; Li as in 2 | 3.5–6 d as built, 0.42 d big (0.3 mm; ~×1.4 slower at 0.4 mm) | **the ogive worth trying after 2** |
| 5 | Al ogive + Ti 15 | ✔ | same | thick Ti film untested | as 4 | only if LNL coats Ti already |
| 6 | Be shells | ✘ | brittle wall | no supplier | best on paper | **drop** |
| 7 | diamond window 45° + Mo | ✔ | 300 µm, glued, brittle | Mo on diamond: development | x-rays 30–45 %/µA | **drop the diamond and the Mo, keep the 45°** |
| 8 | flat Li/Mo/diamond 50 in CFRP | ✔ | 50 µm membrane, chamber | most parts new | x-rays; 0.35 d big | drop |
| 9 | thin Li₂O or LiF on foil, chamber, dump | ✔ | chamber + dump | done on AN2000, and **the films broke in hours to two days** (§2.1) | 0.85 d big, 14–29 d as built | not a fallback: fragile at LNL and slow as built |
| **new** | **tilted one-piece Al cap, Cu stop, pressed Li (§6.1)** | ✔ | flat 0.4–0.5 mm: ×3.5–5.4 | flat parts, existing Li method | as 7 without x-rays (ESTIMATE) | **propose** |

## 6. Better ideas

### 6.1 A one-piece aluminium end cap with a flat face at 45°

The diamond-window design with the diamond, the rings and the glue taken out.

- **The part.** A short Al 6061-T6 tube end, Ø20 bore, wall 0.5 mm (0.3 mm if the workshop can), closed by a
  flat face at 45° to the beam, machined in one piece from bar, with a thick collar 50–60 mm upstream where it
  joins the line (as in the window design; the collar is out of the arms' view). A flat thin face is ordinary
  milling against a backing block; nothing is deep or pointed.
- **1 bar** (ESTIMATE, clamped ellipse 20 × 28 mm, Roark; yield 276 MPa): face 0.4 mm → 80 MPa, ×3.5; 0.5 mm →
  51 MPa, ×5.4; 0.3 mm → 142 MPa, ×1.9 (too thin unless the bore is Ø16: ×3.0). Use **0.4–0.5 mm**.
- **Heat:** +5 K across the face at 1 µA, plus the end piece (~6 K): the film stays near room temperature.
- **The stop.** ≥ 12 µm of Cu along the beam is 8.5 µm along the normal of a 45° face. On a flat face at a short
  throw this is an ordinary coating: a sputtered seed on a Ti or Cr adhesion layer and electroplated Cu, or plain
  sputtering for an hour or two. Coat the whole face and the first centimetre of the bore; no mask.
- **The lithium.** LNL's rolled foil, pressed with **flat** moulds, as they do now on the cup. For 12 µm along
  the beam (§4.2), an 8.5 µm foil. Any disc size up to the bore.
- **Why it is better than the ogive:**
  - the film's thickness along the beam is the same everywhere by geometry, so the flank problem, the Li mask
    and the line-of-sight coating all disappear;
  - the vertices lie within ±3 mm along the beam for a σ 2 mm spot, against 5–14 mm upstream on the ogive's
    flank, which cost ~25 % there;
  - it is the best *buildable* geometry in Geant4: the 45° window gave σ68 9.1°, 0.31–0.35 d (big plastics) and
    4.2–5.6 / 6.5–9.6 d as built (200–300 µm diamond), against 10.5°, 0.43 d, 4.4 / 8.7 d for the ogive with the
    liner, and the trace says aluminium for diamond changes nothing at 0.3 mm and +0.3–0.5° at 0.4–0.5 mm (§4.5);
  - Cu K x-rays leave through 0.4–0.5 mm of Al, as in the 0.4 mm ogive (2.5 % per arm per µA there; ESTIMATE
    here until simulated).
- **What it does not fix:** the Ø20 end piece is in the leptons' view (9.1° against 6.2° without it,
  SHAPES_GEANT §4.1). A 0.3 mm wall or the wide adapter of L11 are the levers, as before.
- **Not yet in Geant4.** One configuration line in the existing binary (§8).

### 6.2 Thinner lithium

10–12 µm instead of 20 (§4.2), for 51–61 % of the γ₀ at 1.10 MeV (15 µm: 77 %). The single-arm rate falls in
proportion. Decide after the one-week film test.

### 6.3 If the ogive stays

1. His Cu ogive, **electroformed** (hard Cu, 200–250 µm), Li pressed on the tip cap only. Cheap, weeks.
2. The Al ogive at 0.4 mm with **Cu plated over the whole inside** (zincate or sputtered seed, then acid Cu to
   ≥ 12 µm at the tip with an anode wire on the axis), baked, Li pressed on the tip. No sputtering deep in the
   cone, no masks, no lithium evaporator.
3. Ask whether a **rounder tip** (R 6–8 mm instead of 2.8) is acceptable to him: it takes 95 % of a σ 2 mm beam on
   the cap, so a pressed disc works and the flank no longer matters. It needs a Geant4 check of what it costs
   the leptons.

### 6.4 If evaporated lithium is wanted anyway

Copy Novosibirsk, not the beam pipe: a small evaporation stand that takes the end cap on a gate valve, a
close-coupled source, the film's thickness from the weighed charge, and the cap carried to the line under vacuum
behind its valve. On a 45° flat face a close source still gives a film that is uniform along the beam.

### 6.5 A tantalum stop

Ta is the standard backing at this energy (LUNA, PTB) because it takes up hydrogen without blistering. A 10 µm
Ta foil or film in place of the Cu costs +0.4° in the trace; its L x-rays (8–9 keV) are stopped by the same
aluminium as Cu K. Worth asking if LNL has it at hand; not needed for a first run.

## 7. What to ask Pierfrancesco now

Replacing the questions of `CU_LINER.md` §9:

1. **How does he intend to put the lithium on his ogive?** Pressed foil with new moulds for the pointed tip, or
   evaporation? His 2015 paper mentions a dedicated lithium evaporator: does it exist and work today, what
   thickness and area does it give, and how does the target leave it (under vacuum, under argon)?
2. To be clear about our 4 Nov proposal: we do **not** need anything deposited in the beam pipe. We meant a
   coating chamber. Given how his group works, would he rather have a part on which his rolled-and-pressed
   lithium works directly?
3. Would he consider a **flat face at 45°** instead of the point (§6.1)? It keeps his method and removes the
   flank.
4. Can the LNL workshop turn a 0.4–0.5 mm aluminium wall, and can the targets group (which sputters 100 µm of Mo
   on copper) put 10–15 µm of copper on a flat aluminium face *below ~150 °C*, or would a plating shop do it?
5. **The vacuum at the target** on the line he has in mind (pressure, what the residual gas is, PVC or ceramic
   insulator), and whether a film can sit there for a week under beam while we watch the 478 keV and γ₀ lines.
6. How thin can a rolled foil be made reproducibly (we would like 8–12 µm), and how is it carried from the
   glovebox to the line?
7. The beam spot (σ and halo) at the target, as before.

## 8. Next steps

1. **Geant4, one small run (L14) with the existing binary** (`mx17_full_sim_culiner_812488b`, the L10 window
   geometry and analysis). Lines for a new `shapes/lxplus/l14_configs.sh`, by analogy with `l10_configs.sh` /
   `l11_configs.sh` (`$WIN` without the Ti rings; check the ring flag there before submitting):
   - `CFG[cap45al400cu]="$WIN --win-plane 10:45 --film Li:748 --backing Cu:8.5+Al:400"` (20 µm Li along the beam);
   - `CFG[cap45al500cu]="… --backing Cu:8.5+Al:500"`;
   - `CFG[cap45al400cu_li12]="… --film Li:449 --backing Cu:8.5+Al:400"` (12 µm along the beam; yields rescaled);
   - the same with `--win-endpiece Al:0.3:55` and with the wide adapter;
   - the Cu K x-ray library for one of them.
   Submit after L13 has cleared the queue, at low job priority.
2. Fold thinner lithium into `shapes_nd.py` (a yield and line-mix change only): days for 10 / 12 / 15 µm.
3. Withdraw the Mo and Be designs from the decks and the target page, or mark them "not buildable at 1 µA" /
   "no supplier"; rewrite the two budget lines (§4.8).
4. Correct `CU_LINER.md` §8 (sputter rate and "line of sight") and `TARGET_OPTIONS.md` §6 (the hydroxide
   conclusion) with pointers here. Done as notes on 2026-11-11; the decks still show the old text.
5. The one-week film test at LNL (§4.2, item 4) goes on the list for the first contact about beam time.

## 9. Code and outputs

- `review_li_conversion.py` → `../out/target/options/review_li_conversion.csv` (§4.2).
- `review_alt.py` → `../out/target/options/review_alt_trace.csv` (§4.5; needs `L9_SEL`, `LNL_SEL`).
- Stress and heat of the flat cap: closed forms quoted in §6.1 (Roark clamped ellipse,
  σ = 6 q b² / [t² (3 + 2α² + 3α⁴)], α = b/a; radial conduction ΔT = P/(2πkt)·[ln(a/r_spot) + ½]).
- Evaporation charge: m = π d² ρ t for a small-area (cosine) source on the axis.

## 10. Sources

Literature search of 2026-11-11 (three web-research agents; tags as in the text). Numbers in the text refer to
this list. Not re-read by me beyond the files in `../refs/`: treat a [snippet] as a lead, and check any [read]
quote in its source before it goes into a talk or a message.

1. BINP, JINST 15 P10006 (2020): bnct.inp.nsk.su/publics/2020/2020_JINST_15_P10006.pdf
2. BINP lithium deposition system: bnct.inp.nsk.su/publics/2019/16.pdf
3. Ishiyama, Mater. Trans. 54, 1760 (in-situ Li deposition, Li₃N overcoat).
4. Lederer et al., PTB, PRC 85, 055809 and poster (indico.cern.ch/event/83067).
5. Karlsruhe activations: arXiv:0806.2063, arXiv:0805.4747.
6. Oxidation of Li films: osti.gov/servlets/purl/1392280.
7. BINP yield paper: pmc.ncbi.nlm.nih.gov/articles/PMC8465961.
8. BINP in-situ RBS of the Li layer: bnct.inp.nsk.su/publics/2025/tro-09-AB002.pdf.
9. arXiv:1403.1285 (a Li-on-Ta target found as Li₂CO₃).
10. LNL CN quasi-monoenergetic neutrons, arXiv:2605.12005 (`../refs/`).
11. arXiv:2603.04471 (Notre Dame, 100 µm Li on Cu).
12. Liu et al., Prog. Nucl. Sci. Technol. 7, 381 (RANS-II target; Ti against blistering).
13. Sas et al., arXiv:2205.07744 (ATOMKI; Li into the Al backing).
14. Rupp et al., J. Phys. Chem. Lett. (2019), doi:10.1021/acs.jpclett.9b02014 (Li diffusion in Cu).
15. Tran The Anh et al., arXiv:2401.11676 (Hanoi).
16. MEG II, arXiv:2411.07994.
17. Góngora-Servín et al., Acta Phys. Pol. B Proc. Suppl. 18, 2-A13 (2025) (`../refs/`).
18. Badrutdinov et al., Metals 7, 558 (2017) (blistering thresholds).
19. LUNA review, arXiv:1707.07952.
20. Hunt et al., NIM A (osti.gov/pages/servlets/purl/1610385) (Ti films peeling).
21. CERN electroforming (L. Lain Amador, indico.cern.ch/event/1025940): 200 µm-wall Cu chamber; Cu-on-Al sequence.
22. Thin-wall machining guide (rapiddirect.com, vendor); LHCb VELO upgrade, arXiv:1302.6035.
23. Sputtered Cu on alumina adhesion (NTU record 10356/86256); sputter-rate note (angstromsciences.com).
24. CERN beryllium beam-pipe production (home.cern/cern-begins-beryllium-beam-pipe-production); VACOM quotation
    10110525 (2018); Directive (EU) 2019/983.
25. Coherent CVD diamond windows via Edmund Optics (Ø20 × 0.7 mm $5,190; Ø25 × 0.7 mm $6,930); Diamond Materials
    UHV windows (no price published).
26. Mastinu et al., Nuovo Cimento C 38 (2015) 193, doi:10.1393/ncc/i2015-15193-y (micro-channel Li target;
    "dedicated evaporator"); slides elamatscience.ifj.edu.pl/slides/Mastinu_slides.pdf.
27. Torres-Sánchez et al., arXiv:2311.06143 (LNL Tandem; 200 µm Li pressed on a hemispherical 300 µm Cu backing).
28. B. Góngora-Servín, PhD thesis, Ferrara 2025 (sfera.unife.it/handle/11392/2586232): LiF targets and their
    lifetimes on AN2000. A copy is in `~/Downloads/PhD_Thesis_Gongora.pdf` (32 MB, saved by the search).
29. LNL targets group, EURO-LABS meeting May 2026
    (indico.in2p3.fr/event/39016, "EUROLABS_2026 GSI meeting_final_INFN_LNL.pdf").
30. Skliarova et al., Molecules 24 (2019) 25 (110–125 µm Mo sputtered on Cu at LNL); Garcia Diaz et al., SRF2021
    SUPCAV007 (30–45 µm Nb inside 6 GHz cavities).
31. LNS target laboratory: chetec-infra.eu/jra/star/infn-lns_uke.
