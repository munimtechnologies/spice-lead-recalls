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
- [PAH 2019-20 grader note](pah-2019-0.1.0-grader.md) (D2-D5). The first sealed run failed its gate
  on two sample IDs ending `AD` (every count held). It is being regraded under the
  [ID-pattern amendment](id-pattern-0.1.1-amendment.md).

## Bisphenol A, nine years: 2009-10 to 2017-18

- [Pre-registration](bpa-series-0.1.0-prereg.md), [census note](bpa-series-0.1.0-census.md) and
  [grader note](bpa-series-0.1.0-grader.md). All seven files hold their printed totals. 2013-14
  has 45 pastas, so a later report's "34" is a slip. 2017-18 has 322 imported samples, not 325.
  The 2009-10 file's sampling dates look like placeholders.
- [Result for five of the seven files](bpa-series-0.1.0-result.md). 4 of 6 held. 2010-11 has no
  positive, and 2013-14 and 2017-18 reproduce in full. 2012-13's Table 5 leaves out 67 of the
  file's 119 canned pastas and counts three salsas as curry. 2016-17's Table 2 is canned food only,
  and the file's 27 extra samples carry exactly the report's 21 non-canned positives. At a common
  5.2 ppb cut, 2013-14's positive share is 2.4 times 2012-13's, and it is higher in every shared
  category.
- 2009-10 and 2011-12 failed only the sample-ID pattern (every count held). They are being
  regraded under the [ID-pattern amendment](id-pattern-0.1.1-amendment.md).

MV2, Munim, Inc., mv2@munimtech.com
