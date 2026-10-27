# CFIA's Alternaria toxin surveys 2014-2022: what the report and the file labels say (alternaria-report-check 0.1.0)

REPORT-CHECK-MARKER: alternaria-report-check-0.1.0

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0.

This note records CFIA's final report on its *Alternaria* toxin surveys, together with the
names-only census of the two open per-sample files behind them. **It was written before any
result value in either file was read.** A pre-registered check of the files follows
(`alternaria 0.1.0`). Its predictions are fixed against the figures below, which this note makes
public first. The note makes no finding about any product or brand, and it is not a health-risk
claim: Health Canada judged the levels found "not expected to pose a concern to human health".

## Sources

- **Report:** CFIA, "*Alternaria* in Selected Foods – April 1, 2014 to March 31, 2018 and April
  1, 2019 to March 31, 2022", Food chemistry – Targeted surveys – Final report. Web page
  `inspection.canada.ca/en/food-safety-industry/food-chemistry-and-microbiology/food-safety-testing-reports-and-journal-articles/alternaria-selected-foods`,
  "Date modified: 2023-03-16". The same report is also a PDF
  (`alternaria_in_selected_foods_1677269941678_eng.pdf`). We read the web tables on 2026-10-27.
- **File F1:** Open Government Portal dataset `8888649b-c059-4f76-ae0f-30ab6c1159c5` (created
  2026-07-22), CSV resource `c93db5ad-283a-45e1-8995-f1dc33c9392c`, SHA-256
  `9b79ec399c2d7e016ee52aef0279767b68e9d09f8fbda3316e772bf1cca3722a` (925,935 bytes, UTF-8 with
  BOM). It has 5,190 rows: 2,595 samples, each with one alternariol (AOH) row and one alternariol
  monomethyl ether (AME) row. All rows use one unit (`ng/g`) and seven plan codes (`2014_TS025` to
  `2021_TS025`; there is no 2018 code). Results are numeric, with literal zeros and no comma
  decimals.
- **File F2:** dataset `c97c7e25-7acc-449a-91f1-1ac811490ec4`, "*Alternaria* in Beer, Juices,
  Oils and Seeds – April 1, 2018 to March 31, 2019", CSV resource
  `7e210ca5-2e37-406c-9144-4d0e055d45fd`, SHA-256
  `39ec24c7b20ab71334cf1915ef790a48a3d2a0abf5b9c7068f35a2e6557ac5e8` (147,136 bytes, cp1252).
  It has 798 rows: 399 samples, two rows each (AOH, AME), with the value in a `MaxOfAMOUNT`
  column. The report cites this survey as its footnote 7.
- Both censuses come from sealed job `myco-census-v2` (2026-10-25). That job read headers,
  labels and counts only.
- All data are under the Open Government Licence – Canada.

## What the report prints

The report gives AOH + AME as one summed total per sample. It gives no limit of detection or
quantification. Table 2 (n, positives (%), min, max, average of positives, ppb):

| Product type | n | positive | min | max | avg |
|---|---|---|---|---|---|
| Fresh pepper | 79 | 0 (0) | 0 | 0 | 0 |
| Grain-based foods | 755 | 610 (81) | 0.090 | 240 | 4.2 |
| Infant foods | 258 | 197 (76) | 0.10 | 26 | 5.2 |
| Juices | 217 | 82 (38) | 0.050 | 340 | 6.0 |
| Nut/seed products | 147 | 96 (65) | 0.046 | 20 | 2.8 |
| Pomegranate products | 243 | 179 (74) | 0.060 | 870 | 165 |
| Processed fruits and vegetables | 582 | 192 (33) | 0.050 | 880 | 8.7 |
| Sunflower oil | 41 | 31 (76) | 0.10 | 62 | 5.9 |
| Wine | 275 | 167 (61) | 0.092 | 21 | 1.9 |
| **Total** | **2597** | **1554 (60)** | **0.046** | **871** | **23** |

