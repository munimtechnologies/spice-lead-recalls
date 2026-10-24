# Pre-registration: ochratoxin A in Canada's retail foods beyond spices (ota-foods 0.1.0)

PREREG-MARKER: ota-foods-0.1.0-prereg

By MV2 of Munim, Inc. Prepared with AI agents. Text CC BY 4.0; code Apache-2.0. Contains
information licensed under the Open Government Licence – Canada.

Written on 2026-10-24, before the grading job read any value of the 7,606 non-spice samples.
The commit time of this note is the record. A sealed job (`ota-foods-v1`) waits until this note
is public, makes its copy of `ota_foods.py` and `test_ota_foods.py` match the published copy,
runs the offline tests, and only then reads the data and grades.

## Data

- CFIA, *Ochratoxin A in Selected Foods – April 1, 2012 to March 31, 2018 and April 1, 2019
  to March 31, 2022*, open.canada.ca dataset `37300d06-0887-4353-bc9b-4f030f1089a2`,
  resource `ebc03414-5782-48e7-9294-30b37213479e`, released 2026-10-06.
- Pinned SHA-256 `3d86e455cb3855cdea7fced6f72f30ab5d435467cb242a578d00fa91764fbe82`
  (8,384 rows), as recorded by ota-spices 0.1.0 and by a names-only census job
  (`ota-census-v1`, 2026-10-24).
- CFIA's report on the same survey (Tables 1, 2, 5, 7 and 8; Appendix A and B) is read for the
  printed figures quoted below.

## What was and was not seen

- **Seen:** the header and the label counts of every non-result column (Function, Origin,
  Product, test type, component, unit, plan code), from the names-only census. Every unit is
  `ng/g` (= ppb) and every component is `Ochratoxin A`. CFIA's report and its printed tables.
  The published ota-spices 0.1.0 result note, which reports **spices** and four raisins above
  10 ppb.
- **Not seen:** any result value of a non-spice sample. ota-spices 0.1.0 also published a
  per-sample table (`data/ota_samples.csv`) that holds every value. No agent working on this
  study opened it. That cannot be proven, so this study is "blind as far as we know" in the
  same sense as coumarin-tea 0.1.0. Raisins are graded nowhere below, because their count above
  10 ppb is already published.
- **Not checked first:** how the file writes non-detects. The census left the Result column
  out on purpose. The rule below is registered, and the job reports a format census of the
  Result column. CFIA's coumarin files taught us that one file wrote non-detects as the bare
  detection limit. If this one does too, C1 and C2 fail, and that becomes the finding.

## Why this is new

CFIA's report gives one row per food category. It does not count samples against the EU
maximum levels, which were lowered or newly set on 1 January 2023 (Regulation (EU) 2022/1370,
now Annex I of Regulation (EU) 2023/915). Before this, nobody had read the open file by
product. We found no other reuse of it, which is no surprise: it was released 18 days ago.
The report also contradicts itself twice, and the file can settle both:

1. Table 2 prints infant formula as **13 positives (7%), maximum 11 ppb, average 1.1**. Table 8
   prints the same 192 samples by year as 2012: 148 samples, 35% positive, maximum 0.89;
   2014: 44 samples, 18% positive, maximum 0.46. That is about 60 positives, never above 0.89.
   Appendix B agrees with Table 8 (conventional soy formula 116 samples, 48% positive,
   0.040–0.89; organic soy 24, 17%; dairy 52, none detected).
2. The report's text says "the highest OTA level (9.1 ppb) was observed in a ground coffee
   sample". Tables 2 and 5 print a coffee maximum of 11 ppb (the 2013 row; 2015's maximum is
   9.1).

## Rules

**Non-detect rule.** A blank cell, a value starting with `<`, a not-detected token (`ND`,
`n.d.`, `n/d`, `not detected`, `non détecté`) or the number 0 is a non-detect, read as 0 ppb.
Any number above 0 is a detection. A value that is none of these counts as unparsed. A decimal
comma is accepted only when there is no point.

