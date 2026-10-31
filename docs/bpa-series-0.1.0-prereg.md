# Nine years of CFIA bisphenol A surveys: predictions fixed before seven open files are read (bpa-series 0.1.0)

PREREG-MARKER: bpa-series-0.1.0-prereg

Made with AI agents working in MV2's (Munim, Inc.) name. Text CC BY 4.0; code Apache-2.0.
Not a compliance finding, not about any product or brand, and not dietary or medical advice.

## What this is

The Canadian Food Inspection Agency (CFIA) has tested canned and packaged foods for bisphenol A
(BPA) in targeted surveys since 2009, and publishes a per-sample CSV for each survey on
open.canada.ca (Open Government Licence - Canada). The 2018-19 and 2020-21 files are already
registered in `docs/bpa-pah-report-0.1.0-prereg.md`. This note fixes predictions about the seven
earlier files **from the printed report pages alone**, before any census or value of the files is
read:

| Short name | Report (inspection.canada.ca slug) | Open file (dataset / resource) | Portal size, MD5 |
|---|---|---|---|
| bpa-2009 | 2009-2010 Bisphenol-A in infant food and formula (`bisphenol`) | 9846894f-16f2-4834-952a-2e66a162719b / 4ff8f342-d0ea-45a4-9cf5-6f5220e84925 | 32,261 B, 7eacc09417bd528dcca26b8009b824f5 |
| bpa-2010 | 2010-2011 Bisphenol A in infant formula and foods (`2010-2011-bisphenol`) | ee1d2ca0-18a4-457a-9978-59d20cc6e191 / ab208fba-5551-4d16-87a7-b810a73dbcba | 39,475 B, 56b061a4596746dc9736afabac5fbc2a |
| bpa-2011 | 2011-2012 Bisphenol A in canned foods (`bisphenol-canned-foods`) | 3c1749ef-d6a2-400d-a096-8dd5a13507b2 / 86eb4b33-11b4-475d-a0ff-3f32a611a73e | 69,780 B, afae926b6784187c1b15c19f16c928ef |
| bpa-2012 | 2012-2013 Bisphenol A in canned foods (`bisphenol-canned-foods-0`) | d0539c7a-90ea-4874-a66d-7c75f6cd814d / c2f6fb46-4c3f-4c23-acfb-4badfc70c835 | 87,982 B, 5da0bea9d42e56c68b0423b63cfacb96 |
| bpa-2013 | 2013-2014 Bisphenol A in canned foods (dataset description; the report page now returns 404) | eba65062-23e4-4530-90bd-767d0c04c079 / 755045de-88a0-4ad7-8015-e630d9ca8fcd | 94,214 B, no MD5 listed |
| bpa-2016 | BPA and alternatives in selected foods, April 1, 2016 to March 31, 2017 (`bisphenol-and-bpa-alternatives-selected-foods`) | 10478dd5-7ce8-4542-887c-572f0bfe0c8c / 26aa5b60-08a4-4bad-bbdc-17527e6698a3 | 395,585 B, no MD5 listed |
| bpa-2017 | BPA and alternatives in canned meat, fish and seafood, April 1, 2017 to March 31, 2018 (`bisphenol-and-bpa-alternatives`) | 15b7f392-56ef-4772-a8e5-aba2c3b0b980 / 4dfc8b9a-0b97-4c76-b3e4-07879a8e0c88 | 339,854 B, 12a495421962033f4c723492e49682fa |

Order of work: (1) this note is committed with the census code `bpa_series_census.py` and its
offline tests; (2) the sealed job `bpa-series-census-v1` waits until this note is public, then runs
a names-only census of all seven files (rows, samples, labels, units; every result cell classified
by shape only; numbers are never printed, summed or compared); (3) the census grades the items
marked **[census]**; (4) a grader fixed in a later commit, after the census and before any value
is read, grades the items marked **[values]**, with the label-to-category mapping stated in that
commit.