Tables 3 to 11 split these by survey year (the CFIA rows; n, positives, min, max, average):
fresh pepper 2020 79, 0. Barley-based 2021 123, 78, 0.093–240, 5.7. Corn-based 2020 52, 37,
0.20–6.7, 2.0. Rice-based 2020 53, 37, 0.10–2.3, 0.80. Wheat-based 2021 122, 99, 0.10–29, 2.2;
2020 1, 1, 3.5; 2017 283, 247, 0.090–37, 2.2. Infant puree 2019 108, 94, 0.52–26, 7.9; 2016 58,
42, 0.20–37, 4.4. Toddler/baby meals 2019 90, 60, 0.10–12, 1.1; 2016 2, 1, 1.2. Juices 2015 147,
72, 0.050–340, 6.6; 2014 75, 15, 0.20–200, 28; 2018 174, 125, 0.050–570, 17. Nut/seed 2020 113,
65, 0.046–6.2, 1.4; 2017 34, 31, 0.20–20, 5.6; 2018–19 50, 36, 0.054–55, 6.0. Pomegranate 2019
187, 124, 0.060–870, 160; 2015 51, 50, 2.6–620, 180. Processed fruit (fruit-based) 2016 333, 109,
0.050–150, 3.4; tomato-based 2016 100, 41, 0.060–350, 9.4; 2015 101, 36, 0.080–880, 25. Sunflower
oil 2017 41, 31, 0.10–62, 5.9; oils 2018 90, 50, 0.10–57, 7.1. Wine 2015 200, 141, 0.092–21, 1.8;
2014 75, 26, 0.50–11, 2.6. Appendix Table A1 breaks each category into product types. Within
each category its counts and positives sum exactly to Table 2's figures.

## Seven things the report's own arithmetic shows

1. **Table 1 swaps two rows.** Table 1 lists pomegranate products as 582 samples (156 domestic)
   and processed fruits and vegetables as 243 (24 domestic). Table 2 has the reverse: 243 and 582.
   Table 2 is the consistent one. Its percentages fit only that way round (179/243 = 74%,
   192/582 = 33%), and Appendix A1's pomegranate rows sum to 243 samples and 179 positives, its
   processed fruit and vegetable rows to 582 and 192. Read as printed, Table 1 would put 156
   Canadian-origin samples among the pomegranate products.
2. **The total maximum is below a row maximum.** Table 2's Total row prints a maximum of 871
   ppb. Its processed fruit and vegetables row prints 880, as do the summary and results text,
   Table 9 (tomato-based, 2015) and A1 (whole tomato). A total maximum cannot be lower than the
   maximum of one of its rows. One reading is that 871 is the pomegranate maximum (printed as 870
   at two significant figures) and was copied into the Total.
3. **The infant row matches 2019 alone.** Table 2 prints infant foods as 258 samples and 197
   positives, with a maximum of 26 and an average of 5.2. Table 5's 2016 purée row has a
   maximum of 37 (A1's fruit purées agree). The four Table 5 rows, weighted by their positives,
   give an average of 5.00–5.10 even allowing for rounding, not 5.2. The 2019 rows alone (purée
   and meals, 154 positives) give a maximum of 26 and an average of 5.20–5.30. So the counts
   cover both years, but the maximum and average look like they cover 2019 only.
4. **Five samples move between juices and pomegranate.** Table 6's 2014 and 2015 juice rows sum
   to 222 samples and 87 positives, against Table 2's 217 and 82. Table 8's pomegranate rows sum
   to 238 and 174, against 243 and 179. The difference is the same five positive samples in each
   case. They are counted as juices by year and as pomegranate products in Table 2 and A1.
5. **Table 9 leaves out 48 processed peppers.** Its rows sum to 534 samples and 186 positives,
   against Table 2's 582 and 192. A1 lists 27 processed "Pepper" (1 positive) and 21
   "Pepper – Hot" (5 positive) samples, which make up exactly the 48 and 6. The file places them
   in 2020.
6. **Sorghum is in the total but has no row.** Table 4's CFIA rows sum to 634 grain-based
   samples and 499 positives, against Table 2's 755 and 610. Table 4 has a sorghum row with
   literature values only. The gap implies 121 sorghum-based samples with 111 positives (92%,
   the highest detection rate of any grain) and an average of about 11 ppb among the positives.
   The report prints none of these figures.
7. **Cherry juice's average exceeds its maximum.** A1 prints cherry juice as 2 samples, both
   positive, at 7.6 and 8.7 ppb, with an average of 16. The mean of 7.6 and 8.7 is 8.15. 16 is
   close to their sum (16.3).

The report also says there are no regulated limits for these toxins "in Canada or elsewhere in
the world". Strictly, that is accurate. But in Commission Recommendation (EU) 2022/553 (5 April
2022) the EU set **indicative levels**, which trigger investigation and are not maximum levels. They
are set per toxin, in µg/kg (= ng/g; AOH / AME): processed tomato products 10 / 5, sesame seeds
30 / 30, sunflower seeds 30 / 30, sunflower oil 10 / 10, and cereal-based foods for infants and
young children 2 / 2. The report gives only AOH + AME sums, so it cannot be compared with these.
The open file gives each toxin separately.

