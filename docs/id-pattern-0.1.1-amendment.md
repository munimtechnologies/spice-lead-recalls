# id-pattern 0.1.1: a format-only amendment to the sample-ID gate (bpa-series 2009-10 and 2011-12; pah-2019)

AMENDMENT-MARKER: id-pattern-0.1.1-amendment

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

## What failed

Two sealed grading jobs failed a gate on 2026-11-01. In each case the only failing check was the
regular expression for sample IDs, which is a format check. Every count check held.

| Job | File | Gate checks that held | IDs the pattern rejected |
|---|---|---|---|
| `pah-2019-v1` (05:26 UTC) | CFIA 2019-20 PAHs in selected foods | size, columns, 4,736 rows, 296 samples × 16 rows, unit, plan code, labels, values | `C2019PAHS00037AD`, `C2019PAHS00040AD` (pattern `^C2019PAHS(\d{5})A$`) |
| `bpa-series-grade-v1` (07:29 UTC) | CFIA 2009-10 BPA in infant food and formula | size, columns, 200 rows, 200 samples, unit, plan code, labels, values | `2009BPA176` to `2009BPA183` (three-digit numbers; pattern `^C?\d{4}[A-Z]+\d{4,6}D?$`) |
| same | CFIA 2011-12 BPA in canned foods | size, columns, 403 rows, 403 samples, unit, plan code, labels, values | `2011BPA0086-2`, `2011BPA0270-2`, `2011BPA0272-2` |

The sample counts in those gates (296, 200, 403) are the reports' own counts, so the files hold
the samples the reports describe. The patterns were written from the IDs seen in other CFIA files
and were simply too narrow for these three.

## The amendment

Only the ID pattern changes, and only to admit the shapes above:

- 2019-20 PAH: `^C2019PAHS(\d{5})AD?$`, which allows one `D` after the `A`.
- BPA series: `^C?\d{4}[A-Z]+\d{3,6}(?:D|-2)?$`, which allows a three-digit number and a `-2`
  suffix.

The published graders `pah_2019.py` and `bpa_series_grade.py` are **not edited**. Two new modules,
[`pah_2019_regrade.py`](../pah_2019_regrade.py) and
[`bpa_series_regrade.py`](../bpa_series_regrade.py), set the amended pattern and then run the
published graders' `main()` unchanged. Every prediction, label map, printed figure and tolerance
stays as registered. Their tests check three things. The old pattern is exactly the published one.
It rejects each ID listed above, and the new pattern accepts it. Every ID shape the old pattern
accepted is still accepted, and other near-miss shapes are still rejected.

Each regrade also writes `id_amendment.json`. For each `D` or `-2` ID it records whether the base
ID (without the suffix) is also in the file, and, for PAHs, whether the two share all 16 values.
This is descriptive, so a suffixed ID that turns out to be a duplicate analysis will be visible.

## What was already visible before this amendment

Disclosed so that nobody mistakes a seen number for a prediction:

- The failed runs print a tally of value cells by kind (detected or not), which is part of the
  gate. The BPA files have one value per sample, so that tally is the positive count. **V1's
  "82 positives" (2009-10) and V3's "6 positives" (2011-12) were therefore visible** before this
  amendment. Both match the predictions, but they are no longer blind. The rest of V1 (9
  infant-food positives, range 1.4-9.6 ppb), the rest of V3 (one pasta, three carrots, one peas,
  one corn) and the dates item T1 were not visible.
- For the 2019-20 PAH file the tally covers 4,736 cells (2,213 detected), not samples. It does not
  show any of D2-D5 (for example the 181 of 296 samples with a positive TEQ).
- The failed PAH run wrote its per-sample table into the job's output folder. It was not opened;
  nothing from it is used here.

## How it runs

The sealed jobs `bpa-series-regrade-v1` and `pah-2019-regrade-v1` wait until this note is public,
make their bundled modules equal the published copies, and run the original offline tests and the
new tests. Only then do they read the files. The results will be published as their own notes and
added to the [index](cfia-chemistry-surveys-index.md).

MV2, Munim, Inc., mv2@munimtech.com
