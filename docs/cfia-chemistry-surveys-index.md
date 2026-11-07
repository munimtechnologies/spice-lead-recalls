# CFIA chemistry surveys: open per-sample files checked against their printed reports (index)

Made with AI agents working in MV2's (Munim, Inc.) name. Text CC BY 4.0; code Apache-2.0.
This page is an index of the notes below. It makes no new claims. None of the notes is a
compliance finding, and none is dietary or medical advice. The earlier spice, coumarin and
mycotoxin series are listed in [analyses-index.md](analyses-index.md).

The Canadian Food Inspection Agency (CFIA) publishes a report page for each targeted chemistry
survey and a per-sample CSV on open.canada.ca (Open Government Licence - Canada). Each series
below follows the same order of work:

1. Predictions are fixed from the printed report alone.
2. A names-only census counts labels and units without reading any value.
3. The label maps and a grader are committed before any value is read.
4. A sealed job grades the predictions.
5. An independent test re-runs the published result from GitHub.

Failed predictions are reported as failed. A gate that fails is never edited after the fact; a
format-only fix is published as a separate amendment before the files are read again.

**The pattern so far.** Totals in the open files match the printed totals far more often than
splits do. Where a report and its file disagree, the file usually matches the report's detailed
tables, and the summary or a later table is off. Several mismatches turn out to be a table that
silently covers only part of the file (a subset of pastas, canned food only, four samples fewer,
or formulas without the soy-based ones). In the two PAH files, three pairs of samples with
different foods or origins carry identical values; the two food-colour files have none. The two
ethyl carbamate files are the first pair whose origin splits match in every cell that can be
checked, and the 2018-19 one is the second file in the series with a 1,000-fold scale problem
(after the 2014-15 aflatoxin M1 unit label). The perchlorate files add a new kind: averages. Two
CFIA documents describe the same samples with different, unstated averages (all samples with
non-detects as zero, or detects only), and one later table pairs a subset's count and range with
the full group's average. The 2020-21 phthalates file reproduces every value claim of its report,
and only its origin table is off; the 2018-19 flatbread and vegan file reproduces its report in
full. Later CFIA tables' "2012 to 2015" phthalate rows carry the 2012-2018 file's detections
(every positive count, minimum and maximum) over different sample counts, so their printed
detection rates are higher than the file gives. The 2012-2018 fumonisin report, the longest in
the series, disagrees with itself in ten places before its file is opened; its arithmetic predicts
77 teff samples where its grain table prints 11, and the file's teff label then holds 59. The
three fumonisin files are the first in the series that are all larger than their reports (277,
498 and 4,320 samples against 276, 454 and 4,261). The 2012-2018 file still reproduces its
report's headline extremes and all three averages; the 2010-11 file adds a new kind of problem,
one analyte (fumonisin B2) stored for its first 56 samples only, with the page's positive count
matching B1 alone. On the portal side, open.canada.ca's resource sizes are kibibytes rounded up,
not rounded to nearest.

## All items in one table

- [CFIA open-data errata 0.3.0](cfia-open-data-errata-0.3.0.md) and
  [`data/cfia-open-data-errata.csv`](../data/cfia-open-data-errata.csv) (CC BY 4.0). The 75
  report-vs-file items from the notes below, one row each, with a kind, the evidence it rests
  on and the note that first published it. 45 rest on a report and its file disagreeing, 17 on a
  report contradicting itself, 9 on the file alone and 4 on a later CFIA document. Five rows
  (four slips) change a number by 10 times or more. `test_cfia_errata.py` checks it. 0.3.0 adds
  eleven items from the fumonisin census and result notes and fills in the file figure of four
  report-only fumonisin rows. Earlier versions: [0.2.0](cfia-open-data-errata-0.2.0.md) (64
  items) and [0.1.0](cfia-open-data-errata-0.1.0.md) (49).

## Children's Food Project (aflatoxin M1, lead)

- [Overview](childrens-food-project.md)
- Aflatoxin M1 trend: [pre-registration](cfp-afm1-trend-0.1.0-prereg.md) and
  [result](cfp-afm1-trend-0.1.0-result.md)
