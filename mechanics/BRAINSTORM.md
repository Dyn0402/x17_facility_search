# Mechanics for a horizontal beam: brainstorm

*Started 2026-11-18. This is a brainstorm. The numbers are ESTIMATES from textbook formulas
(`mech_estimates.py` → `out/*.csv`) unless a source is given. Facts that only the n_TOF builders know are
marked **(ask)**.*

## 0. The problem in one paragraph

At n_TOF EAR2 the beam is **vertical**: sim +Y is up, and the four arms stand around it as vertical walls.
The LS necks on B and C point up (+v), and the SiPM bars run vertically. Gravity acts in the plane of
every detector face. Every other site in this repo (ILL, LNL, Demokritos, Birmingham, FRANZ, NFS, …) has a
**horizontal** beam, so the arm plane becomes vertical and gravity now acts across some faces. The
Geant4 work already allows for this in one place: the ILL and LNL cosmic runs put the zenith along sim z
(`--vertical-axis`, arms A/C on top and bottom; `ill/FEASIBILITY_SIM.md`). Nothing so far covers the hardware:
the frame, the target support, or how each subsystem behaves when it is turned 90°.

**The physics acceptance does not change** with the roll angle about the beam, because the source is
isotropic and azimuthally symmetric. Two things do: the cosmic topology, and what gravity does to each
subsystem. So the roll angle is a free design choice.

## 1. The main choice: "plus" or "X" roll

| | **Plus** (arms at 0/90/180/270°: one top, one bottom, two sides) | **X** (rolled 45°: every arm tilted 45°) |
|---|---|---|
| Gravity across a face | full on top and bottom, none on the sides | 0.71 × full on all four arms |
| Arms alike? | two kinds (horizontal, vertical); top ≠ bottom (the cathode sags opposite ways) | **all four alike**, so one calibration and one mounting design |
| LS vessels (§3.4) | top and bottom slabs lie flat, and the expansion bubble spreads over the face | every neck can point 45° up, so the bubble stays in the neck/funnel as at n_TOF |
| SiPM bars (§3.2) | flat on top and bottom, so they bend about the weak axis | bend at 0.71 × that on every arm |
| Cosmics | studied: faking muons go 57 % top + bottom (`ill/FEASIBILITY_SIM.md`); chord angles peak 110–130° | **not simulated.** Muons near the axis pass through the top and bottom corners and miss every arm; off-axis ones hit two *adjacent* arms at 45° incidence. Needs a rolled zenith in the cosmic generator |
| Lowest point below the beam axis | ~51 cm (back of the bottom LS) | ~53 cm (outer corner of the lower arms) |
| Already in Geant4 | yes (`--vertical-axis z`) | no (§5.2) |

**Leaning X**, provided the cosmic simulation does not show it is worse. It removes the two worst
gravity cases (a flat LS slab and flat SiPM bars) and makes the four arms identical. A frame that can
*roll* (§2) keeps both options open, and rolling by 90° in a run swaps which arm is on top: a free
check of gravity- and cosmic-related systematics.

## 2. The frame

At n_TOF the arms stood on the EAR2 floor or a platform, with the beam pipe rising through the middle
**(ask: how were the arms held? CAD or photos of the n_TOF stand)**. A horizontal beam needs a new structure.

**Concept: two end rings plus rails.** Put one square or round ring upstream and one downstream, both
outside the trigger stack's ±25–27 cm along the beam. Join them with four longitudinal rails, and bolt each
arm to two rails. This keeps all structure outside the lepton acceptance, because it sits along the beam
beyond the arms. It matches the LNL beam-line finding: every support must be ≥ 27 cm upstream
(`lnl/target/TARGET_OPTIONS.md` §18).

- The rings must be **split or C-shaped**, so they can be installed around an existing beam line.
- **Round rings on rollers** allow any roll angle: plus, X, or a 90° swap.
- **Loads.** Known parts are ~16 kg per arm (MM ~4.5, scintillators ~3, LS ~8). The DREAM FEUs,
  enclosures and fixings are not counted **(ask)**. That gives ~60–100 kg for four arms as built. A
  75 × 75 × 5 cm big plastic is **29 kg**, so big plastics add ~115 kg. Total: ~100–250 kg with nothing
  exotic. The difficulty is not the mass but that part of it hangs overhead (§4).
- **Stiffness is set by the alignment, not by strength.** The MM measure position to 0.6–0.8 mm, so frame
  deflection between survey and running should stay ≲ 0.1–0.2 mm. Survey in the final orientation and under
  load, then align with cosmics. Top–bottom cosmics are plentiful and cross two arms in a straight line,
  which helps here.
- **Beam height.** The envelope is ~51–53 cm below the axis (§1). Frame feet push that to ~0.65–0.75 m, which
  fits LNL's ~1.2 m line (`lnl/AUDIT_2026-10-26.md` A2). Every other facility: **(ask)** the beam height
  and the free floor.
