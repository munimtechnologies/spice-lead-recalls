# tds-ota-2008 0.1.0: Health Canada's open Total Diet Study ochratoxin A file (2008-09) against the paper that reports it — result

RESULT-MARKER: tds-ota-2008-0.1.0-result

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This grades the pre-registration [tds-ota-2008-0.1.0-prereg.md](tds-ota-2008-0.1.0-prereg.md),
which was public first, at tag `v0.4.74`. The sealed job `tds-ota-2008-v1` ran on 2026-10-29 at
07:23 UTC (python:3.12, 1 GB, no host paths). It waited for the registration's marker to be
public, checked that its bundled `tds_ota_2008.py` and `test_tds_ota_2008.py` were byte-identical
to the published copies, ran the offline tests and only then read the two SHA-256-pinned files.
**The gate passed, and 7 of 11 graded items held: two of five consistency checks and all five
blind predictions but one.**

This is a reference comparison of an open file with the paper that reports it, not a compliance
finding and not about any brand. Canada sets no ochratoxin A (OTA) maximum level for these foods;
the paper and later reviews put Canadian OTA exposure far below levels linked to harm in animals.
It is not dietary or medical advice.

## Headlines

1. **The open file reports 14 trace OTA detections that the paper's Table 3 shows as "n.d."** Of
   the 137 composites the file carries, Table 3 prints a measured value for 94 and "n.d." for 43.
   The file matches every one of the 94 printed values at its printed precision (C2 held, 94 of
   94), but for 14 of the 43 "n.d." composites it reports a measured result — an `=` operator with
   a number from 0.001 to 0.004 ng/g, seven in each city-year. So the file's own detection count
   is **108 of 137 (79%)**, against the **94** Table 3 prints and the **"51 of 70 in each year"**
   (73%, 102/140) of the paper's text and abstract: three different detection counts for one
   study. The file is the more complete record. (C1, C4 and P1 all turn on this gap.)
2. **Every value Table 3 prints, the file reproduces, and the two maxima match (C2, C3 held).**
   The highest OTA is semi-moist raisins at 2.348 ng/g in Quebec City (2008) and white wheat
   flour at 1.695 ng/g in Calgary (2009), printed in the paper as 2.3 and 1.7.
3. **The English and French open files agree to the row (P3 held).** All 137 rows pair one-to-one
   by sample code with the same operator class and the same value, even though the portal marks
   the English file's own validation as "failure" and stores the two language copies in different
   row orders. The disagreement is only between the file and the paper's table, not within the
   open data.
4. **The food rankings are stable and cereal-led (P2, P4, P5 held).** The 24 `ng/ml` (liquid)
   rows are exactly Table 3's starred liquids plus the ready-to-use soy infant formula; 16 of the
   top 20 foods by two-year mean contain cereal (the paper's Table 4: 16 of 20); and the Spearman
   correlation between the 2008 and 2009 values of the 67 foods sampled in both cities is **0.81**.
   No composite exceeds any EU OTA level where one applies.

## Data

- **EN:** Health Canada / Government of Canada, "Total Diet Study — mycotoxin results 2008-2009".
  Open Government Portal dataset `71fa9c90-f690-4928-9239-69b4ecbeccee`, resource
  `d1cbf697-ff08-4518-b69f-b633efbfb620`, SHA-256 `3d80ade4…af79` (74,452 bytes, Windows-1252),
  Open Government Licence – Canada. 137 rows, one OTA result per composite, in the CANLINE layout.
- **FR:** resource `237fe2c2-2f86-4ef4-b11d-485a28f8a57a`, SHA-256 `6fd5a225…a171` (86,687 bytes),
  the same 137 rows in a different order.
- **The paper (R1):** Tam J, Pantazopoulos P, Scott PM, Moisey J, Dabeka RW, Richard IDK.
  "Application of isotope dilution mass spectrometry: determination of ochratoxin A in the
  Canadian Total Diet Study". *Food Addit Contam Part A* 2011;28(6):754-761,
  doi:10.1080/19440049.2010.504750, open access as PMC3118520. 140 composites: the same 70 foods
  bought in Quebec City (2008) and Calgary (2009), LC-MS/MS with a ¹³C internal standard,
  recovery-corrected. The file carries 137 of the 140 (Quebec City has no baby-food mixed
  vegetables; Calgary has no beer or wine).

## Gate (passed)

All nine checks held: the SHA-256; 137 rows, one per sample; 69 Quebec City and 68 Calgary rows;
every food name mapped to a Table 3 code, and the 137 food-year pairs exactly Table 3's 140 less
the three the census found missing; one analyte (`Ochratoxin A`); units `ng/g` 113 and `ng/ml` 24;
and every result either `=` with a number above 0 or a below-limit operator (`<LOD/MDL`) with 0,
both kinds present (108 detected, 29 below-limit).

## Graded items: 7 of 11 held

| ID | Registered | Observed in the file | Met |
|---|---|---|---|
| G | gate (above) | 9 of 9 checks | ✅ |
| C1 | detected exactly when Table 3 prints a value (not n.d.) | 14 composites detected where Table 3 is n.d. | ❌ |
| C2 | every detected value rounds to Table 3's figure | 94 of 94 | ✅ |
| C3 | maxima raisins 2.3 (2008), white wheat flour 1.7 (2009) | 2.348, 1.695 | ✅ |
| C4 | the text: 51 detected in each year | 56 (2008), 52 (2009) | ❌ |
| C5 | the text: 47 (2008) and 43 (2009) above the LOQ | 47; 40 (file LOQ) / 41 (paper LOQ) | ❌ |
| P1 | the file follows Table 3: 49 (2008) and 45 (2009) detected | 56, 52 | ❌ |
| P2 | 24 ng/ml rows = Table 3's starred liquids + soy formula | exactly those 24 | ✅ |
| P3 | English and French agree, 137 rows, same operator class and value | all 137 pair | ✅ |
| P4 | ≥ 16 of the top 20 foods by two-year mean are cereal | 16 | ✅ |
| P5 | Spearman rho ≥ 0.7 between the 2008 and 2009 values of shared foods | 0.81 (n = 67) | ✅ |

The three misses C1, C4 and P1 are one finding told three ways: the file detects OTA in 108 of
its 137 composites, more than Table 3's 94 printed values and more than the text's "51 in each
year." C5 is the same at the LOQ: 2008 reproduces the text's 47 exactly, but 2009 is 40 (the
file's own LOQ) or 41 (the paper's), short of the printed 43.