- Lead: [pre-registration](cfp-lead-0.1.0-prereg.md) and [result](cfp-lead-0.1.0-result.md)

## Furans in canned and dried foods, 2018-19

- [Pre-registration](furan-2018-0.1.0-prereg.md) and [result](furan-2018-0.1.0-result.md).
  Gate passed, 2 of 9 held. The file reproduces 174 of the 175 per-sample totals the report
  lists, but not its per-analyte table.

## Toxic metals in selected foods, 2018-19

- [Pre-registration](tmet-2018-0.1.0-prereg.md) and [result](tmet-2018-0.1.0-result.md). The file
  holds 987 samples where the report counts 985.

## PAHs in selected foods, 2018-19

- [Pre-registration](pah-2018-0.1.0-prereg.md) and [result](pah-2018-0.1.0-result.md). 6 of 7
  held. Table 2 reproduces in full. Figure 1's copied oil list is the soybean panel, not the
  sunflower panel.
- [Whole-file scan for identical samples](pah-2018-0.1.0-twin-scan.md). It finds two pairs of
  different foods with identical PAH values, a soybean and a sunflower oil, and a roasted pepper
  and a cookie.

## Bisphenols 2018-19 and 2020-21, and PAHs 2019-20

- [Pre-registration](bpa-pah-report-0.1.0-prereg.md),
  [census note](bpa-pah-report-0.1.0-census.md) and
  [grader note](bpa-pah-report-0.1.0-grader.md). B1 failed: the 2018-19 file holds 377 samples,
  not the summary's 381. C1 held (2020-21: 402 samples, all 15 origin cells). D1 held (2019-20 PAH
  file: 296 samples, 34 / 114 / 148).
- [Bisphenol result](bpa-2018-2020-0.1.0-result.md). 4 of 8 held. Both files reproduce their
  Table 2 in full, and 2020-21 also reproduces Tables 3-5. The 2018-19 report's 381 samples, 43%,
  and Table 3's 138 formulas (maximum 5.89, average 1.65) and 96 sauces need exactly four samples
  the open file lacks: three formulas, one of them BPA-positive at 5.89, and one sauce with no
  BPA. Two 2020-21 sentences do not match the file: two of the eight BADGE-and-BPA samples are
  Canadian meats, and one of the five BPS-positive corned beefs has no BPA.
- [PAH 2019-20 result](pah-2019-0.1.0-result.md), graded under the
  [ID-pattern amendment](id-pattern-0.1.1-amendment.md) after the
  [grader note](pah-2019-0.1.0-grader.md). The gate passes and 3 of 3 held: Table 2 reproduces in
  all 20 cells, and the text's formula, nut and olive-oil claims hold. Table 3's olive-oil 0.23 is
  the file's 0.2373 cut off, not rounded. Two olive oils of different origin (unknown and
  Argentina) carry identical values for all 16 PAHs. The two `AD` IDs have no `A` partner. Its
  independent test re-ran from GitHub in a sealed job on 2026-11-02 and passed (11 tests).

## Bisphenol A, nine years: 2009-10 to 2017-18

- [Pre-registration](bpa-series-0.1.0-prereg.md), [census note](bpa-series-0.1.0-census.md) and
  [grader note](bpa-series-0.1.0-grader.md). All seven files hold their printed totals. 2013-14
  has 45 pastas, so a later report's "34" is a slip. 2017-18 has 322 imported samples, not 325.
- [Result for five of the seven files](bpa-series-0.1.0-result.md). 4 of 6 held. 2010-11 has no
  positive, and 2013-14 and 2017-18 reproduce in full. 2012-13's Table 5 leaves out 67 of the
  file's 119 canned pastas and counts three salsas as curry. 2016-17's Table 2 is canned food only,
  and the file's 27 extra samples carry exactly the report's 21 non-canned positives. At a common
  5.2 ppb cut, 2013-14's positive share is 2.4 times 2012-13's, and it is higher in every shared
  category.
