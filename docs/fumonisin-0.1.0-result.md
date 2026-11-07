# Result: CFIA's open 2010-11, 2011-12 and 2012-2018 fumonisin files against their reports (fumonisin 0.1.0)

RESULT-MARKER: fumonisin-0.1.0-result

Made with AI agents working in MV2's (Munim, Inc.) name. Text CC BY 4.0; code Apache-2.0.
Not a compliance finding and not dietary or medical advice. Canada has no maximum level for
fumonisins in food, so no sample is judged against one here. No item below has been confirmed
by a person or by CFIA; these are pointers, not confirmed errors.

This note grades the value items of two pre-registrations,
[fumonisin-2010](fumonisin-2010-0.1.0-prereg.md) and
[fumonisin-series](fumonisin-series-0.1.0-prereg.md), under the label maps and rules fixed in the
census notes ([2010-11](fumonisin-2010-0.1.0-census.md),
[2011-12 and 2012-2018](fumonisin-series-0.1.0-census.md)) and the
[grader note](fumonisin-0.1.0-grader.md), all published (v0.4.116 to v0.4.123) before any result
value was read.

## How it was graded

The sealed job `fumonisin-grade-v1` ran on 2026-11-07 from 12:39 to 12:41 UTC. It first checked
that both pre-registrations, both census notes, the grader note and the grader were public with
their markers, and made its code equal to the published copies. Then it ran the grader's 10
offline tests and the census-notes test (22 tests in all, all passed), and only then downloaded
and graded the three files. All three gates hold: each file's MD5 is the portal's and its size
is in the kibibyte band. The grader found no format problem in any file: no unknown analyte, no
repeated or missing B1/B2 row, no non-numeric, negative or unparsed cell, and no unmapped label.

Its outputs are published unchanged in `data/`: `fumonisin_fum10_samples.csv`,
`fumonisin_fum11_samples.csv` and `fumonisin_fum1218_samples.csv` (one row per sample: product,
mapped group, named grain, function, origin, date, April-March survey year, B1, B2 and total in
ng/g, which is ppb), and the three sealed records `fumonisin_<file>_record.json`.
`test_fumonisin_result.py` re-reads the CSVs with its own code (it does not import the grader)
and checks every figure below.

## Tally: 6 of 17 graded value items held

| File | Held | Failed | Not graded |
|---|---|---|---|
| 2010-11 (277 samples; page 276) | V2 | V1, V3, V4, 2010-V5 | |
| 2011-12 (498; page 454) | A-V2 | A-V1, A-V3, A-V4 | |
| 2012-2018 (4,320; report 4,261) | B-V2, B-V3, B-V4, B-V11 | B-V1; B-V7, B-V8, B-V10 (on the label map, fixed at census) | B-V5, B-V6, B-V9 |

With the census items (6 of 17 held, 1 not gradable), 12 of 33 graded items held across the
three files.

## 2010-11: one of five held

| Item | Registered (page) | File | Grade |
|---|---|---|---|
| V1 | 157 positives | **185** (total above zero) | fails |
| V2 | minimum 20, in a chip-block sample and a cornmeal/grits sample | 20.0, six samples: three in the chip block, two Cornmeal, one Popcorn | **holds** |
| V3 | maximum 6650, a cornmeal/grits | **4750** (2010FMN0213, Cornmeal; B1 4750, B2 0) | fails |
| V4 | 8 above 800: 4 cereals, 3 cornmeal/grits, 1 chip block | **7**: 3 Cereal - Corn, 3 Cornmeal, 1 tortilla | fails |
| 2010-V5 | average 268 (2012-2018 report, Table 7) | 206.85 over 185 positives | fails |

Read after grading (exploratory, not registered; the test pins each figure):

- **The page's 157 is exactly the number of samples with fumonisin B1 above zero.** 120 of the
  277 samples have B1 = 0; the other 28 of the 185 positives have B2 only.
- **B2 is stored only for the first 56 samples.** B2 is above zero in exactly 56 samples, and
  they are the samples numbered 2010FMN0001 to 2010FMN0055 (with 2010FMN0031-2), every one of
  them. All 221 later samples have B2 = 0, including the 4,750 ppb cornmeal. Half of the 56
  (28) have B2 with no B1. In the 2011-12 and 2012-2018 files no sample has B2 without B1, and
  B2 is above zero in samples spread through each file (107 in 2011-12).
- Over the 157 B1-positive samples the totals average 220.2 and B1 alone 206.8; neither is 268.
- **A lead, not a finding.** The page's 6650 maximum, its eighth sample above 800 and the later
  report's 268 average are all absent from the file. All three would be reachable if the B2
  results of samples 2010FMN0056 onward were measured but stored as 0. For 268 over 157 samples
  the missing B2 would have to total 7,508 ng/g, 27% of those 129 samples' B1 (32,475 in all,
  27,823 after the first block); for 6650 the largest sample would need a B2 of 1,900. Only CFIA
  can say whether that is what happened.

Non-detects are written as 0; the smallest non-zero B1 and B2 are both 20.0. Positives by
function: Domestic 90, Import 95.

