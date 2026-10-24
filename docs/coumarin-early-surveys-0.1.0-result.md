<!-- RESULT-MARKER: coumarin-early-surveys-0.1.0-result -->
# coumarin-early-surveys 0.1.0: result

By MV2 of Munim, Inc. Made with AI agents working in MV2's name. Code Apache-2.0; this note and
the tables CC BY 4.0. Data: CFIA 2011-12 and 2012-13 coumarin targeted surveys (Open Government
Licence - Canada). A check of published summary figures against the agency's own open files, plus
replications of earlier screens. It is **not a compliance finding** (Canada sets no coumarin
limit), not about any brand, and not individual dietary or medical advice.

Grades [`coumarin-early-surveys-0.1.0-prereg.md`](coumarin-early-surveys-0.1.0-prereg.md), public
at tag `v0.4.48` before any of the 139 non-cinnamon values was read.

## Headline

**Gate passed; 8 of 12 met (7 of 11 predictions).** All five blind replications held, CFIA's six
printed 2011-12 category maxima matched the file at printed precision, and the 2012-13 spice-mix average was
confirmed. Four predictions failed: C2, C3, V1 and V2.

All four failures have one cause, found after grading. **CFIA's open 2011-12 file writes its
four non-detects as the bare number `0.29`, the detection limit, with no "<" or flag.** A reader
who takes the file at face value (as our registered parser did) counts 193 of 193 samples
detected. CFIA's summary says 98%, which is 189 of 193. Read as non-detects, those four rows
reproduce CFIA's 98% and its "<0.29" minima exactly.

Under that reading, the 2011-12 tea and spice-mix averages that CFIA reprints in later reports
under the note "Only positive results were used" are **all-sample means**, like the 2014-15
averages found by the [table audit](coumarin-cfia-table-audit-0.1.0-result.md). On a positives-only
basis they would be **418** (printed 380) and **367** (printed 352). This explanation is post hoc,
not graded; the registered grades stand as below.

## How it was graded

Sealed compute job `coumarin-early-v1` (2026-10-24 15:23-15:25 UTC, `python:3.12`, no host paths,
1 GB). `check_prereg.py` confirmed the pre-registration was public with its marker and made every
module it ran equal the published copy; the offline tests (fixtures only) passed;
`coumarin_early_surveys.py` 0.1.0 then read the SHA-256-pinned files (2011-12 `10d2a339…540a`,
30,173 bytes; 2012-13 `6c155d79…bc14`, 15,549 bytes) through the published `coumarin_cinnamon.py`
0.1.0 parser. That parser reads results starting with "<", "ND" or "0" as non-detects and every
other number as a measurement.

## Gate and predictions

| id | prediction | observed | grade |
|---|---|---|---|
| E0 (gate) | both files: SHA-256, exact label census, all mg/kg, every result parsed, no other components, published cinnamon values reproduce | all seven checks pass in both files | **pass** |
| C1 | each 2011-12 non-cinnamon maximum equals CFIA's printed one | spice mix 2,013.8 (2014), tea 1,040.1 (1040), baked goods 95.3, cereal 56.7, baking mix 45.8, baby food 14.9 | met |
| C2 | detection rounds to 98% (2011-12) and 100% (2012-13) | 193 of 193 (100%) and 93 of 93 (100%) | **failed** |
| C3 | Table 3 rows T1-T3 match n, minimum, maximum | n and maximum match in all three; T3 minimum 29.7 (30) matches; T1 and T2 print "<0.29" but the parse finds no non-detect | **failed** |
| V1 | 2011-12 tea, printed 380: positives | both means 379.86 (no non-detect as parsed): "both" | **failed** |
| V2 | 2011-12 spice mix, printed 352: positives | both means 351.93: "both" | **failed** |
| V3 | 2012-13 spice mix, printed 568: both | 53 of 53 detected, mean 567.74 | met |
| R1 | at most 8 of 20 baked goods over 15 mg/kg | 4 of 20 | met |
| R2 | at most 3 of 20 baked goods over 50 mg/kg | 2 of 20 | met |
| R3 | 1 or 2 of 15 cereals over 20 mg/kg | 1 of 15 | met |
| R4 | 1 to 3 of 11 teas put a 15 kg child over the TDI in one 2 g cup (100% transfer) | 2 of 11 | met |
| R5 | baby-food median below the 2011-12 cereal median | 5.2 against 6.6 | met |

T0 (2011-12 ground cinnamon, already published) was reported, not graded: n 87, minimum 16.2,
maximum 7,816.3 and mean 3,594.0 all match CFIA's reprint (87, 16.2, 7816, 3594).

## What went wrong: non-detects stored as the detection limit (post hoc)

Three things point the same way:

1. In the raw 2011-12 file, 179 results have one decimal place, 10 are whole numbers, and exactly
   **four have two decimals. All four are `0.29`**, the value CFIA prints as "<0.29". No other
   result in the 139 non-cinnamon samples is below 1.2 mg/kg (the cinnamon minimum is 6.2).
2. The four sit one each in tea, spice mix, cereal and baked goods. **193 − 4 = 189 detected, which
   rounds to CFIA's 98%** (97.9%). As parsed, the file gives 100%.
3. CFIA's Table 3 prints the tea and spice-mix minima as "<0.29": at least one non-detect in each.
   One of the four is a tea and one a spice mix.

The 2012-13 file has no `<` sign and no two-decimal result; its 100% detection matches CFIA.

The coding matters to anyone who reuses the open file: read naively, it raises the detection rate
and lowers the minimum detected value of four categories to 0.29. It does not change any maximum,
any exceedance count or any median used above.

