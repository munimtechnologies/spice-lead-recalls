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
silently covers only part of the file (a subset of pastas, canned food only, or four samples fewer).
In the two PAH files, three pairs of samples with different foods or origins carry identical values;
the two food-colour files have none.

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

## Ethyl carbamate, 2018-19 and 2019-20

- [Pre-registration](ethyl-carbamate-0.1.0-prereg.md), fixed from the printed reports before either
  file is read. The 2019-20 text says 93% of soy samples had no EC, but 6 of 100 had it. A later
  CFIA report gives the 2019 soy row a minimum of 4.0 and an average of 74.1, which are the
  original report's all-products figures (soy alone: 7 and 108). The portal lists the 2019-20 file
  at 58 bytes, too small for 300 samples. A names-only census runs next.

MV2, Munim, Inc., mv2@munimtech.com
