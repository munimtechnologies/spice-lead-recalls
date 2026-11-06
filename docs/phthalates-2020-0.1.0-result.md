# phthalates-2020 0.1.0: result — the 2020-21 phthalates file reproduces every value claim of its report; only the origin table and one unit sentence are off

RESULT-MARKER: phthalates-2020-0.1.0-result

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This is the result of the [pre-registration](phthalates-2020-0.1.0-prereg.md) (`v0.4.111`), graded
as fixed in the [census note](phthalates-2020-0.1.0-census.md) and the
[grader note](phthalates-2020-0.1.0-grader.md) (`v0.4.112`). The sealed job `phthalates-grade-v1`
ran on 2026-11-06 from 08:34 to 08:36 UTC. It first checked that all three notes were public and
that its modules matched the published copies, then ran the 11 offline tests (all passed), and only
then read the values of CFIA's open 2020-21 phthalates file (open.canada.ca dataset
`4ae4c2b3-e1b7-451a-b313-02e51d73da73`, 117,529 bytes, MD5 `612780be14a4a571044d93aaa27f99f2`).
This is a reproducibility check of open government data. It is not a compliance finding (Canada has
set no maximum level for phthalates in food, and Health Canada found every detected level safe), not
about any brand, and not dietary or medical advice. Values are ppm (µg/g).

The sealed record is [`data/phthalates_2020_record.json`](../data/phthalates_2020_record.json) and
the per-sample table is [`data/phthalates_2020_samples.csv`](../data/phthalates_2020_samples.csv)
(one row per sample, CC BY 4.0, derived from the Open Government Licence - Canada file).
[`test_phthalates_2020_result.py`](../test_phthalates_2020_result.py) recomputes every number below
from that table with its own code (it does not import the grader).

## Summary

- **Gate.** As written (G) it failed on format, as the census note said in advance: every sample
  has a `Phthalate Screen` row whose result is a text count. Under the format-only amendment A1
  (published before any value was read) the gate passed: MD5 and size match, 500 samples, every
  phthalate row a number in µg/g, every screen row a count token, no format problem of any kind.
- **All five value items held, under A1** (V1-V5). These grades are reported apart from the
  pre-registered gate, which failed as written.
- **Census items (graded earlier, unchanged):** S1, S2 and S5 held; S3 (Table 1 origin) and S4
  (region labels) failed.
- **The screen counts agree with the rows in all 500 samples**, and every stored value is a
  detect (no zero rows, no tiny values): the smallest stored result is 0.2 ppm.

So the file reproduces Table 2 in all 18 cells, Table 3's two 2020 rows, and every number in the
text that concerns values. What does not match the file are Table 1's origin cells (off by one or
two samples in each group, with every group total right), the four regions (the file has no region
field), and a sentence that needs no file: "0.006 mg/L (0.6 parts per billion)" is 6 parts per
billion.

## Item by item (under A1)

| ID | What was predicted | Result | What the file shows |
|---|---|---|---|
| V1 | Table 2: RTE 250 / 5 / 0.3 / 4.2 / 1.56 (2%); fats and oils 250 / 31 / 0.2 / 3.4 / 0.86 (12%); total 500 / 36 / 0.2 / 4.2 / 0.96 (7%) | **held** | RTE 250 / 5 / 0.3 / 4.2 / 1.560 (2.0%); fats and oils 250 / 31 / 0.2 / 3.4 / 0.865 (12.4%); total 500 / 36 / 0.2 / 4.2 / 0.961 (7.2%) |
| V2 | 464 samples without phthalates; the largest result, 4.2, is a children's RTE meal | **held** | 464; one largest result, 4.2 ppm, `C2020PHTH00482`, labelled `Meal - Toddler/Baby` |
| V3 | DEHP above zero in 23 samples; each other phthalate in 1 to 9; exactly 7 samples with two or more | **held** | DEHP 23, DBP 9, DINP 8, DIDP 5, DNOP 2, BBP 1; 7 samples with two or more |
| V4 | Table 3 2020: oils 150, 0.2-3.4, 0.89; dressings 50, 0.3-0.6, 0.45; 29 positive oils; two positive dressings, 0.3 and 0.6 | **held** | oils 150, 29 positive, 0.2-3.4, average 0.893; dressings 50, two positive (0.3 and 0.6), average 0.45 |
| V5 | No mayonnaise or shortening above zero | **held** | none of the 2 mayonnaises or 48 shortenings has a phthalate row |