- [Regrade of 2009-10 and 2011-12](bpa-series-0.1.1-regrade-result.md), under the
  [ID-pattern amendment](id-pattern-0.1.1-amendment.md). All seven gates pass, and 6 of 8 graded
  items held. 2009-10 has 82 positives (9 in infant food, 1.4-9.6 ppb), and 2011-12 has exactly
  six. The 2009-10 dates are 200 consecutive days assigned in the text-sorted order of the sample
  IDs, and 35 of those IDs are zero-padded wrongly, so they are not real sampling dates. The three
  2011-12 `-2` IDs are separate later samples that reuse a number. Both pinned tests re-ran from
  GitHub in a sealed job and passed (16 and 10 tests).

## Food colours, 2009-10 and 2018-19

- [Pre-registration](food-colours-0.1.0-prereg.md), fixed from the printed reports before either
  file is read. The 2018-19 report's own tables differ by one detection: the per-colour counts add
  up to 337 and the per-commodity counts to 336. Its text also gives 219 colour-free samples
  against the table's 218.
- [Census note, label maps and grader](food-colours-0.1.0-census.md). 4 of 6 census items held.
  The 2018-19 origin totals are 56 / 183 / 160, not 56 / 184 / 159; the difference is one sweet.
  The 2018-19 file lists all 43 colours for every sample (399 x 46 rows). The 2009-10 file lists
  water-soluble colours for only 41 samples, which makes its "93%" sentence very unlikely to hold.
- [Result](food-colours-0.1.0-result.md). Both gates pass; 4 of 8 held. The file has 337
  detections, so Table 3 is right and Table 2's sweets cell (260) is one short. The three failed
  2018-19 items all come down to one value: the second Orange II result is 0.042 ppm (an imported
  pudding), not below 0.039, so Orange II's average is 0.1315, not below the 0.13 LQ. Leaving out
  that one sub-LQ result gives Table 2's 336 exactly (a reading, not proven). Table 3 otherwise
  reproduces in full; 218 samples are colour-free, not 219; the 539 ppm Allura Red candy and the
  single Rhodamine B sample hold. In 2009-10 the five named colours are 97.4% of results, not 93%.
  Its independent test re-ran from GitHub in a sealed job on 2026-11-02 and passed (12 tests).

## Ethyl carbamate, 2018-19 and 2019-20

- [Pre-registration](ethyl-carbamate-0.1.0-prereg.md), fixed from the printed reports before either
  file is read. The 2019-20 text says 93% of soy samples had no EC, but 6 of 100 had it. A later
  CFIA report gives the 2019 soy row a minimum of 4.0 and an average of 74.1, which are the
  original report's all-products figures (soy alone: 7 and 108).
- [Census note, label maps and grader](ethyl-carbamate-0.1.0-census.md). 4 of 5 census items
  held. The 2019-20 file is complete (58,972 bytes, matching the portal MD5); the portal's "58"
  size reads as kibibytes rounded up (see the phthalates census note), not bytes. Every product total and every origin cell that can be checked
  matches. One 2018-19 beer is labelled "Beef" and one 2019-20 fermented vegetable
  "Fish/Seafood"; both sit inside their product's ID block. The 2018-19 file gives sake, spirits
  and wine one label, so those rows and the wine-limit sentence cannot be checked, and its last
  sampling date is 6 March 2019, not the text's 21 March.
- [Result](ethyl-carbamate-0.1.0-result.md). Both gates pass; 3 of 6 graded items held. 2019-20
  reproduces in full: 94 of 100 soy samples have no EC, and the later report's soy row is the
  Total row (soy alone averages 108.0). The three 2018-19 items failed for one reason: 36 of the
  37 detected values are stored 1,000 times smaller than the report's ppb under a "ng/g" unit
  (beers 0.004 for a printed 4), while one vinegar is on the printed scale (135). All 36 come from
  samples whose region is West. Read as micrograms per gram (exploratory, not pre-registered), the
  36 values reproduce every printed 2018-19 cell and the later report's subtotal. Its independent
  test re-ran from GitHub in a sealed job on 2026-11-03 and passed (10 tests).

## Perchlorate, 2010-11, 2011-13 and 2013-14

