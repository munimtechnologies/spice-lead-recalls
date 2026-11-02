# perchlorate-series 0.1.0: pre-registration — CFIA's three open perchlorate files (2010-11, 2011-13, 2013-14) against their reports and a later CFIA comparison table

PREREG-MARKER: perchlorate-series-0.1.0-prereg

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.
Written on 2026-11-02, before any of the three open files was opened. Everything below comes from
the three report pages, a later CFIA report and the portal records (size, hash and description).

This is a reproducibility check of open government data. It is not a compliance finding (Health
Canada has set no maximum level for perchlorate in food), it is not about any brand, and it is not
dietary or medical advice. All values are ppb.

## Sources

- **p10:** "2010-2011 Perchlorate in Fresh Fruits and Vegetables, Dairy Products and Infant
  Formulae" (CFIA summary page; the full report is available on request only). Open dataset
  `436bec6d-f410-45cc-89ff-f5331cfa663c`, resource `46630289-3b83-4392-b648-da594e5357ce`, portal
  size 95,033 bytes, MD5 `f497970ea94e7d4eaf74fdabb9535bca`.
- **p11:** "2011-2013 Perchlorate in Fresh Fruits and Vegetables, Fruit and Vegetable Juice,
  Dairy-Based Products and Infant Formulas" (summary page; full report on request). Dataset
  `0bdaecc5-805e-4f42-a182-338870635221`, resource `beccac79-f18e-4270-9c2c-c6ce645fc2b4`, 228,127
  bytes, MD5 `66a04ce98555c6898c18ebaefc042a96`.
- **p13:** "2013-2014 Perchlorate in Selected Foods" (summary page; full report on request).
  Dataset `79e83e09-be72-4cec-b410-1e69aaa450f7`, resource `7511b1a3-48c7-4386-ae6e-f2c4e87c6e84`,
  78,310 bytes, MD5 `05b587cb13f15932894200ba5879445a`.
- **Table 3** of CFIA's "Perchlorate in Dairy Products and Infant Formula - April 1, 2020 to March
  31, 2021". It compares the 2020-21 survey with ten rows from the three earlier surveys, which it
  cites as "[unpublished data]". All three files have been on open.canada.ca since 2023. Averages
  in that report "use only positive results".

Table 3's earlier rows (samples, minimum, maximum, average):

| Product | Survey | Samples | Min | Max | Average |
|---|---|---|---|---|---|
| Cheese | 2013 (p13) | 20 | 3 | 42 | 9.0 |
| Cheese | 2010 (p10) | 23 | 2 | 24 | 5.1 |
| Cream | 2012 (p11, second year) | 9 | 3 | 7 | 4.0 |
| Cream | 2011 (p11, first year) | 8 | 3 | 6 | 4.3 |
| Infant formula | 2013 (p13) | 30 | 2 | 64 | 16.5 |
| Infant formula | 2011 (p11, first year) | 68 | 2 | 33 | 11.8 |
| Infant formula | 2010 (p10) | 74 | 2 | 22 | 10.4 |
| Milk | 2010 (p10) | 42 | 2 | 9 | 5.1 |
| Yogurt | 2013 (p13) | 30 | 2 | 11 | 4.9 |
| Yogurt | 2010 (p10) | 24 | 2 | 12 | 5.1 |

## What the printed figures already show (no file needed)

- **R1. Table 3's three 2010 dairy averages cannot all be right.** It gives cheese, milk and
  yogurt the same 5.1. The 2010-11 report gives yogurt 4.9, and names cheese (5) and yogurt (4.9)
  as the dairy products with the highest averages, which puts milk below 4.9. A single dairy-wide
  average copied into each row would produce three equal values.
- **R2. Table 3's 2010 formula row has 74 samples; the 2010-11 report has 89 formulas.** Its dairy
  rows (23 + 42 + 24 = 89) do match the report's 89 dairy products.
- **R3. 2013-14's "54% of infant formula" is impossible with Table 3's 30 formulas:** 16 of 30 is
  53% and 17 of 30 is 57%.
- **R4. 2013-14 dairy is consistent only in a narrow band.** Cheese 20 + yogurt 30 = 50 and 80% of
  50 is 40 detects. With Table 3's averages (9.0 and 4.9) and the report's dairy average of 6
  (5.5-6.5), 40 detects need 6-16 cheese detects (194 + 4.1c <= 260 and 198 + 4.1c >= 220), and
  since yogurt has only 30 samples, 10-16.
- **R5. Counts implied by the percentages.** p10: 65% of 433 fruits and vegetables = 280-283; 87%
  of 89 dairy = 77; 63% of 89 formulas = 56. p11: 1426 = 881 + 225 + 233 + 87 = 663 + 763; 637 with
  no perchlorate (45%) leaves 789 detects; 23% of 225 juices = 51 or 52; 60% of 233 dairy-based
  products = 139 or 140; 56% of 87 formulas = 49; so fresh fruit and vegetables hold 548-550
  detects. p13: 477 samples, 205 without perchlorate (43%), 272 detects.
- **R6.** Table 3 has no 2011 or 2012 cheese, milk or yogurt row, although p11 tested 233
  dairy-based products. Its 2011 formula row has 68 samples of p11's 87.

## Census predictions (labels, dates, counts and cell shapes only; no value read)

