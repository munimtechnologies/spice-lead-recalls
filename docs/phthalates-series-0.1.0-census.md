# phthalates-series 0.1.0: census note, label maps and size-band amendment (CFIA 2018-19 flatbreads and vegan products; 2012-2018 selected foods)

CENSUS-MARKER: phthalates-series-0.1.0-census

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This note follows the [pre-registration](phthalates-series-0.1.0-prereg.md) (`v0.4.113`). It
reports the names-only census of both open files and fixes the label maps, the coding and one
amendment of the gates **before any result value is read**. It is part of the series indexed at
[cfia-chemistry-surveys-index.md](cfia-chemistry-surveys-index.md). It is not a compliance finding
(Canada has no maximum level for phthalates in food), not about any brand, and not dietary or
medical advice.

## The census run

The sealed job `phthalates-series-census-v1` ran on 2026-11-06 from 12:34 to 12:36 UTC. It first
checked that the pre-registration was public and that its modules equalled the published copies,
then ran the 4 offline tests in `test_phthalates_series_census.py` (all passed), and only then ran
`phthalates_series_census.py`. That module counts labels, units, row shapes and text tokens. It
never prints, sums or compares a numeric result.

## F: 2018-19 flatbreads and vegan products

- **The file.** 149,790 bytes; MD5 equals the portal's (`22dc3074e8e2c55b60fb96a666c5ff16`); UTF-8
  with a byte-order mark; 15 columns; 680 rows; 599 distinct sample IDs. One plan code
  (`2018_SRDEHP`). Eight IDs carry a letter suffix (seven end in `D`, one in `E`); none of them has
  a twin without the suffix.
- **Layout: the same two levels as the 2020-21 file.** Each sample has one `Phthalate Screen` row
  holding a text count with unit `n/a`, and one numeric row in µg/g (= ppm) for each phthalate
  found. Screen tokens: 526 samples read 0, 65 read 1 and 8 read 2. Rows per sample agree: 526
  samples have 1 row, 65 have 2 and 8 have 3 (81 phthalate rows).
- **Phthalate labels** (rows, all numeric, all µg/g): DINP 51, DEHP 24, DBP 4, DIDP 2. There is
  no BBP row and no DNOP row.
- **Products** (8 labels): `Bakery Product - Bread - Other` 119, `Bakery Product -
  Tortilla/Wrap/Pita` 87, `Bakery Product - Bread` 1, `Bakery Product - Bun/Roll` 1;
  `Dairy Alternative` 76, `Mayonnaise - Vegan` 53, `Meat Alternative` 125, `Tofu` 137.
- **Origin** (`Function`): flatbreads 97 domestic / 38 imported / 73 unknown; vegan products 121 /
  156 / 114.
- **Dates.** All 599 parse; the first is 2018-05-14 and the last 2019-01-22. No region field.

### F items, graded

- **F-G as written: FAILED, on the size band alone.** The MD5 matches, there are 599 distinct IDs,
  and every phthalate row is a number under one unit (µg/g); the screen rows are allowed by the
  gate's wording. But 149,790 bytes is below the registered band (150,016-151,040). See A2 below.
- **F-S1 HELD.** The four `Bakery Product` labels make 208 flatbreads (119 + 87 + 1 + 1); the vegan
  labels split 76 / 53 / 125 / 137 = 391.
- **F-S2 HELD, in all six cells.** 97 / 38 / 73 and 121 / 156 / 114. This is the first
  phthalates file in the series whose origin table matches the report exactly.
- **F-S3 HELD.** Every date lies in the 2018-19 survey year and the last is before 21 March
  2019. The file's dates span 14 May 2018 to 22 January 2019, a narrower window than the page's
  "between April 1, 2018 and March 21, 2019".
- **F-S4 FAILED as written.** The file names four phthalates, not six. This follows from the
  layout: a phthalate gets a row only when found, so BBP and DNOP would be absent from the labels
  if they were never detected, which is what the page says ("No other compounds were detected").
  The four labels are all among the six tested.

3 of 5 F census items held, and F-G as written failed.

## P: 2012-2018 selected foods

- **The file.** 1,288,434 bytes; MD5 equals the portal's (`2c80659a91013f3657519375ee33b400`);
  UTF-8 with a byte-order mark; 15 columns; 5,865 rows; 4,517 distinct sample IDs, matching the
  report summary seen in search results. Many IDs carry a letter suffix (55 end in `D`; others end
  in `R`, `E` or `F`).
- **Layout: the same two levels.** Screen tokens: 3,540 samples read 0, 695 read 1, 204 read 2, 67
  read 3 and 11 read 4; rows per sample agree (1,348 phthalate rows).
- **Phthalate labels** (rows, all numeric, all µg/g): DINP 659, DEHP 273, DBP 209, DIDP 199, BBP
  8. There is no DNOP row.
- **Products:** 122 labels. **Dates:** all 4,517 parse, from 2012-04-09 to 2018-02-28; by April-March
  survey year 752 / 736 / 780 / 748 / 751 / 750 (2012-13 to 2017-18). No region field.

### P items, graded

- **P-G as written: FAILED, on the size band alone.** MD5, 4,517 IDs and the phthalate rows all
  hold; 1,288,434 bytes is below the registered band (1,288,704-1,289,728).
- **P-S1 HELD.** All six survey years are present and every date falls inside them.
- **P-S2 FAILED as written.** Five phthalates are named, not six; DNOP has no row (see F-S4).
- **P-S3 FAILED, under both readings.** With the labels mapped as below and survey years taken
  from the sampling date:

