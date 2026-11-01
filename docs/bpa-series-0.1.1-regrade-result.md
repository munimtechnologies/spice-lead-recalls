# bpa-series 0.1.1: CFIA's 2009-10 and 2011-12 bisphenol A files regraded under the ID-pattern amendment — result

RESULT-MARKER: bpa-series-0.1.1-regrade-result

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This completes the [bpa-series 0.1.0 pre-registration](bpa-series-0.1.0-prereg.md) (`v0.4.87`).
The [first result](bpa-series-0.1.0-result.md) (`v0.4.96`) graded five of CFIA's seven open BPA
files. The 2009-10 and 2011-12 gates had failed only on the sample-ID regular expression, so the
public [ID-pattern amendment](id-pattern-0.1.1-amendment.md) (`v0.4.97`) widened that one pattern
and left the published grader unchanged. The amendment also disclosed that the failed run had
already shown V1's 82 and V3's 6 positive counts.

The sealed job `bpa-series-regrade-v1` ran on 2026-11-01 from 14:08 to 14:10 UTC (python:3.12,
1 GB, no host paths). It waited until the four notes were public. It checked that its bundled
modules matched the published copies, and ran the 19 original and 8 amendment offline tests (all
passed). Only then did it read the seven files.

**All seven gates now pass. Across the seven files, 6 of the 8 graded items held: V1, V2, V3, V5,
V7 and D1.** V4 and V6 are unchanged from the first result: V4 failed, as said in advance, and V6
failed on 2 of its 7 checks. The other five files gave the same results as in the first run.

This is a reproducibility check of open government data, not a compliance finding and not about
any brand. Canada has no maximum level for BPA in food. Nothing here is dietary or medical
advice. All figures are ppb (the 2009-10 file is in ng/g, which is the same unit). Averages are
over positive samples only.

## Headlines

1. **2009-10 (V1 held).** The file has 200 samples: 100 infant formulas and 100 infant foods.
   82 are positive (41%). Of these, 73 are formulas (1.6-9.2 ppb) and 9 are infant foods
   (1.4-9.6 ppb), so the overall range is 1.4 to 9.6, as the report prints. The report's
   packaging and formula-type clauses (70 of 89 metal, 12 of 32 glass, no detection in powder or
   cereal, all infant-food positives in glass jars) cannot be graded: the file has no package or
   formula-type column.
2. **2011-12 (V3 held).** Exactly 6 of 403 samples are positive: three carrots (307, 21.9 and
   18.0 ppb), one pea (183.3), one corn (74.0) and one canned pasta (73.0). None of the 101
   fruits, 50 juices and beverages or 5 soups is positive. The file's category counts (101 fruit,
   50 juices/beverages, 151 vegetables/legumes, 96 + 5 = 101 pastas/soups) match the report's
   exactly. This survey is the one that the 2016-17 trend table leaves out.
3. **The 2009-10 sampling dates were filled in after a text sort (T1, descriptive).** The 200
   dates are 200 consecutive calendar days, 21 July 2009 to 5 February 2010. They include
   Christmas Day, New Year's Day and 28 Saturdays and 28 Sundays (each weekday occurs 28 or 29
   times). Sorted as text, the sample IDs line up with those days exactly: the n-th ID in text
   order is dated 21 July 2009 + (n - 1) days, for all 200.
   That order is a spreadsheet's text order, not the order of the sample numbers:
   - 27 IDs carry one zero too many (`2009BPA00065`, `00066`, `00081`-`00088`, `00134`-`00150`).
   - 8 IDs carry one zero too few (`2009BPA176`-`183`).
   - Read as numbers, the 200 IDs are exactly 1 to 200, each once. Numbers 1-100 are the formulas
     and 101-200 the infant foods.
   - In text order, `2009BPA00065` sorts between `0006` and `0007`, so it is dated 27 July 2009.
     Its numeric neighbours `0064` and `0067` are dated 19 and 20 October.

   A real sampling date does not depend on how the ID was zero-padded. So these dates were
   generated as a running series after the IDs were sorted as text; they do not record when the
   samples were taken. The registered form of the
   question (date = 1 October 2009 + (number - 1) days) fits none of the 200. The census note
   already said these dates "look like placeholders"; this shows how they were made. Do not
   read seasonality or sampling order from the 2009-10 date column.
