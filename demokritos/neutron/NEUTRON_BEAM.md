# Demokritos neutron beams on the ³He capsule: closed

Written 2026-10-19. Code: `neutron_beam.py` → `../out/neutron/` (`run_log.txt` is the last run). Deck:
`../deck/build_neutron_deck.py`, published as notes slug `demokritos-neutron-beam`.

**Verdict.** The Demokritos neutron beams cannot drive the n_TOF ³He capsule to an X17 measurement.

- With the flux the lab quotes, the capsule makes ~500 ³He pairs per day. That is half of n_TOF EAR2, and 34 years
  to 3σ at ATOMKI's strength even with the big plastics.
- Any source strong enough to change that makes ×360–4400 more pairs in its own production target, 1 cm upstream.
  The measurement then becomes the proton measurement, done worse.

Every assumption below is in the neutrons' favour.

---

## 1. The question and the method

Dylan's question: can the lab's mono-energetic neutron beams, with the n_TOF 500 bar ³He capsule, measure
³He(n,e⁺e⁻)⁴He for X17, as n_TOF did?

The chain, per µA of beam on the neutron-production target:

1. **Source.** Y₀ is the number of neutrons per sr per s toward the capsule. It is taken two ways:
   - **lab**: the flux the lab quotes. Vlastou et al. (IAEA) give a maximum of 10⁵–10⁶ n/cm²/s at the sample;
     Amanatidis 2024 places the samples ~1.7 cm from the target. This is taken at the top, 10⁶ at 1.7 cm.
   - **max**: computed from the target itself (§3). This is an upper bound on what any target could give.
2. **Capsule.** The pair rate is Y₀ × n × σ_pair × G:
   - n = 1.25×10²² ³He/cm³ (500 bar, 62.7 mg/cm³);
   - G = ∫dV/r² over the gas. The gas profile is the n_TOF capsule from MX17_Full_Geant `DetectorConstruction.cc`:
     17.0 cm³, 1.07 g of ³He, Ø 2 cm, ~8 cm long. The nose faces the source.
   - The flux at every point of the gas is taken at its 0° value.
   - G = 1.10 cm with the gas tip at 1.7 cm (the lab's sample position), 1.82 cm at 1.0 cm (the best case: 1 mm
     backing, water cooling, the 5.5 mm Al nose).
3. **σ_pair.** From Viviani et al., PRC 105 014001, Table V: 0.0431–0.146 µb for E_n = 0.17–2 MeV.
4. **Days to 3σ at ATOMKI's strength.** Scaled from the Demokritos p + t Geant4 result (`../ESTIMATES.md` §6):
   - the same ⁴He\*, the same apparatus, the same X17/IPC = 1.1×10⁻³;
   - days = 3.44 d (big plastics) or 45.4 d (as built) × 1.84×10⁶ / (³He pairs per day).

   This leaves out every neutron-induced background, the capsule's thicker walls and the E_n spread. For the
   ILL, the same scaling gives 2,000 d as built. The full ILL study (reach ~1×10⁻² per 50-day cycle) implies
   ~4,000 d at this strength, so the scaling is optimistic by ~×2.
5. **Production target.** The same beam makes ⁴He\* (or ⁸Be\*) directly in the production target (§5).

## 2. The energy window (figure: deck slide 3)

The X17 edge for n + ³He is θ_min = 2 asin(m_X/E_X):

| E_n | θ_min (m = 16.94 MeV) |
|---|---|
| thermal | 111° |
| 0.35 MeV | 109° |
| 2 MeV | 100° |
| 5 MeV | ~87° |
| 20 MeV | ~57° |

The Demokritos sources:

| reaction | E_n | in the X17 window? |
|---|---|---|
| ⁷Li(p,n) | 0.12–0.65 MeV | yes |
| ³H(p,n) | 2.0–5.3 MeV | the bottom only |
| ²H(d,n) | 4–11.5 MeV | no |
| ³H(d,n) | 15–21 MeV | no |

So only ⁷Li(p,n) and ³H(p,n) at E_n ≈ 2 MeV are considered. For ³H(p,n), E_p = 2.79 MeV gives E_n = 2.0 MeV at 0°.

## 3. Pair rates (per µA, 4π, before any selection)

| configuration | Y₀ [n/sr/s] | ³He pairs/day | X17/day | days to 3σ, big plastics | as built | µA for 50 d, big plastics |
|---|---|---|---|---|---|---|
| ⁷Li(p,n), lab flux, E_n 0.35 MeV | 2.9×10⁶ | 213 | 0.24 | 29,800 (82 yr) | 392,000 | 595 |
| **³H(p,n), lab flux, E_n 2 MeV** | 2.9×10⁶ | **504** | 0.56 | **12,600 (34 yr)** | 165,000 | **251** |
| ³H(p,n), all the target's tritium | 4.8×10⁷ | 13,700 | 15 | 462 | 6,090 | 9.2 |
| ⁷Li(p,n), thick metallic Li | 2.4×10⁸ | 42,000 | 46 | 151 | 1,990 | 3.0 |
| ³H(p,n) moderated, every n absorbed in ³He | — | 615 | 0.68 | 10,300 | 135,000 | 206 |
| ⁷Li(p,n) moderated, every n absorbed | — | 4,150 | 4.6 | 1,530 | 20,100 | 31 |

How the two "max" rows are built:

- **³H(p,n), all the target's tritium.**
  - N_T = 3.96×10¹⁹ T/cm² (2.1 mg/cm² Ti at T/Ti = 1.5).
  - σ(p,n) = 0.6 b, the upper end of 0.5–0.6 b near E_p = 2.8 MeV (Brune et al. 1999, nucl-ex/9902010).
  - That is 1.5×10⁸ n/s/µA. At 0° it is ×2 forward in the c.m. and ×2.02 from the Jacobian.
  - Y₀ comes out ×16 the quoted flux.
