# Pre-registration: CFIA's open 2009-10 aflatoxin file for dried figs and dried dates (aflatoxin-figs-2009 0.1.0)

PREREG-MARKER: aflatoxin-figs-2009-0.1.0-prereg

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code
Apache-2.0.

**Written before any result value in the file was read.** The figures below come from CFIA's
summary page and from a names-only census of the open file. The census records labels, counts
and the format of each result cell, but never a value.

The grading code is `aflatoxin_figs_2009.py`, and its offline tests are
`test_aflatoxin_figs_2009.py`. A sealed compute job grades this registration only after it is
public on GitHub. The job checks out the published code and then reads the SHA-256-pinned file.

Nothing here is a finding about any product, brand or health risk. Canada sets no aflatoxin
maximum level for dried fruit. CFIA referred all positive results to its programs for follow-up.

## What CFIA printed

- **R1:** CFIA, "2009-2010 Aflatoxin in Dried Figs and Dried Dates" (TS-CHEM-09/10-01), summary
  page (modified 2018-09-04, read 2026-10-28). It says: "One hundred (49 dried dates, 51 dried
  figs) samples were collected and analysed"; "The samples originated from 11 different
  countries"; the method "detects the aflatoxin forms B1, B2, G1 and G2", reported individually
  and as totals; "All of the 49 (100%) dried date samples and 47 of 51 (92%) dried fig samples
  did not contain detectable levels"; "Four dried fig samples contained aflatoxin levels ranging
  from 7.5 to 78.7 ppb". It gives no limit of detection. The full report is available on request.
- **R2:** CFIA, "2010-2011 Aflatoxins in Dried Fruits, Nuts and Nut Products, and Corn Products".
  It reports that none of its 90 dried dates and dried figs had detectable aflatoxins, and calls
  this similar to 2009-10.

## What the census shows (names only)

- **AF:** Open Government Portal dataset `bfac4a9d-ba2f-433a-8425-9b2fc7689d72`, resource
  `8339ffec-f854-430c-b3c8-4718e18ed4b2`, 60,259 bytes, Windows-1252, SHA-256 `5d3300b7…b055d`,
  Open Government Licence – Canada.
- 500 rows on 100 samples, five rows each: `Aflatoxin B1`, `B2`, `G1`, `G2` and
  `Total Aflatoxins` (100 rows each). All are in `ppb`, and every `Function` is `Import`. Sampled
  2009-11-02 to 2010-01-27.
- Every result cell is a number. Literal zeros are present, and only **14** cells are non-zero,
  each a different value.
- `Product`: `DATE` 250 rows and `FIG` 250 rows, so **50 dates and 50 figs**.
- `Origin` (rows): IRAN 100, TURKEY 100, UNITED STATES 100, GREECE 75, CHINA 30, TUNISIA 25,
  UNKNOWN 25, SAUDI ARABIA 15, ALGERIA 10, FRANCE 10, ITALY 10, so 20, 20, 20, 15, 6, 5, 5, 3,
  2, 2 and 2 samples.

## Two points from the labels alone (recorded, not graded)

- **L1.** R1 says 49 dates and 51 figs. The file labels 50 of each. The labels cannot say which
  is right. If the file is right, R1's "47 of 51 (92%)" figs without aflatoxin would be 46 of 50.
- **L2.** R1 says the samples "originated from 11 different countries". The file names 10
  countries, and 5 samples are `UNKNOWN`.

## Data and rules

- **Values (registered rule):** a number above 0 is a positive, and a literal 0 is a non-detect.
  Any blank, text, negative or non-finite cell fails the gate. A sample is positive if any of
  its five cells is positive.
- **Units:** units go through an explicit table, and an unknown unit fails the gate.
- **EU reference levels** (Regulation (EU) 2023/915, dried figs, carried over from 1058/2012):
  aflatoxin B1 6.0 µg/kg, and the sum of B1, B2, G1 and G2 10.0 µg/kg. "Exceeds" means strictly
  above. The sum is computed from the four forms, as the EU defines it. These levels did not
  apply in Canada. The summary page quotes earlier EU figures of 4 and 10 ppb.

## Gate (G)

If the gate fails, nothing below is graded. It requires: the SHA-256 matches; 500 rows, 100
samples and five rows per sample, one for each component; one product and one origin per sample;
the product and origin row counts above; one known unit; every cell a positive number or a
literal 0 (both present); and exactly 14 non-zero cells.

## Consistency checks (C1, C2)

- **C1.** No `DATE` sample is positive, and exactly **4** `FIG` samples are.
- **C2.** The positive samples' `Total Aflatoxins` range from **7.5** to **78.7** ppb at the
  printed precision (the minimum within 7.45–7.55 and the maximum within 78.65–78.75).

## Blind predictions (P1–P6)

- **P1.** In every one of the 100 samples, `Total Aflatoxins` equals B1 + B2 + G1 + G2 within
  **0.25 ppb**. CFIA's multi-analyte group rows were per-sample sums in the 2018-19
  multi-mycotoxin survey ([multimyco-2018 detail](multimyco-2018-detail-0.1.0.md)).
- **P2.** Aflatoxin B1 is detected in every positive sample.
- **P3.** B1 is the largest single form in at least **3** positive samples (ties go to B1).
- **P4.** At least **2** positive samples declare **Turkey** as origin.
- **P5.** At least **3** positive samples exceed at least one current EU level for dried figs
  (B1 above 6.0 or the sum above 10.0 µg/kg). With the printed minimum at 7.5 ppb, the open
  question is the low end.
- **P6.** Aflatoxin G1 is detected in at least **2** positive samples.

The 14 non-zero cells fit 4 totals plus 10 form results, so the four positives carry 2.5 forms
on average if P1 holds. P3 and P6 ask how those forms split.

## Also reported (not graded)

- Every positive sample: product, origin, region, date, all five values, the sum of forms and
  which EU levels it exceeds.
- Samples by product and declared origin (which origins the figs and dates came from).

## Outputs

The job writes two files:

- `aflatoxin_figs_2009_samples.csv`: one row per sample (sample, product, origin, region, date,
  B1, B2, G1, G2, total, in ppb).
- `aflatoxin_figs_2009_summary.json`: the gate, every check and prediction with its observed
  values, the census and provenance.

The next run publishes these with a result note and a pinned recompute test that does not import
the grader.

## Prior art

On 2026-10-28, a search for analyses of this open file found none. CFIA's summary page gives the
figures above, and its 2010-11 report compares the two surveys only by their headline.
