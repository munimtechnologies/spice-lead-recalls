# perchlorate-series 0.1.0: result — counts and maxima reproduce; the averages follow two different conventions, and Table 3's formula averages include the soy formulas its counts leave out

RESULT-MARKER: perchlorate-series-0.1.0-result

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This is the result of the [pre-registration](perchlorate-series-0.1.0-prereg.md) (`v0.4.106`),
graded as fixed in the [census note](perchlorate-series-0.1.0-census.md) (`v0.4.108`) and the
[grader note](perchlorate-series-0.1.0-grader.md) (`v0.4.109`). The sealed job
`perchlorate-grade-v1` ran on 2026-11-04 from 23:58 to 00:02 UTC. It first checked that all three
notes were public and that its modules matched the published copies, then ran the 14 offline tests
(all passed), and only then read the values of CFIA's three open perchlorate files: 2010-11 (611
samples), 2011-13 (1,426) and 2013-14 (477). This is a reproducibility check of open government
data. It is not a compliance finding (Health Canada has set no maximum level for perchlorate in
food), not about any brand, and not dietary or medical advice. Values are ppb (ng/g).

The sealed record is [`data/perchlorate_summary.json`](../data/perchlorate_summary.json) and the
per-sample table is [`data/perchlorate_samples.csv`](../data/perchlorate_samples.csv).
[`test_perchlorate_series_result.py`](../test_perchlorate_series_result.py) recomputes every number
below from that table with its own code (it does not import the grader).

## Summary

- **Gate: passed for all three files** (portal size and MD5, every role column, every result a
  number, every unit `ng/g`, no short rows, one row per sample, every label mapped). Every
  non-detect is stored as exactly 0; the smallest stored detect in each file is 2.
- **1 of 9 graded predictions held** (V1). V2 to V9 failed. The graded sample counts, detect
  counts, minima and maxima almost all hold; the exceptions are the 2011-13 formula detects (51,
  not 49) and the 2013-14 group shares (below), besides the 2011 cream count the census note had
  already failed (6 creams dated 2011-12, not 8). Almost every failure is in an **average**.
- **Two averaging conventions.** As registered, averages were of detects only. The 2010-11
  summary's averages are not: counting non-detects as zero (all samples), cucumber gives 48.6,
  tomato 44.9, cheese 5, yogurt 4.9 and soy formula 16.7, exactly as printed. The later CFIA table
  (Table 3 of the 2020-21 dairy and formula report) does use detects only (2010 milk 5.1 and yogurt
  5.1, 2013 cheese 9.0 and yogurt 4.9, 2012 cream 4.0 all reproduce that way). This reading was
  found after grading; it is descriptive and changes no grade.
- **Table 3's formula rows mix two populations, in all three surveys.** The sample count and the
  range are those of the formulas not labelled soy (74, 2-22; 68, 2-33; 30, 2-64), as the census
  note found. The average is that of **all** formulas including soy (10.4, 11.8, 16.5). Non-soy
  averages are 7.7, 9.7 and 15.7.
- **Table 3's 2010 cheese average (5.1) matches nothing tried.** Cheeses average 7.25 over detects
  and 5.04 over all 23 samples. The pre-registered guess that the dairy-wide average was copied
  into each row is refuted: it is 5.55 (detects) or 4.80 (all samples).
- **The 2013-14 group shares cannot be reproduced.** Under the grading map, three of the five
  shares fail (fresh vegetables 92 of 131 = 70.2% against 71%; processed products 53 of 97 = 54.6%
  against 40%; assorted foods 48 of 100 = 48% against 61%). None of the 11 placements that the
  label arithmetic allowed gives the processed share 40% (the closest is 39.2%), so no
  label-based map can save V8.

## Item by item

| ID | What was predicted | Result | What the file shows |
|---|---|---|---|
| V1 | 2010-11 detects 280-283 / 77 / 56; min 2; max 540 | **held** | 283 / 77 / 56; min 2; max 540 (a kale) |
| V2 | 2010-11 cucumber 48.6 and tomato 44.9 top the commodity averages; cheese 5, yogurt 4.9, milk below both; soy formula 16.7 | failed | detect-only averages: cucumber 59.4, tomato 70.6, cheese 7.25, yogurt 5.13, milk 5.08, soy 19.2. Only "milk below both" holds |
| V3 | Table 3 2010 dairy: counts 23 / 42 / 24, maxima 24 / 9 / 12, minima 2; at most one average 5.1; dairy-wide average 5.05-5.15 | failed | counts, maxima and minima hold; milk (5.08) and yogurt (5.13) both give 5.1; dairy-wide 5.55 |
| V4 | Table 3 2010 formula row (74; 2-22; 10.4) is `Infant Formula - Dairy` | failed | 74 samples, 2-22 hold; their average is 7.74 |
| V5 | 2011-13: 637 without; juice 51-52, dairy-based 139-140, formula 49 detects; fruit 44%, vegetables 74%; min 2, max 2400 | failed | all hold except formula: 51 detects of 87, not 49 |
| V6 | Table 3 creams 2011 (3, 6, 4.25-4.35) and 2012 (3, 7, 3.95-4.05); formulas 2, 33, 11.75-11.85 | failed | 2012 creams hold (9 samples, 3-7, 4.0); 2011 creams average 4.6 (6 samples by date, not 8); non-soy formulas 2-33 hold but average 9.70 |
| V7 | 2011-13: cucumber 106, leafy greens 65, tomato 57 are the three highest averages | failed | the top three are cucumber, leafy, tomato as predicted; tomato 56.7 holds, cucumber is 107.2 and the six leafy commodities pooled 59.8 |
| V8 | 2013-14: 205 without; shares 71 / 40 / 80 / 30 / 61; averages 130 / 23 / 5 / 6; min 2; max 3300 (arugula) | failed | 205, dairy 80%, grain 30%, grain 5.2, dairy 6.0, min 2 and the 3300 arugula (C2013PERC00065) hold; shares 70.2 / 54.6 / 48; fresh average 137.1, processed 31.6 |
| V9 | Table 3 2013: cheese 3-42 (9.0), formula 2-64 (16.5), yogurt 2-11 (4.9); 10-16 of 40 dairy detects are cheeses | failed | cheese (20; 3-42; 9.0) and yogurt (30; 2-11; 4.86) hold, 11 of the 40 dairy detects are cheeses; the 30 non-soy formulas run 2-64 but average 15.71 |

