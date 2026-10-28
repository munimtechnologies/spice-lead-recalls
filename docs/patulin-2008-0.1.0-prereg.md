# Pre-registration: CFIA's open 2008-09 patulin file for apple juice and apple juice concentrate (patulin-2008 0.1.0)

PREREG-MARKER: patulin-2008-0.1.0-prereg

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code
Apache-2.0.

**Written before any result value in the file was read.** The figures below come from CFIA's
summary page and from a names-only census of the open file. The census records labels, counts
and the number of distinct values in each column, but never a value.

The grading code is `patulin_2008.py`, and its offline tests are `test_patulin_2008.py`. A sealed
compute job grades this registration only after it is public on GitHub. The job checks out the
published code and then reads the SHA-256-pinned file.

Nothing here is a finding about any product, brand or health risk. CFIA concluded that the
patulin levels it found did not present a risk to children or the general population.

## What CFIA printed

- **R1:** CFIA, "2008-2009 Patulin in Apple Juice Products", summary page (modified 2018-09-04,
  read 2026-10-28). It says: "104 samples of apple juice and apple juice concentrate (94
  imported, 10 domestic)"; "88.5% of the samples had patulin levels below the reporting limit of
  10 parts per billion (ppb)"; "Of the 44 apple juice samples collected, 37 samples (84%) had
  patulin concentrations below 10 ppb"; "Fifty five of the 60 samples (92%) of apple juice
  concentrates had patulin concentrations below 10 ppb"; "The highest measured level of patulin
  was 26.7 ppb in apple juice and 24.0 ppb in apple juice concentrates"; "All of the samples were
  below the Codex draft maximum level of 50 ppb". It also says there was "no difference in
  compliance rate between imported and domestic products" and no "relationship between country
  of origin and the measured patulin level". It gives no limit of detection, no averages and no
  tables. The full report is available on request.
- From R1's own arithmetic: 7 juices and 5 concentrates, 12 samples in all, are at or above
  10 ppb, and 92 of 104 = 88.46% are below, which prints as 88.5%. The printed figures agree
  with each other.

## What the census shows (names only)

- **PA:** Open Government Portal dataset `a3c93b73-f001-47b7-abbd-4df1438a9b06`, resource
  `60694a95-9060-49e4-b1ec-b61910e4c8c9`, 372,295 bytes, Windows-1252, SHA-256
  `4039e4a8…be66`, Open Government Licence – Canada.
- 104 rows on 104 samples, one row each. Every `Component` is `Patulin` and every `Plan Code`
  `2008_FP8APL7`. The result column is `AMOUNT`, with one unit column (one distinct value).
- `Product`: `Apple Juice Concentrate` 60 and `Apple Juice` 44, as on R1.
- `Function`: `imported` 94 and `domestic` 10, as on R1.
- `Origin`: CHINA 42, UNITED STATES 23, CHILE 17, CANADA 10, SOUTH AFRICA 5, UNKNOWN 3, TURKEY
  2, JORDAN 1, MOLDOVA 1.
- `AMOUNT` holds **12 distinct values** across 104 samples. The census does not say which.
- The census's sampling dates ("10-Mar-09" to "7-Nov-08") are the text-order minimum and maximum
  of `D-Mon-YY` strings, not a date range (the same artefact the
  [aflatoxin-figs-2009 result](aflatoxin-figs-2009-0.1.0-result.md) corrected). The grader
  parses dates and reports the real range; no graded item uses them.

## Data and rules

- **Values (registered rule):** a number above 0 is a measured result; a literal 0, a `<`
  followed by a number or a limit name (for example `<10`, `<LOQ`) and an ND-type token (`ND`,
  `Not detected`, `BRL`, `NQ` and close variants, listed in the code) are below-limit entries.
  A blank, any other text, or a negative or non-finite number fails the gate.
- **Units:** units go through an explicit table, and an unknown unit fails the gate. For juice,
  1 µg/L is read as 1 µg/kg (ppb).
- **"At or above 10 ppb"** means a measured number of at least 10.0 ppb. Concentrates are read
  as reported; the page does not say whether they were reconstituted.

## Gate (G)

If the gate fails, nothing below is graded. It requires: the SHA-256 matches; 104 rows and 104
samples, one row each; the product, function and origin row counts above; one component
(`Patulin`); one known unit; and every `AMOUNT` cell classified under the value rule, with at
least one measured number.

## Consistency checks (C1–C4)

- **C1.** Exactly **7** of 44 apple juices and **5** of 60 concentrates are at or above 10 ppb.
- **C2.** The maxima are **26.7** ppb (apple juice) and **24.0** ppb (concentrate) at the printed
  precision (within 26.65–26.75 and 23.95–24.05).
- **C3.** No sample is at or above 50 ppb.
- **C4.** Origin is not linked to being at or above 10 ppb: Fisher's exact two-sided p is at
  least 0.05 both for China against all other origins and for imported against domestic.

## Blind predictions (P1–P5)

- **P1.** No `AMOUNT` cell holds a number above 0 and below 10 ppb: the open file is censored at
  the reporting limit, as the page's figures are. (The census's 12 distinct values for 104
  samples point this way, but do not settle it.)
- **P2.** Every `domestic` sample declares `CANADA` as origin, and no `imported` sample does.
- **P3.** At least **8** of the quantified (at or above 10 ppb) results are below 15 ppb: they sit
  near the reporting limit.
- **P4.** At most **1** of the 10 domestic samples is at or above 10 ppb.
- **P5.** At least **3** of the quantified samples declare **China** as origin (42 of 104 samples
  do).

## Also reported (not graded)

- Every quantified sample: product, origin, function, region, date and value.
- The below-limit entries and how often each form is used, the parsed sampling-date range, and
  samples at or above 10 ppb by product and by declared origin.
- A reference count: samples above 10 µg/kg, the EU's patulin level for apple products for
  infants and young children (Regulation (EU) 2023/915). Juice for adults in the EU, and apple
  juice in Canada today, have a 50 µg/kg level; C3 covers that.

## Outputs

The job writes two files:

- `patulin_2008_samples.csv`: one row per sample (sample, product, origin, function, region,
  date, the raw `AMOUNT` entry, its kind and the value in ppb).
- `patulin_2008_summary.json`: the gate, every check and prediction with its observed values,
  the census and provenance.

The next run publishes these with a result note and a pinned recompute test that does not import
the grader.

## Prior art

On 2026-10-28, searches for analyses of this open file (released on the portal in March 2024)
found none. CFIA's summary page gives the figures above. As far as we know, the result column has
not been read outside CFIA.