Rules for the value items: a sample is "positive" for an analyte when its value is a number above
0; averages are over positives only (the 2016-17 and 2017-18 reports say so; the earlier pages
print no average); ppm is converted to ppb (x 1000); a printed figure matches when the file's
value is within half a unit of its last printed digit; a printed percentage matches when the
file's count gives it after rounding. An item that needs a label the file lacks is reported as
ungraded, not as a miss.

Searches on 2026-10-31 found no earlier per-sample analysis of these seven open files, no check of
them against the printed reports, and no multi-year series built from them. Health Canada's
published BPA trend work uses Total Diet Study composites, not these CFIA survey files.

## Printed figures (ppb unless stated)

- **bpa-2009** (no tables). 200 samples: 100 infant food (cereals, fruit and vegetable purees,
  mixed meals) and 100 infant formula (powdered, ready-to-serve, concentrated). 59% without
  detectable BPA. None detected in powdered formula or infant cereal; infant food 9%;
  ready-to-serve formula 65%; concentrated formula 100% (all in metal cans). By package: metal cans
  70 of 89 (79%); glass jars with metal lids 12 of 32 (38%); none in plastic, paper-plastic or
  paper-metal. Range 1.4 to 9.6.
- **bpa-2010** (no tables). 234 samples, October 2010 to March 2011, 11 cities: 127 dairy and soy
  infant formula, 92 fruit products, 15 fruit juices. BPA not detected in any sample.
- **bpa-2011** (no tables). 403 samples, April 2011 to March 2012, 11 cities: 101 fruit products,
  50 juices/beverages, 151 vegetables/legumes, 101 pastas/soups. Not detected in 98.5%. Six
  positives: one pasta in tomato sauce, three whole-style cut carrots, one tender peas, one
  cream-style corn; none in fruit products, juices, beverages or soups.
- **bpa-2012** (no tables). 576 samples: 217 pastas/soups, 144 vegetables/legumes, 73 fruit
  products, 72 juices/beverages, 46 coconut milks, 24 curry products. 145 positives (74.8% not
  detected); every category had a positive. Range 0.0052 ppm (a canned pasta) to 0.381 ppm (a
  coconut milk).
- **bpa-2013** (dataset description). 391 samples: 93 pastas/soups, 70 vegetables, 55 infant
  formula, 54 juices/beverages, 43 ready-to-consume energy/sports/soft drinks, 38 fruit products,
  20 pie fillings, 13 coconut milks, 5 curry products. Not detected in 35.5%. Range 0.001 ppm (a
  tropical fruit salad) to 0.565 ppm (a corn).
- **bpa-2016** Table 1: canned 76 domestic, 287 imported, 101 unspecified, 464; other packaging
  3, 13, 11, 27; total 491. Table 2 (canned BPA; n, positive, min, max, average): beverages 135,
  91, 1.7, 639, 40.8; coconut milk 14, 12, 24.2, 1370, 306; fruit 50, 34, 2.0, 1160, 62.1; infant
  formula 66, 46, 2.3, 44.0, 8.7; pasta 48, 39, 1.6, 270, 86.7; pie filling 20, 16, 8.5, 2240,
  281; sauce 13, 5, 1.9, 1120, 228; soup 46, 39, 2.5, 410, 107; vegetables 72, 58, 5.3, 751,
  **139**. Table 3 (other packaging, n / positive): 27 / 21. Table 4: BADGE coconut milk 4
  (16.1, 224, 109), sauces 1 (14.3); BPF vegetables 3 (2.4, 3.8, 3.3); no BPS. Summary: BPA in
  361 (340 canned, 21 other); average **87.2** in all products, **91.6** canned (max 2240),
  **15.2** other (max 188). Results text: "an average level of **140** ppb in canned products and
  **6.7** ppb in products in other packaging"; vegetables **138**. Text: pie filling maximum 2240
  (canned pumpkin), next 530; coconut milk 1370, next 478; fruit 1160 (pineapple), next 186;
  sauces 1120 (green curry paste), next 7.5 (a tomato sauce that also contains BADGE); the highest
  BADGE (224) is a coconut milk without BPA; the three BPF positives are bamboo shoots that also
  contain BPA.