- **Seismic.** Greece (Demokritos) is high-seismicity, and northern Italy and Grenoble are moderate. A
  frame with overhead mass and a liquid on it will probably need anchoring to the facility's code **(ask
  each facility)**.

## 3. Subsystem by subsystem

### 3.1 Micromegas TPCs

Construction (MX17_Geant `design/GEOMETRY_FROM_CAD.md`), going inward from the target side:

- 60 µm mylar window on a 5 mm Al flange;
- a 5 mm gas gap;
- the drift cathode: 50 µm Kapton with 9 µm Cu, 406 mm free span;
- a 30 mm drift gap in the Al gas frame;
- the 1.7 mm readout board with the mesh;
- rohacell, then an 8 mm Al backing ring with a 402 mm aperture.

- **Drift cathode: the one MM part where gravity matters.** It has gas on both sides, so its only
  out-of-plane loads are its weight (1.5 N/m²) and electrostatics. The drift field pulls with only
  2×10⁻³ N/m². A grounded window 5 mm away would pull with ~0.2 N/m² **(ask: window potential)**. The sag
  therefore depends on how tightly the foil was stretched, which nobody has written down **(ask)**:

  | foil tension | sag, face horizontal | drift-gap change | X roll |
  |---|---|---|---|
  | 5 N/m (barely taut) | 3.1 mm | 10 % | 7 % |
  | 20 N/m | 0.8 mm | 2.6 % | 1.8 % |
  | 100 N/m (well stretched) | 0.15 mm | 0.5 % | 0.4 % |

  At n_TOF this was zero. Horizontal, the gap **opens** at the centre on the top arm (the cathode hangs
  away from the mesh) and **closes** on the bottom arm. The result is a centre-to-edge change in drift field
  and in the drift-time-to-depth scale, opposite in sign on top and bottom. 233 V/cm sits on the rising
  part of the Ar/iC₄H₁₀ 90/10 velocity curve, so a few % in the gap is a few % in v_drift.
  **Fix if needed:** re-stretch the cathode, or add a few thin spacers. **Check:** lay a spare module flat,
  facing up and then down, and compare drift-time maps from cosmics or ⁵⁵Fe (§5.1).
- **Readout board.** Its weight (31 N/m² face down) deflects the bare 1.7 mm FR4 by 0.12–0.39 mm over 402 mm,
  an upper bound since the rohacell stiffens it. 1 mbar of gas overpressure does 3× more, and was already
  there at n_TOF **(ask: the operating overpressure)**. So gravity changes an existing effect by about
  ±30 %, with opposite sign on top and bottom.
- **Mesh.** The CAD puts the mesh inside the board, which suggests a **bulk** Micromegas: pillars hold the
  mesh, and gravity does not matter. If the mesh floats instead, its weight (~1 N/m²) against the
  ~70 N/m² of electrostatic pressure at amplification fields is a ~1 % effect on the top arm, and only with
  HV on **(ask: bulk or floating)**.
- **Window.** Its weight (0.8 N/m²) is ≪ 1 % of the gas-pressure bulge. Negligible.
- **Gas.** Ar/iC₄H₁₀ 90/10 is denser than air, so a leak pools at the floor: an oxygen-deficiency check and
  an isobutane flammability classification for each hall **(ask)**. Inside a horizontal chamber, light
  contaminants (water vapour, air) rise to the upper face. The inlet and outlet positions should flush it,
  and they were laid out for a vertical module **(ask: port positions)**. The n_TOF water problem
  (`slow_control/`) is no reason to add new dead volumes.
- **FEUs, connectors, cables.** Electronics that sat beside a vertical module now hang off its face or
  edge. The connectors need strain relief, so the cable weight is not carried by the board.

### 3.2 SiPM scintillator walls

These are 20 bars of 500 × 25 × 3 mm PVT, read at both ends, in a 62 cm enclosure. At n_TOF the bars hung
vertically, with no bending. Lying flat with only their ends held, each bar sags by **4.4 mm** (free ends) or
**0.9 mm** (clamped). The X roll gives 3.1 / 0.6 mm. On edge (the side arms in plus) the sag is
< 0.1 mm. The stress is small (0.6 MPa), but PVT creeps over a months-long run, a sagging bar pulls on its
end couplings to the SiPMs, and neighbouring bars can touch through their wrapping. **Fix:** a thin
support sheet under the bars (foam or a 0.5 mm Al/CFRP skin, which adds material in front of the plastics;
cost it in Geant4) **(ask: how the bars are held in the enclosure now)**.

### 3.3 Trigger plastics and big plastics

The as-built 20 × 30 × 2 cm bars (1.2 kg each) are fine in any orientation. A big plastic is 29 kg, and
the top one hangs over the target, so it needs a tray or frame, not tape. PMTs on light guides should be
**supported by themselves**. A PMT and base (~0.5–1 kg) cantilevered on a glued light-guide joint will
crack it if the joint is loaded sideways.