**Category map** (exact Product labels; see `CATEGORY_LABELS` in `ota_foods.py`). Cocoa:
`Cocoa Powder`. Coffee: `Coffee`, `Coffee - Ground`, `Coffee - Instant`, `Beverage - Coffee`,
plus the one `Dried mixes` sample in plan `2013_SB447`. Soy: `Beverage - Soy`, `Flour - Soy`,
`Tofu`, `Bean - Soy`, `Soy Products`, plus the two `Dried mixes` samples in plan `2012_SB447`.
Infant formula: `Infant Formula - Soy`, `Infant Formula - Dairy`. Licorice:
`Licorice Products`. Nuts: 17 nut and nut-butter labels. Seeds: 8 `Seed - …` labels. Dried
fruit: 21 fruit labels. Pulses: 18 bean, pea, lentil and chickpea labels. Spices: every label
starting with `Spice`, plus `Pepper`, `Pepper - Hot - Fresh`, `Herb - Cilantro - Dried`,
`Herb - Marjoram - Fresh` and `Celery`. Everything else is grain-based.

Category sizes under this map, from label counts alone:

| Category | File | CFIA Table 2 |
|---|---|---|
| Cocoa | 242 | 242 |
| Coffee | 790 | 790 |
| Dried fruit | 696 | 695 |
| Grain-based foods | 4,124 | 4,112 |
| Infant formula | 192 | 192 |
| Licorice | 140 | 140 |
| Nuts and nut butters | 148 | 148 |
| Pulses | 635 | 647 |
| Seeds | 279 | 279 |
| Soy | 361 | 361 |
| Spices | 777 | 778 |

Seven categories match exactly. Twelve samples CFIA counts as pulses carry grain-like labels
(the pulse surveys are plans 2016, 2017 and 2020, which also hold `Flour - Other`,
`Grain - Other` and `Pasta`). One sample is off between dried fruit and spices. Labels cannot
resolve either, so per-sample checks below use only the seven exact categories, plus dried
fruit for its maximum.

**EU maximum levels** (µg/kg = ppb). Checked against two independent summaries of Regulation
(EU) 2022/1370 (Agrolab; Food Safety Magazine), which agree on every level used here:

| Group | File labels | n | EU level |
|---|---|---|---|
| Infant cereals | `Infant Food - Cereal` | 409 | 0.50 |
| Breakfast cereals | `Cereal - Adult`, `Cereal - Children` | 609 | 3.0 (2.0 reported too) |
| Bakery wares, cereal snacks | 5 bakery labels, `Baked Goods`, `Crackers`, `Chips - Corn`, `Chips - Other` | 1,274 | 2.0 |
| Oat products | `Grain - Oat`, `Flour - Oat`, `Oatmeal`, `Bran - Oat` | 320 | 3.0 |
| Wheat products | `Flour - Wheat`, `Bran - Wheat`, `Wheat Products`, `Couscous` | 294 | 3.0 |
| Roasted coffee | `Coffee`, `Coffee - Ground` | 601 | 3.0 |
| Instant coffee | `Coffee - Instant` | 56 | 5.0 |
| Cocoa powder | `Cocoa Powder` | 242 | 3.0 |
| Licorice | `Licorice Products` | 140 | 10 (other liquorice confectionery) |
| Dried vine fruit | `Raisin`, `Currant` | 203 | 8.0 (descriptive only) |
| Dried figs | `Fig` | 48 | 8.0 |
| Other dried fruit | 15 labels (not vine fruit, fig, `Cranberry`, melon or plantain) | 441 | 2.0 |
| Pistachios, seeds, soybeans | `Nut - Pistachio`, `Seed - Sunflower`, `Seed - Pumpkin`, `Seed - Hemp`, `Bean - Soy` | 214 | 5.0 |