## The two averaging conventions (descriptive, not graded)

The pre-registration fixed averages as detect-only and said an all-samples average could be
reported descriptively, "never as a regrade". Here it is.

**2010-11 summary page: all samples, non-detects as zero.**

| Commodity | Samples | Detects | Sum of detects | All-sample average | Printed | Detect-only average |
|---|---|---|---|---|---|---|
| Cucumber | 22 | 18 | 1,069 | 48.59 | 48.6 | 59.39 |
| Tomato (incl. greenhouse) | 55 | 35 | 2,472 | 44.95 | 44.9 | 70.63 |
| Cheese | 23 | 16 | 116 | 5.04 | 5 | 7.25 |
| Yogurt | 24 | 23 | 118 | 4.92 | 4.9 | 5.13 |
| Milk | 42 | 38 | 193 | 4.60 | below both | 5.08 |
| Infant formula, soy | 15 | 13 | 250 | 16.67 | 16.7 | 19.23 |

All six printed figures reproduce under the all-samples reading. The "top two" claim still fails
on any reading: four kale samples, all detected (15, 30, 130 and 540), average 178.75. The summary
may have left kale out for its small count; the file does not say.

**Table 3 of the 2020-21 report: detects only.** Its rows that can be matched reproduce as
detect-only averages: 2010 milk 5.08 (5.1) and yogurt 5.13 (5.1); 2013 cheese 9.0 and yogurt 4.86
(4.9); 2012 cream 4.0. So two CFIA documents describing the same 2010-11 samples use different
averages: the 2010-11 summary gives yogurt 4.9, Table 3 gives 5.1, and both are right under their
own convention. Neither document says which it uses.

## Table 3's formula rows (descriptive, not graded)

| Survey | Table 3 row | Non-soy formulas in the file | All formulas in the file |
|---|---|---|---|
| 2010-11 | 74; 2-22; 10.4 | 74; 43 detects; 2-22; **7.74** | 89; 56 detects; 2-50; **10.41** |
| 2011-13 | 68; 2-33; 11.8 | 68; 37 detects; 2-33; **9.70** | 87; 51 detects; 2-35; **11.84** |
| 2013-14 | 30; 2-64; 16.5 | 30; 14 detects; 2-64; **15.71** | 39; 21 detects; 2-64; **16.52** |

In every survey the count and the range fit the non-soy formulas and the average fits all
formulas. In 2010-11 and 2011-13 the range also excludes the soy maximum (50 and 35). A row that
mixes the two populations is not a reading of the file that any single subset gives. The census
note had already shown that the counts leave out soy; this result shows the averages do not.

## The 2013-14 shares (descriptive, not graded)

The grader note fixed the six-group map from label counts and the printed shares alone, and said
that under it each share allowed exactly one detect count (93 / 39 / 40 / 21 / 18 / 61). The file
gives 92 / 53 / 40 / 21 / 18 / 48, which still sums to 272. The block counts behind that:

| Block | Samples | Detects |
|---|---|---|
| Dried fruit (six labels) and potato products | 46 | 19 |
| Dried vegetables | 17 | 12 |
| Mixed vegetables | 10 | 9 |
| Soup | 15 | 4 |
| Salsa | 9 | 9 |
| Juices, nectars and fruit drinks | 47 | 12 |
| `Beverage - Other` | 3 | 2 |
| Pizza products | 20 | 17 |

The grade job also listed all 11 placements of the eight movable blocks that the label arithmetic
allowed. Across those 11 the processed group's share ranges from 39.2% to 59.8%, and none rounds to
40%. With the juices among processed products (the placement the grader note ruled out), processed
is 65 of 144 (45.1%) and assorted 36 of 53 (67.9%). So the 2013-14 summary's six groups are not any
grouping of this file's labels that was tried; its fresh-vegetable average (130 against 137.1) and
processed average (23 against 31.6) point the same way.

## Limits

- The averaging readings are found after grading and are descriptive. They explain the printed
  figures; they do not prove how CFIA computed them.
- Table 3's 2011 cream row (8 samples) does not match the file's 6 creams dated in 2011-12. Survey
  years come from the sampling-date column, as registered; the file has no other year field.
- The leafy-greens pool (six commodities, 342 samples) is this series' choice, not CFIA's; the
  report's 65 may pool a different set.
- The 2013-14 report's group sizes are not printed, so the share failure may be a grouping that no
  label in the file reveals.

## Next

A sealed job (`perchlorate-result-v1`) downloads this note, its data tables and the independent test
from GitHub and runs the test, so the published result is re-checked from what is public.

MV2, Munim, Inc., mv2@munimtech.com
