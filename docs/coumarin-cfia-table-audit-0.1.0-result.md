<!-- RESULT-MARKER: coumarin-cfia-table-audit-0.1.0-result -->
# coumarin-cfia-table-audit 0.1.0: result

By MV2 of Munim, Inc. Made with AI agents working in MV2's name. Code Apache-2.0; this note and
the table CC BY 4.0. Data: CFIA 2014-15 and 2015-16 coumarin targeted surveys (Open Government
Licence - Canada). An audit of published summary statistics against the agency's own open files.
It is **not a finding about any product, brand or health risk**, and it does not change any of
CFIA's conclusions, which rest on maxima and on Health Canada's assessments.

Grades [`coumarin-cfia-table-audit-0.1.0-prereg.md`](coumarin-cfia-table-audit-0.1.0-prereg.md),
public at tag `v0.4.46` before any non-tea value in either file was read.

## Headline

**Every average in CFIA's 2014-15 coumarin Table 2 is the mean of all samples, with non-detects
counted as zero, although the table note says "Only positive results were used to calculate the
average (hazard) levels."** All five predicted 2014-15 rows (four product rows and the grand total)
match the all-sample mean at printed precision and none matches the positives mean. The 2015-16
table follows its note: its averages are positives-only means. Gate and **8 of 8** verdicts met.

The size of the gap matters most where few samples were detected. For 2014-15 "Oils and extracts"
(46 of 239 detected), the printed average is **46.2 ppm**, while the positives-only mean the note
describes is **240.2 ppm**, 5.2 times higher. Survey-wide, the printed 149 ppm corresponds to a
positives-only mean of **238.3 ppm**.

## How it was graded

Sealed compute job `coumarin-cfia-audit-v1` (2026-10-24 08:02-08:03 UTC, `python:3.12`, no host
paths). `check_prereg.py` confirmed this study's pre-registration was public with its marker and
that the bundled modules equal the published copies; the offline tests (fixtures only) passed;
`coumarin_cfia_table_audit.py` 0.1.0 then read the SHA-256-pinned files (2014-15 `e418443d…ec1e`,
108,318 bytes; 2015-16 `45208635…d30c`, 117,565 bytes) through the published
`coumarin_eu_limits.py` 0.1.1 parser and rebuilt every Table 2 row from the labels fixed in the
pre-registration. It writes aggregate figures only; no per-sample value of a non-tea row is
published.

A computed mean "equals" a printed average when it rounds to it at the printed precision (within
0.05 of "4.7", within 0.5 of "302").

## Gate and predictions

| id | prediction | observed | grade |
|---|---|---|---|
| A0 (gate) | every file row maps to exactly one Table 2 row; row sizes equal CFIA's; no unmeasured rows; all units ug/g | both files: all labels mapped, 739 and 747 rows, sizes exact, none unmeasured, all `ug/g` | **pass** |
| Q1 | 2014-15 cooking sauces: all-samples | all 4.723 / positives 5.592 vs printed 4.7 | met |
| Q2 | 2014-15 dried beverage mixes: all-samples | 17.776 / 28.146 vs 17.8 | met |
| Q3 | 2014-15 oils and extracts: all-samples | 46.223 / 240.161 vs 46.2 | met |
| Q4 | 2014-15 spice mixes: all-samples | 329.434 / 384.956 vs 329 | met |
| Q5 | 2014-15 grand total: all-samples | 148.972 / 238.290 vs 149 | met |
| Q6 | 2015-16 spice mixes: positives | all 310.448 / positives 328.273 vs 328 | met |
| Q7 | 2015-16 baked goods: positives | 16.866 / 18.038 vs 18 | met |
| Q8 | 2015-16 grand total: positives | 351.414 / 391.801 vs 392 | met |

**9 of 9 (gate + 8 verdicts) met.** Reported but not graded, as registered: 2014-15 tea
(all-samples, known before registration), 2015-16 tea (positives, known) and 2015-16 ground
cinnamon (29 of 29 detected, so both means are 2,838.9 against the printed 2,839).

## The rebuilt tables (`data/coumarin_cfia_table_audit.csv`)

Every count, detected count, minimum and maximum in both tables matches CFIA's printed figure
exactly. Only the meaning of the averages differs.

