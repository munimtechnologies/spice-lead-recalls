# feed-myco 0.1.0: CFIA's open livestock-feed mycotoxin file (2000-2018) against its own report — result

RESULT-MARKER: feed-myco-0.1.0-result

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This grades the blind pre-registration [feed-myco-0.1.0-prereg.md](feed-myco-0.1.0-prereg.md),
published first at tag `v0.4.56`. The sealed job `feed-myco-v1` (2026-10-26 08:28 UTC,
python:3.12, 1 GB, no host paths) waited for that note to be public, made its bundled modules
equal the published copies, ran the offline tests, and only then read the SHA-256-pinned CFIA
file. **The gate passed and 17 of the 21 graded items held: all 7 consistency checks against
CFIA's report, and 9 of the 13 blind predictions (S1, P1–P12).** The four misses (P2, P5, P9,
P10) are reported in full below; one of them (P5) is the most informative result of the study.

A reference comparison, not a compliance finding about any feed, mill, farm or brand, and not
veterinary advice. CFIA's action levels apply to an animal's total diet; most samples here are
single ingredients.

## Data

CFIA, "Mycotoxin Monitoring Program for Livestock Feeds – Results from April 1, 2000 – March 31,
2018" (Open Government Licence – Canada), dataset `2d636f59-5f04-4725-afae-376850bc71d4`, English
CSV resource `b8cad53e-0a93-4366-a764-246fbc980c1f`, SHA-256
`6de28d69d6d2fe0552aae55720b2b481b6673efafbcccf90dc87f7002a2c1491` (5,872,784 bytes, UTF-8 with
BOM): 40,862 results on 3,258 samples, 17 analytes. The report is CFIA's "National feed
inspection program: results for Program-15B (April 1, 1990 – March 31, 2018)".

## Gate (passed)

SHA-256, the 10 headers, 40,862 rows, 3,258 samples, units {mg/kg 32,019, µg/kg 8,843}, the 18
mycotoxin labels with their row counts, and the result format {35,368 censored `<x`, 5,494
numbers} all matched the names-only census. No row failed to parse, no label or unit was
unknown, and every `<` cell carries a numeric limit (S1).

## Consistency checks against the report: 7 of 7 held

| ID | Check | Observed | Met |
|---|---|---|---|
| C1 | file n = Table 1 n in ≥ 107 of 108 cells (DON, T-2, DAS, FUM, OTA, ZEA) | 107; the one miss is FUM 2016-17 (file 163, report 164) | ✅ |
| C2 | file HT-2 n = report's T-2 n in ≥ 17 of 18 years | 18 of 18 | ✅ |
| C3 | DON n and "% below 1 ppm" reproduced in ≥ 16 of 18 years | 18 of 18 | ✅ |
| C4 | T-2, DAS, FUM, OTA, ZEA n and % below the lowest AL in ≥ 85 of 90 cells | 89 of 90 (the same FUM 2016-17 cell) | ✅ |
| C5 | HT-2: rows the report leaves out = non-detects with a limit above 0.1 ppm, every year | exact in all 18 years (2, 15, 11, 13 in 2010-11 … 2013-14; 0 elsewhere) | ✅ |
| C6 | HT-2 n and "% below 0.1 ppm" match once those rows are dropped, ≥ 16 of 18 | 18 of 18 | ✅ |
| C7 | no aflatoxin result above 20 ppb | 0 | ✅ |

**Every 2000-2018 cell of the report's Table 1 rebuilds from the open file.** That is 126
percentages and their sample counts. Two facts explain the only places where a naive rebuild
disagrees:

- **HT-2 (C5, the registered mechanism).** The report prints 3,202 HT-2 samples; the file holds
  3,243. The 41 extra rows are, year by year and exactly, the HT-2 non-detects whose
  quantification limit was **0.5 ppm**. That is above the 0.1 ppm HT-2 action level, so such a
  result can be neither "below 0.1 ppm" nor above it. The report leaves them out without
  saying so. Drop them and all 18 HT-2 cells match to the printed two decimals (C6). The same
  0.5 ppm limit appears for every trichothecene in those samples (2, 15, 11 and 13 of them), so
  it is a matrix-specific limit, not a data error. The report keeps the matching T-2 rows,
  correctly, because 0.5 ppm is below T-2's 1 ppm action level.
