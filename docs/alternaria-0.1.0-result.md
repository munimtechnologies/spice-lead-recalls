# alternaria 0.1.0: CFIA's open Alternaria toxin files against its report and the EU's indicative levels — result

RESULT-MARKER: alternaria-0.1.0-result

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This grades the pre-registration [alternaria-0.1.0-prereg.md](alternaria-0.1.0-prereg.md) and its
companion [report-check note](alternaria-report-check-0.1.0.md). Both were public first, at tags
`v0.4.63` and `v0.4.62`. The sealed job `alternaria-v1` ran on 2026-10-27 at 15:51 UTC (python:3.12,
1 GB, no host paths). It waited until both notes were public, checked that its bundled
`alternaria.py` and `test_alternaria.py` were byte-identical to the published copies, ran the
offline tests, and only then read the two SHA-256-pinned files.
**The gate passed. 17 of 29 graded items held: 11 of 17 consistency checks, 2 of 6 report
predictions and 3 of 5 EU predictions.**

This is a reference comparison, not a compliance finding. The EU levels used are *indicative*
levels that trigger investigation; they are not maximum levels. Canada sets no limit for these
toxins. It is not a finding about any brand, and it is not dietary or medical advice. Health
Canada judged the levels CFIA found "not expected to pose a concern to human health".

## Headlines

1. **The report's two largest tomato results are not in the open file.** CFIA's report prints
   880 ppb (AOH + AME) for a 2015 whole tomato and 350 ppb for a 2016 tomato-based product. No
   sample in the 2014–2022 file comes near either value. Its largest tomato-label total is
   **6.72 ppb**, and its only total above 700 ppb is the 871 ppb 2019 pomegranate juice. So
   Table 2's "Total" maximum of 871 is the file's true maximum, and the 880 printed elsewhere is
   the figure the file does not hold. P3 and P4 assumed the opposite and missed.
2. **The whole gap between report and file sits in four rows.** The report has 2,597 samples and
   1,554 positives; the file has 2,595 and 1,551. Rebuilt row by row, every other report row
   matches the file exactly on samples and positives. The 2 missing samples and 3 missing
   positives fall in 2014–15 juices and pomegranate (one positive sample fewer), 2015 tomato
   products (one sample fewer), 2016 tomato products (one positive fewer) and 2014 wine (one
   positive fewer). The rows holding the two missing tomato extremes are among them.
3. **First per-toxin comparison of CFIA's open retail data with EU Recommendation 2022/553.**
   CFIA's report gives only AOH + AME sums, so it cannot make this comparison; the file can. **3 of
   51 sunflower oils** exceed the sunflower-oil level (AOH 10 / AME 10 µg/kg), and **2 of 3
   sesame seeds** exceed the sesame level (30 / 30). No sunflower seed (0 of 51) and no processed
   tomato product (0 of 200) does. The tomato result follows from headline 1: the only tomato
   values that would have exceeded are the two the file does not hold.
4. **Two of the report's internal contradictions are settled as predicted.** The infant row's
   maximum (26) and average (5.2) cover 2019 alone (P1), and Table 1 swaps the pomegranate and
   processed fruit and vegetable rows (P2).

## Data

- **F1:** CFIA, *Alternaria* in selected foods 2014–2022, resource
  `c93db5ad-283a-45e1-8995-f1dc33c9392c`, SHA-256 `9b79ec39…3722a`. It has 2,595 samples, each
  with one AOH row and one AME row.
- **F2:** CFIA, *Alternaria* in beer, juices, oils and seeds 2018–19, resource
  `7e210ca5-2e37-406c-9144-4d0e055d45fd`, SHA-256 `39ec24c7…5e8`. It has 399 samples.
- Both are under the Open Government Licence – Canada. Every value cell passed the registered
  format rule: F1 has 2,606 positive cells and 2,584 literal zeros, and F2 has 370 and 428, with
  no comma, `<` or text cell. All units are `ng/g`. A sample's total is AOH + AME, with
  non-detects as 0, which is how the report sums them.

## Consistency checks (C1–C17): 11 of 17 held

Each check needs n and positives to match exactly, and the minimum, maximum and average of
positives to match at printed precision.