### 3.4 Liquid scintillator vessels: probably the hardest item

Each is a flat 45 × 45 × 2.1 cm CFRP slab, with a funnel and a Ø50 mm neck holding a half-inserted PMT, and
6.5 L of LAB (~5.6 kg). The Geant model has fill-dependent bulge domes (`DetectorConstruction.cc`). At n_TOF,
B and C had the neck up and D and A had it sideways (`ls_rot_deg`).

- **The bubble.** Any expansion volume collects at the highest point. With the neck up, that point is in the
  neck or funnel, away from the slab. **A slab lying flat (top or bottom arm in plus) spreads the bubble as a
  thin layer under its upper face.** That makes the active thickness non-uniform across the arm, and the
  bubble moves as the temperature changes. In the X roll, every neck can point 45° up, so this does not
  happen **(ask: is the vessel sealed or vented? bubble volume?)**.
- **Bulge and hydrostatics.** Standing up, the 45 cm column puts ~3.8 kPa on the bottom of the slab. Lying
  flat, it is ~0.2 kPa, uniform. The thickness profile, and the Geant geometry, therefore depend on
  orientation. Probably a small effect, but the sim's bulge domes should follow the real orientation.
- **Leaks overhead.** A top-arm vessel drips onto the target, the bottom arm and the electronics. LAB is not
  very flammable (flash point ~130 °C) or toxic, but a drip tray is needed. On the top arm the tray sits
  *in front of* the LS, in the leptons' path: thin, and costed in Geant4.
- **PMT orientation in Earth's field.** This changes with the roll angle, so the gains move by a few %.
  Recalibrate in situ, and check the mu-metal.

### 3.5 Target and beam line

- At n_TOF the capsule sat in a vertical pipe. Now every target is **cantilevered** off a horizontal line:
  the LNL thin CFRP chamber (`liChamberHalfLen` 300 mm, its wall sets the opening-angle resolution), the
  ILL/Birmingham ³He cells (a 30 bar × 40 cm vessel is heavy: `he3_target/`), the Demokritos Ti-T holder.
- **The thin window and chamber must carry no load.** Support the line both upstream and downstream
  ≥ 27 cm from the target, outside the arms. The LNL floor stand at ~17 cm goes through the bottom arm and
  must move (`lnl/target/TARGET_OPTIONS.md` §18). The beam dump (Cu stop, 250 mm downstream) and its cooling
  lines need their own support behind the arms, not on the chamber.
- **Bending of a long cell or chamber under its own weight and the vacuum load** moves the target off the
  detector axis. A few mm is harmless for acceptance, but it shifts the assumed vertex of the chord
  angle. Survey the target position under vacuum.

## 4. Safety, installation, access

- **Overhead loads.** The top arm, big plastic and LS hang above people during installation and above the
  target during running. Facilities ask for load calculations and rated lifting points; check each one's
  rules **(ask)**. Crane or hoist availability per facility **(ask)**.
- **Assembly sequence around an existing beam line.** Install the bottom half of the frame, then the side
  arms, the target, and the top arm last. A split ring helps.
- **Access.** Swapping a top-arm module or refilling an LS means lowering it. A frame that rolls (§2) can
  bring any arm to the side for service.
- **Transport.** The frame splits to pass doors and lifts **(ask: door sizes at the short-listed sites)**.

## 5. What would settle the open points

1. **Bench test, cheap and decisive:** run one spare MM module lying flat, facing up and then facing down,
   with cosmics or ⁵⁵Fe. Compare gain and drift-time maps with the vertical module. Fill one LS vessel and lay
   it flat to see the bubble. This could be done in the lab before any frame exists.
2. **Cosmic simulation of the X roll:** generalise `--vertical-axis x|z` in MX17_Full_Geant's cosmic generator
   to an arbitrary zenith (a roll angle about the beam). Rerun the ILL/LNL cosmic cuts (segment collinearity,
   TOF, E_sum window) at 0° and 45°. This decides the choice in §1. It is a small change: the change goes in
   MX17_Full_Geant on the active branch.
3. **Ask the n_TOF builders:** cathode tension and mounting, bulk or floating mesh, gas overpressure and port
   positions, window potential, how the SiPM bars are held, LS sealing and bubble volume, FEU and enclosure
   masses, and the n_TOF stand CAD.
4. **Ask each short-listed facility:** beam height, free floor, crane, floor load, seismic rule, gas-safety
   rules (Ar ODH, isobutane).
5. **Then a concept frame** (FreeCAD, like `vessel_design/`), with the materials it puts near the
   acceptance (support sheet, drip tray) added to Geant4.

## 6. Not affected

- Pair acceptance and the reach numbers (isotropic source).
- The Geant4 cosmic studies already done for ILL and LNL, which used a horizontal beam with zenith ⟂ beam.
- Everything electrical: HV, DREAM, trigger logic. Only cable routing and strain relief change.