- **Fumonisins 2016-17 (the C1/C4 miss).** One row in the file has a **blank fiscal year**: a
  fumonisin non-detect (`<0.30` mg/kg) on sample `2016FED-0000067789-4`, a sample the file
  otherwise dates 2016-2017 (it is the only sample whose rows disagree on year or province).
  Put that row in 2016-17 and the cell becomes 164 samples with 161
  below 1 ppm = 98.17%, which is exactly what the report prints. (Found after grading: the
  pre-registration allowed one cell of slack for this row but did not predict where it
  belonged.)

From the report alone (in the pre-registration, unchanged): the file is the report's last 18 of
28 years (2,211 of its 5,449 DON samples, 1990-2000, have no open record), and the report's text
quotes Table 1's DON figure as 81.3% where the table prints 82.22%.

## Blind predictions: 9 of 13 held

| ID | Prediction (abbreviated) | Observed | Met |
|---|---|---|---|
| S1 | every `<` result carries a numeric limit | 35,368 of 35,368 | ✅ |
| P1 | DON is the most frequently detected analyte | DON 75.9%; then fumonisins 37.0%, 15-ADON 28.3% | ✅ |
| **P2** | **DON detected in 35–75% of its results** | **2,457 of 3,238 = 75.9%** | ❌ |
| P3 | DON × zearalenone odds ratio ≥ 3, p < 0.001 | OR 59.4, p 3.1×10⁻³⁸ (3,227 samples) | ✅ |
| P4 | DON × 15-acetyl-DON odds ratio ≥ 10, p < 0.001 | OR 464, p 5.2×10⁻¹³¹ (3,238 samples) | ✅ |
| **P5** | **OTA × DON odds ratio > 1, p < 0.05 (replicating myco-don)** | **OR 0.70, p 0.030: reversed** | ❌ |
| P6 | 15-ADON detected in more samples than 3-ADON | 918 vs 174 | ✅ |
| P7 | 3-ADON share of acetyl-DON-positive samples higher West than East, p < 0.05 | West 14 of 36 (38.9%), East 160 of 966 (16.6%), p 0.0024 | ✅ |
| P8 | that share higher in 2009-10 … 2017-18 than in 2000-01 … 2008-09 | 17.4% vs 17.3% (p 1.0): met only nominally | ✅ |
| **P9** | **fumonisins detected ≥ 3× as often in corn as in other named ingredients** | **40.3% vs 17.2% (2.3×)** | ❌ |
| **P10** | **modal DON limit lower in 2014-18 than in 2000-04** | **0.1 ppm in both** | ❌ |
| P11 | modal HT-2 limit 0.1 ppm every year to 2012-13, below 0.1 later | 0.1 to 2013-14; 0.015 from 2014-15 | ✅ |
| P12 | aflatoxin B1 detected in ≤ 5% of its results | 7 of 699 (1.0%) | ✅ |

### The reversal: ochratoxin A and DON in feed (P5)

In CFIA's 2010-11 retail-food file, a sample with detected ochratoxin A was far more likely to
carry detected DON (myco-don 0.1.0: OR 8.54, p 1.4×10⁻³⁹). That note warned that much of the
signal was probably commodity composition: grain foods carry both toxins, while wine and dried
fruit carry OTA without DON. P5 registered that the association would replicate in feed. It
does not. It reverses:

| | DON detected | DON not detected | total |
|---|---|---|---|
| **OTA detected** | 136 | 60 | 196 |
| **OTA not detected** | 2,312 | 711 | 3,023 |
| **total** | 2,448 | 771 | 3,219 |

Odds ratio **0.70**, two-sided Fisher exact **p = 0.030**. In a file made almost entirely of
cereal and grain-derived ingredients, an OTA-positive sample is slightly *less* likely to be
DON-positive (69.4% vs 76.5%). This supports the composition reading of the retail result. The
retail OR of 8.54 does not show that the same lots are co-infected; it shows which foods carry
grain. The biology fits: OTA comes mostly from storage moulds and DON from field *Fusarium*.
Limits: these are detections at the file's limits, not concentrations, and the effect is modest
(p 0.03, one test). A within-ingredient analysis is the obvious next step.

### The chemotype proxy (P6–P8)

