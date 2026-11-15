# CFIA open-data errata 0.4.0: four mycotoxin and tea series added, 86 items in one table

ERRATA-MARKER: cfia-open-data-errata-0.4.0

Made with AI agents working in MV2's (Munim, Inc.) name. Data CC BY 4.0; code Apache-2.0.

**What this is.** [`data/cfia-open-data-errata.csv`](../data/cfia-open-data-errata.csv) collects,
one row per item, the places where a series of pre-registered notes found that a Canadian Food
Inspection Agency (CFIA) report and its open per-sample file on open.canada.ca disagree, or where
a report or file disagrees with itself. Each row cites the note where the item was first
published, so the evidence, code and sealed-job record for it can be checked there. The table adds
no new finding: it is a single, machine-readable list of 86 items.

**What it is not.** No person at Munim, Inc. or at CFIA has confirmed these items by hand. They are
pointers for whoever maintains or re-uses the files, not confirmed errors. None of them is a
compliance finding, and none is dietary or medical advice. CFIA's own safety assessments are not
questioned here.

## What changed since 0.3.0

[Version 0.3.0](cfia-open-data-errata-0.3.0.md) had 75 items, all from the series in the
[CFIA chemistry surveys index](cfia-chemistry-surveys-index.md). 0.4.0 adds 11 rows from four
series that were published in the earlier [analyses index](analyses-index.md); no existing row
changes. Each new row was re-read from its own published note before it was added.

- **Dried tea, 2009-10** (new series `dried-tea-2009`, 3 rows, from the
  [result](dried-tea-2009-0.1.0-result.md) and [census](dried-tea-2009-0.1.0-census.md) notes):
  the page says every metal except beryllium was found in every tea, but the file has mercury
  above zero in only 32 of 100 teas (`tea-2009-metals-every`; a zero may mean below a reporting
  limit); the 2010-11 page calls its own 87% mercury rate much higher than in earlier years,
  which fits the file, not the 2009-10 page (`tea-2009-mercury-pages`); and the information PDF
  states 206 GC-MS and 160 LC-MS analytes while its own table has 207 and 157 rows
  (`tea-2009-pdf-a1`).
- **Aflatoxins in dried dates and figs, 2009-10** (new series `figs-2009`, 1 row, from the
  [result](aflatoxin-figs-2009-0.1.0-result.md)): the page's 49 dates and 51 figs against the
  file's 50 and 50 (`figs-2009-split`). The printed 92% of figs without aflatoxin fits both
  splits, so the file cannot say which is right.
- **Feed mycotoxins, Program 15B** (new series `feed-myco`, 3 rows, from the
  [result](feed-myco-0.1.0-result.md)): the report's 3,202 HT-2 samples against the file's 3,243,
  where the 41 extra rows are exactly the HT-2 non-detects whose 0.5 ppm quantification limit is
  above the 0.1 ppm action level (`feed-ht2-41`); the text quoting Table 1's DON share as 81.3%
  where the table prints 82.22% (`feed-don-813`); and one fumonisin row with a blank fiscal year
  that, placed in 2016-17, gives the report's 164 samples and 98.17% exactly
  (`feed-fum-2016-blank-year`).
- **Multi-mycotoxins, 2018-19** (new series `multimyco-2018`, 4 rows, from the
  [result](multimyco-2018-0.1.0-result.md)): 388 positives in the text and 386 in Table 2 against
  387 in the file (`mm-2018-positives`); a printed DON average of 282 ppb where the file's 306 DON
  positives average 181.3, although the DON count and maximum match exactly (`mm-2018-don-avg`);
  three of Table 3's nine group counts off by 1 to 4 (`mm-2018-groups`); and "17 different
  mycotoxins" where the file shows 18 of its 24 labels detected (`mm-2018-17-toxins`).

## Columns

| Column | Meaning |
|---|---|
| `item_id` | stable slug, prefixed by series |
| `series` | which series of notes (see the indexes) |
| `survey_years` | survey years the item concerns |
| `analyte` | chemical(s) |
| `where` | which document and which table, figure, sentence or file column |
| `finding` | one sentence, as published in the cited note |
| `printed` | the figure as printed, where one applies |
| `open_file` | the figure the open file gives, where one applies (empty if the file cannot show it) |
| `kind` | what sort of item (below) |
| `evidence` | what the item rests on (below) |
| `note` | the note in `docs/` that first published it |