| ID | Report row | Printed n / pos / min / max / avg | File | Met |
|---|---|---|---|---|
| C1 | fresh pepper 2020 | 79 / 0 / – / 0 / – | 79 / 0 | ✅ |
| C2 | barley-based 2021 | 123 / 78 / 0.093 / 240 / 5.7 | 123 / 78 / 0.093 / 237.6 / 5.75 | ✅ |
| C3 | corn-based 2020 | 52 / 37 / 0.20 / 6.7 / 2.0 | 52 / 37 / 0.20 / 6.72 / 2.01 | ✅ |
| C4 | wheat-based 2017 | 283 / 247 / 0.090 / 37 / 2.2 | 283 / 247 / 0.090 / 37.3 / 2.18 | ✅ |
| C5 | infant purée 2019 | 108 / 94 / 0.52 / 26 / 7.9 | 108 / 94 / 0.518 / 25.94 / 7.87 | ✅ |
| C6 | infant purée 2016 | 58 / 42 / 0.20 / 37 / 4.4 | 58 / 42 / 0.20 / 37.1 / 4.45 | ✅ |
| C7 | toddler/baby meals 2019 | 90 / 60 / 0.10 / 12 / 1.1 | 90 / 60 / 0.10 / 11.94 / 1.09 | ✅ |
| C8 | toddler/baby meals 2016 | 2 / 1 / – / 1.2 / – | 2 / 1 / – / 1.218 | ✅ |
| **C9** | sunflower seeds 2017 | 34 / 31 / 0.20 / 20 / **5.6** | 34 / 31 / 0.20 / 20.46 / **5.651** | ❌ |
| C10 | pomegranate products 2019 | 187 / 124 / 0.060 / 870 / 160 | 187 / 124 / 0.060 / 871 / 162.2 | ✅ |
| C11 | fruit-based processed 2016 | 333 / 109 / 0.050 / 150 / 3.4 | 333 / 109 / 0.050 / 146.31 / 3.39 | ✅ |
| **C12** | tomato-based 2016 | 100 / **41** / 0.060 / **350** / **9.4** | 100 / **40** / 0.060 / **6.72** / **1.02** | ❌ |
| C13 | sunflower oil 2017 | 41 / 31 / 0.10 / 62 / 5.9 | 41 / 31 / 0.10 / 62.3 / 5.93 | ✅ |
| **C14** | wine 2014 | 75 / **26** / 0.50 / **11** / **2.6** | 75 / **25** / 0.50 / **6.0** / **2.04** | ❌ |
| **C15** | wine 2015 | 200 / 141 / 0.092 / **21** / **1.8** | 200 / 141 / 0.092 / **10.6** / **1.68** | ❌ |
| **C16** | F2 juices 2018 (without pomegranate juice) | 174 / **125** / 0.050 / 570 / **17** | 174 / **120** / 0.050 / 573 / **7.47** | ❌ |
| **C17** | F2 seeds / oils / overall | seeds min **0.054**; rest as printed | seeds min **0.113**; oils and overall all match | ❌ |

What the misses mean:

- **C12 (2016 tomato).** The report's row sum is 41 × 9.4 (383.4–387.5 at printed precision);
  the file's is 40 × 1.02 = 40.9. The difference, 342–347 ppb, is one positive result of about
  345 ppb, consistent with the printed maximum "350" at two significant figures. The file has
  the same 100 samples but holds that result as a non-detect or not at all. No 2016 sample in the
  file has a total above 146.
- **2015 tomato (graded under P4).** The report has 101 samples, 36 positive, max 880, average 25
  (row sum 882–918). The file has 100 samples, 36 positive, max 3.91, sum 26.2. The difference
  (856–892) fits one result near 880 ppb. Because the positive counts are equal, the file's row
  must also differ from the report's in at least one other sample.
- **C14, C15 (wine).** The report's wine maxima (11 in 2014, 21 in 2015) are nearly twice the
  file's (6.0 and 10.6), and its averages are higher. The 2014 row also has one positive more.
  In 2014 the gap in the row sum (15–18 ppb) is larger than one extra result of at most 11.5 ppb
  could make, so more than one wine sample differs. We cannot tell from the file which.
- **C16 (2018 juices).** The printed positives (125) and average (17) reproduce exactly once F2's
  5 pomegranate juices are added: 120 + 5 = 125 positives, and (896.9 + 1,246.5) / 125 = 17.1.
  The printed n (174) matches the file only without them. So Table 6's 2018 juice row counts the
  pomegranate juices among its positives but not in its sample size. With that reading F2's
  totals close exactly: 232 positives = 125 juices (with pomegranate) + 36 seeds + 50 oils + 21
  beers.
- **C9 and C17 are small.** For C9, the 2017 sunflower-seed average is 5.651, which rounds to 5.7,
  not 5.6. The row sum would have to be 0.04 ppb lower. For C17, the F2 seed minimum is 0.113, not
  0.054; the seed n, positives, maximum and average all match.

## Report predictions (P1–P6): 2 of 6 held

