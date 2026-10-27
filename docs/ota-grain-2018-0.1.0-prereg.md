# Pre-registration: CFIA's open 2018-19 ochratoxin A grain file against its two reports, and against the same year's multi-mycotoxin survey at a common cut (ota-grain-2018 0.1.0)

PREREG-MARKER: ota-grain-2018-0.1.0-prereg

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code
Apache-2.0.

**Written before any result value in the OTA grain file was read.** The figures used below
come from CFIA's two reports and from a names-only census. All of them are recorded in the
companion note [ota-grain-2018-report-check-0.1.0.md](ota-grain-2018-report-check-0.1.0.md),
which is committed with this one. The multi-mycotoxin file (MM) was already read and graded in
[multimyco-2018 0.1.0](multimyco-2018-0.1.0-result.md). This registration uses only its published
OTA facts: 20 positives, smallest 0.8 ppb, and the per-label positives in
`data/multimyco_2018_positives.csv`.

The grading code is `ota_grain_2018.py`, and its offline tests are `test_ota_grain_2018.py`. A
sealed compute job grades this registration only after it is public on GitHub. The job checks
out the published code and then reads the two SHA-256-pinned files.

Nothing here is a finding about any product, brand or health risk. Health Canada's OTA levels
for these foods are proposed, not in force.

## Data and rules

- **OG:** resource `d9d79110-e472-4aec-89ee-e51861f4d88d`, SHA-256 `36dde7d7…7d47403`. It has
  496 rows, one OTA result per sample.
- **MM:** resource `09a3c285-8552-4a38-b4be-cdf6d5fc3fd2`, SHA-256 `ba508494…3835`. Only its 750
  OTA rows are used.
- **Values (registered rule):**
  - A cell that parses as a number above 0 is a positive.
  - A cell that does not parse as a number is a non-detect token (the census shows 276 such
    cells in OG).
  - A literal 0 is a non-detect in MM, its known coding. In OG a literal 0 fails the gate.
  - A negative or non-finite number fails the gate.
  - The gate also fails if OG uses more than 10 distinct non-detect strings. That way, an
    annotated positive (such as "0.05 *") cannot be silently read as a non-detect.
- **Units:** converted to ppb through an explicit table. An unknown unit fails the gate.
- **Row statistics:** for each row we compute n, the number of positives, the minimum positive,
  the maximum and the average of positives.
- **Matching:** a figure "matches" a printed one if it rounds to it at the printed precision,
  using printed decimal places ("0.050" covers 0.0495–0.0505, "0.05" covers 0.045–0.055) or
  units for whole numbers ("11" covers 10.5–11.5). R22's percent positive must equal the
  file's percentage rounded half up.
- **Common cut:** 0.8 ppb. This is MM's smallest OTA positive, and the OTA limit of detection
  CFIA lists for the multi-mycotoxin method in its 2015–2018 report. A result is "at or above
  the cut" if it is ≥ 0.8 ppb.

## Gate (G)

The gate has two parts. If it fails, nothing below is graded.

- **OG:** the SHA-256 matches, along with 496 rows and samples, one row each, all
  `Ochratoxin A`, all 21 product-label counts, `Origin` CANADA 92 and UNKNOWN 232, and one unit
  that is in the table. There are exactly 220 positive cells and 276 token cells, using 1–10
  distinct tokens.
- **MM:** the SHA-256 matches, along with 18,750 rows, 750 OTA rows (one per sample), only
  positive or literal-0 OTA cells with 20 positives, a smallest positive of 0.8, and units in
  the table. The two files share exactly these seven product labels: `Buckwheat Products`,
  `Crackers`, `Grain - Kamut`, `Kamut Products`, `Pasta - Dry`, `Quinoa Products` and
  `Rye Products`.

## Consistency checks (C1–C10): every report row the labels identify

