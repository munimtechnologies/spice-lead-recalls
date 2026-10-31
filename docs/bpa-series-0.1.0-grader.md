# bpa-series 0.1.0: the value grader for seven CFIA bisphenol A files (V1-V7, D1, T1), fixed before any value is read

GRADER-MARKER: bpa-series-0.1.0-grader

Made with AI agents working in MV2's (Munim, Inc.) name. Text CC BY 4.0; code Apache-2.0.
Not a compliance finding, not about any product or brand, and not dietary or medical advice.

This note commits `bpa_series_grade.py` and its offline tests `test_bpa_series_grade.py`
**before any result value of the seven files is read.** The predictions are the value items of
the pre-registration [bpa-series-0.1.0-prereg.md](bpa-series-0.1.0-prereg.md) (tag `v0.4.87`).
The census items (S1-S5) and the label maps were graded and fixed in the
[census note](bpa-series-0.1.0-census.md) (`v0.4.91`). The sealed job `bpa-series-grade-v1` waits
until all three notes are public, checks that its bundled code equals the published code, runs
the tests, and only then reads the files.

## The grader

- **Gate (per file):** byte size as on the portal record; the bilingual columns found by their
  English headers; rows and samples as the census counted them (200, 234, 403, 576, 391, 491 x 4
  and 468 x 4); one row per component per sample (BPA only to 2013-14; BPA, BADGE, BPF and BPS
  from 2016-17); unit ng/g (2009-10) or ug/g (later) and the plan code `20NN_SB451` on every row;
  only the product labels the census found; every result a number >= 0. If a file's gate fails,
  its items are reported as ungraded.
- **Units and rules, as registered:** 2009-10 values are ppb as they stand; later values x ug/g
  are 1000 x ppb. A value above 0 is positive; averages are over positives; a printed figure
  matches when the file's figure is within half a unit of its last printed digit.
- **Label maps:** exactly the census note's maps. The "every other label" vegetable groups are
  written out label by label from the census lists, and the tests check that every map covers
  every census label and gives the census counts.

| ID | Registered | Graded as |
|---|---|---|
| V1 | 2009-10: 82 positives; 9 infant-food positives; range 1.4 to 9.6 | all four; the package, powdered-formula and cereal clauses are **ungraded** (no label) |
| V2 | 2010-11: no positive sample | positives = 0 |
| V3 | 2011-12: exactly 6 positives: one pasta, three carrots, one peas, one corn | total 6 and each of the four counts |
| V4 | 2012-13: 145 positives; min 5.2 (a pasta), max 381 (a coconut milk); at least 4 of Table 5's five non-pasta/soup rows in full; pasta/soup hold 92 positives | all five checks. **Said in advance:** the curry (21 vs 24) and vegetable (147 vs 144) rows cannot match on n, so at most 3 of the 5 rows can reproduce and V4 fails whatever the values are. The map that moves the three `Salsa` samples to curry (24 and 144) is reported as exploratory |
| V5 | 2013-14: 252 positives; min 1.0 (a fruit), max 565 (a corn); at least 7 of Table 5's nine rows in full, pasta as 45 of 45 | all four checks |
| V6 | 2016-17: Table 2 in at least 8 of 9 rows; 361 positives (340 canned); averages 91.6 canned, 87.2 all; the text's maxima and next-highest values | only what the file can show (it has no packaging label): the coconut milk, fruit, pie filling and vegetable rows in full (vegetables at 139 **or** 138, no prediction between them); 361 positives in all 491; the all-products average 87.2; pie filling 2240 (`Pie Filling - Pumpkin`) then 530, coconut milk 1370 then 478, fruit 1160 (`Pineapple`) then 186, sauces 1120 then 7.5, over all packaging. The other five rows, the 340 canned positives and the 91.6 / 15.2 averages are **ungraded** |
| V7 | 2017-18: Table 2's BPA rows, meat average 35.6 (not 34.6 or 46.6); 1480 then 567; one BPS positive (a meat, 1.79); 69 of 72 BADGE and all 68 BPF positives also contain BPA | the meat, fish and total rows in full; the top value an imported fish at 1480, the next 567; exactly one BPS positive, a meat at 1.79; BADGE 72 with 69 BPA-positive; BPF 68, all BPA-positive |
| D1 | exploratory, directional: at a common 5.2 ppb cut in the categories shared by 2012-13 and 2013-14, the 2013-14 share is at least 1.5 times the 2012-13 share | pooled share at or above 5.2 ppb in vegetables, fruit, juices/beverages (2013-14 without energy, sports and soft drinks), pastas/soups, coconut milk and curry (2013-14 `Sauces`); the ratio must be >= 1.5 |
| T1 | descriptive (labels and dates only) | the 2009-10 dates: how many differ, whether they are consecutive days, and how many samples sit on 2009-10-01 + (sample number - 1) days, or on first date + rank by sample number, by file row order and by ID text; weekdays; the two 5-digit IDs |
| X6 | descriptive | 2016-17 Table 4 (BADGE, BPF, BPS) over all packaging; whether the highest BADGE (224) is a coconut milk without BPA and the three BPF positives are bamboo shoots with BPA; a twin scan for copied rows |
| X7 | descriptive | 2017-18 Table 2's BADGE, BPF and BPS rows, the text's BADGE average 10.1, and a twin scan |

A sharper reading of the census note, before any value is read: it said V4's row check "can hold
only if both the curry and the vegetable rows match". Under the fixed map neither can match on n,
so at most three of the five rows (beverages, coconut milk, fruit) can reproduce in full, and V4
**will fail** however the values fall. It stays registered as written and is graded as written.

**Reported, not graded:** detection shares; origins by the Function column; each file's sampling
dates (how many parse, how many differ, the most common); the lowest and highest positives; the
2013-14 D-suffixed sample; the 2012-13 curry positives under both maps.

**Arithmetic from the printed figures alone** (pinned by `TestPrintedArithmetic`): the nine 2013
rows add to 391 samples and 252 positives; the 2012 rows' positives add to 144, and 145 - 53 = 92
for pasta/soup; the 2016 Table 2 rows weighted by positives give 91.6 and unweighted 140 (so the
text's 140 is an average of category averages); only 35.6 gives the 2017 total's 44.8.

## Next

`bpa-series-grade-v1` grades V1-V7 and D1 and writes T1, X6 and X7. The result note, the
per-sample tables and an independent recompute test follow.

MV2, Munim, Inc., mv2@munimtech.com
