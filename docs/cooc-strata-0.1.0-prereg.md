# Pre-registration: is the ochratoxin A × DON co-occurrence a commodity effect? (cooc-strata 0.1.0)

PREREG-MARKER: cooc-strata-0.1.0-prereg

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

Two per-sample tables already published in this repository give opposite pooled answers to one
question: when a sample carries detected ochratoxin A (OTA), is it more likely to carry detected
deoxynivalenol (DON)?

- **Retail foods** (CFIA 2010-11; [myco-don 0.1.0](myco-don-0.1.0-result.md),
  `data/myco_don_2010_samples.csv`, 943 samples): yes, strongly. 2×2 table (OTA and DON, OTA
  only, DON only, neither) = (275, 40, 280, 348); odds ratio **8.54**.
- **Livestock feeds** (CFIA 2000-2018; [feed-myco 0.1.0](feed-myco-0.1.0-result.md),
  `data/feed_myco_samples.csv`, 3,219 samples tested for both) = (136, 60, 2,312, 711); odds
  ratio **0.70**, p 0.030.

Both notes said the pooled figure probably reflects which commodities carry which toxin
(composition), not that the same lot was infected by both. OTA comes mostly from storage moulds
and DON from field *Fusarium*. This note tests that directly, before the test is run.
Mantel-Haenszel (MH) odds ratios and Cochran-Mantel-Haenszel (CMH) tests are computed **within
commodity strata**: CFIA's `product` label for retail (e.g. `Flour - Wheat`, `Wine`,
`Infant Food - Cereal`) and the ingredient common name for feed (e.g. `Corn`, `Barley`).

**What has and has not been seen.** The pooled tables above, some per-product DON facts from
myco-don (no DON in 139 wines or 97 dried-fruit samples; 76 of 93 infant cereals with DON), and
the feed file's fumonisin-by-corn split. **No within-stratum OTA × DON table has been computed
for either file.** The public commit timestamp of this note fixes the predictions before the
sealed job `cooc-strata-v1` computes one.

## Data and rules

- The job fetches the two committed CSVs from this repository's `main` branch after this note is
  public. **Gate** (facts already published): the retail table has 1,886 rows and 943 samples
  with the pooled table (275, 40, 280, 348); the feed table has 3,258 samples with the pooled
  table (136, 60, 2,312, 711). If any gate check fails, nothing is graded.
- **Detection** = the committed `detected` flag (retail) or `det_OTA` / `det_DON` (feed; blank =
  not tested, excluded). A sample counts only if tested for both toxins.
- **Strata:** retail = the sample's `product` value; feed = `ingredient_name` (blank → its own
  stratum). Each stratum is used as written, with no merging.
- **MH odds ratio** = Σ(a·d/n) / Σ(b·c/n) over strata. **CMH** = (|Σ(a − E[a])| − 0.5)² / Σ
  Var(a), 1 df, continuity-corrected. A stratum with one sample or a constant margin adds
  nothing. Code: `cooc_strata.py`. Offline tests, including a constructed Simpson's-paradox
  case, are in `test_cooc_strata.py`.

## Predictions (graded)

- **M1** Retail: the within-product MH odds ratio is **at most √8.54 = 2.92**, so more than half of
  the pooled log odds ratio lies *between* products. *Why:* grain foods carry both toxins
  and wine and dried fruit carry OTA without DON. Those differences alone could make a large
  pooled OR.
- **M2** Retail: a positive association **remains** within products (MH OR > 1 and CMH p < 0.05).
  *Why:* within a grain product, lots stored badly after a wet harvest can carry both. This is a
  genuine guess. M1 and M2 can both hold.
- **M3** Feed: within ingredients the MH odds ratio lies in **[0.5, 1.5]** with CMH **p ≥ 0.05**
  (no detectable within-ingredient association).
- **M4** Feed: the within-ingredient MH odds ratio is **closer to 1** than the pooled 0.70
  (|ln MH| < |ln 0.70|), i.e. stratifying by ingredient removes part of the reversal.

## Reported, not graded

Per-stratum tables (`cooc_strata_retail.csv`, `cooc_strata_feed.csv`) with each stratum's
odds ratio (Haldane-corrected where a cell is zero). The number of informative strata. A
sensitivity analysis on the feed file stratified by the coarser `ingredient_type`
(`cooc_strata_feed_by_type.csv`).

## Limits stated up front

Detections are binary at each file's own limits, not concentrations. CFIA's product labels mix
grains (`Cereal - Adult`), so composition can remain inside a stratum. Feed samples carry no
grain-origin field. The two files differ in era, matrix and method, so neither MH estimate is a
causal claim about co-infection. As far as searches on 2026-10-25 and 2026-10-26 found,
published OTA × DON co-occurrence figures from feed or food surveys are pooled, and none
stratifies CFIA's open data by commodity. Not a finding about any product, feed, mill or farm.