- [Pre-registration](perchlorate-series-0.1.0-prereg.md), fixed from the three summary pages and
  the comparison table (Table 3) of CFIA's 2020-21 dairy and infant-formula report, which cites
  the earlier surveys as unpublished data. Table 3 gives 2010's cheese, milk and yogurt the same
  average (5.1), while the 2010-11 summary gives yogurt 4.9 and puts milk below both. Its 2010
  formula row has 74 samples where the 2010-11 report has 89. And 2013-14's "54% of infant
  formula" cannot be reached with Table 3's 30 formulas (16 of 30 is 53%, 17 of 30 is 57%).
- [Census note and label maps](perchlorate-series-0.1.0-census.md). The gate passes for all three
  files and 4 of 7 census items held, including the 2010-11 origin split (146 / 285 / 2). Table
  3's formula rows count only formulas not labelled soy: 74 of 89, 68 of 87 and 30 of 39. The
  2013-14 file has 39 formulas, so its "54%" is possible (21 of 39). The 2011-13 file has 15
  creams where Table 3 needs 17. No result value has been read; a grader note comes next.
- [Grader note](perchlorate-series-0.1.0-grader.md), with `perchlorate_series.py` and its offline
  tests. It fixes the 2013-14 six-group map before any value is read. The summary gives each
  group's detect share but not its size. Of the 16 ways to place the juices, soup, salsa and
  other drinks, only one lets every printed share be met with 272 detects in all: the juices
  count as assorted foods, not processed fruit products. That map allows exactly one detect count
  per group (93 / 39 / 40 / 21 / 18 / 61). With the juices among processed products, no count of
  the 53 remaining assorted foods rounds to 61%.
- [Result](perchlorate-series-0.1.0-result.md). All three gates pass; 1 of 9 held. Sample counts,
  detect counts, minima and maxima almost all reproduce; the failures are averages and the
  2013-14 shares. Read afterwards (descriptive): the 2010-11 summary averages over all samples
  with non-detects as zero (cucumber 48.6, tomato 44.9, cheese 5, yogurt 4.9 and soy formula 16.7
  all reproduce that way), while Table 3 averages detects only. In all three surveys Table 3's
  formula row gives the non-soy formulas' count and range with the average of all formulas,
  soy included (10.4, 11.8, 16.5; non-soy alone 7.7, 9.7, 15.7). Its 2010 cheese 5.1 matches
  neither reading. No placement the label arithmetic allowed gives 2013-14's processed share of
  40% (the file gives 39.2% to 59.8%). Its independent test re-ran from GitHub in a sealed job on
  2026-11-05 and passed (16 tests).

## Phthalates in ready-to-eat meals, vegetable fats and oils, 2020-21

- [Pre-registration](phthalates-2020-0.1.0-prereg.md), fixed from the report page before any part
  of the file is opened. The report's arithmetic pins the fats-and-oils split: salad dressings at
  4% of 50 is exactly 2 positives (they must be 0.3 and 0.6 ppm), so oils carry 29 of the 31. The
  page's "0.006 mg/L (0.6 parts per billion)" for the US bottled-water DEHP limit is 6 parts per
  billion.
- [Census note, label map and amendment A1](phthalates-2020-0.1.0-census.md). The gate as
  written failed: every sample has a `Phthalate Screen` row holding a text count with unit `n/a`,
  next to one µg/g row per phthalate found. 3 of 5 census items held: 250 meals and 250 fats and
  oils, 150 oils / 50 dressings / 50 shortenings and mayonnaises, and the six phthalate labels.
  Table 1's origin cells are off by one or two samples in each group (file 56 / 166 / 28 and
  28 / 159 / 63; printed 56 / 165 / 29 and 27 / 161 / 62), and the file has no region field. The
  screen tokens already show 464 samples without phthalates, DEHP in 23 and 7 with more than one.
  Value items are graded under a format-only amendment (A1), reported apart.
- [Grader note](phthalates-2020-0.1.0-grader.md), with `phthalates_2020.py` and 11 offline tests,
  published before any value is read.
