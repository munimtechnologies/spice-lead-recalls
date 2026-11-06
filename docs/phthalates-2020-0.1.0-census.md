# phthalates-2020 0.1.0: census note, label map and format amendment (CFIA 2020-21 phthalates file)

CENSUS-MARKER: phthalates-2020-0.1.0-census

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This note follows the [pre-registration](phthalates-2020-0.1.0-prereg.md). It reports the
names-only census of CFIA's open 2020-21 phthalates file and fixes the label map, the coding and a
format-only amendment of the gate **before any result value is read**. It is part of the series
indexed at [cfia-chemistry-surveys-index.md](cfia-chemistry-surveys-index.md). It is not a
compliance finding (Canada has no maximum level for phthalates in food), not about any brand, and
not dietary or medical advice.

## The census run

The sealed job `phthalates-census-v1` ran on 2026-11-05 from 19:40 to 19:41 UTC. It first checked
that the pre-registration was public and that its modules equalled the published copies, then
ran the 6 offline tests in `test_phthalates_census.py` (all passed), and only then ran
`phthalates_census.py`. That module counts labels, units, row shapes and text tokens. It never
prints, sums or compares a numeric result.

## What the census found

- **The file.** 117,529 bytes; its MD5 equals the portal's (`612780be14a4a571044d93aaa27f99f2`);
  UTF-8 with a byte-order mark; 15 columns; 548 rows; 500 sample IDs, `C2020PHTH00001` to
  `C2020PHTH00500` with no gaps and no repeats. One plan code (`2020_SRDEHP`).
- **Layout: long, two levels.** Every sample has one `Phthalate Screen` row whose result is a
  text count, such as `0 Phthalates detected / Phtalate détecté`, with unit `n/a`. A sample also
  has one row for each phthalate found in it, with a numeric result in µg/g (= ppm). There are no
  non-detect rows for single phthalates: a phthalate that was not found has no row.
- **Screen tokens.** 464 samples read `0 Phthalates detected`, 29 read 1, 5 read 2, 1 reads 4 and 1
  reads 5. The rows per sample agree in distribution: 464 samples have 1 row, 29 have 2, 5 have
  3, 1 has 5 and 1 has 6. That is 48 phthalate rows (29 + 10 + 4 + 5).
- **Phthalate labels** (rows, all numeric, all µg/g): DEHP (`Bis(2-ethylhexyl) phthalate`) 23,
  DBP (`Dibutylphthalate`) 9, DINP 8, DIDP 5, DNOP 2, BBP 1.
- **Products** (22 labels): Meal - RTE 79, Meal - Toddler/Baby 53, Pizza Products 50, Soup 45,
  Infant Food - Puree 23; Salad Dressing 50, Vegetable Shortening 48, Mayonnaise 2; and 14 oil
  labels: Peanut 17, Sunflower 17, Canola 16, Olive 16, Corn 15, Palm 15, Sesame 15, Soybean 14,
  Blend 12, Coconut 5, Vegetable 3, Flax 2, Grapeseed 2, Avocado 1.
- **Origin.** A `Function` column (Domestic / Import / Unknown) and an `Origin` country column.
- **No region column.** The file has no region field at all.
- **Dates.** All 500 sampling dates parse; the first is 2020-06-01 and the last 2021-03-10.

## The label map (fixed now)

- **Ready-to-eat meals (250):** Meal - RTE, Meal - Toddler/Baby, Pizza Products, Soup and
  `Infant Food - Puree` (79 + 53 + 50 + 45 + 23 = 250).
- **Vegetable fats and oils (250):** oils = every label starting `Oil - ` (150); salad dressings =
  `Salad Dressing` (50); shortening = `Vegetable Shortening` (48); mayonnaise = `Mayonnaise` (2).
  No label says vegan mayonnaise.
- **Origin** = the `Function` column (Domestic, Import, Unknown), read as the report's domestic,
  imported and unspecified.
- **Children's label** = `Meal - Toddler/Baby`.

## Census items, graded