| id | report row | file labels | n | pos (or %) | min | max | avg |
|---|---|---|---|---|---|---|---|
| C1 | R20 Table 2 rye | `Rye Products`, `Flour - rye` | 25 | 15 | 0.050 | 1.9 | 0.24 |
| C2 | R20 Table 3 baking mixes | `Baking Mixes` | 28 | 9 | 0.051 | 0.46 | 0.16 |
| C3 | R20 Table 3 infant cereal (wheat) | `Infant Food - Cereal` | 28 | 5 | 0.050 | 0.17 | 0.077 |
| C4 | R20 Table 3 pasta | `Pasta - Dry` | 28 | 21 | 0.049 | 0.34 | 0.18 |
| C5 | R20 text / Table 2 | whole file | – | – | 0.042 | 11 | – |
| C6 | R22 less commonly consumed grains 2018 | rye, kamut, `Buckwheat Products`, `Quinoa Products`, `Flour - Other` | 100 | 44% | 0.05 | 7.6 | 1.0 |
| C7 | R22 oat 2018 | `Bran - Oat`, `Oatmeal`, `Oat Products`, `Flour - Oat` | 97 | 54% | 0.05 | 1.6 | 0.26 |
| C8 | R22 rice 2018 | `Grain - Rice` | 99 | 14% | 0.049 | 11 | 1.1 |
| C9 | R22 wheat 2018 | `Wheat Products` | 29 | 62% | 0.06 | 1.5 | 0.4 |
| C10 | R22 grain-based foods 2018 | the other eight labels | 171 | 54% | 0.042 | 2.2 | 0.24 |

C7 and C8 also settle two contradictions in R20. Rice has 14 positives, not 13 (C8's 14% of 99
can only be 14). The oat average is 0.26, not Table 4's 2.6.

## Blind predictions (P1–P6)

**On the grain rows the labels only bound (R20 Table 2):**

- **P1.** `Buckwheat Products` (23) holds the survey's buckwheat maximum: its maximum matches
  **7.6**, with **9–11** positives (R20: 11 of 25). `Quinoa Products` (24) holds the quinoa
  maximum: its maximum matches **5.8**, with **7–8** positives (R20: 8 of 25).
- **P2.** The 25 kamut-labelled samples have **9–10** positives and a maximum of at most
  **1.25** (R20: 10 of 26, maximum 1.2).
- **P3.** Exactly **one** sample outside `Buckwheat Products` and `Quinoa Products` is above
  3 ppb, and it is a `Grain - Rice` sample (the 11 ppb brown rice behind R20's 99.8%).

**Across the two 2018-19 methods (the new part):**

- **P4 (headline).** On the seven shared product labels, read at the common 0.8 ppb cut, the
  OTA-only file's detection does **not** differ from the multi-mycotoxin file's. The test is a
  continuity-corrected Cochran–Mantel–Haenszel test with labels as strata, and the prediction
  is a two-sided **p ≥ 0.05**. At each file's own limits the two are expected to differ widely,
  which is reported but not graded. If P4 holds, the 75%-versus-2% cracker gap is a
  reporting-limit effect. If it fails, the multi-mycotoxin method also misses or under-reports
  OTA above its own limit.
- **P5.** Of the 29 `Crackers`, at least **20** are positive, but at most **3** are at or above
  0.8 ppb. The multi-mycotoxin file has OTA in 2 of 101 crackers.
- **P6.** Between **10 and 39** of the 496 OG samples (2.0–7.9%) are at or above 0.8 ppb. That
  is the same order as MM's 20 of 750 (2.7%).

## Also reported (not graded)

- The non-detect token(s) and the unit string.
- At both cuts: the per-label 2×2 tables, the pooled table, the MH odds ratio and the CMH
  figures.
- `Crackers` + `Crispbread/Crouton` (31) against R20's crackers/crispbreads row (40, 30
  positive, 0.047–2.2, average 0.41).
- Every label's statistics.
- Samples above 3 ppb in buckwheat and quinoa (no proposed level), infant cereals above
  0.5 ppb, and oat bran above 7 ppb.

## Outputs

The job writes three files:

- `ota_grain_2018_samples.csv`: one row per sample (sample, product, family, origin, detected,
  OTA).
- `ota_grain_2018_crossmethod.csv`: per shared label, n, detected and the count at or above
  0.8 ppb in each file.
- `ota_grain_2018_summary.json`: the gate, every check and prediction with its observed
  values, the census and provenance.

The next run publishes these with a result note and a pinned recompute test that does not
import the grader.
