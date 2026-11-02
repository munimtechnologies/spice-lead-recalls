# perchlorate-series 0.1.0: names-only census of CFIA's three perchlorate files, and the label maps

CENSUS-MARKER: perchlorate-series-0.1.0-census

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This follows the [perchlorate-series 0.1.0 pre-registration](perchlorate-series-0.1.0-prereg.md)
(`v0.4.106`). The sealed job `perchlorate-census-v1` ran on 2026-11-02 from 12:14 to 12:16 UTC
(python:3.12, 1 GB, no host paths). It waited until the pre-registration was public, checked its
modules against the published copies and ran the 7 offline tests (all passed). Only then did it
open the three files, and it read labels, units, cell shapes, sample counts and sampling years
only. **No result value has been read.**

This note grades the gate and the six census items, fixes the label maps for p10 and p11, and says
which value items the census already settles. The p13 six-group map and the grader follow in a
separate grader note, also before any value is read. This is a reproducibility check of open
government data. It is not a compliance finding (Health Canada has set no maximum level for
perchlorate in food), not about any brand, and not dietary or medical advice.

## Census items: 4 of 7 held

| ID | Registered | Observed | Met |
|---|---|---|---|
| G | each file matches its portal size and MD5; one result per sample; 611 / 1,426 / 477 samples | all hold (95,033 / 228,127 / 78,310 bytes; one perchlorate row per sample; every row ng/g; every result cell a number) | ✅ (gate) |
| S1 | p10: 433 fresh fruits and vegetables / 89 dairy / 89 formulas; dairy 23 cheese / 42 milk / 24 yogurt | 433 / 89 / 89; Cheese 23, Milk 42, Yogurt 24 | ✅ |
| S2 | p10 fruit and vegetables by origin 146 domestic / 285 imported / 2 unknown (secondary source) | 146 / 285 / 2 | ✅ |
| S3 | p11: 881 / 225 / 233 / 87; by year 663 and 763 | 881 / 225 / 233 / 87 under the map below; the plan codes split 663 (2011) and 763 (2012) | ✅ (groups; see below for dates) |
| S4 | p11 first year holds 68 of the 87 formulas; creams 8 in the first year and 9 in the second | the file has 15 samples labelled Cream, so 8 + 9 = 17 is impossible | ❌ |
| S5 | p13: 20 cheeses, 30 yogurts, 30 infant formulas; dairy is those 50 | cheeses 20 and yogurts 30 hold; **the file has 39 infant formulas** | ❌ |
| S6 | so 2013-14's "54% of infant formula" is impossible | with 39 formulas, 21 of 39 = 53.8% rounds to 54% | ❌ |

**S3 and the dates.** The census module looks for a column whose name starts with "Date Sampled".
The p11 file names it `DateSample`, so the module did not read p11's dates. The year split above
comes from the plan codes (`2011_TS006` 663, `2012_TS006` 763), which equal the report's years.
The grader reads `DateSample` (a label, not a value) and reports the date split and S4's formula
year split before it reads any result.

**S2 held,** so the 2017 review's figures for the 2010-11 origins match the open file exactly.

## The main census finding: Table 3's formula rows leave out the soy formulas

Table 3 of the 2020-21 report restates one infant-formula row for each earlier survey. In every
one of the three files, its sample count equals the number of formulas **not** labelled soy:

| Survey | Formulas in the file | Labelled soy | Not soy | Table 3 |
|---|---|---|---|---|
| 2010-11 (p10) | 89 | 15 (`Infant Formula - Soy`) | 74 (`Infant Formula - Dairy`) | 74 |
| 2011-13 (p11) | 87 | 19 | 68 (`Infant Formula - Dairy` 67, `Infant Formula - Dairy - Organic` 1) | 68 ("2011") |
| 2013-14 (p13) | 39 | 9 | 30 (`Infant Formula - Dairy` 23, `Infant Formula - Other` 7) | 30 |

The 2020-21 report covers dairy products and dairy-based formula, so leaving soy out of the
comparison is reasonable, but Table 3 does not say so. This explains two of the pre-registration's
report-only findings: R2 (74 versus 89 in 2010-11) and R3 (the "54%" that seemed impossible with
30 formulas is possible with all 39). For p11, 68 is the count over **both** survey years; the
grader will show whether all 68 non-soy formulas fall in the first year, as Table 3's "2011"
label implies.

## What the files look like

**p10 (2010-11), 611 samples.** 16 bilingual columns; plan `2010_TS006`. 35 product labels.
Sampling dates run from 5 July 2010 to 14 March 2011 (`D-Mon-YY`). Region is blank for 223 samples
(Atlantic 63, Ontario 108, Quebec 88, West 129). IDs are `2010PER0001` style. Formulas are all
imports; milk and yogurt are all domestic; cheese is 4 domestic and 19 imported. Spinach has 2
samples with function Unknown, the only unknowns, as S2 needs.

**p11 (2011-13), 1,426 samples.** Same 16 columns, but the date column is `DateSample`. 66 product
labels. The file mixes two ID styles: 663 IDs are `2011PER0001` style (as many as the 2011 plan
code has), and 763 are `C2012PERC00003` to `C2012PERC00800` with 35 numbers missing. Five
second-year IDs carry a `D` suffix (`00054D`, `00220D`, `00393D`, `00519D`, `00566D`). Regions:
Atlantic 97, Ontario 534, Quebec 329, West 466.

