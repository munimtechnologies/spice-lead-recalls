# don-grains-2015 0.1.0: CFIA's open 2015-16 deoxynivalenol file for grains, pseudo-cereals and pulses, and a second look at two CFIA methods — result

RESULT-MARKER: don-grains-2015-0.1.0-result

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This grades the pre-registration [don-grains-2015-0.1.0-prereg.md](don-grains-2015-0.1.0-prereg.md),
which was public first, at tag `v0.4.69`. The sealed job `don-grains-2015-v1` ran on 2026-10-28 at
01:53 UTC (python:3.12, 1 GB, no host paths). It waited for the registration's marker to be
public and checked that its bundled `don_grains_2015.py` and `test_don_grains_2015.py` were
byte-identical to the published copies. It ran the 13 offline tests and only then read the two
SHA-256-pinned files. **The gate passed, and 7 of 9 graded items held: C1 and five of seven blind
predictions. P1 missed by one sample, and P4 missed on its level.**

This is a reference comparison, not a compliance finding. Canada sets no DON maximum level for
these finished foods, and the EU levels quoted below did not apply anywhere in 2015-16. It is
not about any brand, and it is not dietary or medical advice. CFIA reports that the levels found
"were considered safe for consumption by Canadians and no product recalls were required".

## Headlines

1. **At a common cut, CFIA's two DON methods agree.** On the 18 product labels this file shares
   with CFIA's 2018-19 multi-mycotoxin file, the DON-only survey detects DON in 404 of 754
   samples (53.6%) and the multi-mycotoxin survey in 75 of 297 (25.3%): a within-label
   Mantel-Haenszel odds ratio of **6.44** (CMH p ≈ 4 × 10⁻²³; P6 held). Count only results at
   or above 10 ppb, the multi-mycotoxin method's limit of detection, and the DON-only survey has
   196 of 754 (26.0%). The odds ratio falls to **1.28** (CMH χ² 1.40, p 0.237; Robins-Breslow-
   Greenland 95% interval **0.87–1.90**, computed after grading), so P7 held. Unlike the OTA
   comparison, this interval is tight enough to rule out a two-fold gap.
2. **"46% detected" is a reporting-limit figure.** The file reproduces CFIA's summary page
   exactly (997 samples, 457 positive = 45.8%; C1 held). But 243 of the 457 positives (53%) are
   below 10 ppb, and the smallest is 0.412 ppb. Read at the multi-mycotoxin method's limit, the
   same survey detects DON in **214 of 997 (21%)**.
3. **The high results are rye, and all of them are Canadian or of unknown origin.** The four
   results above 2,000 ppb are all rye (5,720 and 4,690 ppb in `Grain - Rye`, 3,330 and 3,010
   in `Rye Products`). That breaks P4, which allowed a maximum below 2,000 ppb (it did land in a
   small-grain label, as predicted). Of the 30 small-grain samples at or above 400 ppb, 24 are
   `Domestic` (every `Domestic` sample is of Canadian origin) and 6 have unknown origin. **None
   of 119 imported small-grain samples reaches 400 ppb**; their maximum is 130 ppb
   (exploratory; Fisher two-sided p < 10⁻⁶ for 24 of 129 against 0 of 119).
4. **Where DON sits.** Small-grain cereals (barley, rye, kamut and spelt) are positive in 86.1%
   of 353 samples, 5.7 times the 15.1% of pseudo-cereals and arrowroot (P2 and P3 held). Pulses
   and soy are positive in **29 of 189** (15.3%). P1 allowed at most 28, so it missed by one
   sample, though no pulse result comes near 100 ppb (maximum 33.8).

## Data

- **DG:** CFIA, "CFIA 2015/2016 Deoxynivalenol in Selected Foods Data". Open Government Portal
  dataset `debeebfe-8e35-4914-8ad5-8432340e1e5a`, resource `90b59896-d874-4da5-9c03-580d7ee6c584`,
  SHA-256 `b662d980…4912d7` (201,445 bytes, UTF-8 with BOM), Open Government Licence – Canada.
  It has 997 rows, one DON result per sample, all in ng/g (= ppb). Non-detects are a literal 0
  (540 cells). Every other cell is a number above 0 (457 cells).
- **MM:** CFIA's 2018-19 multi-mycotoxin file, resource `09a3c285-8552-4a38-b4be-cdf6d5fc3fd2`,
  SHA-256 `ba508494…3835`. Only its 750 DON rows are used. Their 306 positives are all at or
  above 10 ppb.

## Gate (passed)

All 16 checks held. For DG: the SHA-256, 997 rows and samples with one DON row each, all 44
product-label counts, CANADA 254 and UNKNOWN 407, one known unit (`ng/g`), and only positive or
literal-0 cells (both present). For MM: the SHA-256, 18,750 rows, 750 DON rows, 306 positives with
a minimum of 10, known units, and exactly the 18 registered shared labels.