## Which mean the reprinted averages are (post hoc)

With the four `0.29` rows read as non-detects:

| row | n | detected | printed min / max / average | mean, all samples (ND = 0) | mean, all (ND = 0.29) | mean, positives only | printed = |
|---|---|---|---|---|---|---|---|
| 2011-12 tea | 11 | 10 | <0.29 / 1040 / 380 | 379.84 | 379.86 | 417.82 | all samples |
| 2011-12 spice mix | 24 | 23 | <0.29 / 2014 / 352 | 351.92 | 351.93 | 367.22 | all samples |
| 2012-13 spice mix | 53 | 53 | 30 / 3078 / 568 | 567.74 | – | 567.74 | both |

Both 2011-12 averages match the all-sample mean whether the non-detects count as 0 or as 0.29, and
neither matches the positives-only mean the note describes (they miss it by about 76 and 30 times the
rounding window). So the registered "positives" predictions fail under either reading of the file.

Putting this together with the earlier audit, CFIA's *Coumarin in Selected Foods, 2016 to 2018*
Table 3 (read 2026-10-24 from
[inspection.canada.ca](https://inspection.canada.ca/en/food-safety-industry/food-chemistry-and-microbiology/food-safety-testing-reports-and-journal-articles/coumarin-selected-foods-2016-2018))
mixes two kinds of average under one positives-only note:

| tea row | printed | basis | positives only |
|---|---|---|---|
| 2011 | 380 | all samples | 418 |
| 2013 | 500 | positives | 500 |
| 2014 | 302 | all samples | 356 |
| 2015 | 442 | positives | 442 |

For spice mixes: 2011 352 (positives 367), 2012 568 (both), 2014 329 (positives 385), 2015 327
(not checked here). The 2011 figures move less than the 2014 ones because only one tea and one
spice mix were non-detects.

## Results on the 139 unseen samples

Per category (`data/coumarin_early_surveys.csv`, as parsed; the four `0.29` values are kept as
CFIA wrote them):

| survey | category | n | median | mean | max |
|---|---|---|---|---|---|
| 2011-12 | spice mix | 24 | 75.2 | 351.9 | 2,013.8 |
| 2011-12 | tea | 11 | 281.2 | 379.9 | 1,040.1 |
| 2011-12 | breakfast cereal | 15 | 6.6 | 10.0 | 56.7 |
| 2011-12 | baked goods | 20 | 9.8 | 15.8 | 95.3 |
| 2011-12 | baking mix | 7 | 21.9 | 22.9 | 45.8 |
| 2011-12 | baby food | 9 | 5.2 | 6.3 | 14.9 |
| 2012-13 | spice mixes | 53 | 329.3 | 567.7 | 3,077.6 |

- **EU levels (reference only).** 4 of 20 baked goods exceed the EU's 15 mg/kg fine-bakery level
  and 2 of 20 its 50 mg/kg seasonal level; 1 of 15 breakfast cereals exceeds 20 mg/kg. These sit
  below the 2013-14 rates (42 of 100 bakery samples over 15).
- **Tea per cup, 100% transfer.** No 2 g or 4 g adult cup crosses a 60 kg adult's coumarin TDI
  (the top tea gives 34.7% and 69.3% of it). A 15 kg child's 2 g cup crosses it for 2 of 11 teas
  (18.2%) and a 4 g cup for 4 of 11. The earlier finding that no standard 2 g cup puts a 60 kg
  adult over the TDI now holds in all four surveys with open tea data (633 teas).
- **Baby food.** For an 8 kg infant eating 30 g a day, none of the 9 reaches the TDI (the top
  sample gives 55.9% of it); at 60 g a day, 1 of 9 crosses it. Baby food sits below the
  cereals, as in 2013-14.
- **Spice mixes.** The 2012-13 summary says no sample exceeded the 2011-12 levels. That holds
  survey-wide (top cinnamon 7,621.1 against 7,816.3) but not for spice mixes: a 2012-13 mix
  reaches 3,077.6 mg/kg against a 2011-12 top of 2,013.8.

As far as we found, this is the first open per-category summary of these two surveys, whose full
reports are available only on request.

## Data and test

- `data/coumarin_early_samples.csv`: the 139 non-cinnamon samples (survey, CFIA sample number,
  Product label, declared origin, mg/kg as in the file). The files carry no brand names.
- `data/coumarin_early_surveys.csv`: one line per Product label in both surveys (n, detected,
  smallest detected, median, both means, maximum), as parsed. The cinnamon lines aggregate values
  published by `coumarin-cinnamon` 0.1.0.
- `test_coumarin_early_surveys_result.py` recomputes every number in this note from those two
  tables: the per-category lines, all twelve grades, the post-hoc non-detect reading (189 of
  193, the "<0.29" minima and both means for each reprinted row), the tea per-cup and infant
  figures and the EU counts. Plain `csv`, `statistics`, `unittest`.

## Limits

- The non-detect reading is inferred from three consistent facts, not stated by CFIA; it was found
  after grading, so it explains the failures but is not itself a blind test.
- A match at printed precision is evidence about how a figure was computed, not proof. Here the
  losing mean misses by at least 30 times the rounding window.
- Samples are small (7 to 53 per category). The EU levels apply to foods as eaten and Canada sets
  no coumarin limit; baking mixes are sold dry and are not compared. The tea screen assumes all
  coumarin reaches the cup, an upper bound.
- No finding here concerns the safety of any product. CFIA and Health Canada judged these surveys
  on maxima and exposure assessments, which this note does not touch.

<!-- RESULT-MARKER: coumarin-early-surveys-0.1.0-result -->