- **G (gate) as written: FAILED.** Three of its parts hold: the MD5 matches, the size is in the
  113,000-118,000 band, and there are 500 distinct sample IDs. Two do not. 36 result cells are
  detection counts (`1 Phthalate detected` and so on), which are neither numbers nor non-detect
  tokens. And the file has two unit labels, `n/a` (the 500 screen rows) and `µg/g` (all 48
  phthalate rows). The prediction did not foresee a screen row. The gate is not edited.
- **S1 HELD.** 250 ready-to-eat meals and 250 vegetable fats and oils.
- **S2 HELD.** 150 oils, 50 salad dressings, and 50 shortenings and mayonnaises (48 + 2).
- **S3 FAILED.** Ready-to-eat meals: 56 domestic / 166 imported / 28 unknown in the file, against
  the printed 56 / 165 / 29. Vegetable fats and oils: 28 / 159 / 63 against 27 / 161 / 62. Totals
  84 / 325 / 91 against 83 / 326 / 91. The country column gives the same domestic counts (56 and 28
  samples from Canada). So Table 1 is off by one sample in ready-to-eat meals and by one or two
  in each fats-and-oils cell, while every group total matches.
- **S4 FAILED as written.** There is no region field, so the four region labels cannot exist. The
  date part holds: every date falls between 2020-04-01 and 2021-03-31.
- **S5 HELD.** The phthalate labels are exactly the six registered (BBP, DBP, DNOP, DEHP, DINP,
  DIDP), written out in full. The seventh label, `Phthalate Screen`, is a per-sample count, not a
  phthalate.

3 of 5 census items held, and the gate as written failed.

## Amendment A1 (format only, fixed before any value is read)

The value items V1-V5 are graded under one format-only amendment, reported apart from the
pre-registered grades. **A1:** G's cell and unit checks apply to the six phthalate rows only (each
must be a number in µg/g), and each screen row must be a count token of the form `N
Phthalate(s) detected`. The MD5, size band and 500-sample checks stay. Every grade made under A1
is labelled as such in the result. In the series' terms this is the kind of format-only fix the
index allows: it is published here as a separate amendment, before the values are read.

## Coding (fixed now)

- A sample's result is the sum of its phthalate rows; a missing phthalate counts as zero. It is
  positive when that sum is above zero. µg/g is ppm, so no unit conversion is made.
- Averages are of positives only. A printed figure matches within half a unit of its last digit;
  a share matches when it rounds half up to the printed whole number.
- The screen count is checked against the number of phthalate rows and the number above zero; any
  sample where they disagree is listed.

## What the census already decides (said in advance)

The census reads labels, not values, but the screen tokens and row counts already show most of
the counting claims. These are not blind any more:

- 464 samples carry no phthalate row, as the report's 464 says (V2, first part).
- 36 samples carry at least one phthalate row, as Table 2's 36 positives say (V1, total row).
- DEHP has 23 rows, the other five 1 to 9 each, and 7 samples have two or more rows (V3).

The grader still checks each against the values, because a stored row could hold zero. These
parts are not yet known from the census: the split of the 36 between meals and fats and oils, the
29 oils and 2 dressings, every minimum, maximum and average, and which sample holds the maximum.

**V2's hot-dog part cannot be graded.** The product labels are categories only. V2 is graded on:
464 samples without phthalates, and a single largest result that matches 4.2 and sits in a
ready-to-eat meal labelled `Meal - Toddler/Baby`. If the largest result is labelled `Meal - RTE`
or anything else, V2 fails.

## For CFIA's open-data team (already from the census)

Table 1's origin cells do not match the file by one or two samples in each group, although every
group total does. The file has no region field, while the report describes sampling in four
regions.

## Next step

The [grader note](phthalates-2020-0.1.0-grader.md) publishes `phthalates_2020.py` and its offline
tests. The sealed job `phthalates-grade-v1` reads values only after this note and the grader note
are public.

MV2, Munim, Inc., mv2@munimtech.com