## 2011-12: one of four held

| Item | Registered (page) | File | Grade |
|---|---|---|---|
| A-V1 | 162 positives: 161 corn-based, 1 soy flour at 22.4 | **175**: corn-named 157, other 16, soy-named **2** (a soy flour at 22.4 and a soy infant formula at 284.6) | fails |
| A-V2 | smallest corn positive 20.8 (page), not 23.1 (later Table 7) | **20.8** (2011FUM0326, Chips - Corn) | **holds** |
| A-V3 | maximum 4442.5, a cornmeal | 4442.5, but labelled **Corn Products** (2011FUM0456) | fails |
| A-V4 | corn positives average 253.2 (Table 7) | 259.80 (corn-named); 247.97 (corn-named and other) | fails |

So the file sides with the 2011-12 page against the later report on the corn minimum (20.8), and
holds the page's maximum value. Read after grading: one positive (2011FUM0037, a cornmeal) is
dated 2011-02-09, in the 2010-11 survey year; B2 is above zero in 107 samples, and the smallest
non-zero B2 is 15.0, below the smallest non-zero B1 (20.8). Positives by function: Domestic 56,
Import 109, Unknown 10.

## 2012-2018: four of eight graded items held

| Item | Registered (report) | File | Grade |
|---|---|---|---|
| B-V1 | 1,076 positives: grain 1,073, soy 2, tea 1 | **1,080**: grain **1,077**, soy 2, tea 1 | fails |
| B-V2 | 20 to 7790, the largest a cornmeal | 20.0 to 7790.0 (C2017FUMN00349, Cornmeal, 2017-18) | **holds** |
| B-V3 | the two soy positives: a tofu in 2012-13 (27) and a soy flour in 2013-14 (45) | exactly these (C2012FUMN00438, C2013FUMN00420) | **holds** |
| B-V4 | the tea positive is a black tea at 43 | 43.0, Tea - Black, 2016-17 | **holds** |
| B-V11 | Table 2's averages: grain 365, soy 36, total 364 | 364.97, 36.0, 364.06 | **holds** |
| B-V7, B-V8, B-V10 | rice positives; oat 2017; Table 7's corn rows | failed on the label map at census | fails |
| B-V5, B-V6, B-V9 | Table 3 by grain; wheat 2012; children's corn cereals | not gradable from the labels | not graded |

B-V3 settles the report's own contradiction (R10 in the pre-registration): its appendix and
Table 15 are right, and the text's "only 2 samples of tofu" is a slip (one tofu, one soy flour).
Every average in Table 2 reproduces even though the file has 4 more grain positives and 59 more
samples. The file also confirms the text slip R11: its 2012-13 maximum is 7711.0
(C2012FUMN00452, a cornmeal), as the tables print, and no sample is 7710.

Read after grading (exploratory, not registered):

- **15 of the 16 "D" sample numbers have no partner in the file.** Only C2015FUMN00349D
  (arrowroot) has its plain-numbered partner; the other 15 stand alone, so they are not repeat
  analyses of samples the file holds. One is positive (C2013FUMN00590D, corn bran, 288). Without them the file has 4,304
  samples and 1,079 positives, still not the report's 4,261 and 1,076.
- Positives by survey year: 229, 226, 178, **2, 1**, 444 for 2012-13 to 2017-18. The 1,500
  samples of 2015-16 and 2016-17, none of them under a corn-named label, hold only three
  positives.
- The teff label (59 samples) has one positive, 43.0. Corn-named labels by year hold 169 of 272
  (2012-13), 178 of 264, 117 of 201 and 254 of 493 (2017-18) positives.
- Some printed row extremes appear in the file under broad labels, which cannot place them: the
  2012 wheat row's 393 is a "Bread - Other" sample in 2012-13 (308.9 + 84.1), and the 2014 rice
  row's 249 a "Cereal - Adult" sample in 2014-15. The rice row's 33 and the oat row's 53 each
  occur several times under corn and cereal labels.
- Positives by function: Domestic 128, Import 752, Unknown 200. Non-detects are written as 0.

## What this adds to the series

The three fumonisin files are the first in the series that are all larger than their reports.
Where values can be checked, the 2012-2018 file reproduces its report's headline table (both
extremes, all three averages, and the soy and tea positives), while the two older files differ
from their pages in their positive counts and extremes. The 2010-11 file shows a new kind of
problem for the series: a whole analyte present for the first 56 samples only, and a printed
positive count that matches B1 alone.

## Limits

- The labels are coarser than the reports' groups, so several items were graded on label maps
  fixed at census; three could not be graded at all.
- The exploratory readings and the B2 lead were found after the values were read. They are
  reported apart and are not pre-registered results.
- The files were published on 2026-11-03; if CFIA replaces one, its gate will fail on a re-run
  and this note will not be edited.

## Next

An independent sealed job re-runs `test_fumonisin_result.py` from GitHub. The items above are
in [CFIA open-data errata 0.3.0](cfia-open-data-errata-0.3.0.md), published with this note.

MV2, Munim, Inc., mv2@munimtech.com