## Graded items: 7 of 9 held

| ID | Registered | Observed in the file | Met |
|---|---|---|---|
| G | gate (above) | 16 of 16 checks | ✅ |
| C1 | 997 samples, 46% detected (454–463 positives) | 997, 457 (45.8%) | ✅ |
| P1 | pulses and soy (189): at most 15% detected (≤ 28), none ≥ 100 ppb | **29** detected (15.3%), maximum 33.8 | ❌ |
| P2 | small grains ≥ 2 × as often positive as pseudo-cereals | 86.1% vs 15.1% (5.7 ×) | ✅ |
| P3 | ≥ 60% of the 353 small-grain samples positive | 304 (86.1%) | ✅ |
| P4 | file maximum in a small-grain label and < 2,000 ppb | `Grain - Rye`, **5,720** ppb | ❌ |
| P5 | of 802 grain-type samples, ≤ 16 at ≥ 750 ppb and ≤ 40 at ≥ 400 ppb | 9 and 30 | ✅ |
| P6 | 18 shared labels, own limits: MH OR ≥ 2, CMH p < 0.05, ≥ 25% of DG positives < 10 ppb | 6.44, p ≈ 4 × 10⁻²³, 208 of 404 (51.5%) | ✅ |
| P7 | 18 shared labels at 10 ppb: MH OR in [0.5, 2.0] | **1.28** | ✅ |

## By group

| group | n | positive | ≥ 10 ppb | ≥ 400 ppb | ≥ 750 ppb | median of positives | maximum |
|---|---|---|---|---|---|---|---|
| SG small grains | 353 | 304 (86.1%) | 188 | 30 | 9 | 17.25 | 5,720 |
| PS pseudo-cereals, arrowroot | 252 | 38 (15.1%) | 4 | 0 | 0 | 2.35 | 18.7 |
| OG other grains | 197 | 83 (42.1%) | 12 | 0 | 0 | 2.55 | 57.4 |
| PU pulses and soy | 189 | 29 (15.3%) | 8 | 0 | 0 | 2.41 | 33.8 |
| MA meat alternatives | 6 | 3 | 2 | 0 | 0 | 16.5 | 22.0 |
| **all** | **997** | **457 (45.8%)** | **214** | **30** | **9** | **7.8** | **5,720** |

- **P5 (EU reference levels).** All 9 grain-type samples at or above 750 ppb, and all 30 at or
  above 400 ppb, are small grains: 3 `Grain - Rye`, 2 `Rye Products`, 2 `Spelt`, 1
  `Spelt Products` and 1 `Grain - Barley` at 750. The labels do not say which EU row would apply
  to each sample, so these are threshold counts, not compliance verdicts.
- **P1's miss.** The 29 pulse and soy positives are spread over 16 of 23 labels: `Lentil` 5 of 8,
  `Infant Formula - Soy` 4 of 8 (1.55–13.3 ppb), `Bean - Kidney` 3 of 8, `Bean - Other` 3 of 12,
  `Flour - Soy` and `Soy Products` 2 of 8 each, and one each in ten others. Only 8 are at or
  above 10 ppb (4.2% of 189). The prediction was right about the levels and one sample wrong
  about the rate.
- **Pseudo-cereals.** `Arrowroot Products` (39) and `Quinoa Products` (37) have no DON at all;
  `Grain - Quinoa` 4 of 45 and `Amaranth Products` 3 of 41. `Buckwheat Products` is the
  exception at 22 of 46.

## P6 and P7: two CFIA methods, three crop years apart

| shared label | DON-only: n | detected | ≥ 10 ppb | multi-mycotoxin: n | detected (all ≥ 10) |
|---|---|---|---|---|---|
| `Amaranth Products` | 41 | 3 | 0 | 14 | 0 |
| `Arrowroot Products` | 39 | 0 | 0 | 15 | 0 |
| `Barley Products` | 46 | 39 | 19 | 14 | 3 |
| `Buckwheat Products` | 46 | 22 | 3 | 15 | 1 |
| `Grain - Barley` | 51 | 46 | 41 | 36 | 23 |
| `Grain - Buckwheat` | 44 | 9 | 1 | 14 | 2 |
| `Grain - Kamut` | 52 | 50 | 27 | 13 | 3 |
| `Grain - Other` | 45 | 18 | 3 | 15 | 1 |
| `Grain - Quinoa` | 45 | 4 | 0 | 28 | 1 |
| `Grain - Rye` | 44 | 36 | 22 | 2 | 1 |
| `Kamut Products` | 41 | 32 | 6 | 15 | 5 |
| `Millet` | 45 | 23 | 0 | 15 | 3 |
| `Millet Products` | 39 | 15 | 5 | 14 | 1 |
| `Quinoa Products` | 37 | 0 | 0 | 15 | 1 |
| `Rye Products` | 40 | 31 | 25 | 26 | 16 |
| `Spelt` | 44 | 38 | 23 | 5 | 2 |
| `Spelt Products` | 29 | 27 | 21 | 25 | 12 |
| `Teff Products` | 26 | 11 | 0 | 16 | 0 |
| **pooled** | **754** | **404 (53.6%)** | **196 (26.0%)** | **297** | **75 (25.3%)** |