- **⁷Li(p,n), thick metallic Li at 2.5 MeV.**
  - ~9×10⁸ n/s/µA (Lee & Zhou, NIM B 152 (1999) 1), rounded up to 10⁹ and taken ×3 forward.
  - σ_pair is taken at 0.7 MeV, the top of the spectrum.

Both put the capsule's gas tip 1.0 cm from the beam spot.

**Moderating does not help.** Thermal capture gives 4.8×10⁻¹¹ pairs per absorbed neutron (M1; the E0 channel adds
tens of percent). Even if every source neutron were absorbed in the ³He, that is ≤ 615 or 4,150 pairs per day per µA.

**Benchmarks** (pairs/day):

| facility | ³He pairs/day | basis |
|---|---|---|
| n_TOF EAR2, 0.2–2 MeV (the 2026 campaign) | 900 | 22.5 X17/day at X17/IPC = 0.025, `docs/PLAN_GANIL_NFS.md` §5.3 |
| ILL design | 4.1×10⁴ | 10¹⁰ absorbed n/s |
| needed for 3σ in 50 d (big plastics / as built) | 1.27×10⁵ / 1.67×10⁶ | |
| p + ³H directly at Demokritos, 0.9 MeV | 1.84×10⁶ | the proton route |

## 4. Current

Days scale as 1/I.

- Ti-T neutron targets run at 0.7–1 µA, because a hot target loses its tritium.
- At the lab's flux, 50 days needs 251 µA: 700 W into a ~1 cm² Ti-T spot.
- The best-case sources need 3–9 µA, with every factor rounded up and the capsule 1 cm from a water-cooled target.
  Even granting those, §5 applies.

## 5. The production target makes the same pairs, ×360–4400 more

**³H(p,n) source.** The protons that make the neutrons also capture on the target's tritium: ³H(p,γ)⁴He at
E\* = 21.90 MeV. The capsule's E\* is 22.08 MeV at E_n = 2 MeV.

σ(p,γ) at E_p = 2.79 MeV comes two ways:

- the Hahn S-factor fit, extrapolated (`demokritos_rates.py`): 76 µb;
- detailed balance on ⁴He(γ,p)³H, with σ(γ,p) = 0.6–1.2 mb near 22 MeV: 49–98 µb. The sources are Shima et al.,
  PRC 72 (2005) 044004, and Raut et al., PRL 108 (2012) 042502; their data disagree by up to ~50 %.

With the Born E1 pair fraction 4.7×10⁻³:

| | pairs/day per µA |
|---|---|
| the Ti-T target | 4.9–9.9×10⁶ |
| the capsule | 1.37×10⁴ |
| **ratio** | **×360–720** |

**4π shell bound.** Suppose every source neutron crossed L cm of 500 bar ³He:

| L | ³He | pairs/day | target ÷ shell |
|---|---|---|---|
| 1 cm | 5 g | 2.3×10⁴ | ×210 |
| 5 cm | 88 g | 1.2×10⁵ | ×42 |
| 10 cm | 452 g | 2.3×10⁵ | ×21 |

None of these can be built. The capsule holds 1 g.

**⁷Li(p,n) source.**
- A thick Li target at 2.5 MeV captures through both 1⁺ resonances on the way down: 3.7×10⁻⁸ γ₀ + 6.1×10⁻⁸ γ₁
  per proton (the LNL cross sections; direct capture is held flat above the last measured point).
- That is 6.1×10⁵ γ/s/µA and 1.8×10⁸ ⁸Be pairs/day, **×4,400** the capsule's.

**The vertices cannot be separated.**
- The target and the capsule gas are 1–8 cm apart.
- The MM pointing cut accepts tracks within 135 mm of the assumed vertex, and the angular resolution is 9–14°.
- For ³H(p,n), the target's pairs have the capsule's X17 edge.
- For Li, the ⁸Be pairs' E_sum is 3–4 MeV lower. The arms contain ~40 % of the lepton energy, so an E_sum cut
  cannot remove ×10³.

## 6. What this does not rule out

- **p + ³H on the lab's Ti-T at 0.9 MeV**, below the (p,n) threshold: 3.4 d with big plastics and 45 d as built
  (Geant4, statistics only, `../ESTIMATES.md` §6). This is the Demokritos option.
- **³He with neutrons where the flux is 10⁴× higher and no target sits next to the cell:** the ILL, GANIL-NFS.

## 7. Inputs and simplifications (all generous to the neutrons)

| input | value | source / why generous |
|---|---|---|
| lab flux | 10⁶ n/cm²/s at 1.7 cm | top of the quoted 10⁵–10⁶ |
| σ(³H(p,n)) | 0.6 b | top of 0.5–0.6 b |
| 0° peaking, ³H(p,n) | ×2 c.m. × 2.02 Jacobian | evaluation ~1.5–2 in c.m. |
| thick-Li yield | 10⁹ n/s/µA, ×3 forward | literature ~9×10⁸ |
| capsule distance | gas tip at 1.0 cm | backing + cooling + 5.5 mm Al nose |
| flux through the gas | 0° value everywhere | real flux falls off-axis |
| σ_pair above 2 MeV | not used | only E_n ≤ 2 MeV |
| reach scaling | from p + t Geant4 | no neutron-induced background, thin target; ~×2 optimistic against the ILL study |
| X17/IPC | 1.1×10⁻³ (ATOMKI ⁴He, as in the proton study) | |
