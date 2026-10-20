# FRM II SR10 fission-neutron beam (MEDAPP / NECTAR), Garching — the facility record

Started 2026-10-20. Every number has its source; **(ask)** marks what could not be found publicly.
Confidence codes as in `survey/SOURCES.md`: V verified (document read), S search summary, E estimate.

## 1. Where and what

- **Site:** Forschungs-Neutronenquelle Heinz Maier-Leibnitz (FRM II), TU München, Lichtenbergstraße 1,
  85748 Garching (48.266 N, 11.671 E), ~15 km north of Munich. 20 MW research reactor, compact
  HEU core (8.1 kg, 93 % ²³⁵U), light-water cooled, D₂O moderated; max unperturbed thermal flux
  8×10¹⁴ n/cm²/s; normally 4 cycles of 60 days a year. Wagner et al., J. Nucl. Phys. At. Energy 3 (2007) 30
  (`survey/refs/Wagner2007_MEDAPP.pdf`); Wagner, ÖMPG Salzburg 2011 slides. **V**.
- **The beam:** beam tube **SR10**, the world's only beamline fission converter. Two U₃Si₂-Al plates
  (93 % ²³⁵U, 540 g, 80 kW of fission power) are driven down a chute into the D₂O tank next to the
  nose of SR10, ~1 m from the core. Thermal neutrons from the core fission in the plates; the beam
  tube looks straight at them, with "nearly no moderating material towards the beam tube".
  4 shutter drums, then filters, a multi-leaf collimator and two shielded irradiation rooms in line:
  **MEDAPP** (therapy and short experiments) and, behind it, **NECTAR** (radiography/tomography,
  permanent set-ups). Wagner 2007; MLZ, JLSRF 1 A18 and A19 (2015). **V**.

## 2. Beam numbers

| quantity | value | source | conf. |
|---|---|---|---|
| spectrum | Watt (²³⁵U fission) plus a small intermediate component; measured by multi-foil activation + MCNP | Breitkreutz et al., NIM A 593 (2008) 466; Wagner 2011 slide | V (statement) |
| mean neutron energy | 1.9 MeV at MEDAPP (1.6 MeV quoted for the bare tube in 2007; 1.8 MeV at NECTAR) | JLSRF A18, A19; MLZ 2025 poster | V |
| maximum neutron energy | "around 10 MeV" | MLZ 2025 poster (Sommer, Chemnitz) | V |
| flux, standard filters (1 cm B4C-epoxy + 3.5 cm Pb) | **3.2×10⁸ n/cm²/s** free in air at the MEDAPP reference position | FRM II web page; Wagner 2011; MLZ 2025 poster | V |
| flux, other filters | up to 7×10⁸ n/cm²/s | JLSRF A18; Wagner 2007 | V |
| γ | mean 2.4 MeV behind the standard filters; n:γ dose ratio fixed at 3:1 (0.54 vs 0.20 Gy/min at 2 cm in water) | Wagner 2011; Wagner 2007 | V |
| γ per neutron | ≈ 1 photon per neutron (from the dose ratio and fluence-to-dose factors: 2.4 MeV γ ~1.0×10⁻¹¹ Gy cm², fission n ~2.9×10⁻¹¹ Gy cm²) | `medapp_beam.py` | E |
| field | MLC up to 27 × 19 cm (also "30 × 20 cm"); leaves 1.5 cm wide, 60 cm deep, Fe/PE/Pb, vertical motion | JLSRF A18; Wagner 2007 | V |
| geometry | source-to-surface distance **592 cm** at MEDAPP; effective source 15 × 15 cm² | Wagner 2011 (Kampfer dose profile) | V |
| sample space | MEDAPP max 40 × 30 cm (in the field); NECTAR up to 80 × 80 × 80 cm, 500 kg, custom set-ups "easily attached" | JLSRF A18, A19 | V |
| NECTAR flux | 8.7×10⁵ – 4.7×10⁷ n/cm²/s (filter dependent), L/D ≤ 233 | JLSRF A19 | V |
| thermal option | converter out: D₂O spectrum, 28 meV, ~2×10⁹ n/cm²/s at MEDAPP | JLSRF A18 | V |
| uses listed | therapy, dosimetry, electronics irradiation (on-line tests), **fundamental physics**, in-beam γ spectrometry (FaNGas HPGe) | JLSRF A18 | V |