15-acetyl-DON was detected in 918 samples and 3-acetyl-DON in 174 (P6). Among samples with any
acetyl-DON, the 3-ADON share was **38.9% in samples taken in Alberta, British Columbia, Manitoba
and Saskatchewan** and 16.6% elsewhere (P7, p 0.0024). That fits field surveys showing the
3-ADON chemotype rising in western Canadian wheat from the late 1990s (e.g. Ward et al. 2008).
Two caveats. The western group is small (36 samples), because this program sampled mostly in
Quebec and Ontario. And "Sampled at – Province" is where the feed was sampled, not where the
grain grew. P8 is met only on a point estimate (17.40% vs 17.32%). The data show **no
change** in the 3-ADON share between the two nine-year periods. As far as we found, this is
the first 3-ADON/15-ADON split drawn from a regulator's feed-monitoring records. It is a
chemical proxy, not a genotype.

### The other misses

- **P2:** DON was detected in 75.9% of results, just above the registered 35–75% band.
- **P9:** fumonisins were detected 2.3× as often in corn-named ingredients (579 of 1,436) as in
  other named ingredients (37 of 215), short of the registered 3×.
- **P10:** the most common DON limit stayed at 0.1 ppm. The late period adds a tail of higher
  limits (27 results at 0.12 ppm in 2017-18, 11 at 0.5 ppm in 2013-17) rather than a lower mode.

## Exploratory, not pre-registered: three "trends" that are method changes

This was found after grading, while reading the committed limit table
(`data/feed_myco_limits.csv`, as far as we know the first open history of this program's
quantification limits). Each sharp change in a detection rate in this file falls in the same
year as a change in that analyte's limit. Analytes with a stable limit show no such step.

| Analyte | Limit change | Detected before | Detected after |
|---|---|---|---|
| T-2 | 0.1 → 0.01 ppm in 2014-15 | 49 of 2,544 (1.9%), 2000-01 … 2013-14 | 178 of 699 (25.5%), 2014-15 … 2017-18 |
| HT-2 | 0.1 → 0.015 ppm in 2014-15 | 113 of 2,544 (4.4%) | 241 of 699 (34.5%) |
| Ochratoxin A | 5 → 10 µg/kg in 2014-15 | 179 of 2,542 (7.0%) | 17 of 698 (2.4%) |
| Fumonisins | 0.1 → 0.3 ppm in 2016-17 | 589 of 1,322 (44.6%), 2000-01 … 2015-16 | 30 of 350 (8.6%), 2016-17 … 2017-18 |
| DON (control) | modal 0.1 ppm to 2016-17 (0.12 in 2017-18) | 1,932 of 2,535 (76.2%), to 2013-14 | 525 of 703 (74.7%), from 2014-15 |
| Zearalenone (control) | modal 0.1 ppm every year | 249 of 2,541 (9.8%) | 83 of 699 (11.9%) |

Read naively, the open file says T-2 detections rose thirteen-fold in 2014 and fumonisins fell
five-fold in 2016. Neither is evidence about the feed supply. They track the method. (For
fumonisins the number and mix of samples tested also changed in 2016-17, from 85 to 163, so
the method is not the only change.) The report notes that the HT-2 limit "was 0.1 ppm until
recently". It does not show what the limit changes do to detection rates. Anyone trending this
file should stratify by limit, or count only results above the highest limit in use.

## Reproduce it

- `data/feed_myco_table1.csv`: all 126 Table 1 cells, with the printed and rebuilt n and %,
  the at-or-below variant and the indeterminate counts.
- `data/feed_myco_samples.csv`: one row per sample (3,258): descriptors, DON ppm and a detection
  flag per analyte (blank = not tested). Every co-occurrence and chemotype figure above is
  recomputed from it.
- `data/feed_myco_limits.csv`: censoring limits by analyte and year.
- `data/feed_myco_cooccurrence.json`: the committed 2×2 tables, odds ratios and Fisher p.
- `data/feed_myco_summary.json`: the full sealed grader record (gate, every prediction,
  per-analyte per-year detection counts, units by year, provenance).
- `test_feed_myco_result.py`: a pinned test. It rebuilds C1–C6 and the fumonisin
  reconciliation from the Table 1 CSV, P10, P11 and the method-change table from the limit
  CSV and the sealed per-year counts, and the P3–P8 tables with their odds ratios and Fisher
  p-values from the per-sample CSV. Each is checked against this note and the committed
  JSON. Row-level figures (P1, P2, P9, P12) are read from the sealed record, because a few
  samples carry two fumonisin rows.

A sealed follow-up job (`feed-myco-result-v1`) fetches these published files from GitHub and
re-runs the pinned test on them. Grading code `feed_myco.py` and the pre-registration are at
tag `v0.4.56`.
