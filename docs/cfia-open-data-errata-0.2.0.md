# CFIA open-data errata 0.2.0: every report-vs-file item from the chemistry-survey series, in one table

ERRATA-MARKER: cfia-open-data-errata-0.2.0

Made with AI agents working in MV2's (Munim, Inc.) name. Data CC BY 4.0; code Apache-2.0.

**What this is.** [`data/cfia-open-data-errata.csv`](../data/cfia-open-data-errata.csv) collects,
one row per item, every place where the series of notes in the
[CFIA chemistry surveys index](cfia-chemistry-surveys-index.md) found that a Canadian Food
Inspection Agency (CFIA) report page and its open per-sample file on open.canada.ca disagree, or
where a report or file disagrees with itself. Each row cites the note where the item was first
published, so the evidence, code and sealed-job record for it can be checked there. The table adds
no new finding: it is a single, machine-readable list of 64 items.

**What it is not.** No person at Munim, Inc. or at CFIA has confirmed these items by hand. They are
pointers for whoever maintains or re-uses the files, not confirmed errors. None of them is a
compliance finding, and none is dietary or medical advice. CFIA's own safety assessments are not
questioned here.

## What changed since 0.1.0

[Version 0.1.0](cfia-open-data-errata-0.1.0.md) had 49 items. 0.2.0 adds 15, and changes none of
the 49:

- **4 from the [phthalates-series result](phthalates-series-0.1.0-result.md)** (2012-2015 rows of
  two later reports against the 2012-2018 file): the printed 57.1% and 36% detection rates (54.0%
  and 19.0% over the file's samples), the grain row's 460 (459 in the file), the nut and seed
  butter average (17.26, printed 17.2) and the oil and fats-and-oils averages (106.0 and 95.6,
  printed 107 and 84.3).
- **11 from the [fumonisin-series pre-registration](fumonisin-series-0.1.0-prereg.md)**, found in
  the 2012-2018 fumonisin report's own tables before either new fumonisin file was opened: teff
  counted as 11 where the report's other tables need 77; a conventional total 74 short; rice year
  rows 19 short; a 2014 rice row and a 2012 wheat row that cannot be right as printed; 1 of 3
  printed as 67%; 167 of 214 printed as 68%; two tofu positives where the appendix shows one tofu
  and one soy flour; a soy list that is only the conventional column; 7710 for 7711; and a 2011
  corn minimum of 23.1 where the 2011-12 page says 20.8. These rows have no `open_file` figure
  yet: the files will be read only after the census and grader notes are public.

## Columns

| Column | Meaning |
|---|---|
| `item_id` | stable slug, prefixed by series |
| `series` | which series of notes (see the index) |
| `survey_years` | survey years the item concerns |
| `analyte` | chemical(s) |
| `where` | which document and which table, figure, sentence or file column |
| `finding` | one sentence, as published in the cited note |
| `printed` | the figure as printed, where one applies |
| `open_file` | the figure the open file gives, where one applies (empty if the file has not been read) |
| `kind` | what sort of item (below) |
| `evidence` | what the item rests on (below) |
| `note` | the note in `docs/` that first published it |

## Counts (64 items)

| kind | items | meaning |
|---|---|---|
| `count` | 12 | a sample or detection count differs |
| `value` | 8 | a single printed value (maximum, minimum, cut-off, per-analyte value) differs |
| `text` | 8 | a sentence, name or figure panel does not match |
| `average` | 7 | an average follows an unstated or mixed convention, or cannot be right |
| `share` | 6 | a printed percentage cannot be reached |
| `subset` | 5 | a table silently covers part of the file, or the wrong row |
| `unit` | 4 | a unit label or unit conversion is off (incl. the 1,000-fold ethyl carbamate file) |
| `label` | 4 | a product label or sample ID is out of pattern |
| `origin` | 3 | an origin split differs while totals hold |
| `coverage` | 3 | the file lacks a field or detail the report uses |
| `date` | 2 | sampling dates differ or are not real dates |
| `duplicate` | 2 | different samples carry identical values |

| evidence | items | meaning |
|---|---|---|
| `report_vs_file` | 36 | the report and the open file disagree |
| `report_internal` | 17 | the report contradicts itself (no file needed) |
| `file_internal` | 7 | the file alone shows it |
| `report_vs_report` | 4 | a later CFIA document restates an earlier survey differently |

By series: Children's Food Project 2, furans 2018-19 5, toxic metals 2018-19 1, PAHs 2018-19 2,
PAHs 2019-20 3, bisphenols 2018-19 and 2020-21 3, BPA 2009-10 to 2017-18 6, food colours 6,
ethyl carbamate 7, perchlorate 6, phthalates 2020-21 3, phthalates 2012-2019 9, fumonisins
2011-2018 11.

## What the table shows

- **Most items are small, but five rows (four slips) change a number by 10 times or more:** the
  2014-15 aflatoxin M1 unit label (`cfp-afm1-2014-unit`), the 2021 lead maximum
  (`cfp-lead-2021-max`), the 2018-19 ethyl carbamate file storing 36 of 37 detects 1,000 times too
  small (`ec-2018-1000x`), and the '0.6 ppb' that is 6 ppb on two phthalate pages (`ph-2020-ppb`,
  `ph-2018-ppb`). The largest new gap is teff: 11 printed where 77 is needed (`fum-2018-teff-11`).
- **Count items are mostly off by one or two samples** (7 of 12). The larger gaps are a later
  report's 34 pastas where the file has 45, four samples that the 2018-19 bisphenol report counts
  but the open file lacks (381 against 377), and three in the 2012-2018 fumonisin report's own
  tables (teff 11 against 77, a conventional total 74 short, rice 189 against 170).
- **Later tables are the weakest link.** Five `subset` items and four `report_vs_report` items
  come from a later CFIA table restating an earlier survey: a subset without saying so (non-soy
  formulas, canned food only), the Total row printed as the soy row, counts that match no year
  grouping, or a different minimum.
- **One report holds ten of the seventeen `report_internal` items.** The 2012-2018 fumonisin
  report is the longest in the series (16 tables and two appendices), and its year tables,
  appendices and text disagree in ten places that need no file to see.

## Limits

- Scope: the series in the CFIA chemistry surveys index only. The earlier spice, coumarin and
  mycotoxin series ([analyses-index.md](analyses-index.md)) have their own report-vs-file items
  (for example ochratoxin A, deoxynivalenol, Alternaria and the 2018-19 multi-mycotoxin survey);
  they are not yet included and will be added only after each is re-read from its own note.
- The fumonisin rows rest on the report alone. When the files are graded, each will either gain an
  `open_file` figure or be reported as not borne out; a later version will say which.
- The items reflect the open files as downloaded for each note (dates and MD5s are in the notes).
  The table does not re-check whether CFIA has since changed a file.

## Check it

`test_cfia_errata.py` (standard library only) checks the header, the counts above, a few values
copied verbatim from the notes, and that every row's note is linked from the index:

    python -m unittest -v test_cfia_errata

A sealed job re-runs this test against the copy published on GitHub.

MV2, Munim, Inc., mv2@munimtech.com
