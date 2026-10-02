# A ⁴He bag around the ILL ³He target

2026-10-02. The question: air ¹⁴N is a significant background at the ILL
(`../ill/`). Would a ⁴He balloon around the ³He cell remove it? What would it
do to lepton scattering and to ³He loss through the cell wall?

It also covers the follow-up: the ³He leak rate turned out to be large, so
how do we make the cell tight without adding background or e⁺e⁻ scattering,
and should it stay at 1 bar?

Everything here is analytic. It is calibrated against the ILL Geant4 campaign
where that campaign has a number: the ¹⁴N(n,γ) rate on the air path matches
V0 to 1 %.

| file | what it is |
|---|---|
| `he4_bag.py` | All the arithmetic. §1 neutrons in air vs ⁴He; §2 Highland scattering on the cell → Micromegas chord; §3 ³He permeation of G1–G6, in air or in a ⁴He bag; §4 alternative skins for the 1 bar cell; §5 leak budget of seals and bonds; §6 choosing the foil (metal, gauge, scattering budget, strength) |
| `make_he4_bag_deck.py` | The slide note, built with `dylan-cern-site/scripts/slidedoc.py`. It reads `he4_bag.py` directly, so its numbers and titles follow the model |
| `out/neutrons.csv` | Captures and scattering per beam neutron on the 30 cm path, for air and for He at several air fractions |
| `out/leptons.csv` | θ₀ per leg vs lepton KE: air, ⁴He, ⁴He + bag foil |
| `out/permeation_bif{1,10}.csv` | Per cell: ³He loss per day and per cycle, cost, τ, ⁴He and air inflow, sealed-cell dilution |
| `out/he4_flush_bif1.csv` | Fresh-³He flow that holds ⁴He < 5 % in a cell sitting in the bag |
| `out/skins.csv` | Skin options for the G1 geometry: x/X₀, θ₀ at 6.3 MeV, loss range, barrel captures, hardest γ line |
| `out/seals.csv` | Leak budget: O-rings, epoxy bonds, foil pinholes, bare barrel |
| `out/metals.csv` | §6a: barrier metals (Al, Be, Mg, Zr, Cu, Pb) at their thinnest foil on 12 µm PET |
| `out/foil_gauge.csv` | §6b: Al gauge 6–25 µm: θ₀, captures, typical pinholes, barrel loss |
| `out/chord_budget.csv`, `out/chord_ladder.csv` | §6c: x/X₀ per layer of a lepton leg; θ₀ as the big layers are replaced |
| `out/hoop.csv` | §6d: membrane stress at 10 / 30 / 50 / 1000 mbar |
| `out/figures/he4_bag.png` (+ `.csv`) | Summary figure: ¹⁴N vs bag purity, and the sealed-cell ³He decay |
| `out/he4_bag_deck.html` | The slide note, live at <https://dylan-neff.web.cern.ch/notes/ill-he4-bag-3he-leak.html> |

```bash
python3 he4_bag/he4_bag.py              # tables -> he4_bag/out/
python3 he4_bag/make_he4_bag_deck.py    # -> he4_bag/out/he4_bag_deck.html
python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py he4_bag/out/he4_bag_deck.html \
        --slug ill-he4-bag-3he-leak --force --deploy
```

Inputs from `../ill/`:
- `out/h113_spectrum.csv`;
- the V0 and C1 rates quoted in `SIM_STATUS.md` and `FEASIBILITY_SIM.md`;
- `sim/analysis_v3/contract_ladders.csv` (wall captures).

It needs numpy, pandas, scipy and matplotlib. The figure uses
`ill/figstyle.py`.

**Assumptions to replace with measurements:**
- He permeability: PET ~1 barrer (literature, ~2×); Kapton 1 barrer
  (placeholder, sources differ ~10×). N₂ 0.006 and O₂ 0.03 barrer in PET.
