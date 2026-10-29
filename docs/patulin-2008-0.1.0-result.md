# patulin-2008 0.1.0: CFIA's open 2008-09 patulin file for apple juice and concentrate — result

RESULT-MARKER: patulin-2008-0.1.0-result

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This grades the pre-registration [patulin-2008-0.1.0-prereg.md](patulin-2008-0.1.0-prereg.md),
which was public first, at tag `v0.4.73`. The sealed job `patulin-2008-v1` ran on 2026-10-29 at
02:49 UTC (python:3.12, 1 GB, no host paths). It confirmed the registration's marker was public
and that its bundled `patulin_2008.py` and `test_patulin_2008.py` were byte-identical to the
published copies. It ran the 10 offline tests and only then read the SHA-256-pinned file.
**The gate failed on 1 of its 10 checks, so under the registration nothing is graded (0 of 1).**
The other nine checks passed: the SHA-256, rows, samples, product, function, origin, component
and unit. The failed check is the value rule. **75 of the 104 `AMOUNT` cells read `<0`**, and the
registered rule did not cover that form, because it accepted a `<` entry only when a number above
0 follows.

This is not a compliance finding. It is not about any brand, and it is not dietary or medical
advice. CFIA concluded that the patulin levels it found did not present a risk to children or
the general population.

## Headlines

1. **The open file writes "below the reporting limit" in two ways, and one of them is
   impossible.** Of the 92 below-limit samples, 17 read `<10` and 75 read `<0`, "less than zero".
   17 + 75 = 92 = 104 − 12, which is exactly the summary page's count of samples below 10 ppb, so
   `<0` is a below-limit entry with its limit dropped, not a result.
2. **The change follows the calendar, not the region.** All 17 `<10` entries are in samples taken
   from 3 November to 16 December 2008 (sample numbers up to `FSAP8-00027`). From 12 January 2009
   on, every below-limit entry is `<0` (69 of 69), and 6 entries from late November and December
   2008 already read `<0`. Both forms occur in samples from the West, Quebec and Ontario regions.
   The likeliest explanation is a change in how results were entered or exported partway
   through the survey, but the file cannot show that.
