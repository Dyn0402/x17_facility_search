# Intense D-D neutron sources — facility record

Compiled 2026-11-09. Web sources read that day; facts not public are **(ask)**, analytic stand-ins are **ESTIMATE**.
This is a class of machine, not one site. Reach and configurations: `FEASIBILITY.md`.

## 1. The sources (2.45 MeV D-D unless stated)

| source | yield n/s | status | evidence | access |
|---|---|---|---|---|
| **Phoenix high-yield gas target** (300 kV, microwave ion source, windowless D₂ gas) | **3×10¹¹ measured**; 5×10¹¹ was a stated goal | shown 2013–2018; 2026 availability of a D-D system **(ask)** | IPAC 2018 TUYGBF2; Radel slides | commercial product, one vendor; no user programme found |
| SHINE / Phoenix record, 4.6×10¹³ | D-T, not D-D (search result inferred D-T from the scale; **(ask)** to confirm) | 2019 | shinefusion.com, Physics World | not usable for us (14 MeV) |
| **Adelphi DD-110** | ~1×10¹⁰ rated | commercial, compact | adelphitech product listing; WPI lab page: DD110M ~1×10¹⁰ | purchase, price **(ask)** |
| **Astral Systems Mk2** | ~1×10¹⁰ D-D (vendor directory only; Mk0 10⁸) | sale from Q4 2025 stated by listing; yield not independently checked | UKAEA industry listing | purchase or irradiation campaigns (D-D) |
| **Avalanche Energy Lando / FusionWERX** | licensed to 10¹⁰ n/s (company claim, not a measured yield); 2023 poster projected >10¹³ | FusionWERX construction planned; $29M raised Feb 2026 | NEI magazine, press | commercial/test facility, future **(ask)** |
| **LBNL HFNG** | 3×10⁸ measured (design 10¹¹) | research device | NIM 2018; APS 2015; arXiv 1803.03723 | collaboration **(ask)** |
| **ENEA FNG (Frascati), D-D mode** | 5.7×10⁸ measured at 1 mA (nominal up to 10⁹) | operating as of ENEA 2023 pages; 2025–26 status not found **(ask)** | arXiv 1505.06654; ENEA 2023 press | fusion programme / collaboration; nearest European option |
| **NSD-Fusion (IEC)** | 2×10⁷ at 115 kV, 15 mA (model not stated) | older | IAEA abstract | not competitive |
| **Starfire nGen-300 / -350** | 5×10⁶–10⁷ (1e8 on one later page) | commercial; $99.5k for an nGen-310-DD (2022 quote) | starfireindustries.com; FNAL-hosted quote | too weak |
| **Thermo MP320** | 2×10⁶ D-D | catalogue says no longer sold (spares only) | thermofisher.com | too weak |
| **IEC (Wisconsin, Kyoto)** | up to 1.8×10⁸ (Wisconsin) | research | ANS FST, UW FTI | too weak; Kyoto absolute yield not found |
| **TU Wien, Tokamak Energy D-D, LLNL D-D lab generators** | searched, nothing usable | — | — | none **(ask)** if wanted |

**Accelerator D(d,n) on deuterium**

| machine | what | status | yield | for us |
|---|---|---|---|---|
| Lanzhou ZF-400 | 450 keV, 50 mA, rotating TiD | published design/evaluation (EPJ A 2019) | 2.8×10¹¹ D-D | no gas target, China **(ask)** |
| INR Moscow HCADI | 430 keV, 20 mA | published | up to 5×10¹⁰ | access not realistic |
| LLNL gas-target RFQ | 6–7 MeV deuterons on D₂ gas | design/imaging | E_n up to ~10 MeV (too hard forward) | no |
| SPIRAL2 (GANIL) | RFQ 0.75 MeV/u, up to 5 mA deuterons CW | linac operating; no intermediate D-gas station | D(d,n) at the RFQ energy is hypothetical | station would have to be built |
| SARAF, LIPAc | deuterons at MeV | no D₂-gas neutron station found | — | not checked in depth **(ask)** |

No operating 5–10 mA, 1–2 MeV deuteron machine with a D₂ gas neutron target was found. This row is a "what if".

## 2. Cost and access

- **Buying:** the only prices found are Starfire nGen-310-DD $99.5k (2022, weak source) and a Polish group's ~$300k for a
  shielded installed device (type unclear). A 3×10¹¹ gas-target system has no public price **(ask)**; ESTIMATE several M€ with the vault, not a quoted figure.
