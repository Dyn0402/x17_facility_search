# colliders/: X17 → e⁺e⁻ in STAR, sPHENIX and the LHC experiments

*Started 2026-11-12.* Can the central barrels of RHIC and LHC experiments see X17 → e⁺e⁻? How
much do the leptons scatter in the material, how much signal can be tracked, and how?

## Read this first

**2026-11-12, first pass** (toy MC with real fits; write-up [`X17_COLLIDERS.md`](X17_COLLIDERS.md) §0).

- **The ATOMKI (nuclear, at rest) X17 is invisible:** its 8.4 MeV leptons curl up before any
  tracker requirement. The exception is ALICE ITS-standalone at 0.2 T (23 % pair acceptance).
  Colliders can only see X17 from meson decays, π⁰/η → γX17, and that tests **only a vector X17**:
  C-parity forbids it for an axial vector, gauge invariance for a pseudoscalar. The vector is the
  case SINDRUM already excludes for protophobic couplings.
- **Scattering is not the limit:** for boosted pairs σ_M ≈ 19 MeV·√(x/X₀) whatever the momentum.
  The toy gives σ(m_ee) = 0.3–0.5 MeV with silicon and 1.2 MeV with STAR's TPC alone.
- **The threshold sets the acceptance:** pT ≳ 60 MeV (STAR), ≳ 100 MeV (sPHENIX TPC), ≳ 16–20 MeV
  (sPHENIX silicon-only, ALICE ITS standalone). **sPHENIX should use the silicon alone:** ×6 the
  π⁰-made X17 of its TPC tracks.
- **Conversions fake m ≈ 0.6·B·r:** 16.8 MeV for the sPHENIX pipe. A pair fit under the conversion
  hypothesis removes 98–99 % of them; a per-track χ² does not.
- **Reach** (3σ, 10¹⁰ Au+Au / 10¹² pp): BR(π⁰ → γX17) ~ (0.3–1.5)×10⁻⁷ and BR(η → γX17) ~
  (1.5–6)×10⁻⁷ on statistics. A 0.1 % background-shape systematic takes π⁰ back to the NA48/2 level
  (~10⁻⁶) and η to (2–15)×10⁻⁶. That is still below the (2.6–9)×10⁻⁵ a protophobic vector would
  give. The η channel with a photon tag is the one worth a real study.

## Layout

| path | what |
|---|---|
| [`X17_COLLIDERS.md`](X17_COLLIDERS.md) | the write-up (numbered, dated) |
| [`star/`](star/README.md) | STAR as modelled, sources, open questions |
| [`sphenix/`](sphenix/README.md) | sPHENIX as modelled (design and "quoted" material), sources |
| [`lhc/`](lhc/README.md) | ALICE Run 3 (0.5 / 0.2 T), ALICE 3, and why not LHCb / ATLAS / CMS / FASER |
| `toy/detectors.py` | barrel tracker descriptions (layers, X₀, resolutions, track cuts) |
| `toy/kinematics.py` | meson spectra (Tsallis, mT scaling), P → γX17, Kroll-Wada Dalitz, π⁰ photons |
| `toy/tracking.py` | vectorised helix simulation (Highland MS, Bethe-Heitler brems, outbound arc), broken-line primary fit, pair conversion-hypothesis fit |
| `toy/run.py` | one (detector, source) point → `out/pairs/<det>__<source>__<system>.{csv,json}` |
| `toy/campaign.sh` | all 12 configurations × 13 sources (~1.5 h on 16 cores, resumable) |
| `toy/analytic.py` | thresholds, scattering floor, conversion fake masses, η → γX17 estimate → `out/analytic_*.csv` |
| `toy/analyze.py` | acceptance, σ(m), backgrounds, reach → `out/reach.csv` and the figures |
| `out/` | figures (each with its `.csv`) and tables |

## Running

```bash
PY=~/PycharmProjects/nTof_x17/.venv/bin/python
bash colliders/toy/campaign.sh          # ~1.5 h; writes colliders/out/pairs/
$PY colliders/toy/analytic.py
$PY colliders/toy/analyze.py
```

Everything runs locally (no Geant4): it is a toy with real fits, not a detector simulation.
