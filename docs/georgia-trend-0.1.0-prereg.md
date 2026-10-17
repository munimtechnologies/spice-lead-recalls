# Pre-registration: did lead in spices bought in Georgia fall after 2020? (georgia-trend 0.1.0)

By MV2 of Munim, Inc. Prepared with AI agents. Text CC BY 4.0; code Apache-2.0.

**Status:** written and committed **before** any NYC result was split by year within a
purchase country. What has been seen is stated here. The 2016–2025 totals for
Georgia-bought case results (157 results, 49 ≥ 50 ppm, 86 ≥ 2 ppm) and for Bangladesh
(398, 21 ≥ 50 ppm) are published in
[purchase-place-0.1.0-result.md](purchase-place-0.1.0-result.md). Twelve individual
Georgia-bought rows from January to May 2016 were seen while checking that "GEORGIA"
means the country. No count by year or by period was made. The code will be written
after this file is public. It will read only the committed snapshot
`data/nyc_spice_lead_snapshot_2026-10-17.csv` through `purchase_place.tagged_rows`.

## Question

NYC's Health Department issued a multilingual advisory on Georgian spices, reported its
findings to Georgian authorities, and surveyed local shops (CDC success story, NYC
advisory). If that work, or action in Georgia, reduced gross contamination, then spices
bought in Georgia and tested in NYC case investigations should reach 50 ppm less often
in 2021–2025 than in 2016–2020.

## Rows and definitions (fixed now)

- Rows: `purchase_place.tagged_rows` with frame C (case investigation) and collection year
  2016–2025. Periods: **early** = 2016–2020, **late** = 2021–2025.
- Georgia-bought: `purchase_country` is exactly `GEORGIA` after strip and upper-case.
  Bangladesh-bought: exactly `BANGLADESH`. Abroad: the `abroad` group of purchase_place 0.1.0.
- Shares are among results. A non-detect counts as below every threshold. Thresholds are
  inclusive (≥).

## Predictions

- **P1:** The Georgia-bought share ≥ 50 ppm is lower late than early.
- **P2:** The late share is at most half the early share.
- **P3:** Exact two-sided Fisher p < 0.05 for Georgia-bought early vs late at ≥ 50 ppm.
- **P4 (control):** For Bangladesh-bought results, early vs late at ≥ 50 ppm, Fisher
  p ≥ 0.05 (no detectable change).
- **P5:** Georgia-bought results are a smaller fraction of all C-abroad results late than
  early.

If either Georgia period has fewer than 15 results, P1–P3 are reported as **not
gradable** rather than met or failed.

Reported without prediction: Georgia-bought and Bangladesh-bought counts by year, shares
≥ 2 ppm in both periods, and the same split for C-US.

## Limits known now

- Case investigations are triggered by poisoned residents, so a fall in Georgia-bought
  testing could reflect fewer cases, a different case mix, or changed sampling practice,
  not cleaner spices.
- Results are not products or households. One home can add several rows in one day.
- A period split is coarse, and the cut at 2020/2021 is a choice made now, before the
  data, not the date of any single intervention.
