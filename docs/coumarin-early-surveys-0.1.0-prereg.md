<!-- PREREG-MARKER: coumarin-early-surveys-0.1.0-prereg -->
# coumarin-early-surveys 0.1.0: pre-registration

By MV2 of Munim, Inc. Made with AI agents working in MV2's name. Code Apache-2.0; this note
CC BY 4.0. Data: CFIA 2011-12 and 2012-13 coumarin targeted surveys (Open Government Licence -
Canada).
This checks published summary figures against the agency's own open files and repeats earlier
screens on samples not read before. It is not a compliance finding (Canada sets no coumarin
limit), not about any brand, and not individual dietary or medical advice.

## Question

CFIA's first two coumarin surveys have open per-sample files: 2011-12 (193 samples) and 2012-13
(93 samples). Their full reports are available only on request. The public summary pages give a
detection rate, and for 2011-12 the highest result in each product category. Later reports
(2014-15, 2015-16 and 2016-18) reprint a "Table 3" row for each survey's tea and spice mixes under
a note saying only positive results were used for the average.

`coumarin-cinnamon` 0.1.0 published the 147 cinnamon samples. The other **139 samples** have not
been read: 2011-12 tea, spice mixes, breakfast cereals, baked goods, baking mixes and baby food,
and the 2012-13 spice mixes. This study asks three things:

1. Do CFIA's printed figures for these surveys match the open files?
2. Which mean does each reprinted average equal: the positives-only mean, as footnoted, or the
   mean of all samples? The [table audit](coumarin-cfia-table-audit-0.1.0-result.md) found that
   CFIA's 2014-15 table prints all-sample means under a positives-only note.
3. Do the earlier screens (EU coumarin maximum levels, the per-cup tea TDI screen and the infant
   comparison) replicate on these unseen samples?

## Method

- **Files.** SHA-256 pinned: 2011-12 `10d2a339...` (resource `796ade00-...`), 2012-13
  `6c155d79...` (resource `51630c7f-...`). Both digests were recorded by the coumarin-cinnamon-v1
  job. Both files are parsed by the published `coumarin_cinnamon.py` 0.1.0 parser. That parser
  reads results starting with "<", "ND" or "0" as non-detects (0). A sample is "detected" when
  its value is above 0. Both files give units as mg/kg (= ppm).
- **Categories** are the exact Product labels from a names-only census of each file. The census
  read the Product column only and displayed no result.

| survey | Product label | n | status |
|---|---|---|---|
| 2011-12 | `Ground Cinnamon` | 87 | published (coumarin-cinnamon) |
| 2011-12 | `Cinnamon Sticks` | 20 | published (coumarin-cinnamon) |
| 2011-12 | `Spice mix` | 24 | **unseen** |
| 2011-12 | `Tea` | 11 | **unseen** |
| 2011-12 | `Cereal` | 15 | **unseen** |
| 2011-12 | `Baked Goods` | 20 | **unseen** |
| 2011-12 | `Baking mix` | 7 | **unseen** |
| 2011-12 | `Baby Food` | 9 | **unseen** |
| 2012-13 | `Cinnamon` | 40 | published (coumarin-cinnamon) |
| 2012-13 | `Spice Mixes` | 53 | **unseen** |

- **Matching rule** (as in the table audit): a computed figure matches a printed one when it
  rounds to it at the printed precision (within 0.5 of "380", within 0.05 of "95.3"). An average's
  verdict is `positives`, `all-samples`, `both` (only possible when every sample is detected) or
  `neither`. A minimum printed as "<0.29" is read as "at least one non-detect".
- **Exceedance** means strictly above the level, as in every earlier study in this repository.

## Status of the values

- **Already published:** the 147 cinnamon values (`coumarin-cinnamon` 0.1.0).
- **Not seen:** no value of the 139 other samples has been read or published by any agent
  working on this repository, as far as the project's records show. The raw files were
  downloaded by the coumarin-cinnamon-v1 job (2026-10-18), which wrote only cinnamon results to
  its outputs. This run read only the Product column.
- The predictions rest only on CFIA's printed figures (below) and on earlier published results
  from *other* surveys.

### CFIA's printed figures

2011-12 summary page: 193 samples, coumarin detected in 98%. Highest results: ground cinnamon
7816, cinnamon sticks 6823, spice mixes 2014, tea 1040, baked goods 95.3, breakfast cereals 56.7,
baking mixes 45.8, baby food 14.9 ppm. 2012-13 summary page: 93 samples, detected in 100%,
highest 7621 ppm (a ground cinnamon).

