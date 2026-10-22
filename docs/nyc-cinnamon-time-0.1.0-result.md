# nyc-cinnamon-time 0.1.0: result

By MV2 of Munim, Inc. Prepared with AI agents; no human has reviewed these numbers yet.
Text CC BY 4.0; code Apache-2.0.

This grades [`nyc-cinnamon-time-0.1.0-prereg.md`](nyc-cinnamon-time-0.1.0-prereg.md), committed in
v0.4.33 before any case-frame cinnamon row was read. The grader `nyc_cinnamon_time.py` was written after
that commit and ran once, unchanged, in a sealed compute job (nyc-cinnamon-time-v1, 2026-10-21, about
19:50 UTC, python:3.12, standard library only). Its tests passed first. It reads the committed snapshot
`data/nyc_spice_lead_snapshot_2026-10-17.csv` (NYC DOHMH dataset da9u-wz3r) and writes
`data/nyc_cinnamon_time.csv`, with one line for every cinnamon-named row. `test_nyc_cinnamon_time.py`
recomputes every number below from those files.

## Summary

- **All four predictions held. H1 and H3 were met; H2 was not.**
- NYC's lead case investigations hold 45 cinnamon samples. 26 had a detectable lead value, and 8 of
  those were above ASTA's 2.0 ug/g bark level (31%).
- Only one sample reached the 50 ppm gross bar (1 of 45, 2.2%): a cinnamon powder collected in
  2013, bought abroad, at 880 ppm. Every other exceedance was between 2.3 and 12.3 ug/g.
- After the late-2023 recall of cinnamon applesauce pouches, investigators sampled cinnamon about
  three times as often per year as in 2019-2022. Most of the case exceedances still came from
  other years.
- The store-frame cross-check matches the earlier ASTA yardstick result exactly: 25 rows, 11 above 2.0,
  and the same row ids.

## Predictions and hypotheses

| Item | Pre-registered | Result | Grade |
|---|---|---|---|
| P1 case cinnamon rows | 45 [15, 120] | 45 | held |
| P2 share of detected rows > 2.0 ug/g | 40% [15%, 65%] | 8/26 = 30.8% | held |
| P3 share of rows >= 50 ppm | 4% [0%, 12%] | 1/45 = 2.2% | held |
| P4 post-recall rows per year / 2019-2022 rows per year | >= 2 [0.8, 5] | 9.43 / 3.00 = 3.14 | held (both parts) |
| H1 case gross rate below the 11.0% all-spice abroad rate | yes | 2.2% < 11.0% | met |
| H2 case rate > 2.0 at least the store rate outside Jan 2024 | yes | 30.8% vs 1/2 = 50% | **not met** |
| H3 post-recall period does not hold most case exceedances | yes | 3 of 8 | met |

P1 landed exactly on its point estimate. That is luck inside a wide interval, not precision.

**H2, read plainly.** Outside January 2024 the store frame holds only 4 cinnamon rows: 2 non-detects,
1 at 1.1 ug/g and 1 at 2.94 ug/g (row 8705). The comparison therefore rests on 2 detected store samples,
and a single sample decides it. H2 is graded "not met" because that is what the pre-registered rule
gives. Counting non-detects in the denominator does not change the grade: 8 of 45 case rows (17.8%)
against 1 of 4 store rows (25%). Read it as "no evidence that case cinnamon is worse than store
cinnamon outside the recall month", not as evidence that it is better.

## Case frame by period

Rows / detected / above 2.0 ug/g / at or above 50 ppm. Rows per year are given for closed periods only.

| Period | Rows | Detected | > 2.0 | >= 50 | Rows per year |
|---|---|---|---|---|---|
| before 2019 (2012-2018) | 9 | 7 | 3 | 1 | - |
| 2019-2022 | 12 | 7 | 2 | 0 | 3.0 |
| Jan-Oct 2023 | 2 | 2 | 0 | 0 | 2.4 |
| Nov 2023-Dec 2024 (post-recall) | 11 | 4 | 3 | 0 | 9.4 |
| 2025 on | 11 | 6 | 0 | 0 | - |
| no date | 0 | 0 | 0 | 0 | - |

All 11 of the "2025 on" rows were collected in 2025. The snapshot (2026-10-17) holds no 2026 case
cinnamon rows, and this data cannot tell whether that is a reporting lag or a real absence. Taken as one
year, 2025 stayed near the post-recall sampling rate (about 11 rows) but had no exceedance among its 6
detected samples. In the post-recall period, 3 of the 4 detected samples were above 2.0 ug/g, and all
three were recorded as bought in the United States. These are small counts, described here and not
tested.

