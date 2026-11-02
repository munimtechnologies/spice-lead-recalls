# food-colours 0.1.0: CFIA's 2009-10 and 2018-19 food-colour files against their reports — result

RESULT-MARKER: food-colours-0.1.0-result

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This completes the [food-colours 0.1.0 pre-registration](food-colours-0.1.0-prereg.md) (`v0.4.100`).
The [census note](food-colours-0.1.0-census.md) (`v0.4.102`) graded the six census items (4 of 6
held). It also fixed the label maps and coding and published the grader `food_colours.py`, all
before any value was read.

The sealed job `food-colours-grade-v1` ran on 2026-11-02 from 04:02 to 04:03 UTC (python:3.12,
1 GB, no host paths). It waited until both notes were public and checked its modules against the
published copies. It ran the 17 offline tests (all passed), and only then read the two files.
Both match their portal records (MD5 `7651427618a70aa3ad2a51ab90bcae8c` for 2018-19,
`dc558d850720b90610da2c75424d1cd7` for 2009-10).

**Both gates pass, and 4 of 8 graded predictions held (V4, V5, V6, V7).** V1, V2, V3 and V8 failed.
V9 could not be graded, as the census note said in advance.

This is a reproducibility check of open government data. It is not a compliance finding, it is
not about any brand, and it is not dietary or medical advice. All values are ug/g (ppm). A colour
counts as detected in a sample when any of its rows is above zero.

## Headlines

1. **The 2018-19 file holds 337 colour detections, so the report's per-colour Table 3 (337) is
   right and its per-commodity Table 2 (336) is one short.** The missing detection is in the
   sweets row: the file has 261 sweets detections, and Table 2 prints 260. The other 11 cells of
   Table 2 reproduce exactly, as does the rule that each of the 13 positive oils carries exactly
   one colour.
2. **The three failed 2018-19 predictions all come down to the second Orange II result.** Orange II
   is detected in two sweets: a soft candy at 0.221 ppm (`C2018FCOL00293`) and an imported
   pudding at 0.042 ppm (`C2018FCOL00376`). The registration guessed that the second result was
   below 0.039 ppm, because only then is the average below the 0.13 ppm limit of quantification
   (LQ) that Table 3 prints for Orange II. It is 0.042, so the average is 0.1315. That is not below
   0.13, although it rounds to it. This one value fails V2 (Orange II's average), V3 (the
   explanation for 337 vs 336) and, through the sweets cell, V1.
3. **One reading fits all of it (not graded).** The 0.042 ppm result is the only Orange II result
   below Orange II's LQ. If Table 2 left that one result out, its sweets cell is 260 and its
   total 336, exactly as printed. The file cannot confirm this, and the report prints no LQ for
   the other colours, some of which have results as low as 0.07 ppm.
4. **Table 3 otherwise reproduces in full.** For all nine colours, the number of samples and the
   maximum match. All eight printed averages match within rounding. No colour outside the nine is
   above zero. Allura Red is in 101 samples (maximum 539, average 78.7), Tartrazine in 100 (144,
   27.1) and Brilliant Blue FCF in 61 (85, 9.5).
5. **The text's 219 colour-free samples should be 218.** 181 of the 399 samples carry at least one
   colour and 218 carry none (V4). 178 of the 181 carry one to four colours, and three carry five or
   six (V5).
6. **The text's named results hold.** The highest level of any colour is Allura Red at 539 ppm, in
   a hard candy (`C2018FCOL00366`; V6). Rhodamine B is in exactly one sample, an imported pickled
   vegetable at 10.8 ppm (`C2018FCOL00263`; V7). Orange II and Rhodamine B each have one row in the
   water-soluble test and one in the fat-soluble test, and no sample has either colour above zero
   in both rows. Chrysoidine G is never detected.
7. **2009-10: the "93%" sentence does not match the file (V8).** The file has water-soluble rows
   for 41 of its 100 samples, every one of them above zero (76 results), and no fat-soluble dye
   above zero. Those two clauses hold. But the five colours named in the sentence (Tartrazine,
   Sunset Yellow, Brilliant Blue, Allura Red and Amaranth) account for 74 of the 76 results, or
   97.4%, not 93%. Every one of the 41 samples carries at least one of the five, so a count by
   samples gives 100%. The census note said in advance that 93% was very unlikely.
8. **No copied rows.** Unlike both PAH files, neither colour file has two samples with identical
   profiles (two or more colours, same values).

## Graded items: 4 of 8 held

