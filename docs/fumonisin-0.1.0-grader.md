# Grader: CFIA's open 2010-11, 2011-12 and 2012-2018 fumonisin files (fumonisin 0.1.0)

GRADER-MARKER: fumonisin-0.1.0-grader

Made with AI agents working in MV2's (Munim, Inc.) name. Text CC BY 4.0; code Apache-2.0.
Not a compliance finding and not dietary or medical advice; Canada has no maximum level for
fumonisins in food.

This note publishes the grader for the value items of two pre-registrations,
[fumonisin-2010](fumonisin-2010-0.1.0-prereg.md) and
[fumonisin-series](fumonisin-series-0.1.0-prereg.md), **before any result value of the three files
has been read**. The label maps and grading rules it applies are fixed in the two census notes
([2010-11](fumonisin-2010-0.1.0-census.md), [2011-12 and 2012-2018](fumonisin-series-0.1.0-census.md)).

## Code

- `fumonisin_grade.py` (module marker FUMONISIN-GRADE-MODULE 0.1.0). Standard library only; it
  uses `cfia_census.py` (download, decoding, column roles) and `perchlorate_census.py` (dates and
  April-March survey years) from this repository, unchanged.
- `test_fumonisin_grade.py`: 10 offline tests on synthetic rows (parsing, decimal and thousands
  commas, format problems, the label maps, the half-unit bands and every graded item).
- `test_fumonisin_census_notes.py`: checks every count in both census notes against the published
  census records in `data/`.

## What it does

For each file it downloads the resource from open.canada.ca, checks the gate again (MD5 and the
KiB band read as rounded up), and builds one record per sample: product, function, origin,
sampling date and survey year, B1, B2 and total = B1 + B2 (ng/g). Format problems are listed, not
fixed: an unknown analyte, a repeated or missing B1/B2 row, a non-numeric or negative result, a
unit other than ng/g, a sample with two product labels, an unparsed date or a label outside the
map. Values are graded only if the gate holds; the sample counts, which already fail, do not stop
grading.

Items graded (each "holds" only if every check in it holds): V1, V2, V3, V4 and 2010-V5 for
2010-11; A-V1 to A-V4 for 2011-12; B-V1, B-V2, B-V3, B-V4 and B-V11 for 2012-2018. B-V5, B-V6 and
B-V9 are recorded as not gradable from the labels, and B-V7, B-V8 and B-V10 as failed on the label
map, as the census note fixed them.

Also written, not graded: per-label and per-group figures, the 2012-2018 groups and named grains by
survey year, the corn-named labels by year, the sixteen "D" sample numbers with their partners,
the figures without the "D" samples, zero rows and the smallest non-zero B1 and B2 (how non-detects
are written), positives by function and year, the ten largest totals, cells with a comma, and the
exploratory look-ups of printed figures.

## Outputs

`fumonisin_<file>_record.json` (gate, problems, grades, descriptive figures) and
`fumonisin_<file>_samples.csv` (one row per sample: sample, product, group, named grain, function,
origin, date, survey year, B1, B2, total) for fum10, fum11 and fum1218. The result note will publish
them with an independent test that re-reads the CSVs.

## Order of work

1. The pre-registrations (v0.4.116, v0.4.120) and census module (v0.4.121) are public.
2. This commit: both census notes, the census records, this note, the grader and its tests.
3. A sealed job waits until these notes are public, makes its code equal the published copies, runs
   both test files, then grades the three files.
4. A result note and an independent re-run from GitHub follow.

MV2, Munim, Inc., mv2@munimtech.com
