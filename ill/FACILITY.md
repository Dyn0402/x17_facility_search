# The ILL, as far as an X17 run needs to know it

Research record, compiled 2026-10-01 from public ILL pages and the
literature (sources at the bottom; every number here has one). Facts first,
then what they mean for us. Anything marked **(ask)** could not be found
publicly and has to come from the instrument responsible.

---

## The reactor

| | |
|---|---|
| Source | High Flux Reactor, Grenoble: the most intense continuous neutron source for science. 57–58 MW nominal; there is no pulse and no flash. |
| 2026 cycles | **199**: 24 Mar – 11 May, 48 d, 56 MW · **200**: 8 Jun – 3 Aug, 56 d, 47.9 MW · **201**: 1 Sep – 29 Oct, 58 d, 46.2 MW |
| 2025 cycles | 197: 63 d at 42.5 MW · 198: 63 d at 41.2 MW, then 7 d at 55 MW + 14 d at 41.2 MW |
| Reduced power | Since 2025 most cycles have run at 41–48 MW, i.e. 72–84 % of nominal. No public explanation found **(ask)**. Instrument fluxes are quoted at full power and should be derated. |
| Future | The Associates (FR, DE, UK) committed to operation **until 2033** (6th Protocol, 2021); operation beyond 2030 was later confirmed. No 2027 cycle dates published yet. |
| Rhythm | Typically 3–4 cycles per year of ~50–60 days, ~150–200 beam days/year in total. |

**For us:** a realistic window is 2028–2032. Plan around ~50-day cycles at
~46 MW. The flux table in `ill_rates.py` carries a power factor for that.

## The instruments that fit

ILL's Nuclear & Particle Physics (NPP) group runs the beams in question. Three
are relevant.

### PF1B — the obvious one

| | |
|---|---|
| Beam | Cold, from the vertical liquid-D₂ cold source, via the **H113 ballistic supermirror guide** (m = 2, 76 m) in guide hall ILL7 |
| Capture flux | **2×10¹⁰ n/cm²/s** unpolarised (ILL page; one later paper quotes 2.2×10¹⁰ at the guide exit). Polarised: **3×10⁹** |
| Cross-section | **6 × 20 cm²** unpolarised; polarised 3 × 4.5 or 6 × 8 cm² |
| Spectrum | mean λ **4.0–4.5 Å** (≈ 4–5 meV). Capture flux / particle flux ≈ λ/1.80 Å ≈ 2.4 |
| Polarisation | 98 % (bender) or **99.7 %** (crossed supermirror polarisers); spin flippers > 99.5 % |
| Beam height | 140 cm above the floor |
| Character | A "bring your own experiment" facility. Users install complete setups in the casemate: PERKEO II/III, aSPECT, PERC (being commissioned), the EXILL HPGe array (2012–13), fission-fragment experiments. |
| Precedent for us | **PERKEO II at PF1B searched for n → χ + e⁺e⁻** (arXiv:1905.01912), a dark-sector e⁺e⁻ search at this beam, with a published background treatment. Read it before writing the proposal. |
| Unknowns **(ask)** | casemate floor area and crane; ambient γ / fast-n background in the casemate; spectrum table (we need dΦ/dλ for the Geant gun); divergence after the guide; ⁶LiF/B₄C collimation options; whether H113 has line of sight to the core (prompt γ / fast n carried down the guide) |

### FIPPS — the plug-and-play one

| | |
|---|---|
| Beam | **Thermal** guide H22, collimated to a **halo-free pencil beam of 1.5 cm diameter** |
| Flux | **10⁸ n/cm²/s** at target (≈ 1.8×10⁸ n/s in total) |
| Collimation | 5 circular apertures (10 mm, 4×12 mm) of neutron absorber, each backed by 5 cm Pb, in an evacuated tube lined with 1 cm borated plastic, 2.7 m long |
| Character | A fixed HPGe array around the target. Room for a foreign setup is **(ask)**. |

**For us:** the 1.5 cm halo-free pencil fits the as-built capsule's Ø20 mm
bore almost exactly. That is the strongest argument for FIPPS: the capsule
runs unchanged, nothing hits the shoulder, and the rate is beam-limited at
~1.8×10⁸ n/s. That is still ~200 n_TOF thermal-gate days per ILL day. But FIPPS
is built around its own Ge array, so whether our four arms fit in place of or
around it is the first question to ask.

