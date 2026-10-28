# Pre-registration: Health Canada's open Total Diet Study ochratoxin A file (2008-09) against the paper that reports it (tds-ota-2008 0.1.0)

PREREG-MARKER: tds-ota-2008-0.1.0-prereg

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code
Apache-2.0.

**Written before any result value in the file was read.** The figures below come from the
published paper and from a names-only census of the open file. The census records labels,
counts, limits and the format of the result columns, but never a result value or a count of
results.

The grading code is `tds_ota_2008.py`, and its offline tests are `test_tds_ota_2008.py`. A
sealed compute job grades this registration only after it is public on GitHub. The job checks out
the published code and then reads the SHA-256-pinned files.

Nothing here is a finding about any product, brand or health risk. The paper and later reviews
found Canadian OTA exposure far below levels linked to harm in animals.

## What the paper printed

- **R1:** Tam J, Pantazopoulos P, Scott PM, Moisey J, Dabeka RW, Richard IDK. "Application of
  isotope dilution mass spectrometry: determination of ochratoxin A in the Canadian Total Diet
  Study". *Food Addit Contam Part A* 2011;28(6):754-761, doi:10.1080/19440049.2010.504750,
  open access as PMC3118520 (read 2026-10-28). 140 composites: the same 70 foods bought in Quebec
  City (2008) and Calgary (2009). LC-MS/MS with a ¹³C-labelled internal standard. Results are
  corrected for recovery.
- **Table 3** prints one value per food and year, or "n.d.", plus one LOD and one LOQ per food
  (ng/g, or ng/ml for 12 starred liquids). Its footnote says values below the estimated LOD are
  given "for potential statistical analysis". The grader holds all 70 rows (`TABLE3`), copied
  twice from the PMC page and checked against each other.
- **Text:** "In both years, 73% (51/70) of the samples had detectable levels of OTA (greater than
  the LOD)" (the abstract: 102/140). "In 2008, 67% (47/70) were above the LOQ, while in 2009, 61%
  (43/70) were above the LOQ." The highest values are raisins at 2.3 ng/g (2008) and white wheat
  flour at 1.7 ng/g (2009). Cereal-containing foods are 16 of the top 20 by two-year mean
  (Table 4).

### The paper against itself (already known, from the paper alone)

Counting Table 3: **49** of 70 entries are not "n.d." in 2008 and **46** in 2009, so 95 of 140,
not the 51, 51 and 102 of the text and abstract. The LOQ counts do match: 47 (2008) and 43 (2009)
of Table 3's values are above the printed LOQ. Recomputing the top 20 from Table 3 gives 16
cereal-containing foods, as the text says. The offline tests pin all four counts.

## What the census shows (names only)

- **EN:** Open Government Portal dataset `71fa9c90-f690-4928-9239-69b4ecbeccee`, resource
  `d1cbf697-ff08-4518-b69f-b633efbfb620`, 74,452 bytes, Windows-1252, SHA-256 `3d80ade4…af79`
  (the portal gives no hash and marks its validation as "failure"; every row has 36 cells).
  **FR:** resource `237fe2c2-2f86-4ef4-b11d-485a28f8a57a`, 86,687 bytes, SHA-256 `6fd5a225…a171`,
  MD5 equal to the portal's hash. Open Government Licence – Canada. CANLINE layout: the data
  dictionary says `Result Operator` is `=`, `<LOD/MDL` or `ND`, and `Result Value` is 0 for a
  below-limit result.
- **137 composites, not 140.** One row each; 69 from Quebec City and 68 from Calgary. 67 food
  names appear in both cities. Quebec City has no `Mixed Vegetable, Baby Food` (Table 3's
  "Vegetables, peas", n.d. in 2008). Calgary has no `Beer & Malt` and no `Wine, Other` (Table 3:
  0.01 and n.d. in 2009).
- One analyte (`Ochratoxin A`), one lab, one method (ONT-SOP-0116), every row a composite.
  Units: `ng/g` 113 rows, `ng/ml` 24.
- Only `=` and `<LOD/MDL` occur in the operator column (no `ND`). No row has `=` with a 0, and
  no row has a below-limit operator with a non-zero value. Values have at most 3 decimals.
