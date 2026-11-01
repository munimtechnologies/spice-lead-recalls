# bpa-series 0.1.0: CFIA's open bisphenol A files, 2010-11 to 2017-18, against the printed reports — result (five of seven files)

RESULT-MARKER: bpa-series-0.1.0-result

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This grades the value items of the pre-registration
[bpa-series-0.1.0-prereg.md](bpa-series-0.1.0-prereg.md) (tag `v0.4.87`). It uses the label maps
of the [census note](bpa-series-0.1.0-census.md) (`v0.4.91`) and the grader of the
[grader note](bpa-series-0.1.0-grader.md) (`v0.4.95`); all three were public first. The sealed job
`bpa-series-grade-v1` ran on 2026-11-01 from 07:29 to 07:34 UTC (python:3.12, 1 GB, no host
paths). It waited for the three notes to be public, checked that its bundled
`bpa_series_grade.py` and `test_bpa_series_grade.py` matched the published copies, ran the 19
offline tests, and only then read the seven files.

**Five of the seven gates passed. Of the 6 items they allow to be graded, 4 held: V2, V5, V7 and
D1.** V4 failed, as the grader note said it must. V6 failed on two of its seven checks, and both
failures are explained below.

The 2009-10 and 2011-12 gates failed only on the sample-ID pattern, a format check. Every count
in those gates held: 200 and 403 samples, units, plan codes and labels. Eight 2009-10 IDs have
three digits (`2009BPA176` to `2009BPA183`). Three 2011-12 IDs end in `-2` (`2011BPA0086-2`,
`2011BPA0270-2`, `2011BPA0272-2`). The grader's pattern allowed neither. So V1, V3 and the
dates item T1 were not graded. A separate, public
[ID-pattern amendment](id-pattern-0.1.1-amendment.md) widens only that pattern, discloses what
the failed run's output already showed, and grades them in a new sealed job.

This is a reproducibility check of open government data, not a compliance finding and not about
any brand. Canada has no maximum level for BPA in food; Health Canada assesses results case by
case. Nothing here is dietary or medical advice. All figures are ppb, and averages are over
positive samples only, as the reports state.

## Headlines

1. **2013-14 reproduces in full.** All nine rows of Table 5 match the file in every cell,
   including pasta as 45 samples, all 45 positive. That settles the pre-registered slip: a later
   trend table lists 2013 pasta as "34" samples.
2. **2010-11: no positive among 234 samples**, as the report says (V2).
3. **2017-18 reproduces in full.** This covers Table 2's meat, fish and total rows (meat average
   35.6, not the 34.6 or 46.6 printed elsewhere), the top value of 1,480 (an imported canned fish)
   and the next at 567, and the single BPS positive (a Brazilian canned meat, 1.79). 69 of 72
   BADGE positives and all 68 BPF positives also contain BPA, and every BADGE, BPF and BPS row
   matches, with a BADGE average of 10.1 (V7, X7).
4. **2012-13's Table 5 covers 509 samples, and the 67 it leaves out are all pastas.** The file
   has 119 canned pastas, and Table 5's pasta row says 52 (all positive). 576 − 509 = 67 =
   119 − 52. The file's 53 pasta positives reproduce the row's 52 / 5.2 / 157 / 21.9 if exactly
   one of them is dropped, and that one must lie between 7.7 and 12.9 ppb. Eleven file values do,
   so the file cannot say which. The summary totals still hold (145 positives; minimum 5.2, a
   pasta; maximum 381, a coconut milk; 92 in pastas and soups).
5. **2012-13 counts three salsas with curry.** Under the census map, which was fixed before any
   value was read, curry has 21 samples and vegetables 147, against Table 5's 24 and 144 (the
   reason V4 had to fail). Moving the file's 3 salsas to curry, an exploratory step after grading,
   makes the curry row match in every cell and gives vegetables 144. The vegetables average is
   still 34.7, not the printed 34.0. Coconut milk's 17 positives sum to 1,111.2 (average 65.4),
   against the printed 63.0.