## Case frame by purchase place

| Purchase place | Rows | Detected | > 2.0 | >= 50 |
|---|---|---|---|---|
| United States | 23 | 13 | 4 | 0 |
| abroad | 13 | 9 | 4 | 1 |
| unknown / not stated | 9 | 4 | 0 | 0 |

## Every exceeding case row

| row_id | Collected | Bought | Lead (ug/g) | Name as recorded |
|---|---|---|---|---|
| 665 | 2012-12-12 | abroad | 4.4 | Cinnamon Powder |
| 702 | 2013-02-14 | abroad | **880** | Cinnamon Powder |
| 1253 | 2015-02-19 | abroad | 4.9 | Cinnamon bark |
| 3725 | 2019-03-29 | abroad | 2.3 | Cinnamon bark |
| 5525 | 2021-05-14 | US | 5.3 | Cinnamon |
| 7833 | 2024-03-22 | US | 3.2 | GROUND CINNAMON |
| 8278 | 2024-09-10 | US | 2.43 | Cinnamon Stick Flat |
| 8429 | 2024-10-24 | US | 12.3 | Canela Ceylon Cinnamon Sticks |

Row 765 (2013, US, "Cinnamon") is exactly 2.0 ug/g and is not counted, because the pre-registration
counts only values strictly above the level. In the store frame, row 7582 is likewise exactly 2.0.

## Question 3: is cinnamon a lead-chromate target?

Pre-registered reading: if cinnamon's lead comes mostly from soil, bark or processing, it should
often exceed the ASTA level but rarely reach 50 ppm. That is the pattern found. 7 of the 8 case
exceedances sit between 2.3 and 12.3 ug/g, and the store frame's maximum is 23 ug/g. The one 880 ppm
sample, from 2013, is the kind of value usually associated with deliberate adulteration. This dataset
has no chromium pairing for it, so the source of the lead cannot be told from these rows. The pattern
is consistent with the reading; it does not prove where the lead came from.

## Store-frame cross-check (not blind)

The whole-word cinnamon list used here finds the same store rows as the ASTA yardstick's bark category
(v0.4.31). There are 25 rows, 11 of them above 2.0 ug/g, and the ids are identical: 7584, 7588, 7590,
7592, 7611, 7613, 7615, 7622, 7628, 7630 and 8705. 21 rows were bought 2024-01-04 to 2024-01-23, and 10
of those exceed. The two methods agree on this frame, so the case-frame counts above do not depend on
which list is used.

## Set apart (not graded)

- Frame code A: 3 cinnamon rows (2011, 2018, 2019), all detected, none above 2.0.
- Blend: 1 case row, "Cinnamon spice mix" (row 2390, 2017, 0.33 ug/g).
- Sensitivity: row 5762, "Black Pepper, Cinnamon and Coriander" (2021, non-detect), is a multi-spice
  sample that the blend word list did not catch. Dropping it gives 44 rows. No grade changes: P3 becomes
  1/44 = 2.3%, P4 becomes 9.43 / 2.75 = 3.43, and the P2, H1, H2 and H3 numbers are unchanged.

## Limits

- Only the case-frame and time splits were blind. The store-frame figures were known before the
  pre-registration.
- Case samples are items taken from households during lead investigations. They describe what
  investigators collected, not any market.
- 19 of the 45 case rows are non-detects counted as below both levels, so every rate is a lower
  bound. Detection limits are not recorded per row.
- Rows per year measure how often investigators sampled cinnamon, not how much contaminated cinnamon
  was in circulation.
- Cinnamon and cassia cannot be told apart by product name.
- ASTA's levels are voluntary industry guidance, not legal limits. Brands that appear in the
  `product_name` column are as recorded by NYC DOHMH; this note draws no conclusion about any brand.
- The counts are small (45 case rows, 8 exceedances). The period and purchase-place splits are
  descriptive.

## Reproduce

```
python nyc_cinnamon_time.py          # writes data/nyc_cinnamon_time.csv and .json
python -m unittest -v test_nyc_cinnamon_time
```

Sources: NYC DOHMH open dataset da9u-wz3r, snapshot 2026-10-17, committed in this repo; ASTA Guidance Levels V3 (2026-06-08), Table 2.