| ID | Prediction |
|---|---|
| G | each file matches its portal size and MD5; one perchlorate result per sample; samples 611 (p10), 1426 (p11), 477 (p13) |
| S1 | p10 product groups 433 fresh fruits and vegetables / 89 dairy / 89 infant formulas, with dairy split cheese 23 / milk 42 / yogurt 24 (Table 3) |
| S2 | p10 fresh fruit and vegetables by origin 146 domestic / 285 imported / 2 unknown. *Secondary source:* this split is attributed to the full CFIA report by a 2017 review (Environmental Monitoring and Assessment, doi 10.1007/s10661-017-5793-x) that was seen only in a search excerpt; graded, but weighted as such |
| S3 | p11 groups 881 fresh fruits and vegetables / 225 juices / 233 dairy-based products / 87 infant formulas; by sampling date 663 from April 2011 to March 2012 and 763 from April 2012 to March 2013 |
| S4 | p11 first year (April 2011 - March 2012) holds 68 of the 87 formulas; creams are 8 in the first year and 9 in the second (Table 3) |
| S5 | p13 has 20 cheeses, 30 yogurts and 30 infant formulas (Table 3), and its dairy group is those 50 |
| S6 | so the 2013-14 formula share cannot be 54% (R3): the census count of p13 formulas admits no detect count that rounds to 54% |

Label maps (fresh fruit vs fresh vegetable, leafy greens, the six 2013-14 groups, soy-based
formula) are fixed in the census note before any value is read, as for the earlier series.

## Value predictions (graded by a sealed job after the census note fixes maps and coding)

| ID | Prediction |
|---|---|
| V1 | p10: detects 280-283 fruits and vegetables, 77 dairy, 56 formulas; minimum detect rounds to 2, maximum 540 |
| V2 | p10 averages of positives: cucumbers 48.6 and tomatoes 44.9 are the two highest fruit-and-vegetable commodity averages; cheese rounds to 5 and yogurt to 4.9, both above milk; soy-based formula 16.7 |
| V3 | Table 3's 2010 dairy rows: counts 23 / 42 / 24 and maxima 24 / 9 / 12 hold and every minimum rounds to 2; at most one of the three averages is within 5.05-5.15, and the dairy-wide average of positives is 5.05-5.15 (R1: the shared 5.1 is the dairy-wide figure) |
| V4 | Table 3's 2010 formula row (74; 2-22; 10.4) does not describe all 89 formulas. If the census note finds exactly one labelled subset of 74 (for example all but the soy-based), that subset reproduces minimum 2, maximum 22 and average 10.35-10.45 |
| V5 | p11: 637 samples without perchlorate; detects 51-52 juices, 139-140 dairy-based, 49 formulas; fresh fruit 44% and fresh vegetables 74% of their census counts; minimum detect rounds to 2, maximum 2400 |
| V6 | Table 3's p11 rows: creams 2011 (minimum 3, maximum 6, average 4.25-4.35) and 2012 (3, 7, 3.95-4.05); formulas 2011 (2, 33, 11.75-11.85) |
| V7 | p11 commodity averages of positives: cucumbers 106, leafy green vegetables 65 and tomatoes 57 are the three highest |
| V8 | p13: 205 without perchlorate; detect shares fresh vegetables 71%, processed fruit/vegetable 40%, dairy 80%, grain 30%, assorted 61% (formula: see S6); averages of positives fresh vegetables 130, processed 23, grain 5, dairy 6; minimum rounds to 2; the maximum is 3300 and its label names arugula |
| V9 | Table 3's p13 rows: cheese (3, 42, 8.95-9.05), formula (2, 64, 16.45-16.55), yogurt (2, 11, 4.85-4.95); and 10-16 of the 40 dairy detects are cheeses (R4) |

## Coding (fixed now; the census note may only add label maps)

- A sample is a *detect* when its perchlorate result is above zero, or is a number where
  non-detects are written as text (`ND`, `<LOD` and the like). If a file codes non-detects as a
  number at or below some limit, the census note says so before any value is read, and that rule
  applies.
- One result per sample; if a sample has more than one perchlorate row, its largest value counts
  and the census note reports it.
- Averages are of positive results only (the 2020-21 report's stated rule), for all three
  reports. If a summary average fails under that rule, the result may report the all-samples
  average as a description, never as a regrade.
- A printed figure matches when the file's value is within half a unit of its last printed digit
  ("5" covers 4.5-5.5; "4.9" covers 4.85-4.95). A percentage matches when it rounds to the printed
  whole number.
- Survey years run April to March. A file's year split uses its sampling-date column.

## Limits

- All three reports are summaries; their tables are available only on request, so the per-product
  counts tested here come from Table 3 of the 2020-21 report, from percentages and from one
  secondary source (S2).
- Neither summary states a limit of detection. All printed minima are 2 or 3.
- Labels may be too coarse for some items (leafy greens, soy-based formula, arugula). An item that
  the labels cannot settle is reported as ungraded, never inferred.

## The next step

A sealed job (`perchlorate-census-v1`) waits until this note is public, checks that its modules
match the published copies, runs the offline tests in `test_perchlorate_census.py`, and only then
runs `perchlorate_census.py`: labels, units, cell shapes, sample counts and sampling-year counts per
product label, never a value. The census note then grades G and S1-S6 and fixes the label maps and
the grader before any value is read.

Prior art: searches on 2026-11-02 found the three CFIA summary pages, the open dataset records,
the 2020-21 report and literature reviews that cite the 2010-11 summary, but no analysis of any of
the three per-sample files and no check of Table 3's earlier rows.

MV2, Munim, Inc., mv2@munimtech.com
