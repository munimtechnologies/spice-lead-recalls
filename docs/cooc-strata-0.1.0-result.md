# cooc-strata 0.1.0: is the ochratoxin A × DON co-occurrence a commodity effect? — result

RESULT-MARKER: cooc-strata-0.1.0-result

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This grades the pre-registration [cooc-strata-0.1.0-prereg.md](cooc-strata-0.1.0-prereg.md),
published first at tag `v0.4.58`. The sealed job `cooc-strata-v1` (2026-10-26 14:04 UTC,
python:3.12, 1 GB, no host paths) waited for that note to be public, checked that its bundled
`cooc_strata.py` and `test_cooc_strata.py` were byte-identical to the published copies, ran the
12 offline tests, and only then fetched the two committed per-sample tables from this
repository. **The gate passed and 4 of the 5 graded items held (G, M1, M3, M4). M2 missed.**

**Short answer: yes, mostly.** In both files, most of the pooled association comes from
comparing different commodities, not from what happens inside one. Within CFIA's retail
product labels the odds ratio falls from 8.54 to 1.40, and within feed ingredient names the
feed reversal shrinks from 0.70 to 0.90. Neither within-stratum estimate differs detectably from 1.

A statistical reading of two open CFIA files, not a finding about any product, feed, mill or
farm, and not a claim about whether particular lots were or were not co-infected.

## Data

- Retail: `data/myco_don_2010_samples.csv` (CFIA 2010-11 ochratoxin A and DON in selected foods,
  committed with [myco-don 0.1.0](myco-don-0.1.0-result.md)): 1,886 rows, 943 samples, each
  tested for both toxins. Stratum = CFIA's `product` label.
- Feed: `data/feed_myco_samples.csv` (CFIA livestock-feed monitoring 2000-2018, committed with
  [feed-myco 0.1.0](feed-myco-0.1.0-result.md)): 3,258 samples, 3,219 tested for both. Stratum =
  `ingredient_name` as written (blank = its own stratum; no merging, so `Wheat shorts` and
  `Wheat Shorts` stay separate, as registered).

## Gate (passed)

Retail 1,886 rows / 943 samples with pooled (OTA and DON, OTA only, DON only, neither) =
(275, 40, 280, 348); feed 3,258 samples with pooled (136, 60, 2,312, 711). All five checks matched.

## Graded predictions: 4 of 5 held (gate included)

| ID | Prediction | Observed | Met |
|---|---|---|---|
| G | gate (above) | all 5 checks | ✅ |
| M1 | retail within-product MH OR ≤ √8.54 = 2.92 | **1.40** | ✅ |
| **M2** | **retail: MH OR > 1 and CMH p < 0.05** | **MH 1.40, CMH p 0.38** | ❌ |
| M3 | feed within-ingredient MH OR in [0.5, 1.5], CMH p ≥ 0.05 | MH 0.90, CMH p 0.63 | ✅ |
| M4 | feed MH OR closer to 1 than pooled 0.70 | \|ln 0.90\| = 0.10 < \|ln 0.70\| = 0.36 | ✅ |

| | Pooled OR | Strata (informative) | Samples in informative strata | MH OR | CMH χ² (p) |
|---|---|---|---|---|---|
| Retail 2010-11, by product | 8.54 | 21 (8) | 517 of 943 | 1.40 | 0.77 (0.38) |
| Feed 2000-18, by ingredient name | 0.70 | 101 (14) | 2,867 of 3,219 | 0.90 | 0.23 (0.63) |

### Retail: 84% of the log odds ratio lies between products

ln 1.40 / ln 8.54 = 0.336 / 2.145, so about **84% of the pooled log odds ratio is between
products** and 16% within them. The pattern is simple. Grain foods carry both toxins often
(`Flour - Wheat`: 55 of 60 samples have both; `Cereal - Adult`: 107 of 162). Most non-grain foods
carry neither. Of the 348 "neither" samples, 299 are wine (136), dairy infant formula (88), figs
(28), dates (27), apricots (10) and raisins (10). A detected toxin of either kind therefore mostly
marks "this is a grain food".

The eight informative strata:

| Product | n | OTA&DON | OTA only | DON only | neither | OR |
|---|---|---|---|---|---|---|
| Cereal - Adult | 162 | 107 | 3 | 49 | 3 | 2.18 |
| Beer | 130 | 22 | 7 | 81 | 20 | 0.78 |
| Infant Food - Cereal | 93 | 23 | 3 | 53 | 14 | 2.03 |
| Chips - Corn | 58 | 6 | 1 | 49 | 2 | 0.24 |
| Cereal - Children | 34 | 12 | 0 | 21 | 1 | 1.74* |
| Cornmeal | 17 | 1 | 0 | 13 | 3 | 0.78* |
| Grain - Oat | 16 | 13 | 0 | 2 | 1 | 16.2* |
| Infant Formula - Soy | 7 | 1 | 2 | 0 | 4 | 5.4* |