- ³He permeates 10 % faster than ⁴He.
- Metallisation barrier factor (BIF): 1–10, unmeasured.
- Foil pinholes: ~50/m² at 9 µm.
- Viton O-rings: Parker rule, 9 barrer. Epoxy: 5 barrer.
- ³He at 2500 €/L(STP).
- ~10⁻⁴ barrel crossings per beam neutron.

## Bottom line

- **⁴He gives no ¹⁴N-like background.** It captures no neutrons at all,
  because there is no bound ⁵He. It also scatters neutrons ~13× less than air.
- **The air that matters is the 300 mm of open beam path** between the
  collimator aperture and the Be window, not the air around the cell.
  - The analytic ¹⁴N(n,γ) rate on that path is 2.54 × 10⁻⁴ per beam neutron.
    Geant4 V0 gives 2.5 × 10⁻⁴ (ratio 1.01).
  - All air in C1 gives 2.7 × 10⁻⁴/n. So ~90 % of the ¹⁴N(n,γ) is the
    direct beam in that path. The other ~10 % is scattered neutrons captured
    in air around the detector. (This split is inferred by comparing two runs;
    it was not tallied directly.)
- **So the sensible version of the idea is a He-filled (or evacuated) flight
  tube** from the aperture to the Be window, sealed onto the cell flange. It
  removes:
  - ~90 % of the air ¹⁴N(n,γ);
  - the 0.6 % ¹⁴N(n,p) loss;
  - the ~2 % of beam scattered in air.

  The He only has to be ~99 % clean: the remaining ¹⁴N scales with the air
  fraction (1 % air → 2.5 × 10⁻⁶/n, a 100× reduction). This is standard
  beamline practice and was already on the list in `FEASIBILITY_SIM.md` §6.4.
- **A balloon around the cell and detector is not worth it.**
  - What it would add: the remaining ~10 % of air captures, and ~20 % less
    lepton scattering, which is worth < 2 % in reach.
  - What it would cost: it floods a mylar cell with ⁴He (see below). He would
    also permeate the Micromegas entrance windows into their gas, and HV breaks
    down far more easily in He than in air.
- **Permeation: the bag neither slows nor speeds the ³He loss**, because the
  ³He partial pressure outside is ~0 in air and in ⁴He alike. **It does hurt
  through what comes in.** ⁴He enters the cell ~90× faster than N₂ + O₂ do
  from air (mylar), or ~20× faster (Kapton). A sealed cell in the bag slowly
  becomes ⁴He.
- **Side finding that matters more:** bare 12 µm mylar (G1) loses ~0.45 L(STP)
  of ³He per day. That is a 3.4-day time constant, ~22 L per 50-day cycle, of
  order 50 k€. The source figure is a literature PET He permeability of
  ~1 barrer, uncertain by ~2×. Either the metallisation gives a measured ≳10×
  barrier, or G1 needs a feed system and a budget for the loss. This sharpens
  the "G1 if permeation is manageable" caveat in `FEASIBILITY_SIM.md` §5.

## 1. Neutrons (H113 beam, mean λ 4.87 Å)

Cross sections: thermal values (Sears/NIST), scaled as 1/v for absorption. The
free-gas correction is applied for scattering.

| gas on the 30 cm path | ¹⁴N(n,γ) 10.8 MeV /n | ¹⁴N(n,p) /n | ⁴⁰Ar(n,γ) /n | scattered |
|---|---|---|---|---|
| air | 2.5e-4 | 5.8e-3 | 1.3e-5 | 1.6 % (G4: ~2 %) |
| He + 5 % air | 1.3e-5 | 2.9e-4 | 6e-7 | 0.19 % |
| He + 1 % air | 2.5e-6 | 5.8e-5 | 1e-7 | 0.13 % |
| pure ⁴He | 0 | 0 | 0 | 0.12 % |