### PF2 / SuperSUN — not relevant (ultracold neutrons).

## Getting beam time

| route | what | when |
|---|---|---|
| **Standard proposal** | peer-reviewed by the subcommittee (college) | deadlines twice a year, **mid-February and mid-September**. Autumn 2026: 15 Sep 2026, panels 3–4 Nov 2026. |
| **EBTA — Extensive Beam Time Access** | **for PF1B, PF2 and FIPPS only**; for "projects that require a long preparation phase and beam time of the order of a full reactor cycle or longer". An allocation is committed **up to 3 years ahead**, and readiness must be demonstrated within those 3 years. Needs the EBTA form + a 5–10 page science & technical document (motivation, beam-time justification, milestones, setup, safety risks, ILL resources needed, team). Yearly progress reports. | 2026: one spring round (deadline 16 Mar 2026). **From 2027: an annual call.** |
| EASY / DDT | rapid / director's discretionary access | all year; useful for a **background-measurement day** before the main run |

Eligibility: the **two-thirds rule**. If proposers come from non-member
countries, at least two-thirds of the team must come from ILL Associate or
Scientific Member countries. CERN is not a member, so the team must be
weighted toward member-country institutes; the Italian, French and German
groups help. **(ask)** how a CERN-hosted collaboration is counted.

**For us:** EBTA is designed for exactly this case: a full cycle, a large
external setup, and years of preparation. The realistic path is an EASY/DDT
background day at PF1B (or a parasitic measurement), then an EBTA proposal in
the 2027 annual round for a run in 2028–29.

## Things specific to a ³He target at a reactor

- **Tritium.** Every absorbed neutron makes a triton: about 0.08 GBq per
  cycle at 10¹⁰ n/s and about 1 GBq at 10¹¹ n/s. The cell becomes a sealed
  tritium source, and ILL health physics will review the containment.
- **Polarised ³He is local.** The ILL's **Tyrex** MEOP filling station makes
  polarised ³He for spin-filter cells daily, at ~70 % on the instrument (80 %
  reached). Combined with PF1B's 99.7 % beam, this enables the spin-selected
  entrance channel in `report.html` §6. **(ask)** whether Tyrex can fill a
  cell of our geometry, and the relaxation time (T₁) needed against a cycle.
- **³He as a beam stop.** An opaque ³He volume absorbs neutrons without
  capture γ. That is an established low-background beam-stop technique (NIST,
  "³He beam stop minimizing gamma ray and fast neutron background"), so the cell
  doubles as our beam dump.
- **⁶LiF collimators** are the standard γ-free absorber at PF1B. They do make
  fast neutrons from ⁶Li(n,t) followed by (t,n) at ~10⁻⁴ per absorption, which
  is a known source in PGAA work.

## Theory context gathered on the way

- **Viviani, Filandri, Girlanda, Gustavino, Kievsky, Marcucci, Schiavilla, PRC
  105, 014001 (2022), arXiv:2104.07808.** This is the ab initio
  ³H(p,e⁺e⁻)⁴He / ³He(n,e⁺e⁻)⁴He calculation. They fit the 2019 ATOMKI ⁴He
  data for S, P, V and A bosons (Table IX: V proto-phobic ε₀ = 2.56×10⁻³,
  ε_z = −3ε₀; A ε₀ = 2.58×10⁻³). They conclude that a **proto-phobic vector**
  explains both the ⁸Be and ⁴He anomalies, while for an axial boson the two
  sets of couplings look inconsistent. Their n+³He predictions start at
  E_n = 0.17 MeV, and the experimental site they discuss is n_TOF. **They never
  computed the thermal point.** That one run of their code is the most valuable
  input an ILL proposal could have (see `README.md`, open question 1).