Table 3 rows, the same in the 2014-15, 2015-16 and 2016-18 reports (average footnoted "only
positive results"):

| id | survey | row | n | min | max | average |
|---|---|---|---|---|---|---|
| T0 | 2011-12 | Ground cinnamon | 87 | 16.2 | 7816 | 3594 |
| T1 | 2011-12 | Tea | 11 | <0.29 | 1040 | 380 |
| T2 | 2011-12 | Spice mix | 24 | <0.29 | 2014 | 352 |
| T3 | 2012-13 | Spice mix | 53 | 30 | 3078 | 568 |

A note from the printed figures alone: the 2012-13 summary says no sample exceeded the levels of
2011-12. That holds survey-wide (7621 below 7816), but not for spice mixes: the reprinted 2012-13
spice-mix maximum (3078) is above the 2011-12 one (2014).

## Gate and predictions

| id | kind | prediction |
|---|---|---|
| E0 | gate | both files match their SHA-256 and the exact label census above, every unit is mg/kg, every result parses, there are no non-coumarin rows, and the published cinnamon values reproduce (2011-12 ground cinnamon smallest 16.2 and largest 7816.3, sticks largest 6823.2; 2012-13 cinnamon largest 7621.1) |
| C1 | consistency | each 2011-12 non-cinnamon category's maximum equals CFIA's printed maximum (2014, 1040, 95.3, 56.7, 45.8, 14.9) |
| C2 | consistency | detection rounds to CFIA's 98% (189 or 190 of 193) in 2011-12 and is 100% (93 of 93) in 2012-13 |
| C3 | consistency | rows T1-T3 match the file's n, minimum and maximum |
| V1 | verdict | T1, 2011-12 tea (380): **positives** |
| V2 | verdict | T2, 2011-12 spice mix (352): **positives** |
| V3 | verdict | T3, 2012-13 spice mix (568): **both** (every sample detected, so the two means agree) |
| R1 | replication | at most 8 of the 20 baked goods exceed the EU's 15 mg/kg fine-bakery level |
| R2 | replication | at most 3 of the 20 baked goods exceed the EU's 50 mg/kg seasonal-bakery level |
| R3 | replication | 1 or 2 of the 15 breakfast cereals exceed the EU's 20 mg/kg cereal level |
| R4 | replication | 1 to 3 of the 11 teas put a 15 kg child over EFSA's coumarin TDI (0.1 mg/kg bw/day) in one 2 g cup at 100% transfer (above 750 mg/kg) |
| R5 | replication | the baby-food median is strictly below the 2011-12 cereal median |

T0 is reported but not graded: its 87 values are already published. If E0 fails, nothing else
is graded, and an amendment comes first.

### Reasoning

- **C1-C3** test the parse against CFIA's own figures. In the 2014-15 and 2015-16 Table 2s,
  every count, minimum and maximum matched the files exactly, even where an average was
  mislabelled.
- **V1, V2 (positives).** This is a weak prior, stated as one. CFIA's 2014-15 table used
  all-sample means, but its reprint of the 2013-14 tea average (500) matches the positives mean.
  So the reprinted rows for earlier surveys seem to come from those surveys' own reports, not to
  be recomputed. Either outcome is informative, and "neither" is possible. Both rows print a "<"
  minimum, so their two means must differ.
- **V3 (both).** CFIA prints 100% detection and a 30 ppm minimum for these 53 spice mixes, so
  the positives mean and the all-sample mean are the same number. The test is whether that
  number rounds to 568.
- **R1, R2.** The 2011-12 "baked goods" are cookies and granola or breakfast bars (summary page).
  In 2013-14, 2 of 31 cookies exceeded 15 mg/kg, against 39 of 68 cinnamon-forward "Baked Goods"
  (42 of 100 bakery samples overall), and 11 of 100 exceeded 50 mg/kg
  ([coumarin-eu-limits](coumarin-eu-limits-0.1.1-result.md)). The cookie-heavy mix should sit
  below 42% (at most 8 of 20) and near 11% above 50 mg/kg (at most 3 of 20). CFIA's 95.3 maximum
  guarantees at least one in each; that is not a prediction.
- **R3.** In 2013-14, 3 of 136 cereals exceeded 20 mg/kg. CFIA's 56.7 maximum guarantees at
  least one here, and a second would already be a higher rate than 2013-14's.
- **R4.** Across 622 teas in three later surveys, 102 (16.4%) crossed this line; 16.4% of 11 is
  about 1.8. CFIA's 1040 maximum guarantees at least one. No adult 2 g cup can cross it (that
  needs above 3,000 mg/kg), so the adult scenario is reported, not graded.
- **R5.** In 2013-14, infant cereals (median 1.25 mg/kg) sat below children's cereals (median
  3.4) ([coumarin-infant](coumarin-infant-0.1.0-result.md)), and CFIA's printed maxima here are
  14.9 for baby food against 56.7 for cereals.

## Descriptive outputs (not graded)

- `coumarin_early_surveys.csv`: one line per Product label in both surveys, with n, detected,
  smallest detected, median, positives mean, all-sample mean and maximum. As far as we found,
  this is the first open per-category summary of these two surveys, whose reports are only
  available on request.
- `coumarin_early_samples.csv`: the 139 non-cinnamon samples (CFIA sample number, label,
  declared origin, mg/kg). No brand names: the files carry none.
- The infant screen as in coumarin-infant (8 kg infant, 30 g a day): CFIA's 14.9 maximum already
  implies no baby food reaches the TDI at 30 g (at most 56%). The 60 g count is reported.
- The tea per-cup table for all four scenarios (adult and child, 2 g and 4 g).

## Grading

The sealed job `coumarin-early-v1` (`python:3.12`, no host paths, 1 GB) runs these steps:

1. `check_prereg.py` waits until this note is public. It then makes every module it runs equal
   the published copy.
2. `test_coumarin_early_surveys.py` runs offline tests. It uses fixtures only, with no CFIA
   values.
3. `coumarin_early_surveys.py` 0.1.0 downloads and SHA-checks both files, grades E0, C1-C3, V1-V3
   and R1-R5, and writes `early_grades.json`, `early_summary.json` and the two CSVs.

## Limits (stated in advance)

- The samples are small (9 to 53 per category), so the R predictions are coarse.
- A match at printed precision is evidence about how a figure was computed, not proof.
- The 2011-12 "Baby Food" label mixes infant cereals and purées, so the infant screen uses
  dry-cereal serving sizes as an upper bound.
- EU levels apply to foods as eaten. Baking mixes are sold dry, so they are reported but not
  compared with an EU level.

<!-- PREREG-MARKER: coumarin-early-surveys-0.1.0-prereg -->
