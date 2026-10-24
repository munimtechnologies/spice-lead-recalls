<!-- RESULT-MARKER: coumarin-tea-replication-0.1.1-result -->
# coumarin-tea-replication 0.1.1: result (a verification, not a blind test)

By MV2 of Munim, Inc. Made with AI agents working in MV2's name. Code Apache-2.0; this note and
the tables CC BY 4.0. Data: CFIA 2013-14, 2014-15 and 2015-16 coumarin targeted surveys (Open
Government Licence - Canada). A bounded per-cup exposure screen on open data. Canada sets no
coumarin limit for food, so this is **not a compliance finding**, not a statement about any brand,
and not individual dietary or medical advice.

Grades the [0.1.0 pre-registration](coumarin-tea-replication-0.1.0-prereg.md) as amended by
[0.1.1](coumarin-tea-replication-0.1.1-amendment.md).

## Status, up front

**This is a verification, not a blind test.** The ten predictions were written before any 2014-15
or 2015-16 tea value was read, and they are graded exactly as registered. But the first sealed job
stopped at its parse gate after printing every observed value, because CFIA's 2014-15 report
mislabels its tea average (see the amendment and the companion
[table audit](coumarin-cfia-table-audit-0.1.0-result.md)). The gate was then amended and the
predictions re-graded. Anyone reading the 0.1.0 output could already see that all ten would hold,
which is why the amendment, published before the re-grade, labels it a verification. Read the
10 of 10 below in that light.

## Headline

The per-cup screen of [coumarin-tea 0.1.0](coumarin-tea-0.1.0-result.md) (2013-14, 115 teas)
**replicates in CFIA's two later surveys** (507 new teas):

- **No tea in any of the three surveys** (622 teas) puts a 60 kg adult over the whole-day coumarin
  tolerable daily intake (TDI) in one standard 2 g cup, even at a 100% leaf-to-cup transfer ceiling.
  The highest cup reaches 81% (2013-14), 64% (2014-15) and 74% (2015-16) of the adult day budget.
- A 15 kg child's standard 2 g cup crosses the child TDI less often in both later surveys:
  **13.3%** (28 of 210, 2014-15) and **13.8%** (41 of 297, 2015-16), against **28.7%** (33 of 115)
  in 2013-14.
- **Herbal teas carry the exceedances.** Pooled over the three surveys, 90 of the 102 child
  standard-cup exceedances (88%) are CFIA "Tea - Herbal" samples: 90 of 218 herbal teas (41.3%)
  against 12 of 404 of every other type (3.0%). In 2015-16 the herbal median (392 mg/kg) is the
  highest of the six types.

## How it was graded

Sealed compute job `coumarin-cfia-audit-v1` (2026-10-24 08:02-08:03 UTC, `python:3.12`, no host
paths): `check_prereg.py` confirmed the amendment and the audit pre-registration were public with
their markers and that every module the job ran equals the published copy; the offline tests
passed; then `coumarin_tea_replication.py` 0.1.1 read the three SHA-256-pinned CFIA files
(2013-14 `3c8a18c0…3f4f`, 2014-15 `e418443d…ec1e`, 2015-16 `45208635…d30c`) through the published
`coumarin_eu_limits.py` 0.1.1 parser and graded. A tea is a row whose Product is exactly one of
CFIA's six labels (`Tea - Black/Green/Herbal/Oolong/White/Other`). Unit census of all 622 tea rows:
`ug/g` (= mg/kg). Re-selecting the 2013-14 teas by the same rule reproduces the published
coumarin-tea counts exactly (115 teas; 0 / 7 / 33 / 45 over the TDI).

## Gate and predictions

| | prediction (as registered; G0 as amended) | observed | grade |
|---|---|---|---|
| G0 (gate) | per later survey: measured rows, exact tea count and six-type census, units all ug/g, tea max, detected count, and CFIA's printed average in its registered band (2014-15 now vs the all-sample mean) | 2014-15: 739 rows, 210 teas, census exact, max 1,920, detected 178, all-sample mean 301.9 (CFIA 302). 2015-16: 747 rows, 297 teas, census exact, max 2,230, detected 245, positives mean 441.6 (CFIA 442) | **pass** (14 of 14 checks) |
| P1 | no later-survey tea over an adult's TDI in a standard 2 g cup | 0 of 210; 0 of 297 | met |
| P2 (primary) | child 2 g cup: share over the TDI lower in each later survey than 2013-14's 0.287 | 0.133; 0.138 | met |
| P3 | 2014-15 child 2 g share in [0.04, 0.22] | 28 / 210 = 0.133 | met |
| P4 | 2015-16 child 2 g share in [0.10, 0.32] | 41 / 297 = 0.138 | met |
| P5 | 2014-15 child 4 g share in [0.12, 0.40] | 54 / 210 = 0.257 | met |
| P6 | 2015-16 child 4 g share in [0.18, 0.45] | 97 / 297 = 0.327 | met |
| P7 | 2014-15 adult 4 g: count over the TDI in [1, 12] | 5 | met |
| P8 | 2015-16 adult 4 g: count over the TDI in [2, 30] | 14 | met |
| P9 | child 2 g share higher in 2015-16 than in 2014-15 | 0.138 > 0.133 (41/297 vs 28/210) | met, narrowly |
| P10 | in 2015-16, Tea - Herbal has the strictly highest median of the six types | Herbal 392 > Other 320 > Oolong 198.5 > Black 184 > Green 147 > White 23.65 | met |

