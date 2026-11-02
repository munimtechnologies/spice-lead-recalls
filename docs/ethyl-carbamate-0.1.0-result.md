# ethyl-carbamate 0.1.0: result — CFIA's 2018-19 file stores 36 of its 37 detects 1,000 times too small; 2019-20 reproduces in full

RESULT-MARKER: ethyl-carbamate-0.1.0-result

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This is the result of the [pre-registration](ethyl-carbamate-0.1.0-prereg.md) (`v0.4.104`),
graded with the label maps and grader of the [census note](ethyl-carbamate-0.1.0-census.md)
(`v0.4.105`). Both were public before any result value was read. This is a reproducibility check of
open government data. It is not a compliance finding, it is not about any brand, and it is not
dietary or medical advice.

**Run.** The sealed job `ethyl-carbamate-grade-v1` ran on 2026-11-02 from 12:13 to 12:14 UTC
(python:3.12, 1 GB, no host paths). It checked that the census note was public and that its modules
matched the published copies, ran the 11 offline tests (all passed), and then graded. Both gates
passed (size, MD5, columns, numeric values, unit, 390 and 300 samples with one row each).

## Headline

- **2019-20 (fermented vegetables and soy): every graded item held** (V5, V6, V7). Table 2
  reproduces in full, 94 of 100 soy samples have no EC (so the text's "93%" is a slip), and the
  later CFIA report's 2019 soy row (minimum 4.0, average 74.1) does carry the all-products Total row:
  soy alone is 7 to 217 with an average of exactly 108.0, and all nine detects average 74.11.
- **2018-19 (alcoholic beverages and vinegars): V1, V2 and V3 failed as registered, for one
  reason.** Every sample count and every detect count matches, but 36 of the 37 detected values
  are 1,000 times smaller than the report's ppb figures, although every row's unit is "ng/g" (ppb).
  The two detected beers read 0.004, where Table 2 prints 4; the highest alcoholic beverage reads
  0.086, where Table 2 prints 86. **One value is on the printed scale:** the vinegar
  `C2018ETCA00370` reads 135.0, which is Table 2's vinegar maximum of 135.
- **Exploratory, not pre-registered:** reading the 36 values below 1 as micrograms per gram (that
  is, multiplying them by 1,000) and leaving the 135 alone reproduces every printed 2018-19 cell
  that can be checked, including the later report's alcoholic-beverage subtotal.

So 3 of the 6 graded items held. V4 (the 86 ppb wine) stays ungraded because the file has no
wine label.

## The graded items

| ID | Registered | Observed | Met |
|---|---|---|---|
| V1 | ec18 Table 2: beer 125 / 2 / 4-4 / 4; vinegar 125 / 6 / 6-135 / 29.5; sake + spirits + wine pooled 140 / 29 / 4-86 / 15.42-15.62; total 390 / 37 / 4-135 / 17.2 | every sample and detect count holds; beer 0.004-0.004, average 0.004; vinegar 0.006-135, average 22.507; pooled 0.004-0.086, average 0.0156; total 0.004-135, average 3.66 | ❌ |
| V2 | both beer detects round to 4; one vinegar is 135 and the other five each round to 6-13 and sum to 41-43 | beers 0.004 and 0.004; vinegars 0.006, 0.006, 0.007, 0.010, 0.013 (sum 0.042) and 135.0 | ❌ |
| V3 | the later report's alcoholic subtotal: 265 / 31 / 4-86 / 14.75-14.85 | 265 / 31 / 0.004-0.086, average 0.0148 | ❌ |
| V4 | the 86 ppb wine is fortified, sweet or 20 years old | ungraded: the file labels every sake, spirit and wine "Beverage - Alcohol" | — |
| V5 | ec19 Table 2: vegetables 3 detects 4, 6, 9 (average 6.25-6.35); soy 6 detects, 7-217, average 107.5-108.5; total 9, 4-217, 73.5-74.5 | vegetables 4, 6, 9 (6.33); soy 7, 9, 94, 157, 164, 217 (108.0); total 74.11 | ✅ |
| V6 | 94 of 100 soy samples have no EC; the vegetable detects are 2 sauerkrauts and 1 other fermented vegetable | 94; Sauerkraut 4, Sauerkraut 6, Pickled Vegetable - Misc 9 | ✅ |
| V7 | soy minimum 7 and average 107.5-108.5; all-products average 74.05-74.15 | 7; 108.0; 74.11 | ✅ |

V6 was graded without its bean-curd and miso part, as the census note said in advance: the soy
detects are all labelled "Soy Products". Five of the six are imports from Taiwan (217, 164, 157,
94 and 9 ppb) and one is Canadian (7 ppb).

## The 2018-19 scale problem

The file's result column (`MaxOfAMOUNT`) holds 353 zeros and 37 values above zero, so the detect
counts are right: 2 beers, 29 sakes, spirits and wines, and 6 vinegars, as Table 2 prints. The
values themselves are on two scales:

- **36 values run from 0.004 to 0.086.** Read as ppb, as the unit column says, they would be far
  below anything the report prints (its smallest printed result is 4). Read as micrograms per gram
  (ppm), they are 4 to 86 ppb.
- **One value, 135.0, is a vinegar** (`C2018ETCA00370`, sampled 3 May 2018, origin unknown). Read
  as ppb it is Table 2's vinegar maximum. Read as ppm it would be 135,000 ppb.

No single unit makes the file agree with its report: under "ng/g" 36 results are 1,000 times too
small, and under "µg/g" the vinegar is 1,000 times too large. The file is internally inconsistent,
not just mislabelled.

**Where the values come from.** All 36 small values belong to samples whose region is West. The
135 is the only result above zero among the Ontario samples:

| Region | Samples | Detects |
|---|---|---|
| West | 122 | 36 (all below 1) |
| Ontario | 154 | 1 (135.0) |
| Quebec | 87 | 0 |
| Atlantic | 27 | 0 |

The file does not say which laboratory analysed which sample, so this table is a description, not
a cause. It does mean that 36 of the report's 37 detects come from samples collected in one region.

## Exploratory: the rescaled file reproduces the report

This part was not pre-registered and does not change any grade. Multiplying each 2018-19 value
below 1 by 1,000:

| Row (printed) | File, rescaled |
|---|---|
| Beer 125 / 2 / 4-4 / 4 | 125 / 2 / 4-4 / 4 |
| Vinegar 125 / 6 / 6-135 / 29.5 | 125 / 6 / 6-135 / 29.5 (detects 6, 6, 7, 10, 13, 135) |
| Sake + spirits + wine (pooled band 15.42-15.62) | 140 / 29 / 4-86 / 15.55 (sum 451) |
| Total 390 / 37 / 4-135 / 17.2 | 390 / 37 / 4-135 / 17.19 (636 / 37) |
| Later report's alcoholic subtotal 265 / 31 / 4.0-86.0 / 14.8 | 265 / 31 / 4-86 / 14.81 (459 / 31) |

The five smaller vinegars come out at 6 to 13 and sum to 42, as the report's arithmetic required
(pre-registration R6). CFIA's own tables, including the later 2016-22 report, therefore used values
1,000 times larger than the ones published for 36 samples.

Two descriptive notes on the pooled row, also exploratory: the largest value (86 after rescaling,
Table 2's wine maximum) is an import from the Republic of Korea (`C2018ETCA00126`); the file does not
say what kind of drink it is. The three detects from Japan rescale to 7, 17 and 33, so they cannot
all be the report's three sakes (7, about 7 and 33); the file's single label cannot separate them.

## Descriptive results (no grade)

- **Labels.** The "Beef" sample (`C2018ETCA00251`, Iceland) and the "Fish/Seafood" sample
  (`C2019ETCA00272`, Korea) both have no EC. Mapping them by ID block, as the census note fixed,
  gives the printed counts.
- **Dates.** 2018-19 runs from 3 April 2018 to 6 March 2019 (the text says 21 March). 2019-20 runs
  from 9 April 2019 to 23 March 2020.
- **IDs.** 2018-19: 1-400 with ten gaps in the alcohol block; 2019-20: 1-300, with one `D` ID
  (`C2019ETCA00152D`) and no plain partner.

## What this adds to the CFIA erratum list

For a later note to CFIA's open-data team (held for review):
1. 2018-19 ethyl carbamate file: 36 of 37 detects are stored 1,000 times smaller than the report's
   ppb values under a "ng/g" unit; one vinegar (`C2018ETCA00370`, 135) is on the printed scale.
2. 2018-19: one beer labelled "Beef" (`C2018ETCA00251`); sampling ends 6 March 2019, not 21 March.
3. 2019-20: one fermented vegetable labelled "Fish/Seafood" (`C2019ETCA00272`); the portal's size
   field reads 58 for a 58,972-byte file; the French labels "Cornichon" and "Marinades (concombre)"
   look swapped; the text's "93%" should be 94%.
4. The 2016-22 report's Table 3 row for the 2019 soy survey carries the all-products minimum and
   average (4.0 and 74.1); soy alone is 7.0 and 108.

## Files and how to check

- `data/ethyl_carbamate_samples.csv`: one row per sample for both files (file, sample, product,
  mapped type, function, origin, region, date, EC as stored in the file). Values are copied
  unchanged; nothing is rescaled.
- `data/ethyl_carbamate_summary.json`: the sealed job's full record.
- `test_ethyl_carbamate_result.py`: an independent test that does not import the grader. From the
  per-sample table it rebuilds the graded rows, the scale finding, the region table, the
  exploratory rescale and the ec19 items, and checks them against the record. A sealed job re-runs
  it from GitHub after this note is public.

Source data: CFIA, open.canada.ca datasets `303903b7-91ba-4a79-ad37-7bcd9f0dc8a1` and
`920d97a1-b98d-4def-b386-dd234a45f457` (Open Government Licence - Canada).

**Limits.** The report pages print no limit of detection, and the file has none. The region
pattern does not show which laboratory produced which value. The rescale is a reading that makes
the file match the report; only CFIA can say which values are the measured ones. Prior art: a
search on 2026-11-02 found the report pages, the later 2016-22 report and the dataset records, but
no earlier note of this scale problem.

MV2, Munim, Inc., mv2@munimtech.com