**p13 (2013-14), 477 samples.** Same 16 columns; plan `2013_TS006`. 88 product labels. Sampling
dates run from 13 June 2013 to 31 March 2014. IDs run from 1 to 500 with 23 numbers missing.
Regions: Atlantic 29, Ontario 187, Quebec 107, West 154.

## Label maps (fixed before any value is read)

**Organic and greenhouse.** Throughout, a label's `- Organic` (any case) or ` (GH)` variant joins
its base product (for example `Tomato (GH)` is tomato, `Lettuce - Leaf - Organic` is lettuce).

**p10 groups.**
- Dairy (89): `Cheese` 23, `Milk` 42, `Yogurt` 24.
- Infant formula (89): `Infant Formula - Dairy` 74, `Infant Formula - Soy` 15. The soy-based
  formula of V2 is `Infant Formula - Soy`. V4's subset of 74 is `Infant Formula - Dairy`.
- Fresh fruits and vegetables (433): every other label.
- Commodities (V2): one per base product after the organic/GH rule, with `Lettuce`,
  `Lettuce - Leaf` and `Lettuce - head` pooled as lettuce. `Cabbage - Chinese`, `Misc Vegetables`,
  `Radicchio`, `Arugula`, `Chard` and `Kale` stay separate commodities.

**p11 groups.**
- Infant formula (87): the three `Infant Formula` labels. Table 3's formula row is the 68 not
  labelled soy.
- Juice (225): every `Juice - ...` label (213), `Cider - Apple` 6, `Nectar - Other` 4,
  `Nectar - Prune` 2.
- Dairy-based products (233): `Cheese` 1, `Cream` 15, `Dessert - Frozen` 28,
  `Dessert - Frozen (Dairy)` 3, `Desserts` 7, `Dressing` 28, `Misc - Dairy` 85 (+2 organic),
  `Pudding` 25, `Sauces` 37 and `Misc` 2. The total 233 needs the two `Misc` samples.
- Fresh fruit (356): blueberry 22, grapefruit 25, lemon 25, cantaloupe 22, orange 92,
  strawberry 86, watermelon 84.
- Fresh vegetables (525): arugula 1, chard 48, cucumber 95, endive 1, kale 1, lettuce (all seven
  lettuce labels) 247, spinach 44, tomato 88.
- **Why tomato and cucumber are vegetables here.** It is the only placement the report's own
  figures allow. With 356 fruits and 525 vegetables, "44%" means 155-158 fruit detects and "74%"
  386-391 vegetable detects, 541-549 in all, which meets the 548-550 fresh-produce detects implied
  by the other printed counts (R5). With tomatoes counted as fruit (444 / 437) the same percentages
  give 516-522, which cannot.
- Leafy green vegetables (V7): arugula, chard, endive, kale, lettuce and spinach, pooled (342).
  V7 ranks this pooled group against cucumber, tomato and each fresh fruit.
- Creams (V6): `Cream`, by sampling year from `DateSample`.

**p13.** Dairy (50) is the cheese labels (`Camembert` 3, `Cheddar` 1, `Cheese` 13, `Feta` 2,
`Gouda` 1) and the yogurt labels (`Yogurt` 10, `Yogurt - Frozen` 10, `Beverage - Yogurt` 10).
Infant formula is all 39; Table 3's formula row (V9) is the 30 not labelled soy. The other four
groups (fresh vegetables, processed fruit and vegetable products, grain products, assorted foods)
need a map for the other 77 labels, including herbs with and without "Fresh", 14 potato labels
and dried fruit. It is fixed in the grader note before any value is read.

**Coding.** Every result cell in all three files is a number, and no cell holds `<`, `ND` or
text, so non-detects must be written as numbers. As registered, a sample is a detect when its
result is above zero. The grader first reports how many results are exactly zero and the five
smallest above zero for each file. If the files code non-detects as a small positive number, the
detect counts will come out far above the printed ones, and the result will say so; it will not
be patched.

## What the census already settles

- **S4 fails on creams.** V6's cream rows are still graded on the 15 `Cream` samples by year,
  but 8 + 9 cannot both hold.
- **V4 is gradable:** there is exactly one labelled subset of 74, `Infant Formula - Dairy`.
- **V9's formula row** is graded on the 30 non-soy p13 formulas; with all 39 it is a different
  population.
- **V8's formula share** stays out of V8 as registered (see S6). For the record only: with 39
  formulas, 54% needs exactly 21 detects.
- **V2** needs cucumbers and tomatoes to top every p10 commodity, including small leafy ones
  (arugula 6, chard 8, kale 4, radicchio 1). The census cannot tell whether they do.

## The next step

A grader note fixes the p13 map and publishes `perchlorate_series.py` with offline tests. A sealed
job then waits for that note, reports the p11 date split and the zero coding, and grades V1-V9.

The census records are committed as `data/perchlorate_p10_census.json`,
`data/perchlorate_p11_census.json` and `data/perchlorate_p13_census.json` (labels and counts only).

MV2, Munim, Inc., mv2@munimtech.com