- With the air path in He, the hardest remaining single-capture lines near the
  beam come from the Be window (1.4 × 10⁻⁴/n, 6.8 MeV) and the Al ring
  (1.5–1.9 × 10⁻⁴/n, 7.7 MeV). Both are well below the Esum > 13 MeV cut.
  - ¹⁴N survives in the Kapton walls (G3–G6) and in the air around the
    detector, so the 10.83 MeV endpoint does not go away. Its rate drops ~10×.
- Use mylar, not Kapton, for any tube window: Kapton contains N.
- The 2 % of the beam scattered in air may also feed some of the captures in
  the detector materials (~1 × 10⁻³/n), which dominate the Micromegas rate.
  Analytics cannot settle that. **One Geant4 rerun would:** C1 on G1 with the
  flight path set to G4_He. It would also give the change in Micromegas rate
  and in the accidental Esum tail.

## 2. Lepton scattering

Highland θ₀ per leg, for the G1 skin, the Micromegas entrance and 16 cm of
gas. The energies are the p10/50/90 of the softer X17 lepton and the median of
the harder one.

| KE [MeV] | air | ⁴He, bag sealed on the MM windows | ⁴He + 25 µm mylar foil | ⁴He + 100 µm foil |
|---|---|---|---|---|
| 4.1 | 5.0° | 4.0° | 4.2° | 4.7° |
| 6.3 | 3.4° | 2.7° | 2.8° | 3.2° |
| 9.1 | 2.4° | 1.9° | 2.0° | 2.3° |

- ⁴He reduces the scattering by ~20 %, as long as the bag foil is thin.
- The reach does not care. The opening-angle resolution is set by the
  assumed-vertex term (7.8° against 2.2° with the true vertex), and even ideal
  vertexing gains only 13 % (`FEASIBILITY_SIM.md` §1).

## 3. ³He permeation (Fick's law per species, barrel area only)

The model:
- Mylar: He 1 barrer, N₂ 0.006, O₂ 0.03.
- Kapton: He 1 barrer, a placeholder; sources disagree by 10×.
- ³He permeates 10 % faster than ⁴He (assumed).
- BIF is the barrier improvement factor of a metallisation; it is unmeasured.

| cell | ³He fill [bar·L] | loss, bare [L/day] | per cycle, bare | τ bare | τ BIF 10 | ³He left after 50 d sealed in the bag (bare / BIF 10) |
|---|---|---|---|---|---|---|
| G1 1 bar mylar R40 | 1.5 | 0.45 | 22 L (~56 k€) | 3.4 d | 34 d | 0 % / 23 % |
| G2 1 bar mylar R100 | 9.4 | 1.1 | 56 L | 8.4 d | 84 d | 0 % / 55 % |
| G3 2 bar Kapton R40 | 1.5 | 0.049 | 2.4 L | 31 d | 310 d | 20 % / 85 % |
| G5 3 bar Kapton R40 | 1.5 | 0.023 | 1.2 L | 65 d | 650 d | 46 % / 93 % |

What the bag changes:

- **³He out: unchanged.** It is driven by the ³He partial pressure, which is
  ~0 outside in either case.
- **What comes in.**
  - In air: N₂ + O₂ at 1/90 of the ³He loss rate (mylar). Over a sealed cycle
    that makes ~6 % N₂ in G1. That causes 2 × 10⁻⁶/n of in-cell ¹⁴N(n,γ),
    which is negligible.
  - In ⁴He: ⁴He at ~the ³He loss rate.
    - For the zero-Δp mylar cell this keeps the pressure balanced; in air the
      cell would collapse instead. But it dilutes the ³He, and the stopping
      length grows as 1/p(³He).
    - Holding ⁴He < 5 % in G1 needs ~8 L/day of fresh ³He flushed through
      (5 cell volumes a day). The outflow is a ³He/⁴He mix that can be reused
      only after isotope separation. For the Kapton cells it is 0.1–0.4 L/day.
- **The one upside:** permeated ³He goes into the bag instead of the hall. At
  < 1 % concentration in a flowing bag, though, it is not practically
  recoverable.