## What the file labels say (names only)

The report's 2,597 samples are 2 more than the file's 2,595. Adding up the year-specific rows of
Tables 3–11, plus the two derived groups (48 processed peppers in 2020, 121 sorghum in 2021),
gives the report's samples by year. They match the file's plan codes exactly in 2016 (493), 2017
(358), 2019 (385), 2020 (346) and 2021 (366). Both missing samples fall in the first two years:

- **2014:** the report has 150 (75 juices + 75 wine); the file has 149 (75 wine + 74 others).
- **2015:** the report has 499 (147 juices + 51 pomegranate + 101 tomato-based + 200 wine); the
  file has 498. Its tomato labels (`Tomato Sauce` 91, `Tomato` 6, `Tomato - Organic` 3) give
  100 against 101. Its juice and pomegranate labels give 198 = 147 + 51 exactly.

For most report rows the file's product labels identify the samples exactly:

- **Fresh pepper 2020, 79:** `Pepper - Fresh` 40, `Pepper - Organic` 5, and 34 samples carrying
  `Pepper - Hot - Fresh` or `Pepper (GH)`. One of those samples has one row under each label:
  27 AOH rows and 26 AME rows for the first, 7 and 8 for the second.
- **Wine:** 75 in 2014 and 200 in 2015. **Sunflower oil 2017:** 41.
- **Infant foods, 258:** purée 58 (2016) + 108 (2019) and `Infant Food (non-cereal)` 2 (2016)
  + 90 (2019). Every Table 5 row matches.
- **Barley-based 2021, 123:** `Grain - Barley` 97 + `Barley Products` 26.
- **Corn-based 2020, 52:** `Cereal - Corn` 44 + `Cereal - Mixed Grains` 8.
- **Wheat-based 2017, 283:** `Flour - Wheat` 147, `Couscous` 68, `Wheat Products` 65,
  `Cereal` 2, `Cereal - Adult` 1.
- **Nut/seed 2017, 34:** `Seed - Sunflower` 34.
- **Pomegranate 2019, 187:** `Pomegranate` 94 (A1's arils 40 + fresh fruit 51 + seeds 3),
  `Juice - Pomegranate` 73, `Juice - Blend` 16, `Beverage - Fruit` 4 (A1's 4 pomegranate drinks).
- **Tomato-based 2016, 100:** `Tomato Sauce` 98 + `Tomato` 2.
  **Fruit-based 2016, 333:** every other 2016 label except the infant foods.

Two report rows cannot be recovered from the labels:

- **2020 nut/seed (113).** A1 lists 34 almond, 32 peanut, 18 mixed-nut and 12 mixed-seed
  samples among them, but the only file label that names a nut is `Mixed Fruit & Nuts` (1
  sample). By count, the 113 sit among 167 samples labelled `Snack Bar` 41, `Cereal - Rice` 48,
  `Crackers` 40, `Protein Bar` 19, `Granola/Cereal Bar` 17, `Rice Products` 1 and
  `Mixed Fruit & Nuts` 1. These 167 are exactly rice 53 + wheat 1 + nut/seed 113.
- **2021 wheat (122) and sorghum (121).** The file's sorghum labels (`Grain - Sorghum` 32,
  `Sorghum Products` 87) give 119, and its wheat-type labels 124. So the file and the report
  disagree on 2 products.

Origin: the file's `Origin` labels give 713 CANADA, 697 UNKNOWN and 1,185 samples from 43
named foreign origins. The report has 714 domestic, 702 unspecified and 1,181 imported. The 44
named origins (Canada included) match the report's "44 countries". The file's separate
`Function` column (Domestic 713, Import 1,364, Unknown 518 samples) matches neither split.

**File F2 (2018–19)** is the survey behind the report's 2018 rows: 174 juice-type samples (all
juices, nectars, cider and `Beverage - Other`, leaving out the 5 `Juice - Pomegranate`), matching
Table 6. Its 50 seeds (sunflower 17, pumpkin 12, flax 10, chia 8, sesame 3) match Table 7, and its
90 oils (10 kinds) match Table 10. It also has 80 **beers**, which appear in no table of the
2014–2022 report. The dataset page gives 232 of 399 samples (58%) positive, ranging from 0.050
to 573 ppb.

## Next

A pre-registration (`alternaria 0.1.0`) fixes, before any value is read: which reading of each
point above the file supports, a reproduction of every report row the labels identify, and the
first per-toxin comparison of Canadian retail foods with the EU's 2022 indicative levels.
