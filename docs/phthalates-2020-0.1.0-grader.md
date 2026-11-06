# phthalates-2020 0.1.0: grader note (CFIA 2020-21 phthalates file)

GRADER-MARKER: phthalates-2020-0.1.0-grader

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This note publishes the grader for the [pre-registration](phthalates-2020-0.1.0-prereg.md), using
the label map, coding and amendment A1 fixed in the [census note](phthalates-2020-0.1.0-census.md).
It is committed before any result value of the file has been read. It is not a compliance finding,
not about any brand, and not dietary or medical advice.

## Files

- `phthalates_2020.py`: the grader (standard library only, plus `cfia_census.py` for loading and
  header roles).
- `test_phthalates_2020.py`: 11 offline tests on synthetic data, with no network and no CFIA file.
  They check the label map, parsing (comma decimals, the screen token, unknown components,
  non-numeric results, wrong units, missing screen rows, unmapped products), the matching rules,
  and the grades on a synthetic 500-sample population built to the report's printed figures (all
  five items hold) and on two changed copies (a positive shortening; a largest result labelled
  `Meal - RTE`).

## What the grader does

1. Loads the file from open.canada.ca and checks its MD5 and size.
2. Parses each sample: product, `Function` (origin), the screen count, and one value per
   phthalate row. Format problems are listed by kind.
3. Gate: records G as written (expected to fail, as the census note says) and A1. Value items are
   graded only if A1 holds.
4. Recomputes S1-S3 from the parsed samples, as a cross-check of the census.
5. Grades V1-V5:
   - **V1:** Table 2 for meals, fats and oils, and the total: samples, positives, minimum,
     maximum, average of positives, and positive share.
   - **V2:** 464 samples at zero; a single largest result that matches 4.2, in a ready-to-eat
     meal labelled `Meal - Toddler/Baby`.
   - **V3:** DEHP above zero in 23 samples; each other phthalate in 1 to 9; exactly 7 samples with
     two or more above zero.
   - **V4:** Table 3's 2020 rows: oils (150 samples, 0.2-3.4, average 0.89) and salad dressings
     (50, 0.3-0.6, 0.45); 29 positive oils; exactly two positive dressings, matching 0.3 and 0.6.
   - **V5:** no mayonnaise or shortening above zero.
6. Also reports, not graded: each phthalate's count and range, the five smallest stored values,
   positives by product label and by origin, identical non-zero totals, and any sample whose
   screen count disagrees with its rows.

Outputs: `phthalates_2020_record.json` (the sealed record) and `phthalates_2020_samples.csv` (one
row per sample, CC BY 4.0, derived from the Open Government Licence - Canada file).

## The sealed job

`phthalates-grade-v1` waits until the pre-registration, the census note and this note are all
public. It then makes its modules equal the published copies, runs the offline tests, and only
then runs the grader.

MV2, Munim, Inc., mv2@munimtech.com