## 4. Stopping the leak without adding material (`he4_bag.py` §4–5)

- **Pressure doesn't make a cell tighter.** Permeation follows the ³He partial
  pressure. A pressure wall needs t = Δp·R/σ. At a fixed bar·L inventory, the
  loss goes as 1/(p − 1) and x/X₀ goes as (p − 1). So every polymer wall sits
  on the same loss × x/X₀ line, and so does bare PET at any thickness.
- **So stay at 1 bar, and make the skin a barrier rather than a wall.** Rolled
  Al foil is impermeable to He: gas gets through only at pinholes, of which a
  9 µm foil has ~50/m².
  - A 12 µm PET + 9 µm Al laminate is 1.4 × 10⁻⁴ X₀.
  - It raises θ₀ at 6.3 MeV by +4 % (3.37° → 3.49°).
  - Its barrel captures are ~10⁻⁸/n (Al lines ≤ 7.7 MeV), against
    3.8 × 10⁻⁴/n for the other cell solids.
  - The barrel loss is < 10⁻⁴ L per cycle, even with 100× more pinholes from
    creasing on the rods.
- **The leak then moves to the seals.** The Viton O-rings (Be window, Al cap)
  pass ~8 cm³ per cycle; the epoxy bonds pass ~10⁻⁵ L. Indium or metal seals
  would go lower.
- **This can be tested on the bench.** Bare G1 leaks ~5 × 10⁻³ mbar·L/s; a
  foil cell should leak ~2 × 10⁻⁶. A standard He leak detector reaches 10⁻¹⁰.
- Vapour-deposited Al (the existing 2 × 40 nm on the mylar) is not the same
  thing. Its He barrier factor is unmeasured and probably a few.

Slide note: `make_he4_bag_deck.py` → `out/he4_bag_deck.html`, published at
<https://dylan-neff.web.cern.ch/notes/ill-he4-bag-3he-leak.html>.

## 6. Choosing the foil (`he4_bag.py` §6, follow-up 2026-10-02)

Four questions. Is there a barrier better than Al that doesn't capture
neutrons? How thin can the foil go? What dominates the scattering, if not the
foil? Does a 1 bar cell need any strength?

**The foil is already outside the beam.** The beam at the window is
r50/90/99 = 7.1 / 10.2 / 12.9 mm (Geant4 V0), and the G1 barrel sits at
R = 40 mm. Only neutrons scattered in the ³He reach it, ~10⁻⁴ per beam
neutron, so a 12 µm PET + 7 µm Al skin gives ~1.3 × 10⁻⁸ captures/n. The
other sources are far larger:
- Be window: 1.4 × 10⁻⁴/n.
- Al ring and caps: 1.5–1.9 × 10⁻⁴/n.
- 30 cm air path: 2.5 × 10⁻⁴/n.

The Al that matters is the **8 mm end caps**. The upstream cap and ring are in
63 % of G1 accidentals (`../ill/FEASIBILITY_SIM.md` §9). Two Geant4 runs would
settle it:
1. C1 on G1 with the laminate skin. This needs a two-layer `--skin`;
   `Al:0.007` alone gives a bound.
2. G1 with the upstream cap lined with ⁶LiF, or trimmed, run through
   `acc_sources.py`.

**Aluminium is the right metal.** Each option below is at its thinnest
metre-size foil, laminated on 12 µm PET:

| metal | thinnest foil | capture/µm vs Al | X₀/µm vs Al | θ₀ 6.3 MeV | hardest γ | verdict |
|---|---|---|---|---|---|---|
| Al | 6 µm | 1 | 1 | 3.45° | 7.72 | use |
| Be | 8 µm | 0.07 | 0.25 | 3.40° | 6.81 | small brittle toxic discs, can't be wrapped |
| Mg | 25 µm | 0.19 | 0.62 | 3.58° | **11.09** | ²⁵Mg line above ¹⁴N |
| Zr | 10 µm | 0.57 | 5.7 | 4.09° | 8.63 | ×6 scattering |
| Cu | 6 µm | 23 | 6.2 | 3.85° | 7.92 | ×23 capture |
| Pb | 25 µm | 0.41 | 16 | 7.16° | 7.37 | ×16 scattering |

