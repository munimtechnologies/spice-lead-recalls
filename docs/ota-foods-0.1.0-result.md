<!-- RESULT-MARKER: ota-foods-0.1.0-result -->
# ota-foods 0.1.0: result

By MV2 of Munim, Inc. Made with AI agents working in MV2's name. Code Apache-2.0; this note and the
tables CC BY 4.0. Data: CFIA, *Ochratoxin A in Selected Foods* (2012-2018 and 2019-2022), open.canada.ca
dataset `37300d06-0887-4353-bc9b-4f030f1089a2`, released 2026-10-06 (Open Government Licence - Canada).
A check of CFIA's published figures against the agency's own open file, and a count of the samples over
the EU maximum levels in force since 2023. It is **not a compliance finding** (Canada has no ochratoxin A
maximum level in force for these foods), not about any brand, and not individual dietary or medical advice.

Grades [`ota-foods-0.1.0-prereg.md`](ota-foods-0.1.0-prereg.md), public at tag `v0.4.50` before any value
of the 7,607 non-spice samples was read.

## Headline

**Gate passed; 20 of 21 met.** The one miss, C5, is a finding about the report, not the method. Two things
stand out:

1. **CFIA's Table 2 infant-formula row is wrong, and its own Table 8 is right (P1).** Table 2 prints
   infant formula as 13 positives, maximum 11 ppb, average 1.1. The open file holds **60 of 192 detected,
   maximum 0.886 ppb** — which matches Table 8 and Appendix B of the same report exactly (plan 2012: 148
   samples, 52 detected = 35%, max 0.886 ≈ 0.89; plan 2014: 44 samples, 8 detected = 18%, max 0.465 ≈ 0.46;
   no dairy formula detected). The pre-registration named this contradiction in advance and bet on Table 8.
2. **For ochratoxin A, CFIA's Table 2 averages really are positives-only means (V1, V2),** exactly as the
   table note says — unlike CFIA's coumarin tables, where the same note sat over all-sample means (see the
   [coumarin table audit](coumarin-cfia-table-audit-0.1.0-result.md)). Every one of the six testable
   averages is the positives mean, not the all-sample mean.

Everything CFIA printed for the seven categories whose labels map one-to-one (detected counts, maxima,
minima), the coffee survey-year rows of Table 5, and the overall 48% detection rate reproduce from the
file exactly. All twelve blind predictions held.

## How it was graded

Sealed compute job `ota-foods-v1` (2026-10-24 21:36-21:37 UTC, `python:3.12`, no host paths, 1 GB).
`check_prereg.py` confirmed the pre-registration was public with its marker and made the bundled
`ota_foods.py` and `test_ota_foods.py` equal the published copies; the offline tests (synthetic rows only)
passed; `ota_foods.py` 0.1.0 then read the SHA-256-pinned file
(`3d86e455…be82`, 1,353,085 bytes, 8,384 rows) and graded. The registered non-detect rule reads a blank
cell, a `<` value, a not-detected token or the number 0 as a non-detect (0 ppb) and any positive number as
a detection.

## Gate and predictions

| id | prediction | observed | grade |
|---|---|---|---|
| G (gate) | SHA-256; 8,384 rows and distinct samples; unit ng/g and component Ochratoxin A on every row; every result parsed; the 11 category sizes as registered; the published spice maximum (a paprika, 1,700-1,850 ppb) | all seven checks pass | **pass** |
| C1 | 4,056 of 8,384 detected (CFIA: 4,056, 48%) | 4,056 (3,540 of 7,607 non-spice + 516 spices) | met |
| C2 | positives equal Table 2 for cocoa, coffee, licorice, nuts, seeds, soy | 219, 190, 111, 31, 87, 51 — all match | met |
| C3 | category maxima equal Table 2 (cocoa, coffee, dried fruit, licorice, nuts, seeds, soy) | 6.58→6.6, 10.9→11, 116.4→116, 36.1→36, 1.16→1.2, 64.7→65, 2.96→3.0 | met |
| C4 | lowest detected values equal Table 2 minima (same seven) | 0.07, 0.043, 0.041, 0.042, 0.048, 0.05, 0.04 — all match | met |
| C5 | Health Canada's proposed levels flag 116-122 grain-based foods (CFIA: 119) | **125 over** (126 at or above) | **failed** |
| C6 | coffee by plan equals Table 5; no coffee in another plan | 2013: 199/10.9; 2014: 141/6.71; 2015: 300/9.103; 2019: 150/1.21 — all match | met |
| V1 | coffee, nuts, soy averages are positives-only means | all three positives | met |
| V2 | cocoa, licorice, seeds averages are positives-only means | all three positives | met |
| P1 | infant formula follows Table 8: 55-65 detected, max 0.89, no dairy detected | 60 detected, max 0.886, 0 dairy | met |
| P2 | the 9.1 ppb ground coffee is the 2015 maximum; overall max is 2013 | 2015 top = Coffee - Ground 9.103; overall max = 2013 Coffee - Instant 10.9 | met |
| P3 | 25-100 of 409 infant cereals over 0.5 ppb | 95 | met |
| P4 | infant cereals are more than half of the grain-based foods over the HC levels | 95 of 125 | met |
| P5 | a larger share of oat products than wheat products over 3 ppb | oat 8/320 (2.5%) vs wheat 6/294 (2.0%) | met |
| P6 | at most 18 of 609 breakfast cereals over 3 ppb | 3 | met |
| P7 | 1-64 of 1,274 bakery wares / cereal snacks over 2 ppb | 9 | met |
| P8 | 1-30 of 601 roasted coffees over 3; 1-12 of 56 instant over 5 | 4 and 4 | met |
| P9 | 5-45 of 242 cocoa powders over 3 ppb | 10 | met |
| P10 | 1-8 of 140 licorice over 10 ppb | 6 | met |
| P11 | ≤ 8% of 441 other dried fruit over 2; ≤ 3 of 48 figs over 8 | 7 (1.6%) and 0 | met |
| P12 | ≤ 6 of 214 pistachios/seeds/soybeans over 5 ppb | 2 | met |