4. **The three 2011-12 `-2` IDs are separate samples that reuse a sample number.** Each has the
   same product as its base ID, but it was taken 82 or 113 days later. Two of the three also have
   a different origin: `2011BPA0270` is a Canadian (domestic) corn and `0270-2` an imported US
   corn; `0272` is Canadian and `0272-2` Thai. All six are non-detects. The report's 403 samples
   include all of them, so this changes no figure.

## Graded items: 6 of 8 held

| ID | Registered | Observed in the file | Met |
|---|---|---|---|
| G09 | 2009-10 structure gate | all 10 checks under the amended ID pattern; MD5 matches the portal | ✅ (gate) |
| G10-G17 | the other five gates | unchanged: all pass | ✅ (gate) |
| G11 | 2011-12 structure gate | all 10 checks under the amended ID pattern; MD5 matches the portal | ✅ (gate) |
| V1 | 2009-10: 82 positives, 9 infant food, 1.4-9.6 (package, powder and cereal clauses ungraded) | 82; 9; 1.4-9.6 | ✅ (82 was visible before; see the amendment) |
| V2 | 2010-11: no positive | 0 of 234 | ✅ |
| V3 | 2011-12: six positives (1 pasta, 3 carrots, 1 peas, 1 corn) | exactly those six | ✅ (6 was visible before) |
| V4 | 2012-13 | unchanged: only 2 of 5 rows in full | ❌ (said in advance) |
| V5 | 2013-14 | unchanged: all nine rows | ✅ |
| V6 | 2016-17 | unchanged: 5 of 7 checks | ❌ |
| V7 | 2017-18 | unchanged: all 7 checks | ✅ |
| D1 | 2013-14 share at 5.2 ppb ≥ 1.5 × 2012-13's | unchanged: 2.38 | ✅ |
| T1 | descriptive: 2009-10 dates as a calendar sequence of the sample numbers | a sequence of the text-sorted IDs, not of the numbers; see headline 3 | (descriptive) |

## What the series shows, all seven files

Every file holds its report's printed sample total, and five of the seven reproduce their main
tables in full or with every miss explained. The misses sit in summaries, sentences and trend
tables that reprint earlier surveys. One example is 2013 pasta printed as "34" when the file and
the 2013-14 report have 45. Another is a 2012-13 table that silently covers 509 of 576 samples.
The 2009-10 date column is the one field that carries no information at all.

## Limits

- "Positive" is the file's own coding (a value above 0). The files give no per-sample reporting
  limit.
- V1's 82 and V3's 6 were visible in the failed run's output before this regrade, as the
  amendment disclosed. The other V1 and V3 checks and T1 were not.
- Headline 3's account of how the dates were made is an inference from the pattern. It fits all
  200 rows, and the registered alternative fits none. The file itself does not say how its dates
  were entered.
- Headline 4 and the ID arithmetic in headline 3 were checked after grading and were not
  pre-registered.

Prior art: searches on 2026-10-30, 2026-10-31 and 2026-11-01 found the CFIA report pages and
open dataset records, but no analysis of these per-sample files.

## Reproduce it

- `data/bpa_2009_samples.csv` and `data/bpa_2011_samples.csv` are the sealed job's per-sample
  tables. Each row has ID, product, category, Function, origin, region, date and BPA (ppb).
- `data/bpa_series_summary_0.1.1.json` is the regrade's full grader record (all seven files).
  The first run's record, `data/bpa_series_summary_0.1.0.json`, is kept unchanged.
- `data/bpa_series_id_amendment.json` lists the IDs that the old pattern rejected and the `-2`
  pairs.
- `test_bpa_series_regrade_result.py` does not import the grader. From the two tables, it
  recomputes V1, V3, the date sequence, the ID arithmetic and the `-2` pairs with its own code,
  and it checks the sealed records.

A sealed follow-up job (`bpa-series-result-v2`) fetches the published files from GitHub and runs
this test and the corrected 0.1.0 test.

MV2, Munim, Inc., mv2@munimtech.com
