# phthalates-series 0.1.0: grader note (CFIA 2018-19 flatbreads and vegan products; 2012-2018 selected foods)

GRADER-MARKER: phthalates-series-0.1.0-grader

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This note publishes the grader for the [pre-registration](phthalates-series-0.1.0-prereg.md), using
the label maps, coding and amendment A2 fixed in the [census note](phthalates-series-0.1.0-census.md).
It is committed before any result value of either file has been read. It is not a compliance
finding, not about any brand, and not dietary or medical advice.

## Files

- `phthalates_series.py`: the grader (standard library only, plus `cfia_census.py` for loading and
  header roles and `perchlorate_census.py` for dates and April-March survey years).
- `test_phthalates_series.py`: 14 offline tests on synthetic data, with no network and no CFIA
  file. They check both files' component names (with and without the `(DEHP)`-style suffix),
  number reading (a decimal comma such as `0,54`, and a thousands comma such as `2,608`, which must
  not become 2.608), the ID-year and size-band helpers (rounding up fits all four portal sizes seen so far, rounding to
  nearest only two), both label maps, parsing (comma decimals, both screen-unit spellings, and
  every kind of format problem), the gate and A2, the F grades on a synthetic 599-sample population
  built to the printed Table 2 (all four items hold) and on a changed copy, and the P year filter,
  rows and names tables on a small synthetic population.

## What the grader does

1. Loads each file from open.canada.ca and checks its MD5 and size (as written, and under A2).
2. Parses each sample: product, `Function` (origin), sampling date and survey year, the year in its
   ID, the screen count, and one value per phthalate row. Format problems are listed by kind.
3. Grades values only if A2 holds.
4. **F:** recomputes F-S1 and F-S2, then grades
   - **F-V1:** all seven Table 2 rows (samples, positives, share, minimum, maximum, average);
   - **F-V2:** 526 samples at zero; a single largest result matching 24.00, in a tofu;
   - **F-V3:** DINP above zero in 51-56 samples, DEHP in 21-26, DBP in 4, DIDP in 2, BBP and DNOP in
     none, at least 5 samples with two or more;
   - **F-V4:** tofu's three positives 0.54, 7.985-8.035 and 24.00; mayonnaise's 0.72, 0.985-1.035
     and 3.19.
5. **P:** grades
   - **P-V1:** 977 positives; smallest total 0.26; largest 2,608;
   - **P-V2** (Y3 by date): grain products 460 / 167 / 36% / 0.27 / 23.3 / 1.60; nut and seed
     butters 100 / 59 / 59% / 0.5 / 315 / 17.2; RTE meals 224 / 128 / 0.27 / 15.4 / 1.46;
   - **P-V3** (Y3): vegetable fats and oils 327 / 0.26 / 2,608 / 84.3; oils 180 / 0.26 / 2,608 /
     107; salad dressings 22 / 8 / 36% / 0.71 / 3.75 / 2.25;
   - **P-V4** (Y3): mayonnaise share rounding to 12% with average 2.77; no shortening above zero.
   An item holds only if every part holds; the record keeps each part, so a row whose count
   failed in the census still shows whether its minimum, maximum and average match.
6. Also reports, not graded: each phthalate's count, share of all samples and range; the five
   smallest stored values and the ten largest totals; positives by product and by origin;
   identical non-zero totals; any stored zero; any sample whose screen count disagrees with its
   rows. For P also, names only: every group by sampling year and by ID year, ID year against
   sampling year, and the Y3 groups by origin; and, with values, every group's figures for each
   single year, for Y3 and Y4, and for Y3 and Y4 read from the ID year. These readings are there to
   test whether a printed row restates a subset of the file (as the perchlorate series found); they
   change no grade.

Outputs: `phthalates_fv18_record.json` and `phthalates_ps12_record.json` (the sealed records), and
`phthalates_fv18_samples.csv` and `phthalates_ps12_samples.csv` (one row per sample, CC BY 4.0,
derived from the Open Government Licence - Canada files).

## The sealed job

`phthalates-series-grade-v1` waits until the pre-registration, the census note and this note are
all public. It then makes its modules equal the published copies, runs the offline tests, and only
then runs the grader.

MV2, Munim, Inc., mv2@munimtech.com