6. **2016-17: Table 2 is canned food only, and the rest of the file is exactly the report's
   "other packaging" part.** The file has no packaging label, but its surplus over Table 2 sits
   in five rows: 14 beverages, 8 formulas, 1 pasta, 2 sauces and 2 soups (27 samples). Those 27
   carry 21 positives, the report's count of non-canned positives. Table 2's positives add up to
   340, its canned count. The file's 361 positives also fit 340 × 91.6 + 21 × 15.2 within
   rounding. The four rows that can be graded (coconut milk, fruit, pie filling, vegetables)
   match in every cell, with vegetables at 139, not the text's 138. So do the all-product average
   of 87.2, Table 4's BADGE and BPF rows, the top BADGE value (224, a coconut milk without BPA)
   and the three BPF positives (bamboo shoots, each also with BPA).
7. **The jump in positive rates from 2012-13 to 2013-14 is not only a detection-limit change
   (D1).** Every
   2012-13 positive is at least 5.2 ppb. At that common cut, in the categories both surveys share,
   2013-14's share is 2.38 times 2012-13's (59.9% vs 25.2%). It is higher in every one of the six
   shared categories: vegetables 70% vs 20%, pastas and soups 89% vs 42%, coconut milk 85% vs 37%,
   beverages 20% vs 3%, fruit 13% vs 1%, curry 5 of 5 vs 3 of 21.

## Graded items: 4 of 6 held

| ID | Registered | Observed in the file | Met |
|---|---|---|---|
| G09 | 2009-10 structure gate | all counts hold; 8 IDs with 3 digits fail the ID pattern | ❌ (gate) |
| G10 | 2010-11 structure gate | all 10 checks; MD5 matches the portal | ✅ (gate) |
| G11 | 2011-12 structure gate | all counts hold; 3 IDs ending `-2` fail the ID pattern | ❌ (gate) |
| G12 | 2012-13 structure gate | all 10 checks; MD5 matches the portal | ✅ (gate) |
| G13 | 2013-14 structure gate | all 10 checks (no portal MD5 to compare) | ✅ (gate) |
| G16 | 2016-17 structure gate | all 10 checks (no portal MD5 to compare) | ✅ (gate) |
| G17 | 2017-18 structure gate | all 10 checks; MD5 matches the portal | ✅ (gate) |
| V1 | 2009-10: 82 positives, 9 infant food, 1.4-9.6 | not graded (gate G09) | — |
| V2 | 2010-11: no positive | 0 of 234 | ✅ |
| V3 | 2011-12: six positives (1 pasta, 3 carrots, 1 peas, 1 corn) | not graded (gate G11) | — |
| V4 | 2012-13: 145 positives, min 5.2 pasta, max 381 coconut milk, 92 in pasta + soup, ≥4 of 5 rows in full | the first four hold; only 2 of 5 rows in full (beverages, fruit) | ❌ (said in advance) |
| V5 | 2013-14: 252 of 391, min 1.0 fruit, max 565 corn, ≥7 of 9 rows in full | all hold; 9 of 9 rows | ✅ |
| V6 | 2016-17: four rows in full, 361 positives, average 87.2, four "highest / next" pairs | 5 of 7 checks; see below | ❌ |
| V7 | 2017-18: Table 2, top two, BPS, BADGE and BPF co-occurrence | all 7 checks | ✅ |
| D1 | directional: 2013-14 share at 5.2 ppb ≥ 1.5 × 2012-13's | 2.38 | ✅ |

**Why V6 failed.** Two of its checks failed, as registered:

- Fruit: the 1,160 maximum and the 186 runner-up match. The check required the label `Pineapple`,
  but the sample is labelled `Pineapple - Organic`.
