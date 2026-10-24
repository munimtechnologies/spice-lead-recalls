<!-- PREREG-MARKER: coumarin-cfia-table-audit-0.1.0-prereg -->
# coumarin-cfia-table-audit 0.1.0: pre-registration

By MV2 of Munim, Inc. Made with AI agents working in MV2's name. Code Apache-2.0; this note
CC BY 4.0. Data: CFIA 2014-15 and 2015-16 coumarin targeted surveys (Open Government Licence -
Canada).
This audits published summary statistics against the agency's own open files. It is not a
finding about any product, brand or health risk.

## Question

Each of CFIA's coumarin survey reports has a Table 2 that gives, for each product type, the
number of samples, the number with detected coumarin, the minimum, the maximum and an
**average**. Both reports footnote that average: "Only positive results were used to calculate
the average (hazard) levels."

The [coumarin-tea-replication 0.1.1 amendment](coumarin-tea-replication-0.1.1-amendment.md) found
that the 2014-15 tea average (302) equals the mean of **all** 210 teas with non-detects as 0
(301.9), not the positives mean (356.2). The 2015-16 tea average (442) does equal the positives
mean (441.6).

**Is the 2014-15 tea row a one-off, or does it describe the whole table?** For every Table 2 row
of both reports, which mean does the printed average equal: the positives-only mean, as
footnoted, or the all-sample mean? We found no published reconciliation of these tables with
CFIA's open per-sample files.

## Method

- Files: the same SHA-256-pinned files as the tea replication (2014-15 `e418443d...`, 739 rows;
  2015-16 `45208635...`, 747 rows), parsed by the published `coumarin_eu_limits.py` 0.1.1. Every
  result is in ug/g (= mg/kg = ppm). Non-detects are coded `0`. A sample is "detected" when its
  value is above 0.
- **Row mapping.** An agent ran a names-only census of each file's Product column. It counted
  labels and displayed no result value. Each Table 2 row is the exact set of labels below, and
  every row in each file falls in exactly one set:

| survey | CFIA Table 2 row | Product labels in the file | n (CFIA) |
|---|---|---|---|
| 2014-15 | Cooking sauces | `Sauces` | 148 |
| 2014-15 | Dried beverage mixes | `Dried mixes` | 38 |
| 2014-15 | Oils and extracts | `Misc` | 239 |
| 2014-15 | Spice mixes | `Spice - Mixed` | 104 |
| 2014-15 | Tea | the six `Tea - *` labels | 210 |
| 2015-16 | Ground cinnamon | `Ground cinnamon` | 29 |
| 2015-16 | Tea | the six `Tea - *` labels | 297 |
| 2015-16 | Spice mixes | `Spice - Mixed` | 221 |
| 2015-16 | Baked goods | `Baked Goods` (199) + `Bakery Product - Bagel` (1) | 200 |

  The census counts equal CFIA's row sizes, and they add up to 739 and 747.
- **Matching rule.** A computed mean "equals" the printed average when it rounds to it at the
  printed precision: within 0.05 of "4.7", within 0.5 of "302". A row's verdict is
  `positives`, `all-samples`, `both` (possible only when every sample is detected) or `neither`.
- Every row also reports n, detected count, smallest detected value and maximum against CFIA's
  printed figures. These are descriptive, not graded.

## Status of the values

- **Already seen:** all 2014-15 and 2015-16 tea values (in the tea replication job output) and
  the 29 ground-cinnamon values for 2015-16 (published by `coumarin-cinnamon` 0.1.0).
- **Not seen:** no value from the 2014-15 cooking sauces, dried beverage mixes, oils and extracts
  or spice mixes, or from the 2015-16 spice mixes or baked goods, has been read or published by
  any agent working on this repository. The grand totals mix seen and unseen rows.
- The predictions rest only on CFIA's printed Table 2 figures, which are below.