- [Result](phthalates-2020-0.1.0-result.md). Under A1 all five value items held: Table 2 in all 18
  cells, the 464 samples without phthalates, the single 4.2 ppm maximum in a `Meal - Toddler/Baby`
  sample, DEHP in 23 samples with 7 multi-phthalate samples, and Table 3's 2020 oil and dressing
  rows. The pre-registration's arithmetic is confirmed exactly: the two positive dressings are 0.3
  and 0.6 ppm and the oils carry the other 29. Only 2 of 53 toddler and baby meals have
  phthalates, but they are the two largest ready-to-eat results and the only meals with more than
  one phthalate. Its independent test re-ran from GitHub in a sealed job on 2026-11-06 and passed
  (15 tests).

## Phthalates in flatbreads and vegan products 2018-19, and the 2012-2015 rows of two later tables

- [Pre-registration](phthalates-series-0.1.0-prereg.md), fixed from two report pages before either
  file (2018-19, 599 samples; 2012-2018, about 4,517) is opened. The 2018-19 tables are
  internally consistent (shares, sub-totals and both weighted averages), and they pin tofu's three
  positives to 0.54, about 8.01 and 24.00. The page's text has four slips that need no file to
  see: "599 ... flatbreads" (Table 1: 208), "BINP" and "BDP" (not among the six tested), and the
  same "0.006 mg/L (0.6 ppb)" as the 2020-21 page. The 2012-2015 rows that the 2018-19 and
  2020-21 reports print (grain products, nut and seed butters, ready-to-eat meals, oils, salad
  dressings, mayonnaise) are predicted from the 2012-2018 file. Their 57.1% and 36% rates pin 128
  of 224 meals and 8 of 22 dressings.
- [Census note, label maps and size-band amendment A2](phthalates-series-0.1.0-census.md). Both
  MD5s match, but both files sit just below their registered size bands, because the portal's
  kibibyte sizes are rounded up (this fits all four files checked so far); A2 fixes the band. The
  2018-19 file holds 208 flatbreads and 391 vegan products and matches its origin table in all six
  cells; its screen counts already give 526 samples without phthalates, DINP in 51 (so "BINP" is
  DINP), DEHP in 24, DBP in 4 and DIDP in 2. The 2012-2018 file holds 4,517 samples, 977 with a
  phthalate. Read by sampling year, its 2012-15 nut and seed butters are exactly the 2018-19
  report's 100, and its grain products 459 against 460; but the 2020-21 report's 2012-2015 counts
  (224 meals, 180 oils, 22 dressings, 327 fats and oils) match no combination of survey years.
- [Grader note](phthalates-series-0.1.0-grader.md), with `phthalates_series.py` and 14 offline
  tests, published before any value of either file is read.
- [Result](phthalates-series-0.1.0-result.md). Under A2, 6 of 8 value items held. The 2018-19
  file reproduces Table 2 in all 42 cells and every value claim of the text, including tofu's
  middle positive (8.0, derived as about 8.01 from the printed average alone). In the 2012-2018
  file every 2012-15 positive count, minimum and maximum that the two later reports print is
  there, but the sample counts mostly are not: 237 meals (printed 224), 42 dressings (22), 459
  grain products (460), 160 oils (180), 248 fats and oils (327). So the 2020-21 report's 57.1% of
  meals and 36% of dressings are 54.0% and 19.0% over the file's samples. The nut and seed
  butters average 17.26 (printed 17.2), and oils 106.0 (107). Its independent test re-ran from
  GitHub in a sealed job on 2026-11-07 and passed (17 tests).

## Fumonisins: 2010-11, 2011-12 and 2012-2018 (three files opened on the portal on 2026-11-03)

- [2010-11 pre-registration](fumonisin-2010-0.1.0-prereg.md), fixed from the report page before
  any part of the newly published file is opened: 276 samples in eleven product groups, 157
  positive, 20 to 6650 ppb, and eight samples above 800 ppb (4 cereals, 2 grits, 1 tortilla,
  1 cornmeal). The page's own arithmetic holds (the counts add to 276; 157 of 276 is 57%).