**10 of 10 met; every prediction carries `"blind": false`.** P9 is a near-tie (a difference of
0.5 percentage points) and should not be read as a trend.

## Per-survey and pooled tables

Coumarin in one cup (mg) = concentration (mg/kg) × dry tea per cup (kg) × transfer (fixed at 1.0).
"Over" means strictly above the concentration at which one cup delivers the drinker's whole-day
budget (EFSA TDI 0.1 mg/kg bw/day: 6 mg for a 60 kg adult, 1.5 mg for a 15 kg child). Thresholds:
A1 adult 2 g 3,000 mg/kg; A2 adult 4 g 1,500; C1 child 2 g 750; C2 child 4 g 375. Non-detects
count as 0.

| teas | n | detected | median | mean | mean of detected | p90 | max | A1 | A2 | C1 | C2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2013-14 | 115 | 114 | 240 | 495.7 | 500.0 | 1,420 | 2,430 | 0 | 7 | 33 (28.7%) | 45 (39.1%) |
| 2014-15 | 210 | 178 | 124 | 301.9 | 356.2 | 944 | 1,920 | 0 | 5 | 28 (13.3%) | 54 (25.7%) |
| 2015-16 | 297 | 245 | 191 | 364.3 | 441.6 | 1,180 | 2,230 | 0 | 14 | 41 (13.8%) | 97 (32.7%) |
| later two | 507 | 423 | 172 | 338.5 | 405.7 | 1,030 | 2,230 | 0 | 19 | 69 (13.6%) | 151 (29.8%) |
| all three | 622 | 537 | 180.5 | 367.5 | 425.7 | 1,130 | 2,430 | 0 | 26 (4.2%) | 102 (16.4%) | 196 (31.5%) |

Concentrations in mg/kg; p90 is the nearest-rank 90th percentile. Across all 622 teas the median
standard adult cup gives 6.0% of the adult day budget, and the most coumarin-rich tea 81%.

**By type** (`data/coumarin_tea_replication_by_type.csv`), pooled over the three surveys:

| type | n | C1 over | A2 over |
|---|---|---|---|
| Tea - Herbal | 218 | 90 (41.3%) | 24 |
| all other types | 404 | 12 (3.0%) | 2 |

The twelve non-herbal child standard-cup exceedances are 4 black and 1 "other" tea in 2014-15 and
3 black, 2 oolong and 2 "other" teas in 2015-16; none in 2013-14.

## Data and test

- `data/coumarin_tea_replication_samples.csv`: all 622 tea rows (survey, CFIA tea type, region,
  declared origin, mg/kg, % of each drinker's day budget under A1-C2, the four over-TDI flags, unit).
- `data/coumarin_tea_replication_by_type.csv`: 17 survey × type rows.
- `test_coumarin_tea_replication_result.py` recomputes every number in this note from those two
  files (and the measured-row counts from `data/coumarin_cfia_table_audit.csv`) with plain `csv`,
  `math`, `statistics` and `unittest`, and re-grades G0 and P1-P10.

## What the misread average changed

The 0.1.0 reasoning scaled the 2013-14 distribution by the ratio of positives means and took
CFIA's printed 302 as the 2014-15 positives mean (0.60× of 2013-14's 500); the true ratio is
356 / 500 = 0.71×. The 2014-15 bands were therefore centred somewhat low. They were not re-centred,
and all three 2014-15 band predictions (P3, P5, P7) still held.

## Limits

- **100% transfer is a ceiling.** Real infusions release only part of the coumarin, so every count
  is an upper bound. TDI is a lifetime value; one day over it is not a health finding.
- **Children rarely drink cinnamon tea.** The child scenarios are a reference bound.
- **Targeted sampling, generic names.** CFIA lists only the tea type, region and declared origin.
  The 2015-16 survey also targeted licorice-flavoured teas. The surveys are not market shares, and
  the lower later shares are not evidence that the market changed.
- **Not blind.** See the status above.

<!-- RESULT-MARKER: coumarin-tea-replication-0.1.1-result -->