- **Hiring:** no rental offer found. Astral advertises irradiation campaigns; no rate found **(ask)**.
- **Travelling:** nobody runs a 3×10¹¹ D-D user beam. FNG is the only European D-D station found, ~×500 weaker in yield.
  US Phoenix-type machines are commercial and in-house; hosting MX17 would be a contract **(ask)**. US export or site rules for the apparatus: **(ask)**.

## 3. What hosting needs (ESTIMATE)

- A dedicated vault: 3×10¹¹ n/s of 2.45 MeV is about 3.4 Sv/h at 1 m (2.4×10⁶ n/cm²/s × ~400 pSv·cm², ESTIMATE). Roughly 1.5–2 m of concrete or a labyrinth, and a licensed D₂ gas handling system.
- Tritium: D(d,p)T makes tritons about as fast as neutrons, ~1.3×10¹⁸ T in 50 d at 3×10¹¹ n/s, ~2 GBq (ESTIMATE). Needs a D₂ recirculation/getter plan, and T buildup makes a small 14 MeV tail **(ask)** the fraction.
- The source's beam axis must be ~90–135° to the cell axis for E_n in the window (§ FEASIBILITY 2), with the beamline outside the arm envelope.
- The ³He cell: the 30 bar × 40 cm NFS-style cell, 87 L STP ≈ 217 k€ of ³He, as at Birmingham (`birmingham/TARGET_GEANT.md`).

## 4. Contacts (public, none contacted)

Phoenix LLC / SHINE Technologies (Madison and Janesville, WI): E. Michalak, R. Radel, Rittenhouse on the IPAC 2018 paper. ENEA FNG: Frascati fusion division.
Adelphi Technology, Redwood City. Astral Systems (UK). Avalanche Energy.

## 5. Sources

- Phoenix: <https://proceedings.jacow.org/ipac2018/export/TUYGBF2.xml>, <https://trinity.ans.org/file/1445/radel-150616.pdf>, <https://shinefusion.com/blog/phoenix-and-shine-complete-unprecedented-neutron-production-run>, <https://wisinvpartners.com/2019/06/19/phoenix-completes-milestone-test-with-unprecedented-neutron-output-and-reliability/>
- Adelphi: <https://www.plantautomation-technology.com/index.php/products/adelphi-technology-inc/dd109-neutron-generator>, <https://wp.wpi.edu/radlab/?p=10>, <https://www-pub.iaea.org/MTCD/Publications/PDF/P1433_CD/datasets/papers/ap_ie-01.pdf>
- Astral: <https://ukaeaevents.com/industry-directory/organisation/astral-systems/>, <https://ntrs.nasa.gov/citations/20240014095>
- Avalanche: <https://www.neimagazine.com/news/avalanche-energy-launches-fusionwerx/>, <https://www.streetinsider.com/PRNewswire/Avalanche+Energy+Raises+%2429+Million+Following+Plasma+Physics+Breakthroughs/25933235.html>, <https://meetings-archive.aps.org/dpp/2023/yo08/10>
- LBNL HFNG: <https://arxiv.org/pdf/1803.03723>, <https://meetings-archive.aps.org/apr/2015/t1/54>, <https://escholarship.org/uc/item/6z74x57b>
- FNG: <https://arxiv.org/pdf/1505.06654>, <https://agenda.enea.it/event/767/>, <https://www.media.enea.it/en/press-releases-and-news/years-archive/year-2023/energy-fusion-fng-the-most-intense-14-mev-neutron-source-in-europe-turns-30.html>, <https://euro-fusion.org/member-news/celebrating-30-years-of-europes-most-intense-neutron-source/>
- NSD: <https://www-pub.iaea.org/MTCD/publications/PDF/P1433_CD/datasets/abstracts/sm_en-18.html>. Starfire: <https://www.starfireindustries.com/ngen>, <https://indico.fnal.gov/event/54623/contributions/242735/attachments/155694/202820/Starfire_RFQ_NGEN220217-02.pdf>. Thermo: <https://www.thermofisher.com/order/catalog/product/1517021A>
- Accelerators: <https://link.springer.com/article/10.1140/epja/i2019-12848-5>, <https://proceedings.jacow.org/r10/talks/frchx01_talk.pdf>, <https://accelconf.web.cern.ch/linac2016/papers/we1a06.pdf>, <https://accelconf.web.cern.ch/napac2016/papers/tua1io02.pdf>
- Cost: <https://www.slcj.uw.edu.pl/wp-content/uploads/2019/01/KMiernik_abstrakt.pdf>