- [2011-12 and 2012-2018 pre-registration](fumonisin-series-0.1.0-prereg.md), with
  `test_fumonisin_series_prereg.py` (14 offline checks of the printed figures), fixed before
  either file is opened. The 2011-12 page (454 samples, 162 positive) is consistent. The 2012-2018
  report (4,261 samples; 16 tables and two appendices) is consistent in its Tables 1 and 2 but
  not elsewhere: its grain table adds to 3,584, not 3,650, and the shortfall is teff, printed as
  11 where the teff table's rows, the table's own 1% and the organic and conventional totals all
  need 77. A 2012 wheat row's average (99.7) cannot be right with a 28.8 minimum and a 393
  maximum, a 2014 rice row has one positive with two different extremes, 1 of 3 is printed as
  67% and 167 of 214 as 68%, and the text's two positive tofus are one tofu and one soy flour in
  its own appendix. The note predicts 77 teff samples, a 2012 wheat average of 184.0 to 186.2,
  the five rice positives, and the 2011-12 corn minimum (20.8 on its page, 23.1 in the later
  report). It also adds one prediction for the 2010-11 file, still unread: its positives average
  268 ppb, as the later report prints.
- [2010-11 census note and label map](fumonisin-2010-0.1.0-census.md). The gate holds; 2 of 4
  census items held (B1 and B2 only, all in ng/g). The file has 277 samples, not 276, in 9
  labels: five match a page group one to one, cornmeal and grits share one label (41 = 34 + 7),
  and the chips, tortilla and corn-products labels hold 79 where the page's chips, tacos,
  tortillas and cornbread mix add to 78.
- [2011-12 and 2012-2018 census note and label maps](fumonisin-series-0.1.0-census.md). Both gates
  hold; 4 of 13 census items held and 1 cannot be graded. The 2011-12 file has 498 samples, not
  454 (corn-named 262, soy-named 191, 45 neither). The 2012-2018 file has 4,320, not 4,261: grain
  3,713, soy 182 (its labels match the report's soy appendix row by row, less three soy infant
  cereals) and tea 425 (one white tea short). Its function column matches Table 1 in only 2 of 9
  cells. No label names wheat and 1,262 samples name no grain, so the report's grain tables cannot
  be rebuilt from the file. The teff label holds 59 samples (7 / 7 / 10 / 35 by year), neither the
  printed 11 nor the predicted 77; that 11 is wrong stands either way. The note fixes how each
  value item is graded: three are not gradable from the labels and three fail on the label map.
- [Grader note](fumonisin-0.1.0-grader.md), with `fumonisin_grade.py`, 10 offline tests and
  `test_fumonisin_census_notes.py` (every census count checked against the published census
  records in `data/`), published before any value of the three files is read.
- [Result](fumonisin-0.1.0-result.md). All three gates hold and no file has a format problem;
  6 of 17 graded value items held (3 not gradable). 2012-2018 reproduces Table 2's extremes
  (20 to 7790, a cornmeal) and all three averages (365, 36, 364), and settles the report's tofu
  contradiction: its two soy positives are a 2012-13 tofu (27) and a 2013-14 soy flour (45); but
  it has 1,080 positives, not 1,076. 2011-12 has the page's 20.8 corn minimum (not the later
  report's 23.1) and its 4442.5 maximum, under a "Corn Products" label, but 175 positives, not
  162, including a soy infant formula at 284.6. 2010-11 has 185 positives, not 157, a 4750
  maximum, not 6650, and 7 samples above 800, not 8. Read afterwards (exploratory): the 2010-11
  page's 157 is exactly the samples with B1 above zero, and B2 is above zero in exactly the first
  56 samples by number (2010FMN0001 to 0055) and in none of the 221 later ones. If those later B2
  results were measured but stored as 0, the page's 6650, its eighth sample above 800 and the
  later report's 268 average would all be reachable (a lead only CFIA can settle).
  `test_fumonisin_result.py` re-reads the three per-sample tables in `data/`; a sealed job
  re-runs it from GitHub.

MV2, Munim, Inc., mv2@munimtech.com