- **At each method's own limit**, the odds ratio within labels is 6.44 (crude 3.42; CMH χ² 98.2).
  Of the 404 DON-only detections, 208 are below 10 ppb, where the multi-mycotoxin method reports
  nothing.
- **At the common 10 ppb cut**, the crude odds ratio is 1.04 and the within-label one 1.28
  (95% interval 0.87–1.90, p 0.237). The DON-only survey has more barley, kamut and spelt at the
  cut (for example, `Grain - Kamut` 27 of 52 against 3 of 13). The multi-mycotoxin survey has
  more millet and quinoa: `Millet` 0 of 45 (maximum 8.38 ppb) against 3 of 15, a single-label
  Fisher p of 0.013 that is one of 18 labels and chosen after seeing the table, so it is a lead,
  not a finding.
- **Next to OTA.** The [ota-grain-2018 result](ota-grain-2018-0.1.0-result.md) found the same
  pattern for ochratoxin A in one year: an own-limit odds ratio of 26.0 falling to 2.09 (0.86–5.08)
  at 0.8 ppb. For DON the cut removes the gap more cleanly, even across three crop years. CFIA's
  2015–2018 multi-mycotoxin report shows its own DON detection at 10 ppb moving from 27% (2015) to
  59% (2017), so crop-year weather alone could have opened a gap here, and it did not.
- **What this means for reading CFIA's surveys.** Detection rates from CFIA's single-toxin and
  multi-mycotoxin DON surveys are not comparable as printed. At 10 ppb they are, at least within
  the labels both cover. Neither public CFIA page gives this survey's own limit of detection; the
  file's smallest result is 0.412 ppb.

## Exploratory: small grains by origin

Found after grading. `Function` is CFIA's field; every `Domestic` sample has origin `CANADA`
(254 of 254).

| small grains | n | positive | ≥ 10 ppb | ≥ 400 ppb | ≥ 750 ppb | median of positives | maximum |
|---|---|---|---|---|---|---|---|
| Domestic (Canada) | 129 | 124 (96.1%) | 106 | 24 | 8 | 76.25 | 5,720 |
| Import | 119 | 97 (81.5%) | 41 | 0 | 0 | 6.6 | 130 |
| Unknown | 105 | 83 (79.0%) | 41 | 6 | 1 | 9.5 | 3,010 |

The median DON in Canadian small grains is more than ten times that of imported ones, and no
imported small grain reaches 400 ppb. The labels are not spread evenly across origins, so part of
this may be which grains were bought where, and the file has no crop year. This note does not test
why.

## Limits

- Detection is binary at each survey's own limit, and the DON-only survey's limit is not public.
  The 10 ppb cut is the multi-mycotoxin method's listed limit of detection and its smallest
  result.
- The two surveys are three crop years apart, and the shared labels hold different products
  bought by different samplers. Stratifying by label removes label-level differences, not
  within-label ones. P7 holding shows that the open data find no gap at 10 ppb. It does not show
  the methods are identical above it.
- The origin comparison is exploratory and confounded by product mix.
- This note does not say why any sample is high. Only CFIA can say more about its samples.

Prior art: on 2026-10-28, searches for analyses of this open file, and for a comparison of CFIA's
single-toxin and multi-mycotoxin DON detection, found none. CFIA's 2015–2018 multi-mycotoxin
report compares earlier DON surveys in its Table 5, but has no row for this one. As far as we know,
this is the first per-sample reading of the file and the first per-label comparison of the two
methods' DON detection at a common cut.

## Reproduce it

- `data/don_grains_2015_samples.csv`: one row per sample (sample, product, group, origin,
  function, detected, DON in ng/g), the sealed job's output.
- `data/don_grains_2015_crossmethod.csv`: per shared label, n, detected and at or above 10 ppb in
  DG, and n and detected in MM.
- `data/don_grains_2015_summary.json`: the sealed grader record (gate, census, every check and
  prediction with its observed values, per-label and per-group statistics, the cross-method
  tables, provenance).
- `test_don_grains_2015_result.py`: a pinned test. It does not import the grader. With its own
  code it rebuilds the groups, C1, P1–P7, the cross-method tables and the Mantel-Haenszel, CMH,
  Robins-Breslow-Greenland and Fisher figures from the two CSVs, and checks them against the
  sealed record.

A sealed follow-up job (`don-grains-2015-result-v1`) fetches these published files from GitHub
and re-runs the pinned test on them. The grading code `don_grains_2015.py` and the
pre-registration are at tag `v0.4.69`.
