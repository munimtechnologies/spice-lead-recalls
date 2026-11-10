# CFIA's open 2009-10 dried-tea file: value items graded (dried-tea-2009 0.1.0 result)

RESULT-MARKER: dried-tea-2009-0.1.0-result

Made with AI agents working in MV2's (Munim, Inc.) name. Text CC BY 4.0; code Apache-2.0.
Not a compliance finding and not dietary or medical advice. Dated 2026-11-10. No person has checked
these numbers yet.

This note grades the value items of the [pre-registration 0.1.0](dried-tea-2009-0.1.0-prereg.md)
(V1, V2, V4-V6; V3 cannot be graded) and items P1-P3 of the
[census note](dried-tea-2009-0.1.0-census.md), from the sealed job `dried-tea-grade-v2`
(2026-11-10 01:55-01:59 UTC), which ran the published [dried_tea_grade.py](../dried_tea_grade.py)
0.1.0 and its tests on the same file (MD5 f21f016693b4608ff7059d28be35bb26, same as the portal
record and the census). Full output: [results/dried_tea_grade_2009.json](../results/dried_tea_grade_2009.json).

## Grades

| Item | Prediction | File | Grade |
|---|---|---|---|
| P1 | The 100 pesticide ("A") and 100 metal ("B") sample numbers are the same 100 teas | 100 in both, all 100 metal numbers end in "B" | **Holds** |
| P2 | Each "Pesticide Screen" count equals that sample's named rows, per method | 200 of 200 agree | **Holds** |
| P3 | All 166 named-pesticide rows are numbers in µg/g | 166 of 166 | **Holds** |
| V1 | Exactly 69 teas have a detected residue | 69 (screen text: 69) | **Holds** (not fully blind, see the census note) |
| V2 | Exactly 41 teas have a pesticide value above 0.1 ppm | 40 above; 41 at or above | **Fails** (by one) |
| V3 | Violations by tea type | the file has no tea-type field | **Not graded** |
| V4 | Every metal except beryllium is above zero in all 100 teas (the 2009-10 page) | 7 metals are zero in some teas | **Fails** (as V6 predicted) |
| V5 | Beryllium is above zero in fewer than all teas | 0 of 100 | **Holds** |
| V6 | Mercury is above zero in fewer than 87% of teas (the 2010-11 page) | 32 of 100 | **Holds** |

6 of 8 graded items held. Non-detects are written as 0 in the metal rows (no blanks, no "<").

## What the file says

- **Mercury (R5): the file supports the 2010-11 page, not the 2009-10 page.** The 2009-10 report
  page says every metal except beryllium was found in every tea, which would include mercury. The
  open file has mercury above zero in only **32 of 100** teas (highest 0.0303 µg/g). The 2010-11
  page called its own 87% detection rate much higher than in earlier years, which fits a 2009-10
  rate of 32%, not 100%. The 2009-10 page's sentence is wrong for mercury as the file stands.
- **The same sentence fails for six more metals.** Teas with a value of zero: mercury 68, tin 44,
  antimony 40, molybdenum 13, selenium 3, arsenic 1, titanium 1. Beryllium is zero in all 100.
  The other 10 metals are above zero in every tea.
- **The 41 violations are values at or above 0.1 ppm.** 40 teas have a pesticide value strictly
  above 0.1 µg/g and one more has exactly 0.1 as stored. The page's 41 (and its 59% compliance)
  therefore counts a value equal to 0.1, or a value that was rounded to 0.1 when stored. V2 was
  registered as "above 0.1" and fails as written; the page's count itself is reproduced.
- **Detections (V1) are reproduced exactly:** 69 teas, and the per-method screen text agrees with
  the named rows for all 200 sample-method pairs.
- By origin (reported, not graded; strictly above 0.1): China 28 of 54 teas, Japan 3 of 3, the
  United States 3 of 5, Vietnam 3 of 5, Canada 1 of 15, Hong Kong 1 of 1, unknown origin 1 of 2,
  others 0. 20 teas have two or more values above 0.1.

## For the errata table

Two candidates for the next version of the [CFIA open-data errata table](cfia-open-data-errata-0.3.0.md):
the 2009-10 page's "every metal except beryllium in every sample" against the file (`report_vs_file`;
mercury 32 of 100, six other metals short), and the two pages' conflict on mercury (`report_vs_report`,
settled by the file in favour of the 2010-11 page). They are listed here and not yet added; the
census note's PDF analyte-count item (A1) is a third.

## Limits

- A zero in the file may mean "not detected" or "below a reporting limit"; the file does not give
  detection limits, so "above zero" is read as "detected", as registered.
- The report pages are dated 2018-09-04 as published; CFIA may hold data not in the open file.

MV2, Munim, Inc., mv2@munimtech.com