- **bpa-2016 Table 5** (BPA in canned products by survey year) prints these earlier rows (n,
  positive, min, max, average): 2013: beverages 97, 34, 1.1, 190, 13.6; coconut milk 13, 12, 4.8,
  253, 84.2; fruit 38, 19, 1.0, 53.6, 6.7; infant formula 55, 28, 1.1, 12.5, 4.8; **pasta 34, 45
  (100%)**, 6.7, 93.0, 19.5; pie filling 20, 8, 3.4, 47.3, 22.3; curry sauces 5, 5, 6.2, 226,
  75.5; soup 48, 42, 1.2, 307, 42.6; vegetables 70, 59, 1.1, 565, 31.8. 2012: beverages 72, 2,
  5.9, 12.0, 9.0; coconut milk 46, 17, 5.4, 381, 63.0; fruit 73, 1, 8.6; pasta 52, 52, 5.2, 157,
  21.9; curry sauces 24, 3, 88.0, 298, 227; soup 98, 39, 5.7, 277, 76.2; vegetables 144, 30, 5.5,
  103, 34.0. 2010: infant formula **37**, 0. Text: 464 canned samples "compared with data from
  targeted surveys conducted in previous years for a total of **1390** samples"; "(19 of 24)
  contained average levels of BPA that were consistently below 100 ppb".
- **bpa-2017** Table 1 (domestic, imported, unspecified, total): canned meat 111, 102, 18, 231;
  canned fish and seafood 14, 220, 3, 237; total 125, **325**, 21, 468. Table 2 (n, positive, min,
  max, average): meat BPA 231, 170, 1.20, 407, **35.6**; BADGE 53, 0.98, 46.2, 10.8; BPF 68, 1.01,
  63.6, 15.3; BPS 1 at 1.79; fish BPA 237, 159, 1.29, 1480, 54.7; BADGE 19, 0.97, 53.2, 8.02; no
  BPF or BPS; total BPA 468, 329, 1.20, 1480, 44.8. Summary: meat BPA average **34.6**; BPA section:
  "46.6 ppb for meat and 54.7 ppb for seafood". Text: 1480 is an imported sardine, the next
  highest 567; BADGE average 10.1; 69 of 72 BADGE positives also contain BPA; every BPF positive
  also contains BPA.

## Report-internal arithmetic (no data)