## The finding: CFIA's Table 2 infant-formula row

CFIA's report prints infant formula three ways, and only Table 2 disagrees with the file:

| source | n | positive | maximum | average |
|---|---|---|---|---|
| Table 2 | 192 | 13 (7%) | 11 ppb | 1.1 |
| Table 8 (2012) | 148 | 35% (52) | 0.89 | — |
| Table 8 (2014) | 44 | 18% (8) | 0.46 | — |
| **the open file** | 192 | **60 (31%)** | **0.886** | 0.137 (positives), 0.043 (all) |

The file reproduces Table 8 and Appendix B to the digit (52 and 8 detected, 0.886 and 0.465 maxima) and
contradicts Table 2 on every number. A maximum of 11 ppb and an average of 1.1 appear nowhere in the 192
infant-formula samples; 11 ppb is the printed coffee maximum. The most likely reading is that Table 2's
infant-formula row was filled from the wrong source. This resolves the first contradiction the
pre-registration flagged. A short erratum note is drafted for CFIA but not sent.

CFIA's text also says "the highest OTA level (9.1 ppb) was observed in a ground coffee sample," while
Tables 2 and 5 print a coffee maximum of 11. The file settles it (P2): the overall coffee maximum is
**10.9 ppb in a 2013 instant coffee**, and 9.103 ppb is the maximum of the 2015 survey, in a ground
coffee. The sentence describes the 2015 survey; the table describes the whole file.

## Which mean the averages are (V1, V2)

For every testable category the printed average equals the positives-only mean at printed precision and
is well clear of the all-sample mean:

| category | printed avg | positives mean | all-sample mean | verdict |
|---|---|---|---|---|
| coffee | 0.96 | 0.962 | 0.231 | positives |
| nuts | 0.20 | 0.200 | 0.042 | positives |
| soy | 0.36 | 0.356 | 0.050 | positives |
| cocoa | 1.3 | 1.343 | 1.216 | positives |
| licorice | 2.1 | 2.115 | 1.677 | positives |
| seeds | 1.1 | 1.144 | 0.357 | positives |

So for ochratoxin A the Table 2 note ("only positive results were used") is accurate. The coumarin files
printed all-sample means under the same note; this one does not. Reusable fact: the same agency's tables
cannot be assumed to use one convention — each survey's table has to be checked against its own file.

## The miss: Health Canada's grain-based count (C5)

CFIA's report says 119 grain-based foods exceeded Health Canada's proposed levels (infant cereals 0.5,
wheat bran 7, other grain-based foods 3 ppb). The file gives **125 strictly over, 126 at or above**:

| part | level | over |
|---|---|---|
| infant cereals | 0.5 | 95 |
| wheat bran | 7 | 0 |
| other grain-based | 3 | 30 |
| **total** | | **125** |

The gap of 6-7 is only partly resolved. The twelve samples that carry grain-type labels but which CFIA
counts under pulses (`Grain - Other`, `Flour - Other`, `Pasta` in the pulse surveys) account for just one
of it: exactly one such sample exceeds its level — a `Flour - Other` in the 2017 survey at 3.34 ppb — so
reclassifying all twelve as CFIA does lowers the count to at most 124, still above 119. The remaining
gap cannot be told apart from the open file: CFIA may have excluded a product on composition grounds,
applied a level to the food as eaten, or rounded a borderline value. The count is reported honestly as
125; the direction and the infant-cereal share (P4: 95 of 125, more than half) are unaffected.