\* Haldane-corrected (a zero cell); shown for description only. The MH estimate uses the raw cells.

**M2 missed.** The registered guess was that a positive association would survive within
products. The point estimate is positive (1.40), as are the two largest cereal strata (2.18 and
2.03), but beer and corn chips go the other way. The CMH test is far from significant (p 0.38).
The within-product data are thin: the informative strata hold only 16 "OTA only" samples. So
this does not show the within-product association is zero. It shows it is small at most: a
Robins-Breslow-Greenland 95% interval for the MH OR (computed after grading, not graded) is
**0.72 to 2.70**, which excludes the pooled 8.54.

### Feed: the reversal is mostly corn versus small grains

ln 0.90 / ln 0.70 = −0.102 / −0.361, so about **72% of the feed reversal is between ingredients**.
Corn is 40% of the feed samples tested for both toxins. It carries DON very often and OTA almost never.
The small grains carry OTA more often and DON less often:

| Ingredient | n | OTA detected | DON detected | within OR |
|---|---|---|---|---|
| Corn | 1,297 | 13 (1.0%) | 1,199 (92.4%) | 0.44 |
| Barley | 476 | 64 (13.4%) | 319 (67.0%) | 0.93 |
| (blank) | 356 | 41 (11.5%) | 277 (77.8%) | 1.20 |
| Wheat | 350 | 31 (8.9%) | 208 (59.4%) | 0.94 |
| Oats | 143 | 12 (8.4%) | 79 (55.2%) | 0.37 |

Pool these and an OTA-positive sample is more likely to be a small grain, so less likely to be
DON-positive. Inside barley and wheat (826 samples) the odds ratios are 0.93 and 0.94. The
Robins-Breslow-Greenland 95% interval for the feed MH OR (after grading, not graded) is
**0.64 to 1.28**.

### Sensitivity (reported, not graded): the answer depends on how fine the strata are

Stratified by CFIA's coarser `ingredient_type`, the feed MH OR is **0.64 with CMH p 0.0066**.
That is *further* from 1 than the pooled 0.70. The reason is the `Cereals` type (2,346
samples). It puts corn together with barley, wheat and oats, and its own odds ratio is 0.42
(82, 47, 1,788, 429). Stratify by type and you keep the composition effect. Stratify by
ingredient name and it goes away. Anyone stratifying grain mycotoxin data should split at least
corn from the small grains.

## What this settles, and what it does not

- The retail OR of 8.54 (myco-don P11) and the feed OR of 0.70 (feed-myco P5) are both mostly
  **composition**: which commodities carry which toxin. Neither is good evidence for or
  against co-infection of the same lot. The biology fits too: OTA comes mostly from storage moulds
  (*Penicillium verrucosum*, *Aspergillus*) and DON from field *Fusarium*.
- Within commodities, both files are compatible with no association. The retail interval
  (0.72–2.70) still allows a modest positive one.
- Limits: detections are binary at each file's own limits, which changed over time in the feed
  file (OTA 5 → 10 µg/kg in 2014-15; see feed-myco). Year is not a stratum here. CFIA's labels
  still mix grains (`Cereal - Adult`). The two files differ in era, matrix and method.

Prior art: searches on 2026-10-25 and 2026-10-26 found published OTA × DON co-occurrence figures
from food and feed surveys only as pooled counts or pooled correlations. We found none that
stratifies by commodity, and none that uses CFIA's open per-sample files. As far as we know, this
is the first within-commodity test of OTA × DON co-occurrence on a regulator's open per-sample data.

## Reproduce it

- `data/cooc_strata_retail.csv`, `data/cooc_strata_feed.csv`, `data/cooc_strata_feed_by_type.csv`:
  every stratum's 2×2 cells, odds ratio, Haldane flag and informative flag (sealed job output).
- `data/cooc_strata_summary.json`: the sealed grader record (gate, M1–M4, MH and CMH figures).
- `test_cooc_strata_result.py`: a pinned test. It rebuilds every stratum from the two committed
  per-sample tables with its own standard-library code, which does not import the grader. It then
  checks each table against the strata CSVs and the sealed record, and recomputes the MH odds ratios, CMH
  tests, between-stratum shares and Robins-Breslow-Greenland intervals quoted above.

A sealed follow-up job (`cooc-strata-result-v1`) fetches these published files from GitHub and
re-runs the pinned test on them. The grading code `cooc_strata.py` and the pre-registration are at
tag `v0.4.58`.
