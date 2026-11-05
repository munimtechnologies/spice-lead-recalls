# phthalates-2020 0.1.0: pre-registration — CFIA's 2020-21 phthalates survey (ready-to-eat meals, vegetable fats and oils) against its open file

PREREG-MARKER: phthalates-2020-0.1.0-prereg

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

Written on 2026-11-05, **before any part of the open file has been opened** (not its header, not a
row). Every figure below comes from CFIA's report page
["Phthalates in ready-to-eat meals, vegetable fats and oils"](https://inspection.canada.ca/en/food-safety-industry/food-chemistry-and-microbiology/testing-reports-and-journal-articles/2020-2021-phthalates)
(page last modified 2024-11-25) and from the open.canada.ca record of the file. This is a
reproducibility check of open government data, in the series indexed at
[cfia-chemistry-surveys-index.md](cfia-chemistry-surveys-index.md). It is not a compliance finding
(Canada has set no maximum level for phthalates in food, and Health Canada found every detected
level safe), not about any brand, and not dietary or medical advice.

## The file

open.canada.ca dataset `4ae4c2b3-e1b7-451a-b313-02e51d73da73` ("Phthalates in ready-to-eat
meals, vegetable fats and oils - 2020-2021"), resource `960252a3-4b35-44ef-9e8d-46ed1b0dd61c`
(CSV), portal size "115", portal MD5 `612780be14a4a571044d93aaa27f99f2`, Open Government Licence -
Canada. The portal size is read as kilobytes (other CFIA records give kB, not bytes).

## What the report says

- 500 samples, sampled at retail from 1 April 2020 to 31 March 2021 in six cities in four regions
  (Atlantic, Quebec, Ontario, West): 250 ready-to-eat (RTE) meals (infant, children's and adult
  meals, pizza products) and 250 vegetable fats and oils (oils, salad dressings, vegetable
  shortenings, mayonnaise and vegan mayonnaise).
- Six phthalates: BBP, DBP, DNOP, DEHP, DINP and DIDP. Results are the sum of the phthalates
  detected in a sample, in ppm.
- Table 1 (origin): RTE meals 56 domestic / 165 imported / 29 unspecified; vegetable fats and oils
  27 / 161 / 62; total 83 / 326 / 91.
- Table 2: RTE meals 250 samples, 5 positive (2%), 0.3-4.2 ppm, average 1.56; vegetable fats and
  oils 250, 31 (12%), 0.2-3.4, 0.86; total 500, 36 (7%), 0.2-4.2, 0.96.
- Text: 464 of 500 (93%) had none; the highest, 4.2 ppm, was an RTE hot dog meal for children;
  DEHP was found in 23 samples (4.6%); each other phthalate in 1 to 9 samples; 7 samples had more
  than one phthalate; in 2020 no mayonnaise had phthalates; vegetable shortening had none; salad
  dressings fell from 36% to 4% positive.
- Table 3 (footnote: "Only positive results were used to calculate the average"): 2020 oil 150
  samples, 0.2-3.4, 0.89; 2020 salad dressing 50 samples, 0.3-0.6, 0.45. Its 2012-2015 rows
  (unpublished data) are not checked here.

## What the report's own arithmetic already says (R)

- **R1.** Table 2 is internally consistent: 5/250 = 2%, 31/250 = 12.4%, 36/500 = 7.2%, and the
  positives' weighted average (5 x 1.56 + 31 x 0.86) / 36 = 0.957 gives 0.96. 464 + 36 = 500.
- **R2.** The fats-and-oils split is pinned by the text. Salad dressings at 4% of 50 is exactly
  2 positives; with no positive mayonnaise or shortening, oils carry the other 29 (19.3% of 150).
  Then (29 x 0.89 + 2 x 0.45) / 31 = 0.862, which gives Table 2's 0.86. Two positives with
  minimum 0.3, maximum 0.6 and average 0.45 must be exactly 0.3 and 0.6.
- **R3.** The five RTE positives sum to 5 x 1.56 = 7.8 ppm (7.775-7.825 with rounding); with 0.3
  and 4.2 among them, the other three sum to about 3.3.
- **R4.** DEHP's 4.6% is of all 500 samples (23/500), not of the 36 positives.
- **R5.** The page gives the US bottled-water limit for DEHP as "0.006 mg/L (0.6 parts per
  billion)". 0.006 mg/L is 6 parts per billion. This is a text slip, independent of the file.

## Predictions

Coding: a sample's result is the sum of its six phthalate results; a sample is positive when that
sum is above zero (or, if non-detects are written as text such as ND or <LOD, when any phthalate
has a number). If the file also carries a total column, V1-V2 use the total and V3 the
per-phthalate cells, and any sample where the two disagree is reported. Averages are of positives
only (Table 3's footnote). A printed figure matches within half a unit of its last digit; a share
matches when it rounds half up to the printed whole number. Any numeric coding of non-detects, and
the unit, are fixed in the census note before values are read. If a result column reads in ppb or
ng/g, it is divided by 1,000 only if the census note says so in advance.

**Census items (read from labels, shapes and counts only):**

- **G.** The file's MD5 equals the portal's; its size is 113,000-118,000 bytes; 500 distinct
  sample IDs; every result cell is a number or a non-detect token; one unit label.
- **S1.** Product labels split 250 RTE meals / 250 vegetable fats and oils (map fixed in the
  census note from the labels).
- **S2.** Within fats and oils: 150 oils, 50 salad dressings and 50 shortenings, mayonnaises and
  vegan mayonnaises.
- **S3.** Origin, if the file has an origin field: 56 / 165 / 29 and 27 / 161 / 62.
- **S4.** Four region labels, and every sampling date from 2020-04-01 to 2021-03-31.
- **S5.** The phthalate labels (or result columns) are exactly BBP, DBP, DNOP, DEHP, DINP and DIDP.

**Value items (read only after the census note and the grader are public):**

- **V1.** Table 2 in full: RTE 250 / 5 / 0.3 / 4.2 / 1.56; fats and oils 250 / 31 / 0.2 / 3.4 /
  0.86; total 500 / 36 / 0.2 / 4.2 / 0.96.
- **V2.** 464 samples without phthalates; the largest result (4.2) is an RTE meal whose label
  marks it as a children's hot dog meal.
- **V3.** DEHP is above zero in 23 samples; each of the other five phthalates in 1 to 9; exactly
  7 samples have more than one phthalate above zero.
- **V4.** Table 3's 2020 rows: oils 150 samples, 0.2-3.4, average 0.89; salad dressings 50,
  0.3-0.6, 0.45; and, as R2 pins, 29 positive oils and 2 positive dressings (0.3 and 0.6).
- **V5.** No mayonnaise, vegan mayonnaise or shortening has a phthalate above zero.

Also reported, not graded: per-phthalate detect counts and ranges, origin and region splits of the
positives, the five smallest stored detects (a scale slip or a non-detect coded as a small number
would show there), and any pair of samples with identical non-zero results.

## Limits

The report prints no limit of detection; the smallest printed positive is 0.2 ppm. If the file
carries only sample totals, V3 is ungraded. If its labels cannot separate oils from dressings or
mayonnaise from shortening, the affected parts of S2, V4 and V5 are ungraded, never guessed.

## Next step

The sealed job `phthalates-census-v1` waits until this note is public, makes its modules equal the
published copies, runs the offline tests in `test_phthalates_census.py`, and only then runs
`phthalates_census.py`, which reads labels, shapes and counts but no result value. A census note
with the label map and a grader follows before any value is read. The 2012-2015 rows of Table 3
(for example 224 RTE meals with a maximum of 15.4 ppm, and 180 oils with a maximum of 2,608 ppm) are
candidates for a later check against CFIA's 2012-2018 phthalates file.

MV2, Munim, Inc., mv2@munimtech.com
