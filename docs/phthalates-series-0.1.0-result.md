# phthalates-series 0.1.0: result — the 2018-19 flatbread and vegan file reproduces its report in full; two later tables' "2012-2015" rows have the 2012-2018 file's detections over different sample counts

RESULT-MARKER: phthalates-series-0.1.0-result

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This is the result of the [pre-registration](phthalates-series-0.1.0-prereg.md) (`v0.4.113`),
graded as fixed in the [census note](phthalates-series-0.1.0-census.md) (amendment A2, label
maps, coding) and the [grader note](phthalates-series-0.1.0-grader.md) (`v0.4.115`). The sealed job
`phthalates-series-grade-v1` ran on 2026-11-06 at 19:57 UTC. It first checked that all three notes
were public and that its modules matched the published copies, then ran the 14 offline tests (all
passed), and only then read the values of two CFIA open files (Open Government Licence - Canada):

- **F**, 2018-19 phthalates in flatbreads and vegan products: open.canada.ca dataset
  `c4202b90-03d1-4eef-9fcc-0740066fc0c4`, 149,790 bytes, MD5 `22dc3074e8e2c55b60fb96a666c5ff16`,
  599 samples.
- **P**, 2012-2018 phthalates in selected foods: dataset `ea25d8e4-180c-4f7c-a912-f37381168664`,
  1,288,434 bytes, MD5 `2c80659a91013f3657519375ee33b400`, 4,517 samples.

This is a reproducibility check of open government data. It is not a compliance finding (Canada
has set no maximum level for phthalates in food, and Health Canada found the detected levels
safe), not about any brand, and not dietary or medical advice. Values are ppm (µg/g); a sample's
result is the sum of its phthalates; averages are of positives only, as registered.

The sealed records are [`data/phthalates_fv18_record.json`](../data/phthalates_fv18_record.json)
and [`data/phthalates_ps12_record.json`](../data/phthalates_ps12_record.json). The per-sample tables
are [`data/phthalates_fv18_samples.csv`](../data/phthalates_fv18_samples.csv) and
[`data/phthalates_ps12_samples.csv`](../data/phthalates_ps12_samples.csv) (one row per sample, CC BY
4.0, derived from the Open Government Licence - Canada files).
[`test_phthalates_series_result.py`](../test_phthalates_series_result.py) recomputes every graded
number and every exploratory reading below from those tables with its own code (it does not import
the grader); the descriptive ranges come from the sealed records.

## Summary

- **Gates.** As written, both failed on the size band alone (both MD5s match). Under amendment A2
  (open.canada.ca sizes are kibibytes rounded up), published before any value was read, both pass.
  Every value grade below is under A2.
- **6 of 8 value items held.** F: 4 of 4. P: 2 of 4 (P-V1 and P-V4 held; P-V2 and P-V3 failed).
- **F reproduces its report in full**: Table 2 in all seven rows and 42 cells, every value claim
  of the text, and (from the census) the origin table in all six cells. Every figure of the report
  that the file can check matches. The page's text slips (below) need no file.
- **P's "2012-2015" rows: the detections reproduce, the sample counts mostly do not.** Every
  positive count, minimum and maximum printed for April 2012 to March 2015 is in the file. The
  averages of grain products, ready-to-eat meals and salad dressings match too. What differs is the
  number of samples: 459 grain products (printed 460), 237 meals (224), 42 dressings (22), 160 oils
  (180) and 248 fats and oils (327). Two averages also differ: nut and seed butters 17.26 (printed
  17.2) and oils 106.0 (107); the fats-and-oils average (95.6 against 84.3) differs because the
  group itself does.

## F: 2018-19 flatbreads and vegan products (all four held)

| Table 2 row | Printed: samples / positives (%) / min / max / average | File |
|---|---|---|
| Flatbreads | 208 / 54 (26) / 0.57 / 15.00 / 2.70 | 208 / 54 (26.0) / 0.57 / 15.00 / 2.699 |
| Vegan products | 391 / 19 (5) / 0.50 / 24.00 / 3.61 | 391 / 19 (4.9) / 0.50 / 24.00 / 3.610 |
| Dairy alternatives | 76 / 6 (8) / 0.59 / 2.78 / 1.17 | 76 / 6 (7.9) / 0.59 / 2.78 / 1.167 |
| Mayonnaise (vegan) | 53 / 3 (6) / 0.72 / 3.19 / 1.64 | 53 / 3 (5.7) / 0.72 / 3.19 / 1.637 |
| Meat alternatives | 125 / 7 (6) / 0.50 / 7.57 / 3.45 | 125 / 7 (5.6) / 0.50 / 7.57 / 3.449 |
| Tofu | 137 / 3 (2) / 0.54 / 24.00 / 10.85 | 137 / 3 (2.2) / 0.54 / 24.00 / 10.847 |
| Total | 599 / 73 (12) / 0.50 / 24.00 / 2.94 | 599 / 73 (12.2) / 0.50 / 24.00 / 2.936 |

