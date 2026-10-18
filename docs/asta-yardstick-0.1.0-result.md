# ASTA yardstick 0.1.0: result

This is the graded result for the pre-registration in
[`asta-yardstick-0.1.0-prereg.md`](asta-yardstick-0.1.0-prereg.md) (v0.4.30). The predictions, the category
map and the rule that non-detects count as below the level were fixed there before any count was made.

**Author:** MV2, Munim, Inc. (mv2@munimtech.com). Work made with AI agents.
**License:** text CC BY 4.0; code Apache-2.0.

- **Grader:** [`../asta_yardstick.py`](../asta_yardstick.py) (standard library only).
  [`../test_asta_yardstick.py`](../test_asta_yardstick.py) recomputes every count below from the committed
  tables and lists every exceeding row by its `row_id`.
- **Data (already in this repo):** `data/nyc_spice_lead_snapshot_2026-10-17.csv` (NYC DOHMH "Metal Content
  of Consumer Products", da9u-wz3r, frame S = store survey, laboratory results in ppm) and
  `data/raman_reach_samples.csv` (Forsyth et al. 2026, *npj Science of Food*, Supplementary Table 8, CC BY 4.0).
- **Yardstick:** ASTA *Guidance Levels for Heavy Metals in Spices* V3 (2026-06-08), Table 2/3, lead:
  fruit 0.60, seed/aril 0.90, bud 1.0, flower pistil 1.0, root/rhizome 1.50, bark 2.0, herb 2.0 µg/g.
  These are **voluntary industry guidance, not law**. "Exceeds ASTA" does not mean illegal, and it does not
  mean unsafe for any one person. A sample counts only if its lead is strictly above the level.

## Headline

| frame | n | over the ASTA level | gross (≥ 50 ppm), for comparison |
|---|---|---|---|
| NYC store survey (frame 3) | 477 | **41 (8.6%)** including blends; **29 (6.1%)** single spices only | 2 (0.4%) |
| Eastern-India market turmeric (frame 15) | 503 | **163 (32.4%)** at least; **up to 503** (see the detection-limit problem below) | 139 (27.6%) |

The near-background yardstick raises the NYC store count about 15-20 times over the gross count. But it does
**not** do that the way we predicted. The extra exceedances are not low-level background in pepper and cumin.
They are a few specific products: cinnamon, Georgian "saffron" and spice blends.

## NYC store survey (n = 477; 179 with a detected value, 298 non-detects)

| ASTA category (level, µg/g) | rows with a detected value | over the level |
|---|---|---|
| bark: cinnamon (2.0) | 22 (25 rows in all) | **11** |
| flower pistil: "saffron" (1.0) | 7 | **7** |
| fruit: chili, pepper, paprika, sumac (0.60) | 42 | 5 |
| root/rhizome: turmeric, ginger (1.50) | 26 | 4 |
| seed: cumin, fenugreek (0.90) | 4 | 1 |
| herb: oregano, bay, thyme, basil (2.0) | 6 | 1 |
| bud: clove (1.0) | 1 | 0 |
| **single spices** | **108** | **29** |
| blends (no ASTA category; 2.0 bucket) | 40 | 12 |
| not a mapped spice (see below) | 31 | not scored |

- **Cinnamon.** 21 of the 25 cinnamon rows were bought between 2024-01-04 and 2024-01-23, and 10 of those 21
  are above 2.0 µg/g (highest 23 µg/g). That buying round came weeks after the late-2023 recall of
  cinnamon applesauce pouches for lead; the dataset does not say why these samples were bought.
- **"Saffron."** All 7 rows are above 1.0 µg/g: five at 14-21 µg/g bought in 2016 (declared Georgia) and two
  at 1.1 and 1.3. In Georgian shops "saffron" (*imeruli shaphrani*, Imeretian saffron) usually means dried
  marigold (*Tagetes*) petals, not crocus pistils. So the ASTA category is uncertain for these rows, but
  14-21 µg/g is above every ASTA level (the highest is 2.0).
- **Blends** over 2.0: two Yemeni spice mixes at 570 and 610 µg/g (these are the frame's only two gross
  results), five five-spice powders (2.4-3.0), two Jamaican curry powders (2.2 and 20), a curry powder
  (12), a Mexican spice mix (5.9) and a Georgian soup seasoning (3.52).
- **Fruit and seed spices**, the categories whose levels sit inside the 0.4-3 ppm background band, held only
  6 of the 29 single-spice exceedances: chili/pepper at 0.66-1.1 µg/g and one ground cumin at 2.6 µg/g.
- **Not scored (31 rows with a detected value):** 11 tequesquite (a mineral salt), 5 hoja santa leaves,
  2 barberry, 2 achiote/annatto, 2 safflower, and 9 single rows (Svanetian salt, ground shrimp, *utskho
  suneli*, *comino molido*, *piment doux*, a Vietnamese curry-powder name written without accents, and three
  names we could not identify: "ZRA 3PA", "Pikin", "Anelina"). Mapping the obvious ones by hand changes little:
  barberry at 0.86 (as a fruit) and achiote at 3.0 (as a seed) would each add one exceedance; *comino molido*
  (cumin, 0.30), *piment doux* (sweet pepper, 0.28), *utskho suneli* (blue fenugreek, 0.40) and the curry
  powder (0.73, a blend) stay below. Safflower petals at 3.5 would add a third only if held to the pistil
  level. So the map's edges move the NYC count by 2, or 3 at most.

## Eastern-India market turmeric (n = 503)

Every sample is turmeric (root/rhizome, 1.50 µg/g). The study measured lead by handheld XRF with a
**detection limit of 4 µg/g**, which is **above** ASTA's 1.50 µg/g level. Its table codes the 340 non-detects
as 2 µg/g (half the detection limit).

- 163 samples have a measured value (lowest 3 µg/g), and all 163 are above 1.50 µg/g: **163 / 503 = 32.4%**.
  152 of them are above 10 µg/g (India's limit), 6.7 times the ASTA level or more.
- The 340 non-detects can't be judged against ASTA: the instrument cannot show whether a sample is below
  1.50 µg/g. Under the pre-registered rule they count as below, so 163 is a **lower bound**. The true number
  lies anywhere from 163 to 503.
- A naive comparison of the coded value (2 > 1.5) would report 503 of 503 (100%) over the level. That number
  is an artefact of the non-detect code, not a finding.

## Pre-registered predictions

| prediction | result | graded |
|---|---|---|
| Frame 3: 25 exceedances, 80% interval [8, 55] | 41 with blends, 29 single spices | inside the interval; point estimate too low |
| Frame 15: 175 exceedances, floor 152, 80% interval [152, 210] | 163 | inside the interval; floor held |
| H1: NYC store at least 3× its gross rate (at least 6 samples) | 41 (or 29) of 477 | **met** |
| H2: frame 15 above 30% and above 3× the NYC store rate | 32.4% vs 8.6% (or 6.1%) | **met** |
| H3: NYC exceedances mostly fruit/seed (background); frame 15 turmeric far above the level | NYC: 6 of 29; frame 15: 152 of 163 above 10 µg/g | **not met** (the NYC half failed) |

H1 held, but its stated reason did not. We expected background lead in low-level spices to push many NYC
samples just over 0.6-0.9 µg/g. Instead, 5 of 42 detected fruit-spice rows and 1 of 4 seed rows were over.
The exceedances cluster in **specific products** (cinnamon bought in one month, Georgian "saffron" and
blends), several of them far above any level.

## What this means

1. **A different bar finds a different problem.** At 50 ppm the NYC store frame shows two Yemeni blends.
   At ASTA's levels it shows a cinnamon problem (10 of 21 in January 2024) and a Georgian "saffron" problem
   (14-21 µg/g). Neither of those is visible at the gross bar.
2. **Field XRF at a 4 µg/g detection limit can't check ASTA compliance for turmeric.** To screen against
   1.50 µg/g you need a lab method (ICP-MS) or an instrument that detects lead below that level. This is a
   limit of the tool, not a criticism of the study, which was built to find adulteration far above 10 µg/g.
3. **For Yellow Flag:** a Raman screen reaches lead chromate at about 0.1-0.5% w/w, which is about
   640-3,200 µg/g of lead. It targets gross adulteration and can't speak to guidance-level compliance at 0.6-2.0
   µg/g. The pitch has to keep saying so.

## Limits

- ASTA levels are voluntary guidance chosen to match EU limits. Nothing here is advice to any person about
  any food, and no brand named here has been found to break any law.
- The category map is name-based and published in full in the grader. Blends have no ASTA category; the 2.0
  bucket is our choice, fixed in the pre-registration. Georgian "saffron" is probably marigold.
- NYC's open table gives no detection limit per row, so its non-detects also count as below the level, and
  both frames' counts are lower bounds.
- The NYC store survey is not a random sample of shelves. DOHMH chooses what to buy, and buying rounds (like
  January 2024 cinnamon) are targeted. Its rates describe what DOHMH bought, not the NYC market.
- Frame 15 lead is handheld XRF calibrated to ICP-MS (mean error about 18% for roots, per the article), one
  sample per distinct type on sale.

Data: NYC DOHMH, NYC Open Data da9u-wz3r (snapshot 2026-10-17); Forsyth J.E. et al., npj Science of Food (2026),
doi:10.1038/s41538-026-00867-8, Supplementary Table 8, CC BY 4.0. Levels: ASTA Guidance Levels for Heavy
Metals in Spices V3 (2026-06-08). Prepared by MV2 of Munim, Inc. with AI agents.