## 3. Status (October 2026)

- **The reactor has not run since 16 March 2020.** The replacement central channel was not delivered
  by March 2026; TUM will give a restart date only after it is installed and accepted
  (Bavarian parliament Drucksache 19/11406, 23 Mar 2026, `survey/refs/BayernLandtag_2026-03_FRM2.pdf`). **V**.
- Late-2025 press: no date given any more; the technical director said installation and start-up
  take another ~6 months after delivery. **S** (ingenieur.de, diebayern.de, forschung-und-lehre.de).
- MLZ still advertises MEDAPP for fast-neutron damage studies (MLZ conference, July 2025). **V**.
- **Restart: (ask).** Earliest plausible is 2027.

## 4. What it would take to host MX17

- **Space.** MEDAPP's room is a treatment room with a patient couch; the field is 27 × 19 cm. The
  four arms span ~1.6 m across and ~1 m along the beam (with 75 cm plates, ~2 m across). Is there
  room for the arms around the beam axis in MEDAPP, or in NECTAR behind it (lower flux unless the
  NECTAR collimator is opened)? **(ask)**
- **Beam size.** The MLC can collimate to ~8 × 8 cm (leaves 1.5 cm), the Ø8 cm cell spot assumed here.
  The penumbra from a 15 cm source at 5.9 m is ~1 cm per metre past the collimator. **E**.
- **Flight tube.** The model needs an evacuated (or He) tube from the MLC exit to the cell window and an
  exit tube to a beam dump behind the arms; in air, ~1 % of the beam scatters per metre near the arms.
- **Beam dump.** NECTAR has a beam stop; in MEDAPP the beam ends on the room wall (ask: distance).
- **Running time.** 4 cycles × 60 d per year in normal operation, shared with medicine and NECTAR.
- **Contacts (public, JLSRF / MLZ 2025):** MEDAPP instrument scientist Christoph Genreith (2015);
  MLZ 2025 poster: L. Sommer, T. Chemnitz; NECTAR: T. Bücherl, S. Söllradl.

## 5. Sources

- Wagner, Bücherl, Kampfer, Kastenmüller, Waschkowski, *Thermal neutron converter for irradiations with
  fission neutrons*, J. Nucl. Phys. At. Energy (Kyiv) 3(21) (2007) 30. `survey/refs/Wagner2007_MEDAPP.pdf`.
- F. M. Wagner, *Medizinische Neutronenbestrahlungen an einem Forschungsreaktor*, ÖMPG Salzburg,
  19 May 2011: <https://alt.strahlenschutzverband.at/uploads/media/05_20110121_Wagner.pdf>. `refs/Wagner2011_OEMPG.pdf`.
- MLZ, *MEDAPP: Fission neutron beam for science, medicine, and industry*, JLSRF 1, A18 (2015),
  doi:10.17815/jlsrf-1-43. `refs/JLSRF_A18_MEDAPP.pdf`.
- MLZ, *NECTAR: Radiography and tomography station using fission neutrons*, JLSRF 1, A19 (2015),
  doi:10.17815/jlsrf-1-45. `refs/JLSRF_A19_NECTAR.pdf`.
- Sommer, Chemnitz, *The MEDAPP instrument as test site for fast neutron radiation damage*, MLZ
  Conference 2025: <https://indico.frm2.tum.de/event/540/contributions/5461/>. `refs/MLZ2025_MEDAPP_poster.pdf`.
- Breitkreutz, Wagner, Röhrmoser, Petry, *Spectral fluence rates of the fast reactor neutron beam MEDAPP
  at FRM II*, NIM A 593 (2008) 466 (abstract only; full text not read).
- FRM II, *Irradiation with fast neutrons*:
  <https://www.frm2.tum.de/en/frm2/the-neutron-source/irradiation-facilities/irradiation-with-fast-neutrons/>.
