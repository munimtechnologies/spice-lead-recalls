# Pre-registration: lead in six open CFIA Children's Food Project files (2017 to 2022) against every lead figure CFIA printed, and against the U.S. FDA's 2025 baby-food action levels (cfp-lead 0.1.0)

PREREG-MARKER: cfp-lead-0.1.0-prereg

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code
Apache-2.0.

**Written before any lead result value in these files was read.** The figures below come from
CFIA's report pages (re-read 2026-10-30) and from a names-only census of the open files (job
`cfp-metals-census-v1`, 2026-10-30). The census records file hashes, headers, labels, units,
row counts and the *format* of the result column (numbers or zeros, how many decimals), but
never a lead value or a count of detections.

The grading code is `cfp_lead.py`, and its offline tests are `test_cfp_lead.py`. A sealed compute
job (`cfp-lead-v1`) grades this registration only after it is public on GitHub. The job checks
out the published code and then reads the SHA-256-pinned files.

Nothing here is a finding about any product, brand or health risk. Health Canada reviewed every
CFP metal result and found none a safety concern. Canada's maximum levels for lead cover fruit
juice (0.05 ppm) and infant formula (0.01 ppm as consumed); the other products tested have none.
The U.S. FDA levels used below are non-binding U.S. guidance, used only as a reference scale.

## Why this is new