## The 14 composites the file calls detected and Table 3 calls "n.d."

| sample | food | year | file value (ng/g) | Table 3 | paper LOD |
|---|---|---|---|---|---|
| 5583 | Cheese, hard | 2008 | 0.004 | n.d. | 0.008 |
| 5584 | Cheese, processed | 2008 | 0.004 | n.d. | 0.006 |
| 5566 | Desserts (baby food) | 2008 | 0.003 | n.d. | 0.006 |
| 5571 | Dinners, cereal+veg+meat | 2008 | 0.004 | n.d. | 0.002 |
| 5567 | Formula, milk base | 2008 | 0.004 | n.d. | 0.005 |
| 5585 | Popcorn, microwave | 2008 | 0.001 | n.d. | 0.002 |
| 5519 | Soya sauce | 2008 | 0.004 | n.d. | 0.002 |
| 6922 | Rice | 2009 | 0.003 | n.d. | 0.001 |
| 6925 | Baked beans, canned | 2009 | 0.004 | n.d. | 0.003 |
| 6928 | Corn chips | 2009 | 0.003 | n.d. | 0.003 |
| 6930 | Grape juice, bottled | 2009 | 0.003 | n.d. | 0.002 |
| 6934 | Candy | 2009 | 0.002 | n.d. | 0.003 |
| 6935 | Peanut butter | 2009 | 0.002 | n.d. | 0.002 |
| 6947 | Formula, milk base | 2009 | 0.004 | n.d. | 0.005 |

All 14 are `=` results between 0.001 and 0.004 ng/g. Seven sit below the paper's stated LOD for
that food — consistent with Table 3's footnote that values below the estimated LOD are given "for
potential statistical analysis" and so would print as "n.d." — but the other seven sit at or above
the LOD: five strictly above it (the cereal-vegetable-meat dinner at 0.004 against a 0.002 LOD,
soya sauce, rice, baked beans and grape juice) and two exactly at it (corn chips and peanut
butter). So Table 3's "n.d." is not a single clean threshold against the file. Either way, the
open file keeps a quantified estimate where the published table shows none.

## Limits

- Table 3 is read from the open-access PMC copy, transcribed twice and cross-checked, and the
  three composites the file lacks (baby-food mixed vegetables; beer; wine) are excluded from every
  count. One food-name mapping is a judgement call, fixed before grading: `Bologna, Chicken` is
  taken as Table 3's "Pork, cured", the only meat row left once the other six are paired by name.
- "Detected" here is the file's own coding (`=` with a number above 0). It is not a claim about
  the true limit of detection of the method; the point is only that the file and the table draw
  the detect/non-detect line in different places.
- One study, two city-years, 137 composites. The figures describe this file and this paper, not
  OTA in Canadian food in general. Reviews since put the exposure well below levels of concern.
- The EU levels are a reference only (Regulation (EU) 2023/915: dried vine fruit 8.0, wine and
  grape juice 2.0, cereal products 3.0, foods for infants 0.50 µg/kg). Canada has no OTA maximum
  level for these foods. No composite exceeds the level that fits it.

Prior art: on 2026-10-28, searches found the paper (R1), Health Canada's dataset listing (record
last modified 2025-06-11) and reviews that cite the paper's maxima. They found no comparison of
the open file with the paper's table, and no note of the gap between the text's, the table's and
the file's detection counts. As far as we know, this is the first per-row reading of the open
file against the paper.

## Reproduce it

- `data/tds_ota_2008_samples.csv`: one row per composite (sample, food, Table 3 code, city, year,
  operator, raw value, kind, value, unit, LOD, LOQ, and Table 3's printed figure), the sealed
  job's output.
- `data/tds_ota_2008_summary.json`: the sealed grader record (the gate, every check and prediction
  with its observed values, the English/French comparison, the census and provenance).
- `test_tds_ota_2008_result.py`: a pinned test. It does not import the grader. With its own code
  it rebuilds the census counts, C1–C5, P1, P2, P4 and P5, the EU count and the top-20 ranking
  from the CSV, recomputes the Spearman correlation, and checks them against the sealed record.

A sealed follow-up job (`tds-ota-2008-result-v1`) fetches these published files from GitHub and
re-runs the pinned test on them. The grading code `tds_ota_2008.py` and the pre-registration are
at tag `v0.4.74`.
