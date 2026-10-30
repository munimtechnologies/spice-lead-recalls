# cfp-afm1-trend 0.1.0: aflatoxin M1 in six open CFIA Children's Food Project files (2012-13 to 2022) against every figure CFIA printed — result

RESULT-MARKER: cfp-afm1-trend-0.1.0-result

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This grades the pre-registration [cfp-afm1-trend-0.1.0-prereg.md](cfp-afm1-trend-0.1.0-prereg.md),
which was public first, at tag `v0.4.77`. The sealed job `cfp-afm1-trend-v1` ran on 2026-10-29 at
23:49 UTC (python:3.12, 2 GB, no host paths). It waited for the registration's marker to be
public, checked that its bundled `cfp_afm1_trend.py` and `test_cfp_afm1_trend.py` were
byte-identical to the published copies, ran the offline tests and only then read the six
SHA-256-pinned files. **All six per-year gates passed, and 10 of 12 graded items held: the gate,
all six consistency checks and three of five blind predictions.**

This is a reproducibility check of open government data, not a compliance finding and not about
any brand. Canada sets no maximum level for aflatoxin M1 (AFM1) in milk products; CFIA uses the
Codex level of 0.5 ppb for milk as a reference, and Health Canada judged every level reported
"not of concern". The values are for products as sampled (formula mostly as powder), not as fed.
It is not dietary or medical advice.

## Headlines

1. **The open files reproduce every AFM1 figure CFIA printed (C1–C6, 6 of 6).** 2012-13: 12 of
   101 samples detected (CFIA: "12%"); 2014-15: 4 formulas, nothing else; 2016: 7 of 63 formulas
   at 0.0184–0.0795 ppb plus one infant biscuit at 0.0217; 2018: 10 of 52 at 0.010–0.086; 2020:
   0 of 76 dairy desserts; 2022: 1 of 93, an infant formula at 0.0566 ppb. In all, 35 of 468
   samples carried a detectable AFM1 result, the highest 0.136 ppb.
2. **The 2014-15 file's `µg/g` unit label is 1000 times off (P2 held).** Its four formula
   positives are stored as 0.011, 0.022, 0.052 and 0.061, exactly the report's "0.011 ppb to
   0.061 ppb", so the numbers are already ppb (ng/g). Read as labelled, the top value would be
   61 ppb, about 120 times the Codex 0.5 ppb. Every other year is labelled `ng/g`. Anyone pooling
   the open files by their unit column would get 2014-15 wrong by three orders of magnitude.
3. **The highest values are two 2012-13 milk-based formulas at 0.13 and 0.136 ppb (P1 missed).**
   The 2012-13 report printed no range, only "12%" and "below the Codex 0.5 ppb". We predicted
   every value would be below 0.1 ppb; these two are not. Both are still under a third of the
   Codex level, and they are powder values.
4. **Three of the twelve 2012-13 detections are specialized formulas (P4 missed):** 0.021, 0.023
   and 0.055 ppb, against 9 of 87 milk-based formulas. The one soy formula was not detected.
5. **No AFM1 in any of 160 yogurts, yogurt beverages and puddings across four years (P3 held);**
   upper 95% (Wilson) bound 2.3%.
6. **Formula at a common 0.02 ppb cut (P5 held as a point estimate, not a significant fall).**
   2012-13 to 2018 pooled: 28 of 238 (11.8%, 95% interval 8.3–16.5%); 2022: 1 of 34 (2.9%,
   0.5–14.9%). One-sided Fisher exact p = 0.094. The 2022 rate is lower, but this sample cannot
   tell a real decline from chance.

## Gate (passed in all six years)

Per year: the SHA-256; all five columns found by header; AFM1 rows, distinct samples, units and
samples per product class equal to the names-only census; and every AFM1 result either a number
above 0 (detected) or 0 (not detected). No `<` values, tokens or blanks occurred, so no
`bad_shapes` were recorded. 2020 holds two AFM1 rows per sample (152 rows, 76 samples), and in
every 2020 sample both rows are 0.

## Graded items: 10 of 12 held

