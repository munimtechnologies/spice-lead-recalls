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
| Gazwi et al. 2022 (Sci Rep 12:9834, PMC9013364) | Egypt (El-Minia market) | **aqueous seed extract** (water, 65 °C), then digested | ICP-OES (iCAP 6500 Duo) | 12.45 ± 0.65 |
| Tefera & Teklewold 2021 (Heliyon 7:e07048, PMC8138603) | Ethiopia (markets) | whole seed, acid digest | flame AAS | 10.83–18.93 (three market means) |

## What the pattern shows

- **Three whole-seed digests, three origins, two independent analytical principles
  (collision-cell ICP-MS and hydride-generation AAS) all put coriander chromium
  below 1 ppm.** The Ugulu (2023) value is the newest piece and the first non-ICP-MS
  whole-seed measurement in the set; it agrees with the two ICP-MS values rather than
  with the high ones, even though it uses a different instrument and a different
  continent's seed, and even at the wastewater-irrigated site.
- **The two values above 10 ppm are the outliers.** One is a single flame-AAS market
  survey (Tefera & Teklewold, Ethiopia). The other (Gazwi, 12.45 ppm) is not a
  whole-seed digest at all but an **aqueous extract** of the seed read by ICP-OES, so
  it measures a different thing and is not directly comparable to the other studies or
  to NYC's total chromium "as sold."
- So among measurements comparable to NYC's (whole seed or powder), **three of the
  four studies report coriander chromium under 1 ppm**, and only one whole-seed study
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

## What it means for the two NYC coriander flags

Both edges (2.70 ppm for the Georgia 2019 sample, 5.48 ppm for the Bangladesh 2017
sample) sit **above all three whole-seed ceilings under 1 ppm** but **below** the
flame-AAS range and the aqueous-extract ICP-OES value. `cr_baseline.py` therefore
marks both pairs **unresolved**, and that remains the honest machine verdict.

The weight of the comparable (whole-seed) evidence, however, leans one way: three
studies under 1 ppm, across India, Bulgaria and Pakistan, by two independent methods,
against one flame-AAS study at 10–19 ppm. On that balance the chromium in NYC's two
coriander samples is more consistent with being pigment-associated — i.e. the
lead-chromate reading is probably real — than with ordinary natural background. It
cannot be *confirmed* from the literature, because one comparable whole-seed study
disagrees and coriander chromium plainly varies with soil and origin. Resolving it
needs a chromium blank measured on clean coriander of the same origin, ideally by
collision-cell ICP-MS. The lead finding (51–52 ppm) stands either way.

## Limits and provenance

- Each value was read from the paper's own table or abstract; preparation and method
  are reported as the paper states them. Surveys are small (n = 1–40 per study), and
  the dry-weight versus as-sold basis differs between papers. NYC reports total
  chromium as sold.
- Ugulu et al. (2023) describe a "gaseous hydride generation" step for chromium, which
  is unusual (chromium does not readily form a volatile hydride). We report the value
  as published and flag the oddity; its agreement with the two independent ICP-MS
  values is nonetheless notable.
- This note will be folded into the tool's ceiling table: the Ugulu whole-seed value
  will be added to `data/natural_cr_ceilings.csv` (v0.1.1) alongside `cr_baseline.py`'s
  full-run outputs. Adding it does not change the current verdicts, because at
  0.46–0.55 ppm it joins the ceilings already below both coriander edges.
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
- Gazwi HSS, et al. *Scientific Reports* 12:9834 (2022). PMC9013364. (ICP-OES, aqueous
  coriander seed extract.)
- Tefera M, Teklewold A. Health risk assessment of heavy metals in selected Ethiopian
  spices. *Heliyon* 7:e07048 (2021). doi:10.1016/j.heliyon.2021.e07048. PMC8138603.
  (Flame AAS.)
- Hammer D, Nicolas M, Andrey D. Improved chromium determination in various food
  matrices using dynamic reaction cell ICP-MS. *Atomic Spectroscopy* 26(6) (2005).
  (Residual-carbon interference over-estimates chromium in standard-mode ICP-MS; the
  reaction cell corrects it.)

Contact: MV2, Munim, Inc. — mv2@munimtech.com