1. **The 2013 pasta row.** Table 5's "34" pastas with "45 (100%)" positives cannot both be true.
   With 45 pastas every 2013-14 total fits: 45 pasta + 48 soup = the description's 93
   pastas/soups; the nine 2013 rows then add to 391 samples (the description's total) and 252
   positives, and 391 - 252 = 139 = 35.5% (the description's "not detected"). With 34 they add to
   380, and the text's 1390 (= 464 + 380 + 509 + 37) carries the slip.
2. **The 2012 rows cover 509 of 576 samples.** The 2012 pasta (52) and soup (98) rows add to 150,
   where the 2012-13 page has 217 pastas/soups; every other 2012 row equals the page's category
   count. The 2012 rows' positives add to 144, where the page has 145. So the 67 pasta/soup
   samples missing from Table 5 hold one positive, or a 2012 row is misprinted.
3. **2010 formula: 37 vs 127.** Table 5's 2010 infant formula row has 37 samples; the 2010-11
   survey tested 127 formulas. 37 fits a subset (for example the canned ones).
4. **2011-12 is left out.** Table 5 and the 1390 total contain no 2011-12 rows, although that
   survey tested 403 canned samples with 6 positives (the lowest detection rate in the series).
5. **"19 of 24."** Table 5 prints 24 numeric averages; 18 of them are below 100 (the six at or
   above: coconut milk 306, pie filling 281, sauces 228 and 227, vegetables 138, soup 107).
6. **2016 canned average.** The nine Table 2 rows weighted by positives give 31,148.7 / 340 =
   91.6 (the summary); their unweighted mean is 1,259.3 / 9 = 139.9 (the results text's 140).
   Table 3's rows weighted give 319.7 / 21 = 15.2 (the summary) and (31,148.7 + 319.7) / 361 =
   87.2 (the summary's all-products figure). So 140 and 6.7 are averages of category averages,
   not of samples.
7. **2017 meat average.** Only 35.6 reproduces Table 2's total: (170 x 35.6 + 159 x 54.7) / 329 =
   44.8; 34.6 gives 44.3 and 46.6 gives 50.5.
8. **2017 imported total.** 102 + 220 = 322, not 325; with 322 the row adds to 468.
9. **2009 positives.** 70 + 12 = 82 = 41% of 200 (the page's 59% not detected); the other 79
   samples (plastic, paper-plastic, paper-metal) hold none.

## Predictions

- **S1 [census]** At least 6 of the 7 files hold exactly the printed total of samples: 200, 234,
  403, 576, 391, 491, 468.
- **S2 [census]** Where the file's product labels map to the printed categories without
  ambiguity, the category counts above reproduce (graded per file; mapping stated with the
  grader).
- **S3 [census]** bpa-2013 holds **45** pastas and 48 soups (Table 5's 34 is a slip). Competing
  reading, registered: 34 pastas and 59 other pasta/soup samples.
- **S4 [census]** bpa-2017 origins: meat 111 / 102 / 18 and fish 14 / 220 / 3, so **322**
  imported, not 325.
- **S5 [census]** If bpa-2010 records package type, exactly 37 of its formulas are canned (Table
  5's 2010 row). If bpa-2009 records it, the packages split 89 metal / 32 glass with metal lid /
  79 other. Ungraded if no package label exists.
- **V1 [values]** bpa-2009: 82 positives; 70 of 89 metal and 12 of 32 glass-metal (if packages are
  labelled); none in powdered formula or cereal; all 9 infant-food positives in glass jars with
  metal lids; range 1.4 to 9.6.
- **V2 [values]** bpa-2010: no positive sample.
- **V3 [values]** bpa-2011: exactly 6 positives (one pasta, three carrots, one peas, one corn).
- **V4 [values]** bpa-2012: 145 positives, minimum 5.2 (a pasta), maximum 381 (a coconut milk); at
  least 4 of Table 5's five non-pasta/soup 2012 rows reproduce in full (n, positives, min, max,
  average); the pasta/soup samples hold 92 positives.
- **V5 [values]** bpa-2013: 252 positives of 391, minimum 1.0 (a tropical fruit salad), maximum
  565 (a corn); at least 7 of Table 5's nine 2013 rows reproduce in full, pasta as 45 of 45.
- **V6 [values]** bpa-2016: Table 2 reproduces in at least 8 of 9 rows; 361 positives (340
  canned); the canned positives average **91.6** (not 140) and all products 87.2. No prediction
  on vegetables 139 vs 138; the file decides. The text's maxima and next-highest values hold.
- **V7 [values]** bpa-2017: Table 2's BPA rows reproduce and the meat average is **35.6** (not
  34.6 or 46.6); 1480 then 567; one BPS positive (a meat, 1.79); 69 of 72 BADGE positives and all
  68 BPF positives also contain BPA.
- **D1 (exploratory, directional)** Detection rates rise from 1.5% (2011-12) to 25% (2012-13) and
  64.5% (2013-14), while the lowest printed positive falls from 5.2 to 1.0 ppb. Re-cut at a common
  5.2 ppb in the categories shared by 2012-13 and 2013-14 (vegetables, fruit, juices/beverages,
  pastas/soups, coconut milk, curry), the 2013-14 share stays at least 1.5 times the 2012-13
  share, so the rise is not only a lower detection limit. Each file's non-detect coding and any
  printed limit are reported.

## Honest limits

The figures above were transcribed from the report pages and the open.canada.ca descriptions on
2026-10-31; the grader re-reads them. Table 5 may draw on later data revisions than the early
pages, so some misses could be revisions, not errors. The census grades only counts and labels.
Label mapping for the value items is fixed from the census before any value is read, and stated
in the grader's commit. A failed prediction is reported as failed.

MV2, Munim, Inc., mv2@munimtech.com