3. **Taken literally, the file understates an upper-bound estimate about three-fold.** Means
   across all 104 samples, from the file's 12 measured values (sum 188.0 ppb):
   - lower bound (below-limit entries as 0): **1.81 ppb**;
   - upper bound with every below-limit entry at the 10 ppb reporting limit the page states:
     **10.65 ppb**;
   - upper bound taking each cell's own limit (17 at 10, 75 at 0): **3.44 ppb**.

   A parser that rejects a zero limit stops, as ours did. One that strips the `<` reads 75
   measured zeros. One that substitutes the cell's limit produces the 3.44. This is the fifth way
   we have seen CFIA's open files code a non-detect, after a literal 0, the bare detection limit,
   a text token and the CANLINE operator column (see
   [Reading CFIA's mycotoxin detection rates](reading-cfia-detection-rates-0.1.0.md)).
4. **Read the way the page implies (exploratory, not graded), the file agrees with every figure
   CFIA printed.** Counting `<0` as below the limit, after the gate failed and with every value
   now seen: 7 of 44 apple juices and 5 of 60 concentrates are at or above 10 ppb (92 of 104
   below, 88.5%). The maxima are 26.7 ppb (juice) and 24 (concentrate, written `24`). None is at
   50 ppb, and origin shows no link to patulin.

## Data

- **PA:** CFIA, "2008-09 Patulin in Apple Juice Products". Open Government Portal dataset
  `a3c93b73-f001-47b7-abbd-4df1438a9b06`, resource `60694a95-9060-49e4-b1ec-b61910e4c8c9`,
  SHA-256 `4039e4a8…be66` (372,295 bytes, Windows-1252), Open Government Licence – Canada. 104
  rows on 104 samples, one patulin result each, all in `ng/g` (= ppb). Plan code `2008_FP8APL7`.
- `AMOUNT` holds 12 numbers (10.1 to 26.7), 17 × `<10` and 75 × `<0`, so 12 distinct entries,
  as the names-only census recorded.

## Gate (failed on the value rule)

| check | result |
|---|---|
| SHA-256, 104 rows, 104 samples, one row each | ✅ |
| product (60/44), function (94/10) and origin row counts | ✅ |
| one component (`Patulin`), one known unit (`ng/g`) | ✅ |
| every `AMOUNT` cell a number, a literal 0, a `<` entry with a limit above 0, or an ND token | ❌ 75 × `<0` |

Under the registration a failed gate grades nothing. The table below is therefore reported as
**exploratory**. To produce it, the value rule was extended after the failure so that `<0` reads
as below the limit, and every value had been seen first. It is not a blind test, and it is not
counted as one.

## The registered items, read after the gate failed (exploratory, not graded)

| ID | Registered | Observed in the file | Would hold |
|---|---|---|---|
| C1 | 7 of 44 juices and 5 of 60 concentrates at or above 10 ppb | 7 and 5 | yes |
| C2 | maxima 26.7 (juice) and 24.0 (concentrate) at printed precision | 26.7 and 24 | yes |
| C3 | none at or above 50 ppb | 0 | yes |
| C4 | origin not linked: Fisher p ≥ 0.05, China vs others and imported vs domestic | China 3 of 42 vs 9 of 62, p 0.35; imported 11 of 94 vs domestic 1 of 10, p 1.0 | yes |
| P1 | no number above 0 and below 10 ppb | none (smallest 10.1) | yes |
| P2 | every domestic sample declares Canada; no imported one does | 10 and 0 | yes |
| P3 | at least 8 of the quantified results below 15 ppb | **7** of 12 | no |
| P4 | at most 1 of 10 domestic samples at or above 10 ppb | 1 (a concentrate, 19.9) | yes |
| P5 | at least 3 quantified samples declare China | 3 | yes |

## The 12 quantified samples

| sample | product | declared origin | function | region | sampled | ppb |
|---|---|---|---|---|---|---|
| FSAP8-00015 | juice | Jordan | imported | West | 2008-11-28 | 26.7 |
| FSAP8-00094 | concentrate | China | imported | Ontario | 2009-02-06 | 24 |
| FSAP8-00003 | juice | United States | imported | West | 2008-11-07 | 21.5 |
| FSAP8-00032 | concentrate | Canada | domestic | Ontario | 2009-01-22 | 19.9 |
| FSAP8-00084 | juice | Chile | imported | Ontario | 2009-02-03 | 17.4 |
| FSAP8-00135 | juice | United States | imported | Ontario | 2009-03-02 | 12.6 |
| FSAP8-00134 | juice | Moldova | imported | Ontario | 2009-03-04 | 12.5 |
| FSAP8-00220 | concentrate | United States | imported | Ontario | 2009-03-10 | 12.5 |
| FSAP8-00030 | concentrate | United States | imported | Ontario | 2009-01-12 | 10.4 |
| FSAP8-00294 | juice | Unknown | imported | West | 2009-03-19 | 10.3 |
| FSAP8-00098 | concentrate | China | imported | Ontario | 2009-02-06 | 10.1 |
| FSAP8-00117 | juice | China | imported | Ontario | 2009-03-02 | 10.1 |

The file's minimum measured value is 10.1, so it is censored at the reporting limit, like the
page. Four of the twelve sit within 0.5 ppb of it. All twelve are under 50 ppb, which is Canada's
maximum level for apple juice today and the EU's level for fruit juice. All twelve are above
10 µg/kg, the EU's level for apple products for infants and young children (Regulation (EU)
2023/915), but these are general retail juices, so that comparison is context only.

## Other things the file shows

- **Sampling dates:** 3 November 2008 to 23 March 2009. The pre-registration's census gave
  "10-Mar-09" to "7-Nov-08", a text-order artefact that the registration already flagged.
- **Three sample numbers carry an `A` suffix** (`FSAP8-00012A`, `-00118A`, `-00294A`), each next
  to an unsuffixed twin. Two differ from their twin in region or product. One (`00118A`) matches
  its twin on every label. The file and the page both count them as separate samples, so the 104
  includes them.

## Limits

- The registered test did not run past its gate. Everything after the gate table is exploratory
  and was read with the values in view.
- 104 samples and 12 quantified results describe this survey, not apple juice in general. Counts
  by country are too small to say anything about any country's juice.
- The file gives no limit of detection, and the page gives only the 10 ppb reporting limit.
  Whether `<0` came from a data-entry step, a database export or a later conversion cannot be
  told from the open file. Only CFIA can say.
- Concentrates are read as reported. The page does not say whether they were reconstituted.

Prior art: on 2026-10-28, before the registration, searches found no analysis of this open file beyond
CFIA's own summary page. As far as we know, this is the first per-sample reading of it and the
first record of its `<0` coding.

## Reproduce it

- `data/patulin_2008_samples.csv`: one row per sample (sample, product, origin, function,
  region, date, the raw `AMOUNT` entry, its kind under the registered rule, and ppb). This is the
  sealed job's output.
- `data/patulin_2008_summary.json`: the sealed grader record (the failed gate, every item with
  its observed values, the census and provenance).
- `test_patulin_2008_result.py`: a pinned test. It does not import the grader. With its own code
  it rebuilds the label counts, the two below-limit forms and their dates, the three bounds, the
  exploratory C1–C4 (its own Fisher test) and P1–P5 from the CSV, and checks them against the
  sealed record.

A sealed follow-up job (`patulin-2008-result-v1`) fetches these published files from GitHub and
re-runs the pinned test on them. The grading code `patulin_2008.py` and the pre-registration are
at tag `v0.4.73`.