## How often foods cross the EU maximum levels (reference only)

The EU lowered or newly set these levels on 1 January 2023 (Regulation (EU) 2022/1370, now Annex I of
Regulation (EU) 2023/915). CFIA's report does not count against them. Per `data/ota_foods_eu.csv`:

| EU group | level (ppb) | n | detected | over | maximum |
|---|---|---|---|---|---|
| infant cereals | 0.5 | 409 | 190 | 95 (23.2%) | 4.85 |
| breakfast cereals | 3.0 | 609 | 360 | 3 | 6.95 |
| bakery wares, cereal snacks | 2.0 | 1,274 | 924 | 9 | 65.4 |
| oat products | 3.0 | 320 | 143 | 8 | 21.2 |
| wheat products | 3.0 | 294 | 220 | 6 | 12.8 |
| roasted coffee | 3.0 | 601 | 150 | 4 | 9.103 |
| instant coffee | 5.0 | 56 | 36 | 4 | 10.9 |
| cocoa powder | 3.0 | 242 | 219 | 10 | 6.58 |
| licorice confectionery | 10 | 140 | 111 | 6 | 36.1 |
| dried vine fruit | 8.0 | 203 | 144 | 4 | 116.4 |
| dried figs | 8.0 | 48 | 11 | 0 | 0.14 |
| other dried fruit | 2.0 | 441 | 70 | 7 | 18.0 |
| pistachios, seeds, soybeans | 5.0 | 214 | 43 | 2 | 64.7 |

Across all thirteen groups, **158 of 4,851 samples** are over their EU level. Infant cereals carry most of
the count (95), at a modest 4.85 ppb maximum; the highest single reading over a level is a 116.4 ppb dried
vine fruit (already reported by [ota-spices](ota-spices-0.1.0-result.md) in context). Breakfast cereals,
oat and wheat products use the 3.0 ppb row; a product with oilseeds, nuts or dried fruit would carry a
higher level, so these are upper counts.

As far as we found, this is the first time the open file has been read by product and counted against the
2023 EU levels. It was released 18 days before this study, which is why no other reuse was found.

## How the file codes non-detects

The pre-registration left the Result column out of its census on purpose, because CFIA's 2011-12 coumarin
file wrote non-detects as the bare detection limit. This file does not: of 8,384 results, **4,056 are
positive and 4,328 are a literal `0`** — no `<` value and no not-detected token anywhere. Detected values
carry 0 to 4 decimal places (0: 52, 1: 274, 2: 1,621, 3: 2,104, 4: 4) and one value has nine. So a reader
who takes a blank or `0` as a non-detect and any positive number as a detection reproduces CFIA's 48%
exactly, and the detection-limit trap that caught the coumarin surveys does not arise here.

## Data and test

- `data/ota_foods_categories.csv`: the 11 Table 2 categories (n, detected, minimum, median, both means,
  maximum, and CFIA's printed figures and the verdict).
- `data/ota_foods_eu.csv`: the 13 EU groups (level, n, detected, over, share, maximum).
- `data/ota_foods_samples.csv`: one row per non-spice sample (7,607 rows: plan, function, declared origin,
  product label, category, EU group and level, the raw result, the parsed ppb and the detect flag). The
  file names no brand. The 777 spices were published by [ota-spices 0.1.0](ota-spices-0.1.0-result.md).
- `test_ota_foods_result.py` recomputes every number in this note from the per-sample table: the ten
  non-spice category rows, the thirteen EU-group counts, the Health Canada split (95/0/30, 125 and 126),
  the six positives-mean verdicts, infant formula by plan against Table 8, the 4,056 detection total and
  the non-detect census, and the full 21-grade pattern (20 met, C5 the only miss). Plain `csv`,
  `statistics`, `unittest`.

## Limits

- EU levels are a yardstick only. Canada has no ochratoxin A maximum level in force for these foods;
  Health Canada's proposals remain proposals, and CFIA judged the levels found not a health concern.
- The file carries no composition, so each sample gets one EU row by its label. Breakfast cereals and
  bakery products with dried fruit or nuts carry higher EU levels than used here, so those counts are
  upper bounds.
- Category membership is from exact Product labels. Twelve grain-labelled samples CFIA counts as pulses,
  and one sample sits between dried fruit and spices, cannot be resolved from labels; the per-sample
  checks use the label mapping as registered.
- The Table 2 reading of the infant-formula row is an inference about how the report was compiled, not a
  statement by CFIA; it is drawn from the file's exact agreement with Table 8 and Appendix B.
- No finding here concerns the safety of any product.

<!-- RESULT-MARKER: ota-foods-0.1.0-result -->
