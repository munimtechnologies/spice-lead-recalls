# Pre-registration: CFIA's open Alternaria toxin files against its report, and against the EU's indicative levels (alternaria 0.1.0)

PREREG-MARKER: alternaria-0.1.0-prereg

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code
Apache-2.0.

**Written before any result value in either file was read.** The figures used below come from
CFIA's report and from a names-only census. Both are recorded in the companion note
[alternaria-report-check-0.1.0.md](alternaria-report-check-0.1.0.md), committed with this one.
The grading code is `alternaria.py`; its offline tests are `test_alternaria.py`. A sealed compute
job grades this registration only after it is public on GitHub. That job checks out the
published code, then reads the SHA-256-pinned files. Nothing here is a finding about any product,
brand or health risk. The EU levels used are indicative levels that trigger investigation, not
maximum levels, and Canada sets no limit for these toxins.

## Data and rules

- **F1:** CFIA's 2014–2022 file, resource `c93db5ad-283a-45e1-8995-f1dc33c9392c`, SHA-256
  `9b79ec39…3722a`. It has 5,190 rows: 2,595 samples, one AOH row and one AME row each, unit
  `ng/g`.
- **F2:** CFIA's 2018–19 file, resource `7e210ca5-2e37-406c-9144-4d0e055d45fd`, SHA-256
  `39ec24c7…5e8`. It has 798 rows: 399 samples, two rows each, with the value in `MaxOfAMOUNT`.
- **Values:** a cell is a non-detect if it is blank, `0`, starts with `<` or is a non-detect
  token. A positive is a plain non-negative decimal. **Any comma or unparseable cell fails the
  gate.** That way an unexpected coding is caught, not misread. The census already shows
  literal zeros in F1, the non-detect coding of CFIA's DON and OTA files.
- **Units:** converted to ng/g (= µg/kg = ppb) through an explicit table. An unknown unit fails
  the gate.
- **Per sample:** the total is AOH + AME, with non-detects counted as 0, which is how the report
  sums them. A sample is positive if its total is above 0. Each report row is reproduced with
  four figures: the minimum positive total, the maximum total, and the average of the positive
  totals.
- **Precision:** a figure "matches" a printed one if it rounds to it at the printed precision,
  to two significant figures for whole numbers with trailing zeros ("870" covers 865–875,
  "200" covers 195–205), and to the printed decimal places otherwise ("0.090" covers
  0.0895–0.0905).
- **Report rows:** each row is mapped to F1's product labels and plan year exactly as in the
  report-check note, for example `Infant Food - Puree` in plan 2019 for the 2019 purée row.

## Gate (G)

For both files: the SHA-256 matches, along with the row and sample counts, two rows per sample
(one AOH, one AME), the component counts, the row count of every product label, and F1's
plan-code row counts. Every unit is in the unit table. Every value cell passes the format rule,
with at least one positive. If the gate fails, nothing below is graded.

## Consistency checks (C1–C17): the report rows the labels identify

Each check needs n and the positive count to match exactly, and the minimum, maximum and average
to match at printed precision ("N/A" cells are skipped).

| id | row (file labels) | n | pos | min | max | avg |
|---|---|---|---|---|---|---|
| C1 | fresh pepper 2020 (4 pepper labels) | 79 | 0 | – | 0 | – |
| C2 | barley-based 2021 | 123 | 78 | 0.093 | 240 | 5.7 |
| C3 | corn-based 2020 (`Cereal - Corn`, `Cereal - Mixed Grains`) | 52 | 37 | 0.20 | 6.7 | 2.0 |
| C4 | wheat-based 2017 | 283 | 247 | 0.090 | 37 | 2.2 |
| C5 | infant purée 2019 | 108 | 94 | 0.52 | 26 | 7.9 |
| C6 | infant purée 2016 | 58 | 42 | 0.20 | 37 | 4.4 |
| C7 | toddler/baby meals 2019 | 90 | 60 | 0.10 | 12 | 1.1 |
| C8 | toddler/baby meals 2016 | 2 | 1 | N/A | 1.2 | N/A |
| C9 | sunflower seeds 2017 (nut/seed 2017) | 34 | 31 | 0.20 | 20 | 5.6 |
| C10 | pomegranate products 2019 | 187 | 124 | 0.060 | 870 | 160 |
| C11 | fruit-based processed 2016 | 333 | 109 | 0.050 | 150 | 3.4 |
| C12 | tomato-based 2016 | 100 | 41 | 0.060 | 350 | 9.4 |
| C13 | sunflower oil 2017 | 41 | 31 | 0.10 | 62 | 5.9 |
| C14 | wine 2014 | 75 | 26 | 0.50 | 11 | 2.6 |
| C15 | wine 2015 | 200 | 141 | 0.092 | 21 | 1.8 |
| C16 | F2 juices 2018 (all juice-type labels except `Juice - Pomegranate`) | 174 | 125 | 0.050 | 570 | 17 |
| C17 | F2 seeds 2018–19 / F2 oils 2018 / F2 overall | 50 / 90 / 399 | 36 / 50 / 232 | 0.054 / 0.10 / 0.050 | 55 / 57 / 573 | 6.0 / 7.1 / – |

