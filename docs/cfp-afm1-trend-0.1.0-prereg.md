# Pre-registration: aflatoxin M1 in six open CFIA Children's Food Project files (2012-13 to 2022) against every figure CFIA printed for them (cfp-afm1-trend 0.1.0)

PREREG-MARKER: cfp-afm1-trend-0.1.0-prereg

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code
Apache-2.0.

**Written before any aflatoxin M1 result value in these files was read.** The figures below come
from CFIA's report pages and from a names-only census of the open files (job
`cfp-afm1-years-census-v2`, 2026-10-29). The census records file hashes, headers, labels, units
and counts of rows, but never an aflatoxin M1 result value or a count of detections. For three
of the six years it did not even record the format of the result column, because its column
finder missed the `Result - Résultat` header. So this registration also fixes the value rule
blind.

The grading code is `cfp_afm1_trend.py`, and its offline tests are `test_cfp_afm1_trend.py`. A
sealed compute job (`cfp-afm1-trend-v1`) grades this registration only after it is public on
GitHub. The job checks out the published code and then reads the SHA-256-pinned files.

Nothing here is a finding about any product, brand or health risk. Canada sets no maximum level
for aflatoxin M1 (AFM1) in milk products. CFIA compares results with the Codex level of 0.5 ppb
for milk, and Health Canada judged every level it reported "not of concern".

## Why this is new

CFIA publishes the Children's Food Project (CFP) one year at a time, as a report page and a
per-sample CSV. On 2026-10-29, searches found the yearly reports, the open datasets and news
summaries of single years. They found no study that rebuilds the AFM1 series across years from
the open files, and no check of the files against the printed figures. This would be the first
open, per-sample AFM1 series for infant formula and dairy desserts sold in Canada. It is graded
against every figure CFIA printed, and its unit and count gaps are recorded.

## What CFIA printed (report pages read 2026-10-29)

- **2012-13** (148 milk-based, soy-based and specialized formulas bought nationally): "All
  milk-based and some specialized infant formula samples were analyzed for aflatoxin M1.
  Detectable levels of aflatoxin M1 were found in 12% of samples. All results were below the
  Codex ... 0.5 ppb." No count, range or limit is printed.
- **2014-15**: "A total of 32 milk-based infant food samples were tested ... formula, yogurt and
  puddings." "Aflatoxin M1 was detected in 4 of the 20 samples of infant formula ... Levels ranged
  from 0.011 ppb to 0.061 ppb in powdered formulas." "Aflatoxin M1 was not detected in 12 samples
  of milk-based yogurts and puddings."
- **2016**: 114 milk-based infant food and formula samples tested; detected in 8. "Aflatoxin M1 was
  detected in 7 of the 63 samples of infant formula and in 1 sample of 6 samples of infant
  biscuits." Formula range 0.018-0.080 ppb; the biscuit 0.022 ppb. (Table 1 lists 86 milk-based
  formulas bought.)
- **2018-19**: "A total of 52 dairy infant formula samples were tested ... detected in 10 of the 52
  ... Levels ranged from 0.01 ppb to 0.086 ppb."
- **2020**: "None of the samples contained detectable levels of aflatoxin M1" (76 yogurts, yogurt
  beverages and puddings; Table 1: 36 puddings, 40 yogurts and yogurt beverages).
- **2022**: 93 samples (34 dairy infant formulas, 51 yogurts, 8 yogurt beverages); "Aflatoxin M1
  was detected in 1 sample of infant formula at 0.0566 ppb"; the other 92 had none.
- No page gives a detection limit for AFM1.

## What the census shows (names only)

All 16 open CFP files (2008-09 to 2023) were read. Six carry `Aflatoxin M1` rows. In every one,
the component column holds the single label `Aflatoxin M1`:

| Year | AFM1 rows | Samples | Unit | Product labels (samples) |
|---|---|---|---|---|
| 2012-13 | 101 | 101 | ng/g | Infant Formula - Milk 87; Infant Formula - Specialized 11 + Infant formula - Specialized 2; Infant Formula - Soy 1 |
| 2014-15 | 32 | 32 | **µg/g** | Infant Formula 22; Yogurt 6; Toddler snacks 4 |
| 2016 | 114 | 114 | ng/g | Infant Formula - Dairy 63; Yogurt 18; Infant Food (non-cereal) 15; Meal - Toddler/Baby 9; Infant Biscuit 6; Infant Food - Cereal 2; Pudding 1 |
| 2018 | 52 | 52 | ng/g | Infant Formula - Dairy 52 |
| 2020 | 152 | 76 | ng/g | rows: Pudding 72; Yogurt 58; Beverage - Yogurt 22 (two AFM1 rows per sample) |
| 2022 | 93 | 93 | ng/g | Yogurt 51; Infant Formula - Dairy 33; Beverage - Yogurt 8; Infant Formula - Other 1 |

SHA-256 (full hashes in the grader): 2012-13 `0b0ae681…2931`, 2014-15 `d2cfa733…f98f7da59`, 2016
`6a8b9c78…1cfdbe`, 2018 `be6a1d7c…bb4659755`, 2020 `e1c895c5…f91eb27b46`, 2022
`14d3712e…eb851c61`. Open Government Licence – Canada.

Already visible from the labels alone, before any value:

1. **2014-15's unit is µg/g**, 1000 times the ng/g (= ppb) of every other year. Read as µg/g, a
   printed 0.011 ppb would be stored as 0.000011.
