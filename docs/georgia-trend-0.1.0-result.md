# Did lead in spices bought in Georgia fall after 2020? Result of georgia-trend 0.1.0

By MV2 of Munim, Inc. Prepared with AI agents. Text CC BY 4.0; code Apache-2.0.

**Status:** graded against [the pre-registration](georgia-trend-0.1.0-prereg.md), which
was committed (in release v0.4.1) before any NYC result was split by year within a
purchase country. Every prediction is reported, met or not. Sections 4 and 5 report the
figures the pre-registration listed as "reported without prediction", plus checks added
after grading. They grade nothing.

## 1. What ran

`georgia_trend.py` 0.1.0 reads only the committed snapshot
`data/nyc_spice_lead_snapshot_2026-10-17.csv` (NYC DOHMH *Metal Content of Consumer
Products*, `da9u-wz3r`, Food-Spice lead) through `purchase_place.tagged_rows` 0.1.0,
unchanged. It keeps case-investigation results (frame C) collected in 2016–2025 and
splits them into **early** (2016–2020) and **late** (2021–2025). "Georgia-bought" means
`purchase_country` is exactly `GEORGIA` (the country). The tables are
`data/georgia_trend.csv` and `data/georgia_trend_by_year.csv`.

`test_georgia_trend.py` recomputes both tables offline. It checks that early plus late
equals the published 2016–2025 rows of `data/purchase_place.csv`, and that Georgia,
Bangladesh and the other abroad countries add up to the abroad group. Every count was
also tallied independently by pattern-matching the snapshot. One 2019 US-bought case row
is a fish sauce reported in mg/l, not ppm, so it is excluded, exactly as in earlier
releases.

## 2. The five predictions

| Purchase place (C results) | Early 2016–2020 | ≥ 50 ppm | Late 2021–2025 | ≥ 50 ppm |
|---|---:|---:|---:|---:|
| Georgia | 141 | 49 (34.8%) | 16 | 0 (0%) |
| Bangladesh (control) | 239 | 18 (7.5%) | 159 | 3 (1.9%) |
| All abroad | 697 | 89 (12.8%) | 421 | 9 (2.1%) |

| # | Prediction | Observed | Verdict |
|---|---|---|---|
| — | Both Georgia periods have at least 15 results | 141 and 16 | gradable |
| P1 | Georgia-bought share ≥ 50 ppm lower late than early | 0% vs 34.8% | met |
| P2 | Late share at most half the early share | 0 ≤ 17.4% | met |
| P3 | Fisher two-sided p < 0.05, Georgia early vs late, ≥ 50 ppm | p ≈ 0.003 | met |
| P4 | **Control:** Bangladesh-bought early vs late at ≥ 50 ppm, Fisher p ≥ 0.05 | 7.5% → 1.9%, p ≈ 0.01–0.02 | **failed** |
| P5 | Georgia-bought results a smaller fraction of C-abroad late than early | 3.8% vs 20.2% | met |

**4 of 5 met, and the one that failed is the control.** The test pins the P3 p value
between 0.001 and 0.01 (hand calculation: 0.0030) and the P4 p value between 0.008 and
0.05. They are not quoted to more digits.

## 3. What it means

**Gross contamination in Georgia-bought spices did disappear from NYC case
investigations.** Before 2021, a third of Georgia-bought results were at or above
50 ppm, and some reached 10,000–78,000 ppm. From 2021 to 2025 none of 16 reached 50 ppm.
Only one reached 2 ppm (3.5 ppm, a ground spice mix), against 85 of 141 early (60%,
Fisher p < 0.001). Georgia-bought results also became rare: about 28 a year before 2021,
about 3 a year after, and none in 2023 or 2025.

**But this data cannot credit that fall to anything specific to Georgia.** The control
failed. Bangladesh-bought gross contamination fell too, from 7.5% to 1.9%, and the last
Bangladesh-bought result at or above 50 ppm was in May 2022. So did everything else.
Spices bought in all other foreign countries fell from 6.9% to 2.4% at 50 ppm (22 of 317
to 6 of 246; Fisher p between 0.002 and 0.1). US-bought results fell from 9 of 406 to 0
of 365 (p ≈ 0.004). Low-level lead in US-bought spices did not change: 6.2% vs 5.5% at
2 ppm (p > 0.3).