| survey | row | n | detected | min | max | mean, all samples | mean, positives only | printed | printed = |
|---|---|---|---|---|---|---|---|---|---|
| 2014-15 | Cooking sauces | 148 | 125 | 0.2 | 50 | 4.72 | 5.59 | 4.7 | all samples |
| 2014-15 | Dried beverage mixes | 38 | 24 | 0.2 | 239 | 17.78 | 28.15 | 17.8 | all samples |
| 2014-15 | Oils and extracts | 239 | 46 | 0.2 | 1,000 | 46.22 | 240.16 | 46.2 | all samples |
| 2014-15 | Spice mixes | 104 | 89 | 0.8 | 2,170 | 329.43 | 384.96 | 329 | all samples |
| 2014-15 | Tea | 210 | 178 | 0.2 | 1,920 | 301.94 | 356.22 | 302 | all samples |
| 2014-15 | Grand total | 739 | 462 | 0.2 | 2,170 | 148.97 | 238.29 | 149 | all samples |
| 2015-16 | Ground cinnamon | 29 | 29 | 6.8 | 5,040 | 2,838.86 | 2,838.86 | 2839 | both |
| 2015-16 | Tea | 297 | 245 | 0.2 | 2,230 | 364.30 | 441.62 | 442 | positives |
| 2015-16 | Spice mixes | 221 | 209 | 0.2 | 3,040 | 310.45 | 328.27 | 328 | positives |
| 2015-16 | Baked goods | 200 | 187 | 0.2 | 130 | 16.87 | 18.04 | 18 | positives |
| 2015-16 | Grand total | 747 | 670 | 0.2 | 5,040 | 351.41 | 391.80 | 392 | positives |

Values in ppm (the files' unit is ug/g = mg/kg; the 2015-16 report's "ppb" column header is read as
ppm, since cinnamon at 5,040 ppb would be implausibly low). How far a positives-only reader of the
2014-15 table is off: cooking sauces ×1.19, dried beverage mixes ×1.58, oils and extracts ×5.20,
spice mixes ×1.17, tea ×1.18, grand total ×1.60.

The pre-registered reasoning holds up: CFIA's own printed figures already pointed here. The
2014-15 grand total is reproduced from the printed rows only under the all-sample reading
(sum of n × average / 739 = 148.9, printed 149; the positives reading gives 186.5), and the 2015-16
total only under the positives reading (sum of detected × average / 670 = 391.8, printed 392).

## Where the mislabelled figures travel

CFIA's later report *Coumarin in Selected Foods, 2016 to 2018* (Table 3, read on 2026-10-24 from
[inspection.canada.ca](https://inspection.canada.ca/en/food-safety-industry/food-chemistry-and-microbiology/food-safety-testing-reports-and-journal-articles/coumarin-selected-foods-2016-2018))
compares its results with earlier CFIA surveys under a note that only positive results were used.
It reprints the 2014 tea average as 302 and the 2014 spice-mix average as 329, next to
positives-only averages for other years. On a like-for-like positives basis those two figures are
356 and 385. So the dip that table shows for tea (500 in 2013, 302 in 2014, 442 in 2015) is partly
an artefact of the label, and the 2014 spice-mix figure sits next to its neighbours (390 in 2013,
327 in 2015) at 385, not 329. (We checked the basis of the 2013 tea figure, which is
positives-only, but not of the 2013 spice-mix figure.) (That
table also gives 508 teas and 324 spice mixes for 2014, where the 2014-15 report's Table 2 and the
open file have 210 and 104; the 2014-15 report's own Table 3 has the same larger figures.)

Anyone reusing the 2014-15 averages as positives-only hazard levels, in an exposure model or a
literature comparison, should use the positives column above.

## Data and test

- `data/coumarin_cfia_table_audit.csv`: one line per Table 2 row: computed and printed n,
  detected, minimum, maximum, both means and the verdict.
- `test_coumarin_cfia_table_audit_result.py` re-derives every verdict from that table by the
  registered rounding rule, checks that the rows add up to the grand totals (counts, maxima, and
  the coumarin totals implied by both kinds of mean), recomputes both tea rows from the published
  per-sample tea table (`data/coumarin_tea_replication_samples.csv`) and recomputes the
  grand-total arithmetic from CFIA's printed figures. Plain `csv`, `math`, `statistics`,
  `unittest`.

## Limits

- A match at printed precision is evidence about how a figure was computed, not proof. Here no
  graded verdict is a near-tie: in every graded row the other mean misses the printed figure by
  more than twice the half-unit rounding window (closest: 2015-16 baked goods, 16.87 against 18,
  window 0.5), and in every 2014-15 row by at least 17 times the window.
- The 2013-14 report's own Table 2 is not open, so it is not audited. Its tea average of 500,
  reprinted later, matches the positives mean of the open file.
- Only Table 2 of each report is audited. The figures from the 2016-2018 report above were read
  from its web page and are not part of the graded audit.
- No finding here concerns the safety of any product. CFIA and Health Canada judged these surveys
  on maxima and exposure assessments, which this audit does not touch.

<!-- RESULT-MARKER: coumarin-cfia-table-audit-0.1.0-result -->