On 2026-10-29, searches found CFIA's yearly reports, the open datasets, and reviews of single
report pages (one discusses the 2021 report's text). They found no per-sample, multi-year
analysis of the CFP lead data, no check of the open files against the printed lead tables, no
note that the 2021 table's 0.18 ppm meal maximum conflicts with the same report's text and
mean, and no comparison of these Canadian samples with the FDA's 2025 action levels.

## What CFIA printed (ppm; tested / negative / positive / max / mean)

- **2017** juice: 51 / 49 / 2 / 0.009 / 0.000. Table note: "Average of positive results only."
  Text: "2 samples of juice (3.9%) had low levels of lead. All levels were below the maximum
  level of 0.05 ppm."
- **2018-19**: puree 38 / 38 / 0; dairy formula 52 / 49 / 3 / 0.019 / 0.02; soy formula 7 / 7 / 0;
  toddler/baby meal 11 / 11 / 0; pasta 35 / 34 / 1 / 0.03 / 0.03. Text: "Three of the 59 infant
  formula samples contained levels of lead ranging from 0.016 to 0.019 ppm"; "One sample of
  dried pasta contained a level of 0.03 ppm."
- **2019**: yogurt beverage 11 / 11 / 0; infant cereal 48 / 37 / 11 / 0.093 / 0.01; puree
  98 / 97 / 1 / 0.015 / 0.0002; snack 78 / 71 / 7 / 0.04 / 0.0025; yogurt 16 / 16 / 0. Text: "7.6%
  (19 samples)".
- **2020**: children's cereal 50 / 47 / 3 / 0.10 / 0.003; fruit snack 20 / 19 / 1 / 0.03 / 0.001;
  granola/cereal bar 29 / 28 / 1 / 0.03 / 0.001; pudding 36 / 36 / 0. Text: "96.3% (130 samples)
  ... did not contain detected levels of lead."
- **2021**: fruit and vegetable puree 124 / 123 / 1 / 0.02 / 0; infant and toddler meals
  53 / 51 / 2 / **0.18** / 0.001; canned and dry pasta 47 / 44 / 3 / 0.05 / 0.002; juice
  67 / 67 / 0. Text: "97.9% (285 samples)" not detected; "Detected levels of lead ranged from
  0.015 to 0.047 ppm with the highest levels in canned and dry pasta."
- **2022**: infant cereals 39 / 16 / 23, minimum detected 0.0050, max 0.0211, mean 0.0089;
  infant/children's snacks 69 / 28 / 41, minimum 0.0050 (printed "00050"), max 0.196, mean
  0.0152. Notes: "Minimum detected amount", "Average of detected amounts". Text: "44 samples
  (41%) did not contain detectable levels of lead"; "ranged from 0.0050 ppm to 0.196 ppm", the
  highest "in a gluten free cracker product".

Already visible from the printed figures alone, before any value:

1. **The 2021 meal maximum (0.18) cannot be right.** The text puts the top detected value at
   0.047, in pasta. The table's own meal mean, 0.001 over 53 samples, bounds the two meal
   positives' sum below 0.0795, which a 0.18 cannot fit. The likely reading is 0.018.
2. **The means follow different conventions.** 2018-19 (dairy formula: three positives of
   0.016-0.019 print a mean of 0.02, where an all-sample mean would be about 0.001) and 2022 (by
   its note) average the positives only. 2019 (puree: one positive
   at 0.015, mean 0.0002) averages all samples. 2017's note says positives only, but two
   positives up to 0.009 cannot average 0.000; only an all-sample mean prints that.
3. **The reporting limit fell in 2022.** The smallest detected value is 0.015-0.016 ppm in the
   2018-19 and 2021 texts and 0.0050 in 2022, when lead detection jumped from 2-8% of samples to
   59%. 2017's juice maximum (0.009) is also below 0.015.

## What the census shows (names only)

Every file has one lead row per sample, component label `Lead`, unit `µg/g` (= ppm), and a
result column holding only numbers and zeros (no `<`, no text). Product labels per year, mapped
to the report's product types before any value was read:

| Year | Lead rows | Product labels → report type |
|---|---|---|
| 2017 | 51 | Juice - Toddler/Infant 51 → juice |
| 2018 | 143 | Infant Formula - Dairy 52; Infant Food - Puree 38; Pasta - Dry 19 + Pasta - Canned 16 → pasta 35; Meal - Toddler/Baby 11; Infant Formula - Soy 7 |
| 2019 | 251 | Infant Food - Puree 98; Infant Food - Snack 78; Infant Food - Cereal 48; Yogurt 16; Beverage - Yogurt 11 |
| 2020 | 135 | Cereal - Children 48 + Oatmeal 2 → children's cereal 50; Pudding 36; Granola/Cereal Bar 29; Fruit Snacks 16 + Raisin 4 → fruit snack 20 |
| 2021 | 291 | Infant Food - Puree 159 + Fruit Purée 11 + Fruit & Vegetable Purée 2 + Meal - Toddler/Baby 5 → **puree and meals together, 177**; Pasta - Dry 36 + Pasta - Canned 11 → pasta 47; eight juice and fruit-beverage labels → juice 67 |
| 2022 | 108 | Infant Food - Cereal 39; Crackers 25 + Cookies 23 + Infant Food - Snack 14 + Granola/Cereal Bar 5 + Baking Mixes 2 → snacks 69 |

Every mapped total equals the printed "tested" count. **2021's file cannot reproduce the report's
puree/meal split:** the report has 124 purees and 53 meals, the file labels only 5 samples as
meals. The two are graded together (177 tested, 174 negative, 3 positive). The 2023 file also
carries lead (105 rows), but CFIA has not posted a 2023 report, so it is not graded here.

SHA-256 (full hashes in the grader): 2017 `6fe317c9…4c87e7`, 2018 `be6a1d7c…bb4659755`, 2019
`6b5b7019…94cbce2`, 2020 `e1c895c5…f91eb27b46`, 2021 `5364b9cd…aa7f1c544`, 2022
`14d3712e…eb851c61`. Open Government Licence – Canada.

## Rules (fixed now)

- **Rows:** a row is lead when its component cell is `Lead` (or `Plomb`). Columns are found by
  header (`Sample No.`, `Component`, `Amount` or `Result`, `Unit` or `Report Unit`, `Product`).
- **Value rule:** a number above 0 is **detected**; 0, a `<` with a number ≥ 0, or a
  not-detected token is **not detected**; anything else fails that year's gate.
- **"Matches"** means the value rounds to the printed figure at its printed precision (for
  example 0.045-0.055 for "0.05", 0.00015-0.00025 for "0.0002").
- **Means:** "all-sample" = the sum of detected values over all samples in the row;
  "positives-only" = the same sum over the detected samples.

## Gate (G), per year

Each year is gated on its own: the SHA-256; all five columns found; lead rows and distinct
samples equal to the census; unit `µg/g` on every row; samples per product label equal to the
census; and every result passing the value rule. A year that fails is reported with the masked
shape of every value that broke the rule. G is met only if all six pass.

## Consistency checks (C2017–C2022)

For each year, every printed table row reproduces: tested, negative and positive counts, and
(where there are positives) the maximum at printed precision. 2021's puree and meals are
checked as one row (177 / 174 / 3), without a maximum. Plus the printed text figures:

- **C2018:** formulas (dairy + soy) 3 of 59 detected, the smallest matching 0.016 and the
  largest 0.019.
- **C2019:** 19 of 251 detected.
- **C2020:** 130 of 135 not detected.
- **C2021:** 285 of 291 not detected; the smallest detected value matches 0.015 and the largest
  0.047, and the largest is a pasta.
- **C2022:** 44 of 108 not detected; overall range matches 0.0050–0.196, with the largest a
  `Crackers` sample; both rows' smallest detected value matches 0.0050.

## Blind predictions (P1–P6)

- **P1.** 2021: the appendix's 0.18 ppm meal maximum is not in the file. The largest puree/meal
  value is below 0.05 ppm, and no 2021 value rounds to 0.18.
- **P2.** 2021: one of the three puree/meal positives rounds to **0.018** ppm (0.18 with its
  decimal point moved).
- **P3.** The smallest detected lead value is at least **0.010 ppm** in each of 2018, 2019, 2020
  and 2021 (2022's printed 0.0050 is checked in C2022). If it holds, no file before 2022 shows
  any lead value between 0 and 10 ppb.
- **P4.** FDA dry-infant-cereal action level (20 ppb = 0.020 ppm): **at least 6 of the 48** 2019
  infant cereals, and **1 to 3 of the 39** 2022 infant cereals, are above it.
- **P5.** Each printed mean with positives (12 rows; 2021's split puree/meal rows excluded) is
  reproduced by the predicted convention: **all-sample in 2017, 2019, 2020 and 2021;
  positives-only in 2018-19 and 2022**. 2017 is predicted against its own table note.
- **P6.** Infant cereal at a common **0.015 ppm** cut: the 2022 detection rate is below 2019's.
  Point estimates; the one-sided Fisher exact p and Wilson 95% intervals are reported, and a
  non-significant gap will be called that.

## Also reported (not graded)

- **FDA reference table:** for each sample group the FDA levels plausibly cover (purees 2018,
  2019, 2021; 2018 meals; 2019 yogurt; 2020 pudding: 10 ppb; 2019 and 2022 infant cereals:
  20 ppb), the count above the level with a Wilson 95% interval; for purees also the count above
  20 ppb (the level for single-ingredient root vegetables, which the file cannot identify). We
  will say plainly that before 2022 a "not detected" lead result (reporting limit about 15 ppb)
  **cannot show that a puree, meal, yogurt or pudding was under the 10 ppb level**. Caveats:
  these are Canadian samples tested as sold; FDA's levels cover packaged food for children under
  two, so children's yogurts and puddings may fall outside them; the guidance sets no levels for
  snacks, infant formula or juice, which are left out.
- Snacks at the common 0.015 ppm cut, 2019 against 2022, with Fisher p.
- Per year and product type: samples, detections, minimum, maximum and both means.
- The per-sample table carries each sample's declared origin and function (import or domestic),
  but no origin comparison is registered.

## Outputs

- `cfp_lead_samples.csv`: one row per lead sample (year, sample, product, report type, origin,
  function, unit, rows, raw value, kind, value in ppm).
- `cfp_lead_summary.json`: the gates, every check and prediction with observed values, the FDA
  table, the census and provenance.

The next run publishes these with a result note and a pinned recompute test that does not import
the grader.

Published with this registration: `data/cfp_component_catalogue.csv` (CC BY 4.0), the census's
list of every component in all 16 open CFP files (2008-09 to 2023) with its row count and units
per year. It holds names and counts only, no result values, and is meant as a finding aid for
anyone working with these files.