| ID | Registered | Observed in the file | Met |
|---|---|---|---|
| G18 / G09 | gates: size, MD5, columns, numeric values, unit; 399 x 46 rows and 43 labels; 100 samples | all hold | ✅ (gate) |
| V1 | Table 2: with colour 9 / 13 / 28 / 131 (181); detections 23 / 13 / 40 / 260 (336); one colour per oil positive | 9 / 13 / 28 / 131 (181); 23 / 13 / 40 / **261 (337)**; one per oil | ❌ |
| V2 | Table 3: samples and maximum for all nine colours; averages within rounding; Orange II average below 0.13; no other colour | 9 / 9 counts, 9 / 9 maxima, 8 / 8 averages; Orange II average **0.1315**; no other colour | ❌ |
| V3 | 337 detections, with one Orange II result under 0.039 ppm | 337; Orange II results **0.221 and 0.042** | ❌ |
| V4 | 218 colour-free samples (not 219) | 218 | ✅ |
| V5 | 177 or 178 samples with one to four colours | 178 (80 / 64 / 23 / 11), plus 2 with five and 1 with six | ✅ |
| V6 | highest level: Allura Red 539 ppm in a candy | `C2018FCOL00366`, Candy - Hard, 539 | ✅ |
| V7 | Rhodamine B in exactly one sample, 10.8 ppm | `C2018FCOL00263`, pickled vegetable (Lebanon), 10.8 | ✅ |
| V8 | 2009-10: 41 of 100 with colour; no fat-soluble dye; the five colours 92.5-93.5% of results | 41; none; **97.4%** (74 of 76) | ❌ |
| V9 | 2009-10 named non-compliant samples | the file has categories, not product names | (ungraded) |

## What else the files show (descriptive, named in advance in the census note)

- **Non-detects are coded as zero.** The 2018-19 file has 18,017 zero rows and 337 rows above
  zero. The smallest detected values are Orange II 0.042, Brilliant Blue FCF 0.07, Sunset Yellow
  FCF 0.33 and Allura Red 0.4 ppm; Tartrazine starts at 1.0 and Rhodamine B is only 10.8. The
  2009-10 file lists water-soluble colours only where one was found.
- **The mixed-label sample is a date format, not a different date.** One of the 46 rows of
  `C2018FCOL00400` gives its date as `2/1/2019`; the other 45 give `1-Feb-19`. Both are
  1 February 2019.
- **IDs.** The 2018-19 IDs use the numbers 1 to 400 with 2 missing. `C2018FCOL00008D` has no plain
  `00008`, so the `D` does not mark a second analysis of a listed sample (the same as the two `AD`
  IDs in the 2019-20 PAH file).
- **Dates look like real sampling dates.** 2018-19 runs from 4 April 2018 to 26 March 2019 on 133
  different dates (at most 17 samples on one day). Unlike the 2009-10 bisphenol A file, they are
  not one consecutive day per ID in ID order.
  2009-10 runs from 1 September 2009 to 8 January 2010 on 16 dates (25 samples on 9 November 2009).
- **Origins.** The census note reported that one sweet is listed as Unknown in the file where
  Table 1 counts it as imported. All totals match.
- **2009-10's largest values** are in one imported sample in the "Spices/flavours" category
  (`2009COL0012`): Tartrazine 3,836.7 and Allura Red 2,174.7 ug/g. The file gives no product name,
  so it cannot say what kind of product this is. This is a description only.

## Limits

- Headline 3 is a reading that fits; it is not proven. The report does not say how Table 2 treats
  results below the LQ, and it gives an LQ only for Orange II.
- The 2009-10 report's full text is not online, so V8 was graded against the sentence quoted in the
  pre-registration. The 93% figure could not be rebuilt from the file by any count tried (rows or
  samples).
- The label map that puts salad dressings with oils was chosen using Table 1's oil row (see the
  census note), so the oil cells are not fully independent. The sweets cells, where the one
  difference sits, are independent.
- "Detected" is the file's own coding (a value above zero). The file gives no reporting limits.

Prior art: searches on 2026-11-01 and 2026-11-02 found CFIA's report pages and the open dataset
records, but no analysis of either per-sample file.

## Reproduce it

- `data/food_colours_c18_samples.csv` is the sealed job's per-sample table for 2018-19 (ID,
  product, type, Function, origin, region, date, number of colours, top colour and level).
- `data/food_colours_c18_detections.csv` has one row per detected (sample, colour) pair: 337 rows.
- `data/food_colours_c09_rows.csv` holds all 176 rows of the 2009-10 file.
- `data/food_colours_summary.json` is the grader's full record.
- `test_food_colours_result.py` does not import the grader. From the three tables it rebuilds
  Table 2 by type, Table 3 per colour, V3-V8, the Orange II reading, the origin split, the ID
  numbers, the dates and the twin scan with its own code, and checks them against the sealed record.

A sealed follow-up job (`food-colours-result-v1`) fetches the published files from GitHub and runs
this test.

MV2, Munim, Inc., mv2@munimtech.com