"Exceeds" means strictly above the level. Product composition is not in the file. Breakfast
cereals use 3.0, because the 2.0 row applies only to products without oilseeds, nuts or dried
fruit. Licorice uses the confectionery row (10), not the 50 or 80 rows for extract.

**Health Canada's proposed levels**, as CFIA's report applies them to grain-based foods:
infant cereals 0.5, wheat bran 7, other grain-based foods 3 ppb, counted above the level.
CFIA reports 119 grain-based foods over these levels, and 6 raisins over 10 ppb.

## Gate (G)

All must hold, or nothing below is graded:

- the SHA-256 above;
- 8,384 rows and 8,384 distinct sample numbers;
- unit `ng/g` and component `Ochratoxin A` on every row;
- every result parses under the non-detect rule;
- category sizes exactly as in the table above;
- the highest spice is a `Spice - Paprika` between 1,700 and 1,850 ppb (published by ota-spices).

## Consistency checks against CFIA's printed figures (C)

A failed C check is a finding about the file or the report, not about this method.

- **C1.** 4,056 samples are detected (CFIA: 4,056, 48%).
- **C2.** Detected counts equal Table 2 for cocoa 219, coffee 190, licorice 111, nuts 31,
  seeds 87 and soy 51.
- **C3.** Category maxima equal Table 2 at printed precision: cocoa 6.6, coffee 11, dried
  fruit 116, licorice 36, nuts 1.2, seeds 65, soy 3.0.
- **C4.** The lowest detected values equal Table 2 minima at printed precision: cocoa 0.070,
  coffee 0.043, dried fruit 0.041, licorice 0.042, nuts 0.048, seeds 0.050, soy 0.040.
- **C5.** Health Canada's proposed levels flag 116–122 grain-based foods (CFIA: 119; the
  ±3 allows for the 12 unresolved pulse samples and for CFIA's rounding).
- **C6.** Coffee by plan year equals Table 5: plan 2013 has 199 samples with maximum 11,
  2014 has 141 (6.7), 2015 has 300 (9.1), 2019 has 150 (1.2), and no coffee is in another plan.

## Which mean each printed average is (V)

Table 2's note says only detected values were averaged. CFIA's coumarin tables printed
all-sample means under the same note in 2011-12 and 2014-15. Here, simple arithmetic favours
positives-only for three categories. If coffee's 0.96 were an all-sample mean, the 190
positives would average 4.0 ppb, but Table 5's yearly positive averages are 0.20–1.8. The same
reasoning applies to nuts (0.95 against a maximum of 1.2) and soy (2.5 against 3.0).

- **V1.** The printed coffee (0.96), nuts (0.20) and soy (0.36) averages equal the
  positives-only mean at printed precision.
- **V2.** The printed cocoa (1.3), licorice (2.1) and seeds (1.1) averages equal the
  positives-only mean at printed precision.

## Blind predictions (P)

Each prediction rests only on CFIA's printed figures and on what the literature says about the
spread of OTA levels. The reasoning is given so that a miss can be read.

- **P1. Infant formula follows Table 8, not Table 2.** 55–65 of the 192 are detected, the
  maximum is 0.89 at printed precision, and no `Infant Formula - Dairy` sample is detected.
  *Why:* Table 8 and Appendix B agree with each other on about 60 positives and a 0.89
  maximum, and say dairy formula had none. Only Table 2 says 13, 11 and 1.1.
- **P2. The 9.1 ppb sentence describes 2015 only.** The top coffee in plan 2015 is a
  `Coffee - Ground` sample at 9.1, and the overall coffee maximum is in plan 2013.
- **P3.** 25–100 of the 409 infant cereals exceed 0.5 ppb, the level of both the EU and
  Health Canada's proposal. *Why:* CFIA prints 47% detected with an average of 0.62 among
  positives. Under a log-normal spread, between about a third and a half of positives would
  sit above 0.5, which is 60–95 samples. The lower bound allows for a tighter spread.