The averages are of positives only, as Table 3's footnote says and as registered. Over all samples
(non-detects as zero) they would be 0.031, 0.107 and 0.069, which match nothing printed, so this
report uses one convention throughout (unlike the perchlorate series, where two CFIA documents
used two).

## What the pre-registration's arithmetic said, and the file

The pre-registration derived three things from the report alone (R2, R3), before the file was
opened. All three are confirmed:

- Salad dressings at 4% of 50 had to be exactly 2 positives, 0.3 and 0.6 ppm. They are
  (`C2020PHTH00416`, domestic, DEHP 0.3; `C2020PHTH00402`, DINP 0.6).
- The oils then had to carry 29 of the 31 fats-and-oils positives. They do; their 29 totals sum to
  25.9 ppm (average 0.893).
- The five RTE positives had to sum to about 7.8 ppm. They sum to exactly 7.8 (2.2 + 0.6 + 0.3 +
  0.5 + 4.2).

## Descriptive (not graded)

- **The two children's meals.** Only 2 of the 53 `Meal - Toddler/Baby` samples carry phthalates,
  but they are the two largest RTE results and the only RTE samples with more than one phthalate:
  `C2020PHTH00482` (4.2 ppm: DBP, DNOP, DEHP and DIDP each 0.9, DINP 0.6; origin unknown) and
  `C2020PHTH00050` (2.2 ppm: DBP 0.4, DNOP 0.5, DEHP 0.5, DIDP 0.8; imported). The other three RTE
  positives are two pizza products and a soup, each with one phthalate. The report names the 4.2
  ppm sample a hot dog meal; the file's labels are categories only and cannot confirm that.
- **Per phthalate** (samples, range): DEHP 23, 0.2-2.9; DBP 9, 0.2-0.9; DINP 8, 0.3-0.6; DIDP 5,
  0.5-2.0; DNOP 2, 0.5-0.9; BBP 1, 0.6.
- **Positives by product:** sesame oil 8, palm oil 7, olive oil 6, coconut and peanut oil 2 each,
  avocado, blend, soybean and sunflower oil 1 each; salad dressing 2; toddler/baby meals 2, pizza
  products 2, soup 1. By origin (`Function`): imported 31, domestic 2, unknown 3.
- **Values sit on a 0.1 ppm grid.** All 48 stored results have one decimal place, so identical
  totals between samples are expected and say nothing here (unlike the PAH files, where whole
  16-value profiles repeated).
- **No stored non-detects.** A phthalate that was not found has no row, and every screen count
  equals both the number of rows and the number of rows above zero.

## For CFIA's open-data team

Two items, both small, neither about a value:

1. Table 1's origin cells do not match the file: RTE meals 56 / 166 / 28 in the file against the
   printed 56 / 165 / 29, and vegetable fats and oils 28 / 159 / 63 against 27 / 161 / 62. Every
   group total matches. The country column gives the same domestic counts (56 and 28 Canadian
   samples).
2. The page's "0.006 mg/L (0.6 parts per billion)" for the US bottled-water DEHP limit is 6 parts
   per billion. The 2018-19 flatbread and vegan page has the same sentence.

The report describes sampling in four regions; the file has no region field.

## Limits

- V1-V5 are graded under amendment A1, a format-only change published before values were read; as
  written, the gate failed. The census note had already shown the counting parts of V1-V3 (464
  without, 36 with rows, DEHP 23, 7 multi) from the screen tokens, so those parts were not blind.
  The blind parts were the split of the 36 between meals and fats and oils, the 29 oils and 2
  dressings, every minimum, maximum and average, and which sample holds the maximum.
- Table 3's 2012-2015 rows are not checked here; they are checked against CFIA's 2012-2018 file in
  the [phthalates-series pre-registration](phthalates-series-0.1.0-prereg.md).

## Next

A sealed job (`phthalates-2020-result-v1`) downloads this note, its data tables and the independent
test from GitHub and runs the test, so the published result is re-checked from what is public.

MV2, Munim, Inc., mv2@munimtech.com
