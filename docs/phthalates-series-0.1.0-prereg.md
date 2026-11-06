# phthalates-series 0.1.0: pre-registration — CFIA's 2018-19 flatbread and vegan phthalates survey, and the 2012-2015 rows two later CFIA reports print, against the open files

PREREG-MARKER: phthalates-series-0.1.0-prereg

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

Written on 2026-11-06, **before any part of either open file has been opened** (not a header, not
a row). This is a reproducibility check of open government data, in the series indexed at
[cfia-chemistry-surveys-index.md](cfia-chemistry-surveys-index.md). It is not a compliance finding
(Canada has set no maximum level for phthalates in food, and Health Canada found every detected
level safe), not about any brand, and not dietary or medical advice.

## The files

- **F (2018-19).** open.canada.ca dataset `c4202b90-03d1-4eef-9fcc-0740066fc0c4` ("Phthalates in
  Flatbread and Vegan Products - 2018-2019"), resource `8ce9082f-b339-4e5d-b74a-fa1747d295ac`
  (CSV), portal size "147", portal MD5 `22dc3074e8e2c55b60fb96a666c5ff16`, published 2026-02-19.
- **P (2012-2018).** dataset `ea25d8e4-180c-4f7c-a912-f37381168664` ("Food Safety Action Plan
  Targeted Survey - Phthalates 2012 to 2018", "the data reported in the report Phthalates in
  selected foods - April 1, 2012, to March 31, 2018"), resource
  `072329d5-0f9c-4e3f-aae1-c4996ae2b5d5` (CSV), portal size "1259", portal MD5
  `2c80659a91013f3657519375ee33b400`, file last modified 2026-03-25.

Both are under the Open Government Licence - Canada. Portal sizes are read as kibibytes rounded to
a whole number: the 2020-21 phthalates file (portal "115") has 117,529 bytes = 114.8 KiB, and the
2019-20 ethyl carbamate file (portal "58") has 58,972 bytes = 57.6 KiB. So F should have
150,016-151,040 bytes and P 1,288,704-1,289,728 bytes.

## What the reports say

**F's report**: ["Phthalates in Flatbread and Vegan Products - April 1, 2018 to March 31, 2019"](https://inspection.canada.ca/en/food-safety-industry/food-chemistry-and-microbiology/food-safety-testing-reports-and-journal-articles/phthalates-flatbread-and-vegan-products)
(page modified 2022-10-05):

- Six phthalates tested: BBP, DBP, DNOP, DEHP, DINP and DIDP. Samples from retail in Halifax,
  Montreal, Toronto, Ottawa, Vancouver and Calgary, "sampled between April 1, 2018 and March 21,
  2019". Averages use positive results only.
- Table 1 (origin, domestic / imported / unspecified): flatbreads 97 / 38 / 73 = 208; vegan
  products 121 / 156 / 114 = 391; total 218 / 194 / 187 = 599.
- Table 2 (samples, positives (%), min, max, average, ppm): flatbreads 208, 54 (26), 0.57, 15.00,
  2.70; vegan products 391, 19 (5), 0.50, 24.00, 3.61; of which dairy alternative 76, 6 (8), 0.59,
  2.78, 1.17; mayonnaise 53, 3 (6), 0.72, 3.19, 1.64; meat alternative 125, 7 (6), 0.50, 7.57,
  3.45; tofu 137, 3 (2), 0.54, 24.00, 10.85; total 599, 73 (12), 0.50, 24.00, 2.94.
- Text: 526 (88%) had no detectable phthalates; "BINP was the most commonly detected phthalate,
  found in 9% of samples"; "DEHP was the second most frequently detected phthalate (4% of
  samples)"; "BDP and DIDP were only found in 4 and 2 samples, respectively"; "No other compounds
  were detected".
- Table 3 prints two rows for "2012-15": grain products 460, 167 (36), 0.27, 23.3, 1.60; nut/seed
  butters 100, 59 (59), 0.5, 315, 17.2.

**The 2020-21 report**, ["Phthalates in ready-to-eat meals, vegetable fats and oils"](https://inspection.canada.ca/en/food-safety-industry/food-chemistry-and-microbiology/testing-reports-and-journal-articles/2020-2021-phthalates),
Table 3, "2012 to 2015" rows (samples, min, max, average; cited as "unpublished data"): RTE meals
224, 0.27, 15.4, 1.46; vegetable fats and oils 327, 0.26, 2608, 84.3; oil 180, 0.26, 2608, 107;
salad dressing 22, 0.71, 3.75, 2.25. Text: RTE detection "57.1% in the 2012 to 2015 survey years";
salad dressings 36% positive; "12% of mayonnaise samples" positive, average 2.77 ppm; "no samples of
vegetable shortening tested in 2012 to 2015 had detectable levels".

**P's own report** is on open-science.canada.ca, which these agents cannot load. Its summary as
shown in web-search results (not read directly, so used only for P-G's sample count): 4,517
samples, 3,540 (78%) without detectable phthalates, totals from 0.26 to 2,608 ppm.

## What the reports' own arithmetic already says (R)

- **R1.** F's Table 2 shares all round correctly (54/208 = 26.0%, 19/391 = 4.9%, 6/76 = 7.9%,
  3/53 = 5.7%, 7/125 = 5.6%, 3/137 = 2.2%, 73/599 = 12.2%); the vegan rows add up (76 + 53 + 125 +
  137 = 391; 6 + 3 + 7 + 3 = 19); 526 + 73 = 599.
- **R2.** F's averages are consistent: vegan (6 x 1.17 + 3 x 1.64 + 7 x 3.45 + 3 x 10.85) / 19 =
  68.64 / 19 = 3.613 (printed 3.61); total (54 x 2.70 + 68.64) / 73 = 2.938 (printed 2.94).
- **R3.** Three-positive rows are pinned: tofu's positives are 0.54, 24.00 and 3 x 10.85 - 24.54 =
  8.01 (7.985-8.035 with rounding); mayonnaise's are 0.72, 3.19 and 4.92 - 3.91 = 1.01
  (0.985-1.035).
- **R4.** Text slips on F's page, independent of the file: "A total of 599 domestic and imported
  flatbreads and 391 vegan products" (Table 1: 208 flatbreads, 599 in all); "BINP" and "BDP" are not
  among the six tested (read here as DINP and DBP); "0.006 milligram per liter (0.6 ppb)" is 6 ppb
  (the 2020-21 page repeats the same slip). The sampling end (March 21) inside a survey period
  ending March 31 is not a slip.
- **R5.** If "9% of samples" and "4% of samples" are of all 599, DINP is in 51-56 samples and DEHP
  in 21-26; with DBP 4 and DIDP 2 that is at least 78 detections in 73 positive samples, so at least
  5 samples hold more than one phthalate.
- **R6.** The 2012-15 detection rates pin counts: 57.1% of 224 RTE meals can only be 128; 36% of
  22 salad dressings can only be 8.

## Predictions

Coding as in the 2020-21 grader: a sample's result is the sum of its phthalate results; a phthalate
with no row, or a non-detect token, counts as zero; a sample is positive when the sum is above zero;
averages are of positives only. A printed figure matches within half a unit of its last digit; a
share matches when it rounds half up to the printed number. The unit, any per-sample screen row and
any non-detect coding are fixed in the census note before values are read.

**Census items (labels, shapes and counts only):**

- **F-G.** MD5 equals the portal's; 150,016-151,040 bytes; 599 distinct sample IDs; every result
  cell of a phthalate row is a number or a non-detect token, under one unit label. A per-sample
  screen or summary row with a text result is allowed and is not a phthalate row.
- **F-S1.** Product labels split 208 flatbreads / 391 vegan products, and the vegan labels split
  76 dairy alternatives / 53 mayonnaises / 125 meat alternatives / 137 tofu (map fixed in the
  census note from the labels).
- **F-S2.** If the file has an origin field: 97 / 38 / 73 and 121 / 156 / 114.
- **F-S3.** Every sampling date from 2018-04-01 to 2019-03-31, the last on or before 2019-03-21.
- **F-S4.** The phthalate labels are exactly the six tested.
- **P-G.** MD5 equals the portal's; 1,288,704-1,289,728 bytes; 4,517 distinct sample IDs; result
  cells of phthalate rows as in F-G.
- **P-S1.** Sampling dates fall in the six survey years 2012-13 to 2017-18, each present, none
  before 2012-04-01 or after 2018-03-31.
- **P-S2.** The phthalate labels are the same six.
- **P-S3.** "2012 to 2015" means the survey years 2012-13, 2013-14 and 2014-15 (reading Y3). Under
  Y3 the product labels can be mapped to RTE meals 224, grain products 460, nut/seed butters 100,
  and vegetable fats and oils 327 (oils 180, salad dressings 22). Reading Y4 (adding 2015-16) is
  checked too; exactly one reading should fit. The map is fixed in the census note from the labels.

**Value items (read only after the census note and the grader are public):**

- **F-V1.** F's Table 2 in full (all seven rows above).
- **F-V2.** 526 samples without phthalates; the largest result, 24.00, is a tofu.
- **F-V3.** Under the all-599 reading: DINP above zero in 51-56 samples, DEHP in 21-26, DBP in 4,
  DIDP in 2, BBP and DNOP in none; at least 5 samples with more than one phthalate.
- **F-V4.** R3: tofu's positives 0.54, about 8.01 and 24.00; mayonnaise's 0.72, about 1.01 and
  3.19.
- **P-V1.** Whole file: 977 positive samples (4,517 - 3,540), totals from 0.26 to 2,608.
- **P-V2.** Under the census-note reading of "2012 to 2015": grain products 460 / 167 / 0.27 /
  23.3 / 1.60; nut/seed butters 100 / 59 / 0.5 / 315 / 17.2; RTE meals 224 / 128 / 0.27 / 15.4 /
  1.46.
- **P-V3.** Same years: vegetable fats and oils 327 / 0.26 / 2,608 / 84.3; oils 180 / 0.26 / 2,608
  / 107; salad dressings 22 / 8 / 0.71 / 3.75 / 2.25.
- **P-V4.** Same years: mayonnaise 12% positive (half-up rounding) with average 2.77; no shortening
  positive.

Also reported, not graded: per-phthalate counts and ranges in both files, the five smallest stored
detects (a scale slip would show there), identical non-zero totals, and, for P, every product
group per survey year. A later CFIA table restating only part of a group (the pattern found in the
perchlorate series) is tested on labelled subsets before any figure is called wrong.

## Said in advance

If either file has the 2020-21 layout (a screen row per sample holding a text count, plus one row
per phthalate found), the census's own counts of screen tokens and phthalate rows already decide
F-V2's 526, most of F-V3, and P-V1's positive count. The census note will say which items it has
decided before any value is read.

## Limits

P's report could not be read; P's predictions rest on tables in two later reports and on a search
summary. If labels cannot separate a group (grain products from other baked goods, mayonnaise from
dressings), the affected items are ungraded, never guessed.

## Next step

The sealed job `phthalates-series-census-v1` waits until this note is public, makes its modules
equal the published copies, runs the offline tests in `test_phthalates_series_census.py`, and only
then runs `phthalates_series_census.py`, which reads labels, shapes and counts but no result value.
A census note with the label maps and a grader follows before any value is read.

MV2, Munim, Inc., mv2@munimtech.com