- Sampling dates are placeholders (`2008-01-01` for Quebec City, `2009-01-01` for Calgary).
- **LOD and LOQ are per row in the file.** LOD has 11 distinct values, from 0 (one row) to 0.012;
  three rows fall outside the paper's stated range of 0.001-0.008 ng/g (0, 0.01 and 0.012). LOQ
  has 23 distinct values, up to 0.039, above the paper's largest LOQ of 0.025.
- The French file has the same 137 rows and 36 columns but in a **different row order** (sample
  codes agree position by position in 1 row), so English and French must be paired by sample code.

## Data and rules

- **Food names:** every one of the file's 70 food names is mapped to a Table 3 code in the
  grader (`FILE_TO_CODE`), fixed now. One mapping is a judgement call: `Bologna, Chicken` is
  taken as "Pork, cured" (BB05), the only meat row left once the other six are paired by name.
- **City = year:** Quebec City = 2008, Calgary = 2009.
- **Results:** `=` with a number above 0 is a detected result; `<LOD/MDL` or `ND` with 0 is a
  below-limit result. Anything else fails the gate. Values are read as reported (ng/g or ng/ml).
- **"Matches Table 3"** means the file value rounds to Table 3's figure at its printed precision
  (for example 0.165-0.175 for "0.17", 0.95-1.05 for "1.0").

## Gate (G)

If the gate fails, nothing below is graded. It requires: the SHA-256 matches; 137 rows, one per
sample; 69 Quebec City and 68 Calgary rows; every food name mapped, and the 137 food-year pairs
exactly the 140 of Table 3 less the three named above; one analyte; units `ng/g` 113 and `ng/ml`
24; every result detected or below-limit under the rule, with both present.

## Consistency checks against the paper (C1–C5)

- **C1.** Each file row is detected exactly when Table 3 prints a value (not "n.d.") for that
  food and year.
- **C2.** Every detected value that Table 3 also prints matches it at the printed precision.
- **C3.** The highest value is raisins, 2.3 ng/g, in Quebec City (2008), and white wheat flour,
  1.7 ng/g, in Calgary (2009).
- **C4.** The text: **51** composites detected in each city.
- **C5.** The text: **47** (2008) and **43** (2009) detected values above the LOQ, using the
  file's own LOQ for each row. (The count against Table 3's LOQ is reported too.)

## Blind predictions (P1–P5)

- **P1.** The file follows Table 3, not the text: **49** of 69 Quebec City rows and **45** of 68
  Calgary rows are detected (Table 3's counts over the composites the file has).
- **P2.** The 24 `ng/ml` rows are exactly Table 3's 12 starred liquids where present (22 rows)
  plus the ready-to-use soy infant formula in both cities.
- **P3.** The English and French files agree: all 137 rows pair by sample code, one to one, with
  the same operator class (`=` or below-limit) and the same value (a decimal comma read as a
  point).
- **P4.** At least **16** of the top 20 foods by two-year mean (below-limit = 0; the 67 foods in
  both cities) are cereal-containing: every bakery, cereal, flour, pasta and rice row (FF), the
  infant cereal and cereal dinner (LL01, LL03), and the five fast foods (NN).
- **P5.** Rankings hold across city-years: Spearman's rho between the 2008 and 2009 values of
  the 67 shared foods is at least **0.7**.

## Also reported (not graded)

- Every C1 and C2 mismatch with both figures, the maximum per city, detected counts above the
  file's and the paper's LOQ, the full top 20, and how many rows have an LOD inside the paper's
  0.001-0.008 range.
- A reference count: rows above the EU's OTA levels where one fits (Regulation (EU) 2023/915:
  dried vine fruit 8.0 µg/kg, wine and grape juice 2.0, cereal products 3.0, foods for infants
  0.50). Canada has no OTA maximum levels in force; this is context, not compliance.

## Outputs

- `tds_ota_2008_samples.csv`: one row per composite (sample, food, Table 3 code, city, year,
  operator, raw value, kind, value, unit, LOD, LOQ, Table 3's figure).
- `tds_ota_2008_summary.json`: the gate, every check and prediction with observed values, the
  English/French comparison, the census and provenance.

The next run publishes these with a result note and a pinned recompute test that does not import
the grader.

## Prior art

On 2026-10-28, searches found the paper (R1), Health Canada's dataset listing (record last
modified 2025-06-11) and reviews that cite the paper's maxima. They found no comparison of the
open file with the paper's table, and no mention of the gap between the text's and the table's
detection counts.