## Counts (86 items)

| kind | items | meaning |
|---|---|---|
| `count` | 22 | a sample or detection count differs |
| `value` | 10 | a single printed value (maximum, minimum, cut-off, per-analyte value) differs |
| `share` | 9 | a printed percentage cannot be reached |
| `average` | 9 | an average follows an unstated or mixed convention, or cannot be right |
| `text` | 8 | a sentence, name or figure panel does not match |
| `subset` | 6 | a table silently covers part of the file, or the wrong row |
| `label` | 6 | a product label, sample ID or year field is out of pattern |
| `unit` | 4 | a unit label or unit conversion is off (incl. the 1,000-fold ethyl carbamate file) |
| `origin` | 4 | an origin split differs while totals hold |
| `coverage` | 4 | the file lacks a field, detail or analyte the report uses |
| `date` | 2 | sampling dates differ or are not real dates |
| `duplicate` | 2 | different samples carry identical values |

| evidence | items | meaning |
|---|---|---|
| `report_vs_file` | 52 | the report and the open file disagree |
| `report_internal` | 19 | the report contradicts itself (no file needed) |
| `file_internal` | 10 | the file alone shows it |
| `report_vs_report` | 5 | a later CFIA document restates an earlier survey differently |

By series: Children's Food Project 2, furans 2018-19 5, toxic metals 2018-19 1, PAHs 2018-19 2,
PAHs 2019-20 3, bisphenols 2018-19 and 2020-21 3, BPA 2009-10 to 2017-18 6, food colours 6,
ethyl carbamate 7, perchlorate 6, phthalates 2020-21 3, phthalates 2012-2019 9, fumonisins
2010-11 5, fumonisins 2011-2018 17, dried tea 2009-10 3, dates and figs 2009-10 1, feed
mycotoxins 3, multi-mycotoxins 2018-19 4.

## What the new rows add

- **No new 10-fold slip.** The five rows (four slips) that change a number by 10 times or more
  are still the four listed in 0.3.0. The new rows are counts, shares and one average.
- **Two gaps are explained exactly by the file.** The 41 extra HT-2 rows are the non-detects
  whose quantification limit cannot be compared with the action level, and the blank fiscal
  year accounts for the one sample missing from the 2016-17 fumonisin cell. Both are ways a
  report can silently leave rows out; neither suggests a wrong value.
- **One average cannot come from the file's positives.** The 2018-19 DON average (282 against
  181.3) is the largest relative gap among the new rows, and the count and maximum match, so it
  is not a different sample set. Why it differs is a question only CFIA can answer.
- **A "found in every sample" sentence.** The dried-tea mercury item depends on how zeros are
  read: if a zero means "below a reporting limit", the file does not support "every tea"; the
  2010-11 page's own comparison points the same way.

## Limits

- Scope: the series in the CFIA chemistry surveys index plus these four. Other items in the
  earlier spice, coumarin and mycotoxin notes (for example ochratoxin A in infant formula and
  grains, DON in grains, Alternaria toxins in tomato products, coumarin) are not included yet;
  each will be added only after it is re-read from its own note.
- Seven report-only fumonisin rows from 0.3.0 still cannot be checked from the files, whose labels
  are coarser than the report's grain groups.
- The items reflect the open files as downloaded for each note (dates and MD5s are in the notes).
  The table does not re-check whether CFIA has since changed a file.

## Check it

`test_cfia_errata.py` (standard library only) checks the header, the counts above, a few values
copied verbatim from the notes (including the arithmetic behind four of the new rows), and that
every row's note is linked from the CFIA chemistry surveys index:

    python -m unittest -v test_cfia_errata

The agent skill in `skills/cfia-open-data-errata/` bundles this table (errata 0.4.0, 86 items);
`test_cfia_errata_skill.py` checks that its copy is byte-identical to `data/`. A sealed job
built this release from the files published on GitHub and ran both tests before it was
published.

MV2, Munim, Inc., mv2@munimtech.com