| ID | Prediction | Observed | Met |
|---|---|---|---|
| P1 | All 258 infant samples: 197 positive, max 37, average 4.95–5.15 (Table 2's 26 and 5.2 are 2019-only) | 258 / 197, max 37.1, avg **5.04**. The 2019 rows alone give max 25.94 and avg 5.23. | ✅ |
| P2 | At most 24 of the 187 2019 pomegranate samples have Origin CANADA (Table 1 swaps two rows) | **13** of 187 | ✅ |
| P3 | F1's largest total matches 880 and is a 2015 tomato; the pomegranate maximum is 870.5–871.5 | Largest total **871.0**, a 2019 pomegranate juice. No total near 880. | ❌ |
| P4 | 2015 tomato labels: 100 samples, 35–36 positive, min 0.080, max 880 | 100 / 36 / 0.080 / max **3.91** | ❌ |
| P5 | F1 has 1,552–1,554 positives; smallest positive total 0.046 | **1,551**; smallest **0.050** | ❌ |
| P6 | F2: all 5 pomegranate juices positive, 16 of 80 beers positive | 5 of 5; beers **21** of 80 | ❌ |

P3, P4 and P5 all missed for the same reason as C12. The prediction assumed the 880 ppb tomato was
in the file and that the report's 871 was a copying slip. It is the other way round. P5's 0.046 is
the report's 2020 nut/seed minimum. The file's 2020 snack, cereal, cracker and nut group has a
minimum of 0.091, so that value is not in the file either. P6 missed because C16's 125 already
includes the pomegranate juices, which leaves 21 positives, not 16, for beer. Beer is in no table
of the report: 21 of F2's 80 beers (26%) carry AOH or AME, at most 1.17 ppb.

## EU Recommendation 2022/553 (E1–E5): 3 of 5 held

"Exceeds" means AOH above its level **or** AME above its level (µg/kg = ng/g).

| ID | Food (levels AOH / AME) | Prediction | Observed | Met |
|---|---|---|---|---|
| E1 | processed tomato products (10 / 5), 200 samples 2015–16 | 2–4 exceed | **0** (largest AOH 6.22, AME 0.90) | ❌ |
| E2 | sunflower seeds (30 / 30), 51; sesame seeds (30 / 30), 3 | ≤ 1 sunflower, 0 sesame | sunflower **0**; sesame **2 of 3** | ❌ |
| E3 | sunflower oil (10 / 10), 51 | 2–8 exceed | **3** | ✅ |
| E4 | which toxin dominates | AME > 50% of mass in sunflower; AOH > 50% in fruit | AOH share 38.9% in sunflower seeds and oil; **75.0%** in pomegranate, wine and tomato | ✅ |
| E5 | infant purées, 2 / 2 (benchmark only) | 25–60% above | **79 of 166 (47.6%)** | ✅ |

The samples above an EU indicative level:

| File | Sample | Year | Product label | Origin label | AOH | AME | Over |
|---|---|---|---|---|---|---|---|
| F1 | C2017ALTN00049 | 2017 | Oil - Sunflower | CANADA | 11.4 | 8.88 | AOH |
| F1 | C2017ALTN00296 | 2017 | Oil - Sunflower | CANADA | 11.9 | 50.4 | both |
| F1 | C2017ALTN00309 | 2017 | Oil - Sunflower | CANADA | 10.2 | 43.0 | both |
| F2 | C2018ALTN00379 | 2018 | Seed - Sesame | CANADA | 1.4 | 53.7 | AME |
| F2 | C2018ALTN00397 | 2018 | Seed - Sesame | INDIA | 34.7 | 16.1 | AOH |

E5 is a benchmark, not an applicable level: the EU's 2 / 2 level is for *cereal-based* foods for
infants and young children, and CFIA's purées are fruit and vegetable purées. The sesame count is
3 samples, too few for a rate. Origin is CFIA's label for the product, not necessarily where the
seed or oil was grown.

## What this settles, and what it does not

- **Settled from the file:** Table 1's swap; the 2019-only infant maximum and average; how
  Table 6's 2018 juice row treats pomegranate juice; that sorghum and the 2020 nut/seed group sit
  where the report-check note placed them (their merged rows match exactly: 243 / 210 and
  167 / 103); and where the 2-sample, 3-positive gap lies.
- **Not settled:** *why* the open file lacks the report's 880 and ~345 ppb tomato results and its
  higher wine values. The data may have been corrected after the report, the report may have used
  a different extract, or the report may contain errors. The file cannot tell these apart. Only
  CFIA can.
- **Limits:** the tomato, wine and juice reconciliations use the report's rounded figures, so
  they give ranges, not single values. The EU comparison uses CFIA's sample results as
  published. It does not apply measurement uncertainty or the EU's LOQ requirements. Tenuazonic
  acid, which also has EU indicative levels, was not measured.

Prior art: a search on 2026-10-27 found Health Canada's 2012 study of AOH and AME in 83 Canadian
grain foods (Scott et al.) and the EU Recommendation itself. We found no comparison of CFIA's
open per-sample *Alternaria* data with the 2022/553 indicative levels, and no published
reconciliation of the report with its open files. As far as we know, both are first here.

## Reproduce it

- `data/alternaria_samples.csv`: one row per sample (file, sample, plan, product, origin,
  category, AOH, AME, total; 2,994 rows), the sealed job's output.
- `data/alternaria_summary.json`: the sealed grader record (gate, C1–C17, P1–P6, E1–E5,
  per-category statistics, census, provenance).
- `test_alternaria_result.py`: a pinned test. It rebuilds every category from the per-sample
  table with its own label mapping, which does not import the grader, and checks the result
  against the sealed record. It then recomputes every figure quoted above: the four-row
  reconciliation, the infant and pomegranate figures, the juice arithmetic and the EU
  exceedances.

A sealed follow-up job (`alternaria-result-v1`) fetches these published files from GitHub and
re-runs the pinned test on them. The grading code `alternaria.py` and the pre-registration are at
tag `v0.4.63`.
