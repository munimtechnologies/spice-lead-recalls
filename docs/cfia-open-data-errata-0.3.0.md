# CFIA open-data errata 0.3.0: every report-vs-file item from the chemistry-survey series, in one table

ERRATA-MARKER: cfia-open-data-errata-0.3.0

Made with AI agents working in MV2's (Munim, Inc.) name. Data CC BY 4.0; code Apache-2.0.

**What this is.** [`data/cfia-open-data-errata.csv`](../data/cfia-open-data-errata.csv) collects,
one row per item, every place where the series of notes in the
[CFIA chemistry surveys index](cfia-chemistry-surveys-index.md) found that a Canadian Food
Inspection Agency (CFIA) report page and its open per-sample file on open.canada.ca disagree, or
where a report or file disagrees with itself. Each row cites the note where the item was first
published, so the evidence, code and sealed-job record for it can be checked there. The table adds
no new finding: it is a single, machine-readable list of 75 items.

**What it is not.** No person at Munim, Inc. or at CFIA has confirmed these items by hand. They are
pointers for whoever maintains or re-uses the files, not confirmed errors. None of them is a
compliance finding, and none is dietary or medical advice. CFIA's own safety assessments are not
questioned here.

## What changed since 0.2.0

[Version 0.2.0](cfia-open-data-errata-0.2.0.md) had 64 items. 0.3.0 adds 11 and fills in the file
figure of 4 others; no other row changes.

- **4 of the 11 report-only fumonisin rows now have an `open_file` figure**, from the
  [fumonisin result](fumonisin-0.1.0-result.md): the teff label holds 59 samples (`fum-2018-teff-11`;
  neither the printed 11 nor the predicted 77, so the 11 is wrong either way); the two soy
  positives are one tofu and one soy flour (`fum-2018-tofu`); the 2012-13 maximum is 7711
  (`fum-2018-conv-max`); and the 2011-12 corn minimum is 20.8, as its page says, not the later
  report's 23.1 (`fum-2011-min`). The other 7 could not be checked from the files' labels and keep
  an empty `open_file`.
- **5 new rows for the 2010-11 fumonisin file** (new series `fumonisin-2010`): 277 samples
  against the page's 276; 185 positives against 157, with exactly 157 having B1 above zero; B2
  above zero in exactly the first 56 samples by number and in none of the 221 later ones; a
  4750 maximum and 7 samples above 800 against the page's 6650 and 8; and positives averaging
  206.85 against a later report's 268.
- **6 new rows for the 2011-12 and 2012-2018 files**: 498 samples and 175 positives against 454
  and 162; a soy infant formula at 284.6 that the 2011-12 page does not mention; 4,320 samples and
  1,080 positives against 4,261 and 1,076; Table 1's origin split matching the file in 2 of 9
  cells; 24 white teas against the text's 25; and 16 "D" sample numbers that are not repeats of
  samples in the file.

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
| `open_file` | the figure the open file gives, where one applies (empty if the file cannot show it) |
| `kind` | what sort of item (below) |
| `evidence` | what the item rests on (below) |
| `note` | the note in `docs/` that first published it |

## Counts (75 items)

| kind | items | meaning |
|---|---|---|
| `count` | 17 | a sample or detection count differs |
| `value` | 10 | a single printed value (maximum, minimum, cut-off, per-analyte value) differs |
| `text` | 8 | a sentence, name or figure panel does not match |
| `average` | 8 | an average follows an unstated or mixed convention, or cannot be right |
| `share` | 6 | a printed percentage cannot be reached |
| `subset` | 5 | a table silently covers part of the file, or the wrong row |
| `label` | 5 | a product label or sample ID is out of pattern |
| `unit` | 4 | a unit label or unit conversion is off (incl. the 1,000-fold ethyl carbamate file) |
| `origin` | 4 | an origin split differs while totals hold |
| `coverage` | 4 | the file lacks a field, detail or analyte the report uses |
| `date` | 2 | sampling dates differ or are not real dates |
| `duplicate` | 2 | different samples carry identical values |

| evidence | items | meaning |
|---|---|---|
| `report_vs_file` | 45 | the report and the open file disagree |
| `report_internal` | 17 | the report contradicts itself (no file needed) |
| `file_internal` | 9 | the file alone shows it |
| `report_vs_report` | 4 | a later CFIA document restates an earlier survey differently |

By series: Children's Food Project 2, furans 2018-19 5, toxic metals 2018-19 1, PAHs 2018-19 2,
PAHs 2019-20 3, bisphenols 2018-19 and 2020-21 3, BPA 2009-10 to 2017-18 6, food colours 6,
ethyl carbamate 7, perchlorate 6, phthalates 2020-21 3, phthalates 2012-2019 9, fumonisins
2010-11 5, fumonisins 2011-2018 17.

## What the table shows

- **Most items are small, but five rows (four slips) change a number by 10 times or more:** the
  2014-15 aflatoxin M1 unit label (`cfp-afm1-2014-unit`), the 2021 lead maximum
  (`cfp-lead-2021-max`), the 2018-19 ethyl carbamate file storing 36 of 37 detects 1,000 times too
  small (`ec-2018-1000x`), and the '0.6 ppb' that is 6 ppb on two phthalate pages (`ph-2020-ppb`,
  `ph-2018-ppb`).
- **The fumonisin files bring the series' largest count gaps.** All three files are larger than
  their reports (by 1, 44 and 59 samples), and their positive counts differ by 28, 13 and 4.
  Earlier count items were mostly off by one or two samples.
- **A new kind of coverage problem.** In the 2010-11 fumonisin file one of the two analytes (B2)
  is filled in only for the first 56 samples by number (`fum-2010-b2-first-56`); the page's
  positive count matches B1 alone (`fum-2010-157`). Whether the later B2 results were measured is
  a question only CFIA can answer.
- **Later tables are the weakest link.** Five `subset` items and four `report_vs_report` items
  come from a later CFIA table restating an earlier survey. One of them is now settled by a file:
  the 2011-12 corn minimum is the original page's 20.8, not the later report's 23.1.

## Limits

- Scope: the series in the CFIA chemistry surveys index only. The earlier spice, coumarin and
  mycotoxin series ([analyses-index.md](analyses-index.md)) have their own report-vs-file items;
  they are not yet included and will be added only after each is re-read from its own note.
- Seven report-only fumonisin rows cannot be checked from the files, whose labels are coarser
  than the report's grain groups; they stay report-only.
- The items reflect the open files as downloaded for each note (dates and MD5s are in the notes).
  The table does not re-check whether CFIA has since changed a file.

## Check it

`test_cfia_errata.py` (standard library only) checks the header, the counts above, a few values
copied verbatim from the notes, and that every row's note is linked from the index:

    python -m unittest -v test_cfia_errata

A sealed job re-runs this test against the copy published on GitHub.

MV2, Munim, Inc., mv2@munimtech.com