- **P4.** Infant cereals are more than half of the grain-based foods over Health Canada's
  proposed levels. *Why:* the other grain-based foods need more than 3 ppb. In Table 7's
  rows for the years in this file, the grain-based foods average 0.24–0.53 among positives,
  with yearly maxima of 1.5–7 apart from one 65 ppb waffle. Oats reach 21 and wheat 13.
- **P5.** A larger share of oat products than of wheat products exceeds 3 ppb. *Why:* the oat
  rows of Table 7 reach 21 ppb, and oat flour averages 2.0. Wheat's highest in these years is
  13, and its sub-product averages are 0.20–0.86, apart from bulgur at 2.2.
- **P6.** At most 18 of the 609 breakfast cereals (3%) exceed 3 ppb. *Why:* the average
  among positives is 0.50.
- **P7.** 1–64 of the 1,274 bakery wares and cereal snacks (at most 5%) exceed the EU's
  2 ppb. *Why:* the averages are 0.24–0.95 and the maximum is 65 (frozen waffles).
- **P8.** 1–30 of the 601 roasted coffees exceed the EU's 3 ppb, and 1–12 of the 56 instant
  coffees exceed its 5 ppb. *Why:* among positives, beans average 0.56 and ground coffee
  0.66, against 2.5 for instant (64% detected). The coffee maxima are 11 and 9.1.
- **P9.** 5–45 of the 242 cocoa powders exceed the EU's 3 ppb. *Why:* 90% are detected, the
  average is 1.3 and the maximum 6.6.
- **P10.** 1–8 of the 140 licorice products exceed 10 ppb. *Why:* the average is 2.1 and the
  maximum 36.
- **P11.** At most 8% of the 441 other dried fruits exceed the EU's 2 ppb, and at most 3 of the
  48 dried figs exceed 8 ppb. *Why:* the printed detection rates are low: apricots 26%, figs
  28%, dates 9%, prunes and pineapples 8%.
- **P12.** At most 6 of the 214 pistachios, sunflower, pumpkin and hemp seeds and soybeans
  exceed the EU's 5 ppb. *Why:* the nut maximum is 1.2 and the soy maximum 3.0. The only high
  seed value printed is a single 65.

## Reported, not graded

- A format census of the Result column: counts of `<` values, tokens, zeros and blanks, and
  the number of decimals in detected values.
- The full table for all 11 categories against Table 2, with both means and the verdict for
  each.
- Every EU group's count over its level, breakfast cereals over 2.0, the other cereal products
  (pasta, flours, baking mixes, other grains) over 3.0, and a total across all EU groups.
- Coffee by plan year, with the detection rate against Table 5.
- Infant formula by plan year, against Table 8.
- Health Canada's split by infant cereal, wheat bran and other grain, with ≥ as well as >, and
  dried vine fruit over 10 ppb (> and ≥), against CFIA's 6.
- A per-sample table of the 7,606 non-spice samples. The file names no brand.

## Limits, stated in advance

- EU levels are a yardstick only. Canada has no OTA maximum level in force for these foods;
  Health Canada's 2009 proposals remain proposals. CFIA judged the levels found not a health
  concern, and nothing here says otherwise.
- The file has no composition, so each sample gets one EU row by its label. Breakfast cereals
  and bakery products with dried fruit or nuts carry higher EU levels than those used here.
  Generic labels such as `Dried Fruit` and `Mixed Fruit` may include vine fruit.
- `Origin` is often the packer's country or missing (3,703 rows say UNKNOWN). No origin
  analysis is registered.
- Plan codes are taken as CFIA's survey years. C6 tests that reading for coffee.

## Files

- `ota_foods.py`: the grader (standard library only).
- `test_ota_foods.py`: offline tests on synthetic rows.
- After grading: `docs/ota-foods-0.1.0-result.md`, `data/ota_foods_categories.csv`,
  `data/ota_foods_eu.csv`, `data/ota_foods_samples.csv` and a pinned result test.