| Group (labels) | 2012-13 | 2013-14 | 2014-15 | 2015-16 | Y3 (2012-15) | Y4 (2012-16) | Printed |
|---|---|---|---|---|---|---|---|
| RTE meals (`Meal - RTE`, `Meal - Toddler/Baby`, `Pizza Products`) | 0 | 171 | 66 | 67 | 237 | 304 | 224 |
| Grain products (13 `Bakery Product` labels, `Cereal - Adult`, `Cereal - Children`, `Oatmeal`, `Infant Food - Cereal`) | 99 | 250 | 110 | 110 | **459** | 569 | 460 |
| Nut and seed butters (`Butter - ...` labels, `Tahini`) | 0 | 0 | 100 | 99 | **100** | 199 | 100 |
| Oils (`Oil - ...` labels) | 0 | 65 | 95 | 65 | 160 | 225 | 180 |
| Salad dressings | 0 | 5 | 37 | 37 | 42 | 79 | 22 |
| Mayonnaise | 0 | 0 | 26 | 25 | 26 | 51 | - |
| Vegetable shortening | 0 | 10 | 10 | 11 | 20 | 31 | - |
| Vegetable fats and oils (oils, dressings, mayonnaise, shortening) | 0 | 80 | 168 | 138 | 248 | 386 | 327 |

  Reading Y3 fits the 2018-19 report's two rows: nut and seed butters exactly (88 butters and 12
  tahini, all from 2014-15) and grain products within one sample (459 for 460). Reading Y4 fits
  neither. The 2020-21 report's four 2012-2015 counts (224 meals, 180 oils, 22 dressings, 327 fats
  and oils) fit no combination of survey years: the meal counts by year are 171, 66 and 67, the
  dressing counts 5, 37 and 37, and no sum of them gives 224 or 22. That report cites these rows as
  "unpublished data"; they are not this file's label groups by sampling year.

1 of 3 P census items held, and P-G as written failed.

## Amendment A2 (size band only, fixed before any value is read)

The pre-registration read portal sizes as whole kibibytes **rounded to nearest**. Both files fall
below that band, by 226 and 270 bytes, while both MD5s match. The portal **rounds up**: 149,790
bytes is 146.3 KiB (portal "147"), 1,288,434 is 1,258.2 KiB ("1259"). The two earlier files fit
that rule too (117,529 bytes = 114.8 KiB, "115"; 58,972 = 57.6 KiB, "58"), so rounding up fits all
four files and rounding to nearest fits two. **A2:** each gate's size check becomes "more than
(k - 1) x 1,024 and at most k x 1,024 bytes" for portal size k. Everything else in F-G and P-G stays.
Under A2 both gates pass. Every value grade is made under A2 and labelled so, apart from the
pre-registered gates, which failed as written. (The MD5 alone already identifies each file; the size
check adds nothing to it.)

## The label maps (fixed now)

- **F.** Flatbreads = every label starting `Bakery Product - ` (208). Dairy alternatives = `Dairy
  Alternative`; mayonnaise = `Mayonnaise - Vegan`; meat alternatives = `Meat Alternative`; tofu =
  `Tofu`. Vegan products = those four (391).
- **P, reading Y3 by sampling date** (2012-04-01 to 2015-03-31), the reading that fits the 2018-19
  report: groups as in the table above. `Butter` without a suffix (dairy butter, 170) is not a nut
  butter; `Infant Food - Snack`, `Lard` and `Animal Fat` are in no group. The year in each sample ID
  (for example `C2014...`) is reported alongside, descriptively, because a survey's ID year and its
  sampling dates need not agree.

## Coding (fixed now; as in the 2020-21 grader)

A sample's result is the sum of its phthalate rows; a phthalate with no row counts as zero; a sample
is positive when that sum is above zero. µg/g is ppm. Averages are of positives only. A printed
figure matches within half a unit of its last digit; a share matches when it rounds half up to the
printed whole number.

## What the census already decides (said in advance)

- **F-V2, first part:** 526 samples carry no phthalate row, as the page's 526 says.
- **F-V1, total positives:** 73 samples carry at least one phthalate row, as Table 2's 73 says.
- **F-V3, all of it:** DINP 51 (in 51-56), DEHP 24 (in 21-26), DBP 4, DIDP 2, BBP and DNOP 0, and
  8 samples with two phthalates (at least 5). So the page's "BINP ... 9% of samples" fits DINP
  (51 of 599 = 8.5%), and DEHP's "4% of samples" fits 24 of 599 (4.0%).
- **P-V1, the count:** 977 samples carry a phthalate row (4,517 - 3,540), as the summary says.
- **P-V2 and P-V3 fail on their counts under Y3:** RTE meals 237 (not 224), grain products 459
  (not 460), vegetable fats and oils 248 (not 327), oils 160 (not 180), dressings 42 (not 22). Only
  the nut and seed butters' count (100) holds.

The grader still checks each count against the values, because a stored row could hold zero. These
are not yet known: every group split of the F positives, every minimum, maximum and average, the
sample holding each maximum, the P group positives (167 grain, 59 nut and seed, 128 meals, 8
dressings) and P-V4 (mayonnaise 12% at 2.77; no shortening).

## Next step

The [grader note](phthalates-series-0.1.0-grader.md) publishes `phthalates_series.py` and its
offline tests. The sealed job `phthalates-series-grade-v1` reads values only after this note and the
grader note are public.

MV2, Munim, Inc., mv2@munimtech.com