- **F-V1 held:** the table above.
- **F-V2 held:** 526 samples have no phthalate; the single largest result, 24.0 ppm, is a tofu
  (`C2018PHTH00718`, imported, DBP alone).
- **F-V3 held:** DINP in 51 samples (8.5%, the page's "BINP ... 9%"), DEHP in 24 (4.0%), DBP in 4,
  DIDP in 2, BBP and DNOP in none; 8 samples hold two phthalates.
- **F-V4 held:** the pre-registration derived tofu's middle positive from the printed average
  alone (3 x 10.85 - 24.54 = 8.01, so 7.985 to 8.035). It is 8.0 (`C2018PHTH00719`: DBP 4.0 and DEHP
  4.0). Mayonnaise's middle positive, derived the same way as about 1.01, is 1.0.

The census had already settled the counting parts of F-V2 and F-V3 and the 73 positives (from
the screen rows), so those parts were not blind. The blind parts were the split of the 73 between
groups, every minimum, maximum and average, the sample holding the maximum, and F-V4.

**Text slips on the 2018-19 page** (registered as R4 before the file was read; the file does not
change them): "599 ... flatbreads" (Table 1: 208 flatbreads, 599 in all); "BINP" and "BDP", which
are not among the six phthalates tested (the file has DINP 51 and DBP 4, matching the page's 9%
and 4); and "0.006 milligram per liter (0.6 ppb)", which is 6 ppb.

## P: 2012-2018 selected foods

- **P-V1 held:** 977 of 4,517 samples carry a phthalate; totals run from 0.26 to 2,607.68 ppm
  (printed 2,608), the maximum a palm oil (`F2014PHTH00774`, 2014-15).
- **P-V4 held:** 3 of 26 mayonnaises from 2012-15 are positive (11.5%, printed 12%), averaging
  2.773 (2.77); none of the 20 vegetable shortenings is.
- **P-V2 failed** and **P-V3 failed**, part by part as below (2012-15 read by sampling date, April
  2012 to March 2015, the reading fixed in the census note).

| 2012-15 row (source) | Printed | File | What matches |
|---|---|---|---|
| Grain products (2018-19 Table 3) | 460 / 167 (36%) / 0.27 / 23.3 / 1.60 | 459 / 167 (36.4%) / 0.27 / 23.31 / 1.603 | all but the count, by one |
| Nut and seed butters (2018-19 Table 3) | 100 / 59 (59%) / 0.5 / 315 / 17.2 | 100 / 59 (59.0%) / 0.5 / 315.0 / 17.259 | all but the average |
| Ready-to-eat meals (2020-21 Table 3, text 57.1%) | 224 / 128 (57.1%) / 0.27 / 15.4 / 1.46 | 237 / 128 (54.0%) / 0.27 / 15.40 / 1.465 | all but the count |
| Salad dressings (2020-21 Table 3, text 36%) | 22 / 8 (36%) / 0.71 / 3.75 / 2.25 | 42 / 8 (19.0%) / 0.71 / 3.75 / 2.246 | all but the count |
| Oils (2020-21 Table 3) | 180 / - / 0.26 / 2608 / 107 | 160 / 98 / 0.26 / 2607.68 / 106.0 | minimum and maximum |
| Vegetable fats and oils (2020-21 Table 3) | 327 / - / 0.26 / 2608 / 84.3 | 248 / 109 / 0.26 / 2607.68 / 95.6 | minimum and maximum |

(The 128 meals and 8 dressings are the counts that the printed 57.1% of 224 and 36% of 22 allow,
as registered; the file has exactly those positives.)

What this means:

1. **The printed detection rates for meals and dressings are higher than the file gives.** The
   2020-21 report's 57.1% of 2012-15 meals and 36% of dressings follow from its own counts (128 of
   224, 8 of 22). Over the file's samples from the same years they are 54.0% (128 of 237) and 19.0%
   (8 of 42). The 13 extra meals and 20 extra dressings in the file are all without phthalates.
2. **Grain products are one sample short in the file** (459 against 460), with every other figure
   equal.