2. **2014-15's products do not match the report.** The file has 22 formulas, 6 yogurts and 4
   toddler snacks. The report has 20 formulas and 12 yogurts and puddings.
3. **2016's AFM1 rows cover more than the report says.** 32 rows are infant foods, meals,
   biscuits and cereal, and the report names only formula, yogurt and biscuits. The 63 formulas
   match the report's results, not its Table 1 (86).
4. **2012-13 includes one soy formula**, though the report says milk-based and some specialized
   formulas were tested.
5. **2020 has two AFM1 rows per sample.** The 76 samples match the report. Halved, the row
   counts also match its Table 1: 36 puddings, and 35 imported, 32 domestic and 9 unspecified
   samples. That holds if both rows of a sample agree.
6. 2016, 2018 and 2020 hold an `Amount` column whose AFM1 entries are plain numbers (2020: only
   zeros), with at most 4 decimals and no text tokens. The census did not record the format of
   2012-13's, 2014-15's or 2022's `Result` column.

## Data and rules (fixed now)

- **Rows:** a row is AFM1 when its component cell names aflatoxin M1. Columns are found by
  header (`Sample No.`, `Component`, `Amount` or `Result`, `Unit` or `Report Unit`, `Product`,
  `Origin`).
- **Value rule:** a number above 0 is **detected**. A 0, a `<` followed by a number ≥ 0
  (including `<0`), or a not-detected token (`ND`, `n.d.`, `Not detected`, `<LOD`, `<MDL`,
  `<RL`, `BRL` and close variants) is **not detected**. Anything else (blank, `NA`, `NQ`, `BLQ`,
  `<LOQ`, `Trace`, other text, a negative) fails that year's gate.
- **Samples:** a sample is detected if any of its AFM1 rows is. Its value is the largest one.
- **Product classes:** *formula* if the product label contains "formula"; *dairy dessert* if it
  contains "yogurt" or "pudding"; *other* otherwise. Formula type: soy, specialized,
  milk/dairy, or other.
- **Units:** converted to ppb by a table only (ng/g ×1; µg/g ×1000). For 2014-15 the grader
  tries both readings against the printed range (see P2).
- **"Matches"** means the value rounds to the printed figure at its printed precision (for
  example 0.0795-0.0805 for "0.080", 0.005-0.015 for "0.01").

## Gate (G), per year

Each year is gated on its own. A year is graded only if its gate passes. The gate requires: the
SHA-256 matches; all five columns are found; the AFM1 rows, distinct samples, units and samples
per product class equal the census above; and every AFM1 result passes the value rule. A year
that fails is reported with the masked shape of every value that broke the rule (digits shown
as `#`). The overall G is met only if all six pass.

## Consistency checks against CFIA's printed figures (C1–C6)

- **C1 (2012-13):** exactly **12** of the 101 AFM1 samples are detected (the only count that
  rounds to 12% of 101; the share of the report's 148 is reported too), and none reaches 0.5 ppb.
- **C2 (2014-15):** **4** samples are detected, all formulas. No yogurt or toddler snack is
  detected.
- **C3 (2016):** **7** formulas, at a minimum matching 0.018 and a maximum matching 0.080 ppb, and
  exactly one other sample, an `Infant Biscuit`, matching 0.022 ppb. No yogurt or pudding.
- **C4 (2018):** **10** of 52, with the minimum matching 0.01 and the maximum 0.086 ppb.
- **C5 (2020):** **0** of 76.
- **C6 (2022):** **1** of 93, a formula, matching 0.0566 ppb.

## Blind predictions (P1–P5)

- **P1.** Every detected AFM1 value in the five ng/g years is below **0.1 ppb**, a fifth of the
  Codex level. Of the five, only 2012-13 has no printed maximum.
- **P2.** **The 2014-15 µg/g label is 1000× off.** The stored formula positives already match
  the printed 0.011–0.061 ppb, rather than matching it only after multiplying by 1000. The
  grader records both readings. If neither matches, P2 fails, and 2014-15 is left out of P5.
- **P3.** No AFM1 is detected in any yogurt, yogurt beverage or pudding in any graded year
  (6 + 19 + 76 + 59 = 160 samples if all four years pass). An upper 95% bound is reported.
- **P4.** In 2012-13, every detection is a milk-based formula. None of the 13 specialized
  formulas or the 1 soy formula is detected.
- **P5.** **Infant formula at a common 0.02 ppb cut** (above every printed minimum except
  2014-15's 0.011, 2016's 0.018 and 2018's 0.01): the 2022 detection rate (of 34) is below the
  pooled 2012-13–2018 rate. This compares point estimates. The one-sided Fisher exact p and
  Wilson 95% intervals are reported, and a non-significant gap will be called that, not "a fall".

## Also reported (not graded)

- Per year and class: samples, detections, the products detected, and the minimum and maximum.
- Formula per year at the 0.02 ppb cut, with Wilson 95% intervals.
- The 2014-15 and 2016 count gaps against the reports (22 vs 20 formulas; 63 vs 86).
- The per-sample table carries each sample's declared origin, but no origin comparison is
  registered.

## Outputs

- `cfp_afm1_trend_samples.csv`: one row per AFM1 sample (year, sample, product, class, formula
  type, origin, unit, rows, raw values, kind, stored value, unit factor).
- `cfp_afm1_trend_summary.json`: the gates, every check and prediction with observed values, the
  census and provenance.

The next run publishes these with a result note and a pinned recompute test that does not import
the grader.