- Polymers and coatings are not He barriers: they gain ≲10×, against ≳10⁴×
  for a continuous metal foil. That covers vapour Al, AlOx/SiOx, EVOH and LCP.
- The choice of metal barely matters anyway. With Al, half of the barrel's
  ~10⁻⁸/n comes from the PET's hydrogen.

**Gauge: 6–7 µm converter foil.**
- Pinholes only matter at ~1.5 × 10⁶ per m², about one per mm². Only above
  that does the barrel reach the O-ring floor of 8 cm³ per cycle.
- Typical 6 µm foil has ~10³ per m². Even with ×100 more from creasing, the
  barrel stays ~15× under the floor.
- θ₀ at 6.3 MeV is 3.45° with 6 µm, 3.49° with 9 µm and 3.70° with 25 µm.
- **Order PET/Al only.** Stock packaging laminates add a 50–100 µm PE
  heat-seal layer, which has more X₀ than everything else in the skin.

**The scattering "base" is the detector, not the cell.** Share of x/X₀ on one
lepton leg:

| layer | share |
|---|---|
| Micromegas entrance, 9 µm Cu | 39 % |
| 16 cm air, cell → Micromegas | 33 % |
| Micromegas entrance, 50 µm Kapton | 11 % |
| Micromegas entrance, 40 µm mylar | 9 % |
| 7 µm Al foil | 5 % |
| 12 µm PET | 3 % |

θ₀ at 6.3 MeV for each configuration:

| configuration | θ₀ |
|---|---|
| no skin | 3.32° |
| 12 µm PET (G1 as simulated) | 3.37° |
| 12 µm PET + 7 µm Al | 3.46° |
| …and an aluminised Micromegas cathode instead of the 9 µm Cu | 2.63° |
| …and He on the 16 cm chord | 1.76° |

- The cathode is the cheap win. The 9 µm Cu is assumed to be the drift
  cathode's cladding; check that against the detector drawings.
- **Scattering does not set the reach.** The opening-angle resolution is 7.8°,
  dominated by the assumed vertex (§2).

**Strength at 1 bar: little, but not none.** At R = 40 mm the membrane
stress is σ = Δp·R/t:

| case | laminate | 7 µm Al alone |
|---|---|---|
| 50 mbar (±30 mbar weather + a few K on a sealed cell) | 11 MPa | 29 MPa |
| yield | PET ~100 MPa | soft Al foil ~35 MPa |

- Keep the PET as the load layer. Dropping it saves only ~1 % in θ₀.
- **The cell can't be pumped out to fill it.** A full 1 bar inward collapses
  the skin between the rods. Pump it down inside a vacuum enclosure, or
  flush-fill it, which wastes ³He.
- A bellows or a small reservoir on the fill line would hold Δp near 0.

Assumptions:
- The pinhole densities, thinnest foils and yields are catalogue-level, good
  to an order of magnitude.
- The barrel crossing rate is analytic.

## Verdict

The idea makes sense in a narrower form: **put the beam's air path in He (or
vacuum), not the target.** It is cheap, standard, and removes ~90 % of the
¹⁴N(n,γ), with an analytic rate that matches Geant4. Surrounding the cell
itself buys almost nothing more. It makes the permeation problem worse for the
mylar cell and adds He problems for the Micromegas and HV. The more urgent
item is G1's own ³He permeation. Stay at 1 bar, but use a rolled-Al-foil
laminate skin: 12 µm PET + 6–7 µm Al converter foil, with no PE sealant layer.
Fill it inside a vacuum enclosure, and leak-test a prototype before the design
freeze. The foil is outside the beam. The Al that drives the accidentals is
the 8 mm end caps, so line or trim those.
