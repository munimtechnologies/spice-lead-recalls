# CFIA open-data errata 0.1.0: every report-vs-file item from the chemistry-survey series, in one table

ERRATA-MARKER: cfia-open-data-errata-0.1.0

Made with AI agents working in MV2's (Munim, Inc.) name. Data CC BY 4.0; code Apache-2.0.

**What this is.** [`data/cfia-open-data-errata.csv`](../data/cfia-open-data-errata.csv) collects,
one row per item, every place where the series of notes in the
[CFIA chemistry surveys index](cfia-chemistry-surveys-index.md) found that a Canadian Food
Inspection Agency (CFIA) report page and its open per-sample file on open.canada.ca disagree, or
where a report or file disagrees with itself. Each row cites the note where the item was first
published, so the evidence, code and sealed-job record for it can be checked there. The table adds
no new finding: it is a single, machine-readable list of 49 items.

**What it is not.** No person at Munim, Inc. or at CFIA has confirmed these items by hand. They are
pointers for whoever maintains or re-uses the files, not confirmed errors. None of them is a
compliance finding, and none is dietary or medical advice. CFIA's own safety assessments are not
questioned here.

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
| `open_file` | the figure the open file gives, where one applies |
| `kind` | what sort of item (below) |
| `evidence` | what the item rests on (below) |
| `note` | the note in `docs/` that first published it |

## Counts (49 items)

| kind | items | meaning |
|---|---|---|
| `count` | 8 | a sample or detection count differs |
| `text` | 6 | a sentence, name or figure panel does not match |
| `value` | 5 | a single printed value (maximum, cut-off, per-analyte value) differs |
| `subset` | 5 | a table silently covers part of the file, or the wrong row |
| `unit` | 4 | a unit label or unit conversion is off (incl. the 1,000-fold ethyl carbamate file) |
| `average` | 4 | an average follows an unstated or mixed convention |
| `label` | 4 | a product label or sample ID is out of pattern |
| `share` | 3 | a printed percentage cannot be reached |
| `origin` | 3 | an origin split differs while totals hold |
| `coverage` | 3 | the file lacks a field or detail the report uses |
| `date` | 2 | sampling dates differ or are not real dates |
| `duplicate` | 2 | different samples carry identical values |

| evidence | items | meaning |
|---|---|---|
| `report_vs_file` | 32 | the report and the open file disagree |
| `report_internal` | 7 | the report contradicts itself (no file needed) |
| `file_internal` | 7 | the file alone shows it |
| `report_vs_report` | 3 | a later CFIA document restates an earlier survey differently |

By series: Children's Food Project 2, furans 2018-19 5, toxic metals 2018-19 1, PAHs 2018-19 2,
PAHs 2019-20 3, bisphenols 2018-19 and 2020-21 3, BPA 2009-10 to 2017-18 6, food colours 6,
ethyl carbamate 7, perchlorate 6, phthalates 2020-21 3, phthalates 2012-2019 5.

## What the table shows

- **Most items are small, but five rows (four slips) change a number by 10 times or more:** the
  2014-15 aflatoxin M1 unit label (`cfp-afm1-2014-unit`), the 2021 lead maximum
  (`cfp-lead-2021-max`), the 2018-19 ethyl carbamate file storing 36 of 37 detects 1,000 times too
  small (`ec-2018-1000x`), and the '0.6 ppb' that is 6 ppb on two phthalate pages (`ph-2020-ppb`,
  `ph-2018-ppb`).
- **Count items are mostly off by one or two samples** (6 of 8). The larger gaps are a later
  report's 34 pastas where the file has 45, and four samples that the 2018-19 bisphenol report
  counts but the open file lacks (381 against 377).
- **Later tables are the weakest link.** Five `subset` items and three `report_vs_report` items
  come from a later CFIA table restating an earlier survey: a subset without saying so (non-soy
  formulas, canned food only), the Total row printed as the soy row, or counts that match no
  year grouping.

## Limits

- Scope: the series in the CFIA chemistry surveys index only. The earlier spice, coumarin and
  mycotoxin series ([analyses-index.md](analyses-index.md)) have their own report-vs-file items
  (for example ochratoxin A, deoxynivalenol, Alternaria and the 2018-19 multi-mycotoxin survey);
  they are not in 0.1.0 and will be added only after each is re-read from its own note.
- Items still being graded (the 2018-19 and 2012-2018 phthalates value items) are not included.
- The items reflect the open files as downloaded for each note (dates and MD5s are in the notes).
  The table does not re-check whether CFIA has since changed a file.

## Check it

`test_cfia_errata.py` (standard library only) checks the header, the counts above, a few values
copied verbatim from the notes, and that every row's note is linked from the index:

    python -m unittest -v test_cfia_errata

A sealed job re-runs this test against the copy published on GitHub.

MV2, Munim, Inc., mv2@munimtech.com