3. **The nut and seed butters' average is 17.26, which rounds to 17.3.** The 59 positives sum to
   1,018.30 ppm; a printed 17.2 needs at most 1,017.75. The count, share, minimum and maximum all
   match, so this is either a cut-off instead of a rounding (as in the PAH 2019-20 file's 0.2373
   printed as 0.23) or a value that differs slightly.
4. **The oil and fats-and-oils rows describe groups that are not the file's.** Their minimum and
   maximum are the file's (both extremes are oils), but neither count nor average is.

The 2020-21 report cites these rows as "unpublished data", and the P file's portal record was last
modified on 2026-03-25, after both reports, so the rows may come from an earlier working table.
Either way, the open file and the printed rows do not describe the same samples.

## Exploratory (not registered; read after the values)

These readings were looked for after the grade. Many subsets of a 4,517-sample file can be tried,
so a fit here is a lead, not a finding. The test pins each number so that it can be checked.

- **The 22 dressings.** The file's 2012-15 dressings with origin "Unknown" are exactly 22, and they
  hold all 8 positives (8 of 22 = 36%). The other 20 (3 domestic, 17 imported) have no phthalate.
- **The 180 oils.** 160 oils plus the 20 shortenings make 180, but the shortenings have no
  phthalate, so the average would stay 106.0, not 107.
- **The 84.3 average.** Adding 2012-15's 17 positive dairy butters (of 84; they sum to 212.17 ppm)
  to the 109 fats-and-oils positives gives (10,415.62 + 212.17) / 126 = 84.35, which rounds to 84.3,
  at the edge. The count would then be 332 (348 with the 16 lard and animal-fat samples, none
  positive), not 327. So this does not explain the row either.

## Descriptive (not graded)

- **F per phthalate** (samples, range): DINP 51, 0.5-15.0; DEHP 24, 0.58-4.0; DBP 4, 0.54-24.0;
  DIDP 2, 0.95-1.0. F positives by origin: domestic 34, imported 12, unknown 27; by product: flatbread
  breads 25, tortillas, wraps and pitas 28, one bun, dairy alternatives 6, vegan mayonnaise 3, meat
  alternatives 7, tofu 3.
- **F values are coarse.** Many results are whole numbers (24.0, 15.0, 8.0, 7.0, 4.0, 2.0, 1.0); six
  samples share a total of 1.0 and three share 2.0. That fits rounding at the laboratory, not
  copied rows.
- **P per phthalate** (samples, range): DINP 659, 0.26-85.7; DEHP 273, 0.27-587; DBP 209, 0.26-4.3;
  DIDP 199, 0.26-2,520; BBP 8, 0.30-1.92; DNOP none. The ten largest totals are all oils (eight palm,
  two coconut), 364 to 2,608 ppm. P positives by origin: domestic 310, imported 427, unknown 240.
- **No stored non-detects** in either file: a phthalate not found has no row, and every screen count
  equals the number of rows.

## For CFIA's open-data team

Pointers, not confirmed errors; no person at CFIA has reviewed them.

1. Phthalates 2012-2015 rows in the 2020-21 report's Table 3 (meals 224, oils 180, dressings 22,
   fats and oils 327) and the detection rates in its text (57.1%, 36%) do not match the open
   2012-2018 file's samples from those years (237, 160, 42, 248; 54.0%, 19.0%), although every
   positive count, minimum and maximum does.
2. The 2018-19 report's Table 3 grain row counts 460 samples; the file has 459 for those years.
   Its nut and seed butter average, 17.2, is 17.26 in the file.
3. The 2018-19 page's text: "599 ... flatbreads", "BINP", "BDP" and "0.6 ppb" (6 ppb).

## Limits

- The gates failed as written; the value grades are under A2, a size-band-only amendment published
  before any value was read. The MD5s alone identify both files.
- P's own report (on open-science.canada.ca) could not be read, so P's predictions rest on two
  later reports and a search summary. A row in P's own report might match the file where the later
  tables do not.
- "2012 to 2015" is read by sampling date (April 2012 to March 2015), as fixed in the census note;
  reading it by the year in the sample ID gives the same grain, nut, meal and dressing groups and
  smaller oil groups (130 oils, 218 fats and oils), which fit no better.

## Next

A sealed job (`phthalates-series-result-v1`) downloads this note, the data tables and the
independent test from GitHub and runs the test, so the published result is re-checked from what is
public. The new items will be added to the [CFIA open-data errata](cfia-open-data-errata-0.1.0.md)
table in its next version.

MV2, Munim, Inc., mv2@munimtech.com
