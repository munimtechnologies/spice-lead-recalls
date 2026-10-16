# Natural chromium in coriander, and the lead-chromate ratio

A companion note to `cr_baseline.py` (see the repository README, section 2). It
collects every published value we could find for the natural chromium content of
coriander (*Coriandrum sativum*) seed, stratified by analytical method, and reads
what the analytical-chemistry literature says about why those values disagree by
more than an order of magnitude. Coriander is the one spice where that disagreement
straddles the lead-chromate signal in New York City's lab data, so it is the single
place where the Pb:Cr fingerprint test cannot be settled from published chromium
alone.

By MV2 of Munim, Inc. Text CC BY 4.0. Made with AI agents working in MV2's name.
Every value below was read from the cited paper's own table or abstract.

Updated 2026-10-16: added a fifth study, Haidu et al. 2017, whose coriander value was
measured by neutron activation (no digestion, no plasma) and is below its 0.35 mg/kg
detection limit. Later the same day: added Lopez et al. 2022, an ICP-MS market study
in which coriander powder itself carried lead chromate (section "A known lead-chromate
coriander sample").

## The two NYC samples at issue

`nyc_spice_lead.py` pairs each NYC chromium result with the lead result for the
same product. Two coriander pairs fall in the chromate-like band (molar Pb:Cr
0.7–2) yet carry little chromium, so a spice's own chromium could in principle
account for the ratio:

| NYC rows (Pb/Cr) | collected | spice | bought in | Pb ppm | Cr ppm | molar Pb:Cr | edge ppm |
|---|---|---|---|---|---|---|---|
| 3282/3281 | 2019-01-22 | Coriander | Georgia | 51 | 9.1 | 1.41 | 2.70 |
| 2290/2289 | 2017-06-07 | Coriander powder | Bangladesh | 52 | 12 | 1.09 | 5.48 |

The *edge* is the most natural chromium (ppm) a pair can lose before its molar Pb:Cr
ratio rises above 2 and the pair leaves the band:
`edge = Cr − (Pb / 207.2) / 2 × 51.996`. A pair is **robust** if its edge is above
every published natural-chromium ceiling for the spice, **unresolved** if above some
and not others.

## Every published coriander chromium value we found

| study | origin | sample and preparation | method (instrument) | Cr (mg/kg) |
|---|---|---|---|---|
| Cicero et al. 2022 (Foods 11:548, PMC8871210) | India (Saudi market) | whole seed, acid digest | ICP-MS, collision cell | 0.129 |
| Voica et al. 2021 (Molecules 26:7081, PMC8658825) | Bulgaria (Romanian market) | whole seed, composite of 5 lots, acid digest | ICP-MS, He KED cell | 0.912 ± 0.045 |
| Ugulu et al. 2023 (Plants 12(20):3652, PMC10609805) | Pakistan (Sargodha, two irrigation sites) | whole seed, HNO₃/H₂O₂ digest | atomic absorption (hydride-generation step; PE AAS-300) | 0.460–0.548 |
| Haidu et al. 2017 (J Anal Methods Chem 2017:9748413, PMC5463156) | Romania (uncontaminated area near Orăștie, 2015 crop) | whole fruit (*Coriandri fructus*), ground with ceramic tools, **no digestion** | k₀ neutron activation (Budapest Research Reactor) | < 0.35 (detection limit, dry weight) |
| Gazwi et al. 2022 (Sci Rep 12:9834, PMC9013364) | Egypt (El-Minia market) | **aqueous seed extract** (water, 65 °C), then digested | ICP-OES (iCAP 6500 Duo) | 12.45 ± 0.65 |
| Tefera & Teklewold 2021 (Heliyon 7:e07048, PMC8138603) | Ethiopia (markets) | whole seed, acid digest | flame AAS | 10.83–18.93 (three market means) |

## What the pattern shows

- **Four whole-seed measurements, four origins, three independent analytical
  principles (collision-cell ICP-MS, hydride-generation AAS and neutron activation)
  all put coriander chromium below 1 ppm.** The Ugulu (2023) value is the first
  non-ICP-MS whole-seed measurement in the set; it agrees with the two ICP-MS values
  rather than with the high ones, even at the wastewater-irrigated site.
- **The neutron-activation value (Haidu 2017) closes the last method loophole.**
  Neutron activation reads the ground fruit directly: there is no acid digest that
  could leave refractory chromium undissolved, and no plasma, so neither a polyatomic
  nor a spectral interference applies. It found coriander chromium below its 0.35 ppm
  detection limit. In the same study (same area and crop year), dill fruit, a close relative, read 0.45
  ppm. The method read chromium in its tobacco reference material slightly *high*
  (7.51 against a consensus 6.4 mg/kg), so the coriander bound is not an under-reading.
- **The two values above 10 ppm are the outliers.** One is a single flame-AAS market
  survey (Tefera & Teklewold, Ethiopia). The other (Gazwi, 12.45 ppm) is not a
  whole-seed digest at all but an **aqueous extract** of the seed read by ICP-OES, so
  it measures a different thing and is not directly comparable to the other studies or
  to NYC's total chromium "as sold."
- So among measurements comparable to NYC's (whole seed or powder), **four of the
  five studies report coriander chromium under 1 ppm**, and only one whole-seed study
  (flame AAS) disagrees.

## Why the methods disagree, and which to believe

A common worry is that the low values come from an insensitive method missing
chromium. The analytical literature points the other way for ICP-MS:

- **Carbon-based polyatomic interference inflates, not deflates, standard-mode
  ICP-MS chromium.** The ⁴⁰Ar¹²C⁺ ion (and ³⁵Cl¹⁶OH⁺) overlaps ⁵²Cr and ⁵³Cr; in
  carbon-rich plant and food digests this makes an uncorrected (standard-mode) ICP-MS
  read chromium *too high*. A collision or dynamic-reaction cell removes it. Working
  on foods, Hammer, Nicolas & Andrey (Atomic Spectroscopy 26(6), 2005) validated
  dynamic-reaction-cell ICP-MS against graphite-furnace AAS and five certified
  reference materials and showed that both of their digestion routes left residual
  carbon that over-estimated chromium in standard mode, and that the cell corrected
  it. Both low coriander ICP-MS values here used a cell (Cicero: collision cell;
  Voica: helium kinetic-energy discrimination), so they are *not* an artifact of poor
  sensitivity — an uncorrected ICP-MS would have erred high, not low.
- **A digest that misses refractory chromium would err low**, and every acid-digest
  value in the table could in principle share that bias. The neutron-activation value
  needs no digest and still finds less than 0.35 ppm, so incomplete digestion does not
  explain the sub-1-ppm cluster either.
- **ICP-OES has poor chromium sensitivity** (detection limits roughly an order of
  magnitude above ICP-MS) and chromium emission lines can suffer spectral overlap from
  iron and vanadium, which bias a low true value upward near the limit. Combined with
  the aqueous-extract basis, the Gazwi 12.45 ppm value is the least comparable point in
  the table.
- **Flame AAS (Tefera & Teklewold)** is a legitimate whole-seed measurement, but with
  no interference cell and higher detection limits than cell-ICP-MS. We did not find a
  documented chromium-specific over-reading mechanism for flame AAS, so this value is
  not dismissible: it is the one directly comparable measurement that disagrees with the
  sub-1-ppm cluster.

## A known lead-chromate coriander sample

Lopez et al. (2022, *Environ Sci Technol* 56:16996, PMC9730856) bought 12 coriander
powders in Patna, India, in 2020 and measured them by ICP-MS (Thermo XSERIES 2, nitric
acid microwave digest, triplicate digestions). Their lead: median 86 mg/kg, range
0.05–250 (Table 1). Across their spices, "when Pb concentrations exceeded 1 mg/kg, the
molar Pb/Cr ratio was near or above 1", which they read as lead chromate adulteration.
They also ran the diphenylcarbazide (DPC) colour test, which detects hexavalent
chromium, and list coriander powder among the spices in which it detected Cr(VI). Plant
chromium is naturally Cr(III), as the same paper notes.

One coriander powder is described with both numbers: colour developed (Cr(VI) present)
at **87 mg/kg lead and 13 mg/kg chromium**. Run through the same arithmetic as the NYC
pairs:

| sample | Pb ppm | Cr ppm | molar Pb:Cr | edge ppm | Cr(VI) by DPC |
|---|---|---|---|---|---|
| Lopez 2022, Patna coriander powder | 87 | 13 | 1.68 | 2.08 | detected |
| NYC 2019, Georgia coriander | 51 | 9.1 | 1.41 | 2.70 | not tested |
| NYC 2017, Bangladesh coriander powder | 52 | 12 | 1.09 | 5.48 | not tested |

What this adds:

- **Coriander powder is a documented lead-chromate target**, measured by ICP-MS in a
  South Asian market, not only turmeric. The NYC pairs are therefore not an unlikely
  kind of adulteration.
- **A sample whose chromium was shown to be hexavalent looks just like the NYC
  pairs.** Its lead and chromium are the same size, its ratio is in the band, and its
  edge (2.08 ppm) is *smaller* than either NYC edge. `cr_baseline.py` would also mark
  it **unresolved**, because 2.08 ppm is below the flame-AAS and ICP-OES ceilings. So
  for coriander the rule is conservative: being unresolved here does not argue against
  lead chromate.
- **A cheaper way to settle such cases is speciation, not a blank.** Natural chromium
  in the plant is Cr(III); the pigment is Cr(VI). A Cr(VI) test (DPC colour, or a
  speciation method in a laboratory) on the same sample answers the question that the
  total-chromium ratio cannot. Lopez et al. also report its limit: one coriander powder
  with 167 mg/kg lead showed no colour, so a negative DPC result is not proof of
  absence.

The tool's verdicts do not change: this sample is not a natural-chromium value, so it
does not enter `data/natural_cr_ceilings.csv`. The per-sample lead and chromium values
of all 12 Patna powders are in the paper's Supplementary Table S1. Lopez et al. describe
their low-lead samples (lead under 1 mg/kg, coriander among them) as having Pb/Cr below
0.5, which they read as geogenic. Once Table S1 is read, those coriander rows can add
ICP-MS natural-chromium values to the ceiling table.

## What it means for the two NYC coriander flags

Both edges (2.70 ppm for the Georgia 2019 sample, 5.48 ppm for the Bangladesh 2017
sample) sit **above all four whole-seed ceilings under 1 ppm** but **below** the
flame-AAS range and the aqueous-extract ICP-OES value. `cr_baseline.py` therefore
marks both pairs **unresolved**, and that remains the honest machine verdict.

The weight of the comparable (whole-seed) evidence, however, leans one way: four
studies under 1 ppm, across India, Bulgaria, Pakistan and Romania, by three
independent methods, against one flame-AAS study at 10–19 ppm. On that balance the
chromium in NYC's two coriander samples is more consistent with being
pigment-associated — i.e. the lead-chromate reading is probably real — than with
ordinary natural background. The Lopez et al. sample adds that a coriander powder with
the same profile did carry hexavalent chromium. It still cannot be *confirmed* from the
literature, because one comparable whole-seed study disagrees and coriander chromium
plainly varies with soil and origin. Resolving it needs either a Cr(VI) test on the
product itself or a chromium blank measured on clean coriander of the same origin,
ideally by collision-cell ICP-MS. The lead finding (51–52 ppm) stands either way.

## Limits and provenance

- Each value was read from the paper's own table or abstract; preparation and method
  are reported as the paper states them. Surveys are small (n = 1–40 per study), and
  the dry-weight versus as-sold basis differs between papers. NYC reports total
  chromium as sold.
- Ugulu et al. (2023) describe a "gaseous hydride generation" step for chromium, which
  is unusual (chromium does not readily form a volatile hydride). We report the value
  as published and flag the oddity; its agreement with the two independent ICP-MS
  values is nonetheless notable.
- Haidu et al. (2017) is one lot of crop-grown fruit from an uncontaminated area, not
  market seed, and reports a detection limit rather than a measured value. Their
  results are per kg of dry plant (masses corrected for volatiles); their air-dried
  coriander lost 7.28% of its mass at 105 °C, so on an as-sold basis the bound would
  be slightly lower still, not higher. The tobacco reference value it was checked against is a consensus,
  not a certified, value.
- Lopez et al. (2022) do not say in the main text whether their ICP-MS used a
  collision cell, and they give the number of coriander powders that turned colour only
  in a figure. The 87/13 mg/kg sample is the one their text describes; the others are
  in Supplementary Table S1, which we have not yet read. Their paper is CC BY-NC-ND, so
  only facts and short quotes are used here.
- No study from Georgia or the wider Caucasus was found, so none of the five values
  is origin-matched to the 2019 Georgia sample.
- This note will be folded into the tool's ceiling table: the Ugulu value and the
  Haidu bound (as 0.35, method INAA) will be added to `data/natural_cr_ceilings.csv`
  (v0.1.1) alongside `cr_baseline.py`'s full-run outputs. Adding them does not change
  the current verdicts, because both sit below both coriander edges.
- We have still not found any published Pb:Cr lead-chromate test that subtracts a
  spice-specific natural-chromium background, by any method.

## References

- Cicero N, et al. Mineral and microbiological analysis of spices and aromatic herbs.
  *Foods* 11:548 (2022). doi:10.3390/foods11040548. PMC8871210.
- Voica C, et al. ICP-MS assessment of essential and toxic trace elements in foodstuffs
  with different geographic origins. *Molecules* 26:7081 (2021).
  doi:10.3390/molecules26237081. PMC8658825.
- Ugulu I, et al. Influence of industrial wastewater irrigation on heavy metal content
  in coriander (*Coriandrum sativum* L.): ecological and health risk assessment.
  *Plants (Basel)* 12(20):3652 (2023). doi:10.3390/plants12203652. PMC10609805.
- Haidu D, Párkányi D, Moldovan RI, et al. Elemental characterization of Romanian crop
  medicinal plants by neutron activation analysis. *Journal of Analytical Methods in
  Chemistry* 2017:9748413 (2017). doi:10.1155/2017/9748413. PMC5463156. (k₀-INAA;
  coriander fruit Cr below the 0.35 mg/kg detection limit, Table 2.)
- Gazwi HSS, et al. *Scientific Reports* 12:9834 (2022). PMC9013364. (ICP-OES, aqueous
  coriander seed extract.)
- Tefera M, Teklewold A. Health risk assessment of heavy metals in selected Ethiopian
  spices. *Heliyon* 7:e07048 (2021). doi:10.1016/j.heliyon.2021.e07048. PMC8138603.
  (Flame AAS.)
- Hammer D, Nicolas M, Andrey D. Improved chromium determination in various food
  matrices using dynamic reaction cell ICP-MS. *Atomic Spectroscopy* 26(6) (2005).
  (Residual-carbon interference over-estimates chromium in standard-mode ICP-MS; the
  reaction cell corrects it.)
- Lopez AM, Nicolini CM, Aeppli M, Luby SP, Fendorf S, Forsyth JE. Assessing analytical
  methods for the rapid detection of lead adulteration in the global spice market.
  *Environ Sci Technol* 56(23):16996–17006 (2022). doi:10.1021/acs.est.2c03241.
  PMC9730856. (ICP-MS, pXRF and DPC on 69 spice samples; 12 coriander powders from
  Patna, India, 2020.)

Contact: MV2, Munim, Inc. — mv2@munimtech.com