| survey | row | n | detected | min | max | printed average |
|---|---|---|---|---|---|---|
| 2014-15 | Cooking sauces | 148 | 125 | 0.2 | 50 | 4.7 |
| 2014-15 | Dried beverage mixes | 38 | 24 | 0.2 | 239 | 17.8 |
| 2014-15 | Oils and extracts | 239 | 46 | 0.2 | 1000 | 46.2 |
| 2014-15 | Spice mixes | 104 | 89 | 0.8 | 2170 | 329 |
| 2014-15 | Tea | 210 | 178 | 0.2 | 1920 | 302 |
| 2014-15 | Grand total | 739 | 462 | 0.2 | 2170 | 149 |
| 2015-16 | Ground cinnamon | 29 | 29 | 6.8 | 5040 | 2839 |
| 2015-16 | Tea | 297 | 245 | 0.2 | 2230 | 442 |
| 2015-16 | Spice mixes | 221 | 209 | 0.2 | 3040 | 328 |
| 2015-16 | Baked goods | 200 | 187 | 0.2 | 130 | 18 |
| 2015-16 | Grand total | 747 | 670 | 0.2 | 5040 | 392 |

(The 2015-16 report prints "ppb" in its column headers. The file's unit is ug/g, and cinnamon at
5,040 only makes sense as mg/kg, so this is read as ppm.)

## Gate and predictions

| id | kind | prediction |
|---|---|---|
| A0 | gate | in both files, every row maps to exactly one Table 2 row, each row's size equals CFIA's, no row is unmeasured, and every unit is ug/g |
| Q1 | verdict | 2014-15 cooking sauces: **all-samples** |
| Q2 | verdict | 2014-15 dried beverage mixes: **all-samples** |
| Q3 | verdict | 2014-15 oils and extracts: **all-samples** |
| Q4 | verdict | 2014-15 spice mixes: **all-samples** |
| Q5 | verdict | 2014-15 grand total: **all-samples** |
| Q6 | verdict | 2015-16 spice mixes: **positives** |
| Q7 | verdict | 2015-16 baked goods: **positives** |
| Q8 | verdict | 2015-16 grand total: **positives** |

Reported but not graded: both Tea rows (already known) and 2015-16 ground cinnamon (29 of 29
detected, so the two means are identical). If A0 fails, Q1-Q8 are not graded and an amendment
comes first.

### Reasoning (from CFIA's printed figures only)

- **2014-15: one formula for the whole table.** If every row average is an all-sample mean, the
  all-sample grand mean is sum(n x average) / 739 = 110,050 / 739 = **148.9**, which prints as
  CFIA's **149**. Under the footnoted reading, the grand positives mean would be
  sum(detected x average) / 462 = **186.5**. If only the tea row were an all-sample mean and the
  other rows positives means, the printed total would match neither reading. So the printed total
  points to every 2014-15 row being an all-sample mean.
- **2015-16: footnote followed.** The positives reading reproduces the printed total:
  sum(detected x average) / 670 = **391.8**, printed as **392**. The all-sample reading gives
  387.8. The tea row already matches the positives mean.
- **What could fail.** Rounding in CFIA's printed row averages could push a recomputed mean just
  outside the half-unit window. A row could also have been computed differently (the 2015-16
  report's Table 3 prints different figures for ground cinnamon, 28 samples averaging 2,939, and
  spice mixes, 222 averaging 327). And sum(n x average) is consistent with several different
  per-row splits, so the total alone does not prove each row.

## Grading

The sealed job `coumarin-cfia-audit-v1` (`python:3.12`, no host paths) runs these steps:

1. `check_prereg.py` waits until this note and the tea amendment are public. It then makes every
   module it runs equal the published copy.
2. Offline tests run for both modules. They use fixtures only, no CFIA values.
3. `coumarin_tea_replication.py` 0.1.1 re-grades the tea replication (a verification).
4. `coumarin_cfia_table_audit.py` 0.1.0 writes `coumarin_cfia_table_audit.csv` (one line per
   Table 2 row: computed and printed n, detected, min, max, both means and the verdict),
   `audit_summary.json` and `audit_grades.json`. No per-sample values.

## Limits (stated in advance)

- A match at printed precision is evidence about how a figure was computed, not proof. Two
  formulas can round to the same number. That is why rows with 100% detection are not graded.
- The audit covers the two reports with an open Table 2. The 2013-14 report's full text is
  available only on request, so its own table is not audited. Its tea average of 500, reprinted
  in the 2014-15 report, matches the positives mean.
- A mislabelled average does not change any of CFIA's conclusions, which rest on maxima and on
  Health Canada's assessments. It does matter to anyone who reuses the averages as positives-only
  hazard levels, for example in exposure models or literature comparisons. The 2014-15 report's
  own Table 3 compares its 302 with other studies' averages.

<!-- PREREG-MARKER: coumarin-cfia-table-audit-0.1.0-prereg -->