The Bangladesh control was a poor choice, and that was knowable before the data. Forsyth
et al. 2023 (*Environ Res* 232:116328) document a 2019 food-safety enforcement campaign in
Bangladesh that cut lead chromate adulteration in turmeric there. So Bangladesh was not
an untreated country. Two readings fit the numbers. Both are consistent with the
literature, and this data cannot separate them:

1. **Source-country action worked in both places.** In Georgia, Forsyth et al. 2024
   (*Environ Res* 250:118504) measured spice lead falling sharply across 29 cities from
   2020 to 2022. In Bangladesh, enforcement began in 2019.
2. **Case-investigation practice or case mix changed citywide after 2020.** A drop in
   every purchase group at 50 ppm, including spices bought in the US, fits that too.

What the NYC open data does show cleanly is that the extreme Georgia-bought results
(hundreds to tens of thousands of ppm) stopped after 2020, and so did the Georgia-bought
cases themselves.

## 4. Reported without prediction

**By year** (C results, then results ≥ 50 ppm; `data/georgia_trend_by_year.csv`):

| Year | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Georgia | 17 / 6 | 57 / 23 | 11 / 3 | 48 / 12 | 8 / 5 | 3 / 0 | 10 / 0 | 0 / 0 | 3 / 0 | 0 / 0 |
| Bangladesh | 26 / 4 | 14 / 2 | 15 / 1 | 160 / 9 | 24 / 2 | 32 / 2 | 34 / 1 | 38 / 0 | 19 / 0 | 36 / 0 |

**At 2 ppm:** Georgia-bought 60.3% early vs 6.3% late; Bangladesh-bought 20.1% vs 9.4%;
all abroad 25.7% vs 9.7%; US-bought 6.2% vs 5.5%.

## 5. Check added after grading: collection dates

One household visit can add many rows on one day, and every p value above treats rows as
independent. As a rough correction, each distinct collection date is treated as one
investigation. It is a proxy only: two homes can share a date, and one home can span two.
Georgia-bought results come from 44 dates early and 4 dates late (2021-03-28, 2022-02-18,
2022-12-02, 2024-06-05). On 30 of the 44 early dates at least one spice reached 50 ppm;
on none of the 4 late dates did. Fisher two-sided p = 3060/194580 ≈ 0.016, exact and pinned
in the test. The Georgia drop survives this correction, but it rests on 4 late visits.

## 6. Prior art and what is new

The fall itself is not new. NYC's Health Department reported its findings to Georgian
authorities and issued a multilingual advisory. Forsyth et al. 2024 measured spice lead
falling in Georgia's own markets from 2020 to 2022. A Pure Earth summary and NYC's
investigators have described a steep decline in elevated blood lead among NYC children of
Georgian ancestry. We have not checked those NYC figures against a primary source.

What this note adds is narrower. It is a pre-registered, fully reproducible test on
NYC's open laboratory table. It shows the Georgia-bought decline in case-investigation
spices, with exact counts by year. It also shows that the decline is not specific to
Georgia in that table: a control registered in advance, and every other purchase group,
fell too. Anyone citing NYC's open data as evidence that a Georgia-specific intervention
worked should know that this data alone cannot separate it from a citywide shift. We found
no earlier published analysis that tests the NYC open table this way.

## 7. Limits

- Case investigations are triggered by poisoned residents. Fewer Georgia-bought results
  can mean fewer cases (the intervention working) or a change in who gets investigated
  and what gets sampled. This note cannot tell which.
- The late Georgia period has 16 results from 4 collection dates. A 0% share there is
  compatible with a true late rate of up to about 20% of results (one-sided 97.5% bound
  for 0 of 16 is 20.6%), and dates are a crude proxy for households.
- `purchase_country` is self-reported in a home interview.
- The 2020/2021 cut was fixed before the data. It is not the date of any one
  intervention, and 2020 itself had only 8 Georgia-bought results.