| ID | Registered | Observed in the files | Met |
|---|---|---|---|
| G | per-year gate, all six years | 6 of 6 years pass | ✅ |
| C1 | 2012-13: 12 of 101 detected (12%), all < 0.5 ppb | 12 of 101 (11.9%), max 0.136 | ✅ |
| C2 | 2014-15: 4 formulas, nothing else | 4 formulas; 0 of 6 yogurts, 0 of 4 snacks | ✅ |
| C3 | 2016: 7 formulas at 0.018–0.080; 1 infant biscuit at 0.022 | 7 at 0.0184–0.0795; biscuit 0.0217 | ✅ |
| C4 | 2018: 10 of 52 at 0.01–0.086 | 10 of 52 at 0.010–0.086 | ✅ |
| C5 | 2020: 0 of 76 | 0 of 76 | ✅ |
| C6 | 2022: 1 of 93, a formula at 0.0566 | 1 of 93, formula 0.0566 | ✅ |
| P1 | every detected value in the ng/g years < 0.1 ppb | max 0.136 (2012-13) | ❌ |
| P2 | 2014-15 `µg/g` label 1000× off | stored 0.011–0.061 = printed ppb | ✅ |
| P3 | no AFM1 in any yogurt or pudding | 0 of 160 | ✅ |
| P4 | 2012-13 detections only in milk-based formula | 9 milk + 3 specialized | ❌ |
| P5 | formula ≥ 0.02 ppb: 2022 rate below pooled 2012-13–2018 | 2.9% vs 11.8% (p = 0.094) | ✅ |

## Per year

| Year | Samples | Detected | Formula detected | Range detected (ppb) | Unit label |
|---|---|---|---|---|---|
| 2012-13 | 101 | 12 | 12 of 101 | 0.010–0.136 | ng/g |
| 2014-15 | 32 | 4 | 4 of 22 | 0.011–0.061 | µg/g (should be ng/g) |
| 2016 | 114 | 8 | 7 of 63 | 0.0184–0.0795 (biscuit 0.0217) | ng/g |
| 2018 | 52 | 10 | 10 of 52 | 0.010–0.086 | ng/g |
| 2020 | 76 | 0 | no formula tested | — | ng/g |
| 2022 | 93 | 1 | 1 of 34 | 0.0566 | ng/g |

## Exploratory, not registered: every formula detection with a declared origin is from the United States

The per-sample table carries each sample's declared origin. The pre-registration said no origin
comparison was registered, so this is a pattern noticed after grading, reported as a hypothesis
only. Of the 272 formula samples, 195 are declared `UNITED STATES`, 50 another country (Ireland,
Switzerland, Canada, the Netherlands) and 27 `UNKNOWN`. AFM1 was detected in **30 of the 195
U.S.-origin formulas (15.4%)**, **0 of the 50 others** and 4 of the 27 unknown. A one-sided Fisher
exact test of 0 of 50 against 30 of 195 gives p ≈ 0.0006; within 2012-13 alone (12 of 69 against
0 of 32) p ≈ 0.007. Strong caveats: the comparison was chosen after seeing the data; samples of
the same product line are not independent, so the real evidence is weaker than these p-values
suggest; "origin" is the declared country of the product, not of the milk; and every value is far
below the Codex reference. A fresh, pre-registered test on independent data (another CFIA or
Health Canada AFM1 survey) would be needed before calling this a finding.

## Limits

- "Detected" is each file's own coding (a number above 0). No page or file gives an AFM1 limit of
  detection, so years with different limits are compared only at the common 0.02 ppb cut (P5).
- The samples CSV's `unit_factor_to_ppb` column shows the factor implied by each row's unit
  label (1000 for 2014-15's `µg/g`). Following P2, the analysis used 1 for 2014-15 (see
  `analysis.ppb_factor` in the summary).
- 2016's AFM1 rows include 32 infant foods, meals, biscuits and cereals that the report's text
  does not list; only the biscuit was detected. 2014-15's file has 22 formulas and 10 other
  samples where the report says 20 formulas and 12 yogurts and puddings.
- Values are on the product as sampled. Powdered formula is diluted when prepared, so as-fed
  levels are lower; no as-fed comparison is made, and no comparison with the EU's 0.025 µg/kg
  level for infant formula (which applies to the ready-to-use product) is attempted.

Prior art: on 2026-10-29, searches found CFIA's yearly reports, the open datasets and news
summaries of single years. They found no multi-year rebuild of the AFM1 series from the open
files, no check of the files against the printed figures, and no note of the 2014-15 unit label.

## Reproduce it

- `data/cfp_afm1_trend_samples.csv`: one row per AFM1 sample (year, sample, product, class,
  formula type, origin, unit, rows, raw values, kind, stored value, label factor), the sealed
  job's output.
- `data/cfp_afm1_trend_summary.json`: the sealed grader record (gates, every check and
  prediction with observed values, the census and provenance).
- `test_cfp_afm1_trend_result.py`: a pinned test. It does not import the grader. With its own
  code it rebuilds the per-year counts, C1–C6, P1–P5 (Wilson intervals and the Fisher p from
  scratch) and the exploratory origin table from the CSV, and checks them against the sealed
  record.

A sealed follow-up job (`cfp-afm1-trend-result-v1`) fetches these published files from GitHub
and re-runs the pinned test on them. The grading code `cfp_afm1_trend.py` and the
pre-registration are at tag `v0.4.77`.