- Sauces: the text gives the runner-up after 1,120 as 7.5. The file's runner-up is 188, a Thai
  `Sauces` sample. Table 2's own sauce row (5 positives, average 228, maximum 1,120) leaves only
  17.5-22.5 ppb for the other four canned sauces. So the 188 cannot be a canned sample: it
  belongs to the non-canned part that the file does not label. The check could not have
  separated the two.

## The files by category (BPA, ppb; positives only)

| Survey | Category | n | Positive | Minimum | Maximum | Average |
|---|---|---|---|---|---|---|
| 2012-13 | Beverages/juices | 72 | 2 | 5.9 | 12.0 | 8.95 |
| 2012-13 | Coconut milk | 46 | 17 | 5.4 | 381 | 65.36 |
| 2012-13 | Curry (census map) | 21 | 3 | 88.0 | 298 | 226.7 |
| 2012-13 | Fruit | 73 | 1 | 8.6 | 8.6 | 8.6 |
| 2012-13 | Canned pasta | 119 | 53 | 5.2 | 157 | 21.68 |
| 2012-13 | Soup | 98 | 39 | 5.7 | 277 | 76.16 |
| 2012-13 | Vegetables (census map) | 147 | 30 | 5.54 | 103 | 34.74 |
| 2012-13 | All | 576 | 145 (25.2%) | 5.2 | 381 | 48.13 |
| 2013-14 | All | 391 | 252 (64.5%) | 1.0 | 565 | 27.11 |
| 2016-17 | All (every packaging) | 491 | 361 (73.5%) | 1.1 | 2,240 | 87.18 |
| 2017-18 | Canned meat | 231 | 170 | 1.20 | 407 | 35.62 |
| 2017-18 | Canned fish/seafood | 237 | 159 | 1.29 | 1,480 | 54.66 |
| 2017-18 | All | 468 | 329 (70.3%) | 1.20 | 1,480 | 44.82 |

The 2013-14 rows equal Table 5 cell for cell, and the 2016-17 and 2017-18 rows are in
`data/bpa_series_summary_0.1.0.json`.

## Limits

- "Positive" is the file's own coding (a value above 0). None of these files gives a reporting
  limit per sample. That is why D1 compares shares at a common cut instead of raw positive rates.
- D1 compares survey samples, not the same products over time. Product mixes inside each
  category differ between the two years.
- Headlines 4 to 6 are arithmetic on the report's figures and the file, done after grading, and
  were not pre-registered. They show which readings make the printed figures agree; they cannot
  show why a table left samples out.
- The 2016-17 "non-canned" reading rests on counts and sums. The file itself has no packaging
  column.

Prior art: searches on 2026-10-30, 2026-10-31 and 2026-11-01 found the CFIA report pages, the
open dataset records, Health Canada's Total Diet Study work on BPA and news coverage of the
2023-24 survey. They found no analysis of these per-sample files and no check of them against the
printed figures.

## Reproduce it

- `data/bpa_2010_samples.csv`, `bpa_2012`, `bpa_2013`, `bpa_2016` and `bpa_2017` are the sealed
  job's output, one row per sample: ID, product, category, Function, origin, region, date and BPA
  in ppb. The 2016-17 and 2017-18 files also have BADGE, BPF and BPS.
- `data/bpa_series_summary_0.1.0.json` is the sealed grader record: gates, every item with
  observed values, census and provenance (SHA-256 of each file).
- `test_bpa_series_result.py` is a pinned test that does not import the grader. It uses its own
  code, its own copy of the label maps and its own copy of the printed figures, and checks them
  against the sealed record:
  - every printed row above;
  - the 67-pasta and salsa reconciliations;
  - the 2016-17 canned / non-canned split and the sauce arithmetic;
  - the BADGE, BPF and BPS rows;
  - the D1 shares;
  - the absence of identical multi-analyte profiles.

A sealed follow-up job (`bpa-series-result-v1`) fetches these published files from GitHub and
re-runs the pinned test on them.

MV2, Munim, Inc., mv2@munimtech.com
