# purchase-recording 0.1.0: since 2023, most NYC spice lead records lack a purchase country

By MV2 of Munim, Inc. Prepared with AI agents. Text CC BY 4.0; code Apache-2.0.

**Status:** a descriptive robustness check of
[georgia-trend 0.1.0](georgia-trend-0.1.0-result.md). It is **not pre-registered** and
grades no predictions. It was done after the georgia-trend result was published, to ask
whether that result depends on how purchase country was recorded. Code:
`purchase_recording.py`. Data: `data/purchase_recording_by_year.csv`. Test:
`test_purchase_recording.py` recomputes every figure here from the committed snapshot
`data/nyc_spice_lead_snapshot_2026-10-17.csv`.

## What changed in the records

NYC case-investigation spice results (frame C) whose purchase country is blank,
"UNKNOWN OR NOT STATED" or "UNITED STATES MINOR OUTLYING ISLANDS" (the `unknown` group
of purchase-place 0.1.0), by collection year:

| Year | Results | No purchase country | Share | Results ≥ 50 ppm | of which no purchase country |
|---|---|---|---|---|---|
| 2016 | 107 | 4 | 3.7% | 20 | 1 |
| 2017 | 135 | 7 | 5.2% | 28 | 0 |
| 2018 | 120 | 2 | 1.7% | 7 | 0 |
| 2019 | 684 | 42 | 6.1% | 30 | 0 |
| 2020 | 113 | 1 | 0.9% | 14 | 0 |
| 2021 | 150 | 16 | 10.7% | 3 | 1 |
| 2022 | 196 | 34 | 17.3% | 2 | 0 |
| 2023 | 375 | 224 | 59.7% | 5 | 4 |
| 2024 | 334 | 151 | 45.2% | 6 | 4 |
| 2025 | 231 | 75 | 32.5% | 2 | 0 |

- 2016–2020: 56 of 1,159 results (4.8%) lack a purchase country. 2021–2025: 500 of
  1,286 (38.9%).
- Among results ≥ 50 ppm: 1 of 99 lacked one in 2016–2020, against 9 of 18 in 2021–2025
  (exact two-sided Fisher p ≈ 5 × 10⁻⁸). The nine come from six collection dates
  (2021-04-06, 2023-05-03, 2023-09-05, 2023-10-20, 2024-05-08, 2024-06-24).
- For all nine, the country of manufacture is also unrecorded.

We do not know why recording changed. The open table does not say. It could be a change
in forms, in data entry, or in which cases were investigated.

## What it does to the georgia-trend result

Each claim is re-checked with the unrecorded results placed where they hurt it most.

1. **The citywide fall holds.** Without any purchase split, case results ≥ 50 ppm fell
   from 99 of 1,159 (8.5%) in 2016–2020 to 18 of 1,286 (1.4%) in 2021–2025
   (p < 10⁻¹⁰). Recording cannot explain this.
2. **The fall in spices bought abroad holds.** Assign all 500 late unrecorded results to
   "bought abroad" and none of the early ones. Abroad results ≥ 50 ppm then go from
   89 of 697 (12.8%) to 18 of 921 (2.0%), p < 10⁻¹⁰.
3. **The Georgia-specific fall does not hold up as a share.** georgia-trend reported
   Georgia-bought results ≥ 50 ppm falling from 49 of 141 to 0 of 16 (P1–P3). If the
   nine unrecorded late results ≥ 50 ppm had been bought in Georgia, the late share
   would be 9 of 25 (36%), slightly above the early 34.8%. As a **count**, Georgia-bought
   gross results still fell from 49 in 2016–2020 to between 0 and 9 in 2021–2025, at
   least a five-fold drop. P5 (Georgia's falling fraction of abroad results) cannot be
   separated from the recording change at all.

So georgia-trend's own conclusion stands and gets stronger. Gross contamination fell
across the board, and the open table cannot credit the fall to Georgia. Its Georgia
share tests (P1–P3) carry an extra caveat: they assume that a missing purchase country
is unrelated to where the spice was bought.

## Why it matters for screening

From 2023 on, half of NYC's gross case results, and most results overall, can no longer
be traced to where the spice was bought. Purchase place was the strongest marker of
gross contamination in this table (purchase-place 0.1.0: 8.8% ≥ 50 ppm if bought abroad,
1.2% if bought in the US). Recording it on every home visit costs one question. See
[ask-where-bought.md](ask-where-bought.md).

## Limits

- Descriptive and done after the result it checks. It is reported as such.
- "Unknown" lumps blank, "UNKNOWN OR NOT STATED" and US Minor Outlying Islands, as
  purchase-place 0.1.0 does. Of the 556 such C rows in 2016–2025, one (2019) is US Minor
  Outlying Islands, none is blank, and the rest say UNKNOWN OR NOT STATED.
- Results are not households, and one investigation can add many rows on one date.