- **Selection rules at thermal energy** (s-wave only: J^π = 0⁺ from ¹S₀, 1⁺
  from ³S₁; ground state 0⁺):

  | X17 | from 0⁺ (¹S₀) | from 1⁺ (³S₁) |
  |---|---|---|
  | scalar 0⁺ | allowed (L = 0) | forbidden (parity) |
  | pseudoscalar 0⁻ | forbidden (parity) | allowed (L = 1) |
  | vector 1⁻ | forbidden (0→0) | allowed (magnetic-type) |
  | axial 1⁺ | forbidden (0→0) | allowed (L = 0) |

  So a thermal beam tests V, A and P through the 1⁺ channel and S through the
  0⁺. The 0⁻ and 1⁻ states that dominate the ATOMKI ³H(p,…) energies are
  absent (p-wave, suppressed ~10⁻⁵ below 2 eV).
- **The thermal M1 is hindered.** The 55 μb ³He(n,γ) (Wolfs et al., PRL 63,
  2721 (1989): 54 ± 6 μb; Wervelman et al., NPA 526 (1991): 55 ± 3 μb) is tiny
  next to p(n,γ) and d(n,γ). The one-body M1 nearly cancels and meson-exchange
  currents dominate (the "hen" problem). A boson whose isospin couplings differ
  from the photon's need not share that cancellation. That is why the
  X17-to-γ ratio at thermal energy cannot be borrowed from the MeV value.
- **The E0 side** connects to the α-particle monopole transition form factor,
  which ab initio theory does not reproduce (the context of the matrix element
  used in nTof_x17 `ipc_channels`). A spin-selected measurement of the E0 pair yield is a
  nuclear-structure result in its own right.

## Alternatives, briefly

- **FRM II (Garching), MEPHISTO**: a cold beam built for particle physics, the
  direct analogue of PF1B. FRM II has been offline for years, and MLZ says the
  restart date will be announced later. Not plannable today.
- **ESS (Lund), ANNI**: the planned pulsed cold-beam particle-physics station.
  A long-pulse source would add time-of-flight back. Its timeline is not
  plannable for this decade's run.
- **NIST NCNR / ORNL HFIR**: comparable cold beams; not explored here.

## Sources

- ILL reactor cycles: <https://www.ill.eu/en/the-facility/the-ill-high-flux-reactor/reactor-cycles/>
- UKRI, "Green light to extend ILL operations until 2033": <https://www.ukri.org/news/green-light-to-extend-ill-operations-until-2033/>
- PF1B characteristics: <https://www2017.ill.eu/for-all-users/instruments/instruments-list/pf1b/characteristics>
- PF1B polariser papers: <https://arxiv.org/pdf/2208.14305>, <https://arxiv.org/pdf/1906.04690>
- NPP instruments overview: <https://www.ill.eu/en/science-technology/ill-science-groups/nuclear-particle-physics/instruments/>
- FIPPS characteristics and collimation: <https://www.ill.eu/users/instruments/instruments-list/fipps/characteristics>, <https://www.ill.eu/users/instruments/instruments-list/fipps/description/fipps-collimation>
- ILL spring 2026 call + EBTA: <https://lists.neutronsources.org/pipermail/neutron/2026/009676.html>
- EBTA page: <https://www.ill.eu/en/for-ill-users/applying-for-beam-time/type-of-beamtime-access/ebta-proposals/>
- Standard access: <https://ill.eu/for-ill-users/applying-for-beamtime/standard-access>
- Tyrex history: <https://www.ill.eu/users/instruments/instruments-list/tyrex-2/history>
- PERKEO II n → χ e⁺e⁻: <https://arxiv.org/pdf/1905.01912>
- EXILL at PF1B: <https://www.osti.gov/pages/biblio/1507786>
- NIST ³He beam stop: <https://www.nist.gov/publications/3he-beam-stop-minimizing-gamma-ray-and-fast-neutron-background>
- Ricochet fast-neutron background at the ILL: <https://arxiv.org/pdf/2208.01760>
- Viviani et al., arXiv:2104.07808: <https://arxiv.org/pdf/2104.07808>
- Wolfs et al., PRL 63, 2721: <https://link.aps.org/doi/10.1103/PhysRevLett.63.2721>; Wervelman ECN report: <https://publications.ecn.nl/ECN-RX--90-061>
- MLZ user office (FRM II status): <https://mlz-garching.de/user-office>