C16 also tests the reading in the report-check note that Table 6's 174 juices for 2018 are F2's
juice-type labels without its 5 pomegranate juices.

## Blind predictions on the report's open points (P1–P6)

- **P1 (infant row).** Across all 258 infant samples, 197 are positive, the maximum matches
  **37** (not Table 2's 26), and the average of positives lies in **[4.95, 5.15)** (not 5.2).
  Table 2's maximum and average reflect the 2019 rows only.
- **P2 (Table 1 swap).** At most **24** of the 187 pomegranate-label samples from 2019 have
  `Origin` CANADA. The literal reading of Table 1, with 156 domestic pomegranate products,
  would need about 100 or more.
- **P3 (871 vs 880).** F1's largest summed total matches **880** and belongs to a 2015 tomato-label
  sample. The largest 2019 pomegranate total lies in **[870.5, 871.5)**: Table 2's "871" is the
  pomegranate maximum.
- **P4 (the missing 2015 tomato sample).** The 2015 tomato labels hold 100 samples (a census
  fact). **35 or 36** of them are positive, the minimum matches 0.080 and the maximum matches 880.
- **P5 (file totals).** F1 has **1,552–1,554** positive samples (the report has 1,554 of 2,597;
  the file lacks 2), and its smallest positive total matches **0.046**.
- **P6 (F2 beer).** Beer is in no table. If C16 and C17 hold, beer positives plus
  pomegranate-juice positives must equal 232 − 125 − 36 − 50 = 21. The prediction is that all
  **5** pomegranate juices are positive (F1's pomegranate juices are 98–99% positive in the
  report), so beer positives are **16 of 80**.

## Blind predictions against EU Recommendation 2022/553 (E1–E5): the new part

CFIA's report gives only AOH + AME sums. The EU's indicative levels are per toxin, so this is
the first comparison of CFIA's open retail data with them. "Exceeds" means AOH above its level
**or** AME above its level.

- **E1 (processed tomato products, AOH 10 / AME 5).** Of the 200 tomato-label samples from 2015
  and 2016, **2 to 4** exceed. The report's arithmetic suggests only two large totals: 880 in
  whole tomato and 350 in diced tomato. A1's other tomato rows have maxima of 3.9 to 5.2.
- **E2 (sunflower and sesame seeds, 30 / 30).** At most **1** of the 51 sunflower-seed-label
  samples exceeds (F1 2017: 34, F2: 17), and **none** of F2's 3 sesame seeds.
- **E3 (sunflower oil, 10 / 10).** Of the 51 sunflower-oil-label samples (F1 2017: 41, F2: 10),
  **2 to 8** exceed.
- **E4 (which toxin dominates).** In sunflower seeds and oil pooled (F1 + F2), **AME** carries
  more than half of the summed AOH + AME mass. In the fruit-based rows pooled (2019 pomegranate,
  wine, 2015–16 tomato), **AOH** carries more than half. Both halves must hold.
- **E5 (infant purées, reference only).** The EU's 2 / 2 level is for *cereal-based* infant food,
  and CFIA's are fruit and vegetable purées, so this is a benchmark, not an applicable level. The
  prediction is that **25–60%** of the 166 purées (2016 + 2019) have AOH or AME above 2 ng/g.

## Outputs

The job writes `alternaria_samples.csv`, one row per sample (file, sample, plan, product, origin,
category, AOH, AME, total), and `alternaria_summary.json` (gate, every check and prediction with
its observed values, per-category statistics, the census, provenance). The next run publishes
these with a result note and a pinned recompute test that does not import the grader.
